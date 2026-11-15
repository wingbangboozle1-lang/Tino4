#!/usr/bin/env python3
"""Build a public, privacy-first inheritance decision guide.

No household inputs are embedded, imported, inferred, or emitted. Private
records belong in an offline adviser workpaper, not this public repository.
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
    "fed_2008": ("Federal Reserve History — The Great Recession", "https://www.federalreservehistory.org/essays/great-recession-and-its-aftermath", "Reports an approximately 57% S&P 500 peak-to-trough decline and an approximately 30% average U.S. home-price decline from prior peaks. These historical observations do not forecast an individual portfolio or property."),
    "bls_cpi": ("U.S. Bureau of Labor Statistics — CPI", "https://www.bls.gov/cpi/", "Consumer Price Index data and methodology; historical inflation is not a future path."),
    "cbo_long": ("Congressional Budget Office — Long-Term Budget Outlook", "https://www.cbo.gov/topics/budget/long-term-budget-outlook", "Long-run fiscal and economic baseline publications; not a 50-year property or portfolio forecast."),
    "cbo_outlook": ("Congressional Budget Office — Economic Outlook", "https://www.cbo.gov/topics/economy", "Near-term economic baseline publications; verify the latest edition before use."),
    "fhfa": ("Federal Housing Finance Agency — House Price Index", "https://www.fhfa.gov/data/hpi", "Broad house-price index data; not an appraisal or forecast for a particular home."),
    "sec_stocks": ("SEC Investor.gov — Stocks", "https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks", "General stock-market risk information; no expected return is promised."),
    "congress_law": ("Congress.gov — Public Law 119-21", "https://www.congress.gov/bill/119th-congress/house-bill/1", "Enacted federal legislation; check statutory text and current IRS guidance for application."),
    "ftb_forms": ("California Franchise Tax Board — Forms and publications", "https://www.ftb.ca.gov/forms/", "Official entry point for current Form 540 instructions. The specific surcharge and capital-gain treatment must be checked in the instructions for the relevant tax year; no sensitivity is published here."),
    "sos_measures": ("California Secretary of State — Qualified ballot measures", "https://www.sos.ca.gov/elections/ballot-measures/qualified-ballot-measures", "Official ballot-measure list; full text and certified results must be checked separately."),
    "hud_fmr": ("HUD — Fair Market Rents", "https://www.huduser.gov/portal/datasets/fmr.html", "Housing-program benchmark methodology; not an appraisal, lawful rent, or current lease amount."),
}

PAGES = [
    ("index.html", "Decision overview", "Start"),
    ("pages/executive-summary.html", "Executive summary", "Start"),
    ("pages/decision-analysis.html", "Compare paths", "Decision"),
    ("pages/questions.html", "Questions & missing evidence", "Decision"),
    ("pages/suggestions.html", "Suggestions for review", "Decision"),
    ("pages/property-profiles.html", "Private property inventory", "Private planning"),
    ("pages/operating-costs.html", "Costs & coverage", "Private planning"),
    ("pages/projections.html", "Projection worksheet", "Private planning"),
    ("pages/property-tax.html", "Property-tax rules", "Law & process"),
    ("pages/inheritance-process.html", "Deadline timeline", "Law & process"),
    ("pages/estate-thresholds.html", "Estate-tax thresholds", "Law & process"),
    ("pages/law-watchlist.html", "Law watchlist", "Law & process"),
    ("pages/black-swan.html", "Black-swan conditions", "Stress tests"),
    ("pages/phased-investing.html", "Treasury staging tool", "Stress tests"),
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


def content_for(path: str) -> tuple[str, str, str]:
    """Return heading, lead, body for each public page; no case data is used."""
    if path == "index.html":
        body = callout("No household-specific recommendation is published", "The public repository is not a safe place for private property, tax, trust, lease, or investment data. This overview therefore gives decision gates and official rules, but does not rank a household path or expose identifying figures.", "warning")
        body += table("What would change the answer?", ["Decision-changing fact", "Current state", "Evidence needed"], [
            (["Trust, title, timing, debt", "Not available in this public project.", "Executed trust and deed; trustee authority; distribution date; debts and reserves."], STATUS["missing"], ["ca_prob", "ca_rtc480"]),
            (["Property-tax exclusion eligibility", "Cannot determine without family relationship, transferor use, title, value, occupancy and claim facts." , "Written eligibility review; confirm whether long-term occupancy is actually intended."], STATUS["missing"], ["boe_prop19", "ca_rtc63"]),
            (["After-tax sale / rent / keep comparison", "No property values, basis, rent, expenses, or tax returns are published." , "Independent date-of-death appraisal; private basis schedule; leases; expense records; sale-cost bids."], STATUS["missing"], ["irs_basis", "irs_rental", "irs_pub551"]),
            (["Where the household will live", "A separately owned residence and tenant obligations may alter every path; details are intentionally withheld." , "Written occupancy plan and counsel review of lease and local rules."], STATUS["missing"], ["irs_rental", "ca_rent"]),
            (["Estate-level liquidity / federal filing", "A home value alone cannot establish estate tax exposure." , "Full confidential estate inventory, adjusted taxable gifts, marital/portability facts and liquidity needs."], STATUS["missing"], ["irs_estate", "irs_estate_faq"]),
        ])
        body += prose("Safe decision order", "Set the family's written decision rules before seeing a forecast. Confirm trust and title, get independent values, establish tax basis and assessed-value treatment, validate use and leases, price recurring costs, then compare every path at the same dates and horizon. Keep all private inputs in a locally controlled, non-public workpaper.")
        body += prose("Conditional fork", "If a qualifying heir intends to occupy the transferred home as a principal residence long-term, test the Proposition 19 family-home exclusion and its deadlines. If not, model the reassessed tax branch and compare rental, sale, or mixed paths. No branch can be chosen from public facts alone.")
        return "Decision overview", "A privacy-first decision framework: official rules and questions are public; household facts stay private.", body
    if path.endswith("executive-summary.html"):
        body = callout("Executive takeaway", "The answer is not currently knowable from public information. Separate the estate-tax, income-tax basis, and property-tax assessment questions; obtain independent evidence; and agree in writing on the decision criteria before calculating outcomes.", "warning")
        body += table("What is established vs. not established", ["Topic", "Established by official source", "Still needs private evidence"], [
            (["Federal estate tax", "Current filing threshold is determined for the year of death and uses an estate-level test, not a per-heir allowance.", "Gross estate, adjusted taxable gifts, deductions, marital/portability history."], STATUS["rule"], ["irs_estate", "irs_estate_faq"]),
            (["Inherited basis", "General federal rule is date-of-death fair market value, subject to exceptions and reporting rules.", "Written date-of-death appraisal, improvements, depreciation, trust and estate records."], STATUS["rule"], ["irs_basis", "irs_pub551"]),
            (["Property-tax assessment", "California rules include Proposition 13 and a conditional Proposition 19 family-home exclusion.", "Eligibility, current roll, direct assessments, transfer status, claim and occupancy."], STATUS["rule"], ["boe_prop19", "ca_rtc63", "ca_rtc51"]),
            (["Operating costs", "Official agencies publish rules and tools, not a private property's current insurance/repair/utility cost.", "Written insurance quotes, recent bills, inspection and five-year capital plan."], STATUS["guidance"], ["cdi", "cslb"]),
        ])
        body += prose("Recommendation standard", "Do not call a projection the best plan until it includes the same tax year and horizon for all alternatives; sale taxes and fees; debt; occupancy; rental legality; vacancy; capital costs; utilities; insurance; liquidity; and reinvestment risk.")
        return "Executive summary", "The high-impact unknowns and a safe order of operations.", body
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
        return "Compare paths", "A fair comparison includes pure and mixed choices, on the same timeline.", body
    if path.endswith("questions.html"):
        rows = [
            (["What is actually transferring and when?", "Unknown: trust terms, amendments, trustee authority, title, debt, distribution conditions and transfer date." , "Attorney obtains and reviews executed documents; trustee confirms timeline in writing."], STATUS["missing"], ["ca_prob", "ca_rtc480"]),
            (["What is date-of-death fair market value and tax basis?", "No independent appraisal or estate basis schedule is available here." , "Obtain qualified written valuation as of date of death; reconcile improvements and depreciation with the CPA."], STATUS["missing"], ["irs_basis", "irs_pub551"]),
            (["Does the heir qualify for Proposition 19?", "Relationship, transferor occupancy, transferee occupancy, value limit and claim status are unknown." , "Counsel/assessor confirms statutory eligibility and long-term occupancy intention in writing."], STATUS["missing"], ["boe_prop19", "ca_rtc63", "boe_lta"]),
            (["What are actual rental and occupancy rights?", "Leases, permits, unit status, deposits and local rules are unavailable." , "Review every lease, lawful-use record, inspection and local ordinance with counsel."], STATUS["missing"], ["irs_rental", "ca_rent"]),
            (["What will costs be?", "Current bills, insurance terms, inspection and maintenance history are not in this public project." , "Collect multiple written insurance quotes, utility bills, contractor bids and a five-year capital plan."], STATUS["missing"], ["cdi", "cslb"]),
            (["Could federal estate tax or liquidity be material?", "No inventory, prior taxable gifts, marital or portability details are available." , "CPA/estate counsel builds a confidential estate-level calculation and liquidity plan."], STATUS["missing"], ["irs_estate", "irs_estate_faq", "irs_706"]),
            (["What is meant by 'Prop H'?", "Ambiguous without jurisdiction, election year and official measure identifier; no terms are modeled." , "Identify the measure and obtain its official text, fiscal analysis and current status."], STATUS["unverified"], ["sos_measures"]),
            (["What transfer tax and recording fees apply on sale?", "No amount is published because the property's jurisdiction, sale price, exemptions and recorded documents are not public or verified." , "Obtain the local official transfer-tax and recorder fee schedules and include them in the closing estimate."], STATUS["missing"], ["ca_rtc11911", "ca_gov27361"]),
            (["What is California income tax on gains?", "No sensitivity is published because the applicable Form 540 instructions and tax-year treatment have not been verified for this project." , "CPA reads official FTB instructions for the relevant tax year and documents the 1% tax threshold and capital-gain treatment."], STATUS["unverified"], ["ftb_forms"]),
        ]
        return "Questions & missing evidence", "A decision-ready question register, with practical discovery steps.", table("Questions to close before choosing", ["Question", "Known from current public evidence", "How to discover the missing information"], rows)
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
            (["Property A — inherited home", "No location, value, parcel identifier, tax history or insurance figure is published." , "Keep location and complete source records in a private inventory; obtain date-of-death valuation."], STATUS["missing"], ["irs_basis", "boe_prop19"]),
            (["Property B — already-owned property", "No location, value, rent roll, tax history, tenant or insurance data is published." , "Keep current title, leases, lawful-unit documentation, basis and bills privately; do not merge it with inherited assets."], STATUS["missing"], ["irs_rental", "irs_pub551"]),
            (["Evidence standard", "Owner memory or an online estimate is not an independent valuation or tax record." , "Use assessor roll, written appraisal, current insurance declarations, utility bills and executed leases."], STATUS["guidance"], ["irs_basis", "cdi", "irs_rental"]),
        ]
        body = table("Private inventory checklist", ["Record set", "Public disclosure boundary", "Private evidence to collect"], rows)
        body += callout("Do not upload records here", "Use placeholders in this public project. Never commit deeds, parcel numbers, names, statements, tax bills, insurance policies, leases, trust documents or adviser correspondence.", "warning")
        return "Private property inventory", "A checklist for the two roles in the decision, without identifying property details.", body
    if path.endswith("operating-costs.html"):
        rows = [
            (["Property tax", "Use the official tax bill and assessor roll; identify base-year value, direct assessments, exemptions, reassessment triggers, the tax-rate area and its published rate." , "Obtain the actual bill and official tax-rate-area schedule; do not infer a parcel-specific rate from a generic levy."], STATUS["guidance"], ["boe_prop19", "ca_rtc51"]),
            (["Insurance", "Premium depends on property, use, coverage, deductible, underwriting and market availability." , "Get multiple written owner-occupied and landlord-policy quotes; compare exclusions and FAIR Plan/DIC gaps."], STATUS["guidance"], ["cdi"]),
            (["Water, power and solar", "Tariffs, metering, solar export rules and household usage determine actual bills and credits." , "Collect account bills and interconnection/tariff documents; no generic bill is substituted."], STATUS["guidance"], ["cpuc_solar", "water_board"]),
            (["Maintenance and capital", "A property-condition assessment and repair history are needed; a percentage-of-value shortcut is not a bid." , "Create five-year safety, roof, structure, plumbing, electrical, HVAC and accessibility plans with bids."], STATUS["guidance"], ["cslb"]),
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
        return "Projection worksheet", "A reproducible approach for a private offline model; no property-specific projections are published.", body
    if path.endswith("property-tax.html"):
        rows = [
            (["Separate tax concepts", "Estate-tax valuation, income-tax basis, and property-tax assessed value answer different questions." , "Maintain separate ledgers and separate source documents."], STATUS["guidance"], ["irs_estate", "irs_basis", "ca_rtc51"]),
            (["Proposition 13", "California taxable value generally uses a base-year system with a statutory inflation adjustment; property bills can include other components." , "Confirm the parcel's assessed value and actual rate area from the assessor and tax bill."], STATUS["rule"], ["ca_rtc51", "boe_prop19"]),
            (["Proposition 19 family-home exclusion", "Requires statutory relationship and residence conditions; the claimant must satisfy occupancy and filing requirements." , "Claim only if eligible and the heir intends to occupy long-term; verify consequences before a later rental or sale."], STATUS["rule"], ["boe_prop19", "ca_rtc63", "boe_lta"]),
            (["Current indexed cap", "The official cap is $1,044,586 for qualifying transfers through February 15, 2027; the amount is periodically adjusted." , "Use the BOE amount applicable on the transfer date, not a forward projection."], STATUS["rule"], ["boe_lta"]),
            (["Property tax on an inherited home", "A qualifying claim may preserve the factored base value subject to the statutory value-limit calculation; failure to qualify can lead to reassessment." , "Obtain an assessor determination; do not treat a public model as eligibility advice."], STATUS["guidance"], ["boe_prop19", "ca_rtc63"]),
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
            (["California estate tax", "California's published guidance says estate tax returns are not required for deaths on or after January 1, 2005; current law must be rechecked at death." , "Separate state estate tax from federal estate tax and income-tax consequences."], STATUS["guidance"], ["ca_sco", "ca_rtc13301"]),
            (["Portability and prior gifts", "A surviving spouse's portability may require an estate-tax return even where the estate is below the filing threshold." , "Ask now about prior taxable gifts, deceased-spouse unused exclusion and timely filing."], STATUS["guidance"], ["irs_estate_faq", "irs_estate"]),
            (["Future threshold", "No official source can establish a future estate exclusion decades ahead; Congress can amend law." , "Use dated scenarios only and refresh from enacted law and IRS annual guidance."], STATUS["assumption"], ["congress_law", "irs_2027"]),
        ]
        return "Estate-tax thresholds", "The exclusion is not a per-heir allowance; assess the whole estate and year of death.", table("Estate and inheritance tax questions", ["Topic", "Current official information", "Next step"], rows)
    if path.endswith("law-watchlist.html"):
        rows = [
            (["Enacted federal law", "Public Law 119-21 is enacted; use the current IRS annual amounts and statute rather than old proposals." , "Document enactment date and operative year; recheck IRS guidance annually."], STATUS["rule"], ["congress_law", "irs_2027"]),
            (["Pending federal proposals", "A bill or proposal is not law unless enacted; no proposal-specific household outcome is modeled here." , "For each bill, record official status, text, committee action, effective date and whether it became law."], STATUS["guidance"], ["congress_law"]),
            (["California ballot measures", "Qualified list, measure text, election results and operative law are distinct records." , "Check official text and certified results; do not infer effect from a title."], STATUS["guidance"], ["sos_measures"]),
            (["Property-tax law", "Current Proposition 19 rules remain subject to amendment and future BOE indexed amount updates." , "Recheck BOE, statute and local assessor immediately before transfer."], STATUS["rule"], ["boe_prop19", "boe_lta", "ca_rtc63"]),
            (["Local measure called 'Prop H'", "Ambiguous without jurisdiction, year and official ballot number; no terms or impact are asserted." , "Identify the measure and verify full text, election result and effective date from the relevant official election authority."], STATUS["unverified"], ["sos_measures"]),
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
        body += '<section class="prose"><h2>Local-only sensitivity tool</h2><p>Enter generic scenario assumptions. This is an illustration, not a forecast, advice, or a historical backtest. No values are stored or transmitted.</p><div class="calculator"><label>Starting amount <input id="phase-amount" type="number" min="0" step="10" inputmode="decimal" placeholder="Enter privately"></label><label>Staging months <input id="phase-months" type="number" min="24" max="36" step="1" value="24"></label><label>Annual Treasury yield (%) <input id="phase-yield" type="number" min="-5" max="30" step="0.1" placeholder="Enter assumption"></label><label>Annual equity price drift (%) <input id="phase-equity" type="number" min="-50" max="50" step="0.1" placeholder="Enter assumption"></label><label>Equity decline during staging (%) <input id="phase-crash" type="number" min="0" max="90" step="1" value="57"></label><button id="phase-run" type="button">Run illustration</button><button id="phase-clear" type="button">Clear</button><p id="phase-result" role="status" aria-live="polite">No calculation run.</p></div></section>'
        body += prose("Limits", "This simple illustration assumes a linear price path during staging and ends at the last purchase; it does not model a post-staging crash, recovery, dividends, fees, taxes, withdrawals, asset correlations, property costs or changing Treasury yields. It is not a historical backtest or a recommendation.")
        return "Treasury staging tool", "Model 24–36 months of 3-month to 2-year Treasuries beside equity entry and renewal risk.", body
    if path.endswith("attorney-cpa-brief.html"):
        body = callout("Print-ready adviser handoff", "Bring this generic checklist to counsel and the tax adviser. Keep all names, property identifiers, documents and household figures out of the public site.", "info")
        body += table("Attorney & CPA briefing checklist", ["Workstream", "Questions to resolve", "Documents / action"], [
            (["Trust and title", "What transfers, when, subject to what debts and authority?", "Executed trust and amendments, deed, statements of authority, debt and beneficiary records."], STATUS["missing"], ["ca_prob", "ca_rtc480"]),
            (["Valuation and tax basis", "What is date-of-death value, adjusted basis, depreciation and improvement history?", "Independent appraisal, prior returns, capital-improvement receipts, depreciation schedules."], STATUS["missing"], ["irs_basis", "irs_pub551", "irs_rental"]),
            (["Estate tax and liquidity", "Does filing or payment apply; are gifts, marital deduction or portability relevant?", "Complete confidential inventory, prior gift returns, liquidity calendar and Form 706 advice."], STATUS["missing"], ["irs_estate_faq", "irs_706"]),
            (["Property-tax eligibility", "Is the heir eligible and willing to occupy long-term; what are deadlines and later-conversion consequences?", "Written BOE/assessor analysis, occupancy plan, claim calendar and current indexed cap."], STATUS["missing"], ["boe_prop19", "ca_rtc63", "boe_lta"]),
            (["Income tax and alternatives", "Compare sale in transfer year, later sale, rental, live, and mixed paths; test depreciation and recapture." , "CPA compares identical tax dates/horizons, costs, debt, rent, utility/insurance, and Section 121."], STATUS["missing"], ["irs_121", "irs_rental", "ftb_forms"]),
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
        return "Decision log", "Record the decision and date so a future reader can understand what was chosen and why.", table("Decision-log template", ["Entry", "Prompt", "Record"], rows)
    if path.endswith("flagged-for-review.html"):
        rows = [
            (["No private inventory", "Property values, assessed values, rent, bills, leases, title and insurance records are deliberately absent." , "Build and store the inventory offline; do not add it to Git or the site."], STATUS["missing"], ["irs_basis", "irs_rental", "cdi"]),
            (["Future-year law and economic path", "A transfer expected decades from now cannot be determined from present rules or official baseline forecasts." , "Recheck current law, indexed amounts, proposals and markets annually."], STATUS["guidance"], ["irs_2027", "boe_lta", "cbo_long"]),
            (["Form 540 sensitivity", "Specific one-percent tax and capital-gain sensitivity is not published because the current tax-year Form 540 instructions have not been verified in this build." , "CPA reads the FTB instructions for the applicable year and records a sourced calculation."], STATUS["unverified"], ["ftb_forms"]),
            (["Prop H", "The identifier alone does not establish jurisdiction, election year or measure text; no impact is modeled." , "Confirm official measure and full text with the relevant election authority."], STATUS["unverified"], ["sos_measures"]),
            (["History / repository exposure", "Earlier public Git objects and copies may retain content no longer shown on the site. A site rebuild cannot recall prior clones, PR diffs or caches." , "Repository administrator should assess visibility, history remediation and GitHub Support options; preserve a private archive before a rewrite."], STATUS["missing"], ["congress_law"]),
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
        body = callout("Privacy comes first", "This public site intentionally contains no property locality, address, parcel identifier, household amount, tax history, rent roll, policy detail, or household-specific recommendation. Use placeholders here and store private records outside the repository.", "warning")
        body += table("Privacy controls and limits", ["Control", "Current behavior", "Limitation"], [
            (["Public build inputs", "The generator contains only generic rules and public sources; no household data file is read." , "A public site cannot be used as a private case database."], STATUS["guidance"], ["irs_estate", "boe_prop19"]),
            (["Browser controls", "What-if calculations run in memory; the browser code makes no network requests or storage writes." , "Avoid entering sensitive details on a shared device; refresh to clear transient values."], STATUS["guidance"], ["treasury_bills", "sec_stocks"]),
            (["Current site", "Location and individual property figures are omitted." , "Anyone with repository access can read all tracked text and source files."], STATUS["guidance"], ["irs_basis"]),
            (["Earlier public copies", "A new build cannot remove old commits, forks, downloaded archives, cached pages or PR diffs." , "Treat anything previously public as potentially retained; admin-level remediation may be needed."], STATUS["missing"], ["congress_law"]),
        ])
        return "Privacy & limits", "Privacy is a design constraint, not a rounding promise.", body
    return "Not found", "", ""


def render(path: str, title: str, group: str) -> str:
    root = path == "index.html"
    prefix = "" if root else "../"
    page_path = path
    heading, lead, body = content_for(page_path)
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
<meta name="description" content="Privacy-first, source-linked inheritance decision framework; no household-specific data is published.">
<title>{title_full}</title><link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/app.js" defer></script></head>
<body{body_class}><a class="skip" href="#main">Skip to content</a><div class="layout"><aside class="sidebar"><a class="brand" href="{prefix}index.html"><span class="brand-icon" aria-hidden="true">◈</span><span>PRIVATE<br>DECISION BRIEF</span></a><p class="sidebar-note">Trust transfer +<br>already-owned property</p><nav aria-label="Main navigation">{nav_html}</nav><div class="sidebar-bottom">No property identifiers or case figures<br>Official sources linked by scope<br>Private work stays offline</div></aside>
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
    print(f"Built {len(PAGES)} privacy-first pages; no household inputs were read.")

if __name__ == "__main__":
    build()
