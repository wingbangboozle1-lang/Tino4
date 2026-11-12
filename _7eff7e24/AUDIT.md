# Integration audit — arena-7eff7e24

Checked 2026-11-12. Scope: current public product, public build dependency chain, evidence
claims retained in this replacement, synthetic arithmetic, publication boundary and integration.
This is **not** certification of every historical repository line or every page of long legal
publications. No private parcel, address, beneficiary or account research was conducted.

## Findings and corrections

1. The original public build read `_c07ccf45/data/inputs.json` and emitted a recognizable combination
   of household value, assessment, tax, rent and utility history. Its original privacy page said
   rounding removed an exact search match and noindex kept the model out of search results.
   Neither establishes anonymity or confidentiality. The repository API confirms public visibility.
   The new build reads only generic content, official passages and fictional model constants.
   Existing case-derived packages are removed from the current tree. History and prior PR diffs
   remain; no claim that old disclosures were purged. F01/F02 and Privacy explain this.
2. Original `pages/executive-summary.html` said an appraisal “locks the basis that makes the sale
   tax-free.” IRS inherited-property FAQ explicitly says a sale above basis has a taxable gain.
   An appraisal documents value; it does not stop appreciation or guarantee a tax-free sale.
   Replaced with conditional basis treatment and seller/estate review requirements.
3. Original summary described B's tax base as “permanently low.” BOE Publication 29 describes
   reassessment on ownership change/new construction; law can also change. Replaced with the
   distinction that A's inheritance alone does not re-inherit B, without permanent guarantees.
4. Original summary told the owner to claim a 1.6% rent increase “each year.” The directly checked
   Rent Board page specifies March 2026–February 2027 only, and posts a November 9 proposal
   (File 261020) that is NOT enacted. The new law-watch page separates these statuses.
5. Original model/cross-audit treated two rental units out of three as an automatic 2/3 expense
   allocation. Unit count alone does not establish the allocation. IRS Publication 527 requires
   separating rental and personal expenses. Q11/Q14 request actual use/lease/tax evidence.
6. Original site's source-per-row and rounding checks could pass while unsupported insurance,
   utility and forward returns were published as household conclusions. The new status labels
   distinguish directly checked official statements, analytical guidance, missing facts and
   invented examples. Every actual household numeric estimate remains blank. Source links on
   synthetic/guidance rows are explicitly contextual, not support for invented parameters.
7. Rechecked current IRS exclusion figures, Form 706 whole-estate and filing/payment rules,
   inherited basis, BOE Prop. 19 residence/value/claim rules, California death-tax prohibition,
   and the RTC 13302 pickup exception together with Controller post-2004 filing guidance.
   Exact current Prop. 19 allowance is not used as a 2045 forecast. $10-rounded statutory displays
   are explicitly not filing values. Only 29 retained source scopes are described as verified.
8. Several routes returned error/maintenance content despite successful retrieval status. The
   ledger records failures. No FHFA local return series/backtest was independently confirmed;
   earlier success probabilities and modeled ranks are not carried forward as verified facts.
9. The example model is deliberately synthetic, not a private-tax engine. Rates, costs, return
   paths and underwriting are invented. It omits actual brackets, NIIT stacking, SALT, debt,
   estate allocation, half-month depreciation, withdrawals and local charges. All omissions
   are visible. Terminal tax and nominal/real arithmetic have separate unit tests.

## Concurrent integration — PRs #40–43

During this session, main advanced from `26697d8` to `92c8f3d`. Other sessions had added
Suggestions/Open Questions and board-only records. Their shared-output tasks are done or
superseded; only deployment-log scopes remained in progress. Read all new board entries and
new generator content before reconciliation.

Preserved useful substance, with source/privacy corrections:

* Six financial suggestions SUG-01 through SUG-06 are retained as conditional review choices:
  equity, balanced, bills/cash, rent A, occupy A/rent available B space, occupy A/personal B use.
  No unsupported household wealth rank, quote, universal allocation or “never choose” verdict.
* Site improvement ideas retained: private evidence/readiness workflow, year/path selector,
  decision gates, sensitivity display, separate financial/product suggestions and meeting brief.
* Questions inventory expanded to 16 accountable evidence tasks; inheritance deadline workflow
  retained. Old `pages/open-questions.html` URL redirects to `pages/questions.html`.
* A8F's source-label concern IR-019 is resolved by blank unverified utility cells; CPUC links
  support tariff mechanics, not household bills. History concern IR-018 remains open as F01.
* Other sessions' task-board records preserved verbatim. No branch switching or force-push.

## Verification limits

All 29 retained official source scopes were directly read using fetch_page; retrieval chunks and
short excerpts are in `evidence.py`. No statement that the entire IRS/BOE publications or every
pending bill was exhaustively audited. The public missing-evidence and flags pages disclose
this limit. Authorized private documents, insurance underwriting and future law cannot be
verified from these public sources alone.

Technical checks: deterministic build; internal target/anchor resolution; each table body row
has a registered official URL and status; visible identifier/rounding checks; 561 synthetic CSV
rows (11 transfer years × 51 endpoints); publication exclusions; 13 independent arithmetic and
content tests; JavaScript syntax check; Chromium desktop/mobile navigation and interactive
review/reset/year-selector smoke tests. Browser test dependencies are optional and ignored,
not part of the static product or Python build. No third-party browser requests observed.
