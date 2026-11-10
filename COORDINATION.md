# COORDINATION.md — shared task board

Project: inheritance decision analysis for **Property A (Cupertino)** and **Property B (San Francisco)**, published as a GitHub Pages dashboard.

All times are UTC. Session IDs are the short IDs in each session's branch name.

---

## 0. Rules every session must follow

### 0.1 Privacy (top priority — read before committing anything)

This repository and its GitHub Pages site are **public**. Anything committed here (files, commit messages, PR text, this board) is visible to anyone, permanently, through Git history.

1. **Never commit personal information**: no names, street addresses, parcel numbers (APN / block-lot), trust names, dates of birth, account numbers, e-mail addresses, phone numbers, or family details. Use placeholders: `[BENEFICIARY]`, `[TRUSTOR]`, `[TRUSTEE]`, `[TRUST]`, `[PROPERTY A]`, `[PROPERTY B]`, `[ADVISOR]`.
2. **Never commit the owner's exact year-by-year assessed values or tax-bill amounts.** Those can be matched against public assessment rolls to find a specific parcel. Only the generalized inputs in `data/inputs.json` may be published. Exact figures are for in-session ("internal") checks only and must stay out of Git.
3. **Location is published at city / county level only.** No ZIP codes, neighborhood names, or anything narrower.
4. **Never look up the specific properties** (no parcel, owner, permit, or listing searches). Research covers laws, rates, and public statistics only.
5. If personal information is discovered during research, do not record it anywhere in the repo.
6. Run `python3 tools/privacy_scan.py` before every push once the tool exists.

### 0.2 Verification

1. Every table row on the site carries a source link to an official site (government agency, legislature, court, regulator, or the body that issues the figure).
2. A value is marked **verified** only after the official page was opened in the session and the value was read on that page. Record the URL and date.
3. If a value cannot be confirmed from an official source: leave it **blank**, mark it **unverified**, and list it on the Flagged for Review page. Never infer or fill in values.
4. Forward-looking numbers are **projections**, never "verified". Each projection row links to the official source of the rule or statistic it is built from and states the formula.

### 0.3 Working agreement

1. Read this file first. Claim a task by writing your session ID and file scope in the board, then commit and push the claim immediately. Never start a task another session has claimed.
2. Work only on your own branch and only inside your claimed file scope. To change a file owned by another session, add a row to **Change requests** instead of editing it.
3. Small, frequent commits. `git pull --rebase` before every push. On a merge conflict: stop, resolve without discarding the other session's work, and log it in **Log**.
4. Shared outputs (table data, site index, navigation) are changed only by the final integration session after all other tasks are done.
5. A claim older than 60 minutes with no commits may be taken over by another session; note the handoff in **Log**.
6. Status values: `unclaimed`, `in progress`, `done`, `needs review`. `needs review` means the item is published on the Flagged for Review page and does not block anything.

### 0.4 Branch naming

The requested convention is `session-<id>/<task>`. Sessions launched from the Arena platform are pinned to a single platform-assigned branch that cannot be renamed and cannot push to other branches. For those sessions the platform branch (for example `arena/f5c6ffa9-tino4`) stands in for `session-<id>/<task>`, and the session ID is the short ID inside the branch name.

---

## 1. Task board

| ID | Task | Status | Owner (session) | Branch | File scope | Claimed (UTC) |
|----|------|--------|-----------------|--------|------------|---------------|
| T00 | Repo review, privacy baseline, coordination board | in progress | f5c6ffa9 | arena/f5c6ffa9-tino4 | `COORDINATION.md`, `README.md` | 2026-11-10 10:15 |
| T01 | Research: California property tax (Prop 13, Prop 19, local rates, transfer tax) | in progress | f5c6ffa9 | arena/f5c6ffa9-tino4 | `data/facts/property_tax.json` | 2026-11-10 10:15 |
| T02 | Research: federal estate and gift tax; California estate / inheritance tax | in progress | f5c6ffa9 | arena/f5c6ffa9-tino4 | `data/facts/estate_tax.json` | 2026-11-10 10:15 |
| T03 | Research: income tax (basis step-up, capital gains, home-sale exclusion, rental income) | in progress | f5c6ffa9 | arena/f5c6ffa9-tino4 | `data/facts/income_tax.json` | 2026-11-10 10:15 |
| T04 | Research: operating costs (insurance, water, electricity / solar, maintenance) | in progress | f5c6ffa9 | arena/f5c6ffa9-tino4 | `data/facts/costs.json` | 2026-11-10 10:15 |
| T05 | Research: rental rules (San Francisco Rent Ordinance, state tenant law, vacancy tax) | in progress | f5c6ffa9 | arena/f5c6ffa9-tino4 | `data/facts/rental_rules.json` | 2026-11-10 10:15 |
| T06 | Research: step-by-step trust inheritance process | in progress | f5c6ffa9 | arena/f5c6ffa9-tino4 | `data/facts/process.json` | 2026-11-10 10:15 |
| T07 | Research: pending and proposed law changes | in progress | f5c6ffa9 | arena/f5c6ffa9-tino4 | `data/facts/law_watch.json` | 2026-11-10 10:15 |
| T08 | Research: economic anchors (inflation, home-price index, market returns, rents) | in progress | f5c6ffa9 | arena/f5c6ffa9-tino4 | `data/facts/economics.json` | 2026-11-10 10:15 |
| T09 | Projection and decision model | in progress | f5c6ffa9 | arena/f5c6ffa9-tino4 | `tools/model.py`, `data/inputs.json`, `data/projections.json` | 2026-11-10 10:15 |
| T10 | Site generator, styles, category pages | in progress | f5c6ffa9 | arena/f5c6ffa9-tino4 | `tools/build.py`, `tools/check_links.py`, `tools/privacy_scan.py`, `assets/`, generated `*.html` except `index.html` | 2026-11-10 10:15 |
| T11 | Line-by-line verification pass and Flagged for Review list | in progress | f5c6ffa9 | arena/f5c6ffa9-tino4 | `data/flags.json`, `data/sources.json` | 2026-11-10 10:15 |
| T12 | Final integration: merge branches, re-verify combined data, link check, PR to `main`, merge, confirm Pages deploy | in progress | f5c6ffa9 | arena/f5c6ffa9-tino4 | shared outputs: `index.html`, navigation, combined table data, `.nojekyll` | 2026-11-10 10:15 |

Session `f5c6ffa9` is the only session on record at claim time (remote had one branch, `main`, with one commit, and no open pull requests), so it holds every task and also acts as the final integration session.

---

## 2. Change requests (edits needed in a file another session owns)

| Date (UTC) | Requesting session | File | Owner session | Request | Status |
|------------|--------------------|------|---------------|---------|--------|
| — | — | — | — | none yet | — |

---

## 3. Completed-task records (sources, verification performed, irregularities)

Filled in as each task is finished.

---

## 4. Pull requests and deploys

| PR | Branch → target | Opened (UTC) | Merge result | Pages deploy |
|----|-----------------|--------------|--------------|--------------|
| — | — | — | — | — |

---

## 5. Log

| Time (UTC) | Session | Event |
|------------|---------|-------|
| 2026-11-10 10:15 | f5c6ffa9 | Board created (file did not exist). Remote checked: only `main` (single "Initial commit"), no other branches, no pull requests. All tasks claimed by this session. |
| 2026-11-10 10:15 | f5c6ffa9 | Repo review: repository is **public**; GitHub Pages already enabled (deploy from branch `main`, folder `/`). Repo contained only `README.md` with a one-line title. Privacy rules in section 0.1 adopted because of the public visibility. |
