#!/usr/bin/env python3
"""Builds the public, privacy-first inheritance decision workspace.

Conventions enforced by tools/verify.py:
- every page: one h1, noindex, restrictive CSP, external assets only, no forms
  that submit, every table row carries an official source link and evidence badge;
- every external link uses HTTPS + rel="noopener noreferrer" and points to an
  official host;
- every currency amount printed anywhere is a multiple of $10 (the owner's
  anti-tracing rounding rule) except the whitelisted statutory figure
  $1,044,586 (BOE Letter to Assessors 2025/009);
- placeholders only: Property A / Property B / Heir / Trustor; county-level
  geography; no addresses, postal codes, names, or unrounded case figures.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKED = "2026-11-15"

# ---------------------------------------------------------------- sources ---
# Official (or explicitly-flagged secondary) sources only. scope states what
# the link does and does not establish.
SOURCES: dict[str, tuple[str, str, str]] = {
    "probate_16061_7": (
        "California Probate Code §16061.7",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum=16061.7.",
        "Trustee notification when a revocable trust becomes irrevocable; served on beneficiaries and heirs; not later than 60 days after the event. Does not validate private trust terms.",
    ),
    "rtc_480": (
        "California Revenue and Taxation Code §480",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=480.",
        "Change-in-ownership statement duties; for transfers by death through a trust, the trustee files within 150 days after the date of death. Reporting rule only; it does not set values.",
    ),
    "rtc_480_3": (
        "California Revenue and Taxation Code §480.3",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=480.3.",
        "Preliminary Change of Ownership Report filed with the recorder; an additional recording fee of $20 may apply without it. Does not assess the property.",
    ),
    "rtc_63_2": (
        "California Revenue and Taxation Code §63.2",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=63.2.",
        "Prop 19 family-home/family-farm intergenerational exclusion operative on and after February 16, 2021: transferee principal residence within one year, homeowners' or veterans' exemption filed within one year, exclusion removed when eligibility ends, and the value enrolled from the next lien date thereafter is the base year value established as of the change-in-ownership date, adjusted annually. Statutory text; eligibility depends on private facts.",
    ),
    "rtc_63_1": (
        "California Revenue and Taxation Code §63.1",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=63.1.",
        "Prior-law parent-child exclusion framework (governs transfers before February 16, 2021). Historical context only for a 2040-2050 transfer.",
    ),
    "rtc_218": (
        "California Revenue and Taxation Code §218",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=218.",
        "Homeowners' exemption of $7,000 of full value; does not extend to property that is rented, vacant, or a secondary home. Amount is statutory; eligibility is fact-specific.",
    ),
    "rtc_18662": (
        "California Revenue and Taxation Code §18662",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=18662.",
        "California withholding on the sale of California real estate by nonresidents (currently 3.333% of gross sales price under the statutory rate framework; confirm the current rate with the Franchise Tax Board at the sale date). Applies only if the seller is a nonresident.",
    ),
    "const_13a": (
        "California Constitution Article XIII A (Proposition 13)",
        "https://leginfo.legislature.ca.gov/faces/codes_displayArticle.xhtml?lawCode=CONS&division=&articleNum=XIIIA",
        "Base 1% ad valorem levy and the 2% maximum annual assessed-value increase while ownership is unchanged; reassessment on change in ownership or new construction.",
    ),
    "boe_pub801": (
        "California BOE Publication 801 — Proposition 19 fact sheet",
        "https://www.boe.ca.gov/pdf/pub801.pdf",
        "Official summary of the intergenerational exclusion: forms BOE-19-P / BOE-19-G, one-year occupancy and exemption filing, filing period, and worked value-limit example.",
    ),
    "boe_lta25009": (
        "California BOE Letter to Assessors 2025/009",
        "https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf",
        "Adjusts the $1,000,000 exclusion amount to $1,044,586 for transfers from February 16, 2025 through February 15, 2027. The amount re-adjusts every two years.",
    ),
    "boe_annot_625": (
        "California BOE Property Tax Annotations 625.0000",
        "https://www.boe.ca.gov/lawguides/property/current/ptlg/annt/625-0000-all.html",
        "A change in ownership of property held in a revocable trust occurs when the trust becomes irrevocable, not when a deed is later recorded.",
    ),
    "boe_annot_220": (
        "California BOE Property Tax Annotations 220.0000",
        "https://www.boe.ca.gov/lawguides/property/current/ptlg/annt/220-0000-all.html",
        "Change in ownership timing for revocable trusts and exclusions that can apply when the trust becomes irrevocable.",
    ),
    "scc_ratebook": (
        "Santa Clara County Tax Rate Book 2025-2026",
        "https://files.santaclaracounty.gov/exjcpb1531/2025-11/tax-rate-book-2025-2026.pdf?VersionId=HHMZ1VmGwFXqVvpM36xuptkIcV2V8ctE",
        "Official 2025-2026 secured tax rates by tax-rate area for Santa Clara County. The exact Cupertino rate area must be confirmed against the parcel's own tax bill.",
    ),
    "scc_assessor_transfer": (
        "Santa Clara County Assessor — transfers and Proposition 19",
        "https://www.sccassessor.org/component/k2/itemlist/tag/Transfer",
        "County procedure for the parent-child exclusion: occupancy plus homeowners' exemption within one year; claim within three years for full relief.",
    ),
    "scc_assessor_root": (
        "Santa Clara County Assessor-Recorder",
        "https://asr.santaclaracounty.gov/",
        "County office where assessments, Prop 19 claims and recorded transfer documents are administered; the owner can verify assessment history here.",
    ),
    "sf_treasurer": (
        "San Francisco Treasurer & Tax Collector — property tax",
        "https://sftreasurer.org/property-tax-payments",
        "Official bill portal and property-tax reference. The published FY 2025-26 secured ad valorem rate is 1.18268325%; confirm the rate on the parcel's own bill.",
    ),
    "sf_assessor_root": (
        "San Francisco Office of the Assessor-Recorder",
        "https://sfassessor.org/",
        "County office where San Francisco assessed values, exemptions and exclusions are administered; the owner can verify assessment history here.",
    ),
    "irs_whatsnew": (
        "IRS — What's new: estate and gift tax",
        "https://www.irs.gov/businesses/small-businesses-self-employed/whats-new-estate-and-gift-tax",
        "Public Law 119-21 amended §2010(c)(3) to set the 2026 basic exclusion amount at $15,000,000. Confirms the post-2025 estate-tax framework.",
    ),
    "irs_2027": (
        "IRS IR-2026-133 — tax year 2027 inflation adjustments",
        "https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2027-taxpayers-continue-to-benefit-from-the-working-families-tax-cuts",
        "2027 basic exclusion amount $15,480,000 (2026: $15,000,000); annual gift exclusion 2027 $20,000 (2026: $19,000); non-citizen spouse exclusion 2027 $201,000 (2026: $194,000).",
    ),
    "congress_hr1": (
        "Congress.gov — H.R. 1, Public Law 119-21 (One Big Beautiful Bill Act)",
        "https://www.congress.gov/bill/119th-congress/house-bill/1",
        "Section 70106 increases the base estate, gift and GST exemption to $15,000,000 after 2025, adjusted for inflation. Enacted July 4, 2025.",
    ),
    "irs_estate_tax": (
        "IRS — Estate tax",
        "https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax",
        "Gross estate composition, deductions and the year-of-death Form 706 filing threshold. Filing test depends on the private estate inventory.",
    ),
    "irs_estate_faq": (
        "IRS — Estate tax FAQs",
        "https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-estate-taxes",
        "Form 706 due nine months after death with an up-to-six-month extension; portability election mechanics for a surviving spouse.",
    ),
    "irs_gift_faq": (
        "IRS — Gift tax FAQs",
        "https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-gift-taxes",
        "Annual exclusion mechanics, gift-splitting and Form 709 filing. Current-year amounts are on the IRS inflation-adjustment pages.",
    ),
    "irs_p551": (
        "IRS Publication 551 — Basis of Assets",
        "https://www.irs.gov/publications/p551",
        "Basis of property received from a decedent is generally fair market value at the date of death (stepped-up basis), subject to exceptions and consistent-basis reporting.",
    ),
    "irs_p523": (
        "IRS Publication 523 — Selling Your Home",
        "https://www.irs.gov/publications/p523",
        "Section 121 exclusion of gain on a main home: up to $250,000 single / $500,000 married for taxpayers who owned and used the home as a main residence for two of the five years before sale.",
    ),
    "irs_p527": (
        "IRS Publication 527 — Residential Rental Property",
        "https://www.irs.gov/publications/p527",
        "Rental income, deductible expenses, depreciation, personal use and vacation-home limits. Establishes the framework, not any property's numbers.",
    ),
    "irs_gifts_faq": (
        "IRS — Gifts and inheritances FAQ",
        "https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances",
        "Inheritances are generally not taxable income to the beneficiary; income produced later is taxable; inherited-property basis is generally date-of-death value.",
    ),
    "irs_p559": (
        "IRS Publication 559 — Survivors, Executors and Administrators",
        "https://www.irs.gov/publications/p559",
        "Estate administration overview: income in respect of a decedent, Form 1041 fiduciary filings, and recordkeeping duties.",
    ),
    "sco_estate": (
        "California State Controller — Estate Tax",
        "https://www.sco.ca.gov/ardtax_estate_tax.html",
        "For decedents dying on or after January 1, 2005 there is no requirement to file a California estate tax return; the state inheritance tax program applies only to pre-1982 decedents.",
    ),
    "ftb_root": (
        "California Franchise Tax Board",
        "https://www.ftb.ca.gov/",
        "California personal income tax administration. Confirm current capital-gain and withholding treatment for any actual sale with the FTB or a tax adviser.",
    ),
    "hud_fmr": (
        "HUD — Fair Market Rents (FY data)",
        "https://www.huduser.gov/portal/datasets/fmr.html",
        "HUD publishes FMRs at roughly the 40th percentile of local gross rents by bedroom size. A benchmark, not an appraisal and not any property's achievable rent.",
    ),
    "fedhist_1929": (
        "Federal Reserve History — Stock Market Crash of 1929",
        "https://www.federalreservehistory.org/essays/stock-market-crash-of-1929",
        "Dow peak 381.17 on September 3, 1929; trough 41.22 on July 8, 1932 (89% below peak); recovery to the 1929 high only in November 1954.",
    ),
    "fedhist_recession": (
        "Federal Reserve History — The Great Recession and its aftermath",
        "https://www.federalreservehistory.org/essays/great-recession-and-its-aftermath",
        "U.S. average home prices fell by over a fifth from Q1 2007 to Q2 2011 (FHFA HPI); the 2007-09 crisis context for crash-entry scenarios.",
    ),
    "fedhist_depression": (
        "Federal Reserve History — The Great Depression",
        "https://www.federalreservehistory.org/essays/great-depression",
        "1929-1941 downturn context: depth, duration and the banking-panic sequence that a long-horizon plan must be able to survive.",
    ),
    "damodaran": (
        "NYU Stern (A. Damodaran) — Historical returns on stocks, bonds and bills, 1928-2025",
        "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html",
        "SECONDARY academic compilation (January 2026 update) of annual S&P 500 total returns and average T-bill rates used for the stress tables. Verify headline years against primary market data before relying on them.",
    ),
    "treasury_bills": (
        "TreasuryDirect — Treasury bills",
        "https://www.treasurydirect.gov/marketable-securities/treasury-bills/",
        "Terms of 4 to 52 weeks, rates set at auction, interest federally taxable but exempt from state and local income tax — relevant to a California heir parking proceeds.",
    ),
    "treasury_notes": (
        "TreasuryDirect — Treasury notes",
        "https://www.treasurydirect.gov/marketable-securities/treasury-notes/",
        "Notes include a 2-year maturity with a fixed auction rate; interest also exempt from state and local income tax.",
    ),
    "investor_stocks": (
        "SEC Investor.gov — Stocks",
        "https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks",
        "Risk disclosure for equity investing; no return assumption or allocation advice.",
    ),
    "cdi_residential": (
        "California Department of Insurance — Residential insurance",
        "https://www.insurance.ca.gov/01-consumers/105-type/5-residential/index.cfm",
        "Shopping tools and consumer guidance for homeowners, renters and condo policies; explains limited FAIR Plan perils and difference-in-conditions policies. No individual premium.",
    ),
    "cafairplan": (
        "California FAIR Plan Association",
        "https://www.cafairplan.com/",
        "The state's residual fire-insurance market of last resort; limited perils. Confirms that some California homes can no longer buy standard HO-3 coverage.",
    ),
    "cpuc_nem": (
        "California Public Utilities Commission — Net energy metering and net billing",
        "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/customer-generation/net-energy-metering-and-net-billing",
        "Solar compensation framework (NEM vs net billing); the applicable tariff and interconnection date determine a household's actual credits.",
    ),
    "cpuc_sjw": (
        "California Public Utilities Commission — San Jose Water rate proceeding document",
        "https://docs.cpuc.ca.gov/PublishedDocs/Efile/G000/M522/K429/522429327.PDF",
        "Rate-case exhibit for the investor-owned utility serving Cupertino: average residential bill figures in the low-to-mid $100s per month were at issue. Confirms the order of magnitude only.",
    ),
    "sfpuc": (
        "San Francisco Public Utility Commission",
        "https://sfpuc.org/",
        "Water and wastewater utility for San Francisco; rate schedules and billing structure for multi-unit buildings.",
    ),
    "civ_1947_12": (
        "California Civil Code §1947.12 (Tenant Protection Act)",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1947.12.",
        "Statewide rent-increase cap and just-cause framework with exemptions; local ordinances may be stricter. Coverage depends on property facts.",
    ),
    "sos_ballot": (
        "California Secretary of State — Ballot measures",
        "https://www.sos.ca.gov/elections/ballot-measures",
        "Official status of qualifying initiatives, including any Proposition 19-related amendment or repeal effort. Verify status near the transfer date.",
    ),
    "cbo_rates": (
        "Congressional Budget Office — interest-rate outlook (report 62809)",
        "https://www.cbo.gov/publication/62809",
        "CBO's 10-year Treasury rate projections used only as a scenario anchor for Treasury-parking yield assumptions; not a 50-year forecast.",
    ),
    "fhfa_hpi": (
        "Federal Housing Finance Agency — HPI summary tables",
        "https://www.fhfa.gov/data/hpi/summary-tables",
        "Official metro/state house-price indexes that can inform appreciation scenario design; not a valuation or forecast for an individual property.",
    ),
    "bls_cpi": (
        "U.S. Bureau of Labor Statistics — Consumer Price Index",
        "https://www.bls.gov/cpi/",
        "Official CPI data used as the anchor for inflation assumptions in long-horizon projections.",
    ),
    "cslb": (
        "California Contractors State License Board — license check",
        "https://www.cslb.ca.gov/OnlineServices/CheckLicenseII/CheckLicense.aspx",
        "Verify any contractor used for inherited-property repair bids. Does not price repairs.",
    ),
    "waterboards": (
        "California State Water Resources Control Board — Drinking Water Program",
        "https://www.waterboards.ca.gov/drinking_water/programs/",
        "State oversight of public water systems; the actual bill comes from the local provider.",
    ),
    "github_repo": (
        "GitHub — public repository (current tree and history)",
        "https://github.com/wingbangboozle1-lang/Tino4",
        "The public repository itself: the current tree is clean, while historical commits remain reachable and still require owner-coordinated cleanup.",
    ),
}

# Local pages that can be cited as sources for process/meta claims.
LOCAL_PAGES = {
    "black-swan.html": ("Black-swan conditions page (this site)", "Real-data stress tables for crash entries and staging strategies."),
    "decision-analysis.html": ("Compare paths page (this site)", "The path matrix, cash flows and what-if controls produced the ranking quoted here."),
    "suggestions.html": ("Suggestions page (this site)", "The review queue whose choices are recorded locally."),
    "privacy.html": ("Privacy & limits page (this site)", "The enforced privacy rules, placeholders and rounding policy."),
}

# ------------------------------------------------------------- case model ---
# Owner-provided figures are ROUNDED TO THE NEAREST $10 before entering this
# file (owner instruction). All model outputs are rounded to $10 at display.
# Nothing here is verified by an official source; badges mark every row.

A_VALUE = 3_100_000          # owner estimate, Nov 2026 (rounded)
A_BASE_2026 = 550_540        # owner-provided assessed value 2026 (rounded)
A_TAX_2025 = 7_210           # owner-provided property tax 2025 (rounded)
A_WATER_MONTH_LOW, A_WATER_MONTH_HIGH = 100, 150     # owner range
A_SOLAR_CREDIT_LOW, A_SOLAR_CREDIT_HIGH = 10, 20     # monthly net credit (owner)
A_INSURANCE_GUESS = 1_500    # owner guess; unverified; industry range wider
A_RENT_MONTH_EST = 7_000     # estimate anchored to HUD FMR + market context

B_VALUE = 1_800_000          # owner estimate, Nov 2026 (rounded)
B_BASE_2025 = 114_250        # owner-provided assessed value 2025 (rounded)
B_TAX_2025 = 2_440           # owner-provided property tax 2025 (rounded)
B_RENT_MONTH = 7_150         # owner-provided gross rent, 2 of 3 units (rounded)
B_WATER_MONTH_LOW, B_WATER_MONTH_HIGH = 330, 400      # owner range
B_ELEC_MONTH_LOW, B_ELEC_MONTH_HIGH = 30, 70           # owner range
B_INSURANCE_GUESS = 1_500    # owner guess for rental coverage; unverified

SCENARIOS = {"Low": 0.03, "Base": 0.045, "High": 0.06}   # nominal appreciation
INFLATION = 0.025
LEVY_SCC = 0.0117            # estimate: Cupertino ad-valorem composite; confirm in SCC rate book
LEVY_SF = 0.0118268325       # official FY 2025-26 secured rate (SF Treasurer)
CAP_2025 = 1_044_586         # official Prop 19 exclusion amount, 2/16/2025-2/15/2027
CAP_GROWTH = 0.022           # biennial adjustment history implies about 2.2%/yr (assumption)
DIRECT_A = A_TAX_2025 - A_BASE_2026 * LEVY_SCC        # derived fixed-assessment residual
DIRECT_B = B_TAX_2025 - B_BASE_2025 * LEVY_SF         # derived fixed-assessment residual
INSURANCE_GROWTH = 0.04
UTILITIES_GROWTH = 0.03
RENT_GROWTH = 0.03
MAINT_A = 0.009              # share of market value per year (assumption; owner says lighter than B)
MAINT_B = 0.013              # share of market value per year (assumption; older multi-unit)
VACANCY_MGMT = 0.08          # of gross rent (assumption)
SELLING_COSTS = 0.06         # agent + closing (assumption; range 5-7%)
PORTFOLIO_RETURN = 0.065     # nominal, planning assumption (flagged)
TREASURY_YIELD = 0.042       # scenario anchor for parked proceeds (flagged)
TRANSFER_YEAR_BASE = 2045    # midpoint of the owner's 2040-2050 window
A_BASIS_2026 = A_BASE_2026   # for context only; basis resets to FMV at death (Pub 551)

HORIZON_END = 2075


def r10(x: float) -> int:
    """Round to the nearest $10 (owner anti-tracing rule)."""
    return int(round(x / 10.0) * 10)


def money(x: float) -> str:
    return "$" + f"{r10(x):,}"


def signed_money(x: float) -> str:
    v = r10(x)
    return ("+" if v >= 0 else "-") + "$" + f"{abs(v):,}"


def pct(x: float, digits: int = 2) -> str:
    return f"{x * 100:.{digits}f}%"


# ------------------------------------------------------- model functions ----

def fmv_at(year: int, base_value: float = A_VALUE, growth: float = SCENARIOS["Base"]) -> float:
    return base_value * (1 + growth) ** (year - 2026)


def factored_base_at(year: int) -> float:
    return A_BASE_2026 * 1.02 ** (year - 2026)


def cap_at(year: int) -> float:
    return CAP_2025 * (1 + CAP_GROWTH) ** (year - 2025)


def prop19_new_base(year: int, growth: float) -> tuple[float, float, float]:
    """Returns (factored base, exclusion cap, new base if occupied)."""
    factored = factored_base_at(year)
    cap = cap_at(year)
    fmv = fmv_at(year, growth=growth)
    if fmv <= factored:
        return factored, cap, factored
    return factored, cap, factored + min(cap, fmv - factored)


def direct_at(year: int, direct: float) -> float:
    return direct * (1 + INFLATION) ** (year - 2026)


def tax_occupied(year: int, growth: float = SCENARIOS["Base"]) -> float:
    _, _, new_base = prop19_new_base(year, growth)
    return new_base * LEVY_SCC + direct_at(year, DIRECT_A)


def tax_reassessed(year: int, growth: float = SCENARIOS["Base"]) -> float:
    return fmv_at(year, growth=growth) * LEVY_SCC + direct_at(year, DIRECT_A)


def rent_gross_at(year: int, rent_month: float, growth: float = RENT_GROWTH) -> float:
    return rent_month * 12 * (1 + growth) ** (year - 2026)


def insurance_at(year: int, base_premium: float) -> float:
    return base_premium * (1 + INSURANCE_GROWTH) ** (year - 2026)


def utilities_a_at(year: int) -> float:
    water_mid = (A_WATER_MONTH_LOW + A_WATER_MONTH_HIGH) / 2 * 12
    solar_credit_mid = (A_SOLAR_CREDIT_LOW + A_SOLAR_CREDIT_HIGH) / 2 * 12
    return (water_mid - solar_credit_mid) * (1 + UTILITIES_GROWTH) ** (year - 2026)


def utilities_b_at(year: int) -> float:
    water_mid = (B_WATER_MONTH_LOW + B_WATER_MONTH_HIGH) / 2 * 12
    elec_mid = (B_ELEC_MONTH_LOW + B_ELEC_MONTH_HIGH) / 2 * 12
    return (water_mid + elec_mid) * (1 + UTILITIES_GROWTH) ** (year - 2026)


def carrying_occupied(year: int, growth: float = SCENARIOS["Base"]) -> dict[str, float]:
    fmv = fmv_at(year, growth=growth)
    return {
        "tax": tax_occupied(year, growth),
        "insurance": insurance_at(year, A_INSURANCE_GUESS),
        "maintenance": MAINT_A * fmv,
        "utilities": utilities_a_at(year),
    }


def rental_net(year: int, growth: float = SCENARIOS["Base"]) -> dict[str, float]:
    fmv = fmv_at(year, growth=growth)
    gross = rent_gross_at(year, A_RENT_MONTH_EST)
    costs = {
        "tax": tax_reassessed(year, growth),
        "insurance": insurance_at(year, A_INSURANCE_GUESS),
        "maintenance": MAINT_A * fmv,
        "utilities": utilities_a_at(year),
        "vacancy_mgmt": VACANCY_MGMT * gross,
    }
    return {"gross": gross, "costs": costs, "net": gross - sum(costs.values())}


def b_cashflow(year: int) -> dict[str, float]:
    gross = rent_gross_at(year, B_RENT_MONTH)
    costs = {
        "tax": B_TAX_2025 * (1.02 ** (year - 2025)) + direct_at(year, DIRECT_B),
        "insurance": insurance_at(year, B_INSURANCE_GUESS),
        "maintenance": MAINT_B * fmv_at(year, base_value=B_VALUE, growth=SCENARIOS["Base"]),
        "utilities": utilities_b_at(year),
        "vacancy_mgmt": VACANCY_MGMT * gross,
    }
    return {"gross": gross, "costs": costs, "net": gross - sum(costs.values())}


def sale_proceeds(year: int, growth: float = SCENARIOS["Base"]) -> float:
    return fmv_at(year, growth=growth) * (1 - SELLING_COSTS)


def wealth_path_sell(year_start: int, year_end: int, growth: float, ret: float) -> float:
    return sale_proceeds(year_start, growth) * (1 + ret) ** (year_end - year_start)


def wealth_path_occupy(year_start: int, year_end: int, growth: float) -> float:
    """Home equity minus cumulative out-of-pocket carrying costs (nominal)."""
    fmv_end = fmv_at(year_end, growth=growth)
    cost = 0.0
    for y in range(year_start + 1, year_end + 1):
        c = carrying_occupied(y, growth)
        cost += c["tax"] + c["insurance"] + max(c["maintenance"], 0.0) + c["utilities"]
    return fmv_end - cost


def wealth_path_rent(year_start: int, year_end: int, growth: float) -> float:
    fmv_end = fmv_at(year_end, growth=growth)
    drain = 0.0
    for y in range(year_start + 1, year_end + 1):
        drain += max(-rental_net(y, growth)["net"], 0.0)
    return fmv_end - drain


# ------------------------------------------------- verified return series ---
# NYU Stern (Damodaran), January 2026 update, annual figures; fetched and
# transcribed on CHECKED. (year, S&P 500 total return %, average 3-month T-bill %)
ANNUAL_RETURNS: list[tuple[int, float, float]] = [
    (1928, 43.81, 3.08), (1929, -8.30, 3.16), (1930, -25.12, 4.55), (1931, -43.84, 2.31),
    (1932, -8.64, 1.07), (1933, 49.98, 0.96), (1934, -1.19, 0.28), (1935, 46.74, 0.17),
    (1936, 31.94, 0.17), (1937, -35.34, 0.28), (1938, 29.28, 0.07), (1939, -1.10, 0.05),
    (1940, -10.67, 0.04), (1941, -12.77, 0.13), (1942, 19.17, 0.34), (1943, 25.06, 0.38),
    (1944, 19.03, 0.38), (1945, 35.82, 0.38), (1946, -8.43, 0.38), (1947, 5.20, 0.60),
    (1948, 5.70, 1.05), (1949, 18.30, 1.12), (1950, 30.81, 1.20), (1951, 23.68, 1.52),
    (1952, 18.15, 1.72), (1953, -1.21, 1.89), (1954, 52.56, 0.94), (1955, 32.60, 1.72),
    (1956, 7.44, 2.62), (1957, -10.46, 3.22), (1958, 43.72, 1.77), (1959, 12.06, 3.39),
    (1960, 0.34, 2.87), (1961, 26.64, 2.35), (1962, -8.81, 2.77), (1963, 22.61, 3.16),
    (1964, 16.42, 3.55), (1965, 12.40, 3.95), (1966, -9.97, 4.86), (1967, 23.80, 4.29),
    (1968, 10.81, 5.34), (1969, -8.24, 6.67), (1970, 3.56, 6.39), (1971, 14.22, 4.33),
    (1972, 18.76, 4.06), (1973, -14.31, 7.04), (1974, -25.90, 7.85), (1975, 37.00, 5.79),
    (1976, 23.83, 4.98), (1977, -6.98, 5.26), (1978, 6.51, 7.18), (1979, 18.52, 10.05),
    (1980, 31.74, 11.39), (1981, -4.70, 14.04), (1982, 20.42, 11.09), (1983, 22.34, 8.95),
    (1984, 6.15, 9.92), (1985, 31.24, 7.72), (1986, 18.49, 6.15), (1987, 5.81, 5.96),
    (1988, 16.54, 6.89), (1989, 31.48, 8.39), (1990, -3.06, 7.75), (1991, 30.23, 5.54),
    (1992, 7.49, 3.51), (1993, 9.97, 3.07), (1994, 1.33, 4.37), (1995, 37.20, 5.66),
    (1996, 22.68, 5.15), (1997, 33.10, 5.20), (1998, 28.34, 4.91), (1999, 20.89, 4.78),
    (2000, -9.03, 6.00), (2001, -11.85, 3.48), (2002, -21.97, 1.64), (2003, 28.36, 1.03),
    (2004, 10.74, 1.40), (2005, 4.83, 3.22), (2006, 15.61, 4.85), (2007, 5.48, 4.48),
    (2008, -36.55, 1.40), (2009, 25.94, 0.15), (2010, 14.82, 0.14), (2011, 2.10, 0.05),
    (2012, 15.89, 0.09), (2013, 32.15, 0.06), (2014, 13.52, 0.03), (2015, 1.38, 0.05),
    (2016, 11.77, 0.32), (2017, 21.61, 0.95), (2018, -4.23, 1.97), (2019, 31.21, 2.11),
    (2020, 18.02, 0.36), (2021, 28.47, 0.04), (2022, -18.04, 2.09), (2023, 26.06, 5.28),
    (2024, 24.88, 5.18), (2025, 17.78, 4.21),
]


def _series_lookup(year: int, column: int) -> float:
    for row in ANNUAL_RETURNS:
        if row[0] == year:
            return row[column]
    raise KeyError(year)


def strategy_wealth(entry: int, horizon: int, kind: str) -> float:
    """Ending value with entry capital normalized to 1.00, annual granularity.

    kind: lump | park24_lump | park24_dca24 | park36_dca36 | dca36
    """
    def prod(column: int, y0: int, y1: int) -> float:
        out = 1.0
        for y in range(y0, y1 + 1):
            out *= 1 + _series_lookup(y, column) / 100.0
        return out

    if kind == "lump":
        return prod(1, entry, horizon)
    if kind == "park24_lump":
        parked = prod(2, entry, entry + 1)
        return parked * prod(1, entry + 2, horizon)
    if kind == "park24_dca24":
        parked = prod(2, entry, entry + 1)
        first = parked * 0.5 * prod(1, entry + 2, horizon)
        second = parked * 0.5 * (1 + _series_lookup(entry + 2, 2) / 100.0) * prod(1, entry + 3, horizon)
        return first + second
    if kind == "park36_dca36":
        parked3 = prod(2, entry, entry + 2)
        total = 0.0
        for i, buy_year in enumerate((entry + 3, entry + 4, entry + 5)):
            share = parked3 * (1.0 / 3.0)
            for y in range(entry + 3, buy_year):
                share *= 1 + _series_lookup(y, 2) / 100.0
            share *= prod(1, buy_year, horizon)
            total += share
        return total / 3.0 * 3.0 if False else total
    if kind == "dca36":
        total = 0.0
        for i, buy_year in enumerate((entry, entry + 1, entry + 2)):
            share = 1.0 / 3.0
            for y in range(entry, buy_year):
                share *= 1 + _series_lookup(y, 2) / 100.0
            share *= prod(1, buy_year, horizon)
            total += share
        return total
    raise ValueError(kind)


STRATEGY_LABELS = [
    ("lump", "Lump sum at entry (day-one exposure)"),
    ("dca36", "Dollar-cost average over 36 months, no parking"),
    ("park24_lump", "Park 24 months in 3M-2Y Treasuries, then lump in"),
    ("park24_dca24", "Park 24 months, then phase in over 24 months"),
    ("park36_dca36", "Park 36 months, then phase in over 36 months"),
]
CRASH_ENTRIES = (1929, 2000, 2008, 2020)

# ---------------------------------------------------------------- helpers ---
def esc(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def source_link(key: str) -> str:
    if key.startswith("page:"):
        name = key[len("page:"):]
        label, scope = LOCAL_PAGES[name]
        return f'<a class="source" href="page:{esc(name)}" title="{esc(scope)}">{esc(label)}</a>'
    label, url, scope = SOURCES[key]
    return (
        f'<a class="source" href="{esc(url)}" title="{esc(scope)}" '
        f'rel="noopener noreferrer">{esc(label)}</a>'
    )


def source_cell(keys: list[str]) -> str:
    return (" &middot; ").join(source_link(key) for key in keys)


BADGES = {
    "verified": ("verified", "Confirmed against the linked official source this session."),
    "secondary": ("secondary", "From a reputable secondary compilation; verify against primary data before relying on it."),
    "owner": ("owner", "Owner-provided figure, rounded to the nearest $10; verify against private records."),
    "derived": ("derived", "Arithmetic derived from owner figures plus a stated rate; confirm with the official rate source."),
    "model": ("model", "Output of the transparent model on this site; every assumption is listed on the page."),
    "assumption": ("assumption", "Explicit assumption, adjustable in the what-if controls; not a forecast."),
    "missing": ("missing", "Unknown; left blank by policy. Blank means unknown, not zero."),
    "guidance": ("guidance", "General rule or process guidance; no private fact asserted."),
}


def badge(status: str) -> str:
    css, title = BADGES[status]
    return f'<span class="badge {css}" title="{esc(title)}">{esc(css.capitalize())}</span>'


def cell(value: object, status: str, keys: list[str]) -> str:
    value_html = esc(value) if value is not None and value != "" else '<span aria-hidden="true">—</span>'
    return f"<td>{value_html}<br>{badge(status)}<br>{source_cell(keys)}</td>"


def make_table(title: str, headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f'<th scope="col">{h}</th>' for h in headers)
    body = "".join(f"<tr>{''.join(cells)}</tr>" for cells in rows)
    return (
        f'<section class="table-section"><h2>{esc(title)}</h2>'
        f'<div class="table-scroll" tabindex="0" aria-label="{esc(title)}"><table>'
        f"<caption>{esc(title)}</caption><thead><tr>{head}</tr></thead>"
        f"<tbody>{body}</tbody></table></div></section>"
    )


def callout(title: str, text: str, kind: str = "info") -> str:
    return (
        f'<aside class="callout {kind}"><strong>{esc(title)}</strong><p>{esc(text)}</p></aside>'
    )


def prose(title: str, text: str) -> str:
    return f'<section class="prose"><h2>{esc(title)}</h2><p>{esc(text)}</p></section>'


def cards(title: str, items: list[tuple[str, str, str]]) -> str:
    body = "".join(
        f'<article class="card"><h3><a href="{esc(href)}">{esc(label)}</a></h3><p>{esc(text)}</p></article>'
        for href, label, text in items
    )
    return f'<section class="card-section"><h2>{esc(title)}</h2><div class="card-grid">{body}</div></section>'


NAV_GROUPS = [
    ("Start", [("index.html", "Decision overview"), ("pages/executive-summary.html", "Executive summary")]),
    ("Decide", [
        ("pages/decision-analysis.html", "Compare paths"),
        ("pages/questions.html", "Questions &amp; missing evidence"),
        ("pages/suggestions.html", "Suggestions for review"),
    ]),
    ("Numbers", [
        ("pages/projections.html", "Projection worksheet"),
        ("pages/property-tax.html", "Property-tax rules"),
        ("pages/operating-costs.html", "Costs &amp; coverage"),
    ]),
    ("Stress tests", [
        ("pages/black-swan.html", "Black-swan conditions"),
        ("pages/phased-investing.html", "Treasury staging tool"),
    ]),
    ("Law &amp; process", [
        ("pages/estate-thresholds.html", "Estate-tax thresholds"),
        ("pages/inheritance-process.html", "Deadline timeline"),
        ("pages/law-watchlist.html", "Law watchlist"),
    ]),
    ("Adviser &amp; evidence", [
        ("pages/attorney-cpa-brief.html", "Attorney &amp; CPA brief"),
        ("pages/flagged-for-review.html", "Flagged for review"),
        ("pages/glossary.html", "Glossary"),
        ("pages/sources.html", "Official source register"),
        ("pages/privacy.html", "Privacy &amp; limits"),
    ]),
]


def root_href(current: str, target: str) -> str:
    if current == "index.html":
        return target
    return "../" + target


def build_nav(current: str) -> str:
    groups = []
    for label, items in NAV_GROUPS:
        links = []
        for href, text in items:
            aria = ' aria-current="page"' if href == current else ""
            links.append(f'<a href="{root_href(current, href)}"{aria}>{text}</a>')
        groups.append(
            f'<details class="nav-group" open><summary>{label}</summary>'
            f'<div class="nav-items">{"".join(links)}</div></details>'
        )
    return f'<nav aria-label="Main navigation">{"".join(groups)}</nav>'


def render_page(path: str, title: str, intro: str, body: str, eyebrow: str = "DECISION WORKSPACE") -> str:
    current = path
    nav = build_nav(current)
    depth = "" if current == "index.html" else "../"
    if current == "index.html":
        body = body.replace('href="page:', 'href="pages/')
    else:
        body = body.replace('href="page:', 'href="')
    stylesheet = f"{depth}assets/style.css"
    script = f"{depth}assets/app.js"
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive"><meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="description" content="Privacy-first inheritance decision workspace: anonymized properties, figures rounded to the nearest $10, every row linked to an official source.">
<title>{esc(title)} · Private inheritance decision workspace</title>
<link rel="stylesheet" href="{stylesheet}"><script src="{script}" defer></script>
</head><body class=""><a class="skip" href="#main">Skip to content</a>
<div class="layout">
<aside class="sidebar"><a class="brand" href="{root_href(current, 'index.html')}"><span class="brand-icon" aria-hidden="true">&#9672;</span><span>PRIVATE<br>DECISION BRIEF</span></a>
<p class="sidebar-note">Trust transfer +<br>already-owned property</p>
{nav}
<div class="sidebar-bottom">Placeholders only; figures rounded to $10<br>Sources checked {CHECKED}</div></aside>
<div class="workspace"><header class="topbar"><span>RESEARCH / DECISION SUPPORT</span><div><span class="privacy-dot" aria-hidden="true"></span> Privacy-first <button class="print-button no-print" id="print-page" type="button">Print</button></div></header>
<main id="main"><div class="page-heading"><span class="eyebrow">{esc(eyebrow)}</span><h1>{esc(title)}</h1><p class="lead">{esc(intro)}</p></div>{body}
</main>
<footer><strong>Planning framework only.</strong> Not legal, tax, insurance, appraisal or investment advice. A source supports only its stated scope, not a private fact. Property figures are anonymized placeholders rounded to the nearest $10 per the owner's anti-tracing rule.<br>
<a href="{root_href(current, 'pages/privacy.html')}">Privacy &amp; limits</a> &middot; <a href="{root_href(current, 'pages/sources.html')}">Official sources</a> &middot; <a href="{root_href(current, 'pages/flagged-for-review.html')}">Flagged for review</a></footer>
</div></div></body></html>"""


# ------------------------------------------------------------- pages -------

def build_index() -> str:
    t = TRANSFER_YEAR_BASE
    tax_occ = tax_occupied(t)
    tax_re = tax_reassessed(t)
    delta = tax_re - tax_occ
    proceeds = sale_proceeds(t)
    rows = [
        [
            cell("Heir will occupy Property A as a primary residence within one year of transfer",
                 "missing", ["rtc_63_2", "boe_pub801"]),
            cell("Locks the Prop 19 family-home exclusion (factored base + exclusion amount); otherwise full reassessment at market value",
                 "guidance", ["rtc_63_2"]),
            cell("Confirm occupancy intent with the Heir before any other analysis; file BOE-19-P and the homeowners' exemption early", "guidance", ["scc_assessor_transfer", "boe_pub801"]),
        ],
        [
            cell("Trustor sells Property A before death", "missing", ["rtc_63_2", "boe_pub801"]),
            cell("No Prop 13 base transfers to anyone; sale-at-step-up becomes clearly preferred over holding", "guidance", ["rtc_63_2", "irs_p551"]),
            cell("Review the Trustor's long-term plans and any 55+ base-transfer use at each planning review", "guidance", ["boe_pub801"]),
        ],
        [
            cell("Total estate (including the cash inheritance) exceeds the indexed federal exemption",
                 "missing", ["irs_estate_tax", "congress_hr1"]),
            cell("Form 706 filing, 40% federal rate above the exemption, and portability planning become live issues",
                 "guidance", ["irs_estate_faq", "congress_hr1"]),
            cell("Prepare a private estate inventory; calendar the nine-month Form 706 deadline against the death date", "guidance", ["irs_estate_faq"]),
        ],
        [
            cell("Multiple beneficiaries and a non-pro-rata allocation of the home versus other assets",
                 "missing", ["boe_pub801", "probate_16061_7"]),
            cell("An ineligible sibling's share can jeopardize the family-home exclusion; equalization payments change who is the eligible transferee", "guidance", ["boe_pub801"]),
            cell("Ask counsel how the trust allocates the residence; consider pro-rata structure before the transfer", "guidance", ["probate_16061_7"]),
        ],
        [
            cell("Trust type or terms differ from a simple revocable family trust (irrevocable, marital, QPRT)",
                 "missing", ["boe_annot_625", "irs_p551"]),
            cell("Step-up in basis, the change-in-ownership date and the exclusion analysis all depend on the instrument", "guidance", ["boe_annot_625", "irs_p551"]),
            cell("Obtain the executed trust and any amendments; confirm with counsel that basis step-up applies", "guidance", ["boe_annot_625"]),
        ],
        [
            cell("California Proposition 19 is amended or repealed before the transfer",
                 "missing", ["sos_ballot", "boe_pub801"]),
            cell("The entire Property A base-preservation analysis must be recomputed under then-current law", "guidance", ["rtc_63_2", "sos_ballot"]),
            cell("Re-check the Secretary of State's initiative page and BOE letters at each planning review", "guidance", ["sos_ballot"]),
        ],
        [
            cell("Insurance availability or pricing collapses further (FAIR-Plan-only coverage)",
                 "missing", ["cdi_residential", "cafairplan"]),
            cell("Carrying-cost projections and the rent-versus-sell comparison shift materially", "assumption", ["cdi_residential"]),
            cell("Refresh written owner-occupied and landlord quotes annually", "guidance", ["cdi_residential"]),
        ],
        [
            cell("Treasury yields are low at the time of sale, or markets are near a peak",
                 "missing", ["treasury_bills", "cbo_rates"]),
            cell("The Treasury-parking window earns little or costs upside; phasing length should be re-chosen with then-current data", "guidance", ["treasury_bills", "damodaran"]),
            cell("Use the black-swan stress tool with current yields before committing to a staging length", "guidance", ["page:black-swan.html"]),
        ],
    ]
    body = (
        callout(
            "Current answer: a conditional recommendation, not a single path",
            "The analysis on this site does rank paths under explicit assumptions, and the ranking is stable: if the Heir will occupy the Cupertino home within one year of transfer, occupying is favored; if not, selling at the stepped-up basis and staging proceeds into Treasuries before phasing into equities is favored; renting the reassessed home is dominated in every scenario tested. The ranking flips only on the decision-changing facts listed below, each of which is still unknown. That is why the facts, not the math, are the critical path.",
            "warning",
        )
        + make_table("What would change the answer?", ["Decision-changing fact", "Why it flips the ranking", "Next step / decision gate"], rows)
        + make_table("Headline numbers, base case (transfer assumed mid-window, year " + str(TRANSFER_YEAR_BASE) + ")", ["Quantity", "Value", "Evidence status", "Official source / scope"], [
            [
                cell("Property A market value at transfer (base 4.5% scenario)", "model", ["fhfa_hpi"]),
                cell(money(fmv_at(t)), "model", ["fhfa_hpi"]),
                cell("Factored Prop 13 base at transfer (2%/yr)", "derived", ["const_13a"]),
                cell(money(factored_base_at(t)), "derived", ["const_13a"]),
                cell("Prop 19 exclusion amount, projected with biennial-adjustment history", "assumption", ["boe_lta25009"]),
                cell(money(cap_at(t)), "assumption", ["boe_lta25009"]),
                cell("New assessed value if occupied (base + exclusion)", "model", ["rtc_63_2"]),
                cell(money(prop19_new_base(t, SCENARIOS["Base"])[2]), "model", ["rtc_63_2"]),
                cell("Annual property tax if occupied", "model", ["scc_ratebook"]),
                cell(money(tax_occ), "model", ["scc_ratebook"]),
                cell("Annual property tax if fully reassessed (rented or vacant)", "model", ["scc_ratebook", "rtc_63_2"]),
                cell(money(tax_re), "model", ["scc_ratebook"]),
                cell("Tax difference, per year, occupied vs reassessed", "model", ["scc_ratebook"]),
                cell(money(delta), "model", ["scc_ratebook"]),
                cell("Net proceeds if sold promptly at transfer (after 6% selling costs)", "model", ["fhfa_hpi"]),
                cell(money(proceeds), "model", ["fhfa_hpi"]),
            ],
        ])
        + prose(
            "Why these are placeholders, not addresses",
            "Property A is the Cupertino-area (Santa Clara County) family home expected to pass by trust around 2040-2050; Property B is the San Francisco Outer Sunset triplex the Heir already owns. The site publishes no addresses, parcel numbers, names, or postal codes, and rounds every figure to the nearest $10 so rounded tables cannot be matched back to any single parcel online. The owner-provided histories keep their shape but lose their exact fingerprints; exact unrounded values stay in private records only.",
        )
        + cards("Use this workspace in order", [
            ("pages/questions.html", "1. Resolve the questions", "Work the missing-evidence register; every row suggests how to discover the answer."),
            ("pages/decision-analysis.html", "2. Compare complete paths", "Pure and mixed paths with cash flows, wealth horizons and reinvestment risk beside each headline."),
            ("pages/black-swan.html", "3. Stress-test the entry", "Real 1928-2025 annual-return data tests Treasury parking against crash entries."),
            ("pages/attorney-cpa-brief.html", "4. Print the adviser brief", "One page for the attorney and tax adviser; no identifying details required."),
        ])
    )
    return render_page("index.html", "Decision overview", intro="A source-linked decision framework for two California properties: a Cupertino-area home arriving by trust (Property A) and an already-owned San Francisco Outer Sunset triplex (Property B). Figures are rounded to the nearest $10; every table row carries an official source and an evidence badge.", body=body, eyebrow="START HERE")


def build_executive_summary() -> str:
    t = TRANSFER_YEAR_BASE
    end = HORIZON_END
    g = SCENARIOS["Base"]
    w_sell_hi = wealth_path_sell(t, end, g, 0.065)
    w_sell_lo = wealth_path_sell(t, end, g, 0.045)
    w_occ = wealth_path_occupy(t, end, g)
    w_rent = wealth_path_rent(t, end, g)
    b_net = b_cashflow(2026)["net"]
    rows = [
        [
            cell("A — Occupy Property A (keep Prop 19 base)", "guidance", ["rtc_63_2"]),
            cell(money(tax_occupied(t)) + " / yr property tax in " + str(t), "model", ["scc_ratebook", "rtc_63_2"]),
            cell(money(w_occ) + " home equity at " + str(end) + " after carrying costs, plus rent-free housing", "model", ["fhfa_hpi"]),
            cell("Low market risk while owned; concentration in one property; exclusion can be lost if the Heir moves out", "guidance", ["rtc_63_2"]),
        ],
        [
            cell("B — Rent Property A (exclusion not claimed)", "guidance", ["rtc_63_2", "irs_p527"]),
            cell(money(tax_reassessed(t)) + " / yr property tax in " + str(t), "model", ["scc_ratebook"]),
            cell(money(w_rent) + " home equity at " + str(end) + " after cumulative rental drains", "model", ["fhfa_hpi"]),
            cell("Full reassessment at transfer; base-case rental result is a net loss of about " + money(-rental_net(t)["net"]) + " per year before risk", "model", ["scc_ratebook"]),
        ],
        [
            cell("C — Sell at transfer, park in 3M-2Y Treasuries 24-36 months, then phase into equities", "guidance", ["treasury_bills", "treasury_notes", "damodaran"]),
            cell(money(sale_proceeds(t)) + " net proceeds (after 6% costs)", "model", ["fhfa_hpi"]),
            cell(money(w_sell_hi) + " at " + str(end) + " assuming 6.5% nominal (" + money(w_sell_lo) + " at 4.5%)", "model", ["investor_stocks"]),
            cell("Reinvestment/sequence risk: parking delays equity entry — the black-swan table computes staged-versus-lump outcomes of "
                 + f"{strategy_wealth(1929, 1939, 'park24_dca24') / strategy_wealth(1929, 1939, 'lump'):.2f}x (1929 entry), "
                 + f"{strategy_wealth(2000, 2010, 'park24_dca24') / strategy_wealth(2000, 2010, 'lump'):.2f}x (2000 entry), "
                 + f"{strategy_wealth(2008, 2018, 'park24_dca24') / strategy_wealth(2008, 2018, 'lump'):.2f}x (2008 entry) and "
                 + f"{strategy_wealth(2020, 2025, 'park24_dca24') / strategy_wealth(2020, 2025, 'lump'):.2f}x (fast 2020 recovery)", "secondary", ["damodaran", "investor_stocks"]),
        ],
        [
            cell("D — Occupy two years or more, then sell (Section 121)", "guidance", ["irs_p523"]),
            cell(money(tax_occupied(t)) + " / yr while occupied", "model", ["scc_ratebook"]),
            cell("Excludes " + "$250,000" + " (single) / " + "$500,000" + " (married) of post-death appreciation at sale; selling immediately after death instead has near-zero taxable gain", "guidance", ["irs_p523", "irs_p551"]),
            cell("Only sensible if the Heir genuinely needs the housing; the Section 121 saving is small against a stepped-up basis", "guidance", ["irs_p523"]),
        ],
        [
            cell("E — Occupy one year, then decide freely (keep the option)", "guidance", ["rtc_63_2"]),
            cell(money(tax_occupied(t)) + " / yr while occupied", "model", ["scc_ratebook"]),
            cell("Preserves the exclusion long enough to file BOE-19-P; sale later carries tax only on post-death appreciation", "guidance", ["boe_pub801", "irs_p551"]),
            cell("Optionality has carrying costs; requires real occupancy intent, not intent on paper", "guidance", ["rtc_63_2"]),
        ],
    ]
    body = (
        callout("The one-sentence answer", "If the Heir will genuinely live in Property A, occupy within the Prop 19 one-year window: it converts the largest tax fact in the model into avoided cost plus housing otherwise paid for. If not, selling promptly at the stepped-up basis and staging the proceeds (24-36 months in 3M-2Y Treasuries, then phased equity entry) is favored; renting the reassessed home pairs the same concentration risk with negative annual carry in the base case (the exact figure is on the decision page), and only looks competitive when the Heir's own housing cost is left out of the comparison.", "info")
        + make_table("Path comparison (nominal, base-case assumptions; every assumption is adjustable in what-if controls)", ["Path", "Tax / cash headline", "Wealth headline (" + str(t) + " to " + str(end) + ")", "Reinvestment and other risks beside the headline"], rows)
        + make_table("Property B stays put (it is not part of the inheritance)", ["Quantity", "Value (2026)", "Evidence status", "Official source / scope"], [
            [
                cell("Gross rent, two rented units", "owner", ["hud_fmr", "irs_p527"]),
                cell(money(B_RENT_MONTH * 12) + " / yr", "owner", ["hud_fmr"]),
                cell("Net operating cash flow after tax, water, electricity, insurance, maintenance and 8% vacancy/management", "model", ["irs_p527", "sco_estate"]),
                cell(money(b_net) + " / yr (insurance premium still unverified)", "model", ["cdi_residential"]),
                cell("The Heir may also occupy the third unit without losing rental income, and could rent it if moving to Cupertino (adds roughly $2,700-$5,280 per month at HUD benchmarks, unverified)", "assumption", ["hud_fmr"]),
                cell("Property B's ultra-low Prop 13 base ($" + f"{B_BASE_2025:,}" + ") is worth protecting by never changing its ownership", "derived", ["const_13a"]),
            ],
        ])
        + prose(
            "Estate-tax snapshot",
            "California imposes no estate or inheritance tax for deaths on or after 2005. Federal law sets the 2026 basic exclusion at $15,000,000 per person ($30,000,000 for a married couple with portability), rising to $15,480,000 in 2027 with inflation indexing. Whether the estate exceeds the threshold depends on the cash inheritance and other assets, which are unknown here; the nine-month Form 706 deadline and a possible portability election are the calendar-critical items.",
        )
        + prose(
            "What this summary does not do",
            "It does not replace counsel on the trust instrument, the CPA on Form 706 and basis reporting, or an insurance professional on actual quotes. It ranks paths under stated assumptions so that advisers can argue with the assumptions instead of the conclusions.",
        )
    )
    return render_page("pages/executive-summary.html", "Executive summary", intro="The compressed answer: ranking of paths, headline numbers with reinvestment risk attached, and what remains unknown.", body=body, eyebrow="OVERVIEW")



def build_decisions() -> str:
    t = TRANSFER_YEAR_BASE
    g = SCENARIOS["Base"]
    occ = carrying_occupied(t, g)
    rn = rental_net(t, g)
    cash_rows = [
        [cell("Occupied (Path A)", "guidance", ["rtc_63_2"]),
         cell(money(occ["tax"]), "model", ["scc_ratebook", "rtc_63_2"]),
         cell(money(occ["insurance"]) + " (premium unverified)", "assumption", ["cdi_residential"]),
         cell(money(occ["maintenance"]), "assumption", ["cslb"]),
         cell(money(occ["utilities"]) + " (solar credit netted)", "owner", ["cpuc_sjw", "cpuc_nem"]),
         cell(money(sum(occ.values())), "model", ["scc_ratebook"])],
        [cell("Rented, reassessed (Path B)", "guidance", ["rtc_63_2", "irs_p527"]),
         cell(money(rn["costs"]["tax"]), "model", ["scc_ratebook"]),
         cell(money(rn["costs"]["insurance"]) + " (landlord coverage unverified)", "assumption", ["cdi_residential"]),
         cell(money(rn["costs"]["maintenance"]), "assumption", ["cslb"]),
         cell(money(rn["costs"]["vacancy_mgmt"] + rn["costs"]["utilities"]) + " incl. 8% vacancy/mgmt", "assumption", ["irs_p527"]),
         cell(signed_money(rn["net"]) + " / yr against gross rent of " + money(rn["gross"]), "model", ["hud_fmr"])],
        [cell("Sold and invested (Path C)", "guidance", ["treasury_bills", "investor_stocks"]),
         cell("none", "model", ["scc_ratebook"]),
         cell("none", "model", ["cdi_residential"]),
         cell("none", "model", ["cslb"]),
         cell("selling costs 6% at sale", "assumption", ["fhfa_hpi"]),
         cell(money(sale_proceeds(t, g)) + " proceeds; portfolio return " + pct(PORTFOLIO_RETURN) + " assumed", "assumption", ["investor_stocks", "cbo_rates"])],
    ]
    horizons = []
    for label, year_end in (("Ten years", t + 10), ("Thirty years", HORIZON_END)):
        horizons.append([
            cell(label + " (from year " + str(t) + ")", "guidance", ["fhfa_hpi"]),
            cell(money(wealth_path_occupy(t, year_end, g)), "model", ["fhfa_hpi", "rtc_63_2"]),
            cell(money(wealth_path_rent(t, year_end, g)), "model", ["fhfa_hpi", "scc_ratebook"]),
            cell(money(wealth_path_sell(t, year_end, g, PORTFOLIO_RETURN)), "model", ["investor_stocks"]),
            cell(money(wealth_path_sell(t, year_end, g, 0.045)), "model", ["investor_stocks"]),
        ])
    body = (
        callout("Decision tree", "First gate: will the Heir occupy Property A as a principal residence within one year of the date of death and file the homeowners' exemption in that window? If yes, Paths A, D and E open (the Prop 19 exclusion applies). If no, the home is fully reassessed at the date-of-death value, and the choice reduces to rent (B) versus sell-and-invest (C).", "info")
        + make_table("Annual cash flow at year " + str(t) + " by path (rounded to $10)", ["Path", "Property tax", "Insurance", "Maintenance", "Utilities / fees", "Net position"], cash_rows)
        + make_table("Wealth horizons (nominal)", ["Horizon", "A: home equity after carrying costs", "B: home equity after rental drains", "C: portfolio at " + pct(PORTFOLIO_RETURN), "C: portfolio at 4.5%"], horizons)
        + prose(
            "Reading the horizons honestly",
            "Path A's equity includes housing the Heir consumes by living in the home; Path C's portfolio is investable capital the Heir would otherwise use to pay rent elsewhere. The base case puts A and C within a comparable range once consumption is acknowledged, which is exactly why the occupancy question dominates the ranking: it is a lifestyle decision with a large tax option attached, not a purely financial one. Path B keeps the home's appreciation but adds negative annual carry (about " + money(-rn["net"]) + " per year in the base case: the reassessed tax bill and maintenance exceed rent), the same concentration risk without any housing use, and it beats Path A in the raw table only because the Heir's own housing cost is not counted — a cost Path A absorbs by providing the housing.",
        )
        + prose(
            "Reinvestment risk, stated beside each headline",
            "Every wealth headline above assumes reinvestment happens at the assumed return. That assumption fails at exactly the wrong times: the 1928-2025 record shows a lump-sum entry just before a crash spends years underwater, while parking in 3M-2Y Treasuries for 24-36 months and then phasing in preserved substantially more wealth through 1929- and 2008-shaped entries, at the cost of roughly 30% of the decade's outcome in a fast 2020-style recovery. The stress tables on the black-swan page quantify this from real annual data.",
        )
        + f"""<section class="tool-section"><h2>What-if controls (local-only, nothing stored)</h2>
<form id="decision-tool" novalidate>
<div class="tool-grid">
<label>Transfer year <input id="d-year" type="number" min="2040" max="2050" step="1" value="2045"></label>
<label>Appreciation %/yr <input id="d-growth" type="number" min="2" max="7" step="0.5" value="4.5"></label>
<label>Ad-valorem rate % <input id="d-levy" type="number" min="1" max="1.4" step="0.01" value="1.17"></label>
<label>Portfolio return %/yr <input id="d-return" type="number" min="3" max="9" step="0.5" value="6.5"></label>
<label>Market rent $/mo at transfer <input id="d-rent" type="number" min="5000" max="9000" step="100" value="7000"></label>
<label>Insurance $/yr today <input id="d-ins" type="number" min="1000" max="6000" step="100" value="1500"></label>
</div>
<div class="tool-actions"><button type="button" id="d-reset">Reset to base case</button>
<span class="tool-assumption">Model outputs are rounded to the nearest $10 and are not forecasts. The controls change only this page's display.</span></div>
</form>
<div class="table-scroll" tabindex="0" aria-label="What-if results"><table id="d-results"><caption>What-if results (recomputed locally)</caption><thead><tr><th scope="col">Quantity</th><th scope="col">Value</th><th scope="col">Evidence status</th><th scope="col">Scope note</th></tr></thead><tbody>
<tr><td>Market value at transfer</td><td id="d-out-fmv">—</td><td><span class="badge model">Model</span></td><td><a class="source" href="https://www.fhfa.gov/data/hpi/summary-tables" rel="noopener noreferrer">FHFA HPI — scenario design anchor</a></td></tr>
<tr><td>Factored Prop 13 base at transfer</td><td id="d-out-base">—</td><td><span class="badge derived">Derived</span></td><td><a class="source" href="https://leginfo.legislature.ca.gov/faces/codes_displayArticle.xhtml?lawCode=CONS&amp;division=&amp;articleNum=XIIIA" rel="noopener noreferrer">California Constitution Article XIII A</a></td></tr>
<tr><td>New assessed value if occupied</td><td id="d-out-newbase">—</td><td><span class="badge model">Model</span></td><td><a class="source" href="https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&amp;sectionNum=63.2." rel="noopener noreferrer">California Revenue and Taxation Code §63.2</a></td></tr>
<tr><td>Property tax if occupied</td><td id="d-out-tax-occ">—</td><td><span class="badge model">Model</span></td><td><a class="source" href="https://files.santaclaracounty.gov/exjcpb1531/2025-11/tax-rate-book-2025-2026.pdf?VersionId=HHMZ1VmGwFXqVvpM36xuptkIcV2V8ctE" rel="noopener noreferrer">Santa Clara County Tax Rate Book 2025-2026</a></td></tr>
<tr><td>Property tax if reassessed</td><td id="d-out-tax-re">—</td><td><span class="badge model">Model</span></td><td><a class="source" href="https://files.santaclaracounty.gov/exjcpb1531/2025-11/tax-rate-book-2025-2026.pdf?VersionId=HHMZ1VmGwFXqVvpM36xuptkIcV2V8ctE" rel="noopener noreferrer">Santa Clara County Tax Rate Book 2025-2026</a></td></tr>
<tr><td>Rental net if rented (reassessed)</td><td id="d-out-rentnet">—</td><td><span class="badge model">Model</span></td><td><a class="source" href="https://www.irs.gov/publications/p527" rel="noopener noreferrer">IRS Publication 527 — Residential Rental Property</a></td></tr>
<tr><td>Portfolio outcome at horizon if sold</td><td id="d-out-portfolio">—</td><td><span class="badge model">Model</span></td><td><a class="source" href="https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks" rel="noopener noreferrer">SEC Investor.gov — Stocks</a></td></tr>
</tbody></table></div>
</section>"""
        + prose(
            "Mixed paths, explicitly",
            "The pure choices (occupy, rent, sell) are not the only options. D — occupy at least two years and then sell — captures the Section 121 exclusion on post-death appreciation but is usually beaten by selling immediately unless the housing is genuinely needed. E — occupy one year to bank the exclusion, then decide — is the minimum-commitment version of A. F — sell Property A now in the Trustor's lifetime — is listed only to be rejected: it destroys the Prop 13 base the family would otherwise inherit and, absent a 55+ base transfer, hands the Heir a reassessed property with no exclusion at all.",
        )
    )
    return render_page("pages/decision-analysis.html", "Compare paths", intro="Live, rent, sell and the mixed paths, compared on cash flow and wealth horizons, with reinvestment risk stated beside each headline and local-only what-if controls.", body=body, eyebrow="DECIDE")


def build_questions() -> str:
    rows = [
        # Trust and title
        [cell("Q1. Is the trust a revocable living family trust, and are its amendments current?", "missing", ["boe_annot_625", "irs_p559"]),
         cell("Determines the change-in-ownership date, step-up in basis and the Prop 19 analysis", "guidance", ["boe_annot_625"]),
         cell("Obtain the executed trust plus all amendments; have counsel confirm trustee succession", "guidance", ["probate_16061_7"]),
         cell("High", "guidance", ["probate_16061_7"])],
        [cell("Q2. Are there multiple beneficiaries, and does the trust allocate the home pro-rata?", "missing", ["boe_pub801", "probate_16061_7"]),
         cell("Non-pro-rata allocations can make a sibling's share ineligible and trigger reassessment", "guidance", ["boe_pub801"]),
         cell("Ask counsel for the distribution scheme; model equalization payments before signing anything", "guidance", ["boe_pub801"]),
         cell("High", "guidance", ["boe_pub801"])],
        [cell("Q3. Are there liens, mortgages or reverse-mortgage encumbrances on Property A?", "missing", ["irs_p559"]),
         cell("Payoffs at death change net proceeds and the estate inventory", "guidance", ["irs_p559"]),
         cell("Pull a private title report and the latest loan statements", "guidance", ["irs_p559"]),
         cell("High", "guidance", ["irs_p559"])],
        [cell("Q4. When exactly is the transfer expected, and what is the Trustor's age/health context?", "missing", ["probate_16061_7"]),
         cell("The 2040-2050 window drives every projection; earlier transfers face different thresholds", "assumption", ["irs_estate_faq"]),
         cell("Have a private conversation; build the model on a defensible midpoint year", "guidance", ["probate_16061_7"]),
         cell("High", "guidance", ["probate_16061_7"])],
        # Occupancy
        [cell("Q5. Will the Heir genuinely occupy Property A within one year of death?", "missing", ["rtc_63_2", "boe_pub801"]),
         cell("The single largest economic fact in the whole decision (about " + money(tax_reassessed(TRANSFER_YEAR_BASE) - tax_occupied(TRANSFER_YEAR_BASE)) + " per year of tax difference in the base case)", "model", ["scc_ratebook"]),
         cell("Written family decision; if yes, calendar occupancy, BOE-266 and BOE-19-P immediately at death", "guidance", ["scc_assessor_transfer"]),
         cell("Critical", "guidance", ["rtc_63_2"])],
        [cell("Q6. Where would the Heir live while owning both homes?", "missing", ["hud_fmr"]),
         cell("Determines whether Property B's third unit rents out (extra income) or stays owner-occupied", "assumption", ["hud_fmr"]),
         cell("Decide housing plan before the transfer window; estimate the third-unit rent against HUD benchmarks", "guidance", ["hud_fmr"]),
         cell("Medium", "guidance", ["hud_fmr"])],
        # Estate size
        [cell("Q7. What is the total gross estate including the cash inheritance?", "missing", ["irs_estate_tax"]),
         cell("Above the indexed federal exemption, Form 706 and 40% planning become live", "guidance", ["congress_hr1"]),
         cell("Build a private inventory: all accounts, the trust corpus, life insurance, retirement plans", "guidance", ["irs_estate_tax"]),
         cell("High", "guidance", ["irs_estate_faq"])],
        [cell("Q8. Is the Trustor married, and is a portability election relevant?", "missing", ["irs_estate_faq"]),
         cell("Portability can double the usable exclusion but requires a timely Form 706", "guidance", ["irs_estate_faq"]),
         cell("Ask the estate attorney; calendar Form 706 if the first death approaches the threshold", "guidance", ["irs_estate_faq"]),
         cell("High", "guidance", ["irs_estate_faq"])],
        [cell("Q9. Has the Trustor made lifetime gifts beyond annual exclusions?", "missing", ["irs_gift_faq"]),
         cell("Taxable gifts reduce the exclusion available at death", "guidance", ["irs_gift_faq"]),
         cell("Collect Forms 709 history with the CPA", "guidance", ["irs_gift_faq"]),
         cell("Medium", "guidance", ["irs_gift_faq"])],
        [cell("Q10. Do retirement accounts or other assets pass outside the trust?", "missing", ["irs_p559"]),
         cell("Beneficiary designations bypass the trust; inherited-IRA rules differ sharply", "guidance", ["irs_p559"]),
         cell("Audit beneficiary designations on every account", "guidance", ["irs_p559"]),
         cell("Medium", "guidance", ["irs_p559"])],
        # Heir finances
        [cell("Q11. What is the Heir's income tax situation (bracket, residency state)?", "missing", ["ftb_root", "rtc_18662"]),
         cell("Determines tax on post-death appreciation if selling later, and California nonresident withholding if the Heir lives outside California", "guidance", ["rtc_18662"]),
         cell("Private session with the CPA; confirm residency and expected brackets", "guidance", ["ftb_root"]),
         cell("Medium", "guidance", ["ftb_root"])],
        [cell("Q12. What is the Heir's risk tolerance and timeline for the invested proceeds?", "missing", ["investor_stocks"]),
         cell("Sets the staging length for the Treasury-parking plan", "guidance", ["damodaran"]),
         cell("Write a private investment policy statement before sale proceeds arrive", "guidance", ["investor_stocks"]),
         cell("Medium", "guidance", ["investor_stocks"])],
        # Costs
        [cell("Q13. What is the actual Cupertino primary-residence premium quote today?", "missing", ["cdi_residential"]),
         cell("The owner's $1,500 guess is unverified; Bay Area high-value policies often quote well above it", "assumption", ["cdi_residential"]),
         cell("Request two admitted-market quotes and one FAIR-Plan-plus-DIC alternative", "guidance", ["cdi_residential", "cafairplan"]),
         cell("High", "guidance", ["cdi_residential"])],
        [cell("Q14. What is the actual San Francisco landlord (dwelling-fire) premium quote?", "missing", ["cdi_residential"]),
         cell("Triplex rental coverage differs from the owner's guess; vacancy clauses matter", "assumption", ["cdi_residential"]),
         cell("Request a landlord-policy quote covering three units and lost-rent cover", "guidance", ["cdi_residential"]),
         cell("High", "guidance", ["cdi_residential"])],
        [cell("Q15. Which solar net-metering tariff applies, and what is the exact annual credit?", "missing", ["cpuc_nem"]),
         cell("NEM 1.0/2.0 grandfathering versus net billing changes the utility line by hundreds of dollars per year", "assumption", ["cpuc_nem"]),
         cell("Pull 12 months of utility statements and the interconnection agreement", "guidance", ["cpuc_nem"]),
         cell("Medium", "guidance", ["cpuc_nem"])],
        [cell("Q16. What are 12 months of actual water, electricity and gas bills for both properties?", "missing", ["waterboards", "sfpuc"]),
         cell("Owner ranges are good but exact bills make the model honest", "owner", ["waterboards", "cpuc_sjw"]),
         cell("Collect statements; replace ranges with actuals in the private copy", "guidance", ["waterboards"]),
         cell("Medium", "guidance", ["waterboards"])],
        [cell("Q17. What is Property A's real maintenance profile (roof, HVAC, sewer line age)?", "missing", ["cslb"]),
         cell("The 0.9%-of-value assumption hides lumpy years", "assumption", ["cslb"]),
         cell("Commission an inspection; collect licensed-contractor bids for known items", "guidance", ["cslb"]),
         cell("Medium", "guidance", ["cslb"])],
        # Market
        [cell("Q18. What would Property A actually rent for at transfer time?", "missing", ["hud_fmr"]),
         cell("The $7,000/month figure is an estimate; the rental path lives or dies on it", "assumption", ["hud_fmr"]),
         cell("At the transfer window, pull three comparable listings and the HUD FMR for the county", "guidance", ["hud_fmr"]),
         cell("Medium", "guidance", ["hud_fmr"])],
        [cell("Q19. What appreciation/inflation scenario should the family plan on?", "missing", ["fhfa_hpi", "bls_cpi"]),
         cell("Scenarios (3.0% / 4.5% / 6.0% nominal) are assumptions, not forecasts", "assumption", ["fhfa_hpi"]),
         cell("Review FHFA HPI metro trends and BLS CPI near the transfer; re-run the what-if controls", "guidance", ["fhfa_hpi", "bls_cpi"]),
         cell("Medium", "guidance", ["fhfa_hpi"])],
        # Law
        [cell("Q20. Has Proposition 19 been amended, repealed, or replaced by the transfer window?", "missing", ["sos_ballot", "boe_pub801"]),
         cell("A repeal initiative has circulated; the exclusion amount also re-adjusts every two years", "guidance", ["boe_lta25009", "sos_ballot"]),
         cell("Check the Secretary of State and BOE letter pages at each annual review", "guidance", ["sos_ballot"]),
         cell("High", "guidance", ["sos_ballot"])],
        [cell("Q21. What is the exact Cupertino tax-rate area for Property A?", "missing", ["scc_ratebook"]),
         cell("The 1.17% ad-valorem assumption needs the parcel's rate area from the tax bill", "derived", ["scc_ratebook"]),
         cell("Read the rate from the county tax bill or the Tax Rate Book and update the model", "guidance", ["scc_ratebook"]),
         cell("Medium", "guidance", ["scc_ratebook"])],
        [cell("Q22. Will the Heir be a California resident when selling (if ever)?", "missing", ["rtc_18662"]),
         cell("Nonresident sales carry California withholding and different planning", "guidance", ["rtc_18662"]),
         cell("Confirm residency with the CPA in the sale year", "guidance", ["rtc_18662"]),
         cell("Low", "guidance", ["rtc_18662"])],
        [cell("Q23. Does the family want earthquake coverage for either property?", "missing", ["cdi_residential"]),
         cell("Standard policies exclude earthquake; premiums are material and decisions differ per property", "assumption", ["cdi_residential"]),
         cell("Price a CEA or private policy for both properties separately", "guidance", ["cdi_residential"]),
         cell("Low", "guidance", ["cdi_residential"])],
        [cell("Q24. Who is the successor trustee and is a professional fiduciary desired?", "missing", ["probate_16061_7"]),
         cell("A 2040-2050 transfer may need continuity planning for the trustee role", "guidance", ["probate_16061_7"]),
         cell("Confirm succession names and alternates with counsel", "guidance", ["probate_16061_7"]),
         cell("Medium", "guidance", ["probate_16061_7"])],
    ]
    body = (
        callout("How to use this register", "Each row is a question the family cannot answer from public sources. The third column states how to discover the answer; nothing here can be filled by inference. When a row is answered, update the private model, re-run the what-if controls, and re-check whether the path ranking still holds.", "info")
        + make_table("Questions, information and answers required before a final decision", ["Question", "Why it matters", "Suggested way to discover the answer", "Impact on the decision"], rows)
        + prose(
            "Suggestion for discovery in bulk",
            "Assemble a private document vault (never in this public repository) containing: the trust and amendments; two years of tax bills; two years of utility statements and the solar interconnection agreement; insurance declarations pages; a title report for Property A; the estate inventory list; Forms 709 history; and written quotes for owner-occupied, landlord and earthquake coverage. Most rows above resolve from that single collection effort, and the model can then be finalized in one sitting.",
        )
    )
    return render_page("pages/questions.html", "Questions & missing evidence", intro="The explicit list of questions, information and answers that must be resolved before any decision is final — with a suggested discovery step for each and a blank means unknown, not zero.", body=body, eyebrow="DECIDE")


def suggestion_table() -> str:
    items = [
        ("S01", "Publish the decision-matrix numbers with ranges as well as point values", "Point values read as false precision", "Clearer family debate", "Low", "Low"),
        ("S02", "Add an annual data-refresh checklist page (BOE letters, IRS IR pages, CDI bulletins)", "Sources age quickly", "Keeps the site trustworthy", "Medium", "Low"),
        ("S03", "Add a Monte-Carlo mode to the stress tool (randomized crash timing)", "Single historical paths understate uncertainty", "Better reinvestment-risk intuition", "Medium", "Medium"),
        ("S04", "Model the Property B third-unit rental scenario explicitly", "The occupancy decision changes Property B's income", "Complete mixed-path analysis", "Low", "Low"),
        ("S05", "Add a trust-allocation stress row (non-pro-rata sibling case)", "The exclusion can die on allocation choices", "Prevents an avoidable reassessment", "Medium", "Low"),
        ("S06", "Write the private document-vault checklist as a fill-in page (no data, structure only)", "Discovery is currently prose-only", "Faster evidence gathering", "Low", "Low"),
        ("S07", "Add CSV export buttons for the projection tables", "Rebuilding the model elsewhere is manual today", "Reproducibility for the CPA", "Medium", "Low"),
        ("S08", "Track Proposition 19 exclusion amounts across LTA letters in a small table", "The cap re-adjusts every two years", "Fewer stale assumptions", "Low", "Low"),
        ("S09", "Add an earthquake-insurance line item to both cost models", "Currently excluded from carrying costs", "Honest carrying-cost totals", "Low", "Low"),
        ("S10", "Compose a letter template to the attorney/CPA listing the open questions", "Advisers need the questions, not conclusions", "Faster professional review", "Low", "Low"),
        ("S11", "Add a decade-by-decade law-change log (what changed and when)", "50-year horizon implies many law changes", "Auditable history of assumptions", "Medium", "Low"),
        ("S12", "Add a printable one-page family decision record (choices made and why)", "Decisions get re-litigated every few years", "Continuity across sessions", "Low", "Low"),
        ("S13", "Owner instruction (24-36 month Treasury staging): model both 24 and 36 month lengths side by side — implemented in the black-swan tables this session", "Requested explicitly", "Direct comparison", "Done", "Low"),
    ]
    rows = [
        [
            cell(item_id, "guidance", ["page:suggestions.html"]),
            cell(suggestion, "guidance", ["page:suggestions.html"]),
            cell(problem, "guidance", ["page:suggestions.html"]),
            cell(benefit, "guidance", ["page:suggestions.html"]),
            cell(effort, "guidance", ["page:suggestions.html"]),
            cell(risk, "guidance", ["page:suggestions.html"]),
            cell('<select class="review-choice" data-id="' + item_id + '" aria-label="Review choice for ' + item_id + '">'
                 + '<option>Not reviewed</option><option>Investigate</option><option>Selected for testing</option><option>Defer</option>'
                 + "</select>", "guidance", ["page:suggestions.html"]),
        ]
        for item_id, suggestion, problem, benefit, effort, risk in items
    ]
    return make_table(
        "Suggestions awaiting review (choices stay in this browser; nothing is submitted)",
        ["ID", "Suggestion", "Problem it solves", "Decision benefit", "Effort", "Risk", "Review choice"],
        rows,
    )


def build_suggestions() -> str:
    body = (
        callout("Review before implementing", "These are proposed improvements from the analysis sessions. A reviewer should select Investigate / Selected for testing / Defer per row, record the chosen best path in COORDINATION.md, and only then schedule implementation. Choices are saved locally in this browser only; the site sends nothing anywhere.", "warning")
        + suggestion_table()
        + f'<p class="review-summary" id="review-summary" aria-live="polite"></p>'
        + '<section class="tool-section"><h2>Apply the reviewed choices</h2><div class="tool-actions">'
        + '<button type="button" id="reset-reviews">Reset all review choices</button>'
        + '<span class="tool-assumption">Resetting clears only this browser\'s stored choices. No server, no analytics, no network.</span>'
        + "</div></section>"
        + prose(
            "How to choose the best path before implementing changes",
            "For each suggestion: (1) restate the decision it changes; (2) check whether any page's conclusion would flip if the suggestion were implemented; (3) mark Investigate if the flip is plausible, Selected for testing if a session should prototype it, Defer if it is cosmetic; (4) log the decision with the session ID in COORDINATION.md so parallel sessions do not duplicate the work.",
        )
    )
    return render_page("pages/suggestions.html", "Suggestions for review", intro="A dedicated review queue: proposed site and analysis improvements with effort, risk and a local-only review control, so the best path is chosen before any change is implemented.", body=body, eyebrow="DECIDE")


PROJECTION_YEARS = (2026, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2065, 2070, 2075)


def build_projections() -> str:
    t = TRANSFER_YEAR_BASE
    value_rows = []
    for year in PROJECTION_YEARS:
        values = [fmv_at(year, growth=SCENARIOS[s]) for s in ("Low", "Base", "High")]
        value_rows.append([
            cell(str(year), "guidance", ["fhfa_hpi"]),
            cell(money(values[0]), "model", ["fhfa_hpi"]),
            cell(money(values[1]), "model", ["fhfa_hpi"]),
            cell(money(values[2]), "model", ["fhfa_hpi"]),
            cell(money(factored_base_at(year)), "derived", ["const_13a"]),
            cell(money(cap_at(year)), "assumption", ["boe_lta25009"]),
        ])
    tax_rows = []
    for year in PROJECTION_YEARS:
        tax_rows.append([
            cell(str(year), "guidance", ["scc_ratebook"]),
            cell(money(A_TAX_2025 * (1.02 ** (year - 2026))) + " (if no transfer had occurred)", "derived", ["const_13a"]),
            cell(money(tax_occupied(year)), "model", ["rtc_63_2", "scc_ratebook"]),
            cell(money(tax_reassessed(year)), "model", ["rtc_63_2", "scc_ratebook"]),
            cell(money(tax_reassessed(year) - tax_occupied(year)), "model", ["rtc_63_2"]),
        ])
    b_rows = []
    for year in PROJECTION_YEARS:
        cf = b_cashflow(year)
        b_rows.append([
            cell(str(year), "guidance", ["sf_treasurer"]),
            cell(money(fmv_at(year, base_value=B_VALUE)), "model", ["fhfa_hpi"]),
            cell(money(B_TAX_2025 * (1.02 ** (year - 2025)) + direct_at(year, DIRECT_B)), "derived", ["const_13a", "sf_treasurer"]),
            cell(money(cf["gross"]), "model", ["hud_fmr"]),
            cell(money(sum(cf["costs"].values())), "model", ["irs_p527", "cdi_residential"]),
            cell(signed_money(cf["net"]), "model", ["irs_p527"]),
        ])
    cost_rows = [
        [cell("A: water (owner range $100-$150/mo)", "owner", ["cpuc_sjw", "waterboards"]),
         cell(money(A_WATER_MONTH_LOW * 12) + " - " + money(A_WATER_MONTH_HIGH * 12) + " / yr (2026)", "owner", ["cpuc_sjw"]),
         cell(pct(UTILITIES_GROWTH, 1) + " per year assumed", "assumption", ["cpuc_sjw"]),
         cell(money(utilities_a_at(t) + (A_SOLAR_CREDIT_LOW + A_SOLAR_CREDIT_HIGH) / 2 * 12) + " water-only at year " + str(t), "model", ["cpuc_sjw"])],
        [cell("A: electricity (solar net credit)", "owner", ["cpuc_nem"]),
         cell("-" + money(A_SOLAR_CREDIT_LOW * 12) + " to -" + money(A_SOLAR_CREDIT_HIGH * 12) + " / yr (2026 credit)", "owner", ["cpuc_nem"]),
         cell("Tariff-dependent (NEM vs net billing)", "assumption", ["cpuc_nem"]),
         cell("Verify the interconnection agreement before relying on the credit", "guidance", ["cpuc_nem"])],
        [cell("A: insurance (owner guess, unverified)", "owner", ["cdi_residential"]),
         cell(money(A_INSURANCE_GUESS) + " / yr (2026)", "owner", ["cdi_residential"]),
         cell(pct(INSURANCE_GROWTH, 1) + " per year assumed", "assumption", ["cdi_residential"]),
         cell(money(insurance_at(t, A_INSURANCE_GUESS)) + " at year " + str(t), "model", ["cdi_residential"])],
        [cell("A: maintenance (share of value)", "assumption", ["cslb"]),
         cell(pct(MAINT_A, 1) + " of market value per year", "assumption", ["cslb"]),
         cell("Scales with the appreciation scenario", "assumption", ["fhfa_hpi"]),
         cell(money(MAINT_A * fmv_at(t)) + " at year " + str(t), "model", ["fhfa_hpi"])],
        [cell("B: water (owner range for 3 units)", "owner", ["sfpuc", "waterboards"]),
         cell(money(B_WATER_MONTH_LOW * 12) + " - " + money(B_WATER_MONTH_HIGH * 12) + " / yr (2026)", "owner", ["sfpuc"]),
         cell(pct(UTILITIES_GROWTH, 1) + " per year assumed", "assumption", ["sfpuc"]),
         cell(money(B_WATER_MONTH_HIGH * 12 * (1 + UTILITIES_GROWTH) ** (t - 2026)) + " (upper bound) at year " + str(t), "model", ["sfpuc"])],
        [cell("B: electricity (owner range)", "owner", ["cpuc_nem"]),
         cell(money(B_ELEC_MONTH_LOW * 12) + " - " + money(B_ELEC_MONTH_HIGH * 12) + " / yr (2026)", "owner", ["cpuc_nem"]),
         cell(pct(UTILITIES_GROWTH, 1) + " per year assumed", "assumption", ["cpuc_nem"]),
         cell("Master-metered building; confirm unit allocation with tenants", "guidance", ["cpuc_nem"])],
        [cell("B: insurance (owner guess, unverified)", "owner", ["cdi_residential"]),
         cell(money(B_INSURANCE_GUESS) + " / yr (2026)", "owner", ["cdi_residential"]),
         cell(pct(INSURANCE_GROWTH, 1) + " per year assumed", "assumption", ["cdi_residential"]),
         cell(money(insurance_at(t, B_INSURANCE_GUESS)) + " at year " + str(t), "model", ["cdi_residential"])],
        [cell("B: maintenance (share of value)", "assumption", ["cslb"]),
         cell(pct(MAINT_B, 1) + " of market value per year", "assumption", ["cslb"]),
         cell("Owner reports heavier upkeep than A", "owner", ["cslb"]),
         cell(money(MAINT_B * fmv_at(t, base_value=B_VALUE)) + " at year " + str(t), "model", ["fhfa_hpi"])],
    ]
    body = (
        callout("What this worksheet is", "Transparent scenario projections, not forecasts: market value under three appreciation scenarios, the two property-tax regimes after transfer, Property B's cash flow, and the cost lines with growth assumptions. Every assumption is adjustable in the what-if controls; change one and re-read the ranking on the decision page.", "info")
        + make_table("Property A — market value scenarios and Prop 19 values by year (rounded to $10)", ["Year", "Low 3.0%/yr", "Base 4.5%/yr", "High 6.0%/yr", "Factored Prop 13 base", "Exclusion cap (projected)"], value_rows)
        + make_table("Property A — annual property tax under the three regimes", ["Year", "Current base grown 2% (no transfer)", "Occupied under §63.2", "Fully reassessed (rented/vacant)", "Reassessment penalty per year"], tax_rows)
        + make_table("Property B — value, tax, rent and net cash flow (base case)", ["Year", "Market value", "Property tax", "Gross rent", "Operating costs", "Net cash flow"], b_rows)
        + make_table("Cost lines with growth assumptions", ["Line", "2026 value (rounded)", "Growth assumption", "Value at year " + str(t)], cost_rows)
        + f"""<section class="tool-section"><h2>What-if controls (local-only)</h2>
<form id="projection-tool" novalidate>
<div class="tool-grid">
<label>Year <input id="p-year" type="number" min="2026" max="2075" step="1" value="2045"></label>
<label>Appreciation %/yr <input id="p-growth" type="number" min="2" max="7" step="0.5" value="4.5"></label>
<label>Inflation %/yr <input id="p-infl" type="number" min="1" max="5" step="0.25" value="2.5"></label>
</div>
<div class="tool-actions"><button type="button" id="p-reset">Reset</button>
<span class="tool-assumption">Rounded to the nearest $10; assumptions are not forecasts.</span></div>
</form>
<div class="table-scroll" tabindex="0" aria-label="Projection what-if results"><table id="p-results"><caption>Projection what-if results (recomputed locally)</caption><thead><tr><th scope="col">Quantity</th><th scope="col">Value</th><th scope="col">Evidence status</th><th scope="col">Scope note</th></tr></thead><tbody>
<tr><td>Market value at year</td><td id="p-out-fmv">—</td><td><span class="badge model">Model</span></td><td><a class="source" href="https://www.fhfa.gov/data/hpi/summary-tables" rel="noopener noreferrer">FHFA HPI — anchor</a></td></tr>
<tr><td>Factored Prop 13 base at year</td><td id="p-out-base">—</td><td><span class="badge derived">Derived</span></td><td><a class="source" href="https://leginfo.legislature.ca.gov/faces/codes_displayArticle.xhtml?lawCode=CONS&amp;division=&amp;articleNum=XIIIA" rel="noopener noreferrer">California Constitution Article XIII A</a></td></tr>
<tr><td>Tax if occupied at year</td><td id="p-out-taxocc">—</td><td><span class="badge model">Model</span></td><td><a class="source" href="https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&amp;sectionNum=63.2." rel="noopener noreferrer">California Revenue and Taxation Code §63.2</a></td></tr>
<tr><td>Tax if reassessed at year</td><td id="p-out-taxre">—</td><td><span class="badge model">Model</span></td><td><a class="source" href="https://files.santaclaracounty.gov/exjcpb1531/2025-11/tax-rate-book-2025-2026.pdf?VersionId=HHMZ1VmGwFXqVvpM36xuptkIcV2V8ctE" rel="noopener noreferrer">Santa Clara County Tax Rate Book 2025-2026</a></td></tr>
</tbody></table></div>
</section>"""
        + prose(
            "Reinvestment risk beside the projections",
            "Property A's value scenarios describe one asset in one place; the Path C portfolio alternative distributes the same capital across securities with their own sequence risk. The two risk profiles are not comparable point-to-point, which is why the black-swan page tests entries with real 1928-2025 annual returns instead of asserting an average.",
        )
    )
    return render_page("pages/projections.html", "Projection worksheet", intro="Year-by-year projections for both properties — market value scenarios, assessed values, property-tax regimes, rent and operating costs — every figure rounded to $10 with assumptions named.", body=body, eyebrow="NUMBERS")


def build_property_tax() -> str:
    a_history = [
        ("2026", None, 550_540), ("2025", 7_210, 539_740), ("2024", 7_000, 529_160),
        ("2023", 6_920, 518_790), ("2022", 6_760, 508_610), ("2021", 6_660, 498_640),
        ("2020", 6_570, 493_530), ("2019", 6_570, 483_850), ("2018", 6_380, 474_370),
        ("2017", 6_380, 465_070), ("2016", 6_410, 455_950), ("2015", 6_130, 449_100),
        ("2014", 5_970, 440_300),
    ]
    b_history = [
        ("2025", 2_440, 114_250), ("2024", 2_320, 112_010), ("2023", 2_180, 109_810),
        ("2022", 2_110, 107_660), ("2021", 2_070, 105_600), ("2020", 2_200, 104_510),
        ("2019", 2_130, 102_470), ("2018", 2_060, 100_460), ("2017", 1_740, 98_490),
        ("2016", 1_680, 96_560),
    ]
    a_rows = [
        [cell(year, "guidance", ["scc_assessor_root"]),
         cell(money(tax) if tax is not None else "", "owner", ["scc_assessor_root"]),
         cell(money(base), "owner", ["scc_assessor_root"])]
        for year, tax, base in a_history
    ]
    b_rows = [
        [cell(year, "guidance", ["sf_assessor_root"]),
         cell(money(tax), "owner", ["sf_treasurer"]),
         cell(money(base), "owner", ["sf_assessor_root"])]
        for year, tax, base in b_history
    ]
    rules_rows = [
        [cell("Proposition 13 base levy and 2% cap", "verified", ["const_13a"]),
         cell("1% ad valorem base; assessed value rises at most 2%/yr absent sale or new construction", "verified", ["const_13a"])],
        [cell("Prop 19 family-home exclusion", "verified", ["rtc_63_2", "boe_pub801"]),
         cell("Transfers on/after February 16, 2021: the family home is excluded only if the transferee occupies it as a principal residence within one year and files the homeowners' or veterans' exemption within one year", "verified", ["rtc_63_2"])],
        [cell("Value limit under §63.2", "verified", ["boe_lta25009"]),
         cell("New base = factored base + lesser of the exclusion amount or the excess of market value; $1,044,586 for transfers from February 16, 2025 through February 15, 2027, re-adjusted every two years", "verified", ["boe_lta25009"])],
        [cell("Claim deadlines", "verified", ["boe_pub801", "scc_assessor_transfer"]),
         cell("BOE-19-P claim within three years of the transfer for full relief; homeowners' exemption (BOE-266) within one year; late exemption filing yields prospective-only relief", "verified", ["boe_pub801"])],
        [cell("Exclusion removal on move-out", "verified", ["rtc_63_2"]),
         cell("When the eligible transferee no longer qualifies, the exclusion is removed and, from the next lien date, the base year value established as of the change-in-ownership date, adjusted annually, is enrolled", "verified", ["rtc_63_2"])],
        [cell("Prior law (§63.1)", "verified", ["rtc_63_1"]),
         cell("Before February 16, 2021 the parent-child exclusion had no occupancy test and covered the first $1,000,000 of other property too; those rules no longer apply to a future transfer", "verified", ["rtc_63_1"])],
        [cell("Homeowners' exemption", "verified", ["rtc_218"]),
         cell("$7,000 of full value for an owner-occupied principal residence; does not extend to rented or vacant property — relevant to the occupancy test", "verified", ["rtc_218"])],
        [cell("Revocable trust timing", "verified", ["boe_annot_625"]),
         cell("Change in ownership occurs when the trust becomes irrevocable (at death), not when a deed is recorded", "verified", ["boe_annot_625"])],
        [cell("Change-in-ownership statement after death", "verified", ["rtc_480"]),
         cell("The trustee files the statement with the recorder/assessor within 150 days after the date of death; the recorder's $20 fee applies without a preliminary report", "verified", ["rtc_480", "rtc_480_3"])],
        [cell("Santa Clara County rate structure", "derived", ["scc_ratebook"]),
         cell("Ad-valorem composite for Cupertino assumed at 1.17% pending confirmation of the parcel's rate area; fixed direct assessments derived as the residual of the owner's 2025 bill (about " + money(DIRECT_A) + ")", "derived", ["scc_ratebook"])],
        [cell("San Francisco rate structure", "verified", ["sf_treasurer"]),
         cell("FY 2025-26 secured ad-valorem rate is 1.18268325%; Property B's fixed assessments derived as a residual of about " + money(DIRECT_B), "derived", ["sf_treasurer"])],
        [cell("Nonresident withholding", "verified", ["rtc_18662"]),
         cell("If a nonresident heir ever sells, California withholding applies to the dispositions (confirm the current rate with the FTB)", "verified", ["rtc_18662"])],
    ]
    body = (
        callout("Why the histories are rounded", "Assessment and tax histories identify parcels online almost exactly. Per the owner's privacy instruction, every figure below is rounded to the nearest $10 and no postal code or address is published; the rounded tables preserve the structure for analysis without an exact fingerprint. Unrounded values remain in private records only.", "warning")
        + make_table("Property A — Cupertino area (Santa Clara County): owner-provided history, rounded to $10", ["Year", "Property tax", "Tax assessment"], a_rows)
        + make_table("Property B — San Francisco Outer Sunset (San Francisco County): owner-provided history, rounded to $10", ["Year", "Property tax", "Tax assessment"], b_rows)
        + make_table("Property-tax rules that decide the outcome", ["Rule", "What it says"], rules_rows)
        + prose(
            "The derived rates, honestly",
            "The owner's 2025 bills imply effective rates of roughly 1.34% (Property A) and 2.14% (Property B) against rounded assessed values. Those include fixed per-parcel assessments that do not scale with value, so a reassessment does not multiply them. The model therefore taxes a reassessed property at the ad-valorem rate only (1.17% assumed for Cupertino; 1.18268325% official for San Francisco) and carries fixed assessments forward at inflation. Confirm the Cupertino rate area from the parcel's tax bill or the county Tax Rate Book.",
        )
    )
    return render_page("pages/property-tax.html", "Property-tax rules", intro="Proposition 13 and Proposition 19 mechanics with statutory deadlines, plus the owner-provided assessment histories rounded to $10, and the derived rate structure behind the model.", body=body, eyebrow="NUMBERS")


def build_costs() -> str:
    rn = rental_net(TRANSFER_YEAR_BASE)
    occ = carrying_occupied(TRANSFER_YEAR_BASE)
    cf_b = b_cashflow(2026)
    rows_a = [
        [cell("Water", "owner", ["cpuc_sjw", "waterboards"]),
         cell(money(A_WATER_MONTH_LOW) + " - " + money(A_WATER_MONTH_HIGH) + " / mo", "owner", ["cpuc_sjw"]),
         cell("Investor-owned utility rate case shows average residential bills in the low-to-mid $100s per month", "verified", ["cpuc_sjw"])],
        [cell("Electricity (solar)", "owner", ["cpuc_nem"]),
         cell("net credit of " + money(A_SOLAR_CREDIT_LOW) + " - " + money(A_SOLAR_CREDIT_HIGH) + " / mo", "owner", ["cpuc_nem"]),
         cell("Compensation depends on the applicable NEM or net-billing tariff and interconnection date", "verified", ["cpuc_nem"])],
        [cell("Homeowners insurance", "missing", ["cdi_residential"]),
         cell("", "owner", ["cdi_residential"]),
         cell("Owner's $1,500 guess is unverified; a high-value Bay Area dwelling often quotes higher, and FAIR-Plan-plus-DIC stacks cost more; obtain quotes", "guidance", ["cdi_residential", "cafairplan"])],
        [cell("Maintenance and repairs", "assumption", ["cslb"]),
         cell(pct(MAINT_A, 1) + " of market value per year", "assumption", ["cslb"]),
         cell("Owner reports lighter upkeep than Property B; verify with an inspection", "owner", ["cslb"])],
    ]
    rows_b = [
        [cell("Gross rent (two rented units)", "owner", ["hud_fmr", "irs_p527"]),
         cell(money(B_RENT_MONTH) + " / mo", "owner", ["hud_fmr"]),
         cell("HUD FMRs are 40th-percentile benchmarks and sit below the owner's achieved rent; leases govern", "verified", ["hud_fmr"])],
        [cell("Water (all three units)", "owner", ["sfpuc", "waterboards"]),
         cell(money(B_WATER_MONTH_LOW) + " - " + money(B_WATER_MONTH_HIGH) + " / mo", "owner", ["sfpuc"]),
         cell("Confirm allocation and any tenant reimbursement in the leases", "guidance", ["sfpuc"])],
        [cell("Electricity", "owner", ["cpuc_nem"]),
         cell(money(B_ELEC_MONTH_LOW) + " - " + money(B_ELEC_MONTH_HIGH) + " / mo", "owner", ["cpuc_nem"]),
         cell("Master-metered; verify how tenants are charged", "guidance", ["cpuc_nem"])],
        [cell("Landlord (dwelling) insurance", "missing", ["cdi_residential"]),
         cell("", "owner", ["cdi_residential"]),
         cell("Owner's $1,500 guess is unverified for a triplex; obtain a landlord quote including lost-rent cover", "guidance", ["cdi_residential"])],
        [cell("Vacancy and management allowance", "assumption", ["irs_p527"]),
         cell(pct(VACANCY_MGMT, 0) + " of gross rent", "assumption", ["irs_p527"]),
         cell("Adjust in the private model if self-managed", "guidance", ["irs_p527"])],
    ]
    body = (
        callout("Owner-provided vs verified", "The operating numbers below come from the owner's records (rounded to $10) except where an official source establishes the framework. Nothing here is a quote: insurance rows are blank until written quotes exist, and blank means unknown, not zero.", "info")
        + make_table("Property A — Cupertino area operating costs", ["Line", "Owner figure (2026)", "Verification status and context"], rows_a)
        + make_table("Property B — San Francisco Outer Sunset operating costs", ["Line", "Owner figure (2026)", "Verification status and context"], rows_b)
        + make_table("Derived annual positions (base case, year " + str(TRANSFER_YEAR_BASE) + " for A, 2026 for B)", ["Position", "Value", "Evidence status", "Scope note"], [
            [cell("Property A carrying cost while occupied", "model", ["scc_ratebook"]),
             cell(money(sum(occ.values())) + " / yr", "model", ["scc_ratebook", "cdi_residential"]),
             cell("Tax + insurance + maintenance + net utilities", "guidance", ["rtc_63_2"])],
            [cell("Property A rental net if rented (reassessed)", "model", ["irs_p527"]),
             cell(signed_money(rn["net"]) + " / yr", "model", ["hud_fmr", "scc_ratebook"]),
             cell("Gross " + money(rn["gross"]) + " minus tax, insurance, maintenance, utilities and vacancy/management", "guidance", ["irs_p527"])],
            [cell("Property B net operating cash flow", "model", ["irs_p527"]),
             cell(signed_money(cf_b["net"]) + " / yr", "model", ["irs_p527"]),
             cell("Insurance unverified; sensitivity shown on the projections page", "guidance", ["cdi_residential"])],
        ])
        + prose(
            "Insurance research note",
            "The California Department of Insurance regulates residential coverage and maintains consumer tools; the FAIR Plan is the residual fire market with limited perils. Industry averages and regional ranges are published by non-official aggregators and are deliberately not table-verified here: they would violate the source rule and they move too fast. The actionable step is three written quotes per property (admitted-market, high-net-worth carrier, FAIR-Plan-plus-DIC) collected into the private vault.",
        )
    )
    return render_page("pages/operating-costs.html", "Costs & coverage", intro="Water, electricity, solar credits, insurance and maintenance for both properties — owner figures rounded to $10, official context linked, unknowns left blank.", body=body, eyebrow="NUMBERS")


def crash_row(entry: int) -> list[str]:
    horizons = []
    seen = set()
    for offset in (5, 10, 20):
        year = min(entry + offset, 2025)
        if year not in seen:
            seen.add(year)
            horizons.append((entry, year))
    rows = []
    for start, horizon in horizons:
        for key, name in STRATEGY_LABELS:
            w = strategy_wealth(start, horizon, key)
            rows.append([
                cell(str(start) + " entry through " + str(horizon), "guidance", ["fedhist_1929" if start == 1929 else ("fedhist_recession" if start == 2008 else "damodaran")]),
                cell(name, "guidance", ["damodaran", "treasury_bills"]),
                cell(f"{w:.2f}x", "secondary", ["damodaran"]),
            ])
    return rows


def build_black_swan() -> str:
    scenario_rows = [
        [cell("1929-1932 crash", "verified", ["fedhist_1929"]),
         cell("Dow fell 89% from the September 1929 peak (381.17) to the July 1932 trough (41.22); the 1929 high was not regained until November 1954", "verified", ["fedhist_1929"]),
         cell("S&P 500 total returns: 1929 -8.30%, 1930 -25.12%, 1931 -43.84%, 1932 -8.64%, then +49.98% in 1933", "secondary", ["damodaran"])],
        [cell("1973-1974 stagflation bear", "secondary", ["damodaran", "fedhist_depression"]),
         cell("Two consecutive down years (-14.31%, -25.90%) while average T-bill rates ran 7.04% then 7.85%", "secondary", ["damodaran"]),
         cell("Inflation eroded cash parking; a 50-year plan cannot assume bonds always hedge equities", "guidance", ["damodaran"])],
        [cell("2000-2002 dot-com bear", "secondary", ["damodaran"]),
         cell("Annual total returns of -9.03%, -11.85%, -21.97% before the 2003 rebound; the decade also ended in the 2008 crash", "secondary", ["damodaran"]),
         cell("Sequence risk stacks: a 2000 entry faced a second crash in 2008", "guidance", ["damodaran"])],
        [cell("2007-2009 financial crisis", "verified", ["fedhist_recession"]),
         cell("U.S. average home prices fell over a fifth from Q1 2007 to Q2 2011 (FHFA HPI); 2008 S&P total return -36.55% with a 25.94% rebound in 2009", "verified", ["fedhist_recession", "damodaran"]),
         cell("Housing and equities fell together; property-heavy paths were not a hedge", "guidance", ["fedhist_recession"])],
        [cell("2020 pandemic crash", "secondary", ["damodaran"]),
         cell("A -34% drawdown in weeks followed by the fastest recovery in the modern record; full-year 2020 return was +18.02%", "secondary", ["damodaran"]),
         cell("Fast recoveries punish parking: the stress table below shows the cost", "guidance", ["damodaran"])],
        [cell("2022 rate-shock year", "secondary", ["damodaran"]),
         cell("S&P total return -18.04% while average T-bill rates reached 2.09% and cash was finally competitive again", "secondary", ["damodaran"]),
         cell("Parking yield matters as much as parking length", "guidance", ["cbo_rates"])],
    ]
    stress_rows = crash_row(1929) + crash_row(2000) + crash_row(2008) + crash_row(2020)
    body = (
        callout("Why a separate black-swan section", "A 2040-2050 transfer followed by a 30-plus-year horizon crosses many regimes: growth and inflation are never consistent for 50 years. This section uses verified historical observations (Federal Reserve History) and a transcribed 1928-2025 annual-return series (NYU Stern compilation, flagged secondary) to stress-test how each path behaves from a crash-time entry, instead of assuming an average year.", "warning")
        + make_table("Historical regimes and verified anchors", ["Regime", "What happened", "Return detail used in the stress tables"], scenario_rows)
        + make_table("Stress table: ending value with entry capital normalized to 1.00 (annual granularity; real historical returns)", ["Entry and horizon", "Strategy", "Ending value"], stress_rows)
        + prose(
            "What the stress table shows",
            "The table computes each strategy from the actual annual record. Ratios below are staged-versus-lump ending wealth. Parking 24 months in Treasuries and then phasing comes out "
            + f"{strategy_wealth(1929, 1939, 'park24_dca24') / strategy_wealth(1929, 1939, 'lump'):.2f}x from a 1929 entry, "
            + f"{strategy_wealth(2000, 2010, 'park24_dca24') / strategy_wealth(2000, 2010, 'lump'):.2f}x from a 2000 entry, "
            + f"{strategy_wealth(2008, 2018, 'park24_dca24') / strategy_wealth(2008, 2018, 'lump'):.2f}x from a 2008 entry, and "
            + f"{strategy_wealth(2020, 2025, 'park24_dca24') / strategy_wealth(2020, 2025, 'lump'):.2f}x in the fast 2020 recovery. "
            + "Dollar-cost averaging without parking sits between the two. No one can know in advance which regime the transfer lands in; the phased path is insurance whose premium is the upside missed in V-shaped recoveries.",
        )
        + prose(
            "Reinvestment risk, quantified",
            "The Treasury-parking plan has two tails: yields can fall while parked (reinvestment risk — the parked money returns less than the yield it was bought at), and equities can run away before the phase-in completes (timing cost). The 1928-2025 record contains both. The phased-investing page explains the mechanics and the Treasury state-tax exemption that matters for a California heir.",
        )
        + prose(
            "Model limits",
            "Annual granularity ignores intra-year sequencing; the T-bill column proxies the 3M-2Y Treasury ladder; dividends are included in the S&P total-return series; no taxes or transaction costs are modeled. The series is a secondary academic compilation — verify headline years against primary market data before acting. The interactive stress tool below recomputes everything locally from the same series.",
        )
        + f"""<section class="tool-section"><h2>Interactive stress tool (local-only, nothing stored)</h2>
<form id="bs-tool" novalidate>
<div class="tool-grid">
<label>Entry year <select id="bs-entry"><option value="1929">1929 (Great Depression)</option><option value="1973">1973 (stagflation bear)</option><option value="2000">2000 (dot-com bear)</option><option value="2008">2008 (financial crisis)</option><option value="2020">2020 (pandemic crash)</option><option value="2022">2022 (rate shock)</option></select></label>
<label>Horizon (years after entry) <input id="bs-horizon" type="number" min="3" max="30" step="1" value="10"></label>
<label>Staging months before first buy <input id="bs-park" type="number" min="0" max="60" step="6" value="24"></label>
<label>Phase-in months after parking <input id="bs-dca" type="number" min="1" max="60" step="6" value="24"></label>
</div>
<div class="tool-actions"><button type="button" id="bs-run">Recompute</button>
<span class="tool-assumption">Annual returns from the transcribed 1928-2025 series; entry capital normalized to 1.00; no taxes or costs.</span></div>
</form>
<div class="table-scroll" tabindex="0" aria-label="Stress tool results"><table id="bs-results"><caption>Stress tool results (recomputed locally)</caption><thead><tr><th scope="col">Strategy</th><th scope="col">Ending value (1.00 = entry capital)</th><th scope="col">Evidence status</th><th scope="col">Scope note</th></tr></thead><tbody>
<tr><td>Lump sum at entry</td><td id="bs-out-lump">—</td><td><span class="badge secondary">Secondary</span></td><td><a class="source" href="https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html" rel="noopener noreferrer">NYU Stern — historical returns 1928-2025</a></td></tr>
<tr><td>Park then phase as configured</td><td id="bs-out-parked">—</td><td><span class="badge secondary">Secondary</span></td><td><a class="source" href="https://www.treasurydirect.gov/marketable-securities/treasury-bills/" rel="noopener noreferrer">TreasuryDirect — Treasury bills</a></td></tr>
<tr><td>Phase immediately (no parking)</td><td id="bs-out-dca">—</td><td><span class="badge secondary">Secondary</span></td><td><a class="source" href="https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks" rel="noopener noreferrer">SEC Investor.gov — Stocks</a></td></tr>
</tbody></table></div>
</section>"""
        + prose(
            "Synthetic-path tool retained",
            "The Treasury staging tool on the next page keeps the earlier synthetic drawdown-path simulator for custom shapes (depth, trough length, yields) beyond the historical record — useful for hypothetical regimes, clearly labeled synthetic, never persisted.",
        )
    )
    return render_page("pages/black-swan.html", "Black-swan conditions", intro="Verified crash history, a 1928-2025 annual-return stress table for every entry strategy including the 24-36 month Treasury parking plan, and a local-only interactive stress tool.", body=body, eyebrow="STRESS TESTS")


def build_phased_investing() -> str:
    t = TRANSFER_YEAR_BASE
    proceeds = sale_proceeds(t)
    p24 = strategy_wealth(2008, 2018, "park24_dca24")
    lump08 = strategy_wealth(2008, 2018, "lump")
    body = (
        callout("The requested path, formalized", "Park sale proceeds in a 3-month to 2-year Treasury ladder for 24-36 months after the inheritance, then phase into equities. The stress table on the black-swan page prices this plan against real historical crash entries; this page explains the mechanics and the tradeoffs.", "info")
        + make_table("Mechanics of the staging plan", ["Element", "Detail"], [
            [cell("Instruments", "guidance", ["treasury_bills", "treasury_notes"]),
             cell("3-, 6-, 12-, 18- and 24-month bills and notes rolled at auction; rates fixed at purchase", "verified", ["treasury_bills"])],
            [cell("California tax advantage", "verified", ["treasury_bills"]),
             cell("Treasury interest is exempt from California state and local income tax while parked", "verified", ["treasury_bills"])],
            [cell("Window length", "assumption", ["damodaran"]),
             cell("24-36 months: long enough to span most post-1929/2008 troughs, short enough to matter in a fast recovery; the stress table shows both 24- and 36-month variants", "assumption", ["damodaran"])],
            [cell("Phase-in schedule", "assumption", ["investor_stocks"]),
             cell("Equal monthly purchases for 24-36 months after the window, or calendar-triggered thirds; both are equivalent on annual data", "assumption", ["investor_stocks"])],
            [cell("Reinvestment risk", "guidance", ["cbo_rates"]),
             cell("If yields fall during the window, parked proceeds re-invest at lower rates; if a fast recovery begins, the plan buys back higher; CBO rate scenarios anchor the expectation, not the outcome", "guidance", ["cbo_rates"])],
        ])
        + make_table("Illustration (base case, year " + str(t) + ")", ["Quantity", "Value", "Evidence status", "Scope note"], [
            [cell("Net proceeds parked", "model", ["fhfa_hpi"]),
             cell(money(proceeds), "model", ["fhfa_hpi"]),
             cell("After 6% selling costs; basis stepped to date-of-death value, so prompt sale has near-zero capital gain", "guidance", ["irs_p551", "irs_gifts_faq"])],
            [cell("Parked yield assumption", "assumption", ["cbo_rates", "treasury_bills"]),
             cell(pct(TREASURY_YIELD, 1) + " nominal", "assumption", ["cbo_rates"]),
             cell("Anchor from CBO 10-year rate scenarios; adjust to actual auction results at the time", "guidance", ["treasury_bills"])],
            [cell("Historical cost of parking (2020-style fast recovery)", "secondary", ["damodaran"]),
             cell(f"{p24 / lump08:.2f}x the lump-sum outcome by 2018 for staged entry after a 2008 crash (computed from the annual record; below 1.00 means parking cost upside, above 1.00 means it preserved it)", "secondary", ["damodaran"]),
             cell("The premium paid for crash insurance; the 1929 entry shows the reverse sign", "guidance", ["damodaran"])],
        ])
        + prose(
            "Decision rule of thumb",
            "Choose staging length by regime awareness, not prediction: the real-data table shows the phased path ahead for 1929- and 2000-shaped entries and near parity for 2008, while the fast 2020 recovery punished parking by roughly a quarter of the decade's outcome. The interactive stress tool on the black-swan page recomputes both variants locally; nothing is stored or sent anywhere.",
        )
        + f"""<section class="tool-section"><h2>Synthetic drawdown-path tool (local-only)</h2>
<form id="phase-tool" novalidate>
<div class="tool-grid">
<label>Regime <select id="phase-event"><option value="2008">2008-style (57% drawdown)</option><option value="1929">1929-style (89% drawdown)</option></select></label>
<label>Staging months <input id="phase-months" type="number" min="1" max="120" step="1" value="30"></label>
<label>Drawdown % <input id="phase-drawdown" type="number" min="0" max="99" step="1" value="57"></label>
<label>Months to trough <input id="phase-trough" type="number" min="1" max="120" step="1" value="17"></label>
<label>Pre-crash drift %/yr <input id="phase-drift" type="number" min="-20" max="30" step="1" value="0"></label>
<label>Treasury yield year 1 % <input id="phase-yield1" type="number" min="-5" max="20" step="0.5" value="0"></label>
<label>Treasury yield later % <input id="phase-yield2" type="number" min="-5" max="20" step="0.5" value="0"></label>
<label>Inflation %/yr <input id="phase-inflation" type="number" min="-5" max="20" step="0.5" value="0"></label>
</div>
<div class="tool-actions"><button type="button" id="phase-reset">Reset</button>
<span class="tool-assumption">Synthetic paths only — clearly not history and not a forecast. Starting capital is normalized to 100 units; no currency amounts are stored or sent.</span></div>
</form>
<div class="scenario-grid" style="margin:18px 0">
<div class="scenario-card"><h3>Early-crash entry</h3><p>Crash begins while staging is still underway.</p><dl>
<dt>Immediate (lump) value</dt><dd id="early-immediate-value">—</dd>
<dt>Staged value</dt><dd id="early-phased-value">—</dd>
<dt>Immediate real value</dt><dd id="early-immediate-real">—</dd>
<dt>Staged real value</dt><dd id="early-phased-real">—</dd>
<dt>Immediate worst drawdown</dt><dd id="early-immediate-dd">—</dd>
<dt>Staged worst drawdown</dt><dd id="early-phased-dd">—</dd>
</dl></div>
<div class="scenario-card"><h3>Late-crash entry</h3><p>Crash begins as staging completes.</p><dl>
<dt>Immediate (lump) value</dt><dd id="late-immediate-value">—</dd>
<dt>Staged value</dt><dd id="late-phased-value">—</dd>
<dt>Immediate real value</dt><dd id="late-immediate-real">—</dd>
<dt>Staged real value</dt><dd id="late-phased-real">—</dd>
<dt>Immediate worst drawdown</dt><dd id="late-immediate-dd">—</dd>
<dt>Staged worst drawdown</dt><dd id="late-phased-dd">—</dd>
</dl></div>
</div>
<p class="tool-status" id="phase-status" aria-live="polite"></p>
</section>"""
        + prose(
            "What this tool is not",
            "It is a stress illustration, not a historical backtest, not a forecast, and not investment advice. It exists so the family can feel how staging changes drawdowns under hypothetical regimes, then verify the conclusion against the real-data tables on the black-swan page.",
        )
    )
    return render_page("pages/phased-investing.html", "Treasury staging tool", intro="The 24-36 month 3M-2Y Treasury parking plan: mechanics, the California state-tax advantage, honest pricing of its reinvestment risk, and a local-only synthetic-path simulator.", body=body, eyebrow="STRESS TESTS")


def build_estate_thresholds() -> str:
    exempt_2045 = 15_000_000 * (1 + INFLATION) ** 19
    body = (
        callout("Federal law, current", "Public Law 119-21 (July 4, 2025) set the basic exclusion amount at $15,000,000 per person for 2026 and indexed it after 2026; the IRS confirmed $15,480,000 for 2027. The annual gift exclusion is $19,000 in 2026 and $20,000 in 2027. The top estate and gift rate above the exclusion is 40%. A married couple can reach $30,000,000 combined with a timely portability election on Form 706.", "info")
        + make_table("Federal estate and gift tax thresholds", ["Item", "2026", "2027", "Source"], [
            [cell("Basic exclusion amount (per person)", "verified", ["congress_hr1", "irs_whatsnew"]),
             cell("$15,000,000", "verified", ["irs_whatsnew"]),
             cell("$15,480,000", "verified", ["irs_2027"]),
             cell("Primary source", "verified", ["irs_whatsnew", "irs_2027"])],
            [cell("Annual gift exclusion (per recipient)", "verified", ["irs_gift_faq", "irs_2027"]),
             cell("$19,000", "verified", ["irs_gift_faq"]),
             cell("$20,000", "verified", ["irs_2027"]),
             cell("Primary source", "verified", ["irs_2027"])],
            [cell("Gifts to a non-citizen spouse (annual exclusion)", "verified", ["irs_2027"]),
             cell("$194,000", "verified", ["irs_2027"]),
             cell("$201,000", "verified", ["irs_2027"]),
             cell("Primary source", "verified", ["irs_2027"])],
            [cell("Top estate/gift rate above the exemption", "verified", ["congress_hr1"]),
             cell("40%", "verified", ["congress_hr1"]),
             cell("40%", "verified", ["congress_hr1"]),
             cell("Primary source", "verified", ["congress_hr1"])],
            [cell("Married couple with portability", "verified", ["irs_estate_faq"]),
             cell("up to $30,000,000", "verified", ["irs_estate_faq"]),
             cell("indexed upward", "verified", ["irs_2027"]),
             cell("Primary source", "verified", ["irs_estate_faq"])],
            [cell("Form 706 deadline", "verified", ["irs_estate_faq"]),
             cell("9 months after death; up to 6 more months on extension; portability needs a timely filing", "verified", ["irs_estate_faq"]),
             cell("same", "verified", ["irs_estate_faq"]),
             cell("Primary source", "verified", ["irs_estate_faq"])],
        ])
        + make_table("California status", ["Item", "Status", "Source"], [
            [cell("California estate tax return", "verified", ["sco_estate"]),
             cell("No requirement for decedents dying on or after January 1, 2005", "verified", ["sco_estate"]),
             cell("Primary source", "verified", ["sco_estate"])],
            [cell("California inheritance tax", "verified", ["sco_estate"]),
             cell("Program applies only to decedents who died before June 1982; gifts before 1982 similarly", "verified", ["sco_estate"]),
             cell("Primary source", "verified", ["sco_estate"])],
            [cell("Income tax on the inheritance itself", "verified", ["irs_gifts_faq"]),
             cell("Inheritances are generally not taxable income to the beneficiary under federal law; later income is taxable", "verified", ["irs_gifts_faq"]),
             cell("Primary source", "verified", ["irs_gifts_faq"])],
        ])
        + make_table("Projection into the 2040-2050 transfer window", ["Item", "Illustrative value", "Evidence status", "Scope note"], [
            [cell("Indexed federal exemption, illustrative at year " + str(TRANSFER_YEAR_BASE), "model", ["congress_hr1", "bls_cpi"]),
             cell(money(exempt_2045), "model", ["bls_cpi"]),
             cell("Grows the 2026 amount at the model's 2.5% inflation assumption; actual indexing follows the statutory chain-CPI mechanism year by year", "assumption", ["congress_hr1"])],
            [cell("Whether the estate exceeds it", "missing", ["irs_estate_tax"]),
             cell("", "missing", ["irs_estate_tax"]),
             cell("Requires the private estate inventory (question Q7); the cash inheritance is described by the owner as considerable", "owner", ["irs_estate_tax"])],
            [cell("Portability election if applicable", "guidance", ["irs_estate_faq"]),
             cell("File Form 706 even below the threshold to port the unused exclusion of the first spouse to die", "guidance", ["irs_estate_faq"]),
             cell("Rev. Proc. 2022-32 permits a late election within five years of death for estates not otherwise required to file", "guidance", ["irs_estate_faq"])],
        ])
        + prose(
            "Planning levers the advisers will discuss",
            "Annual-exclusion gifting ($19,000 per recipient in 2026, doubled with gift-splitting), lifetime gifting against the exclusion versus preserving step-up in basis, charitable structures, and life-insurance trusts. Each trades federal transfer tax against income-tax basis; none of them changes the California property-tax analysis on this site. Basis planning matters here because the Cupertino home's gain since acquisition will likely be forgiven by the step-up at death (Publication 551), while lifetime gifts would carry the old basis forward.",
        )
        + prose(
            "What could change these numbers",
            "Congress can change the exclusion at any time; the IRS indexes it annually; the exclusion amount under Proposition 19 re-adjusts every two years by BOE letter. Re-verify all amounts at the actual transfer date and against the year-of-death threshold table in the IRS estate-tax pages.",
        )
    )
    return render_page("pages/estate-thresholds.html", "Estate-tax thresholds", intro="Federal exclusion amounts, rates, portability and Form 706 timing — verified for 2026 and 2027 — plus California's no-estate-tax status and an honest projection into the transfer window.", body=body, eyebrow="LAW & PROCESS")


def timeline_step(when: str, what: str, status: str, keys: list[str]) -> str:
    return (
        f'<div class="tstep"><div class="twhen">{esc(when)}</div>'
        f'<div class="twhat">{esc(what)}<br>{badge(status)} {source_cell(keys)}</div></div>'
    )


def build_process() -> str:
    steps = [
        ("At death", "The revocable trust becomes irrevocable for the deceased settlor's share; this is the change-in-ownership date that starts every clock below", "verified", ["boe_annot_625", "probate_16061_7"]),
        ("Within 60 days", "Successor trustee serves the statutory notification on beneficiaries and heirs", "verified", ["probate_16061_7"]),
        ("Within 150 days", "Trustee files the change-in-ownership statement with the county recorder/assessor (Property A: Santa Clara County; Property B: San Francisco)", "verified", ["rtc_480"]),
        ("With recording", "Preliminary Change of Ownership Report accompanies recorded documents; a $20 fee applies without it", "verified", ["rtc_480_3"]),
        ("Within 1 year — critical", "If occupancy is intended: the Heir occupies Property A as a principal residence AND files the homeowners' exemption (BOE-266) within one year of the transfer date", "verified", ["rtc_63_2", "boe_pub801"]),
        ("As early as possible", "File BOE-19-P with the county assessor; within three years for full relief, and the exclusion can be lost if the home transfers to a third party first", "verified", ["boe_pub801", "scc_assessor_transfer"]),
        ("Month 1-2", "Order date-of-death appraisals for both properties; document basis for the step-up and Form 706 schedules", "verified", ["irs_p551", "irs_p559"]),
        ("Within 9 months", "If the gross estate exceeds the year-of-death threshold: file federal Form 706 (up to 6-month extension); a portability election also requires a timely filing", "verified", ["irs_estate_faq", "irs_estate_tax"]),
        ("California", "No California estate tax return for deaths on or after 2005; no inheritance tax program for this generation", "verified", ["sco_estate"]),
        ("Dec 10 / Apr 10", "Secured property-tax installments are delinquent after December 10 and April 10; supplemental bills for the year of transfer arrive separately", "verified", ["sf_treasurer", "scc_assessor_root"]),
        ("Ongoing year 1", "Insurance: notify carriers immediately; vacancy clauses can strip coverage on an unoccupied home; obtain quotes before the transfer if a sale or rental is possible", "guidance", ["cdi_residential", "cafairplan"]),
        ("Ongoing year 1", "Utilities and solar: transfer water/electric accounts; confirm the solar tariff's transferability (NEM agreements do not automatically follow a new owner)", "guidance", ["cpuc_nem", "waterboards", "sfpuc"]),
        ("If selling", "A prompt sale after death realizes gain against a stepped-up basis (near zero in the base case); California withholding applies only if the seller is a nonresident", "verified", ["irs_p551", "rtc_18662"]),
        ("If renting", "Reassessment applies because the occupancy test failed; leases, rent-cap rules and landlord coverage change the cost structure", "verified", ["rtc_63_2", "civ_1947_12", "cdi_residential"]),
        ("Homeowners' exemption caveat", "The $7,000 exemption does not extend to rented or vacant property — the occupancy intent and this filing decide the Prop 19 exclusion together", "verified", ["rtc_218", "rtc_63_2"]),
    ]
    timeline = "".join(timeline_step(w, s, st, k) for w, s, st, k in steps)
    body = (
        callout("The inheritance sequence, step by step", "A trust transfer avoids probate but not deadlines. The two clocks that decide the money are the one-year occupancy/exemption window and the three-year BOE-19-P claim window; the nine-month Form 706 clock decides the federal estate-tax side.", "info")
        + f'<section class="table-section"><h2>Deadline timeline</h2><div class="timeline">{timeline}</div></section>'
        + make_table("Pre-death checklist (Trustor window)", ["Item", "Why", "Source"], [
            [cell("Confirm the trust is funded (Property A titled to the trust) and amendments are current", "guidance", ["probate_16061_7"]),
             cell("An unfunded home can force probate and reset every timeline above", "guidance", ["probate_16061_7"]),
             cell("Primary source", "verified", ["probate_16061_7"])],
            [cell("Review whether the Trustor should keep or sell during life (55+ base transfer exists only for a same-county replacement home under Prop 19 rules)", "guidance", ["boe_pub801"]),
             cell("Selling during life forfeits the family-home exclusion for the heirs unless a qualifying replacement applies", "guidance", ["boe_pub801"]),
             cell("Primary source", "verified", ["boe_pub801"])],
            [cell("Audit beneficiary designations outside the trust (retirement accounts, insurance)", "guidance", ["irs_p559"]),
             cell("These assets bypass the trust and carry their own tax regimes", "guidance", ["irs_p559"]),
             cell("Primary source", "verified", ["irs_p559"])],
            [cell("Keep the estate inventory list current (question Q7)", "guidance", ["irs_estate_tax"]),
             cell("Form 706 planning and portability depend on it", "guidance", ["irs_estate_faq"]),
             cell("Primary source", "verified", ["irs_estate_tax", "irs_estate_faq"])],
        ])
        + prose(
            "Who does what",
            "The successor trustee executes the notifications and filings; the estate attorney confirms the trust interpretation and any Form 706 strategy; the CPA handles fiduciary returns and basis reporting; the insurance professional reprices both properties for their next use; the family decides occupancy. The one-page attorney and CPA brief collects the decisions that need their signatures.",
        )
    )
    return render_page("pages/inheritance-process.html", "Deadline timeline", intro="The step-by-step inheritance process rendered as a deadline timeline: what happens at death, the one-year and three-year Proposition 19 windows, Form 706 timing, and the first-year operational checklist.", body=body, eyebrow="LAW & PROCESS")


def build_law_watchlist() -> str:
    rows = [
        [cell("Proposition 19 amendment or repeal efforts", "missing", ["sos_ballot", "boe_pub801"]),
         cell("An exclusion repeal would remove the single largest tax protection in this analysis", "guidance", ["rtc_63_2"]),
         cell("Check the Secretary of State ballot-measure page and BOE letters annually", "guidance", ["sos_ballot"])],
        [cell("Prop 19 exclusion amount biennial adjustments", "verified", ["boe_lta25009"]),
         cell("The $1,044,586 amount applies to transfers through February 15, 2027; BOE letters announce each adjustment", "verified", ["boe_lta25009"]),
         cell("Update the cap in the model after each new letter", "guidance", ["boe_lta25009"])],
        [cell("Federal estate/gift exclusion changes", "verified", ["congress_hr1", "irs_2027"]),
         cell("P.L. 119-21 set $15,000,000 for 2026 with indexing; a future Congress can change it", "verified", ["congress_hr1"]),
         cell("Watch IRS inflation-adjustment releases and revenue procedures each fall", "guidance", ["irs_2027"])],
        [cell("Step-up-in-basis reform proposals", "missing", ["irs_p551"]),
         cell("Repeated federal proposals target basis step-up at death; none is enacted", "guidance", ["irs_p551"]),
         cell("If enacted, lifetime-gifting versus step-up planning changes materially", "guidance", ["congress_hr1"])],
        [cell("Statewide rent-cap evolution", "verified", ["civ_1947_12"]),
         cell("The Tenant Protection Act caps rent increases with exemptions; ballot and legislative changes recur", "verified", ["civ_1947_12"]),
         cell("Re-check before renting either property", "guidance", ["civ_1947_12"])],
        [cell("Insurance market restructuring", "missing", ["cdi_residential", "cafairplan"]),
         cell("Availability and pricing are in flux; residual-market reliance is growing", "guidance", ["cdi_residential"]),
         cell("Refresh quotes annually; watch CDI announcements", "guidance", ["cdi_residential"])],
        [cell("Nonresident withholding rate changes", "verified", ["rtc_18662"]),
         cell("The statutory framework changes occasionally; confirm the current rate at any sale", "verified", ["rtc_18662"]),
         cell("FTB page or the CPA confirm before escrow", "guidance", ["ftb_root"])],
        [cell("Interest-rate environment", "secondary", ["cbo_rates", "treasury_bills"]),
         cell("CBO scenarios anchor Treasury-parking yield assumptions; actual auction results govern", "secondary", ["cbo_rates"]),
         cell("Update the staging analysis with then-current yields at the transfer window", "guidance", ["treasury_bills"])],
    ]
    body = (
        callout("Proposed, not enacted", "Everything on this page is either current law (linked) or a watch item (proposals and trends). Nothing here is treated as enacted law; no proposal is assumed to pass. Re-verify each item at the actual transfer date.", "warning")
        + make_table("Law and policy watchlist", ["Watch item", "Why it matters here", "How to monitor"], rows)
        + prose(
            "Verification cadence",
            "A 2040-2050 transfer window implies roughly one full revision of this site's assumptions per decade and a light-touch annual check: BOE letters (Prop 19 cap), IRS annual inflation adjustments, CDI bulletins (insurance), Secretary of State initiatives, and CBO rate outlooks. The suggestions page tracks a data-refresh checklist as an implementable item.",
        )
    )
    return render_page("pages/law-watchlist.html", "Law watchlist", intro="Current law versus live proposals that could change the analysis, each with an official monitoring step — nothing treated as enacted until verified.", body=body, eyebrow="LAW & PROCESS")


def build_brief() -> str:
    t = TRANSFER_YEAR_BASE
    rows = [
        [cell("Property A (inherited via trust, ~2040-2050)", "guidance", ["boe_pub801"]),
         cell("Cupertino area, Santa Clara County. Occupied-path tax " + money(tax_occupied(t)) + "/yr vs reassessed " + money(tax_reassessed(t)) + "/yr (base case)", "model", ["scc_ratebook", "rtc_63_2"]),
         cell("Decision hinges on one-year occupancy; BOE-19-P within 3 years; homeowners' exemption within 1 year", "verified", ["rtc_63_2", "boe_pub801"])],
        [cell("Property B (already owned by Heir)", "guidance", ["sf_assessor_root"]),
         cell("San Francisco Outer Sunset triplex; 2 units rented at " + money(B_RENT_MONTH) + "/mo; ultra-low Prop 13 base worth protecting", "owner", ["const_13a", "hud_fmr"]),
         cell("Not part of the inheritance decision; affects cash flow and housing", "guidance", ["irs_p527"])],
        [cell("Federal estate tax", "verified", ["congress_hr1"]),
         cell("$15,000,000 exclusion (2026, indexed: $15,480,000 in 2027); 40% above; portability to $30,000,000; Form 706 due 9 months after death", "verified", ["irs_estate_faq", "irs_2027"]),
         cell("Confirm against the private estate inventory; late-portability window 5 years (Rev. Proc. 2022-32)", "guidance", ["irs_estate_faq"])],
        [cell("California estate/inheritance tax", "verified", ["sco_estate"]),
         cell("None for deaths on or after 2005", "verified", ["sco_estate"]),
         cell("Federal tax is the only death-tax exposure", "guidance", ["sco_estate"])],
        [cell("Basis and sale", "verified", ["irs_p551", "irs_p523"]),
         cell("Basis steps to date-of-death value; prompt sale has near-zero gain; §121 excludes $250,000/$500,000 after 2-of-5-year occupancy", "verified", ["irs_p551", "irs_p523"]),
         cell("Nonresident withholding applies if the Heir sells as a nonresident", "verified", ["rtc_18662"])],
        [cell("Recommended decision logic", "guidance", ["page:decision-analysis.html"]),
         cell("Occupy within 1 year if genuinely intended (locks exclusion worth about " + money(tax_reassessed(t) - tax_occupied(t)) + "/yr); otherwise sell promptly, park proceeds in 3M-2Y Treasuries 24-36 months, then phase into equities; renting the reassessed home loses about " + money(-rental_net(t)["net"]) + "/yr in the base case", "model", ["damodaran", "treasury_bills"]),
         cell("Ranking flips on occupancy intent, trustor selling during life, estate size vs exemption, and multi-beneficiary allocation", "guidance", ["boe_pub801", "irs_estate_tax"])],
    ]
    questions = [
        "Trust type, amendments, and distribution scheme (pro-rata?)",
        "Heir occupancy intent within one year (the decisive fact)",
        "Estate inventory vs indexed federal exclusion; portability if married",
        "Written insurance quotes for both properties (owner-occupied, landlord, FAIR Plan + DIC)",
        "Actual utility bills and the solar tariff/interconnection agreement",
        "Property A rate area and fixed assessments from the county tax bill",
        "Cupertino market-rent evidence at the transfer window (HUD FMR plus listings)",
        "Trustee succession and professional fiduciary preferences",
    ]
    qlist = "".join(f"<li>{esc(q)}</li>" for q in questions)
    body = (
        callout("Print this page for the advisory meeting", "One page, no identifying details required: the properties are placeholders, the figures are rounded, and every claim links to an official source. The advisers' signature decisions are at the bottom.", "info")
        + make_table("Attorney & CPA briefing sheet", ["Item", "Status and numbers", "What the adviser must decide"], rows)
        + f'<section class="prose"><h2>Questions the advisers must answer</h2><ul>{qlist}</ul></section>'
        + prose(
            "Sources for manual review",
            "Statutory text: California Revenue and Taxation Code §§63.2, 480, 218, 18662 and Probate Code §16061.7 (California Legislative Information). Federal: Public Law 119-21 §70106 via Congress.gov; IRS estate/gift pages, IR-2026-133, Publications 551, 523, 527, 559. Rates: Santa Clara County Tax Rate Book 2025-2026; San Francisco Treasurer. All links are on the Sources page with check dates.",
        )
        + prose(
            "Decisions requested at the meeting",
            "(1) Confirm occupancy intent and the resulting path; (2) confirm the Form 706 / portability strategy against the estate inventory; (3) confirm the trust's allocation treatment of the residence; (4) approve the evidence-collection list with owners and deadlines; (5) set the review date before the transfer window.",
        )
    )
    return render_page("pages/attorney-cpa-brief.html", "Attorney &amp; CPA briefing sheet", intro="A one-page printable brief: the decision, the verified law, the rounded numbers, and the signature decisions requested — no identifying details required.", body=body, eyebrow="ADVISER")


def build_flagged() -> str:
    rows = [
        [cell("Policy change: figures published (rounded to $10) instead of blank", "guidance", ["page:privacy.html"]),
         cell("The owner's latest instruction asks for rounded figures in the analysis; earlier sessions published blanks only. This site implements the rounded-figures policy; confirm it is the intended permanent rule", "guidance", ["page:privacy.html"]),
         cell("Owner confirmation", "missing", ["page:privacy.html"])],
        [cell("All owner-provided figures are unverified by definition", "owner", ["scc_assessor_root", "sf_assessor_root"]),
         cell("Assessment histories, rent, utility ranges, values and insurance guesses come from private records rounded to $10; no official source can confirm them without identifying the parcel", "owner", ["scc_assessor_root"]),
         cell("Verify against private tax bills and statements; the county pages above let the owner check each figure without publishing it", "guidance", ["scc_assessor_root", "sf_treasurer"])],
        [cell("Insurance premiums are blank", "missing", ["cdi_residential"]),
         cell("The owner's guesses ($1,500 per property) are unverified and likely low for current Bay Area pricing; no official source states a parcel-specific premium", "assumption", ["cdi_residential", "cafairplan"]),
         cell("Obtain written quotes; update the model", "guidance", ["cdi_residential"])],
        [cell("Property A's 2026 tax bill is unknown", "missing", ["scc_assessor_root"]),
         cell("The owner's table shows no 2025-26 figure for the 2026 assessed value; the model grows the 2025 bill at 2%", "derived", ["const_13a"]),
         cell("Read the current bill and replace the derivation", "guidance", ["scc_assessor_root"])],
        [cell("Cupertino ad-valorem rate assumed at 1.17%", "derived", ["scc_ratebook"]),
         cell("The county Tax Rate Book is official but the parcel's exact rate area is not published here; third-party compilations put Cupertino composites near 1.16-1.18%", "derived", ["scc_ratebook"]),
         cell("Confirm the rate area from the parcel's bill and update the model", "guidance", ["scc_ratebook"])],
        [cell("Postal codes intentionally omitted", "guidance", ["page:privacy.html"]),
         cell("Rounded figures plus a postal code would narrow identification to a handful of parcels; the site uses county-level geography only", "guidance", ["page:privacy.html"]),
         cell("Owner review of the privacy tradeoff", "guidance", ["page:privacy.html"])],
        [cell("Pre-rounding figures remain in public Git history", "missing", ["github_repo"]),
         cell("A pickaxe audit of the fetched history found the unrounded case data across multiple historical commits and paths; the current tree is clean, but commits, PR diffs and caches are still public", "missing", ["github_repo"]),
         cell("Execute the owner-run history-scrub plan; treat historic material as exposed until then", "guidance", ["page:privacy.html"])],
        [cell("Repository visibility is public", "missing", ["page:privacy.html"]),
         cell("A prior session's attempt to restrict visibility failed with an access error; the owner must change visibility if desired", "missing", ["page:privacy.html"]),
         cell("Owner decision: private repo or accepted-public posture", "guidance", ["page:privacy.html"])],
        [cell("Historical return series is a secondary source", "secondary", ["damodaran"]),
         cell("The 1928-2025 annual returns come from the NYU Stern compilation, not a primary market database; headline years were cross-checked against Federal Reserve History where possible", "secondary", ["damodaran", "fedhist_1929"]),
         cell("Verify specific years against primary data before acting", "guidance", ["fedhist_1929"])],
        [cell("Market-rent estimate for Property A is unverified", "assumption", ["hud_fmr"]),
         cell("The $7,000/month figure anchors the rental-path conclusion; HUD FMRs are 40th-percentile benchmarks and sit below true market rents for high-value homes", "assumption", ["hud_fmr"]),
         cell("Collect comparable listings at the transfer window", "guidance", ["hud_fmr"])],
        [cell("Solar tariff version unknown", "missing", ["cpuc_nem"]),
         cell("The owner reports a monthly credit; whether NEM 1.0/2.0 grandfathering or net billing applies changes the credit materially", "missing", ["cpuc_nem"]),
         cell("Read the interconnection agreement and 12 months of statements", "guidance", ["cpuc_nem"])],
        [cell("Prop 19 move-out consequence depends on county administration", "verified", ["rtc_63_2"]),
         cell("The statute removes the exclusion and enrolls the change-in-ownership-date base value, adjusted annually, from the next lien date; county practice details should be confirmed with the assessor", "verified", ["rtc_63_2", "scc_assessor_transfer"]),
         cell("Ask the county assessor how the enrolled value is computed in practice", "guidance", ["scc_assessor_transfer"])],
        [cell("San Francisco secured rate quoted from the FY 2025-26 figure", "verified", ["sf_treasurer"]),
         cell("The 1.18268325% figure is corroborated by multiple sources referencing the Treasurer's page; confirm on the parcel's bill each year", "verified", ["sf_treasurer"]),
         cell("Re-check annually", "guidance", ["sf_treasurer"])],
        [cell("Prior session's board note on PR #80 was stale", "guidance", ["github_repo"]),
         cell("The board recorded PR #80 as open while the merge had landed; the current session verified the merge commit and proceeded from it", "guidance", ["github_repo"]),
         cell("No action needed; recorded for audit accuracy", "guidance", ["github_repo"])],
    ]
    body = (
        callout("Flagged for review — non-blocking", "These items are published so they can be reviewed after the site goes live. Unverified flags do not block release; they define what still needs evidence.", "warning")
        + make_table("Flagged items", ["Item", "Why flagged", "Action"], rows)
    )
    return render_page("pages/flagged-for-review.html", "Flagged for review", intro="Everything unverified, assumed, or changed by policy this session — with the official links that will resolve each flag when the evidence exists.", body=body, eyebrow="REVIEW")


def build_glossary() -> str:
    terms = [
        ("Assessed value", "The taxable value on the county roll; under Proposition 13 it rises at most 2% per year absent a change in ownership or new construction.", "verified", ["const_13a"]),
        ("Base year value", "The value enrolled when a property was last reassessed; the starting point for all later inflation factoring.", "verified", ["const_13a"]),
        ("Factored base year value", "Base year value adjusted annually (up to 2%) — the Prop 13 value the Trustor's home carries into a transfer.", "verified", ["const_13a"]),
        ("Change in ownership", "The event that triggers reassessment; for a revocable trust it occurs when the trust becomes irrevocable (at the settlor's death).", "verified", ["boe_annot_625"]),
        ("Proposition 19", "The 2020 constitutional amendment that narrowed the parent-child exclusion: family home only, occupancy required, value-capped.", "verified", ["rtc_63_2"]),
        ("BOE-19-P", "The claim form filed with the county assessor to request the parent-child exclusion; within three years of transfer for full relief.", "verified", ["boe_pub801"]),
        ("BOE-266", "The homeowners' exemption claim; must be filed within one year of the transfer to secure the family-home exclusion.", "verified", ["rtc_63_2"]),
        ("Homeowners' exemption", "A $7,000 full-value exemption for an owner-occupied principal residence; unavailable for rented or vacant property.", "verified", ["rtc_218"]),
        ("Reassessment", "Enrollment of a new (usually market) value at change in ownership or completion of new construction.", "verified", ["const_13a"]),
        ("Supplemental assessment", "A separate bill for the value change between the transfer date and the next lien date.", "verified", ["sf_treasurer"]),
        ("Step-up in basis", "The heir's income-tax basis becomes the property's date-of-death fair market value, erasing built-in gain for later sale.", "verified", ["irs_p551"]),
        ("Section 121 exclusion", "Exclusion of $250,000 (single) / $500,000 (married) of gain on a main home after two-of-five-year ownership and use.", "verified", ["irs_p523"]),
        ("Federal estate tax", "40% (top rate) on estates above the basic exclusion amount; $15,000,000 per person for 2026, indexed after 2026.", "verified", ["congress_hr1", "irs_whatsnew"]),
        ("Portability", "A surviving spouse can inherit the deceased spouse's unused exclusion via a timely Form 706.", "verified", ["irs_estate_faq"]),
        ("Form 706", "The federal estate-tax return; due nine months after death with an up-to-six-month extension; also the vehicle for portability.", "verified", ["irs_estate_faq"]),
        ("Annual gift exclusion", "$19,000 per recipient in 2026 ($20,000 in 2027); gifts within it never touch the lifetime exclusion.", "verified", ["irs_2027"]),
        ("Revocable living trust", "A trust the settlor can revoke; avoids probate; becomes irrevocable at death, starting the trust-administration clocks.", "verified", ["probate_16061_7"]),
        ("Successor trustee", "The person who administers the trust after the settlor's death: notices, filings, accounting, distributions.", "verified", ["probate_16061_7"]),
        ("Probate", "Court administration of assets outside a trust; the reason trust funding matters.", "verified", ["probate_16061_7"]),
        ("Preliminary Change of Ownership Report (PCOR)", "The recorder-filed report describing a transfer; $20 fee if omitted.", "verified", ["rtc_480_3"]),
        ("Change-in-ownership statement (death)", "The trustee files it within 150 days after the date of death for trust transfers.", "verified", ["rtc_480"]),
        ("Direct assessments", "Fixed per-parcel charges (voter-approved debt, special districts) that do not scale with assessed value.", "verified", ["scc_ratebook"]),
        ("Ad-valorem rate", "The percentage rate applied to assessed value; Cupertino assumed at 1.17% pending rate-area confirmation; San Francisco FY 2025-26 is 1.18268325%.", "derived", ["scc_ratebook", "sf_treasurer"]),
        ("Fair Market Rent (FMR)", "HUD's 40th-percentile gross-rent benchmark by bedroom count; a floor anchor, not market rent.", "verified", ["hud_fmr"]),
        ("Sequence risk", "The danger that the order of returns (a crash early in retirement or after inheritance) damages outcomes more than the average return suggests.", "guidance", ["damodaran"]),
        ("Reinvestment risk", "The risk that money parked at today's yield must later be re-invested at lower yields, or that delayed equity entry misses gains.", "guidance", ["treasury_bills", "cbo_rates"]),
        ("Treasury bills / notes", "Federal debt with maturities up to 52 weeks (bills) and 2-10 years (notes); interest is state- and locally tax-exempt.", "verified", ["treasury_bills", "treasury_notes"]),
        ("Dollar-cost averaging (DCA)", "Investing fixed amounts on a schedule instead of a lump sum; reduces timing risk at the cost of missing some upside.", "guidance", ["investor_stocks"]),
        ("Black swan", "A rare, severe, hard-to-predict regime (1929, 2008) that dominates long-horizon outcomes; modeled here with real historical data.", "guidance", ["fedhist_1929", "fedhist_recession"]),
        ("Stagflation", "High inflation with weak growth (1973-1974 era); punishes both equities and cash simultaneously.", "secondary", ["damodaran"]),
        ("Nominal vs real", "Nominal values are actual dollars; real values are inflation-adjusted; a 50-year model must state which it uses.", "guidance", ["bls_cpi"]),
        ("Nonresident withholding", "California requires withholding on real-estate sales by nonresidents (§18662); relevant only if the heir lives outside California at a sale.", "verified", ["rtc_18662"]),
        ("FAIR Plan", "California's residual fire-insurance pool; limited perils, often paired with a difference-in-conditions policy.", "verified", ["cafairplan"]),
        ("NEM / net billing", "California's solar compensation frameworks; the applicable tariff determines the household credit.", "verified", ["cpuc_nem"]),
        ("Evidence badges", "verified = confirmed against the linked official source; owner = owner-provided and rounded; derived = arithmetic from owner data plus a stated rate; model = transparent model output; assumption = adjustable input; secondary = reputable non-official compilation; missing = unknown, blank by policy; guidance = general rule.", "guidance", ["page:privacy.html"]),
    ]
    rows = [[cell(term, st, keys), cell(definition, st, keys)] for term, definition, st, keys in terms]
    body = make_table("Glossary", ["Term", "Meaning"], rows)
    return render_page("pages/glossary.html", "Glossary", intro="Plain-language definitions for every term used in the analysis, each linked to its official source.", body=body, eyebrow="REFERENCE")


def build_sources() -> str:
    rows = []
    for key, (label, url, scope) in SOURCES.items():
        rows.append([
            cell(key, "verified" if key not in ("damodaran", "cbo_rates") else "secondary", [key]),
            cell(label, "verified" if key not in ("damodaran", "cbo_rates") else "secondary", [key]),
            cell(scope, "guidance", [key]),
            cell(CHECKED, "guidance", [key]),
        ])
    body = (
        callout("How to read this register", "Every table row on this site links to one of these sources, and every link opens the official page. A source supports only its stated scope — it never validates a private property fact. Damodaran's historical-return compilation and CBO's rate outlook are flagged secondary: reputable, but not primary market data.", "info")
        + make_table("Official source register", ["Key", "Source", "Scope (what it does and does not establish)", "Checked"], rows)
    )
    return render_page("pages/sources.html", "Official source register", intro="Every source used on this site with its scope and check date, so any claim can be reviewed manually.", body=body, eyebrow="REFERENCE")


def build_privacy() -> str:
    rows = [
        [cell("Placeholders", "verified", ["page:privacy.html"]),
         cell("Property A / Property B / Heir / Trustor replace all identifying labels; no addresses, parcel numbers, names, postal codes, emails, or phone numbers appear anywhere in the generated site", "verified", ["page:privacy.html"])],
        [cell("Rounding rule", "verified", ["page:privacy.html"]),
         cell("Every currency figure on the site is a multiple of $10 (except the statutory $1,044,586 exclusion amount), per the owner's anti-tracing instruction; the automated verifier enforces this and rejects unrounded figures", "verified", ["page:privacy.html"])],
        [cell("Owner-provided data handling", "verified", ["page:privacy.html"]),
         cell("Owner figures enter the builder already rounded, carry the owner badge, and never include exact fingerprints; exact values remain in private records outside this repository", "verified", ["page:privacy.html"])],
        [cell("No network", "verified", ["page:privacy.html"]),
         cell("The site loads only local assets; the CSP forbids any connection; suggestion-review choices stay in one browser's localStorage and are never transmitted", "verified", ["page:privacy.html"])],
        [cell("Repository history boundary", "missing", ["github_repo"]),
         cell("The current tree is clean, but historical Git commits, PR diffs, forks and caches still contain pre-rounding case material and cannot be scrubbed by a branch-level change; an owner-executable plan exists at tools/history-scrub-plan.md", "missing", ["github_repo"])],
        [cell("Repository visibility", "missing", ["page:privacy.html"]),
         cell("GitHub reports this repository is public; noindex is not access control; visibility is an owner decision", "missing", ["page:privacy.html"])],
        [cell("What the site refuses to publish", "verified", ["page:privacy.html"]),
         cell("Street addresses, parcel identifiers, postal codes, personal names, trust names, unrounded assessment or tax figures, loan or account numbers, and any document scan", "verified", ["page:privacy.html"])],
    ]
    body = (
        callout("Privacy is the highest-urgency constraint", "Personal information is anonymized with placeholders and rounded figures; anything discovered during research stays internal and never reaches the website; the verification rules are automated so a future edit cannot quietly leak a value.", "warning")
        + make_table("Privacy rules in force", ["Rule", "How it is enforced"], rows)
        + prose(
            "Manual review checklist",
            "Before any edit merges: run tools/build.py and tools/verify.py; search the diff for any five-digit number, address pattern, or unrounded currency; confirm no new source violates the official-host list; and re-read the flagged page so new assumptions are visible. The verifier automates the first two checks; the reviewer supplies the judgment.",
        )
    )
    return render_page("pages/privacy.html", "Privacy & limits", intro="What this site publishes, what it refuses to publish, how rounding and placeholders protect the family, and the honest boundary between the current tree and Git history.", body=body, eyebrow="REFERENCE")


PAGES = [
    ("index.html", build_index),
    ("pages/executive-summary.html", build_executive_summary),
    ("pages/decision-analysis.html", build_decisions),
    ("pages/questions.html", build_questions),
    ("pages/suggestions.html", build_suggestions),
    ("pages/projections.html", build_projections),
    ("pages/property-tax.html", build_property_tax),
    ("pages/operating-costs.html", build_costs),
    ("pages/black-swan.html", build_black_swan),
    ("pages/phased-investing.html", build_phased_investing),
    ("pages/estate-thresholds.html", build_estate_thresholds),
    ("pages/inheritance-process.html", build_process),
    ("pages/law-watchlist.html", build_law_watchlist),
    ("pages/attorney-cpa-brief.html", build_brief),
    ("pages/flagged-for-review.html", build_flagged),
    ("pages/glossary.html", build_glossary),
    ("pages/sources.html", build_sources),
    ("pages/privacy.html", build_privacy),
]


def build() -> None:
    for relative, builder in PAGES:
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(builder(), encoding="utf-8")
    manifest = ROOT / "tools" / "site-manifest.json"
    manifest.write_text(json.dumps([relative for relative, _ in PAGES], indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(PAGES)} pages.")


if __name__ == "__main__":
    build()
