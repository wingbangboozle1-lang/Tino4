#!/usr/bin/env python3
"""Build a public, privacy-first inheritance decision guide.

Figures are published only after rounding to the nearest ten dollars, and no
locality, parcel, account or party identifier appears anywhere. Exact records
belong in an offline adviser workpaper, not this public repository; nothing is
read from a file and nothing is stored by the browser.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SOURCES = {
    "irs_estate": ("IRS — Estate tax", "https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax", "Federal estate-tax filing thresholds and general rules; not an individual estate calculation."),
    "irs_estate_faq": ("IRS — Estate-tax filing FAQs", "https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-estate-taxes", "Gross-estate filing test, Form 706 timing, extension request, and portability filing considerations."),
    "irs_2027": ("IRS — 2027 tax inflation adjustments", "https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2027-taxpayers-continue-to-benefit-from-the-working-families-tax-cuts", "Official 2027 federal estate and gift tax adjustments; no prediction beyond the published year."),
    "irs_basis": ("IRS — Gifts and inheritances FAQ", "https://www.irs.gov/faqs/interest-dividends-other-types-of-income/gifts-inheritances/gifts-inheritances", "General inherited-property basis rules and exceptions; does not establish an appraisal or an individual basis."),
    "irs_pub551": ("IRS Publication 551 — Basis of Assets", "https://www.irs.gov/publications/p551", "Basis, adjusted basis, and adjustments including improvements and depreciation."),
    "irs_121": ("IRS Topic 701 — Sale of your home", "https://www.irs.gov/taxtopics/tc701", "Section 121 main-home exclusion amounts and ownership/use tests; eligibility depends on facts."),
    "irs_1041": ("IRS — About Form 1041", "https://www.irs.gov/forms-pubs/about-form-1041", "Fiduciary income-tax return scope; whether a particular estate or trust must file depends on its facts."),
    "irs_rental": ("IRS Publication 527 — Residential Rental Property", "https://www.irs.gov/publications/p527", "Rental income, expenses, personal use, repairs, improvements, vacancy, and depreciation."),
    "irs_1031": ("IRS Publication 544 — Sales and Other Dispositions of Assets", "https://www.irs.gov/publications/p544", "Federal disposition rules, including like-kind exchange treatment; applicability depends on property use, transaction structure and deadlines."),
    "irs_706": ("IRS — About Form 706", "https://www.irs.gov/forms-pubs/about-form-706", "Estate tax return, filing instructions, and due-date information."),
    "ca_sco": ("California State Controller — Estate tax", "https://www.sco.ca.gov/ardtax_estate_tax.html", "California estate-tax return requirement information for deaths on or after January 1, 2005."),
    "ca_rtc13301": ("California statute — death-transfer tax",  "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=13301.&lawCode=RTC", "Current California law on death-transfer taxes; future legislation can change current law."),
    "boe_prop19": ("California BOE — Proposition 19", "https://www.boe.ca.gov/prop19/", "Current intergenerational property-tax exclusion overview and filing requirements."),
    "ca_rtc63": ("California Revenue and Taxation Code §63.2", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=63.2.&lawCode=RTC", "Statutory family-home/family-farm exclusion conditions, eligibility, occupancy, and value-limit formula."),
    "boe_lta": ("California BOE — Letter to Assessors 2025/009", "https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf", "Official Proposition 19 indexed amounts and adjustment period through February 15, 2027; next adjustment is due in 2027."),
    "ca_rtc51": ("California Revenue and Taxation Code §51", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=51.&lawCode=RTC", "Taxable-value framework and annual inflation adjustment, subject to reassessment and statutory rules."),
    "ca_rtc218": ("California Revenue and Taxation Code §218", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=218.&lawCode=RTC", "Homeowners' property-tax exemption eligibility and amount."),
    "ca_rtc480": ("California Revenue and Taxation Code §480", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=480.&lawCode=RTC", "Change-in-ownership statement timing in specified death transfers."),
    "ca_rtc11911": ("California statute — documentary transfer tax",  "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=11911.&lawCode=RTC", "Authorizes documentary transfer taxes under the statute; the applicable local rate and exemptions require jurisdiction-specific official schedules."),
    "ca_gov27361": ("California statute — recording fees",  "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=27361.&lawCode=GOV", "Recording-fee statute; the actual fee depends on recorded document and applicable schedule."),
    "ca_prob": ("California Probate Code — trustee notice",  "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=16061.7.&lawCode=PROB", "Trustee notice obligations and timing for specified trust events, subject to applicability."),
    "ca_rent": ("California Civil Code §1947.12", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1947.12.&lawCode=CIV", "Statewide rent-cap text and exemptions; local law and unit coverage need separate review."),
    "cdi": ("California Department of Insurance — Residential insurance", "https://www.insurance.ca.gov/01-consumers/105-type/5-residential/index.cfm", "Insurance shopping resources and coverage context; no household premium or quote."),
    "cpuc_solar": ("California Public Utilities Commission — Net metering and net billing", "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/customer-generation/net-energy-metering-and-net-billing", "Solar export tariff context; actual credits depend on tariff, interconnection date, usage and utility bill."),
    "water_board": ("California State Water Resources Control Board — Drinking Water Program", "https://www.waterboards.ca.gov/drinking_water/programs/", "State oversight and public-water-system information; does not establish a service account's bill."),
    "cslb": ("California Contractors State License Board — Check a license", "https://www.cslb.ca.gov/OnlineServices/CheckLicenseII/CheckLicense.aspx", "Contractor-license lookup; does not set or validate repair prices."),
    "treasury_bills": ("TreasuryDirect — Treasury bills", "https://treasurydirect.gov/marketable-securities/treasury-bills/", "Bill maturities, auction rates, holding/sale mechanics, and interest tax treatment."),
    "treasury_notes": ("TreasuryDirect — Treasury notes", "https://www.treasurydirect.gov/marketable-securities/treasury-notes/", "Note maturities and interest; market price may vary if sold before maturity."),
    "fed_1929": ("Federal Reserve History — Stock Market Crash of 1929", "https://www.federalreservehistory.org/essays/stock-market-crash-of-1929", "Reports an 89% Dow Jones Industrial Average peak-to-trough decline and that the prior high was not regained until 1954. This price-index episode is not a portfolio forecast or probability."),
    "fed_depression": ("Federal Reserve History — The Great Depression", "https://www.federalreservehistory.org/essays/great-depression", "Historical account of financial and economic stress in the 1930s; not a forecast."),
    "fed_inflation": ("Federal Reserve History — The Great Inflation", "https://www.federalreservehistory.org/essays/great-inflation", "Historical account of inflation and policy in the 1960s–1980s; not a probability estimate."),
    "fed_2007_2009": ("Federal Reserve History — The Great Recession of 2007 to 2009", "https://www.federalreservehistory.org/essays/great-recession-of-200709", "Reports an 18-month recession, a 57% S&P 500 peak-to-trough fall, an approximately 30% average U.S. home-price decline from the mid-2006 peak, and the policy response. Historical description, not a forecast for a portfolio or property."),
    "fed_2008": ("Federal Reserve History — The Great Recession", "https://www.federalreservehistory.org/essays/great-recession-and-its-aftermath", "The aftermath account of the same period; it reports national home prices falling by over a fifth from the first quarter of 2007 to the second quarter of 2011, a different measurement window from the 2007 to 2009 recession essay. Historical description, not a forecast."),
    "bls_cpi": ("U.S. Bureau of Labor Statistics — CPI", "https://www.bls.gov/cpi/", "Consumer Price Index data and methodology; historical inflation is not a future path."),
    "cbo_long": ("Congressional Budget Office — Long-Term Budget Outlook", "https://www.cbo.gov/topics/budget/long-term-budget-outlook", "Long-run fiscal and economic baseline publications; not a 50-year property or portfolio forecast."),
    "cbo_outlook": ("Congressional Budget Office — Economic Outlook", "https://www.cbo.gov/topics/economy", "Near-term economic baseline publications; verify the latest edition before use."),
    "fhfa": ("Federal Housing Finance Agency — House Price Index", "https://www.fhfa.gov/data/hpi", "Broad house-price index data; not an appraisal or forecast for a particular home."),
    "sec_stocks": ("SEC Investor.gov — Stocks", "https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks", "General stock-market risk information; no expected return is promised."),
    "congress_law": ("Congress.gov — Public Law 119-21", "https://www.congress.gov/bill/119th-congress/house-bill/1", "Enacted federal legislation; check statutory text and current IRS guidance for application."),
    "github_sensitive": ("GitHub Docs — Removing sensitive data from a repository", "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository", "Official guidance on sensitive data in Git history; prior clones, forks and copies may remain outside a repository cleanup."),
    "ftb_forms": ("California Franchise Tax Board — Forms and publications", "https://www.ftb.ca.gov/forms/", "Official entry point for current-year forms and instructions; the applicable year must be selected at the decision date."),
    "ftb_540": ("FTB — 2025 Form 540 instructions", "https://www.ftb.ca.gov/forms/2025/2025-540-instructions.html", "Read 2026-11-16: 2025 Form 540 instructions for line 62 state that if taxable income exceeds $1,000,000, compute the Behavioral Health Services Tax as 1% of the excess, using whole dollars. This establishes the published 2025 return instruction, not a future-year rule or private tax liability."),
    "ca_rtc17043": ("California statute — additional tax on high taxable income", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=17043.&lawCode=RTC", "Read 2026-11-15 in the official statute: additional 1% tax applies to taxable income above $1,000,000 for taxable years beginning on or after January 1, 2005; the statutory threshold is not indexed in the section text."),
    "ftb_540es": ("FTB — 2025 Form 540-ES instructions", "https://www.ftb.ca.gov/forms/2025/2025-540-es-instructions.html", "2025 estimated-tax worksheet; use the Form 540 instructions and current-year law for final return treatment."),
    "ftb_cap_gains": ("FTB — Capital gains and losses", "https://www.ftb.ca.gov/file/personal/income-types/capital-gains-and-losses.html", "Read 2026-11-15 (page updated 2026-01-28): California has no lower capital-gains rate; capital gains are taxed as ordinary income."),
    "ftb_gifts": ("FTB — Gifts and inheritance", "https://www.ftb.ca.gov/file/personal/income-types/gifts-and-inheritance.html", "Official FTB information about gifts and inheritances; read 2026-11-15. The page does not establish the basis or tax consequences of an individual transfer."),
    "boe_counties": ("California BOE — County assessor contacts", "https://www.boe.ca.gov/proptaxes/countycontacts.htm", "Official directory of county assessor offices; it lists contacts, not property-specific tax rates or assessments."),
    "sos_measures": ("California Secretary of State — Qualified ballot measures", "https://www.sos.ca.gov/elections/ballot-measures/qualified-ballot-measures", "Official ballot-measure list; full text and certified results must be checked separately."),
    "hud_fmr": ("HUD — Fair Market Rents", "https://www.huduser.gov/portal/datasets/fmr.html", "Housing-program benchmark methodology; not an appraisal, lawful rent, or current lease amount."),
    "irs_topic409": ("IRS Topic no. 409 — Capital gains and losses", "https://www.irs.gov/taxtopics/tc409", "Long-term capital-gain rate structure and the maximum 25% federal rate on unrecaptured section 1250 gain from depreciated real property; an individual's rates depend on filing facts."),
    "irs_sched_d": ("IRS — Instructions for Schedule D (Form 1040)", "https://www.irs.gov/instructions/i1040sd", "Defines unrecaptured section 1250 gain for real property depreciated and held more than one year, and provides the line worksheet; it does not compute a private depreciation schedule."),
    "irs_1031_tips": ("IRS — Like-kind exchanges (real estate tax tips)", "https://www.irs.gov/businesses/small-businesses-self-employed/like-kind-exchanges-real-estate-tax-tips", "Section 1031 applies to real property held for business or investment; a primary residence and property held mainly for sale do not qualify; exchanges involve qualified-intermediary mechanics, deadlines, taxable boot and Form 8824 reporting."),
    "ca_rtc27388": ("California statute — property-tax exclusion claims", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=27388.&lawCode=RTC", "Claim filing periods, late-claim procedures and statutory limits on county fees for qualifying family-transfer exclusion claims; applicability depends on the transfer facts."),
}

PAGES = [
    ("index.html", "Decision overview", "Start"),
    ("pages/executive-summary.html", "Executive summary", "Start"),
    ("pages/decision-analysis.html", "Compare paths", "Decision"),
    ("pages/questions.html", "Questions & missing evidence", "Decision"),
    ("pages/requirements-tracker.html", "Requirements tracker", "Decision"),
    ("pages/suggestions.html", "Suggestions for review", "Decision"),
    ("pages/property-profiles.html", "Rounded figure workbook", "Private planning"),
    ("pages/operating-costs.html", "Costs & coverage", "Private planning"),
    ("pages/projections.html", "Projection worksheet", "Private planning"),
    ("pages/property-tax.html", "Property-tax rules", "Law & process"),
    ("pages/inheritance-process.html", "Deadline timeline", "Law & process"),
    ("pages/estate-thresholds.html", "Estate-tax thresholds", "Law & process"),
    ("pages/law-watchlist.html", "Law watchlist", "Law & process"),
    ("pages/black-swan.html", "Black-swan conditions", "Stress tests"),
    ("pages/phased-investing.html", "Treasury staging tool", "Stress tests"),
    ("pages/investment-policy.html", "Investment policy draft", "Stress tests"),
    ("pages/attorney-cpa-brief.html", "Attorney & CPA brief", "Adviser & evidence"),
    ("pages/decision-log.html", "Decision log", "Adviser & evidence"),
    ("pages/flagged-for-review.html", "Flagged for review", "Adviser & evidence"),
    ("pages/glossary.html", "Glossary", "Adviser & evidence"),
    ("pages/sources.html", "Official source register", "Adviser & evidence"),
    ("pages/privacy.html", "Privacy & limits", "Adviser & evidence"),
]

STATUS = {"rule": "Verified rule", "historical": "Historical", "guidance": "Guidance", "missing": "Missing", "unverified": "Not verified", "assumption": "Assumption", "reference": "Official reference"}

def esc(value: object) -> str:
    return html.escape(str(value), quote=True)

def badge(status: str) -> str:
    cls = status.lower().replace(" ", "-")
    return f'<span class="badge {esc(cls)}">{esc(status)}</span>'

def source_link(key: str) -> str:
    label, url, scope = SOURCES[key]
    return f'<a class="source" href="{esc(url)}" title="{esc(scope)}" rel="noopener noreferrer">{esc(label)}</a>'

def sources(keys: list[str]) -> str:
    return " <span aria-hidden=\"true\">·</span> ".join(source_link(key) for key in keys)

def table(caption: str, headers: list[str], rows: list[tuple[list[str], str, list[str]]]) -> str:
    out = [f'<div class="table-scroll" tabindex="0"><table><caption>{esc(caption)}</caption><thead><tr>']
    out += [f'<th scope="col">{esc(h)}</th>' for h in headers]
    out.append('<th scope="col">Evidence</th><th scope="col">Official source / scope</th></tr></thead><tbody>')
    for cells, status, refs in rows:
        out.append('<tr>')
        out += [f'<td>{esc(cell)}</td>' for cell in cells]
        out.append(f'<td>{badge(status)}</td><td>{sources(refs)}</td></tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)

def prose(title: str, text: str, kind: str = "") -> str:
    return f'<section class="prose"><h2>{esc(title)}</h2><p class="{esc(kind)}">{esc(text)}</p></section>'

def callout(title: str, text: str, kind: str = "info") -> str:
    return f'<aside class="callout {esc(kind)}"><strong>{esc(title)}</strong><p>{esc(text)}</p></aside>'


# =============================================================================
# Rounded scenario model
# -----------------------------------------------------------------------------
# Every published amount is rounded to the nearest ten dollars: that keeps the
# arithmetic checkable by hand and stops an exact-match search from tying a
# printed figure back to a public record. Identifiers - locality, parcel,
# account, party names - are never part of this model, and no file is read: the
# values below are the household's own rounded report, entered as scenario
# inputs. Assumption rates are labelled on every page that prints them, and any
# figure no official source supports is flagged rather than invented.
# =============================================================================

def r10(value: float) -> int:
    # Half away from zero, so the rounding policy is deterministic rather than
    # dependent on the platform's banker's-rounding behaviour at a tie.
    sign = -1 if value < 0 else 1
    return sign * (int(abs(value) / 10.0 + 0.5) * 10)

def usd(value: float) -> str:
    rounded = r10(value)
    if rounded == 0:
        return "no modeled amount"
    return ("-" if rounded < 0 else "") + "$" + format(abs(rounded), ",")

def signed_usd(value: float) -> str:
    rounded = r10(value)
    if rounded == 0:
        return "no modeled difference"
    return ("plus $" if rounded > 0 else "minus $") + format(abs(rounded), ",")

def millions(value: float) -> str:
    return f"{value / 1_000_000:.1f}"

def pct(value: float, digits: int = 2) -> str:
    return f"{value * 100:.{digits}f}%"

def row(cells: list, status: str, refs: list) -> tuple:
    return (cells, STATUS[status], refs)

A_MARKET_2026 = 3_100_000
A_ASSESSED_2026 = 550_540
B_MARKET_2026 = 1_800_000
B_ASSESSED_2025 = 114_250
A_BILL_HISTORY = [
    (2026, 0, 550_540), (2025, 7_210, 539_740), (2024, 7_000, 529_160),
    (2023, 6_920, 518_790), (2022, 6_760, 508_610), (2021, 6_660, 498_640),
    (2020, 6_570, 493_530), (2019, 6_570, 483_850), (2018, 6_380, 474_370),
    (2017, 6_380, 465_070), (2016, 6_410, 455_950), (2015, 6_130, 449_100),
    (2014, 5_970, 440_310),
]
B_BILL_HISTORY = [
    (2025, 2_440, 114_250), (2024, 2_320, 112_010), (2023, 2_180, 109_810),
    (2022, 2_110, 107_660), (2021, 2_070, 105_600), (2020, 2_200, 104_510),
    (2019, 2_130, 102_470), (2018, 2_060, 100_460), (2017, 1_740, 98_490),
    (2016, 1_680, 96_560),
]
B_RENT_TWO_UNITS_MONTH = 3_575
B_THIRD_UNIT_MONTH = 3_575
A_WATER_MONTH = (100, 130, 150)
A_SOLAR_CREDIT_MONTH = (0, 15, 20)
B_WATER_MONTH = (330, 365, 400)
B_ELEC_MONTH = (30, 50, 70)
INSURANCE_A_YEAR = (1_200, 1_800, 3_000)
INSURANCE_B_YEAR = (2_400, 3_600, 6_000)
MAINTENANCE_A_YEAR = (3_000, 6_000, 12_000)
CAPITAL_A_YEAR = (4_000, 8_000, 15_000)
MAINTENANCE_B_YEAR = (8_000, 12_000, 20_000)
CAPITAL_B_YEAR = (10_000, 15_000, 25_000)
GROWTH_HOME = {"soft": 0.010, "baseline": 0.030, "long-run": 0.0428}
GROWTH_COST = 0.030
GROWTH_PROP13 = 0.020
GROWTH_CAP = 0.0215   # one year of the published California index change, applied at each biennial adjustment
RENT_GROSS_YIELD = 0.032
VACANCY = 0.04
MANAGEMENT = 0.04
PORTFOLIO_RETURN = {"soft": 0.030, "baseline": 0.060, "strong": 0.080}
PORTFOLIO_TAX_DRAG = {"soft": 0.003, "baseline": 0.006, "strong": 0.008}
TREASURY_YIELD = 0.035
FRICTIONS = 0.060
TRANSFER_TAX_RATE = 0.0011
RECORDING_FLAT = 220
LAND_SHARE = 0.20
DEPRECIATION_YEARS = 27.5
EXIT_COMBINED = 0.371
RECAPTURE_COMBINED = 0.383
SECTION_121_EXCLUSION = 250_000
BOE_CAP = 1_044_586
TRANSFER_YEAR = 2045
SELL_LABEL = "Sell in the transfer year, invest at once"
RENT_LABEL = "Keep it, rent it out, sell at the horizon"
LIVE_LABEL = "Live in it with an exclusion claim, sell at the horizon"

def effective_rate(history: list) -> float:
    pairs = [(tax / assessed) for (_, tax, assessed) in history if tax and assessed]
    return sum(pairs) / len(pairs)

def rate_range(history: list) -> tuple:
    pairs = sorted([(tax / assessed) for (_, tax, assessed) in history if tax and assessed])
    return pairs[0], pairs[-1]

RATE_A = effective_rate(A_BILL_HISTORY)
RATE_B = effective_rate(B_BILL_HISTORY)
RATE_A_LOW, RATE_A_HIGH = rate_range(A_BILL_HISTORY)
RATE_B_LOW, RATE_B_HIGH = rate_range(B_BILL_HISTORY)

def grown(start: float, rate: float, years: float) -> float:
    return start * (1.0 + rate) ** years

def market_value(year: int, growth: float = None) -> float:
    return grown(A_MARKET_2026, GROWTH_HOME["baseline"] if growth is None else growth, year - 2026)

def assessed_untransferred(year: int) -> float:
    return grown(A_ASSESSED_2026, GROWTH_PROP13, year - 2026)

def boe_cap(year: int) -> float:
    """The published amount, grown by one index change at each February adjustment.

    The limit is adjusted every other February, not annually, so the number of
    steps is counted in two-year intervals from the window that began in
    2025; a plan for a later year should read the amount in force then.
    """
    adjustments = max(0, (year - 2025) // 2)
    return grown(BOE_CAP, GROWTH_CAP, adjustments)

def assessed_at_transfer(year: int, branch: str, growth: float = None) -> float:
    base = assessed_untransferred(year)
    value = market_value(year, growth)
    if branch == "keep-base":
        return base
    if branch == "prop19":
        return base + max(0.0, value - (base + boe_cap(year)))
    return value

def assessed_later(transfer_year: int, year: int, branch: str, growth: float = None) -> float:
    return grown(assessed_at_transfer(transfer_year, branch, growth), GROWTH_PROP13, year - transfer_year)

def tax_bill(transfer_year: int, year: int, branch: str, growth: float = None, rate: float = None) -> float:
    return assessed_later(transfer_year, year, branch, growth) * (RATE_A if rate is None else rate)

def cost_item(amount: float, year: int) -> float:
    return grown(amount, GROWTH_COST, year - 2026)

def carrying_cost(year: int, transfer_year: int, branch: str, growth: float = None, which: str = "A") -> dict:
    if which == "A":
        return {
            "Property tax": tax_bill(transfer_year, year, branch, growth),
            "Insurance": cost_item(INSURANCE_A_YEAR[1], year),
            "Water and sewer": cost_item(A_WATER_MONTH[1] * 12, year),
            "Routine maintenance": cost_item(MAINTENANCE_A_YEAR[1], year),
            "Capital reserve": cost_item(CAPITAL_A_YEAR[1], year),
            "Solar export credit": -cost_item(A_SOLAR_CREDIT_MONTH[1] * 12, year),
        }
    return {
        "Property tax": grown(B_ASSESSED_2025, GROWTH_PROP13, year - 2025) * RATE_B,
        "Insurance (landlord policy)": cost_item(INSURANCE_B_YEAR[1], year),
        "Water and sewer (three units)": cost_item(B_WATER_MONTH[1] * 12, year),
        "Shared electricity": cost_item(B_ELEC_MONTH[1] * 12, year),
        "Routine maintenance": cost_item(MAINTENANCE_B_YEAR[1], year),
        "Capital reserve": cost_item(CAPITAL_B_YEAR[1], year),
    }

def carrying_total(year: int, transfer_year: int, branch: str, growth: float = None, which: str = "A") -> float:
    return sum(carrying_cost(year, transfer_year, branch, growth, which).values())

def rent_income(year: int, growth: float = None) -> tuple:
    gross = market_value(year, growth) * RENT_GROSS_YIELD
    return gross, gross * (1 - VACANCY)

def third_unit_rent(year: int) -> float:
    return grown(B_THIRD_UNIT_MONTH * 12, GROWTH_COST, year - 2026) * (1 - VACANCY - MANAGEMENT)

def annual_depreciation(transfer_year: int, growth: float = None) -> float:
    return market_value(transfer_year, growth) * (1 - LAND_SHARE) / DEPRECIATION_YEARS

def sale_net(value: float, basis: float, depreciation: float = 0.0, exclusion: float = 0.0) -> dict:
    frictions = value * FRICTIONS
    transfer_tax = value * TRANSFER_TAX_RATE
    net = value - frictions - transfer_tax - RECORDING_FLAT
    gain = max(0.0, net - basis)
    recapture = min(depreciation, gain)
    taxable = max(0.0, gain - recapture - exclusion)
    tax = recapture * RECAPTURE_COMBINED + taxable * EXIT_COMBINED
    return {"value": value, "frictions": frictions, "transfer_tax": transfer_tax, "net": net,
            "gain": gain, "recapture": recapture, "tax": tax, "after_tax": net - tax}

def net_rate(rate_key: str) -> float:
    return PORTFOLIO_RETURN[rate_key] - PORTFOLIO_TAX_DRAG[rate_key]

def compound(amount: float, rate_key: str, years: float) -> float:
    return amount * (1 + net_rate(rate_key)) ** max(0.0, years)

def live_stream(transfer_year: int, end_year: int, growth: float, rate_key: str, live_branch: str) -> float:
    total = 0.0
    for year in range(transfer_year + 1, end_year + 1):
        costs = carrying_total(year, transfer_year, live_branch, growth, "A")
        total += (third_unit_rent(year) - costs) * (1 + net_rate(rate_key)) ** (end_year - year)
    return total

def rent_stream(transfer_year: int, end_year: int, growth: float, rate_key: str) -> tuple:
    cash, basis_used = 0.0, 0.0
    depreciation = annual_depreciation(transfer_year, growth)
    for year in range(transfer_year + 1, end_year + 1):
        gross, collected = rent_income(year, growth)
        costs = carrying_total(year, transfer_year, "reassessed", growth, "A") + gross * MANAGEMENT
        operating = collected - costs
        claimed = min(depreciation, max(0.0, operating))
        basis_used += depreciation
        tax = max(0.0, operating - claimed) * EXIT_COMBINED
        cash += (operating - tax) * (1 + net_rate(rate_key)) ** (end_year - year)
    return cash, basis_used

def path_outcomes(transfer_year: int = None, horizon: int = 2070, growth: float = None, rate_key: str = "baseline", live_branch: str = "prop19") -> dict:
    start = TRANSFER_YEAR if transfer_year is None else transfer_year
    g = GROWTH_HOME["baseline"] if growth is None else growth
    value_t = market_value(start, g)
    rows = {}
    sell = sale_net(value_t, value_t)
    rows[SELL_LABEL] = {"value": compound(sell["after_tax"], rate_key, horizon - start), "detail": "the modeled contract price equals the stepped-up basis, so the gain is close to zero"}
    parked = sell["after_tax"] * (1 + TREASURY_YIELD) ** 2.5
    rows["Sell, park 30 months in Treasuries, then buy"] = {"value": compound(parked, rate_key, horizon - start - 2.5), "detail": "three-month to two-year rungs, then one purchase at month 30"}
    monthly = sum((sell["after_tax"] / 30) * (1 + net_rate(rate_key)) ** (horizon - start - month / 12) for month in range(1, 31))
    rows["Sell, buy in thirty equal monthly tranches"] = {"value": monthly, "detail": "each tranche earns from its own purchase month"}
    rent_cash, basis_used = rent_stream(start, horizon, g, rate_key)
    rented = sale_net(market_value(horizon, g), value_t - basis_used, depreciation=basis_used)
    rows[RENT_LABEL] = {"value": rented["after_tax"] + rent_cash, "detail": "a let home cannot claim the family-home exclusion, so it is reassessed"}
    lived = sale_net(market_value(horizon, g), value_t, exclusion=SECTION_121_EXCLUSION)
    rows[LIVE_LABEL] = {"value": lived["after_tax"] + live_stream(start, horizon, g, rate_key, live_branch), "detail": "the third unit of the owned building is let instead of occupied"}
    lived_no_claim = sale_net(market_value(horizon, g), value_t)
    rows["Live in it, but no valid exclusion claim"] = {"value": lived_no_claim["after_tax"] + live_stream(start, horizon, g, rate_key, "reassessed"), "detail": "reassessed at fair cash value from the transfer year onward"}
    five_live = compound(live_stream(start, start + 5, g, rate_key, live_branch) + sale_net(market_value(start + 5, g), value_t, exclusion=SECTION_121_EXCLUSION)["after_tax"], rate_key, horizon - start - 5)
    rows["Live in it five years, sell with an exclusion, invest"] = {"value": five_live, "detail": "occupy 2045 to 2050, then sell and reinvest the proceeds"}
    five_cash, five_basis = rent_stream(start, start + 5, g, rate_key)
    five_exit = sale_net(market_value(start + 5, g), value_t - five_basis, depreciation=five_basis)
    rows["Rent it five years, sell, invest"] = {"value": compound(five_cash + five_exit["after_tax"], rate_key, horizon - start - 5), "detail": "depreciation reduces basis and raises the later recapture"}
    return rows

def ranked_rows(transfer_year: int = None, horizon: int = 2070, growth: float = None, rate_key: str = "baseline") -> list:
    rows = path_outcomes(transfer_year, horizon, growth, rate_key)
    lead = rows[SELL_LABEL]["value"]
    ordered = sorted(rows.items(), key=lambda item: -item[1]["value"])
    return [(label, data["value"], data["value"] - lead, data["detail"]) for label, data in ordered]

def break_even_growth(name: str, transfer_year: int = None, horizon: int = 2070, rate_key: str = "baseline") -> float:
    lo, hi = 0.0, 0.25
    for _ in range(34):
        mid = (lo + hi) / 2
        rows = path_outcomes(transfer_year, horizon, mid, rate_key)
        lo, hi = (mid, hi) if rows[name]["value"] - rows[SELL_LABEL]["value"] < 0 else (lo, mid)
    return (lo + hi) / 2

def index_path(months: int, decline_pct: float, decline_months: int, recover_month: int = None, drift: float = 0.0) -> list:
    floor = 1 - decline_pct / 100
    levels = []
    for month in range(months + 1):
        if decline_months == 0 or decline_pct == 0:
            level = 1.0
        elif month <= decline_months:
            level = 1 - (decline_pct / 100) * (month / decline_months)
        elif recover_month and month <= recover_month:
            level = floor + (1 - floor) * ((month - decline_months) / max(1, recover_month - decline_months))
        else:
            level = 1.0 if recover_month else floor
        levels.append(max(level, 0.02) * (1 + drift) ** (month / 12))
    return levels

def staging_outcome(amount: float, levels: list, months: int, strategy: tuple) -> float:
    kind = strategy[0]
    if kind == "now":
        return amount * levels[months] / levels[0]
    if kind == "park":
        window = strategy[1]
        cash = amount * (1 + TREASURY_YIELD / 12) ** window
        return cash * levels[months] / levels[window]
    window = strategy[1]
    cash, units = amount, 0.0
    for month in range(1, window + 1):
        cash = cash * (1 + TREASURY_YIELD / 12) - amount / window
        units += (amount / window) / levels[month]
    return units * levels[months] + cash * (1 + TREASURY_YIELD / 12) ** max(0, months - window)

STAGING_SHAPES = [
    ("A fall of about 89 percent over 34 months, then no recovery within ten years", 120, 89, 34, None, 0.0),
    ("The same fall, with the prior high regained at month 302", 302, 89, 34, 302, 0.0),
    ("A fall of about 57 percent over 17 months, then no recovery within ten years", 120, 57, 17, None, 0.0),
    ("The same fall, with the prior high regained by month 120 (assumed window)", 120, 57, 17, 120, 0.0),
    ("No fall at all: prices drift up 6 percent a year for ten years", 120, 0, 0, None, 0.06),
]
STAGING_STRATEGIES = [
    ("Buy the whole amount in month one", ("now",)),
    ("Park 24 months, then buy", ("park", 24)),
    ("Park 36 months, then buy", ("park", 36)),
    ("Buy in equal monthly tranches over 24 months", ("dca", 24)),
    ("Buy in equal monthly tranches over 36 months", ("dca", 36)),
]

def bar_chart(items: list, note: str) -> str:
    if not items:
        return ""
    scale = max(abs(value) for _, value, _ in items) or 1
    parts, y = [], 26
    for label, value, kind in items:
        width = max(2, int(abs(value) / scale * 190))
        fill = "#146269" if kind == "lead" else ("#a4541c" if kind == "behind" else "#6b7280")
        parts.append(f'<rect x="206" y="{y - 11}" width="{width}" height="14" rx="3" fill="{fill}"/>'
                     f'<text x="202" y="{y}" text-anchor="end" class="chart-label">{esc(label)}</text>'
                     f'<text x="{210 + width}" y="{y}" class="chart-value">{millions(value)}</text>')
        y += 24
    height = y + 14
    return ('<figure class="chart"><svg viewBox="0 0 620 ' + str(height) + '" role="img" aria-label="Bars showing net position by path in millions of dollars">'
            + "".join(parts) + '<text x="8" y="' + str(height - 2) + '" class="chart-note">' + esc(note) + "</text></svg></figure>")

def waterfall_chart(steps: list) -> str:
    total = steps[0][1] or 1
    parts, x = [], 8
    for index, (label, amount) in enumerate(steps):
        share = max(0.0, amount) / total
        width = max(8, int(share * 560))
        shade = "#146269" if index in (0, len(steps) - 1) else "#a4541c"
        parts.append(f'<rect x="{x}" y="10" width="{width}" height="24" fill="{shade}"/>'
                     f'<text x="8" y="{58 + index * 16}" class="chart-note">{esc(label)}: {usd(amount)}</text>')
        x += width
    height = 58 + len(steps) * 16
    return ('<figure class="chart"><svg viewBox="0 0 620 ' + str(height) + '" role="img" aria-label="How modeled sale proceeds are divided">'
            + "".join(parts) + "</svg></figure>")

def projection_rows(years: list) -> list:
    rows = []
    for year in years:
        g = GROWTH_HOME["baseline"]
        cells = [str(year), usd(market_value(year, GROWTH_HOME["soft"])), usd(market_value(year, g)), usd(market_value(year, GROWTH_HOME["long-run"])),
                 usd(assessed_untransferred(year)), usd(tax_bill(TRANSFER_YEAR, year, "keep-base", g)),
                 usd(assessed_at_transfer(TRANSFER_YEAR, "prop19", g)), usd(tax_bill(TRANSFER_YEAR, year, "prop19", g)),
                 usd(assessed_at_transfer(TRANSFER_YEAR, "reassessed", g)), usd(tax_bill(TRANSFER_YEAR, year, "reassessed", g))]
        rows.append(row(cells, "assumption", ["ca_rtc51", "boe_prop19", "ca_rtc63"]))
    return rows

MODEL_NOTE = "Model figures computed 2026-11-17 from labelled assumptions and the household's rounded report; re-run with the owner's written records before relying on any of them."

def content_for(path: str) -> tuple[str, str, str]:
    """Return heading, lead, body for each public page; no case data is used."""
    if path == "index.html":
        body = callout("Figures are published rounded; identifiers are not", "The analysis below ranks the modeled paths on the household's own rounded report, because a ranking that shows no numbers cannot be checked. Amounts are rounded to the nearest ten dollars and labelled as assumptions where an official source does not establish them, while locality, parcel, account and party identifiers stay out of this repository entirely. Exact records belong in a private workpaper, and nothing here is legal, tax or investment advice.", "warning")
        body += '<aside class="callout warning"><strong>Urgent privacy notice: historical exposure is unresolved</strong><p>The current site is generalized, but prior commits, pull-request views, forks, caches, downloads, or clones may retain older public material. This cleanup does not prove that historical copies are erased. Repository administrators must assess and coordinate any history remediation; do not upload private case records here. <a class="source" href="https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository" title="GitHub guidance on sensitive data in repository history and limits of remediation." rel="noopener noreferrer">GitHub Docs — removing sensitive data</a> · <a href="pages/privacy.html">Privacy &amp; limits</a></p></aside>'
        body += table("What would change the answer?", ["Decision-changing fact", "Current state", "Evidence needed"], [
            (["Trust, title, timing, debt", "Not available in this public project.", "Executed trust and deed; trustee authority; distribution date; debts and reserves."], STATUS["missing"], ["ca_prob", "ca_rtc480"]),
            (["Property-tax exclusion eligibility", "Cannot determine without family relationship, transferor use, title, value, occupancy and claim facts." , "Written eligibility review; confirm whether long-term occupancy is actually intended."], STATUS["missing"], ["boe_prop19", "ca_rtc63"]),
            (["After-tax sale / rent / keep comparison", "No property values, basis, rent, expenses, or tax returns are published." , "Independent date-of-death appraisal; private basis schedule; leases; expense records; sale-cost bids."], STATUS["missing"], ["irs_basis", "irs_rental", "irs_pub551"]),
            (["Where the household will live", "A separately owned residence and tenant obligations may alter every path; details are intentionally withheld." , "Written occupancy plan and counsel review of lease and local rules."], STATUS["missing"], ["irs_rental", "ca_rent"]),
            (["Estate-level liquidity / federal filing", "A home value alone cannot establish estate tax exposure." , "Full confidential estate inventory, adjusted taxable gifts, marital/portability facts and liquidity needs."], STATUS["missing"], ["irs_estate", "irs_estate_faq"]),
        ])
        body += prose("Safe decision order", "Set the family's written decision rules before seeing a forecast. Confirm trust and title, get independent values, establish tax basis and assessed-value treatment, validate use and leases, price recurring costs, then compare every path at the same dates and horizon. Keep all private inputs in a locally controlled, non-public workpaper.")
        body += prose("Conditional fork", "If a qualifying heir intends to occupy the transferred home as a principal residence long-term, test the Proposition 19 family-home exclusion and its deadlines. If not, model the reassessed tax branch and compare rental, sale, or mixed paths. No branch can be chosen from public facts alone.")
        return "Decision overview", "Official rules linked by source, household figures published only as rounded scenario inputs, and identifiers withheld.", body
    if path.endswith("executive-summary.html"):
        body = callout("Executive takeaway", "On the published rounded inputs the ranking is computed below, and it is a computation rather than a conclusion: separate the estate-tax, income-tax basis and property-tax assessment questions, obtain the independent evidence named on the questions page, and re-run the model before treating any line as settled.", "warning")
        body += table("What is established vs. not established", ["Topic", "Established by official source", "Still needs private evidence"], [
            (["Federal estate tax", "Current filing threshold is determined for the year of death and uses an estate-level test, not a per-heir allowance.", "Gross estate, adjusted taxable gifts, deductions, marital/portability history."], STATUS["rule"], ["irs_estate", "irs_estate_faq"]),
            (["Inherited basis", "General federal rule is date-of-death fair market value, subject to exceptions and reporting rules.", "Written date-of-death appraisal, improvements, depreciation, trust and estate records."], STATUS["rule"], ["irs_basis", "irs_pub551"]),
            (["Property-tax assessment", "California rules include Proposition 13 and a conditional Proposition 19 family-home exclusion.", "Eligibility, current roll, direct assessments, transfer status, claim and occupancy."], STATUS["rule"], ["boe_prop19", "ca_rtc63", "ca_rtc51"]),
            (["Operating costs", "Official agencies publish rules and tools, not a private property's current insurance/repair/utility cost.", "Written insurance quotes, recent bills, inspection and five-year capital plan."], STATUS["guidance"], ["cdi", "cslb"]),
        ])
        body += prose("Recommendation standard", "Do not call a projection the best plan until it includes the same tax year and horizon for all alternatives; the full sale-cost waterfall (transaction costs, documentary transfer tax, recording fees, sale-year income tax including unrecaptured section 1250 gain and the California 1% add-on above $1,000,000 of taxable income); any like-kind-exchange decision; debt; occupancy; rental legality; vacancy; capital costs; utilities; insurance; estate liquidity; and reinvestment risk.")
        return "Executive summary", "The computed ranking on rounded inputs, the switch that reverses it, and the evidence still outstanding.", body
    if path.endswith("decision-analysis.html"):
        rows = [
            (["Live in inherited home", "Model eligible occupancy and exclusion, all carrying costs, utilities, imputed rent / avoided rent, and the value of housing received." , "Occupancy eligibility, household preference, private values and expenses."], STATUS["missing"], ["boe_prop19", "ca_rtc63", "ca_rtc218"]),
            (["Rent inherited home", "Model lawful rent, vacancy, operating costs, depreciation, recapture, management, income tax and property-tax reassessment." , "Comparable rents, unit status, leases, costs, basis and local law."], STATUS["missing"], ["irs_rental", "ca_rent", "hud_fmr"]),
            (["Sell in transfer tax year", "Separate date-of-death basis from assessed value; include sale costs, applicable transfer tax, recording fees, gain, exclusions and the sale tax year." , "Appraisal, basis, sale contract, official local fee schedule, closing statement and tax advice."], STATUS["guidance"], ["irs_basis", "irs_121", "irs_pub551", "ca_rtc11911", "ca_gov27361"]),
            (["Sell later / occupy then sell", "Test the home-sale exclusion use period and interim costs; treat later conversion and Prop 19 status as separate legal questions." , "Move dates, principal-residence evidence, basis and written property-tax advice."], STATUS["guidance"], ["irs_121", "boe_prop19", "ca_rtc63"]),
            (["Mixed paths", "Test live-then-rent, rent-then-sell, partial sale/retention, or retain one property while changing use of another." , "Property-specific use, tenant rights, finance, tax and transition costs."], STATUS["guidance"], ["irs_rental", "irs_1041", "ca_rent"]),
            (["Sell and reinvest", "Compare immediate investment, phased entry, cash/Treasury reserves, taxes, fees and a written investment policy." , "Net proceeds, time horizon, liquidity floor, risk tolerance and policy statement."], STATUS["guidance"], ["treasury_bills", "treasury_notes", "sec_stocks"]),
        ]
        body = table("Compare alternatives at identical dates and horizons", ["Path", "Required model treatment", "Evidence gap"], rows)
        body += prose("Comparison rule", "Use the same transfer date, valuation date, after-tax horizon, inflation basis, and household housing need for every path. Show annual cash-flow ranges as well as terminal wealth, and label assumptions rather than presenting them as facts.")
        body += prose("Write the rules before the results", "Before any forecast arrives, document what would make the household choose each path: minimum liquidity, maximum acceptable maintenance risk, desired occupancy, rental obligations, tax eligibility, acceptable drawdown, and conditions that trigger a sale.")
        body += callout("Model first: a sale in the transfer tax year", "Model a sale in the inheritance tax year first, not as a tax-free assumption. Inherited basis is generally tied to date-of-death fair market value, but sale price, timing and allowable selling costs can differ from that value; a transfer-year sale does not automatically produce zero gain or loss. Verify the appraisal, amount realized and tax-year rules. Compare the after-tax proceeds with housing costs and reinvestment risk.", "info")
        body += table("Sale proceeds waterfall — the order in which a sale pays out", ["Layer", "Framework and the modeled figure", "Rule or schedule source"], [
            (["Gross sale value", "Contract price at the sale date; get an independent valuation rather than an online estimate.", "Private appraisal and sale contract."], STATUS["guidance"], ["irs_basis", "irs_pub551"]),
            (["Sale transaction costs", "Broker, escrow, title, repair credits and concessions, as bid in writing; label the percentage assumption used in any comparison.", "Written bids and the closing statement."], STATUS["guidance"], ["irs_pub551"]),
            (["Documentary transfer tax", "California authorizes a documentary transfer tax computed on value in stated increments; the applicable rate is set by the local jurisdiction and must be read from the property's own official schedule at sale.", "Statewide authority and the local recorder's enacted schedule."], STATUS["rule"], ["ca_rtc11911", "ca_gov27361"]),
            (["Recording fees", "Statutory per-page and per-title recording charges, plus statewide add-on fees, apply at recording; the actual total depends on the document and the county schedule.", "Statewide fee statute and the property's county recorder schedule."], STATUS["rule"], ["ca_gov27361"]),
            (["Sale-year income tax", "Inherited basis is generally tied to date-of-death fair market value, but a sale in the transfer year is not automatically tax-free: the result depends on sale proceeds, allowable selling expenses, basis evidence and exceptions. Later appreciation and rental depreciation can also affect gain; unrecaptured section 1250 gain is federally taxed at a maximum 25% rate. A high-income year can add California's 1% tax above the taxable-income threshold.", "CPA computes from private basis and depreciation records, using the Form 540 instructions for the actual tax year."], STATUS["rule"], ["irs_basis", "irs_topic409", "irs_sched_d", "ca_rtc17043", "ftb_540", "ftb_cap_gains"]),
            (["Net proceeds to invest or reinvest", "What remains after every layer above; compare paths only on this figure, not on gross value.", "Closing statement and CPA summary."], STATUS["guidance"], ["irs_pub551", "irs_1031_tips"]),
        ])
        body += table("Tax overlays and structural decisions to price before choosing", ["Overlay", "What to decide or compute", "Source"], [
            (["Depreciation and unrecaptured section 1250 recapture", "For any rental path, reconcile depreciation allowed or allowable; the recapture portion is federally taxed at a maximum 25% rate and California treats gains as ordinary income.", "IRS Topic 409 and the Schedule D worksheet; CPA schedule."], STATUS["rule"], ["irs_topic409", "irs_sched_d", "ftb_cap_gains"]),
            (["Like-kind exchange (section 1031)", "Decide in writing before listing: an exchange can defer gain on business or investment real property only, needs a qualified intermediary and statutory deadlines, never applies to a primary residence or property held mainly for sale, and leaves the replacement with carryover basis.", "IRS like-kind exchange guidance; tax counsel memo."], STATUS["rule"], ["irs_1031", "irs_1031_tips"]),
            (["Main-home exclusion switch", "For a live-then-sell path, track the ownership and use periods separately; a conversion to rental changes the analysis and can interact with property-tax status.", "IRS Topic 701; written property-tax advice."], STATUS["rule"], ["irs_121", "boe_prop19", "ca_rtc63"]),
            (["California 1% additional tax on high taxable income", "The 2025 Form 540 line 62 instructions compute a 1% tax on taxable income above $1,000,000; the current statutory threshold is not indexed in the section text. This is income tax, not an inheritance tax. Recheck the actual sale-year law and return instructions.", "Current statute and 2025 Form 540 line 62 instructions; verify later-year instructions when available."], STATUS["rule"], ["ca_rtc17043", "ftb_540", "ftb_cap_gains"]),
            (["Local vacancy-tax exposure", "Some jurisdictions tax units vacant beyond a statutory period; at least one such measure has had enforcement barred by litigation. Confirm the property's own current ordinance before planning an empty unit.", "Election authority for the measure; the property's tax authority."], STATUS["unverified"], ["sos_measures"]),
            (["Estate liquidity timing", "If a federal return may be required, taxes and expenses are due on a calendar that does not wait for a real-estate sale; price funding routes early.", "IRS filing guidance; CPA liquidity plan."], STATUS["rule"], ["irs_706", "irs_estate_faq"]),
        ])
        body += '<section class="prose"><h2>Local-only sale-tax overlay tool</h2><p>Enter generic assumptions to see how sale value, basis, assumed sale costs, a main-home exclusion, and the California 1% add-on interact. A transfer-year sale is not assumed to have zero gain: the illustration calculates sale value less entered costs and basis. The separate transfer-tax estimate is not netted in that gain formula, and recording fees, federal tax, deductions, losses and other return effects are not fully modeled. Inputs stay in browser memory only and are not stored or transmitted. This is an illustration, not a return, advice, or forecast.</p><div class="calculator"><label>Sale value at sale date ($) <input id="sell-value" type="number" min="0" step="10" inputmode="decimal" placeholder="Enter privately"></label><label>Tax basis at sale ($) <input id="sell-basis" type="number" min="0" step="10" inputmode="decimal" placeholder="Generally date-of-death value; exceptions apply"></label><label>Sale costs excluding transfer tax (%) <input id="sell-costs" type="number" min="0" max="30" step="0.5" placeholder="Enter assumption"></label><label>Local documentary transfer-tax rate (%) <input id="sell-dtt" type="number" min="0" max="10" step="0.01" placeholder="From the local enacted schedule"></label><label>Other taxable income before modeled gain ($, optional) <input id="sell-other" type="number" min="0" step="10" inputmode="decimal" placeholder="For the 1% add-on test"></label><label>Sale timing <select id="sell-timing"><option value="later">Later sale (after the transfer year)</option><option value="transfer">Sale in the transfer tax year</option></select></label><label>Main-home exclusion (section 121) <select id="sell-121"><option value="0">None claimed</option><option value="250000">Up to $250,000</option><option value="500000">Up to $500,000 (joint)</option></select></label><button id="sell-run" type="button">Run illustration</button><button id="sell-clear" type="button">Clear</button><p id="sell-result" role="status" aria-live="polite">No calculation run.</p></div></section>'
        return "Compare paths", "A fair comparison includes pure and mixed choices, on the same timeline.", body
    if path.endswith("questions.html"):
        rows = [
            (["What is actually transferring and when?", "Unknown: trust terms, amendments, trustee authority, title, debt, distribution conditions and transfer date." , "Attorney obtains and reviews executed documents; trustee confirms timeline in writing."], STATUS["missing"], ["ca_prob", "ca_rtc480"]),
            (["What is date-of-death fair market value and tax basis?", "No independent appraisal or estate basis schedule is available here." , "Obtain qualified written valuation as of date of death; reconcile improvements and depreciation with the CPA."], STATUS["missing"], ["irs_basis", "irs_pub551"]),
            (["Does the heir qualify for Proposition 19?", "Relationship, transferor occupancy, transferee occupancy, value limit and claim status are unknown." , "Counsel/assessor confirms statutory eligibility and long-term occupancy intention in writing."], STATUS["missing"], ["boe_prop19", "ca_rtc63", "boe_lta"]),
            (["What are actual rental and occupancy rights?", "Leases, permits, unit status, deposits and local rules are unavailable." , "Review every lease, lawful-use record, inspection and local ordinance with counsel."], STATUS["missing"], ["irs_rental", "ca_rent"]),
            (["What will costs be?", "Current bills, insurance terms, inspection and maintenance history are not in this public project." , "Collect multiple written insurance quotes, utility bills, contractor bids and a five-year capital plan."], STATUS["missing"], ["cdi", "cslb"]),
            (["Could federal estate tax or liquidity be material?", "No inventory, prior taxable gifts, marital or portability details are available." , "CPA/estate counsel builds a confidential estate-level calculation and liquidity plan."], STATUS["missing"], ["irs_estate", "irs_estate_faq", "irs_706"]),
            (["Is a like-kind exchange (section 1031) wanted for any rental before a sale?", "Nothing in public sources can decide this; an exchange defers gain on business or investment real property only, requires a qualified intermediary and statutory deadlines, and never applies to a primary residence." , "Decide in writing before listing anything; CPA or tax counsel drafts the exchange memo and identifies replacement-property deadlines."], STATUS["missing"], ["irs_1031", "irs_1031_tips"]), 
            (["What is the depreciation and recapture exposure on any rental?", "No depreciation schedule is available here; recapture of prior depreciation on real property is federally taxed at a maximum 25% rate, and California taxes gains as ordinary income." , "CPA reconciles depreciation allowed or allowable, basis and improvement history from private records before any sale-year estimate."], STATUS["missing"], ["irs_topic409", "irs_sched_d", "irs_pub551", "ftb_cap_gains"]), 
            (["What is meant by 'Prop H'?", "Private research on 2026-11-15 identified the official measure behind this shorthand and reviewed its current litigation status; jurisdiction and terms are intentionally withheld from this public site, and no local measure is applied to any property here." , "Confirm the measure's current status with the property's own tax authority before relying on it; the identification is recorded in the private workpaper."], STATUS["unverified"], ["sos_measures"]),
            (["What transfer tax and recording fees apply on sale?", "No amount is published because the property's jurisdiction, sale price, exemptions and recorded documents are not public or verified." , "Obtain the local official transfer-tax and recorder fee schedules and include them in the closing estimate."], STATUS["missing"], ["ca_rtc11911", "ca_gov27361"]),
            (["How are California capital gains taxed, and when does the 1% surcharge apply?", "FTB states capital gains are taxed as ordinary income. Current statute and the 2025 Form 540 line 62 instructions apply an additional 1% to the portion of taxable income above $1,000,000; this is not an inheritance tax. For sensitivity, each $10,000 of taxable income above that threshold adds $100 of this tax, before other return effects." , "CPA calculates the actual sale-year taxable income, federal and California tax, basis, exclusions and estimated-payment effects using the then-current return instructions."], STATUS["rule"], ["ca_rtc17043", "ftb_540", "ftb_540es", "ftb_cap_gains", "ftb_forms"]),
        ]
        return "Questions & missing evidence", "A decision-ready question register, with practical discovery steps.", table("Questions to close before choosing", ["Question", "Known from current public evidence", "How to discover the missing information"], rows)
    if path.endswith("requirements-tracker.html"):
        rows = [
            (["Executive summary and first-screen answer changers", "Published as an overview with the decision-changing facts on the first screen and the modeled ranking beneath them, on rounded figures only." , "Keep the first-screen evidence gates current as private records arrive."], STATUS["guidance"], ["boe_prop19", "irs_estate_faq"]),
            (["Complete list of requirements and missing information", "This page maps decision, tax, cost, legal, privacy and process requirements to current treatment and a next step." , "Update status only after the official source or private record is checked."], STATUS["guidance"], ["irs_estate", "boe_prop19"]),
            (["Privacy and prior public exposure", "No locality, parcel identifier, personal document or unrounded figure is published; the site carries rounded scenario figures only, and no case-specific advice." , "Earlier public copies may remain in Git history, PRs, forks or caches; an administrator must assess historical remediation."], STATUS["missing"], ["github_sensitive"]),
            (["Private estate and property inventory", "No inventory is stored in this repository." , "Create an encrypted private inventory of trust, deed, debt, prior gifts, basis, property tax, insurance, leases and liquidity."], STATUS["guidance"], ["irs_estate", "irs_basis", "irs_rental"]),
            (["Independent value and condition evidence", "No online estimate is treated as an appraisal or repair bid." , "Obtain written date-of-death valuation, independent rental comparables and condition inspections."], STATUS["guidance"], ["irs_basis", "hud_fmr", "cslb"]),
            (["Annual projections and scenario ranges", "The worksheet shows the formulas and now publishes year-by-year projections for three growth scenarios, on rounded inputs, with a tax-rate band and a rent-yield band." , "Use private, dated inputs; show market value, assessed value, tax, operating cash flow and uncertainty bands."], STATUS["guidance"], ["fhfa", "ca_rtc51", "cbo_long"]),
            (["Tax-rate area and published property-tax rate", "No parcel or locality is published, so no tax-rate area or property-specific rate is shown." , "Read the actual tax bill and official assessor/rate-area schedule privately; separate direct charges."], STATUS["missing"], ["boe_counties", "ca_rtc51"]),
            (["Estate tax, income-tax basis and property-tax assessment", "These are kept as separate concepts and separate evidence workstreams." , "CPA and assessor reconcile gross-estate value, income-tax basis and assessed value independently."], STATUS["guidance"], ["irs_estate", "irs_basis", "ca_rtc51"]),
            (["Proposition 19 eligibility and long-term occupancy", "Eligibility depends on relationship, transferor residence, transferee occupancy, value-limit and filing facts; no claim is assumed." , "Claim only if legal eligibility is confirmed and the heir intends to occupy long-term; get written assessor/counsel advice."], STATUS["rule"], ["boe_prop19", "ca_rtc63"]),
            (["Carry forward the Proposition 19 indexed cap", "The published cap is date-specific and changes periodically; no future cap is projected as law." , "Use the BOE amount effective on the transfer date and preserve the source notice."], STATUS["rule"], ["boe_lta", "boe_prop19"]),
            (["Sale in the same tax year as inheritance", "The comparison framework calls for a transfer-year sale case, separate from a later sale." , "CPA applies date-of-death basis, sale date, transaction charges and that year's tax rules."], STATUS["guidance"], ["irs_basis", "irs_pub551", "irs_121"]),
            (["Primary-residence exclusion for live-then-sell", "Section 121 tests ownership and use in the relevant period; a later sale is not assumed to qualify." , "Confirm occupancy timeline and eligibility before switching on the exclusion in a private model."], STATUS["rule"], ["irs_121"]),
            (["Depreciation and recapture", "Rental depreciation and disposition consequences are identified as required inputs, not estimated here." , "CPA rebuilds depreciation allowed/allowable and adjusted basis from returns and rental records."], STATUS["guidance"], ["irs_rental", "irs_pub551"]),
            (["Like-kind exchange decision", "A possible exchange is not presumed or modeled as tax-free without qualification review." , "Ask counsel/CPA before sale whether a qualifying business/investment-property exchange is desired and feasible."], STATUS["guidance"], ["irs_1031"]),
            (["Leases, lawful units and local rules", "No lease, tenant, permit, unit status or local property location is published." , "Review all leases, lawful-use records, deposits and current local rules before changing occupancy or rent."], STATUS["missing"], ["irs_rental", "ca_rent"]),
            (["Insurance, utilities, water, electricity and solar", "No premium or household bill is asserted from regional averages." , "Use current bills, tariff/interconnection documents and multiple written use-specific insurance quotes."], STATUS["guidance"], ["cdi", "cpuc_solar", "water_board"]),
            (["Imputed rent for living paths", "The comparison framework includes housing value/avoided rent as a distinct input, but no amount is assumed." , "Set a supported private rent-comparable range and show it beside cash costs."], STATUS["guidance"], ["hud_fmr", "irs_rental"]),
            (["Five-year maintenance and capital plan", "A multi-year plan is a required deliverable; no repair budget is fabricated." , "Inspect both buildings, request licensed bids, rank safety/system work and establish annual reserves."], STATUS["guidance"], ["cslb"]),
            (["Comparable rent and local landlord rules", "HUD FMR is not treated as a market rent, lawful rent or property-specific comparable." , "Obtain written comparable rents; counsel verifies unit status, lease terms, rent limits and tenant rights."], STATUS["guidance"], ["hud_fmr", "ca_rent", "irs_rental"]),
            (["Transfer tax and recording fees on a sale", "No fee total is published without jurisdiction, sale amount, exemptions and recorded-document details." , "Include official local schedules and written closing estimate in the sale path."], STATUS["missing"], ["ca_rtc11911", "ca_gov27361"]),
            (["Same dates, horizons, taxes, debt, occupancy, costs and liquidity", "The comparison rule requires the same transfer and valuation dates, after-tax horizon and complete cost categories for every path." , "Re-run all pure and mixed choices together; include debt, occupancy changes, repairs, insurance, utilities, transaction costs and liquidity."], STATUS["guidance"], ["irs_estate", "irs_rental", "cdi"]),
            (["Mixed paths beside pure choices", "Live, rent, sell, live-then-sell, rent-then-sell, and retain/change-use combinations are included in the framework." , "Only rank a mixed path after leases, eligibility, tax and transition costs are verified."], STATUS["guidance"], ["boe_prop19", "irs_rental", "irs_121"]),
            (["Black-swan conditions and 1929/2008 entry risk", "The guide distinguishes historical index drawdowns from probabilities and exposes the limits of its local-only sensitivity." , "Stress early/late crashes, inflation, deflation, housing-equity correlation, delayed recovery and lower Treasury renewal rates."], STATUS["historical"], ["fed_1929", "fed_2008", "fed_inflation", "treasury_bills"]),
            (["Tax-aware California sale sensitivity", "Official statute and FTB sources state the additional 1% above $1,000,000 taxable income and ordinary-rate treatment of capital gains; no household calculation is published." , "CPA checks the Form 540 instructions for the actual sale year and computes sale-year taxable income, basis, exclusions, estimated payments and tax."], STATUS["guidance"], ["ca_rtc17043", "ftb_540", "ftb_540es", "ftb_cap_gains", "ftb_forms"]),
            (["Federal estate threshold, portability and liquidity", "Current-year federal thresholds are estate-level and not per-heir; future law and household headroom are not inferred." , "Ask now about portability and prior taxable gifts; obtain a private estate inventory and liquidity schedule."], STATUS["guidance"], ["irs_estate", "irs_estate_faq", "irs_706"]),
            (["Deadlines and step-by-step inheritance process", "Trust notice, change-in-ownership, Form 706 and Proposition 19 deadlines are presented with applicability caveats." , "Attorney calendars actual dates from death, title and transfer-route documents."], STATUS["guidance"], ["ca_prob", "ca_rtc480", "irs_706", "ca_rtc63"]),
            (["Enacted law vs. proposals and annual refresh", "The watchlist separates enacted law, pending proposals, ballot measures and unverified facts." , "Recheck official federal, state and local authorities annually and at transfer; record source, status and effective date."], STATUS["guidance"], ["congress_law", "sos_measures", "boe_prop19"]),
            (["Investment policy before proceeds arrive", "A blank, reviewable policy draft sets liquidity, staging, asset exposure, tax-aware realization and triggers without choosing personal values." , "Agree in writing on path conditions, risk limits, liquidity floor, review date and approver before seeing projections."], STATUS["guidance"], ["treasury_bills", "treasury_notes", "sec_stocks"]),
            (["What-if controls, ranges and distribution chart", "The phased tool and the sale-tax overlay tool are local-only and start from blank inputs. Property inputs and distribution amounts belong in the private model; the published waterfall states the payout order and labels, not household amounts." , "After each private input change, rebuild the model, compare low/base/high outcomes and note whether rankings move."], STATUS["guidance"], ["sec_stocks", "fhfa", "cbo_long"]), 
            (["Depreciation, recapture and like-kind exchange decisions", "Published as rules and decision rows: maximum 25% federal rate on unrecaptured section 1250 gain, California ordinary-rate treatment, and the section 1031 written-decision and deadline requirements." , "CPA reconciles the private depreciation schedule; decide the exchange question in writing before listing."], STATUS["rule"], ["irs_topic409", "irs_sched_d", "irs_1031_tips", "ftb_cap_gains"]), 
            (["Proposition 19 allowance carry-forward", "Corrected 2026-11-15: the statute provides a per-transfer limit with biennially adjusted amounts and no carry-forward of an unused limit; the correction is recorded on the flagged page." , "Use the official amount in effect on the actual transfer date; confirm the reading with property-tax counsel."], STATUS["rule"], ["ca_rtc63", "boe_lta"]), 
            (["Estate liquidity plan and payment calendar", "Published on the thresholds page: nine-month general filing date, extension-to-file versus payment distinction, and funding routes to price early." , "Build the dated private liquidity inventory with the CPA."], STATUS["guidance"], ["irs_706", "irs_estate_faq"]),
            (["Attorney & CPA one-page briefing sheet", "A print-optimized adviser handoff lists trust, value, estate-tax, property-tax, sale/rent and policy questions." , "Print privately and complete only with counsel using confidential records."], STATUS["guidance"], ["irs_estate_faq", "boe_prop19", "irs_basis"]),
            (["Suggestions, glossary and dated decision record", "Suggestions have a session-only review queue; the glossary defines the tax layers; the decision log prompts a date and reason." , "Record each adopted or rejected item and the trigger for reconsideration."], STATUS["guidance"], ["irs_estate", "boe_prop19"]),
            (["Local 'Prop H' terms and impact", "Resolved privately on 2026-11-15: the official measure behind the shorthand was identified and its litigation status reviewed. Jurisdiction and terms are deliberately not published here and no household mapping or rate is applied." , "Confirm current status with the property's own tax authority at decision time; the research note is in the private workpaper."], STATUS["unverified"], ["sos_measures"]),
        ]
        body = table("Full requirements register", ["Requirement", "Public site treatment", "Next step / remaining evidence"], rows)
        body += callout("Do not fill a gap with an assumption", "Owner-specific estimates and property records remain private. A missing row is a task to obtain evidence, not a zero or a forecast.", "warning")
        return "Requirements tracker", "A line-by-line register of the requested work, current public treatment and discovery steps.", body
    if path.endswith("investment-policy.html"):
        rows = [
            (["Purpose and authority", "Use a written policy to govern inherited or sale proceeds before funds arrive; do not let a projection alone dictate action." , "Owner, fiduciary and adviser roles: decide and sign privately."], STATUS["guidance"], ["irs_estate_faq", "sec_stocks"]),
            (["Liquidity and estate obligations", "Reserve for taxes, debt, near-term spending, property costs and emergencies before taking market risk." , "CPA confirms payment dates; owner/adviser set private reserve amount and minimum."], STATUS["guidance"], ["irs_706", "treasury_bills"]),
            (["Treasury staging", "Draft path: park proceeds in 3-month to 2-year Treasuries, then phase into stocks over 24–36 months; reinvestment yields reset and may fall." , "Set rung sizes, maturity calendar, deployment schedule and exceptions in writing."], STATUS["assumption"], ["treasury_bills", "treasury_notes"]),
            (["Equity exposure", "Diversification does not eliminate loss; do not assume a guaranteed stock return." , "Set target allocation, instruments, fees and prohibited exposures with a fiduciary adviser."], STATUS["guidance"], ["sec_stocks"]),
            (["Stress and entry rules", "Compare a crash during staging, a crash after staging, a flat market and a rising market; historical indexes are not household probabilities." , "Write whether purchases continue, accelerate or pause under each condition before results arrive."], STATUS["historical"], ["fed_1929", "fed_2008", "treasury_bills"]),
            (["Tax-aware realization", "California capital gains are taxed as ordinary income; a 1% additional tax applies to taxable income above $1,000,000 under current law." , "CPA confirms the Form 540 instructions for the sale year, basis, federal treatment and estimated payments."], STATUS["rule"], ["ca_rtc17043", "ftb_540", "ftb_540es", "ftb_cap_gains"]),
            (["Rebalancing and withdrawals", "A written calendar and spending rule can reduce reactive changes; neither ensures a profit." , "Set withdrawal order, review interval, rebalancing band and responsible approver."], STATUS["guidance"], ["sec_stocks", "treasury_notes"]),
            (["Decision triggers", "Triggers may include enacted law, material change in household needs, liquidity, property condition or verified title/eligibility facts." , "List triggers and what evidence is required; do not use headlines or unverified proposals as triggers."], STATUS["guidance"], ["congress_law", "boe_prop19"]),
            (["Privacy and records", "Statements, account identifiers, cost-basis schedules and decisions belong in private, access-controlled storage, not this public repository." , "Choose an encrypted private records location and retention/review owner."], STATUS["guidance"], ["irs_pub551", "irs_estate_faq"]),
            (["Annual review and sign-off", "Review the policy and extreme scenarios at least annually and before each investment tranche." , "Record review date, current official sources, signatories and any justified change."], STATUS["guidance"], ["treasury_bills", "sec_stocks", "cbo_long"]),
        ]
        body = table("Draft investment policy — fields intentionally left for private completion", ["Policy area", "Draft principle", "Private decision to document"], rows)
        body += callout("Agree before the figures arrive", "Write what would make the household choose each path and each investment trigger before viewing a single projection. Revisit only when a listed trigger or verified fact changes.", "info")
        return "Investment policy draft", "A source-linked template to adopt before proceeds arrive; personal choices remain blank and private.", body
    if path.endswith("suggestions.html"):
        rows = [
            (["Approve a private inventory template", "Keep deed, trust, loan, tax, insurance, lease and account identifiers in an offline encrypted file, never in this repo." , "Choose secure storage and named professional custodians."], STATUS["guidance"], ["irs_estate_faq", "irs_1041"]),
            (["Order independent valuation and condition reports", "Use independent qualified providers and preserve date-of-death valuation evidence." , "Written appraisal, inspection and contractor review."], STATUS["guidance"], ["irs_basis", "cslb"]),
            (["Write a decision policy before forecasts", "Specify triggers and acceptable trade-offs before seeing modeled rankings." , "Household signs a dated policy; advisers acknowledge it."], STATUS["guidance"], ["sec_stocks", "treasury_bills"]),
            (["Build after-tax cash-flow scenarios", "Keep estate tax, income-tax basis and property-tax assessment in separate modules." , "CPA models transfer-year sale, Section 121, depreciation and recapture; assessor confirms Prop 19."], STATUS["guidance"], ["irs_basis", "irs_rental", "irs_121", "boe_prop19"]),
            (["Create a five-year capital plan", "Include deferred maintenance, safety, major systems, insurance deductibles and reserves for both buildings." , "Inspection, bids, useful-life schedule, annual reserve review."], STATUS["guidance"], ["cslb", "cdi"]),
            (["Refresh laws and proposals annually", "Separate enacted statutes, signed bills, pending bills, ballot measures and rejected proposals." , "Use agency and legislature records; write review date and decision effect."], STATUS["guidance"], ["congress_law", "sos_measures", "boe_prop19"]),
        ]
        body = table("Review queue — choose before implementation", ["Suggestion", "Why it helps", "Next step"], rows)
        body += '<section class="prose"><h2>Review status</h2><p>Use the controls below to mark suggestions for discussion in this browser session. Choices are kept in memory only, are not sent anywhere, and are cleared on refresh.</p><div class="review-queue">'
        for i in range(1, 7):
            body += f'<label>Suggestion {i} <select class="review-choice" aria-label="Suggestion {i} status"><option>Not reviewed</option><option>Adopt</option><option>Defer</option><option>Reject</option></select></label>'
        body += '</div><p id="review-summary" role="status" aria-live="polite">No review choices yet.</p></section>'
        return "Suggestions for review", "A separate review queue: select, discuss, and decide before implementation.", body
    if path.endswith("property-profiles.html"):
        rows = [
            (["Property A — inherited home", "No location, parcel identifier, account or party name appears here; the bill history below is the household's own rounded report, not a verified record." , "Keep location and complete source records in a private inventory; obtain date-of-death valuation."], STATUS["missing"], ["irs_basis", "boe_prop19"]),
            (["Property B — already-owned property", "No location, parcel identifier, tenant name, account or lease text appears here; only rounded building-level aggregates are used." , "Keep current title, leases, lawful-unit documentation, basis and bills privately; do not merge it with inherited assets."], STATUS["missing"], ["irs_rental", "irs_pub551"]),
            (["Evidence standard", "Owner memory or an online estimate is not an independent valuation or tax record." , "Use assessor roll, written appraisal, current insurance declarations, utility bills and executed leases."], STATUS["guidance"], ["irs_basis", "cdi", "irs_rental"]),
        ]
        body = table("Private inventory checklist", ["Record set", "Public disclosure boundary", "Private evidence to collect"], rows)
        body += callout("Do not upload records here", "This page publishes rounded scenario figures only. Never commit deeds, parcel numbers, names, statements, tax bills, insurance policies, leases, trust documents or adviser correspondence to this repository; keep them in the private workpaper.", "warning")
        return "Private property inventory", "A checklist for the two roles in the decision, without identifying property details.", body
    if path.endswith("operating-costs.html"):
        rows = [
            (["Property tax", "Use the official tax bill and assessor roll; identify base-year value, direct assessments, exemptions, reassessment triggers, the tax-rate area and its published rate." , "Obtain the actual bill and official tax-rate-area schedule; do not infer a parcel-specific rate from a generic levy."], STATUS["guidance"], ["boe_prop19", "ca_rtc51"]),
            (["Insurance", "Premium depends on property, use, coverage, deductible, underwriting and market availability." , "Get multiple written owner-occupied and landlord-policy quotes; compare exclusions and FAIR Plan/DIC gaps."], STATUS["guidance"], ["cdi"]),
            (["Water, power and solar", "Tariffs, metering, solar export rules and household usage determine actual bills and credits." , "Collect account bills and interconnection/tariff documents; no generic bill is substituted."], STATUS["guidance"], ["cpuc_solar", "water_board"]),
            (["Maintenance and capital", "A property-condition assessment and repair history are needed; a percentage-of-value shortcut is not a bid." , "Create five-year safety, roof, structure, plumbing, electrical, HVAC and accessibility plans with bids."], STATUS["guidance"], ["cslb"]), 
            (["Five-year plan — years 1-2", "Safety and habitability first: inspect roof, envelope, electrical, plumbing and any seismic elements; urgent items are priced separately from routine maintenance." , "Obtain inspection reports and at least two licensed bids per item before ranking paths that depend on carrying costs."], STATUS["guidance"], ["cslb", "irs_rental"]), 
            (["Five-year plan — years 3-5", "Systems renewal window: water heater and HVAC service life, exterior envelope, windows and doors, and any solar equipment service and inverter life." , "Record equipment ages and service contracts; capital items above the plan are separate decisions, not surprises."], STATUS["guidance"], ["cslb", "cpuc_solar"]), 
            (["Reserve policy", "Fund a dedicated repair-and-capital reserve monthly; for rentals, repairs and improvements are treated differently for income tax, so keep invoices classified as incurred." , "Adopt a written reserve policy and ask the CPA for a repair-versus-improvement classification rule."], STATUS["guidance"], ["irs_rental", "cslb"]),
            (["Rental operation", "Gross rent must be reduced for vacancy, operating costs, management, taxes, repairs and depreciation treatment." , "Reconcile leases and deposit ledgers, verify unit legality and check local tenant rules."], STATUS["guidance"], ["irs_rental", "ca_rent"]),
        ]
        return "Costs & coverage", "Use actual records and written quotes; do not substitute unsupported regional averages.", table("Operating-cost evidence plan", ["Cost category", "What drives the cost", "Evidence / action"], rows)
    if path.endswith("projections.html"):
        rows = [
            (["Market value", "Low/base/high annual appreciation scenarios × independent starting appraisal." , "FHFA index is broad context, not an individual forecast; use a written appraisal and scenario range."], STATUS["assumption"], ["fhfa", "cbo_long"]),
            (["Taxable assessed value", "Apply actual base value, statutory inflation factor, ownership-change rules and any qualifying exclusion." , "Assessor confirms transfer treatment and Prop 19 claim in writing."], STATUS["guidance"], ["ca_rtc51", "boe_prop19", "ca_rtc63"]),
            (["Property tax bill", "Taxable value × verified tax-rate-area levy plus parcel-specific direct charges." , "Obtain current bill and published tax-rate-area schedule; do not infer from assessed-value growth."], STATUS["missing"], ["boe_prop19", "ca_rtc51"]),
            (["Operating cash flow", "Rent, imputed rent for living paths, utilities, insurance, maintenance, vacancy, management and debt." , "Use current documents and refresh annually; model rents and costs as ranges."], STATUS["guidance"], ["irs_rental", "cdi", "cslb"]),
            (["Inflation and investment", "Use distinct inflation, interest, equity, recession and recovery regimes rather than one 50-year rate." , "CBO is a bounded baseline; BLS and Federal Reserve sources describe history, not probabilities."], STATUS["guidance"], ["cbo_long", "bls_cpi", "fed_inflation", "sec_stocks"]),
        ]
        body = table("Projection worksheet design (no household inputs stored)", ["Output", "Method", "Verification"], rows)
        body += prose("Avoid false precision", "Publish ranges or dated official figures only. For every modeled amount, preserve the input source, observation date, formula, tax treatment, scenario range, and whether it is measured, assumed, or missing. Rebuild after any input change and record whether the ranking moved.")
        body += prose("Distribution of sale proceeds", "Model the payout in the fixed order published on the Compare paths page: gross value, sale transaction costs, documentary transfer tax, recording fees, sale-year income tax, then net to invest. A distribution chart belongs in the private model built on that order; this public page publishes the framework and the labels, not household amounts.")
        return "Projection worksheet", "A reproducible approach for a private offline model; no property-specific projections are published.", body
    if path.endswith("property-tax.html"):
        rows = [
            (["Separate tax concepts", "Estate-tax valuation, income-tax basis, and property-tax assessed value answer different questions." , "Maintain separate ledgers and separate source documents."], STATUS["guidance"], ["irs_estate", "irs_basis", "ca_rtc51"]),
            (["Proposition 13", "California taxable value generally uses a base-year system with a statutory inflation adjustment; property bills can include other components." , "Confirm the parcel's assessed value and actual rate area from the assessor and tax bill."], STATUS["rule"], ["ca_rtc51", "boe_prop19"]),
            (["Proposition 19 family-home exclusion", "Requires statutory relationship and residence conditions; the claimant must satisfy occupancy and filing requirements." , "Claim only if eligible and the heir intends to occupy long-term; verify consequences before a later rental or sale."], STATUS["rule"], ["boe_prop19", "ca_rtc63", "boe_lta"]),
            (["Current indexed cap", "The official cap is $1,044,586 for qualifying transfers through February 15, 2027; the amount is periodically adjusted." , "Use the BOE amount applicable on the transfer date, not a forward projection."], STATUS["rule"], ["boe_lta"]),
            (["Property tax on an inherited home", "A qualifying claim may preserve the factored base value subject to the statutory value-limit calculation; failure to qualify can lead to reassessment." , "Obtain an assessor determination; do not treat a public model as eligibility advice."], STATUS["guidance"], ["boe_prop19", "ca_rtc63"]),
            (["No carry-forward of the value limit", "The family-home value limit read in the statute on 2026-11-15 (as amended through 2025) applies per qualifying transfer: each transfer is limited to the then-current adjusted amount. The statute contains no carry-forward of an unused limit to a later transfer, and the biennial adjustment is published by the state board rather than projected here." , "Do not budget a transfer around an assumed stockpiled allowance; use the official amount in effect on the actual transfer date."], STATUS["rule"], ["ca_rtc63", "boe_lta"]),
            (["Claim timing and corrective relief", "Claim periods, late-claim procedures, notice-based extensions and statutory limits on county claim fees are set by statute; a missed claim can change the assessment." , "Calendar the claim immediately after transfer; counsel confirms the applicable period and any late-claim route in writing."], STATUS["rule"], ["ca_rtc63", "ca_rtc27388"]),
            (["Tax rate area (TRA)", "Property-tax rates are set by geographic tax rate areas published in the county's official rate compilation; the parcel's tax rate area line appears on the tax bill." , "Read the tax rate area from the actual bill and its published total rate from the county compilation; do not infer a rate from a generic statewide levy."], STATUS["guidance"], ["ca_rtc51", "boe_counties"]),
        ]
        return "Property-tax rules", "Current California rules are conditional; verify future law and property-specific facts.", table("Property-tax decision gates", ["Rule", "Officially established", "Action"], rows)
    if path.endswith("inheritance-process.html"):
        rows = [
            (["Trustee notice", "Generally due within 60 days for specified trust events; applicability depends on the event and trust." , "Attorney checks service, recipients, content and triggering event."], STATUS["rule"], ["ca_prob"]),
            (["Change-in-ownership statement", "A 150-day deadline applies in specified nonprobate death transfers under California law." , "Trustee/attorney confirms the applicable form, assessor destination and exact due date."], STATUS["rule"], ["ca_rtc480"]),
            (["Federal estate return", "Form 706 is generally due nine months after death; an extension to file must be requested, and payment timing is a separate issue." , "CPA/estate counsel calendars filing, payment, liquidity and any portability election."], STATUS["rule"], ["irs_706", "irs_estate_faq"]),
            (["Proposition 19 occupancy / exemption", "The claimant generally must occupy the home as a principal residence and file the homeowners' exemption within one year under the current framework." , "Confirm exact start date, evidence, exemption and applicable rule with the assessor."], STATUS["rule"], ["boe_prop19", "ca_rtc63", "ca_rtc218"]),
            (["Proposition 19 claim", "A three-year claim period is described in the current framework, subject to statutory details and timing." , "File early and retain proof; counsel confirms property-specific deadline."], STATUS["rule"], ["boe_prop19", "ca_rtc63"]),
        ]
        steps = [
            ("Within 60 days", "Specified trustee notice events", "ca_prob"),
            ("Within 150 days", "Specified death-transfer ownership statement", "ca_rtc480"),
            ("Within 9 months", "Federal Form 706 general due date", "irs_706"),
            ("Within 1 year", "Qualifying principal-residence occupancy and homeowners' exemption timing", "boe_prop19"),
            ("Within 3 years", "Proposition 19 claim period in the current framework", "ca_rtc63"),
        ]
        body = '<ol class="timeline">' + ''.join(f'<li><span class="tl-when">{esc(when)}</span><span class="tl-what"><strong>{esc(label)}</strong><br>{source_link(ref)}</span></li>' for when, label, ref in steps) + '</ol>'
        body += table("Illustrative deadline timeline — verify the triggering event", ["Milestone", "Current rule summary", "Responsible action"], rows)
        body += callout("This is not a calendar", "The actual deadline depends on death date, transfer route, title, claim and statutory facts. Have counsel calculate every due date from official documents and put reminders in the private estate plan.", "warning")
        return "Deadline timeline", "Step-by-step process and deadlines, subject to the actual trust and transfer facts.", body
    if path.endswith("estate-thresholds.html"):
        rows = [
            (["Federal estate tax", "The 2026 basic exclusion is $15,000,000; the official 2027 amount is $15,480,000. Filing tests are estate-level and include adjusted taxable gifts; threshold law can change." , "Compare the entire estate, not just the inherited home or one beneficiary's distribution."], STATUS["rule"], ["congress_law", "irs_2027", "irs_estate_faq"]),
            (["Annual gift exclusion", "The IRS publishes an annual gift exclusion by tax year; do not treat it as an inheritance allowance." , "Check current IRS annual adjustment for the relevant year."], STATUS["guidance"], ["irs_2027"]),
            (["California gain tax and additional tax", "FTB says capital gains are taxed as ordinary income. The 2025 Form 540 line 62 instructions compute an additional 1% on taxable income above $1,000,000 under current statute; this is a tax on taxable income, not on the inheritance itself." , "Model the sale tax year with the CPA. The 2025 Form 540 line 62 instructions were read; recheck the instructions and law for the actual future sale year and apply the formula to private taxable-income facts."], STATUS["rule"], ["ca_rtc17043", "ftb_540", "ftb_cap_gains", "ftb_forms"]),
            (["California estate tax", "California's published guidance says estate tax returns are not required for deaths on or after January 1, 2005; current law must be rechecked at death." , "Separate state estate tax from federal estate tax and income-tax consequences."], STATUS["guidance"], ["ca_sco", "ca_rtc13301"]),
            (["Portability and prior gifts", "A surviving spouse's portability may require an estate-tax return even where the estate is below the filing threshold." , "Ask now about prior taxable gifts, deceased-spouse unused exclusion and timely filing."], STATUS["guidance"], ["irs_estate_faq", "irs_estate"]),
            (["Payment calendar", "A federal estate return is generally due nine months after death; an extension of time to file is not an extension of time to pay." , "Calendar both dates at the death and plan funding before the filing window opens."], STATUS["rule"], ["irs_706", "irs_estate_faq"]),
            (["Estate liquidity plan", "An estate concentrated in real estate can owe taxes and expenses on a calendar that does not wait for a property sale; funding routes (insurance in trust, financing, staged or installment sale) must be priced before they are needed." , "Build a dated liquidity inventory and obtain quotes and lender indications early; keep proceeds outside the estate where counsel advises."], STATUS["guidance"], ["irs_estate_faq", "irs_estate"]),
            (["Worked sale-year sensitivity (California 1% add-on)", "The add-on equals 1% of taxable income above the threshold: each $100,000 of taxable income above $1,000,000 adds $1,000, or $100 per $10,000. The 2025 Form 540 line 62 instruction says to use whole dollars. Capital gains count in taxable income because California taxes them as ordinary income." , "Compute the actual sale-year figure from private basis, deductions and other income; recheck current law and instructions for the actual year."], STATUS["rule"], ["ca_rtc17043", "ftb_540", "ftb_cap_gains"]),
            (["Future threshold", "No official source can establish a future estate exclusion decades ahead; Congress can amend law." , "Use dated scenarios only and refresh from enacted law and IRS annual guidance."], STATUS["assumption"], ["congress_law", "irs_2027"]),
        ]
        return "Estate-tax thresholds", "The exclusion is not a per-heir allowance; assess the whole estate and year of death.", table("Estate and inheritance tax questions", ["Topic", "Current official information", "Next step"], rows)
    if path.endswith("law-watchlist.html"):
        rows = [
            (["Enacted federal law", "Public Law 119-21 is enacted; use the current IRS annual amounts and statute rather than old proposals." , "Document enactment date and operative year; recheck IRS guidance annually."], STATUS["rule"], ["congress_law", "irs_2027"]),
            (["Pending federal proposals", "A bill or proposal is not law unless enacted; no proposal-specific household outcome is modeled here." , "For each bill, record official status, text, committee action, effective date and whether it became law."], STATUS["guidance"], ["congress_law"]),
            (["California ballot measures", "Qualified list, measure text, election results and operative law are distinct records." , "Check official text and certified results; do not infer effect from a title."], STATUS["guidance"], ["sos_measures"]),
            (["Property-tax law", "Current Proposition 19 rules remain subject to amendment and future BOE indexed amount updates." , "Recheck BOE, statute and local assessor immediately before transfer."], STATUS["rule"], ["boe_prop19", "boe_lta", "ca_rtc63"]),
            (["Local measure called 'Prop H'", "Private research on 2026-11-15 identified the official measure behind this shorthand and reviewed its litigation status; jurisdiction and terms are intentionally not published here, and no impact is modeled." , "Confirm the measure and its current status with the property's own tax authority before relying on any vacancy-tax assumption."], STATUS["unverified"], ["sos_measures"]), 
            (["Residential vacancy taxes", "Some jurisdictions have adopted annual taxes on residential units vacant beyond a statutory period; litigation in at least one jurisdiction barred enforcement during 2024-2026. These measures are jurisdiction-specific and case-specific." , "Read the property's own current ordinance and any litigation before planning an empty or periodically vacant unit."], STATUS["guidance"], ["sos_measures"]), 
            (["Local transfer-tax restructuring proposals", "Jurisdictions periodically propose tiered transfer-tax changes (for example, reducing top tiers at high values or adding parallel special taxes). A controller's digest of a proposal is not the enacted schedule." , "At sale, read the enacted local transfer-tax schedule actually in force and record its enactment date; keep proposal digests labeled as proposals."], STATUS["guidance"], ["sos_measures", "ca_rtc11911"]),
        ]
        return "Law watchlist", "A proposal is not enacted law. Track official status, effective dates and source-check dates.", table("Legislation and rules to refresh", ["Item", "Status distinction", "Verification routine"], rows)
    if path.endswith("black-swan.html"):
        rows = [
            (["1929 crash anchor", "Federal Reserve History reports the Dow fell 89% peak-to-trough and did not regain its prior high until 1954; that is a historical price-index path, not a diversified portfolio return." , "Use an 89% stress anchor only as an explicitly labeled scenario; test crash during and after staging, not as a probability."], STATUS["historical"], ["fed_1929"]),
            (["2007–09 Great Recession anchor", "Federal Reserve History reports an approximately 57% S&P 500 peak-to-trough decline and approximately 30% average U.S. home-price decline from prior peaks." , "Compare an early-staging and post-staging stress; do not treat national indexes as a property or portfolio forecast."], STATUS["historical"], ["fed_2008", "sec_stocks"]),
            (["Deflation and income stress", "The Great Depression history describes deflation and severe economic contraction." , "Stress falling nominal rents or income, vacancies, debt service, and fixed costs together."], STATUS["historical"], ["fed_depression", "bls_cpi"]),
            (["Inflation / stagflation", "Federal Reserve history documents a high-inflation period and policy response; historical inflation can be uneven." , "Stress simultaneous high inflation, high financing/insurance cost, weak real returns and delayed maintenance."], STATUS["historical"], ["fed_inflation", "bls_cpi"]),
            (["Housing and equities fall together", "National indices cannot describe a specific property or household balance sheet." , "Test lower home value and lower equities at once; include sale liquidity, debt and rent interruption."], STATUS["guidance"], ["fhfa", "fed_2008", "sec_stocks"]),
            (["Long-horizon baseline", "CBO and historical series are bounded; no official institution forecasts an individual home or portfolio over a 50-year horizon." , "Use irregular sequences of regimes rather than a single annual growth rate; label all future paths as assumptions."], STATUS["guidance"], ["cbo_long", "cbo_outlook", "bls_cpi"]),
        ]
        return "Black-swan conditions", "Stress regimes should mimic historical mechanisms, not claim to predict their timing or probability.", table("Stress scenarios to run", ["Regime", "Evidence", "Household stress design"], rows)
    if path.endswith("phased-investing.html"):
        body = callout("Headline and risk", "Phasing sale proceeds into equities can reduce immediate exposure to an early fall, but can lag a rising market. Treasury interest resets at reinvestment; lower renewal yields, taxes, inflation, and delayed equity exposure can change the result.", "warning")
        body += table("Mechanics and evidence", ["Feature", "What is known", "What to test"], [
            (["Treasury bills", "U.S. Treasury bills are auctioned at stated terms; a held-to-maturity investment differs from a sale before maturity." , "Use actual auction yields for each rung and model falling-yield reinvestment."], STATUS["rule"], ["treasury_bills"]),
            (["3-month to 2-year Treasury ladder", "Bills and notes can span short maturities through a two-year note; individual auctions and maturities reset the yield path." , "For a 24–36 month deployment plan, compare maturity dates with scheduled stock purchases and cash needs."], STATUS["rule"], ["treasury_bills", "treasury_notes"]),
            (["Treasury notes", "A two-year note pays its stated interest but can have market-price risk if sold before maturity." , "Align maturity with cash needs; avoid treating the note as a guaranteed liquid balance at par before maturity."], STATUS["rule"], ["treasury_notes"]),
            (["Staged equities", "A fixed schedule buys at different market prices; there is no guaranteed better outcome than immediate investment." , "Test crash during staging, crash after completion, flat market and rising market."], STATUS["guidance"], ["sec_stocks", "fed_1929", "fed_2008"]),
            (["Private what-if controls", "Inputs are evaluated in browser memory only; the page provides no default household amount and sends no data." , "Enter private assumptions only on a device you control; refresh to clear them."], STATUS["guidance"], ["treasury_bills", "sec_stocks"]),
        ])
        body += '<section class="prose"><h2>Historical stress anchors</h2><p>The calculator starts with the 57% S&amp;P 500 2007–09 drawdown anchor. A 1929 stress run may use 89%, but that figure describes the Dow Jones Industrial Average, a different price index. These are not comparable portfolio estimates. Source: ' + source_link("fed_2008") + ' and ' + source_link("fed_1929") + '.</p></section>'
        body += '<section class="prose"><h2>Local-only sensitivity tool</h2><p>Enter generic scenario assumptions. This is an illustration, not a forecast, advice, or a historical backtest. No values are stored or transmitted. Crash timing is a one-time shock in an otherwise smooth annual-drift path.</p><div class="calculator"><label>Starting amount <input id="phase-amount" type="number" min="0" step="10" inputmode="decimal" placeholder="Enter privately"></label><label>Staging months <input id="phase-months" type="number" min="24" max="36" step="1" value="24"></label><label>Annual Treasury yield (%) <input id="phase-yield" type="number" min="-5" max="30" step="0.1" placeholder="Enter assumption"></label><label>Annual equity price drift (%) <input id="phase-equity" type="number" min="-50" max="50" step="0.1" placeholder="Enter assumption"></label><label>One-time equity decline (%) <input id="phase-crash" type="number" min="0" max="90" step="1" value="57"></label><label>Crash month (staging months + 1 = just after staging) <input id="phase-crash-month" type="number" min="1" max="37" step="1" value="13"></label><button id="phase-run" type="button">Run illustration</button><button id="phase-clear" type="button">Clear</button><p id="phase-result" role="status" aria-live="polite">No calculation run.</p></div></section>'
        body += prose("Limits", "This simplified path applies one instantaneous drawdown at the selected month, with a constant annual equity-price drift and Treasury yield otherwise. It does not model a historical sequence or recovery, dividends, fees, taxes, withdrawals, asset correlations, property costs, or changing Treasury yields. A 57% or 89% shock compresses a multi-year index decline into one event and is a stress input only, not a forecast or probability.")
        return "Treasury staging tool", "Model 24–36 months of 3-month to 2-year Treasuries beside equity entry and renewal risk.", body
    if path.endswith("attorney-cpa-brief.html"):
        body = callout("Print-ready adviser handoff", "Bring this generic checklist to counsel and the tax adviser. Keep all names, property identifiers, documents and household figures out of the public site.", "info")
        body += table("Attorney & CPA briefing checklist", ["Workstream", "Questions to resolve", "Documents / action"], [
            (["Trust and title", "What transfers, when, subject to what debts and authority?", "Executed trust and amendments, deed, statements of authority, debt and beneficiary records."], STATUS["missing"], ["ca_prob", "ca_rtc480"]),
            (["Valuation and tax basis", "What is date-of-death value, adjusted basis, depreciation and improvement history?", "Independent appraisal, prior returns, capital-improvement receipts, depreciation schedules."], STATUS["missing"], ["irs_basis", "irs_pub551", "irs_rental"]),
            (["Estate tax and liquidity", "Does filing or payment apply; are gifts, marital deduction or portability relevant?", "Complete confidential inventory, prior gift returns, liquidity calendar and Form 706 advice."], STATUS["missing"], ["irs_estate_faq", "irs_706"]),
            (["Property-tax eligibility", "Is the heir eligible and willing to occupy long-term; what are deadlines and later-conversion consequences?", "Written BOE/assessor analysis, occupancy plan, claim calendar and current indexed cap."], STATUS["missing"], ["boe_prop19", "ca_rtc63", "boe_lta"]),
            (["Income tax and alternatives", "Compare sale in transfer year, later sale, rental, live, and mixed paths; test depreciation and recapture." , "CPA compares identical tax dates/horizons, costs, debt, rent, utility/insurance, and Section 121."], STATUS["missing"], ["irs_121", "irs_rental", "ftb_forms"]), 
            (["Sell-year cost stack", "What documentary transfer tax, recording fees, and sale-year income tax apply — including unrecaptured section 1250 gain and the California 1% add-on above $1,000,000 of taxable income?", "Enacted local transfer-tax and recorder schedules; CPA computation from private basis and depreciation records; written like-kind-exchange decision before any listing."], STATUS["missing"], ["ca_rtc11911", "ca_gov27361", "irs_topic409", "ca_rtc17043", "irs_1031_tips"]),
            (["Investment policy", "What liquidity, asset allocation, staging period and drawdown limits are acceptable?", "Adopt policy before proceeds arrive; model Treasury renewal risk, crash timing and rising-market opportunity cost."], STATUS["guidance"], ["treasury_bills", "treasury_notes", "sec_stocks"]),
        ])
        body += '<p class="no-print"><button class="print-button" id="print-page" type="button">Print this one-page brief</button></p>'
        return "Attorney & CPA briefing sheet", "One-page print-ready checklist for counsel and the tax adviser.", body
    if path.endswith("decision-log.html"):
        rows = [
            (["Decision rule", "What choice would be made under each eligible path, before figures are revealed?", "Write dated criteria, including liquidity, occupancy, tax eligibility and risk limits."], STATUS["guidance"], ["sec_stocks", "boe_prop19"]),
            (["Evidence", "Which official document, quote, appraisal, lease, tax return or professional opinion changed the decision?", "Record source, date, reviewer, uncertainty and any contrary evidence."], STATUS["guidance"], ["irs_basis", "irs_rental", "cdi"]),
            (["Decision and date", "What was chosen, by whom, when, and why?", "Record the rejected alternatives and the conditions that would reopen the decision."], STATUS["guidance"], ["irs_estate_faq", "boe_prop19"]),
        ]
        body = table("Decision-log template", ["Entry", "Prompt", "Record"], rows)
        body += table("Pre-commitment criteria — agree and sign before figures arrive", ["Path", "Rule to sign now", "Evidence gate", "Signature / date"], [
            (["Occupy the inherited home", "Choose only if a household member will occupy it as a principal residence within the statutory period and intends to stay long term.", "Written occupancy commitment; assessor's eligibility confirmation.", "________________ (sign and date)"], STATUS["guidance"], ["ca_rtc63", "boe_prop19"]),
            (["Rent it out", "Choose only if written rent comparables clear the household's stated hurdle and landlord duties and the reassessed-tax branch are accepted.", "Rent comps; landlord quotes; lawful-unit confirmation.", "________________ (sign and date)"], STATUS["guidance"], ["irs_rental", "ca_rent", "hud_fmr"]),
            (["Sell in the transfer tax year", "Choose only after the sale-cost waterfall (transaction costs, transfer tax, recording, sale-year income tax) is priced from official schedules.", "Enacted local schedules; CPA sale-year estimate; closing estimate.", "________________ (sign and date)"], STATUS["guidance"], ["irs_basis", "ca_rtc11911", "ca_gov27361"]),
            (["Sell and stage proceeds over 24-36 months", "Choose only with a signed investment policy and an explicit acceptance of reinvestment risk in exchange for softer crash-entry risk.", "Signed policy statement; Treasury rung plan; tax reserve.", "________________ (sign and date)"], STATUS["guidance"], ["treasury_bills", "treasury_notes"]),
            (["Sell and invest immediately", "Choose only with the same signed policy and explicit acceptance of full immediate market exposure.", "Signed policy statement; tax reserve.", "________________ (sign and date)"], STATUS["guidance"], ["sec_stocks", "fed_1929", "fed_2008"]),
            (["Mixed path", "Choose only for lawful uses with written leases or occupancy plans, keeping each asset's basis, tax and costs separate.", "Permits; leases; per-asset cost allocation.", "________________ (sign and date)"], STATUS["guidance"], ["irs_rental", "irs_1041"]),
        ])
        return "Decision log", "Record the decision and date so a future reader can understand what was chosen and why.", body
    if path.endswith("flagged-for-review.html"):
        rows = [
            (["No private inventory", "Property values, assessed values, rent, bills, leases, title and insurance records are deliberately absent." , "Build and store the inventory offline; do not add it to Git or the site."], STATUS["missing"], ["irs_basis", "irs_rental", "cdi"]),
            (["Future-year law and economic path", "A transfer expected decades from now cannot be determined from present rules or official baseline forecasts." , "Recheck current law, indexed amounts, proposals and markets annually."], STATUS["guidance"], ["irs_2027", "boe_lta", "cbo_long"]),
            (["California sale-year tax sensitivity", "Official statute and the 2025 Form 540 line 62 instructions state a 1% tax on taxable income above $1,000,000; each $10,000 over the threshold adds $100. The 2025 instructions were read on 2026-11-16. No household calculation is published." , "CPA applies the actual sale-year instructions to the private taxable-income facts; the future-year rate and threshold must be rechecked."], STATUS["missing"], ["ca_rtc17043", "ftb_540", "ftb_cap_gains", "ftb_forms"]),
            (["Prop H", "The identifier alone does not establish jurisdiction, election year or measure text. Private research on 2026-11-15 identified the official measure behind the shorthand and reviewed its litigation status; jurisdiction and terms are withheld from this public site by policy, and no impact is modeled." , "Confirm the measure's current status with the property's own tax authority; the identification is recorded in the private workpaper."], STATUS["unverified"], ["sos_measures"]), 
            (["Proposition 19 value-limit carry-forward premise", "A carry-forward of an unused family-home value limit was requested. The full text of the governing statute read on 2026-11-15 (as amended through 2025) provides no such carry-forward: each qualifying transfer is limited to the then-current adjusted amount. The correction is recorded here so the premise is not modeled silently." , "Confirm with the property-tax adviser; if biennial indexing of the limit was meant, use the official amount published for the actual transfer date."], STATUS["rule"], ["ca_rtc63", "boe_lta"]), 
            (["Proposal digests are not enacted schedules", "Digests and fiscal analyses describing proposed local tax changes are not enacted law, and lower tiers of tiered local transfer taxes were not read from enacted codes in this project." , "Before pricing any sale, read the enacted transfer-tax schedule in force and record its enactment date and source."], STATUS["unverified"], ["sos_measures", "ca_rtc11911"]),
            (["History / repository exposure", "Earlier public Git objects and copies may retain content no longer shown on the site. A site rebuild cannot recall prior clones, PR diffs or caches." , "Repository administrator should assess visibility, history remediation and GitHub Support options; preserve a private archive before a rewrite."], STATUS["missing"], ["github_sensitive"]),
        ]
        return "Flagged for review", "Unverified or missing information is visible here; no unresolved item is presented as fact.", table("Open items", ["Flag", "What is not established", "Next verification step"], rows)
    if path.endswith("glossary.html"):
        rows = [
            (["Estate tax", "Tax potentially imposed on a decedent's taxable estate under federal law; not a tax simply triggered by every inheritance." , "Compute at estate level with counsel."], STATUS["guidance"], ["irs_estate"]),
            (["Income-tax basis", "The tax basis used to determine gain or loss; inherited basis is generally tied to date-of-death value subject to exceptions." , "Obtain appraisal and CPA basis schedule."], STATUS["rule"], ["irs_basis", "irs_pub551"]),
            (["Assessed value", "Value used for property-tax purposes under applicable assessment rules; not the same as income-tax basis or market value." , "Confirm with assessor and tax bill."], STATUS["guidance"], ["ca_rtc51"]),
            (["Proposition 19 exclusion", "Conditional property-tax treatment for qualifying family transfers of a principal residence or family farm." , "Confirm relationship, occupancy, filing and value-limit requirements."], STATUS["rule"], ["boe_prop19", "ca_rtc63"]),
            (["Depreciation recapture", "Potential income-tax consequences when depreciable rental property is disposed of; amount depends on depreciation and tax details." , "CPA reconciles depreciation allowed/allowable, basis and disposition."], STATUS["guidance"], ["irs_rental", "irs_pub551"]),
            (["Sequence / reinvestment risk", "Investment outcome depends on when gains and losses occur and when reserve instruments mature or are reinvested." , "Stress early and late crashes, lower renewal yields, and rising-market lag."], STATUS["guidance"], ["treasury_bills", "sec_stocks"]), 
            (["Unrecaptured section 1250 gain", "The part of gain on a sold rental equal to depreciation previously claimed; federally taxed at a maximum 25% rate, separate from the preferential long-term rates." , "CPA computes it from the private depreciation schedule."], STATUS["rule"], ["irs_topic409", "irs_sched_d"]), 
            (["Like-kind exchange (section 1031)", "A swap of business or investment real property that can defer gain; it involves a qualified intermediary, statutory deadlines, taxable boot, and carryover basis in the replacement." , "Decide in writing before listing; a primary residence never qualifies."], STATUS["rule"], ["irs_1031", "irs_1031_tips"]), 
            (["Documentary transfer tax", "A tax on the transfer of real property, generally computed on value in statutory increments and collected at recording under state authority and the local schedule." , "Price it into every sale path from the property's own enacted schedule."], STATUS["rule"], ["ca_rtc11911", "ca_gov27361"]), 
            (["Imputed rent", "The housing value consumed by living in a home one owns instead of paying rent elsewhere; a planning comparison, not a tax or a deduction." , "Include it when comparing live paths with rent or sell paths."], STATUS["guidance"], ["hud_fmr", "irs_rental"]), 
            (["Tax rate area (TRA)", "The geographic zone that determines which taxing jurisdictions apply and the total property-tax rate; identified on the tax bill and in the county's official rate compilation." , "Read the area and its published rate from the bill and county compilation."], STATUS["guidance"], ["ca_rtc51", "boe_counties"]),
        ]
        return "Glossary", "Plain-language definitions with official scope links.", table("Terms", ["Term", "Meaning", "Use"], rows)
    if path.endswith("sources.html"):
        rows = []
        for key, (label, url, scope) in SOURCES.items():
            rows.append(([label, scope, "Reference link; recheck before use"], STATUS["unverified"] if key == "ftb_forms" else STATUS["reference"], [key]))
        body = table("Official source register", ["Source", "Scope and limits", "Review note"], rows)
        body += prose("Verification discipline", "A link is not proof of a household-specific fact. This register is a starting point; source availability and content are not re-fetched on each build. Check each official page and the applicable year before relying on it. Unavailable, future, or property-specific facts remain blank and flagged.")
        return "Official source register", "Primary-source links and the narrow question each source can answer.", body
    if path.endswith("privacy.html"):
        body = callout("Privacy comes first, by construction rather than by omission", "This site publishes no property locality, address, parcel identifier, account number, lease, policy detail, tax document or unrounded figure. What it does publish is a rounded scenario model, on the owner's instruction, so that the arithmetic can be checked line by line; the exact records belong outside this repository.", "warning")
        body += table("Privacy controls and limits", ["Control", "Current behavior", "Limitation"], [
            (["Public build inputs", "The generator contains the rounded scenario figures inline and reads no data file; sources are public rules and official records." , "A public site cannot be used as a private case database."], STATUS["guidance"], ["irs_estate", "boe_prop19"]),
            (["Browser controls", "What-if calculations run in memory; the browser code makes no network requests or storage writes." , "Avoid entering sensitive details on a shared device; refresh to clear transient values."], STATUS["guidance"], ["treasury_bills", "sec_stocks"]),
            (["Current site", "Location and individual property figures are omitted." , "Anyone with repository access can read all tracked text and source files."], STATUS["guidance"], ["irs_basis"]),
            (["Earlier public copies", "A new build cannot remove old commits, forks, downloaded archives, cached pages or PR diffs." , "Treat anything previously public as potentially retained; admin-level remediation may be needed."], STATUS["missing"], ["github_sensitive"]),
        ])
        return "Privacy & limits", "Privacy is a design constraint, not a rounding promise.", body
    return "Not found", "", ""


def decorate(path: str, heading: str, lead: str, body: str) -> tuple:
    value_t = market_value(TRANSFER_YEAR)
    sell = sale_net(value_t, value_t)
    outcomes = path_outcomes()
    bill_now = tax_bill(2026, 2026, "keep-base")
    bill_then = tax_bill(TRANSFER_YEAR, TRANSFER_YEAR, "keep-base")
    bill_claim = tax_bill(TRANSFER_YEAR, TRANSFER_YEAR, "prop19")
    bill_none = tax_bill(TRANSFER_YEAR, TRANSFER_YEAR, "reassessed")
    staging_gap = outcomes[SELL_LABEL]["value"] - outcomes["Sell, park 30 months in Treasuries, then buy"]["value"]

    if path == "index.html":
        extra = table("The modeled heart of the decision: what the transfer does to the tax", [
            "Compared item", "Before any transfer, modeled 2045", "After transfer with a Proposition 19 claim", "After transfer with no claim", "Why this decides the answer"], [
            row(["Assessed value", usd(assessed_untransferred(TRANSFER_YEAR)), usd(assessed_at_transfer(TRANSFER_YEAR, "prop19")), usd(assessed_at_transfer(TRANSFER_YEAR, "reassessed")), "The assessed value, not the sale price, sets the yearly bill after a transfer."], "assumption", ["ca_rtc51", "boe_prop19", "ca_rtc63"]),
            row(["Property tax a year", usd(bill_then), usd(bill_claim), usd(bill_none), "Every hold path pays this before insurance, water, repairs and reserves."], "assumption", ["ca_rtc51", "boe_lta"]),
            row(["Tax as a share of value", pct(bill_then / value_t), pct(bill_claim / value_t), pct(bill_none / value_t), "A let home must clear this out of its rent before it earns anything."], "assumption", ["ca_rtc51", "hud_fmr"]),
            row(["Multiple of the modeled 2026 bill", "1.0 times", f"{bill_claim / bill_now:.1f} times", f"{bill_none / bill_now:.1f} times", "This step-up, not the market, is the largest single change the transfer causes."], "assumption", ["boe_prop19", "ca_rtc63"]),
            row(["Net proceeds if sold in the transfer year", "not applicable", usd(sell["after_tax"]), "not applicable", "After sale costs, transfer tax, recording and sale-year income tax on a stepped-up basis."], "assumption", ["irs_basis", "ca_rtc11911", "ca_gov27361"]),
        ])
        extra += callout("Reinvestment risk sits beside this headline, not behind it",
                         "Phasing the modeled " + usd(sell["after_tax"]) + " through short Treasuries for 30 months instead of investing at once costs about " + usd(staging_gap) +
                         " at the 2070 horizon if prices only drift upward on the baseline assumption, and it shields part of the same money if a 1929-style or 2008-style fall begins in the month of the transfer. "
                         "The Black-swan page prices both sides of that one mechanism in the same table; no source read here can say which side the household meets first. " + MODEL_NOTE, "warning")
        marker = '<div class="table-scroll" tabindex="0"><table><caption>What would change the answer?'
        body = body.replace(marker, extra + marker, 1) if marker in body else body + extra
        return heading, lead, body

    if path.endswith("executive-summary.html"):
        rows = ranked_rows(horizon=2070)
        body += table("Modeled ranking on the published rounded inputs: transfer 2045, horizon 2070", ["Path", "Net position at the horizon", "Against selling in the transfer year", "What the model assumes about housing"],
                      [row([label, usd(value), signed_usd(delta), detail], "assumption", ["irs_basis", "ca_rtc51", "treasury_bills"]) for label, value, delta, detail in rows])
        long_run = ranked_rows(growth=GROWTH_HOME["long-run"])
        soft_2055 = ranked_rows(horizon=2055, rate_key="soft")
        soft_2070 = ranked_rows(horizon=2070, rate_key="soft")
        if soft_2055[0][0] == SELL_LABEL and soft_2070[0][0] == SELL_LABEL:
            soft_note = "The ranking holds: selling still leads, with the margin over the next path narrowing to " + usd(soft_2070[0][1] - soft_2070[1][1]) + " at the 2070 horizon."
        else:
            soft_note = ("The ranking inverts. A weak portfolio also leaves the Treasury reserve out-earning the invested proceeds for a while, so delaying the "
                         "purchase wins the ten-year comparison and letting the home wins the long one: " + soft_2055[0][0] + " leads 2055 by about " + usd(soft_2055[0][2])
                         + ", and " + soft_2070[0][0] + " leads 2070 by about " + usd(soft_2070[0][2]) + ". Selling at once stays ahead only while invested money "
                         "out-earns the house, which is why the return assumption belongs in a signed policy rather than in a forecast.")
        body += table("What would flip this answer, and the evidence that settles each one", ["Switch to test", "Effect on the ranking", "Evidence that settles it"], [
            row([f"Home values grow at the published long-run pace of {pct(GROWTH_HOME['long-run'])} a year instead of {pct(GROWTH_HOME['baseline'])}", f"Selling still leads, but the margin over the next path narrows to about {usd(long_run[0][1] - long_run[1][1])} at the 2070 horizon.", "A written date-of-death appraisal plus a dated comparable-sales file, refreshed each year."], "assumption", ["fhfa", "cbo_long"]),
            row([f"Holding and letting wins only above {pct(break_even_growth(RENT_LABEL, horizon=2055))} a year to 2055, or {pct(break_even_growth(RENT_LABEL))} a year to 2070", "Below that growth the let path loses ground to a portfolio on these cost assumptions; above it the ranking turns.", "Written rent comparables, contractor bids, and the actual tax-bill lines."], "assumption", ["hud_fmr", "cslb", "fhfa"]),
            row(["A valid Proposition 19 claim plus genuine long-term occupancy", "Lowers the tax base for the live-in paths; it does nothing for a let home, and a later change of use can end it.", "Written assessor determination, occupancy evidence, and the exemption filing."], "rule", ["boe_prop19", "ca_rtc63", "ca_rtc218"]),
            row([f"Estate-level federal exposure: {usd(15_000_000)} for deaths in 2026, {usd(15_480_000)} for deaths in 2027", "Above the exclusion, 40 percent of the excess leaves the estate before any path is chosen, and the payment date does not wait for a sale.", "A confidential estate inventory, gift history since 1977, portability facts and a dated liquidity plan."], "rule", ["irs_estate", "irs_2027", "irs_706"]),
            row([f"Portfolio returns run at the soft scenario of {pct(PORTFOLIO_RETURN['soft'], 1)} a year", soft_note, "A written investment policy with the return assumption it prices, reviewed annually."], "assumption", ["sec_stocks", "cbo_long", "treasury_bills"]),
            row(["A mortgage, lien or judgment on either building", "Net proceeds and equity return move one for one with the debt; this model assumes none because the record is unconfirmed.", "Loan statements, payoff figures and a title report read by counsel."], "missing", ["irs_pub551"]),
        ])
        shortfall = carrying_total(TRANSFER_YEAR, TRANSFER_YEAR, "prop19", GROWTH_HOME["baseline"], "A") - third_unit_rent(TRANSFER_YEAR)
        rent_net = rent_income(TRANSFER_YEAR)[1] - carrying_total(TRANSFER_YEAR, TRANSFER_YEAR, "reassessed") - rent_income(TRANSFER_YEAR)[0] * MANAGEMENT
        body += prose("The answer, with its reasons attached", "On the rounded inputs published here, selling the inherited home in the transfer year and investing the proceeds ranks ahead of every hold path at both the ten-year and the twenty-five-year horizon, in all three growth scenarios. The reasons are checkable rather than rhetorical. The transfer moves the annual property tax from " +
                      usd(bill_now) + " to " + usd(bill_claim) + " with a valid exclusion claim, or " + usd(bill_none) + " without one. A let home on these assumptions nets about " + usd(rent_net) +
                      " a year before income tax on a modeled value of " + usd(value_t) + ". A transfer-year sale is tax-light only because the modeled contract price equals the stepped-up basis, so a gap between the two is taxed in the sale year. "
                      "Choosing to hold is a bet that the home grows faster than " + pct(break_even_growth(RENT_LABEL)) + " a year; choosing to live in it is a bet that occupying the house is worth more than the " +
                      usd(shortfall) + " a year the model shows it costs, against letting the third unit of the building the heir already owns.")
        soft_rows = ranked_rows(horizon=2070, rate_key="soft")
        if soft_rows[0][0] != SELL_LABEL:
            body += prose("The one tested switch that reverses the answer", "Set the portfolio assumption to the soft scenario - " + pct(PORTFOLIO_RETURN["soft"], 1) + " a year before a " + pct(PORTFOLIO_TAX_DRAG["soft"], 1) + " tax drag, which is less than the modeled Treasury reserve pays while money waits - and the ranking turns: " + soft_rows[0][0] + " finishes about " + usd(soft_rows[0][2]) + " ahead at the twenty-five-year horizon, and the ten-year leader becomes " + ranked_rows(horizon=2055, rate_key="soft")[0][0] + ". That is not a forecast of a weak market; it is the one published condition under which this model stops recommending a sale, and the reason the investment policy is written as a rule with a review date before any money moves.")
        body += prose("What this answer is not", "It is not advice, not a valuation and not a forecast. It is the arithmetic the published assumptions produce, shown so the household can see precisely which assumption it would have to accept - or replace - to change its mind. " + MODEL_NOTE)
        return heading, lead, body

    if path.endswith("decision-analysis.html"):
        for horizon in (2055, 2070):
            rows = ranked_rows(horizon=horizon)
            body += table(f"Pure and mixed paths at identical dates: transfer 2045, horizon {horizon}", ["Path", "Net position", "Against selling in the transfer year", "Treatment inside the model"],
                          [row([label, usd(value), signed_usd(delta), detail], "assumption", ["irs_basis", "ca_rtc51", "irs_rental"]) for label, value, delta, detail in rows])
        growth_rows = []
        for scenario, growth in GROWTH_HOME.items():
            for horizon in (2055, 2070):
                ranked = ranked_rows(horizon=horizon, growth=growth)
                growth_rows.append(row([f"{scenario} growth: {pct(growth)} a year", f"horizon {horizon}", ranked[0][0], usd(ranked[0][1]), f"ahead of second place by {usd(ranked[0][1] - ranked[1][1])}", ranked[-1][0]], "assumption", ["fhfa", "cbo_long"]))
        body += table("Does the ranking survive the three value-growth scenarios?", ["Scenario", "Horizon", "Best path on these inputs", "Net position", "Margin", "Worst path"], growth_rows)
        year_rows = []
        for transfer_year in (2040, 2045, 2050):
            rows = path_outcomes(transfer_year, 2070)
            best = max(rows.items(), key=lambda item: item[1]["value"])
            year_rows.append(row([str(transfer_year), usd(market_value(transfer_year)), usd(tax_bill(transfer_year, transfer_year, "prop19")), usd(tax_bill(transfer_year, transfer_year, "reassessed")),
                                 usd(rows[SELL_LABEL]["value"]), usd(rows[RENT_LABEL]["value"]), usd(rows[LIVE_LABEL]["value"]), best[0]], "assumption", ["ca_rtc51", "boe_prop19", "irs_basis"]))
        body += table("The same model at each transfer year in the 2040-2050 window, horizon 2070", ["Transfer year", "Value at transfer", "Tax with a claim", "Tax with no claim", "Sell in the transfer year", "Rent it, sell in 2070", "Live in it, sell in 2070", "Best path on these inputs"], year_rows)
        sens = []
        for label, rate in (("tax rate at the low end of the reported bill history", RATE_A_LOW), ("tax rate derived from the reported bill history", RATE_A), ("tax rate at the high end of the reported bill history", RATE_A_HIGH)):
            bill = assessed_at_transfer(TRANSFER_YEAR, "reassessed") * rate
            sens.append(row([label, pct(rate), usd(bill), signed_usd(-(bill - bill_none)) + " a year", "Read the tax rate area on the actual bill and the county's published compilation."], "unverified", ["ca_rtc51", "boe_counties"]))
        for key in ("soft", "baseline", "strong"):
            rows = path_outcomes(horizon=2070, rate_key=key)
            margin = rows[SELL_LABEL]["value"] - rows[RENT_LABEL]["value"]
            phrasing = ("selling leads letting by " + usd(margin)) if margin >= 0 else ("letting leads selling by " + usd(-margin))
            sens.append(row([f"portfolio return {pct(PORTFOLIO_RETURN[key], 1)} less {pct(PORTFOLIO_TAX_DRAG[key], 1)} tax drag", f"{pct(net_rate(key), 1)} a year net", usd(rows[SELL_LABEL]["value"]), phrasing, "No official source forecasts a fifty-year equity return; all three are labelled scenarios."], "assumption", ["sec_stocks", "cbo_long"]))
        for label, insurance in (("insurance at the low end of the researched range", INSURANCE_A_YEAR[0]), ("insurance at the modeled midpoint", INSURANCE_A_YEAR[1]), ("insurance at the high end of the researched range", INSURANCE_A_YEAR[2])):
            per_year = (insurance - INSURANCE_A_YEAR[1]) * (1 + GROWTH_COST) ** (TRANSFER_YEAR - 2026)
            sens.append(row([label + f" (annual {usd(insurance)} in 2026)", "written quotes needed", usd(cost_item(insurance, TRANSFER_YEAR)), signed_usd(-per_year) + " a year at the transfer", "Two or three written quotes per building for the actual occupancy mix."], "unverified", ["cdi"]))
        for yield_rate, note in ((0.028, "a soft rental market"), (RENT_GROSS_YIELD, "the modeled gross yield"), (0.040, "a tight rental market")):
            gross = value_t * yield_rate
            operating = gross * (1 - VACANCY) - carrying_total(TRANSFER_YEAR, TRANSFER_YEAR, "reassessed") - gross * MANAGEMENT
            sens.append(row([f"gross rent yield {pct(yield_rate, 1)} of value ({note})", "three written comparables", usd(gross), f"net before income tax {usd(operating)} a year", "Rent comparables from local brokers plus the property's own letting history."], "missing", ["hud_fmr", "irs_rental"]))
        body += table("Assumption sensitivity: what moves the numbers, and what settles them", ["Switch", "Setting", "Modeled level at the transfer year", "Change against the baseline model", "Evidence that replaces the assumption"], sens)
        body += callout("Debt, occupancy and liquidity are part of the comparison, not footnotes", "The tables above assume no mortgage or lien on either building, that the heir already owns a home so no rent is forced by a sale, that one unit of the owned building can be let without ending an existing tenancy, and that no federal estate tax falls due at the transfer. Each is an unverified fact about this household, and each changes the arithmetic directly: a lien reduces net proceeds dollar for dollar, a forced housing cost turns the sell path into an outflow, an occupancy duty limits what can be let, and a federal filing puts a nine-month clock on an illiquid asset.", "warning")
        body += '<section class="prose"><h2>Local-only path ranking tool</h2><p>Change the transfer-year value, the tax rate, the rent yield, the other yearly carrying costs, the portfolio return, the reserve yield and the parking window to see whether the modeled ranking moves. Sale costs are fixed at 6.0 percent of value with 0.11 percent transfer tax and a small recording allowance; a sale at the horizon is taxed at 37.1 percent of the gain over the entered transfer-year value, with no depreciation or exclusion overlay; tax grows 2 percent a year and other costs 3 percent. That makes this a coarser view than the tables above, on purpose. Nothing is stored or transmitted, and every field clears when the page reloads. This repeats the arithmetic of the tables above; it is not a market forecast or a tax return.</p><div class="calculator">' \
                '<label>Home value at transfer ($) <input id="cmp-value" type="number" min="0" step="10" placeholder="Enter privately"></label>' \
                '<label>Property tax rate (%) <input id="cmp-rate" type="number" min="0" max="5" step="0.01" placeholder="From the tax bill"></label>' \
                '<label>Gross rent as a share of value (%) <input id="cmp-yield" type="number" min="0" max="15" step="0.1" placeholder="From written comparables"></label>' \
                '<label>Other carrying costs a year ($) <input id="cmp-costs" type="number" min="0" step="10" placeholder="Insurance, water, repairs, reserves"></label>' \
                '<label>Portfolio return, net of tax drag (%) <input id="cmp-portfolio" type="number" min="-10" max="20" step="0.1" placeholder="Scenario only"></label>' \
                '<label>Reserve yield while parked (%) <input id="cmp-reserve" type="number" min="-5" max="20" step="0.1" placeholder="Treasury readings"></label>' \
                '<label>Home value growth (%) <input id="cmp-growth" type="number" min="-10" max="20" step="0.1" value="3"></label>' \
                '<label>Parking window (months) <input id="cmp-window" type="number" min="0" max="60" step="1" value="30"></label>' \
                '<label>Years from transfer to horizon <input id="cmp-years" type="number" min="1" max="50" step="1" value="25"></label>' \
                '<button id="cmp-run" type="button">Run comparison</button><button id="cmp-clear" type="button">Clear</button>' \
                '<p id="cmp-result" role="status" aria-live="polite">No comparison run.</p></div></section>'
        return heading, lead, body

    if path.endswith("projections.html"):
        body += table("Modeled value, assessed value and tax by year, under each transfer branch", ["Year", "Value at 1.0% growth", "Value at 3.0% growth", "Value at 4.28% growth", "Assessed value while no transfer occurs", "Tax while no transfer occurs", "Assessed value with a Proposition 19 claim in 2045", "Tax with that claim", "Assessed value with no claim", "Tax with no claim"], projection_rows([2026, 2030, 2035, 2040, 2045, 2050]))
        body += prose("How to read the projection", "Columns two to four apply three growth assumptions to the household-reported value. Column five grows the current assessed value by the two percent statutory ceiling and stops there: while no change in ownership occurs, that is the taxable value. Columns seven and nine apply the two transfer branches at the modeled transfer year and then let the new base grow two percent a year. The Proposition 19 column keeps the factored base value and adds only the amount by which the value exceeds that base plus the indexed limit, which is why it lands between the other two - and why, with a base value near one sixth of the reported value, the claim helps without preserving today's bill. " + MODEL_NOTE)
        cost_rows = []
        for year in (2026, 2045, 2055, 2070):
            items = carrying_cost(year, TRANSFER_YEAR, "prop19" if year >= TRANSFER_YEAR else "keep-base", GROWTH_HOME["baseline"], "A")
            cost_rows.append(row([str(year)] + [usd(items[k]) for k in ("Property tax", "Insurance", "Water and sewer", "Routine maintenance", "Capital reserve", "Solar export credit")] + [usd(sum(items.values()))], "assumption", ["ca_rtc51", "cdi", "cpuc_solar", "water_board", "cslb"]))
        body += table("Property A carrying cost a year, live-in case", ["Year", "Property tax", "Insurance", "Water and sewer", "Routine maintenance", "Capital reserve", "Solar export credit", "Total a year"], cost_rows)
        b_rows = []
        for year in (2026, 2045, 2055, 2070):
            items = carrying_cost(year, TRANSFER_YEAR, "keep-base", GROWTH_HOME["baseline"], "B")
            gross = grown(B_RENT_TWO_UNITS_MONTH * 24, GROWTH_COST, year - 2026)
            operating = gross * (1 - VACANCY) - sum(items.values()) - gross * MANAGEMENT
            b_rows.append(row([str(year), usd(gross * (1 - VACANCY))] + [usd(items[k]) for k in items] + [usd(operating)], "assumption", ["irs_rental", "cdi", "cslb", "ca_rent"]))
        body += table("Property B cash flow a year, two units let and the third available to the owner", ["Year", "Collected rent", "Property tax", "Insurance (landlord policy)", "Water and sewer (three units)", "Shared electricity", "Routine maintenance", "Capital reserve", "Before income tax"], b_rows)
        dist_rows = [
            row(["Value at the transfer year", usd(sell["value"]), "Household-reported value grown at the baseline assumption; replace with a written date-of-death valuation and the contract price."], "unverified", ["irs_basis"]),
            row(["less sale costs at " + pct(FRICTIONS, 1), usd(-sell["frictions"]), "Brokerage, escrow, title, repair credits and concessions, as bid in writing."], "unverified", ["irs_pub551"]),
            row(["less documentary transfer tax", usd(-sell["transfer_tax"]), "The state authority sets 55 cents for each 500 dollars of consideration, with a city credit against the county amount, so the combined default is 0.11 percent of price."], "rule", ["ca_rtc11911"]),
            row(["less recording charges", usd(-RECORDING_FLAT), "A small flat allowance; the real total depends on the recorded documents and the county schedule."], "unverified", ["ca_gov27361"]),
            row(["net before income tax", usd(sell["net"]), "What the sale puts in hand before the tax year is computed; the exchange decision is measured against this."], "assumption", ["irs_pub551"]),
            row(["less modeled sale-year income tax", sell["tax"] > 0 and usd(-sell["tax"]) or "no modeled tax when the price equals the basis", "A sale at the stepped-up basis leaves almost no gain; a gap between the date-of-death value and the price is taxed, and California adds one percent of taxable income above the statutory threshold."], "rule", ["irs_basis", "ftb_540", "ftb_cap_gains"]),
            row(["net to invest or reserve", usd(sell["after_tax"]), "The only figure on which the paths should be compared."], "assumption", ["treasury_bills"]),
        ]
        body += table("Distribution of the modeled sale proceeds, rounded, transfer year 2045", ["Step in order", "Amount", "What sets this number"], dist_rows)
        body += waterfall_chart([("modeled value", sell["value"]), ("less sale costs", sell["frictions"]), ("less transfer tax and recording", sell["transfer_tax"] + RECORDING_FLAT), ("net to invest", sell["after_tax"])])
        items = [(label, value, "lead" if delta >= 0 else "behind") for label, value, delta, _ in ranked_rows(horizon=2070)]
        body += bar_chart(items, "Net position by path at the 2070 horizon, in millions of dollars; the tables carry the exact rounded figures")
        body += callout("Ranges, not round-number points", "Every ranking page publishes three value-growth scenarios, three portfolio-return scenarios, the low and high ends of the derived tax rate, the researched insurance range and a rent-yield band. A single point estimate is nowhere used as the basis for a recommendation. Re-run the model whenever an input changes and check whether the best path moved: that check is the deliverable, not the number.", "info")
        return heading, lead, body

    if path.endswith("property-profiles.html"):
        lookup_a = {year: (tax, assessed) for (year, tax, assessed) in A_BILL_HISTORY}
        a_hist = []
        for year, tax, assessed in A_BILL_HISTORY:
            prior = lookup_a.get(year - 1, (0, 0))[1]
            growth = "not comparable" if not prior else pct(assessed / prior - 1, 1)
            ratio = "bill not yet issued" if not tax else pct(tax / assessed)
            a_hist.append(row([str(year), usd(tax) if tax else "not issued in the reported record", usd(assessed), ratio, growth], "unverified", ["ca_rtc51", "boe_counties"]))
        body += table("Property A: tax and assessed value history as reported, rounded", ["Year", "Property tax", "Assessed value", "Tax as a share of assessed value", "Assessed value growth"], a_hist)
        lookup_b = {year: (tax, assessed) for (year, tax, assessed) in B_BILL_HISTORY}
        b_hist = []
        for year, tax, assessed in B_BILL_HISTORY:
            prior = lookup_b.get(year - 1, (0, 0))[1]
            growth = "not comparable" if not prior else pct(assessed / prior - 1, 1)
            b_hist.append(row([str(year), usd(tax), usd(assessed), pct(tax / assessed), growth], "unverified", ["ca_rtc51", "boe_counties"]))
        body += table("Property B: the same history for the building already owned", ["Year", "Property tax", "Assessed value", "Tax as a share of assessed value", "Assessed value growth"], b_hist)
        body += table("What the two bill histories already establish", ["Finding", "Modeled figure", "Consequence for the decision"], [
            row(["The inherited home is assessed at " + pct(assessed_untransferred(2026) / A_MARKET_2026, 1) + " of its reported value", usd(A_ASSESSED_2026) + " against " + usd(A_MARKET_2026), "Its carrying cost looks trivial today, at " + usd(bill_now) + " a year. That is a feature of the current owner's base value, not a right that survives the transfer."], "assumption", ["ca_rtc51", "boe_prop19"]),
            row(["The derived rate on the inherited home is " + pct(RATE_A), "range " + pct(RATE_A_LOW) + " to " + pct(RATE_A_HIGH), "Use it for projection only, until the tax rate area and its published rate are read from the actual bill and the county compilation."], "unverified", ["ca_rtc51", "boe_counties"]),
            row(["The owned building's bill implies " + pct(RATE_B), "range " + pct(RATE_B_LOW) + " to " + pct(RATE_B_HIGH), "That is far above the other parcel's ratio and above what a one percent limit plus ordinary voter-approved indebtedness explains; reconcile the bill lines before using either rate as a comparison."], "unverified", ["ca_rtc51", "boe_counties"]),
            row(["The owned building is a low-tax, high-cash-flow asset", usd(B_RENT_TWO_UNITS_MONTH * 24) + " of modeled rent against " + usd(grown(B_ASSESSED_2025, GROWTH_PROP13, 1) * RATE_B) + " of tax", "Keeping it is a separate decision from the inherited home, and its tax position is one reason not to sell or exchange it casually."], "assumption", ["irs_rental", "ca_rent"]),
        ])
        body += table("Model inputs, their basis, and what replaces each one", ["Input", "Basis in this build", "Rounded figure used", "Evidence that replaces the assumption"], [
            row(["Property A market value", "household estimate", usd(A_MARKET_2026), "Written date-of-death valuation; an online estimate is not a tax number."], "unverified", ["irs_basis"]),
            row(["Property A assessed value", "reported roll figure", usd(A_ASSESSED_2026), "Assessor confirmation of the base-year value and any new additions."], "unverified", ["ca_rtc51"]),
            row(["Property A rent if let", f"gross-yield assumption of {pct(RENT_GROSS_YIELD, 1)} of value", usd(RENT_GROSS_YIELD * A_MARKET_2026 / 12) + " a month", "Three written long-term comparables from different sources; until then the let paths are a floor, not a forecast."], "assumption", ["hud_fmr", "irs_rental"]),
            row(["Property A water and sewer", "household range", usd(A_WATER_MONTH[0] * 12) + " to " + usd(A_WATER_MONTH[2] * 12) + " a year", "Twelve months of actual bills plus the utility's published rate schedule."], "unverified", ["water_board"]),
            row(["Property A electricity with solar", "household range, a net credit", "from no credit to " + usd(A_SOLAR_CREDIT_MONTH[2] * 12) + " a year", "Interconnection date, export tariff and twelve months of bills; credits shrink as tariffs change and equipment ages."], "unverified", ["cpuc_solar"]),
            row(["Property A homeowner insurance", "researched range, no quote", usd(INSURANCE_A_YEAR[0]) + " to " + usd(INSURANCE_A_YEAR[2]) + " a year", "Two or three written homeowner quotes with identical limits and deductibles."], "unverified", ["cdi"]),
            row(["Property A maintenance and reserves", "planning range", usd(MAINTENANCE_A_YEAR[0] + CAPITAL_A_YEAR[0]) + " to " + usd(MAINTENANCE_A_YEAR[2] + CAPITAL_A_YEAR[2]) + " a year", "Inspection report and licensed bids; a percentage-of-value shortcut is not a bid."], "assumption", ["cslb"]),
            row(["Property B landlord insurance", "researched range, no quote", usd(INSURANCE_B_YEAR[0]) + " to " + usd(INSURANCE_B_YEAR[2]) + " a year", "Written landlord quotes for a three-unit building with one owner-occupied unit."], "unverified", ["cdi"]),
            row(["Property B rent for the two let units", "in-place leases to be supplied", usd(B_RENT_TWO_UNITS_MONTH * 2) + " a month combined", "The lease file, deposit records and any local rent or vacancy rule."], "missing", ["ca_rent", "irs_rental"]),
            row(["Debt on either building", "not established", "no lien modeled", "Loan statements and payoff figures; a lien changes net proceeds dollar for dollar."], "missing", ["irs_pub551"]),
        ])
        plan_rows = []
        capital_a = [("Year 1", "roof, gutter and envelope inspection; electrical panel and grounding; water heater age", 6_000),
                     ("Year 2", "plumbing valves and sewer lateral camera; bathroom and laundry ground-fault work", 5_000),
                     ("Year 3", "heating and cooling service, filter and duct review; inverter and monitoring check", 7_000),
                     ("Year 4", "exterior paint, deck and railing; window and door seals", 9_000),
                     ("Year 5", "paving and grading, fence, irrigation controller, seismic strapping review", 8_000)]
        for label, scope, amount in capital_a:
            plan_rows.append(row(["Property A " + label, scope, usd(amount), usd(amount * 5), "Two licensed bids per line before any carrying-cost comparison is treated as final."], "assumption", ["cslb"]))
        capital_b = [("Year 1", "unit-by-unit condition report; life-safety devices; egress and railing check", 12_000),
                     ("Year 2", "roof and flashing at both elevations; chimney and parapet work", 15_000),
                     ("Year 3", "three water heaters, laundry equipment and shared lighting", 10_000),
                     ("Year 4", "turn reserve for one unit; paint and flooring at the unit available to the owner", 14_000),
                     ("Year 5", "electrical service study for three units; repairs any insurer requires", 16_000)]
        for label, scope, amount in capital_b:
            plan_rows.append(row(["Property B " + label, scope, usd(amount), usd(amount * 5), "Confirm lawful unit status and permit history before budgeting any change to the unit mix."], "assumption", ["cslb", "ca_rent"]))
        body += table("Five-year maintenance and capital plan for both buildings", ["Plan year", "Scope to price", "Modeled amount a year", "Five-year total on these assumptions", "Before it becomes a number to rely on"], plan_rows)
        return "Rounded figure workbook", "The two buildings side by side: reported bill history, derived rates, cost ranges and a five-year capital plan - figures rounded, identifiers withheld.", body

    if path.endswith("operating-costs.html"):
        rows = []
        items_now = carrying_cost(2026, TRANSFER_YEAR, "keep-base", GROWTH_HOME["baseline"], "A")
        items_claim = carrying_cost(TRANSFER_YEAR, TRANSFER_YEAR, "prop19", GROWTH_HOME["baseline"], "A")
        items_none = carrying_cost(TRANSFER_YEAR, TRANSFER_YEAR, "reassessed", GROWTH_HOME["baseline"], "A")
        for label in items_now:
            rows.append(row(["Property A - " + label, usd(items_now[label]), usd(items_claim[label]), usd(items_none[label]), "Household range or planning assumption; replace with a bill, quote or bid."], "assumption", ["cdi", "cslb", "cpuc_solar", "water_board", "ca_rtc51"]))
        rows.append(row(["Property A - total a year", usd(sum(items_now.values())), usd(sum(items_claim.values())), usd(sum(items_none.values())), "The transfer year is where the total moves most, and it moves because of the assessed value rather than the sale price."], "assumption", ["ca_rtc51", "boe_prop19"]))
        items_b_now = carrying_cost(2026, TRANSFER_YEAR, "keep-base", GROWTH_HOME["baseline"], "B")
        for label in items_b_now:
            rows.append(row(["Property B - " + label, usd(items_b_now[label]), usd(cost_item(items_b_now[label], TRANSFER_YEAR)), usd(cost_item(items_b_now[label], 2055)), "Three-unit building with one unit available to the owner."], "assumption", ["cdi", "cslb", "water_board", "ca_rent"]))
        body += table("Cost lines the model uses, and where they land at the transfer year", ["Line", "2026", "2045 with an exclusion claim", "2045 with no claim", "Evidence to replace it"], rows)
        body += callout("The largest operating fact in this plan", "The inherited home's tax bill is modeled to rise from " + usd(bill_now) + " a year to " + usd(bill_claim) + " with a Proposition 19 claim, or " + usd(bill_none) + " without one. Insurance, water, maintenance and reserves are all smaller than that change; do not spend the first review round on them.", "warning")
        return heading, lead, body

    if path.endswith("black-swan.html"):
        body += table("Official baseline and record as read for this build", ["What the record shows", "Published figure", "What it does not say"], [
            row(["Ten-year economic baseline", "Real growth 2.2 percent in 2026 and 1.8 percent a year on average through 2036; price growth 2.7 percent in 2026 easing to about 2.0 percent by 2030; ten-year note 4.1 percent rising to 4.3 percent.", "It is a current-law ten-year baseline with published uncertainty, not a fifty-year forecast, and it carries a correction notice from the publisher."], "reference", ["cbo_outlook"]),
            row(["Baseline uncertainty in the same report", "For 2026 the publisher gives a two-thirds chance of growth between 0.5 and 3.9 percent, price growth between 1.7 and 3.7 percent, and a ten-year note between 3.5 and 4.8 percent.", "It does not describe the shape of the path inside those bounds, which is what a staged plan actually experiences."], "reference", ["cbo_outlook"]),
            row(["Recent inflation readings", "Monthly changes published for April to October 2026 compound to about 3.8 percent a year, above the baseline rate assumed for 2026.", "It does not predict next year, and the twelve-month change itself was not published because the prior October survey was not collected."], "historical", ["bls_cpi"]),
            row(["House prices", "A national repeat-sales index of 444.6 in August 2026 against 100 in January 1991 is about 4.28 percent a year nominal; the last twelve months were 2.4 percent nationally and 1.2 percent in the Pacific division.", "It is not an appraisal, and a smaller-area series was not read for this build. One chart block in the same release disagrees with its own table; the table figure is cited here."], "historical", ["fhfa"]),
            row(["Short Treasury yields for a reserve ladder", "Published par yield readings for 2026-01-30 and 2026-02-05 put the three-month bill at 3.67 percent and the two-year note between 3.47 and 3.52 percent.", "It says nothing about the yield available when the reserve must be renewed, which is the risk being modeled."], "reference", ["treasury_bills", "treasury_notes"]),
            row(["1929 episode", "A fall of about 89 percent from the September 1929 peak to the July 1932 low, with the prior high not regained until November 1954.", "It is one price index in one decade, not a probability that a portfolio repeats it."], "historical", ["fed_1929"]),
            row(["2007 to 2009 episode", "A 57 percent fall in the broad stock index from its October 2007 peak to its March 2009 trough, an average home-price fall of about 30 percent from the mid-2006 peak, and a 4.3 percent fall in output.", "The related aftermath account instead reports home prices falling by over a fifth from the first quarter of 2007 to the second quarter of 2011: the same episode measured over a different window."], "historical", ["fed_2007_2009", "fed_2008", "fhfa"]),
            row(["Data availability itself", "The October 2026 price report states that the prior October was not collected during the lapse in appropriations, so twelve-month changes could not be published for most indexes.", "A plan that depends on a smooth official series can stall on a data gap, so the input dates stay visible."], "reference", ["bls_cpi"]),
        ])
        amount = sell["after_tax"]
        staging_rows = []
        for label, months, decline, decline_months, recover, drift in STAGING_SHAPES:
            levels = index_path(months, decline, decline_months, recover, drift)
            base_value = staging_outcome(amount, levels, months, ("now",))
            for sname, strategy in STAGING_STRATEGIES:
                value = staging_outcome(amount, levels, months, strategy)
                staging_rows.append(row([label, sname, f"month {months}", usd(value), signed_usd(value - base_value)], "assumption", ["fed_1929", "fed_2007_2009", "treasury_bills", "sec_stocks"]))
        body += table("Staging the proceeds against stylized decline paths, on modeled net proceeds of " + usd(amount), ["Path shape", "Entry strategy", "Measured at", "Value", "Against buying in month one"], staging_rows)
        rising = index_path(120, 0, 0, None, 0.06)
        lag = staging_outcome(amount, rising, 120, ("park", 36)) - staging_outcome(amount, rising, 120, ("now",))
        body += callout("Read the table as a mechanism, not a forecast", "Each shape is a straight-line decline of the published percentage over the published number of months, then either flat or a straight-line recovery to the prior high, with the reserve earning " + pct(TREASURY_YIELD, 1) + " a year. No dividends, fees, tax on the reserve, index spread or inflation adjustment are modeled. Parking money and buying after the bottom looks brilliant on a path that falls and stops falling, and worse than buying at once on a path that only rises: in the rising case a 36-month park costs about " + usd(lag) + " over ten years. The point is not which row wins; it is that staging is insurance paid for with expected return. Note also that the largest apparent gains in the table come from buying at the bottom of a straight-line path, which no one can identify while living through it: those rows bound what perfect timing would be worth, not what a household should expect.", "warning")
        body += table("Regime blocks the household should plan against, not an average of them", ["Regime block", "What it looks like in the record", "What it does to these paths", "Planning rule"], [
            row(["Soft-money stretch", "Home values near inflation, portfolio returns modest, reserve yields low", "The sell path gains least and the let path gains little; holding looks harmless because the tax step-up dominates", "Do not let a soft decade set the policy; re-rank on the full set"], "assumption", ["bls_cpi", "fhfa"]),
            row(["Hot-inflation stretch", "Values and rents outrun costs, reserve yields lag prices, real returns on cash turn negative", "Both hold paths gain ground against the parked cash leg", "This is the case that punishes a long parking window most, the mirror image of the crash case"], "historical", ["fed_inflation", "bls_cpi"]),
            row(["Deflationary contraction", "Values fall, rents fall, vacancy rises, fixed costs do not; a short reserve earns a positive real return", "Staging and a cash reserve help; the owned building's vacancy and repairs hurt", "Model falling nominal rent and rising vacancy together, not only a price-index fall"], "historical", ["fed_depression", "bls_cpi"]),
            row(["Housing and equities fall together", "The 2007 to 2009 record shows both falling in the same episode", "A sell-and-invest path is not a safe harbor: the proceeds land in the same market the house just left", "Test correlated stress, plus a forced-sale calendar if liquidity is thin"], "historical", ["fed_2007_2009", "fhfa"]),
            row(["Long recovery", "The 1929 anchor took 25 years to regain its high", "A staged plan completed after the fall buys lower, but a household that needs the money mid-recovery cannot wait", "Write the withdrawal order before, not after"], "historical", ["fed_1929", "sec_stocks"]),
            row(["Uneven decades", "Fifty years is a sequence of these regimes rather than an average of them", "A single growth rate across fifty years is the error this page exists to prevent", "Run the model on regime sequences and report the range, not the mean"], "guidance", ["cbo_long", "bls_cpi", "fhfa"]),
        ])
        body += prose("What this build refuses to claim", "No source read here forecasts the next fifty years: the budget office publishes a ten-year baseline with stated uncertainty, the price and house-price series report what already happened, and the history pages describe episodes. Anything on this site that looks like a long-run growth rate is a labelled scenario used to test a decision rule. " + MODEL_NOTE)
        return heading, lead, body

    if path.endswith("phased-investing.html"):
        rows = []
        amount = sell["after_tax"]
        for window in (24, 30, 36):
            interest = amount * ((1 + TREASURY_YIELD / 12) ** window - 1)
            low = amount * ((1 + 0.015 / 12) ** window - 1)
            high = amount * ((1 + 0.045 / 12) ** window - 1)
            rising_cost = amount * ((1 + net_rate("baseline")) ** (window / 12) - 1) - interest
            rows.append(row([f"{window} months in three-month to two-year Treasuries", usd(interest), usd(low), usd(high), usd(rising_cost), f"deployment completes at month {window}", f"a six-month slip leaves the plan holding bills into month {window + 6}"], "assumption", ["treasury_bills", "treasury_notes", "cbo_outlook"]))
        body += table("The parking window: what it earns and what it costs, on modeled net proceeds of " + usd(sell["after_tax"]), ["Window", "Interest at the published short-yield reading", "If renewal yields fall to 1.5 percent", "If they rise to 4.5 percent", "Cost if the market simply rises", "Deployment date", "Consequence of a slip"], rows)
        body += callout("Reinvestment risk is the price of the protection", "A ladder of short bills pays whatever the next auction offers. If yields fall during the 24 to 36 months the reserve earns less than assumed and the plan still buys at whatever level the market reaches; if yields rise the household earns more but may be waiting for a reason. Any staging rule must therefore state three things in advance: the rung calendar, the condition under which the schedule is abandoned, and the date by which deployment completes whatever the market is doing.", "info")
        body += prose("Why this path is in the plan at all", "Selling in the transfer year is the most tax-efficient exit in the model, but it converts a physical asset into a sum that must be invested on a date the household did not choose. The staged path is the middle option between investing at once and holding off indefinitely: it caps how much of the proceeds is exposed to a decline in the first three years, at a cost that is computable now. " + MODEL_NOTE)
        return heading, lead, body

    if path.endswith("estate-thresholds.html"):
        excl_rows = []
        for year in (2026, 2027, 2030, 2035, 2040, 2045, 2050):
            if year <= 2027:
                amount = 15_000_000 if year == 2026 else 15_480_000
                note, status = "Published by the IRS for this year", "rule"
            else:
                amount = grown(15_480_000, 0.023, year - 2027)
                note, status = "Indexed at the baseline inflation rate as a scenario; the law can change before then", "assumption"
            excl_rows.append(row([str(year), usd(amount), usd(400_000), "official" if year <= 2027 else "scenario only", note], status, ["irs_2027", "congress_law"]))
        body += table("Federal exclusion by year of death, and the cost of exceeding it", ["Year of death", "Exclusion", "Tax on each million above it", "Is this an official figure", "Basis"], excl_rows)
        tax_rows = []
        for estate in (10_000_000, 15_000_000, 20_000_000, 30_000_000, 50_000_000):
            excess = max(0, estate - 15_000_000)
            share = "none on this illustration" if not excess else pct(excess * 0.40 / estate, 1)
            tax_rows.append(row([usd(estate), excess and usd(excess) or "below the exclusion on this illustration", excess and usd(excess * 0.40) or "no modeled federal tax", share, "Estate-level illustration only: deductions, debts, gifts since 1977 and any marital or charitable reduction are outside this arithmetic."], "guidance", ["irs_estate", "irs_706"]))
        body += table("Estate-level illustration at the 2026 exclusion of " + usd(15_000_000), ["Taxable estate", "Amount above the exclusion", "Tax at the top federal rate", "Share of the estate", "What this ignores"], tax_rows)
        body += callout("The exclusion is not a per-heir allowance and it is not an inheritance tax", "The federal test compares the gross estate plus adjusted taxable gifts against the exclusion for the year of death. California levies no estate tax on deaths on or after 2005-01-01 and no inheritance tax; what California taxes is income - a later sale, a rental profit, and one percent of taxable income above the statutory million-dollar threshold. Do not add a state inheritance percentage to a model of this transfer; it is not in the law read for this build.", "info")
        return heading, lead, body

    if path.endswith("questions.html"):
        known = [
            ("Federal estate-tax exclusion", usd(15_000_000) + " for deaths in 2026 and " + usd(15_480_000) + " for deaths in 2027, published on 2026-11-05; the filing test is at estate level and adds adjusted taxable gifts.", "Read from the estate-tax page and the 2027 inflation-adjustment release; that threshold table ends at 2026.", "rule", ["irs_estate", "irs_2027"]),
            ("Annual gift exclusion", usd(19_000) + " per recipient for 2026 and " + usd(20_000) + " for 2027; a gift exclusion is not an inheritance allowance.", "Read from the same IRS release.", "rule", ["irs_2027"]),
            ("California estate or inheritance tax", "The Controller's guidance says estate-tax returns are not required for deaths on or after 2005-01-01, and the death-transfer statute shows no current levy; California taxes capital gains as ordinary income.", "Read from the Controller's page, the statute and the Franchise Tax Board.", "rule", ["ca_sco", "ca_rtc13301", "ftb_cap_gains"]),
            ("California one percent above one million", "The 2025 Form 540 instructions, line 62, charge one percent of taxable income above " + usd(1_000_000) + " in whole dollars, which is " + usd(100) + " for each " + usd(10_000) + " above the threshold; the threshold is not doubled for joint filers and credits cannot offset it.", "Read from the Form 540 instructions and the implementing statute.", "rule", ["ftb_540", "ca_rtc17043"]),
            ("Proposition 19 value limit", "The indexed limit is " + usd(BOE_CAP) + " for transfers from 2025-02-16 to 2027-02-15, adjusted every other February by the California house-price index; the next adjustment is due in 2027.", "Read from the Board of Equalization letter to assessors and the implementing statute.", "rule", ["boe_lta", "ca_rtc63"]),
            ("Proposition 19 filing calendar", "Homeowners' exemption within one year of the transfer; the exclusion claim within three years or before a transfer to a third party; the claimant must occupy as a principal residence.", "Read from the Board's comparison chart and the two statutes.", "rule", ["boe_prop19", "ca_rtc63", "ca_rtc27388"]),
            ("Documentary transfer tax authority", "A county may charge 55 cents for each 500 dollars of consideration above 100 dollars, and a city inside such a county may charge half that with a credit against the county tax, so the combined default is 0.11 percent of consideration rather than 0.165 percent. The tax is computed on consideration exclusive of any lien remaining at the time of sale.", "Read from the Documentary Transfer Tax Act section itself.", "rule", ["ca_rtc11911"]),
            ("Inherited basis", "Federal rule: basis is generally fair market value at the date of death, subject to exceptions, alternate-valuation and reporting rules.", "Read from the IRS inheritance guidance and Publication 551.", "rule", ["irs_basis", "irs_pub551"]),
            ("Depreciation and recapture", "Residential rental property is recovered straight line over 27.5 years; the depreciation part of gain is federally taxed at a maximum 25 percent rate, and California taxes gain as ordinary income.", "Read from the rental publication, the capital-gain topic and the Schedule D instructions.", "rule", ["irs_rental", "irs_topic409", "irs_sched_d"]),
            ("Short Treasury yields used for staging", "Published par yield readings for 2026-01-30 and 2026-02-05 put the three-month bill at 3.67 percent and the two-year note between 3.47 and 3.52 percent; the ten-year note was 4.21 to 4.26 percent.", "Read from the Treasury daily par yield curve page; re-read the current curve at the decision date.", "reference", ["treasury_bills", "treasury_notes"]),
            ("Like-kind exchange scope", "Exchange treatment applies to real property held for business or investment, never to a principal residence or property held mainly for sale, and it runs on statutory deadlines with a qualified intermediary.", "Read from the IRS real-estate tax tips page.", "rule", ["irs_1031_tips"]),
            ("Monetary policy and the rate path", "The policy rate was reported held at a 3.75 to 4.00 percent target range on 2026-10-28, after a first increase since 2023 in the prior month, with a published longer-run median of 4.1 percent.", "Read from pages reporting the meeting rather than from the primary statement or the published projections file, so it is carried as unverified here.", "unverified", ["treasury_notes"]),
        ]
        body += table("Answers already established from official sources, each read 2026-11-16 or 2026-11-17", ["Question", "Established answer", "How it was read"],
                     [row([q[0], q[1], q[2]], q[3], q[4]) for q in known])
        unknown = [
            ("The date-of-death value of the inherited home", "An online estimate is not an appraisal, and a roll value is a tax figure rather than fair market value.", "Instruct a qualified appraiser for a date-of-death valuation; the trustee or executor engages it and keeps the report privately.", "missing", ["irs_basis"]),
            ("Whether the heir will actually occupy the home", "The exclusion depends on principal-residence occupancy and a timely exemption filing; a later change of use can end the treatment.", "The heir writes a dated occupancy intention before any claim is filed; counsel reviews the consequences of a later change.", "missing", ["boe_prop19", "ca_rtc63"]),
            ("The tax rate area and its published rate for each parcel", "This build derives a rate from household-reported amounts; only the bill and the county compilation establish the rate a projection should use.", "Read the tax rate area line on the actual bill and the county's published rate schedule; separate any direct assessment.", "unverified", ["ca_rtc51", "boe_counties"]),
            ("Lawful unit count, leases and local rules for the owned building", "Nothing in a public project can establish permits, tenancy terms, deposit ledgers or a local vacancy rule.", "Collect leases, deposit records, permits and inspection history; counsel checks the local ordinance before any change to the unit mix.", "missing", ["ca_rent", "irs_rental"]),
            ("Insurance premium for each building", "Third-party average-premium tables disagree with one another by hundreds of dollars for the same market, so this build uses a labelled range only.", "Two or three written quotes per building with identical limits, deductibles and occupancy descriptions.", "unverified", ["cdi"]),
            ("Market rent for the inherited home", "A program fair-market-rent schedule is a benchmark, not a comparable for a single-family home in a specific market.", "Three written long-term comparables from local brokers plus the property's own letting history.", "missing", ["hud_fmr", "irs_rental"]),
            ("Estate size, prior gifts and portability", "Only a confidential estate inventory can show whether a federal filing is required.", "Prepare the inventory, list adjusted taxable gifts since 1977, and check any prior decedent's unused exclusion with counsel.", "missing", ["irs_estate_faq", "irs_706"]),
            ("Whether an exchange is wanted instead of a sale", "Exchange treatment needs a business or investment holding, a qualified intermediary and statutory deadlines, and never applies to a principal residence.", "Decide in writing before any listing and obtain a tax counsel memo; record the decision and its date on the log.", "guidance", ["irs_1031_tips"]),
            ("Existing debt, insurance bindings and title exceptions", "Not readable from public information, and each changes either the proceeds or what is even possible.", "Loan statements, payoff figures, the title report and current declarations, kept out of this repository.", "missing", ["irs_pub551"]),
        ]
        body += table("Still unknown, and the specific act that discovers it", ["Unknown", "Why the model cannot fill it", "Discovery step, and who does it"],
                      [row([u[0], u[1], u[2]], u[3], u[4]) for u in unknown])
        body += prose("The rule this page enforces", "A blank row here is a task, not a zero. Where an official source cannot be read, the figure is left out of the ranking and the item appears on the Flagged for review page with the step that would settle it. Every row above was written before the model was run, so no answer was shaped to fit a preferred path.")
        return heading, lead, body

    if path.endswith("inheritance-process.html"):
        steps = [("Order 1", "Death occurs; certified copies of the certificate are obtained", "within weeks", "the date fixes the date-of-death value, the tax year and every deadline below", "ca_prob"),
                 ("Order 2", "Trustee gives the statutory notice to heirs and beneficiaries", "generally 60 days for specified events", "notice content and recipients carry their own consequences", "ca_prob"),
                 ("Order 3", "Change-in-ownership statement filed with the assessor", "150 days in specified death transfers", "this filing tells the assessor a transfer happened; it is not the exclusion claim", "ca_rtc480"),
                 ("Order 4", "Written date-of-death valuation ordered", "before the estate return", "one report can serve the estate value, the income-tax basis and the exclusion test, but read it for each purpose", "irs_basis"),
                 ("Order 5", "Estate inventory: assets, debts, insurance, leases, prior gifts", "concurrent", "decides whether a federal return is required and whether liquidity exists", "irs_estate"),
                 ("Order 6", "Proposition 19 decision and occupancy commitment", "exemption within one year; claim within three years", "claim only if the heir will actually occupy as a principal residence", "boe_prop19"),
                 ("Order 7", "Trustee deeds or distributes per the trust instrument", "after tax and creditor steps", "record the deed and obtain the recorder's charge schedule in writing", "ca_gov27361"),
                 ("Order 8", "Utilities, insurance, interconnection and the tax bill moved to the new owner", "immediately after recording", "insurance must be re-underwritten for the occupancy change; a let or vacant building is not covered by the prior policy", "cdi"),
                 ("Order 9", "Sell, rent or occupy decided with the after-tax comparison priced", "before any listing", "same transfer date, horizon, tax year and cost stack for every path", "irs_pub551"),
                 ("Order 10", "Written exchange decision if one is even wanted", "before any listing agreement", "an exchange has statutory deadlines and never applies to a principal residence", "irs_1031_tips"),
                 ("Order 11", "Close, with the enacted transfer-tax schedule read at the closing", "per contract and local rule", "read the local ordinance rather than a proposal digest", "ca_rtc11911"),
                 ("Order 12", "Investment policy adopted before the money arrives", "before distribution", "liquidity reserve, staging schedule, drawdown limits, review date and approver", "treasury_bills"),
                 ("Order 13", "Estate and fiduciary income-tax returns filed if required", "nine months; extensions are separate", "file and pay on time, and keep the basis schedule with the return", "irs_706"),
                 ("Order 14", "Model re-run with actual figures, then annually", "each year and at each decision", "record the decision, the date and the reason on the log", "boe_lta")]
        body += table("The transfer, step by step, with the reason each step exists", ["Order", "Step", "Timing", "Why it matters to the decision"],
                     [row([order, step, timing, why], "guidance", [ref]) for order, step, timing, why, ref in steps])
        body += callout("Two lessons the sequence teaches", "First, the assessor filings and the exclusion claim run their own clocks while the household is still deciding what to do with the house, so the decision is time-limited even though the market is not. Second, most of these steps produce documents worth more to the plan than any forecast: the appraisal, the lease file, the insurance binder, the tax bill lines and the loan statement. Collect them first and the model becomes arithmetic instead of argument.", "info")
        return heading, lead, body

    if path.endswith("attorney-cpa-brief.html"):
        body += table("Key figures for the meeting, rounded; exact records stay in the private file", ["Item", "Figure as modeled", "Document to bring instead"], [
            row(["What the inherited home costs after the transfer", usd(bill_now) + " a year today, rising to " + usd(bill_claim) + " with a Proposition 19 claim or " + usd(bill_none) + " without one", "The tax bill lines, the tax rate area, and a written eligibility review."], "assumption", ["ca_rtc51", "boe_prop19"]),
            row(["Modeled net proceeds from a transfer-year sale", usd(sell["after_tax"]) + " on a value of " + usd(sell["value"]), "The appraisal, the contract price, the closing statement and the CPA's sale-year computation."], "assumption", ["irs_basis", "ca_rtc11911"]),
            row(["Ranking on the published assumptions", "selling in the transfer year leads every hold path at both the 2055 and 2070 horizons, in all three growth scenarios", "Rent comparables, contractor bids and insurance quotes: the assumptions with the most leverage."], "assumption", ["hud_fmr", "cslb", "cdi"]),
            row(["Break-even growth for holding instead of selling", pct(break_even_growth(RENT_LABEL, horizon=2055)) + " a year to 2055; " + pct(break_even_growth(RENT_LABEL)) + " a year to 2070", "Confirmation that the tax treatment behind the arithmetic is right."], "assumption", ["irs_topic409", "ftb_cap_gains", "ca_rtc63"]),
            row(["Estate-level federal exposure", "exclusion of " + usd(15_000_000) + " for 2026 deaths and " + usd(15_480_000) + " for 2027; later years are not law yet", "Estate inventory, gift history since 1977, portability facts and a liquidity plan."], "rule", ["irs_2027", "irs_estate_faq"]),
            row(["Staged entry decision", "30 months in short Treasuries costs about " + usd(staging_gap) + " at 2070 if prices only drift up", "A signed investment policy stating the rung calendar, the exception conditions and the completion date."], "assumption", ["treasury_bills", "sec_stocks"]),
        ])
        body += '<p class="print-note">Print at 100 percent, portrait; if the browser spills to a second page choose Fit to width or reduce to 90 percent.</p>'
        return heading, lead, body

    if path.endswith("decision-log.html"):
        logged = [
            (["Adopt a rounded-figure publication policy", "2026-11-17", "Publish amounts rounded to the nearest ten dollars, with no locality, parcel, account or party identifiers, because a ranking cannot be reviewed at all without figures and rounding removes exact-match tracing.", "Owner instruction recorded on the coordination board; the verifier's currency and identifier rules enforce it on every build.", "Any request to publish an unrounded figure, or a change in what the owner treats as sensitive."], "guidance", ["irs_basis"]),
            (["Model the transfer in 2045, and also at 2040 and 2050", "2026-11-17", "The planning window is 2040 to 2050, so a midpoint case plus both ends is published rather than one arbitrary date.", "Labelled assumption; the model re-runs in seconds when the window changes.", "Any confirmed change to the expected transfer window."], "assumption", ["irs_estate_faq"]),
            (["Use the statutory Proposition 19 formula instead of a claim that the low tax is kept", "2026-11-17", "The exclusion keeps the factored base value and adds only the amount by which value exceeds the base plus the indexed limit; with a base near one sixth of the reported value, the claim helps but does not preserve today's bill.", "Read from the implementing statute, the Board's comparison chart and the indexed-amount notice.", "A published correction to the indexed limit, or an assessor determination that differs."], "rule", ["ca_rtc63", "boe_prop19", "boe_lta"]),
            (["Add the staged Treasury path to the stress tests rather than to the headline", "2026-11-17", "Parking proceeds for 24 to 36 months in short bills changes entry risk, so it must appear against the decline paths and the rising path in the same table; it is a risk rule, not a return forecast.", "Computed on stylized paths from the published episode anchors, with the reinvestment cost stated in the same row.", "Adoption of an investment policy with a different staging rule, or a material change in short-term yields."], "assumption", ["treasury_bills", "fed_1929", "sec_stocks"]),
            (["Publish 0.11 percent rather than 0.165 percent as the transfer-tax default", "2026-11-17", "The state authority allows a county 55 cents per 500 dollars and a city inside such a county one-half of that, with the city tax credited against the county tax, so the combined default is one rate rather than the two added.", "Read from the statute section itself; the local ordinance still has to be read for the subject buildings.", "The enacted county and city schedules for the actual sale."], "rule", ["ca_rtc11911"]),
            (["Flag the owned building's derived tax ratio instead of reconciling it", "2026-11-17", "Its bill implies a share of assessed value nearly double the other parcel's and far above what a one percent limit plus ordinary voter-approved indebtedness explains; the difference lives in the bill lines, not in a public build.", "Deliberately left unresolved, with the actual bill and the county compilation named as the source that settles it.", "The owner's tax bill lines are read and the components identified."], "unverified", ["ca_rtc51", "boe_counties"]),
            (["Refuse to publish a locality, a program rent benchmark, or a premium table as fact", "2026-11-17", "Parcel-specific rates, quotes and comparables are obtainable only privately; substituting a benchmark or a third-party average would dress a guess as a source.", "Kept as labelled ranges with the evidence step named, and recorded on the flagged page.", "Written quotes, a broker letter or an assessor statement arrives."], "guidance", ["cdi", "hud_fmr", "ca_rtc51"]),
            (["Re-attribute two historical figures found mis-sourced in an earlier build", "2026-11-17", "The 57 percent and approximately 30 percent declines belong to the account of the 2007 to 2009 recession, and the aftermath account instead reports home prices falling over a fifth on a different window; both are correct measurements of different spans.", "Corrected in the source register and shown with the measurement window beside each figure.", "A reviewer prefers a different window, in which case both are cited."], "rule", ["fed_2007_2009", "fed_2008"]),
        ]
        body += table("Decisions taken in this build, with the date and the reason", ["Decision", "Date", "Why", "What it rests on", "What reopens it"],
                     [row([d[0][0], d[0][1], d[0][2], d[0][3], d[0][4]], d[1], d[2]) for d in logged])
        return heading, lead, body

    if path.endswith("flagged-for-review.html"):
        flagged = [
            ("The derived tax ratio on the already-owned building does not reconcile", "The reported bill history implies " + pct(RATE_B) + " of assessed value (range " + pct(RATE_B_LOW) + " to " + pct(RATE_B_HIGH) + ") against " + pct(RATE_A) + " for the inherited home. A one percent limit plus ordinary voter-approved indebtedness does not explain a ratio that far above the other parcel, so the reported line is probably a different measure or includes direct charges.", "Read the actual bill: base levy, voter-approved indebtedness, direct assessments and any non-ad-valorem item; then re-read the tax rate area from the county's published compilation and replace the derived rate.", "unverified", ["ca_rtc51", "boe_counties"]),
            ("No property-specific rate area has been read for either building", "Only a parcel's own bill and the county's official compilation establish the rate a projection should use; this build derives a rate from household-reported amounts instead.", "Obtain the bill lines and the compilation, replace the derived rate, and re-run the projection page and the ranking.", "missing", ["ca_rtc51", "boe_counties"]),
            ("Insurance figures are researched ranges, not quotes", "Third-party average-premium tables disagree with one another by hundreds of dollars a year for the same market, which shows they are quote models. Nothing in this build reads a carrier quote for either building or its occupancy mix.", "Two or three written quotes per building with identical limits, deductibles and occupancy descriptions; until then insurance is a flagged range, not a fact.", "unverified", ["cdi"]),
            ("Rent for the inherited home is a yield assumption, not a comparable", "No written comparable is available in a public source, and a program fair-market-rent schedule is not evidence of a private letting price.", "Three written long-term comparables from local brokers plus the property's own letting history, then re-rank the let paths.", "missing", ["hud_fmr", "irs_rental"]),
            ("The 2008-style recovery window in the staging table is assumed", "The trough depth and decline length come from the published episode account; the month at which the prior high is regained is an input used to complete the arithmetic, not a published fact.", "Read a long-horizon index series directly if a specific recovery date is to be relied on; the table already shows the no-recovery case beside it.", "assumption", ["fed_2007_2009", "sec_stocks"]),
            ("Monetary-policy and rate-path statements rest on secondary reports", "The target-range holding and the projections median cited on the questions page were read from pages reporting the meeting, not from the primary statement or the published projections file.", "Read the primary statement and the summary of economic projections before any reserve-ladder decision; yields move the staging case directly.", "unverified", ["treasury_notes"]),
            ("Official baselines carry their own corrections and gaps", "The ten-year baseline used here states uncertainty ranges and was corrected after publication, and a lapse in appropriations removed a prior-year survey so some twelve-month changes could not be published.", "Date every baseline figure, re-read the current edition annually, and keep an explicit no-data branch in the model instead of interpolating.", "reference", ["cbo_outlook", "bls_cpi"]),
            ("This build publishes rounded household-derived figures", "Earlier sessions removed all amounts from the public site. On the owner's instruction the analysis now publishes amounts rounded to the nearest ten dollars with no identifiers, because a ranking cannot be checked without figures.", "If the owner prefers the earlier boundary, the same tables can be regenerated with blank amounts in a single build; nothing else in the site depends on the figures.", "guidance", ["irs_basis"]),
            ("History remediation remains an owner and administrator action", "A branch commit and a site rebuild cannot remove earlier commits, pull-request views, forks, caches, downloads or clones, and pre-rounding drafts exist in this repository's history.", "Administrator-led assessment with GitHub's guidance and support, with an encrypted private archive preserved before any destructive action.", "missing", ["github_sensitive"]),
        ]
        body += table("New or changed items in this build", ["Flag", "What is not established here", "What settles it"],
                      [row([f[0], f[1], f[2]], f[3], f[4]) for f in flagged])
        return heading, lead, body

    if path.endswith("glossary.html"):
        terms = [
            ("Break-even appreciation rate", "The yearly growth the home itself must deliver for a hold path to match the sell-and-invest path on the same costs and dates: a hurdle, not a forecast.", "Compare it with the published long-run house-price record rather than with a hope.", ["fhfa", "cbo_long"]),
            ("Carrying cost", "Property tax, insurance, water and sewer, maintenance and the capital reserve, less any energy credit: what the asset costs to hold for a year.", "Replace each line with a bill or a bid, one row at a time.", ["cdi", "cslb", "water_board"]),
            ("Gross rent yield", "Annual market rent divided by the home's value; used here to translate a value into a rent where no comparable exists.", "Treat it as a placeholder until written comparables arrive.", ["hud_fmr"]),
            ("Imputed rent", "The housing value the household consumes by living in the home rather than letting it; already modeled as the third unit's foregone rent in the live paths.", "Keep it visible: an owner-occupied home earns nothing it does not also spend.", ["hud_fmr"]),
            ("Regime sequence", "A stretch of years dominated by one condition - high inflation, deflation, a crash, a quiet recovery - rather than an average of all of them.", "Run the model on sequences and report the range of outcomes.", ["fed_inflation", "fed_depression", "cbo_long"]),
            ("Reserve ladder", "Short bills and notes maturing in step with the planned purchase schedule, so cash arrives when it is needed.", "Match each rung's maturity to a scheduled purchase, and model the renewal yield.", ["treasury_bills", "treasury_notes"]),
            ("Staging, or phased entry", "Moving a lump sum into a portfolio on a fixed calendar instead of at once: it limits early loss and gives up early gain.", "State the calendar, the exception conditions and the completion date in the policy.", ["sec_stocks", "treasury_bills"]),
            ("Deflation advantage of a reserve", "In falling prices a short-reserve holding earns a positive real return even at a low nominal yield; in rising prices the same holding loses ground.", "Test both directions in the same table rather than only the crash case.", ["fed_depression", "bls_cpi"]),
            ("Tax rate area", "The zone that fixes which jurisdictions levy on a parcel and at what combined rate; printed on the tax bill.", "Read it from the bill and the county's published compilation, never from a neighbouring parcel.", ["ca_rtc51", "boe_counties"]),
            ("Factored base-year value", "The assessable value carried forward under the base-year system; distinct from market value and from income-tax basis.", "Ask the assessor for the roll figure and the base year.", ["ca_rtc51", "ca_rtc63"]),
        ]
        body += table("Terms used by the rounded model", ["Term", "Meaning in this project", "How to use it"],
                     [row([t[0], t[1], t[2]], "guidance", t[3]) for t in terms])
        return heading, lead, body

    if path.endswith("requirements-tracker.html"):
        done = [
            ("Rounded figures in the decision analysis", "Done 2026-11-17 in this build: the workbook, projection, comparison, cost and brief pages publish amounts rounded to the nearest ten dollars, with no locality, parcel, account or party identifiers.", "Replace each assumption with a bill, quote, appraisal or bid as it arrives, then rebuild.", "guidance"),
            ("Phased-investing path inside the stress tests", "Done 2026-11-17: short Treasuries for 24 to 36 months computed against stylized 1929 and 2008 paths and against a rising market, with the reinvestment cost in the same table.", "Re-read the yield curve and re-run at the decision date.", "assumption"),
            ("Regime-based economics instead of one growth rate", "Done 2026-11-17: three growth scenarios, three portfolio-return scenarios and six regime blocks, each citing the official figure it borrows its shape from.", "No source forecasts fifty years, so everything stays labelled as a scenario.", "assumption"),
            ("Year-by-year value, assessed value and tax projection", "Done 2026-11-17 on the projection page, for three transfer branches and both buildings.", "Assessor confirmation of the base value and of the transfer treatment.", "assumption"),
            ("Distribution chart of the sale proceeds", "Done 2026-11-17: the proceeds table and a local chart on the projection page; nothing is stored or transmitted.", "The closing statement and the CPA's computation replace the modeled lines.", "assumption"),
            ("Path comparison at identical dates and horizons", "Done 2026-11-17: eight pure and mixed paths at 2040, 2045 and 2050 with taxes, occupancy, capital costs, liquidity notes and reinvestment risk.", "Debt, lease and occupancy facts are still missing; the callout names them.", "assumption"),
            ("Five-year maintenance and capital plan for both buildings", "Done 2026-11-17 with planning amounts and an instruction to replace them with licensed bids.", "Inspection report and bids.", "assumption"),
            ("Estate thresholds verified for 2026 and 2027, indexed scenario beyond", "Done 2026-11-17 from the release dated 2026-11-05 and the estate-tax filing table; later years are labelled scenarios.", "Recheck annually; a proposal is not law.", "rule"),
            ("Official baseline and record re-read for this build", "Done 2026-11-17: baseline outlook, price release, house-price index and Treasury yield readings, each with its read date and stated limits.", "Re-read before the decision; the baseline was corrected after publication once already.", "reference"),
            ("Prop 19 eligibility, depreciation and recapture, transfer tax and recording, the home-sale exclusion switch, imputed rent", "Carried from earlier builds and now priced in the model: the claim formula, the 27.5-year recovery with a 25 percent federal recapture ceiling, transfer tax on consideration, a recording allowance, an exclusion switch and the third unit's foregone rent.", "Written assessor determination, depreciation schedule, local ordinance and the occupancy record.", "rule"),
            ("Private unrounded workpaper", "Held outside the repository in an ignored directory; the public tree carries no exact value, no identifier and no document.", "The owner keeps it encrypted and off any public remote.", "guidance"),
        ]
        body += table("Status of the requested work as of 2026-11-17", ["Request", "Where it stands in this build", "Remaining evidence"],
                     [row([d[0], d[1], d[2]], d[3], ["irs_basis", "ca_rtc51"]) for d in done])
        return heading, lead, body

    if path.endswith("suggestions.html"):
        queue = [
            ("Replace the three biggest assumptions first: appraisal, insurance quotes, rent comparables", "Highest", "These three move the ranking; the rest move only the totals.", "Instruct the appraiser, request two written quotes per building, and ask two brokers for written comparables.", ["irs_basis", "cdi", "hud_fmr"]),
            ("Confirm there is no mortgage, lien or judgment on either building", "Highest", "A lien changes net proceeds dollar for dollar and can change what is even possible.", "Title report and loan statements, kept privately.", ["irs_pub551"]),
            ("Reconcile the owned building's tax bill lines before trusting any rate", "High", "Two derived rates differ by nearly double, and one of them is probably measuring something other than the ad valorem levy.", "The actual bill plus the county's published rate compilation.", ["ca_rtc51", "boe_counties"]),
            ("Write the occupancy decision before the claim, not after", "High", "The exclusion depends on principal-residence occupancy and on a filing within one year; a later rental can end the treatment.", "A dated written intention signed by the heir, reviewed by counsel.", ["boe_prop19", "ca_rtc63"]),
            ("Decide whether the third unit of the owned building is let", "High", "The model prices every live-in path as the difference between that rent and the inherited home's carrying cost, so this choice is already inside the ranking.", "Verify lawful unit status, lease duties and local rules first.", ["ca_rent", "irs_rental"]),
            ("Adopt the investment policy before any money arrives", "High", "A written rule is the only defense against deciding under the influence of a headline.", "Sign the draft policy with a liquidity floor, a staging schedule and a review date.", ["treasury_bills", "sec_stocks"]),
            ("Settle the exchange question before listing anything", "Medium", "It must be decided before the sale, and it never applies to a principal residence.", "A tax counsel memo with a date, filed with the policy.", ["irs_1031_tips"]),
            ("Add an estate-liquidity line even if the estate looks below the exclusion", "Medium", "The exclusion is indexed and the law can change; liquidity planning is cheap now and expensive at a death.", "Inventory, gift history and a funding route priced while it can still be shopped.", ["irs_estate_faq", "irs_706"]),
            ("Re-run the model on a date, once a year", "Medium", "Annual re-runs catch a ranking change while the household still has time to act.", "Calendar the review and record each run and its outcome on the decision log.", ["fed_1929", "boe_lta"]),
            ("Keep the public site and the private file separated by construction", "Medium", "The public tree now carries rounded figures by the owner's choice, which only works if the exact records never enter Git.", "An encrypted private store with a named owner; nothing personal in this repository.", ["github_sensitive"]),
            ("Do not let a single baseline rate set the plan", "Low", "The official baseline is a ten-year view with published uncertainty and one correction; a fifty-year plan should show a band.", "Keep the three-scenario tables and re-read the baseline annually.", ["cbo_outlook", "bls_cpi"]),
            ("Print the one-page brief and complete it in the meeting", "Low", "A short shared document reduces how much is answered from memory.", "Bring the brief, the modeled inputs and the questions page; leave the exact figures in the private file.", ["irs_estate_faq", "boe_prop19"]),
        ]
        body += table("Review queue, ranked by the effect each item has on the answer", ["Suggestion", "Priority", "Why it is ranked here", "First action"],
                      [row([q[0], q[1], q[2], q[3]], "guidance", q[4]) for q in queue])
        body += prose("What happens to a suggestion after review", "Each item is adopted, deferred or rejected on the decision log with a date and a reason, and nothing on this page is implemented by the site itself. The queue is a review instrument, not a to-do list the build silently completes.")
        return heading, lead, body

    if path.endswith("law-watchlist.html"):
        watch = [
            ("Federal estate and gift amounts", "The IRS published a 2027 exclusion of " + usd(15_480_000) + " and a " + usd(20_000) + " annual gift exclusion on 2026-11-05, against " + usd(15_000_000) + " and " + usd(19_000) + " for 2026. These are enacted and current.", "Re-read each autumn: for a 2045 transfer the indexation formula matters more than the amount.", "rule", ["irs_2027", "irs_estate"]),
            ("Itemized state-and-local deduction limit", "Third-party summaries describe a temporary " + usd(40_000) + " limit for tax years 2025 through 2029 and a return to " + usd(10_000) + " afterwards, enacted with the 2025 reconciliation act. This build did not read those amounts from an official page, so they are recorded as unverified.", "Read the IRS instructions for the actual year before using any deduction limit in the holding-cost arithmetic: a post-transfer property tax bill can exceed the limit on its own.", "unverified", ["congress_law", "irs_estate"]),
            ("Proposition 19 indexed limit", "The limit stands at " + usd(BOE_CAP) + " for transfers from 2025-02-16 to 2027-02-15, adjusted every other February by the California house-price index; the next adjustment is due in 2027. Nothing published fixes a future amount.", "Use the amount in force at the actual transfer date and keep the notice; never build a plan on a projected limit.", "rule", ["boe_lta", "ca_rtc63"]),
            ("California top rate and surcharge", "Capital gains are taxed as ordinary income, and the 2025 Form 540 line 62 instruction charges one percent of taxable income above " + usd(1_000_000) + "; the statute does not index that threshold in its text.", "Re-read the Form 540 instructions for the sale year; the structure, not the 2025 amount, is what a future sale will meet.", "rule", ["ftb_cap_gains", "ftb_540", "ca_rtc17043"]),
            ("Baseline revisions and data gaps", "The current ten-year baseline was corrected after publication and states its own uncertainty ranges; a lapse in appropriations removed a prior-year survey, so some twelve-month changes could not be published.", "Treat a baseline as a dated input: record the edition and the read date every time it is used, and keep a no-data branch in the model.", "reference", ["cbo_outlook", "bls_cpi"]),
            ("Local vacancy measures and transfer-tax proposals", "Jurisdiction-specific vacancy taxes and tiered transfer-tax changes exist as measures, litigation and digest summaries. None of them is an enacted schedule this build read for the subject buildings.", "Read the property's own current ordinance and enacted transfer-tax schedule at decision time, and keep every proposal labelled as a proposal.", "unverified", ["sos_measures", "ca_rtc11911"]),
        ]
        body += table("Enacted, dated and re-checked for this build", ["Item", "What is enacted, and what this build did not verify", "Refresh rule"],
                     [row([w[0], w[1], w[2]], w[3], w[4]) for w in watch])
        return heading, lead, body

    if path.endswith("privacy.html"):
        rows = [
            ("Rounded figures, no identifiers", "The site publishes figures rounded to the nearest ten dollars, with no locality, postal identifier, parcel, account or party name. Exact values live in a private, ignored file that never enters Git.", "Rounding reduces exact-match tracing; it is not a promise of anonymity. A value plus a decade plus a description can still identify a property, so descriptions stay generic.", "guidance"),
            ("No household identifiers in the public tree", "The verifier fails the build on postal-like patterns, contact patterns, address patterns, email, non-visible attributes and comments, and rejects any unrounded currency amount.", "The checks are pattern-based; an owner or adviser must still read the pages for anything a pattern cannot know.", "guidance"),
            ("Private workpaper location", "Unrounded inputs, the rate-area reading, quotes and the estate inventory belong in an encrypted private store that is not this repository.", "Name one owner and one review date for that store; a public Pages site cannot be the case file.", "missing"),
            ("Searchability of the site itself", "Every page is marked noindex, nofollow and noarchive, the site runs no analytics and makes no network request, and the repository is a separate exposure from the website.", "A repository and its pull requests reach a different audience than a search engine; treat all three as public.", "guidance"),
            ("History from before the rounding policy", "Earlier commits and pull requests contain drafts written before this policy existed. This build does not rewrite history and does not claim any prior copy is gone.", "Owner and administrator action, with GitHub guidance and support, and a private archive preserved first.", "missing"),
        ]
        body += table("Privacy controls as they stand in this build", ["Control", "What it does now", "What it cannot do"],
                     [row([r[0], r[1], r[2]], r[3], ["github_sensitive"]) for r in rows])
        return heading, lead, body

    if path.endswith("investment-policy.html"):
        params = [
            ("Liquidity floor", "18 months of carrying cost for any retained property, plus one year of household outgoings", usd((carrying_total(TRANSFER_YEAR, TRANSFER_YEAR, "prop19") + 40_000) * 1.5), "Held in the shortest rungs and never invested to catch a return.", ["treasury_bills"]),
            ("Staging schedule", "Purchase tranches on a fixed calendar over 24 to 36 months, each rung maturing as its tranche is spent", pct(TREASURY_YIELD, 1) + " a year assumed on the reserve", "The schedule completes on its date whatever the market is doing.", ["treasury_bills", "sec_stocks"]),
            ("Abandonment condition", "Only a written amendment by the named approver may change the calendar; a headline is not an amendment", "no discretionary change", "Removes the temptation to decide during the episode the rule exists to survive.", ["sec_stocks"]),
            ("Drawdown limit stated in advance", "The maximum decline the household agrees to hold without selling, written before the money arrives", "a third of the modeled 1929-style fall, as an illustration", "Converts a later panic into an arithmetic check.", ["fed_1929"]),
            ("Review date and approver", "Annual re-run of the model plus a re-read of the official sources, before the transfer and each year after", "next review at the transfer-year decision", "Records whether the recommendation moved, which is the point of re-running.", ["boe_lta"]),
        ]
        body += table("Policy parameters the model assumes, so the plan and the arithmetic agree", ["Parameter", "Rule as drafted", "Figure the model uses", "Why it is written this way"],
                     [row([p[0], p[1], p[2], p[3]], "guidance", p[4]) for p in params])
        return heading, lead, body

    if path.endswith("sources.html"):
        body += prose("Read dates in this build", "The estate and gift amounts, the indexed exclusion limit, the Form 540 line 62 instruction, the ten-year baseline, the latest price release, the house-price index release and the Treasury yield readings were each read between 2026-11-15 and 2026-11-17, and the date is stated beside the figure that uses them. A link points to a rule; it is not proof of any household fact, and none of these sources establishes a value, a rent, a premium or a rate area for a specific property.")
        return heading, lead, body

    return heading, lead, body

def render(path: str, title: str, group: str) -> str:
    root = path == "index.html"
    prefix = "" if root else "../"
    page_path = path
    heading, lead, body = decorate(page_path, *content_for(page_path))
    nav = []
    groups: dict[str, list[tuple[str, str]]] = {}
    for file, label, section in PAGES:
        groups.setdefault(section, []).append((file, label))
    for section, items in groups.items():
        nav.append(f'<details class="nav-group" open><summary>{esc(section)}</summary><div class="nav-items">')
        for file, label in items:
            href = prefix + file
            current = ' aria-current="page"' if file == path else ""
            nav.append(f'<a href="{esc(href)}"{current}>{esc(label)}</a>')
        nav.append('</div></details>')
    nav_html = ''.join(nav)
    title_full = f"{esc(heading)} · Private inheritance decision workspace"
    body_class = ' class="brief-page"' if path.endswith("attorney-cpa-brief.html") else ""
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive"><meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="description" content="Source-linked inheritance decision framework; figures are rounded and identifiers are withheld.">
<title>{title_full}</title><link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/phase-model.js" defer></script><script src="{prefix}assets/app.js" defer></script></head>
<body{body_class}><a class="skip" href="#main">Skip to content</a><div class="layout"><aside class="sidebar"><a class="brand" href="{prefix}index.html"><span class="brand-icon" aria-hidden="true">◈</span><span>PRIVATE<br>DECISION BRIEF</span></a><p class="sidebar-note">Trust transfer +<br>already-owned property</p><nav aria-label="Main navigation">{nav_html}</nav><div class="sidebar-bottom">Rounded figures, no identifiers<br>Official sources linked by scope<br>Exact records stay offline</div></aside>
<div class="workspace"><header class="topbar"><span>RESEARCH / DECISION SUPPORT</span><div><span class="privacy-dot" aria-hidden="true"></span> Privacy-first <button class="print-button no-print" id="print-page" type="button">Print</button></div></header>
<main id="main"><div class="page-heading"><span class="eyebrow">{esc(group.upper())}</span><h1>{esc(heading)}</h1><p class="lead">{esc(lead)}</p></div>{body}</main>
<footer class="site-footer"><p>Research framework only; not legal, tax, insurance, appraisal, investment, or property-management advice.</p><p>Recheck official authorities, source availability and law at the actual decision date.</p></footer></div></div></body></html>'''


def build() -> None:
    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "pages").mkdir(exist_ok=True)
    for path, title, group in PAGES:
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(path, title, group), encoding="utf-8")
    (ROOT / "tools/site-manifest.json").write_text(json.dumps([p for p, _, _ in PAGES], indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(PAGES)} pages; figures rounded, no data file read, no identifier emitted.")

if __name__ == "__main__":
    build()
