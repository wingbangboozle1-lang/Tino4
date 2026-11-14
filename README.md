# Two-property inheritance decision brief

A privacy-conscious static site about two distinct situations: **Property A** is expected to pass through a trust around 2040–2050; **Property B** is already owned by the inheritor, is multi-unit, and is partly rented. The dashboard compares occupy, rent, sell, and mixed sale/reinvestment paths, with deadlines, source links, a review-only suggestions queue, glossary and printable adviser sheet.

The public site uses A/B labels and rounds dollar figures to $10, but rounding is **not anonymisation**. A combination of property values, tax assessments, rents and property characteristics may still identify an asset. No address, name, ZIP or parcel number is intentionally included in the rendered site. The repository has historical public disclosures; this branch does not rewrite shared history or claim those disclosures have been purged. See `pages/privacy.html` and `pages/flagged-for-review.html`.

## What is here

| Path | Purpose |
| --- | --- |
| `index.html` | Dashboard, conditional answer, first-screen reversal conditions, and grouped navigation |
| `pages/*.html` | 17 section pages plus short redirects for retired URLs |
| `pages/black-swan.html` | California housing replay plus historical stock/Treasury anchors and a local-only phased-entry stress lab |
| `pages/advisor-brief.html` | One-page attorney/CPA meeting sheet; no household-specific dollar totals |
| `pages/glossary.html` | Plain-language terms with official links |
| `pages/inheritance-process.html` | Deadline timeline and inheritance workflow |
| `pages/suggestions.html` | Review queue; choices stay in this browser and do not implement proposals |
| `assets/case-projections.csv` | Year-by-year case projection data, display amounts rounded to $10 |
| `_7adb71fc/` | Generator, evidence ledger, models, page text and manifest |
| `_7eff7e24/case_data.py`, `case_model.py` | Rounded case inputs and property cash-flow model |
| `tools/build.py`, `tools/verify.py`, `tools/test_case.py` | Build entry point, structural/source/privacy checks, regression tests |
| `.github/workflows/verify.yml` | CI tests, rebuild, verification and reproducible-output check |

## Build and check locally

```sh
python3 tools/build.py       # self-checks, then writes the site
python3 tools/verify.py      # structure, source coverage, rounding, privacy tokens and links
python3 -m unittest discover -s tools -p 'test_*.py'
```

The build is standard-library Python and makes no network calls. The static site has a restrictive Content Security Policy and `noindex` metadata. Browser what-if controls calculate locally and do not store or transmit the entered amount or selected path. The review queue persists only review selections in local browser storage.

## What the stock-entry lab does—and does not do

The scenario tool compares all-at-once stock exposure with a 24-, 30- or 36-month illustrative short-Treasury bridge followed by equal-dollar monthly stock purchases over 6 or 12 months. The bridge is represented by a constant-yield cash proxy, not a security-level bill ladder or note valuation. A control also allows some stock exposure immediately, so a mixed path can be examined. The default principal is a hypothetical scale only, not an estimate of this household's proceeds. The constant gross Treasury yield is an adjustable sensitivity, not a current quote or forecast.

- The 1929-like sequence is a synthetic linear path to an 80% loss floor over 33 months and then flat; the Federal Reserve source reports a historical decline of more than 80%, but does not supply the monthly total-return series used by a true backtest.
- The 2008–2011 sequence uses official year-end S&P composite **price-index** levels and assumed linear monthly interpolation. It excludes dividends and is not an exact monthly investment replay.
- The rising-market path is invented, to expose the opportunity cost of waiting.
- Treasury's official 2008 3-month and 2-year par-yield observations are shown as evidence that yields can change. They are not holding-period returns. The model does not capture actual bill-roll yields, federal tax on interest, note coupon reinvestment or a 2-year note's market-price change if sold before maturity. The displayed entry values are nominal and pre-tax.

These scenarios are transparent stress assumptions, not forecasts or investment recommendations. They complement—not replace—the separate after-tax property comparisons and adviser review.

## How evidence and amounts are handled

- Display dollars use half-up rounding to the nearest $10. That reduces precision but does not, by itself, prevent re-identification.
- Official sources support legal rules, historical data or security terms; they do not verify household facts. Owner-supplied inputs, projections, invented assumptions and missing evidence are labelled separately.
- Where a required private or future fact cannot be verified, the site flags it for adviser review instead of presenting an inference as an official value.
- Every data-table row includes an official source link and an evidence status. The verifier checks structure and source coverage; it does not certify that every sentence is legally or financially correct.

## Scope

This is a planning aid, not legal, tax, insurance, appraisal or investment advice. Laws, rates and thresholds can change before a 2040–2050 transfer. Re-check primary sources and have the trustee's attorney, CPA and property/insurance advisers review the actual documents and inputs before acting.
