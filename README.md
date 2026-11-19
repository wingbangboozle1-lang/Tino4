# Privacy-first inheritance decision guide

This repository builds a public, source-linked guide to inheritance planning, property-tax rules, rental and sale considerations, investment-sequence risk, and adviser questions. It is a generic educational framework, not a household case file or recommendation.

## Privacy boundary

- No household inputs, property locations, valuations, tax histories, rents, leases, insurance details, identities, private documents or case-specific recommendations belong in this repository or public site.
- Do not treat anonymized or rounded private figures as safe to publish. Public records and combinations of facts can make them identifiable.
- Store deeds, trusts, tax returns, account records, leases, policies, utility bills, appraisals, quotes and adviser correspondence only in an access-controlled private location outside Git.
- Browser what-if tools operate locally in memory. The site contains no analytics or remote scripts, and no browser storage. Refresh to clear entered values; do not enter sensitive information on shared devices.
- `tools/sitebuild.py` contains generic guidance and official-source links only. It does not import a household model or read a private input file.
- A current-tree cleanup cannot erase earlier commits, pull-request views, forks, caches, downloads or clones. Historical exposure must be treated as potentially retained and assessed by repository administrators. See `tools/history_scrub_runbook.md`.

## Site map

The 26 pages group executive and decision summaries, the requirements tracker, private-inventory and cost checklists, property-tax and estate law, deadlines, black-swan conditions, Treasury staging, an investment-policy draft, adviser handoff, questions, suggestions, a decision log, glossary, source register, privacy limits and flagged items.

The public guide does not rank household choices or publish property-specific projections. It explains which evidence a private analysis needs and how to compare pure and mixed choices at the same transfer dates and horizons. Separate estate tax, income-tax basis and property-tax assessment. Include debt, occupancy, capital costs, taxes, liquidity, imputed rent and reinvestment risk in any private comparison. Use ranges, identify assumptions, and agree decision rules before revealing projected outcomes.

## Build and verify

```sh
python3 tools/build.py
python3 tools/verify.py
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/recheck.py
python3 tools/privacy_scan.py
```

`tools/verify.py` checks the generated page manifest, official source links and evidence badges on every table row, source-host allowlist, local links, restrictive CSP/noindex, currency formatting, and absence of browser storage, network calls and remote resources. The build never reads a household input file.

`tools/recheck.py` fingerprints the public evidence layer and reports whether it moved. It can optionally compare the ordering in an offline model file located outside this repository, without printing its figures; do not provide a private-model path in a shared environment.

`tools/privacy_scan.py` is a read-only Git-history audit. Its findings do not prove third-party copies have been erased. A passing current-tree build is not history remediation.

## Evidence standard and limits

Official sources establish only the narrow rule or public information stated beside each link. They do not establish private title, eligibility, assessment, valuation, tax basis, rental legality, costs or insurance coverage. Missing or unverified items are left unfilled and paired with a next step. Future laws, economic paths, rents, premiums and returns are not presented as official forecasts.

This guide is general research, not legal, tax, appraisal, insurance, investment or property-management advice. Recheck authorities and deadlines at the actual transfer date with qualified advisers.
