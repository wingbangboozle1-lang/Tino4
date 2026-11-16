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

    def test_homepage_discloses_unresolved_historical_exposure(self):
        homepage = sitebuild.render("index.html", "Decision overview", "Start")
        self.assertIn("historical exposure is unresolved", homepage)
        self.assertIn("prior commits, pull-request views, forks, caches, downloads, or clones", homepage)
        self.assertIn("https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository", homepage)
        self.assertLess(homepage.index("historical exposure is unresolved"), homepage.index("What would change the answer?"))

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
        self.assertIn("$100 per $10,000", page)
        self.assertIn("ftb_540", str(sitebuild.SOURCES))
        self.assertIn("ftb_540es", str(sitebuild.SOURCES))
        self.assertIn("line 62", str(sitebuild.SOURCES["ftb_540"]))

    def test_transfer_year_sale_uses_entered_proceeds_basis_and_costs(self):
        script = r'''
const fs = require('fs');
const vm = require('vm');
const values = {
  'sell-value': '120', 'sell-basis': '100', 'sell-costs': '10',
  'sell-dtt': '0', 'sell-other': '0', 'sell-timing': 'transfer', 'sell-121': '0'
};
const elements = new Map();
function element(id) {
  if (!elements.has(id)) elements.set(id, {
    value: values[id] || '', textContent: '',
    addEventListener(type, callback) { this[`${type}Handler`] = callback; }
  });
  return elements.get(id);
}
global.document = { getElementById: element, querySelectorAll: () => [] };
global.window = { print() {} };
vm.runInThisContext(fs.readFileSync('assets/app.js', 'utf8'));
element('sell-run').clickHandler();
console.log(element('sell-result').textContent);
element('sell-value').value = '80';
element('sell-costs').value = '0';
element('sell-run').clickHandler();
console.log(element('sell-result').textContent);
'''
        output = subprocess.check_output(["node", "-e", script], cwd=ROOT.parent, text=True)
        self.assertIn("$10 (potential gain", output)
        self.assertIn("-$20 (potential loss", output)
        self.assertNotIn("gain is modeled at $0", output)

    def test_phase_model_compares_crash_timing_and_rising_market_lag(self):
        script = r'''const model = require(process.argv[1]);
const early = model.simulate({amount: 24000, months: 24, treasuryYieldPct: 0, equityDriftPct: 0, crashPct: 57, crashMonth: 1});
if (Math.abs(early.immediateShockLoss - 13680) > 1 || early.phasedShockLoss !== 0 || !(early.phasedEnding > early.immediateEnding)) process.exit(1);
const after = model.simulate({amount: 24000, months: 24, treasuryYieldPct: 0, equityDriftPct: 0, crashPct: 57, crashMonth: 25});
if (Math.abs(after.immediateShockLoss - after.phasedShockLoss) > 1 || Math.abs(after.phasedEnding - after.immediateEnding) > 1) process.exit(2);
const rising = model.simulate({amount: 24000, months: 24, treasuryYieldPct: 0, equityDriftPct: 8, crashPct: 0, crashMonth: 13});
if (!(rising.immediateEnding > rising.phasedEnding)) process.exit(3);
'''
        result = subprocess.run(["node", "-e", script, str(ROOT.parent / "assets/phase-model.js")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_decision_completeness_rules_are_published_generically(self):
        decision = sitebuild.render("pages/decision-analysis.html", "Compare paths", "Decision")
        self.assertIn("sale in the transfer tax year", decision)
        self.assertIn("not as a tax-free assumption", decision)
        self.assertIn("Sale proceeds waterfall", decision)
        self.assertIn("unrecaptured section 1250 gain", decision)
        self.assertIn("Like-kind exchange (section 1031)", decision)
        self.assertIn("Local-only sale-tax overlay tool", decision)
        self.assertIn("sell-run", decision)
        prop_tax = sitebuild.render("pages/property-tax.html", "Property-tax rules", "Law & process")
        self.assertIn("No carry-forward of the value limit", prop_tax)
        self.assertIn("Tax rate area (TRA)", prop_tax)
        estate = sitebuild.render("pages/estate-thresholds.html", "Estate-tax thresholds", "Law & process")
        self.assertIn("Estate liquidity plan", estate)
        self.assertIn("each $100,000 of taxable income above $1,000,000 adds $1,000", estate)
        log = sitebuild.render("pages/decision-log.html", "Decision log", "Adviser & evidence")
        self.assertIn("Pre-commitment criteria", log)
        flagged = sitebuild.render("pages/flagged-for-review.html", "Flagged for review", "Adviser & evidence")
        self.assertIn("carry-forward premise", flagged)
        self.assertIn("Proposal digests are not enacted schedules", flagged)
        glossary = sitebuild.render("pages/glossary.html", "Glossary", "Adviser & evidence")
        self.assertIn("Unrecaptured section 1250 gain", glossary)
        self.assertIn("Imputed rent", glossary)
        watchlist = sitebuild.render("pages/law-watchlist.html", "Law watchlist", "Law & process")
        self.assertIn("Residential vacancy taxes", watchlist)
        self.assertIn("Local transfer-tax restructuring proposals", watchlist)

    def test_privacy_boundary_holds_for_research_resolution(self):
        decision = sitebuild.render("pages/decision-analysis.html", "Compare paths", "Decision")
        self.assertNotIn("Cupertino", decision)
        self.assertNotIn("Sunset", decision)
        self.assertNotIn("Santa Clara", decision)
        flagged = sitebuild.render("pages/flagged-for-review.html", "Flagged for review", "Adviser & evidence")
        self.assertIn("withheld from this public site", flagged)

if __name__ == "__main__":
    unittest.main()
