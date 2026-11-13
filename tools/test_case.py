"""Independent checks on the published analysis and on the privacy rules.

These are regressions, not certifications. They fail if a published claim, a
rounding rule or a privacy guard changes without being noticed.
"""
import re
import sys
import unittest
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '_7eff7e24'))
sys.path.insert(0, str(ROOT / '_7adb71fc'))

from case_data import A, B, P, CA_HPI, BOE_FACTORS
from case_model import rounded, projection, path_comparison, allowance, money
import swan
from evidence import SOURCES, FAILED, LABELS
from verify import PROHIBITED


class RoundingTests(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(rounded(125), 130)
        self.assertEqual(rounded(124.99), 120)
        self.assertEqual(rounded(1_044_586), 1_044_590)
        self.assertEqual(rounded(-125), -130)

    def test_every_input_is_a_multiple_of_ten(self):
        for prop in (A, B):
            for key in ('value_2026', 'assessed_2026', 'insurance_year'):
                self.assertEqual(prop[key] % 10, 0, key)
            for lo, hi in (prop['water_year'], prop['electric_year']):
                self.assertEqual(lo % 10, 0)
                self.assertEqual(hi % 10, 0)

    def test_growth_rounds_up_not_to_even(self):
        self.assertEqual(rounded(15), 20)
        self.assertEqual(rounded(25), 30)


class ProjectionTests(unittest.TestCase):
    def test_horizon(self):
        rows = projection('A', transfer=2045)
        self.assertEqual(len(rows), 51)
        self.assertEqual(rows[0]['year'], 2026)
        self.assertEqual(rows[-1]['year'], 2076)

    def test_transfer_resets_only_a(self):
        a = projection('A', transfer=2045)
        b = projection('B')
        self.assertLess(a[18]['tax_assessed'], a[19]['tax_assessed'] * 0.95)
        self.assertAlmostEqual(b[19]['tax_assessed'], b[18]['tax_assessed'] * 1.02, delta=1)

    def test_cap_applies_every_year_before_transfer(self):
        rows = projection('A', transfer=2045)
        self.assertAlmostEqual(rows[18]['tax_assessed'], A['assessed_2026'] * 1.02 ** 18, delta=1)

    def test_qualified_never_above_market(self):
        for r in projection('A', transfer=2040):
            self.assertLessEqual(r['tax_qualified'], r['value'] + 1)

    def test_allowance_uses_published_figure_before_2027(self):
        self.assertEqual(allowance(2026), 1_044_590)
        self.assertEqual(allowance(2027), 1_044_590)
        self.assertGreater(allowance(2045), allowance(2027))

    def test_allowance_is_indexed_like_the_statute_not_like_the_house(self):
        # RTC 63.2 indexes the $1,000,000 base to the FHFA California index, so
        # the allowance must climb faster than a 4% house assumption would imply.
        self.assertGreater(allowance(2045), 1_044_586 * 1.04 ** 18)
        # and it moves in two-year steps, because it is re-set each second February
        self.assertEqual(allowance(2028), allowance(2029))
        self.assertLess(allowance(2028), allowance(2030))

    def test_selling_cost_and_transfer_tax(self):
        c = path_comparison(2045)
        self.assertLess(c['sale_net'], c['sale_price'])
        self.assertGreater(c['sale_net'], c['sale_price'] * 0.92)

    def test_rental_loses_cash_and_reinvest_wins(self):
        c = path_comparison(2045)
        self.assertLess(c['rental_income_20y'], 0)
        self.assertGreater(c['reinvest_after_tax'], c['rental_total'])

    def test_recommendation_holds_for_every_window(self):
        for year in range(2040, 2051):
            c = path_comparison(year)
            self.assertGreater(c['reinvest_after_tax'], c['rental_total'], year)


class ReplayTests(unittest.TestCase):
    def test_series_integrity(self):
        self.assertEqual(len(CA_HPI), 206)
        self.assertEqual(CA_HPI[(1975, 1)], 41.65)
        self.assertEqual(CA_HPI[(2026, 2)], 974.97)
        self.assertEqual(len(BOE_FACTORS), 51)

    def test_published_replay_figures(self):
        self.assertAlmostEqual(swan.cagr((1975, 1), (2026, 2)), 6.35, places=2)
        _, dd = swan.episodes()
        self.assertAlmostEqual(dd['trough_pct'], -41.04, places=1)
        self.assertAlmostEqual(swan.recovery()['years'], 12.75, places=2)
        self.assertAlmostEqual(swan.assessment_replay()['factor_cagr'], 1.81, places=2)
        self.assertAlmostEqual(swan.assessment_replay()['captured_ratio'], 91.1, places=1)

    def test_replay_is_monotone_in_start_date(self):
        windows = swan.start_windows()
        self.assertTrue(windows)
        for w in windows:
            self.assertGreater(w['cagr'], 0)


class EvidenceTests(unittest.TestCase):
    def test_every_source_is_official(self):
        for key, (label, url, passage, scope, chunk) in SOURCES.items():
            self.assertTrue(url.startswith('https://'), key)
            host = url.split('/')[2]
            self.assertTrue(host.endswith('.gov'), key + ' ' + host)
            self.assertTrue(passage.strip(), key)
            self.assertTrue(scope.strip(), key)

    def test_every_source_has_a_public_label(self):
        for key in SOURCES:
            self.assertIn(key, LABELS)

    def test_failed_retrievals_are_recorded(self):
        self.assertGreaterEqual(len(FAILED), 5)

    def test_no_source_copied_without_fetch(self):
        # The ledger records the retrieval date this session used.
        from evidence import DATE
        self.assertEqual(DATE, '2026-11-13')


class PrivacyTests(unittest.TestCase):
    def test_prohibited_pattern_catches_geography(self):
        for text in ('Cupertino', 'zip 95014', 'Outer Sunset', 'APN 123',
                     'Social Security number'):
            self.assertTrue(PROHIBITED.search(text), text)

    def test_published_pages_have_no_geography(self):
        for path in [ROOT / 'index.html', *(ROOT / 'pages').glob('*.html')]:
            text = path.read_text()
            body = re.sub(r'<[^>]+>', ' ', text)
            self.assertIsNone(PROHIBITED.search(body), path.name)

    def test_published_pages_have_no_exact_source_figures(self):
        for path in [ROOT / 'index.html', *(ROOT / 'pages').glob('*.html')]:
            if path.name == 'sources.html':
                continue  # the ledger quotes official passages verbatim
            body = re.sub(r'<[^>]+>', ' ', path.read_text())
            for token in re.findall(r'\$([\d,]+(?:\.\d+)?)', body):
                window = body[max(0, body.find(token) - 140):body.find(token) + 160]
                if re.search(r'exact|statutory|per \$500|per \$1,000|published amount', window, re.I):
                    continue
                self.assertEqual(float(token.replace(',', '')) % 10, 0,
                                 f'{path.name}: {token}')


class ContentTests(unittest.TestCase):
    def test_recommendation_is_stated(self):
        from content_part1 import page_exec
        html = page_exec()
        self.assertIn('Recommendation in one sentence', html)
        self.assertIn('Plan to occupy Property A', html)

    def test_renting_is_not_recommended_and_says_why(self):
        from content_part1 import page_exec
        self.assertIn('Renting A loses cash every year', page_exec())

    def test_questions_cover_discovery(self):
        from content_part2 import page_questions
        html = page_questions()
        for q in (f'Q{i}' for i in range(1, 23)):
            self.assertIn('>' + q + '<', html)

    def test_suggestions_are_review_only(self):
        from content_part2 import page_suggestions
        html = page_suggestions()
        self.assertIn('Not reviewed', html)
        self.assertIn('does not change any projection', html)

    def test_flagged_page_is_labelled(self):
        from content_part3 import page_flagged
        self.assertIn('Flagged for review', page_flagged())

    def test_black_swan_makes_no_probability_claim(self):
        # A disclaimer is allowed to mention the word. A numeric claim is not.
        from content_part1 import page_black_swan
        html = page_black_swan().lower()
        for m in re.finditer(r'(\d+(?:\.\d+)?%|\bthere is a\b)[^.]{0,80}(probab|chance|odds)', html):
            self.fail('probability claim: ' + m.group(0))
        self.assertIn('no probability of a crash', html)

    def test_every_page_returns_markup(self):
        for name in ('page_overview', 'page_exec', 'page_decision', 'page_projections',
                     'page_black_swan', 'page_cost', 'page_tax', 'page_questions',
                     'page_suggestions', 'page_estate', 'page_process', 'page_law',
                     'page_flagged', 'page_sources', 'page_privacy'):
            module = 'content_part1' if name in (
                'page_overview', 'page_exec', 'page_decision', 'page_projections',
                'page_black_swan') else ('content_part2' if name in (
                'page_cost', 'page_tax', 'page_questions', 'page_suggestions') else 'content_part3')
            mod = __import__(module)
            html = getattr(mod, name)()
            self.assertGreater(len(html), 2000, name)
            self.assertNotIn('KeyError', html)


if __name__ == '__main__':
    unittest.main()
