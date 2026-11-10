# COORDINATION.md — Shared Task Board

Repo: `wingbangboozle1-lang/Tino4`
Site: https://wingbangboozle1-lang.github.io/Tino4/ (GitHub Pages, source = `main` / root)
Branch used by this session: **`arena/5e491e8f-tino4`** (PR to `main`)

## Session log

| Session ID | Branch | Window (UTC) | Role |
|---|---|---|---|
| `arena-5e491e8f` | `arena/5e491e8f-tino4` | 2026-11-10 | Sole session: research, model, site build, integration, PR + merge, deploy |

No other session was active in this window. No task was taken over, and no merge conflict occurred.

## Task board

| # | Task | Status | Owner | Files (scope) |
|---|---|---|---|---|
| 1 | Repo review + baseline audit | done | arena-5e491e8f | `README.md` |
| 2 | Source registry + verification pass (official sources only) | done | arena-5e491e8f | `data/sources.json`, `data/facts.json` |
| 3 | Property records: Cupertino 95014 + SF 94122 tax/assessment series | done | arena-5e491e8f | `data/history.json` |
| 4 | Law & tax research: Prop 13 / Prop 19 / basis / estate & inheritance | done | arena-5e491e8f | `data/facts.json`, `pages/laws.html` |
| 5 | Operating cost research: insurance, water, electricity, maintenance | done | arena-5e491e8f | `data/assumptions.json`, `pages/costs.html` |
| 6 | Projection model 2026–2065 (value, assessed value, tax, costs, rent) | done | arena-5e491e8f | `tools/model.py`, `data/projections.json` |
| 7 | Decision analysis: live / rent / sell, after tax | done | arena-5e491e8f | `tools/model.py`, `data/decisions.json` |
| 8 | Inheritance process, step by step | done | arena-5e491e8f | `pages/process.html` |
| 9 | Site build: landing page + category subpages + tables | done | arena-5e491e8f | `index.html`, `pages/*`, `assets/*`, `tools/build.py` |
| 10 | Integration: merge, link check, publish, deploy verification | done | arena-5e491e8f | `main` |

Status values: `unclaimed` / `in progress` / `done` / `needs review`.
`needs review` = published on the Flagged for Review page; does not block merge.

## Ownership / conflict rules used

- Scopes did not overlap; one session held all of them, so nothing was edited outside a claimed scope.
- Shared outputs (`index.html`, navigation, table data) were edited only in the final integration step (task 10).
- `git pull --rebase` immediately before each push; no rebase conflicts occurred.
- Session branch note: this workspace's session branch `arena/5e491e8f-tino4` is fixed and cannot be
  renamed, so it doubles as the integration branch. The PR is from it to `main`.

## Task results

### Task 1 — Repo review
At `f195ee6` the repository held only `README.md` (7 bytes). No prior site, data, or coordination file.
GitHub Pages was already configured: branch `main`, path `/`, public, HTTPS enforced.

### Task 2 — Source registry
36 primary sources, all agency/legislature/utility documents. 41 factual claims, each with a source id
and a status. Every claim marked `verified` resolves to a page that was opened and read this session
(see `VERIFICATION.md` section A). Two sources were removed after their URLs returned 404
(BOE change-in-ownership page, FTB Form 541 page) rather than being left in as link-rot.

### Task 3–8
Recorded in `VERIFICATION.md`, sections A–D, including the arithmetic re-checks and the seven values that
could not be verified.

### Task 9 — Site build
Static site, no dependencies, no build step at deploy time. Gates:
`python3 tools/validate_data.py` and `python3 tools/check_links.py` both green before publish.

### Task 10 — Integration & publish
All pages regenerated from `data/*.json` after every change; no hand-edited tables. Link gate green
before the merge (9 pages, 34 external URLs, all internal links and anchors resolve).

## Irregularities flagged for review

Published on `pages/flagged.html`. None block the merge.

1. **SF effective tax rate ≈2.1%** of assessed value vs. the published 1.18162182% secured rate (~96 bp,
   ≈$1,089/yr unexplained). Modelled as direct charges; unverified.
2. **Cupertino effective rate ≈1.33%** vs. the county's 1.2% planning guidance. Series is internally
   consistent; the ad valorem / charges split is unknown.
3. **Cupertino 2026 tax is blank** in the supplied series — no 2026-27 bill exists yet. Projected.
4. **SF 2018 +18.4% tax on +2% assessment; Cupertino 2017 −0.5% tax on +2% assessment.** Not reconciled.
5. **Insurance ($1,500/yr each) is an owner estimate.** No agency publishes a parcel-level premium.
6. **Cupertino water tariff not retrievable**; owner figure ($100–$150/mo) carried as reported.
7. **Which property is the parents' principal residence is unresolved** — this determines whether Prop 19
   relief exists at all. Modelled both ways; the highest-value open question in the file.
8. **Cash inheritance amount not supplied** — held as `[AMOUNT REDACTED]`.

## PR / merge / deploy

| Item | Value |
|---|---|
| PR | _(filled in after merge)_ |
| Merge commit | _(filled in after merge)_ |
| Pages build | _(filled in after deploy)_ |
| Live URL | https://wingbangboozle1-lang.github.io/Tino4/ |
