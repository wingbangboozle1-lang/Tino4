# A562 privacy-first public-site audit

**Audit date:** 2026-11-14 UTC  
**Status:** privacy containment prepared on the Arena-fixed branch; merge and post-merge Pages verification still required.  
**Scope:** current public Pages output, its generator/checks, the source links used by the generic pages, phased-investing wording, deadline timeline, and deployment. No household values or identifiers are reproduced here.

## Executive result

The post-PR #65 generic publication was privacy-conscious and reproducible, but PR #71 subsequently merged a case-specific publication regression. PR #71 merged as `6815e458d13658810c903d8a5919d37a9222e5a1`; its Pages workflow completed successfully and the Pages API reported `built` for that commit. A live fetch showed owner-supplied property/tax/rent details, an individualized decision statement, and case-oriented pages in the public output. The required verification workflow for that commit failed in its unit/regression-test step before build/verify ran.

I created a normal revert of the PR #71 merge on this feature branch (`8ead1ba`), restoring its first-parent generic baseline (`78fc323`) without rewriting history or adding any household data. That reverted tree builds a generic site, verifies **9 public HTML files and no case-projection CSV**, and passes the one-test generic privacy suite. It is not yet the live `main` site; do not treat Pages privacy as restored until the revert PR is merged and a cache-busted live fetch confirms it.

A revert cannot remove the now-public merge, PR diff, prior Git objects, forks, caches, or clones. No history scrub is claimed or attempted. Legacy source/model files containing case-derived inputs remain in the public working tree; the generic site warns about that exposure. Repository/history remediation remains unresolved and needs repository-owner coordination.

## Verified artifact, privacy, and test results

- The generic generator states that it does not read household inputs or case projections. Running `python3 tools/build.py` succeeded and reproduced the generic output.
- `python3 tools/verify.py` passed: 9 public HTML files; no projection CSV. `python3 -m unittest discover -s tools -p 'test_*.py' -v` passed the one generic privacy regression test. `node --check assets/app.js`, `node --check tools/browser-test.cjs`, and `git diff --check` also passed.
- The generic output keeps the anticipated inheritance distinct from the separately owned property and uses no individualized values, rents, expense history, forecasts, or recommendation. The phased-investing page presents a general 24–36-month Treasury-staging comparison as a framework, not a calculator or return forecast.
- The generic phased page asks for historical crash-entry and inflation stress tests; it does **not** contain results of those tests or a verified historical total-return replay. Do not describe the current generic page as a 1929/2008 replay. No such analysis was added here.
- Current generated HTML is checked by the build/verifier/test. This does not make the repository private: legacy source/model files remain tracked and accessible, and Git history/PRs are separate from Pages output.
- The broader 29-test suite introduced on PR #71 was run locally against that merged tree: 28 tests passed and one failed in `test_published_pages_have_no_exact_source_figures`, because the parser treated an official threshold abbreviated in millions as a literal two-digit dollar amount. The main-branch Actions run failed at “Unit and regression tests.” This was a test-format false positive, not evidence that the generic baseline passed PR #71's privacy regression. The reverted baseline uses its existing generic privacy test; this audit does not claim 29 tests pass.
- No browser smoke test was run. No personalized financial or legal analysis was performed.

## Source-link and wording check

The current generic HTML contains four recurring official starting links plus the timeline's direct links. Each was fetched and its content/title was checked; this is a content-retrieval check, not a raw HTTP-status scanner. The generic site has no case-specific fact table or individualized source-status rows.

| Page claim / use | Official source checked | Result |
| --- | --- | --- |
| Proposition 19 overview and claim period | [California BOE Proposition 19](https://www.boe.ca.gov/prop19/) | Official page retrieved. It says the homeowners' exemption is filed within one year and the exclusion claim within three years or before transfer to a third party. |
| Federal estate-tax scope and current filing threshold | [IRS Estate Tax](https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax) | Official page retrieved; it distinguishes the filing threshold from the amount an heir receives and includes the current-year table. Later-year law remains unknown. |
| Form 706 overview | [IRS About Form 706](https://www.irs.gov/forms-pubs/about-form-706) | Official page retrieved and links to the current instructions. |
| Form 706 deadline and extension wording | [IRS Instructions for Form 706 (July 2026)](https://www.irs.gov/pub/irs-pdf/i706.pdf), [About Form 4768](https://www.irs.gov/forms-pubs/about-form-4768), and [IRS Instructions for Form 4768 (February 2020)](https://www.irs.gov/pub/irs-pdf/i4768.pdf) | The 706 instructions support filing and payment within nine months and an automatic six-month filing extension. IRS describes a separate payment-extension request on Form 4768; the available Form 4768 instructions are dated 2020, so re-check them before any future action. The event date and future law are not known. |
| Treasury-bill framework | [TreasuryDirect Treasury Bills](https://www.treasurydirect.gov/marketable-securities/treasury-bills/) | Official page retrieved. It describes bill maturities, auction-fixed rates, holding/selling, and tax treatment; it does not support a future yield or equity-return assumption. The generic page makes no such forecast. |
| Date-of-death property-tax change, 150-day reporting, occupancy condition, appeal window, installment dates | [BOE Information Sheet 800-9](https://www.boe.ca.gov/pdf/pub800-9.pdf) | Official PDF retrieved. The relevant sections support the timeline's date-of-death rule, reporting/occupancy deadlines, appeal timing, and installment/penalty wording. |
| Trustee notice | [California Probate Code §16061.7](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum=16061.7) | Official code retrieved; subdivision (f) states the 60-day service period, subject to the statute's stated qualifications. |
| Change-in-ownership statement | [California Revenue & Taxation Code §480](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=480) | Official code retrieved; subdivision (b) states the death-transfer reporting period and probate exception. |
| California death/inheritance tax statement used in the audit context | [California Revenue & Taxation Code §13301](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=13301) | Official code retrieved; it bars the state and political subdivisions from imposing the listed gift/death taxes. This is not a claim that the federal estate tax cannot apply. |

### Verified wording gap — leave as review-only

`pages/flagged-for-review.html` says the BOE-19-P claim period is unverified because the BOE information sheet read for the page omits it. The official BOE Proposition 19 page linked above **does** state the exclusion-claim period. This flag is stale/incomplete. Suggested follow-up: update the generic flag and, if desired, add the BOE claim deadline to the generic timeline with the direct BOE link. This suggestion is recorded for review and was **not** implemented in this audit.

## Deployment and privacy boundary

- Post-PR #71: GitHub Pages run `43648228684` succeeded; Pages API reported `built` at merge `6815e45`; the live output contained case-specific owner material. The post-merge verification run `43648229338` failed at its unit/regression tests.
- Containment: merge `6815e45` is reverted on this feature branch only. `main` and the live site remain exposed until the revert PR is merged and deployment is confirmed. After merge, verify the Pages API SHA/status and fetch the home page, privacy page, and phased-investing page with cache-busting URLs.
- The history is not scrubbed. The current generic publication, source repository, and previously published history are different privacy boundaries. A plain revert only changes current output; it cannot recall prior public copies.

## Suggestions for review (not applied)

1. Correct the stale BOE-19-P filing-window flag, linking the official BOE Proposition 19 page. Decide whether the date belongs in the deadline timeline.
2. For any future historical investment comparison, require a documented, source-verified total-return series and explicit inflation/tax treatment; otherwise keep the page at generic stress-test guidance and label synthetic examples as synthetic.
3. Keep future inheritance facts separate from the already-owned property's baseline. Do not publish household/property values, identifiable histories, individualized forecasts, or raw inputs on Pages.
4. Treat removal of legacy inputs and history cleanup as a separate owner-led privacy task. Do not claim it is complete based on the current-output revert.
