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

## Session `arena-38a4359d` — privacy-safe generic decision tools (2026-11-14)

Branch remains platform-fixed at `arena/38a4359d-tino4`; base includes merged privacy remediation PR #58 and follow-up PR #59. The public pages must remain generic: no household-specific values, rents, histories, property locations or personalized recommendation.

| Task | Status | Owner | Scope |
| --- | --- | --- | --- |
| A38-P1 | in progress — add normalized, local-only Treasury-phasing stress controls; generic black-swan page; categorized navigation; executive summary, timeline, questions, glossary and suggestion review | `arena-38a4359d` | `_7adb71fc/sitebuild.py`, `assets/app.js`, `assets/style.css`, `pages/**`, `README.md` |
| A38-P2 | in progress — strengthen public-output privacy verification; remove obsolete current-tree household input/output modules no longer used by the generic build | `arena-38a4359d` | `tools/**`, `.gitignore`, retired case modules only |
| A38-P3 | in progress — record source checks, verification, PR/deploy result and residual history risk | `arena-38a4359d` | `COORDINATION.md` (this section only) |

Prior main history cannot be erased by this follow-up; the existing privacy page and Flagged for Review disclose that. This claim does not authorize a force-push or change to repository visibility.
