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

---

## Session `arena-09b3438c` — owner brief follow-up: privacy remediation (current tree), deadline timeline, integration (2026-11-14)

Branch is platform-fixed at `arena/09b3438c-tino4` (base `main` @ `448f733`). Remote branches at claim time: `main` only, so no other session is active on a feature branch.

| Task ID | Task | Status | Owner | File scope (exclusive) | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| B09-1 | Current-tree privacy remediation: replace ZIP codes, city and neighbourhood names in logs and audit notes with placeholders (`[ZIP-A]`, `[ZIP-B]`, `[city-A]`); keep detector regexes in code | done | `arena-09b3438c` | `COORDINATION.md` (ZIP/city text only, and this section), `_s95cf9249/audit/AUDIT_REPORT.md` | 2026-11-14 |
| B09-2 | Visual deadline timeline on the inheritance step-by-step page, built from the existing sourced rows (no new facts) | done | `arena-09b3438c` | `_7adb71fc/sitebuild.py` (new `pages/deadline-timeline.html`, timeline CSS, one flagged item), generated `pages/**`, `index.html`, `assets/style.css` | 2026-11-14 |
| B09-3 | Rebuild, verify, test, PR to `main`, merge, confirm Pages deploy, record result here | done | `arena-09b3438c` | generated `pages/**`, `index.html`, `assets/**`, this section | 2026-11-14 |

### Log (`arena-09b3438c`)

- 2026-11-14 — Full history fetched read-only (`git fetch --unshallow`; 194 commits). **Finding, not remediable from this branch:** the exact, unrounded owner tax and assessment figures, ZIP codes and the city name appear in earlier commits on `main` (e.g. first added in the 2026-11-10 to 2026-11-12 sessions). The current tree contains no raw figures. A history rewrite requires a force-push to `main` and an owner or admin decision; this session is limited to pushing its own branch, so it did **not** rewrite history. Recommended owner action: decide whether to rewrite history (`git filter-repo` plus force-push, then ask GitHub to purge cached views) or make the repository private, and rotate nothing else since no credentials were found in the tree.

- 2026-11-14 — Merged `origin/main` @ `c3a9999` (PR #58, session `arena-e1ea4bef`) into this branch, which removed the household case pages and CSV from the public site. This session **kept that privacy-safe baseline** and did not reintroduce case figures. Its COORDINATION.md was adopted; this section was re-appended.
- 2026-11-14 — Current-tree privacy scan (`git grep` on HEAD): no raw owner figures and no ZIP codes outside detector patterns in code (`_7adb71fc/verify.py`, `tools/verify.py`, `tools/test_case.py`, `_s95cf9249/audit/check.py`) and one audit-report line. The audit line is redacted to `[ZIP-A]`/`[ZIP-B]`/`[city-A]`. Detector patterns are kept on purpose.
- 2026-11-14 — Added `pages/deadline-timeline.html`: Day 0 date of death; 60-day trustee notice; 150-day change-in-ownership statement; 9-month Form 706 due date and payment; 1-year principal-residence condition; 60-day appeal window; December 10 / April 10 installments. Navigation and index link come from the generator.
- **Sources read on 2026-11-14 (official):** California Probate Code 16061.7 (60-day notice, subd. (f)): https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum=16061.7 ; Revenue and Taxation Code 480 (150 days for death-transfer statement, subd. (e)): https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=480 ; BOE Information Sheet 800-9 (150 days, one-year residence condition, appeal 60 days, December 10 / April 10 delinquency dates, 10% penalty): https://www.boe.ca.gov/pdf/pub800-9.pdf ; IRS Instructions for Form 706 (Rev. July 2026) (9-month due date and payment, Form 4768 6-month extension, 2026 basic exclusion $15,000,000): https://www.irs.gov/pub/irs-pdf/i706.pdf
- **Irregularities (on Flagged for Review):** (1) the BOE FAQ URL `boe.ca.gov/proptaxes/faqs/ownerocc.htm` returned 404 and was not used; (2) the three-year BOE-19-P claim window appears only in a county-hosted copy of the form, not in the official BOE sheet read, so it is not on the timeline and is flagged; (3) the 2026 $15,000,000 threshold applies to 2026 deaths only; the threshold for the actual transfer year is unknown; (4) the **full Git history still contains** the owner's exact figures, ZIP codes and city name (194 commits, checked with `git fetch --unshallow`). A history rewrite needs repository-owner action and was **not** performed by this session.
- **Checks:** `python3 tools/build.py` passed (reproducible); `python3 tools/verify.py` passed (9 public HTML files; privacy checks OK; no case projection file); `python3 -m unittest discover -s tools -p 'test_*.py'` passed (36 tests). Browser smoke test not run (no browser installed in this checkout).
