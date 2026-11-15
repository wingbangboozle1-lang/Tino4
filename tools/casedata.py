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
# forward. The published amount is official; the carry-forward rate is not.
PROP19_LIMIT_NOW = money(1_044_586)
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


# ------------------------------------------------------- historical regimes
# Each entry is an official observation, not a forecast. Sources are keyed into
# tools/sources.py and quoted there with their exact scope.
REGIMES = [
    {
        "id": "r1929",
        "name": "1929 crash and the long deflationary slide",
        "window": "1929-1954",
        "sources": ["fed_1929"],
        "facts": [
            ("Equity index peak", "381.17 on September 3, 1929", "fed_1929"),
            ("Two-day decline", "nearly 13 percent on October 28, 1929 and nearly 12 percent the next day", "fed_1929"),
            ("Trough", "41.22 on July 8, 1932, 89 percent below the peak", "fed_1929"),
            ("Recovery of the peak", "November 23, 1954, about 25 years later", "fed_1929"),
        ],
        "lesson": (
            "A single bad entry month can define a generation. The danger is not only the fall "
            "but the length of the flat period afterwards, which is what breaks a plan that "
            "needs the money."
        ),
    },
    {
        "id": "r1970s",
        "name": "1970s stagflation",
        "window": "1970s",
        "sources": ["bls_cpi", "treasury_yield"],
        "facts": [
            ("Peak twelve-month CPI", "9.1 percent through June 2022, the largest since November 1981", "bls_cpi"),
            ("Cash yield context", "Treasury par yields are published daily and move with policy", "treasury_yield"),
        ],
        "lesson": (
            "Nominal growth can look healthy while real purchasing power falls. A plan built on a "
            "single nominal return assumption is fragile when inflation and equity returns move "
            "against each other."
        ),
    },
    {
        "id": "r2008",
        "name": "Great Recession",
        "window": "December 2007 to June 2009",
        "sources": ["fed_2008"],
        "facts": [
            ("Equity decline", "S&P 500 fell 57 percent from the October 2007 peak to the March 2009 trough", "fed_2008"),
            ("House prices", "fell approximately 30 percent on average from the mid-2006 peak to mid-2009", "fed_2008"),
            ("Output", "real GDP fell 4.3 percent peak to trough", "fed_2008"),
            ("Unemployment", "5 percent in December 2007, peaked at 10 percent in October 2009", "fed_2008"),
        ],
        "lesson": (
            "Housing and equities fell together. Holding one asset class was not a hedge, and an "
            "owner who needed to sell in the trough realised both losses at once."
        ),
    },
    {
        "id": "r2022",
        "name": "2022 inflation shock",
        "window": "2022",
        "sources": ["bls_cpi", "treasury_yield"],
        "facts": [
            ("Twelve-month CPI", "9.1 percent through June 2022", "bls_cpi"),
            ("Rate context", "short Treasury yields repriced quickly; see the daily par yield curve", "treasury_yield"),
        ],
        "lesson": (
            "Short-dated government paper paid a materially better rate within a year. That is the "
            "reinvestment risk in reverse: staging protects against a crash but can also strand an "
            "owner in low yields if rates fall while they wait."
        ),
    },
]


# ------------------------------------------------------ deadline timeline
# Each step names the authority for the deadline. "Day 0" is the date of death.
PROCESS_STEPS = [
    {
        "offset": "Day 0",
        "title": "Date of death",
        "detail": "Every clock below is measured from this date. Nothing in this plan can be executed before the trustee confirms the trust terms and their own authority.",
        "sources": ["prob_16061_7", "irs_706_due"],
    },
    {
        "offset": "60 days",
        "title": "Trustee notice to beneficiaries and heirs",
        "detail": "A trustee must serve the statutory notification within 60 days after a revocable trust becomes irrevocable by reason of death, or within 60 days after becoming aware of a person entitled to notice. This is the step that starts the beneficiary's own review window.",
        "sources": ["prob_16061_7"],
    },
    {
        "offset": "150 days",
        "title": "Change-in-ownership statement to the county",
        "detail": "For an interest in real property transferred by reason of death outside probate, including a transfer through the medium of a trust, the change-in-ownership statement must be filed within 150 days after the date of death. For other transfers the period is 90 days.",
        "sources": ["rtc_480"],
    },
    {
        "offset": "9 months",
        "title": "Federal estate tax return, if required",
        "detail": "Form 706 is generally due nine months after the date of death. A six-month extension is available only if it is requested before the due date and the estimated correct tax is paid before the due date. Filing may still be required below the threshold to elect portability.",
        "sources": ["irs_706_due", "irs_estate_faq", "irs_estate"],
    },
    {
        "offset": "Within 1 year",
        "title": "Occupy the home and claim the homeowners' exemption",
        "detail": "Under the current intergenerational exclusion the transferred principal residence must become the transferee's principal residence within one year, and the transferee must file for the homeowners' or disabled veterans' exemption within one year. Missing this window removes the exclusion.",
        "sources": ["rtc_63_2", "boe_prop19", "rtc_218"],
    },
    {
        "offset": "Within 3 years",
        "title": "File the exclusion claim",
        "detail": "The claim must be filed within three years after the transfer, or before the property is transferred to a third party, or before the transferee stops occupying it, whichever is earliest. In defined circumstances a claim filed after the period may be considered but applies only prospectively.",
        "sources": ["rtc_63_2", "boe_prop19"],
    },
    {
        "offset": "Every January 1",
        "title": "Lien date",
        "detail": "January 1 is the lien date for all property. The assessment and the exemptions that apply on that date drive the bill for the following fiscal year.",
        "sources": ["boe_pub29"],
    },
    {
        "offset": "Every February 15",
        "title": "Exemption claim deadline",
        "detail": "February 15 is the legal deadline for filing most exemption claims, including the homeowners' exemption. A later filing can still receive a reduced share of the exemption by December 10.",
        "sources": ["boe_pub29"],
    },
    {
        "offset": "Every July 2 to September 15",
        "title": "Assessment appeal window",
        "detail": "Applications for reduction in assessed value are filed with the clerk of the county board of supervisors in the stated window, which can extend to November 30. This is the route for disputing a reassessment the owner believes is wrong.",
        "sources": ["boe_pub29"],
    },
    {
        "offset": "December 10 and April 10",
        "title": "Installment delinquency dates",
        "detail": "The first secured installment is delinquent after December 10 and the second after April 10. Missing either date adds penalties that compound the carrying cost of a high-value property.",
        "sources": ["boe_pub29"],
    },
]


# ------------------------------------------------------------ law watchlist
LAW_WATCH = [
    {
        "title": "Proposition 43, Limits Voters' Ability to Raise Revenues for Local Government Services",
        "status": "On the November 3, 2026 ballot; unofficial results reported 2026-11-14",
        "detail": (
            "A legislative constitutional amendment. It was on the November 3, 2026 statewide "
            "ballot. The Secretary of State publishes results as unofficial until certification."
        ),
        "result": (
            "Unofficial statewide result reported on 2026-11-14: about 42.4 percent yes and "
            "57.6 percent no, with all precincts partially reporting. County elections officials "
            "must report final official results by December 4, 2026 and the Secretary of State "
            "certifies on December 11, 2026."
        ),
        "why": "Local special taxes and parcel taxes appear on the property tax bill, so the approval threshold for them affects long-run carrying cost.",
        "sources": ["sos_qualified", "sos_results"],
    },
    {
        "title": "Proposition 42, Prohibits New State Personal Property Taxes and Certain Retroactive State Taxes",
        "status": "On the November 3, 2026 ballot; unofficial results reported 2026-11-14",
        "detail": "An initiative constitutional amendment on the November 3, 2026 statewide ballot.",
        "result": (
            "Unofficial statewide result reported on 2026-11-14: about 51.3 percent yes and "
            "48.7 percent no. Subject to certification on December 11, 2026."
        ),
        "why": "Relevant to any future state-level tax on property or on retroactive assessments.",
        "sources": ["sos_qualified", "sos_results"],
    },
    {
        "title": "Proposition 40, Imposes One-Time Tax on Certain Taxpayers",
        "status": "On the November 3, 2026 ballot; unofficial results reported 2026-11-14",
        "detail": "An initiative constitutional amendment and statute on the November 3, 2026 statewide ballot.",
        "result": (
            "Unofficial statewide result reported on 2026-11-14: about 47.8 percent yes and "
            "52.2 percent no. Subject to certification on December 11, 2026."
        ),
        "why": "A wealth or one-time tax would change the calculus for holding a concentrated, high-value asset.",
        "sources": ["sos_qualified", "sos_results"],
    },
    {
        "title": "Proposition 19 value limit adjustment",
        "status": "Recalculated every other February 16",
        "detail": (
            "The adjusted amount is recalculated using the Federal Housing Finance Agency House "
            "Price Index for California for the prior calendar year. The next adjustment after the "
            "current period occurs in February 2027."
        ),
        "result": (
            "For transfers from February 16, 2025 through February 15, 2027 the amount is "
            "$1,044,586. Any projection that carries this amount forward uses an assumption and is "
            "labeled as such."
        ),
        "why": "The size of the exclusion directly sets the post-transfer assessment and therefore the annual property tax.",
        "sources": ["boe_lta_2025_009", "fhfa_hpi"],
    },
    {
        "title": "Federal transfer tax exclusion",
        "status": "Indexed from 2027",
        "detail": (
            "The basic exclusion is $15,000,000 for estates of decedents who died in 2026 and "
            "$15,480,000 for 2027, with the annual gift exclusion rising from $19,000 to $20,000. "
            "Indexing does not guarantee that a future Congress keeps the amount."
        ),
        "result": "Published by the IRS in IR-2026-133 on November 5, 2026.",
        "why": "A transfer expected in the 2040s sits far beyond any published amount; the amount must be re-read at the time.",
        "sources": ["irs_2027", "irs_estate"],
    },
    {
        "title": "Statewide rent cap",
        "status": "Current law",
        "detail": (
            "An owner may not raise gross rent more than 5 percent plus the change in the cost of "
            "living, or 10 percent, whichever is lower, over any twelve-month period. A new tenancy "
            "in which no prior tenant remains may be set at any initial rate. Exemptions apply, "
            "including for housing with a certificate of occupancy issued within the previous 15 years."
        ),
        "result": "Governs future increases on the two rented units at Property B and on any future tenancy at Property A.",
        "why": "Sets the realistic growth path of rental income and therefore the yield of any keep-and-rent path.",
        "sources": ["civ_1947_12", "ca_leg_search"],
    },
]


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
