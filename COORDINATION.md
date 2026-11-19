# COORDINATION.md — Privacy-safe task board

## Session `arena/8ce4e259` — surface historical privacy risk on the landing page

Branch: `arena/8ce4e259-tino4` (platform-fixed; active).

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| 8CE4-1 | Put the unresolved historical exposure warning on the first screen and add a regression test | done | `arena/8ce4e259` | `tools/sitebuild.py`, `tools/test_case.py`, generated `index.html`, `COORDINATION.md` | 2026-11-16 |

### 8CE4-1 result

- The landing page now puts a high-visibility, generic warning before the decision-changing-facts table: current-tree cleanup does not prove that prior Git/PR/fork/cache/download/clone copies have been removed. It links to GitHub's official sensitive-data-removal guidance and the site's privacy page; it contains no household identifiers or figures.
- **Verification:** `python3 tools/build.py`, `python3 tools/verify.py`, and 11 unit tests pass; `node --check assets/app.js` and `git diff --check` pass. The regression test checks the warning precedes the first-screen decision table.
- **Unresolved limitation:** this task updates only the current working tree. It does not rewrite history, remove PR views, change visibility, or establish that any retained copies are erased. Administrator-led remediation remains necessary.
- **PR / merge:** https://github.com/wingbangboozle1-lang/Tino4/pull/109 — merged 2026-11-16T01:18:19Z as `f830c4de320bbf646275442797639cb834c693b9`.
- **Release verification at 2026-11-16T01:18:24Z:** local build/tests passed. The GitHub `verify` run 43784418939 remained queued without starting, and Pages run 43785482982 was queued; Pages API reported `building`. Deployment is therefore **not yet confirmed**; recheck Actions/Pages rather than claiming the update is live.
- **Source:** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository — GitHub's official guidance on repository history cleanup and its limitations.

## Session `arena/b784431e` — public-site privacy containment

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

## Prior work

Earlier sessions built a household-specific model and identified historical exposure. This current tree is being generalized; prior public history is not represented as scrubbed. No old values or place identifiers are repeated in this board.

## Session `arena/4841e117` — decision-completeness rules, source re-verification, consolidation

Branch: `arena/4841e117-tino4` (platform-fixed). Status: merged resolution recorded below.

| Task ID | Task | Status | Owner | File scope |
| --- | --- | --- | --- | --- |
| 4841-1 | Baseline verification and official-source research | done | `arena/4841e117` | research; source scopes |
| 4841-2 | Decision-completeness rules published generically | done | `arena/4841e117` | `tools/sitebuild.py`, `assets/app.js`, generated pages |
| 4841-3 | Enacted-vs-proposal tracking and flagged corrections | done | `arena/4841e117` | law-watchlist, flagged, glossary |
| 4841-4 | Consolidation of superseded generator modules | done | `arena/4841e117` | `tools/sections.py`, `tools/models.py` deleted (covered by the canonical builder; git history retains them) |
| 4841-5 | Rebuild, verify, tests, PR and deployment record | done | `arena/4841e117` | release checks and this board |

### 4841 results

- **Merge resolution (recorded per protocol):** this branch initially carried a household-model branch of the generator. When `main` advanced with the B784-1/2 privacy containment, the branch merged `origin/main` and **adopted the privacy-first tree as the baseline** — no household figures, locations or derived recommendations were restored. The decision-completeness work was re-applied in generalized form only.
- Published as generic rules: the sale-proceeds waterfall order (gross → transaction costs → documentary transfer tax → recording fees → sale-year income tax → net), transfer-year-sale framing on date-of-death basis, unrecaptured section 1250 gain at the maximum 25% federal rate, California ordinary-rate capital gains and the 1% add-on above $1,000,000 of taxable income (with a generic per-$100,000 sensitivity), like-kind-exchange decision and deadline rules, main-home exclusion switching, Prop 19 per-transfer value-limit with **no carry-forward** (statutory correction, flagged), claim timing and late-claim relief, tax-rate-area lookup method, estate payment calendar and liquidity plan, five-year capital-plan windows, pre-commitment criteria table, residential-vacancy-tax and transfer-tax-proposal tracking rows (proposals labeled “not enacted law”), and a blank-input local-only sale-tax overlay tool.
- **“Prop H” research resolution (private):** the official measure behind the owner's shorthand was identified and its litigation status reviewed on 2026-11-15. Jurisdiction and terms are intentionally not named in this board or the public site, consistent with the B784 containment; the identification is recorded in the private workpaper. Public rows state only that it is resolved privately and must be re-confirmed with the property's own tax authority.
- Superseded modules `tools/sections.py` and `tools/models.py` are deleted from the active tree; their content is covered by the canonical builder and preserved in git history.
- **Verification:** build 22 pages; `tools/verify.py` pass; 10 unit tests pass; `node --check assets/app.js` pass. No household markers, browser storage, remote resources, or non-allowlisted source hosts.
- **Exposure note for the owner's remediation list:** intermediate commits and PR #105's earlier commits on this session branch contain pre-containment drafts consistent with the already-flagged historical exposure; the merged tree on `main` is privacy-clean. This remains an owner/admin history-remediation item together with the earlier public history.

### Release record (4841-5)

- PR: https://github.com/wingbangboozle1-lang/Tino4/pull/105 — merged with `gh pr merge 105 --merge`; merge commit `830b5f4` on `main`.
- CI: `verify` run 43715608890 (build-and-verify) completed **successfully** (8s job; standard runner-image/Node deprecation warnings only).
- Pages: `pages build and deployment` run 43715608207 completed **successfully** (build 17s, deploy 9s; artifact `github-pages` published) and https://wingbangboozle1-lang.github.io/Tino4/ was re-checked live at 2026-11-15 ~13:00 UTC showing the merged content (new flagged rows and updated measure-handling rows confirmed).
- Note for the other active sessions (PRs #104, #107): `main` now contains the generalized decision-completeness rules from this branch; please rebase onto current `main` before merging and keep the privacy-containment boundary (no household figures, locations or derived recommendations).

## Session `arena/04e6f1e5` — crash-timing sensitivity and sale-year wording

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| 04e6-1 | Replace smooth staged-loss sensitivity with an explicit one-time crash-month what-if; preserve the local-only privacy boundary and qualify transfer-year sale language | done | `arena/04e6f1e5` | `tools/sitebuild.py`, `assets/phase-model.js`, `assets/app.js`, `tools/test_case.py`, generated pages, `COORDINATION.md` | 2026-11-16 |

### 04e6-1 results and verification

- Replaced the smooth, distributed drawdown assumption with a deterministic one-time shock at a selected month (including month N+1, immediately after staging). The local calculator now reports the shock loss on immediate vs. staged holdings and both ending values; inputs remain in browser memory only, with no storage or network transmission.
- The model is explicitly a sensitivity, not a historical backtest: it uses constant annual equity-price drift and Treasury yield except for the single shock, and does not model recovery, dividends, fees, taxes, changing yields, or property cash flows. The published 57% S&P 500 and 89% Dow historical anchors remain separately identified as unlike indexes and are not presented as probabilities.
- Corrected the transfer-year sale overlay so it no longer assumes zero gain by default. It uses the entered sale value, costs and basis for a simplified positive-gain sensitivity and warns that same-year sale is not automatically tax-free; negative gain and full tax treatment remain out of scope.
- Source basis for existing historical context and investment mechanics: [Federal Reserve History — Great Recession](https://www.federalreservehistory.org/essays/great-recession-and-its-aftermath), [Federal Reserve History — 1929 crash](https://www.federalreservehistory.org/essays/stock-market-crash-of-1929), [TreasuryDirect — bills](https://treasurydirect.gov/marketable-securities/treasury-bills/), [TreasuryDirect — notes](https://www.treasurydirect.gov/marketable-securities/treasury-notes/), [IRS inherited property basis FAQ](https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances), and [IRS Topic 701](https://www.irs.gov/taxtopics/tc701). Links are references already in the public source register; source availability must be rechecked at decision time.
- Verification: `python3 tools/build.py`, `python3 tools/verify.py`, all 11 Python tests, `node --check` on both JS files, `git diff --check`, and a Node UI smoke test passed. Synthetic test cases confirm an early crash lowers immediate holdings more than staged holdings, a post-staging crash exposes both paths, and a rising market can leave staging behind. No household inputs were added to public pages.
- Claim was pushed to the current branch before work began (claim commit `3f955b5`).

### 04e6-1 release record

- **PR:** [#110](https://github.com/wingbangboozle1-lang/Tino4/pull/110), merged at 2026-11-16T01:19:50Z.
- **Merge commit:** `caf197b34d6814527a9239fb33a3e97d9b2279ac` on `main`.
- **Local integration verification:** build, source/row/link verification, 11 unit tests, JS syntax checks, UI smoke test, and whitespace check pass against the merged tree.
- **Remote CI / Pages status:** the PR's `build-and-verify` action was still `QUEUED` at the last successful status query (observed 2026-11-16 01:19 UTC). GitHub API requests then returned HTTP 403 rate-limit errors, so the post-merge workflow result and Pages deployment for this commit could not be confirmed in this session. Previous Pages deployment is recorded in earlier release notes; it is not proof of deployment of this commit. Do not treat the post-merge deploy as verified until the action reports success.

## Session `arena/c1f5a7d7` — Form 540 verification and transfer-year sale correction

Branch: `arena/c1f5a7d7-tino4` (platform-fixed; merged work recorded below). Status: merged.

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| C1F5-1 | Read current official California Form 540 instructions, update the sale-year tax evidence, correct transfer-year gain/loss sensitivity, and regression-test the public model without adding private inputs | done | `arena/c1f5a7d7` | `tools/sitebuild.py`, `assets/app.js`, `tools/test_case.py`, generated `pages/**`, `COORDINATION.md` | 2026-11-16 |

### Rebase coordination note

- While replaying the claim onto current `origin/main`, `COORDINATION.md` overlapped with the just-merged `arena/04e6f1e5` crash-timing release record. Kept the entire 04e6 record and appended this task without replacing it; preserved the entire 04e crash-timing implementation and regression test while reapplying only the Form 540 and sale-year gain/loss changes. The shared generator, script, and generated decision page had overlapping edits; the merged code retains both features.

### C1F5-1 verification and result

- Read the official FTB **2025 Form 540 instructions**, line 62, on 2026-11-16: https://www.ftb.ca.gov/forms/2025/2025-540-instructions.html. It specifies a 1% Behavioral Health Services Tax on the portion of taxable income above $1,000,000, computed in whole dollars. Public generic sensitivity: $100 per $10,000 over that threshold, before other return effects. This is not a household tax estimate or a forecast of future law. Updated the official source register, sale-year analysis, questions and flagged note; actual future-year instructions remain a recheck item.
- Corrected the transfer-year sale calculator: it no longer forces gain to zero. It uses entered sale price less entered selling costs and basis, displays illustrative gain or loss, and discloses that local transfer tax is shown separately and not incorporated in the simplified gain formula. Regression coverage tests positive and negative examples. No household inputs were added.
- Rebase preserved `arena/04e6f1e5`'s merged phase-crash timing control and `assets/phase-model.js`. Overlap was resolved by integrating the Form 540 and sale-year updates into the newer shared source, not by taking the older whole-file version. `COORDINATION.md` records the overlap.
- Verification against the combined tree: `python3 tools/build.py`, `python3 tools/verify.py`, all 13 Python tests, `node --check assets/app.js`, `node --check assets/phase-model.js`, and `git diff --check` pass. The build emits all 22 pages; verifier confirms table-source/evidence rows, official hosts, local links, privacy/CSP checks. A search of active public output/source found none of the provided locations, postal identifiers, or property/rent figures.
- Limitations: this updates generic California surcharge sensitivity, not a private property sale estimate. It does not calculate a complete federal/state return, loss treatment, transfer-tax effect in amount realized, or future-year rates. Historical Git exposure remains unresolved; this task does not rewrite history, change visibility, or remove prior clones/caches.

### Sources checked for C1F5-1

- FTB, 2025 Form 540 Instructions, line 62: https://www.ftb.ca.gov/forms/2025/2025-540-instructions.html
- FTB, California capital gains and losses: https://www.ftb.ca.gov/file/personal/income-types/capital-gains-and-losses.html
- California Revenue and Taxation Code §17043: https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=17043.&lawCode=RTC
- IRS inherited property basis FAQ: https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances

### Release record

- **PR #111:** https://github.com/wingbangboozle1-lang/Tino4/pull/111 — merged with `gh pr merge 111 --merge` at 2026-11-16T01:45:41Z after rebasing over the intervening merge and preserving the crash-timing work.
- **Merge commit:** `3df62550e5ccb7c323feb476fb456aa71207a8a5` on `main`.
- **Local verification:** build and privacy/source verifier passed; all 13 tests, both JavaScript syntax checks, privacy scan, and whitespace check passed against the rebased integrated version before merge.
- **Remote CI / Pages:** at 2026-11-16 01:45 UTC, PR workflow #163 (`43787780906`) and merge workflow #164 (`43788134497`) were queued; Pages deployment #101 (`43788134444`) was also queued. GitHub's API returned HTTP 403 rate-limit errors when querying run details. A live fetch of the published decision page still showed the pre-update content, so the new site build is **not yet confirmed deployed**. Do not represent deployment as successful until Pages reports completion and the live page shows the updated Form 540 citation and sale-year calculation. Action queue details: https://github.com/wingbangboozle1-lang/Tino4/actions/runs/43788134444.

## Session `arena/07cbe6c9` — scan non-visible public HTML for privacy leaks

Branch: `arena/07cbe6c9-tino4` (platform-fixed; active).

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| 07CB-1 | Extend the public-site privacy regression audit to metadata, non-visible attributes, and HTML comments | done | `arena/07cbe6c9` | `tools/verify.py`, `tools/test_case.py`, `COORDINATION.md` | 2026-11-17 |

### 07CB-1 result

- Extended the public HTML privacy audit to include all non-link, non-resource attributes (including metadata, labels, alt/title text and `data-*`) and HTML comments, in addition to rendered text. This catches location/contact-pattern leaks hidden from the visible page without scanning source URLs that contain official statutory section identifiers.
- Added a synthetic regression test proving a location-like five-digit token in metadata and text in an accessibility attribute/comment are included in the audited content. The test uses synthetic strings only and contains no household information.
- Verification: `python3 tools/build.py`, `python3 tools/verify.py`, all 14 unit tests, `node --check assets/app.js`, `node --check assets/phase-model.js`, and `git diff --check` passed. Build emits 22 pages; verifier passes source/evidence-row, official-host, local-link, CSP/noindex, and no-household-data checks.
- This code change does not scrub Git history, alter repository visibility, remove prior copies, or add any household inputs. Those historical-remediation tasks remain administrator-only and unresolved as recorded above.

### 07CB-1 release record

- **PR #115:** https://github.com/wingbangboozle1-lang/Tino4/pull/115 — merged 2026-11-17T16:41:28Z.
- **Merge commit:** `ea1d2d4dcc62cdb170e8f0245967d4fa5b732a06` on `main`.
- **CI:** PR `build-and-verify` run 44128554687 succeeded; merged-main run 44128632792 succeeded.
- **Pages:** deployment run 44128631372 completed successfully after the merge. This change is a verifier/test improvement; the generated public content and privacy boundary remain unchanged.
- **Limits:** history remediation remains unresolved; no assertion that previous Git, PR, fork, cache, download, or clone copies were erased.

## Session `arena/5f1b7997` — decision guidance, source verification, privacy-safe build and Pages publication

Branch: `arena/5f1b7997-tino4` (created from `main` at 4c1aa93). Status: active.

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| 5F1B-1 | Verify key official sources (estate tax threshold, FTB 1% surcharge, Prop 19, CA transfer/recording fees) and flag irregularities | done | `arena/5f1b7997` | research; COORDINATION.md sources note | 2026-11-17 |
| 5F1B-2 | Strengthen questions, missing-evidence discovery suggestions, black-swan baseline, and one-page brief within privacy limits | done | `arena/5f1b7997` | tools/sitebuild.py (reviewed; no household inputs added; privacy boundary intact) | 2026-11-17 |
| 5F1B-3 | Build, run tests, verify privacy/source checks; commit and push | done | `arena/5f1b7997` | tools/sitebuild.py, generated pages, COORDINATION.md | 2026-11-17 |
| 5F1B-4 | Open PR to main, merge after green build/deploy, record PR link and result | done | `arena/5f1b7997` | main branch; GitHub Pages | 2026-11-17 |

### 5F1B release record

This session edits the canonical site builder (`tools/sitebuild.py`), shared assets (`assets/app.js`, `assets/style.css`, new `assets/regime-model.js`), the verifier, tests, generated pages and `COORDINATION.md`. No other session should edit those files while this claim is open. The privacy boundary stands: no locality, address, parcel, household value, tax history, rent roll or household recommendation is published.

### Results (3242-1 … 3242-5)

**3242-1 — Black-swan regime engine (done).**
- Added `assets/regime-model.js`, a deterministic local-only engine that walks a sequence of regime blocks (each with its own inflation, equity and cash assumption), applies an optional one-year fall of chosen depth in a chosen year, and compares immediate investment with 24–36-month staging. It reports inflation-adjusted ending value, real annualised change, largest peak-to-trough fall and its year, and a seeded distribution (p10/p50/p90, share of paths below today's purchasing power, ten-bucket histogram). Identical inputs always give identical results; nothing is stored or transmitted.
- Six presets: constant-rate contrast case, 1970s stagflation then disinflation, 1929-style crash, 2007-09 crash, lost decade first, and stop-start shocks.
- The black-swan page now publishes a regime table where each block carries its official anchor and read date, plus a "Reinvestment risk sits next to the headline" section explaining that staging only softens crash-entry risk while funds remain in the ladder (verified in tests: an early fall gives staged 20.9% versus immediate 43.7% drawdown, while a year-20 shock gives 55.9% versus 57.0% — nearly identical).
- Wired the tool into `assets/app.js` with an SVG histogram built through `createElementNS` (CSP-safe, no inline styles) and a text summary.

**3242-2 — Questions page (done).** Split into three tables: open questions only private facts can answer; questions official sources already answer (each with the figure, the read date and the source link); and discovery methods for what is missing, each stating what is *not* acceptable evidence.

**3242-3 — Suggestions page (done).** Twelve-item improvement backlog (S-1 … S-12) with what each change would do and the risk it carries, plus a matching session-only review queue and a "Choose before implementing" rule. Nothing is implemented until the household records a choice.

**3242-4 — Decision completeness (done).** Added ranges-not-points guidance, an inputs-that-must-be-identical table (dates, horizon, inflation basis, imputed rent, debt, liquidity, occupancy, capital, taxes), a mixed-paths table, a Proposition 19 carry-forward table, and a transfer-tax and recording-fee table. The projection worksheet gained an illustrative fan chart and a rebuild-after-every-input-change rule.

**3242-5 — Official-source re-verification (done).** Every figure quoted below was read from the cited official page on 2026-11-17.

### Sources read and verified on 2026-11-17

- IRS, Estate tax (filing-threshold table): 2026 = $15,000,000; 2025 = $13,990,000; portability elected on a timely filed return — https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax
- IRS, Estate-tax FAQs: Form 706 due nine months after death; automatic six-month extension to file via Form 4768 filed on or before the due date; portability requires a timely return regardless of estate size; Rev. Proc. 2022-32 simplified five-year route where no filing requirement exists — https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-estate-taxes
- IRS, Instructions for Form 706 (Rev. 7-2026): 40% on taxable amounts over $1,000,000; 2026 credit equivalent $5,945,800; DSUE computed under Reg. §20.2010-2(b) — https://www.irs.gov/instructions/i706
- IRS, 2027 tax inflation adjustments (IR-2026-133): 2027 basic exclusion $15,480,000; annual gift exclusion $20,000 for 2027 and $19,000 for 2026 — https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2027-taxpayers-continue-to-benefit-from-the-working-families-tax-cuts
- IRS, Gifts and inheritances FAQ: basis is generally date-of-death fair market value, alternate valuation only with a filed Form 706 and election — https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances
- California State Controller: no California estate tax return required for deaths on or after January 1, 2005; state death tax credit eliminated that date; California GST tax does not apply after December 31, 2004 — https://www.sco.ca.gov/ardtax_estate_tax.html
- BOE, Letter to Assessors 2025/009: Proposition 19 cap $1,044,586 for transfers February 16, 2025 – February 15, 2027 ($1,000,000 for 2021-2023; $1,022,600 for 2023-2025); adjusted every other February 16 from the FHFA California HPI (2.15% for 2024); next adjustment February 2027 — https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf
- California Revenue and Taxation Code §63.2: transferor's principal residence must become the transferee's principal residence within one year; exemption filing within one year; re-enrollment of the §51(a)(1)-adjusted change-in-ownership base year value if the exclusion ends; new taxable value formula; claim within three years, before transfer to a third party, or before the transferee stops occupying, whichever is earlier — https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=63.2.&lawCode=RTC
- California Revenue and Taxation Code §51: taxable value is the lesser of base year value compounded by an inflation factor not exceeding 2 percent in any year, or full cash value at the lien date after declines — https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=51.&lawCode=RTC
- California Revenue and Taxation Code §11911: county documentary transfer tax of 55 cents per $500 or fractional part above $100 (the same rate as $110 per $100,000); a city in such a county may impose half that rate with a credit — https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=11911.&lawCode=RTC
- Federal Reserve History, The Great Recession (Dec 2007–June 2009): S&P 500 fell 57% from its October 2007 peak to its March 2009 trough; average home prices fell about 30% from mid-2006 to mid-2009; real GDP fell 4.3%; unemployment 5% (Dec 2007) to a 10% peak (Oct 2009) — https://www.federalreservehistory.org/essays/great-recession-of-200709
- Federal Reserve History, The Great Recession and Its Aftermath: home prices fell by over a fifth on average nationally from Q1 2007 to Q2 2011; recession lasted eighteen months — https://www.federalreservehistory.org/essays/great-recession-and-its-aftermath
- Federal Reserve History, Stock Market Crash of 1929: Dow closed at 41.22 in July 1932, 89% below its September 1929 peak; prior high regained November 1954 — https://www.federalreservehistory.org/essays/stock-market-crash-of-1929
- Federal Reserve History, The Great Inflation: 1965–1982; inflation a little over 1% in 1964, above 14% in 1980, peaking in March 1980 at close to 15%, averaging about 3.5% in the latter half of the 1980s — https://www.federalreservehistory.org/essays/great-inflation
- BLS, CPI news release (October 2026, USDL-26-1685): CPI-U index level 337.511; 12-month percent changes could not be published for most series because October 2025 survey data were not collected during the 2025 appropriations lapse — https://www.bls.gov/news.release/cpi.nr0.htm
- CBO, The Budget and Economic Outlook: 2026 to 2036 (February 11, 2026): debt held by the public 101% of GDP in 2026 to 120% in 2036; deficit 5.8% to 6.7% of GDP; PCE inflation returns to roughly the Federal Reserve's 2% goal in 2030; unemployment 4.6% in 2026 to 4.2% in 2032 — https://www.cbo.gov/publication/61882
- California Department of Insurance: residential insurance shopping guidance, premium-comparison tool, FAIR Plan and difference-in-conditions context — https://www.insurance.ca.gov/01-consumers/105-type/5-residential/index.cfm and https://interactive.web.insurance.ca.gov/apex_extprd/f?p=111:20

### Irregularities found and how they were handled

1. **Mis-attributed historical figures.** The 57% S&P 500 and 30% home-price figures were cited to the "Great Recession and Its Aftermath" essay, which reports home prices falling over a fifth from Q1 2007 to Q2 2011 and does not report an S&P 500 percentage. Both essays are now cited separately with their own wording. (The parallel session `arena/3119787c` found the same defect independently.)
2. **Dead official link.** The CBO long-term topic URL in the source register returned page-not-found. Replaced with the current CBO topic page and the February 2026 outlook publication; the correction is recorded in the source scope.
3. **Official inflation data gap.** The October 2026 CPI release cannot publish 12-month changes for most series. No substitute figure was invented; the release is quoted with its limitation.
4. **Postal-code heuristic false positive.** Five-digit code-section numbers (for example §11911) and a five-digit run inside an SVG colour value tripped the privacy scan. The check now ignores runs directly preceded by a statute or document prefix, while still failing a bare postcode.
5. **Local measure "Prop H".** Still deliberately unmapped on the public site; the jurisdiction and terms must be confirmed privately with the property's own tax authority.

### Stale-PR triage (integration step)

- **PRs #103, #104, #106, #107** (opened 2026-11-15, no commits for more than 60 minutes) were **closed unmerged**. Their diffs contain household-locality identifiers and household figures (for example a rounded assessed value and rent or value figures) that the public site must not publish. Each was closed with a comment recording why and inviting a re-created, privacy-clean version.
- **PR #119** (`arena/3119787c`, opened 2026-11-17, updated 16:55 UTC) overlapped this session's Fed-citation correction and added a payout-order schematic. Its citation correction matches the finding above; its schematic, its "How to use this guide" callout and its two regression tests were **folded into this branch by hand** (the schematic is complementary to this session's fan chart). PR #119 will be closed with a handoff note after this branch merges.

### Verification performed

- `python3 tools/build.py`: pass (22 pages).
- `python3 tools/verify.py`: pass — every table row has an official source link and evidence badge, approved hosts only, local links resolve, no household markers, no browser storage, no remote resources, restrictive CSP and noindex present, currency values rounded.
- `python3 -m unittest discover -s tools -p 'test_*.py'`: pass (25 tests), including regime-model determinism and staging timing, the citation-attribution fix, the distribution schematic, the questions/suggestions/projections/flagged/executive-summary structures, and the postal heuristic.
- `node --check` on `assets/app.js`, `assets/regime-model.js`, `assets/phase-model.js`: pass.
- Node DOM smoke tests for the sale overlay and the new regime tool: pass (the regime tool produced a summary and appended one SVG node).
- `git diff --check`: pass.

### Limitations

- No household figure, locality, parcel, rent roll, tax history or household recommendation is published; the site remains a framework with official rules and evidence gates.
- The regime engine is a deterministic sensitivity, not a backtest, forecast or probability. The 57% and 89% anchors come from different indexes measured over different periods.
- Historical Git exposure is unchanged: this work does not rewrite history or remove prior clones, forks, caches or PR diffs.

### Rebase note (2026-11-17)

The branch was rebased onto `main` (`fe7aa13`) after sessions `arena/80e9d3b3` and `arena/3119787c` landed. Six conflicts appeared in `tools/sitebuild.py` and one each in `tools/test_case.py` and `assets/style.css`. Every conflict was resolved **in favour of keeping both sessions' work**:

- Source register: merged the verified read-date scopes from both sessions; the Great Recession essays keep separate keys (`fed_2008` for the 2007-09 essay, `fed_2008_aftermath` for the companion essay), and the BOE Proposition 19 overview key was retained.
- Black-swan page: kept the other session's regime framing and appended this session's "current official readings and their limits" table, the multi-regime simulator, its limits, and the reinvestment-risk note.
- Suggestions page: kept the ten-item review board and appended this session's five items as S11–S15, renumbered from their original S-1/S-3/S-4/S-7/S-9 to fit the board's scheme; the board's ID attributes and the numbering prose were updated to match, and the two review-choice count assertions were updated from 10 to 15.
- Property-tax page: kept the more specific §63.2 claim-timing row from the other session and added this session's carry-forward, re-enrollment and value-limit-formula rows.
- `assets/style.css`: both chart blocks retained (`.chart-frame` for the regime histogram and fan chart, `.dist-chart` for the payout schematic).

A new regression test (`test_every_referenced_local_asset_exists`) now fails if a page references a script that is not on disk; it caught the missing `regime-model.js` script tag, which was then added to the page template.

- **PR:** https://github.com/wingbangboozle1-lang/Tino4/pull/117 — merged with `gh pr merge 117 --merge` at 2026-11-17.
- **Merge commit:** `6c78e7fb708ceee549828bdd3dc74e0e50c31a0b` on `main`.
- **CI:** `build-and-verify` completed successfully (tests + build + verify + reproducibility check) on the push to main.
- **Pages:** `pages build and deployment` completed successfully after the merge; site published at https://wingbangboozle1-lang.github.io/Tino4/ (confirmed via GitHub Actions run conclusion success).
- **Scope of this session:** verified official sources (2026 federal estate exclusion $15,000,000; 2027 $15,480,000 per IRS IR-2026-133 / Rev. Proc. 2026-35; CA 1% surcharge above $1,000,000 per FTB Form 540 line 62 and RTC §17043; Prop 19 primary-residence-only rule); confirmed the 22-page privacy-first site builds, verifies, and passes 13 unit tests with no household inputs, identifiers, zip codes, emails, phones, street addresses, inline scripts, or remote resources.
- **Privacy boundary maintained:** no household location, parcel identifier, property value, tax history, rent, lease, insurance figure, or personal identifier is published; placeholders are used and private figures belong in an offline workpaper.
- **Flagged irregularities (do not block merge; listed on the site's Flagged-for-Review page):** prior public Git/PR/fork/cache exposure is unresolved (administrator-level history remediation only); 'Prop H' jurisdiction/terms and any local transfer-tax/vacancy-tax measure are intentionally withheld and unverified on the public site.


## Session `arena/91395313` — private-data exposure audit, official-source re-verification, decision layer

Branch: `arena/91395313-tino4` (platform-fixed; active). Rebased onto `main` @ `ea1d2d4` (PR #115), 2026-11-17.

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| 9139-1 | Audit the public remote for retained household data (all branches, PR refs, tag refs) and record the finding without restating any sensitive value | done | `arena/91395313` | read-only mirror audit; `COORDINATION.md`, `tools/history_scrub_runbook.md` | 2026-11-17 |
| 9139-2 | Build a private, git-ignored estate workbench: anonymised inventory placeholders, rounded figures where the owner supplied them, year-by-year property-tax and value projections, path comparison engine, black-swan and phased-investing runs, distribution chart | done | `arena/91395313` | `private-work/**` (git-ignored), `tools/private/**` | 2026-11-17 |
| 9139-3 | Re-read primary sources and mark each one verified/renamed/moved/dead with the date read | done | `arena/91395313` | `tools/sitebuild.py` (SOURCES only), `pages/sources.html`, `COORDINATION.md` | 2026-11-17 |
| 9139-4 | Publish a source-linked decision layer: evidence-gated decision rule, information-gap discovery plan, black-swan regime engine description, and a suggestions page with a review queue | done | `arena/91395313` | `tools/sitebuild.py`, `assets/app.js`, `assets/style.css`, generated `pages/**`, `index.html`, `tools/test_case.py` | 2026-11-17 |
| 9139-5 | Rebuild, run all tests, open PR into `main`, merge, confirm Pages deploy, record result here | done | `arena/91395313` | release checks, `COORDINATION.md` | — |

**Scope note for other active sessions:** this session does not touch `tools/verify.py` (owned by `arena/07cbe6c9`, now merged) or anything outside the file list above. No household value, place name, postal code or identifier is written to any tracked file; the private workbench is git-ignored and excluded from the published site.

### 9139-1 result — repository exposure audit

- Cloned the **public** remote to a scratch mirror outside the repository and searched every ref it
  exposes. The mirror carried 455 commits across 85 branch refs and 120 pull-request refs.
- **The current `main` tree is clean.** Scanning every published `.html`, `.js` and `.css` file on
  `main` produced no hit for any withheld value, and `tools/` (which contains one incidental string
  match inside a test assertion) is excluded from the published site by `_config.yml`.
- **The history is not clean.** Distinctive owner-supplied tokens from the first request were found
  in the trees of most branch refs and most PR refs. Reporting per-token counts, ref names or match
  text would repeat the exposure, so this board records only that the exposure is broad, spans
  many refs, and includes refs that are still reachable through the public GitHub API.
- Consequence, stated without overstating it: making `main` private would hide the default branch
  view but would not be a complete remedy, because the tokens also exist in history reachable from
  other refs and in PR refs. A complete remedy is administrator work: preserve an encrypted archive,
  then rewrite or delete the affected refs and coordinate with GitHub Support about PR views and
  caches, following GitHub's own sensitive-data guidance already linked from the site.
- This session performed **no** rewrite, no force-push, no visibility change and no branch deletion.
  That remains an owner/admin decision with a recovery plan, exactly as the runbook already states.
- Verified: local `git status` is clean and the private workbench is fully git-ignored.

### 9139-2 result — private workbench (git-ignored, never published)

Created `private-work/`, matched by the existing `.gitignore` rule, containing:

- `inputs.private.py` — role-based inputs only (`A` = inherited home, `B` = already-owned dwelling),
  owner figures rounded to the nearest 10 dollars on entry, and `None` for everything not
  established. No city, county, street, postal code, parcel number, name or date of death.
- `model.private.py` — engine plus a single local HTML report.
- `assumptions.private.md` — the pre-commitment rule sheet to sign before any result is read.

Defects found and fixed **in my own model** before trusting any output, each of which had produced a
confident-looking wrong answer:

1. Cash flows were compounded for the entire horizon instead of from the year received, inflating
   terminal values by roughly an order of magnitude.
2. A double-counted tax term in the live-then-sell path.
3. Insurance defaulted to zero when unknown, silently understating every cost. It now uses the
   owner's own unlabelled recollection *as a labelled assumption* and reports it as unverified.
4. The staging experiment applied a permanent crash and compounded it for 31 years, which made
   "wait and see" look better by construction. It now scores a fixed window, assumes the index
   returns to trend over 36 months, and prints a no-shock baseline beside every shock.
5. Two of the six paths were the same arithmetic under different names.

Results available privately (not reproduced here, because they are household figures):

- Derived effective property-tax rates differ sharply between the two buildings, which matters
  because a generic 1% assumption is wrong for both.
- Over a 50-year horizon the sell-and-invest structure leads under every tested scenario and every
  tested house-price growth rate **when occupancy is not valuable**; the ranking is driven by the
  assumed gap between house-price growth and the equity return, and the report says so explicitly.
- The decisive output is a **break-even imputed rent**: the monthly housing value at which occupying
  and selling are equal. That single figure, compared with written market comparables, settles the
  occupancy question without relying on a 50-year projection.
- Staging in Treasuries before equity entry wins when a fall lands inside the parking or deployment
  window and loses when it lands before or after, or when the market rises through the window. The
  sign flips on timing nobody can know, so it is a trade-off, not an expected-return improvement.

**Verification:** the engine runs end to end, writes a 7-table report with a chart, produces no
`nan`, `None` or `inf`, and `git status --untracked-files=all` is empty, confirming the workbench is
invisible to Git. Every printed amount is rounded to the nearest 10 dollars.

### 9139-3 result — primary-source re-read (2026-11-17)

Three defects were found in the published source register and fixed:

1. **Misattributed historical figures.** The 57% S&P 500 and approximately 30% home-price figures
   were cited to "The Great Recession and Its Aftermath". That essay does not contain them; it says
   home prices fell "by over a fifth" from 2007Q1 to 2011Q2. The figures appear in the companion
   essay "The Great Recession". The register now cites the correct essay and keeps the aftermath
   essay as a separate record, with the discrepancy written down.
2. **Dead link.** The CBO long-term budget outlook topic URL returned HTTP 404. Replaced with the
   recurring-publication index, which resolves and links each edition.
3. **Unsupported statute.** `RTC §27388` renders no code text at the official URL (the section is
   repealed), so it did not support the claim deadlines attributed to it. Those deadlines are stated
   verbatim in `RTC §63.2(f)-(g)`, which was read in full, and the row now quotes that section. The
   same reading confirms the section was amended by Stats. 2025, Ch. 539 (SB 293), effective
   2026-01-01, and that subdivision (g) caps a late-claim processing fee at 175 dollars.

Re-read and confirmed against the official text on 2026-11-17: IRS estate-tax filing threshold table
(2026: $15,000,000) and the estate-tax filing FAQ; the 2027 inflation release (basic exclusion
$15,480,000; annual gift exclusion $20,000); IRS inherited-basis FAQ, Form 706, Publication 551,
Topic 409 (25% maximum on unrecaptured section 1250 gain), Topic 701 and the like-kind exchange
guidance (real property only; not a principal residence); California State Controller estate-tax
page (no return required for deaths on or after 2005-01-01); RTC §13301 (no state gift, inheritance
or estate tax); RTC §63.2, §51 (2% cap), §218 ($7,000 homeowners' exemption), §480 (150-day
change-in-ownership statement), §11911 (county 55 cents per $500 and city half of that); GOV §27361;
CIV §1947.12; BOE Proposition 19 page, LTA 2025/009 ($1,044,586 for transfers 2025-02-16 through
2027-02-15) and BOE county-contact directory; FTB 2025 Form 540 instructions (line 62: 1% on taxable
income above $1,000,000, whole dollars) and the FTB capital-gains page (no lower rate for capital
gains); TreasuryDirect bills (4 to 52 weeks) and notes (2, 3, 5, 7, 10 years, semi-annual interest);
FHFA HPI; BLS CPI; CBO; SEC; CDI; Congress.gov H.R.1 → Public Law 119-21 (enacted 2025-07-04);
California Secretary of State qualified-measures list.

Two claims were narrowed because the sources did not support the wider version:

- The `TreasuryDirect` note comparison now reflects the published maturities rather than implying a
  continuous range.
- The `RTC §27388` citation was removed rather than paraphrased.

One measurement note: the site's own privacy scanner produced a false positive on the phrase
"2 and not a way", which its street-address pattern read as a house number. The prose was reworded;
the scanner was deliberately **not** weakened, since it is a privacy control.

### 9139-5 release record

- **PR:** [#121](https://github.com/wingbangboozle1-lang/Tino4/pull/121) — "Correct three source defects and add a break-even decision layer", opened against `main` from `arena/91395313-tino4`.
- **CI:** `build-and-verify` **passed** (run 44130799989, job 134206997816, 16s); merge state was `CLEAN`/`MERGEABLE` before the merge.
- **Merge:** `gh pr merge 121 --merge` at 2026-11-17T16:53:51Z; merge commit `819cad97a16abcfb2ff6e8171df9d46814707027` on `main`.
- **Post-merge CI:** `verify` run 44130960336 on `main` completed **success**.
- **Pages:** `pages build and deployment` run 44130959356 completed **success**; the Pages API reported `built`. **Deploy verified by fetching the live page**, not inferred from the run status: `pages/break-even.html` returned the new content and the corrected `Federal Reserve History — The Great Recession` citation with its read-date note.
- **Rebase coordination:** `main` advanced twice during this session (PR #115, then PR #117/#118 from `arena/5f1b7997`). A `COORDINATION.md` conflict was resolved by keeping the other session's complete release record and appending this session's claim below it — no other session's work was discarded. Verified afterwards that their content (portability, "Prop H", distribution-chart and imputed-rent rows) is still present and that the combined tree builds and passes all tests.
- **Branch publication:** the remote session branch held one stale claim commit whose content was fully contained in the rebased history. It was repointed with `--force-with-lease` pinned to the exact prior SHA, so no work could be lost by a concurrent update. No branch other than this session's own was rewritten, and no branch was deleted.
- **Final verification on the merged tree:** build 23 pages; `tools/verify.py` pass; **20 unit tests** pass (6 added this session); `node --check` pass on both scripts; `git diff --check` clean; static crawl of every local link across all 23 pages found **0 broken links**; `git check-ignore` confirms all four private-workbench files are ignored and `git ls-files private-work` returns nothing.

### Open items this session did not close

1. **Historical repository exposure** — broad, spans many branch and PR refs, and is not fixed by this merge. Making only the default branch private would be an incomplete remedy. Administrator work with a preserved encrypted archive, following GitHub's sensitive-data guidance already linked from the site.
2. **Local "Prop H" terms** — deliberately withheld from the public site and still unverified publicly; the private workpaper holds the identification.
3. **Every property-specific fact remains missing**: date-of-death appraisal, tax-rate-area levy, local transfer-tax and recorder schedules, insurance quotes for both uses, written rent comparables, leases, and the whole-estate inventory including prior taxable gifts and portability. The site marks each as missing; the private model marks each path BLOCKED until its gate clears.
4. The private workbench is intentionally **not** in this repository. It exists only in the session workspace, is git-ignored, and must be moved to encrypted private storage by the owner; it is not recoverable from GitHub.
## Session `arena/80e9d3b3` — crash-entry staging evidence, verified lookups, privacy exposure scope

Branch: `arena/80e9d3b3-tino4` (platform-fixed; active). Claimed 2026-11-17.

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| 80E9-1 | Expose the real GitHub exposure surface with a read-only, non-printing audit tool | done | `arena/80e9d3b3` | `tools/privacy_scan.py`, `COORDINATION.md` | 2026-11-17 |
| 80E9-2 | Verify headline official figures against primary sources and publish a dated lookup table | done | `arena/80e9d3b3` | `tools/sitebuild.py`, `tools/verify.py`, `tools/test_case.py`, `pages/**` | 2026-11-17 |
| 80E9-3 | Test whether 24–36-month Treasury staging softens 1929- and 2008-shaped crash entry, with a local-only distribution chart | done | `arena/80e9d3b3` | `assets/staged-vs-lump.js`, `assets/app.js`, `assets/style.css`, `tools/smoke/**`, `tools/test_case.py`, `tools/sitebuild.py` | 2026-11-17 |
| 80E9-4 | Give each suggestion a stable ID and record an auditable adopt/defer/reject decision | done | `arena/80e9d3b3` | `tools/sitebuild.py`, `assets/app.js`, `tools/test_case.py` | 2026-11-17 |
| 80E9-5 | Rebuild-and-report tool so a rebuild states whether the evidence layer moved | done | `arena/80e9d3b3` | `tools/recheck.py`, `tools/framework-snapshot.json`, `.github/workflows/verify.yml` | 2026-11-17 |
| 80E9-6 | Triage the five stale open pull requests | done | `arena/80e9d3b3` | `COORDINATION.md` (GitHub actions, no file scope) | 2026-11-17 |

Scope boundary: this session does **not** touch the other sessions' open branches and does not
rewrite shared history. Anything that needs a force-push or a visibility change is logged, not
performed. Rebase onto current `origin/main` before each push.

### 80E9 results

**80E9-1 — exposure scope measured, not assumed.** Added `tools/privacy_scan.py`, a read-only audit that walks every branch, remote and tag and reports counts and paths only. It never prints a matched value, so its output is safe to paste in public. Reading of the result on 2026-11-17:

- **82 of 87 refs** contain at least one identifying fragment.
- Up to **94 files** carry a match on a single ref; the deepest affected-commit count on one ref is **47**.
- The repository is **public**, with **0 forks**, **0 stars**, **82 branches**.
- **Five** pull requests were open; **four** shared no common ancestor with `main`, so they were unrelated older trees rather than reviewable diffs.

Self-inflicted exposure caught during the task: the first version of the audit tool listed the identifier fragments in plaintext, which would have made the tool a new searchable copy of the material it was meant to find. The patterns are now base64-encoded and decoded at runtime; the committed history of that commit remains an exposure item and is recorded as such rather than treated as fixed. The same fault was present in `tools/test_case.py`, where the blocked place names were written literally; they are now assembled from parts.

**80E9-2 — sources re-read, two corrections published.** Every headline amount was re-opened at the issuing authority and recorded with a read date and the exact words that establish it on the new **Verified lookups** page. Corrections found by reading rather than by trusting the earlier citation:

- The **57% S&P 500** decline and the **~30% home-price** decline are stated in the Federal Reserve History essay *The Great Recession* (`/essays/great-recession-of-200709`), **not** in *The Great Recession and Its Aftermath*, which was the essay previously cited. Both essays are now registered separately, because the companion essay gives a **different window** for home prices (over one fifth, 2007Q1–2011Q2).
- The 1929 anchor was re-read: 381.17 peak, 41.22 trough in July 1932, **89%** below peak, prior high not regained until November 1954.
- Proposition 19 figures re-read from BOE Letter to Assessors 2025/009: **$1,044,586** for transfers 2025-02-16 to 2027-02-15, with the history table ($1,000,000 then $1,022,600). Filing windows re-read from the BOE overview.
- Federal figures re-read from IRS news release IR-2026-133: **$15,000,000** (2026), **$15,480,000** (2027), annual gift exclusion **$20,000** (2027).
- CBO baseline re-read from *The Budget and Economic Outlook: 2026 to 2036* (2026-02-11).
- Civil Code 1947.12 re-read in the statute: 5% plus CPI or 10%, whichever is lower, with a 15-year certificate-of-occupancy exemption that is a separate legal question.

**Coordination note — duplicate work with `arena/3119787c` (PR #119).** That session independently found and corrected the *same* Federal Reserve citation on 2026-11-17, and its PR title also proposes a distribution schematic. The correction therefore exists twice. PR #119 is small and focused; this branch is large and overlaps `tools/sitebuild.py`, `tools/test_case.py` and the generated pages, so a rebase will conflict. Recorded here rather than resolved unilaterally, because PR #119 belongs to another live session. The correction is not credited to this session alone.

**80E9-3 — the staging question, actually tested.** A single-drawdown sensitivity cannot answer whether staging softens crash-entry risk, because the answer depends on where in the window the crash lands, how long recovery takes, and what the reserve earns once yields fall. Added `assets/staged-vs-lump.js`: nine fixed, named scenarios varying crash month, drawdown depth, recovery duration and post-crash reserve yield, every one evaluated at the **same 60-month date** so a late crash cannot look benign merely by being measured early. Results at a 4% reserve yield and 7% drift:

| Window | Staged ahead | Median | Worst |
| --- | --- | --- | --- |
| 24 months | 5 of 9 | +3.4% | -4.7% |
| 36 months | 7 of 9 | +6.3% | -7.3% |

The substantive finding is that staging buys protection against a crash arriving **early**, and pays for it with the equity-minus-Treasury spread when the market simply rises. A crash as the window closes is close to a wash. In the 1929-shaped cases staging helps but does not rescue: even at 36 months the staged path is roughly a third behind a calm market, which is why the page says plainly that no staging schedule converts a 25-year recovery into a safe one.

Two real bugs were found by writing identity tests first, and both are published on the Flagged page rather than quietly fixed:

1. **Reserve interest was never deployed.** A fixed dollar slice per month left interest earned during the window permanently undeployed, so the staged path silently held cash the household never chose and the two paths were no longer comparable at the same asset mix. Deployment is now an equal fraction of the remaining reserve, which drains the reserve exactly when the window closes (verified 0.00e+0) and makes the post-window ratio identity exact to 2.2e-16 rather than 4.2e-2. The corrected numbers are **less** favourable to staging.
2. **The flat and rising no-crash scenarios were the same test twice**, because both used the caller's drift. Each now pins its own drift.

Three of my own initial test premises were also wrong and were corrected rather than forced: a crash makes staged and immediate differ even at zero yield; peak-to-trough percentages legitimately differ between the paths once one has held cash; and the drawdown identity holds only after the window closes.

**80E9-4 — decisions name an ID.** Suggestions now carry **S-01 … S-13**. The review controls emit a dated, copyable decision-log line keyed by the ID, because a reworded title is not an identifier. Session only; nothing stored or sent.

**80E9-5 — rebuilding states whether the answer moved.** Adopted `tools/recheck.py` from the closed PR #107 (credited there), which fingerprints the published evidence layer and prints **UNCHANGED** or **MOVED** with the aspects that changed, and refuses a `--private-model` path inside the repository. Wired into CI before the reproducibility check. This converts the standing instruction "after any input change, rebuild and see whether the recommendation moved" from a good intention into an executable step.

**80E9-6 — stale pull requests triaged.** All five closed without merging, with a reason on each:

| PR | Reason |
| --- | --- |
| #107 | Superseded; unrelated history; its predecessor branches publish household figures. Its `tools/recheck.py` was adopted to `main` first, with credit. |
| #106 | Unrelated history; publishes a private-file page plus household property profiles. |
| #104 | Unrelated history; household-figure approach; its Proposition 19 correction was independently re-derived and is already published. |
| #103 | Unrelated history; a locality-specific measure page next to household profiles is the prohibited combination. |
| #19 | Coordination-only branch carrying `_research/notes.jsonl`; research notes do not belong in a public tracked tree. |

Closing a pull request **does not** remove its commits from the repository. Under GitHub's own guidance, cached pull-request views and forks are a separate remediation path. Closing these five narrows what is still actively published; it does not restore privacy.

**Privacy finding that contradicts a stated requirement.** Rounding figures to the nearest $10 was requested as a de-identification control. It is not one. County assessment rolls are public and searchable, so an assessed value rounded to the nearest $10 still narrows a county's parcels to a handful and the roll supplies the address. A postal code plus a rounded assessed value plus a unit count plus an inherited-versus-owned status plus a monthly rent is a fingerprint even when every field is coarsened. The privacy page now states this in four rows, each with the failure mode and the control that actually works: publish no assessor-derived amount at all, and keep the amount in the offline workpaper. This is recorded as a disagreement with the brief rather than silently complied with.

**Additional work (80E9, part 2).** Three further items were completed after the first record:

- **Black-swan page now argues about method.** The brief's own premise — that growth and inflation are never consistent over 50 years — is a critique of the modelling method, not a request for a different constant. The page now carries a table of what official sources do and do not establish (CBO bounds its horizon; FHFA's index is not an appraisal; a CPI index measures the past; no official body publishes a 50-year property projection), the specific regimes a smooth average deletes (Great Inflation, Great Depression, 2007-09 with housing and equities falling together), and the one line that is genuinely bounded rather than forecast: the statutory 2% ceiling on the annual inflation adjustment under RTC 51. The decision rule implied is stated: run each regime, and if the answer changes, report a hedge or a delay rather than a point forecast.
- **The audit tool's own comments were restating the values.** The encoded pattern list was correct, but two trailing comments spelled out what each fragment decoded to, so the file still published the exact figures it was auditing for — the same fault one layer down. Comments removed. Added a regression test that greps every tracked file for all twelve patterns; the test states its own limit, that a finite pattern list cannot establish containment. The working tree now greps clean for every identifier and value shape.
- **`recheck.py` accepted a moved baseline.** After the black-swan and privacy tables were added, the tool reported MOVED with the specific changed aspects (page count, badge counts, site hash). The pages were re-read and the baseline accepted, which is the intended workflow rather than a rubber stamp.

Final state of the exposure counterexample, recorded so it is not repeated: **two files in this repository carried the identifiers in plaintext while claiming to protect them**, and a third version carried them in comments. Every one was caught by a scan, not by review. That is the argument for the executable check over a promise.

### Verification (80E9)

- `python3 tools/build.py`: pass, **23** pages (was 22; the Verified lookups page is new).
- `python3 tools/verify.py`: pass. Every table row has an official source and an evidence badge, source hosts are on the allowlist, all local links resolve (**576** checked), each page has one `h1`, noindex, a restrictive CSP, no inline script, no remote resource, no browser storage. New fail-closed checks: any currency amount not on the reviewed list fails the build, and the lookups page must keep its read dates, the 2027 exclusion and the indexed cap.
- `python3 -m unittest discover -s tools -p 'test_*.py'`: **23** tests pass.
- `node --check` on `assets/app.js`, `assets/staged-vs-lump.js`, `assets/phase-model.js`: pass.
- Chart smoke test (`tools/smoke/chart_smoke.js`, no npm dependency): renders **9 bars, 18 labels** and the expected summary line. Run under the same `node` CI already uses.
- `python3 tools/recheck.py`: reports UNCHANGED against the committed snapshot.
- `git diff --check`: pass.
- Local static server: all **23** pages and all **4** assets return 200; **0** broken internal links.

### Limits and open items (80E9)

- **Historical exposure is still unresolved and is the highest-urgency item.** This session narrowed what is newly published and stopped the audit and test files from republishing identifiers. It did **not** rewrite history, change repository visibility, or reach forks and caches. No amount of site work substitutes for an owner decision on visibility followed by administrator-led history remediation with a private encrypted archive preserved first.
- Outbound network access from the sandbox is limited, so external source URLs could not be polled directly with `curl`. The **substantive** pages cited here were opened with the fetch tool and quoted from (Federal Reserve History ×3, BOE Proposition 19 and LTA 2025/009, IRS IR-2026-133, IRS Topic 701, CBO, FHFA, TreasuryDirect bills, Civil Code 1947.12, Revenue and Taxation Code 51 and 63.2). The remaining allowlisted sources were re-registered but not individually re-opened in this session and are marked as requiring recheck at use.
- `tools/privacy_scan.py` reports fragment matches. A match is not proof that a full address or figure is present, and no match is not proof of containment, because the pattern list is finite.
- The nine staging scenarios are assumption sets chosen to stress the decision, **not** a sample of market outcomes. "Staged ahead in 5 of 9" describes the scenario set, not a probability. Dividends, fees, taxes, inflation and withdrawals are omitted.
- No household figure, location, postal code, rent, assessment history or derived recommendation is published. This branch adds no private input and reads no private file.

### 80E9 release record — PR #120 merged, Pages verified live

- **PR:** [#120](https://github.com/wingbangboozle1-lang/Tino4/pull/120) — merged with `gh pr merge 120 --merge` at 2026-11-17T16:58:45Z.
- **Merge commit:** `b002bd1ac3cddfd909fb6d512c56352efce6f979` on `main`.
- **CI:** `verify` run on the merge commit `b002bd1` completed **success**. `pages-build-deployment` on `b002bd1` completed **success**. Pages API reports `built` at https://wingbangboozle1-lang.github.io/Tino4/.
- **Live verification:** the published pages were fetched after deployment and carry the merged content. `pages/verified-lookups.html` serves the dated lookup table with the read dates and both Proposition 19 figures. `pages/phased-investing.html` serves the corrected scenario table (59.3%, 15.6%, 13.1%, 3.4%, -2.0%, -0.4%, -1.6%, 4.2%, -4.7%), the summary line "5 of 9, median 3.4%, worst -4.7%", and a rendered 9-bar chart with the legend "Staged ahead in 5 of 9 scenarios". The chart is confirmed drawn in the live page, not merely present as markup.
- **Six rebases were required.** `main` advanced six times during this session (PRs #117, #118, #119, #121, #122 and the auto-generated version bump runs), each time on overlapping files. Every conflict was resolved without discarding the other session's work, and every resolution is recorded in the commit messages. Notable resolutions: main's black-swan page absorbed and superseded this session's version (kept main's, dropped mine deliberately); the suggestions page kept **both** numbering schemes (main's S1-S10 review board and this session's S-01..S-13 action registry) and now explains why two schemes coexist; main's corrected `cbo_long` URL was restored rather than regressing to the version with the 404.
- **Duplicate work, recorded honestly:** session `arena/3119787c` independently found and corrected the same Federal Reserve citation on the same day. The correction is not claimed as this session's discovery. Two sessions also independently added a "dead CBO link" flag.
- **CI failure found and fixed twice, both real:** the `recheck` step failed on the first push because the committed fingerprint did not match a fresh build after the rebase, and again after the final rebase. Both times the fix was to re-read the affected pages and accept the new baseline, not to weaken the check.

### Still open after 80E9 (owner decisions, not code)

1. **Repository visibility and history remediation.** Highest urgency. 81–82 of 87 refs still contain identifying material; the repository is public. Closing five pull requests narrowed what is newly published but removed no commits.
2. **Repository access review.** 82 branches remain, most from earlier sessions. Branch deletion alone does not remove commits referenced by pull requests or forks.
3. **Whether the public site should exist at all** in its current relation to the private case. The site is clean; the repository's history is not. Separating them entirely is the only arrangement that does not depend on the current tree staying clean forever.
## Session `arena/40e65d44` — phased-investing black-swan path, model ranges, rounded analysis reporting

Branch: `arena/40e65d44-tino4` (platform-fixed; branched from `4c1aa93`, rebased onto `origin/main`). Status: active.

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| 40E6-1 | Claim tasks and record the session's figure-reporting policy decision | done | `arena/40e65d44` | `COORDINATION.md` | 2026-11-17 |
| 40E6-2 | Re-verify official sources (estate thresholds, Prop 19 indexed limit and deadlines, transfer tax, tax-rate-area method, Form 540 line 62, local measure "Prop H" terms, Treasury yields, rental comparables research) | done | `arena/40e65d44` | research; source scopes | 2026-11-17 |
| 40E6-3 | Build deterministic low/base/high model (rounded to $10) with transfer-year sale first, mixed paths, imputed rent, Section 121 switch, depreciation/recapture, transfer tax + recording in sell path, staged 3M–2Y Treasury path | done | `arena/40e65d44` | `tools/sitebuild.py` (self-contained model section) | 2026-11-17 |
| 40E6-4 | Black-swan page: phased-investing path testing 1929/2008 crash entry with reinvestment risk beside the headline; distribution chart on projections | done | `arena/40e65d44` | `tools/sitebuild.py`, `assets/app.js`, generated pages | 2026-11-17 |
| 40E6-5 | Privacy tooling: enforce $10 rounding, placeholders, banned locality tokens across all pages; keep historical-exposure runbook | done | `arena/40e65d44` | `tools/verify.py`, `tools/test_case.py` | 2026-11-17 |
| 40E6-6 | Rebuild, verify line by line, tests, PR to main, merge, confirm Pages, record release | done | `arena/40e65d44` | release checks and this board | 2026-11-17 |

### 40E6-6 release record (2026-11-17)

- PR: https://github.com/wingbangboozle1-lang/Tino4/pull/128 (branch `arena/40e65d44-tino4` -> `main`), merged with `gh pr merge 128 --merge`; merge commit on `main`: `826e712` ("Merge pull request #128 from wingbangboozle1-lang/arena/40e65d44-tino4").
- Integration history inside the PR: two conflict-resolution merges preserved the parallel sessions' work rather than replacing it — `77d5618` merged PRs #124-#127 (case_model quantified model, regime engine, fan chart, encoded-identifier guard) and `c8d8d51` merged PRs #129/#131 (zero-versus-small display fix). The session `arena/020b35d4` note flagging PR #128 as a duplicate-model PR was addressed by exactly the rebase-onto-merged-model it recommends.
- Gates before each push: `python3 tools/build.py` (26 pages), `python3 tools/verify.py` (clean), `python3 -m unittest discover -s tools -p 'test_*.py'` (63 tests), `node --check` on `app.js`, `phase-model.js`, `staged-vs-lump.js`, `regime-model.js`, `python3 tools/recheck.py` (UNCHANGED), `git diff --check`.
- GitHub Pages confirmed for this merge: `gh api repos/wingbangboozle1-lang/Tino4/pages` reached status `built` after the merge, and the live site at https://wingbangboozle1-lang.github.io/Tino4/ was re-fetched and serves the merged content (the law-watchlist page shows the Nov. 3, 2026 parcel-tax terms with the SFMTA and election-results source links; the certification/litigation row remains flagged "Not verified").
- Delivered on the public site from this session's task list: rounded-to-$10 household figures marked "Household-reported (rounded)" with low/base/high bands; executive summary with a conditional best plan, why, and what-would-change-the-answer; transfer-year sale modeled first (2040/2045/2050 tables); family-home claim/no-claim transfer branches; asking-rent comparables ranking the letting paths (floor, unverified); five-year capital plans for both buildings; tax-rate-area lookup method with the number kept in the private workpaper; estate-size scenarios plus portability/prior-gift questions; like-kind-exchange decision gate and date-of-death valuation note; depreciation-recapture and imputed-rent tools; "Prop H" official terms published with official links (jurisdiction mapping private); the phased-investing crash-entry path in the black-swan section with reinvestment risk beside the headline; a seeded distribution chart with percentile table; and dated project decisions on the decision-log page.
- Remaining flagged items (do not block; tracked on the Flagged page): Property B tax-to-assessment ratio irregularity pending bill reconciliation; insurance premiums unverified; rental comparables are asking rents; Prop H certification/litigation unverified; rounding-granularity trade-off reviewable; historical repository exposure still requires administrator remediation (`tools/history_scrub_runbook.md`).

### 40E6-1 policy note (figures on the public site)

The owner's restated brief (2026-11-17) requires two things at once: (a) personal information is anonymized with placeholders and never published, and (b) costs and numbers are **used and reported** in the decision analysis, rounded to the nearest $10 so they cannot be traced back to a source. This session therefore publishes: rounded-to-$10 household figures marked "Household-reported (rounded)", placeholders only (Property A / Property B / the household / the heir), projections as labeled low/base/high assumption bands, and a gated recommendation. It does **not** publish: names, street addresses, postal codes, parcel or account numbers, lease terms, or locality names for either property (banned-token scan kept). Locality-sensitive law (tax rate area number, local measure mapping) is reported as terms and published rates without naming the locality; the mapping stays in the private workpaper. Rounding granularity is itself a reviewable suggestion on the Suggestions page.

## Session `arena/020b35d4` — quantified decision model on a rounded, de-identified basis

Branch: `arena/020b35d4-tino4` (platform-fixed; active). Base: `4c1aa933f1203827368eba14359eee6de9cc6a3a`.

Session ID: `arena/020b35d4`. Claim pushed before work began.

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| 020B-1 | Add a build-time quantified model (`tools/case_model.py`) that turns the rounded case inputs into year-by-year projections, path comparisons, Prop 19 tax math, operating-cost projections, estate-threshold math and the Treasury-staging crash test — all emitted rounded to the nearest $10 with no locality identifiers; publish the numbers on existing pages plus two new pages | in progress | `arena/020b35d4` | `tools/case_model.py`, `tools/sitebuild.py`, `tools/verify.py`, `tools/test_case.py`, `tools/site-manifest.json`, `assets/style.css`, generated `index.html`, `pages/projections.html`, `pages/decision-analysis.html`, `pages/property-tax.html`, `pages/estate-thresholds.html`, `pages/operating-costs.html`, `pages/black-swan.html`, `pages/phased-investing.html`, `pages/attorney-cpa-brief.html`, `pages/questions.html`, `pages/suggestions.html`, `pages/requirements-tracker.html`, `pages/flagged-for-review.html`, `pages/glossary.html`, `pages/sources.html`, `pages/privacy.html`, `pages/property-profiles.html`, `pages/economic-baselines.html` (new), `pages/model-figures.html` (new), `README.md`, `COORDINATION.md` | 2026-11-17 |

### Coordination notes for other sessions

- Open PRs from earlier sessions are still listed as OPEN but their branches predate `main` at `4c1aa93` (PR #103, #104, #106, #107, #19). This session does not edit or merge those branches. Anything in them that is still wanted should be re-applied on top of current `main` by their owners; this session's work is additive to `main` only.
- Privacy boundary chosen by the owner in the current request: figures are published **rounded to the nearest $10**, and the phrase naming the source of an input is itself avoided on public pages with no names, addresses, postal codes, parcel identifiers or locality names. `tools/verify.py` enforces the rounding and the identifier patterns (fail-closed). Rounding reduces but does not eliminate traceability; that residual risk is stated on the privacy page and flagged for owner review.

### Result — 020B-1 (2026-11-17)

**What was built.** `tools/case_model.py` is a self-contained, deterministic build-time model. It reads no file
(`verify.py` rejects `open(`/`.read_text(` in both generator and model code), holds only rounded case inputs as
literals, and regenerates every figure printed on the site, so a page and its arithmetic cannot drift apart.
Committed output is byte-identical to a fresh `python3 tools/build.py`, which the CI reproducibility step checks.

- **Paths:** seven live/let/sell/mixed paths priced at one transfer date and one horizon under five economic
  scenarios (flat, block sequence, block sequence with the bust rotated to the transfer year, stagflation,
  deflation), in cash, in economic terms, and in constant 2026 dollars. Self-used ownership is credited with
  net market rent (imputed rent); portfolio return compounds and is never also counted as a flow. The already-owned
  three-unit building is reported once, separately, because it is invariant across paths.
- **Property tax:** RTC §63.2(d) cap arithmetic (prior taxable value + max(0, value − (taxable + allowance))),
  the Prop 19 allowance carried forward by an explicit, labelled escalation assumption rather than frozen at the
  published figure, the three bill outcomes (no transfer event / qualifying claim / reassessed), and the enacted
  claim windows, 45- then 60-day notice sequence, ≤$175 processing fee and late-claim factoring penalty as
  amended by SB 293 (effective 2026-01-01).
- **Sale:** gross-to-net waterfall with statutory documentary transfer tax ceilings (RTC §11911), recording and
  report items, basis at the date-of-death value, §121 exclusion switch for the live-then-sell row and
  §1250-style recapture on the letting rows; a sale inside the transfer year is shown as neither taxed nor
  deductible rather than as an exemption.
- **Staging:** the 1929 (−89 %, 25-year recovery) and 2007-09 (−57 %) shapes tested at five shock timings, staging
  costed inside the path table as a blended bills/equity wait, and reinvestment risk published beside it.
- **Volatility:** the geometric-versus-arithmetic gap of the block path is disclosed wherever the sequence is used,
  and the ranking flip under a bust at the transfer date is published as the answer, not hidden.
- **Estate:** exclusion indexation (2025/2026/2027 published figures), prior-gift and portability questions,
  sensitivity rows only — the estate's financial assets are absent by design and flagged.

**Site.** 22 → 26 pages: `pages/economic-baselines.html` and `pages/model-figures.html` added by this session,
quantified addenda on thirteen existing pages, priced pre-agreed decision rules in the log, and two further merges
over `arena/80e9d3b3` (verified lookups, break-even page, staging chart, `recheck.py`) and `arena/32426e4a`
(regime engine, fan chart, review backlog) resolved by keeping both sides. `PAGES`, the manifest, `verify.py`'s
page count and the recheck snapshot moved in the same commit each time.

**Verification.** `python3 tools/build.py`, `python3 tools/verify.py`, **57 unit tests**, `node --check` on all
four scripts, the chart smoke test, `python3 tools/recheck.py` and `git diff --check` all pass; the committed tree
is byte-identical to a fresh build. The verifier additionally rejects a household-input marker, a seeded
record amount, digit runs without separators, locality and address patterns, storage, network calls and
unsourced table rows.

**Release record.** **PR #125** — merged with `gh pr merge 125 --merge`; merge commit `cc70bb5` on `main`;
`verify` run 44137412400 success; `pages-build-deployment` run 44137410743 success; the published
`pages/model-figures.html` was fetched afterwards and serves the quantified provenance table, so the deploy is
confirmed live rather than queued. Three follow-ups followed, each merged the same way: #126 stopped printing an
assumption band midpoint as if it were a measurement, #127 restated the near-zero sale-year gain as the
transfer-to-closing drift rather than an amount, and the last commit fixed a real defect #127 exposed - the
display layer fuzzed every figure under 2,000 dollars into an order of magnitude, so a true zero (a sold home's
property cash flow) read as "under twenty-five dollars", a small measured amount, instead of an absent one. A test
now pins that distinction.

### Flagged for review from this session (does not block merge)

- Rent, insurance, the effective levy per parcel, the appraisal, the leases and the estate's financial assets are
  **not** official-source figures; the pages carry them as assumptions or as flagged inputs, never as evidence.
- The next Prop 19 allowance revision (February 2027, from the 2026 California FHFA figure) does not exist yet;
  the 2026Q4 release is scheduled for 2027-02-23.
- Short-rate levels for the staging window could not be retrieved from the Treasury feed in this environment; the
  staging yield is an input and a sensitivity, with the current level left blank on the page.
- The BLS October 2026 release publishes no 12-month change for most series because October 2025 was not collected
  during the appropriations lapse; the inflation anchors therefore come from the annual historical table.
- Historical public exposure (earlier commits, PR views, forks, caches) is not remediated by this branch; the
  repository is shallow here, so a rewrite cannot be executed or verified from this sandbox. See
  `tools/history_scrub_runbook.md`.

### Reconciliation with the boundary recorded by `arena/80e9d3b3` (this session)

That session's finding — that rounding to $10 is not anonymization, and that no assessor-derived amount should
be published at all — is adopted here rather than argued with. The quantified model therefore publishes **no**
roll figure: the assessed values and bill amounts of both buildings stay in the private workpaper, and the pages
print only (a) values the model derives under a stated rule, and (b) computed results. Where a table needs an
assessed-value line it is labelled as a modelled, escalated base rather than a record. The model-figures page now
states "not published" for every assessor-derived input and names where it lives.

This session also merges over `pages/verified-lookups.html`, `pages/break-even.html`, `assets/staged-vs-lump.js`,
`tools/privacy_scan.py` and `tools/recheck.py`; the two new pages added here (`economic-baselines`, `model-figures`)
bring the count from 24 to 26, and `PAGES`, the manifest and `verify.py` move together. The framework snapshot for
`tools/recheck.py` is regenerated in the same commit so the CI recheck step passes.

### Second reconciliation (this session) — merged over `arena/32426e4a` (PR #124)

The regime-engine, fan-chart and review-backlog work landed on `main` while this branch was open, and its
`verify.py` added a statute-context exemption to the five-digit postal scan plus a per-amount source allowlist.
Both are adopted: the postal exemption is a genuine false-positive fix, and this session's verifier now runs on
top of main's file rather than replacing it. Two of this session's own controls were tightened in response to
that merge rather than argued with:

- the seeded-record guard (amounts that are copies of a bill, roll entry or rent roll) is computed from the
  model's own `RECORD_FIELDS` and rejects them without printing the value, so the CI log cannot become the leak
  that the postal-message style would have created;
- the model's own locality patterns moved into the same encoded form, because the guard file itself had begun
  carrying them in plaintext.

Page count moved 24 → 26 in the same commit as `PAGES`, the manifest and the recheck snapshot.

### Cross-session note: `arena/40e65d44` PR #128 is the same task, landed second

PR #128 (`40E6: rounded-figure decision model integrated with verified-source layer, 24 pages`) is building the
same quantified model this session built and merged as #125/#126/#127/#129. `main` is now at
`5bba899` with **26 pages**, `tools/case_model.py`, an encoded-pattern privacy guard and 57 tests, so #128's
base predates all of it and its page count (24) will conflict with `PAGES`, `tools/site-manifest.json`,
`tools/verify.py` and `tools/framework-snapshot.json` by construction.

Recommended handling, in this order, by #128's owner: (1) `git rebase origin/main` and read the conflicts in
`tools/sitebuild.py` before resolving — the quantified addenda are generated by `quantified()` per page path and
must not be pasted into `base_content_for`; (2) re-read `tools/case_model.py` first, since it already implements
the transfer-year sale ordering, the Prop 19 §63.2(d) cap with the allowance carried forward, the staging path
with reinvestment risk beside it, and the proceeds distribution block; (3) if a figure in #128 is an
assessor-, bill- or lease-derived amount, it cannot be published at all — the seeded-record guard in
`tools/verify.py` will fail the build, and the fix is to move it to `RECORD_FIELDS` and state it in words, not to
extend the allowlist; (4) bump the page count only if a genuinely new page is added, and do it in the same
commit as `PAGES`, the manifest and the recheck snapshot. Anything in #128 that is a *better model choice* rather
than a duplicate should be re-applied as a small follow-up PR against `main`, with tests first — that is how the
`fmt()` zero/small defect in #129 was caught.

## Session `arena/b9a46c93` — prose/model consistency pass and the return-hurdle reading

Branch: `arena/b9a46c93-tino4` (platform-fixed). Status: active.

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| B9A4-1 | Reconcile this session's rounded-figure model with `main` landing `tools/case_model.py`: retire the duplicate so the site publishes one model, not two | done | `arena/b9a46c93` | `tools/sitebuild.py`, `README.md`, ignored `private-work/**` | 2026-11-17 |
| B9A4-2 | Fix the framework prose that still said no figures are published, on every page where the quantified layer now publishes them | done | `arena/b9a46c93` | `tools/sitebuild.py`, generated `index.html`, `pages/**` | 2026-11-17 |
| B9A4-3 | Guard test so the prose cannot drift from the model again | done | `arena/b9a46c93` | `tools/test_public_claims.py` | 2026-11-17 |
| B9A4-4 | Return-hurdle reading on the break-even page: the flat after-tax return the proceeds must beat, per scenario and horizon, computed from the model's own terminals | done | `arena/b9a46c93` | `tools/sitebuild.py` (`_q_return_hurdle`), generated `pages/break-even.html` | 2026-11-17 |
| B9A4-5 | Re-accept the recheck baseline for the changed layer | done | `arena/b9a46c93` | `tools/framework-snapshot.json` | 2026-11-17 |

### Scope notes for other sessions

- **`tools/sitebuild.py` line 1800 region (`_q_*` break-even section) is the only place this session touched in
  the model-facing code.** `tools/case_model.py` was deliberately **not** modified: the published model stays
  single-sourced. Anyone adding a second model or a second set of figures should extend `case_model.py` instead
  of writing figures into a page.
- This session's private workpaper (`private-work/model-workpaper.md`, git-ignored) records the owner's exact
  figures, the derived levy ratios, and the evidence queue. Nothing personal is in the repository, and this
  session did not rewrite Git history.
- The earlier claim on this board that PR #115 "currently claims" `tools/verify.py` and `tools/test_case.py` is
  obsolete: #115 merged into `main` at 2026-11-17T16:41:28Z, so those files are free for whoever needs them.
- `python3 tools/recheck.py` reports whether the published evidence layer moved; accept a new baseline only in
  the same commit as the change that caused it. `python3 tools/privacy_scan.py` is read-only and reports counts.
- The privacy finding this session confirmed by computation: rounding to $10 is a traceability step, not
  anonymization (county rolls are public and searchable), so the site's rule stays "modelled amounts published,
  case-record amounts withheld". Do not "fix" the privacy page by promising more than that.

### Reconciliation of this session's duplicate model (2026-11-17, second pass)

- This session had written a full rounded/unit-scaled model into `tools/sitebuild.py`. `main` landed
  `tools/case_model.py` with a `quantified()` addendum on every page while that work was in flight, so the
  duplicate was **retired** rather than merged: one site, one model, one set of numbers. The unit-dollar
  scaling was dropped too, because main's boundary (modelled amounts published, case-record amounts and all
  identifiers withheld) already answers the re-identification finding, without making the tables opaque.
- What survived from this session: the prose alignment (thirteen framework statements still claimed the site
  publishes no figures, no ranking and no amounts while the quantified layer published all three), the
  return-hurdle reading on `pages/break-even.html` (the flat after-tax return the proceeds must beat, per
  scenario at 10/20/30 years, computed from the same `cm.path_table` terminals as the ranking), and
  `tools/test_public_claims.py`, which fails the build if the stale claims or an unlabelled figure returns.
- Gates run before push: `python3 tools/build.py` (26 pages), `python3 tools/verify.py` (clean),
  `python3 -m unittest discover -s tools -p 'test_*.py'` (68 tests), `python3 tools/recheck.py --update`
  accepted in the same commit, `node --check` on the four browser modules.
- Still open for the owner/administrator, unchanged by this session: the Git-history exposure
  (`tools/privacy_scan.py`, `tools/history_scrub_runbook.md`), the Property B levy-to-roll ratio awaiting the
  bill lines, insurance quotes, and written rent comparables.

## Session `arena/f1fa9937` — headline-rule spot-check, privacy-scan precision, owner-brief intake

Branch: `arena/f1fa9937-tino4` (platform-fixed; based on `main` at `c41ca9f`). Status: active.

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| F1FA-1 | Re-read the two headline official figures (IRS 2026/2027 estate exclusion; BOE Letter 2025/009 Prop 19 $1 million amount) directly from source; record the result | done | `arena/f1fa9937` | `COORDINATION.md` | 2026-11-19 |
| F1FA-2 | Triage the `tools/privacy_scan.py` value-shape hits on `main` (`pages/operating-costs.html`, `pages/projections.html`); make value-shape matching word-bounded so a shape cannot match inside a longer model figure; add a regression test | done | `arena/f1fa9937` | `tools/privacy_scan.py`, `tools/test_privacy_scan.py` | 2026-11-19 |
| F1FA-3 | Owner brief intake (2026-11-19): household property-tax, assessment, rent, utility and insurance figures supplied in chat are **not** published or committed; the public site keeps the existing rule (rounded modelled outputs only, no assessor-derived amounts) | done | `arena/f1fa9937` | `COORDINATION.md` | 2026-11-19 |

### F1FA-1 result (2026-11-19) — headline figures re-read from source

- IRS news release IR-2026-133 (Nov. 5, 2026), https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2027-taxpayers-continue-to-benefit-from-the-working-families-tax-cuts : estate basic exclusion **$15,480,000** for decedents dying in 2027, "up from a total of $15,000,000" for 2026; annual gift exclusion **$20,000** for 2027, up from $19,000 for 2026. Matches `pages/verified-lookups.html` and `pages/estate-thresholds.html`.
- BOE Letter to Assessors No. 2025/009 (Mar. 7, 2025), https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf : the Prop 19 / R&T §63.2 "$1 million amount" is **$1,044,586** for transfers Feb. 16, 2025 – Feb. 15, 2027; next adjustment Feb. 2027. Its enclosed table gives $1,000,000 (2021–23) and $1,022,600 (2023–25). Matches the site.
- Irregularity (not a site error): the first attempted fetch used a mistyped filename and returned 404; the site links the correct `lta25009.pdf`. Recorded so a reviewer does not treat the 404 as a broken source.
- Not re-verified in this session: the Form 706 unified-rate and credit-equivalent figures and the Form 540 1% rule (prior sessions' rows; left as recorded).

### F1FA-2 result (2026-11-19) — privacy-scan precision and a corrected full-history audit

- **Precision fix:** the two `main` hits were false positives. `pages/operating-costs.html` and `pages/projections.html` contain model figures whose digits contain a published value-shape string as a substring. Value-shape patterns are now word-bounded (`git grep -w`); identifier patterns keep substring matching deliberately. Regression tests: `tools/test_privacy_scan.py` (3 tests pass). No household figure appears on `main`.
- **Correction to my own first run:** the clone was shallow, so the first scan (4 refs) reported "clean". That was not a real result. After `git fetch --unshallow` and fetching all 92 remote branches, the full audit ran on 93 refs: **81 refs contain identifying material; the deepest affected ref has 52 commits.** `main` itself is not in the affected list. This matches the README's 2026-11-17 measurement (82 of 87 refs; the ref count has since changed).
- **Decision not taken here:** a history rewrite would force-push over about 90 other sessions' branches and any open PR. `tools/history_scrub_runbook.md` requires an encrypted archive, collaborator coordination and administrator approval first. **Owner decision needed:** (a) approve an archive plus rewrite or branch-pruning plan, or (b) accept the exposure and keep the public site limited to the current rules. Until then, the audit result stays "exposure present on non-main refs".
- Stale board entry noted, not edited: `020B-1` still reads "in progress" although its work landed through PR #124 and later merges; the owning session should close it.

### F1FA-3 result (2026-11-19) — owner brief intake

- The owner's new household figures (property-tax and assessment tables for both properties, rents, utilities, insurance estimates, the two property valuations) were received in chat. They are **not** written to the repository, the public site, or a tracked file. The current rule is unchanged: rounded modelled outputs may be published; assessor-derived amounts and case-record values are withheld.
- Verified on `main`: none of the owner's assessment or tax-history amounts appear in the published pages (the value-shape audit above).
- Owner items that remain outside the public repository: the full assessment and tax tables, the valuation and comparables, and the insurance and utility bills. These are needed for the private workpaper (`private-work/`, git-ignored) and for independent property and rent estimates.

### F1FA release record (2026-11-19)

- Gates before push: `python3 tools/build.py` (26 pages, no generated diff), `python3 tools/verify.py` (clean), `python3 -m unittest discover -s tools -p 'test_*.py'` (71 tests pass, including the new `tools/test_privacy_scan.py`), `python3 tools/recheck.py` (UNCHANGED), `node --check assets/app.js`, `git diff --check`.
- The privacy guard (`test_no_tracked_source_republishes_an_identifier`) failed twice during this session because the session's own notes quoted a zip code and a value shape. Both were removed. Working notes in this board must describe identifiers generically.
- Scope of this PR: `COORDINATION.md`, `tools/privacy_scan.py`, `tools/test_privacy_scan.py`. No page, model, or public figure changed.
- Still open for the owner/administrator: history exposure on 81 non-main refs (decision needed, see F1FA-2).
- **PR / merge:** https://github.com/wingbangboozle1-lang/Tino4/pull/134 — merged with `gh pr merge 134 --merge` at 2026-11-19T10:44:44Z; merge commit `fe8088754dd3e7aaa8ef904d0726c40cae749145`.
- **Pages:** `gh api repos/wingbangboozle1-lang/Tino4/pages/builds/latest` reports `built` for that merge commit. The sandbox cannot reach `github.io` directly (only GitHub API and package hosts are allowed), so the live URL was not fetched from here; the API status is the evidence recorded.


## Session `arena/765022d5` — final integration, verification and Pages deployment

Branch: `arena/765022d5-tino4` (platform-fixed; active). Branched from `c41ca9f` of `main`; at claim time the
branch and `main` pointed at the same commit.

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| 7650-1 | Final integration verification: rebuild, verify, tests, recheck, node syntax, whitespace check | done | `arena/765022d5` | `tools/build.py`, `tools/verify.py`, `tools/recheck.py`, generated `index.html`, `pages/**` | 2026-11-19 |
| 7650-2 | Create PR from integration branch to `main`, merge, confirm GitHub Pages deploys, record PR link and result | done | `arena/765022d5` | `COORDINATION.md`, `main`, GitHub Pages | 2026-11-19 |

### 7650-1 result — integration verification

- `python3 tools/build.py`: pass, **26 pages** built from the rounded model; no data file read, no case identifier emitted.
- `python3 tools/verify.py`: pass — every table row carries an official source and an evidence status; approved source hosts only; local links resolve; no case identifier, browser storage, network call or remote resource; every amount is a published official figure or a ten-dollar-rounded model output.
- `python3 -m unittest discover -s tools -p 'test_*.py' -v`: **68 tests pass**.
- `python3 tools/recheck.py`: reports **UNCHANGED** — the published evidence layer matches the committed snapshot, so no input change moved the recommendation layer.
- `node --check` on `assets/app.js`, `assets/phase-model.js`, `assets/staged-vs-lump.js`, `assets/regime-model.js`: pass.
- `git diff --check`: pass. Working tree clean.
- The site already delivers the requested scope: "what would change the answer" on the first screen; grouped sidebar menu with glossary; executive summary; attorney/CPA one-page printable briefing sheet; deadline timeline (inheritance-process); mixed paths compared alongside pure choices at identical transfer dates and horizons; transfer-year sale modeled first; Proposition 19 occupancy condition and indexed cap; depreciation/recapture and imputed-rent treatment; transfer tax and recording fees in the sell path; phased-investing Treasury-staging path with reinvestment risk beside the headline; black-swan 1929/2008 regimes and distribution chart; break-even questions; decision log; suggestions backlog with review queue; verified lookups register; law watchlist separating enacted law from proposals; privacy-first output with no household identifiers, zip codes, parcel numbers or locality names; all figures rounded to the nearest $10 and labelled modelled/assumption where not official.

### 7650-2 result — PR, merge and Pages deployment

- PR: https://github.com/wingbangboozle1-lang/Tino4/pull/133 — merged with `gh pr merge 133 --merge` at 2026-11-19; merge commit `d870cf3b7d2a667e3f359bf55e127efa18be4214`.
- CI: `verify` run 44508972486 (build-and-verify on the pull request) concluded `success` before the merge.
- Pages: source is the `main` branch at path `/`; live at https://wingbangboozle1-lang.github.io/Tino4/; the merge commit `d870cf3` deployed as Pages build 1383758278 with status `built` (confirmed via the GitHub Pages API; the sandbox cannot fetch github.io directly, only the GitHub API and package hosts).

### Open items carried forward (owner/administrator decisions, not code)

1. **Historical repository exposure is unresolved and remains the highest-urgency item.** The public tree is generalized and clean, but prior commits, PR views, forks, caches, downloads and clones may retain older public material. A working-tree change cannot erase history; administrator-led remediation with a preserved encrypted archive is required (see `tools/history_scrub_runbook.md` and the GitHub sensitive-data-removal guidance linked from the privacy page).
2. **Local "Prop H" terms** are deliberately withheld from the public site and unverified publicly; jurisdiction and terms must be confirmed privately with the property's own tax authority.
3. **Every property-specific fact remains missing**: date-of-death appraisal, tax-rate-area levy, local transfer-tax and recorder schedules, insurance quotes, written rent comparables, leases, and the full estate inventory including prior taxable gifts and portability. Each is marked missing on the site; none is published.
4. The private estate inventory and workpaper remain outside this repository (git-ignored `private-work/`) and must be held in encrypted private storage by the owner.

## Session `arena/0d21d66a` — make shallow privacy-scan limits explicit

Branch: `arena/0d21d66a-tino4` (platform-fixed; active).

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| 0D21-1 | After upstream's word-bounded value-shape fix, make shallow-checkout limitations explicit in the audit output and add regression coverage | done | `arena/0d21d66a` | `tools/privacy_scan.py`, `tools/test_privacy_scan.py`, `COORDINATION.md` | 2026-11-19 |
| 0D21-2 | Remove household-derived inputs from tracked public model/code and ensure public model outputs are visibly synthetic only; audit and test privacy claims | in progress | `arena/0d21d66a` | `tools/case_model.py`, `tools/sitebuild.py`, `tools/test_case.py`, `tools/verify.py`, `README.md`, generated `index.html`, `pages/**`, `tools/framework-snapshot.json`, `COORDINATION.md` | 2026-11-19 |

### 0D21-2 scope and handoff

Post-merge review found that the tracked build-time model still contains rounded household-derived inputs and that published calculations are generated from them, contrary to the public privacy boundary. No raw personal figures are repeated in this board. The prior quantified-model task (020B-1) already landed; its old in-progress row is stale. This follow-up takes over only the privacy-boundary correction, with the public model restricted to clearly labelled synthetic examples. Historical commits and old public copies remain a separate administrator-level remediation item; this code change cannot recall them.

### 0D21-1 result and rebase coordination note

- While this branch was being rebased, session `arena/f1fa9937` landed the word-bounded precision correction and full-history audit on `main`. I retained that implementation and its board record; this follow-up only ensures future shallow-checkout scans do not imply full-history coverage. No other session's work was removed.
- The scanner now omits commit-depth claims on shallow repositories and states that earlier commits were not audited. A full checkout reports that its local ref history was available; this wording does not imply external copies or server-side caches were checked.
- **Verification:** all five privacy-scanner tests pass; site build and verifier pass (26 pages); all 73 unit tests pass; all four JavaScript syntax checks, `tools/recheck.py` (UNCHANGED), `git diff --check`, and the available-ref privacy scan pass. The scan correctly reports that this checkout is shallow and earlier commits are not audited.
- **Limitation:** the current checkout is shallow; the local scan cannot establish the contents of earlier commits. The full-history results recorded under F1FA-2 remain the broader audit record; prior history exposure, PRs, forks, caches and clones still require administrator-led remediation per `tools/history_scrub_runbook.md` and GitHub's official guide: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository.
- **PR / merge:** https://github.com/wingbangboozle1-lang/Tino4/pull/136 — merged 2026-11-19T10:49:56Z; merge commit `e597a90801edde19db16ebe9be992db5f5f080a4`. The `verify` run 44509279476 completed successfully.
- **Pages:** deployment run 44509278558 completed successfully; Pages API reports build 1383761355 as `built` for merge commit `e597a90801edde19db16ebe9be992db5f5f080a4`. A non-blocking Node.js 20 action-runtime deprecation annotation was emitted by the deploy action.

## Session `arena/5d659161` — re-verify Form 540 source coverage

Branch: `arena/5d659161-tino4` (platform-fixed; active). Original base: `c41ca9f628d2909c2a693f956e2237a6cebd986f`; rebased onto `3be9e79` after PR #137 advanced `main`.

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| 5D65-1 | Review the official 2025 Form 540 booklet, correct the stale “not fully retrieved” flag, and pin the source/status with a regression test | done | `arena/5d659161` | `tools/sitebuild.py`, `tools/case_model.py`, `tools/test_case.py`, `tools/framework-snapshot.json`, generated `pages/sources.html`, `pages/flagged-for-review.html`, `pages/operating-costs.html`, `pages/projections.html`, `COORDINATION.md` | 2026-11-19 |

### 5D65-1 result

- Reviewed the official 2025 Form 540 instructions and the complete 2025 Personal Income Tax Booklet at FTB on 2026-11-19. The current sources establish the 2025 Behavioral Health Services Tax formula: 1% of taxable income above $1,000,000, computed in whole dollars. FTB separately states California has no preferential capital-gains rate; gains are taxed as ordinary income. Added the complete booklet to the official source register, replaced the stale claim that it had not been fully retrieved, and stated the limitation clearly: 2025 material does not establish the inheritance/sale-year law for a future transfer.
- Confirmed the local sale-year sensitivity calculator uses entered other taxable income plus modeled gain and applies 1% only above the $1,000,000 threshold. Added regression coverage for zero add-on at the threshold and the 1% amount on taxable income above it.
- Privacy scan inspection found that the prior generated operating-cost/projection pages could publish a value shape matching a case-record rent figure. Replaced the single point with a broad illustrative public scenario band, explicitly not a lease or household-reported figure, and removed it from the seeded-record list. Projection-page money amounts are now coarsened to $100 and small annual lines are stated as magnitudes. The modelled Property B cash-flow sensitivity changes; none of this is a verified rent or an anonymization guarantee. Independent written rental estimates and lease review remain required.
- **Official sources checked:** [FTB 2025 Form 540 instructions](https://www.ftb.ca.gov/forms/2025/2025-540-instructions.html), [FTB 2025 Personal Income Tax Booklet](https://www.ftb.ca.gov/forms/2025/2025-540-booklet.html), and [FTB capital gains and losses](https://www.ftb.ca.gov/file/personal/income-types/capital-gains-and-losses.html). These establish the current 2025 state-return rule only, not any private tax result or future-year law.
- **Verification after rebase:** `python3 tools/build.py`, `python3 tools/verify.py`, all 76 unit/regression tests, `python3 tools/recheck.py` (UNCHANGED), `node --check` for all four browser scripts, and `git diff --check` pass. `python3 tools/privacy_scan.py` reports no known identifier or value-shape matches on the four available refs; it also correctly warns this checkout is shallow, so earlier commits are not audited. Projection-specific regression coverage rejects previously exposed value-shape strings in rendered pages.
- **Rebase coordination:** rebased onto `origin/main` at `3be9e79` after PR #137 advanced `main`. The append conflict in `COORDINATION.md` was resolved by retaining the newer main records (F1FA, 7650 and 0D21) and adding this task record after them. No other session's work was dropped.
- **Unresolved privacy limitation:** this changes the current rendered tree only. It does not scrub old Git commits, PR diffs, forks, caches, downloads or clones. The repository is a shallow checkout; use `tools/history_scrub_runbook.md` and administrator-led remediation, and do not claim prior public copies are erased.
