"""Reproducible public historical price-index stress calculations.

All observations here come from the cited FRED table-data pages. These are
price-only series (not dividend-inclusive total returns). Treasury yields are
separate 2026 curve observations used only as clearly labeled scenario inputs;
they are not the Treasury returns realized during the historical equity periods.
No household/case data is imported or read.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable

FRED_1929_URL = "https://fred.stlouisfed.org/data/M1109BUSM293NNBR"
FRED_2008_URL = "https://fred.stlouisfed.org/data/SPASTT01USQ661N"
TREASURY_NOV_2026_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
    "TextView?type=daily_treasury_yield_curve&field_tdr_date_value=202611"
)
TREASURY_BILLS_URL = "https://www.treasurydirect.gov/marketable-securities/treasury-bills/"
TREASURY_REINVEST_URL = (
    "https://www.treasurydirect.gov/marketable-securities/"
    "reinvesting-a-marketable-security/"
)

# Treasury daily par curve row for 2026-11-13. CMT rates are interpolated
# par-yield curve observations, not guaranteed security returns or the actual
# auction yields of any selected bill/note.
TREASURY_CURVE = {
    "as_of": "2026-11-13",
    "source_url": TREASURY_NOV_2026_URL,
    "rates_percent": {3: 4.32, 6: 4.42, 12: 4.65, 24: 4.88},
    "terms": {
        3: "3-month Treasury bill",
        6: "6-month Treasury bill",
        12: "1-year par-curve point; not a specific bill auction yield",
        24: "2-year Treasury note curve point",
    },
}


@dataclass(frozen=True)
class PriceSeries:
    key: str
    title: str
    provider: str
    series_id: str
    source_url: str
    frequency: str
    unit: str
    start_year: int
    start_month: int
    step_months: int
    values: tuple[float, ...]
    period_note: str

    def __post_init__(self) -> None:
        if not self.values or any(not isfinite(value) or value <= 0 for value in self.values):
            raise ValueError(f"{self.key} contains an invalid index observation")
        if self.step_months not in (1, 3):
            raise ValueError(f"{self.key} must be monthly or quarterly")

    def date_label(self, index: int) -> str:
        if not 0 <= index < len(self.values):
            raise IndexError(index)
        month_number = (self.start_year - 1) * 12 + (self.start_month - 1) + index * self.step_months
        year, month_zero = divmod(month_number, 12)
        year += 1
        month = month_zero + 1
        if self.step_months == 3:
            return f"{year} Q{(month - 1) // 3 + 1}"
        return f"{year}-{month:02d}"

    def index_for_month_offset(self, offset_months: int) -> int:
        if offset_months < 0 or offset_months % self.step_months:
            raise ValueError(f"{offset_months} months is not an observed {self.frequency} point")
        index = offset_months // self.step_months
        if index >= len(self.values):
            raise ValueError(f"{offset_months} months is outside the sourced series window")
        return index

    def value_at_month_offset(self, offset_months: int) -> float:
        return self.values[self.index_for_month_offset(offset_months)]


# Successive monthly values beginning 1929-09, sourced from the NBER Macrohistory
# monthly Dow-Jones Industrial Stock Price Index table at FRED. The NBER data are
# price-index observations, not total returns. Values are retained at source
# precision for calculations; the public table links each displayed observation.
_DOW_JONES_1929 = (
    362.35, 291.50, 228.20, 247.20, 255.65, 267.40, 278.25, 285.50, 266.70, 243.15, 229.80, 228.80,
    225.00, 198.75, 180.95, 172.15, 167.25, 181.55, 180.05, 158.00, 141.45, 139.30, 145.35, 139.80,
    118.35, 98.10, 103.40, 82.80, 78.55, 78.90, 81.05, 64.05, 51.85, 46.85, 47.75, 64.40,
    71.00, 65.30, 62.20, 58.85, 61.85, 55.15, 57.75, 66.70, 83.30, 93.80, 98.55, 98.85,
    99.45, 91.65, 95.45, 99.05, 102.85, 106.90, 102.30, 103.55, 96.20, 95.90, 92.25, 91.60,
    90.20, 93.00, 98.30, 101.80, 103.20, 103.70, 100.00, 105.45, 112.75, 115.25, 122.65, 126.95,
    130.70, 134.80, 144.75, 141.70, 146.30, 152.00, 154.60, 152.85, 149.50, 155.00, 162.25, 164.95,
    167.40, 172.95, 180.80, 179.05, 182.30, 188.40, 187.10, 177.65, 171.90, 170.30, 177.85, 182.95,
    160.25, 139.90, 124.75, 124.35, 127.25, 125.45, 114.75, 111.00, 113.55, 122.80, 139.75, 140.95,
    136.50, 148.65, 152.25, 151.10, 145.65, 144.85, 142.05, 127.10, 133.00, 135.10, 138.20, 137.80,
    144.40,
)

# Successive quarterly values beginning 2007-Q4, sourced from the OECD
# Financial Market: Share Prices for the United States series at FRED, index
# 2015=100. This is also a price index, not total return.
_OECD_SHARE_PRICES_2008 = (
    92.707380, 84.246600, 86.149060, 77.113590, 53.643950, 47.717500,
    53.532250, 60.638350, 66.322940, 67.316800, 66.720860, 65.137650,
    71.586930, 77.239330, 78.027440, 70.999380, 68.653760, 74.804930,
    72.760230, 75.085660, 77.379230, 83.317290, 86.591680, 89.185930,
    93.969480, 96.294620, 100.105300, 102.264600, 100.569600, 101.702800,
    103.806300, 97.852700, 96.638210, 90.547960, 97.066230, 100.425800,
    100.916600, 106.598600, 108.529500, 111.666400, 116.875200,
)

SERIES = {
    "1929": PriceSeries(
        key="1929",
        title="Dow-Jones Industrial Stock Price Index for United States",
        provider="National Bureau of Economic Research Macrohistory Database, via FRED",
        series_id="M1109BUSM293NNBR",
        source_url=FRED_1929_URL,
        frequency="monthly",
        unit="dollars per share (published index series units)",
        start_year=1929,
        start_month=9,
        step_months=1,
        values=_DOW_JONES_1929,
        period_note="September 1929 through September 1939, monthly observations",
    ),
    "2008": PriceSeries(
        key="2008",
        title="Financial Market: Share Prices for United States",
        provider="OECD Main Economic Indicators, via FRED",
        series_id="SPASTT01USQ661N",
        source_url=FRED_2008_URL,
        frequency="quarterly",
        unit="index, 2015=100",
        start_year=2007,
        start_month=10,
        step_months=3,
        values=_OECD_SHARE_PRICES_2008,
        period_note="2007 Q4 through 2017 Q4, quarterly observations",
    ),
}

OBSERVATION_ROWS = {
    "1929": (
        ("Starting observation", 0),
        ("12 months after start", 12),
        ("24 months after start", 24),
        ("36 months after start", 36),
        ("Lowest monthly observation in this 10-year slice", 33),
        ("10-year endpoint", 120),
    ),
    "2008": (
        ("Starting observation", 0),
        ("2008 Q4", 4),
        ("Lowest quarterly observation in this 10-year slice", 5),
        ("24 months after start", 8),
        ("36 months after start", 12),
        ("10-year endpoint", 40),
    ),
}


@dataclass(frozen=True)
class PathResult:
    series_key: str
    path_key: str
    path_label: str
    wait_months: int
    terminal_per_starting_unit: float
    maximum_observed_drawdown_pct: float
    terminal_date: str
    observation_frequency: str


def round_money_to_10(amount: float) -> int:
    """Round a non-negative user-entered dollar value to the nearest $10."""
    if not isfinite(amount) or amount < 0:
        raise ValueError("amount must be finite and non-negative")
    return int((amount + 5) // 10 * 10)


def _monthly_rate(strategy: str, month_number: int, rung_months: int | None = None) -> float:
    """Return a scenario yield as a fraction, not a promised investment return."""
    rates = TREASURY_CURVE["rates_percent"]
    if strategy == "bill-roll":
        annual = rates[3] / 100
    elif strategy == "four-rung-ladder":
        # Each quarter of starting cash is initially assigned to a different
        # maturity. Once a rung matures, it is assumed to roll into 3-month bills.
        annual = (rates[rung_months] if rung_months and month_number < rung_months else rates[3]) / 100
    else:
        raise ValueError(f"unknown cash strategy: {strategy}")
    # Simplification for a reproducible sensitivity: treat the quoted annualized
    # CMT observation as an effective annual rate and accrue monthly. Actual bill
    # discount conventions, note coupons/prices, tax and auction results differ.
    return (1 + annual) ** (1 / 12) - 1


def _grow_accounts(
    accounts: list[dict[str, float | int]],
    from_month: int,
    to_month: int,
    strategy: str,
) -> None:
    for month_number in range(from_month, to_month):
        for account in accounts:
            rung = int(account["rung_months"]) if "rung_months" in account else None
            account["balance"] = float(account["balance"]) * (1 + _monthly_rate(strategy, month_number, rung))


def _drawdown(values: Iterable[float]) -> float:
    peak = 0.0
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        if peak:
            worst = min(worst, value / peak - 1)
    return worst * 100


def simulate_path(
    series_key: str,
    path_key: str,
    wait_months: int = 24,
    principal: float = 1.0,
) -> PathResult:
    """Simulate an immediate or delayed-equity path over the sourced 10-year slice.

    Delayed paths hold cash for 24 or 36 months, then make four equal base-
    principal purchases every three months (at the wait date and +3/+6/+9 months).
    Cash left after the first three tranches continues at the assumed 3-month
    roll; accrued cash interest is swept into the final purchase. The historical
    price index is used for equity purchases; dividends, taxes, fees, inflation,
    fund tracking differences and personal taxes are not modeled.
    """
    if series_key not in SERIES:
        raise ValueError(f"unknown historical series: {series_key}")
    if not isfinite(principal) or principal <= 0:
        raise ValueError("principal must be finite and positive")
    series = SERIES[series_key]
    if path_key == "immediate":
        shares = principal / series.values[0]
        path_values = [shares * level for level in series.values]
        return PathResult(
            series_key=series_key,
            path_key=path_key,
            path_label="Immediate price-index exposure",
            wait_months=0,
            terminal_per_starting_unit=path_values[-1] / principal,
            maximum_observed_drawdown_pct=_drawdown(path_values),
            terminal_date=series.date_label(len(series.values) - 1),
            observation_frequency=series.frequency,
        )

    if path_key not in ("bill-roll", "four-rung-ladder"):
        raise ValueError(f"unknown path: {path_key}")
    if wait_months not in (24, 36):
        raise ValueError("wait_months must be 24 or 36")
    wait_index = series.index_for_month_offset(wait_months)
    buy_months = tuple(wait_months + 3 * index for index in range(4))
    buy_indexes = tuple(series.index_for_month_offset(month) for month in buy_months)
    if buy_indexes[-1] >= len(series.values):
        raise ValueError("historical series does not cover the full phase-in")

    if path_key == "bill-roll":
        accounts: list[dict[str, float | int]] = [{"balance": principal, "rung_months": 0}]
        label = "3-month bill roll (flat-yield scenario)"
    else:
        rung_months = (3, 6, 12, 24)
        accounts = [
            {"balance": principal / 4, "rung_months": rung}
            for rung in rung_months
        ]
        label = "Equal 3m / 6m / 1y / 2y starting rungs; mature proceeds roll to 3m"

    shares = 0.0
    cash = 0.0
    phase_start_balance: float | None = None
    path_values: list[float] = []
    previous_month = 0
    buy_counter = 0
    for index, price in enumerate(series.values):
        elapsed_month = index * series.step_months
        if phase_start_balance is None:
            _grow_accounts(accounts, previous_month, elapsed_month, path_key)
            if elapsed_month == wait_months:
                cash = sum(float(account["balance"]) for account in accounts)
                accounts = [{"balance": cash, "rung_months": 0}]
        else:
            # After the wait, uninvested funds roll in the modeled 3-month bill
            # assumption until their scheduled equity purchase.
            for month_number in range(previous_month, elapsed_month):
                cash *= 1 + _monthly_rate("bill-roll", month_number)

        if elapsed_month in buy_months:
            if phase_start_balance is None:
                # Month wait is the first purchase date; capture the post-wait
                # ladder value once, then split its principal into four tranches.
                phase_start_balance = cash
            if buy_counter < 3:
                purchase = phase_start_balance / 4
            else:
                # Sweep all earned cash interest into the last scheduled buy.
                purchase = cash
            purchase = min(purchase, cash)
            shares += purchase / price
            cash -= purchase
            buy_counter += 1

        if phase_start_balance is None:
            portfolio_value = sum(float(account["balance"]) for account in accounts)
        else:
            portfolio_value = shares * price + cash
        path_values.append(portfolio_value)
        previous_month = elapsed_month

    return PathResult(
        series_key=series_key,
        path_key=path_key,
        path_label=label,
        wait_months=wait_months,
        terminal_per_starting_unit=path_values[-1] / principal,
        maximum_observed_drawdown_pct=_drawdown(path_values),
        terminal_date=series.date_label(len(series.values) - 1),
        observation_frequency=series.frequency,
    )


def compare_paths(series_key: str, principal: float = 1.0) -> tuple[PathResult, ...]:
    """Return the immediate path and both Treasury paths for 24/36-month waits."""
    return (
        simulate_path(series_key, "immediate", principal=principal),
        simulate_path(series_key, "bill-roll", 24, principal),
        simulate_path(series_key, "four-rung-ladder", 24, principal),
        simulate_path(series_key, "bill-roll", 36, principal),
        simulate_path(series_key, "four-rung-ladder", 36, principal),
    )


def official_observations(series_key: str) -> tuple[dict[str, object], ...]:
    """Selected source values for visible, line-linked observation tables."""
    series = SERIES[series_key]
    return tuple(
        {
            "label": label,
            "date": series.date_label(index),
            "value": series.values[index],
            "change_pct_from_start": (series.values[index] / series.values[0] - 1) * 100,
            "source_url": series.source_url,
            "series_id": series.series_id,
            "frequency": series.frequency,
            "unit": series.unit,
        }
        for label, index in OBSERVATION_ROWS[series_key]
    )


def price_only_peak_to_trough(series_key: str) -> dict[str, object]:
    """Maximum observed peak-to-trough decline within the included 10-year slice."""
    series = SERIES[series_key]
    peak = series.values[0]
    peak_index = 0
    worst = 0.0
    worst_peak_index = 0
    trough_index = 0
    for index, value in enumerate(series.values):
        if value > peak:
            peak = value
            peak_index = index
        drawdown = value / peak - 1
        if drawdown < worst:
            worst = drawdown
            worst_peak_index = peak_index
            trough_index = index
    return {
        "peak_date": series.date_label(worst_peak_index),
        "peak_index": series.values[worst_peak_index],
        "trough_date": series.date_label(trough_index),
        "trough_index": series.values[trough_index],
        "drawdown_pct": worst * 100,
        "source_url": series.source_url,
    }


def public_series_payload() -> dict[str, object]:
    """JSON-safe, case-free data for a static local-only page script."""
    return {
        "treasury": {
            "as_of": TREASURY_CURVE["as_of"],
            "source_url": TREASURY_CURVE["source_url"],
            "bills_url": TREASURY_BILLS_URL,
            "reinvest_url": TREASURY_REINVEST_URL,
            "rates_percent": TREASURY_CURVE["rates_percent"],
            "terms": TREASURY_CURVE["terms"],
        },
        "series": {
            key: {
                "title": series.title,
                "provider": series.provider,
                "series_id": series.series_id,
                "source_url": series.source_url,
                "frequency": series.frequency,
                "unit": series.unit,
                "start_year": series.start_year,
                "start_month": series.start_month,
                "step_months": series.step_months,
                "values": series.values,
                "period_note": series.period_note,
            }
            for key, series in SERIES.items()
        },
    }
