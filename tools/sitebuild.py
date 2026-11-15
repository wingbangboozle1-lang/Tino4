#!/usr/bin/env python3
"""Build a privacy-safe, source-linked inheritance decision workspace.

The public build embeds only anonymized, $10-rounded household figures and
published statutory amounts. It never reads private files. Every substantive
table row carries an evidence status and at least one official source link.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKED = "2026-11-15"
SITE_TITLE = "Private inheritance decision workspace"

# Links were fetched directly on CHECKED unless noted. A source may establish
# a legal rule, a published figure, or a public historical observation — never
# a private property's exact value, bill, lease, premium, or title.
SOURCES = {
    "irs_estate": {
        "label": "IRS — Estate tax",
        "url": "https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax",
        "scope": "Defines the gross estate and the year-of-death Form 706 filing-threshold table (2026: $15,000,000). The threshold is an estate-level test, not an amount per beneficiary.",
        "verified": True,
    },
    "irs_estate_faq": {
        "label": "IRS — Estate-tax filing FAQs",
        "url": "https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-estate-taxes",
        "scope": "Filing test (gross estate plus adjusted taxable gifts and specific gift-tax exemption), 9-month Form 706 due date, up-to-6-month extension via Form 4768, portability election rules and the Rev. Proc. 2022-32 simplified portability method. Also confirms Public Law 119-21 raised the 2026 basic exclusion to $15,000,000.",
        "verified": True,
    },
    "irs_rp2532": {
        "label": "IRS — Rev. Proc. 2025-32 (2026 inflation adjustments)",
        "url": "https://www.irs.gov/pub/irs-drop/rp-25-32.pdf",
        "scope": "Official 2026 amounts: OBBBA §70106 sets the basic exclusion at $15,000,000 for 2026 with inflation adjustment for 2027 and later; estates and trusts keep four rates (10/24/35/37%) with the top bracket beginning over $16,000; 20% capital-gains rate for trusts begins over $16,250. Does not forecast later-year law.",
        "verified": True,
    },
    "irs_2027": {
        "label": "IRS IR-2026-133 — 2027 estate and gift adjustments",
        "url": "https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2027-taxpayers-continue-to-benefit-from-the-working-families-tax-cuts",
        "scope": "States the 2027 basic estate-tax exclusion ($15,480,000) and annual gift exclusion ($20,000), and compares with 2026 ($19,000). Not a forecast of future law.",
        "verified": True,
    },
    "irs_basis": {
        "label": "IRS — Gifts and inheritances FAQ",
        "url": "https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances",
        "scope": "Inherited-property basis is generally date-of-death fair market value, subject to exceptions and consistent-basis rules; gain can arise on a later sale. It does not establish a property's value or basis.",
        "verified": True,
    },
    "irs_topic701": {
        "label": "IRS Topic no. 701 — Sale of your home",
        "url": "https://www.irs.gov/taxtopics/tc701",
        "scope": "Section 121 exclusion of up to $250,000 ($500,000 on a joint return) of gain on a principal residence, with 2-of-5-year ownership and use tests and a once-per-2-years limit. Publication 523 has the full rules.",
        "verified": True,
    },
    "irs_1041": {
        "label": "IRS — About Form 1041",
        "url": "https://www.irs.gov/forms-pubs/about-form-1041",
        "scope": "Form 1041 reporting by fiduciaries for estate or trust income, deductions, gains, losses and distributions. Whether a specific trust must file is not determined here.",
        "verified": True,
    },
    "irs_rental": {
        "label": "IRS Publication 527 — Residential Rental Property",
        "url": "https://www.irs.gov/publications/p527",
        "scope": "Rental income, expenses, personal use, repairs, improvements, vacancy and depreciation (27.5-year residential rental schedule). Not a rent amount or repair budget for a private property.",
        "verified": True,
    },
    "ca_death_tax": {
        "label": "California State Controller — Estate tax",
        "url": "https://www.sco.ca.gov/ardtax_estate_tax.html",
        "scope": "California Estate Tax returns are not required for deaths on or after January 1, 2005. Not a forecast of future law.",
        "verified": True,
    },
    "ca_rtc13301": {
        "label": "California Revenue and Taxation Code §13301",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=13301.&lawCode=RTC",
        "scope": "Bars the state and its political subdivisions from imposing a gift, inheritance, succession, legacy, income, or estate tax on a transfer by reason of death. Future legislatures can change law.",
        "verified": True,
    },
    "boe_prop19": {
        "label": "California BOE — Proposition 19",
        "url": "https://www.boe.ca.gov/prop19/",
        "scope": "Comparison charts: the parent-child exclusion needs the principal residence of transferor AND transferee, a value limit of the current taxable value plus $1,000,000 (biennially adjusted), homeowners' exemption within 1 year of transfer, and the exclusion claim within 3 years or before a third-party transfer. Grandparent-grandchild transfers also need the statutory deceased-parent condition. Cannot establish eligibility without deed, relationship, occupancy and claim facts.",
        "verified": True,
    },
    "boe_lta25009": {
        "label": "California BOE Letter to Assessors 2025/009",
        "url": "https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf",
        "scope": "Official adjustments of the Proposition 19 $1,000,000 amount: $1,000,000 (transfers 2/16/2021–2/15/2023), $1,022,600 (2/16/2023–2/15/2025), $1,044,586 (2/16/2025–2/15/2027), adjusted every other February by the FHFA House Price Index for California (2024 change: 2.15%). Next adjustment February 2027. Application detail: Property Tax Rule 462.520 and LTA 2022/012.",
        "verified": True,
    },
    "ca_rtc63": {
        "label": "California Revenue and Taxation Code §63.2",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=63.2.&lawCode=RTC",
        "scope": "Statutory family-home/family-farm exclusion conditions: qualifying relationship, transferor and transferee principal-residence requirements, one-year homeowners' exemption filing and the value-limit formula. Grandchild transfers need the statutory deceased-parent condition.",
        "verified": True,
    },
    "ca_rtc480": {
        "label": "California Revenue and Taxation Code §480",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=480.&lawCode=RTC",
        "scope": "Change-in-ownership statement for real property transferred by reason of death, including through a trust, within 150 days after death in the specified nonprobate cases.",
        "verified": True,
    },
    "ca_prob160617": {
        "label": "California Probate Code §16061.7",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=16061.7.&lawCode=PROB",
        "scope": "Trustee notice in specified events, including when a revocable trust becomes irrevocable because of death; the statutory notice deadline is generally 60 days. Applicability depends on trust facts.",
        "verified": True,
    },
    "boe_pub29": {
        "label": "California BOE Publication 29 — California Property Tax",
        "url": "https://www.boe.ca.gov/proptaxes/pdf/pub29.pdf",
        "scope": "Proposition 13 overview: 1% general levy plus voter-approved bonded indebtedness, general 2% limit on annual assessed-value growth, reassessment rules. Not a parcel-specific tax rate.",
        "verified": True,
    },
    "ca_rent": {
        "label": "California Civil Code §1947.12",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1947.12.&lawCode=CIV",
        "scope": "Statewide rent-cap text and exemptions. Coverage, local ordinances, permitted use and tenant protections require property- and jurisdiction-specific review.",
        "verified": True,
    },
    "cdi": {
        "label": "California Department of Insurance — Residential insurance",
        "url": "https://www.insurance.ca.gov/01-consumers/105-type/5-residential/index.cfm",
        "scope": "Residential-insurance shopping tools and the limited perils covered by the FAIR Plan and the possible role of a Difference in Conditions policy. No individual premium is stated.",
        "verified": True,
    },
    "cdi_sis": {
        "label": "California Department of Insurance — Sustainable Insurance Strategy",
        "url": "https://www.insurance.ca.gov/01-consumers/180-climate-change/upload/Sustainable-Insurance-Strategy-CDI-Summary-10-14-25.pdf",
        "scope": "CDI's summary of the market-rebuild program: approved wildfire catastrophe models, insurer commitments to write a minimum share of business in distressed areas, FAIR Plan modernization and depopulation goals, rate-review streamlining. Confirms the market is under active regulatory change; states no household premium.",
        "verified": True,
    },
    "cpuc_solar": {
        "label": "California Public Utilities Commission — Net metering and net billing",
        "url": "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/customer-generation/net-energy-metering-and-net-billing",
        "scope": "NEM/NBT tariff differences; under net billing, export credits are usually below retail rates. Eligibility, tariff, interconnection date and a household bill determine actual credits.",
        "verified": True,
    },
    "water_board": {
        "label": "California State Water Resources Control Board — Drinking Water Program",
        "url": "https://www.waterboards.ca.gov/drinking_water/programs/",
        "scope": "State oversight of public water systems. It does not publish an individual service address's water bill or tariff; the provider bill is required.",
        "verified": True,
    },
    "sfpuc_rates": {
        "label": "SFPUC — Proposition 218 water and sewer rate notice (2026)",
        "url": "https://www.sfpuc.gov/accounts-services/water-power-sewer-rates/proposed-water-sewer-rates-2026/proposition-218-notice",
        "scope": "Published rate schedule effective July 1, 2026: average San Francisco single-family combined water/sewer bill about $171 per month (FYE 2026) rising to about $189 (FYE 2027) and $212 (FYE 2028); two-tier volumetric water rates; multi-family tier 1 covers the first 3 units per dwelling per month. A utility's own rate notice, not a specific account's bill.",
        "verified": True,
    },
    "hud_fmr": {
        "label": "HUD — Fair Market Rents",
        "url": "https://www.huduser.gov/portal/datasets/fmr.html",
        "scope": "Annual FMR estimates (FY2027 effective October 1, 2026) used for specified housing programs. FMR is a 40th-percentile gross-rent benchmark, not a property appraisal, lawful rent determination or current lease amount. Area-level figures must be read from HUD's FMR data system for the specific county/area.",
        "verified": True,
    },
    "cslb": {
        "label": "California Contractors State License Board — Check a license",
        "url": "https://www.cslb.ca.gov/OnlineServices/CheckLicenseII/CheckLicense.aspx",
        "scope": "Contractor license and complaint disclosure checking. It does not set or verify a repair estimate.",
        "verified": True,
    },
    "treasury_bills": {
        "label": "TreasuryDirect — Treasury bills",
        "url": "https://treasurydirect.gov/marketable-securities/treasury-bills/",
        "scope": "Bills run 4 to 52 weeks, rates fixed at auction, may be held to maturity or sold earlier; interest is federally taxable and exempt from state and local taxes.",
        "verified": True,
    },
    "treasury_notes": {
        "label": "TreasuryDirect — Treasury notes",
        "url": "https://www.treasurydirect.gov/marketable-securities/treasury-notes/",
        "scope": "Notes include a 2-year maturity, pay a fixed auction rate, may be held to maturity or sold earlier; interest is federally taxable and exempt from state and local taxes.",
        "verified": True,
    },
    "fed_1929": {
        "label": "Federal Reserve History — Stock Market Crash of 1929",
        "url": "https://www.federalreservehistory.org/essays/stock-market-crash-of-1929",
        "scope": "Reports the Dow's 89% peak-to-trough decline and that its pre-crash high was not regained until November 1954. A price-index history, not a diversified portfolio total return.",
        "verified": True,
    },
    "fed_2008": {
        "label": "Federal Reserve History — The Great Recession",
        "url": "https://www.federalreservehistory.org/essays/great-recession-of-200709",
        "scope": "Reports a 57% S&P 500 peak-to-trough decline and an approximately 30% average U.S. home-price decline in that episode. Neither is a local property forecast nor a total-return estimate.",
        "verified": True,
    },
    "bls_cpi": {
        "label": "U.S. Bureau of Labor Statistics — CPI, June 2022",
        "url": "https://www.bls.gov/opub/ted/2022/consumer-prices-up-9-1-percent-over-the-year-ended-june-2022-largest-increase-in-40-years.htm",
        "scope": "Reports a 9.1% twelve-month CPI increase through June 2022, the largest since November 1981. A historical observation, not a long-run inflation assumption.",
        "verified": True,
    },
    "fred_cpi": {
        "label": "FRED (Federal Reserve Bank of St. Louis) — CPI-U, annual averages 1929–2025",
        "url": "https://fred.stlouisfed.org/series/CPIAUCNS",
        "scope": "Official BLS CPI-U (NSA) series. Decade inflation rates and cumulative changes shown on this site are computed from the published annual averages, not estimated.",
        "verified": True,
    },
    "cbo_rates": {
        "label": "Congressional Budget Office — Interest-rate scenarios, 2026–2036",
        "url": "https://www.cbo.gov/publication/62809",
        "scope": "CBO reports a 4.3% average 10-year Treasury rate in its 2026–2036 forecast and 4.8%/5.8% higher-rate scenarios. Not a 50-year forecast, house-price forecast or household investment return.",
        "verified": True,
    },
    "cbo_ltbo": {
        "label": "Congressional Budget Office — The Long-Term Budget Outlook: 2025 to 2055",
        "url": "https://www.cbo.gov/publication/61270",
        "scope": "Real GDP growth averages 1.6% per year over 2025–2055 in CBO's projections (1.8% first decade, slowing to 1.4% third decade); inflation slows to the Federal Reserve's 2% long-term goal by 2027; 10-year Treasury rates stay near their past-30-year average. Current-law projections, not a household forecast.",
        "verified": True,
    },
    "fhfa_hpi": {
        "label": "Federal Housing Finance Agency — HPI summary tables",
        "url": "https://www.fhfa.gov/data/hpi/summary-tables",
        "scope": "Broad state and metropolitan house-price indexes; also the index used to biennially adjust the Proposition 19 $1,000,000 amount. Not a valuation or forecast for an individual property.",
        "verified": True,
    },
    "sec_stocks": {
        "label": "SEC Investor.gov — Stocks FAQs",
        "url": "https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks",
        "scope": "Explains stock risks, potential loss and diversification; prescribes no return assumption or allocation.",
        "verified": True,
    },
    "hcd_sb79": {
        "label": "California HCD — SB 79 Transit-Oriented Development",
        "url": "https://www.hcd.ca.gov/planning-and-research/sb79-tod",
        "scope": "Official program page: SB 79 (signed October 10, 2025) makes qualifying transit-oriented housing developments an allowed use near specified transit stops in urban transit counties, effective July 1, 2026 (Gov. Code §65912.155 et seq.); local jurisdictions process qualifying projects from that date.",
        "verified": True,
    },
    "sos_initiatives": {
        "label": "California Secretary of State — Initiative status (failure memo, May 2026)",
        "url": "https://elections.cdn.sos.ca.gov/ccrov/2026/may/26138jh.pdf",
        "scope": "Official CC/ROV Memorandum #26138 (May 18, 2026): the initiative titled 'Repeals voter-enacted changes to property tax rules for transfers between family members' (Prop 19 repeal) failed — signatures filed were below the number required. Current Proposition 19 rules were not changed by this attempt.",
        "verified": True,
    },
    "sos_ballot": {
        "label": "California Secretary of State — Ballot measure status",
        "url": "https://www.sos.ca.gov/elections/ballot-measures/initiative-and-referendum-status",
        "scope": "Official initiative and referendum status pages, including measures that failed to qualify or were withdrawn. Use to confirm any future repeal attempt's status rather than campaign claims.",
        "verified": True,
    },
    "leginfo_sca4": {
        "label": "California Legislative Information — SCA-4 (2025–2026) status",
        "url": "https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202520260SCA4",
        "scope": "Official status page: SCA-4 (Archuleta) is a property-tax measure for a veterans' exemption — not a restoration of parent-child transfer exclusions. Amended in Senate 04/08/26; held in Senate Appropriations 05/14/26. Included because third-party commentary misdescribed this bill.",
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
        "scope": "Official search interface for California bills and their status. A bill or proposal is not current law unless chaptered and effective.",
        "verified": True,
    },
    "github_history": {
        "label": "GitHub Docs — Removing sensitive data from a repository",
        "url": "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository",
        "scope": "Coordination and side effects of history rewrites; PRs, forks, caches and clones can retain data. GitHub Support or repository-owner action may be needed.",
        "verified": True,
    },
    "congress_s4196_status": {
        "label": "Congress.gov — S. 4196 status",
        "url": "https://www.congress.gov/bill/119th-congress/senate-bill/4196",
        "scope": "Congress.gov lists S. 4196 as introduced March 25, 2026 and referred to Senate Finance; no enactment is shown as of the check date. Status can change.",
        "verified": True,
    },
    "congress_s4196_text": {
        "label": "Congress.gov — S. 4196 introduced text",
        "url": "https://www.congress.gov/bill/119th-congress/senate-bill/4196/text",
        "scope": "Introduced text proposes a $3,500,000 basic exclusion amount and changes to federal estate, gift and generation-skipping transfer tax rules, with a proposed effective date for deaths and gifts after December 31, 2026. This is not enacted law.",
        "verified": True,
    },
    "congress_hr601_text": {
        "label": "Congress.gov — H.R. 601 introduced text",
        "url": "https://www.congress.gov/bill/119th-congress/house-bill/601/text/ih",
        "scope": "Introduced text proposes a 20% rate for estate, gift and generation-skipping transfer taxes and states a proposed effective date for transfers after December 31, 2024. This is not enacted law.",
        "verified": True,
    },
    "congress_s587_status": {
        "label": "Congress.gov — S. 587 status",
        "url": "https://www.congress.gov/bill/119th-congress/senate-bill/587",
        "scope": "As checked 2026-11-15, Congress.gov lists S. 587 as introduced February 13, 2025 and referred to Senate Finance; no enactment is shown. Status can change.",
        "verified": True,
    },
    "congress_s587_text": {
        "label": "Congress.gov — S. 587 introduced text",
        "url": "https://www.congress.gov/bill/119th-congress/senate-bill/587/text/is",
        "scope": "Introduced text proposes to repeal federal estate and generation-skipping transfer taxes and separately changes gift-tax rules. The proposal is not enacted law.",
        "verified": True,
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
    "ca_rtc218": {
        "label": "California Revenue and Taxation Code §218 — Homeowners' property tax exemption",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=218.&lawCode=RTC",
        "scope": "Sets the homeowners' property tax exemption at $7,000 of the dwelling's full value and excludes property that is rented, vacant, under construction on the lien date, or a vacation/secondary home. It does not establish an owner's eligibility.",
        "verified": True,
    },
    "ca_rtc51": {
        "label": "California Revenue and Taxation Code §51 — Base year value",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=51.&lawCode=RTC",
        "scope": "Defines real property's base year value for assessment purposes. It does not value a specific parcel.",
        "verified": True,
    },
    "ca_sb974_status": {
        "label": "California Legislature — SB 974 status, Chapter 665 (2026)",
        "url": "https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202520260SB974",
        "scope": "Status page records SB 974 as chaptered September 27, 2026, Chapter 665, Statutes of 2026, and marks it non-urgency. Verify its operative date and the assessor's implementation before applying it to a transfer.",
        "verified": True,
    },
    "ca_sb974_text": {
        "label": "California SB 974 — chaptered text",
        "url": "https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202520260SB974",
        "scope": "Chaptered amendment to RTC §63.2 expressly treats a special-needs trust established under Probate Code §3604 as an eligible medium for the stated intergenerational property-tax exclusion; eligibility and claim requirements remain. Separate claim-timing relief is limited to qualifying property connected with specified 2025 wildfires.",
        "verified": True,
    },
    "sos_qualified": {
        "label": "California Secretary of State — Qualified statewide ballot measures",
        "url": "https://www.sos.ca.gov/elections/ballot-measures/qualified-ballot-measures",
        "scope": "Read 2026-11-15. Lists the November 3, 2026 statewide measures by number and official ballot title, and notes ACA 13 was removed. The page is a list only: it does not state full measure text, fiscal effects or certified results. Those require the linked voter guide or certified results.",
        "verified": True,
    },
    "sf_rent_board": {
        "label": "San Francisco Rent Board — Department page",
        "url": "https://sf.gov/departments--rent-board",
        "scope": "Read 2026-11-15. States the 1.6% allowable annual increase for covered units from March 1, 2026 through February 28, 2027, and lists 2026 Rent Board news items. Item text and ordinance coverage must be read in the linked notice.",
        "verified": True,
    },
    "sf_treasurer_vacancy_404": {
        "label": "SF Treasurer — vacancy-tax URL retrieval failed",
        "url": "https://sftreasurer.org/empty-homes-tax",
        "scope": "Returned 'Page Not Found' on 2026-11-15. No SF vacancy-tax rule, rate or filing duty is based on this URL; the current official path is unconfirmed.",
        "verified": False,
    },
    "scc_assessor_fetch": {
        "label": "Santa Clara County Assessor homepage — fetch failed",
        "url": "https://assessor.santaclaracounty.gov/",
        "scope": "Fetch failed on 2026-11-15. The reachable Assessor page (asr.santaclaracounty.gov) lists contacts and online services only and has no tax-rate table. No Santa Clara property-tax rate is based on these pages.",
        "verified": False,
    },
    "boj_unverified": {
        "label": "Bank of Japan — official source not confirmed for bubble figures",
        "url": "https://www.boj.or.jp/en/",
        "scope": "The official Bank of Japan source for the historical discount-rate and asset-price figures was not retrieved. Secondary sources conflict, so no Japan bubble figure is published here.",
        "verified": False,
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
        "scope": "Direct retrieval returned a 404 on 2026-11-14. Proposition 19 summaries use the BOE Prop 19 page, LTA 2025/009 and current statute instead.",
        "verified": False,
    },
    "cpuc_water_404": {
        "label": "CPUC water-utilities URL — retrieval failed",
        "url": "https://www.cpuc.ca.gov/industries-and-topics/water/water-utilities",
        "scope": "Direct retrieval redirected to a 404 on 2026-11-14. No household water-rate figure is based on this URL.",
        "verified": False,
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
        ("pages/decision-log.html", "Decision log"),
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
        ("pages/estate-thresholds.html", "Estate tax & headroom"),
        ("pages/inheritance-process.html", "Step-by-step & deadlines"),
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
<meta name="description" content="Privacy-safe, source-linked decision framework. Figures are rounded to the nearest $10; no addresses, postal codes, names or parcel identifiers are published.">
<title>{esc(title)} · {esc(SITE_TITLE)}</title>
<link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/app.js" defer></script>
</head><body class="{esc(page_class)}"><a class="skip" href="#main">Skip to content</a>
<div class="layout">
<aside class="sidebar"><a class="brand" href="{prefix}index.html"><span class="brand-icon" aria-hidden="true">◈</span><span>PRIVATE<br>DECISION BRIEF</span></a>
<p class="sidebar-note">Trust transfer +<br>already-owned property</p>
<nav aria-label="Main navigation">{build_nav(path)}</nav>
<div class="sidebar-bottom">Figures rounded to $10<br>Sources checked {CHECKED}</div></aside>
<div class="workspace"><header class="topbar"><span>RESEARCH / DECISION SUPPORT</span><div><span class="privacy-dot" aria-hidden="true"></span> Privacy-first <button class="print-button no-print" id="print-page" type="button">Print</button></div></header>
<main id="main"><div class="page-heading"><span class="eyebrow">{esc(eyebrow)}</span><h1>{esc(title)}</h1><p class="lead">{esc(intro)}</p></div>{body}</main>
<footer><strong>Planning framework only.</strong> Not legal, tax, insurance, appraisal or investment advice. A source supports only its stated scope, not a private fact. Blank means unknown, not zero. Household figures are rounded to the nearest $10; statutory figures are shown as published. No addresses, postal codes, parcel identifiers or names appear on this site.<br>
<a href="{prefix}pages/privacy.html">Privacy &amp; limits</a> · <a href="{prefix}pages/sources.html">Official sources</a> · <a href="{prefix}pages/flagged-for-review.html">Flagged for review</a></footer>
</div></div></body></html>'''


def build_page(path: str) -> str:
    import sections
    builders = {
        "index.html": sections.build_index,
        "pages/executive-summary.html": sections.build_executive_summary,
        "pages/decision-analysis.html": sections.build_decisions,
        "pages/questions.html": sections.build_questions,
        "pages/projections.html": sections.build_projections,
        "pages/property-tax.html": sections.build_property_tax,
        "pages/operating-costs.html": sections.build_costs,
        "pages/black-swan.html": sections.build_black_swan,
        "pages/phased-investing.html": sections.build_phased_investing,
        "pages/estate-thresholds.html": sections.build_estate_thresholds,
        "pages/inheritance-process.html": sections.build_process,
        "pages/law-watchlist.html": sections.build_law_watchlist,
        "pages/attorney-cpa-brief.html": sections.build_brief,
        "pages/flagged-for-review.html": sections.build_flagged,
        "pages/glossary.html": sections.build_glossary,
        "pages/sources.html": sections.build_sources,
        "pages/privacy.html": sections.build_privacy,
        "pages/suggestions.html": sections.build_suggestions,
        "pages/decision-log.html": sections.build_decision_log,
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
    print(f"Built {len(EXPECTED_PAGES)} pages with $10-rounded figures and source-linked tables.")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    build()
