#!/usr/bin/env python3
"""Arithmetic and content regression tests for the rounded case model."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '_7eff7e24'))
import case  # noqa: E402
from case import rounded, money, prop19_assessment, estate_tax, factor_check  # noqa: E402


class TestRounding(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(rounded(5), 10)      # 0.5 rounds up
        self.assertEqual(rounded(4), 0)
        self.assertEqual(rounded(15), 20)
        self.assertEqual(rounded(7207), 7210)
        self.assertEqual(rounded(550537), 550540)

    def test_all_owner_inputs_rounded(self):
        for hist in (case.A_HISTORY, case.B_HISTORY):
            for tax, av in hist.values():
                if tax is not None:
                    self.assertEqual(tax, rounded(tax))
                self.assertEqual(av, rounded(av))
        self.assertEqual(case.A_VALUE_2026, rounded(case.A_VALUE_2026))
        self.assertEqual(case.B_VALUE_2026, rounded(case.B_VALUE_2026))

    def test_money_display(self):
        self.assertEqual(money(-1234), '\u2212$1,230')
        self.assertEqual(money(550540), '$550,540')


class TestProp19(unittest.TestCase):
    def test_formula(self):
        # old base + (market - old base - allowance) when market exceeds
        self.assertEqual(prop19_assessment(3_100_000, 550_540, 1_044_590), 550_540 + 3_100_000 - 550_540 - 1_044_590)
        # below the allowance: base preserved
        self.assertEqual(prop19_assessment(1_000_000, 550_540, 1_044_590), 550_540)


class TestProjections(unittest.TestCase):
    def test_value_growth(self):
        rows = case.a_projection(2045)
        self.assertEqual(len(rows), 51)
        self.assertEqual(rows[0]['year'], 2026)
        self.assertAlmostEqual(rows[0]['value'], 3_100_000)
        self.assertAlmostEqual(rows[1]['value'], 3_100_000 * 1.03)
        # rent/sell assessment resets at transfer then grows 2%
        at = rows[2045 - 2026]
        self.assertAlmostEqual(at['av_rent'], at['value'])
        nxt = rows[2046 - 2026]
        self.assertAlmostEqual(nxt['av_rent'], at['av_rent'] * 1.02)
        # live path is always <= rent path
        for r in rows:
            self.assertLessEqual(r['av_live'], r['av_rent'] + 1e-6)

    def test_b_projection(self):
        rows = case.b_projection()
        self.assertEqual(len(rows), 51)
        self.assertAlmostEqual(rows[0]['av'], 114_250 * 1.02, delta=1)

    def test_costs_sign(self):
        ac = case.a_costs(2026)
        self.assertLess(ac['electricity'], 0)   # solar credit
        self.assertGreater(ac['water'], 0)


class TestFactorCheck(unittest.TestCase):
    def test_a_history_reconciles(self):
        verdicts = [v for _, _, _, v in factor_check(case.A_HISTORY)]
        self.assertNotIn('flag', verdicts)

    def test_b_2022_flag(self):
        result = {y: v for y, _, _, v in factor_check(case.B_HISTORY)}
        self.assertEqual(result[2022], 'flag')
        self.assertNotIn('flag', [v for y, v in result.items() if y != 2022])


class TestCompare(unittest.TestCase):
    def test_ranking_baseline(self):
        c = case.compare(2045, 20, 6000)
        self.assertGreater(c['sell'], c['rent'])
        self.assertGreater(c['rent'], c['live'])

    def test_break_even_stock_direction(self):
        r = case.break_even_stock(2045, 20, 6000)
        self.assertGreater(r, -0.02)
        self.assertLess(r, 0.12)
        low = case.compare(2045, 20, 6000, stock=r - 0.01)
        high = case.compare(2045, 20, 6000, stock=r + 0.01)
        self.assertLess(low['sell'], low['rent'])
        self.assertGreater(high['sell'], high['rent'])

    def test_rent_grid_monotonic(self):
        prev = 0
        for rent in (4000, 5000, 6000, 7000):
            self.assertGreater(case.compare(2045, 20, rent)['rent'], prev)
            prev = case.compare(2045, 20, rent)['rent']

    def test_proceeds_scaled(self):
        c = case.compare(2050, 20, 6000)
        self.assertAlmostEqual(c['proceeds'], c['mv'] * 0.95, delta=1)


class TestEstate(unittest.TestCase):
    def test_40pct_on_excess(self):
        self.assertEqual(estate_tax(20_000_000, 15_000_000), 2_000_000)
        self.assertEqual(estate_tax(10_000_000, 15_000_000), 0)

    def test_exclusion_projection(self):
        self.assertAlmostEqual(case.exclusion_projection(2027, 0.025), 15_480_000)
        self.assertGreater(case.exclusion_projection(2045, 0.04), case.exclusion_projection(2045, 0))


class TestEpisodes(unittest.TestCase):
    def test_every_episode_has_keys(self):
        for e in case.EPISODES:
            self.assertTrue(e['keys'])
            self.assertTrue(e['facts'])


if __name__ == '__main__':
    unittest.main()
