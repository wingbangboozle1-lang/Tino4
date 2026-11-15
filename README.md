# Privacy-first inheritance decision workspace

This repository builds a static, source-linked decision framework for a home expected to transfer through a trust (Property A, planned around 2040–2050 as an owner planning window) and a separate already-owned home (Property B).

## Privacy and exposure — read first

Case figures appear on the website **only rounded to the nearest $10** — values, assessment and tax histories, rents, utility ranges and insurance estimates — each badged `Owner-supplied`, `Projection` or `Assumption`, never as officially verified. No name, address, postal code, parcel identifier, account number or document identifier is published; locations appear at city level only. The build enforces the rounding rule: any currency amount in public output that is not a multiple of $10 (apart from three explicitly allowed official agency figures) fails verification.

The repository is currently public. A `noindex` directive is not access control. Case-derived source and audit files have been removed from the current tree, but old Git commits, pull-request diffs, forks, caches and clones have **not** been scrubbed. Treat prior case data as exposed. Repository-owner/admin coordination is still required for any access restriction and supported history-cleanup process. Do not store deeds, trust documents, statements, tax bills, leases, utility bills, quotes or other identifying records in this repository.

## Site contents

- `index.html` — case snapshot, the conditional working recommendation with reinvestment risk stated in the headline, and the first-screen "what would change the answer" gates.
- `pages/` — 18 sections: executive summary, compare paths (pure and mixed, with quantified anchors), questions register, suggestions review queue, year-by-year projection scenarios, property-tax rules plus the rounded assessment/tax histories and rate-reconciliation flags, operating-cost pictures, black-swan regimes, the Treasury staging tool with a published worked example, estate thresholds with an illustrative tax table, the step-by-step deadline timeline and annual calendar, law watchlist, printable attorney/CPA brief, flagged-for-review register, glossary, source register with per-source check dates, and privacy limits.
- `assets/` — local-only stylesheet and JavaScript. Review choices stay in this browser; the investment scenario inputs are transient and are not transmitted or persisted.
- `tools/sitebuild.py` — page builder holding only pre-rounded owner figures; it reads no external household input at build time.
- `tools/site-manifest.json` — the exact list of public HTML outputs.
- `tools/verify.py` and `tools/test_case.py` — privacy, structure, link, sourcing, rounding and regression checks.
- `.github/workflows/verify.yml` — rebuilds and tests every change.

There is no household projection CSV. Projections are explicit scenario bands and tax-cap arithmetic, clearly badged, not forecasts.

## Build and verify

```sh
python3 tools/build.py
python3 tools/verify.py
python3 -m unittest discover -s tools -p 'test_*.py' -v
```

The site uses no remote scripts, fonts, images, APIs, analytics or form submission. Official links open only when a reader follows them. The calculator normalizes the starting portfolio to 100 units, uses historical drawdown endpoints with a clearly synthetic path, and defaults to dated reference Treasury yields with adjustable pre-crash drift and inflation assumptions. It is a stress illustration, not a historical backtest, forecast or personal investment recommendation.

## Evidence and limitations

- Current rules and public observations are linked to official IRS, California, county, Treasury, Federal Reserve, BLS, CBO, HUD, FHFA, CDI and San Francisco sources in the source register, each with its last fetch date.
- Every data-table row has a source link and an evidence-status label. Owner-supplied case rows link to the official verification portal, not to a claim of verification.
- The pages distinguish current law, official historical observations, owner-supplied figures, projections, assumptions and missing evidence. No proposal is treated as enacted law.
- Insurance premiums, Property A's rent, repair bids, the estate inventory and the transfer-date value cap remain unverified and are flagged on the Flagged for Review page.
- Re-check laws, deadlines, assessments, insurance availability and market inputs with qualified advisers and the relevant agencies at the actual transfer date.
