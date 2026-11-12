#!/usr/bin/env python3
"""
Self-contained two-property inheritance & household wealth simulation engine (2026-2076).
Pure Python 3 standard library. Strict $10 input and output rounding. Zero external dependencies.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUT_PATH = DATA_DIR / "model_results.json"


def r10(val: float | int | None) -> int | None:
    """Round any dollar figure to the nearest $10 increment."""
    if val is None:
        return None
    return int(decimal_half_away_from_zero(val / 10.0) * 10)


def decimal_half_away_from_zero(x: float) -> int:
    if x >= 0:
        return int(math.floor(x + 0.5))
    return -int(math.floor(-x + 0.5))


# ---------------------------------------------------------------------------
# Verified Federal & California Income / Capital Gains Tax Calculators
# Anchored to official 2026/2027 IRS Rev. Proc. 2026-35 & FTB 2025/2026 tables,
# indexed by cumulative price level (except statutory unindexed thresholds:
# NIIT $200k/$250k IRC §1411, IRC §121 $250k/$500k, SALT $10k post-2029, and
# CA $1,000,000 1% Behavioral Health Services surcharge).
# ---------------------------------------------------------------------------

FED_ORD_SINGLE_2027 = [
    (12150.0, 0.10),
    (49425.0, 0.12),
    (105400.0, 0.22),
    (201275.0, 0.24),
    (255425.0, 0.32),
    (661375.0, 0.35),
    (float("inf"), 0.37),
]

FED_ORD_MFJ_2027 = [
    (24300.0, 0.10),
    (98850.0, 0.12),
    (210800.0, 0.22),
    (402550.0, 0.24),
    (510850.0, 0.32),
    (793650.0, 0.35),
    (float("inf"), 0.37),
]

FED_LTCG_SINGLE_2027 = [
    (50400.0, 0.00),
    (556150.0, 0.15),
    (float("inf"), 0.20),
]

FED_LTCG_MFJ_2027 = [
    (100800.0, 0.00),
    (625650.0, 0.15),
    (float("inf"), 0.20),
]

CA_ORD_SINGLE_2026 = [
    (11410.0, 0.01),
    (27050.0, 0.02),
    (42695.0, 0.04),
    (59270.0, 0.06),
    (74905.0, 0.08),
    (382625.0, 0.093),
    (459145.0, 0.103),
    (765240.0, 0.113),
    (float("inf"), 0.123),
]

CA_ORD_MFJ_2026 = [
    (22820.0, 0.01),
    (54100.0, 0.02),
    (85390.0, 0.04),
    (118540.0, 0.06),
    (149810.0, 0.08),
    (765250.0, 0.093),
    (918290.0, 0.103),
    (1530480.0, 0.113),
    (float("inf"), 0.123),
]


def progressive_tax(taxable: float, brackets: List[Tuple[float, float]], scale: float) -> float:
    if taxable <= 0.0:
        return 0.0
    tax = 0.0
    prev = 0.0
    for upper, rate in brackets:
        scaled_upper = upper * scale if math.isfinite(upper) else float("inf")
        if taxable <= prev:
            break
        span = min(taxable, scaled_upper) - prev
        if span > 0:
            tax += span * rate
        prev = scaled_upper
    return tax


def ltcg_stacked_tax(ordinary_ti: float, ltcg_amount: float, ltcg_brackets: List[Tuple[float, float]], scale: float) -> float:
    if ltcg_amount <= 0.0:
        return 0.0
    start = max(0.0, ordinary_ti)
    end = start + ltcg_amount
    tax = 0.0
    prev = 0.0
    for upper, rate in ltcg_brackets:
        scaled_upper = upper * scale if math.isfinite(upper) else float("inf")
        lo = max(start, prev)
        hi = min(end, scaled_upper)
        if hi > lo:
            tax += (hi - lo) * rate
        prev = scaled_upper
    return tax


def compute_household_income_tax(
    year: int,
    cpi_index: float,
    filing_status: str,
    wage_other_ord: float,
    net_rental_ord: float,
    treasury_interest: float,
    qual_dividends: float,
    ltcg_realized: float,
    unrecaptured_1250: float,
    personal_prop_tax_paid: float,
) -> Dict[str, float]:
    """
    Compute combined Federal + California income, capital gains, §1250 recapture,
    3.8% NIIT, and CA 1% Behavioral Health Services tax (> $1M unindexed).
    Direct U.S. Treasury interest is federally taxable (ordinary + NIIT) and 0% CA tax-exempt.
    """
    is_mfj = filing_status == "mfj"
    fed_std = (32200.0 if is_mfj else 16100.0) * cpi_index
    ca_std = (11750.0 if is_mfj else 5875.0) * cpi_index

    # Passive loss allowance (IRC §469(i) $25k unindexed phases out $100k-$150k MAGI)
    magi_pre = wage_other_ord + max(0.0, net_rental_ord) + treasury_interest + qual_dividends + ltcg_realized + unrecaptured_1250
    if net_rental_ord < 0.0:
        if magi_pre <= 100000.0:
            allowed_loss = min(-net_rental_ord, 25000.0)
        elif magi_pre < 150000.0:
            allowed_loss = min(-net_rental_ord, max(0.0, 25000.0 - 0.5 * (magi_pre - 100000.0)))
        else:
            allowed_loss = 0.0
        allowed_rental_ord = -allowed_loss
    else:
        allowed_rental_ord = net_rental_ord

    # California AGI & Taxable Income (Treasury interest excluded under 31 U.S.C. §3124 & FTB Pub 1001)
    ca_agi = wage_other_ord + allowed_rental_ord + qual_dividends + ltcg_realized + unrecaptured_1250
    ca_itemized = personal_prop_tax_paid  # CA allows property tax itemized deduction without $10k SALT cap
    ca_ded = max(ca_std, ca_itemized)
    ca_ti = max(0.0, ca_agi - ca_ded)
    ca_brackets = CA_ORD_MFJ_2026 if is_mfj else CA_ORD_SINGLE_2026
    ca_base_tax = progressive_tax(ca_ti, ca_brackets, cpi_index)
    ca_bh_surcharge = 0.01 * max(0.0, ca_ti - 1000000.0)  # Unindexed $1M threshold!
    ca_exemption_credit = (316.0 if is_mfj else 158.0) * cpi_index if ca_agi < (450000.0 if is_mfj else 225000.0) * cpi_index else 0.0
    ca_tax = max(0.0, ca_base_tax + ca_bh_surcharge - ca_exemption_credit)

    # Federal AGI & SALT cap (P.L. 119-21: $40,400 indexed 2026-2029 with phaseout >$505k to $10k floor; $10,000 unindexed 2030+)
    fed_ord_gross = wage_other_ord + allowed_rental_ord + treasury_interest
    fed_agi = fed_ord_gross + qual_dividends + ltcg_realized + unrecaptured_1250
    salt_paid = ca_tax + personal_prop_tax_paid
    if year <= 2029:
        cap_top = 40400.0 * (1.01 ** max(0, year - 2026))
        phase_start = 505000.0 * (1.01 ** max(0, year - 2026))
        reduced_cap = max(10000.0, cap_top - 0.30 * max(0.0, fed_agi - phase_start))
        salt_ded = min(salt_paid, reduced_cap)
    else:
        salt_ded = min(salt_paid, 10000.0)
    fed_ded = max(fed_std, salt_ded)

    # Deduct against ordinary income first, spillover against §1250 then LTCG/QDIV
    fed_ord_ti = max(0.0, fed_ord_gross - fed_ded)
    rem_ded = max(0.0, fed_ded - max(0.0, fed_ord_gross))
    sec1250_ti = max(0.0, unrecaptured_1250 - rem_ded)
    rem_ded2 = max(0.0, rem_ded - unrecaptured_1250)
    pref_ti = max(0.0, qual_dividends + ltcg_realized - rem_ded2)

    fed_brackets = FED_ORD_MFJ_2027 if is_mfj else FED_ORD_SINGLE_2027
    ltcg_brackets = FED_LTCG_MFJ_2027 if is_mfj else FED_LTCG_SINGLE_2027

    fed_ord_tax = progressive_tax(fed_ord_ti, fed_brackets, cpi_index)
    # IRC §1250 unrecaptured depreciation taxed at ordinary marginal rates capped at 25%
    if sec1250_ti > 0:
        ord_with_1250 = progressive_tax(fed_ord_ti + sec1250_ti, fed_brackets, cpi_index) - fed_ord_tax
        fed_1250_tax = min(ord_with_1250, 0.25 * sec1250_ti)
    else:
        fed_1250_tax = 0.0

    fed_ltcg_tax = ltcg_stacked_tax(fed_ord_ti + sec1250_ti, pref_ti, ltcg_brackets, cpi_index)

    # 3.8% NIIT (IRC §1411 — unindexed $200,000 single / $250,000 MFJ)
    niit_thresh = 250000.0 if is_mfj else 200000.0
    nii = max(0.0, allowed_rental_ord) + treasury_interest + qual_dividends + ltcg_realized + unrecaptured_1250
    niit = 0.038 * max(0.0, min(nii, fed_agi - niit_thresh))

    fed_tax = fed_ord_tax + fed_1250_tax + fed_ltcg_tax + niit
    return {
        "fed_tax": fed_tax,
        "ca_tax": ca_tax,
        "niit": niit,
        "total_tax": fed_tax + ca_tax,
    }


def marginal_portfolio_tax(
    year: int,
    cpi_index: float,
    filing_status: str,
    base_wage_ord: float,
    net_rental_ord: float,
    treasury_interest: float,
    qual_dividends: float,
    ltcg_realized: float,
    unrecaptured_1250: float,
    personal_prop_tax_paid: float,
) -> Dict[str, float]:
    """Incremental household tax above the wage-only baseline."""
    t_with = compute_household_income_tax(
        year, cpi_index, filing_status, base_wage_ord,
        net_rental_ord, treasury_interest, qual_dividends,
        ltcg_realized, unrecaptured_1250, personal_prop_tax_paid,
    )
    t_wage_only = compute_household_income_tax(
        year, cpi_index, filing_status, base_wage_ord,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    )
    return {
        "fed_incremental": t_with["fed_tax"] - t_wage_only["fed_tax"],
        "ca_incremental": t_with["ca_tax"] - t_wage_only["ca_tax"],
        "niit": t_with["niit"],
        "total_incremental": t_with["total_tax"] - t_wage_only["total_tax"],
    }


# ---------------------------------------------------------------------------
# Historical Assessment & Property Tax Decomposition Audit (2014-2026)
# ---------------------------------------------------------------------------

def audit_historical_rolls(inputs: dict, macro: dict) -> dict:
    boe_map = {row["year"]: row["boe_prop13_factor"] for row in macro["annual_1976_2025"]}
    boe_map[2026] = macro["boe_2026"]["prop13_factor"]

    prop_a_hist = sorted(inputs["property_a"]["tax_and_assessment_history_rounded_10"], key=lambda r: r["year"])
    prop_a_audit = []
    for idx, row in enumerate(prop_a_hist):
        yr = row["year"]
        av = row["assessed_value"]
        tx = row["property_tax"]
        prev_av = prop_a_hist[idx - 1]["assessed_value"] if idx > 0 else None
        boe_fac = boe_map.get(yr)
        expected_av = r10(prev_av * boe_fac) if (prev_av and boe_fac) else None
        diff_av = (av - expected_av) if (av is not None and expected_av is not None) else None
        eff_rate_pct = round(tx / av * 100.0, 3) if (tx is not None and av) else None
        prop_a_audit.append({
            "year": yr,
            "assessed_value_r10": av,
            "property_tax_r10": tx,
            "boe_factor": boe_fac,
            "expected_fbyv_r10": expected_av,
            "rounding_residual_r10": diff_av,
            "effective_tax_rate_pct": eff_rate_pct,
        })

    prop_b_hist = sorted(inputs["property_b"]["tax_and_assessment_history_rounded_10"], key=lambda r: r["year"])
    prop_b_audit = []
    for idx, row in enumerate(prop_b_hist):
        yr = row["year"]
        av = row["assessed_value"]
        tx = row["property_tax"]
        prev_av = prop_b_hist[idx - 1]["assessed_value"] if idx > 0 else None
        boe_fac = boe_map.get(yr)
        # Net taxable = (prev_net + 7000 HOX) * boe_fac - 7000 HOX
        expected_av_with_hox = r10((prev_av + 7000.0) * boe_fac - 7000.0) if (prev_av and boe_fac and av is not None) else None
        diff_av = (av - expected_av_with_hox) if (av is not None and expected_av_with_hox is not None) else None
        eff_rate_pct = round(tx / av * 100.0, 3) if (tx is not None and av) else None
        prop_b_audit.append({
            "year": yr,
            "assessed_value_r10": av,
            "property_tax_r10": tx,
            "boe_factor": boe_fac,
            "expected_net_av_with_7k_hox_r10": expected_av_with_hox,
            "rounding_residual_r10": diff_av,
            "effective_tax_rate_pct": eff_rate_pct,
        })

    return {"property_a": prop_a_audit, "property_b": prop_b_audit}


# ---------------------------------------------------------------------------
# Core 50-Year Path Simulator (2026-2076)
# Supports both deterministic baseline/stress paths and historical/Monte Carlo paths
# ---------------------------------------------------------------------------

DEFAULT_PARAMS = {
    "cpi": 0.024,              # CBO 2.0% PCE ~= 2.4% CPI-U
    "hpi_a": 0.038,            # 1.37% real appreciation on $3.1M high-value SFR
    "hpi_b": 0.034,            # 0.98% real appreciation on $1.8M 3-unit rent-stabilized building
    "hpi_ca": 0.036,           # CA statewide HPI for biennial Prop. 19 cap adjustment
    "rent_mkt": 0.032,         # Unregulated single-family rent growth
    "eq_price": 0.055,         # S&P 500 nominal price appreciation (total 7.0% w/ 1.5% div)
    "eq_div": 0.015,           # S&P 500 qualified dividend yield
    "tbill_yield": 0.038,      # 10-yr / Treasury ladder yield (1.4% real; 0% CA tax!)
    "ins_growth": 0.034,       # CPI + 1.0% CA insurance climate/reinsurance wedge
    "water_growth_long": 0.033,# Post-2028 water/sewer infrastructure escalation
    "elec_growth": 0.032,      # Retail utility tariff growth
    "filing_status": "single",
    "base_wage_2026": 150000.0,
    "ins_a_2026": 1500.0,      # Owner $1,500 baseline (sensitivity tests $4,200)
    "ins_b_2026": 1500.0,      # Owner $1,500 baseline (sensitivity tests $6,500)
    "maint_a_rate": 0.0050,    # 0.50% of value ($15,500 in 2026)
    "maint_b_rate": 0.0085,    # 0.85% of value ($15,300 in 2026)
    "rent_a_2026_mo": 5800.0,  # HUD FY2027 4-BR SAFMR ($5,800/mo); sensitivity $7,200/mo
    "vacancy_a": 0.05,         # 5% turnover/vacancy allowance on Property A rental
    "mgmt_fee_a": 0.06,        # 6% leasing/management allowance when renting Property A
    "vacancy_b": 0.03,         # 3% vacancy allowance on rent-controlled Property B units
    "sell_cost_pct": 0.050,    # 5.0% brokerage + closing + prep friction (+ statutory transfer tax)
    "county_transfer_tax_a": 0.0011, # Verified $0.55 per $500 = 0.11% (0% city conveyance tax)
    "prop19_repealed": False,  # Legislative shock flag (if True, live-in also reassesses 100% or 0%)
    "step_up_repealed": False, # Federal IRC §1014 repeal shock flag
    "nem_sunset_year": 2046,   # CPUC D.14-03-041 20-year legacy solar sunset
}


def build_constant_macro_path(params: dict, start_year: int = 2026, end_year: int = 2076) -> List[dict]:
    path = []
    for yr in range(start_year, end_year + 1):
        path.append({
            "year": yr,
            "cpi": 0.0 if yr == start_year else params["cpi"],
            "hpi_a": 0.0 if yr == start_year else params["hpi_a"],
            "hpi_b": 0.0 if yr == start_year else params["hpi_b"],
            "hpi_ca": 0.0 if yr == start_year else params["hpi_ca"],
            "rent_mkt": 0.0 if yr == start_year else params["rent_mkt"],
            "eq_price": params["eq_price"],
            "eq_div": params["eq_div"],
            "tbill_yield": params["tbill_yield"],
            "ins_growth": 0.0 if yr == start_year else params["ins_growth"],
            "water_a_growth": 0.0 if yr == start_year else (0.0449 if yr == 2027 else params["water_growth_long"]),
            "water_b_growth": 0.0 if yr == start_year else (0.126 if yr == 2027 else (0.125 if yr == 2028 else params["water_growth_long"])),
            "elec_growth": 0.0 if yr == start_year else params["elec_growth"],
            "prop13_fac": 1.0 if yr == start_year else min(1.02, 1.0 + max(-0.02, params["cpi"])),
        })
    return path


def sf_transfer_tax_rate(sale_value: float) -> float:
    """Official City & County of San Francisco Art. 12C Real Property Transfer Tax schedule."""
    if sale_value < 250000:
        return 0.0050
    if sale_value < 1000000:
        return 0.0068
    if sale_value < 5000000:
        return 0.0075
    if sale_value < 10000000:
        return 0.0225
    if sale_value < 25000000:
        return 0.0550
    return 0.0600


def simulate_property_ledgers(
    inputs: dict,
    macro_path: List[dict],
    params: dict,
    transfer_year: int,
) -> List[dict]:
    """
    Generate year-by-year (2026-2076) property values, Prop. 13/19 assessments,
    decomposed property taxes, insurance, water, solar/electricity, and upkeep
    for Property A and Property B.
    """
    val_a = float(inputs["property_a"]["estimated_market_value_2026"])
    val_b = float(inputs["property_b"]["estimated_market_value_2026"])

    # Property A 2026 FBYV = $550,540; 2025 tax = $7,210 on $539,740 -> ad valorem ~1.180% + $841 parcel
    fbyv_a_trust = 550540.0
    ad_valorem_rate_a = 0.01180
    parcel_a = 855.0

    # Property B 2025 net AV = $114,250 (+ $7,000 HOX = $121,250 gross FBYV); 2026 gross FBYV = $121,250 * 1.02 = $123,675
    fbyv_b_gross = 121250.0 * 1.02
    ad_valorem_rate_b = 0.0118162182  # Exact FY2026-27 SF Treasurer rate
    parcel_b = 1110.0

    ins_a = float(params["ins_a_2026"])
    ins_b = float(params["ins_b_2026"])
    water_a = float(inputs["property_a"]["water_annual_midpoint_2026"])
    water_b = float(inputs["property_b"]["water_annual_midpoint_2026"])
    elec_b = float(inputs["property_b"]["electricity_annual_midpoint_2026"])

    rent_b_2u = float(inputs["property_b"]["current_annual_rent_2_units_2026"])
    rent_b_u3_mkt = float(inputs["property_b"]["unit3_market_rent_monthly_2026_benchmark"]) * 12.0
    rent_a_mkt = float(params["rent_a_2026_mo"]) * 12.0

    cpi_cum = 1.0
    ca_hpi_cum = 1.0
    ca_hpi_last_biennial = 1.0
    prop19_cap = 1044586.0  # Official BOE LTA 2025/009 cap through Feb 15, 2027

    av_a_live = None
    av_a_rent = None

    rows = []
    for step in macro_path:
        yr = step["year"]
        if yr > 2026:
            cpi_cum *= (1.0 + step["cpi"])
            val_a *= (1.0 + step["hpi_a"])
            val_b *= (1.0 + step["hpi_b"])
            ca_hpi_cum *= (1.0 + step["hpi_ca"])
            # Biennial Prop 19 adjustment on odd years (2027, 2029, ...) per RTC §63.2(e)
            if yr % 2 == 1:
                prop19_cap *= (ca_hpi_cum / ca_hpi_last_biennial)
                ca_hpi_last_biennial = ca_hpi_cum

            fbyv_a_trust = fbyv_a_trust * step["prop13_fac"]
            fbyv_b_gross = fbyv_b_gross * step["prop13_fac"]
            parcel_a *= (1.0 + 0.5 * max(0.0, step["cpi"]))
            parcel_b *= (1.0 + 0.5 * max(0.0, step["cpi"]))

            ins_a *= (1.0 + step["ins_growth"])
            ins_b *= (1.0 + step["ins_growth"])
            water_a *= (1.0 + step["water_a_growth"])
            water_b *= (1.0 + step["water_b_growth"])
            elec_b *= (1.0 + step["elec_growth"])
            rent_a_mkt *= (1.0 + step["rent_mkt"])
            rent_b_u3_mkt *= (1.0 + step["rent_mkt"])
            # SF Rent Board annual allowable increase = 60% of regional CPI (capped 0%-7% typical)
            sf_allowable = max(0.0, min(0.07, 0.60 * step["cpi"]))
            rent_b_2u *= (1.0 + sf_allowable)

        # Prop 8 temporary reduction check if market value < FBYV
        eff_trust_av_a = min(val_a, fbyv_a_trust)

        if yr < transfer_year:
            cur_av_a_live = eff_trust_av_a
            cur_av_a_rent = eff_trust_av_a
        elif yr == transfer_year:
            if params["prop19_repealed"]:
                # Stress scenario: full reassessment even if occupied
                av_a_live = val_a
            else:
                excluded_limit = fbyv_a_trust + prop19_cap
                excess_fmv = max(0.0, val_a - excluded_limit)
                av_a_live = fbyv_a_trust + excess_fmv
            av_a_rent = val_a
            cur_av_a_live = min(val_a, max(0.0, av_a_live - 7000.0))  # $7,000 HOX claimed on Property A!
            cur_av_a_rent = min(val_a, av_a_rent)
        else:
            av_a_live *= step["prop13_fac"]
            av_a_rent *= step["prop13_fac"]
            cur_av_a_live = min(val_a, max(0.0, av_a_live - 7000.0))
            cur_av_a_rent = min(val_a, av_a_rent)

        tax_a_trust = eff_trust_av_a * ad_valorem_rate_a + parcel_a
        tax_a_live = cur_av_a_live * ad_valorem_rate_a + parcel_a
        tax_a_rent = cur_av_a_rent * ad_valorem_rate_a + parcel_a

        # Property B: if owner lives in Unit 3, $7,000 HOX applies; if owner moves to Property A, HOX shifts to Property A
        av_b_owner_occ = min(val_b, max(0.0, fbyv_b_gross - 7000.0))
        av_b_non_occ = min(val_b, fbyv_b_gross)
        tax_b_owner_occ = av_b_owner_occ * ad_valorem_rate_b + parcel_b
        tax_b_non_occ = av_b_non_occ * ad_valorem_rate_b + parcel_b

        # Property A Solar & Electricity: CPUC 20-year NEM legacy period through nem_sunset_year (2046)
        if yr <= params["nem_sunset_year"]:
            # Slight panel degradation reduces surplus credit slowly
            degrad = max(0.75, 1.0 - 0.005 * (yr - 2026))
            elec_a = -180.0 * cpi_cum * degrad
        else:
            # Post-NEM 20-yr grandfathering: Net Billing Tariff (D.22-12-056) + annualized inverter reserve ($300/yr 2026$)
            elec_a = (960.0 + 300.0) * cpi_cum

        maint_a = val_a * params["maint_a_rate"]
        maint_b = val_b * params["maint_b_rate"]

        rows.append({
            "year": yr,
            "cpi_cum": cpi_cum,
            "prop19_cap": prop19_cap,
            "val_a": val_a,
            "val_b": val_b,
            "fbyv_a_trust": eff_trust_av_a,
            "av_a_live": cur_av_a_live,
            "av_a_rent": cur_av_a_rent,
            "tax_a_trust": tax_a_trust,
            "tax_a_live": tax_a_live,
            "tax_a_rent": tax_a_rent,
            "ins_a": ins_a,
            "water_a": water_a,
            "elec_a": elec_a,
            "maint_a": maint_a,
            "total_opex_a_live": tax_a_live + ins_a + water_a + elec_a + maint_a,
            "total_opex_a_rent": tax_a_rent + ins_a + water_a + elec_a + maint_a,
            "av_b_owner_occ": av_b_owner_occ,
            "av_b_non_occ": av_b_non_occ,
            "tax_b_owner_occ": tax_b_owner_occ,
            "tax_b_non_occ": tax_b_non_occ,
            "ins_b": ins_b,
            "water_b": water_b,
            "elec_b": elec_b,
            "maint_b": maint_b,
            "total_opex_b_owner_occ": tax_b_owner_occ + ins_b + water_b + elec_b + maint_b,
            "total_opex_b_non_occ": tax_b_non_occ + ins_b + water_b + elec_b + maint_b,
            "rent_a_gross": rent_a_mkt,
            "rent_b_2u_gross": rent_b_2u,
            "rent_b_u3_mkt_gross": rent_b_u3_mkt,
        })
    return rows


# ---------------------------------------------------------------------------
# Strategy Wealth & Cash-Flow Engine (Post-Inheritance Window)
# Compares S1 (Sell -> Stocks), S2 (Sell -> 60/40), S3 (Sell -> Treasuries),
# R (Rent Property A), L1 (Live in Property A, Unit 3 unrented),
# and L2 (Live in Property A + Rent Property B Unit 3).
# ---------------------------------------------------------------------------

def evaluate_strategies(
    ledger: List[dict],
    macro_path: List[dict],
    params: dict,
    transfer_year: int,
    horizon_years: int = 20,
    use_irc280a_pro_rata: bool = True,
) -> dict:
    by_yr = {r["year"]: r for r in ledger}
    m_by_yr = {m["year"]: m for m in macro_path}
    end_year = min(2076, transfer_year + horizon_years)
    actual_h = end_year - transfer_year

    row_t0 = by_yr[transfer_year]
    fmv_a_t0 = row_t0["val_a"]

    # Immediate sale proceeds of Property A at transfer_year
    gross_sale_t0 = fmv_a_t0 * (1.0 - params["sell_cost_pct"] - params["county_transfer_tax_a"])
    if params["step_up_repealed"]:
        # Stress test: carryover historical basis (~$550k) taxed at transfer_year
        carry_gain = max(0.0, gross_sale_t0 - 550540.0)
        sale_tax_t0 = marginal_portfolio_tax(
            transfer_year, row_t0["cpi_cum"], params["filing_status"],
            params["base_wage_2026"] * row_t0["cpi_cum"],
            0.0, 0.0, 0.0, carry_gain, 0.0, 0.0,
        )["total_incremental"]
    else:
        # IRC §1014 + CA RTC §18031 step-up to FMV at date of death -> $0 taxable gain (selling costs create slight capital loss)
        sale_tax_t0 = 0.0
    net_sale_proceeds_t0 = gross_sale_t0 - sale_tax_t0

    # Portfolio trackers for each plan:
    # Each plan tracks: equity_mv, equity_basis, treasury_mv (cost=mv)
    plans = {
        "sell_stocks": {"eq_mv": net_sale_proceeds_t0, "eq_basis": net_sale_proceeds_t0, "tb_mv": 0.0, "cum_cf_real": 0.0},
        "sell_60_40": {
            "eq_mv": 0.60 * net_sale_proceeds_t0,
            "eq_basis": 0.60 * net_sale_proceeds_t0,
            "tb_mv": 0.40 * net_sale_proceeds_t0,
            "cum_cf_real": 0.0,
        },
        "sell_treasuries": {"eq_mv": 0.0, "eq_basis": 0.0, "tb_mv": net_sale_proceeds_t0, "cum_cf_real": 0.0},
        "rent_a": {"eq_mv": 0.0, "eq_basis": 0.0, "tb_mv": 0.0, "cum_cf_real": 0.0, "accum_dep_a": 0.0},
        "live_a_keep_u3": {"eq_mv": 0.0, "eq_basis": 0.0, "tb_mv": 0.0, "cum_cf_real": 0.0},
        "live_a_rent_u3": {"eq_mv": 0.0, "eq_basis": 0.0, "tb_mv": 0.0, "cum_cf_real": 0.0},
    }

    # Annual depreciation on Property A if rented (IRS Pub. 527: 27.5-yr straight line on building share of stepped-up FMV)
    annual_dep_a = (fmv_a_t0 * 0.35) / 27.5
    u3_rent_current = row_t0["rent_b_u3_mkt_gross"]

    yearly_trace = []

    for yr in range(transfer_year, end_year):
        r = by_yr[yr]
        m = m_by_yr[yr + 1]
        cpi = r["cpi_cum"]
        wage_ord = params["base_wage_2026"] * cpi

        # Property B cash flows & Schedule E taxable rental income:
        # Case 1: Owner lives in Unit 3 of Property B (Plans S1, S2, S3, R)
        gross_b_2u = r["rent_b_2u_gross"] * (1.0 - params["vacancy_b"])
        opex_b_occ = r["total_opex_b_owner_occ"]
        cf_b_occ = gross_b_2u - opex_b_occ  # Total cash flow on Property B (including personal Unit 3 share)
        if use_irc280a_pro_rata:
            # IRC §280A / IRS Pub. 527: 2 of 3 units rented -> 2/3 of shared building expenses deductible on Schedule E;
            # 1/3 of property tax goes to personal Schedule A!
            sched_e_b_occ = gross_b_2u - (2.0 / 3.0) * opex_b_occ
            pers_ptax_b_occ = (1.0 / 3.0) * r["tax_b_owner_occ"]
        else:
            sched_e_b_occ = cf_b_occ
            pers_ptax_b_occ = 0.0

        # Case 2: Owner lives in Property A, keeps Property B Unit 3 unrented (Plan L1)
        opex_b_non_occ = r["total_opex_b_non_occ"]
        cf_b_unrented_u3 = gross_b_2u - opex_b_non_occ
        sched_e_b_unrented_u3 = gross_b_2u - (2.0 / 3.0) * opex_b_non_occ

        # Case 3: Owner lives in Property A AND leases Property B Unit 3 at market rent (Plan L2)
        if yr > transfer_year:
            sf_cap = max(0.0, min(0.07, 0.60 * m_by_yr[yr]["cpi"]))
            u3_rent_current *= (1.0 + sf_cap)
        gross_b_3u = (r["rent_b_2u_gross"] + u3_rent_current) * (1.0 - params["vacancy_b"])
        cf_b_3u = gross_b_3u - opex_b_non_occ
        sched_e_b_3u = cf_b_3u  # All 3 units rented -> 100% Schedule E!

        # --- Update each plan over [yr, yr+1) ---
        for pkey, pstate in plans.items():
            eq_mv = pstate["eq_mv"]
            eq_basis = pstate["eq_basis"]
            tb_mv = pstate["tb_mv"]

            div_inc = max(0.0, eq_mv) * m["eq_div"]
            tb_inc = max(0.0, tb_mv) * m["tbill_yield"]
            # If liquid balance went negative (cumulative cash-flow deficit funded from liquid savings opportunity cost)
            borrow_drag = min(0.0, tb_mv) * m["tbill_yield"]

            if pkey in ("sell_stocks", "sell_60_40", "sell_treasuries"):
                net_rent_ord = sched_e_b_occ
                pers_ptax = pers_ptax_b_occ
                prop_cash_net = cf_b_occ
            elif pkey == "rent_a":
                eff_rent_a = r["rent_a_gross"] * (1.0 - params["vacancy_a"] - params["mgmt_fee_a"])
                cf_a_rent = eff_rent_a - r["total_opex_a_rent"]
                dep_this_yr = annual_dep_a if (yr - transfer_year) < 27 else (annual_dep_a * 0.5 if (yr - transfer_year) == 27 else 0.0)
                pstate["accum_dep_a"] += dep_this_yr
                sched_e_a = cf_a_rent - dep_this_yr
                net_rent_ord = sched_e_b_occ + sched_e_a
                pers_ptax = pers_ptax_b_occ
                prop_cash_net = cf_b_occ + cf_a_rent
            elif pkey == "live_a_keep_u3":
                net_rent_ord = sched_e_b_unrented_u3
                pers_ptax = r["tax_a_live"]
                prop_cash_net = cf_b_unrented_u3 - r["total_opex_a_live"]
            elif pkey == "live_a_rent_u3":
                net_rent_ord = sched_e_b_3u
                pers_ptax = r["tax_a_live"]
                prop_cash_net = cf_b_3u - r["total_opex_a_live"]

            tax_res = marginal_portfolio_tax(
                yr, cpi, params["filing_status"], wage_ord,
                net_rent_ord, max(0.0, tb_inc), div_inc, 0.0, 0.0, pers_ptax,
            )
            after_tax_cash = prop_cash_net + div_inc + tb_inc + borrow_drag - tax_res["total_incremental"]
            pstate["cum_cf_real"] += after_tax_cash / cpi

            # Price appreciation on existing equities, then reinvest net cash flow per plan allocation
            eq_mv_grown = eq_mv * (1.0 + m["eq_price"])
            if pkey == "sell_stocks":
                # Reinvest net cash flow into equities if positive; if negative, sell small slice or draw cash
                if after_tax_cash >= 0:
                    pstate["eq_mv"] = eq_mv_grown + after_tax_cash
                    pstate["eq_basis"] = eq_basis + after_tax_cash
                else:
                    pstate["eq_mv"] = eq_mv_grown
                    pstate["tb_mv"] = tb_mv + after_tax_cash
            elif pkey == "sell_60_40":
                tot_fin = eq_mv_grown + tb_mv + after_tax_cash
                if tot_fin > 0:
                    # Low-turnover cash-flow rebalancing without forced gain realization
                    pstate["eq_mv"] = eq_mv_grown + 0.60 * after_tax_cash
                    pstate["eq_basis"] = eq_basis + max(0.0, 0.60 * after_tax_cash)
                    pstate["tb_mv"] = tb_mv + 0.40 * after_tax_cash
                else:
                    pstate["tb_mv"] = tot_fin
            elif pkey == "sell_treasuries":
                pstate["tb_mv"] = tb_mv + after_tax_cash
            else:
                # For Rent A / Live A plans, reinvest positive surplus cash flows in the same equity index (fair opportunity comparison!)
                if after_tax_cash >= 0:
                    pstate["eq_mv"] = eq_mv_grown + after_tax_cash
                    pstate["eq_basis"] = eq_basis + after_tax_cash
                else:
                    pstate["eq_mv"] = eq_mv_grown
                    pstate["tb_mv"] = tb_mv + after_tax_cash

        if yr in (transfer_year, transfer_year + 5, transfer_year + 10, transfer_year + 15, end_year - 1):
            yearly_trace.append({
                "year": yr,
                "sell_stocks_fin_nominal": plans["sell_stocks"]["eq_mv"] + plans["sell_stocks"]["tb_mv"],
                "rent_a_prop_plus_fin_nominal": by_yr[yr]["val_a"] + plans["rent_a"]["eq_mv"] + plans["rent_a"]["tb_mv"],
                "live_a_prop_plus_fin_nominal": by_yr[yr]["val_a"] + plans["live_a_keep_u3"]["eq_mv"] + plans["live_a_keep_u3"]["tb_mv"],
            })

    # --- Terminal After-Tax Net Worth Calculation at end_year (Liquidation Comparable, Net of Embedded Taxes!) ---
    r_end = by_yr[end_year]
    cpi_end = r_end["cpi_cum"]
    wage_end = params["base_wage_2026"] * cpi_end
    val_b_end = r_end["val_b"]  # Held identically in all 6 plans (reported both ex-B and including B!)

    summary_plans = {}
    for pkey, pstate in plans.items():
        eq_gain = max(0.0, pstate["eq_mv"] - pstate["eq_basis"])
        prop_a_net_sale = 0.0
        prop_a_ltcg = 0.0
        prop_a_1250 = 0.0

        if pkey in ("rent_a", "live_a_keep_u3", "live_a_rent_u3"):
            gross_sale_end = r_end["val_a"] * (1.0 - params["sell_cost_pct"] - params["county_transfer_tax_a"])
            prop_a_net_sale = gross_sale_end
            base_cost = 550540.0 if params["step_up_repealed"] else fmv_a_t0
            if pkey == "rent_a":
                adj_basis = base_cost - pstate["accum_dep_a"]
                total_gain = max(0.0, gross_sale_end - adj_basis)
                prop_a_1250 = min(total_gain, pstate["accum_dep_a"])
                prop_a_ltcg = max(0.0, total_gain - prop_a_1250)
            else:
                # IRC §121 principal residence exclusion ($250k single / $500k MFJ, unindexed)
                sec121 = 500000.0 if params["filing_status"] == "mfj" else 250000.0
                prop_a_ltcg = max(0.0, gross_sale_end - base_cost - sec121)

        liq_tax = marginal_portfolio_tax(
            end_year, cpi_end, params["filing_status"], wage_end,
            0.0, 0.0, 0.0, eq_gain + prop_a_ltcg, prop_a_1250, 0.0,
        )["total_incremental"]

        net_wealth_ex_b_nom = pstate["eq_mv"] + pstate["tb_mv"] + prop_a_net_sale - liq_tax
        net_wealth_ex_b_real = net_wealth_ex_b_nom / cpi_end
        # Property B net equity if held (value; or net of SF transfer tax if ever valued)
        net_wealth_incl_b_real = (net_wealth_ex_b_nom + val_b_end) / cpi_end

        summary_plans[pkey] = {
            "terminal_wealth_ex_b_nominal_r10": r10(net_wealth_ex_b_nom),
            "terminal_wealth_ex_b_real_2026_r10": r10(net_wealth_ex_b_real),
            "terminal_wealth_incl_b_real_2026_r10": r10(net_wealth_incl_b_real),
            "liquidation_tax_nominal_r10": r10(liq_tax),
            "cum_annual_after_tax_cf_real_2026_r10": r10(pstate["cum_cf_real"]),
            "raw_ex_b_real": net_wealth_ex_b_real,
        }

    return {
        "transfer_year": transfer_year,
        "end_year": end_year,
        "horizon_years": actual_h,
        "fmv_a_at_transfer_nominal_r10": r10(fmv_a_t0),
        "fmv_a_at_transfer_real_2026_r10": r10(fmv_a_t0 / row_t0["cpi_cum"]),
        "net_sale_proceeds_t0_nominal_r10": r10(net_sale_proceeds_t0),
        "net_sale_proceeds_t0_real_2026_r10": r10(net_sale_proceeds_t0 / row_t0["cpi_cum"]),
        "prop19_year1_tax_live_nominal_r10": r10(row_t0["tax_a_live"]),
        "prop19_year1_tax_rent_nominal_r10": r10(row_t0["tax_a_rent"]),
        "prop19_year1_tax_trust_prior_nominal_r10": r10(by_yr[transfer_year - 1]["tax_a_trust"]) if transfer_year > 2026 else r10(row_t0["tax_a_trust"]),
        "plans": summary_plans,
        "yearly_trace": yearly_trace,
    }


def find_breakevens(inputs: dict) -> dict:
    """Solve exact break-even nominal equity total return and break-even Property A monthly rent (2045 transfer, 20-yr horizon)."""
    # 1. Break-even equity total return where Sell -> Stocks == Rent Property A
    lo, hi = 0.01, 0.08
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        p = dict(DEFAULT_PARAMS)
        p["eq_div"] = min(0.015, 0.25 * mid)
        p["eq_price"] = mid - p["eq_div"]
        mp = build_constant_macro_path(p)
        led = simulate_property_ledgers(inputs, mp, p, 2045)
        res = evaluate_strategies(led, mp, p, 2045, 20)
        diff = res["plans"]["sell_stocks"]["raw_ex_b_real"] - res["plans"]["rent_a"]["raw_ex_b_real"]
        if diff > 0:
            hi = mid
        else:
            lo = mid
    be_eq_vs_rent = round(0.5 * (lo + hi) * 100.0, 2)

    # 2. Break-even Property A monthly rent (2026$) where Rent Property A == Sell -> Stocks (at 7.0% baseline equity return)
    lo_r, hi_r = 5000.0, 30000.0
    for _ in range(40):
        mid_r = 0.5 * (lo_r + hi_r)
        p = dict(DEFAULT_PARAMS)
        p["rent_a_2026_mo"] = mid_r
        mp = build_constant_macro_path(p)
        led = simulate_property_ledgers(inputs, mp, p, 2045)
        res = evaluate_strategies(led, mp, p, 2045, 20)
        diff = res["plans"]["rent_a"]["raw_ex_b_real"] - res["plans"]["sell_stocks"]["raw_ex_b_real"]
        if diff > 0:
            hi_r = mid_r
        else:
            lo_r = mid_r
    be_rent_mo = r10(0.5 * (lo_r + hi_r))

    return {
        "breakeven_equity_nominal_return_pct_vs_rent_a": be_eq_vs_rent,
        "breakeven_equity_real_return_pct_vs_rent_a": round(((1.0 + be_eq_vs_rent / 100.0) / 1.024 - 1.0) * 100.0, 2),
        "breakeven_prop_a_monthly_rent_2026_r10_vs_stocks": be_rent_mo,
    }


# ---------------------------------------------------------------------------
# 50-Year Black-Swan Economic Conditions Engine
# 1) Rolling Historical Path Replays (50 cohorts wrapping 1976-2025 official data)
# 2) Six Named Multi-Decade Non-Uniform Black-Swan Regimes (2026-2076)
# 3) 500-Path Seeded Block-Bootstrap 50-Year Stress Distribution
# ---------------------------------------------------------------------------

def build_historical_replay_macro_path(hist_rows: List[dict], start_idx: int, params: dict) -> List[dict]:
    n = len(hist_rows)
    path = []
    for offset, yr in enumerate(range(2026, 2077)):
        if yr == 2026:
            path.append({
                "year": 2026, "cpi": 0.0, "hpi_a": 0.0, "hpi_b": 0.0, "hpi_ca": 0.0,
                "rent_mkt": 0.0, "eq_price": hist_rows[start_idx]["sp500_price_return"],
                "eq_div": hist_rows[start_idx]["sp500_div_yield"],
                "tbill_yield": hist_rows[start_idx]["tbill_3m_yield"],
                "ins_growth": 0.0, "water_a_growth": 0.0, "water_b_growth": 0.0,
                "elec_growth": 0.0, "prop13_fac": 1.0,
            })
        else:
            h = hist_rows[(start_idx + offset) % n]
            cpi = h["cpi_inflation"]
            path.append({
                "year": yr,
                "cpi": cpi,
                "hpi_a": h["hpi_region_a_growth"],
                "hpi_b": h["hpi_region_b_growth"],
                "hpi_ca": h["hpi_ca_growth"],
                "rent_mkt": h["rent_cpi_growth"],
                "eq_price": h["sp500_price_return"],
                "eq_div": h["sp500_div_yield"],
                "tbill_yield": h["gs10_yield"],
                "ins_growth": max(0.0, cpi + 0.01),
                "water_a_growth": max(0.01, cpi + 0.008),
                "water_b_growth": max(0.01, cpi + 0.010),
                "elec_growth": max(0.01, cpi + 0.008),
                "prop13_fac": h["boe_prop13_factor"],
            })
    return path


def build_named_black_swan_regimes(inputs: dict) -> List[dict]:
    """Six realistic 50-year non-uniform economic & statutory shock scenarios (2026-2076)."""
    regimes = []

    def run_custom(code: str, name: str, summary: str, modifier_fn, p_override: dict | None = None):
        p = dict(DEFAULT_PARAMS)
        if p_override:
            p.update(p_override)
        mp = build_constant_macro_path(p)
        for row in mp:
            if row["year"] > 2026:
                modifier_fn(row)
                row["prop13_fac"] = min(1.02, 1.0 + max(-0.02, row["cpi"]))
        led = simulate_property_ledgers(inputs, mp, p, 2045)
        res20 = evaluate_strategies(led, mp, p, 2045, 20)
        res31 = evaluate_strategies(led, mp, p, 2045, 31)  # Full path through 2076!
        winner20 = max(res20["plans"].items(), key=lambda kv: kv[1]["raw_ex_b_real"])[0]
        regimes.append({
            "code": code,
            "name": name,
            "summary": summary,
            "winner_20yr": winner20,
            "horizon_20yr_2065": {k: v["terminal_wealth_ex_b_real_2026_r10"] for k, v in res20["plans"].items()},
            "horizon_full_2076": {k: v["terminal_wealth_ex_b_real_2026_r10"] for k, v in res31["plans"].items()},
            "fmv_a_2045_real_r10": res20["fmv_a_at_transfer_real_2026_r10"],
        })

    # BS-1: 1970s-Style Stagflation & Volcker Rate Spike (2044-2053: 7.5%-9.1% CPI, flat real equities, 8.5% T-bills)
    def mod_stagflation(r):
        yr = r["year"]
        if 2044 <= yr <= 2051:
            r["cpi"] = 0.082
            r["hpi_a"] = 0.088
            r["hpi_b"] = 0.070
            r["hpi_ca"] = 0.085
            r["eq_price"] = -0.015
            r["eq_div"] = 0.025
            r["tbill_yield"] = 0.085
            r["ins_growth"] = 0.105
            r["water_a_growth"] = 0.090
            r["water_b_growth"] = 0.095
        elif 2052 <= yr <= 2056:
            r["cpi"] = 0.038
            r["eq_price"] = 0.085
            r["tbill_yield"] = 0.052

    run_custom(
        "BS-1",
        "1970s-Style Stagflation & Rate Spike (2044–2053)",
        "8.2%/yr CPI surge (calibrated to BLS 1979–1981 & June 2022 9.1% peak), negative real stock returns for 8 years, 8.5% CA-exempt Treasury yields, and Prop. 13 2% assessment cap compression.",
        mod_stagflation,
    )

    # BS-2: Post-Inheritance Equity Crash (-42% over 2 yrs) & Lost Stock Decade (2045-2054)
    def mod_lost_decade(r):
        yr = r["year"]
        if yr in (2046, 2047):
            r["eq_price"] = -0.24
            r["hpi_a"] = -0.06
        elif 2048 <= yr <= 2054:
            r["eq_price"] = 0.022
            r["tbill_yield"] = 0.028
        elif 2055 <= yr <= 2065:
            r["eq_price"] = 0.068

    run_custom(
        "BS-2",
        "Immediate Post-Sale Equity Crash & Lost Decade (2045–2054)",
        "Worst-case sequence-of-returns shock right after selling Property A in 2045: two consecutive -24% equity bear years (2000–2002 / 2008 analog) followed by 7 sluggish years before mean reversion.",
        mod_lost_decade,
    )

    # BS-3: Regional Tech/Housing Bust (-32% Property A drawdown, Prop. 8 reset, slow recovery)
    def mod_housing_bust(r):
        yr = r["year"]
        if 2042 <= yr <= 2045:
            r["hpi_a"] = -0.092
            r["hpi_b"] = -0.075
            r["hpi_ca"] = -0.085
            r["rent_mkt"] = -0.02
        elif 2046 <= yr <= 2052:
            r["hpi_a"] = 0.025
            r["hpi_b"] = 0.022

    run_custom(
        "BS-3",
        "Regional Tech & Housing De-Rating (-32% Pre-Inheritance Bust)",
        "Four-year regional housing contraction (2007–2011 FHFA HPI analog) cutting Property A's real value before 2045 inheritance, followed by muted 2.5% nominal housing growth.",
        mod_housing_bust,
    )

    # BS-4: California Climate Insurance, Megadrought Water & Grid Tariff Crisis
    def mod_ca_carrying_shock(r):
        yr = r["year"]
        if 2032 <= yr <= 2055:
            r["ins_growth"] = 0.085
            r["water_a_growth"] = 0.070
            r["water_b_growth"] = 0.075
            r["elec_growth"] = 0.065

    run_custom(
        "BS-4",
        "California Insurance, Megadrought Water & Utility Escalation",
        "Realistic high-value/landlord baseline quotes ($4,200 Property A / $6,500 Property B) compounded by 8.5%/yr climate insurance inflation and 7%/yr water/grid rate hikes.",
        mod_ca_carrying_shock,
        {"ins_a_2026": 4200.0, "ins_b_2026": 6500.0, "maint_a_rate": 0.008, "maint_b_rate": 0.011},
    )

    # BS-5: Federal Fiscal Dominance & Tax-Law Shock (Repeal of IRC §1014 Step-Up + Repeal of Prop. 19 Exclusion)
    def mod_fiscal_shock(r):
        if r["year"] >= 2036:
            r["cpi"] = 0.030
            r["tbill_yield"] = 0.046

    run_custom(
        "BS-5",
        "Statutory Tax Shock: IRC §1014 Step-Up Repealed + Prop. 19 Exclusion Repealed",
        "Tests CBO debt-stress legislative risk (debt >120% GDP): Congress eliminates date-of-death basis step-up (imposing carryover basis on sale) AND California eliminates even the partial Prop. 19 exclusion.",
        mod_fiscal_shock,
        {"prop19_repealed": True, "step_up_repealed": True},
    )

    # BS-6: Housing Super-Cycle vs. Secular Equity Compression (5.8% Housing, 4.8% Total Stock Return)
    def mod_housing_boom(r):
        r["hpi_a"] = 0.058
        r["hpi_b"] = 0.048
        r["hpi_ca"] = 0.052
        r["rent_mkt"] = 0.045
        r["eq_price"] = 0.035
        r["eq_div"] = 0.013

    run_custom(
        "BS-6",
        "Supply-Locked Housing Boom (5.8%/yr) + Low Equity Premium (4.8%/yr)",
        "Persistent land-supply scarcity drives 5.8%/yr Property A appreciation and $7,200/mo 2026$ executive single-family rent while global equity returns compress to 4.8%/yr.",
        mod_housing_boom,
        {"rent_a_2026_mo": 7200.0},
    )

    return regimes


def run_historical_and_bootstrap_stress(inputs: dict, macro: dict) -> dict:
    hist_rows = macro["annual_1976_2025"]
    n = len(hist_rows)

    # 1. All 50 historical starting cohorts (1976..2025 wrapped cleanly)
    replay_rows = []
    win_counts = {k: 0 for k in ("sell_stocks", "sell_60_40", "sell_treasuries", "rent_a", "live_a_keep_u3")}
    sell_vs_rent_diffs = []

    for idx in range(n):
        mp = build_historical_replay_macro_path(hist_rows, idx, DEFAULT_PARAMS)
        led = simulate_property_ledgers(inputs, mp, DEFAULT_PARAMS, 2045)
        res = evaluate_strategies(led, mp, DEFAULT_PARAMS, 2045, 20)
        core_plans = ["sell_stocks", "sell_60_40", "sell_treasuries", "rent_a", "live_a_keep_u3"]
        best = max(core_plans, key=lambda k: res["plans"][k]["raw_ex_b_real"])
        win_counts[best] += 1
        diff_sr = res["plans"]["sell_stocks"]["raw_ex_b_real"] - res["plans"]["rent_a"]["raw_ex_b_real"]
        sell_vs_rent_diffs.append(diff_sr)
        replay_rows.append({
            "cohort_start_year": hist_rows[idx]["year"],
            "winner": best,
            "sell_stocks_real_r10": res["plans"]["sell_stocks"]["terminal_wealth_ex_b_real_2026_r10"],
            "sell_60_40_real_r10": res["plans"]["sell_60_40"]["terminal_wealth_ex_b_real_2026_r10"],
            "sell_treasuries_real_r10": res["plans"]["sell_treasuries"]["terminal_wealth_ex_b_real_2026_r10"],
            "rent_a_real_r10": res["plans"]["rent_a"]["terminal_wealth_ex_b_real_2026_r10"],
            "live_a_keep_u3_real_r10": res["plans"]["live_a_keep_u3"]["terminal_wealth_ex_b_real_2026_r10"],
            "adv_stocks_over_rent_r10": r10(diff_sr),
        })

    # 2. 500-Path 5-Year Block-Bootstrap over full 50-year non-uniform paths (seed=20261112)
    rng = random.Random(20261112)
    mc_outcomes = {k: [] for k in ("sell_stocks", "sell_60_40", "sell_treasuries", "rent_a", "live_a_keep_u3", "live_a_rent_u3")}
    mc_wins = {k: 0 for k in ("sell_stocks", "sell_60_40", "sell_treasuries", "rent_a", "live_a_keep_u3")}

    for _ in range(500):
        sampled = []
        while len(sampled) < 51:
            bstart = rng.randrange(0, n)
            for b in range(5):
                sampled.append(hist_rows[(bstart + b) % n])
        mp = []
        for offset, yr in enumerate(range(2026, 2077)):
            h = sampled[offset]
            if yr == 2026:
                mp.append({
                    "year": 2026, "cpi": 0.0, "hpi_a": 0.0, "hpi_b": 0.0, "hpi_ca": 0.0,
                    "rent_mkt": 0.0, "eq_price": h["sp500_price_return"], "eq_div": h["sp500_div_yield"],
                    "tbill_yield": h["gs10_yield"], "ins_growth": 0.0, "water_a_growth": 0.0,
                    "water_b_growth": 0.0, "elec_growth": 0.0, "prop13_fac": 1.0,
                })
            else:
                cpi = h["cpi_inflation"]
                # De-mean historical 1976-2025 windfall valuation expansion slightly toward structural real drift while preserving full crash/spike volatility!
                mp.append({
                    "year": yr,
                    "cpi": cpi,
                    "hpi_a": h["hpi_region_a_growth"] - 0.015,
                    "hpi_b": h["hpi_region_b_growth"] - 0.015,
                    "hpi_ca": h["hpi_ca_growth"] - 0.012,
                    "rent_mkt": h["rent_cpi_growth"],
                    "eq_price": h["sp500_price_return"] - 0.020,
                    "eq_div": h["sp500_div_yield"],
                    "tbill_yield": max(0.001, h["gs10_yield"] - 0.010),
                    "ins_growth": max(0.0, cpi + 0.012),
                    "water_a_growth": max(0.01, cpi + 0.008),
                    "water_b_growth": max(0.01, cpi + 0.010),
                    "elec_growth": max(0.01, cpi + 0.008),
                    "prop13_fac": h["boe_prop13_factor"],
                })
        led = simulate_property_ledgers(inputs, mp, DEFAULT_PARAMS, 2045)
        res = evaluate_strategies(led, mp, DEFAULT_PARAMS, 2045, 20)
        for k in mc_outcomes:
            mc_outcomes[k].append(res["plans"][k]["raw_ex_b_real"])
        best_mc = max(mc_wins.keys(), key=lambda k: res["plans"][k]["raw_ex_b_real"])
        mc_wins[best_mc] += 1

    def pct(arr: List[float], q: float) -> int:
        s = sorted(arr)
        idx_f = q * (len(s) - 1)
        lo_i = int(math.floor(idx_f))
        hi_i = int(math.ceil(idx_f))
        val = s[lo_i] + (idx_f - lo_i) * (s[hi_i] - s[lo_i])
        return r10(val)

    mc_percentiles = {}
    for k, arr in mc_outcomes.items():
        mc_percentiles[k] = {
            "p10_r10": pct(arr, 0.10),
            "p25_r10": pct(arr, 0.25),
            "p50_r10": pct(arr, 0.50),
            "p75_r10": pct(arr, 0.75),
            "p90_r10": pct(arr, 0.90),
            "win_share_pct": round(mc_wins[k] / 5.0, 1) if k in mc_wins else None,
        }

    return {
        "historical_50_cohorts": {
            "win_counts": win_counts,
            "sell_stocks_win_pct": round(win_counts["sell_stocks"] / n * 100.0, 1),
            "min_adv_stocks_over_rent_r10": r10(min(sell_vs_rent_diffs)),
            "median_adv_stocks_over_rent_r10": pct(sell_vs_rent_diffs, 0.50),
            "max_adv_stocks_over_rent_r10": r10(max(sell_vs_rent_diffs)),
            "cohorts": replay_rows,
        },
        "block_bootstrap_500_paths": mc_percentiles,
    }


# ---------------------------------------------------------------------------
# Cash Inheritance & Federal/State/Local Estate Threshold Headroom Matrix
# ---------------------------------------------------------------------------

def compute_estate_headroom(ledger_base: List[dict]) -> dict:
    by_yr = {r["year"]: r for r in ledger_base}
    # Official 2026 = $15,000,000; Official 2027 = $15,480,000 (Rev. Proc. 2026-35 §3.44);
    # 2028+ indexed by CPI (2.4%/yr baseline) under P.L. 119-21 permanent IRC §2010(c)(3) indexing
    years_check = [2026, 2027, 2040, 2045, 2050]
    thresholds = []
    for yr in years_check:
        r = by_yr[yr]
        if yr == 2026:
            ex_single = 15000000.0
        elif yr == 2027:
            ex_single = 15480000.0
        else:
            ex_single = 15480000.0 * (r["cpi_cum"] / by_yr[2027]["cpi_cum"])
        ex_mfj_dsue = 2.0 * ex_single
        prop_a_nom = r["val_a"]
        headroom_single_nom = ex_single - prop_a_nom
        headroom_dsue_nom = ex_mfj_dsue - prop_a_nom
        # Statutory cutback stress: Congress halves basic exclusion to $7,500,000 (2026$) indexed
        ex_cutback_nom = 7500000.0 * r["cpi_cum"]
        headroom_cutback_nom = ex_cutback_nom - prop_a_nom

        thresholds.append({
            "year": yr,
            "exclusion_single_nominal_r10": r10(ex_single),
            "exclusion_single_real_2026_r10": r10(ex_single / r["cpi_cum"]),
            "exclusion_married_dsue_nominal_r10": r10(ex_mfj_dsue),
            "prop_a_fmv_nominal_r10": r10(prop_a_nom),
            "prop_a_fmv_real_2026_r10": r10(prop_a_nom / r["cpi_cum"]),
            "cash_headroom_single_nominal_r10": r10(headroom_single_nom),
            "cash_headroom_single_real_2026_r10": r10(headroom_single_nom / r["cpi_cum"]),
            "cash_headroom_dsue_nominal_r10": r10(headroom_dsue_nom),
            "cash_headroom_dsue_real_2026_r10": r10(headroom_dsue_nom / r["cpi_cum"]),
            "cutback_stress_headroom_real_2026_r10": r10(headroom_cutback_nom / r["cpi_cum"]),
        })

    # Cash addition sensitivity at 2045 anchor (in 2026 real dollars)
    r45 = by_yr[2045]
    ex45_real = (15480000.0 * (r45["cpi_cum"] / by_yr[2027]["cpi_cum"])) / r45["cpi_cum"]
    prop_a_45_real = r45["val_a"] / r45["cpi_cum"]
    cash_grid = []
    for cash_real in [0, 2000000, 5000000, 8000000, 10000000, 11000000, 15000000, 25000000]:
        gross_est_real = prop_a_45_real + cash_real
        taxable_single_real = max(0.0, gross_est_real - ex45_real)
        taxable_dsue_real = max(0.0, gross_est_real - 2.0 * ex45_real)
        # Top federal estate tax rate 40% above $1M excess (IRC §2001(c))
        est_tax_single_real = 0.40 * taxable_single_real
        est_tax_dsue_real = 0.40 * taxable_dsue_real
        cash_grid.append({
            "added_cash_real_2026_r10": r10(cash_real),
            "total_estate_real_2026_r10": r10(gross_est_real),
            "headroom_remaining_single_real_r10": r10(ex45_real - gross_est_real),
            "fed_estate_tax_single_real_r10": r10(est_tax_single_real),
            "fed_estate_tax_dsue_real_r10": r10(est_tax_dsue_real),
            "ca_and_local_inheritance_tax_r10": 0,
        })

    return {"by_year": thresholds, "cash_grid_2045_real": cash_grid}


def main() -> None:
    inputs = json.loads((DATA_DIR / "inputs_rounded.json").read_text(encoding="utf-8"))
    macro = json.loads((DATA_DIR / "macro_history_1976_2025.json").read_text(encoding="utf-8"))

    hist_audit = audit_historical_rolls(inputs, macro)

    # Baseline 2045 anchor & all 11 transfer years (2040-2050)
    mp_base = build_constant_macro_path(DEFAULT_PARAMS)
    ledger_2045 = simulate_property_ledgers(inputs, mp_base, DEFAULT_PARAMS, 2045)

    transfer_sweep = []
    for ty in range(2040, 2051):
        led_ty = simulate_property_ledgers(inputs, mp_base, DEFAULT_PARAMS, ty)
        ev20 = evaluate_strategies(led_ty, mp_base, DEFAULT_PARAMS, ty, 20)
        transfer_sweep.append(ev20)

    # Horizons at 2045 transfer: 10-yr (2055), 20-yr (2065), 31-yr (2076)
    horizons_2045 = {
        "10yr": evaluate_strategies(ledger_2045, mp_base, DEFAULT_PARAMS, 2045, 10),
        "20yr": evaluate_strategies(ledger_2045, mp_base, DEFAULT_PARAMS, 2045, 20),
        "31yr_to_2076": evaluate_strategies(ledger_2045, mp_base, DEFAULT_PARAMS, 2045, 31),
    }

    # Sensitivity checks on key modeling improvements (IRC §280A 2/3 vs 3/3, MFJ, High Insurance, High Rent)
    sens_naive_3_3 = evaluate_strategies(ledger_2045, mp_base, DEFAULT_PARAMS, 2045, 20, use_irc280a_pro_rata=False)

    p_mfj = dict(DEFAULT_PARAMS, filing_status="mfj", base_wage_2026=250000.0)
    led_mfj = simulate_property_ledgers(inputs, build_constant_macro_path(p_mfj), p_mfj, 2045)
    sens_mfj = evaluate_strategies(led_mfj, build_constant_macro_path(p_mfj), p_mfj, 2045, 20)

    p_real_ins = dict(DEFAULT_PARAMS, ins_a_2026=4200.0, ins_b_2026=6500.0)
    led_ins = simulate_property_ledgers(inputs, build_constant_macro_path(p_real_ins), p_real_ins, 2045)
    sens_real_ins = evaluate_strategies(led_ins, build_constant_macro_path(p_real_ins), p_real_ins, 2045, 20)

    p_hi_rent = dict(DEFAULT_PARAMS, rent_a_2026_mo=7200.0)
    led_hirent = simulate_property_ledgers(inputs, build_constant_macro_path(p_hi_rent), p_hi_rent, 2045)
    sens_hi_rent = evaluate_strategies(led_hirent, build_constant_macro_path(p_hi_rent), p_hi_rent, 2045, 20)

    breakevens = find_breakevens(inputs)
    black_swan_named = build_named_black_swan_regimes(inputs)
    stress_stats = run_historical_and_bootstrap_stress(inputs, macro)
    estate_matrix = compute_estate_headroom(ledger_2045)

    # Round all ledger_2045 fields to $10 for clean year-by-year 2026-2076 tables
    yearly_2026_2076_rounded = []
    for r in ledger_2045:
        yearly_2026_2076_rounded.append({
            "year": r["year"],
            "cpi_index": round(r["cpi_cum"], 4),
            "prop19_cap_nominal_r10": r10(r["prop19_cap"]),
            "val_a_nominal_r10": r10(r["val_a"]),
            "val_a_real_r10": r10(r["val_a"] / r["cpi_cum"]),
            "av_a_live_nominal_r10": r10(r["av_a_live"]),
            "av_a_rent_nominal_r10": r10(r["av_a_rent"]),
            "tax_a_live_nominal_r10": r10(r["tax_a_live"]),
            "tax_a_rent_nominal_r10": r10(r["tax_a_rent"]),
            "ins_a_nominal_r10": r10(r["ins_a"]),
            "water_a_nominal_r10": r10(r["water_a"]),
            "elec_a_nominal_r10": r10(r["elec_a"]),
            "maint_a_nominal_r10": r10(r["maint_a"]),
            "opex_a_live_nominal_r10": r10(r["total_opex_a_live"]),
            "opex_a_rent_nominal_r10": r10(r["total_opex_a_rent"]),
            "val_b_nominal_r10": r10(r["val_b"]),
            "val_b_real_r10": r10(r["val_b"] / r["cpi_cum"]),
            "av_b_occ_nominal_r10": r10(r["av_b_owner_occ"]),
            "tax_b_occ_nominal_r10": r10(r["tax_b_owner_occ"]),
            "tax_b_non_occ_nominal_r10": r10(r["tax_b_non_occ"]),
            "ins_b_nominal_r10": r10(r["ins_b"]),
            "water_b_nominal_r10": r10(r["water_b"]),
            "elec_b_nominal_r10": r10(r["elec_b"]),
            "maint_b_nominal_r10": r10(r["maint_b"]),
            "opex_b_occ_nominal_r10": r10(r["total_opex_b_owner_occ"]),
            "rent_b_2u_nominal_r10": r10(r["rent_b_2u_gross"]),
            "rent_a_gross_nominal_r10": r10(r["rent_a_gross"]),
        })

    output = {
        "generated_utc": "2026-11-12",
        "historical_roll_audit": hist_audit,
        "baseline_params": DEFAULT_PARAMS,
        "horizons_2045": horizons_2045,
        "transfer_year_sweep_2040_2050": transfer_sweep,
        "sensitivities_2045_20yr": {
            "naive_3_of_3_prop_b_deduction": {k: v["terminal_wealth_ex_b_real_2026_r10"] for k, v in sens_naive_3_3["plans"].items()},
            "married_filing_jointly": {k: v["terminal_wealth_ex_b_real_2026_r10"] for k, v in sens_mfj["plans"].items()},
            "realistic_replacement_insurance_4200_6500": {k: v["terminal_wealth_ex_b_real_2026_r10"] for k, v in sens_real_ins["plans"].items()},
            "executive_sfr_rent_7200_mo": {k: v["terminal_wealth_ex_b_real_2026_r10"] for k, v in sens_hi_rent["plans"].items()},
        },
        "breakevens": breakevens,
        "yearly_2026_2076": yearly_2026_2076_rounded,
        "black_swan_named_regimes": black_swan_named,
        "black_swan_statistical": stress_stats,
        "estate_headroom": estate_matrix,
    }

    # Strip internal float helper keys before saving
    def clean_raw(obj):
        if isinstance(obj, dict):
            return {k: clean_raw(v) for k, v in obj.items() if k != "raw_ex_b_real"}
        if isinstance(obj, list):
            return [clean_raw(x) for x in obj]
        return obj

    OUT_PATH.write_text(json.dumps(clean_raw(output), indent=2) + "\n", encoding="utf-8")
    print(f"Engine complete -> {OUT_PATH}")


if __name__ == "__main__":
    main()
