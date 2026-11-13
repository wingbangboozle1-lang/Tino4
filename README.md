# Two-property inheritance: decision dashboard

A static site answering one question: for a house that is expected to arrive by
trust, and a house that is already owned, is it better to live in the inherited
home, rent it out, or sell it and reinvest?

The published site contains only rounded figures, anonymous property labels
(Property A and Property B), and no addresses, parcel numbers, names or balances.
Every table row carries a link to the official source that supports the rule it
rests on, and a badge saying what kind of evidence the row is.

## What is here

| Path | Purpose |
| --- | --- |
| `index.html` | Dashboard: the recommendation, the four numbers behind it, and links to each section |
| `pages/*.html` | The fifteen section pages, plus short redirects for retired URLs |
| `assets/case-projections.csv` | The year-by-year table as data, every value rounded to $10 |
| `_7adb71fc/` | Generator: official evidence ledger, replay engine, projection engine, page text |
| `_7eff7e24/case_data.py`, `case_model.py` | The case inputs and the cash-flow model |
| `tools/build.py`, `tools/verify.py`, `tools/test_case.py` | Build entry point, site checks, regressions |
| `.github/workflows/verify.yml` | Runs the tests, rebuilds, verifies, and fails if the committed output differs |

## Build and check locally

```sh
python3 tools/build.py       # self-checks, then writes the site
python3 tools/verify.py      # structural, sourcing, rounding and privacy checks
python3 -m unittest discover -s tools -p 'test_*.py'
```

Everything is standard library. There is no network call, no analytics, no
external asset and no build step beyond Python. Pages are served with a strict
Content-Security-Policy and `noindex`.

## How the numbers are handled

- Dollar amounts are rounded half-up to the nearest $10 before publication.
- A figure that no official source supports is left blank and marked
  `missing`, rather than estimated.
- Each row is badged `verified` (an official source states it), `owner` (the
  owner supplied it, not independently confirmed), `projection` (arithmetic on
  rounded inputs under a stated assumption), `assumption` (an invented planning
  parameter), or `missing` (no evidence).
- The black-swan page replays the published California record rather than
  assuming constant growth, and states no probabilities.

## Scope

This is a planning document, not legal, tax or investment advice. Statutes and
thresholds change; the pages link to the primary sources so any figure can be
re-checked before it is relied on.
