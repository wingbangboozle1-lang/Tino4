#!/usr/bin/env python3
"""Deterministic, strictly $10-rounded two-property household decision and
50-year multi-regime black-swan stress engine (2026–2075).

All owner-supplied baseline inputs are stored ONLY in pre-rounded nearest-$10
form. No parcel numbers, street addresses, or unrounded tax-roll figures exist
anywhere in this module.
"""

from __future__ import annotations

import math
from typing import Any


def r10(val: float) -> int:
    """Round any dollar figure to the nearest $10 (half-up for positives)."""
    if val >= 0:
        return int(math.floor((val + 5.0) / 10.0) * 10)
    return -int(math.floor((abs(val) + 5.0) / 10.0) * 10)


# ---------------------------------------------------------------------------
# Strictly pre-rounded ($10) household baseline inputs
# ---------------------------------------------------------------------------
HIST_CUPERTINO = [
    {"year": 2021, "assessed": 512_960, "tax": 6_640},
    {"year": 2022, "assessed": 523_220, "tax": 6_870},
    {"year": 2023, "assessed": 533_680, "tax": 6_970},
    {"year": 2024, "assessed": 539_740, "tax": 7_000},
    {"year": 2025, "assessed": 550_540, "tax": 7_210},
]

HIST_SF = [
    {"year": 2021, "assessed": 106_660, "tax": 2_260},
    {"year": 2022, "assessed": 108_800, "tax": 2_280},
    {"year": 2023, "assessed": 110_970, "tax": 2_330},
    {"year": 2024, "assessed": 112_010, "tax": 2_340},
    {"year": 2025, "assessed": 114_250, "tax": 2_440},
]

BASE_INPUTS = {
    "start_year": 2026,
    "end_year": 2075,
    "cup_val_2026": 3_100_000,
    "sf_val_2026": 1_800_000,
    "cup_av_2025": 550_540,
    "cup_tax_2025": 7_210,
    "sf_av_2025": 114_250,
    "sf_tax_2025": 2_440,
    # Official ad valorem rates + implied 2025 fixed parcel/direct charges (rounded $10)
    "cup_ad_valorem_rate": 0.011488,   # Santa Clara County 2026 Assessor booklet typical TRA
    "sf_ad_valorem_rate": 0.01181622,  # SF BOS File 260971 FY2026-27 secured rate
    "hox_exemption": 7_000,            # CA BOE Pub. 800-6 Homeowners' Exemption
    "cup_fixed_charges_2025": 970,     # Reconciles $550,540 (less $7,000 HOX) * 1.1488% + $970 = $7,210
    "sf_fixed_charges_2025": 1_170,    # Reconciles $114,250 (less $7,000 HOX) * 1.1816% + $1,170 = $2,440
    # Operating costs in 2026 dollars (all divisible by $10)
    "cup_water_2026": 1_500,           # Midpoint of $100–$150/mo ($1,200–$1,800/yr)
    "cup_solar_credit_2026": -180,     # Midpoint of -$10 to -$20/mo (-$120 to -$240/yr) during NEM legacy
    "cup_post_nem_elec_2026": 1_440,   # Post-20-yr NEM sunset net grid + annualized inverter reserve ($120/mo in 2026$)
    "cup_nem_sunset_year": 2043,       # CPUC D.16-01-044 20-year legacy ends <= 2043 for pre-Apr 2023 NEM systems
    "cup_ins_model_2026": 4_800,       # High-value Silicon Valley rebuild assumption (official row blank; $1,500 owner guess tested)
    "cup_ins_owner_guess_2026": 1_500, # Owner's stated placeholder guess
    "cup_maint_pct": 0.0075,           # 0.75%/yr long-run capital + maintenance reserve ($23,250 in 2026$)
    "sf_rent_2units_2026": 85_800,     # $7,150/mo * 12 across 2 rented units
    "sf_unit3_mkt_rent_2026": 45_240,  # $3,770/mo (midpoint of HUD FY2026 94122 2-BR $3,310 & 3-BR $4,230 SAFMR)
    "sf_water_2026": 4_380,            # Midpoint of $330–$400/mo ($3,960–$4,800/yr) across 3 units
    "sf_elec_2026": 600,               # Midpoint of $30–$70/mo ($360–$840/yr)
    "sf_ins_model_2026": 4_500,        # 3-unit habitational policy assumption (official row blank)
    "sf_maint_pct": 0.0085,            # 0.85%/yr coastal 3-unit maintenance/capex reserve ($15,300 in 2026$)
    # Baseline macro & tax parameters (anchored to CBO, IRS Rev. Proc. 2026-35, CA FTB, HUD, TSP)
    "cpi_base": 0.023,                 # CBO long-run CPI-U (~2.3%/yr)
    "cup_apprec_base": 0.035,          # 3.5%/yr nominal baseline (~1.2% real over CPI)
    "sf_apprec_base": 0.030,           # 3.0%/yr nominal baseline (~0.7% real over CPI)
    "ins_infl_base": 0.040,            # Insurance cost trend above general CPI
    "util_infl_base": 0.032,           # Regulated water/electric trend
    "equity_div_yield": 0.015,         # 1.5% qualified dividend yield
    "equity_price_growth": 0.055,      # 5.5% price growth -> 7.0% nominal total return (conservative vs 11.34% TSP C-Fund history)
    "treasury_yield_base": 0.043,      # CBO 2026–2036 10-yr Treasury average (4.3%)
    "cup_gross_rent_yield_hud": 76_680 / 3_100_000,  # HUD FY2026 95014 4-BR SAFMR ($6,390/mo = 2.4735%)
    "cup_gross_rent_yield_base": 0.028,              # 2.80% baseline SFH gross rent yield (~$7,230/mo in 2026$)
    # Transaction & tax rates
    "sale_broker_closing_pct": 0.0500, # 5.00% agent commissions, title, escrow, prep
    "scc_transfer_tax_pct": 0.0011,    # Verified Santa Clara County $0.55/$500 = 0.11% ($0 Cupertino city tax)
    "fed_ord_niit_rate": 0.358,        # 32% federal bracket + 3.8% NIIT on passive/interest income
    "fed_qual_div_niit_rate": 0.188,   # 15% federal qualified dividend + 3.8% NIIT
    "fed_ltcg_niit_rate": 0.238,       # 20% top federal LTCG + 3.8% NIIT on large liquidations
    "fed_sec1250_niit_rate": 0.288,    # 25% max unrecaptured §1250 depreciation + 3.8% NIIT
    "ca_marginal_inc_rate": 0.103,     # 9.3%–11.3% California marginal rate on annual portfolio/rental income
    "ca_liquidation_cg_rate": 0.123,   # 12.3%–13.3% California rate on multi-million lump-sum gain realization
    "prop19_cap_2025_2027": 1_044_590, # BOE NR 25-02 allowance rounded to nearest $10
    "estate_excl_2026": 15_000_000,    # P.L. 119-21 / Form 706 (2026)
    "estate_excl_2027": 15_480_000,    # IRS Rev. Proc. 2026-35 (2027)
}


# ---------------------------------------------------------------------------
# 50-year regime path generators (2026–2075)
# ---------------------------------------------------------------------------
def build_regime_paths(regime_id: str) -> dict[int, dict[str, float]]:
    """Return year-by-year macro & asset-return paths for 2026..2075."""
    paths: dict[int, dict[str, float]] = {}
    for yr in range(2026, 2076):
        p = {
            "cpi": BASE_INPUTS["cpi_base"],
            "cup_g": BASE_INPUTS["cup_apprec_base"],
            "sf_g": BASE_INPUTS["sf_apprec_base"],
            "eq_price": BASE_INPUTS["equity_price_growth"],
            "eq_div": BASE_INPUTS["equity_div_yield"],
            "tsy": BASE_INPUTS["treasury_yield_base"],
            "ins_g": BASE_INPUTS["ins_infl_base"],
            "util_g": BASE_INPUTS["util_infl_base"],
            "rent_g": 0.030,
            "capex_shock_cup": 0.0,
            "step_up_repealed": 0.0,
            "estate_excl_cut": 0.0,
        }
        # SFPUC verified FY2027 & FY2028 water/sewer rate adjustments (+12.6%, +12.5%)
        p["sf_water_g"] = 0.126 if yr == 2027 else (0.125 if yr == 2028 else p["util_g"])

        if regime_id == "R1_STAGFLATION":
            # Replays 1973–1982 / 2021–2022 (+9.1% BLS CPI) stagflation & CBO +150bp/+250bp rate shock
            if 2037 <= yr <= 2042:
                seq = {
                    2037: (0.062, -0.020, -0.030, -0.140, 0.058),
                    2038: (0.088, 0.010, 0.000, -0.110, 0.068),
                    2039: (0.091, 0.025, 0.015, 0.020, 0.072),
                    2040: (0.074, 0.020, 0.010, -0.060, 0.069),
                    2041: (0.055, 0.030, 0.020, 0.085, 0.062),
                    2042: (0.042, 0.040, 0.030, 0.110, 0.056),
                }[yr]
                p["cpi"], p["cup_g"], p["sf_g"], p["eq_price"], p["tsy"] = seq
                p["ins_g"] = p["cpi"] + 0.035
                p["util_g"] = p["cpi"] + 0.020
                p["rent_g"] = p["cpi"] * 0.85
            elif 2058 <= yr <= 2061:
                p["cpi"] = 0.068
                p["cup_g"] = 0.015
                p["sf_g"] = 0.010
                p["eq_price"] = -0.070 if yr in (2058, 2059) else 0.095
                p["tsy"] = 0.064
                p["ins_g"] = 0.095
                p["util_g"] = 0.080

        elif regime_id == "R2_GFC_AT_TRANSFER":
            # Replays 2007–2009 Fed SCF crash (-22% housing, -37% equities) across 2044–2046 transfer window
            if 2044 <= yr <= 2049:
                seq = {
                    2044: (0.012, -0.100, -0.080, -0.220, 0.028),
                    2045: (0.004, -0.140, -0.120, -0.210, 0.022),
                    2046: (0.015, -0.030, -0.030, 0.190, 0.026),
                    2047: (0.020, 0.045, 0.035, 0.145, 0.032),
                    2048: (0.022, 0.055, 0.045, 0.110, 0.038),
                    2049: (0.023, 0.050, 0.040, 0.085, 0.041),
                }[yr]
                p["cpi"], p["cup_g"], p["sf_g"], p["eq_price"], p["tsy"] = seq
                p["rent_g"] = -0.040 if yr in (2044, 2045) else 0.028

        elif regime_id == "R3_SEQ_CRASH_AFTER_SALE":
            # Sequence-of-returns stress: inheritance & sale at 2045 peak, then -38% equity drop in 2046–2047
            if 2043 <= yr <= 2045:
                p["cup_g"] = 0.065
                p["eq_price"] = 0.090
            elif yr == 2046:
                p["cpi"] = 0.010
                p["cup_g"] = -0.110
                p["sf_g"] = -0.090
                p["eq_price"] = -0.240
                p["tsy"] = 0.025
            elif yr == 2047:
                p["cpi"] = 0.014
                p["cup_g"] = -0.090
                p["sf_g"] = -0.070
                p["eq_price"] = -0.180
                p["tsy"] = 0.027
            elif 2048 <= yr <= 2051:
                p["eq_price"] = 0.125
                p["cup_g"] = 0.040

        elif regime_id == "R4_BAY_AREA_SEISMIC_TECH":
            # Localized Silicon Valley / Bay Area seismic + insurance + tech relocation shock (2048–2053)
            if yr == 2048:
                p["cup_g"] = -0.180
                p["sf_g"] = -0.140
                p["ins_g"] = 0.450
                p["capex_shock_cup"] = 160_000.0  # Uninsured earthquake deductible / structural repair
                p["rent_g"] = -0.080
            elif yr in (2049, 2050):
                p["cup_g"] = -0.070
                p["sf_g"] = -0.050
                p["ins_g"] = 0.180
                p["rent_g"] = -0.020
            elif 2051 <= yr <= 2055:
                p["cup_g"] = 0.025
                p["sf_g"] = 0.022
                p["ins_g"] = 0.055

        elif regime_id == "R5_TAX_LAW_REVERSAL":
            # Statutory stress from 2038 onward: IRC §1014 step-up repealed (carryover basis taxed on sale)
            # and federal estate basic exclusion cut to $5,000,000 (2026$ indexed)
            if yr >= 2038:
                p["step_up_repealed"] = 1.0
                p["estate_excl_cut"] = 1.0

        elif regime_id == "R6_EQUITY_LOST_DECADE_SV_BOOM":
            # Replays 2000–2011 secular equity stagnation (~2.7% nominal total return) alongside
            # supply-constrained Silicon Valley housing outperformance (5.4%/yr in 95014)
            if 2045 <= yr <= 2059:
                p["eq_price"] = -0.160 if yr in (2045, 2046, 2053) else 0.042
                p["cup_g"] = 0.054
                p["sf_g"] = 0.038
                p["tsy"] = 0.046

        paths[yr] = p
    return paths


# ---------------------------------------------------------------------------
# Baseline 50-year property trajectories (pre-inheritance & no-transfer reference)
# ---------------------------------------------------------------------------
def simulate_property_series(regime_id: str = "R0_BASELINE") -> list[dict[str, Any]]:
    """Project year-by-year (2026–2075) standalone trajectories for both properties
    prior to reassessment at inheritance (showing Prop. 13 FBYV vs market value),
    plus Prop. 19 allowance and indexed federal estate exclusion."""
    paths = build_regime_paths(regime_id)
    rows: list[dict[str, Any]] = []

    cup_val = float(BASE_INPUTS["cup_val_2026"])
    sf_val = float(BASE_INPUTS["sf_val_2026"])
    cup_fbyv = float(BASE_INPUTS["cup_av_2025"])
    sf_fbyv = float(BASE_INPUTS["sf_av_2025"])
    cup_fixed = float(BASE_INPUTS["cup_fixed_charges_2025"])
    sf_fixed = float(BASE_INPUTS["sf_fixed_charges_2025"])

    cup_water = float(BASE_INPUTS["cup_water_2026"])
    cup_solar = float(BASE_INPUTS["cup_solar_credit_2026"])
    cup_post_nem = float(BASE_INPUTS["cup_post_nem_elec_2026"])
    cup_ins = float(BASE_INPUTS["cup_ins_model_2026"])
    cup_ins_guess = float(BASE_INPUTS["cup_ins_owner_guess_2026"])

    sf_rent2 = float(BASE_INPUTS["sf_rent_2units_2026"])
    sf_unit3_rent = float(BASE_INPUTS["sf_unit3_mkt_rent_2026"])
    sf_water = float(BASE_INPUTS["sf_water_2026"])
    sf_elec = float(BASE_INPUTS["sf_elec_2026"])
    sf_ins = float(BASE_INPUTS["sf_ins_model_2026"])

    prop19_cap = float(BASE_INPUTS["prop19_cap_2025_2027"])
    estate_excl = float(BASE_INPUTS["estate_excl_2026"])
    cum_hpi_2yr = 1.0

    for yr in range(2026, 2076):
        p = paths[yr]
        if yr > 2026:
            cup_val *= 1.0 + p["cup_g"]
            sf_val *= 1.0 + p["sf_g"]
            cup_water *= 1.0 + p["util_g"]
            cup_solar *= 1.0 + p["cpi"]
            cup_post_nem *= 1.0 + p["util_g"]
            cup_ins *= 1.0 + p["ins_g"]
            cup_ins_guess *= 1.0 + p["ins_g"]
            sf_water *= 1.0 + p["sf_water_g"]
            sf_elec *= 1.0 + p["util_g"]
            sf_ins *= 1.0 + p["ins_g"]
            # SF Rent Ordinance: 1.6% verified for 2026-27, then 60% of CPI (capped at 10%)
            sf_rc_inc = 0.016 if yr == 2027 else min(0.10, max(0.0, 0.60 * p["cpi"]))
            sf_rent2 *= 1.0 + sf_rc_inc
            sf_unit3_rent *= 1.0 + max(-0.10, p["rent_g"])

        # Prop. 13 FBYV advances by min(2%, max(0%, CPI)) from 2025 onward
        prop13_factor = 1.0 + min(0.02, max(0.0, p["cpi"]))
        cup_fbyv *= prop13_factor
        sf_fbyv *= prop13_factor
        cup_fixed *= 1.0 + max(0.0, p["cpi"])
        sf_fixed *= 1.0 + max(0.0, p["cpi"])

        # Prop. 8 temporary decline-in-value check (enrolled = min(FBYV, Market Value))
        cup_enrolled = min(cup_fbyv, cup_val)
        sf_enrolled = min(sf_fbyv, sf_val)

        cup_tax_pre = (
            BASE_INPUTS["cup_ad_valorem_rate"] * max(0.0, cup_enrolled - BASE_INPUTS["hox_exemption"])
            + cup_fixed
        )
        sf_tax = (
            BASE_INPUTS["sf_ad_valorem_rate"] * max(0.0, sf_enrolled - BASE_INPUTS["hox_exemption"])
            + sf_fixed
        )

        # Biennial Prop. 19 FHFA CA HPI adjustment on odd years >= 2027
        cum_hpi_2yr *= 1.0 + (0.5 * p["cup_g"] + 0.5 * p["sf_g"])
        if yr >= 2027 and yr % 2 == 1:
            prop19_cap *= max(0.95, cum_hpi_2yr)
            cum_hpi_2yr = 1.0
        elif yr == 2026:
            cum_hpi_2yr = 1.0 + 0.0215  # Carries 2025-26 HPI step into 2027 reset

        # Federal estate tax basic exclusion (verified $15,000,000 in 2026; $15,480,000 in 2027)
        if yr == 2026:
            estate_excl = float(BASE_INPUTS["estate_excl_2026"])
        elif yr == 2027:
            estate_excl = float(BASE_INPUTS["estate_excl_2027"])
        else:
            estate_excl *= 1.0 + max(0.0, p["cpi"] - 0.002)  # Chained-CPI indexing per P.L. 119-21

        eff_estate_excl = estate_excl * (0.35 if p["estate_excl_cut"] > 0 else 1.0)

        cup_elec = cup_solar if yr < BASE_INPUTS["cup_nem_sunset_year"] else cup_post_nem
        cup_maint = cup_val * BASE_INPUTS["cup_maint_pct"] + p["capex_shock_cup"]
        sf_maint = sf_val * BASE_INPUTS["sf_maint_pct"]

        # If inherited in year `yr`: Prop. 19 vs Full Reassessment new Year-1 Cupertino tax
        prop19_av_if_transfer = cup_fbyv + max(0.0, cup_val - (cup_fbyv + prop19_cap))
        cup_tax_prop19_yr1 = (
            BASE_INPUTS["cup_ad_valorem_rate"] * max(0.0, prop19_av_if_transfer - BASE_INPUTS["hox_exemption"])
            + cup_fixed
        )
        cup_tax_full_yr1 = BASE_INPUTS["cup_ad_valorem_rate"] * cup_val + cup_fixed

        rows.append(
            {
                "year": yr,
                "cpi_pct": round(p["cpi"] * 100, 2),
                "cup_val": r10(cup_val),
                "cup_fbyv_pre": r10(cup_enrolled),
                "cup_tax_pre": r10(cup_tax_pre),
                "prop19_cap": r10(prop19_cap),
                "cup_av_prop19_if_inh": r10(prop19_av_if_transfer),
                "cup_tax_prop19_if_inh": r10(cup_tax_prop19_yr1),
                "cup_tax_full_if_inh": r10(cup_tax_full_yr1),
                "cup_water": r10(cup_water),
                "cup_elec": r10(cup_elec),
                "cup_ins_model": r10(cup_ins),
                "cup_ins_guess": r10(cup_ins_guess),
                "cup_maint": r10(cup_maint),
                "sf_val": r10(sf_val),
                "sf_fbyv": r10(sf_enrolled),
                "sf_tax": r10(sf_tax),
                "sf_rent_2u": r10(sf_rent2),
                "sf_unit3_mkt_rent": r10(sf_unit3_rent),
                "sf_water": r10(sf_water),
                "sf_elec": r10(sf_elec),
                "sf_ins_model": r10(sf_ins),
                "sf_maint": r10(sf_maint),
                "estate_excl_single": r10(eff_estate_excl),
                "estate_excl_married_dsue": r10(eff_estate_excl * 2.0),
                # Float values retained internally for exact simulation before final $10 rounding
                "_f": {
                    "cup_val": cup_val,
                    "cup_fbyv": cup_fbyv,
                    "cup_fixed": cup_fixed,
                    "cup_water": cup_water,
                    "cup_elec": cup_elec,
                    "cup_ins": cup_ins,
                    "cup_ins_guess": cup_ins_guess,
                    "cup_maint": cup_maint,
                    "prop19_cap": prop19_cap,
                    "sf_val": sf_val,
                    "sf_fbyv": sf_fbyv,
                    "sf_fixed": sf_fixed,
                    "sf_rent2": sf_rent2,
                    "sf_unit3_rent": sf_unit3_rent,
                    "sf_water": sf_water,
                    "sf_elec": sf_elec,
                    "sf_ins": sf_ins,
                    "sf_maint": sf_maint,
                    "estate_excl": eff_estate_excl,
                },
            }
        )
    return rows


# ---------------------------------------------------------------------------
# Integrated Two-Property Post-Inheritance Plan Comparison Engine
# ---------------------------------------------------------------------------
def evaluate_plans(
    inh_year: int = 2045,
    horizon_years: int = 20,
    regime_id: str = "R0_BASELINE",
    use_owner_ins_guess: bool = False,
    cup_rent_yield_override: float | None = None,
    eq_return_shift: float = 0.0,
    cash_inheritance_buffer: float = 1_000_000.0,
) -> dict[str, Any]:
    """Compare all 5 integrated two-property household plans over
    [inh_year, inh_year + horizon_years - 1]:
      - P1A_SELL_EQUITY: Sell Cupertino at stepped-up basis, stay in SF Unit 3, invest in broad equities
      - P1B_SELL_TREASURY: Sell Cupertino at stepped-up basis, stay in SF Unit 3, invest in CA-tax-exempt U.S. Treasuries
      - P2A_LIVE_CUP_SF2U: Move into Cupertino (claim Prop. 19), keep SF Unit 3 unrented (2 SF units rented)
      - P2B_LIVE_CUP_SF3U: Move into Cupertino (claim Prop. 19), rent out vacated SF Unit 3 under SF rent control (3 SF units rented)
      - P3_RENT_CUP_STAY_SF: Rent out Cupertino (full Prop. 19 reassessment), stay in SF Unit 3 (2 SF units rented)
    """
    paths = build_regime_paths(regime_id)
    series = {r["year"]: r["_f"] for r in simulate_property_series(regime_id)}
    end_yr = min(2075, inh_year + horizon_years - 1)
    actual_h = end_yr - inh_year + 1

    s0 = series[inh_year]
    v_cup_inh = s0["cup_val"]
    fbyv_cup_inh = s0["cup_fbyv"]
    p19_cap_inh = s0["prop19_cap"]

    # Net proceeds if Cupertino sold promptly at inheritance
    gross_sale_costs = v_cup_inh * (
        BASE_INPUTS["sale_broker_closing_pct"] + BASE_INPUTS["scc_transfer_tax_pct"]
    )
    # Under current law (IRC §1014 + CA RTC §18031), pre-death gain tax = $0.
    # In R5_TAX_LAW_REVERSAL, carryover basis (~$550,540) triggers combined federal + CA tax.
    carryover_cg_tax = 0.0
    if paths[inh_year]["step_up_repealed"] > 0:
        taxable_gain = max(0.0, v_cup_inh - gross_sale_costs - BASE_INPUTS["cup_av_2025"])
        carryover_cg_tax = taxable_gain * (
            BASE_INPUTS["fed_ltcg_niit_rate"] + BASE_INPUTS["ca_liquidation_cg_rate"]
        )
    net_sale_proceeds = v_cup_inh - gross_sale_costs - carryover_cg_tax

    comb_ord_rate = BASE_INPUTS["fed_ord_niit_rate"] + BASE_INPUTS["ca_marginal_inc_rate"]
    comb_div_rate = BASE_INPUTS["fed_qual_div_niit_rate"] + BASE_INPUTS["ca_marginal_inc_rate"]
    comb_ltcg_liq = BASE_INPUTS["fed_ltcg_niit_rate"] + BASE_INPUTS["ca_liquidation_cg_rate"]
    comb_recap_liq = BASE_INPUTS["fed_sec1250_niit_rate"] + BASE_INPUTS["ca_liquidation_cg_rate"]

    cup_yield = (
        cup_rent_yield_override
        if cup_rent_yield_override is not None
        else BASE_INPUTS["cup_gross_rent_yield_base"]
    )

    plan_keys = [
        "P1A_SELL_EQUITY",
        "P1B_SELL_TREASURY",
        "P2A_LIVE_CUP_SF2U",
        "P2B_LIVE_CUP_SF3U",
        "P3_RENT_CUP_STAY_SF",
    ]
    results: dict[str, Any] = {}

    for pk in plan_keys:
        sold_cup = pk in ("P1A_SELL_EQUITY", "P1B_SELL_TREASURY")
        invest_in_eq = pk != "P1B_SELL_TREASURY"  # Excess cash flows compound in equity or Treasury matching plan style
        live_in_cup = pk in ("P2A_LIVE_CUP_SF2U", "P2B_LIVE_CUP_SF3U")
        rent_sf_u3 = pk == "P2B_LIVE_CUP_SF3U"
        rent_cup = pk == "P3_RENT_CUP_STAY_SF"

        # Initial liquid portfolio & tax basis at start of inh_year
        liq_val = cash_inheritance_buffer + (net_sale_proceeds if sold_cup else 0.0)
        liq_basis = liq_val

        # Initial Cupertino Prop. 13 / Prop. 19 base-year value if retained
        if live_in_cup:
            cup_fbyv_post = fbyv_cup_inh + max(0.0, v_cup_inh - (fbyv_cup_inh + p19_cap_inh))
        elif rent_cup:
            cup_fbyv_post = v_cup_inh
        else:
            cup_fbyv_post = 0.0

        # Rental Cupertino depreciable basis (35% structure share over 27.5 yrs per IRS Pub. 527)
        cup_depr_annual = (0.35 * v_cup_inh / 27.5) if rent_cup else 0.0
        cum_cup_depr = 0.0
        suspended_passive_loss = 0.0
        sf_u3_rent_curr = s0["sf_unit3_rent"]

        cum_after_tax_op_cf = 0.0
        cum_prop_tax_paid = 0.0
        yr1_net_op_cf = 0.0
        yr1_cup_tax = 0.0
        yearly_log: list[dict[str, int]] = []

        for idx, yr in enumerate(range(inh_year, end_yr + 1)):
            p = paths[yr]
            st = series[yr]
            if idx > 0:
                cup_fbyv_post *= 1.0 + min(0.02, max(0.0, p["cpi"]))
                sf_rc_inc = 0.016 if yr == 2027 else min(0.10, max(0.0, 0.60 * p["cpi"]))
                sf_u3_rent_curr *= 1.0 + sf_rc_inc

            # --- 1. San Francisco (94122) cash flow ---
            sf_enrolled = min(st["sf_fbyv"], st["sf_val"])
            sf_hox = 0.0 if live_in_cup else BASE_INPUTS["hox_exemption"]
            sf_tax = BASE_INPUTS["sf_ad_valorem_rate"] * max(0.0, sf_enrolled - sf_hox) + st["sf_fixed"]
            sf_ins = st["cup_ins_guess"] if use_owner_ins_guess else st["sf_ins"]
            sf_tot_exp = sf_tax + sf_ins + st["sf_water"] + st["sf_elec"] + st["sf_maint"]

            sf_gross_rent = st["sf_rent2"] * 0.96 + (sf_u3_rent_curr * 0.95 if rent_sf_u3 else 0.0)
            rental_share_sf = 1.0 if rent_sf_u3 else (2.0 / 3.0)
            sf_taxable_inc = sf_gross_rent - rental_share_sf * sf_tot_exp
            sf_inc_tax = max(0.0, sf_taxable_inc) * comb_ord_rate
            sf_net_cf = sf_gross_rent - sf_tot_exp - sf_inc_tax

            # --- 2. Cupertino (95014) cash flow ---
            cup_tax = 0.0
            cup_net_cf = 0.0
            if not sold_cup:
                cup_enrolled = min(cup_fbyv_post, st["cup_val"])
                cup_hox = BASE_INPUTS["hox_exemption"] if live_in_cup else 0.0
                cup_tax = (
                    BASE_INPUTS["cup_ad_valorem_rate"] * max(0.0, cup_enrolled - cup_hox)
                    + st["cup_fixed"]
                )
                cup_ins = st["cup_ins_guess"] if use_owner_ins_guess else st["cup_ins"]
                cup_op_exp = cup_tax + cup_ins + st["cup_water"] + st["cup_elec"] + st["cup_maint"]

                if live_in_cup:
                    cup_net_cf = -cup_op_exp
                elif rent_cup:
                    # Gross Cupertino rent less 5% vacancy and 6% management/leasing
                    cup_gross_rent = st["cup_val"] * cup_yield
                    cup_eff_rent = cup_gross_rent * (1.0 - 0.05 - 0.06)
                    depr_this_yr = cup_depr_annual if idx < 27 else (cup_depr_annual * 0.5 if idx == 27 else 0.0)
                    cum_cup_depr += depr_this_yr
                    taxable_cup = cup_eff_rent - cup_op_exp - depr_this_yr
                    if taxable_cup < 0:
                        # IRC §469: passive loss suspended at high MAGI, carried forward
                        suspended_passive_loss += -taxable_cup
                        cup_inc_tax = 0.0
                    else:
                        used_loss = min(suspended_passive_loss, taxable_cup)
                        suspended_passive_loss -= used_loss
                        cup_inc_tax = (taxable_cup - used_loss) * comb_ord_rate
                    cup_net_cf = cup_eff_rent - cup_op_exp - cup_inc_tax

            tot_op_cf = sf_net_cf + cup_net_cf
            cum_after_tax_op_cf += tot_op_cf
            cum_prop_tax_paid += sf_tax + cup_tax
            if idx == 0:
                yr1_net_op_cf = tot_op_cf
                yr1_cup_tax = cup_tax

            # --- 3. Liquid portfolio compounding ---
            if invest_in_eq:
                # Equity return: dividends taxed annually; price appreciation compounds tax-deferred
                after_tax_div = max(0.0, liq_val) * p["eq_div"] * (1.0 - comb_div_rate)
                price_gain = liq_val * (p["eq_price"] + eq_return_shift)
                liq_val = liq_val + price_gain + after_tax_div + tot_op_cf
                liq_basis = liq_basis + after_tax_div + tot_op_cf
            else:
                # U.S. Treasury notes: federal ordinary + NIIT tax only, 0% CA income tax (FTB Pub. 1001)
                after_tax_tsy_rate = p["tsy"] * (1.0 - BASE_INPUTS["fed_ord_niit_rate"])
                tsy_interest_net = liq_val * after_tax_tsy_rate
                liq_val = liq_val + tsy_interest_net + tot_op_cf
                liq_basis = liq_val

            yearly_log.append(
                {
                    "year": yr,
                    "sf_net_cf": r10(sf_net_cf),
                    "cup_net_cf": r10(cup_net_cf),
                    "tot_op_cf": r10(tot_op_cf),
                    "liq_val": r10(liq_val),
                    "cup_val": 0 if sold_cup else r10(st["cup_val"]),
                    "sf_val": r10(st["sf_val"]),
                }
            )

        # --- End-of-horizon valuation (both Holding Net Worth and Full After-Tax Liquidation Value) ---
        end_st = series[end_yr]
        sf_end_val = end_st["sf_val"]
        cup_end_val = 0.0 if sold_cup else end_st["cup_val"]
        pre_liq_nw = liq_val + sf_end_val + cup_end_val

        # Embedded taxes if Cupertino + liquid portfolio were liquidated at end_yr (keeping SF home)
        embedded_eq_tax = max(0.0, liq_val - liq_basis) * comb_ltcg_liq if invest_in_eq else 0.0
        embedded_cup_exit_cost = 0.0
        if not sold_cup:
            sale_fric_end = cup_end_val * (
                BASE_INPUTS["sale_broker_closing_pct"] + BASE_INPUTS["scc_transfer_tax_pct"]
            )
            base_at_death = (
                BASE_INPUTS["cup_av_2025"] if paths[inh_year]["step_up_repealed"] > 0 else v_cup_inh
            )
            sec121_excl = 500_000.0 if live_in_cup and actual_h >= 2 else 0.0
            apprec_gain = max(0.0, (cup_end_val - sale_fric_end) - base_at_death - sec121_excl)
            # Released IRC §469 suspended passive losses offset disposition gain
            net_apprec_gain = max(0.0, apprec_gain - suspended_passive_loss)
            recap_tax = cum_cup_depr * comb_recap_liq
            cg_tax_end = net_apprec_gain * comb_ltcg_liq
            embedded_cup_exit_cost = sale_fric_end + recap_tax + cg_tax_end

        post_liq_nw = pre_liq_nw - embedded_eq_tax - embedded_cup_exit_cost

        results[pk] = {
            "plan_id": pk,
            "inh_year": inh_year,
            "end_year": end_yr,
            "horizon_years": actual_h,
            "cup_fmv_at_inh": r10(v_cup_inh),
            "net_sale_proceeds_at_inh": r10(net_sale_proceeds) if sold_cup else 0,
            "yr1_cup_prop_tax": r10(yr1_cup_tax),
            "yr1_household_op_cf": r10(yr1_net_op_cf),
            "cum_prop_tax_20yr": r10(cum_prop_tax_paid),
            "cum_op_cf_20yr": r10(cum_after_tax_op_cf),
            "end_liq_portfolio": r10(liq_val),
            "end_cup_equity": r10(cup_end_val),
            "end_sf_equity": r10(sf_end_val),
            "pre_liquidation_net_worth": r10(pre_liq_nw),
            "after_liquidation_net_worth": r10(post_liq_nw),
            "yearly": yearly_log,
        }

    ranked = sorted(
        results.values(), key=lambda x: x["after_liquidation_net_worth"], reverse=True
    )
    return {
        "inh_year": inh_year,
        "end_year": end_yr,
        "regime_id": regime_id,
        "cup_fmv_at_inh": r10(v_cup_inh),
        "cup_fbyv_pre_at_inh": r10(fbyv_cup_inh),
        "prop19_cap_at_inh": r10(p19_cap_inh),
        "net_sale_proceeds_if_sold": r10(net_sale_proceeds),
        "plans": results,
        "winner_id": ranked[0]["plan_id"],
        "runner_up_id": ranked[1]["plan_id"],
        "winner_advantage_over_live_2a": r10(
            results[ranked[0]["plan_id"]]["after_liquidation_net_worth"]
            - results["P2A_LIVE_CUP_SF2U"]["after_liquidation_net_worth"]
        ),
        "winner_advantage_over_rent_3": r10(
            results[ranked[0]["plan_id"]]["after_liquidation_net_worth"]
            - results["P3_RENT_CUP_STAY_SF"]["after_liquidation_net_worth"]
        ),
    }


def compute_estate_headroom_matrix(inh_year: int = 2045) -> list[dict[str, Any]]:
    """Compute estate-level exclusion headroom and potential 40% federal estate tax
    across illustrative cash/financial inheritance tiers for single vs married (DSUE) grantors."""
    s_map = {r["year"]: r for r in simulate_property_series("R0_BASELINE")}
    row = s_map[inh_year]
    cup_fmv = row["cup_val"]
    excl_single = row["estate_excl_single"]
    excl_dsue = row["estate_excl_married_dsue"]

    out: list[dict[str, Any]] = []
    for cash_amt in [1_000_000, 3_000_000, 5_000_000, 10_000_000, 15_000_000, 20_000_000, 30_000_000]:
        gross_est = cup_fmv + cash_amt
        taxable_single = max(0, gross_est - excl_single)
        taxable_dsue = max(0, gross_est - excl_dsue)
        out.append(
            {
                "inh_year": inh_year,
                "cup_fmv": r10(cup_fmv),
                "cash_and_other_estate": r10(cash_amt),
                "illustrative_gross_estate": r10(gross_est),
                "excl_single": r10(excl_single),
                "headroom_single": r10(excl_single - gross_est),
                "est_fed_tax_single_40pct": r10(taxable_single * 0.40),
                "excl_married_dsue": r10(excl_dsue),
                "headroom_married_dsue": r10(excl_dsue - gross_est),
                "est_fed_tax_dsue_40pct": r10(taxable_dsue * 0.40),
                "ca_estate_inheritance_tax": 0,
            }
        )
    return out


if __name__ == "__main__":
    base_2045 = evaluate_plans(2045, 20, "R0_BASELINE")
    print("2045 Baseline Winner:", base_2045["winner_id"])
    for k, v in base_2045["plans"].items():
        print(
            f"  {k:22s} | Yr1 CupTax: ${v['yr1_cup_prop_tax']:>7,d} | "
            f"Yr1 OpCF: ${v['yr1_household_op_cf']:>8,d} | "
            f"PreLiq NW (2064): ${v['pre_liquidation_net_worth']:>11,d} | "
            f"AfterLiq NW (2064): ${v['after_liquidation_net_worth']:>11,d}"
        )
    print("\nRegime Stress Comparison (2045 transfer, 20-yr horizon to 2064):")
    for reg in [
        "R0_BASELINE",
        "R1_STAGFLATION",
        "R2_GFC_AT_TRANSFER",
        "R3_SEQ_CRASH_AFTER_SALE",
        "R4_BAY_AREA_SEISMIC_TECH",
        "R5_TAX_LAW_REVERSAL",
        "R6_EQUITY_LOST_DECADE_SV_BOOM",
    ]:
        ev = evaluate_plans(2045, 20, reg)
        p = ev["plans"]
        print(
            f"  {reg:25s} -> Winner: {ev['winner_id']:20s} | "
            f"P1A=${p['P1A_SELL_EQUITY']['after_liquidation_net_worth']:>11,d} | "
            f"P1B=${p['P1B_SELL_TREASURY']['after_liquidation_net_worth']:>11,d} | "
            f"P2B=${p['P2B_LIVE_CUP_SF3U']['after_liquidation_net_worth']:>11,d} | "
            f"P3=${p['P3_RENT_CUP_STAY_SF']['after_liquidation_net_worth']:>11,d}"
        )
