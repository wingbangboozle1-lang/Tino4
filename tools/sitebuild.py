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
CHECKED = "2026-11-14"
SITE_TITLE = "Private inheritance decision workspace"

# Links were fetched directly on CHECKED. The scope is intentionally narrow:
# a source may establish a legal rule or a public historical observation, but
# never a private property's value, bill, lease, premium, title, or tax position.
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
        "scope": "Official search interface for federal bills and resolutions and their status. A proposal is not current law unless enacted; no specific pending bill is treated as law here.",
        "verified": True,
    },
    "ca_legislation": {
        "label": "California Legislative Information — Bill Search",
        "url": "https://leginfo.legislature.ca.gov/faces/billSearchClient.xhtml",
        "scope": "Official search interface for California bills and their status. A bill or proposal is not current law unless chaptered and effective; no specific pending bill is treated as law here.",
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
<meta name="description" content="Privacy-safe, source-linked decision framework. No property addresses, locations, valuations, rents, or expense histories are published.">
<title>{esc(title)} · {esc(SITE_TITLE)}</title>
<link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/app.js" defer></script>
</head><body class="{esc(page_class)}"><a class="skip" href="#main">Skip to content</a>
<div class="layout">
<aside class="sidebar"><a class="brand" href="{prefix}index.html"><span class="brand-icon" aria-hidden="true">◈</span><span>PRIVATE<br>DECISION BRIEF</span></a>
<p class="sidebar-note">Trust transfer +<br>already-owned property</p>
<nav aria-label="Main navigation">{build_nav(path)}</nav>
<div class="sidebar-bottom">No addresses or case amounts<br>Sources checked {CHECKED}</div></aside>
<div class="workspace"><header class="topbar"><span>RESEARCH / DECISION SUPPORT</span><div><span class="privacy-dot" aria-hidden="true"></span> Privacy-first <button class="print-button no-print" id="print-page" type="button">Print</button></div></header>
<main id="main"><div class="page-heading"><span class="eyebrow">{esc(eyebrow)}</span><h1>{esc(title)}</h1><p class="lead">{esc(intro)}</p></div>{body}</main>
<footer><strong>Planning framework only.</strong> Not legal, tax, insurance, appraisal or investment advice. A source supports only its stated scope, not a private fact. Blank means unknown, not zero. The public site intentionally contains no property-specific dollar values or locations.<br>
<a href="{prefix}pages/privacy.html">Privacy &amp; limits</a> · <a href="{prefix}pages/sources.html">Official sources</a> · <a href="{prefix}pages/flagged-for-review.html">Flagged for review</a></footer>
</div></div></body></html>'''


def build_index() -> str:
    rows = [
        {"cells": ["Trust, title and timing", "The actual trust, amendments, trustee authority, distribution trigger and debt are not public or independently confirmed.", "Obtain the executed trust/deed and a written trustee timeline before comparing any path."], "status": "Missing", "sources": ["ca_prob160617", "ca_rtc480"]},
        {"cells": ["Property-tax exclusion eligibility", "A transfer by trust does not by itself establish eligibility for an intergenerational exclusion.", "Confirm the eligible relationship, transferor's principal residence, transferee occupancy and filings."], "status": "Missing", "sources": ["boe_prop19", "ca_rtc63"]},
        {"cells": ["Federal estate-tax exposure", "The 2026 Form 706 filing test uses gross estate plus adjusted taxable gifts and the specific gift-tax exemption; a portability election can also require filing below the threshold.", "Obtain the full estate inventory, prior gifts, deductions and any spouse/portability facts; this is not a per-heir allowance."], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["Already-owned property: rental-income and residence tests", "Property B is separate from the trust transfer. Any current rent, lease, lawful use, net cash flow and ability to serve as a residence are private inputs and are not published or verified here.", "Include any B rent and tenant obligations in a private model, separately from A; confirm lawful use and residence suitability."], "status": "Missing", "sources": ["irs_rental", "ca_rent", "cdi"]},
        {"cells": ["Live, rent, sell or mix", "No after-tax cash-flow comparison is possible without valuations, basis, sale costs, actual bills, leases and quotes.", "Compare whole-property and mixed-use paths only after the data checklist is complete."], "status": "Missing", "sources": ["irs_basis", "irs_rental", "hud_fmr"]},
        {"cells": ["Insurance, repairs and utilities", "Official public sources do not determine a private premium, repair budget, water bill or solar credit.", "Obtain separate written owner-occupied / landlord insurance quotes, inspection bids, utility bills and solar tariff documents."], "status": "Missing", "sources": ["cdi", "cslb", "water_board", "cpuc_solar"]},
        {"cells": ["Investment entry and reinvestment risk", "A 24–36 month Treasury staging plan changes exposure timing but adds reinvestment risk if yields fall; equity prices can fall during or after staging.", "Use the local-only stress tool, replace its explicit assumptions with then-current net yields, and compare crash-during-wait with crash-after-wait."], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
        {"cells": ["Long-range law and market conditions", "No official source can verify future estate thresholds, property values, insurance costs, rent or returns decades ahead.", "Re-check enacted law, official bills, valuations and quotes close to the transfer; do not extrapolate a single rate for fifty years."], "status": "Missing", "sources": ["irs_2027", "cbo_rates", "fhfa_hpi"]},
    ]
    body = callout(
        "Current answer: no path can yet be responsibly ranked",
        "The essential trust, tax-basis, estate, assessment, lease, insurance and operating-cost facts are not independently verified. The public website omits all case-specific amounts and locations to protect privacy; blanks are intentional, not zero.",
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
    body += paragraph("No invented round numbers", "This site does not invent property values, tax bills, rents, utility costs, insurance premiums or repair estimates. Any illustrative figure used only in a private working copy is rounded to the nearest ten dollars and treated as an assumption, never as evidence. Public pages leave property-specific values blank; blank means unknown, not zero.")
    return render_page(
        "index.html",
        "Decision overview",
        "A private planning framework for an anticipated trust transfer and a separate already-owned property. Locations, addresses, values, rent and expense histories are deliberately not published.",
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
        "Executive conclusion",
        "No defensible best path can be selected yet. First resolve the legal transfer and tax facts; then build after-tax cash-flow cases for Property A and Property B separately; then compare pure and mixed choices under adverse market, inflation, repair and insurance conditions.",
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
    body = callout("No winner is being published", "Each path depends on facts not established by public records in this site. A conditional recommendation should be made only after the blank evidence rows are replaced by private documents and professional calculations.", "warning")
    body += make_table("Mixed and pure paths to compare", ["Path", "Property A — anticipated trust transfer", "Property B — already owned", "Main uncertainty / risk"], rows, "The sources link to governing rules or official risk information. They do not establish whether a specific use, rent, exclusion or premium applies.")
    role_rows = [
        {"cells": ["Property A — anticipated trust transfer", "Nothing is owned yet; the asset, its basis, its assessment and the trustee's authority all depend on a transfer that has not happened. Any current occupancy, market value, tax bill or insurance premium is an assumption, not an established fact.", "Do not model A as if it were already owned. Show the pre-transfer and post-transfer states separately and label the transfer date as an open variable."], "status": "Owner-supplied", "sources": ["ca_prob160617", "ca_rtc480", "boe_prop19"]},
        {"cells": ["Property B — already owned", "The owner already holds title, basis, existing tenants and existing operating costs. Whether an owner can occupy part of it without ending an existing tenancy is a lease, local-rule and rent-law question, not a modelling convenience.", "Treat B's rent, vacancy, tenant obligations and basis as separate inputs. A mixed plan that assumes B keeps paying rent after the owner moves in must be verified, not assumed."], "status": "Owner-supplied", "sources": ["irs_rental", "ca_rent"]},
        {"cells": ["Why the distinction changes the answer", "Selling A and keeping B is a one-time capital event plus an ongoing operating asset. Living in A and renting B is two operating assets with one residence. Selling both is a full liquidation. Each carries a different tax basis, assessment history and risk profile.", "Compare paths on the same horizon, the same tax treatment and the same risk case. Mixing A's post-inheritance basis with B's historical costs silently biases the answer."], "status": "Guidance", "sources": ["irs_basis", "boe_pub29", "irs_rental"]},
    ]
    body += make_table("The ownership roles are different assets — keep them separate", ["Asset", "What is actually established", "Modelling rule"], role_rows, "Only the broad roles were supplied. Neither asset's value, basis, assessment, rent, lease, insurance or costs is verified here.")
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
    ]
    body = callout("Answers are intentionally bounded", "The only supplied case structure carried into the public site is that one property is expected through a trust and the other is already owned. No exact costs, valuations, locations, leases or estate amounts are published or inferred.", "info")
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
    body = callout("No household-specific annual dollars are published", "Publishing owner-level assessments, tax bills, expenses or projections could fingerprint a property. The public worksheet therefore leaves every private value blank. Nothing is treated as zero, and no future rate is invented.", "warning")
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
    body += paragraph("Horizon", "The transfer date is long range and intentionally not published or confirmed in this public version. CBO's cited rate outlook runs only through 2036; it cannot responsibly be extended as a fifty-year house-price, inflation, insurance or stock-return forecast. Use annual scenario rows only after private source documents and adviser-approved assumptions are available.")
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
    body = callout("No premiums or monthly cost estimates are published", "The exact quote or bill is private, provider-specific and time-sensitive. The previously supplied estimates are not reproduced or treated as verified. Obtain current written quotes and actual bills for each property's intended use.", "warning")
    body += make_table("Operating-cost inputs and evidence needed", ["Cost / income line", "Public amount", "How to verify privately"], rows)
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
    body += paragraph("Annex: the comparison premises", "A threshold comparison is only usable if five things are stated on the same line: level (estate-wide, not one asset), direction (a tax or an exclusion), unit (per estate, per person, per heir), year of death, and baseline (current law only). Anything else is a headline, not a calculation.")
    body += paragraph("Future law", "The expected transfer is decades away. Do not compound today's exclusion forward or assume it will remain in force. Re-check the Internal Revenue Code, annual IRS revenue procedures, California statutes and any enacted amendments in the actual year of death.")
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
        {"cells": ["Federal bills and proposals", "No specific pending federal proposal is incorporated into this decision framework. A bill or resolution is not current law merely because it is introduced or debated.", "Search Congress.gov near the event; confirm enactment, effective date and IRS implementation before changing a calculation."], "status": "Not verified", "sources": ["congress_legislation", "irs_estate"]},
        {"cells": ["California property-tax transfer rules", "Review RTC §§480 and 63.2, BOE guidance, any later amendments and the assessor's written determination.", "Check filing forms, value limit, occupancy, relationship and transfer date."], "status": "Guidance", "sources": ["ca_rtc480", "ca_rtc63", "boe_prop19"]},
        {"cells": ["California bills and proposals", "No specific pending California bill is relied on as law. A proposal becomes relevant only after its status, chaptering and effective date are verified.", "Search the official bill system and re-check the enacted code, regulations and BOE guidance at transfer."], "status": "Not verified", "sources": ["ca_legislation", "boe_prop19"]},
        {"cells": ["California death-transfer tax", "Current RTC §13301 and State Controller information describe the current rule; do not assume it cannot change.", "Re-check state law for the actual year of death."], "status": "Guidance", "sources": ["ca_rtc13301", "ca_death_tax"]},
        {"cells": ["Rent and tenant protections", "Statewide Civil Code rules have coverage conditions and exemptions; local rules may be more restrictive. The property's jurisdiction is intentionally not published, so a local ordinance cannot be identified here.", "Counsel should check the actual city/county code, rent registry, unit status, lease and tenant rights before occupancy or a rent change."], "status": "Missing", "sources": ["ca_rent", "ca_legislation"]},
        {"cells": ["Insurance availability and coverage", "Market conditions, underwriting, wildfire/flood risk, exclusions and reconstruction costs may change independently of taxes.", "Refresh written quotes and coverage terms; do not extrapolate an old premium."], "status": "Missing", "sources": ["cdi"]},
        {"cells": ["Investment yields and market entry", "Treasury rates are fixed at each auction for the selected security; stock prices can lose value.", "Reprice the ladder and compare reinvestment and sequence risk immediately before investment."], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
        {"cells": ["Long-run economic assumptions", "CBO's cited interest-rate horizon is 2026–2036; no cited official source provides an individual 50-year house value, insurance price, rent or return forecast.", "Use several clearly labeled stress paths; never promote a scenario into a forecast."], "status": "Guidance", "sources": ["cbo_rates", "fhfa_hpi", "bls_cpi"]},
        {"cells": ["Nov 3, 2026 tax-related statewide measures (Props 3, 40–43)", "The official titles are: 3 — extends the existing tax on high incomes for schools and health care; 40 — imposes a one-time tax on certain taxpayers; 41 — prohibits new state taxes that exclude revenue from the state spending limit and requires audits of new state special taxes; 42 — prohibits new state personal property taxes and certain retroactive state taxes; 43 — limits voters' ability to raise local government revenue. The election date (Nov 3, 2026) is before today's date (Nov 15, 2026); certified results were not read here.", "Read the certified results and each measure's full text and fiscal analysis before relying on any tax effect; a ballot title is not a legal outcome by itself."], "status": "Not verified", "sources": ["sos_ballot"]},
        {"cells": ["SF rent-control allowable increase", "The Rent Board page states a 1.6% allowable annual increase for covered units from March 1, 2026 through February 28, 2027. Secondary articles that cite a different figure are superseded by this official page.", "Re-check the Rent Board page each year; confirm whether a unit is covered before applying any increase."], "status": "Verified", "sources": ["sf_rent_board"]},
        {"cells": ["SF Rent Board 2026 notices (demolition/major renovation protections; security-deposit interest)", "The Rent Board page lists a January 23, 2026 item on tenant protections for demolition and major renovation, and a security-deposit interest change effective March 1, 2026. Their substance was not extracted into this site.", "Counsel should read the linked notice text and confirm whether it applies to the specific units before any tenant or deposit decision."], "status": "Not verified", "sources": ["sf_rent_board"]},
    ]
    body = callout("Watch enacted law, not headlines", "The pages distinguish current statutes and agency tables from bills, stress assumptions and future uncertainty. No bill or proposal is represented as current law. The inherited transfer is far in the future; refresh federal, state and actual local rules near the event.", "info")
    body += make_table("Law and market watchlist", ["Topic", "Current official baseline / proposal status", "What to re-check"], rows)
    body += paragraph("No future-year legal projection", "This site intentionally does not extrapolate federal thresholds or California property-tax allowances to a future year. Pending bills are not incorporated as law. Search the official federal and California bill systems and verify enactment and effective dates; the actual local code cannot be identified without a private jurisdiction.")
    return render_page("pages/law-watchlist.html", "Law and market watchlist", "A short list of rules and market inputs that can change the decision, without treating a proposed change or long-run projection as settled fact.", body, "LAW & PROCESS")


def build_brief() -> str:
    rows = [
        {"cells": ["Attorney / trustee", "What does the executed trust permit: who may occupy, rent or sell, when does title change, and what debts or notices apply?", "Trust, all amendments, deed, trustee authority, debt and lease documents", "Action needed"], "status": "Action needed", "sources": ["ca_prob160617", "ca_rtc480"]},
        {"cells": ["Estate attorney / CPA", "What is the whole estate's gross value, adjusted taxable gifts, deductions, and is Form 706 required or a portability election wanted?", "Private asset and debt inventory, prior gifts, valuation reports, spouse facts", "Action needed"], "status": "Action needed", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["CPA / appraiser", "What is the date-of-death value and basis, and what is the tax result if the home is sold or rented?", "Appraisal, executor basis statement, improvement and depreciation records, sale estimate", "Action needed"], "status": "Action needed", "sources": ["irs_basis", "irs_basis_pub", "irs_121"]},
        {"cells": ["Property-tax adviser", "Does an intergenerational exclusion apply, and which statements, occupancy evidence and claims are due and by when?", "Relationship, deed or trust, prior assessment, occupancy proof, exemption and claim dates", "Action needed"], "status": "Action needed", "sources": ["boe_prop19", "ca_rtc63", "ca_rtc218"]},
        {"cells": ["Landlord-tenant counsel", "Which units are legal, what do the leases require, and which mixed occupancy options are lawful while a tenancy continues?", "Permits, certificates of occupancy, leases, deposits, rent history", "Action needed"], "status": "Action needed", "sources": ["ca_rent", "hud_fmr", "irs_rental"]},
        {"cells": ["Insurance broker", "Can each intended use be insured, at what replacement cost, with which exclusions, and what is the nonrenewal fallback?", "Separate owner-occupied and landlord quotes, coverage forms, DIC or FAIR Plan options", "Action needed"], "status": "Action needed", "sources": ["cdi"]},
        {"cells": ["Contractor / inspector", "Which repairs are imminent, and what are the itemised bids?", "Inspection report and licensed bids", "Action needed"], "status": "Action needed", "sources": ["cslb"]},
        {"cells": ["Utility / solar provider", "What are the actual water and electric bills, the tariff, the export credits and the true-up date?", "Twelve to twenty-four months of bills, interconnection and tariff documents", "Action needed"], "status": "Action needed", "sources": ["water_board", "cpuc_solar"]},
        {"cells": ["Investment adviser / CPA", "What is the net investable cash after costs and tax, and how do immediate, Treasury-ladder and phased entry compare after fees and tax?", "After-tax proceeds, liquidity plan, current net yields, fee schedule, allocation policy", "Action needed"], "status": "Action needed", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
    ]
    body = callout("Meeting objective", "Leave with a written conditional recommendation that states each assumption, the source, the deadline, the tax and insurance reserve, and the specific fact that would reverse the answer. Bring the private documents; do not upload them to the public site.", "info")
    body += make_table("One-page adviser handoff checklist", ["Adviser", "Question to answer", "Private records to bring", "Status"], rows)
    body += """<section class="prose brief-block"><h2>Print settings for a true one-pager</h2><p class="table-note">This page is built for one sheet: the print stylesheet hides navigation, the sidebar, buttons and the footer beyond a single attribution line, and reduces table type to fit. Print or save as PDF in portrait with default margins. If the table spills to a second page, print the first page only for the meeting and keep the source register for the file.</p></section>"""
    body += paragraph("Decision boundary", "Property A is the anticipated trust transfer and Property B is already owned. Keep B's rent ledger, leases, assessment, basis and insurance separate from A, and test whether B can serve as a residence without assuming tenant obligations disappear. Compare live, rent, sell, mixed-occupancy and phased-investing alternatives only after counsel and the CPA confirm the legal and tax inputs.")
    body += paragraph("Privacy", "This printable sheet contains no address, locality, valuation, rent, utility amount, insurance premium, parcel identifier or household name. Completed adviser notes belong in an access-controlled file outside this repository.")
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
        ("D07", "Publish no household figure, ever, at any rounding",
         "Household amounts stay in a private file. The public site carries law, method and blank templates only.",
         "Rounding to the nearest ten dollars does not anonymise an assessment history that can be matched across years.",
         [("Privacy", "Critical"), ("Effort", "Low"), ("Privacy impact", "Protective")],
         ["github_history", "boe_pub29"]),
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
    ]
    body = callout("Privacy issue remains urgent", "The current website avoids case-specific figures and locations. The GitHub repository is public, and history cleanup has not been completed. A noindex tag and a cleaned current tree do not erase old commits, PR diffs, forks, caches or clones.", "warning")
    body += make_table("Flagged for review — unresolved items do not imply a verified answer", ["Flag", "What is unresolved", "Required action"], rows)
    scan_rows = [
        {"cells": ["F-09 — Case-derived place identifiers remain in Git history", "A read-only scan of `git rev-list --all --objects` (251 commits, 1,384 unique blobs, 380 distinct paths) found CA-ZIP-shaped five-digit patterns in 95 paths, a property city name in 109 paths, a neighbourhood name in 96 paths and one specific five-digit place identifier in 55 paths. Affected paths include `README.md`, `VERIFICATION.md`, `COORDINATION.md`, `_7adb71fc/**`, `_7eff7e24/**`, `_c07ccf45/**`, `_s95cf9249/**`, `_s9ad1da71/**` and `_research/notes.jsonl`. No matched value is reproduced here.", "Path names and match counts were checked; the values themselves are not republished. A history rewrite, repository visibility change or GitHub Support coordination requires repository-owner/admin action and cannot be safely performed from a session-scoped token on a shared default branch. Treat the historical material as exposed until that is completed."], "status": "Missing", "sources": ["github_history"]},
        {"cells": ["F-10 — Rounding is applied, not a substitute for de-identification", "The public site publishes no household amount. A prior revision of the working notes circulated rounded figures; rounding to the nearest ten dollars does not anonymise an assessment history that can be matched to a parcel across years.", "Any future publication of an amount requires rounding to the nearest ten dollars and a separate check that the value cannot be re-identified from public records."], "status": "Guidance", "sources": ["github_history", "boe_pub29"]},
        {"cells": ["F-11 — Official pages that no longer resolve", "Four previously cited URLs return 404 or redirect to an error page as of this check: the FTB gifts-and-inheritances page, the BOE county-assessor directory, the BOE Publication 801 PDF and the CPUC water-utilities page.", "None of these is used to support a rule or a number. Working alternatives are linked in their place, and the failures stay listed so they are not silently dropped."], "status": "Not verified", "sources": ["ftb_404", "boe_assessor_404", "boe_pub801_404", "cpuc_water_404"]},
        {"cells": ["F-12 — No official source covers the household's actual transfer year", "The longest official baseline cited stops in 2055 and assumes current law; the near-term baseline stops in 2036. No official source supplies a house-price, insurance, rent or portfolio return path for the household's actual year.", "Every projection beyond the published baseline is a labelled scenario with a stated assumption band, not a forecast."], "status": "Missing", "sources": ["cbo_outlook", "cbo_ltbo", "fhfa_hpi"]},
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
    ]
    body = make_table("Terms used in this workspace", ["Term", "Plain-language meaning", "Practical distinction"], rows)
    return render_page("pages/glossary.html", "Glossary", "Short definitions for the legal, tax, property and investment terms used in the decision process.", body, "EVIDENCE")


def build_sources() -> str:
    rows = []
    for key, item in SOURCES.items():
        rows.append({
            "cells": [item["label"], item["scope"], f"Direct page fetch: {CHECKED}"],
            "status": "Verified" if item["verified"] else "Not verified",
            "sources": [key],
        })
    body = callout("Source scope matters", "Every source is an official government, regulator, or platform documentation page. A link verifies only the scope shown in its description; it never verifies a private property fact. Failed fetches are included and visibly marked.", "info")
    body += make_table("Official source register", ["Source", "What it supports / does not support", "Checked"], rows)
    body += paragraph("Verification method", "Sources listed as verified were fetched directly on the check date and read for the narrow statement shown. Failed sources remain flagged rather than silently replaced with secondary material. Re-check legal text and agency guidance at the actual transfer date.")
    return render_page("pages/sources.html", "Official source register", "A direct-source ledger with retrieval date, verification status and a clear statement of each source's limits.", body, "EVIDENCE")


def build_privacy() -> str:
    rows = [
        {"cells": ["Public page content", "The active site uses Property A / Property B roles and publishes no home address, postal code, valuation, assessed-value history, rent amount, utility history, insurance premium or parcel identifier.", "The asset-role distinction is the minimum context requested for decision comparison; do not add identifying documents or amounts."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Public hosting", "GitHub Pages is a public static website. Noindex discourages search indexing but does not restrict access or make a page private.", "Never put deeds, trust papers, tax bills, leases, statements or identifiable values here."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Current branch tree", "Identified case-input, projection, and audit files have been removed from this branch's current tree. This does not erase earlier public commits or PR references.", "Do not use this public repository as a secure vault; keep private records outside GitHub."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Git history / copies", "Earlier commits and PR diffs may remain accessible; forks, cached views and clones cannot be erased by a normal cleanup commit.", "Treat historical material as exposed until an owner/admin-coordinated history-removal process and GitHub support review are complete."], "status": "Missing", "sources": ["github_history"]},
        {"cells": ["Browser controls", "The phased-investing calculator uses transient browser memory only; review choices are stored locally in this browser and are not transmitted by this static site.", "Clear browser site data to remove saved review choices; do not enter confidential values into a public computer."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Anonymized placeholders only", "Any illustrative input used privately is anonymized and labeled as an assumption; no actual name, address, postal code, valuation, rent, bill, premium or parcel identifier is published.", "Keep personal records outside this public repository; treat historical Git material as exposed until owner-admin cleanup."], "status": "Guidance", "sources": ["github_history"]},
    ]
    body = callout("Privacy warning — history is not fully scrubbed", "The repository is public. The current branch tree and generated pages are generic, but historical Git objects, earlier public PRs, forks, caches and clones may retain case-derived material. This branch cannot rewrite public main history; repository-owner/admin coordination is required. Treat prior values as exposed.", "warning")
    body += make_table("Privacy boundary and remaining exposure", ["Area", "Current state", "Safeguard / limitation"], rows)
    round_rows = [
        {"cells": ["Published amounts", "No household amount is published at all. Reinstating any amount requires prior approval and must be rounded to the nearest ten dollars before publication.", "Rounding reduces traceability; it does not anonymise an assessment history, which can still fingerprint a parcel across years."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Statutory amounts", "Only published official figures appear: federal exclusions, the $7,000 homeowners' exemption and the $250,000/$500,000 main-home exclusion.", "These are public law, not household data; they carry a source link on every row."], "status": "Verified", "sources": ["irs_estate", "irs_2027", "ca_rtc218", "irs_121"]},
        {"cells": ["Assessment history", "Assessed-value and tax-bill histories are not published in any form, rounded or not.", "A year-by-year assessment series is effectively a parcel identifier even after rounding."], "status": "Guidance", "sources": ["boe_pub29"]},
        {"cells": ["Place identifiers", "City, neighbourhood, ZIP code, street address and parcel number are all suppressed by an automated release check.", "The check fails the build on a five-digit identifier, street-address pattern, email or phone number."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Projection outputs", "No projection table or CSV is published; the site shows formulas and blank scenario columns only.", "A model output with plausible amounts can be re-identified by anyone who knows the property."], "status": "Guidance", "sources": ["irs_basis"]},
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
        "pages/questions.html": build_questions,
        "pages/projections.html": build_projections,
        "pages/property-tax.html": build_property_tax,
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
