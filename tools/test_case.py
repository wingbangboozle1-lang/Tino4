"""Regression tests for source-linked and privacy-bounded public output."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))


class PublicSitePrivacyTests(unittest.TestCase):
    def test_build_uses_no_household_input_and_emits_manifest_pages(self):
        subprocess.run([sys.executable, str(ROOT / "tools/build.py")], cwd=ROOT, check=True)
        manifest = json.loads((ROOT / "tools/site-manifest.json").read_text(encoding="utf-8"))
        files = [ROOT / path for path in manifest]
        self.assertEqual(len(files), 24)
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
                   "1044586", "1022600", "1000000", "49450", "98900", "545500", "613700", "200000",
                   "16000", "11700", "3300", "16250", "171", "189", "212",
                   # San Francisco Measure H parcel-tax schedule (SFDOE official terms)
                   "129", "249", "799", "65", "400000", "50000"}
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


class RecordIdentifierTests(unittest.TestCase):
    """Record identifiers must fail closed even when every amount is rounded.

    The sample strings are assembled from fragments at run time so that this
    file itself never contains a literal identifier that the verifier would
    flag in the repository tree.
    """

    def setUp(self):
        import verify
        self.verify = verify

    @staticmethod
    def apn(first="316", middle="05", last="012"):
        return "-".join((first, middle, last))

    def test_parcel_and_assessor_identifiers_are_caught(self):
        apn = self.apn()
        other = self.apn("123", "45", "678")
        for text in (
            "APN: " + apn,
            "assessor's parcel number " + apn,
            "Parcel No " + apn,
            "The lots are " + other + " and " + self.apn("999", "88", "777"),
        ):
            self.assertTrue(self.verify.identifier_problems(text), text)
        self.assertTrue(self.verify.APN_BARE_RE.search(apn))
        self.assertTrue(self.verify.APN_BARE_RE.search(other))

    def test_account_trust_and_escrow_numbers_are_caught(self):
        for text in (
            "Account number " + "12" + "345678",
            "trust no. AB-" + "123456",
            "Escrow # " + "8842113",
            "Loan Number " + "55443322",
            "Policy number X-" + "9987" + "1",
        ):
            self.assertTrue(self.verify.identifier_problems(text), text)

    def test_dates_of_birth_are_caught(self):
        for text in (
            "Date of birth: 04/12/" + "1958",
            "DOB 4/12/" + "1958",
            "born on March 3, " + "1949",
        ):
            self.assertTrue(self.verify.identifier_problems(text), text)

    def test_ordinary_prose_is_not_flagged(self):
        for text in (
            "The owner's own tax history, rounded to the nearest ten dollars.",
            "Owner-supplied figures are badged as such and are never verified.",
            "A change in ownership generally re-establishes the base-year value.",
            "Form 706 is generally due nine months after the date of death.",
            "Sections 13301 and 16061 of the California codes.",
            "Postal area 95014 (Cupertino)",
            "Chaptered September 27, 2026 as Chapter 665, Statutes of 2026.",
            "Round to the nearest ten dollars before publication.",
            "The transferee must file for the homeowners' exemption within one year.",
        ):
            self.assertEqual(self.verify.identifier_problems(text), [], text)

    def test_no_published_page_exposes_a_record_identifier(self):
        import verify as v
        manifest = json.loads((TOOLS / "site-manifest.json").read_text(encoding="utf-8"))
        for pattern in (v.APN_RE, v.APN_BARE_RE, v.ACCOUNT_RE, v.DOB_RE):
            for name in manifest:
                text = (ROOT / name).read_text(encoding="utf-8")
                self.assertIsNone(
                    pattern.search(text),
                    f"{name} matched {pattern.pattern[:40]!r}",
                )


if __name__ == "__main__":
    unittest.main()
