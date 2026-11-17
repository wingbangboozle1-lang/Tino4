"""Regression tests for privacy and evidence requirements of the public site."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import case_model as cm
import sitebuild
import verify

class PublicSitePrivacyTests(unittest.TestCase):
    def test_build_reads_no_household_inputs_and_emits_manifest_pages(self):
        source = (ROOT / "sitebuild.py").read_text(encoding="utf-8")
        self.assertNotIn("import models", source)
        self.assertNotIn(".read_text(", source)
        self.assertFalse((ROOT / "models.py").exists())
        sitebuild.build()
        manifest = json.loads((ROOT / "site-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest), verify.PAGE_COUNT)
        self.assertEqual(len(manifest), len(sitebuild.PAGES))
        self.assertTrue(all((ROOT.parent / path).is_file() for path in manifest))

    def test_every_published_table_row_has_official_source_and_status(self):
        sitebuild.build()
        failures = verify.verify()
        self.assertEqual(failures, [])

    def test_homepage_discloses_unresolved_historical_exposure(self):
        homepage = sitebuild.render("index.html", "Decision overview", "Start")
        self.assertIn("historical exposure is unresolved", homepage)
        self.assertIn("prior commits, pull-request views, forks, caches, downloads, or clones", homepage)
        self.assertIn("https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository", homepage)
        self.assertLess(homepage.index("historical exposure is unresolved"), homepage.index("What would change the answer?"))

    def test_no_owner_supplied_household_figures_or_placeholders_are_baked_into_site(self):
        sitebuild.build()
        for page in json.loads((ROOT / "site-manifest.json").read_text(encoding="utf-8")):
            raw = (ROOT.parent / page).read_text(encoding="utf-8")
            self.assertNotIn("Owner-supplied", raw)
            self.assertNotIn("owner-supplied", raw)
            self.assertNotIn("Owner-supplied", raw)
            self.assertNotIn("owner record", raw)
            self.assertNotIn("owner record", raw)
            self.assertNotIn("Owner figure", raw)
            self.assertNotIn("PROPERTY_A", raw)
            self.assertNotIn("PROPERTY_B", raw)

    def test_browser_script_never_stores_or_sends_inputs(self):
        script = (ROOT.parent / "assets/app.js").read_text(encoding="utf-8")
        self.assertNotIn("localStorage", script)
        self.assertNotIn("sessionStorage", script)
        self.assertNotIn("fetch(", script)
        self.assertNotIn("XMLHttpRequest", script)
        self.assertNotIn("sendBeacon", script)

    def test_manifest_has_no_duplicate_outputs(self):
        manifest = json.loads((ROOT / "site-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest), len(set(manifest)))

    def test_law_watchlist_distinguishes_enacted_from_ambiguous_or_unverified(self):
        page = sitebuild.render("pages/law-watchlist.html", "Law watchlist", "Law & process")
        self.assertIn("Enacted federal law", page)
        self.assertIn("Pending federal proposals", page)
        self.assertIn("Not verified", page)

    def test_requirement_tracker_and_investment_policy_cover_requested_gates(self):
        reqs = sitebuild.render("pages/requirements-tracker.html", "Requirements tracker", "Decision")
        self.assertIn("same tax year as inheritance", reqs)
        self.assertIn("Imputed rent", reqs)
        self.assertIn("Prop H", reqs)
        self.assertIn("Transfer tax and recording fees", reqs)
        policy = sitebuild.render("pages/investment-policy.html", "Investment policy draft", "Stress tests")
        self.assertIn("3-month to 2-year Treasuries", policy)
        self.assertIn("24–36 months", policy)
        self.assertIn("Agree before the figures arrive", policy)

    def test_california_surcharge_and_capital_gains_sources_are_explicit(self):
        page = sitebuild.render("pages/estate-thresholds.html", "Estate-tax thresholds", "Law & process")
        self.assertIn("$1,000,000", page)
        self.assertIn("ordinary income", page)
        self.assertIn("$100 per $10,000", page)
        self.assertIn("ftb_540", str(sitebuild.SOURCES))
        self.assertIn("ftb_540es", str(sitebuild.SOURCES))
        self.assertIn("line 62", str(sitebuild.SOURCES["ftb_540"]))

    def test_transfer_year_sale_uses_entered_proceeds_basis_and_costs(self):
        script = r'''
const fs = require('fs');
const vm = require('vm');
const values = {
  'sell-value': '120', 'sell-basis': '100', 'sell-costs': '10',
  'sell-dtt': '0', 'sell-other': '0', 'sell-timing': 'transfer', 'sell-121': '0'
};
const elements = new Map();
function element(id) {
  if (!elements.has(id)) elements.set(id, {
    value: values[id] || '', textContent: '',
    addEventListener(type, callback) { this[`${type}Handler`] = callback; }
  });
  return elements.get(id);
}
global.document = { getElementById: element, querySelectorAll: () => [] };
global.window = { print() {} };
vm.runInThisContext(fs.readFileSync('assets/app.js', 'utf8'));
element('sell-run').clickHandler();
console.log(element('sell-result').textContent);
element('sell-value').value = '80';
element('sell-costs').value = '0';
element('sell-run').clickHandler();
console.log(element('sell-result').textContent);
'''
        output = subprocess.check_output(["node", "-e", script], cwd=ROOT.parent, text=True)
        self.assertIn("$10 (potential gain", output)
        self.assertIn("-$20 (potential loss", output)
        self.assertNotIn("gain is modeled at $0", output)

    def test_phase_model_compares_crash_timing_and_rising_market_lag(self):
        script = r'''const model = require(process.argv[1]);
const early = model.simulate({amount: 24000, months: 24, treasuryYieldPct: 0, equityDriftPct: 0, crashPct: 57, crashMonth: 1});
if (Math.abs(early.immediateShockLoss - 13680) > 1 || early.phasedShockLoss !== 0 || !(early.phasedEnding > early.immediateEnding)) process.exit(1);
const after = model.simulate({amount: 24000, months: 24, treasuryYieldPct: 0, equityDriftPct: 0, crashPct: 57, crashMonth: 25});
if (Math.abs(after.immediateShockLoss - after.phasedShockLoss) > 1 || Math.abs(after.phasedEnding - after.immediateEnding) > 1) process.exit(2);
const rising = model.simulate({amount: 24000, months: 24, treasuryYieldPct: 0, equityDriftPct: 8, crashPct: 0, crashMonth: 13});
if (!(rising.immediateEnding > rising.phasedEnding)) process.exit(3);
'''
        result = subprocess.run(["node", "-e", script, str(ROOT.parent / "assets/phase-model.js")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_decision_completeness_rules_are_published_generically(self):
        decision = sitebuild.render("pages/decision-analysis.html", "Compare paths", "Decision")
        self.assertIn("sale in the transfer tax year", decision)
        self.assertIn("not as a tax-free assumption", decision)
        self.assertIn("Sale proceeds waterfall", decision)
        self.assertIn("unrecaptured section 1250 gain", decision)
        self.assertIn("Like-kind exchange (section 1031)", decision)
        self.assertIn("Local-only sale-tax overlay tool", decision)
        self.assertIn("sell-run", decision)
        prop_tax = sitebuild.render("pages/property-tax.html", "Property-tax rules", "Law & process")
        self.assertIn("No carry-forward of the value limit", prop_tax)
        self.assertIn("Tax rate area (TRA)", prop_tax)
        estate = sitebuild.render("pages/estate-thresholds.html", "Estate-tax thresholds", "Law & process")
        self.assertIn("Estate liquidity plan", estate)
        self.assertIn("each $100,000 of taxable income above $1,000,000 adds $1,000", estate)
        log = sitebuild.render("pages/decision-log.html", "Decision log", "Adviser & evidence")
        self.assertIn("Pre-commitment criteria", log)
        flagged = sitebuild.render("pages/flagged-for-review.html", "Flagged for review", "Adviser & evidence")
        self.assertIn("carry-forward premise", flagged)
        self.assertIn("Proposal digests are not enacted schedules", flagged)
        glossary = sitebuild.render("pages/glossary.html", "Glossary", "Adviser & evidence")
        self.assertIn("Unrecaptured section 1250 gain", glossary)
        self.assertIn("Imputed rent", glossary)
        watchlist = sitebuild.render("pages/law-watchlist.html", "Law watchlist", "Law & process")
        self.assertIn("Residential vacancy taxes", watchlist)
        self.assertIn("Local transfer-tax restructuring proposals", watchlist)

    def test_privacy_boundary_holds_for_research_resolution(self):
        decision = sitebuild.render("pages/decision-analysis.html", "Compare paths", "Decision")
        self.assertNotIn("Cupertino", decision)
        self.assertNotIn("Sunset", decision)
        self.assertNotIn("Santa Clara", decision)
        flagged = sitebuild.render("pages/flagged-for-review.html", "Flagged for review", "Adviser & evidence")
        self.assertIn("withheld from this public site", flagged)

if __name__ == "__main__":
    unittest.main()


class CaseModelTests(unittest.TestCase):
    """Arithmetic the published pages depend on, tested at the rule level."""

    def test_money_is_rounded_to_the_nearest_ten_dollars(self):
        self.assertEqual(cm.r10(550_537), 550_540)
        self.assertEqual(cm.r10(7_207), 7_210)
        self.assertEqual(cm.usd(550_537), "$550,540")
        self.assertEqual(cm.usd(-1_234), "-$1,230")
        self.assertEqual(cm.usd(0), "none")
        self.assertEqual(cm.usd(2.4), "none")
        self.assertEqual(cm.usd(5), "$10")
        self.assertEqual(cm.usd(-4), "none")
        self.assertEqual(cm.r10(2_744_999.6), 2_745_000)
        self.assertTrue(cm.rounding_is_clean(9_499))
        for row in cm.path_table(2045, 30, "sequence"):
            self.assertEqual(cm.r10(float(row["terminal_econ"])) % 10, 0)

    def test_prop_19_cap_adds_the_excess_over_the_prior_base_plus_allowance(self):
        # section 63.2(d): new value = prior taxable value + max(0, value - (prior + allowance))
        taxable, addition, met = cm.prop19_taxable_value(1_000_000, 2_600_000, 1_044_586)
        self.assertFalse(met)
        self.assertAlmostEqual(addition, 555_414)
        self.assertAlmostEqual(taxable, 1_555_414)
        taxable, addition, met = cm.prop19_taxable_value(1_000_000, 1_900_000, 1_044_586)
        self.assertTrue(met)
        self.assertEqual(addition, 0.0)
        self.assertEqual(taxable, 1_000_000)

    def test_allowance_is_carried_forward_and_never_frozen(self):
        self.assertAlmostEqual(cm.PROP19_ALLOWANCE, 1_044_586)
        self.assertGreater(cm.prop19_allowance(2045), cm.PROP19_ALLOWANCE)
        self.assertGreater(cm.prop19_allowance(2050), cm.prop19_allowance(2040))
        self.assertEqual(cm.prop19_allowance(2025), cm.PROP19_ALLOWANCE)

    def test_claim_beats_reassessment_but_costs_more_than_an_untouched_base(self):
        for scenario in ("steady", "sequence"):
            for year in (2040, 2045, 2050):
                claim = cm.a_state_at(year, scenario, "claim")
                rent_branch = cm.a_state_at(year, scenario, "rent")
                keep = cm.a_state_at(year, scenario, "keep")
                self.assertLess(claim["tax"], rent_branch["tax"])
                self.assertGreater(claim["tax"], keep["tax"])
                self.assertAlmostEqual(claim["taxable"], claim["prior_taxable"] + claim["addition"])
                self.assertAlmostEqual(claim["cap"], claim["prior_taxable"] + claim["allowance"])

    def test_sale_in_the_transfer_year_is_neither_taxed_nor_deductible(self):
        value = cm.market_value_at(2045, "steady", "A")
        same_year = cm.sell_waterfall(value, value, 0, "none")
        self.assertEqual(same_year["gross_gain"], 0.0)
        self.assertEqual(same_year["income_tax"], 0.0)
        self.assertLess(same_year["net"], value)
        later = cm.sell_waterfall(value * 1.3, value, 5, "lived")
        self.assertGreater(later["gross_gain"], 0.0)
        self.assertLess(later["taxable_gain"], later["gross_gain"])
        rented = cm.sell_waterfall(value * 1.3, value, 2, "rented")
        self.assertGreater(rented["recapture"], 0.0)
        self.assertEqual(rented["exclusion"], 0.0)

    def test_staging_beats_an_immediate_buy_only_while_the_money_is_still_waiting(self):
        early = cm.staging_case(1_000_000, "2008", 6)
        self.assertGreater(early["difference"], 0)
        self.assertLess(early["immediate"], early["staged"])
        late = cm.staging_case(1_000_000, "2008", cm.STAGING_WINDOW_MONTHS + 6)
        self.assertLessEqual(late["difference"], 0)
        self.assertAlmostEqual(late["share_exposed"], 1.0)
        # with no crash to dodge, staging can only cost money: reinvestment risk
        for anchor in ("1929", "2008"):
            rising = cm.staging_case(1_000_000, anchor, cm.STAGING_WINDOW_MONTHS, crash=False)
            self.assertLess(rising["staged"], rising["immediate"])
            self.assertGreater(rising["difference"], -rising["immediate"])

    def test_reinvestment_risk_is_a_real_cost_of_waiting(self):
        risk = cm.reinvestment_risk(1_000_000, 30, 0.01, 0.07)
        self.assertGreater(risk["price_increase"], risk["bills_income"])
        self.assertGreater(risk["give_up_annual"], 0)
        zero_wait = cm.reinvestment_risk(1_000_000, 0, 0.01, 0.07)
        self.assertEqual(zero_wait["bills_income"], 0.0)
        self.assertEqual(zero_wait["price_increase"], 0.0)

    def test_block_sequence_compounds_below_its_own_average(self):
        average = cm.block_average()
        self.assertLess(average["equity"], average["equity_arith"])
        self.assertLess(average["house"], average["house_arith"])
        sequence, flat = cm.sequence_vs_flat(1_000_000, 30, average["house_arith"])
        self.assertLess(sequence, flat)

    def test_bust_at_the_transfer_date_reorders_the_paths(self):
        steady = cm.path_table(2045, 30, "steady")
        bust = cm.path_table(2045, 30, "bust_at_transfer")
        top_steady = steady[0]["name"]
        top_bust = bust[0]["name"]
        self.assertNotEqual(top_steady, top_bust)
        sell = next(row for row in bust if row["name"] == cm.PATHS[2][0])
        live = next(row for row in bust if row["name"] == cm.PATHS[0][0])
        self.assertGreater(live["terminal_real"], sell["terminal_real"])
        self.assertEqual([row["rank"] for row in bust], list(range(1, 8)))

    def test_every_path_is_priced_at_one_date_one_horizon_and_stays_comparable(self):
        for scenario in cm.SCENARIOS:
            rows = cm.path_table(2045, 30, scenario)
            self.assertEqual(len(rows), 7)
            self.assertTrue(all(row["kind"] in {"pure", "mixed"} for row in rows))
            self.assertTrue(all(isinstance(row["driver"], str) and len(row["driver"]) > 40 for row in rows))
            self.assertAlmostEqual(rows[0]["deflator"], rows[-1]["deflator"])
            self.assertLessEqual(rows[-1]["terminal_econ"], rows[0]["terminal_econ"])
        for horizon, rows in cm.horizon_matrix(2045, "sequence").items():
            self.assertEqual(len(rows), 7, horizon)
        for year, rows in cm.transfer_year_matrix(30, "steady").items():
            self.assertEqual(len(rows), 7, year)

    def test_property_b_is_reported_once_and_not_double_counted(self):
        b = cm.b_reference(2045, "steady")
        self.assertGreater(b["gross_rent"], b["costs"])
        self.assertAlmostEqual(b["net_rental"],
                               b["gross_rent"] * (1 - cm.VACANCY - cm.MANAGEMENT) - b["costs"])
        for scenario in ("steady", "sequence"):
            rows = cm.path_table(2045, 30, scenario)
            self.assertFalse(any("Property B" in str(row["name"]) and "reference" in str(row["name"])
                                 for row in rows))
            # no path row may quote a portfolio return as a cash flow: it is only
            # ever credited through compounding
            self.assertTrue(all(row["flow_cash"] <= row["proceeds"] * 0.1 or row["proceeds"] == 0.0
                                for row in rows), scenario)

    def test_estate_exposure_starts_only_above_the_exclusion(self):
        rows = cm.estate_rows(2045)
        self.assertEqual(rows[0]["tax_on_excess"], 0.0)
        self.assertGreater(rows[-1]["excess"], 0.0)
        self.assertAlmostEqual(rows[-1]["tax_on_excess"], rows[-1]["excess"] * cm.ESTATE_TOP_RATE)
        self.assertGreater(cm.FED_EXCL_2027, cm.FED_EXCL_2026)
        self.assertEqual(cm.SF_STATE_TAX, 0.0)

    def test_decision_log_publishes_priced_decision_rules(self):
        sitebuild.build()
        page = (ROOT.parent / "pages/decision-log.html").read_text(encoding="utf-8")
        self.assertIn("Pre-agreed decision criteria", page)
        self.assertIn("before the figures are read", page)
        self.assertIn("block sequence", page)
        for path in ("pages/decision-analysis.html", "pages/model-figures.html", "pages/economic-baselines.html"):
            rendered = (ROOT.parent / path).read_text(encoding="utf-8")
            self.assertIn("<table", rendered, path)
            self.assertIn("badge", rendered, path)
            self.assertIn("class=\"source\"", rendered, path)

    def test_self_check_reports_no_broken_assumption(self):
        result = cm.self_check()
        self.assertTrue(all(result.values()), result)
