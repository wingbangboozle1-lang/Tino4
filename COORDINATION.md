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

## Session `arena-2c2d483d` — privacy boundary follow-up (2026-11-14)

| Task ID | Task | Status | Owner | File scope |
| --- | --- | --- | --- | --- |
| 2C2D-1 | Phased-investment black-swan scenario | yielded to `arena-38a4359d` (A38 feature landed in PR #57; no duplicate files edited) | `arena-2c2d483d` | none |
| 2C2D-2 | Independent privacy boundary review; document current-tree exposure and safe remediation limits | done — repository/history cleanup remains needs review | `arena-2c2d483d` | `_2c2d483d/privacy-review.md`, this subsection only |

### Log (`arena-2c2d483d`)

- 2026-11-14 — while rebasing the claim before work began, `origin/main` advanced to feature and privacy follow-up commits. Preserved those changes and yielded the overlapping feature claim. This session did not edit those files. The current public pages are now generic after PR #58/#59; the public repository still contains legacy case-specific input/model source and historical Git refs may retain older details. The audit and current state are documented in `_2c2d483d/privacy-review.md`. No history rewrite or force-push was attempted from this pinned shallow branch.
