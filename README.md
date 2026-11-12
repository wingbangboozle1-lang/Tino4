# Two-property inheritance decision dashboard

A privacy-first, official-source-linked static dashboard for one household decision: a single-family
residence held in a revocable trust will be inherited between 2040 and 2050, while the inheritor
already owns a 3-unit building with two units rented and one available to live in. The dashboard
compares — after federal, California and local taxes — living in the inherited home, renting it out,
or selling it and reinvesting the proceeds, with a separate 50-year black-swan section.

**Live site:** https://wingbangboozle1-lang.github.io/Tino4/

Only Python's standard library is used; there are no runtime dependencies and no network calls at build time.

## Pages

| Page | What it answers |
| --- | --- |
| `index.html` | The ranked recommendation, the two-property snapshot, and how to read the numbers |
| `pages/executive-summary.html` | The best plan and why, what executing it involves, and what would change the answer |
| `pages/decision-analysis.html` | Live in / rent out / sell and reinvest for every inheritance year 2040–2050, plus sensitivities |
| `pages/suggestions.html` | Six decision suggestions, site-improvement proposals, and a gated review flow to choose before implementing |
| `pages/open-questions.html` | What we have, what is missing, ten questions that must be answered, and how to discover each gap |
| `pages/property-tax.html` | Rounded assessment and tax history, the fixed-charge explanation, Prop. 13/19/8 mechanics |
| `pages/projections.html` | Year-by-year 2026–2075 values, assessed values, taxes, insurance, water, electricity, upkeep |
| `pages/operating-costs.html` | Verified benchmarks, blank unverified cells, and how each cost line escalates |
| `pages/black-swan-scenarios.html` | Seven non-uniform 50-year regimes versus the baseline |
| `pages/inheritance-process.html` | The California trust sequence with every statutory deadline |
| `pages/estate-thresholds.html` | Federal, California and local thresholds, headroom, future thresholds, pending law |
| `pages/inheritance-law.html` | The sixteen statutory rules that govern the decision |
| `pages/law-watchlist.html` | Enacted changes, pending proposals, live litigation |
| `pages/methodology.html` | Equations, parameters and limitations |
| `pages/privacy.html` | What is omitted and what residual exposure remains |
| `pages/sources.html` | All 47 official sources |
| `pages/flagged-for-review.html` | Every unverified cell, irregularity and assumption |

Every table row links at least one official government publication. Where no official source exists,
the cell is left blank and logged on *Flagged for review* with the link to check.

## Privacy controls

* The two properties appear only as **Property A** and **Property B**. No individual, trustee,
  beneficiary or adviser is named.
* No street address, assessor parcel number, account number, city name, neighbourhood name or ZIP
  code is published anywhere in the site.
* Every owner-supplied figure was rounded to the nearest $10 before it entered the model, and every
  published dollar amount is a multiple of $10 unless it is an exact statutory figure quoted from a
  linked source.
* Every page carries a `noindex, nofollow` directive.
* `_config.yml` excludes all working directories, data files and generators from the Pages build.

These controls reduce, but do not eliminate, re-identification risk in a public repository. The
privacy page states that limit explicitly.

## Build and verify

```sh
python3 tools/build.py     # regenerates data/summary.json, then rebuilds index.html, pages/, assets/
python3 tools/verify.py    # structural, sourcing, rounding and privacy verification
```

`tools/build.py` and `tools/verify.py` delegate to `_c07ccf45/`, which is excluded from the Jekyll
build and therefore never published. The verifier fails on any table row without an official source
link, any external link not in the evidence ledger, any broken internal link, any dollar amount of
$1,000 or more that is not a multiple of $10 (unless it is a quoted statutory figure), any name-like
or parcel-like identifier, and any missing required row count.

## Repository layout

```
index.html, pages/**, assets/**   published static site
tools/build.py, tools/verify.py   wrappers that reproduce and check the site
_c07ccf45/model/engine.py         deterministic, $10-rounded household model
_c07ccf45/evidence/               source registry, flag register, verification ledger
_c07ccf45/tools/                  HTML generator and verifier
_c07ccf45/data/                   rounded inputs and generated summary
```

## Scope

Model output, not tax, legal, investment or appraisal advice. Laws, rates and thresholds change;
every published figure is linked to the publication it came from, with the date it was checked.
