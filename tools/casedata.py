#!/usr/bin/env python3
"""Anonymized working dataset and projection engine.

PRIVACY RULE FOR THIS FILE
--------------------------
This module holds the owner's working figures in the anonymized form the owner
requested: every dollar amount is rounded to the nearest ten dollars, and no
personal identifier is stored. There is no owner name, street address, parcel
or assessor identification number, trust name, account number, date of birth,
document image or contact detail anywhere in this file or in any file it
generates.

EVIDENCE RULE FOR THIS FILE
---------------------------
Two different kinds of number live here and are never mixed:

  "owner"      Supplied by the owner from personal records. Rounded to the
               nearest ten dollars. Not verified against any official page and
               never labeled as verified.
  "derived"    Arithmetic performed on owner figures inside this engine. Labeled
               as a projection or an assumption, never as an official figure.
  "official"   Read from a page in tools/sources.py. Lives in the source
               registry, not here, and is cited with its scope.

Anything that could not be confirmed against an official page is left blank or
flagged. Blank means unknown, not zero.
"""
from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BASE_YEAR = 2026
DEFAULT_TRANSFER_YEAR = 2045
EARLIEST_TRANSFER_YEAR = 2040
LATEST_TRANSFER_YEAR = 2050


# --------------------------------------------------------------- formatting
def money(value: float, step: int = 10) -> int:
    """Round to the nearest ten dollars, halves up, as the owner requested."""
    quantised = (Decimal(str(value)) / Decimal(step)).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    return int(quantised * Decimal(step))


def fmt(value: int | float) -> str:
    """Render a whole-dollar amount with thousands separators."""
    return f"${int(round(value)):,}"


def pct(value: float, places: int = 2) -> str:
    return f"{value * 100:.{places}f}%"


# ------------------------------------------------------------------ assets
PROPERTY_A = {
    "code": "Property A",
    "role": "Anticipated transfer through a revocable trust",
    "county": "Santa Clara County, California",
    "area": "Postal area 95014 (Cupertino)",
    "owner_note": (
        "Not owned by the decision maker today. Expected to transfer through a "
        "trust inside the 2040-2050 window. The window is an expectation, not a "
        "confirmed date and not a legal forecast."
    ),
    "value_now": money(3_100_000),
    "value_basis": "Owner estimate as of November 2026. Not an appraisal.",
    "assessed_growth": 0.02,
}

PROPERTY_B = {
    "code": "Property B",
    "role": "Already owned by the decision maker",
    "county": "City and County of San Francisco",
    "area": "Postal area 94122 (Outer Sunset)",
    "owner_note": (
        "Owned today and held independently of the trust transfer. It carries its "
        "own basis, its own assessment and its own tenancies, and it is the "
        "decision maker's current residence."
    ),
    "value_now": money(1_800_000),
    "value_basis": "Owner estimate as of November 2026. Not an appraisal.",
    "assessed_growth": 0.02,
}

# Year, property tax as billed, enrolled assessment. Rounded to nearest $10.
# Source of the underlying figures: owner's own tax history. Not an official
# record; the county assessor's roll is the controlling record.
A_HISTORY = [
    # year, tax, assessment
    (2026, None, money(550_537)),
    (2025, money(7_207), money(539_743)),
    (2024, money(7_003), money(529_161)),
    (2023, money(6_917), money(518_786)),
    (2022, money(6_755), money(508_614)),
    (2021, money(6_662), money(498_642)),
    (2020, money(6_565), money(493_530)),
    (2019, money(6_565), money(483_854)),
    (2018, money(6_383), money(474_368)),
    (2017, money(6_383), money(465_067)),
    (2016, money(6_414), money(455_949)),
    (2015, money(6_130), money(449_101)),
    (2014, money(5_965), money(440_305)),
]

B_HISTORY = [
    (2025, money(2_439), money(114_248)),
    (2024, money(2_315), money(112_008)),
    (2023, money(2_179), money(109_814)),
    (2022, money(2_107), money(107_662)),
    (2021, money(2_066), money(105_595)),
    (2020, money(2_197), money(104_513)),
    (2019, money(2_134), money(102_465)),
    (2018, money(2_061), money(100_456)),
    (2017, money(1_740), money(98_488)),
    (2016, money(1_675), money(96_557)),
]

HOMEOWNERS_EXEMPTION = money(7_000)  # Revenue and Taxation Code section 218.

# The proprietor's own last known bill is used to derive an effective rate.
# This is arithmetic on an owner figure, not an official rate.
A_TAX_2025, A_ASSESS_2025 = 7_210, 539_740
B_TAX_2025, B_ASSESS_2025 = 2_440, 114_250

# Property A is owner occupied today, so the homeowners' exemption reduces the
# taxable value. Property B is not treated as receiving it, because two of its
# three units are rented and the owner's own unit is one of three.
A_EFFECTIVE_RATE = A_TAX_2025 / (A_ASSESS_2025 - HOMEOWNERS_EXEMPTION)
B_EFFECTIVE_RATE = B_TAX_2025 / B_ASSESS_2025

# Published Proposition 19 value limit and the assumption used to carry it
# forward. The published amount is exact and unrounded: it is an official
# figure, not an owner amount, so rounding it would make it wrong. Only the
# carried-forward projection of it is rounded.
PROP19_LIMIT_NOW = 1_044_586
PROP19_LIMIT_FROM = "February 16, 2025"
PROP19_LIMIT_TO = "February 15, 2027"
PROP19_LIMIT_GROWTH = 0.02  # ASSUMPTION, flagged for review.

# --------------------------------------------------------- operating inputs
# Every item below is owner supplied unless the note says otherwise. Ranges are
# the owner's own observed range. Nothing here is verified against an official
# page except where a source key is named.
OPERATING = {
    "a_water_low": money(100),
    "a_water_high": money(150),
    "b_water_low": money(330),
    "b_water_high": money(400),
    "a_electric_low": money(10),   # net credit to the owner, so a negative cost
    "a_electric_high": money(20),
    "b_electric_low": money(30),
    "b_electric_high": money(70),
    "a_insurance": money(1_500),
    "b_insurance": money(1_500),
    "insurance_low": money(1_500),
    "insurance_high": money(3_000),
    "b_rent_units_rented": 2,
    "b_rent_units_total": 3,
    "b_rent_income": money(7_150),
}

DEFAULT_INPUTS = {
    "transfer_year": DEFAULT_TRANSFER_YEAR,
    "a_appreciation": 0.035,
    "b_appreciation": 0.030,
    "inflation": 0.025,
    "assessed_growth": 0.020,
    "prop19_growth": PROP19_LIMIT_GROWTH,
    "insurance_growth": 0.030,
    "rent_growth": 0.030,
    "maintenance_a": 0.005,      # share of value per year. ASSUMPTION.
    "maintenance_b": 0.010,      # share of value per year. ASSUMPTION.
    "selling_cost": 0.060,       # commission, transfer charges and closing. ASSUMPTION.
    "equity_return": 0.060,
    "treasury_yield": 0.036,
    "staging_months": 30,
    "equity_phase_months": 12,
    "vacancy_rate": 0.050,
    "management_rate": 0.080,
    "horizon_years": 20,
}


# ------------------------------------------------------------------- engine
def _grow(value: float, rate: float, years: float) -> float:
    return value * ((1.0 + rate) ** years)


def assessed_value(asset: str, year: int, inputs: dict) -> int:
    """Prop 13 factored base year value, capped at the annual inflation factor."""
    growth = inputs["assessed_growth"]
    if asset == "A":
        base_year, base_value = 2026, money(550_537)
    else:
        base_year, base_value = 2026, money(114_248) * 1.02
    return money(_grow(base_value, growth, year - base_year))


def market_value(asset: str, year: int, inputs: dict) -> int:
    key = "a_appreciation" if asset == "A" else "b_appreciation"
    base = PROPERTY_A["value_now"] if asset == "A" else PROPERTY_B["value_now"]
    return money(_grow(base, inputs[key], year - BASE_YEAR))


def prop19_limit(year: int, inputs: dict) -> int:
    """Carry the published limit forward. The growth rate is an assumption."""
    return money(_grow(PROP19_LIMIT_NOW, inputs["prop19_growth"], year - 2025))


def new_taxable_value(fmv: float, factored_base: float, limit: float) -> int:
    """Revenue and Taxation Code section 63.2 subdivision (d).

    New taxable value equals the prior taxable value plus any excess of fair
    market value over that value plus the adjusted limit. Where the excess is
    positive this simplifies to fair market value minus the adjusted limit.
    """
    return money(factored_base + max(0.0, fmv - (factored_base + limit)))


def property_tax(taxable: float, rate: float, homeowners: bool) -> int:
    base = taxable - (HOMEOWNERS_EXEMPTION if homeowners else 0)
    return money(max(0.0, base) * rate)


def annual_operating(asset: str, year: int, inputs: dict) -> dict:
    """Owner supplied operating costs, carried forward at the inflation input."""
    years = year - BASE_YEAR
    inflation = inputs["inflation"]
    insurance_rate = inputs["insurance_growth"]
    if asset == "A":
        water = money(money((100 + 150) / 2 * 12) * _grow(1, inflation, years))
        electric_credit = -(money(money((10 + 20) / 2 * 12) * _grow(1, inflation, years)))
        insurance = money(OPERATING["a_insurance"] * _grow(1, insurance_rate, years))
        maintenance = money(market_value("A", year, inputs) * inputs["maintenance_a"])
    else:
        water = money(money((330 + 400) / 2 * 12) * _grow(1, inflation, years))
        electric_credit = money(money((30 + 70) / 2 * 12) * _grow(1, inflation, years))
        insurance = money(OPERATING["b_insurance"] * _grow(1, insurance_rate, years))
        maintenance = money(market_value("B", year, inputs) * inputs["maintenance_b"])
    return {
        "water": water,
        "electric": electric_credit,
        "insurance": insurance,
        "maintenance": maintenance,
        "total": money(water + electric_credit + insurance + maintenance),
    }


def b_rent_income(year: int, inputs: dict) -> int:
    years = year - BASE_YEAR
    return money(OPERATING["b_rent_income"] * 12 * _grow(1, inputs["rent_growth"], years))


def scenario(inputs: dict) -> dict:
    """Compute the full comparison for one set of what-if inputs."""
    t = inputs["transfer_year"]
    horizon = inputs["horizon_years"]

    a_fmv_now = PROPERTY_A["value_now"]
    a_fmv = market_value("A", t, inputs)
    a_base = assessed_value("A", t, inputs)
    limit = prop19_limit(t, inputs)

    taxable_prop19 = new_taxable_value(a_fmv, a_base, limit)
    taxable_full = money(a_fmv)

    tax_now = property_tax(assessed_value("A", BASE_YEAR, inputs), A_EFFECTIVE_RATE, True)
    tax_prop19 = property_tax(taxable_prop19, A_EFFECTIVE_RATE, True)
    tax_full = property_tax(taxable_full, A_EFFECTIVE_RATE, False)

    b_fmv = market_value("B", t, inputs)
    b_tax = property_tax(assessed_value("B", t, inputs), B_EFFECTIVE_RATE, False)

    op_a = annual_operating("A", t, inputs)
    op_b = annual_operating("B", t, inputs)
    rent_b = b_rent_income(t, inputs)

    net_proceeds = money(a_fmv * (1 - inputs["selling_cost"]))

    # Ending value of the sale-and-invest path, immediate entry.
    years_after = horizon
    invested_now = money(net_proceeds * _grow(1, inputs["equity_return"], years_after))

    # Ending value of the sale-and-stage path: park in Treasuries for the
    # staging window, then move into equities for the remainder.
    staging_years = inputs["staging_months"] / 12.0
    after_stage = money(net_proceeds * _grow(1, inputs["treasury_yield"], staging_years))
    remaining = max(0.0, years_after - staging_years)
    invested_staged = money(after_stage * _grow(1, inputs["equity_return"], remaining))

    # Ending value of keeping the property, valued at the appreciation input
    # and net of the carrying costs actually paid over the horizon.
    horizon_year = t + horizon
    a_fmv_end = market_value("A", horizon_year, inputs)
    carry_years = 0.0
    for offset in range(int(horizon)):
        year = t + offset
        carry = property_tax(taxable_prop19, A_EFFECTIVE_RATE, True)
        carry += annual_operating("A", year, inputs)["total"]
        carry_years += carry * _grow(1, 0.0, 0)
    annual_carry = money(
        property_tax(taxable_prop19, A_EFFECTIVE_RATE, True) + op_a["total"]
    )
    cumulative_carry = money(annual_carry * horizon)

    return {
        "transfer_year": t,
        "horizon_years": horizon,
        "a": {
            "value_now": a_fmv_now,
            "value_at_transfer": a_fmv,
            "assessed_at_transfer": a_base,
            "prop19_limit": limit,
            "taxable_prop19": taxable_prop19,
            "taxable_full": taxable_full,
            "tax_now": tax_now,
            "tax_prop19": tax_prop19,
            "tax_full": tax_full,
            "tax_multiple_prop19": round(tax_prop19 / tax_now, 1) if tax_now else None,
            "tax_multiple_full": round(tax_full / tax_now, 1) if tax_now else None,
            "operating": op_a,
            "carrying_total": annual_carry,
            "carrying_monthly": money(annual_carry / 12),
            "value_end": a_fmv_end,
            "cumulative_carry": cumulative_carry,
        },
        "b": {
            "value_at_transfer": b_fmv,
            "tax_at_transfer": b_tax,
            "operating": op_b,
            "rent_income": rent_b,
        },
        "sale": {
            "gross": a_fmv,
            "selling_cost": money(a_fmv * inputs["selling_cost"]),
            "net_proceeds": net_proceeds,
            "invested_now_end": invested_now,
            "after_staging": after_stage,
            "invested_staged_end": invested_staged,
            "staging_shortfall": money(invested_now - invested_staged),
        },
        "effective_rates": {
            "a": A_EFFECTIVE_RATE,
            "b": B_EFFECTIVE_RATE,
        },
    }


def breakeven_rent(taxable: float, rate: float, operating_total: float,
                   inputs: dict) -> int:
    """Gross annual rent needed to cover carrying cost, vacancy and management.

    This avoids inventing a market rent. The reader compares the number against
    an actual quote instead of trusting a fabricated yield.
    """
    tax = property_tax(taxable, rate, False)
    fixed = tax + operating_total
    net_factor = (1 - inputs["vacancy_rate"]) * (1 - inputs["management_rate"])
    return money(fixed / net_factor)


def runtime_payload(inputs: dict) -> str:
    """Everything the browser needs to recalculate without any network call."""
    payload = {
        "baseYear": BASE_YEAR,
        "transferRange": [EARLIEST_TRANSFER_YEAR, LATEST_TRANSFER_YEAR],
        "inputs": inputs,
        "homeownersExemption": HOMEOWNERS_EXEMPTION,
        "effectiveRateA": A_EFFECTIVE_RATE,
        "effectiveRateB": B_EFFECTIVE_RATE,
        "a": {
            "valueNow": PROPERTY_A["value_now"],
            "assessed2026": money(550_537),
            "waterBand": [OPERATING["a_water_low"], OPERATING["a_water_high"]],
            "electricCreditBand": [OPERATING["a_electric_low"], OPERATING["a_electric_high"]],
            "insurance": OPERATING["a_insurance"],
        },
        "b": {
            "valueNow": PROPERTY_B["value_now"],
            "assessed2026": money(114_248) * 1.02,
            "waterBand": [OPERATING["b_water_low"], OPERATING["b_water_high"]],
            "electricBand": [OPERATING["b_electric_low"], OPERATING["b_electric_high"]],
            "insurance": OPERATING["b_insurance"],
            "rentIncomeMonthly": OPERATING["b_rent_income"],
        },
        "prop19LimitNow": PROP19_LIMIT_NOW,
        "prop19LimitBaseYear": 2025,
        "saleNetProceeds": scenario(inputs)["sale"]["net_proceeds"],
    }
    return json.dumps(payload, separators=(",", ":"))


# ------------------------------------------------------- staging simulation
def _month_equity_return(month: int, params: dict) -> float:
    """Monthly equity return for one month of a clearly synthetic path."""
    if month < params["fall_start"]:
        return params["equity"] / 12.0
    if month < params["fall_start"] + params["fall_months"]:
        return (1.0 - params["fall_depth"]) ** (1.0 / params["fall_months"]) - 1.0
    return params["recover"] / 12.0


def simulate_timeline(plan: str, params: dict) -> dict:
    """Monthly simulation of one entry plan under a synthetic fall path.

    Mirrors the browser implementation in assets/app.js. If either is changed,
    the other must be changed in the same way; tools/test_case.py fails the
    build when they diverge.
    """
    cash = float(params["start"])
    equity = 0.0
    worst = float(params["start"])
    months = max(1, int(round(params["horizon"] * 12)))
    for month in range(months):
        if plan == "cash":
            target = 0.0
        elif plan == "immediate":
            target = 1.0
        elif month < params["staging"]:
            target = 0.0
        elif params["phase"] > 0 and month < params["staging"] + params["phase"]:
            target = (month - params["staging"] + 1) / params["phase"]
        else:
            target = 1.0
        total = cash + equity
        want = total * target
        if want > equity:
            move = min(cash, want - equity)
            cash -= move
            equity += move
        monthly_yield = (
            params["yield"] if month < params["staging"] else params["yield_after"]
        ) / 12.0
        cash *= 1 + monthly_yield
        equity *= 1 + _month_equity_return(month, params)
        now = cash + equity
        if now < worst:
            worst = now
    return {"end": cash + equity, "worst": worst}
