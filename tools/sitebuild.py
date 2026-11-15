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
    # --- Added 2026-11-15 (session arena-bce280ee): sell path, transfer tax, Prop 19, Prop H ---
    "scc_tax_rates": {
        "label": "Santa Clara County — Compilation of Tax Rates FY 2025-26",
        "url": "https://files.santaclaracounty.gov/exjcpb1531/2025-11/tax-rate-book-2025-2026.pdf",
        "scope": "Published levy for 816 tax rate areas in fiscal 2025-26; the first two digits of a rate-area number identify the city or unsecured area, and each parcel's rate is its own area's total. Secured instalments are due November 1 and February 1 (delinquent December 10 and April 10, then 10% plus 1.5% per month). Confirms the levy structure only — it does not state a rate for any individual parcel.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "scc_assessor_2026": {
        "label": "Santa Clara County Assessor — 2026 Assessment Information booklet",
        "url": "https://files.santaclaracounty.gov/exjcpb1521/2026-04/assessment-information-2026-booklet-english-3-23-26-web.pdf",
        "scope": "Worked example of a full bill: a 1.0000 general levy plus 0.0388 county retirement levy, 0.10 school bonds and 0.01 water district totals 1.1488 per dollar of assessed value for one example parcel. Also states base-value growth at the lesser of the CPI or 2%, that inheritance reassessment runs from the date of death rather than distribution, that supplemental bills are prorated to June 30, usually not escrowed and appealable within 60 days, and that ordinary maintenance is generally not assessable. An example parcel's rate is not any other parcel's rate.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "scc_recording": {
        "label": "Santa Clara County Clerk-Recorder — Recording real estate",
        "url": "https://www.clerkrecorder.santaclaracounty.gov/recording-documents/recording-real-estate",
        "scope": "States that documentary transfer tax is collected at recording, that a deed claiming no tax owes a stated exemption reason and a zero tax line on the face of the document, and that a preliminary change-of-ownership report is required. Does not set a rate for, or grant an exemption to, any specific transfer.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "scc_recording_fees": {
        "label": "Santa Clara County Clerk-Recorder — Recording document fees",
        "url": "https://www.clerkrecorder.santaclaracounty.gov/recording-documents/recording-document-fees",
        "scope": "Lists the recording fee schedule: the 55-cents-per-$500 documentary transfer tax, the higher combined rate for San Jose, Palo Alto and Mountain View, a 20-dollar penalty for a missing or incomplete preliminary change-of-ownership report, and the non-refundable 75-dollar per-title state charge with per-page add-ons.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "rtc_11911": {
        "label": "California RTC §11911 — Documentary transfer tax rate",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=11911.&lawCode=RTC",
        "scope": "Authorises a county, board or city to tax each deed conveying realty sold at 55 cents per $500 of consideration or value exclusive of liens remaining, on instruments over 100 dollars, with a half-rate city add-on credited against the county tax. The section as read has three subdivisions only and states no exemption: the exemptions sit in Chapter 3 of the same act, where §11930 exempts a transfer of realty outright to, or in trust for, any person or entity by reason of an inter vivos gift or a death.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "rtc_11912": {
        "label": "California RTC §11912 — Who owes the tax",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=11912.&lawCode=RTC",
        "scope": "Places the documentary transfer tax on the person who makes, signs or issues the instrument, or for whose benefit it is made.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "rtc_17043": {
        "label": "California RTC §17043 — 1% surtax on income over $1,000,000",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=17043.&lawCode=RTC",
        "scope": "Imposes an additional 1 percent of the portion of taxable income exceeding $1,000,000 (Proposition 63), and states that the credits and recomputation provisions do not reduce it. Bracket structure for the underlying tax is not published here.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "boe_lta_2026_026": {
        "label": "California BOE — Letter to Assessors 2026/026 (Proposition 19)",
        "url": "https://www.boe.ca.gov/proptaxes/pdf/lta26026.pdf",
        "scope": "Confirms that a transfer includes transfers at death and through trusts; that a 'family home' is a dwelling eligible for the homeowners' or disabled veterans' exemption because of the transferor's ownership and occupation; that the excluded amount is the factored base year value immediately before transfer plus the adjusted limit, with any excess added to the base and indexed; that the transferee must make it a principal residence within one year with no exceptions; that losing occupancy removes the exclusion retroactively to a factored full-cash-value base; and that a quick post-death sale can still qualify if occupancy and both claims were timely. The BOE notes its summaries are not official guidance.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "ftb_cg": {
        "label": "California FTB — Capital gains and losses",
        "url": "https://www.ftb.ca.gov/file/personal/income-types/capital-gains-and-losses.html",
        "scope": "States that California does not have a lower rate for capital gains and that all capital gains are taxed as ordinary income, with differences from the federal computation reported on Schedule D (540). Does not publish a household's bracket or tax.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_1031": {
        "label": "IRS — Like-kind exchanges: real estate tax tips",
        "url": "https://www.irs.gov/businesses/small-businesses-self-employed/like-kind-exchanges-real-estate-tax-tips",
        "scope": "States that section 1031 applies only to real property held for productive use in a business or for investment, that property held primarily for sale never qualifies, that money or unlike property received triggers gain to that extent while losses are not recognized, that grade and quality differences do not defeat like-kind status, and that US and non-US real property are not like-kind. Reported on Form 8824. It does not determine any taxpayer's holding intent.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_409": {
        "label": "IRS Tax Topic 409 — Capital gain and loss",
        "url": "https://www.irs.gov/taxtopics/tc409",
        "scope": "Publishes the 0/15/20 percent long-term rate structure with 2025 income breakpoints, the 25 percent maximum on unrecaptured section 1250 gain, the 28 percent rate on collectibles and section 1202 stock, short-term gains at ordinary rates, and the $3,000 net capital-loss deduction limit with carryover. Brackets change annually.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_1041sd": {
        "label": "IRS — Instructions for Schedule D (Form 1041)",
        "url": "https://www.irs.gov/instructions/i1041sd",
        "scope": "States that property acquired from a decedent is treated as held for more than one year, that basis is generally fair market value at the date of death (or the alternate-valuation figure where elected), and that a sale soon after death usually produces little or no gain.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "irs_706": {
        "label": "IRS — About Form 706 (United States Estate Tax Return)",
        "url": "https://www.irs.gov/forms-pubs/about-form-706",
        "scope": "Describes the return and its schedules as read in this session — A (real estate, at fair market value), K (adjusted taxable gifts), M, O, PC, Q, T and U — the section 2032A special-use valuation election for qualifying family farm and closely held business real property, and portability of an unused exclusion. Form revised August 2025 with instructions revised July 2026, and a request for a closing letter carries a fee after October 26, 2026. It does not value any property or determine any estate's tax.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "sfmta_prop_h": {
        "label": "SFMTA — Muni Proposition H parcel tax",
        "url": "https://www.sfmta.com/getting-around/muni/parcel",
        "scope": "Proposition H as approved by San Francisco voters on November 3, 2026: a 15-year annual parcel tax effective fiscal 2027-28 through 2041-42, billed with the property tax in two instalments, indexed for inflation after the first year. Multifamily: 249 dollars up to 5,000 square feet, then 19.5 cents per square foot, capped at 50,000 dollars. Single-family: 129 dollars up to 3,000 square feet, 42 cents per square foot to 5,000, then 969 dollars plus 1.99 dollars per square foot. Owners of rent-controlled units may pass through up to half the tax, capped at 65 dollars per unit per year, only where the initial base rent predates June 1, 2027. A seniors exemption/reduction requires an annual application.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "sf_elections_2026": {
        "label": "San Francisco Elections — November 3, 2026 results",
        "url": "https://sfelections.org/results/20261103/",
        "scope": "Preliminary (uncertified) official returns for the November 3, 2026 municipal election, including Measure H at 244,760 yes (74.4%) and 84,209 no on 328,969 counted ballots. Preliminary results are subject to canvass and certification.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "sf_asr_page": {
        "label": "San Francisco Assessor-Recorder — Department page",
        "url": "https://www.sf.gov/departments--assessor-recorder",
        "scope": "Canonical department page: the new community portal for exemptions, exclusions, change of address and informal review; the Planning property information map for parcel history; reassessment on change in ownership subject to exclusions; decline-in-value informal review January 2 to March 31 for one-to-four-unit properties and Assessment Appeals Board filing July 2 to September 15; the 2026-2027 roll released July 17, 2026; and a September 22, 2026 notice on an assessment backlog. It does not publish a transfer-tax rate schedule for any sale.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "rtc_11930": {
        "label": "California RTC §11930 — gift and death transfers exempt",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=11930.&lawCode=RTC",
        "scope": "Chapter 3 of the Documentary Transfer Tax Act (Exemptions): the tax does not apply to a deed or other writing by which realty is transferred outright to, or in trust for the benefit of, any person or entity by reason of an inter vivos gift or by reason of the death of any person. Added by Stats. 1996, Ch. 862. It exempts the transfer at death or out of the trust; it does not exempt a later sale to a buyer.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "rtc_11927": {
        "label": "California RTC §11927 — community-property division exempt",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=11927.&lawCode=RTC",
        "scope": "Exempts a deed dividing community, quasi-community or quasi-marital property between spouses where required by a dissolution, nullity or separation judgment or order, or by a written agreement executed in contemplation of one — and conditions the exemption on a written recital, signed by either spouse, stating that the instrument is entitled to the exemption. Read as the model for how an exemption must be claimed on the face of a document.",
        "verified": True,
        "checked": "2026-11-15",
    },
    "rtc_11932": {
        "label": "California RTC §11932 — tax shown on the face of the document",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=11932.&lawCode=RTC",
        "scope": "Where a county has imposed the tax, every document subject to tax that is submitted for recordation must show on its face the amount of tax due and the incorporated or unincorporated location of the realty described. Amended by Stats. 2014, Ch. 20 (AB 1888), effective January 1, 2015.",
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


def money10_zero(value: float, zero_text: str = "none modeled") -> str:
    """money10() with an explicit word for a modeled zero.

    The published-amount rule requires every dollar figure to end in 0, which a bare
    zero cannot satisfy; a modeled zero is therefore printed as words rather than as a
    bare dollar-and-zero, and no row is left looking merely blank (blank means unknown on this site).
    """
    return money10(value) if round10(value) else zero_text


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


def a_value(year: int) -> float:
    return PROPERTY_A["value_2026"] * (1 + A_GROWTH) ** (year - BASE_YEAR)


def a_assessed(year: int) -> float:
    return PROPERTY_A["assessed"][BASE_YEAR] * (1 + ASSESS_CAP) ** (year - BASE_YEAR)


def a_tax_exclusion(year: int) -> float:
    """Property tax on Property A when the transfer QUALIFIES for the Prop 19 exclusion."""
    return prop19_base_qualify(year) * RATE_A


def excl_amount(year: int) -> float:
    return PROP19_EXCL_2025 * (1 + EXCL_GROWTH) ** (year - 2025)


def prop19_base_qualify(year: int, inherit: int = INHERIT_YEAR) -> float:
    """Base year value preserved by a qualifying Proposition 19 family-home transfer.

    Corrected model, 2026-11-15: under RTC §63.2 and BOE guidance the excluded amount is the
    transferor's factored base year value PLUS the adjusted value-limit amount, and the excess of
    full cash value over that sum is added to the transferred base and then indexed annually. A
    home worth far more than base + limit therefore does not keep its old tax base, so the earlier
    simplification (base = factored base year value) overstated the relief; the value limit is
    what caps it.
    """
    if year < inherit:
        return a_assessed(year)
    base_at_transfer = max(a_assessed(inherit), a_value(inherit) - excl_amount(inherit))
    return base_at_transfer * (1 + ASSESS_CAP) ** (year - inherit)


def prop19_base_reassess(year: int, inherit: int = INHERIT_YEAR) -> float:
    """Base year value after a NON-qualifying change in ownership: full cash value at transfer."""
    if year < inherit:
        return a_assessed(year)
    return a_value(inherit) * (1 + ASSESS_CAP) ** (year - inherit)


def prop19_excess(year: int = INHERIT_YEAR, inherit: int = INHERIT_YEAR) -> float:
    """Amount by which full cash value exceeds (factored base year value + value limit)."""
    if year < inherit:
        return 0.0
    return max(a_value(inherit) - (a_assessed(inherit) + excl_amount(inherit)), 0.0)


def a_tax_reassessed(year: int, inherit: int = INHERIT_YEAR):
    if year < inherit:
        return None
    return prop19_base_reassess(year, inherit) * RATE_A


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


# ---------------------------------------------------------------------------
# Session arena-bce280ee (2026-11-15): pre-decision action register.
#
# Adds the missing decision layers the owner asked for, each computed from the
# same privacy-rounded inputs and labeled assumptions so every published amount
# ends in 0: the published tax-rate-area decomposition, the same-tax-year sale
# model, the Proposition 19 occupancy rule and carry-forward, the five-year
# capital plan, Proposition H (San Francisco, approved November 3, 2026), the
# depreciation/recapture model, imputed rent, the §121 switch, estate liquidity
# and portability, and the annual re-run protocol.
# ---------------------------------------------------------------------------

# Published Santa Clara County rate structure (County Compilation of Tax Rates
# FY 2025-26 and the Assessor's 2026 assessment booklet): 1.0000 general levy
# + 0.0388 county retirement levy + voter-approved debt, expressed per $100 of
# assessed value. The Assessor's own worked example totals 1.1488.
SC_LEVY_TOTAL = 0.011488   # the booklet example: 1.0000 + 0.0388 + 0.10 + 0.01
SC_HOMEEX = 7000            # RTC §218 homeowners' exemption (statutory amount)
SC_DTT_RATE = 0.0011        # RTC §11911(a): 55 cents per $500 = 0.11% (Cupertino adds no city tax)
FED_LTCG_TOP = 0.20         # 2025/2026 top long-term capital-gain rate band (IRS Topic 409)
FED_RECAPTURE_TOP = 0.25    # unrecaptured section 1250 gain maximum rate (IRS Topic 409)
NIIT_RATE = 0.038           # IRS net investment income tax
CA_TOP = 0.133              # 12.3% top bracket + 1% over $1,000,000 (RTC §17043, Prop 63)
SEC121_SINGLE = 250000      # IRC §121 exclusion, single filer (IRS Topic 701)
DEPR_LIFE_YEARS = 27.5      # residential rental recovery period (IRS Publication 946)
BUILDING_SHARE = 0.8        # assumption: land/value split for depreciation
RENT_HURDLE_LOAD = RENT_LOAD

# Third-party listing aggregates for the Cupertino area (not official, not
# parcel-specific) used only as a scenario band until a written comparable study
# exists. Published rounded, badged Not verified on the flagged page.
A_RENT_BAND = (5550, 6400)


# Proposition H — City and County of San Francisco parcel tax approved November 3,
# 2026 (SFMTA official terms; FY 2027-28 amounts, indexed for inflation after that).
PROP_H = {
    "single_family": {"base_area": 3000, "base": 129, "mid_area": 5000, "mid_cents": 42, "high_dollars": 1.99, "high_base": 969},
    "multifamily": {"base_area": 5000, "base": 249, "marginal_dollars": 0.195, "cap": 50_000},
    "passthrough_share": 0.5,
    "passthrough_cap_per_unit": 65,
    "start_fy": 2027,
    "end_fy": 2042,
}


def prop_h_multifamily(area: float, infl: float = 0.0, years: int = 0) -> float:
    """Proposition H annual parcel tax for a multifamily residential parcel."""
    factor = (1 + infl) ** years
    if area <= PROP_H["multifamily"]["base_area"]:
        return PROP_H["multifamily"]["base"] * factor
    raw = PROP_H["multifamily"]["base"] + PROP_H["multifamily"]["marginal_dollars"] * (area - PROP_H["multifamily"]["base_area"])
    return min(raw, PROP_H["multifamily"]["cap"]) * factor


def prop_h_passthrough(tax: float, units: int) -> float:
    """Recoverable share for rent-controlled units: half of the tax, capped per unit."""
    return min(tax * PROP_H["passthrough_share"], PROP_H["passthrough_cap_per_unit"] * units)


def a_bill_levy_only(year: int) -> float:
    """The published-levy share of the owner-supplied rounded bill for Property A."""
    return SC_LEVY_TOTAL * max(PROPERTY_A["assessed"][year] - SC_HOMEEX, 0)


def a_bill_fixed_charge(year: int) -> float:
    """Residual of the supplied bill after the published levy — special charges or a
    higher rate-area total. Which it is must be read off the actual bill."""
    return PROPERTY_A["tax"][year] - a_bill_levy_only(year)


A_FIXED_CHARGE = a_bill_fixed_charge(2025)
A_BLENDED_RATE = RATE_A
A_LEVY_GAP_BPS = (RATE_A - SC_LEVY_TOTAL) * 10_000


def a_assessed_reassessed(year: int, inherit: int = INHERIT_YEAR) -> float | None:
    if year < inherit:
        return None
    return prop19_base_reassess(year, inherit)


def a_assessed_qualify(year: int, inherit: int = INHERIT_YEAR) -> float:
    return prop19_base_qualify(year, inherit)


def a_tax_exclusion_decomp(year: int) -> float:
    """Occupy-and-claim branch: published levy on (preserved base − homeowners' exemption) + fixed charges."""
    return SC_LEVY_TOTAL * max(a_assessed_qualify(year) - SC_HOMEEX, 0.0) + A_FIXED_CHARGE


def a_tax_reassessed_decomp(year: int, inherit: int = INHERIT_YEAR) -> float | None:
    base = a_assessed_reassessed(year, inherit)
    if base is None:
        return None
    return SC_LEVY_TOTAL * max(base - SC_HOMEEX, 0.0) + A_FIXED_CHARGE


# Capital-reserve planning bands (assumption, expressed as a share of the modeled value):
# a sinking fund is the only line that survives every path, so it is sized here rather than
# guessed per item. Replace with licensed bids before use.
A_RESERVE_PCT = (0.005, 0.010)
A_RESERVE_BAND = (A_RESERVE_PCT[0] * PROPERTY_A["value_2026"], A_RESERVE_PCT[1] * PROPERTY_A["value_2026"])
A_RESERVE_MID = sum(A_RESERVE_BAND) / 2
B_RESERVE_PCT = (0.010, 0.015)
B_RESERVE_BAND = (B_RESERVE_PCT[0] * PROPERTY_B["value_2026"], B_RESERVE_PCT[1] * PROPERTY_B["value_2026"])
B_RESERVE_MID = sum(B_RESERVE_BAND) / 2


def a_load_ex_tax(year: int = INHERIT_YEAR, rent: float = 0.0) -> float:
    """Operating load on a rented Property A excluding the property-tax line.

    RENT_LOAD is a blended assumption that already contains the tax line; the tax consequence
    is priced separately by the Proposition 19 branch, so it must not be counted twice.
    """
    tax_share = a_tax_exclusion(year) / max(rent * 12.0, 1.0)
    return max(RENT_LOAD - min(tax_share, RENT_LOAD), 0.05)


def prop19_breakeven_rent(year: int = INHERIT_YEAR, load: float | None = None) -> float:
    """Gross monthly rent at which letting the house exactly offsets the Prop 19 tax relief.

    Above this rent, the carry-and-rent path wins on the tax-and-rent comparison alone; below it,
    occupying wins. Only the relief term is modeled: the comparison ignores any outside rent the
    occupant would otherwise pay, which is the term that usually reverses the ranking.
    """
    relief = tax_delta_decomp(year) or 0.0
    load = RENT_LOAD if load is None else load
    return relief / 12.0 / (1.0 - load)




def tax_delta_decomp(year: int, inherit: int = INHERIT_YEAR) -> float | None:
    reassessed = a_tax_reassessed_decomp(year, inherit)
    if reassessed is None:
        return None
    return reassessed - a_tax_exclusion_decomp(year)


DELTA_2045_DECOMP = tax_delta_decomp(INHERIT_YEAR)
DELTA_10YR_DECOMP = sum(tax_delta_decomp(y) for y in range(INHERIT_YEAR, INHERIT_YEAR + 10))
RENT_HURDLE_DECOMP = (DELTA_10YR_DECOMP / 10) / 12 / (1 - RENT_HURDLE_LOAD)
BLENDED_MINUS_DECOMP = DELTA_10YR - DELTA_10YR_DECOMP

# Proposition 19 occupancy economics, computed on the corrected value-limit model.
PROP19_RELIEF_2045 = tax_delta_decomp(INHERIT_YEAR)
PROP19_RELIEF_2045_BLENDED = DELTA_2045
PROP19_EXCESS_2045 = prop19_excess()
PROP19_LIMIT_2045 = a_assessed(INHERIT_YEAR) + excl_amount(INHERIT_YEAR)
PROP19_BREAKEVEN_MONTH = prop19_breakeven_rent(load=a_load_ex_tax(rent=A_RENT_BAND[0]))
PROP19_10YR_RELIEF = DELTA_10YR_DECOMP
PROP19_10YR_RELIEF_BLENDED = DELTA_10YR
A_TAX_SHARE_OF_LOAD = min(a_tax_exclusion(INHERIT_YEAR) / (A_RENT_BAND[0] * 12.0), RENT_LOAD)

# Owner-supplied 2025 figures, restated against the published rate structure.
IMPLIED_RATE_2025 = PROPERTY_A["tax"][2025] / PROPERTY_A["assessed"][2025]
IMPLIED_RATE_WITH_EXEMPTION = PROPERTY_A["tax"][2025] / (PROPERTY_A["assessed"][2025] - SC_HOMEEX)

def sale_case(hold_years: int = 0, rented: bool = False, sec121: bool = False,
              inherit: int = INHERIT_YEAR) -> dict:
    """After-cost, after-tax proceeds from selling Property A `hold_years` after transfer.

    Inherited basis is generally date-of-death value (IRC §1014), so a sale in the
    year of the transfer produces little or no gain. Renting in the meantime adds
    depreciation, which becomes taxable recapture and permanently taxable gain.
    """
    sale_year = inherit + hold_years
    price = a_value(sale_year)
    basis = a_value(inherit)
    depreciation = 0.0
    if rented and hold_years > 0:
        depreciation = a_value(inherit) * BUILDING_SHARE / DEPR_LIFE_YEARS * hold_years
        basis -= depreciation
    gain = max(price - basis, 0.0)
    recapture = min(depreciation, gain) if depreciation else 0.0
    remainder = max(gain - recapture, 0.0)
    excluded = min(SEC121_SINGLE, remainder) if sec121 else 0.0
    remainder = max(remainder - excluded, 0.0)
    taxable = recapture + remainder
    fed = recapture * FED_RECAPTURE_TOP + remainder * FED_LTCG_TOP
    niit = taxable * NIIT_RATE
    state = taxable * CA_TOP
    selling = price * SELL_COST
    dtt = price * SC_DTT_RATE
    taxes = fed + niit + state
    return {
        "sale_year": sale_year,
        "price": price,
        "basis": basis,
        "gain": gain,
        "recapture": recapture,
        "excluded": excluded,
        "taxable": taxable,
        "fed": fed,
        "niit": niit,
        "state": state,
        "taxes": taxes,
        "selling": selling,
        "dtt": dtt,
        "net": price - selling - dtt - taxes,
        "tax_rate": (taxes / price) if price else 0.0,
    }


SALE_NOW = sale_case(0)
SALE_LATER_RENT = sale_case(5, rented=True)
SALE_LATER_LIVE = sale_case(5, sec121=True)
SALE_LATER_IDLE = sale_case(5)
COST_OF_WAITING_RENT = SALE_NOW["net"] - SALE_LATER_RENT["net"]

# Property A carrying costs used by the capital plan (owner-supplied bands and
# labeled planning bands; every published amount is rounded to the nearest $10).
A_WATER_YEAR = sum(PROPERTY_A["water_month"]) / 2 * 12
A_SOLAR_YEAR = -sum(PROPERTY_A["solar_credit_month"]) / 2 * 12
A_INS_MID = sum(A_INS_BAND) / 2
B_INS_MID = sum(B_INS_BAND) / 2
A_MAINT_MID = sum(MAINT_A_BAND) / 2
B_MAINT_MID = sum(B_MAINT_BAND) / 2
B_WATER_YEAR = sum(PROPERTY_B["water_month"]) / 2 * 12
B_ELEC_YEAR = sum(PROPERTY_B["electric_month"]) / 2 * 12

CAPITAL_PLAN_A = [
    (1, "Roof, flashing and gutter inspection; clear drainage", "Repair band", "Roof age and condition are unverified; a bid is required."),
    (1, "Water heater age check and pressure/expansion tank", "Reserve", "Age unknown; plan replacement inside the band, not at zero."),
    (1, "Solar array, inverter and interconnection document review", "Verify", "Inverter life is typically shorter than module life; the tariff governs credit."),
    (2, "Seismic and structural review; water-consumptive fixture upgrade", "Reserve", "No public source prices this work for a specific house."),
    (2, "Interior repaint and flooring refresh for letting or sale readiness", "Reserve", "Only needed if the path is rent or sell; skip if it delays a healthy sale."),
    (3, "Exterior paint, deck and fence treatment", "Reserve", "Bay-area moisture and sun exposure shorten cycles."),
    (3, "HVAC service contract or heat-pump replacement reserve", "Reserve", "Equipment age unverified."),
    (4, "Electrical panel, wiring and EV/charger capacity", "Reserve", "Older Cupertino tract homes may need panel work before added load."),
    (4, "Bathroom and kitchen caulk, grout, ventilation check", "Repair band", "Moisture damage is the common hidden cost in a rented or vacant home."),
    (5, "Landscaping, trees, hardscape and fire-safety defensible space", "Reserve", "Tree work near structures is a recurring, uninsurable cost."),
    (5, "Re-appraise the plan: compare actual spend to the reserve and re-set it", "Governance", "The plan is only useful if variance is reviewed annually."),
]

CAPITAL_PLAN_B = [
    (1, "Rent Board registration, lease audit and unit-legality reconciliation", "Verify", "Uncounted or unlawful units must not carry projected rent."),
    (1, "Roof, flashing, skylights and common-area water intrusion", "Repair band", "Older flat-roof SF buildings leak; deferred roof work is the usual large surprise."),
    (1, "Knob-and-tube wiring, panel and GFCI audit (insurance-driven)", "Reserve", "Insurers frequently condition or price coverage on the electrical condition."),
    (2, "Sewer lateral, cleanouts and lateral-line inspection", "Reserve", "Sidewalk/vault work is a city-permitted item; no public source prices it."),
    (2, "Exterior paint, stucco and siding (lead-safe prep if pre-1978)", "Reserve", "Lead-safe surface prep and permit requirements raise cost and duration."),
    (3, "Interior unit turnover: kitchens, bathrooms, flooring, appliances", "Reserve", "Turnover scope sets the achievable rent, and is the largest discretionary line."),
    (3, "Life-safety: smoke/CO devices, egress, handrails, extinguishers", "Verify", "Required devices must be installed and documented before a rent increase is defensible."),
    (4, "Seismic retrofit / sill plate and cripple-wall inspection", "Reserve", "Retrofit exclusion from reassessment must be confirmed with the assessor."),
    (4, "Water heater(s), boiler/furnace and laundry equipment service", "Reserve", "Shared-equipment condition is an operating-expense and safety issue at once."),
    (5, "Weatherization, insulation, windows, HVAC tune-up and solar feasibility", "Reserve", "Energy work also changes the tenant-absorbed cost split."),
    (5, "Reconcile actual spend against reserves; refresh the five-year plan", "Governance", "A plan that is not reconciled becomes a guess."),
]


NAV_GROUPS = [
    ("Start", [
        ("index.html", "Decision overview"),
        ("pages/executive-summary.html", "Executive summary"),
    ]),
    ("Decision", [
        ("pages/decision-analysis.html", "Compare paths"),
        ("pages/questions.html", "Questions & missing evidence"),
        ("pages/requirements-tracker.html", "Requirements tracker"),
        ("pages/suggestions.html", "Suggestions for review"),
    ]),
    ("Properties", [
        ("pages/property-profiles.html", "Property profiles (rounded figures)"),
        ("pages/operating-costs.html", "Costs & coverage"),
    ]),
    ("Numbers", [
        ("pages/projections.html", "Projection worksheet"),
        ("pages/property-tax.html", "Property-tax rules"),
        ("pages/capital-plan.html", "Five-year capital plan"),
    ]),
    ("Sell path & timing", [
        ("pages/sale-timing.html", "Sale timing & tax year"),
        ("pages/investment-policy.html", "Investment policy"),
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
    "pages/requirements-tracker.html",
    "pages/suggestions.html",
    "pages/projections.html",
    "pages/property-tax.html",
    "pages/capital-plan.html",
    "pages/sale-timing.html",
    "pages/investment-policy.html",
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
        "Handled": "verified",
        "Handled with a flag": "guidance",
        "Open — owner action": "missing",
        "Open — private step": "missing",
        "Result uncertified": "owner",
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
        {"cells": ["Property-tax exclusion eligibility", "This is the single largest lever, and it is capped: at the modeled 2045 transfer a qualifying transfer enrolls the house at about " + money10(a_assessed_qualify(2045)) + " instead of the full " + money10(a_assessed_reassessed(2045)) + " — a tax of about " + money10(a_tax_exclusion(2045)) + " per year against about " + money10(a_tax_reassessed(2045)) + " — because the value limit lets only the factored base year value plus the adjusted exclusion amount carry over, and the older base of about " + money10(FBYY_2045) + " is far below the value.", "Confirm the eligible relationship, the transferor's principal residence, transferee occupancy within one year, the homeowners' exemption filing within one year, and the claim within three years."], "status": "Owner-supplied (privacy-rounded)", "sources": ["boe_prop19", "ca_rtc63", "boe_lta_2025_009", "owner_a"]},
        {"cells": ["Federal estate-tax exposure", "The 2026 Form 706 filing test uses gross estate plus adjusted taxable gifts and the specific gift-tax exemption; a portability election can also require filing below the threshold.", "Obtain the full estate inventory, prior gifts, deductions and any spouse/portability facts; this is not a per-heir allowance."], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["Already-owned property: rental income continues under every path", "Property B supplies about " + money10(PROPERTY_B["rent_month"]) + " per month of gross rent from two rented units (owner-supplied, rounded) and does not reassess at the inheritance. Its covered-unit rent increases are capped at 1.6% for March 2026 - February 2027.", "Include B's rent, vacancy and tenant obligations in a private model, separately from A; confirm the vacant unit's lawful status before counting its rent."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "irs_rental", "sf_rent_board"]},
        {"cells": ["Rent A instead of living in it: the hurdle", "Renting A triggers the reassessment branch: after an assumed 35% operating-and-tax load, gross rent must exceed about " + money10(RENT_HURDLE_MONTH) + " per month just to offset the " + money10(DELTA_2045) + " per-year property-tax difference. What A would actually rent for is unknown and unverified.", "Obtain written rent comparables for A before ranking the rent path; the hurdle is a derived planning number, not a rent appraisal."], "status": "Assumption", "sources": ["owner_a", "boe_prop19", "ca_rtc63", "irs_rental"]},
        {"cells": ["Insurance, repairs and utilities", "Official public sources do not determine a private premium, repair budget, water bill or solar credit.", "Obtain separate written owner-occupied / landlord insurance quotes, inspection bids, utility bills and solar tariff documents."], "status": "Missing", "sources": ["cdi", "cslb", "water_board", "cpuc_solar"]},
        {"cells": ["Investment entry and reinvestment risk", "A 24–36 month Treasury staging plan changes exposure timing but adds reinvestment risk if yields fall; equity prices can fall during or after staging.", "Use the local-only stress tool, replace its explicit assumptions with then-current net yields, and compare crash-during-wait with crash-after-wait."], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
        {"cells": ["Long-range law and market conditions", "No official source can verify future estate thresholds, property values, insurance costs, rent or returns decades ahead.", "Re-check enacted law, official bills, valuations and quotes close to the transfer; do not extrapolate a single rate for fifty years."], "status": "Missing", "sources": ["irs_2027", "cbo_rates", "fhfa_hpi"]},
    ]
    body = callout(
        "Conditional best plan under the baseline assumptions (owner-supplied, privacy-rounded figures)",
        "Live in Property A after the transfer and claim the family-home exclusion: occupy within one year, file the homeowners' exemption within one year, and file the intergenerational claim within three years. At the modeled 2045 transfer that keeps the value limit — not the whole long-held base — and costs about " + money10(a_tax_exclusion(2045)) + " per year in property tax, versus about " + money10(a_tax_reassessed(2045)) + " per year if the home is instead reassessed — a difference of about " + money10(DELTA_2045) + " every year, about " + money10(DELTA_10YR) + " over the first ten years. Keep Property B as is: its rental income continues under either choice. Selling A instead nets about " + money10(SELL_NET_2045) + " after assumed sale costs and moves the decision from property tax to reinvestment risk. REINVESTMENT RISK, BESIDE THE HEADLINE: any sale proceeds parked in 3-month-to-2-year Treasuries for 24-36 months earn the then-current auction rate, which may be lower at each renewal; staged buying also lags a rising market. See the black-swan page before treating a sale as the default.",
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
        "Under the published baseline (2045 transfer, owner-supplied rounded figures, labeled growth/indexing assumptions), the decisive lever is the Proposition 19 family-home exclusion — but it is a capped lever, not a freeze: living in Property A and claiming it costs about " + money10(a_tax_exclusion(2045)) + " per year at 2045 against about " + money10(a_tax_reassessed(2045)) + " if the house is instead reassessed at full value, a difference of roughly " + money10(DELTA_2045) + " a year and " + money10(DELTA_10YR) + " over the first ten years. The conditional best plan is therefore to make Property A the principal residence after transfer (occupy within one year, exemption within one year, claim within three years), keep Property B rented as is, and treat a sale of Property A (about " + money10(SELL_NET_2045) + " net under baseline assumptions) as the alternative that trades property-tax certainty for reinvestment and sequence risk. Verify the trust terms, the assessor's determination and the household's estate position with professionals before acting; the ranking flips if the exclusion fails, rent comparables beat the derived hurdle (about " + money10(RENT_HURDLE_MONTH) + " per month gross), or the household's own housing cost in the sell path is small.",
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
        "Property B is already owned, so the future inheritance does not reassess it and its rental income continues under any plan for Property A. Property A's treatment at transfer is the decisive lever: if it can qualify as the transferee's principal residence under the family-home rules, the long-held base carries over; if it cannot, the taxable value resets to the full market value at the transfer — and the carry-over is capped by the value limit, which on the modeled figures enrolls about " + money10(a_assessed_qualify(2045)) + " rather than the older " + money10(FBYY_2045) + " base. Keep the two assets' costs, basis and records separate in every calculation.",
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
        "Baseline: 2045 transfer, owner-supplied rounded figures, 4% market-growth scenario, 2% assessed-value cap, derived effective rates, 3% exclusion indexing, 7% assumed sale costs, 35% assumed rent load. Under those assumptions the property-tax lever dominates, though the value limit caps how much of it is relief: exclusion-claimed A costs about " + money10(a_tax_exclusion(2045)) + " per year at 2045 versus about " + money10(a_tax_reassessed(2045)) + " reassessed, and B's " + money10(PROPERTY_B["rent_month"]) + " per month of gross rent continues under every path. Ranking: 1) live in A with the family-home exclusion claimed and keep B rented; 2) rent A only if written rent comparables exceed the derived hurdle (about " + money10(RENT_HURDLE_MONTH) + " per month gross); 3) sell A (about " + money10(SELL_NET_2045) + " net after assumed costs) and stage the proceeds — competitive only after counting where the household lives and the reinvestment risks on the black-swan page. The ranking flips if the exclusion fails, if rent comps beat the hurdle, or if the household's housing cost in the sell path is small. Reinvestment risk belongs beside headline 3: staged Treasuries earn an unknown renewal rate each rung, and staged buying lags a rising market.",
        "warning",
    )
    body += make_table("Mixed and pure paths to compare", ["Path", "Property A — anticipated trust transfer", "Property B — already owned", "Main uncertainty / risk"], rows, "The sources link to governing rules or official risk information. They do not establish whether a specific use, rent, exclusion or premium applies.")
    computed_rows = [
        {"cells": ["1 — Live in A (exclusion claimed); keep B rented",
                   money10(a_tax_exclusion(2045)) + " per year property tax at 2045; enrolled base about " + money10(a_assessed_qualify(2045)) + " because the value limit, not the " + money10(FBYY_2045) + " carried base, is what binds,",
                   money10(-1 * DELTA_10YR) + " property-tax position versus the reassessed branch over 2045-2054, plus in-kind housing",
                   "Qualifies only if occupancy (within 1 year), the homeowners' exemption (within 1 year) and the claim (within 3 years) all happen; confirm with the assessor."],
         "status": "Projection", "sources": ["owner_a", "boe_prop19", "ca_rtc63", "ca_rtc218"]},
        {"cells": ["2 — Rent A; keep B and keep living in B",
                   "Reassessed branch: about " + money10(a_tax_reassessed(2045)) + " per year at 2045 (the full cash value at transfer, grown at the cap thereafter)",
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
<p class="table-note">Adjust the assumptions and the key numbers recompute in this browser. Defaults mirror the published baseline. Nothing is stored or transmitted; the tool does not calculate income tax, insurance, maintenance or rent.</p>
<form id="path-tool" class="tool-grid">
<label>Market value at transfer<input id="path-value" type="number" min="0" max="99999999" step="10" value="6531230" inputmode="numeric"></label>
<label>Assessed base carried over<input id="path-base" type="number" min="0" max="99999999" step="10" value="802030" inputmode="numeric"></label>
<label>Effective tax rate (%)<input id="path-rate" type="number" min="0" max="5" step="0.01" value="1.34" inputmode="decimal"></label>
<label>Assessed-value growth cap (%)<input id="path-cap" type="number" min="0" max="10" step="0.1" value="2" inputmode="decimal"></label>
<label>Prop 19 exclusion at transfer<input id="path-excl" type="number" min="0" max="99999999" step="10" value="1886640" inputmode="numeric"></label>
<label>Rent operating load (%)<input id="path-load" type="number" min="0" max="90" step="1" value="35" inputmode="decimal"></label>
<div class="tool-actions no-print"><button id="path-reset" type="button">Reset to baseline</button><span class="tool-assumption">Derived values are rounded to the nearest $10 in the display.</span></div>
</form>
<div class="scenario-grid" aria-live="polite">
<article class="scenario-card"><h3>Exclusion claimed (live in A)</h3><dl><dt>Property tax, year 1</dt><dd id="path-tax-excl">—</dd><dt>Property tax, year 10</dt><dd id="path-tax-excl10">—</dd><dt>Ten-year cumulative</dt><dd id="path-tax-exclcum">—</dd></dl></article>
<article class="scenario-card"><h3>Reassessed (rent or sell branch)</h3><dl><dt>Property tax, year 1</dt><dd id="path-tax-re">—</dd><dt>Property tax, year 10</dt><dd id="path-tax-re10">—</dd><dt>Ten-year cumulative</dt><dd id="path-tax-recum">—</dd></dl></article>
<article class="scenario-card"><h3>Branch difference</h3><dl><dt>Annual difference, year 1</dt><dd id="path-delta1">—</dd><dt>Ten-year cumulative difference</dt><dd id="path-delta10">—</dd><dt>Rent hurdle per month</dt><dd id="path-hurdle">—</dd></dl></article>
<article class="scenario-card"><h3>Sell branch</h3><dl><dt>Net proceeds (7% costs)</dt><dd id="path-sellnet">—</dd><dt>Proceeds at 6%/yr, year 10</dt><dd id="path-sell10">—</dd><dt>Reinvestment risk</dt><dd>see black-swan page</dd></dl></article>
</div>
<p id="path-status" class="tool-status" role="status">Change a control to rerun the local comparison.</p>
<p class="table-note">Model (corrected 2026-11-15): the exclusion branch taxes max(carried base, market value − value limit) grown at the cap, because a qualifying Proposition 19 transfer keeps the factored base plus the excess of value over (base + limit); the reassessed branch taxes the full market value at transfer, also grown at the cap; both at the entered effective rate. The earlier version of this tool taxed the exclusion branch on the carried base alone and the reassessed branch on market value less the exclusion, which overstated the relief and understated the penalty for not qualifying — see the corrected pair on the property-tax page. The rent hurdle divides the ten-year difference by ten years, twelve months, and (1 − load). Sale branch subtracts 7% assumed costs and compounds 6%/yr, both labeled assumptions. This is not tax advice.</p>
</section>'''

    breakeven_rows = [
        {"cells": ["Proposition 19 relief, year 1 (2045)", money10(PROP19_RELIEF_2045) + " per year", "Levy of 1.1488 on the base preserved by a qualifying transfer, against the full-cash-value base, plus the residual fixed charge implied by the supplied bill.", "This is the whole prize for occupying — the value limit caps it, and it is smaller than the raw gap between the old and new tax bases."],
         "status": "Projection", "sources": ["scc_assessor_2026", "boe_lta_2026_026", "owner_a"]},
        {"cells": ["Same relief at the owner's blended effective rate", money10(PROP19_RELIEF_2045_BLENDED) + " per year", "The same base difference at the rate derived from the supplied 2025 bill instead of the published levy example.", "The gap between these two rows is the rate assumption, not a law question — which is why reading the bill's rate area comes first."],
         "status": "Projection", "sources": ["scc_tax_rates", "owner_a"]},
        {"cells": ["Relief over ten years (2045-2054)", money10(PROP19_10YR_RELIEF) + " cumulative", "Each year's relief indexed at the 2% assessed-value cap.", "The ten-year figure is the number worth trading against rent; one year of relief is not."],
         "status": "Projection", "sources": ["ca_rtc51", "boe_prop19"]},
        {"cells": ["Break-even gross rent that makes letting beat occupying", money10(PROP19_BREAKEVEN_MONTH) + " per month", "Relief divided by twelve and grossed up by the operating load excluding the property-tax line (so the tax is not counted twice).", "The only rent evidence available for the area — third-party listing aggregates near " + money10(A_RENT_BAND[0]) + " to " + money10(A_RENT_BAND[1]) + " — sits above this break-even, so on tax and carry alone letting wins; the term that reverses it is the outside rent an occupant would otherwise pay."],
         "status": "Assumption", "sources": ["owner_a", "hud_fmr", "irs_rental"]},
        {"cells": ["Rent needed to match the reassessed branch (published hurdle)", money10(RENT_HURDLE_MONTH) + " per month", "The site's existing hurdle: ten-year tax difference over ten years, twelve months, grossed up by a 35% load.", "Higher than the break-even above because it charges the whole tax difference to rent and treats the tax line as part of the load; both are shown so the reader can see which assumption moves the answer."],
         "status": "Projection", "sources": ["owner_a", "boe_prop19", "irs_rental"]},
        {"cells": ["Cost of waiting five years and renting, then selling", money10(COST_OF_WAITING_RENT) + " of net proceeds", "Same asset, same assumptions: sale in the transfer year against sale after a five-year rented hold, with depreciation and recapture modeled.", "This is the price of an undecided household: the delay is taxed even when the decision is only a hold."],
         "status": "Projection", "sources": ["irs_basis", "irs_409", "ftb_cg", "owner_a"]},
        {"cells": ["Imputed rent forgone by occupying, ten years", money10(A_RENT_BAND[0] * 12 * 10 * (1 - RENT_LOAD)) + " net of the assumed load", "The housing benefit the occupant receives, valued at the low end of the unverified rent band; it is a modeling convention and is not income to anyone or deductible by anyone.", "Put it on the same line as the relief: occupying is not a costless choice, and neither is letting. The comparison is between two ways of consuming the same asset."],
         "status": "Assumption", "sources": ["owner_a", "irs_rental"]},
        {"cells": ["Difference between the two modeling paths", money10(BLENDED_MINUS_DECOMP) + " over ten years", "Published-levy decomposition against the blended rate derived from the supplied bill.", "Neither is 'the model': the difference is a question for the assessor's bill, and it is larger than most of the investment-return assumptions on this site."],
         "status": "Guidance", "sources": ["scc_tax_rates", "scc_assessor_2026", "owner_a"]},
    ]
    body += make_table("Break-even table — what each path has to beat", ["Quantity", "Modeled value", "How it is computed", "How to read it"], breakeven_rows,
                       "Every figure is derived from the privacy-rounded owner-supplied inputs and the labeled assumptions above; nothing here is a bid, a quote, a rent appraisal or tax advice. The break-even rows exist so the decision can be read as a set of thresholds: if the real rent, the real levy or the real hold period moves past a number in this table, the ranking changes, and that is the point of stating it.")
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
    action_rows = [
        {"cells": ["Tax rate area, read from the bill", "The county publishes levy totals for 816 tax rate areas; the Assessor's worked example totals 1.1488 per dollar of assessed value for one parcel. Property A's own area and levy are not published here, and the supplied 2025 bill implies a rate " + f"{A_LEVY_GAP_BPS:.0f}" + " basis points above that example.", "Read the rate-area number on the parcel's own secured bill before trusting any tax figure in this model — including the numbers on this page. The number is a parcel identifier and stays off this public site."],
         "status": "Not verified", "sources": ["scc_tax_rates", "scc_assessor_2026", "owner_a"]},
        {"cells": ["Sale in the same tax year as the transfer", "Inherited basis is generally the date-of-death value, so a sale in the transfer year shows little or no gain; every later year moves appreciation into a taxable gain, and renting adds recapture on top.", "Price the same-year case first and re-run it with the actual valuation date: the model on the sale-timing page quantifies the cost of waiting."],
         "status": "Verified", "sources": ["irs_basis", "irs_1041sd", "ftb_cg"]},
        {"cells": ["Like-kind exchange: decide before listing", "Section 1031 applies only to property held for business or investment and never to property held primarily for sale; with a stepped-up basis there is usually no gain left to defer.", "Answer the question in writing before the property is listed, so the decision is not made by default at closing."],
         "status": "Verified", "sources": ["irs_1031"]},
        {"cells": ["Market rent on Property A is treated as a floor, not an estimate", "The only available figures for the area are third-party listing aggregates (a three-bedroom band of roughly " + money10(A_RENT_BAND[0]) + " to " + money10(A_RENT_BAND[1]) + " a month), not a written comparable study for this house. Every rent-driven result in this model is therefore a floor: if the real rent is lower, the rent path's advantage shrinks.", "Commission a written rent comparable from a licensed broker before ranking the rent path; until then the model refuses to call the rent path a winner on the strength of listing aggregates."],
         "status": "Not verified", "sources": ["owner_a", "hud_fmr", "irs_rental"]},
        {"cells": ["Written valuation at the date of death", "The estate reports fair market value on Schedule A of Form 706; the assessor appraises separately; the alternate-valuation election can change the number for both purposes.", "Commission one appraisal with a stated purpose covering the estate computation, the basis, the sale-timing test and the assessor's comparison, and file it with the decision log."],
         "status": "Verified", "sources": ["irs_706", "scc_assessor_2026"]},
        {"cells": ["Proposition H on Property B from fiscal 2027-28", "An enacted 15-year San Francisco parcel tax on owners, billed with the property tax and indexed; the modeled amount at an assumed building area is about " + money10(prop_h_multifamily(6500)) + " a year.", "Add it to the carrying stack for Property B in every year of the projection, and confirm the parcel's measured area and classification at the assessor."],
         "status": "Projection", "sources": ["sfmta_prop_h", "sf_elections_2026"]},
        {"cells": ["Re-run the whole model once a year", "Assessed values, levies, exemptions, insurance, rents and thresholds all move on their own calendars, and several of them have appeal or filing windows.", "Treat this worksheet as a dated artifact: record the re-run date in the decision log and keep the prior year's output beside it."],
         "status": "Guidance", "sources": ["boe_pub29", "sf_asr_page", "scc_assessor_2026"]},
    ]
    body += make_table("Action-register rows added on 2026-11-15 — what the model now requires", ["Input or decision", "What the official source establishes", "How to treat it in the model"], action_rows,
                       "These rows close the owner's pre-decision action list: the rate-area lookup, the same-tax-year sale, the written valuation, the like-kind-exchange question, the rent-as-floor rule and the annual re-run. None of them can be settled from public sources for a private parcel.")
    body += svg_bar_chart("Modeled net proceeds by exit year (Property A at the modeled 2045 transfer)",
                          [(label, case["net"], kind) for (label, case, kind) in [
                              ("Sell in the transfer year", SALE_NOW, "bar-a"),
                              ("Live five years, then sell", SALE_LATER_LIVE, "bar-b"),
                              ("Hold five years, no exclusion", SALE_LATER_IDLE, "bar-c"),
                              ("Rent five years, then sell", SALE_LATER_RENT, "bar-d"),
                          ]])
    dist_rows = []
    for year in (2040, 2045, 2050):
        low = PROPERTY_A["value_2026"] * (1 + 0.01) ** (year - BASE_YEAR)
        mid = a_value(year)
        high = PROPERTY_A["value_2026"] * (1 + 0.06) ** (year - BASE_YEAR)
        dist_rows.append({"cells": [str(year), money10(low), money10(mid), money10(high),
                                    money10(high - low),
                                    "Low path is 1% nominal growth, near the long-run real appreciation of a broad index; high path is 6%. Both are labeled scenario growth rates, not forecasts, and the middle column is the site's baseline 4% assumption."],
                          "status": "Projection", "sources": ["owner_a", "fhfa_hpi", "cbo_ltbo"]})
    body += make_table("Distribution of the modeled value, by transfer-year scenario", ["Year", "Slow market (1%/yr)", "Baseline (4%/yr)", "Fast market (6%/yr)", "Spread, slow to fast", "What the spread means"], dist_rows,
                       "The spread is the honest output of a 2040-2050 window: at the modeled midpoint the slow and fast paths differ by more than " + money10(PROPERTY_A["value_2026"] * ((1.06 ** 19) - (1.01 ** 19))) + " of value, which is larger than every carrying-cost line on this site combined except the property-tax branch. That is why the decision is framed by the tax branch rather than by a single point estimate.")
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
    rate_rows = [
        {"cells": ["Read the tax rate area before using any rate", "Santa Clara County publishes a compilation of levy rates for 816 tax rate areas for fiscal 2025-26; the first two digits of the area number identify the city or unsecured area, and every parcel's rate is its own area's total, capped at the 1% general levy plus voter-approved debt.", "Find the rate-area number printed on the parcel's own secured bill, then read that area's total. This site deliberately publishes no rate-area number for Property A: the number is a parcel identifier and belongs in private records, not on a public page."],
         "status": "Guidance", "sources": ["scc_tax_rates"]},
        {"cells": ["The published example is not the parcel's rate", "The Assessor's 2026 booklet works one example bill as a 1.0000 general levy plus 0.0388 county retirement levy, 0.10 for school bonds and 0.01 for a water district: 1.1488 per dollar of assessed value, or about 11,500 dollars on a 1,000,000 dollar assessed value.", "Use the example to understand the structure of the bill, never as a rate to multiply a value by. Bonds and direct charges are parcel-specific."],
         "status": "Verified", "sources": ["scc_assessor_2026"]},
        {"cells": ["What the owner-supplied bill implies", "The supplied 2025 figures for Property A — an assessed value near " + money10(PROPERTY_A["assessed"][2025]) + " and a tax bill near " + money10(PROPERTY_A["tax"][2025]) + " — imply a total rate of about " + f"{IMPLIED_RATE_2025 * 100:.2f}" + " percent of assessed value, or about " + f"{IMPLIED_RATE_WITH_EXEMPTION * 100:.2f}" + " percent after the statutory homeowners' exemption. That is roughly " + f"{A_LEVY_GAP_BPS:.0f}" + " basis points above the 1.1488 example.",
         "Either the bill includes parcel-specific charges the example does not, or one of the supplied figures is misremembered. Both cannot be right at the published levy, so the bill's line items decide; this site does not choose between them."],
         "status": "Owner-supplied (privacy-rounded)", "sources": ["scc_assessor_2026", "owner_a", "scc_tax_rates"]},
        {"cells": ["What a 10-dollar rounding policy cannot hide", "Rounding to the nearest ten dollars prevents a search hit on an exact figure, but a year-by-year assessed-value series can still be matched against a county roll by anyone who knows where to look.", "The privacy control that matters is not publishing the parcel number, address or owner name — which the release check enforces — combined with the owner's decision to publish rounded values."],
         "status": "Guidance", "sources": ["owner_a", "boe_pub29"]},
    ]
    body += make_table("Property A's tax rate: read the bill's rate area first", ["Row", "What the official source says", "What to do with it"], rate_rows,
                       "No tax rate area number, parcel number or address is published anywhere on this site. The rate-area lookup is the owner's private step, and the derived percentage above is computed only from owner-supplied rounded figures.")
    body += callout(
        "A question closed today: the transfer tax at death",
        "Earlier sessions could not confirm whether the county charges documentary transfer tax when a house passes by death or out of a trust, because only commercial title and tax websites asserted the exemption. "
        "The code has now been read directly: §11930 states that the tax does not apply where realty is transferred outright to, or in trust for the benefit of, any person or entity by reason of an inter vivos gift or by reason of a death, "
        "and §11932 requires the tax to be shown on the face of any recorded document that is subject to it. The exemption covers the inheritance step only. A sale to a buyer afterwards is a separate, taxable instrument, which is why the "
        "sell-path costing on this site keeps the transfer tax on the sale line and removes it from the transfer line.",
        "info",
    )
    ph_rows = [
        {"cells": ["What it is", "A 15-year annual parcel tax approved by San Francisco voters on November 3, 2026 to fund Muni service, billed on the property-tax bill in two instalments beginning in fiscal 2027-28 and indexed for inflation after the first year.", "It is a tax on owners, not a rent measure: it does not cap rents or change tenant rights, and it does not appear in the Property A analysis at all."],
         "status": "Verified", "sources": ["sfmta_prop_h", "sf_elections_2026"]},
        {"cells": ["Multifamily rate, as published", "249 dollars for a multifamily parcel up to 5,000 square feet of building area, then 19.5 cents per square foot, capped at 50,000 dollars a year.", "For Property B the modeled amount at an assumed 6,500 square feet is about " + money10(prop_h_multifamily(6500)) + " a year; the true figure depends on the parcel's measured area and classification, neither of which is verified here."],
         "status": "Projection", "sources": ["sfmta_prop_h", "owner_b"]},
        {"cells": ["Single-family comparison", "129 dollars up to 3,000 square feet, 42 cents per square foot to 5,000, then 969 dollars plus 1.99 dollars per square foot above 5,000.", "Classification matters: a three-unit building is taxed on the multifamily schedule, and each unit's status is a Roll question, not an assumption."],
         "status": "Verified", "sources": ["sfmta_prop_h"]},
        {"cells": ["Pass-through limit", "Owners of rent-controlled units may pass through up to half of the tax, capped at 65 dollars per unit per year, and only where the unit's initial base rent predates June 1, 2027.", "On the modeled figures the recoverable share is about " + money10(prop_h_passthrough(prop_h_multifamily(6500), PROPERTY_B["rented_units"])) + " a year across the two rented units — roughly a quarter of the tax, so most of it stays with the owner."],
         "status": "Projection", "sources": ["sfmta_prop_h", "sf_rent_board"]},
        {"cells": ["Seniors exemption", "Owners aged 65 or older who occupy the parcel may qualify for an exemption or reduction, applied for annually through a portal that opens December 1, 2026, with a June 1 deadline and automatic renewal.", "Not applicable to a rented building, but relevant if the household occupies a unit; the application is a recurring deadline."],
         "status": "Verified", "sources": ["sfmta_prop_h"]},
        {"cells": ["Cost context", "The Controller's estimate of the measure's revenue is about 177,000,000 dollars a year citywide; the tax is one line among many on a San Francisco parcel.", "Add it to the carrying-cost stack for Property B rather than treating it as a rounding item."],
         "status": "Verified", "sources": ["sfmta_prop_h"]},
    ]
    body += make_table("San Francisco Proposition H — an enacted parcel tax on Property B", ["Element", "What the official source states", "Effect on the model"], ph_rows,
                       "Proposition H was treated in earlier sessions as a possible rent measure and left as pending research. It is neither: it passed on November 3, 2026 with preliminary returns of 244,760 yes and 84,209 no, and it is an owner-paid parcel tax running through fiscal 2041-42. Amounts follow the SFMTA's published rate schedule for fiscal 2027-28, indexed for inflation thereafter; the uncertified election result is flagged.")
    limit_rows = [
        {"cells": ["The value limit is the binding constraint", "The excluded amount is the transferor's factored base year value immediately before the transfer plus the adjusted limit (the 2025-2027 amount is $1,044,586); the excess of full cash value over that sum is added to the base and then indexed annually.", "On the modeled 2045 Property A figures the value limit binds hard: the preserved base is about " + money10(a_assessed_qualify(INHERIT_YEAR)) + " against a full-cash-value base of about " + money10(a_assessed_reassessed(INHERIT_YEAR)) + ", so relief is worth roughly " + money10(PROP19_RELIEF_2045) + " a year — not the entire gap between the old and the new tax base."],
         "status": "Projection", "sources": ["boe_lta_2026_026", "boe_prop19", "owner_a"]},
        {"cells": ["Correction recorded on 2026-11-15", "Earlier pages in this workspace modeled the qualifying branch as keeping the factored base year value alone, and the non-qualifying branch as market value less the limit. Read together with §63.2 and the BOE letter, the correct pair is: qualifying base = factored base year value plus the excess over the limit; non-qualifying base = full cash value at the transfer.", "This session's model now uses the corrected pair everywhere, which lowers the modeled benefit of Proposition 19 and raises the modeled cost of failing to qualify. Re-read any conclusion drawn from the earlier headline figures."],
         "status": "Guidance", "sources": ["ca_rtc63", "boe_lta_2026_026"]},
        {"cells": ["Why partial relief still matters", "Because the excess is added rather than the exclusion denied, a high-value home can still receive partial relief — and the indexed 2% cap applies to the resulting base thereafter.", "Model the branches as continuous, not as a yes/no switch; and have the assessor's determination, not this page, settle it."],
         "status": "Verified", "sources": ["boe_prop19", "ca_rtc51"]},
    ]
    body += make_table("The Proposition 19 value limit, corrected", ["Point", "What the official rule requires", "Modeled effect"], limit_rows,
                       "Amounts come from the privacy-rounded owner-supplied value and the labeled growth assumptions on the projection worksheet; the official 2025-2027 limit figure is quoted as published. A future year's limit is adjusted biennially and must be read at transfer.")
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
        "Staging compared in dollars — modeled net proceeds of about " + money10(SELL_NET_2045) + " (baseline assumptions)",
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
    liquidity_rows = [
        {"cells": ["What the estate has to pay, and when", "Form 706 and the tax are generally due nine months after the date of death, with an extension available on request; the IRS notes that a filing can also be required below the threshold when the estate elects to transfer an unused exclusion to a surviving spouse.", "Put a dated liquidity requirement beside the transfer-year projection, not after it. The liquidity question is a calendar, and the calendar does not move because a house has not sold."],
         "status": "Verified", "sources": ["irs_estate_faq", "irs_706"]},
        {"cells": ["Where the cash actually sits", "The owner reports considerable cash in the estate in addition to both houses. Whether that cash is inside the trust or passes outside it changes the gross-estate computation, the liquidity analysis and the basis analysis at once.", "Ask the trustee's counsel, in writing, which assets are inside the trust and which are outside; then re-run the headroom line. Nothing on this site can infer it."],
         "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_a", "irs_estate"]},
        {"cells": ["A forced sale is the expensive way to raise cash", "Fair market value is the price between a willing buyer and a willing seller, neither under compulsion, and the IRS states that a forced-sale price is not fair market value — which is also the number that sets the heir's basis.", "A sale made to pay tax can depress the reported value that everything else in this file depends on. Sequence liquidity first and the sale second; do not let the deadline choose the timing."],
         "status": "Verified", "sources": ["irs_estate_faq", "irs_basis"]},
        {"cells": ["Deferral and special valuation are narrow tools", "Form 706 provides for electing special-use valuation of qualifying family farm and closely held business real property and for requesting installment payment, on the schedules named in the instructions.", "Note them so they are not overlooked, and do not assume either applies to two suburban houses; eligibility is a professional determination."],
         "status": "Cross-checked", "sources": ["irs_706"]},
        {"cells": ["Portability, and whether it was already used", "An estate may elect to transfer any unused federal exclusion to a surviving spouse, and the election can require filing a return that would otherwise not be required.", "Ask now, for both generations: was a portability election made, on which return, and for how much? An unmade election is usually not recoverable later."],
         "status": "Verified", "sources": ["irs_estate_faq", "irs_2027"]},
        {"cells": ["Prior taxable gifts change the threshold test", "The filing test is the gross estate plus adjusted taxable gifts, reduced by the specific gift-tax exemption used during life; Form 706 reports the gifts on Schedule K.", "Request every gift-tax return (Form 709) and a list of gifts above the annual exclusion before modeling headroom. A comparison that omits lifetime gifts is the most common error this page exists to prevent."],
         "status": "Verified", "sources": ["irs_estate_faq", "irs_706"]},
        {"cells": ["Gift now, or inherit later — the trade is basis", "The annual gift exclusion is a separate amount from the lifetime exclusion, and it does not raise the recipient's income-tax basis, whereas property acquired at death generally takes a date-of-death value.", "Gifting reduces estate-tax exposure and destroys the step-up at the same time. On a highly appreciated house that trade can cost more in income tax than it saves in estate tax; run both numbers with the CPA."],
         "status": "Guidance", "sources": ["irs_2027", "irs_basis"]},
        {"cells": ["California has no death-transfer tax today", "Current state law bars a state or local tax on a transfer by reason of death; the prohibition is statutory and could be amended by a later legislature or an approved measure.", "Treat the absence of a state transfer tax as a condition to re-check at transfer, not as a permanent feature of the plan."],
         "status": "Verified", "sources": ["ca_rtc13301", "ca_death_tax"]},
        {"cells": ["Proposition 19 is the state tax that does apply", "The property-tax consequence of the transfer is a reassessment question, not an estate-tax question, and it is capped by the value limit: on the modeled figures the relief is worth about " + money10(PROP19_RELIEF_2045) + " a year, not the whole gap between the old and the new base.", "Put the property-tax branch and the estate-tax branch on the same page only as separate columns. They have different tests, different filing clocks and different consequences for the same house."],
         "status": "Projection", "sources": ["boe_lta_2026_026", "ca_rtc63", "owner_a"]},
    ]
    body += make_table("Liquidity plan if the estate may exceed the exclusion", ["Question", "What the official source establishes", "What to do about it, in order"], liquidity_rows,
                       "No household estate inventory, prior-gift history, deduction schedule or trust authority is published here, so no conclusion about this estate's exposure is drawn. The rows state the order in which the questions have to be answered, and which document answers each one.")
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
        {"cells": ["San Francisco Proposition H (Muni parcel tax) — ENACTED", "Approved by San Francisco voters on November 3, 2026 (preliminary official returns: 244,760 yes, 74.4%; 84,209 no, on 328,969 counted ballots) and NOT a rent measure: it is a 15-year annual parcel tax on property owners, billed with the property tax from fiscal 2027-28 through 2041-42 and indexed for inflation after the first year.", "Re-read the SFMTA schedule and the certified results, confirm the parcel's building area and classification, and check the seniors exemption/reduction application window (portal opens December 1, 2026; due June 1; auto-renews) and the 50% pass-through conditions for rent-controlled owners."], "status": "Verified", "sources": ["sfmta_prop_h", "sf_elections_2026"]},
        {"cells": ["Documentary transfer tax on a death or trust transfer", "Verified against the code on 2026-11-15: §11911 sets only the rate (55 cents per 500 dollars of consideration over 100 dollars), while §11930 in the Act's exemptions chapter states that the tax does not apply where realty is transferred outright to, or in trust for the benefit of, any person or entity by reason of an inter vivos gift or a death. §11932 requires the tax, if any, to be shown on the face of the recorded document. A later sale to a buyer is a different instrument and is not exempt.", "Have the preparer state the statutory basis for the exemption on the deed before recording, and re-read §11930 and the county's exemption codes at transfer; this closes a question earlier sessions had to leave flagged on the strength of commercial title sites alone."], "status": "Verified", "sources": ["rtc_11930", "rtc_11932", "rtc_11911", "scc_recording"]},
        {"cells": ["Federal capital-gain and recapture rates", "IRS Tax Topic 409 publishes the 0/15/20 percent long-term bands with 2025 income breakpoints, the 25 percent maximum on unrecaptured section 1250 gain and the 28 percent rate on collectibles; short-term gain is taxed as ordinary income. The rates are annual and several proposals would change them.", "Re-read Topic 409 and Publication 550 for the actual year of sale, and confirm the net investment income tax and any state surcharge that applies to the same gain."], "status": "Verified", "sources": ["irs_409", "ftb_cg", "irs_niit"]},
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
        {"cells": ["Appraiser (engaged by the estate)", "One written valuation at the valuation date whose stated purpose covers the estate computation, the heir's income-tax basis, the sale-timing test and the assessor's comparison; ask whether the alternate-valuation election and the six-month window apply to a signed early sale.", "Draft engagement letter, the comparable set used, the reasonableness range, the valuation date, and the executor's beneficiary statement of values"], "status": "Guidance", "sources": ["irs_706", "irs_basis", "irs_estate_faq"]},
        {"cells": ["Real-estate tax counsel (Proposition 19)", "Two questions in writing: whether the household's occupancy intent can satisfy the one-year principal-residence condition with no exceptions, and what happens to the enrolled value if occupancy later stops; then whether any base-year value transfer to a replacement home is available.", "The transferor's occupancy and exemption records, the trust instrument, the intended move-in date, and the assessor's written determination"], "status": "Guidance", "sources": ["boe_prop19", "boe_lta_2026_026", "ca_rtc63"]},
        {"cells": ["CPA before any listing (exchange question)", "Whether a section 1031 exchange is wanted at all — with a stepped-up basis the answer is usually no — and what depreciation and recapture would do to a rented path; confirm California's ordinary-income treatment of the same gain.", "Basis schedule, depreciation plan, projected hold period, and the draft Form 8824 analysis if an exchange is considered"], "status": "Guidance", "sources": ["irs_1031", "irs_409", "ftb_cg"]},
        {"cells": ["Title company / recorder (transfer tax)", "Confirm the exemption recital for a transfer by reason of death or out of the trust on the face of the document, and the preliminary change-of-ownership report, before recording; a later sale to a buyer is separately taxable.", "Draft deed, the §11930 basis for no tax due, the PCOR form, and the closing statement's transfer-tax line"], "status": "Verified", "sources": ["rtc_11930", "rtc_11932", "scc_recording"]},
        {"cells": ["San Francisco compliance (Property B)", "Proposition H registration and rate classification for the parcel, the seniors application window if an owner occupies, the pass-through conditions for rent-controlled units, and the assessor's decline-in-value review and appeal windows.", "The SFMTA notice, the assessor's roll record for building area and classification, the Rent Board registration for each unit, and the leases"], "status": "Guidance", "sources": ["sfmta_prop_h", "sf_asr_page", "sf_rent_board"]},
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
        ("D13", "Correct the Proposition 19 value-limit model",
         "Earlier pages modeled the qualifying branch as keeping the factored base year value alone and the non-qualifying branch as market value less the limit. Read against RTC §63.2 and BOE Letter to Assessors 2026/026, the correct pair is: qualifying base = factored base year value plus the excess of full cash value over (that base + the adjusted limit); non-qualifying base = full cash value at the transfer. The model, both page tables and the browser tool now use the corrected pair everywhere.",
         "The value limit is the binding constraint on a high-value home, so the correction lowers the modeled benefit of qualifying and raises the modeled cost of failing to. Leaving it in place would have made the occupancy decision look roughly twice as valuable as the statute allows, which is a decision-changing error rather than a rounding difference.",
         [("Decision quality", "High"), ("Effort", "Medium"), ("Privacy impact", "None")],
         ["ca_rtc63", "boe_lta_2026_026", "boe_prop19"]),
        ("D14", "Reclassify San Francisco Proposition H from pending research to enacted tax",
         "Proposition H was carried in earlier sessions as a possibly-pending tenant/rent measure. It is an approved 15-year Muni parcel tax on owners (November 3, 2026), billed with the property tax from fiscal 2027-28 through 2041-42, with published single-family, multifamily, commercial and vacant-land rates, an inflation index, a seniors application, and a limited 50% pass-through for rent-controlled owners.",
         "A recurring line-item tax on the owned building belongs in the carrying stack of every path, and a rent-control assumption that does not exist must not be imported into the tenant analysis. The election result is published as preliminary and flagged as uncertified.",
         [("Decision quality", "High"), ("Effort", "Low"), ("Privacy impact", "None")],
         ["sfmta_prop_h", "sf_elections_2026", "sf_rent_board"]),
        ("D15", "Publish market rent on Property A as a floor, not an estimate",
         "The only available rent evidence for the area is third-party listing aggregates, so the rent path is stated as: gross rent must clear the modeled break-even, and any conclusion that renting wins is provisional until a written comparable study exists. No rent figure on this site is labeled as an appraisal of this house.",
         "Listing aggregates are the weakest input in the file and the one most likely to be mistaken for knowledge. Declaring them a floor keeps the honest asymmetry: the tax branch is derived from statute, the rent branch is not.",
         [("Decision quality", "High"), ("Effort", "Low"), ("Privacy impact", "None")],
         ["owner_a", "hud_fmr", "irs_rental"]),
        ("D16", "Model a sale in the same tax year as the transfer first",
         "The sale-timing page puts the transfer-year sale ahead of every later exit case, and the depreciation, section 121 and recapture consequences are modeled as the cost of waiting rather than as separate topics.",
         "The stepped-up basis makes the transfer-year answer close to settled and makes every later year a quantifiable cost; leading with the later cases buried the only comparison the owner can act on now.",
         [("Decision quality", "High"), ("Effort", "Medium"), ("Privacy impact", "None")],
         ["irs_basis", "irs_1041sd", "irs_409", "ftb_cg"]),
        ("D17", "Leave a public tax rate area number unpublished by design",
         "The property-tax page explains how to read the rate area off the bill and refuses to print the number or to treat the county's 1.1488 worked example as Property A's rate; the residual difference in the supplied figures is shown as an unresolved discrepancy instead of being assigned to a special district.",
         "A tax rate area number identifies the parcel, and guessing what the residual on a bill represents would manufacture a fact. Both choices keep the model honest in the same direction.",
         [("Privacy", "High"), ("Decision quality", "Medium"), ("Privacy impact", "Protective")],
         ["scc_tax_rates", "scc_assessor_2026", "owner_a"]),
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
        {"cells": ["F-24 — Prop 19 model correction changes earlier headlines", "This session corrected the value-limit branches (see decision log D13). Pages written before the correction described the exclusion branch as preserving the factored base year value alone and the reassessed branch as market value less the exclusion, which overstated the relief from qualifying and understated the cost of failing to. The corrected figures are about " + money10(PROP19_RELIEF_2045) + " a year of relief at the published levy and " + money10(PROP19_RELIEF_2045_BLENDED) + " at the owner's blended effective rate, against the earlier headline of roughly " + money10(DELTA_2045) + ".", "Re-read the property-tax, projection and compare-paths pages after the correction rather than quoting a saved copy of an earlier build. The correction is a modeling change, not a legal opinion: the assessor's determination and counsel govern."], "status": "Guidance", "sources": ["ca_rtc63", "boe_lta_2026_026"]},
        {"cells": ["F-25 — Property A's rent has no official source", "The rent figures used anywhere on this site for the Cupertino-area house come from third-party listing aggregates, not from a lease, a broker's written comparable study or an official table; the HUD Fair Market Rent page still returns 404 (F-11). They are published rounded and are used only as a floor.", "Commission a written rent comparable before ranking the rent path, and treat every rent-driven number on this site as provisional until it exists."], "status": "Not verified", "sources": ["owner_a", "hud_fmr"]},
        {"cells": ["F-26 — Carrying-cost bands are planning assumptions, not bids", "The five-year capital plan, the reserve percentages, the insurance bands and the maintenance bands are scheduling tools. No public source prices a private roof, lateral, turnover package or policy, and the FAIR Plan increase referenced in F-22 is itself third-party reporting.", "Replace each band with a licensed bid, a written quote and the actual provider bills; keep the plan as the calendar those documents attach to."], "status": "Assumption", "sources": ["cslb", "cdi", "irs_rental"]},
        {"cells": ["F-27 — San Francisco transfer-tax schedule and uncertified election returns", "The City's real-property transfer-tax pages returned 404 when fetched on 2026-11-15, so no San Francisco rate, tier or exemption is published anywhere on this site, and a sale of Property B leaves the transfer-tax cell blank. Separately, the November 3, 2026 results used for Proposition H are preliminary returns, not certified.", "Read the current official rate schedule before any Property B sale is priced, and confirm Proposition H against the certified canvass and the SFMTA's published rate sheet for the tax year billed."], "status": "Not verified", "sources": ["sf_asr_page", "sf_elections_2026"]},
        {"cells": ["F-28 — Privacy gate re-run for this session's published figures", "The new sell-path, capital-plan and investment-policy pages were built through the same release check: every published amount is either a listed official figure or rounded to the nearest ten dollars, no tax-rate-area, parcel, account, trust, loan or policy identifier of any kind appears anywhere in the tree, and the pages carry no script, form, remote resource or fetch capability. A re-audit of this branch was run on 2026-11-15 against the fresh build: every published amount on the new pages is either a listed official figure or rounded to the nearest ten dollars, and no new file in the tree carries an address, parcel identifier, account reference or date of birth. The reachable history of this session's clone holds 19 commits and 212 objects and is unscrubbed (F-01, F-16, F-23), which this branch cannot fix.", "Keep the owner-side action from F-01 open: an owner/admin coordinated all-ref cleanup plus a GitHub Support request. Nothing in this session widened the exposure in the current tree, and the history scrub runbook in the repository remains ready for the owner to execute."], "status": "Guidance", "sources": ["github_history", "owner_a"]},
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
        {"cells": ["Documentary transfer tax", "A county/city tax on recorded property transfers, imposed at 55 cents per 500 dollars of consideration over 100 dollars where the county has adopted it; §11930 excludes an instrument that transfers realty outright to, or in trust for, any person by reason of an inter vivos gift or a death, and §11932 requires any tax due to be shown on the face of the recorded document.", "Confirm the current statutory exclusion and local rate with the recorder at the actual transfer."], "status": "Guidance", "sources": ["ca_rtc480"]},
        {"cells": ["Unrecaptured section 1250 gain (depreciation recapture)", "The part of a sale gain on depreciated real property that is taxed at a maximum 25% federal rate instead of the ordinary long-term rate.", "It is the price of having claimed depreciation while renting; it cannot be avoided by reclassifying the gain."], "status": "Verified", "sources": ["irs_409"]},
        {"cells": ["Value limit (Proposition 19)", "The excluded amount for an intergenerational family-home transfer is the transferor's factored base year value plus a periodically adjusted limit; value above that sum is added to the transferred base.", "It is why a high-value inherited home does not keep its old tax bill, and why the modeled relief is far smaller than the raw difference between the old and new bases."], "status": "Verified", "sources": ["boe_prop19", "boe_lta_2026_026"]},
        {"cells": ["Base-year value transfer (replacement home)", "A separate Proposition 19 benefit allowing an eligible seller who occupied the original home to carry its factored base year value to a replacement principal residence bought or built within two years, with the excess in value added to the base.", "Distinct from the family-home exclusion: different conditions, different filing clock, and it is the allowance that can be carried forward after the heir occupies and later sells."], "status": "Verified", "sources": ["boe_prop19"]},
        {"cells": ["Alternate valuation", "An estate may value property six months after the date of death — and at the date of any sale or distribution inside that window — only if it lowers both the gross estate and the combined estate and generation-skipping transfer tax; basis then follows the alternate figure.", "A sale signed inside six months can tie the estate value and the heir's basis to one number."], "status": "Verified", "sources": ["irs_706", "irs_1041sd"]},
        {"cells": ["Portability", "The election by which an estate transfers its unused federal exclusion to a surviving spouse, which can require a Form 706 filing even when no return would otherwise be due.", "It is an election on a return, not an automatic entitlement; whether one was made is a question to ask now."], "status": "Verified", "sources": ["irs_estate_faq"]},
        {"cells": ["Adjusted taxable gifts", "Lifetime taxable gifts added to the gross estate for the estate-tax filing test and reducing the exclusion available at death; reported on Form 706 Schedule K.", "A headroom calculation that omits prior gifts is wrong in the direction that matters most."], "status": "Verified", "sources": ["irs_estate_faq", "irs_706"]},
        {"cells": ["Like-kind exchange (section 1031)", "A deferral, available only for real property held for business or investment, of gain when it is exchanged for other business or investment real property; property held primarily for sale never qualifies.", "With a stepped-up basis there is usually little gain to defer, so the decision is normally 'no' — and it should be written down before listing."], "status": "Verified", "sources": ["irs_1031"]},
        {"cells": ["Imputed rent", "A modeling convention that values the housing a resident owner receives by occupying a property they could otherwise let, usually gross market rent net of operating load.", "It is not income to anyone, not deductible by anyone and not taxable; it exists so that occupying and letting are compared on the same line."], "status": "Guidance", "sources": ["irs_rental"]},
        {"cells": ["Rent hurdle and break-even rent", "Two derived numbers, not market data: the hurdle is the gross rent a rented path must earn to offset the property-tax branch difference; the break-even is the rent at which letting overtakes the value of the Proposition 19 relief alone.", "They differ because of how the operating load treats the tax line. Both move with the assessor's actual levy, so read the bill first."], "status": "Projection", "sources": ["owner_a", "irs_rental"]},
        {"cells": ["Tax rate area", "The parcel-level levy jurisdiction used in Santa Clara County's published rate compilation; 816 areas exist for fiscal 2025-26 and the first two digits identify the city or unsecured area.", "It is read off the parcel's own bill. The number is a parcel identifier, so it is deliberately not published on this site."], "status": "Verified", "sources": ["scc_tax_rates"]},
        {"cells": ["Supplemental assessment", "A separate, prorated bill issued when a change in ownership or new construction causes reassessment, appealable within 60 days of the notice and usually not handled inside escrow.", "It can arrive against the estate in the transfer year, before or without a sale."], "status": "Verified", "sources": ["scc_assessor_2026"]},
        {"cells": ["Proposition H (San Francisco)", "The 15-year Muni parcel tax approved on November 3, 2026, billed with the property tax from fiscal 2027-28 through 2041-42, with separate single-family, multifamily, commercial and vacant-land rates and a limited pass-through for rent-controlled owners.", "It is an owner-paid parcel tax, not a rent regulation, and it belongs in Property B's carrying stack in every path."], "status": "Verified", "sources": ["sfmta_prop_h", "sf_elections_2026"]},
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
        ("S11", "Sell path", "Take a priced transfer-year sale to the CPA before listing", "Run the same-tax-year sale case on the sale-timing page with the actual valuation date, then ask the two questions it depends on: is any gain left to defer under section 1031, and what would depreciation and recapture cost if the house is rented first.", "The stepped-up basis makes the transfer-year answer close to settled and every later year quantifiably more expensive; deciding after the property is listed turns a tax question into a closing-table negotiation.", ["irs_basis", "irs_1031", "irs_409", "ftb_cg"]),
        ("S12", "Property tax", "Reconcile Property A's bill against the published levy before trusting any tax line", "Read the rate area and each bill line, compare them with the published levy structure, and settle the residual difference with the assessor's office rather than with an assumption.", "The modeled rate is derived from the owner's rounded figures and sits above the published levy example; the difference between those two numbers moves the ten-year property-tax result more than any investment assumption on this site.", ["scc_tax_rates", "scc_assessor_2026", "owner_a"]),
        ("S13", "Occupancy", "Decide the occupancy question in writing, before it is a deadline", "State whether the household will actually live in the inherited house as a principal residence, for how long, and what the plan is if that changes; then have counsel confirm the claim, the exemption filing and the removal rule.", "Proposition 19's family-home exclusion requires occupancy within one year with no exceptions, and losing occupancy pulls the exclusion back retroactively to a factored full-cash-value base — an intention that is never written down is usually the intention that fails.", ["boe_prop19", "boe_lta_2026_026", "ca_rtc63"]),
        ("S14", "San Francisco", "Calendar the Property B compliance items that now exist", "Add the Proposition H application and renewal dates, the parcel's area and classification check, the Rent Board registration for each unit, and the assessor's informal-review and appeal windows to the annual calendar.", "These are enacted, dated obligations with hard deadlines; a missed seniors application, a missed appeal window or an unregistered unit each costs money that no projection on this site can recover.", ["sfmta_prop_h", "sf_asr_page", "sf_rent_board"]),
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


def money(v: object) -> str:
    """Alias used by the sell-path pages so every published amount is rounded the same way."""
    return money10(float(v))


def svg_bar_chart(title: str, series: list[tuple[str, float, str]], width: int = 720, height: int = 260) -> str:
    """A dependency-free, inline-SVG scenario distribution chart.

    `series` is (label, value, colour-class). Values are drawn as a horizontal distribution
    so the chart stays readable at any width and needs no script, no canvas and no remote asset.
    """
    if not series:
        return ""
    top = max(value for _, value, _ in series) or 1.0
    bar_h = 26
    gap = 12
    label_w = 250
    value_w = 110
    plot_w = width - label_w - value_w - 20
    chart_h = height
    bars = []
    y = 24
    step = (chart_h - 60) / max(len(series), 1)
    for label, value, kind in series:
        w = max(2.0, plot_w * (value / top))
        bars.append(
            f'<g class="chart-row"><text class="chart-label" x="{label_w - 12}" y="{y + 12}" text-anchor="end">{esc(label)}</text>'
            f'<rect class="chart-bar {kind}" x="{label_w}" y="{y}" width="{w:.1f}" height="{bar_h}" rx="3"></rect>'
            f'<text class="chart-value" x="{label_w + w + 10:.1f}" y="{y + 12}">{esc(money10(value))}</text></g>'
        )
        y += step
    axis = (
        f'<line class="chart-axis" x1="{label_w}" y1="{chart_h - 26}" x2="{label_w + plot_w}" y2="{chart_h - 26}"></line>'
        f'<text class="chart-axis-label" x="{label_w}" y="{chart_h - 8}">0</text>'
        f'<text class="chart-axis-label" x="{label_w + plot_w}" y="{chart_h - 8}" text-anchor="end">{esc(money10(top))}</text>'
    )
    return (
        f'<figure class="chart"><svg viewBox="0 0 {width} {chart_h}" role="img" '
        f'aria-label="{esc(title)}: horizontal bar chart of modeled amounts, all rounded to the nearest ten dollars">'
        f'<title>{esc(title)}</title>{"".join(bars)}{axis}</svg>'
        f'<figcaption>{esc(title)} — modeled amounts, rounded to the nearest ten dollars; '
        'not a prediction. The figures below repeat the same numbers as text for screen readers and print.</figcaption></figure>'
    )


def build_requirements_tracker() -> str:
    rows = []
    items = [
        ("Executive summary and first-screen answer changers", "The overview page leads with the facts that change the answer, and the computed headlines are derived from the model rather than typed into prose.", "Handled", "pages/executive-summary.html", "Keep the first-screen gates current as private records arrive.", ["irs_estate_faq", "boe_prop19"]),
        ("Complete list of requirements and missing information", "This page is that register: every requirement the owner listed, mapped to where the site treats it now.", "Handled", "pages/requirements-tracker.html", "Update a row only after the official source or private record has been checked.", ["irs_estate", "boe_prop19"]),
        ("Privacy: rounded figures, no identifiers", "Owner-supplied figures are published rounded to the nearest ten dollars and badged Owner-supplied (privacy-rounded); names, addresses, parcel and account identifiers are banned by a mechanical check that fails the build.", "Handled", "pages/privacy.html", "Re-read the privacy page after any new figure is added; rounding is not anonymisation.", ["owner_a", "owner_b", "github_history"]),
        ("Prior public exposure and history scrub", "The exposure audit, the pattern counts and the runbook are published; the scrub itself needs repository-owner authority and cannot be done from a session branch.", "Open — owner action", "pages/flagged-for-review.html", "Owner/admin to run the prepared scrub procedure and open the GitHub Support request.", ["github_history"]),
        ("Estate and property inventory", "No inventory is stored here; the pages name the documents the estate and both holdings require.", "Open — private step", "pages/questions.html", "Build an encrypted private inventory: trust, deed, debt, prior gifts, basis, bills, leases, liquidity.", ["irs_estate", "irs_basis"]),
        ("Independent value and condition evidence", "The written date-of-death valuation is specified as an engagement with a stated purpose covering four uses, not an online estimate.", "Handled", "pages/sale-timing.html", "Commission the appraisal; record its date and comparable set in the decision log.", ["irs_706", "irs_basis"]),
        ("Year-by-year value, assessed value, tax and cost projections", "The worksheet publishes 2026-2050 columns for both buildings in both Prop 19 branches, plus a slow/base/fast value distribution and an inline chart.", "Handled", "pages/projections.html", "Re-run annually with the inputs below; do not extend the published baselines as if they were forecasts.", ["fhfa_hpi", "ca_rtc51", "cbo_ltbo"]),
        ("Property A tax-rate area and published rate", "The lookup method, the 816-area structure and the county's worked example are published; Property A's own area number is deliberately not printed and the residual discrepancy is shown as unresolved.", "Handled with a flag", "pages/property-tax.html", "Read the rate area off the parcel's own bill and reconcile the residual with the assessor.", ["scc_tax_rates", "scc_assessor_2026", "owner_a"]),
        ("Estate tax, income-tax basis and property-tax assessment kept separate", "Three separate workstreams with three separate clocks are stated on the estate-thresholds, sale-timing and property-tax pages.", "Handled", "pages/estate-thresholds.html", "Have the CPA and the assessor reconcile them independently; do not let one number answer all three.", ["irs_estate", "irs_basis", "ca_rtc51"]),
        ("Proposition 19 eligibility and long-term occupancy", "The occupancy rule is stated as a hard rule with its one-year clock, its retroactive removal on stopping occupancy, and a break-even against rent.", "Handled", "pages/sale-timing.html", "Claim only if legal eligibility is confirmed and the household intends to occupy long term; get that intent in writing.", ["boe_prop19", "ca_rtc63", "boe_lta_2026_026"]),
        ("Carry the Proposition 19 allowance forward", "The value-limit formula is modeled as the binding cap, and the separate replacement-home base-year-value transfer is documented with its two-year and three-transfer conditions.", "Handled with a flag", "pages/property-tax.html", "Use the BOE amount effective at transfer, and re-read the value-limit indexing rather than the figure published here.", ["boe_prop19", "boe_lta_2026_026"]),
        ("Sale in the same tax year as the inheritance", "Modeled first, as the owner asked: the transfer-year sale case sits above the four exit-year cases and the site's headline prose derives from it.", "Handled", "pages/sale-timing.html", "Have the CPA apply the actual date-of-death basis, sale date and that year's rules.", ["irs_basis", "irs_1041sd", "irs_409"]),
        ("Main-home exclusion for a live-then-sell path", "A switch in the local tool and a dedicated row in the exit-case table model the two-out-of-five-year tests and the single-filer exclusion.", "Handled", "pages/sale-timing.html", "Confirm the occupancy timeline before relying on the exclusion.", ["irs_topic701"]),
        ("Depreciation and recapture", "A rented hold reduces basis by straight-line depreciation over an assumed 27.5-year life, and the recapture is taxed at 25% at sale; both are modeled and exposed as controls.", "Handled", "pages/capital-plan.html", "Have the CPA rebuild depreciation allowed or allowable from the actual returns.", ["irs_rental", "irs_409", "irs_basis"]),
        ("Like-kind exchange decision before selling", "A dedicated section states what section 1031 now covers, why a stepped-up basis usually makes it pointless, and what it costs; the answer is to be written down before listing.", "Handled", "pages/sale-timing.html", "Ask counsel and the CPA before the property is listed, not at closing.", ["irs_1031"]),
        ("Leases, lawful units and local rules", "Property B's unit count, registration and covered-increase cap are carried as required verifications, and unverified unit rent is never counted.", "Open — private step", "pages/questions.html", "Reconcile permits, leases, registrations and deposits with counsel before projecting any unit's rent.", ["irs_rental", "ca_rent", "sf_rent_board"]),
        ("Insurance, utilities, water, electricity and solar", "Owner-supplied bands are published rounded and badged, with the insurance market treated as a stressed input; no regional average is presented as this household's premium.", "Handled with a flag", "pages/operating-costs.html", "Collect written use-specific quotes, current bills, and the signed solar tariff and interconnection documents.", ["cdi", "cdi_sis", "cpuc_solar", "sfpuc_rates"]),
        ("Imputed rent for living paths", "Ten years of imputed rent, net of the assumed operating load, sits beside the Proposition 19 relief on both the break-even table and the local tool, and is labeled as a modeling convention.", "Handled", "pages/decision-analysis.html", "Replace the band with a written comparable study when one exists.", ["owner_a", "irs_rental"]),
        ("Five-year maintenance and capital plan for both buildings", "A dated item plan for each building, with class labels, reserve bands sized as a share of value, and an annual reconciliation step.", "Handled", "pages/capital-plan.html", "Replace every band with a licensed bid; keep the plan as the calendar those bids attach to.", ["cslb", "irs_rental"]),
        ("Market rent on Property A, or letting treated as a floor", "The site states plainly that the only rent evidence available is third-party listing aggregates, publishes it rounded, and treats every rent-driven result as a floor until a written comparable exists.", "Handled with a flag", "pages/projections.html", "Commission written rent comparables; the ranking is provisional until then.", ["owner_a", "hud_fmr"]),
        ("Transfer tax and recording fees on a sale", "Priced line by line: the county rate, the city add-on rule, the per-title and PCOR charges, who owes the tax, and the statutory exemption for a death or trust transfer.", "Handled", "pages/sale-timing.html", "Have the preparer state the exemption basis on the face of the deed before recording.", ["rtc_11911", "rtc_11930", "scc_recording_fees"]),
        ("Same dates, horizons, taxes, debt, occupancy, costs and liquidity", "The comparison rule on the paths page requires identical dates and the full cost stack for every path, pure or mixed.", "Handled", "pages/decision-analysis.html", "Re-run all paths together whenever one input changes; a partial re-run is a biased re-run.", ["irs_estate", "irs_rental", "cdi"]),
        ("Mixed paths beside pure choices", "Mixed paths (occupy one unit, rent lawful units, sell one asset, short holds) are ranked alongside the pure choices rather than appended as footnotes.", "Handled", "pages/decision-analysis.html", "Only rank a mixed path after leases, eligibility and transition costs are verified.", ["boe_prop19", "irs_rental", "irs_topic701"]),
        ("Black-swan conditions and 1929/2008 entry risk", "Historical drawdown anchors are distinguished from probabilities, and both crash-timing directions are computed in the local staging tool.", "Handled", "pages/black-swan.html", "Stress lower renewal yields alongside the crash cases; historical anchors are severity, not likelihood.", ["fed_1929", "fed_2008", "treasury_bills"]),
        ("California tax treatment of a sale gain", "Ordinary-income treatment and the additional 1 percent above one million dollars of taxable income are cited to the FTB page and the statute, and are inside the exit-case math.", "Handled", "pages/sale-timing.html", "Re-read the current Form 540 instructions in the sale year; the full booklet was not retrieved for this build.", ["ftb_cg", "rtc_17043"]),
        ("Federal estate threshold, portability and prior gifts", "The estate-thresholds page now carries the liquidity plan, the portability question and the adjusted-taxable-gifts question as explicit rows.", "Handled", "pages/estate-thresholds.html", "Ask now about prior gifts and any earlier portability election; do not wait for the transfer.", ["irs_estate", "irs_estate_faq", "irs_706"]),
        ("Investment policy written before proceeds arrive", "A ten-section policy with staging and renewal rules, rebalance bands, prohibited actions, review cadence and reversal conditions, plus the yield and risk facts it must state honestly.", "Handled", "pages/investment-policy.html", "Sign and date it, then record which version applied when in the decision log.", ["sec_stocks", "treasury_bills", "cbo_rates"]),
        ("Annual model re-run and law-change watch", "A re-run protocol with cadences and windows is published on the capital plan page, and the watchlist separates enacted changes from proposals.", "Handled", "pages/law-watchlist.html", "Log each re-run date; treat a proposal as a proposal until it is chaptered.", ["boe_pub29", "ca_legislation", "irs_2027"]),
        ("San Francisco Proposition H", "Modeled as the enacted owner-paid parcel tax it is (approved November 3, 2026), with the SFMTA's published schedule, the pass-through cap and the seniors application window.", "Result uncertified", "pages/property-tax.html", "Confirm the certified canvass and the parcel's area and classification before relying on the amount.", ["sfmta_prop_h", "sf_elections_2026"]),
        ("Step-by-step inheritance process and deadlines", "The deadline timeline carries the 60-day trust notice, the 150-day change-in-ownership statement, the nine-month return, the one-year occupancy and exemption clocks and the three-year claim window.", "Handled", "pages/inheritance-process.html", "Calendar each clock from its own trigger; a late claim can be prospective only.", ["ca_prob160617", "ca_rtc480", "irs_estate_faq", "boe_prop19"]),
        ("Printable adviser handoff", "The attorney and CPA brief now carries the new questions: the valuation engagement scope, the exchange decision, the occupancy intent, the exemption recital and the San Francisco compliance items.", "Handled", "pages/attorney-cpa-brief.html", "Print it, and record the answers back into the decision log.", ["irs_estate_faq", "boe_prop19", "rtc_11930"]),
    ]
    for requirement, treatment, status, target, next_step, sources in items:
        rows.append({
            "cells": [requirement, treatment,
                      SafeHTML(f'<a class="source" href="{esc(root_href("pages/requirements-tracker.html", target))}">{esc(target.split("/")[-1].replace(".html", "").replace("-", " "))}</a>'),
                      next_step],
            "status": status,
            "sources": list(sources),
        })
    body = callout(
        "Every requirement, one register",
        "The owner's instruction list is long, and the honest answer to most of it is 'the method is published, the private record is not'. This register keeps both halves visible: what the site now does about each requirement, and the one next action that would close it. "
        "Rows marked Open are not oversights in the analysis — they are questions that cannot be answered from public sources for a private parcel.",
        "info",
    )
    body += make_table("Requirements register — treatment and next step", ["Requirement", "How this site treats it now", "Where", "Next step"], rows,
                       "Statuses are evidence statuses, not completion grades: Handled means the method and its sources are published here, not that the household's question is answered. A row is closed only when the named private record exists.")
    body += cards("Closely related", [
        ("Questions & missing evidence", "The question-by-question record list for counsel, CPA, assessor and insurer.", "pages/questions.html"),
        ("Flagged for review", "Everything that could not be verified from an official source, listed rather than smoothed over.", "pages/flagged-for-review.html"),
        ("Decision log", "The recorded decisions, including the model correction and the reclassification of Proposition H.", "pages/decision-log.html"),
    ], current="pages/requirements-tracker.html")
    return render_page("pages/requirements-tracker.html", "Requirements tracker",
                       "Every requirement from the owner's list mapped to how this workspace treats it now, where it lives, and the next step that would close it.", body, "DECISION")


def build_sale_timing() -> str:
    body = callout(
        "Do this first: price a sale in the tax year of the inheritance",
        "A sale in the same tax year as the transfer is modeled first because it is the only branch whose income-tax answer is close to settled before the numbers arrive. "
        "Inherited property generally takes a date-of-death value as its income-tax basis, and the IRS states that a sale soon after the date of death therefore usually shows little or no gain. "
        "Every later year of holding converts tax-free appreciation into a taxable gain, and renting the house converts part of that gain into depreciation recapture. Price the same-year sale first, "
        "then ask what a later sale costs — not the other way round.",
        "info",
    )
    rule_rows = [
        {"cells": ["Income-tax basis at death", "Basis of property acquired from a decedent is generally its fair market value at the date of death, and the IRS adds that a sale soon after the date of death usually produces little or no gain.", "A sale in the transfer year is close to income-tax-free federally; do not assume the same for a later year."],
         "status": "Verified", "sources": ["irs_basis", "irs_estate_faq"]},
        {"cells": ["Holding period", "The Schedule D instructions for estates and trusts state that property acquired from a decedent is treated as held for more than one year.", "Any gain on an early sale is already long-term, so no waiting period is needed to reach the preferential federal rate."],
         "status": "Verified", "sources": ["irs_1041sd"]},
        {"cells": ["California has no preferential rate", "California does not have a lower rate for capital gains: all capital gains are taxed as ordinary income.", "A delayed sale moves post-death appreciation into ordinary-rate state income, which is where the timing cost concentrates."],
         "status": "Verified", "sources": ["ftb_cg"]},
        {"cells": ["The one-million-dollar surcharge", "An additional 1 percent tax applies to the portion of taxable income above $1,000,000, and the credits and recomputation provisions do not reduce it.", "On a large post-death gain the surcharge is a real layer; it is modeled on top of the top bracket here."],
         "status": "Verified", "sources": ["rtc_17043"]},
        {"cells": ["Rate bands that do apply federally", "Maximum federal long-term rates are 0, 15 and 20 percent by taxable income, and unrecaptured section 1250 gain is taxed at a maximum of 25 percent.", "The recapture rate is the number a rented path has to carry; it is not the same rate as the gain it sits beside."],
         "status": "Verified", "sources": ["irs_409"]},
        {"cells": ["Main-home exclusion", "Up to $250,000 of gain ($500,000 on a joint return) can be excluded on a main home when the ownership and use tests for the prior five years are met.", "The heir earns this only by living in the home for two of the five years before the sale; renting does not build it."],
         "status": "Verified", "sources": ["irs_topic701"]},
        {"cells": ["Assessment is set at death, not at distribution", "The Santa Clara County Assessor states that reassessment of property acquired by inheritance from an estate or living trust occurs as of the date of death rather than the distribution date, and that an assessment will be made in the name of the estate even if the property is sold instead of distributed.", "Delaying the sale does not defer the property-tax consequence of the transfer; a supplemental bill can be issued against the estate."],
         "status": "Verified", "sources": ["scc_assessor_2026"]},
        {"cells": ["Supplemental bills are separate and time-limited", "A supplemental assessment is issued whenever a change of ownership or new construction causes reassessment, measured against the prior value and prorated for the months left in the fiscal year ending June 30; it is billed separately, is usually not prorated in escrow and not paid from an impound account, and an appeal of the value or the reassessment decision is due within 60 days of the notice.", "Budget a possible supplemental bill in the transfer year and calendar the 60-day appeal window as a hard deadline."],
         "status": "Verified", "sources": ["scc_assessor_2026"]},
    ]
    body += make_table("What a same-tax-year sale does — and does not do", ["Rule", "What the official source states", "Effect on the decision"], rule_rows,
                       "These rows describe the tax system, not this household's tax position. Only the estate's actual valuation date, basis, deductions and the assessor's determination can settle a real sale.")

    case_rows = []
    for label, case, note in (
        ("Sell in the transfer year (modeled 2045)", SALE_NOW, "Gain is the difference between the sale price and the date-of-death value; the model sets it to zero because both use the same date and the same value."),
        ("Live in it five years, then sell — main-home tests met", SALE_LATER_LIVE, "Five more years of appreciation is taxable, but the exclusion removes the first $250,000 of the remaining gain for a single filer who meets the two-out-of-five-year tests."),
        ("Hold five years and sell — never a principal residence", SALE_LATER_IDLE, "Identical appreciation to the row above with no exclusion available: this is the cost of a hold that never became a home."),
        ("Rent it for five years, then sell", SALE_LATER_RENT, "Renting adds depreciation now and converts that depreciation into taxable unrecaptured section 1250 gain later, on top of the appreciation."),
    ):
        case_rows.append({
            "cells": [label, str(case["sale_year"]), money10(case["price"]),
                      money10_zero(case["gain"], "none (sale and basis share the modeled date)"),
                      money10_zero(case["taxes"]),
                      money10(case["selling"] + case["dtt"]), money10(case["net"]), note],
            "status": "Projection", "sources": ["owner_a", "irs_basis", "ftb_cg", "irs_409", "irs_topic701", "scc_recording", "cbo_rates"],
        })
    body += make_table("Modeled exit years — same asset, same assumptions, different timing",
                       ["Exit case", "Sale year", "Modeled sale price", "Taxable gain", "Income tax (federal + net investment income + California)",
                        "Selling costs and transfer tax", "Modeled net proceeds", "What drives the difference"],
                       case_rows,
                       "Method, stated so it can be re-run: sale price = the 4% market-growth scenario applied to the owner-supplied rounded 2026 value; basis = the modeled 2045 date-of-death value; a rented hold reduces basis by straight-line depreciation of the building share (assumed 80% of value over 27.5 years); federal tax at 20% on long-term gain and 25% on unrecaptured section 1250 gain, plus the 3.8% net investment income tax; California at 13.3% (a 12.3% top bracket plus the additional 1% above $1,000,000); selling costs at the assumed 7%; Santa Clara County documentary transfer tax at 0.11% of the consideration. No deduction interactions, no state exclusion conformity analysis, no allocation between heirs and no alternate-valuation election are modeled, and every figure is rounded to the nearest ten dollars. This is an illustrative sensitivity, not a tax calculation.")
    body += callout(
        "The number the timing question turns on",
        "Under these assumptions, waiting five years and renting costs about " + money10(COST_OF_WAITING_RENT) + " of net proceeds relative to selling in the transfer year — before counting five years of property tax, insurance, maintenance and vacancy on one side against five years of rent on the other. "
        "Timing is decided before investing, because it sets how much of the proceeds are actually investable.",
        "warning",
    )
    body += svg_bar_chart("Modeled net proceeds by exit year (Property A, same asset, same assumptions)",
                          [(label, case["net"], kind) for (label, case, kind) in [
                              ("Sell in the transfer year", SALE_NOW, "bar-a"),
                              ("Live five years, then sell", SALE_LATER_LIVE, "bar-b"),
                              ("Hold five years, no exclusion", SALE_LATER_IDLE, "bar-c"),
                              ("Rent five years, then sell", SALE_LATER_RENT, "bar-d"),
                          ]] )

    cost_rows = [
        {"cells": ["County documentary transfer tax", "The county and any participating board may tax each deed conveying realty sold at 55 cents for each $500 of consideration or value exclusive of liens that remain, on instruments over 100 dollars; a city inside a taxing county may add half that amount, credited against the county tax.", "About " + money10(SALE_NOW["dtt"]) + " on the modeled 2045 sale price"],
         "status": "Verified", "sources": ["rtc_11911", "scc_recording"]},
        {"cells": ["City conveyance add-on", "The recorder's fee schedule lists a higher combined rate for San Jose, Palo Alto and Mountain View; no city add-on is listed for the Cupertino area, so the county rate is the planning figure.", "None assumed"],
         "status": "Verified", "sources": ["scc_recording_fees"]},
        {"cells": ["Who owes it", "The statute places the tax on the person who makes, signs or issues the instrument, or for whose benefit it is made — which is why the seller customarily bears it at closing.", "Seller side of the ledger"],
         "status": "Verified", "sources": ["rtc_11912"]},
        {"cells": ["Recording and per-title charges", "Recorded documents carry per-page, indexing and title fees, including a state charge of 75 dollars for each real-estate title, plus an additional 20 dollars when a required preliminary change-of-ownership report is missing or incomplete.", "Budget a small fixed allowance, not zero"],
         "status": "Verified", "sources": ["scc_recording_fees"]},
        {"cells": ["The transfer at death or out of the trust", "Section 11930 of the Documentary Transfer Tax Act states that the tax does not apply to a deed or other writing by which realty is transferred outright to, or in trust for the benefit of, any person or entity by reason of an inter vivos gift or by reason of a death.", "No transfer tax is modeled on the inheritance step itself — but the exemption is for that step only, so it does not shelter the later sale to a buyer"],
         "status": "Verified", "sources": ["rtc_11930"]},
        {"cells": ["How an exemption has to be claimed", "Section 11932 requires every document subject to tax to show on its face the amount of tax due and the location of the realty; the spousal exemption in §11927 is expressly conditioned on a written recital signed by a spouse stating that the instrument is entitled to the exemption; and the recorder likewise requires a claimed exemption to be stated on the face of the deed with the tax shown as zero.", "Do not rely on an exemption being recognised after the fact: have the preparer write the statutory basis on the document before recording"],
         "status": "Verified", "sources": ["rtc_11932", "rtc_11927", "scc_recording"]},
        {"cells": ["San Francisco transfer tax, if Property B is ever sold", "San Francisco taxes real property transfers on a tiered schedule; the City's own rate pages returned 404 when fetched on 2026-11-15, so no rate, tier or exemption is stated here.", "—"],
         "status": "Not verified", "sources": ["sf_asr_page"]},
        {"cells": ["Commissions, escrow and title", "No public source sets a commission, management or escrow fee; the model carries an assumed 7% combined cost band and the real figure comes from the listing agreement and the closing statement.", "About " + money10(SALE_NOW["selling"]) + " under the 7% assumption"],
         "status": "Assumption", "sources": ["owner_a"]},
        {"cells": ["Possible supplemental tax bill", "Prorated to the months remaining in the fiscal year after the reassessment, billed separately from the regular bill, and generally not handled inside escrow.", "Model it; the amount depends on the assessor's value, not on the sale price"],
         "status": "Projection", "sources": ["scc_assessor_2026"]},
    ]
    body += make_table("Price the sell path, line by line", ["Item", "What the official source says", "Modeled effect at the 2045 sale"], cost_rows,
                       "Transfer taxes and recording charges are small beside the property-tax and income-tax branches, which is exactly why they belong in the same table: a sell path that ignores them is not fully priced.")

    val_rows = [
        {"cells": ["Who values it", "The estate reports fair market value on Schedule A of Form 706; the county assessor separately appraises to set a new base year value whenever a reassessment is required.", "Two valuations with two purposes and possibly two numbers — do not substitute one for the other."],
         "status": "Verified", "sources": ["irs_706", "scc_assessor_2026"]},
        {"cells": ["The standard to demand", "Fair market value is the price at which property would change hands between a willing buyer and a willing seller, neither under any compulsion and both having reasonable knowledge of relevant facts; the IRS adds that a forced-sale price is not fair market value.", "Require the valuation date, the comparable set and a written reasonableness range in the engagement letter."],
        "status": "Verified", "sources": ["irs_estate_faq", "irs_706"]},
        {"cells": ["Alternate valuation", "The estate may elect to value property as of six months after death — and as of the date of sale or distribution inside that window — only if doing so reduces both the gross estate and the combined estate and generation-skipping transfer tax; the trust Schedule D instructions state that basis follows the alternate-valuation figure.", "A sale signed inside the six-month window can tie the estate value and the heir's basis to one number, which is a further argument for pricing an early sale."],
         "status": "Verified", "sources": ["irs_706", "irs_1041sd"]},
        {"cells": ["Basis consistency", "Basis for inherited property is generally the date-of-death value and is subject to the consistent-basis rules that tie a beneficiary's basis to the value reported for estate-tax purposes.", "Do not spend an appreciated basis before the executor's statement arrives; ask the CPA which figure will govern."],
         "status": "Verified", "sources": ["irs_basis"]},
        {"cells": ["Special-use and family-farm valuation", "Form 706 provides for electing special-use valuation of qualifying family farm and closely held business real property, reported with the return; the schedules read in this session were A (real estate), K (adjusted taxable gifts), M, O, PC, Q, T and U.", "Not a residential planning tool; note it only if the trust holds qualifying land, and read the schedule text before assuming an election is available."],
         "status": "Cross-checked", "sources": ["irs_706"]},
        {"cells": ["What the appraisal is for", "The same written number feeds four analyses: the estate-tax computation, the heir's income-tax basis, the sale-timing sensitivity and the assessor's comparison.", "Commission one appraisal with a stated purpose covering all four, and record its date and assumptions in the decision log."],
         "status": "Guidance", "sources": ["irs_706", "irs_basis"]},
    ]
    body += make_table("Obtain a written valuation of the inherited house at the date of death", ["Question", "What the official source establishes", "What to require in the engagement"], val_rows,
                       "A written appraisal dated to the valuation date, with comparable sales and a reasonableness range, is the single document that makes the sale-timing, estate-tax and basis analyses comparable. A listing price, an insurance figure or an online estimate is not that document.")

    kc_rows = [
        {"cells": ["What survives today", "A like-kind exchange defers gain when real property used in a business or held for investment is exchanged solely for other business or investment real property; the Tax Cuts and Jobs Act limited it to real property, and property held primarily for sale never qualified.", "It is an investment-property tool, not a way to defer tax on selling an inherited family home for cash."],
         "status": "Verified", "sources": ["irs_1031"]},
        {"cells": ["Why it is usually unnecessary here", "Because the inherited basis is generally the date-of-death value, an early sale produces little or no gain to defer; deferring zero gain buys nothing and adds intermediary fees and strict deadlines.", "Decide this before listing. The answer is probably no, and writing that down is the point."],
         "status": "Guidance", "sources": ["irs_1031", "irs_basis"]},
        {"cells": ["When it becomes attractive", "If the heir holds the house as a rental for years, accumulated appreciation and depreciation become taxable, and an exchange can defer them into replacement real property with the basis carried over; the deferral is reported on Form 8824.", "Only worth discussing after a rental decision is made, with a CPA and a qualified intermediary engaged before closing."],
         "status": "Verified", "sources": ["irs_1031"]},
        {"cells": ["What it costs you", "Boot or cash received triggers gain to that extent, losses are not recognized in the exchange, and the replacement property inherits the old basis, so the deferred gain travels with it.", "Compare against simply paying tax on a stepped-up basis — often the cheaper option for inherited property."],
         "status": "Verified", "sources": ["irs_1031"]},
        {"cells": ["The California layer", "California computes gain on its own schedule and taxes all capital gains as ordinary income, so a deferral analyzed only at the federal level is incomplete.", "Have the CPA confirm state treatment and any add-back before calling a deferral a saving."],
         "status": "Verified", "sources": ["ftb_cg"]},
    ]
    body += make_table("Decide whether a like-kind exchange is wanted — before listing", ["Question", "Official rule", "Planning consequence"], kc_rows,
                       "This table deliberately stops short of a recommendation: whether an exchange is available turns on the heir's use, holding intent and the property's role, all of which are professional determinations.")

    carry_rows = [
        {"cells": ["The occupancy rule, stated exactly", "The Proposition 19 family-home exclusion applies to a principal residence of the transferor, the transfer must be to a child or grandchild, the excluded amount is the factored base year value plus the adjusted value-limit amount, and the transferee must occupy the home as a principal residence within one year of the transfer — the BOE states plainly that there are no exceptions.", "So the exclusion is not a rental-planning tool: it is available only if the household intends to live in the house, long term."],
         "status": "Verified", "sources": ["boe_prop19", "boe_lta_2026_026"]},
        {"cells": ["Death and trust transfers count", "The BOE letter to assessors confirms that a transfer includes a transfer at death and a transfer through a trust, so the inherited-house path is inside the rule rather than beside it.", "The one-year occupancy clock runs from the date of death or the transfer, not from the day the paperwork is finished."],
         "status": "Verified", "sources": ["boe_lta_2026_026"]},
        {"cells": ["The value limit caps the benefit", "The excluded amount is the factored base year value immediately before the transfer plus the adjusted limit (the 2025-2027 amount is $1,044,586), and any excess of full cash value over that sum is added to the base and then indexed annually.", "On the modeled Property A figures the value limit is what does the work: the relief is worth about " + money10(PROP19_RELIEF_2045) + " a year, not the whole gap between the old and the new tax base."],
         "status": "Projection", "sources": ["boe_prop19", "ca_rtc63", "owner_a"]},
        {"cells": ["Occupancy must be continuous", "If the transferee stops using the home as a principal residence, the exclusion is removed at the next lien date and the enrolled value reverts to the date-of-transfer full cash value factored forward — the relief is pulled back retroactively, not merely stopped.", "A plan that occupies for three years and then rents is not a plan with a preserved base; it is a plan with a delayed reassessment."],
         "status": "Verified", "sources": ["boe_lta_2026_026", "ca_rtc63"]},
        {"cells": ["The claims, both of them", "The exclusion claim is generally filed within three years of the transfer or before a transfer to a third party, and the homeowners' or disabled veterans' exemption must be claimed within one year; a late claim generally gives relief only from the year of filing forward.", "Calendar both dates independently, and budget the higher bill until a claim is processed."],
         "status": "Verified", "sources": ["boe_prop19", "ca_rtc218"]},
        {"cells": ["The separate base-year-value transfer", "A claimant who sells a principal residence may transfer its factored base year value to a replacement principal residence purchased or newly built within two years, anywhere in California, with the value above the original added to the transferred base; up to three transfers are allowed, subject to the age-55, disability or disaster conditions.", "This is the allowance carried forward — a second, separate benefit with its own conditions, available to the heir as owner, not to the estate."],
         "status": "Verified", "sources": ["boe_prop19"]},
        {"cells": ["Break-even for occupying", "Occupying preserves about " + money10(PROP19_RELIEF_2045) + " a year of property tax under the modeled 2045 figures, roughly " + money10(PROP19_10YR_RELIEF) + " over ten years. Letting the house instead earns gross rent net of an operating load that already excludes the property-tax line, so the two paths cross at about " + money10(PROP19_BREAKEVEN_MONTH) + " of gross monthly rent.", "Above that rent the tax-and-carry arithmetic favors letting; below it, occupying wins. The comparison ignores the outside rent an occupant would otherwise pay, which is usually the larger term and points the other way."],
         "status": "Projection", "sources": ["owner_a", "boe_prop19", "ca_rtc63", "irs_rental"]},
        {"cells": ["Multi-unit buildings are tested per unit", "The BOE guidance states that each unit of a multi-unit property is separately eligible or ineligible, and that a property is tested as a family home only where the transferor owned and occupied it.", "Property B's rented units are not covered by the transferor's occupancy; do not carry a single-family conclusion across to a three-unit building."],
         "status": "Verified", "sources": ["boe_lta_2026_026", "ca_rtc63"]},
    ]
    body += make_table("The Proposition 19 occupancy rule, and the allowance carried forward", ["Element", "Current official rule", "Why it matters to this decision"], carry_rows,
                       "Read the exclusion and the base-year-value transfer as two different benefits with two different tests. Neither is available on paper alone, and neither survives a decision to rent immediately.")
    body += '''<section class="tool-section" aria-labelledby="carry-tool-heading">
<h2 id="carry-tool-heading">Carry-or-sell what-if controls — local only</h2>
<p class="table-note">Change an input and the numbers recompute in this browser. Defaults mirror the published baseline (a modeled 2045 transfer of the rounded owner-supplied value). Nothing is stored, submitted or transmitted; the tool does not compute an actual tax return.</p>
<form id="carry-tool" class="tool-grid">
<label>Modeled value at transfer<input id="carry-value" type="number" min="0" max="99999999" step="10" value="6531230" inputmode="numeric"></label>
<label>Years held after transfer<input id="carry-hold" type="number" min="0" max="30" step="1" value="5" inputmode="numeric"></label>
<label>Market growth assumption (%)<input id="carry-growth" type="number" min="0" max="12" step="0.1" value="4" inputmode="decimal"></label>
<label>Effective tax rate (%)<input id="carry-rate" type="number" min="0" max="5" step="0.01" value="1.34" inputmode="decimal"></label>
<label>Prop 19 value limit at transfer<input id="carry-limit" type="number" min="0" max="99999999" step="10" value="1886640" inputmode="numeric"></label>
<label>Factored base year value carried in<input id="carry-base" type="number" min="0" max="99999999" step="10" value="802030" inputmode="numeric"></label>
<label>Gross monthly rent available on A<input id="carry-rent" type="number" min="0" max="100000" step="10" value="5550" inputmode="numeric"></label>
<label>Rent operating load (%)<input id="carry-load" type="number" min="0" max="90" step="1" value="35" inputmode="decimal"></label>
<label>Use during the hold<select id="carry-use"><option value="own">Occupy; Proposition 19 claimed</option><option value="own121">Occupy two of five years, then sell (section 121 available)</option><option value="rent">Rent it out (depreciation, then recapture)</option><option value="vacant">Hold vacant, no exclusion, no rent</option></select></label>
<label class="tool-check"><input id="carry-forward" type="checkbox"> Carry the base-year value forward to a replacement home</label>
<div class="tool-actions no-print"><button id="carry-reset" type="button">Reset to baseline</button><span class="tool-assumption">Derived amounts display rounded to the nearest $10; a modeled zero prints as "none modeled".</span></div>
</form>
<div class="scenario-grid" aria-live="polite">
<article class="scenario-card"><h3>Sale after the hold</h3><dl><dt>Modeled sale price</dt><dd id="carry-price">—</dd><dt>Taxable gain over the stepped-up basis</dt><dd id="carry-gain">—</dd><dt>Depreciation recapture inside the gain</dt><dd id="carry-recapture">—</dd><dt>Section 121 amount excluded</dt><dd id="carry-excluded">—</dd></dl></article>
<article class="scenario-card"><h3>What the exit costs</h3><dl><dt>Income tax (federal + net investment income + California)</dt><dd id="carry-taxes">—</dd><dt>Selling costs and transfer tax</dt><dd id="carry-costs">—</dd><dt>Net proceeds</dt><dd id="carry-net">—</dd></dl></article>
<article class="scenario-card"><h3>Property tax and occupancy</h3><dl><dt>Proposition 19 relief, year 1</dt><dd id="carry-relief">—</dd><dt>Relief over ten years (2% cap indexing)</dt><dd id="carry-relief10">—</dd><dt>Break-even gross monthly rent to prefer letting</dt><dd id="carry-breakeven">—</dd><dt>Imputed rent forgone by occupying, ten years</dt><dd id="carry-imputed">—</dd><dt>Value of the allowance carried forward, year 1</dt><dd id="carry-forward-value">—</dd></dl></article>
</div>
<p id="carry-status" class="tool-status" role="status">Change a control to rerun the local comparison.</p>
<p class="table-note">Model, stated so it can be checked: sale price = value at transfer grown at the entered rate for the hold years; basis = the date-of-death value, reduced by straight-line depreciation of an assumed 80% building share over 27.5 years when the use is "rent it out"; federal tax at 25% on recapture and 20% on other long-term gain, plus 3.8% net investment income tax; California at 13.3%; the single-filer main-home exclusion of $250,000 where the use is "occupy two of five years"; costs at 7% plus 0.11% transfer tax. Property-tax relief = (full value − max(carried base, value − limit)) × rate, indexed at the 2% cap. Imputed rent is gross rent net of the entered load over ten years: a modeling convention that puts the occupant's housing benefit on the same line as the rent a letting path would earn, and it is not income to anyone or taxable to anyone. Rates are the labeled assumptions of this site and change with the year of sale.</p>
</section>'''

    body += paragraph("How to use this page", "Run the same-year sale case first. Then decide in writing whether the household wants the property-tax benefit of occupancy, the income-tax benefit of an early sale, or a mixed path — and only then write the investing policy for whatever money is actually left. Re-run this page with the real valuation date, the assessor's determination and the CPA's basis schedule before anything is signed.")
    body += cards("Related pages", [
        ("Property-tax rules", "The rate structure, the levy decomposition and the occupancy conditions behind the numbers above.", "pages/property-tax.html"),
        ("Five-year capital plan", "What the house costs to hold while the decision stays open.", "pages/capital-plan.html"),
        ("Investment policy", "The written policy the proceeds need before they arrive.", "pages/investment-policy.html"),
        ("Deadline timeline", "The 60-day, 150-day, nine-month, one-year and three-year clocks in one view.", "pages/inheritance-process.html"),
    ], current="pages/sale-timing.html")
    return render_page("pages/sale-timing.html", "Sale timing and the tax year of the inheritance",
                       "Why a sale in the same tax year as the transfer is modeled first, what the sale actually costs line by line, what a written valuation has to settle, and the exact Proposition 19 occupancy rule with its break-even.",
                       body, "SELL PATH")


def build_capital_plan() -> str:
    body = callout(
        "Two buildings, two plans, one reserve discipline",
        "Maintenance and capital cost is the line most likely to move a projected winner into a loss — and the line with no official source: no government publication prices a private roof, sewer lateral or turnover package. "
        "Each plan below is a scheduling and reserve tool with amount bands, not an estimate of this household's costs. Replace every band with a licensed bid before it enters a comparison.",
        "warning",
    )
    body += callout(
        "Why both buildings get a plan, not just the inherited one",
        "Property B is already owned and already tenanted, so its capital needs are present-day cash flows that compete with whatever the household does about Property A. A plan that prices only the inherited house "
        "implicitly assumes the other building costs nothing to hold, which is the assumption most likely to reverse a ranking.",
        "info",
    )

    def plan_rows(plan):
        return [{"cells": [str(year), item, kind, note], "status": "Assumption",
                 "sources": ["irs_rental", "cslb"]} for year, item, kind, note in plan]

    body += make_table("Property A (Cupertino-area house) — five-year maintenance and capital plan", ["Year", "Item", "Class", "Why it is in the plan"], plan_rows(CAPITAL_PLAN_A),
                       "Owner-supplied context: the house is reported as a primary residence with solar generation and less maintenance demand than the San Francisco building. Repairs and improvements are separated because they are treated differently for tax, and because only improvements may add to basis.")
    body += make_table("Property B (San Francisco three-unit) — five-year maintenance and capital plan", ["Year", "Item", "Class", "Why it is in the plan"], plan_rows(CAPITAL_PLAN_B),
                       "A tenanted building carries legal and tenant-facing obligations a vacant house does not: registration, lawful rent, required devices and turnover standards all sit ahead of discretionary capital work.")

    reserve_rows = [
        {"cells": ["Property A — routine maintenance and repairs", money10(MAINT_A_BAND[0]) + " to " + money10(MAINT_A_BAND[1]), money10(A_MAINT_MID), "The owner reports lighter demand than the San Francisco building; a planning range, not a bid."], "status": "Assumption", "sources": ["owner_a", "cslb"]},
        {"cells": ["Property A — capital reserve on top of repairs", money10(A_RESERVE_BAND[0]) + " to " + money10(A_RESERVE_BAND[1]), money10(A_RESERVE_MID), "Sized as 0.5% to 1.0% of the modeled value (an assumption). Fund it in every path, including a sale, so the plan does not depend on the outcome."], "status": "Assumption", "sources": ["owner_a", "irs_rental"]},
        {"cells": ["Property A — insurance", money10(A_INS_BAND[0]) + " to " + money10(A_INS_BAND[1]), money10(A_INS_MID), "The owner's recollection sits at the bottom of the band; a written quote is required. California wildfire underwriting is volatile and renewal, not price, is the risk."], "status": "Owner-supplied (privacy-rounded)", "sources": ["cdi", "cdi_sis", "owner_a"]},
        {"cells": ["Property A — water and sewer", money10(PROPERTY_A["water_month"][0] * 12) + " to " + money10(PROPERTY_A["water_month"][1] * 12), money10(A_WATER_YEAR), "Owner-supplied monthly band for a Cupertino-area house; the provider's current rate schedule and the actual bill are the record."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_a", "sjw_rates"]},
        {"cells": ["Property A — electricity net of the solar credit", money10(PROPERTY_A["solar_credit_month"][0] * 12) + " credit to " + money10(PROPERTY_A["solar_credit_month"][1] * 12) + " credit", money10(-A_SOLAR_YEAR), "Reported as a small monthly net credit rather than a bill. The tariff, the true-up and inverter age decide the number; a credit is not income."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_a", "cpuc_solar"]},
        {"cells": ["Property B — maintenance and repairs", money10(B_MAINT_BAND[0]) + " to " + money10(B_MAINT_BAND[1]), money10(B_MAINT_MID), "An older three-unit building with tenants; the band is deliberately wider than Property A's."], "status": "Assumption", "sources": ["owner_b", "cslb"]},
        {"cells": ["Property B — capital reserve", money10(B_RESERVE_BAND[0]) + " to " + money10(B_RESERVE_BAND[1]), money10(B_RESERVE_MID), "Sized at 1.0% to 1.5% of value: an occupied building cannot defer a failed roof, boiler or lateral the way a vacant house can."], "status": "Assumption", "sources": ["owner_b", "irs_rental"]},
        {"cells": ["Property B — insurance", money10(B_INS_BAND[0]) + " to " + money10(B_INS_BAND[1]), money10(B_INS_MID), "A landlord or mixed-use form, not a homeowners policy; the owner's recollection is treated as a low anchor."], "status": "Owner-supplied (privacy-rounded)", "sources": ["cdi", "owner_b"]},
        {"cells": ["Property B — water for three units", money10(PROPERTY_B["water_month"][0] * 12) + " to " + money10(PROPERTY_B["water_month"][1] * 12), money10(B_WATER_YEAR), "Owner-supplied for the whole building. The SFPUC's 2026 rate notice publishes an average single-family combined bill near 171 dollars a month rising to 212 dollars by FYE 2028, and a multi-family tier structure; metering decides how much is recoverable."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "sfpuc_rates"]},
        {"cells": ["Property B — common-area electricity", money10(PROPERTY_B["electric_month"][0] * 12) + " to " + money10(PROPERTY_B["electric_month"][1] * 12), money10(B_ELEC_YEAR), "Owner-supplied band for common area only; separately metered tenants carry their own usage."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_b", "pge_tariffs"]},
        {"cells": ["Property B — Proposition H parcel tax from fiscal 2027-28", money10(prop_h_multifamily(5000)) + " up to " + money10(prop_h_multifamily(8000)), money10(prop_h_multifamily(6500)), "Approved by San Francisco voters on November 3, 2026 and effective through fiscal 2041-42; billed on the property-tax bill in two installments from fall 2027 and indexed for inflation. The exact amount depends on the parcel's building area and classification."], "status": "Projection", "sources": ["sfmta_prop_h", "sf_elections_2026"]},
        {"cells": ["Property B — rent increase that Proposition H allows to be passed through", money10(prop_h_passthrough(prop_h_multifamily(6500), 2)) + " a year across the two rented units", money10(prop_h_passthrough(prop_h_multifamily(6500), 2)), "The measure allows up to half of the tax to be passed through, capped at 65 dollars per unit per year, and only where the initial base rent predates June 1, 2027. Where it applies it offsets roughly a quarter of the tax, not all of it."], "status": "Projection", "sources": ["sfmta_prop_h", "sf_rent_board"]},
    ]
    body += make_table("Annual carrying-cost and reserve lines to fund in every path", ["Line", "Low to high band", "Planned midpoint", "Basis and limit"], reserve_rows,
                       "Bands are amounts a household can fund, not predictions. Every midpoint is an assumption to be replaced by a quote, a bid or a bill; property-specific amounts are rounded to the nearest ten dollars.")

    tax_rows = [
        {"cells": ["Repairs versus improvements", "IRS guidance on residential rental property separates deductible expenses and repairs from improvements, which are capitalized and recovered instead of deducted in the year paid.", "Classify every invoice in the year it is received; a misclassified repair becomes a basis error discovered years later."], "status": "Verified", "sources": ["irs_rental"]},
        {"cells": ["Depreciating the inherited house if it is rented", "Residential rental property is recovered straight line over 27.5 years, measured from the basis established for the property with land excluded.", "Depreciation shelters rent now and becomes a taxable item at sale: a timing choice, not a saving."], "status": "Verified", "sources": ["irs_rental", "irs_basis"]},
        {"cells": ["Recapture at sale", "Unrecaptured section 1250 gain — the portion of gain attributable to depreciation on real property — is taxed at a maximum federal rate of 25 percent, separate from the rate on other long-term gain.", "Model the recapture before assuming a rented path out-earns an early sale."], "status": "Verified", "sources": ["irs_409"]},
        {"cells": ["What death does to prior depreciation", "Basis for inherited property is generally the fair market value at the date of death, so the heir starts from a fresh basis rather than from the decedent's depreciated one.", "The decedent's accumulated depreciation does not follow the house; only the heir's own does."], "status": "Verified", "sources": ["irs_basis"]},
        {"cells": ["The California layer on the recapture", "California has no lower rate for capital gains and taxes all capital gains as ordinary income.", "Do not import a federal rate schedule into the state figure: at the modeled top rates the state adds 13.3% on the same gain."], "status": "Verified", "sources": ["ftb_cg", "rtc_17043"]},
        {"cells": ["Personal-use allocation", "Renting part of a property, or using part of it personally, requires income and expenses to be separated between uses.", "An occupancy plan needs an explicit allocation rule in the model before any rent is counted."], "status": "Verified", "sources": ["irs_rental"]},
        {"cells": ["Work that does not trigger reassessment", "The Santa Clara Assessor states that ordinary maintenance is generally not assessable, and that specific exclusions exist — including for seismic retrofit and certain disaster repairs — each requiring the applicable filing.", "Confirm the exclusion in writing with the assessor before assuming a repair is tax-neutral; a surprise addition to assessed value is permanent."], "status": "Verified", "sources": ["scc_assessor_2026"]},
        {"cells": ["Who does the work", "A contractor must be licensed for the trade, and the state board's licence check is the only public verification of that; nothing in it prices the job.", "License-check and bid every vendor in the plan, and keep the bids with the reserve reconciliation."], "status": "Verified", "sources": ["cslb"]},
    ]
    body += make_table("Depreciation, recapture and the repair/improvement line", ["Issue", "Official rule", "How to apply it"], tax_rows,
                       "Three systems must not be mixed: the depreciation schedule drives income tax, the assessor's base year value drives property tax, and the estate appraisal drives basis. Each has its own source and its own clock.")

    rerun_rows = [
        {"cells": ["Re-run the year-by-year model", "Once a year, on a fixed date", "Rebuild value, assessed value, tax, insurance, utilities and rent from the current documents; keep the prior year's output for comparison.", "A model that is not re-run silently converts an assumption into a fact."], "status": "Guidance", "sources": ["boe_pub29", "irs_estate"]},
        {"cells": ["Re-read the tax bill, not the estimate", "When each new secured bill arrives", "Check the rate-area line, the total levy, the exemptions taken and every non-base charge against the model's tax line.", "The published levy example is not the parcel's levy; the bill is."], "status": "Guidance", "sources": ["scc_tax_rates", "scc_assessor_2026"]},
        {"cells": ["Check the assessment against the appeal window", "Annually, inside the window", "San Francisco's informal review runs January 2 to March 31 for one-to-four-unit properties and an Assessment Appeals Board filing is due July 2 to September 15; Santa Clara supplemental appeals are due 60 days from the notice.", "A decline in value is only recovered if it is claimed; the window does not reopen."], "status": "Verified", "sources": ["sf_asr_page", "scc_assessor_2026"]},
        {"cells": ["Re-price insurance", "At every renewal, and again before any change of use", "Obtain owner-occupied and landlord quotes separately; record the coverage form and the wildfire exposure treatment.", "Non-renewal is a market event in California, not a household failure — and it arrives without warning."], "status": "Guidance", "sources": ["cdi", "cdi_sis"]},
        {"cells": ["Refresh the capital plan", "Annually, with the reconciliation", "Compare actual spend with the reserve, re-set the bands and move items between years only with a written reason.", "The plan earns its keep only when variance is reviewed."], "status": "Guidance", "sources": ["cslb", "irs_rental"]},
        {"cells": ["Re-check the law that changed", "Quarterly, against the watchlist", "Separate enacted changes from proposals, and record the effective date, not the headline, for each.", "A proposed rate change modeled as law distorts every downstream number."], "status": "Guidance", "sources": ["irs_2027", "ca_legislation", "boe_prop19"]},
    ]
    body += make_table("Annual re-run protocol — the plan is a living document", ["Action", "Cadence", "What to do", "Why it fails if skipped"], rerun_rows,
                       "This is the operating discipline the owner asked for: the model is only as good as the date it was last fed. Nothing here requires new data collection beyond the documents that already arrive each year.")
    body += cards("Related pages", [
        ("Property-tax rules", "How the assessed base, the levy and the exemptions build the tax line.", "pages/property-tax.html"),
        ("Costs and coverage", "Insurance, utilities and rent evidence still missing for both buildings.", "pages/operating-costs.html"),
        ("Sale timing and the tax year", "What holding costs at sale, and what an early sale avoids.", "pages/sale-timing.html"),
        ("Compare paths", "Carrying costs and reserves folded into each path's cash flow.", "pages/decision-analysis.html"),
    ], current="pages/capital-plan.html")
    return render_page("pages/capital-plan.html", "Five-year maintenance and capital plan",
                       "A dated, item-by-item plan for both buildings, the reserve lines that fund them, the depreciation and recapture rules that decide what a holding path earns, and the annual re-run protocol.",
                       body, "NUMBERS")


def build_investment_policy() -> str:
    body = callout(
        "Write it before the money arrives",
        "An investment policy written after proceeds land is a document drafted under pressure: the market is moving, the house may still be unsold, and the temptation is to decide by headline. Written in advance, the same policy "
        "settles the routine questions once — allocation, staging, rebalancing, cash reserve, tax handling and what would justify a change — and leaves only the genuinely unexpected to the review clause. Sign it, date it, and record "
        "in the decision log which version applied on which date.",
        "info",
    )
    policy_rows = [
        {"cells": ["1. Purpose and scope", "One paragraph naming the proceeds the policy governs, who may act, and which accounts are in scope. Exclude anything the trust or estate has not yet distributed.", "A policy with no account list is not a policy"], "sources": ["irs_1041"]},
        {"cells": ["2. Horizon and liquidity needs", "State the planned use of the money and the years until it is needed, plus the reserve held for property taxes, insurance, repairs and vacancies.", "A reserve that is not named gets invested anyway"], "sources": ["irs_rental"]},
        {"cells": ["3. Staging rule", "Park proceeds in the short-bill to two-year-note range and buy the equity allocation on a written schedule — the number of purchases and their dates decided in advance, not later.", "Lump-sum and dollar-cost-averaging both fail when the choice is made mid-move"], "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["4. Renewal rule", "State what happens at each maturing rung: renew at the short end, extend duration, or accelerate the scheduled purchases if yields are higher and the schedule is behind.", "Reinvestment risk is the cost of a ladder and is invisible until it is decided at the counter"], "sources": ["treasury_bills", "cbo_rates"]},
        {"cells": ["5. Allocation bands", "Target weights with rebalance bands, so the policy decides the trade and not the news cycle.", "No bands means every month looks like a month to act"], "sources": ["sec_stocks"]},
        {"cells": ["6. Tax handling", "Prefer holding periods that qualify for long-term treatment, decide in advance how losses are used, and record that state gain is taxed as ordinary income rather than at the federal rate schedule.", "A federal-only analysis overstates the after-tax return of every taxable sale"], "sources": ["ftb_cg", "irs_1041sd"]},
        {"cells": ["7. Prohibited actions", "No leverage, no single-position concentration beyond a stated limit, no illiquid commitments while the property decision is open, and no amendment outside the annual review except the written triggers.", "An exception granted under pressure becomes the new default"], "sources": ["sec_stocks"]},
        {"cells": ["8. Review cadence", "One scheduled annual review plus event-driven review when a listed trigger fires, each recorded as a dated entry.", "A review that is not written down leaves no evidence the policy was followed"], "sources": ["cbo_outlook"]},
        {"cells": ["9. Reversal conditions", "The specific, observable facts that change the plan: a materially different net yield on the staging band, a law change affecting the estate or the property tax, an insurance non-renewal or repair shock, or a failed Proposition 19 claim.", "A plan nothing could change is a wish, not a policy"], "sources": ["boe_prop19", "irs_estate", "cdi"]},
        {"cells": ["10. Advice and authority", "Name the adviser and their standard of care, the fee basis, who is authorised to instruct, and state that the policy is reviewed with a tax adviser before implementation.", "Execution that runs ahead of documented advice is unverifiable afterwards"], "sources": ["sec_stocks"]},
    ]
    body += make_table("The ten sections to write, in order", ["Section", "What it must say", "Failure mode it prevents"],
                       [{"cells": r["cells"], "status": "Guidance", "sources": r["sources"]} for r in policy_rows],
                       "A policy is a set of decisions made in advance. Each row is written as a rule the owner could follow without further judgment in the moment, which is the entire point.")

    yield_rows = [
        {"cells": ["Staging band, first rung", "3-month bill", "About 4.3 percent (November 2026 par yield curve, cross-checked against market quotes of the same series)", "The rate is fixed at auction; the next auction's rate is unknown"],
         "status": "Cross-checked", "sources": ["treasury_curve", "treasury_bills"]},
        {"cells": ["Staging band, last rung", "2-year note", "About 4.9 percent (same curve)", "Held to maturity, or sold earlier at whatever price then applies"],
         "status": "Cross-checked", "sources": ["treasury_curve", "treasury_notes"]},
        {"cells": ["Ten-year anchor in the near-term outlook", "10-year note", "4.3 percent average across the CBO 2026-2036 baseline, with 4.8 and 5.8 percent higher-rate paths", "A macro baseline to 2036, not a promise and not a 50-year path"],
         "status": "Verified", "sources": ["cbo_rates"]},
        {"cells": ["State and local tax on the reserve", "Interest income", "TreasuryDirect states that interest is exempt from state and local income taxes and taxable federally", "Improves the after-tax yield of the staging sleeve relative to other cash holdings"],
         "status": "Verified", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Equity side of the choice", "Scheduled purchases", "The SEC states that stock prices fall as well as rise and that investors can lose money; no official expected return is asserted anywhere on this site", "Staging changes when exposure begins; it does not remove the exposure"],
         "status": "Verified", "sources": ["sec_stocks"]},
        {"cells": ["Severity anchors for a crash during staging", "Historical drawdowns", "The 1929 Dow decline of about 89 percent peak to trough, with the prior high not regained until November 1954; the 2007-09 S&P 500 decline of about 57 percent", "Two severity anchors, not probabilities"],
         "status": "Historical", "sources": ["fed_1929", "fed_2008"]},
        {"cells": ["Inflation erosion of a long wait", "CPI path", "CBO's near-term outlook runs to 2036 and its long-term projection to 2055; neither reaches the household's horizon with any authority over it", "A policy that stages for years must say what it assumes about purchasing power"],
         "status": "Verified", "sources": ["cbo_outlook", "cbo_ltbo"]},
    ]
    body += make_table("The yield and risk facts the policy has to state honestly", ["Element", "Instrument or rule", "Official figure or statement", "Caveat"],
        [{"cells": r["cells"], "status": r["status"], "sources": r["sources"]} for r in yield_rows],
        "Re-read the current auction results and the current curve at the moment of implementation: anything older than a few days in this table is context, not an input.")

    band_rows = [
        {"cells": ["Cash and reserve", "Hold the next twelve months of carrying costs in cash, then stage the remainder; the reserve is not investable", "Any month in which the reserve cannot be met from cash without selling a rung early", "The carrying-cost bands on the capital plan page are the reserve's size"], "status": "Projection", "sources": ["irs_rental", "cdi"]},
        {"cells": ["Staged Treasury rungs", "Equal scheduled purchases over 24 to 36 months, laddered so a rung matures each month", "Yields rise enough that the waiting cash is a decided cost, or the property decision changes the amount being staged", "Reinvestment risk sits beside the headline yield and must be shown in the same table"], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Equity sleeve", "Diversified, low-turnover, held in taxable accounts where the long-term holding period matters", "Drift beyond the stated band, or a change in the horizon that the policy names", "No expected return is assumed anywhere in this document"], "status": "Guidance", "sources": ["sec_stocks"]},
        {"cells": ["Real property held directly", "Treated as its own concentrated asset class with tax, leverage and insurance consequences of its own", "Insurance non-renewal, a repair shock, or a rent or occupancy rule change", "Depreciation and recapture are modeled, not assumed away"], "status": "Guidance", "sources": ["irs_rental", "cdi", "irs_409"]},
        {"cells": ["Anything illiquid", "No commitments while the property decision is open", "A request to sign before the transfer facts are known", "The estate's own liquidity needs outrank any return story"], "status": "Guidance", "sources": ["irs_estate", "irs_estate_faq"]},
    ]
    body += make_table("Rebalance bands and review triggers", ["Sleeve", "Default rule", "What triggers a change", "What stays true either way"], band_rows,
                       "Write the trigger, the date and the decision into the decision log whenever a band is breached, so a later reader can see that the policy was followed rather than invented after the fact.")

    liquidity_rows = [
        {"cells": ["Estate liquidity need", "A Form 706 filing is tested on the gross estate plus adjusted taxable gifts, and the estate must be able to pay tax without a forced sale of real property; the IRS notes the nine-month due date and the extension available on request.", "Estates whose assets are mostly one house solve this with life insurance, an existing cash reserve or a partial sale; the point of the policy is to decide which before the death."], "status": "Verified", "sources": ["irs_estate_faq", "irs_estate"]},
        {"cells": ["Where the cash sits", "The owner reports the estate holds considerable cash in addition to both houses. Whether that is inside or outside the trust changes the liquidity analysis, the basis analysis and the gross-estate computation.", "Ask the trustee's counsel, in writing, which assets are inside the trust and which pass outside it."], "status": "Owner-supplied (privacy-rounded)", "sources": ["owner_a", "irs_estate"]},
        {"cells": ["Portability", "An estate may elect to transfer any unused federal exclusion to a surviving spouse, and the IRS notes the election may require filing Form 706 even where no return would otherwise be required.", "Ask now whether a prior election was made, and on which return; portability is not automatic."], "status": "Verified", "sources": ["irs_estate_faq"]},
        {"cells": ["Prior taxable gifts", "The filing test adds adjusted taxable gifts to the gross estate and reduces the exclusion by the specific gift-tax exemption used; Schedule K of Form 706 reports the gifts.", "Ask for every lifetime gift over the annual exclusion, in writing, before modeling the estate's headroom."], "status": "Verified", "sources": ["irs_estate_faq", "irs_706"]},
        {"cells": ["What the policy must not assume", "Nothing published here forecasts the exclusion in a future year: the current figures are the 2026 and 2027 amounts, and the 2026 proposals to change the exclusion are not law.", "Write the policy to the law in force at implementation, and re-check it then — the policy is not a tax position."], "status": "Verified", "sources": ["irs_2027", "irs_estate"]},
    ]
    body += make_table("Liquidity clauses the policy has to contain while the estate is still open", ["Clause", "What the official source establishes", "What to write in the policy"], liquidity_rows,
                       "An investment policy for inheritance proceeds is really two policies: how the estate pays what it owes, and what the heir does with what is left. They are written in that order.")
    body += paragraph("Agreeing the answer before the figures arrive", "The owner's own discipline — agreeing in writing what would make the household choose each path before the projections are produced — is the difference between a decision and a rationalisation. Put the reversal conditions on the first screen, the signed policy here, and the dated record in the decision log. If the figures later argue for a different path, the written conditions show whether the answer moved because the facts moved or because the wish moved.")
    return render_page("pages/investment-policy.html", "Investment policy for the proceeds",
                       "A written policy prepared before any money arrives: staging and renewal rules, rebalance bands, tax handling, prohibited actions, the liquidity clauses that cover the estate itself, and the conditions that would change the plan.",
                       body, "SELL PATH")


def build_page(path: str) -> str:
    builders = {
        "index.html": build_index,
        "pages/executive-summary.html": build_executive_summary,
        "pages/decision-analysis.html": build_decisions,
        "pages/property-profiles.html": build_property_profiles,
        "pages/questions.html": build_questions,
        "pages/requirements-tracker.html": build_requirements_tracker,
        "pages/projections.html": build_projections,
        "pages/property-tax.html": build_property_tax,
        "pages/capital-plan.html": build_capital_plan,
        "pages/sale-timing.html": build_sale_timing,
        "pages/investment-policy.html": build_investment_policy,
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
