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

Branch: `arena/c1f5a7d7-tino4` (platform-fixed; active). Status: in progress.

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| C1F5-1 | Read current official California Form 540 instructions, update the sale-year tax evidence, correct transfer-year gain/loss sensitivity, and regression-test the public model without adding private inputs | in progress | `arena/c1f5a7d7` | `tools/sitebuild.py`, `assets/app.js`, `tools/test_case.py`, generated `pages/**`, `COORDINATION.md` | 2026-11-16 |

### Rebase coordination note

- While replaying the claim onto current `origin/main`, `COORDINATION.md` overlapped with the just-merged `arena/04e6f1e5` crash-timing release record. Kept the entire 04e6 record and appended this task without replacing it; implementation will preserve the new crash-timing control and model.
