"""Regression tests for source-linked and privacy-bounded public output."""
import json
import shutil
import subprocess
import tempfile
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import casedata as cd  # noqa: E402


class PublicSitePrivacyTests(unittest.TestCase):
    def test_build_uses_no_household_input_and_emits_manifest_pages(self):
        subprocess.run([sys.executable, str(ROOT / "tools/build.py")], cwd=ROOT, check=True)
        manifest = json.loads((ROOT / "tools/site-manifest.json").read_text(encoding="utf-8"))
        files = [ROOT / path for path in manifest]
        self.assertEqual(len(files), 19)
        self.assertTrue(all(path.is_file() for path in files))
        self.assertFalse((ROOT / "assets/case-projections.csv").exists())
        self.assertIn("Attorney &amp; CPA briefing sheet", (ROOT / "pages/attorney-cpa-brief.html").read_text(encoding="utf-8"))
        self.assertIn("24–36 months", (ROOT / "pages/suggestions.html").read_text(encoding="utf-8"))
        self.assertIn("Blank early / midpoint / late transfer scenarios", (ROOT / "pages/projections.html").read_text(encoding="utf-8"))
        subprocess.run([sys.executable, str(ROOT / "tools/verify.py")], cwd=ROOT, check=True)

    def test_privacy_pages_disclose_current_tree_and_history_boundary(self):
        privacy = (ROOT / "pages/privacy.html").read_text(encoding="utf-8")
        flagged = (ROOT / "pages/flagged-for-review.html").read_text(encoding="utf-8")
        self.assertIn("The repository is public", privacy)
        self.assertIn("historical Git objects", privacy)
        self.assertIn("Current branch tree", privacy)
        self.assertIn("GitHub reports this repository is public", flagged)
        self.assertIn("Treat historic material as exposed", flagged)

    def test_browser_controls_do_not_send_or_store_calculator_inputs(self):
        script = (ROOT / "assets/app.js").read_text(encoding="utf-8")
        self.assertNotRegex(script, r"\b(fetch|XMLHttpRequest|sendBeacon)\b")
        self.assertNotIn("localStorage.setItem('phase", script)
        self.assertNotIn('localStorage.setItem("phase', script)
        self.assertIn("public-suggestion-review-v2", script)

    def test_law_watchlist_distinguishes_chaptered_change_from_unenacted_bills(self):
        subprocess.run([sys.executable, str(ROOT / "tools/build.py")], cwd=ROOT, check=True)
        law = (ROOT / "pages/law-watchlist.html").read_text(encoding="utf-8")
        sources = (ROOT / "pages/sources.html").read_text(encoding="utf-8")
        self.assertIn("SB 974", law)
        self.assertIn("Chapter 665, Statutes of 2026", law)
        self.assertIn("special-needs trust", law)
        self.assertIn("not a general rule for all family transfers", law)
        self.assertIn("S.4196", law)
        self.assertIn("H.R.601", law)
        self.assertIn("S.587", law)
        self.assertIn("non-urgency", law)
        self.assertIn("$3,500,000", law)
        self.assertIn("Proposal—not law", law)
        self.assertIn("Direct page fetch: 2026-11-15", sources)
        self.assertIn("bill_id=202520260SB974", sources)
        self.assertIn("119th-congress/senate-bill/4196", sources)
        self.assertIn("119th-congress/house-bill/601", sources)
        self.assertIn("119th-congress/senate-bill/587", sources)
        for label in (
            "California Secretary of State — Qualified statewide ballot measures",
            "San Francisco Rent Board — Department page",
            "SF Treasurer — vacancy-tax URL retrieval failed",
            "Santa Clara County Assessor homepage — fetch failed",
        ):
            start = sources.rfind("<tr>", 0, sources.index(label))
            end = sources.index("</tr>", start)
            self.assertIn("Direct page fetch: 2026-11-15", sources[start:end])
        self.assertIn("not enacted", law)
        subprocess.run([sys.executable, str(ROOT / "tools/verify.py")], cwd=ROOT, check=True)

    def test_manifest_has_no_duplicate_output_paths(self):
        manifest = json.loads((ROOT / "tools/site-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest), len(set(manifest)))
        for path in manifest:
            self.assertFalse(path.startswith("/"))
            self.assertFalse(".." in Path(path).parts)

    def test_browser_engine_matches_python_engine(self):
        """The shipped tables and the live controls must agree."""
        if shutil.which("node") is None:
            self.skipTest("node is not available")
        inputs = cd.DEFAULT_INPUTS
        years = [2026, 2030, 2035, 2040, 2045, 2050]
        expectations = []
        for year in years:
            mkt_a = cd.market_value("A", year, inputs)
            base_a = cd.assessed_value("A", year, inputs)
            base_b = cd.assessed_value("B", year, inputs)
            cap = cd.prop19_limit(year, inputs)
            occ = cd.new_taxable_value(mkt_a, base_a, cap)
            expectations.append({
                "year": year,
                "marketA": mkt_a,
                "marketB": cd.market_value("B", year, inputs),
                "assessedA": base_a,
                "assessedB": base_b,
                "limit": cap,
                "taxableOccupied": occ,
                "taxOccupied": cd.property_tax(occ, cd.A_EFFECTIVE_RATE, True),
                "taxRented": cd.property_tax(cd.money(mkt_a), cd.A_EFFECTIVE_RATE, False),
                "taxB": cd.property_tax(base_b, cd.B_EFFECTIVE_RATE, False),
                "rentB": cd.b_rent_income(year, inputs),
                "opATotal": cd.annual_operating("A", year, inputs)["total"],
                "opBTotal": cd.annual_operating("B", year, inputs)["total"],
            })
        fixture = {
            "data": json.loads(cd.runtime_payload(inputs)),
            "inputs": {
                "transferYear": inputs["transfer_year"],
                "aApp": inputs["a_appreciation"],
                "bApp": inputs["b_appreciation"],
                "inflation": inputs["inflation"],
                "assessedGrowth": inputs["assessed_growth"],
                "prop19Growth": inputs["prop19_growth"],
                "insuranceGrowth": inputs["insurance_growth"],
                "rentGrowth": inputs["rent_growth"],
                "maintenanceA": inputs["maintenance_a"],
                "maintenanceB": inputs["maintenance_b"],
                "sellingCost": inputs["selling_cost"],
                "equityReturn": inputs["equity_return"],
                "treasuryYield": inputs["treasury_yield"],
                "stagingMonths": inputs["staging_months"],
                "horizonYears": inputs["horizon_years"],
            },
            "expectations": expectations,
        }
        with tempfile.TemporaryDirectory() as tmp:
            fixture_path = Path(tmp) / "fixture.json"
            fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
            result = subprocess.run(
                ["node", str(TOOLS / "engine_check.cjs"), str(fixture_path)],
                cwd=ROOT, capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class WorkingFigureTests(unittest.TestCase):
    """The anonymized, ten-dollar-rounded working-figure layer."""

    def test_every_published_figure_is_rounded_to_ten_dollars(self):
        scenario = cd.scenario(cd.DEFAULT_INPUTS)
        for group in ("a", "b", "sale"):
            for key, value in scenario[group].items():
                if isinstance(value, (int, float)) and abs(value) > 1000:
                    self.assertEqual(value % 10, 0, f"{group}.{key} = {value}")

    def test_rounding_is_half_up_to_the_nearest_ten(self):
        self.assertEqual(cd.money(5_965), 5_970)
        self.assertEqual(cd.money(7_003), 7_000)
        self.assertEqual(cd.money(7_207), 7_210)
        self.assertEqual(cd.money(550_537), 550_540)

    def test_prop19_formula_follows_the_statute(self):
        self.assertEqual(cd.new_taxable_value(1_500_000, 500_000, 1_044_586), 500_000)
        self.assertEqual(cd.new_taxable_value(5_000_000, 500_000, 1_044_586), 3_955_410)
        self.assertEqual(cd.new_taxable_value(1_544_586, 500_000, 1_044_586), 500_000)

    def test_homeowners_exemption_applies_only_when_claimed(self):
        self.assertEqual(cd.property_tax(1_000_000, 0.01, True), 9_930)
        self.assertEqual(cd.property_tax(1_000_000, 0.01, False), 10_000)

    def test_transfer_year_moves_the_step_up(self):
        early = cd.scenario({**cd.DEFAULT_INPUTS, "transfer_year": 2040})
        late = cd.scenario({**cd.DEFAULT_INPUTS, "transfer_year": 2050})
        self.assertLess(early["a"]["tax_prop19"], late["a"]["tax_prop19"])

    def test_occupied_always_costs_less_then_rented(self):
        for year in range(2040, 2051):
            s = cd.scenario({**cd.DEFAULT_INPUTS, "transfer_year": year})
            self.assertLessEqual(s["a"]["tax_prop19"], s["a"]["tax_full"], year)

    def test_no_personal_identifier_in_the_data_module(self):
        source = (TOOLS / "casedata.py").read_text(encoding="utf-8")
        for forbidden in ("owner_name", "trust_name", "account_number",
                          "date_of_birth", "apn", "parcel_number", "street"):
            self.assertNotIn(forbidden + " =", source.lower())
            self.assertNotIn(forbidden + "=", source.lower())
        self.assertNotIn("street", json.dumps(cd.PROPERTY_A).lower())
        self.assertNotIn("street", json.dumps(cd.PROPERTY_B).lower())

    def test_working_figures_publish_with_a_disclaimer_and_a_badge(self):
        for name in ("index.html", "pages/projections.html", "pages/property-tax.html"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("Working figures published below the blank framework", text, name)
            self.assertIn("rounded to the nearest ten dollars", text, name)
            self.assertIn("Owner-supplied", text, name)

    def test_privacy_page_states_the_residual_risk_plainly(self):
        privacy = (ROOT / "pages" / "privacy.html").read_text(encoding="utf-8")
        self.assertIn("Rounding is not anonymisation", privacy)
        self.assertIn("most re-identifiable element", privacy)
        self.assertIn("public postal area", privacy)

    def test_flags_from_the_working_layer_are_published(self):
        flagged = (ROOT / "pages" / "flagged-for-review.html").read_text(encoding="utf-8")
        self.assertIn("F-20", flagged)
        self.assertIn("Flagged after publishing the working figures", flagged)


if __name__ == "__main__":
    unittest.main()
