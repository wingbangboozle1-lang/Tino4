# Inheritance decision workspace

A static, source-linked decision workspace for two California properties:

- **Property A** — a home expected to transfer through a revocable trust inside the 2040-2050 window. Not owned by the decision maker today.
- **Property B** — a three-unit building the decision maker already owns and lives in, with two units let.

The site is built from `tools/` and published with GitHub Pages. It is a planning
framework, not legal, tax, insurance, appraisal or investment advice.

## Privacy — read this first

- No owner name, street address, parcel or assessor identification number, trust name, account number, date of birth, document image, email address or telephone number appears on any page.
- Every working dollar figure is rounded to the nearest ten dollars.
- The only location detail published is the county and the public postal area, which is needed to reproduce the utility tariff and insurance research.
- The site carries `noindex`, a restrictive Content Security Policy and no third-party asset. A `noindex` directive is **not** access control.
- **Residual risk:** a rounded assessment history plus a public postal area could in principle be matched against a county assessment roll. That risk is documented on the privacy page rather than hidden.
- **Public Git history is not scrubbed.** Earlier commits, pull-request diffs, forks, caches and clones may retain material that a normal cleanup commit does not remove. Repository-owner or administrator coordination and GitHub Support are still required. Do not use this repository as a secure vault.

## What the analysis says

On the figures available today, the largest number in the decision is the
property tax step-up at transfer, not the sale price and not the rent. The model
puts the annual bill on Property A at roughly eight times its current level if
the home is occupied as a principal residence, and roughly eleven times if it is
not. Every path has to be measured against that step.

The workspace deliberately does not rank the paths. It lists the condition that
would reverse each one and asks for the evidence that separates them first.

## Site contents

| Group | Pages |
| --- | --- |
| Start here | `index.html` (what changes the answer), executive summary |
| The decision | eight paths, questions and missing evidence, suggestions for review |
| The numbers | projections with what-if controls, property tax and assessment, operating costs |
| Stress tests | black swan regimes, Treasury staging tool |
| Law and process | estate tax thresholds, deadline timeline, law watchlist |
| Advisers and evidence | attorney and CPA brief, flagged for review, glossary, source register, privacy and limits |

Every data-table row carries an evidence badge and at least one official source
link. Values that could not be confirmed against an official page are left blank
or labeled for review. Blank means unknown, not zero.

Evidence labels: **Verified** (read from an official page), **Official** (statute
or agency rule), **Historical** (official historical observation),
**Owner-supplied** (from the owner's own records, not verified), **Projection**
(arithmetic on owner figures), **Assumption** (a modelling input),
**Not verified** (unknown).

## Build and check

```sh
python3 tools/build.py          # regenerate index.html, pages/ and the manifest
python3 tools/verify.py         # sourcing, rounding, link and privacy checks
python3 -m unittest discover -s tools -p 'test_*.py' -v
node tools/dom-test.cjs         # optional DOM and script check (needs jsdom)
node tools/browser-test.cjs     # optional Playwright layout check (needs browser deps)
```

`tools/engine_check.cjs` is run by the Python test suite. It fails the build if
the browser engine in `assets/app.js` and the Python engine in `tools/casedata.py`
ever disagree, so the shipped default tables and the live controls cannot drift
apart.

## Layout

- `tools/casedata.py` — anonymized working figures and the projection engine.
- `tools/sources.py` — the official source registry, each entry with the date it was read and the narrow scope it supports.
- `tools/sitebuild.py` — page builder.
- `tools/verify.py`, `tools/test_case.py` — checks and tests.
- `tools/site-manifest.json` — the exact list of published HTML outputs.
- `assets/` — local-only stylesheet and script. Review choices stay in the reader's browser; no input is transmitted or stored on a server.
- `COORDINATION.md` — the shared task board for parallel sessions.

## Rules for changing this repository

1. Never infer a value to fill a gap. Leave it blank and flag it.
2. Every table row needs a source link and an evidence badge.
3. Round owner figures to the nearest ten dollars.
4. Add a source only after reading the page, and write its scope as narrowly as the page supports.
5. Change `tools/casedata.py` and `assets/app.js` together; the parity test enforces it.
