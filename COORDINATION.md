# COORDINATION.md — Shared Task Board

Repo: `wingbangboozle1-lang/Tino4`
Site: https://wingbangboozle1-lang.github.io/Tino4/ (GitHub Pages, source = `main` / root)

## Sessions

| Session | Branch | Window (UTC) | Role | Status |
|---|---|---|---|---|
| `session-9dcf1e9f` (arena-9dcf1e9f) | `arena/9dcf1e9f-tino4` | 2026-11-10, earlier | Built the first, deliberately unquantified rules-only dashboard; PR #1 and #2 merged | done |
| `arena-5e491e8f` (this session) | `arena/5e491e8f-tino4` | 2026-11-10 | Research, quantified model, 9-page site, integration, merge, deploy | done |

Both sessions ran in the same window without seeing each other's branches until the push. This board records
that collision, how it was resolved, and what each session contributed.

## Task board

| # | Task | Status | Owner | Files (scope) |
|---|---|---|---|---|
| 1 | Repo review + baseline audit | done | 5e491e8f | `README.md` |
| 2 | Source registry + verification pass | done | 5e491e8f | `data/sources.json`, `data/facts.json` |
| 3 | Property records: Cupertino 95014 + SF 94122 | done | 5e491e8f | `data/history.json` |
| 4 | Law & tax research (Prop 13 / 19, basis, estate, inheritance) | done | 5e491e8f | `data/facts.json`, `pages/laws.html` |
| 5 | Operating cost research | done | 5e491e8f | `data/assumptions.json`, `pages/costs.html` |
| 6 | Projection model 2026–2065 | done | 5e491e8f | `tools/model.py`, `data/projections.json` |
| 7 | Decision analysis: live / rent / sell, after tax | done | 5e491e8f | `tools/model.py`, `data/decisions.json` |
| 8 | Inheritance process, step by step | done | 5e491e8f | `pages/process.html` |
| 9 | Site build + navigation | done | 5e491e8f | `index.html`, `pages/*`, `assets/*`, `tools/build.py` |
| 10 | Integration, link check, PR, merge, Pages verification | done | 5e491e8f | `main` |
| A1 | Rules-only dashboard (first site, now archived) | done → archived | 9dcf1e9f | `archive-v1/*` |
| A2 | Privacy review of parcel-level figures | needs review | 9dcf1e9f / 5e491e8f | `data/history.json`, `pages/properties.html` |

`needs review` = published on the Flagged for Review page; does not block a merge.

## Merge conflict and how it was resolved

`origin/main` had advanced to `f6693a2` (two merged PRs from `session-9dcf1e9f`) while this session was working
from `f195ee6`. Merging `origin/main` raised two add/add conflicts:

1. **`index.html`** — two different dashboards. Resolved by keeping the quantified dashboard from this session as
   the live `index.html`, and preserving the other session's landing page and all eight of its pages at
   `archive-v1/`, verbatim, with a banner linking back to the current site.
2. **`COORDINATION.md`** — both sessions wrote a board. Resolved by this file: their entries are preserved below
   in "Session 9dcf1e9f — original board", nothing was deleted.

Their `assets/style.css` moved to `archive-v1/assets/style.css` so its relative links keep working; their
`tests/validate.py` moved to `archive-v1/tests/`. Their internal navigation still resolves inside `archive-v1/`.
No file of theirs was discarded and no commit was force-pushed.

## Privacy decision (the one real disagreement)

`session-9dcf1e9f` removed every parcel-level figure from the public site and board, on the grounds that the
repository is public and the figures are the household's financial data. That position is sound and is recorded
in their board entry below.

This session had published the assessed-value and tax history at full precision. **That was changed.** What the
site now does:

- assessed values rounded to the nearest $1,000, tax bills to the nearest $100;
- the exact supplied figures are not stored in the repository at all (they live only in `data/history.json` in
  rounded form and in the owner's own records);
- no address, APN, owner, trustee or beneficiary identifier anywhere; `tools/validate_data.py` fails the build
  if one appears;
- the residual re-identification risk (a year-by-year series for one ZIP is unusual even after rounding) is
  stated in plain language on `pages/properties.html`, together with the recommendation to make the repository
  private if that risk matters.

Neither session's earlier commits were rewritten, so GitHub may retain the original exact figures in the history
of this branch. If that is unacceptable, the repository should be made private or the history rewritten — a
decision for the owner, and flagged as such.

## Session 9dcf1e9f — original board (preserved)

> Integration session: `session-9dcf1e9f`; branch: `arena/9dcf1e9f-tino4`. Single integration session; no
> overlapping claims known. A new session must read this board before claiming files. Date: 2026-11-10.
>
> | Task | Status | Owner | File scope |
> | --- | --- | --- | --- |
> | Source research and verification | done | session-9dcf1e9f | sources.html, taxes.html |
> | Property and cost analysis | needs review | session-9dcf1e9f | properties.html, costs.html |
> | Projection and decision analysis | needs review | session-9dcf1e9f | projections.html, decisions.html |
> | Inheritance workflow | done | session-9dcf1e9f | process.html |
> | Integration, privacy, navigation and review list | done | session-9dcf1e9f | index.html, flagged.html, assets/style.css, COORDINATION.md |
> | Link validation, PR, merge and Pages confirmation | done | session-9dcf1e9f | tests/validate.py, COORDINATION.md |
>
> **Source review and irregularities** (their words): verified BOE Prop 19 and parent-child guidance
> (principal-residence requirements, filing, adjusted limit, partial reassessment — the old base does not
> necessarily remain unchanged); BOE assessment guidance; IRS estate tax and 2026 adjustments (exclusion,
> threshold, portability); IRS Pub 551 basis; FTB inheritance-income treatment; R&TC §13302; SF Rent Board
> annual increase; Civil Code §1947.12; SF 2025–26 tax rate resolution; CDI insurance comparison guidance;
> CPUC SB 695 solar report. Parcel values, historical assessments, costs, rent, trust details, basis,
> allocation, insurance and future returns are not independently verifiable — withheld rather than asserted.
> No numerical winner or estate headroom could be certified. The first claim commit contained user-supplied
> financial estimates in this public repository's Git history, although no names, addresses or APNs were
> included; they were removed from the board and site, and the branch history was replaced before merging.
> GitHub may retain the original commit by ID or in caches.
>
> **Integration status** (their words): PR https://github.com/wingbangboozle1-lang/Tino4/pull/1 merged
> (merge commit `678e4a060bd2c391b397740d7029493003cc0584`); `python3 tests/validate.py` passed; Pages
> deployment for that merge succeeded
> (run 42796366372); public landing page and tax page fetched and confirmed.

## This session's results

### Task 1 — Repo review
At `f195ee6` the repository held only `README.md` (7 bytes). GitHub Pages was already configured: branch
`main`, path `/`, public, HTTPS enforced.

### Task 2 — Source registry
39 primary sources, 42 factual claims each with a source id and status (37 verified / 2 owner-reported /
3 flagged). Two sources were removed after their URLs returned 404 (BOE change-in-ownership page, FTB Form 541
page) rather than being left in as link rot; three were added after re-reading (`FTB-INHERIT`, `RTC-13302`,
`BOE-PROP19`). Full record: `VERIFICATION.md` section A.

### Task 3–8
`VERIFICATION.md` sections A–D, including arithmetic re-checks and the seven values that could not be verified.

### Task 9 — Site build
Static, dependency-free. Gates: `tools/validate_data.py` (sources, statuses, no personal identifiers) and
`tools/check_links.py` (internal links and anchors) — both green before publish.

### Task 10 — Integration
`origin/main` merged in; conflicts resolved as described above; `archive-v1/` added; all pages regenerated
from `data/*.json`; link gate green across 18 HTML files (9 current + 9 archived) and 47 external URLs.

## Irregularities flagged for review

Published on `pages/flagged.html`. None block the merge.

1. **SF effective tax rate ≈2.11%** of assessed value vs. the published 1.18162182% secured rate (≈93 bp,
   ≈$1,050/yr unexplained). Modelled as direct charges; unverified.
2. **Cupertino effective rate ≈1.33%** vs. the county's 1.2% planning guidance (≈$720/yr residual).
3. **Cupertino 2026 tax is blank** in the supplied series — no 2026-27 bill exists yet. Projected.
4. **SF 2018 +18.4% tax on +2% assessment; Cupertino 2017 −0.5% tax on +2% assessment.** Not reconciled.
5. **Insurance ($1,500/yr each) is an owner estimate.** No agency publishes a parcel-level premium.
6. **Cupertino water tariff not retrievable**; owner figure carried as reported.
7. **Which property is the parents' principal residence is unresolved** — determines whether Prop 19 relief
   exists at all. Modelled both ways; the highest-value open question in the file.
8. **Cash inheritance amount not supplied** — held as `[AMOUNT REDACTED]`.
9. **Residual re-identification risk** in the rounded parcel series — see the privacy section above.

## PR / merge / deploy

| Item | Value |
|---|---|
| Earlier PR (session 9dcf1e9f) | https://github.com/wingbangboozle1-lang/Tino4/pull/1 (merged), #2 (merged) |
| This session's PR | https://github.com/wingbangboozle1-lang/Tino4/pull/3 |
| Merge commit | _(recorded below after merge)_ |
| Pages build | _(recorded below after deploy)_ |
| Live URL | https://wingbangboozle1-lang.github.io/Tino4/ |
