# Inheritance decision dashboard

A privacy-respecting, official-source-linked decision guide for a home that will be inherited through a trust (2040–2050), analysed side by side with the already-owned multi-unit building the inheritor also owns. The goal is clear: compare, after tax, whether to live in the inherited home, rent it, or sell it and reinvest — and to project everything (values, assessed values, property taxes, insurance, water, electricity, upkeep, estate-tax headroom) over 50 years under baseline and black-swan conditions.

**Live site:** https://wingbangboozle1-lang.github.io/Tino4/

## What is on the site

| Area | Page |
| --- | --- |
| Overview and the answer | `index.html` |
| Executive summary | `pages/executive-summary.html` |
| Live vs rent vs sell, after tax | `pages/decision-analysis.html` |
| The two properties | `pages/properties.html` |
| Year-by-year projections 2026–2076 | `pages/projections.html` |
| Running costs (tax, insurance, water, electricity, solar, upkeep) | `pages/operating-costs.html` |
| Tax and property law (federal, California, local) | `pages/inheritance-law.html`, `pages/estate-thresholds.html` |
| Step-by-step inheritance process | `pages/inheritance-process.html` |
| Black-swan conditions (replays of 1977–2025 history) | `pages/black-swan-scenarios.html` |
| Law changes to watch | `pages/law-watchlist.html` |
| Every flagged item, with links | `pages/flagged-for-review.html` |
| Sources (quoted passages) | `pages/sources.html` |
| Method and privacy | `pages/methodology.html` |

Every table row links to an official source (IRS, BOE, FTB, county/city agencies, CBO, BLS, FHFA, HUD, CPUC, CFPB, courts/legislature) and carries a status label: **Verified**, **Owner-supplied**, **Projection**, **Assumption** or **Not verified**. Values that could not be confirmed from an official source are left blank.

## Privacy model

- Published figures that derive from the owner's private inputs are **rounded to the nearest $10 before they enter the model**, so no published number can be traced back to a source document or to an online search. Distinctive exact values (bills, assessments) are never shown.
- No name, street address, ZIP code, parcel number, account number, e-mail or phone number appears anywhere on the site. Two cities appear only where an official source is county- or city-specific; see the notice on the Flagged for Review page.
- Nothing in this repository should contain the owner's un-rounded private figures. Working files live under underscore-prefixed directories (`_research/`, `_s9ad1da71/`, `_a24b1c8c/`, `s179ec133/_work/`), which the Pages/Jekyll build does not publish.
- The site is `noindex`; it is a private decision brief, not a public document.
- Removing or publishing a file never removes it from Git history, forks, caches or prior deployments. See the Flagged for Review page and the task board.

## Build and verify

Requires only Python 3 and its standard library:

```sh
python3 tools/build.py     # regenerate the root site from the pinned generator (s179ec133/_work/tools/)
python3 tools/verify.py    # line-by-line structural/link/rounding/privacy checks, 0 failures expected
```

`tools/verify.py` checks, for every published page: every table row has an official source link and a status label; every external link is in the evidence ledger and on an official domain; every internal link and anchor resolves; every dollar amount ≥ $1,000 is a multiple of $10 unless it is an exact official statutory figure; no ZIP codes, addresses, e-mails, parcel wording; every page is `noindex`; no old public trees are present; `_config.yml` excludes the board and tooling.

## Data trail

- Evidence ledger (URLs, quoted passages, fetch dates): `s179ec133/_work/research/ledger/*.json`
- Model and results: `s179ec133/_work/model/`, `s179ec133/_work/data/`
- Parallel candidate builds and audits: `_s9ad1da71/`, `_a24b1c8c/` (kept for cross-check; not published)
- Task board and verification record: `COORDINATION.md`

The dashboard is general information for the owner's decision, not legal, tax, investment or insurance advice. Confirm every step with the linked official source and a licensed professional before acting.
