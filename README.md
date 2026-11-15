# Privacy-first inheritance decision workspace

This repository builds a static, source-linked decision framework for a home
expected to transfer through a trust (planning window 2040–2050) and a separate
already-owned 3-unit building. It compares occupy / rent / sell / mixed paths,
projects values, assessments, taxes and costs year by year, stress-tests
phased investing against historical crash anchors, and prepares a one-page
attorney and CPA briefing sheet.

## Privacy and exposure — read first

The generated website publishes **no property address, locality below metro
level, postal code, parcel identifier, name, account number or exact
pre-rounding figure**. Household and cost figures are rounded to the nearest
$10 (the owner's de-identification rule, enforced mechanically by
`tools/verify.py`); published statutory amounts (IRS thresholds, the BOE
Proposition 19 cap, utility tariff averages) appear exactly as published.
Estimates are shown as ranges. Property A (anticipated trust transfer) and
Property B (already owned) are analyzed as separate assets.

The repository is currently public. A `noindex` directive is not access
control. The current tree is clean, but old Git commits, pull-request diffs,
forks, caches and clones have **not** been scrubbed — treat prior pre-rounding
case data as exposed. The ready-to-run remediation is
`tools/history_scrub.sh` + `tools/history_scrub_runbook.md`; it requires
repository-owner/admin action (force-push coordination + GitHub Support for PR
diffs and caches) and a private archive first. Do not store deeds, trust
documents, statements, tax bills, leases, utility bills, quotes or other
identifying records in this repository.

## Site contents

- `index.html` — "What would change the answer" triage on the first screen.
- `pages/` — 18 sections: executive summary (with rounded numbers), path
  comparison with cash-flow bands, questions & missing evidence, suggestions
  review queue, year-by-year projection worksheet with post-transfer
  assessment branches, property-tax rules and cap history, operating costs and
  insurance, black-swan historical anchors and an illustrative irregular
  50-year path, Treasury staging tool with dollar view, estate-tax headroom
  and projected exclusions, inheritance process with a deadline timeline, law
  watchlist (with two verification corrections), printable attorney/CPA
  brief, flagged items, glossary, source register and privacy limits.
- `assets/` — local-only stylesheet and JavaScript. Review choices stay in
  this browser's local storage; calculator inputs are transient and are never
  transmitted or persisted.
- `tools/sitebuild.py`, `tools/sections.py`, `tools/models.py` — page builder,
  content sections and the projection engine. `models.py` holds only the
  rounded figures displayed on the site; the build reads no private inputs.
- `tools/verify.py` and `tools/test_case.py` — sourcing, privacy and the $10
  rounding rule (non-statutory currency amounts must be multiples of $10;
  statutory amounts are registered with their source).
- `tools/history_scrub.sh` + `tools/history_scrub_runbook.md` — owner-run
  history remediation (not yet executed).
- `.github/workflows/verify.yml` — rebuilds and tests every change.

## Build and verify

```sh
python3 tools/build.py
python3 tools/verify.py
python3 -m unittest discover -s tools -p 'test_*.py' -v
```

The site uses no remote scripts, fonts, images, APIs, analytics or form
submission. The staging tool normalizes capital to 100 units, calibrates
drawdowns to sourced historical endpoints (1929 Dow −89%; 2007–09 S&P −57%),
and includes adjustable yields, drift and inflation plus an optional dollar
view. It is a stress illustration, not a backtest, forecast or personal
investment recommendation.

## Evidence and limitations

- Every data-table row has an official source link and an evidence-status
  label (Verified / Owner-supplied / Projection / Assumption / Missing /
  Not verified / Guidance). The linked source supports only its stated scope.
- Case figures come from the owner's rounded descriptions ("Owner-supplied").
  Projections are computed from labeled scenario assumptions; none is a
  forecast. Future thresholds, caps and markets cannot be verified.
- Unconfirmable values are blank and flagged — never inferred. Failed
  official retrievals stay flagged in the source register.
- Two widely repeated claims failed official verification and are recorded as
  corrections: the 2026 Prop 19 repeal initiative officially failed (SOS memo,
  May 2026), and SCA-4 is a veterans' exemption measure, not parent-child
  relief.
- Re-check laws, deadlines, assessments, insurance availability and market
  inputs with qualified advisers at the actual transfer date.
