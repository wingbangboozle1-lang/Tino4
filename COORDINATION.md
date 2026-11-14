# COORDINATION.md — Shared Task Board

## Current session: privacy-first public site remediation

- Branch: `arena/e1ea4bef-tino4` (platform-fixed; no alternate branch/worktree was created).
- Status: completed in this branch; publication/history cleanup still requires repository-owner coordination.
- Scope: `_7adb71fc/sitebuild.py`, `tools/build.py`, `tools/verify.py`, `tools/test_case.py`, generated public `index.html`, `pages/**`, `assets/style.css`, and removal of the public case projection CSV.
- Work: replaced personalized public pages with generic guidance, added an attorney/CPA printable brief, missing-information checklist, reviewable suggestions, privacy limitations and flagged-review information. The public build no longer imports or reads household case inputs and emits no projections.
- Verification: `python3 tools/build.py`, `python3 tools/verify.py`, and `python3 -m unittest discover -s tools -p 'test_*.py' -v` pass. The verifier scans every public HTML file for case identifiers and case-like figures and confirms the projection CSV is absent.
- Important limitation: the current public Git tree contains historical coordination and research material that may include case-derived details, and prior Git objects, PRs, forks, caches, and clones cannot be removed by this site change. The checkout is shallow and this session did not rewrite remote history or force-push. A repository-owner-coordinated history cleanup is still required; review repository visibility and preserve a secure private archive before any rewrite.
- Official primary-source links are referenced in the private research records, but this generic site makes no household-specific legal or financial conclusion. Re-verify all law and deadlines at the future transfer date with counsel and the relevant agencies.

---

## Session `arena-e428aa88` — privacy-first repository and release audit (2026-11-14)

Branch is platform-fixed at `arena/e428aa88-tino4`; no branch/worktree creation. Read the task board through the latest privacy-first remediation record. This session continues the owner-requested audit and final release verification on the current branch only.

| Task ID | Task | Status | Owner | File scope (exclusive) | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| E428-1 | Audit the published site and current tracked tree for privacy exposure; add enforceable release checks; remediate what is safe on the pinned branch and explicitly preserve any unresolved history/admin limitation | in progress | `arena-e428aa88` | `COORDINATION.md` (this section only), `README.md`, `_7adb71fc/**`, `_7eff7e24/**`, `assets/**`, `index.html`, `pages/**`, `tools/**`, `.github/workflows/verify.yml` | 2026-11-14 |
| E428-2 | Rebuild, run tests and source/privacy/link checks; PR current branch to `main`, merge only if checks pass, verify Pages deploy and record result | in progress | `arena-e428aa88` | `COORDINATION.md` (this section only), release verification | 2026-11-14 |

### Claim/rebase conflict log

- While committing this claim, `origin/main` advanced from the initial base (`448f733`) to `bea5d88`, integrating privacy-remediation PR #58 and follow-up PR #59. The claim-only rebase conflicted because the incoming session replaced the historical board with a concise privacy-first status record. Resolution preserves the entire incoming board and tree, then appends this claim; no incoming work was discarded. The session continues from the updated `main` state.

Pre-rounding history remediation is not presumed complete. The audit will inspect the updated public tree and available Git history, enforce checks against accidental publication, and clearly flag any historic exposure that cannot be removed safely from this pinned branch.
