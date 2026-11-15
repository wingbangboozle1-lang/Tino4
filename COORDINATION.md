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
| E428-1 | Audit the published site and current tracked tree for privacy exposure; add enforceable release checks; remediate what is safe on the pinned branch and explicitly preserve any unresolved history/admin limitation | done | `arena-e428aa88` | `COORDINATION.md` (this section only), `README.md`, `_7adb71fc/**`, `_7eff7e24/**`, `_1775f697/review/**`, `_a3de132b/audit/**`, `_s8bb142d0/audit/**`, `_s95cf9249/audit/**`, `assets/**`, `index.html`, `pages/**`, `tools/**`, `.github/workflows/verify.yml` | 2026-11-14 |
| E428-2 | Rebuild, run tests and source/privacy/link checks; PR current branch to `main`, merge only if checks pass, verify Pages deploy and record result | done | `arena-e428aa88` | `COORDINATION.md` (this section only), release verification | 2026-11-14 |

### Claim/rebase conflict log

- While committing this claim, `origin/main` advanced from the initial base (`448f733`) to `bea5d88`, integrating privacy-remediation PR #58 and follow-up PR #59. The claim-only rebase conflicted because the incoming session replaced the historical board with a concise privacy-first status record. Resolution preserves the entire incoming board and tree, then appends this claim; no incoming work was discarded. The session continues from the updated `main` state.

Pre-rounding history remediation is not presumed complete. A safe current-tree pattern scan found case-derived source, financial and audit material under `_7adb71fc/`, `_7eff7e24/`, `_1775f697/review/`, `_a3de132b/audit/`, `_s8bb142d0/audit/`, and `_s95cf9249/audit/`; output was limited to paths and match counts, with no matched values printed. E428-1's exclusive scope is expanded above to cover those artifacts for current-tree cleanup. The current E428 worktree removes the identified case-input, projection, and audit material from the branch tree and moves the generic builder into `tools/`; the legacy files remain in Git history. A read-only GitHub check confirmed repository-admin permission and public Pages status, but an attempted visibility restriction was rejected with HTTP 403 (`Resource not accessible by integration`), so the repository remains public. No history rewrite or force-push has occurred. The audit will preserve these unresolved exposure limits, enforce checks against accidental website publication, and flag historic material that cannot be removed safely from this pinned branch.

### E428 findings and verification (2026-11-14)

- **Current-tree privacy remediation:** removed the identified case-input, personalized page-source, projection, and audit files from this branch's current tree. The builder now reads no household inputs and emits 18 generic pages; no property-specific projection CSV is present. Main is unchanged until PR merge, so the public main tree still needs the planned cleanup merge.
- **Public-history finding:** the earlier safe pattern audit of `origin/main` covered 199 reachable commits; financial-data patterns matched 195 commits and 252 paths across the audited history. The corrected place-identifier scan matched 7 paths in both `HEAD` and `origin/main`. This is pattern presence, not a determination that every match is personal data; no matched values were printed. Public history, PR diffs, forks, caches and clones remain unresolved.
- **Repository access:** GitHub API confirms public visibility, default branch `main`, and legacy Pages status `built` at `https://wingbangboozle1-lang.github.io/Tino4/`. A visibility-restriction request failed with HTTP 403 `Resource not accessible by integration`; visibility did not change. Repository owner/admin follow-up is required to reconnect with repository-administration permission or change visibility, then coordinate history cleanup and GitHub Support as appropriate.
- **Build and checks:** after the final builder wording edits and branch sync, `python3 -m py_compile tools/*.py`, `python3 tools/build.py`, `python3 tools/verify.py`, `python3 -m unittest discover -s tools -p 'test_*.py' -v`, and `git diff --check` passed. Four unit/regression tests passed, including a check that the privacy pages distinguish current-tree cleanup from unresolved public Git history. The verifier checks all 18 pages, every table row's source and evidence badge, local-only resources, the manifest, retired current-tree artifacts, and generic address/postal/phone/email/currency patterns; it explicitly does not scan Git history.
- **Browser smoke test:** after branch sync and rebuild, using locally installed, ignored Playwright/Chromium test dependencies and extracted runtime libraries, `tools/browser-test.cjs` passed all 18 desktop and 18 mobile pages, suggestion save/reset, calculator controls, print layout, zero JavaScript errors, and no third-party requests. No screenshots or browser dependencies are tracked.
- **Sources / unresolved evidence:** official primary sources are linked in every data-table row and catalogued with scope and check date in `pages/sources.html`. Current IRS 2026/2027 amounts, Form 706 timing, California RTC §§63.2/13301/480 and Probate Code §16061.7, BOE Proposition 19/Publication 29, IRS rental/basis/1041 guidance, TreasuryDirect, Federal Reserve History, BLS, CBO, FHFA, HUD, CDI, CPUC and CSLB sources were reviewed. FTB inheritance, the BOE county-assessor directory, BOE Publication 801 and a CPUC water-utilities URL returned 404; each failure is labeled unverified. Property-specific values, local ordinances, leases, bills, insurance and repair quotes remain blank; no conditional winner is supported yet.
- **Branch sync / PR status (2026-11-14):** after PR #77 merged, `origin/main` advanced to `7f713e2` and GitHub reported PR #78 as conflicting. This branch merged that `main` tip without rewriting history. Conflicts were resolved in favor of this branch's generic 18-page builder and sanitized current tree; the stale legacy builder, audit artifacts, and older unmanifested deadline page were not reintroduced. The repository remains public and historical objects remain untouched.
- **Release result (re-checked 2026-11-15):** PR #78 (`https://github.com/wingbangboozle1-lang/Tino4/pull/78`) merged to `main` at `c9530a3de5207e86c1dd554f7067674bee1c8682` on 2026-11-14. GitHub Actions `verify` and `pages build and deployment` both completed successfully for that commit (runs `43650573824` and `43650573589`). GitHub Pages reports `built` at `https://wingbangboozle1-lang.github.io/Tino4/`; the repository remains public. Local revalidation on the current checkout: `python3 tools/build.py`, `python3 tools/verify.py`, `python3 -m unittest discover -s tools -p 'test_*.py' -v`, and `git diff --check` all pass; four tests pass, 18 pages are generated and structurally verified. This pass does not re-fetch each external source or independently repeat the recorded browser smoke test; see the source register and prior dated verification above. Do not describe public Git history as scrubbed. Repository-owner/admin access and supported history cleanup are still required, with copies, forks, PR diffs and caches treated as potentially exposed.

## Session `arena/fdd082b5-tino4` — feature enhancements and Pages release (2026-11-15)

Branch: `arena/fdd082b5-tino4` (platform-fixed; created from `main` at `c9530a3de5207e86c1dd554f7067674bee1c8682`). Status: active.

| Task ID | Task | Status | Owner | File scope (exclusive) | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| FDD-1 | Add explicit 3M–2Y Treasury 24–36 month staged-investing path to black-swan, with 1929/2008 crash-entry test and reinvestment risk beside headline | done | `arena/fdd082b5-tino4` | `tools/sitebuild.py`, `pages/black-swan.html`, `pages/phased-investing.html` | 2026-11-15 |
| FDD-2 | Add "no invented round numbers" principle to first screen and anonymized-placeholders row to privacy; keep all property-specific values blank | done | `arena/fdd082b5-tino4` | `tools/sitebuild.py`, `index.html`, `pages/privacy.html` | 2026-11-15 |
| FDD-3 | Rebuild, verify, and tests pass; commit built HTML so the committed site matches a fresh build; push the branch | done | `arena/fdd082b5-tino4` | `index.html`, `pages/*.html`, `tools/site-manifest.json` | 2026-11-15 |
| FDD-4 | Open PR `arena/fdd082b5-tino4` → `main`, merge after checks pass, confirm GitHub Pages deploy, record result | in progress | `arena/fdd082b5-tino4` | PR to `main`; Pages deploy | 2026-11-15 |

### Session notes

- **Privacy-first (highest urgency):** all public pages remain generic. No addresses, postal codes, valuations, rents, utility costs, or insurance premiums are published. The user's specific property data (Cupertino and San Francisco values, zips, rent, insurance) stays internal/placeholder-only and never appears on the website. `tools/verify.py` hard-rejects any currency amount other than the four IRS figures ($15,000,000 / $15,480,000 / $19,000 / $20,000) and any non-statute five-digit identifier in any tracked text file, including this board.
- **Rounding:** "round to the nearest ten dollars" applies only to private working copies and is labeled an assumption, never evidence. Public pages leave property-specific values blank (blank means unknown, not zero).
- **Pre-rounding Git history:** NOT scrubbed. The platform pins this branch; no force-push or history rewrite is performed, and `origin/main` remains public with historical objects intact. Owner/admin coordination is still required for any access restriction or supported history cleanup (see the existing E428 limitation in this board).
- **External source verification:** official sources were last fetched and recorded in the prior session record (2026-11-14). This session did not re-fetch them because sandbox outbound access is limited to github.com/api.github.com; re-verify law, thresholds, and costs at the actual transfer date.
- Features already present and retained: executive summary, mixed and pure paths, what-if Treasury-staging controls, reinvestment risk beside headline, "what would change the answer" on the first screen, deadline timeline, grouped navigation, glossary, one-page printable Attorney & CPA briefing sheet, suggestions review queue, questions/information/answer register, estate-tax thresholds, inheritance-process steps, black-swan economic conditions, and the official source register.

- **Release handoff:** PR #78 (`https://github.com/wingbangboozle1-lang/Tino4/pull/78`) is open. `gh pr checks 78` reported no checks on the branch, so there is no GitHub CI result and the PR has not been merged. The local build, verifier, unit/regression, diff, and browser results are recorded above. Do not describe the public history as scrubbed. Repository-owner/admin history cleanup is still required, and the access-control 403 must be resolved separately. After the PR is merged, verify the Pages build on `main` and append the deployment result here.
---

## Session `96b5208b` — inheritance decision site (2026-11-15)

- Branch: `arena/96b5208b-tino4`. The platform fixed this branch name and it cannot be renamed. The `session-<id>/<task>` convention is therefore not applied; this is logged here and no alternate branch was created.
- Task ID: IH-1 — extend the generic decision site (law watchlist rows for Nov 3, 2026 tax measures, Treasury bill terms, flagged-for-review rows), run build/tests/verify, open PR to `main`, merge, confirm Pages deploy, and record the result here.
- Status: in progress.
- File scope (exclusive to this session): `COORDINATION.md` (this section only), `pages/law-watchlist.html`, `pages/phased-investing.html`, `pages/flagged-for-review.html`, `pages/sources.html`, `tools/sitebuild.py`, `tools/site-manifest.json`, `index.html`, `README.md`.
- Constraints: no personal or property-specific figures on the public site; every table row keeps an official source link; unverified values are blank and flagged; no history rewrite or force-push.

### IH-1 status and findings (2026-11-15)

- **Scope change (logged):** `tools/verify.py` was touched to add four official host suffixes (`sf.gov`, `sftreasurer.org`, `santaclaracounty.gov`, `boj.or.jp`) used by new flagged-review source records. No other allowlist entry changed.
- **Added:** law-watchlist rows for Props 3 and 40–43 (official ballot titles, marked "Not verified" because the election (Nov 3, 2026) is before today and certified results were not read); SF Rent Board 1.6% row (verified against sf.gov); SF Rent Board 2026 notice row (not verified); flagged-review rows F-09 to F-15 for failed or conflicting retrievals (SF vacancy-tax path, Santa Clara rate, HUD FMR, Japan bubble, CA FTB brackets, SF coverage cutoff, measure outcomes).
- **Not added:** no dollar figures, property values, rents, or premiums were published. Property-specific calculations remain local-only.
- **Checks:** `python3 -m unittest discover -s tools -p 'test_*.py'` (4 tests), `python3 tools/build.py`, `python3 tools/verify.py` pass.
- **Branch sync note:** the first claim push was rebased onto `origin/main` at `7006c79` (PR #80). A stale earlier claim commit on this branch was replaced by a claim-only commit via `--force-with-lease` on this session's own branch; no other branch or `main` was modified.
- **Pending:** PR to `main`, merge result, and GitHub Pages deploy result will be recorded below after the merge.
- **Release result (2026-11-15):** IH-1 PR `https://github.com/wingbangboozle1-lang/Tino4/pull/81` merged to `main` at `a10c91b` (merge commit). `verify` (run after the identifier fix, `pass`) and `pages build and deployment` both completed with `success` for `a10c91b`. The live page `pages/flagged-for-review.html` shows the new F-09 to F-15 rows. Public-history exposure, the Santa Clara rate, HUD FMR values, Japan bubble figures, CA FTB brackets and Nov 3, 2026 certified results remain open and are flagged, not resolved.
---

### CC44 rebase conflict log (2026-11-15)

- `origin/main` advanced twice while this session worked: to `9ef9d48` (PR #79) and then to `993236f` (PRs #80, #81, #82 from sessions `arena/fdd082b5`, `arena/96b5208b`). This branch was rebased onto `origin/main`; the rebase conflicted in `COORDINATION.md` and `tools/sitebuild.py`.
- Resolution: the entire incoming board and all incoming site work are preserved (law-watchlist rows for the Nov 3, 2026 measures, the SF rent rows, flagged rows F-09 to F-15, the source records and the added host allowlist entries). This session's records are appended after them. No incoming work was discarded and no incoming row was renumbered; this session's new flags were relabelled F-16 to F-19 to avoid colliding with the existing F-09 to F-15.
- `tools/verify.py`: the incoming session added four official host suffixes; this session additionally allows the published statutory amounts `$7,000`, `$250,000`, `$500,000`, the CBO publication identifiers `61882` and `61270`, and documents each allowance in a comment. Nothing was removed from the incoming allowlist.

---

## Session `arena/cc44a347-tino4` — decision-content build, privacy and Pages deploy (2026-11-15)

Branch is platform-fixed at `arena/cc44a347-tino4`, branched from `main` at `c9530a3` and fast-forwarded locally to `origin/main` `9ef9d48` before any content edit. No other branch or worktree was created. This session claims the scopes below exclusively; it read the whole board first and found no active conflicting claim (PR #19 is a stale coordination PR from session `arena/ec965fac` dated 2026-11-11 and is left open, untouched).

| Task ID | Task | Status | Owner | File scope (exclusive) | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| CC44-1 | Claim record and board maintenance | done | `arena/cc44a347` | `COORDINATION.md` (this section only) | 2026-11-15 |
| CC44-2 | Black-swan regimes: real historical figures plus official CBO/HUD/FHFA baselines, replacing single-constant-growth framing; phased Treasury ladder with reinvestment risk and crash-during/crash-after entry | in progress | `arena/cc44a347` | `tools/sitebuild.py` (`SOURCES`, `build_black_swan`, `build_phased_investing`), `assets/app.js` (ladder panel only) | 2026-11-15 |
| CC44-3 | Ranges instead of round numbers, reinvestment risk beside the headline, "what would change the answer" first screen, mixed paths, deadlines timeline, grouped menu/glossary, executive summary, suggestions review queue | in progress | `arena/cc44a347` | `tools/sitebuild.py` (all builders except the ones in CC44-2), `assets/style.css`, `pages/**`, `index.html` | 2026-11-15 |
| CC44-4 | Privacy: pre-rounding range discipline, anonymised placeholders, history scan report, repository visibility handling, enforceable release checks | in progress | `arena/cc44a347` | `tools/verify.py`, `tools/test_case.py`, `tools/sitebuild.py` (`SOURCES`/privacy/flagged builders), `README.md`, `_config.yml` | 2026-11-15 |
| CC44-5 | One-page printable attorney & CPA briefing sheet | in progress | `arena/cc44a347` | `tools/sitebuild.py` (`build_brief`), `assets/style.css` (print rules only) | 2026-11-15 |
| CC44-6 | Integration and release: rebuild, verify, browser smoke test, PR to `main`, merge, confirm GitHub Pages deploy, record result | in progress | `arena/cc44a347` | `COORDINATION.md` (this section only) | 2026-11-15 |

Rules this session follows: sources are fetched directly and cited by scope; no case value, place identifier or household amount is added to the public tree; any fact that cannot be confirmed from an official source is left blank and listed on the "Flagged for review" page. This session is the only one editing the claimed files, so no cross-session handoff is required.

### CC44-4 findings so far — history and privacy (read before any history rewrite)

- The checkout was shallow. `git fetch --unshallow` was run read-only; the repository now has 251 reachable commits and `origin/main` moved from `c9530a3` to `9ef9d48` (PR #79). The branch was fast-forwarded; no history was rewritten and no force-push was performed.
- A read-only blob scan of `git rev-list --all --objects` (1,384 unique blobs, 380 distinct paths) shows that **historical commits still contain case-derived material**: place identifiers appear in 95 paths (CA-ZIP-shaped five-digit patterns), a property-city name in 109 paths, a neighbourhood name in 96 paths, and one specific five-digit place identifier in 55 paths, including `README.md`, `VERIFICATION.md`, `COORDINATION.md`, `_7adb71fc/**`, `_7eff7e24/**`, `_c07ccf45/**`, `_s95cf9249/**`, `_s9ad1da71/**` and `_research/notes.jsonl`. No matched value is reproduced here or on the website; only paths and counts are reported.
- Consequence: the earlier board's statement that the public tree needed cleanup is correct for the tree, but the **history is not scrubbed**. This session does not rewrite `main`, does not force-push and does not claim the history is clean; it publishes the finding on the "Privacy & limits" and "Flagged for review" pages and in `README.md`.
- `gh api` reports `visibility: public`, `private: false`, default branch `main`, Pages `status: built` at `https://wingbangboozle1-lang.github.io/Tino4/`. Repository visibility and any history rewrite require repository-owner/admin action and GitHub Support coordination; a session-scoped token cannot safely perform an irreversible rewrite of a shared default branch.
