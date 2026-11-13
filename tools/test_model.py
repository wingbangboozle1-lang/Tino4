"""Isolated legacy arithmetic tests and public-content regression checks; no personal inputs."""
import math
import re
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'_7eff7e24'))
from model import rounded, money, prop19_assessment, projection, compare, rates, exclusion, REGIMES
from content import content, PAGES
from evidence import SOURCES
from verify import CASE_SPECIFIC_PATTERNS

class ModelTests(unittest.TestCase):
    def test_half_up_not_bankers(self):
        self.assertEqual(rounded(125),130)
        self.assertEqual(rounded(124.99),120)
        self.assertEqual(rounded(-125),-130)
        self.assertEqual(money(-125),'−$130')
    def test_prop19_excess_and_boundary(self):
        self.assertEqual(prop19_assessment(1_500_000,300_000,1_000_000),500_000)
        self.assertEqual(prop19_assessment(1_300_000,300_000,1_000_000),300_000)
        self.assertEqual(prop19_assessment(900_000,300_000,1_000_000),300_000)
    def test_full_fifty_year_horizon(self):
        for y in range(2040,2051):
            rows=projection(y)
            self.assertEqual(len(rows),51)
            self.assertEqual([r['year'] for r in rows],list(range(2026,2077)))
            self.assertAlmostEqual(rows[-1]['value'],1_000_000*1.03**50)
            self.assertAlmostEqual(rows[-1]['real'],rows[-1]['value']/1.025**50)
    def test_transfer_resets_only_at_transfer(self):
        rows={r['year']:r for r in projection(2045)}
        self.assertAlmostEqual(rows[2044]['full'],200_000*1.02**18)
        r=rows[2045]
        self.assertEqual(r['full'],r['value'])
        self.assertAlmostEqual(r['qualified'],r['old']+max(0,r['value']-r['old']-1_000_000))
        self.assertAlmostEqual(rows[2046]['full'],r['full']*1.02)
        self.assertAlmostEqual(rows[2046]['qualified'],r['qualified']*1.02)
    def test_base_levy_and_costs(self):
        r=projection()[10]
        self.assertAlmostEqual(r['tax'],r['full']*.01)
        self.assertAlmostEqual(r['insurance'],3000*1.04**10)
        self.assertAlmostEqual(r['water'],1200*1.03**10)
        self.assertAlmostEqual(r['electricity'],600*1.03**10)
    def test_one_year_equity_after_tax(self):
        # $950k starts invested, 2% income, 25% dividend tax, basis adds net income.
        initial=950_000
        dividend=initial*.02
        balance=initial*1.06-dividend*.25
        basis=initial+dividend*.75
        expected=balance-max(0,balance-basis)*.25
        self.assertAlmostEqual(compare(years=1)['equity'],expected)
    def test_one_year_rental_after_tax(self):
        rent=48_000*.95
        expense=1200+600+3000+10000+10000+rent*.08
        dep=700_000/27.5
        cf=rent-expense-max(0,rent-expense-dep)*.30
        self.assertAlmostEqual(compare(years=1)['first_cash'],cf)
        terminal=1_000_000*1.03*.95
        gain=max(0,terminal-(1_000_000-dep))
        recapture=min(gain,dep)
        expected=terminal-recapture*.30-(gain-recapture)*.25+cf
        self.assertAlmostEqual(compare(years=1)['rental'],expected)
    def test_after_tax_bills_compound(self):
        for years in (1,20,50):
            self.assertAlmostEqual(compare(years=years)['bills'],950_000*(1+.03*.70)**years)
    def test_stress_is_non_uniform(self):
        self.assertEqual(rates('Equity crash',1)['equity'],-.4)
        self.assertEqual(rates('Equity crash',2)['equity'],-.1)
        self.assertEqual(rates('Equity crash',3)['equity'],.12)
        self.assertEqual(rates('Equity crash',6)['equity'],.06)
        self.assertEqual(rates('Compound shock',1)['equity'],-.4)
        self.assertLess(compare('Equity crash')['equity'],compare()['equity'])
        self.assertLess(compare('Insurance and repairs')['rental'],compare()['rental'])
    def test_capex_not_permanent_maintenance(self):
        rows=projection(regime='Insurance and repairs')
        self.assertAlmostEqual(rows[3]['maintenance'],10000*1.03**3+75000)
        self.assertAlmostEqual(rows[4]['maintenance'],10000*1.03**4)
    def test_exclusion_is_synthetic_not_official(self):
        self.assertEqual(exclusion(2027),15_480_000)
        self.assertEqual(exclusion(2045,0),15_480_000)
        self.assertAlmostEqual(exclusion(2045),15_480_000*1.025**18)
    def test_all_regimes_finite_and_real_deflated(self):
        for name in REGIMES:
            c=compare(name,50)
            self.assertTrue(all(math.isfinite(v) for v in c.values()))
            self.assertLess(c['real_equity'],c['equity'])
    def test_content_regressions(self):
        self.assertEqual(len(SOURCES),36)
        self.assertIn('no evidence-backed winner',content('executive-summary').lower())
        self.assertIn('Not reviewed',content('suggestions'))
        self.assertIn('actual household answers are missing',content('estate-thresholds'))
        self.assertIn('not enacted law',content('law-watchlist').lower())
        self.assertIn('scheduled for repeal January 1, 2030',content('law-watchlist'))
        self.assertIn('FHFA publishes repeat-sales',content('black-swan-scenarios'))
        self.assertIn('no dollar forecast is published',content('projections').lower())

    def test_public_currency_is_only_verified_current_law(self):
        public=' '.join(content(key) for key,_,_ in PAGES)
        amounts=set(re.findall(r'\$[\d,]+(?:\.\d+)?',public))
        allowed={'$10','$7,000','$20,000','$125,000','$200,000','$250,000',
                 '$500,000','$1,044,590','$15,000,000','$15,480,000'}
        self.assertLessEqual(amounts,allowed)
        for invented in ('$1,000,000','$200,000 assessment','$48,000'):
            self.assertNotIn(invented,public)
        self.assertNotIn('SYNTHETIC_NOT_HOUSEHOLD',public)

    def test_public_pages_do_not_rely_on_retired_synthetic_scenario_rates(self):
        public=' '.join(content(key) for key,_,_ in PAGES)
        rates=set(re.findall(r'(?<![\w.])\d+(?:\.\d+)?%',public))
        allowed={'0%','1%','1.6%','2%','3.8%','4.3%','5%','9.1%','10%',
                 '13.7%','15%','20%','25%','40%'}
        self.assertLessEqual(rates,allowed)
    def test_public_copy_uses_generic_property_context(self):
        public_content=' '.join(content(key) for key,_,_ in PAGES).casefold()
        for pattern in CASE_SPECIFIC_PATTERNS:
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern,public_content,re.I))
        self.assertIn('for this generic scenario',public_content)
        self.assertIn('if some space is rented or used personally',public_content)
        self.assertIn('current root coordination.md',public_content)
        self.assertIn('jekyll exclusions do not restrict git access',public_content)

if __name__=='__main__': unittest.main()
