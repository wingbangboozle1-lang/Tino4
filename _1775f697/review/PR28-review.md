# Independent review of the merged dashboard (PR #28)

**Reviewed:** 2026-11-12 UTC  
**Commit reviewed:** `e788d0e1141d85cd6556afa774f5eb0e001805d9`  
**Scope:** Public root pages and generator after the integration; selected official sources; privacy, source-link coverage, model-validity boundaries, and publication status. No household figures are repeated here.

## Verification performed

- Rebuilt the merged dashboard and ran its verifier: 14 pages, 584 table rows, 1,364 links, 1,909 dollar amounts, zero structural failures. This is structural verification, **not** evidence that every model assumption or every linked fact is correct.
- Independently opened the official sources below and checked the cited legal or data boundary against the relevant page text:
  - IRS, [IR-2026-133 / Revenue Procedure 2026-35](https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2027-taxpayers-continue-to-benefit-from-the-working-families-tax-cuts): confirms the published 2026 and 2027 federal estate exclusions and the separate annual gift exclusion. An estate-tax filing threshold is estate-level and is not an amount each beneficiary may inherit tax-free.
  - IRS, [Estate tax](https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax): gross-estate calculation includes assets and certain trust interests; filing requirement is based on the decedent's estate and adjusted taxable gifts, and a filing can also be made to elect portability.
  - California Legislature, [Revenue and Taxation Code §13301](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=13301.&lawCode=RTC): bars both the state and its political subdivisions from imposing gift, inheritance, succession, legacy, or estate tax on account of a death.
  - California BOE, [Proposition 19](https://www.boe.ca.gov/Prop19/) and [2025 adjustment notice](https://www.boe.ca.gov/news/2025/nr-25-02.htm): family-home exclusion is conditional on the applicable transferor/transferee and principal-residence requirements; the indexed limit applies only to eligible family homes/farms and the published period, not automatically to an unrelated property or a future transfer year.
  - IRS, [Gifts and inheritances / basis](https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances): inherited-property basis is generally date-of-death fair market value, with an alternate-valuation-date election only under specified estate-return conditions; the source does not establish the treatment of an unknown trust instrument.
  - California FTB, [Gifts and inheritance](https://www.ftb.ca.gov/file/personal/income-types/gifts-and-inheritance.html): inheritance itself is not California income, while income later produced by inherited assets is reportable.
  - California Department of Insurance, [Residential Property Insurance Report](https://www.insurance.ca.gov/0400-news/0200-studies-reports/0250-homeowners-study/) and [Wildfire Risk Information Reporting](https://www.insurance.ca.gov/01-consumers/200-wrr/WildfireRiskInfoRpt.cfm): official reporting includes historical ZIP-level premium/exposure or policy-level premium information, with the report page identifying experience through 2023. This is **not** a current quote for a particular owner-occupied or landlord policy.
  - FHFA, [House Price Index](https://www.fhfa.gov/data/hpi): describes historical repeat-sales indexes; it is not an official forecast for a specific property.
  - GitHub, [Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository): history rewriting requires coordination and does not automatically remove copies, forks, cached views, or pull-request references.
- GitHub Pages build API reports the latest reviewed root build as `built` with no build error. This confirms deployment processing only; it is not a privacy or model-validity check.

## Findings

1. **Critical privacy finding — current root output conflicts with the brief.** The merged root dashboard publishes household-specific dollar projections and an individualized ranking derived from the supplied property/rent/cost profile. Placeholder property labels, omitted street/ZIP identifiers, and ten-dollar rounding do not make a distinctive derived financial profile anonymous. These figures must not remain in the public website under the user's explicit privacy instruction. Do not quote or reproduce any such figures in new public commits, logs, PR descriptions, or build output.
2. **Build-log exposure.** The delegated build runs the model engine, whose normal stdout includes derived household outcomes. Build output is not part of the HTML, but it can be retained in command or automation logs. A public build must not execute or emit the private model.
3. **A green structural verifier is not source verification.** It confirms page/row/link/status structure and checks a source allow-list; it cannot prove that a linked page supports every assertion, that private inputs are valid, or that a forecast is sound. No claim is made here that all 584 rows have been independently fact-checked line by line.
4. **Personalized ranking is assumption-dependent.** Trust type and terms, ownership/basis, transfer date, tax profile, tax-rate area, future assessment, insurance, rent, maintenance, utilities, sale costs, portfolio allocation/returns, and laws in the 2040s are not fixed by the cited sources. Historical replay frequency is not a calibrated probability of future superiority. The model ranking is illustrative and should not be represented as a verified recommendation.
5. **Insurance wording needs precision.** It is accurate to leave current parcel-specific premiums blank without a quote. It is inaccurate to imply that California publishes no ZIP-level insurance experience data: CDI exposes historical data, but it is not a current, property-specific quote.
6. **Public-history exposure is unresolved.** The present site can be corrected without erasing past public commits, PR diffs, caches, or forks. Any repository-history cleanup needs an owner/admin-led, coordinated process consistent with GitHub's documentation; a normal follow-up commit is not a purge.

## Required corrective actions

- Replace household-specific root projections and recommendations with source-linked rules, explicitly labeled synthetic/index-only scenarios, and blank/flagged fields for unverified private inputs.
- Ensure the public build never loads household inputs or prints their derived results.
- Preserve the 2027 IRS update and the verified federal/California rule distinctions; do not extrapolate today's thresholds or Proposition 19 amount into the 2040s as facts.
- Update the insurance note to distinguish historic ZIP-level experience from a current quote.
- Keep the history-remediation issue prominently flagged and seek repository-owner action; do not imply the current Pages deployment or a $10 rounding check removes historic exposure.

## Boundaries

This review is not legal, tax, investment, or insurance advice. It does not verify the owner's personal documents or values and does not publish them. The root-row factual audit remains incomplete and should be treated as **needs review** unless each non-synthetic assertion is separately checked against its linked official text.
