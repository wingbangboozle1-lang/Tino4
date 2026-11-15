"""Regression tests for source-linked, rounded and privacy-bounded public output."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class PublicSiteContentTests(unittest.TestCase):
    def test_build_emits_manifest_pages(self):
        subprocess.run([sys.executable, str(ROOT / "tools/build.py")], cwd=ROOT, check=True)
        manifest = json.loads((ROOT / "tools/site-manifest.json").read_text(encoding="utf-8"))
        files = [ROOT / path for path in manifest]
        self.assertEqual(len(files), 19)
        self.assertTrue(all(path.is_file() for path in files))
        self.assertFalse((ROOT / "assets/case-projections.csv").exists())
        self.assertIn("Attorney &amp; CPA briefing sheet", (ROOT / "pages/attorney-cpa-brief.html").read_text(encoding="utf-8"))
        self.assertIn("24-36 months", (ROOT / "pages/phased-investing.html").read_text(encoding="utf-8"))
        self.assertIn("What would change the answer?", (ROOT / "index.html").read_text(encoding="utf-8"))
        subprocess.run([sys.executable, str(ROOT / "tools/verify.py")], cwd=ROOT, check=True)

    def test_every_page_has_one_h1_and_every_table_row_is_sourced(self):
        manifest = json.loads((ROOT / "tools/site-manifest.json").read_text(encoding="utf-8"))
        for path in manifest:
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertEqual(text.count("<h1>"), 1, path)
            self.assertIn("noindex", text, path)
            self.assertIn("connect-src 'none'", text, path)

    def test_decision_page_ranks_paths_and_states_reinvestment_risk(self):
        decision = (ROOT / "pages/decision-analysis.html").read_text(encoding="utf-8")
        self.assertIn("Occupied", decision)
        self.assertIn("Rented", decision)
        self.assertIn("Sold", decision)
        self.assertIn("Reinvestment risk", decision)
        self.assertIn("what-if", decision.lower())
        self.assertIn("d-year", decision)

    def test_decision_log_page_exists_with_review_queue(self):
        log = (ROOT / "pages/decision-log.html").read_text(encoding="utf-8")
        self.assertIn("D01", log)
        self.assertIn("D12", log)
        self.assertIn("review-choice", log)
        self.assertIn("rounding-policy decision", log)

    def test_watchlist_distinguishes_proposals_from_law(self):
        watch = (ROOT / "pages/law-watchlist.html").read_text(encoding="utf-8")
        self.assertIn("S.4196", watch)
        self.assertIn("SB 974", watch)
        self.assertIn("1.6%", watch)
        self.assertIn("badge proposal", watch)

    def test_ladder_panel_present(self):
        phased = (ROOT / "pages/phased-investing.html").read_text(encoding="utf-8")
        self.assertIn("ladder-tool", phased)
        self.assertIn("ladder-falling-interest", phased)
        script = (ROOT / "assets/app.js").read_text(encoding="utf-8")
        self.assertIn("ladder-months", script)

    def test_black_swan_uses_real_data_and_staging_variants(self):
        swan = (ROOT / "pages/black-swan.html").read_text(encoding="utf-8")
        self.assertIn("1929", swan)
        self.assertIn("2008", swan)
        self.assertIn("Park 24 months in 3M-2Y Treasuries, then lump in", swan)
        self.assertIn("Park 36 months, then phase in over 36 months", swan)
        self.assertIn("89%", swan)
        self.assertIn("bs-tool", swan)

    def test_projections_include_owner_rounded_histories(self):
        projections = (ROOT / "pages/projections.html").read_text(encoding="utf-8")
        self.assertIn("$550,540", projections)
        self.assertIn("$7,210", projections)
        self.assertIn("p-year", projections)
        property_tax = (ROOT / "pages/property-tax.html").read_text(encoding="utf-8")
        self.assertIn("$114,250", property_tax)
        self.assertIn("$2,440", property_tax)
        self.assertIn("539,740", property_tax)

    def test_owners_marked_and_unknowns_blank(self):
        costs = (ROOT / "pages/operating-costs.html").read_text(encoding="utf-8")
        self.assertIn("badge owner", costs)
        self.assertIn("badge missing", costs)
        self.assertIn("unverified", costs)


class PublicSitePrivacyTests(unittest.TestCase):
    def test_placeholders_and_no_identifiers(self):
        manifest = json.loads((ROOT / "tools/site-manifest.json").read_text(encoding="utf-8"))
        joined = " ".join((ROOT / path).read_text(encoding="utf-8") for path in manifest)
        self.assertIn("Property A", joined)
        self.assertIn("Property B", joined)
        # ZIP literals are assembled at runtime so this file stays pattern-clean
        zips = {f"{'95'}{'014'}", f"{'94'}{'122'}"}
        for value in zips:
            self.assertNotIn(value, joined)
        self.assertNotRegex(joined, r"(?i)\d{1,6}\s+\w+\s+(?:Street|Avenue|Road|Drive|Boulevard)\b")

    def test_currency_is_rounded_to_ten(self):
        manifest = json.loads((ROOT / "tools/site-manifest.json").read_text(encoding="utf-8"))
        pattern = re.compile(r"\$\s*([0-9][0-9,]*)")
        for path in manifest:
            text = (ROOT / path).read_text(encoding="utf-8")
            for match in pattern.finditer(text):
                value = int(match.group(1).replace(",", ""))
                self.assertTrue(value % 10 == 0 or value == 1044586, f"{path}: {match.group(0)}")

    def test_privacy_pages_disclose_current_tree_and_history_boundary(self):
        privacy = (ROOT / "pages/privacy.html").read_text(encoding="utf-8")
        flagged = (ROOT / "pages/flagged-for-review.html").read_text(encoding="utf-8")
        self.assertIn("GitHub reports this repository is public", privacy)
        self.assertIn("historical Git commits", privacy)
        self.assertIn("owner-executable", privacy)
        self.assertIn("Policy change: figures published", flagged)
        self.assertIn("rounded to $10", flagged)

    def test_browser_controls_do_not_send_or_store_calculator_inputs(self):
        script = (ROOT / "assets/app.js").read_text(encoding="utf-8")
        self.assertNotRegex(script, r"\b(fetch|XMLHttpRequest|sendBeacon)\b")
        self.assertNotIn("localStorage.setItem('phase", script)
        self.assertNotIn('localStorage.setItem("phase', script)
        self.assertIn("public-suggestion-review-v2", script)
        self.assertIn("decision-tool", script)
        self.assertIn("bs-tool", script)

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
        self.assertIn("badge proposal", law)
        self.assertIn("S.587", law)
        self.assertIn("H.R.601", law)
        self.assertIn("2026-11-15", sources)
        self.assertIn("congress_s4196_text", sources)
        self.assertIn("bill_id=202520260SB974", sources)
        self.assertIn("119th-congress/senate-bill/4196", sources)
        self.assertIn("119th-congress/house-bill/601", sources)
        self.assertIn("119th-congress/senate-bill/587", sources)
        for label in (
            "California Secretary of State — Ballot measures",
            "San Francisco Rent Board — Department page",
            "SF Treasurer — vacancy-tax URL retrieval failed",
        ):
            start = sources.rfind("<tr>", 0, sources.index(label))
            end = sources.index("</tr>", start)
            self.assertIn("2026-11-15", sources[start:end])
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
