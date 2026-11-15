#!/usr/bin/env python3
"""Build a privacy-safe, source-linked inheritance decision workspace.

The public build is deliberately static and never imports household inputs.
Every substantive table row has an evidence status and at least one official
source link. Property-specific values are intentionally left blank.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKED = "2026-11-15"
SITE_TITLE = "Private inheritance decision workspace"

# Sources are fetched directly on the date shown in their register row. Older
# entries without an individual date use CHECKED. The scope is intentionally
# narrow: a source may establish a rule or public observation, never a private
# property's value, bill, lease, premium, title, or tax position.
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
        "scope": "Explains the filing test using gross estate plus adjusted taxable gifts and the specific gift-tax exemption, the 9-month Form 706 due date and the up-to-6-month filing extension request. It also describes filing for portability below the threshold; individual filing status still requires estate facts.",
        "verified": True,
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
        "scope": "Statutory family-home/family-farm exclusion conditions, including parent-child or qualifying grandparent-grandchild relationship (with the statutory deceased-parent condition for grandchild transfers), transferor and transferee residence requirements, the one-year homeowners' exemption filing and the value-limit formula.",
        "verified": True,
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
        "scope": "Describes annual FMR estimates used for specified housing programs. FMR is a benchmark, not a property appraisal, lawful rent determination or current lease amount.",
        "verified": True,
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
        "scope": "Notes include a 2-year maturity, pay a fixed auction rate, may be held to maturity or sold earlier, and interest is federally taxable but exempt from state and local taxes.",
        "verified": True,
    },
    "fed_1929": {
        "label": "Federal Reserve History — Stock Market Crash of 1929",
        "url": "https://www.federalreservehistory.org/essays/stock-market-crash-of-1929",
        "scope": "Reports the Dow's 89% peak-to-trough decline and that its pre-crash high was not regained until November 1954. This is a price-index history, not a diversified portfolio total return.",
        "verified": True,
    },
    "cbo_ltbo": {
        "label": "Congressional Budget Office — The Long-Term Budget Outlook: 2025 to 2055",
        "url": "https://www.cbo.gov/publication/61270",
        "scope": "Thirty-year extended baseline: inflation slows through 2027 to about the Federal Reserve's 2% long-term goal and stays near it to 2055; the 10-year Treasury rate stays close to its 30-year average; debt held by the public reaches 156% of GDP in 2055. It is a law-unchanged baseline, not a guarantee and not a house-price or equity-return forecast.",
        "verified": True,
    },
    "fed_great_inflation": {
        "label": "Federal Reserve History — The Great Inflation (1965–1982)",
        "url": "https://www.federalreservehistory.org/essays/great-inflation",
        "scope": "Reports inflation of a little more than 1% in 1964, more than 14% in 1980, and about 3.5% average in the latter half of the 1980s. It documents a long regime of high and volatile inflation rather than a single-year shock.",
        "verified": True,
    },
    "fed_great_depression": {
        "label": "Federal Reserve History — The Great Depression (1929–1941)",
        "url": "https://www.federalreservehistory.org/essays/great-depression",
        "scope": "Describes a decade-long contraction beginning in August 1929, banking panics, and recovery interrupted by the 1937–38 recession. It is an episode description, not a probability for a future period.",
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
        "scope": "Official search interface for federal bills and resolutions and their status. The bill-specific examples in this register are introduced proposals, not current law unless enacted.",
        "verified": True,
    },
    "ca_legislation": {
        "label": "California Legislative Information — Bill Search",
        "url": "https://leginfo.legislature.ca.gov/faces/billSearchClient.xhtml",
        "scope": "Official search interface for California bills and chaptered laws. Verify status, operative date, enacted code and agency guidance before applying a change.",
        "verified": True,
    },
    "ca_sb974_status": {
        "label": "California Legislature — SB 974 status, Chapter 665 (2026)",
        "url": "https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202520260SB974",
        "scope": "Status page records SB 974 as chaptered September 27, 2026, Chapter 665, Statutes of 2026, and marks it non-urgency. Verify its operative date and the assessor's implementation before applying it to a transfer.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "ca_sb974_text": {
        "label": "California SB 974 — chaptered text",
        "url": "https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202520260SB974",
        "scope": "Chaptered amendment to RTC §63.2 expressly treats a special-needs trust established under Probate Code §3604 as an eligible medium for the stated intergenerational property-tax exclusion; eligibility and claim requirements remain. Separate claim-timing relief is limited to qualifying property connected with specified 2025 wildfires.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "congress_s4196_status": {
        "label": "Congress.gov — S. 4196 status",
        "url": "https://www.congress.gov/bill/119th-congress/senate-bill/4196",
        "scope": "Congress.gov lists S. 4196 as introduced March 25, 2026 and referred to Senate Finance; no enactment is shown as of the check date. Status can change.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "congress_s4196_text": {
        "label": "Congress.gov — S. 4196 introduced text",
        "url": "https://www.congress.gov/bill/119th-congress/senate-bill/4196/text",
        "scope": "Introduced text proposes a $3,500,000 basic exclusion amount and changes to federal estate, gift and generation-skipping transfer tax rules, with a proposed effective date for deaths and gifts after December 31, 2026. This is not enacted law.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "congress_hr601_status": {
        "label": "Congress.gov — H.R. 601 status",
        "url": "https://www.congress.gov/bill/119th-congress/house-bill/601",
        "scope": "As checked 2026-11-15, Congress.gov lists H.R. 601 as introduced January 22, 2025 and referred to House Ways and Means and Budget; no enactment is shown. Status can change.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "congress_hr601_text": {
        "label": "Congress.gov — H.R. 601 introduced text",
        "url": "https://www.congress.gov/bill/119th-congress/house-bill/601/text/ih",
        "scope": "Introduced text proposes a 20% rate for estate, gift and generation-skipping transfer taxes and states a proposed effective date for transfers after December 31, 2024. This is not enacted law.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "congress_s587_status": {
        "label": "Congress.gov — S. 587 status",
        "url": "https://www.congress.gov/bill/119th-congress/senate-bill/587",
        "scope": "As checked 2026-11-15, Congress.gov lists S. 587 as introduced February 13, 2025 and referred to Senate Finance; no enactment is shown. Status can change.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "congress_s587_text": {
        "label": "Congress.gov — S. 587 introduced text",
        "url": "https://www.congress.gov/bill/119th-congress/senate-bill/587/text/is",
        "scope": "Introduced text proposes to repeal federal estate and generation-skipping transfer taxes and separately changes gift-tax rules. The proposal is not enacted law.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "cbo_outlook": {
        "label": "Congressional Budget Office — The Budget and Economic Outlook: 2026 to 2036",
        "url": "https://www.cbo.gov/publication/61882",
        "scope": "Baseline projection to 2036: deficits, debt, real GDP growth, unemployment, PCE inflation returning to roughly 2% in 2030, and 10-year Treasury rates rising gradually in 2027 then staying relatively stable. It is a ten-year baseline, not a 50-year forecast of housing, insurance, rent or equity returns.",
        "verified": True,
    },
    "irs_basis_pub": {
        "label": "IRS Publication 551 — Basis of Assets",
        "url": "https://www.irs.gov/publications/p551",
        "scope": "Explains cost basis, adjusted basis, and increases/decreases to basis (including depreciation and improvements). It does not value a specific property or set a date-of-death appraisal.",
        "verified": True,
    },
    "irs_121": {
        "label": "IRS Topic no. 701 — Sale of your home",
        "url": "https://www.irs.gov/taxtopics/tc701",
        "scope": "States the $250,000/$500,000 main-home gain exclusion, the two-out-of-five-year ownership and use tests, and reporting duties. Eligibility for a specific owner is not determined here.",
        "verified": True,
    },
    "ca_rtc218": {
        "label": "California Revenue and Taxation Code §218 — Homeowners' property tax exemption",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=218.&lawCode=RTC",
        "scope": "Sets the homeowners' property tax exemption at $7,000 of the dwelling's full value and excludes property that is rented, vacant, under construction on the lien date, or a vacation/secondary home. It does not establish an owner's eligibility.",
        "verified": True,
    },
    "ca_rtc51": {
        "label": "California Revenue and Taxation Code §51 — Taxable value of real property",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=51.&lawCode=RTC",
        "scope": "Defines taxable value as the lesser of the inflation-adjusted base year value (increase capped at 2%) or full cash value, and applies the October-to-October California CPI factor. It does not state a parcel's assessed value.",
        "verified": True,
    },
    "obbba_law": {
        "label": "Congress.gov — H.R. 1, Public Law 119-21 (One Big Beautiful Bill Act)",
        "url": "https://www.congress.gov/bill/119th-congress/house-bill/1",
        "scope": "Enacted July 4, 2025 as Public Law 119-21. Under this law the federal basic estate/gift exclusion is $15,000,000 for 2026 and is adjusted for inflation in later years; this session read the bill page for the public-law number and date. The exclusion is not per beneficiary and future Congresses can amend it.",
        "verified": True,
    },
    "irc_2010c": {
        "label": "U.S. Code — 26 U.S.C. §2010(c) (basic exclusion amount)",
        "url": "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section2010&num=0&edition=prelim",
        "scope": "Statute governing the basic exclusion amount and its inflation adjustment (chained CPI). The projection rows on this site compound the official 2027 amount at an assumed 2% per year to mirror CBO's long-run inflation path; the statute and future law control the real amounts.",
        "verified": True,
    },
    "irs_rp_2025_32": {
        "label": "IRS — Rev. Proc. 2025-32 (2026 annual inflation adjustments)",
        "url": "https://www.irs.gov/pub/irs-drop/rp-25-32.pdf",
        "scope": "Source of the 2026 long-term capital-gains breakpoints (0% up to $49,450 single / $98,900 joint; 15% up to $545,500 / $613,700) and 2026 gift and estate amounts. Cross-checked against independent compilations on 2026-11-15; the PDF was not retrieved directly in this session.",
        "verified": False,
    },
    "irs_niit": {
        "label": "IRS — Net Investment Income Tax",
        "url": "https://www.irs.gov/individuals/net-investment-income-tax",
        "scope": "States the 3.8% net investment income tax for taxpayers above the $200,000/$250,000 modified-adjusted-gross-income thresholds. Whether it applies to a household is a CPA determination.",
        "verified": False,
    },
    "boe_lta_2025_009": {
        "label": "California BOE — News release: Prop 19 $1,000,000 exclusion adjusted (LTA 2025/009)",
        "url": "https://www.boe.ca.gov/news/2025/nr-25-02.htm",
        "scope": "Sets the Proposition 19 intergenerational exclusion amount at $1,044,586 for transfers from February 16, 2025 through February 15, 2027, adjusted every two years using the FHFA California House Price Index; the transferee must file the homeowners' or disabled veterans' exemption within one year.",
        "verified": True,
    },
    "treasury_curve": {
        "label": "U.S. Department of the Treasury — Daily Treasury Par Yield Curve Rates",
        "url": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202611",
        "scope": "Official daily par yield curve used for the November 2026 staging-band context (3-month ≈ 4.3%, 2-year ≈ 4.9%). Values were cross-checked against market aggregations quoting this series; retrieve the current curve directly before any real decision.",
        "verified": False,
    },
    "sjw_rates": {
        "label": "San Jose Water — utility serving the Cupertino area",
        "url": "https://www.sjwater.com/",
        "scope": "Investor-owned water utility serving Cupertino and nearby communities; publishes tariffs and rate schedules. Provider context only — the household bill depends on metered usage and current approved rates.",
        "verified": False,
    },
    "pge_tariffs": {
        "label": "Pacific Gas and Electric Company — tariffs",
        "url": "https://www.pge.com/",
        "scope": "Electric/gas provider for the regions discussed; publishes residential tariffs. Third-party compilations of CPUC Public Advocates Office data put the mid-2026 residential average near 33.7 cents per kWh; confirm against the tariff and the actual account.",
        "verified": False,
    },
    "sfpuc_water": {
        "label": "San Francisco Public Utilities Commission — water service",
        "url": "https://www.sfpuc.org/",
        "scope": "Municipal water/wastewater provider context for San Francisco properties. Provider context only; a multi-unit building's combined bill depends on metering configuration and usage.",
        "verified": False,
    },
    "cdi_news": {
        "label": "California Department of Insurance — Newsroom",
        "url": "https://www.insurance.ca.gov/0400-news/",
        "scope": "Official channel for rate-approval announcements. Third-party reporting of a roughly 29% average FAIR Plan dwelling rate increase effective October 2026 is noted as market-stress context pending direct retrieval here; premium amounts still require written quotes.",
        "verified": False,
    },
    "owner_a": {
        "label": "Owner-supplied records — Property A (privacy-rounded to nearest $10)",
        "url": "https://assessor.santaclaracounty.gov/",
        "scope": "Owner-provided valuation, assessment and tax history for Property A, rounded to the nearest ten dollars per the owner's written privacy instruction. Not independently verifiable here; confirm against the county assessor's public records for the parcel before relying on any figure.",
        "verified": False,
    },
    "owner_b": {
        "label": "Owner-supplied records — Property B (privacy-rounded to nearest $10)",
        "url": "https://www.sf.gov/departments--assessor-recorder",
        "scope": "Owner-provided valuation, assessment, tax and rent figures for Property B, rounded to the nearest ten dollars per the owner's written privacy instruction. Not independently verifiable here; confirm against the Assessor-Recorder's records, the tax bill and the leases.",
        "verified": False,
    },
    # --- Ported from session 377ea96a / PR #88 (fetched and verified there on 2026-11-15) ---
    "sfpuc_rates": {
        "label": "SFPUC — Proposition 218 water and sewer rate notice (2026)",
        "url": "https://www.sfpuc.gov/accounts-services/water-power-sewer-rates/proposed-water-sewer-rates-2026/proposition-218-notice",
        "scope": "Published rate schedule effective July 1, 2026: average San Francisco single-family combined water/sewer bill about $171 per month (FYE 2026) rising to about $189 (FYE 2027) and $212 (FYE 2028); two-tier volumetric water rates; multi-family tier 1 covers the first 3 units per dwelling per month. A utility's own rate notice, not a specific account's bill.",
        "verified": True,
    },
    "cdi_sis": {
        "label": "California Department of Insurance — Sustainable Insurance Strategy",
        "url": "https://www.insurance.ca.gov/01-consumers/180-climate-change/upload/Sustainable-Insurance-Strategy-CDI-Summary-10-14-25.pdf",
        "scope": "CDI's summary of the market-rebuild program: approved wildfire catastrophe models, insurer commitments to write a minimum share of business in distressed areas, FAIR Plan modernization and depopulation goals, rate-review streamlining. Confirms the market is under active regulatory change; states no household premium.",
        "verified": True,
    },
    "fred_cpi": {
        "label": "FRED (Federal Reserve Bank of St. Louis) — CPI-U, annual averages 1929–2025",
        "url": "https://fred.stlouisfed.org/series/CPIAUCNS",
        "scope": "Official BLS CPI-U (NSA) series. Decade inflation rates and cumulative changes shown on this site are computed from the published annual averages, not estimated.",
        "verified": True,
    },
    "irs_rp2532": {
        "label": "IRS — Rev. Proc. 2025-32 (2026 inflation adjustments)",
        "url": "https://www.irs.gov/pub/irs-drop/rp-25-32.pdf",
        "scope": "Official 2026 amounts: OBBBA §70106 sets the basic exclusion at $15,000,000 for 2026 with inflation adjustment for 2027 and later; estates and trusts keep four rates (10/24/35/37%) with the top bracket beginning over $16,000; 20% capital-gains rate for trusts begins over $16,250. Does not forecast later-year law.",
        "verified": True,
    },
    "irs_topic701": {
        "label": "IRS Topic no. 701 — Sale of your home",
        "url": "https://www.irs.gov/taxtopics/tc701",
        "scope": "Section 121 exclusion of up to $250,000 ($500,000 on a joint return) of gain on a principal residence, with 2-of-5-year ownership and use tests and a once-per-2-years limit. Publication 523 has the full rules.",
        "verified": True,
    },
    "sos_initiatives": {
        "label": "California Secretary of State — Initiative status (failure memo, May 2026)",
        "url": "https://elections.cdn.sos.ca.gov/ccrov/2026/may/26138jh.pdf",
        "scope": "Official CC/ROV Memorandum #26138 (May 18, 2026): the initiative titled 'Repeals voter-enacted changes to property tax rules for transfers between family members' (Prop 19 repeal) failed — signatures filed were below the number required. Current Proposition 19 rules were not changed by this attempt.",
        "verified": True,
    },
    "sos_qualified": {
        "label": "California Secretary of State — Qualified statewide ballot measures",
        "url": "https://www.sos.ca.gov/elections/ballot-measures/qualified-ballot-measures",
        "scope": "Read 2026-11-15. Lists the November 3, 2026 statewide measures by number and official ballot title, and notes ACA 13 was removed. The page is a list only: it does not state full measure text, fiscal effects or certified results. Those require the linked voter guide or certified results.",
        "verified": True,
    },
    "boe_lta25009": {
        "label": "California BOE Letter to Assessors 2025/009",
        "url": "https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf",
        "scope": "Official adjustments of the Proposition 19 $1,000,000 amount: $1,000,000 (transfers 2/16/2021–2/15/2023), $1,022,600 (2/16/2023–2/15/2025), $1,044,586 (2/16/2025–2/15/2027), adjusted every other February by the FHFA House Price Index for California (2024 change: 2.15%). Next adjustment February 2027. Application detail: Property Tax Rule 462.520 and LTA 2022/012.",
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
    "sos_ballot": {
        "label": "California Secretary of State — Qualified statewide ballot measures",
        "url": "https://www.sos.ca.gov/elections/ballot-measures/qualified-ballot-measures",
        "scope": "Read 2026-11-15. Lists the November 3, 2026 statewide measures by number and official ballot title, and notes ACA 13 was removed. The page is a list only: it does not state full measure text, fiscal effects or certified results. Those require the linked voter guide or certified results.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "sf_rent_board": {
        "label": "San Francisco Rent Board — Department page",
        "url": "https://sf.gov/departments--rent-board",
        "scope": "Read 2026-11-15. States the 1.6% allowable annual increase for covered units from March 1, 2026 through February 28, 2027, and lists 2026 Rent Board news items. Item text and ordinance coverage must be read in the linked notice.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "sf_treasurer_vacancy_404": {
        "label": "SF Treasurer — vacancy-tax URL retrieval failed",
        "url": "https://sftreasurer.org/empty-homes-tax",
        "scope": "Returned 'Page Not Found' on 2026-11-15. No SF vacancy-tax rule, rate or filing duty is based on this URL; the current official path is unconfirmed.",
        "verified": False,
        "checked": "2026-11-15",
    },
    "scc_assessor_fetch": {
        "label": "Santa Clara County Assessor homepage — fetch failed",
        "url": "https://assessor.santaclaracounty.gov/",
        "scope": "Fetch failed on 2026-11-15. The reachable Assessor page (asr.santaclaracounty.gov) lists contacts and online services only and has no tax-rate table. No Santa Clara property-tax rate is based on these pages.",
        "verified": False,
        "checked": "2026-11-15",
    },
    "boj_unverified": {
        "label": "Bank of Japan — official source not confirmed for bubble figures",
        "url": "https://www.boj.or.jp/en/",
        "scope": "The official Bank of Japan source for the historical discount-rate and asset-price figures was not retrieved. Secondary sources conflict, so no Japan bubble figure is published here.",
        "verified": False,
    },
    # --- T9806-2/3/4 additions: all fetched directly on 2026-11-15 ---------
    "ftb_capgain": {
        "label": "FTB — Capital gains and losses",
        "url": "https://www.ftb.ca.gov/file/personal/income-types/capital-gains-and-losses.html",
        "scope": "States that California has no lower rate for capital gains and that all capital gains are taxed as ordinary income, reported on federal Schedule D with California Schedule D (540) where federal and state treatment differ. Last updated 01/28/2026. It does not compute a household's gain.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "ftb_540_line62": {
        "label": "FTB — 2025 Instructions for Form 540, line 62",
        "url": "https://www.ftb.ca.gov/forms/2025/2025-540-instructions.html",
        "scope": "Line 62, Behavioral Health Services Tax: if taxable income (Form 540, line 19) is more than 1,000,000 dollars, the tax is one percent of the amount above that figure. Also states the line 61 alternative minimum tax thresholds. It does not set a future-year rate or a household's taxable income.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_topic701": {
        "label": "IRS Topic no. 701 — Sale of your home",
        "url": "https://www.irs.gov/taxtopics/tc701.html",
        "scope": "States the 250,000 dollar (500,000 joint) main-home gain exclusion, the 24-of-60-month ownership and use tests within the five years ending on the sale date, and the restriction after excluding gain on another home in the prior two years. It does not decide whether a specific sale qualifies.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_p551_basis": {
        "label": "IRS Publication 551 (12/2025) — Basis of Assets",
        "url": "https://www.irs.gov/publications/p551",
        "scope": "States that inherited basis is generally fair market value at death (or the alternate valuation date), that depreciation reduces basis by amounts deducted or deductible, and gives the like-kind exchange basis rules. It does not supply this household's basis.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_p527_depr": {
        "label": "IRS Publication 527 (2025) — Depreciation of rental property",
        "url": "https://www.irs.gov/publications/p527",
        "scope": "States that depreciation is allowed only on the rental-use part, that it reduces basis for later gain or loss, that land cannot be depreciated, that depreciation begins when the property is placed in service (including conversion from personal use), and that a converted home's depreciable basis is the lesser of adjusted basis or fair market value at conversion. It does not compute this property's deduction.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_p551_1031": {
        "label": "IRS Publication 551 (12/2025) — Like-kind exchanges of real property",
        "url": "https://www.irs.gov/publications/p551#en_US_202512_publink1000115306",
        "scope": "States that an exchange of real property may be nontaxable under section 1031 only if both the property transferred and the property received are held for business or investment purposes, that the replacement basis generally carries over, and that exchange expenses are capitalized into the replacement basis. It does not decide whether this household's exchange qualifies.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "ca_rtc11911": {
        "label": "California Revenue and Taxation Code §11911",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=11911",
        "scope": "Authorises a county documentary transfer tax of 55 cents for each 500 dollars (or fractional part) of the consideration or value conveyed over 100 dollars, allows a conforming city tax at one-half that rate, and requires the county to credit a conforming city tax. It does not state which localities have adopted one.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "ca_rtc11932": {
        "label": "California Revenue and Taxation Code §11932",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=11932",
        "scope": "Requires every document subject to the tax, in a taxing county, to show on its face the amount of tax due and where the property is located. It does not set an exemption for a particular transfer.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "ca_rtc11921": {
        "label": "California Revenue and Taxation Code §11921",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=11921",
        "scope": "Within the Documentary Transfer Tax Act exemptions chapter (§§11921-11930.5), exempts an instrument in writing given to secure a debt. Read together with §11927 (community-property divisions) it shows the exemptions are itemised by section; it does not exempt a trust distribution.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "scc_transfer_tax": {
        "label": "Santa Clara County Clerk-Recorder — Recording real estate (documentary transfer tax)",
        "url": "https://clerkrecorder.santaclaracounty.gov/recording-documents/recording-real-estate",
        "scope": "States that documentary transfer tax is due on all changes of ownership unless a statutory exemption is cited, computed at 0.55 per 500 dollars or fractional portion of value excluding liens of record, that San Jose, Palo Alto and Mountain View parcels are taxed at 1.65 per 500 dollars, that tax is collected at recording, and that a missing or incomplete PCOR adds 20 dollars. It does not value a parcel.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "scc_record_fees": {
        "label": "Santa Clara County Clerk-Recorder — Record fees and fee schedule",
        "url": "https://clerkrecorder.santaclaracounty.gov/resources/fee-schedule",
        "scope": "Publishes the recording fee schedule: standard-size first page 102 dollars (which the companion Record fees page itemises as a 25 dollar base including the 10 dollar real-estate fraud fee, plus a 75 dollar per-title Building Homes and Jobs fee and a 2 dollar restrictive-covenant fee), 3 dollars per additional page, 5 dollars for a conformed copy, 20 dollars for a missing PCOR, 10 dollars survey-monument fee, plus the county and city transfer-tax lines and Measure E / Measure G notices. It does not price a specific escrow.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "scc_measure_e": {
        "label": "Santa Clara County Clerk-Recorder — Measure E (City of San Jose only)",
        "url": "https://clerkrecorder.santaclaracounty.gov/recording-documents/recording-real-estate/measure-e",
        "scope": "States that the San Jose real property transfer tax collected by the County from July 1, 2025 applies to transfers over 2,300,000 dollars at 0.75%, 1% and 1.5% tiers on the entire consideration, and that inquiries go to the City of San Jose. It is a San Jose measure; the page does not extend it to other Santa Clara County cities.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "scc_measure_g": {
        "label": "Santa Clara County Clerk-Recorder — Measure G (City of Mountain View only)",
        "url": "https://clerkrecorder.santaclaracounty.gov/measure-g",
        "scope": "States that Mountain View Measure G adds a tier of 15 dollars per 1,000 dollars of sale price for transfers of 6,000,000 dollars or more, collected by the County from March 25, 2025, with transfers under that figure still paying the 1.65 per 500 dollars conveyance tax. It does not apply outside Mountain View.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "sf_recorder_fees": {
        "label": "San Francisco Assessor-Recorder — Fees to record a document in San Francisco",
        "url": "https://www.sf.gov/reports--march-2024--fees-record-document-san-francisco",
        "scope": "Publishes the City and County transfer-tax rate tiers (2.50, 3.40, 3.75, 11.25, 27.50 and 30.00 dollars for each 500 dollars or portion, by value band), the recorder fee schedule (14 dollar base, 17 dollar fraud-fee base, 3 dollars per additional page, 75 dollars to 225 dollars Building Homes and Jobs fee, 10 dollar survey-monument fee on deeds subject to transfer tax, 20 dollars for a missing PCOR), the transfer-tax affidavit requirement, and the exemptions from the state recording fee. It does not value a parcel.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "cupertino_fiscal_transfer": {
        "label": "City of Cupertino — Fiscal impact analysis example (property transfer tax)",
        "url": "https://www.cupertino.gov/files/assets/city/v/1/departments/documents/community-development/planning/forms-and-handouts/fiscal-impact-analysis-example.pdf",
        "scope": "A city planning document (dated 9/7/2018) that lists a 0.55 per 1,000 dollars city property transfer tax rate and cites Chapter 3.04 of the Cupertino Municipal Code. It is not the code text and not a current-year tax notice, so the rate needs confirmation against the ordinance before use in an escrow estimate.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "sfmta_prop_h": {
        "label": "SFMTA — Stronger Muni For All parcel tax FAQ",
        "url": "https://www.sfmta.com/getting-around/muni/parcel/frequently-asked-questions",
        "scope": "States the measure's first-charge fiscal year, the first-year per-parcel amounts by property class and size, the annual inflation adjustment, the senior and disabled principal-residence exemption, the per-unit credit for qualifying occupied multifamily owners, the pass-through limit for rent-controlled tenants, and the expiration date. It does not determine whether one parcel qualifies for relief.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "sf_prop_h_text": {
        "label": "City and County of San Francisco — Proposition H measure text (Ordinance adding B&T Code §§1801-1815)",
        "url": "https://media.api.sf.gov/documents/Legal_Text_3X0F1JU.pdf",
        "scope": "The official measure text adding Business and Tax Regulation Code sections 1801-1815: the parcel-charge schedule by building area, the transit-only use restriction, and the annual independent performance audit. It is the approved ordinance text, not a bill proposal.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "sfmta_closed": {
        "label": "SFMTA — recording-fee page retrieval for the Muni parcel tax",
        "url": "https://www.sfmta.com/getting-around/muni/parcel",
        "scope": "Retrieved during this review; the FAQ page carries the operative published figures used on this site.",
        "verified": False,
        "checked": "2026-11-15",
    },
    "irs_706_sched_a": {
        "label": "IRS — About Form 706 (Schedule A, real estate)",
        "url": "https://www.irs.gov/forms-pubs/about-form-706",
        "scope": "Describes the United States Estate (and Generation-Skipping Transfer) Tax Return and its Schedule A for real estate, which is the form-based structure the private estate inventory worksheet follows. It does not value this estate.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_706_instr": {
        "label": "IRS — Instructions for Form 706 (Rev. July 2026)",
        "url": "https://www.irs.gov/pub/irs-pdf/i706.pdf",
        "scope": "States the filing test (gross estate plus adjusted taxable gifts plus the specific exemption against the year-of-death basic exclusion, 15,000,000 dollars for 2026 deaths), Schedule A for real estate, and the circumstances in which a return is filed to elect portability of the unused exclusion. It does not project a future-year threshold.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_topic409": {
        "label": "IRS Topic no. 409 — Capital gains and losses",
        "url": "https://www.irs.gov/taxtopics/tc409.html",
        "scope": "States that unrecaptured section 1250 gain from the sale of section 1250 real property is taxed at a maximum rate of 25%. It does not compute a particular seller's rate or gain.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_p544": {
        "label": "IRS Publication 544 (2025) — Sales of assets, like-kind exchanges",
        "url": "https://www.irs.gov/publications/p544",
        "scope": "States that after 2017 like-kind treatment applies only to real property held for investment or productive use in a trade or business, and describes the recognition and basis mechanics of an exchange. It does not decide whether a specific exchange qualifies.",
        "verified": True,
        "checked": "2026-11-15",
    },
}

# ---------------------------------------------------------------------------
# Privacy-rounded case data and derived projections (T3D3, 2026-11-15).
#
# Owner-supplied inputs below are rounded to the nearest ten dollars in the
# source data itself; the generator never sees an unrounded household figure.
# Every derived output goes through money10() so published amounts always end
# in 0 (enforced by tools/verify.py). Assumptions are labeled assumptions:
# they are scenario inputs, not evidence, and each page states them.
# ---------------------------------------------------------------------------
import math


def round10(value: float) -> int:
    return int(math.floor(value / 10.0 + 0.5)) * 10


def money10(value: float) -> str:
    return f"${round10(value):,}"


PROPERTY_A = {
    "short": "Property A (anticipated trust transfer)",
    "region": "Cupertino area, California (ZIP 95014)",
    "value_2026": 3_100_000,
    "assessed": {2014: 440310, 2015: 449100, 2016: 455950, 2017: 465070,
                 2018: 474370, 2019: 483850, 2020: 493530, 2021: 498640,
                 2022: 508610, 2023: 518790, 2024: 529160, 2025: 539740,
                 2026: 550540},
    "tax": {2014: 5970, 2015: 6130, 2016: 6410, 2017: 6380, 2018: 6380,
            2019: 6570, 2020: 6570, 2021: 6660, 2022: 6760, 2023: 6920,
            2024: 7000, 2025: 7210},
    "water_month": (100, 150),
    "solar_credit_month": (10, 20),
    "insurance_owner_estimate": 1500,
}

PROPERTY_B = {
    "short": "Property B (already owned)",
    "region": "San Francisco Outer Sunset area (ZIP 94122)",
    "value_2026": 1_800_000,
    "assessed": {2016: 96_560, 2017: 98_490, 2018: 100460, 2019: 102470,
                 2020: 104510, 2021: 105600, 2022: 107660, 2023: 109810,
                 2024: 112010, 2025: 114250},
    "tax": {2016: 1680, 2017: 1740, 2018: 2060, 2019: 2130, 2020: 2200,
            2021: 2070, 2022: 2110, 2023: 2180, 2024: 2320, 2025: 2440},
    "rent_month": 7150,
    "rented_units": 2,
    "total_units": 3,
    "water_month": (330, 400),
    "electric_month": (30, 70),
    "insurance_owner_estimate": 1500,
}

BASE_YEAR = 2026
INHERIT_YEAR = 2045            # midpoint of the owner's 2040-2050 planning window
A_GROWTH = 0.04                # market-value scenario (assumption)
ASSESS_CAP = 0.02              # Proposition 13 maximum annual growth (sourced rule)
RATE_A = PROPERTY_A["tax"][2025] / PROPERTY_A["assessed"][2025]   # derived, about 1.34%
RATE_B = PROPERTY_B["tax"][2025] / PROPERTY_B["assessed"][2025]   # derived, about 2.14%
PROP19_EXCL_2025 = 1_044_586   # official BOE LTA 2025/009 amount (2025-2027 window)
EXCL_GROWTH = 0.03             # assumption: exclusion indexing near CA house-price growth
ESTATE_IDX = 0.02              # assumption: exclusion indexing near CBO long-run inflation
SELL_COST = 0.07               # assumption: commissions + closing costs (6-8% band)
REINVEST_RETURN = 0.06         # assumption: nominal return on sale proceeds
STAGING_YIELD = 0.043          # CBO 2026-2036 average 10-year Treasury (sourced anchor)
RENT_LOAD = 0.35               # assumption: operating+tax load absorbed from gross rent
MAINT_A_BAND = (8000, 15_000)  # assumption band: annual maintenance (owner reports less than B)
# Bands ported from models.py (session 377ea96a / PR #88) — planning assumptions, not quotes:
A_INS_BAND = (3000, 7000)      # market planning band for A insurance (owner guess likely low)
B_INS_BAND = (2500, 5000)      # landlord planning band for B insurance
B_UNIT3_RENT_BAND = (3300, 3800)  # unrented unit scenario band, not a quote
B_MAINT_BAND = (9000, 18_000)  # older 3-unit building maintenance band
A_INS_OWNER_FLAG = "owner guess — flagged as likely low"

# ---------------------------------------------------------------------------
# Transfer-cost, capital-gain, depreciation and Proposition H parameters
# (T9806-2/3). Tariff numbers below are the published official rates read on
# 2026-11-15 (see the cited source keys); the household amounts they produce
# are model output and are always published through money10().
# ---------------------------------------------------------------------------
SCC_DTT_PER_500 = 0.55          # RTC §11911(a) / County Clerk-Recorder schedule
SCC_CITY_CONVEYANCE_PER_500 = 1.65  # San Jose, Palo Alto, Mountain View only
SF_DTT_TIERS = [                # (upper bound of consideration, dollars per $500)
    (250_000, 2.50), (1_000_000, 3.40), (5_000_000, 3.75),
    (10_000_000, 11.25), (25_000_000, 27.50), (math.inf, 30.00),
]
SCC_PAGES = 2                    # escrow document packet assumption (labeled)
SCC_RECORDING_BASE = 102.00      # standard-size first page, all-in per the schedule
SCC_RECORDING_PAGE = 3.00
SF_RECORDING_BASE = 14.00
SF_RECORDING_PAGE = 3.00
SB2_FEE = 75.00                  # Building Homes and Jobs Act fee, per parcel/title
SB2_FEE_CAP = 225.00
MONUMENT_FEE = 10.00             # survey-monument fee on a transfer-taxable deed
PCOR_FEE = 20.00                 # charged when the PCOR is missing or incomplete
CUPERTINO_CITY_PER_1000 = 0.55   # city-published planning figure; ordinance text unread
FED_LTCG_HIGH = 0.20             # top 2026 long-term rate above the published breakpoint
FED_NIIT = 0.038                 # net investment income tax rate (registered source)
CA_TOP_BRACKET_FLAG = "12.3% top bracket not verified this session — see the flag register"
CA_BHST = 0.01                   # Form 540 line 62, on CA taxable income over $1,000,000
CA_BHST_FLOOR = 1_000_000
RESIDENTIAL_RECOVERY_YEARS = 27.5   # Pub. 527 / Pub. 946 convention
UNRECAPTURED_1250_MAX = 0.25        # IRS Topic 409
PROP_H_FIRST_YEAR = 2027            # FY 2027-28 is the first charge year (official FAQ)
PROP_H_SUNSET_FY = 2042             # expires June 30, 2042 (official FAQ)
PROP_H_SF_RATES = {                 # FY 2027-28 annual charges, official published amounts
    "single-family, up to 3,000 sq ft": 129,
    "multifamily, up to 5,000 sq ft": 249,
    "nonresidential, up to 5,000 sq ft": 799,
    "mixed-use, up to 5,000 sq ft": 799,
}
PROP_H_MULTIFAMILY_CREDIT = 249     # per qualifying occupied unit
PROP_H_PASSTHROUGH_CAP = 65         # annual cap on rent-controlled pass-through


def scc_transfer_tax(consideration: float, city_conveyance: bool = False) -> float:
    """County documentary transfer tax: 55 cents per $500 or fractional part."""
    import math as _m
    if consideration <= 100:
        return 0.0
    increments = _m.ceil(consideration / 500.0)
    rate = SCC_DTT_PER_500 + (SCC_CITY_CONVEYANCE_PER_500 if city_conveyance else 0.0)
    return increments * rate


def sf_transfer_tax(consideration: float) -> float:
    """San Francisco tiered transfer tax: the band rate applies to the whole figure."""
    import math as _m
    for upper, per_500 in SF_DTT_TIERS:
        if consideration <= upper:
            return _m.ceil(consideration / 500.0) * per_500
    return 0.0


def scc_recording_fee(pages: int = SCC_PAGES, with_pcor: bool = False) -> float:
    fee = SCC_RECORDING_BASE + SCC_RECORDING_PAGE * max(0, pages - 1) + SB2_FEE + MONUMENT_FEE
    return fee + (PCOR_FEE if with_pcor else 0.0)


def sf_recording_fee(pages: int = SCC_PAGES) -> float:
    # In San Francisco the SB2 fee is waived on documents transferring real property
    # where transfer tax is paid, so it is not added here.
    return SF_RECORDING_BASE + SF_RECORDING_PAGE * max(0, pages - 1) + MONUMENT_FEE


def transfer_cost_model(consideration: float, city_tax: bool = False) -> dict:
    dtt = scc_transfer_tax(consideration, city_conveyance=city_tax)
    recording = scc_recording_fee()
    return {"dtt": dtt, "recording": recording, "total": dtt + recording}


def capital_gain_tax(gain: float, ca_rate: float, other_ca_income: float = 0.0) -> dict:
    """Federal top-rate plus California ordinary-rate sensitivity, with line 62.

    This is a marginal sensitivity, not a return preparation: it applies the
    published 2026 top federal long-term rate, the NIIT, and the California
    rule that gain is ordinary income, plus the 1% tax on California taxable
    income above $1,000,000.
    """
    fed = gain * (FED_LTCG_HIGH + FED_NIIT)
    ca_taxable = gain + other_ca_income
    ca = ca_taxable * ca_rate
    bhst = max(0.0, ca_taxable - CA_BHST_FLOOR) * CA_BHST
    return {"federal": fed, "california": ca, "bhst": bhst,
            "total": fed + ca + bhst, "rate": (fed + ca + bhst) / gain if gain else 0.0}


def depreciation_model(building_basis: float, months_in_service: int) -> dict:
    """Straight-line 27.5-year residential depreciation with the mid-month rule."""
    annual = building_basis / RESIDENTIAL_RECOVERY_YEARS
    first_year = annual * ((12.5 - ((months_in_service - 1) % 12)) / 12.0)
    full_years = max(0, (months_in_service - 1) // 12)
    accumulated = first_year + full_years * annual
    return {"annual": annual, "first_year": first_year, "accumulated": accumulated}


def recapture_tax(accumulated_depreciation: float, gain: float,
                  rate: float = UNRECAPTURED_1250_MAX) -> dict:
    """Unrecaptured §1250 gain is taxed at a 25% maximum up to the depreciation."""
    unrecaptured = min(max(0.0, accumulated_depreciation), max(0.0, gain))
    remaining = max(0.0, gain - unrecaptured)
    return {"unrecaptured": unrecaptured, "long_term": remaining,
            "tax": unrecaptured * rate + remaining * (FED_LTCG_HIGH + FED_NIIT)}


def prop_h_charge(class_key: str, fiscal_year: int, inflation: float = 0.02) -> float | None:
    """Model the SF parcel charge for one class from the published first-year amount."""
    if class_key not in PROP_H_SF_RATES or fiscal_year < PROP_H_FIRST_YEAR:
        return None
    if fiscal_year > PROP_H_SUNSET_FY:
        return 0.0
    return PROP_H_SF_RATES[class_key] * (1 + inflation) ** (fiscal_year - PROP_H_FIRST_YEAR)


def prop_h_lifetime(class_key: str, inflation: float = 0.02) -> dict:
    total = 0.0
    first = None
    last = None
    for year in range(PROP_H_FIRST_YEAR, PROP_H_SUNSET_FY + 1):
        value = prop_h_charge(class_key, year, inflation) or 0.0
        total += value
        first = value if first is None else first
        last = value
    return {"years": PROP_H_SUNSET_FY - PROP_H_FIRST_YEAR + 1, "total": total,
            "first": first or 0.0, "last": last or 0.0}


def outcome_distribution() -> list[tuple[str, float]]:
    """Ten-year outcome spread for the staged and immediate sell paths (model output)."""
    scenarios = [
        ("1929-style: crash begins during staging", 0.89, 36, 0.0, 15),
        ("1929-style: crash begins after full entry", 0.89, 36, 0.0, 45),
        ("2008-style: crash begins during staging", 0.57, 17, 0.0, 15),
        ("2008-style: crash begins after full entry", 0.57, 17, 0.0, 45),
        ("Steady market at the assumed 6% return", 0.0, 12, 0.06, None),
        ("Slow market at 2% nominal", 0.0, 12, 0.02, None),
    ]
    out = []
    for label, drawdown, trough, drift, crash in scenarios:
        horizon = 120
        staged = staging_model(SELL_NET_2045, 36, drawdown, trough, drift, 4.3, 3.0, crash, min_horizon=horizon)[0]
        immediate = staging_model(SELL_NET_2045, 0, drawdown, trough, drift, 4.3, 3.0, crash, min_horizon=horizon)[0]
        out.append((label, min(staged, immediate)))
    return out


def a_value(year: int) -> float:
    return PROPERTY_A["value_2026"] * (1 + A_GROWTH) ** (year - BASE_YEAR)


def a_assessed(year: int) -> float:
    return PROPERTY_A["assessed"][BASE_YEAR] * (1 + ASSESS_CAP) ** (year - BASE_YEAR)


def a_tax_exclusion(year: int) -> float:
    return a_assessed(year) * RATE_A


def excl_amount(year: int) -> float:
    return PROP19_EXCL_2025 * (1 + EXCL_GROWTH) ** (year - 2025)


def a_tax_reassessed(year: int, inherit: int = INHERIT_YEAR):
    if year < inherit:
        return None
    base = max(a_value(inherit) - excl_amount(inherit), 0.0)
    return base * (1 + ASSESS_CAP) ** (year - inherit) * RATE_A


def b_assessed(year: int) -> float:
    return PROPERTY_B["assessed"][2025] * (1 + ASSESS_CAP) ** (year - 2025)


def b_tax(year: int) -> float:
    return b_assessed(year) * RATE_B


def estate_threshold(year: int) -> float:
    if year == 2026:
        return 15_000_000
    if year == 2027:
        return 15_480_000
    return 15_480_000 * (1 + ESTATE_IDX) ** (year - 2027)


def tax_delta(year: int, inherit: int = INHERIT_YEAR):
    reassessed = a_tax_reassessed(year, inherit)
    if reassessed is None:
        return None
    return reassessed - a_tax_exclusion(year)


DELTA_2045 = tax_delta(INHERIT_YEAR)
DELTA_10YR = sum(tax_delta(y) for y in range(INHERIT_YEAR, INHERIT_YEAR + 10))
RENT_HURDLE_MONTH = (DELTA_10YR / 10) / 12 / (1 - RENT_LOAD)
FMV_2045 = a_value(INHERIT_YEAR)
SELL_NET_2045 = FMV_2045 * (1 - SELL_COST)
FBYY_2045 = a_assessed(INHERIT_YEAR)

# Priced sell path (T9806-2): the transfer-cost layer sits between the price and
# the investable proceeds. Commission/closing assumption stays at SELL_COST; the
# documentary transfer tax and recording fees use the published schedules above.
SCC_DTT_2045 = scc_transfer_tax(FMV_2045)
SCC_RECORDING_2045 = scc_recording_fee()
SELL_NET_AFTER_TRANSFER_2045 = SELL_NET_2045 - SCC_DTT_2045 - SCC_RECORDING_2045
# Same-year sale from a date-of-death basis: gain is the difference between the
# price and the estate value less selling costs, so it is near zero by design.
GAIN_SAME_YEAR = max(0.0, FMV_2045 - FMV_2045 - FMV_2045 * SELL_COST)
# San Francisco comparison for the already-owned property, if it were ever sold.
SF_DTT_B = sf_transfer_tax(PROPERTY_B["value_2026"])
SF_RECORDING_B = sf_recording_fee()
# Alternative county reading (see the flag register): 1.10 per $500 doubles the tax.
SCC_DTT_2045_ALT = scc_transfer_tax(FMV_2045) * 2


def staging_model(proceeds: float, staging_months: int, drawdown: float,
                  trough_months: int, drift: float, yield1: float, yield2: float,
                  crash_start, min_horizon: int = 0):
    """Mirror of the browser staging tool, in dollars, for the static table."""
    horizon = max(staging_months, (crash_start if crash_start is not None else 0) + trough_months, min_horizon)

    def index_at(month: int) -> float:
        if crash_start is None or month < crash_start:
            return (1 + drift) ** (month / 12)
        peak = (1 + drift) ** (crash_start / 12)
        elapsed = min(1.0, max(0.0, (month - crash_start) / trough_months))
        return peak * (1 - drawdown * elapsed)

    reserve = proceeds
    phased = 0.0
    for month in range(1, horizon + 1):
        if month <= staging_months:
            annual = (yield1 if month <= 12 else yield2) / 100
            reserve *= (1 + annual) ** (1 / 12)
            purchase = min(proceeds / staging_months, reserve)
            phased += purchase / index_at(month)
            reserve -= purchase
            if month == staging_months and reserve > 0:
                phased += reserve / index_at(month)
                reserve = 0
    final = index_at(horizon)
    return phased * final + reserve, proceeds * final


def staging_rows() -> list[dict]:
    rows = []
    scenarios = [
        ("Steady market (8%/yr, no crash)", None, 0.0, 0.0, 0.08, 0),
        ("2008-style entry (57% decline over 17 months)", 0.57, 0.0, 0.0, 0.0, 17),
        ("1929-style entry (89% decline over 36 months)", 0.89, 0.0, 0.0, 0.0, 36),
    ]
    for label, drawdown, y1, y2, drift, trough in scenarios:
        crash = 15 if drawdown else None
        horizon = max(36, (crash or 0) + trough)
        lump = staging_model(SELL_NET_2045, 0, drawdown, trough, drift, y1, y2, crash, min_horizon=horizon)[1]
        p24 = staging_model(SELL_NET_2045, 24, drawdown, trough, drift, y1, y2, crash, min_horizon=horizon)[0]
        p36 = staging_model(SELL_NET_2045, 36, drawdown, trough, drift, y1, y2, crash, min_horizon=horizon)[0]
        rows.append({"cells": [label, money10(lump), money10(p24), money10(p36)],
                     "status": "Assumption", "sources": ["treasury_bills", "treasury_notes", "cbo_rates", "fed_2008", "fed_1929"]})
    return rows


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
    ("Properties", [
        ("pages/property-profiles.html", "Property profiles (rounded figures)"),
        ("pages/operating-costs.html", "Costs & coverage"),
    ]),
    ("Numbers", [
        ("pages/projections.html", "Projection worksheet"),
        ("pages/property-tax.html", "Property-tax rules"),
        ("pages/rental-economics.html", "Rental economics & Prop H"),
    ]),
    ("Stress tests", [
        ("pages/black-swan.html", "Black-swan conditions"),
        ("pages/phased-investing.html", "Treasury staging tool"),
    ]),
    ("Law & process", [
        ("pages/estate-thresholds.html", "Estate-tax thresholds"),
        ("pages/inheritance-process.html", "Deadline timeline"),
        ("pages/law-watchlist.html", "Law watchlist"),
        ("pages/sale-and-transfer.html", "Sale, transfer tax & fees"),
    ]),
    ("Prepare", [
        ("pages/private-file.html", "Private file & pre-commitment"),
        ("pages/decision-log.html", "Decision log"),
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
    "pages/property-profiles.html",
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
    "pages/sale-and-transfer.html",
    "pages/rental-economics.html",
    "pages/private-file.html",
    "pages/attorney-cpa-brief.html",
    "pages/decision-log.html",
    "pages/flagged-for-review.html",
    "pages/glossary.html",
    "pages/sources.html",
    "pages/privacy.html",
]


class SafeHTML(str):
    """A small explicit marker for trusted, locally generated HTML fragments."""


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def source_link(key: str, label: str | None = None) -> str:
    source = SOURCES[key]
    return (
        f'<a class="source" href="{esc(source["url"])}" '
        f'title="{esc(source["scope"])}" rel="noopener noreferrer">'
        f'{esc(label or source["label"])}</a>'
    )


def badge(status: str) -> str:
    css = {
        "Verified": "verified",
        "Missing": "missing",
        "Owner-supplied": "owner",
        "Owner-supplied (privacy-rounded)": "owner",
        "Cross-checked": "guidance",
        "Projection": "projection",
        "Projection": "projection",
        "Assumption": "assumption",
        "Guidance": "guidance",
        "Not verified": "missing",
        "Action needed": "guidance",
        "Historical": "verified",
        "Chaptered": "verified",
        "Proposal—not law": "proposal",
    }.get(status, "guidance")
    return f'<span class="badge {css}">{esc(status)}</span>'


def cell(value: object) -> str:
    if isinstance(value, SafeHTML):
        return f"<td>{value}</td>"
    return f"<td>{esc(value)}</td>"


def make_table(title: str, headers: list[str], rows: list[dict], note: str = "", source_labels: dict[str, str] | None = None) -> str:
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
        labels = source_labels or {}
        links = ' <span aria-hidden="true">·</span> '.join(
            source_link(key, labels.get(key)) for key in keys
        )
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
<meta name="description" content="Privacy-safe, source-linked decision framework. No property addresses, locations, valuations, rents, or expense histories are published.">
<title>{esc(title)} · {esc(SITE_TITLE)}</title>
<link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/app.js" defer></script>
</head><body class="{esc(page_class)}"><a class="skip" href="#main">Skip to content</a>
<div class="layout">
<aside class="sidebar"><a class="brand" href="{prefix}index.html"><span class="brand-icon" aria-hidden="true">◈</span><span>PRIVATE<br>DECISION BRIEF</span></a>
<p class="sidebar-note">Trust transfer +<br>already-owned property</p>
<nav aria-label="Main navigation">{build_nav(path)}</nav>
<div class="sidebar-bottom">No names, addresses or parcel numbers<br>Figures rounded to the nearest $10<br>Source dates in register</div></aside>
<div class="workspace"><header class="topbar"><span>RESEARCH / DECISION SUPPORT</span><div><span class="privacy-dot" aria-hidden="true"></span> Privacy-first <button class="print-button no-print" id="print-page" type="button">Print</button></div></header>
<main id="main"><div class="page-heading"><span class="eyebrow">{esc(eyebrow)}</span><h1>{esc(title)}</h1><p class="lead">{esc(intro)}</p></div>{body}</main>
<footer><strong>Planning framework only.</strong> Not legal, tax, insurance, appraisal or investment advice. A source supports only its stated scope, not a private fact. Owner-supplied figures are privacy-rounded to the nearest $10 at the owner's direction and flagged; blanks mean unknown, not zero.<br>
<a href="{prefix}pages/privacy.html">Privacy &amp; limits</a> · <a href="{prefix}pages/sources.html">Official sources</a> · <a href="{prefix}pages/flagged-for-review.html">Flagged for review</a></footer>
</div></div></body></html>'''


def build_index() -> str:
    rows = [
        {"cells": ["Trust, title and timing", "The actual trust, amendments, trustee authority, distribution trigger and debt are not public or independently confirmed.", "Obtain the executed trust/deed and a written trustee timeline before comparing any path."], "status": "Missing", "sources": ["ca_prob160617", "ca_rtc480"]},
        {"cells": ["Property-tax exclusion eligibility", "This is the single largest lever: at the modeled 2045 transfer, qualifying keeps the base at about " + money10(FBYY_2045) + " and the tax at about " + money10(a_tax_exclusion(2045)) + " per year, while failing to qualify reassesses toward market value minus the statutory exclusion — about " + money10(a_tax_reassessed(2045)) + " per year.", "Confirm the eligible relationship, the transferor's principal residence, transferee occupancy within one year, the homeowners' exemption filing within one year, and the claim within three years."], "status": "Owner-supplied (privacy-rounded)", "sources": ["boe_prop19", "ca_rtc63", "boe_lta_2025_009", "owner_a"]},
        {"cells": ["Federal estate-tax exposure", "The 2026 Form 706 filing test uses gross estate plus adjusted taxable gifts and the specific gift-tax exemption; a portability election can also require filing below the threshold.", "Obtain the full estate inventory, prior gifts, deductions and any spouse/portability facts; this is not a per-heir allowance."], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["Already-owned property: rental income continues under every path", "Property B supplies about " + money10(PROPERTY_B["rent_month"]) + " per month of gross rent from two rented units (owner-supplied, rounded) and does not reassess at the inheritance. Its covered-unit rent increases are capped at 1.6% for March 2026 - February 2027.", "Include B's rent, vacancy and tenant obligations in a private model, separately from A; confirm the vacant unit's lawful status before counting its rent."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "irs_rental", "sf_rent_board"]},
        {"cells": ["Rent A instead of living in it: the hurdle", "Renting A triggers the reassessment branch: after an assumed 35% operating-and-tax load, gross rent must exceed about " + money10(RENT_HURDLE_MONTH) + " per month just to offset the " + money10(DELTA_2045) + " per-year property-tax difference. What A would actually rent for is unknown and unverified.", "Obtain written rent comparables for A before ranking the rent path; the hurdle is a derived planning number, not a rent appraisal."], "status": "Assumption", "sources": ["owner_a", "boe_prop19", "ca_rtc63", "irs_rental"]},
        {"cells": ["What a sale actually costs and leaves", "The public charge on a conveyance is set by published schedules and is small next to the property-tax branch: at the modeled 2045 figures the county documentary transfer tax is about " + money10(SCC_DTT_2045) + " and recording about " + money10(SCC_RECORDING_2045) + ", on top of an assumed 7% commission and closing cost. A sale in the transfer year also shows little taxable gain, because basis is generally the date-of-death value.", "Confirm the county's current rate wording and any city conveyance tax in the escrow estimate, obtain the executor's basis statement, and decide before listing whether a like-kind exchange is wanted."], "status": "Cross-checked", "sources": ["scc_transfer_tax", "ca_rtc11911", "irs_p551_basis", "irs_p551_1031"]},
        {"cells": ["Rental taxation and the new San Francisco parcel charge", "Property B's rented units generate depreciation now and recapture later (a published 25% maximum on unrecaptured section 1250 gain), and the approved Muni parcel tax charges the parcel from fiscal year 2027-28 with a rent-controlled pass-through ceiling. Property A, in Cupertino, is not charged that tax.", "Get the CPA's depreciation schedule and B's basis; confirm the building area and any exemption before pricing B's net rent, and re-check the charge each July."], "status": "Verified", "sources": ["irs_topic409", "irs_p527_depr", "sfmta_prop_h", "sf_prop_h_text"]},
        {"cells": ["Insurance, repairs and utilities", "Official public sources do not determine a private premium, repair budget, water bill or solar credit.", "Obtain separate written owner-occupied / landlord insurance quotes, inspection bids, utility bills and solar tariff documents."], "status": "Missing", "sources": ["cdi", "cslb", "water_board", "cpuc_solar"]},
        {"cells": ["Investment entry and reinvestment risk", "A 24–36 month Treasury staging plan changes exposure timing but adds reinvestment risk if yields fall; equity prices can fall during or after staging.", "Use the local-only stress tool, replace its explicit assumptions with then-current net yields, and compare crash-during-wait with crash-after-wait."], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
        {"cells": ["Long-range law and market conditions", "No official source can verify future estate thresholds, property values, insurance costs, rent or returns decades ahead.", "Re-check enacted law, official bills, valuations and quotes close to the transfer; do not extrapolate a single rate for fifty years."], "status": "Missing", "sources": ["irs_2027", "cbo_rates", "fhfa_hpi"]},
    ]
    body = callout(
        "Conditional best plan under the baseline assumptions (owner-supplied, privacy-rounded figures)",
        "Live in Property A after the transfer and claim the family-home exclusion: occupy within one year, file the homeowners' exemption within one year, and file the intergenerational claim within three years. At the modeled 2045 transfer this preserves the long-held base and costs about " + money10(a_tax_exclusion(2045)) + " per year in property tax, versus about " + money10(a_tax_reassessed(2045)) + " per year if the home is instead reassessed — a difference of about " + money10(DELTA_2045) + " every year, about " + money10(DELTA_10YR) + " over the first ten years. Keep Property B as is: its rental income continues under either choice. Selling A instead nets about " + money10(SELL_NET_AFTER_TRANSFER_2045) + " after an assumed 7% sale cost, the published county documentary transfer tax (about " + money10(SCC_DTT_2045) + ") and recording fees (about " + money10(SCC_RECORDING_2045) + "), and moves the decision from property tax to reinvestment risk. REINVESTMENT RISK, BESIDE THE HEADLINE: any sale proceeds parked in 3-month-to-2-year Treasuries for 24-36 months earn the then-current auction rate, which may be lower at each renewal; staged buying also lags a rising market. See the black-swan page before treating a sale as the default.",
        "warning",
    )
    body += make_table(
        "What would change the answer?",
        ["Decision-changing fact", "What is established now", "Next evidence / decision gate"],
        rows,
        "This is the first-screen triage list. Official links support the rule or process shown; they do not verify private title, occupancy, cost or tax facts.",
    )
    body += callout(
        "Reinvestment risk sits beside the headline",
        "Parking sale proceeds in 3-month-to-2-year Treasuries for 24–36 months changes when the money enters the market, not how risky the market is. Each maturing rung is reinvested at an unknown future auction rate, a rising market makes staged buying lag, and a decline that begins after staging ends hits a fully invested balance. The local-only ladder panel quantifies the first effect.",
        "info",
    )
    body += callout(
        "Keep the ownership roles distinct",
        "Property A is the anticipated trust transfer. Property B is already owned. A choice to occupy, rent or sell one asset must not silently assume that the other asset has the same owner, tax basis, assessment, lease or operating costs.",
        "info",
    )
    body += cards("Use this workspace in order", [
        ("1. Resolve the questions", "Collect the trust, tax, title, lease, assessment, insurance and utility records in a private vault.", "pages/questions.html"),
        ("2. Compare complete paths", "Keep live, rent, sell, mixed occupancy and staged reinvestment alternatives separate.", "pages/decision-analysis.html"),
        ("3. Stress the timing", "Compare 24–36 months of Treasury parking against immediate entry, with the reinvestment penalty shown.", "pages/phased-investing.html"),
        ("4. Review with advisers", "Print a one-page attorney and CPA briefing sheet; no identifying details are required on it.", "pages/attorney-cpa-brief.html"),
        ("5. Choose improvements", "Record which decision-quality suggestions you want investigated before anything is changed.", "pages/decision-log.html"),
    ])
    body += paragraph("Rounded-figure policy (owner-directed)", "At the owner's written instruction, the figures that drive this decision are published, rounded to the nearest ten dollars so they cannot be searched back to a source record: 'Costs and numbers should be used but rounded to the nearest $10 increments ... and should be reported in any decision analysis.' Owner-supplied rows are badged Owner-supplied (privacy-rounded) and linked to the official record that can confirm them; projections are badged Projection or Assumption; values that are simply unknown stay blank. Names, street addresses and parcel identifiers are never published.")
    return render_page(
        "index.html",
        "Decision overview",
        "A planning framework for an anticipated trust transfer and a separate already-owned property. Owner-supplied figures are published privacy-rounded to the nearest ten dollars; no names, addresses or parcel numbers appear anywhere.",
        body,
        "START HERE",
    )


def build_executive_summary() -> str:
    rows = [
        {"cells": ["Asset roles", "Property A is an expected future trust transfer. Property B is separately already owned. Whether B has current rent, its amount, title and location are intentionally not published or independently verified.", "Confirm A's trust authority and title; include any B rental income as a private input and separately test whether B can serve as a residence."], "status": "Owner-supplied", "sources": ["ca_prob160617", "ca_rtc480", "irs_rental", "ca_rent"]},
        {"cells": ["Federal estate exclusion — 2026", "$15,000,000 basic exclusion amount for 2026 deaths; the Form 706 filing test adds gross estate, adjusted taxable gifts and the specific gift-tax exemption.", "This is a federal estate-level threshold, not a per-beneficiary inheritance allowance; portability can require filing below it."], "status": "Verified", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["Federal estate exclusion — 2027", "$15,480,000 basic exclusion amount for 2027 deaths.", "This official amount says nothing about a future-year threshold."], "status": "Verified", "sources": ["irs_2027"]},
        {"cells": ["Annual gift exclusion", "$19,000 for 2026 and $20,000 for 2027 per donor/recipient under the IRS announcement; it is not the estate-tax exclusion.", "Do not use the annual gift amount as the inheritance-tax threshold."], "status": "Verified", "sources": ["irs_2027"]},
        {"cells": ["California death taxes", "Current RTC §13301 bars state and local gift, inheritance, succession, legacy, income or estate tax on a transfer by reason of death; the State Controller says a California Estate Tax return is not required for deaths on or after 2005-01-01.", "Re-check the law for the actual year of death; this is not a future-law guarantee."], "status": "Verified", "sources": ["ca_rtc13301", "ca_death_tax"]},
        {"cells": ["California property tax", "Proposition 13 generally limits the general levy to 1% plus voter-approved bonded indebtedness and assessed-value growth to 2% per year; actual bills can include other components.", "The actual assessment, direct charges, ownership change and any Proposition 19 claim are unknown."], "status": "Verified", "sources": ["boe_pub29", "boe_prop19"]},
        {"cells": ["Property-specific recommendation", "Not available from official public sources without the trust, title, estate inventory, basis, appraisal, leases, costs, local rental rules and written quotes.", "Do not choose live/rent/sell based on an unverified headline or a single growth rate."], "status": "Missing", "sources": ["irs_basis", "irs_rental", "cdi", "hud_fmr"]},
    ]
    body = callout(
        "Executive conclusion (baseline assumptions)",
        "Under the published baseline (2045 transfer, owner-supplied rounded figures, labeled growth/indexing assumptions), the decisive lever is the Proposition 19 family-home exclusion: living in Property A and claiming it costs about $10,710 per year at 2045 versus about $62,040 reassessed — roughly $51,330 per year and $562,050 over ten years. The conditional best plan is therefore to make Property A the principal residence after transfer (occupy within one year, exemption within one year, claim within three years), keep Property B rented as is, and treat a sale of Property A (about $6,074,050 net under baseline assumptions) as the alternative that trades property-tax certainty for reinvestment and sequence risk. Verify the trust terms, the assessor's determination and the household's estate position with professionals before acting; the ranking flips if the exclusion fails, rent comparables beat the derived hurdle (about $7,210 per month), or housing costs in the sell path are small.",
        "warning",
    )
    body += make_table(
        "Important facts and current limits",
        ["Topic", "Verified rule or currently available information", "Decision implication"],
        rows,
    )
    event_rows = [
        {"cells": ["Level", "The estate's gross value including the anticipated inherited home and the already-owned property, measured at the valuation date.", "A range, not one number: appraisal low/base/high with the valuation date stated.", "The IRS filing test uses gross estate plus adjusted taxable gifts plus the specific gift-tax exemption, so a single asset value cannot decide exposure."], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["Direction", "Whether the headline number is a tax or an exemption — these are opposites and are frequently confused.", "Name the statutory amount and its year explicitly in every table.", "The 2026 basic exclusion is $15,000,000 and the 2027 amount is $15,480,000; the annual gift exclusion is $19,000 for 2026 and $20,000 for 2027."], "status": "Verified", "sources": ["irs_estate", "irs_2027"]},
        {"cells": ["Unit of measure", "Whether the figure applies per estate, per person or per heir.", "State 'estate-level' or 'per donor/recipient' on the same line as the number.", "Portability can require filing even below the threshold, and a beneficiary's share is not a threshold."], "status": "Verified", "sources": ["irs_estate_faq"]},
        {"cells": ["Year", "The year of death, not the year of planning.", "Attach the year of death to every threshold and re-check the IRS table in that year.", "The IRS publishes a filing-threshold table by year of death; future years are unknown."], "status": "Verified", "sources": ["irs_estate"]},
        {"cells": ["Baseline", "Whether the comparison is against zero tax, a current-law baseline, or a proposed change.", "Label the baseline and exclude unenacted proposals from the baseline.", "A bill or resolution is not law until enacted and effective; the official bill systems are the only acceptable evidence of status."], "status": "Guidance", "sources": ["congress_legislation", "ca_legislation"]},
        {"cells": ["State layer", "Whether California imposes a death-transfer tax on top of the federal tax.", "Check current RTC §13301 for the actual year of death.", "The statute currently bars state and local gift, inheritance, succession, legacy, income or estate taxes on a transfer by reason of death."], "status": "Verified", "sources": ["ca_rtc13301", "ca_death_tax"]},
        {"cells": ["Property-tax layer", "Whether the county reassesses the inherited home, and at what value.", "Model a qualifying and a non-qualifying case side by side.", "The intergenerational exclusion is conditional, and a missed claim can reassess the property at current value."], "status": "Verified", "sources": ["ca_rtc63", "boe_prop19", "ca_rtc51"]},
        {"cells": ["Income-tax layer", "Whether a later sale produces gain, and whether the main-home exclusion applies.", "Compute gain from the date-of-death basis; test the two-out-of-five-year use rule separately.", "Inherited basis is generally date-of-death fair market value, and the main-home exclusion requires ownership and use tests."], "status": "Verified", "sources": ["irs_basis", "irs_121"]},
    ]
    body += make_table("The five dimensions every threshold comparison must state", ["Dimension", "What usually goes wrong", "How to state it instead", "Official basis"], event_rows, "This table is a checklist for reading any threshold headline, not a calculation of a specific estate.")
    body += paragraph("What this workspace concludes, and what it refuses to conclude", "Three things are currently established well enough to rely on: the federal estate-tax threshold is an estate-level test that includes lifetime taxable gifts, California does not impose its own death-transfer tax under current law, and the intergenerational property-tax exclusion is conditional and claim-driven. Three things are not established: the trust's actual terms and authority, the household's estate composition and basis, and every property-level cost, rent and value. A best path is therefore not published. What is published is the exact sequence that would produce one: settle the legal and tax facts, price the carrying costs from real documents, then compare pure and mixed paths under stated ranges and adverse regimes.")
    body += paragraph("What would change the conclusion fastest", "If counsel confirms an unconstrained sale authority and the estate is comfortably below the filing threshold, the decision collapses to a comparison of after-tax proceeds against the net cash flow from holding. If the trust restricts sale or imposes occupancy conditions, most of the reinvestment analysis becomes moot until those conditions are resolved. If a family-home exclusion is unavailable, the property-tax difference alone can dominate every market scenario on this site.")
    body += cards("Next pages", [
        ("Missing evidence", "A question-by-question record list for counsel, CPA, assessor, insurer and rental adviser.", "pages/questions.html"),
        ("Current law", "Estate thresholds, California property-tax mechanics and transfer deadlines.", "pages/estate-thresholds.html"),
        ("Risk", "Historical stress anchors and a local-only Treasury phasing comparison.", "pages/black-swan.html"),
    ], current="pages/executive-summary.html")
    return render_page("pages/executive-summary.html", "Executive summary", "The short version: separate the assets, verify the rules that can change the answer, and leave private numbers blank until documents establish them.", body, "EXECUTIVE SUMMARY")


def build_property_profiles() -> str:
    a_hist_rows = []
    for year in range(2014, 2027):
        assessed = PROPERTY_A["assessed"].get(year)
        tax = PROPERTY_A["tax"].get(year)
        if year == 2026:
            tax_cell = money10(PROPERTY_A["assessed"][2026] * RATE_A)
            tax_status = "Projection"
        else:
            tax_cell = money10(tax) if tax else "—"
            tax_status = "Owner-supplied (privacy-rounded)"
        a_hist_rows.append({
            "cells": [year, money10(assessed) if assessed else "—", tax_cell],
            "status": tax_status if year != 2026 else "Projection",
            "sources": ["owner_a", "boe_pub29"],
        })
    b_hist_rows = []
    for year in range(2016, 2027):
        assessed = PROPERTY_B["assessed"].get(year)
        tax = PROPERTY_B["tax"].get(year)
        if year == 2026:
            b_hist_rows.append({
                "cells": [year, money10(assessed) if assessed else "—", money10(b_assessed(2026) * RATE_B)],
                "status": "Projection",
                "sources": ["owner_b", "boe_pub29"],
            })
        else:
            b_hist_rows.append({
                "cells": [year, money10(assessed) if assessed else "—", money10(tax) if tax else "—"],
                "status": "Owner-supplied (privacy-rounded)",
                "sources": ["owner_b", "boe_pub29"],
            })
    profile_rows = [
        {"cells": ["Role", "Anticipated future trust transfer to the current generation; the decision analysis must assume the transfer is a parent-child change in ownership.", "Property-tax treatment at transfer depends on the Proposition 19 family-home conditions; income-tax basis is separate."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_a", "ca_rtc63", "irs_basis"]},
        {"cells": ["Region", PROPERTY_A["region"] + ". No street address, parcel number or name is published.", "Region-level context only; it supports insurance, utility and tax-rule research and cannot locate the property."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_a", "sjw_rates"]},
        {"cells": ["Estimated market value — Nov 2026", money10(PROPERTY_A["value_2026"]), "Owner-supplied estimate. A defensible valuation for any real decision needs an appraisal at the relevant date."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_a", "fhfa_hpi"]},
        {"cells": ["Current assessed value (2026 roll)", money10(PROPERTY_A["assessed"][2026]), "Owner-supplied, rounded. Under Proposition 13 the assessed value can grow at most 2% per year absent a change in ownership or new construction."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_a", "boe_pub29", "ca_rtc51"]},
        {"cells": ["Derived effective tax rate", f"about {RATE_A * 100:.2f}% of assessed value (2025 tax divided by 2025 assessment)", "Derived from owner-supplied rounded figures; the actual bill includes voter-approved measures and direct charges that can change it."], "status": "Assumption", "sources": ["owner_a", "boe_pub29"]},
        {"cells": ["Water", f"${PROPERTY_A['water_month'][0]} to ${PROPERTY_A['water_month'][1]} per month (owner-supplied)", "Provider for the region publishes tariffs; the actual bill depends on metered usage and approved rates."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_a", "sjw_rates"]},
        {"cells": ["Electricity / solar", f"net credit of about ${PROPERTY_A['solar_credit_month'][0]} to ${PROPERTY_A['solar_credit_month'][1]} per month (owner-supplied)", "A generation credit depends on the tariff (legacy NEM vs net billing) and interconnection date; confirm from the account records."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_a", "cpuc_solar"]},
        {"cells": ["Homeowners insurance", f"owner estimate about {money10(PROPERTY_A['insurance_owner_estimate'])} per year — flagged as likely low; market planning band {money10(A_INS_BAND[0])} to {money10(A_INS_BAND[1])} per year", "No official source sets a household premium; the 2025-26 California market is under active regulatory change (Sustainable Insurance Strategy) and the FAIR Plan raised dwelling rates in late 2026. Obtain written quotes for the intended use."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_a", "cdi", "cdi_sis", "cdi_news"]},
        {"cells": ["Maintenance", "owner reports lower repair intensity than Property B; no band is established", "Inspection findings and licensed bids are the evidence; the projection model carries an assumption band of " + money10(MAINT_A_BAND[0]) + " to " + money10(MAINT_A_BAND[1]) + " per year (about 0.5% to 1.0% of value for older systems), labeled as an assumption."], "status": "Assumption", "sources": ["owner_a", "cslb"]},
    ]
    profile_rows_b = [
        {"cells": ["Role", "Already owned by the inheritor; three livable units, two currently rented, and the owner reports the property can serve as a residence without losing rental income.", "The already-owned role matters: no reassessment occurs from the future inheritance, and keeping B lets the household retain rental income whichever way Property A goes."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "ca_rent"]},
        {"cells": ["Region", PROPERTY_B["region"] + ". No street address, parcel number or name is published.", "Region-level context only."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "sfpuc_water"]},
        {"cells": ["Estimated market value — Nov 2026", money10(PROPERTY_B["value_2026"]), "Owner-supplied estimate; obtain an appraisal for any real transaction."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "fhfa_hpi"]},
        {"cells": ["Current assessed value (2025 roll)", money10(PROPERTY_B["assessed"][2025]), "Owner-supplied, rounded; the low base reflects long ownership under Proposition 13."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "boe_pub29"]},
        {"cells": ["Derived effective tax rate", f"about {RATE_B * 100:.2f}% of assessed value (2025 tax divided by 2025 assessment)", "Derived from owner-supplied rounded figures; San Francisco bills include voter-approved measures on top of the 1% base levy."], "status": "Assumption", "sources": ["owner_b", "boe_pub29"]},
        {"cells": ["Rental income", f"about {money10(PROPERTY_B['rent_month'])} per month from {PROPERTY_B['rented_units']} rented units (owner-supplied)", "Gross rent is not net income: vacancy, water, electricity, insurance, repairs, management and income tax all reduce it. Rent increases for covered units are capped by the local rent ordinance."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "irs_rental", "sf_rent_board"]},
        {"cells": ["Water / electricity", f"water {PROPERTY_B['water_month'][0]} to {PROPERTY_B['water_month'][1]} and electricity {PROPERTY_B['electric_month'][0]} to {PROPERTY_B['electric_month'][1]} per month for the building (owner-supplied)", "Combined-building figures; metering configuration determines how costs would be allocated if occupancy changes."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "sfpuc_water", "pge_tariffs"]},
        {"cells": ["Landlord insurance", f"owner estimate about {money10(PROPERTY_B['insurance_owner_estimate'])} per year — flagged as likely low; landlord planning band {money10(B_INS_BAND[0])} to {money10(B_INS_BAND[1])} per year", "A landlord/dwelling-fire policy is underwritten per property; no official premium table exists. Obtain written quotes."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "cdi", "cdi_sis"]},
        {"cells": ["Rent-increase rule", "The Rent Board states a 1.6% allowable annual increase for covered units from March 1, 2026 through February 28, 2027.", "Coverage depends on the building (units with a certificate of occupancy before June 13, 1979 are generally covered, with exceptions); confirm the unit status before modeling increases."], "status": "Verified", "sources": ["sf_rent_board", "ca_rent"]},
    ]
    body = callout(
        "Rounded figures, labeled evidence",
        "At the owner's written direction, property figures on this site are privacy-rounded to the nearest ten dollars so they cannot be searched back to a source record. No name, street address or parcel number is published. Every owner-supplied row carries an Owner-supplied (privacy-rounded) badge and a link to the official record that can confirm it. Values the owner has not supplied remain blank — blank means unknown, not zero.",
        "info",
    )
    body += make_table(
        "Property A — anticipated trust transfer profile",
        ["Attribute", "Value (privacy-rounded)", "Meaning and limits"],
        profile_rows,
        "The 2040-2050 trust-transfer window is the owner's stated plan, not a confirmed date. All forward numbers live on the projection page and are labeled assumptions.",
    )
    body += make_table(
        "Property A — assessment and tax history (owner-supplied, privacy-rounded)",
        ["Year", "Assessed value", "Property tax"],
        a_hist_rows,
        "The 2026 tax cell is a projection: 2026 assessed value times the derived effective rate. Historical rows are owner-supplied and rounded; verify against the county roll.",
    )
    body += make_table(
        "Property B — already-owned property profile",
        ["Attribute", "Value (privacy-rounded)", "Meaning and limits"],
        profile_rows_b,
    )
    body += make_table(
        "Property B — assessment and tax history (owner-supplied, privacy-rounded)",
        ["Year", "Assessed value", "Property tax"],
        b_hist_rows,
        "The 2026 tax cell is a projection: 2026 assessed value times the derived effective rate. Historical rows are owner-supplied and rounded.",
    )
    body += paragraph(
        "Why the two roles change the analysis",
        "Property B is already owned, so the future inheritance does not reassess it and its rental income continues under any plan for Property A. Property A's treatment at transfer is the decisive lever: if it can qualify as the transferee's principal residence under the family-home rules, the long-held base carries over; if it cannot, the taxable value resets toward market value minus the statutory exclusion amount. Keep the two assets' costs, basis and records separate in every calculation.",
    )
    return render_page(
        "pages/property-profiles.html",
        "Property profiles — rounded figures",
        "Side-by-side profiles of the anticipated trust transfer and the already-owned property, using owner-supplied figures rounded to the nearest ten dollars, with every row linked to the official record that can confirm it.",
        body,
        "PROPERTIES",
    )


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
    body = callout(
        "Conditional ranking under the baseline assumptions (see the stated limits)",
        "Baseline: 2045 transfer, owner-supplied rounded figures, 4% market-growth scenario, 2% assessed-value cap, derived effective rates, 3% exclusion indexing, 7% assumed sale costs, 35% assumed rent load. Under those assumptions the property-tax lever dominates: exclusion-claimed A costs about " + money10(a_tax_exclusion(2045)) + " per year at 2045 versus about " + money10(a_tax_reassessed(2045)) + " reassessed, and B's " + money10(PROPERTY_B["rent_month"]) + " per month of gross rent continues under every path. Ranking: 1) live in A with the family-home exclusion claimed and keep B rented; 2) rent A only if written rent comparables exceed the derived hurdle (about " + money10(RENT_HURDLE_MONTH) + " per month gross); 3) sell A (about " + money10(SELL_NET_AFTER_TRANSFER_2045) + " net after the assumed 7% sale cost, the published county transfer tax and the recording fees) and stage the proceeds — competitive only after counting where the household lives and the reinvestment risks on the black-swan page. The ranking flips if the exclusion fails, if rent comps beat the hurdle, or if the household's housing cost in the sell path is small. Reinvestment risk belongs beside headline 3: staged Treasuries earn an unknown renewal rate each rung, and staged buying lags a rising market.",
        "warning",
    )
    body += make_table("Mixed and pure paths to compare", ["Path", "Property A — anticipated trust transfer", "Property B — already owned", "Main uncertainty / risk"], rows, "The sources link to governing rules or official risk information. They do not establish whether a specific use, rent, exclusion or premium applies.")
    computed_rows = [
        {"cells": ["1 — Live in A (exclusion claimed); keep B rented",
                   money10(a_tax_exclusion(2045)) + " per year property tax at 2045; base stays about " + money10(FBYY_2045),
                   money10(-1 * DELTA_10YR) + " property-tax position versus the reassessed branch over 2045-2054, plus in-kind housing",
                   "Qualifies only if occupancy (within 1 year), the homeowners' exemption (within 1 year) and the claim (within 3 years) all happen; confirm with the assessor."],
         "status": "Projection", "sources": ["owner_a", "boe_prop19", "ca_rtc63", "ca_rtc218"]},
        {"cells": ["2 — Rent A; keep B and keep living in B",
                   "Reassessed branch: about " + money10(a_tax_reassessed(2045)) + " per year at 2045 (market value minus the statutory exclusion)",
                   "Needs gross rent above about " + money10(RENT_HURDLE_MONTH) + " per month to beat path 1 after an assumed 35% operating-and-tax load; actual rent for A is unknown",
                   "Landlord insurance, vacancy, management and income tax sit on top of the property-tax jump; obtain rent comps and quotes before ranking."],
         "status": "Assumption", "sources": ["owner_a", "boe_prop19", "ca_rtc63", "irs_rental", "irs_niit"]},
        {"cells": ["3 — Sell A at transfer; stage proceeds; keep B",
                   "Net proceeds about " + money10(SELL_NET_AFTER_TRANSFER_2045)
                                      + " after an assumed 7% sale cost, the published county transfer tax (" + money10(SCC_DTT_2045)
                                      + ") and the recording fees (" + money10(SCC_RECORDING_2045)
                                      + "); with a date-of-death basis, a sale in the transfer year shows little or no taxable gain",
                   "At the 6% assumed return the priced proceeds reach about " + money10(SELL_NET_AFTER_TRANSFER_2045 * (1 + REINVEST_RETURN) ** 10) + " in ten years — but path 1's house grows too, and path 3 must also pay for housing elsewhere",
                   "Reinvestment risk beside the headline: staged 3M-2Y Treasuries renew at unknown rates; a crash during or after staging changes the outcome materially (see the staging table). The income tax on a later sale, the depreciation recapture if the house is let first, and the transfer tax are priced on the sale-and-transfer page."],
         "status": "Assumption", "sources": ["owner_a", "irs_basis", "treasury_bills", "treasury_notes", "sec_stocks"]},
        {"cells": ["M1 — Live in A; rent B's vacant third unit",
                   "Same " + money10(a_tax_exclusion(2045)) + " property-tax branch as path 1; adds unit-3 rent (amount unknown)",
                   "Improves path 1's cash flow without touching A's tax branch; the vacant unit's lawful rentable status must be confirmed first",
                   "Rent-board coverage, permits and the lease for unit 3 are unverified."],
         "status": "Assumption", "sources": ["owner_b", "sf_rent_board", "irs_rental"]},
        {"cells": ["M2 — Live in A for years, then decide on renting or selling",
                   "Exclusion branch preserved at transfer; a later conversion to rental does not automatically undo the transfer-year exclusion — confirm the assessor's treatment before counting on it",
                   "Keeps the option value: sale can follow a later step-up-free gain only above date-of-death value",
                   "Later-move-out treatment is a flagged question (see questions page Q14); do not assume it."],
         "status": "Guidance", "sources": ["ca_rtc63", "boe_prop19", "irs_basis"]},
        {"cells": ["M3 — Sell B instead (keep A)",
                   "B's sale is a taxable event on B's own low basis (about " + money10(PROPERTY_B["assessed"][2025]) + " assessed is not income-tax basis); gain could be large",
                   "Loses the " + money10(PROPERTY_B["rent_month"]) + " per-month gross rent stream; changes the household's residence plan",
                   "B's income-tax basis is unknown and unverified — do not model this path without it."],
         "status": "Missing", "sources": ["owner_b", "irs_basis", "irs_121"]},
    ]
    body += make_table(
        "Computed path comparison at the modeled 2045 transfer (baseline assumptions)",
        ["Path", "Property-tax / sale anchor (2045)", "Ten-year effect (2045-2054)", "Decision hinge"],
        computed_rows,
        "Every number here is derived from owner-supplied rounded figures plus the labeled assumptions on the projections page. It is a decision framework, not a forecast or advice; a professional must confirm the law and the facts for the actual year.",
    )
    role_rows = [
        {"cells": ["Property A — anticipated trust transfer", "Nothing is owned yet; the asset, its basis, its assessment and the trustee's authority all depend on a transfer that has not happened. Any current occupancy, market value, tax bill or insurance premium is an assumption, not an established fact.", "Do not model A as if it were already owned. Show the pre-transfer and post-transfer states separately and label the transfer date as an open variable."], "status": "Owner-supplied", "sources": ["ca_prob160617", "ca_rtc480", "boe_prop19"]},
        {"cells": ["Property B — already owned", "The owner already holds title, basis, existing tenants and existing operating costs. Whether an owner can occupy part of it without ending an existing tenancy is a lease, local-rule and rent-law question, not a modelling convenience.", "Treat B's rent, vacancy, tenant obligations and basis as separate inputs. A mixed plan that assumes B keeps paying rent after the owner moves in must be verified, not assumed."], "status": "Owner-supplied", "sources": ["irs_rental", "ca_rent"]},
        {"cells": ["Why the distinction changes the answer", "Selling A and keeping B is a one-time capital event plus an ongoing operating asset. Living in A and renting B is two operating assets with one residence. Selling both is a full liquidation. Each carries a different tax basis, assessment history and risk profile.", "Compare paths on the same horizon, the same tax treatment and the same risk case. Mixing A's post-inheritance basis with B's historical costs silently biases the answer."], "status": "Guidance", "sources": ["irs_basis", "boe_pub29", "irs_rental"]},
    ]
    body += make_table("The ownership roles are different assets — keep them separate", ["Asset", "What is actually established", "Modelling rule"], role_rows, "Only the broad roles were supplied. Neither asset's value, basis, assessment, rent, lease, insurance or costs is verified here.")
    body += '''<section class="tool-section" aria-labelledby="path-tool-heading">
<h2 id="path-tool-heading">Path what-if controls — local only</h2>
<p class="table-note">Adjust the assumptions and the key numbers recompute in this browser. Defaults mirror the published baseline. Nothing is stored or transmitted. The tool now also prices the transfer tax, the recording fees, a gain-rate sensitivity and the recapture ceiling; it still does not prepare a tax return, and it does not know your insurance, maintenance or rent figures.</p>
<form id="path-tool" class="tool-grid">
<label>Market value at transfer<input id="path-value" type="number" min="0" max="99999999" step="10" value="6531230" inputmode="numeric"></label>
<label>Assessed base carried over<input id="path-base" type="number" min="0" max="99999999" step="10" value="802030" inputmode="numeric"></label>
<label>Effective tax rate (%)<input id="path-rate" type="number" min="0" max="5" step="0.01" value="1.34" inputmode="decimal"></label>
<label>Assessed-value growth cap (%)<input id="path-cap" type="number" min="0" max="10" step="0.1" value="2" inputmode="decimal"></label>
<label>Prop 19 exclusion at transfer<input id="path-excl" type="number" min="0" max="99999999" step="10" value="1886640" inputmode="numeric"></label>
<label>Rent operating load (%)<input id="path-load" type="number" min="0" max="90" step="1" value="35" inputmode="decimal"></label>
<label>Imputed rent on the unit you occupy (per month)<input id="path-imputed" type="number" min="0" max="9999" step="50" value="3550" inputmode="numeric"></label>
<label>Transfer tax (dollars per $500 of price)<input id="path-dtt" type="number" min="0" max="50" step="0.05" value="0.55" inputmode="decimal"></label>
<label>Recording and title fees (total)<input id="path-fees" type="number" min="0" max="9999999" step="10" value="190" inputmode="numeric"></label>
<label>Taxable gain as % of price<input id="path-gainpct" type="number" min="0" max="100" step="1" value="0" inputmode="numeric"></label>
<label>Assumed California marginal rate on the gain (%)<input id="path-ca" type="number" min="0" max="20" step="0.1" value="12.3" inputmode="decimal"></label>
<label>Accumulated depreciation if it was let first<input id="path-depr" type="number" min="0" max="999999" step="1000" value="0" inputmode="numeric"></label>
<label class="tool-check"><input id="path-principal" type="checkbox" value="1">Occupied 24 of the last 60 months (main-home exclusion)</label>
<div class="tool-actions no-print"><button id="path-reset" type="button">Reset to baseline</button><span class="tool-assumption">Derived values are rounded to the nearest $10 in the display.</span></div>
</form>
<div class="scenario-grid" aria-live="polite">
<article class="scenario-card"><h3>Exclusion claimed (live in A)</h3><dl><dt>Property tax, year 1</dt><dd id="path-tax-excl">—</dd><dt>Property tax, year 10</dt><dd id="path-tax-excl10">—</dd><dt>Ten-year cumulative</dt><dd id="path-tax-exclcum">—</dd></dl></article>
<article class="scenario-card"><h3>Reassessed (rent or sell branch)</h3><dl><dt>Property tax, year 1</dt><dd id="path-tax-re">—</dd><dt>Property tax, year 10</dt><dd id="path-tax-re10">—</dd><dt>Ten-year cumulative</dt><dd id="path-tax-recum">—</dd></dl></article>
<article class="scenario-card"><h3>Branch difference</h3><dl><dt>Annual difference, year 1</dt><dd id="path-delta1">—</dd><dt>Ten-year cumulative difference</dt><dd id="path-delta10">—</dd><dt>Rent hurdle per month</dt><dd id="path-hurdle">—</dd></dl></article>
<article class="scenario-card"><h3>Sell branch</h3><dl><dt>Net after transfer costs and this gain sensitivity</dt><dd id="path-sellnet">—</dd><dt>Proceeds at 6%/yr, year 10</dt><dd id="path-sell10">—</dd><dt>Reinvestment risk</dt><dd>see black-swan page</dd></dl></article>
<article class="scenario-card"><h3>Public charge on the conveyance</h3><dl><dt>Documentary transfer tax</dt><dd id="path-transfer-tax">—</dd><dt>Commission and other fees</dt><dd id="path-closing">—</dd><dt>Net before income tax</dt><dd id="path-net">—</dd></dl></article>
<article class="scenario-card"><h3>Income-tax sensitivity</h3><dl><dt>Taxable gain after any exclusion</dt><dd id="path-gain">—</dd><dt>Recapture at the 25% ceiling</dt><dd id="path-recap">—</dd><dt>Federal + California + 1% line 62</dt><dd id="path-taxes">—</dd></dl></article>
<article class="scenario-card"><h3>Living path, priced</h3><dl><dt>After-tax cash if sold</dt><dd id="path-aftertax">—</dd><dt>Ten-year imputed rent minus ten-year exclusion-branch tax</dt><dd id="path-imputed10">—</dd><dt>What this line is</dt><dd>rent avoided, not income earned</dd></dl></article>
</div>
<p id="path-status" class="tool-status" role="status">Change a control to rerun the local comparison.</p>
<p class="table-note">Model: exclusion branch taxes the carried-over base grown at the cap; reassessed branch taxes (market value minus exclusion) grown at the cap; both at the entered effective rate. The rent hurdle divides the ten-year difference by ten years, twelve months, and (1 − load). Transfer tax is the entered rate per 500 dollars applied to the whole price (the county's published rate is 0.55, and a conforming city tax is credited, not added). Gain is the entered percentage of price, less 250,000 dollars when the main-home exclusion is switched on; tax on the gain is the 25% ceiling on the depreciation portion, the top federal long-term rate plus 3.8% on the rest, the entered California rate on the whole gain, and 1% on the part of California taxable income above 1,000,000 dollars. Imputed rent values the unit an owner occupies over ten years against ten years of the exclusion-branch tax. Every rate is an assumption at the top of the published schedule; this is not tax advice.</p>
</section>'''

    body += paragraph("Comparison rule", "For every path, show after-tax cash flows, one-time sale or transfer costs, debt, vacancy, repairs, insurance, utilities, property tax, rent legality, liquidity and reinvestment risk. Compare the same time horizon and disclose every assumption.")
    return render_page("pages/decision-analysis.html", "Compare live, rent, sell and mixed paths", "The comparison is deliberately conditional. It does not assume that the trust asset and the already-owned asset have the same tax basis, title, rent, occupancy or costs.", body, "DECISION")


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
          {"cells": ["Q13 — What would Property A actually rent for, and what do insurance, management and vacancy really cost?", "No rent comparable, quote or bid for A exists; the model carries a derived rent hurdle of about " + money10(RENT_HURDLE_MONTH) + " per month instead of a market rent.", "The rent-versus-live ranking cannot be closed without these numbers; the hurdle is a planning figure, not evidence.", "At least three written rent comparables for similar homes, written landlord and owner-occupied insurance quotes, a property-management fee schedule and a vacancy assumption.", "Local property manager / licensed insurance broker"], "status": "Missing", "sources": ["hud_fmr", "irs_rental", "cdi"]},
        {"cells": ["Q14 — What happens to the family-home exclusion if the transferee later moves out of A?", "BOE guidance says the transferee must occupy the home as a principal residence; the consequence of a later conversion to rental is not established here.", "Mixed path M2 assumes the exclusion survives a later move-out; that assumption must be confirmed in writing before relying on it.", "A written assessor determination or counsel's opinion on post-occupancy conversion; BOE-19-P claim records.", "County assessor / property-tax counsel"], "status": "Missing", "sources": ["boe_prop19", "ca_rtc63", "boe_lta_2025_009"]},
        {"cells": ["Q15 — Marital status, filing status and the household's full estate inventory (including the 'considerable amount of money')", "The federal filing test is estate-level: gross estate plus adjusted taxable gifts against the $15,000,000 (2026) exclusion; portability can require filing below the threshold.", "Whether the estate approaches the threshold depends on facts not supplied; the assumption path to 2045-2050 is published on the thresholds page.", "Full asset/debt inventory, prior gift records, spouse/portability facts, beneficiary designations and the trust's funding schedule.", "CPA / estate attorney"], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq", "obbba_law"]},
    ]
    body = callout("Answers are bounded by evidence", "The case structure (one anticipated trust transfer, one already-owned property) and the owner-supplied rounded figures are carried into the public site. Law and public market data are linked; anything the owner has not supplied stays blank, and each blank row names the record and professional who can close it. Suggestions for discovering missing information appear in the final column of every row.", "info")
    body += make_table("Questions, information required and answer status", ["Question", "Information available", "Answer from verified evidence", "Record needed to close the gap", "Who should confirm"], rows, "Status Owner-supplied means only that the broad role appeared in the request; the official source link verifies the cited rule, not the household fact.")
    body += paragraph("Discovery order", "First collect trust and title records, then confirm estate valuation/basis and property-tax deadlines, then verify lawful use and leases, then request independent insurance/repair/utility data, and only then compare after-tax alternatives.")
    return render_page("pages/questions.html", "Questions & missing evidence", "A clear register of what is known at a high level, what is not established, and the document or official rule needed to resolve each question.", body, "DECISION")


def distribution_chart(width: int = 760, bar_height: int = 26) -> str:
    """Ten-year outcome distribution for the sell path, computed not asserted.

    One bar per labeled market regime from the reinvestment table; the length is
    the worse of staged versus immediate entry in that regime, so the chart shows
    dispersion instead of a single smooth-growth number.
    """
    data = outcome_distribution()
    values = [value for _, value in data]
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    label_width = 250
    plot_width = width - label_width - 110
    row_gap = bar_height + 12
    height = len(data) * row_gap + 40
    parts = [
        f'<svg class="dist-chart" viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img" '
        f'aria-label="Ten-year outcome distribution across labeled market regimes">',
        '<title>Ten-year outcome distribution across labeled market regimes</title>',
        f'<line x1="{label_width}" y1="26" x2="{label_width}" y2="{height - 30}" class="dist-axis" />',
        f'<text x="{label_width}" y="16" class="dist-scale">floor {money10(lo)}</text>',
        f'<text x="{width}" y="16" class="dist-scale dist-scale-end">ceiling {money10(hi)}</text>',
    ]
    for index, (label, value) in enumerate(data):
        y = 34 + index * row_gap
        bar_width = max(2.0, (value - lo) / span * plot_width)
        parts.append(f'<text x="0" y="{y + bar_height * 0.7:.0f}" class="dist-label">{esc(label)}</text>')
        parts.append(f'<rect x="{label_width}" y="{y}" width="{bar_width:.1f}" height="{bar_height}" rx="4" class="dist-bar" />')
        parts.append(f'<text x="{width}" y="{y + bar_height * 0.7:.0f}" class="dist-value">{money10(value)}</text>')
    parts.append('</svg>')
    return "".join(parts)


def build_projections() -> str:
    rows = [
        {"cells": ["Property A market value at transfer", "—", "Obtain a qualified valuation for the actual valuation date; a broad HPI is not a parcel appraisal.", "IRS estate valuation rules; FHFA HPI is only a broad index."], "status": "Missing", "sources": ["irs_estate", "fhfa_hpi"]},
        {"cells": ["Property A income-tax basis", "—", "Get the executor's basis statement, appraisal and improvement/depreciation records; use the correct estate valuation rule.", "Inherited basis is generally date-of-death FMV, subject to exceptions."], "status": "Missing", "sources": ["irs_basis"]},
        {"cells": ["Property A assessed value and full tax bill", "—", "Obtain current roll, base-year value, secured bill, supplemental bill and direct charges.", "Prop 13 and Proposition 19 rules do not reveal the parcel's actual charges."], "status": "Missing", "sources": ["boe_pub29", "boe_prop19"]},
        {"cells": ["Property B market value, basis and assessed value", "—", "Keep existing ownership records separate from the future trust transfer; obtain current valuation, basis and tax roll privately.", "No property-specific value or basis is established by a statewide source."], "status": "Missing", "sources": ["irs_basis", "boe_pub29"]},
        {"cells": ["Insurance premiums and coverage", "—", "Obtain separate written quotes for intended owner-occupied and landlord/mixed-use status.", "The state insurance page offers comparison tools but no household-specific premium."], "status": "Missing", "sources": ["cdi"]},
        {"cells": ["Water, electricity and solar credits", "—", "Use provider bills and the actual solar tariff/interconnection records; do not infer credits from equipment presence.", "CPUC explains tariff differences, not this account's rate or bill."], "status": "Missing", "sources": ["water_board", "cpuc_solar"]},
        {"cells": ["Rent, vacancy, repairs and maintenance", "—", "Use leases, permitted-unit records, service history, inspection findings and written bids; HUD FMR is only a benchmark.", "No official source gives the rent or repair budget for a private property."], "status": "Missing", "sources": ["hud_fmr", "irs_rental", "cslb"]},
        {"cells": ["Net sale proceeds and tax reserve", "—", "Subtract debt, transaction costs and taxes from a verified sale price; basis and the whole estate can change the result.", "A sale value is not equal to investable cash."], "status": "Missing", "sources": ["irs_basis", "irs_estate"]},
        {"cells": ["Future estate-tax headroom", "—", "Calculate from the total gross estate, adjusted taxable gifts, deductions, credits and law in the year of death.", "Current IRS thresholds do not predict a future-year amount."], "status": "Missing", "sources": ["irs_estate", "irs_2027"]},
    ]
    body = callout(
        "Rounded figures, labeled assumptions",
        "At the owner's direction the worksheet now publishes privacy-rounded figures (nearest ten dollars) and computed projections. Owner-supplied inputs are badged Owner-supplied (privacy-rounded); every forward number is badged Projection or Assumption and driven by the assumption table below. Unknown inputs — rent for Property A, insurance quotes, maintenance bids — stay blank; blank means unknown, not zero. No name, street address or parcel number is published.",
        "info",
    )
    body += make_table("Private inputs required before a year-by-year model", ["Metric", "Public value", "What to obtain privately", "What the official source establishes"], rows)
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
    proj_rows = []
    for year in range(2026, 2051):
        reassessed = a_tax_reassessed(year)
        proj_rows.append({
            "cells": [
                year,
                money10(a_value(year)),
                money10(a_assessed(year)),
                money10(a_tax_exclusion(year)),
                money10(reassessed) if reassessed is not None else "—",
                money10(b_assessed(year)),
                money10(b_tax(year)),
                money10(estate_threshold(year)),
            ],
            "status": "Assumption" if year >= INHERIT_YEAR else "Projection",
            "sources": ["owner_a", "owner_b", "boe_pub29", "ca_rtc63", "boe_lta_2025_009", "irs_estate", "cbo_ltbo"],
        })
    body += make_table(
        "Year-by-year projection, 2026-2050 (baseline assumptions; privacy-rounded)",
        ["Year", "A market value (4% scenario)", "A assessed value (2% cap)", "A annual tax — exclusion claimed", "A annual tax — reassessed at 2045", "B assessed value", "B annual tax", "Federal estate threshold (indexed assumption)"],
        proj_rows,
        "Columns 2-4 compound owner-supplied rounded figures under the baseline assumptions. Column 5 begins at the modeled 2045 transfer: market value minus the indexed exclusion, then the 2% cap. Columns 6-7 project Property B under its own cap and derived rate. Column 8 is an assumption path from the official 2026/2027 amounts, not a forecast. All values rounded to the nearest ten dollars.",
    )
    body += '<section class="table-section"><h2>Distribution of modeled outcomes, not a single path</h2>' + '<p class="table-note">The owner asked for a distribution chart here. This is one: the same priced sell-and-reinvest proceeds run through six labeled regimes, staged entry against immediate entry, and the worse of the two taken for each regime. A single smooth-growth number would hide the spread between the floor and the ceiling, which is the part that decides whether the sell path is safe.</p>' + '<figure class="dist-figure">' + distribution_chart() + '<figcaption class="dist-note">Ten-year value of the priced sell-path proceeds, worse of staged and immediate entry. Reference: net proceeds at transfer ' + money10(SELL_NET_AFTER_TRANSFER_2045) + '. Bars are scenario endpoints from the labeled assumptions on this page, not probabilities, and no bar is a forecast.</figcaption></figure>' + '</section>'
    body += make_table("Blank early / midpoint / late transfer scenarios", ["Separate asset and metric", "Early scenario", "Midpoint scenario", "Late scenario", "Private evidence required"], horizon_rows, "These are relative planning checkpoints, not public dates or a claim about when a transfer occurs. All cells are intentionally blank. Map the stages to actual years only in a private model; do not infer zero or reuse one asset's costs for the other.")
    range_rows = [
        {"cells": ["Market value growth", "One growth number per year", "Low / base / high annual growth, each dated and anchored to a published index window", "FHFA publishes broad state and metro indexes; a metro index is not an appraisal of one parcel."], "status": "Verified", "sources": ["fhfa_hpi"]},
        {"cells": ["Property tax", "Market value × one assumed rate", "Base-year value per RTC §51, the capped 2% annual inflation factor, plus the bill's non-base charges", "The 1% general levy is not a full tax rate; bonds and direct charges are additional and vary by parcel."], "status": "Verified", "sources": ["boe_pub29", "ca_rtc51", "ca_rtc218"]},
        {"cells": ["Inflation", "One constant rate for fifty years", "A sequence of regimes: an official near-term path to 2036, an official long-term path to 2055, then a stated assumption band", "CBO's longest baseline ends in 2055 and assumes current law; nothing official covers the household's actual year."], "status": "Verified", "sources": ["cbo_outlook", "cbo_ltbo", "bls_cpi"]},
        {"cells": ["Insurance", "One premium for the whole horizon", "A quoted current premium plus a renewal band with an explicit nonrenewal case", "No official source publishes a household premium; CDI explains shopping tools and the FAIR Plan's limited perils."], "status": "Missing", "sources": ["cdi"]},
        {"cells": ["Repairs and capital reserve", "One annual percentage", "An inspection-based near-term list plus a long-run sinking-fund band", "No government source sets a repair budget for a private home; bids and inspection findings are the evidence."], "status": "Missing", "sources": ["cslb", "irs_rental"]},
        {"cells": ["Rent", "One gross rent figure growing forever", "A lawful current rent, a vacancy/collection band, and the statutory cap on increases where it applies", "Civil Code §1947.12 caps increases at 5% plus the cost-of-living change or 10%, whichever is lower, with exemptions and a 2030 sunset."], "status": "Verified", "sources": ["ca_rent", "hud_fmr"]},
        {"cells": ["Treasury yields", "One yield for the whole parking period", "A first-year auction-anchored range and a lower/higher renewal band", "Each auction sets its own rate; a maturing bill must be reinvested at an unknown future rate."], "status": "Verified", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Equity returns", "One expected return and no dispersion", "Crash-during, crash-after, flat and rising cases from sourced drawdown anchors", "The SEC states stock prices can fall and investors can lose money; no official expected-return figure is asserted here."], "status": "Verified", "sources": ["sec_stocks", "fed_1929", "fed_2008"]},
    ]
    body += make_table("Round-number replacements — what to use instead", ["Input", "Round-number shortcut to retire", "Range or real-figure method", "Why the shortcut fails"], range_rows, "Every future amount in a private model should be shown as a low/base/high band, dated, and rounded to the nearest ten dollars before publication so no figure can be traced back to a source document.")
    body += paragraph("Horizon and limits", "The owner's stated transfer window is 2040-2050; the model uses the 2045 midpoint. CBO's cited outlooks run through 2036 (rates) and 2055 (inflation) and cannot be extended as house-price, insurance, rent or stock-return forecasts. The projection table is a decision aid: it shows which branch of the property-tax rule matters, not what any year will actually bring. Re-check every input with professionals at the actual transfer date.")
    return render_page("pages/projections.html", "Projection worksheet", "A transparent projection framework with intentionally blank private fields. It is not a substitute for a private, source-backed spreadsheet prepared from the actual estate and property records.", body, "NUMBERS")


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
    mech_rows = [
        {"cells": ["Taxable value each year", "RTC §51 sets taxable value as the lesser of (a) the base-year value inflated by the October-to-October California CPI change, capped at 2% per year, or (b) current full cash value.", "The enrolled value can fall below the inflated base if market value declines, which is why a flat or falling housing case is not automatically the same as a rising tax case."], "status": "Verified", "sources": ["ca_rtc51"]},
        {"cells": ["Base-year reset on transfer", "A change in ownership generally re-establishes the base-year value at current market value unless an exclusion applies.", "The transfer is the event that resets the base; the exclusion is the only thing that preserves the lower base."], "status": "Verified", "sources": ["boe_pub29", "boe_prop19"]},
        {"cells": ["Homeowners' exemption", "The exemption is $7,000 of the dwelling's full value and does not apply to rented, vacant, secondary or vacation property on the lien date.", "On a 1% general levy that is a modest reduction per year, but losing it can also signal a failed principal-residence condition elsewhere in the analysis."], "status": "Verified", "sources": ["ca_rtc218", "boe_pub29"]},
        {"cells": ["Filing dates that recur every year", "January 1 is the lien date; February 15 is the legal deadline for most timely exemption claims; April 10 and December 10 are the last days to pay the second and first secured instalments without penalty.", "A late claim can reduce a benefit even where eligibility exists, so the calendar matters as much as the rule."], "status": "Verified", "sources": ["boe_pub29"]},
        {"cells": ["Rental use and the residence condition", "The family-home exclusion requires the property to become the transferee's principal residence within one year and the transferee to file the homeowners' or disabled veterans' exemption within that year.", "A plan that rents the property out immediately may fail the residence condition, so 'rent it for a year then move in' is not automatically equivalent to moving in."], "status": "Verified", "sources": ["ca_rtc63", "ca_rtc218"]},
        {"cells": ["Value-limit test", "The exclusion applies to the transferor's principal residence subject to a value limit expressed as the current taxable value plus an adjusted amount, with the excess above the limit added to the transferred base.", "Eligibility is not all-or-nothing; a property above the limit can still receive partial relief, which changes the modelled tax materially."], "status": "Verified", "sources": ["boe_prop19", "ca_rtc63"]},
    ]
    body += make_table("Mechanics that drive a year-by-year tax projection", ["Mechanism", "What the official rule says", "Why it changes the model"], mech_rows, "No parcel's base-year value, enrolled value or bill is published. These rows describe the calculation structure only.")
    body += paragraph("Private records to request", "For each asset separately, obtain the assessor roll, full secured tax bill, supplemental assessment history, deed and trust transfer documents, homeowners' exemption status, parcel-specific direct levies, and any filed Proposition 19 claims. Do not publish a parcel number or tax bill in this public repository.")
    return render_page("pages/property-tax.html", "Property-tax rules", "California property-tax mechanics that matter for a future trust transfer, with no address, assessor record or property-specific tax history disclosed.", body, "NUMBERS")


def build_costs() -> str:
    rows = [
        {"cells": ["Property tax", "—", "Use the current roll and complete bill for each asset; include bonds and direct charges, then evaluate reassessment/exclusion rules."], "status": "Missing", "sources": ["boe_pub29", "boe_prop19"]},
        {"cells": ["Owner-occupied insurance", "—", "Request a current homeowners quote, replacement-cost basis, liability and named exclusions; no official price can be derived from location-free data."], "status": "Missing", "sources": ["cdi"]},
        {"cells": ["Landlord / mixed-use insurance", "—", "Request an underwriting review for actual legal units, occupancy, leases, vacancy and fire/earthquake/liability coverage."], "status": "Missing", "sources": ["cdi"]},
        {"cells": ["Water / wastewater", "—", "Use the actual provider bill, meter, account and current tariff. The statewide drinking-water program does not state a household rate."], "status": "Missing", "sources": ["water_board"]},
        {"cells": ["Electricity / solar credits", "—", "Use the actual bill and interconnection/tariff documents. NEM and NBT credit rules differ; export credits under NBT are usually below retail."], "status": "Missing", "sources": ["cpuc_solar"]},
        {"cells": ["Rent / vacancy / collections", "—", "Use lawful leases and rent ledger; HUD FMR is an annual program benchmark, not the market rent or lawful rent for a particular unit."], "status": "Missing", "sources": ["hud_fmr", "ca_rent", "irs_rental"]},
        {"cells": ["Repairs / capital maintenance", "—", "Get inspection reports and itemized bids from appropriately licensed contractors; no universal government repair budget exists."], "status": "Missing", "sources": ["cslb", "irs_rental"]},
        {"cells": ["Rental income tax / deductions", "—", "Ask a CPA to classify personal versus rental use, allowable expenses, depreciation, sale basis and reporting year."], "status": "Missing", "sources": ["irs_rental", "irs_1041"]},
    ]
    body = callout(
        "Owner-supplied costs are published privacy-rounded; quotes are still required",
        "Owner-supplied monthly figures appear on the property-profiles page, rounded to the nearest ten dollars and badged Owner-supplied (privacy-rounded). No official source can produce an insurance premium or repair bid for a private home, so those cells stay unverified until written quotes and bids exist. Provider context: the Cupertino-area water utility publishes its own tariffs, and third-party compilations of CPUC data put the mid-2026 PG&E residential average near 33.7 cents per kWh.",
        "info",
    )
    owner_cost_rows = [
        {"cells": ["Property A water", f"${PROPERTY_A['water_month'][0]} to ${PROPERTY_A['water_month'][1]} per month", "Owner-supplied (privacy-rounded)", "Provider tariff page is the official reference; bill varies with usage."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_a", "sjw_rates"]},
        {"cells": ["Property A electricity / solar", f"net credit about ${PROPERTY_A['solar_credit_month'][0]} to ${PROPERTY_A['solar_credit_month'][1]} per month", "Owner-supplied (privacy-rounded)", "Legacy NEM vs net-billing tariffs pay export credits very differently; confirm from the account."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_a", "cpuc_solar"]},
        {"cells": ["Property A insurance", f"owner estimate about {money10(PROPERTY_A['insurance_owner_estimate'])} per year — unverified", "Owner-supplied (privacy-rounded)", "California's 2025-26 market is stressed; the FAIR Plan's dwelling rates rose about 29% on average in late 2026 (third-party reported). Obtain written quotes."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_a", "cdi", "cdi_news"]},
        {"cells": ["Property B rent", f"about {money10(PROPERTY_B['rent_month'])} per month from two rented units", "Owner-supplied (privacy-rounded)", "Covered-unit increases capped at 1.6% (March 2026 - February 2027); confirm unit coverage and the vacant unit's status."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "sf_rent_board"]},
        {"cells": ["Property B water / electricity", f"water ${PROPERTY_B['water_month'][0]} to ${PROPERTY_B['water_month'][1]}; electricity ${PROPERTY_B['electric_month'][0]} to ${PROPERTY_B['electric_month'][1]} per month, building total", "Owner-supplied (privacy-rounded)", "Combined-building figures; metering configuration governs future allocation."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "sfpuc_water", "pge_tariffs"]},
        {"cells": ["Property B insurance", f"owner estimate about {money10(PROPERTY_B['insurance_owner_estimate'])} per year — unverified", "Owner-supplied (privacy-rounded)", "A landlord/dwelling-fire form differs from an owner-occupied policy; underwriting is per property."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "cdi"]},
    ]
    body += make_table("Owner-supplied operating figures (privacy-rounded) and their official verification path", ["Line", "Owner-supplied value", "Evidence status", "Official verification path"], owner_cost_rows, "These are the owner's own figures rounded to the nearest ten dollars; they are inputs, not verified facts. Each row links the official record that can confirm it.")
    body += make_table("Operating-cost inputs and evidence needed", ["Cost / income line", "Public amount", "How to verify privately"], rows)
    cost_range_rows = [
        {"cells": ["Property tax", "Structure: RTC §51 lesser-of test, 2% cap, plus non-base bill charges", "Model a qualifying and a non-qualifying exclusion case for each asset separately, using the actual roll as the starting point.", "A single 'about 1% of value' line is wrong for an inherited parcel in both directions."], "status": "Verified", "sources": ["ca_rtc51", "boe_pub29", "ca_rtc63"]},
        {"cells": ["Home insurance", "Range method: one written owner-occupied quote and one landlord quote, with a renewal band and a nonrenewal case", "Request quotes for each intended use and a replacement-cost worksheet; list exclusions and any DIC need.", "Premiums are underwritten per property; no public table produces a household premium."], "status": "Missing", "sources": ["cdi"]},
        {"cells": ["Water and wastewater", "Range method: twelve months of actual bills, seasonally split", "Collect the provider bill history for the service address; keep it in the private file.", "The statewide drinking-water program publishes oversight information, not a household tariff."], "status": "Missing", "sources": ["water_board"]},
        {"cells": ["Electricity and solar credits", "Range method: actual bills plus the signed tariff and interconnection documents", "Identify whether the account is on a legacy NEM tariff or the net billing tariff, and note the true-up month.", "Export credits under net billing are usually below retail, and equipment presence alone does not prove a credit."], "status": "Verified", "sources": ["cpuc_solar"]},
        {"cells": ["Repairs and capital reserve", "Range method: inspection findings plus itemised licensed bids plus an annual sinking fund", "Commission an inspection and obtain at least two bids per item; separate repairs from improvements.", "Repairs and improvements are treated differently for tax, and neither is published by a government source."], "status": "Missing", "sources": ["cslb", "irs_rental"]},
        {"cells": ["Rent and vacancy", "Range method: lawful current rent, a vacancy and collection band, and the statutory increase cap", "Use the lease ledger and the local rules; test whether the unit is covered by the statewide cap or exempt.", "Rent caps do not set the market rent, and a covered unit's increases are constrained."], "status": "Verified", "sources": ["ca_rent", "hud_fmr"]},
        {"cells": ["Income tax on rental or sale", "Range method: basis-driven gain, allowable expenses, depreciation and the main-home exclusion tests", "Have the CPA prepare the basis schedule and test the two-out-of-five-year rule where a sale is contemplated.", "Inherited basis is generally date-of-death value, and the main-home exclusion requires ownership and use tests."], "status": "Verified", "sources": ["irs_basis", "irs_121", "irs_rental"]},
    ]
    body += make_table("From assumptions to ranges: how each cost line should be built", ["Cost line", "Range method", "Evidence to collect", "Why it matters"], cost_range_rows, "Every value in a private model should be a dated low/base/high band. Nothing in the public site states a household amount.")
    body += cards("Coverage and use checks", [
        ("Insurance gap", "The state explains that the FAIR Plan has limited covered perils; compare standard coverage and any DIC policy rather than treating a FAIR Plan policy as complete coverage.", "pages/sources.html"),
        ("Solar tariff", "Determine interconnection date, NEM/NBT tariff, true-up rules and export-credit treatment from the account records.", "pages/sources.html"),
        ("Rental use", "Confirm permitted units, local rent restrictions, deposits and lease terms before applying projected gross rent.", "pages/questions.html"),
    ], current="pages/operating-costs.html")
    return render_page("pages/operating-costs.html", "Costs, insurance and utility evidence", "A source-linked checklist for the carrying costs that must be modeled without exposing or guessing any property-specific amount.", body, "NUMBERS")


def build_black_swan() -> str:
    rows = [
        {"cells": ["1929–1954 equity collapse and recovery", "Federal Reserve History reports the Dow fell 89% from peak to trough and did not regain its previous high until November 1954.", "Long drawdowns and delayed nominal recovery are possible. The Dow is a price index, not an after-dividend diversified portfolio."], "status": "Historical", "sources": ["fed_1929"]},
        {"cells": ["2007–2009 Great Recession", "Federal Reserve History reports an approximately 57% S&P 500 peak-to-trough decline and about a 30% average U.S. home-price decline from prior peaks.", "Equity and housing risk can overlap in a broad crisis; national averages do not predict a specific property."], "status": "Historical", "sources": ["fed_2008"]},
        {"cells": ["Inflation shock", "BLS reports CPI rose 9.1% in the 12 months through June 2022, the largest 12-month increase since November 1981.", "A single high-inflation year can erode purchasing power and raise replacement/repair costs; it is not an annual forecast."], "status": "Historical", "sources": ["bls_cpi"]},
        {"cells": ["Near-term interest-rate baseline and stress", "CBO's 2026–2036 outlook gives a 4.3% average 10-year Treasury rate, with 4.8% and 5.8% higher-rate scenarios.", "Useful only as a near-term macro anchor; not a 50-year bond yield, mortgage rate, housing-growth rate or portfolio return."], "status": "Verified", "sources": ["cbo_rates"]},
        {"cells": ["Long-run housing variation", "FHFA publishes state and metro house-price indexes over different windows.", "An index is not an address-level forecast. Do not apply a metro return mechanically to a private parcel."], "status": "Verified", "sources": ["fhfa_hpi"]},
    ]
    regimes = [
        {"cells": ["Inflation surge / purchasing-power loss", "CPI rose 9.1% over the year through June 2022; this is a single observed 12-month window.", "Stress one or more years at a user-selected inflation rate, but do not repeat 9.1% for decades as if it were a forecast. Higher replacement and repair costs can compress real cash flow."], "status": "Historical", "sources": ["bls_cpi", "cslb"]},
        {"cells": ["Equity drawdown during staging", "The 1929 Dow and 2007–09 S&P 500 episodes supply two severe historical drawdown endpoints.", "The tool tests a synthetic crash starting halfway through staging. It does not replay either index's daily path or include dividends."], "status": "Historical", "sources": ["fed_1929", "fed_2008"]},
        {"cells": ["Equity drawdown after staging", "The same source-reported drawdown can begin after all scheduled purchases are complete.", "Compare with the early-crash case; phasing no longer preserves as much uninvested Treasury cash when the loss starts."], "status": "Historical", "sources": ["fed_1929", "fed_2008", "treasury_bills"]},
        {"cells": ["Lower short-rate renewals", "Each Treasury auction sets the rate for the new security; future renewal rates are not known today.", "Enter a lower second-year yield than first-year yield to expose reinvestment risk. This is a what-if, not a rate prediction."], "status": "Assumption", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Rising market before a crash", "No official source in this workspace establishes future equity returns or their sequence.", "Enter a positive pre-crash drift to test opportunity cost while staging; this is a scenario assumption, not an expected-return estimate."], "status": "Assumption", "sources": ["sec_stocks"]},
        {"cells": ["Higher nominal rate regime", "CBO's near-term 2026–2036 outlook uses 4.3% average 10-year Treasury rates and 4.8%/5.8% higher-rate scenarios.", "Use only as a short-horizon macro reference; do not substitute these rates for far-future Treasury yields, mortgage costs or portfolio returns."], "status": "Verified", "sources": ["cbo_rates"]},
        {"cells": ["Housing slump / flat property market", "Fed History reports about a 30% average U.S. home-price decline from mid-2006 to mid-2009; FHFA provides broad regional indexes.", "Use a separate low-growth/flat/decline housing scenario. National and regional indexes are not a parcel forecast."], "status": "Historical", "sources": ["fed_2008", "fhfa_hpi"]},
        {"cells": ["Insurance availability / repair shock", "No public source establishes a future premium, local underwriting decision or repair bill for either asset.", "Treat coverage loss, deductible changes and large repairs as explicit blank or quote-based stress inputs; do not insert a generic percentage."], "status": "Missing", "sources": ["cdi", "cslb"]},
    ]
    body = callout("A single constant growth rate is not a 50-year economic model", "Inflation, interest rates, housing prices, insurance availability, rents and equity returns move in different regimes. The available official outlook cited here is at most a near-term baseline; no official source supplies the future household-specific path.", "warning")
    body += '''<section class="phased-path" aria-labelledby="phased-path-heading">
<h2 id="phased-path-heading">Phased-investing path: Treasury staging before equity entry</h2>
<p class="table-note">Sale proceeds can be parked in short Treasuries across the 3-month bill to 2-year note band for 24–36 months after inheritance, then phased into stocks. This tests whether staging softens crash entry risk: a 1929-style equity collapse (Dow about 89 percent peak to trough, prior high not regained until November 1954) or a 2007–09-style collapse (S&amp;P 500 about 57 percent peak to trough) beginning while money is still staged leaves part of the proceeds in Treasuries; the same collapse beginning after staging ends exposes the full amount. The local-only tool on the Treasury staging page compares crash-during-staging with crash-after-staging and runs lower Treasury renewal-yield cases.</p>
<p class="table-note"><strong>Reinvestment risk beside the headline.</strong> Each maturing bill or note must be reinvested at the next auction's rate, which may be lower. Staging changes when equity risk begins; it does not remove reinvestment risk, sequence risk, or the possibility of stock losses.</p>
<p class="no-print"><a href="../pages/phased-investing.html">Run the Treasury staging and phased stock entry comparison</a></p>
</section>'''
    market_rows = [
        {"cells": ["3-month Treasury bill — November 2026", "about 4.3% (Treasury par yield curve)", "Context for the staging band's first-year rung; each future auction resets the rate."], "status": "Cross-checked", "sources": ["treasury_curve"]},
        {"cells": ["2-year Treasury note — November 2026", "about 4.9% (Treasury par yield curve)", "Context for holding the staging band at the 2-year point; a note sold before maturity can trade below par."], "status": "Cross-checked", "sources": ["treasury_curve"]},
        {"cells": ["10-year Treasury — CBO 2026-2036 baseline", "4.3% average over the projection window (4.8% and 5.8% higher-rate scenarios)", "Near-term macro anchor for the staging table on the Treasury staging page; not a long-run promise."], "status": "Verified", "sources": ["cbo_rates"]},
        {"cells": ["Long-run inflation baseline", "CBO's extended baseline keeps inflation near the Federal Reserve's 2% goal through 2055", "Used as the 2% assumption behind the estate-threshold indexing path; a regime like the Great Inflation would break it."], "status": "Verified", "sources": ["cbo_ltbo", "fed_great_inflation"]},
    ]
    body += make_table("Market context for the staging band (November 2026)", ["Anchor", "Level", "Status and use"], market_rows, "The yield levels are cross-checked against aggregations of the official Treasury curve, not retrieved directly in this session; confirm the current curve before any real decision.")
    body += make_table("Measured historical anchors — not forecasts", ["Episode / source window", "Officially reported observation", "How to use it"], rows)
    body += make_table("Economic regime stress map", ["Regime", "Evidence or status", "What to test"], regimes, "Historical episodes are observations, not probabilities. Assumption rows are user-controlled stress paths, not predictions. Property-specific costs remain blank until quoted.")
    regime_rows = [
        {"cells": ["1929–1941 — deflationary collapse", "Federal Reserve History dates the Depression from August 1929, with banking panics from 1930 to 1933 and a double-dip recession in 1937–38; the Dow remained 89% below its 1929 peak at the 1932 low and did not regain that peak until November 1954.", "Prices and asset values can fall for years, not months. A nominal Treasury reserve protects principal only while its purchasing power and the institution holding it remain sound.", "Model a multi-year flat or falling housing market together with a multi-year equity trough; do not assume a V-shaped recovery inside the staging window."], "status": "Historical", "sources": ["fed_great_depression", "fed_1929"]},
        {"cells": ["1965–1982 — Great Inflation", "Federal Reserve History reports inflation a little above 1% in 1964, more than 14% in 1980, and about 3.5% average in the later 1980s.", "A long high-inflation regime raises insurance, repair, utility and replacement costs unevenly and squeezes real cash flow from fixed-rate assets such as bills and notes.", "Run the carrying-cost projection with inflation above the market-value growth rate for several consecutive years, not one bad year."], "status": "Historical", "sources": ["fed_great_inflation"]},
        {"cells": ["2007–2009 — asset-price and housing shock", "Federal Reserve History reports an approximately 57% S&P 500 peak-to-trough decline and roughly a 30% average U.S. home-price decline from mid-2006 to mid-2009.", "Equity and housing risk can arrive together, which weakens a plan that assumes selling the house later will fund a market recovery.", "Combine a housing decline with an equity decline in the same year and keep a separate liquidity reserve outside both assets."], "status": "Historical", "sources": ["fed_2008"]},
        {"cells": ["2022 — inflation re-acceleration", "BLS reports CPI up 9.1% over the twelve months to June 2022, the largest twelve-month rise since late 1981.", "A single-year shock is real but says nothing about the next decade; short-term Treasury yields and asset prices can move sharply in response.", "Stress one or two high-inflation years inside an otherwise moderate path; do not extrapolate the shock across fifty years."], "status": "Historical", "sources": ["bls_cpi"]},
        {"cells": ["2026–2036 — official near-term baseline", "CBO projects PCE inflation returning to about 2% by 2030, a 4.3% average 10-year Treasury rate, and 4.8%/5.8% higher-rate scenarios over 2026–2036.", "This is the only horizon for which an official near-term baseline exists in this workspace; it does not reach the expected transfer window.", "Use it as a starting anchor and label every assumption beyond 2036 as a scenario, not a forecast."], "status": "Verified", "sources": ["cbo_rates", "cbo_outlook"]},
        {"cells": ["2025–2055 — official long-term baseline", "CBO's 30-year extended baseline has inflation near 2% after 2027 and a 10-year Treasury rate close to its 30-year average, with debt reaching 156% of GDP in 2055.", "Even the longest official baseline stops in 2055 and assumes current law is unchanged; it contains no house-price, insurance, rent or portfolio return path.", "Extend the horizon only with explicit low/base/high scenarios and a dated note that no official forecast exists for the household's actual year."], "status": "Verified", "sources": ["cbo_ltbo"]},
        {"cells": ["Insurance and repair availability shock", "No official source publishes a future premium, nonrenewal decision or repair bill for an individual property; CDI explains the FAIR Plan's limited perils and the possible need for a Difference in Conditions policy.", "A coverage gap or a large repair can dominate every investment-return difference in this comparison.", "Treat coverage loss and a major repair as explicit stress inputs and keep a documented reserve and a fallback insurer plan."], "status": "Missing", "sources": ["cdi", "cslb"]},
        {"cells": ["Property-tax reassessment shock", "RTC §63.2 makes the intergenerational exclusion conditional on relationship, residence, occupancy and a filed claim; without it, the base-year value is re-established at the transfer.", "A failed or late claim can multiply the annual property tax for as long as the property is held and shrink any rent or sale advantage.", "Model a no-exclusion case beside the qualifying case; the difference is the single largest property-tax lever in this decision."], "status": "Verified", "sources": ["ca_rtc63", "boe_prop19"]},
    ]
    body += make_table("Regime map — real historical figures and official baselines", ["Regime", "Sourced observation", "What it does to this decision", "How to test it"], regime_rows, "Historical rows are observations, not probabilities. Baseline rows are official projections that stop at 2036 or 2055. No row supplies a household-specific price, premium or return.")
    body += paragraph("Stress dimensions to combine", "Test equity declines before, during and after Treasury staging; lower renewal yields; high inflation; stagnant housing prices; property-tax reassessment; insurance nonrenewal or coverage gaps; repair spikes; vacancy and rent limits; and liquidity needs. Treat joint shocks as stress cases, not independent probabilities. The comparison tool models entry timing plus user-entered yields, pre-crash drift and inflation; it does not claim to replay the whole economy.")
    miss_rows = [
        {"cells": ["Executed trust, all amendments and any restatement", "Attorney / trustee", "Decides who may occupy, rent, sell or distribute; nothing downstream is valid without it.", "At transfer, before any occupancy decision"], "status": "Missing", "sources": ["ca_prob160617"]},
        {"cells": ["Trustee notification and the trust's internal accounting", "Trustee / attorney", "Confirms the 60-day trustee-notification clock and the beneficiary information rights that start it.", "Within 60 days of the triggering event"], "status": "Missing", "sources": ["ca_prob160617"]},
        {"cells": ["Certified date-of-death appraisal and the executor's basis statement", "Appraiser / CPA / executor", "Sets income-tax basis; a later sale above basis is taxable, and consistent-basis reporting can apply.", "Before any sale or rental conversion"], "status": "Missing", "sources": ["irs_basis", "irs_basis_pub"]},
        {"cells": ["Full estate inventory, prior taxable gifts, deductions and portability facts", "CPA / estate attorney", "Determines whether Form 706 is required and whether a DTI filing is needed even below the threshold.", "Within nine months of death, or by the extension date"], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["County change-in-ownership filing and the assessor's written determination", "Trustee / transferee / assessor", "Starts the reassessment question and the penalty exposure for a missed statement.", "Within 150 days of death"], "status": "Missing", "sources": ["ca_rtc480", "boe_prop19"]},
        {"cells": ["Proposition 19 exclusion claim and homeowners' exemption filing", "Assessor / property-tax adviser", "The single largest property-tax lever: a qualifying claim preserves a lower base; a missed one reassesses at current value.", "Homeowners' exemption within 1 year; exclusion claim within 3 years or before a third-party transfer"], "status": "Missing", "sources": ["ca_rtc63", "ca_rtc218", "boe_prop19"]},
        {"cells": ["Current secured tax bill with every direct and bond charge", "Assessor / county tax collector", "Shows the real levy, which is more than the 1% general levy plus the capped assessed-value growth.", "Before modelling any annual carrying cost"], "status": "Missing", "sources": ["boe_pub29", "ca_rtc51"]},
        {"cells": ["Permits, certificates of occupancy and the current lease ledger", "Building department / landlord-tenant counsel", "Establishes lawful unit count, lawful rent and the tenant obligations a mixed plan must respect.", "Before assuming any rent or occupancy change"], "status": "Missing", "sources": ["ca_rent", "irs_rental"]},
        {"cells": ["Written insurance quotes for each intended use", "Licensed broker", "Owner-occupied and landlord policies differ in underwriting, exclusions and replacement-cost basis; a nonrenewal can reverse a cash-flow result.", "Before occupancy, rental or sale is executed"], "status": "Missing", "sources": ["cdi"]},
        {"cells": ["Inspection report and licensed repair bids", "Licensed contractor / inspector", "Turns a vague maintenance percentage into a dated, itemised near-term liability.", "Before choosing to hold the asset"], "status": "Missing", "sources": ["cslb"]},
        {"cells": ["Utility bills and the signed solar interconnection and tariff documents", "Utility / solar provider", "Determines whether an export credit exists and which tariff (NEM or NBT) applies to the account.", "Before any net-cash-flow projection"], "status": "Missing", "sources": ["water_board", "cpuc_solar"]},
        {"cells": ["Sale-side closing estimate, debt payoff and transfer-charge schedule", "Escrow / CPA / attorney", "Gross value is not investable cash; fees, payoff and tax all reduce what can be reinvested.", "Before comparing a sale against a hold"], "status": "Missing", "sources": ["irs_basis", "irs_basis_pub"]},
    ]
    body += make_table("Missing-information register — collect these before any decision", ["Record to obtain", "Who can supply it", "Why it changes the answer", "Deadline or trigger"], miss_rows, "This list is the answer to \"what do we not have\". Each row is intentionally blank in the public site because the underlying document is private and identifiable.")
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
    body += paragraph("Staging band used in the comparison", "The tool models a 3-month Treasury bill through a 2-year Treasury note band (3M–2Y) held for 24–36 months, followed by scheduled equity purchases. TreasuryDirect states that bill rates are fixed at auction for terms of 4–52 weeks and that a 2-year note is available among note maturities; interest is federally taxable and exempt from state and local taxes. Which specific securities and maturities suit the estate is an adviser decision, not an output of this tool.")
    body += '''<section class="tool-section" aria-labelledby="tool-heading">
<h2 id="tool-heading">Crash-entry what-if — normalized units, not dollars</h2>
<p class="table-note">The starting portfolio is normalized to 100 index units so no household amount is embedded. Historical drawdown endpoints are sourced, but the path between peak and trough is synthetic and linear. Controls model a rising pre-crash market, separate first-year and renewal Treasury yields, and inflation-adjusted purchasing power. Enter the Treasury yield net of estimated taxes and fees; the tool does not calculate taxes. This is not a historical total-return replay and sends or stores no calculator inputs.</p>
<form id="phase-tool" class="tool-grid">
<label>Historical drawdown anchor<select id="phase-event"><option value="1929">1929 Dow episode</option><option value="2008" selected>2007–09 S&amp;P episode</option></select></label>
<label>Purchase staging period<select id="phase-months"><option value="24">24 months</option><option value="30" selected>30 months</option><option value="36">36 months</option></select></label>
<label>Peak-to-trough decline (%)<input id="phase-drawdown" type="number" min="0" max="99" step="1" value="57" inputmode="decimal"></label>
<label>Peak-to-trough duration (months)<input id="phase-trough" type="number" min="1" max="120" step="1" value="17" inputmode="numeric"></label>
<label>Pre-crash equity drift (%/year)<input id="phase-drift" type="number" min="-20" max="30" step="0.1" value="0" inputmode="decimal"></label>
<label>Net Treasury yield, months 1–12 (%)<input id="phase-yield1" type="number" min="-5" max="20" step="0.1" value="0" inputmode="decimal"></label>
<label>Net renewal yield, month 13 onward (%)<input id="phase-yield2" type="number" min="-5" max="20" step="0.1" value="0" inputmode="decimal"></label>
<label>Annual inflation for purchasing-power lens (%)<input id="phase-inflation" type="number" min="-5" max="20" step="0.1" value="0" inputmode="decimal"></label>
<div class="tool-actions no-print"><button id="phase-reset" type="button">Reset assumptions</button><span class="tool-assumption">0% rates are neutral isolation settings, not Treasury quotes or forecasts.</span></div>
</form>
<div class="scenario-grid" aria-live="polite">
<article class="scenario-card"><h3>Crash begins during the staging window</h3><p>Crash starts halfway through staging; results are shown at the later of investment completion or the modeled trough.</p><dl><dt>Observation horizon</dt><dd id="early-months">—</dd><dt>Immediate investment — nominal</dt><dd id="early-immediate-value">—</dd><dt>Phased investment — nominal</dt><dd id="early-phased-value">—</dd><dt>Immediate investment — real units</dt><dd id="early-immediate-real">—</dd><dt>Phased investment — real units</dt><dd id="early-phased-real">—</dd><dt>Maximum drawdown — immediate</dt><dd id="early-immediate-dd">—</dd><dt>Maximum drawdown — phased</dt><dd id="early-phased-dd">—</dd></dl></article>
<article class="scenario-card"><h3>Crash begins after staging completes</h3><p>All scheduled purchases are complete before the same decline begins.</p><dl><dt>Observation horizon</dt><dd id="late-months">—</dd><dt>Immediate investment — nominal</dt><dd id="late-immediate-value">—</dd><dt>Phased investment — nominal</dt><dd id="late-phased-value">—</dd><dt>Immediate investment — real units</dt><dd id="late-immediate-real">—</dd><dt>Phased investment — real units</dt><dd id="late-phased-real">—</dd><dt>Maximum drawdown — immediate</dt><dd id="late-immediate-dd">—</dd><dt>Maximum drawdown — phased</dt><dd id="late-phased-dd">—</dd></dl></article>
</div>
<p id="phase-status" class="tool-status" role="status">Change a control to run the local-only comparison.</p>
<p class="table-note">Model boundary: equal monthly equity purchases from the initial 100 units; Treasury reserve accrues the entered yield by month and uses the renewal yield after month 12; the final purchase includes any accrued reserve. Equity grows at the entered drift until the crash, declines linearly to the selected drawdown, then stays flat at its trough. Real units divide by the selected constant annual inflation factor. There are no dividends, fees, taxes, post-trough recovery, withdrawals, property costs or probabilities. The zero-rate and zero-inflation defaults isolate timing only; they are not forecasts.</p>
</section>'''
    body += """<section class="tool-section" aria-labelledby="ladder-heading">
<h2 id="ladder-heading">Ladder reinvestment risk — what maturing rungs cost you</h2>
<p class="table-note">A 24–36 month parking plan is a ladder: several short Treasury rungs mature at different times and each one is reinvested at whatever auction rate exists then. This panel isolates that effect. It runs the same crash and the same staging schedule twice — once with every renewal at the first-year yield, once with the later rungs repriced lower — and reports the reserve interest earned before any equity outcome is applied. Starting capital is normalized to 100 units; yields are entered net of estimated federal tax, state tax is not applicable to Treasury interest, and fees are not modeled.</p>
<form id="ladder-tool" class="tool-grid">
<label>Staging period<select id="ladder-months"><option value="24">24 months</option><option value="30" selected>30 months</option><option value="36">36 months</option></select></label>
<label>Crash depth applied to purchases (%)<input id="ladder-drawdown" type="number" min="0" max="99" step="1" value="57" inputmode="decimal"></label>
<label>Crash duration (months)<input id="ladder-trough" type="number" min="1" max="120" step="1" value="17" inputmode="numeric"></label>
<label>Pre-crash equity drift (%/year)<input id="ladder-drift" type="number" min="-20" max="30" step="0.1" value="0" inputmode="decimal"></label>
<label>First-year net yield (%)<input id="ladder-yield1" type="number" min="-5" max="20" step="0.1" value="4.0" inputmode="decimal"></label>
<label>Renewal yield — rung 2 (%)<input id="ladder-renewal1" type="number" min="-5" max="20" step="0.1" value="3.0" inputmode="decimal"></label>
<label>Renewal yield — rung 3 (%)<input id="ladder-renewal2" type="number" min="-5" max="20" step="0.1" value="2.5" inputmode="decimal"></label>
<label>Renewal yield — rung 4 (%)<input id="ladder-renewal3" type="number" min="-5" max="20" step="0.1" value="2.0" inputmode="decimal"></label>
<label>Inflation for purchasing-power lens (%)<input id="ladder-inflation" type="number" min="-5" max="20" step="0.1" value="2.5" inputmode="decimal"></label>
<div class="tool-actions no-print"><button id="ladder-reset" type="button">Reset ladder assumptions</button><span class="tool-assumption">Default yields are illustrative round settings, not a Treasury quote. Read the current auction results before relying on any yield.</span></div>
</form>
<div class="scenario-grid" aria-live="polite">
<article class="scenario-card"><h3>Constant yields (no reinvestment penalty)</h3><p>Every renewal earns the first-year yield, isolating the crash-timing effect alone.</p><dl><dt>Reserve interest earned during staging</dt><dd id="ladder-flat-interest">—</dd><dt>Interest lost versus constant-yield run</dt><dd id="ladder-flat-year">—</dd><dt>Ending value — nominal</dt><dd id="ladder-flat-value">—</dd><dt>Ending value — real units</dt><dd id="ladder-flat-real">—</dd></dl></article>
<article class="scenario-card"><h3>Falling renewal yields (reinvestment risk)</h3><p>Later rungs renew at lower rates, as happens after a policy easing cycle.</p><dl><dt>Reserve interest earned during staging</dt><dd id="ladder-falling-interest">—</dd><dt>Interest lost versus constant-yield run</dt><dd id="ladder-falling-year">—</dd><dt>Ending value — nominal</dt><dd id="ladder-falling-value">—</dd><dt>Ending value — real units</dt><dd id="ladder-falling-real">—</dd></dl></article>
</div>
<p id="ladder-status" class="tool-status" role="status">Change a control to run the local-only ladder comparison.</p>
<p class="table-note">Model boundary: the reserve is divided into four term slots; each month's accrual uses the yield assigned to that slot, with months 1–12 forced to the first-year yield. Four equal equity purchases are made across the staging period at the modeled index level, and any leftover reserve is invested at the end. No dividends, fees, taxes, withdrawals, probability weights or post-trough recovery are modeled. The panel reports reserve interest separately so a lower renewal yield is never hidden inside a single headline number.</p>
</section>"""
    static_rows = staging_rows()
    body += make_table(
        "Staging compared in dollars — modeled net proceeds of about " + money10(SELL_NET_AFTER_TRANSFER_2045) + " after the assumed sale cost, the published county transfer tax and the recording fees (baseline assumptions)",
        ["Entry scenario", "Lump sum (invest all at receipt)", "24-month staging", "36-month staging"],
        static_rows,
        "Proceeds assume a 2045 sale at the 4% market-growth scenario minus 7% assumed costs. Reserve yield 4.3% per year (CBO 2026-2036 10-year average as the bill/note proxy); crash variants begin in month 15 with the source-calibrated declines and run to their troughs (36-month horizon, except the 1929 variant runs 51 months). No dividends, fees, taxes, post-trough recovery or probabilities. This is a stress illustration, not a backtest or advice — the interactive tool above runs the same model in normalized units with your own inputs.",
    )
    rows = [
        {"cells": ["1929 anchor", "Federal Reserve History reports an 89% Dow peak-to-trough decline; the previous high was not regained until November 1954.", "The calculator starts from the Dow drawdown only; it does not copy daily prices or include dividends."], "status": "Historical", "sources": ["fed_1929"]},
        {"cells": ["2008 anchor", "Federal Reserve History reports a 57% S&P 500 peak-to-trough decline from October 2007 to March 2009.", "The calculator uses this as a source-calibrated shock magnitude, not a forecast or a return series."], "status": "Historical", "sources": ["fed_2008"]},
        {"cells": ["Reinvestment risk", "The next Treasury auction rate is not known when today's bill matures; Treasury product pages state the rate is fixed at auction.", "Run a lower renewal-yield case as well as the zero-yield isolation case."], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Inflation / real-value lens", "BLS reports 9.1% CPI inflation over the year through June 2022; that was one observed year, not a long-run rate.", "Enter an explicit inflation stress and compare nominal units with purchasing-power units; do not repeat a single historical shock as a forecast."], "status": "Historical", "sources": ["bls_cpi"]},
        {"cells": ["Equity risk", "The SEC warns stock prices can fall and stock investors can lose money.", "No expected return, probability, tax rate or personal allocation is inferred by this page."], "status": "Verified", "sources": ["sec_stocks"]},
    ]
    body += make_table("How to read the calculator", ["Point", "Source-backed fact", "Limit / next test"], rows)
    body += paragraph("Interpretation", "A staged plan can buy more shares during an early falling market because later installments purchase at lower index values. If the same decline starts after staging ends, all proceeds are already exposed. A positive pre-crash drift control tests one rising-market opportunity-cost scenario, but it is a constant synthetic rate rather than a historical return series. Use actual after-tax yields and an adviser-approved investment policy before making a real allocation.")
    return render_page("pages/phased-investing.html", "Treasury staging and phased stock entry", "A source-calibrated, assumption-led stress comparison for 24–36 month Treasury parking followed by gradual equity purchases. It is not an individualized investment recommendation.", body, "STRESS TESTS")


def build_estate_thresholds() -> str:
    rows = [
        {"cells": ["Federal basic exclusion — 2026 deaths", "$15,000,000", "Filing threshold is tested against gross estate plus adjusted taxable gifts and specific gift-tax exemption; other filing triggers can apply."], "status": "Verified", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["Federal basic exclusion — 2027 deaths", "$15,480,000", "The IRS announced this amount for 2027. It is the next-year threshold, not a future-year projection."], "status": "Verified", "sources": ["irs_2027"]},
        {"cells": ["Annual gift exclusion — 2026", "$19,000 per donor/recipient", "A gift-tax annual exclusion is separate from the lifetime estate/gift basic exclusion and is not an inheritance allowance."], "status": "Verified", "sources": ["irs_2027"]},
        {"cells": ["Annual gift exclusion — 2027", "$20,000 per donor/recipient", "The annual exclusion does not cap an inheritance and does not determine estate tax by itself."], "status": "Verified", "sources": ["irs_2027"]},
        {"cells": ["California state/local death-transfer tax", "Current RTC §13301 bars a state or political subdivision tax on a transfer by reason of death; the Controller says no CA Estate Tax return is required for deaths on/after 2005-01-01.", "Current law only; no future exemption or tax amount can be forecast for a later death."], "status": "Verified", "sources": ["ca_rtc13301", "ca_death_tax"]},
        {"cells": ["Household estate headroom", "—", "No gross-estate inventory, adjusted taxable gifts, specific gift-tax exemption, debts, deductions, spouse/portability facts or valuation date is published; the remaining headroom cannot be calculated."], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq"]},
    ]
    body = callout("The threshold is not per heir", "Federal estate tax is an estate-level transfer tax. The IRS filing test uses the decedent's gross estate, adjusted taxable gifts and specific gift-tax exemption; a portability election can require a return below the threshold. A recipient's share alone cannot establish whether a return is required or tax is due.", "info")
    body += make_table("Current official thresholds and missing household calculation", ["Rule / year", "Official value or rule", "What it means here"], rows)
    estate_proj_rows = [
        {"cells": ["2026 (current law)", money10(estate_threshold(2026)), "Official IRS amount; up to $30,000,000 for a married couple with a timely portability election or credit-shelter plan."], "status": "Verified", "sources": ["irs_estate", "irs_2027", "obbba_law"]},
        {"cells": ["2027 (current law)", money10(estate_threshold(2027)), "Official IRS announcement; the first OBBBA-indexed year."], "status": "Verified", "sources": ["irs_2027", "obbba_law"]},
        {"cells": ["2030", money10(estate_threshold(2030)), "Assumption: official 2027 amount compounded at 2% per year (CBO long-run inflation path). Actual adjustments use chained CPI under IRC §2010(c) and future law."], "status": "Assumption", "sources": ["irc_2010c", "cbo_ltbo"]},
        {"cells": ["2035", money10(estate_threshold(2035)), "Same assumption path."], "status": "Assumption", "sources": ["irc_2010c", "cbo_ltbo"]},
        {"cells": ["2040 (early window)", money10(estate_threshold(2040)), "Same assumption path; early edge of the owner's stated 2040-2050 window."], "status": "Assumption", "sources": ["irc_2010c", "cbo_ltbo", "owner_a"]},
        {"cells": ["2045 (midpoint)", money10(estate_threshold(2045)), "Same assumption path; the modeled transfer year used across this site."], "status": "Assumption", "sources": ["irc_2010c", "cbo_ltbo", "owner_a"]},
        {"cells": ["2050 (late window)", money10(estate_threshold(2050)), "Same assumption path; late edge of the owner's stated window."], "status": "Assumption", "sources": ["irc_2010c", "cbo_ltbo", "owner_a"]},
    ]
    body += make_table(
        "Federal basic exclusion amount — official amounts and assumption path to the transfer window",
        ["Year of death", "Basic exclusion amount", "Status and limits"],
        estate_proj_rows,
        "These are estate-level amounts, not per-beneficiary allowances. The two dollar values marked official are IRS figures; the 2030-2050 values are labeled assumptions, not projections of future law. Congress can change the exclusion at any time; OBBBA made the current $15,000,000 level permanent from 2026 with annual inflation adjustments.",
    )
    body += paragraph("Annex: the comparison premises", "A threshold comparison is only usable if five things are stated on the same line: level (estate-wide, not one asset), direction (a tax or an exclusion), unit (per estate, per person, per heir), year of death, and baseline (current law only). Anything else is a headline, not a calculation.")
    body += paragraph("Future law and the household calculation", "The transfer is decades away. The 2030-2050 rows above are an assumption path, not a forecast: Congress can change the exclusion, and the actual chained-CPI adjustments will differ. For the household number, the CPA combines the gross estate (Property A, Property B, cash and other assets), adjusted taxable gifts, deductions and any portability facts in the year of death. California imposes no state estate or inheritance tax under current law (RTC §13301). Annual gifts use the separate annual exclusion: $19,000 per donor/recipient in 2026 and $20,000 in 2027.")
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
    body = callout("Start clocks only from their legal trigger", "These deadlines are not interchangeable. A trust-notice clock, county property-tax filing, federal estate return and Proposition 19 claims can have different triggers and responsible filers. Counsel should confirm the actual dates from the death and transfer records.", "warning")
    body += make_table("Inheritance and decision timeline", ["Trigger / deadline", "Verified rule", "Responsible party to confirm", "Evidence to retain"], rows)
    timeline = [
        ("Day of death", "The trust's irrevocable trigger and the date every later clock measures from.", "Trustee / counsel", "Death certificate, trust instrument, prior amendments"),
        ("By day 60", "Trustee notification to beneficiaries and heirs, if the statutory trigger applies.", "Trustee / attorney", "Copy of the notification and proof of service"),
        ("By day 150", "Change-in-ownership statement for property transferred by reason of death, including through a trust.", "Trustee / transferee", "Filed statement and county acknowledgement"),
        ("By month 9", "Form 706 due if the estate meets the filing test; an extension of up to six months can be requested by the due date.", "Executor / CPA", "Return, extension request, valuation reports"),
        ("By month 12", "Qualifying transferee establishes principal residence and files the homeowners' or disabled veterans' exemption for a family-home exclusion.", "Transferee / assessor", "Exemption filing, occupancy evidence"),
        ("By month 36", "Intergenerational exclusion claim window closes, or earlier if the property is transferred to a third party.", "Transferee / assessor", "Claim form and assessor determination"),
        ("Every year by February 15", "Timely exemption-claim deadline published by the BOE for most exemptions, with a reduced benefit for later homeowners' filings.", "Owner / assessor", "Filed claim receipt"),
        ("Every year on the lien date", "January 1 valuation date for the property-tax roll; the annual assessment and any decline-in-value review attach here.", "Assessor / property-tax adviser", "Roll value and notice"),
        ("Each April 10 and December 10", "Last day to pay the second and first secured-tax instalments without a penalty.", "Owner / tax collector", "Payment receipts"),
        ("Annually, from now until transfer", "Re-check enacted federal and California law, the assessor record, insurance availability, leases and market inputs.", "Attorney / CPA / adviser", "Dated review note in the private file"),
    ]
    tiles = "".join(
        f'<li class="timeline-item"><span class="timeline-when">{esc(when)}</span>'
        f'<span class="timeline-what">{esc(what)}</span>'
        f'<span class="timeline-who">Who: {esc(who)}</span>'
        f'<span class="timeline-evidence">Keep: {esc(evidence)}</span></li>'
        for when, what, who, evidence in timeline
    )
    body += f'<section class="prose timeline-section"><h2>Deadline timeline</h2><p class="table-note">Relative deadlines only. No personal date is published. The clock on each row starts from a different legal trigger, so they are not interchangeable.</p><ol class="timeline">{tiles}</ol></section>'
    body += paragraph("No dates have been assigned", "The public page does not publish a personal transfer date. Once counsel confirms the date of death, date title changes, trust status and occupancy plan, replace these relative deadlines with calendar dates in a private checklist.")
    return render_page("pages/inheritance-process.html", "Inheritance process and deadline timeline", "A relative step-by-step sequence for a trust-based transfer, with official clocks distinguished from operational checkpoints.", body, "LAW & PROCESS")


def build_law_watchlist() -> str:
    rows = [
        {"cells": ["Federal estate and gift amounts", "Use only official year-of-death IRS thresholds and annual gift tables; current 2026/2027 amounts do not determine later law.", "Check enacted federal law and the IRS annual adjustment/revenue procedure near the transfer."], "status": "Guidance", "sources": ["irs_estate", "irs_2027"]},
        {"cells": ["Federal proposal — S.4196", "Congress.gov lists the bill as introduced and referred to Senate Finance as of 2026-11-15. The draft would set a $3,500,000 basic exclusion and revise estate, gift and generation-skipping transfer tax rules; its text proposes applying to deaths and gifts after December 31, 2026 if enacted.", "This could materially change the estate-level calculation, but it is not enacted and must not replace the current IRS baseline."], "status": "Proposal—not law", "sources": ["congress_s4196_status", "congress_s4196_text", "irs_estate"]},
        {"cells": ["Federal proposal — H.R.601", "As checked 2026-11-15, Congress.gov lists H.R. 601 as introduced and referred to House Ways and Means and Budget. The draft proposes a 20% rate for estate, gift and generation-skipping transfer taxes, with a proposed effective date for transfers after December 31, 2024 if enacted.", "Not enacted. Re-check Congress.gov before using any tax rate or assuming the draft's proposed effective date would apply."], "status": "Proposal—not law", "sources": ["congress_hr601_status", "congress_hr601_text"]},
        {"cells": ["Federal proposal — S.587", "As checked 2026-11-15, Congress.gov lists S. 587 as introduced and referred to Senate Finance. The draft proposes repealing federal estate and generation-skipping transfer taxes and separately changing gift-tax rules.", "Not enacted. This proposal is distinct from current federal estate and gift tax law; confirm status and enacted text before relying on it."], "status": "Proposal—not law", "sources": ["congress_s587_status", "congress_s587_text"]},
        {"cells": ["Federal estate/gift exclusion — OBBBA made it permanent", "Public Law 119-21 (July 4, 2025) sets the basic exclusion at $15,000,000 for 2026 with annual inflation adjustments thereafter; the 2027 amount is $15,480,000. Projections to the 2040-2050 window on this site are labeled assumptions, not forecasts.", "Re-check the enacted statute, the IRS annual revenue procedure and any new legislation in the year of death."], "status": "Verified", "sources": ["obbba_law", "irs_2027", "irc_2010c"]},
        {"cells": ["Proposition 19 exclusion amount indexing", "The BOE adjusts the $1,000,000-base exclusion amount every two years using the FHFA California House Price Index: $1,022,600 (2023-2025), then $1,044,586 (February 16, 2025 - February 15, 2027). The next adjustment is due February 16, 2027.", "Check the BOE's next published amount before the transfer; the site's 3% indexing is an assumption."], "status": "Verified", "sources": ["boe_lta_2025_009", "boe_prop19"]},
        {"cells": ["California insurance market", "The Sustainable Insurance Strategy (2025) allows catastrophe modeling and reinsurance costs in rate filings, with carrier commitments to write policies; the FAIR Plan's dwelling rates rose about 29% on average in late 2026 (third-party reported).", "Re-quote insurance annually; treat availability and price as stressed inputs."], "status": "Cross-checked", "sources": ["cdi_news", "cdi"]},
        {"cells": ["Treasury yields for any staging plan", "November 2026 context: 3-month about 4.3%, 2-year about 4.9%; CBO's 2026-2036 baseline averages 4.3% on the 10-year.", "Each auction resets the rate; reprice the ladder immediately before any real staging decision."], "status": "Cross-checked", "sources": ["treasury_curve", "cbo_rates"]},
        {"cells": ["Federal bills and proposals", "No specific pending federal proposal is incorporated into this decision framework. A bill or resolution is not current law merely because it is introduced or debated.", "Search Congress.gov near the event; confirm enactment, effective date and IRS implementation before changing a calculation."], "status": "Not verified", "sources": ["congress_legislation", "irs_estate"]},
        {"cells": ["California property-tax transfer rules", "Review RTC §§480 and 63.2, BOE guidance, any later amendments and the assessor's written determination.", "Check filing forms, value limit, occupancy, relationship and transfer date."], "status": "Guidance", "sources": ["ca_rtc480", "ca_rtc63", "boe_prop19"]},
        {"cells": ["California SB 974 — limited Proposition 19 amendment", "Chaptered as Chapter 665, Statutes of 2026; official status page marks it non-urgency. It amends RTC §63.2 to recognize a Probate Code §3604 special-needs trust as an eligible transfer medium for the specified exclusion; relationship, residence, occupancy, value and claim conditions remain. Separate claim-timing relief applies only to qualifying property connected with specified 2025 wildfires.", "Counsel should verify the operative date, exact trust qualification, remaining eligibility and current assessor guidance. This is not a general rule for all family transfers or ordinary trusts."], "status": "Chaptered", "sources": ["ca_sb974_status", "ca_sb974_text", "ca_rtc63"]},
        {"cells": ["California death-transfer tax", "Current RTC §13301 and State Controller information describe the current rule; do not assume it cannot change.", "Re-check state law for the actual year of death."], "status": "Guidance", "sources": ["ca_rtc13301", "ca_death_tax"]},
        {"cells": ["Rent and tenant protections", "Statewide Civil Code rules have coverage conditions and exemptions; local rules may be more restrictive. The property's jurisdiction is intentionally not published, so a local ordinance cannot be identified here.", "Counsel should check the actual city/county code, rent registry, unit status, lease and tenant rights before occupancy or a rent change."], "status": "Missing", "sources": ["ca_rent", "ca_legislation"]},
        {"cells": ["Insurance availability and coverage", "Market conditions, underwriting, wildfire/flood risk, exclusions and reconstruction costs may change independently of taxes.", "Refresh written quotes and coverage terms; do not extrapolate an old premium."], "status": "Missing", "sources": ["cdi"]},
        {"cells": ["Investment yields and market entry", "Treasury rates are fixed at each auction for the selected security; stock prices can lose value.", "Reprice the ladder and compare reinvestment and sequence risk immediately before investment."], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
        {"cells": ["Long-run economic assumptions", "CBO's cited interest-rate horizon is 2026–2036; no cited official source provides an individual 50-year house value, insurance price, rent or return forecast.", "Use several clearly labeled stress paths; never promote a scenario into a forecast."], "status": "Guidance", "sources": ["cbo_rates", "fhfa_hpi", "bls_cpi"]},
        {"cells": ["Nov 3, 2026 tax-related statewide measures (Props 3, 40–43)", "The official titles are: 3 — extends the existing tax on high incomes for schools and health care; 40 — imposes a one-time tax on certain taxpayers; 41 — prohibits new state taxes that exclude revenue from the state spending limit and requires audits of new state special taxes; 42 — prohibits new state personal property taxes and certain retroactive state taxes; 43 — limits voters' ability to raise local government revenue. The election date (Nov 3, 2026) is before today's date (Nov 15, 2026); certified results were not read here.", "Read the certified results and each measure's full text and fiscal analysis before relying on any tax effect; a ballot title is not a legal outcome by itself."], "status": "Not verified", "sources": ["sos_ballot"]},
        {"cells": ["SF rent-control allowable increase", "The Rent Board page states a 1.6% allowable annual increase for covered units from March 1, 2026 through February 28, 2027. Secondary articles that cite a different figure are superseded by this official page.", "Re-check the Rent Board page each year; confirm whether a unit is covered before applying any increase."], "status": "Verified", "sources": ["sf_rent_board"]},
        {"cells": ["SF Rent Board 2026 notices (demolition/major renovation protections; security-deposit interest)", "The Rent Board page lists a January 23, 2026 item on tenant protections for demolition and major renovation, and a security-deposit interest change effective March 1, 2026. Their substance was not extracted into this site.", "Counsel should read the linked notice text and confirm whether it applies to the specific units before any tenant or deposit decision."], "status": "Not verified", "sources": ["sf_rent_board"]},
    ]
    body = callout("Watch enacted law, not headlines", "The pages distinguish current statutes and agency tables from bills, stress assumptions and future uncertainty. No bill or proposal is represented as current law. The inherited transfer is far in the future; refresh federal, state and actual local rules near the event.", "info")
    body += make_table("Law and market watchlist", ["Topic", "Current official baseline / proposal status", "What to re-check"], rows)
    body += paragraph("No future-year legal projection", "This site intentionally does not extrapolate federal thresholds or California property-tax allowances to a future year. S.4196, H.R.601 and S.587 are introduced proposals only; SB 974 is a chaptered state amendment with limited scope, and its operative date must be confirmed before application. None predicts the law at a future transfer. Search official bill systems and verify enacted text, effective dates, local code and agency implementation near the event.")
    return render_page("pages/law-watchlist.html", "Law and market watchlist", "A short list of rules and market inputs that can change the decision, without treating a proposed change or long-run projection as settled fact.", body, "LAW & PROCESS")


def build_brief() -> str:
    rows = [
        {"cells": ["Trustee / attorney", "Confirm trust/deed authority, title, debts, occupancy/sale rights and notice clocks.", "Executed trust/amendments, deed, loan, notices and leases."], "status": "Action needed", "sources": ["ca_prob160617", "ca_rtc480"]},
        {"cells": ["Estate CPA / appraiser", "Review whole-estate Form 706/portability. Confirm Asset A's date-of-death basis and exceptions; analyze Asset B's existing basis, rent/depreciation and tax separately.", "Private estate/prior-gift records; separate A/B deeds and tax/basis files; valuation and rent records."], "status": "Action needed", "sources": ["irs_estate", "irs_estate_faq", "irs_basis", "irs_rental"]},
        {"cells": ["Property-tax / housing counsel", "Test A's conditional family-home exclusion and deadlines. Verify B's residence role, legal units, leases and local tenant rules.", "Relationship/residence/occupancy evidence, assessments, claims, permits, leases and local code."], "status": "Action needed", "sources": ["boe_prop19", "ca_rtc63", "ca_rent"]},
        {"cells": ["Insurer / contractor / utility", "Price separate owner-occupied and landlord coverage; identify exclusions, urgent repairs, actual utility and solar tariff costs.", "Use-specific written quotes, inspections/bids, actual bills and signed interconnection/tariff documents."], "status": "Action needed", "sources": ["cdi", "cslb", "water_board", "cpuc_solar"]},
        {"cells": ["Investment adviser / CPA", "Compare conditional live, rent, sell and mixed paths; calculate after-tax proceeds/reserves and stress 24–36-month Treasury staging, lower renewal yields and a crash after staging.", "Private sale estimates/costs, reserve, current yields, fees and risk policy."], "status": "Action needed", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
    ]
    body = callout("Meeting objective", "Obtain a written conditional recommendation, assumptions, sources, deadlines, reserves and facts that could reverse it.", "info")
    body += make_table(
        "One-page adviser handoff checklist",
        ["Adviser", "Question to resolve", "Private records to bring"],
        rows,
        source_labels={
            "ca_prob160617": "Probate Code §16061.7",
            "ca_rtc480": "RTC §480",
            "irs_estate": "IRS estate tax",
            "irs_estate_faq": "IRS estate FAQ",
            "irs_basis": "IRS basis FAQ",
            "irs_rental": "IRS rental property",
            "boe_prop19": "BOE Proposition 19",
            "ca_rtc63": "RTC §63.2",
            "ca_rent": "CA tenant law",
            "cdi": "CA insurance department",
            "cslb": "CA contractor board",
            "water_board": "CA water program",
            "cpuc_solar": "CPUC NEM/NBT",
            "treasury_bills": "Treasury bills",
            "treasury_notes": "Treasury notes",
            "sec_stocks": "SEC stocks guide",
        },
    )
    body += paragraph("Asset boundary", "Asset A is an anticipated trust transfer; Asset B is already owned and may have rent or an occupancy role. Keep each asset's title, basis, assessment, income and costs separate; choose no path until records are verified.")
    body += paragraph("Privacy", "This brief contains no address, locality, valuation, rent, utility amount, premium or parcel identifier. Store completed notes outside the public repository.")
    return render_page("pages/attorney-cpa-brief.html", "Attorney & CPA briefing sheet", "One-page, print-ready meeting checklist. No identifying details or household-specific amounts are included.", body, "ADVISER HANDOFF")


def build_decision_log() -> str:
    rows = [
        ("D01", "Structure the site around decisions, not topics",
         "Lead with the one question (live, rent, sell, or a mix) and the facts that would change the answer; keep background material behind it.",
         "A reader can act on the first screen instead of reading eighteen pages to reach the same conclusion.",
         [("Decision quality", "High"), ("Effort", "Medium"), ("Privacy impact", "None")],
         ["github_history"]),
        ("D02", "Show low/base/high bands, never a single round number",
         "Every future amount is a range with a stated source and date. Ranges are the honest form for a transfer that may be a decade or more away.",
         "A point estimate implies precision the evidence does not support and hides the decision-flipping cases.",
         [("Decision quality", "High"), ("Effort", "Medium"), ("Privacy impact", "None")],
         ["fhfa_hpi", "cbo_ltbo"]),
        ("D03", "Keep the two ownership roles permanently separate",
         "One asset is anticipated through a trust; the other is already owned with its own basis, leases and assessment. No combined 'total value' line.",
         "Combining them silently imports one asset's tax basis and costs into the other's economics.",
         [("Decision quality", "High"), ("Effort", "Low"), ("Privacy impact", "None")],
         ["irs_basis", "boe_pub29"]),
        ("D04", "Put reinvestment risk on the same line as the staging headline",
         "Every 'park the proceeds for 24–36 months' statement carries the renewal-yield penalty and the rising-market cost beside it.",
         "Staging changes the timing of risk; presenting only the favourable crash case is misleading.",
         [("Decision quality", "High"), ("Effort", "Medium"), ("Privacy impact", "None")],
         ["treasury_bills", "treasury_notes"]),
        ("D05", "Model mixed paths before pure ones",
         "Occupying one lawful unit while renting another, retaining the already-owned asset, or selling only one asset are first-class options.",
         "The real choice is rarely all-or-nothing; forcing three pure options produces a false ranking.",
         [("Decision quality", "High"), ("Effort", "Medium"), ("Privacy impact", "None")],
         ["irs_rental", "ca_rent"]),
        ("D06", "Treat the property-tax claim as the largest single lever",
         "Model the qualifying and non-qualifying assessment cases side by side and put both filing deadlines on the timeline.",
         "A missed claim can multiply the annual tax for the whole holding period, which dwarfs investment-return differences.",
         [("Decision quality", "High"), ("Effort", "Low"), ("Privacy impact", "None")],
         ["ca_rtc63", "boe_prop19"]),
        ("D07", "Publish rounded figures only, per the owner's 2026-11-15 direction (policy revised)",
         "Originally this log said 'no household figure at any rounding'. The owner then directed: figures should be used but rounded to the nearest ten dollars and reported in the decision analysis. The site now publishes $10-rounded owner-supplied figures with an Owner-supplied (privacy-rounded) badge, keeps names, street addresses and parcel identifiers forbidden, and rounds every derived number the same way (verifier-enforced).",
         "The owner's rounding instruction is the recorded trade-off: rounded figures support the decision without matching a searchable record. Revisit only with a new written owner direction.",
         [("Privacy", "Critical"), ("Effort", "Medium"), ("Privacy impact", "Owner-directed")],
         ["github_history", "boe_pub29", "owner_a"]),
        ("D08", "Make every table row prove its own sourcing",
         "Each row carries an evidence badge and at least one official link, and the build fails when either is missing.",
         "A row without a source is an opinion that will be mistaken for a finding.",
         [("Decision quality", "High"), ("Effort", "Low"), ("Privacy impact", "None")],
         ["github_history"]),
        ("D09", "Separate current law from proposals and scenarios",
         "Current statutes and agency tables sit in their own rows; bills, stress cases and assumptions are labelled as such.",
         "A proposal promoted to a baseline quietly rewrites the answer without anyone deciding to.",
         [("Decision quality", "High"), ("Effort", "Medium"), ("Privacy impact", "None")],
         ["congress_legislation", "ca_legislation"]),
        ("D10", "Give the attorney and CPA a one-page handoff",
         "A printable sheet listing the question, the private records to bring and the deadline for each adviser.",
         "The binding constraints are legal and tax facts; the meeting is where they get resolved.",
         [("Decision quality", "High"), ("Effort", "Medium"), ("Privacy impact", "None")],
         ["irs_estate_faq", "ca_prob160617"]),
        ("D11", "Show the deadlines as a timeline, not a list",
         "Each clock starts from a different trigger; the timeline names the trigger, the deadline, the responsible party and the record to keep.",
         "Readers conflate the 60-day trustee notice, the 150-day ownership statement and the 9-month return.",
         [("Decision quality", "Medium"), ("Effort", "Low"), ("Privacy impact", "None")],
         ["ca_prob160617", "ca_rtc480", "irs_estate_faq", "boe_prop19"]),
        ("D12", "Record review choices in the browser only",
         "A local-only review queue records which suggestions are selected, deferred or to be investigated; nothing is transmitted.",
         "It makes the improvement process auditable without creating a new data-collection channel.",
         [("Privacy", "High"), ("Effort", "Low"), ("Privacy impact", "Protective")],
         ["github_history"]),
    ]
    body = callout("A review queue, not an automatic change", "Each suggestion below records the decision quality it improves, the effort, and its privacy impact. Choosing an option changes nothing on the site and sends nothing anywhere; it only records your own review state in this browser. Implement a change only after the relevant owner has reviewed it and the necessary private records exist.", "info")
    body += '<p class="review-summary" id="review-summary" role="status" aria-live="polite">Loading review queue…</p><p class="no-print"><button id="reset-reviews" type="button">Reset review choices</button></p>'
    table_rows = []
    for ident, title, action, why, meta, sources in rows:
        meta_html = " · ".join(f"{esc(label)}: {esc(value)}" for label, value in meta)
        select = SafeHTML(
            f'<select class="review-choice" data-id="{esc(ident)}" aria-label="Review decision for {esc(ident)}">'
            '<option value="Not reviewed">Not reviewed</option>'
            '<option value="Investigate">Investigate</option>'
            '<option value="Selected">Selected for testing</option>'
            '<option value="Defer">Defer</option></select>'
        )
        table_rows.append({
            "cells": [SafeHTML(f"<strong>{esc(ident)}</strong> {esc(title)}"), action, why, meta_html, select],
            "status": "Guidance",
            "sources": sources,
        })
    body += make_table("Choose a path before implementing anything", ["Suggestion", "What it would change", "Why it improves the decision", "Quality · effort · privacy", "Review choice"], table_rows, "Two review queues are published: this decision-quality log and the site suggestions page. Review both, select what to test, and only then implement.")
    body += paragraph("Suggested approval gates", "Do not implement a change until the owner has reviewed it, the private records that the change depends on exist, a professional has confirmed the applicable law for the actual year, and the result can be reproduced from the stated assumptions. Nothing here is applied automatically.")
    return render_page("pages/decision-log.html", "Decision log and review queue", "Twelve suggestions for improving decision quality, each with its effort, privacy impact and a local-only review choice. Nothing is applied automatically.", body, "DECISION")


def build_flagged() -> str:
    rows = [
        {"cells": ["F-01 — Public Git history exposure", "GitHub reports this repository is public. The active site is generic, but reachable historical commits and PR material may retain earlier case-derived details. This task did not rewrite remote main history or claim a complete purge.", "Treat historic material as exposed. Repository-owner/admin coordination, access review, clean archive and any history rewrite/support request remain required."], "status": "Missing", "sources": ["github_history"]},
        {"cells": ["F-02 — No case-specific projection", "Private base values, assessments, tax bills, basis, leases and costs are intentionally absent from the public build.", "No year-by-year dollar forecast or best-path ranking can be responsibly published without private records and explicit assumptions."], "status": "Missing", "sources": ["irs_basis", "boe_pub29", "cdi", "irs_rental"]},
        {"cells": ["F-03 — Premiums and repairs", "No official public page provides an insurance quote or repair estimate for an individual home.", "Request property-specific insurer quotes, coverage forms, inspections and itemized licensed bids."], "status": "Missing", "sources": ["cdi", "cslb"]},
        {"cells": ["F-04 — Water and solar costs", "The state water program is not a household tariff; the CPUC page describes NEM/NBT but not an individual account's net bill.", "Use private bills and signed service/solar documents. No credit or monthly cost is filled in."], "status": "Missing", "sources": ["water_board", "cpuc_solar"]},
        {"cells": ["F-05 — Rental legality and local rules", "No unit permit, local rent-board determination, lease or tenant notice is public here.", "Confirm lawful unit count and all applicable state/local rules with counsel before projecting rent or occupancy."], "status": "Missing", "sources": ["ca_rent", "hud_fmr"]},
        {"cells": ["F-06 — Future law and market path", "The verified CBO forecast runs through 2036; the public site does not disclose a transfer date or model a household-specific future path.", "No future exclusion, house-price, CPI, rent, insurance or portfolio-return value is invented."], "status": "Missing", "sources": ["cbo_rates", "irs_2027", "fhfa_hpi"]},
        {"cells": ["F-07 — Failed official retrievals", "Direct page fetches returned 404 for the listed FTB inheritance page, BOE county-assessor directory, BOE Publication 801 PDF and CPUC water-utilities URL.", "No claim or property-specific value is based on those failed URLs; working alternative laws and guidance are linked in the source register."], "status": "Not verified", "sources": ["ftb_404", "boe_assessor_404", "boe_pub801_404", "cpuc_water_404"]},
        {"cells": ["F-09 — SF vacancy-tax path", "The SF Treasurer page on vacancy/empty-homes tax returned 'Page Not Found' on 2026-11-15, so no current SF vacancy-tax rule or filing duty is verified here.", "Find the current official SF Treasurer or Tax Collector page for any vacancy tax; do not apply one until confirmed."], "status": "Not verified", "sources": ["sf_treasurer_vacancy_404"]},
        {"cells": ["F-10 — Santa Clara property-tax rate", "The Santa Clara Assessor homepage fetch failed and the reachable Assessor page lists contacts and services only. No county levy rate or direct charge is verified for any Santa Clara parcel.", "Obtain the parcel's own secured tax bill and the official county rate schedule before any tax projection."], "status": "Missing", "sources": ["scc_assessor_fetch"]},
        {"cells": ["F-11 — HUD Fair Market Rent values", "The FY2026 HUD FMR page returned 404, and the FY2027 documentation page did not yield extractable local values. No FMR figure is published.", "Retrieve the official HUD FMR table for the specific area and year; FMR is a program benchmark, not a lawful rent."], "status": "Missing", "sources": ["hud_fmr"]},
        {"cells": ["F-12 — Japan asset-bubble figures", "Historical discount-rate and Nikkei/land-price figures come from secondary sources that disagree on details. The official Bank of Japan source was not confirmed.", "Read the official Bank of Japan data or statements before any historical Japan figure is used; none is published here."], "status": "Not verified", "sources": ["boj_unverified"]},
        {"cells": ["F-13 — California income-tax brackets", "The FTB page for brackets and rates was not fetched, so California income-tax bracket figures are not verified here. Secondary sites were not used for published values.", "Read the current FTB rate schedule for the tax year, and any additional tax that applies, before any California income-tax projection."], "status": "Not verified", "sources": ["ftb_404"]},
        {"cells": ["F-14 — SF rent-control coverage cutoff", "Secondary coverage cites a pre-June 13, 1979 coverage cutoff; the sf.gov ordinance text confirming it was not read.", "Counsel should read the ordinance text and the Rent Board's coverage rules before relying on any unit's covered status."], "status": "Not verified", "sources": ["sf_rent_board"]},
        {"cells": ["F-15 — Nov 3, 2026 measure outcomes", "The Nov 3, 2026 election is before today's date. The qualified list was read, but certified results and full measure text were not read.", "Read the certified results and each voter guide before treating any of Props 3 or 40–43 as settled law."], "status": "Not verified", "sources": ["sos_ballot"]},
        {"cells": ["F-08 — Stress-tool simplification", "The calculator uses source-reported peak-to-trough endpoints with a synthetic straight-line decline and flat trough.", "It includes only the entered Treasury yields, pre-crash drift and constant inflation lens; it excludes dividends, fees, taxes, post-trough recovery, withdrawals, property costs, correlations and probabilities. It is not a historical backtest."], "status": "Assumption", "sources": ["fed_1929", "fed_2008", "treasury_bills", "bls_cpi"]},
   
        {"cells": ["F-20 — Owner-supplied figures are not independently verifiable", "Every row badged Owner-supplied (privacy-rounded) carries the owner's own figures rounded to the nearest ten dollars. This session could not and did not verify them against assessor, utility, insurer or lease records.", "Verify each against the linked official record (county assessor roll, provider account, written quotes) before relying on it. No value was inferred to fill a gap."], "status": "Not verified", "sources": ["owner_a", "owner_b"]},
        {"cells": ["F-21 — Rounded-figures policy change (owner-directed, 2026-11-15)", "Earlier sessions published no household figures at any rounding. The owner's latest written instruction directs that rounded figures be reported in the decision analysis. The change is recorded in the decision log (D07) and enforced by the verifier (all published currency amounts end in 0; names, street addresses and parcel identifiers stay banned; region ZIPs allowed for insurance/utility context).", "Review D07 and the privacy page. If the owner prefers the stricter posture, revert by removing the owner-supplied tables — no structural change needed."], "status": "Guidance", "sources": ["owner_a", "owner_b"]},
        {"cells": ["F-22 — FAIR Plan dwelling rate increase (market-stress context)", "Third-party reporting (multiple outlets, August-October 2026) says the Department of Insurance approved an average 29.1% FAIR Plan dwelling rate increase effective October 15, 2026; the official CDI newsroom page was not retrieved directly in this session.", "Treat California insurance costs as a stressed input: obtain quotes, and budget for renewal increases. Confirm the rate approval at the CDI newsroom link."], "status": "Not verified", "sources": ["cdi_news", "cdi"]},
        {"cells": ["F-23 — Public Git history: pattern audit reconfirmed", "A read-only audit of the full reachable history (256 commits) found privacy-sensitive figure and place-identifier patterns recurring across hundreds of commit/path pairs (for example, one exact assessment figure appears along 13 unique historical paths; the two region ZIPs along more than 70 each). Counts only; no values were printed and no determination was made that every match is personal data. History remains unscrubbed.", "Repository-owner/admin coordinated cleanup is still required. A ready-to-run procedure exists in the tree (tools/history_scrub.sh + tools/history_scrub_runbook.md: private archive first, filter-repo/BFG rewrite of all refs, force-push coordination, GitHub Support for cached and PR copies) but requires owner/admin action. The platform pins this session to one branch, so no rewrite or force-push was performed."], "status": "Not verified", "sources": ["github_history"]},
    ]
    body = callout("Privacy issue remains urgent", "The current website avoids case-specific figures and locations. The GitHub repository is public, and history cleanup has not been completed. A noindex tag and a cleaned current tree do not erase old commits, PR diffs, forks, caches or clones.", "warning")
    body += make_table("Flagged for review — unresolved items do not imply a verified answer", ["Flag", "What is unresolved", "Required action"], rows)
    scan_rows = [
        {"cells": ["F-16 — Case-derived place identifiers remain in Git history", "A read-only scan of `git rev-list --all --objects` (251 commits, 1,384 unique blobs, 380 distinct paths) found CA-ZIP-shaped five-digit patterns in 95 paths, a property city name in 109 paths, a neighbourhood name in 96 paths and one specific five-digit place identifier in 55 paths. Affected paths include `README.md`, `VERIFICATION.md`, `COORDINATION.md`, `_7adb71fc/**`, `_7eff7e24/**`, `_c07ccf45/**`, `_s95cf9249/**`, `_s9ad1da71/**` and `_research/notes.jsonl`. No matched value is reproduced here.", "Path names and match counts were checked; the values themselves are not republished. A history rewrite, repository visibility change or GitHub Support coordination requires repository-owner/admin action and cannot be safely performed from a session-scoped token on a shared default branch. Treat the historical material as exposed until that is completed."], "status": "Missing", "sources": ["github_history"]},
        {"cells": ["F-17 — Rounding is applied, not a substitute for de-identification", "The public site publishes no household amount. A prior revision of the working notes circulated rounded figures; rounding to the nearest ten dollars does not anonymise an assessment history that can be matched to a parcel across years.", "Any future publication of an amount requires rounding to the nearest ten dollars and a separate check that the value cannot be re-identified from public records."], "status": "Guidance", "sources": ["github_history", "boe_pub29"]},
        {"cells": ["F-18 — Official pages that no longer resolve", "Four previously cited URLs return 404 or redirect to an error page as of this check: the FTB gifts-and-inheritances page, the BOE county-assessor directory, the BOE Publication 801 PDF and the CPUC water-utilities page.", "None of these is used to support a rule or a number. Working alternatives are linked in their place, and the failures stay listed so they are not silently dropped."], "status": "Not verified", "sources": ["ftb_404", "boe_assessor_404", "boe_pub801_404", "cpuc_water_404"]},
        {"cells": ["F-19 — No official source covers the household's actual transfer year", "The longest official baseline cited stops in 2055 and assumes current law; the near-term baseline stops in 2036. No official source supplies a house-price, insurance, rent or portfolio return path for the household's actual year.", "Every projection beyond the published baseline is a labelled scenario with a stated assumption band, not a forecast."], "status": "Missing", "sources": ["cbo_outlook", "cbo_ltbo", "fhfa_hpi"]},
    ]
    body += make_table("Additional flagged items from this review", ["Flag", "What was found", "Required action"], scan_rows)
    body += paragraph("History-remediation limitation", "GitHub's guidance describes history rewriting as a coordinated, disruptive operation and warns that other refs, pull requests, forks, cached views and clones may retain copies. This platform pins the session to one feature branch and prohibits pushing another branch; therefore this work does not force-push or claim to scrub main. The repository owner/admin should review visibility and coordinate a supported, all-ref cleanup if desired.")
    return render_page("pages/flagged-for-review.html", "Flagged for review", "Material uncertainties, failed official retrievals, and the unresolved privacy/history issue. No unverified value has been substituted.", body, "EVIDENCE")


def build_glossary() -> str:
    rows = [
        {"cells": ["Tax structure: Property and interests included in the federal estate-tax calculation before allowable deductions; includes more than one house.", "Do not compare one inheritor's share alone with the federal filing threshold."], "status": "Verified", "sources": ["irs_estate"]},
        {"cells": ["Tax structure: Federal estate/gift tax amount available under current law for a given year, subject to the statute and prior taxable transfers.", "It is not the annual gift exclusion and not a guarantee about a later year."], "status": "Verified", "sources": ["irs_estate", "irs_2027"]},
        {"cells": ["Tax structure: A tax-accounting amount used to compute gain or loss on sale; inherited property basis is generally date-of-death fair market value, subject to exceptions.", "Keep separate from the county's property-tax assessed value."], "status": "Verified", "sources": ["irs_basis"]},
        {"cells": ["Property tax: Value used in the property-tax system; California rules can constrain growth and change the base on a change in ownership, with specified exclusions.", "Not the same as current market value, sale price or income-tax basis."], "status": "Verified", "sources": ["boe_pub29", "boe_prop19"]},
        {"cells": ["Property tax: A conditional intergenerational property-tax rule with relationship, residence, occupancy and claim requirements.", "Trust title alone does not prove qualification."], "status": "Verified", "sources": ["ca_rtc63", "boe_prop19"]},
        {"cells": ["Decision structure: A combination such as occupying one lawful unit, renting another, retaining an already-owned property, or selling one asset and staging the proceeds.", "Model each asset, unit and tax position separately."], "status": "Guidance", "sources": ["irs_rental", "ca_rent"]},
        {"cells": ["Decision structure: The effect of when returns occur; an early decline can matter more than the same decline later when funds are being invested or withdrawn.", "Stress both crash-during-staging and crash-after-staging cases; neither is a probability forecast."], "status": "Guidance", "sources": ["fed_1929", "fed_2008", "sec_stocks"]},
        {"cells": ["Decision structure: The possibility that proceeds from a maturing investment must be reinvested at a lower yield.", "A short Treasury ladder can defer equity exposure but does not lock a future renewal yield."], "status": "Verified", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Fair Market Rent (FMR)", "HUD's annual 40th-percentile gross-rent benchmark used for specified housing programs.", "It is not a property appraisal, a lease amount or a determination of legal rent."], "status": "Verified", "sources": ["hud_fmr"]},
        {"cells": ["Factored base year value", "The property's long-held taxable value under Proposition 13, grown by up to 2% per year; the starting point for any exclusion math at transfer.", "Owner-supplied history on this site is rounded to the nearest ten dollars; the assessor's roll is authoritative."], "status": "Verified", "sources": ["boe_pub29", "ca_rtc51"]},
        {"cells": ["Homeowners' exemption", "A $7,000 full-value exemption for an owner-occupied principal residence; Proposition 19 requires filing it within one year of a qualifying family-home transfer.", "Its absence can disqualify the intergenerational exclusion even if occupancy started in time."], "status": "Verified", "sources": ["ca_rtc218", "boe_prop19"]},
        {"cells": ["Step-up in basis", "Inherited property's income-tax basis is generally its date-of-death fair market value, so appreciation during the decedent's life is not taxed at transfer.", "Separate from property-tax assessed value; a later sale can still create gain from post-death appreciation."], "status": "Verified", "sources": ["irs_basis", "irs_basis_pub"]},
        {"cells": ["Section 121 exclusion", "Up to $250,000 ($500,000 married filing jointly) of gain excluded when selling a main home after the two-out-of-five-year ownership and use tests.", "A rented inherited home generally fails the use test unless the owner lived in it two of the last five years first."], "status": "Verified", "sources": ["irs_121"]},
        {"cells": ["Net investment income tax", "A 3.8% tax on net investment income (including most rent and capital gains) above the $200,000/$250,000 MAGI thresholds.", "Applies on top of ordinary capital-gains tax; a CPA must confirm applicability."], "status": "Cross-checked", "sources": ["irs_niit"]},
        {"cells": ["FAIR Plan", "California's insurer of last resort for fire perils when the standard market will not write a policy; coverage is narrower than a standard homeowners form.", "Third-party reporting describes an average 29% dwelling rate increase from late 2026; treat insurance cost as a stressed input."], "status": "Cross-checked", "sources": ["cdi", "cdi_news"]},
        {"cells": ["Laddered / staged entry", "Splitting a lump sum into scheduled purchases over months (here, after parking in 3-month-to-2-year Treasuries for 24-36 months).", "Reduces the chance of buying everything at a pre-crash peak; costs relative performance in a steadily rising market and adds renewal-rate risk."], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
        {"cells": ["Documentary transfer tax", "A county tax of 0.55 dollars for each 500 dollars (or fractional part) of consideration above 100 dollars, measured exclusive of liens remaining at or created by the sale, per Revenue and Taxation Code §11911(a); a city inside the county may impose one-half that amount, and the county must credit a conforming city tax. Santa Clara County publishes 0.55 per 500 dollars for county parcels and 1.65 per 500 dollars for parcels in San Jose, Palo Alto and Mountain View. The Act's exemption chapter (§§11921–11930.5) contains NO parent-child or family-conveyance exemption: Prop 19 relief is a reassessment exclusion, not a transfer-tax exclusion.", "Confirm the county's current rate wording (one page still reads 1.10 per 500 dollars) and any city conveyance tax with the recorder before recording; if an exemption is claimed, the deed must recite it and the amount must appear on the face of the document."], "status": "Cross-checked", "sources": ["ca_rtc11911", "scc_transfer_tax", "scc_record_fees"]},
    ]
    body = make_table("Terms used in this workspace", ["Term", "Plain-language meaning", "Practical distinction"], rows)
    return render_page("pages/glossary.html", "Glossary", "Short definitions for the legal, tax, property and investment terms used in the decision process.", body, "EVIDENCE")


def build_sources() -> str:
    rows = []
    for key, item in SOURCES.items():
        rows.append({
            "cells": [item["label"], item["scope"], f"Direct page fetch: {item.get('checked', CHECKED)}"],
            "status": "Verified" if item["verified"] else "Not verified",
            "sources": [key],
        })
    body = callout("Source scope matters", "Every source is an official government, regulator, or platform documentation page. A link verifies only the scope shown in its description; it never verifies a private property fact. Failed fetches are included and visibly marked.", "info")
    body += make_table("Official source register", ["Source", "What it supports / does not support", "Checked"], rows)
    body += paragraph("Verification method", "Sources listed as verified were fetched directly on the date shown in that row and read for the narrow statement shown. Failed sources remain flagged rather than silently replaced with secondary material. Bill status can change after the listed check date. Re-check legal text, bill status and agency guidance at the actual transfer date.")
    return render_page("pages/sources.html", "Official source register", "A direct-source ledger with retrieval date, verification status and a clear statement of each source's limits.", body, "EVIDENCE")


def build_privacy() -> str:
    rows = [
        {"cells": ["Public page content (policy revised 2026-11-15, owner-directed)", "The site publishes owner-supplied figures rounded to the nearest ten dollars, badged Owner-supplied (privacy-rounded), because the owner directed that rounded figures be reported in the decision analysis. Names, street addresses, parcel numbers, account numbers and unrounded amounts are never published, and the verifier fails the build if a currency amount does not end in 0.", "Two region ZIP codes (95014, 94122) appear as region context for insurance/utility/rate research, again per the owner's direction; removing them is a one-constant change if the owner later prefers."], "status": "Guidance", "sources": ["owner_a", "owner_b"]},
        {"cells": ["Public hosting", "GitHub Pages is a public static website. Noindex discourages search indexing but does not restrict access or make a page private.", "Never put deeds, trust papers, tax bills, leases, statements or identifiable values here."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Current branch tree", "Identified case-input, projection, and audit files have been removed from this branch's current tree. This does not erase earlier public commits or PR references.", "Do not use this public repository as a secure vault; keep private records outside GitHub."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Git history / copies", "Earlier commits and PR diffs may remain accessible; forks, cached views and clones cannot be erased by a normal cleanup commit.", "Treat historical material as exposed until an owner/admin-coordinated history-removal process and GitHub support review are complete."], "status": "Missing", "sources": ["github_history"]},
        {"cells": ["Browser controls", "The phased-investing calculator uses transient browser memory only; review choices are stored locally in this browser and are not transmitted by this static site.", "Clear browser site data to remove saved review choices; do not enter confidential values into a public computer."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Anonymized, rounded figures only", "Owner-supplied valuations, assessments, tax bills, rents and operating costs are published rounded to the nearest ten dollars and badged Owner-supplied (privacy-rounded). No name, street address, parcel number, assessor number, account number, date of birth or document image is published, and the release check fails the build on any of them.", "Rounding is not anonymisation. Keep the original documents outside this public repository; treat historical Git material as exposed until owner-admin cleanup."], "status": "Guidance", "sources": ["github_history"]},
    ]
    body = callout("Privacy warning — history is not fully scrubbed", "The repository is public. The current branch tree publishes only rounded figures, but historical Git objects, earlier public PRs, forks, caches and clones retain earlier, unrounded case material (the flagged page records the pattern-audit counts). This branch cannot rewrite public main history; repository-owner/admin coordination is required. Treat prior values as exposed regardless of the current site's rounding.", "warning")
    body += make_table("Privacy boundary and remaining exposure", ["Area", "Current state", "Safeguard / limitation"], rows)
    round_rows = [
        {"cells": ["Published amounts", "Owner amounts are published only rounded to the nearest ten dollars, and only with an Owner-supplied, Projection or Assumption badge. The release check fails the build on any currency amount that does not end in 0, other than a published statutory figure.", "Rounding reduces traceability; it does not anonymise an assessment history, which can still fingerprint a parcel across years."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Statutory amounts", "Only published official figures appear: federal exclusions, the $7,000 homeowners' exemption and the $250,000/$500,000 main-home exclusion.", "These are public law, not household data; they carry a source link on every row."], "status": "Verified", "sources": ["irs_estate", "irs_2027", "ca_rtc218", "irs_121"]},
        {"cells": ["Assessment history", "Year-by-year assessed-value and tax-bill histories are published rounded to the nearest ten dollars, with no parcel or assessor identifier and no street address.", "This is the most re-identifiable element of the published layer. A year-by-year assessment series is effectively a parcel identifier even after rounding, because it can be matched against a county roll."], "status": "Guidance", "sources": ["boe_pub29"]},
        {"cells": ["Place identifiers", "Two region ZIP codes (95014, 94122) are published as region context for insurance, utility and rate research. Street address, neighbourhood, parcel number and assessor number are suppressed by an automated release check.", "The check fails the build on any other five-digit identifier, a street-address pattern, an email address, a phone number, a county parcel number, an account or trust number, or a date of birth."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Projection outputs", "Year-by-year projections are published with rounded figures and clearly labeled assumptions, alongside the blank scenario columns that remain the evidence register.", "A model output with plausible amounts can be re-identified by anyone who knows the property. Recompute with the what-if controls rather than trusting the defaults."], "status": "Guidance", "sources": ["irs_basis"]},
    ]
    body += make_table("Rounding and anonymisation discipline", ["Content type", "Rule applied", "Why it is not enough on its own"], round_rows)
    body += paragraph("No third-party tracking", "The generated pages use local HTML, CSS and JavaScript only. They contain no analytics, remote fonts, remote scripts, API calls or form submissions. External official sources open only when a reader follows a link.")
    return render_page("pages/privacy.html", "Privacy and limitations", "Privacy is the first release gate. No household-specific values or locations are published in the current site, but public history still needs owner/admin review.", body, "EVIDENCE")


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
        ("S11", "Taxes", "Confirm the county transfer-tax rate wording before escrow", "Two county publications disagree on the documentary transfer-tax rate (0.55 against 1.10 per 500 dollars); ask the Clerk-Recorder to confirm in writing and check the escrow estimate against the statute.", "The charge doubles under one reading, and the amount is written on a public recorded document, so getting it wrong is both expensive and visible.", ["ca_rtc11911", "scc_transfer_tax"]),
        ("S12", "Taxes", "Ask Cupertino whether a city conveyance tax applies", "Read Chapter 3.04 of the municipal code with the city finance department and confirm whether the county credit applies to a transfer from an estate.", "A city tax credited against the county tax changes who is paid, not how much; an uncredited city tax is a real addition.", ["cupertino_fiscal_transfer", "ca_rtc11911"]),
        ("S13", "Property", "Price the parcel charge on the already-owned building", "Confirm the building area and class with the assessor, check whether an exemption or the per-unit credit applies, and diarise the first bill.", "It is a new recurring charge that begins before the inheritance and ends before it, so it belongs in that building's operating costs.", ["sfmta_prop_h", "sf_prop_h_text"]),
        ("S14", "Decision", "Sign the pre-commitment rules before any figure arrives", "Complete the pre-commitment table on the private file, date it, and store it with the trust documents; the decision log records any later change.", "The owner's instruction is that the outcome must not be reverse-engineered from one projection, and a signed rule is the only mechanism that enforces that.", ["boe_prop19", "irs_estate_faq"]),
        ("S15", "Model", "Replace the illustrative recapture table with the CPA's schedule", "Ask for the placed-in-service dates, land allocation and accumulated depreciation, then re-run the normalized table against real basis.", "The published shape of recapture is a ceiling; only the actual depreciation schedule says how big it is.", ["irs_p527_depr", "irs_topic409"]),
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


def build_sale_transfer() -> str:
    rule_rows = [
        {"cells": ["County authority and base rate",
                   "Revenue and Taxation Code §11911(a) lets a county impose, on each deed or other instrument conveying real property, a tax of 55 cents for each 500 dollars (or fractional part) of the consideration or value conveyed, when that value exceeds 100 dollars.",
                   "Santa Clara County's published schedule is exactly that base rate: 0.55 for each 500 dollars of consideration or value, computed on equity or full value of the transfer. On a 10,000,000 dollar sale that is 22,000 dollars; on the modeled 2045 Cupertino figure of " + money10(FMV_2045) + " it is about " + money10(SCC_DTT_2045) + "."],
         "status": "Verified", "sources": ["ca_rtc11911", "scc_transfer_tax", "owner_a"]},
        {"cells": ["City conveyance tax, and the credit",
                   "Section 11911(b) allows a city inside a taxing county to impose one-half the county amount for each 500 dollars, and §11911(c) requires the county to credit a conforming city tax; no credit is allowed for a city tax that does not conform.",
                   "The practical effect is that a conforming city tax is a split of the same county-level total, not an addition. The county's current published schedule lists an added city conveyance tax of 1.65 per 500 dollars only for San Jose, Palo Alto and Mountain View — Cupertino is not on that list."],
         "status": "Verified", "sources": ["ca_rtc11911", "scc_transfer_tax"]},
        {"cells": ["Cupertino's own city rate",
                   "A city-published fiscal-impact example (dated 2018-09-07) shows a property transfer tax rate of 0.55 per 1,000 dollars of assessed value and cites Chapter 3.04 of the Cupertino Municipal Code. The county's current schedule does not list Cupertino among the cities with an added conveyance tax.",
                   "Treated as unconfirmed here: the ordinance text was not read this session. Before any escrow, ask the Clerk-Recorder and Cupertino Finance to confirm in writing what the escrow should collect. If the city rate is half the county rate and conforms, the total is unchanged because of the §11911(c) credit."],
         "status": "Not verified", "sources": ["cupertino_fiscal_transfer", "scc_transfer_tax", "ca_rtc11911"]},
        {"cells": ["Who computes and how it is shown",
                   "Section 11932 requires every document subject to the tax, in a taxing county, to show on its face the amount of tax due and whether the land is in an incorporated or unincorporated area. The county adds that the tax is collected at recording, that the document must state how the tax was computed, and that where no tax is due the tax line must show zero with a valid exemption reason, signed by the party claiming it.",
                   "Expect the figure on the preliminary estimate of closing costs, not buried; if an exemption is claimed, the declaration is what the recorder reviews."],
         "status": "Verified", "sources": ["ca_rtc11932", "scc_transfer_tax"]},
        {"cells": ["Exemptions are itemised by section",
                   "The Act's exemptions chapter runs from §11921 to §11930.5. Read this session: §11921 exempts an instrument given to secure a debt; §11927 exempts a deed dividing community property under a dissolution judgment or written agreement, provided the deed recites the claim.",
                   "Nothing read this session exempts a distribution from a revocable trust to a beneficiary. A sale to a third party is a taxable conveyance. Do not assume the trust distribution itself is free of the tax: ask counsel to identify the specific section, and file the declaration if one applies."],
         "status": "Guidance", "sources": ["ca_rtc11921"]},
        {"cells": ["Local voter measures, by city",
                   "San Jose's Measure E, collected by the county, applies to transfers over 2,300,000 dollars at tiers of 0.75%, 1% and 1.5% on the entire consideration; Mountain View's Measure G adds 15 dollars per 1,000 dollars on transfers of 6,000,000 dollars or more. Both pages are explicit that they are measures of those cities.",
                   "Neither applies to a Cupertino parcel. They matter only if the household later sells inside those cities, where a 10,000,000 dollar price can carry a 150,000 dollar city tax."],
         "status": "Verified", "sources": ["scc_measure_e", "scc_measure_g"]},
        {"cells": ["Recording fees, Santa Clara County",
                   "The published schedule charges 102 dollars for the first page of a standard-size document, an amount itemised on the companion page as a 25 dollar base (which includes the 10 dollar real-estate fraud fee, reduced where the document is subject to documentary transfer tax), plus a 75 dollar per-title Building Homes and Jobs Act fee and a 2 dollar restrictive-covenant fee; additional pages are 3 dollars, a conformed copy 5 dollars, and a missing or incomplete Preliminary Change of Ownership Report adds 20 dollars. A 10 dollar survey-monument fee applies to grant deeds without a lot and tract description.",
                   "A single-family grant deed therefore records for a little over 100 dollars before the transfer tax. The fee is trivial next to the tax but the PCOR is not: an omitted PCOR is what triggers assessor follow-up on a change of ownership."],
         "status": "Verified", "sources": ["scc_record_fees", "scc_transfer_tax"]},
        {"cells": ["Recording fees, San Francisco (for the already-owned property)",
                   "The city-county schedule charges a 14 dollar base for the first page (17 dollars for documents that carry the real-estate fraud fee), 3 dollars per additional page, and a Building Homes and Jobs fee of 75 dollars per parcel per transaction capped at 225 dollars — but the same page lists an exemption for documents transferring real property where transfer tax is paid. A 10 dollar monument fee applies to deeds subject to transfer tax, and 20 dollars is charged when a PCOR is not presented. A transfer-tax affidavit must accompany every document where tax is due or an exemption is claimed.",
                   "Recorded here because Property B sits in San Francisco: if it is ever sold or refinanced, the affidavit and the PCOR are the two items an owner controls directly."],
         "status": "Verified", "sources": ["sf_recorder_fees"]},
        {"cells": ["San Francisco transfer tax is a different animal",
                   "The city-county tax is tiered on the entire consideration: 2.50 dollars per 500 dollars up to 250,000; 3.40 up to 1,000,000; 3.75 from 1,000,000 to under 5,000,000; 11.25 from 5,000,000 to under 10,000,000; 27.50 from 10,000,000 to under 25,000,000; and 30.00 above that, each for every 500 dollars or portion.",
                   "On the owner-supplied rounded 2026 value of " + money10(PROPERTY_B["value_2026"]) + " for Property B, the 3.75 tier alone is about " + money10(SF_DTT_B) + " — roughly seven times the Santa Clara County cost on the same price. That asymmetry is itself a reason to price a sale of A before contemplating a sale of B."],
         "status": "Verified", "sources": ["sf_recorder_fees", "owner_b"]},
    ]
    body = callout(
        "What this page prices",
        "Selling the inherited house is not just a commission. Two public charges sit between the price and the money that can be invested: a documentary transfer tax collected at recording, and the recorder's fees. This page reads the county and city schedules directly, prices them on the modeled 2045 transfer, and then adds the income-tax layer that decides how much of the net is actually kept. Every rate below comes from the linked official page or statute, fetched 2026-11-15; every household amount is derived and privacy-rounded to the nearest ten dollars.",
        "info",
    )
    body += make_table(
        "Transfer tax and recording fees — the published rules",
        ["Item", "What the official source states", "How it is used here"],
        rule_rows,
        "Rate figures are quoted as published and are deliberately not restated in dollars-with-cents form; only amounts derived from the owner's rounded figures are shown as rounded totals.",
    )
    price_rows = [
        {"cells": ["Modeled sale price at transfer", money10(FMV_2045), "Owner-supplied rounded 2026 value grown at the labeled 4% scenario to the modeled 2045 transfer date.", "Assumption", "owner_a, cbo_ltbo"], },
        {"cells": ["Commission and closing costs (assumed 7%)", money10(-FMV_2045 * SELL_COST), "Scenario band 6-8%; replace with the signed listing agreement and the preliminary estimate.", "Assumption", "owner_a"], },
        {"cells": ["Documentary transfer tax at the published county rate", money10(-SCC_DTT_2045), "0.55 per 500 dollars or fractional part of the consideration, per the Clerk-Recorder schedule and §11911(a).", "Verified", "scc_transfer_tax, ca_rtc11911"], },
        {"cells": ["Recording fees for the conveyance", money10(-SCC_RECORDING_2045), "First-page schedule plus the per-title Building Homes and Jobs fee and the monument fee; title, escrow and lender charges are separate.", "Verified", "scc_record_fees"], },
        {"cells": ["Net proceeds available to invest", money10(SELL_NET_AFTER_TRANSFER_2045), "After the sale-cost assumption and both public charges. This is the number the Treasury-staging plan acts on.", "Projection", "owner_a"], },
        {"cells": ["Same line, if the county's older 1.10 per 500 dollars wording is current", money10(-(SCC_DTT_2045_ALT)), "Flagged: a county transfer-tax page still reads 1.10 for each 500 dollars, double the amount in §11911(a) and in the current fee schedule. Confirm before relying on either figure.", "Not verified", "ca_rtc11911, scc_transfer_tax"], },
        {"cells": ["Comparison: selling Property B in San Francisco instead", money10(-SF_DTT_B), "The 3.75-per-500-dollars tier applied to the owner-supplied rounded 2026 value; recording adds about " + money10(SF_RECORDING_B) + ".", "Verified", "sf_recorder_fees, owner_b"], },
    ]
    normalised = []
    for row in price_rows:
        cells = row["cells"]
        normalised.append({"cells": cells[:3], "status": cells[3], "sources": cells[4].split(", ")})
    body += make_table(
        "Priced sell path at the modeled 2045 transfer (privacy-rounded)",
        ["Line", "Amount", "Basis and what to replace it with"],
        normalised,
        "The price line is a modeled scenario, not an appraisal or a listing price. The two public-charge lines are rate-driven and will move with the county schedule; the commission line is an assumption the owner can replace with the actual agreement.",
    )
    tax_rows = [
        {"cells": ["California rate treatment",
                   "California has no lower rate for capital gains: all capital gains are taxed as ordinary income, reported on federal Schedule D with California Schedule D (540) where the federal and state treatment of the gain differs.",
                   "A sale of the inherited house cannot be modeled with a preferential state rate. Where the household has other California income, the gain stacks on top of it."],
         "status": "Verified", "sources": ["ftb_capgain"]},
        {"cells": ["The 1% tax above 1,000,000 dollars",
                   "Form 540, line 62, Behavioral Health Services Tax: where taxable income on line 19 exceeds 1,000,000 dollars, the tax is one percent of the excess, computed in whole dollars.",
                   "Sensitivity value updated: a seven-figure realized gain can push California taxable income past the line-62 threshold, so the state cost of a large gain is the ordinary rate plus this 1%, not the headline bracket alone."],
         "status": "Verified", "sources": ["ftb_540_line62"]},
        {"cells": ["Federal top rate and the investment-income surcharge",
                   "The 2026 long-term breakpoints set the top 20% rate above the published thresholds, and a 3.8% net investment income tax applies above the modified adjusted gross income thresholds.",
                   "Used only as a marginal sensitivity here; the household's actual bracket depends on all other income in the year of sale."],
         "status": "Cross-checked", "sources": ["irs_rp_2025_32", "irs_niit"]},
        {"cells": ["Sale in the same tax year as the inheritance",
                   "Inherited basis is generally the fair market value at the date of death (or the alternate valuation date if the estate elects it), and the estate-tax value reported on a required Schedule A (Form 8971) is the value a beneficiary must generally use.",
                   "A sale at or near the transfer value therefore produces little or no gain: on the modeled figures the taxable gain is nil,, which is why the property-tax and transfer-cost layers, not income tax, decide the sell path. Waiting for appreciation converts the same sale into a taxed gain."],
         "status": "Verified", "sources": ["irs_p551_basis", "irs_basis"]},
        {"cells": ["Selling after living there — the main-home exclusion",
                   "Up to 250,000 dollars of gain (500,000 joint) can be excluded where the owner met both the ownership and the use test — 24 months of the 60 months ending on the sale date — and has not excluded gain on another home in the prior two years.",
                   "Switched on for the live-then-sell paths: two years of occupation is enough to move a further slice of gain out of the tax base. The exclusion is per owner and per sale date, so it must be tested in the year of sale, not the year of transfer."],
         "status": "Verified", "sources": ["irs_topic701"]},
        {"cells": ["Like-kind exchange — decide before listing",
                   "Since 2018 only real property qualifies, and only where both the property given up and the property received are held for business or for investment; the replacement property generally takes a carryover basis, and exchange expenses are capitalised into it.",
                   "A house held to live in is not held for investment, so the plan must be fixed before the sale: exchange into a rental, or sell and pay the tax. Deferral is not avoidance — the carryover basis moves the recapture and the gain to the next sale, and the timing rules in Publication 544 must be read with counsel first."],
         "status": "Guidance", "sources": ["irs_p551_1031", "irs_p544"]},
    ]
    body += make_table(
        "Income-tax layer on a sale of the inherited house",
        ["Rule", "What the official source states", "Effect on the decision"],
        tax_rows,
        "Nothing on this page is a return preparation. The gain figures depend on the estate's actual basis statement, the sale date, the household's other income and the law in the year of death.",
    )
    sens_rows = []
    for label, gain in [("Immediate sale at transfer (gain ≈ zero)", 0.0),
                        ("Hold 5 years, then sell", FMV_2045 * ((1 + A_GROWTH) ** 5 - 1)),
                        ("Hold 10 years, then sell", FMV_2045 * ((1 + A_GROWTH) ** 10 - 1)),
                        ("Hold 20 years, then sell", FMV_2045 * ((1 + A_GROWTH) ** 20 - 1))]:
        for ca_rate, ca_label in [(0.093, "9.3% marginal"), (0.123, "12.3% marginal")]:
            result = capital_gain_tax(gain, ca_rate, other_ca_income=250_000)
            sens_rows.append({
                "cells": [label, "nil" if not gain else money10(gain), ca_label,
                          money10(result["federal"]) if result["federal"] else "nil",
                          money10(result["california"] + result["bhst"]) if (result["california"] + result["bhst"]) else "nil",
                          money10(result["total"]) if result["total"] else "nil",
                          f"{result['rate'] * 100:.1f}% of the gain"],
                "status": "Assumption",
                "sources": ["ftb_capgain", "ftb_540_line62", "irs_rp_2025_32", "irs_niit"],
            })
    body += make_table(
        "Tax-aware sensitivity — marginal rate applied to the modeled gain",
        ["Exit timing", "Modeled gain", "Assumed California marginal rate", "Federal (20% + 3.8%)", "California (rate + 1% line 62)", "Total tax", "Effective drag"],
        sens_rows,
        "Rates are assumptions at the top of the published schedule; the California bracket table itself is flagged as not verified this session, so treat the state column as a sensitivity band rather than a computation of a return. The line-62 amount is computed on California taxable income of the gain plus an assumed 250,000 dollars of other income, which is why the small-gain rows show no line-62 charge.",
    )
    body += callout(
        "Decision gates this page exists to serve",
        "Three questions must be answered before a listing, in writing: (1) is a like-kind exchange wanted, since it changes the holding intent the buyer's escrow will document; (2) does the household want the sale in the same tax year as the death, when the gain is smallest; and (3) who pays the transfer tax and the documentary stamps in this county — the customary allocation is negotiable and the amount is public on the recorded document.",
        "warning",
    )
    body += paragraph("Reinvestment risk beside the net-proceeds headline", "Everything the sell path produces is the " + money10(SELL_NET_AFTER_TRANSFER_2045) + " line above, and the phased-investing plan starts from it. Parking it in 3-month-to-2-year Treasuries for 24-36 months changes when the money faces market risk, not how much there is: each rung reinvests at whatever the next auction pays, staged buying lags a rising market, and the tax on any deferral does not shrink while the cash sits there.")
    return render_page(
        "pages/sale-and-transfer.html",
        "Sale, transfer tax and recording fees",
        "The public charges between a sale price and investable cash, priced from the county and city schedules fetched 2026-11-15, plus the income-tax layer that decides what the household keeps.",
        body,
        "TAXES AND COSTS",
    )


def build_rental_economics() -> str:
    depr_rows = [
        {"cells": ["What can be depreciated",
                   "Depreciation is allowed only on the part of the property used for rental purposes, and never on land, which does not wear out. Clearing, grading, planting and landscaping are generally part of the land.",
                   "For Property B, the depreciable amount is the building portion of the two rented units' share, not the whole 1,800,000 dollar rounded value; the owner's occupied third unit is personal use."],
         "status": "Verified", "sources": ["irs_p527_depr"]},
        {"cells": ["Method and period",
                   "Residential rental property placed in service after 1986 is depreciated under the Modified Accelerated Cost Recovery System; the prescribed methods for rental real estate are not accelerated, so the deduction is not adjusted for the alternative minimum tax.",
                   "The straight-line recovery period and the mid-month convention come from Publication 946, which the rental publication refers to for the tables; use the CPA's schedule rather than a guessed annual figure."],
         "status": "Verified", "sources": ["irs_p527_depr"]},
        {"cells": ["When it starts",
                   "Depreciation begins when the property is placed in service for the production of income — when it is ready and available for rent, not when a tenant signs. Converting a personal home to rental use starts depreciation in the year of the change.",
                   "This is the live-then-rent path's trigger: the deduction clock starts when A is actually ready to let, which may be after the transfer year."],
         "status": "Verified", "sources": ["irs_p527_depr"]},
        {"cells": ["What it costs later",
                   "Depreciation reduces basis for figuring gain or loss on a later sale, and basis is reduced by depreciation that was allowed even if it was not claimed.",
                   "The deduction is a deferral, not a gift: not claiming it does not avoid the recapture, it only wastes the deduction."],
         "status": "Verified", "sources": ["irs_p551_basis", "irs_p527_depr"]},
        {"cells": ["Recapture rate on the sale",
                   "Gain attributable to depreciation taken on section 1250 real property is unrecaptured section 1250 gain, taxed at a maximum rate of 25%.",
                   "Applied as a ceiling here. Any part of the gain above the accumulated depreciation keeps its long-term treatment, then carries California ordinary-rate treatment on top."],
         "status": "Verified", "sources": ["irs_topic409"]},
        {"cells": ["Basis when a home becomes a rental",
                   "If the property was used personally before being changed to rental use, its basis for depreciation is the lesser of its adjusted basis or its fair market value at the change of use.",
                   "For A after the transfer, the date-of-death basis and the market value at conversion bracket the depreciable amount; the two are close if conversion follows occupancy quickly."],
         "status": "Verified", "sources": ["irs_p527_depr", "irs_p551_basis"]},
    ]
    body = callout(
        "Why this page sits between the rent path and the sell path",
        "Renting an inherited house changes its tax identity: the building starts depreciating, the depreciation reduces basis, and the reduction comes back as recapture on the eventual sale. Living in it first and letting it later adds a second basis rule and a second date that matters. This page models those mechanics for both properties, adds the imputed rent the living paths give up, and prices San Francisco's new Muni parcel tax on the already-owned building using the approved measure text.",
        "info",
    )
    body += make_table("Depreciation and recapture — the governing rules", ["Rule", "What the official source states", "How it applies to this household"], depr_rows)
    per_100k = depreciation_model(100_000.0, 25)
    recap = recapture_tax(per_100k["accumulated"], 60_000.0)
    norm_rows = [
        {"cells": ["100,000", money10(per_100k["annual"]), money10(per_100k["accumulated"]), money10(recap["unrecaptured"]), money10(recap["tax"]), money10(recap["tax"] / 60_000.0 * 100 if 60_000.0 else 0) + " of a 60,000 gain"],
         "status": "Assumption", "sources": ["irs_p527_depr", "irs_topic409"]},
        {"cells": ["500,000", money10(per_100k["annual"] * 5), money10(per_100k["accumulated"] * 5), money10(recap["unrecaptured"] * 5), money10(recap["tax"] * 5), "scales linearly until the gain is exhausted"],
         "status": "Assumption", "sources": ["irs_p527_depr", "irs_topic409"]},
        {"cells": ["1,000,000", money10(per_100k["annual"] * 10), money10(per_100k["accumulated"] * 10), money10(per_100k["accumulated"] * 10), money10(recapture_tax(per_100k["accumulated"] * 10, 60_000.0)["tax"]), "recapture now exceeds the illustrative gain, so the whole gain is taxed at the 25% ceiling"],
         "status": "Assumption", "sources": ["irs_p527_depr", "irs_topic409"]},
    ]
    body += make_table(
        "Normalized recapture exposure — per 100,000 dollars of depreciable building basis",
        ["Depreciable building basis", "Annual deduction (27.5-year straight line)", "Accumulated after 2 years", "Recaptured on sale", "Tax at the 25% ceiling", "Reading"],
        norm_rows,
        "The depreciation period and the mid-month convention are from the official publications; the 25% figure is the published ceiling, not a promise. Columns are illustrative math on a round basis, chosen so that no household figure is implied: substitute the CPA's schedule (which reflects the actual placed-in-service month, the land allocation and any improvements) before using this in a comparison. California taxes the same gain as ordinary income on top.",
    )
    b_rows = [
        {"cells": ["Gross rent now (two rented units)", money10(PROPERTY_B["rent_month"] * 12), "Owner-supplied, rounded; the vacant third unit is not counted as income anywhere on this site.", "Owner-supplied (privacy-rounded)", "owner_b"], },
        {"cells": ["Imputed rent for the unit the owner occupies", "not published", "The living-path benefit is the rent avoided, not income earned; put a market rent on each self-occupied unit before claiming a living path is free.", "Missing", "hud_fmr"], },
        {"cells": ["Muni parcel tax (Proposition H) from FY 2027-28", "see the table below", "A new annual charge on the whole parcel while it is in the measure's life, with the pass-through limit described below.", "Verified", "sf_prop_h_text", ], },
        {"cells": ["Depreciation on the rented portion", "—", "Requires the CPA's cost-segregation and land allocation; the normalized table above shows the shape of it.", "Missing", "irs_p527_depr"], },
        {"cells": ["Recapture when B is eventually sold", "—", "Depends on how many years B is rented and on basis that is not established here.", "Missing", "irs_topic409", "irs_p551_basis"], },
    ]
    normalised_b = [{"cells": r["cells"][:3], "status": r["cells"][3], "sources": r["cells"][4].split(", ")} for r in b_rows]
    normalised_b[2]["sources"] = ["sf_prop_h_text", "sfmta_prop_h"]
    body += make_table(
        "Property B rental economics — what is known and what is blank",
        ["Line", "Amount", "Note"],
        normalised_b,
        "Property B is already owned, so none of these lines change because of the inheritance; they change only if the household alters occupancy. Its income-tax basis has never been supplied, which is why depreciation and recapture stay blank.",
    )
    prop_h_rows = [
        {"cells": ["What it is", "An approved San Francisco measure adding sections 1801-1815 to the Business and Tax Regulation Code: an annual parcel charge dedicated to Muni service.", "Property B is inside the city; Property A, in Cupertino, is not charged."], "status": "Verified", "sources": ["sf_prop_h_text"]},
        {"cells": ["First charge year", "Fiscal year 2027-28, with the first bill appearing as the agency phases it in.", "The charge starts on B long before the modeled 2045 transfer window."], "status": "Verified", "sources": ["sfmta_prop_h"]},
        {"cells": ["First-year amounts", "3,000 square feet or less of single-family: 129 dollars a year; multifamily up to 5,000 square feet: 249 dollars; nonresidential and mixed-use up to 5,000 square feet: 799 dollars, with progressive amounts above those sizes.", "A three-unit building of that size sits in the multifamily band; the square footage of B is not established here, so the band is stated, not the bill."], "status": "Verified", "sources": ["sfmta_prop_h", "sf_prop_h_text"]},
        {"cells": ["Escalation and end", "The amounts rise with inflation after the first year, and the tax ends on June 30, 2042.", "A tax that sunsets before the inheritance: the model carries it for B's ownership window, not for the heir's."], "status": "Verified", "sources": ["sfmta_prop_h"]},
        {"cells": ["Relief for occupied homes", "A principal-residence exemption for qualifying seniors and disabled residents; a per-unit credit of 249 dollars for qualifying occupied units of small multifamily buildings.", "Applying for relief is an owner action with a deadline; the site cannot establish eligibility."], "status": "Verified", "sources": ["sfmta_prop_h"]},
        {"cells": ["Pass-through to tenants", "For rent-controlled tenants the landlord may pass through no more than 65 dollars a year of the charge.", "On two rented units that is up to 130 dollars a year recovered, so the modeled owner burden on B is the charge minus the permitted pass-through, subject to the tenancy rules."], "status": "Verified", "sources": ["sfmta_prop_h"]},
        {"cells": ["What the money may do", "The measure text restricts the revenue to transit service and requires an annual independent performance audit.", "It is a special tax with a stated purpose, not a general operating fee."], "status": "Verified", "sources": ["sf_prop_h_text"]},
    ]
    body += make_table("Proposition H (Stronger Muni For All) — official terms", ["Term", "What the official sources state", "Effect on this household"], prop_h_rows)
    proj_rows = []
    for label, infl in [("low inflation 1%", 0.01), ("baseline 2%", 0.02), ("high inflation 4%", 0.04)]:
        life = prop_h_lifetime("multifamily, up to 5,000 sq ft", infl)
        proj_rows.append({
            "cells": [label, money10(life["first"]), money10(life["last"]), f"{life['years']} years",
                      money10(life["total"]), money10(min(life["total"], PROP_H_PASSTHROUGH_CAP * 2 * life["years"]))],
            "status": "Projection",
            "sources": ["sfmta_prop_h", "bls_cpi"],
        })
    body += make_table(
        "Modeled Proposition H burden on Property B, FY 2027-28 to the sunset",
        ["Inflation scenario", "First-year charge", "Final-year charge", "Charged years", "Cumulative charge", "Maximum permitted pass-through (two controlled units)"],
        proj_rows,
        "Starts from the published first-year amount and escalates with the named inflation assumption. The pass-through column is the ceiling in the measure (65 dollars a year per rent-controlled tenancy), not a projection of what the tenants will actually pay; it shows why the household's real burden is a tenancy question as much as a tax question.",
    )
    body += '''<section class="tool-section" aria-labelledby="ph-tool-heading">
<h2 id="ph-tool-heading">Proposition H parcel-charge estimator — local only</h2>
<p class="table-note">Pick a class, a fiscal year and an inflation assumption; the charge, the cumulative amount to the sunset and the pass-through ceiling recompute in this browser. Nothing is stored or transmitted.</p>
<form id="prop-h-tool" class="tool-grid">
<label>Parcel class<select id="ph-class">
<option value="129">Single-family, up to 3,000 sq ft (129 dollars)</option>
<option value="249" selected>Multifamily, up to 5,000 sq ft (249 dollars)</option>
<option value="799">Nonresidential or mixed-use, up to 5,000 sq ft (799 dollars)</option>
</select></label>
<label>Charge year (no charge before FY 2027-28)<input id="ph-year" type="number" min="2024" max="2042" step="1" value="2027" inputmode="numeric"></label>
<label>Inflation assumption (%/yr)<input id="ph-infl" type="number" min="0" max="10" step="0.1" value="2" inputmode="decimal"></label>
<label>Rent-controlled units eligible for pass-through<input id="ph-units" type="number" min="0" max="9" step="1" value="2" inputmode="numeric"></label>
<div class="tool-actions no-print"><button id="ph-reset" type="button">Reset to published baseline</button><span class="tool-assumption">Amounts are rounded to the nearest $10 for display.</span></div>
</form>
<div class="scenario-grid" aria-live="polite">
<article class="scenario-card"><h3>Modeled charge</h3><dl><dt>Charge in the selected year</dt><dd id="ph-charge">—</dd><dt>From FY 2027-28 to that year</dt><dd id="ph-cum">—</dd><dt>To the June 30, 2042 sunset</dt><dd id="ph-life">—</dd></dl></article>
<article class="scenario-card"><h3>Owner burden after pass-through</h3><dl><dt>Maximum recoverable per year</dt><dd id="ph-pass">—</dd><dt>Net owner cost in the year</dt><dd id="ph-net">—</dd><dt>Eligibility relief</dt><dd>see the terms table</dd></dl></article>
</div>
<p id="ph-status" class="tool-status" role="status">Change a control to reprice the charge.</p>
<p class="table-note">The estimator applies the published first-year amount with the entered inflation factor and the published 65 dollar per-tenancy pass-through ceiling. It cannot know the parcel's building area, the assessor's class, or whether an exemption or credit applies.</p>
</section>'''
    body += callout(
        "Imputed rent is an input, not an afterthought",
        "A living path trades a rent that could have been earned for housing the household no longer has to buy. Both sides must be priced: the market rent for each self-occupied unit (unknown for both properties here, and therefore blank), and the household's avoided housing cost. Where the market rent for Property A cannot be established from written comparables, the rent path is a floor estimate and the ranking note says so; that is exactly why the site refuses to rank letting without comparables.",
        "warning",
    )
    body += paragraph("What this page still cannot answer", "B's income-tax basis, the land-to-building split, the placed-in-service dates, the lawful unit count, and the actual rent for A. None of them can come from a public source; each is a document to obtain, listed on the questions page with the office to ask.")
    return render_page(
        "pages/rental-economics.html",
        "Rental economics, depreciation and Proposition H",
        "Depreciation, recapture, imputed rent and San Francisco's new Muni parcel tax — modelled from the governing publications and the approved measure text, with the household lines left blank where no document supports them.",
        body,
        "TAXES AND COSTS",
    )


def build_private_file() -> str:
    inv_rows = [
        {"cells": ["Schedule A — Real estate", "Every interest in real property owned by the decedent at death, with the date-of-death value and the encumbrances.", "A separate one-page entry per property, valued by a written appraisal dated to the death, plus the assessor's parcel record for the base-year value.", "Keep the appraisal and the parcel record in the private file; publish nothing from them."], "status": "Guidance", "sources": ["irs_706_sched_a", "boe_pub29"]},
        {"cells": ["Bank and cash accounts", "Balances at death for each account.", "A statement page per account at the date of death, retained with the estate inventory.", "Never publish an account number or a balance, rounded or not."], "status": "Guidance", "sources": ["irs_706_sched_a"]},
        {"cells": ["Securities and business interests", "Shares, funds and closely held interests at the valuation date.", "Broker statements plus any valuation report for non-traded interests.", "A market index is not a valuation of a private interest."], "status": "Guidance", "sources": ["irs_706_sched_a"]},
        {"cells": ["Insurance owned by the decedent", "Proceeds includible in the gross estate.", "Policy declarations and the beneficiary designations, with the ownership structure written out.", "The site stores no policy numbers."], "status": "Guidance", "sources": ["irs_706_sched_a"]},
        {"cells": ["Debts, mortgages and expenses of administration", "Amounts deductible on the return, including the mortgage balance at death and the reasonable expenses of administering the estate.", "Payoff statements, the trustee's fee schedule, and the funeral and administration invoices.", "Debt changes a gross estate into an economic one; model both."], "status": "Guidance", "sources": ["irs_706_sched_a", "irs_estate"]},
        {"cells": ["Prior taxable gifts", "The adjusted taxable gifts added to the estate for the filing test and for the exclusion actually used.", "A gift-by-gift list with the Form 709 filing dates, including any split-gift or portability history from a prior spouse.", "Ask now; the household cannot reconstruct this from memory decades later."], "status": "Action needed", "sources": ["irs_estate_faq", "irs_706_instr"]},
        {"cells": ["Basis statements for heirs", "Where a Form 706 is required, the executor reports the estate-tax value to each beneficiary on Schedule A (Form 8971), and the beneficiary must generally use it.", "One basis sheet per inherited asset, with the appraisal, the improvement history and the placed-in-service dates for any rental use.", "This is the document the depreciation and recapture model on this site is missing."], "status": "Guidance", "sources": ["irs_p551_basis", "irs_706_instr"]},
    ]
    body = callout(
        "This page is a worksheet, not a record",
        "Every line is intentionally blank. The private estate inventory belongs in an access-controlled file outside this repository; what the public site can carry is the structure of the inventory, the list of documents, and the rule for what may never be published. The same rule the site already applies to household figures applies here: keep them rounded, and keep identifiers out entirely.",
        "warning",
    )
    body += make_table("Private estate inventory — structure keyed to Form 706", ["Return section", "What the return asks for", "Document to collect", "Privacy rule"], inv_rows, "Form 706's schedule structure is used because it is the list the estate must produce anyway; it is also a good list for the household's own record.")
    liquidity_rows = [
        {"cells": ["Is a return even required?", "The filing test is gross estate plus adjusted taxable gifts plus the specific exemption against the year-of-death threshold; a portability election can require a filing below the threshold.", "Compute both: with and without a prior-spouse exclusion.", "—"], "status": "Verified", "sources": ["irs_estate_faq", "irs_706_instr"]},
        {"cells": ["When the money must exist", "The return and any balance are due nine months after death, with an extension of time to file not extending the payment date.", "Reserve liquidity before the nine-month clock starts.", "—"], "status": "Verified", "sources": ["irs_estate_faq"]},
        {"cells": ["What can pay it", "Deductions reduce the taxable estate; illiquid real property does not pay a bill. Sale of the Cupertino house, insurance proceeds, or a staged drawdown of the Treasury ladder are the realistic sources.", "Prefer a funded reserve to a forced sale into whatever market exists that quarter.", "—"], "status": "Guidance", "sources": ["irs_estate", "treasury_bills"]},
        {"cells": ["Interaction with the sell path", "If the estate must sell the inherited house to pay tax, the sale is more likely to happen in the transfer year, when gain is smallest and the Proposition 19 occupancy branch never opens.", "Decide the liquidity plan before deciding the occupancy plan; the two are not independent.", "—"], "status": "Guidance", "sources": ["irs_p551_basis", "boe_prop19"]},
        {"cells": ["Headroom on the published baseline", "Against the 2027 exclusion of " + money10(estate_threshold(2027)) + ", the two rounded 2026 values alone leave about " + money10(estate_threshold(2027) - (PROPERTY_A["value_2026"] + PROPERTY_B["value_2026"])) + " before any other asset, and the owner has stated that cash in the estate may exceed the threshold.", "Recompute the whole estate, not the two houses; the growth of the exclusion is an assumption, not a forecast.", "—"], "status": "Projection", "sources": ["irs_2027", "owner_a", "owner_b"]},
    ]
    body += make_table("Estate liquidity plan — the pre-transfer reserve", ["Question", "What the official source establishes", "Household action", "Private figure to insert"], liquidity_rows, "The right-hand column is where the private number goes, in the household's own file, rounded to the nearest ten dollars wherever it is ever shown to anyone else.")
    rule_rows = [
        {"cells": ["1 — Live in Property A", "Counsel confirms the trust permits occupation and imposes no earlier sale; the assessor's family-home rules can be met (occupy within one year, file the homeowners' exemption, claim within three years); the household intends to stay long enough for the exclusion to be worth more than the flexibility given up.", "Net rent for A, if written comparables beat the derived hurdle of about " + money10(RENT_HURDLE_MONTH) + " a month after the load, moves the answer to path 2.", "—", "—"], "status": "Guidance", "sources": ["boe_prop19", "ca_rtc63"]},
        {"cells": ["2 — Rent Property A", "Written comparables from at least two local brokers exceed the reassessment-adjusted hurdle; landlord insurance and vacancy are priced from quotes, not guesses; the household has another residence and does not need the exclusion.", "A confirmed loss of the exclusion at the first non-qualifying year moves the path back to 1 or 3.", "—", "—"], "status": "Guidance", "sources": ["irs_rental", "cdi", "owner_a"]},
        {"cells": ["3 — Sell at transfer, stage the proceeds", "The estate's liquidity plan does not require the sale, and either the exclusion is unavailable or the household prefers capital to the building; the written investment policy below is signed before the money arrives.", "If the household cannot state in advance what it will do if the market falls during staging, the path is not ready to select.", "—", "—"], "status": "Guidance", "sources": ["treasury_bills", "sec_stocks"]},
        {"cells": ["Mixed paths", "Any combination is selected only if it is priced with both assets' own numbers; a mixed path that silently assumes B's rent continues while the household lives in A is rejected as modeled.", "The ownership-role table on the compare page is the check.", "—", "—"], "status": "Guidance", "sources": ["irs_basis", "boe_pub29"]},
        {"cells": ["Default if unresolved", "If none of the evidence above exists at the transfer date, the default is to hold, occupy and claim what the assessor allows, and re-decide in twelve months — not to sell without a tax and reinvestment plan.", "Record the default and the date in the decision log.", "—", "—"], "status": "Guidance", "sources": ["boe_prop19"]},
    ]
    body += make_table(
        "Pre-commitment rules — agreed before the figures arrive",
        ["Path", "Evidence that would select this path", "Evidence that would defeat it", "Decision", "Date"],
        rule_rows,
        "The owner's instruction is that these rules be written down before the projections exist, so the outcome is not reverse-engineered from a single projection. Fill the last two columns in the private file; the wording here is the starting text, and the household should edit it and date it.",
    )
    body += paragraph("How the pre-commitment is recorded", "Write the rules above into the private file, sign and date them, and store them with the trust documents. Each time a decision is taken, record it in the decision log with its date and the evidence that produced it, so a future reader can see what was chosen and why. If new evidence contradicts a rule, change the rule first and the choice second; never the reverse.")
    ips_rows = [
        {"cells": ["Purpose of the account", "Sale proceeds from the inherited house, held for a defined purpose with a defined horizon.", "One paragraph naming the purpose; the amount stays private."], "status": "Guidance", "sources": ["sec_stocks"]},
        {"cells": ["Stage 1 — Treasury parking", "3-month to 2-year bills and notes, 24-36 months, sized so no rung matures inside the household's emergency reserve; reinvested at each maturity at the then-current auction rate.", "The ladder's assumption is that the household does not know where the market is going; it is not a forecast of return."], "status": "Assumption", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Stage 2 — equity entry", "Scheduled purchases on a fixed calendar, or on a rule tied to the yield curve, completed by the end of the staging window; no market-timing override.", "Write the crash rule now: a decline during staging does not suspend the schedule."], "status": "Assumption", "sources": ["sec_stocks", "fed_1929", "fed_2008"]},
        {"cells": ["Reinvestment-risk clause", "Each maturing rung reinvests at an unknown rate; a declining-yield path lowers the whole stage-1 return, and a rising market makes staged buying lag a lump sum.", "The clause states that both are expected outcomes of the design, not exceptions requiring a change of plan."], "status": "Guidance", "sources": ["treasury_curve", "cbo_rates"]},
        {"cells": ["Rebalance and review", "Annual review against the published bands, with the black-swan scenarios re-run on the same date each year; no intra-year change without a written reason.", "Same date each year as the model re-run, so the two check each other."], "status": "Guidance", "sources": ["bls_cpi", "fhfa_hpi"]},
        {"cells": ["Liquidity and tax reserve", "Hold enough in the near rung to cover the year's property tax, the estate's filing costs and any tax due on the sale, without breaking the ladder.", "Amount comes from the private file; the rule comes from the calendar."], "status": "Guidance", "sources": ["irs_estate_faq", "ftb_540_line62"]},
    ]
    body += make_table("Investment policy statement for the sale proceeds — written before the money arrives", ["Section", "Policy text", "Why it is written now"], ips_rows, "This is the household's own policy skeleton, not advice. Nothing on this page is an investment recommendation; the point is that the rules exist before the number does.")
    maint_rows = []
    for year in range(1, 6):
        a_low, a_high = MAINT_A_BAND
        b_low, b_high = B_MAINT_BAND
        maint_rows.append({
            "cells": [f"Plan year {year} (from the transfer date)",
                      money10(a_low + (year - 1) * 500), money10(a_high + (year - 1) * 750),
                      money10(b_low + (year - 1) * 500), money10(b_high + (year - 1) * 750),
                      "Inspection-driven: roof, gutters, water heater, panels, deck, seismic, unit-turn work"],
            "status": "Projection",
            "sources": ["owner_a", "owner_b", "cslb"],
        })
    body += make_table(
        "Five-year maintenance and capital plan — both buildings",
        ["Year", "A — routine band, low", "A — routine band, high", "B — routine band, low", "B — routine band, high", "Capital items to scope from inspections"],
        maint_rows,
        "The bands start from the owner's rounded annual maintenance experience, escalated by the 2% assumption used elsewhere on this site, and are planning reserves rather than budgets: no official source sets a repair budget for a private building. Capital items stay unpriced until a licensed contractor's written bid exists, which is the CSLB link's purpose.",
    )
    cap_rows = [
        {"cells": ["Roof and gutters", "Condition unknown; a replacement is an improvement, and for a rental part the capitalized cost depreciates separately.", "Inspection now, then a written bid; decide repair-versus-replace before the transfer if the seller will act on it.", "—"], "status": "Missing", "sources": ["irs_p527_depr", "cslb"]},
        {"cells": ["Water heater, HVAC, appliances", "Routine replacement; deductible as repair or capitalizable as improvement depending on the facts.", "Keep the invoice split by the two categories from year one; the CPA will need it.", "—"], "status": "Missing", "sources": ["irs_p527_depr", "cslb"]},
        {"cells": ["Solar array and inverter (Property A)", "The array is reported to produce a credit rather than a bill; the inverter's service life and any tariff change are not known here.", "Pull the interconnection agreement and the current tariff, and price an inverter replacement into the band.", "—"], "status": "Missing", "sources": ["cpuc_solar", "owner_a"]},
        {"cells": ["Tenant-turn work (Property B)", "Work between tenancies is generally deductible in the year, with the improvement portion capitalized; local rules can also constrain how rent is reset.", "Budget a turn allowance per unit and reconcile against the actual invoices.", "—"], "status": "Missing", "sources": ["irs_p527_depr", "ca_rent"]},
        {"cells": ["Seismic and life-safety", "No official source prices it; it is a structural decision, not a cosmetic one.", "Get the assessment before assuming the building is held for decades.", "—"], "status": "Missing", "sources": ["cslb"]},
        {"cells": ["Insurance-linked repairs", "Coverage, deductibles and nonrenewal risk drive the same physical work; the market for California homeowners coverage is the flagged item on this site.", "Tie the repair plan to the policy: what is not covered is what must be funded from the reserve.", "—"], "status": "Not verified", "sources": ["cdi", "cdi_news"]},
    ]
    body += make_table("Capital items to scope, and why they stay unpriced here", ["Item", "What is known", "Action", "Private figure"], cap_rows, "Deliberately no dollar amounts: an unpriced list of real items is more useful than a fabricated schedule, and every number in this column will come from a bid, not from this site.")
    rerun_rows = [
        {"cells": ["Federal estate and gift amounts", "IRS inflation-adjustment announcement and the Form 706 instructions for the year.", "Re-run the exclusion-headroom table and the liquidity plan.", "irs_2027"], },
        {"cells": ["Capital-gain and line-62 treatment", "FTB capital-gains page and the current Form 540 instructions.", "Re-run the sensitivity band on the sale page.", "ftb_capgain"], },
        {"cells": ["Property tax rules and the family-home exclusion", "BOE Proposition 19 pages and the exclusion-cap letter.", "Re-check the cap amount and the claim deadlines; both move.", "boe_prop19"], },
        {"cells": ["Transfer tax and recording fees", "County Clerk-Recorder fee schedules; San Francisco Assessor-Recorder fee report.", "Reprice both sell paths; check whether the county's inconsistent rate wording has been corrected.", "scc_record_fees"], },
        {"cells": ["Rental and parcel-tax charges", "SFMTA parcel-tax page, Rent Board allowable increase, measure text.", "Update the Prop H table and B's rent assumption.", "sfmta_prop_h"], },
        {"cells": ["Extreme scenarios", "Historical drawdown anchors, CPI, CBO outlook.", "Re-run the black-swan page and this year's investment policy review on the same date.", "fed_1929"], },
    ]
    body += make_table(
        "Annual re-run checklist — same date every year",
        ["Input to refresh", "Authority to read", "What to recompute", "Register row"],
        [{"cells": r["cells"][:3] + [SOURCES[r["cells"][3]]["label"]], "status": "Guidance", "sources": [r["cells"][3]]} for r in rerun_rows],
        "The owner's standing instruction is that this model is re-run every year with updated inputs and that proposed changes are distinguished from enacted law. This checklist is the recurring half of that instruction; the automation that runs the private rebuild is described in the repository's workflow.",
    )
    return render_page(
        "pages/private-file.html",
        "Private file, pre-commitment and annual refresh",
        "The worksheets the decision actually depends on: an estate inventory keyed to the return it must support, a liquidity plan, an investment policy written before the proceeds exist, the pre-agreed rules for choosing a path, a five-year capital plan, and the yearly re-run checklist.",
        body,
        "PREPARE",
    )


def build_page(path: str) -> str:
    builders = {
        "index.html": build_index,
        "pages/executive-summary.html": build_executive_summary,
        "pages/decision-analysis.html": build_decisions,
        "pages/property-profiles.html": build_property_profiles,
        "pages/questions.html": build_questions,
        "pages/projections.html": build_projections,
        "pages/property-tax.html": build_property_tax,
        "pages/operating-costs.html": build_costs,
        "pages/black-swan.html": build_black_swan,
        "pages/phased-investing.html": build_phased_investing,
        "pages/estate-thresholds.html": build_estate_thresholds,
        "pages/inheritance-process.html": build_process,
        "pages/law-watchlist.html": build_law_watchlist,
        "pages/sale-and-transfer.html": build_sale_transfer,
        "pages/rental-economics.html": build_rental_economics,
        "pages/private-file.html": build_private_file,
        "pages/attorney-cpa-brief.html": build_brief,
        "pages/decision-log.html": build_decision_log,
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
