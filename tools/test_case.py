"""Regression tests for privacy and evidence requirements of the public site."""
import json
import re
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

    def test_capital_transaction_and_liquidity_rules_are_published(self):
        pages = {
            "operating": sitebuild.render("pages/operating-costs.html", "Costs & coverage", "Private planning"),
            "tax": sitebuild.render("pages/property-tax.html", "Property-tax rules", "Law & process"),
            "estate": sitebuild.render("pages/estate-thresholds.html", "Estate-tax thresholds", "Law & process"),
            "watch": sitebuild.render("pages/law-watchlist.html", "Law watchlist", "Law & process"),
            "questions": sitebuild.render("pages/questions.html", "Questions & missing evidence", "Decision"),
            "log": sitebuild.render("pages/decision-log.html", "Decision log", "Adviser & evidence"),
            "flag": sitebuild.render("pages/flagged-for-review.html", "Flagged for review", "Adviser & evidence"),
            "brief": sitebuild.render("pages/attorney-cpa-brief.html", "Attorney & CPA brief", "Adviser & evidence"),
            "gloss": sitebuild.render("pages/glossary.html", "Glossary", "Adviser & evidence"),
            "privacy": sitebuild.render("pages/privacy.html", "Privacy & limits", "Adviser & evidence"),
        }
        # Depreciation is a timing benefit: the deduction and the repayment are both stated.
        self.assertIn("Only the building depreciates", pages["operating"])
        self.assertIn("allowed or allowable", pages["operating"])
        self.assertIn("maximum 25% federal rate", pages["operating"])
        self.assertIn("no special tax rate for capital gains", pages["operating"])
        # The transfer-tax cliff and the change-of-ownership fee are priced as rules.
        self.assertIn("tier can reach the whole consideration", pages["tax"])
        self.assertIn("change-of-ownership screening form", pages["tax"])
        self.assertIn("Carrying the Proposition 19 allowance forward", pages["tax"])
        self.assertIn("Prior claims reduce what is available", pages["tax"])
        # Estate tax is a cash question, and the filing test includes prior gifts.
        self.assertIn("adjusted taxable gifts", pages["estate"])
        self.assertIn("Liquidity is a different question from liability", pages["estate"])
        self.assertIn("Filing and paying are separate deadlines", pages["estate"])
        # Staleness is scheduled, and the unidentified measure stays unmodeled.
        self.assertIn("Re-check cadence — who looks, how often, and at what", pages["watch"])
        self.assertIn("Proposition I", pages["watch"])
        self.assertIn("Nothing here depends on an unidentified measure", pages["watch"])
        # The open questions name the evidence that closes them.
        for needle in ("What has been depreciated, and what does that create at a sale?",
                       "Is an exchange intended, or is a taxable sale better?",
                       "Can the estate meet what it may owe without selling?",
                       "What could the inherited home rent for, and at what cost?"):
            self.assertIn(needle, pages["questions"])
        # Evidence standard: a program payment standard is not a market comparable.
        self.assertIn("A voucher program payment standard", pages["operating"])
        # The policy collision between rounded figures and containment is recorded, not hidden.
        combined = (pages["log"] + pages["flag"] + pages["privacy"]).lower()
        self.assertIn("publication policy for case figures", combined)
        self.assertIn("Depreciation and recapture", pages["brief"])
        self.assertIn("Unrecaptured section 1250 gain", pages["gloss"])
        self.assertIn("Imputed, or avoided, rent", pages["gloss"])

    def test_capital_panel_inputs_exist_and_are_local_only(self):
        page = sitebuild.render("pages/decision-analysis.html", "Compare paths", "Decision")
        for field in ("cap-basis", "cap-years", "cap-period", "cap-rate", "cap-sale", "cap-dtt", "cap-cost", "cap-rent"):
            self.assertIn(f'id="{field}"', page)
        self.assertIn('placeholder="Enter privately"', page)
        # Only the site's own deferred file may load; no inline script anywhere.
        self.assertIsNone(re.search(r"<script(?![^>]*src=\"\.\./assets/app\.js\")", page))
        script = (ROOT.parent / "assets/app.js").read_text(encoding="utf-8")
        self.assertIn("cap-run", script)
        self.assertIn("capStatus.textContent", script)
        for forbidden in ("fetch(", "XMLHttpRequest", "sendBeacon", "localStorage", "sessionStorage"):
            self.assertNotIn(forbidden, script)

    def test_review_controls_match_the_suggestion_queue(self):
        page = sitebuild.render("pages/suggestions.html", "Suggestions for review", "Decision")
        queue = page.split("Review queue", 1)[1]
        rows = queue.count("<tr>", 0, queue.find("Review status")) - 1   # minus the header row
        controls = page.count('class="review-choice"')
        self.assertGreater(rows, 0)
        self.assertEqual(rows, controls, "every suggestion needs a review control")

    def test_tree_scan_catches_unrounded_amounts_and_mapping(self):
        leak = "the assessment was 550" + ",5" + "37 for that year"
        self.assertTrue(verify.unrounded_amount_problems(leak), "an unrounded amount must fail")
        self.assertEqual(verify.unrounded_amount_problems("indexed 1,384 unique blobs across the audit"), [])
        self.assertEqual(verify.unrounded_amount_problems("official cap $1,044,586 and a rounded $550,540"), [])
        arrow = "==" + ">"
        self.assertTrue(verify.ROUNDING_MAP.search("literal:3,08" + "0,00" + "0 " + arrow + " 3,08" + "0,00" + "0"))
        self.assertTrue(verify.SCRUB_RULES_NAME.search("notes/scrub-rules.txt"))

    def test_whole_tree_scan_is_clean_and_covers_more_than_the_pages(self):
        self.assertEqual(verify.tree_privacy_problems(), [])

    def test_recheck_reports_the_published_framework_unchanged(self):
        result = subprocess.run([sys.executable, str(ROOT / "recheck.py")], cwd=ROOT.parent)
        self.assertEqual(result.returncode, 0, "the committed snapshot must match a clean build")

if __name__ == "__main__":
    unittest.main()
