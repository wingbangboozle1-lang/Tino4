# Inheritance decision dashboard

A privacy-first, official-source-linked static dashboard for reviewing inheritance decisions: one home will be inherited through a trust (2040–2050); the inheritor already owns a separate multi-unit building. Compare, after tax, whether to live in the inherited home, rent it, or sell it and reinvest — with year-by-year projections (value, assessed value, property tax, insurance, water, electricity, upkeep) over 50 years and a separate black-swan section, plus a step-by-step inheritance process, estate-tax thresholds and headroom, a law-change watchlist, and a Flagged for Review register. Built using only Python's standard library.

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

Every table row links to an official source (IRS, BOE, FTB, county/city agencies, CBO, BLS, FHFA, HUD, CPUC, CFPB, courts/legislature) and carries a status label: **Verified**, **Owner-supplied**, **Projection**, **Assumption** or **Not verified**. Values that cannot be confirmed from an official source are left blank.

## Build and verify

```sh
python3 tools/build.py
python3 tools/verify.py
```

`tools/build.py` re-runs the model engine and rebuilds the root site deterministically from the pinned generator in `s179ec133/_work/`. `tools/verify.py` checks, for every published page: every table row has an official source link and a status label; every external link is in the evidence ledger and on an official domain; every internal link and anchor resolves; every dollar amount of $1,000 or more is a multiple of $10 unless it is an exact official statutory figure; no ZIP codes, neighbourhood names, e-mail addresses or parcel wording; every page asks search engines not to index it; the working-directory exclusions in `_config.yml` (including the legacy candidate directory) are in place. Requires only Python 3 and its standard library.

GitHub Pages is configured to build from the root of `main`. Jekyll's `_config.yml` excludes the board, tooling and working directories from the site. The public site uses anonymized placeholders (Property A / Property B) and rounds every owner-supplied and projected dollar amount to the nearest $10. No names, street addresses, parcel numbers, ZIP codes, e-mail addresses or account data are published. Rounding is not a guarantee of anonymity: distinctive figures combined over time can still be identifying, and the repository and its history are public. Deleting files in a subsequent commit does not erase previous commits, deployments, caches, or forks. Keep exact figures and private documents out of this public repository. See the task board for the privacy incident and outstanding remediation.

## Data trail

- Evidence ledger (URLs, quoted passages, fetch dates): `s179ec133/_work/research/ledger/*.json`
- Model and results: `s179ec133/_work/model/`, `s179ec133/_work/data/`
- Parallel candidate builds and audits (kept for cross-check, not published): `_s9ad1da71/`, `_a24b1c8c/`
- Task board and verification record: `COORDINATION.md`

The dashboard is educational, not legal, tax, investment or insurance advice. Every table row links to an official source and carries a status label (Verified / Owner-supplied / Projection / Assumption / Not verified). Values that cannot be confirmed from an official source are left blank and listed on the Flagged for Review page. Models are hypothetical, not official predictions or personalized recommendations. Confirm every step with the linked official source and a licensed professional before acting.
