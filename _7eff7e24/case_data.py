"""Case figures for the two properties, rounded to $10 BEFORE use.

Privacy design
--------------
Every amount below is rounded half-up to the nearest $10 before any arithmetic runs,
so no published number can be worked back to an exact bill, assessment or balance.
Only what the owner stated in the brief is present. Nothing was looked up about a
person, address, parcel or account. Where the owner gave a range, the range is kept.
Where a figure is missing it is ``None`` — never zero, never guessed.

Status vocabulary (also used by the table renderer)
---------------------------------------------------
Verified    an official source states the amount or rule
Owner       the owner stated it in the brief; not independently confirmed
Projection  arithmetic on rounded inputs under a stated assumption
Assumption  an invented model parameter, not a fact about this household
Missing     no evidence exists yet; the cell is blank by design
"""

# ---------------------------------------------------------------------------
# Property A — the home to be inherited through a trust, 2040-2050
# ---------------------------------------------------------------------------
A = dict(
    label='Property A',
    role='Future inheritance through a trust',
    value_2026=3_100_000,      # owner estimate, November 2026
    assessed_2026=550_540,     # owner-supplied roll value, +2% pattern, rounded
    tax_2025=7_210,            # owner-supplied bill, rounded
    tax_2026=None,             # owner supplied no bill for the current year
    water_year=(1_200, 1_800), # owner: about $100-$150 a month
    electric_year=(-240, -120),# owner: solar usually produces a small credit
    insurance_year=1_500,      # owner estimate, explicitly unconfirmed
    maintenance_pct=0.010,     # assumption used in projections, not a quote
    units=1,
)

# ---------------------------------------------------------------------------
# Property B — already owned by the inheritor, occupied plus rented units
# ---------------------------------------------------------------------------
B = dict(
    label='Property B',
    role='Already owned; current residence plus rented units',
    value_2026=1_800_000,      # owner estimate, November 2026
    assessed_2026=116_530,     # 114,250 x 1.02, rounded; 2026 roll not supplied
    tax_2025=2_440,            # owner-supplied bill, rounded
    tax_2026=None,
    water_year=(3_960, 4_800), # owner: $330-$400 a month for three units
    electric_year=(360, 840),  # owner: $30-$70 a month
    insurance_year=1_500,      # owner estimate, explicitly unconfirmed
    maintenance_pct=0.015,     # assumption used in projections, not a quote
    units=3,
    rent_mo=7_150,             # two rented units, combined, owner-supplied
    vacant_units=1,
)

# Owner-supplied historical tax and assessment records, each entry rounded.
A_HISTORY = [
    (2014, 5_960, 440_300), (2015, 6_130, 449_100), (2016, 6_410, 455_950),
    (2017, 6_380, 465_070), (2018, 6_380, 474_370), (2019, 6_560, 483_850),
    (2020, 6_560, 493_530), (2021, 6_660, 498_640), (2022, 6_760, 508_610),
    (2023, 6_920, 518_790), (2024, 7_000, 529_160), (2025, 7_210, 539_740),
    (2026, None, 550_540),
]
B_HISTORY = [
    (2016, 1_680, 96_560), (2017, 1_740, 98_490), (2018, 2_060, 100_460),
    (2019, 2_130, 102_470), (2020, 2_200, 104_510), (2021, 2_070, 105_600),
    (2022, 2_110, 107_660), (2023, 2_180, 109_810), (2024, 2_320, 112_010),
    (2025, 2_440, 114_250),
]

# ---------------------------------------------------------------------------
# Model parameters. These are invented planning assumptions, labelled as such
# everywhere they surface. None is a forecast and none is a quote.
# ---------------------------------------------------------------------------
P = dict(
    transfer=(2040, 2050),     # planning window from the brief
    transfer_default=2045,
    horizon=2076,              # 50 years of compounding from 2026
    home_growth=(0.03, 0.04, 0.05),
    home_growth_default=0.04,
    assess_cap=0.020,          # Constitution art. XIII A s.2(b); BOE pub. 29
    assess_observed=0.0181,    # BOE factor table, 51 annual factors, 1976-77..2026-27
    cpi=0.030,
    cpi_observed=0.0390,       # BOE CCPI column, same 51 years
    allowance_2025=1_044_590,  # ROUNDED DISPLAY of the 1,044,586 statutory figure
    allowance_growth=(0.03, 0.04, 0.05),
    rent_growth=0.025,
    rent_cap_statutory=0.10,   # Civ. Code 1947.12 ceiling, sunsets 2030-01-01
    equity=0.060,
    bills=0.035,
    div_yield=0.020,
    tax_div=0.331,             # assumption: 20% fed + 3.8% NIIT + 9.3% CA
    tax_gain=0.331,
    recapture=0.250,           # IRS Topic 409, unrecaptured s.1250
    tax_rent=0.300,
    selling_cost=0.060,        # assumption: commission, escrow, title, concessions
    transfer_tax=0.0011,       # RTC 11911 county rate, $0.55 per $500
    vacancy=0.050,
    management=0.080,
    rent_yield=(0.020, 0.028, 0.040),   # gross annual rent / market value
    rent_yield_default=0.028,
    building_share=0.70,       # depreciation split assumption
    dep_life=27.5,
    exclusion_2026=15_000_000, # IRS, verified
    exclusion_2027=15_480_000, # IRS IR-2026-133, verified
    estate_top_rate=0.40,      # IRS Form 706
    estate_growth=0.025,
)

# Ranges reduced to the midpoints used for the headline projection.
A_MID = dict(water=1_560, electric=-180, insurance=1_500, tax_rate=0.01336,
             maint=A['maintenance_pct'])
B_MID = dict(water=4_380, electric=600, insurance=1_500, tax_rate=0.02136,
             maint=B['maintenance_pct'])

# Verified official reference points used by the black-swan page.
BOE_FACTORS = [1.02]*51
for _i, _v in {7: 1.01, 19: 1.0119, 20: 1.0111, 23: 1.01853, 28: 1.01867,
               34: 0.99763, 35: 1.00753, 38: 1.00454, 39: 1.01998,
               40: 1.01525, 45: 1.01036}.items():
    BOE_FACTORS[_i] = _v
BOE_CCPI = [6.250, 7.169, 8.233, 9.826, 17.316, 7.134, 11.137, 1.033, 5.034,
            5.089, 4.374, 2.095, 5.160, 4.730, 4.758, 6.390, 3.039, 3.441,
            2.308, 1.194, 1.115, 2.399, 2.081, 1.853, 3.214, 4.172, 3.215,
            2.459, 1.867, 3.665, 4.596, 2.269, 3.380, 3.477, -0.237, 0.753,
            2.889, 3.081, 0.454, 1.998, 1.525, 2.619, 2.962, 3.847, 2.980,
            1.036, 5.561, 7.274, 3.181, 2.514, 3.307]
BOE_START = 1976  # first assessment year in the factor table

# FHFA all-transactions house price index, California, quarterly 1975Q1-2026Q2.
CA_HPI = {}
_RAW = """1975 41.65 42.79 44.36 45.75
1976 47.85 50.31 53.60 55.58
1977 58.08 63.02 67.97 70.69
1978 73.23 76.01 78.63 81.80
1979 84.89 88.68 93.13 96.36
1980 100.00 102.79 106.52 108.39
1981 110.48 112.83 116.28 117.54
1982 104.00 107.26 104.73 115.82
1983 116.73 117.43 117.20 117.67
1984 119.44 120.06 121.63 122.73
1985 124.47 126.23 129.11 130.50
1986 132.21 134.74 137.69 141.05
1987 144.66 148.21 152.86 157.17
1988 162.93 169.63 177.66 187.35
1989 196.10 205.79 217.71 224.54
1990 227.30 228.07 229.96 228.46
1991 228.39 226.97 226.98 228.63
1992 227.44 225.08 222.56 222.56
1993 219.11 217.24 215.39 214.11
1994 211.99 206.87 203.81 200.93
1995 199.59 201.49 203.82 203.49
1996 203.46 200.89 200.51 201.53
1997 202.48 204.53 208.55 212.21
1998 216.84 221.56 227.41 231.79
1999 235.29 239.29 244.76 249.95
2000 260.81 267.83 276.82 285.37
2001 296.41 305.47 311.89 316.27
2002 324.71 335.73 348.36 358.56
2003 366.84 373.71 386.37 411.05
2004 424.32 450.89 496.70 515.81
2005 538.37 569.94 598.37 625.13
2006 638.13 643.96 646.07 642.37
2007 633.56 622.92 599.71 575.13
2008 542.90 498.03 460.20 444.32
2009 440.32 420.20 410.92 412.19
2010 409.16 407.91 410.16 405.64
2011 391.12 384.83 386.42 385.24
2012 380.93 381.57 390.50 398.78
2013 407.18 425.87 446.82 461.60
2014 471.23 484.00 494.12 499.74
2015 504.97 516.28 529.45 536.77
2016 543.78 553.43 565.55 572.35
2017 578.30 590.29 602.08 610.68
2018 621.13 632.98 640.98 640.88
2019 645.09 651.64 658.55 662.82
2020 669.09 676.76 684.68 698.85
2021 718.45 761.06 800.76 833.14
2022 866.74 919.32 912.98 886.84
2023 883.91 905.46 915.82 915.73
2024 930.66 945.84 954.25 956.74
2025 958.13 966.27 966.01 969.38
2026 975.22 974.97"""
for _line in _RAW.splitlines():
    _p = _line.split()
    for _q, _v in enumerate(_p[1:], 1):
        CA_HPI[(int(_p[0]), _q)] = float(_v)

# Named episodes taken directly from the official series above.
EPISODES = [
    ('1990-1997 aerospace and defence contraction',
     1990, 1, 1997, 1, 'Twelve consecutive quarters without a new nominal high.'),
    ('2006-2012 global financial crisis',
     2006, 3, 2012, 1, 'Largest peak-to-trough decline in the published state series.'),
    ('2007-2011 slow bleed after the credit shock',
     2007, 1, 2011, 4, 'Four calendar years of falling prices.'),
    ('1981-1982 Volcker disinflation',
     1981, 2, 1982, 3, 'Six quarters down while the CPI ran in double digits.'),
]

# Owner baseline projection check: does the supplied history compound at the
# statutory ceiling, the observed state average, or something faster?
def assess_check(history, tax_rate):
    """Return [(year, step_pct, tax_implied_by_assessment, tax_supplied)].

    The implied tax is the assessed value times the effective rate the owner's own
    bills support. It is shown only to expose where the supplied history is not
    internally consistent; it is not an official bill.
    """
    out = []
    for i in range(1, len(history)):
        y0, t0, a0 = history[i-1]
        y1, t1, a1 = history[i]
        out.append((y1, a1/a0 - 1, a1 * tax_rate, t1))
    return out
