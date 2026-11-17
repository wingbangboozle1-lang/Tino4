# Privacy-first inheritance decision guide

This repository builds a public, source-linked guide to inheritance planning, property-tax rules, rental and sale considerations, investment-sequence risk, and adviser questions. It publishes a full scenario model so the arithmetic can be checked line by line, while publishing **no** property location, address, parcel identifier, account number, lease text, insurance declaration, identity, or household dollar value.

## Unit-dollar publication policy — highest priority

- Rounding to a nice number is not anonymization: county assessment rolls are public and searchable, so a rounded assessed value still narrows a county's parcels to a handful. Property-specific amounts are therefore published in **unit dollars** — dollars per $1,000,000 of the household's 2026 baseline value — together with the ratios (percent of value, multiples, break-even growth rates) that actually decide the question. A reader multiplies a unit figure by their own value divided by one million to get their own dollars; the ranking is unchanged because every line scales together.
- No household dollar value, assessed value, bill, rent, premium or repair quote appears in any page, commit message, or pull-request text. The local what-if tools compute in real dollars from figures the user types in, in memory only.
- Amounts published by an official source (the federal exclusion, the section 121 exclusion, the Proposition 19 indexed limit, the state thresholds) appear in their exact published form so a reader can compare a page against the issuing authority directly. `tools/verify.py` fails the build on any currency amount that is neither one of those official amounts (`OFFICIAL_AMOUNTS`) nor a multiple of ten dollars, and `tools/test_case.py` scans every tracked file for the household's value shapes and identifiers.
- Identifiers never enter the model or the site: locality, address, parcel, account, policy, and party names belong in a private workpaper. The generator embeds no data file and reads none; the verifier also fails the build on postal-like, phone, email, and street patterns, and on non-visible attributes or HTML comments.
- Exact records — the household's own dollar figures, the roll values, the rate-area reading, quotes and the estate inventory — live in `private-work/` and `private-data/`, both git-ignored, plus the owner's encrypted offline store. Nothing in either directory may be copied into a page, a commit message, a pull-request body, or an issue comment.
- Assumption rates are labelled as assumptions wherever they print (value growth, cost inflation, gross rent yield, portfolio return, tax drag, reserve yield). An item no official source supports is flagged on the "Flagged for review" page with the specific act that would settle it; it never becomes a headline figure.
- `python3 tools/recheck.py --update` accepts a changed evidence layer into `tools/framework-snapshot.json`; the recheck run states whether the published layer moved (row counts, badge mix, site hash) rather than only whether the build passed. Accepting a new baseline is the recorded act of review, so it goes in the same commit as the change and the decision-log entry.
- Keep deeds, trusts, tax returns, parcel identifiers, account numbers, leases, insurance declarations, utility bills, appraisals, quotes and adviser correspondence outside this repository.
- Browser what-if tools run in memory only; they compute in real dollars from figures the person at the keyboard types in, round their own output to the nearest ten dollars, and never store or transmit it. The site has no remote scripts, forms, analytics, network calls, or browser storage; refresh clears entered values.
- A working-tree cleanup cannot erase earlier public commits, pull-request diffs, forks, caches, downloads, or clones, which contain drafts from before this policy. The historical exposure remains unresolved and must be treated as potentially retained. Repository administrators should assess visibility and history remediation; preserve a private encrypted archive before any destructive history action.
- Browser what-if values run in memory only. The site has no remote scripts, forms, analytics, network calls, or browser storage. Refresh the page to clear entered values.
- **Measured on 2026-11-17:** identifying material was reachable in 82 of 87 refs, in up to 94 files on one ref and as deep as 47 commits on another, in a public repository with five open pull requests (four unrelated to `main`, since closed). This is the highest-urgency open item and it is an owner decision, not a code change.
- **Rounding to the nearest $10 is not anonymization.** County assessment rolls are public and searchable, so a rounded assessed value still narrows a county to a handful of parcels. The working rule is that no assessor-derived amount is published at all; the amount stays in the offline workpaper.
- Public GitHub Pages and a private family case file are different products. Do not place confidential case records in the public site or repository.

## Site map

The 24 generated pages group the work into executive/decision summaries, the full requirements tracker, private inventory and cost checklists, property-tax and estate law, dated official-figure lookups, deadlines, black-swan conditions, Treasury staging, a draft investment policy, adviser handoff, questions, suggestions, a decision log, a glossary, source register, privacy limits and flagged items.

- Public pages use generic roles and official rules only. There is no private input file or household-specific projection in the active build.
- Browser what-if values run in memory only. The site has no remote scripts, forms, analytics, network calls, or browser storage. Refresh the page to clear entered values.
- A working-tree cleanup cannot erase earlier public commits, pull-request diffs, forks, caches, downloads, or clones. The historical exposure remains unresolved and must be treated as potentially retained. Repository administrators should assess visibility and history remediation; preserve a private encrypted archive before any destructive history action.
- **Measured on 2026-11-17:** identifying material was reachable in 82 of 87 refs, in up to 94 files on one ref and as deep as 47 commits on another, in a public repository with five open pull requests (four unrelated to `main`, since closed). This is the highest-urgency open item and it is an owner decision, not a code change.
- **Rounding to the nearest $10 is not anonymization.** County assessment rolls are public and searchable, so a rounded assessed value still narrows a county to a handful of parcels. The working rule is that no assessor-derived amount is published at all; the amount stays in the offline workpaper.

- Browser what-if tools run in memory only; they compute in real dollars from figures the person at the keyboard types in, round their own output to the nearest ten dollars, and never store or transmit it. The site has no remote scripts, forms, analytics, network calls, or browser storage; refresh clears entered values.
- A working-tree cleanup cannot erase earlier public commits, pull-request diffs, forks, caches, downloads, or clones, which contain drafts from before this policy. The historical exposure remains unresolved and must be treated as potentially retained. Repository administrators should assess visibility and history remediation; preserve a private encrypted archive before any destructive history action.

## Build and verify

```sh
python3 tools/build.py
python3 tools/verify.py
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/recheck.py    # rebuilds and reports whether the evidence layer moved
python3 tools/privacy_scan.py   # read-only exposure audit, prints counts only
```

- Browser what-if tools run in memory only; they compute in real dollars from figures the person at the keyboard types in, round their own output to the nearest ten dollars, and never store or transmit it. The site has no remote scripts, forms, analytics, network calls, or browser storage; refresh clears entered values.
- A working-tree cleanup cannot erase earlier public commits, pull-request diffs, forks, caches, downloads, or clones, which contain drafts from before this policy. The historical exposure remains unresolved and must be treated as potentially retained. Repository administrators should assess visibility and history remediation; preserve a private encrypted archive before any destructive history action.
- Public pages use generic roles and official rules only. There is no private input file or household-specific projection in the active build.
- Browser what-if values run in memory only. The site has no remote scripts, forms, analytics, network calls, or browser storage. Refresh the page to clear entered values.
- A working-tree cleanup cannot erase earlier public commits, pull-request diffs, forks, caches, downloads, or clones. The historical exposure remains unresolved and must be treated as potentially retained. Repository administrators should assess visibility and history remediation; preserve a private encrypted archive before any destructive history action.
- **Measured on 2026-11-17:** identifying material was reachable in 82 of 87 refs, in up to 94 files on one ref and as deep as 47 commits on another, in a public repository with five open pull requests (four unrelated to `main`, since closed). This is the highest-urgency open item and it is an owner decision, not a code change.
- **Rounding to the nearest $10 is not anonymization.** County assessment rolls are public and searchable, so a rounded assessed value still narrows a county to a handful of parcels. The working rule is that no assessor-derived amount is published at all; the amount stays in the offline workpaper.

## Evidence standard

Official sources establish only the narrow rule or public information stated beside each link. They do not verify private title, eligibility, assessment, valuation, tax basis, rental legality, costs or insurance coverage. Missing and unverified items are labeled and given a next step. Future laws, economic paths, insurance costs, rents and returns are not presented as official forecasts.

## Important limits

This is general research, not legal, tax, appraisal, insurance, investment or property-management advice. Recheck current law and official deadlines with qualified advisers at the actual transfer date. Use a private, access-controlled, offline model for household figures, after-tax scenarios and final decisions.
