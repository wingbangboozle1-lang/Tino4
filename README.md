# Privacy-first inheritance decision guide

This repository builds a public, source-linked guide to inheritance planning, property-tax rules, rental and sale considerations, investment-sequence risk, and adviser questions. It deliberately does **not** publish or store household-specific property locations, valuations, tax histories, rents, leases, insurance information, identities, or recommendations.

## Privacy boundary — highest priority

- Keep deeds, trusts, tax returns, parcel identifiers, account numbers, leases, insurance declarations, utility bills, appraisals, quotes and adviser correspondence outside this repository.
- Public pages use generic roles and official rules only. There is no private input file or household-specific projection in the active build.
- Browser what-if values run in memory only. The site has no remote scripts, forms, analytics, network calls, or browser storage. Refresh the page to clear entered values.
- A working-tree cleanup cannot erase earlier public commits, pull-request diffs, forks, caches, downloads, or clones. The historical exposure remains unresolved and must be treated as potentially retained. Repository administrators should assess visibility and history remediation; preserve a private encrypted archive before any destructive history action.
- **Enforcement is mechanical, not editorial.** The verifier scans every tracked text file — not only the built pages — for comma-grouped amounts that are neither $10-rounded nor registered official figures, for rounded-to-unrounded mapping patterns, and for a committed redaction-rules file. That is what catches a figure written into a script or a note, which a page-level check misses. A figure-free history-rewrite runbook lives in `tools/`; the rules file itself must stay outside every clone.
- **Open decision, recorded on the site:** an owner instruction asked for decision-driving figures to be published rounded to the nearest ten dollars, and a layer was built that way. The containment policy now in force publishes no household figures at all, and its release check rejects the badge such rows would carry. The two cannot both hold on one public page; the choice is recorded and dated in the decision log rather than made silently.
- Public GitHub Pages and a private family case file are different products. Do not place confidential case records in the public site or repository.

## Site map

The 22 generated pages carry the official rules a household comparison has to satisfy — depreciation and its recapture, the transfer-tax tier method and recording charges, the home-sale exclusion's occupancy conditions, like-kind exchange scope, the imputed-rent and rent-comparable evidence standard, a five-year capital plan, estate liquidity and portability prompts, and a published re-check cadence — each row linked to its source and badged. They group the work into executive/decision summaries, the full requirements tracker, private inventory and cost checklists, property-tax and estate law, deadlines, black-swan conditions, Treasury staging, a draft investment policy, adviser handoff, questions, suggestions, a decision log, a glossary, source register, privacy limits and flagged items.

The homepage puts **what would change the answer** on the first screen. The project does not choose a household path from absent or unverified evidence. The comparison framework covers live, rent, sell in the transfer year, live-then-sell, mixed paths, and sell-and-reinvest; it requires identical transfer dates and horizons, with taxes, debt, occupancy, costs, liquidity and reinvestment risk treated explicitly.

## Build and verify

```sh
python3 tools/build.py
python3 tools/verify.py
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/recheck.py            # MOVED or UNCHANGED for the published evidence layer
node tools/dom-test.cjs             # optional: npm install --no-save jsdom
```

`tools/recheck.py` exists for one reason: an input change must be reported as a change to what the framework
asserts, not absorbed silently as a passing build. It rebuilds, verifies, and compares a committed fingerprint
(`tools/framework-snapshot.json`: page count, data-row count, badge counts, the source register, and a hash of
the rendered pages) against the current state. `MOVED` means the affected pages must be re-read before an
earlier conclusion is repeated; then accept the reviewed state with `--update`. It can also diff a *private*
model's ranking — `--private-model ../somewhere-outside-this-repo/model.json` — printing only whether the
order changed, never the figures.

CI rebuilds and verifies the generated site. The verifier checks the page manifest, source and evidence badge on every table row, source-host allowlist, local links, CSP/noindex, source currency, and that active builder code contains no household model inputs.

## Evidence standard

Official sources establish only the narrow rule or public information stated beside each link. They do not verify private title, eligibility, assessment, valuation, tax basis, rental legality, costs or insurance coverage. Missing and unverified items are labeled and given a next step. Future laws, economic paths, insurance costs, rents and returns are not presented as official forecasts.

## Important limits

This is general research, not legal, tax, appraisal, insurance, investment or property-management advice. Recheck current law and official deadlines with qualified advisers at the actual transfer date. Use a private, access-controlled, offline model for household figures, after-tax scenarios and final decisions.
