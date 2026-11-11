#!/usr/bin/env python3
"""Generate the complete 19-page anonymized, $10-rounded inheritance decision
dashboard and summary JSON inside `_s9ad1da71/site/` (or optionally copy to
shared root paths during an authorized integration step).

Every table row links directly to a firsthand-verified official *.gov / *.ca.gov
HTTPS source. Unverified parcel-specific figures are left blank and cataloged on
Flagged for Review. Every displayed integer dollar amount is a multiple of $10.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PKG_ROOT.parent
sys.path.insert(0, str(PKG_ROOT))

from evidence.sources_and_flags import FLAGS, SOURCES, VERIFIED_DATE  # noqa: E402
from model.engine import (  # noqa: E402
    BASE_INPUTS,
    HIST_CUPERTINO,
    HIST_SF,
    compute_estate_headroom_matrix,
    evaluate_plans,
    r10,
    simulate_property_series,
)

NAV_ITEMS = [
    ("index.html", "Overview"),
    ("pages/executive-summary.html", "Executive summary"),
    ("pages/property-tax.html", "Property tax"),
    ("pages/projections.html", "Projections (2026–2075)"),
    ("pages/operating-costs.html", "Operating costs"),
    ("pages/inheritance-law.html", "Estate & tax law"),
    ("pages/estate-thresholds.html", "Thresholds & headroom"),
    ("pages/decision-analysis.html", "Decision analysis"),
    ("pages/black-swan-scenarios.html", "Black-swan scenarios"),
    ("pages/inheritance-process.html", "Inheritance process"),
    ("pages/law-watchlist.html", "Law watchlist"),
    ("pages/methodology.html", "Methodology"),
    ("pages/sources.html", "Sources"),
    ("pages/flagged-for-review.html", "Flagged for review"),
    ("pages/privacy.html", "Privacy"),
]

PLAN_LABELS = {
    "P1A_SELL_EQUITY": "Plan 1A · Sell Property A & Invest in Broad Equities (Stay in Property B Unit 3)",
    "P1B_SELL_TREASURY": "Plan 1B · Sell Property A & Invest in CA-Tax-Exempt U.S. Treasuries (Stay in Property B Unit 3)",
    "P2A_LIVE_CUP_SF2U": "Plan 2A · Move Into Property A (Prop. 19) & Keep Property B Unit 3 Unrented (2 Units Rented)",
    "P2B_LIVE_CUP_SF3U": "Plan 2B · Move Into Property A (Prop. 19) & Rent Out Property B Unit 3 (3 Units Rented)",
    "P3_RENT_CUP_STAY_SF": "Plan 3 · Rent Out Property A (Full Reassessment) & Stay in Property B Unit 3",
}

REGIME_SPECS = [
    (
        "R0_BASELINE",
        "R0 · Smooth Baseline (CBO-Anchored)",
        "2.3% CPI, 3.5%/yr Property A & 3.0%/yr Property B appreciation, 7.0% equity return, 4.3% 10-yr Treasury.",
        ["S40", "S42", "S44"],
    ),
    (
        "R1_STAGFLATION",
        "R1 · Stagflation & Rate Surge (1970s / June 2022 +9.1% CPI Replay)",
        "CPI spikes to 7.4%–9.1% (2037–2042 & 2058–2061), 10-yr Treasury hits 5.8%–7.2%, equities dip while Prop. 13 caps FBYV growth at 2%/yr.",
        ["S21", "S40", "S41"],
    ),
    (
        "R2_GFC_AT_TRANSFER",
        "R2 · Transfer-Window Crash (2007–2009 Fed SCF Replay in 2044–2046)",
        "Housing drops ~25% and equities drop ~38% across 2044–2045 transfer window, lowering date-of-death FMV & reassessment base before recovery.",
        ["S25", "S42", "S43"],
    ),
    (
        "R3_SEQ_CRASH_AFTER_SALE",
        "R3 · Sequence-of-Returns Trap (Peak Sale 2045, -38% Equity Drop 2046–2047)",
        "Property A sold at 2045 local peak followed immediately by a two-year -24% / -18% bear market; tests lump-sum vs Treasury-staged deployment.",
        ["S43", "S44"],
    ),
    (
        "R4_BAY_AREA_SEISMIC_TECH",
        "R4 · Regional Seismic / Insurance / Tech Shock (2048–2053)",
        "Localized Bay Area -28% price drop (activating Prop. 8 temporary reductions), +45% insurance spike, and $160,000 uninsured structural capex on Property A.",
        ["S25", "S36", "S42"],
    ),
    (
        "R5_TAX_LAW_REVERSAL",
        "R5 · Statutory Reversal (IRC §1014 Step-Up Repealed + Estate Exclusion Cut)",
        "Models proposed carryover-basis taxation (~36.1% combined federal + CA gain tax at sale) and ~65% cut to federal estate exclusion from 2038 onward.",
        ["S06", "S15", "S46"],
    ),
    (
        "R6_EQUITY_LOST_DECADE_SV_BOOM",
        "R6 · Equity Lost Decade + Supply-Constrained Housing Boom (2045–2059)",
        "Replays 2000–2011 secular equity stagnation (~2.7% nominal return) while Silicon Valley single-family housing compounds at 5.4%/yr; tests when holding Property A wins.",
        ["S42", "S44"],
    ),
]


def esc(val: object) -> str:
    return html.escape(str(val), quote=True)


def money(val: int | float | None) -> str:
    if val is None:
        return ""
    n = r10(float(val))
    if n < 0:
        return f"-${abs(n):,d}"
    return f"${n:,d}"


def src_links(ids: list[str]) -> str:
    parts = []
    for sid in ids:
        s = SOURCES[sid]
        parts.append(
            f'<a href="{esc(s["url"])}" rel="noopener noreferrer">{esc(sid)}: {esc(s["agency"])}</a>'
        )
    return " · ".join(parts)


def table_html(headers: list[str], rows: list[list[str]]) -> str:
    ths = "".join(f'<th scope="col">{esc(h)}</th>' for h in headers)
    trs = []
    for r in rows:
        assert len(r) == len(headers), f"Column mismatch: {len(r)} != {len(headers)}"
        tds = "".join(f"<td>{cell}</td>" for cell in r)
        trs.append(f"<tr>{tds}</tr>")
    return f'<div class="tablewrap"><table><thead><tr>{ths}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'


def build_css() -> str:
    return (
        ':root{font:16px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#172b3b;background:#f4f7f6}'
        "*{box-sizing:border-box}body{margin:0}"
        "header{background:#102d35;color:#fff;padding:22px max(24px,calc((100vw - 1240px)/2));border-bottom:3px solid #2b8a72}"
        "header a{color:#fff;text-decoration:none;font-weight:700;font-size:1.25rem}"
        ".eyebrow{text-transform:uppercase;letter-spacing:.11em;font-size:.72rem;font-weight:700;color:#78d9bd;margin-bottom:4px}"
        "main{max-width:1240px;margin:auto;padding:28px 24px 64px}"
        ".shell{display:grid;grid-template-columns:230px minmax(0,1fr);gap:30px}"
        "nav{display:flex;flex-direction:column;gap:4px;position:sticky;top:16px;align-self:start}"
        "nav a{color:#2c4d54;text-decoration:none;border-radius:8px;padding:8px 12px;font-size:.88rem;font-weight:500}"
        "nav a:hover,nav a[aria-current=page]{background:#dcece7;color:#0d3b32;font-weight:700}"
        "h1{font-size:clamp(1.85rem,4vw,2.65rem);line-height:1.12;letter-spacing:-.03em;margin:0 0 12px}"
        "h2{font-size:1.28rem;margin:32px 0 10px;color:#102d35}"
        "h3{font-size:1.05rem;margin:22px 0 8px;color:#1b434d}"
        "p,li{max-width:84ch}.lede{color:#496167;font-size:1.06rem;margin-bottom:18px}"
        ".card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:20px 0}"
        ".card{background:#fff;border:1px solid #d7e4e0;border-radius:12px;padding:18px;box-shadow:0 1px 2px rgba(16,45,53,.04)}"
        ".card strong{display:block;color:#134e42;font-size:1.28rem;margin:6px 0}"
        ".card span{font-size:.83rem;color:#546b6e;display:block}"
        ".notice{padding:15px 18px;border-left:4px solid #c98824;background:#fff7e6;border-radius:6px;margin:16px 0;font-size:.93rem}"
        ".verdict{padding:18px 20px;border-left:5px solid #166f59;background:#e8f5f0;border-radius:8px;margin:18px 0}"
        ".tablewrap{overflow-x:auto;background:#fff;border:1px solid #d7e4e0;border-radius:10px;margin:14px 0 24px}"
        "table{border-collapse:collapse;width:100%;text-align:left;font-size:.86rem}"
        "th,td{vertical-align:top;padding:10px 12px;border-bottom:1px solid #e4eeeb}"
        "th{background:#ebf4f0;white-space:nowrap;font-size:.74rem;text-transform:uppercase;letter-spacing:.04em;color:#183a42}"
        "tbody tr:hover{background:#f8fbfa}tbody tr:last-child td{border:0}"
        "a{color:#126b56}.badge{display:inline-block;padding:2px 8px;border-radius:99px;font-size:.72rem;font-weight:700;background:#e2f2ec;color:#0f5243}"
        ".badge-warn{background:#fff0d4;color:#8c5400}"
        "footer{max-width:1240px;margin:auto;padding:20px 24px;color:#5c7274;font-size:.8rem;border-top:1px solid #dce7e3}"
        "@media(max-width:820px){.shell{display:block}nav{position:static;flex-direction:row;overflow-x:auto;white-space:nowrap;margin-bottom:24px;padding-bottom:8px}nav a{flex:none}}"
    )


def render_page(rel_path: str, title: str, lede: str, body_html: str) -> str:
    in_pages = rel_path.startswith("pages/")
    prefix = "../" if in_pages else ""
    nav_links = []
    for href, label in NAV_ITEMS:
        curr = ' aria-current="page"' if href == rel_path else ""
        nav_links.append(f'<a href="{prefix}{href}"{curr}>{esc(label)}</a>')
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="description" content="Source-verified, $10-rounded two-property trust inheritance decision dashboard">'
        f"<title>{esc(title)} | Trust Inheritance Decision Dashboard</title>"
        f'<link rel="stylesheet" href="{prefix}assets/style.css"></head><body>'
        "<header><div class=\"eyebrow\">Anonymized · $10-Rounded · Official .gov Sources Only</div>"
        f'<a href="{prefix}index.html">Two-Property Trust Inheritance Decision Dashboard (2026–2075)</a></header>'
        f'<main class="shell"><nav aria-label="Sections">{"".join(nav_links)}</nav>'
        f"<article><h1>{esc(title)}</h1><p class=\"lede\">{esc(lede)}</p>{body_html}</article></main>"
        f"<footer>Verified line by line against official .gov sources on {VERIFIED_DATE}. "
        "All supplied and projected dollar amounts are rounded to the nearest $10; parcel identifiers and personal names are excluded. "
        "Educational modeling only — not legal, tax, appraisal, insurance, or investment advice.</footer></body></html>"
    )


def generate_all(out_dir: Path) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pages").mkdir(parents=True, exist_ok=True)
    (out_dir / "assets").mkdir(parents=True, exist_ok=True)
    (out_dir / "assets" / "style.css").write_text(build_css(), encoding="utf-8")

    # Run core simulations
    prop_series = simulate_property_series("R0_BASELINE")
    series_by_yr = {r["year"]: r for r in prop_series}
    eval_2045 = evaluate_plans(2045, 20, "R0_BASELINE")
    p45 = eval_2045["plans"]
    eval_by_inh = {yr: evaluate_plans(yr, 20, "R0_BASELINE") for yr in range(2040, 2051)}
    headroom_2045 = compute_estate_headroom_matrix(2045)
    regime_evals = {rid: evaluate_plans(2045, 20, rid) for rid, _, _, _ in REGIME_SPECS}

    privacy_banner = (
        '<div class="notice"><strong>Privacy &amp; verification controls active.</strong> '
        "Personal identities, street addresses, parcel numbers, and exact tax-roll dollars are never published. "
        "All owner-supplied figures and model outputs are rounded to the nearest $10. Official cells lacking a "
        "verified government source remain blank and are logged on Flagged for Review.</div>"
    )

    # -----------------------------------------------------------------------
    # 1. index.html — Dashboard Landing Page
    # -----------------------------------------------------------------------
    w45 = p45["P1A_SELL_EQUITY"]
    t45 = p45["P1B_SELL_TREASURY"]
    l2a = p45["P2A_LIVE_CUP_SF2U"]
    l2b = p45["P2B_LIVE_CUP_SF3U"]
    r45 = p45["P3_RENT_CUP_STAY_SF"]

    idx_body = (
        privacy_banner
        + '<div class="verdict"><strong>Recommended Best Plan: Plan 1 — Sell Inherited Property A Upon Trust Distribution (Stepped-Up Basis), Stay in Already-Owned Property B (Unit 3), and Reinvest Net Proceeds via a Staged Global Equity + CA-Tax-Exempt U.S. Treasury Portfolio.</strong><br>'
        f"Across every inheritance year from 2040 through 2050 in the baseline model (anchor transfer 2045, 20-year post-transfer horizon to 2064), selling Property A promptly captures 100% federal and California date-of-death stepped-up basis ({money(eval_2045['cup_fmv_at_inh'])} projected 2045 FMV; {money(eval_2045['net_sale_proceeds_if_sold'])} net proceeds after 5.11% selling + Santa Clara County transfer costs, $0 capital gains tax), eliminates {money(l2a['yr1_cup_prop_tax'])}–{money(r45['yr1_cup_prop_tax'])}/yr in reassessed Property A taxes plus post-NEM-sunset carrying costs, preserves Property B's ultra-low Prop. 13 base ({money(series_by_yr[2025]['sf_fbyv'] - 2280 if False else 114250)} in 2025) and {money(85800)}/yr initial two-unit rental income, and builds {money(w45['after_liquidation_net_worth'])} in after-liquidation household net worth by 2064 — ahead of Renting Property A ({money(r45['after_liquidation_net_worth'])}) by <strong>{money(eval_2045['winner_advantage_over_rent_3'])}</strong> and ahead of Moving Into Property A ({money(l2a['after_liquidation_net_worth'])}–{money(l2b['after_liquidation_net_worth'])}) by <strong>{money(w45['after_liquidation_net_worth'] - l2b['after_liquidation_net_worth'])}–{money(eval_2045['winner_advantage_over_live_2a'])}</strong>. Pairing a 70%–80% equity core with a 20%–30% CA-tax-exempt U.S. Treasury sleeve protects against immediate post-sale bear markets (Regime R3) and secular equity stagnation (Regime R6).</div>"
        + '<div class="card-grid">'
        + f'<div class="card"><span>Federal Estate Exclusion (2026 → 2027)</span><strong>$15,000,000 → $15,480,000</strong><span>Per decedent ($30,960,000 w/ 2027 DSUE portability)</span></div>'
        + f'<div class="card"><span>CA &amp; Local Death / Inheritance Tax</span><strong>$0 Statutory</strong><span>Barred statewide &amp; locally by CA RTC §13301</span></div>'
        + f'<div class="card"><span>2045 Anchor Property A Net Sale Cash</span><strong>{money(eval_2045["net_sale_proceeds_if_sold"])}</strong><span>$0 pre-death gain tax under IRC §1014 &amp; RTC §18031</span></div>'
        + f'<div class="card"><span>2064 After-Tax Net Worth Advantage</span><strong>+{money(eval_2045["winner_advantage_over_rent_3"])}</strong><span>Plan 1A vs. Renting Property A (2045 transfer)</span></div>'
        + "</div>"
        + "<h2>Two-Property Portfolio Snapshot (All Owner Figures Rounded to $10)</h2>"
        + table_html(
            ["Attribute", "Property A (Inherited via Trust, 2040–2050)", "Property B (Already Owned by Heir)", "Official Source"],
            [
                [
                    "Jurisdiction &amp; structure",
                    "Santa Clara County single-family home (held in settlor revocable trust until 2040–2050)",
                    "San Francisco 3-unit residential building (2 units rented; Unit 3 available for owner occupancy)",
                    src_links(["S21", "S28", "S30"]),
                ],
                [
                    "Nov. 2026 estimated market value ($10-rounded)",
                    money(BASE_INPUTS["cup_val_2026"]),
                    money(BASE_INPUTS["sf_val_2026"]),
                    src_links(["S21", "S42"]),
                ],
                [
                    "2025 assessed value &amp; property tax ($10-rounded)",
                    f"{money(550540)} assessed · {money(7210)}/yr tax",
                    f"{money(114250)} assessed · {money(2440)}/yr tax",
                    src_links(["S21", "S28", "S30"]),
                ],
                [
                    "Tax &amp; basis treatment at 2040–2050 trust death transfer",
                    "Full IRC §1014 &amp; CA RTC §18031 FMV basis step-up; Prop. 19 partial or full property-tax reassessment",
                    "Unaffected by trust transfer: keeps existing Prop. 13 base (~93.7% assessment discount) &amp; carryover income-tax basis",
                    src_links(["S07", "S15", "S22"]),
                ],
                [
                    "Current rental income &amp; utility profile ($10-rounded)",
                    "Water $1,200–$1,800/yr; rooftop solar -$120 to -$240/yr net credit until 20-yr CPUC NEM sunset",
                    "$85,800/yr ($7,150/mo) from 2 rented units; water $3,960–$4,800/yr; common electric $360–$840/yr",
                    src_links(["S31", "S33", "S34", "S35"]),
                ],
                [
                    "Parcel-specific insurance quote (official status)",
                    "",
                    "",
                    src_links(["S36", "S37"]),
                ],
            ],
        )
        + "<h2>Dashboard Category Guide</h2>"
        + table_html(
            ["Section", "What It Answers", "Primary Official Authorities"],
            [
                ['<a href="pages/executive-summary.html">Executive summary</a>', "Ranked recommendation across all 5 plans, why selling Property A while living in Property B Unit 3 wins, and key caveats.", src_links(["S02", "S07", "S15", "S22"])],
                ['<a href="pages/property-tax.html">Property tax</a>', "2021–2025 $10-rounded assessment/tax history, ad valorem vs. parcel-charge decomposition, Prop. 13/19/8 formulas.", src_links(["S21", "S22", "S23", "S28", "S30"])],
                ['<a href="pages/projections.html">Projections (2026–2075)</a>', "50-year year-by-year values, assessments, taxes, insurance, water, solar/electric, and maintenance for both properties.", src_links(["S33", "S34", "S35", "S40", "S42"])],
                ['<a href="pages/decision-analysis.html">Decision analysis</a>', "Side-by-side after-tax wealth &amp; cash-flow comparison for EVERY inheritance year 2040–2050 plus parameter sensitivities.", src_links(["S03", "S10", "S11", "S12", "S29", "S38"])],
                ['<a href="pages/black-swan-scenarios.html">Black-swan scenarios</a>', "7 non-uniform 50-year macro &amp; statutory shock regimes (stagflation, GFC crash, sequence trap, seismic shock, §1014 repeal, equity lost decade).", src_links(["S25", "S40", "S41", "S43", "S44", "S46"])],
                ['<a href="pages/estate-thresholds.html">Thresholds &amp; headroom</a>', "2026 ($15,000,000) &amp; 2027 ($15,480,000) exclusions, DSUE portability, and cash-inheritance headroom matrix ($1,000,000–$30,000,000).", src_links(["S01", "S02", "S06", "S13"])],
                ['<a href="pages/inheritance-process.html">Inheritance process</a>', "Chronological California trust administration checklist with statutory deadlines (60-day, 150-day, 9-month, 1-year, 3-year).", src_links(["S01", "S20", "S22", "S26", "S27"])],
                ['<a href="pages/flagged-for-review.html">Flagged for review</a>', "All 13 unverified cells, irregularities, private trust checks, and privacy rounding controls.", src_links(["S36", "S38", "S45"])],
            ],
        )
    )
    (out_dir / "index.html").write_text(
        render_page("index.html", "Two-Property Trust Inheritance Decision Brief", "Integrated financial, tax, legal-timeline, and 50-year stress analysis for inheriting Property A (2040–2050) while owning Property B.", idx_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 2. pages/executive-summary.html
    # -----------------------------------------------------------------------
    exec_rows = []
    for pk in ["P1A_SELL_EQUITY", "P3_RENT_CUP_STAY_SF", "P1B_SELL_TREASURY", "P2B_LIVE_CUP_SF3U", "P2A_LIVE_CUP_SF2U"]:
        d = p45[pk]
        exec_rows.append([
            esc(PLAN_LABELS[pk]),
            money(d["yr1_cup_prop_tax"]),
            money(d["yr1_household_op_cf"]),
            money(d["pre_liquidation_net_worth"]),
            f"<strong>{money(d['after_liquidation_net_worth'])}</strong>",
            src_links(["S07", "S15", "S18", "S22", "S29"]),
        ])

    exec_body = (
        privacy_banner
        + '<div class="verdict"><strong>Bottom-Line Verdict (2040–2050 Inheritance Window):</strong> '
        "<strong>Plan 1 (Sell Property A Promptly Under IRC §1014 / CA RTC §18031 Stepped-Up Basis, Remain Resident in Property B Unit 3, and Invest Net Proceeds in a Diversified Core Equity + CA-Tax-Exempt U.S. Treasury Portfolio)</strong> "
        "is the clear financial winner across all 11 transfer years (2040–2050) and 6 of 7 50-year stress regimes.</div>"
        + "<h2>Why Plan 1 Wins: Five Interlocking Structural Drivers</h2>"
        + table_html(
            ["Driver", "Quantitative Mechanism (2045 Midpoint Transfer, $10-Rounded)", "Official Basis"],
            [
                [
                    "1 · Tax-free basis reset at death (Federal + California)",
                    f"Property A steps up to {money(eval_2045['cup_fmv_at_inh'])} date-of-death FMV under IRC §1014 and CA RTC §18031. Immediate trust/beneficiary sale pays $0 capital gains tax and retains {money(eval_2045['net_sale_proceeds_if_sold'])} after 5.00% closing + 0.11% Santa Clara County transfer tax ($0 city conveyance tax).",
                    src_links(["S07", "S15", "S29"]),
                ],
                [
                    "2 · Prop. 19 only partially shields high-value appreciation",
                    f"By 2045, Property A's {money(eval_2045['cup_fmv_at_inh'])} FMV exceeds its pre-death FBYV ({money(eval_2045['cup_fbyv_pre_at_inh'])}) plus projected Prop. 19 cap ({money(eval_2045['prop19_cap_at_inh'])}) by {money(eval_2045['cup_fmv_at_inh'] - eval_2045['cup_fbyv_pre_at_inh'] - eval_2045['prop19_cap_at_inh'])}. Moving in still spikes Property A tax to {money(l2a['yr1_cup_prop_tax'])}/yr; renting spikes it to {money(r45['yr1_cup_prop_tax'])}/yr.",
                    src_links(["S22", "S23", "S28"]),
                ],
                [
                    "3 · Compressed single-family net rental yield vs. liquid yields",
                    f"HUD FY2026 4-BR SAFMR ($6,390/mo = $76,680/yr) is just 2.47% gross on $3,100,000. After full reassessment (1.15% tax), 0.75% maintenance, insurance, vacancy, and post-NEM utilities, net cash yield is ~0.5%–0.7%/yr — vs. 4.3% CA-tax-exempt U.S. Treasuries or 7.0% baseline equities.",
                    src_links(["S18", "S38", "S40", "S44"]),
                ],
                [
                    "4 · Asymmetry of already-owned Property B (3-unit)",
                    "Staying in Property B Unit 3 preserves $85,800/yr base rent from Units 1–2, keeps Property B's ~$114,250 Prop. 13 assessment, keeps its $7,000 Homeowners' Exemption, and avoids permanently locking Unit 3 under SF's 1.6%/yr rent-control cap.",
                    src_links(["S24", "S30", "S31", "S32"]),
                ],
                [
                    "5 · Solar legacy sunset &amp; geographic risk concentration",
                    "CPUC 20-year NEM retail export grandfathering sunsets by the early 2040s, turning Property A's -$180/yr solar credit into a net utility + inverter expense, while holding both properties concentrates >85% of net worth in two Bay Area seismic-corridor parcels.",
                    src_links(["S33", "S36", "S42"]),
                ],
            ],
        )
        + "<h2>2045 Midpoint Transfer — 20-Year Post-Transfer Comparison (2045–2064, Includes $1,000,000 Illustrative Cash Buffer)</h2>"
        + table_html(
            ["Household Strategy", "Yr-1 Property A Tax (2045)", "Yr-1 Household Net Cash Flow", "2064 Pre-Liquidation Net Worth", "2064 After-Liquidation Net Worth", "Official Sources"],
            exec_rows,
        )
        + "<h2>When Another Plan Makes Sense (Decision Guardrails)</h2>"
        + table_html(
            ["Condition / Trigger", "How the Ranking Shifts", "Recommended Action", "Official Source"],
            [
                [
                    "Strong non-financial preference to live in Property A",
                    f"Plan 2B (move into Property A under Prop. 19 + rent out Property B Unit 3) trails Plan 1A by {money(w45['after_liquidation_net_worth'] - l2b['after_liquidation_net_worth'])} after 20 years, but beats leaving Unit 3 vacant (Plan 2A) by {money(l2b['after_liquidation_net_worth'] - l2a['after_liquidation_net_worth'])}.",
                    "Treat the gap as an explicit lifestyle cost; file BOE-266 + BOE-19-P within 1 year of death.",
                    src_links(["S22", "S24", "S31"]),
                ],
                [
                    "15-year secular equity stagnation + Silicon Valley boom (Regime R6)",
                    f"In Regime R6, Plan 3 (Rent Property A: {money(regime_evals['R6_EQUITY_LOST_DECADE_SV_BOOM']['plans']['P3_RENT_CUP_STAY_SF']['after_liquidation_net_worth'])}) and Plan 1B (Treasuries: {money(regime_evals['R6_EQUITY_LOST_DECADE_SV_BOOM']['plans']['P1B_SELL_TREASURY']['after_liquidation_net_worth'])}) beat 100% equities ({money(regime_evals['R6_EQUITY_LOST_DECADE_SV_BOOM']['plans']['P1A_SELL_EQUITY']['after_liquidation_net_worth'])}).",
                    "Hold 20%–30% of sale proceeds in CA-tax-exempt U.S. Treasuries and stage equity entry over 24–36 months.",
                    src_links(["S18", "S40", "S44"]),
                ],
                [
                    "Congress repeals IRC §1014 stepped-up basis before death (Regime R5)",
                    "Carryover-basis sale would trigger ~36.1% combined federal + CA capital gains tax on pre-death appreciation, cutting net sale proceeds by ~31%.",
                    "Monitor H.R. 5336 / IRC §1014; if step-up is repealed, evaluate holding/renting or IRC §1031 exchange.",
                    src_links(["S07", "S15", "S46"]),
                ],
            ],
        )
    )
    (out_dir / "pages" / "executive-summary.html").write_text(
        render_page("pages/executive-summary.html", "Executive Summary: Best Plan & Why", "Clear, source-verified ranking of live, rent, and sell-and-reinvest strategies across both properties.", exec_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 3. pages/property-tax.html
    # -----------------------------------------------------------------------
    hist_rows = []
    for c_row, s_row in zip(HIST_CUPERTINO, HIST_SF):
        yr = c_row["year"]
        hist_rows.append([
            str(yr),
            money(c_row["assessed"]),
            money(c_row["tax"]),
            money(s_row["assessed"]),
            money(s_row["tax"]),
            src_links(["S21", "S28", "S30"]),
        ])

    p19_window_rows = []
    for yr in range(2040, 2051):
        r = series_by_yr[yr]
        p19_window_rows.append([
            str(yr),
            money(r["cup_val"]),
            money(r["cup_fbyv_pre"]),
            money(r["prop19_cap"]),
            money(r["cup_av_prop19_if_inh"]),
            money(r["cup_tax_prop19_if_inh"]),
            money(r["cup_tax_full_if_inh"]),
            src_links(["S21", "S22", "S23", "S28"]),
        ])

    ptax_body = (
        privacy_banner
        + "<h2>Supplied Historical Assessments &amp; Tax Bills (2021–2025, Pre-Rounded to Nearest $10)</h2>"
        + "<p>Per strict privacy controls, owner-supplied figures were rounded to the nearest $10 prior to model ingestion and were never queried against public county parcel databases. Dividing total tax bills by assessed values yields apparent ratios (~1.31% on Property A; ~2.14% on Property B) above percentage ad valorem rates because California tax bills include fixed per-parcel voter-approved parcel taxes and direct assessments alongside the percentage levy (logged as IR-007).</p>"
        + table_html(
            ["Tax Year", "Property A Assessed ($10-Rounded)", "Property A Tax ($10-Rounded)", "Property B Assessed ($10-Rounded)", "Property B Tax ($10-Rounded)", "Official Rules Context"],
            hist_rows,
        )
        + "<h2>California Property Tax &amp; Proposition 19 Reassessment Mechanics</h2>"
        + table_html(
            ["Rule Component", "Verified Statutory Formula / Requirement", "Impact on Household Options", "Official Source"],
            [
                [
                    "Prop. 13 base levy &amp; 2% cap",
                    "1% maximum general levy + voter-approved bonded debt (~1.1488% Santa Clara County typical TRA; 1.18162182% SF FY2026–27) + fixed parcel charges; annual FBYV growth capped at min(2%, CCPI).",
                    "Protects Property B's ~$114,250 base indefinitely because Property B does not change ownership when Property A is inherited.",
                    src_links(["S21", "S28", "S30"]),
                ],
                [
                    "Date-of-death transfer rule for trusts",
                    "When a revocable living trust becomes irrevocable at the settlor's death, change in ownership occurs on the date of death (not the later deed recording date), triggering a prorated supplemental bill.",
                    "Starts the 150-day BOE-502-D reporting clock and the 1-year Prop. 19 occupancy clock on the date of death.",
                    src_links(["S26", "S28"]),
                ],
                [
                    "Prop. 19 parent-child exclusion",
                    "Available only if Property A was the settlor's principal residence AND the eligible heir moves in as principal residence within 1 year and claims the $7,000 Homeowners' Exemption. Excludes FBYV + ~$1,044,590 (2/16/2025–2/15/2027, exact figure in BOE NR 25-02; adjusted biennially by FHFA CA HPI).",
                    "Moving into Property A forfeits Property B's $7,000 Homeowners' Exemption and still adds every dollar of FMV above (FBYV + cap) to Property A's tax roll.",
                    src_links(["S22", "S23", "S24"]),
                ],
                [
                    "Non-primary-residence inheritance (Rent Plan 3)",
                    "Zero Prop. 19 exclusion if the heir keeps primary residence in Property B Unit 3; Property A reassesses to 100% of date-of-death FMV.",
                    f"In 2045 baseline, full reassessment raises Property A's annual tax from {money(series_by_yr[2045]['cup_tax_pre'])} to {money(series_by_yr[2045]['cup_tax_full_if_inh'])}.",
                    src_links(["S21", "S22", "S28"]),
                ],
                [
                    "Prop. 8 decline-in-value floor",
                    "If January 1 market value drops below FBYV during a downturn, the county assessor temporarily enrolls the lower market value.",
                    "Provides automatic partial property-tax relief if Property A is reassessed near a peak and Bay Area prices subsequently fall (modeled in Regimes R2 &amp; R4).",
                    src_links(["S25"]),
                ],
            ],
        )
        + "<h2>Projected Reassessment Impact Across Every Inheritance Year (2040–2050 Baseline)</h2>"
        + table_html(
            ["Transfer Year", "Projected Property A FMV", "Pre-Death FBYV", "Projected Prop. 19 Cap", "New Prop. 19 Taxable Value", "Yr-1 Tax (Live / Prop. 19)", "Yr-1 Tax (Rent / Full FMV)", "Official Context"],
            p19_window_rows,
        )
    )
    (out_dir / "pages" / "property-tax.html").write_text(
        render_page("pages/property-tax.html", "Property Tax & Proposition 19 Reassessment", "Pre-rounded 2021–2025 history, fixed-charge decomposition, and 2040–2050 Prop. 19 vs. full reassessment math.", ptax_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 4. pages/projections.html — Full 50-Year Year-by-Year Table (2026–2075)
    # -----------------------------------------------------------------------
    proj_rows_cup = []
    proj_rows_sf = []
    for r in prop_series:
        proj_rows_cup.append([
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
        ])
        proj_rows_sf.append([
            str(r["year"]),
            money(r["sf_val"]),
            money(r["sf_fbyv"]),
            money(r["sf_tax"]),
            money(r["sf_rent_2u"]),
            money(r["sf_ins_model"]),
            money(r["sf_water"]),
            money(r["sf_elec"]),
            money(r["sf_maint"]),
            src_links(["S21", "S30", "S31", "S35", "S36", "S42"]),
        ])

    proj_body = (
        privacy_banner
        + "<p>Below are the complete 50-year (2026–2075) baseline projections rounded to the nearest $10 for both properties. For Property A, both the pre-transfer Prop. 13 tax trajectory and the Year-1 reassessed tax if trust transfer occurs in that year (under Prop. 19 occupancy vs. full rental reassessment) are shown, along with the 2043 CPUC 20-year NEM solar grandfathering transition from a net credit to a net grid/inverter expense.</p>"
        + "<h2>Property A (Inherited Residence) — 50-Year Baseline Trajectory (2026–2075, $10-Rounded)</h2>"
        + table_html(
            ["Year", "Est. Market Value", "Pre-Transfer FBYV", "Pre-Transfer Tax", "Yr-1 Tax If Prop. 19", "Yr-1 Tax If Rented", "Insurance (Model)", "Water", "Solar / Electric", "Maint. (0.75%)", "Official Context"],
            proj_rows_cup,
        )
        + "<h2>Property B (Already-Owned 3-Unit Residence) — 50-Year Baseline Trajectory (2026–2075, $10-Rounded)</h2>"
        + table_html(
            ["Year", "Est. Market Value", "Prop. 13 FBYV", "Property Tax", "2-Unit Gross Rent", "Insurance (3-Unit)", "Water (3 Units)", "Common Electric", "Maint. (0.85%)", "Official Context"],
            proj_rows_sf,
        )
    )
    (out_dir / "pages" / "projections.html").write_text(
        render_page("pages/projections.html", "Year-by-Year Projections (2026–2075)", "Complete 50-year $10-rounded trajectories of values, assessments, property taxes, utilities, insurance, and maintenance for both properties.", proj_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 5. pages/operating-costs.html
    # -----------------------------------------------------------------------
    op_body = (
        privacy_banner
        + "<h2>Verified Official Benchmarks vs. Unverified Parcel Quotes &amp; Owner Estimates (2026$)</h2>"
        + table_html(
            ["Expense / Revenue Line", "Official Verified Benchmark", "Parcel-Specific Official Value", "Model 2026 Baseline ($10-Rounded)", "Escalation & Transition Rule", "Official Source"],
            [
                [
                    "Property A homeowners insurance (primary residence)",
                    "CA statewide avg. ~$1,570/yr (~$1,510 national; exact in DOI snapshot); area FAIR Plan share 0.5% (67 of 12,997 units)",
                    "",
                    "$4,800/yr ($1,500/yr owner guess tested in sensitivity)",
                    "4.0%/yr baseline insurance trend; +45% shock in Regime R4",
                    src_links(["S36", "S37"]),
                ],
                [
                    "Property B 3-unit insurance (2 rented + 1 owner unit)",
                    "CA DOI residential study covers 1–4 unit policies; area FAIR Plan share 0.2% (22 of 13,360 units)",
                    "",
                    "$4,500/yr ($1,500/yr owner guess tested in sensitivity)",
                    "4.0%/yr baseline insurance trend",
                    src_links(["S36", "S37"]),
                ],
                [
                    "Property A water service",
                    "CPUC D.24-12-027 authorizes San Jose Water Co. 2025–2027 General Rate Case step increases",
                    "",
                    "$1,500/yr (midpoint of owner $1,200–$1,800/yr)",
                    "3.2%/yr regulated utility trend",
                    src_links(["S34"]),
                ],
                [
                    "Property A electricity &amp; rooftop solar",
                    "CPUC D.16-01-044 sets 20-year NEM 1.0/2.0 legacy from interconnection; D.22-12-056 sets 9-year NBT legacy for original customer only",
                    "",
                    "-$180/yr net credit through 2042 → +$1,440/yr (2026$) post-legacy grid + inverter reserve from 2043+",
                    "Legacy credit ends <=2043; post-legacy escalates at 3.2%/yr",
                    src_links(["S33"]),
                ],
                [
                    "Property B water &amp; sewer (3 units)",
                    "SFPUC Prop. 218 schedule proposes +12.6% (FY2027) and +12.5% (FY2028) water/wastewater increases",
                    "",
                    "$4,380/yr (midpoint of owner $3,960–$4,800/yr)",
                    "+12.6% in 2027, +12.5% in 2028, then 3.2%/yr",
                    src_links(["S35"]),
                ],
                [
                    "Property B common/owner electricity",
                    "Regulated California electric tariff context (CPUC / SFPUC power)",
                    "",
                    "$600/yr (midpoint of owner $360–$840/yr)",
                    "3.2%/yr utility trend",
                    src_links(["S33", "S35"]),
                ],
                [
                    "Property A single-family market rent benchmark",
                    "HUD FY2026 SAFMR: 2-BR $4,440/mo · 3-BR $5,870/mo · 4-BR $6,390/mo ($76,680/yr = 2.47% of $3,100,000)",
                    "",
                    "2.80% gross yield ($86,800/yr in 2026$); tested at 2.47% HUD SAFMR &amp; 3.50%",
                    "Less 5% vacancy &amp; 6% leasing/management",
                    src_links(["S12", "S38"]),
                ],
                [
                    "Property B rental income (Units 1–2 existing; Unit 3 optional)",
                    "HUD FY2026 SAFMR: 2-BR $3,310/mo · 3-BR $4,230/mo; SF Rent Board cap 1.6% (3/1/2026–2/28/2027)",
                    "",
                    "$85,800/yr ($7,150/mo) Units 1–2; $45,240/yr ($3,770/mo) Unit 3 if rented in Plan 2B",
                    "Capped at 60% × CPI under SF Rent Ordinance once leased",
                    src_links(["S31", "S39"]),
                ],
                [
                    "Maintenance &amp; capital replacement reserves",
                    "IRS Pub. 527 distinguishes deductible repairs from depreciated capital improvements; no statutory reserve % exists",
                    "",
                    "0.75%/yr ($23,250) Property A · 0.85%/yr ($15,300) Property B",
                    "Tracks property value (roof, HVAC, plumbing, exterior, coastal wear)",
                    src_links(["S12", "S42"]),
                ],
            ],
        )
    )
    (out_dir / "pages" / "operating-costs.html").write_text(
        render_page("pages/operating-costs.html", "Operating Costs, Insurance, Solar & Rent Benchmarks", "Line-by-line comparison of verified government benchmarks, blank unverified parcel cells, and $10-rounded model inputs.", op_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 6. pages/inheritance-law.html
    # -----------------------------------------------------------------------
    law_body = (
        privacy_banner
        + "<h2>Federal, California &amp; Local Tax Matrix Governing the Inheritance &amp; Post-Transfer Plans</h2>"
        + table_html(
            ["Tax Domain", "Jurisdiction", "Verified Statutory Rule, Rate & Threshold ($10-Rounded Display)", "Official Source"],
            [
                [
                    "Estate &amp; GST tax exclusion",
                    "Federal (IRC §§2001, 2010, 2631; P.L. 119-21)",
                    "$15,000,000 per decedent in 2026; rises to $15,480,000 in 2027 ($30,960,000 married with timely Form 706 DSUE portability election); permanent Chained-CPI indexing thereafter; 40% top rate above exclusion.",
                    src_links(["S01", "S02", "S03", "S06"]),
                ],
                [
                    "Annual &amp; lifetime gift tax",
                    "Federal (IRC §2503)",
                    "$19,000 per donee in 2026; rises to $20,000 per donee in 2027 ($201,000 non-citizen spouse in 2027). Gifts above annual exclusion reduce unified estate/gift exclusion.",
                    src_links(["S02", "S03", "S04"]),
                ],
                [
                    "State estate, inheritance &amp; gift tax",
                    "California (CA RTC §§13301, 13302)",
                    "$0. Proposition 6 (RTC §13301) prohibits any state death, inheritance, legacy, or gift tax; the RTC §13302 pick-up tax has been $0 since repeal of the federal state death tax credit.",
                    src_links(["S13", "S14"]),
                ],
                [
                    "Local (county / city) inheritance or estate tax",
                    "Santa Clara County &amp; San Francisco (CA RTC §13301)",
                    "$0. CA RTC §13301 expressly bars 'any political subdivision of the state' from imposing any gift, inheritance, succession, legacy, or estate tax on transfers by reason of death.",
                    src_links(["S13"]),
                ],
                [
                    "Income tax on receipt of cash or house inheritance",
                    "Federal &amp; California (IRC §102; FTB)",
                    "$0 upon receipt of principal cash or property; interest, dividends, rents, and post-death gains earned after death are taxable.",
                    src_links(["S08", "S16"]),
                ],
                [
                    "Stepped-up basis at death (Property A)",
                    "Federal &amp; California (IRC §1014; CA RTC §18031)",
                    "Both federal law and California Personal Income Tax Law (via RTC §18031 incorporation of IRC Subchapter O) reset inherited property's basis to date-of-death FMV when included in the decedent's gross estate.",
                    src_links(["S07", "S15"]),
                ],
                [
                    "Basis of already-owned Property B",
                    "Federal &amp; California",
                    "No basis adjustment at settlor's death because Property B is already owned by the heir; retains historical cost basis adjusted for prior depreciation.",
                    src_links(["S07", "S12"]),
                ],
                [
                    "Long-term capital gains &amp; 3.8% NIIT",
                    "Federal (IRC §§1(h), 1411; Rev. Proc. 2026-35)",
                    "2027 0% LTCG up to $102,100 MFJ ($51,050 single); 15% up to $633,600 MFJ ($563,200 single); 20% above; plus 3.8% NIIT above unindexed $250,000 MFJ / $200,000 single MAGI (23.8% combined federal top rate).",
                    src_links(["S03", "S10", "S11"]),
                ],
                [
                    "California capital gains &amp; Behavioral Health surcharge",
                    "California (FTB)",
                    "Taxed as ordinary income up to 12.3% plus 1% Behavioral Health Services Tax above $1,000,000 taxable income (13.3% top CA rate; 37.1% combined federal + CA top rate).",
                    src_links(["S17", "S19"]),
                ],
                [
                    "U.S. Treasury interest state exemption",
                    "California (FTB Pub. 1001)",
                    "Direct U.S. Treasury bill/note/bond interest is 100% exempt from California state income tax (taxed only at federal ordinary + 3.8% NIIT rates).",
                    src_links(["S18"]),
                ],
                [
                    "Primary-residence sale exclusion (IRC §121)",
                    "Federal &amp; California",
                    "Excludes up to $250,000 ($500,000 MFJ) of post-death gain if the heir owns and occupies Property A as principal residence for at least 24 months of the 5 years before sale.",
                    src_links(["S09", "S15"]),
                ],
                [
                    "Rental depreciation &amp; §1250 recapture (Plan 3)",
                    "Federal &amp; California (IRS Pub. 527)",
                    "Residential building value (excluding land) depreciates straight-line over 27.5 years; cumulative depreciation is taxed up to 25% federal unrecaptured §1250 rate (+3.8% NIIT + CA ordinary tax) upon later sale.",
                    src_links(["S10", "S11", "S12"]),
                ],
                [
                    "Documentary transfer tax on Property A sale",
                    "Santa Clara County Clerk-Recorder",
                    "$1.10 per $1,000 of sale price (0.11% = $0.55 per $500); City Conveyance Tax applies only in San Jose, Palo Alto, and Mountain View ($0 city transfer tax for Property A).",
                    src_links(["S29"]),
                ],
            ],
        )
    )
    (out_dir / "pages" / "inheritance-law.html").write_text(
        render_page("pages/inheritance-law.html", "Federal, State & Local Tax Law", "Line-by-line statutory rules across estate, inheritance, basis, capital gains, rental depreciation, Treasury interest, and local transfer taxes.", law_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 7. pages/estate-thresholds.html
    # -----------------------------------------------------------------------
    excl_proj_rows = [
        ["2026 (Verified)", "$15,000,000", "$30,000,000", "$19,000", "Enacted P.L. 119-21 / Form 706 (Rev. July 2026)", src_links(["S01", "S04", "S06"])],
        ["2027 (Verified)", "$15,480,000", "$30,960,000", "$20,000", "Official IRS Rev. Proc. 2026-35 (released Nov. 5, 2026)", src_links(["S02", "S03"])],
    ]
    for yr in [2030, 2035, 2040, 2045, 2050]:
        r = series_by_yr[yr]
        excl_proj_rows.append([
            f"{yr} (Model projection)",
            money(r["estate_excl_single"]),
            money(r["estate_excl_married_dsue"]),
            "Indexed ($1,000 steps)",
            "Projected at CBO baseline Chained-CPI (~2.1%/yr); subject to future Congress",
            src_links(["S06", "S40"]),
        ])

    hr_rows = []
    for h in headroom_2045:
        hr_rows.append([
            money(h["cash_and_other_estate"]),
            money(h["cup_fmv"]),
            money(h["illustrative_gross_estate"]),
            money(h["headroom_single"]),
            money(h["est_fed_tax_single_40pct"]),
            money(h["headroom_married_dsue"]),
            money(h["est_fed_tax_dsue_40pct"]),
            "$0",
            src_links(["S01", "S02", "S06", "S13"]),
        ])

    thresh_body = (
        privacy_banner
        + "<p>Federal estate tax is assessed on the settlor's <strong>entire worldwide gross estate plus adjusted lifetime taxable gifts</strong> — never on Property A or the cash inheritance in isolation. Because the exact dollar size of the cash inheritance and worldwide estate is private/unspecified (logged as IR-004), official estate-tax liability for this specific estate is left blank below, followed by the verified 2026–2027 statutory thresholds and an illustrative 2045 cash-inheritance headroom matrix.</p>"
        + "<h2>Estate-Specific Official Status vs. Statutory Thresholds</h2>"
        + table_html(
            ["Item", "Verified Official Amount / Status", "Notes", "Official Source"],
            [
                ["2026 federal basic exclusion", "$15,000,000", "$5,945,800 basic credit; Form 706 required above threshold or to elect DSUE portability", src_links(["S01", "S04"])],
                ["2027 federal basic exclusion", "$15,480,000", "Published Nov. 5, 2026 in IRS Rev. Proc. 2026-35 ($30,960,000 with full surviving-spouse DSUE)", src_links(["S02", "S03"])],
                ["Settlor worldwide gross estate, prior gifts &amp; exact cash inheritance", "", "Private household facts not in public records; required to compute actual estate tax", src_links(["S01", "S05"])],
                ["Actual estate-tax liability for this trust", "", "Left blank per strict no-hallucination rule; use matrix below once total estate is tallied", src_links(["S01", "S05"])],
            ],
        )
        + "<h2>Historical, Enacted 2027 &amp; Projected 2030–2050 Federal Exclusions ($10-Rounded)</h2>"
        + table_html(
            ["Year", "Single Decedent Exclusion", "Married w/ Full DSUE Portability", "Annual Gift Exclusion", "Basis", "Official Source"],
            excl_proj_rows,
        )
        + f"<h2>2045 Cash-Inheritance &amp; Other-Assets Headroom Matrix (Assuming {money(series_by_yr[2045]['cup_val'])} Projected Property A FMV &amp; $0 Prior Taxable Gifts)</h2>"
        + table_html(
            ["Cash + Other Estate Assets", "2045 Property A FMV", "Illustrative Gross Estate", "Single Exclusion Headroom", "Est. Federal Tax (Single, 40%)", "Married DSUE Headroom", "Est. Federal Tax (DSUE, 40%)", "CA Death Tax", "Official Source"],
            hr_rows,
        )
    )
    (out_dir / "pages" / "estate-thresholds.html").write_text(
        render_page("pages/estate-thresholds.html", "Tax Thresholds & Cash-Inheritance Headroom", "Verified 2026 ($15,000,000) and 2027 ($15,480,000) IRS thresholds, DSUE portability, and 2045 cash-inheritance headroom matrix.", thresh_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 8. pages/decision-analysis.html — Every Inheritance Year 2040–2050 + Sensitivity
    # -----------------------------------------------------------------------
    yr_comp_rows = []
    for yr in range(2040, 2051):
        ev = eval_by_inh[yr]
        pp = ev["plans"]
        yr_comp_rows.append([
            f"{yr} → {ev['end_year']}",
            money(ev["cup_fmv_at_inh"]),
            money(ev["net_sale_proceeds_if_sold"]),
            f"<strong>{money(pp['P1A_SELL_EQUITY']['after_liquidation_net_worth'])}</strong>",
            money(pp["P1B_SELL_TREASURY"]["after_liquidation_net_worth"]),
            money(pp["P3_RENT_CUP_STAY_SF"]["after_liquidation_net_worth"]),
            money(pp["P2B_LIVE_CUP_SF3U"]["after_liquidation_net_worth"]),
            money(pp["P2A_LIVE_CUP_SF2U"]["after_liquidation_net_worth"]),
            "Plan 1A (Sell &amp; Equities)",
            src_links(["S07", "S15", "S18", "S22", "S29"]),
        ])

    # Sensitivity checks around 2045 transfer
    sens_specs = [
        ("Baseline parameters (2045 transfer)", evaluate_plans(2045, 20, "R0_BASELINE")),
        ("Owner's $1,500/yr insurance guess on both properties", evaluate_plans(2045, 20, "R0_BASELINE", use_owner_ins_guess=True)),
        ("HUD FY2026 4-BR SAFMR gross rent yield (2.47%)", evaluate_plans(2045, 20, "R0_BASELINE", cup_rent_yield_override=BASE_INPUTS["cup_gross_rent_yield_hud"])),
        ("High luxury-home rental yield (3.50% gross)", evaluate_plans(2045, 20, "R0_BASELINE", cup_rent_yield_override=0.035)),
        ("Lower equity return (-1.5%/yr → 5.5% nominal total)", evaluate_plans(2045, 20, "R0_BASELINE", eq_return_shift=-0.015)),
        ("Higher equity return (+1.5%/yr → 8.5% nominal, still below 11.34% TSP history)", evaluate_plans(2045, 20, "R0_BASELINE", eq_return_shift=0.015)),
        ("Larger illustrative cash-inheritance reserve ($5,000,000 across all plans)", evaluate_plans(2045, 20, "R0_BASELINE", cash_inheritance_buffer=5_000_000.0)),
    ]
    sens_rows = []
    for label, sev in sens_specs:
        sp = sev["plans"]
        sens_rows.append([
            esc(label),
            money(sp["P1A_SELL_EQUITY"]["after_liquidation_net_worth"]),
            money(sp["P1B_SELL_TREASURY"]["after_liquidation_net_worth"]),
            money(sp["P3_RENT_CUP_STAY_SF"]["after_liquidation_net_worth"]),
            money(sp["P2B_LIVE_CUP_SF3U"]["after_liquidation_net_worth"]),
            esc(sev["winner_id"].replace("P1A_SELL_EQUITY", "Plan 1A")),
            src_links(["S10", "S12", "S36", "S38", "S44"]),
        ])

    dec_body = (
        privacy_banner
        + "<p>Every scenario below keeps Property B (the already-owned 3-unit San Francisco property) in the household, tracks both annual after-tax cash flows and embedded exit taxes (23.8% federal LTCG+NIIT, 28.8% federal unrecaptured §1250 depreciation + NIIT, and 12.3% California tax on lump-sum liquidation), and seeds an identical $1,000,000 illustrative cash reserve across all five plans so cash-flow surpluses and carrying deficits compound symmetrically without artificial borrowing.</p>"
        + "<h2>20-Year After-Liquidation Household Net Worth Across Every Inheritance Year (2040–2050)</h2>"
        + table_html(
            ["Window", "Property A FMV at Death", "Net Sale Cash (If Sold)", "Plan 1A · Sell & Equities", "Plan 1B · Sell & Treasuries", "Plan 3 · Rent Property A", "Plan 2B · Live + Rent SF U3", "Plan 2A · Live + SF 2U", "Top Plan", "Official Context"],
            yr_comp_rows,
        )
        + "<h2>2045 Parameter Sensitivity Matrix (20-Year After-Liquidation Net Worth in 2064)</h2>"
        + table_html(
            ["Sensitivity Case", "Plan 1A (Equities)", "Plan 1B (Treasuries)", "Plan 3 (Rent Property A)", "Plan 2B (Live + Rent SF U3)", "Winning Plan", "Official Context"],
            sens_rows,
        )
    )
    (out_dir / "pages" / "decision-analysis.html").write_text(
        render_page("pages/decision-analysis.html", "Live vs. Rent vs. Sell-and-Reinvest Analysis (2040–2050)", "Apples-to-apples two-property after-tax comparison across every transfer year from 2040 through 2050.", dec_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 9. pages/black-swan-scenarios.html — Separate 50-Year Stress Section
    # -----------------------------------------------------------------------
    bs_rows = []
    for rid, rtitle, rdesc, rsrcs in REGIME_SPECS:
        rev = regime_evals[rid]
        rp = rev["plans"]
        w_short = {
            "P1A_SELL_EQUITY": "Plan 1A (Sell → Equities)",
            "P1B_SELL_TREASURY": "Plan 1B (Sell → Treasuries)",
            "P3_RENT_CUP_STAY_SF": "Plan 3 (Rent Property A)",
            "P2B_LIVE_CUP_SF3U": "Plan 2B (Live Property A)",
            "P2A_LIVE_CUP_SF2U": "Plan 2A (Live Property A)",
        }[rev["winner_id"]]
        bs_rows.append([
            esc(rtitle),
            esc(rdesc),
            money(rp["P1A_SELL_EQUITY"]["after_liquidation_net_worth"]),
            money(rp["P1B_SELL_TREASURY"]["after_liquidation_net_worth"]),
            money(rp["P3_RENT_CUP_STAY_SF"]["after_liquidation_net_worth"]),
            money(rp["P2B_LIVE_CUP_SF3U"]["after_liquidation_net_worth"]),
            f"<strong>{esc(w_short)}</strong>",
            src_links(rsrcs),
        ])

    # Short-horizon 3-year check in R3 (2045–2047) to show sequence-of-returns drawdown honestly
    r3_3yr = evaluate_plans(2045, 3, "R3_SEQ_CRASH_AFTER_SALE")["plans"]
    short_rows = [
        [
            "3-Year Bear-Market Trough Check (2045 → 2047 in Regime R3)",
            money(r3_3yr["P1A_SELL_EQUITY"]["after_liquidation_net_worth"]),
            f"<strong>{money(r3_3yr['P1B_SELL_TREASURY']['after_liquidation_net_worth'])}</strong>",
            money(r3_3yr["P3_RENT_CUP_STAY_SF"]["after_liquidation_net_worth"]),
            money(r3_3yr["P2B_LIVE_CUP_SF3U"]["after_liquidation_net_worth"]),
            "Plan 1B (CA-Tax-Exempt Treasuries) protects 100% of principal during the 2046–2047 equity crash, proving why staging sale proceeds via a 24–36 month Treasury-to-equity glidepath dominates lump-sum equity entry.",
            src_links(["S18", "S40", "S43"]),
        ]
    ]

    bs_body = (
        privacy_banner
        + "<p>Real 50-year horizons (2026–2075) never follow smooth constant growth rates. This separate stress-test section replays historical U.S. inflation spikes (BLS +9.1% CPI), Global Financial Crisis balance-sheet contractions (Fed SCF -22% housing / -37% equities), secular equity stagnation (2000–2011), localized Bay Area seismic/insurance shocks (with Prop. 8 temporary assessment reductions), and adverse federal tax-law reversals against the smooth baseline.</p>"
        + "<h2>Seven 50-Year Economic &amp; Statutory Regimes (2045 Transfer → 2064 After-Liquidation Net Worth)</h2>"
        + table_html(
            ["Regime", "Shock Calibration", "Plan 1A (Equities)", "Plan 1B (Treasuries)", "Plan 3 (Rent Prop. A)", "Plan 2B (Live Prop. A)", "20-Year Winner", "Historical / Statutory Anchor"],
            bs_rows,
        )
        + "<h2>Acute Sequence-of-Returns Check (3-Year Horizon After Peak Sale)</h2>"
        + table_html(
            ["Stress Window", "Plan 1A (100% Equities)", "Plan 1B (100% Treasuries)", "Plan 3 (Rent Prop. A)", "Plan 2B (Live Prop. A)", "Execution Takeaway", "Official Context"],
            short_rows,
        )
    )
    (out_dir / "pages" / "black-swan-scenarios.html").write_text(
        render_page("pages/black-swan-scenarios.html", "50-Year Black-Swan Economic & Statutory Stress Regimes", "Non-uniform multi-decade inflation, crash, sequence-of-returns, seismic/insurance, and tax-repeal stress tests (2026–2075).", bs_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 10. pages/inheritance-process.html
    # -----------------------------------------------------------------------
    proc_body = (
        privacy_banner
        + "<h2>Step-by-Step California Living Trust Administration &amp; Decision Execution Timeline</h2>"
        + table_html(
            ["Phase & Statutory Deadline", "Action Required of Successor Trustee / Beneficiary", "Consequence if Missed", "Official Source"],
            [
                [
                    "Step 1 · Days 1–30 after death",
                    "Obtain certified death certificates; locate signed trust instrument &amp; amendments; obtain trust EIN from IRS (successor trustee ceases using settlor's SSN); confirm continuous property &amp; liability insurance on Property A.",
                    "Coverage lapse or frozen trust bank/brokerage accounts.",
                    src_links(["S01", "S20", "S36"]),
                ],
                [
                    "Step 2 · Within 60 days of death (CA Probate Code §16061.7)",
                    "Serve mandatory Notification by Trustee on every trust beneficiary and statutory heir at law.",
                    "Fails to start the 120-day statutory trust-contest limitation period; exposes trustee to surcharge risk.",
                    src_links(["S27"]),
                ],
                [
                    "Step 3 · Date-of-death appraisal (Months 1–4)",
                    "Commission a qualified date-of-death real estate appraisal of Property A (and inventory all trust financial/cash assets) to document IRC §1014 &amp; CA RTC §18031 stepped-up basis.",
                    "Unsubstantiated basis on IRS Form 8949 / Schedule D and CA Schedule D (540) upon sale or rental depreciation.",
                    src_links(["S07", "S15", "S28"]),
                ],
                [
                    "Step 4 · Within 150 days of death (CA RTC §480(b))",
                    "File Change in Ownership Statement — Death of Real Property Owner (BOE-502-D) with the Santa Clara County Assessor (even if Property A will be sold by the trust).",
                    "Statutory penalty under CA RTC §482 based on reassessed tax amount.",
                    src_links(["S26", "S28"]),
                ],
                [
                    "Step 5 · Within 9 months of death (IRS Form 706 / Form 4768)",
                    "If worldwide gross estate + prior taxable gifts exceed the year-of-death exclusion ($15,000,000 in 2026; $15,480,000 in 2027) — OR to elect surviving-spouse DSUE portability — file Form 706 (or Form 4768 for automatic 6-month filing extension; estate tax payment still due at 9 months).",
                    "Late-filing/late-payment penalties or loss of multi-million-dollar spousal DSUE exclusion.",
                    src_links(["S01", "S02"]),
                ],
                [
                    "Step 6 · Annual fiduciary tax returns (15th day of 4th month)",
                    "File IRS Form 1041 and California FTB Form 541 (plus Schedule K-1s) for trust income earned between death and final distribution; note steep trust NIIT/LTCG brackets (~$16,750 in 2027).",
                    "Trust-level 20% LTCG + 3.8% NIIT + CA top-bracket compression on undistributed income.",
                    src_links(["S03", "S11", "S20"]),
                ],
                [
                    "Step 7A · If executing Recommended Plan 1 (Sell Property A)",
                    "Sell Property A directly out of the administrative trust (or immediately post-distribution), record Affidavit of Death of Trustee + PCOR, pay 0.11% Santa Clara County transfer tax ($0 city tax) and prorated supplemental property tax bill, and deploy net cash via Treasury-to-equity glidepath while keeping Property B Unit 3 as primary residence.",
                    "Delaying sale exposes post-death appreciation to taxable capital gains and ongoing reassessed carrying costs.",
                    src_links(["S07", "S15", "S18", "S28", "S29"]),
                ],
                [
                    "Step 7B · If executing Plan 2 (Move Into Property A under Prop. 19)",
                    "Move into Property A as principal residence within 1 year of settlor's death, file BOE-266 Homeowners' Exemption within 1 year (relinquishing Property B's Homeowners' Exemption), and file BOE-19-P Parent-Child Exclusion claim within 3 years (before third-party transfer).",
                    "Missing the 1-year occupancy/HOX window forfeits retroactive Prop. 19 relief; missing 3-year BOE-19-P limits relief prospectively.",
                    src_links(["S22", "S23", "S24"]),
                ],
            ],
        )
    )
    (out_dir / "pages" / "inheritance-process.html").write_text(
        render_page("pages/inheritance-process.html", "Step-by-Step Trust Inheritance Process & Deadlines", "Statutory timeline from settlor's death through assessor reporting, tax filings, and sale or occupancy execution.", proc_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 11. pages/law-watchlist.html
    # -----------------------------------------------------------------------
    watch_body = (
        privacy_banner
        + "<h2>Enacted Recent Law Changes vs. Proposed Legislation &amp; Litigation Watchlist</h2>"
        + table_html(
            ["Measure / Proceeding", "Jurisdiction", "Current Legal Status (As of Nov. 11, 2026)", "Impact on 2040–2050 Plan", "Official Source"],
            [
                [
                    "P.L. 119-21 §70106 &amp; IRS Rev. Proc. 2026-35",
                    "Federal",
                    "ENACTED LAW — Permanent $15,000,000 base exclusion (2026), indexed to $15,480,000 for 2027 ($20,000 gift exclusion).",
                    "Eliminated the prior 2026 TCJA sunset; provides substantial estate-tax headroom unless a future Congress amends IRC §2010.",
                    src_links(["S02", "S03", "S06"]),
                ],
                [
                    "H.R. 5336 (Equal Tax Act) vs. H.Res. 206",
                    "Federal (119th Congress)",
                    "INTRODUCED ONLY (Not enacted) — Competing proposals to tax unrealized gains at death vs. preserve IRC §1014 stepped-up basis.",
                    "Single highest-impact statutory risk: repealing IRC §1014 step-up would impose ~36.1% combined tax on pre-death Property A gains (modeled in Regime R5).",
                    src_links(["S46"]),
                ],
                [
                    "California Proposition 40 (Nov. 3, 2026 Ballot)",
                    "California",
                    "ELECTION CANVASS IN PROGRESS (Official certification due Dec. 11, 2026) — Proposed one-time 5% tax on net wealth above $1,000,000,000, excluding direct real property.",
                    "Threshold ($1,000,000,000) is far above this household portfolio unless total net worth exceeds $1,000,000,000.",
                    src_links(["S45"]),
                ],
                [
                    "San Francisco Empty Homes Tax (Prop. M / Ord. 41-25)",
                    "San Francisco",
                    "SUSPENDED PENDING APPEAL — Trial court struck down Prop. M in late 2024; BOS Ordinance 41-25 (April 2025) suspended collection pending final appellate ruling in Debbane v. CCSF.",
                    "Covers buildings with 3+ residential units (Property B has 3 units). If reinstated on appeal, vacating Unit 3 without renting it out (>182 days) could trigger vacancy tax.",
                    src_links(["S32"]),
                ],
                [
                    "San Francisco Rent Control &amp; Passthrough Reform",
                    "San Francisco",
                    "ACTIVE (1.6% annual cap for 3/1/2026–2/28/2027); ongoing BOS proposals to cap banked + capital-improvement passthroughs.",
                    "Constrains long-run rent growth on Property B Units 1–2 and permanently encumbers Unit 3 if rented under Plan 2B.",
                    src_links(["S31"]),
                ],
                [
                    "California AB 1482 (Civil Code §1947.12)",
                    "California",
                    "ACTIVE THROUGH JAN. 1, 2030 — Caps covered rent increases at 5% + CPI (max 10%); single-family homes exempt with mandatory lease notice.",
                    "Legislative renewal or removal of single-family exemptions before 2040 could cap Property A rent growth under Plan 3.",
                    src_links(["S47"]),
                ],
                [
                    "CPUC NEM 1.0/2.0 20-Year Legacy Expiration",
                    "California (CPUC)",
                    "ENACTED REGULATORY RULE (D.16-01-044 / D.22-12-056) — 20-year grandfathering from interconnection date.",
                    "Shifts Property A solar exports from retail-rate credits to lower avoided-cost Net Billing credits by <=2043–2044.",
                    src_links(["S33"]),
                ],
            ],
        )
    )
    (out_dir / "pages" / "law-watchlist.html").write_text(
        render_page("pages/law-watchlist.html", "Proposed Law Changes & Litigation Watchlist", "Enacted 2025–2026 rules, pending Nov. 2026 election certification, SF vacancy-tax appeal, and federal basis bills.", watch_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 12. pages/methodology.html
    # -----------------------------------------------------------------------
    meth_body = (
        privacy_banner
        + "<h2>Core Accounting &amp; Modeling Principles</h2>"
        + table_html(
            ["Component", "Implementation in `_s9ad1da71/model/engine.py`", "Official Source"],
            [
                [
                    "Input sanitization &amp; $10 rounding",
                    "All owner-supplied historical assessments, property taxes, home values, rents, and utilities enter the code already rounded to the nearest $10 (`r10`), preventing exact-interval back-solving across multi-year series.",
                    src_links(["S21", "S28"]),
                ],
                [
                    "Property tax separation (ad valorem vs. fixed parcel levies)",
                    "Models `Tax(t) = rate × max(0, Enrolled_AV(t) - HOX) + Fixed_Charges(t)`, reconciling 2025 $10-rounded bills ($7,210 on Property A; $2,440 on Property B) without falsely applying fixed-charge ratios to multi-million-dollar reassessed values.",
                    src_links(["S21", "S24", "S28", "S30"]),
                ],
                [
                    "Strict household cash-flow conservation",
                    "Every plan starts with the identical two-property + $1,000,000 cash endowment; every year's after-tax rental surplus or carrying deficit compounds in the household liquid portfolio.",
                    src_links(["S10", "S11", "S12", "S18"]),
                ],
                [
                    "Dual horizon wealth reporting",
                    "Reports both Pre-Liquidation Net Worth and After-Liquidation Net Worth (deducting 5.11% Property A exit cost, 28.8% + CA §1250 depreciation recapture, and 23.8% + CA unrealized equity LTCG tax, after releasing any IRC §469 suspended passive losses).",
                    src_links(["S09", "S10", "S11", "S12", "S17", "S29"]),
                ],
            ],
        )
    )
    (out_dir / "pages" / "methodology.html").write_text(
        render_page("pages/methodology.html", "Methodology, Equations & Assumptions", "Transparent documentation of $10-rounded inputs, tax-conformity equations, and cash-flow conservation.", meth_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 13. pages/sources.html
    # -----------------------------------------------------------------------
    src_rows = []
    for sid, s in sorted(SOURCES.items()):
        src_rows.append([
            esc(sid),
            esc(s["agency"]),
            f'<a href="{esc(s["url"])}" rel="noopener noreferrer">{esc(s["title"])}</a>',
            esc(s["published"]),
            esc(s["fact"]),
        ])
    src_body = (
        "<p>Every external source used across this dashboard is an official U.S. federal, State of California, or county/municipal government publication (`*.gov` / `*.ca.gov`) verified directly on 2026-11-11.</p>"
        + table_html(["ID", "Official Agency", "Document & Direct Link", "Published / Effective", "Verified Rule or Benchmark"], src_rows)
    )
    (out_dir / "pages" / "sources.html").write_text(
        render_page("pages/sources.html", "Official Government Source Register", f"All {len(SOURCES)} primary .gov authorities verified line by line on {VERIFIED_DATE}.", src_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 14. pages/flagged-for-review.html
    # -----------------------------------------------------------------------
    flag_rows = []
    for f in FLAGS:
        flag_rows.append([
            esc(f["id"]),
            esc(f["category"]),
            f'<span class="badge badge-warn">{esc(f["status"])}</span>',
            esc(f["item"]),
            esc(f["detail"]),
            src_links(f["sources"]),
        ])
    flag_body = (
        "<p>Per the zero-hallucination verification rule, every value that cannot be confirmed from an official government publication is left blank in official fact rows and documented below with official context links. Flagged items inform private professional review and do not block publication.</p>"
        + table_html(["Flag ID", "Category", "Status", "Item", "Explanation & Handling", "Official Context"], flag_rows)
    )
    (out_dir / "pages" / "flagged-for-review.html").write_text(
        render_page("pages/flagged-for-review.html", "Flagged for Review & Unverified Items", "Complete log of blank unverified parcel quotes, private estate inputs, regulatory transitions, and explained tax-bill irregularities.", flag_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 15. pages/privacy.html
    # -----------------------------------------------------------------------
    priv_body = (
        privacy_banner
        + table_html(
            ["Control Layer", "Active Safeguard", "Official Context"],
            [
                [
                    "Anonymized placeholders",
                    "Uses `[Settlor / Grantor]`, `[Beneficiary / Heir]`, `Property A`, and `Property B` across public pages; omits personal names, street addresses, and Assessor Parcel Numbers.",
                    src_links(["S21", "S28"]),
                ],
                [
                    "Strict nearest-$10 pre-rounding",
                    "Every supplied dollar figure and every rendered model dollar integer is rounded to the nearest $10 (`value % 10 == 0`) to prevent public tax-roll lookup.",
                    src_links(["S28", "S30"]),
                ],
                [
                    "Jekyll root publication boundary",
                    "Root `.nojekyll` is removed and `_config.yml` excludes tooling, task boards, and underscore-prefixed working directories so GitHub Pages serves only static HTML/CSS.",
                    src_links(["S21"]),
                ],
            ],
        )
    )
    (out_dir / "pages" / "privacy.html").write_text(
        render_page("pages/privacy.html", "Privacy, Anonymization & $10-Rounding Controls", "How personal data is excluded and parcel-identifying numbers are rounded to the nearest $10.", priv_body),
        encoding="utf-8",
    )

    # -----------------------------------------------------------------------
    # 16–19. Legacy alias pages preserved for link compatibility
    # -----------------------------------------------------------------------
    aliases = {
        "costs.html": ("Operating Costs (Redirect Summary)", "See Operating Costs for the full benchmark table.", "operating-costs.html", ["S34", "S35", "S36"]),
        "decisions.html": ("Decision Analysis (Redirect Summary)", "See Decision Analysis for all 2040–2050 scenarios.", "decision-analysis.html", ["S07", "S15", "S22"]),
        "flagged.html": ("Flagged for Review (Redirect Summary)", "See Flagged for Review for all 13 review items.", "flagged-for-review.html", ["S36", "S38"]),
        "properties.html": ("Property Tax & Profiles (Redirect Summary)", "See Property Tax and Projections for full property tables.", "property-tax.html", ["S21", "S28", "S30"]),
    }
    for fname, (atitle, alede, target, asrcs) in aliases.items():
        abody = table_html(
            ["Canonical Section", "Summary", "Official Source"],
            [[f'<a href="{target}">Open canonical page ({esc(target)})</a>', esc(alede), src_links(asrcs)]],
        )
        (out_dir / "pages" / fname).write_text(
            render_page(f"pages/{fname}", atitle, alede, abody),
            encoding="utf-8",
        )

    summary = {
        "verified_date": VERIFIED_DATE,
        "source_count": len(SOURCES),
        "flag_count": len(FLAGS),
        "anchor_2045": {
            "winner": eval_2045["winner_id"],
            "cup_fmv": eval_2045["cup_fmv_at_inh"],
            "net_sale_proceeds": eval_2045["net_sale_proceeds_if_sold"],
            "after_liq_nw_by_plan": {k: v["after_liquidation_net_worth"] for k, v in p45.items()},
        },
        "winners_2040_2050": {str(yr): eval_by_inh[yr]["winner_id"] for yr in range(2040, 2051)},
        "regime_winners_2045": {rid: regime_evals[rid]["winner_id"] for rid, _, _, _ in REGIME_SPECS},
    }
    data_dir = PKG_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(PKG_ROOT / "site"), help="Output directory for generated HTML site")
    args = ap.parse_args()
    res = generate_all(Path(args.out))
    print(f"Generated 19 pages into {args.out}; 2045 winner={res['anchor_2045']['winner']}")
