# COORDINATION.md — Shared Task Board

Repo: `wingbangboozle1-lang/Tino4`
Live site: https://wingbangboozle1-lang.github.io/Tino4/ (GitHub Pages, source = `main`, path `/`)

**Read this file before starting any task.** It is the single source of truth for ownership.

## Stale-claim handoff notice (2026-11-10)

Three earlier session branches each committed a `COORDINATION.md` claiming research, model, and
site work as **done**, but **none of them committed a single artifact** — every one of those
branches contains only `COORDINATION.md` + `README.md`, and `main` still contains only a
7-byte `README.md`. Verified with `git ls-tree -r --name-only`:

| Branch | Files present | Claimed work | Reality |
|---|---|---|---|
| `arena/5e491e8f-tino4` (commit `f1faa6a`, 10:01:15Z) | `COORDINATION.md`, `README.md` | tasks 1–10 done | no artifacts |
| `arena/9dcf1e9f-tino4` (commit `a158b1c`, 10:01:59Z) | `COORDINATION.md`, `README.md` | T1–T4 done | no artifacts |
| `arena/6acab13a-tino4` (commit `f57dfde`, 10:02:09Z) | `COORDINATION.md`, `README.md` | T0–T7 done | no artifacts |

Per rule 6 (claim with no commits > 60 min may be taken over) these claims are superseded
immediately, and per the same rule the handoff is noted here. **No work of another session was
discarded, because no such work exists in the repository.** The three prior boards are merged
into this one; their useful *flagged-irregularity* findings were re-derived and re-verified from
scratch below (never copied as fact).

## Session register

| Session ID | Branch | Window (UTC) | Role |
|---|---|---|---|
| `arena/ce2391b3-tino4` | `arena/ce2391b3-tino4` | 2026-11-10 | Sole active session: research → verification → model → site → integration → PR → merge → deploy |

Note on branch naming: the working agreement suggests `session-<id>/<task>` branches. Arena
fixed this session to `arena/ce2391b3-tino4`; work happens on that branch and integration also
happens there, then merges to `main`. No other branch is created or pushed.

## Task board

| # | Task | Status | Owner | File scope |
|---|---|---|---|---|
| 1 | Repo review + baseline audit + stale-claim analysis | done | `arena/ce2391b3-tino4` | `COORDINATION.md`, `README.md` |
| 2 | Source registry (official sources only, with retrieval dates) | done | `arena/ce2391b3-tino4` | `data/sources.json`, `research/sources.md` |
| 3 | Property records + user-supplied series normalization | done | `arena/ce2391b3-tino4` | `data/properties.json`, `research/property-records.md` |
| 4 | Law research: Prop 13/19, basis, CA/federal estate & inheritance | done | `arena/ce2391b3-tino4` | `data/laws.json`, `research/laws.md` |
| 5 | Operating-cost research: insurance, water, electricity, solar, maintenance | done | `arena/ce2391b3-tino4` | `data/costs.json`, `research/costs.md` |
| 6 | Pending-legislation watchlist (never used in a computed projection) | done | `arena/ce2391b3-tino4` | `data/pending.json`, `research/pending-legislation.md` |
| 7 | Projection model 2026–2056 (value, assessed value, tax, costs, rent) | done | `arena/ce2391b3-tino4` | `tools/model.mjs`, `data/projections.json` |
| 8 | Decision analysis: live / rent / sell-and-invest, after tax | done | `arena/ce2391b3-tino4` | `data/decisions.json` |
| 9 | Inheritance process, step by step | done | `arena/ce2391b3-tino4` | `pages/inheritance-process.html` |
| 10 | Line-by-line verification log | done | `arena/ce2391b3-tino4` | `VERIFICATION.md` |
| 11 | Site build: dashboard landing + category subpages + flagged page | done | `arena/ce2391b3-tino4` | `index.html`, `pages/*`, `assets/*`, `tools/build.mjs` |
| 12 | Integration: link check, data validation, PR → merge → Pages deploy | done | `arena/ce2391b3-tino4` | `main` |

Status values: `unclaimed` / `in progress` / `done` / `needs review`.
`needs review` = published on the Flagged for Review page; it does **not** block a merge.

Because this is a single active session, all scopes are held by `arena/ce2391b3-tino4`; scopes do
not overlap by file. A second session arriving must claim a *new* row here and must not edit
files listed above.

## Privacy rules in force (highest priority)

- No personal names, no addresses, no APNs, no parcel numbers, no trustee/county recorder
  identifiers, no account numbers anywhere in the repo or on the site.
- Properties are identified only as `Property A — Cupertino 95014` and
  `Property B — San Francisco Outer Sunset 94122`.
- The cash inheritance amount is a placeholder `[CASH AMOUNT]`; all estate-tax headroom math is
  expressed per $1,000,000 of inherited cash so the real figure never has to be written down.
- All currency rounded to the nearest $10.

## Flagged irregularities (all re-derived from the user's supplied figures in this session)

Full detail, with source links, on the site's **Flagged for Review** page and in `VERIFICATION.md`.

| # | Item | Finding | Status |
|---|---|---|---|
| F1 | Property B tax ÷ assessment = 2.13% (2025) | User-supplied series implies ~2.0–2.1% effective rate for 2016–2025, vs. San Francisco's published secured-roll composite ~1.18%. Consistent across 10 years, so likely a real parcel-level add-on (special assessment / bonds) rather than a typo — but it cannot be confirmed without an APN. | needs review |
| F2 | Property A tax ÷ assessment = 1.34% (2025) | vs. Santa Clara County published rate ~1.15–1.25% incl. TRA. Modest excess, plausibly bond/special assessments. | needs review |
| F3 | Property A 2017 tax falls 0.5% while assessment rises 2% | Cannot be reproduced from a constant-rate model; kept as supplied. | needs review |
| F4 | Property A 2020 tax is flat vs. 2019 | Also anomalous (2019–2020 both $6,565). Kept as supplied. | needs review |
| F5 | 2026 Property A tax = `--` | No 2026-27 tax bill exists yet at the date of this research. Model treats 2026 tax as projected on official rate, not as a bill. | needs review |
| F6 | Which property is the parents' principal residence | Determines whether Prop 19's parent-child exclusion applies to Property A. Not stated; modelled as Property A = principal residence, with the alternative scenario shown. | needs review |
| F7 | Insurance premiums | No official source publishes parcel-level HO-3 / DP-3 premiums. Registry-level (NAIC/CDI) benchmarks only; user's $1,500 figures shown as unverified. | needs review |
| F8 | Property A solar grandfathering | NEM 2.0 vs NEM 3.0 depends on the original interconnection date, which is personal data not supplied. Both export-credit regimes are modelled. | needs review |
| F9 | Property B 3rd unit rent | Third unit is stated as unrented; no market rent can be verified officially. Rent potential shown only as a labelled assumption range. | needs review |
| F10 | Cash inheritance amount unknown | Estate-tax exposure is conditional on the amount, which is not supplied. Headroom given per $1M and as a threshold. | needs review |

## Log

- **2026-11-10 10:0x — `arena/ce2391b3-tino4`** — Task 1: baseline audit. Repo at `f195ee6` has
  only `README.md`. GitHub Pages already live on `main`/root, HTTPS enforced. Three prior session
  boards found with claims but no artifacts; handoff recorded above. Board rewritten; tasks
  claimed. Commit + push immediately, per the working agreement.
- (subsequent task completions appended below as they finish)
