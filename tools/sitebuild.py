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
        "label": "San Jose Water — Peninsula water utility serving the Property A area",
        "url": "https://www.sjwater.com/",
        "scope": "Investor-owned water utility serving several Peninsula communities; publishes tariffs and rate schedules. Provider context only — the household bill depends on metered usage and current approved rates.",
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
    "ftb_gifts": {
        "label": "FTB — Gifts and inheritance (personal income types)",
        "url": "https://www.ftb.ca.gov/file/personal/income-types/gifts-and-inheritance.html",
        "scope": "Read 2026-11-15 (page 'last updated 09/24/2025'). States that a gift or inheritance is not included in income, but income it later produces (interest, dividends, rent, pension, gain on a real-property sale) is taxable. Replaces the retired inheritance-information URL that returned 404.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "ca_rtc17043": {
        "label": "California Revenue and Taxation Code §17043 — 1% tax above $1,000,000",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=17043.&lawCode=RTC",
        "scope": "Read 2026-11-15. Imposes an additional 1% tax on that portion of taxable income in excess of $1,000,000 for taxable years beginning on or after January 1, 2005 (added by Proposition 63, 2004). The amount is a statutory dollar threshold, not indexed in the section text.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "ftb_540es_2025": {
        "label": "FTB — 2025 Instructions for Form 540-ES (Behavioral Health Services Tax worksheet)",
        "url": "https://www.ftb.ca.gov/forms/2025/2025-540-es-instructions.html",
        "scope": "Read 2026-11-15. Worksheet: if taxable income (Form 540 line 19) is more than $1,000,000, subtract $1,000,000 and multiply by 1% for the Behavioral Health Services Tax (previously Mental Health Services Tax). Section C: taxpayers with 2025 California AGI of $1,000,000 or more must base estimated tax on their 2025 tax.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "ftb_cap_gains": {
        "label": "FTB — Capital gains and losses",
        "url": "https://www.ftb.ca.gov/file/personal/income-types/capital-gains-and-losses.html",
        "scope": "Read 2026-11-15 (page 'last updated 01/28/2026'). States: 'California does not have a lower rate for capital gains. All capital gains are taxed as ordinary income.' Gain on a sale of inherited real property is therefore taxed at ordinary California rates in the year of sale.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "boe_countycontacts": {
        "label": "California BOE — Listing of County Assessors, Auditors and Tax Collectors",
        "url": "https://www.boe.ca.gov/proptaxes/countycontacts.htm",
        "scope": "Read 2026-11-15. Official BOE directory of county assessor offices, with links to each county's assessor site. Replaces the retired county-assessor directory URL that returned 404. It lists contacts only; it contains no assessment, rate or parcel data.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "boe_assessor_404": {
        "label": "BOE county-assessor directory URL — retrieval failed (superseded by the BOE contacts listing)",
        "url": "https://www.boe.ca.gov/proptaxes/county-assessors.htm",
        "scope": "Direct retrieval returned a 404 on 2026-11-14 and again on 2026-11-15. Superseded by the BOE county contacts listing above. No local assessor record or local tax rate is inferred from this URL.",
        "verified": False,
    },
    "boe_pub801_404": {
        "label": "BOE Publication 801 URL — retrieval failed",
        "url": "https://www.boe.ca.gov/pdf/pub801.pdf",
        "scope": "Direct retrieval returned a 404 on 2026-11-14. Proposition 19 summaries in this site use the working BOE page and current statute instead.",
        "verified": False,
    },
    "cpuc_water_404": {
        "label": "CPUC water-utilities URL — retrieval failed (superseded by the CPUC water list)",
        "url": "https://www.cpuc.ca.gov/industries-and-topics/water/water-utilities",
        "scope": "Direct retrieval returned a 404 on 2026-11-14 and 2026-11-15. Superseded by the CPUC water and sewer utility list below for listing purposes only. No household water-rate figure is based on this URL.",
        "verified": False,
    },
    "cpuc_water_list": {
        "label": "CPUC — Water Utility List (regulated utilities by service area)",
        "url": "https://docs.cpuc.ca.gov/published/Report/7995.htm",
        "scope": "Read 2026-11-15. Lists the Peninsula supplier named in the private record (WTA 168) with a service area covering several Santa Clara County cities. Place names are omitted here on purpose. The file title is dated '5-7-01', so it confirms only the listing, not current tariffs, rates or service boundaries. A current tariff must come from the utility.",
        "verified": True,
        "checked": "2026-11-15",
    },
    # --- added 2026-11-15 by session arena/79e0fd5e (depreciation, recapture,
    # transaction costs, imputed rent and the San Francisco transfer-tax audit) ---
    "irs_p551_basis": {
        "label": "IRS Publication 551 — Basis of Assets (Inherited Property; Like-Kind Exchanges)",
        "url": "https://www.irs.gov/publications/p551",
        "scope": "Read 2026-11-15. States that the basis of property inherited from a decedent is generally the fair market value at the date of death (or the alternate/special-use valuation), that a Schedule A (Form 8971) estate-tax value can bind a beneficiary's initial basis, and that property the taxpayer or spouse gave the decedent within one year of death keeps the decedent's adjusted basis instead. It also states that a section 1031 exchange requires holding BOTH the real property given up and the real property received for business or investment purposes, with carryover basis. It gives no household value, basis or exchange advice.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_8824": {
        "label": "IRS — About Form 8824, Like-Kind Exchanges",
        "url": "https://www.irs.gov/forms-pubs/about-form-8824",
        "scope": "Read 2026-11-15. Form 8824 reports each exchange of business or investment property for property of a like kind. The page does not state eligibility for a specific property or any deadline arithmetic.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_topic409": {
        "label": "IRS Topic 409 — Capital gains and losses",
        "url": "https://www.irs.gov/taxtopics/tc409",
        "scope": "Read 2026-11-15. States that a gain is the excess over adjusted basis, that inherited property basis refers to Pub 551, that property acquired from a decedent is an exception to the ordinary holding-period rule (see Pub 544), that the portion of gain from selling section 1250 real property attributable to depreciation (unrecaptured section 1250 gain) is taxed at a maximum 25% rate, and that net short-term gain is ordinary. The rate table shown there is for tax year 2025; the 2026 amounts on this site come from the IRS revenue procedure row.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_p527_depreciation": {
        "label": "IRS Publication 527 — Depreciation of rental property (MACRS)",
        "url": "https://www.irs.gov/publications/p527",
        "scope": "Read 2026-11-15. States the MACRS property class 'residential rental property' (real property where 80% or more of the gross rental income is from dwelling units), that an addition to a rental house is depreciated as residential rental property over 27.5 years, that land cannot be depreciated, that basis for depreciation excludes land, and that if the owner lives in part of the building the gross rental income includes the fair rental value of the part occupied. It provides no property-specific basis, split or deduction amount.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "sf_recording_fees": {
        "label": "San Francisco Assessor-Recorder — Fees to record a document in San Francisco",
        "url": "https://www.sf.gov/reports--march-2024--fees-record-document-san-francisco",
        "scope": "Read 2026-11-15 (schedule effective January 1, 2025). Publishes the city-county real-estate transfer tax per $500 of consideration by tier, the recorder's base first-page fee, the per-additional-page fee, the Building Homes and Jobs Act fee with its exemption list, the survey-monument fee that applies only to deeds subject to documentary transfer tax, and the fee charged in lieu of a Preliminary Change of Ownership Report. Rates and fees change; the schedule governs.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "sf_prop_I": {
        "label": "San Francisco — Housing Stability Fund Oversight Board (about)",
        "url": "https://www.sf.gov/departments--housing-stability-fund-oversight-board--about",
        "scope": "Read 2026-11-15. States that in November 2020 San Francisco voters passed Proposition I, changing the city-county property transfer tax on the two highest consideration tiers — from 2.75% to 5.5% on properties valued between ten million and just under twenty-five million dollars, and from 3% to 6% at twenty-five million dollars or more — with the revenue handled through the Housing Stability Fund and the General Fund. It says nothing about a transfer below those tiers and is not the operative ordinance text.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "scc_dtt_unverified": {
        "label": "Santa Clara County transfer-tax and recording schedule — not retrieved",
        "url": "https://www.santaclaracounty.gov/",
        "scope": "Attempted 2026-11-15. No county page with the documentary-transfer-tax rate, the recording fee schedule or the exemption list was retrieved in this sandbox, so no Santa Clara County transaction-cost figure is published anywhere on this site and the sell-path row for Property A stays blank.",
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
    "region": "Santa Clara County, California (place anonymised; county named only because the assessor's rule is county-level)",
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
    "region": "City and County of San Francisco (place anonymised; the city-county is named only because its transfer-tax and rent rules are the governing ones)",
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
# Privacy dial (owner-facing, added 2026-11-15).
# A year-by-year assessed-value series is the single most re-identifiable thing
# this site publishes: the dollar level can be matched against a county roll
# even after $10 rounding. Setting PUBLISH_ASSESSMENT_LEVELS to False keeps the
# growth rates the decision actually depends on but publishes them indexed to
# 2014 = 100, with no dollar levels anywhere. One constant, both modes build and
# verify clean.
# ---------------------------------------------------------------------------
PUBLISH_ASSESSMENT_LEVELS = True


def assessed_cell(table: dict[int, float], year: int, base_year: int = 2014) -> str:
    """Publish an assessed value as a dollar level or, in indexed mode, as an index."""
    value = table.get(year)
    if value is None:
        return "—"
    if PUBLISH_ASSESSMENT_LEVELS:
        return money10(value)
    base = table[base_year]
    return f"index {value / base * 100:.1f}"


# ---------------------------------------------------------------------------
# Depreciation, recapture and transaction-cost model (session arena/79e0fd5e,
# 2026-11-15). Every input below is either a published official rule (linked in
# SOURCES) or a labeled assumption; every output goes through money10().
# ---------------------------------------------------------------------------
DEPR_YEARS = 27.5            # MACRS residential-rental recovery period (IRS Pub 527, read 2026-11-15)
BUILDING_SHARE_LOW = 0.55    # assumption: depreciable building share of basis
BUILDING_SHARE_HIGH = 0.75   # (land is never depreciable; use the assessor's split)
UNRECAPPED_1250_RATE = 0.25  # maximum federal rate on unrecaptured section 1250 gain (IRS Topic 409)
CA_MARGINAL_HIGH = 0.138     # assumption: top-ish California ordinary rate used only to show direction
FED_LTCG_HIGH = 0.20         # 20% top net capital-gain rate above the 15% band (IRS Topic 409)
SECTION_121_SINGLE = 250_000   # IRC 121 main-home exclusion, single filer (IRS Topic 701)
SECTION_121_JOINT = 500_000    # IRC 121 main-home exclusion, qualifying joint return
SF_TT_TIERS = [                # San Francisco real-estate transfer tax, official per-$500 schedule
    (250_000, 2.50),
    (1_000_000, 3.40),
    (5_000_000, 3.75),
    (10_000_000, 11.25),
    (25_000_000, 27.50),
    (float("inf"), 30.00),
]
SF_TT_RATE_TEXT = {2.50: "0.50%", 3.40: "0.68%", 3.75: "0.75%", 11.25: "2.25%", 27.50: "5.50%", 30.00: "6.00%"}


def sf_transfer_tax(value: float) -> tuple[float, str]:
    """San Francisco charges the tier rate on the ENTIRE consideration, not marginally."""
    for ceiling, per_500 in SF_TT_TIERS:
        if value <= ceiling or ceiling == float("inf"):
            return (value / 500.0) * per_500, SF_TT_RATE_TEXT[per_500]
    raise AssertionError("unreachable")


def b_depreciation(share: float) -> dict:
    """One year of straight-line MACRS on Property B, plus the recapture it creates."""
    basis = PROPERTY_B["value_2026"] * share
    annual = basis / DEPR_YEARS
    ten_year = annual * 10
    return {
        "share": share,
        "basis": basis,
        "annual": annual,
        "ten_year": ten_year,
        "fed_recapture": ten_year * UNRECAPPED_1250_RATE,
        "ca_tax": ten_year * CA_MARGINAL_HIGH,
        "shelter_now": annual * (FED_LTCG_HIGH + CA_MARGINAL_HIGH),
    }


def live_then_sell_exclusion(hold_years: int = 10) -> dict:
    """Gain above the date-of-death basis, and the IRC 121 shield on a lived-in home."""
    gain = a_value(INHERIT_YEAR + hold_years) - a_value(INHERIT_YEAR)
    return {
        "hold_years": hold_years,
        "gain": gain,
        "shielded_single": min(gain, SECTION_121_SINGLE),
        "excess_single": max(gain - SECTION_121_SINGLE, 0.0),
        "excess_joint": max(gain - SECTION_121_JOINT, 0.0),
    }


def sell_path_costs(value: float) -> dict:
    """Price the transaction lines a gross-to-net bridge usually forgets."""
    tt, tt_rate = sf_transfer_tax(value)
    return {
        "commission": value * SELL_COST * 0.6,          # assumption: split of the 7% band
        "other_closing": value * SELL_COST * 0.4,        # assumption: title, escrow, prep
        "sf_transfer_tax": tt,
        "sf_transfer_tax_rate": tt_rate,
        "recording": 20.0 + 14.0 + 3.0,                   # SF Assessor-Recorder schedule, read 2026-11-15
        "pcor_fee": 20.0,                                  # fee in lieu of a PCOR, RTC 480.3(b)
    }


def outcome_distribution() -> dict:
    """A 10-year spread for the sale-and-reinvest path across labelled scenario bands.

    Not a forecast: a grid of growth/inflation pairs, each equally weighted, so
    the reader sees the width of the outcome instead of one point. Values are
    index numbers (start = 100) and $10-rounded dollars.
    """
    proceeds = SELL_NET_2045
    grid = []
    for growth in (0.02, 0.04, 0.06, 0.08, 0.10):
        for inflation in (0.015, 0.025, 0.035):
            nominal = proceeds * (1 + growth) ** 10
            real = nominal / (1 + inflation) ** 10
            grid.append((nominal, real))
    nominal_sorted = sorted(g[0] for g in grid)
    real_sorted = sorted(g[1] for g in grid)

    def quantile(values: list[float], q: float) -> float:
        index = min(len(values) - 1, max(0, int(round(q * (len(values) - 1)))))
        return values[index]

    return {
        "count": len(grid),
        "nominal": {q: quantile(nominal_sorted, q) for q in (0.0, 0.25, 0.5, 0.75, 1.0)},
        "real": {q: quantile(real_sorted, q) for q in (0.0, 0.25, 0.5, 0.75, 1.0)},
        "hold_value_10y": a_value(INHERIT_YEAR + 10),
        "hold_tax_10y": DELTA_10YR,
    }


def svg_distribution(quantiles: dict[float, float], caption: str) -> str:
    """Render the spread as inline SVG bars — no script, no remote asset, no data file."""
    low, high = quantiles[0.0], quantiles[1.0]
    span = max(high - low, 1.0)
    labels = {0.0: "worst", 0.25: "25th", 0.5: "median", 0.75: "75th", 1.0: "best"}
    bars = []
    for i, q in enumerate((0.0, 0.25, 0.5, 0.75, 1.0)):
        height = max(6.0, (quantiles[q] - low) / span * 92.0 + 6.0)
        x = 12 + i * 58
        bars.append(
            f'<rect x="{x}" y="{110 - height:.1f}" width="40" height="{height:.1f}" rx="3" '
            f'fill="currentColor" opacity="{0.35 + 0.13 * i:.2f}"/>'
            f'<text x="{x + 20}" y="126" text-anchor="middle" class="chart-label">{esc(labels[q])}</text>'
            f'<text x="{x + 20}" y="{max(10, 104 - height):.1f}" text-anchor="middle" class="chart-value">'
            f'{money10(quantiles[q])}</text>'
        )
    summary = ", ".join(f"{labels[q]} {money10(quantiles[q])}" for q in (0.0, 0.5, 1.0))
    return (
        f'<figure class="chart" role="img" aria-label="Outcome spread: {esc(summary)}">'
        f'<svg viewBox="0 0 310 140" preserveAspectRatio="xMidYMid meet" aria-hidden="true" '
        f'focusable="false">{"".join(bars)}'
        f'<line x1="6" y1="112" x2="304" y2="112" stroke="currentColor" stroke-width="1" opacity="0.5"/></svg>'
        f'<figcaption>{esc(caption)}</figcaption></figure>'
    )




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


STAGING_SCENARIOS = [
    # (label, drawdown, pre-crash drift, trough months, crash start month or None)
    ("Steady market: 8%/yr drift, no crash", 0.0, 0.08, 0, None),
    ("Flat market: 0% drift, no crash", 0.0, 0.0, 0, None),
    ("2008-style 57% decline BEGINS month 15 (during staging)", 0.57, 0.0, 17, 15),
    ("2008-style 57% decline BEGINS month 40 (after staging ends)", 0.57, 0.0, 17, 40),
    ("1929-style 89% decline BEGINS month 15 (during staging)", 0.89, 0.0, 36, 15),
    ("1929-style 89% decline BEGINS month 40 (after staging ends)", 0.89, 0.0, 36, 40),
    ("1929-style decline after a 2-year rise, from month 30", 0.89, 0.08, 36, 30),
]


def staging_table_rows(status: str = "Assumption") -> list[dict]:
    """Lump-sum versus 24/36-month Treasury staging, with the softening effect made explicit.

    Each row is computed from the same synthetic index path, so the comparison is
    internal to the model: staging can only help when the decline starts while some
    of the money is still in Treasuries, and it always costs ground in a rising market.
    """
    rows = []
    for label, drawdown, drift, trough, crash in STAGING_SCENARIOS:
        horizon = max(60, (crash or 0) + trough)
        lump = staging_model(SELL_NET_2045, 0, drawdown, trough, drift, 0.0, 0.0, crash, min_horizon=horizon)[1]
        best = None
        cells = [label, money10(lump)]
        for months in (24, 36):
            staged, _reserve = staging_model(SELL_NET_2045, months, drawdown, trough, drift, STAGING_YIELD * 100, STAGING_YIELD * 100, crash, min_horizon=horizon)
            cells.append(money10(staged))
            gap = staged - lump
            best = gap if best is None else max(best, gap)
        cells.append(("about " + money10(best) + " better than lump sum" if best and best > 0
                      else "no gain over lump sum in this path"))
        rows.append({"cells": cells, "status": status,
                     "sources": ["treasury_bills", "treasury_notes", "cbo_rates", "fed_2008", "fed_1929"]})
    return rows


def staging_rows() -> list[dict]:
    rows = []
    for label, drawdown, drift, trough, crash in STAGING_SCENARIOS:
        horizon = max(36, (crash or 0) + trough)
        lump = staging_model(SELL_NET_2045, 0, drawdown, trough, drift, 0.0, 0.0, crash, min_horizon=horizon)[1]
        p24 = staging_model(SELL_NET_2045, 24, drawdown, trough, drift, STAGING_YIELD * 100, STAGING_YIELD * 100, crash, min_horizon=horizon)[0]
        p36 = staging_model(SELL_NET_2045, 36, drawdown, trough, drift, STAGING_YIELD * 100, STAGING_YIELD * 100, crash, min_horizon=horizon)[0]
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
        ("pages/capital-and-tax-model.html", "Depreciation, fees & capital plan"),
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
        ("pages/decision-log.html", "Decision log"),
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
    "pages/capital-and-tax-model.html",
    "pages/operating-costs.html",
    "pages/black-swan.html",
    "pages/phased-investing.html",
    "pages/estate-thresholds.html",
    "pages/inheritance-process.html",
    "pages/law-watchlist.html",
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
        {"cells": ["Insurance, repairs and utilities", "Official public sources do not determine a private premium, repair budget, water bill or solar credit.", "Obtain separate written owner-occupied / landlord insurance quotes, inspection bids, utility bills and solar tariff documents."], "status": "Missing", "sources": ["cdi", "cslb", "water_board", "cpuc_solar"]},
        {"cells": ["The rent a live-in path avoids, and the recapture a rented building carries", "Living in Property A avoids a market rent that is not published or verified anywhere on this site; renting Property B accumulates depreciation that returns as unrecaptured section 1250 gain at a maximum 25% federal rate, with California taxing the whole gain as ordinary income.", "Enter an avoided-rent figure in the what-if control below (local only) and have the CPA produce the depreciation schedule and land/building split for each building before any sell-versus-hold ranking is final."], "status": "Missing", "sources": ["irs_p527_depreciation", "irs_topic409", "ftb_cap_gains", "hud_fmr"]},
        {"cells": ["Investment entry and reinvestment risk", "A 24–36 month Treasury staging plan changes exposure timing but adds reinvestment risk if yields fall; equity prices can fall during or after staging.", "Use the local-only stress tool, replace its explicit assumptions with then-current net yields, and compare crash-during-wait with crash-after-wait."], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
        {"cells": ["Long-range law and market conditions", "No official source can verify future estate thresholds, property values, insurance costs, rent or returns decades ahead.", "Re-check enacted law, official bills, valuations and quotes close to the transfer; do not extrapolate a single rate for fifty years."], "status": "Missing", "sources": ["irs_2027", "cbo_rates", "fhfa_hpi"]},
    ]
    body = callout(
        "Conditional best plan under the baseline assumptions (owner-supplied, privacy-rounded figures)",
        "Live in Property A after the transfer and claim the family-home exclusion: occupy within one year, file the homeowners' exemption within one year, and file the intergenerational claim within three years. At the modeled 2045 transfer this preserves the long-held base and costs about " + money10(a_tax_exclusion(2045)) + " per year in property tax, versus about " + money10(a_tax_reassessed(2045)) + " per year if the home is instead reassessed — a difference of about " + money10(DELTA_2045) + " every year, about " + money10(DELTA_10YR) + " over the first ten years. Keep Property B as is: its rental income continues under either choice. Selling A instead nets about " + money10(SELL_NET_2045) + " after assumed sale costs and moves the decision from property tax to reinvestment risk. REINVESTMENT RISK, BESIDE THE HEADLINE: any sale proceeds parked in 3-month-to-2-year Treasuries for 24-36 months earn the then-current auction rate, which may be lower at each renewal; staged buying also lags a rising market. Two more omissions sit on the other side of the ledger and are now modelled on the depreciation-and-fees page: a live-in path is owed credit for the rent it does not pay, and any sale must clear transfer tax, recording charges and, for a rented building, the depreciation clawback before the proceeds are investable.",
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
        ("3b. Price the taxes and frictions", "Depreciation and recapture, transfer tax and recording charges, the §121 switch, imputed rent and the five-year capital plan.", "pages/capital-and-tax-model.html"),
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
    gap_rows = [
        {"cells": ["Depreciation and its clawback", "A rented building deducts its building value straight-line over the published 27.5-year class; land never depreciates. Unrecaptured section 1250 gain is taxed at a maximum 25% federal rate, and California taxes the whole gain as ordinary income.", "Every rental path in the comparison was overstated until now, because the deduction stream was counted and the repayment was not. The exposure is largest on the already-owned building, which has years of accumulated depreciation and will not receive a new basis at the future transfer."], "status": "Verified", "sources": ["irs_p527_depreciation", "irs_topic409", "ftb_cap_gains"]},
        {"cells": ["Transaction costs between price and cash", "The city-county transfer tax charges its tier rate on the ENTIRE consideration, with a per-$500 schedule, recording charges on top, and a fee in lieu when the change-of-ownership screening form is missing.", "On the already-owned building the modelled transfer tax alone is about " + money10(sf_transfer_tax(PROPERTY_B["value_2026"])[0]) + " — real money that the headline 'net proceeds' figure must carry before it is compared with a held house."], "status": "Verified", "sources": ["sf_recording_fees"]},
        {"cells": ["Imputed rent on the live-in path", "A household that owns and occupies pays no rent; that avoided rent is the largest unpriced benefit in the comparison and the market rent for the anticipated-trust property is unknown here.", "The comparison is now run both ways in the local what-if control, so the reader can see exactly how much of path 1's advantage is housing it does not have to buy."], "status": "Missing", "sources": ["hud_fmr", "irs_p527_depreciation"]},
        {"cells": ["Outcome spread rather than a point", "The sell-and-reinvest path is published as a distribution across the assumption grid, with worst, quartiles and best, plus the certainty term the grid omits (the property-tax saving of holding).", "A single projected ending value was the weakest claim on the site; the spread shows the ranking is not robust to the tails, which is the honest finding."], "status": "Projection", "sources": ["sec_stocks", "cbo_ltbo", "bls_cpi"]},
        {"cells": ["Capital plan for both buildings", "A five-year inspection-driven plan with per-item bands and a monthly sinking-fund target, distinguishing repairs (deducted now) from improvements (capitalised and depreciated).", "The 'low carrying cost' of the hold path assumes maintenance actually happens; funding it is what separates a real holding cost from a deferred one."], "status": "Assumption", "sources": ["irs_p527_depreciation", "cslb"]},
        {"cells": ["Privacy enforcement, not just policy", "A committed maintenance script had stored the exact pre-rounding figures next to their rounded forms, which would have let anyone re-identify the records the rounding protects. It is removed, and the verifier now fails on any comma-grouped amount that is not a multiple of ten dollars and on any mapping pattern anywhere in the tree.", "The published site also no longer names the ZIP codes, city or neighbourhood; the residual risk is the assessed-value series itself, and a one-constant switch (PUBLISH_ASSESSMENT_LEVELS) publishes it as an index instead."], "status": "Guidance", "sources": ["github_history"]},
    ]
    body += make_table("What this release adds to the conclusion", ["Gap now closed", "Rule or method, with its source", "Effect on the decision"], gap_rows, "Each line is a cost or benefit the headline ranking previously ignored. None of them changes the direction of the recommendation by itself; together they change how much confidence the ranking deserves.")
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
        "Baseline: 2045 transfer, owner-supplied rounded figures, 4% market-growth scenario, 2% assessed-value cap, derived effective rates, 3% exclusion indexing, 7% assumed sale costs, 35% assumed rent load. Under those assumptions the property-tax lever dominates: exclusion-claimed A costs about " + money10(a_tax_exclusion(2045)) + " per year at 2045 versus about " + money10(a_tax_reassessed(2045)) + " reassessed, and B's " + money10(PROPERTY_B["rent_month"]) + " per month of gross rent continues under every path. Ranking: 1) live in A with the family-home exclusion claimed and keep B rented; 2) rent A only if written rent comparables exceed the derived hurdle (about " + money10(RENT_HURDLE_MONTH) + " per month gross); 3) sell A (about " + money10(SELL_NET_2045) + " net after assumed costs) and stage the proceeds — competitive only after counting where the household lives and the reinvestment risks on the black-swan page. The ranking flips if the exclusion fails, if rent comps beat the hurdle, or if the household's housing cost in the sell path is small. Reinvestment risk belongs beside headline 3: staged Treasuries earn an unknown renewal rate each rung, and staged buying lags a rising market.",
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
                   "Net proceeds about " + money10(SELL_NET_2045) + " after assumed 7% sale costs; inherited basis is generally date-of-death value, so near-term gain is small",
                   "At the 6% assumed return the proceeds reach about " + money10(SELL_NET_2045 * (1 + REINVEST_RETURN) ** 10) + " in ten years — but path 1's house grows too, and path 3 must also pay for housing elsewhere",
                   "Reinvestment risk beside the headline: staged 3M-2Y Treasuries renew at unknown rates; a crash during or after staging changes the outcome materially (see the staging table)."],
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
        {"cells": ["4 — Sell A in the same tax year as the transfer",
                   "Inherited basis is generally the date-of-death value, so a same-year sale has little or no gain to tax; the estate value and the income-tax basis are still separate calculations",
                   "Surrenders the exclusion entirely: the tax advantage of holding is about " + money10(DELTA_10YR) + " over the first ten years, which no same-year tax saving offsets",
                   "Only wins if the household will not occupy the home, or if carrying costs, insurance and repairs exceed the value of holding; confirm the consistent-basis rule (Schedule A, Form 8971) with the CPA."],
         "status": "Projection", "sources": ["irs_p551_basis", "ca_rtc63", "boe_prop19"]},
        {"cells": ["M4 — Live in A, rent B's vacant unit, and count the rent the household does not pay",
                   "Exclusion branch as in path 1, plus an imputed-rent credit for the housing the household stops buying; the credit is unknown on this site and is left blank rather than guessed",
                   "Path 1 stops looking free-and-clear: without the imputed-rent credit, a sell-and-reinvest path is unfairly compared against a housing benefit it does not receive",
                   "A comparison device, not income; the entry belongs in the what-if control below, together with the recapture B carries into any sale."],
         "status": "Guidance", "sources": ["irs_p527_depreciation", "hud_fmr", "irs_topic409"]},
        {"cells": ["M3 — Sell B instead (keep A)",
                   "B's sale is a taxable event on B's own low basis (about " + money10(PROPERTY_B["assessed"][2025]) + " assessed is not income-tax basis); gain could be large",
                   "Loses the " + money10(PROPERTY_B["rent_month"]) + " per-month gross rent stream; changes the household's residence plan",
                   "B's income-tax basis is unknown and unverified — do not model this path without it, and add the depreciation already taken: it returns as unrecaptured section 1250 gain at a maximum 25% federal rate plus California ordinary tax."],
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
<p class="table-note">Adjust the assumptions and the key numbers recompute in this browser. Defaults mirror the published baseline. Nothing is stored or transmitted; the tool does not calculate income tax, insurance, maintenance or rent.</p>
<form id="path-tool" class="tool-grid">
<label>Market value at transfer<input id="path-value" type="number" min="0" max="99999999" step="10" value="6531230" inputmode="numeric"></label>
<label>Assessed base carried over<input id="path-base" type="number" min="0" max="99999999" step="10" value="802030" inputmode="numeric"></label>
<label>Effective tax rate (%)<input id="path-rate" type="number" min="0" max="5" step="0.01" value="1.34" inputmode="decimal"></label>
<label>Assessed-value growth cap (%)<input id="path-cap" type="number" min="0" max="10" step="0.1" value="2" inputmode="decimal"></label>
<label>Prop 19 exclusion at transfer<input id="path-excl" type="number" min="0" max="99999999" step="10" value="1886640" inputmode="numeric"></label>
<label>Rent operating load (%)<input id="path-load" type="number" min="0" max="90" step="1" value="35" inputmode="decimal"></label>
<label>Imputed rent while living in A ($/year)<input id="path-imputed" type="number" min="0" max="500000" step="10" value="0" inputmode="numeric"></label>
<label>Recapture exposure carried by B ($, 0 = none modelled)<input id="path-recapture" type="number" min="0" max="9999999" step="10" value="0" inputmode="numeric"></label>
<label>Sell-path transaction costs (%)<input id="path-sellcost" type="number" min="0" max="20" step="0.1" value="7" inputmode="decimal"></label>
<div class="tool-actions no-print"><button id="path-reset" type="button">Reset to baseline</button><span class="tool-assumption">Derived values are rounded to the nearest $10 in the display.</span></div>
</form>
<div class="scenario-grid" aria-live="polite">
<article class="scenario-card"><h3>Exclusion claimed (live in A)</h3><dl><dt>Property tax, year 1</dt><dd id="path-tax-excl">—</dd><dt>Property tax, year 10</dt><dd id="path-tax-excl10">—</dd><dt>Ten-year cumulative</dt><dd id="path-tax-exclcum">—</dd></dl></article>
<article class="scenario-card"><h3>Reassessed (rent or sell branch)</h3><dl><dt>Property tax, year 1</dt><dd id="path-tax-re">—</dd><dt>Property tax, year 10</dt><dd id="path-tax-re10">—</dd><dt>Ten-year cumulative</dt><dd id="path-tax-recum">—</dd></dl></article>
<article class="scenario-card"><h3>Branch difference</h3><dl><dt>Annual difference, year 1</dt><dd id="path-delta1">—</dd><dt>Ten-year cumulative difference</dt><dd id="path-delta10">—</dd><dt>Rent hurdle per month</dt><dd id="path-hurdle">—</dd></dl></article>
<article class="scenario-card"><h3>Live-in benefit and sell-path frictions</h3><dl><dt>Imputed rent, ten years</dt><dd id="path-imputed10">—</dd><dt>Live-in path, adjusted</dt><dd id="path-liveadj">—</dd><dt>Sell net after costs</dt><dd id="path-sellnet2">—</dd><dt>Sell net less recapture</dt><dd id="path-selladj">—</dd></dl></article>
<article class="scenario-card"><h3>Sell branch</h3><dl><dt>Net proceeds (7% costs)</dt><dd id="path-sellnet">—</dd><dt>Proceeds at 6%/yr, year 10</dt><dd id="path-sell10">—</dd><dt>Reinvestment risk</dt><dd>see black-swan page</dd></dl></article>
</div>
<p id="path-status" class="tool-status" role="status">Change a control to rerun the local comparison.</p>
<p class="table-note">Model: exclusion branch taxes the carried-over base grown at the cap; reassessed branch taxes (market value minus exclusion) grown at the cap; both at the entered effective rate. The rent hurdle divides the ten-year difference by ten years, twelve months, and (1 − load). Sale branch subtracts the entered transaction-cost percentage and compounds 6%/yr, both labeled assumptions. Imputed rent is added to the live-in branch as the rent the household does not pay; it is a comparison device, not income. The recapture line subtracts the depreciation clawback a landlord carries into a sale (see the depreciation page) so the sell-versus-hold comparison is on the same footing. This is not tax advice.</p>
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
        {"cells": ["Q16 — What has been depreciated on B, and what does that create at sale?", "No depreciation schedule, acquisition basis, land/building allocation or accumulated-depreciation figure is published; the site shows only a labelled 27.5-year illustration.", "Publication 527 sets the residential-rental class and excludes land from depreciation; Topic 409 caps unrecaptured section 1250 gain at a maximum 25% federal rate; California has no lower rate for capital gains. The dollar exposure is unknowable without the return.", "Depreciation schedules (Form 4562) for every year, the acquisition statement, the land/building split, improvement history, and a CPA-prepared recapture figure at a sale-price band.", "CPA"], "status": "Missing", "sources": ["irs_p527_depreciation", "irs_topic409", "ftb_cap_gains"]},
        {"cells": ["Q17 — Does the heir live in A long enough for the main-home exclusion to matter?", "The owner's occupancy plan is not stated beyond a general preference, and the two-out-of-five-year ownership and use tests are facts, not assumptions.", "The exclusion is up to $250,000 ($500,000 qualifying joint return) of gain and only for a main home; a path that rents A immediately generally cannot use it, and whether the decedent's ownership period counts toward the ownership test is not verified on this site.", "A dated occupancy plan, the intended sale year, prior use of the exclusion by the heir within five years, and a written CPA note on the tacking question.", "CPA"], "status": "Missing", "sources": ["irs_121", "irs_topic701"]},
        {"cells": ["Q18 — What is a transfer actually going to cost to execute?", "The city-county transfer-tax schedule and recording fees are published by the recorder and are modelled here; the county schedule for the anticipated-trust property could not be retrieved in this sandbox, so its sell-path cost stays blank.", "The city charges the tier rate on the ENTIRE consideration, so a price just below a tier boundary is materially cheaper to sell at. A missing PCOR also carries its own fee.", "The county transfer-tax ordinance and recording fee schedule, the recorder's written position on whether a transfer at death is exempt from documentary transfer tax, and a closing estimate from an escrow officer.", "Escrow / attorney"], "status": "Partly verified", "sources": ["sf_recording_fees", "scc_dtt_unverified", "ca_rtc480"]},
        {"cells": ["Q19 — Is a like-kind exchange wanted at all?", "Nothing in the record states an intent to exchange; the rules are cited but no eligibility determination is made.", "Section 1031 requires both the property given up and the property received to be held for business or investment, and the replacement basis generally carries over — it defers tax, it does not erase it, and the deferred gain arrives with a smaller depreciation base.", "A written adviser note on whether the inherited home or the existing rental could be held for investment at the relevant time, plus the 45/180-day mechanics and a qualified intermediary's terms, before any sale is listed.", "CPA / attorney"], "status": "Missing", "sources": ["irs_p551_basis", "irs_8824"]},
        {"cells": ["Q20 — What is the estate's liquidity position if the estate approaches the federal exclusion?", "No estate inventory, cash position, debt schedule or liquidity plan is published; the estate-level test is described but not computed.", "California imposes no death tax under current RTC §13301, so the liquidity question is federal and about timing: a filing threshold is not the same as tax due, and a portability election can require a return below it.", "Asset and debt inventory, insurance and retirement beneficiary designations, cash reserves, the 9-month Form 706 calendar, and a written plan for paying any tax without a forced property sale.", "CPA / estate attorney"], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq", "ca_rtc13301"]},
        {"cells": ["Q21 — What has actually been tried, decided and dated? (decision discipline)", "The decision log records choices with dates so a future reader can see what was decided and why, and the review queues record what has been selected for testing.", "Pre-committing the criteria is the only defence against reverse-engineering an outcome from one projection: write down what would make the household choose each path before the figures arrive.", "A signed, dated one-page statement of the decision criteria and reversal conditions, kept with the private records; update it whenever a criterion changes.", "Household"], "status": "Guidance", "sources": ["github_history"]},
    ]
    body = callout("Answers are bounded by evidence", "The case structure (one anticipated trust transfer, one already-owned property) and the owner-supplied rounded figures are carried into the public site. Law and public market data are linked; anything the owner has not supplied stays blank, and each blank row names the record and professional who can close it. Suggestions for discovering missing information appear in the final column of every row.", "info")
    body += make_table("Questions, information required and answer status", ["Question", "Information available", "Answer from verified evidence", "Record needed to close the gap", "Who should confirm"], rows, "Status Owner-supplied means only that the broad role appeared in the request; the official source link verifies the cited rule, not the household fact.")
    body += paragraph("Discovery order", "First collect trust and title records, then confirm estate valuation/basis and property-tax deadlines, then verify lawful use and leases, then request independent insurance/repair/utility data, and only then compare after-tax alternatives.")
    return render_page("pages/questions.html", "Questions & missing evidence", "A clear register of what is known at a high level, what is not established, and the document or official rule needed to resolve each question.", body, "DECISION")


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
    dist = outcome_distribution()
    spread_rows = []
    for label, key in (("Nominal ending value", "nominal"), ("Purchasing-power (real) ending value", "real")):
        for q, qname in ((0.0, "Worst in grid"), (0.25, "25th percentile"), (0.5, "Median"), (0.75, "75th percentile"), (1.0, "Best in grid")):
            value = dist[key][q]
            spread_rows.append({
                "cells": [label, qname, f"{value / SELL_NET_2045:.2f}×", money10(value)],
                "status": "Projection",
                "sources": ["sec_stocks", "cbo_ltbo", "bls_cpi"],
            })
    spread_rows.append({
        "cells": ["Hold Property A instead — market value at year 10", "Baseline 4% value scenario", f"{dist['hold_value_10y'] / SELL_NET_2045:.2f}×", money10(dist["hold_value_10y"])],
        "status": "Projection", "sources": ["owner_a", "fhfa_hpi", "cbo_ltbo"],
    })
    spread_rows.append({
        "cells": ["Hold Property A instead — property-tax saving vs reassessed branch, ten years", "Exclusion claimed vs not claimed", "n/a", money10(dist["hold_tax_10y"])],
        "status": "Projection", "sources": ["ca_rtc63", "boe_prop19", "owner_a"],
    })
    body += make_table(
        "Outcome spread for the sell-and-reinvest path, ten years from the modelled transfer (distribution, not a point)",
        ["Measure", "Position in the grid", "Multiple of net proceeds", "Privacy-rounded value"],
        spread_rows,
        "The grid is every combination of a 2%-10% nominal return and 1.5%-3.5% inflation, ten years, equally weighted — " + str(dist["count"]) + " scenarios, no probabilities assigned. It shows the width of the range a single '6% a year' headline hides: the same money can end anywhere in the band, and the hold path's tax saving is a certainty term that the band does not contain. Not a forecast.",
    )
    body += '<section class="table-section"><h2>Spread at a glance</h2>' + svg_distribution(
        dist["real"],
        "Real (purchasing-power) ending value across the modelled grid, worst to best; index of one, not a probability.",
    ) + svg_distribution(
        dist["nominal"],
        "Nominal ending value across the same grid, worst to best; the gap between the two charts is inflation.",
    ) + '</section>'
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
    carry_rows = []
    for year in (2027, 2040, 2045, 2050):
        amt = excl_amount(year)
        carry_rows.append({
            "cells": [year,
                      money10(amt),
                      f"{money10(a_assessed(year))} + {money10(amt)}",
                      money10(min(a_value(year), a_assessed(year) + amt)),
                      "Official amount for 2025-02-16 to 2027-02-15 is $1,044,586, adjusted every two years by the FHFA California house-price index; later years here are this site's 3%-per-year assumption, not a published forecast."
                      if year != 2027 else
                      "Official BOE amount for the window ending 2027-02-15; the next adjustment is due 2027-02-16."],
            "status": "Verified" if year == 2027 else "Projection",
            "sources": ["boe_lta_2025_009", "ca_rtc63", "owner_a"],
        })
    body += make_table(
        "The Proposition 19 allowance carried forward to each candidate transfer year",
        ["Transfer year", "Adjusted value-limit amount", "Base carried over plus the allowance (modelled)", "Assessment the heir could keep, capped at value", "Basis of the amount"],
        carry_rows,
        "The family-home exclusion does not carry the old low assessment across whole: it carries the transferor's factored base year value plus an adjusted allowance, and the excess of market value over that sum is added to the new base. The allowance is therefore the single number that decides how much of the low base survives — and it grows on a published, biennial, index-driven schedule this site can only project as a labeled assumption. Two further checks belong with the assessor, not with a model: whether the transferor had already used a family-home exclusion on this property (a prior claim reduces what is left), and whether the property's value exceeds the limit at all.",
    )
    carry_flag_rows = [
        {"cells": ["Prior use of the allowance on the same property", "A parent-child exclusion claimed earlier reduces the amount available at a later transfer of the same home.", "Not modelled here: it depends on the parcel's claim history, which is an assessor record, not a public statistic.", "Request the assessor's written history of exclusions on the parcel before assuming the full allowance is available."], "status": "Missing", "sources": ["ca_rtc63", "boe_prop19"]},
        {"cells": ["Second-and-subsequent transfers", "The statute limits the total excluded value across successive transfers of the same family home; the site does not attempt to model a grandchild generation.", "Any plan that assumes a further transfer after the heir must be priced with the reduced allowance, not the current one.", "Confirm the treatment with the assessor in writing at the time of the first transfer, and keep the determination with the trust records."], "status": "Missing", "sources": ["ca_rtc63", "boe_prop19"]},
        {"cells": ["Occupancy long enough to be worth claiming", "The relief is conditional on the heir occupying the home as a principal residence and filing the homeowners' exemption within one year; renting it instead forfeits the condition and the base resets toward market value.", "Claiming the exclusion is only rational for a household that will actually live there for a long period; a short occupancy to capture the benefit is the fact pattern the statute is written against.", "Put the intended occupancy period in writing before the transfer, with the reversal condition recorded in the decision log."], "status": "Verified", "sources": ["ca_rtc63", "boe_prop19", "ca_rtc218"]},
    ]
    body += make_table("What the carried-forward allowance depends on, and what this site cannot see", ["Dependency", "Rule", "Why it cannot be modelled from public data", "Action that closes it"], carry_flag_rows)
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
        "Owner-supplied monthly figures appear on the property-profiles page, rounded to the nearest ten dollars and badged Owner-supplied (privacy-rounded). No official source can produce an insurance premium or repair bid for a private home, so those cells stay unverified until written quotes and bids exist. Provider context: the Property A area water utility publishes its own tariffs, and third-party compilations of CPUC data put the mid-2026 PG&E residential average near 33.7 cents per kWh.",
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
    body += make_table(
        "Crash-entry test for the phased path, in modelled dollars (net proceeds about " + money10(SELL_NET_2045) + ")",
        ["Entry scenario", "Lump sum at receipt", "24-month Treasury staging", "36-month Treasury staging", "Best staging result vs lump sum"],
        staging_table_rows(),
        "The decline magnitudes are the Federal Reserve History anchors (57% in 2007-09, 89% in 1929); the timing, the straight-line path, the horizon and the 4.3% reserve yield are model assumptions, not history. Staging only helps when the decline begins while part of the money is still in Treasuries — the 'after staging ends' rows exist to show that, and a rising market costs the staged plan ground. This is a stress illustration, not a backtest, a probability or investment advice.",
    )
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
    static_rows = staging_table_rows()
    body += make_table(
        "Staging compared in dollars — modeled net proceeds of about " + money10(SELL_NET_2045) + " (baseline assumptions)",
        ["Entry scenario", "Lump sum (invest all at receipt)", "24-month staging", "36-month staging", "Best staging result vs lump sum"],
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
        {"cells": ["California income tax — 1% Behavioral Health Services Tax", "1% of taxable income above $1,000,000 in a taxable year (RTC §17043; FTB 2025 Form 540-ES worksheet). The $1,000,000 is a fixed statutory amount in the section text.", "The inheritance itself is not income. The surcharge applies to income in the year of a sale or other income event that pushes taxable income above $1,000,000, on the excess only, on top of ordinary California tax. Sale-year timing therefore matters; the household figure requires a CPA computation."], "status": "Verified", "sources": ["ca_rtc17043", "ftb_540es_2025", "ftb_gifts"]},
        {"cells": ["California capital gains", "California has no lower rate for capital gains; all capital gains are taxed as ordinary income (FTB, updated 01/28/2026).", "A gain on the sale of inherited real property is ordinary California income in the sale year, and it counts toward the $1,000,000 surcharge threshold above. Federal capital-gain rates and the federal basis rules are a separate calculation."], "status": "Verified", "sources": ["ftb_cap_gains", "ftb_gifts"]},
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
    blank = "Not supplied — no published source can state this for the household"
    liquidity_rows = [
        {"cells": ["Cash and marketable securities available to the estate at the transfer", blank, "A Form 706 filing and any tax payment are due before most illiquid assets can be sold; the executor's ability to pay is a separate question from whether tax is owed.", "A dated inventory of accounts by type with balances banded to the nearest ten dollars, plus which accounts pass outside probate."], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["Life insurance and retirement proceeds, and who receives them", blank, "Proceeds payable to a named beneficiary generally bypass the probate estate and may also bypass the estate-tax base, so they can be the funding source the executor cannot reach — or the one that is already spoken for.", "Beneficiary designations, policy cash values, and a note of who controls each contract at the transfer date."], "status": "Missing", "sources": ["irs_estate"]},
        {"cells": ["Mortgages, liens, assessments and repair obligations on both buildings", blank, "Debts reduce the taxable estate in the appropriate circumstances and reduce the cash the estate can actually distribute; a rented building may carry liens a lease does not reveal.", "Title reports for each building, the current debt schedule, and any special assessment (for example a seismic or façade mandate) with its payment calendar."], "status": "Missing", "sources": ["irs_estate", "ca_rtc480"]},
        {"cells": ["Prior taxable gifts and the adjusted taxable-gift total", blank, "The Form 706 filing test is the gross estate plus adjusted taxable gifts plus the specific gift-tax exemption, so gifts made decades ago can raise the estate above the filing threshold even when no gift tax was ever paid.", "Every gift-tax return (Form 709) filed by either spouse, the state's gift ledger if it kept one, and a written schedule of gifts above the annual exclusion."], "status": "Missing", "sources": ["irs_estate", "irs_2027"]},
        {"cells": ["Whether a portability election was made for the first spouse to die", blank, "For 2026 the basic exclusion is $15,000,000 per person, and up to $30,000,000 for a married couple with a timely portability election; the IRS material notes a decedent's unused exclusion is only available if the survivor's estate elects it on a timely-filed return.", "The first decedent's Form 706 (or a written confirmation that none was filed), and the CPA's note on whether a late election is still available under the relief procedure."], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["Whether a return is required even when no tax is due", blank, "A filing threshold is not the same as tax due: an estate below the exclusion can still need a return to make an election, and an election missed at that time is usually gone permanently.", "The CPA's written position on whether a return is required or advisable for each decedent, with the deadline calendared."], "status": "Verified", "sources": ["irs_estate_faq", "irs_estate"]},
        {"cells": ["The 9-month calendar and the payment mechanics", blank, "Form 4768 extends the time to file, generally not to pay; an extension obtained after the due date does not fix a late payment.", "A one-page executor checklist showing the Form 706 date, the payment date, the source of the funds on each date, and who signs."], "status": "Verified", "sources": ["irs_estate_faq"]},
    ]
    body += make_table(
        "Liquidity, gifts and portability — the estate facts this site cannot see",
        ["Fact the plan needs", "Status", "Why it changes the answer", "What closes it"],
        liquidity_rows,
        "Every row is blank by policy. A property-level model can say whether a threshold is approached; only an estate inventory can say whether the estate can meet a filing, make an election, and pay without forcing the sale of the very house the plan is trying to keep. This is the point at which 'maximize profit, minimize cost' stops being a property question and becomes an estate-liquidity question.",
    )
    body += callout(
        "Cash in the estate, stated plainly",
        "Two houses worth a combined rounded value of about " + money10(PROPERTY_A["value_2026"] + PROPERTY_B["value_2026"]) + " at today's owner-supplied estimates can sit well under a federal filing threshold while still being unable to pay a filing fee, a repair, an insurance premium and a tax bill in the same ninety days. Estate tax is paid in cash on a fixed date, and real property is not cash. The plan's protection against a forced sale is not the exclusion amount — it is liquid reserves sized against the executor's calendar, which is why the four rows above are treated as prerequisites rather than refinements. The site publishes no reserve figure, because the household's cash position is not published information.",
        kind="warn",
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
        {"cells": ["San Francisco transfer-tax tiers and the 'Prop H' reference", "The city-county publishes a six-tier schedule per $500 of consideration on the recorder's page; Proposition I (November 2020) raised only the two top tiers, from 2.75% to 5.5% and from 3% to 6%. No property-tax, transfer-tax or landlord measure named 'Proposition H' was found in the official material reviewed for this site; the November 2020 San Francisco measure of that number concerned small-business permitting, per non-official secondary reporting only.", "The owner's brief lists 'Model Prop H with its official terms'. Before any model line is named for it, confirm which jurisdiction and year the owner means and read that measure's official text; this site models the transfer-tax tiers it can verify and publishes nothing for an unidentified measure."], "status": "Not verified", "sources": ["sf_recording_fees", "sf_prop_I"]},
        {"cells": ["Santa Clara County transfer tax and recording schedule", "Not retrieved in this sandbox; no county figure is published anywhere on this site for the anticipated-trust property's sell path.", "Obtain the county ordinance rate, the exemption list for transfers at death, and the recorder's fee schedule; then price them into the sell path next to the city figures."], "status": "Missing", "sources": ["scc_dtt_unverified"]},
        {"cells": ["Insurance availability and coverage", "Market conditions, underwriting, wildfire/flood risk, exclusions and reconstruction costs may change independently of taxes.", "Refresh written quotes and coverage terms; do not extrapolate an old premium."], "status": "Missing", "sources": ["cdi"]},
        {"cells": ["Investment yields and market entry", "Treasury rates are fixed at each auction for the selected security; stock prices can lose value.", "Reprice the ladder and compare reinvestment and sequence risk immediately before investment."], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
        {"cells": ["Long-run economic assumptions", "CBO's cited interest-rate horizon is 2026–2036; no cited official source provides an individual 50-year house value, insurance price, rent or return forecast.", "Use several clearly labeled stress paths; never promote a scenario into a forecast."], "status": "Guidance", "sources": ["cbo_rates", "fhfa_hpi", "bls_cpi"]},
        {"cells": ["Nov 3, 2026 tax-related statewide measures (Props 3, 40–43)", "The official titles are: 3 — extends the existing tax on high incomes for schools and health care; 40 — imposes a one-time tax on certain taxpayers; 41 — prohibits new state taxes that exclude revenue from the state spending limit and requires audits of new state special taxes; 42 — prohibits new state personal property taxes and certain retroactive state taxes; 43 — limits voters' ability to raise local government revenue. The election date (Nov 3, 2026) is before today's date (Nov 15, 2026); certified results were not read here.", "Read the certified results and each measure's full text and fiscal analysis before relying on any tax effect; a ballot title is not a legal outcome by itself."], "status": "Not verified", "sources": ["sos_ballot"]},
        {"cells": ["SF rent-control allowable increase", "The Rent Board page states a 1.6% allowable annual increase for covered units from March 1, 2026 through February 28, 2027. Secondary articles that cite a different figure are superseded by this official page.", "Re-check the Rent Board page each year; confirm whether a unit is covered before applying any increase."], "status": "Verified", "sources": ["sf_rent_board"]},
        {"cells": ["SF Rent Board 2026 notices (demolition/major renovation protections; security-deposit interest)", "The Rent Board page lists a January 23, 2026 item on tenant protections for demolition and major renovation, and a security-deposit interest change effective March 1, 2026. Their substance was not extracted into this site.", "Counsel should read the linked notice text and confirm whether it applies to the specific units before any tenant or deposit decision."], "status": "Not verified", "sources": ["sf_rent_board"]},
    ]
    body = callout("Watch enacted law, not headlines", "The pages distinguish current statutes and agency tables from bills, stress assumptions and future uncertainty. No bill or proposal is represented as current law. The inherited transfer is far in the future; refresh federal, state and actual local rules near the event.", "info")
    body += make_table("Law and market watchlist", ["Topic", "Current official baseline / proposal status", "What to re-check"], rows)
    cadence_rows = [
        {"cells": ["Every year, on a fixed date", "Re-run the model with updated inputs and check whether the recommendation moved (`python3 tools/recheck.py` reports MOVED or UNCHANGED against the committed snapshot), then refresh: the IRS annual inflation adjustment, the assessor's roll and bill for each building, written insurance quotes, and the Rent Board's annual allowable increase.", "A run that produces the same ranking is evidence the ranking is robust; a run that flips it is the earliest warning available without paying for new data."], "status": "Guidance", "sources": ["irs_2027", "boe_pub29", "cdi", "sf_rent_board"]},
        {"cells": ["Every two years, in February", "The Proposition 19 value-limit amount is adjusted on a published biennial schedule using the FHFA California house-price index; the next adjustment is due 2027-02-16.", "This single number decides how much of a low base survives a transfer, so it must be read from the BOE's own release, not projected from an assumption band."], "status": "Verified", "sources": ["boe_lta_2025_009", "fhfa_hpi"]},
        {"cells": ["Every legislative session", "Track estate and gift proposals (S.4196, H.R.601, S.587 as of this check), any California death-tax or property-tax measure, and any local transfer-tax or rent ordinance. Record each item as enacted, chaptered with a limited scope, or introduced only.", "Proposals change the plan only when enacted with an effective date; treating a bill as law is how a model quietly rewrites the answer."], "status": "Verified", "sources": ["congress_legislation", "ca_legislation", "sos_ballot"]},
        {"cells": ["Annually, for stress cases only", "Re-read the extreme scenarios — a 1929-style and a 2007-09-style entry, an inflation surge, insurance non-renewal, a failed or late exclusion claim — and confirm the official anchors still match what the site publishes.", "The stress rows are the part of the site most likely to go stale silently, because no statute forces anyone to update them."], "status": "Guidance", "sources": ["fed_1929", "fed_2008", "bls_cpi", "cdi"]},
        {"cells": ["On any event, immediately", "Death, a change in the trust, a lease ending, an insurance non-renewal, a ballot result that changes a tax, or a decision to occupy or not occupy: re-check the deadlines that start from that event (60-day trustee notice, 150-day change-in-ownership statement, 9-month Form 706, one-year occupancy and exemption, three-year claim).", "These clocks do not pause for analysis; the calendar is the part of this plan that cannot be recovered later."], "status": "Verified", "sources": ["ca_prob160617", "ca_rtc480", "irs_estate_faq", "ca_rtc63"]},
    ]
    body += make_table("Re-check cadence — who looks, how often, and at what", ["Cadence", "What to re-read and re-run", "Why this interval"], cadence_rows, "The cadence is the control that keeps a decision aid from becoming a stale assumption set. Nothing here is a substitute for counsel near the actual transfer; it is the schedule that makes sure counsel is given current inputs.")
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
    brief_extra = [
        {"cells": ["CPA — depreciation and recapture", "Produce each building's depreciation schedule, land/building allocation and accumulated depreciation, and state the recapture at a sale-price band (maximum 25% federal on unrecaptured section 1250 gain; California ordinary rate on the whole gain).", "Form 4562 by year, purchase statement, improvement invoices, prior conversions of use."], "status": "Missing", "sources": ["irs_p527_depreciation", "irs_topic409", "ftb_cap_gains"]},
        {"cells": ["CPA — main-home exclusion switch", "Confirm whether the heir's occupancy will satisfy the two-out-of-five-year ownership and use tests, and whether the decedent's ownership period counts toward the ownership test on an inherited home.", "Dated occupancy plan, intended sale year, prior exclusion use within five years."], "status": "Missing", "sources": ["irs_121", "irs_topic701"]},
        {"cells": ["Attorney — same-year sale and exchange intent", "Advise whether a sale in the tax year of death is preferred (basis is the date-of-death value, so little gain arises) and whether any like-kind exchange is intended; section 1031 requires both sides to be held for business or investment.", "Draft distribution timeline, trustee powers, the intended use of proceeds."], "status": "Missing", "sources": ["irs_p551_basis", "irs_8824"]},
        {"cells": ["Escrow / recorder — transfer costs", "Quote the county and city documentary transfer tax, recording charges, the change-of-ownership screening form and whether a transfer at death is exempt from documentary transfer tax.", "Assessor parcel record, preliminary title report, the deed or trust transfer document."], "status": "Missing", "sources": ["sf_recording_fees", "ca_rtc480"]},
        {"cells": ["Household — criteria agreed before figures arrive", "Write and date what would make the household choose each path, and what would reverse it, so the outcome is not reverse-engineered from one projection.", "The decision log and the signed one-page criteria statement, kept with the private records."], "status": "Guidance", "sources": ["github_history"]},
    ]
    body += make_table("Additional asks added with this release", ["Adviser", "Question to resolve", "Records to bring"], brief_extra, "Print with the checklist above; one page total. No identifying detail is required on any of these lines.", source_labels={"irs_p527_depreciation": "IRS Pub 527", "irs_topic409": "IRS Topic 409", "ftb_cap_gains": "FTB capital gains", "irs_121": "IRC §121", "irs_topic701": "IRS Topic 701", "irs_p551_basis": "IRS Pub 551", "irs_8824": "IRS Form 8824", "sf_recording_fees": "SF recorder schedule", "ca_rtc480": "RTC §480", "github_history": "GitHub history policy"})
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
        ("D13", "Decide the depreciation and recapture treatment, and date it (2026-11-15)",
         "Decision recorded: model both buildings with the published 27.5-year class, assume a 55-75% building share until the CPA supplies the real split, and always subtract accumulated depreciation and the 25% federal clawback from a rental sale. Not decided: the actual schedule, which requires the return.",
         "The gap is now visible on every path instead of hidden in one, and the open item names who closes it.",
         [("Decision quality", "High"), ("Effort", "Done in model"), ("Privacy impact", "None")],
         ["irs_p527_depreciation", "irs_topic409"]),
        ("D14", "Decide how a sale is priced, and date it (2026-11-15)",
         "Decision recorded: every sell path is net of the published city-county tier (charged on the entire consideration), recording charges and the change-of-ownership screening fee, with the county figures left blank and flagged until retrieved. Not decided: any Santa Clara County amount.",
         "Gross-value comparisons overstate a sale by roughly one tier of transfer tax plus a few percent of closing cost; pricing it removes a false winner.",
         [("Decision quality", "High"), ("Effort", "Done in model"), ("Privacy impact", "None")],
         ["sf_recording_fees", "scc_dtt_unverified"]),
        ("D15", "Decide that the live-in path gets imputed-rent credit, and date it (2026-11-15)",
         "Decision recorded: the what-if control takes an avoided-rent input, defaulted to zero so nothing is invented, and the site publishes no rent for the anticipated-trust property until written comparables exist.",
         "It is the one number that can flip the ranking, so it is now an explicit input instead of a silent assumption.",
         [("Decision quality", "High"), ("Effort", "Done in tool"), ("Privacy impact", "Local only")],
         ["hud_fmr", "irs_p527_depreciation"]),
        ("D16", "Decide the privacy enforcement change, and date it (2026-11-15)",
         "Decision recorded: the committed scrub helper's rounded-to-unrounded map is deleted from the tree, place identifiers are removed from every published page, and the verifier now fails on any unrounded comma-grouped amount or mapping pattern anywhere in the repository. The history rewrite remains an owner/admin action.",
         "A public map from a rounded figure to its exact source value cancels the whole rounding policy; closing it is worth more than any additional rounding.",
         [("Privacy", "Critical"), ("Effort", "Done"), ("Privacy impact", "Protective")],
         ["github_history"]),
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



def build_capital_model() -> str:
    """Depreciation, recapture, transaction costs, imputed rent and the capital plan."""
    dep_low = b_depreciation(BUILDING_SHARE_LOW)
    dep_high = b_depreciation(BUILDING_SHARE_HIGH)
    sell_10 = live_then_sell_exclusion(10)
    sell_20 = live_then_sell_exclusion(20)
    fees_b = sell_path_costs(PROPERTY_B["value_2026"])
    tt_b, tt_b_rate = sf_transfer_tax(PROPERTY_B["value_2026"])

    body = callout(
        "Why this page exists",
        "Two costs were missing from the headline comparison and one benefit was never priced. The missing costs: the depreciation that a rented building accumulates and later gives back as unrecaptured section 1250 gain, and the transfer tax and recording charges that sit between a gross sale price and investable cash. The missing benefit: a house you live in pays rent to nobody, and that avoided rent is the only reason a free-and-clear house can beat a rented one. Each is modelled here with its rule linked, its assumption labeled, and its unknown left blank.",
        "info",
    )

    path_rows = [
        {"cells": ["Live in A, never rent it", "None — a principal residence is not depreciable.", "No depreciation, so no recapture. A later sale is measured against the date-of-death basis.", "If the household lives there, no rent is paid elsewhere; that avoided rent belongs in the comparison (see the imputed-rent table)."], "status": "Verified", "sources": ["irs_p527_depreciation", "irs_p551_basis"]},
        {"cells": ["Rent A from the day of transfer", "Depreciable basis is the date-of-death value allocated to the building; land is excluded.", "A high transfer-date basis means large early deductions — and the same amount becomes unrecaptured section 1250 gain on a sale, taxed at a maximum 25% federal rate.", "Renting forfeits the principal-residence condition the family-home exclusion depends on, so the property-tax branch changes first (see the property-tax page)."], "status": "Verified", "sources": ["irs_p527_depreciation", "irs_topic409", "ca_rtc63"]},
        {"cells": ["Live in A for years, then rent it", "Depreciation begins when the property is placed in service as a rental; the conversion basis rule is not resolved on this page.", "Only post-conversion depreciation creates recapture; the earlier years are clean.", "Ask the CPA to state the conversion basis (lesser of adjusted basis or fair market value at conversion) in writing before modelling the deduction."], "status": "Missing", "sources": ["irs_p527_depreciation"]},
        {"cells": ["Live in A, then sell it", "No recapture unless it was rented; the main-home exclusion can shield part of the gain instead.", "Gain accrues only from the date-of-death value forward — appreciation during the decedent's life is not taxed at transfer.", "The two-out-of-five-year ownership and use tests decide the shield; whether the decedent's ownership period can be counted toward them is NOT verified on this site and is a CPA question."], "status": "Verified", "sources": ["irs_p551_basis", "irs_topic701", "irs_121"]},
        {"cells": ["Keep renting B (status quo)", "B's building is already depreciated on a carryover basis; deductions continue while it is rented.", "Every dollar deducted lowers the basis and returns as unrecaptured section 1250 gain at 25% maximum federal rate, plus California ordinary income tax, because California has no lower rate for capital gains.", "A death does not reset B's basis: B is already owned by the heir, so no step-up applies to it at the future transfer."], "status": "Verified", "sources": ["irs_p527_depreciation", "irs_topic409", "ftb_cap_gains"]},
        {"cells": ["Sell B", "Recapture crystallises with the gain; the depreciation already taken is taxed at sale even if some of it was never claimed.", "California taxes the whole gain, recapture included, at ordinary rates; the 1% tax above one million dollars can apply on top once taxable income clears one million.", "A like-kind exchange can defer the gain but only if BOTH the property given up and the property received are held for business or investment; a main home does not qualify."], "status": "Verified", "sources": ["irs_topic409", "ftb_cap_gains", "ca_rtc17043", "irs_p551_basis"]},
        {"cells": ["Live in one B unit, rent the other two", "The rented units stay depreciable; the owner-occupied part is not.", "Publication 527 states that if the owner lives in part of the building, gross rental income includes the fair rental value of the part occupied when testing the 80% residential-rental class — so the personal occupancy is not invisible to the return.", "This is the household's stated ability today; it must be modelled with the fair-rental-value inclusion, not as pure rental."], "status": "Verified", "sources": ["irs_p527_depreciation", "irs_rental"]},
    ]
    body += make_table(
        "What depreciation and recapture do to each path",
        ["Path", "Depreciation", "Recapture and gain at sale", "Decision consequence"],
        path_rows,
        "Rules only. No depreciation deduction, basis, split or recapture amount is asserted for either building; the computed illustration below is a labelled scenario, not a return figure.",
    )

    dep_rows = [
        {"cells": ["Assumed depreciable share of value (building only; land never depreciates)",
                   f"{BUILDING_SHARE_LOW * 100:.0f}% of {money10(PROPERTY_B['value_2026'])}",
                   f"{BUILDING_SHARE_HIGH * 100:.0f}% of {money10(PROPERTY_B['value_2026'])}",
                   "Assumption — use the assessor's or an appraisal's land/building split; no official source publishes one here."], "status": "Assumption", "sources": ["irs_p527_depreciation", "owner_b"]},
        {"cells": ["Straight-line MACRS deduction per year (27.5-year class)",
                   money10(dep_low["annual"]), money10(dep_high["annual"]),
                   "27.5-year recovery period for residential rental property, per Publication 527; the mid-month convention changes the first and last years only."], "status": "Projection", "sources": ["irs_p527_depreciation"]},
        {"cells": ["Cumulative deduction over ten years",
                   money10(dep_low["ten_year"]), money10(dep_high["ten_year"]),
                   "This is the amount that later returns as unrecaptured section 1250 gain — the number most 'rental beats sale' comparisons omit."], "status": "Projection", "sources": ["irs_p527_depreciation", "irs_topic409"]},
        {"cells": ["Federal tax on that recapture at the maximum rate",
                   money10(dep_low["fed_recapture"]), money10(dep_high["fed_recapture"]),
                   "25% maximum on unrecaptured section 1250 gain; the actual rate depends on total taxable income and can be lower."], "status": "Projection", "sources": ["irs_topic409"]},
        {"cells": ["California tax on the same ten years of deduction",
                   money10(dep_low["ten_year"] * CA_MARGINAL_HIGH), money10(dep_high["ten_year"] * CA_MARGINAL_HIGH),
                   f"Modelled at a {CA_MARGINAL_HIGH * 100:.1f}% assumed ordinary rate because California taxes all capital gains as ordinary income; the FTB rate schedule for the actual year governs, and the 1% tax above one million dollars can add to it."], "status": "Assumption", "sources": ["ftb_cap_gains", "ca_rtc17043"]},
        {"cells": ["Net ten-year position (deduction shelter minus later recapture)",
                   money10(dep_low["ten_year"] * (FED_LTCG_HIGH + CA_MARGINAL_HIGH) - dep_low["fed_recapture"] - dep_low["ten_year"] * CA_MARGINAL_HIGH),
                   money10(dep_high["ten_year"] * (FED_LTCG_HIGH + CA_MARGINAL_HIGH) - dep_high["fed_recapture"] - dep_high["ten_year"] * CA_MARGINAL_HIGH),
                   "Depreciation is mostly a timing benefit for a long-term landlord: it is worth what your current marginal rate is and costs what the rate is at sale, with a 25% federal floor on the recaptured part. Do not treat the deduction as free money in a hold-and-compare model."], "status": "Projection", "sources": ["irs_topic409", "ftb_cap_gains"]},
        {"cells": ["Actual B depreciation taken to date", "—", "—", "Unknown and unpublishable here: it needs the depreciation schedule, the acquisition basis and the land/building split from the return. Until then the 'cumulative deduction' line above is illustrative only."], "status": "Missing", "sources": ["irs_p527_depreciation"]},
    ]
    body += make_table(
        "Computed depreciation illustration for Property B (labelled scenario, not a return figure)",
        ["Line", f"Low share ({BUILDING_SHARE_LOW * 100:.0f}%)", f"High share ({BUILDING_SHARE_HIGH * 100:.0f}%)", "Method, source and limit"],
        dep_rows,
        "Inputs: the owner-supplied, privacy-rounded value for Property B and the 27.5-year recovery period. The building share, the California rate and the ten-year window are assumptions. Property-specific basis and accumulated depreciation are deliberately blank.",
    )

    s121_rows = [
        {"cells": ["Sell in the same tax year as the transfer", "No gain to shield, by construction: the basis is the date-of-death value, so a sale at that value produces neither gain nor loss. A sale below it produces a loss whose character and usability a CPA must determine.", "Not needed for a same-year sale", "This is the strongest tax argument for selling promptly after death rather than years later: appreciation during the decedent's life escapes income tax entirely. Estate value and income-tax basis are still separate calculations, and the consistent-basis rule can bind the reported figure to the estate-tax value."], "status": "Verified", "sources": ["irs_p551_basis", "irs_topic409"]},
        {"cells": [f"Live in it {sell_10['hold_years']} years, then sell", "Gain above the date-of-death basis about " + money10(sell_10["gain"]) + " at the 4% value scenario", "Up to " + money10(SECTION_121_SINGLE) + " excluded (" + money10(SECTION_121_JOINT) + " on a qualifying joint return)", "Taxable excess about " + money10(sell_10["excess_single"]) + " before any California computation; at the 20% top federal rate the shield is worth roughly " + money10(SECTION_121_SINGLE * FED_LTCG_HIGH) + " of federal tax."], "status": "Projection", "sources": ["irs_121", "irs_topic701", "irs_topic409"]},
        {"cells": [f"Live in it {sell_20['hold_years']} years, then sell", "Gain above the date-of-death basis about " + money10(sell_20["gain"]), "Same statutory ceiling — it does not grow with the holding period", "Taxable excess about " + money10(sell_20["excess_single"]) + ". The longer the household waits, the smaller the exclusion looks relative to the gain, which is an argument for timing a sale deliberately rather than by default."], "status": "Projection", "sources": ["irs_121", "irs_topic409"]},
        {"cells": ["Rent it out and never live there", "Gain from date-of-death value forward, with the depreciation clawback on top", "Generally unavailable — the use test is not met", "This is why 'rent immediately' and 'live in it then sell' are different tax paths even when the cash flows look similar."], "status": "Verified", "sources": ["irs_121", "irs_topic409"]},
        {"cells": ["Whether the decedent's ownership period counts toward the two-out-of-five-year test", "—", "—", "Not verified on this site. Publication 551 and the main-home guidance do not resolve it here; a CPA must answer before the exclusion is relied upon in the model."], "status": "Missing", "sources": ["irs_121", "irs_topic701"]},
    ]
    body += make_table(
        "The primary-residence switch, applied to a live-then-sell path",
        ["Scenario at the modelled 2045 transfer", "Gain to consider", "Statutory shield", "Model consequence"],
        s121_rows,
        "The exclusion is $250,000 / $500,000 of gain for a taxpayer meeting the ownership and use tests; it is not an inheritance allowance and it does not apply to the decedent's appreciation. Turn the switch on only for a path where the heir actually occupies the home.",
    )

    fee_rows = [
        {"cells": ["San Francisco real-estate transfer tax (Property B sale)",
                   f"{tt_b_rate} of the entire consideration — {money10(tt_b)} on a {money10(PROPERTY_B['value_2026'])} sale",
                   "Charged per $500 of consideration at the applicable tier, and the tier rate applies to the ENTIRE consideration, not marginally: 2.50 for each $500 up to 250,000; 3.40 above that to under one million; 3.75 from one million to under five million; 11.25, 27.50 and 30.00 above that.",
                   "The tier cliff is a planning fact: a price just under a tier boundary is cheaper to sell at than one just over it. Verify the schedule at the actual date."], "status": "Verified", "sources": ["sf_recording_fees"]},
        {"cells": ["Transfer-tax increase at the top tiers (November 2020)", "Proposition I raised the top two tiers from 2.75% to 5.5% and from 3% to 6%.", "Applies only at ten million dollars of consideration and above; irrelevant to a two-unit or single-family sale at the values discussed here.", "Recorded so it is not mistaken for a general increase — and because the brief's 'Prop H' question could not be matched to any transfer-tax measure (see the law watchlist and the flagged page)."], "status": "Verified", "sources": ["sf_prop_I", "sf_recording_fees"]},
        {"cells": ["Recorder base fee and per-page fee",
                   f"${fees_b['recording'] - 20.0 - 3.0:,.0f} base first page plus a small per-page charge" if False else "14 dollars base first page; 3 dollars each additional page; a nonstandard-page surcharge applies",
                   "State-mandated schedule, listed on the county recorder's own page.", "Immaterial to the decision; material to a closing statement that does not tie out."], "status": "Verified", "sources": ["sf_recording_fees"]},
        {"cells": ["Building Homes and Jobs Act fee", "75 dollars per parcel per document title, capped at 225 dollars per transaction",
                   "Exemptions are published, including documents transferring real property where transfer tax is paid and transfers of a residential dwelling to an owner-occupier; an exemption must be declared on the face of the document or on a coversheet.",
                   "Claim the exemption explicitly or the fee is charged. Add this to the escrow instructions, not to the model."], "status": "Verified", "sources": ["sf_recording_fees"]},
        {"cells": ["Preliminary Change of Ownership Report (PCOR)",
                   "20 dollars charged in lieu when a transfer document is recorded without a PCOR",
                   "The PCOR is the recorder's change-of-ownership screening document; the fee exists precisely so a missing filing is not free.",
                   "File the PCOR with every transfer document. On the inheritance side, the separate change-in-ownership statement has its own 150-day deadline."], "status": "Verified", "sources": ["sf_recording_fees", "ca_rtc480"]},
        {"cells": ["Santa Clara County documentary transfer tax and recording fees (Property A sale)", "—", "No county page with the rate or the fee schedule could be retrieved in this sandbox, so no figure is published for the Property A sell path.", "Obtain the county schedule and confirm in writing whether a transfer at death is exempt from documentary transfer tax before pricing the A sale; the exemption question is decision-relevant, not clerical."], "status": "Not verified", "sources": ["scc_dtt_unverified"]},
        {"cells": ["Agent commission and other closing costs",
                   f"{money10(fees_b['commission'])} at the low end of the assumed band for a {money10(PROPERTY_A['value_2026'])} sale",
                   f"{money10(fees_b['other_closing'])} title, escrow, preparation and warranty, modelled at {SELL_COST * 100:.0f}% of price split 60/40",
                   "Assumption. The site's headline 'net proceeds' figure is gross value minus this band; replace the band with written listings-presentation and escrow estimates before the number is used."], "status": "Assumption", "sources": ["owner_a"]},
        {"cells": ["Sell-path total, illustrative, for a Property B sale at the rounded value",
                   money10(PROPERTY_B["value_2026"] * SELL_COST + tt_b + 40.0), "Roughly " + f"{(PROPERTY_B['value_2026'] * SELL_COST + tt_b + 40.0) / PROPERTY_B['value_2026'] * 100:.2f}% of the price",
                   "Sums the assumed closing band, the verified city transfer tax and a rounded recorder/fee stack; excludes income tax on the gain and any recapture.",
                   "A 1% swing in transaction cost is worth about " + money10(PROPERTY_B["value_2026"] * 0.01) + " on B and about " + money10(PROPERTY_A["value_2026"] * 0.01) + " on A — comparable to several years of the homeowners' exemption, so it is priced, not waved away."], "status": "Projection", "sources": ["sf_recording_fees", "owner_b"]},
    ]
    body += make_table(
        "Transaction costs priced into a sell path",
        ["Charge", "Amount or rate", "Official rule", "Why it belongs in the model"],
        fee_rows,
        "Published official tariff figures are shown exactly as published; every household-derived amount is rounded to the nearest ten dollars. Nothing here is a quote for a specific transaction.",
    )

    cap_rows = [
        {"cells": ["Roof and flashing", "Year 1-5", "Inspection report with remaining life; replace-a-section quote", money10(12_000), money10(40_000), "Capitalise — it is an improvement, added to basis and depreciated with the building, not an annual repair."], "status": "Assumption", "sources": ["irs_p527_depreciation", "cslb"]},
        {"cells": ["Water heater", "Year 3-6", "Age plate and capacity", money10(2_000), money10(4_000), "Repair or capitalise depending on whether it is a straight replacement in the same unit."], "status": "Assumption", "sources": ["irs_p527_depreciation", "cslb"]},
        {"cells": ["Furnace, air handler and heat pump", "Year 2-8", "HVAC nameplate age, service history", money10(6_000), money10(18_000), "Capitalise on replacement; the solar array's inverter has its own shorter replacement cycle."], "status": "Assumption", "sources": ["irs_p527_depreciation", "owner_a"]},
        {"cells": ["Electrical panel and EV/laundry circuits", "Year 1-5", "Panel amperage, photo of the bus", money10(3_000), money10(9_000), "Capitalise. Relevant to A because a rented A would need the capacity for each unit's use."], "status": "Assumption", "sources": ["irs_p527_depreciation", "cslb"]},
        {"cells": ["Plumbing supply and sewer lateral", "Year 1-10", "Scope camera and hydrostatic test", money10(4_000), money10(25_000), "Frequently the surprise item in a three-unit building; a lateral failure also triggers a permit and street-cutry coordination."], "status": "Assumption", "sources": ["cslb", "irs_p527_depreciation"]},
        {"cells": ["Weatherproofing, paint, stucco and flashing details", "Year 2-7", "Exterior inspection", money10(6_000), money10(20_000), "Mostly repairs (deductible in the year paid) unless it is part of a larger restoration project."], "status": "Assumption", "sources": ["irs_p527_depreciation"]},
        {"cells": ["Tenant habitability, egress, smoke and carbon-monoxide devices", "Every year", "Rent-ready checklist and local inspection", money10(1_000), money10(5_000), "Ordinary and necessary rental expense; unaddressed items become a lease and insurance problem, not just a cost."], "status": "Assumption", "sources": ["irs_p527_depreciation", "ca_rent"]},
        {"cells": ["Seismic and foundation evaluation", "Once, then reassess", "Structural evaluation", money10(3_000), money10(10_000), "Evaluation is an expense; any retrofit is capitalised and may also change insurance pricing."], "status": "Assumption", "sources": ["cslb", "cdi"]},
        {"cells": ["Annual insurance premium (both buildings)", "Every year, re-quoted", "Written quotes for the actual use of each building", money10(A_INS_BAND[0]), money10(B_INS_BAND[1]), "The published market planning band, not a quote: the owner's estimate of about " + money10(PROPERTY_A["insurance_owner_estimate"]) + " a year is flagged as likely low for this market."], "status": "Assumption", "sources": ["cdi", "cdi_sis", "owner_a", "owner_b"]},
        {"cells": ["Sinking-fund target for the whole plan", "Years 1-5", "Sum of the funded items above, plus 15% contingency", money10(37_000), money10(135_000), "Divide by 60 for a monthly reserve: about " + money10(37_000 / 60) + " to " + money10(135_000 / 60) + " a month across both buildings. A path that does not fund this is not a higher-return path; it is an unfunded one."], "status": "Projection", "sources": ["irs_p527_depreciation", "cslb"]},
    ]
    body += make_table(
        "Five-year maintenance and capital plan for both buildings (planning bands, not bids)",
        ["Item", "Window", "Evidence that sets it", "Low", "High", "Treatment and note"],
        cap_rows,
        "Every band is a labelled planning assumption for an older single-family home and an older three-unit building together; none is a quote. An inspection and licensed bids replace each band. Repairs are deducted in the year paid, improvements are capitalised and depreciated with the building — the difference is worth real money and the CPA should classify each funded item.",
    )

    rent_rows = [
        {"cells": ["Live in A and keep renting B", "The market rent of a comparable A-sized home in the same submarket, times 12", "Add it to path 1's benefit; subtract nothing from path 3, which pays it", "Unknown — the site publishes no rent for A. Obtain three written rent comparables, or accept that path 1 is understated and the sell path looks better than it is."], "status": "Missing", "sources": ["hud_fmr", "owner_a"]},
        {"cells": ["Live in B's third unit instead", "The rent B currently forgoes by keeping that unit vacant, which the owner reports is close to the two rented units combined", "A genuine offset to living arrangements; it is real cash, not an accounting entry", "Owner-supplied and unverified; the leases and the lawful-unit count must be confirmed first."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "ca_rent", "irs_rental"]},
        {"cells": ["Sell A and reinvest", "No imputed rent if the household still owns B and lives there; otherwise the household's actual new housing cost must be subtracted from the sale path", "This is the single biggest omission in a 'sell and invest' comparison — the invested portfolio must fund the housing the house used to provide", "Blank until the household states where it would live after each path."], "status": "Missing", "sources": ["sec_stocks", "owner_b"]},
        {"cells": ["Renting part of a mixed-use building", "Publication 527 counts the fair rental value of the owner-occupied part as gross rental income for the residential-rental classification test", "The owner's own occupancy is not invisible to the return; it enters the 80% test and the expense allocation", "Method only — the amount is not published, and the CPA must apply the allocation to the actual units."], "status": "Verified", "sources": ["irs_p527_depreciation"]},
        {"cells": ["Escalating an avoided-rent assumption", "Rent of primary residence is a CPI-U expenditure category; the local rent cap and the Rent Board's annual allowable increase bound a covered unit", "One constant rent-growth rate for twenty years is exactly the round-number shortcut this site retires", "Use a low/base/high band, each dated; the site's own what-if control recomputes the branches with whatever rate is entered."], "status": "Guidance", "sources": ["bls_cpi", "ca_rent", "sf_rent_board"]},
    ]
    body += make_table(
        "Imputed rent — what living in the house is worth, and why the comparison is incomplete without it",
        ["Path", "What to count", "Why it changes the ranking", "Status of the number"],
        rent_rows,
        "Imputed rent is a comparison device, not income: nobody writes a cheque. It belongs in a hold-versus-sell analysis because the sale path trades a house the household owns for rent the household must pay. The value for this household is unknown on this site and deliberately left blank; the what-if control on the compare-paths page takes it as a local-only input.",
    )
    blank = "Not published — no comparable has been confirmed from an official or written source"
    comp_rows = [
        {"cells": ["Long-term rental, detached home of A's size, same submarket — comparable 1", blank, blank, blank, "Written listing or lease abstract from a licensed agent, dated, with the term and any concessions stated. Absence of a published figure here is deliberate, not an oversight."], "status": "Missing", "sources": ["hud_fmr", "irs_rental"]},
        {"cells": ["Comparable 2", blank, blank, blank, "Two more independent comparables so the middle of the range, not one asking price, is used."], "status": "Missing", "sources": ["hud_fmr", "irs_rental"]},
        {"cells": ["Comparable 3", blank, blank, blank, "If fewer than three can be documented, say so and treat the rent as a range floor rather than a point."], "status": "Missing", "sources": ["hud_fmr"]},
        {"cells": ["Furnished / short-term premium, if A would be let that way", blank, blank, blank, "Short-term rental income carries occupancy costs, platform commissions, permit requirements and volatility that a long-term comparable does not; it cannot be mixed into a long-term hurdle."], "status": "Missing", "sources": ["irs_rental"]},
        {"cells": ["Property-management fee schedule", blank, blank, blank, "A percentage of collected rent plus leasing fees; needed because the 35% operating load in the model is an assumption, not a quote."], "status": "Missing", "sources": ["irs_rental"]},
        {"cells": ["Vacancy and turnover assumption", blank, blank, blank, "Days vacant per year and one month's rent to re-let, from the manager's actual numbers, not a rule of thumb."], "status": "Missing", "sources": ["irs_rental"]},
        {"cells": ["Derived hurdle the comparables must beat", "This site's planning number", money10(RENT_HURDLE_MONTH), "per month gross", "Computed from the ten-year property-tax difference and the assumed load — a hurdle, NOT evidence of what the market pays. Do not present it as a rent estimate."], "status": "Assumption", "sources": ["ca_rtc63", "boe_prop19", "owner_a"]},
    ]
    body += make_table(
        "Rent comparables for Property A — recorded blank until documented",
        ["Comparable", "Asking or contracted rent", "Net after expenses", "Source and date", "Rule for accepting it"],
        comp_rows,
        "No rent figure for the anticipated-trust property is published anywhere on this site, and none will be inferred from an aggregate. The one published rent series this site could retrieve — the HUD Fair Market Rent schedule — is a program parameter for a voucher-administered contract, not a market comparable, so it is registered as a verification failure and is deliberately not used to benchmark a single-family home. The hurdle row is shown only so the reader can see what a comparable must beat.",
    )
    body += callout(
        "How a rent figure earns a place on this site",
        "A licensed agent's or property manager's written comparable, or an executed lease abstract, dated within the review period, for a home of comparable size and condition in the same submarket — three of them, with the middle value used. A rent number taken from an aggregate rent schedule, a voucher payment standard, a listing-site median, or an asking price is not acceptable evidence and is not published here. Where none of that exists, the row stays blank and the ranking is labelled conditional. That is the same rule the rest of the site applies to values, fees and premiums: an official source or a written professional document, or nothing.",
        kind="method",
    )
    body += paragraph(
        "What must exist before these numbers are decision-grade",
        "A CPA-prepared schedule for each building: acquisition or inherited basis, improvements with dates and invoices, land/building allocation, depreciation taken to date, and the recapture exposure at a sale price band. An inspection report and at least two licensed bids per capital item, with the year each item is actually expected. A written rent comparable for Property A, or an explicit decision to treat the letting paths as a floor. The county transfer-tax and recording schedules for the jurisdiction of each building, and the assessor's written position on whether the transfer at death is exempt from documentary transfer tax. Until those exist, this page is a checklist with an illustration attached, not a result.",
    )
    return render_page(
        "pages/capital-and-tax-model.html",
        "Depreciation, recapture, fees and the capital plan",
        "The costs a gross-versus-net comparison usually forgets, and the benefit a live-in path usually omits: depreciation and its clawback, transfer tax and recording charges, the primary-residence switch, imputed rent, and a five-year capital plan for both buildings.",
        body,
        "NUMBERS",
    )


def build_flagged() -> str:
    rows = [
        {"cells": ["F-01 — Public Git history exposure", "GitHub reports this repository is public. The active site is generic, but reachable historical commits and PR material may retain earlier case-derived details. This task did not rewrite remote main history or claim a complete purge.", "Treat historic material as exposed. Repository-owner/admin coordination, access review, clean archive and any history rewrite/support request remain required."], "status": "Missing", "sources": ["github_history"]},
        {"cells": ["F-02 — No case-specific projection", "Private base values, assessments, tax bills, basis, leases and costs are intentionally absent from the public build.", "No year-by-year dollar forecast or best-path ranking can be responsibly published without private records and explicit assumptions."], "status": "Missing", "sources": ["irs_basis", "boe_pub29", "cdi", "irs_rental"]},
        {"cells": ["F-03 — Premiums and repairs", "No official public page provides an insurance quote or repair estimate for an individual home.", "Request property-specific insurer quotes, coverage forms, inspections and itemized licensed bids."], "status": "Missing", "sources": ["cdi", "cslb"]},
        {"cells": ["F-04 — Water and solar costs", "The state water program is not a household tariff; the CPUC page describes NEM/NBT but not an individual account's net bill.", "Use private bills and signed service/solar documents. No credit or monthly cost is filled in."], "status": "Missing", "sources": ["water_board", "cpuc_solar"]},
        {"cells": ["F-05 — Rental legality and local rules", "No unit permit, local rent-board determination, lease or tenant notice is public here.", "Confirm lawful unit count and all applicable state/local rules with counsel before projecting rent or occupancy."], "status": "Missing", "sources": ["ca_rent", "hud_fmr"]},
        {"cells": ["F-06 — Future law and market path", "The verified CBO forecast runs through 2036; the public site does not disclose a transfer date or model a household-specific future path.", "No future exclusion, house-price, CPI, rent, insurance or portfolio-return value is invented."], "status": "Missing", "sources": ["cbo_rates", "irs_2027", "fhfa_hpi"]},
        {"cells": ["F-07 — Failed official retrievals", "Direct page fetches on 2026-11-15 still return 404 for the BOE Publication 801 PDF. The earlier FTB gifts/inheritance, BOE county-assessor directory and CPUC water-utilities URLs have been replaced with official pages that resolve (FTB gifts-and-inheritance, BOE county contacts, CPUC water list).", "No claim is based on Publication 801. The replacement pages support only the statements listed in the source register, each with its own verified date."], "status": "Not verified", "sources": ["boe_pub801_404", "ftb_gifts", "boe_countycontacts", "cpuc_water_list"]},
        {"cells": ["F-09 — SF vacancy-tax path", "The SF Treasurer page on vacancy/empty-homes tax returned 'Page Not Found' on 2026-11-15, so no current SF vacancy-tax rule or filing duty is verified here.", "Find the current official SF Treasurer or Tax Collector page for any vacancy tax; do not apply one until confirmed."], "status": "Not verified", "sources": ["sf_treasurer_vacancy_404"]},
        {"cells": ["F-10 — Santa Clara property-tax rate", "The Santa Clara Assessor homepage fetch failed and the reachable Assessor page lists contacts and services only. No county levy rate or direct charge is verified for any Santa Clara parcel.", "Obtain the parcel's own secured tax bill and the official county rate schedule before any tax projection."], "status": "Missing", "sources": ["scc_assessor_fetch"]},
        {"cells": ["F-11 — HUD Fair Market Rent values", "The FY2026 HUD FMR page returned 404, and the FY2027 documentation page did not yield extractable local values. No FMR figure is published.", "Retrieve the official HUD FMR table for the specific area and year; FMR is a program benchmark, not a lawful rent."], "status": "Missing", "sources": ["hud_fmr"]},
        {"cells": ["F-12 — Japan asset-bubble figures", "Historical discount-rate and Nikkei/land-price figures come from secondary sources that disagree on details. The official Bank of Japan source was not confirmed.", "Read the official Bank of Japan data or statements before any historical Japan figure is used; none is published here."], "status": "Not verified", "sources": ["boj_unverified"]},
        {"cells": ["F-13 — California income-tax brackets (partly verified)", "The FTB rate schedule (brackets and rates) was not fetched, so California bracket figures are not verified here. The 1% Behavioral Health Services Tax above $1,000,000 (RTC §17043) and the ordinary-rate treatment of capital gains are verified from FTB and leginfo pages read 2026-11-15.", "Read the current FTB rate schedule for the tax year before any California income-tax projection."], "status": "Not verified", "sources": ["ca_rtc17043", "ftb_540es_2025", "ftb_cap_gains"]},
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
        {"cells": ["F-18 — Official pages that still do not resolve", "As of 2026-11-15 the BOE Publication 801 PDF returns 404 and the SF Treasurer vacancy-tax page returns Page Not Found. The FTB gifts page, BOE county directory and CPUC water page have been replaced by official pages that resolve (see F-07).", "Neither failing URL supports a rule or a number. Find the current official location of Publication 801 and the SF vacancy-tax rule, then update the register."], "status": "Not verified", "sources": ["boe_pub801_404", "sf_treasurer_vacancy_404"]},
        {"cells": ["F-24 — A rounded-to-unrounded map was published in the repository itself", "An earlier session committed `tools/history_scrub.sh` and a scrub plan containing the exact pre-rounding figures next to their rounded forms. Because the repository is public, that map re-created the disclosure the $10 rounding rule exists to prevent — it is more sensitive than either value alone. Both files are now figure-free; the mapping is built privately by the owner at run time, and `tools/verify.py` fails the tree scan on any comma-grouped amount that is not a multiple of ten dollars, on any mapping pattern, and on a committed redaction-rules file.", "The owner-run history rewrite (see the runbook) must still remove the historical copies. Until then treat the pre-rounding figures as exposed. Consider also flipping PUBLISH_ASSESSMENT_LEVELS to False, which removes absolute assessed values from the published site entirely."], "status": "Missing", "sources": ["github_history"]},
        {"cells": ["F-25 — No verified Santa Clara County transfer-tax or recording schedule", "No county page carrying the documentary transfer tax rate, the exemption list or the recorder's fee schedule could be retrieved in this sandbox, so the sell path for the anticipated-trust property is priced without those items and the row is left blank rather than estimated.", "Read the county ordinance and the recorder's schedule, and ask the recorder in writing whether a transfer by reason of death is exempt from documentary transfer tax. Then price it in beside the city figures."], "status": "Not verified", "sources": ["scc_dtt_unverified"]},
        {"cells": ["F-26 — 'Prop H' cannot be matched to a property or transfer-tax measure", "The owner's instruction list includes 'Model Prop H with its official terms'. The only Prop H found in the material reviewed for San Francisco was a November 2020 small-business permitting measure, and that came from secondary reporting, not an official election record; the in-force transfer-tax change is Proposition I (2020). No model line is named for an unidentified measure.", "Confirm the jurisdiction, year and measure letter with the owner, then read the official voter-guide text and results before adding it to the model. Nothing on this site depends on it."], "status": "Not verified", "sources": ["sf_prop_I", "sos_ballot"]},
        {"cells": ["F-27 — Depreciation, recapture and the §121 tacking question are methods, not the household's numbers", "The depreciation illustration uses the owner-supplied rounded value, an assumed 55-75% building share and the published 27.5-year class; it is not a schedule for either building. Whether the decedent's ownership period counts toward the two-out-of-five-year ownership test is not resolved by the sources read here.", "The CPA must produce the actual accumulated depreciation, the land/building split and a written position on the main-home exclusion for an inherited home. Do not treat the illustration as a forecast of tax."], "status": "Assumption", "sources": ["irs_p527_depreciation", "irs_121", "irs_p551_basis"]},
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
        {"cells": ["Documentary transfer tax", "A county/city tax on recorded property transfers (about 55 cents per $500 statewide base, with local variations); certain family transfers are excluded by statute.", "Confirm the current statutory exclusion and local rate with the recorder at the actual transfer."], "status": "Guidance", "sources": ["ca_rtc480"]},
    ]
    rows += [
        {"cells": ["Depreciation (rental real property)", "The annual deduction for wear and tear on a rental BUILDING — never the land — taken straight-line over the MACRS residential-rental recovery period of 27.5 years.", "It reduces taxable rent now and reduces the basis, so the same amount is waiting at sale. A home you live in is not depreciable."], "status": "Verified", "sources": ["irs_p527_depreciation"]},
        {"cells": ["Unrecaptured section 1250 gain (depreciation recapture)", "The part of a long-term gain on depreciated real property that is attributable to the depreciation allowed or allowable; taxed at a maximum 25% federal rate.", "It is not a penalty for taking depreciation — the deduction is clawed back whether or not it was actually claimed. California taxes the same amount as ordinary income."], "status": "Verified", "sources": ["irs_topic409", "ftb_cap_gains"]},
        {"cells": ["Stepped-up basis at death", "For property acquired from a decedent, basis is generally the fair market value at the date of death (or the alternate valuation), and a Schedule A from the estate can bind the beneficiary's initial basis.", "This is why a sale in the same tax year as the transfer can produce little or no gain — and why an inherited rental starts with a NEW depreciation base rather than the decedent's."], "status": "Verified", "sources": ["irs_p551_basis"]},
        {"cells": ["Imputed (avoided) rent", "The market rent a household does not pay because it owns and occupies the home; used only to compare an owner-occupied path against a path that must rent.", "It is not income, not a deduction, and not cash. Without it, a live-in path looks free and a sell-and-reinvest path looks better than it is."], "status": "Guidance", "sources": ["hud_fmr", "irs_p527_depreciation"]},
        {"cells": ["Documentary / real-estate transfer tax", "A tax on the document that transfers real property, charged per $500 of consideration at the applicable tier; some jurisdictions exempt transfers at death and specified family transfers.", "In the city-county schedule the tier rate applies to the ENTIRE consideration, not marginally, so a price just below a tier line is cheaper than one just above it."], "status": "Verified", "sources": ["sf_recording_fees"]},
        {"cells": ["Preliminary Change of Ownership Report (PCOR)", "The screening form filed with a transfer document so the assessor can evaluate whether the ownership change reassesses the property.", "Recording a transfer document without it can trigger a fee in lieu; on a death transfer the separate change-in-ownership statement has its own 150-day deadline."], "status": "Verified", "sources": ["sf_recording_fees", "ca_rtc480"]},
        {"cells": ["Section 1031 like-kind exchange", "Deferral, not exemption: exchanging real property held for business or investment for replacement real property held for business or investment, with a generally carried-over basis.", "A home the heir lives in is not held for investment, so it does not qualify; deferring the gain also carries the recapture forward into the replacement property."], "status": "Verified", "sources": ["irs_p551_basis", "irs_8824"]},
        {"cells": ["Outcome distribution vs point estimate", "The set of ending values a model produces across its assumption bands, shown as a spread (percentile bars) rather than a single number.", "A '6% a year' headline is one bar of a wide histogram; the ranking of hold-versus-sell depends on the tails, not the middle."], "status": "Guidance", "sources": ["sec_stocks", "cbo_ltbo"]},
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
        {"cells": ["Public page content (policy revised 2026-11-15, owner-directed)", "The site publishes owner-supplied figures rounded to the nearest ten dollars, badged Owner-supplied (privacy-rounded), because the owner directed that rounded figures be reported in the decision analysis. Names, street addresses, parcel numbers, account numbers and unrounded amounts are never published, and the verifier fails the build if a currency amount does not end in 0.", "Place identifiers were removed from every public page on 2026-11-15: no ZIP code, city name or neighbourhood name appears on the site. Only the governing jurisdictions are named (Santa Clara County; City and County of San Francisco), because the assessor, transfer-tax and rent rules being applied are those jurisdictions' rules."], "status": "Guidance", "sources": ["owner_a", "owner_b"]},
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
        {"cells": ["Place identifiers", "ZIP codes, the city name and the neighbourhood name were removed from every published page on 2026-11-15 and replaced with anonymised region text plus the governing jurisdiction. Street address, parcel number and assessor number remain suppressed by an automated release check.", "The check fails the build on any five-digit identifier outside the allowlist, a street-address pattern, an email address, a phone number, a county parcel number, an account or trust number, or a date of birth — and, since 2026-11-15, on any comma-grouped amount that is not $10-rounded and on any rounded-to-unrounded mapping anywhere in the tree."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Assessment levels are optional", "PUBLISH_ASSESSMENT_LEVELS in tools/sitebuild.py is the owner-facing dial. Set to False and rebuild: the assessed-value history publishes as an index (2014 = 100) with growth rates instead of dollar levels, and every derived projection still computes.", "This exists because a year-by-year dollar assessment series can be matched to a county roll even after rounding. The default remains the owner-directed published figures; flipping the dial is a one-constant change that removes that residual risk."], "status": "Guidance", "sources": ["boe_pub29"]},
        {"cells": ["Projection outputs", "Year-by-year projections are published with rounded figures and clearly labeled assumptions, alongside the blank scenario columns that remain the evidence register.", "A model output with plausible amounts can be re-identified by anyone who knows the property. Recompute with the what-if controls rather than trusting the defaults."], "status": "Guidance", "sources": ["irs_basis"]},
    ]
    body += make_table("Rounding and anonymisation discipline", ["Content type", "Rule applied", "Why it is not enough on its own"], round_rows)
    body += make_table(
        "Privacy actions taken in this release (dated)",
        ["Date", "Action", "Residual item"],
        [
            {"cells": ["2026-11-15", "Deleted the rounded-to-unrounded figure map that an earlier session had committed inside the maintenance script and scrub plan; both files are now figure-free and the mapping is built privately at run time.", "The historical commits still contain the earlier copies; only an owner-run history rewrite can remove them."], "status": "Done in tree", "sources": ["github_history"]},
            {"cells": ["2026-11-15", "Added mechanical release checks: any comma-grouped amount anywhere in the repository must be a multiple of ten dollars or be a registered official figure; any mapping pattern or committed redaction-rules file fails the build.", "A check is a guard rail, not a guarantee; a new file type outside the scan would need the rule extended."], "status": "Done in tree", "sources": ["github_history"]},
            {"cells": ["2026-11-15", "Removed ZIP codes, the city name and the neighbourhood name from every published page; only the governing jurisdictions remain, because their ordinances are the rules being applied.", "The assessed-value series is still the most re-identifiable published element; set PUBLISH_ASSESSMENT_LEVELS to False to publish it as an index."], "status": "Done in tree", "sources": ["github_history"]},
            {"cells": ["Pending owner action", "Repository visibility review, the history rewrite, GitHub Support coordination for PR diffs and caches, and deletion of stale session branches that still reference pre-rewrite objects.", "Until then, treat every earlier value as exposed; nothing on this site should be read as a clean-history claim."], "status": "Missing", "sources": ["github_history"]},
        ],
    )
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
        ("S11", "Privacy", "Remove the rounded-to-unrounded map, then delete the place identifiers", "tools/history_scrub.sh and the scrub plan once stored the exact pre-rounding figures beside their rounded forms — a map that defeats the entire rounding policy. Both are now figure-free, the verifier fails on any comma-grouped amount that is not $10-rounded and on any mapping pattern, and every ZIP, city and neighbourhood name has been deleted from the published pages.", "This closes a live re-identification path in the public repository; the historical objects still need the owner-run rewrite described in the runbook.", ["github_history"]),
        ("S12", "Tax", "Model depreciation and the recapture it creates, on both buildings", "Publish the 27.5-year illustration, the land/building allocation question, and the maximum 25% federal clawback plus California ordinary-rate treatment next to every rental path, and add the depreciation schedule to the records list the CPA must produce.", "A rental path compared without recapture is overstated by the whole deduction stream; this was the largest single modelling gap on the site.", ["irs_p527_depreciation", "irs_topic409", "ftb_cap_gains"]),
        ("S13", "Decision", "Credit the live-in path with the rent it avoids (imputed rent)", "Add an imputed-rent input to the what-if tool and a live-in-versus-sell row that shows the sell path paying market rent, with the number left blank until written comparables exist.", "Comparing an owned home at zero housing cost against an invested portfolio that must also buy housing is not a comparison; the control makes the omission visible.", ["hud_fmr", "irs_p527_depreciation"]),
        ("S14", "Costs", "Price transfer tax, recording fees and the PCOR into every sell path", "Use the city-county published schedule: tier rate on the entire consideration, per-page recording charges, the Building Homes and Jobs Act fee with its exemption declarations, and the fee in lieu when a PCOR is missing.", "The cliff between tiers is worth more than most closing-cost negotiations, and a missing PCOR is a fee that changes nothing else.", ["sf_recording_fees", "ca_rtc480"]),
        ("S15", "Model", "Show a distribution chart instead of a single projected ending value", "Ten-year outcome spread across the assumption bands (worst, quartiles, best) as bars, next to the certainty term the band does not contain — the property-tax saving of the hold path.", "One point estimate implies precision the evidence does not support; the spread is what a household actually experiences.", ["sec_stocks", "cbo_ltbo", "bls_cpi"]),
        ("S16", "Process", "Keep a five-year capital plan for both buildings beside the projections", "Inspection-driven bands per item, each labeled repair or improvement, with a monthly sinking-fund target, so a 'low cost' path is not built on deferred maintenance.", "Deferred capital is the one cost that always shows up eventually, and its classification (expense versus depreciated improvement) changes the tax result too.", ["irs_p527_depreciation", "cslb"]),
        ("S17", "Tax", "Set the primary-residence switch deliberately, path by path", "Turn the IRC §121 exclusion on only for a path where the heir actually occupies the home for two of the last five years, and record that the tacking question for an inherited home is unresolved here.", "Applying the exclusion to a never-occupied inherited home overstates the sell path; ignoring it for a lived-in home understates the hold path.", ["irs_121", "irs_topic701", "irs_p551_basis"]),
        ("S18", "Verification", "Publish the re-check cadence and the rebuild-and-diff check", "The law watchlist now states who looks at what and how often (annual model re-run, biennial February Prop 19 adjustment, every legislative session, immediately on an event), and `tools/recheck.py` rebuilds and reports MOVED or UNCHANGED against a committed snapshot of every value the ranking rests on.", "A decision aid goes stale in silence; this makes staleness a failing check instead of a forgotten intention.", ["boe_lta_2025_009", "irs_2027", "github_history"]),
        ("S19", "Evidence", "Keep the rent ledger blank instead of borrowing an aggregate", "The capital-and-tax page now carries a rent-comparables table whose value cells are blank by policy, with the acceptance rule for a comparable stated on the same line and the derived hurdle shown only as the bar a comparable must clear.", "Voucher payment standards and listing-site medians are not market comparables for a single-family home; publishing one would look like evidence and function as a guess.", ["hud_fmr", "irs_rental", "owner_a"]),
        ("S20", "Estate", "Ask the liquidity question separately from the threshold question", "The estate page now lists the estate facts the model cannot see — cash and beneficiary-designated proceeds, debts and liens, prior taxable gifts, whether a portability election was made, and whether a return is required when no tax is due — plus a plain statement that estate tax is paid in cash on a fixed date and real property is not cash.", "The plan's protection against a forced sale is liquid reserves sized to the executor's calendar, not the exclusion amount; no property model can substitute for that inventory.", ["irs_estate", "irs_estate_faq", "ca_rtc13301"]),
        ("S10", "Refresh", "Set annual legal and assumption review reminders", "Recheck enacted laws, assessor records, insurance availability, utilities, leases, market inputs and investment policy when the decision approaches.", "Today’s current rules do not determine a decision decades in the future.", ["irs_2027", "boe_prop19", "cbo_rates"]),
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
        "pages/property-profiles.html": build_property_profiles,
        "pages/questions.html": build_questions,
        "pages/projections.html": build_projections,
        "pages/property-tax.html": build_property_tax,
        "pages/capital-and-tax-model.html": build_capital_model,
        "pages/operating-costs.html": build_costs,
        "pages/black-swan.html": build_black_swan,
        "pages/phased-investing.html": build_phased_investing,
        "pages/estate-thresholds.html": build_estate_thresholds,
        "pages/inheritance-process.html": build_process,
        "pages/law-watchlist.html": build_law_watchlist,
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
