#!/usr/bin/env python3
"""Build a public, privacy-first inheritance decision guide.

No household inputs are embedded, imported, inferred, or emitted. Private
records belong in an offline adviser workpaper, not this public repository.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import case_model as cm  # noqa: E402  (build-time model; reads no files)

SOURCES = {
    "irs_estate": ("IRS — Estate tax", "https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax", "Read 2026-11-17: the gross estate is valued at fair market value at death; deductions include mortgages, debts and administration expenses, and lifetime taxable gifts since 1977 are added before the unified credit is applied. Published filing thresholds include 13,990,000 dollars for 2025 deaths and 15,000,000 dollars for 2026 deaths, plus the portability note. Not an individual estate calculation."),
    "irs_estate_faq": ("IRS — Estate-tax filing FAQs", "https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-estate-taxes", "Read 2026-11-17: Form 706 is due nine months after death, a six-month extension is available on Form 4768 filed by the due date, the 2026 threshold is 15,000,000 dollars, portability requires a timely filed return, and Rev. Proc. 2022-32 gives a five-year late-election path only for estates below the filing threshold."),
    "irs_2027": ("IRS — 2027 tax inflation adjustments", "https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2027-taxpayers-continue-to-benefit-from-the-working-families-tax-cuts", "Read 2026-11-17 (IR-2026-133, November 5, 2026): the basic exclusion amount for 2027 deaths is 15,480,000 dollars, up from 15,000,000 for 2026; the annual gift exclusion rises to 20,000 from 19,000; the top individual rate stays 37 percent. No prediction beyond the published year."),
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
    "ca_rtc63": ("California Revenue and Taxation Code §63.2", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=63.2.&lawCode=RTC", "Read 2026-11-17 (as amended by Stats. 2025, Ch. 539 (SB 293), effective January 1, 2026): the family-home exclusion requires the transferor's principal residence and that it become the transferee's principal residence within one year, with a homeowners' or disabled veterans' exemption filed within one year; the new taxable value is the prior taxable value plus the excess of fair market value over that taxable value plus the indexed one-million-dollar amount, or zero if there is no excess; claims are filed within three years or before a transfer to a third party or the end of occupancy, whichever is earlier, or within six months of a supplemental or escape notice; a 45-day and then 60-day notice sequence applies and a county processing fee up to 175 dollars may be required. A 'transfer' expressly includes transfers through an inter vivos or testamentary trust. The section text read does not contain a carry-forward subdivision for an unused difference."),
    "boe_lta": ("California BOE — Letter to Assessors 2025/009", "https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf", "Read 2026-11-17: the 1,000,000 dollar amount in section 63.2 is adjusted every other 16 February by the prior calendar year's FHFA House Price Index for California; it is 1,044,586 dollars for transfers from 16 February 2025 through 15 February 2027 (1,022,600 for 2023-2025 and 1,000,000 for 2021-2023), based on a 2.15 percent 2024 California index change, and the next adjustment is due in February 2027."),
    "ca_rtc51": ("California Revenue and Taxation Code §51", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=51.&lawCode=RTC", "Taxable-value framework and annual inflation adjustment, subject to reassessment and statutory rules."),
    "ca_rtc218": ("California Revenue and Taxation Code §218", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=218.&lawCode=RTC", "Homeowners' property-tax exemption eligibility and amount."),
    "ca_rtc480": ("California Revenue and Taxation Code §480", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=480.&lawCode=RTC", "Change-in-ownership statement timing in specified death transfers."),
    "ca_rtc11911": ("California statute — documentary transfer tax",  "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=11911.&lawCode=RTC", "Read 2026-11-17: a county or city and county may impose a tax where consideration exceeds 100 dollars, at a rate of fifty-five cents for each five hundred dollars or fractional part (0.11 percent), and a city within such a county may impose one-half that rate (0.055 percent), with a credit for the city tax against the county tax. Whether a particular county or city has adopted a levy, its rate, and any exemptions must be read from that jurisdiction's ordinance."),
    "ca_gov27361": ("California statute — recording fees",  "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=27361.&lawCode=GOV", "Recording-fee statute; the actual fee depends on recorded document and applicable schedule."),
    "ca_prob": ("California Probate Code — trustee notice",  "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=16061.7.&lawCode=PROB", "Trustee notice obligations and timing for specified trust events, subject to applicability."),
    "ca_rent": ("California Civil Code §1947.12", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1947.12.&lawCode=CIV", "Statewide rent-cap text and exemptions; local law and unit coverage need separate review."),
    "cdi": ("California Department of Insurance — Residential insurance", "https://www.insurance.ca.gov/01-consumers/105-type/5-residential/index.cfm", "Insurance shopping resources and coverage context; no household premium or quote."),
    "cpuc_solar": ("California Public Utilities Commission — Net metering and net billing", "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/demand-side-management/customer-generation/net-energy-metering-and-net-billing", "Solar export tariff context; actual credits depend on tariff, interconnection date, usage and utility bill."),
    "water_board": ("California State Water Resources Control Board — Drinking Water Program", "https://www.waterboards.ca.gov/drinking_water/programs/", "State oversight and public-water-system information; does not establish a service account's bill."),
    "cslb": ("California Contractors State License Board — Check a license", "https://www.cslb.ca.gov/OnlineServices/CheckLicenseII/CheckLicense.aspx", "Contractor-license lookup; does not set or validate repair prices."),
    "treasury_bills": ("TreasuryDirect — Treasury bills", "https://treasurydirect.gov/marketable-securities/treasury-bills/", "Bill maturities, auction rates, holding/sale mechanics, and interest tax treatment."),
    "treasury_notes": ("TreasuryDirect — Treasury notes", "https://www.treasurydirect.gov/marketable-securities/treasury-notes/", "Note maturities and interest; market price may vary if sold before maturity."),
    "fed_1929": ("Federal Reserve History — Stock Market Crash of 1929", "https://www.federalreservehistory.org/essays/stock-market-crash-of-1929", "Read 2026-11-17: the Dow closed at 381.17 on 3 September 1929, fell 13 percent on 28 October and 12 percent on 29 October, lost almost half its value by mid-November, closed at 41.22 on 8 July 1932 - 89 percent below the peak - and did not regain the 1929 level until 23 November 1954. A price-index episode, not a portfolio forecast or probability."),
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
    "ftb_forms": ("California Franchise Tax Board — Forms and publications", "https://www.ftb.ca.gov/forms/", "Official entry point for current-year forms and instructions; the applicable year must be selected at the decision date."),
    "ftb_540": ("FTB — 2025 Form 540 instructions", "https://www.ftb.ca.gov/forms/2025/2025-540-instructions.html", "Read 2026-11-16: 2025 Form 540 instructions for line 62 state that if taxable income exceeds $1,000,000, compute the Behavioral Health Services Tax as 1% of the excess, using whole dollars. This establishes the published 2025 return instruction, not a future-year rule or private tax liability."),
    "ca_rtc17043": ("California statute — additional tax on high taxable income", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=17043.&lawCode=RTC", "Read 2026-11-15 in the official statute: additional 1% tax applies to taxable income above $1,000,000 for taxable years beginning on or after January 1, 2005; the statutory threshold is not indexed in the section text."),
    "ftb_540es": ("FTB — 2025 Form 540-ES instructions", "https://www.ftb.ca.gov/forms/2025/2025-540-es-instructions.html", "2025 estimated-tax worksheet; use the Form 540 instructions and current-year law for final return treatment."),
    "ftb_cap_gains": ("FTB — Capital gains and losses", "https://www.ftb.ca.gov/file/personal/income-types/capital-gains-and-losses.html", "Read 2026-11-15 (page updated 2026-01-28): California has no lower capital-gains rate; capital gains are taxed as ordinary income."),
    "ftb_gifts": ("FTB — Gifts and inheritance", "https://www.ftb.ca.gov/file/personal/income-types/gifts-and-inheritance.html", "Official FTB information about gifts and inheritances; read 2026-11-15. The page does not establish the basis or tax consequences of an individual transfer."),
    "boe_counties": ("California BOE — County assessor contacts", "https://www.boe.ca.gov/proptaxes/countycontacts.htm", "Official directory of county assessor offices; it lists contacts, not property-specific tax rates or assessments."),
    "sos_measures": ("California Secretary of State — Qualified ballot measures", "https://www.sos.ca.gov/elections/ballot-measures/qualified-ballot-measures", "Official ballot-measure list; full text and certified results must be checked separately."),
    "hud_fmr": ("HUD — Fair Market Rents", "https://www.huduser.gov/portal/datasets/fmr.html", "Housing-program benchmark methodology; not an appraisal, lawful rent, or current lease amount."),
    "irs_topic409": ("IRS Topic no. 409 — Capital gains and losses", "https://www.irs.gov/taxtopics/tc409", "Read 2026-11-17: for 2025 a 0 percent rate applies up to 48,350 dollars of taxable income for single filers, 15 percent up to 533,400 dollars, and 20 percent above; unrecaptured section 1250 gain is taxed at a maximum of 25 percent; net short-term gain is ordinary; the capital-loss deduction is limited to 3,000 dollars; and losses from selling personal-use property, including a home, are not deductible. Inherited property follows the Publication 544 holding-period exceptions. An individual's rates depend on filing facts, and the net investment income tax may apply (Topic 559, Form 8960)."),
    "irs_sched_d": ("IRS — Instructions for Schedule D (Form 1040)", "https://www.irs.gov/instructions/i1040sd", "Defines unrecaptured section 1250 gain for real property depreciated and held more than one year, and provides the line worksheet; it does not compute a private depreciation schedule."),
    "irs_1031_tips": ("IRS — Like-kind exchanges (real estate tax tips)", "https://www.irs.gov/businesses/small-businesses-self-employed/like-kind-exchanges-real-estate-tax-tips", "Section 1031 applies to real property held for business or investment; a primary residence and property held mainly for sale do not qualify; exchanges involve qualified-intermediary mechanics, deadlines, taxable boot and Form 8824 reporting."),
    "fed_great_recession": ("Federal Reserve History - The Great Recession (2007-2009)", "https://www.federalreservehistory.org/essays/great-recession-of-200709", "Read 2026-11-17: real GDP fell 4.3 percent from 2007Q4 to 2009Q2, unemployment went from 5 percent to 9.5 percent and then 10 percent, home prices fell about 30 percent from mid-2006 to mid-2009, the S&P 500 fell 57 percent from October 2007 to March 2009, household net worth fell from about 69 trillion to 55 trillion dollars, and the federal funds target went from 5.25 percent in September 2007 to 0 to 0.25 percent by December 2008. Historical record, not a forecast."),
    "bls_hist": ("BLS - historical CPI-U table", "https://www.bls.gov/cpi/tables/historical-cpi-u-201710.pdf", "Read 2026-11-17 (supplemental historical CPI-U table, Table 24): annual average percent change from the previous year - +17.4 (1917), +18.0 (1918), +15.6 (1920), -10.5 (1921), -6.1 (1922), -9.9 (1932), -5.1 (1933), +14.4 (1947), +10.9 (1942). Historical record; consult the current release for recent years."),
    "bls_latest": ("BLS - Consumer Price Index summary, October 2026", "https://www.bls.gov/news.release/cpi.nr0.htm", "Read 2026-11-17: CPI-U index level 337.511 for October 2026 and seasonally adjusted monthly changes; most 12-month changes could not be published because October 2025 survey data were not collected during the lapse in appropriations."),
    "fed_goal": ("Federal Reserve - inflation (PCE) explainer", "https://www.federalreserve.gov/economy-at-a-glance-inflation-pce.htm", "Read 2026-11-17: the Federal Reserve seeks inflation of 2 percent over the longer run as measured by the annual change in the PCE price index. A policy objective, not a forecast of any asset."),
    "ftb_fed_changes": ("FTB - summary of federal income tax changes", "https://www.ftb.ca.gov/about-ftb/data-reports-plans/Summary-of-Federal-Income-Tax-Changes/index.html", "Read 2026-11-17: California does not conform to federal rates and uses its own rates of 1 to 12.3 percent, plus an additional 1 percent on taxable income above 1,000,000 dollars, for a maximum personal rate of 13.3 percent."),
    "irs_8960": ("IRS - About Form 8960, net investment income tax", "https://www.irs.gov/forms-pubs/about-form-8960", "Read 2026-11-17: the form taxpayers use to figure the net investment income tax; the model's 3.8 percent drag is applied per the Form 8960 instructions, which must be read for the actual year."),
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
    ("pages/model-figures.html", "Model figures and provenance", "Private planning"),
    ("pages/property-tax.html", "Property-tax rules", "Law & process"),
    ("pages/inheritance-process.html", "Deadline timeline", "Law & process"),
    ("pages/estate-thresholds.html", "Estate-tax thresholds", "Law & process"),
    ("pages/law-watchlist.html", "Law watchlist", "Law & process"),
    ("pages/black-swan.html", "Black-swan conditions", "Stress tests"),
    ("pages/phased-investing.html", "Treasury staging tool", "Stress tests"),
    ("pages/economic-baselines.html", "Economic baselines", "Stress tests"),
    ("pages/investment-policy.html", "Investment policy draft", "Stress tests"),
    ("pages/attorney-cpa-brief.html", "Attorney & CPA brief", "Adviser & evidence"),
    ("pages/decision-log.html", "Decision log", "Adviser & evidence"),
    ("pages/flagged-for-review.html", "Flagged for review", "Adviser & evidence"),
    ("pages/glossary.html", "Glossary", "Adviser & evidence"),
    ("pages/sources.html", "Official source register", "Adviser & evidence"),
    ("pages/privacy.html", "Privacy & limits", "Adviser & evidence"),
]

STATUS = {"rule": "Verified rule", "historical": "Historical", "guidance": "Guidance", "missing": "Missing",
          "unverified": "Not verified", "assumption": "Assumption", "reference": "Official reference",
          "derived": "Derived in-model"}

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


def base_content_for(path: str) -> tuple[str, str, str]:
    """Return heading, lead, body for each public page; the framework text."""
    if path == "index.html":
        body = callout("What this site publishes, and what it never publishes", "The figures on this site are modelled results, built from case inputs that are rounded to the nearest ten dollars and carry no name, address, postal code, parcel identifier or locality. What is published is an arithmetic comparison of paths and the break-evens that decide them; the decision, the private records, and the unrounded figures stay in the family's own access-controlled file, and no projection here is presented as a forecast.", "warning")
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
        body += callout("Model first: a sale in the transfer tax year", "Model a sale in the inheritance tax year first, not as a tax-free assumption. Inherited basis is generally tied to date-of-death fair market value, but sale price, timing and allowable selling costs can differ from that value; a transfer-year sale does not automatically produce zero gain or loss. Verify the appraisal, amount realized and tax-year rules. Compare the after-tax proceeds with housing costs and reinvestment risk.", "info")
        body += table("Sale proceeds waterfall — the order in which a sale pays out", ["Layer", "Framework (amounts stay private)", "Rule or schedule source"], [
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
        body = callout("Privacy comes first", "This public site intentionally contains no property locality, address, parcel identifier, household amount, tax history, rent roll, policy detail, or household-specific recommendation. Use placeholders here and store private records outside the repository.", "warning")
        body += table("Privacy controls and limits", ["Control", "Current behavior", "Limitation"], [
            (["Public build inputs", "The generator contains only generic rules and public sources; no household data file is read." , "A public site cannot be used as a private case database."], STATUS["guidance"], ["irs_estate", "boe_prop19"]),
            (["Browser controls", "What-if calculations run in memory; the browser code makes no network requests or storage writes." , "Avoid entering sensitive details on a shared device; refresh to clear transient values."], STATUS["guidance"], ["treasury_bills", "sec_stocks"]),
            (["Current site", "Location and individual property figures are omitted." , "Anyone with repository access can read all tracked text and source files."], STATUS["guidance"], ["irs_basis"]),
            (["Earlier public copies", "A new build cannot remove old commits, forks, downloaded archives, cached pages or PR diffs." , "Treat anything previously public as potentially retained; admin-level remediation may be needed."], STATUS["missing"], ["github_sensitive"]),
        ])
        return "Privacy & limits", "Privacy is a design constraint, not a rounding promise.", body
    return "Not found", "", ""


# --------------------------------------------------------------------------
# quantified addenda: every figure below is produced by tools/case_model.py
# from rounded inputs (nearest ten dollars) and is regenerated at build time,
# so the page and the arithmetic cannot drift apart.
# --------------------------------------------------------------------------

BASE_YEAR = 2045
LONG_HORIZON = 30
BASE_SCENARIO = "steady"
SCENARIO_ORDER = ("steady", "sequence", "bust_at_transfer", "stagflation", "deflation")
TRANSFER_YEARS = (2040, 2045, 2050)


def _label(scenario: str) -> str:
    return str(cm.SCENARIOS[scenario]["label"])


def _n(value: float, zero_text: str = "none") -> str:
    """Money text from the model, ten-dollar-rounded, zero rendered as a word."""
    text = cm.usd(value)
    return zero_text if text == "none" else text


def _exact(value: float) -> str:
    """A published official amount, printed as published rather than rounded."""
    return f"${int(value):,}"


def _p(value: float, places: int = 2) -> str:
    return cm.pct(value, places)


def _bars(items: list[tuple[str, float]], unit: str = "") -> str:
    """A print-safe horizontal bar block built only from div widths."""
    top = max(abs(value) for _, value in items) or 1.0
    out = ['<div class="bars" role="img" aria-label="Comparison bar block">']
    for label, value in items:
        share = abs(value) / top * 100.0
        shown = f"{value:,.0f}" if unit == "raw" else _n(value)
        out.append(
            f'<div class="bar-row"><span class="bar-label">{esc(label)}</span>'
            f'<span class="bar-track"><span class="bar-fill" style="width: {share:.1f}%"></span></span>'
            f'<span class="bar-value">{esc(shown)}</span></div>'
        )
    out.append("</div>")
    return "".join(out)


def quantified(path: str) -> str:
    """Quantified sections appended to the framework pages."""
    headline = cm.headline(BASE_SCENARIO, BASE_YEAR, LONG_HORIZON)
    if path == "index.html":
        return _q_index(headline)
    if path.endswith("decision-analysis.html"):
        return _q_paths(headline)
    if path.endswith("projections.html"):
        return _q_projections()
    if path.endswith("property-tax.html"):
        return _q_property_tax()
    if path.endswith("operating-costs.html"):
        return _q_costs()
    if path.endswith("estate-thresholds.html"):
        return _q_estate()
    if path.endswith("black-swan.html"):
        return _q_black_swan()
    if path.endswith("phased-investing.html"):
        return _q_staging()
    if path.endswith("economic-baselines.html"):
        return _q_baselines()
    if path.endswith("model-figures.html"):
        return _q_figures()
    if path.endswith("attorney-cpa-brief.html"):
        return _q_brief(headline)
    if path.endswith("questions.html"):
        return _q_questions(headline)
    if path.endswith("suggestions.html"):
        return _q_suggestions(headline)
    if path.endswith("requirements-tracker.html"):
        return _q_requirements()
    if path.endswith("flagged-for-review.html"):
        return _q_flagged()
    if path.endswith("privacy.html"):
        return _q_privacy()
    if path.endswith("glossary.html"):
        return _q_glossary()
    if path.endswith("decision-log.html"):
        return _q_log()
    return ""


def _q_index(headline: dict) -> str:
    be = cm.break_evens(BASE_YEAR, LONG_HORIZON, BASE_SCENARIO)
    seq = cm.break_evens(BASE_YEAR, LONG_HORIZON, "sequence")
    body = callout(
        "How to read the figures on this site",
        "Every dollar figure is rounded to the nearest ten dollars, which is the owner's chosen "
        "de-identification step, and no name, address, postal code, parcel identifier or locality "
        "appears anywhere in the generated pages. The figures are modelled outcomes on stated "
        "assumptions, not appraisals, tax returns or forecasts: rows carry an evidence badge and a "
        "link to the official source for the rule behind them, and every unverified input is listed on "
        "the flagged-for-review page.",
        "warning",
    )
    body += table(
        "The answer moves when one of these six numbers moves",
        ["Fact that changes the ranking", "Modelled value at a 2045 transfer", "What it decides", "If it turns out different"],
        [
            ([
                "Occupancy: does the heir make Property A a principal residence within one year?",
                "Prop 19 partial carry-over holds the bill at " + _n(headline["bill_if_claimed"]) + " instead of "
                + _n(headline["bill_if_let"]) + " a year, a saving of " + _n(headline["prop19_saving"]),
                "Whether keeping the home is cheap enough to be a serious option at all",
                "If nobody occupies it, the reassessed bill applies from the next lien date and the ranking "
                "shifts toward selling",
             ], STATUS["rule"], ["ca_rtc63", "boe_prop19", "boe_lta"]),
            ([
                "Housing: does the household need a home, and would it live in this one?",
                "The housing a self-used owner gets is worth about " + _n(cm.market_rent(BASE_YEAR, BASE_SCENARIO)[1])
                + " a year at the top of the current listing band",
                "This is the largest single number in the comparison and it only exists in the live-in paths",
                "If the household will not live there, delete the imputed-rent credit and the keep paths lose "
                "most of their case",
             ], STATUS["assumption"], ["irs_121", "hud_fmr", "irs_rental"]),
            ([
                "Portfolio: what after-tax return do the sale proceeds earn?",
                "Holding beats selling only if the home appreciates faster than " + _p(be["needed_house_cagr"])
                + " a year in the flat baseline, or " + _p(seq["needed_house_cagr"]) + " a year on the block sequence",
                "The single hinge between sell now and keep for thirty years",
                "A one-percentage-point change in the assumed equity return moves the ranking; the scenario "
                "table on the compare-paths page shows the flip",
             ], STATUS["assumption"], ["sec_stocks", "cbo_long", "bls_cpi"]),
            ([
                "Rent: can the house be let for more than it costs?",
                "Break-even gross rent " + _n(be["needed_month_rent"]) + " a month in the flat baseline against a "
                + _n(be["quoted_month_rent"]) + " market indication; on the block sequence the break-even falls to "
                + _n(seq["needed_month_rent"]),
                "Whether the rental paths are a plan or a placeholder",
                "A written market-rent letter moves this from indication to evidence; until then the letting "
                "rows are a floor, not a forecast",
             ], STATUS["unverified"], ["irs_rental", "hud_fmr"]),
            ([
                "Estate: how far above the federal exclusion is the whole estate?",
                "The exclusion is " + _n(cm.FED_EXCL_2026) + " for 2026 deaths and " + _n(cm.FED_EXCL_2027)
                + " for 2027; both homes at today's values use " + _n(cm.A_MARKET_2026 + cm.B_MARKET_2026)
                + " of it",
                "Whether a liquidity plan and a Form 706 are needed before anything else is decided",
                "The cash figure is not supplied in this project at all, so estate exposure stays open and "
                "flagged; the filing test is estate-level, not heir-level",
             ], STATUS["rule"], ["irs_estate", "irs_estate_faq", "irs_2027"]),
            ([
                "Cost base: are insurance, maintenance and the capital plan real numbers?",
                "Modelled insurance " + _n(cm.midpoint(*cm.A_INSURANCE_YR)) + " and maintenance "
                + _n(cm.A_MARKET_2026 * cm.midpoint(*cm.MAINT_PCT_A)) + " a year, both flagged",
                "Whether the keep-and-let rows survive their own expense column",
                "Written quotes and three licensed bids replace both; the site marks them unverified until "
                "they exist",
             ], STATUS["missing"], ["cdi", "cslb"]),
        ],
    )
    body += table(
        "First screen: the model's headline, in 2026 dollars",
        ["Measure", "Flat baseline", "Block sequence", "Read this as"],
        [
            ([
                "Best-ranked path (30 years, same date, same horizon)",
                str(cm.path_table(BASE_YEAR, LONG_HORIZON, "steady")[0]["name"]),
                str(cm.path_table(BASE_YEAR, LONG_HORIZON, "sequence")[0]["name"]),
                "The winner is not stable across economic paths, so the household has to choose which world it "
                "is planning for, in writing, before the figures arrive",
             ], STATUS["assumption"], ["bls_cpi", "cbo_long", "sec_stocks"]),
            (["Wealth spread between the best and worst path",
              _n(headline["spread_real"]) + " real", _n(cm.path_table(BASE_YEAR, LONG_HORIZON, "sequence")[0]["terminal_real"] - cm.path_table(BASE_YEAR, LONG_HORIZON, "sequence")[-1]["terminal_real"]) + " real",
              "The cost of choosing badly, on these assumptions, in constant dollars"],
             STATUS["assumption"], ["cbo_long", "bls_cpi"]),
            (["Cost of the property tax alone if the exclusion is not available",
              _n(cm.a_state_at(BASE_YEAR, "steady", "rent")["tax"]) + " a year",
              _n(cm.a_state_at(BASE_YEAR, "sequence", "rent")["tax"]) + " a year",
              "Roughly a third of the gross rent a house of this value can command; it is the reason the "
              "letting rows are thin"],
             STATUS["rule"], ["ca_rtc63", "boe_prop19"]),
            (["Income tax on a sale inside the transfer year",
              _n(headline["income_tax_on_sale_now"]), _n(headline["income_tax_on_sale_now"]),
              "Selling on the date-of-death value leaves almost no gain, and a small loss after selling costs is "
              "not deductible on personal-use property: neither taxed nor deductible"],
             STATUS["rule"], ["irs_basis", "irs_topic409", "ftb_cap_gains"]),
        ],
    )
    body += prose(
        "What is deliberately not claimed",
        "Open items listed on the questions page are not gaps in the arithmetic: the model does not know the death year, the estate's cash balance, the appraised value, the leases, "
        "the insurance policy or the heir's tax bracket. Those are the open questions on the questions page, "
        "each with the number it would change and the document that supplies it.",
    )
    return body


def _q_paths(headline: dict) -> str:
    body = callout(
        "Same transfer date, same horizon, one cost and tax engine",
        "The seven paths below are priced at a " + str(BASE_YEAR) + " transfer with a " + str(LONG_HORIZON)
        + "-year horizon in five economic scenarios. Property B is already owned by the same person who "
        "inherits Property A and its ownership does not change in any path, so B is reported once, separately, "
        "instead of being repeated in every row.",
        "info",
    )
    rows = []
    for row in cm.path_table(BASE_YEAR, LONG_HORIZON, BASE_SCENARIO):
        rows.append(([
            str(row["rank"]), str(row["name"]), str(row["kind"]).capitalize(),
            _n(row["flow_cash"]) + " / " + _n(row["flow_econ"]),
            _n(row["proceeds"]), _n(row["liquidity"]),
            _n(row["terminal_econ"]), _n(row["terminal_real"]),
            str(row["driver"]),
        ], STATUS["assumption"], ["cbo_long", "irs_basis", "ftb_cap_gains", "ca_rtc63"]))
    body += table(
        "Flat baseline: wealth at " + str(BASE_YEAR + LONG_HORIZON) + ", in 2026 dollars",
        ["Rank", "Path", "Type", "Annual cash / economic flow", "Proceeds invested", "Liquid at transfer",
         "Nominal wealth", "Wealth in 2026 dollars", "Why it lands here"],
        rows,
    )
    body += _bars([(str(row["name"])[:56], float(row["terminal_real"]))
                   for row in cm.path_table(BASE_YEAR, LONG_HORIZON, BASE_SCENARIO)])
    body += prose(
        "How the flows are counted",
        "A self-used owned home is credited with the market rent a let property would net after vacancy and "
        "management, so living in a house you own is not counted as free and the live and let rows stay "
        "comparable. Portfolio income is never added as a flow - the after-tax return compounds inside the "
        "portfolio - so nothing is double counted. Income tax on rents is modelled as sheltered by "
        "depreciation, which is what makes the exit recapture a real cost of the letting rows.",
    )
    matrix = cm.rank_matrix(BASE_YEAR, LONG_HORIZON)
    names = [row["name"] for row in matrix["steady"]]
    rank_rows = []
    for name in names:
        cells = [name]
        for scenario in SCENARIO_ORDER:
            found = next(row for row in matrix[scenario] if row["name"] == name)
            cells.append(" #" + str(found["rank"]) + "  " + _n(float(found["terminal_real"])))
        spread = max(
            float(next(row for row in matrix[s] if row["name"] == name)["terminal_real"]) for s in SCENARIO_ORDER
        ) - min(float(next(row for row in matrix[s] if row["name"] == name)["terminal_real"]) for s in SCENARIO_ORDER)
        cells.append(_n(spread))
        rank_rows.append((cells, STATUS["assumption"], ["bls_cpi", "cbo_long", "fed_inflation", "fed_2008"]))
    body += table(
        "Does the ranking survive a different economic path? (wealth in 2026 dollars)",
        ["Path", _label("steady"), _label("sequence"), _label("bust_at_transfer"), _label("stagflation"),
         _label("deflation"), "Best minus worst"],
        rank_rows,
    )
    body += callout(
        "The honest reading of that table",
        "Two paths swap first place between the flat baseline and every scenario that contains a bust or high "
        "inflation. That is not a defect in the model; it is the answer to the question 'which plan is best' "
        "when the future is not one growth rate. The decision rule the household should write down is therefore "
        "a break-even, not a projection: keep the home if you believe it compounds above "
        + _p(headline["break_even_appreciation"]) + " a year after tax and you will actually live in it, and "
        "otherwise sell in the transfer year while the gain is still the size of a rounding error.",
        "warning",
    )
    horizons = cm.horizon_matrix(BASE_YEAR, BASE_SCENARIO)
    h_rows = []
    for horizon, hrows in horizons.items():
        best = hrows[0]
        sell = next(row for row in hrows if row["name"] == cm.PATHS[2][0])
        h_rows.append((
            [str(horizon) + " years", str(best["name"]), _n(float(best["terminal_real"])),
             _n(float(sell["terminal_real"])), _n(float(best["terminal_real"]) - float(sell["terminal_real"]))],
            STATUS["assumption"], ["cbo_long", "sec_stocks"],
        ))
    body += table("The same paths at different horizons (flat baseline, 2026 dollars)",
                  ["Horizon", "Best path", "Best", "Sell in transfer year", "Difference"], h_rows)
    t_rows = []
    for year, trows in cm.transfer_year_matrix(LONG_HORIZON, "sequence").items():
        best = trows[0]
        claim = cm.a_state_at(year, "sequence", "claim")
        rent_branch = cm.a_state_at(year, "sequence", "rent")
        t_rows.append((
            [str(year), _n(claim["value"]), _n(claim["allowance"]), _n(rent_branch["tax"]), _n(claim["tax"]),
             str(best["name"])[:52], _n(float(best["terminal_real"]))],
            STATUS["assumption"], ["boe_lta", "ca_rtc63", "bls_cpi"],
        ))
    body += table(
        "The transfer year is not a choice, so it is tested",
        ["Transfer year", "Modelled value", "Prop 19 allowance indexed to that year", "Bill if let",
         "Bill if claimed", "Best path on the block sequence", "Best path, 2026 dollars"],
        t_rows,
    )
    w_rows = []
    for row in cm.waterfall_rows(BASE_YEAR, BASE_SCENARIO):
        w_rows.append((
            [str(row["label"]), _n(row["price"]), "-" + _n(row["costs"]).lstrip("-"), _n(row["transfer_tax"]),
             _n(row["misc"]), _n(row["basis"]), _n(row["gross_gain"]), _n(row["exclusion"]),
             _n(row["income_tax"]), _n(row["net"])],
            STATUS["rule"], ["irs_121", "irs_topic409", "ca_rtc11911", "ca_gov27361", "ftb_cap_gains"],
        ))
    body += table(
        "Distribution of the sale proceeds, in the published order",
        ["Timing", "Price", "Selling costs", "Documentary transfer tax", "Recording and reports",
         "Basis (date-of-death value)", "Gain", "Main-home exclusion", "Income tax", "Net to invest"],
        w_rows,
    )
    first = cm.waterfall_rows(BASE_YEAR, BASE_SCENARIO)[0]
    body += _bars([
        ("Price", first["price"]),
        ("less selling costs", -first["costs"]),
        ("less transfer tax", -first["transfer_tax"]),
        ("less recording and reports", -first["misc"]),
        ("less income tax", -first["income_tax"]),
        ("Net to invest", first["net"]),
    ])
    body += prose(
        "What the distribution shows",
        "The income-tax line is the one most people expect to be large and it is the smallest: a sale inside "
        "the transfer year is priced against a basis set at the date of death, so the gain is the drift over a "
        "few months and the loss left after five percent selling costs is not deductible on personal-use "
        "property. Delay does not create a deduction either; it creates a taxable gain.",
    )
    be = cm.break_evens(BASE_YEAR, LONG_HORIZON, BASE_SCENARIO)
    seq = cm.break_evens(BASE_YEAR, LONG_HORIZON, "sequence")
    b = cm.b_reference(BASE_YEAR, BASE_SCENARIO)
    body += table(
        "Break-evens, which is the form this decision should be written in",
        ["Question", "Flat baseline", "Block sequence", "Status"],
        [
            (["Gross monthly rent that makes letting match selling", _n(be["needed_month_rent"]),
              _n(seq["needed_month_rent"]), "Listing indications run " + _n(cm.A_RENT_MONTH[0]) + " to "
              + _n(cm.A_RENT_MONTH[1]) + " a month; both are unverified"],
             STATUS["unverified"], ["irs_rental", "hud_fmr"]),
            (["Home appreciation needed to match selling and investing", _p(be["needed_house_cagr"]),
              _p(seq["needed_house_cagr"]), "Compare with any published index you are told to believe"],
             STATUS["assumption"], ["fhfa", "cbo_long"]),
            (["Same, but crediting the household's own housing", _p(be["needed_house_cagr_with_housing"]),
              _p(seq["needed_house_cagr_with_housing"]),
              "A negative number means living there wins even if values fall; that is the power of owning the "
              "home you would otherwise rent"],
             STATUS["assumption"], ["irs_121", "bls_cpi"]),
            (["Annual property-tax saving from a qualifying Proposition 19 claim", _n(be["tax_saving_from_claim"]),
              _n(seq["tax_saving_from_claim"]), "Requires the heir's principal-residence occupancy and a claim "
              "filed inside the statutory window"],
             STATUS["rule"], ["ca_rtc63", "boe_prop19", "boe_lta"]),
            (["Property B's year-one economics, identical in every path", _n(b["net_rental"]) + " net rental",
              _n(cm.b_reference(BASE_YEAR, "sequence")["net_rental"]) + " net rental",
              "Shown once so the ranking is not mistaken for the household's whole cash position; B's "
              "depreciation history and lawful-unit status are open items"],
             STATUS["unverified"], ["irs_rental", "ca_rent"]),
        ],
    )
    return body


def _q_projections() -> str:
    body = callout(
        "What these tables are",
        "They are arithmetic on the rounded owner-figure inputs, grown by the block sequence, so a reader can "
        "see how a value, an assessed value and a bill move together over time. They are not appraisals and not "
        "assessor records: the assessed-value line follows the two percent statutory adjustment that applies "
        "while no change in ownership is recorded.",
        "warning",
    )
    rows = []
    for row in cm.value_projection_rows("sequence", 25):
        rows.append((
            [str(int(row["year"])), _n(row["value"]), _n(row["assessed_capped"]), _p(row["share"], 0),
             _n(row["tax_capped"]), _n(row["allowance"]), _n(row["cap_line"]), _n(row["addition"]),
             _n(row["tax_claim"]), _n(row["tax_reassessed"]), _n(row["tax_saving"])],
            STATUS["assumption"], ["ca_rtc51", "ca_rtc63", "boe_lta"],
        ))
    body += table(
        "Property A: value, capped assessed value, and the bill under each transfer branch",
        ["Year", "Modelled value", "Assessed if no transfer event", "Assessed as a share of value",
         "Bill with no transfer", "Prop 19 allowance indexed", "Value cap line (assessed + allowance)",
         "Addition above the cap", "Bill with a qualifying claim", "Bill if reassessed", "Claim saves"],
        rows,
    )
    body += prose(
        "The one line most plans miss",
        "The Proposition 19 allowance is added to the existing taxable value, not substituted for it, so a "
        "home worth far more than the capped base does not carry its historic bill forward untouched: the "
        "excess over the cap is added, and the bill settles between the capped number and the fully reassessed "
        "one. The allowance itself is re-indexed every other February by the California house-price index, so "
        "a plan built on today's figure understates the benefit in a later transfer year.",
    )
    cost_rows = []
    for row in cm.operating_cost_rows("sequence", 25)[::2]:
        cost_rows.append((
            [str(int(row["year"])), _n(row["a_value"]), _n(row["a_tax"]), _n(row["a_water"]),
             _n(row["a_power"]), _n(row["a_insurance"]), _n(row["a_maintenance"]), _n(row["a_total"]),
             _n(row["b_tax"]), _n(row["b_water"]), _n(row["b_power"]), _n(row["b_insurance"]),
             _n(row["b_rent"]), _n(row["b_net"])],
            STATUS["assumption"], ["cpuc_solar", "water_board", "cdi", "cslb", "irs_rental"],
        ))
    body += table(
        "Both buildings: recurring cost by year, grown with the sequence's own price path",
        ["Year", "A value", "A tax", "A water", "A electric (solar credit)", "A insurance", "A maintenance",
         "A total", "B tax", "B water", "B electric", "B insurance", "B gross rent", "B net after costs"],
        cost_rows,
    )
    body += callout(
        "Why Property B's tax line looks impossible",
        "Its assessed value is a small fraction of its market value because the assessed base is capped and the "
        "building has not changed hands. That is the same mechanism Property A has, and it is the asset the "
        "household would destroy by triggering a change in ownership without a qualifying exclusion. It is also "
        "why any plan that transfers B, or adds an owner to its title, needs its own analysis before it is "
        "signed.",
        "info",
    )
    plan = cm.capital_plan()
    plan_rows = []
    for item, why, evidence, low, high in plan:
        plan_rows.append(([item, why, evidence, _n(low), _n(high)], STATUS["assumption"], ["cslb", "cdi"]))
    body += table(
        "Five-year capital plan skeleton for both buildings",
        ["Item", "Why it is on the list", "Evidence that sizes it", "Low", "High"],
        plan_rows,
    )
    a_low, a_high = cm.capital_plan_total("A")
    b_low, b_high = cm.capital_plan_total("B")
    body += table(
        "Capital plan totals over five years",
        ["Building", "Five-year low", "Five-year high", "Per year on the high case"],
        [
            (["Property A, inherited", _n(a_low), _n(a_high), _n(a_high / 5)], STATUS["assumption"], ["cslb"]),
            (["Property B, already owned", _n(b_low), _n(b_high), _n(b_high / 5)], STATUS["assumption"], ["cslb"]),
            (["Both, per year, added to the operating costs above", _n((a_high + b_high) / 5),
              _n((a_high + b_high) / 5), _n((a_high + b_high) / 5)],
             STATUS["assumption"], ["cslb", "cdi"]),
        ],
    )
    return body


def _q_property_tax() -> str:
    body = callout(
        "Worked example of the exclusion arithmetic, on rounded figures",
        "A home whose capped taxable value is " + _n(cm.A_ASSESSED_2026) + " and whose value at transfer is "
        "modelled at " + _n(cm.a_state_at(BASE_YEAR, "steady", "keep")["value"]) + " cannot carry its whole base "
        "forward: the cap is the prior taxable value plus the indexed allowance, and everything above it is "
        "added back. The saving is real, and it is smaller than most summaries imply.",
        "info",
    )
    rows = []
    for year in TRANSFER_YEARS:
        for scenario in ("steady", "sequence"):
            claim = cm.a_state_at(year, scenario, "claim")
            rent_branch = cm.a_state_at(year, scenario, "rent")
            keep = cm.a_state_at(year, scenario, "keep")
            rows.append((
                [str(year), _label(scenario), _n(claim["value"]), _n(claim["prior_taxable"]),
                 _n(claim["allowance"]), _n(claim["cap"]), "yes" if claim["cap_met"] else "no",
                 _n(claim["addition"]), _n(keep["tax"]), _n(claim["tax"]), _n(rent_branch["tax"]),
                 _n(rent_branch["tax"] - claim["tax"])],
                STATUS["rule"], ["ca_rtc63", "boe_lta", "ca_rtc51", "boe_prop19"],
            ))
    body += table(
        "Transfer-year arithmetic: capped base, indexed allowance, addition, and the three bills",
        ["Transfer year", "Scenario", "Value at transfer", "Prior taxable value", "Indexed allowance",
         "Cap line", "Cap met?", "Addition", "Bill if no transfer event", "Bill with a qualifying claim",
         "Bill if reassessed", "Claim saves a year"],
        rows,
    )
    rows = []
    for year, amount in ((2021, cm.PROP19_ALLOWANCE_2021), (2023, cm.PROP19_ALLOWANCE_2023), (2025, cm.PROP19_ALLOWANCE)):
        rows.append(([f"16 February {year} transfer window", _exact(amount),
                     "Published by the BOE under the biennial adjustment in section 2.1(c)(4) of article XIII A; "
                     "the next adjustment is due in February 2027"],
                    STATUS["rule"], ["boe_lta"]))
    for year in (2040, 2045, 2050):
        rows.append(([f"Modelled {year} window", _n(cm.prop19_allowance(year)),
                      "Projected forward at an assumed California house-price rate; an assumption, not a "
                      "published figure, and it moves the bill in the table above"],
                     STATUS["assumption"], ["boe_lta", "fhfa"]))
    body += table("Carrying the allowance forward instead of freezing it",
                  ["Window", "Allowance used in the model", "Basis"], rows)
    rows = [
        (["Effective levy on the capped base, Property A", _p(cm.A_RATE),
          "Arithmetic on the owner's rounded 2025 bill and assessed value; the constitutional limit is one "
          "percent of taxable value, and voter-approved and district measures sit on top of it, so the parcel's "
          "published tax-rate-area schedule must confirm the total"],
         STATUS["unverified"], ["ca_rtc51", "boe_counties"]),
        (["Effective levy, Property B", _p(cm.B_RATE),
          "Same derivation from the owner's rounded 2025 pair; the higher share is why the transfer tax and any "
          "later change of ownership on that building deserve their own review"],
         STATUS["unverified"], ["ca_rtc51", "boe_counties"]),
        (["Assessed value as a share of market value, Property A", _p(cm.A_ASSESSED_SHARE_OF_MARKET, 0),
          "The Prop 13 base is the whole reason holding an inherited Bay Area home can beat selling one"],
         STATUS["derived"], ["ca_rtc51"]),
        (["Documentary transfer tax ceiling on a residential sale", _p(cm.DTT_COUNTY_MAX + cm.DTT_CITY_MAX),
          "State law caps the county levy at fifty-five cents for each five hundred dollars of consideration and "
          "lets a city add one-half of that; whether a given county or city has adopted anything, and at what "
          "rate, has to be read from that jurisdiction's ordinance"],
         STATUS["rule"], ["ca_rtc11911"]),
    ]
    body += table("Rates the model uses, and what each one still needs",
                  ["Rate", "Value", "What is verified and what is not"], rows)
    body += table(
        "Deadlines that decide the property-tax outcome",
        ["Trigger", "Period", "Consequence if missed", "Source read"],
        [
            (["Home becomes the heir's principal residence", "within one year of the transfer",
              "The family-home exclusion is unavailable and the taxable value becomes the full value",
              "Section 63.2(a)(1)(A) as read on 2026-11-17"],
             STATUS["rule"], ["ca_rtc63"]),
            (["Homeowners' exemption claim", "within one year of the transfer",
              "The exclusion is removed; the base is re-enrolled factored forward from the year eligibility ends",
              "Section 63.2(a)(1)(B) and (C)"],
             STATUS["rule"], ["ca_rtc63", "ca_rtc218"]),
            (["Claim for the exclusion", "within three years, or before a transfer to a third party or the end "
              "of occupancy, whichever comes first", "Late claims are considered only from the lien date of the "
              "year filed, and the county may charge a processing fee capped at 175 dollars",
              "Section 63.2(f) and (g)"],
             STATUS["rule"], ["ca_rtc63", "ca_rtc27388"]),
            (["Assessor notice of potential eligibility", "45 days from the notice, then a second notice with 60 "
              "days", "Reassessment proceeds and the fee provision can apply", "Section 63.2(g)"],
             STATUS["rule"], ["ca_rtc63"]),
            (["Change-in-ownership statement on a death transfer", "as provided for the specified death "
              "transfers", "Assessor records lag and the exclusion review starts late", "Section 480"],
             STATUS["rule"], ["ca_rtc480"]),
        ],
    )
    body += callout(
        "Enacted, not proposed",
        "Section 63.2 as read on 2026-11-17 carries an amendment effective 1 January 2026 that extends claim "
        "timing for properties reassessed after the January 2025 emergency fires. That is an enacted change and "
        "it is dated; it does not generalise to other properties or to future years, and the watchlist page "
        "keeps proposals separate from this.",
        "info",
    )
    return body


def _q_costs() -> str:
    rows = []
    for label, now, driver in (
        ("Water, Property A", cm.midpoint(*cm.A_WATER_MONTH) * 12, "owner-figure monthly range, grown with prices"),
        ("Electric, Property A (credit while owner-occupied)", -cm.midpoint(*cm.A_SOLAR_CREDIT_MONTH) * 12,
         "the array nets a credit rather than a bill today; the export tariff is the risk in that line"),
        ("Insurance, Property A", cm.midpoint(*cm.A_INSURANCE_YR),
         "assumption band used because no quote is on file; the owner's estimate of "
         + _n(cm.A_INSURANCE_GUESS_YR) + " is carried on the flagged page"),
        ("Maintenance, Property A", cm.A_MARKET_2026 * cm.midpoint(*cm.MAINT_PCT_A),
         "midpoint of an assumption band of " + _p(cm.MAINT_PCT_A[0], 2) + " to "
         + _p(cm.MAINT_PCT_A[1], 2) + " of value a year"),
        ("Water, Property B", cm.midpoint(*cm.B_WATER_MONTH) * 12, "whole three-unit building, owner-paid"),
        ("Electric, Property B", cm.midpoint(*cm.B_POWER_MONTH) * 12, "common area only, owner-paid"),
        ("Insurance, Property B", cm.midpoint(*cm.B_INSURANCE_YR), "assumption band for a three-unit let building"),
        ("Maintenance, Property B", cm.B_MARKET_2026 * cm.MAINT_PCT_B[1] * 0.75,
         "older let building; the band runs " + _p(cm.MAINT_PCT_B[0], 1) + " to "
         + _p(cm.MAINT_PCT_B[1], 1) + " of value"),
    ):
        rows.append(([label, _n(now) + " a year", _n(now / 12) + " a month", driver],
                     STATUS["assumption"], ["cdi", "cslb", "cpuc_solar", "water_board"]))
    body = table("Year-one cost lines used by every path", ["Line", "Per year", "Per month", "Basis"], rows)
    body += callout(
        "The insurance line is the one to fix first",
        "Premiums follow the dwelling-coverage limit, and the limit has to follow rebuilding cost, not market "
        "value or an estimate taken from a typical house. An owner estimate of " + _n(cm.A_INSURANCE_GUESS_YR)
        + " a year is plausible for an average home in this state and is not a number to plan a high-value "
        "house on: two written quotes with the declarations page attached replace it, and the model reruns. "
        "Nothing in this project claims to know a carrier's rate.",
        "warning",
    )
    rows = []
    for row in cm.operating_cost_rows("sequence", 25)[:25:4]:
        year = int(row["year"])
        rows.append((
            [str(year), _n(row["a_tax"] + row["a_water"] + row["a_power"] + row["a_insurance"] + row["a_maintenance"]),
             _n(row["b_tax"] + row["b_water"] + row["b_power"] + row["b_insurance"] + row["b_maintenance"]),
             _n(row["b_rent"]), _n(row["b_net"])],
            STATUS["assumption"], ["cdi", "cslb", "cpuc_solar", "water_board"],
        ))
    body += table("Cost growth on the block sequence, four-year steps",
                  ["Year", "Property A total", "Property B total", "B gross rent", "B net after its costs"], rows)
    body += prose(
        "Why the utility lines are not footnotes",
        "A house whose electric bill is a credit is worth a few hundred dollars a year more than the same house "
        "without the array, and a building where the owner pays water for three units is worth about five "
        "thousand dollars a year less than one where tenants pay it. Both lines are contractual and local: the "
        "export tariff terms for the array, the sewer and storm-water charges, and the tenant-reimbursement "
        "arrangements have to be read from the bills and the leases, not from a model.",
    )
    return body


def _q_estate() -> str:
    body = callout(
        "The filing test is estate-level, and the cash number is missing",
        "Nothing in this project states the size of the estate's financial assets, so no estate tax is computed "
        "here. What can be done from official rules is to show where the line sits, how it indexes, how much of "
        "it the two homes already occupy, and what a given excess would cost at the top rate.",
        "warning",
    )
    rows = [
        (["2025 death", _n(cm.FED_EXCL_2025), "Published IRS filing threshold for the year of death",
          "Test: gross estate plus adjusted taxable gifts plus the specific gift tax exemption"],
         STATUS["rule"], ["irs_estate", "irs_estate_faq"]),
        (["2026 death", _n(cm.FED_EXCL_2026), "Published filing threshold; the statute was amended to this "
          "amount for calendar year 2026 gifts as well", "Same test"],
         STATUS["rule"], ["irs_estate", "irs_estate_faq"]),
        (["2027 death", _n(cm.FED_EXCL_2027), "Published in the IRS inflation adjustments for 2027",
          "Indexing continues after 2027, which is why a 2040-2050 plan must not freeze this number"],
         STATUS["rule"], ["irs_2027"]),
        (["Annual gift exclusion, 2026 and 2027", _n(cm.GIFT_EXCL_2026) + " then " + _n(cm.GIFT_EXCL_2027),
          "Gifts above the annual exclusion consume the same lifetime amount", "Prior taxable gifts reduce the "
          "exclusion available at death, so the gift history is a decision input, not trivia"],
         STATUS["rule"], ["irs_2027", "irs_estate_faq"]),
        (["California estate or inheritance tax", _n(cm.SF_STATE_TAX),
          "California imposes no estate tax of its own for deaths on or after 1 January 2005",
          "The state line is zero by rule; the state's income-tax treatment of a later sale is not"],
         STATUS["rule"], ["ca_sco", "ca_rtc13301"]),
    ]
    body += table("Where the federal line sits, and what indexes it", ["Item", "Amount", "Source basis", "Why it matters here"], rows)
    rows = []
    for year in TRANSFER_YEARS:
        for row in cm.estate_rows(year)[:2]:
            rows.append((
                [str(year), _n(row["homes"]), _n(row["other"]), _n(row["gross"]), _n(row["exclusion"]),
                 _n(row["cash_before_filing"]), _n(row["excess"]), _n(row["tax_on_excess"])],
                STATUS["assumption"], ["irs_estate", "irs_2027", "bls_cpi"],
            ))
    body += table(
        "Headroom before the filing test is met, with the homes grown to the modelled transfer year",
        ["Death year modelled", "Both homes", "Other assets in the estate", "Gross estate", "Indexed exclusion",
         "Room left for everything else", "Amount above the exclusion", "Modelled tax on that excess"],
        rows,
    )
    rows = []
    for extra_assets in (0, 5_000_000, 10_000_000, 20_000_000, 30_000_000):
        row = cm.estate_rows(2045)
        base = cm.estate_projection(2045, cm.A_MARKET_2026 + cm.B_MARKET_2026)
        total = base["homes"] + extra_assets
        excess = max(0.0, total - base["exclusion"])
        rows.append((
            [_n(extra_assets), _n(total), _n(base["exclusion"]), "yes" if excess else "no",
             _n(excess), _n(excess * cm.ESTATE_TOP_RATE),
             "no return required on these facts" if not excess else "Form 706 required"],
            STATUS["assumption"] if abs(cm.ESTATE_TOP_RATE - 0.40) < 1e-9 else STATUS["unverified"],
            ["irs_estate", "irs_estate_faq"],
        ))
    body += table(
        "Sensitivity: the same estate with different amounts of cash and securities",
        ["Non-home assets", "Gross estate", "Exclusion in the modelled year", "Above the line?", "Excess",
         "Tax on the excess at the top rate", "Filing note"],
        rows,
    )
    body += prose(
        "Three things to ask before the money arrives",
        "Portability: a deceased spousal unused exclusion can double the amount available, but only if a Form 706 "
        "was filed for the first death, whether or not it was otherwise required, and the relief for missing that "
        "deadline is limited. Prior taxable gifts: gifts since 1976 are added back when the tax is computed, so a "
        "gift history changes the answer at death. Liquidity: tax is paid in cash, and an estate whose wealth is "
        "two houses and a brokerage account needs the plan written before it is needed. Each of these is a "
        "document request, not an opinion.",
    )
    body += table(
        "Dates that bind the estate side",
        ["Event", "Deadline", "Authority read on 2026-11-17"],
        [
            (["Form 706 due", "nine months after the date of death",
              "IRS estate-tax FAQs; a six-month extension is available by filing Form 4768 on or before the due date"],
             STATUS["rule"], ["irs_estate_faq", "irs_706"]),
            (["Portability election", "only on a timely filed return for the first estate",
              "Rev. Proc. 2022-32 allows a late portability-only filing within five years for estates under the "
              "filing threshold, and no relief for estates that were required to file"],
             STATUS["rule"], ["irs_estate_faq"]),
            (["Trustee notice to heirs after a trust becomes irrevocable", "as specified in the Probate Code",
              "State law sets the notice and the contest window; the trust instrument can shorten practical "
              "timelines"],
             STATUS["rule"], ["ca_prob"]),
            (["California inheritance tax", "not applicable",
              "No state estate or inheritance tax for deaths on or after 1 January 2005"],
             STATUS["rule"], ["ca_sco", "ca_rtc13301"]),
        ],
    )
    return body


def _q_black_swan() -> str:
    rows = []
    for row in cm.BLOCKS:
        years, name, house, infl, rent, equity, bills = row
        rows.append((
            [str(years) + " years", name.title(), _p(house, 1), _p(infl, 1), _p(rent, 1), _p(equity, 1), _p(bills, 1),
             "A planning block, assembled from the documented episodes named on the economic-baselines page; "
             "it is not a forecast of any decade"],
            STATUS["assumption"], ["bls_hist", "fed_inflation", "fed_1929", "fed_great_recession", "fhfa"],
        ))
    body = table("The block path used by the tables on this site",
                 ["Length", "Block", "Home values", "Prices", "Rents", "Equities", "Bills", "Standing"], rows)
    avg = cm.block_average()
    body += table(
        "Why one average is not a projection",
        ["Series", "Arithmetic mean of the blocks", "Compounded (geometric) mean", "Effect of the difference over 30 years"],
        [
            (["Home values", _p(avg["house_arith"]), _p(avg["house"]),
              "A " + _n(1_000_000) + " home ends at " + _n(1_000_000 * (1 + avg["house"]) ** 30)
              + " instead of " + _n(1_000_000 * (1 + avg["house_arith"]) ** 30)],
             STATUS["assumption"], ["fhfa", "bls_cpi"]),
            (["Equities", _p(avg["equity_arith"]), _p(avg["equity"]),
              "The block path contains a 57 percent fall, which costs more of the compounding than the recovery "
              "years win back"],
             STATUS["assumption"], ["fed_1929", "fed_2008", "sec_stocks"]),
            (["Bills", _p(avg["bills_arith"]), _p(avg["bills"]),
              "Small, which is exactly why the waiting leg of a staged plan is a timing tool and not a return"],
             STATUS["assumption"], ["treasury_bills", "treasury_notes"]),
        ],
    )
    flat_start = 1_000_000
    seq_value, flat_value = cm.sequence_vs_flat(flat_start, 30, avg["house"])
    body += callout(
        "The same average, two different outcomes",
        "One million dollars of value grown at the block path ends at " + _n(seq_value) + " after thirty years, "
        "against " + _n(flat_value) + " on a flat " + _p(avg["house_arith"]) + " a year, even though the blocks "
        "average to that number. Any fifty-year projection built on a single rate is therefore not a forecast of "
        "this household's asset - it is a rounding of the risk away.",
        "warning",
    )
    rows = []
    for scenario in SCENARIO_ORDER:
        table_rows = cm.path_table(BASE_YEAR, LONG_HORIZON, scenario)
        best = table_rows[0]
        sell = next(row for row in table_rows if row["name"] == cm.PATHS[2][0])
        rates = cm.scenario_rates(scenario, 30)
        rows.append((
            [_label(scenario), _p(sum(rates["house"]) / 30, 1), _p(sum(rates["infl"]) / 30, 1),
             _p(sum(rates["equity"]) / 30, 1), str(best["name"])[:58], _n(float(best["terminal_real"])),
             _n(float(sell["terminal_real"])),
             _n(float(best["terminal_real"]) - float(sell["terminal_real"]))],
            STATUS["assumption"], ["bls_cpi", "cbo_long", "fed_inflation", "fed_depression"],
        ))
    body += table(
        "Which world the household is planning for decides which path wins (2026 dollars)",
        ["Scenario", "Home growth", "Prices", "Equities", "Best path", "Best", "Sell in transfer year", "Gap"],
        rows,
    )
    body += prose(
        "How this is meant to be used",
        "Not as a probability. Each row is the same seven paths in a different economic world, priced with the "
        "same costs and the same tax rules. Where the winner changes, the household's job is to decide which "
        "world it can live with being wrong about, and to write that down before the appraisal and the tax "
        "figures arrive. Where the winner does not change, the decision is safe to make now.",
    )
    rows = []
    for row in cm.staging_table(cm.headline()["net_sale_proceeds"], "2008"):
        rows.append((
            ["shock in month " + str(int(row["shock_month"])), _n(row["immediate"]), _n(row["staged"]),
             _n(row["difference"]), _p(row["share_exposed"], 0), _n(row["bills_income"]),
             "Staging limits the money exposed to a crash inside the buying window and does nothing for one "
             "that arrives after it"],
            STATUS["assumption"], ["fed_great_recession", "treasury_bills", "sec_stocks"],
        ))
    body += table(
        "Crash-entry test on the modelled net proceeds, 2007-09 shape (one-shot 57 percent fall)",
        ["Shock timing", "Invested at once", "Staged over 30 months", "Staging minus immediate",
         "Share of the money already invested at the shock", "Interest earned while waiting", "Reading"],
        rows,
    )
    rows = []
    for row in cm.staging_table(cm.headline()["net_sale_proceeds"], "1929"):
        rows.append((
            ["shock in month " + str(int(row["shock_month"])), _n(row["immediate"]), _n(row["staged"]),
             _n(row["difference"]), _p(row["share_exposed"], 0),
             "The 1929 anchor is the hard case: the index level did not return to its 1929 high for roughly "
             "twenty-five years, so a plan that waits for the crash to end before buying at all can end up "
             "buying at a level already far above the trough"],
            STATUS["historical"], ["fed_1929", "fed_depression", "treasury_bills"],
        ))
    body += table(
        "Same test on the 1929-32 shape (one-shot 89 percent fall, ten-year horizon)",
        ["Shock timing", "Invested at once", "Staged over 30 months", "Staging minus immediate",
         "Share invested at the shock", "Reading"],
        rows,
    )
    return body


def _q_staging() -> str:
    proceeds = cm.headline()["net_sale_proceeds"]
    body = callout(
        "What the staging path is, in numbers",
        "Park the net proceeds of a sale in a ladder of three-month to two-year Treasury maturities for 24 to 36 "
        "months after the transfer, then move into equities in equal tranches - twelve quarterly steps in the "
        "model. The point is not to beat the market; it is to stop a single decision date from deciding the next "
        "thirty years, and to pay for that insurance in a measurable way.",
        "info",
    )
    rows = []
    for window in (24, 30, 36):
        for anchor in ("2008", "1929"):
            for row in cm.staging_table(proceeds, anchor, window):
                if int(row["shock_month"]) in (0, window, window + 6):
                    rows.append((
                        [str(window) + " months", anchor, "month " + str(int(row["shock_month"])),
                         _n(row["immediate"]), _n(row["staged"]), _n(row["difference"]),
                         _p(row["share_exposed"], 0), _n(row["bills_income"])],
                        STATUS["assumption"], ["treasury_bills", "treasury_notes", "fed_1929", "fed_great_recession"],
                    ))
    body += table(
        "Staging window against crash timing, on the modelled net proceeds of " + _n(proceeds),
        ["Window", "Historical shape", "Shock lands", "Invested at once", "Staged", "Staged minus at-once",
         "Exposed at the shock", "Bills income while waiting"],
        rows,
    )
    body += callout(
        "Reinvestment risk, next to the headline",
        "Staging is not free. In a market that keeps rising the un-deployed money buys in higher: "
        "the model's own arithmetic gives "
        + _n(cm.reinvestment_risk(proceeds, 30, cm.CRASH_ANCHORS["2008"]["bills"], cm.CRASH_ANCHORS["2008"]["drift"])["price_increase"])
        + " of price increase on the waiting money over the 30-month window at a 10 percent drift, and the "
        "waiting leg earns " + _n(cm.reinvestment_risk(proceeds, 30, cm.CRASH_ANCHORS["2008"]["bills"],
                                                       cm.CRASH_ANCHORS["2008"]["drift"])["bills_income"])
        + " in bills over the same span. In a crisis the safe leg earns close to nothing, because the rates on "
        "bills are cut in the same weeks the shares fall: the federal funds target went from 5.25 percent in "
        "September 2007 to 0 to 0.25 percent by December 2008, which is the reason a 2008-shaped crash is the "
        "best case for waiting and the worst case for the yield earned while waiting.",
        "warning",
    )
    rows = []
    for months in (0, 12, 24, 30, 36, 48):
        risk = cm.reinvestment_risk(proceeds, months, 0.035, 0.070)
        rows.append((
            [str(months) + " months", _n(risk["bills_income"], "zero"), _n(risk["price_increase"], "zero"),
             _n(risk["give_up_annual"]), _n(risk["ten_year_gap"]),
             "cost of waiting measured against the same proceeds invested at once, before tax"],
            STATUS["assumption"], ["treasury_bills", "sec_stocks", "cbo_outlook"],
        ))
    body += table("What the waiting costs when nothing goes wrong",
                  ["Waiting window", "Earned in bills", "Price bought over", "Annual give-up",
                   "Gap after ten years", "Basis"], rows)
    rows = []
    staged_path = next(row for row in cm.path_table(BASE_YEAR, LONG_HORIZON, BASE_SCENARIO)
                       if row["name"] == cm.PATHS[3][0])
    plain_path = next(row for row in cm.path_table(BASE_YEAR, LONG_HORIZON, BASE_SCENARIO)
                      if row["name"] == cm.PATHS[2][0])
    rows.append(([
        "Sell and stage (30-month window, twelve tranches)", _n(plain_path["terminal_real"]),
        _n(staged_path["terminal_real"]), _n(float(staged_path["terminal_real"]) - float(plain_path["terminal_real"])),
        "Both rows sell the house on the same date with the same costs; only the deployment schedule differs",
    ], STATUS["assumption"], ["treasury_bills", "sec_stocks"]))
    body += table("Staging inside the thirty-year comparison, flat baseline",
                  ["Path", "Immediate deployment", "Staged deployment", "Cost of staging", "Note"], rows)
    body += prose(
        "The decision rule this supports",
        "Write the rule before the money exists: stage for a fixed window, buy on a fixed schedule, and do not "
        "extend the window because the market looks about to fall. A staging plan that is allowed to grow is a "
        "market-timing plan wearing a policy document, and the two rows above show what the discipline costs "
        "when nothing happens.",
    )
    body += prose(
        "Mechanics worth fixing in advance",
        "Bills are bought at auction through TreasuryDirect in denominations the site states, maturities run "
        "four, eight, thirteen, seventeen and twenty-six weeks for bills and two to ten years for notes, and "
        "interest on both is taxable federally and exempt from California income tax. A two-year note held to "
        "maturity returns par; sold early it can return less. None of that is a household fact and none of it "
        "needs to be guessed - it is read from the Treasury pages at the day of purchase.",
    )
    return body


def _q_baselines() -> str:
    body = callout(
        "Why this page exists",
        "A fifty-year plan is not one number repeated fifty times. Prices have moved by more than ten percent in "
        "a year and by less than minus ten percent in another, home values have fallen by a fifth over fourteen "
        "quarters, and equity indexes have taken twenty-five years to return to a previous high. The rows below "
        "are the documented record; the block path used by the model is assembled from shapes like these, and it "
        "is a planning device, not a forecast.",
        "warning",
    )
    rows = [
        (["1917, 1918", "+17.4 percent, +18.0 percent", "Annual average CPI-U percent change",
          "Wartime price surge; the fastest annual averages in the published series"],
         STATUS["historical"], ["bls_hist"]),
        (["1920, 1921, 1922", "+15.6, -10.5 (annual average; -10.8 on the December-to-December measure), -6.1 percent", "Annual average CPI-U percent change",
          "A one-year swing of more than twenty-five points between two adjacent years"],
         STATUS["historical"], ["bls_hist", "fed_depression"]),
        (["1964 to 1980", "about 1 percent, then more than 14 percent", "Federal Reserve history of the period",
          "The Great Inflation ran from 1965 to 1982, with four recessions and two energy shortages inside it"],
         STATUS["historical"], ["fed_inflation"]),
        (["1970, 1994, 1995, 1996", "+5.7, +2.6, +2.8, +3.0 percent", "Annual average CPI-U percent change",
          "Long stretches of low-single-digit change, which is what a single-rate projection quietly assumes"],
         STATUS["historical"], ["bls_hist"]),
        (["3 September 1929 to 8 July 1932", "381.17 to 41.22, a fall of 89 percent", "Dow Jones Industrial Average closes",
          "The index did not return to the 1929 level until 23 November 1954"],
         STATUS["historical"], ["fed_1929"]),
        (["December 2007 to June 2009", "real GDP -4.3 percent; unemployment 5 percent to 10 percent",
          "Federal Reserve history of the recession", "Longest recession since the Second World War, as of that writing"],
         STATUS["historical"], ["fed_great_recession"]),
        (["October 2007 to March 2009", "S&P 500 -57 percent", "Federal Reserve history of the recession",
          "Household net worth fell from about 69 trillion to 55 trillion dollars over the same span"],
         STATUS["historical"], ["fed_great_recession"]),
        (["Mid-2006 to mid-2009", "home prices -30 percent on average nationally", "Federal Reserve history",
          "The 2007 first quarter to 2011 second quarter decline measured on the FHFA index was over a fifth"],
         STATUS["historical"], ["fed_great_recession", "fhfa"]),
        (["Calendar 2024, California", "+2.15 percent house-price change", "FHFA House Price Index, as published by the BOE",
          "This is the number that re-indexes the Proposition 19 allowance every other February"],
         STATUS["rule"], ["boe_lta", "fhfa"]),
        (["October 2026", "CPI-U index 337.511; monthly change +0.4 percent seasonally adjusted",
          "BLS release read on 2026-11-17", "The release could not publish most twelve-month changes because "
          "October 2025 survey data were not collected during the lapse in appropriations"],
         STATUS["reference"], ["bls_latest"]),
        (["Longer-run policy anchor", "2 percent, measured by the annual change in the PCE price index",
          "Federal Reserve statement on longer-run goals", "The central bank's own target is a rate, not a "
          "ceiling or a floor for the next fifty years"],
         STATUS["rule"], ["fed_goal"]),
    ]
    body += table("Documented variability, with the source beside each row",
                  ["Period", "What happened", "Measure", "Why it belongs in a fifty-year plan"], rows)
    body += table(
        "Housing-specific history that a Bay Area projection has to survive",
        ["Observation", "Figure", "Reading"],
        [
            (["National home prices doubled over the run-up", "1998 to 2006", "The sharpest increase recorded in "
              "US history at the time of that writing, in an episode that ended in a thirty percent fall"],
             STATUS["historical"], ["fed_great_recession"]),
            (["Household mortgage debt as a share of GDP", "61 percent in 1998 to 97 percent in 2006",
              "Leverage, not prices, is what turned a decline into a crisis; a household with no mortgage on the "
              "inherited home is in a different position from the market average"],
             STATUS["historical"], ["fed_great_recession"]),
            (["Slow recoveries after a bust", "real GDP only 4.5 percent above its previous peak by 2013, "
              "unemployment 7.3 percent", "A 'recovery' headline can coexist with a portfolio that has barely "
              "regained its old level for six years"],
             STATUS["historical"], ["fed_great_recession"]),
            (["State-level growth in the allowance year used by the model", _p(0.0215),
              "Used to carry the Proposition 19 allowance forward; a repeat of a boom decade would raise it, "
              "and a bust would lower or freeze it"],
             STATUS["rule"], ["boe_lta", "fhfa"]),
        ],
    )
    body += prose(
        "How the model turns this into a path, and how it does not",
        "The block path gives each of the next thirty years a home-growth rate, a price rate, a rent rate, an "
        "equity rate and a bill yield, taken in uneven blocks rather than one average, then loops. Every table "
        "that uses it says so in its evidence column. What the model never does is assign a probability to a "
        "bust, forecast a level, or present a single number as the expected outcome; the official sources "
        "above describe what happened, not what will.",
    )
    return body


def _q_figures() -> str:
    a_claim = cm.a_state_at(BASE_YEAR, BASE_SCENARIO, "claim")
    rent_branch = cm.a_state_at(BASE_YEAR, BASE_SCENARIO, "rent")
    keep = cm.a_state_at(BASE_YEAR, BASE_SCENARIO, "keep")
    sale = cm.sell_waterfall(a_claim["value"], a_claim["value"], 0, "none", months_after_transfer=6)
    rows = [
        (["Property A, market value, November 2026", _n(cm.A_MARKET_2026), "Case figure, rounded",
          "Replace with a written date-of-death appraisal; nothing else in the model is worth re-running before "
          "this is on file", "irs_basis"], STATUS["unverified"]),
        (["Property A, capped assessed value, 2026", _n(cm.A_ASSESSED_2026), "Case figure, rounded",
          "Confirm against the assessor's roll for the parcel in the private file", "ca_rtc51"], STATUS["unverified"]),
        (["Property A, bill, 2025", _n(cm.A_TAX_2025), "Case figure, rounded", "Confirm the bill's components: "
          "the one percent limit, any voter-approved measures, any direct assessment", "ca_rtc51"], STATUS["unverified"]),
        (["Property A, effective levy on assessed value", _p(cm.A_RATE), "Derived from the two rounded figures above",
          "Confirm against the published tax-rate-area schedule for the parcel", "ca_rtc51"], STATUS["derived"]),
        (["Property B, market value, November 2026", _n(cm.B_MARKET_2026), "Case figure, rounded",
          "Only needed here to size the estate and the reassessment comparison", "irs_basis"], STATUS["unverified"]),
        (["Property B, capped assessed value and bill, 2025", _n(cm.B_ASSESSED_2025) + " and " + _n(cm.B_TAX_2025),
          "Case figure, rounded", "Confirm the two-unit income, the vacant unit's lawful status and the "
          "lease terms", "ca_rent"], STATUS["unverified"]),
        (["Property B, rent roll", _n(cm.B_RENT_MONTH) + " a month, two units let", "Case figure, rounded",
          "Confirm against the executed leases; the derived average per unit is " + _n(cm.B_UNIT_RENT_MONTH)
          + " a month and is not evidence about the vacant unit", "irs_rental"], STATUS["unverified"]),
        (["Water, Property A", _n(cm.A_WATER_MONTH[0]) + " to " + _n(cm.A_WATER_MONTH[1]) + " a month",
          "Case figure, rounded range", "Twelve months of bills turn this into a series; sewer and storm-water "
          "charges are separate lines", "water_board"], STATUS["unverified"]),
        (["Electric, Property A", "credit of " + _n(cm.A_SOLAR_CREDIT_MONTH[0]) + " to "
          + _n(cm.A_SOLAR_CREDIT_MONTH[1]) + " a month", "Case figure, rounded range",
          "Read the interconnection date and the export tariff; the credit is a rate-plan artifact and can be "
          "reduced for a new owner", "cpuc_solar"], STATUS["unverified"]),
        (["Insurance, both buildings", _n(cm.midpoint(*cm.A_INSURANCE_YR)) + " and "
          + _n(cm.midpoint(*cm.B_INSURANCE_YR)) + " a year", "Model assumption band, no quote on file",
          "The owner's estimates are " + _n(cm.A_INSURANCE_GUESS_YR) + " and " + _n(cm.B_INSURANCE_GUESS_YR)
          + " a year; both are flagged as likely low for the coverage limits these buildings need", "cdi"],
         STATUS["unverified"]),
        (["Maintenance, as a share of value", _p(cm.MAINT_PCT_A[0], 2) + " to " + _p(cm.MAINT_PCT_A[1], 2),
          "Model assumption band", "Replace with the five-year capital plan and the last three years of invoices",
          "cslb"], STATUS["assumption"]),
        (["Market rent, Property A", _n(cm.A_RENT_MONTH[0]) + " to " + _n(cm.A_RENT_MONTH[1]) + " a month",
          "Listing indications for comparable homes in the same submarket, 2026",
          "A written rent letter from two agents replaces this; a program fair-market-rent figure of about "
          + _n(cm.A_RENT_PROGRAM_FLOOR_MONTH) + " is a floor for a different housing class and is not this "
          "home's rent", "hud_fmr"], STATUS["unverified"]),
        (["Selling costs", _p(cm.SELL_COST, 0) + " of price, band " + _p(cm.SELL_COST_BAND[0], 0) + " to "
          + _p(cm.SELL_COST_BAND[1], 0), "Model assumption",
          "Confirm with the listing agreement and the escrow estimate; concessions and any city levy change "
          "the number", "ca_rtc11911"], STATUS["assumption"]),
        (["Vacancy and management", _p(cm.VACANCY, 0) + " and " + _p(cm.MANAGEMENT, 0) + " of gross rent",
          "Model assumption", "Only needed if the letting paths stay live; a management proposal fixes both",
          "irs_rental"], STATUS["assumption"]),
        (["Transfer year and horizon", str(BASE_YEAR) + " and " + str(LONG_HORIZON) + " years",
          "Chosen for comparability, not predicted", "Re-run at 2040 and 2050; the tables already show both",
          "cbo_long"], STATUS["assumption"]),
    ]
    rows_out = []
    for cells, status in rows:
        rows_out.append((cells[:4], status, [cells[4]]))
    body = ""
    body += table("Every input, with what it is and what replaces it",
                  ["Input", "Value used", "Provenance", "What would turn it into evidence"], rows_out)
    body += table(
        "What the inputs produce in the modelled transfer year, " + str(BASE_YEAR),
        ["Derived figure", "Value", "How it is computed"],
        [
            (["Value at transfer", _n(a_claim["value"]), "Rounded 2026 value, grown by the block path"],
             STATUS["assumption"], ["bls_cpi", "fhfa"]),
            (["Capped assessed value if nothing changes", _n(keep["prior_taxable"]),
              "2026 assessed value grown at the two percent adjustment limit"],
             STATUS["rule"], ["ca_rtc51"]),
            (["Proposition 19 allowance in that year", _n(a_claim["allowance"]),
              "The published indexed amount carried forward by an assumed California house-price rate"],
             STATUS["assumption"], ["boe_lta"]),
            (["Cap line", _n(a_claim["cap"]), "Capped assessed value plus the allowance"],
             STATUS["rule"], ["ca_rtc63"]),
            (["Addition above the cap", _n(a_claim["addition"]),
              "Value minus the cap line, which is the part that gets reassessed"],
             STATUS["rule"], ["ca_rtc63"]),
            (["Taxable value with a qualifying claim", _n(a_claim["taxable"]),
              "Capped base plus the addition"],
             STATUS["rule"], ["ca_rtc63"]),
            (["Bill with a claim, bill if reassessed, bill with no transfer event",
             _n(a_claim["tax"]) + " / " + _n(rent_branch["tax"]) + " / " + _n(keep["tax"]),
              "Each taxable value times the derived effective levy"],
             STATUS["derived"], ["ca_rtc51"]),
            (["Net proceeds of a sale in the transfer year", _n(sale["net"]),
              "Price, less selling costs, less transfer tax and recording items, less income tax on the "
              "measured gain of " + _n(sale["gross_gain"])],
             STATUS["rule"], ["ca_rtc11911", "irs_basis"]),
        ],
    )
    body += prose(
        "Rounding is a privacy control, not a precision claim",
        "Amounts are rounded to the nearest ten dollars at the point of publication, after the arithmetic. That "
        "is enough to stop a published figure from being matched to a single online record by searching its "
        "exact value; it is not enough to make the set of figures unidentifiable to someone who already knows "
        "the household, which is why the site carries no locality, no postal code, no parcel identifier and no "
        "name, and why the repository's earlier history is treated as exposed.",
    )
    return body


def _q_brief(headline: dict) -> str:
    rows = []
    for row in cm.path_table(BASE_YEAR, LONG_HORIZON, BASE_SCENARIO):
        rows.append((
            [str(row["rank"]), str(row["name"])[:46], _n(row["flow_econ"]), _n(row["terminal_real"]),
             str(row["driver"])[:150]],
            STATUS["assumption"], ["ca_rtc63", "irs_basis", "ftb_cap_gains"],
        ))
    body = callout(
        "One page for the attorney and the CPA",
        "Rounded figures, same transfer date and horizon for every path, and a list of the documents that would "
        "replace an assumption with evidence. Print this page; the two-column layout fits one sheet.",
        "info",
    )
    body += table(
        "The question, in figures",
        ["Item", "Modelled value", "Ask"],
        [
            (["Home value at a " + str(BASE_YEAR) + " transfer", _n(headline["value"]),
              "Confirm the date-of-death appraisal standard and who instructs the appraiser"],
             STATUS["unverified"], ["irs_basis"]),
            (["Bill if the heir occupies and claims", _n(headline["bill_if_claimed"]),
              "Confirm eligibility, occupancy timing and the claim window"],
             STATUS["rule"], ["ca_rtc63", "boe_prop19"]),
            (["Bill if the home is let or left alone", _n(headline["bill_if_let"]),
              "Confirm what the assessor will use as value at transfer"],
             STATUS["rule"], ["ca_rtc63"]),
            (["Annual saving the claim is worth", _n(headline["prop19_saving"]),
              "Confirm the occupancy intention in writing before anyone relies on this"],
             STATUS["derived"], ["ca_rtc63"]),
            (["Income tax on a sale inside the transfer year", _n(headline["income_tax_on_sale_now"]),
              "Confirm basis, holding period treatment and whether any gain exists at all"],
             STATUS["rule"], ["irs_basis", "ftb_cap_gains", "irs_topic409"]),
            (["Net proceeds if sold in the transfer year", _n(headline["net_sale_proceeds"]),
              "Confirm selling costs, transfer tax adoption and recording charges"],
             STATUS["assumption"], ["ca_rtc11911", "ca_gov27361"]),
            (["Break-even appreciation to justify keeping", _p(headline["break_even_appreciation"]),
              "Counsel and CPA to challenge the return assumption, not the housing assumption"],
             STATUS["assumption"], ["sec_stocks", "cbo_long"]),
            (["Break-even rent for the letting paths", _n(cm.break_evens(BASE_YEAR, LONG_HORIZON, BASE_SCENARIO)["needed_month_rent"]) + " a month",
              "Replace with two written rent letters; program fair-market-rent is a floor for a different class"],
             STATUS["unverified"], ["hud_fmr", "irs_rental"]),
        ],
    )
    body += table("Path comparison at " + str(BASE_YEAR + LONG_HORIZON) + ", in 2026 dollars",
                  ["Rank", "Path", "Annual economic flow", "Wealth at horizon", "Why"], rows)
    body += table(
        "Documents to bring, in the order the model needs them",
        ["Document", "Replaces which assumption", "Owner"],
        [
            (["Executed trust, certificate of trust, and the distribution provisions for this home",
              "who receives what, and whether occupancy is even possible", "Attorney"],
             STATUS["missing"], ["ca_prob"]),
            (["Written appraisal at the date of death, and the prior owner's basis records",
              "the value line and the gain line", "CPA and appraiser"],
             STATUS["missing"], ["irs_basis", "irs_pub551"]),
            (["Assessor roll for both parcels, current bills, and the published tax-rate-area schedule",
              "the effective levy on each building", "Attorney"],
             STATUS["missing"], ["ca_rtc51", "boe_counties"]),
            (["Proposition 19 claim form, the occupancy plan, and the homeowners'-exemption filing",
              "the " + _n(headline["prop19_saving"]) + " a year saving", "Attorney"],
             STATUS["missing"], ["ca_rtc63", "ca_rtc218"]),
            (["Two insurance quotes with declarations pages, twelve months of utility bills, and the solar "
              "interconnection terms", "the operating-cost column", "Household"],
             STATUS["missing"], ["cdi", "cpuc_solar"]),
            (["Executed leases, rent-roll history, and the lawful-unit documentation for the let building",
              "the rental income and the legality risk", "Attorney"],
             STATUS["missing"], ["irs_rental", "ca_rent"]),
            (["Estate inventory: financial assets, prior gift history, and the first spouse's Form 706 if any",
              "the estate-tax line and the portability question", "CPA and attorney"],
             STATUS["missing"], ["irs_estate", "irs_estate_faq"]),
            (["Written household decision rules, signed and dated before the figures are read",
              "nothing - it constrains the reading of everything", "Household"],
             STATUS["missing"], ["sec_stocks"]),
        ],
    )
    return body


def _q_questions(headline: dict) -> str:
    be = cm.break_evens(BASE_YEAR, LONG_HORIZON, BASE_SCENARIO)
    body = callout(
        "How to use this list",
        "Each line states what is unknown, who can answer it, what document closes it, and which modelled number "
        "moves when the answer arrives. A question with no effect on any figure is a discussion, not a task, and "
        "is left off this table.",
        "info",
    )
    rows = [
        ("Will the heir actually live in the home, and for how long?", "Household, in writing",
         "A signed occupancy statement with a date and a reason",
         "Sets the imputed-rent credit, the whole of the Proposition 19 eligibility question, and the "
         + _n(headline["prop19_saving"]) + " a year saving; it is the largest single driver in the model",
         "ca_rtc63", STATUS["missing"]),
        ("What is the home worth at the date of death?", "Licensed appraiser, engaged by the fiduciary",
         "Written appraisal at the date of death, plus the assessor's transfer-year determination",
         "Sets the reassessment addition, the cap arithmetic and the gain line; the model currently runs on a "
         "rounded owner figure", "irs_basis", STATUS["missing"]),
        ("What is the estate's financial wealth?", "CPA and fiduciary", "Confidential estate inventory with dates",
         "Decides whether a Form 706 and a liquidity plan exist at all; the exclusion is " + _n(cm.FED_EXCL_2026)
         + " for a 2026 death", "irs_estate", STATUS["missing"]),
        ("Were there taxable gifts, and was a portability election made for the first death?",
         "CPA, from Forms 709 and any Form 706", "Prior gift schedules and the first estate's filing",
         "Reduces or doubles the amount available; it changes the estate rows, not the house ranking",
         "irs_estate_faq", STATUS["missing"]),
        ("What is the published tax-rate-area total for this parcel, and what sits inside it?",
         "County assessor and auditor-controller", "The published rate-area schedule and one full bill",
         "The model derives " + _p(cm.A_RATE) + " from two rounded owner figures; the difference between one "
         "percent and that number is " + _n(cm.a_state_at(BASE_YEAR, BASE_SCENARIO, "keep")["tax"] * 0.25)
         + " a year of cost", "ca_rtc51", STATUS["unverified"]),
        ("Can the home be let at all, and on what terms?", "Attorney and a letting agent",
         "Zoning and short-term-rental check, lease review, two written rent letters",
         "Turns the " + _n(cm.A_RENT_MONTH[0]) + " to " + _n(cm.A_RENT_MONTH[1]) + " indication into evidence and "
         "tests the break-even rent of " + _n(be["needed_month_rent"]), "hud_fmr", STATUS["missing"]),
        ("Is the let building's third unit lawful, and are the two leases assignable and enforceable?",
         "Attorney, with the city's permit records", "Certificate of occupancy or permit history, and both leases",
         "An unlawful unit can end the income and reorder the whole comparison; it also changes what can be "
         "insured", "ca_rent", STATUS["missing"]),
        ("Is there any mortgage, HELOC, tax lien or assessment on either building?", "Title report and county records",
         "Preliminary title report for both parcels",
         "The model assumes no debt; a carried low-rate loan changes the sell-versus-keep arithmetic and the "
         "liquidity column", "ca_gov27361", STATUS["missing"]),
        ("What are the real insurance and maintenance numbers?", "Two agents and three licensed contractors",
         "Quotes with declarations pages, an inspection report, a costed five-year plan",
         "Replaces the flagged bands of " + _n(cm.midpoint(*cm.A_INSURANCE_YR)) + " and "
         + _n(cm.A_MARKET_2026 * cm.midpoint(*cm.MAINT_PCT_A)) + " a year", "cdi", STATUS["missing"]),
        ("Has the trust been reviewed for how this specific distribution is authorised?", "Estate attorney",
         "Amendment or a written confirmation, plus the trustee's powers list",
         "Determines whether occupancy, a lease or a sale is even permitted without a court process, and whether "
         "the low assessed value can be preserved", "ca_prob", STATUS["missing"]),
        ("What is the heir's own marginal tax position, now and at transfer?", "CPA",
         "Last two returns and a projection of the heir's bracket",
         "Drives the " + _p(cm.TAX_ON_QUALIFIED, 1) + " tax drag the model applies to the portfolio and whether "
         "the sale-year gain is taxed at " + _p(cm.CA_TOP_RATE + cm.CA_MHST, 1) + " in California", "ftb_cap_gains",
         STATUS["missing"]),
        ("Is the like-kind exchange route wanted?", "Attorney and CPA before any listing agreement",
         "Written structure memo with deadlines diarised",
         "Only relevant if the home will be held for investment; a primary residence and property held mainly for "
         "sale do not qualify", "irs_1031_tips", STATUS["missing"]),
    ]
    body += table("What has to be known before a decision is defensible",
                  ["Question", "Who answers", "Document that closes it", "Which number moves and how"],
                  [([r[0], r[1], r[2], r[3]], r[5], [r[4]]) for r in rows])
    body += table(
        "Answers already on file, and what they are worth",
        ["Question", "Answer", "Effect on the model"],
        [
            (["Does California tax an inheritance?", "No state estate or inheritance tax for deaths on or after "
              "2005; California does tax the later gain as ordinary income, with one percent more above "
              + _n(cm.CA_MHST_FLOOR) + " of taxable income",
              "Removes the state transfer-tax line and puts the weight on basis, the surcharge and the "
              "reassessment rule"],
             STATUS["rule"], ["ca_sco", "ftb_cap_gains", "ftb_540", "ca_rtc17043"]),
            (["Is the inherited home's income-tax basis stepped?", "Yes, generally to fair market value at death, "
              "with exceptions and reporting rules",
              "Makes a sale inside the transfer year close to income-tax-free, which is why the model prices it "
              "first"],
             STATUS["rule"], ["irs_basis", "irs_pub551"]),
            (["Can the low assessed value simply be kept?", "Only with a qualifying family-home claim, which "
              "requires principal-residence occupancy by the heir, a homeowners' exemption filing within one "
              "year, and a claim within three years; and it is capped at the prior taxable value plus the indexed "
              + _n(cm.PROP19_ALLOWANCE) + " allowance",
              "Splits the model into three bill outcomes: " + _n(cm.a_state_at(BASE_YEAR, BASE_SCENARIO, "keep")["tax"])
              + ", " + _n(cm.a_state_at(BASE_YEAR, BASE_SCENARIO, "claim")["tax"]) + " and "
              + _n(cm.a_state_at(BASE_YEAR, BASE_SCENARIO, "rent")["tax"])],
             STATUS["rule"], ["ca_rtc63", "boe_prop19", "boe_lta"]),
        ],
    )
    return body


def _q_suggestions(headline: dict) -> str:
    body = callout(
        "Suggestions, staged so nothing is implemented before it is chosen",
        "Each suggestion says what it changes, what it costs in effort, and what evidence would justify it. The "
        "owner's rule is the same one the model uses: no projection is adopted as a plan until the input behind "
        "it is a document.",
        "info",
    )
    rows = [
        ("Now, before any decision", "Get two insurance quotes and one inspection with a costed five-year plan",
         "Replaces " + _n(cm.midpoint(*cm.A_INSURANCE_YR)) + " and "
         + _n(cm.A_MARKET_2026 * cm.midpoint(*cm.MAINT_PCT_A)) + " a year of assumption in every cost row",
         "Two days of calls; the fees are the only cost", "The cost column is currently the second largest block "
         "in the comparison and the least evidenced", "cdi", STATUS["missing"]),
        ("Now", "Write the household's decision rules and sign them, dated, before any new figure is read",
         "Stops the projection from choosing the answer", "One evening", "It is the only control that works on "
         "the reading of every other number", "sec_stocks", STATUS["missing"]),
        ("Now", "Replace the derived levy with the published tax-rate-area schedule",
         "Tests " + _p(cm.A_RATE) + " against the assessor's and auditor's published totals",
         "One records request", "Every tax line in the model scales on it, including the reassessment branch",
         "ca_rtc51", STATUS["unverified"]),
        ("Next quarter", "Commission two written rent letters for the home and one for the vacant unit in the "
         "other building", "Turns the letting rows from a floor into a comparison against the break-even of "
         + _n(cm.break_evens()["needed_month_rent"]) + " a month", "A week and an agent's time",
         "The letting paths are the only rows the model currently cannot rank with confidence", "hud_fmr",
         STATUS["missing"]),
        ("Next quarter", "Split the three tax questions in the dashboard, permanently",
         "Estate tax, income-tax basis, and property-tax assessment appear as three separate blocks with three "
         "separate sources", "A design change", "Conflating them is the most common and most expensive error in "
         "inherited-property decisions", "irs_estate", STATUS["guidance"]),
        ("Next quarter", "Add a scenario selector to every table, with the block path as the default",
         "Readers see the same row under five economic worlds instead of one", "Modelled already; needs page "
         "wiring", "A single-rate table invites the reader to treat an assumption as a forecast", "cbo_long",
         STATUS["guidance"]),
        ("Next quarter", "Publish the model's own inputs and provenance next to the outputs",
         "Every figure on the site becomes traceable to a rule, a derived value, a rounded input or an "
         "assumption", "Done on the model-figures page; keep it updated",
         "A reader who cannot find the input cannot challenge the output", "irs_pub551", STATUS["guidance"]),
        ("Next quarter", "Add a standing recheck date and a law-watchlist diff",
         "The site records when each source was read and what changed since", "A build-time field per source",
         "Enacted changes and proposals have to stay separated or the site becomes an argument for whatever is "
         "in the news", "sos_measures", STATUS["guidance"]),
        ("Before the transfer", "Set the investment policy for the proceeds, in writing, with the staging window "
         "fixed", "Removes the 'should we wait' question at the moment it is hardest to answer",
         "One document", "The staging rows show the cost of waiting and the cost of not waiting; both are "
         "decided better in advance", "treasury_bills", STATUS["missing"]),
        ("Before the transfer", "Decide, in writing, whether the let building stays in the family",
         "The capped base on that building is the most valuable tax asset the household has, and it is not for "
         "sale in any path here", "A one-line decision recorded in the log",
         "It reframes the whole question: this is a decision about one house, not about a portfolio of property",
         "ca_rtc51", STATUS["guidance"]),
        ("Ongoing", "Re-run the model each year with the current bill, the published allowance, and a refreshed "
         "appraisal or estimate", "Keeps the break-evens honest", "One afternoon a year",
         "The allowance re-indexes every other February and the levy schedule changes with each local measure",
         "boe_lta", STATUS["guidance"]),
        ("Ongoing", "Keep the public site and the private case file separate", "Nothing about this household "
         "leaves the private file", "Every commit",
         "Rounding protects a number, not a person; the earlier public history is treated as exposed",
         "github_sensitive", STATUS["guidance"]),
    ]
    body += table("Suggestion backlog, in the order the model can use it",
                  ["When", "Suggestion", "What it changes", "Effort", "Why it is on the list", "Status"],
                  [([r[0], r[1], r[2], r[3], r[4]], r[6], [r[5]]) for r in rows])
    body += table(
        "How to find the missing information, by method",
        ["Missing item", "Method that produces evidence", "What does not count", "Official reference"],
        [
            (["Value at date of death", "A licensed appraisal, ordered by the fiduciary, with the effective date "
              "and the comparable sales listed", "An online estimate, an assessor's market value, or a listing "
              "price", "irs_basis"], STATUS["missing"], ["irs_basis"]),
            (["Market rent for a high-value single-family home", "Two written rent letters from agents who let "
              "this class, plus the last twelve months of a comparable's rent history",
              "A voucher-program fair-market-rent figure, which prices a different housing class", "hud_fmr"],
             STATUS["missing"], ["hud_fmr", "irs_rental"]),
            (["Insurance cost", "Two quoted policies with declarations pages, matched on the dwelling limit, and "
              "a rebuild-cost estimate", "A neighbour's premium or a state average", "cdi"],
             STATUS["missing"], ["cdi"]),
            (["Property-tax treatment at transfer", "A written pre-filing determination or a claim review with "
              "the assessor, plus the published rate-area schedule", "A county website FAQ", "boe_prop19"],
             STATUS["missing"], ["boe_prop19", "ca_rtc63", "boe_counties"]),
            (["Capital costs", "Three licensed bids against an inspection report", "A rule of thumb as a "
              "percentage of value", "cslb"], STATUS["missing"], ["cslb"]),
            (["Lease and unit legality", "Title and permit records, both leases, and the local rental ordinance",
              "The current tenants' understanding of the arrangement", "ca_rent"],
             STATUS["missing"], ["ca_rent"]),
            (["Estate size", "A confidential inventory with statements, plus the gift history",
              "A guess at what the accounts hold", "irs_estate"], STATUS["missing"], ["irs_estate"]),
        ],
    )
    return body


def _q_requirements() -> str:
    done = [
        ("Phased investing tested against 1929 and 2008 entry risk", "done",
         "The staging tables price the same crash at five different months and both windows", "fed_1929", "fed_2008"),
        ("Ranges instead of round-number assumptions", "done",
         "Bands are used for rent, insurance and maintenance; every band is flagged as unverified", "cdi", "hud_fmr"),
        ("What would change the answer, on the first screen", "done",
         "Six thresholds with the modelled value each one moves", "ca_rtc63", "irs_estate"),
        ("Mixed paths alongside the pure choices", "done",
         "Three mixed paths, including live-then-sell and let-then-sell, priced on the same engine", "irs_121", "irs_rental"),
        ("Reinvestment risk beside the staging headline", "done",
         "The waiting-cost table sits under the crash table on the same page", "treasury_bills", "sec_stocks"),
        ("All paths compared at the same transfer date and horizon", "done",
         "One engine, five scenarios, four horizons, three transfer years", "cbo_long", "bls_cpi"),
        ("Taxes, debt, occupancy, capital costs and liquidity in one view", "partial",
         "Debt is the exception: nothing in this project states a loan, so the model assumes none and flags it",
         "ca_gov27361", "irs_1041"),
        ("Deadlines as a timeline", "done", "The timeline page plus the dated filing table on this page",
         "ca_prob", "irs_706"),
        ("Grouped menu and glossary", "done", "Six groups and a glossary of every term the model uses",
         "irs_pub551", "boe_prop19"),
        ("One-page attorney and CPA brief", "done", "Printable, two-column, figures and document list on one sheet",
         "irs_estate", "ftb_cap_gains"),
        ("Proposition 19 modelled with the allowance carried forward", "done",
         "The allowance re-indexes in every transfer-year row instead of freezing at " + _n(cm.PROP19_ALLOWANCE),
         "boe_lta", "ca_rtc63"),
        ("Depreciation and recapture modelled", "done",
         "Twenty-seven and a half year straight-line depreciation, recapture on the exit rows, and the "
         "consequence for the let-then-sell path", "irs_rental", "irs_sched_d"),
        ("Transfer tax and recording fees priced into the sell path", "done",
         "Statutory ceilings applied at " + _p(cm.DTT_COUNTY_MAX + cm.DTT_CITY_MAX) + " with local adoption flagged",
         "ca_rtc11911", "ca_gov27361"),
        ("Primary-residence exclusion switched on for living-then-sell", "done",
         "The live-five-years row uses the " + _n(cm.S121_SINGLE) + " exclusion", "irs_121", "irs_topic409"),
        ("Imputed rent for living paths", "done", "Every self-used owned home is credited with its net market rent",
         "irs_rental", "bls_cpi"),
        ("Model run on ranges rather than points", "partial",
         "Costs and rents are ranges; the value input is a single rounded owner figure pending an appraisal",
         "irs_basis", "fhfa"),
        ("Form 540 surcharge read and applied", "done",
         "One percent above " + _n(cm.CA_MHST_FLOOR) + " is applied in the tax-rate columns", "ftb_540", "ca_rtc17043"),
        ("Distribution chart for the proceeds", "done", "The waterfall table and bar block on the compare-paths page",
         "ca_rtc11911", "irs_topic409"),
        ("Separate estate tax, income-tax basis and property-tax assessment", "done",
         "Three pages, three source sets, and a brief that says so", "irs_estate", "irs_basis", "ca_rtc51"),
        ("Estate thresholds with projections and the missing cash figure", "partial",
         "Exclusion, indexation and sensitivity rows are published; the estate's financial assets are unknown by "
         "design", "irs_2027", "irs_estate_faq"),
        ("Black-swan section that mimics uneven growth and inflation", "done",
         "A thirty-year block path with a dated bust, plus four flat alternatives", "bls_cpi", "fed_inflation"),
        ("Executive summary, questions list and suggestions section", "done",
         "Each with the evidence standard attached", "irs_basis", "sec_stocks"),
        ("Privacy-first containment and rounding", "done",
         "Rounded to " + str(cm.ROUND_TO) + " dollars, no locality identifiers, fail-closed verifier checks",
         "github_sensitive", "irs_estate"),
        ("Prior public-data exposure contained in the working tree", "partial",
         "Nothing identifying is published here; earlier history is a separate administrator action and is "
         "recorded as unresolved", "github_sensitive", "irs_estate"),
    ]
    rows = []
    for item, status, note, *keys in done:
        refs = [k for k in keys if k in SOURCES]
        rows.append(([item, "Complete in this build" if status == "done" else "Partly complete", note],
                     STATUS["rule"] if status == "done" else STATUS["guidance"], refs or ["cbo_long"]))
    body = table("The owner's task list, with the built artefact beside it",
                 ["Requirement", "Status", "Where it is satisfied"], rows)
    body += callout(
        "What is still open by design",
        "Nothing on this site is a decision. The three rows marked partly complete are open because the household "
        "has not supplied an appraisal, a debt position or an estate inventory, and the model refuses to invent "
        "them: the affected cells stay flagged.",
        "warning",
    )
    return body


def _q_flagged() -> str:
    rows = [
        ("Insurance and maintenance figures are assumption bands, not quotes",
         "The owner's estimates of " + _n(cm.A_INSURANCE_GUESS_YR) + " a year sit far below the band the model "
         "uses for a home of this replacement cost; a dwelling limit that does not track rebuild cost is a "
         "coverage problem before it is a budget problem",
         "cdi", "Two written quotes with declarations pages"),
        ("Market rent is a listing indication for a different housing class",
         "The " + _n(cm.A_RENT_MONTH[0]) + " to " + _n(cm.A_RENT_MONTH[1]) + " band comes from advertised listings "
         "of comparable homes, not signed leases; the program fair-market-rent figure of about "
         + _n(cm.A_RENT_PROGRAM_FLOOR_MONTH) + " is a floor for another class and must not be used as this "
         "home's rent", "hud_fmr", "Two written rent letters, plus lease evidence"),
        ("Effective property-tax rates are derived, not looked up",
         _p(cm.A_RATE) + " and " + _p(cm.B_RATE) + " are quotients of the owner's rounded bill and assessed value; "
         "the constitutional limit is one percent and the rest is measure-driven and time-limited",
         "ca_rtc51", "The published tax-rate-area schedule and one complete bill"),
        ("The estate top rate has not been re-read from the current Form 706 instructions",
         "The model applies " + _p(cm.ESTATE_TOP_RATE, 0) + " to the excess over the exclusion for the "
         "sensitivity rows only; the graduated schedule and any deductions are not modelled",
         "irs_706", "The Form 706 instructions for the year of death"),
        ("The Proposition 19 allowance is projected, not published, beyond February 2027",
         "Only the amounts up to the " + _n(cm.PROP19_ALLOWANCE) + " window are published; the model re-indexes "
         "them by an assumed California house-price rate, which moves the bill in every transfer-year row",
         "boe_lta", "The BOE adjustment issued in the February preceding the transfer"),
        ("A local shorthand measure referred to as 'Prop H' in earlier notes is still unmapped",
         "No locality is named in this project and no rate is modelled from an unverified local measure; the item "
         "stays open until the official text and the jurisdiction are read",
         "sos_measures", "The official measure text and the adopting jurisdiction"),
        ("Federal like-kind exchange deadlines are referenced, not quoted",
         "The identification and completion periods are stated on the IRS page; this site does not restate the "
         "day counts", "irs_1031_tips", "Read the IRS page and the form instructions before any listing agreement"),
        ("Federal inflation data for October 2026 lacks most twelve-month changes",
         "The October 2025 survey was not collected during the lapse in appropriations, so year-on-year "
         "comparisons in that month cannot be published; the model's inflation anchors come from the annual "
         "series instead", "bls_cpi", "The BLS note on handling missing data"),
        ("The estate's financial assets, all debt, and any prior gift history are absent",
         "Estate-tax rows are therefore sensitivity rows, and the sell-versus-keep comparison assumes no loan on "
         "either building", "irs_estate", "The confidential inventory, the title reports, and Forms 709 and 706"),
        ("The 2025 California Form 540 instruction booklet was not fully retrieved",
         "The surcharge line and the capital-gain treatment are read from the instructions page and the statute; a "
         "future-year return needs the booklet for that year", "ftb_540", "The instruction booklet for the sale year"),
        ("Four pull requests from earlier sessions remain open against an older main",
         "They predate the current privacy boundary and may reintroduce figures; nothing in them is merged or "
         "assumed here", "github_sensitive", "Owners rebase or close them against current main"),
        ("Earlier public history in this repository is not scrubbed",
         "A working tree cannot erase prior commits, pull-request views, forks, caches or clones; repository "
         "visibility is a separate administrator decision", "github_sensitive",
         "Administrator-led remediation, with a private encrypted archive taken first"),
    ]
    body = table(
        "Open items, each with the evidence that closes it",
        ["Flagged item", "Why it matters and how the model handles it", "Document or record that closes it"],
        [([r[0], r[1], r[3]], STATUS["unverified"], [r[2]]) for r in rows],
    )
    body += prose(
        "How the model handles a flagged number",
        "It keeps the figure, marks the row unverified, states the direction the error runs, and refuses to let "
        "the flagged number decide anything on its own. A ranking that flips because of an unverified input is "
        "reported as a tie plus a to-do, which is what the break-even tables do here.",
    )
    return body


def _q_privacy() -> str:
    rows = [
        ("Published amounts are rounded to the nearest " + str(cm.ROUND_TO) + " dollars",
         "Rounding defeats exact-value searching, which is the exposure the owner identified. It does not hide a "
         "household from someone who already knows the household, so the site also omits locality, postal codes, "
         "parcel identifiers, names and dates of the assets",
         "The verifier fails the build on any unrounded amount, any five-digit location-like identifier, any "
         "street-address pattern, and any locality token from the case", "github_sensitive", STATUS["guidance"]),
        ("The site is marked noindex and serves a restrictive content policy",
         "No remote scripts, no storage, no analytics, no forms; the what-if tool runs in page memory only",
         "Read by the verifier on every page", "sec_stocks", STATUS["rule"]),
        ("Earlier history remains exposed",
         "This repository was public with earlier, less generalised content; a working-tree change does not remove "
         "history, forks, caches or clones, and only an administrator can decide on visibility or history "
         "remediation", "Treat the earlier figures as retained by someone; take a private encrypted archive "
         "before any destructive history action", "github_sensitive", STATUS["missing"]),
        ("Nothing personal should ever be committed here",
         "Deeds, trust instruments, returns, bills, statements, leases, policies, appraisals and adviser "
         "correspondence belong in an access-controlled private store, not in a repository that publishes a public "
         "site", "The ignore patterns cover the private workpaper paths; the rule that keeps them out is the "
         "one that matters", "irs_1041", STATUS["guidance"]),
    ]
    return table("Privacy controls, stated as what they do and do not do",
                 ["Control", "What it protects", "How it is enforced or limited"],
                 [([r[0], r[1], r[2]], r[4], [r[3]]) for r in rows])


def _q_log() -> str:
    """The criteria to agree before the figures are read, priced with the model."""
    be = cm.break_evens(BASE_YEAR, LONG_HORIZON, BASE_SCENARIO)
    seq = cm.break_evens(BASE_YEAR, LONG_HORIZON, "sequence")
    rows = [
        ("I will keep the home only if I will actually live in it as my principal residence within one year of "
         "the transfer, and I will file the claim.",
         "Worth " + _n(be["tax_saving_from_claim"]) + " a year against the reassessed bill; forfeited by a late "
         "claim, which restarts only from the lien date of the filing year",
         "ca_rtc63"),
        ("I will keep it only if I believe it compounds above the portfolio's after-tax return, which on these "
         "assumptions means above " + _p(be["needed_house_cagr"]) + " a year in the flat baseline and "
         + _p(seq["needed_house_cagr"]) + " a year on the block sequence.",
         "Below those rates, selling at the transfer date is worth more; the housing credit flips the "
         "comparison in the other direction, so this test is only for a home that is not lived in",
         "cbo_long"),
        ("I will let it only if a written rent letter clears the operating cost, which the model puts at "
         + _n(cm.owner_costs("A", BASE_YEAR, BASE_SCENARIO, cm.a_state_at(BASE_YEAR, BASE_SCENARIO, "rent")["taxable"], False)["total"])
         + " a year before any income tax.",
         "Two written letters, not listings; the break-even gross rent on these assumptions is "
         + _n(be["needed_month_rent"]) + " a month in the flat baseline",
         "irs_rental"),
        ("I will sell in the same tax year as the transfer, and I will not wait for a better price while the "
         "basis is already set at it.",
         "A sale on the date-of-death value leaves no gain to tax and no deductible loss; every year of delay "
         "moves the price away from the basis in both directions",
         "irs_basis"),
        ("I will stage the proceeds over a fixed window on a fixed schedule and will not extend the window "
         "because the market looks about to fall.",
         "The crash tables price the benefit; the waiting table prices the cost, which on the model is "
         + _n(cm.reinvestment_risk(cm.headline()["net_sale_proceeds"], 30, 0.035, 0.070)["price_increase"])
         + " of price bought over at a 7 percent drift",
         "treasury_bills"),
        ("I will not transfer, refinance or add an owner to the other building without a separate property-tax "
         "analysis.",
         "Its capped base is the most valuable tax asset in the household and a change in ownership ends it",
         "ca_rtc51"),
        ("I will sign this page, dated, before the appraisal and the tax figures are read, and I will re-run the "
         "model annually rather than re-argue it whenever a number changes.",
         "The build regenerates every figure from its inputs, so a re-run is one command and not a negotiation "
         "with oneself",
         "irs_estate"),
    ]
    return table(
        "Pre-agreed decision criteria, with the figure each one turns on",
        ["Rule, to be agreed and signed before the figures are read", "What the model says it is worth", "Official reference"],
        [([r[0], r[1]], STATUS["guidance"], [r[2]]) for r in rows],
    )


def _q_glossary() -> str:
    rows = [
        ("Taxable value", "The assessed figure the levy is applied to; under Proposition 13 it grows by no more "
         "than two percent a year until a change in ownership resets it", "ca_rtc51"),
        ("Factored base year value", "A base year value grown forward to the current year by the statutory "
         "adjustments; this is the number the Proposition 19 cap is built on", "ca_rtc63"),
        ("Change in ownership", "The event that triggers reassessment; a transfer at death is treated under its "
         "own rules, and a trust transfer is inside the family-home exclusion's definition", "ca_rtc480"),
        ("The indexed one-million-dollar allowance", "The amount added to the prior taxable value to form the "
         "Proposition 19 cap; re-indexed every other February by the California house-price index", "boe_lta"),
        ("Imputed rent", "The market rent a self-used owned home would earn; used so that living in a house you "
         "own is not counted as free housing in a comparison with letting it", "irs_rental"),
        ("Economic view against cash view", "Cash counts money that moves; the economic view also counts the "
         "housing the household consumes itself, which is what makes the paths comparable", "irs_121"),
        ("Unrecaptured section 1250 gain", "Depreciation previously claimed on rental real property, taxed on "
         "sale at up to a twenty-five percent federal rate, with California taxing it as ordinary income",
         "irs_sched_d"),
        ("Nonqualified use", "Periods a home was rented rather than occupied, which reduce the main-home "
         "exclusion; the reason the let-then-sell row is priced differently from the live-then-sell row",
         "irs_121"),
        ("Deceased spousal unused exclusion", "The unused part of a deceased spouse's exclusion, available only "
         "if a federal estate-tax return was timely filed for that estate", "irs_estate_faq"),
        ("Adjusted taxable gifts", "Lifetime gifts counted in the estate-tax computation; they reduce what the "
         "exclusion at death covers", "irs_estate"),
        ("Sequence risk", "The chance that the order of returns, not their average, decides the outcome; the "
         "reason the model runs the same thirty-year arithmetic with the bust moved next to the transfer date",
         "sec_stocks"),
        ("Reinvestment risk", "The risk that money held back is redeployed at worse prices or lower yields; it "
         "sits on the same page as every staging figure", "treasury_bills"),
        ("Documentary transfer tax", "A county levy on the sale document, capped in state law at fifty-five cents "
         "per five hundred dollars of consideration, with a city allowed half again; local adoption varies",
         "ca_rtc11911"),
        ("Effective levy", "Bill divided by assessed value; in this model it is derived from the owner's rounded "
         "figures and stays flagged until the published rate-area schedule confirms it", "ca_rtc51"),
    ]
    return table("Terms the model uses, in the sense this site uses them",
                 ["Term", "Meaning here", "Official reference"],
                 [([r[0], r[1]], STATUS["reference"], [r[2]]) for r in rows])


NEW_PAGES = {
    "pages/model-figures.html": (
        "Model figures and provenance",
        "Every input the pages use, its rounded value, and what would replace it with evidence. Figures are "
        "rounded to the nearest ten dollars after the arithmetic; official published amounts are shown exactly.",
    ),
    "pages/economic-baselines.html": (
        "Economic baselines",
        "The documented record on variability - prices, house values, equity drawdowns and policy rates - and the "
        "block path the model uses instead of one growth rate for fifty years.",
    ),
}


def content_for(path: str) -> tuple[str, str, str]:
    """Framework text for every page, plus the quantified addendum where one applies."""
    if path in NEW_PAGES:
        heading, lead = NEW_PAGES[path]
        return heading, lead, quantified(path)
    heading, lead, body = base_content_for(path)
    return heading, lead, body + quantified(path)


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
<title>{title_full}</title><link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/phase-model.js" defer></script><script src="{prefix}assets/app.js" defer></script></head>
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
