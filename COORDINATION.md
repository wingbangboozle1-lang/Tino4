# COORDINATION.md — Shared Task Board

Repo: `wingbangboozle1-lang/Tino4`
Site: https://wingbangboozle1-lang.github.io/Tino4/ (GitHub Pages, source = `main` / root)

## Session log

| Session ID | Branch | Window (UTC) | Role |
|---|---|---|---|
| `arena-5e491e8f` | originally `arena/5e491e8f-tino4`, integration on `session/arena-5e491e8f-integration` | 2026-11-10 | Sole session this window: research, site build, integration, PR + merge, deploy |

> Branch-name note: this session was launched on `arena/5e491e8f-tino4`, which is a
> protected session branch in the Arena workspace. Integration work was therefore done on
> `session/arena-5e491e8f-integration` (the `session-<id>/<task>` naming convention in the
> working agreement) and merged to `main` by PR. No other session was active; no task was
> taken over from another session.

## Task board

| # | Task | Status | Owner | Files (scope) |
|---|---|---|---|---|
| 1 | Repo review + baseline audit | done | arena-5e491e8f | `README.md` |
| 2 | Source registry + verification pass (official sources only) | done | arena-5e491e8f | `data/sources.json` |
| 3 | Property records: Cupertino 95014 + SF 94122 property tax/assessment series | done | arena-5e491e8f | `data/properties.json` |
| 4 | Law & tax research: Prop 13 / Prop 19 / basis / estate & inheritance | done | arena-5e491e8f | `data/laws.json` |
| 5 | Operating cost research: insurance, water, electricity, maintenance | done | arena-5e491e8f | `data/costs.json` |
| 6 | Projection model 2026–2056 (value, assessed value, tax, costs, rent) | done | arena-5e491e8f | `data/projections.json`, `assets/js/model.js` |
| 7 | Decision analysis: live / rent / sell-and-invest, after-tax | done | arena-5e491e8f | `data/decisions.json` |
| 8 | Inheritance process, step by step (CA trust → Prop 19 claim → basis) | done | arena-5e491e8f | `pages/inheritance-process.html` |
| 9 | Site build: landing page + category subpages + tables | done | arena-5e491e8f | `index.html`, `pages/*`, `assets/*` |
| 10 | Integration: merge, link check, publish to GitHub Pages | done | arena-5e491e8f | `main` |

Status values: `unclaimed` / `in progress` / `done` / `needs review`.
`needs review` = published on the Flagged for Review page; does not block merge.

## Ownership / conflict rules used this window

- Scopes above did not overlap between tasks; one session held all of them.
- Shared outputs (`index.html`, `pages/index`, nav, table data) were edited only in the
  final integration step (task 10), after tasks 1–9 were complete.
- Small frequent commits; `git pull --rebase` immediately before each push.

## Task results, sources, verification performed

### Task 1 — Repo review
Repository at `f195ee6` contained only `README.md` (7 bytes: `# Tino4`). No prior site, no
prior data, no `COORDINATION.md`. GitHub Pages already configured: branch `main`, path `/`,
public, HTTPS enforced, URL https://wingbangboozle1-lang.github.io/Tino4/.

### Task 2 — Source registry
Every table row in the site carries a `source_id` that resolves to `data/sources.json`.
Registry is restricted to primary/agency sources: IRS, California BOE, California FTB,
California Legislature, Santa Clara County, City & County of San Francisco, SFPUC,
San José Water, PG&E, CPUC, HUD, U.S. Census, California Department of Insurance,
California FAIR Plan, Santa Clara County Assessor, SF Assessor-Recorder.

### Task 3–8 — See `VERIFICATION.md` for the line-by-line record (value → source → status).

### Task 9 — Site build
Static site, no external JS/CSS dependencies (Pages-safe, no build step). `python3
tools/check_links.py` and `tools/validate_data.py` gate the build.

### Task 10 — Integration & publish
See "PR / merge / deploy" section at the bottom of this file.

## Irregularities flagged for review

All items below are published on `pages/flagged.html`. None block the merge.

1. **SF effective tax rate in user-provided data is ~2.1%**, well above San Francisco's
   published secured roll rate (~1.18%). Cupertino series implies ~1.33% vs. Santa Clara
   County's ~1.15%–1.25%. The user's series are kept verbatim for trend, and model runs use
   the published county rates. Flagged.
2. **Property-tax series end at 2026 = `--`** (no 2026 tax bill exists yet at time of
   writing). Model starts from 2026–27 roll assumptions, marked projected.
3. **Assessor identity fields are intentionally absent** — no APN, no address, no parcel
   number, no trust/trustee names. Privacy requirement (highest priority).
4. **Insurance premiums are range estimates**, not quotes. No official source publishes a
   parcel-level 95014/94122 premium. Values used are CPI/FAIR-Plan-anchored ranges and are
   labeled unverified-estimate in the cost table.
5. **Water/electricity** at 94122: user figure $330–$400/mo water across 3 units implies
   well above SFPUC single-family typical; retained as reported (landlord account includes
   common irrigation/laundry). Flagged, not modeled as authoritative.
6. **AB 1482 rent cap CPI** applies to Cupertino (no local rent ordinance). The published
   cap for the Aug 2025–Jul 2026 window is used only where the official announcement was
   retrievable; otherwise row left blank and flagged.
7. **Federal estate-tax exemption after 2025** — verified against enacted legislation, not
   proposed bills. Any *proposed* change is listed separately as "pending legislation" and
   never used in a computed projection.

## PR / merge / deploy

(filled in after the merge — PR number, merge commit, Pages build status)
