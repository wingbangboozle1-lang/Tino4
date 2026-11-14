# Private decision framework

A static GitHub Pages framework for organizing an anticipated trust inheritance and a separately owned rental property. The public site is intentionally generic: it does not publish the household's figures, addresses, location history, or individualized recommendation.

**Important privacy warning:** the repository is public. Legacy source/model files in excluded directories still contain rounded household-specific inputs, and earlier Git history or pull-request diffs may contain older details. Jekyll exclusions only affect what is built into Pages; they do not make repository files private. Do not add deeds, trust documents, tax bills, account details, parcel records, or other personal information. See [Privacy and limitations](pages/privacy.html), [Flagged for review](pages/flagged-for-review.html), and the internal audit record at `_2c2d483d/privacy-review.md`. The current site has been generalized, but repository and history remediation is not complete.

## Public site

| Path | Purpose |
| --- | --- |
| `index.html` | Decision gates, separation of the future inheritance from the already-owned property, and links to the checklist |
| `pages/attorney-cpa-brief.html` | Printable adviser-meeting checklist; use the browser's Print or Save as PDF |
| `pages/phased-investing.html` | General 24–36 month Treasury-staging and phased-stock-entry framework; no household inputs or return forecast |
| `pages/deadline-timeline.html` | Source-linked statutory deadlines and flagged items to confirm |
| `pages/glossary.html` | Plain-language definitions |
| `pages/suggestions.html` | Review-only improvements; no suggestions are applied automatically |
| `pages/what-we-need.html` | Questions and documents needed before a decision |
| `pages/privacy.html`, `pages/flagged-for-review.html` | Privacy boundary and unresolved items |

The public site makes no household-specific tax or investment recommendation and publishes no property projection CSV. The phased-investing page describes scenarios and risks; it is not an interactive personalized calculator and does not claim to replay historical 1929 or 2008 portfolio returns.

## Build and checks

```sh
python3 tools/build.py
python3 tools/verify.py
python3 -m unittest discover -s tools -p 'test_*.py' -v
```

The build uses Python's standard library. The verifier checks the published HTML boundary and confirms that no case-projection CSV is generated. These checks do not prove that every law is current, every source supports each sentence, that the repository is anonymous, or that historical Git objects have been erased.

## Research and decision limitations

- The current site keeps the future trust transfer distinct from the property already owned by the inheritor.
- Trust terms, date-of-death basis, tax filing obligations, local property-tax administration, insurance availability, legal unit status, leases, utilities, repairs, and the total estate are facts to establish from private records and qualified advisers.
- Rules and thresholds can change before the anticipated transfer. Confirm them with current official sources and counsel at the relevant time.
- This is a planning framework, not legal, tax, insurance, appraisal, or investment advice.
