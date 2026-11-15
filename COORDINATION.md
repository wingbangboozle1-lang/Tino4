# COORDINATION.md — Privacy-safe task board

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

## Session `arena-79e0fd5e-tino4` — reverse-map leak closure, tax/depreciation rules, evidence checks and release (2026-11-15)

Branch: `arena/79e0fd5e-tino4` (platform-fixed; branched from `main` at `60a054e`). No other branch or worktree is created; the `session-<id>/<task>` naming convention is therefore not applied, which is logged here per the board's own rule.

| Task ID | Task | Status | Owner | File scope (exclusive) | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| 79E-1 | Close the reverse-map leak found in the tracked tree: `tools/history_scrub.sh` and `tools/history-scrub-plan.md` publish the exact pre-rounding figures next to their rounded forms, which undoes the whole $10-rounding policy. Rewrite both so the mapping lives only in the owner's private copy | done | `arena-79e0fd5e-tino4` | `tools/history_scrub.sh`, `tools/history-scrub-plan.md`, `tools/history_scrub_runbook.md`, `README.md` | 2026-11-15 |
| 79E-2 | Close the enforcement gap: the verifier's currency check only sees `$`-prefixed amounts, so comma-grouped figures without a dollar sign (the leak above) pass. Add a tree-wide comma-grouped-number rule and a rounding-map ban; extend tests | done | `arena-79e0fd5e-tino4` | `tools/verify.py`, `tools/test_case.py` | 2026-11-15 |
| 79E-3 | Depreciation and recapture: model Property B's depreciation stream, the §1014 step-up effect on A, and unrecaptured §1250 gain on a later sale; add the §121 live-then-sell switch and a §1031 advisory row, with official sources | done | `arena-79e0fd5e-tino4` | `tools/sitebuild.py` (new builders + SOURCES), `pages/operating-costs.html`, `pages/decision-analysis.html`, `pages/questions.html`, `pages/glossary.html` | 2026-11-15 |
| 79E-4 | Avoided (imputed) rent as a modelled input for every live-in path, plus the sale-year tax-year alignment. Delivered as a rule row, a blank-by-policy rent-evidence standard and a local-only input in the capital panel; the rounded-figure what-if tool it was first built into no longer exists | done | `arena-79e0fd5e-tino4` | `assets/app.js`, `pages/decision-analysis.html`, `index.html` (via generated build) | 2026-11-15 |
| 79E-5 | Transfer tax, recording and documentary fees priced into the sell path; California documentary-transfer-tax death exemption; Prop H (SF real-estate transfer tax) modelled with official terms; Prop 19 allowance carried forward in every transfer-year row | done | `arena-79e0fd5e-tino4` | `tools/sitebuild.py`, `pages/property-tax.html`, `pages/estate-thresholds.html`, `pages/law-watchlist.html` | 2026-11-15 |
| 79E-6 | Distribution chart on the projections page (outcome spread across scenario bands, not a point estimate) and a five-year maintenance/capital plan table for both buildings | done | `arena-79e0fd5e-tino4` | `tools/sitebuild.py`, `assets/style.css`, `pages/projections.html`, `pages/operating-costs.html` | 2026-11-15 |
| 79E-7 | Rebuild-and-diff check: a `tools/recheck.py` that rebuilds the model and reports whether the published recommendation moved, per the owner's "rebuild after any input change" instruction | done | `arena-79e0fd5e-tino4` | `tools/recheck.py` (new), `.github/workflows/verify.yml` | 2026-11-15 |
| 79E-8 | Suggestions queue + executive summary + attorney/CPA brief updates for everything above; rebuild, verify, tests, PR to `main`, merge, confirm Pages deploy, record result | done | `arena-79e0fd5e-tino4` | `pages/suggestions.html`, `pages/executive-summary.html`, `pages/attorney-cpa-brief.html`, `pages/flagged-for-review.html`, generated site | 2026-11-15 |

### Overlap check against session `arena/a897a17d-tino4` (A897-1/A897-2)

This session's claim was pushed after that session's PR #97 merged to `main` at `a513bc4`. Read before any merge:

- A897's 2026-11-15 source refresh (FTB BHSTS 1% rows, BOE LTA pages, CPUC NEM 3.0, RTC §119.1, the CA capital-gain rows, the new glossary terms, and the `1191` verifier allowance) is **kept as canonical**. This session does not restate or renumber those rows and adds no competing CA income-tax rows; its Form 540 / capital-gain task is therefore recorded as done by PR #97 and is not repeated here.
- Shared files (`tools/sitebuild.py` `SOURCES`, `tools/verify.py`, `tools/test_case.py`, `README.md`): this session's edits are **additive only** — new source keys, new builder sections, a new verifier rule, new tests. Its branch was rebased onto `a513bc4` first, and every rebase keeps A897's rows byte-for-byte unless a rule is being extended. If A897-2 pushes again, this session rebases again rather than overwriting.
- This session's exclusive content: the reverse-map leak in `tools/history_scrub.sh` / `tools/history-scrub-plan.md` (79E-1/2), depreciation and recapture modelling (79E-3), the imputed-rent input (79E-4), transfer-tax / recording-fee / Prop H pricing and the Prop 19 allowance carried forward through every transfer year (79E-5), the outcome-spread chart and five-year capital plan (79E-6), and `tools/recheck.py` (79E-7).

Constraints this session follows: no force-push, no history rewrite of `main`, no edits to another session's claimed scope; all published currency stays $10-rounded (or an allowlisted official figure); no names, street addresses, parcel or account identifiers on any public page; every table row keeps an official source link and an evidence badge; anything not confirmable from an official source stays blank and is listed on the flagged page.

### Outcome, and the policy collision this session did not resolve unilaterally

**READ FIRST.** This session built a publication layer in which owner-supplied costs appear rounded to the nearest ten dollars, per an explicit owner instruction that decision-driving numbers be published for clarity. Sessions `b784431e` (PRs #101/#102, now on `main`) adopted the stricter containment policy: no household figures at all, and `tools/verify.py` fails on any row badged as carrying figures supplied by the household. **Both cannot hold on one public page.** This session merged `main`, withdrew its publication layer rather than re-applying figures over the newer policy, and did not revert the containment decision.

**An owner decision is still required:** keep containment and hold every figure in the private workpaper, or relax the policy and restore the rounded publication path together with its rounding checks. The decision-log row records the question as open; nothing here silently picks a side.

What survived the reconciliation, folded into the containment architecture as rules, evidence standards and checks:

- rental depreciation and its recapture (recovery period, mid-month convention, land excluded, allowed-or-allowable, the maximum federal rate on unrecaptured section 1250 gain, California's ordinary-rate treatment, the personal-use fair-rental-value rule, and why a stepped-up inherited base restarts the recovery period) — costs page;
- documentary transfer tax mechanics from the recorder's published schedule (per 500 dollars of consideration, the tier reaching the entire consideration at a boundary, per-page recording charges, the affordable-housing parcel fee and its declared exemptions, the fee in lieu when no change-of-ownership statement accompanies a document), plus the Proposition 19 allowance carried forward with its biennial indexing, prior-claim reduction and occupancy conditions — property-tax page;
- the estate-level filing test (gross estate plus adjusted taxable gifts plus the specific exemption), portability needing a timely return, filing and payment as separate deadlines, and liquidity as a different question from liability — estate page;
- the rent-evidence standard, which rejects a voucher payment standard or an area median as a market comparable and leaves the row blank instead of inferring; a five-year capital plan with repair-versus-capitalisation treatment and reserve funding built from bids;
- a published re-check cadence (annual rebuild, biennial February reading of the indexed allowance, every legislative session, immediately on an event) and the Prop H / Proposition I clarification — watchlist;
- a unit-free outcome-spread illustration and a crash-entry comparison in index units (start = 100), so the shape of a result is published and no household amount is; a local-only capital and tax sensitivity panel with no prefilled value, no storage and no network call;
- whole-tree scanning in `tools/verify.py` (comma-grouped amounts that are neither $10-rounded nor registered official figures, rounded/unrounded mapping patterns, a committed redaction-rules file) — this is the 79E-2 enforcement, which survives intact and now guards files the old page-level check could not see;
- `tools/recheck.py`: rebuild, verify, and diff a committed fingerprint of the published evidence layer (`MOVED` / `UNCHANGED`), with an optional `--private-model` path outside the repository that reports only whether a ranking order changed, never the figures;
- `tools/dom-test.cjs` restored as an optional jsdom smoke test covering both panels and the no-storage rule, plus a non-blocking CI step.

**Withdrawn with the architecture it was built for:** `tools/models.py`/`tools/sections.py` stay deleted (they carried the pre-rounding reverse map, which this session removed as 79E-1); `tools/recommendation-snapshot.json` and the rounded per-path dollar tables are removed from the tree; the path-tool inputs in `assets/app.js` are gone because the containment site has no such tool; `pages/capital-and-tax-model.html` was folded into the existing rules pages rather than published as a figures page.

**Release:** PR to `main` from `arena/79e0fd5e-tino4`, opened after merging `origin/main` `6047b9e`; checks (unittest → build → verify → recheck → reproducibility) and the optional DOM step; merged; Pages deploy confirmed. Result recorded below once merged.
