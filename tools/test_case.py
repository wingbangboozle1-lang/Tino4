"""Regression tests for source-linked and privacy-bounded public output."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class PublicSitePrivacyTests(unittest.TestCase):
    def test_build_uses_no_household_input_and_emits_manifest_pages(self):
        subprocess.run([sys.executable, str(ROOT / "tools/build.py")], cwd=ROOT, check=True)
        manifest = json.loads((ROOT / "tools/site-manifest.json").read_text(encoding="utf-8"))
        files = [ROOT / path for path in manifest]
        self.assertEqual(len(files), 18)
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
        self.assertIn("Copies outside the branch", privacy)
        self.assertIn("Current branch tree", privacy)
        self.assertIn("Published branch history", privacy)
        self.assertIn("GitHub reports this repository is public", flagged)
        self.assertIn("Treat any earlier material as exposed", flagged)
        self.assertIn("Server-side copies of the earlier history", flagged)

    def test_every_cited_source_is_verified(self):
        sources = (ROOT / "pages/sources.html").read_text(encoding="utf-8")
        self.assertNotIn("Not verified", sources)
        self.assertIn("Official source register", sources)

    def test_phased_tool_models_the_3m_to_2y_ladder_and_reinvestment_risk(self):
        page = (ROOT / "pages/phased-investing.html").read_text(encoding="utf-8")
        self.assertIn("Parked in 2-year notes", page)
        self.assertIn("phase-noteshare", page)
        self.assertIn("Reinvestment risk", page)
        self.assertIn("Headline — phased vs immediate", page)
        self.assertIn("renewal yield falls by", page)
        script = (ROOT / "assets/app.js").read_text(encoding="utf-8")
        self.assertIn("phase-noteshare", script)
        self.assertIn("reinvest-cost", script)

    def test_deadline_timeline_and_adviser_brief_carry_official_clocks(self):
        process = (ROOT / "pages/inheritance-process.html").read_text(encoding="utf-8")
        brief = (ROOT / "pages/attorney-cpa-brief.html").read_text(encoding="utf-8")
        self.assertIn("150 days", process)
        self.assertIn("BOE-502-D", process)
        self.assertIn("Deadline strip", brief)
        self.assertIn("Tax adviser (CPA or enrolled agent)", brief)
        self.assertIn("3M-to-2Y Treasury ladder", brief)

    def test_official_benchmark_inputs_replace_guessed_rates(self):
        projections = (ROOT / "pages/projections.html").read_text(encoding="utf-8")
        self.assertIn("Official benchmark inputs", projections)
        self.assertIn("4.32%", projections)
        self.assertIn("+317.15% since 1991", projections)
        black_swan = (ROOT / "pages/black-swan.html").read_text(encoding="utf-8")
        self.assertIn("3-month to 2-year staging path", black_swan)

    def test_decision_logic_is_conditional_and_not_a_recommendation(self):
        decisions = (ROOT / "pages/decision-analysis.html").read_text(encoding="utf-8")
        self.assertIn("Conditional decision logic", decisions)
        self.assertIn("what would reverse it", decisions.lower())
        self.assertIn("No winner is being published", decisions)

    def test_browser_controls_do_not_send_or_store_calculator_inputs(self):
        script = (ROOT / "assets/app.js").read_text(encoding="utf-8")
        self.assertNotRegex(script, r"\b(fetch|XMLHttpRequest|sendBeacon)\b")
        self.assertNotIn("localStorage.setItem('phase", script)
        self.assertNotIn('localStorage.setItem("phase', script)
        self.assertIn("public-suggestion-review-v2", script)

    def test_manifest_has_no_duplicate_output_paths(self):
        manifest = json.loads((ROOT / "tools/site-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest), len(set(manifest)))
        for path in manifest:
            self.assertFalse(path.startswith("/"))
            self.assertFalse(".." in Path(path).parts)

    def test_published_pages_carry_no_case_identifiers(self):
        pattern = re.compile(r"cupertino|san\s+francisco|outer\s+sunset|\b9[0-9]{4}\b", re.I)
        for relative in json.loads((ROOT / "tools/site-manifest.json").read_text(encoding="utf-8")):
            content = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIsNone(pattern.search(content), f"{relative} contains a case identifier")


if __name__ == "__main__":
    unittest.main()
