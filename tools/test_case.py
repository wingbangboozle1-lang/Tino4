"""Regression tests for source-linked and privacy-bounded public output."""
import json
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

    def test_every_public_currency_amount_is_rounded_to_10(self):
        """Owner rule: case figures are multiples of $10; only explicitly
        allowed official agency amounts may differ."""
        import re

        official = {"1074", "519", "1044586"}
        pattern = re.compile(r"\$([0-9][0-9,]*)")
        manifest = json.loads((ROOT / "tools/site-manifest.json").read_text(encoding="utf-8"))
        for path in [ROOT / item for item in manifest]:
            for match in pattern.finditer(path.read_text(encoding="utf-8")):
                digits = match.group(1).replace(",", "")
                self.assertTrue(
                    int(digits) % 10 == 0 or digits in official,
                    f"{path.name} contains unrounded amount ${match.group(1)}",
                )

    def test_case_tables_and_rounding_disclosure_are_published(self):
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        projections = (ROOT / "pages/projections.html").read_text(encoding="utf-8")
        flagged = (ROOT / "pages/flagged-for-review.html").read_text(encoding="utf-8")
        self.assertIn("rounded to the nearest $10", index)
        self.assertIn("Working recommendation", index)
        self.assertIn("Property A — market value scenarios by year", projections)
        self.assertIn("property tax at the transfer, by state", projections)
        self.assertIn("F-09 — Property B rate discrepancy", flagged)

    def test_manifest_has_no_duplicate_output_paths(self):
        manifest = json.loads((ROOT / "tools/site-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest), len(set(manifest)))
        for path in manifest:
            self.assertFalse(path.startswith("/"))
            self.assertFalse(".." in Path(path).parts)


if __name__ == "__main__":
    unittest.main()
