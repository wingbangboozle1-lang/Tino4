"""Regression tests for the public historical-price stress calculation."""
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_7adb71fc"))

import phased_history as history


class SourcedSeriesTests(unittest.TestCase):
    def test_series_metadata_and_public_sources(self):
        depression = history.SERIES["1929"]
        crisis = history.SERIES["2008"]
        self.assertEqual(depression.series_id, "M1109BUSM293NNBR")
        self.assertIn("National Bureau of Economic Research", depression.provider)
        self.assertTrue(depression.source_url.startswith("https://fred.stlouisfed.org/"))
        self.assertEqual(depression.frequency, "monthly")
        self.assertEqual(depression.unit, "dollars per share (published index series units)")
        self.assertEqual((depression.date_label(0), depression.date_label(120)), ("1929-09", "1939-09"))
        self.assertEqual(crisis.series_id, "SPASTT01USQ661N")
        self.assertIn("OECD", crisis.provider)
        self.assertTrue(crisis.source_url.startswith("https://fred.stlouisfed.org/"))
        self.assertEqual(crisis.frequency, "quarterly")
        self.assertEqual(crisis.unit, "index, 2015=100")
        self.assertEqual((crisis.date_label(0), crisis.date_label(40)), ("2007 Q4", "2017 Q4"))
        self.assertIn("price-only", history.__doc__ or "")

    def test_selected_observations_match_fetched_source_tables(self):
        depression = history.official_observations("1929")
        self.assertEqual(
            [(row["date"], row["value"]) for row in depression],
            [
                ("1929-09", 362.35),
                ("1930-09", 225.00),
                ("1931-09", 118.35),
                ("1932-09", 71.00),
                ("1932-06", 46.85),
                ("1939-09", 144.40),
            ],
        )
        crisis = history.official_observations("2008")
        self.assertEqual(
            [(row["date"], row["value"]) for row in crisis],
            [
                ("2007 Q4", 92.707380),
                ("2008 Q4", 53.643950),
                ("2009 Q1", 47.717500),
                ("2009 Q4", 66.322940),
                ("2010 Q4", 71.586930),
                ("2017 Q4", 116.875200),
            ],
        )
        for row in (*depression, *crisis):
            self.assertTrue(row["source_url"].startswith("https://fred.stlouisfed.org/data/"))
            self.assertTrue(row["series_id"])

    def test_price_only_drawdowns_use_the_peak_preceding_the_trough(self):
        depression = history.price_only_peak_to_trough("1929")
        self.assertEqual((depression["peak_date"], depression["trough_date"]), ("1929-09", "1932-06"))
        self.assertAlmostEqual(depression["drawdown_pct"], -87.0705, places=3)
        crisis = history.price_only_peak_to_trough("2008")
        self.assertEqual((crisis["peak_date"], crisis["trough_date"]), ("2007 Q4", "2009 Q1"))
        self.assertAlmostEqual(crisis["drawdown_pct"], -48.5289, places=3)

    def test_curve_snapshot_has_all_initial_ladder_rungs(self):
        self.assertEqual(history.TREASURY_CURVE["as_of"], "2026-11-13")
        self.assertEqual(history.TREASURY_CURVE["rates_percent"], {3: 4.32, 6: 4.42, 12: 4.65, 24: 4.88})
        self.assertTrue(history.TREASURY_CURVE["source_url"].startswith("https://home.treasury.gov/"))
        self.assertTrue(history.TREASURY_BILLS_URL.startswith("https://www.treasurydirect.gov/"))
        self.assertTrue(history.TREASURY_REINVEST_URL.startswith("https://www.treasurydirect.gov/"))


class HistoricalPageTests(unittest.TestCase):
    def test_page_has_public_sources_blank_local_input_and_price_only_caveats(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from build_history_page import render

        html = render()
        self.assertIn('id="market-form"', html)
        self.assertIn('id="market-principal"', html)
        self.assertIn('value=""', html)
        self.assertIn('not a realized historical portfolio', html.lower())
        self.assertIn('not dividend-inclusive', (history.__doc__ or ""))
        self.assertIn("M1109BUSM293NNBR", html)
        self.assertIn("SPASTT01USQ661N", html)
        self.assertIn("2026-11-13", html)
        self.assertIn("not a total-return decline", html)
        self.assertIn('type="application/json"', html)
        self.assertIn('../assets/history.js', html)
        self.assertNotIn('localStorage', html)

    def test_calculator_source_is_local_only(self):
        script = (ROOT / "assets/history.js").read_text(encoding="utf-8")
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sendBeacon", "document.cookie"):
            self.assertNotIn(forbidden, script)
        self.assertIn("roundToTen", script)


class HistoricalPathTests(unittest.TestCase):
    def test_comparison_has_immediate_24_and_36_month_paths(self):
        for series_key in history.SERIES:
            results = history.compare_paths(series_key)
            self.assertEqual(
                [(result.path_key, result.wait_months) for result in results],
                [
                    ("immediate", 0),
                    ("bill-roll", 24),
                    ("four-rung-ladder", 24),
                    ("bill-roll", 36),
                    ("four-rung-ladder", 36),
                ],
            )
            for result in results:
                self.assertTrue(math.isfinite(result.terminal_per_starting_unit))
                self.assertGreater(result.terminal_per_starting_unit, 0)
                self.assertLessEqual(result.maximum_observed_drawdown_pct, 0)
                self.assertEqual(result.terminal_date, history.SERIES[series_key].date_label(40 if series_key == "2008" else 120))

    def test_model_results_are_reproducible_and_not_labeled_total_return(self):
        depression = history.compare_paths("1929")
        self.assertAlmostEqual(depression[0].terminal_per_starting_unit, 0.39850973, places=7)
        self.assertAlmostEqual(depression[1].terminal_per_starting_unit, 2.18394094, places=7)
        self.assertAlmostEqual(depression[2].terminal_per_starting_unit, 2.19180724, places=7)
        crisis = history.compare_paths("2008")
        self.assertAlmostEqual(crisis[0].terminal_per_starting_unit, 1.26068928, places=7)
        self.assertAlmostEqual(crisis[1].terminal_per_starting_unit, 1.94812032, places=7)
        self.assertAlmostEqual(crisis[2].terminal_per_starting_unit, 1.95513722, places=7)
        self.assertIn("price-index", depression[0].path_label)
        self.assertIn("not dividend-inclusive total returns", history.__doc__ or "")

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            history.simulate_path("unknown", "immediate")
        with self.assertRaises(ValueError):
            history.simulate_path("1929", "bill-roll", 18)
        with self.assertRaises(ValueError):
            history.simulate_path("2008", "bill-roll", 36, 0)

    def test_currency_rounding_is_to_nearest_ten(self):
        self.assertEqual(history.round_money_to_10(14), 10)
        self.assertEqual(history.round_money_to_10(15), 20)
        self.assertEqual(history.round_money_to_10(24), 20)
        self.assertEqual(history.round_money_to_10(25), 30)
        with self.assertRaises(ValueError):
            history.round_money_to_10(-10)


if __name__ == "__main__":
    unittest.main()
