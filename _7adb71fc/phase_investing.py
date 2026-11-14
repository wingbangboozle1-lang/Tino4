"""Illustrative phased-entry stress model for sale proceeds.

This is not a forecast, recommendation, or historical investment backtest. The
1929 path is a deliberately simple, linear price-index drawdown to the
Federal-Reserve-documented *more than* 80% peak-to-trough loss, then held flat.
The 2008 path uses official end-of-year S&P composite price-index observations
and linearly interpolates between them for monthly purchase dates. The rising
path is invented. All three are nominal price-only paths: no dividends, fees,
inflation, capital-gains tax, federal tax on Treasury interest, or Treasury
price changes are included.

The starting principal is an illustrative amount only. The cash yield is a
user-selected, constant gross rate; it is not an observed or projected
3-month-to-2-year Treasury yield. This deliberately isolates entry timing.
"""
from decimal import Decimal, ROUND_HALF_UP

HORIZON_MONTHS = 48
STARTING_PRINCIPAL = 100_000
DEFAULT_TREASURY_YIELD = 0.03
DEFAULT_WAIT_MONTHS = 24
DEFAULT_PHASE_MONTHS = 12
DEFAULT_IMMEDIATE_SHARE = 0.0

# End-of-year S&P composite price-index values from ERP 2026 Table B-56.
# 2007 is month 0; 2008-2011 are the four following year ends.
S_AND_P_YEAR_END = (1468.36, 903.25, 1115.10, 1257.64, 1257.60)

SCENARIOS = {
    "1929": "1929-like deep drawdown",
    "2008": "2008–2011 price-index sequence",
    "rising": "Rising-market opportunity-cost case",
}


def round_money(value):
    """Round a displayed dollar amount half-up to the nearest $10."""
    return int((Decimal(str(value)) / 10).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 10)


def money(value):
    value = round_money(value)
    return ("−" if value < 0 else "") + f"${abs(value):,}"


def market_index(scenario, month):
    """Return the synthetic nominal price level, normalized to 100 at month 0."""
    if scenario not in SCENARIOS:
        raise ValueError("unknown scenario")
    if not 0 <= month <= HORIZON_MONTHS:
        raise ValueError("month outside the 48-month test horizon")

    if scenario == "1929":
        # Fall 1929 to June 1932 is approximately 33 months. Exactly -80% is
        # used as a conservative severity floor; the Fed source says more than
        # 80%. Interpolation and the later flat line are assumptions.
        trough_months = 33
        if month >= trough_months:
            return 20.0
        return 100.0 - (80.0 * month / trough_months)

    if scenario == "2008":
        year = min(month // 12, 3)
        within = month - year * 12
        left = S_AND_P_YEAR_END[year]
        right = S_AND_P_YEAR_END[year + 1]
        level = left + (right - left) * (within / 12)
        return level / S_AND_P_YEAR_END[0] * 100

    # An invented +8%/year price-only path demonstrates the risk of waiting
    # through a rising market. It is a sensitivity case, not a baseline return.
    return 100.0 * (1.08 ** (month / 12))


def market_path(scenario):
    return [market_index(scenario, month) for month in range(HORIZON_MONTHS + 1)]


def simulate(principal=STARTING_PRINCIPAL, scenario="2008", wait_months=DEFAULT_WAIT_MONTHS,
             phase_months=DEFAULT_PHASE_MONTHS, annual_treasury_yield=DEFAULT_TREASURY_YIELD,
             immediate_share=DEFAULT_IMMEDIATE_SHARE):
    """Compare immediate equity, a mixed bridge/phase path, and cash-proxy-only.

    ``immediate_share`` of principal enters stocks at month 0. The remainder
    stays in a constant-yield Treasury cash proxy until the chosen wait ends,
    then all remaining cash (including assumed gross interest during phase-in)
    is invested in equal-dollar monthly installments over ``phase_months``.
    Results are valued at month 48.
    """
    if principal <= 0:
        raise ValueError("principal must be positive")
    if wait_months not in (24, 30, 36):
        raise ValueError("wait must be 24, 30, or 36 months")
    if phase_months not in (6, 12):
        raise ValueError("phase-in must be 6 or 12 months")
    if not 0 <= annual_treasury_yield <= 0.06:
        raise ValueError("gross Treasury-yield sensitivity must be 0%–6%")
    if not 0 <= immediate_share <= 1:
        raise ValueError("immediate stock share must be between 0 and 1")
    if wait_months + phase_months > HORIZON_MONTHS:
        raise ValueError("phase-in must finish within the 48-month horizon")

    path = market_path(scenario)
    monthly_growth = (1 + annual_treasury_yield) ** (1 / 12)
    cash = principal * (1 - immediate_share)
    shares = principal * immediate_share / path[0]
    fixed_purchase = None

    for month in range(1, HORIZON_MONTHS + 1):
        cash *= monthly_growth
        if month == wait_months:
            annuity_factor = sum(monthly_growth ** k for k in range(phase_months))
            fixed_purchase = cash * monthly_growth ** phase_months / annuity_factor
        if wait_months < month <= wait_months + phase_months:
            # Size a level-dollar installment schedule so the bridge balance,
            # including assumed interest during phase-in, is invested by the end.
            purchase = cash if month == wait_months + phase_months else min(cash, fixed_purchase)
            shares += purchase / path[month]
            cash -= purchase

    return {
        "scenario": scenario,
        "principal": principal,
        "horizon_months": HORIZON_MONTHS,
        "wait_months": wait_months,
        "phase_months": phase_months,
        "annual_treasury_yield": annual_treasury_yield,
        "immediate_share": immediate_share,
        "immediate_equity": principal * path[-1] / path[0],
        "mixed_phase": shares * path[-1] + cash,
        "treasury_only": principal * (1 + annual_treasury_yield) ** (HORIZON_MONTHS / 12),
        "ending_cash": cash,
        "ending_shares": shares,
        "index_start": path[0],
        "index_end": path[-1],
    }


def scenario_summary(principal=STARTING_PRINCIPAL, annual_treasury_yield=DEFAULT_TREASURY_YIELD,
                     phase_months=DEFAULT_PHASE_MONTHS, immediate_share=DEFAULT_IMMEDIATE_SHARE):
    """Static four-year comparison used for the pre-JavaScript page view."""
    rows = []
    for scenario in SCENARIOS:
        immediate = simulate(principal, scenario, 24, phase_months,
                             annual_treasury_yield, immediate_share)
        staged24 = immediate["mixed_phase"]
        staged30 = simulate(principal, scenario, 30, phase_months,
                             annual_treasury_yield, immediate_share)["mixed_phase"]
        staged36 = simulate(principal, scenario, 36, phase_months,
                             annual_treasury_yield, immediate_share)["mixed_phase"]
        park = immediate["treasury_only"]
        rows.append({
            "scenario": scenario,
            "immediate": immediate["immediate_equity"],
            "park_then_phase_24": staged24,
            "park_then_phase_30": staged30,
            "park_then_phase_36": staged36,
            "treasury_only": park,
        })
    return rows
