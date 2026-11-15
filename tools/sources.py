#!/usr/bin/env python3
"""Official source registry for the decision workspace.

Every entry was fetched and read directly on CHECKED (see below). The scope
statement is deliberately narrow: a source may establish a legal rule, a
statutory amount, a published rate, or a historical observation. No source
here establishes a private property's value, basis, lease, bill, premium,
title, occupancy, or tax position.

An entry with verified=False is a retrieval failure or a gateway page. Such an
entry must never be used to support a numeric claim; it exists only to give a
reader an official place to start.
"""
from __future__ import annotations

CHECKED = "2026-11-15"

SOURCES: dict[str, dict] = {
    # ---------------------------------------------------------------- federal
    "irs_estate": {
        "label": "IRS — Estate tax",
        "url": "https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax",
        "scope": (
            "Defines the gross estate and the Form 706 filing threshold by year of death. "
            "The 2026 filing threshold is $15,000,000. The test is gross estate plus adjusted "
            "taxable gifts and the specific gift tax exemption; it is not an amount per beneficiary."
        ),
        "verified": True,
    },
    "irs_2027": {
        "label": "IRS IR-2026-133 — 2027 inflation adjustments",
        "url": "https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2027-taxpayers-continue-to-benefit-from-the-working-families-tax-cuts",
        "scope": (
            "States a $15,480,000 basic exclusion amount for estates of decedents who die during "
            "2027, up from $15,000,000 for 2026, and a $20,000 annual gift exclusion for 2027, "
            "up from $19,000 for 2026. It is a published adjustment, not a forecast of later years."
        ),
        "verified": True,
    },
    "irs_706_due": {
        "label": "IRS — Filing estate and gift tax returns",
        "url": "https://www.irs.gov/businesses/small-businesses-self-employed/filing-estate-and-gift-tax-returns",
        "scope": (
            "States that the estate tax return is generally due nine months after the date of death, "
            "and that a six-month extension is available if requested before the due date and the "
            "estimated correct amount of tax is paid before the due date."
        ),
        "verified": True,
    },
    "irs_estate_faq": {
        "label": "IRS — Frequently asked questions on estate taxes",
        "url": "https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-estate-taxes",
        "scope": (
            "Explains the filing test, the portability election for a surviving spouse on a timely "
            "filed return, and the nine-month due date. Individual application depends on estate facts."
        ),
        "verified": True,
    },
    "irs_basis": {
        "label": "IRS — Gifts and inheritances FAQ",
        "url": "https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances",
        "scope": (
            "States that the basis of property inherited from a decedent is generally the fair market "
            "value on the date of death, or the alternate valuation date only if a Form 706 is filed "
            "and the alternate valuation is elected; gain is taxable on a later sale above basis. It "
            "also describes the consistent-basis reporting rule tied to Form 8971 Schedule A. It does "
            "not establish any property's value or basis."
        ),
        "verified": True,
    },
    "irs_pub523": {
        "label": "IRS — About Publication 523, Selling Your Home",
        "url": "https://www.irs.gov/forms-pubs/about-publication-523",
        "scope": (
            "Identifies Publication 523 as the IRS explanation of the tax rules that apply when a "
            "home is sold. The exclusion amount and the ownership and use tests must be read from the "
            "current publication; this build does not quote them."
        ),
        "verified": True,
    },
    "irs_pub527": {
        "label": "IRS — Publication 527, Residential Rental Property",
        "url": "https://www.irs.gov/publications/p527",
        "scope": (
            "Covers rental income, deductible rental expenses, personal use, repairs versus "
            "improvements, vacancy and depreciation. It provides no rent amount, expense budget or "
            "depreciation figure for any private property."
        ),
        "verified": True,
    },
    "irs_1041": {
        "label": "IRS — About Form 1041",
        "url": "https://www.irs.gov/forms-pubs/about-form-1041",
        "scope": (
            "Describes fiduciary reporting of estate or trust income, deductions, gains, losses and "
            "distributions. Whether a particular trust must file is not determined by this page."
        ),
        "verified": True,
    },
    "irs_topic503": {
        "label": "IRS — Topic no. 503, Deductible taxes",
        "url": "https://www.irs.gov/taxtopics/tc503",
        "scope": (
            "States that an individual's state and local tax deduction is limited to a combined "
            "$40,000 ($20,000 if married filing separately), subject to a modified adjusted gross "
            "income limitation but not reduced below $10,000. Real property taxes are deductible "
            "subject to that limit; transfer taxes and service charges for water, sewer or trash are "
            "listed as nondeductible."
        ),
        "verified": True,
    },
    "irs_home": {
        "label": "IRS — irs.gov entry point",
        "url": "https://www.irs.gov",
        "scope": (
            "Gateway only. No figure in this site is based on this URL where no specific IRS page was "
            "retrieved and read during this build."
        ),
        "verified": True,
    },
    # ------------------------------------------------------------- California
    "rtc_13301": {
        "label": "California Revenue and Taxation Code §13301",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=13301.&lawCode=RTC",
        "scope": (
            "Current statutory text bars the state and its political subdivisions from imposing any "
            "gift, inheritance, succession, legacy, income, or estate tax on a transfer occurring by "
            "reason of a death. Future legislatures and voters can change this."
        ),
        "verified": True,
    },
    "rtc_63_2": {
        "label": "California Revenue and Taxation Code §63.2",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=63.2.&lawCode=RTC",
        "scope": (
            "Current parent-child and grandparent-grandchild exclusion text: the transfer must be of "
            "the transferor's principal residence and must become the transferee's principal residence "
            "within one year; the transferee must file for the homeowners' or disabled veterans' "
            "exemption within one year; the new taxable value is the prior taxable value plus any "
            "excess of fair market value over that value plus the inflation-adjusted amount; the claim "
            "must be filed within three years or before transfer to a third party; if the transferee "
            "later stops qualifying, the base year value established at the change in ownership date, "
            "adjusted annually, is enrolled."
        ),
        "verified": True,
    },
    "rtc_480": {
        "label": "California Revenue and Taxation Code §480",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=480.&lawCode=RTC",
        "scope": (
            "Requires a signed change-in-ownership statement. For an interest in real property "
            "transferred by reason of death other than through probate, including a transfer through "
            "the medium of a trust, the statement must be filed within 150 days after the date of "
            "death. For other changes in ownership the period is 90 days."
        ),
        "verified": True,
    },
    "rtc_218": {
        "label": "California Revenue and Taxation Code §218",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=218.&lawCode=RTC",
        "scope": (
            "Sets the homeowners' property tax exemption at $7,000 of the full value of the dwelling, "
            "and states that the exemption does not extend to property that is rented, vacant, under "
            "construction on the lien date, or a vacation or secondary home."
        ),
        "verified": True,
    },
    "boe_prop19": {
        "label": "California BOE — Proposition 19",
        "url": "https://www.boe.ca.gov/prop19/",
        "scope": (
            "Summarizes current intergenerational transfer rules, the value limit of current taxable "
            "value plus the biennially adjusted amount, the one-year homeowners' exemption filing, "
            "the three-year claim period, and contrast with former Propositions 58 and 193. It cannot "
            "establish eligibility without the relationship, occupancy, deed and filing facts."
        ),
        "verified": True,
    },
    "boe_lta_2025_009": {
        "label": "BOE Letter To Assessors No. 2025/009",
        "url": "https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf",
        "scope": (
            "States that for transfers occurring February 16, 2025 through February 15, 2027 the "
            "adjusted amount is $1,044,586, that the amount is recalculated every other February 16 "
            "using the Federal Housing Finance Agency House Price Index for California, and that the "
            "next adjustment occurs in February 2027."
        ),
        "verified": True,
    },
    "boe_pub29": {
        "label": "BOE Publication 29 — California Property Tax: An Overview (March 2025)",
        "url": "https://www.boe.ca.gov/proptaxes/pdf/pub29.pdf",
        "scope": (
            "States that Proposition 13 limited the property tax rate to 1 percent plus the rate "
            "needed to fund voter-approved bonded indebtedness, that property is reassessed to current "
            "market value only on a change in ownership or new construction, and that annual base year "
            "value increases are generally limited to 2 percent. Also publishes the annual property tax "
            "calendar: January 1 lien date; February 15 exemption claim deadline; April 10 and December "
            "10 installment delinquency dates; July 2 to September 15 or November 30 assessment appeal "
            "filing window."
        ),
        "verified": True,
    },
    "boe_home": {
        "label": "California BOE — boe.ca.gov entry point",
        "url": "https://www.boe.ca.gov",
        "scope": (
            "Gateway only. No county tax-rate-area rate was retrieved for this build, so no composite "
            "rate is asserted for either property."
        ),
        "verified": True,
    },
    "prob_16061_7": {
        "label": "California Probate Code §16061.7",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=16061.7.&lawCode=PROB",
        "scope": (
            "Requires trustee notification when a revocable trust or any portion becomes irrevocable "
            "because of the death of a settlor, to be served not later than 60 days after the event, "
            "or 60 days after the trustee becomes aware of a person entitled to notice."
        ),
        "verified": True,
    },
    "civ_1947_12": {
        "label": "California Civil Code §1947.12",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1947.12.&lawCode=CIV",
        "scope": (
            "Current statewide rent cap: over any 12-month period an owner may not increase gross rent "
            "more than 5 percent plus the percentage change in the cost of living, or 10 percent, "
            "whichever is lower, of the lowest gross rent charged in the prior 12 months. A new "
            "tenancy in which no prior tenant remains may be set at any initial rate. The section lists "
            "exemptions, including housing issued a certificate of occupancy within the previous 15 "
            "years and separately alienable dwellings meeting stated conditions and notice rules."
        ),
        "verified": True,
    },
    "sf_gov_assess": {
        "label": "City and County of San Francisco — real property assessments",
        "url": "https://www.sf.gov/information--learn-about-real-property-assessments",
        "scope": (
            "States that the tax rate is 1 percent plus any voter-approved bond indebtedness and direct "
            "assessments, that reassessment generally occurs on change in ownership or new construction, "
            "and that annual assessment increases are limited to the lower of inflation or 2 percent. It "
            "does not state a composite rate for any parcel."
        ),
        "verified": True,
    },
    "sos_qualified": {
        "label": "California Secretary of State — Qualified statewide ballot measures",
        "url": "https://www.sos.ca.gov/elections/ballot-measures/qualified-ballot-measures",
        "scope": (
            "Lists the statewide measures qualified for the November 3, 2026 general election, "
            "including Proposition 43, Limits Voters' Ability to Raise Revenues for Local Government "
            "Services, a legislative constitutional amendment, and Proposition 42, which prohibits new "
            "state personal property taxes and certain retroactive state taxes."
        ),
        "verified": True,
    },
    "sos_results": {
        "label": "California Secretary of State — State ballot measure results",
        "url": "https://electionresults.sos.ca.gov/returns/ballot-measures",
        "scope": (
            "Publishes unofficial statewide results and states that county elections officials must "
            "report final official results by December 4, 2026 and that the Secretary of State will "
            "certify the results on December 11, 2026. Results reported on 2026-11-14 are unofficial "
            "and change during the canvass."
        ),
        "verified": True,
    },
    "ca_leg_search": {
        "label": "California Legislative Information — bill search",
        "url": "https://leginfo.legislature.ca.gov/faces/billSearchClient.xhtml",
        "scope": (
            "Official search interface for California bills and their status. A proposal is not law "
            "unless chaptered and effective; no pending bill is treated as law in this site."
        ),
        "verified": True,
    },
    "congress_search": {
        "label": "Congress.gov — advanced legislation search",
        "url": "https://www.congress.gov/advanced-search/legislation",
        "scope": (
            "Official search interface for federal bills and resolutions and their status. A proposal "
            "is not law unless enacted; no pending bill is treated as law in this site."
        ),
        "verified": True,
    },
    # ------------------------------------------------- utilities and coverage
    "sfpuc_rates": {
        "label": "SFPUC — Rate schedules for water and sewer service (effective July 1, 2026)",
        "url": "https://www.sfpuc.gov/sites/default/files/accounts-and-services/Rates_Schedule_Water_Sewer_2026-7.pdf",
        "scope": (
            "Publishes the adopted FY 2026-27 and FY 2027-28 meter service charges, volumetric water "
            "rates and wastewater and stormwater schedules for single-family and multi-family "
            "residential customers. It publishes rates, not any account's bill."
        ),
        "verified": True,
    },
    "sfpuc_prop218": {
        "label": "SFPUC — Proposition 218 notice, proposed water and sewer rates",
        "url": "https://www.sfpuc.gov/accounts-services/water-power-sewer-rates/proposed-water-sewer-rates-2026/proposition-218-notice",
        "scope": (
            "States current and proposed multi-family residential water tier rates and residential "
            "wastewater rates per unit, and describes the billing basis including the assumed share of "
            "water use returned to the sewer, 95 percent for multi-family residential."
        ),
        "verified": True,
    },
    "sjwc_tariff": {
        "label": "San Jose Water Company — CPUC tariff sheets effective July 1, 2026",
        "url": "https://www.sjwater.com/media/mu3pbdin/al629a-_web.pdf",
        "scope": (
            "Filed tariff sheets stating a general metered service quantity rate and stating that the "
            "served territory includes portions of Cupertino together with other named cities. Whether "
            "a particular parcel is served by this utility is not established here and must be read "
            "from the account or bill."
        ),
        "verified": True,
    },
    "cupertino_sanitary": {
        "label": "Cupertino Sanitary District",
        "url": "https://www.cupertinosanitarydistrict.org/",
        "scope": (
            "Identifies the district as the sewer service provider for customers in Cupertino and "
            "surrounding communities, and posts its public hearing notices for annual sewer service "
            "rate changes. It does not publish an individual account charge."
        ),
        "verified": True,
    },
    "cdi_residential": {
        "label": "California Department of Insurance — home/residential insurance",
        "url": "https://www.insurance.ca.gov/01-consumers/105-type/5-residential/index.cfm",
        "scope": (
            "Provides official residential insurance shopping tools, including a premium comparison "
            "tool, a coverage comparison tool and a company contact list, and explains that the FAIR "
            "Plan covers only fire or lightning, internal explosion and smoke, that extended coverage "
            "and vandalism may be added, and that a Differences in Conditions policy may be needed for "
            "perils such as theft and liability. It publishes no individual premium."
        ),
        "verified": True,
    },
    "cpuc_solar": {
        "label": "CPUC — net energy metering and net billing",
        "url": "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/customer-generation/net-energy-metering-and-net-billing",
        "scope": (
            "Explains the difference between net energy metering and net billing tariffs and that "
            "export credits under net billing are usually below retail rates. Eligibility, tariff, "
            "interconnection date and a household's own bill determine the actual credit."
        ),
        "verified": True,
    },
    "cslb": {
        "label": "Contractors State License Board — check a license",
        "url": "https://www.cslb.ca.gov/OnlineServices/CheckLicenseII/CheckLicense.aspx",
        "scope": (
            "Allows a reader to check a contractor licence and complaint disclosure. It does not set or "
            "verify any repair estimate."
        ),
        "verified": True,
    },
    # ---------------------------------------------------------------- markets
    "treasury_yield": {
        "label": "U.S. Treasury — Daily Treasury par yield curve rates",
        "url": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026",
        "scope": (
            "Publishes the official daily par yield curve, including the 3-month, 2-year and 10-year "
            "constant maturity rates. Rates change daily; the figures quoted in this site are labeled "
            "with the observation dates read directly from this page and are inputs a reader should "
            "replace with current values."
        ),
        "verified": True,
    },
    "treasury_bills": {
        "label": "TreasuryDirect — Treasury bills",
        "url": "https://treasurydirect.gov/marketable-securities/treasury-bills/",
        "scope": (
            "States that bills have terms from 4 to 52 weeks, that the rate is fixed at auction, that "
            "they may be held to maturity or sold earlier, and that interest is federally taxable but "
            "exempt from state and local tax."
        ),
        "verified": True,
    },
    "treasury_notes": {
        "label": "TreasuryDirect — Treasury notes",
        "url": "https://www.treasurydirect.gov/marketable-securities/treasury-notes/",
        "scope": (
            "States that notes include a 2-year maturity, pay a fixed auction rate, may be held to "
            "maturity or sold earlier, and that interest is federally taxable but exempt from state "
            "and local tax."
        ),
        "verified": True,
    },
    "fed_1929": {
        "label": "Federal Reserve History — Stock Market Crash of 1929",
        "url": "https://www.federalreservehistory.org/essays/stock-market-crash-of-1929",
        "scope": (
            "Reports that the Dow peaked at 381.17 on September 3, 1929, closed at 41.22 on July 8, "
            "1932, which was 89 percent below the peak, and did not regain the 1929 high until "
            "November 23, 1954. It also reports declines of nearly 13 percent on October 28, 1929 and "
            "nearly 12 percent the next day. This is a price index history, not a total return."
        ),
        "verified": True,
    },
    "fed_2008": {
        "label": "Federal Reserve History — The Great Recession",
        "url": "https://www.federalreservehistory.org/essays/great-recession-of-200709",
        "scope": (
            "Reports that the recession ran December 2007 to June 2009, that home prices fell "
            "approximately 30 percent on average from the mid-2006 peak to mid-2009, that the S&P 500 "
            "fell 57 percent from its October 2007 peak to its March 2009 trough, that real GDP fell "
            "4.3 percent peak to trough and that unemployment peaked at 10 percent in October 2009."
        ),
        "verified": True,
    },
    "bls_cpi": {
        "label": "Bureau of Labor Statistics — CPI, June 2022",
        "url": "https://www.bls.gov/opub/ted/2022/consumer-prices-up-9-1-percent-over-the-year-ended-june-2022-largest-increase-in-40-years.htm",
        "scope": (
            "Reports a 9.1 percent twelve-month CPI increase through June 2022, the largest such "
            "increase since November 1981. It is a historical observation, not a long-run assumption."
        ),
        "verified": True,
    },
    "cbo_rates": {
        "label": "Congressional Budget Office — interest rate scenarios, 2026 to 2036",
        "url": "https://www.cbo.gov/publication/62809",
        "scope": (
            "Reports CBO's average 10-year Treasury rate for its 2026-2036 projection and higher-rate "
            "scenarios. It is a ten-year budget projection, not a fifty-year forecast, a house price "
            "forecast or a household return."
        ),
        "verified": True,
    },
    "fhfa_hpi": {
        "label": "Federal Housing Finance Agency — House Price Index summary tables",
        "url": "https://www.fhfa.gov/data/hpi/summary-tables",
        "scope": (
            "Publishes state and metropolitan area house price indexes, including the California index "
            "used to adjust the Proposition 19 value limit. Index history informs scenario design; it "
            "is not an appraisal or a forecast for an individual property."
        ),
        "verified": True,
    },
    "sec_stocks": {
        "label": "SEC Investor.gov — stocks",
        "url": "https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks",
        "scope": (
            "Explains stock risks, the possibility of loss and the role of diversification. It does not "
            "prescribe a return assumption or an allocation."
        ),
        "verified": True,
    },
    "hud_fmr": {
        "label": "HUD — Fair Market Rents",
        "url": "https://www.huduser.gov/portal/datasets/fmr.html",
        "scope": (
            "Describes annual Fair Market Rent estimates used for specified housing programs. FMR is a "
            "program benchmark, not an appraisal, a lawful rent determination or a current lease amount."
        ),
        "verified": True,
    },
    # ---------------------------------------------------------------- privacy
    "gh_sensitive": {
        "label": "GitHub Docs — removing sensitive data from a repository",
        "url": "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository",
        "scope": (
            "Explains the coordination and side effects of history rewrites and warns that pull "
            "requests, forks, caches and clones can retain data. GitHub Support or repository owner "
            "action may be needed."
        ),
        "verified": True,
    },
    # ----------------------------------------------------- retrieval failures
    "ftb_inheritance_404": {
        "label": "FTB — gifts and inheritances page (retrieval failed)",
        "url": "https://www.ftb.ca.gov/file/personal/income-types/income-from-gifts-and-inheritances.html",
        "scope": (
            "Direct retrieval failed during an earlier session and was not successfully re-read in "
            "this one. No California income tax treatment of an inheritance is asserted in this site."
        ),
        "verified": False,
    },
    "scc_rate_unverified": {
        "label": "Santa Clara County composite tax rate — not retrieved",
        "url": "https://www.boe.ca.gov",
        "scope": (
            "No official county tax-rate-area rate for Property A was retrieved during this build, so "
            "the composite rate is not confirmed from an official page. The rate used in projections "
            "is derived from the owner's own bill and is labeled an owner-derived figure, not an "
            "official rate."
        ),
        "verified": False,
    },
    "cupertino_water_unverified": {
        "label": "Property A retail water provider — not confirmed",
        "url": "https://www.cupertino.gov",
        "scope": (
            "The retail water provider for the specific parcel was not confirmed from an official "
            "record during this build. More than one provider serves the postal area. The provider and "
            "the tariff must be read from the account or bill."
        ),
        "verified": False,
    },
}


def source(key: str) -> dict:
    if key not in SOURCES:
        raise KeyError(f"Unregistered source key: {key}")
    return SOURCES[key]
