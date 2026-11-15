"""Regression tests for the source-linked, privacy-bounded public output.

The suite rebuilds the site, runs the verifier, checks the rounding and privacy
rules, asserts a small set of figures that must not move without review, and
checks that the browser engine agrees with the Python engine.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import casedata as cd  # noqa: E402
from sources import SOURCES  # noqa: E402


class BuildAndStructureTests(unittest.TestCase):
    def test_build_emits_manifest_pages_and_no_case_outputs(self):
        subprocess.run([sys.executable, str(TOOLS / "build.py")], cwd=ROOT, check=True)
        manifest = json.loads((TOOLS / "site-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest), 18)
        self.assertEqual(len(manifest), len(set(manifest)))
        for item in manifest:
            self.assertTrue((ROOT / item).is_file(), item)
        self.assertFalse((ROOT / "assets" / "case-projections.csv").exists())

    def test_verifier_passes(self):
        subprocess.run([sys.executable, str(TOOLS / "verify.py")], cwd=ROOT, check=True)

    def test_requested_sections_are_present(self):
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("What would change the answer", index)
        self.assertIn("Property A", index)
        self.assertIn("Property B", index)
        brief = (ROOT / "pages" / "attorney-cpa-brief.html").read_text(encoding="utf-8")
        self.assertIn("Attorney and CPA", brief)
        self.assertIn("brief-sheet", brief)
        staged = (ROOT / "pages" / "phased-investing.html").read_text(encoding="utf-8")
        self.assertIn("24 to 36 month", staged)
        self.assertIn("Reinvestment risk, shown beside the headline", staged)
        paths = (ROOT / "pages" / "decision-analysis.html").read_text(encoding="utf-8")
        self.assertIn("Mixed", paths)
        self.assertIn("What would reverse it", paths)
        timeline = (ROOT / "pages" / "inheritance-process.html").read_text(encoding="utf-8")
        self.assertIn("timeline-list", timeline)
        self.assertIn("150 days", timeline)
        glossary = (ROOT / "pages" / "glossary.html").read_text(encoding="utf-8")
        self.assertIn("Proposition 19", glossary)
        suggestions = (ROOT / "pages" / "suggestions.html").read_text(encoding="utf-8")
        self.assertIn("review-choice", suggestions)
        self.assertIn("Nothing here is applied automatically", suggestions)


class RoundingAndPrivacyTests(unittest.TestCase):
    def test_rounding_is_to_the_nearest_ten_dollars_half_up(self):
        self.assertEqual(cd.money(5_965), 5_970)
        self.assertEqual(cd.money(7_003), 7_000)
        self.assertEqual(cd.money(7_207), 7_210)
        self.assertEqual(cd.money(550_537), 550_540)
        self.assertEqual(cd.money(1_044_586), 1_044_590)

    def test_no_personal_identifier_is_published(self):
        for path in sorted((ROOT / "pages").glob("*.html")) + [ROOT / "index.html"]:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("APN", text)
            self.assertNotIn("assessor's parcel", text.lower())
            self.assertNotIn("@", text.split("<footer>")[0].replace("mailto:", ""))

    def test_owner_data_module_holds_no_identifier_fields(self):
        source = (TOOLS / "casedata.py").read_text(encoding="utf-8")
        for forbidden in ("address", "owner_name", "trust_name", "account_number", "date_of_birth"):
            self.assertNotIn(forbidden + " =", source)
            self.assertNotIn(forbidden + "=", source)

    def test_privacy_page_discloses_the_residual_risk_and_history_limit(self):
        privacy = (ROOT / "pages" / "privacy.html").read_text(encoding="utf-8")
        self.assertIn("Not scrubbed", privacy)
        self.assertIn("public postal area", privacy)
        self.assertIn("Rounded to the nearest ten dollars", privacy)
        self.assertIn("noindex", privacy)
        flagged = (ROOT / "pages" / "flagged-for-review.html").read_text(encoding="utf-8")
        self.assertIn("Prior public Git history is not scrubbed", flagged)

    def test_browser_script_makes_no_network_call(self):
        script = (ROOT / "assets" / "app.js").read_text(encoding="utf-8")
        for api in ("fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket"):
            self.assertNotIn(api, script)


class EvidenceTests(unittest.TestCase):
    def test_every_source_has_a_scope_and_a_verified_flag(self):
        for key, source in SOURCES.items():
            self.assertTrue(source["label"], key)
            self.assertTrue(source["url"].startswith("https://"), key)
            self.assertTrue(source["scope"], key)
            self.assertIsInstance(source["verified"], bool, key)

    def test_unverified_sources_are_marked_and_limited(self):
        failing = [key for key, source in SOURCES.items() if not source["verified"]]
        self.assertTrue(failing, "at least one retrieval failure must be recorded honestly")
        markers = ("retrieval failed", "not retrieved", "not confirmed")
        for key in failing:
            scope = SOURCES[key]["scope"].lower()
            self.assertTrue(any(marker in scope for marker in markers), key)

    def test_official_figures_appear_only_on_sourced_rows(self):
        thresholds = (ROOT / "pages" / "estate-thresholds.html").read_text(encoding="utf-8")
        self.assertIn("15,000,000", thresholds)
        self.assertIn("15,480,000", thresholds)
        self.assertIn("irs.gov", thresholds)
        prop = (ROOT / "pages" / "property-tax.html").read_text(encoding="utf-8")
        self.assertIn("1,044,586", prop)
        self.assertIn("boe.ca.gov", prop)

    def test_unknown_values_are_left_blank_rather_than_invented(self):
        thresholds = (ROOT / "pages" / "estate-thresholds.html").read_text(encoding="utf-8")
        self.assertIn("Blank by design", thresholds)
        self.assertIn("A blank cell is an unknown, not a zero", thresholds)


class EngineTests(unittest.TestCase):
    def test_prop19_formula_follows_the_statute(self):
        # Below the limit: no addition to the prior taxable value.
        self.assertEqual(cd.new_taxable_value(1_500_000, 500_000, 1_044_586), 500_000)
        # Above the limit: fair market value less the adjusted amount.
        self.assertEqual(cd.new_taxable_value(5_000_000, 500_000, 1_044_586), 3_955_410)
        # Exactly at the limit: no addition.
        self.assertEqual(cd.new_taxable_value(1_544_586, 500_000, 1_044_586), 500_000)

    def test_property_tax_applies_the_homeowners_exemption_only_when_claimed(self):
        occupied = cd.property_tax(1_000_000, 0.01, True)
        rented = cd.property_tax(1_000_000, 0.01, False)
        self.assertEqual(occupied, 9_930)
        self.assertEqual(rented, 10_000)

    def test_transfer_year_change_moves_the_step_up(self):
        early = cd.scenario({**cd.DEFAULT_INPUTS, "transfer_year": 2040})
        late = cd.scenario({**cd.DEFAULT_INPUTS, "transfer_year": 2050})
        self.assertLess(early["a"]["tax_prop19"], late["a"]["tax_prop19"])
        self.assertLess(early["a"]["value_at_transfer"], late["a"]["value_at_transfer"])

    def test_staging_costs_when_nothing_falls(self):
        params = {
            "start": 100, "staging": 30, "phase": 12,
            "yield": cd.DEFAULT_INPUTS["treasury_yield"],
            "yield_after": cd.DEFAULT_INPUTS["treasury_yield"],
            "equity": cd.DEFAULT_INPUTS["equity_return"],
            "fall_depth": 0.0, "fall_start": 0, "fall_months": 1,
            "recover": 0.08, "horizon": 20,
        }
        immediate = cd.simulate_timeline("immediate", params)
        staged = cd.simulate_timeline("staged", params)
        self.assertLess(staged["end"], immediate["end"])

    def test_staging_helps_when_the_fall_lands_in_the_wait(self):
        base = {
            "start": 100, "staging": 30, "phase": 12,
            "yield": cd.DEFAULT_INPUTS["treasury_yield"],
            "yield_after": cd.DEFAULT_INPUTS["treasury_yield"],
            "equity": cd.DEFAULT_INPUTS["equity_return"],
            "fall_depth": 0.57, "fall_start": 6, "fall_months": 18,
            "recover": 0.08, "horizon": 20,
        }
        immediate = cd.simulate_timeline("immediate", base)
        staged = cd.simulate_timeline("staged", base)
        self.assertGreater(staged["end"], immediate["end"])

    def test_browser_engine_matches_python_engine(self):
        scenario_inputs = cd.DEFAULT_INPUTS
        years = [2026, 2030, 2035, 2040, 2045, 2050]
        expectations = []
        for year in years:
            mkt_a = cd.market_value("A", year, scenario_inputs)
            base_a = cd.assessed_value("A", year, scenario_inputs)
            mkt_b = cd.market_value("B", year, scenario_inputs)
            base_b = cd.assessed_value("B", year, scenario_inputs)
            cap = cd.prop19_limit(year, scenario_inputs)
            occ = cd.new_taxable_value(mkt_a, base_a, cap)
            expectations.append({
                "year": year,
                "marketA": mkt_a,
                "marketB": mkt_b,
                "assessedA": base_a,
                "assessedB": base_b,
                "limit": cap,
                "taxableOccupied": occ,
                "taxOccupied": cd.property_tax(occ, cd.A_EFFECTIVE_RATE, True),
                "taxRented": cd.property_tax(cd.money(mkt_a), cd.A_EFFECTIVE_RATE, False),
                "taxB": cd.property_tax(base_b, cd.B_EFFECTIVE_RATE, False),
                "rentB": cd.b_rent_income(year, scenario_inputs),
                "opATotal": cd.annual_operating("A", year, scenario_inputs)["total"],
                "opBTotal": cd.annual_operating("B", year, scenario_inputs)["total"],
            })
        params = {
            "start": 100, "staging": 30, "phase": 12,
            "yield": scenario_inputs["treasury_yield"], "yield_after": 0.02,
            "equity": scenario_inputs["equity_return"], "fall_depth": 0.57,
            "fall_start": 6, "fall_months": 18, "recover": 0.08,
            "horizon": scenario_inputs["horizon_years"],
        }
        camel_inputs = {
            "transferYear": scenario_inputs["transfer_year"],
            "aApp": scenario_inputs["a_appreciation"],
            "bApp": scenario_inputs["b_appreciation"],
            "inflation": scenario_inputs["inflation"],
            "assessedGrowth": scenario_inputs["assessed_growth"],
            "prop19Growth": scenario_inputs["prop19_growth"],
            "insuranceGrowth": scenario_inputs["insurance_growth"],
            "rentGrowth": scenario_inputs["rent_growth"],
            "maintenanceA": scenario_inputs["maintenance_a"],
            "maintenanceB": scenario_inputs["maintenance_b"],
            "sellingCost": scenario_inputs["selling_cost"],
            "equityReturn": scenario_inputs["equity_return"],
            "treasuryYield": scenario_inputs["treasury_yield"],
            "stagingMonths": scenario_inputs["staging_months"],
            "horizonYears": scenario_inputs["horizon_years"],
        }
        fixture = {
            "data": json.loads(cd.runtime_payload(scenario_inputs)),
            "inputs": camel_inputs,
            "expectations": expectations,
            "sim": {
                "immediate": round(cd.simulate_timeline("immediate", params)["end"], 4),
                "immediateWorst": round(cd.simulate_timeline("immediate", params)["worst"], 4),
                "staged": round(cd.simulate_timeline("staged", params)["end"], 4),
                "stagedWorst": round(cd.simulate_timeline("staged", params)["worst"], 4),
                "cash": round(cd.simulate_timeline("cash", params)["end"], 4),
            },
        }
        if shutil.which("node") is None:
            self.skipTest("node is not available; browser parity is checked separately")
        with tempfile.TemporaryDirectory() as tmp:
            fixture_path = Path(tmp) / "fixture.json"
            fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
            result = subprocess.run(
                ["node", str(TOOLS / "engine_check.cjs"), str(fixture_path)],
                cwd=ROOT, capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
