#!/usr/bin/env python3
"""Generators for pages 1-8 of the 15-page candidate dashboard."""
from __future__ import annotations

import html
from typing import Dict

from style_and_layout import (
    fmt_usd,
    render_page,
    svg_50yr_projection_lines,
    svg_strategy_bars,
    td,
    tr_row,
)

PLAN_META = [
    ("sell_stocks", "Plan S1 — Sell [Property A] at Inheritance → 100% Broad Equity Index (Live in [Property B] Unit 3)"),
    ("sell_60_40", "Plan S2 — Sell [Property A] at Inheritance → 60/40 Stocks + Direct U.S. Treasuries (Live in [Property B] Unit 3)"),
    ("rent_a", "Plan R — Keep & Rent Out [Property A] (Full Prop. 19 Reassessment; Live in [Property B] Unit 3)"),
    ("sell_treasuries", "Plan S3 — Sell [Property A] at Inheritance → 100% CA-Tax-Exempt U.S. Treasuries (Live in [Property B] Unit 3)"),
    ("live_a_rent_u3", "Plan L2 — Move Into [Property A] (Prop. 19 Cap) + Lease Out [Property B] Unit 3 at Market Rent"),
    ("live_a_keep_u3", "Plan L1 — Move Into [Property A] (Prop. 19 Cap; Keep [Property B] Unit 3 Unrented)"),
]


def build_index(inputs: dict, results: dict, ledger: Dict[str, dict]) -> str:
    h20 = results["horizons_2045"]["20yr"]
    p = h20["plans"]
    be = results["breakevens"]
    mc = results["black_swan_statistical"]["block_bootstrap_500_paths"]
    hist50 = results["black_swan_statistical"]["historical_50_cohorts"]
    est45 = [r for r in results["estate_headroom"]["by_year"] if r["year"] == 2045][0]

    s1_exb = p["sell_stocks"]["terminal_wealth_ex_b_real_2026_r10"]
    s1_inc = p["sell_stocks"]["terminal_wealth_incl_b_real_2026_r10"]
    r_exb = p["rent_a"]["terminal_wealth_ex_b_real_2026_r10"]
    l1_exb = p["live_a_keep_u3"]["terminal_wealth_ex_b_real_2026_r10"]

    rows = []
    for pkey, label in PLAN_META:
        pv = p[pkey]
        adv_vs_l1 = pv["terminal_wealth_ex_b_real_2026_r10"] - l1_exb
        win_mc = mc[pkey]["win_share_pct"]
        win_txt = f"{win_mc:.1f}%" if win_mc is not None else "Variant"
        rcls = "highlight-row" if pkey == "sell_stocks" else ""
        srcs = ["IRS-INHERIT-FAQ", "CA-RTC-18031", "BOE-PROP19", "TSP-RETURNS"]
        if "treasuries" in pkey or "60_40" in pkey:
            srcs = ["IRS-INHERIT-FAQ", "TD-TAX-EXEMPT", "FTB-PUB-1001", "CBO-OUTLOOK-2026"]
        elif pkey == "rent_a":
            srcs = ["BOE-PROP19", "IRS-P527", "HUD-SAFMR-2027", "IRS-TC409"]
        elif "live_a" in pkey:
            srcs = ["CA-RTC-63-2", "BOE-NR-25-02", "SF-EHT", "BOE-HOX"]
        rows.append(tr_row([
            td(html.escape(label), bold=(pkey == "sell_stocks")),
            td(fmt_usd(pv["terminal_wealth_ex_b_real_2026_r10"]), num=True, bold=True),
            td(fmt_usd(pv["terminal_wealth_incl_b_real_2026_r10"]), num=True),
            td(fmt_usd(pv["cum_annual_after_tax_cf_real_2026_r10"], signed=True), num=True),
            td(fmt_usd(adv_vs_l1, signed=True), num=True),
            td(win_txt, num=True),
        ], srcs, "proj", ledger, row_cls=rcls))

    body = f"""
<div class="callout rec">
  <strong>Recommended Strategy (Maximizing After-Tax Profit &amp; Lowering Carrying Costs):</strong>
  Upon inheriting <strong>[Property A]</strong> through the family trust (<code>2040–2050</code> window), <strong>sell [Property A]</strong> to capture the <code>0%</code> federal and California capital-gains basis step-up at death (<code>IRC §1014</code> / <code>CA RTC §18031</code>), <strong>continue living in Unit 3 of already-owned [Property B]</strong> while keeping Units 1–2 rented (preserving <code>[Property B]</code>'s ultra-low Proposition 13 assessed base of <code>$114,250</code> in 2025), and deploy the <code>{fmt_usd(h20["net_sale_proceeds_t0_real_2026_r10"])}</code> (constant 2026$) net proceeds via an 18–36 month U.S. Treasury-to-Broad-Equity index glidepath. Over a 20-year post-inheritance horizon, <strong>Plan S1 (Sell → Broad Stocks)</strong> reaches <strong>{fmt_usd(s1_exb)}</strong> real 2026$ (<strong>{fmt_usd(s1_inc)}</strong> total household real net worth including <code>[Property B]</code>) — outperforming <strong>Renting [Property A]</strong> by <strong>{fmt_usd(s1_exb - r_exb, signed=True)}</strong> and outperforming <strong>Living in [Property A]</strong> by <strong>{fmt_usd(s1_exb - l1_exb, signed=True)}</strong> in constant 2026 purchasing power.
</div>

<div class="kpi-grid">
  <div class="kpi-card winner">
    <div class="kpi-label">Best 20-Yr Real Net Worth (Ex-B / Incl-B)</div>
    <div class="kpi-value">{fmt_usd(s1_exb)} / {fmt_usd(s1_inc)}</div>
    <div class="kpi-sub">Sell [Property A] at 2045 transfer → Broad Equity Index (constant 2026$)</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Historical &amp; Bootstrap Win Rate</div>
    <div class="kpi-value">{hist50["sell_stocks_win_pct"]:.1f}% / {mc["sell_stocks"]["win_share_pct"]:.1f}%</div>
    <div class="kpi-sub">49 of 50 actual 1976–2025 cohorts · 81.6% of 500 de-meaned stress paths</div>
  </div>
  <div class="kpi-card warn">
    <div class="kpi-label">2045 Prop. 19 Year-1 Tax Shock</div>
    <div class="kpi-value">{fmt_usd(h20["prop19_year1_tax_live_nominal_r10"])} / {fmt_usd(h20["prop19_year1_tax_rent_nominal_r10"])}</div>
    <div class="kpi-sub">Nominal Yr-1 tax if Occupied vs. Rented (up from {fmt_usd(h20["prop19_year1_tax_trust_prior_nominal_r10"])} prior trust roll)</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">2045 Federal Estate Cash Headroom</div>
    <div class="kpi-value">{fmt_usd(est45["cash_headroom_single_real_2026_r10"])}</div>
    <div class="kpi-sub">Extra cash (2026$) above [Property A] before 40% estate tax ($0 CA/local tax)</div>
  </div>
</div>

{svg_strategy_bars(p)}

<h2>All Six Household Strategies at a Glance (2045 Inheritance → 2065, Constant 2026$)</h2>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Strategy (All Plans Retain [Property B] &amp; Its 2 Rented Units)</th>
        <th class="num">2065 Wealth Ex-[Property B] (2026$)</th>
        <th class="num">2065 Total Wealth Incl. [Property B] (2026$)</th>
        <th class="num">20-Yr Cum. Net Cash Flow (2026$)</th>
        <th class="num">Gain vs. Live in [Property A] (2026$)</th>
        <th class="num">Bootstrap Win %</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows)}
    </tbody>
  </table>
</div>

<h2>Dashboard Directory</h2>
<div class="card-grid">
  <div class="nav-card">
    <h3><a href="pages/executive-summary.html">1. Executive Summary &amp; Action Plan</a></h3>
    <p>Why selling [Property A] wins, why keeping [Property B] works, break-even equity return ({be["breakeven_equity_nominal_return_pct_vs_rent_a"]:.2f}% nominal) &amp; break-even rent ({fmt_usd(be["breakeven_prop_a_monthly_rent_2026_r10_vs_stocks"])}/mo), and tactical risk controls.</p>
  </div>
  <div class="nav-card">
    <h3><a href="pages/decision-analysis.html">2. Live vs. Rent vs. Sell Matrix</a></h3>
    <p>Complete comparisons across 10-yr, 20-yr, and 31-yr horizons, all 11 transfer years (2040–2050), MFJ vs. Single, IRC §280A 2/3 expense allocation, and insurance/rent sensitivities.</p>
  </div>
  <div class="nav-card">
    <h3><a href="pages/properties.html">3. Properties &amp; Forensic Roll Audit</a></h3>
    <p>$10-rounded baseline profiles for [Property A] ($3,100,000) and [Property B] ($1,800,000), plus 2014–2026 line-by-line BOE Prop. 13 factor verification and $7,000 HOX proof.</p>
  </div>
  <div class="nav-card">
    <h3><a href="pages/operating-costs.html">4. Operating Costs, Solar NEM &amp; Insurance</a></h3>
    <p>Decomposed ad valorem + parcel taxes, CDI insurance study vs. blank parcel quotes, CPUC 20-yr solar NEM sunset (&le;2046) to Net Billing Tariff, and water/sewer rate orders.</p>
  </div>
  <div class="nav-card">
    <h3><a href="pages/projections.html">5. 50-Year Projections (2026–2076)</a></h3>
    <p>Every single year from 2026 through 2076 for both properties: market value, Prop. 13/19 assessed value, property tax, insurance, water, solar/electricity, and upkeep.</p>
  </div>
  <div class="nav-card">
    <h3><a href="pages/black-swan-scenarios.html">6. 50-Year Black-Swan Stress Suite</a></h3>
    <p>Six named non-uniform multi-decade shocks (stagflation, -42% post-sale crash, -32% housing bust, insurance/drought crisis, §1014 repeal, housing boom) + 50 historical cohorts.</p>
  </div>
  <div class="nav-card">
    <h3><a href="pages/estate-thresholds.html">7. Cash Inheritance &amp; Estate Thresholds</a></h3>
    <p>2026 ($15,000,000) &amp; 2027 ($15,480,000) federal exclusions, $0 CA/local death tax (RTC §13301), married DSUE portability, and cash headroom matrix ($0–$25,000,000).</p>
  </div>
  <div class="nav-card">
    <h3><a href="pages/flagged-for-review.html">8. Flagged for Review &amp; Official Sources</a></h3>
    <p>Every unverified blank cell, owner estimate, forensic roll anomaly, and modeling assumption — plus <a href="pages/inheritance-process.html">Step-by-Step Trust Process</a> and <a href="pages/sources.html">44 Official .gov Sources</a>.</p>
  </div>
</div>
"""
    return render_page(
        "index.html",
        "Inheritance & Two-Property Financial Decision Dashboard",
        "Line-by-line official-source analysis comparing living in, renting out, or selling an inherited single-family trust property ([Property A]) alongside an already-owned 3-unit residential building ([Property B]) from 2026 through 2076.",
        body,
    )


def build_executive_summary(inputs: dict, results: dict, ledger: Dict[str, dict]) -> str:
    h10 = results["horizons_2045"]["10yr"]["plans"]
    h20 = results["horizons_2045"]["20yr"]
    p20 = h20["plans"]
    h31 = results["horizons_2045"]["31yr_to_2076"]["plans"]
    be = results["breakevens"]
    est45 = [r for r in results["estate_headroom"]["by_year"] if r["year"] == 2045][0]

    rows = [
        tr_row([
            td("1. Primary Recommendation", bold=True),
            td("Sell [Property A] promptly after trust inheritance; keep [Property B] (reside in Unit 3, keep 2 units rented); deploy net proceeds via an 18–36 month Treasury-to-Broad-Equity index glidepath."),
            td(fmt_usd(p20["sell_stocks"]["terminal_wealth_ex_b_real_2026_r10"]), num=True, bold=True),
        ], ["IRS-INHERIT-FAQ", "CA-RTC-18031", "TSP-RETURNS"], "proj", ledger, "highlight-row"),
        tr_row([
            td("2. Balanced Lower-Volatility Alternative", bold=True),
            td("Sell [Property A] → hold 60% Broad Equity Index + 40% Direct U.S. Treasury Ladder (0% CA income tax under 31 U.S.C. §3124 & FTB Pub. 1001). Protects against immediate post-sale bear markets (BS-2)."),
            td(fmt_usd(p20["sell_60_40"]["terminal_wealth_ex_b_real_2026_r10"]), num=True, bold=True),
        ], ["TD-TAX-EXEMPT", "FTB-PUB-1001", "CBO-OUTLOOK-2026"], "proj", ledger),
        tr_row([
            td("3. Why Renting Out [Property A] Trails Selling", bold=True),
            td("Non-principal-residence transfers get $0 Prop. 19 exclusion: Yr-1 tax jumps to $75,370 nominal ($48,030 real 2026$), solar NEM 20-yr retail credits expire <=2046, and net pre-tax cap rate compresses near ~1.2%/yr."),
            td(fmt_usd(p20["rent_a"]["terminal_wealth_ex_b_real_2026_r10"]), num=True),
        ], ["BOE-PROP19", "CPUC-NEM", "HUD-SAFMR-2027"], "proj", ledger),
        tr_row([
            td("4. Why Living in [Property A] Is Costliest", bold=True),
            td("Even with Prop. 19's indexed principal-residence cap ($1,044,590 [$10-rounded] in 2025–2027), excess FMV drives Yr-1 property tax to $51,150 nominal while locking up $3,807,440 (real 2026$) of investable sale equity."),
            td(fmt_usd(p20["live_a_keep_u3"]["terminal_wealth_ex_b_real_2026_r10"]), num=True),
        ], ["CA-RTC-63-2", "BOE-NR-25-02", "BOE-LTA-2026-026"], "proj", ledger, "warn-row"),
        tr_row([
            td("5. Mandatory Mitigation If Living in [Property A]", bold=True),
            td("If lifestyle preference overrides financial optimization and you move into [Property A], lease out Unit 3 of [Property B] at market rent ($3,410/mo 2026$ HUD 2-BR SAFMR) rather than leaving it empty."),
            td(fmt_usd(p20["live_a_rent_u3"]["terminal_wealth_ex_b_real_2026_r10"]), num=True),
        ], ["HUD-SAFMR-2027", "SF-RENT-LEARN", "SF-EHT"], "proj", ledger),
        tr_row([
            td("6. Break-Even Thresholds (2045 Anchor, 20-Yr)", bold=True),
            td(f"Broad equities only need {be['breakeven_equity_nominal_return_pct_vs_rent_a']:.2f}%/yr nominal ({be['breakeven_equity_real_return_pct_vs_rent_a']:.2f}%/yr real) to beat renting [Property A]; [Property A] would require {fmt_usd(be['breakeven_prop_a_monthly_rent_2026_r10_vs_stocks'])}/mo (2026$) gross rent to tie 7.0% equities."),
            td(fmt_usd(be["breakeven_prop_a_monthly_rent_2026_r10_vs_stocks"]), num=True),
        ], ["HUD-SAFMR-2027", "CBO-OUTLOOK-2026", "TSP-RETURNS"], "proj", ledger),
        tr_row([
            td("7. Cash Inheritance Tax-Free Headroom", bold=True),
            td("California and local death/inheritance taxes are $0 (CA RTC §13301). Under P.L. 119-21 ($15,480,000 in 2027, CPI-indexed), a single trustor in 2045 has $11,104,710 (real 2026$) of additional tax-free cash headroom above [Property A]."),
            td(fmt_usd(est45["cash_headroom_single_real_2026_r10"]), num=True),
        ], ["IRS-RP-2026-35", "CA-RTC-13301", "CA-SCO-ESTATE"], "verified", ledger),
    ]

    h_rows = []
    for pkey, label in PLAN_META:
        h_rows.append(tr_row([
            td(html.escape(label), bold=(pkey == "sell_stocks")),
            td(fmt_usd(h10[pkey]["terminal_wealth_ex_b_real_2026_r10"]), num=True),
            td(fmt_usd(p20[pkey]["terminal_wealth_ex_b_real_2026_r10"]), num=True, bold=True),
            td(fmt_usd(h31[pkey]["terminal_wealth_ex_b_real_2026_r10"]), num=True),
        ], ["IRS-INHERIT-FAQ", "BOE-PROP19", "TSP-RETURNS"], "proj", ledger, "highlight-row" if pkey == "sell_stocks" else ""))

    body = f"""
<h2>Core Analytical Findings &amp; Structural Asymmetry</h2>
<p>Three California and federal statutory rules interact at the moment of inheritance to create a decisive financial asymmetry between <strong>[Property A]</strong> and <strong>[Property B]</strong>:</p>
<ul>
  <li><strong>Tax-Free Exit Window at Death (IRC §1014 &amp; CA RTC §18031):</strong> Assuming [Property A] is held in a standard revocable living trust included in the settlor's gross estate (<code>Rev. Rul. 2023-2</code>), its income-tax basis resets to 100% of date-of-death fair market value (projected <code>{fmt_usd(h20["fmv_a_at_transfer_nominal_r10"])}</code> nominal / <code>{fmt_usd(h20["fmv_a_at_transfer_real_2026_r10"])}</code> real 2026$ in 2045). Selling shortly after death incurs <strong>$0 federal LTCG, $0 3.8% NIIT, and $0 California 13.3% income tax</strong> on decades of prior appreciation — only brokerage/closing friction (~5.0%) plus the verified <code>0.11%</code> county documentary transfer tax.</li>
  <li><strong>Proposition 19 Reassessment Penalty on Holding [Property A] (CA RTC §63.2):</strong> Unlike income-tax basis, California's Proposition 13 property-tax base does <em>not</em> carry over intact. Renting [Property A] triggers 100% reassessment to market value (<code>{fmt_usd(h20["prop19_year1_tax_rent_nominal_r10"])}/yr</code> nominal Year-1 property tax vs. <code>{fmt_usd(h20["prop19_year1_tax_trust_prior_nominal_r10"])}/yr</code> before death). Even moving into [Property A] within 1 year only shields <code>FBYV + indexed $1,044,590 [$10-rounded] cap</code>, leaving a <code>{fmt_usd(h20["prop19_year1_tax_live_nominal_r10"])}/yr</code> nominal Year-1 tax bill.</li>
  <li><strong>Locked-In Proposition 13 Advantage on Already-Owned [Property B]:</strong> Because [Property B] is already owned by the inheritor, no change in ownership occurs. Its 2025 net assessed value is just <code>$114,250</code> (<code>$2,440/yr</code> tax on a <code>$1,800,000</code> building), while two rented units already produce <code>$7,150/mo</code> (<code>$85,800/yr</code>) and Unit 3 provides primary housing at zero incremental housing outlay.</li>
</ul>

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Strategic Pillar</th>
        <th>Verified Mechanism &amp; Reasoning</th>
        <th class="num">Key Benchmark (2026$)</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows)}
    </tbody>
  </table>
</div>

<h2>Post-Inheritance Horizon Comparison (2045 Transfer: 10-Yr, 20-Yr &amp; 31-Yr to 2076, Constant 2026$ Ex-[Property B])</h2>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Strategy</th>
        <th class="num">10-Yr Horizon (2055, 2026$)</th>
        <th class="num">20-Yr Horizon (2065, 2026$)</th>
        <th class="num">31-Yr Horizon (2076, 2026$)</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(h_rows)}
    </tbody>
  </table>
</div>
"""
    return render_page(
        "pages/executive-summary.html",
        "Executive Summary & Recommended Plan",
        "Complete synthesis of tax, property, operating-cost, and investment tradeoffs — and why liquidating [Property A] under IRC §1014 while retaining [Property B] dominates across every horizon.",
        body,
    )


def build_decision_analysis(inputs: dict, results: dict, ledger: Dict[str, dict]) -> str:
    sweep = results["transfer_year_sweep_2040_2050"]
    sens = results["sensitivities_2045_20yr"]
    base20 = results["horizons_2045"]["20yr"]["plans"]

    sweep_rows = []
    for item in sweep:
        ty = item["transfer_year"]
        pl = item["plans"]
        rcls = "highlight-row" if ty == 2045 else ""
        sweep_rows.append(tr_row([
            td(f"{ty} → {item['end_year']}", bold=(ty == 2045)),
            td(fmt_usd(item["fmv_a_at_transfer_real_2026_r10"]), num=True),
            td(fmt_usd(pl["sell_stocks"]["terminal_wealth_ex_b_real_2026_r10"]), num=True, bold=True),
            td(fmt_usd(pl["sell_60_40"]["terminal_wealth_ex_b_real_2026_r10"]), num=True),
            td(fmt_usd(pl["rent_a"]["terminal_wealth_ex_b_real_2026_r10"]), num=True),
            td(fmt_usd(pl["sell_treasuries"]["terminal_wealth_ex_b_real_2026_r10"]), num=True),
            td(fmt_usd(pl["live_a_rent_u3"]["terminal_wealth_ex_b_real_2026_r10"]), num=True),
            td(fmt_usd(pl["live_a_keep_u3"]["terminal_wealth_ex_b_real_2026_r10"]), num=True),
        ], ["IRS-INHERIT-FAQ", "BOE-PROP19", "TD-TAX-EXEMPT"], "proj", ledger, rcls))

    sens_rows = []
    sens_cases = [
        ("Baseline (Single, $150,000 Wage, IRC §280A 2/3 Alloc., $1,500 Ins., $5,800/mo Rent A)", {k: v["terminal_wealth_ex_b_real_2026_r10"] for k, v in base20.items()}, ["IRS-P527", "HUD-SAFMR-2027", "BOE-PROP19"]),
        ("Married Filing Jointly ($250,000 Joint Wage, Wider Brackets & $500,000 §121)", sens["married_filing_jointly"], ["IRS-RP-2026-35", "IRS-TC701", "FTB-RATES-2025"]),
        ("Realistic High-Value / 3-Unit Landlord Insurance ($4,200 Prop. A / $6,500 Prop. B)", sens["realistic_replacement_insurance_4200_6500"], ["CDI-SNAPSHOT-2026", "CDI-STUDY"]),
        ("Executive Single-Family Rent on [Property A] ($7,200/mo in 2026$)", sens["executive_sfr_rent_7200_mo"], ["HUD-SAFMR-2027", "CA-AG-RENTCAPS"]),
        ("Naive 3/3 Property B Schedule E Deduction (Ignoring IRC §280A 1/3 Personal Use)", sens["naive_3_of_3_prop_b_deduction"], ["IRS-P527"]),
    ]
    for label, vals, sids in sens_cases:
        sens_rows.append(tr_row([
            td(html.escape(label), bold=label.startswith("Baseline")),
            td(fmt_usd(vals["sell_stocks"]), num=True, bold=True),
            td(fmt_usd(vals["sell_60_40"]), num=True),
            td(fmt_usd(vals["rent_a"]), num=True),
            td(fmt_usd(vals["sell_treasuries"]), num=True),
            td(fmt_usd(vals["live_a_rent_u3"]), num=True),
            td(fmt_usd(vals["live_a_keep_u3"]), num=True),
        ], sids, "proj", ledger, "highlight-row" if label.startswith("Baseline") else ""))

    body = f"""
<h2>1. Full Transfer-Year Sweep Across 2040–2050 (20-Year Post-Inheritance Horizon, Constant 2026$ Ex-[Property B])</h2>
<p>Because the exact date of trust succession between <code>2040</code> and <code>2050</code> is unknown, every strategy is evaluated across all 11 possible transfer years. <strong>Plan S1 (Sell → Broad Stocks)</strong> and <strong>Plan S2 (Sell → 60/40)</strong> rank #1 and #2 in every single transfer year from 2040 through 2050.</p>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Transfer → Horizon</th>
        <th class="num">[Property A] FMV at Death (2026$)</th>
        <th class="num">S1: Sell → Stocks</th>
        <th class="num">S2: Sell → 60/40</th>
        <th class="num">R: Rent [Property A]</th>
        <th class="num">S3: Sell → Treasuries</th>
        <th class="num">L2: Live + Rent U3</th>
        <th class="num">L1: Live (U3 Empty)</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(sweep_rows)}
    </tbody>
  </table>
</div>

<h2>2. Tax, Insurance &amp; Rental Sensitivity Matrix (2045 Transfer → 2065, Constant 2026$ Ex-[Property B])</h2>
<p>Testing Married Filing Jointly brackets, realistic high-value/habitational insurance quotes (<code>$4,200/yr</code> [Property A] and <code>$6,500/yr</code> [Property B]), executive single-family rent (<code>$7,200/mo</code> 2026$), and IRC §280A pro-rata rental deduction rules confirms that the strategy ranking never flips.</p>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Sensitivity Case</th>
        <th class="num">S1: Sell → Stocks</th>
        <th class="num">S2: Sell → 60/40</th>
        <th class="num">R: Rent [Property A]</th>
        <th class="num">S3: Sell → Treasuries</th>
        <th class="num">L2: Live + Rent U3</th>
        <th class="num">L1: Live (U3 Empty)</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(sens_rows)}
    </tbody>
  </table>
</div>
"""
    return render_page(
        "pages/decision-analysis.html",
        "Decision Matrix: Live vs. Rent vs. Sell & Reinvest",
        "After-tax household wealth comparisons across all 11 inheritance years (2040–2050), multiple asset allocations (Equities, 60/40, CA-Tax-Exempt U.S. Treasuries), and key tax/operating sensitivities.",
        body,
    )


def build_properties(inputs: dict, results: dict, ledger: Dict[str, dict]) -> str:
    audit_a = results["historical_roll_audit"]["property_a"]
    audit_b = results["historical_roll_audit"]["property_b"]

    profile_rows = [
        tr_row([td("[Property A] Estimated Market Value (Nov. 2026)"), td(fmt_usd(3100000), num=True, bold=True), td("Single-family residence held in family trust; anticipated transfer 2040–2050")], ["BOE-PROP19", "IRS-INHERIT-FAQ"], "owner", ledger),
        tr_row([td("[Property A] 2026 Assessed Value / 2025 Property Tax"), td("$550,540 / $7,210", num=True), td("2026 property tax bill left blank (unconfirmed); 2025 effective rate 1.336% of assessed value (0.233% of market value)")], ["BOE-LTA-2026-002", "SCC-TAXRATEBOOK-2025"], "owner", ledger),
        tr_row([td("[Property A] Solar, Water & Upkeep Baseline"), td("-$180/yr elec. · $1,500/yr water", num=True), td("Solar generates -$20 to -$10/mo net credit (20-yr CPUC NEM cap <=2046); water $100–$150/mo; upkeep lower than [Property B]")], ["CPUC-NEM", "CPUC-SJWC-GRC", "CFPB-UPKEEP"], "owner", ledger),
        tr_row([td("[Property B] Estimated Market Value (Nov. 2026)"), td(fmt_usd(1800000), num=True, bold=True), td("Already owned by inheritor; 3 livable units (no reassessment upon inheriting [Property A])")], ["SF-TTX-SECURED", "BOE-CIO-FAQ"], "owner", ledger),
        tr_row([td("[Property B] Rental Configuration & Current Income"), td("$7,150/mo ($85,800/yr)", num=True, bold=True), td("2 rented units generating ~$7,150/mo total; 1 unrented unit available for primary residence ($0 Empty Homes Tax per A172067)")], ["SF-RENT-RATES", "SF-EHT", "HUD-SAFMR-2027"], "owner", ledger),
        tr_row([td("[Property B] 2025 Assessed Value & Property Tax"), td("$114,250 / $2,440", num=True), td("Enrolls $7,000 Homeowners' Exemption (Gross FBYV $121,250); 2025 tax is 0.136% of $1,800,000 market value")], ["SF-TTX-SECURED", "BOE-HOX", "BOE-LTA-2026-002"], "owner", ledger),
        tr_row([td("[Property B] Water & Common Electricity (All 3 Units)"), td("$4,380/yr water · $600/yr elec.", num=True), td("Water $330–$400/mo across 3 units (subject to 12.6% / 12.5% FY27–FY28 utility hikes); electricity $30–$70/mo")], ["SFPUC-PROP218", "IRS-P527"], "owner", ledger),
    ]

    rows_a = []
    for r in reversed(audit_a):
        tx_cell = fmt_usd(r["property_tax_r10"])
        exp_cell = fmt_usd(r["expected_fbyv_r10"]) if r["expected_fbyv_r10"] is not None else "Base Year"
        res_cell = fmt_usd(r["rounding_residual_r10"], signed=True) if r["rounding_residual_r10"] is not None else "—"
        eff_cell = f"{r['effective_tax_rate_pct']:.3f}%" if r["effective_tax_rate_pct"] is not None else '<span class="blank-cell"></span>'
        st = "flagged" if r["property_tax_r10"] is None else "owner"
        rows_a.append(tr_row([
            td(str(r["year"]), bold=(r["year"] in (2025, 2026))),
            td(fmt_usd(r["assessed_value_r10"]), num=True),
            td(tx_cell, num=True),
            td(f"{r['boe_factor']:.5f}".rstrip("0").rstrip("."), num=True),
            td(exp_cell, num=True),
            td(res_cell, num=True),
            td(eff_cell, num=True),
        ], ["BOE-LTA-2026-002", "SCC-TAXRATEBOOK-2025"], st, ledger, "warn-row" if st == "flagged" else ""))

    rows_b = []
    for r in reversed(audit_b):
        av_cell = fmt_usd(r["assessed_value_r10"])
        tx_cell = fmt_usd(r["property_tax_r10"])
        exp_cell = fmt_usd(r["expected_net_av_with_7k_hox_r10"]) if r["expected_net_av_with_7k_hox_r10"] is not None else ("—" if r["year"] == 2026 else "Base Year")
        res_cell = fmt_usd(r["rounding_residual_r10"], signed=True) if r["rounding_residual_r10"] is not None else "—"
        eff_cell = f"{r['effective_tax_rate_pct']:.3f}%" if r["effective_tax_rate_pct"] is not None else '<span class="blank-cell"></span>'
        st = "flagged" if (r["property_tax_r10"] is None or (r["rounding_residual_r10"] is not None and abs(r["rounding_residual_r10"]) > 20)) else "owner"
        rows_b.append(tr_row([
            td(str(r["year"]), bold=(r["year"] in (2025, 2026))),
            td(av_cell, num=True),
            td(tx_cell, num=True),
            td(f"{r['boe_factor']:.5f}".rstrip("0").rstrip("."), num=True),
            td(exp_cell, num=True),
            td(res_cell, num=True),
            td(eff_cell, num=True),
        ], ["BOE-LTA-2026-002", "SF-TTX-SECURED", "BOE-HOX"], st, ledger, "warn-row" if st == "flagged" else ""))

    body = f"""
<h2>Baseline Property Summary ($10-Rounded Owner Inputs &amp; Official Context)</h2>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Attribute</th>
        <th class="num">$10-Rounded Baseline</th>
        <th>Notes &amp; Operational Role</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(profile_rows)}
    </tbody>
  </table>
</div>

<h2>Forensic Roll Audit: [Property A] (2014–2026) vs. Official BOE Prop. 13 Factors</h2>
<p>Comparing each year's <code>$10</code>-rounded assessed value against <code>Prior AV × Official BOE CCPI Factor</code> (from <code>BOE Letter 2026/002</code>) yields an exact <code>$0</code> residual from 2016 through 2025 (including sub-2% CCPI years <code>2016 = 1.01525</code> and <code>2021 = 1.01036</code>), proving an unbroken Proposition 13 base year with zero Homeowners' Exemption deducted on the reported line. The unconfirmed 2026 tax bill is left blank.</p>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Roll Year</th>
        <th class="num">Assessed Value ($10-Rounded)</th>
        <th class="num">Property Tax ($10-Rounded)</th>
        <th class="num">Official BOE Factor</th>
        <th class="num">Expected FBYV ($10)</th>
        <th class="num">Residual</th>
        <th class="num">Effective Tax %</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows_a)}
    </tbody>
  </table>
</div>

<h2>Forensic Roll Audit: [Property B] (2016–2026) &amp; Proof of $7,000 Homeowners' Exemption</h2>
<p>Applying <code>(Prior Net AV + $7,000 HOX) × Official BOE Factor - $7,000 HOX</code> matches [Property B]'s 2018–2025 net assessed values within <code>$0–$10</code> every year (including <code>2021 = 1.01036</code>), proving that [Property B] currently deducts the constitutional <code>$7,000</code> Homeowners' Exemption. Two items are flagged: (1) 2026 tax and assessed value were not supplied and remain blank; (2) <code>2016 → 2017</code> shows a <code>-$1,170</code> step difference (consistent with initial HOX enrollment or minor fixture adjustment).</p>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Roll Year</th>
        <th class="num">Net Assessed ($10-Rounded)</th>
        <th class="num">Property Tax ($10-Rounded)</th>
        <th class="num">Official BOE Factor</th>
        <th class="num">Expected Net AV w/ $7k HOX</th>
        <th class="num">Residual</th>
        <th class="num">Effective Tax %</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows_b)}
    </tbody>
  </table>
</div>
"""
    return render_page(
        "pages/properties.html",
        "Two-Property Baseline & Forensic Assessment Roll Audit",
        "Complete $10-rounded historical tax and assessment verification for [Property A] (2014–2026) and [Property B] (2016–2026) tested against official California BOE CCPI inflation factors.",
        body,
    )


def build_operating_costs(inputs: dict, results: dict, ledger: Dict[str, dict]) -> str:
    rows = [
        tr_row([
            td("Property Tax — [Property A] (2025 Verified / 2026 Official Bill)", bold=True),
            td("$7,210 (2025) / Blank (2026)", num=True),
            td("$7,350/yr (modeled 2026)", num=True),
            td("1.00% Prop. 13 levy ($5,400) + ~0.18% voter GO bonds ($970) + ~$840 fixed parcel charges; jumps to $51,150 (Live) or $75,370 (Rent) in 2045."),
        ], ["SCC-TAXRATEBOOK-2025", "BOE-PROP19"], "flagged", ledger, "warn-row"),
        tr_row([
            td("Property Tax — [Property B] (2025 Owner Roll / FY26-27 Rate)", bold=True),
            td("$2,440 (2025) / Blank (2026)", num=True),
            td("$2,480/yr (modeled 2026)", num=True),
            td("Verified 1.18162182% ad valorem rate ($1,350 on $114,250 net AV) + ~$1,090 parcel/special assessments; rises by ~$80/yr if $7,000 HOX moves to [Property A]."),
        ], ["SF-TTX-SECURED", "BOE-HOX"], "flagged", ledger, "warn-row"),
        tr_row([
            td("Homeowners Insurance — [Property A] ($3,100,000 Single-Family)", bold=True),
            td('<span class="blank-cell"></span> (CDI CA avg: $1,570)', num=True),
            td("$1,500 base / $4,200 sens.", num=True),
            td("CDI Oct. 27, 2026 statewide admitted average is $1,570 [$10-rounded]; parcel-specific HO-3/HO-5 quote for a $3,100,000 dwelling is unpublished (left blank; $4,200/yr replacement sensitivity tested)."),
        ], ["CDI-SNAPSHOT-2026", "CDI-STUDY"], "flagged", ledger, "warn-row"),
        tr_row([
            td("Rental Property Insurance — [Property B] ($1,800,000 3-Unit Building)", bold=True),
            td('<span class="blank-cell"></span> (Parcel quote blank)', num=True),
            td("$1,500 base / $6,500 sens.", num=True),
            td("3-unit mixed owner-occupied/tenant building requires Dwelling Fire / Habitational Landlord coverage + premises liability; parcel quote left blank and $6,500/yr sensitivity modeled."),
        ], ["CDI-STUDY", "CDI-SNAPSHOT-2026"], "flagged", ledger, "warn-row"),
        tr_row([
            td("Water Service — [Property A]", bold=True),
            td("$100–$150/mo ($1,200–$1,800/yr)", num=True),
            td("$1,500/yr (+4.49% in 2027)", num=True),
            td("Regulated Class A water GRC (D.24-12-077) adopted 3.99% escalation in 2026 and 4.49% in 2027; modeled at 3.3%/yr thereafter."),
        ], ["CPUC-SJWC-GRC"], "owner", ledger),
        tr_row([
            td("Water & Sewer — [Property B] (All 3 Units Master-Metered)", bold=True),
            td("$330–$400/mo ($3,960–$4,800/yr)", num=True),
            td("$4,380/yr (+12.6% / +12.5%)", num=True),
            td("Official Prop. 218 schedule increases combined water/sewer bills ~12.6% in FY2026–27 and ~12.5% in FY2027–28 before normalizing."),
        ], ["SFPUC-PROP218"], "verified", ledger),
        tr_row([
            td("Solar & Electricity — [Property A] (CPUC 20-Yr NEM Sunset)", bold=True),
            td("-$20 to -$10/mo (-$180/yr)", num=True),
            td("-$180/yr through 2046; +$1,260/yr real post-2046", num=True),
            td("CPUC D.14-03-041 grandfathers NEM 1.0/2.0 retail export credits for 20 years from interconnection (<=2046), then shifts to Net Billing Tariff (D.22-12-056) avoided-cost credits + inverter reserve."),
        ], ["CPUC-NEM"], "verified", ledger),
        tr_row([
            td("Common / Owner Electricity — [Property B]", bold=True),
            td("$30–$70/mo ($360–$840/yr)", num=True),
            td("$600/yr (+3.2%/yr)", num=True),
            td("Covers common-area and owner-paid electric load; tenants carry separately metered unit electricity."),
        ], ["CPUC-NEM", "IRS-P527"], "owner", ledger),
        tr_row([
            td("Regular Maintenance & Capital Upkeep — [Property A] vs. [Property B]", bold=True),
            td("Lower on [Property A] than [Property B]", num=True),
            td("$15,500/yr (0.50%) vs. $15,300/yr (0.85%)", num=True),
            td("[Property A] high land-value ratio modeled at 0.50% of value (stress 1.00% per CFPB); [Property B] 3-unit multi-kitchen/bath structure modeled at 0.85% of value (stress 1.25%)."),
        ], ["CFPB-UPKEEP", "IRS-P527"], "assumed", ledger),
        tr_row([
            td("HUD FY2027 Rental Benchmarks (Official $10-Rounded SAFMRs)", bold=True),
            td("Prop. A 4-BR: $5,800/mo · Prop. B 2-BR: $3,410/mo", num=True),
            td("$69,600/yr Prop. A · $85,800/yr Prop. B (2u)", num=True),
            td("Owner's $7,150/mo across 2 rented units (~$3,580/mo $10-rounded avg) aligns closely with HUD FY2027 2-BR ($3,410/mo) & 3-BR ($4,460/mo) SAFMRs."),
        ], ["HUD-SAFMR-2027", "SF-RENT-RATES"], "verified", ledger),
    ]

    body = f"""
<h2>Line-by-Line Operating Cost &amp; Benchmark Schedule (2026 Baseline &amp; Escalation Rules)</h2>
<p>Every operating cost input was cross-checked against official utility tariffs, county tax-rate books, California Department of Insurance market reports, and HUD FY2027 Small Area Fair Market Rent schedules. Where an exact parcel-level insurance quote or 2026 tax bill cannot be verified from a public government database without exposing parcel identity, the official value cell is left blank and flagged while both the owner's <code>$1,500/yr</code> baseline and realistic replacement-cost sensitivities (<code>$4,200/yr</code> and <code>$6,500/yr</code>) are modeled explicitly.</p>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Cost / Revenue Line Item</th>
        <th class="num">Verified / Owner Input ($10)</th>
        <th class="num">2026 Model Input ($10)</th>
        <th>Statutory &amp; Tariff Escalation Basis</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows)}
    </tbody>
  </table>
</div>
"""
    return render_page(
        "pages/operating-costs.html",
        "Operating Costs, Utilities, Solar NEM Sunset & Insurance",
        "Official-source breakdown of property taxes, homeowners vs. 3-unit rental insurance, CPUC/municipal water rate hikes, the 20-year solar NEM grandfathering cliff, and maintenance reserves.",
        body,
    )


def build_projections(inputs: dict, results: dict, ledger: Dict[str, dict]) -> str:
    yearly = results["yearly_2026_2076"]

    rows_a = []
    rows_b = []
    for r in yearly:
        yr = r["year"]
        rcls = "highlight-row" if yr == 2045 else ("warn-row" if yr == 2047 else "")
        rows_a.append(tr_row([
            td(str(yr), bold=(yr in (2026, 2045, 2047, 2065, 2076))),
            td(fmt_usd(r["val_a_nominal_r10"]), num=True, bold=(yr == 2045)),
            td(fmt_usd(r["val_a_real_r10"]), num=True),
            td(fmt_usd(r["av_a_live_nominal_r10"]), num=True),
            td(fmt_usd(r["av_a_rent_nominal_r10"]), num=True),
            td(fmt_usd(r["tax_a_live_nominal_r10"]), num=True),
            td(fmt_usd(r["tax_a_rent_nominal_r10"]), num=True),
            td(fmt_usd(r["ins_a_nominal_r10"]), num=True),
            td(fmt_usd(r["water_a_nominal_r10"]), num=True),
            td(fmt_usd(r["elec_a_nominal_r10"], signed=True), num=True),
            td(fmt_usd(r["maint_a_nominal_r10"]), num=True),
        ], ["BOE-PROP19", "CPUC-NEM", "CPUC-SJWC-GRC", "CDI-SNAPSHOT-2026"], "proj", ledger, rcls))

        rows_b.append(tr_row([
            td(str(yr), bold=(yr in (2026, 2045, 2065, 2076))),
            td(fmt_usd(r["val_b_nominal_r10"]), num=True),
            td(fmt_usd(r["val_b_real_r10"]), num=True),
            td(fmt_usd(r["av_b_occ_nominal_r10"]), num=True),
            td(fmt_usd(r["tax_b_occ_nominal_r10"]), num=True),
            td(fmt_usd(r["ins_b_nominal_r10"]), num=True),
            td(fmt_usd(r["water_b_nominal_r10"]), num=True),
            td(fmt_usd(r["elec_b_nominal_r10"]), num=True),
            td(fmt_usd(r["maint_b_nominal_r10"]), num=True),
            td(fmt_usd(r["rent_b_2u_nominal_r10"]), num=True, bold=True),
        ], ["SF-TTX-SECURED", "SFPUC-PROP218", "SF-RENT-RATES", "CFPB-UPKEEP"], "proj", ledger, "highlight-row" if yr == 2045 else ""))

    body = f"""
{svg_50yr_projection_lines(yearly)}

<h2>1. [Property A] Year-by-Year Projections: 2026–2076 (Nominal Dollars, $10-Rounded, 2045 Transfer Anchor)</h2>
<p>Note two structural inflections highlighted below: <strong>2045</strong> (Proposition 19 reassessment upon trust inheritance — partial cap if occupied vs. 100% FMV if rented) and <strong>2047</strong> (expiration of CPUC's 20-year NEM 2.0 retail solar credit period after 2046, shifting electricity from a small annual credit to Net Billing Tariff cost + inverter reserve).</p>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Year</th>
        <th class="num">Market Value</th>
        <th class="num">Real Value (2026$)</th>
        <th class="num">Assessed (Live)</th>
        <th class="num">Assessed (Rent)</th>
        <th class="num">Prop. Tax (Live)</th>
        <th class="num">Prop. Tax (Rent)</th>
        <th class="num">Insurance</th>
        <th class="num">Water</th>
        <th class="num">Solar / Elec.</th>
        <th class="num">Upkeep</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows_a)}
    </tbody>
  </table>
</div>

<h2>2. [Property B] Year-by-Year Projections: 2026–2076 (Nominal Dollars, $10-Rounded, Owner-Occupied HOX)</h2>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Year</th>
        <th class="num">Market Value</th>
        <th class="num">Real Value (2026$)</th>
        <th class="num">Net Assessed</th>
        <th class="num">Property Tax</th>
        <th class="num">Insurance</th>
        <th class="num">Water (3u)</th>
        <th class="num">Electricity</th>
        <th class="num">Upkeep</th>
        <th class="num">2-Unit Gross Rent</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows_b)}
    </tbody>
  </table>
</div>
"""
    return render_page(
        "pages/projections.html",
        "Year-by-Year Property & Cost Projections (2026–2076)",
        "Complete 51-year annual schedule (2026–2076) of market values, Prop. 13 / Prop. 19 assessed values, property taxes, insurance, water, electricity/solar, maintenance, and rent.",
        body,
    )


def build_black_swan(inputs: dict, results: dict, ledger: Dict[str, dict]) -> str:
    named = results["black_swan_named_regimes"]
    mc = results["black_swan_statistical"]["block_bootstrap_500_paths"]
    cohorts = results["black_swan_statistical"]["historical_50_cohorts"]["cohorts"]

    named_rows = []
    for b in named:
        h20 = b["horizon_20yr_2065"]
        rcls = "highlight-row" if b["winner_20yr"] == "sell_stocks" else "warn-row"
        named_rows.append(tr_row([
            td(f"{b['code']}: {html.escape(b['name'])}", bold=True),
            td(html.escape(b["summary"])),
            td(fmt_usd(h20["sell_stocks"]), num=True, bold=(b["winner_20yr"] == "sell_stocks")),
            td(fmt_usd(h20["sell_60_40"]), num=True),
            td(fmt_usd(h20["rent_a"]), num=True, bold=(b["winner_20yr"] == "rent_a")),
            td(fmt_usd(h20["sell_treasuries"]), num=True),
            td(fmt_usd(h20["live_a_keep_u3"]), num=True),
        ], ["BLS-CPI-2022", "FHFA-HPI", "TSP-RETURNS", "CBO-OUTLOOK-2026"], "proj", ledger, rcls))

    mc_rows = []
    for pkey, label in PLAN_META:
        m = mc[pkey]
        w_str = f"{m['win_share_pct']:.1f}%" if m["win_share_pct"] is not None else "Variant"
        mc_rows.append(tr_row([
            td(html.escape(label), bold=(pkey == "sell_stocks")),
            td(fmt_usd(m["p10_r10"]), num=True),
            td(fmt_usd(m["p25_r10"]), num=True),
            td(fmt_usd(m["p50_r10"]), num=True, bold=True),
            td(fmt_usd(m["p75_r10"]), num=True),
            td(fmt_usd(m["p90_r10"]), num=True),
            td(w_str, num=True),
        ], ["FRED-SERIES", "ERP-B56", "BOE-LTA-2026-002"], "proj", ledger, "highlight-row" if pkey == "sell_stocks" else ""))

    cohort_rows = []
    for c in cohorts:
        rcls = "warn-row" if c["winner"] != "sell_stocks" else ""
        cohort_rows.append(tr_row([
            td(str(c["cohort_start_year"]), bold=(c["winner"] != "sell_stocks")),
            td(fmt_usd(c["sell_stocks_real_r10"]), num=True, bold=(c["winner"] == "sell_stocks")),
            td(fmt_usd(c["sell_60_40_real_r10"]), num=True),
            td(fmt_usd(c["rent_a_real_r10"]), num=True, bold=(c["winner"] == "rent_a")),
            td(fmt_usd(c["sell_treasuries_real_r10"]), num=True),
            td(fmt_usd(c["live_a_keep_u3_real_r10"]), num=True),
            td(fmt_usd(c["adv_stocks_over_rent_r10"], signed=True), num=True),
        ], ["FRED-SERIES", "ERP-B56", "FHFA-HPI"], "proj", ledger, rcls))

    body = f"""
<div class="callout warn">
  <strong>Why Non-Uniform 50-Year Stress Testing Matters:</strong> Smooth constant-growth projections hide sequence-of-returns crashes, stagflationary bursts, climate insurance shocks, and statutory tax shifts. This section tests all strategies across (1) <strong>six multi-decade Black-Swan regimes</strong>, (2) <strong>500 block-bootstrapped 50-year paths</strong> (with equity returns conservatively de-meaned by <code>-2.0%/yr</code>), and (3) <strong>all 50 actual historical macro cohorts from 1976 through 2025</strong>.
</div>

<h2>1. Six Named 50-Year Non-Uniform Black-Swan Regimes (2045 Transfer → 2065 Real 2026$ Ex-[Property B])</h2>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Scenario</th>
        <th>Shock Architecture</th>
        <th class="num">S1: Stocks</th>
        <th class="num">S2: 60/40</th>
        <th class="num">R: Rent A</th>
        <th class="num">S3: Treasuries</th>
        <th class="num">L1: Live A</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(named_rows)}
    </tbody>
  </table>
</div>

<h2>2. 500-Path 5-Year Block-Bootstrap Distribution (De-Meaned Returns, 2065 Wealth in 2026$ Ex-[Property B])</h2>
<p>Even at the <strong>10th-percentile bad-luck tail</strong> (<code>{fmt_usd(mc["sell_stocks"]["p10_r10"])}</code>), selling [Property A] into broad equities exceeds the <em>median</em> outcome of moving into [Property A] (<code>{fmt_usd(mc["live_a_keep_u3"]["p50_r10"])}</code>). Meanwhile, <strong>Plan S2 (60/40 Stocks + CA-Tax-Exempt U.S. Treasuries)</strong> cushions immediate post-sale crashes (such as <code>BS-2</code>) with minimal median give-up.</p>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Strategy</th>
        <th class="num">10th Pct (Tail)</th>
        <th class="num">25th Pct</th>
        <th class="num">50th Pct (Median)</th>
        <th class="num">75th Pct</th>
        <th class="num">90th Pct</th>
        <th class="num">Win %</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(mc_rows)}
    </tbody>
  </table>
</div>

<h2>3. All 50 Rolling Historical Macro Cohorts (1976–2025 Actual CPI, Regional HPI, S&amp;P 500 &amp; Treasuries)</h2>
<p>Replaying actual year-by-year U.S. inflation, regional FHFA house price indexes, BOE Prop. 13 factors, S&amp;P 500 returns, and 10-year Treasury yields across every starting year from 1976 to 2025: <strong>Sell → Stocks wins 49 out of 50 historical cohorts (98.0%)</strong>; only the cohort hitting the 2000–2002 dot-com bust and 2008 financial crisis right after inheritance favors Rent [Property A] / 60-40.</p>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Historical Start Year</th>
        <th class="num">S1: Sell → Stocks</th>
        <th class="num">S2: Sell → 60/40</th>
        <th class="num">R: Rent [Property A]</th>
        <th class="num">S3: Treasuries</th>
        <th class="num">L1: Live [Property A]</th>
        <th class="num">Stocks vs. Rent Edge</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(cohort_rows)}
    </tbody>
  </table>
</div>
"""
    return render_page(
        "pages/black-swan-scenarios.html",
        "50-Year Black-Swan Economic Conditions & Historical Replay",
        "Non-uniform multi-decade economic shock modeling (stagflation, post-sale sequence-of-returns crash, regional housing bust, climate insurance surge, and §1014 repeal) plus 50-cohort historical replay.",
        body,
    )


def build_inheritance_law(inputs: dict, results: dict, ledger: Dict[str, dict]) -> str:
    rows = [
        tr_row([td("IRC §1014(a)/(b) & Rev. Rul. 2023-2", bold=True), td("Federal Basis Step-Up at Death"), td("Property in a revocable living trust included in the settlor's gross estate resets to 100% of date-of-death FMV; irrevocable trusts excluded from the gross estate do NOT get §1014 step-up.")], ["IRS-INHERIT-FAQ", "IRS-RR-2023-2"], "verified", ledger),
        tr_row([td("CA RTC §18031 & FTB Guidance", bold=True), td("California Full Conformity to §1014 & §121"), td("California incorporates IRC Subchapter O basis rules (full FMV step-up at death), excludes inheritances from income, and taxes post-death capital gains as ordinary income (up to 13.3%).")], ["CA-RTC-18031", "FTB-INHERIT", "FTB-CAPGAINS"], "verified", ledger),
        tr_row([td("Proposition 13 (Cal. Const. Art. XIII A)", bold=True), td("1% Base Levy + Max 2%/Yr CCPI Factor"), td("Assessed value compounds by min(2.0%, CCPI); 2026–27 CCPI was 3.307%, setting the 2026 roll factor at 1.02. Already-owned [Property B] keeps its $114,250 (2025) net assessed base.")], ["BOE-LTA-2026-002", "BOE-CIO-FAQ"], "verified", ledger),
        tr_row([td("Proposition 19 (CA RTC §63.2 & LTA 2026/026)", bold=True), td("Parent-Child Principal Residence Cap"), td("Applies ONLY if transferor's principal residence becomes transferee's principal residence within 1 year (filing BOE-266 & BOE-19-P). Excludes FBYV + $1,044,590 [$10-rounded from BOE Feb. 2025–Feb. 2027 schedule]; excess FMV added to roll. Rental/non-occupied inheritance gets $0 exclusion.")], ["BOE-PROP19", "CA-RTC-63-2", "BOE-NR-25-02", "BOE-LTA-2026-026"], "verified", ledger),
        tr_row([td("Homeowners' Exemption (BOE-266)", bold=True), td("$7,000 Assessed Value Reduction on One Home"), td("Available on a single owner-occupied primary residence. Moving from [Property B] to [Property A] requires terminating the exemption on [Property B] by Dec. 10 and claiming it on [Property A].")], ["BOE-HOX"], "verified", ledger),
        tr_row([td("Federal LTCG, IRC §1250 & 3.8% NIIT", bold=True), td("0%/15%/20% LTCG · 25% §1250 · 3.8% NIIT"), td("Long-term gains taxed up to 20% + 3.8% NIIT above unindexed $200,000 single / $250,000 MFJ MAGI; rental building depreciation recaptured up to 25% federal + CA ordinary rates.")], ["IRS-TC409", "IRS-TC559", "IRS-P527"], "verified", ledger),
        tr_row([td("IRC §121 Principal Residence Exclusion", bold=True), td("$250,000 Single / $500,000 MFJ"), td("Excludes post-inheritance capital gain on sale of a main home owned and occupied >=24 months of the prior 5 years (does not shield §1250 depreciation).")], ["IRS-TC701"], "verified", ledger),
        tr_row([td("CA Brackets & 1% Behavioral Health Tax", bold=True), td("1.0%–12.3% + 1.0% Over $1,000,000"), td("2025 top 12.3% bracket starts above $742,950 [$10-rounded] single ($1,485,910 [$10-rounded] MFJ), plus an unindexed 1% Behavioral Health Services surcharge above $1,000,000 taxable income.")], ["FTB-RATES-2025", "FTB-540ES-2026"], "verified", ledger),
        tr_row([td("Federal SALT Cap (P.L. 119-21 §70120)", bold=True), td("$40,400 in 2026 (2025–2029) → $10,000 in 2030+"), td("Temporarily raised to $40,000 (2025) and $40,400 (2026, phased down >$505,000 MAGI to $10,000 floor) through 2029; reverts to $10,000 in 2030 (covering the entire 2040–2050 transfer window).")], ["IRS-SALT-2026"], "verified", ledger),
        tr_row([td("Direct U.S. Treasury State Tax Exemption", bold=True), td("0% California Income Tax on U.S. Obligations"), td("Interest on Treasury Bills, Notes, Bonds, FRNs, and TIPS is 100% exempt from California up-to-13.3% income tax (reported as subtraction on Schedule CA 540).")], ["TD-TAX-EXEMPT", "FTB-PUB-1001"], "verified", ledger),
        tr_row([td("Documentary & Real Property Transfer Taxes", bold=True), td("0.11% [Jurisdiction A] · 0.50%–6.00% [Jurisdiction B]"), td("Inheritances without consideration are exempt. On sale, [Property A] pays only the 0.11% county tax ($0 city conveyance tax); [Property B] faces 0.75% ($1M–<$5M) or 2.25% ($5M–<$10M) on entire value.")], ["CA-RTC-11911", "SCC-RECORDER-FEES", "SF-TRANSFER-TAX"], "verified", ledger),
        tr_row([td("Local Rent Control, AB 1482 & Empty Homes Tax", bold=True), td("1.6% Local Cap (2026–27) · $0 Empty Homes Tax"), td("[Property B]'s 2 rented units are capped at 60% of regional CPI (1.6% for 3/2026–2/2027; Housing Inventory license required). Empty Homes Tax was invalidated and affirmed Sept. 11, 2026 (A172067). Trust-owned single-family [Property A] is AB 1482-exempt with lease notice.")], ["SF-RENT-LEARN", "SF-RENT-RATES", "SF-EHT", "CA-AG-RENTCAPS"], "verified", ledger),
    ]

    body = f"""
<h2>Federal, State &amp; Local Tax and Property Rules Governing the Two Properties</h2>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Statute / Authority</th>
        <th>Rule Summary</th>
        <th>Direct Impact on [Property A] &amp; [Property B]</th>
        <th>Official Sources</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows)}
    </tbody>
  </table>
</div>
"""
    return render_page(
        "pages/inheritance-law.html",
        "Federal, California & Local Tax and Property Law",
        "Line-by-line statutory guide to IRC §1014 basis step-up, Proposition 13, Proposition 19, Schedule E mixed-use allocation, transfer taxes, rent control, and CA-exempt U.S. Treasuries.",
        body,
    )
