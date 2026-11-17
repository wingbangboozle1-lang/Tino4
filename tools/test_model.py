"""Arithmetic and privacy tests for the rounded scenario model in sitebuild.py.

These tests pin the derivations the published tables depend on: the rounding
policy, the tax-rate derivation from the reported bill history, the Proposition
19 value formula, the proceeds waterfall identity, the staging arithmetic, and
the absence of identifiers or unrounded amounts in the generated pages.
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import sitebuild  # noqa: E402


class RoundingTests(unittest.TestCase):
    def test_amounts_round_to_the_nearest_ten_dollars(self):
        self.assertEqual(sitebuild.r10(7_204), 7_200)
        self.assertEqual(sitebuild.r10(7_205), 7_210)
        self.assertEqual(sitebuild.usd(3_100_004), "$3,100,000")
        self.assertEqual(sitebuild.usd(-12_341), "-$12,340")

    def test_zero_is_never_printed_as_a_dollar_figure(self):
        self.assertEqual(sitebuild.usd(2), "no modeled amount")
        self.assertEqual(sitebuild.signed_usd(1), "no modeled difference")
        self.assertNotIn("$0", sitebuild.usd(1_234_567))

    def test_signed_delta_words_read_as_comparisons(self):
        self.assertTrue(sitebuild.signed_usd(5_000).startswith("plus $5,000"))
        self.assertTrue(sitebuild.signed_usd(-5_000).startswith("minus $5,000"))


class InputDerivationTests(unittest.TestCase):
    def test_effective_rate_is_the_mean_ratio_of_the_reported_bills(self):
        expected = sum(t / a for (_, t, a) in sitebuild.A_BILL_HISTORY if t and a)
        expected /= len([1 for (_, t, _) in sitebuild.A_BILL_HISTORY if t])
        self.assertAlmostEqual(sitebuild.RATE_A, expected, places=10)
        self.assertGreater(sitebuild.RATE_A, 0.010)
        self.assertLess(sitebuild.RATE_A, 0.020)

    def test_rate_range_brackets_the_mean(self):
        self.assertLessEqual(sitebuild.RATE_A_LOW, sitebuild.RATE_A)
        self.assertGreaterEqual(sitebuild.RATE_A_HIGH, sitebuild.RATE_A)
        self.assertGreater(sitebuild.RATE_B, sitebuild.RATE_A)

    def test_tax_bill_uses_the_derived_rate_on_the_assessed_value(self):
        bill = sitebuild.tax_bill(2026, 2026, "keep-base")
        self.assertAlmostEqual(bill, sitebuild.A_ASSESSED_2026 * sitebuild.RATE_A, places=6)

    def test_carrying_total_equals_the_sum_of_its_lines(self):
        items = sitebuild.carrying_cost(2045, 2045, "prop19", None, "A")
        self.assertAlmostEqual(sum(items.values()), sitebuild.carrying_total(2045, 2045, "prop19"))
        self.assertLess(items["Solar export credit"], 0)


class AssessmentBranchTests(unittest.TestCase):
    def test_no_transfer_keeps_the_factored_base_growing_by_the_statutory_ceiling(self):
        self.assertAlmostEqual(sitebuild.assessed_untransferred(2027), sitebuild.A_ASSESSED_2026 * 1.02, places=6)
        self.assertEqual(sitebuild.assessed_at_transfer(2045, "keep-base"), sitebuild.assessed_untransferred(2045))

    def test_proposition_19_adds_only_the_amount_above_base_plus_limit(self):
        base = sitebuild.assessed_untransferred(2045)
        value = sitebuild.market_value(2045)
        limit = sitebuild.boe_cap(2045)
        self.assertAlmostEqual(sitebuild.assessed_at_transfer(2045, "prop19"), base + (value - base - limit), places=6)
        self.assertGreater(sitebuild.assessed_at_transfer(2045, "prop19"), base)
        self.assertLess(sitebuild.assessed_at_transfer(2045, "prop19"), value)

    def test_the_claim_adds_nothing_while_value_sits_inside_base_plus_limit(self):
        original = sitebuild.A_MARKET_2026
        try:
            sitebuild.A_MARKET_2026 = 500_000
            self.assertAlmostEqual(sitebuild.assessed_at_transfer(2026, "prop19"), sitebuild.assessed_untransferred(2026), places=6)
        finally:
            sitebuild.A_MARKET_2026 = original

    def test_no_claim_reassesses_at_fair_cash_value(self):
        self.assertEqual(sitebuild.assessed_at_transfer(2045, "reassessed"), sitebuild.market_value(2045))

    def test_the_exclusion_limit_is_adjusted_every_other_february(self):
        self.assertEqual(sitebuild.boe_cap(2025), sitebuild.BOE_CAP)
        self.assertEqual(sitebuild.boe_cap(2026), sitebuild.BOE_CAP)
        self.assertAlmostEqual(sitebuild.boe_cap(2027), sitebuild.BOE_CAP * 1.0215, places=4)
        self.assertAlmostEqual(sitebuild.boe_cap(2045), sitebuild.BOE_CAP * 1.0215 ** 10, places=2)


class ProceedsWaterfallTests(unittest.TestCase):
    def test_waterfall_lines_sum_to_net_proceeds(self):
        deal = sitebuild.sale_net(4_000_000, 3_000_000)
        self.assertAlmostEqual(deal["value"] - deal["frictions"] - deal["transfer_tax"] - sitebuild.RECORDING_FLAT, deal["net"], places=6)
        self.assertAlmostEqual(deal["net"] - deal["tax"], deal["after_tax"], places=6)

    def test_transfer_tax_default_is_the_county_rate_not_county_plus_city(self):
        self.assertAlmostEqual(sitebuild.TRANSFER_TAX_RATE, 0.0011, places=10)
        self.assertAlmostEqual(4_000_000 * sitebuild.TRANSFER_TAX_RATE, 4_400, places=6)

    def test_a_sale_at_basis_owes_no_modeled_income_tax(self):
        deal = sitebuild.sale_net(3_000_000, 3_000_000)
        self.assertEqual(deal["tax"], 0)

    def test_exclusion_reduces_tax_and_never_makes_it_negative(self):
        with_exclusion = sitebuild.sale_net(5_000_000, 3_000_000, exclusion=sitebuild.SECTION_121_EXCLUSION)
        without = sitebuild.sale_net(5_000_000, 3_000_000)
        self.assertLess(with_exclusion["tax"], without["tax"])
        self.assertGreaterEqual(with_exclusion["tax"], 0)

    def test_depreciation_is_recaptured_before_capital_gain_rates_apply(self):
        deal = sitebuild.sale_net(4_000_000, 3_800_000, depreciation=2_000_000)
        self.assertEqual(deal["recapture"], deal["gain"])
        self.assertAlmostEqual(deal["tax"], deal["gain"] * sitebuild.RECAPTURE_COMBINED, places=6)

    def test_annual_depreciation_uses_the_27_5_year_recovery_over_improvements(self):
        self.assertAlmostEqual(sitebuild.annual_depreciation(2045) * 27.5, sitebuild.market_value(2045) * 0.8, places=6)


class PathRankingTests(unittest.TestCase):
    def test_selling_in_the_transfer_year_leads_every_hold_path_at_both_horizons(self):
        for horizon in (2055, 2070):
            ranked = sitebuild.ranked_rows(horizon=horizon)
            self.assertEqual(ranked[0][0], sitebuild.SELL_LABEL, f"horizon {horizon}")
            self.assertEqual(ranked[0][2], 0)

    def test_selling_still_leads_in_all_three_growth_scenarios(self):
        for growth in sitebuild.GROWTH_HOME.values():
            ranked = sitebuild.ranked_rows(horizon=2070, growth=growth)
            self.assertEqual(ranked[0][0], sitebuild.SELL_LABEL)

    def test_the_break_even_growth_rate_sits_above_the_long_run_scenario(self):
        break_even = sitebuild.break_even_growth(sitebuild.RENT_LABEL)
        self.assertGreater(break_even, sitebuild.GROWTH_HOME["long-run"])
        self.assertLess(break_even, 0.20)

    def test_break_even_is_consistent_with_the_gap_it_describes(self):
        rows_at_break = sitebuild.path_outcomes(horizon=2070, growth=sitebuild.GROWTH_HOME["long-run"])
        self.assertLess(rows_at_break[sitebuild.RENT_LABEL]["value"], rows_at_break[sitebuild.SELL_LABEL]["value"])

    def test_parking_lags_investing_at_once_when_prices_only_rise(self):
        rows = sitebuild.path_outcomes(horizon=2070)
        self.assertLess(rows["Sell, park 30 months in Treasuries, then buy"]["value"], rows[sitebuild.SELL_LABEL]["value"])
        self.assertLess(rows["Sell, buy in thirty equal monthly tranches"]["value"], rows["Sell, park 30 months in Treasuries, then buy"]["value"])

    def test_earlier_transfer_years_do_not_change_the_ranking(self):
        for transfer_year in (2040, 2045, 2050):
            ranked = sitebuild.ranked_rows(transfer_year=transfer_year, horizon=2070)
            self.assertEqual(ranked[0][0], sitebuild.SELL_LABEL)

    def test_a_softer_portfolio_narrows_the_gap_and_can_reverse_the_ranking(self):
        soft = sitebuild.ranked_rows(horizon=2070, rate_key="soft")
        base = sitebuild.ranked_rows(horizon=2070, rate_key="baseline")
        self.assertLess(abs(soft[1][2]), abs(base[1][2]))
        self.assertEqual(base[0][0], sitebuild.SELL_LABEL)
        self.assertNotEqual(soft[0][0], sitebuild.SELL_LABEL)

    def test_the_soft_ranking_is_stated_as_a_tested_switch_not_a_forecast(self):
        page = sitebuild.render("pages/executive-summary.html", "Executive summary", "Start")
        self.assertIn("Portfolio returns run at the soft scenario", page)
        self.assertIn("written investment policy", page)


class StagingTests(unittest.TestCase):
    def test_flat_index_makes_buying_now_and_buying_later_equivalent_before_interest(self):
        levels = sitebuild.index_path(60, 0, 0)
        self.assertAlmostEqual(sitebuild.staging_outcome(100_000, levels, 60, ("now",)), 100_000, places=6)

    def test_parking_beats_buying_at_the_top_when_the_market_falls_and_stays_down(self):
        levels = sitebuild.index_path(120, 89, 34)
        immediate = sitebuild.staging_outcome(1_000_000, levels, 120, ("now",))
        parked = sitebuild.staging_outcome(1_000_000, levels, 120, ("park", 36))
        self.assertGreater(parked, immediate)

    def test_parking_loses_when_the_market_only_rises(self):
        levels = sitebuild.index_path(120, 0, 0, None, 0.06)
        immediate = sitebuild.staging_outcome(1_000_000, levels, 120, ("now",))
        parked = sitebuild.staging_outcome(1_000_000, levels, 120, ("park", 36))
        self.assertLess(parked, immediate)

    def test_tranche_buys_land_between_the_two_extremes_in_a_falling_market(self):
        levels = sitebuild.index_path(120, 57, 17)
        immediate = sitebuild.staging_outcome(1_000_000, levels, 120, ("now",))
        tranched = sitebuild.staging_outcome(1_000_000, levels, 120, ("dca", 24))
        parked = sitebuild.staging_outcome(1_000_000, levels, 120, ("park", 24))
        self.assertGreater(tranched, immediate)
        self.assertLess(tranched, parked)

    def test_the_index_path_never_goes_negative(self):
        for shape in sitebuild.STAGING_SHAPES:
            levels = sitebuild.index_path(shape[1], shape[2], shape[3], shape[4])
            self.assertTrue(all(level > 0 for level in levels))


class PrivacyInvariantsTests(unittest.TestCase):
    CURRENCY = re.compile(r"(?<![\w])\$\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
    OFFICIAL = {"15000000", "15480000", "20000", "1044586", "1022600", "1000000", "250000", "500000", "7000"}

    def test_every_dollar_amount_in_the_site_is_a_multiple_of_ten(self):
        pages = [Path(sitebuild.ROOT / name) for name, _, _ in sitebuild.PAGES]
        offenders = []
        for page in pages:
            for amount in self.CURRENCY.findall(page.read_text(encoding="utf-8")):
                normalized = amount.replace(",", "")
                if "." in normalized or (len(normalized) < 2 or (not normalized.endswith("0") and normalized not in self.OFFICIAL)):
                    offenders.append((page.name, amount))
        self.assertEqual(offenders, [])

    def test_no_locality_or_identifier_appears_in_the_generator(self):
        source = (ROOT / "sitebuild.py").read_text(encoding="utf-8").lower()
        for token in ("cupertino", "san francisco", "santa clara", "bayview", "inglenook", "95014", "94122", "street", "avenue", "boulevard"):
            self.assertNotIn(token, source, f"{token} found in the generator")

    def test_generated_pages_are_byte_identical_when_rebuilt(self):
        sitebuild.build()
        first = {name: (sitebuild.ROOT / name).read_bytes() for name, _, _ in sitebuild.PAGES}
        sitebuild.build()
        for name, payload in first.items():
            self.assertEqual(payload, (sitebuild.ROOT / name).read_bytes(), f"{name} is not reproducible")

    def test_the_public_tree_publishes_no_unrounded_household_report(self):
        # The reported figures are all multiples of ten, so this checks that the
        # model did not leak a precise intermediate (e.g. an unrounded bill).
        for page in ("pages/property-profiles.html", "pages/projections.html", "pages/operating-costs.html"):
            text = (sitebuild.ROOT / page).read_text(encoding="utf-8")
            self.assertNotIn(".00", text)
            self.assertNotIn("<script>", text)
            self.assertNotIn("data:image", text)


if __name__ == "__main__":
    unittest.main()
