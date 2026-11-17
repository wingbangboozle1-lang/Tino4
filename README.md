# Privacy-first inheritance decision guide

This repository builds a public, source-linked guide to inheritance planning, property-tax rules, rental and sale considerations, investment-sequence risk, and adviser questions. It deliberately does **not** publish or store household-specific property locations, valuations, tax histories, rents, leases, insurance information, identities, or recommendations.

## Privacy boundary — highest priority

- Keep deeds, trusts, tax returns, parcel identifiers, account numbers, leases, insurance declarations, utility bills, appraisals, quotes and adviser correspondence outside this repository.
- Public pages use generic roles and official rules only. There is no private input file or household-specific projection in the active build.
- Browser what-if values run in memory only. The site has no remote scripts, forms, analytics, network calls, or browser storage. Refresh the page to clear entered values.
- A working-tree cleanup cannot erase earlier public commits, pull-request diffs, forks, caches, downloads, or clones. The historical exposure remains unresolved and must be treated as potentially retained. Repository administrators should assess visibility and history remediation; preserve a private encrypted archive before any destructive history action.
- **Measured on 2026-11-17:** identifying material was reachable in 82 of 87 refs, in up to 94 files on one ref and as deep as 47 commits on another, in a public repository with five open pull requests (four unrelated to `main`, since closed). This is the highest-urgency open item and it is an owner decision, not a code change.
- **Rounding to the nearest $10 is not anonymization.** County assessment rolls are public and searchable, so a rounded assessed value still narrows a county to a handful of parcels. The working rule is that no assessor-derived amount is published at all; the amount stays in the offline workpaper.
- Public GitHub Pages and a private family case file are different products. Do not place confidential case records in the public site or repository.

## Site map

The 24 generated pages group the work into executive/decision summaries, the full requirements tracker, private inventory and cost checklists, property-tax and estate law, dated official-figure lookups, deadlines, black-swan conditions, Treasury staging, a draft investment policy, adviser handoff, questions, suggestions, a decision log, a glossary, source register, privacy limits and flagged items.

Two pages carry most of the analytical weight:

- **Verified lookups** records every headline figure with the date it was read from the issuing authority and the words that establish it, plus what is deliberately left blank.
- **Treasury staging tool** tests whether 24-36 months of Treasury staging softens a 1929- or 2008-shaped crash, across nine fixed published scenarios evaluated at the same date, with a distribution chart. It states the trade-off rather than a recommendation: staging protects against an early crash and costs the equity-minus-Treasury spread when markets rise.

The homepage puts **what would change the answer** on the first screen and explains in plain language why a missing fact is shown as missing rather than filled in. The break-even page reduces the biggest unknown to a single figure that written market comparables can settle. The project does not choose a household path from absent or unverified evidence. The comparison framework covers live, rent, sell in the transfer year, live-then-sell, mixed paths, and sell-and-reinvest; it requires identical transfer dates and horizons, with taxes, debt, occupancy, costs, liquidity and reinvestment risk treated explicitly.

## Build and verify

```sh
python3 tools/build.py
python3 tools/verify.py
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/recheck.py    # rebuilds and reports whether the evidence layer moved
python3 tools/privacy_scan.py   # read-only exposure audit, prints counts only
```

CI rebuilds and verifies the generated site. The verifier checks the page manifest, source and evidence badge on every table row, source-host allowlist, local links, CSP/noindex, source currency, and that active builder code contains no household model inputs. It also fails on any currency amount that is not on the reviewed list, so adding a figure requires adding a source and a read date.

`tools/recheck.py` exists because a passing build is not the same as an unchanged answer. It fingerprints the published evidence layer and prints UNCHANGED or MOVED with the aspects that changed, so the standing instruction "rebuild after any input change and say whether the recommendation moved" is executable rather than aspirational.

`tools/privacy_scan.py` is read-only and deliberately non-printing: it reports which refs contain identifying material, as counts, refs and paths only, never the values. Its own pattern list is encoded so the tool does not republish what it searches for.

## Evidence standard

Official sources establish only the narrow rule or public information stated beside each link. They do not verify private title, eligibility, assessment, valuation, tax basis, rental legality, costs or insurance coverage. Missing and unverified items are labeled and given a next step. Future laws, economic paths, insurance costs, rents and returns are not presented as official forecasts.

## Important limits

This is general research, not legal, tax, appraisal, insurance, investment or property-management advice. Recheck current law and official deadlines with qualified advisers at the actual transfer date. Use a private, access-controlled, offline model for household figures, after-tax scenarios and final decisions.
