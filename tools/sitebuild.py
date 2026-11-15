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
    "fed_2008": ("Federal Reserve History — The Great Recession", "https://www.federalreservehistory.org/essays/great-recession-and-its-aftermath", "Reports an approximately 57% S&P 500 peak-to-trough decline and an approximately 30% average U.S. home-price decline from prior peaks. These historical observations do not forecast an individual portfolio or property."),
    "bls_cpi": ("U.S. Bureau of Labor Statistics — CPI", "https://www.bls.gov/cpi/", "Consumer Price Index data and methodology; historical inflation is not a future path."),
    "cbo_long": ("Congressional Budget Office — Long-Term Budget Outlook", "https://www.cbo.gov/topics/budget/long-term-budget-outlook", "Long-run fiscal and economic baseline publications; not a 50-year property or portfolio forecast."),
    "cbo_outlook": ("Congressional Budget Office — Economic Outlook", "https://www.cbo.gov/topics/economy", "Near-term economic baseline publications; verify the latest edition before use."),
    "fhfa": ("Federal Housing Finance Agency — House Price Index", "https://www.fhfa.gov/data/hpi", "Broad house-price index data; not an appraisal or forecast for a particular home."),
    "sec_stocks": ("SEC Investor.gov — Stocks", "https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks", "General stock-market risk information; no expected return is promised."),
    "congress_law": ("Congress.gov — Public Law 119-21", "https://www.congress.gov/bill/119th-congress/house-bill/1", "Enacted federal legislation; check statutory text and current IRS guidance for application."),
    "github_sensitive": ("GitHub Docs — Removing sensitive data from a repository", "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository", "Official guidance on sensitive data in Git history; prior clones, forks and copies may remain outside a repository cleanup."),
    "ftb_forms": ("California Franchise Tax Board — Forms and publications", "https://www.ftb.ca.gov/forms/", "Official entry point for current Form 540 instructions. The specific Form 540 booklet was not retrieved for this project; see the separately linked Form 540-ES worksheet and capital-gains guidance."),
    "ca_rtc17043": ("California statute — additional tax on high taxable income", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=17043.&lawCode=RTC", "Read 2026-11-15 in the official statute: additional 1% tax applies to taxable income above $1,000,000 for taxable years beginning on or after January 1, 2005; the statutory threshold is not indexed in the section text."),
    "ftb_540es": ("FTB — 2025 Form 540-ES instructions", "https://www.ftb.ca.gov/forms/2025/2025-540-es-instructions.html", "Read 2026-11-15: worksheet computes 1% Behavioral Health Services Tax on taxable income above $1,000,000. This is not the full Form 540 booklet; verify current-year instructions."),
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
    ("pages/property-profiles.html", "Private property inventory", "Private planning"),
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
        body += prose("Recommendation standard", "Do not call a projection the best plan until it includes the same tax year and horizon for all alternatives; the full sale-cost waterfall (transaction costs, documentary transfer tax, recording fees, sale-year income tax including unrecaptured section 1250 gain and the California 1% add-on above $1,000,000 of taxable income); any like-kind-exchange decision; debt; occupancy; rental legality; vacancy; capital costs; utilities; insurance; estate liquidity; and reinvestment risk.")
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
        body += callout("Model first: a sale in the transfer tax year", "Before ranking any path, price the one branch that needs no forecast. Inherited basis is generally date-of-death fair market value, so a sale in the transfer tax year often has little or no income-tax gain. That branch is the anchor every other path must beat after housing costs and reinvestment risk.", "info")
        body += table("Sale proceeds waterfall — the order in which a sale pays out", ["Layer", "Framework (amounts stay private)", "Rule or schedule source"], [
            (["Gross sale value", "Contract price at the sale date; get an independent valuation rather than an online estimate.", "Private appraisal and sale contract."], STATUS["guidance"], ["irs_basis", "irs_pub551"]),
            (["Sale transaction costs", "Broker, escrow, title, repair credits and concessions, as bid in writing; label the percentage assumption used in any comparison.", "Written bids and the closing statement."], STATUS["guidance"], ["irs_pub551"]),
            (["Documentary transfer tax", "California authorizes a documentary transfer tax computed on value in stated increments; the applicable rate is set by the local jurisdiction and must be read from the property's own official schedule at sale.", "Statewide authority and the local recorder's enacted schedule."], STATUS["rule"], ["ca_rtc11911", "ca_gov27361"]),
            (["Recording fees", "Statutory per-page and per-title recording charges, plus statewide add-on fees, apply at recording; the actual total depends on the document and the county schedule.", "Statewide fee statute and the property's county recorder schedule."], STATUS["rule"], ["ca_gov27361"]),
            (["Sale-year income tax", "In the transfer tax year, gain is generally small because basis is date-of-death value. A later sale adds post-death appreciation; depreciated rentals add unrecaptured section 1250 gain taxed federally at a maximum 25% rate; a high-income sale year can add the California 1% tax on taxable income above $1,000,000.", "CPA computes from private basis and depreciation records."], STATUS["rule"], ["irs_basis", "irs_topic409", "irs_sched_d", "ca_rtc17043", "ftb_540es", "ftb_cap_gains"]),
            (["Net proceeds to invest or reinvest", "What remains after every layer above; compare paths only on this figure, not on gross value.", "Closing statement and CPA summary."], STATUS["guidance"], ["irs_pub551", "irs_1031_tips"]),
        ])
        body += table("Tax overlays and structural decisions to price before choosing", ["Overlay", "What to decide or compute", "Source"], [
            (["Depreciation and unrecaptured section 1250 recapture", "For any rental path, reconcile depreciation allowed or allowable; the recapture portion is federally taxed at a maximum 25% rate and California treats gains as ordinary income.", "IRS Topic 409 and the Schedule D worksheet; CPA schedule."], STATUS["rule"], ["irs_topic409", "irs_sched_d", "ftb_cap_gains"]),
            (["Like-kind exchange (section 1031)", "Decide in writing before listing: an exchange can defer gain on business or investment real property only, needs a qualified intermediary and statutory deadlines, never applies to a primary residence or property held mainly for sale, and leaves the replacement with carryover basis.", "IRS like-kind exchange guidance; tax counsel memo."], STATUS["rule"], ["irs_1031", "irs_1031_tips"]),
            (["Main-home exclusion switch", "For a live-then-sell path, track the ownership and use periods separately; a conversion to rental changes the analysis and can interact with property-tax status.", "IRS Topic 701; written property-tax advice."], STATUS["rule"], ["irs_121", "boe_prop19", "ca_rtc63"]),
            (["California 1% additional tax on high taxable income", "In any large-gain year, taxable income (including capital gains) above $1,000,000 is taxed an extra 1%; the threshold is not indexed. Compute with the CPA before assuming a sale-year tax rate.", "Current statute and the state worksheet; current-year instructions."], STATUS["rule"], ["ca_rtc17043", "ftb_540es", "ftb_cap_gains"]),
            (["Local vacancy-tax exposure", "Some jurisdictions tax units vacant beyond a statutory period; at least one such measure has had enforcement barred by litigation. Confirm the property's own current ordinance before planning an empty unit.", "Election authority for the measure; the property's tax authority."], STATUS["unverified"], ["sos_measures"]),
            (["Estate liquidity timing", "If a federal return may be required, taxes and expenses are due on a calendar that does not wait for a real-estate sale; price funding routes early.", "IRS filing guidance; CPA liquidity plan."], STATUS["rule"], ["irs_706", "irs_estate_faq"]),
        ])
        body += '<section class="prose"><h2>Local-only sale-tax overlay tool</h2><p>Enter generic assumptions to see how gain, a main-home exclusion, and the California 1% add-on interact. Inputs are evaluated in browser memory only, no value is stored or transmitted, and no default household amount is provided. This is an illustration, not advice or a forecast.</p><div class="calculator"><label>Sale value at sale date ($) <input id="sell-value" type="number" min="0" step="10" inputmode="decimal" placeholder="Enter privately"></label><label>Tax basis at sale ($) <input id="sell-basis" type="number" min="0" step="10" inputmode="decimal" placeholder="Date-of-death value if just inherited"></label><label>Sale costs (%) <input id="sell-costs" type="number" min="0" max="30" step="0.5" placeholder="Enter assumption"></label><label>Local documentary transfer-tax rate (%) <input id="sell-dtt" type="number" min="0" max="10" step="0.01" placeholder="From the local enacted schedule"></label><label>Other taxable income ($, optional) <input id="sell-other" type="number" min="0" step="10" inputmode="decimal" placeholder="For the 1% add-on test"></label><label>Sale timing <select id="sell-timing"><option value="later">Later sale (after the transfer year)</option><option value="transfer">Sale in the transfer tax year</option></select></label><label>Main-home exclusion (section 121) <select id="sell-121"><option value="0">None claimed</option><option value="250000">Up to $250,000</option><option value="500000">Up to $500,000 (joint)</option></select></label><button id="sell-run" type="button">Run illustration</button><button id="sell-clear" type="button">Clear</button><p id="sell-result" role="status" aria-live="polite">No calculation run.</p></div></section>'
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
            (["How are California capital gains taxed, and when does the 1% surcharge apply?", "FTB states capital gains are taxed as ordinary income. Current statute and the 2025 Form 540-ES worksheet apply an additional 1% to taxable income above $1,000,000; that is not an inheritance tax. No household sale-year sensitivity is available." , "CPA calculates sale-year taxable income, federal and California tax, basis, exclusions and estimated-payment effects; verify the current Form 540 booklet, which was not retrieved for this build."], STATUS["rule"], ["ca_rtc17043", "ftb_540es", "ftb_cap_gains", "ftb_forms"]),
        ]
        return "Questions & missing evidence", "A decision-ready question register, with practical discovery steps.", table("Questions to close before choosing", ["Question", "Known from current public evidence", "How to discover the missing information"], rows)
    if path.endswith("requirements-tracker.html"):
        rows = [
            (["Executive summary and first-screen answer changers", "Published as a privacy-safe overview with an explicit list of decision-changing facts; no household ranking is emitted." , "Keep the first-screen evidence gates current as private records arrive."], STATUS["guidance"], ["boe_prop19", "irs_estate_faq"]),
            (["Complete list of requirements and missing information", "This page maps decision, tax, cost, legal, privacy and process requirements to current treatment and a next step." , "Update status only after the official source or private record is checked."], STATUS["guidance"], ["irs_estate", "boe_prop19"]),
            (["Privacy and prior public exposure", "No household location, personal document, property figure or case-specific recommendation is published in the current site." , "Earlier public copies may remain in Git history, PRs, forks or caches; an administrator must assess historical remediation."], STATUS["missing"], ["github_sensitive"]),
            (["Private estate and property inventory", "No inventory is stored in this repository." , "Create an encrypted private inventory of trust, deed, debt, prior gifts, basis, property tax, insurance, leases and liquidity."], STATUS["guidance"], ["irs_estate", "irs_basis", "irs_rental"]),
            (["Independent value and condition evidence", "No online estimate is treated as an appraisal or repair bid." , "Obtain written date-of-death valuation, independent rental comparables and condition inspections."], STATUS["guidance"], ["irs_basis", "hud_fmr", "cslb"]),
            (["Annual projections and scenario ranges", "The public worksheet explains formulas and requires low/base/high paths; no household amounts or year-by-year case projections are emitted." , "Use private, dated inputs; show market value, assessed value, tax, operating cash flow and uncertainty bands."], STATUS["guidance"], ["fhfa", "ca_rtc51", "cbo_long"]),
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
            (["Tax-aware California sale sensitivity", "Official statute and FTB sources state the additional 1% above $1,000,000 taxable income and ordinary-rate treatment of capital gains; no household calculation is published." , "CPA checks the current Form 540 booklet and computes sale-year taxable income, basis, exclusions, estimated payments and tax."], STATUS["guidance"], ["ca_rtc17043", "ftb_540es", "ftb_cap_gains", "ftb_forms"]),
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
            (["Tax-aware realization", "California capital gains are taxed as ordinary income; a 1% additional tax applies to taxable income above $1,000,000 under current law." , "CPA confirms the sale-year Form 540 instructions, basis, federal treatment and estimated payments."], STATUS["rule"], ["ca_rtc17043", "ftb_540es", "ftb_cap_gains"]),
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
            (["California gain tax and additional tax", "FTB says capital gains are taxed as ordinary income. An additional 1% applies to the portion of taxable income above $1,000,000 under current statute and the 2025 Form 540-ES worksheet; this is a tax on taxable income, not on the inheritance itself." , "Model the sale tax year with the CPA. Full Form 540 booklet was not retrieved here; check current-year instructions and household deductions/basis."], STATUS["rule"], ["ca_rtc17043", "ftb_540es", "ftb_cap_gains", "ftb_forms"]),
            (["California estate tax", "California's published guidance says estate tax returns are not required for deaths on or after January 1, 2005; current law must be rechecked at death." , "Separate state estate tax from federal estate tax and income-tax consequences."], STATUS["guidance"], ["ca_sco", "ca_rtc13301"]),
            (["Portability and prior gifts", "A surviving spouse's portability may require an estate-tax return even where the estate is below the filing threshold." , "Ask now about prior taxable gifts, deceased-spouse unused exclusion and timely filing."], STATUS["guidance"], ["irs_estate_faq", "irs_estate"]),
            (["Payment calendar", "A federal estate return is generally due nine months after death; an extension of time to file is not an extension of time to pay." , "Calendar both dates at the death and plan funding before the filing window opens."], STATUS["rule"], ["irs_706", "irs_estate_faq"]),
            (["Estate liquidity plan", "An estate concentrated in real estate can owe taxes and expenses on a calendar that does not wait for a property sale; funding routes (insurance in trust, financing, staged or installment sale) must be priced before they are needed." , "Build a dated liquidity inventory and obtain quotes and lender indications early; keep proceeds outside the estate where counsel advises."], STATUS["guidance"], ["irs_estate_faq", "irs_estate"]),
            (["Worked sale-year sensitivity (California 1% add-on)", "The add-on equals 1% of taxable income above the threshold: each $100,000 of taxable income above $1,000,000 adds $1,000. Capital gains count in taxable income because California taxes them as ordinary income." , "Compute the actual sale-year figure from private basis, deductions and other income; the statutory threshold is not indexed."], STATUS["rule"], ["ca_rtc17043", "ftb_540es", "ftb_cap_gains"]),
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
            (["California sale-year tax sensitivity", "The one-percent additional tax above taxable income of $1,000,000 and ordinary-rate capital-gain treatment are stated on official statute/FTB sources. No household calculation is published, and the full Form 540 booklet was not retrieved for this build." , "CPA verifies current Form 540 instructions and calculates the sale-year tax from private basis and taxable-income facts."], STATUS["missing"], ["ca_rtc17043", "ftb_540es", "ftb_cap_gains", "ftb_forms"]),
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
        body = callout("Privacy comes first", "This public site intentionally contains no property locality, address, parcel identifier, household amount, tax history, rent roll, policy detail, or household-specific recommendation. Use placeholders here and store private records outside the repository.", "warning")
        body += table("Privacy controls and limits", ["Control", "Current behavior", "Limitation"], [
            (["Public build inputs", "The generator contains only generic rules and public sources; no household data file is read." , "A public site cannot be used as a private case database."], STATUS["guidance"], ["irs_estate", "boe_prop19"]),
            (["Browser controls", "What-if calculations run in memory; the browser code makes no network requests or storage writes." , "Avoid entering sensitive details on a shared device; refresh to clear transient values."], STATUS["guidance"], ["treasury_bills", "sec_stocks"]),
            (["Current site", "Location and individual property figures are omitted." , "Anyone with repository access can read all tracked text and source files."], STATUS["guidance"], ["irs_basis"]),
            (["Earlier public copies", "A new build cannot remove old commits, forks, downloaded archives, cached pages or PR diffs." , "Treat anything previously public as potentially retained; admin-level remediation may be needed."], STATUS["missing"], ["github_sensitive"]),
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
