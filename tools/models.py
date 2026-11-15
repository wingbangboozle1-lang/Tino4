#!/usr/bin/env python3
"""Projection engine for the public decision workspace.

All household figures are rounded to the nearest $10 at the point of display
(see r10). Inputs are the anonymized, rounded owner-supplied figures only;
this module never reads a private file. Statutory figures (IRS thresholds,
the Proposition 19 cap) are passed through unrounded because they are
published amounts, not household data.
"""
from __future__ import annotations

# --- Rounded owner-supplied case figures (nearest $10) -----------------------
A_VALUE_2026 = 3_100_000          # est. market value, Property A, Nov 2026
A_VALUE_LOW = 3_050_000
A_VALUE_HIGH = 3_150_000
A_AV_2026 = 550_540               # factored base year value, 2026 roll
A_TAX_2026 = 7_210                # annual property tax, 2025 bill
B_VALUE_2026 = 1_800_000
B_VALUE_LOW = 1_750_000
B_VALUE_HIGH = 1_850_000
B_AV_2025 = 114_250               # latest owner-supplied assessment
B_TAX_2025 = 2_440
B_RENT_2UNITS_MO = 7_150          # two units combined, owner-supplied
B_RENT_UNIT3_LOW_MO = 3_300       # unrented unit: scenario band, not a quote
B_RENT_UNIT3_HIGH_MO = 3_800

# Owner-supplied rounded operating inputs (2026 money)
A_WATER_LOW_MO, A_WATER_HIGH_MO = 100, 150
A_SOLAR_CREDIT_LOW_MO, A_SOLAR_CREDIT_HIGH_MO = 10, 20
B_WATER_LOW_MO, B_WATER_HIGH_MO = 330, 400
B_ELEC_LOW_MO, B_ELEC_HIGH_MO = 30, 70
A_INS_OWNER = 1_500               # owner guess — flagged as likely low
B_INS_OWNER = 1_500
A_INS_LOW, A_INS_HIGH = 3_000, 7_000       # market planning band (flagged)
B_INS_LOW, B_INS_HIGH = 2_500, 5_000

# Scenario bands (assumptions — labeled on the site)
A_MAINT_LOW_PCT, A_MAINT_HIGH_PCT = 0.005, 0.010   # of value per year
B_MAINT_LOW, B_MAINT_HIGH = 9_000, 18_000          # per year, older 3-unit
SALE_COST_PCT_LOW, SALE_COST_PCT_HIGH = 0.04, 0.08
SALE_COST_PCT_BASE = 0.05
STOCK_LOW, STOCK_BASE, STOCK_HIGH = 0.04, 0.06, 0.08     # nominal, scenario
VALUE_GROWTH_LOW, VALUE_GROWTH_BASE, VALUE_GROWTH_HIGH = 0.020, 0.035, 0.050
CAP_GROWTH_LOW, CAP_GROWTH_HIGH = 0.020, 0.035           # FHFA CA HPI band
INFLATION_LOW, INFLATION_BASE, INFLATION_HIGH = 0.020, 0.025, 0.030
RENT_GROWTH = 0.020
AV_FACTOR = 0.02                 # Proposition 13 general annual cap
PROP19_CAP_2025_2027 = 1_044_586  # statutory (BOE LTA 2025/009), not rounded

# Observed bill-to-assessment ratios from the rounded owner tables
RATIO_A = A_TAX_2026 / A_AV_2026   # ≈ 1.31 %
RATIO_B = B_TAX_2025 / B_AV_2025   # ≈ 2.14 % — irregular, flagged for review

# Official CPI-U annual averages (BLS series CPIAUCNS via FRED), 1929-2025.
CPI_ANNUAL = {
    1929: 17.158, 1930: 16.700, 1933: 12.933, 1939: 13.908, 1940: 14.008,
    1946: 19.517, 1948: 24.042, 1949: 23.808, 1959: 29.150, 1969: 36.683,
    1973: 44.400, 1979: 72.575, 1981: 90.925, 1989: 123.967, 1999: 166.575,
    2009: 214.537, 2019: 255.657, 2020: 258.811, 2022: 292.655, 2025: 321.943,
}


def r10(value: float) -> int:
    """Round to the nearest $10 — the public rounding rule for case figures."""
    return int(round(value / 10.0) * 10)


def money(value: float) -> str:
    rounded = r10(value)
    if rounded < 0:
        return f"-${abs(rounded):,}"
    return f"${rounded:,}"


def money_exact(value: int) -> str:
    """Published statutory figures are shown exactly as published."""
    return f"${value:,}"


def pct(value: float, digits: int = 1) -> str:
    return f"{value * 100:.{digits}f}%"


def cagr(start: float, end: float, years: float) -> float:
    return (end / start) ** (1.0 / years) - 1.0


def cpi_stats() -> list[tuple[str, str, str]]:
    """Regime rows computed from the official CPI series above."""
    c = CPI_ANNUAL
    rows = [
        ("1929–1933 depression deflation",
         f"CPI fell {pct(1 - c[1933] / c[1929])} cumulative ({pct(cagr(c[1929], c[1933], 4))} per year)",
         "Computed from the official annual CPI averages."),
        ("1930s (1929–1939)",
         f"{pct(cagr(c[1929], c[1939], 10))} per year average",
         "A decade of falling then flat prices."),
        ("1946–1948 postwar inflation",
         f"{pct(c[1948] / c[1946] - 1)} cumulative in 2 years ({pct(cagr(c[1946], c[1948], 2))} per year)",
         "Price controls lifted; rapid catch-up inflation."),
        ("1970s (1969–1979)",
         f"{pct(cagr(c[1969], c[1979], 10))} per year average",
         "Stagflation decade."),
        ("1973–1981",
         f"CPI doubled in 8 years ({pct(cagr(c[1973], c[1981], 8))} per year)",
         "Two oil shocks inside one expansion."),
        ("1980s (1979–1989)",
         f"{pct(cagr(c[1979], c[1989], 10))} per year average",
         "Disinflation after the 1981 peak."),
        ("1990s (1989–1999)",
         f"{pct(cagr(c[1989], c[1999], 10))} per year average",
         "Moderate inflation."),
        ("2000s (1999–2009)",
         f"{pct(cagr(c[1999], c[2009], 10))} per year average",
         "Includes the 2008 price reversal."),
        ("2010s (2009–2019)",
         f"{pct(cagr(c[2009], c[2019], 10))} per year average",
         "Low-inflation decade."),
        ("2020–2022 surge",
         f"{pct(c[2022] / c[2020] - 1)} cumulative in 2 years ({pct(cagr(c[2020], c[2022], 2))} per year)",
         "Matches the BLS-reported 9.1% peak 12-month reading in June 2022."),
        ("2019–2025",
         f"{pct(cagr(c[2019], c[2025], 6))} per year average",
         "Post-pandemic price level shift."),
    ]
    return rows


# --- Value / assessment projections ----------------------------------------
def value_at(year: int, rate: float = VALUE_GROWTH_BASE, start: float = A_VALUE_2026) -> float:
    return start * (1.0 + rate) ** (year - 2026)


def fbv_a_at(year: int) -> float:
    """Factored base year value under the general 2% annual cap."""
    return A_AV_2026 * (1.0 + AV_FACTOR) ** (year - 2026)


def prop19_cap_at(transfer_year: int, hpi_rate: float = CAP_GROWTH_LOW) -> float:
    """Projected adjusted $1,000,000 amount for a transfer-year (biennial
    FHFA HPI adjustment). Anchored on the published $1,044,586 (2025–2027)."""
    return PROP19_CAP_2025_2027 * (1.0 + hpi_rate) ** (transfer_year - 2026)


def p19_av(transfer_year: int, rate: float = VALUE_GROWTH_BASE,
           hpi_rate: float = CAP_GROWTH_LOW) -> float:
    """Family-home exclusion: new taxable value = FBV + excess above the cap.

    When market value at transfer is FBV + cap or less, the factored base
    year value carries over. Above that, the excess over the cap is added.
    """
    fm = value_at(transfer_year, rate)
    fbv = fbv_a_at(transfer_year)
    cap = prop19_cap_at(transfer_year, hpi_rate)
    excess = max(0.0, fm - fbv - cap)
    return fbv + excess


def full_reassess_av(transfer_year: int, rate: float = VALUE_GROWTH_BASE) -> float:
    return value_at(transfer_year, rate)


def tax_a(av: float) -> float:
    return av * RATIO_A


def tax_b(av: float) -> float:
    return av * RATIO_B


def b_av_at(year: int) -> float:
    return B_AV_2025 * (1.0 + AV_FACTOR) ** (year - 2025)


# --- Estate threshold projections ------------------------------------------
EXCLUSION_2026 = 15_000_000
EXCLUSION_2027 = 15_480_000
GIFT_2026 = 19_000
GIFT_2027 = 20_000
TRUST_TOP_2026 = 16_000      # estates & trusts top bracket begins over $16,000
TRUST_LTCG_2026 = 16_250     # 20% capital-gains rate threshold for trusts
EXCLUSION_FIRST_PROJECTED = 2028


def exclusion_at(year: int, cpi_rate: float = INFLATION_BASE) -> float:
    """Projected basic exclusion amount: $15,480,000 (2027) indexed at the
    selected CPI scenario. OBBBA directs annual inflation adjustment after
    2026 (Rev. Proc. 2025-32 §2.14). Projection — not law."""
    if year <= 2026:
        return EXCLUSION_2026
    if year == 2027:
        return EXCLUSION_2027
    return EXCLUSION_2027 * (1.0 + cpi_rate) ** (year - 2027)


# --- Black-swan irregular path --------------------------------------------
# Each era: (label, years, stock annual nominal, house annual nominal, CPI).
# Shocks are stitched from the sourced historical anchors on the black-swan
# page. This is an illustration of uneven regimes, not a forecast.
IRREGULAR_ERAS = [
    ("Late-cycle boom", 2027, 2029, 0.12, 0.06, 0.030),
    ("2008-magnitude crash", 2030, 2032, -0.24, -0.11, 0.010),
    ("Recovery", 2033, 2037, 0.10, 0.04, 0.025),
    ("1970s-style stagflation", 2038, 2045, 0.01, 0.02, 0.060),
    ("Disinflationary bull", 2046, 2055, 0.11, 0.05, 0.030),
    ("1973-74-style bear and stall", 2056, 2062, -0.08, -0.02, 0.015),
    ("Moderate growth", 2063, 2076, 0.07, 0.035, 0.025),
]


def irregular_path(checkpoints: tuple[int, ...] = (2030, 2040, 2050, 2060, 2076)) -> dict:
    """Compound one dollar through the irregular era schedule; return checkpoints."""
    stocks = 1.0
    houses = 1.0
    prices = 1.0
    out: dict[int, tuple[float, float, float]] = {2026: (1.0, 1.0, 1.0)}
    for label, y0, y1, s, h, c in IRREGULAR_ERAS:
        years = y1 - y0 + 1
        stocks *= (1.0 + s) ** years
        houses *= (1.0 + h) ** years
        prices *= (1.0 + c) ** years
        out[y1] = (stocks, houses, prices)
        for cp in checkpoints:
            if y0 <= cp <= y1:
                k = cp - y0 + 1
                out[cp] = (stocks / (1.0 + s) ** (years - k),
                           houses / (1.0 + h) ** (years - k),
                           prices / (1.0 + c) ** (years - k))
    return {k: out[k] for k in sorted(out) if k in (2026,) or k in checkpoints or k == 2076}


# --- Path cash-flow snapshot (2026 money, rounded at display) --------------
def path_cashflows() -> dict:
    """Annual cash-flow bands for the compared paths, before income taxes.

    Low band = high costs + low income; high band = low costs + high income.
    Every input is either owner-supplied (rounded) or a labeled scenario band.
    """
    b_rent_all = (B_RENT_2UNITS_MO + B_RENT_UNIT3_LOW_MO) * 12
    b_rent_all_high = (B_RENT_2UNITS_MO + B_RENT_UNIT3_HIGH_MO) * 12
    b_costs_low = B_TAX_2025 + B_INS_LOW + B_WATER_LOW_MO * 12 + B_ELEC_LOW_MO * 12 + B_MAINT_LOW
    b_costs_high = B_TAX_2025 + B_INS_HIGH + B_WATER_HIGH_MO * 12 + B_ELEC_HIGH_MO * 12 + B_MAINT_HIGH
    a_costs_low = A_TAX_2026 + A_INS_LOW + A_WATER_LOW_MO * 12 + A_MAINT_LOW_PCT * A_VALUE_2026 - A_SOLAR_CREDIT_HIGH_MO * 12
    a_costs_high = A_TAX_2026 + A_INS_HIGH + A_WATER_HIGH_MO * 12 + A_MAINT_HIGH_PCT * A_VALUE_2026 - A_SOLAR_CREDIT_LOW_MO * 12
    rent_a_low, rent_a_high = 5_500 * 12, 7_500 * 12      # scenario band, flagged
    reassessed_tax = tax_a(full_reassess_av(2026, 0.0))   # at today's value
    a_rental_extras_low = 0.05 * rent_a_low + 0.06 * rent_a_low    # vacancy + mgmt
    a_rental_extras_high = 0.05 * rent_a_high + 0.06 * rent_a_high

    p1_low = b_rent_all - b_costs_high - a_costs_high
    p1_high = b_rent_all_high - b_costs_low - a_costs_low
    p2_low = B_RENT_2UNITS_MO * 12 - b_costs_high
    p2_high = B_RENT_2UNITS_MO * 12 - b_costs_low
    p3_low = rent_a_low - reassessed_tax - A_INS_HIGH - A_WATER_HIGH_MO * 12 - A_MAINT_HIGH_PCT * A_VALUE_2026 - a_rental_extras_low
    p3_high = rent_a_high - reassessed_tax - A_INS_LOW - A_WATER_LOW_MO * 12 - A_MAINT_LOW_PCT * A_VALUE_2026 - a_rental_extras_high
    return {
        "p1": (p1_low, p1_high),
        "p2": (p2_low, p2_high),
        "p3": (p3_low, p3_high),
        "b_rent_all": (b_rent_all, b_rent_all_high),
        "b_costs": (b_costs_low, b_costs_high),
        "a_costs": (a_costs_low, a_costs_high),
        "reassessed_tax": reassessed_tax,
        "net_sale": A_VALUE_2026 * (1 - SALE_COST_PCT_BASE),
    }


def sale_net(gross: float = A_VALUE_2026, cost_pct: float = SALE_COST_PCT_BASE) -> float:
    return gross * (1 - cost_pct)


# --- Treasury staging model (mirrors the browser tool exactly) --------------
def phase_model(months: int = 30, drawdown: float = 0.57, trough: int = 17,
                drift: float = 0.0, y1: float = 0.0, y2: float = 0.0,
                inflation: float = 0.0, early: bool = True) -> dict:
    """Normalized-100-units staging model. Equal monthly purchases; Treasury
    reserve accrues the entered yields; equity grows at drift until the crash,
    declines linearly to the drawdown over `trough` months, then stays flat.
    Returns monthly value paths and summary outcomes."""
    n = int(months)
    crash_start = n // 2 if early else n
    horizon = max(n, crash_start + int(trough))

    def price(m: int) -> float:
        p = (1.0 + drift) ** (m / 12.0) if m <= crash_start else (1.0 + drift) ** (crash_start / 12.0)
        if m > crash_start:
            k = min(m - crash_start, int(trough))
            p *= 1.0 - drawdown * (k / float(trough))
        return max(p, 0.0001)

    reserve = 100.0
    shares = 0.0
    imp_shares = 100.0 / price(0)
    imp_path, phase_path, real_path = [], [], []
    install = 100.0 / n
    for m in range(0, horizon + 1):
        if m > 0:
            factor = (1.0 + (y1 if m <= 12 else y2)) ** (1.0 / 12.0)
            reserve *= factor
            if m <= n:
                buy = install if m < n else reserve  # final purchase includes accruals
                shares += buy / price(m)
                reserve -= buy
        v_phase = shares * price(m) + reserve
        v_imp = imp_shares * price(m)
        phase_path.append(v_phase)
        imp_path.append(v_imp)
        real_path.append((1.0 + inflation) ** (m / 12.0))

    def max_dd(path: list[float]) -> float:
        peak, worst = path[0], 0.0
        for v in path:
            peak = max(peak, v)
            if peak > 0:
                worst = max(worst, 1.0 - v / peak)
        return worst

    def real(path: list[float]) -> list[float]:
        return [v / r for v, r in zip(path, real_path)]

    imp_real, phase_real = real(imp_path), real(phase_path)
    return {
        "horizon": horizon,
        "imp_final": imp_path[-1],
        "phase_final": phase_path[-1],
        "imp_final_real": imp_real[-1],
        "phase_final_real": phase_real[-1],
        "imp_dd": max_dd(imp_path),
        "phase_dd": max_dd(phase_path),
    }
