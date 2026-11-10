# Bay Area Inheritance Decision File

A source-verified analysis of whether to **live in, rent, or sell** a Cupertino house (95014, ≈$3,100,000)
that is expected to pass through a family trust between 2040 and 2050, while a three-unit San Francisco
building (94122, ≈$1,800,000) stays in the family.

Live site: **https://wingbangboozle1-lang.github.io/Tino4/**

## What is in here

```
index.html                  Executive summary and dashboard
pages/properties.html       Snapshot + 12-year assessment and tax history
pages/taxes.html            Prop 13 mechanics, 2026-2065 projections, Prop 19 outcomes, estate tax thresholds
pages/costs.html            Insurance, water, electricity, maintenance — with what is and is not verifiable
pages/decisions.html        Four strategies to 2065, after-tax, with sensitivity and break-even
pages/process.html          14-step inheritance process with deadlines and forms
pages/laws.html             Federal / California / local rules, enacted changes, things being discussed
pages/sources.html          Full source registry, line-by-line verification record, model assumptions
pages/flagged.html          Everything unverified or irregular, and what would resolve it
data/sources.json           The 36 official sources (IRS, BOE, FTB, SCC Assessor, SF Treasurer, SFPUC, PG&E, CDI, ...)
data/facts.json             41 factual claims, each with a source id and a status badge
data/history.json           Owner-supplied assessment and tax series (verbatim)
data/assumptions.json       Every model input
data/projections.json       Generated output (do not edit by hand)
data/decisions.json         Generated ranking summary
tools/model.py              Projection + decision engine
tools/build.py              Static site generator
tools/validate_data.py      Data gate: sources, statuses, no personal identifiers
tools/check_links.py        Link gate: internal links and anchors
COORDINATION.md             Shared task board for parallel agent sessions
VERIFICATION.md             The audit trail: what was checked, against what, and what was not
```

## Rebuild

```bash
python3 tools/model.py        # regenerate data/projections.json + data/decisions.json
python3 tools/build.py        # render index.html and pages/*.html
python3 tools/validate_data.py
python3 tools/check_links.py
```

No dependencies beyond the Python 3 standard library. No build step, no external CSS or JS, so the
output runs directly on GitHub Pages.

## Privacy

This repository contains **no** street address, assessor's parcel number, owner, trustee or beneficiary
name, or account number. Properties are identified only by ZIP code. `tools/validate_data.py` fails the
build if a pattern resembling an APN, SSN or street address appears in the data.

## Standing

This is an internal planning document, not legal, tax or investment advice. Rules change; every rule
carries a link so it can be re-checked. Figures are rounded to the nearest $10.
