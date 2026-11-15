"""Regression tests for source-linked, $10-rounded, privacy-bounded public output."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class PublicSitePrivacyTests(unittest.TestCase):
    def test_build_emits_manifest_pages_without_private_inputs(self):
        subprocess.run([sys.executable, str(ROOT / "tools/build.py")], cwd=ROOT, check=True)
        manifest = json.loads((ROOT / "tools/site-manifest.json").read_text(encoding="utf-8"))
        files = [ROOT / path for path in manifest]
        self.assertEqual(len(files), 19)
        self.assertTrue(all(path.is_file() for path in files))
        self.assertFalse((ROOT / "assets/case-projections.csv").exists())
        self.assertIn("Attorney &amp; CPA briefing sheet", (ROOT / "pages/attorney-cpa-brief.html").read_text(encoding="utf-8"))
        self.assertIn("24–36 months", (ROOT / "pages/phased-investing.html").read_text(encoding="utf-8"))
        self.assertIn("assessment-branch", (ROOT / "pages/projections.html").read_text(encoding="utf-8"))
        subprocess.run([sys.executable, str(ROOT / "tools/verify.py")], cwd=ROOT, check=True)

    def test_rounding_rule_is_enforced_for_case_figures(self):
        # Every non-statutory currency amount in the public tree must end in $10.
        from verify import CURRENCY_RE, STATUTORY_CURRENCY, currency_ok
        text = (ROOT / "pages/projections.html").read_text(encoding="utf-8")
        amounts = [m.group(1) for m in CURRENCY_RE.finditer(text)]
        self.assertTrue(amounts)
        bad = [a for a in amounts if not currency_ok(a)]
        self.assertEqual(bad, [], f"non-$10-rounded amounts in public output: {bad}")
        # The statutory figures themselves stay exact where published.
        self.assertIn("1044586", STATUTORY_CURRENCY)

    def test_privacy_pages_disclose_current_tree_and_history_boundary(self):
        privacy = (ROOT / "pages/privacy.html").read_text(encoding="utf-8")
        flagged = (ROOT / "pages/flagged-for-review.html").read_text(encoding="utf-8")
        self.assertIn("Rounding rule", privacy)
        self.assertIn("history", privacy.lower())
        self.assertIn("history_scrub_runbook", privacy)
        self.assertIn("history is not scrubbed", privacy)
        self.assertIn("Treat historic material as exposed", flagged)
        self.assertIn("pre-rounding", flagged)

    def test_no_exact_pre_rounding_case_figures_leak(self):
        # Exact (pre-rounding) owner values must never appear in public files.
        banned = ["550,537", "539,743", "7,207", "6,917", "114,248", "2,439", "2,315"]
        for path in (ROOT / "pages").glob("*.html"):
            text = path.read_text(encoding="utf-8")
            for value in banned:
                self.assertNotIn(value, text, f"{path.name} contains pre-rounding figure {value}")

    def test_browser_controls_do_not_send_or_store_calculator_inputs(self):
        script = (ROOT / "assets/app.js").read_text(encoding="utf-8")
        self.assertNotRegex(script, r"\b(fetch|XMLHttpRequest|sendBeacon)\b")
        self.assertNotIn("localStorage.setItem('phase", script)
        self.assertNotIn('localStorage.setItem("phase', script)
        self.assertIn("public-suggestion-review-v2", script)
        self.assertIn("phase-proceeds", script)

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

    def test_prop19_cap_and_estate_figures_are_exact(self):
        pt = (ROOT / "pages/property-tax.html").read_text(encoding="utf-8")
        estate = (ROOT / "pages/estate-thresholds.html").read_text(encoding="utf-8")
        self.assertIn("$1,044,586", pt)   # statutory cap shown exactly
        self.assertIn("$15,480,000", estate)  # 2027 exclusion shown exactly
        self.assertIn("$15,000,000", estate)  # 2026 exclusion shown exactly


if __name__ == "__main__":
    unittest.main()
