# COORDINATION.md — Shared Task Board

## Current session: privacy-first public site remediation

- Branch: `arena/e1ea4bef-tino4` (platform-fixed; no alternate branch/worktree was created).
- Status: completed in this branch; publication/history cleanup still requires repository-owner coordination.
- Scope: `_7adb71fc/sitebuild.py`, `tools/build.py`, `tools/verify.py`, `tools/test_case.py`, generated public `index.html`, `pages/**`, `assets/style.css`, and removal of the public case projection CSV.
- Work: replaced personalized public pages with generic guidance, added an attorney/CPA printable brief, missing-information checklist, reviewable suggestions, privacy limitations and flagged-review information. The public build no longer imports or reads household case inputs and emits no projections.
- Verification: `python3 tools/build.py`, `python3 tools/verify.py`, and `python3 -m unittest discover -s tools -p 'test_*.py' -v` pass. The verifier scans every public HTML file for case identifiers and case-like figures and confirms the projection CSV is absent.
- Important limitation: the current public Git tree contains historical coordination and research material that may include case-derived details, and prior Git objects, PRs, forks, caches, and clones cannot be removed by this site change. The checkout is shallow and this session did not rewrite remote history or force-push. A repository-owner-coordinated history cleanup is still required; review repository visibility and preserve a secure private archive before any rewrite.
- Official primary-source links are referenced in the private research records, but this generic site makes no household-specific legal or financial conclusion. Re-verify all law and deadlines at the future transfer date with counsel and the relevant agencies.
