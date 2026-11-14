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

## Session `arena-f1a0a0df` — follow-up audit (2026-11-14)

The platform-fixed branch is `arena/f1a0a0df-tino4`. This task was narrowed after `main` advanced during the initial claim push: PRs #58 and #59 already introduced and corrected the generic, privacy-first public site. No site generator or generated page is edited by this session unless a specific defect is found and ownership is re-checked.

| Task ID | Task | Status | Owner | File scope (exclusive) | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| F1A-1 | Independently audit the merged privacy-safe site, reproducible build, verifier, source-link coverage, and whether repository-history exposure can be remediated from this pinned branch; publish a factual audit result | in progress | `arena-f1a0a0df` | `COORDINATION.md` (audit log only; no site files) | 2026-11-14 |

### Log (`arena-f1a0a0df`)

- 2026-11-14 — `git pull --rebase origin main` found that `main` had advanced to PR #59. The rebase conflicted only in `COORDINATION.md`, where the incoming privacy-remediation session had deliberately replaced the old board (which contained case-derived details) with a short sanitized record. Resolved by retaining the incoming sanitized file verbatim and narrowing this claim to a read-only audit. No content from the older, more revealing board was restored; no other session's work was discarded.
