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

## Session `arena/b9a46c93` — checkable scenario model in unit dollars, year-by-year projections, black-swan regime realism

Branch: `arena/b9a46c93-tino4` (platform-fixed). Status: active.

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| B9A4-1 | Publish a checkable-figure policy: property-specific amounts as unit dollars per $1,000,000 of baseline value plus ratios, nearest $10 rounding, all identifiers and household value shapes withheld; exact records kept in an ignored `private-work/` workpaper | done | `arena/b9a46c93` | `README.md`, `COORDINATION.md`, ignored `private-work/model-workpaper.md` | 2026-11-17 |
| B9A4-2 | Figure workbook: bill-history ratios, derived effective rates, anomaly flags, five-year capital plan, insurance/utility evidence steps | done | `arena/b9a46c93` | `tools/sitebuild.py`, generated `pages/property-profiles.html` | 2026-11-17 |
| B9A4-3 | Year-by-year projections 2026-2050 (market value, assessed value under three transfer branches, property tax, operating cash flow) plus the sale-proceeds distribution chart | done | `arena/b9a46c93` | `tools/sitebuild.py`, `assets/style.css`, generated `pages/projections.html` | 2026-11-17 |
| B9A4-4 | Compare pure and mixed paths at identical transfer year and horizons with taxes, debt, occupancy, capital costs, liquidity and reinvestment risk; add local what-if controls | done | `arena/b9a46c93` | `tools/sitebuild.py`, `assets/app.js`, generated `pages/decision-analysis.html` | 2026-11-17 |
| B9A4-5 | Black-swan realism: verified official baseline anchors and regime sequences over a 50-year horizon, plus the Treasury-staging path (3-month to 2-year, 24-36 months) tested against 1929/2008 crash-entry risk | done | `arena/b9a46c93` | `tools/sitebuild.py`, `assets/app.js`, `assets/style.css`, generated `pages/black-swan.html`, `pages/phased-investing.html` | 2026-11-17 |
| B9A4-6 | Refresh executive summary, questions, suggestions, requirements tracker, decision log, attorney & CPA brief, deadline timeline, estate thresholds, property-tax, glossary, law watchlist, privacy and source register with the verified 2026-11-17 readings | done | `arena/b9a46c93` | `tools/sitebuild.py`, generated `index.html` and `pages/**` | 2026-11-17 |
| B9A4-7 | Model regression tests in a new test module, rebuild, verify, PR, merge, Pages deploy confirmation | in progress | `arena/b9a46c93` | `tools/test_model.py`, `COORDINATION.md`, `README.md` | 2026-11-17 |

### Scope notes for other sessions

- This session does **not** edit `tools/verify.py`, `tools/test_case.py`, `tools/recheck.py`, `tools/privacy_scan.py`,
  `tools/framework-snapshot.json` content policy, or `assets/staged-vs-lump.js` / `assets/phase-model.js`. It accepted a
  new `tools/recheck.py --update` baseline because the published evidence layer changed; that is the documented flow,
  and the acceptance is recorded in the same commit as the change.
- **Rounded figures vs the identifier guard, reconciled 2026-11-17.** `origin/main` added a repo-wide test that blocks
  the household's value shapes (two market estimates, one monthly rent figure, and the two roll values the owner reported) from
  being tracked anywhere, and a privacy page that explains why rounding to $10 is not anonymization while county rolls
  stay public and searchable. Both were kept, unmodified. This session's deliverable - a ranking that can be checked
  line by line without publishing the household's numbers - now satisfies that guard by publishing property-specific
  magnitudes as **unit dollars** (dollars per $1,000,000 of the household's 2026 baseline value) plus ratios, with the
  ranking itself scale-invariant. Official amounts (estate exclusion, section 121 amounts, the Proposition 19 indexed
  limit, the state thresholds) are printed exactly as issued so a reader can compare against the source directly.
  `tools/sitebuild.py` grew `raw_usd` / `usd` (scaling) / `official_usd` / `rounded_usd` formatters to make the rule
  structural: a new table cannot leak a household amount by accident.
- Consequence for anyone editing `tools/sitebuild.py`: never print a household-derived amount through
  `official_usd`/`rounded_usd`, and never print an official amount through `usd()`. `tools/test_model.py` asserts both
  directions, and `tools/test_case.py` still scans every tracked file for the value shapes.
- This session does not rewrite Git history and does not force-push. The history exposure stays an owner/administrator
  action (`tools/history_scrub_runbook.md`), and the exact records stay in the ignored `private-work/` directory.
| B9A4-8 | Reconcile the model with `origin/main`'s identifier guard without weakening it: unit-dollar formatters, both privacy tests kept, new snapshot baseline | done | `arena/b9a46c93` | `tools/sitebuild.py`, `tools/test_model.py`, `tools/framework-snapshot.json`, `README.md`, `COORDINATION.md` | 2026-11-17 |
