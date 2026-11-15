"""Regression tests for privacy and evidence requirements of the public site."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
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
        self.assertEqual(len(manifest), 22)
        self.assertTrue(all((ROOT.parent / path).is_file() for path in manifest))

    def test_every_published_table_row_has_official_source_and_status(self):
        sitebuild.build()
        failures = verify.verify()
        self.assertEqual(failures, [])

    def test_no_owner_supplied_household_figures_or_placeholders_are_baked_into_site(self):
        sitebuild.build()
        for page in json.loads((ROOT / "site-manifest.json").read_text(encoding="utf-8")):
            raw = (ROOT.parent / page).read_text(encoding="utf-8")
            self.assertNotIn("Owner-supplied", raw)
            self.assertNotIn("owner-supplied", raw)
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
        self.assertIn("ca_rtc17043", str(sitebuild.SOURCES))
        self.assertIn("ftb_540es", str(sitebuild.SOURCES))

if __name__ == "__main__":
    unittest.main()
