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
        self.assertEqual(len(files), 20)
        self.assertTrue(all(path.is_file() for path in files))
        self.assertFalse((ROOT / "assets/case-projections.csv").exists())
        self.assertIn("Attorney &amp; CPA briefing sheet", (ROOT / "pages/attorney-cpa-brief.html").read_text(encoding="utf-8"))
        self.assertIn("24–36 months", (ROOT / "pages/suggestions.html").read_text(encoding="utf-8"))
        self.assertIn("Blank early / midpoint / late transfer scenarios", (ROOT / "pages/projections.html").read_text(encoding="utf-8"))
        profiles = (ROOT / "pages/property-profiles.html").read_text(encoding="utf-8")
        self.assertIn("Owner-supplied (privacy-rounded)", profiles)
        self.assertIn("Year-by-year projection, 2026-2050", (ROOT / "pages/projections.html").read_text(encoding="utf-8"))
        self.assertIn("Computed path comparison at the modeled 2045 transfer", (ROOT / "pages/decision-analysis.html").read_text(encoding="utf-8"))
        self.assertIn("id=\"path-tool\"", (ROOT / "pages/decision-analysis.html").read_text(encoding="utf-8"))
        self.assertIn("Staging compared in dollars", (ROOT / "pages/phased-investing.html").read_text(encoding="utf-8"))
        self.assertIn("F-20 — Owner-supplied figures", (ROOT / "pages/flagged-for-review.html").read_text(encoding="utf-8"))
        subprocess.run([sys.executable, str(ROOT / "tools/verify.py")], cwd=ROOT, check=True)

    def test_currency_amounts_are_rounded_or_official(self):
        import re
        pattern = re.compile(r"\$\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)(?![0-9,])")
        allowed = {"15000000", "15480000", "19000", "20000", "250000", "500000", "7000",
                   "1044586", "1022600", "1000000", "49450", "98900", "545500", "613700", "200000"}
        for page in list((ROOT / "pages").glob("*.html")) + [ROOT / "index.html"]:
            for match in pattern.finditer(page.read_text(encoding="utf-8")):
                digits = match.group(1).replace(",", "")
                ok = ("." not in digits) and (digits.endswith("0") or digits in allowed)
                self.assertTrue(ok, f"{page.name} has a non-rounded or unapproved amount {match.group(1)}")

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


if __name__ == "__main__":
    unittest.main()
