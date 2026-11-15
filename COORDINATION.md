# COORDINATION.md — Privacy-safe task board

## Session `arena/b784431e` — public-site privacy containment

Branch: `arena/b784431e-tino4` (platform-fixed; rebased onto the latest `origin/main`). Status: active.

| Task ID | Task | Status | Owner | File scope | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| B784-1 | Remove household-specific locations, values, assessment histories, rents and derived recommendations from the public site and active source tree; preserve generic decision guidance and official rules; add fail-closed privacy checks | done | `arena/b784431e` | `tools/sitebuild.py`, `tools/models.py`, `tools/sections.py`, `tools/verify.py`, `tools/test_case.py`, `tools/site-manifest.json`, `assets/app.js`, `assets/style.css`, `.gitignore`, generated `index.html`, `pages/**`, `README.md`, `COORDINATION.md`, history-remediation notes | 2026-11-15 |
| B784-2 | Rebuild, inspect privacy and source coverage, run automated tests, and prepare current-branch PR / deployment verification | in progress | `arena/b784431e` | release checks and `COORDINATION.md` | 2026-11-15 |

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

### B784-2 release record

Release checks are underway. Record PR, checks, merge and Pages deployment here only after they are confirmed. Do not record household-specific details or identifiers.

## Prior work

Earlier sessions built a household-specific model and identified historical exposure. This current tree is being generalized; prior public history is not represented as scrubbed. No old values or place identifiers are repeated in this board.
