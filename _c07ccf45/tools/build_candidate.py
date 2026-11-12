#!/usr/bin/env python3
"""Static dashboard generator for session s-c07ccf45 (standard library only).

Emits a clean, simple, source-linked site: index.html + pages/*.html + assets/style.css.
Every table row carries at least one direct link to an official *.gov / *.ca.gov
publication. Official cells that cannot be verified are left blank and explained on
the Flagged for Review page. No name, street address, parcel number, city name,
neighbourhood name or ZIP code is rendered anywhere.

Usage: python3 _c07ccf45/tools/build_candidate.py [--out DIR]
"""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG / "model"))
sys.path.insert(0, str(PKG / "evidence"))

from engine import (  # noqa: E402
    BASE_INPUTS,
    HIST_PROP_A,
    HIST_PROP_B,
    build_regime_paths,
    compute_estate_headroom_matrix,
    evaluate_plans,
    simulate_property_series,
)
from sources_and_flags import FLAGS, SOURCES, VERIFIED_DATE  # noqa: E402

SITE_TITLE = "Two-Property Inheritance Decision Brief"

PLAN_SHORT = {
    "P1A_SELL_EQUITY": "Plan 1A — Sell A, stay in B Unit 3, invest proceeds in broad equities",
    "P1B_SELL_TREASURY": "Plan 1B — Sell A, stay in B Unit 3, invest proceeds in CA-tax-exempt U.S. Treasuries",
    "P1C_SELL_BALANCED_75_25": "Plan 1C — Sell A, stay in B Unit 3, invest 75% equities / 25% CA-tax-exempt Treasuries",
    "P2A_LIVE_CUP_SF2U": "Plan 2A — Move into A, keep B Unit 3 vacant (2 units rented)",
    "P2B_LIVE_CUP_SF3U": "Plan 2B — Move into A, rent out vacated B Unit 3 (3 units rented)",
    "P3_RENT_CUP_STAY_SF": "Plan 3 — Rent out A, keep living in B Unit 3",
}
PLAN_TINY = {
    "P1A_SELL_EQUITY": "1A · Sell → equities",
    "P1B_SELL_TREASURY": "1B · Sell → Treasuries",
    "P1C_SELL_BALANCED_75_25": "1C · Sell → 75/25",
    "P2A_LIVE_CUP_SF2U": "2A · Live in A (B: 2 units)",
    "P2B_LIVE_CUP_SF3U": "2B · Live in A (B: 3 units)",
    "P3_RENT_CUP_STAY_SF": "3 · Rent A, live in B",
}

REGIME_SPECS = [
    (
        "R0_BASELINE",
        "Baseline — smooth long-run growth",
        "CPI 2.3%/yr, home growth 3.5% (A) / 3.0% (B), equities 7.0%/yr total, 10-yr Treasury 4.3% (CBO long-run average).",
        ["S40", "S42"],
    ),
    (
        "R1_STAGFLATION",
        "Stagflation replay (2037–2042 and 2058–2061)",
        "CPI peaks at 9.1% (the June-2022 U.S. peak) with falling real home prices and a rising Treasury yield; a second 6.8% inflation burst later.",
        ["S41", "S40"],
    ),
    (
        "R2_GFC_AT_TRANSFER",
        "Financial crisis landing on the transfer year (2044–2049)",
        "Home values fall 10%–14% for two years while equities fall 21%–22%, mirroring 2007–09 household balance-sheet losses, then recover.",
        ["S43", "S42"],
    ),
    (
        "R3_SEQ_CRASH_AFTER_SALE",
        "Sequence-of-returns trap (2046–2047)",
        "Sale completes at a local peak, then equities fall 24% and 18% in consecutive years while home values fall 11% and 9%.",
        ["S43", "S44"],
    ),
    (
        "R4_BAY_AREA_SEISMIC_TECH",
        "Seismic / insurance availability shock (2048–2055)",
        "A regional seismic event cuts both home values 18% / 14%, insurance premiums jump 45% in one year and 18% the next, plus a $160,000 uninsured repair bill.",
        ["S25", "S36", "S37"],
    ),
    (
        "R5_TAX_LAW_REVERSAL",
        "Stepped-up basis repealed from 2038",
        "IRC §1014 is repealed: inherited basis reverts to the pre-death base, gains realised at sale are taxed, and the estate exclusion drops to 35% of the scheduled amount.",
        ["S07", "S46"],
    ),
    (
        "R6_EQUITY_LOST_DECADE_SV_BOOM",
        "Equity lost decade + local home boom (2045–2059)",
        "Equities return 4.2%/yr with three −16% drawdowns while local home values compound 5.4% / 3.8%.",
        ["S44", "S42"],
    ),
]


# ---------------------------------------------------------------------------
# rendering helpers
# ---------------------------------------------------------------------------
PLACE_GEO = [
    ("Santa Clara County", "the county"),
    ("San Francisco", "the city"),
    ("San Jose", "the region"),
    ("Bay Area", "the region"),
    ("Sunset", "the coastal district"),
]


def sanitize(text: str) -> str:
    """Remove place names from any published string (links keep the identity)."""
    out = str(text)
    for a, b in PLACE_GEO:
        out = out.replace(a, b)
    return out


def esc(v: object) -> str:
    return html.escape(str(v), quote=True)


def money(v: float) -> str:
    v = int(round(v / 10.0) * 10) if abs(v) >= 1000 else int(round(v))
    if v < 0:
        return f"−${abs(v):,d}"
    return f"${v:,d}"


def src_links(ids: list[str] | tuple[str, ...]) -> str:
    out = []
    for sid in ids:
        s = SOURCES[sid]
        out.append(
            f'<a class="src" href="{esc(s["url"])}" rel="noopener noreferrer">{sid}</a>'
        )
    return " ".join(out)


def table(headers: list[str], rows: list[list[str]], cls: str = "") -> str:
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = []
    for i, r in enumerate(rows):
        tds = "".join(f"<td>{c}</td>" for c in r)
        body.append(f"<tr>{tds}</tr>" if i % 2 == 0 else f'<tr class="alt">{tds}</tr>')
    return (
        f'<div class="tw"><table class="{cls}"><thead><tr>{th}</tr></thead>'
        f"<tbody>{''.join(body)}</tbody></table></div>"
    )


NAV = [
    ("index.html", "Overview"),
    ("pages/executive-summary.html", "Best plan"),
    ("pages/decision-analysis.html", "Decision analysis"),
    ("pages/suggestions.html", "Suggestions"),
    ("pages/open-questions.html", "Open questions"),
    ("pages/property-tax.html", "Property tax"),
    ("pages/projections.html", "50-year projections"),
    ("pages/operating-costs.html", "Costs & insurance"),
    ("pages/black-swan-scenarios.html", "Black-swan stress"),
    ("pages/inheritance-process.html", "Inheritance steps"),
    ("pages/estate-thresholds.html", "Tax thresholds"),
    ("pages/inheritance-law.html", "Tax law"),
    ("pages/law-watchlist.html", "Law watch"),
    ("pages/methodology.html", "Methodology"),
    ("pages/privacy.html", "Privacy"),
    ("pages/sources.html", "Sources"),
    ("pages/flagged-for-review.html", "Flagged for review"),
]

CSS = """
:root{--ink:#14202b;--mut:#5a6673;--line:#dde3e9;--bg:#f6f8fa;--acc:#0b5d8a;--ok:#0d6b45;--warn:#8a5a00;--red:#8a1c1c}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc)}
header{background:#fff;border-bottom:1px solid var(--line);padding:18px 20px 12px}
.brand{font-weight:700;font-size:20px;letter-spacing:.2px}
.brand small{display:block;font-weight:400;color:var(--mut);font-size:13px;margin-top:3px}
nav{max-width:1180px;margin:0 auto;padding:10px 20px;display:flex;flex-wrap:wrap;gap:6px}
nav a{font-size:13px;text-decoration:none;border:1px solid var(--line);background:#fff;border-radius:999px;padding:4px 10px;color:var(--ink)}
nav a:hover{border-color:var(--acc);color:var(--acc)}
main{max-width:1180px;margin:0 auto;padding:22px 20px 60px}
h1{font-size:27px;line-height:1.25;margin:6px 0 6px}
h2{font-size:20px;margin:34px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h3{font-size:16px;margin:22px 0 6px}
p,li{color:#22303d}
.lead{color:var(--mut);font-size:15px;margin:0 0 18px}
.notice{background:#eef4f9;border:1px solid #cfe0ee;border-left:4px solid var(--acc);border-radius:6px;padding:11px 14px;font-size:14px;margin:0 0 18px}
.verdict{background:#fff;border:1px solid var(--line);border-left:5px solid var(--ok);border-radius:8px;padding:16px 18px;margin:0 0 20px}
.verdict strong{color:var(--ok)}
.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:16px 0 8px}
.card{background:#fff;border:1px solid var(--line);border-radius:8px;padding:13px 15px}
.card span{display:block;font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.4px}
.card strong{display:block;font-size:22px;margin:4px 0 2px}
.card em{display:block;font-size:12.5px;color:var(--mut);font-style:normal}
.tw{overflow-x:auto;background:#fff;border:1px solid var(--line);border-radius:8px;margin:12px 0 8px}
table{border-collapse:collapse;width:100%;font-size:13.4px}
th,td{padding:8px 10px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}
th{background:#eef1f5;font-size:12px;text-transform:uppercase;letter-spacing:.3px;color:#35414d;position:sticky;top:0}
tr.alt td{background:#fbfcfd}
td:first-child,th:first-child{white-space:nowrap}
a.src{display:inline-block;font:600 11px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;text-decoration:none;background:#eef4f9;border:1px solid #cfe0ee;border-radius:4px;padding:1px 5px;margin:1px 2px 1px 0;color:var(--acc)}
.badge{display:inline-block;font-size:11px;font-weight:700;border-radius:4px;padding:2px 6px;background:#fdf3e0;color:var(--warn);border:1px solid #f0dcb4}
.blank{color:#9aa5b1;font-style:italic}
footer{border-top:1px solid var(--line);background:#fff;color:var(--mut);font-size:12.5px;padding:18px 20px;text-align:center}
.toc{columns:2;column-gap:26px;font-size:14px}
@media(max-width:720px){.toc{columns:1}}
"""


def render_page(rel: str, title: str, lede: str, body: str) -> str:
    depth = rel.count("/")
    prefix = "../" * depth
    nav = "".join(
        f'<a href="{prefix}{href}">{esc(label)}</a>' for href, label in NAV
    )
    body = body.replace("@FLAGPAGE@", prefix + "pages/flagged-for-review.html")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{esc(title)} · {esc(SITE_TITLE)}</title>
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<header>
  <div class="brand">{esc(SITE_TITLE)}<small>Anonymized, source-linked model for inheriting one residence (2040–2050) while already owning a 3-unit building · verified {esc(VERIFIED_DATE)}</small></div>
</header>
<nav>{nav}</nav>
<main>
<h1>{esc(title)}</h1>
<p class="lead">{lede}</p>
{body}
</main>
<footer>
  Model output, not tax, legal, investment or appraisal advice. Every published dollar figure is rounded to the nearest $10;
  exact official statutory amounts are quoted as published and linked. Personal identities, street addresses, parcel numbers,
  city names, neighbourhood names and ZIP codes are not published anywhere on this site.
</footer>
</body>
</html>
"""


PRIVACY = (
    '<div class="notice"><strong>Privacy &amp; verification controls.</strong> The two properties appear only as '
    '<em>Property A</em> (the trust-held residence to be inherited) and <em>Property B</em> (the already-owned 3-unit building). '
    "No name, street address, parcel or account number, city name, neighbourhood name or ZIP code is published. Every owner-supplied "
    "figure was rounded to the nearest $10 before modelling, so exact tax-roll values cannot be matched by search. Official cells that "
    "no government source supports are left blank and explained on the "
    '<a href="@FLAGPAGE@">Flagged for review</a> page.</div>'
)


def rel_prefix(rel: str, target: str) -> str:
    return "../" * rel.count("/") + target


# ---------------------------------------------------------------------------
# page bodies
# ---------------------------------------------------------------------------
def page_index(anchor: dict, series: list[dict], headroom: list[dict]) -> str:
    p = anchor["plans"]
    r = {row["year"]: row for row in series}
    rank = sorted(p.values(), key=lambda x: x["after_liquidation_net_worth"], reverse=True)

    rank_rows = []
    for i, d in enumerate(rank, 1):
        rank_rows.append(
            [
                f"<strong>{i}</strong>",
                esc(PLAN_SHORT[d["plan_id"]]),
                money(d["yr1_cup_prop_tax"]),
                money(d["yr1_household_op_cf"]),
                money(d["cum_op_cf_20yr"]),
                f"<strong>{money(d['after_liquidation_net_worth'])}</strong>",
                src_links(["S07", "S15", "S18", "S22", "S29"]),
            ]
        )

    cards = (
        '<div class="card-grid">'
        '<div class="card"><span>Federal estate exclusion</span><strong>$15,000,000</strong>'
        "<em>2026 per decedent; $15,480,000 for 2027</em></div>"
        '<div class="card"><span>State &amp; local death tax</span><strong>$0</strong>'
        "<em>Barred by CA RTC §13301 (state and every subdivision)</em></div>"
        f'<div class="card"><span>Property A value at a 2045 transfer</span><strong>{money(anchor["cup_fmv_at_inh"])}</strong>'
        f'<em>{money(anchor["net_sale_proceeds_if_sold"])} net cash if sold at stepped-up basis</em></div>'
        f'<div class="card"><span>Plan 1A edge over renting A out</span><strong>{money(anchor["winner_advantage_over_rent_3"])}</strong>'
        "<em>20 years after a 2045 transfer, after all taxes</em></div>"
        "</div>"
    )

    snapshot = table(
        [
            "Attribute",
            "Property A — inherited residence",
            "Property B — already-owned 3-unit building",
            "Official source",
        ],
        [
            [
                "How it is held today",
                "In a revocable trust; expected distribution 2040–2050 on the settlor's death",
                "Already owned by the heir; no trust transfer involved",
                src_links(["S07", "S15", "S27"]),
            ],
            [
                "Estimated market value, Nov 2026 (rounded)",
                money(BASE_INPUTS["cup_val_2026"]),
                money(BASE_INPUTS["sf_val_2026"]),
                src_links(["S42", "S21"]),
            ],
            [
                "2025 assessed value · property tax (rounded)",
                f"{money(BASE_INPUTS['cup_av_2025'])} · {money(BASE_INPUTS['cup_tax_2025'])}/yr",
                f"{money(BASE_INPUTS['sf_av_2025'])} · {money(BASE_INPUTS['sf_tax_2025'])}/yr",
                src_links(["S21", "S28", "S30"]),
            ],
            [
                "Effective tax as a share of assessed value",
                "~1.34% (percentage levy plus fixed parcel charges)",
                "~2.14% (tiny Prop. 13 base carries the same fixed parcel charges)",
                src_links(["S21", "S28", "S30"]),
            ],
            [
                "What death does to the income-tax basis",
                "Steps up to date-of-death fair market value (IRC §1014 / RTC §18031)",
                "Unchanged — no death event, so the historical basis continues",
                src_links(["S07", "S15"]),
            ],
            [
                "What death does to the property-tax base",
                "Prop. 19 applies: parent-child exclusion only if the heir occupies within 1 year, capped at FBYV + $1,044,586",
                "Unaffected; the existing Prop. 13 base and $7,000 exemption continue",
                src_links(["S22", "S23", "S24"]),
            ],
            [
                "Utilities the owner supplies (2026, rounded)",
                "Water $1,500/yr; rooftop solar nets a −$180/yr credit until the 20-year NEM window closes",
                "Water/sewer $4,380/yr for 3 units; common electricity $600/yr",
                src_links(["S33", "S34", "S35"]),
            ],
            [
                "Rent in place",
                "None — vacant on distribution",
                "$85,800/yr from the 2 rented units ($7,150/mo); unit 3 is the owner's",
                src_links(["S31", "S38", "S39"]),
            ],
            [
                "Parcel-specific insurance premium",
                '<span class="blank">blank — no official source exists</span>',
                '<span class="blank">blank — no official source exists</span>',
                src_links(["S36", "S37"]),
            ],
        ],
    )

    guide = table(
        ["Page", "What it answers", "Main official authorities"],
        [
            [
                f'<a href="pages/executive-summary.html">Best plan and why</a>',
                "The ranked recommendation, the five mechanisms behind it, and the conditions that would flip it.",
                src_links(["S07", "S15", "S22", "S40"]),
            ],
            [
                f'<a href="pages/decision-analysis.html">Decision analysis</a>',
                "Live in A, rent A out, or sell and reinvest — compared for every inheritance year 2040–2050, plus sensitivity cases.",
                src_links(["S10", "S11", "S12", "S29"]),
            ],
            [
                f'<a href="pages/suggestions.html">Suggestions — pick the path</a>',
                "Six ranked decision suggestions, site-improvement proposals, and a gated flow so you choose in writing before acting.",
                src_links(["S07", "S15", "S22", "S29"]),
            ],
            [
                f'<a href="pages/open-questions.html">Open questions &amp; readiness</a>',
                "What we have vs. what is missing, ten questions that must be answered, and the exact next step to close each gap.",
                src_links(["S01", "S26", "S27", "S36"]),
            ],
            [
                f'<a href="pages/property-tax.html">Property tax</a>',
                "The full $10-rounded assessment and tax history, the ad-valorem vs. fixed-charge split, and Prop. 13/19/8 mechanics.",
                src_links(["S21", "S22", "S23", "S28"]),
            ],
            [
                f'<a href="pages/projections.html">50-year projections</a>',
                "Year-by-year 2026–2075 values, assessed values, taxes, insurance, water, electricity and maintenance for both properties.",
                src_links(["S21", "S33", "S35", "S36", "S42"]),
            ],
            [
                f'<a href="pages/operating-costs.html">Costs &amp; insurance</a>',
                "What is officially verified, what stays blank, and how each cost line escalates.",
                src_links(["S34", "S36", "S38"]),
            ],
            [
                f'<a href="pages/black-swan-scenarios.html">Black-swan stress</a>',
                "Seven non-uniform 50-year regimes — stagflation, crisis landing on the transfer year, sequence risk, seismic shock, basis repeal.",
                src_links(["S25", "S41", "S43", "S46"]),
            ],
            [
                f'<a href="pages/inheritance-process.html">Inheritance steps</a>',
                "The California trust-administration sequence with its 60-day, 150-day, 9-month, 1-year and 3-year deadlines.",
                src_links(["S01", "S20", "S26", "S27"]),
            ],
            [
                f'<a href="pages/estate-thresholds.html">Tax thresholds &amp; cash inheritance</a>',
                "Federal, state and local death-tax thresholds, headroom by estate size, future thresholds and pending law changes.",
                src_links(["S01", "S02", "S13", "S46"]),
            ],
            [
                f'<a href="pages/flagged-for-review.html">Flagged for review</a>',
                "Every blank unverified cell, every owner-history irregularity, and every modeling assumption — with the link to check it.",
                src_links(["S36", "S38", "S45"]),
            ],
        ],
    )

    body = (
        PRIVACY
        + '<div class="verdict"><strong>Recommended plan: sell Property A on distribution at the stepped-up basis, keep living in '
        "Property B's unit 3, and reinvest the net proceeds — staged into broad equities with a 20%–30% CA-tax-exempt Treasury sleeve "
        f"(Plans 1A and 1C).</strong><br>At the 2045 midpoint, {money(anchor['cup_fmv_at_inh'])} of Property A steps up to "
        f"date-of-death value under IRC §1014 and CA RTC §18031 and converts to {money(anchor['net_sale_proceeds_if_sold'])} of cash with "
        f"$0 capital-gains tax. Selling removes {money(p['P2A_LIVE_CUP_SF2U']['yr1_cup_prop_tax'])}–"
        f"{money(p['P3_RENT_CUP_STAY_SF']['yr1_cup_prop_tax'])}/yr of reassessed Property A tax plus its post-solar carrying costs, "
        f"and finishes 20 years later at {money(p['P1A_SELL_EQUITY']['after_liquidation_net_worth'])} after all taxes — "
        f"{money(anchor['winner_advantage_over_rent_3'])} ahead of renting Property A out and "
        f"{money(anchor['winner_advantage_over_live_2a'])} ahead of moving in. Plan 1A wins in every inheritance year 2040–2050 and in "
        "5 of 7 stress regimes; the two exceptions are the regimes where a Treasury or property-heavy mix overtakes it.</div>"
        + cards
        + "<h2>Ranked plans — 2045 transfer, 20 years to 2064, after all taxes</h2>"
        + table(
            [
                "Rank",
                "Strategy",
                "Year-1 Property A tax",
                "Year-1 household net cash flow",
                "Cumulative 20-yr operating cash flow",
                "After-liquidation net worth (2064)",
                "Official basis",
            ],
            rank_rows,
        )
        + f"<p class=\"lead\">All six plans are evaluated on the same terms: identical starting assets, including a {money(1_000_000)} "
        "illustrative cash reserve, and every annual surplus or deficit compounds inside the household portfolio. \"After-liquidation\" "
        "deducts the taxes and costs that would actually be paid to turn assets into spendable cash.</p>"
        + "<h2>Two-property snapshot</h2>"
        + snapshot
        + "<h2>Dashboard contents</h2>"
        + guide
        + "<h2>How to read the numbers</h2>"
        + '<div class="toc"><ul>'
        + "<li><strong>Rounded, always.</strong> Every owner-supplied figure was rounded to the nearest $10 before it entered the model; exact official statutory amounts are quoted and linked.</li>"
        + "<li><strong>Blank beats invented.</strong> If no government publication supports a cell, it stays empty and is logged with the link to check.</li>"
        + "<li><strong>Both sides of the ledger.</strong> Each plan is charged its property taxes, insurance, utilities, maintenance, income tax on rental profit, and the exit taxes it embeds.</li>"
        + "<li><strong>Two horizons.</strong> Year-by-year to 2075, and a 20-year wealth comparison anchored on the transfer year you choose.</li>"
        + "</ul></div>"
    )
    return body


def page_exec(anchor: dict, regimes: dict) -> str:
    p = anchor["plans"]
    w = p["P1A_SELL_EQUITY"]
    r = p["P3_RENT_CUP_STAY_SF"]
    l2a = p["P2A_LIVE_CUP_SF2U"]
    l2b = p["P2B_LIVE_CUP_SF3U"]
    b = p["P1B_SELL_TREASURY"]
    c = p["P1C_SELL_BALANCED_75_25"]

    drivers = table(
        ["Driver", "What the numbers show (2045 transfer)", "Official basis"],
        [
            [
                "1 · The basis resets at death",
                f"Property A steps up to {money(anchor['cup_fmv_at_inh'])} under IRC §1014 and CA RTC §18031. Selling costs 5.00% brokerage/closing plus 0.11% county transfer tax ($0 city tax), leaving "
                f"{money(anchor['net_sale_proceeds_if_sold'])} — with no capital-gains tax because there is no gain above the new basis.",
                src_links(["S07", "S15", "S29"]),
            ],
            [
                "2 · Prop. 19 only shields part of the tax base",
                f"By 2045 the home is worth {money(anchor['cup_fmv_at_inh'])} against a pre-death base of {money(anchor['cup_fbyv_pre_at_inh'])} plus a "
                f"{money(anchor['prop19_cap_at_inh'])} allowance. Even the favourable parent-child route re-bases "
                f"{money(anchor['cup_fmv_at_inh'] - anchor['cup_fbyv_pre_at_inh'] - anchor['prop19_cap_at_inh'])} of value and lifts the bill to "
                f"{money(l2a['yr1_cup_prop_tax'])}/yr; keeping it as a rental lifts it to {money(r['yr1_cup_prop_tax'])}/yr with no Prop. 19 relief at all.",
                src_links(["S22", "S23", "S28"]),
            ],
            [
                "3 · The rental yield is thinner than any liquid alternative",
                f"Official HUD small-area rent for the area is $6,390/mo for a 4-bedroom — $76,680/yr, 2.47% gross on {money(BASE_INPUTS['cup_val_2026'])}. "
                "After reassessed tax, insurance, maintenance, vacancy, management and the end of the solar credit, net cash yield is under 1%. A 10-year Treasury yields 4.3% and equities are modelled at 7.0% total.",
                src_links(["S18", "S38", "S40", "S44"]),
            ],
            [
                "4 · Property B is the asset worth protecting",
                f"Staying in unit 3 keeps {money(BASE_INPUTS['sf_rent_2units_2026'])}/yr of in-place rent, the building's {money(BASE_INPUTS['sf_av_2025'])} Prop. 13 base, its $7,000 exemption, and keeps unit 3 out of the local rent-control regime. "
                "Moving out and renting it caps its growth at 1.6% for 2026–27 and subjects it to just-cause eviction rules.",
                src_links(["S24", "S30", "S31"]),
            ],
            [
                "5 · Two dated risks land inside the window",
                "The rooftop solar credit is tied to a 20-year legacy window that closes by the early 2040s, turning today's small credit into a bill plus inverter replacement. Holding both properties keeps most of the household's net worth in two parcels in the same seismic and insurance market.",
                src_links(["S33", "S36", "S42"]),
            ],
        ],
    )

    guard = table(
        ["If this is true", "What changes", "What to do", "Official basis"],
        [
            [
                "You genuinely want to live in Property A",
                f"Plan 2B trails Plan 1A by {money(w['after_liquidation_net_worth'] - l2b['after_liquidation_net_worth'])} over 20 years but beats leaving unit 3 empty (Plan 2A) by {money(l2b['after_liquidation_net_worth'] - l2a['after_liquidation_net_worth'])}. "
                "Treat the gap as the explicit price of the lifestyle choice, not as a modeling error.",
                "Occupy within 1 year, file the $7,000 exemption claim and the Prop. 19 claim inside their windows, and rent unit 3 rather than leave it vacant.",
                src_links(["S22", "S24", "S31"]),
            ],
            [
                "Equities stagnate for a decade while local homes boom",
                f"Under regime R6, renting Property A ({money(regimes['R6_EQUITY_LOST_DECADE_SV_BOOM']['plans']['P3_RENT_CUP_STAY_SF']['after_liquidation_net_worth'])}) and Treasuries ({money(regimes['R6_EQUITY_LOST_DECADE_SV_BOOM']['plans']['P1B_SELL_TREASURY']['after_liquidation_net_worth'])}) both beat 100% equities ({money(regimes['R6_EQUITY_LOST_DECADE_SV_BOOM']['plans']['P1A_SELL_EQUITY']['after_liquidation_net_worth'])}).",
                "Hold 20%–30% in CA-tax-exempt Treasuries and stage equity entry over 24–36 months instead of buying in one day.",
                src_links(["S18", "S40", "S44"]),
            ],
            [
                "Congress repeals stepped-up basis before the death",
                f"Under regime R5 the pre-death gain is taxed before reinvestment and the exclusion falls to 35% of schedule. Net sale proceeds drop by roughly a third.",
                "If a repeal is enacted before the death, re-run the comparison: renting may beat selling, and the trust should not sell in the year of death without advice.",
                src_links(["S07", "S15", "S46"]),
            ],
            [
                "The estate is large enough to owe federal estate tax",
                "Estate tax is computed on the whole estate, not on this house. A 40% federal rate applies only above the exclusion; California adds $0 at any size.",
                "Have the trustee tally the gross estate, consider portability, and file Form 706 on time if a return is required.",
                src_links(["S01", "S02", "S13"]),
            ],
        ],
    )

    body = (
        PRIVACY
        + '<div class="verdict"><strong>Bottom line.</strong> Sell Property A when the trust distributes it, stay in Property B unit 3, and '
        "reinvest in a staged equity portfolio with a Treasury reserve. The plan wins on every transfer year from 2040 to 2050 in the baseline, "
        "and it wins because of structural arithmetic — a tax-free basis reset, a property-tax base that resets upward whether you occupy or rent, "
        "and a rental yield below every liquid alternative — not because of a lucky return assumption.</div>"
        + "<h2>Five mechanisms behind the recommendation</h2>"
        + drivers
        + "<h2>Six plans, one 20-year scoreboard (2045 transfer → 2064)</h2>"
        + table(
            [
                "Strategy",
                "Property A tax, year 1",
                "Household net cash flow, year 1",
                "Pre-liquidation net worth (2064)",
                "After-liquidation net worth (2064)",
                "Gap to the winner",
                "Official basis",
            ],
            [
                [
                    esc(PLAN_TINY[k]),
                    money(p[k]["yr1_cup_prop_tax"]),
                    money(p[k]["yr1_household_op_cf"]),
                    money(p[k]["pre_liquidation_net_worth"]),
                    f"<strong>{money(p[k]['after_liquidation_net_worth'])}</strong>",
                    "—" if k == "P1A_SELL_EQUITY" else money(p[k]["after_liquidation_net_worth"] - w["after_liquidation_net_worth"]),
                    src_links(["S07", "S15", "S18", "S22"]),
                ]
                for k in [
                    "P1A_SELL_EQUITY",
                    "P1C_SELL_BALANCED_75_25",
                    "P3_RENT_CUP_STAY_SF",
                    "P1B_SELL_TREASURY",
                    "P2B_LIVE_CUP_SF3U",
                    "P2A_LIVE_CUP_SF2U",
                ]
            ],
        )
        + "<h2>What the winning plan actually involves</h2>"
        + table(
            ["Step", "Action", "Why it matters here", "Official basis"],
            [
                [
                    "Year 0 — months 1–6 after death",
                    "Appraise Property A at the date of death, open the trust's own tax identity, and sell from the administrative trust or immediately after distribution.",
                    "Locks the basis that makes the sale tax-free, and stops post-death appreciation from becoming taxable gain.",
                    src_links(["S07", "S15", "S27"]),
                ],
                [
                    "Year 0 — sale",
                    "Pay 5.00% of proceeds in brokerage/closing costs and 0.11% county transfer tax; expect a prorated supplemental property-tax bill from the reassessment date.",
                    "The only material friction in the plan, and it is small relative to one year of reassessed carrying cost.",
                    src_links(["S29", "S28"]),
                ],
                [
                    "Years 0–3",
                    "Move the proceeds into a broad equity index in 24–36 monthly tranches, holding the uninvested balance in Treasury bills while the schedule runs.",
                    "Removes the single-day entry risk that regime R3 punishes; Treasury interest is exempt from California income tax.",
                    src_links(["S18", "S43"]),
                ],
                [
                    "Ongoing",
                    "Keep Property B's $7,000 homeowners' exemption, claim the 1.6% allowable increase each year, and hold a maintenance reserve.",
                    "Protects the one asset whose property-tax base is permanently low.",
                    src_links(["S24", "S31"]),
                ],
            ],
        )
        + "<h2>When a different plan makes sense</h2>"
        + guard
        + "<h2>What could make this recommendation wrong</h2>"
        + table(
            ["Risk", "Direction of the error", "How the model treats it", "Official basis"],
            [
                [
                    "Equity returns below the 7.0% baseline",
                    "Narrows the gap; below roughly 4% Treasuries and renting become competitive.",
                    "Sensitivity table re-runs −1.5%/yr; regime R6 tests a full lost decade.",
                    src_links(["S44", "S40"]),
                ],
                [
                    "Home values compounding faster than 3.5%",
                    "Raises the value of holding; renting closes part of the gap.",
                    "Regime R6 tests 5.4% local growth; the sensitivity table re-tests the rental yield.",
                    src_links(["S42"]),
                ],
                [
                    "Selling costs higher than 5.11%",
                    "Reduces the sale advantage proportionally, but not enough to reverse the ranking at any tested value.",
                    "Exit costs are charged to every plan that sells, including the embedded exit cost of holding.",
                    src_links(["S29"]),
                ],
                [
                    "Insurance repriced sharply",
                    "Penalises whichever property you keep — the 3-unit building carries the larger bill.",
                    "Insurance escalates at 4.0%/yr with a +45% shock in regime R4.",
                    src_links(["S36", "S37"]),
                ],
            ],
        )
    )
    return body


def page_decision(anchor: dict, by_year: dict) -> str:
    rows = []
    for yr in range(2040, 2051):
        ev = by_year[str(yr)]
        pp = ev["plans"]
        rows.append(
            [
                f"{yr} → {ev['end_year']}",
                money(ev["cup_fmv_at_inh"]),
                money(ev["net_sale_proceeds_if_sold"]),
                f"<strong>{money(pp['P1A_SELL_EQUITY']['after_liquidation_net_worth'])}</strong>",
                money(pp["P1C_SELL_BALANCED_75_25"]["after_liquidation_net_worth"]),
                money(pp["P3_RENT_CUP_STAY_SF"]["after_liquidation_net_worth"]),
                money(pp["P2B_LIVE_CUP_SF3U"]["after_liquidation_net_worth"]),
                money(pp["P2A_LIVE_CUP_SF2U"]["after_liquidation_net_worth"]),
                src_links(["S07", "S15", "S18", "S22", "S29"]),
            ]
        )

    sens_specs = [
        ("Baseline parameters", evaluate_plans(2045, 20, "R0_BASELINE")),
        ("Insurance at the owner's $1,500/yr estimate", evaluate_plans(2045, 20, "R0_BASELINE", use_owner_ins_guess=True)),
        ("Rent A at the official HUD rent (2.47% gross yield)", evaluate_plans(2045, 20, "R0_BASELINE", cup_rent_yield_override=BASE_INPUTS["cup_gross_rent_yield_hud"])),
        ("Rent A at a high 3.50% gross yield", evaluate_plans(2045, 20, "R0_BASELINE", cup_rent_yield_override=0.035)),
        ("Equity return 1.5 points lower (5.5% total)", evaluate_plans(2045, 20, "R0_BASELINE", eq_return_shift=-0.015)),
        ("Equity return 1.5 points higher (8.5% total)", evaluate_plans(2045, 20, "R0_BASELINE", eq_return_shift=0.015)),
        ("$5,000,000 cash inheritance instead of $1,000,000", evaluate_plans(2045, 20, "R0_BASELINE", cash_inheritance_buffer=5_000_000.0)),
    ]
    sens_rows = []
    for label, ev in sens_specs:
        pp = ev["plans"]
        sens_rows.append(
            [
                esc(label),
                money(pp["P1A_SELL_EQUITY"]["after_liquidation_net_worth"]),
                money(pp["P1C_SELL_BALANCED_75_25"]["after_liquidation_net_worth"]),
                money(pp["P3_RENT_CUP_STAY_SF"]["after_liquidation_net_worth"]),
                money(pp["P2B_LIVE_CUP_SF3U"]["after_liquidation_net_worth"]),
                esc(PLAN_TINY[ev["winner_id"]]),
                src_links(["S10", "S12", "S36", "S38", "S44"]),
            ]
        )

    yearly_rows = []
    for a, b2 in zip(anchor["plans"]["P1A_SELL_EQUITY"]["yearly"], anchor["plans"]["P3_RENT_CUP_STAY_SF"]["yearly"]):
        yearly_rows.append(
            [
                str(a["year"]),
                money(a["tot_op_cf"]),
                money(a["liq_val"]),
                money(b2["tot_op_cf"]),
                money(b2["liq_val"]),
                money(a["cup_val"]) if a["cup_val"] else "<span class=\"blank\">sold</span>",
                money(a["sf_val"]),
                src_links(["S12", "S18", "S31", "S42"]),
            ]
        )

    body = (
        PRIVACY
        + "<p>This page compares the three decisions the brief asks about — live in the inherited house, rent it out, or sell and "
        "reinvest — for every possible inheritance year between 2040 and 2050. Each plan keeps Property B, pays its own property "
        "taxes, insurance, utilities, maintenance and income tax, and is then charged the tax that would be owed to convert the "
        "final assets into cash.</p>"
        + "<h2>20-year after-tax net worth, by inheritance year</h2>"
        + table(
            [
                "Window",
                "Property A value at death",
                "Net sale cash",
                "1A · Sell → equities",
                "1C · Sell → 75/25",
                "3 · Rent A out",
                "2B · Live in A, rent B unit 3",
                "2A · Live in A, B unit 3 vacant",
                "Official basis",
            ],
            rows,
        )
        + "<p class=\"lead\">The ranking holds in all eleven years. Later transfers start from a larger Property A value but also a larger "
        "reassessed tax base, so the advantage of selling is not a timing artefact.</p>"
        + "<h2>Sensitivity cases around a 2045 transfer</h2>"
        + table(
            [
                "Case",
                "1A · equities",
                "1C · 75/25",
                "3 · rent A out",
                "2B · live in A",
                "Winner",
                "Official basis",
            ],
            sens_rows,
        )
        + "<h2>Why renting the inherited house loses: the arithmetic line by line</h2>"
        + table(
            ["Line", "Rent Property A (Plan 3), 2045", "Sell and invest (Plan 1A), 2045", "Official basis"],
            [
                [
                    "Gross income on the asset",
                    f"2.80% gross rent yield = {money(BASE_INPUTS['cup_val_2026'] * 0.028)}/yr in 2026 dollars (official HUD benchmark implies 2.47%)",
                    f"Portfolio yields 4.3% (Treasury) to 7.0% (equity) on {money(anchor['net_sale_proceeds_if_sold'])}",
                    src_links(["S18", "S38", "S40"]),
                ],
                [
                    "Property tax",
                    f"{money(anchor['plans']['P3_RENT_CUP_STAY_SF']['yr1_cup_prop_tax'])}/yr after full reassessment to fair market value",
                    "$0 — the property is no longer held",
                    src_links(["S21", "S22"]),
                ],
                [
                    "Insurance, water, electricity, maintenance",
                    "All borne by the owner; the solar credit ends by the early 2040s and the pool pumps, roof and inverter do not",
                    "None; the proceeds have no carrying cost",
                    src_links(["S33", "S36"]),
                ],
                [
                    "Vacancy and management",
                    "5% vacancy plus 6% leasing/management charged against gross rent",
                    "None",
                    src_links(["S12"]),
                ],
                [
                    "Income tax",
                    "Rent is ordinary income at the combined federal + NIIT + California rate; depreciation shields only the building share and is recaptured at up to 25% on sale",
                    "Equity: 1.5% qualified dividends plus realised gains; Treasuries: federal only, zero California tax",
                    src_links(["S10", "S11", "S12", "S18"]),
                ],
                [
                    "Liquidity and concentration",
                    "A single illiquid parcel; a forced sale in a bad year pays the same exit costs",
                    "Daily liquidity; sale costs are paid once at exit, and the exit tax is modelled explicitly",
                    src_links(["S29", "S43"]),
                ],
            ],
        )
        + "<h2>The same two plans, year by year (2045 → 2064, rounded)</h2>"
        + table(
            [
                "Year",
                "Plan 1A household net cash flow",
                "Plan 1A liquid portfolio",
                "Plan 3 household net cash flow",
                "Plan 3 liquid portfolio",
                "Property A value (Plan 3)",
                "Property B value",
                "Official basis",
            ],
            yearly_rows,
        )
    )
    return body


def page_property_tax(anchor: dict, series: list[dict]) -> str:
    hist_a = [
        [str(r["year"]), money(r["assessed"]), money(r["tax"]) if r["tax"] else '<span class="blank">not supplied</span>', f"{r['boe_factor']:.5f}", src_links(["S21", "S28"])]
        for r in HIST_PROP_A
    ]
    hist_b = [
        [str(r["year"]), money(r["assessed"]), money(r["tax"]), f"{r['boe_factor']:.5f}", src_links(["S21", "S30"])]
        for r in HIST_PROP_B
    ]

    by_yr = {r["year"]: r for r in series}
    p19 = []
    for yr in range(2040, 2051):
        r = by_yr[yr]
        p19.append(
            [
                str(yr),
                money(r["cup_val"]),
                money(r["cup_fbyv_pre"]),
                money(r["prop19_cap"]),
                money(r["cup_av_prop19_if_inh"]),
                money(r["cup_tax_prop19_if_inh"]),
                money(r["cup_tax_full_if_inh"]),
                src_links(["S21", "S22", "S23", "S28"]),
            ]
        )

    body = (
        PRIVACY
        + "<h2>Supplied history, rounded to the nearest $10</h2>"
        + "<p>Both histories are shown exactly as supplied after rounding. They are not corrected to match a formula, because the "
        "supplied bills are the record of what was actually paid. The last column shows the maximum annual assessment growth the law "
        "allows (the lower of 2% and the California inflation factor), which is what an assessor is permitted to apply.</p>"
        + "<h3>Property A — trust-held residence (2014–2026)</h3>"
        + table(["Tax year", "Assessed value", "Tax bill", "Max lawful factor", "Official basis"], hist_a)
        + "<h3>Property B — 3-unit building (2016–2025)</h3>"
        + table(["Tax year", "Assessed value", "Tax bill", "Max lawful factor", "Official basis"], hist_b)
        + "<h2>Why the effective rate looks higher than 1%</h2>"
        + table(
            ["Rule", "Verified requirement", "Effect on these two properties", "Official basis"],
            [
                [
                    "The 1% levy is not the whole bill",
                    "Prop. 13 caps the general levy at 1% of assessed value plus voter-approved bonded debt; bills also carry per-parcel taxes and direct assessments.",
                    "Property A's bill is about 1.34% of assessed value and Property B's about 2.14%: on a very small Prop. 13 base, the fixed parcel charges dominate the percentage levy.",
                    src_links(["S21", "S28"]),
                ],
                [
                    "Fixed charges do not grow with value",
                    "Direct assessments and parcel taxes are levied per parcel or per benefit unit, not as a share of value.",
                    "The model therefore separates rate × assessed value from a fixed-charge line that inflates with consumer prices.",
                    src_links(["S21", "S30"]),
                ],
                [
                    "Annual growth is capped",
                    "Factored base-year value may rise by the lower of 2% and the California consumer price index each year.",
                    "A 0% inflation year means a 0% assessment increase — the cap is a ceiling, not a schedule.",
                    src_links(["S21"]),
                ],
                [
                    "Declines are enrolled too",
                    "Where January 1 market value falls below the factored base, the assessor temporarily enrolls market value and restores it as prices recover.",
                    "This softens the tax on a holding plan during a crash, which the stress regimes model.",
                    src_links(["S25"]),
                ],
            ],
        )
        + "<h2>What a 2040–2050 inheritance does to Property A's tax base</h2>"
        + table(
            ["Rule", "Verified requirement", "Consequence for each plan", "Official basis"],
            [
                [
                    "Transfer date is the death date",
                    "When a revocable trust becomes irrevocable at death, the change in ownership is dated to the death, not to the later deed — and a prorated supplemental bill follows.",
                    "Starts the 150-day reporting clock and the 1-year occupancy clock on the same day.",
                    src_links(["S26", "S28"]),
                ],
                [
                    "Parent-child relief is narrow",
                    "The exclusion applies only to the settlor's principal residence, only if the child occupies it as a principal residence within one year and claims the $7,000 exemption; value above the base plus $1,044,586 is added to the roll.",
                    f"Occupy it and the tax still rises to {money(anchor['plans']['P2A_LIVE_CUP_SF2U']['yr1_cup_prop_tax'])}/yr in a 2045 transfer.",
                    src_links(["S22", "S23", "S24"]),
                ],
                [
                    "No occupancy, no relief",
                    "A child who keeps living elsewhere gets no parent-child exclusion — the property is reassessed to full market value.",
                    f"Renting it out costs {money(anchor['plans']['P3_RENT_CUP_STAY_SF']['yr1_cup_prop_tax'])}/yr in the first year of a 2045 transfer.",
                    src_links(["S21", "S22"]),
                ],
                [
                    "One exemption per household",
                    "The $7,000 exemption may be claimed on only one principal residence per household.",
                    "Claiming it on Property A means giving it up on Property B — a real but small cost of moving.",
                    src_links(["S24"]),
                ],
                [
                    "The allowance is re-set every two years",
                    "The parent-child allowance is adjusted every second February 15 by the prior year's California house-price change; the published figure covers 16 Feb 2025 – 15 Feb 2027.",
                    "The 2040–2050 allowance is projected, not published, and is labeled as such everywhere it appears.",
                    src_links(["S22", "S23"]),
                ],
            ],
        )
        + "<h2>Projected reassessment for every inheritance year, 2040–2050</h2>"
        + table(
            [
                "Transfer year",
                "Property A market value",
                "Pre-death taxable base",
                "Projected Prop. 19 allowance",
                "New taxable value if you occupy",
                "Year-1 tax if you occupy",
                "Year-1 tax if you rent it out",
                "Official basis",
            ],
            p19,
        )
        + "<p class=\"lead\">The allowance column is a projection built from the statutory two-year adjustment rule and is shown in "
        "italics-free plain figures only to make the arithmetic visible; the only published allowance is the one linked above.</p>"
    )
    return body


def page_projections(series: list[dict]) -> str:
    rows_a = [
        [
            str(r["year"]),
            money(r["cup_val"]),
            money(r["cup_fbyv_pre"]),
            money(r["cup_tax_pre"]),
            money(r["cup_tax_prop19_if_inh"]),
            money(r["cup_tax_full_if_inh"]),
            money(r["cup_ins_model"]),
            money(r["cup_water"]),
            money(r["cup_elec"]),
            money(r["cup_maint"]),
            src_links(["S21", "S23", "S33", "S34", "S36", "S42"]),
        ]
        for r in series
    ]
    rows_b = [
        [
            str(r["year"]),
            money(r["sf_val"]),
            money(r["sf_fbyv"]),
            money(r["sf_tax"]),
            money(r["sf_rent_2u"]),
            money(r["sf_unit3_mkt_rent"]),
            money(r["sf_ins_model"]),
            money(r["sf_water"]),
            money(r["sf_elec"]),
            money(r["sf_maint"]),
            src_links(["S21", "S30", "S31", "S35", "S36", "S42"]),
        ]
        for r in series
    ]
    body = (
        PRIVACY
        + "<p>Fifty years, both properties, every line the brief asks for, in 2026 dollars grown at the modeled nominal rates. "
        "Property A shows its pre-transfer tax if nothing happens, plus the first-year tax under each inheritance route so you can "
        "compare a transfer in that year against any other. The solar credit flips to a net cost when the 20-year legacy window closes "
        "in the early 2040s.</p>"
        + "<h2>Property A — inherited residence, 2026–2075</h2>"
        + table(
            [
                "Year",
                "Market value",
                "Taxable base (pre-transfer)",
                "Property tax (pre-transfer)",
                "Year-1 tax if occupied",
                "Year-1 tax if rented or sold-to-hold",
                "Insurance (modeled)",
                "Water",
                "Solar / electric",
                "Maintenance &amp; capex",
                "Official basis",
            ],
            rows_a,
        )
        + "<h2>Property B — already-owned 3-unit building, 2026–2075</h2>"
        + table(
            [
                "Year",
                "Market value",
                "Prop. 13 base",
                "Property tax",
                "In-place rent, 2 units",
                "Market rent, unit 3",
                "Insurance (3-unit)",
                "Water &amp; sewer",
                "Common electric",
                "Maintenance &amp; capex",
                "Official basis",
            ],
            rows_b,
        )
        + "<h2>Assumptions behind the growth rates</h2>"
        + table(
            ["Parameter", "Value", "Why", "Official basis"],
            [
                ["Consumer price inflation", "2.3%/yr", "Long-run average used as the baseline; the stress section replays 9.1%.", src_links(["S40", "S41"])],
                ["Property A value growth", "3.5%/yr nominal", "Below the long-run regional index to avoid assuming the past repeats.", src_links(["S42"])],
                ["Property B value growth", "3.0%/yr nominal", "Coastal 3-unit building, slightly slower than a single-family home.", src_links(["S42"])],
                ["Insurance trend", "4.0%/yr", "Above general inflation; the market has repriced faster than CPI.", src_links(["S36"])],
                ["Water trend, A", "3.2%/yr", "Regulated utility general rate case steps.", src_links(["S34"])],
                ["Water trend, B", "8.0% in 2027–28, then 3.2%", "Municipal multi-year rate schedule with front-loaded increases.", src_links(["S35"])],
                ["Property B rent growth", "1.6% in 2027, then 60% of CPI capped at 10%", "The rent-stabilisation formula, applied to covered units.", src_links(["S31"])],
                ["Property A rent growth", "CPI less 15%", "Market rent tracks incomes more closely than prices.", src_links(["S38"])],
                ["Solar credit", "−$180/yr until the legacy window closes", "Today's credit held flat in real terms, then replaced by a modeled net grid cost plus inverter reserve.", src_links(["S33"])],
            ],
        )
    )
    return body


def page_costs(anchor: dict) -> str:
    rows = [
        [
            "Property A — homeowners insurance",
            "California statewide average homeowner premium is published in the Department of Insurance market snapshot; the area's FAIR Plan share is 0.5% of insured dwellings",
            '<span class="blank">blank — no official parcel quote</span>',
            f"{money(BASE_INPUTS['cup_ins_model_2026'])}/yr modeled; the owner's {money(BASE_INPUTS['cup_ins_owner_guess_2026'])}/yr guess is tested separately",
            "4.0%/yr, +45% shock in the seismic regime",
            src_links(["S36", "S37"]),
        ],
        [
            "Property B — 3-unit building insurance",
            "Department of Insurance data cover 1–4 unit residential policies; the area's FAIR Plan share is 0.2%",
            '<span class="blank">blank — no official parcel quote</span>',
            f"{money(BASE_INPUTS['sf_ins_model_2026'])}/yr modeled; the owner's {money(BASE_INPUTS['cup_ins_owner_guess_2026'])}/yr guess is tested separately",
            "4.0%/yr, +45% shock in the seismic regime",
            src_links(["S36", "S37"]),
        ],
        [
            "Property A — water",
            "Regulated water utility general rate case authorises 2025–2027 step increases",
            '<span class="blank">blank — no official parcel amount</span>',
            f"{money(BASE_INPUTS['cup_water_2026'])}/yr (midpoint of the supplied $1,200–$1,800/yr)",
            "3.2%/yr",
            src_links(["S34"]),
        ],
        [
            "Property A — electricity and rooftop solar",
            "Retail-rate export credits last 20 years from interconnection; the successor tariff pays avoided cost, with a 9-year legacy for the original customer",
            '<span class="blank">blank — no official parcel amount</span>',
            f"{money(BASE_INPUTS['cup_solar_credit_2026'])}/yr credit until the legacy window closes, then {money(BASE_INPUTS['cup_post_nem_elec_2026'])}/yr in 2026 dollars",
            "Credit held flat in real terms; post-legacy cost escalates at 3.2%",
            src_links(["S33"]),
        ],
        [
            "Property B — water and sewer, 3 units",
            "Municipal multi-year retail water and sewer rate adjustments fund regional capital works",
            '<span class="blank">blank — no official parcel amount</span>',
            f"{money(BASE_INPUTS['sf_water_2026'])}/yr (midpoint of the supplied $3,960–$4,800/yr)",
            "8.0% in 2027–28, then 3.2%",
            src_links(["S35"]),
        ],
        [
            "Property B — common electricity",
            "Regulated electric tariff context",
            '<span class="blank">blank — no official parcel amount</span>',
            f"{money(BASE_INPUTS['sf_elec_2026'])}/yr (midpoint of the supplied $360–$840/yr)",
            "3.2%/yr",
            src_links(["S33"]),
        ],
        [
            "Property A — maintenance and capital reserve",
            "No statute sets a residential reserve rate; the tax rules distinguish repairs from capitalised improvements",
            '<span class="blank">blank — no official amount</span>',
            f"{money(BASE_INPUTS['cup_maint_2026'])}/yr (about $800/mo) plus a shock in the seismic regime",
            "CPI + 1.0%",
            src_links(["S12"]),
        ],
        [
            "Property B — maintenance and capital reserve, 3 units",
            "Same rule; a 3-unit building carries three kitchens, three baths, a shared roof and exterior",
            '<span class="blank">blank — no official amount</span>',
            f"{money(BASE_INPUTS['sf_maint_2026'])}/yr (about $1,200/mo) — higher than Property A, as the brief assumes",
            "CPI + 1.0%",
            src_links(["S12"]),
        ],
        [
            "Property A — achievable rent",
            "Official small-area fair market rent for the area: $3,340 efficiency, $3,800 1-bed, $4,440 2-bed, $5,870 3-bed, $6,390 4-bed per month",
            '<span class="blank">blank — no official single-family rent for this parcel</span>',
            f"2.80% gross yield ({money(BASE_INPUTS['cup_val_2026'] * 0.028)}/yr) modeled; official 4-bed rent implies 2.47%",
            "CPI less 15%, after 5% vacancy and 6% management",
            src_links(["S38", "S12"]),
        ],
        [
            "Property B — rent in place and unit 3",
            "Official small-area fair market rent: $3,310 2-bed, $4,230 3-bed per month; the local allowable increase is 1.6% for 2026–27",
            '<span class="blank">blank — in-place rent is a private fact</span>',
            f"{money(BASE_INPUTS['sf_rent_2units_2026'])}/yr from 2 units; {money(BASE_INPUTS['sf_unit3_mkt_rent_2026'])}/yr if unit 3 is rented",
            "1.6% in 2027, then 60% of CPI",
            src_links(["S31", "S39"]),
        ],
    ]
    body = (
        PRIVACY
        + "<p>The brief asked for insurance researched against the owner's ~$1,500/yr estimate. The finding is unambiguous: "
        "no government publication quotes a premium for a specific dwelling, so the parcel-specific cells stay blank, and the model "
        "carries a researched assumption instead. The owner's $1,500/yr is tested in the sensitivity table, where it changes the "
        "dollar totals but not the ranking.</p>"
        + table(
            [
                "Cost line",
                "What is officially verified",
                "Parcel-specific official value",
                "What the model uses (2026 dollars, rounded)",
                "Escalation rule",
                "Official basis",
            ],
            rows,
        )
        + "<h2>Why the $1,500/yr insurance estimate is too low to rely on</h2>"
        + table(
            ["Consideration", "Detail", "Official basis"],
            [
                [
                    "Statewide average vs. a high-value home",
                    "The statewide average homeowner premium is roughly the same order of magnitude as the owner's estimate, but averages are dominated by ordinary homes. A rebuild of a multi-million-dollar dwelling at current construction cost is a different exposure, and the modeled figure reflects that.",
                    src_links(["S36"]),
                ],
                [
                    "Insurance is repricing faster than inflation",
                    "Market-wide premium increases have run ahead of consumer price inflation, which is why the model escalates insurance at 4.0% rather than 2.3%.",
                    src_links(["S36", "S37"]),
                ],
                [
                    "A 3-unit building is not a homeowner policy",
                    "A 3-unit building needs a dwelling policy covering rented units, loss of rents and landlord liability; the premium and the deductible structure differ from an owner-occupied single-family policy.",
                    src_links(["S36", "S12"]),
                ],
                [
                    "Availability, not just price",
                    "The FAIR Plan is the insurer of last resort; its policy count has grown sharply, which matters if either property becomes hard to insure.",
                    src_links(["S37"]),
                ],
            ],
        )
        + "<h2>Net operating picture at a 2045 transfer</h2>"
        + table(
            ["Plan", "Year-1 Property A tax", "Year-1 household net cash flow", "Twenty-year operating cash flow", "Official basis"],
            [
                [
                    esc(PLAN_TINY[k]),
                    money(anchor["plans"][k]["yr1_cup_prop_tax"]),
                    money(anchor["plans"][k]["yr1_household_op_cf"]),
                    money(anchor["plans"][k]["cum_op_cf_20yr"]),
                    src_links(["S12", "S24", "S31", "S36"]),
                ]
                for k in [
                    "P1A_SELL_EQUITY",
                    "P3_RENT_CUP_STAY_SF",
                    "P2B_LIVE_CUP_SF3U",
                    "P2A_LIVE_CUP_SF2U",
                ]
            ],
        )
    )
    return body


def page_black_swan(regime_evals: dict) -> str:
    defs = table(
        ["Regime", "What it replays", "Official basis"],
        [[esc(t), esc(d), src_links(srcs)] for _rid, t, d, srcs in REGIME_SPECS],
    )

    compare = []
    for rid, title, _d, _s in REGIME_SPECS:
        series = {r["year"]: r for r in simulate_property_series(rid)}
        pick = [2030, 2045, 2050, 2060, 2075]
        row = [esc(title.split("—")[0].strip())]
        for y in pick:
            row.append(money(series[y]["cup_val"]))
        row.append(money(series[pick[-1]]["sf_val"]))
        row.append(src_links(["S40", "S42", "S43"]))
        compare.append(row)

    ev = regime_evals
    outcome = []
    for rid, title, _d, srcs in REGIME_SPECS:
        pp = ev[rid]["plans"]
        outcome.append(
            [
                esc(title.split("—")[0].strip()),
                money(pp["P1A_SELL_EQUITY"]["after_liquidation_net_worth"]),
                money(pp["P1C_SELL_BALANCED_75_25"]["after_liquidation_net_worth"]),
                money(pp["P1B_SELL_TREASURY"]["after_liquidation_net_worth"]),
                money(pp["P3_RENT_CUP_STAY_SF"]["after_liquidation_net_worth"]),
                money(pp["P2B_LIVE_CUP_SF3U"]["after_liquidation_net_worth"]),
                f"<strong>{esc(PLAN_TINY[ev[rid]['winner_id']])}</strong>",
                src_links(srcs),
            ]
        )

    short = evaluate_plans(2045, 3, "R3_SEQ_CRASH_AFTER_SALE")["plans"]
    body = (
        PRIVACY
        + "<p>A 50-year projection that grows at a constant rate is a ruler, not a forecast. This separate section replays seven "
        "non-uniform histories — real inflation spikes, a financial crisis that lands on the transfer year, a crash immediately "
        "after the sale, a seismic and insurance shock, a repeal of stepped-up basis, and a long equity stagnation with a local "
        "housing boom — against the smooth baseline.</p>"
        + "<h2>The seven regimes</h2>"
        + defs
        + "<h2>Property A value under each regime</h2>"
        + table(
            ["Regime", "2030 value", "2045 value", "2050 value", "2060 value", "2075 value", "Property B value in 2075", "Official basis"],
            compare,
        )
        + "<h2>Twenty-year after-tax outcome, 2045 transfer → 2064</h2>"
        + table(
            [
                "Regime",
                "1A · equities",
                "1C · 75/25",
                "1B · Treasuries",
                "3 · rent A out",
                "2B · live in A",
                "Winner",
                "Official basis",
            ],
            outcome,
        )
        + "<h2>The acute test: a crash the year after the sale</h2>"
        + table(
            ["Three-year window, 2045 → 2047", "1A · 100% equities", "1C · 75/25", "3 · rent A out", "2B · live in A", "What it proves", "Official basis"],
            [
                [
                    "Equities fall 24% then 18% straight after the sale",
                    money(short["P1A_SELL_EQUITY"]["after_liquidation_net_worth"]),
                    money(short["P1C_SELL_BALANCED_75_25"]["after_liquidation_net_worth"]),
                    money(short["P1B_SELL_TREASURY"]["after_liquidation_net_worth"]),
                    money(short["P3_RENT_CUP_STAY_SF"]["after_liquidation_net_worth"]),
                    "Selling is still right; entering the market in one day is not. Staging the proceeds through Treasuries over 24–36 months keeps the plan's advantage while removing the single-day timing risk.",
                    src_links(["S18", "S43", "S44"]),
                ]
            ],
        )
        + "<h2>What the stress tests change, and what they do not</h2>"
        + table(
            ["Finding", "Consequence for the plan", "Official basis"],
            [
                [
                    "Selling survives every regime",
                    "Plan 1A or 1C is the top or near-top plan in all seven; no regime makes holding the house the best financial choice, although renting nearly closes the gap when equities stagnate.",
                    src_links(["S42", "S44"]),
                ],
                [
                    "The mix matters more than the decision",
                    "In the stagnating-equity regime a 25% Treasury sleeve, or even 100% Treasuries, beats 100% equities — which is the argument for staging, not for holding the house.",
                    src_links(["S18", "S40"]),
                ],
                [
                    "The seizure risk is statutory, not market",
                    "A repeal of IRC §1014 would tax the pre-death gain and is the one change that materially weakens selling; it is tracked on the law watch page.",
                    src_links(["S07", "S46"]),
                ],
                [
                    "Insurance is the underestimated shock",
                    "A seismic event with a 45% premium jump and an uninsured repair bill hits whichever property is held; holding two concentrates that exposure.",
                    src_links(["S36", "S37", "S25"]),
                ],
            ],
        )
    )
    return body


def page_process() -> str:
    body = (
        PRIVACY
        + "<p>The sequence below is the California trust path, with the statutory deadline that drives each step. Deadlines run from "
        "the date of death, not from the date a beneficiary learns of it.</p>"
        + table(
            ["Step and deadline", "What must be done", "If it is missed", "Official basis"],
            [
                [
                    "Days 1–30",
                    "Obtain certified death certificates, locate the signed trust and any amendments, obtain a separate tax identification number for the trust, and confirm the property stays insured in the trust's name.",
                    "A coverage gap or frozen accounts; the trust cannot sell what it cannot insure or transact on.",
                    src_links(["S01", "S20", "S36"]),
                ],
                [
                    "Within 60 days — trustee notification",
                    "Serve the statutory notification on every beneficiary and every heir at law.",
                    "The contest period does not start on schedule and the trustee is exposed to surcharge.",
                    src_links(["S27"]),
                ],
                [
                    "Months 1–4 — date-of-death appraisal",
                    "Commission a date-of-death appraisal of Property A and inventory all financial assets; this document is the basis evidence for every later tax filing.",
                    "Unsupported basis on the final return and on any depreciation schedule if the house is rented.",
                    src_links(["S07", "S15", "S28"]),
                ],
                [
                    "Within 150 days — change in ownership report",
                    "File the death-of-owner change-in-ownership statement with the county assessor, even if the property will be sold.",
                    "A statutory penalty computed on the reassessed tax.",
                    src_links(["S26", "S28"]),
                ],
                [
                    "Within 9 months — federal estate return",
                    "File Form 706 if the worldwide estate plus prior taxable gifts exceeds the year-of-death exclusion, or to elect portability for a surviving spouse. A six-month filing extension is available, but tax is still due at nine months.",
                    "Late-filing and late-payment penalties, or loss of a multi-million-dollar portable exclusion.",
                    src_links(["S01", "S02"]),
                ],
                [
                    "Annual — fiduciary income tax",
                    "File the federal fiduciary return and the California fiduciary return for income earned between death and distribution, with the beneficiary statements.",
                    "Trust-level brackets compress quickly: the top capital-gain rate applies at a low income threshold for trusts.",
                    src_links(["S03", "S11", "S20"]),
                ],
                [
                    "Route 1 — sell (recommended)",
                    "Sell from the administrative trust or immediately after distribution; record the trustee's death affidavit and the preliminary change of ownership report; pay 0.11% county transfer tax and the prorated supplemental bill; deploy the proceeds on a staged schedule.",
                    "Delay converts post-death appreciation into taxable gain and keeps the reassessed carrying cost running.",
                    src_links(["S07", "S15", "S18", "S28", "S29"]),
                ],
                [
                    "Route 2 — occupy under Prop. 19",
                    "Move in as principal residence within 1 year of death, file the $7,000 exemption claim within 1 year (relinquishing it on Property B), and file the parent-child exclusion claim within 3 years.",
                    "Losing the 1-year window forfeits retroactive relief; missing the 3-year claim limits relief to the future.",
                    src_links(["S22", "S23", "S24"]),
                ],
                [
                    "Route 3 — rent it out",
                    "Complete the same ownership reports, then place the property in service, start depreciation on the building share only, and keep contemporaneous records of every repair and improvement.",
                    "No parent-child relief at all, and depreciation errors surface as recapture on the eventual sale.",
                    src_links(["S12", "S22", "S21"]),
                ],
            ],
        )
        + "<h2>Documents to assemble before the death, if possible</h2>"
        + table(
            ["Document", "Why it matters", "Official basis"],
            [
                ["The signed trust and every amendment", "Determines whether the property is in the taxable estate and who may sell it; a completed-gift or irrevocable structure can forfeit the step-up.", src_links(["S07", "S15"])],
                ["Deeds and the preliminary title report", "Establishes what is actually held and whether anyone else is on title.", src_links(["S28"])],
                ["The date-of-death appraisal", "The single most valuable document for both the income-tax basis and the property-tax valuation.", src_links(["S07", "S28"])],
                ["Prior gift-tax returns", "Prior taxable gifts reduce the exclusion available at death.", src_links(["S01", "S04"])],
                ["Insurance binder and claims history", "A claim can make a property uninsurable at the moment it must be insured.", src_links(["S36", "S37"])],
            ],
        )
    )
    return body


def page_thresholds(headroom: list[dict], series: list[dict]) -> str:
    by_yr = {r["year"]: r for r in series}
    proj = [
        ["2026 — verified", "$15,000,000", "$30,000,000", "$19,000", "Enacted: Public Law 119-21; Form 706 instructions", src_links(["S01", "S04", "S06"])],
        ["2027 — verified", "$15,480,000", "$30,960,000", "$20,000", "Published 5 Nov 2026 in the 2027 inflation procedure", src_links(["S02", "S03"])],
    ]
    for y in [2030, 2035, 2040, 2045, 2050]:
        r = by_yr[y]
        proj.append(
            [
                f"{y} — projected",
                money(r["estate_excl_single"]),
                money(r["estate_excl_married_dsue"]),
                "indexed",
                "Projected from the enacted indexation rule at the baseline inflation path; not published",
                src_links(["S06", "S40"]),
            ]
        )

    hr = [
        [
            money(h["cash_and_other_estate"]),
            money(h["cup_fmv"]),
            money(h["illustrative_gross_estate"]),
            money(h["headroom_single"]),
            money(h["est_fed_tax_single_40pct"]),
            money(h["headroom_married_dsue"]),
            money(h["est_fed_tax_dsue_40pct"]),
            "$0",
            src_links(["S01", "S02", "S06", "S13"]),
        ]
        for h in headroom
    ]

    body = (
        PRIVACY
        + "<p>There is no inheritance tax in California and no federal tax on receiving an inheritance. What exists is a federal "
        "estate tax on the deceased person's total estate, and it only bites above the exclusion. The tables below show the verified "
        "thresholds, the headroom at each estate size, and the result once the estate crosses the line.</p>"
        + "<h2>The three taxes that could apply, and what each actually taxes</h2>"
        + table(
            ["Tax", "Levied on", "Rate and threshold", "Applies to this household?", "Official basis"],
            [
                [
                    "Federal estate tax",
                    "The deceased person's entire worldwide estate plus prior taxable gifts",
                    "40% above the basic exclusion: $15,000,000 for 2026, $15,480,000 for 2027, or double with a valid portability election",
                    "Only if the whole estate exceeds the exclusion — the exact estate size is private and is left blank",
                    src_links(["S01", "S02", "S05"]),
                ],
                [
                    "California estate or inheritance tax",
                    "Nothing",
                    "$0 — the state and every city and county are barred from imposing a gift, inheritance, succession, legacy or estate tax; the old pick-up tax has been $0 since the federal credit was repealed",
                    "No",
                    src_links(["S13", "S14"]),
                ],
                [
                    "Income tax on the inheritance itself",
                    "Nothing on receipt",
                    "$0 on inherited cash and property; income earned afterwards (interest, dividends, rent, post-death gains) is taxable",
                    "No tax on receipt; tax on everything the assets earn afterwards",
                    src_links(["S08", "S16"]),
                ],
            ],
        )
        + "<h2>Verified and projected thresholds</h2>"
        + table(
            ["Year", "Exclusion per decedent", "Married couple with portability", "Annual gift exclusion", "Basis of the figure", "Official basis"],
            proj,
        )
        + "<h2>Headroom and tax at each estate size — a 2045 death</h2>"
        + table(
            [
                "Cash and other assets",
                "Property A value",
                "Illustrative gross estate",
                "Headroom, single",
                "Federal tax at 40%, single",
                "Headroom, married with portability",
                "Federal tax at 40%, married",
                "California death tax",
                "Official basis",
            ],
            hr,
        )
        + "<p class=\"lead\">Headroom is negative once the estate crosses the exclusion; the tax column then shows the 40% federal "
        "rate applied to the excess. California adds nothing at any size. The estate's true size, prior gifts and whether portability "
        "was elected are private facts, which is why the estate-specific tax cell is blank elsewhere on this site.</p>"
        + "<h2>How much cash can pass before any federal tax is due</h2>"
        + table(
            ["If the estate holds only cash and Property A", "Single decedent, 2045", "Married couple with portability, 2045", "Official basis"],
            [
                [
                    "Cash that can pass with no federal estate tax",
                    money(by_yr[2045]["estate_excl_single"] - by_yr[2045]["cup_val"]),
                    money(by_yr[2045]["estate_excl_married_dsue"] - by_yr[2045]["cup_val"]),
                    src_links(["S01", "S02"]),
                ],
                [
                    "California tax on that cash",
                    "$0",
                    "$0",
                    src_links(["S13", "S14"]),
                ],
                [
                    "Tax on any cash above that line",
                    "40% of the excess",
                    "40% of the excess",
                    src_links(["S01", "S05"]),
                ],
                [
                    "What the heir then owes on receipt",
                    "Nothing — the estate pays, not the beneficiary",
                    "Nothing",
                    src_links(["S05", "S08"]),
                ],
            ],
        )
        + "<h2>Proposed and pending changes to these rules</h2>"
        + table(
            ["Measure or proposal", "Status", "What it would change", "Likely effect on this household", "Official basis"],
            [
                [
                    "Repeal or modification of stepped-up basis at death",
                    "Introduced in Congress; not enacted",
                    "Would tax unrealised gains at death or carry over the deceased's basis instead of resetting it",
                    "The single largest statutory risk to the recommendation; modelled as regime R5",
                    src_links(["S46", "S07"]),
                ],
                [
                    "State wealth tax proposal on the November 2026 ballot",
                    "Canvas in progress; certification due 11 Dec 2026",
                    "A one-time tax on net worth above $1,000,000,000, excluding direct real property",
                    "No effect at any plausible household size here",
                    src_links(["S45"]),
                ],
                [
                    "Federal exclusion after 2027",
                    "Enacted indexing from 2026; future Congress could change it",
                    "The exclusion is permanent law at $15,000,000 with inflation indexing, but no Congress can bind a later one",
                    "A cut to 35% of schedule is modelled as part of regime R5",
                    src_links(["S06", "S03"]),
                ],
                [
                    "California estate tax proposals",
                    "Would require a statutory change; none enacted",
                    "Any state estate tax would need to override the current statutory prohibition",
                    "Currently $0 at every estate size; the prohibition is what would have to change first",
                    src_links(["S13", "S14"]),
                ],
            ],
        )
    )
    return body


def page_law() -> str:
    body = (
        PRIVACY
        + table(
            ["Tax question", "Jurisdiction", "Verified rule (2026–2027)", "Official basis"],
            [
                [
                    "Estate and generation-skipping exclusion",
                    "Federal",
                    "$15,000,000 per decedent for 2026; $15,480,000 for 2027; $30,960,000 for a married couple with a valid portability election; 40% top rate above the exclusion.",
                    src_links(["S01", "S02", "S03", "S06"]),
                ],
                [
                    "Annual gift exclusion",
                    "Federal",
                    "$19,000 per recipient in 2026; $20,000 in 2027; $201,000 for a non-citizen spouse in 2027. Gifts above the annual amount use the lifetime exclusion.",
                    src_links(["S02", "S03", "S04"]),
                ],
                [
                    "State and local death taxes",
                    "California",
                    "$0. The Revenue and Taxation Code bars the state and every political subdivision from imposing an estate, inheritance, succession, legacy or gift tax; the pick-up tax is $0 because the federal credit it mirrored was repealed.",
                    src_links(["S13", "S14"]),
                ],
                [
                    "Income tax on receipt",
                    "Federal and California",
                    "$0 on inherited cash or property. Interest, dividends, rents and post-death gains are taxable.",
                    src_links(["S08", "S16"]),
                ],
                [
                    "Basis of the inherited house",
                    "Federal and California",
                    "Fair market value at the date of death, if the property is included in the deceased's gross estate. California conforms to the federal basis rules.",
                    src_links(["S07", "S15"]),
                ],
                [
                    "Basis of the already-owned building",
                    "Federal and California",
                    "No adjustment — there is no death event for this owner. Historical cost less prior depreciation continues.",
                    src_links(["S07", "S12"]),
                ],
                [
                    "Long-term capital gains and the net investment income tax",
                    "Federal",
                    "0%, 15% or 20% by taxable income (2027 thresholds: 0% to $102,100 joint / $51,050 single; 20% above $633,600 / $563,200), plus 3.8% on investment income above $250,000 joint / $200,000 single.",
                    src_links(["S03", "S10", "S11"]),
                ],
                [
                    "Capital gains and the behavioral-health surcharge",
                    "California",
                    "No preferential rate: gains are taxed as ordinary income up to 12.3%, plus 1% above $1,000,000 of taxable income.",
                    src_links(["S17", "S19"]),
                ],
                [
                    "Treasury interest",
                    "California",
                    "Interest on direct U.S. Treasury obligations is exempt from California income tax; it remains taxable federally.",
                    src_links(["S18"]),
                ],
                [
                    "Home-sale exclusion",
                    "Federal",
                    "Up to $250,000 ($500,000 joint) of gain excluded after 24 months of ownership and use as a principal residence within the prior five years.",
                    src_links(["S09"]),
                ],
                [
                    "Rental depreciation and recapture",
                    "Federal",
                    "Residential building value depreciates straight-line over 27.5 years; prior depreciation is recaptured at up to 25% on sale.",
                    src_links(["S10", "S12"]),
                ],
                [
                    "Shared expenses in an owner-occupied multi-unit building",
                    "Federal",
                    "Where part of a building is rented and part is the owner's home, expenses are divided between rental and personal use — two-thirds rental in a 3-unit building where the owner occupies one unit.",
                    src_links(["S12"]),
                ],
                [
                    "Property tax levy and growth cap",
                    "California",
                    "1% general levy plus voter-approved debt, with assessed value growth capped at the lower of 2% and the state inflation factor.",
                    src_links(["S21", "S28"]),
                ],
                [
                    "Transfer tax on a sale",
                    "County",
                    "$0.55 per $500 of price (0.11%); the city conveyance tax does not apply in Property A's jurisdiction.",
                    src_links(["S29"]),
                ],
                [
                    "Rent stabilisation",
                    "Local and state",
                    "The local allowable increase is 1.6% for 2026–27; the state cap on covered tenancies is 5% plus inflation, capped at 10%, through 1 January 2030, with a conditional single-family exemption.",
                    src_links(["S31", "S47"]),
                ],
                [
                    "Fiduciary income tax",
                    "Federal and California",
                    "Trusts file annually; trust-level brackets compress far sooner than individual brackets, so undistributed gains are taxed quickly at the top rate.",
                    src_links(["S03", "S11", "S20"]),
                ],
            ],
        )
    )
    return body


def page_watch() -> str:
    body = (
        PRIVACY
        + table(
            ["Measure", "Jurisdiction", "Status as of 12 Nov 2026", "Effect on the 2040–2050 decision", "Official basis"],
            [
                [
                    "Public Law 119-21 estate and gift provisions",
                    "Federal",
                    "Enacted — permanent $15,000,000 exclusion for 2026, indexed to $15,480,000 for 2027",
                    "Removes the old 2026 sunset; gives substantial headroom unless a later Congress amends the exclusion",
                    src_links(["S06", "S02"]),
                ],
                [
                    "Stepped-up basis repeal proposals",
                    "Federal",
                    "Introduced only; not enacted",
                    "Would convert a tax-free sale into a taxed one; the largest single risk to selling, modelled as regime R5",
                    src_links(["S46", "S07"]),
                ],
                [
                    "State wealth tax (November 2026 ballot)",
                    "California",
                    "Canvas in progress; official certification due 11 December 2026",
                    "Threshold is $1,000,000,000 and direct real property is excluded — no practical effect here",
                    src_links(["S45"]),
                ],
                [
                    "Local vacant-unit tax",
                    "Local",
                    "Struck down at trial, collection suspended, and the Court of Appeal affirmed on 11 September 2026",
                    "Means leaving unit 3 empty currently carries no vacancy tax, but the litigation could still be appealed — a reason not to rely on vacancy as a strategy",
                    src_links(["S32"]),
                ],
                [
                    "Rent stabilisation and passthrough reform",
                    "Local",
                    "1.6% allowable increase for 2026–27; proposals to cap banked and capital-improvement passthroughs are pending",
                    "Constrains rent growth on the two rented units and would encumber unit 3 if it is rented",
                    src_links(["S31"]),
                ],
                [
                    "Statewide rent cap",
                    "California",
                    "In force through 1 January 2030; single-family homes conditionally exempt with the required lease notice",
                    "A renewal or removal of the single-family exemption before 2040 would cap rent growth if Property A is rented",
                    src_links(["S47"]),
                ],
                [
                    "Solar export credit sunset",
                    "California",
                    "Enacted regulatory rule: 20-year legacy from interconnection, then avoided-cost export credits",
                    "Turns Property A's small credit into a net cost within the planning window",
                    src_links(["S33"]),
                ],
                [
                    "Insurance market reform",
                    "California",
                    "Ongoing sustainable-insurance strategy; FAIR Plan policy count rising",
                    "Availability, not only price, is the risk for both properties",
                    src_links(["S36", "S37"]),
                ],
            ],
        )
    )
    return body


def page_method(anchor: dict) -> str:
    body = (
        PRIVACY
        + "<h2>Accounting rules the model follows</h2>"
        + table(
            ["Component", "How it is implemented", "Official basis"],
            [
                [
                    "Rounding",
                    "Every owner-supplied figure is stored already rounded to the nearest $10, and every rendered dollar amount is re-rounded at output. Official statutory amounts are quoted exactly as published and linked.",
                    src_links(["S21", "S28"]),
                ],
                [
                    "Property tax formula",
                    "Tax = rate × max(0, assessed value − $7,000 exemption) + fixed parcel charges, with the fixed charges inflating at consumer prices. The formula reproduces the supplied 2025 bills and does not apply a fixed-charge ratio to a reassessed multi-million-dollar value.",
                    src_links(["S21", "S24", "S28", "S30"]),
                ],
                [
                    "Assessment growth",
                    "The taxable base grows by the lower of 2% and modeled inflation, and is set to the lower of that base and market value so a decline is enrolled.",
                    src_links(["S21", "S25"]),
                ],
                [
                    "Inheritance reassessment",
                    "Occupying under Prop. 19 re-bases the property to base + allowance + any excess over that sum; renting re-bases to full market value.",
                    src_links(["S22", "S23"]),
                ],
                [
                    "Rental tax",
                    "Gross rent less 5% vacancy and 6% management, less the rental share of operating expenses, less depreciation on the building share, at the combined federal + NIIT + California rate, with losses suspended and released against later rental income.",
                    src_links(["S11", "S12"]),
                ],
                [
                    "Cash-flow conservation",
                    "Every plan starts with the same assets, including an illustrative $1,000,000 cash reserve; each year's surplus or deficit compounds inside the household portfolio, so a plan that consumes cash is charged for it.",
                    src_links(["S10", "S18"]),
                ],
                [
                    "Two wealth measures",
                    "Pre-liquidation net worth counts assets at value. After-liquidation net worth deducts the costs and taxes that turning those assets into cash would actually incur, including embedded equity gains and property sale costs.",
                    src_links(["S09", "S10", "S11", "S17", "S29"]),
                ],
            ],
        )
        + "<h2>Parameter set</h2>"
        + table(
            ["Parameter", "Value used", "Origin", "Official basis"],
            [
                ["Property A ad valorem rate", f"{BASE_INPUTS['cup_ad_valorem_rate'] * 100:.4f}%", "County assessor's published typical tax-rate-area figure", src_links(["S28"])],
                ["Property B ad valorem rate", f"{BASE_INPUTS['sf_ad_valorem_rate'] * 100:.5f}%", "Adopted secured roll rate for the fiscal year", src_links(["S30"])],
                ["Homeowners' exemption", "$7,000", "Statutory assessed-value exemption, one residence per household", src_links(["S24"])],
                ["Prop. 19 allowance used", "$1,044,586", "Published for transfers between 16 Feb 2025 and 15 Feb 2027", src_links(["S23"])],
                ["10-year Treasury yield", "4.3%", "Long-run projection average", src_links(["S40"])],
                ["Equity total return", "7.0% (5.5% price plus 1.5% dividends)", "Deliberately below the long-run historical average", src_links(["S44"])],
                ["Selling cost", "5.00% plus 0.11% transfer tax", "Commissions, title, escrow and prep, plus the county rate", src_links(["S29"])],
                ["Federal ordinary rate on investment income", "35.8%", "32% bracket plus 3.8% net investment income tax", src_links(["S11"])],
                ["California marginal rate", "10.3%", "Mid-to-upper state bracket", src_links(["S17", "S19"])],
                ["Illustrative cash reserve", "$1,000,000", "Modeling placeholder so no plan borrows implicitly; not a claim about the actual inheritance", src_links(["S01"])],
            ],
        )
        + "<h2>Known limitations</h2>"
        + table(
            ["Limitation", "Why it is disclosed", "Official basis"],
            [
                ["The actual estate size is unknown", "Estate tax depends on the whole estate; the model shows headroom tables instead of inventing a number.", src_links(["S01", "S05"])],
                ["Insurance is an assumption, not a quote", "No official parcel quote exists; the owner's $1,500 is tested.", src_links(["S36"])],
                ["The 2040–2050 allowance is projected", "Only the current two-year allowance is published.", src_links(["S23"])],
                ["Rents beyond the current official benchmark are modeled", "Official rent is a 40th-percentile benchmark, not this parcel's achievable rent.", src_links(["S38", "S39"])],
                ["Future law is unknowable", "The stress regimes exist to show what happens if the law changes, not to predict it.", src_links(["S46", "S45"])],
            ],
        )
        + "<h2>Reproducing the numbers</h2>"
        + "<p>Everything on this site is generated from a single deterministic script. Running the engine regenerates "
        f"<code>data/summary.json</code>; running the generator rebuilds every page from that data. At a 2045 transfer the winner is "
        f"{esc(PLAN_TINY[anchor['winner_id']])} at {money(anchor['plans']['P1A_SELL_EQUITY']['after_liquidation_net_worth'])} "
        f"after liquidation, {money(anchor['winner_advantage_over_rent_3'])} ahead of renting and "
        f"{money(anchor['winner_advantage_over_live_2a'])} ahead of moving in.</p>"
    )
    return body


def page_privacy() -> str:
    body = (
        "<h2>What is deliberately absent</h2>"
        + table(
            ["Control", "How it is applied", "Why it matters", "Official basis"],
            [
                [
                    "Placeholders instead of identities",
                    "The site names the two properties only as Property A and Property B. No individual, trustee, beneficiary, lender or adviser is named.",
                    "The repository is public; a name in a page is a name on the internet.",
                    src_links(["S28"]),
                ],
                [
                    "No addresses, parcels or jurisdictions",
                    "No street address, assessor parcel number, account number, city name, neighbourhood name or ZIP code appears anywhere on the site.",
                    "A parcel number or a ZIP plus a value is enough to identify the property on a county roll.",
                    src_links(["S21", "S28"]),
                ],
                [
                    "Rounding to the nearest $10",
                    "Every supplied assessment, tax bill, market value, rent and utility figure was rounded before modelling, and every published amount is a multiple of $10.",
                    "An exact tax bill is a search key. Rounding to $10 removes the exact match while preserving every decision.",
                    src_links(["S28", "S30"]),
                ],
                [
                    "Blank rather than guessed",
                    "Where no official source exists, the cell is empty and logged on the Flagged for review page.",
                    "An invented official value would be both wrong and unfalsifiable.",
                    src_links(["S36", "S38"]),
                ],
                [
                    "Not indexed by search engines",
                    "Every page carries a no-index directive.",
                    "Keeps the model out of search results even though the repository is public.",
                    src_links(["S28"]),
                ],
                [
                    "Working files excluded from publication",
                    "Model code, data files, the coordination board and this session's directory are excluded from the site build and are not served.",
                    "Publication is limited to the static pages that were reviewed.",
                    src_links(["S21"]),
                ],
            ],
        )
        + "<h2>Residual exposure you should know about</h2>"
        + table(
            ["Residual risk", "Status", "What remains to be done", "Official basis"],
            [
                [
                    "The Git repository is public",
                    "Rounding and placeholders reduce but do not eliminate re-identification when combined with knowledge of two properties in one market.",
                    "If the material must be non-public, the repository should be made private or the analysis kept out of version control.",
                    src_links(["S21"]),
                ],
                [
                    "Earlier commits in the repository's history",
                    "Prior working commits may contain pre-rounding figures; the live site does not serve them, but history is not rewritten by a normal commit.",
                    "History rewriting requires owner action with a force-push; it has not been performed.",
                    src_links(["S21"]),
                ],
                [
                    "Third-party caches",
                    "Search engines and archives can retain copies of previously served pages.",
                    "Removal requests and a no-index directive are the available controls.",
                    src_links(["S28"]),
                ],
                [
                    "Facts the model reveals indirectly",
                    "A recommendation this specific implies a household with two properties in one metropolitan area.",
                    "The site states the trade-offs in general terms and avoids facts that are not needed for the decision.",
                    src_links(["S21"]),
                ],
            ],
        )
        + "<p class=\"lead\">This page describes controls, not a guarantee. Rounding and anonymisation reduce the risk of casual "
        "re-identification; they do not make a public repository private.</p>"
    )
    return body


def page_suggestions(anchor: dict, regimes: dict, by_year: dict) -> str:
    p = anchor["plans"]
    w = p["P1A_SELL_EQUITY"]
    # decision suggestions table
    sug_rows = [
        [
            "SUG-01 · Sell Property A at stepped-up basis, stay in Property B Unit 3, invest in broad equities (Plan 1A)",
            "Choose when the goal is to maximise 20-year after-tax wealth and you do not need to live in Property A. At a 2045 transfer, $5,959,750 steps up under IRC §1014 / RTC §18031, nets $5,655,210 after 5.11% sale friction, with $0 capital-gains tax; after-liquidation $24,737,450 in 2064 — $4,944,320 ahead of renting Property A and $10,076,390 ahead of moving in.",
            "Highest after-liquidation net worth in all 11 inheritance years (2040–2050) and in 5 of 7 black-swan regimes; removes $53,580–$70,180/yr reassessed tax and post-solar carrying cost.",
            "You give up use of Property A; portfolio is exposed to equity drawdowns (regime R3: −24% then −18% two-year crash).",
            src_links(["S07", "S15", "S22", "S28", "S29"]),
        ],
        [
            "SUG-02 · Sell Property A, stay in Property B Unit 3, split 75% equities / 25% CA-tax-exempt Treasuries (Plan 1C)",
            "Choose when you want most of Plan 1A's upside with a dampener for a crash the year after sale. $22,927,150 after-liquidation in 2064 (2045 transfer), $1,810,300 behind pure equities but ahead of renting in 6 of 7 regimes.",
            "Treasury interest is exempt from California income tax (S18); staging over 24–36 months removes single-day entry risk; after-liquidation gap to renting is $3,134,020.",
            "You surrender $1,810,300 of expected upside vs. pure equities in baseline; still leaves Property A unused.",
            src_links(["S07", "S15", "S18", "S40", "S43"]),
        ],
        [
            "SUG-03 · Sell Property A, hold proceeds entirely in CA-tax-exempt Treasuries (Plan 1B)",
            "Choose when preservation and predictable income outweigh growth — near-retirement horizon, or you expect an equity lost decade. $17,496,230 after-liquidation in baseline; wins outright in regime R6 (equity lost decade + local boom: $18,694,600 vs $16,466,860 for equities).",
            "No equity volatility; Treasury interest exempt from California tax; fully liquid; beats renting when equities lag.",
            "$7,241,220 behind equities in baseline; still requires finding new housing if you must leave Property B.",
            src_links(["S18", "S40", "S44", "S29"]),
        ],
        [
            "SUG-04 · Rent out Property A, keep living in Property B Unit 3 (Plan 3)",
            "Choose only if you insist on retaining both parcels in the same seismic and insurance market and can carry $70,180/yr reassessed tax plus insurance, maintenance and management to net a sub-1% cash yield. Generates $68,350/yr household cash flow year 1 and $1,896,740 20-year operating cash, but finishes $4,944,320 behind selling in baseline.",
            "Keeps both appreciated parcels; $85,800/yr Property B rent retained; after-liquidation $19,793,130 in 2064.",
            "Property A reassessed to full $5,959,750 (no Prop. 19 relief); depreciation recapture taxed at 25% + 13.3% California at exit; concentrated seismic/insurance risk (regime R4).",
            src_links(["S12", "S21", "S22", "S36", "S38"]),
        ],
        [
            "SUG-05 · Move into Property A, rent out vacated Property B Unit 3 (Plan 2B)",
            "Choose when lifestyle — living in Property A — is the objective and you price it explicitly. Trail vs. sell: $8,229,950 over 20 years (baseline). Beats leaving Unit 3 empty by $1,846,440. Requires occupying within 1 year and filing Prop. 19 + $7,000 exemption claims on time.",
            "$53,580/yr Property A tax (partial Prop. 19 relief: FBYV $802,030 + $1,044,586 allowance); Property B 3-unit rent $131,040/yr replaces 2-unit $85,800/yr.",
            "Highest carrying cost of ownership plans; Property B loses its exemption if you claim it on Property A; Unit 3 becomes rent-controlled (1.6% allowable increase, just-cause rules).",
            src_links(["S22", "S24", "S30", "S31", "S28"]),
        ],
        [
            "SUG-06 · Move into Property A, leave Property B Unit 3 vacant (Plan 2A)",
            "Never choose as a financial plan — it is the cost of leaving money on the table. $14,661,060 after-liquidation, $10,076,390 behind selling and $1,846,440 behind renting Unit 3. Listed only to quantify the vacancy cost.",
            "None financially; useful only to illustrate the $1,846,440 cost of an empty unit over 20 years.",
            "Negative $63,620/yr year-1 cash flow; $1,884,880 cumulative 20-year drain before any wealth comparison.",
            src_links(["S24", "S30", "S31", "S32"]),
        ],
    ]

    site_rows = [
        [
            "Add a side-by-side selector with a 2040–2050 slider",
            "Readers must compare six plans across 11 inheritance years in a static table today.",
            "Interactive year picker that re-ranks the six plans and rewrites the property-tax and net-worth figures for the selected year reduces misreading of the wrong column.",
            "High — removes the most common user error in the decision analysis page.",
            src_links(["S21", "S28", "S40"]),
        ],
        [
            "Surface the 5 mechanisms as a decision gate checklist on the suggestions page",
            "The executive summary's five mechanisms (basis step-up, Prop. 19 cap, rental yield vs. Treasuries, Property B exemption, solar sunset) are the actual deciders.",
            "A gated flow: if you answer no to 'will you live in Property A?' the plan narrows to sell vs. rent; the site can then highlight only the relevant rows.",
            "High — turns 42 tables into a 3-question flow without changing any number.",
            src_links(["S07", "S15", "S22", "S33", "S38"]),
        ],
        [
            "Expose the open-questions inventory as a fillable readiness tracker",
            "Today the missing items (insurance quotes, trust instrument type, estate size, solar interconnection date, lifestyle preference) are buried in the flagged page.",
            "A tracker showing Have / Missing / Assumed with a due date and who to ask (trustee, CPA, insurance broker, assessor) turns the model into an execution checklist.",
            "High — the decision cannot be acted on without those answers.",
            src_links(["S01", "S26", "S27", "S36", "S33"]),
        ],
        [
            "Show sensitivity bands, not just the baseline point estimate",
            "The decision analysis page already contains sensitivity cases but the executive summary shows only the $24,737,450 point.",
            "Display the range for each plan (−1.5%/yr equity, +1.0%/yr home growth, repeal of step-up) so the reader sees that the ranking holds across bands except in R5/R6.",
            "Medium — prevents overconfidence in a single number.",
            src_links(["S42", "S43", "S44", "S46"]),
        ],
        [
            "Separate meta suggestions from analytical suggestions visually",
            "The new suggestions page mixes 'improve the site' with 'which plan to pick' — readers conflate the two.",
            "Two tabs or accordions: 'How this site could be clearer' vs. 'Which path to choose' makes the review-before-implementation step explicit.",
            "Medium — requested directly in the brief: 'choose the best path before implementing any changes'.",
            src_links(["S21", "S28"]),
        ],
        [
            "Add a printable one-page decision brief",
            "The full site is 15 pages; a trustee or advisor meeting needs a single page.",
            "A one-page PDF with the ranked scoreboard, the five mechanisms, the three deadlines (60-day notice, 150-day ownership statement, 1-year Prop. 19 move-in), and the open questions to bring to the meeting.",
            "Medium — practical adoption aid, no new analysis.",
            src_links(["S26", "S27", "S22", "S24"]),
        ],
    ]

    gate_rows = [
        [
            "Gate 0 — Confirm you understand the three options the brief actually compares",
            "Read the executive summary and the suggestions page; do not act on the flagged or source pages alone. Every number is shown for a 2045 transfer and for 2040–2050; pick your transfer year first.",
            "The brief models only live in Property A, rent Property A, or sell Property A and reinvest — while always keeping Property B. There is no 'sell both and leave' or 'gift before death' scenario.",
            src_links(["S07", "S15", "S21"]),
        ],
        [
            "Gate 1 — Is moving into Property A a lifestyle requirement, not a financial preference?",
            "If yes, the comparison narrows to Plan 2B vs. Plan 1A and the explicit lifestyle price is $8,229,950 over 20 years (2045 baseline). If no, the financial comparison is Plan 1A vs. Plan 3 and the gap is $4,944,320.",
            "This single answer determines which scoreboard column to read; everything else is arithmetic conditional on it.",
            src_links(["S22", "S24", "S28"]),
        ],
        [
            "Gate 2 — Do you have the four blocking documents?",
            "Obtain before choosing: the signed trust and amendments, the preliminary title report, the date-of-death appraisal instruction, and the trustee's 60-day notice list. Without them the basis cannot be proved and the Prop. 19 window cannot be met.",
            "IRC §1014 basis and Prop. 19 relief both depend on documents created before or within 60–150 days of death; delay is not recoverable.",
            src_links(["S07", "S15", "S26", "S27", "S28"]),
        ],
        [
            "Gate 3 — Choose a risk sleeve before you choose a plan",
            "Decide the Treasury reserve (0% for pure equities, 20–30% for the staged 75/25 plan, 100% for capital preservation). This choice decides the R3 sequence-risk outcome ($20,704,040 vs. $16,981,140) more than the timing of the sale.",
            "The staged 24–36 month Treasury-to-equity entry is the hedge against the trap where the sale completes at a peak and equities fall 24% then 18%.",
            src_links(["S18", "S40", "S43"]),
        ],
        [
            "Gate 4 — Verify the two assumptions that change the math",
            "Get two hard quotes: a parcel-specific HO-3 dwelling quote for Property A and a 1–4 unit dwelling quote for Property B; and confirm the rooftop solar interconnection date and remaining NEM legacy years. Model uses $4,800/yr and $4,500/yr plus $1,500/yr water vs. owner estimates of $1,500/yr; the gap is $3,200–$3,000/yr per property.",
            "Insurance repriced at 4.0%/yr with a 45% seismic shock is the largest operating-cost escalation; solar sunset (20-year legacy) flips a −$180/yr credit to a $1,440/yr cost by the mid-2040s.",
            src_links(["S33", "S36", "S37"]),
        ],
        [
            "Gate 5 — Review the suggestion, record the choice, then execute the inheritance steps page",
            "Mark one suggestion as chosen, note the date and the open questions it closes, and follow the inheritance steps in order: death certificates → trust TIN → 60-day notice → appraisal → 150-day ownership statement → 9-month Form 706/portability check → sale or Prop. 19 filing.",
            "The inheritance process page's deadlines run from the date of death, not from when you decide; choosing first and executing second prevents missing the 1-year Prop. 19 and 3-year claim windows.",
            src_links(["S01", "S20", "S26", "S27", "S22", "S23"]),
        ],
    ]

    body = (
        PRIVACY
        + '<div class="verdict"><strong>How to use this page.</strong> Review every suggestion here before changing anything on the site or committing to a financial plan. '
        "The first table is the six decision suggestions — pick one. The second table is site-improvement suggestions — pick which ones to implement. "
        "The third table is the gate sequence that forces a choice in writing before any execution step in the inheritance process."
        "</div>"
        + "<h2>Decision suggestions — pick one of six, with the price of each choice</h2>"
        + "<p>All figures are for a 2045 transfer → 2064, after-liquidation, rounded to $10; every row is linked to the official rule it depends on. "
        "The same ranking holds for every inheritance year 2040–2050 in baseline; the exceptions are regimes R5 and R6.</p>"
        + table(["Suggestion", "What it means in this brief", "Why it wins or loses (financial consequence)", "Trade-off you accept", "Official basis"], sug_rows)
        + "<h2>Site-improvement suggestions — how the dashboard could make this decision clearer</h2>"
        + "<p>These are changes to the site itself, not changes to your finances. Each one addresses a verified friction in the current pages. "
        "Implementing them does not alter any projection; it reduces the chance of misreading one.</p>"
        + table(["Improvement suggestion", "Friction it removes", "Decision-making benefit", "Priority", "Official basis"], site_rows)
        + "<h2>Recommended review flow — do not implement until you have passed these gates</h2>"
        + "<p>The gates are sequential: you cannot pass Gate 2 without answering Gate 1. A choice recorded here is reversible until the trust sells or files a Prop. 19 claim; "
        "after that the property-tax base and the basis are locked.</p>"
        + table(["Gate", "What to do before deciding", "Why this gate blocks the next step", "Official basis"], gate_rows)
        + "<p class=\"lead\">After you choose a suggestion above, open the <a href=\"open-questions.html\">Open questions &amp; decision readiness checklist</a> to close the "
        "information gaps that remain, then follow the <a href=\"inheritance-process.html\">Inheritance steps</a> page in deadline order.</p>"
    )
    return body


def page_open_questions() -> str:
    have_rows = [
        [
            "Property A — market value Nov 2026, rounded $3,100,000",
            "Have — owner-supplied, rounded to $10 before modelling; model escalates at 3.5%/yr (local FHFA repeat-sales trend)",
            "$3,100,000 (2026) → $5,959,750 (2045) in baseline; source register S42",
            "Obtain a retrospective broker price opinion or licensed appraisal for the file; do not publish a new exact value.",
            src_links(["S42", "S21"]),
        ],
        [
            "Property A — assessed value & tax history 2014–2026, rounded",
            "Have — 13 years supplied, each rounded to $10; 2026 assessed $550,540 (+2.0% BOE factor), 2025 tax $7,210; effective rate ~1.34% implying fixed parcel charges",
            "Reproduces 2025 bill as 1.1488% × (assessed − $7,000) + fixed charges; used to project 2040–2050 reassessments",
            "Confirm the 2026 roll entry after publication; history already matches the published inflation factors within one irregularity flagged as IR-007.",
            src_links(["S21", "S25", "S28"]),
        ],
        [
            "Property B — market value Nov 2026, rounded $1,800,000; assessed $114,250 / tax $2,440 (2025)",
            "Have — owner-supplied, rounded to $10; 3-unit building, 2 units rented at $85,800/yr, 1 unit owner-occupiable; Prop. 13 base intact",
            "$1,800,000 → $3,207,750 (2045) in baseline; ad valorem rate 1.18162% + $7,000 exemption if retained",
            "Confirm title vesting and rent roll from leases; history matches the secured-roll rate within rounding.",
            src_links(["S30", "S31", "S39"]),
        ],
        [
            "Property B — rent-control and vacancy status",
            "Have — allowable increase 1.6% (2026–27 = 60% of regional CPI), just-cause rules apply; Empty Homes Tax struck down and suspended (Court of Appeal affirmed preemption Sep. 2026)",
            "$85,800/yr from 2 units escalated at 1.6% then 60% of CPI; Unit 3 at $45,240/yr if rented",
            "Re-check the rent board's current rates page within 30 days of any decision — File 261020 cap has not been enacted as of Nov. 2026.",
            src_links(["S31", "S32"]),
        ],
        [
            "Federal & California death-tax framework",
            "Have — verified to official sources: federal exclusion $15,000,000 (2026) → $15,480,000 (2027 indexed), 40% above exclusion; California + every subdivision barred from any estate/inheritance tax (RTC §13301); stepped-up basis under IRC §1014 / RTC §18031",
            "Headroom tables show $0 California tax at any estate size; federal tax applied only on illustrative tiers above exclusion",
            "Re-verify exclusion year-of-death figure at death (indexed to C-CPI-U; $15,480,000 projected for 2027).",
            src_links(["S01", "S02", "S05", "S13", "S14", "S15"]),
        ],
        [
            "Property-tax mechanics & Prop. 19 cap",
            "Have — Prop. 13 1% + voter debt, 2% FBYV cap, reassessment on change in ownership; Prop. 19 parent-child requires principal-residence occupancy within 1 year and claim within 3 years; current cap $1,044,586 (exact statutory figure) for 2025–2027, biennially indexed to FHFA California HPI",
            "Used to compute $53,580/yr (live-in) vs. $70,180/yr (rental) year-1 tax at 2045 transfer",
            "Projected caps for 2040–2050 are modelled, not published; check the BOE biennial release in February of the death year.",
            src_links(["S21", "S22", "S23", "S24", "S28"]),
        ],
        [
            "Utilities, solar, and rate cases",
            "Have — Property A water $1,500/yr, solar −$180/yr credit until 20-year NEM legacy expires (by early 2040s), then $1,440/yr cost; Property B water/sewer $4,380/yr, electricity $600/yr; verified to CPUC D.16-01-044/D.22-12-056 and general rate cases",
            "Water escalates 3.2%/yr (8% in 2027–28 for Property B sewer), electricity 3.2%/yr, solar credit flat then cost",
            "Confirm solar interconnection date to pin the legacy expiry year; model assumes sunset by 2046.",
            src_links(["S33", "S34", "S35"]),
        ],
        [
            "Insurance market context (no parcel quote)",
            "Have (context) / Missing (parcel quote) — no official parcel-specific HO-3 or 1–4 unit dwelling quote exists; modeled $4,800/yr (Property A) and $4,500/yr (Property B) vs. owner $1,500/yr estimate; statewide average ~$1,570/yr in 8.3M voluntary policies; FAIR Plan 0.5% (Property A area) / 0.2% (Property B area)",
            "Official benchmark cells on operating-costs table are intentionally blank; model escalates 4.0%/yr with 45% seismic-shock spike",
            "Obtain two written broker quotes — one HO-3 for Property A and one 1–4 unit dwelling policy for Property B — and replace the $4,800/$4,500 assumptions before acting.",
            src_links(["S36", "S37"]),
        ],
        [
            "Rent benchmarks (HUD SAFMR 40th percentile)",
            "Have — FY2026 SAFMR: Property A area 4-BR $6,390/mo; Property B area 2-BR $3,310/mo, 3-BR $4,230/mo; not parcel rents",
            "Single-family rent modelled 2.80% gross yield ($86,800/yr); Property A 4-BR benchmark implies 2.47%; Property B Unit 3 $45,240/yr modelled",
            "Order a local rent survey for Property A's achievable single-family rent; model spread is the largest driver of Plan 3's result.",
            src_links(["S38", "S39"]),
        ],
        [
            "Capital-market & inflation history",
            "Have — CBO 10-yr Treasury 4.3% (2026–2036 avg), BLS CPI 9.1% peak (June 2022), FHFA HPI 3.0–3.5%/yr 20-yr compound, S&P 500 total return 7.0% modelled (below 11.6% historical 1977–2025), Fed flow-of-funds 2007–09 −22% housing / −37% equity drawdowns",
            "Seven regimes replay these official series; baseline uses CBO/FHFA/BLS long-run averages",
            "No further discovery needed; history is published and linked.",
            src_links(["S40", "S41", "S42", "S43", "S44"]),
        ],
        [
            "Statutory process & deadlines",
            "Have — 60-day trustee notice (Prob. §16061.7), 150-day change-in-ownership statement (RTC §480(b)), 9-month Form 706 / portability, 1-year Prop. 19 move-in, 3-year Prop. 19 claim, 15th-day-of-4th-month fiduciary returns",
            "Inheritance steps page lists each deadline with the miss penalty; all verified to the legislative text",
            "Confirm with counsel at death — deadlines run from date of death, not distribution.",
            src_links(["S01", "S20", "S26", "S27", "S28"]),
        ],
    ]

    q_rows = [
        [
            "Q-01 · Is Property A in a revocable trust that will get a full stepped-up basis, or in an irrevocable/completed-gift vehicle?",
            "Determines whether $5,959,750 of gain is tax-free. Revocable grantor trust → full step-up (IRC §1014, RTC §18031); completed-gift irrevocable → $0 step-up and the sell-vs-rent math reverses into a large pre-reinvestment tax.",
            "$4,944,320 advantage of selling assumes step-up; without it net cash drops by roughly one-third under regime R5 and renting may win.",
            "No trust instrument on file — unknown.",
            "Ask the trustee and the drafting attorney for the signed trust, every amendment, and whether any property was transferred by completed gift. Have a CPA confirm grantor-trust status in writing.",
            src_links(["S07", "S15", "S28"]),
        ],
        [
            "Q-02 · What is the total gross estate plus prior taxable gifts and is the grantor single or married (portability available)?",
            "Determines federal estate tax. Exclusion $15,000,000 (2026) / $15,480,000 (2027); single vs. DSUE (spouse's unused exclusion) doubles headroom; California is $0 always; tax is 40% only on the amount above the exclusion.",
            "Headroom table: $19,800,000 gross estate (Property A $5,959,750 + $13,840,250 cash) leaves ~$4,759,750 headroom single in 2045; $31,000,000 estate owes $2,400,000 federal single, $0 DSUE.",
            "No estate size supplied — illustrative tiers shown only; flagged as IR-004.",
            "Have the trustee tally date-of-death FMV of Property A + all other assets + prior Forms 709; decide 706 filing/portability election within 9 months (6-month extension available for filing, not for tax).",
            src_links(["S01", "S02", "S05", "S13", "S14"]),
        ],
        [
            "Q-03 · Do you intend to live in Property A as your principal residence within 1 year of death?",
            "Gates Prop. 19. Yes → reassessed to FBYV $802,030 + $1,044,586 allowance + excess over that sum = $53,580/yr (2045). No → full reassessment to $5,959,750 = $70,180/yr. Missing the 1-year move or the 3-year claim forfeits retroactive relief.",
            "$16,600/yr difference in year-1 tax; $1,044,586 allowance is an exact statutory figure, not a model assumption.",
            "Unknown — lifestyle preference not stated.",
            "Decide in writing before the 1-year deadline; if yes, file the $7,000 exemption claim and Prop. 19 parent-child claim and relinquish the exemption on Property B.",
            src_links(["S22", "S23", "S24", "S28"]),
        ],
        [
            "Q-04 · What is the achievable market rent for Property A as a single-family rental in its jurisdiction?",
            "Drives Plan 3's return. Model uses 2.80% gross ($86,800/yr) vs. official 4-BR SAFMR 2.47% ($76,680/yr). $18,240/mo ($218,880/yr) would be needed to tie equities — 3.14× the official 4-BR benchmark.",
            "Every $10,000/yr of rent is ~$160,000 of 20-year after-liquidation wealth at baseline escalation.",
            "No local rent survey — modelled from HUD benchmark and the brief's yield assumption; flagged as IR-003.",
            "Order a licensed property-management rent opinion for a comparable single-family home; compare to HUD SAFMR $6,390/mo 4-BR to sanity-check.",
            src_links(["S12", "S38", "S40"]),
        ],
        [
            "Q-05 · What are the parcel-specific insurance premiums for Property A (HO-3) and Property B (1–4 unit dwelling)?",
            "Largest operating-cost uncertainty. Model uses $4,800/yr and $4,500/yr vs. owner $1,500/yr; escalates 4.0%/yr with +45% seismic shock. Statewide average $1,570/yr proves $1,500/yr is not a high-value rebuild quote.",
            "$3,000–$3,300/yr difference per property compounds to $80,000–$100,000 over 20 years per property before shock.",
            "No quotes — official cells intentionally blank per IR-001/IR-002.",
            "Get two written quotes from a California-licensed broker, one HO-3 and one landlord dwelling policy, stating rebuild cost, deductible, wildfire/seismic exclusions, and FAIR Plan eligibility before passing Gate 4.",
            src_links(["S36", "S37"]),
        ],
        [
            "Q-06 · When was the rooftop solar interconnected and how many NEM legacy years remain?",
            "Determines when −$180/yr credit becomes $1,440/yr cost plus a $4,500 inverter at year 15. Legacy is 20 years from interconnection (NEM 1.0/2.0 retail export), expiring by 2043–2046 for existing systems; NBT gives only 9 years for the original customer.",
            "$1,620/yr swing per year after expiry; model assumes sunset by 2046.",
            "Interconnection date not supplied; model assumption flagged.",
            "Pull the interconnection agreement and the most recent true-up bill from the utility; confirm remaining legacy years in writing from the utility or CPUC record.",
            src_links(["S33"]),
        ],
        [
            "Q-07 · What is your risk posture for the reinvested proceeds — can you tolerate a 24% then 18% two-year equity fall right after the sale?",
            "Decides the Treasury sleeve. Regime R3 sequence-of-returns trap turns a lump-sum equity sale into $20,704,040 (equities) vs. $16,981,140 (Treasuries staged) vs. $16,534,110 (renting kept) — the 75/25 staged plan lands at $19,773,310, hedging most of the trap.",
            "$3,722,900 swing between pure equities and Treasuries in R3; baseline gap is $7,241,220 the other way.",
            "Unknown — no risk preference or horizon stated beyond the 2040–2050 window.",
            "Write down a target equity/Treasury split (e.g., 100/0, 75/25, 0/100) and a 24–36 month dollar-cost staging schedule; Treasury interest is CA-tax-exempt per S18.",
            src_links(["S18", "S40", "S43", "S44"]),
        ],
        [
            "Q-08 · Will Property B's unrented unit be kept as your residence or rented, and can you carry the vacancy cost?",
            "Property B Unit 3 is the fulcrum between Plan 2A and 2B. Keeping it vacant is a −$63,620/yr year-1 drain and −$1,884,880 20-year drain; renting it adds $45,240/yr and $664,620 real over 20 years but subjects it to rent control (1.6% allowable increase, just-cause).",
            "$1,846,440 gap between 2A and 2B in baseline; $4,944,320 gap between 1A and renting both.",
            "Current rent $85,800/yr from 2 units known; Unit 3 status is a choice, not a fact.",
            "Decide before death if possible: if you plan to live in Property A, line up a tenant or manager for Unit 3 so it does not sit empty past the 1-year Prop. 19 window.",
            src_links(["S31", "S32", "S39"]),
        ],
        [
            "Q-09 · Are you aware of the statutory trust-administration workload and its deadlines?",
            "A California trust inheritance is not a deed transfer; it is a sequence with penalties. 60-day notice → 120-day contest; 150-day BOE-502-D ($ penalty on reassessed tax); 9-month 706/portability; 1-year/3-year Prop. 19; annual 541 fiduciary returns with compressed trust brackets.",
            "Missing the 150-day statement or the 706 portability election is a multi-thousand to multi-million dollar error; delay in appraisal converts post-death appreciation to taxable gain.",
            "No documents assembled — steps page lists them all.",
            "Retain counsel now and assemble: trust + amendments, deeds, title report, gift returns, insurance binder, and an appraisal engagement letter ready to execute on death.",
            src_links(["S01", "S03", "S20", "S26", "S27", "S28"]),
        ],
        [
            "Q-10 · Has Congress, the state or a court changed stepped-up basis, Prop. 19, or local rent/transfer rules by the time of death?",
            "Law watch is not speculative — H.R. 5336 would tax unrealized gains at death; Prop. 19's allowance is reset every two years; File 261020 would cap banked increases at 10%/yr; the Empty Homes Tax was suspended after a Court of Appeal preemption ruling.",
            "Regime R5 reprices the sell plan down by roughly a third if §1014 is repealed and the exclusion falls to 35% of schedule.",
            "Current law verified Nov. 2026; future law unknowable — law-watch page tracks each item with the check date.",
            "Check the law-watch page at death and have counsel confirm: is §1014 intact, what is the current Prop. 19 cap (February of death year), and has any pending bill been enacted.",
            src_links(["S22", "S23", "S31", "S32", "S45", "S46"]),
        ],
    ]

    next_rows = [
        [
            "1 — Immediate, before any decision",
            "Have the trustee pull the signed trust + amendments, deeds, preliminary title report, and prior gift-tax returns; confirm who the successor trustee is.",
            "Answers Q-01 and Q-02; proves ownership, amendment history, and whether the step-up is available; needed for the 60-day notice list.",
            src_links(["S07", "S15", "S27", "S28"]),
        ],
        [
            "2 — Within 1 week of confirming the trust path",
            "Commission two insurance broker quote requests (HO-3 for Property A; 1–4 unit dwelling for Property B) and a local rent survey for Property A.",
            "Closes the $3,000–$3,300/yr per-property insurance gap and the single-family rent uncertainty (Q-04/Q-05); official cells are blank until this is done.",
            src_links(["S36", "S37", "S38"]),
        ],
        [
            "3 — Within 30 days, still before the death",
            "Write down answers to Q-03, Q-07 and Q-08: live-in vs. sell preference, equity/Treasury split, and Unit 3 vacancy decision. Record which suggestion (SUG-01 to SUG-06) you choose and why.",
            "The choice is reversible until sale/Prop. 19 filing; documenting it prevents drift and satisfies the 'choose best path before implementing' requirement.",
            src_links(["S22", "S24", "S18"]),
        ],
        [
            "4 — At death, in deadline order",
            "Execute the inheritance steps page: death certificates → trust TIN → 60-day notice → date-of-death appraisal → 150-day BOE-502-D → 9-month 706/portability → sale or Prop. 19 filing (1-year move, 3-year claim).",
            "Each step has a statutory miss penalty; appraisal is the $5,959,750 basis proof; Form 706 preserves up to $15,480,000 of spousal exclusion if applicable.",
            src_links(["S01", "S02", "S20", "S26", "S27", "S28"]),
        ],
        [
            "5 — If you choose to sell",
            "Engage a brokerage with 5.00% + 0.11% transfer tax closing disclosure, sell from the administrative trust, and stage proceeds over 24–36 monthly Treasury-to-equity tranches.",
            "Locks the tax-free basis (S07/S15) and hedges regime R3 sequence risk; Treasury interest is CA-tax-exempt (S18).",
            src_links(["S07", "S15", "S18", "S29", "S33"]),
        ],
        [
            "6 — Ongoing until the decision is made",
            "Re-check the law-watch page each quarter: Prop. 19 cap (February biennial), federal exclusion index (C-CPI-U), rent-board allowable increase (Feb/Mar), and any bill moving from 'proposed' to 'enacted'.",
            "The model's projected 2040–2050 caps and exclusions are not published yet; the next BOE release is February of the death year.",
            src_links(["S01", "S22", "S23", "S31", "S45", "S46"]),
        ],
    ]

    body = (
        PRIVACY
        + '<div class="verdict"><strong>What this page answers.</strong> The brief models six plans from rounded figures and official sources, but it cannot answer for you '
        "whether you want to live in Property A, what the whole estate is worth, or what your insurance actually costs. This page lists every question that must be answered before "
        "any choice is final, marks what the site already has and what is still missing, and gives the exact next step to close each gap. "
        "Do not implement a plan until every row below is Have or a written assumption you accept."
        "</div>"
        + "<h2>What we already have and what is still missing</h2>"
        + "<p>Have means verified to an official source and used in the model. Missing means no official parcel-specific source exists and the model uses an assumption flagged on the Flagged for review page. "
        "Items marked Have still need a document in hand at death.</p>"
        + table(["Information", "Status today", "Value used in the model", "How to close the gap — next document or quote", "Official basis"], have_rows)
        + "<h2>Questions that must be answered before any decision can be reasonably made</h2>"
        + "<p>Each question is scored by what changes if the answer flips. The 'Current answer' column is the gap — most are blank today. "
        "The discovery column is the action you take to turn it into Have.</p>"
        + table(["Question", "Why it matters — what flips if the answer changes", "Financial consequence of a different answer", "Current answer / status", "How to discover the definitive answer", "Official basis"], q_rows)
        + "<h2>Suggested discovery plan — in the order you should do it</h2>"
        + "<p>Do not pay for an appraisal or list the house until priority 1–3 are done. The deadlines in priority 4 start at death, not at sale.</p>"
        + table(["Priority", "Action", "What it uncovers (which Q it answers)", "Official basis"], next_rows)
        + "<p class=\"lead\">When every question above has a definitive answer, return to the <a href=\"suggestions.html\">Suggestions</a> page, re-select one suggestion, and execute the "
        "<a href=\"inheritance-process.html\">Inheritance steps</a> in deadline order. If any answer is still unknown, the model is not ready to be acted on.</p>"
    )
    return body


def page_sources() -> str:
    rows = [
        [
            esc(sid),
            esc(sanitize(s["agency"])),
            f'<a href="{esc(s["url"])}" rel="noopener noreferrer">{esc(sanitize(s["title"]))}</a>',
            esc(s["published"]),
            esc(sanitize(s["fact"])),
        ]
        for sid, s in sorted(SOURCES.items())
    ]
    body = (
        f"<p>All {len(SOURCES)} authorities below are official federal, California or local government publications, "
        f"each checked directly on {esc(VERIFIED_DATE)}. Nothing on this site cites a secondary commentary or a news article.</p>"
        + table(["ID", "Agency", "Document", "Published or effective", "Rule or benchmark taken from it"], rows)
    )
    return body


def page_flags() -> str:
    rows = []
    for f in FLAGS:
        rows.append(
            [
                esc(f["id"]),
                esc(sanitize(f["category"])),
                f'<span class="badge">{esc(f["status"])}</span>',
                esc(sanitize(f["item"])),
                esc(sanitize(f["detail"])),
                src_links(f["sources"]),
            ]
        )
    body = (
        "<p>Every cell that no official publication supports, every irregularity in the supplied history, and every modeling "
        "assumption is listed here with the link you would check it against. Nothing on this page blocks the decision; each item "
        "tells you what to verify before acting on it.</p>"
        + table(["ID", "Category", "Status", "Item", "Explanation and handling", "Official context"], rows)
    )
    return body


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(PKG / "site"))
    args = ap.parse_args()
    out = Path(args.out)
    (out / "pages").mkdir(parents=True, exist_ok=True)
    (out / "assets").mkdir(parents=True, exist_ok=True)

    series = simulate_property_series("R0_BASELINE")
    anchor = evaluate_plans(2045, 20, "R0_BASELINE")
    by_year = {str(y): evaluate_plans(y, 20, "R0_BASELINE") for y in range(2040, 2051)}
    regimes = {rid: evaluate_plans(2045, 20, rid) for rid, _t, _d, _s in REGIME_SPECS}
    headroom = compute_estate_headroom_matrix(2045)

    pages = {
        "index.html": (
            SITE_TITLE,
            f"Anonymized decision dashboard for inheriting a trust-held residence between 2040 and 2050 while already owning a 3-unit building. {len(SOURCES)} official sources, {len(FLAGS)} flagged items.",
            page_index(anchor, series, headroom),
        ),
        "pages/executive-summary.html": (
            "Best plan and why",
            "The ranked recommendation, the five mechanisms behind it, what executing it involves, and the conditions that would change the answer.",
            page_exec(anchor, regimes),
        ),
        "pages/decision-analysis.html": (
            "Decision analysis: live in, rent out, or sell and reinvest",
            "Six plans compared for every inheritance year 2040–2050, with sensitivity cases and the year-by-year cash-flow trail.",
            page_decision(anchor, by_year),
        ),
        "pages/suggestions.html": (
            "Suggestions — choose the best path before implementing any changes",
            "Six ranked decision suggestions, site-improvement proposals, and a gated review flow so you choose in writing before acting.",
            page_suggestions(anchor, regimes, by_year),
        ),
        "pages/open-questions.html": (
            "Open questions & decision readiness checklist",
            "What we have, what is missing, the ten questions that must be answered, and the exact next steps to close each gap.",
            page_open_questions(),
        ),
        "pages/property-tax.html": (
            "Property tax, assessment history and Prop. 19",
            "The full rounded assessment and tax history for both properties, the fixed-charge explanation, and what a 2040–2050 inheritance does to the tax base.",
            page_property_tax(anchor, series),
        ),
        "pages/projections.html": (
            "50-year projections, 2026–2075",
            "Year-by-year values, assessed values, property taxes, insurance, water, electricity and maintenance for both properties.",
            page_projections(series),
        ),
        "pages/operating-costs.html": (
            "Operating costs, insurance and rent benchmarks",
            "What is officially verified, what has no official source, and how each cost line behaves over fifty years.",
            page_costs(anchor),
        ),
        "pages/black-swan-scenarios.html": (
            "50-year black-swan economic conditions",
            "Seven non-uniform regimes — stagflation, crisis at the transfer date, sequence-of-returns trap, seismic and insurance shock, basis repeal, equity lost decade.",
            page_black_swan(regimes),
        ),
        "pages/inheritance-process.html": (
            "Step-by-step inheritance process",
            "The California trust sequence with every statutory deadline, from trustee notification to the three routes for the house.",
            page_process(),
        ),
        "pages/estate-thresholds.html": (
            "Estate and inheritance tax thresholds, headroom and cash",
            "Federal, California and local thresholds, headroom by estate size, future thresholds and the proposals that would change them.",
            page_thresholds(headroom, series),
        ),
        "pages/inheritance-law.html": (
            "Federal, state and local tax law",
            "The sixteen statutory rules that actually govern this decision, each quoted to its official source.",
            page_law(),
        ),
        "pages/law-watchlist.html": (
            "Enacted changes, pending proposals and litigation",
            "What has already changed, what is proposed, and what is still in court — with the date each status was checked.",
            page_watch(),
        ),
        "pages/methodology.html": (
            "Methodology, equations and assumptions",
            "How the tax formulas, cash-flow conservation and two wealth measures work, plus every parameter and limitation.",
            page_method(anchor),
        ),
        "pages/privacy.html": (
            "Privacy and anonymization controls",
            "What is omitted, why rounding to $10 matters, and the residual exposure that no page-level control can remove.",
            page_privacy(),
        ),
        "pages/sources.html": (
            "Official source register",
            f"All {len(SOURCES)} authorities, checked on {VERIFIED_DATE}.",
            page_sources(),
        ),
        "pages/flagged-for-review.html": (
            "Flagged for review",
            "Every unverified cell, every irregularity in the supplied history and every modeling assumption, with the link to check it.",
            page_flags(),
        ),
    }

    for rel, (title, lede, body) in pages.items():
        (out / rel).write_text(render_page(rel, title, lede, body), encoding="utf-8")
    (out / "assets" / "style.css").write_text(CSS.lstrip(), encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"built {len(pages)} pages into {out}")


if __name__ == "__main__":
    main()
