# COORDINATION.md — privacy-safe task board

## Session `arena/6e0ed674` — privacy containment and main integration

Branch: `arena/6e0ed674-tino4` (platform-fixed; active).

| Task ID | Task | Status | Owner | File scope |
| --- | --- | --- | --- | --- |
| 6E0E-1 | Remove household-specific figures from the active public build and integrate the privacy-first site with current main | rebased and locally verified; PR #140 updated, CI pending | `arena/6e0ed674` | public builder, verifier, scanner/tests, generated site, README, coordination board |

- Removed the household case model and derived outputs; retained the inherited trust transfer versus already-owned rental asset distinction generically. No personal identifiers or assessment-derived values are published. Kept source-linked Form 540 line 62 and California additional 1% guidance.
- Rebase conflict resolution uses the latest `origin/main` privacy-first builder, verifier, identifier scanner, and source/test updates; the removed `tools/case_model.py` remains absent. Main's current 26-page build and coordination updates are preserved. The chart-smoke script from the rebased patch targeted an asset removed by current main, so it was not carried forward.
- Final verification after resolving against current `main`: `python3 tools/build.py` and `python3 tools/verify.py` passed (26 generic pages); 14 Python tests passed; syntax checks passed for `assets/app.js`, `assets/phase-model.js`, and `assets/regime-model.js`; `git diff --check` passed; `python3 tools/recheck.py --update` refreshed the framework snapshot. A separate nine-scenario chart smoke test passed against the earlier resolved privacy builder, but is not claimed for the final current-main chart code.
- PR #140 was updated on the current branch against current `main`. The latest GitHub query (2026-11-19) reported no checks and unknown mergeability; recheck both before any merge. No CI pass is claimed.
- Historical exposure remains unresolved. This clone is shallow; no history rewrite, external-copy cleanup, deployment, or merge is claimed.


## Current session `arena/4e566e41`

Branch: `arena/4e566e41-tino4` (platform-fixed; active).

| Task ID | Task | Status | Owner | File scope |
| --- | --- | --- | --- | --- |
| 4E56-1 | Remove household-derived inputs and outputs from the public build; retain a generic source-linked guide | done | `arena/4e566e41` | `tools/sitebuild.py`, `tools/verify.py`, `tools/test_*.py`, generated site, `assets/**`, `README.md`, `COORDINATION.md` |
| 4E56-2 | Assess historical privacy exposure and record administrator-only remediation requirements | needs review | repository administrator | Git refs, pull-request views, forks, caches, hosting-provider copies |

## 4E56-1 completion record

- Removed the build-time household model and its private-derived outputs, and removed a client-side distribution routine that contained household-derived amounts. The public pages now contain generic decision guidance, official-source summaries, blank evidence gates and local-only what-if tools; no household inputs, recommendations or projections are built.
- Kept the inherited-versus-already-owned distinction as a generic planning rule, without publishing property identifiers or case amounts. The ambiguous local shorthand remains unresolved and no locality-specific measure is mapped or applied.
- Preserved the first-screen “What would change the answer?” table, the 26-page menu, suggestions/review controls, printable attorney/CPA brief, deadline and glossary pages, black-swan context and 24–36 month Treasury-staging sensitivity.
- Replaced the history scanner's encoded household patterns with a generic direct-identifier scan. It does not establish that earlier sensitive material is erased.
- **Verification:** `python3 tools/build.py`, `python3 tools/verify.py`, `python3 -m unittest discover -s tools -p 'test_*.py' -v`, JavaScript syntax checks and `git diff --check` pass. The verifier confirms every data row has an official-source link and evidence label, and pages contain no browser storage, remote resources or network calls.
- **Source for history-remediation limits:** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
- **Irregularity:** current checkout is shallow and contains only the base commit; no history rewrite was attempted. This work cannot scrub prior Git objects, pull-request views, forks, caches or clones. Treat exposure as potentially retained until a repository administrator conducts and verifies remediation.

## Previously completed work carried forward from `main`

| Session | Work | Status | Scope |
| --- | --- | --- | --- |
| `arena/f1fa9937` | Official-source spot-check; generic scan precision and shallow-history limitations | done | `tools/sitebuild.py`, `tools/privacy_scan.py`, `tools/test_privacy_scan.py` |
| `arena/765022d5` | Prior integrated build, verification and Pages release checks | done | `tools/build.py`, `tools/verify.py`, `tools/recheck.py`, generated site |

The Form 540 source register carries the merged 2026-11-19 review of the complete 2025 California Personal Income Tax Booklet. No household-specific tax sensitivity is published.

## 4E56-2 status and limitation

A working-tree rebuild cannot remove earlier Git objects or guarantee removal of pull-request views, forks, caches, downloads or clones. A repository administrator must preserve an encrypted private archive, assess repository visibility and every affected ref, coordinate any history rewrite, and consult the hosting provider about retained copies. Do not force-push or claim that prior exposure is erased from this task branch. See `tools/history_scrub_runbook.md`.

## Coordination rules

- Work only on the platform-fixed branch for this session.
- Keep public content generic and source-linked; do not copy private workpapers into Git.
- Mark research verified only after checking the linked official source and recording its scope.
- Record handoffs, verification and unresolved issues here without including household facts.

## Concurrent main update during rebase

PR #139 advanced only the shared coordination board while this task was being rebased. The note is recorded here at a high level; it did not change the public-site or verification scope. This session retained its current board and sanitized site work without overwriting other product files.
