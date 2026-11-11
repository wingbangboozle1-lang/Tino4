"""Owner inputs (already rounded to the nearest $10) and model assumptions.

PRIVACY RULE: this file may only ever contain owner figures that are already rounded
to the nearest $10. Un-rounded figures, names, addresses, parcel numbers, ZIP codes and
neighbourhood names must never be written to this repository.
"""

BASE_YEAR = 2026
LAST_YEAR = 2075          # black-swan section runs 50 years
PROJ_LAST = 2060          # year-by-year baseline tables
INHERIT_YEARS = [2040, 2045, 2050]
CENTRAL_T = 2045
HORIZONS = [10, 20]
CENTRAL_H = 10

# ---------------------------------------------------------------- Property A (to be inherited)
A = {
    "label": "Property A",
    "place": "Cupertino, Santa Clara County",
    "kind": "single-family home with rooftop solar",
    "status": "to be inherited through a family trust, expected 2040-2050",
    "value_2026": 3_100_000,
    # roll year -> assessed value, rounded to $10
    "assessed": {2014: 440_310, 2015: 449_100, 2016: 455_950, 2017: 465_070, 2018: 474_370,
                 2019: 483_850, 2020: 493_530, 2021: 498_640, 2022: 508_610, 2023: 518_790,
                 2024: 529_160, 2025: 539_740, 2026: 550_540},
    # roll year -> tax bill, rounded to $10 (2026 bill not supplied)
    "tax": {2014: 5_970, 2015: 6_130, 2016: 6_410, 2017: 6_380, 2018: 6_380, 2019: 6_570,
            2020: 6_570, 2021: 6_660, 2022: 6_760, 2023: 6_920, 2024: 7_000, 2025: 7_210},
    "water_month": (100, 150),
    "elec_month": (-20, -10),       # solar: small net credit
    "insurance_year": 1_500,         # owner's guess
}

# ---------------------------------------------------------------- Property B (already owned)
B = {
    "label": "Property B",
    "place": "San Francisco",
    "kind": "residential building with three livable units",
    "status": "already owned by the future beneficiary",
    "value_2026": 1_800_000,
    "assessed": {2016: 96_560, 2017: 98_490, 2018: 100_460, 2019: 102_470, 2020: 104_510,
                 2021: 105_600, 2022: 107_660, 2023: 109_810, 2024: 112_010, 2025: 114_250},
    "tax": {2016: 1_680, 2017: 1_740, 2018: 2_060, 2019: 2_130, 2020: 2_200, 2021: 2_070,
            2022: 2_110, 2023: 2_180, 2024: 2_320, 2025: 2_440},
    "units": 3,
    "units_rented": 2,
    "rent_month": 7_150,
    "water_month": (330, 400),
    "elec_month": (30, 70),
    "insurance_year": 1_500,         # owner's guess
}

# ---------------------------------------------------------------- official constants used by the model
OFFICIAL = {
    "prop13_cap": 0.02,
    "prop19_allowance": 1_044_586,           # transfers 16 Feb 2025 - 15 Feb 2027
    "homeowners_exemption": 7_000,
    "rate_A": 0.011636,                      # sum of FY2025-26 component rates (see facts)
    "rate_B": 0.0118162182,                  # San Francisco FY2026-27
    "sf_parcel_taxes_2025": 829.22,          # 334.38 + 319.34 + 3 x 21.50 + 99 + 12
    "sf_measure_h_min": 129,
    "estate_excl": {2026: 15_000_000, 2027: 15_480_000},
    "estate_rate": 0.40,
    "gift_excl": {2026: 19_000, 2027: 20_000},
    "sec121_joint": 500_000, "sec121_single": 250_000,
    "niit_rate": 0.038, "niit_joint": 250_000,
    "recapture_cap": 0.25,
    "depr_years": 27.5,
    "fed_joint_2027": [(0, .10), (25_600, .12), (104_050, .22), (218_250, .24), (416_650, .32),
                       (529_100, .35), (793_650, .37)],
    "fed_ltcg_joint_2027": (102_100, 633_600),
    "ca_joint_2025": [(0, .01), (22_158, .02), (52_528, .04), (82_904, .06), (115_084, .08),
                      (145_448, .093), (742_958, .103), (891_542, .113), (1_485_906, .123)],
    "sf_rent_share_of_cpi": 0.60,
    "hud_rent_A_4br_2026": 6_390,
    "transfer_tax": 0.0011,
    "treasury_10y": 0.0498, "treasury_3m": 0.0430,
    "cdi_avg_premium": 1_571,
}

# ---------------------------------------------------------------- assumptions (not official facts)
# Each has low / base / high.  "why" is shown on the Methodology page.
ASSUME = {
    "infl":      {"low": .020, "base": .025, "high": .035,
                  "why": "CPI-U rose 2.5% a year over 1994-2024 and 3.6% a year over 1975-2024; the Congressional Budget Office projects inflation consistent with the Federal Reserve's 2% goal from 2027."},
    "home_A":    {"low": .030, "base": .045, "high": .060,
                  "why": "FHFA house price index for the San Jose metro: 3.0% a year over 2005-2025, 5.8% over 1995-2025, 6.7% over 1976-2025. Base is the midpoint of the 20- and 30-year rates."},
    "home_B":    {"low": .025, "base": .040, "high": .055,
                  "why": "FHFA house price index for the San Francisco metro division: 2.7% a year over 2005-2025, 5.6% over 1995-2025, 6.5% over 1976-2025. Base is the midpoint of the 20- and 30-year rates."},
    "rent_mkt":  {"low": .025, "base": .035, "high": .045,
                  "why": "BLS rent index for the San Francisco area: 3.4% a year over 2004-2024, 3.8% over 1994-2024."},
    "water":     {"low": .035, "base": .043, "high": .050,
                  "why": "BLS water, sewer and trash index: 4.3% a year over 1998-2024 (4.0% over the last 10 years, 4.6% over the last 20)."},
    "elec":      {"low": .025, "base": .030, "high": .040,
                  "why": "BLS electricity index: 3.0% a year over 2014-2024, 3.4% over 2004-2024, 2.7% over 1995-2024."},
    "stock":     {"low": .060, "base": .080, "high": .100,
                  "why": "A U.S. stock index fund returned 11.3% a year including dividends over 1988-2025 (federal Thrift Savings Plan C Fund); a broad U.S. share-price index rose 6.8% a year excluding dividends over 1969-2025. Base is set well below the fund's record on purpose."},
    "cash":      {"low": .030, "base": .045, "high": .050,
                  "why": "Treasury yields on 10 Nov 2026 ran from 4.30% (3-month) to 4.98% (10-year)."},
}
FIXED = {
    "stock_share": 0.60,            # sell option: 60% stock index fund / 40% Treasuries
    "dividend_yield": 0.015,        # taxed every year; rest of the stock return is taxed when sold
    "selling_cost": 0.06,           # commission, transfer tax, escrow, preparation (transfer tax by statute is 0.11%)
    "sale_months": 6,               # carrying costs while the home is being sold
    "vacancy": 0.05,                # rental options
    "building_share": 0.25,         # share of Property A's value that is building (depreciable)
    "other_income_2026": 200_000,   # household's other taxable income, joint return, 2026 dollars
    "maint_A_2026": 10_000,         # placeholder until the owner supplies actual spending
    "maint_B_2026": 15_000,
    "chained_gap": 0.003,           # chained CPI assumed 0.3 point below CPI-U (federal indexing)
    # cost growth is modelled as a spread over consumer-price inflation
    "spread_insurance": 0.020,      # premiums assumed to rise 2 points faster than prices
    "spread_water": 0.018,          # base water growth 4.3% = 2.5% + 1.8
    "spread_elec": 0.005,           # base electricity growth 3.0% = 2.5% + 0.5
    "spread_rent": 0.010,           # base market-rent growth 3.5% = 2.5% + 1.0
    "solar_legacy_latest_end": 2043,
    "b_unit_rent_month_2026": 3_580,  # average of the two rented units, rounded to $10
}
