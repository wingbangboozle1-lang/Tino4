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
    "irs_topic409": ("IRS Topic 409 — Capital gains and losses", "https://www.irs.gov/taxtopics/tc409", "Gain is the excess over adjusted basis; unrecaptured section 1250 gain from depreciated real property is taxed at a maximum 25% federal rate; short-term gain is ordinary income. The rate table on that page applies to a stated tax year."),
    "irs_8824": ("IRS — About Form 8824 (like-kind exchanges)", "https://www.irs.gov/forms-pubs/about-form-8824", "Reports each exchange of business or investment real property for like property. Filing the form does not establish qualification; deferral depends on held-for-use and timing rules."),
    "irs_8971": ("IRS — About Form 8971 (basis reporting)", "https://www.irs.gov/forms-pubs/about-form-8971", "Required executors report per-estate values and beneficiaries; a value reported on Schedule A can bind the beneficiary's initial basis. Only estates required to file receive these statements."),
    "sf_fees": ("San Francisco County Recorder — fees to record a document", "https://www.sf.gov/reports--march-2024--fees-record-document-san-francisco", "Official city-county schedule: documentary transfer tax per 500 dollars of consideration by tier, per-page recording charges, the real-estate fraud fee, the survey-monument fee, the affordable-housing parcel fee with its exemptions, and the fee charged when no change-of-ownership statement accompanies a document. Confirm the current schedule before closing."),
    "sf_prop_i": ("San Francisco — Housing Stability Fund Oversight Board (about)", "https://www.sf.gov/departments--housing-stability-fund-oversight-board--about", "Official page recording that the November 2020 Proposition I measure raised the top transfer-tax tiers and where the revenue goes. Use it to identify the in-force measure; read the charter amendment for operative text."),
    "hud_fmr": ("HUD — Fair Market Rents", "https://www.huduser.gov/portal/datasets/fmr.html", "Housing-program benchmark methodology; not an appraisal, lawful rent, or current lease amount."),
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
            (["Depreciation already taken, and the recapture it creates", "A rented building's deductions reduce basis, and the reduction returns as gain at sale — at a maximum 25% federal rate on unrecaptured section 1250 gain, with California taxing the whole gain as ordinary income." , "CPA-built depreciation history (allowed or allowable, not only claimed), land/building allocation, improvement records, and a disposition calculation for the intended sale year."], STATUS["missing"], ["irs_rental", "irs_topic409", "ftb_cap_gains"]),
            (["Transaction costs between gross price and cash", "Documentary transfer tax, recording charges, the change-of-ownership screening fee and any local add-on are set by the recording jurisdiction's published schedule, not by a percentage convention." , "A written closing estimate from an escrow officer plus the official local schedule for each building's jurisdiction."], STATUS["missing"], ["sf_fees", "ca_rtc11911", "ca_gov27361"]),
            (["The rent a live-in path does not pay", "A household occupying a home it owns avoids a market rent; a comparison that ignores it treats housing as free on one path only." , "Written rent comparables for a comparable home in the same submarket, used as a labelled comparison device and never as income."], STATUS["missing"], ["hud_fmr", "irs_rental"]),
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
        body += prose("Where the rules layer lives", "The mechanics that decide whether a path is cheaper are published on the rules pages rather than in a headline: rental depreciation and its recapture, the change-of-ownership filing, the home-sale exclusion conditions and the like-kind exchange scope on the property-tax page; the transaction-cost and rent-evidence standards on the costs page; the estate-level filing test, the gift history, the portability election and the liquidity distinction on the estate page; the crash-entry comparison in index units on the staging page; and the re-check cadence on the watchlist. Each row names its official source, and each unknown stays blank with the step that would close it.")
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
        body += table(
            "Rules that decide whether a path is actually cheaper",
            ["Mechanism", "What the official source establishes", "How to apply it without inventing a number"],
            [
                (["Inherited basis and the sale-year question", "For property acquired from a decedent, basis is generally the fair market value at the date of death, so a sale in that same year can produce little or no gain to tax. An estate that must file a basis-reporting return can bind the beneficiary's initial basis to the reported estate value.", "Have the CPA compare a same-year sale with a later sale using the appraisal and the estate's reported values; do not assume both a stepped-up income-tax basis and a low assessed value survive without checking the exclusion conditions."], STATUS["rule"], ["irs_basis", "irs_pub551", "irs_8971"]),
                (["The primary-residence switch", "The home-sale exclusion applies to a main home and depends on owning and using the home for the required period; eligibility cannot be presumed for an inherited house the heir never occupied.", "Run each path with the exclusion switched on only where occupancy is actually planned, and ask the CPA to state in writing whether the decedent's ownership period counts toward the ownership test."], STATUS["rule"], ["irs_121", "irs_1031"]),
                (["Depreciation is a timing benefit, not a saving", "A rented building's cost is recovered over the residential-rental recovery period; the recovered amount reduces basis and returns as gain on disposition, at a maximum 25% federal rate for unrecaptured section 1250 gain.", "Show the deduction and the clawback in the same view of the private model: state the marginal rate the shelter is worth at, and the rate the repayment is taxed at."], STATUS["rule"], ["irs_rental", "irs_topic409", "ftb_cap_gains"]),
                (["Exchange is deferral, not forgiveness", "A like-kind exchange requires both the property given up and the property received to be held for business or investment, and the replacement property generally carries over the lower basis.", "Decide before listing whether an exchange is wanted at all; a beneficiary who wants a fresh basis is often better served by a fully taxable sale, and the identification and receipt deadlines cannot be met after the fact."], STATUS["rule"], ["irs_1031", "irs_8824"]),
                (["Avoided rent belongs on the live-in side", "No official source establishes what a household would pay to house itself in an equivalent owned home; the comparison requires a private, sourced estimate.", "Use written comparables or a stated household budget line, label it imputed rent, and apply it symmetrically so the invested path is charged the housing it must buy."], STATUS["guidance"], ["hud_fmr", "irs_rental"]),
                (["Outcome spread instead of a single forecast", "No official source establishes a household's future path; official baselines are bounded and historical episodes are observations, not probabilities.", "Present low, quartile and high outcomes across the assumption grid as a spread, and record whether the ranking of paths survives the tails."], STATUS["guidance"], ["cbo_long", "fhfa", "bls_cpi", "sec_stocks"]),
            ],
        )
        body += '<section class="tool-section"><h2>Local-only capital and tax sensitivity</h2>'
        body += '<p class="table-note">Enter your own figures in your own browser. Nothing is stored, sent or published, and no field is prefilled with a household value. The panel answers the three questions a gross-versus-net comparison usually skips: what depreciation shelters and later returns, what the recording jurisdiction takes before proceeds are investable, and what the household saves by occupying the home it owns. Refresh the page to clear the fields.</p>'
        body += '<div class="calculator">'
        body += '<label>Value used as the depreciable basis <input id="cap-basis" type="number" min="0" step="10" placeholder="Enter privately"></label>'
        body += '<label>Years the building was rented <input id="cap-years" type="number" min="0" max="40" step="1" value="10"></label>'
        body += '<label>Recovery period in years <input id="cap-period" type="number" min="10" max="40" step="0.5" value="27.5"></label>'
        body += '<label>Marginal rate on rental income (%) <input id="cap-rate" type="number" min="0" max="60" step="0.5" value="40"></label>'
        body += '<label>Sale price <input id="cap-sale" type="number" min="0" step="10" placeholder="Enter privately"></label>'
        body += '<label>Transfer tax per 500 of consideration <input id="cap-dtt" type="number" min="0" step="0.05" placeholder="From the local schedule"></label>'
        body += '<label>Other closing costs (%) <input id="cap-cost" type="number" min="0" max="15" step="0.1" value="7"></label>'
        body += '<label>Rent the household would otherwise pay, per year <input id="cap-rent" type="number" min="0" step="10" placeholder="Enter privately"></label>'
        body += '<button id="cap-run" type="button">Run locally</button><button id="cap-clear" type="button">Clear</button>'
        body += '<p id="cap-status" class="tool-status" role="status" aria-live="polite">No calculation run.</p>'
        body += '</div>'
        body += '<p class="table-note">Method: straight-line deduction on the entered basis over the entered recovery period, with no mid-month convention and no land allocation applied — those belong to the CPA, so treat the deduction as an upper bound. The repayment is shown at the maximum federal rate on unrecaptured section 1250 gain plus the entered state rate, because California taxes the gain as ordinary income. Transfer tax is the entered per-500 amount applied to the whole sale price, which is how the published schedule behaves at a tier boundary. Avoided rent is a comparison device, not income. Amounts are rounded to the nearest ten dollars in the result line; nothing here is tax advice.</p>'
        body += '</section>'
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
            (["What transfer tax and recording fees apply on sale?", "No amount is published, because the jurisdiction, price, exemptions and recorded documents are not public or verified. The published city-county schedule does establish that the tax is charged per 500 dollars of consideration and that the applicable tier can reach the entire consideration.", "Obtain the official transfer-tax and recorder fee schedules for each building's jurisdiction and a written closing estimate from an escrow officer, and ask the recorder whether a transfer at death pays the tax."], STATUS["missing"], ["ca_rtc11911", "ca_gov27361", "sf_fees"]),
            (["What has been depreciated, and what does that create at a sale?", "No depreciation schedule, land/building allocation or accumulated-depreciation figure is published. The recovery period, the mid-month convention, the exclusion of land, the allowed-or-allowable rule and the maximum federal rate on unrecaptured section 1250 gain are established rules.", "The CPA produces the depreciation history from returns, or reconstructs what was allowable, with the acquisition and improvement records, and calculates the repayment at an intended sale-price band and year."], STATUS["missing"], ["irs_rental", "irs_topic409", "ftb_cap_gains"]),
            (["Will the heir occupy the inherited home long enough for the home-sale exclusion?", "The occupancy plan is not published, and the ownership-and-use tests are questions of fact. Whether an heir may count the decedent's ownership period is not resolved by the sources cited on this site.", "A dated occupancy plan, the intended sale year, any prior use of the exclusion, and a written CPA position on the period test before the exclusion is relied on in a model."], STATUS["missing"], ["irs_121"]),
            (["Is an exchange intended, or is a taxable sale better?", "A like-kind exchange requires both sides to be held for business or investment, defers rather than eliminates tax, and generally carries the lower basis and the repayment forward into the replacement property.", "A written adviser note on held-for-use before the property is listed, plus the identification and receipt deadlines and a qualified intermediary's terms, if an exchange is pursued."], STATUS["missing"], ["irs_1031", "irs_8824"]),
            (["Can the estate meet what it may owe without selling?", "No estate inventory, cash position, debt schedule, insurance or retirement beneficiary designations or liquidity plan is published, and an estate-level filing test cannot be evaluated from a property value.", "A confidential inventory of accounts by type with balances, debts and liens, beneficiary designations, prior gift returns, and a written plan for the filing and payment dates — including whether a portability election requires a return below the threshold."], STATUS["missing"], ["irs_estate", "irs_estate_faq", "irs_706"]),
            (["What could the inherited home rent for, and at what cost?", "No rent comparable, management fee schedule, vacancy assumption or insurance quote is published for a specific property, and none is inferred from an area median or a program payment standard.", "Three written comparables from a licensed agent or manager, a written management fee schedule, a vacancy assumption from actual turnover, and two quotes each for owner-occupied and landlord coverage."], STATUS["missing"], ["hud_fmr", "irs_rental", "cdi"]),
            (["Which property-tax relief survives a later rental or sale?", "The conditions on a family-home transfer are published; the consequences of the household's actual later use are property-specific determinations.", "The assessor's written determination and the claim file, kept with the trust records, plus a note on what a later conversion does to the assessment and to any gain."], STATUS["missing"], ["boe_prop19", "ca_rtc63"]),
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
            (["Transfer tax and recording fees on a sale", "No fee total is published without jurisdiction, sale amount, exemptions and recorded-document details. The rule that the applicable tier can reach the entire consideration is published and is the reason a sale price near a boundary behaves unexpectedly." , "Include official local schedules and a written closing estimate in the sale path, and confirm whether a transfer at death pays the tax."], STATUS["missing"], ["ca_rtc11911", "ca_gov27361", "sf_fees"]),
            (["Re-check cadence and a rebuild-and-diff gate", "The cadence is published on the watchlist, and a repository check rebuilds the site, runs the verifier and compares a committed fingerprint of the evidence layer so a change that alters what the framework asserts is reported rather than absorbed.", "Run the check on every assumption change and before any release; refresh the snapshot only after the framework has been re-read."], STATUS["guidance"], ["boe_lta", "irs_2027", "congress_law"]),
            (["Outcome distribution instead of a point estimate", "The method — an assumption grid, percentile spread, certainty on its own line, and the cell count shown — is published, with a unit-free index illustration of what a spread looks like.", "Apply the method in the private model where the household figures live, and record whether each path's ranking survives the tails."], STATUS["guidance"], ["cbo_long", "fhfa", "sec_stocks"]),
            (["Same dates, horizons, taxes, debt, occupancy, costs and liquidity", "The comparison rule requires the same transfer and valuation dates, after-tax horizon and complete cost categories for every path." , "Re-run all pure and mixed choices together; include debt, occupancy changes, repairs, insurance, utilities, transaction costs and liquidity."], STATUS["guidance"], ["irs_estate", "irs_rental", "cdi"]),
            (["Mixed paths beside pure choices", "Live, rent, sell, live-then-sell, rent-then-sell, and retain/change-use combinations are included in the framework." , "Only rank a mixed path after leases, eligibility, tax and transition costs are verified."], STATUS["guidance"], ["boe_prop19", "irs_rental", "irs_121"]),
            (["Black-swan conditions and 1929/2008 entry risk", "The guide distinguishes historical index drawdowns from probabilities and exposes the limits of its local-only sensitivity." , "Stress early/late crashes, inflation, deflation, housing-equity correlation, delayed recovery and lower Treasury renewal rates."], STATUS["historical"], ["fed_1929", "fed_2008", "fed_inflation", "treasury_bills"]),
            (["Tax-aware California sale sensitivity", "Official statute and FTB sources state the additional 1% above $1,000,000 taxable income and ordinary-rate treatment of capital gains; no household calculation is published." , "CPA checks the current Form 540 booklet and computes sale-year taxable income, basis, exclusions, estimated payments and tax."], STATUS["guidance"], ["ca_rtc17043", "ftb_540es", "ftb_cap_gains", "ftb_forms"]),
            (["Federal estate threshold, portability and liquidity", "Current-year federal thresholds are estate-level and not per-heir; future law and household headroom are not inferred." , "Ask now about portability and prior taxable gifts; obtain a private estate inventory and liquidity schedule."], STATUS["guidance"], ["irs_estate", "irs_estate_faq", "irs_706"]),
            (["Deadlines and step-by-step inheritance process", "Trust notice, change-in-ownership, Form 706 and Proposition 19 deadlines are presented with applicability caveats." , "Attorney calendars actual dates from death, title and transfer-route documents."], STATUS["guidance"], ["ca_prob", "ca_rtc480", "irs_706", "ca_rtc63"]),
            (["Enacted law vs. proposals and annual refresh", "The watchlist separates enacted law, pending proposals, ballot measures and unverified facts." , "Recheck official federal, state and local authorities annually and at transfer; record source, status and effective date."], STATUS["guidance"], ["congress_law", "sos_measures", "boe_prop19"]),
            (["Investment policy before proceeds arrive", "A blank, reviewable policy draft sets liquidity, staging, asset exposure, tax-aware realization and triggers without choosing personal values." , "Agree in writing on path conditions, risk limits, liquidity floor, review date and approver before seeing projections."], STATUS["guidance"], ["treasury_bills", "treasury_notes", "sec_stocks"]),
            (["What-if controls, ranges and distribution chart", "The phased tool is local-only. Other property inputs and distribution projections belong in the private model; no static household chart is published." , "After each private input change, rebuild the model, compare low/base/high outcomes and note whether rankings move."], STATUS["guidance"], ["sec_stocks", "fhfa", "cbo_long"]),
            (["Attorney & CPA one-page briefing sheet", "A print-optimized adviser handoff lists trust, value, estate-tax, property-tax, sale/rent and policy questions." , "Print privately and complete only with counsel using confidential records."], STATUS["guidance"], ["irs_estate_faq", "boe_prop19", "irs_basis"]),
            (["Suggestions, glossary and dated decision record", "Suggestions have a session-only review queue; the glossary defines the tax layers; the decision log prompts a date and reason." , "Record each adopted or rejected item and the trigger for reconsideration."], STATUS["guidance"], ["irs_estate", "boe_prop19"]),
            (["Local 'Prop H' terms and impact", "The shorthand is not enough to publish or apply a local measure without identifying jurisdiction and official text; no household mapping or rate is published." , "Confirm the measure and read its official text, certified result, tax category and effective date in private adviser review."], STATUS["unverified"], ["sos_measures"]),
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
            (["Model depreciation and the repayment it creates", "Rental deductions reduce basis and return as gain at a capped federal rate, with California taxing the gain as ordinary income; a live-in path forgoes both the deduction and the repayment.", "Have the CPA produce each building's depreciation history and a recapture figure at a price band, then re-run the path comparison with it included."], STATUS["guidance"], ["irs_rental", "irs_topic409", "ftb_cap_gains"]),
            (["Price transaction costs into every sale path", "Documentary transfer tax is charged per 500 dollars of consideration and the applicable tier can reach the entire consideration, so a price just over a boundary is more expensive to convey.", "Obtain each jurisdiction's official schedule and a written closing estimate, and confirm in writing whether a transfer at death pays the tax."], STATUS["guidance"], ["sf_fees", "ca_rtc11911"]),
            (["Credit the live-in path with the rent it avoids", "A comparison that charges the invested path for housing but not the owned path is not a comparison; the avoided rent has no official source and must be documented privately.", "Obtain three written rent comparables and enter the middle value as a labelled imputed-rent line, applied symmetrically."], STATUS["guidance"], ["hud_fmr", "irs_rental"]),
            (["Show a distribution instead of a single projection", "Publish the worst, quartile, median and best ending values across the assumption grid, with the property-tax consequence kept on its own line because it does not depend on the market.", "Adopt the grid method in the private model and record whether each path's ranking survives the tails."], STATUS["guidance"], ["cbo_long", "fhfa", "sec_stocks"]),
            (["Decide the publication policy for case figures", "An owner instruction asked for costs to be published rounded to the nearest ten dollars; the containment policy adopted on this branch publishes no household figures at all, and the release check rejects a row badged as carrying figures supplied by the household. Both cannot be true of one public page.", "Choose deliberately: keep figures in the private workpaper, or relax the policy and re-add rounding enforcement. Record the choice and the date in the decision log rather than letting two rules coexist."], STATUS["unverified"], ["github_sensitive", "irs_basis"]),
            (["Keep the re-check on a schedule, not in memory", "Annual rebuild and refresh, biennial reading of the indexed property-tax allowance, a check each legislative session, and immediate recalculation on an event that starts a deadline.", "Adopt the published cadence, run the rebuild-and-diff check on it, and record each review with its date."], STATUS["guidance"], ["boe_lta", "irs_2027", "congress_law"]),
        ]
        body = table("Review queue — choose before implementation", ["Suggestion", "Why it helps", "Next step"], rows)
        body += '<section class="prose"><h2>Review status</h2><p>Use the controls below to mark suggestions for discussion in this browser session. Choices are kept in memory only, are not sent anywhere, and are cleared on refresh.</p><div class="review-queue">'
        # One control per suggestion, derived from the queue so adding a row cannot desync it.
        for i in range(1, len(rows) + 1):
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
        body = table("Operating-cost evidence plan", ["Cost category", "What drives the cost", "Evidence / action"], rows)
        body += table(
            "Rental depreciation, the clawback it creates, and the personal-use switch",
            ["Rule", "What the official source states", "How it changes a path comparison"],
            [
                (["Only the building depreciates", "Residential rental property is recovered straight-line over the stated recovery period under the general depreciation system, using a mid-month convention; land is never depreciable and the basis used for depreciation excludes it.", "A gross-value figure is not a depreciable base. The private model needs a land/building allocation, and an addition to a rental house follows the same class life."], STATUS["rule"], ["irs_rental"]),
                (["Deductions count whether or not they were taken", "Depreciation reduces basis, and the reduction applies to depreciation allowed or allowable; a sale is measured against adjusted basis.", "Skipping the deduction does not avoid the repayment. A building that has been rented carries the reduced basis even if no return claimed it, so the CPA must reconstruct it."], STATUS["rule"], ["irs_rental", "irs_pub551"]),
                (["The recovered amount returns as gain at a capped rate", "Gain is the excess over adjusted basis; the part attributable to depreciation on real property used in a business or for investment is unrecaptured section 1250 gain, taxed at a maximum 25% federal rate. Short-term gain is ordinary income.", "Sheltering at a high marginal rate and repaying at up to 25% is a timing benefit, not a saving. Publish both halves or neither, and remember a ceiling is not the taxpayer's rate."], STATUS["rule"], ["irs_topic409", "irs_rental"]),
                (["California does not discount the gain", "The state Franchise Tax Board states there is no special tax rate for capital gains; gains are taxed like other income, and an additional one percent applies to the portion of taxable income above the statutory threshold.", "A federal-only recapture estimate understates the exit cost. Model the sale year with the household's ordinary rates and the threshold, not a federal capital-gains bracket."], STATUS["rule"], ["ftb_cap_gains", "ca_rtc17043", "ftb_540es"]),
                (["An inherited rental starts from a new base", "Basis for property acquired from a decedent is generally the fair market value at death, and an estate that must report basis can bind the beneficiary's initial basis to the reported value.", "Depreciation accumulated before death does not attach to the stepped-up portion, but the heir's own recovery period begins at the new base — so the recapture question belongs to the years after the transfer."], STATUS["rule"], ["irs_basis", "irs_pub551", "irs_8971"]),
                (["Living in part of a rented building changes the income line", "If the owner occupies part of a structure, gross rental income includes the fair rental value of the part not held out for rent, and personal-use limits decide which deductions may be claimed against rental income.", "The conversion year is not a free switch: the same year can carry both rental and personal-use treatment, and mis-stating it moves both the deduction and the later repayment."], STATUS["rule"], ["irs_rental"]),
                (["A main home is not depreciable", "Depreciation is allowed for property held for the production of income or for business use; a residence the owner occupies is not such property.", "The path that lives in the inherited home forgoes the deduction stream — and forgoes the clawback with it. That symmetry is the honest way to compare the paths."], STATUS["rule"], ["irs_rental", "irs_121"]),
            ],
        )
        body += table(
            "Five-year capital plan: what to inspect, and how each item is treated",
            ["Building system", "What the plan must record", "Treatment to confirm"],
            [
                (["Roof, structure, drainage", "Inspection date, remaining life, defect list, two or more licensed bids per item, and whether a failure creates a habitability or disclosure issue.", "Ordinary repairs that keep the property working are expenses; a replacement that adds value or extends life is a capital improvement recovered through depreciation."], STATUS["guidance"], ["cslb", "irs_rental"]),
                (["Electrical, HVAC, plumbing, fire safety", "Age and capacity against the configuration actually intended — a multi-unit rental and a single-family home need different panel, egress and separation answers.", "Work done at the same time as a change of use may need to be allocated between the rental and personal-use periods."], STATUS["guidance"], ["cslb", "irs_rental"]),
                (["Windows, envelope, insulation, solar", "Whether equipment is shared between units or with an owner-occupied portion, and the interconnection date that sets the export arrangement.", "An addition to a rental house is residential rental property; shared or personal-use portions need allocation."], STATUS["guidance"], ["irs_rental", "cpuc_solar"]),
                (["Water heating, leaks, sewer laterals", "The condition items a water provider or an insurer will ask about, and any mandatory upgrade with its compliance deadline.", "Emergency repairs are usually expenses; a betterment or adaptation is capitalized, and casualty treatment is a separate question for the CPA."], STATUS["guidance"], ["irs_rental", "water_board"]),
                (["Seismic bracing and tenant safety items", "The scope the household is willing to fund, with a dated decision either way rather than silence.", "Deferred capital is a cost that arrives later; recording the decision to defer is what makes it a choice instead of an error."], STATUS["guidance"], ["cslb", "cdi"]),
                (["Reserve funding", "A monthly sinking-fund target per building built from bids, not from a percentage of value, beside the deductibles and coverage limits that decide who pays when something fails.", "Reserves are not deductible; they are the cash that prevents a forced sale. Coverage limits decide whether a failure is an inconvenience or a liquidity event."], STATUS["guidance"], ["cdi", "cslb"]),
            ],
        )
        body += table(
            "Rent evidence: the standard a comparable has to meet",
            ["Evidence type", "Acceptable as a market comparable?", "Why"],
            [
                (["Written listing or executed lease abstract from a licensed agent or manager, dated, for a similar home in the same submarket", "Yes — three of them, and use the middle of the range", "It is a documented, dated market observation for a comparable unit, with the term and any concessions stated."], STATUS["guidance"], ["irs_rental"]),
                (["An asking price on a rental listing site", "No, on its own", "An asking price is not a rent, so nothing on this site is derived from asking prices alone."], STATUS["guidance"], ["irs_rental"]),
                (["A voucher program payment standard", "No", "A payment standard is an administrative parameter for a program contract, not a market rent for a specific home; it is not used as a benchmark anywhere on this site."], STATUS["guidance"], ["hud_fmr"]),
                (["An area median from a data aggregator", "No", "Medians describe a geography, not a building of this size, condition and configuration; they are context at best."], STATUS["guidance"], ["hud_fmr", "fhfa"]),
                (["Nothing documented", "The row stays blank and is flagged", "Leaving the value visible as unknown tells the reader the rent comparison is unresolved, instead of hiding it behind a guess."], STATUS["missing"], ["irs_rental"]),
            ],
        )
        body += callout("What this page cannot tell you", "No rent, premium, bill or repair figure for a specific property is published here, and none is inferred from an average. The evidence standard above exists so the private workpaper can be filled by a professional instead of guessed in public.", "warning")
        return "Costs & coverage", "Use actual records and written quotes; do not substitute unsupported regional averages.", body
    if path.endswith("projections.html"):
        rows = [
            (["Market value", "Low/base/high annual appreciation scenarios × independent starting appraisal." , "FHFA index is broad context, not an individual forecast; use a written appraisal and scenario range."], STATUS["assumption"], ["fhfa", "cbo_long"]),
            (["Taxable assessed value", "Apply actual base value, statutory inflation factor, ownership-change rules and any qualifying exclusion." , "Assessor confirms transfer treatment and Prop 19 claim in writing."], STATUS["guidance"], ["ca_rtc51", "boe_prop19", "ca_rtc63"]),
            (["Property tax bill", "Taxable value × verified tax-rate-area levy plus parcel-specific direct charges." , "Obtain current bill and published tax-rate-area schedule; do not infer from assessed-value growth."], STATUS["missing"], ["boe_prop19", "ca_rtc51"]),
            (["Operating cash flow", "Rent, imputed rent for living paths, utilities, insurance, maintenance, vacancy, management and debt." , "Use current documents and refresh annually; model rents and costs as ranges."], STATUS["guidance"], ["irs_rental", "cdi", "cslb"]),
            (["Inflation and investment", "Use distinct inflation, interest, equity, recession and recovery regimes rather than one 50-year rate." , "CBO is a bounded baseline; BLS and Federal Reserve sources describe history, not probabilities."], STATUS["guidance"], ["cbo_long", "bls_cpi", "fed_inflation", "sec_stocks"]),
        ]
        body = table("Projection worksheet design (no household inputs stored)", ["Output", "Method", "Verification"], rows)
        body += table(
            "Outcome distribution: the method, stated before any number",
            ["Step", "What to do", "Why it belongs in the analysis"],
            [
                (["Lay out the assumption grid", "Cross the market-growth band with the inflation band and value each path at every cell, weighting the cells equally unless there is a documented reason not to.", "One rate implies precision the evidence cannot support; the grid is where a ranking is actually decided."], STATUS["guidance"], ["fhfa", "bls_cpi"]),
                (["Publish the spread, not the middle", "Report the bottom, the quartiles, the median and the top of the ending values, in nominal and in inflation-adjusted terms, and keep the number of cells visible.", "A median hides the case where the plan fails, and the tails are what a household actually experiences."], STATUS["guidance"], ["sec_stocks", "cbo_long"]),
                (["Keep certainty on its own line", "Show the property-tax consequence of the transfer separately from the growth assumption, because it does not depend on the market performing.", "A tax result that survives every cell of the grid is the only kind of figure a plan should lean on."], STATUS["guidance"], ["ca_rtc51", "boe_prop19"]),
                (["Label every cell as what it is", "Distinguish official figures, published schedules and assumptions, and never present an assumed rate as a source finding.", "The register and the badges exist so a reader can trace a number to a document, or see that no document exists."], STATUS["guidance"], ["irs_estate", "boe_lta"]),
                (["Rebuild after any input change", "Re-run the model and the site together, and record whether the ranking moved — not merely whether the build passed.", "An input change that reverses a recommendation is a finding; a passing build proves nothing about it."], STATUS["guidance"], ["irs_basis", "ftb_cap_gains"]),
                (["Do not extend history forward", "Use historical episodes as magnitudes and durations to test against, not as a path; no official source forecasts an individual home or portfolio decades out.", "Stress rows are the part of a framework most likely to go stale silently, so they are re-read on a published cadence."], STATUS["guidance"], ["fed_1929", "fed_2008", "fed_inflation"]),
            ],
        )
        body += method_chart()
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
        body = table("Property-tax decision gates", ["Rule", "Officially established", "Action"], rows)
        body += table(
            "Transfer tax, recording charges and the change-of-ownership filing",
            ["Charge or rule", "What the published schedule establishes", "Consequence for a sale or transfer"],
            [
                (["Documentary transfer tax is charged per 500 dollars of consideration", "The city-county schedule states an amount per 500 dollars of consideration in tiers that rise with price, with a reduced per-500 amount for rent-restricted affordable housing.", "A sale cannot be priced as if one flat rate applied; the local rate, the tier and the rounding convention must be read from the schedule for the jurisdiction and the year."], STATUS["rule"], ["sf_fees", "ca_rtc11911"]),
                (["The applicable tier can reach the whole consideration", "Under the published schedule the tier amount per 500 dollars applies to the entire consideration once the price crosses a tier boundary, rather than only to the excess above it.", "A price just above a boundary can cost far more in tax than one just below it — more than the difference in price. Have escrow confirm the method for the parcel and year, and never re-time or split a sale price to sit just over a line."], STATUS["rule"], ["sf_fees"]),
                (["Recording charges and the real-estate fraud fee", "A base charge covers the first page, with per-page and nonstandard-page charges on top, plus a fee on documents affecting title that is not charged when recorded concurrently with a transfer that pays transfer tax.", "Closing cost is document-driven: page count, the number of instruments and concurrent filing all change the total, so it belongs in the escrow estimate rather than a rule of thumb."], STATUS["rule"], ["sf_fees", "ca_gov27361"]),
                (["The local affordable-housing parcel fee and its exemptions", "The per-parcel fee applies to declarations of change in ownership and is capped per transaction, with an exemption for documents that pay transfer tax and for a residential dwelling transferred to an owner-occupier — which must be declared on the face of the instrument or on a coversheet.", "Exemptions are claimed in writing at recording; an undeclared exemption is paid. Confirm who signs the declaration, and do not assume a transfer at death is exempt."], STATUS["rule"], ["sf_fees"]),
                (["The change-of-ownership screening form", "A fee is charged when a transfer document is recorded without the required change-of-ownership statement; the state statute separately sets a filing deadline for specified transfers by reason of death.", "Missing the form is a fee that buys nothing, and the death-transfer filing window runs whether or not a sale is planned."], STATUS["rule"], ["sf_fees", "ca_rtc480"]),
                (["Whether a transfer at death pays transfer tax", "That question is answered by the local ordinance and the recorder, not by a general rule; no jurisdiction-neutral answer is published on this site.", "Obtain the recorder's written position before relying on an exempt transfer, and keep separate the transfer-tax question and the change-in-ownership question."], STATUS["unverified"], ["ca_rtc11911", "ca_rtc480"]),
                (["The second building's jurisdiction", "No official schedule for the anticipated-trust property's county could be confirmed for this build, so no amount is published for it and no neighbouring-city add-on is assumed.", "Read the county ordinance and the recorder's schedule, then price them into the private model beside the city figures."], STATUS["missing"], ["boe_counties"]),
                (["The top-tier increase and the measure's real name", "The city's own page records that the November 2020 measure raising the top two transfer-tax tiers was Proposition I. A measure referred to as 'Prop H' could not be matched to any property, transfer-tax or landlord measure in the official material reviewed.", "Cite the measure that exists. Before modeling a proposal under the other name, confirm jurisdiction, year and ballot number and read the official text; nothing on this site depends on an unidentified measure."], STATUS["unverified"], ["sf_prop_i", "sos_measures"]),
            ],
        )
        body += table(
            "Carrying the Proposition 19 allowance forward",
            ["Fact to hold", "Current official position", "Why it decides the outcome"],
            [
                (["What the exclusion actually preserves", "A qualifying family-home transfer keeps the transferor's factored base year value plus an adjusted value-limit amount; the excess of market value over that sum is added to the new base, and the taxable value cannot exceed market value.", "The allowance, not the low base, is the decisive number: it is the only term that shrinks the reassessment, and it is capped at the property's value."], STATUS["rule"], ["ca_rtc63", "boe_prop19"]),
                (["The allowance is indexed on a published schedule", "The letter to assessors gives the amount in effect through mid-February 2027 and states that it is adjusted every two years using the federal housing index for California, with the next adjustment due in 2027.", "For a transfer decades away no one can publish the amount in advance: project it as a labelled assumption, and read the official figure for the actual year of transfer before a claim is prepared."], STATUS["rule"], ["boe_lta", "fhfa"]),
                (["Prior claims reduce what is available", "The statute limits what may be excluded across family-home transfers of the same property, including later transfers, and treats subsequent transfers under its own conditions.", "A property whose transferor already used an exclusion may carry less relief than the published allowance implies; the assessor's claim history decides it, not the statutory maximum."], STATUS["missing"], ["ca_rtc63"]),
                (["Occupancy and filing conditions", "The claimant must occupy the home as a principal residence and file the homeowners' exemption within the required period, and the property-tax claim has a separate deadline; relief is disallowed if the conditions fail.", "A claim made for a house that is then rented is the fact pattern the conditions are written against: the cost is reassessment plus the loss of the filing position."], STATUS["rule"], ["boe_prop19", "ca_rtc218", "ca_rtc63"]),
                (["Renting after the claim is a separate question", "The rules distinguish a qualifying owner-occupied transfer from later rental use, and conversion consequences are property-specific.", "Do not treat a live-in plan as revocable at will: model the later-rental branch before claiming, and retain the written determination with the trust records."], STATUS["guidance"], ["boe_prop19", "ca_rtc63"]),
            ],
        )
        body += prose("Publication note", "This page states the rules and where each figure comes from. Amounts for a specific building are not published here: they belong in a private workpaper, where they can be reconciled to a tax bill, a deed, an escrow statement and a return instead of to a public page.")
        return "Property-tax rules", "Current California rules are conditional; verify future law and property-specific facts.", body
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
            (["Future threshold", "No official source can establish a future estate exclusion decades ahead; Congress can amend law." , "Use dated scenarios only and refresh from enacted law and IRS annual guidance."], STATUS["assumption"], ["congress_law", "irs_2027"]),
            (["What the filing test adds up", "The estate-tax filing test is built from the gross estate plus adjusted taxable gifts plus the specific gift-tax exemption, so gifts made decades earlier can create a filing duty on their own.", "Assemble the gift history before concluding that an estate is below a threshold: obtain every prior gift-tax return and a written schedule of gifts above the annual exclusion."], STATUS["rule"], ["irs_estate", "irs_estate_faq"]),
            (["Portability needs a timely return", "A deceased spouse's unused exclusion is available only if the survivor's estate elects it on a timely filed return, which can mean filing when no tax is due.", "Ask now, for each spouse, whether an election was made or is still available; an election missed at the time is usually gone."], STATUS["rule"], ["irs_estate_faq", "irs_706"]),
            (["Filing and paying are separate deadlines", "An extension request extends the time to file, not the time to pay; an extension obtained after the due date does not cure a late payment.", "Put both dates on one page of the executor checklist, with the source of the cash named against the payment date."], STATUS["rule"], ["irs_706", "irs_estate_faq"]),
            (["Liquidity is a different question from liability", "Whether tax is owed is an estate-level calculation; whether it can be paid without selling real property is a cash question, and estate tax is paid in cash on a fixed date.", "Size liquid reserves against the filing and payment calendar. A threshold comparison is not a liquidity plan, and real property is not cash."], STATUS["guidance"], ["irs_estate", "irs_estate_faq"]),
            (["What this site cannot see", "No estate inventory, cash position, debt schedule, insurance or retirement beneficiary designations or prior-gift history is published, and none is inferred.", "Keep the inventory in the private workpaper; bring it to the CPA with the two dates that matter, and record who confirmed each figure."], STATUS["missing"], ["irs_estate", "irs_basis"]),
        ]
        return "Estate-tax thresholds", "The exclusion is not a per-heir allowance; assess the whole estate and year of death.", table("Estate and inheritance tax questions", ["Topic", "Current official information", "Next step"], rows)
    if path.endswith("law-watchlist.html"):
        rows = [
            (["Enacted federal law", "Public Law 119-21 is enacted; use the current IRS annual amounts and statute rather than old proposals." , "Document enactment date and operative year; recheck IRS guidance annually."], STATUS["rule"], ["congress_law", "irs_2027"]),
            (["Pending federal proposals", "A bill or proposal is not law unless enacted; no proposal-specific household outcome is modeled here." , "For each bill, record official status, text, committee action, effective date and whether it became law."], STATUS["guidance"], ["congress_law"]),
            (["California ballot measures", "Qualified list, measure text, election results and operative law are distinct records." , "Check official text and certified results; do not infer effect from a title."], STATUS["guidance"], ["sos_measures"]),
            (["Property-tax law", "Current Proposition 19 rules remain subject to amendment and future BOE indexed amount updates." , "Recheck BOE, statute and local assessor immediately before transfer."], STATUS["rule"], ["boe_prop19", "boe_lta", "ca_rtc63"]),
            (["Local measure called 'Prop H'", "Ambiguous without jurisdiction, year and official ballot number; no terms or impact are asserted. The city's own page shows the in-force transfer-tax tier increase came from Proposition I in November 2020." , "Confirm with the owner which jurisdiction, year and letter is meant, then read the official voter guide text and certified result. Nothing here depends on an unidentified measure."], STATUS["unverified"], ["sos_measures", "sf_prop_i"]),
            (["County transfer-tax schedules", "A county may levy a documentary transfer tax and set its own rate, exemptions and rounding; the schedule for the anticipated-trust property's county was not confirmed for this build, so no amount is published for it.", "Read the county ordinance and the recorder's fee schedule, and obtain the recorder's written position on whether a transfer at death is exempt, before pricing a sale."], STATUS["missing"], ["ca_rtc11911", "boe_counties", "sf_fees"]),
            (["Home-sale exclusion on an inherited home", "The exclusion's ownership and use tests are published; whether an heir counts the decedent's ownership period is not settled by the sources cited here.", "Get the CPA's written position before the exclusion is switched on in any model of a later sale."], STATUS["unverified"], ["irs_121"]),
        ]
        body = table("Legislation and rules to refresh", ["Item", "Status distinction", "Verification routine"], rows)
        body += table(
            "Re-check cadence — who looks, how often, and at what",
            ["Cadence", "What to re-read", "Why this interval"],
            [
                (["Every year, on a fixed date", "Rebuild the site and the private model together and record whether the ranking moved; refresh the IRS annual inflation adjustments, each building's assessor roll and tax bill, written insurance quotes, and any local rent adjustment published for the coming period.", "A run that reproduces the same ranking is evidence it is robust; a run that reverses it is the cheapest warning available."], STATUS["guidance"], ["irs_2027", "boe_counties", "cdi"]),
                (["Every two years, in February", "The indexed value-limit amount for a family-home transfer, adjusted on a published biennial schedule using the federal housing index for California.", "This single figure decides how much of a low base survives a transfer, so it must be read from the official release rather than projected."], STATUS["rule"], ["boe_lta", "fhfa"]),
                (["Every legislative session", "Estate and gift proposals, any state death-tax or property-tax measure, and local transfer-tax or rent ordinances — recorded as enacted, chaptered with limited scope, or introduced only.", "A proposal changes a plan only when enacted with an effective date; treating a bill as law is how a model quietly rewrites the answer."], STATUS["guidance"], ["congress_law", "sos_measures"]),
                (["Annually, for stress cases", "Re-read the historical anchors and the bounded official baselines used in the stress rows and confirm the published magnitudes still match.", "Nothing in law forces these rows to be updated, which is exactly why they need a scheduled re-read."], STATUS["guidance"], ["fed_1929", "fed_2008", "bls_cpi", "cbo_long"]),
                (["Immediately on an event", "Death, a trust amendment, a lease ending, an insurance non-renewal, a ballot result that changes a tax, or a decision to occupy or not occupy: recalculate every clock that starts from that event.", "Statutory deadlines do not pause for analysis, and a missed filing window cannot be recovered later."], STATUS["rule"], ["ca_prob", "ca_rtc480", "irs_706", "boe_prop19"]),
            ],
        )
        body += prose("What is deliberately not modeled", "No proposal-specific household outcome is published, and no unidentified ballot measure is given terms. Where the official text has not been read, the row says so and names the step that would close it.")
        return "Law watchlist", "A proposal is not enacted law. Track official status, effective dates and source-check dates.", body
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
        body += staging_index_table()
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
            (["Depreciation and recapture", "What has been depreciated on each building, what was allowable but not claimed, and what is repaid at a sale in the intended year?", "Depreciation schedules by year, acquisition and improvement records, the land/building allocation, and a recapture calculation at a stated price band."], STATUS["missing"], ["irs_rental", "irs_topic409", "ftb_cap_gains"]),
            (["Occupancy and the home-sale exclusion", "Will the heir occupy the inherited home for the required period, and does any part of the decedent's ownership count?", "A dated occupancy plan, the intended sale year, prior use of the exclusion, and the CPA's written position before the exclusion is modeled."], STATUS["missing"], ["irs_121"]),
            (["Closing costs and transfer taxes", "What do documentary transfer tax, recording charges, the change-of-ownership screening fee and any local add-on cost in each jurisdiction, and is a transfer at death exempt?", "The official schedule for each jurisdiction, the recorder's written position on a death transfer, and a closing estimate from an escrow officer."], STATUS["missing"], ["sf_fees", "ca_rtc11911", "ca_rtc480"]),
            (["Exchange versus taxable sale", "Is a like-kind exchange wanted, does held-for-use qualify on both sides, and is a carried-over basis acceptable to the heirs?", "A written adviser note before listing, the identification and receipt calendar, and qualified intermediary terms if an exchange proceeds."], STATUS["missing"], ["irs_1031", "irs_8824"]),
            (["Condition and reserves", "What does each building need in the next five years, and is each item a repair or a capital improvement?", "Inspection reports, two or more licensed bids per item, the classification the CPA will use, and the funded reserve target beside the insurance deductibles."], STATUS["missing"], ["cslb", "cdi", "irs_rental"]),
            (["Decision criteria before the figures", "What would make the household choose each path, and what would reverse it?", "A signed, dated one-page criteria statement kept with the private records, updated whenever a criterion changes."], STATUS["guidance"], ["sec_stocks", "boe_prop19"]),
        ])
        body += '<p class="no-print"><button class="print-button" id="print-page" type="button">Print this one-page brief</button></p>'
        return "Attorney & CPA briefing sheet", "One-page print-ready checklist for counsel and the tax adviser.", body
    if path.endswith("decision-log.html"):
        rows = [
            (["Decision rule", "What choice would be made under each eligible path, before figures are revealed?", "Write dated criteria, including liquidity, occupancy, tax eligibility and risk limits."], STATUS["guidance"], ["sec_stocks", "boe_prop19"]),
            (["Evidence", "Which official document, quote, appraisal, lease, tax return or professional opinion changed the decision?", "Record source, date, reviewer, uncertainty and any contrary evidence."], STATUS["guidance"], ["irs_basis", "irs_rental", "cdi"]),
            (["Decision and date", "What was chosen, by whom, when, and why?", "Record the rejected alternatives and the conditions that would reopen the decision."], STATUS["guidance"], ["irs_estate_faq", "boe_prop19"]),
            (["Rule adopted — recapture is modeled beside depreciation", "Adopted for this build: any path that rents a building carries the deduction and the repayment, so a comparison that shows one without the other is rejected. Recorded as a method rule, not a household result.", "The rules table on the costs page; the private model must reconcile to the CPA's depreciation history when it arrives."], STATUS["rule"], ["irs_rental", "irs_topic409"]),
            (["Rule adopted — transaction costs are priced from the recording jurisdiction's schedule", "Adopted for this build: no sale path is compared on a gross value, and no county amount is invented where the schedule was not confirmed.", "The transfer-tax table on the property-tax page; the blank county row and its next step are recorded on the flagged page."], STATUS["rule"], ["sf_fees", "ca_rtc11911"]),
            (["Rule adopted — the live-in path is charged nothing and credited nothing at first", "Adopted for this build: avoided rent enters the comparison only as a documented private figure, so an unverified rent never moves a published ranking.", "The rent-evidence standard on the costs page; the open item stays in the question register until comparables exist."], STATUS["guidance"], ["hud_fmr", "irs_rental"]),
            (["Decision needed — publication policy for case figures", "Recorded as open: a rounded-figure publication layer and the containment policy in force are mutually exclusive on a public page, and this session did not silently reverse either.", "Owner decides and dates the outcome in this log; the verifier enforces whichever policy is chosen."], STATUS["unverified"], ["github_sensitive"]),
        ]
        return "Decision log", "Record the decision and date so a future reader can understand what was chosen and why.", table("Decision-log template", ["Entry", "Prompt", "Record"], rows)
    if path.endswith("flagged-for-review.html"):
        rows = [
            (["No private inventory", "Property values, assessed values, rent, bills, leases, title and insurance records are deliberately absent." , "Build and store the inventory offline; do not add it to Git or the site."], STATUS["missing"], ["irs_basis", "irs_rental", "cdi"]),
            (["Future-year law and economic path", "A transfer expected decades from now cannot be determined from present rules or official baseline forecasts." , "Recheck current law, indexed amounts, proposals and markets annually."], STATUS["guidance"], ["irs_2027", "boe_lta", "cbo_long"]),
            (["California sale-year tax sensitivity", "The one-percent additional tax above taxable income of $1,000,000 and ordinary-rate capital-gain treatment are stated on official statute/FTB sources. No household calculation is published, and the full Form 540 booklet was not retrieved for this build." , "CPA verifies current Form 540 instructions and calculates the sale-year tax from private basis and taxable-income facts."], STATUS["missing"], ["ca_rtc17043", "ftb_540es", "ftb_cap_gains", "ftb_forms"]),
            (["Prop H", "The identifier alone does not establish jurisdiction, election year or measure text; no impact is modeled." , "Confirm official measure and full text with the relevant election authority."], STATUS["unverified"], ["sos_measures"]),
            (["History / repository exposure", "Earlier public Git objects and copies may retain content no longer shown on the site. A site rebuild cannot recall prior clones, PR diffs or caches." , "Repository administrator should assess visibility, history remediation and GitHub Support options; preserve a private archive before a rewrite."], STATUS["missing"], ["github_sensitive"]),
            (["Publication policy conflict: rounded case figures versus none", "One owner instruction directed that costs be published rounded to the nearest ten dollars so they cannot be traced to a source record, and a decision-analysis layer was built on that basis. The containment policy now in force publishes no household figures at all, and the release check rejects the badge such a row would carry. The two cannot both be satisfied on one public page.", "An explicit owner decision, recorded and dated in the decision log: keep the containment policy and hold every figure in the private workpaper, or relax it and restore the rounded publication path with the rounding checks that make it safe. Until then the figures stay out of the site."], STATUS["unverified"], ["github_sensitive", "irs_basis"]),
            (["Enforcement added, and what it cannot do", "The verifier now scans every tracked text file, not only the manifest pages, for comma-grouped amounts that are not rounded tens or registered official figures, for rounded-to-unrounded mapping patterns, and for a committed redaction-rules file. It also requires the state trustee-notice, change-in-ownership, recording-fee, transfer-tax and high-income surcharge statute identifiers to appear as registered official figures.", "A current-tree check cannot erase history. Run it on every commit and pull request, and re-read the runbook before publishing any new tool, script or note file."], STATUS["guidance"], ["github_sensitive"]),
            (["County transfer-tax schedule for one building", "No official county schedule could be confirmed for this build, so the sell path for that property is priced without transfer tax or recording charges and the row is left blank rather than estimated.", "Read the county ordinance and recorder's schedule, and obtain the recorder's written position on whether a transfer at death is subject to the tax, before the closing estimate is treated as complete."], STATUS["missing"], ["ca_rtc11911", "boe_counties"]),
            (["Home-sale exclusion period on an inherited home", "The published tests cover ownership and use in a five-year window; whether an heir may count the decedent's ownership period is not established by the sources cited on this site.", "Have the CPA put the position in writing, with the authority relied on, before any path assumes the exclusion applies."], STATUS["unverified"], ["irs_121"]),
            (["Rent, insurance, repair and utility figures", "No property-specific rent, premium, bill or bid is published; a voucher payment standard and an area median are expressly rejected as market comparables, so the live-in comparison stays open.", "Three written comparables, two quotes per coverage type, and licensed bids per capital item, held in the private workpaper and summarized here only as evidence status."], STATUS["missing"], ["hud_fmr", "cdi", "cslb"]),
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
            (["Unrecaptured section 1250 gain", "The part of a long-term gain on depreciated real property attributable to depreciation allowed or allowable, taxed at a capped federal rate.", "Treat depreciation as a loan from the tax authority: it shelters income now and is repaid at sale, and California taxes the same amount as ordinary income."], STATUS["rule"], ["irs_topic409", "ftb_cap_gains"]),
            (["Basis used for depreciation", "The depreciable portion of cost or other basis — the building, not the land — reduced by depreciation taken or required to be taken.", "Ask for the land/building allocation and the depreciation schedule, not just the purchase price."], STATUS["rule"], ["irs_rental", "irs_pub551"]),
            (["Stepped-up basis", "For property acquired from a decedent, basis is generally the fair market value at death, subject to exceptions and to estate basis-reporting consistency.", "It explains why a sale soon after a transfer can produce little gain, and why an inherited rental begins a fresh recovery period."], STATUS["rule"], ["irs_basis", "irs_pub551", "irs_8971"]),
            (["Documentary transfer tax", "A tax on the document that transfers real property, commonly stated per 500 dollars of consideration, with local rates, tiers and exemptions set by ordinance.", "Price the sale, not just the price: the tier method can make a lower price meaningfully cheaper to convey."], STATUS["rule"], ["ca_rtc11911", "sf_fees"]),
            (["Change-of-ownership screening", "The filing that lets the assessor evaluate whether a transfer changes the taxable value, required on its own deadline for specified death transfers, with a fee when a transfer document is recorded without it.", "Filing it is not agreement that reassessment is owed; the property-tax claim is a separate, later filing."], STATUS["rule"], ["ca_rtc480", "sf_fees"]),
            (["Imputed, or avoided, rent", "The market rent a household does not pay because it occupies a home it owns, used only to compare an owned path against a path that must buy housing.", "Never booked as income. Its whole purpose is to stop a live-in path being credited with free housing."], STATUS["guidance"], ["hud_fmr", "irs_rental"]),
            (["Outcome distribution", "The set of ending values a model produces across its assumption bands, reported as a spread with the number of cells shown.", "A point estimate is one bar of a histogram; the ranking of live, rent and sell depends on the tails."], STATUS["guidance"], ["cbo_long", "fhfa", "sec_stocks"]),
            (["Re-check cadence", "The published schedule on which each rule, amount and assumption is re-read from its official source.", "A decision aid goes stale in silence unless the re-read is scheduled and named."], STATUS["guidance"], ["irs_2027", "boe_lta", "congress_law"]),
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
            (["Whole-tree scanning", "The release check now inspects every tracked text file — scripts, plans, notes, configuration — for comma-grouped amounts that are not rounded tens or registered official figures, for rounded-to-unrounded mapping patterns, and for a committed redaction-rules file.", "A page-level check misses a figure written in a tool or a plan; a tree-level check catches it. It still cannot see a value that was never comma-grouped, so the rounding rule is enforced at the source of every published amount as well."], STATUS["guidance"], ["github_sensitive"]),
            (["Rounded figures as a privacy method", "Rounding to ten dollars was directed as a way to publish decision-driving numbers without exposing a source record. It reduces, and does not remove, re-identification risk: a short series of rounded values can still match one property.", "Treat any rounded figure as publishable only if its owner would also publish the unrounded one. The containment policy currently in force takes the stricter line and publishes no case figures; that choice is recorded and dated in the decision log rather than left to two rules coexisting."], STATUS["unverified"], ["github_sensitive"]),
            (["Identifiers removed from the site", "Property locations, parcel identifiers and account numbers are absent from the current pages, and the generator reads no data file, so no identifier can be emitted from an input.", "Anyone with repository access can still read tracked tool and note files; keep redaction rules and private data outside every clone."], STATUS["guidance"], ["github_sensitive"]),
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


def method_chart() -> str:
    """Method illustration: an outcome spread in index units, rendered at build time.

    Deliberately unit-free. An index (central case = 100) lets the page show what a
    distribution looks like — including that the tails can reverse a ranking — without
    publishing or implying any household amount, property or date. Inline SVG only: no
    script, no remote asset, nothing stored.
    """
    labels = ("worst", "low", "central", "high", "best")
    indexes = (62, 84, 100, 121, 145)
    heights = (24, 52, 78, 60, 34)
    bars = "".join(
        f'<rect x="{12 + i * 62}" y="{100 - height:.1f}" width="40" height="{height:.1f}" '
        f'fill="currentColor" opacity="{0.25 + 0.15 * i:.2f}"></rect>'
        for i, height in enumerate(heights)
    )
    ticks = "".join(
        f'<text x="{32 + i * 62}" y="94" text-anchor="middle" class="chart-value">{esc(value)}</text>'
        f'<text x="{32 + i * 62}" y="112" text-anchor="middle" class="chart-label">{esc(label)}</text>'
        for i, (label, value) in enumerate(zip(labels, indexes))
    )
    return (
        '<figure class="chart" role="img" aria-label="Illustrative outcome spread in index units: '
        'worst 62, low 84, central 100, high 121, best 145">'
        '<svg viewBox="0 0 310 120" preserveAspectRatio="xMidYMid meet" aria-hidden="true" focusable="false">'
        f"{bars}{ticks}</svg>"
        "<figcaption>Method illustration, not a forecast. Ending values across an assumption grid, as an index "
        "where the central case is 100. The bars are equally weighted grid cells, not probabilities; no household "
        "amount, property or date is implied.</figcaption></figure>"
    )


def staging_index_table() -> str:
    """Crash-entry comparison for Treasury staging, in index units — no currency at all.

    Same shape as the page's local-only panel (linear price path, staged purchases, a
    reserve accruing at the stated yield), evaluated from a start of 100 so the published
    rows show the *shape* of the result without any household amount.
    """
    periods = 36
    reserve_yield = 4.3 / 100 / 12
    trough_months = 17

    def end_value(staging: int, decline_pct: float, crash_start: int | None, drift_pct: float) -> float:
        horizon = max(periods, (crash_start or 0) + trough_months)
        drift = drift_pct / 100 / 12

        def unit(month: int) -> float:
            value = 1.0 + drift * month
            if crash_start is not None and month > crash_start:
                elapsed = min(month - crash_start, trough_months) / trough_months
                value -= (decline_pct / 100) * elapsed
            return max(0.0001, value)

        cash, shares = 100.0, 0.0
        # Lump sum buys everything at the receipt price; staging buys a quarter of the
        # reserve at the end of each staging quarter, then anything left at the horizon.
        if staging == 0:
            return 100.0 * unit(horizon) / unit(1)
        installment = 25.0
        buys = {max(1, month) for month in (staging // 4, staging // 2, (3 * staging) // 4, staging)}
        for month in range(1, horizon + 1):
            cash *= 1 + reserve_yield
            if month in buys and cash > 0:
                buy = min(cash, installment)
                cash -= buy
                shares += buy / unit(month)
        if cash > 0:
            shares += cash / unit(horizon)
            cash = 0.0
        return shares * unit(horizon)

    # (label, decline magnitude, month the decline begins, annual drift before it)
    cases = [
        ("Flat prices, no decline", 0.0, None, 0.0),
        ("Rising prices at an 8% annual drift, no decline", 0.0, None, 8.0),
        ("2007-09 style 57% decline beginning during staging", 57.0, 15, 8.0),
        ("2007-09 style 57% decline beginning after staging ends", 57.0, 40, 8.0),
        ("1929 style 89% decline beginning during staging", 89.0, 15, 8.0),
        ("1929 style 89% decline beginning after staging ends", 89.0, 40, 8.0),
    ]
    rows = []
    for label, decline, crash, drift_pct in cases:
        lump = end_value(0, decline, crash, drift_pct)
        staged_24 = end_value(24, decline, crash, drift_pct)
        staged_36 = end_value(36, decline, crash, drift_pct)
        best = max(staged_24, staged_36)
        if best > lump + 0.05:
            reading = "staging ends ahead of immediate entry"
        elif best < lump - 0.05:
            reading = "staging ends behind immediate entry"
        else:
            reading = "no material difference in this path"
        rows.append((
            [label, f"{lump:.1f}", f"{staged_24:.1f}", f"{staged_36:.1f}", reading],
            STATUS["assumption"],
            ["treasury_bills", "treasury_notes", "fed_2008", "fed_1929", "cbo_long"],
        ))
    body = table(
        "Crash-entry test in index units (start = 100, no currency involved)",
        ["Scenario", "Invest all at receipt", "24-month Treasury staging", "36-month Treasury staging", "Reading"],
        rows,
    )
    return body + prose(
        "What this table can and cannot support",
        "It compares entry timing under a synthetic straight-line price path with a fixed decline length, a stated annual drift "
        "before any decline, and a reserve yield taken from the official near-term ten-year baseline. It models no dividends, "
        "fees, taxes, withdrawals, correlations or recovery after the trough, and it assigns no probability to any row. Staging "
        "can only help when the decline begins while money is still in Treasuries; the rows where it begins later exist to show "
        "exactly that. Read it as a shape, then run your own numbers in the panel on this page.",
    )


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
