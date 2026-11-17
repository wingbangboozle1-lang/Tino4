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
        self.assertEqual(len(manifest), verify.EXPECTED_PAGES)
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

    def test_privacy_scanner_checks_metadata_attributes_and_comments(self):
        audit = verify.Audit()
        audit.feed('<meta name="description" content="12345">')
        audit.feed('<span aria-label="hidden location marker">safe</span>')
        audit.feed('<!-- comment marker -->')
        checked_text = " ".join(audit.text)
        self.assertIn("12345", checked_text)
        self.assertIn("hidden location marker", checked_text)
        self.assertIn("comment marker", checked_text)
        self.assertTrue(verify.POSTAL.search(checked_text))

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

    def test_corrected_citations_are_published_and_old_claim_is_gone(self):
        """The 57%/30% figures must not be attributed to the essay that lacks them."""
        src = sitebuild.SOURCES
        self.assertIn("great-recession-of-200709", src["fed_2008"][1])
        self.assertIn("great-recession-and-its-aftermath", src["fed_2008_aftermath"][1])
        # Merge note: main's wording was kept for fed_2008_aftermath because it
        # also records the corrected cbo_long URL review. Both wordings make the
        # same point, so the assertion is on the substance, not on one phrasing.
        self.assertTrue(
            "over a fifth" in src["fed_2008_aftermath"][2]
            or "does not state a 57 percent equity decline" in src["fed_2008_aftermath"][2],
            src["fed_2008_aftermath"][2],
        )
        self.assertNotIn("ca_rtc27388", src)
        flagged = sitebuild.render("pages/flagged-for-review.html", "Flagged for review", "Adviser & evidence")
        self.assertIn("misattributed historical figures", flagged)
        self.assertIn("dead official link", flagged)
        self.assertIn("unsupported statute section", flagged)
        # The CBO topic URL that returned 404 must not reappear as a LINK.
        # It may still appear inside prose that *describes* the correction, so
        # the assertion is on href, not on the bare string.
        self.assertNotIn('href="https://www.cbo.gov/topics/budget/long-term-budget-outlook"', flagged)
        self.assertIn("cbo.gov/recurring-publication/55129", str(sitebuild.SOURCES["cbo_long"]))

    def test_break_even_page_states_thresholds_not_forecasts(self):
        page = sitebuild.render("pages/break-even.html", "Break-even questions", "Decision")
        self.assertIn("break-even", page.lower())
        self.assertIn("imputed rent", page)
        self.assertIn("cannot decide whether a family should live somewhere", page)
        self.assertNotIn("recommendation:", page.lower())

    def test_black_swan_page_uses_regimes_and_correct_attribution(self):
        page = sitebuild.render("pages/black-swan.html", "Black-swan conditions", "Stress tests")
        self.assertIn("Regime", page)
        self.assertIn("different indexes", page)
        self.assertIn("not a probability", page)
        # inflation history anchors quoted from the Federal Reserve essay
        self.assertIn("14 percent", page)
        self.assertIn("1954", page)

    def test_suggestions_page_offers_decisions_before_implementation(self):
        page = sitebuild.render("pages/suggestions.html", "Suggestions for review", "Decision")
        self.assertIn("Adopt", page)
        self.assertIn("Defer", page)
        self.assertIn("Reject", page)
        self.assertIn("is not a decision about the estate", page)
        self.assertEqual(page.count('class="review-choice"'), 10)

    def test_no_household_figures_leak_into_the_new_pages(self):
        for path, title, group in sitebuild.PAGES:
            raw = sitebuild.render(path, title, group)
            for token in ("3,100,000", "1,800,000", "7,150", "550,537", "114,248",
                          "95014", "94122", "Cupertino", "Outer Sunset", "Santa Clara"):
                self.assertNotIn(token, raw, f"{path} leaks {token}")

    def test_private_workbench_is_git_ignored(self):
        ignore = (ROOT.parent / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("/private-work/", ignore)
        import subprocess
        result = subprocess.run(["git", "check-ignore", "-q", "private-work/model.private.py"],
                                cwd=ROOT.parent)
        self.assertEqual(result.returncode, 0)

    def test_privacy_boundary_holds_for_research_resolution(self):
        # The forbidden terms are assembled from parts so this test file does
        # not itself become a plaintext copy of the identifiers it blocks. This
        # is hygiene, not security: a determined reader can reassemble them.
        locality = "Cup" + "ertino"
        sublocality = "Sun" + "set"
        county = "Santa " + "Clara"
        postal_a = "95" + "014"
        postal_b = "94" + "122"
        place_terms = [locality, sublocality, county]
        postals = [postal_a, postal_b]

        decision = sitebuild.render("pages/decision-analysis.html", "Compare paths", "Decision")
        homepage = sitebuild.render("index.html", "Decision overview", "Start")
        flagged = sitebuild.render("pages/flagged-for-review.html", "Flagged for review", "Adviser & evidence")
        for page in (decision, homepage, flagged):
            for term in place_terms:
                self.assertNotIn(term, page)
            for postal in postals:
                self.assertNotIn(postal, page)
        self.assertIn("withheld from this public site", flagged)

    def test_staged_model_arithmetic_identities(self):
        """The staged model must pass identities that a plausible-looking but
        wrong implementation would fail."""
        script = r'''const model = require(process.argv[1]);

// 1. With a flat price index and a zero reserve yield, tranching cannot change
//    anything: every purchase is at the same price, so both paths must end at
//    exactly the lump sum. This is the identity a wrong implementation breaks.
const zero = model.run({months: 24, treasuryYieldPct: 0, equityDriftPct: 0, scenarioId: "flat"});
if (Math.abs(zero.stagedEnding - 1) > 1e-9 || Math.abs(zero.immediateEnding - 1) > 1e-9) process.exit(11);

// 1b. Staging must NOT be a free lunch: with a crash but a zero reserve yield,
//     the staged path differs from the immediate path only because of purchase
//     timing, and it must still lose money in the deep crash.
const crashZero = model.run({months: 24, treasuryYieldPct: 0, equityDriftPct: 7, scenarioId: "early-1929"});
if (!(crashZero.stagedEnding < 1 && crashZero.immediateEnding < 1)) process.exit(21);

// 2. Against a flat price index the staged path must gain exactly the reserve
//    yield applied to the average uninvested balance, and the immediate path
//    must not move at all.
const flat = model.run({months: 24, treasuryYieldPct: 4, equityDriftPct: 7, scenarioId: "flat"});
if (!(flat.stagedEnding > 1 && Math.abs(flat.immediateEnding - 1) < 1e-9)) process.exit(12);

// 3. Once the window closes, the staged path holds 100% equity and no reserve,
//    so its value must track the immediate path at a CONSTANT ratio for the
//    rest of the horizon. (Peak-to-trough percentages legitimately differ,
//    because the staged path was partly in cash earlier and so has a different
//    peak; that is a real feature, not an identity.)
const after = model.run({months: 24, treasuryYieldPct: 4, equityDriftPct: 7, scenarioId: "after-2008"});
if (after.uninvestedReserve > 1e-9) process.exit(13);
const ratios = [];
for (let i = 24; i < after.immediateCurve.length; i += 1) {
  ratios.push(after.stagedCurve[i] / after.immediateCurve[i]);
}
const spread = Math.max(...ratios) - Math.min(...ratios);
if (spread > 1e-9) process.exit(31);
// and that constant ratio must be below 1, because staging bought in later at
// higher prices during a rising market before the crash
if (!(ratios[0] < 1)) process.exit(32);

// 4. A crash inside the window must hurt the immediate path more.
const early = model.run({months: 24, treasuryYieldPct: 4, equityDriftPct: 7, scenarioId: "early-2008"});
if (!(early.immediateWorstDrawdownPct > early.stagedWorstDrawdownPct)) process.exit(14);
if (!(early.stagedEnding > early.immediateEnding)) process.exit(15);

// 5. A longer window must protect more when the crash is inside it, and one
//    published scenario must lose to the lump sum - otherwise the model is a
//    sales pitch rather than a test.
const long = model.run({months: 36, treasuryYieldPct: 4, equityDriftPct: 7, scenarioId: "early-2008"});
if (!(long.stagedEnding > early.stagedEnding)) process.exit(16);
const all = model.runAll({months: 24, treasuryYieldPct: 4, equityDriftPct: 7});
if (all.losses < 1) process.exit(17);
if (!(all.results.length === model.SCENARIOS.length)) process.exit(18);

// 6. The flat and rising scenario pair must actually differ.
const rising = model.run({months: 24, treasuryYieldPct: 4, equityDriftPct: 7, scenarioId: "rising"});
if (Math.abs(rising.immediateEnding - flat.immediateEnding) < 1e-6) process.exit(19);

// 7. Out-of-range windows must be rejected.
for (const bad of [12, 48]) {
  let threw = false;
  try { model.run({months: bad, treasuryYieldPct: 4, equityDriftPct: 7, scenarioId: "flat"}); }
  catch (_e) { threw = true; }
  if (!threw) process.exit(20);
}
'''
        result = subprocess.run(
            ["node", "-e", script, str(ROOT.parent / "assets/staged-vs-lump.js")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, f"staged model identity failed: {result.returncode} {result.stderr}")

    def test_staged_model_is_local_only_and_prints_no_household_figures(self):
        script = (ROOT.parent / "assets/staged-vs-lump.js").read_text(encoding="utf-8")
        for banned in ("localStorage", "sessionStorage", "fetch(", "XMLHttpRequest", "sendBeacon", "document.cookie"):
            self.assertNotIn(banned, script)

    def test_historical_anchors_match_the_official_essays(self):
        """Guard against a future edit silently changing a verified number."""
        script = (ROOT.parent / "assets/staged-vs-lump.js").read_text(encoding="utf-8")
        self.assertIn("depthPct: 89", script)
        self.assertIn("depthPct: 57", script)
        self.assertIn("federalreservehistory.org/essays/stock-market-crash-of-1929", script)
        self.assertIn("federalreservehistory.org/essays/great-recession-of-200709", script)


    def test_staged_chart_renders_one_bar_per_published_scenario(self):
        """A chart that silently renders nothing looks fine in a screenshot."""
        output = subprocess.check_output(
            ["node", str(ROOT / "smoke" / "chart_smoke.js")], cwd=ROOT.parent, text=True
        )
        self.assertIn("bars: 9", output)
        self.assertIn("labels: 18", output)
        self.assertIn("Staged ahead in 5 of 9", output)


    def test_suggestions_have_stable_ids_and_a_copyable_decision_record(self):
        page = sitebuild.render("pages/suggestions.html", "Suggestions for review", "Decision")
        for sid in ["S-01", "S-07", "S-13"]:
            self.assertIn(sid, page)
        # 10 site-improvement items (S1-S10) plus the numbered action registry
        self.assertEqual(page.count('class="review-choice"'), 10)
        self.assertIn("Numbered action registry", page)
        self.assertIn("Cite the hyphenated form in the decision log", page)
        script = (ROOT.parent / "assets" / "app.js").read_text(encoding="utf-8")
        self.assertIn("Suggested decision-log lines", script)
        self.assertIn("dataset.id", script)


    def test_first_screen_leads_with_decision_changing_facts(self):
        """The homepage must put 'what would change the answer' above the fold,
        and must offer the staging trade-off as a decision-changer rather than
        burying it in a stress-test page."""
        homepage = sitebuild.render("index.html", "Decision overview", "Start")
        position_table = homepage.index("What would change the answer?")
        self.assertLess(position_table, homepage.index("Safe decision order"))
        self.assertIn("Does staging the sale proceeds actually reduce crash risk?", homepage)
        self.assertIn("beat immediate investment in 5", homepage)
        # the staged-investing result must not be a promise
        self.assertIn("worst about -5%", homepage)

    def test_privacy_page_publishes_the_rounding_caveat(self):
        """Rounding to $10 was requested as a privacy control. It is not one,
        and the site must say so rather than imply the figures are anonymous."""
        page = sitebuild.render("pages/privacy.html", "Privacy & limits", "Adviser & evidence")
        self.assertIn("Why rounding to a round number is not anonymization", page)
        self.assertIn("County assessment rolls are public and searchable", page)
        self.assertIn("Measured exposure scope, audited 2026-11-17", page)
        self.assertIn("82 of 87 refs", page)


    def test_recheck_reports_whether_the_evidence_layer_moved(self):
        """Rebuilding must state whether the recommendation-visible layer
        changed, not merely whether the build passed."""
        result = subprocess.run(
            ["python3", str(ROOT / "recheck.py")], cwd=ROOT.parent,
            capture_output=True, text=True,
        )
        self.assertIn(result.returncode, (0, 1), result.stdout + result.stderr)
        self.assertIn("recheck:", result.stdout)
        self.assertTrue(
            "UNCHANGED" in result.stdout or "MOVED" in result.stdout or "snapshot" in result.stdout,
            result.stdout,
        )

    def test_recheck_refuses_a_private_model_inside_the_repository(self):
        """The private model must be able to live outside the tracked tree."""
        script = (ROOT / "recheck.py").read_text(encoding="utf-8")
        self.assertIn("must point outside the repository", script)
        self.assertIn("--private-model", script)
        self.assertIn("Only the ordering is ever printed", script)


    def test_no_tracked_source_republishes_an_identifier(self):
        """Scan every tracked file for the case identifiers and value shapes.

        This is a regression guard, not proof of containment: the pattern list
        is finite and a clean result does not show that history is clean. It
        exists because two files in this repository previously carried the
        identifiers in plaintext while claiming to protect them.
        """
        import base64
        import subprocess as sp

        encoded = [
            "OTUwMTQ=", "OTQxMjI=", "Q3VwZXJ0aW5v", "U3Vuc2V0IERpc3RyaWN0",
            "U2FudGEgQ2xhcmEgQ291bnR5", "UGFya3NpZGU=", "QmFuY3JvZnQ=",
            "MywxMDAsMDAw", "MSw4MDAsMDAw", "NywxNTA=", "NTUwLDUzNw==", "MTE0LDI0OA==",
        ]
        patterns = [base64.b64decode(item).decode() for item in encoded]
        offenders = []
        for pattern in patterns:
            result = sp.run(
                ["git", "grep", "-l", "-i", "-F", "--", pattern],
                cwd=ROOT.parent, capture_output=True, text=True,
            )
            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                path = line.split(":", 1)[-1]
                # This test necessarily contains the encoded patterns, so it is
                # the one file exempted. The exemption is narrow on purpose: it
                # covers only base64 fragments, never a decoded identifier.
                if path == "tools/test_case.py":
                    continue
                offenders.append(path)
        self.assertEqual(sorted(set(offenders)), [], f"identifier republished in: {sorted(set(offenders))}")


    def test_published_staging_table_matches_live_model_output(self):
        """The page quotes figures; the model produces them. If an edit changes
        the model or the page without the other, this fails. Numbers that drift
        away from their source are how a projection stops being reproducible."""
        import json as _json
        script = r'''const m = require(process.argv[1]);
const r24 = m.runAll({months:24, treasuryYieldPct:4, equityDriftPct:7});
const r36 = m.runAll({months:36, treasuryYieldPct:4, equityDriftPct:7});
console.log(JSON.stringify({
  w24: Object.fromEntries(r24.results.map(r=>[r.scenarioId, +(r.difference*100).toFixed(1)])),
  w36: Object.fromEntries(r36.results.map(r=>[r.scenarioId, +(r.difference*100).toFixed(1)])),
  s24: {wins: r24.wins, median: +(r24.medianDifference*100).toFixed(1), worst: +(r24.worstDifference*100).toFixed(1)},
  s36: {wins: r36.wins, median: +(r36.medianDifference*100).toFixed(1), worst: +(r36.worstDifference*100).toFixed(1)}
}));
'''
        live = _json.loads(subprocess.check_output(
            ["node", "-e", script, str(ROOT.parent / "assets/staged-vs-lump.js")], text=True
        ))
        page = sitebuild.render("pages/phased-investing.html", "Treasury staging tool", "Stress tests")

        def fmt(value):
            return f"{value:+.1f}".replace("+", "")

        # Every scenario's 24-month result must appear as a stated figure.
        for scenario_id, diff in live["w24"].items():
            magnitude = abs(diff)
            if magnitude < 0.05:
                continue
            self.assertIn(f"{magnitude:.1f}%", page, f"{scenario_id} result {diff}% not published")

        # The two summary sentences must agree with the model.
        self.assertIn(f"ahead of a lump sum in {live['s24']['wins']} of 9", page)
        self.assertIn(f"median advantage of {live['s24']['median']:.1f}%", page)
        self.assertIn(f"worst case of {live['s24']['worst']:.1f}%", page)
        self.assertIn(f"ahead in {live['s36']['wins']} of 9", page)
        self.assertIn(f"median of {live['s36']['median']:.1f}%", page)
        self.assertIn(f"worst case of {live['s36']['worst']:.1f}%", page)

        # And the scenario count must match the model, so adding a scenario
        # without re-running the published prose fails here.
        self.assertEqual(len(live["w24"]), 9)


if __name__ == "__main__":
    unittest.main()
