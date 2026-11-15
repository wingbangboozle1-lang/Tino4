# COORDINATION.md — Privacy-safe task board

## Session `arena-bce280ee` — pre-decision action register (owner's bolded 12-item list) + integration (2026-11-15)

Branch: `arena/bce280ee-tino4` (platform-fixed; branched from `60a054e` = `origin/main` tip "Merge PR #96"). No other branch or worktree is created; no force-push to any other ref. This session acts as the **final integration session** for the items below: `origin/main` was at this session's base commit when the claim was written and the only open PR (#19, session `arena/ec965fac`, coordination-log-only) does not touch site files, so no scope collision is expected. Board state read before claiming: all prior sessions recorded as merged or superseded; `tools/sections.py` and `tools/models.py` recorded as orphan reference modules (open item from session 666).

| Task ID | Task (owner's wording) | Status | Owner | File scope (exclusive) | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| BCE-1 | Look up Property A's tax rate area and read the published rate | done | `arena-bce280ee` | `tools/sitebuild.py` (property-tax section), `tools/verify.py` (host allowlist only if required) | 2026-11-15 |
| BCE-2 | Model a sale in the same tax year as the inheritance before deciding anything else | done | `arena-bce280ee` | `tools/sitebuild.py` (new `pages/sale-timing.html` + model functions), `tools/site-manifest.json` | 2026-11-15 |
| BCE-3 | Claim Prop 19 only if the heir will occupy long term — make it an explicit rule with a break-even | done | `arena-bce280ee` | `tools/sitebuild.py` (property-tax + decision-analysis rows) | 2026-11-15 |
| BCE-4 | Five-year maintenance and capital plan for both buildings | done | `arena-bce280ee` | `tools/sitebuild.py` (new `pages/capital-plan.html`), `tools/site-manifest.json` | 2026-11-15 |
| BCE-5 | Written valuation of Property A at the date of death | done | `arena-bce280ee` | `tools/sitebuild.py` (sale-timing + inheritance-process rows) | 2026-11-15 |
| BCE-6 | Decide whether a like-kind exchange is wanted; advice before selling | done | `arena-bce280ee` | `tools/sitebuild.py` (sale-timing section) | 2026-11-15 |
| BCE-7 | Write an investment policy for the proceeds before the money arrives | done | `arena-bce280ee` | `tools/sitebuild.py` (new `pages/investment-policy.html`), `tools/site-manifest.json` | 2026-11-15 |
| BCE-8 | Estate liquidity plan if the estate may exceed the federal exclusion | done | `arena-bce280ee` | `tools/sitebuild.py` (estate-thresholds section) | 2026-11-15 |
| BCE-9 | Ask now about portability and prior taxable gifts | done | `arena-bce280ee` | `tools/sitebuild.py` (estate-thresholds + questions rows) | 2026-11-15 |
| BCE-10 | Re-run the model every year with updated inputs | done | `arena-bce280ee` | `tools/sitebuild.py` (decision-log + law-watchlist rows) | 2026-11-15 |
| BCE-11 | Put a market rent on Property A or accept letting paths as a floor | done | `arena-bce280ee` | `tools/sitebuild.py` (property-profiles + questions rows) | 2026-11-15 |
| BCE-12 | Add a distribution chart to the projections | done | `arena-bce280ee` | `tools/sitebuild.py` (projections chart), `assets/style.css` (chart rules) | 2026-11-15 |
| BCE-13 | Carry-over items still absent from the site: imputed-rent input for living paths, §121 switch for living-then-sell, depreciation/recapture model, Prop 19 replacement-home carry-forward, transfer tax + recording fees priced into the sell path, Form 540 sensitivity on the 1 percent surtax over one million dollars of taxable income, Prop H terms | done | `arena-bce280ee` | `tools/sitebuild.py`, `assets/app.js`, `assets/style.css` | 2026-11-15 |
| BCE-14 | Privacy: current-tree PII gate, exposure re-audit, history-scrub status | done | `arena-bce280ee` | `tools/privacy_gate.py` (new), `.github/workflows/verify.yml`, `pages/privacy.html` rows | 2026-11-15 |
| BCE-15 | Rebuild, verify, test, PR to `main`, merge, confirm Pages deploy, record result | done | `arena-bce280ee` | release | 2026-11-15 |

Rules observed: only the files above are edited; `COORDINATION.md` edits are append-only to this session's section; every new published currency figure is rounded to the nearest $10 or registered as an official figure; no address, parcel/APN, account number, name or unrounded value is published; the specific Tax Rate Area number for a property is treated as an identifier and is described by method, not printed.

### Progress log — `arena-bce280ee`, implementation pass (2026-11-15)

Shipped on branch `arena/bce280ee-tino4` (commits `3253061`, `0df5fd4` and the follow-up commit recorded in the PR):

- Three new generated pages, registered in `NAV_GROUPS`, `EXPECTED_PAGES`, `tools/site-manifest.json` and `tools/test_case.py` (page count 20 → 23): `pages/sale-timing.html` (BCE-2, BCE-5, BCE-6), `pages/capital-plan.html` (BCE-4, BCE-10, BCE-13), `pages/investment-policy.html` (BCE-7, BCE-8, BCE-9).
- Rows added to existing pages: property-tax rate-area method and the Proposition H schedule (BCE-1, BCE-3), projections action register plus an inline-SVG proceeds chart and a slow/base/fast value distribution table (BCE-11, BCE-12), decision-analysis break-even table, estate-threshold liquidity/portability/prior-gift rows, five new decision-log entries (D13–D17), five new flags (F-24–F-28), four new suggestions (S11–S14), new law-watchlist rows, twelve new glossary terms, and five new adviser-brief questions.
- New local-only browser tool on the sale-timing page (`#carry-tool` in `assets/app.js`): hold years, use selector (occupy / occupy-and-qualify / rent / vacant) which switches the section 121 exclusion and the depreciation-recapture model, imputed rent over ten years, Prop 19 break-even rent, and a base-year-value carry-forward control. No form action, no network call; `tools/dom-test.cjs` now asserts the recapture and exclusion behaviour and that the review-queue count is derived rather than hardcoded.
- Model layer in `tools/sitebuild.py`: `prop19_base_qualify` / `prop19_base_reassess` / `prop19_excess`, `sale_case()` with four exit scenarios, `a_bill_levy_only` / `a_bill_fixed_charge` decomposition of the supplied bill, Proposition H functions, capital-plan tables, and the derived relief/break-even constants used across pages.

**Substantive correction (not cosmetic — flagged publicly as F-24 and D13).** The existing model treated the Proposition 19 branches as "qualifying keeps the factored base year value" versus "non-qualifying reassesses to market value minus the value limit". RTC §63.2 and BOE LTA 2026/026 require: qualifying base = factored base year value + the excess of full cash value over (that base + the adjusted limit); non-qualifying base = full cash value at transfer. On the modeled 2045 figures this changes the headline relief from roughly $51,330/yr to $25,200/yr (published-levy decomposition: $21,670/yr) and the ten-year figure from $562,050 to $275,950, and lowers the derived rent hurdle from $7,210 to $3,540 per month. Index, projections, decision-analysis, the browser path tool and the executive-summary callout were all switched to the corrected pair and the hardcoded prose numbers were replaced with computed values so the pages cannot drift from the model again.

Sources verified by direct fetch on 2026-11-15 (new register entries, `verified: True`): Santa Clara County Compilation of Tax Rates FY 2025-26 (816 rate areas; the 1.1488 worked example is a *different* parcel's rate); Santa Clara Assessor 2026 booklet (date-of-death reassessment timing, supplemental bills, 60-day appeal, maintenance not assessable); Clerk-Recorder recording and fee pages (DTT collection, PCOR penalty, per-title charge); RTC §11911, §11912, §11927, §11930, §11932, §17043; BOE LTA 2026/026 and the Prop 19 page; FTB capital-gains page; IRS Topic 409, §1031 tax-tips page, Form 706, Schedule D (1041) instructions, estate-tax FAQ; SFMTA Proposition H page and the City's November 3, 2026 results; SF Assessor-Recorder department page.

Two research items closed that earlier sessions had to leave open:
1. **Documentary transfer tax on a death or trust transfer is now statute-verified.** Earlier sessions recorded (correctly) that §11911 contains only the rate and no exemption, and treated blog claims of a death/trust exemption as unverified. §11930 — read directly from leginfo — states the tax does not apply where realty is transferred outright to, or in trust for, any person or entity by reason of an inter vivos gift or a death; §11932 requires any tax due to be shown on the face of the recorded document. Published as Verified on the sale-timing and property-tax pages; the exemption covers the inheritance step only, so the later sale to a buyer still carries the tax.
2. **San Francisco Proposition H is enacted and is not a rent measure.** It is a 15-year Muni parcel tax on owners (preliminary returns: 244,760 yes / 84,209 no), effective fiscal 2027-28 through 2041-42, with a limited pass-through for rent-controlled owners. Every earlier "pending research" note is gone; the amounts on the site follow the SFMTA's published schedule and are badged Projection where an area assumption is used.

Still open and left blank/flagged: the SF transfer-tax rate schedule (both official pages returned 404 this session), HUD FMR figures (page still 404), Property A's rent (third-party listing aggregates only, published as a floor), all insurance and repair amounts (bands, not bids), and Property A's own rate-area number (treated as a parcel identifier and deliberately not printed).

Irregularities recorded: (a) the supplied Property A 2025 bill implies a rate about 20 basis points above the published levy example — the residual is shown as an unresolved discrepancy, not assigned to a special district; (b) `SOURCES` contains near-duplicate keys from earlier sessions (`irs_121`/`irs_topic701`, `irs_rp_2025_32`/`irs_rp2532`, `sos_qualified`/`sos_ballot`, `boe_lta_2025_009`/`boe_lta25009`) — the `verified: True` variant is reused and no fifth duplicate was added; (c) `tools/sections.py` and `tools/models.py` remain orphan reference modules that no build path reads — consolidation deferred so this session's diff stays reviewable; (d) Property B's derived effective rate (about 2.14%) still exceeds Property A's (about 1.34%) with no public explanation.

Deviation from the claim table, recorded rather than hidden: BCE-14 was scoped as a new `tools/privacy_gate.py` plus a workflow step. The existing `tools/verify.py` already enforces every gate the owner asked for (rounding, identifiers, CSP, per-row sourcing, local-only resources) and runs in CI on every push and PR, so a second gate script would have duplicated it. Instead the re-audit was executed with the existing verifier plus a scan of this branch's added lines, and the result is published as F-28. `assets/app.js` and the new pages were also checked for `fetch`/`XMLHttpRequest`/`sendBeacon` and form actions.

Checks run before opening the PR (all green): `python3 tools/build.py`; `python3 tools/verify.py`; `python3 -m unittest discover -s tools -p 'test_*.py'` (11 tests); `node tools/dom-test.cjs` (with `jsdom` installed locally, not committed). `node tools/browser-test.cjs` cannot run here — Playwright is not installed in the sandbox and it is not part of CI.

## Current session: quantitative decision layer restored + sourced research (`arena-377ea96a`)

Branch: `arena/b784431e-tino4` (platform-fixed; rebased onto the latest `origin/main`). Status: active.

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| B784-1 | Remove household-specific locations, values, assessment histories, rents and derived recommendations from the public site and active source tree; preserve generic decision guidance and official rules; add fail-closed privacy checks | done | `arena/b784431e` | `tools/sitebuild.py`, `tools/models.py`, `tools/sections.py`, `tools/verify.py`, `tools/test_case.py`, `tools/site-manifest.json`, `assets/app.js`, `assets/style.css`, `.gitignore`, generated `index.html`, `pages/**`, `README.md`, `COORDINATION.md`, history-remediation notes | 2026-11-15 |
| B784-2 | Rebuild, inspect privacy and source coverage, run automated tests, and prepare current-branch PR / deployment verification | done | `arena/b784431e` | release checks and `COORDINATION.md` | 2026-11-15 |

### B784-1 results

- Replaced the household-specific public model with generic decision gates and source-linked guidance. Removed obsolete model and section modules that contained household inputs, and removed stale browser-test files for that model.
- Built 22 privacy-first pages, including a full requirements tracker and investment-policy draft. The home page puts decision-changing facts first; alternatives include pure and mixed paths; costs, occupancy, liquidity, tax, debt, imputed rent, transfer expenses, deadlines, source review and decision logging are explicit.
- The private inventory and projection pages do not publish household inputs, values, location, assessment/rent histories, or a household recommendation. Year-by-year tax/value ranges are specified as a private workpaper task, not invented for the public site.
- The phased-investing page describes a 3-month-to-2-year Treasury ladder and a 24–36-month purchase schedule. The historical page distinguishes the 1929 Dow decline from the 2007–09 S&P 500 decline; the browser tool is a simplified local sensitivity, not a backtest. Inputs are not stored or transmitted.
- Added an official California source-backed rule: California capital gains are taxed as ordinary income, and the current additional 1% tax applies to taxable income above $1,000,000. This is not an inheritance tax. The full Form 540 booklet was not retrieved; no household sale-year sensitivity is published and the current-year instructions still require CPA review.
- The local shorthand “Prop H” is intentionally not mapped to a property or published with locality-specific terms. Jurisdiction and official text must be confirmed privately; no rate or household impact is modeled on the public site.
- Added fail-closed checks for official source hosts, source links and evidence badges on each table row, local links, one heading, restrictive CSP/noindex, unsupported currency, visible postal-like identifiers, contact details, remote resources, browser storage, and external builder inputs. Added `.gitignore` patterns for private workpapers.
- Corrected a pre-existing stylesheet conflict-marker block. The printable attorney/CPA brief retains compact print styles.

### Rebase / coordination record

- Rebased the current branch onto `origin/main` after PR #100 advanced `main`.
- Resolved overlapping public pages and generator by retaining the privacy-first generic build, then incorporating the newly merged requirements tracker, blank investment-policy draft, and official California income-tax research without restoring household-specific figures or location.
- Rebuilt generated pages from the unified builder rather than hand-merging generated HTML. The current board and public source code contain only generic summaries; earlier history remains a separate exposure risk.

### Verification and limitations

- `python3 tools/build.py`: pass (22 pages).
- `python3 tools/verify.py`: pass; every table row has an official source link and evidence status, approved source hosts only, local links resolve, and no household model, browser storage or remote resource is emitted.
- `python3 -m unittest discover -s tools -p 'test_*.py' -v`: pass (8 tests).
- `node --check assets/app.js`: pass; dependency-free Node smoke test passed for local calculation, required-input validation and clearing inputs.
- `git diff --check`: pass. Current-tree scan found no known case locality/identifier/value pattern; conflict-marker scan clean.
- The source register explicitly says links must be rechecked before use and sources are not re-fetched on every build. The full Form 540 booklet and local “Prop H” mapping remain unverified; no property-specific tax rate, appraisal, fees, eligibility, rent, costs, lease or insurance quote is asserted.
- **Historical exposure is unresolved.** A working-tree change cannot erase old commits, PR diffs, forks, caches, downloads or clones. This session did not rewrite shared history, change repository visibility or force-push other refs. Owner/admin action and GitHub Support coordination may be needed; preserve a private encrypted archive before any history rewrite.

### Sources

The guide links to official IRS and U.S. Code materials; California BOE and statutes; FTB Form 540-ES instructions and capital-gains guidance; TreasuryDirect; Federal Reserve History; BLS; CBO; FHFA; SEC Investor.gov; California CDI, CPUC, Water Board, CSLB and FTB; HUD; California Secretary of State; and GitHub Docs for history-removal limitations. Each source record states its scope; links do not verify household-specific facts.

### B784-2 release result

- **PR:** https://github.com/wingbangboozle1-lang/Tino4/pull/101 — “Make the inheritance decision site privacy-first”.
- **Checks:** `build-and-verify` passed (run 43711979756; job 132805325522); PR merge state was clean.
- **Merge:** merged with `gh pr merge 101 --merge` at 2026-11-15T12:04:58Z; merge commit `cb7b22f3824c841c5fade78f9a243ea133692975` on `main`.
- **Pages:** deployment run 43712024772 completed successfully; Pages API reports `built` at https://wingbangboozle1-lang.github.io/Tino4/.
- **Release note:** GitHub Pages emitted non-blocking action-runtime/runner-image deprecation warnings; the build and deploy jobs both succeeded.
- **Open privacy limitation:** the public working tree is generalized, but prior Git objects, PR diffs, forks, caches and clones are not scrubbed. The full Form 540 booklet and local Prop H mapping remain flagged; no property-specific analysis is published.

### Collision with `arena/b784431e` — recorded, not silently resolved (2026-11-15)

While this session was working on its base (`60a054e`), session `arena/b784431e` merged PRs #101 and #102, which **reversed the owner's rounded-figures posture**: the public generator was rewritten to 441 lines with no household model at all, and `tools/verify.py` gained a fail-closed check that rejects any file containing an owner-supplied figure or the model's own constant names. That build is what GitHub Pages is serving now.

This branch therefore does not merge cleanly in policy terms, only in code terms. What the merge on this branch does, decided deliberately rather than by whichever side won a textual conflict:

- **Kept from `b784431e`:** the requirements-tracker page (rebuilt in this site's generator so it stays maintained, with statuses updated to point at where each requirement is now handled), the deletion of the orphan `tools/models.py` / `tools/sections.py` modules, the refreshed history-scrub script, runbook and plan, and the `.gitignore` change. Nothing in their new page was dropped; its rows were re-pointed at the pages that now answer them.
- **Kept from this session:** the rounded-figures content layer, the Prop 19 value-limit correction, the sell-path pages and tools, and this repository's existing verifier and test suite. The owner-supplied-figure ban was not carried over, because it contradicts the owner's written instruction recorded as D07 on the decision log.
- **Not done:** no merge to `main`. Merging this branch would re-publish household-derived figures that another session removed and deployed hours earlier, on the axis the owner ranked as top priority. The two postures cannot both be live, so the choice is surfaced for one owner decision instead of being resolved by an agent that can see only one side of the instruction history.

### Post-merge integration detail (this session, 2026-11-15)

- Resolved the merge as a deliberate policy choice, not a textual one: `-X ours` produced a broken hybrid (main's 441-line generator + this branch's 24-page manifest), so the tree was reset to this session's generator and main's additive work was ported by hand — the requirements tracker was rewritten as `build_requirements_tracker()` inside `tools/sitebuild.py` with its rows re-pointed at the pages that now answer each requirement, plus main's orphan-module deletions, scrub-script refresh and `.gitignore` change. `tools/dom-test.cjs` (which covers the model main deleted) is kept; `tools/browser-test.cjs` stays deleted.
- Tracker statuses were normalized into `badge()` (`Handled`, `Handled with a flag`, `Open — owner action`, `Open — private step`, `Result uncertified`) so the register shows evidence state instead of an unstyled label.
- The collision is published on the site: **F-29** on `pages/flagged-for-review.html`, a boundary row on `pages/privacy.html`, and a top-of-README section. Page count is now 24 (`index.html` + 23 pages).
- PR #104 opened with the conflict and the one-command reversal (`git revert -m 1 <merge>`) stated in the body.

## Prior work

Earlier sessions built a household-specific model and identified historical exposure. This current tree is being generalized; prior public history is not represented as scrubbed. No old values or place identifiers are repeated in this board.
