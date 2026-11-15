# Privacy-first inheritance decision workspace

This repository builds a static, source-linked decision framework for a home expected to transfer through a trust and a separate already-owned home. The long-range transfer window is intentionally not disclosed in the public version and is not a confirmed date or legal forecast.

## Privacy and exposure — read first

The generated website is generic. It does not publish a property address, locality, parcel identifier, private valuation, assessment, rent, lease, utility bill, insurance premium, repair estimate, household tax projection or property-specific recommendation. Unknown values are left blank and labeled for review. Property A (anticipated trust transfer) and Property B (already owned) are analyzed as separate assets.

What the site *does* publish is public market and statutory information that is available to everyone: Treasury constant-maturity yields, state house-price index changes, inflation observations, federal estate-tax thresholds and California statutes. Those figures are dated observations with an explicit check date, not forecasts and not household facts.

The repository is currently public. A `noindex` directive is not access control. The published branch history has been rewritten so that no commit reachable from the branch contains the earlier case-derived material, but a branch rewrite cannot retract pull-request diffs, forks, cached views or clones that already copied the material. Repository-owner/admin coordination and a GitHub Support request are still required to purge those copies, and the owner should decide whether the repository should be private. Do not store deeds, trust documents, statements, tax bills, leases, utility bills, quotes or other identifying records in this repository.

## Site contents

- `index.html` — decision-changing facts and next steps.
- `pages/` — 18 sections covering the executive summary, live/rent/sell/mixed paths, conditional decision logic, missing facts, blank projection scenarios with official benchmark inputs, California property-tax rules, operating costs, historical stress regimes, the 3M-to-2Y Treasury staging tool, legal thresholds and deadlines, law watchlist, the attorney and tax-adviser brief, flagged items, glossary, source register and privacy limits.
- `assets/` — local-only stylesheet and JavaScript. Review choices stay in this browser; the investment scenario inputs are transient and are not transmitted or persisted.
- `tools/sitebuild.py` — generic page builder. It does not import or read household inputs.
- `tools/site-manifest.json` — the exact list of public HTML outputs.
- `tools/verify.py` and `tools/test_case.py` — privacy, structure, link, sourcing and regression checks.
- `.github/workflows/verify.yml` — rebuilds and tests every change.

There is no household projection CSV or personalized numeric forecast in the public output. The projection worksheet provides blank early/midpoint/late scenario cells and formulas only; a useful private forecast requires the actual trust, appraisal, tax, lease, insurance and operating records.

## Build and verify

```sh
python3 tools/build.py
python3 tools/verify.py
python3 -m unittest discover -s tools -p 'test_*.py' -v
```

The site uses no remote scripts, fonts, images, APIs, analytics or form submission. Official links open only when a reader follows them. The calculator normalizes the starting portfolio to 100 units, splits the parking period between 2-year notes and rolling 3-month bills, uses historical drawdown endpoints with a clearly synthetic path, and includes adjustable yields, ladder mix, pre-crash drift, a renewal-yield stress and inflation assumptions. It is a stress illustration, not a historical backtest, forecast or personal investment recommendation.

## Evidence and limitations

- Every data-table row has a source link and an evidence-status label, and the source register records the check date and the narrow scope each source supports.
- Current rules and public history are linked to official IRS, California, Treasury, Federal Reserve, BLS, CBO, HUD, FHFA, SEC and GitHub sources in the source register.
- The pages distinguish current law, official historical observations, assumptions and missing evidence. No proposal is treated as enacted law.
- Local rent rules, property-tax bills, insurance, utility and building requirements cannot be verified without a private jurisdiction and property records; they remain flagged rather than inferred.
- Re-check laws, deadlines, assessments, insurance availability and market inputs with qualified advisers and the relevant agencies at the actual transfer date.
