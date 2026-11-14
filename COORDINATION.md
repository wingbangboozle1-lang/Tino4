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
- 2026-11-14 — PR #60 (https://github.com/wingbangboozle1-lang/Tino4/pull/60) merged to `main` as `4a29086bd46b849e7799ee373bd10102574f5015`. Verify run 43646927347 passed; Pages deployment run 43646956696 completed successfully and the Pages API reported `built`, `error: null`. Cache-busted live checks returned the generic decision workspace, phased-investing framework, and attorney/CPA brief. A normal cached fetch initially showed the previous artifact; the cache-busted response confirmed the new deployment. Repository/history remediation remains open and is not claimed complete.

| 2C2D-3 | Make the public Privacy and Flagged for Review pages explicit that excluded legacy source files can still be read in a public GitHub repository; add privacy wording regression test | done — current source-data removal remains needs review | `arena-2c2d483d` | `_7adb71fc/sitebuild.py`, `tools/test_case.py`, generated privacy/review pages, this subsection only |
| 2C2D-4 | Correct stale README claims about case-specific pages, CSV, model, browser controls, and CSP; document the current generic site and unresolved public-repository source exposure | done | `arena-2c2d483d` | `README.md`, this subsection only |

- 2026-11-14 — README now reflects the privacy-safe generic Pages site, no case-projection CSV, no interactive personal calculator, and the public-repository/history limitation. Build and verifier passed (9 public HTML files; no case CSV); 1 test passed; `git diff --check` passed. No case-specific figures or identifiers were added.

- 2026-11-14 — clarified on the public Privacy and Flagged for Review pages that excluded legacy source/model files can remain publicly readable from GitHub even when not built into Pages; added regression assertions. `python3 tools/build.py`, `python3 tools/verify.py` (9 HTML files; no case projection CSV), one unit test, and `git diff --check` passed. These warnings do not remove the current legacy inputs or history; the report keeps that remediation open. No new personal data or property-specific figures were added.

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

---

## Session `arena-bab50453` — overlap check and yield (2026-11-14)

The pinned checkout initially started from `0112ebb9`, while `origin/main` advanced during this session. After fetching `origin/main` at `55c3e041`, I confirmed the phased-investing framework and anonymized attorney/CPA sheet, along with the timeline/glossary/review pages, had already landed through the concurrent integration PRs. To avoid duplicate features and, more importantly, avoid restoring household-specific generated projections onto the newly privacy-remediated public site, I yielded the overlapping tasks and synchronized this branch to `origin/main`. No work from the earlier local draft was published or pushed.

- **BAB-1 phased-investing / black-swan:** yielded; the generic public phased-investing page is already in the synchronized main tree.
- **BAB-2 printable professional briefing sheet:** yielded; the generic placeholder-free printable page is already in the synchronized main tree.
- **BAB-3 review:** existing main verification/deployment records cover the integrated site. Repository-history cleanup remains unresolved as recorded by the privacy remediation session; no force-push or destructive rewrite was attempted.
- **Verification on the synchronized tree:** see the current main workflow and the logged PR #62 deployment record. No separate branch feature PR was opened because the requested pages already exist on main.

## Session `arena-3d54dd27` — yield of ZIP-redaction claim and owner-blocker status (2026-11-14)

| Task ID | Task | Status | Owner | File scope |
| --- | --- | --- | --- | --- |
| 3D54-1 | Remove literal ZIP codes from repo audit, test and verifier files | yielded to `arena-09b3438c` (B09-1 already claimed these files and kept detector regexes in code). PR #67 closed without merge; commit `0c1d4af` kept on the branch for reference only | `arena-3d54dd27` | none on main |
| 3D54-2 | Owner decision: publish household analysis on `main` or keep generic site | open; needs owner decision. Not implemented. | `arena-3d54dd27` | none |

- Log: the household-analysis additions (anchored 1929/2008 phased test, mixed-path engine, browser what-if page) are kept as untracked internal drafts and are not published. The what-if port matches the Python engine (parity test passes) but is not on the site.
- Log: the open ZIP-in-code detector question and the raw owner figures in `_7eff7e24/content.py` are for the owner (F01). Not changed here.
- Log: `_s95cf9249/audit/check.py` reads `assets/synthetic-projections.csv`, which is not on main, so it fails on main independently of any redaction.
- **Verification on the synchronized tree:** the current main workflow and Pages deployment were checked; the requested pages already existed on main, so no feature code was duplicated. A coordination-only PR was opened to record this handoff.

### Integration / deployment record for `arena-bab50453`

- PR #64 (coordination-only): https://github.com/wingbangboozle1-lang/Tino4/pull/64 — merged 2026-11-14 22:18:23 UTC as `4557ef23e2c65c13085dfddfdc668e19a64ca4be`. The PR verification run 43647357616 passed. Its first Pages run was cancelled because a higher-priority deployment was queued; this was not a build failure.
- Subsequent current-main verification run 43647411822 passed. Pages deployment run 43647411127 succeeded for commit `37c05db22fb8c71843e6746958aaeca7973ec386` (after concurrent PR #65); Pages API status is `built` at https://wingbangboozle1-lang.github.io/Tino4/.
- Live page fetch checks: `/pages/phased-investing.html` serves the Treasury staging model with local what-if controls and risk disclosures; `/pages/attorney-cpa-brief.html` serves the printable adviser handout and sourced statutory references.

- 2026-11-14 — PR #66 (coordination-only deployment record): https://github.com/wingbangboozle1-lang/Tino4/pull/66 merged as `f6babe769daf0746faaa31fe222cdc19f26c0149` at 22:20:33 UTC. PR verification run 43647550264 passed. The first post-merge Pages run was canceled as a higher-priority Pages deployment entered the queue; the next queued Pages run 43647671712 completed successfully for concurrent main commit `9d0b7bfa3629907c31be392ed528ed72073d61cb`. GitHub Pages API reports `built`; live checks for the phased-investing and Attorney & CPA brief pages passed.
- 2026-11-14 — PR #70 (coordination-only): https://github.com/wingbangboozle1-lang/Tino4/pull/70 merged as `d63630460d23080e9a470162a3f313c04037ad5d` at 22:22:58 UTC; PR verification run 43647770324 passed. The first queued Pages jobs were superseded by higher-priority runs; final Pages deployment run 43647804186 succeeded, GitHub Pages API reports `built`, and the two relevant live pages were fetched successfully.

---

## Session `arena-d10d2c46` — household analysis hold, flags and integration handoff (2026-11-14)

Branch: `arena/d10d2c46-tino4` (platform-fixed). Base: `main` @ `d636304`. Claimed: 2026-11-14 22:24 UTC.

Process note: household-analysis edits to the internal engine and generator were made on this branch before this claim was written. They are **not** committed or pushed; they are held in the local stash `d10d2c46 household analysis drafts (INTERNAL...)`. The branch was then reset to `origin/main`. The two local merge commits from the earlier PR #57 import were redundant, because `448f733` is an ancestor of `main`.

| Task ID | Task | Status | Owner | File scope (exclusive) | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| D10-1 | Household analysis (sell / rent / live / mixed paths, break-evens, what-if, deadline timeline) with corrected internal engine | held: not published, pending owner decision `3D54-2` | `arena-d10d2c46` | none on `main`; drafts remain in the local stash | 2026-11-14 22:24 UTC |
| D10-2 | Record the hold, generic Flagged-for-Review items, and integration requests; no shared output edited | in progress | `arena-d10d2c46` | `COORDINATION.md` (this section only) | 2026-11-14 22:24 UTC |

### Log (`arena-d10d2c46`)

- **Decision (held, not published).** Household analysis is not published on `main`. `main` is deliberately generic after PR #58/#59, and publishing household projections is open owner decision `3D54-2`. Nothing household-specific is committed in this session. Internal work is held in a local stash on this branch, `d10d2c46 household analysis drafts (INTERNAL...)`, and can be recovered with `git stash pop`. The stash is not pushed.
- **Branch reset.** The branch was reset to `origin/main`, discarding two local merge commits from the earlier PR #57 import. Those commits added nothing beyond `main`, because `448f733` is an ancestor of `main`.
- **Internal engine corrections (in the held stash; the legacy source on `main` still has the old formulas).** (1) The rental path used the value in the horizon year as the terminal basis, not the basis carried from transfer. This overstated the rental path by a material amount at a 2045 transfer. (2) The Prop 19 taxable value now follows BOE LTA 2026/026: the larger of the factored base year value and full value less the allowance. The earlier formula is removed. (3) The conversion-reassessment alternative is removed. (4) The allowance constant is rounded to $10 before use, so the calculation follows the rounding rule. The sell-at-transfer and rent-then-sell paths did not depend on (2) or (3).
- **Request to integration (generic Flagged-for-Review items, not yet on the page).**
  - (a) Allowance indexing: the BOE intro guide says the allowance is adjusted annually. The county page and the statute summary say every second February 16. Sources conflict.
  - (b) Post-move-out treatment: a county FAQ says the property is taxed at the factored base year value without reassessment. BOE LTA 2026/026 says the enrolled value is the full value at transfer, factored. Attorney/CPA question. The county page is not a `.gov` source and is not linked.
  - (c) Late homeowners-exemption claim: the county FAQ is silent. The BOE intro guide, citing Rule 462.520, says the exclusion starts in the claim year.
  - (d) Resolved in the engine: the conversion-reassessment alternative is removed; BOE LTA 2026/026 supports the factored full-value rule.
  - (e) Living paths exclude any value of housing and any avoided rent. Break-even thresholds are not estimates until the owner supplies or declines that input.
  - (f) Rent yield and stock return are invented planning parameters. The break-evens are sensitivities, not forecasts.
  - (g) The IRC 121 exclusion uses the single-filer amount until the filing status is known. Whether the heir may count the decedent's ownership and use periods is unchecked.
  - (h) The growth windows in the what-if design come from a stored FHFA copy that has not been re-fetched.
  - (i) The one-page attorney and CPA sheet has not been printed or page-counted; no browser is available here.
  - (j) Verbatim statutory quotations: the owner's $10 rounding rule may conflict with exact figures in quotes. Owner decision.
  - (k) Unrounded owner figures remain in Git history (F01/F02). Already on the board; referenced, not re-logged.
  - (l) Mixed paths, break-evens, and deadline sequencing have not been reviewed by an adviser.
- **Owner decisions needed.** (1) Confirm `3D54-2`: publish household analysis, or keep the generic site. (2) Decide whether the legacy engine formulas in `_7eff7e24/` should be corrected in the repository (code only, no figures). (3) Decide item (j).
- **Verification.** On `origin/main` `d636304`, `python3 tools/build.py` reproduced the published tree with no diff. `python3 tools/verify.py` passed (9 public HTML files, privacy checks OK). `python3 -m unittest discover -s tools -p 'test_*.py'` passed (1 test). No browser was run.
- **Conflict.** At push time `main` advanced (PR #72). `COORDINATION.md` conflicted. Resolved by keeping `main`'s text byte-for-byte and appending this section. No other session's entry was altered.
