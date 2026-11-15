#!/usr/bin/env python3
"""Build the source-linked inheritance decision workspace.

The build is static. It reads no network resource, ships no third-party asset,
and stores nothing outside the reader's own browser. Every substantive table
row carries an evidence badge and at least one official source link.

Privacy: no owner name, street address, parcel or assessor identifier, trust
name, account number or contact detail is written into any page. Working dollar
figures are rounded to the nearest ten dollars. Owner-supplied figures are
labeled as owner-supplied and are never presented as verified.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

import casedata as cd
from sources import SOURCES, CHECKED

ROOT = Path(__file__).resolve().parent.parent
SITE_TITLE = "Inheritance decision workspace"

NAV_GROUPS = [
    ("Start here", [
        ("index.html", "What changes the answer"),
        ("pages/executive-summary.html", "Executive summary"),
    ]),
    ("The decision", [
        ("pages/decision-analysis.html", "Compare eight paths"),
        ("pages/questions.html", "Questions and missing evidence"),
        ("pages/suggestions.html", "Suggestions for review"),
    ]),
    ("The numbers", [
        ("pages/projections.html", "Projections and what-if"),
        ("pages/property-tax.html", "Property tax and assessment"),
        ("pages/operating-costs.html", "Operating costs"),
    ]),
    ("Stress tests", [
        ("pages/black-swan.html", "Black swan conditions"),
        ("pages/phased-investing.html", "Treasury staging tool"),
    ]),
    ("Law and process", [
        ("pages/estate-thresholds.html", "Estate tax thresholds"),
        ("pages/inheritance-process.html", "Deadline timeline"),
        ("pages/law-watchlist.html", "Law watchlist"),
    ]),
    ("Advisers and evidence", [
        ("pages/attorney-cpa-brief.html", "Attorney and CPA brief"),
        ("pages/flagged-for-review.html", "Flagged for review"),
        ("pages/glossary.html", "Glossary"),
        ("pages/sources.html", "Official source register"),
        ("pages/privacy.html", "Privacy and limits"),
    ]),
]

EXPECTED_PAGES = [p for _, links in NAV_GROUPS for p, _ in links]


class SafeHTML(str):
    """Marker for trusted, locally generated HTML fragments."""


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def money(value: float) -> str:
    return f"${cd.money(value):,}"


def source_link(key: str) -> str:
    s = SOURCES[key]
    flag = "" if s["verified"] else ' <span class="src-warn" title="Retrieval failed or gateway only">unverified</span>'
    return (
        f'<a class="source" href="{esc(s["url"])}" title="{esc(s["scope"])}" '
        f'rel="noopener noreferrer">{esc(s["label"])}</a>{flag}'
    )


BADGE_CSS = {
    "Verified": "verified",
    "Official": "verified",
    "Historical": "verified",
    "Owner-supplied": "owner",
    "Projection": "projection",
    "Assumption": "assumption",
    "Derived": "assumption",
    "Not verified": "missing",
    "Action needed": "guidance",
    "Guidance": "guidance",
}


def badge(status: str) -> str:
    return f'<span class="badge {BADGE_CSS.get(status, "guidance")}">{esc(status)}</span>'


NUMERIC_RE = re.compile(r"^-?\$?[\d,]+(\.\d+)?%?$")


def cell(value: object, owner_figure: bool = False) -> str:
    if isinstance(value, SafeHTML):
        return f'<td class="num owner-figure">{value}</td>'
    text = str(value)
    numeric = isinstance(value, (int, float)) and not isinstance(value, bool)
    if not numeric and NUMERIC_RE.match(text.strip()):
        numeric = True
    classes = []
    if numeric:
        classes.append("num")
    if owner_figure and numeric:
        classes.append("owner-figure")
    cls = f' class="{" ".join(classes)}"' if classes else ""
    return f'<td{cls}>{esc(value)}</td>'


def make_table(title: str, headers, rows, note: str = "") -> str:
    if not rows:
        raise ValueError(f"Table {title!r} has no rows")
    head = "".join(f'<th scope="col">{esc(h)}</th>' for h in headers)
    head += '<th scope="col">Evidence</th><th scope="col">Official source</th>'
    body = []
    for row in rows:
        keys = row.get("sources", [])
        if not keys or any(k not in SOURCES for k in keys):
            raise ValueError(f"Every row in {title!r} needs registered sources; got {keys}")
        cells = "".join(
            cell(v, owner_figure=bool(row.get("owner_figures", False))) for v in row["cells"]
        )
        links = ' <span aria-hidden="true">·</span> '.join(source_link(k) for k in keys)
        body.append(f"<tr>{cells}<td>{badge(row.get('status', 'Guidance'))}</td><td>{links}</td></tr>")
    caption = f"<caption>{esc(title)}</caption>"
    note_html = f'<p class="table-note">{esc(note)}</p>' if note else ""
    return (
        f'<section class="table-section"><h2>{esc(title)}</h2>{note_html}'
        f'<div class="table-scroll" tabindex="0" role="region" aria-label="{esc(title)}">'
        f"<table>{caption}<thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"
        f"</div></section>"
    )


def callout(title: str, text: str, kind: str = "info") -> str:
    return f'<aside class="callout {esc(kind)}"><strong>{esc(title)}</strong><p>{esc(text)}</p></aside>'


def prose(title: str, *paragraphs: str) -> str:
    body = "".join(f"<p>{esc(p)}</p>" for p in paragraphs)
    return f'<section class="prose"><h2>{esc(title)}</h2>{body}</section>'


def cards(title: str, items, current: str) -> str:
    body = []
    for heading, description, target in items:
        href = root_href(current, target)
        body.append(
            f'<article class="card"><h3><a href="{esc(href)}">{esc(heading)}</a></h3>'
            f"<p>{esc(description)}</p></article>"
        )
    return f'<section class="card-section"><h2>{esc(title)}</h2><div class="card-grid">{"".join(body)}</div></section>'


def root_href(current: str, target: str) -> str:
    return target if current == "index.html" else f"../{target}"


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


def render_page(path: str, title: str, intro: str, body: str,
                eyebrow: str = "DECISION WORKSPACE", extra_class: str = "") -> str:
    is_root = path == "index.html"
    prefix = "" if is_root else "../"
    cls = "brief-page" if path == "pages/attorney-cpa-brief.html" else ""
    cls = (cls + " " + extra_class).strip()
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive"><meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="description" content="Source-linked decision workspace for an anticipated trust transfer and a separate already-owned property.">
<title>{esc(title)} · {esc(SITE_TITLE)}</title>
<link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/app.js" defer></script>
</head><body class="{esc(cls)}"><a class="skip" href="#main">Skip to content</a>
<div id="runtime-payload" hidden data-payload="{esc(cd.runtime_payload(cd.DEFAULT_INPUTS))}"></div>
<div class="layout">
<aside class="sidebar"><a class="brand" href="{prefix}index.html"><span class="brand-icon" aria-hidden="true">&#9672;</span><span>INHERITANCE<br>DECISION DESK</span></a>
<p class="sidebar-note">Property A: trust transfer<br>Property B: already owned</p>
<nav aria-label="Main navigation">{build_nav(path)}</nav>
<div class="sidebar-bottom">Anonymized · rounded to $10<br>Sources checked {CHECKED}</div></aside>
<div class="workspace"><header class="topbar"><span>RESEARCH AND DECISION SUPPORT</span><div><span class="privacy-dot" aria-hidden="true"></span> Privacy-first <button class="print-button no-print" id="print-page" type="button">Print</button></div></header>
<main id="main"><div class="page-heading"><span class="eyebrow">{esc(eyebrow)}</span><h1>{esc(title)}</h1><p class="lead">{esc(intro)}</p></div>{body}</main>
<footer><strong>Planning framework only.</strong> Not legal, tax, insurance, appraisal or investment advice. A source supports only its stated scope, never a private fact. Blank means unknown, not zero. No personal identifier is published on this site.<br>
<a href="{prefix}pages/privacy.html">Privacy and limits</a> · <a href="{prefix}pages/sources.html">Official sources</a> · <a href="{prefix}pages/flagged-for-review.html">Flagged for review</a></footer>
</div></div></body></html>'''


# ------------------------------------------------------------------ helpers
def fmt_rate(rate: float) -> str:
    return f"{rate * 100:.3f}%"


def slider(ident: str, label: str, minimum, maximum, step, value, unit: str = "") -> str:
    data_min, data_max = minimum, maximum
    return (
        f'<div class="control"><label for="{esc(ident)}">{esc(label)}'
        f' <output id="{esc(ident)}-out" for="{esc(ident)}">{esc(value)}{esc(unit)}</output></label>'
        f'<input type="range" id="{esc(ident)}" name="{esc(ident)}" min="{esc(data_min)}" '
        f'max="{esc(data_max)}" step="{esc(step)}" value="{esc(value)}"></div>'
    )


# ==========================================================================
# Page builders
# ==========================================================================
def build_index() -> str:
    s = cd.scenario(cd.DEFAULT_INPUTS)
    a = s["a"]
    inputs = cd.DEFAULT_INPUTS
    body = callout(
        "Read this first: the answer is conditional",
        "No path can be responsibly ranked until the trust terms, the transferor's occupancy at "
        "transfer, the estate inventory and the actual insurance and repair quotes exist. The "
        "figures below are the owner's own working numbers, rounded to the nearest ten dollars, "
        "combined with rules read from official pages. They are a starting model, not a conclusion.",
        "warning",
    )

    rows = [
        {
            "cells": [
                "Is the home the transferor's principal residence at transfer?",
                "Not known. The current intergenerational exclusion applies only to a principal residence of the transferor.",
                "Get a written statement of the transferor's residence status from the trustee, and review the trust's occupancy terms.",
            ],
            "status": "Action needed",
            "sources": ["rtc_63_2", "boe_prop19"],
        },
        {
            "cells": [
                "Can the home become the transferee's principal residence within one year?",
                "Not decided. The exclusion requires occupancy within one year and a homeowners' exemption filing within one year.",
                "Decide occupancy before the transfer, not after. A late decision forfeits the exclusion.",
            ],
            "status": "Action needed",
            "sources": ["rtc_63_2", "rtc_218"],
        },
        {
            "cells": [
                "What is the post-transfer assessment?",
                f"Modelled at {money(a['taxable_prop19'])} if occupied and {money(a['taxable_full'])} if not, using the {cd.DEFAULT_TRANSFER_YEAR} default year.",
                "Recompute with the actual transfer date and the then-published limit; the limit is recalculated every other February.",
            ],
            "status": "Projection",
            "sources": ["rtc_63_2", "boe_lta_2025_009"],
        },
        {
            "cells": [
                "How large is the property tax step-up?",
                f"Modelled at {money(a['tax_now'])} today rising to {money(a['tax_prop19'])} occupied or {money(a['tax_full'])} rented at the default transfer year.",
                "Confirm the tax-rate-area rate from the county; this model derives it from the owner's own bill.",
            ],
            "status": "Projection",
            "sources": ["boe_pub29", "scc_rate_unverified"],
        },
        {
            "cells": [
                "What is the federal estate tax position?",
                f"The 2026 Form 706 filing threshold is $15,000,000 and the 2027 basic exclusion is $15,480,000. Neither is an amount per beneficiary.",
                "Obtain the full estate inventory, prior adjusted taxable gifts and any portability facts from the trustee and the CPA.",
            ],
            "status": "Verified",
            "sources": ["irs_estate", "irs_2027", "irs_estate_faq"],
        },
        {
            "cells": [
                "Does California tax the inheritance?",
                "Current statute bars the state and its political subdivisions from imposing any gift, inheritance, succession, legacy, income or estate tax on a transfer by reason of death.",
                "Re-read the statute and any successor provision at the transfer date; voters and the Legislature can change it.",
            ],
            "status": "Official",
            "sources": ["rtc_13301", "ca_leg_search"],
        },
        {
            "cells": [
                "What is market rent for Property A?",
                "Not known. No rent figure is invented here.",
                "Obtain three written rent opinions for the postal area, then compare with the break-even rent on the projections page.",
            ],
            "status": "Not verified",
            "sources": ["hud_fmr", "irs_pub527"],
        },
        {
            "cells": [
                "Is insurance actually available and at what price?",
                "Not known. The owner's figure is an estimate.",
                "Obtain written owner-occupied and landlord quotes, including replacement cost, exclusions and any FAIR Plan fallback.",
            ],
            "status": "Action needed",
            "sources": ["cdi_residential"],
        },
        {
            "cells": [
                "What will the law be in the 2040s?",
                "Unknown. No official source forecasts it.",
                "Re-check the estate exclusion, the Proposition 19 limit and local tax measures close to the transfer.",
            ],
            "status": "Not verified",
            "sources": ["congress_search", "ca_leg_search", "irs_2027"],
        },
    ]
    body += make_table(
        "What would change the answer",
        ["Decision-changing fact", "What is known now", "Next evidence or decision gate"],
        rows,
        "This is the first-screen triage list. Official links establish the rule or the process shown. They do not verify private title, occupancy, cost or tax facts.",
    )

    body += '<section class="stat-grid">'
    stats = [
        ("Property A modelled value at transfer", money(a["value_at_transfer"]), "Projection"),
        ("Annual property tax if occupied", money(a["tax_prop19"]), "Projection"),
        ("Annual property tax if rented", money(a["tax_full"]), "Projection"),
        ("Annual property tax today", money(a["tax_now"]), "Derived"),
        ("Property B gross rent income", money(s["b"]["rent_income"]) + " / yr", "Owner-supplied"),
        ("Net proceeds if sold at transfer", money(s["sale"]["net_proceeds"]), "Projection"),
    ]
    for label, value, status in stats:
        body += (
            f'<article class="stat"><p class="stat-label">{esc(label)}</p>'
            f'<p class="stat-value">{esc(value)}</p>{badge(status)}</article>'
        )
    body += "</section>"

    body += callout(
        "Keep the two assets separate in every calculation",
        "Property A is an anticipated transfer that the decision maker does not own today. "
        "Property B is already owned, is the current residence, and carries its own basis, "
        "assessment and tenancies. A choice about one must never silently assume the other's "
        "basis, assessment, rent or operating cost.",
        "info",
    )

    body += cards("Use this workspace in order", [
        ("1. Resolve the questions", "Collect the trust, title, assessment, lease, insurance and utility evidence before choosing.", "pages/questions.html"),
        ("2. Compare all eight paths", "Pure and mixed paths, including the staged Treasury route, side by side.", "pages/decision-analysis.html"),
        ("3. Print the adviser brief", "A one-page sheet for the attorney and the CPA with no identifying detail on it.", "pages/attorney-cpa-brief.html"),
    ], "index.html")

    return render_page(
        "index.html",
        "What changes the answer",
        "A source-linked decision workspace for a home expected to transfer through a trust, and a "
        "separate three-unit property the decision maker already owns. Working figures are rounded "
        "to the nearest ten dollars and no personal identifier appears anywhere on this site.",
        body,
        "START HERE",
    )


def build_executive_summary() -> str:
    s = cd.scenario(cd.DEFAULT_INPUTS)
    a, b, sale = s["a"], s["b"], s["sale"]
    be_rent = cd.breakeven_rent(a["taxable_full"], cd.A_EFFECTIVE_RATE, a["operating"]["total"], cd.DEFAULT_INPUTS)

    body = prose(
        "The finding in one paragraph",
        "The single largest number in this decision is not the sale price and not the rent. It is "
        "the property tax step-up at the moment of transfer. Property A is modelled at "
        f"{money(a['value_now'])} today and about {money(a['value_at_transfer'])} at the default "
        f"transfer year of {cd.DEFAULT_TRANSFER_YEAR}. Under current rules the enrolled assessment "
        f"moves from roughly {money(a['assessed_at_transfer'])} to about {money(a['taxable_prop19'])} "
        f"if the home is occupied as a principal residence, or about {money(a['taxable_full'])} if "
        f"it is not. That carries the annual bill from about {money(a['tax_now'])} to about "
        f"{money(a['tax_prop19'])} or {money(a['tax_full'])}, a multiple of roughly "
        f"{a['tax_multiple_prop19']}x or {a['tax_multiple_full']}x. Every other choice has to be "
        "measured against that step.",
        "Property B is a different asset with different economics. It is already owned, it is the "
        f"current residence, and two of its three units produce about {money(b['rent_income'])} of "
        "gross rent a year on the owner's figures. Its enrolled assessment and therefore its bill "
        "are far lower relative to value. Property B is what makes a mixed path possible, because "
        "it lets the household keep rental income while changing how Property A is used.",
    )

    rows = [
        {
            "cells": ["Property tax step-up dominates", f"About {money(a['tax_now'])} today versus about {money(a['tax_prop19'])} occupied or {money(a['tax_full'])} rented at the default transfer year.", "Model the assessment first; the financing and rent questions come second."],
            "status": "Projection",
            "sources": ["rtc_63_2", "boe_lta_2025_009", "boe_pub29"],
        },
        {
            "cells": ["Occupancy is worth real money", "The current exclusion requires the home to be the transferor's principal residence and to become the transferee's principal residence within one year, with an exemption filing within one year.", "Treat the one-year occupancy decision as a hard deadline, not a preference."],
            "status": "Official",
            "sources": ["rtc_63_2", "boe_prop19", "rtc_218"],
        },
        {
            "cells": ["Move out later without losing the value", "The statute provides that when the exclusion stops applying, the base year value established at the change in ownership date, adjusted annually, is enrolled. Occupying for the qualifying year and renting afterwards is therefore a distinct path worth modelling.", "Confirm the wording and any county procedure with the attorney before relying on it."],
            "status": "Official",
            "sources": ["rtc_63_2"],
        },
        {
            "cells": ["Basis resets at death", "Basis of inherited property is generally fair market value at date of death, or the alternate valuation date only if a return is filed and the election is made. A sale soon after transfer therefore usually produces little taxable gain.", "Get the date-of-death valuation documented; it sets the basis for every later path."],
            "status": "Verified",
            "sources": ["irs_basis", "irs_pub523"],
        },
        {
            "cells": ["Selling is not automatically tax-free at the state level", "Current California statute bars a state inheritance or estate tax on a transfer by reason of death, but a later sale can still carry federal and state income tax consequences and local transfer charges.", "Have the CPA model the sale before assuming a net number."],
            "status": "Official",
            "sources": ["rtc_13301", "irs_basis", "irs_pub523"],
        },
        {
            "cells": ["Federal estate tax is a threshold test, not a beneficiary allowance", f"The 2026 filing threshold is $15,000,000 and the 2027 basic exclusion is $15,480,000. The test uses the gross estate plus adjusted taxable gifts and the specific gift tax exemption.", "Obtain the estate inventory rather than assuming the home alone determines the answer."],
            "status": "Verified",
            "sources": ["irs_estate", "irs_2027", "irs_estate_faq"],
        },
        {
            "cells": ["Renting Property A needs a rent number nobody has yet", f"Carrying cost if rented is modelled at about {money(a['tax_full'] + a['operating']['total'])} a year before any financing or management. The break-even gross rent, before financing, is about {money(be_rent)} a year.", "Get three written rent opinions before choosing a keep-and-rent path."],
            "status": "Projection",
            "sources": ["irs_pub527", "hud_fmr", "civ_1947_12"],
        },
        {
            "cells": ["Sequence risk is the real reason to consider staging", "The Dow did not regain its 1929 high until November 1954, about 25 years later. The S&P 500 fell 57 percent from October 2007 to March 2009 while house prices fell about 30 percent.", "Compare crash-during-wait with crash-after-entry before trusting any headline."],
            "status": "Historical",
            "sources": ["fed_1929", "fed_2008"],
        },
        {
            "cells": ["The deduction for property tax is capped", "An individual's state and local tax deduction is limited to a combined $40,000, or $20,000 if married filing separately, subject to a modified adjusted gross income limitation but not reduced below $10,000.", "Do not model the full property tax as deductible at the federal level."],
            "status": "Verified",
            "sources": ["irs_topic503"],
        },
        {
            "cells": ["Today's rules will not be the 2040s rules", "The Proposition 19 limit is recalculated every other February from the California house price index, and the federal exclusion is indexed from 2027. Neither guarantees a future amount.", "Re-read every figure at the transfer date; nothing here is a promise about future law."],
            "status": "Official",
            "sources": ["boe_lta_2025_009", "fhfa_hpi", "irs_2027"],
        },
    ]
    body += make_table(
        "Executive findings",
        ["Finding", "What the model and the statutes show", "What to do with it"],
        rows,
        "Owner-supplied figures are rounded to the nearest ten dollars. Projection rows use the default transfer year and the default growth assumptions; change them on the projections page.",
    )

    body += prose(
        "Conditional recommendation",
        "On the evidence available today, and only if the home is the transferor's principal "
        "residence at transfer, the path that preserves the most optionality is to take occupancy "
        "within the one-year window, file the homeowners' exemption, file the exclusion claim within "
        "three years, and only then decide whether to stay, rent or sell. That ordering preserves "
        "the reduced assessment while the market, the insurance market and the household's own needs "
        "become clearer. It does not require deciding now whether to keep the property for life.",
        "If the home is not the transferor's principal residence at transfer, or if occupancy within "
        "one year is not realistic, the exclusion is likely unavailable. In that case the comparison "
        "narrows to a concentrated, low-yield asset with a heavy annual bill versus selling and "
        "reinvesting, and the answer becomes much more sensitive to the reinvestment path than to "
        "the property itself.",
        "This is a conditional conclusion, not a recommendation to act. It reverses if the trust "
        "restricts occupancy, if insurance becomes unavailable at a workable price, if the estate is "
        "large enough to create a filing obligation, or if the household needs the proceeds.",
    )

    return render_page(
        "pages/executive-summary.html",
        "Executive summary",
        "The important details in one place: what drives the answer, what the statutes actually "
        "require, and what would reverse the conclusion.",
        body,
        "SUMMARY",
    )


def build_decision_analysis() -> str:
    s = cd.scenario(cd.DEFAULT_INPUTS)
    a, b, sale = s["a"], s["b"], s["sale"]
    inputs = cd.DEFAULT_INPUTS
    be_rent = cd.breakeven_rent(a["taxable_full"], cd.A_EFFECTIVE_RATE, a["operating"]["total"], inputs)
    staging_gap = sale["invested_now_end"] - sale["invested_staged_end"]

    paths = [
        {
            "id": "P1",
            "name": "Occupy Property A, keep Property B unchanged",
            "kind": "Mixed",
            "tax": money(a["tax_prop19"]),
            "income": money(b["rent_income"]),
            "risk": "Concentration in one asset plus a large fixed annual bill. Liquidity is low.",
            "reversal": "Reverses if the household cannot occupy within one year, or if insurance or the bill becomes unaffordable relative to income.",
            "sources": ["rtc_63_2", "rtc_218", "irs_topic503"],
        },
        {
            "id": "P2",
            "name": "Occupy Property A and also let the third unit of Property B",
            "kind": "Mixed",
            "tax": money(a["tax_prop19"]),
            "income": f"{money(b['rent_income'])} plus the third unit (unquoted)",
            "risk": "Adds landlord exposure at B and changes the owner-occupancy profile at B. Local rules and lawful unit status govern.",
            "reversal": "Reverses if the third unit is not lawfully lettable, or if the loss of owner-occupancy at B changes its tax or insurance treatment.",
            "sources": ["rtc_63_2", "civ_1947_12", "irs_pub527"],
        },
        {
            "id": "P3",
            "name": "Occupy for the qualifying year, then let Property A and return to Property B",
            "kind": "Mixed",
            "tax": money(a["tax_prop19"]),
            "income": "Market rent for A, unquoted",
            "risk": "Depends on the statutory rule that the base year value established at the change in ownership date, adjusted annually, is enrolled when the exclusion stops applying. Needs legal confirmation.",
            "reversal": "Reverses if counsel reads the statute differently, if the county requires continuing occupancy, or if rent does not clear the break-even.",
            "sources": ["rtc_63_2", "irs_pub527", "hud_fmr"],
        },
        {
            "id": "P4",
            "name": "Let Property A from the start, keep living at Property B",
            "kind": "Pure",
            "tax": money(a["tax_full"]),
            "income": "Market rent for A, unquoted",
            "risk": "Pays the highest annual bill and keeps the largest concentration. Break-even gross rent before financing is about " + money(be_rent) + " a year.",
            "reversal": "Reverses if market rent cannot clear break-even, or if insurance and repair reserves consume the margin.",
            "sources": ["rtc_63_2", "irs_pub527", "hud_fmr", "cdi_residential"],
        },
        {
            "id": "P5",
            "name": "Sell Property A at transfer and invest the proceeds immediately",
            "kind": "Pure",
            "tax": "None after sale",
            "income": f"{money(sale['net_proceeds'])} invested",
            "risk": "Full exposure to entry-point risk. A crash immediately after the sale is the worst case for this path.",
            "reversal": "Reverses if the household needs the housing service the property provides, or if a crash at entry would be unrecoverable within the horizon.",
            "sources": ["irs_basis", "irs_pub523", "sec_stocks", "fed_2008"],
        },
        {
            "id": "P6",
            "name": "Sell Property A, park the proceeds in Treasury bills and notes, then phase into equities",
            "kind": "Mixed",
            "tax": "None after sale",
            "income": f"{money(sale['net_proceeds'])} staged",
            "risk": f"Trades entry-point risk for reinvestment risk. On the default assumptions this path ends about {money(staging_gap)} below immediate entry if markets do not fall. It wins when the fall happens during the wait.",
            "reversal": "Reverses if yields fall while waiting, or if equities rise strongly during the staging window and never retrace.",
            "sources": ["treasury_bills", "treasury_notes", "treasury_yield", "sec_stocks"],
        },
        {
            "id": "P7",
            "name": "Sell Property B, move into Property A, invest the Property B proceeds",
            "kind": "Mixed",
            "tax": money(a["tax_prop19"]),
            "income": f"Proceeds from B, valued about {money(b['value_at_transfer'])} at transfer",
            "risk": "Gives up an income-producing asset with a low relative assessment to secure the exclusion. Concentrates further in A.",
            "reversal": "Reverses if Property B's low assessment and rental income are more valuable than the exclusion, or if the sale of B creates a large taxable gain.",
            "sources": ["rtc_63_2", "irs_pub523", "boe_pub29"],
        },
        {
            "id": "P8",
            "name": "Sell both properties and invest everything",
            "kind": "Pure",
            "tax": "None after sale",
            "income": f"About {money(sale['net_proceeds'] + b['value_at_transfer'] * (1 - inputs['selling_cost']))} invested",
            "risk": "Maximum liquidity and maximum diversification, but gives up both the housing service and the low assessed values. Fully exposed to entry-point risk.",
            "reversal": "Reverses if housing cost in the local area rises faster than the portfolio, or if the household wants a property anchor.",
            "sources": ["irs_pub523", "sec_stocks", "hud_fmr"],
        },
    ]

    rows = []
    for p in paths:
        rows.append({
            "cells": [p["id"], p["kind"], p["name"], p["tax"], p["income"], p["risk"], p["reversal"]],
            "status": "Projection",
            "sources": p["sources"],
        })
    body = make_table(
        "Eight paths, including five mixed paths",
        ["ID", "Type", "Path", "Annual property tax on A after transfer", "Income or proceeds", "Principal risk", "What would reverse it"],
        rows,
        "All dollar cells use the default transfer year and default growth assumptions. Change them on the projections page. Nothing here ranks the paths; the ranking depends on facts not yet in evidence.",
    )

    body += callout(
        "Why the mixed paths are modelled separately",
        "Forcing a choice between live, rent and sell hides the paths that actually preserve optionality. "
        "Occupying for the qualifying year and then letting the property is a different economic path "
        "from occupying permanently, and selling one asset while keeping the other is different from "
        "selling both. Each has its own tax trigger, its own liquidity profile and its own reversal condition.",
        "info",
    )

    rows2 = [
        {
            "cells": ["Carrying cost of A if occupied", money(a["carrying_total"]), f"About {money(a['carrying_monthly'])} a month", "Property tax plus the owner's water, solar credit, insurance and maintenance figures."],
            "status": "Projection",
            "sources": ["rtc_63_2", "boe_pub29", "cdi_residential"],
        },
        {
            "cells": ["Carrying cost of A if rented", money(a["tax_full"] + a["operating"]["total"]), f"About {money((a['tax_full'] + a['operating']['total']) / 12)} a month", "Same operating figures with the full reassessment and no homeowners' exemption."],
            "status": "Projection",
            "sources": ["rtc_63_2", "rtc_218"],
        },
        {
            "cells": ["Break-even gross rent for A", money(be_rent), f"About {money(be_rent / 12)} a month", "Before any financing. Includes the vacancy and management assumptions; compare against three written rent opinions."],
            "status": "Assumption",
            "sources": ["irs_pub527", "hud_fmr"],
        },
        {
            "cells": ["Property B gross rent", money(b["rent_income"]), f"About {money(b['rent_income'] / 12)} a month", "Owner-supplied figure for two of three units, grown at the rent growth assumption. Not verified against leases."],
            "status": "Owner-supplied",
            "sources": ["civ_1947_12", "irs_pub527"],
        },
        {
            "cells": ["Net proceeds if A is sold", money(sale["net_proceeds"]), "After selling costs", "Gross value less the selling cost assumption. Local transfer charges and the exact commission are not verified."],
            "status": "Assumption",
            "sources": ["irs_basis", "irs_pub523"],
        },
        {
            "cells": ["Staged versus immediate entry", money(sale["invested_staged_end"]), money(sale["invested_now_end"]), f"On the default assumptions staging ends about {money(staging_gap)} behind if markets do not fall. The gap is the price of the protection."],
            "status": "Assumption",
            "sources": ["treasury_bills", "treasury_notes", "treasury_yield"],
        },
    ]
    body += make_table(
        "Numbers the comparison depends on",
        ["Measure", "Amount", "Per month or note", "How it is built and what is missing"],
        rows2,
        "Every figure here is either an owner-supplied figure rounded to the nearest ten dollars, or arithmetic on one. None is verified against an official record.",
        )

    body += prose(
        "How to read this page",
        "The paths are not ranked because the ranking depends on facts that are not yet in evidence. "
        "Choose the reversal column first: pick the two or three paths whose reversal conditions you "
        "could actually live with, then go and get the evidence that separates them. That inverts the "
        "usual order and prevents analysing a path the trust, the county or the insurance market will "
        "not permit.",
    )
    return render_page(
        "pages/decision-analysis.html",
        "Compare eight paths",
        "Pure and mixed paths for the anticipated transfer, with the property tax treatment, the "
        "principal risk and the condition that would reverse each one.",
        body,
        "DECISION",
    )


def build_questions() -> str:
    groups = [
        ("Trust, title and timing", [
            ("Is the trust revocable, and does it become irrevocable on death?", "Not in evidence", "Read the executed trust and any amendments. Ask the trustee to confirm in writing when the trust becomes irrevocable and who the successor trustee is."),
            ("Does the trust restrict occupancy, sale or mortgaging of the home?", "Not in evidence", "Ask counsel for a written summary of trustee powers and any occupancy or distribution conditions."),
            ("Is the home the transferor's principal residence at transfer?", "Not in evidence", "This determines whether the intergenerational exclusion is available at all. Obtain a written statement from the trustee and evidence of residence."),
            ("Are there debts, liens, reverse mortgage or other encumbrances?", "Not in evidence", "Order a title report and a beneficiary demand; liens survive transfer and change the net proceeds."),
            ("What is the expected transfer window?", "Owner expects 2040 to 2050", "Treat it as a window, not a date. Recompute the model at the early and late ends before committing to any path."),
        ], ["prob_16061_7", "rtc_63_2", "boe_prop19", "irs_706_due"]),
        ("Valuation and basis", [
            ("What is the date-of-death fair market value?", "Not in evidence", "A date-of-death appraisal or a documented valuation is the single most important number; it sets basis for every later path."),
            ("Was an alternate valuation date elected?", "Not in evidence", "Only available if a federal estate return is filed and the election is made on it. Ask the executor."),
            ("Was a Form 8971 Schedule A issued to any beneficiary?", "Not in evidence", "If issued, basis may have to be reported consistently with the estate tax value."),
            ("What is the current fair market value of Property B?", "Owner estimate only", "Order an appraisal or a broker price opinion; the model uses an owner estimate."),
        ], ["irs_basis", "irs_estate_faq", "irs_pub523"]),
        ("Federal and state transfer tax", [
            ("What is the gross estate, including adjusted taxable gifts?", "Not in evidence", "The filing test adds lifetime taxable gifts to the gross estate; the home alone does not answer it. Obtain the inventory from the trustee."),
            ("Is a portability election relevant?", "Not in evidence", "A portability election is made on a timely filed return; filing can matter even below the threshold."),
            ("Will a federal estate return be required?", "Not in evidence", "Compare the gross estate plus adjusted taxable gifts with the year-of-death threshold, then confirm with the CPA."),
            ("Does California impose any inheritance or estate tax?", "Current statute says no", "Statute bars a state inheritance or estate tax on a transfer by reason of death, but it can change. Re-read at the transfer date."),
        ], ["irs_estate", "irs_2027", "irs_estate_faq", "rtc_13301"]),
        ("Property tax and assessment", [
            ("What is the tax-rate-area rate for Property A?", "Derived from the owner's bill", f"The model uses {fmt_rate(cd.A_EFFECTIVE_RATE)}, derived from the owner's own last bill. The official county rate was not retrieved."),
            ("Why is Property B's implied rate so high?", "Flagged irregularity", f"The owner's figures imply {fmt_rate(cd.B_EFFECTIVE_RATE)}, far above the 1 percent base plus voter-approved debt described by the city. The bill likely includes direct assessments or parcel taxes, or the assessment figure is not the taxable value. Reconcile against the actual bill."),
            ("What will the Proposition 19 limit be at transfer?", "Published only through February 15, 2027", f"The current amount is ${cd.PROP19_LIMIT_NOW:,}. It is recalculated every other February from the California house price index."),
            ("Is a homeowners' exemption in place at Property A today?", "Not verified", "Confirm from the current bill; it affects the derived effective rate."),
        ], ["boe_pub29", "boe_lta_2025_009", "rtc_218", "sf_gov_assess", "scc_rate_unverified"]),
        ("Operating costs and insurance", [
            ("What does insurance actually cost, and is it available?", "Owner estimate only", "Obtain written owner-occupied and landlord quotes with replacement cost, exclusions and any FAIR Plan fallback."),
            ("What is the true maintenance and repair run rate?", "Owner estimate only", "Build a reserve schedule from inspection reports and three years of actual spend, not from a rule of thumb."),
            ("Who supplies water to Property A and on what tariff?", "Not confirmed", "More than one provider serves the postal area. Read the provider and the tariff from the account or bill."),
            ("What is the solar interconnection agreement and tariff?", "Not in evidence", "Export credits depend on the tariff and the interconnection date; the equipment alone does not establish a credit."),
            ("What is the sewer charge at Property A?", "Provider identified, rate not retrieved", "The sanitary district posts its annual rate proceedings; read the current rate from the district or the bill."),
        ], ["cdi_residential", "cupertino_water_unverified", "sjwc_tariff", "cupertino_sanitary", "cpuc_solar", "cslb"]),
        ("Rental use", [
            ("What is market rent for Property A?", "Not in evidence", "Obtain three written rent opinions, then compare with the break-even rent on the projections page."),
            ("Is the third unit at Property B lawfully lettable?", "Not in evidence", "Confirm permits, unit legality and local registration before counting any additional rent."),
            ("What are the existing leases and deposit balances at Property B?", "Not in evidence", "Read the leases; lawful rent, rent cap coverage and just-cause obligations depend on them."),
            ("What rent increases are permitted on the two let units?", "Statutory cap applies, local rules may add", "The statewide cap is 5 percent plus the change in the cost of living, or 10 percent, whichever is lower, subject to exemptions and local rules."),
        ], ["civ_1947_12", "hud_fmr", "irs_pub527", "sf_gov_assess"]),
        ("Reinvestment", [
            ("What is the household's real horizon and liquidity need?", "Not stated", "A staged plan only helps if the money is not needed during the staging window. State the horizon before choosing a path."),
            ("What are current Treasury yields at the time of the decision?", "Published daily", "Read the 3-month and 2-year constant maturity rates from the Treasury par yield curve on the day of the decision."),
            ("What is the household's tax position on interest and gains?", "Not in evidence", "Treasury interest is federally taxable but exempt from state and local tax; confirm the combined effect with the CPA."),
        ], ["treasury_yield", "treasury_bills", "treasury_notes", "sec_stocks", "irs_topic503"]),
    ]

    body = callout(
        "How to use this register",
        "Each question is stated with what is currently known and a concrete way to discover the "
        "missing information. Nothing is inferred to fill a gap. Where a value is unknown it stays "
        "unknown, and the model shows the break-even or the range instead of inventing a number.",
        "info",
    )
    for title, items, sources in groups:
        rows = [{
            "cells": [q, known, action],
            "status": "Action needed" if "Not in evidence" in known or "estimate" in known.lower() or "Derived" in known or "Flagged" in known or "Not confirmed" in known else "Verified",
            "sources": sources,
        } for q, known, action in items]
        body += make_table(title, ["Question", "What is known now", "How to discover the missing information"], rows)

    return render_page(
        "pages/questions.html",
        "Questions and missing evidence",
        "Every question that needs an answer before a decision is reasonable, what is already known, "
        "and the concrete step that would produce the missing information.",
        body,
        "DECISION",
    )


def build_suggestions() -> str:
    suggestions = [
        ("S01", "Privacy", "Keep every identifying record out of this repository", "Store the deed, the trust, tax bills, leases, statements and quotes in an access-controlled vault outside GitHub. Publish only anonymized, rounded figures.", "This repository is public. A noindex tag is not access control, and history, pull requests, forks, caches and clones can retain material.", ["gh_sensitive"]),
        ("S02", "Site", "Default every table to a banded view with a one-click detail toggle", "Show ranges by default and reveal the ten-dollar-rounded working figures only when the reader asks for them.", "Reduces the chance of a casual reader linking a rounded assessment history to a public assessment roll.", ["gh_sensitive"]),
        ("S03", "Decision", "Get the trust summary in writing before modelling anything", "Ask counsel to state the trustee's powers, distribution conditions, occupancy rights and the dates that start legal clocks.", "Prevents analysing a path the trust does not permit.", ["prob_16061_7", "rtc_480"]),
        ("S04", "Site", "Add a printable evidence checklist", "One page listing every missing document with a checkbox and the official place to obtain it.", "Turns the questions page into something that can be taken to an adviser meeting.", ["rtc_480", "irs_706_due"]),
        ("S05", "Tax", "Split the three separate tax calculations", "Ask the CPA for three schedules: federal gross estate and adjusted gifts, inherited basis, and county assessment with the Proposition 19 claim.", "These are different legal calculations with different deadlines; combining them produces wrong answers.", ["irs_estate", "irs_basis", "boe_prop19"]),
        ("S06", "Tax", "Model the property tax step-up as its own line, before any financing or rent analysis", "Put the post-transfer assessment and bill at the top of every path comparison.", "On these figures the step-up dwarfs the other annual costs and drives the ranking.", ["rtc_63_2", "boe_lta_2025_009"]),
        ("S07", "Model", "Show break-even rent instead of an invented market rent", "Publish the gross rent needed to cover carrying cost, vacancy and management, and let a real quote be compared against it.", "Avoids building a decision on a fabricated yield.", ["irs_pub527", "hud_fmr"]),
        ("S08", "Model", "Keep reinvestment risk next to every staging headline", "Show the staging shortfall, the yield-fall case and the missed-rally case beside the crash-during-wait case.", "Staging changes the timing of risk; it does not make equities safe.", ["treasury_bills", "treasury_notes", "fed_1929"]),
        ("S09", "Model", "Add a crash-immediately-after-entry case to the staging tool", "Model the drop starting one month after the money reaches equities, not only during the wait.", "That is the case the staged path handles worst, and it is easy to overlook.", ["fed_2008", "sec_stocks"]),
        ("S10", "Operations", "Obtain written insurance quotes for both owner-occupied and landlord use", "Include replacement cost, exclusions, and a FAIR Plan and Differences in Conditions comparison.", "Availability and price can reverse an apparent cash-flow winner on its own.", ["cdi_residential"]),
        ("S11", "Operations", "Reconcile the water provider and tariff from an actual bill", "Read the provider name, meter size and tariff from a bill rather than assuming a provider from the postal area.", "More than one provider serves the area, and rate structures differ materially.", ["cupertino_water_unverified", "sjwc_tariff", "sfpuc_rates"]),
        ("S12", "Operations", "Read the solar interconnection agreement before counting a credit", "Confirm the tariff, the interconnection date and the true-up month.", "Export credits under net billing are usually below retail; the panels alone do not prove a credit.", ["cpuc_solar"]),
        ("S13", "Legal", "Confirm the one-year occupancy and three-year claim windows in writing", "Ask the attorney to confirm the residency and filing conditions for the intergenerational exclusion.", "Missing either window likely removes the exclusion, which is the largest single lever in this decision.", ["rtc_63_2", "boe_prop19"]),
        ("S14", "Legal", "Ask counsel to confirm the move-out-later rule before relying on it", "Confirm that when the exclusion stops applying, the base year value established at the change in ownership date, adjusted annually, is enrolled.", "If confirmed, occupying for the qualifying year and letting afterwards becomes a materially better path.", ["rtc_63_2"]),
        ("S15", "Research", "Reconcile the Property B effective rate against the actual bill", f"The owner's figures imply {fmt_rate(cd.B_EFFECTIVE_RATE)}, far above the 1 percent base plus voter-approved debt. Identify the direct assessments or parcel taxes on the bill.", "A wrong rate corrupts every projection built on it.", ["sf_gov_assess", "boe_pub29"]),
        ("S16", "Research", "Retrieve the official county tax-rate-area rate for Property A", "Ask the county for the composite rate, or read it from the bill's tax-rate area line.", "The model currently derives the rate from the owner's own bill, which is arithmetic, not an official figure.", ["scc_rate_unverified", "boe_pub29"]),
        ("S17", "Governance", "Set a dated re-verification reminder", "Re-read the federal exclusion, the Proposition 19 limit, the local ballot measures and the insurance market every year, and again at the transfer.", "A transfer expected in the 2040s cannot be decided on 2026 law.", ["irs_2027", "boe_lta_2025_009", "sos_qualified"]),
        ("S18", "Site", "Add a keyboard-first skip pattern and visible focus rings to every control", "Test the sliders and the review queue with a keyboard only, and confirm focus is always visible.", "The what-if controls are unusable without it on a keyboard or screen reader.", ["gh_sensitive"]),
        ("S19", "Decision", "Write down the reversal conditions before choosing", "For each path, record the evidence that would reverse it, and review that list at least annually.", "A recommendation that cannot name its own reversal condition is not a recommendation.", ["rtc_63_2", "irs_estate"]),
        ("S20", "Privacy", "Treat prior Git history as exposed until an owner-administered cleanup is complete", "Do not rely on this repository as a vault, and coordinate any history rewrite with the repository owner and GitHub Support.", "Earlier commits, pull-request diffs, forks, caches and clones can retain data that a normal cleanup commit does not remove.", ["gh_sensitive"]),
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
        rows.append({"cells": [ident, group, title, action, why, select], "status": "Guidance", "sources": sources})
    body = callout(
        "Nothing here is applied automatically",
        "Selecting an option records a review decision in this browser only. It changes no file, no "
        "model and no page. Use the review summary to build an agenda before any change is made.",
        "info",
    )
    body += '<p class="review-summary" id="review-summary" role="status" aria-live="polite">Loading review queue...</p>'
    body += '<p class="no-print"><button id="reset-reviews" type="button">Reset review choices</button></p>'
    body += make_table(
        "Reviewable suggestions",
        ["ID", "Category", "Suggestion", "What it would take", "Why it may improve the decision", "Review choice"],
        rows,
        "Twenty proposals covering privacy, evidence quality, modelling, operations and site usability. Each is a proposal only.",
    )
    body += prose(
        "Approval gates before anything is implemented",
        "Do not implement a financial or site change until the owner has reviewed it, the underlying "
        "private records exist, a qualified professional has confirmed the applicable law, and the "
        "model's result is reproducible from the stated assumptions. A suggestion selected here is a "
        "candidate, not an instruction.",
    )
    return render_page(
        "pages/suggestions.html",
        "Suggestions for review",
        "A selectable review queue. Choose what to investigate or adopt before anything is changed.",
        body,
        "DECISION",
    )


def build_projections() -> str:
    inputs = cd.DEFAULT_INPUTS
    s = cd.scenario(inputs)

    body = callout(
        "What-if controls stay in your browser",
        "Moving a slider recalculates the tables below in this page only. Nothing is sent anywhere, "
        "nothing is saved to a server, and the page makes no network request. Reloading restores the "
        "default assumptions.",
        "info",
    )

    controls = [
        slider("transfer_year", "Transfer year", 2040, 2050, 1, inputs["transfer_year"]),
        slider("a_appreciation", "Property A growth, percent a year", 0.0, 7.0, 0.1, round(inputs["a_appreciation"] * 100, 1), "%"),
        slider("b_appreciation", "Property B growth, percent a year", 0.0, 7.0, 0.1, round(inputs["b_appreciation"] * 100, 1), "%"),
        slider("inflation", "Inflation, percent a year", 0.0, 8.0, 0.1, round(inputs["inflation"] * 100, 1), "%"),
        slider("assessed_growth", "Assessment growth cap, percent a year", 0.0, 2.0, 0.1, round(inputs["assessed_growth"] * 100, 1), "%"),
        slider("prop19_growth", "Proposition 19 limit growth, percent a year", 0.0, 5.0, 0.1, round(inputs["prop19_growth"] * 100, 1), "%"),
        slider("insurance_growth", "Insurance growth, percent a year", 0.0, 12.0, 0.1, round(inputs["insurance_growth"] * 100, 1), "%"),
        slider("rent_growth", "Rent growth, percent a year", 0.0, 8.0, 0.1, round(inputs["rent_growth"] * 100, 1), "%"),
        slider("maintenance_a", "Property A upkeep, percent of value a year", 0.0, 3.0, 0.1, round(inputs["maintenance_a"] * 100, 1), "%"),
        slider("maintenance_b", "Property B upkeep, percent of value a year", 0.0, 3.0, 0.1, round(inputs["maintenance_b"] * 100, 1), "%"),
        slider("selling_cost", "Selling costs, percent of price", 0.0, 10.0, 0.1, round(inputs["selling_cost"] * 100, 1), "%"),
        slider("equity_return", "Equity return, percent a year", 0.0, 12.0, 0.1, round(inputs["equity_return"] * 100, 1), "%"),
        slider("treasury_yield", "Treasury yield, percent a year", 0.0, 10.0, 0.1, round(inputs["treasury_yield"] * 100, 1), "%"),
        slider("staging_months", "Staging window, months", 0, 60, 1, inputs["staging_months"]),
        slider("horizon_years", "Horizon after transfer, years", 1, 40, 1, inputs["horizon_years"]),
    ]
    body += (
        '<section class="controls-section"><h2>What-if controls</h2>'
        '<form class="controls" id="control-form">' + "".join(controls) +
        '<div class="control control-actions"><button type="reset" id="reset-controls">Reset to defaults</button></div>'
        '</form>'
        '<p class="table-note">All growth inputs are nominal and compound annually. The assessment '
        'growth cap models the annual limit on base year value increases. The Proposition 19 limit '
        'growth is an assumption: the published amount is recalculated every other February from the '
        'California house price index.</p></section>'
    )

    body += '<section class="stat-grid" id="scenario-stats">'
    stats = [
        ("Value of A at transfer", money(s["a"]["value_at_transfer"]), "Projection"),
        ("Assessment of A at transfer", money(s["a"]["assessed_at_transfer"]), "Projection"),
        ("New taxable value if occupied", money(s["a"]["taxable_prop19"]), "Projection"),
        ("New taxable value if rented", money(s["a"]["taxable_full"]), "Projection"),
        ("Annual tax if occupied", money(s["a"]["tax_prop19"]), "Projection"),
        ("Annual tax if rented", money(s["a"]["tax_full"]), "Projection"),
        ("Net proceeds if sold", money(s["sale"]["net_proceeds"]), "Projection"),
        ("Staged ending value", money(s["sale"]["invested_staged_end"]), "Assumption"),
        ("Immediate-entry ending value", money(s["sale"]["invested_now_end"]), "Assumption"),
    ]
    for label, value, status in stats:
        body += (
            f'<article class="stat" data-stat="{esc(label)}"><p class="stat-label">{esc(label)}</p>'
            f'<p class="stat-value">{esc(value)}</p>{badge(status)}</article>'
        )
    body += "</section>"

    # Property A projection rows.
    years = [2026, 2030, 2035, 2040, 2041, 2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050]
    rows_a = []
    for year in years:
        mkt = cd.market_value("A", year, inputs)
        assessed = cd.assessed_value("A", year, inputs)
        tax_pre = cd.property_tax(assessed, cd.A_EFFECTIVE_RATE, True)
        limit = cd.prop19_limit(year, inputs)
        taxable_p19 = cd.new_taxable_value(mkt, assessed, limit)
        taxable_full = cd.money(mkt)
        rows_a.append({
            "cells": [
                str(year),
                money(mkt),
                money(assessed),
                money(tax_pre) if year <= inputs["transfer_year"] else "transferred",
                money(cd.property_tax(taxable_p19, cd.A_EFFECTIVE_RATE, True)),
                money(cd.property_tax(taxable_full, cd.A_EFFECTIVE_RATE, False)),
            ],
            "status": "Projection",
            "sources": ["boe_pub29", "rtc_63_2", "boe_lta_2025_009"],
            "owner_figures": True,
        })
    body += make_table(
        "Property A: value, assessment and the two post-transfer tax paths",
        ["Year", "Market value", "Enrolled assessment", "Tax before transfer", "Tax after transfer if occupied", "Tax after transfer if rented"],
        rows_a,
        "Pre-transfer rows show the property continuing under its current assessment. After the transfer year the two columns show the intergenerational exclusion outcome and the full reassessment outcome.",
    )

    rows_b = []
    for year in years:
        mkt = cd.market_value("B", year, inputs)
        assessed = cd.assessed_value("B", year, inputs)
        rows_b.append({
            "cells": [
                str(year),
                money(mkt),
                money(assessed),
                money(cd.property_tax(assessed, cd.B_EFFECTIVE_RATE, False)),
                money(cd.b_rent_income(year, inputs)),
                money(cd.annual_operating("B", year, inputs)["total"]),
            ],
            "status": "Projection",
            "sources": ["boe_pub29", "sf_gov_assess", "irs_pub527"],
            "owner_figures": True,
        })
    body += make_table(
        "Property B: value, assessment, tax, rent and operating cost",
        ["Year", "Market value", "Enrolled assessment", "Property tax", "Gross rent, two units", "Operating cost"],
        rows_b,
        "Property B is already owned, so its assessment continues under the annual cap for as long as ownership does not change. Rent is grown at the rent growth input, which is an assumption and not a prediction of what the rent cap allows.",
    )

    body += prose(
        "How to read these two tables",
        "The two assets are deliberately separated because they have different owners, different "
        "bases and different clocks. Property A's tax line is discontinuous: it is low and rising "
        "slowly until the transfer, then it jumps once. Property B's line is continuous. A combined "
        "table would hide exactly the discontinuity that drives the decision.",
        "The assessment column for Property A is the factored base year value growing at the annual "
        "cap. It is not the market value, and the gap between the two columns is the reason the "
        "transfer matters so much.",
    )
    return render_page(
        "pages/projections.html",
        "Projections and what-if",
        "Every projection on one page with live controls. Change an assumption and the tables "
        "recalculate in your browser.",
        body,
        "NUMBERS",
    )


def build_property_tax() -> str:
    s = cd.scenario(cd.DEFAULT_INPUTS)
    a = s["a"]
    rows_hist_a = []
    prev_tax = None
    for year, tax, assessed in cd.A_HISTORY:
        delta = ""
        if prev_tax is not None and tax is not None:
            delta = f"{(tax - prev_tax) / prev_tax * 100:+.1f}%"
        if tax is not None:
            prev_tax = tax
        rows_hist_a.append({
            "cells": [str(year), money(tax) if tax is not None else "not yet billed", delta or "-", money(assessed)],
            "status": "Owner-supplied",
            "sources": ["boe_pub29", "rtc_218"],
            "owner_figures": True,
        })
    body = make_table(
        "Property A: billed tax and enrolled assessment, rounded to ten dollars",
        ["Year", "Property tax billed", "Change in bill", "Enrolled assessment"],
        rows_hist_a,
        "Owner's own tax history, rounded to the nearest ten dollars. The county assessment roll is the controlling record. The 2026 bill is shown as not yet billed because the owner did not supply a figure for it.",
    )

    rows_hist_b = []
    prev = None
    for year, tax, assessed in cd.B_HISTORY:
        delta = ""
        if prev is not None:
            delta = f"{(tax - prev) / prev * 100:+.1f}%"
        prev = tax
        rows_hist_b.append({
            "cells": [str(year), money(tax), delta, money(assessed)],
            "status": "Owner-supplied",
            "sources": ["boe_pub29", "sf_gov_assess"],
            "owner_figures": True,
        })
    body += make_table(
        "Property B: billed tax and enrolled assessment, rounded to ten dollars",
        ["Year", "Property tax billed", "Change in bill", "Enrolled assessment"],
        rows_hist_b,
        "Owner's own tax history, rounded to the nearest ten dollars. The implied rate is flagged for review on the flagged page.",
    )

    rows_rules = [
        {"cells": ["Base rate", "1 percent of assessed value, plus the rate needed to fund voter-approved bonded indebtedness", "Sets the ceiling on the ad valorem portion of the bill."],
         "status": "Official", "sources": ["boe_pub29", "sf_gov_assess"]},
        {"cells": ["Annual assessment growth", "Generally limited to 2 percent, or inflation if lower", "Explains why a long-held assessment drifts far below market value."],
         "status": "Official", "sources": ["boe_pub29", "sf_gov_assess"]},
        {"cells": ["Reassessment trigger", "Change in ownership or completion of new construction", "The transfer is the trigger; this is the moment the bill is reset."],
         "status": "Official", "sources": ["boe_pub29", "sf_gov_assess"]},
        {"cells": ["Homeowners' exemption", "$7,000 of full value, not available where the dwelling is rented, vacant or a secondary home", "Small in dollars but it is also the eligibility marker for the intergenerational exclusion."],
         "status": "Official", "sources": ["rtc_218", "rtc_63_2"]},
        {"cells": ["Intergenerational exclusion conditions", "Transferor's principal residence, transferee's principal residence within one year, exemption filing within one year, claim within three years", "Missing any one of these likely removes the exclusion."],
         "status": "Official", "sources": ["rtc_63_2", "boe_prop19"]},
        {"cells": ["Value limit formula", f"Prior taxable value plus any excess of fair market value over that value plus the adjusted amount, currently ${cd.PROP19_LIMIT_NOW:,} for transfers {cd.PROP19_LIMIT_FROM} through {cd.PROP19_LIMIT_TO}", "The adjusted amount is recalculated every other February from the California house price index."],
         "status": "Official", "sources": ["rtc_63_2", "boe_lta_2025_009", "fhfa_hpi"]},
        {"cells": ["If the exclusion later stops applying", "The base year value established at the change in ownership date, adjusted annually, is enrolled", "This is why occupying for the qualifying year and letting afterwards is a distinct path. Confirm with counsel."],
         "status": "Official", "sources": ["rtc_63_2"]},
        {"cells": ["Change-in-ownership statement", "Within 150 days after death for a transfer by reason of death outside probate, including through a trust", "A late filing can carry a penalty."],
         "status": "Official", "sources": ["rtc_480"]},
        {"cells": ["Lien date and installments", "January 1 lien date; first installment delinquent after December 10; second after April 10", "Timing matters for cash flow in the year of transfer."],
         "status": "Official", "sources": ["boe_pub29"]},
        {"cells": ["Appeal window", "Applications for reduction are filed with the clerk of the county board of supervisors, July 2 to September 15, or to November 30", "The route for disputing a reassessment the owner believes is wrong."],
         "status": "Official", "sources": ["boe_pub29"]},
    ]
    body += make_table(
        "The rules that set the bill",
        ["Rule", "What the official sources say", "Why it matters here"],
        rows_rules,
        "Statutory text and official summaries are quoted narrowly. None of it establishes this property's eligibility.",
    )

    rows_math = [
        {"cells": ["Market value at transfer", money(a["value_at_transfer"]), "Owner estimate grown at the appreciation assumption."], "status": "Projection", "sources": ["irs_basis"]},
        {"cells": ["Enrolled assessment at transfer", money(a["assessed_at_transfer"]), "Factored base year value grown at the annual cap."], "status": "Projection", "sources": ["boe_pub29"]},
        {"cells": ["Adjusted limit at transfer", money(a["prop19_limit"]), f"Published amount is ${cd.PROP19_LIMIT_NOW:,}; carrying it forward uses an assumption."], "status": "Assumption", "sources": ["boe_lta_2025_009", "fhfa_hpi"]},
        {"cells": ["Taxable value if occupied", money(a["taxable_prop19"]), "Market value less the adjusted limit, because the excess is positive."], "status": "Projection", "sources": ["rtc_63_2"]},
        {"cells": ["Taxable value if rented", money(a["taxable_full"]), "Full reassessment to market value, no homeowners' exemption."], "status": "Projection", "sources": ["rtc_63_2", "rtc_218"]},
        {"cells": ["Annual tax if occupied", money(a["tax_prop19"]), f"About {money(a['tax_prop19'] / 12)} a month, using the rate derived from the owner's own bill."], "status": "Projection", "sources": ["scc_rate_unverified", "boe_pub29"]},
        {"cells": ["Annual tax if rented", money(a["tax_full"]), f"About {money(a['tax_full'] / 12)} a month."], "status": "Projection", "sources": ["scc_rate_unverified", "boe_pub29"]},
        {"cells": ["Annual tax today", money(a["tax_now"]), f"The step-up is about {a['tax_multiple_prop19']}x if occupied and {a['tax_multiple_full']}x if rented."], "status": "Derived", "sources": ["boe_pub29"]},
    ]
    body += make_table(
        "The step-up arithmetic at the default transfer year",
        ["Line", "Amount", "How it is built"],
        rows_math,
        "Every figure on this table is arithmetic on owner-supplied values plus published statutory amounts. None of it is an official determination.",
    )

    body += callout(
        "The rate is not verified",
        f"The model derives Property A's rate of {fmt_rate(cd.A_EFFECTIVE_RATE)} from the owner's own "
        f"last bill, and Property B's rate of {fmt_rate(cd.B_EFFECTIVE_RATE)} the same way. Neither is "
        "an official county rate. Property B's implied rate is far above the 1 percent base plus "
        "voter-approved debt described by the city, which is flagged for review. Obtain the actual "
        "tax-rate-area rate from the county before relying on any projection.",
        "warning",
    )
    return render_page(
        "pages/property-tax.html",
        "Property tax and assessment",
        "The owner's billed history, the rules that set the bill, and the arithmetic of the "
        "post-transfer step-up.",
        body,
        "NUMBERS",
    )


def build_costs() -> str:
    s = cd.scenario(cd.DEFAULT_INPUTS)
    a, b = s["a"], s["b"]
    op_a, op_b = a["operating"], b["operating"]

    rows = [
        {"cells": ["Property A", "Water", f"${cd.OPERATING['a_water_low']} to ${cd.OPERATING['a_water_high']} a month", f"About {money(op_a['water'])} a year", "Owner-supplied range. The retail water provider for the parcel was not confirmed."],
         "status": "Owner-supplied", "sources": ["cupertino_water_unverified", "sjwc_tariff"]},
        {"cells": ["Property A", "Electricity, net of solar", f"About ${cd.OPERATING['a_electric_low']} to ${cd.OPERATING['a_electric_high']} a month in credit", f"About {money(abs(op_a['electric']))} a year credit", "Owner-supplied range. Export credits under net billing are usually below retail and depend on the tariff and interconnection date."],
         "status": "Owner-supplied", "sources": ["cpuc_solar"]},
        {"cells": ["Property A", "Insurance", f"About {money(cd.OPERATING['a_insurance'])} a year", f"Owner's estimate; not quoted", "The owner's figure sits near the low end of a wide market. Obtain written quotes for owner-occupied and landlord use."],
         "status": "Not verified", "sources": ["cdi_residential"]},
        {"cells": ["Property A", "Upkeep and repair", f"{cd.DEFAULT_INPUTS['maintenance_a'] * 100:.1f} percent of value a year", f"About {money(op_a['maintenance'])} a year", "Assumption only. The owner states the amount is lower than Property B. Replace with actual spend and an inspection-derived reserve."],
         "status": "Assumption", "sources": ["cslb"]},
        {"cells": ["Property B", "Water, three units", f"${cd.OPERATING['b_water_low']} to ${cd.OPERATING['b_water_high']} a month", f"About {money(op_b['water'])} a year", "Owner-supplied range. The city publishes multi-family water and wastewater schedules; the account's own usage is not known."],
         "status": "Owner-supplied", "sources": ["sfpuc_rates", "sfpuc_prop218"]},
        {"cells": ["Property B", "Electricity, common and vacant unit", f"${cd.OPERATING['b_electric_low']} to ${cd.OPERATING['b_electric_high']} a month", f"About {money(op_b['electric'])} a year", "Owner-supplied range. Not verified against bills."],
         "status": "Owner-supplied", "sources": ["cpuc_solar"]},
        {"cells": ["Property B", "Insurance", f"About {money(cd.OPERATING['b_insurance'])} a year", "Owner's estimate; not quoted", "A three-unit building occupied partly by the owner needs a landlord or mixed-use policy, not an owner-occupied one."],
         "status": "Not verified", "sources": ["cdi_residential"]},
        {"cells": ["Property B", "Upkeep and repair", f"{cd.DEFAULT_INPUTS['maintenance_b'] * 100:.1f} percent of value a year", f"About {money(op_b['maintenance'])} a year", "Assumption only, set higher than Property A because the building is older and has more units."],
         "status": "Assumption", "sources": ["cslb"]},
        {"cells": ["Property B", "Gross rent", f"{money(cd.OPERATING['b_rent_income'])} a month for {cd.OPERATING['b_rent_units_rented']} of {cd.OPERATING['b_rent_units_total']} units", f"About {money(b['rent_income'])} a year at the transfer year", "Owner-supplied figure. Not verified against leases. Future increases are subject to the statewide cap and any local rules."],
         "status": "Owner-supplied", "sources": ["civ_1947_12", "irs_pub527", "hud_fmr"]},
    ]
    body = make_table(
        "Operating costs, income and what is missing",
        ["Property", "Item", "Owner's range or figure", "Modelled annual amount", "What is missing"],
        rows,
        "Owner-supplied figures are rounded to the nearest ten dollars. Nothing here is verified against a bill, a lease, a policy or a quote.",
    )

    rows_total = [
        {"cells": ["Property A, occupied", money(a["tax_prop19"]), money(op_a["total"]), money(a["carrying_total"]), money(a["carrying_monthly"])],
         "status": "Projection", "sources": ["rtc_63_2", "boe_pub29", "cdi_residential"]},
        {"cells": ["Property A, rented", money(a["tax_full"]), money(op_a["total"]), money(a["tax_full"] + op_a["total"]), money((a["tax_full"] + op_a["total"]) / 12)],
         "status": "Projection", "sources": ["rtc_63_2", "rtc_218", "cdi_residential"]},
        {"cells": ["Property B today", money(cd.property_tax(cd.assessed_value("B", 2026, cd.DEFAULT_INPUTS), cd.B_EFFECTIVE_RATE, False)), money(op_b["total"]), money(cd.property_tax(cd.assessed_value("B", 2026, cd.DEFAULT_INPUTS), cd.B_EFFECTIVE_RATE, False) + op_b["total"]), money((cd.property_tax(cd.assessed_value("B", 2026, cd.DEFAULT_INPUTS), cd.B_EFFECTIVE_RATE, False) + op_b["total"]) / 12)],
         "status": "Projection", "sources": ["sf_gov_assess", "boe_pub29"]},
    ]
    body += make_table(
        "Annual carrying cost at the default transfer year",
        ["Case", "Property tax", "Operating cost", "Total a year", "Total a month"],
        rows_total,
        "Excludes any financing, any management fee and any vacancy. Property B's rent income is shown separately and is not netted here.",
    )

    body += callout(
        "Insurance is the largest unverified operating input",
        "The owner's insurance figure is an estimate for both properties. Official sources publish "
        "shopping tools and explain that the FAIR Plan covers only fire or lightning, internal "
        "explosion and smoke, with theft and liability requiring a separate Differences in Conditions "
        "policy. A three-unit building with a partial owner-occupancy needs a landlord or mixed-use "
        "policy. Obtain written quotes before relying on any path.",
        "warning",
    )

    rows_discover = [
        {"cells": ["Water provider for Property A", "Read the provider name, meter size and tariff from a current bill", "More than one provider serves the postal area, and tariff structures differ."], "status": "Not verified", "sources": ["cupertino_water_unverified", "sjwc_tariff"]},
        {"cells": ["Sewer charge for Property A", "Read the current rate from the sanitary district's posted rate proceedings or the bill", "The district posts annual rate hearings; the parcel's charge is not published here."], "status": "Not verified", "sources": ["cupertino_sanitary"]},
        {"cells": ["City water and sewer schedules for Property B", "Apply the published multi-family schedules to the account's actual metered usage", "The city publishes rates, not bills. Usage for three units is not known."], "status": "Not verified", "sources": ["sfpuc_rates", "sfpuc_prop218"]},
        {"cells": ["Solar tariff for Property A", "Read the interconnection agreement, the tariff name and the true-up month", "Export credits under net billing are usually below retail."], "status": "Not verified", "sources": ["cpuc_solar"]},
        {"cells": ["Insurance quotes for both properties", "Request written quotes for owner-occupied, landlord and mixed-use, with replacement cost and exclusions", "Availability and price can reverse a cash-flow winner on their own."], "status": "Not verified", "sources": ["cdi_residential"]},
        {"cells": ["Repair reserve for both properties", "Build from inspection reports plus three years of actual spend", "A percentage of value is a placeholder, not an estimate."], "status": "Not verified", "sources": ["cslb"]},
    ]
    body += make_table(
        "How to replace every estimate with evidence",
        ["Estimate to replace", "What to obtain", "Why the estimate is not good enough"],
        rows_discover,
        "Each row names an official place to start. This site does not fill any of these gaps with an inferred number.",
    )
    return render_page(
        "pages/operating-costs.html",
        "Operating costs",
        "Water, power, insurance, upkeep and rent for both properties, each labelled by how much it "
        "can be trusted.",
        body,
        "NUMBERS",
    )


def build_black_swan() -> str:
    body = callout(
        "Regimes, not averages",
        "Growth and inflation are never a constant line for fifty years. This page describes four "
        "officially documented regimes and what each one does to the decision. Every figure quoted is "
        "a historical observation read from an official history page; none is a forecast.",
        "info",
    )

    for regime in cd.REGIMES:
        rows = [{"cells": [label, value], "status": "Historical" if regime["id"] in ("r1929", "r2008") else "Verified", "sources": [src]} for label, value, src in regime["facts"]]
        body += (
            f'<section class="regime"><h2>{esc(regime["name"])} <span class="muted">({esc(regime["window"])})</span></h2>'
            + make_table(f"Official observations: {regime['name']}", ["Measure", "What the official source reports"], rows)
            + f'<p class="regime-lesson"><strong>What it teaches:</strong> {esc(regime["lesson"])}</p></section>'
        )

    rows_risk = [
        {"cells": ["Your entry point can dominate the outcome", "The Dow did not regain its 1929 high until November 1954, about 25 years after the peak", "A single lump-sum entry just before a drawn-out decline is the worst case for a sale-and-invest path."], "status": "Historical", "sources": ["fed_1929", "sec_stocks"]},
        {"cells": ["Housing and equities can fall together", "Home prices fell about 30 percent on average while the S&P 500 fell 57 percent in the same episode", "Keeping the property is not automatically a hedge against an equity crash."], "status": "Historical", "sources": ["fed_2008"]},
        {"cells": ["Inflation can run far above a planning assumption", "Twelve-month CPI reached 9.1 percent through June 2022, the largest since November 1981", "A nominal return assumption that ignores an inflation regime overstates real outcomes."], "status": "Historical", "sources": ["bls_cpi"]},
        {"cells": ["Cash yields move, in both directions", "Treasury par yields are published daily and reprice with policy", "A staging plan can look safe going in and pay much less by the time it ends, or much more."], "status": "Verified", "sources": ["treasury_yield", "treasury_bills", "treasury_notes"]},
        {"cells": ["A long flat period is a different failure from a crash", "The 1929 peak was not regained for about 25 years", "A plan that needs the money inside the flat period fails even without a further fall."], "status": "Historical", "sources": ["fed_1929"]},
        {"cells": ["Long-run projections are scenarios, not forecasts", "The ten-year budget projection publishes rate scenarios to 2036; no official source forecasts to the 2040s", "Treat the default growth assumptions as one scenario among many and re-run the model at the extremes."], "status": "Verified", "sources": ["cbo_rates", "fhfa_hpi"]},
    ]
    body += make_table(
        "What the regimes do to this decision",
        ["Risk", "Official observation", "Consequence for the choice"],
        rows_risk,
        "Historical observations describe what happened in a named episode. They do not predict the next one.",
    )

    staged = [
        {"cells": ["Stage in Treasury bills and notes for 24 to 36 months, then phase into equities over about a year", "Removes the risk that a crash lands in the first months of equity ownership", "Adds reinvestment risk: yields may be lower when the money moves, and equities may have risen during the wait"], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
        {"cells": ["Bills have terms from 4 to 52 weeks and notes include a 2-year maturity; both may be held to maturity or sold earlier", "Matched to a 24 to 36 month window without taking credit or equity risk", "Selling before maturity can produce a gain or a loss; interest is federally taxable but exempt from state and local tax"], "status": "Official", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Crash during the wait", "The strongest case for staging", "Test it on the staging tool with the 1929 and 2008 depths"], "status": "Guidance", "sources": ["fed_1929", "fed_2008"]},
        {"cells": ["Crash immediately after entry", "The weakest case for staging", "Staging does not protect against this; only a longer horizon or a lower equity weight does"], "status": "Guidance", "sources": ["fed_2008", "sec_stocks"]},
        {"cells": ["Quiet rally during the wait", "The hidden cost", "The missed compounding appears as the staging shortfall shown beside the headline on the staging tool"], "status": "Guidance", "sources": ["treasury_yield", "sec_stocks"]},
    ]
    body += make_table(
        "Where the staged path fits",
        ["Design choice", "What it buys", "What it costs"],
        staged,
        "The staging tool on the next page puts numbers on each of these cases and shows the reinvestment risk beside the headline, not below it.",
    )
    return render_page(
        "pages/black-swan.html",
        "Black swan conditions",
        "Four officially documented economic regimes, what each does to the decision, and where a "
        "staged entry fits.",
        body,
        "STRESS TESTS",
    )


def build_phased_investing() -> str:
    body = callout(
        "A stress illustration, not a backtest",
        "The calculator normalises the starting portfolio to 100 units and applies a clearly labelled "
        "synthetic path. It uses historical drawdown endpoints as the depth of the fall, not as a "
        "replay of history. It is not a forecast and not a personal investment recommendation.",
        "warning",
    )

    body += '''
<section class="calculator" id="calc">
  <h2>Staged entry versus immediate entry</h2>
  <form class="controls" id="calc-form">
    <div class="control"><label for="calc-proceeds">Starting proceeds, units<output id="calc-proceeds-out" for="calc-proceeds">100</output></label>
      <input type="range" id="calc-proceeds" min="10" max="1000" step="10" value="100"></div>
    <div class="control"><label for="calc-staging">Staging window, months<output id="calc-staging-out" for="calc-staging">30</output></label>
      <input type="range" id="calc-staging" min="0" max="60" step="1" value="30"></div>
    <div class="control"><label for="calc-phase">Phasing period into equities, months<output id="calc-phase-out" for="calc-phase">12</output></label>
      <input type="range" id="calc-phase" min="0" max="36" step="1" value="12"></div>
    <div class="control"><label for="calc-yield">Treasury yield, percent a year<output id="calc-yield-out" for="calc-yield">3.6</output></label>
      <input type="range" id="calc-yield" min="0" max="10" step="0.1" value="3.6"></div>
    <div class="control"><label for="calc-yield-after">Treasury yield after the wait, percent<output id="calc-yield-after-out" for="calc-yield-after">2.0</output></label>
      <input type="range" id="calc-yield-after" min="0" max="10" step="0.1" value="2.0"></div>
    <div class="control"><label for="calc-equity">Equity return before any fall, percent a year<output id="calc-equity-out" for="calc-equity">6.0</output></label>
      <input type="range" id="calc-equity" min="0" max="15" step="0.1" value="6.0"></div>
    <div class="control"><label for="calc-drop">Fall depth, percent<output id="calc-drop-out" for="calc-drop">57.0</output></label>
      <input type="range" id="calc-drop" min="0" max="90" step="1" value="57"></div>
    <div class="control"><label for="calc-drop-start">Fall starts at month<output id="calc-drop-start-out" for="calc-drop-start">6</output></label>
      <input type="range" id="calc-drop-start" min="0" max="60" step="1" value="6"></div>
    <div class="control"><label for="calc-drop-months">Fall unfolds over, months<output id="calc-drop-months-out" for="calc-drop-months">18</output></label>
      <input type="range" id="calc-drop-months" min="1" max="48" step="1" value="18"></div>
    <div class="control"><label for="calc-recover">Recovery after the fall, percent a year<output id="calc-recover-out" for="calc-recover">8.0</output></label>
      <input type="range" id="calc-recover" min="0" max="20" step="0.1" value="8.0"></div>
    <div class="control"><label for="calc-horizon">Horizon, years<output id="calc-horizon-out" for="calc-horizon">20</output></label>
      <input type="range" id="calc-horizon" min="1" max="40" step="1" value="20"></div>
    <div class="control control-actions"><button type="reset" id="calc-reset">Reset</button></div>
  </form>
  <div class="calc-results">
    <table class="calc-table" data-generated="client">
      <caption>Staged entry versus immediate entry under the chosen path. Values are
      arithmetic on the controls above, computed in this browser, and are not sourced figures.</caption>
      <thead><tr><th scope="col">Case</th><th scope="col">Ending value, units</th><th scope="col">Worst point, units</th><th scope="col">Difference from immediate entry</th></tr></thead>
      <tbody id="calc-rows"></tbody>
    </table>
    <div class="calc-note">
      <h3>Reinvestment risk, shown beside the headline</h3>
      <ul id="calc-risk"></ul>
    </div>
  </div>
</section>'''

    rows = [
        {"cells": ["1929 endpoint", "The Dow closed 89 percent below its peak in July 1932 and did not regain the 1929 high until November 1954", "Use as the fall depth for a drawn-out, deflationary regime."], "status": "Historical", "sources": ["fed_1929"]},
        {"cells": ["2008 endpoint", "The S&P 500 fell 57 percent from October 2007 to March 2009 while house prices fell about 30 percent", "Use as the fall depth for a shorter, sharper regime where housing also falls."], "status": "Historical", "sources": ["fed_2008"]},
        {"cells": ["Instrument terms", "Bills run 4 to 52 weeks and notes include a 2-year maturity; both may be sold before maturity", "Match the instrument to the window rather than holding longer paper than the plan needs."], "status": "Official", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Tax character of the interest", "Treasury interest is federally taxable but exempt from state and local tax", "Changes the after-tax comparison against a taxable alternative."], "status": "Official", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Yield observation point", "The par yield curve is published daily, including the 3-month and 2-year constant maturity rates", "Replace the calculator's default with the rate on the day of the decision."], "status": "Verified", "sources": ["treasury_yield"]},
        {"cells": ["Equity risk statement", "Stocks can lose value and diversification does not remove that risk", "Staging changes the timing of exposure; it does not remove it."], "status": "Verified", "sources": ["sec_stocks"]},
    ]
    body += make_table(
        "Inputs the calculator uses, and where each comes from",
        ["Input", "What the official source supports", "How to use it"],
        rows,
        "The fall depths are historical endpoints used as scenario depths. They are not a replay and not a prediction.",
    )

    body += prose(
        "How to read the three cases",
        "The calculator reports three cases side by side. Staged entry parks the proceeds in Treasury "
        "paper for the staging window, then phases into equities over the phasing period. Immediate "
        "entry puts the whole amount into equities at once. Cash simply stays in Treasury paper for "
        "the whole horizon.",
        "The fall can be timed to start during the staging window, during the phasing period, or after "
        "the money is fully invested. Run all three. The case where the fall starts during the wait is "
        "the best case for staging; the case where it starts right after entry is the worst. The "
        "quiet-rally case, where nothing falls, is the one that shows the cost of the insurance.",
    )
    return render_page(
        "pages/phased-investing.html",
        "Treasury staging tool",
        "Park the sale proceeds in 3-month to 2-year Treasury paper for 24 to 36 months, then phase "
        "into equities, and see what that does to 1929 and 2008 style entry risk.",
        body,
        "STRESS TESTS",
    )


def build_estate_thresholds() -> str:
    rows = [
        {"cells": ["2026", "$15,000,000", "$19,000", "Form 706 filing threshold for the year of death and the annual gift exclusion."], "status": "Verified", "sources": ["irs_estate"]},
        {"cells": ["2027", "$15,480,000", "$20,000", "Basic exclusion and annual gift exclusion published in IR-2026-133 on November 5, 2026."], "status": "Verified", "sources": ["irs_2027"]},
        {"cells": ["2025", "$13,990,000", "$19,000", "Shown for comparison, read from the IRS filing-threshold table."], "status": "Verified", "sources": ["irs_estate"]},
        {"cells": ["2024", "$13,610,000", "$18,000", "Shown for comparison, read from the IRS filing-threshold table."], "status": "Verified", "sources": ["irs_estate"]},
    ]
    body = make_table(
        "Federal filing threshold and exclusions by year of death",
        ["Year of death", "Form 706 threshold / basic exclusion", "Annual gift exclusion", "What the source states"],
        rows,
        "The threshold is not an amount per beneficiary. The filing test uses the gross estate plus adjusted taxable gifts and the specific gift tax exemption.",
    )

    rows2 = [
        {"cells": ["What counts", "The gross estate includes cash and securities, real estate, insurance, trusts, annuities, business interests and other assets, valued at fair market value at death", "The home is only one line in the calculation."], "status": "Official", "sources": ["irs_estate"]},
        {"cells": ["What is added back", "The value of lifetime taxable gifts beginning with gifts made in 1977 is added before the tax is computed", "Prior gifts can pull an estate over the threshold even when the remaining assets do not."], "status": "Official", "sources": ["irs_estate"]},
        {"cells": ["When it is due", "Generally nine months after the date of death, with a six-month extension only if requested before the due date and the estimated correct tax is paid before the due date", "A late request loses the extension."], "status": "Official", "sources": ["irs_706_due"]},
        {"cells": ["Portability", "Estates of decedents survived by a spouse may elect to pass unused exemption to the surviving spouse on a timely filed return", "Filing can matter below the threshold."], "status": "Official", "sources": ["irs_estate_faq", "irs_estate"]},
        {"cells": ["California", "Current statute bars the state and its political subdivisions from imposing any gift, inheritance, succession, legacy, income or estate tax on a transfer by reason of death", "This is current statute, not a promise about future law."], "status": "Official", "sources": ["rtc_13301", "ca_leg_search"]},
        {"cells": ["Basis", "Basis of inherited property is generally fair market value at date of death, or the alternate valuation date only if a return is filed and the election is made on it", "Sets the gain on any later sale."], "status": "Verified", "sources": ["irs_basis"]},
        {"cells": ["Consistent basis reporting", "A recipient who receives a Schedule A to Form 8971 may have to report basis consistent with the estate tax value", "An accuracy-related penalty can apply to an overstated basis."], "status": "Verified", "sources": ["irs_basis"]},
        {"cells": ["Deductibility of the tax itself", "Estate and inheritance taxes are listed as nondeductible, and the state and local tax deduction is capped at $40,000, or $20,000 if married filing separately, subject to a modified adjusted gross income limitation but not reduced below $10,000", "Do not model the property tax as fully deductible."], "status": "Verified", "sources": ["irs_topic503"]},
    ]
    body += make_table(
        "How the federal calculation actually works",
        ["Element", "What the official source says", "Why it matters"],
        rows2,
        "None of this determines whether this particular estate owes tax. That requires the inventory, the prior gift history and the deductions.",
    )

    rows3 = [
        {"cells": ["Threshold beyond 2027", "No official source publishes an amount for the 2040s", "Blank by design", "Re-read the current exclusion in the year of death. Indexing does not bind a future Congress."], "status": "Not verified", "sources": ["irs_2027", "congress_search"]},
        {"cells": ["State inheritance tax in the 2040s", "No official source forecasts it", "Blank by design", "Re-read the statute and the ballot measures in the year of death."], "status": "Not verified", "sources": ["rtc_13301", "ca_leg_search", "sos_qualified"]},
        {"cells": ["Local transfer charges", "Not retrieved", "Blank by design", "Obtain the county and city transfer charge schedule at the time of a sale."], "status": "Not verified", "sources": ["boe_home", "irs_topic503"]},
    ]
    body += make_table(
        "What is deliberately blank",
        ["Item", "Published figure", "Value used here", "What to do instead"],
        rows3,
        "A blank cell is an unknown, not a zero. Nothing in this site fills a gap with an inferred number.",
    )

    body += callout(
        "The inheritance is described as more than the exempt amount",
        "The owner has said the inheritance includes a considerable sum that may exceed the amount "
        "that can pass without tax. That makes the gross estate calculation, not the home, the "
        "governing question. Obtain the estate inventory and the prior gift history from the trustee "
        "before drawing any conclusion, and confirm the filing obligation with the CPA in the year of "
        "death. The published amounts above are the only amounts this site will state.",
        "warning",
    )
    return render_page(
        "pages/estate-thresholds.html",
        "Estate tax thresholds",
        "What the federal and California rules actually say, the published amounts, and what is "
        "deliberately left blank because no official source states it.",
        body,
        "LAW AND PROCESS",
    )


def build_process() -> str:
    body = callout(
        "Every clock runs from the date of death",
        "The timeline below is built from statutory deadlines and the official property tax calendar. "
        "It is a planning aid; the trustee and counsel control the actual dates and must confirm them.",
        "info",
    )
    items = []
    for i, step in enumerate(cd.PROCESS_STEPS, start=1):
        links = " ".join(source_link(k) for k in step["sources"])
        items.append(
            f'<li class="timeline-item"><span class="timeline-marker" aria-hidden="true">{i}</span>'
            f'<div class="timeline-body"><p class="timeline-offset">{esc(step["offset"])}</p>'
            f'<h3>{esc(step["title"])}</h3><p>{esc(step["detail"])}</p>'
            f'<p class="timeline-sources">{links}</p></div></li>'
        )
    body += f'<section class="timeline"><h2>Deadline timeline</h2><ol class="timeline-list">{"".join(items)}</ol></section>'

    rows = [
        {"cells": ["Step 1", "Confirm the trust and the trustee", "Read the executed trust and amendments; confirm who the successor trustee is and what powers they hold", "Nothing else can be planned until authority is confirmed."], "status": "Action needed", "sources": ["prob_16061_7"]},
        {"cells": ["Step 2", "Receive the trustee notification", "The trustee must serve it within 60 days after the trust becomes irrevocable by reason of death", "This starts the beneficiary's own review window."], "status": "Official", "sources": ["prob_16061_7"]},
        {"cells": ["Step 3", "Value the property as of the date of death", "Obtain a date-of-death valuation and keep the documentation", "It sets the basis for every later path."], "status": "Verified", "sources": ["irs_basis"]},
        {"cells": ["Step 4", "Decide occupancy before the one-year deadline", "The exclusion requires the home to become the transferee's principal residence within one year", "This is a decision, not a formality, and it must be made early."], "status": "Official", "sources": ["rtc_63_2", "boe_prop19"]},
        {"cells": ["Step 5", "File the change-in-ownership statement", "Within 150 days after death where the transfer is by reason of death outside probate, including through a trust", "A late filing can carry a penalty."], "status": "Official", "sources": ["rtc_480"]},
        {"cells": ["Step 6", "Determine whether a federal estate return is due", "Compare the gross estate plus adjusted taxable gifts with the year-of-death threshold", "Due nine months after death; a six-month extension must be requested before the due date."], "status": "Official", "sources": ["irs_estate", "irs_706_due", "irs_estate_faq"]},
        {"cells": ["Step 7", "Claim the homeowners' exemption", "File within one year of the transfer; the general exemption deadline is February 15 and a later filing can receive a reduced share by December 10", "The exemption is also the eligibility marker for the exclusion."], "status": "Official", "sources": ["rtc_63_2", "rtc_218", "boe_pub29"]},
        {"cells": ["Step 8", "File the exclusion claim", "Within three years after the transfer, or before transfer to a third party, or before the transferee stops occupying it, whichever is earliest", "A late claim may be considered but generally applies only prospectively."], "status": "Official", "sources": ["rtc_63_2", "boe_prop19"]},
        {"cells": ["Step 9", "Confirm insurance and utilities in the new owner's name", "Obtain written quotes and transfer accounts; read the solar tariff and the true-up month", "Coverage must exist from the date of transfer, not from the date of decision."], "status": "Action needed", "sources": ["cdi_residential", "cpuc_solar"]},
        {"cells": ["Step 10", "Verify the assessment on the roll", "Check the enrolled value after the transfer, and use the appeal window if it looks wrong", "The appeal window runs July 2 to September 15, or to November 30."], "status": "Official", "sources": ["boe_pub29"]},
    ]
    body += make_table(
        "The process step by step",
        ["Step", "What happens", "Deadline or action", "Why it matters"],
        rows,
        "Deadlines are statutory or published by the agency named in the source column. Individual facts can change which deadline applies.",
    )
    return render_page(
        "pages/inheritance-process.html",
        "Deadline timeline",
        "What the inheritance process looks like step by step, with every deadline traced to the "
        "statute or the official calendar that sets it.",
        body,
        "LAW AND PROCESS",
    )


def build_law_watchlist() -> str:
    rows = []
    for item in cd.LAW_WATCH:
        rows.append({
            "cells": [item["title"], item["status"], item["detail"], item["result"], item["why"]],
            "status": "Verified" if "current law" in item["status"].lower() or "every other" in item["status"].lower() or "indexed" in item["status"].lower() else "Action needed",
            "sources": item["sources"],
        })
    body = make_table(
        "Law and ballot measures to watch",
        ["Measure or rule", "Status", "What the official source says", "Reported result or current amount", "Why it matters here"],
        rows,
        "Results reported before certification are unofficial. County elections officials must report final official results by December 4, 2026 and the Secretary of State certifies on December 11, 2026.",
    )

    body += callout(
        "A proposal is not law",
        "Nothing on this page is treated as enacted unless the source says it is. Ballot results "
        "reported before certification can change during the canvass, and a bill is not law until it "
        "is chaptered and effective. Re-read every item at the transfer date.",
        "warning",
    )

    rows_how = [
        {"cells": ["Federal bills", "Search the official legislation interface for the current status of any proposal", "A proposal is not law unless enacted."], "status": "Guidance", "sources": ["congress_search"]},
        {"cells": ["California bills", "Search the official bill interface for status and chapter information", "A bill is not law unless chaptered and effective."], "status": "Guidance", "sources": ["ca_leg_search"]},
        {"cells": ["Statewide ballot measures", "Read the qualified measures list and the official results page", "Results are unofficial until the Secretary of State certifies."], "status": "Guidance", "sources": ["sos_qualified", "sos_results"]},
        {"cells": ["Property tax rules", "Read the statute and the official summaries, not secondary commentary", "A summary can lag a statutory amendment."], "status": "Guidance", "sources": ["rtc_63_2", "boe_prop19", "boe_pub29"]},
    ]
    body += make_table(
        "Where to check, and how often",
        ["Area", "Official place to check", "Caveat"],
        rows_how,
        "Set a dated reminder. A transfer expected in the 2040s cannot be decided on today's law.",
    )
    return render_page(
        "pages/law-watchlist.html",
        "Law watchlist",
        "Measures and rules that could move the answer, with official sources and the caveat that "
        "nothing is law until it is enacted and effective.",
        body,
        "LAW AND PROCESS",
    )


def build_brief() -> str:
    s = cd.scenario(cd.DEFAULT_INPUTS)
    a = s["a"]
    be_rent = cd.breakeven_rent(a["taxable_full"], cd.A_EFFECTIVE_RATE, a["operating"]["total"], cd.DEFAULT_INPUTS)
    body = f'''
<section class="brief-sheet">
<p class="brief-print-hint no-print">This page is designed to print on one sheet. No name, address, parcel number, trust name or account number appears on it.</p>
<h2>Briefing sheet for the attorney and the tax adviser</h2>
<p class="brief-meta">Prepared from owner-supplied figures rounded to the nearest ten dollars, and from statutory and official sources read on {esc(CHECKED)}. Not legal, tax or investment advice. Every question below needs a professional answer before any action.</p>

<h3>1. The two assets</h3>
<ul>
<li><strong>Property A.</strong> Anticipated transfer through a revocable trust, {esc(cd.PROPERTY_A['county'])}, {esc(cd.PROPERTY_A['area'])}. Not owned by the client today. Owner's estimate of value about {esc(money(a['value_now']))} as of November 2026. Expected transfer window 2040 to 2050.</li>
<li><strong>Property B.</strong> Already owned, {esc(cd.PROPERTY_B['county'])}, {esc(cd.PROPERTY_B['area'])}. Three units, two currently let, about {esc(money(cd.OPERATING['b_rent_income']))} a month gross on the owner's figures. Owner's estimate of value about {esc(money(cd.PROPERTY_B['value_now']))}.</li>
</ul>

<h3>2. The number that drives everything</h3>
<ul>
<li>Modelled value of Property A at the {esc(str(cd.DEFAULT_TRANSFER_YEAR))} default transfer year: about {esc(money(a['value_at_transfer']))}.</li>
<li>Enrolled assessment at that year: about {esc(money(a['assessed_at_transfer']))}.</li>
<li>New taxable value if the intergenerational exclusion applies: about {esc(money(a['taxable_prop19']))}. If it does not: about {esc(money(a['taxable_full']))}.</li>
<li>Annual property tax: about {esc(money(a['tax_now']))} today, about {esc(money(a['tax_prop19']))} if occupied, about {esc(money(a['tax_full']))} if rented. A multiple of about {esc(str(a['tax_multiple_prop19']))}x or {esc(str(a['tax_multiple_full']))}x.</li>
</ul>

<h3>3. Questions we need answered in writing</h3>
<ol>
<li>Was the home the transferor's principal residence at transfer, and can evidence of that be produced?</li>
<li>Can the transferee occupy it as a principal residence within one year, and file the homeowners' exemption within one year?</li>
<li>Does the trust permit occupancy, letting or sale, and who must consent?</li>
<li>Confirm the statutory consequence if the exclusion later stops applying: is the base year value established at the change in ownership date, adjusted annually, the value that is enrolled?</li>
<li>What is the gross estate, including adjusted taxable gifts, and is a federal estate return required?</li>
<li>What is the date-of-death valuation, and was an alternate valuation date elected on a filed return?</li>
<li>Was a Form 8971 Schedule A issued, and does a consistent-basis requirement apply?</li>
<li>What is the tax-rate-area rate, and why does Property B's bill imply about {esc(fmt_rate(cd.B_EFFECTIVE_RATE))} when the city describes 1 percent plus voter-approved debt and direct assessments?</li>
<li>What local transfer charges would apply on a sale?</li>
<li>What insurance is actually available, for owner-occupied and for landlord use, and at what price?</li>
</ol>

<h3>4. Deadlines we are tracking</h3>
<ul>
<li>Trustee notification within 60 days after the trust becomes irrevocable by reason of death.</li>
<li>Change-in-ownership statement within 150 days after death where the transfer is outside probate, including through a trust.</li>
<li>Federal estate return generally due nine months after death; a six-month extension must be requested before the due date and the estimated tax paid before it.</li>
<li>Occupancy as principal residence within one year; homeowners' exemption filed within one year.</li>
<li>Exclusion claim within three years, or before transfer to a third party, or before occupancy ends, whichever is earliest.</li>
<li>January 1 lien date; February 15 exemption deadline; December 10 and April 10 installment delinquency dates; July 2 to September 15, or November 30, appeal window.</li>
</ul>

<h3>5. Modelling notes the adviser should challenge</h3>
<ul>
<li>The effective tax rates are derived from the client's own bills, not from an official county rate. Property A about {esc(fmt_rate(cd.A_EFFECTIVE_RATE))}, Property B about {esc(fmt_rate(cd.B_EFFECTIVE_RATE))}.</li>
<li>Upkeep is modelled as a share of value ({esc(f"{cd.DEFAULT_INPUTS['maintenance_a'] * 100:.1f}")} percent for A, {esc(f"{cd.DEFAULT_INPUTS['maintenance_b'] * 100:.1f}")} percent for B). That is a placeholder, not an estimate.</li>
<li>Insurance is the client's own estimate of about {esc(money(cd.OPERATING['a_insurance']))} a year for each property and has not been quoted.</li>
<li>Selling costs are assumed at {esc(f"{cd.DEFAULT_INPUTS['selling_cost'] * 100:.1f}")} percent of price. Local transfer charges are not verified.</li>
<li>Market rent for Property A is unknown. The break-even gross rent before any financing is about {esc(money(be_rent))} a year. Please compare that with three written rent opinions.</li>
<li>The state and local tax deduction is capped at $40,000, or $20,000 if married filing separately, subject to a modified adjusted gross income limitation but not reduced below $10,000.</li>
<li>The Proposition 19 adjusted amount is ${cd.PROP19_LIMIT_NOW:,} for transfers {esc(cd.PROP19_LIMIT_FROM)} through {esc(cd.PROP19_LIMIT_TO)}, and is recalculated every other February.</li>
</ul>

<h3>6. What would change our recommendation</h3>
<ul>
<li>The home is not the transferor's principal residence at transfer.</li>
<li>Occupancy within one year is not realistic.</li>
<li>The trust restricts occupancy, letting or sale.</li>
<li>Insurance is unavailable or unaffordable.</li>
<li>Market rent cannot clear the break-even.</li>
<li>The estate crosses the filing threshold and liquidity is needed to pay tax.</li>
<li>The household needs the proceeds inside the staging window.</li>
</ul>
<p class="brief-foot">Sources for every statement on this sheet are listed on the source register. Owner-supplied amounts are rounded to the nearest ten dollars and are not verified. Blank means unknown, not zero.</p>
</section>'''
    return render_page(
        "pages/attorney-cpa-brief.html",
        "Attorney and CPA brief",
        "One printable page covering the assets, the driver, the questions, the deadlines, the "
        "assumptions to challenge, and the reversal conditions.",
        body,
        "ADVISERS",
    )


def build_flagged() -> str:
    s = cd.scenario(cd.DEFAULT_INPUTS)
    a = s["a"]
    rows = [
        {"cells": ["F01", "Property B implied effective rate is anomalous", f"The owner's figures imply about {fmt_rate(cd.B_EFFECTIVE_RATE)}, far above the 1 percent base plus voter-approved bonded indebtedness and direct assessments described by the city.", "Reconcile the bill line by line and identify the direct assessments, parcel taxes or supplemental items. Until then every Property B projection is unreliable.", "High"],
         "status": "Action needed", "sources": ["sf_gov_assess", "boe_pub29"]},
        {"cells": ["F02", "Property A tax rate is derived, not official", f"The model uses about {fmt_rate(cd.A_EFFECTIVE_RATE)}, derived from the owner's last bill. No county tax-rate-area rate was retrieved from an official page.", "Ask the county for the composite rate, or read it from the bill's tax-rate-area line.", "High"],
         "status": "Not verified", "sources": ["scc_rate_unverified", "boe_pub29"]},
        {"cells": ["F03", "Retail water provider for Property A is unconfirmed", "More than one provider serves the postal area. A filed tariff names the territory as portions of Cupertino among other cities, which does not confirm the parcel.", "Read the provider name and tariff from a current bill.", "Medium"],
         "status": "Not verified", "sources": ["cupertino_water_unverified", "sjwc_tariff"]},
        {"cells": ["F04", "Insurance premium is an estimate for both properties", "The owner's figure of about " + money(cd.OPERATING["a_insurance"]) + " a year for each property was not quoted. Property B is a three-unit building and needs a landlord or mixed-use policy, not an owner-occupied one.", "Obtain written quotes with replacement cost and exclusions, and compare against the FAIR Plan and a Differences in Conditions policy.", "High"],
         "status": "Not verified", "sources": ["cdi_residential"]},
        {"cells": ["F05", "Upkeep is a placeholder percentage, not an estimate", f"Modelled at {cd.DEFAULT_INPUTS['maintenance_a'] * 100:.1f} percent of value for A and {cd.DEFAULT_INPUTS['maintenance_b'] * 100:.1f} percent for B.", "Replace with inspection-derived reserve schedules and three years of actual spend.", "Medium"],
         "status": "Assumption", "sources": ["cslb"]},
        {"cells": ["F06", "Market rent for Property A is unknown", "No rent figure is published on this site because none has been verified.", "Obtain three written rent opinions and compare with the break-even rent.", "High"],
         "status": "Not verified", "sources": ["hud_fmr", "irs_pub527"]},
        {"cells": ["F07", "Solar credit depends on a tariff nobody has produced", "Export credits under net billing are usually below retail and depend on the tariff, the interconnection date and the true-up month.", "Produce the interconnection agreement and the tariff, and confirm the true-up month.", "Medium"],
         "status": "Not verified", "sources": ["cpuc_solar"]},
        {"cells": ["F08", "Selling costs are an assumption", f"Modelled at {cd.DEFAULT_INPUTS['selling_cost'] * 100:.1f} percent of price. Local transfer charges were not retrieved.", "Obtain the commission quote and the county and city transfer charge schedules.", "Medium"],
         "status": "Assumption", "sources": ["boe_home", "irs_pub523"]},
        {"cells": ["F09", "The Proposition 19 limit is carried forward by assumption", f"The published amount is ${cd.PROP19_LIMIT_NOW:,} for transfers {cd.PROP19_LIMIT_FROM} through {cd.PROP19_LIMIT_TO}. Carrying it to the 2040s uses an assumed rate.", "Re-read the published amount for the actual transfer period; it is recalculated every other February.", "High"],
         "status": "Assumption", "sources": ["boe_lta_2025_009", "fhfa_hpi"]},
        {"cells": ["F10", "Estate size is described but not quantified", "The owner states the inheritance includes a considerable sum that may exceed the exempt amount. No inventory was available.", "Obtain the estate inventory and the prior gift history; the home alone does not answer the filing test.", "High"],
         "status": "Not verified", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["F11", "Transfer window is an expectation, not a date", "The 2040 to 2050 window is the owner's expectation. No document establishing it was available.", "Confirm from the trust; model both the early and the late end.", "Medium"],
         "status": "Not verified", "sources": ["prob_16061_7"]},
        {"cells": ["F12", "Lawful unit count at Property B is unverified", "The owner describes three liveable units with two let. Permits, registration and lawful use were not confirmed.", "Reconcile permits, registration and leases before counting any additional rent.", "High"],
         "status": "Not verified", "sources": ["civ_1947_12", "sf_gov_assess"]},
        {"cells": ["F13", "Prior public Git history is not scrubbed", "Earlier commits, pull-request diffs, forks, caches and clones may retain material that a cleanup commit does not remove.", "Coordinate a supported history cleanup with the repository owner and GitHub Support. Do not treat this repository as a vault.", "High"],
         "status": "Action needed", "sources": ["gh_sensitive"]},
        {"cells": ["F14", "Rounded working figures remain theoretically linkable", "An assessment history rounded to ten dollars, combined with a public postal area, could in principle be matched against a county assessment roll.", "Weigh the analytical benefit against that residual risk, and consider the banded default view proposed in the suggestions queue.", "Medium"],
         "status": "Action needed", "sources": ["gh_sensitive", "boe_pub29"]},
        {"cells": ["F15", "No official source was retrieved for a local transfer charge", "A sale would likely carry county and city transfer charges. No official schedule was read.", "Obtain the schedules at the time of a sale; the site leaves the value blank rather than inferring it.", "Medium"],
         "status": "Not verified", "sources": ["boe_home"]},
    ]
    body = callout(
        "Flagged items block nothing, but they are not resolved",
        "This page lists every irregularity and every unverified value found during the build. Each "
        "one is published with its official source so it can be reviewed and closed. Nothing here is "
        "inferred to fill a gap: where a value is unknown, the model shows a break-even or a range "
        "instead.",
        "warning",
    )
    body += make_table(
        "Flagged for review",
        ["ID", "Irregularity", "What was found", "What to do", "Priority"],
        rows,
        "Priorities reflect how much the item can move the decision, not how difficult it is to resolve.",
    )
    return render_page(
        "pages/flagged-for-review.html",
        "Flagged for review",
        "Every irregularity and unverified value found during the build, with the official source "
        "that would resolve it.",
        body,
        "ADVISERS",
    )


GLOSSARY = [
    ("Alternate valuation date", "A valuation date six months after death that may be used only if a federal estate return is filed and the election is made on it.", "irs_basis"),
    ("Assessment appeal window", "The annual period, July 2 to September 15 or to November 30, during which an application for reduction in assessed value is filed with the clerk of the county board of supervisors.", "boe_pub29"),
    ("Base year value", "The assessed value established when a property changes ownership or new construction is completed. It is generally increased by no more than 2 percent a year afterwards.", "boe_pub29"),
    ("Break-even rent", "The gross annual rent needed to cover property tax, operating cost, vacancy and management before any financing. Used here instead of an invented market rent.", "irs_pub527"),
    ("Change in ownership", "The event that triggers reassessment in California. A transfer by reason of death is a change in ownership unless an exclusion applies.", "boe_pub29"),
    ("Change-in-ownership statement", "The signed statement filed with the county recorder or assessor. It is due within 150 days after death where the transfer is by reason of death outside probate, including through a trust.", "rtc_480"),
    ("Consistent basis reporting", "A rule that can require a recipient's basis to match the value finally determined for federal estate tax purposes, tied to Form 8971 Schedule A.", "irs_basis"),
    ("Equity return assumption", "The nominal annual return used to grow invested proceeds in the model. It is an input, not a forecast.", "sec_stocks"),
    ("Factored base year value", "The base year value after the annual inflation adjustments permitted by the Constitution.", "rtc_63_2"),
    ("FAIR Plan", "California's insurer of last resort. It covers fire or lightning, internal explosion and smoke, and other perils must usually be added through a Differences in Conditions policy.", "cdi_residential"),
    ("Form 706", "The United States Estate and Generation-Skipping Transfer Tax Return. Generally due nine months after death, with a six-month extension only if requested before the due date.", "irs_706_due"),
    ("Gross estate", "Everything the decedent owns or has certain interests in at death, valued at fair market value, before deductions.", "irs_estate"),
    ("Homeowners' exemption", "A $7,000 reduction in the full value of an owner-occupied dwelling. It does not apply where the dwelling is rented, vacant or a secondary home.", "rtc_218"),
    ("Intergenerational transfer exclusion", "The Proposition 19 exclusion for a transfer of a principal residence between parents and children, or in defined circumstances grandparents and grandchildren, subject to occupancy, filing and value conditions.", "rtc_63_2"),
    ("Lien date", "January 1. The date on which property is valued and exemptions are determined for the following fiscal year.", "boe_pub29"),
    ("Net billing tariff", "The solar export tariff under which credits are usually below retail rates, as opposed to the older net energy metering tariffs.", "cpuc_solar"),
    ("Phasing", "Moving staged cash into equities gradually over a stated period rather than in one transaction.", "treasury_notes"),
    ("Portability", "An election allowing a surviving spouse to use a deceased spouse's unused federal exclusion. It is made on a timely filed estate tax return.", "irs_estate_faq"),
    ("Reinvestment risk", "The risk that the yield available when staged cash is finally invested is lower than the yield available when the plan started.", "treasury_yield"),
    ("Sequence risk", "The risk that the order of returns matters, so a decline early in the period does more damage than the same decline later.", "fed_1929"),
    ("Staging", "Holding sale proceeds in short-dated government paper for a stated window before investing in equities.", "treasury_bills"),
    ("State and local tax deduction limit", "The cap on the itemized deduction for state and local taxes: $40,000, or $20,000 if married filing separately, subject to a modified adjusted gross income limitation but not reduced below $10,000.", "irs_topic503"),
    ("Step-up in basis", "The general rule that the basis of inherited property is its fair market value on the date of death rather than the decedent's original cost.", "irs_basis"),
    ("Tax-rate area", "The geographic combination of local agencies and voter-approved debt whose rates apply to a parcel. It sets the composite rate on the bill.", "boe_home"),
    ("Trustee notification", "The notice a trustee must serve within 60 days after a revocable trust becomes irrevocable by reason of death.", "prob_16061_7"),
    ("Value limit", "Under Proposition 19, the prior taxable value plus the inflation-adjusted amount. Any fair market value above it is added to the new taxable value.", "boe_lta_2025_009"),
]


def build_glossary() -> str:
    rows = [{"cells": [term, definition], "status": "Official", "sources": [src]} for term, definition, src in GLOSSARY]
    body = make_table(
        "Glossary",
        ["Term", "Meaning as used on this site"],
        rows,
        "Each definition is drawn from the official source linked beside it. Where a term is used loosely in the market, this glossary uses the statutory or official meaning.",
    )
    return render_page(
        "pages/glossary.html",
        "Glossary",
        "Plain meanings for the terms this site uses, each tied to the official source that defines it.",
        body,
        "ADVISERS",
    )


def build_sources() -> str:
    rows = []
    for key, s in SOURCES.items():
        rows.append({
            "cells": [
                s["label"],
                "Verified" if s["verified"] else "Retrieval failed or gateway only",
                s["scope"],
                f'<a href="{esc(s["url"])}" rel="noopener noreferrer">{esc(s["url"])}</a>',
            ],
            "status": "Verified" if s["verified"] else "Not verified",
            "sources": [key],
        })
    body = callout(
        "Every source was read on " + CHECKED,
        "Each page listed here was fetched and read directly during this build, and the figure or rule "
        "attributed to it was compared against the text of that page. A source supports only the "
        "scope written beside it. No source here establishes a private property's value, basis, "
        "lease, bill, premium, title, occupancy or tax position.",
        "info",
    )
    body += make_table(
        "Official source register",
        ["Source", "Retrieval status", "Scope of what it supports", "Address"],
        rows,
        "An entry marked as a retrieval failure or gateway only is never used to support a numeric claim.",
    )
    body += prose(
        "How this register is maintained",
        "Add a source only after reading the page and copying what it actually says. Write the scope "
        "as narrowly as the page supports. If a page cannot be retrieved, record it as a failure and "
        "leave the dependent value blank rather than substituting an unverified figure.",
    )
    return render_page(
        "pages/sources.html",
        "Official source register",
        "Every source cited anywhere on this site, the exact scope each one supports, and its address.",
        body,
        "ADVISERS",
    )


def build_privacy() -> str:
    rows = [
        {"cells": ["Personal identifiers", "None published", "No owner name, street address, parcel or assessor identification number, trust name, account number, date of birth, document image, email address or telephone number appears on any page.", "Keep executed documents, bills, leases, statements, quotes and inspection reports out of this repository entirely."],
         "status": "Guidance", "sources": ["gh_sensitive"]},
        {"cells": ["Location", "County and public postal area only", "The postal area is published because the utility tariffs and the insurance market research cannot be reproduced without it. No street address or parcel is published.", "If the residual linkability is unacceptable, remove the postal area and re-run the research at county level."],
         "status": "Guidance", "sources": ["gh_sensitive", "sfpuc_rates"]},
        {"cells": ["Dollar figures", "Rounded to the nearest ten dollars", "Every working dollar figure in the owner's data is rounded to the nearest ten dollars before it is written into a page.", "Rounding does not guarantee anonymity. A rounded assessment history combined with a public postal area could in principle be matched against a county assessment roll."],
         "status": "Action needed", "sources": ["gh_sensitive", "boe_pub29"]},
        {"cells": ["Evidence labelling", "Owner-supplied is never called verified", "Owner figures, derived arithmetic, projections and assumptions carry different badges and are never mixed with figures read from official pages.", "If a figure's provenance is unclear, label it unverified rather than promoting it."],
         "status": "Guidance", "sources": ["gh_sensitive"]},
        {"cells": ["Browser behaviour", "Local only", "The pages use local HTML, CSS and JavaScript only. There is no analytics, remote font, remote script, API call or form submission. Slider values and review choices stay in this browser.", "Clear site data to remove saved review choices. Do not enter confidential values on a public computer."],
         "status": "Guidance", "sources": ["gh_sensitive"]},
        {"cells": ["Search indexing", "Discouraged, not prevented", "Every page carries a noindex, nofollow and noarchive directive and a restrictive content security policy.", "A noindex directive is not access control. Anyone with the address can still read the page."],
         "status": "Guidance", "sources": ["gh_sensitive"]},
        {"cells": ["Public repository", "Currently public", "The repository is public. Earlier sessions confirmed public visibility and could not change it without repository administrator permission.", "Repository owner or administrator action is required to change visibility."],
         "status": "Action needed", "sources": ["gh_sensitive"]},
        {"cells": ["Prior Git history", "Not scrubbed", "Earlier commits, pull-request diffs, forks, caches and clones may retain material that a cleanup commit does not remove. This session performed no force-push and no history rewrite.", "Treat prior material as exposed. Coordinate a supported history cleanup with the repository owner and GitHub Support, and preserve a secure private archive first."],
         "status": "Action needed", "sources": ["gh_sensitive"]},
    ]
    body = callout(
        "Privacy is the first release gate, and it is not fully closed",
        "The published site contains no personal identifier and no unrounded private figure. It does "
        "contain rounded working figures and a public postal area, which is a real but bounded "
        "residual risk that is documented here rather than hidden. The larger unresolved exposure is "
        "the public Git history, which this branch cannot rewrite.",
        "warning",
    )
    body += make_table(
        "Privacy boundary and remaining exposure",
        ["Area", "Current state", "What this means", "Safeguard or limitation"],
        rows,
        "Read this page before sharing the site address with anyone.",
    )
    body += prose(
        "What to do if the residual risk is not acceptable",
        "Remove the postal areas and re-run the utility and insurance research at county level. "
        "Widen the rounding to bands. Or keep the analysis in a private document and publish only the "
        "generic framework. Any of these keeps the structure of the analysis while reducing what can "
        "be matched against a public record.",
        "Independently of the site, coordinate with the repository owner and GitHub Support about the "
        "public history. A clone, a fork or a cached view is not fixed by changing the pages.",
    )
    return render_page(
        "pages/privacy.html",
        "Privacy and limits",
        "What is published, what is withheld, what is rounded, and what exposure still remains.",
        body,
        "ADVISERS",
    )


BUILDERS = {
    "index.html": build_index,
    "pages/executive-summary.html": build_executive_summary,
    "pages/decision-analysis.html": build_decision_analysis,
    "pages/questions.html": build_questions,
    "pages/suggestions.html": build_suggestions,
    "pages/projections.html": build_projections,
    "pages/property-tax.html": build_property_tax,
    "pages/operating-costs.html": build_costs,
    "pages/black-swan.html": build_black_swan,
    "pages/phased-investing.html": build_phased_investing,
    "pages/estate-thresholds.html": build_estate_thresholds,
    "pages/inheritance-process.html": build_process,
    "pages/law-watchlist.html": build_law_watchlist,
    "pages/attorney-cpa-brief.html": build_brief,
    "pages/flagged-for-review.html": build_flagged,
    "pages/glossary.html": build_glossary,
    "pages/sources.html": build_sources,
    "pages/privacy.html": build_privacy,
}


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
        target.write_text(BUILDERS[path](), encoding="utf-8")
    (ROOT / "tools" / "site-manifest.json").write_text(
        json.dumps(EXPECTED_PAGES, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Built {len(EXPECTED_PAGES)} pages with source-linked tables and rounded working figures.")


if __name__ == "__main__":
    build()
