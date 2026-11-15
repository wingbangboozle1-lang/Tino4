#!/usr/bin/env python3
"""Build a privacy-first, source-linked inheritance decision workspace.

The public build is deliberately static and never imports household inputs at
runtime: the owner-supplied figures below are already rounded to the nearest
$10 before they are written anywhere in this file. No name, address, postal
code, parcel identifier or document identifier is emitted. Every substantive
table row has an evidence status and at least one official source link.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKED = "2026-11-15"
SITE_TITLE = "Private inheritance decision workspace"

# Links were fetched directly on CHECKED. The scope is intentionally narrow:
# a source may establish a legal rule or a public historical observation, but
# never a private property's value, bill, lease, premium, title, or tax position.
SOURCES = {
    "irs_estate": {
        "label": "IRS — Estate tax",
        "url": "https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax",
        "scope": "Defines the gross estate, allowable deductions and the year-of-death Form 706 filing threshold table through 2026. The threshold is not an amount per beneficiary.",
        "verified": True,
    },
    "irs_2027": {
        "label": "IRS IR-2026-133 — 2027 estate and gift adjustments",
        "url": "https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2027-taxpayers-continue-to-benefit-from-the-working-families-tax-cuts",
        "scope": "States the 2027 basic estate-tax exclusion and annual gift exclusion, and compares them with 2026 amounts. Does not forecast future law.",
        "verified": True,
    },
    "irs_estate_faq": {
        "label": "IRS — Estate-tax filing FAQs",
        "url": "https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-estate-taxes",
        "scope": "Explains the filing test using gross estate plus adjusted taxable gifts and the specific gift-tax exemption, the 9-month Form 706 due date, the up-to-6-month Form 4768 extension, and that portability can require a filing below the threshold. Notes that the Working Families Tax Cuts (Public Law 119-21, July 4, 2025) set the 2026 basic exclusion at $15,000,000. Individual filing status still requires estate facts.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_basis": {
        "label": "IRS — Gifts and inheritances FAQ",
        "url": "https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances",
        "scope": "States that inherited-property basis is generally date-of-death fair market value, subject to exceptions and consistent-basis rules; gain can arise on a later sale. It does not establish a property's value or tax basis.",
        "verified": True,
    },
    "irs_1041": {
        "label": "IRS — About Form 1041",
        "url": "https://www.irs.gov/forms-pubs/about-form-1041",
        "scope": "Describes Form 1041 reporting by fiduciaries for estate or trust income, deductions, gains, losses, and distributions. Whether a specific trust must file is not determined here.",
        "verified": True,
    },
    "irs_rental": {
        "label": "IRS Publication 527 — Residential Rental Property",
        "url": "https://www.irs.gov/publications/p527",
        "scope": "Covers rental income, expenses, personal use, repairs, improvements, vacancy and depreciation. It does not provide a rent amount or repair budget for a private property.",
        "verified": True,
    },
    "ca_death_tax": {
        "label": "California State Controller — Estate tax",
        "url": "https://www.sco.ca.gov/ardtax_estate_tax.html",
        "scope": "States that California Estate Tax returns are not required for deaths on or after January 1, 2005. The page is not a forecast of future law.",
        "verified": True,
    },
    "ca_rtc13301": {
        "label": "California Revenue and Taxation Code §13301",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=13301.&lawCode=RTC",
        "scope": "Current text bars the state and its political subdivisions from imposing a gift, inheritance, succession, legacy, income, or estate tax on a transfer by reason of death. Future legislatures can change law.",
        "verified": True,
    },
    "boe_prop19": {
        "label": "California BOE — Proposition 19",
        "url": "https://www.boe.ca.gov/prop19/",
        "scope": "Summarizes current intergenerational property-tax rules, principal-residence requirements, filing periods and the periodically adjusted value-limit formula. It cannot establish eligibility without the deed, relationship, occupancy and claim facts.",
        "verified": True,
    },
    "ca_rtc63": {
        "label": "California Revenue and Taxation Code §63.2",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=63.2.&lawCode=RTC",
        "scope": "Statutory family-home exclusion conditions: transferor's principal residence, transferee must become principal residence within one year of transfer, homeowners' or disabled veterans' exemption must be filed within one year, exclusion claim within three years or before the earlier of a third-party transfer or loss of occupancy, value cap of factored base year value plus $1,000,000 as biennially adjusted, and removal of the exclusion when the transferee is no longer exempt-eligible. Qualifying grandchild transfers also require the statutory deceased-parent condition.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "ca_rtc480": {
        "label": "California Revenue and Taxation Code §480",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=480.&lawCode=RTC",
        "scope": "Requires a change-in-ownership statement for real property transferred by reason of death, including through a trust, within 150 days after death in the specified nonprobate cases.",
        "verified": True,
    },
    "ca_prob160617": {
        "label": "California Probate Code §16061.7",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=16061.7.&lawCode=PROB",
        "scope": "Requires trustee notice in specified events, including when a revocable trust becomes irrevocable because of death; the statutory notice deadline is generally 60 days. Applicability depends on trust facts.",
        "verified": True,
    },
    "boe_pub29": {
        "label": "California BOE Publication 29 — California Property Tax",
        "url": "https://www.boe.ca.gov/proptaxes/pdf/pub29.pdf",
        "scope": "Overview of Proposition 13: a 1% general levy plus voter-approved bonded indebtedness and a general 2% limit on annual assessed-value growth, subject to reassessment rules and other bill components. It is not a parcel-specific tax rate.",
        "verified": True,
    },
    "ca_rent": {
        "label": "California Civil Code §1947.12",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1947.12.&lawCode=CIV",
        "scope": "Current statewide rent-cap text and exemptions. Coverage, local ordinances, permitted use and tenant protections require property- and jurisdiction-specific review.",
        "verified": True,
    },
    "cdi": {
        "label": "California Department of Insurance — Residential insurance",
        "url": "https://www.insurance.ca.gov/01-consumers/105-type/5-residential/index.cfm",
        "scope": "Provides residential-insurance shopping tools and explains the limited perils covered by the FAIR Plan and the possible role of a Difference in Conditions policy. No individual premium is stated.",
        "verified": True,
    },
    "cpuc_solar": {
        "label": "California Public Utilities Commission — Net metering and net billing",
        "url": "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/customer-generation/net-energy-metering-and-net-billing",
        "scope": "Explains NEM/NBT tariff differences; under net billing, export credits are usually below retail rates. Eligibility, tariff, interconnection date and a household bill determine actual credits.",
        "verified": True,
    },
    "water_board": {
        "label": "California State Water Resources Control Board — Drinking Water Program",
        "url": "https://www.waterboards.ca.gov/drinking_water/programs/",
        "scope": "Describes state oversight of public water systems. It does not publish an individual service address's water bill or tariff; the provider bill is required.",
        "verified": True,
    },
    "hud_fmr": {
        "label": "HUD — Fair Market Rents",
        "url": "https://www.huduser.gov/portal/datasets/fmr.html",
        "scope": "Describes annual FMR estimates (40th-percentile gross rents) used for specified housing programs; the FY2027 documentation system is live. FMR is a benchmark, not a property appraisal, lawful rent determination or current lease amount. Area-level values require an interactive query and are left blank here where not retrieved.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "cslb": {
        "label": "California Contractors State License Board — Check a license",
        "url": "https://www.cslb.ca.gov/OnlineServices/CheckLicenseII/CheckLicense.aspx",
        "scope": "Allows a reader to check a contractor license and complaint disclosure. It does not set or verify a repair estimate.",
        "verified": True,
    },
    "treasury_bills": {
        "label": "TreasuryDirect — Treasury bills",
        "url": "https://treasurydirect.gov/marketable-securities/treasury-bills/",
        "scope": "Bills have terms from 4 to 52 weeks, rates fixed at auction, may be held to maturity or sold earlier, and interest is federally taxable but exempt from state and local taxes.",
        "verified": True,
    },
    "treasury_notes": {
        "label": "TreasuryDirect — Treasury notes",
        "url": "https://www.treasurydirect.gov/marketable-securities/treasury-notes/",
        "scope": "Notes include 2-, 3-, 5-, 7- and 10-year terms, pay a fixed auction rate every six months, may be held to maturity or sold earlier, and interest is federally taxable but exempt from state and local taxes. The page's latest posted 10-year note auction result was 5.000% when checked on 2026-11-15; auction rates change.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "fed_1929": {
        "label": "Federal Reserve History — Stock Market Crash of 1929",
        "url": "https://www.federalreservehistory.org/essays/stock-market-crash-of-1929",
        "scope": "Reports the Dow's 89% peak-to-trough decline and that its pre-crash high was not regained until November 1954. This is a price-index history, not a diversified portfolio total return.",
        "verified": True,
    },
    "fed_2008": {
        "label": "Federal Reserve History — The Great Recession",
        "url": "https://www.federalreservehistory.org/essays/great-recession-of-200709",
        "scope": "Reports a 57% S&P 500 peak-to-trough decline and an approximately 30% average U.S. home-price decline in that episode. Neither is a local property forecast or a total-return estimate.",
        "verified": True,
    },
    "bls_cpi": {
        "label": "U.S. Bureau of Labor Statistics — CPI, June 2022",
        "url": "https://www.bls.gov/opub/ted/2022/consumer-prices-up-9-1-percent-over-the-year-ended-june-2022-largest-increase-in-40-years.htm",
        "scope": "Reports a 9.1% twelve-month CPI increase through June 2022, the largest twelve-month increase since November 1981. It is a historical observation, not a long-run inflation assumption.",
        "verified": True,
    },
    "cbo_rates": {
        "label": "Congressional Budget Office — Interest-rate scenarios, 2026–2036",
        "url": "https://www.cbo.gov/publication/62809",
        "scope": "CBO reports a 4.3% average 10-year Treasury rate in its 2026–2036 forecast and 4.8%/5.8% higher-rate scenarios. It is not a 50-year forecast, house-price forecast or household investment return.",
        "verified": True,
    },
    "fhfa_hpi": {
        "label": "Federal Housing Finance Agency — HPI summary tables",
        "url": "https://www.fhfa.gov/data/hpi/summary-tables",
        "scope": "Publishes broad state and metropolitan-area house-price indexes. Index history can inform scenario design but is not a valuation or forecast for an individual property.",
        "verified": True,
    },
    "sec_stocks": {
        "label": "SEC Investor.gov — Stocks FAQs",
        "url": "https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks",
        "scope": "Explains stock risks, potential loss and diversification; it does not prescribe a return assumption or portfolio allocation.",
        "verified": True,
    },
    "github_history": {
        "label": "GitHub Docs — Removing sensitive data from a repository",
        "url": "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository",
        "scope": "Explains the coordination and side effects of history rewrites and warns that PRs, forks, caches and clones can retain data. GitHub Support or repository-owner action may be needed.",
        "verified": True,
    },
    "congress_legislation": {
        "label": "Congress.gov — Advanced legislation search",
        "url": "https://www.congress.gov/advanced-search/legislation",
        "scope": "Official search interface for federal bills and resolutions and their status. A proposal is not current law unless enacted; no specific pending bill is treated as law here.",
        "verified": True,
    },
    "ca_legislation": {
        "label": "California Legislative Information — Bill Search",
        "url": "https://leginfo.legislature.ca.gov/faces/billSearchClient.xhtml",
        "scope": "Official search interface for California bills and their status. A bill or proposal is not current law unless chaptered and effective; no specific pending bill is treated as law here.",
        "verified": True,
    },
    "ftb_404": {
        "label": "FTB inheritance-information URL — retrieval failed",
        "url": "https://www.ftb.ca.gov/file/personal/income-types/income-from-gifts-and-inheritances.html",
        "scope": "Direct retrieval returned a 404 on 2026-11-14. No California income-tax claim is based on this unavailable page.",
        "verified": False,
    },
    "boe_assessor_404": {
        "label": "BOE county-assessor directory URL — retrieval failed",
        "url": "https://www.boe.ca.gov/proptaxes/county-assessors.htm",
        "scope": "Direct retrieval returned a 404 on 2026-11-14. No local assessor record or local tax rate is inferred from this URL.",
        "verified": False,
    },
    "boe_pub801_404": {
        "label": "BOE Publication 801 URL — retrieval failed",
        "url": "https://www.boe.ca.gov/pdf/pub801.pdf",
        "scope": "Direct retrieval returned a 404 on 2026-11-14. Proposition 19 summaries in this site use the working BOE page and current statute instead.",
        "verified": False,
    },
    "cpuc_water_404": {
        "label": "CPUC water-utilities URL — retrieval failed",
        "url": "https://www.cpuc.ca.gov/industries-and-topics/water/water-utilities",
        "scope": "Direct retrieval redirected to a 404 on 2026-11-14. No household water-rate figure is based on this URL.",
        "verified": False,
    },
    "sftreasurer_rate": {
        "label": "San Francisco Treasurer & Tax Collector — Secured Property Taxes",
        "url": "https://sftreasurer.org/property/secured-property-taxes",
        "scope": "States the secured property tax rate for Fiscal Year 2026-27 is 1.18162182%, the installment delinquency dates (December 10 and April 10, 10% penalty), and that a supplemental assessment follows a change in ownership. A parcel bill can include additional charges; this page does not verify any private bill.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "scc_rate_book": {
        "label": "Santa Clara County Controller-Treasurer — Property Tax Rate Book (FY2025-26)",
        "url": "https://controller.santaclaracounty.gov/property-tax-distribution/property-tax-rate-book",
        "scope": "Official annual compilation of tax rates by tax rate area. The linked FY2025-26 book documents the 1% maximum levy, countywide component rates (retirement 0.0388, library 0.0024, housing bond 0.0056, VMC 2008 0.0052), voter-approved debt rates, the ≤2% annual assessed-value limit and secured due dates (November 1 / December 10, February 1 / April 10). Parcel totals require the parcel's tax rate area.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "boe_lta26026": {
        "label": "California BOE Letter to Assessors 2026/026 — Proposition 19 intergenerational FAQ",
        "url": "https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf",
        "scope": "Dated August 3, 2026. Explains the value cap (factored base year value plus the adjusted $1,000,000 amount), that continual use as the family home is required, that the exclusion is removed when the transferee is no longer eligible for the homeowners' exemption with the transfer-date full cash value then enrolled, and the filing windows: homeowners' exemption within one year, exclusion claim within three years or before the earlier of a third-party transfer or loss of occupancy.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "boe_lta25009": {
        "label": "California BOE Letter to Assessors 2025/009 — $1,000,000 value-cap adjustment",
        "url": "https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf",
        "scope": "Publishes the Proposition 19 value-cap amounts: $1,000,000 (transfers Feb 16, 2021 – Feb 15, 2023), $1,022,600 (2023 – 2025) and $1,044,586 (Feb 16, 2025 – Feb 15, 2027). The amount is adjusted every other February 16 by the FHFA California House Price Index; the next adjustment is February 2027. Later transfer dates will use an unpublished amount.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_cg": {
        "label": "IRS Topic no. 409 — Capital gains and losses",
        "url": "https://www.irs.gov/taxtopics/tc409",
        "scope": "Long-term capital gain rates of 0% (taxable income up to $48,350 single / $96,700 joint), 15% (up to $533,400 / $600,050) and 20% above those thresholds for 2025-year rules; short-term gains are taxed as ordinary income. It does not compute any taxpayer's liability.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_niit": {
        "label": "IRS Topic no. 559 — Net investment income tax",
        "url": "https://www.irs.gov/taxtopics/tc559",
        "scope": "States the 3.8% net investment income tax on the lesser of net investment income or modified adjusted gross income above $200,000 (single/household) or $250,000 (joint); applies to individuals, estates and trusts; includes rents and net gains from property dispositions.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_706": {
        "label": "IRS — Instructions for Form 706 (07/2026), Table A",
        "url": "https://www.irs.gov/instructions/i706",
        "scope": "Table A unified rate schedule: graduated rates from 18% to 40%, with 40% on taxable amounts over $1,000,000 and $345,800 of tax on the first $1,000,000. Also lists the annual gift-exclusion history ($19,000 for 2025 through 2026) and the basic-exclusion credit equivalent of $5,945,800 for a $15,000,000 exclusion at 2026 rates.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "ftb_cg": {
        "label": "California FTB — Capital gains and losses",
        "url": "https://www.ftb.ca.gov/file/personal/income-types/capital-gains-and-losses.html",
        "scope": "States that California does not have a lower rate for capital gains and that all capital gains are taxed as ordinary income (page last updated 01/28/2026). It does not compute a taxpayer's rate.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "rtc17041": {
        "label": "California Revenue and Taxation Code §17041",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=17041.&lawCode=RTC",
        "scope": "Base California personal income tax schedule of 1% to 9.3% with annual bracket indexing directed to the Franchise Tax Board. Higher statutory tiers and the FTB annual tables govern actual rates.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "rtc17043": {
        "label": "California Revenue and Taxation Code §17043",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=17043.&lawCode=RTC",
        "scope": "Imposes an additional 1% California tax on taxable income over $1,000,000 (Proposition 63, operative January 1, 2005).",
        "verified": True,
        "checked": "2026-11-15",
    },
    "bls_hist": {
        "label": "BLS — Historical CPI-U, Table 24 (October 2017 edition)",
        "url": "https://www.bls.gov/cpi/tables/historical-cpi-u-201710.pdf",
        "scope": "Annual CPI-U average percent changes: +11.0% (1974), +11.3% (1979), +13.5% (1980), +10.3% (1981), −9.0% (1931), −9.9% (1932), +3.8% (2008), −0.4% (2009). Historical observations, not forecasts; the edition is dated October 2017.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "bls_mlr100": {
        "label": "BLS Monthly Labor Review — One hundred years of price change",
        "url": "https://www.bls.gov/opub/mlr/2014/article/one-hundred-years-of-price-change-the-consumer-price-index-and-the-american-inflation-experience.htm",
        "scope": "Reports that the all-items CPI fell 27.4% from October 1929 to April 1933, rose 72.7% total over 1913–1929 (about 3.5% annually), and fell 15.8% in the 12 months ending June 1921. Historical observations only.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "fed_pce": {
        "label": "Federal Reserve — Economy at a Glance, Inflation (PCE)",
        "url": "https://www.federalreserve.gov/economy-at-a-glance-inflation-pce.htm",
        "scope": "States the Federal Reserve's longer-run inflation objective of 2 percent as measured by annual PCE price-index change, and displays a latest reading of 3.6% for September 2026. An objective and a latest observation, not a forecast.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "treasury_curve": {
        "label": "U.S. Treasury — Daily Treasury Par Yield Curve Rates, 2026",
        "url": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026",
        "scope": "Official daily par yields. Rows verified for January 2, 2026: 3-month 3.65%, 6-month 3.61%, 1-year 3.55%, 2-year 3.47%, 10-year 4.19%. The page is dated Friday, November 13, 2026; yields change daily and must be re-checked at any decision date.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "cdi_report": {
        "label": "California Department of Insurance — Residential Property Insurance Report",
        "url": "https://www.insurance.ca.gov/0400-news/0200-studies-reports/0250-homeowners-study/",
        "scope": "CDI's biennial residential fire-insurance study: Part I premium and exposure data for 2008–2023 (spreadsheet) and Part II ZIP-code-level experience for 2018–2023. Structures with five or more units are excluded. No individual premium is stated.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "cdi_ho_avg": {
        "label": "CDI — Homeowners Multi-Peril average written premiums (2001–2017)",
        "url": "https://www.insurance.ca.gov/0400-news/0200-studies-reports/0250-homeowners-study/upload/A-Homeowners-2_v1-2.pdf",
        "scope": "Statewide average written premium for owner-occupied homeowners policies (HO1/2/3/5/8 or equivalent): $1,074 in experience year 2017; full 2001–2017 series in the linked table. A statewide average across coverage levels, not a Bay Area quote for any property.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "cdi_rental_avg": {
        "label": "CDI — Dwelling Fire (Rental Dwelling) average written premiums (2001–2017)",
        "url": "https://www.insurance.ca.gov/0400-news/0200-studies-reports/0250-homeowners-study/upload/A-DF-Rental-2_v1.pdf",
        "scope": "Statewide average written premium for rental-dwelling / landlord policies covering up to four units: $519 in experience year 2017; full 2001–2017 series in the linked table. A statewide average, not a quote for any building.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "sf_rent": {
        "label": "San Francisco — Learn about rent increases",
        "url": "https://www.sf.gov/learn-about-rent-increases-san-francisco",
        "scope": "Official San Francisco Rent Ordinance guidance: allowed annual increase of 1.4% effective March 1, 2025 through February 28, 2026; a rent-increase license and Housing Inventory reporting are required; 30-day or 90-day notice rules apply. The percentage resets each March 1 — verify the current rate before use.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "scc_assessor": {
        "label": "Santa Clara County Assessor — official property search",
        "url": "https://asr.santaclaracounty.gov/",
        "scope": "Official county assessor portal for property search, assessment look-up, decline-in-value requests, exemptions and Proposition 19 claim support. It is the verification route for owner-supplied roll values; this link does not itself confirm any private figure.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "sf_assessor": {
        "label": "San Francisco Assessor-Recorder — official department page",
        "url": "https://www.sf.gov/departments--assessor-recorder",
        "scope": "Official San Francisco Assessor-Recorder page with the community property portal for assessment information, exemptions and exclusions, plus official dates for appeals and tax payments. Verification route for owner-supplied San Francisco figures.",
        "verified": True,
        "checked": "2026-11-15",
    },
}

NAV_GROUPS = [
    ("Start", [
        ("index.html", "Decision overview"),
        ("pages/executive-summary.html", "Executive summary"),
    ]),
    ("Decision", [
        ("pages/decision-analysis.html", "Compare paths"),
        ("pages/questions.html", "Questions & missing evidence"),
        ("pages/suggestions.html", "Suggestions for review"),
    ]),
    ("Numbers", [
        ("pages/projections.html", "Projection worksheet"),
        ("pages/property-tax.html", "Property-tax rules"),
        ("pages/operating-costs.html", "Costs & coverage"),
    ]),
    ("Stress tests", [
        ("pages/black-swan.html", "Black-swan conditions"),
        ("pages/phased-investing.html", "Treasury staging tool"),
    ]),
    ("Law & process", [
        ("pages/estate-thresholds.html", "Estate-tax thresholds"),
        ("pages/inheritance-process.html", "Deadline timeline"),
        ("pages/law-watchlist.html", "Law watchlist"),
    ]),
    ("Adviser & evidence", [
        ("pages/attorney-cpa-brief.html", "Attorney & CPA brief"),
        ("pages/flagged-for-review.html", "Flagged for review"),
        ("pages/glossary.html", "Glossary"),
        ("pages/sources.html", "Official source register"),
        ("pages/privacy.html", "Privacy & limits"),
    ]),
]

EXPECTED_PAGES = [
    "index.html",
    "pages/executive-summary.html",
    "pages/decision-analysis.html",
    "pages/questions.html",
    "pages/suggestions.html",
    "pages/projections.html",
    "pages/property-tax.html",
    "pages/operating-costs.html",
    "pages/black-swan.html",
    "pages/phased-investing.html",
    "pages/estate-thresholds.html",
    "pages/inheritance-process.html",
    "pages/law-watchlist.html",
    "pages/attorney-cpa-brief.html",
    "pages/flagged-for-review.html",
    "pages/glossary.html",
    "pages/sources.html",
    "pages/privacy.html",
]


# ---------------------------------------------------------------------------
# Owner-supplied case figures.
#
# Every monetary value below is already rounded to the nearest $10 (halves
# away from zero) exactly as the owner instructed, before it appears anywhere
# in this file. No name, address, postal code, parcel identifier, account
# number or document identifier is stored or emitted. Owner-supplied values
# are never labelled verified: rows that use them are badged
# "Owner-supplied" and linked to the official verification portal.
# ---------------------------------------------------------------------------


def r10(value: float) -> int:
    """Round a non-negative amount to the nearest $10, halves away from zero."""
    return int((float(value) + 5.0) // 10) * 10


# Official published amounts that are not multiples of $10. These are agency
# figures (never case data) and are exempt from the owner's rounding rule.
OFFICIAL_UNROUNDED = (1_074, 519, 1_044_586)


def money(value: float) -> str:
    """Format an amount. Case amounts must already be multiples of $10."""
    amount = int(value)
    if amount % 10 and amount not in OFFICIAL_UNROUNDED:
        raise ValueError(f"unrounded case amount: {amount}")
    return f"${amount:,}"


def money_range(low: float, high: float) -> str:
    return f"{money(r10(low))}–{money(r10(high))}"


# Property A — anticipated trust transfer (owner-supplied, rounded to $10).
A_VALUE = 3_100_000          # owner estimate, November 2026
A_ASSESS = {                 # owner-supplied tax-assessment history
    2014: 440_310, 2015: 449_100, 2016: 455_950, 2017: 465_070,
    2018: 474_370, 2019: 483_850, 2020: 493_530, 2021: 498_640,
    2022: 508_610, 2023: 518_790, 2024: 529_160, 2025: 539_740,
    2026: 550_540,
}
A_TAX = {                    # owner-supplied annual property tax history
    2014: 5_970, 2015: 6_130, 2016: 6_410, 2017: 6_380, 2018: 6_380,
    2019: 6_570, 2020: 6_570, 2021: 6_660, 2022: 6_760, 2023: 6_920,
    2024: 7_000, 2025: 7_210, 2026: None,   # 2026 bill not yet supplied
}
# Property B — already owned by the same person (owner-supplied, rounded).
B_VALUE = 1_800_000          # owner estimate, November 2026
B_ASSESS = {
    2016: 96_560, 2017: 98_490, 2018: 100_460, 2019: 102_470,
    2020: 104_510, 2021: 105_600, 2022: 107_660, 2023: 109_810,
    2024: 112_010, 2025: 114_250,
}
B_TAX = {
    2016: 1_680, 2017: 1_740, 2018: 2_060, 2019: 2_130, 2020: 2_200,
    2021: 2_070, 2022: 2_110, 2023: 2_180, 2024: 2_320, 2025: 2_440,
}
# Owner-supplied operating inputs (rounded ranges / amounts, per month).
A_WATER = (100, 150)         # water, per month
A_SOLAR = (10, 20)           # solar credit profit, per month
A_INSURANCE_OWNER = 1_500    # owner estimate, per year — not verified
B_RENT_MONTH = 7_150         # gross rent from two of three units
B_UNITS, B_RENTED_UNITS = 3, 2
B_WATER = (330, 400)         # water for all three units, per month
B_ELEC = (30, 70)            # electricity, per month
B_INSURANCE_OWNER = 1_500    # owner estimate, per year — not verified
TRANSFER_WINDOW = "2040–2050"  # owner planning window, not a confirmed date

# Rate anchors used in projections (see each row's source and badge).
RATE_A_LO = 0.0105   # 1% statutory base + documented countywide components
RATE_A_HI = 0.0134   # owner-implied 2025 effective rate (7,210 / 539,740)
RATE_B_OFFICIAL = 0.0118162182   # SF FY2026-27 secured rate (Treasurer)
RATE_B_IMPLIED = 0.0214          # owner-implied 2025 effective rate (2,440 / 114,250)
CAP_1M_CURRENT = 1_044_586       # BOE LTA 2025/009, transfers 2025-02-16 → 2027-02-15
GROWTH_CAP = 0.02                # Proposition 13 annual assessed-value cap

# Market-value scenario bands (explicit assumptions, not forecasts):
# slow 1–3%/yr, central 3–5%/yr, fast 5–7%/yr, informed by FHFA HPI history.
SCENARIOS = (("Slow", 0.01, 0.03), ("Central", 0.03, 0.05), ("Fast", 0.05, 0.07))


def value_band(base: int, year: int, lo: float, hi: float, start: int = 2026) -> str:
    n = year - start
    return money_range(base * (1 + lo) ** n, base * (1 + hi) ** n)


def assessed_at(base: int, base_year: int, year: int) -> int:
    """Assessed value grown at the Proposition 13 2% cap."""
    return r10(base * (1 + GROWTH_CAP) ** (year - base_year))


def implied_rate(tax: int, assess: int) -> str:
    return f"{tax / assess:.2%}"


# Today-dollar illustration of Property A's annual property tax at transfer
# (owner estimate as the full-cash-value proxy), rounded to $10.
A_TAX_NO_EXCL = (r10(A_VALUE * RATE_A_LO), r10(A_VALUE * RATE_A_HI))
A_TAX_EXCL = (
    r10((A_VALUE - CAP_1M_CURRENT) * RATE_A_LO),
    r10((A_VALUE - CAP_1M_CURRENT) * RATE_A_HI),
)
A_TAX_GAP = (A_TAX_NO_EXCL[0] - A_TAX_EXCL[0], A_TAX_NO_EXCL[1] - A_TAX_EXCL[1])
# Property B 2026 projected tax at the official rate vs the owner-implied rate.
B_2026_ASSESS = assessed_at(B_ASSESS[2025], 2025, 2026)
B_2026_TAX = (
    r10(B_2026_ASSESS * RATE_B_OFFICIAL),
    r10(B_2026_ASSESS * RATE_B_IMPLIED),
)


# ---------------------------------------------------------------------------
# Phased-investing worked example — mirrors assets/app.js exactly so the
# static table and the live tool agree. Normalized units, never dollars.
# ---------------------------------------------------------------------------


def _phase_sim(crash_start: int, staging: int, drawdown: float,
               trough: int, drift: float, y1: float, y2: float) -> dict:
    starting = 100.0
    horizon = max(staging, crash_start + trough)
    peak = (1 + drift) ** (crash_start / 12)

    def index_at(month: int) -> float:
        if month < crash_start:
            return (1 + drift) ** (month / 12)
        elapsed = min(1.0, max(0.0, (month - crash_start) / trough))
        return peak * (1 - drawdown * elapsed)

    reserve, shares = starting, 0.0
    imm_peak = ph_peak = starting
    imm_worst = ph_worst = 0.0
    for month in range(1, horizon + 1):
        if month <= staging:
            annual = (y1 if month <= 12 else y2) / 100.0
            reserve *= (1 + annual) ** (1 / 12)
            purchase = min(starting / staging, reserve)
            shares += purchase / max(index_at(month), 1e-6)
            reserve -= purchase
            if month == staging and reserve > 0:
                shares += reserve / max(index_at(month), 1e-6)
                reserve = 0.0
        idx = index_at(month)
        imm_value, ph_value = starting * idx, shares * idx + reserve
        imm_peak = max(imm_peak, imm_value)
        ph_peak = max(ph_peak, ph_value)
        imm_worst = min(imm_worst, imm_value / imm_peak - 1)
        ph_worst = min(ph_worst, ph_value / ph_peak - 1)
    final_index = index_at(horizon)
    return {
        "months": horizon,
        "immediate": starting * final_index,
        "phased": shares * final_index + reserve,
        "imm_dd": imm_worst * 100,
        "ph_dd": ph_worst * 100,
    }


# Reference yields: Daily Treasury par curve, January 2, 2026 (verified).
PHASE_REF_Y1, PHASE_REF_Y2 = 3.55, 3.47


def phase_worked_rows() -> list[dict]:
    rows = []
    for label, drawdown, trough in (
        ("2007–09 S&P 500 episode (−57%)", 0.57, 17),
        ("1929 Dow episode (−89%)", 0.89, 36),
    ):
        for timing, crash_start in (("begins during staging", 15), ("begins after staging", 30)):
            result = _phase_sim(crash_start, 30, drawdown, trough, 0.0,
                                PHASE_REF_Y1, PHASE_REF_Y2)
            rows.append({
                "cells": [
                    label, timing, f"{result['months']} months",
                    f"{result['immediate']:.2f} units", f"{result['phased']:.2f} units",
                    f"{result['imm_dd']:.1f}%", f"{result['ph_dd']:.1f}%",
                ],
                "status": "Projection",
                "sources": ["fed_1929", "fed_2008", "treasury_curve"],
            })
    return rows


class SafeHTML(str):
    """A small explicit marker for trusted, locally generated HTML fragments."""


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def source_link(key: str) -> str:
    source = SOURCES[key]
    return (
        f'<a class="source" href="{esc(source["url"])}" '
        f'title="{esc(source["scope"])}" rel="noopener noreferrer">'
        f'{esc(source["label"])}</a>'
    )


def badge(status: str) -> str:
    css = {
        "Verified": "verified",
        "Missing": "missing",
        "Owner-supplied": "owner",
        "Projection": "projection",
        "Assumption": "assumption",
        "Guidance": "guidance",
        "Not verified": "missing",
        "Action needed": "guidance",
        "Historical": "verified",
    }.get(status, "guidance")
    return f'<span class="badge {css}">{esc(status)}</span>'


def cell(value: object) -> str:
    if isinstance(value, SafeHTML):
        return f"<td>{value}</td>"
    return f"<td>{esc(value)}</td>"


def make_table(title: str, headers: list[str], rows: list[dict], note: str = "") -> str:
    if not rows:
        raise ValueError(f"Table {title!r} has no rows")
    head = "".join(f"<th scope=\"col\">{esc(h)}</th>" for h in headers)
    head += '<th scope="col">Evidence status</th><th scope="col">Official source / scope</th>'
    body_rows = []
    for row in rows:
        keys = row.get("sources", [])
        if not keys or any(key not in SOURCES for key in keys):
            raise ValueError(f"Every row in {title!r} needs a registered source")
        cells = "".join(cell(value) for value in row["cells"])
        links = ' <span aria-hidden="true">·</span> '.join(source_link(key) for key in keys)
        body_rows.append(
            f"<tr>{cells}<td>{badge(row.get('status', 'Guidance'))}</td><td>{links}</td></tr>"
        )
    caption = f'<caption>{esc(title)}</caption>'
    note_html = f'<p class="table-note">{esc(note)}</p>' if note else ""
    return (
        f'<section class="table-section"><h2>{esc(title)}</h2>{note_html}'
        f'<div class="table-scroll" tabindex="0" aria-label="{esc(title)}">'
        f'<table>{caption}<thead><tr>{head}</tr></thead><tbody>{"".join(body_rows)}</tbody></table>'
        f'</div></section>'
    )


def callout(title: str, text: str, kind: str = "info") -> str:
    return f'<aside class="callout {esc(kind)}"><strong>{esc(title)}</strong><p>{esc(text)}</p></aside>'


def paragraph(title: str, text: str) -> str:
    return f'<section class="prose"><h2>{esc(title)}</h2><p>{esc(text)}</p></section>'


def cards(title: str, items: list[tuple[str, str, str]], current: str = "index.html") -> str:
    body = []
    for heading, description, target in items:
        href = root_href(current, target)
        body.append(
            f'<article class="card"><h3><a href="{esc(href)}">{esc(heading)}</a></h3>'
            f'<p>{esc(description)}</p></article>'
        )
    return f'<section class="card-section"><h2>{esc(title)}</h2><div class="card-grid">{"".join(body)}</div></section>'


def root_href(current: str, target: str) -> str:
    if current == "index.html":
        return target
    return f"../{target}"


def build_nav(current: str) -> str:
    groups = []
    for group, links in NAV_GROUPS:
        items = []
        for target, label in links:
            href = root_href(current, target)
            active = ' aria-current="page"' if target == current else ""
            items.append(f'<a href="{esc(href)}"{active}>{esc(label)}</a>')
        groups.append(
            f'<details class="nav-group" open><summary>{esc(group)}</summary>'
            f'<div class="nav-items">{"".join(items)}</div></details>'
        )
    return "".join(groups)


def render_page(path: str, title: str, intro: str, body: str, eyebrow: str = "DECISION WORKSPACE", body_class: str = "") -> str:
    is_root = path == "index.html"
    prefix = "" if is_root else "../"
    page_class = "brief-page" if path == "pages/attorney-cpa-brief.html" else ""
    page_class = (page_class + " " + body_class).strip()
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive"><meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="description" content="Privacy-first, source-linked inheritance decision framework. Case figures are rounded to the nearest $10; no addresses, postal codes or identifiers are published.">
<title>{esc(title)} · {esc(SITE_TITLE)}</title>
<link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/app.js" defer></script>
</head><body class="{esc(page_class)}"><a class="skip" href="#main">Skip to content</a>
<div class="layout">
<aside class="sidebar"><a class="brand" href="{prefix}index.html"><span class="brand-icon" aria-hidden="true">◈</span><span>PRIVATE<br>DECISION BRIEF</span></a>
<p class="sidebar-note">Trust transfer +<br>already-owned property</p>
<nav aria-label="Main navigation">{build_nav(path)}</nav>
<div class="sidebar-bottom">Case figures rounded to $10<br>No addresses or identifiers<br>Sources checked {CHECKED}</div></aside>
<div class="workspace"><header class="topbar"><span>RESEARCH / DECISION SUPPORT</span><div><span class="privacy-dot" aria-hidden="true"></span> Privacy-first <button class="print-button no-print" id="print-page" type="button">Print</button></div></header>
<main id="main"><div class="page-heading"><span class="eyebrow">{esc(eyebrow)}</span><h1>{esc(title)}</h1><p class="lead">{esc(intro)}</p></div>{body}</main>
<footer><strong>Planning framework only.</strong> Not legal, tax, insurance, appraisal or investment advice. A source supports only its stated scope, not a private fact. Blank means unknown, not zero. Case figures are owner-supplied and rounded to the nearest $10; they are not officially verified. No address, postal code or identifier is published.<br>
<a href="{prefix}pages/privacy.html">Privacy &amp; limits</a> · <a href="{prefix}pages/sources.html">Official sources</a> · <a href="{prefix}pages/flagged-for-review.html">Flagged for review</a></footer>
</div></div></body></html>'''


def build_index() -> str:
    snapshot_rows = [
        {"cells": [
            "Property A — anticipated trust transfer (Cupertino, Santa Clara County)",
            f"{money(A_VALUE)} owner estimate (Nov 2026); 2026 assessment {money(A_ASSESS[2026])}; 2025 property tax {money(A_TAX[2025])}, an implied effective rate of {implied_rate(A_TAX[2025], A_ASSESS[2025])}; water {money_range(*A_WATER)} per month; solar credit {money_range(*A_SOLAR)} per month; insurance owner estimate {money(A_INSURANCE_OWNER)} per year (unverified).",
            f"After a trust transfer the annual property tax becomes about {money_range(*A_TAX_NO_EXCL)} at full reassessment, or {money_range(*A_TAX_EXCL)} if the family-home exclusion is claimed and kept — a gap of about {money_range(*A_TAX_GAP)} per year.",
        ], "status": "Owner-supplied", "sources": ["scc_assessor", "scc_rate_book", "boe_lta26026"]},
        {"cells": [
            "Property B — already owned (San Francisco)",
            f"{money(B_VALUE)} owner estimate (Nov 2026); 2025 assessment {money(B_ASSESS[2025])}; 2025 property tax {money(B_TAX[2025])}, an implied effective rate of {implied_rate(B_TAX[2025], B_ASSESS[2025])} against the official FY2026-27 secured rate of 1.18162182%; {B_RENTED_UNITS} of {B_UNITS} units rented at {money(B_RENT_MONTH)} per month gross ({money(B_RENT_MONTH * 12)} per year); water {money_range(*B_WATER)} per month; electricity {money_range(*B_ELEC)} per month; insurance owner estimate {money(B_INSURANCE_OWNER)} per year (unverified).",
            f"Property B is already owned and stays out of the transfer. The gap between the official rate and the owner-implied rate is flagged for bill verification; 2026 projected tax is {money_range(*B_2026_TAX)}.",
        ], "status": "Owner-supplied", "sources": ["sf_assessor", "sftreasurer_rate", "sf_rent"]},
    ]
    rows = [
        {"cells": ["Trust, title and timing", f"The executed trust, amendments, trustee authority and distribution trigger are not independently confirmed. The owner-planned transfer window is {TRANSFER_WINDOW} (planning assumption, not a confirmed date).", "Obtain the executed trust/deed and a written trustee timeline before comparing any path; every statutory clock below starts from an actual date of death."], "status": "Owner-supplied", "sources": ["ca_prob160617", "ca_rtc480"]},
        {"cells": ["Property-tax exclusion eligibility", f"A transfer by trust does not by itself establish the family-home exclusion. With it, the taxable value at transfer is capped at full cash value minus the current $1,000,000 amount ({money(CAP_1M_CURRENT)} for transfers through February 15, 2027); without it the full transfer-date value is enrolled — today dollars, about {money_range(*A_TAX_NO_EXCL)} per year versus {money_range(*A_TAX_EXCL)}.", "Confirm the transferor's principal residence, the eligible relationship, occupancy within one year, the homeowners' exemption filing within one year, and the exclusion claim within three years."], "status": "Guidance", "sources": ["boe_prop19", "ca_rtc63", "boe_lta26026", "boe_lta25009"]},
        {"cells": ["Federal estate-tax exposure", "The 2026 Form 706 filing test uses gross estate plus adjusted taxable gifts against a $15,000,000 basic exclusion ($15,480,000 for 2027 deaths); tax above the exclusion runs at graduated rates up to 40%. The cash portion of this inheritance is not published or verified here.", "Obtain the full estate inventory, prior gifts, deductions and any spouse/portability facts; this is an estate-level test, not a per-heir allowance."], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq", "irs_706"]},
        {"cells": ["Property A rent, sale net proceeds and basis", f"Income-tax basis on a post-death sale is generally the date-of-death value, so a sale soon after transfer can produce little taxable gain; sale costs are an explicit 5%–7% planning assumption ({money_range(A_VALUE * 0.93, A_VALUE * 0.95)} net of costs before tax). Property A's market rent is not established and is left blank.", "Obtain rent comps or an appraisal, a broker net sheet, the deed/basis statement and two written insurance quotes before ranking rent-versus-sell."], "status": "Assumption", "sources": ["irs_basis", "irs_cg", "ftb_cg", "hud_fmr"]},
        {"cells": ["Property B rental income and rent control", f"Two of three units produce {money(B_RENT_MONTH)} per month gross ({money(B_RENT_MONTH * 12)} per year, owner-supplied). The San Francisco Rent Ordinance allowed increase was 1.4% for March 1, 2025 – February 28, 2026, and the owner can occupy the third unit.", "Confirm lease terms, unit legality, Rent Board coverage, the current-year allowable increase and the rent ledger before treating rent as durable income."], "status": "Owner-supplied", "sources": ["sf_rent", "ca_rent", "irs_rental"]},
        {"cells": ["Insurance and repairs", f"Owner estimates are {money(A_INSURANCE_OWNER)} and {money(B_INSURANCE_OWNER)} per year; CDI's statewide averages were {money(1074)} (owner-occupied, 2017) and {money(519)} (rental dwelling up to four units, 2017). Neither is a Bay Area quote; repair budgets are blank pending inspection.", "Request separate written owner-occupied and landlord quotes, replacement-cost estimates, inspection reports and licensed bids for each property."], "status": "Missing", "sources": ["cdi_report", "cdi_ho_avg", "cdi_rental_avg", "cslb"]},
        {"cells": ["Investment entry and reinvestment risk", "A 24–36 month Treasury staging plan after the transfer changes crash-entry exposure: in the published worked example a crash during staging ends at 56.21 versus 43.00 units (2008-style) while a crash after staging ends at 45.03 versus 43.00 — phasing helps only when the decline arrives during the wait, and maturing bills reinvest at unknown future auction yields.", "Use the local-only stress tool with then-current net yields; compare crash-during-wait, crash-after-wait and rising-market cases before allocating."], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes", "treasury_curve", "fed_1929", "fed_2008"]},
        {"cells": ["Long-range law and market conditions", "The Federal Reserve's longer-run objective is 2% PCE inflation while the latest reading is 3.6% (September 2026); CBO's 2026–2036 outlook puts the 10-year Treasury at 4.3% on average with 4.8% and 5.8% higher-rate scenarios. None of this verifies a 50-year path.", "Re-check enacted law, official bills, valuations, yields and quotes close to the transfer; never extrapolate one rate across five decades."], "status": "Guidance", "sources": ["fed_pce", "cbo_rates", "irs_2027", "fhfa_hpi"]},
    ]
    body = callout(
        "Working recommendation (conditional): keep Property B, sell Property A near the transfer, stage the proceeds",
        f"On the verified rules and owner-supplied figures, the default path is: keep and continue operating the already-owned San Francisco property; at the trust transfer, sell the inherited house soon after the date of death so the stepped-up basis keeps income tax minimal; park net proceeds in 3-month to 2-year Treasuries for 24–36 months and phase into equities. Reinvestment risk sits beside this headline: maturing bills may renew at lower yields, and phasing only softens entry risk when a crash occurs during the wait — see the worked example. The alternative — move into the inherited house and claim the family-home exclusion — is quantified above and wins only if the household actually wants that residence. All of this stays conditional on the gates below.",
        "warning",
    )
    body += make_table(
        "Case snapshot — owner-supplied figures rounded to the nearest $10",
        ["Asset", "Known figures (rounded, not officially verified)", "Decision implication"],
        snapshot_rows,
        "Owner-supplied means the figure came with the request and is rounded to $10 for privacy; the source links are the official portals where each figure must be verified. Blanks are unknown, not zero.",
    )
    body += make_table(
        "What would change the answer?",
        ["Decision-changing fact", "What is established now", "Next evidence / decision gate"],
        rows,
        "This is the first-screen triage list. Official links support the rule or process shown; they do not verify private title, occupancy, cost or tax facts.",
    )
    body += callout(
        "Keep the ownership roles distinct",
        "Property A is the anticipated trust transfer. Property B is already owned. A choice to occupy, rent or sell one asset must not silently assume that the other asset has the same owner, tax basis, assessment, lease or operating costs.",
        "info",
    )
    body += cards("Use this workspace in order", [
        ("1. Resolve the questions", "Collect the trust, tax, title, lease, assessment, insurance and utility records in a private vault.", "pages/questions.html"),
        ("2. Compare complete paths", "Keep live, rent, sell, mixed occupancy and staged reinvestment alternatives separate.", "pages/decision-analysis.html"),
        ("3. Review with advisers", "Print a one-page attorney and CPA briefing sheet; no identifying details are required on it.", "pages/attorney-cpa-brief.html"),
    ])
    return render_page(
        "index.html",
        "Decision overview",
        "A private planning framework for an anticipated trust transfer and a separate already-owned property. Case figures are rounded to the nearest $10; no addresses, postal codes or identifiers are published.",
        body,
        "START HERE",
    )


def build_executive_summary() -> str:
    rows = [
        {"cells": ["Asset roles", f"Property A is an expected future trust transfer planned around {TRANSFER_WINDOW} (owner planning window, not a confirmed date). Property B is already owned by the same person: {B_RENTED_UNITS} of {B_UNITS} units rent for {money(B_RENT_MONTH)} per month gross ({money(B_RENT_MONTH * 12)} per year) and the owner occupies the third unit.", "Confirm A's trust authority and title; keep B's rent ledger, leases and occupancy rules separate from every A decision."], "status": "Owner-supplied", "sources": ["ca_prob160617", "ca_rtc480", "irs_rental", "sf_rent"]},
        {"cells": ["Working recommendation (conditional)", f"Default path: keep Property B; sell Property A soon after the date of death so the stepped-up basis keeps income tax minimal; stage net proceeds ({money_range(A_VALUE * 0.93, A_VALUE * 0.95)} before tax at a 5%–7% cost assumption) in 3-month to 2-year Treasuries for 24–36 months, then phase into equities. Alternative: occupy A and claim the family-home exclusion if that residence is genuinely wanted.", "Reversal conditions: an unaffordable or unwilling sale process, a household decision to live in A, estate liquidity needs that keep A, insurance quotes that change the math, or rent comps that make renting A competitive at reassessed tax."], "status": "Guidance", "sources": ["irs_basis", "irs_cg", "boe_lta26026", "treasury_notes"]},
        {"cells": ["Property A tax at transfer", f"Without the family-home exclusion the full transfer-date value is enrolled: today dollars about {money_range(*A_TAX_NO_EXCL)} per year. With the exclusion claimed and kept, taxable value is capped at full cash value minus the current {money(CAP_1M_CURRENT)} cap amount: about {money_range(*A_TAX_EXCL)} per year — a gap of about {money_range(*A_TAX_GAP)} per year.", "Eligibility needs the transferor's principal residence, occupancy within one year, the homeowners' exemption within one year and the exclusion claim within three years; losing eligibility re-enrolls the transfer-date full cash value."], "status": "Projection", "sources": ["boe_lta26026", "boe_lta25009", "ca_rtc63", "scc_rate_book"]},
        {"cells": ["Property B operating picture", f"Owner-supplied: {money(B_RENT_MONTH * 12)} per year gross rent; water {money_range(*B_WATER)} per month; electricity {money_range(*B_ELEC)} per month; 2025 tax {money(B_TAX[2025])} at an implied {implied_rate(B_TAX[2025], B_ASSESS[2025])} versus the official FY2026-27 rate of 1.18162182%; 2026 projected tax {money_range(*B_2026_TAX)}. Insurance owner estimate {money(B_INSURANCE_OWNER)} per year against CDI's statewide rental average of {money(519)} (2017).", "Reconcile the rate discrepancy against the actual bill, confirm Rent Ordinance coverage and the current allowable increase, and obtain a written landlord policy quote."], "status": "Owner-supplied", "sources": ["sftreasurer_rate", "sf_rent", "cdi_rental_avg", "sf_assessor"]},
        {"cells": ["Federal estate exclusion — 2026", "$15,000,000 basic exclusion amount for 2026 deaths; the Form 706 filing test adds gross estate, adjusted taxable gifts and the specific gift-tax exemption.", "This is a federal estate-level threshold, not a per-beneficiary inheritance allowance; portability can require filing below it."], "status": "Verified", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["Federal estate exclusion — 2027", "$15,480,000 basic exclusion amount for 2027 deaths.", "This official amount says nothing about a future-year threshold."], "status": "Verified", "sources": ["irs_2027"]},
        {"cells": ["Illustrative estate tax above the threshold", "At 2026 rates the marginal rate above the exclusion is 40%: an illustrative taxable estate of $16,000,000 implies about $400,000 of federal estate tax, $18,000,000 implies about $1,200,000 and $20,000,000 implies about $2,000,000.", "Illustration only — the actual gross estate, deductions, gifts, credits and year of death are unknown; the estate (not each heir) pays any tax."], "status": "Projection", "sources": ["irs_706", "irs_estate"]},
        {"cells": ["Annual gift exclusion", "$19,000 for 2026 and $20,000 for 2027 per donor/recipient under the IRS announcement; it is not the estate-tax exclusion.", "Do not use the annual gift amount as the inheritance-tax threshold."], "status": "Verified", "sources": ["irs_2027"]},
        {"cells": ["California death taxes", "Current RTC §13301 bars state and local gift, inheritance, succession, legacy, income or estate tax on a transfer by reason of death; the State Controller says a California Estate Tax return is not required for deaths on or after 2005-01-01.", "Re-check the law for the actual year of death; this is not a future-law guarantee."], "status": "Verified", "sources": ["ca_rtc13301", "ca_death_tax"]},
        {"cells": ["California property tax", "Proposition 13 generally limits the general levy to 1% plus voter-approved bonded indebtedness and assessed-value growth to 2% per year; actual bills can include other components.", "Owner-supplied histories are consistent with the 2% cap (A: 1.34% implied; B: 2.14% implied versus the official 1.18162182% rate) — both must be reconciled against the bills."], "status": "Owner-supplied", "sources": ["boe_pub29", "scc_rate_book", "sftreasurer_rate"]},
        {"cells": ["Insurance and repairs", f"Owner estimates are {money(A_INSURANCE_OWNER)} and {money(B_INSURANCE_OWNER)} per year; CDI statewide averages were {money(1074)} (owner-occupied, 2017) and {money(519)} (rental dwelling up to four units, 2017); ZIP-level CDI data exists for 2018–2023. Repair budgets are blank pending inspection.", "Obtain written quotes for each intended use before treating any premium as real; the statewide averages are not Bay Area quotes."], "status": "Missing", "sources": ["cdi_report", "cdi_ho_avg", "cdi_rental_avg", "cslb"]},
    ]
    body = callout(
        "Executive conclusion — one conditional recommendation, four gates",
        f"Working answer: keep the already-owned San Francisco property, sell the inherited house soon after the date of death (stepped-up basis keeps income tax minimal), and stage the net proceeds through 24–36 months of 3-month to 2-year Treasuries before phasing into equities — or occupy the inherited house and claim the family-home exclusion if that is the residence the household actually wants. Renting the inherited house without occupying it is the weakest path because reassessment alone costs about {money_range(*A_TAX_NO_EXCL)} per year before any rent is known. This ranking is conditional on four gates: (1) the trust and title documents confirm the transfer and sale authority; (2) the estate inventory confirms liquidity and any federal estate-tax position; (3) written insurance, rent and repair evidence replaces the owner estimates; (4) the property-tax bills reconcile the implied rates shown here. Reinvestment risk is part of the headline, not a footnote: staging reduces crash-during-wait exposure but exposes maturing cash to future auction yields.",
        "warning",
    )
    body += make_table(
        "Important facts and current limits",
        ["Topic", "Verified rule or currently available information", "Decision implication"],
        rows,
    )
    body += cards("Next pages", [
        ("Missing evidence", "A question-by-question record list for counsel, CPA, assessor, insurer and rental adviser.", "pages/questions.html"),
        ("Current law", "Estate thresholds, California property-tax mechanics and transfer deadlines.", "pages/estate-thresholds.html"),
        ("Risk", "Historical stress anchors and a local-only Treasury phasing comparison.", "pages/black-swan.html"),
    ], current="pages/executive-summary.html")
    return render_page("pages/executive-summary.html", "Executive summary", "The short version: keep the already-owned property, sell the inherited house near the transfer and stage the proceeds — unless the household wants to live in the inherited house — with four verification gates and every case figure rounded to $10.", body, "EXECUTIVE SUMMARY")


def build_decisions() -> str:
    rows = [
        {"cells": ["Live in A; retain B", "Test whether A can qualify as a family home under current law; determine the separate rental/occupancy economics of B.", "Trust restrictions, eligibility, occupancy within the statutory period, current B leases and lost/retained rent must be documented.", "A family-home exclusion is conditional; rental and personal use can affect tax reporting and costs."], "status": "Guidance", "sources": ["boe_prop19", "ca_rtc63", "irs_rental"]},
        {"cells": ["Use B as residence; rent, retain or sell A", "Keep A's transfer authority, occupancy, rental use and sale alternative separate from B.", "Include any B rent using its private rent ledger; verify tenant/lease obligations and whether B can lawfully and practically serve as a residence.", "B's current rent, net operating costs, residence suitability, insurance and any required lease transition are not independently confirmed or published."], "status": "Missing", "sources": ["irs_rental", "ca_rent", "cdi"]},
        {"cells": ["Rent A; retain B",  "Treat A as a rental only after transfer authority, permitted use, tenant status, rent restrictions, insurance and basis are confirmed.", "Gross rent is not net return; include vacancy, tax, repairs, insurance, utilities, management and income taxes.", "Current local rent control, lawful unit count and property-specific rents are not verified."], "status": "Missing", "sources": ["irs_rental", "ca_rent", "hud_fmr", "cdi"]},
        {"cells": ["Sell A; retain B", "Use a defensible date-of-death value/basis, sale costs, debt payoff and tax analysis before estimating reinvestable proceeds.", "A sale may create taxable gain above basis; estate tax is a separate whole-estate analysis.", "No sale value, basis, debt, transaction costs or after-tax proceeds are published."], "status": "Missing", "sources": ["irs_basis", "irs_estate", "irs_rental"]},
        {"cells": ["Live in A; rent lawful units in A and/or B", "Model each legal unit and the owner's actual occupancy separately; do not assume the whole property can be rented or that one unit is lawful.", "Separate rental and personal-use expenses, leases, deposits, utilities and insurance; compare the net cash flow with full occupancy cost.", "Unit legality, leases, operating costs and relevant local rules are missing."], "status": "Missing", "sources": ["irs_rental", "ca_rent", "cdi"]},
        {"cells": ["Short hold, then sell A", "Compare interim carrying costs and occupancy against the sale date, tax basis, property-tax status and sale expenses.", "A short hold can change both tax and property-tax treatment; calendar dates and use matter.", "No holding period, tax year, valuation, title condition or rule eligibility is confirmed."], "status": "Missing", "sources": ["irs_basis", "boe_prop19", "ca_rtc480"]},
        {"cells": ["Sell A; park proceeds in short Treasuries; phase into stocks", "Compare immediate investment with a 24–36 month Treasury ladder and scheduled equity purchases, including early and late crash entry.", "Staging may reduce exposure during an early decline but can lag a rising market; maturing securities create reinvestment risk if yields fall.", "Net proceeds, future auction yields, tax status, liquidity, risk tolerance and investment policy are unknown."], "status": "Assumption", "sources": ["treasury_bills", "treasury_notes", "fed_1929", "fed_2008", "sec_stocks"]},
        {"cells": ["Retain A; change B occupancy or rental pattern", "Keep A's expected trust transfer separate from B's current ownership, basis, leases and rental operations.", "This mixed path can avoid a forced all-or-nothing choice but may alter rent, tax reporting, insurance and tenant obligations.", "B's occupancy, lease ledger, legal unit count and cash flow are not verified here."], "status": "Missing", "sources": ["irs_rental", "ca_rent", "cdi"]},
    ]
    body = callout("Conditional ranking: sell-and-stage leads, occupy is the real alternative, rent-without-occupying trails", f"The verified rules and owner-supplied figures rank the pure paths as follows. (1) Sell A near the date of death and stage the proceeds: income tax is minimal on the stepped-up basis, net proceeds are about {money_range(A_VALUE * 0.93, A_VALUE * 0.95)} at a 5%–7% cost assumption, and official-yield anchor income on that pool is roughly {money_range(2_900_000 * 0.0347, 2_900_000 * 0.052)} per year before tax (3.47% two-year CMT to 5.2% ten-year close, both 2026 official readings — not a forecast). (2) Occupy A and claim the family-home exclusion: today-dollar tax of about {money_range(*A_TAX_EXCL)} per year, but only if occupancy and both filings happen on time. (3) Rent A without occupying it: reassessed tax of about {money_range(*A_TAX_NO_EXCL)} per year before a single dollar of rent is known, which is why it trails until rent comps prove otherwise. Keep B in every path — selling B would realize gain on a long-held, low-basis asset. Each row below still depends on the listed evidence.", "warning")
    body += make_table("Mixed and pure paths to compare", ["Path", "Property A — anticipated trust transfer", "Property B — already owned", "Main uncertainty / risk"], rows, "The sources link to governing rules or official risk information. They do not establish whether a specific use, rent, exclusion or premium applies.")
    anchor_rows = [
        {"cells": ["Sell A near death →24–36 month Treasury staging → equities", f"Net proceeds ≈ {money_range(A_VALUE * 0.93, A_VALUE * 0.95)} (5%–7% cost assumption); income tax ≈ minimal if sold after the date-of-death basis attaches; staging worked example ends at 56.21 vs 43.00 units when the crash lands mid-staging (2008-style) and 45.03 vs 43.00 when it lands after.", f"{money(B_RENT_MONTH * 12)} per year gross rent continues; no change to B's title or basis.", "Sale timing must follow the basis step-up; reinvestment yields are unknown;5%–7% sale cost is an assumption."], "status": "Projection", "sources": ["irs_basis", "treasury_curve", "fed_2008", "irs_rental"]},
        {"cells": ["Occupy A; claim the family-home exclusion", f"Today-dollar tax ≈ {money_range(*A_TAX_EXCL)} while the exclusion is kept (versus {money_range(*A_TAX_NO_EXCL)} without it); requires occupancy within one year, homeowners' exemption within one year, exclusion claim within three years.", f"Two of {B_UNITS} units can continue renting at {money(B_RENT_MONTH)} per month while the owner occupies the third — or all three units if the household moves out of B.", "Relinquishing B occupancy; continual-use requirement; value cap at the actual transfer date is unknown (next BOE adjustment February 2027)."], "status": "Projection", "sources": ["boe_lta26026", "boe_lta25009", "ca_rtc63", "sf_rent"]},
        {"cells": ["Live in B; rent A (no exclusion)", f"Reassessed tax ≈ {money_range(*A_TAX_NO_EXCL)} per year before rent; Property A's market rent is blank — the path cannot be ranked above (1) or (2) until rent comps exist.", f"{money(B_RENT_MONTH * 12)} per year gross rent plus A rent if obtained.", "Rent legality and local rules for A; vacancy; distant-landlord costs; the tax floor dominates until rent is proven."], "status": "Missing", "sources": ["hud_fmr", "ca_rent", "irs_rental", "scc_rate_book"]},
        {"cells": ["Occupy A for a period, then return to B and rent A", "Saves roughly the exclusion gap ({money_range(*A_TAX_GAP)} per year) only while occupied; on loss of eligibility the transfer-date full cash value is enrolled, so the tax advantage does not persist after moving out.", "Rent pattern shifts with the household's move; Rent Ordinance rules still govern B's tenancies.", "Two moves, dual carrying costs, and the enrollment rule that ends the advantage — model before committing."], "status": "Projection", "sources": ["boe_lta26026", "ca_rtc63", "sf_rent"]},
        {"cells": ["Sell B (not recommended)", "No change to A's decision.", "B's basis is the original cost basis (no step-up is expected for an already-owned asset), so a sale realizes gain on roughly the difference between value and basis, taxed as ordinary income in California plus federal rates and the 3.8% net investment income tax where applicable.", "Large, avoidable tax bill; loss of the rental income stream and the residence."], "status": "Guidance", "sources": ["ftb_cg", "irs_cg", "irs_niit", "irs_basis"]},
    ]
    body += make_table("Quantified anchors behind the ranking", ["Path", "Property A economics", "Property B economics", "Key caveat"], anchor_rows, "All case amounts are owner-supplied or scenario arithmetic rounded to $10. Yield anchors are dated official readings, not forecasts. Ranges labelled as assumptions must be replaced with quotes and comps.")
    body += paragraph("Comparison rule", "For every path, show after-tax cash flows, one-time sale or transfer costs, debt, vacancy, repairs, insurance, utilities, property tax, rent legality, liquidity and reinvestment risk. Compare the same time horizon and disclose every assumption. The tables above already apply this rule to the four quantified anchors; extend the same treatment to any new path before adopting it.")
    return render_page("pages/decision-analysis.html", "Compare live, rent, sell and mixed paths", "Pure and mixed paths with quantified anchors, a conditional ranking, and the evidence that would reverse it. The trust asset and the already-owned asset never share a tax basis, title, rent or cost assumption.", body, "DECISION")


def build_questions() -> str:
    rows = [
        {"cells": ["Q1 — What exactly transfers, when, and under whose authority?", "Only the trust-transfer role is supplied; the instrument, amendments, distribution terms and trustee authority are absent.", "No verified answer; do not assume a beneficiary can occupy, rent or sell without trustee authority.", "Executed trust and amendments, deed, trustee contact, written distribution/sale/occupancy directions.", "Attorney / trustee"], "status": "Owner-supplied", "sources": ["ca_prob160617", "ca_rtc480"]},
        {"cells": ["Q2 — What is the full gross estate, adjusted taxable-gift history and specific gift-tax exemption?", "The public site does not publish an estate inventory or cash amount.", "Federal threshold exposure cannot be calculated from one home or beneficiary share; portability may independently require filing.", "Asset/debt inventory, prior taxable gifts, specific gift-tax exemption, deductions, spouse/portability facts and valuation date.", "CPA / estate attorney"], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["Q3 — What is the income-tax basis and defensible transfer value?", "No appraisal, Form 706, Schedule A/Form 8971 or basis schedule is published.", "IRS says inherited basis is generally date-of-death FMV, subject to exceptions; later sale above basis may create gain.", "Date-of-death appraisal, executor basis statement, improvements, depreciation and prior transfer records.", "CPA / appraiser"], "status": "Missing", "sources": ["irs_basis", "irs_estate"]},
        {"cells": ["Q4 — Does the transfer qualify for a California family-home exclusion?", "Relationship, transferor occupancy, trust title, transferee occupancy, value limit and claim status are not verified.", "Eligibility is conditional; occupancy and claim deadlines matter. Grandchild transfers have an additional statutory deceased-parent test.", "Deed/trust, family relationship, any intermediary-parent status, prior exemption, principal-residence proof, value-limit calculation, filed claim and dates.", "Assessor / property-tax adviser"], "status": "Missing", "sources": ["boe_prop19", "ca_rtc63"]},
        {"cells": ["Q5 — What is the current assessed value and complete tax bill for each asset?", "No tax bill or assessor roll is published.", "A 1% base levy and 2% general assessed-value cap do not reveal special charges or reassessment treatment.", "Current roll, supplemental bill, direct assessments, bond charges, base-year value, appeal status.", "Assessor / CPA"], "status": "Missing", "sources": ["boe_pub29", "boe_prop19"]},
        {"cells": ["Q6 — What is the legal unit count and rental-control coverage?", "No permit, certificate, lease or local determination is published.", "Do not assume all units are rentable or that statewide rules are the only applicable rules.", "Permits, certificates of occupancy, leases, rent registry, local ordinances and tenant notices.", "Landlord-tenant attorney / building authority"], "status": "Missing", "sources": ["ca_rent", "hud_fmr", "irs_rental"]},
        {"cells": ["Q7 — What is Property B's rental income after vacancy, expenses and taxes?", "No private rent amount, lease ledger or tenant record is published; include any current rent as a private input.", "HUD FMR is a program benchmark, not B's actual collected rent or a lawful rent determination.", "B's leases, rent roll, deposits, vacancy/collection history, permitted unit status, expense ledger and tax return; evaluate A separately if rented.", "CPA / property manager"], "status": "Missing", "sources": ["hud_fmr", "irs_rental", "ca_rent"]},
        {"cells": ["Q8 — What insurance is available for each intended use?", "No insurer quote, replacement-cost estimate or coverage form is published.", "Primary-residence and landlord/mixed-use underwriting can differ; a price cannot be derived from the state guide.", "Separate written quotes, exclusions, replacement-cost basis, liability, fire/earthquake and any FAIR Plan/DIC gap.", "Licensed insurance broker"], "status": "Missing", "sources": ["cdi"]},
        {"cells": ["Q9 — What are water, electricity, solar-credit and repair costs?", "No bills, tariff, interconnection agreement, inspection or bid is published.", "Solar export credits depend on tariff and interconnection; no household credit or cost can be inferred.", "At least 24 months of utility bills, solar/NEM/NBT agreement, roof/infrastructure inspections, licensed bids.", "Utility / solar provider / contractor"], "status": "Missing", "sources": ["water_board", "cpuc_solar", "cslb"]},
        {"cells": ["Q10 — What are net sale proceeds and selling costs?", "No appraisal, debt payoff, sale contract, fee quote or local transfer-tax schedule is published.", "Do not treat gross sale value as investable cash; basis, debt, costs and tax all matter.", "Broker/closing estimate, debt statement, title search, transfer charges and tax calculation.", "CPA / escrow / attorney"], "status": "Missing", "sources": ["irs_basis", "irs_estate"]},
        {"cells": ["Q11 — Can Property B serve as a residence, and how would any current rent affect the choice?", "The public site includes no B rent amount, lease, permit, inspection or occupancy record; do not infer these facts.", "Do not compare living in B with retaining/renting it until legal and physical suitability, tenant obligations and net rent are confirmed.", "B's lease/tenant records, lawful-unit permits, inspection, title/debt, use-specific insurance, utilities, rent ledger and occupancy plan.", "Landlord-tenant counsel / insurer / property adviser"], "status": "Missing", "sources": ["irs_rental", "ca_rent", "cdi"]},
        {"cells": ["Q12 — What investment policy should apply to any sale proceeds?", "No distribution amount, tax reserve, portfolio or risk tolerance is published.", "The 24–36 month Treasury option is a scenario, not an individualized recommendation.", "Net proceeds, tax reserve, cash needs, allocation policy, fee schedule, net yields and withdrawal plan.", "Fee-only fiduciary investment adviser / CPA"], "status": "Missing", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
    ]
    rows += [
        {"cells": ["Q13 — Reconcile the implied property-tax rates", f"Owner histories imply {implied_rate(A_TAX[2025], A_ASSESS[2025])} for Property A (2025 tax {money(A_TAX[2025])} on {money(A_ASSESS[2025])}) and {implied_rate(B_TAX[2025], B_ASSESS[2025])} for Property B (2025 tax {money(B_TAX[2025])} on {money(B_ASSESS[2025])}) versus the official San Francisco FY2026-27 rate of 1.18162182% and Santa Clara's documented components.", "Property B's implied rate is roughly 0.95 percentage points above the official composite — too large to be explained by known components alone. Property A's rate sits above the countywide component floor and may include flat parcel charges or supplemental amounts.", "The actual secured bills, tax-rate-area code, any supplemental or escape bills, and direct-charge lines for both properties.", "County assessor / tax collector"], "status": "Owner-supplied", "sources": ["sftreasurer_rate", "scc_rate_book", "scc_assessor", "sf_assessor"]},
        {"cells": ["Q14 — Will the family-home exclusion apply at the transfer date?", f"The rule is verified: transferor's principal residence, occupancy within one year, homeowners' exemption within one year, exclusion claim within three years, taxable value capped at full cash value minus the biennially adjusted $1,000,000 amount ({money(CAP_1M_CURRENT)} today). What is not verified is whether the transferor's home meets the principal-residence test and what the cap will be in {TRANSFER_WINDOW}.", "Eligibility is conditional and the cap amount at the actual transfer date is unpublished (next BOE adjustment February 2027).", "Proof of the transferor's residence and occupancy, family relationship, both filed claims, and the BOE cap amount published for the transfer date.", "Assessor / property-tax attorney"], "status": "Missing", "sources": ["boe_lta26026", "boe_lta25009", "ca_rtc63", "boe_prop19"]},
        {"cells": ["Q15 — What can Property A actually rent for, and is a rental lawful?", "No rent comp, permit or lease for Property A exists in the record; HUD FMR values require an interactive lookup and were not retrieved.", f"Renting A cannot be ranked without this number; the tax floor alone is about {money_range(*A_TAX_NO_EXCL)} per year without the exclusion.", "Three written rent comps, legal-unit confirmation, and local rules for the A jurisdiction.", "Property manager / landlord-tenant counsel"], "status": "Missing", "sources": ["hud_fmr", "ca_rent", "irs_rental"]},
        {"cells": ["Q16 — What will insurance actually cost?", f"Owner estimates are {money(A_INSURANCE_OWNER)} and {money(B_INSURANCE_OWNER)} per year. CDI statewide averages were {money(1074)} (owner-occupied, 2017) and {money(519)} (rental dwelling up to four units, 2017); CDI ZIP-level experience for 2018–2023 exists but requires an interactive query.", "Neither the owner estimates nor the statewide averages establish a Bay Area premium; owner-occupied and landlord underwriting differ.", "Two written quotes per property for the intended use, replacement-cost estimates, exclusions and any earthquake or difference-in-conditions decisions.", "Licensed insurance broker"], "status": "Missing", "sources": ["cdi_report", "cdi_ho_avg", "cdi_rental_avg"]},
        {"cells": ["Q17 — How large is the cash portion of the inheritance?", "No estate inventory is published; the federal test is estate-level: $15,000,000 for 2026 deaths and $15,480,000 for 2027 deaths, with 40% above the exclusion.", "Estate-tax exposure, liquidity for any tax due, and the size of the Treasury-staging pool all remain uncomputed.", "Full asset and debt inventory, prior taxable gifts, deductions, executor valuations and any portability facts.", "CPA / estate attorney"], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq", "irs_706"]},
        {"cells": ["Q18 — What is Property A's existing tax basis?", "No purchase price, improvement record or depreciation history is available for the pre-transfer asset.", "Basis becomes the date-of-death value only after death; a pre-death sale by the trustee would use the old basis and could realize a large gain.", "Deed history, improvement records, and the executor's basis statement (consistent-basis rules may require Form 8971 reporting).", "CPA / appraiser"], "status": "Missing", "sources": ["irs_basis", "irs_estate"]},
    ]
    body = callout("Knowns are rounded; answers stay bounded", f"Known and published (rounded to $10): both valuations, both assessment and tax histories, Property B's rent and utility ranges, and the statutory clocks and thresholds. Owner-supplied values are not officially verified; every gap below still needs a document. No address, postal code or identifier is carried into this site.", "info")
    body += make_table("Questions, information required and answer status", ["Question", "Information available", "Answer from verified evidence", "Record needed to close the gap", "Who should confirm"], rows, "Status Owner-supplied means the figure arrived with the request and is rounded to $10; the official source link verifies the cited rule, not the household fact.")
    body += paragraph("Discovery order", "First collect trust and title records, then confirm estate valuation/basis and property-tax deadlines, then verify lawful use and leases, then request independent insurance/repair/utility data, and only then compare after-tax alternatives.")
    return render_page("pages/questions.html", "Questions & missing evidence", "A clear register of what is known at a high level, what is not established, and the document or official rule needed to resolve each question.", body, "DECISION")


def build_projections() -> str:
    body = callout(
        "Scenario arithmetic, not a forecast — case figures rounded to $10",
        f"Owner-supplied starting points: Property A {money(A_VALUE)} and Property B {money(B_VALUE)} (November 2026 estimates). Value bands are explicit assumptions — slow 1–3%, central 3–5%, fast 5–7% per year — informed by FHFA house-price history, not predictions. Assessed values follow the Proposition 13 2% cap. The transfer-state rows use today's dollars and the current {money(CAP_1M_CURRENT)} value cap; the cap at the actual transfer date is unpublished (next BOE adjustment February 2027). Blank means unknown, not zero.",
        "warning",
    )
    for title, base in (
        ("Property A — market value scenarios by year (owner-estimate base)", A_VALUE),
        ("Property B — market value scenarios by year (owner-estimate base)", B_VALUE),
    ):
        value_rows = [
            {
                "cells": [
                    str(year),
                    value_band(base, year, 0.01, 0.03),
                    value_band(base, year, 0.03, 0.05),
                    value_band(base, year, 0.05, 0.07),
                ],
                "status": "Projection",
                "sources": ["fhfa_hpi", "irs_basis"],
            }
            for year in range(2026, 2051)
        ]
        body += make_table(
            title,
            ["Year", "Slow growth (1–3%/yr)", "Central growth (3–5%/yr)", "Fast growth (5–7%/yr)"],
            value_rows,
            "Scenario bands from the owner estimate; FHFA indexes inform the band widths but are not a parcel appraisal or a forecast.",
        )
    pre_rows = []
    for year in range(2026, 2037):
        assessed = assessed_at(A_ASSESS[2026], 2026, year)
        pre_rows.append({
            "cells": [
                str(year),
                money(assessed),
                money(r10(assessed * RATE_A_LO)),
                money(r10(assessed * RATE_A_HI)),
                "Pre-transfer path; the bill at the transfer date depends on the exclusion decision.",
            ],
            "status": "Projection",
            "sources": ["boe_pub29", "scc_rate_book"],
        })
    body += make_table(
        "Property A — assessed value and property tax before the transfer (2% cap)",
        ["Year", "Assessed value", "Tax at 1.05% component floor", "Tax at 1.34% owner-implied rate", "Note"],
        pre_rows,
        "Assessment grown at the Proposition 13 cap from the owner-supplied 2026 value. The floor sums the statutory 1% and documented countywide components; the upper rate is the owner-implied 2025 effective rate. Both ends are planning ranges, not bills.",
    )
    state_rows = [
        {"cells": ["Family-home exclusion claimed and kept", money(r10(A_VALUE - CAP_1M_CURRENT)), money_range(*A_TAX_EXCL), "Occupancy within one year, homeowners' exemption within one year, exclusion claim within three years; the cap amount adjusts every two years by the FHFA California HPI."], "status": "Projection", "sources": ["boe_lta26026", "boe_lta25009", "ca_rtc63"]},
        {"cells": ["No exclusion — rent or hold A without occupying it", money(A_VALUE), money_range(*A_TAX_NO_EXCL), "The full transfer-date full cash value is enrolled, then grows at the 2% cap."], "status": "Projection", "sources": ["boe_lta26026", "scc_rate_book"]},
        {"cells": ["Exclusion lost after occupying (household moves out)", money(A_VALUE), money_range(*A_TAX_NO_EXCL), "BOE guidance: the transfer-date full cash value (new base year value), factored, is enrolled on the following lien date — the advantage ends on moving out."], "status": "Projection", "sources": ["boe_lta26026"]},
        {"cells": ["Annual gap while the exclusion is kept", "—", money_range(*A_TAX_GAP), "Yearly property-tax saving versus full reassessment, in today's dollars."], "status": "Projection", "sources": ["boe_lta26026", "boe_lta25009"]},
    ]
    body += make_table(
        "Property A — property tax at the transfer, by state (today-dollar illustration)",
        ["State at or after transfer", "Taxable value", "Annual property tax", "Condition"],
        state_rows,
        f"Full-cash-value proxy is the {money(A_VALUE)} owner estimate; rate band 1.05%–1.34%. The actual transfer-date value, cap and tax-rate area are not yet known.",
    )
    b_rows = []
    for year in range(2026, 2037):
        assessed = assessed_at(B_ASSESS[2025], 2025, year)
        b_rows.append({
            "cells": [
                str(year),
                money(assessed),
                money(r10(assessed * RATE_B_OFFICIAL)),
                money(r10(assessed * RATE_B_IMPLIED)),
                "Official-rate column uses the FY2026-27 secured rate; the implied column replays the owner's 2025 effective rate. The gap is flagged for bill verification.",
            ],
            "status": "Projection",
            "sources": ["sftreasurer_rate", "boe_pub29"],
        })
    body += make_table(
        "Property B — assessed value and property tax by year (no transfer event)",
        ["Year", "Assessed value (2% cap)", "Tax at official 1.18162182% rate", "Tax at owner-implied 2.14% rate", "Note"],
        b_rows,
        "Property B has no change-in-ownership event, so its existing base year value simply grows at the cap. Both rate columns are shown because the owner-implied rate does not reconcile with the official composite rate.",
    )
    formula_rows = [
        {"cells": ["Market value", "Starting appraisal × (1 + selected scenario growth)^year", "Historical FHFA indexes may help build scenarios but are not a personalized forecast."], "status": "Assumption", "sources": ["fhfa_hpi", "cbo_rates"]},
        {"cells": ["Assessed value / property tax", "Apply current assessment, ownership-change rules, approved exclusions and the bill's non-base components.", "California assessment rules are not equivalent to multiplying market value by one guessed rate."], "status": "Guidance", "sources": ["boe_pub29", "boe_prop19", "ca_rtc63"]},
        {"cells": ["Net rental cash flow", "Collected rent − vacancy/collection loss − tax − insurance − utilities − repairs − management − income tax.", "Use the actual rental ledger, legal rent and tax allocation; separate personal-use and rental-use expenses."], "status": "Guidance", "sources": ["irs_rental", "ca_rent", "hud_fmr"]},
        {"cells": ["Net sale cash", "Sale proceeds − debt payoff − fees − tax due − retained cash reserve.", "The capital-gain basis and estate-tax calculation are distinct analyses."], "status": "Guidance", "sources": ["irs_basis", "irs_estate"]},
        {"cells": ["Real purchasing power", "Nominal future value ÷ cumulative inflation factor.", "Use multiple inflation regimes; one observed CPI year is not a 50-year assumption."], "status": "Guidance", "sources": ["bls_cpi", "cbo_rates"]},
    ]
    body += make_table("Model equations and limitations", ["Output", "Transparent method", "Limit"], formula_rows, "These are model structures, not a numeric forecast. A future-year model should use separate low/base/high assumptions and a dated source or a clearly labeled scenario for every rate.")
    horizon_rows = [
        {"cells": ["Property A — market value", "—", "—", "—", "Use an appraisal at the relevant date; broad FHFA history is a scenario aid, not a valuation."], "status": "Missing", "sources": ["irs_estate", "fhfa_hpi"]},
        {"cells": ["Property A — assessed value and full property tax", "—", "—", "—", "Use the roll, supplemental assessments, direct charges and actual Prop 19 determination."], "status": "Missing", "sources": ["boe_pub29", "boe_prop19"]},
        {"cells": ["Property A — owner-occupied / landlord insurance", "—", "—", "—", "Request quotes for each intended use, replacement cost, exclusions and coverage gap."], "status": "Missing", "sources": ["cdi"]},
        {"cells": ["Property A — utilities and solar credits", "—", "—", "—", "Use provider bills, account tariffs and signed interconnection documents."], "status": "Missing", "sources": ["water_board", "cpuc_solar"]},
        {"cells": ["Property A — maintenance and capital repairs", "—", "—", "—", "Use inspections, service history, licensed bids and a separately stated reserve."], "status": "Missing", "sources": ["cslb", "irs_rental"]},
        {"cells": ["Property A — lawful gross rent / net rental cash flow", "—", "—", "—", "Use legal-unit records, leases, vacancy history, operating costs and tax allocation."], "status": "Missing", "sources": ["hud_fmr", "ca_rent", "irs_rental"]},
        {"cells": ["Property A — net sale proceeds after tax and costs", "—", "—", "—", "Use sale estimate, debt payoff, transaction fees, basis and tax advice."], "status": "Missing", "sources": ["irs_basis", "irs_estate"]},
        {"cells": ["Property B — market value", "—", "—", "—", "Keep this existing asset separate from the expected trust transfer; use date-specific evidence, not a statewide index as appraisal."], "status": "Missing", "sources": ["fhfa_hpi"]},
        {"cells": ["Property B — assessed value and full property tax", "—", "—", "—", "Use the current roll, bill, supplemental assessments, direct charges and any appeals."], "status": "Missing", "sources": ["boe_pub29", "boe_prop19"]},
        {"cells": ["Property B — owner-occupied / landlord insurance", "—", "—", "—", "Request use-specific quotes and current coverage terms; no premium can be projected from a public source."], "status": "Missing", "sources": ["cdi"]},
        {"cells": ["Property B — utilities and solar credits", "—", "—", "—", "Use the actual provider bills and tariff/interconnection record."], "status": "Missing", "sources": ["water_board", "cpuc_solar"]},
        {"cells": ["Property B — maintenance and capital repairs", "—", "—", "—", "Use its own inspection, service history, licensed bids and reserve; do not combine with Property A."], "status": "Missing", "sources": ["cslb", "irs_rental"]},
        {"cells": ["Property B — lawful gross rent / net rental cash flow", "—", "—", "—", "Use its own permits, lease ledger, local rules, vacancy and tax allocation."], "status": "Missing", "sources": ["hud_fmr", "ca_rent", "irs_rental"]},
        {"cells": ["Property B — net sale proceeds after tax and costs", "—", "—", "—", "Use its own sale estimate, debt payoff, transaction fees, basis and tax advice."], "status": "Missing", "sources": ["irs_basis", "irs_estate"]},
    ]
    body += make_table("Blank early / midpoint / late transfer scenarios", ["Separate asset and metric", "Early scenario", "Midpoint scenario", "Late scenario", "Private evidence required"], horizon_rows, "These are relative planning checkpoints, not public dates or a claim about when a transfer occurs. All cells are intentionally blank. Map the stages to actual years only in a private model; do not infer zero or reuse one asset's costs for the other.")
    body += paragraph("Horizon", f"The owner-planned transfer window is {TRANSFER_WINDOW} — a planning assumption, not a confirmed date or a legal forecast. CBO's cited rate outlook runs only through 2036; it cannot responsibly be extended as a fifty-year house-price, inflation, insurance or stock-return forecast. The scenario rows above are arithmetic bands from stated assumptions; use them only alongside private source documents and adviser-approved inputs.")
    return render_page("pages/projections.html", "Projection worksheet", "Year-by-year scenario bands, property-tax cap arithmetic and at-transfer states — all rounded to $10, all badged as owner-supplied or projection, and not a substitute for a private, source-backed spreadsheet built from the actual estate and property records.", body, "NUMBERS")


def build_property_tax() -> str:
    rows = [
        {"cells": ["General levy", "California's general property-tax levy is 1% of assessed value, plus voter-approved bonded indebtedness; other charges may appear on the bill.", "Do not treat the 1% general levy as the complete effective bill rate."], "status": "Verified", "sources": ["boe_pub29"]},
        {"cells": ["Annual assessed-value limit", "Proposition 13 generally limits annual assessed-value growth to no more than 2%, subject to the inflation factor and change-of-ownership/new-construction rules.", "The cap applies to assessed value, not every line of the tax bill; a downturn can also affect enrolled value under other rules."], "status": "Verified", "sources": ["boe_pub29"]},
        {"cells": ["Trust transfer reporting", "RTC §480 requires a change-in-ownership statement within 150 days after death for specified real-property transfers through a trust.", "Trustee/transferee responsibility and the exact filing route must be confirmed for the actual transfer."], "status": "Verified", "sources": ["ca_rtc480"]},
        {"cells": ["Parent-child / grandparent-grandchild family-home exclusion", "Eligibility depends on relationship, the transferor's principal residence, transferee occupancy within 1 year, a filed claim and the adjusted value limit; qualifying grandchild transfers also require the statutory deceased-parent condition.", "The homeowners' exemption generally must be filed within 1 year. A trust distribution alone does not prove an exclusion; a rental-only path may fail the residence condition."], "status": "Verified", "sources": ["boe_prop19", "ca_rtc63"]},
        {"cells": ["Claim window", "BOE guidance says the exclusion claim is generally filed within 3 years of transfer or before a transfer to a third party; the homeowners' exemption has its own 1-year requirement.", "Calendar both deadlines independently; confirm the current form and assessor process at transfer."], "status": "Verified", "sources": ["boe_prop19", "ca_rtc63"]},
        {"cells": ["Actual assessed value, parcel levy and tax bill", "—", "Latest roll, secured bill, supplemental bill, direct charges and any appeal are not publicly reproduced here."], "status": "Missing", "sources": ["boe_pub29", "boe_prop19"]},
    ]
    body = callout("Critical distinction", "Income-tax basis and property-tax assessed value are different systems. A date-of-death basis analysis does not by itself determine the assessed value or a Proposition 19 exclusion.", "info")
    body += make_table("California property-tax rules and missing parcel facts", ["Issue", "Current source-backed rule", "What remains unknown"], rows, "The California BOE warns that statutes and rules change; verify the law and assessor's calculation at the actual transfer.")
    def history_rows(assess: dict, tax: dict, rate_hint: str) -> list[dict]:
        built = []
        years = sorted(assess)
        for index, year in enumerate(years):
            prior = assess[years[index - 1]] if index else None
            change = f"{(assess[year] / prior - 1):+.1%}" if prior else "—"
            tax_cell = money(tax[year]) if tax.get(year) else "— (bill not supplied)"
            rate_cell = implied_rate(tax[year], assess[year]) if tax.get(year) else "—"
            built.append({
                "cells": [str(year), tax_cell, money(assess[year]), change, rate_cell],
                "status": "Owner-supplied",
                "sources": [rate_hint],
            })
        return built

    body += make_table(
        "Property A — owner-supplied assessment and tax history (rounded to $10)",
        ["Year", "Property tax", "Tax assessment", "Assessment change", "Implied effective rate"],
        history_rows(A_ASSESS, A_TAX, "scc_assessor"),
        "Figures arrived with the request, are rounded to the nearest $10 and are not officially verified. Growth matches the Proposition 13 2% cap; the implied rate is the owner tax divided by the owner assessment. Verify each row against the county roll and bill.",
    )
    body += make_table(
        "Property B — owner-supplied assessment and tax history (rounded to $10)",
        ["Year", "Property tax", "Tax assessment", "Assessment change", "Implied effective rate"],
        history_rows(B_ASSESS, B_TAX, "sf_assessor"),
        "Same rounding and status as Property A. Property B has no transfer event, so its history should continue on the 2% cap path shown in the projections.",
    )
    b_official_2025 = r10(B_ASSESS[2025] * RATE_B_OFFICIAL)
    reconciliation_rows = [
        {"cells": ["Property A implied rate versus county components", f"Owner 2025: {money(A_TAX[2025])} on {money(A_ASSESS[2025])} = {implied_rate(A_TAX[2025], A_ASSESS[2025])}. Documented countywide components total about 1.05% before tax-rate-area voter debt.", "Plausible only if the parcel's tax-rate area adds voter-approved debt and/or flat parcel charges, or if the supplied tax includes supplemental amounts.", "Pull the parcel's tax-rate-area code and full bill lines from the county portal; re-run this table."], "status": "Not verified", "sources": ["scc_rate_book", "scc_assessor"]},
        {"cells": ["Property B implied rate versus the official composite", f"Owner 2025: {money(B_TAX[2025])} on {money(B_ASSESS[2025])} = {implied_rate(B_TAX[2025], B_ASSESS[2025])}. Official FY2026-27 composite rate: 1.18162182%, which on the 2025 assessment is about {money(b_official_2025)}.", f"The implied rate exceeds the official composite by about 0.95 percentage points — roughly {money(B_TAX[2025] - b_official_2025)} per year on 2025 values. Known components cannot explain the whole gap.", "Reconcile against the actual bill: direct levies, supplemental or escape charges, arrears, per-unit billing, or a data-source error."], "status": "Not verified", "sources": ["sftreasurer_rate", "sf_assessor"]},
        {"cells": ["2026 Property A bill", "The owner-supplied table stops at a 2026 assessment of " + money(A_ASSESS[2026]) + " with no 2026 tax figure.", "Do not infer the 2026 bill; the first post-request installment figures are not in the record.", "Fetch the current secured bill after it is mailed (first installment due November 1, delinquent December 10)."], "status": "Missing", "sources": ["scc_rate_book", "scc_assessor"]},
    ]
    body += make_table(
        "Rate reconciliation — flagged for review",
        ["Check", "What the numbers say", "Why it matters", "Verification step"],
        reconciliation_rows,
        "These are the arithmetic irregularities found while lining up the owner-supplied histories against official rates. They do not prove an error; they require the bills.",
    )
    body += paragraph("Private records to request", "For each asset separately, obtain the assessor roll, full secured bill, supplemental assessment history, deed and trust transfer documents, homeowners' exemption status, parcel-specific direct levies, tax-rate-area code, and any filed Proposition 19 claims. Do not publish a parcel number or full bill in this public repository — the rounded tables above are the public maximum.")
    return render_page("pages/property-tax.html", "Property-tax rules", "California property-tax mechanics that matter for a future trust transfer, with no address, assessor record or property-specific tax history disclosed.", body, "NUMBERS")


def build_costs() -> str:
    rows = [
        {"cells": ["Property tax", f"Pre-transfer 2026 projection for A: {money_range(r10(A_ASSESS[2026] * RATE_A_LO), r10(A_ASSESS[2026] * RATE_A_HI))}; for B (2026): {money_range(*B_2026_TAX)}. At transfer A moves to the transfer-state ranges on the projections page.", "Pull both full bills including bonds and direct charges; reconcile the flagged rate gaps first."], "status": "Projection", "sources": ["scc_rate_book", "sftreasurer_rate"]},
        {"cells": ["Owner-occupied insurance (A)", f"Owner estimate {money(A_INSURANCE_OWNER)} per year beside CDI's statewide average of {money(1074)} (experience year 2017, owner-occupied policies).", "Request a current homeowners quote with replacement-cost basis, liability and named exclusions; CDI ZIP-level experience for 2018–2023 is available for context."], "status": "Missing", "sources": ["cdi", "cdi_ho_avg", "cdi_report"]},
        {"cells": ["Landlord / mixed-use insurance (B)", f"Owner estimate {money(B_INSURANCE_OWNER)} per year beside CDI's statewide rental-dwelling average of {money(519)} (experience year 2017, policies up to four units).", "Request an underwriting review for the actual legal units, occupancy, leases, vacancy and fire, earthquake and liability coverage."], "status": "Missing", "sources": ["cdi", "cdi_rental_avg", "cdi_report"]},
        {"cells": ["Water / wastewater", f"A: {money_range(*A_WATER)} per month (owner). B: {money_range(*B_WATER)} per month for all {B_UNITS} units (owner).", "Use the actual provider bills and current tariff; the statewide drinking-water program does not state a household rate."], "status": "Owner-supplied", "sources": ["water_board"]},
        {"cells": ["Electricity and solar credit", f"A: net credit of $120–$240 per month with solar installed (owner range {money_range(*A_SOLAR)}). B: {money_range(*B_ELEC)} per month (owner).", "Use actual bills and interconnection or tariff documents; NEM and NBT credit rules differ and export credits under NBT are usually below retail."], "status": "Owner-supplied", "sources": ["cpuc_solar"]},
        {"cells": ["Rent, vacancy and collections", f"B: {money(B_RENT_MONTH)} per month gross from {B_RENTED_UNITS} of {B_UNITS} units ({money(B_RENT_MONTH * 12)} per year, owner). A rent is blank.", "Use lawful leases and the rent ledger; confirm Rent Ordinance coverage and the current allowable increase; HUD FMR is only a benchmark."], "status": "Owner-supplied", "sources": ["sf_rent", "hud_fmr", "irs_rental"]},
        {"cells": ["Repairs and capital maintenance", "Blank — no inspection or bid exists. Planning placeholders only: A $15,500–$31,000 per year (0.5%–1.0% of value); B $9,000–$18,000 per year.", "Get inspection reports and itemized bids from licensed contractors; replace the placeholders before any decision."], "status": "Assumption", "sources": ["cslb", "irs_rental"]},
        {"cells": ["Rental income tax and deductions", "Not computed. California taxes capital gains and rent as ordinary income (1%–9.3% statutory tiers plus 1% above $1,000,000); federal rates plus the 3.8% net investment income tax can also apply.", "Ask a CPA to classify personal versus rental use, allowable expenses, depreciation, sale basis and reporting year."], "status": "Guidance", "sources": ["irs_rental", "irs_1041", "rtc17041", "rtc17043", "ftb_cg", "irs_niit"]},
    ]
    body = callout(
        "Rounded owner figures are now shown — still not officially verified",
        f"Every case amount below is owner-supplied and rounded to the nearest $10. Official CDI statewide averages sit beside the insurance estimates for context. Bills, quotes and bids remain the only acceptable verification, and no address, postal code or account identifier appears anywhere on this site.",
        "warning",
    )
    a_rows = [
        {"cells": ["Property tax (2026, pre-transfer)", money_range(r10(A_ASSESS[2026] * RATE_A_LO), r10(A_ASSESS[2026] * RATE_A_HI)), "2% cap from the owner-supplied 2026 assessment at the 1.05%–1.34% rate band."], "status": "Projection", "sources": ["scc_rate_book", "boe_pub29"]},
        {"cells": ["Water", f"{money_range(*A_WATER)} per month ({money_range(A_WATER[0] * 12, A_WATER[1] * 12)} per year)", "Owner-supplied range; verify against provider bills."], "status": "Owner-supplied", "sources": ["water_board"]},
        {"cells": ["Solar electricity credit (net)", "$120–$240 per month credit (owner range $10–$20)", "Owner reports a small net profit; NEM or NBT tariff rules must be confirmed from account documents."], "status": "Owner-supplied", "sources": ["cpuc_solar"]},
        {"cells": ["Home insurance", f"Owner estimate {money(A_INSURANCE_OWNER)} per year; CDI statewide average {money(1074)} (2017)", "Neither figure is a Bay Area quote; two written quotes are required."], "status": "Missing", "sources": ["cdi_ho_avg", "cdi_report"]},
        {"cells": ["Maintenance and repairs", "Blank — planning placeholder $15,500–$31,000 per year", "Owner says maintenance is lower than Property B's; replace with inspection bids."], "status": "Assumption", "sources": ["cslb"]},
        {"cells": ["Cash cost before maintenance and income tax", money_range(8_240, 10_560), "Tax + water \u2212 solar credit + owner insurance, low and high ends."], "status": "Projection", "sources": ["scc_rate_book", "water_board", "cpuc_solar", "cdi_ho_avg"]},
    ]
    body += make_table(
        "Property A — annual operating picture (today dollars, rounded to $10)",
        ["Line item", "Amount", "Basis and status"],
        a_rows,
        "At the transfer, property tax moves to the transfer-state ranges on the projections page; all other lines continue unless the use changes.",
    )
    b_rows = [
        {"cells": ["Gross rent (2 of 3 units)", f"{money(B_RENT_MONTH * 12)} per year ({money(B_RENT_MONTH)} per month)", "Owner-supplied; the third unit is owner-occupied. Rent control may cap increases."], "status": "Owner-supplied", "sources": ["sf_rent", "irs_rental"]},
        {"cells": ["Property tax (2026)", money_range(*B_2026_TAX), "Official-rate end versus owner-implied-rate end; the gap is flagged for bill verification."], "status": "Projection", "sources": ["sftreasurer_rate", "scc_assessor"]},
        {"cells": ["Water (all units)", money_range(3_960, 4_800) + " per year", "Owner monthly range multiplied by twelve."], "status": "Owner-supplied", "sources": ["water_board"]},
        {"cells": ["Electricity", money_range(360, 840) + " per year", "Owner monthly range multiplied by twelve."], "status": "Owner-supplied", "sources": ["water_board"]},
        {"cells": ["Insurance", f"Owner estimate {money(B_INSURANCE_OWNER)} per year; CDI statewide rental average {money(519)} (2017)", "Landlord policy required for the rented units; two written quotes are required."], "status": "Missing", "sources": ["cdi_rental_avg", "cdi_report"]},
        {"cells": ["Property management (placeholder)", money(6_860) + " per year", "8% of gross rent — assumption only; replace with a management agreement."], "status": "Assumption", "sources": ["irs_rental"]},
        {"cells": ["Maintenance (placeholder)", money_range(9_000, 18_000) + " per year", "0.5%–1.0% of the owner value estimate — assumption only; replace with inspection bids."], "status": "Assumption", "sources": ["cslb"]},
        {"cells": ["Net before maintenance, management and income tax", money_range(76_170, 78_600), "Gross rent minus water, electricity, property tax and owner insurance, low and high ends."], "status": "Projection", "sources": ["sf_rent", "sftreasurer_rate", "water_board"]},
        {"cells": ["Net after the management and maintenance placeholders", money_range(51_310, 62_740), "Still before federal and California income tax, vacancy and capital repairs; the placeholders dominate the width of this range."], "status": "Assumption", "sources": ["irs_rental", "cslb", "ftb_cg"]},
    ]
    body += make_table(
        "Property B — annual operating picture (today dollars, rounded to $10)",
        ["Line item", "Amount", "Basis and status"],
        b_rows,
        "Property B already operates; these owner-supplied figures are the baseline the inherited-property choices are compared against.",
    )
    body += make_table("Operating-cost verification checklist", ["Cost / income line", "Current public amount", "How to verify privately"], rows, "Every row still requires the private record named in the last column, even where a rounded figure is shown.")
    body += cards("Coverage and use checks", [
        ("Insurance gap", "The state explains that the FAIR Plan has limited covered perils; compare standard coverage and any DIC policy rather than treating a FAIR Plan policy as complete coverage.", "pages/sources.html"),
        ("Solar tariff", "Determine interconnection date, NEM/NBT tariff, true-up rules and export-credit treatment from the account records.", "pages/sources.html"),
        ("Rental use", "Confirm permitted units, local rent restrictions, deposits and lease terms before applying projected gross rent.", "pages/questions.html"),
    ], current="pages/operating-costs.html")
    return render_page("pages/operating-costs.html", "Costs, insurance and utility evidence", "Annual operating pictures for both properties with owner figures rounded to $10, official CDI averages for context, and a verification checklist for everything still unconfirmed.", body, "NUMBERS")


def build_black_swan() -> str:
    rows = [
        {"cells": ["1929–1954 equity collapse and recovery", "Federal Reserve History reports the Dow fell 89% from peak to trough and did not regain its previous high until November 1954.", "Long drawdowns and delayed nominal recovery are possible. The Dow is a price index, not an after-dividend diversified portfolio."], "status": "Historical", "sources": ["fed_1929"]},
        {"cells": ["2007–2009 Great Recession", "Federal Reserve History reports an approximately 57% S&P 500 peak-to-trough decline and about a 30% average U.S. home-price decline from prior peaks.", "Equity and housing risk can overlap in a broad crisis; national averages do not predict a specific property."], "status": "Historical", "sources": ["fed_2008"]},
        {"cells": ["Inflation shock", "BLS reports CPI rose 9.1% in the 12 months through June 2022, the largest 12-month increase since November 1981.", "A single high-inflation year can erode purchasing power and raise replacement/repair costs; it is not an annual forecast."], "status": "Historical", "sources": ["bls_cpi"]},
        {"cells": ["Near-term interest-rate baseline and stress", "CBO's 2026–2036 outlook gives a 4.3% average 10-year Treasury rate, with 4.8% and 5.8% higher-rate scenarios.", "Useful only as a near-term macro anchor; not a 50-year bond yield, mortgage rate, housing-growth rate or portfolio return."], "status": "Verified", "sources": ["cbo_rates"]},
        {"cells": ["Long-run housing variation", "FHFA publishes state and metro house-price indexes over different windows.", "An index is not an address-level forecast. Do not apply a metro return mechanically to a private parcel."], "status": "Verified", "sources": ["fhfa_hpi"]},
        {"cells": ["Great Depression deflation", "BLS reports the all-items CPI fell 27.4% from October 1929 to April 1933, with annual average declines of 9.0% in 1931 and 9.9% in 1932.", "Nominal declines of this depth hit cash flows, rents and asset prices together; a fifty-year plan must survive deflation years, not only inflation years."], "status": "Historical", "sources": ["bls_mlr100", "bls_hist"]},
        {"cells": ["1970s–early 1980s inflation regime", "BLS annual average CPI changes: 11.0% (1974), 11.3% (1979), 13.5% (1980), 10.3% (1981).", "Sustained high inflation raises replacement and repair costs while eroding fixed-income purchasing power — stress more than one year at a time."], "status": "Historical", "sources": ["bls_hist"]},
        {"cells": ["Current inflation versus the policy target", "The Federal Reserve's longer-run objective is 2% PCE inflation; the latest displayed reading is 3.6% for September 2026.", "Today's gap matters for near-term yields, insurance and rent; it is an observation, not a projection of the next decade."], "status": "Verified", "sources": ["fed_pce"]},
        {"cells": ["Interest-rate regime shift inside one year", "The official daily par curve shows the 10-year at 4.19% on January 2, 2026; CBO reports it closed at 5.2% on October 1, 2026; TreasuryDirect's latest posted 10-year auction was 5.000% when checked November 15, 2026.", "Rate paths are not smooth: staging yields, renewal yields and borrowing costs can move substantially within the 24–36 month staging window itself."], "status": "Historical", "sources": ["treasury_curve", "cbo_rates", "treasury_notes"]},
    ]
    regimes = [
        {"cells": ["Inflation surge / purchasing-power loss", "CPI rose 9.1% over the year through June 2022; this is a single observed 12-month window.", "Stress one or more years at a user-selected inflation rate, but do not repeat 9.1% for decades as if it were a forecast. Higher replacement and repair costs can compress real cash flow."], "status": "Historical", "sources": ["bls_cpi", "cslb"]},
        {"cells": ["Deflation / nominal decline", "The CPI fell 27.4% between October 1929 and April 1933 (BLS) and the annual average fell 0.4% in 2009.", "Test flat-to-falling rents and values alongside falling yields: property tax is assessed on the capped base, so a nominal decline squeezes net cash flow from both sides."], "status": "Historical", "sources": ["bls_mlr100", "bls_hist"]},
        {"cells": ["Equity drawdown during staging", "The 1929 Dow and 2007–09 S&P 500 episodes supply two severe historical drawdown endpoints.", "The tool tests a synthetic crash starting halfway through staging. It does not replay either index's daily path or include dividends."], "status": "Historical", "sources": ["fed_1929", "fed_2008"]},
        {"cells": ["Equity drawdown after staging", "The same source-reported drawdown can begin after all scheduled purchases are complete.", "Compare with the early-crash case; phasing no longer preserves as much uninvested Treasury cash when the loss starts."], "status": "Historical", "sources": ["fed_1929", "fed_2008", "treasury_bills"]},
        {"cells": ["Lower short-rate renewals", "Each Treasury auction sets the rate for the new security; future renewal rates are not known today.", "Enter a lower second-year yield than first-year yield to expose reinvestment risk. This is a what-if, not a rate prediction."], "status": "Assumption", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Rising market before a crash", "No official source in this workspace establishes future equity returns or their sequence.", "Enter a positive pre-crash drift to test opportunity cost while staging; this is a scenario assumption, not an expected-return estimate."], "status": "Assumption", "sources": ["sec_stocks"]},
        {"cells": ["Higher nominal rate regime", "CBO's near-term 2026–2036 outlook uses 4.3% average 10-year Treasury rates and 4.8%/5.8% higher-rate scenarios.", "Use only as a short-horizon macro reference; do not substitute these rates for far-future Treasury yields, mortgage costs or portfolio returns."], "status": "Verified", "sources": ["cbo_rates"]},
        {"cells": ["Housing slump / flat property market", "Fed History reports about a 30% average U.S. home-price decline from mid-2006 to mid-2009; FHFA provides broad regional indexes.", "Use a separate low-growth/flat/decline housing scenario. National and regional indexes are not a parcel forecast."], "status": "Historical", "sources": ["fed_2008", "fhfa_hpi"]},
        {"cells": ["Insurance availability / repair shock", "No public source establishes a future premium, local underwriting decision or repair bill for either asset.", "Treat coverage loss, deductible changes and large repairs as explicit blank or quote-based stress inputs; do not insert a generic percentage."], "status": "Missing", "sources": ["cdi", "cslb"]},
    ]
    body = callout("A single constant growth rate is not a 50-year economic model", f"Everything at stake in this case moves with those regimes: the inherited house is worth about {money(A_VALUE)} today, the already-owned house about {money(B_VALUE)}, the already-owned property throws off {money(B_RENT_MONTH * 12)} per year in gross rent, and the sell-and-stage path would put roughly {money_range(A_VALUE * 0.93, A_VALUE * 0.95)} of proceeds through 24–36 months of Treasury parking before equity entry. Inflation, interest rates, housing prices, insurance availability, rents and equity returns move in different regimes, and the official outlooks cited here are at most near-term anchors — no official source supplies a fifty-year household path.", "warning")
    body += make_table("Measured historical anchors — not forecasts", ["Episode / source window", "Officially reported observation", "How to use it"], rows)
    body += make_table("Economic regime stress map", ["Regime", "Evidence or status", "What to test"], regimes, "Historical episodes are observations, not probabilities. Assumption rows are user-controlled stress paths, not predictions. Property-specific costs remain blank until quoted.")
    body += paragraph("Stress dimensions to combine", "Test equity declines before, during and after Treasury staging; lower renewal yields; high inflation; stagnant housing prices; property-tax reassessment; insurance nonrenewal or coverage gaps; repair spikes; vacancy and rent limits; and liquidity needs. Treat joint shocks as stress cases, not independent probabilities. The comparison tool models entry timing plus user-entered yields, pre-crash drift and inflation; it does not claim to replay the whole economy.")
    body += cards("Run the entry-risk comparison", [
        ("24–36 month Treasury staging", "Compare a historical crash during staging with one after staging, and change renewal yields locally in your browser.", "pages/phased-investing.html"),
        ("Law and assumptions", "Use current official law only for present-day rules; refresh tax thresholds and costs at the actual event.", "pages/law-watchlist.html"),
    ], current="pages/black-swan.html")
    return render_page("pages/black-swan.html", "Black-swan economic conditions", "Historical evidence for uneven growth, inflation and market shocks, with strict limits on what those episodes can say about a future property or portfolio.", body, "STRESS TESTS")


def build_phased_investing() -> str:
    body = callout("Reinvestment risk belongs beside the headline", "Treasury bills and notes have fixed auction rates for their terms. When a short holding matures, the next auction yield may be lower; staging can therefore reduce early equity exposure yet leave more money earning less. A rising market can also make phased buying lag a lump-sum investment.", "warning")
    instrument_rows = [
        {"cells": ["Treasury bills", "4–52 week terms; rate fixed at auction; interest is federally taxable and exempt from state/local taxes; can be sold before maturity.", "A 3-month ladder requires reinvestment at future auction rates; early sale can have a different price."], "status": "Verified", "sources": ["treasury_bills"]},
        {"cells": ["Treasury notes", "2-, 3-, 5-, 7- and 10-year terms; a 2-year note can span the staging horizon; interest is federally taxable and exempt from state/local taxes.", "A note sold before maturity may have a market price different from par; decide whether to hold to maturity or sell."], "status": "Verified", "sources": ["treasury_notes"]},
    ]
    body += make_table("Instrument facts", ["Instrument", "Official product terms", "Decision risk"], instrument_rows)
    yield_rows = [
        {"cells": ["3-month par yield", "3.65%", "January 2, 2026", "Short-parking reference for the staging window"], "status": "Verified", "sources": ["treasury_curve"]},
        {"cells": ["6-month par yield", "3.61%", "January 2, 2026", "Short-parking reference for the staging window"], "status": "Verified", "sources": ["treasury_curve"]},
        {"cells": ["1-year par yield", "3.55%", "January 2, 2026", "Default for the tool's months 1–12 input"], "status": "Verified", "sources": ["treasury_curve"]},
        {"cells": ["2-year par yield", "3.47%", "January 2, 2026", "Default for the tool's renewal input"], "status": "Verified", "sources": ["treasury_curve"]},
        {"cells": ["10-year par yield", "4.19%", "January 2, 2026", "Context for the longer end of any ladder"], "status": "Verified", "sources": ["treasury_curve"]},
        {"cells": ["10-year Treasury close", "5.2%", "October 1, 2026", "Shows how far yields moved inside the same year"], "status": "Verified", "sources": ["cbo_rates"]},
        {"cells": ["Latest posted 10-year note auction", "5.000%", "Posted November 15, 2026", "Auction results, not secondary par yields; re-check before investing"], "status": "Verified", "sources": ["treasury_notes"]},
    ]
    body += make_table(
        "Dated reference yields for the staging decision",
        ["Reference point", "Rate", "As of", "How to use it"],
        yield_rows,
        "Official readings on specific dates — not forecasts. Replace both tool inputs with the net yields actually available on the decision date; taxes and fees are not modeled by the tool.",
    )
    body += make_table(
        "Worked example — 30-month staging at the reference yields, zero drift",
        ["Drawdown anchor", "Crash timing", "Horizon", "Immediate investment (end)", "Phased investment (end)", "Max drawdown — immediate", "Max drawdown — phased"],
        phase_worked_rows(),
        "Same model as the live tool: 100 starting units, equal monthly equity purchases, reference yields of 3.55% then 3.47%, zero drift, zero inflation, synthetic linear crash. Phasing clearly helps only when the crash begins during staging; when it begins afterwards the two paths converge, and a rising pre-crash market makes phasing lag.",
    )
    body += '''<section class="tool-section" aria-labelledby="tool-heading">
<h2 id="tool-heading">Crash-entry what-if — normalized units, not dollars</h2>
<p class="table-note">The starting portfolio is normalized to 100 index units so no household amount is embedded. Historical drawdown endpoints are sourced, but the path between peak and trough is synthetic and linear. Controls model a rising pre-crash market, separate first-year and renewal Treasury yields, and inflation-adjusted purchasing power. Enter the Treasury yield net of estimated taxes and fees; the tool does not calculate taxes. This is not a historical total-return replay and sends or stores no calculator inputs.</p>
<form id="phase-tool" class="tool-grid">
<label>Historical drawdown anchor<select id="phase-event"><option value="1929">1929 Dow episode</option><option value="2008" selected>2007–09 S&amp;P episode</option></select></label>
<label>Purchase staging period<select id="phase-months"><option value="24">24 months</option><option value="30" selected>30 months</option><option value="36">36 months</option></select></label>
<label>Peak-to-trough decline (%)<input id="phase-drawdown" type="number" min="0" max="99" step="1" value="57" inputmode="decimal"></label>
<label>Peak-to-trough duration (months)<input id="phase-trough" type="number" min="1" max="120" step="1" value="17" inputmode="numeric"></label>
<label>Pre-crash equity drift (%/year)<input id="phase-drift" type="number" min="-20" max="30" step="0.1" value="0" inputmode="decimal"></label>
<label>Net Treasury yield, months 1–12 (%)<input id="phase-yield1" type="number" min="-5" max="20" step="0.01" value="3.55" inputmode="decimal"></label>
<label>Net renewal yield, month 13 onward (%)<input id="phase-yield2" type="number" min="-5" max="20" step="0.01" value="3.47" inputmode="decimal"></label>
<label>Annual inflation for purchasing-power lens (%)<input id="phase-inflation" type="number" min="-5" max="20" step="0.1" value="0" inputmode="decimal"></label>
<div class="tool-actions no-print"><button id="phase-reset" type="button">Reset assumptions</button><span class="tool-assumption">Default yields are the dated January 2, 2026 par-curve reference (3.55% / 3.47%) — replace them with net yields available on the decision date. Zero drift and zero inflation isolate timing.</span></div>
</form>
<div class="scenario-grid" aria-live="polite">
<article class="scenario-card"><h3>Crash begins during the staging window</h3><p>Crash starts halfway through staging; results are shown at the later of investment completion or the modeled trough.</p><dl><dt>Observation horizon</dt><dd id="early-months">—</dd><dt>Immediate investment — nominal</dt><dd id="early-immediate-value">—</dd><dt>Phased investment — nominal</dt><dd id="early-phased-value">—</dd><dt>Immediate investment — real units</dt><dd id="early-immediate-real">—</dd><dt>Phased investment — real units</dt><dd id="early-phased-real">—</dd><dt>Maximum drawdown — immediate</dt><dd id="early-immediate-dd">—</dd><dt>Maximum drawdown — phased</dt><dd id="early-phased-dd">—</dd></dl></article>
<article class="scenario-card"><h3>Crash begins after staging completes</h3><p>All scheduled purchases are complete before the same decline begins.</p><dl><dt>Observation horizon</dt><dd id="late-months">—</dd><dt>Immediate investment — nominal</dt><dd id="late-immediate-value">—</dd><dt>Phased investment — nominal</dt><dd id="late-phased-value">—</dd><dt>Immediate investment — real units</dt><dd id="late-immediate-real">—</dd><dt>Phased investment — real units</dt><dd id="late-phased-real">—</dd><dt>Maximum drawdown — immediate</dt><dd id="late-immediate-dd">—</dd><dt>Maximum drawdown — phased</dt><dd id="late-phased-dd">—</dd></dl></article>
</div>
<p id="phase-status" class="tool-status" role="status">Change a control to run the local-only comparison.</p>
<p class="table-note">Model boundary: equal monthly equity purchases from the initial 100 units; Treasury reserve accrues the entered yield by month and uses the renewal yield after month 12; the final purchase includes any accrued reserve. Equity grows at the entered drift until the crash, declines linearly to the selected drawdown, then stays flat at its trough. Real units divide by the selected constant annual inflation factor. There are no dividends, fees, taxes, post-trough recovery, withdrawals, property costs or probabilities. The default yields are the dated January 2, 2026 reference above; zero drift and zero inflation isolate timing only. Nothing here is a forecast.</p>
</section>'''
    rows = [
        {"cells": ["1929 anchor", "Federal Reserve History reports an 89% Dow peak-to-trough decline; the previous high was not regained until November 1954.", "The calculator starts from the Dow drawdown only; it does not copy daily prices or include dividends."], "status": "Historical", "sources": ["fed_1929"]},
        {"cells": ["2008 anchor", "Federal Reserve History reports a 57% S&P 500 peak-to-trough decline from October 2007 to March 2009.", "The calculator uses this as a source-calibrated shock magnitude, not a forecast or a return series."], "status": "Historical", "sources": ["fed_2008"]},
        {"cells": ["Reinvestment risk", "The next Treasury auction rate is not known when today's bill matures; Treasury product pages state the rate is fixed at auction.", "Run a lower renewal-yield case as well as the zero-yield isolation case."], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Inflation / real-value lens", "BLS reports 9.1% CPI inflation over the year through June 2022; that was one observed year, not a long-run rate.", "Enter an explicit inflation stress and compare nominal units with purchasing-power units; do not repeat a single historical shock as a forecast."], "status": "Historical", "sources": ["bls_cpi"]},
        {"cells": ["Equity risk", "The SEC warns stock prices can fall and stock investors can lose money.", "No expected return, probability, tax rate or personal allocation is inferred by this page."], "status": "Verified", "sources": ["sec_stocks"]},
    ]
    body += make_table("How to read the calculator", ["Point", "Source-backed fact", "Limit / next test"], rows)
    body += paragraph("Interpretation", "A staged plan can buy more shares during an early falling market because later installments purchase at lower index values. If the same decline starts after staging ends, all proceeds are already exposed. A positive pre-crash drift control tests one rising-market opportunity-cost scenario, but it is a constant synthetic rate rather than a historical return series. Use actual after-tax yields and an adviser-approved investment policy before making a real allocation.")
    return render_page("pages/phased-investing.html", "Treasury staging and phased stock entry", "A source-calibrated, assumption-led stress comparison for parking sale proceeds in 3-month to 2-year Treasuries for 24–36 months after the transfer, then phasing into stocks — with a published worked example and dated reference yields. Not an individualized investment recommendation.", body, "STRESS TESTS")


def build_estate_thresholds() -> str:
    rows = [
        {"cells": ["Federal basic exclusion — 2026 deaths", "$15,000,000", "Filing threshold is tested against gross estate plus adjusted taxable gifts and specific gift-tax exemption; other filing triggers can apply."], "status": "Verified", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["Federal basic exclusion — 2027 deaths", "$15,480,000", "The IRS announced this amount for 2027. It is the next-year threshold, not a future-year projection."], "status": "Verified", "sources": ["irs_2027"]},
        {"cells": ["Annual gift exclusion — 2026", "$19,000 per donor/recipient", "A gift-tax annual exclusion is separate from the lifetime estate/gift basic exclusion and is not an inheritance allowance."], "status": "Verified", "sources": ["irs_2027"]},
        {"cells": ["Annual gift exclusion — 2027", "$20,000 per donor/recipient", "The annual exclusion does not cap an inheritance and does not determine estate tax by itself."], "status": "Verified", "sources": ["irs_2027"]},
        {"cells": ["California state/local death-transfer tax", "Current RTC §13301 bars a state or political subdivision tax on a transfer by reason of death; the Controller says no CA Estate Tax return is required for deaths on/after 2005-01-01.", "Current law only; no future exemption or tax amount can be forecast for a later death."], "status": "Verified", "sources": ["ca_rtc13301", "ca_death_tax"]},
        {"cells": ["Household estate headroom", "The cash and asset portion of this inheritance is not published; the owner notes it could exceed the exclusion.", "Without the inventory the headroom cannot be calculated — use the illustrative table below until the CPA produces the estate schedule."], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq"]},
    ]
    body = callout("The threshold is not per heir", "Federal estate tax is an estate-level transfer tax. The IRS filing test uses the decedent's gross estate, adjusted taxable gifts and specific gift-tax exemption; a portability election can require a return below the threshold. A recipient's share alone cannot establish whether a return is required or tax is due.", "info")
    body += make_table("Current official thresholds and missing household calculation", ["Rule / year", "Official value or rule", "What it means here"], rows)
    illustration_rows = []
    for estate in (16_000_000, 18_000_000, 20_000_000):
        tax_2026 = r10(0.40 * (estate - 15_000_000))
        tax_2027 = r10(0.40 * (estate - 15_480_000))
        illustration_rows.append({
            "cells": [money(estate), money(tax_2026), money(tax_2027),
                      "Assumes a 2026 or 2027 death, taxable estate equal to this figure, no other credits and the 40% marginal rate above the exclusion. Illustration only."],
            "status": "Projection",
            "sources": ["irs_706", "irs_estate"],
        })
    body += make_table(
        "Illustrative federal estate tax above the exclusion (rounded to $10)",
        ["Illustrative taxable estate", "Tax if death in 2026 (exclusion $15,000,000)", "Tax if death in 2027 (exclusion $15,480,000)", "What the arithmetic assumes"],
        illustration_rows,
        "Marginal rate of 40% above the basic exclusion, taken from the IRS unified rate schedule; the estate — not each heir — pays any tax, and deductions, prior gifts, portability and valuation rules can change the result. Replace every figure with the CPA's schedule once the inventory exists.",
    )
    body += paragraph("Future law", "The Working Families Tax Cuts (Public Law 119-21, enacted July 4, 2025) set the basic exclusion at $15,000,000 for 2026, and the IRS announced $15,480,000 for 2027. Nothing in the record establishes the amount for a death around the owner-planned transfer window, and no official source here indexes the exclusion that far. Do not compound today's exclusion forward; re-check the Internal Revenue Code, the annual IRS revenue procedure, California statutes and any enacted amendments in the actual year of death.")
    return render_page("pages/estate-thresholds.html", "Estate tax, gift exclusion and headroom", "Federal thresholds currently verified from IRS sources, California death-tax law, and the specific facts still required to determine estate exposure.", body, "LAW & PROCESS")


def build_process() -> str:
    rows = [
        {"cells": ["At death / trust becomes irrevocable", "If the statutory trigger applies, trustee notice is generally due within 60 days; the duty and recipients depend on Probate Code §16061.7.", "Trustee / counsel", "Collect trust, amendments, trustee authority and beneficiary notice records."], "status": "Verified", "sources": ["ca_prob160617"]},
        {"cells": ["Within 150 days after death", "RTC §480 requires a change-in-ownership statement for specified real property transferred by reason of death, including a trust transfer.", "Trustee / transferee / assessor", "Confirm county filing route and obtain proof of filing; the actual responsibility depends on the transfer."], "status": "Verified", "sources": ["ca_rtc480"]},
        {"cells": ["Within 9 months after death", "Form 706 is due if required. IRS says an extension request of up to 6 months can be made by filing Form 4768 by the due date.", "Executor / CPA", "Determine the filing requirement and tax-payment/election deadlines separately; this row states the filing clock only."], "status": "Verified", "sources": ["irs_estate_faq"]},
        {"cells": ["Within 1 year of qualifying transfer", "For a qualifying family home, the transferee generally must establish principal residence and file the homeowners' or disabled veterans' exemption within one year.", "Transferee / assessor", "Verify the relationship, qualifying transferor residence, trust/title facts, occupancy and filed exemption."], "status": "Verified", "sources": ["boe_prop19", "ca_rtc63"]},
        {"cells": ["Within 3 years of transfer, or before third-party transfer", "BOE guidance describes this claim window for the intergenerational exclusion; the separate one-year residence/exemption condition still matters.", "Transferee / assessor", "Calendar both claims; obtain current forms and written assessor confirmation."], "status": "Verified", "sources": ["boe_prop19", "ca_rtc63"]},
        {"cells": ["Annual income-tax return, if required", "A fiduciary may need Form 1041 for estate/trust income, deductions, gains, losses and distributions; the applicable due date depends on the filing year and entity facts.", "Trustee / CPA", "Identify the tax year, EIN, income and distribution reporting; confirm the current form instructions."], "status": "Guidance", "sources": ["irs_1041"]},
        {"cells": ["Before occupancy, rental, sale or reinvestment", "No single universal statutory date is asserted for this operational gate.", "Trustee / attorney / insurer / CPA", "Bind proper insurance, verify legal use and leases, reserve taxes/repairs, and approve a written path before taking on risk."], "status": "Guidance", "sources": ["cdi", "ca_rent", "irs_rental"]},
    ]
    body = callout("Start clocks only from their legal trigger", "These deadlines are not interchangeable. A trust-notice clock, county property-tax filing, federal estate return and Proposition 19 claims can have different triggers and responsible filers. Counsel should confirm the actual dates from the death and transfer records. The owner-planned transfer window is " + TRANSFER_WINDOW + " — a planning assumption, not a confirmed date.", "warning")
    body += SafeHTML('''<section class="prose"><h2>Step-by-step sequence</h2>
<ol class="timeline">
<li><strong>Death of the transferor</strong> — the revocable trust becomes irrevocable and every clock below starts (owner-planned window: ''' + TRANSFER_WINDOW + ''', planning assumption only).</li>
<li><strong>Within 60 days</strong> — trustee serves the notification on beneficiaries and heirs (Probate Code §16061.7).</li>
<li><strong>Within 150 days</strong> — change-in-ownership statement filed with the county recorder or assessor for the trust transfer (Revenue and Taxation Code §480).</li>
<li><strong>Within 1 year</strong> — transferee occupies the inherited house as a principal residence and files the homeowners' exemption — the first Proposition 19 claim step.</li>
<li><strong>Within 9 months (extendable by 6)</strong> — Form 706 filed if the estate meets the filing test or a portability election is needed.</li>
<li><strong>Within 3 years</strong> — Proposition 19 exclusion claim filed, or earlier if occupancy ends or the property passes to a third party.</li>
<li><strong>Every fiscal year</strong> — secured property-tax installments (due November 1 and February 1; delinquent December 10 and April 10) and Form 1041 if the estate or trust has income.</li>
<li><strong>Before any occupancy, rental or sale</strong> — insurance bound, legal use and leases verified, tax reserves set, written path approval from the household and advisers.</li>
<li><strong>After the date-of-death basis attaches</strong> — sell the inherited house or occupy it and complete the exclusion filings; a sale before death would not receive the step-up.</li>
<li><strong>24–36 months after the proceeds arrive</strong> — park in 3-month to 2-year Treasuries while phasing into equities; re-price yields at each auction.</li>
<li><strong>Annually thereafter</strong> — refresh law, assessments, insurance, rents, yields and the suggestion review queue.</li>
</ol></section>''')
    body += make_table("Inheritance and decision timeline", ["Trigger / deadline", "Verified rule", "Responsible party to confirm", "Evidence to retain"], rows)
    calendar_rows = [
        {"cells": ["January 1", "Lien date for all property; the assessment for the fiscal year is fixed.", "Assessor / owner"], "status": "Verified", "sources": ["boe_pub29"]},
        {"cells": ["February 15", "Legal deadline for filing most exemption claims, including the homeowners' exemption.", "Transferee / owner"], "status": "Verified", "sources": ["boe_pub29"]},
        {"cells": ["March 1", "San Francisco rent-increase cycle: the Rent Board publishes a new allowable percentage each year (1.4% for March 1, 2025 – February 28, 2026); a license and inventory report are required first.", "Landlord (Property B)"], "status": "Verified", "sources": ["sf_rent"]},
        {"cells": ["April 10", "Second secured installment delinquent (10% penalty plus fees).", "Taxpayer"], "status": "Verified", "sources": ["boe_pub29", "sftreasurer_rate", "scc_rate_book"]},
        {"cells": ["July 1", "County assessor must complete the local assessment roll.", "Assessor"], "status": "Verified", "sources": ["boe_pub29"]},
        {"cells": ["July 2 – September 15", "Window to file an application for reduction in assessed value with the county board.", "Owner / tax counsel"], "status": "Verified", "sources": ["boe_pub29", "sf_assessor"]},
        {"cells": ["August 31", "Unsecured taxes delinquent.", "Taxpayer"], "status": "Verified", "sources": ["boe_pub29"]},
        {"cells": ["November 1", "First secured installment due; bills are mailed by this date.", "Taxpayer"], "status": "Verified", "sources": ["scc_rate_book", "sftreasurer_rate"]},
        {"cells": ["December 10", "First secured installment delinquent (10% penalty); also the date to file for 80% of the homeowners' exemption for the year.", "Taxpayer / transferee"], "status": "Verified", "sources": ["boe_pub29", "sftreasurer_rate", "scc_rate_book"]},
    ]
    body += make_table("Annual property-tax and rent calendar", ["Date (each year)", "What happens", "Who acts"], calendar_rows, "Statewide dates from BOE Publication 29; installment mechanics confirmed for both counties on the linked official pages; the San Francisco rent reset is local.")
    body += paragraph("Assign calendar dates privately", "The relative deadlines above become calendar dates only once counsel confirms the date of death, title transfer and trust status. Keep the filled-in calendar, filed proofs and bills in the private record — this public page carries only the relative clocks and the owner-planned window.")
    return render_page("pages/inheritance-process.html", "Inheritance process and deadline timeline", "A relative step-by-step sequence for a trust-based transfer, with official clocks distinguished from operational checkpoints.", body, "LAW & PROCESS")


def build_law_watchlist() -> str:
    rows = [
        {"cells": ["Federal estate and gift amounts", "Use only official year-of-death IRS thresholds and annual gift tables; current 2026/2027 amounts do not determine later law.", "Check enacted federal law and the IRS annual adjustment/revenue procedure near the transfer."], "status": "Guidance", "sources": ["irs_estate", "irs_2027"]},
        {"cells": ["Federal bills and proposals", "No specific pending federal proposal is incorporated into this decision framework. A bill or resolution is not current law merely because it is introduced or debated.", "Search Congress.gov near the event; confirm enactment, effective date and IRS implementation before changing a calculation."], "status": "Not verified", "sources": ["congress_legislation", "irs_estate"]},
        {"cells": ["California property-tax transfer rules", "Review RTC §§480 and 63.2, BOE guidance, any later amendments and the assessor's written determination.", "Check filing forms, value limit, occupancy, relationship and transfer date."], "status": "Guidance", "sources": ["ca_rtc480", "ca_rtc63", "boe_prop19"]},
        {"cells": ["California bills and proposals", "No specific pending California bill is relied on as law. A proposal becomes relevant only after its status, chaptering and effective date are verified.", "Search the official bill system and re-check the enacted code, regulations and BOE guidance at transfer."], "status": "Not verified", "sources": ["ca_legislation", "boe_prop19"]},
        {"cells": ["California death-transfer tax", "Current RTC §13301 and State Controller information describe the current rule; do not assume it cannot change.", "Re-check state law for the actual year of death."], "status": "Guidance", "sources": ["ca_rtc13301", "ca_death_tax"]},
        {"cells": ["Rent and tenant protections", "Statewide Civil Code rules have coverage conditions and exemptions, and San Francisco's Rent Ordinance is identified for Property B (published allowable increase of 1.4% for March 1, 2025 – February 28, 2026, reset each March 1). Property A's Cupertino local rules are not yet mapped.", "Counsel should check each city's code, rent registry, unit status, lease and tenant rights before occupancy or a rent change; verify the current-year San Francisco percentage."], "status": "Guidance", "sources": ["ca_rent", "sf_rent", "ca_legislation"]},
        {"cells": ["Insurance availability and coverage", "Market conditions, underwriting, wildfire/flood risk, exclusions and reconstruction costs may change independently of taxes.", "Refresh written quotes and coverage terms; do not extrapolate an old premium."], "status": "Missing", "sources": ["cdi"]},
        {"cells": ["Investment yields and market entry", "Treasury rates are fixed at each auction for the selected security; stock prices can lose value.", "Reprice the ladder and compare reinvestment and sequence risk immediately before investment."], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
        {"cells": ["Long-run economic assumptions", "CBO's cited interest-rate horizon is 2026–2036; no cited official source provides an individual 50-year house value, insurance price, rent or return forecast.", "Use several clearly labeled stress paths; never promote a scenario into a forecast."], "status": "Guidance", "sources": ["cbo_rates", "fhfa_hpi", "bls_cpi"]},
        {"cells": ["Proposition 19 value-cap amount", f"The $1,000,000 cap component is {money(CAP_1M_CURRENT)} for transfers from February 16, 2025 through February 15, 2027 and is adjusted every other February 16 by the FHFA California House Price Index; the next adjustment is February 2027.", "Re-fetch the BOE letter for the transfer date — a transfer around the owner-planned window will use a different, then-unpublished amount."], "status": "Verified", "sources": ["boe_lta25009", "boe_lta26026"]},
        {"cells": ["San Francisco allowable rent increase", "The published rate was 1.4% for March 1, 2025 – February 28, 2026; the Rent Board resets the percentage each March 1 under the ordinance.", "Verify the current-year percentage, the license requirement and inventory reporting before modeling any rent growth on Property B."], "status": "Verified", "sources": ["sf_rent"]},
        {"cells": ["Federal estate exclusion after 2027", "Public Law 119-21 set $15,000,000 for 2026 and the IRS announced $15,480,000 for 2027; no source here establishes any later amount.", "Check the next annual IRS revenue procedure and any enacted amendments each year; do not index it forward by assumption."], "status": "Missing", "sources": ["irs_estate_faq", "irs_2027", "congress_legislation"]},
        {"cells": ["Inflation and rate path into the decision", "Latest official readings: PCE inflation 3.6% (September 2026) against the Fed's 2% objective; 10-year par yield 4.19% (January 2, 2026) versus a 5.2% close on October 1, 2026.", "Refresh these readings immediately before staging proceeds or signing insurance; a single dated reading is not a trend."], "status": "Verified", "sources": ["fed_pce", "treasury_curve", "cbo_rates"]},
    ]
    body = callout("Watch enacted law, not headlines", "The pages distinguish current statutes and agency tables from bills, stress assumptions and future uncertainty. No bill or proposal is represented as current law. The inherited transfer is far in the future; refresh federal, state and actual local rules near the event.", "info")
    body += make_table("Law and market watchlist", ["Topic", "Current official baseline / proposal status", "What to re-check"], rows)
    body += paragraph("No future-year legal projection", "This site intentionally does not extrapolate federal thresholds or California property-tax allowances to a future year. Pending bills are not incorporated as law. The cities are known at the summary level (Cupertino for Property A, San Francisco for Property B), but city and county code, local ordinances and their amendments must still be re-read from the official systems at the decision date.")
    return render_page("pages/law-watchlist.html", "Law and market watchlist", "A short list of rules and market inputs that can change the decision, without treating a proposed change or long-run projection as settled fact.", body, "LAW & PROCESS")


def build_brief() -> str:
    rows = [
        {"cells": ["Attorney / trustee", "What does the executed trust permit, who may occupy, rent or sell, when does title change, and what debts or notices apply?", "Trust, amendments, deed, trustee authority, debt/lease documents.", "Action needed"], "status": "Action needed", "sources": ["ca_prob160617", "ca_rtc480"]},
        {"cells": ["CPA / estate attorney", "What is the whole estate's gross value, adjusted taxable gifts, deductions and any portability or Form 706 filing requirement?", "Private asset/debt inventory, prior gifts, valuation reports, spouse/portability facts.", "Action needed"], "status": "Action needed", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["CPA / appraiser", "What is the correct date-of-death value, basis, improvement/depreciation record and tax result if sold or rented?", "Appraisal, executor basis statement, improvements, depreciation and sale estimate.", "Action needed"], "status": "Action needed", "sources": ["irs_basis", "irs_rental"]},
        {"cells": ["Property-tax adviser", "Does an eligible family-home exclusion apply, and what statements, occupancy and claims are due?", "Relationship, deed/trust, prior assessment, occupancy proof, exemption and claim dates.", "Action needed"], "status": "Action needed", "sources": ["boe_prop19", "ca_rtc63", "ca_rtc480"]},
        {"cells": ["Landlord-tenant counsel", "Which units are legal, what local/state rules apply, what do current leases require, and which mixed-use options are lawful?", "Permits, certificate of occupancy, leases, deposits, rent history and local requirements.", "Action needed"], "status": "Action needed", "sources": ["ca_rent", "hud_fmr", "irs_rental"]},
        {"cells": ["Insurance / property professionals", "Can each intended use be insured, for what replacement cost and exclusions, and what repairs are imminent?", "Separate written owner-occupied and landlord quotes, inspection reports and licensed bids.", "Action needed"], "status": "Action needed", "sources": ["cdi", "cslb"]},
        {"cells": ["Utility / solar provider", "What are the actual water/electric bills, tariff, export credits, true-up and interconnection conditions?", "Bills, account tariff and signed solar/interconnection documents.", "Action needed"], "status": "Action needed", "sources": ["water_board", "cpuc_solar"]},
        {"cells": ["Investment adviser / CPA", "What is net investable cash after costs and taxes; compare immediate, Treasury ladder, phased stock, mixed and reserve paths?", "After-tax proceeds, liquidity plan, current net yields, fees, policy allocation and risk tolerance.", "Action needed"], "status": "Action needed", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
    ]
    body = callout("Meeting objective", f"Leave the meeting with a written conditional recommendation, the assumptions, the deadlines, the tax and insurance reserves, and the facts that would reverse the answer. Working position on file: keep Property B, sell Property A soon after the date of death and stage the proceeds ({money_range(A_VALUE * 0.93, A_VALUE * 0.95)} at a 5%–7% cost assumption) through 24–36 months of Treasuries into equities — unless the household chooses to occupy A and claim the family-home exclusion ({money_range(*A_TAX_EXCL)} versus {money_range(*A_TAX_NO_EXCL)} per year in today's dollars).", "info")
    glance_rows = [
        {"cells": ["Assets", f"Property A (inherited via trust, planned {TRANSFER_WINDOW}): {money(A_VALUE)} owner estimate, 2026 assessment {money(A_ASSESS[2026])}, 2025 tax {money(A_TAX[2025])}. Property B (already owned): {money(B_VALUE)} owner estimate, 2025 assessment {money(B_ASSESS[2025])}, 2025 tax {money(B_TAX[2025])}.", "Confirm title, trust authority and both tax bills."], "status": "Owner-supplied", "sources": ["scc_assessor", "sf_assessor"]},
        {"cells": ["Income and costs", f"B rents {B_RENTED_UNITS} of {B_UNITS} units at {money(B_RENT_MONTH)} per month gross ({money(B_RENT_MONTH * 12)} per year); water {money_range(*B_WATER)} and electricity {money_range(*B_ELEC)} per month on B; A water {money_range(*A_WATER)} per month plus a {money_range(*A_SOLAR)} solar credit; insurance estimates {money(A_INSURANCE_OWNER)} and {money(B_INSURANCE_OWNER)} per year (unverified).", "Replace insurance and maintenance estimates with quotes and bids."], "status": "Owner-supplied", "sources": ["sf_rent", "water_board", "cpuc_solar", "cdi_report"]},
        {"cells": ["Tax thresholds", "Federal exclusion $15,000,000 (2026) / $15,480,000 (2027), 40% above; California imposes no death tax; California taxes capital gains as ordinary income; NIIT 3.8% can apply.", "Produce the estate inventory and a projected filing position."], "status": "Verified", "sources": ["irs_estate", "irs_2027", "irs_706", "ca_rtc13301", "ftb_cg", "irs_niit"]},
        {"cells": ["Deadline set", "Trustee notice 60 days; change-in-ownership statement 150 days; occupancy and homeowners' exemption 1 year; Form 706 9 months (+6); exclusion claim 3 years; installments November 1 / February 1.", "Calendar every date from the actual date of death."], "status": "Verified", "sources": ["ca_prob160617", "ca_rtc480", "ca_rtc63", "irs_estate_faq", "scc_rate_book"]},
    ]
    body += make_table("Case at a glance — figures rounded to $10, not officially verified", ["Topic", "Current figures", "Adviser action"], glance_rows, "Owner-supplied amounts are rounded for privacy; verify each against bills, leases and quotes before relying on it.")
    body += make_table("One-page adviser handoff checklist", ["Adviser", "Question to answer", "Private records to bring", "Status"], rows)
    body += paragraph("Decision boundary", "Property A is the anticipated trust transfer; Property B is already owned. Keep B's rent ledger, leases, assessment, basis and insurance separate from A, and test whether B can serve as a residence without assuming tenant obligations disappear. The ranking on file (sell-and-stage A, or occupy A and claim the exclusion) is conditional on the trust documents, the estate inventory, written quotes and reconciled tax bills — counsel and the CPA confirm those inputs before anything is signed.")
    body += paragraph("Privacy", "This printable brief carries only figures rounded to the nearest $10 and no address, postal code, parcel identifier or document identifier. Print this page or use your browser's Save as PDF. Store completed adviser notes, deeds, bills and quotes outside the public repository.")
    return render_page("pages/attorney-cpa-brief.html", "Attorney & CPA briefing sheet", "One-page, print-ready briefing with the rounded case figures, the deadline set and the open adviser questions. No addresses or identifiers are included.", body, "ADVISER HANDOFF")


def build_flagged() -> str:
    rows = [
        {"cells": ["F-01 — Public Git history exposure", "GitHub reports this repository is public. The active site is generic, but reachable historical commits and PR material may retain earlier case-derived details. This task did not rewrite remote main history or claim a complete purge.", "Treat historic material as exposed. Repository-owner/admin coordination, access review, clean archive and any history rewrite/support request remain required."], "status": "Missing", "sources": ["github_history"]},
        {"cells": ["F-02 — Case figures are owner-supplied, rounded and unverified", "Assessment and tax histories, values, rents and utility ranges are published rounded to $10 but have not been checked against any assessor roll, bill, lease or account statement.", "Verify every row through the county portals linked in the source register; treat all Owner-supplied badges as provisional until then."], "status": "Owner-supplied", "sources": ["scc_assessor", "sf_assessor", "irs_basis"]},
        {"cells": ["F-03 — Premiums and repairs", "No official public page provides an insurance quote or repair estimate for an individual home.", "Request property-specific insurer quotes, coverage forms, inspections and itemized licensed bids."], "status": "Missing", "sources": ["cdi", "cslb"]},
        {"cells": ["F-04 — Water and solar costs", "The state water program is not a household tariff; the CPUC page describes NEM/NBT but not an individual account's net bill.", "Use private bills and signed service/solar documents. No credit or monthly cost is filled in."], "status": "Missing", "sources": ["water_board", "cpuc_solar"]},
        {"cells": ["F-05 — Rental legality and local rules", "No unit permit, local rent-board determination, lease or tenant notice is public here.", "Confirm lawful unit count and all applicable state/local rules with counsel before projecting rent or occupancy."], "status": "Missing", "sources": ["ca_rent", "hud_fmr"]},
        {"cells": ["F-06 — Future law and market path", "The verified CBO forecast runs through 2036. The site discloses only the owner-planned window " + TRANSFER_WINDOW + " (a planning assumption) and scenario bands, never a verified future exclusion, house-price, CPI, rent, insurance or portfolio-return value.", "Re-check enacted law and refresh every dated reading at the actual transfer; treat all bands as scenarios."], "status": "Missing", "sources": ["cbo_rates", "irs_2027", "fhfa_hpi", "fed_pce"]},
        {"cells": ["F-07 — Failed official retrievals", "Direct page fetches returned 404 for the listed FTB inheritance page, BOE county-assessor directory, BOE Publication 801 PDF and CPUC water-utilities URL.", "No claim or property-specific value is based on those failed URLs; working alternative laws and guidance are linked in the source register."], "status": "Not verified", "sources": ["ftb_404", "boe_assessor_404", "boe_pub801_404", "cpuc_water_404"]},
        {"cells": ["F-08 — Stress-tool simplification", "The calculator uses source-reported peak-to-trough endpoints with a synthetic straight-line decline and flat trough.", "It includes only the entered Treasury yields, pre-crash drift and constant inflation lens; it excludes dividends, fees, taxes, post-trough recovery, withdrawals, property costs, correlations and probabilities. It is not a historical backtest."], "status": "Assumption", "sources": ["fed_1929", "fed_2008", "treasury_bills", "bls_cpi"]},
        {"cells": ["F-09 — Property B rate discrepancy", f"Owner-implied 2025 rate {implied_rate(B_TAX[2025], B_ASSESS[2025])} versus the official FY2026-27 composite of 1.18162182% — roughly {money(B_TAX[2025] - r10(B_ASSESS[2025] * RATE_B_OFFICIAL))} per year on 2025 values.", "Reconcile against the actual bill: direct levies, supplemental or escape charges, arrears or a data-source error. Do not budget from either number until reconciled."], "status": "Not verified", "sources": ["sftreasurer_rate", "sf_assessor"]},
        {"cells": ["F-10 — Property A implied rate", f"Owner-implied 2025 rate {implied_rate(A_TAX[2025], A_ASSESS[2025])} sits above the documented countywide component floor of about 1.05% before tax-rate-area debt and flat charges.", "Pull the parcel's tax-rate-area code and full bill lines; confirm whether flat parcel charges or supplemental amounts explain the gap."], "status": "Not verified", "sources": ["scc_rate_book", "scc_assessor"]},
        {"cells": ["F-11 — Insurance estimates", f"Owner estimates of {money(A_INSURANCE_OWNER)} and {money(B_INSURANCE_OWNER)} per year are unverified; CDI statewide averages ({money(1074)} owner-occupied and {money(519)} rental dwelling, 2017) are not Bay Area quotes, and the CDI ZIP-level query for 2018–2023 was not retrieved.", "Obtain two written quotes per property; optionally query the CDI ZIP-level report for context. Until then every insurance cell stays flagged."], "status": "Missing", "sources": ["cdi_report", "cdi_ho_avg", "cdi_rental_avg"]},
        {"cells": ["F-12 — Residual re-identification risk", "Rounding to $10 and withholding addresses reduces casual tracing, but a multi-year assessment series can still resemble a public assessor roll, and county rolls are public records.", "If stronger privacy is required, publish only grouped ranges (for example, values banded to $100,000) instead of the annual series; the owner may request that change at any time."], "status": "Guidance", "sources": ["github_history", "scc_assessor", "sf_assessor"]},
        {"cells": ["F-13 — Transfer-date cap and value unknown", f"The Proposition 19 cap component is {money(CAP_1M_CURRENT)} only for transfers through February 15, 2027; the amount at a transfer around {TRANSFER_WINDOW} is unpublished, and the transfer-date full cash value will differ from today's estimate.", "Re-fetch the BOE adjustment letter and order a date-of-death appraisal when the transfer is near; the transfer-state tax rows are today-dollar illustrations only."], "status": "Missing", "sources": ["boe_lta25009", "irs_estate"]},
        {"cells": ["F-14 — Rent benchmarks not retrieved", "HUD Fair Market Rent values for the relevant areas require an interactive query that was not completed; Property A's rent remains blank.", "Run the HUD documentation system for the property's areas and collect three written rent comps before ranking any rental path."], "status": "Missing", "sources": ["hud_fmr"]},
        {"cells": ["F-15 — Planning assumptions in the numbers", "Growth bands (1–3% / 3–5% / 5–7%), sale costs (5%–7%), management (8%) and maintenance placeholders (0.5%–1.0% of value) are labeled assumptions, not measurements.", "Replace each with an appraisal, a broker net sheet, a management agreement and inspection bids before relying on any total."], "status": "Assumption", "sources": ["fhfa_hpi", "cslb", "irs_rental"]},
    ]
    body = callout("Privacy issue remains urgent", "The current website publishes only $10-rounded case figures and no address, postal code, parcel or identifier. The GitHub repository is still public and history cleanup has not been completed; a noindex tag and a cleaned current tree do not erase old commits, PR diffs, forks, caches or clones. See F-12 for the residual re-identification risk of the rounded annual series itself.", "warning")
    body += make_table("Flagged for review — unresolved items do not imply a verified answer", ["Flag", "What is unresolved", "Required action"], rows)
    body += paragraph("History-remediation limitation", "GitHub's guidance describes history rewriting as a coordinated, disruptive operation and warns that other refs, pull requests, forks, cached views and clones may retain copies. This platform pins the session to one feature branch and prohibits pushing another branch; therefore this work does not force-push or claim to scrub main. The repository owner/admin should review visibility and coordinate a supported, all-ref cleanup if desired.")
    return render_page("pages/flagged-for-review.html", "Flagged for review", "Material uncertainties, rate discrepancies, failed retrievals and the unresolved privacy/history issue — each with the action that would clear it. No unverified value has been presented as verified.", body, "EVIDENCE")


def build_glossary() -> str:
    rows = [
        {"cells": ["Gross estate", "Property and interests included in the federal estate-tax calculation before allowable deductions; includes more than one house.", "Do not compare one inheritor's share alone with the federal filing threshold."], "status": "Verified", "sources": ["irs_estate"]},
        {"cells": ["Basic exclusion amount", "Federal estate/gift tax amount available under current law for a given year, subject to the statute and prior taxable transfers.", "It is not the annual gift exclusion and not a guarantee about a later year."], "status": "Verified", "sources": ["irs_estate", "irs_2027"]},
        {"cells": ["Income-tax basis", "A tax-accounting amount used to compute gain or loss on sale; inherited property basis is generally date-of-death fair market value, subject to exceptions.", "Keep separate from the county's property-tax assessed value."], "status": "Verified", "sources": ["irs_basis"]},
        {"cells": ["Assessed value", "Value used in the property-tax system; California rules can constrain growth and change the base on a change in ownership, with specified exclusions.", "Not the same as current market value, sale price or income-tax basis."], "status": "Verified", "sources": ["boe_pub29", "boe_prop19"]},
        {"cells": ["Proposition 19 family-home exclusion", "A conditional intergenerational property-tax rule with relationship, residence, occupancy and claim requirements.", "Trust title alone does not prove qualification."], "status": "Verified", "sources": ["ca_rtc63", "boe_prop19"]},
        {"cells": ["Mixed path", "A combination such as occupying one lawful unit, renting another, retaining an already-owned property, or selling one asset and staging the proceeds.", "Model each asset, unit and tax position separately."], "status": "Guidance", "sources": ["irs_rental", "ca_rent"]},
        {"cells": ["Sequence risk", "The effect of when returns occur; an early decline can matter more than the same decline later when funds are being invested or withdrawn.", "Stress both crash-during-staging and crash-after-staging cases; neither is a probability forecast."], "status": "Guidance", "sources": ["fed_1929", "fed_2008", "sec_stocks"]},
        {"cells": ["Reinvestment risk", "The possibility that proceeds from a maturing investment must be reinvested at a lower yield.", "A short Treasury ladder can defer equity exposure but does not lock a future renewal yield."], "status": "Verified", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Fair Market Rent (FMR)", "HUD's annual 40th-percentile gross-rent benchmark used for specified housing programs.", "It is not a property appraisal, a lease amount or a determination of legal rent."], "status": "Verified", "sources": ["hud_fmr"]},
        {"cells": ["Value cap (Proposition 19)", "The intergenerational exclusion's ceiling: the factored base year value plus a $1,000,000 amount that the BOE adjusts every other February 16 by the FHFA California House Price Index ($1,044,586 for transfers through February 15, 2027).", "Above the cap the excess is added to the taxable value — the exclusion never freezes a low assessment on a much more valuable home."], "status": "Verified", "sources": ["boe_lta25009", "boe_lta26026"]},
        {"cells": ["New base year value", "The transfer-date full cash value that is enrolled if a family-home exclusion is never claimed or is later lost when the transferee stops qualifying.", "This is why renting the inherited house without occupying it — or moving out later — resets the tax base to the value at death, not the old low assessment."], "status": "Verified", "sources": ["boe_lta26026"]},
        {"cells": ["Step-up in basis", "The income-tax basis of inherited property is generally its fair market value on the date of death (or the alternate valuation date if elected).", "Selling soon after death keeps taxable gain small; selling before death does not get the step-up."], "status": "Verified", "sources": ["irs_basis", "irs_706"]},
        {"cells": ["Implied effective rate", "Owner-supplied annual tax divided by the owner-supplied assessment — the rate the history implies rather than a published rate.", "A mismatch against the official composite rate (as on Property B) is a bill-verification flag, not a tax rule."], "status": "Owner-supplied", "sources": ["sftreasurer_rate", "scc_rate_book"]},
        {"cells": ["Net investment income tax (NIIT)", "A 3.8% federal tax on the lesser of net investment income or modified adjusted gross income above $200,000 (single) or $250,000 (joint); applies to estates and trusts as well.", "Rent, interest, dividends and property gains can all be swept into it; model it alongside ordinary rates."], "status": "Verified", "sources": ["irs_niit"]},
    ]
    body = make_table("Terms used in this workspace", ["Term", "Plain-language meaning", "Practical distinction"], rows)
    return render_page("pages/glossary.html", "Glossary", "Short definitions for the legal, tax, property and investment terms used in the decision process.", body, "EVIDENCE")


# Sources re-fetched during the 2026-11-15 session; every other verified
# source was last fetched on 2026-11-14 by the prior session and is carried
# forward with its earlier date.
REFETCHED = {
    "irs_estate", "irs_2027", "irs_estate_faq", "irs_basis", "irs_rental",
    "ca_death_tax", "ca_rtc13301", "boe_prop19", "ca_rtc63", "ca_rtc480",
    "ca_prob160617", "boe_pub29", "ca_rent", "cdi", "treasury_bills",
    "treasury_notes", "fed_1929", "fed_2008", "cbo_rates", "hud_fmr",
    "sftreasurer_rate", "scc_rate_book", "boe_lta26026", "boe_lta25009",
    "irs_cg", "irs_niit", "irs_706", "ftb_cg", "rtc17041", "rtc17043",
    "bls_hist", "bls_mlr100", "fed_pce", "treasury_curve", "cdi_report",
    "cdi_ho_avg", "cdi_rental_avg", "sf_rent", "scc_assessor", "sf_assessor",
}


def build_sources() -> str:
    rows = []
    for key, item in SOURCES.items():
        checked = item.get("checked") or ("2026-11-15" if key in REFETCHED else "2026-11-14")
        rows.append({
            "cells": [item["label"], item["scope"], f"Direct page fetch: {checked}"],
            "status": "Verified" if item["verified"] else "Not verified",
            "sources": [key],
        })
    body = callout("Source scope matters", "Every source is an official government, regulator, or platform documentation page. A link verifies only the scope shown in its description; it never verifies a private property fact. Failed fetches are included and visibly marked.", "info")
    body += make_table("Official source register", ["Source", "What it supports / does not support", "Checked"], rows)
    body += paragraph("Verification method", "Each row shows the date its page was last fetched directly and read for the narrow statement shown:2026-11-15 for this session's verification pass,2026-11-14 for sources carried forward from the prior session. Failed retrievals remain flagged rather than silently replaced with secondary material. Re-check legal text, rates and agency guidance at the actual transfer date.")
    return render_page("pages/sources.html", "Official source register", "A direct-source ledger with retrieval date, verification status and a clear statement of each source's limits.", body, "EVIDENCE")


def build_privacy() -> str:
    rows = [
        {"cells": ["Public page content", "The site uses Property A / Property B roles with city-level context only. Case figures — values, assessment and tax histories, rents, utilities, insurance estimates — appear ONLY rounded to the nearest $10 and badged Owner-supplied, Projection or Assumption. No home address, postal code, parcel identifier, account number, document identifier, name or lease term is published.", "Do not add identifying documents or unrounded amounts. If the owner wants stronger privacy, the annual series can be banded further (see F-12) on request."], "status": "Guidance", "sources": ["github_history", "scc_assessor", "sf_assessor"]},
        {"cells": ["Public hosting", "GitHub Pages is a public static website. Noindex discourages search indexing but does not restrict access or make a page private.", "Never put deeds, trust papers, tax bills, leases, statements or identifiable values here."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Current branch tree", "Identified case-input, projection, and audit files have been removed from this branch's current tree. This does not erase earlier public commits or PR references.", "Do not use this public repository as a secure vault; keep private records outside GitHub."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Git history / copies", "Earlier commits and PR diffs may remain accessible; forks, cached views and clones cannot be erased by a normal cleanup commit.", "Treat historical material as exposed until an owner/admin-coordinated history-removal process and GitHub support review are complete."], "status": "Missing", "sources": ["github_history"]},
        {"cells": ["Browser controls", "The phased-investing calculator uses transient browser memory only; review choices are stored locally in this browser and are not transmitted by this static site.", "Clear browser site data to remove saved review choices; do not enter confidential values into a public computer."], "status": "Guidance", "sources": ["github_history"]},
    ]
    body = callout("Privacy warning — history is not fully scrubbed", "The repository is public. The current branch tree publishes only $10-rounded case figures with no identifiers, but historical Git objects, earlier public PRs, forks, caches and clones may retain unrounded or more detailed case-derived material. This branch cannot rewrite public main history; repository-owner/admin coordination is required. Treat prior values as exposed.", "warning")
    body += make_table("Privacy boundary and remaining exposure", ["Area", "Current state", "Safeguard / limitation"], rows)
    body += paragraph("No third-party tracking", "The generated pages use local HTML, CSS and JavaScript only. They contain no analytics, remote fonts, remote scripts, API calls or form submissions. External official sources open only when a reader follows a link.")
    return render_page("pages/privacy.html", "Privacy and limitations", "Privacy is the first release gate: case figures appear only rounded to $10 with no addresses or identifiers, and public Git history still needs owner/admin review.", body, "EVIDENCE")


def suggestion_table() -> str:
    suggestions = [
        ("S01", "Privacy", "Keep private records in an access-controlled vault", "Store executed trust/deed, tax returns, leases, bills, quotes and inspections outside the public repository; publish only generic conclusions.", "History removal and access control must be coordinated with the repository owner/admin.", ["github_history"]),
        ("S02", "Decision", "Require a written trust and title summary before modeling", "Ask counsel to identify transfer authority, distribution conditions, occupancy rights, debts, title and the dates that start legal clocks.", "Prevents analyzing a path the trustee or title does not permit.", ["ca_prob160617", "ca_rtc480"]),
        ("S03", "Tax", "Separate estate tax, income-tax basis and property-tax assessment", "Have the CPA prepare one schedule for the gross estate and adjusted gifts, one for inherited basis, and one for county assessment/Prop 19.", "These are distinct legal calculations, not interchangeable values.", ["irs_estate", "irs_basis", "boe_pub29", "boe_prop19"]),
        ("S04", "Property", "Verify legal unit count and local rental rules", "Reconcile permits, leases, rent registration, tenant deposits, occupancy, and statewide/local rent limits before estimating net rent.", "Gross rent from an unverified unit is not a lawful or reliable return.", ["ca_rent", "hud_fmr", "irs_rental"]),
        ("S05", "Operations", "Get separate current insurance and repair evidence", "Request written owner-occupied and landlord/mixed-use quotes, replacement-cost estimates, exclusions, inspections and itemized bids.", "Insurance availability and deferred repairs can reverse an apparent cash-flow winner.", ["cdi", "cslb"]),
        ("S06", "Utilities", "Reconcile bills and solar tariff before assuming a credit", "Collect actual water/electric bills and the signed solar interconnection and tariff documents; note NEM/NBT and true-up dates.", "Equipment alone does not establish future net export compensation.", ["water_board", "cpuc_solar"]),
        ("S07", "Model", "Compare mixed paths alongside pure choices", "Include occupancy of lawful units, existing-property retention, rent on other lawful units, short hold-then-sale, sale of one asset, and staged reinvestment.", "Avoids forcing a false live-versus-rent-versus-sell choice.", ["irs_rental", "ca_rent", "boe_prop19"]),
        ("S08", "Markets", "Put reinvestment risk next to any staging headline", "Compare 24–36 months of Treasury staging under crash-during and crash-after entry, lower renewal yields, inflation and a rising market before the decline.", "Staging changes risk timing; it does not make equities safe or guarantee a better ending value.", ["treasury_bills", "treasury_notes", "fed_1929", "fed_2008", "bls_cpi"]),
        ("S09", "Governance", "Put reversal conditions on the first screen", "Track the facts that change the path: trust restrictions, estate threshold, Prop 19 eligibility, unit legality, net rent, insurance, repair reserve and liquidity.", "A recommendation should name evidence that would reverse it.", ["irs_estate", "boe_prop19", "cdi", "sec_stocks"]),
        ("S10", "Refresh", "Set annual legal and assumption review reminders", "Recheck enacted laws, assessor records, insurance availability, utilities, leases, market inputs and investment policy when the decision approaches.", "Today’s current rules do not determine a decision decades in the future.", ["irs_2027", "boe_prop19", "cbo_rates"]),
        ("S11", "Privacy", "Keep the $10 rounding rule as a release gate", "Every published case figure must be a multiple of $10 (the build now enforces this), and no address, postal code or identifier may appear. Consider banding the annual series to $100,000 if the owner wants more distance from the public assessor rolls.", "Rounding plus identifier withholding is what makes a public decision site possible at all (see F-12 for the residual risk).", ["github_history", "scc_assessor"]),
        ("S12", "Data", "Reconcile both property-tax rate discrepancies against the actual bills", f"Property B's implied {implied_rate(B_TAX[2025], B_ASSESS[2025])} versus the official 1.18162182% and Property A's implied {implied_rate(A_TAX[2025], A_ASSESS[2025])} versus the documented component floor both need bill-level answers.", "Every tax projection on the site inherits this gap until it is closed.", ["sftreasurer_rate", "scc_rate_book", "sf_assessor", "scc_assessor"]),
        ("S13", "Decision", "Adopt the conditional recommendation with written reversal gates", "Keep B; sell A soon after the date of death and stage the proceeds — or occupy A and claim the exclusion — and write down the four gates (trust documents, estate inventory, quotes, reconciled bills) that would reverse it.", "A recommendation without reversal conditions drifts into anchoring; the gates keep it honest.", ["irs_basis", "boe_lta26026", "irs_706"]),
        ("S14", "Numbers", "Replace every placeholder with a quote or bid", "Insurance estimates, the 5%–7% sale cost, the 8% management figure and the 0.5%–1.0% maintenance bands are labeled assumptions; swap them for written evidence at the next review.", "The recommendation's margins are wider than some of these placeholders — quotes decide whether rent-A ever competes.", ["cdi_report", "cslb", "irs_rental"]),
        ("S15", "Tax", "Calendar the Proposition 19 claim sequence before the transfer", "Occupancy and homeowners' exemption within one year, exclusion claim within three years, and a dated pull of the BOE value-cap letter for the transfer window.", "Missing either filing forfeits roughly the annual gap between the exclusion and full reassessment.", ["ca_rtc63", "boe_lta26026", "boe_lta25009"]),
        ("S16", "Markets", "Re-price the Treasury ladder at every auction", "Use the dated reference yields as starting inputs, then replace them with actual net yields at each auction; keep the crash-during and crash-after cases side by side.", "The worked example shows phasing helps only when the decline arrives during the wait — and renewals are unknown.", ["treasury_curve", "treasury_notes", "fed_2008"]),
        ("S17", "Rent", "Complete the HUD FMR lookups and three rent comps for Property A", "Run the HUD documentation system for the relevant areas and collect written comps before any rental path is ranked.", "A rent-versus-sell comparison is arithmetic only after the rent number exists (see F-14).", ["hud_fmr", "irs_rental"]),
    ]
    rows = []
    for ident, group, title, action, why, sources in suggestions:
        select = SafeHTML(
            f'<select class="review-choice" data-id="{esc(ident)}" aria-label="Review decision for {esc(ident)}">'
            '<option value="Not reviewed">Not reviewed</option>'
            '<option value="Investigate">Investigate</option>'
            '<option value="Selected">Selected for testing</option>'
            '<option value="Defer">Defer</option></select>'
        )
        rows.append({
            "cells": [ident, group, title, action, why, select],
            "status": "Guidance",
            "sources": sources,
        })
    return make_table("Reviewable suggestions — no change is applied automatically", ["ID", "Category", "Suggestion", "What to do", "Why it may improve the decision", "Review choice"], rows)


def build_suggestions() -> str:
    body = callout("Choose what to review before implementing anything", "Each choice is saved only in this browser's local storage. Nothing is sent to a server and no change to the site or decision is made by selecting an option. Use Reset to clear the local review queue.", "info")
    body += '<p class="review-summary" id="review-summary" role="status" aria-live="polite">Loading review queue…</p><p class="no-print"><button id="reset-reviews" type="button">Reset review choices</button></p>'
    body += suggestion_table()
    body += paragraph("Suggested approval gates", "Do not implement a financial or site change until the relevant owner has reviewed it, the necessary private records exist, a professional confirms applicable law, and the model's result is reproducible under stated assumptions.")
    return render_page("pages/suggestions.html", "Suggestions for review", "A selectable review queue for improving decision quality. Suggestions are proposals, not automatic changes or personalized advice.", body, "DECISION")


def build_page(path: str) -> str:
    builders = {
        "index.html": build_index,
        "pages/executive-summary.html": build_executive_summary,
        "pages/decision-analysis.html": build_decisions,
        "pages/questions.html": build_questions,
        "pages/projections.html": build_projections,
        "pages/property-tax.html": build_property_tax,
        "pages/operating-costs.html": build_costs,
        "pages/black-swan.html": build_black_swan,
        "pages/phased-investing.html": build_phased_investing,
        "pages/estate-thresholds.html": build_estate_thresholds,
        "pages/inheritance-process.html": build_process,
        "pages/law-watchlist.html": build_law_watchlist,
        "pages/attorney-cpa-brief.html": build_brief,
        "pages/flagged-for-review.html": build_flagged,
        "pages/glossary.html": build_glossary,
        "pages/sources.html": build_sources,
        "pages/privacy.html": build_privacy,
        "pages/suggestions.html": build_suggestions,
    }
    return builders[path]()


def build() -> None:
    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "pages").mkdir(exist_ok=True)
    expected = {Path(name).name for name in EXPECTED_PAGES if name.startswith("pages/")}
    for path in (ROOT / "pages").glob("*.html"):
        if path.name not in expected:
            path.unlink()
    for path in EXPECTED_PAGES:
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(build_page(path), encoding="utf-8")
    manifest = ROOT / "tools" / "site-manifest.json"
    manifest.write_text(json.dumps(EXPECTED_PAGES, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(EXPECTED_PAGES)} privacy-safe pages with source-linked tables; no household inputs were read.")


if __name__ == "__main__":
    build()
