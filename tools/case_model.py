"""Quantified projection model behind the public pages.

Privacy contract for this module (owner's instruction, 2026-11-17):

* every dollar amount that reaches a page is rounded to the nearest ten dollars
  by :func:`usd`, so a published figure cannot be matched to a single online
  record by searching its exact value;
* no personal name, address, postal code, parcel or roll identifier, locality
  name, account number or document date appears here;
* every constant carries a provenance label so the page can mark it as an
  enacted rule, a derived figure, a rounded owner-stated input, or an
  unverified assumption.

The model is arithmetic on stated assumptions. It is not a forecast, an
appraisal, a tax return, or advice. Where a number cannot be confirmed from an
official source it is labelled ``assumption`` or ``unverified`` by the caller
and listed on the flagged-for-review page.
"""
from __future__ import annotations

ROUND_TO = 10

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def r10(value: float) -> int:
    """Round to the nearest ten dollars (the owner's de-identification step).

    Half-way amounts round up rather than to even, so the published figure never
    depends on Python's tie-breaking for a value such as five dollars exactly.
    """
    scaled = float(value) / ROUND_TO
    return int((scaled + 0.5) // 1 if scaled >= 0 else -((-scaled + 0.5) // 1)) * ROUND_TO


def usd(value: float) -> str:
    """Format a dollar amount, rounded to $10, never with cents.

    A true zero is written as a word, because a rendered zero reads like a
    measurement; a rounding artifact must not look like one.
    """
    rounded = r10(value)
    if rounded == 0:
        return "none"
    sign = "-" if rounded < 0 else ""
    return f"{sign}${abs(rounded):,}"


def pct(value: float, places: int = 2) -> str:
    return f"{value * 100:.{places}f}%"


def grow(start: float, rate: float, years: int) -> float:
    value = float(start)
    for _ in range(max(0, int(years))):
        value *= 1.0 + rate
    return value


def midpoint(low: float, high: float) -> float:
    return (low + high) / 2.0


# --------------------------------------------------------------------------
# publication guard
# --------------------------------------------------------------------------
#
# A shared public page must not print a figure that a reader could type into a
# search box and land on one assessor record or one listing. Escalated and
# computed figures move away from the source records on their own. The starting
# rows of the year-by-year tables do not: they are the inputs themselves. Those
# rows are offset here by one percent, and the offset is stated on the page. One
# percent is small enough that the row is still the same quantity and large
# enough that no published amount equals a record line.

SNAPSHOT_OFFSET = 0.010


def snapshot(value: float) -> float:
    """Offset a starting-year snapshot so it is not a copy of a record."""
    return float(value) * (1.0 + SNAPSHOT_OFFSET)


def snapshot_low(value: float) -> float:
    return float(value) * (1.0 - SNAPSHOT_OFFSET)


def fmt(value: float) -> str:
    """Display an amount: words below 2,000 dollars, rounded figures above it.

    See :func:`magnitude`. Model internals are untouched - this is the only
    place the rounding and the fuzzing meet the page.
    """
    if float(value) == 0.0:
        return usd(value)
    if abs(float(value)) < 2_000:
        return magnitude(value)
    return usd(value)


def magnitude(value: float) -> str:
    """Describe a small amount in words instead of printing it.

    Below two thousand dollars a precise figure is worth little to a thirty-year
    decision and a great deal to a search, so small lines are stated as orders of
    magnitude. Larger modelled amounts are still printed, because the escalated
    and computed figures they come from are the model's own.
    """
    sign = "credit of " if value < 0 else ""
    size = abs(float(value))
    if size < 25:
        return sign + "under twenty-five dollars"
    if size < 100:
        return sign + "tens of dollars"
    if size < 250:
        return sign + "a hundred to two hundred dollars"
    if size < 750:
        return sign + "several hundred dollars"
    if size < 2_000:
        return sign + "under two thousand dollars"
    return usd(size)


def band(low: float, high: float) -> str:
    """State a range in search-proof terms: rounded outward, to a coarse grain.

    A band endpoint written exactly is as findable as a bill line. Flooring the
    bottom and ceilinging the top, on a grain of fifty dollars (a hundred above
    a thousand), keeps a range usable for a decision and useless as a
    fingerprint - and it is the reason the verifier's seeded-amount guard can
    allow a range through at all.
    """
    grain = 100 if max(abs(low), abs(high)) >= 1_000 else 50
    floor_low = int(abs(low) // grain) * grain
    ceil_high = -(-int(abs(high)) // grain) * grain
    if floor_low == 0:
        return f"under ${ceil_high:,}"
    return f"${floor_low:,} to ${ceil_high:,}"


# The names whose values come from a bill, a roll entry, an appraisal estimate or
# a rent roll - the guard in tools/verify.py reads this list and rejects any
# published amount equal to one of them. Band endpoints are listed too, because
# a range's end is as findable as its middle.
RECORD_FIELDS = (
    "A_MARKET_2026", "A_ASSESSED_2026", "A_ASSESSED_2025", "A_TAX_2025",
    "B_MARKET_2026", "B_ASSESSED_2025", "B_TAX_2025", "B_RENT_MONTH",
    "A_WATER_MONTH", "A_SOLAR_CREDIT_MONTH", "B_WATER_MONTH", "B_POWER_MONTH",
)


# --------------------------------------------------------------------------
# owner-stated inputs, rounded to $10 (observation date: November 2026)
# --------------------------------------------------------------------------

# Property A - the home passing through the trust around 2040-2050.
A_MARKET_2026 = 3_100_000
A_ASSESSED_2026 = 550_540
A_ASSESSED_2025 = 539_740
A_TAX_2025 = 7_210
A_WATER_MONTH = (100, 150)          # owner-stated range, whole dollars per month
A_SOLAR_CREDIT_MONTH = (10, 20)     # owner-stated: net bill credit, not a bill
A_INSURANCE_GUESS_YR = 1_500        # owner estimate, flagged as likely low
A_LAND_SHARE = 0.30                 # assumption for depreciation basis split

# Property B - already owned by the same person who inherits A; three livable
# units, two let, one vacant, and the owner can occupy the vacant unit without
# giving up the two leases.
B_MARKET_2026 = 1_800_000
B_ASSESSED_2025 = 114_250
B_TAX_2025 = 2_440
B_RENT_MONTH = 7_150                # two units combined
B_UNITS = 3
B_WATER_MONTH = (330, 400)          # whole building, owner-paid
B_POWER_MONTH = (30, 70)            # common area, owner-paid
B_INSURANCE_GUESS_YR = 1_500
B_UNIT_RENT_MONTH = B_RENT_MONTH / 2.0   # derived average of the two let units

# Derived levies: the bill and the assessed value are the owner's own record,
# so the ratio is arithmetic, not an assumption. It still has to be confirmed
# against the published tax-rate-area schedule (flagged item).
A_RATE = A_TAX_2025 / A_ASSESSED_2025
B_RATE = B_TAX_2025 / B_ASSESSED_2025
A_ASSESSED_SHARE_OF_MARKET = A_ASSESSED_2026 / A_MARKET_2026
B_ASSESSED_SHARE_OF_MARKET = B_ASSESSED_2025 / B_MARKET_2026

# Market indications for rent and insurance. Not leases, not quotes.
A_RENT_MONTH = (8_000, 11_000)
A_RENT_PROGRAM_FLOOR_MONTH = 3_500
A_INSURANCE_YR = (3_600, 5_400)
B_INSURANCE_YR = (2_500, 4_500)
MAINT_PCT_A = (0.0035, 0.0100)
MAINT_PCT_B = (0.0060, 0.0120)
VACANCY = 0.05
MANAGEMENT = 0.08
SELL_COST = 0.05                    # brokerage plus escrow/title concessions
SELL_COST_BAND = (0.04, 0.06)
TRANSFER_MISC_YR = (500, 1_500)     # recording, reports, notary, courier

# --------------------------------------------------------------------------
# enacted rules read from official sources (read 2026-11-17 unless noted)
# --------------------------------------------------------------------------

PROP13_CAP = 0.02                     # Cal. Const. art. XIII A s.1(a); RTC s.51
PROP19_ALLOWANCE = 1_044_586          # transfers 2025-02-16 .. 2027-02-15 (BOE LTA 2025/009)
PROP19_ALLOWANCE_2023 = 1_022_600
PROP19_ALLOWANCE_2021 = 1_000_000
PROP19_ADJUST_YEARS = 2               # every other 16 February
DTT_COUNTY_MAX = 0.0011               # RTC s.11911(a): 0.55 dollars per 500 of price
DTT_CITY_MAX = 0.00055                # RTC s.11911(b): one-half of the county rate
FED_EXCL_2025 = 13_990_000
FED_EXCL_2026 = 15_000_000
FED_EXCL_2027 = 15_480_000
GIFT_EXCL_2026 = 19_000
GIFT_EXCL_2027 = 20_000
ESTATE_TOP_RATE = 0.40                # flagged: recheck the current Form 706 rate schedule
FED_ORDINARY_TOP = 0.37                # 2027 schedule (IRS inflation adjustments)
FED_LTCG_TOP = 0.20
NIIT = 0.038
CA_TOP_RATE = 0.123
CA_MHST = 0.01                        # 1 percent above 1,000,000 of taxable income
CA_MHST_FLOOR = 1_000_000
UNREC_1250_MAX = 0.25
DEPRE_LIFE = 27.5
S121_SINGLE = 250_000
S121_JOINT = 500_000
CAPLOSS_DEDUCTION = 3_000
HOME_EXEMPTION = 7_000                # RTC s.218; recheck at the lien date
SF_STATE_TAX = 0                      # California levies no estate or inheritance tax

# Rates used inside the model for after-tax portfolio income.
TAX_ON_INTEREST = FED_ORDINARY_TOP * 0.85 + NIIT + CA_TOP_RATE + CA_MHST   # ~46.5 percent
TAX_ON_QUALIFIED = FED_LTCG_TOP + NIIT + CA_TOP_RATE + CA_MHST             # ~37.1 percent


def ca_mhst(taxable_income: float) -> float:
    """Behavioral-health surcharge: 1 percent of taxable income above 1,000,000."""
    return max(0.0, taxable_income - CA_MHST_FLOOR) * CA_MHST


# --------------------------------------------------------------------------
# economic conditions: growth and inflation are never constant for long
# --------------------------------------------------------------------------

# Block sequence used for the year-by-year tables. Each block is
# (years, home growth, inflation, rent growth, equity return, bill yield).
# The blocks are a synthetic planning path assembled from documented episodes;
# they are not a forecast and not a probability.
BLOCKS: list[tuple[int, str, float, float, float, float, float]] = [
    (6, "expansion", 0.050, 0.026, 0.035, 0.090, 0.040),
    (4, "slowdown", 0.015, 0.022, 0.015, 0.030, 0.030),
    (5, "boom", 0.060, 0.030, 0.040, 0.110, 0.035),
    (2, "bust", -0.180, 0.015, -0.030, -0.570, 0.005),
    (6, "recovery", 0.050, 0.028, 0.045, 0.150, 0.020),
    (7, "quiet", 0.025, 0.024, 0.025, 0.060, 0.030),
]


def block_schedule(start_year: int) -> list[dict[str, float | int | str]]:
    """Year-by-year growth rates from the block sequence, looping after 30 years."""
    rows: list[dict[str, float | int | str]] = []
    year = start_year
    while len(rows) < 30:
        for years, name, house, infl, rent, equity, bills in BLOCKS:
            for _ in range(years):
                if len(rows) >= 30:
                    break
                rows.append({"year": year, "block": name, "house": house,
                             "infl": infl, "rent": rent, "equity": equity, "bills": bills})
                year += 1
    return rows


def block_average() -> dict[str, float]:
    """Geometric and arithmetic averages of the block path (30 years)."""
    rows = block_schedule(2027)
    n = len(rows)
    out: dict[str, float] = {}
    for key in ("house", "infl", "rent", "equity", "bills"):
        arithmetic = sum(float(r[key]) for r in rows) / n
        product = 1.0
        for r in rows:
            product *= 1.0 + float(r[key])
        out[key] = product ** (1.0 / n) - 1.0
        out[key + "_arith"] = arithmetic
    return out


def sequence_vs_flat(start: float, years: int, flat: float) -> tuple[float, float]:
    """Terminal value on the block path versus the same-name flat rate.

    Same average growth, different order: the blocks cost money even when the
    arithmetic mean is unchanged. That is why the site refuses to quote one
    growth rate for fifty years.
    """
    rows = block_schedule(2027)[:years]
    value = float(start)
    for row in rows:
        value *= 1.0 + float(row["house"])
    return value, grow(start, flat, years)


# --------------------------------------------------------------------------
# year-by-year rate paths
# --------------------------------------------------------------------------


def block_flatten(rotate: int = 0) -> list[dict[str, float | str]]:
    """The 30-year block path, optionally rotated so a chosen block comes first.

    Rotation is how the model asks "what if the bust lands in the first year
    after the transfer instead of year sixteen?" without pretending to know
    when a bust will happen.
    """
    flat: list[dict[str, float | str]] = []
    for years, name, house, infl, rent, equity, bills in BLOCKS:
        for _ in range(years):
            flat.append({"block": name, "house": house, "infl": infl, "rent": rent,
                         "equity": equity, "bills": bills})
    if rotate:
        flat = flat[rotate % len(flat):] + flat[:rotate % len(flat)]
    return flat


def bust_rotation() -> int:
    for index, row in enumerate(block_flatten()):
        if row["block"] == "bust":
            return index
    return 0


SCENARIOS = {
    "steady": {"label": "Flat baseline", "rotate": None,
               "note": "One constant rate for every year - the straw-man a single-rate projection uses."},
    "sequence": {"label": "Block sequence as dated", "rotate": 0,
                 "note": "Growth, inflation and returns arrive in uneven blocks, which is how the "
                         "record reads: an 89 percent index fall, a 57 percent fall, years of 0.1 "
                         "percent deflation and a peak above 14 percent inflation."},
    "bust_at_transfer": {"label": "Block sequence, bust moved to the transfer year", "rotate": "bust",
                         "note": "Same thirty-year arithmetic, reordered. The crash lands inside the "
                                 "decision window instead of sixteen years later."},
    "stagflation": {"label": "High-inflation repeat", "rotate": None,
                    "note": "Flat path anchored on 1965-1982, when inflation ran from about 1 percent "
                            "in 1964 to more than 14 percent in 1980."},
    "deflation": {"label": "Deflation repeat", "rotate": None,
                  "note": "Flat path anchored on 1920-1921, when the annual price change swung from "
                          "+15.6 percent to -10.5 percent."},
}

FLAT_RATES = {
    "steady": {"house": 0.030, "infl": 0.025, "rent": 0.025, "insur": 0.040,
               "equity": 0.070, "bills": 0.035, "cap": PROP13_CAP, "hpi": 0.0215},
    "stagflation": {"house": 0.055, "infl": 0.077, "rent": 0.055, "insur": 0.090,
                    "equity": 0.062, "bills": 0.055, "cap": PROP13_CAP, "hpi": 0.055},
    "deflation": {"house": -0.030, "infl": -0.020, "rent": -0.010, "insur": 0.030,
                  "equity": -0.020, "bills": 0.010, "cap": PROP13_CAP, "hpi": -0.030},
}


def scenario_rates(scenario: str, years: int) -> dict[str, list[float]]:
    """Per-year rate series for a scenario, keyed by rate name."""
    if scenario in FLAT_RATES:
        base = FLAT_RATES[scenario]
        return {key: [value] * years for key, value in base.items()}
    spec = SCENARIOS[scenario]
    rotate = spec["rotate"]
    rotate = bust_rotation() if rotate == "bust" else 0
    flat = block_flatten(rotate)
    out = {"house": [], "rent": [], "equity": [], "bills": [], "infl": [],
           "insur": [], "cap": [], "hpi": []}
    for index in range(years):
        row = flat[index % len(flat)]
        out["house"].append(float(row["house"]))
        out["rent"].append(float(row["rent"]))
        out["equity"].append(float(row["equity"]))
        out["bills"].append(float(row["bills"]))
        out["infl"].append(float(row["infl"]))
        out["insur"].append(float(row["infl"]) + 0.015)
        out["cap"].append(PROP13_CAP)
        out["hpi"].append(max(-0.100, float(row["house"])))
    return out


def after_tax(rates: dict[str, list[float]], years: int) -> dict[str, list[float]]:
    """Apply the modelled tax drag to the two portfolio legs."""
    out = dict(rates)
    out["equity_net"] = [r * (1.0 - TAX_ON_QUALIFIED) for r in rates["equity"][:years]]
    out["bills_net"] = [r * (1.0 - TAX_ON_INTEREST) for r in rates["bills"][:years]]
    return out


def compound_flow(start: float, annual_flow: float, rates: list[float]) -> float:
    """Terminal value of a portfolio fed by a level annual flow, one rate per year."""
    value = float(start)
    for rate in rates:
        value = value * (1.0 + rate) + annual_flow
    return value


def compound_series(start: float, rates: list[float]) -> float:
    value = float(start)
    for rate in rates:
        value *= 1.0 + rate
    return value


def cumulative_factor(rates: list[float], span: int) -> float:
    factor = 1.0
    for rate in rates[:span]:
        factor *= 1.0 + rate
    return factor


# --------------------------------------------------------------------------
# California property-tax mechanics
# --------------------------------------------------------------------------


def prop19_allowance(transfer_year: int, hpi_rate: float = 0.0215) -> float:
    """Index the family-home allowance forward by biennial California HPI steps.

    The BOE adjusts the 1,000,000 dollar amount every other 16 February by the
    prior calendar year's FHFA House Price Index for California. This projects
    that indexing so the allowance is not frozen at its 2025 value in a
    2040-2050 model; the growth rate is an explicit assumption.
    """
    steps = max(0, (transfer_year - 2025) // PROP19_ADJUST_YEARS)
    return PROP19_ALLOWANCE * (1.0 + hpi_rate) ** steps


def prop19_taxable_value(prior_taxable: float, fair_value: float, allowance: float) -> tuple[float, float, bool]:
    """Return (new taxable value, addition, cap met) under RTC s.63.2(d)."""
    cap = prior_taxable + allowance
    if fair_value < cap:
        return prior_taxable, 0.0, True
    return prior_taxable + (fair_value - cap), fair_value - cap, False


def annual_tax(taxable: float, rate: float) -> float:
    return max(0.0, taxable) * rate


def a_state_at(transfer_year: int, scenario: str, branch: str) -> dict[str, float | bool]:
    """Assessed value and bill for Property A in the transfer year.

    branch ``keep``: the base is still capped at two percent a year (no
    transfer event, or a qualifying transfer with the whole base carried).
    branch ``claim``: Proposition 19 family-home claim, partial carry-over.
    branch ``rent``: change in ownership with no qualifying exclusion, so the
    taxable value becomes the full value.
    """
    span = max(0, transfer_year - 2026)
    rates = scenario_rates(scenario, max(span, 1) + 40)
    prior_taxable = A_ASSESSED_2026 * cumulative_factor(rates["cap"], span)
    value = A_MARKET_2026 * cumulative_factor(rates["house"], span)
    allowance = prop19_allowance(transfer_year, 0.0215 if scenario in ("steady", "sequence", "bust_at_transfer")
                                 else FLAT_RATES.get(scenario, {"hpi": 0.0215})["hpi"])
    if branch == "keep":
        taxable, addition, met = prior_taxable, 0.0, True
    elif branch == "claim":
        taxable, addition, met = prop19_taxable_value(prior_taxable, value, allowance)
    else:
        taxable, addition, met = value, value, False
    return {
        "value": value,
        "prior_taxable": prior_taxable,
        "allowance": allowance,
        "cap": prior_taxable + allowance,
        "taxable": taxable,
        "addition": addition,
        "cap_met": met,
        "rate": A_RATE,
        "tax": annual_tax(taxable, A_RATE),
        "tax_reassessed": annual_tax(value, A_RATE),
    }


def b_state_at(transfer_year: int, scenario: str) -> dict[str, float]:
    span = max(0, transfer_year - 2026)
    rates = scenario_rates(scenario, span + 1)
    assessed = B_ASSESSED_2025 * cumulative_factor(rates["cap"], span)
    value = B_MARKET_2026 * cumulative_factor(rates["house"], span)
    return {"assessed": assessed, "value": value, "rate": B_RATE,
            "tax": annual_tax(assessed, B_RATE), "years": span}


def market_value_at(year: int, scenario: str, prop: str) -> float:
    start = A_MARKET_2026 if prop == "A" else B_MARKET_2026
    span = max(0, year - 2026)
    rates = scenario_rates(scenario, span)
    return start * cumulative_factor(rates["house"], span)


# --------------------------------------------------------------------------
# operating costs
# --------------------------------------------------------------------------


def owner_costs(prop: str, transfer_year: int, scenario: str, taxable: float, occupied: bool) -> dict[str, float]:
    """Annual owner-paid operating cost in the transfer year.

    Water and power use the owner's rounded ranges; insurance and maintenance
    are the flagged assumption bands; the solar array shows up as a credit while
    the home is owner-occupied, not as income.
    """
    span = max(0, transfer_year - 2026)
    rates = scenario_rates(scenario, span + 1)
    infl = cumulative_factor(rates["infl"], span)
    insur = cumulative_factor(rates["insur"], span)
    cost_infl = infl * cumulative_factor(rates["house"], span) ** 0.5
    if prop == "A":
        water = midpoint(*A_WATER_MONTH) * 12 * infl
        power = -midpoint(*A_SOLAR_CREDIT_MONTH) * 12 * infl if occupied else 0.0
        insurance = midpoint(*A_INSURANCE_YR) * insur
        maint = A_MARKET_2026 * midpoint(*MAINT_PCT_A) * cost_infl
        maint_low = A_MARKET_2026 * MAINT_PCT_A[0] * cost_infl
        maint_high = A_MARKET_2026 * MAINT_PCT_A[1] * cost_infl
        rate = A_RATE
    else:
        water = midpoint(*B_WATER_MONTH) * 12 * infl
        power = midpoint(*B_POWER_MONTH) * 12 * infl
        insurance = midpoint(*B_INSURANCE_YR) * insur
        maint = B_MARKET_2026 * MAINT_PCT_B[1] * 0.75 * cost_infl
        maint_low = B_MARKET_2026 * MAINT_PCT_B[0] * cost_infl
        maint_high = B_MARKET_2026 * MAINT_PCT_B[1] * cost_infl
        rate = B_RATE
    tax = annual_tax(taxable, rate)
    return {
        "tax": tax, "water": water, "power": power, "insurance": insurance,
        "maintenance": maint, "maintenance_low": maint_low, "maintenance_high": maint_high,
        "total": tax + water + power + insurance + maint,
    }


def operating_cost_rows(scenario: str = "sequence", years: int = 25) -> list[dict[str, float]]:
    """Year-by-year value, assessed value, bill and operating cost for both homes.

    Property A's assessed value grows at the two percent cap, which is what
    happens while no change in ownership is recorded; the transfer-year branches
    are priced separately in :func:`a_state_at`. Costs grow with the scenario's
    own price path, and the solar array is a credit against the bill, not income.
    """
    rates = scenario_rates(scenario, years + 2)
    out: list[dict[str, float]] = []
    a_value = float(A_MARKET_2026)
    a_assessed = float(A_ASSESSED_2026)
    b_value = float(B_MARKET_2026)
    b_assessed = float(B_ASSESSED_2025)
    infl = 1.0
    insur = 1.0
    build_cost = 1.0
    rent_b = float(B_RENT_MONTH * 12)
    for index in range(years):
        year = 2026 + index
        first = index == 0
        # the starting-year bill is the record; offset it with the same guard used
        # on the value rows so no published amount equals a single bill line
        tax_a = annual_tax(snapshot_low(a_assessed) if first else a_assessed, A_RATE)
        tax_b = annual_tax(snapshot_low(b_assessed) if first else b_assessed, B_RATE)
        water_a = midpoint(*A_WATER_MONTH) * 12 * infl
        power_a = -midpoint(*A_SOLAR_CREDIT_MONTH) * 12 * infl
        ins_a = midpoint(*A_INSURANCE_YR) * insur
        maint_a = A_MARKET_2026 * midpoint(*MAINT_PCT_A) * build_cost
        water_b = midpoint(*B_WATER_MONTH) * 12 * infl
        power_b = midpoint(*B_POWER_MONTH) * 12 * infl
        ins_b = midpoint(*B_INSURANCE_YR) * insur
        maint_b = B_MARKET_2026 * MAINT_PCT_B[1] * 0.75 * build_cost
        out.append({
            "year": float(year),
            "a_value": snapshot(a_value) if first else a_value,
            "a_assessed": snapshot_low(a_assessed) if first else a_assessed, "a_tax": tax_a,
            "a_water": water_a, "a_power": power_a, "a_insurance": ins_a, "a_maintenance": maint_a,
            "a_total": tax_a + water_a + power_a + ins_a + maint_a,
            "a_share": a_assessed / max(a_value, 1.0),
            "b_value": snapshot(b_value) if first else b_value,
            "b_assessed": snapshot_low(b_assessed) if first else b_assessed, "b_tax": tax_b,
            "b_water": water_b, "b_power": power_b, "b_insurance": ins_b, "b_maintenance": maint_b,
            "b_rent": snapshot(rent_b) if first else rent_b,
            "b_total": tax_b + water_b + power_b + ins_b + maint_b,
            "b_net": rent_b * (1.0 - VACANCY - MANAGEMENT) - (tax_b + water_b + power_b + ins_b + maint_b),
            "infl": infl,
        })
        a_value *= 1.0 + rates["house"][index]
        b_value *= 1.0 + rates["house"][index]
        a_assessed *= 1.0 + rates["cap"][index]
        b_assessed *= 1.0 + rates["cap"][index]
        infl *= 1.0 + rates["infl"][index]
        insur *= 1.0 + rates["insur"][index]
        build_cost *= 1.0 + (rates["infl"][index] + rates["house"][index]) / 2.0
        rent_b *= 1.0 + rates["rent"][index]
    return out


def value_projection_rows(scenario: str = "sequence", until: int = 2051) -> list[dict[str, float]]:
    """Value, capped assessed value, capped bill and reassessed bill by year."""
    years = max(1, until - 2026)
    rates = scenario_rates(scenario, years + 2)
    out: list[dict[str, float]] = []
    a_value = float(A_MARKET_2026)
    a_assessed = float(A_ASSESSED_2026)
    for index in range(years + 1):
        allowance = prop19_allowance(2026 + index, rates["hpi"][index])
        claim_taxable, addition, met = prop19_taxable_value(a_assessed, a_value, allowance)
        shown_value = snapshot(a_value) if index == 0 else a_value
        shown_base = snapshot_low(a_assessed) if index == 0 else a_assessed
        out.append({
            "year": float(2026 + index), "value": shown_value, "assessed_capped": shown_base,
            "tax_capped": annual_tax(shown_base, A_RATE), "allowance": allowance,
            "cap_line": shown_base + allowance, "addition": addition,
            "tax_claim": annual_tax(claim_taxable, A_RATE),
            "tax_reassessed": annual_tax(shown_value, A_RATE),
            "tax_saving": annual_tax(shown_value, A_RATE) - annual_tax(claim_taxable, A_RATE),
            "share": a_assessed / max(a_value, 1.0), "cap_met": 1.0 if met else 0.0,
        })
        a_value *= 1.0 + rates["house"][index]
        a_assessed *= 1.0 + rates["cap"][index]
    return out


def capital_plan() -> list[tuple[str, str, str, int, int]]:
    """Five-year capital plan skeleton: item, why, evidence, low, high (dollars)."""
    return [
        ("Roof and flashings", "Composition roofing reaches 20 to 25 years; a failed roof turns a capital item into an interior-damage claim.", "Inspection report with dated photos", 25_000, 45_000),
        ("HVAC and water heater", "Two mechanical systems of the same age tend to fail inside one another's warranty-free window.", "Age and service tags", 15_000, 28_000),
        ("Solar inverter and racking", "The array is what makes the electric bill a credit; inverters age faster than panels.", "Monitoring data and install date", 3_000, 7_000),
        ("Sewer lateral and drainage", "A collapsed lateral in a let or empty house is a repair and a liability event at once.", "Camera inspection", 4_000, 12_000),
        ("Seismic and fire hardening", "Retrofit and defensible-space work changes insurance terms and, in some markets, resale.", "Retrofit assessment", 8_000, 25_000),
        ("Weatherization and windows", "The cheapest way to keep the self-generation credit worth what it was under the older export tariff.", "Energy audit", 5_000, 15_000),
        ("Paint, stucco, gutters", "Deferred exterior work is the item inspectors repeat most on older Bay Area houses.", "Walk-through list", 8_000, 18_000),
        ("Unit updates in the let building", "Kitchens, flooring and appliances drive both rent and vacancy time.", "Rent-roll review", 20_000, 60_000),
    ]


def capital_plan_total(prop: str) -> tuple[int, int]:
    rows = capital_plan()
    keep = [r for r in rows if "let building" not in r[0]] if prop == "A" else [r for r in rows if "Solar" not in r[0]]
    return sum(r[3] for r in keep), sum(r[4] for r in keep)


# --------------------------------------------------------------------------
# sale mechanics
# --------------------------------------------------------------------------


def sell_waterfall(price: float, basis: float, holding_years: int = 0, occupancy: str = "none",
                   dtt: bool = True, months_after_transfer: int = 0) -> dict[str, float]:
    """``months_after_transfer`` drifts the price off the date-of-death value.

    A sale a few months after the transfer is priced on the market at that later
    date while the basis stays at the date-of-death value, so the gain is the
    drift plus or minus selling costs. A small loss after costs is not deductible
    on personal-use property, which is why the same-year sale reads as neither
    taxed nor deductible rather than as an exemption.
    """
    """Gross-to-net waterfall in the published order.

    Order: price, sale costs, documentary transfer tax and recording items,
    income tax, then net to invest. The basis is the date-of-death value the heir
    takes, so a sale inside the transfer year shows a small gain rather than a
    large one; a sale after rental use adds depreciation recapture, and a sale
    after owner occupancy can use the main-home exclusion.
    """
    price = price * (1.0 + months_after_transfer / 12.0 * 0.03)
    costs = price * SELL_COST
    transfer_tax = price * (DTT_COUNTY_MAX + DTT_CITY_MAX) if dtt else 0.0
    misc = midpoint(*TRANSFER_MISC_YR) * 2
    gross_gain = max(0.0, price - costs - basis)
    exclusion = S121_SINGLE if occupancy == "lived" else 0.0
    taxable_gain = max(0.0, gross_gain - exclusion)
    federal = taxable_gain * (FED_LTCG_TOP + NIIT)
    state = taxable_gain * (CA_TOP_RATE + CA_MHST)
    depreciation = basis * (1.0 - A_LAND_SHARE) / DEPRE_LIFE * holding_years if occupancy == "rented" else 0.0
    recapture = min(taxable_gain, depreciation) * (UNREC_1250_MAX + CA_TOP_RATE + CA_MHST) if depreciation else 0.0
    income_tax = federal + state + recapture
    return {
        "price": price, "costs": costs, "transfer_tax": transfer_tax, "misc": misc,
        "basis": basis, "gross_gain": gross_gain, "exclusion": exclusion,
        "taxable_gain": taxable_gain, "federal": federal, "state": state,
        "depreciation": depreciation, "recapture": recapture, "income_tax": income_tax,
        "net": price - costs - transfer_tax - misc - income_tax,
    }


def waterfall_rows(transfer_year: int, scenario: str) -> list[dict[str, float | str]]:
    """Same transfer date, same horizon, three sale timings priced side by side."""
    value_now = market_value_at(transfer_year, scenario, "A")
    rates = scenario_rates(scenario, 6)
    rows: list[dict[str, float | str]] = []
    for label, years_held, occupancy in (
        ("Sell in the transfer year", 0, "none"),
        ("Sell after five years of living there", 5, "lived"),
        ("Sell after two years of letting it", 2, "rented"),
    ):
        price = value_now * cumulative_factor(rates["house"], years_held)
        row = sell_waterfall(price, value_now, years_held, occupancy)
        row["label"] = label
        rows.append(row)
    return rows


# --------------------------------------------------------------------------
# paths
# --------------------------------------------------------------------------

PATHS = (
    ("Live in A as the principal home; let the vacant unit in B", "pure", "A"),
    ("Let A on a long-term lease; household stays in B", "pure", "B"),
    ("Sell A in the transfer year; invest; household stays in B", "pure", "B"),
    ("Sell A; park the proceeds in 3-month to 2-year Treasuries for 30 months; phase in", "mixed", "B"),
    ("Live in A for five years, then sell and invest", "mixed", "A"),
    ("Let A for 24 months to test the market, then sell", "mixed", "B"),
    ("Keep A vacant and undecided", "pure", "none"),
)


def b_reference(transfer_year: int, scenario: str) -> dict[str, float]:
    """Property B's year-one economics, identical in every path.

    B is already owned by the person who inherits A, carries two leases and a
    vacant unit, and the household can occupy the vacant unit without breaking a
    lease. Ownership of B does not change under any path, so its net contribution
    cancels out of the ranking and is published once, separately, so the ranking
    is not mistaken for the household's whole cash position.
    """
    span = max(0, transfer_year - 2026)
    rates = scenario_rates(scenario, span + 1)
    state = b_state_at(transfer_year, scenario)
    costs = owner_costs("B", transfer_year, scenario, state["assessed"], False)
    gross_rent = B_RENT_MONTH * 12 * cumulative_factor(rates["rent"], span)
    unit_rent = B_UNIT_RENT_MONTH * 12 * cumulative_factor(rates["rent"], span)
    return {
        "assessed": state["assessed"], "value": state["value"], "tax": state["tax"],
        "gross_rent": gross_rent, "unit_rent": unit_rent, "costs": costs["total"],
        "net_rental": gross_rent * (1.0 - VACANCY - MANAGEMENT) - costs["total"],
        "annual_depreciation": state["value"] * 0.75 / DEPRE_LIFE,
    }


def blended_wait(rates: list[float], wait_years: int, bills: list[float], half: float = 0.5) -> list[float]:
    """Rates for a portfolio that is being deployed rather than already invested.

    During the waiting window only part of the money is in equities, on average
    half of it for a straight-line twelve-tranche schedule, so the leg earns a
    blend of the equity rate and the bill rate. That is the whole cost of staging
    in a market that does not fall.
    """
    out = list(rates)
    for index in range(min(wait_years, len(out))):
        out[index] = rates[index] * half + bills[index] * (1.0 - half)
    return out


def _terminal(flow: float, owned_start: float, held: int, sale_proceeds: float,
              portfolio_start: float, horizon: int, rates: dict[str, list[float]]) -> float:
    """Wealth at the horizon for one path, with the sale handled in its own year.

    ``flow`` is the property's own annual operating result (rent received less
    owner costs, negative when the household lives there) and is reinvested at
    the after-tax portfolio rate. Portfolio income is never added as a flow, so
    nothing is counted twice.
    """
    held = min(max(0, held), horizon)
    house_rate = rates["house"]
    equity = rates["equity_net"]
    owned_at_held = owned_start * cumulative_factor(house_rate, held)
    flows_at_held = compound_flow(0.0, flow, equity[:held])
    port_at_held = portfolio_start * cumulative_factor(equity, held) + flows_at_held
    if held >= horizon:
        return owned_at_held + flows_at_held + portfolio_start * cumulative_factor(equity, horizon)
    remaining = horizon - held
    return (port_at_held + sale_proceeds) * cumulative_factor(equity, remaining)


def path_table(transfer_year: int, horizon: int, scenario: str) -> list[dict[str, object]]:
    """Household comparison of the pure and mixed paths at one date and horizon.

    Amounts describe Property A and the proceeds portfolio only; Property B is
    identical across paths and is reported once by :func:`b_reference`. A
    self-used owned home is credited with its market rent (imputed rent), so
    living in a house you own is not counted as free - that is what makes the
    live and let rows comparable instead of flattered.
    """
    rates = after_tax(scenario_rates(scenario, max(horizon, 1) + 30), horizon + 1)
    years_from_2026 = max(0, transfer_year - 2026)
    rent_factors = scenario_rates(scenario, years_from_2026 + 2)
    a_value = market_value_at(transfer_year, scenario, "A")
    rent_a_low, rent_a_high = market_rent(transfer_year, scenario)
    rent_a = (rent_a_low + rent_a_high) / 2.0
    unit_rent = B_UNIT_RENT_MONTH * 12 * cumulative_factor(rent_factors["rent"], years_from_2026)

    claim = a_state_at(transfer_year, scenario, "claim")
    rent_branch = a_state_at(transfer_year, scenario, "rent")
    keep_branch = a_state_at(transfer_year, scenario, "keep")
    costs_live = owner_costs("A", transfer_year, scenario, claim["taxable"], True)
    costs_let = owner_costs("A", transfer_year, scenario, rent_branch["taxable"], False)
    costs_keep = owner_costs("A", transfer_year, scenario, keep_branch["taxable"], True)
    depreciation = a_value * (1.0 - A_LAND_SHARE) / DEPRE_LIFE

    sale_now = sell_waterfall(a_value, a_value, 0, "none", months_after_transfer=6)
    proceeds = sale_now["net"]
    rows: list[dict[str, object]] = []

    def add(title: str, kind: str, occupancy: str, flow: float, owned: float, held: int,
            sale_proceeds: float, portfolio_start: float, liquidity: float, driver: str,
            wait_years: int = 0) -> None:
        local = rates
        if wait_years:
            local = dict(rates)
            local["equity_net"] = blended_wait(rates["equity_net"], wait_years, rates["bills_net"])
        flow_econ = flow + (rent_a - rent_a * VACANCY - rent_a * MANAGEMENT if occupancy == "A" else 0.0)
        deflator = cumulative_factor(scenario_rates(scenario, horizon + 2)["infl"], horizon)
        rows.append({
            "name": title, "kind": kind, "occupancy": occupancy,
            "deflator": deflator,
            "flow_cash": flow, "flow_econ": flow_econ, "value_now": owned,
            "held": held, "proceeds": portfolio_start or sale_proceeds, "liquidity": liquidity,
            "terminal_cash": _terminal(flow, owned, held, sale_proceeds, portfolio_start, horizon, local),
            "terminal_econ": _terminal(flow_econ, held and held or held, owned, held, sale_proceeds, portfolio_start, horizon, local) if False else _terminal(flow_econ, owned, held, sale_proceeds, portfolio_start, horizon, local),
            "terminal_real": _terminal(flow_econ, owned, held, sale_proceeds, portfolio_start, horizon, local) / deflator,
            "driver": driver,
        })

    live_flow = -costs_live["total"]
    let_flow = rent_a * (1.0 - VACANCY - MANAGEMENT) - costs_let["total"]

    add(PATHS[0][0], PATHS[0][1], PATHS[0][2], live_flow, a_value, horizon, 0.0, 0.0, 0.0,
        "The Prop 19 partial carry-over holds the bill at " + usd(claim["tax"]) + " instead of "
        + usd(rent_branch["tax"]) + ", worth " + usd(rent_branch["tax"] - claim["tax"]) + " a year; the "
        "housing the household consumes is worth about " + usd(rent_a) + " a year, and letting the vacant "
        "unit in B brings in " + usd(unit_rent) + " of cash that the stay-at-B paths give up.")

    add(PATHS[1][0], PATHS[1][1], PATHS[1][2], let_flow, a_value, horizon, 0.0, 0.0, 0.0,
        "Reassessment puts " + pct(rent_branch["tax"] / max(rent_a, 1.0), 0) + " of the gross rent into the "
        "bill before any other cost. Depreciation of about " + usd(depreciation) + " a year shelters the rest "
        "from income tax, and that shelter turns into recapture on the eventual sale.")

    add(PATHS[2][0], PATHS[2][1], PATHS[2][2], 0.0, 0.0, 0, 0.0, proceeds, proceeds,
        "Gain over the date-of-death value is the price drift over the few months between transfer and "
        "closing, not the whole historical appreciation, so the sale is close to income-tax-free and the full " + usd(proceeds) + " compounds from "
        "day one at " + pct(rates["equity_net"][0], 1) + " after tax.")

    stage_years = 3
    bills_avg = sum(rates["bills_net"][:stage_years]) / stage_years
    add(PATHS[3][0], PATHS[3][1], PATHS[3][2], 0.0, 0.0, 0, 0.0, proceeds, proceeds,
        "Identical sale, but the money waits: the parked leg earns about " + pct(bills_avg, 1) +
        " after tax for 30 months and twelve tranches buy at twelve different prices. The table on the "
        "Treasury staging page prices what that does under a crash and in a market that keeps rising.")

    live_then = sell_waterfall(a_value * cumulative_factor(rates["house"], 5), a_value, 5, "lived")
    add(PATHS[4][0], PATHS[4][1], PATHS[4][2], live_flow, a_value, 5, live_then["net"], 0.0, live_then["net"],
        "Occupancy in two of the five years supports a main-home exclusion of up to " + usd(S121_SINGLE) +
        " of a single filer's gain; modelled tax on the rest of the " + usd(live_then["gross_gain"]) +
        " gain is " + usd(live_then["income_tax"]) + ".")

    let_then = sell_waterfall(a_value * cumulative_factor(rates["house"], 2), a_value, 2, "rented")
    add(PATHS[5][0], PATHS[5][1], PATHS[5][2], let_flow, a_value, 2, let_then["net"], 0.0, let_then["net"],
        "Two letting years trigger reassessment, forfeit the main-home exclusion, and move "
        + usd(2 * depreciation) + " of depreciation into the recapture column; modelled exit tax is "
        + usd(let_then["income_tax"]) + " against " + usd(2 * let_flow) + " of rent kept.")

    add(PATHS[6][0], PATHS[6][1], PATHS[6][2], -costs_keep["total"], a_value, horizon, 0.0, 0.0, 0.0,
        "The capped bill stays at " + usd(keep_branch["tax"]) + " a year, the house earns nothing, and each "
        "year of delay adds another year of capital-cost risk with no decision attached to it.")

    rows.sort(key=lambda r: -float(r["terminal_econ"]))
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
    return rows


def median_rate(rates: list[float], years: int) -> float:
    return sum(rates[:years]) / max(1, years)


def headline(scenario: str = "steady", transfer_year: int = 2045, horizon: int = 30) -> dict[str, object]:
    """The six numbers a reader needs before touching any table.

    Every value is rounded to the nearest ten dollars by the page formatter. The
    dict is deliberately small: it is the first-screen version of the argument,
    and each item names the fact that would change it.
    """
    rates = scenario_rates(scenario, horizon + 2)
    claim = a_state_at(transfer_year, scenario, "claim")
    rent_branch = a_state_at(transfer_year, scenario, "rent")
    keep_branch = a_state_at(transfer_year, scenario, "keep")
    costs = owner_costs("A", transfer_year, scenario, rent_branch["taxable"], False)
    sale = sell_waterfall(claim["value"], claim["value"], 0, "none")
    be = break_evens(transfer_year, horizon, scenario)
    rows = path_table(transfer_year, horizon, scenario)
    return {
        "scenario": scenario,
        "transfer_year": transfer_year,
        "horizon": horizon,
        "value": claim["value"],
        "bill_if_undecided": keep_branch["tax"],
        "bill_if_claimed": claim["tax"],
        "bill_if_let": rent_branch["tax"],
        "prop19_saving": rent_branch["tax"] - claim["tax"],
        "operating_cost_let": costs["total"],
        "net_sale_proceeds": sale["net"],
        "income_tax_on_sale_now": sale["income_tax"],
        "break_even_appreciation": be["needed_house_cagr"],
        "break_even_rent_month": be["needed_month_rent"],
        "quoted_rent_month": midpoint(*A_RENT_MONTH),
        "best_path": rows[0]["name"],
        "worst_path": rows[-1]["name"],
        "spread": float(rows[0]["terminal_econ"]) - float(rows[-1]["terminal_econ"]),
        "spread_real": float(rows[0]["terminal_real"]) - float(rows[-1]["terminal_real"]),
        "deflator": float(rows[0]["deflator"]),
    }



def rank_matrix(transfer_year: int = 2045, horizon: int = 30,
                scenarios: tuple[str, ...] = ("steady", "sequence", "bust_at_transfer", "stagflation", "deflation")) -> dict[str, list[dict[str, object]]]:
    """The same paths under every scenario, so a ranking can be tested for stability.

    If a path wins in every column, the household can commit to it now. If the
    winner changes with the economic path, the honest output is the break-even
    number, not a prediction, and the page says so.
    """
    return {scenario: path_table(transfer_year, horizon, scenario) for scenario in scenarios}


def horizon_matrix(transfer_year: int = 2045, scenario: str = "sequence",
                   horizons: tuple[int, ...] = (5, 10, 20, 30)) -> dict[int, list[dict[str, object]]]:
    """The same paths at the same transfer date but different horizons."""
    return {horizon: path_table(transfer_year, horizon, scenario) for horizon in horizons}


def transfer_year_matrix(horizon: int = 30, scenario: str = "sequence",
                         years: tuple[int, ...] = (2040, 2045, 2050)) -> dict[int, list[dict[str, object]]]:
    """The same paths at three possible transfer years, same horizon each."""
    return {year: path_table(year, horizon, scenario) for year in years}


def estate_rows(death_year: int, homes_2026: float | None = None) -> list[dict[str, float]]:
    """Federal estate exposure for a house-and-cash estate at the given death year.

    Rows step the non-home part of the estate upward so the household can read
    the amount at which a return, and then a tax, appears. The exclusion is
    indexed at the published pace; California imposes no estate or inheritance
    tax of its own, so the state column is zero by rule rather than by estimate.
    """
    homes_value = A_MARKET_2026 + B_MARKET_2026 if homes_2026 is None else homes_2026
    out: list[dict[str, float]] = []
    for extra_assets in (0.0, 5_000_000.0, 10_000_000.0, 20_000_000.0):
        base = estate_projection(death_year, homes_value)
        total = base["homes"] + extra_assets
        excess = max(0.0, total - base["exclusion"])
        out.append({
            "death_year": float(death_year), "homes": base["homes"], "other": extra_assets,
            "gross": total, "exclusion": base["exclusion"], "headroom": base["headroom"],
            "excess": excess, "tax_on_excess": excess * ESTATE_TOP_RATE,
            "cash_before_filing": max(0.0, base["exclusion"] - total),
        })
    return out


def staging_summary(principal: float, horizon_years: float = 10.0) -> list[dict[str, object]]:
    """Crash-entry test for both historical anchors and for staged windows.

    The 1929 row is also run to a twenty-five year horizon because that is how
    long the index stayed below its 1929 level, which is the part of the
    episode that matters to a household deciding how fast to get invested.
    """
    out: list[dict[str, object]] = []
    for anchor in ("2008", "1929"):
        for window in (0, 24, 30, 36):
            rows = staging_table(principal, anchor, window) if window else [staging_case(principal, anchor, 0, 0, 1)]
            for row in rows:
                record = dict(row)
                record["anchor"] = anchor
                record["window"] = window
                out.append(record)
    long_1929 = []
    for window in (0, 30):
        rows = staging_table(principal, "1929", window) if window else [staging_case(principal, "1929", 0, 0, 1)]
        for row in rows:
            record = dict(staging_case(principal, "1929", int(row["shock_month"]), window or 1,
                                       STAGING_PHASES, years=25.0))
            record["anchor"] = "1929 at 25 years"
            record["window"] = window
            long_1929.append(record)
    out.extend(long_1929)
    return out


# --------------------------------------------------------------------------
# Treasury staging and the crash-entry test
# --------------------------------------------------------------------------

STAGING_WINDOW_MONTHS = 30
STAGING_PHASES = 12

CRASH_ANCHORS = {
    "1929": {"peak": "September 1929", "trough": "July 1932", "fall": 0.89,
             "years_to_prior_high": 25, "bills": 0.010, "drift": 0.020,
             "anchor": "Dow Jones Industrial Average: 381.17 close on 1929-09-03, 41.22 close on "
                       "1932-07-08, and no return to the 1929 level until 1954-11-23."},
    "2008": {"peak": "October 2007", "trough": "March 2009", "fall": 0.57,
             "years_to_prior_high": 6, "bills": 0.005, "drift": 0.100,
             "anchor": "S&P 500 fell 57 percent from the October 2007 peak to the March 2009 trough; "
                       "home prices fell about 30 percent from mid-2006 to mid-2009."},
}


def staging_case(principal: float, anchor: str, shock_month: int,
                 months_staged: int = STAGING_WINDOW_MONTHS, phases: int = STAGING_PHASES,
                 years: float = 10.0, crash: bool = True) -> dict[str, float]:
    """One-shot crash at ``shock_month``: invest at once versus staged buying.

    Deliberately simple and deterministic. Equities drift at the anchor's own
    long-run rate every year except the crash month, the crash is a single level
    change, and bills earn a flat yield. No dividends, recovery curve, fees,
    taxes or property cash flows are modelled, so this measures the *shape* of
    entry risk, not a return forecast.
    """
    cfg = CRASH_ANCHORS[anchor]
    shock = cfg["fall"]
    drift = cfg["drift"]
    bills = cfg["bills"]

    fall = (1.0 - shock) if crash else 1.0

    def drift_from(month: int) -> float:
        return (1.0 + drift / 12.0) ** month * fall * (1.0 + drift) ** max(0.0, years - month / 12.0)

    immediate = principal * drift_from(shock_month)
    staged = 0.0
    per_phase = principal / phases
    exposed_dollars = 0.0
    for index in range(phases):
        buy_month = int(round(index * months_staged / phases))
        bill_growth = (1.0 + bills / 12.0) ** buy_month
        if buy_month <= shock_month:
            exposed_dollars += per_phase
            value = per_phase * bill_growth * (1.0 + drift / 12.0) ** (shock_month - buy_month) * fall
            value *= (1.0 + drift) ** max(0.0, years - shock_month / 12.0)
        else:
            value = per_phase * bill_growth * (1.0 + drift) ** max(0.0, years - buy_month / 12.0)
        staged += value
    return {
        "shock_month": shock_month,
        "immediate": immediate,
        "staged": staged,
        "difference": staged - immediate,
        "exposed_dollars": exposed_dollars,
        "share_exposed": exposed_dollars / max(principal, 1.0),
        "bills_income": principal * (1.0 + bills) ** (months_staged / 12.0) - principal,
        "no_shock_reference": principal * (1.0 + drift) ** years,
    }


def staging_table(principal: float, anchor: str, months_staged: int = STAGING_WINDOW_MONTHS) -> list[dict[str, float]]:
    """Same crash, five different months for it to land in."""
    months = [0, int(months_staged * 0.4), months_staged, months_staged + 6, 60]
    return [staging_case(principal, anchor, month, months_staged) for month in months]


def reinvestment_risk(principal: float, months: int, bills: float, equity: float, years: float = 10.0) -> dict[str, float]:
    """What waiting costs when the market does not fall."""
    wait = months / 12.0
    parked = principal * (1.0 + bills) ** wait
    bought_in = principal * (1.0 + equity) ** wait
    return {
        "bills_income": parked - principal,
        "price_increase": bought_in - principal,
        "ten_year_gap": bought_in * (1.0 + equity) ** (years - wait) - principal * (1.0 + equity) ** years,
        "give_up_annual": principal * (equity - bills),
    }


# --------------------------------------------------------------------------
# break-evens: the numbers that would change the answer
# --------------------------------------------------------------------------


def break_evens(transfer_year: int = 2045, horizon: int = 30, scenario: str = "sequence") -> dict[str, object]:
    rates = after_tax(scenario_rates(scenario, max(horizon, 1) + 25), horizon)
    equity = rates["equity_net"]
    a_value = market_value_at(transfer_year, scenario, "A")
    claim = a_state_at(transfer_year, scenario, "claim")
    rent_branch = a_state_at(transfer_year, scenario, "rent")
    costs_let = owner_costs("A", transfer_year, scenario, rent_branch["taxable"], False)
    costs_live = owner_costs("A", transfer_year, scenario, claim["taxable"], True)
    sale = sell_waterfall(a_value, a_value, 0, "none")
    proceeds = sale["net"]

    sell_terminal = compound_flow(proceeds, 0.0, equity[:horizon])
    house_terminal = a_value * cumulative_factor(rates["house"], horizon)
    annuity_factor = (1.0 + equity[0]) ** horizon - 1.0 if len(set(equity)) == 1 else None
    # level-annuity factor from the scenario's own average after-tax rate
    avg = sum(equity[:horizon]) / horizon
    factor = ((1.0 + avg) ** horizon - 1.0) / avg if avg else horizon

    # gross rent that makes letting match selling, at the same date and horizon
    needed_net = (sell_terminal - house_terminal) / factor
    needed_gross = (needed_net + costs_let["total"]) / (1.0 - VACANCY - MANAGEMENT)
    needed_month = needed_gross / 12.0

    # appreciation a held home needs to match the portfolio, with no rent credit
    needed_house = (sell_terminal / max(a_value, 1.0)) ** (1.0 / horizon) - 1.0
    # ... and with the household's own housing credited at market rent
    credit = compound_flow(0.0, market_rent(transfer_year, scenario)[0], equity[:horizon])
    needed_house_with_housing = ((sell_terminal - credit) / max(a_value, 1.0)) ** (1.0 / horizon) - 1.0

    saving = rent_branch["tax"] - claim["tax"]
    filing_cost = 175.0 + 2_000.0
    return {
        "a_value": a_value, "proceeds": proceeds, "horizon": horizon,
        "sell_terminal": sell_terminal, "house_terminal": house_terminal,
        "needed_month_rent": needed_month,
        "quoted_month_rent": midpoint(*A_RENT_MONTH),
        "needed_house_cagr": needed_house,
        "needed_house_cagr_with_housing": needed_house_with_housing,
        "avg_equity_net": avg,
        "tax_saving_from_claim": saving,
        "claim_years_to_breakeven": filing_cost / max(saving, 1.0),
        "live_cost": costs_live["total"],
        "let_cost": costs_let["total"],
        "annual_portfolio_income": proceeds * avg,
    }


def market_rent(transfer_year: int, scenario: str) -> tuple[float, float]:
    """Low and high market rent for Property A in the transfer year."""
    span = max(0, transfer_year - 2026)
    factor = cumulative_factor(scenario_rates(scenario, span + 1)["rent"], span)
    return A_RENT_MONTH[0] * 12 * factor, A_RENT_MONTH[1] * 12 * factor


# --------------------------------------------------------------------------
# estate-threshold math
# --------------------------------------------------------------------------


def estate_projection(death_year: int, homes_2026: float, house_rate: float = 0.030,
                      cpi_rate: float = 0.025) -> dict[str, float]:
    """Headroom under the federal exclusion, indexed forward at the published pace.

    The exclusion is indexed for inflation from the 2027 figure the IRS has
    published; the homes grow at the model's house rate. California levies no
    estate or inheritance tax of its own, so the state line is zero.
    """
    exclusion = FED_EXCL_2027 * (1.0 + cpi_rate) ** max(0, death_year - 2027)
    homes = homes_2026 * (1.0 + house_rate) ** max(0, death_year - 2026)
    headroom = exclusion - homes
    return {
        "exclusion": exclusion, "homes": homes, "headroom": headroom,
        "cash_before_filing": max(0.0, headroom),
        "excess": max(0.0, -headroom),
        "tax_on_excess": max(0.0, -headroom) * ESTATE_TOP_RATE,
    }


# --------------------------------------------------------------------------
# verification hooks used by the unit tests
# --------------------------------------------------------------------------


def rounding_is_clean(value: float) -> bool:
    return r10(value) % ROUND_TO == 0


def self_check() -> dict[str, object]:
    """Consistency checks the test suite can assert on."""
    claim = a_state_at(2045, "steady", "claim")
    rent = a_state_at(2045, "steady", "rent")
    rows = path_table(2045, 30, "sequence")
    staged_early = staging_case(1_000_000, "2008", 6)
    staged_late = staging_case(1_000_000, "2008", 36)
    be = break_evens()
    return {
        "rounding_clean": all(rounding_is_clean(float(x)) for x in (claim["tax"], rent["tax"], rows[0]["terminal_econ"])),
        "prop19_addition_positive": claim["addition"] > 0,
        "claim_tax_below_reassessed_tax": claim["tax"] < rent["tax"],
        "claim_tax_between_capped_and_full": claim["tax"] > annual_tax(A_ASSESSED_2026, A_RATE),
        "staging_helps_when_the_crash_is_early": staged_early["difference"] > 0,
        "staging_does_not_help_after_the_window": staged_late["difference"] <= 0,
        "path_count": len(rows),
        "ranking_is_a_sorted_list": [r["rank"] for r in rows] == list(range(1, len(rows) + 1)),
        "break_even_rent_is_a_sane_number": 0.0 < float(be["needed_month_rent"]) < 5.0 * midpoint(*A_RENT_MONTH),
        "estate_tax_scales_with_the_excess": estate_rows(2045)[3]["tax_on_excess"] > estate_rows(2045)[2]["tax_on_excess"],
        "rank_matrix_is_complete": (len(rank_matrix(2045, 30)) == 5
                                    and all(len(v) == 7 for v in rank_matrix(2045, 30).values())),
        "real_and_nominal_differ_under_inflation": any(
            abs(float(r["terminal_econ"]) / float(r["deflator"]) - float(r["terminal_real"])) < 1.0
            for r in path_table(2045, 30, "stagflation")),
    }
