#!/usr/bin/env python3
"""Deterministic, strictly $10-rounded two-property household decision and
50-year multi-regime black-swan stress engine (2026–2076) for session s-c07ccf45.

All owner-supplied baseline inputs are stored ONLY in pre-rounded nearest-$10
form. No parcel numbers, street addresses, city/neighborhood names, ZIP codes,
or unrounded tax-roll figures exist anywhere in this module.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def r10(val: float) -> int:
    """Round any dollar figure to the nearest $10 (half-up for positives)."""
    if val >= 0:
        return int(math.floor((val + 5.0) / 10.0) * 10)
    return -int(math.floor((abs(val) + 5.0) / 10.0) * 10)


# ---------------------------------------------------------------------------
# Strictly pre-rounded ($10) household baseline inputs (full 2014-2026 & 2016-2025 series)
# ---------------------------------------------------------------------------
HIST_PROP_A = [
    {"year": 2014, "assessed": 440_310, "tax": 5_970, "boe_factor": 1.00454},
    {"year": 2015, "assessed": 449_100, "tax": 6_130, "boe_factor": 1.01998},
    {"year": 2016, "assessed": 455_950, "tax": 6_410, "boe_factor": 1.01525},
    {"year": 2017, "assessed": 465_070, "tax": 6_380, "boe_factor": 1.02000},
    {"year": 2018, "assessed": 474_370, "tax": 6_380, "boe_factor": 1.02000},
    {"year": 2019, "assessed": 483_850, "tax": 6_570, "boe_factor": 1.02000},
    {"year": 2020, "assessed": 493_530, "tax": 6_570, "boe_factor": 1.02000},
    {"year": 2021, "assessed": 498_640, "tax": 6_660, "boe_factor": 1.01036},
    {"year": 2022, "assessed": 508_610, "tax": 6_760, "boe_factor": 1.02000},
    {"year": 2023, "assessed": 518_790, "tax": 6_920, "boe_factor": 1.02000},
    {"year": 2024, "assessed": 529_160, "tax": 7_000, "boe_factor": 1.02000},
    {"year": 2025, "assessed": 539_740, "tax": 7_210, "boe_factor": 1.02000},
    {"year": 2026, "assessed": 550_540, "tax": None, "boe_factor": 1.02000},
]

HIST_PROP_B = [
    {"year": 2016, "assessed": 96_560, "tax": 1_680, "boe_factor": 1.01525},
    {"year": 2017, "assessed": 98_490, "tax": 1_740, "boe_factor": 1.02000},
    {"year": 2018, "assessed": 100_460, "tax": 2_060, "boe_factor": 1.02000},
    {"year": 2019, "assessed": 102_470, "tax": 2_130, "boe_factor": 1.02000},
    {"year": 2020, "assessed": 104_510, "tax": 2_200, "boe_factor": 1.02000},
    {"year": 2021, "assessed": 105_600, "tax": 2_070, "boe_factor": 1.01036},
    {"year": 2022, "assessed": 107_660, "tax": 2_110, "boe_factor": 1.02000},
    {"year": 2023, "assessed": 109_810, "tax": 2_180, "boe_factor": 1.02000},
    {"year": 2024, "assessed": 112_010, "tax": 2_320, "boe_factor": 1.02000},
    {"year": 2025, "assessed": 114_250, "tax": 2_440, "boe_factor": 1.02000},
]

BASE_INPUTS = {
    "start_year": 2026,
    "end_year": 2075,
    "cup_val_2026": 3_100_000,
    "sf_val_2026": 1_800_000,
    "cup_av_2025": 539_740,
    "cup_av_2026": 550_540,
    "cup_tax_2025": 7_210,
    "sf_av_2025": 114_250,
    "sf_tax_2025": 2_440,
    # Official ad valorem rates + implied 2025 fixed parcel/direct charges (rounded $10)
    "cup_ad_valorem_rate": 0.011488,   # County Assessor 2026 booklet typical TRA
    "sf_ad_valorem_rate": 0.01181622,  # BOS File 260971 FY2026-27 secured rate
    "hox_exemption": 7_000,            # CA BOE Pub. 800-6 Homeowners' Exemption
    "cup_fixed_charges_2025": 1_090,   # Reconciles ($539,740 - $7,000)*1.1488% + $1,090 = $7,210
    "sf_fixed_charges_2025": 1_170,    # Reconciles ($114,250 - $7,000)*1.1816% + $1,170 = $2,440
    # Operating costs in 2026 dollars (all divisible by $10)
    "cup_water_2026": 1_500,           # Midpoint of $100–$150/mo ($1,200–$1,800/yr)
    "cup_solar_credit_2026": -180,     # Midpoint of -$10 to -$20/mo (-$120 to -$240/yr) during NEM legacy
    "cup_post_nem_elec_2026": 1_440,   # Post-20-yr NEM sunset net grid + annualized inverter reserve ($120/mo in 2026$)
    "cup_nem_sunset_year": 2044,       # CPUC D.16-01-044 20-year legacy ends <= 2044 for pre-Apr 2023 NEM systems
    "cup_ins_model_2026": 4_800,       # High-value single-family rebuild assumption (official row blank; $1,500 owner guess tested)
    "cup_ins_owner_guess_2026": 1_500, # Owner's stated placeholder guess
    # Maintenance & capital reserves: dollar-based so the 3-unit coastal building costs more
    # per year than the single-family home (planner/engineering assumption; no statute sets a rate)
    "cup_maint_2026": 9_600,           # ~$800/mo single-family home upkeep + capex reserve
    "sf_maint_2026": 14_400,           # ~$1,200/mo for a 3-unit building (roof, plumbing, exterior, 3 kitchens/baths)
    "sf_rent_2units_2026": 85_800,     # $7,150/mo * 12 across 2 rented units
    "sf_unit3_mkt_rent_2026": 45_240,  # $3,770/mo (midpoint of HUD FY2026 2-BR $3,310 & 3-BR $4,230 SAFMR)
    "sf_water_2026": 4_380,            # Midpoint of $330–$400/mo ($3,960–$4,800/yr) across 3 units
    "sf_elec_2026": 600,               # Midpoint of $30–$70/mo ($360–$840/yr)
    "sf_ins_model_2026": 4_500,        # 3-unit habitational policy assumption (official row blank)
    # Baseline macro & tax parameters (anchored to CBO, IRS Rev. Proc. 2026-35, CA FTB, HUD)
    "cpi_base": 0.023,                 # CBO long-run CPI-U (~2.3%/yr)
    "cup_apprec_base": 0.035,          # 3.5%/yr nominal baseline (~1.2% real over CPI)
    "sf_apprec_base": 0.030,           # 3.0%/yr nominal baseline (~0.7% real over CPI)
    "ins_infl_base": 0.040,            # Insurance cost trend above general CPI
    "util_infl_base": 0.032,           # Regulated water/electric trend
    "equity_div_yield": 0.015,         # 1.5% qualified dividend yield
    "equity_price_growth": 0.055,      # 5.5% price growth -> 7.0% nominal total return (conservative vs 11.6% historical)
    "treasury_yield_base": 0.043,      # CBO 2026–2036 10-yr Treasury average (4.3%)
    "cup_gross_rent_yield_hud": 76_680 / 3_100_000,  # HUD FY2026 4-BR SAFMR ($6,390/mo = 2.4735%)
    "cup_gross_rent_yield_base": 0.028,              # 2.80% baseline SFH gross rent yield (~$7,230/mo in 2026$)
    # Transaction & tax rates
    "sale_broker_closing_pct": 0.0500, # 5.00% agent commissions, title, escrow, prep
    "scc_transfer_tax_pct": 0.0011,    # Verified County $0.55/$500 = 0.11% ($0 city conveyance tax)
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
        p["sf_water_g"] = 0.080 if yr in (2027, 2028) else p["util_g"]

        if regime_id == "R1_STAGFLATION":
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
            if yr == 2048:
                p["cup_g"] = -0.180
                p["sf_g"] = -0.140
                p["ins_g"] = 0.450
                p["capex_shock_cup"] = 160_000.0
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
            if yr >= 2038:
                p["step_up_repealed"] = 1.0
                p["estate_excl_cut"] = 1.0

        elif regime_id == "R6_EQUITY_LOST_DECADE_SV_BOOM":
            if 2045 <= yr <= 2059:
                p["eq_price"] = -0.160 if yr in (2045, 2046, 2053) else 0.042
                p["cup_g"] = 0.054
                p["sf_g"] = 0.038
                p["tsy"] = 0.046

        paths[yr] = p
    return paths


def simulate_property_series(regime_id: str = "R0_BASELINE") -> list[dict[str, Any]]:
    """Project year-by-year (2026–2075) standalone trajectories for both properties."""
    paths = build_regime_paths(regime_id)
    rows: list[dict[str, Any]] = []

    cup_val = float(BASE_INPUTS["cup_val_2026"])
    sf_val = float(BASE_INPUTS["sf_val_2026"])
    cup_fbyv = float(BASE_INPUTS["cup_av_2026"])
    sf_fbyv = float(BASE_INPUTS["sf_av_2025"]) * 1.02
    cup_fixed = float(BASE_INPUTS["cup_fixed_charges_2025"]) * 1.023
    sf_fixed = float(BASE_INPUTS["sf_fixed_charges_2025"]) * 1.023

    cup_water = float(BASE_INPUTS["cup_water_2026"])
    cup_solar = float(BASE_INPUTS["cup_solar_credit_2026"])
    cup_post_nem = float(BASE_INPUTS["cup_post_nem_elec_2026"])
    cup_ins = float(BASE_INPUTS["cup_ins_model_2026"])
    cup_ins_guess = float(BASE_INPUTS["cup_ins_owner_guess_2026"])
    cup_maint_yr = float(BASE_INPUTS["cup_maint_2026"])
    sf_maint_yr = float(BASE_INPUTS["sf_maint_2026"])

    sf_rent2 = float(BASE_INPUTS["sf_rent_2units_2026"])
    sf_unit3_rent = float(BASE_INPUTS["sf_unit3_mkt_rent_2026"])
    sf_water = float(BASE_INPUTS["sf_water_2026"])
    sf_elec = float(BASE_INPUTS["sf_elec_2026"])
    sf_ins = float(BASE_INPUTS["sf_ins_model_2026"])

    prop19_cap = float(BASE_INPUTS["prop19_cap_2025_2027"])
    estate_excl = float(BASE_INPUTS["estate_excl_2026"])

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
            cup_maint_yr *= 1.0 + p["cpi"] + 0.010
            sf_maint_yr *= 1.0 + p["cpi"] + 0.010
            sf_rc_inc = 0.016 if yr == 2027 else min(0.10, max(0.0, 0.60 * p["cpi"]))
            sf_rent2 *= 1.0 + sf_rc_inc
            sf_unit3_rent *= 1.0 + max(-0.10, p["rent_g"])

            prop13_factor = 1.0 + min(0.02, max(0.0, p["cpi"]))
            cup_fbyv *= prop13_factor
            sf_fbyv *= prop13_factor
            cup_fixed *= 1.0 + max(0.0, p["cpi"])
            sf_fixed *= 1.0 + max(0.0, p["cpi"])

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

        # Biennial Prop. 19 FHFA CA HPI adjustment on odd years >= 2027 (prior year's CA HPI change per BOE LTA 2025/009)
        if yr >= 2027 and yr % 2 == 1:
            prev_p = paths[yr - 1]
            prior_yr_ca_hpi = 0.5 * prev_p["cup_g"] + 0.5 * prev_p["sf_g"]
            prop19_cap *= max(0.95, 1.0 + prior_yr_ca_hpi)

        if yr == 2026:
            estate_excl = float(BASE_INPUTS["estate_excl_2026"])
        elif yr == 2027:
            estate_excl = float(BASE_INPUTS["estate_excl_2027"])
        else:
            estate_excl *= 1.0 + max(0.0, p["cpi"] - 0.002)

        eff_estate_excl = estate_excl * (0.35 if p["estate_excl_cut"] > 0 else 1.0)

        cup_elec = cup_solar if yr < BASE_INPUTS["cup_nem_sunset_year"] else cup_post_nem
        cup_maint = cup_maint_yr + p["capex_shock_cup"]
        sf_maint = sf_maint_yr

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
                "_f": {
                    "cup_val": cup_val,
                    "cup_fbyv": cup_fbyv,
                    "cup_fixed": cup_fixed,
                    "cup_water": cup_water,
                    "cup_elec": cup_elec,
                    "cup_ins": cup_ins,
                    "cup_ins_guess": cup_ins_guess,
                    "cup_maint": cup_maint,
                    "cup_maint_base": cup_maint_yr,
                    "sf_maint_base": sf_maint_yr,
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


def evaluate_plans(
    inh_year: int = 2045,
    horizon_years: int = 20,
    regime_id: str = "R0_BASELINE",
    use_owner_ins_guess: bool = False,
    cup_rent_yield_override: float | None = None,
    eq_return_shift: float = 0.0,
    cash_inheritance_buffer: float = 1_000_000.0,
) -> dict[str, Any]:
    """Compare all 6 integrated two-property household plans over
    [inh_year, inh_year + horizon_years - 1]:
      - P1A_SELL_EQUITY: Sell Property A at stepped-up basis, stay in Property B Unit 3, invest 100% in equities
      - P1B_SELL_TREASURY: Sell Property A at stepped-up basis, stay in Property B Unit 3, invest 100% in CA-tax-exempt U.S. Treasuries
      - P1C_SELL_BALANCED_75_25: Sell Property A at stepped-up basis, stay in Property B Unit 3, invest 75% Equities / 25% CA-tax-exempt U.S. Treasuries
      - P2A_LIVE_CUP_SF2U: Move into Property A (claim Prop. 19), keep Property B Unit 3 unrented (2 units rented)
      - P2B_LIVE_CUP_SF3U: Move into Property A (claim Prop. 19), rent out vacated Property B Unit 3 (3 units rented)
      - P3_RENT_CUP_STAY_SF: Rent out Property A (full Prop. 19 reassessment), stay in Property B Unit 3 (2 units rented)
    """
    paths = build_regime_paths(regime_id)
    series = {r["year"]: r["_f"] for r in simulate_property_series(regime_id)}
    end_yr = min(2075, inh_year + horizon_years - 1)
    actual_h = end_yr - inh_year + 1

    s0 = series[inh_year]
    v_cup_inh = s0["cup_val"]
    fbyv_cup_inh = s0["cup_fbyv"]
    p19_cap_inh = s0["prop19_cap"]

    gross_sale_costs = v_cup_inh * (
        BASE_INPUTS["sale_broker_closing_pct"] + BASE_INPUTS["scc_transfer_tax_pct"]
    )
    carryover_cg_tax = 0.0
    if paths[inh_year]["step_up_repealed"] > 0:
        taxable_gain = max(0.0, v_cup_inh - gross_sale_costs - BASE_INPUTS["cup_av_2026"])
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
        "P1C_SELL_BALANCED_75_25",
        "P2A_LIVE_CUP_SF2U",
        "P2B_LIVE_CUP_SF3U",
        "P3_RENT_CUP_STAY_SF",
    ]
    results: dict[str, Any] = {}

    for pk in plan_keys:
        sold_cup = pk in ("P1A_SELL_EQUITY", "P1B_SELL_TREASURY", "P1C_SELL_BALANCED_75_25")
        eq_weight = 0.0 if pk == "P1B_SELL_TREASURY" else (0.75 if pk == "P1C_SELL_BALANCED_75_25" else 1.0)
        live_in_cup = pk in ("P2A_LIVE_CUP_SF2U", "P2B_LIVE_CUP_SF3U")
        rent_sf_u3 = pk == "P2B_LIVE_CUP_SF3U"
        rent_cup = pk == "P3_RENT_CUP_STAY_SF"

        init_liq = cash_inheritance_buffer + (net_sale_proceeds if sold_cup else 0.0)
        eq_val = init_liq * eq_weight
        eq_basis = eq_val
        tsy_val = init_liq * (1.0 - eq_weight)

        if live_in_cup:
            cup_fbyv_post = fbyv_cup_inh + max(0.0, v_cup_inh - (fbyv_cup_inh + p19_cap_inh))
        elif rent_cup:
            cup_fbyv_post = v_cup_inh
        else:
            cup_fbyv_post = 0.0

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

            # --- 1. Property B (3-unit) cash flow ---
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

            # --- 2. Property A (inherited home) cash flow ---
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
                    cup_gross_rent = st["cup_val"] * cup_yield
                    cup_eff_rent = cup_gross_rent * (1.0 - 0.05 - 0.06)
                    depr_this_yr = cup_depr_annual if idx < 27 else (cup_depr_annual * 0.5 if idx == 27 else 0.0)
                    cum_cup_depr += depr_this_yr
                    taxable_cup = cup_eff_rent - cup_op_exp - depr_this_yr
                    if taxable_cup < 0:
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
            after_tax_div = max(0.0, eq_val) * p["eq_div"] * (1.0 - comb_div_rate)
            price_gain = eq_val * (p["eq_price"] + eq_return_shift)
            after_tax_tsy_rate = p["tsy"] * (1.0 - BASE_INPUTS["fed_ord_niit_rate"])
            tsy_interest_net = max(0.0, tsy_val) * after_tax_tsy_rate

            eq_val = eq_val + price_gain + after_tax_div + tot_op_cf * eq_weight
            eq_basis = eq_basis + after_tax_div + tot_op_cf * eq_weight
            tsy_val = tsy_val + tsy_interest_net + tot_op_cf * (1.0 - eq_weight)
            liq_val = eq_val + tsy_val

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

        end_st = series[end_yr]
        sf_end_val = end_st["sf_val"]
        cup_end_val = 0.0 if sold_cup else end_st["cup_val"]
        liq_val = eq_val + tsy_val
        pre_liq_nw = liq_val + sf_end_val + cup_end_val

        embedded_eq_tax = max(0.0, eq_val - eq_basis) * comb_ltcg_liq
        embedded_cup_exit_cost = 0.0
        if not sold_cup:
            sale_fric_end = cup_end_val * (
                BASE_INPUTS["sale_broker_closing_pct"] + BASE_INPUTS["scc_transfer_tax_pct"]
            )
            base_at_death = (
                BASE_INPUTS["cup_av_2026"] if paths[inh_year]["step_up_repealed"] > 0 else v_cup_inh
            )
            sec121_excl = 500_000.0 if live_in_cup and actual_h >= 2 else 0.0
            apprec_gain = max(0.0, (cup_end_val - sale_fric_end) - base_at_death - sec121_excl)
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
    pkg_root = Path(__file__).resolve().parent.parent
    base_2045 = evaluate_plans(2045, 20, "R0_BASELINE")
    summary = {
        "session": "s-c07ccf45",
        "verified_date": "2026-11-12",
        "anchor_2045": base_2045,
        "years_2040_2050": {
            str(yr): evaluate_plans(yr, 20, "R0_BASELINE") for yr in range(2040, 2051)
        },
        "regimes_2045": {
            reg: evaluate_plans(2045, 20, reg)
            for reg in [
                "R0_BASELINE",
                "R1_STAGFLATION",
                "R2_GFC_AT_TRANSFER",
                "R3_SEQ_CRASH_AFTER_SALE",
                "R4_BAY_AREA_SEISMIC_TECH",
                "R5_TAX_LAW_REVERSAL",
                "R6_EQUITY_LOST_DECADE_SV_BOOM",
            ]
        },
        "estate_headroom_2045": compute_estate_headroom_matrix(2045),
    }
    (pkg_root / "data" / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print("2045 Baseline Winner:", base_2045["winner_id"])
    for k, v in base_2045["plans"].items():
        print(
            f"  {k:24s} | Yr1 PropA Tax: ${v['yr1_cup_prop_tax']:>7,d} | "
            f"Yr1 OpCF: ${v['yr1_household_op_cf']:>8,d} | "
            f"AfterLiq NW (2064): ${v['after_liquidation_net_worth']:>11,d}"
        )
