"""Case projection model built ONLY from owner-supplied inputs rounded to $10
BEFORE use, plus labeled assumptions. Every displayed dollar is rounded to $10.

Property A = future trust inheritance (single-family home, City of Cupertino,
Santa Clara County). Property B = already-owned three-unit property (San
Francisco). No name, street address, ZIP code or parcel number is stored here.

Status vocabulary used by the site: Verified / Owner-supplied / Projection /
Assumption / Guidance / Missing / Synthetic.
"""
from decimal import Decimal, ROUND_HALF_UP

# ---------------------------------------------------------------- rounding
def rounded(n):
    """Round to nearest $10, half up. All public dollars pass through this."""
    return int((Decimal(str(n)) / 10).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * 10)


def money(n):
    n = rounded(n)
    return ('\u2212' if n < 0 else '') + '$' + f'{abs(n):,}'


# ------------------------------------------------- owner-supplied inputs
# Every figure below is owner-supplied and was rounded to $10 before storage.
# History tables (rounded): year -> (annual property tax, tax assessment)
A_HISTORY = {
    2014: (5970, 440310), 2015: (6130, 449100), 2016: (6410, 455950),
    2017: (6380, 465070), 2018: (6380, 474370), 2019: (6570, 483850),
    2020: (6570, 493530), 2021: (6660, 498640), 2022: (6760, 508610),
    2023: (6920, 518790), 2024: (7000, 529160), 2025: (7210, 539740),
    2026: (None, 550540),
}
B_HISTORY = {
    2016: (1680, 96560), 2017: (1740, 98490), 2018: (2060, 100460),
    2019: (2130, 102470), 2020: (2200, 104510), 2021: (2070, 105600),
    2022: (2110, 107660), 2023: (2180, 109810), 2024: (2320, 112010),
    2025: (2440, 114250),
}
A_VALUE_2026 = 3_100_000          # owner estimate, Nov 2026 (already $10-rounded)
B_VALUE_2026 = 1_800_000          # owner estimate, Nov 2026
B_RENT_MO = 7150                  # owner: 2 rented units combined, per month
B_UNITS_TOTAL = 3                 # owner: 3 livable units, 2 rented, 1 owner-occupied
A_WATER_MO = (100, 150)           # owner range, per month
A_SOLAR_CREDIT_MO = (10, 20)      # owner: net credit, per month (profit)
B_WATER_MO = (330, 400)           # owner range, whole property
B_ELEC_MO = (30, 70)              # owner range
A_INSURANCE_YR = 1500             # owner tentative estimate — NOT a quote
B_INSURANCE_YR = 1500             # owner tentative estimate — NOT a quote

# Derived effective all-in bill rates (bill / assessment), from rounded owner
# history, rounded to 0.001 percentage point before use.
A_RATE = round(7210 / 539740, 5)          # ~0.01336
B_RATE = round(2440 / 114250, 5)          # ~0.02136

# ------------------------------------------------------- model assumptions
# These are modeling assumptions, not verified forecasts or official data.
ASSUME = dict(
    home_growth=0.03,        # nominal; FHFA since-1991 anchors ~4.5-4.7%/yr, 1-yr now negative
    cost_growth=0.025,       # CPI-ish; CBO: 2.7% (2026) -> 2.0% (2030)
    insurance_growth=0.05,   # CA market stress
    rent_growth=0.025,
    assessment_growth=0.02,  # Prop 13 ceiling path (BOE factor currently 1.02)
    allowance_growth=0.02,   # Prop 19 allowance (statute adjusts biennially by CA HPI)
    stock_return=0.06,       # diversified total return
    stock_yield=0.02,        # dividend portion taxed annually
    bill_return=0.04,        # CBO 10-yr Treasury averages 4.3% 2026-2036 -> 4% use
    sale_cost=0.05,          # selling costs (commission/transfer/escrow), assumption
    mgmt=0.06,               # property management, % of collected rent
    vacancy=0.05,
    tax_ordinary=0.30,       # invented combined effective rate on ordinary income/interest
    tax_gain=0.25,           # invented combined effective rate on long-term gains/dividends
    tax_recapture=0.30,      # invented combined rate on depreciation recapture
    building_share=0.70,     # land/building split for depreciation only
    maint_a=6000,            # ASSUMPTION — owner gave no amount; replace with quotes
    maint_b=12000,           # ASSUMPTION
    ins_a_landlord=2500,     # ASSUMPTION — landlord policy costs more than owner-occupied
)
START, END = 2026, 2076
INHERITANCE_YEARS = tuple(range(2040, 2051))
ALLOWANCE_2026 = 1_044_590    # BOE family-home limit display, $10-rounded (2025-02-16..2027-02-15)
HOMEOWNER_EXEMPTION = 7000    # BOE: reduces taxable value, not taxes dollar-for-dollar

# ------------------------------------------ official factor checks (BOE)
# BOE LTA 2026/002: roll-year inflation factors (the "2026-27" factor 1.02
# applies to the 2026 roll; 2021-22 factor 1.01036 applied to the 2021 roll).
BOE_FACTORS = {
    2015: 1.01998, 2016: 1.01525, 2017: 1.02, 2018: 1.02, 2019: 1.02,
    2020: 1.02, 2021: 1.01036, 2022: 1.02, 2023: 1.02, 2024: 1.02,
    2025: 1.02, 2026: 1.02,
}


def factor_check(history):
    """Compare owner-supplied year-to-year assessment steps with BOE factors.
    Returns list of (year, expected, observed, match); expected = rounded
    prior assessment x official factor."""
    out = []
    for year in sorted(BOE_FACTORS):
        if year in history and (year - 1) in history:
            prev = history[year - 1][1]
            exp = rounded(prev * BOE_FACTORS[year])
            obs = history[year][1]
            diff = obs - exp
            # Within ±$10 the difference can be display rounding of the
            # owner-supplied figures; beyond that it is a real discrepancy.
            verdict = 'match' if diff == 0 else ('rounding' if abs(diff) <= 10 else 'flag')
            out.append((year, exp, obs, verdict))
    return out


# ------------------------------------------------------------ projections
def prop19_assessment(market, old_base, allowance):
    return old_base + max(0, market - old_base - allowance)


def value_at(year, base, growth):
    return base * (1 + growth) ** (year - START)


def allowance_at(year):
    return ALLOWANCE_2026 * (1 + ASSUME['allowance_growth']) ** (year - START)


def a_projection(transfer=2045, growth=None):
    """Property A 2026-2076. Before transfer the assessment follows the old
    Prop 13 base (2% ceiling path). At `transfer` two counterfactual
    assessments appear: full reassessment (rent or sell) and the Prop. 19
    family-home outcome (live in it, if eligible). After transfer each path
    grows at the assessment ceiling path. Base levy shown at the derived
    effective rate; homeowners' exemption reduces the live path."""
    g = ASSUME['home_growth'] if growth is None else growth
    reset_rent = value_at(transfer, A_VALUE_2026, g)
    reset_live = prop19_assessment(reset_rent,
                                   value_at(transfer, A_HISTORY[2026][1], ASSUME['assessment_growth']),
                                   allowance_at(transfer))
    rows = []
    for year in range(START, END + 1):
        mv = value_at(year, A_VALUE_2026, g)
        base = value_at(year, A_HISTORY[2026][1], ASSUME['assessment_growth'])
        if year < transfer:
            av_rent = av_live = base
        elif year == transfer:
            av_rent, av_live = reset_rent, reset_live
        else:
            av_rent = reset_rent * (1 + ASSUME['assessment_growth']) ** (year - transfer)
            av_live = reset_live * (1 + ASSUME['assessment_growth']) ** (year - transfer)
        tax_rent = av_rent * A_RATE
        tax_live = max(0, av_live - HOMEOWNER_EXEMPTION) * A_RATE
        rows.append(dict(year=year, value=mv, base=base, av_rent=av_rent,
                         av_live=av_live, tax_rent=tax_rent, tax_live=tax_live))
    return rows


def b_projection(growth=None):
    """Property B 2026-2076, unchanged ownership. Common to every strategy.
    2026 assessment projected from the 2025 roll at the official 2026 factor."""
    g = ASSUME['home_growth'] if growth is None else growth
    rows = []
    av = B_HISTORY[2025][1] * BOE_FACTORS[2026]   # 2026 roll (projection)
    for year in range(START, END + 1):
        mv = value_at(year, B_VALUE_2026, g)
        if year > START:
            av *= 1 + ASSUME['assessment_growth']
        rows.append(dict(year=year, value=mv, av=av, tax=av * B_RATE))
    return rows


def a_costs(year, landlord=False):
    """Annual operating costs for A at `year` (nominal), from rounded owner
    ranges (midpoints) escalated by assumptions. Solar credit is negative."""
    esc_c = (1 + ASSUME['cost_growth']) ** (year - START)
    esc_i = (1 + ASSUME['insurance_growth']) ** (year - START)
    water = ((A_WATER_MO[0] + A_WATER_MO[1]) / 2) * 12 * esc_c
    solar = -((A_SOLAR_CREDIT_MO[0] + A_SOLAR_CREDIT_MO[1]) / 2) * 12 * esc_c
    ins = (ASSUME['ins_a_landlord'] if landlord else A_INSURANCE_YR) * esc_i
    maint = ASSUME['maint_a'] * esc_c
    return dict(water=water, electricity=solar, insurance=ins, maintenance=maint)


def b_costs(year):
    esc_c = (1 + ASSUME['cost_growth']) ** (year - START)
    esc_i = (1 + ASSUME['insurance_growth']) ** (year - START)
    water = ((B_WATER_MO[0] + B_WATER_MO[1]) / 2) * 12 * esc_c
    elec = ((B_ELEC_MO[0] + B_ELEC_MO[1]) / 2) * 12 * esc_c
    return dict(water=water, electricity=elec,
                insurance=B_INSURANCE_YR * esc_i,
                maintenance=ASSUME['maint_b'] * esc_c)


# ------------------------------------------------- decision comparison
def compare(transfer=2045, years=20, rent_mo_2026=6000, growth=None,
            stock=None, home_g=None):
    """After-modeled-tax comparison of the three paths for Property A only.
    B is common to all paths and excluded. All paths assume the household
    keeps living at B (zero incremental housing cost); the Live path pays
    A's carrying costs as a negative ledger at the after-tax bill rate so the
    terminals are comparable. Live-in-A also consumes A's housing services
    (a lifestyle value priced separately) and may unlock B's spare unit
    (rent unknown, excluded). rent_mo_2026 is an ASSUMPTION grid point in
    2026 dollars; achievable rent is not verified."""
    g = home_g if home_g is not None else ASSUME['home_growth']
    s = stock if stock is not None else ASSUME['stock_return']
    p = ASSUME
    mv = value_at(transfer, A_VALUE_2026, g)
    base = value_at(transfer, A_HISTORY[2026][1], p['assessment_growth'])
    allow = allowance_at(transfer)

    # --- Sell at transfer: basis = death-date FMV, gain ~ 0, sale friction only
    proceeds = mv * (1 - p['sale_cost'])
    equity = proceeds
    basis = proceeds
    for t in range(1, years + 1):
        div = equity * p['stock_yield']
        reinvest = div * (1 - p['tax_gain'])
        equity = equity * (1 + s) - div * p['tax_gain']
        basis += reinvest
    sell_terminal = equity - max(0, equity - basis) * p['tax_gain']

    # --- Rent at transfer: full reassessment at transfer value
    rent = rent_mo_2026 * (1 + p['rent_growth']) ** (transfer - START) * 12
    av = mv
    cash = 0.0
    cumulative_dep = 0.0
    building = mv * p['building_share']
    y1_cash = None
    for t in range(1, years + 1):
        yr = transfer + t - 1
        if t > 1:
            rent *= 1 + p['rent_growth']
            av *= 1 + p['assessment_growth']
        collected = rent * (1 - p['vacancy'])
        costs = a_costs(yr, landlord=True)
        expense = (costs['water'] + costs['electricity'] + costs['insurance']
                   + costs['maintenance'] + av * A_RATE + collected * p['mgmt'])
        dep = min(building / 27.5, max(0, building - cumulative_dep))
        taxable = collected - expense - dep
        income_tax = max(0, taxable) * p['tax_ordinary']
        cf = collected - expense - income_tax
        if y1_cash is None:
            y1_cash = cf
        cash = cash * (1 + p['bill_return'] * (1 - p['tax_ordinary'])) + cf
        cumulative_dep += dep
    horizon_value = mv * (1 + g) ** years          # market value at horizon
    sale_net = horizon_value * (1 - p['sale_cost'])
    gain = max(0, sale_net - (mv - cumulative_dep))
    recapture = min(gain, cumulative_dep)
    rent_terminal = (sale_net - recapture * p['tax_recapture']
                     - (gain - recapture) * p['tax_gain'] + cash)

    # --- Live at transfer: Prop. 19 assessment; negative ledger of carrying cost
    av_live = prop19_assessment(mv, base, allow)
    ledger = 0.0
    y1_live_cost = None
    for t in range(1, years + 1):
        yr = transfer + t - 1
        costs = a_costs(yr)
        if t == 1:
            tax_live = max(0, av_live - HOMEOWNER_EXEMPTION) * A_RATE
        else:
            tax_live = max(0, av_live * (1 + p['assessment_growth']) ** (t - 1)
                           - HOMEOWNER_EXEMPTION) * A_RATE
        carry = tax_live + costs['water'] + costs['electricity'] \
            + costs['insurance'] + costs['maintenance']
        if y1_live_cost is None:
            y1_live_cost = carry
        ledger = ledger * (1 + p['bill_return'] * (1 - p['tax_ordinary'])) + carry
    # house kept as home; terminal value if sold at horizon, gain over step-up basis
    horizon_value = mv * (1 + g) ** years
    horizon_net = horizon_value * (1 - p['sale_cost'])
    live_terminal = (horizon_net
                     - max(0, horizon_net - mv) * p['tax_gain']
                     - ledger)
    return dict(sell=sell_terminal, rent=rent_terminal, live=live_terminal,
                proceeds=proceeds, mv=mv, base=base, allow=allow,
                av_rent=mv, av_live=av_live, y1_cash=y1_cash,
                y1_live_cost=y1_live_cost, rent_y1=rent,
                cash=cash, dep=cumulative_dep)


def break_even_stock(transfer=2045, years=20, rent_mo_2026=6000):
    lo, hi = -0.02, 0.12
    for _ in range(60):
        mid = (lo + hi) / 2
        if compare(transfer, years, rent_mo_2026, stock=mid)['sell'] < \
           compare(transfer, years, rent_mo_2026, stock=mid)['rent']:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def break_even_home(transfer=2045, years=20, rent_mo_2026=6000):
    lo, hi = 0.0, 0.12
    for _ in range(60):
        mid = (lo + hi) / 2
        if compare(transfer, years, rent_mo_2026, home_g=mid)['rent'] < \
           compare(transfer, years, rent_mo_2026, home_g=mid)['sell']:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def break_even_rent(transfer=2045, years=20):
    """2026-dollar monthly rent at which Rent == Sell (may not exist in range)."""
    lo, hi = 500, 30000
    for _ in range(60):
        mid = (lo + hi) / 2
        if compare(transfer, years, mid)['rent'] < compare(transfer, years, mid)['sell']:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ------------------------------------------------------- estate headroom
def estate_tax(gross, exclusion):
    """Simplified: 40% on taxable estate above exclusion; no prior gifts/deductions."""
    return max(0, gross - exclusion) * 0.40


def exclusion_projection(year, growth):
    """Illustrative only: 2027 published amount grown at an assumed rate."""
    return 15_480_000 * (1 + growth) ** (year - 2027)


# ---------------------------------------------- real-history stress data
# Official observations used by the black-swan page. Percentages are official
# and not $-rounded; every row links its source keys.
EPISODES = [
    dict(name='1970s inflation burst', window='1973-1982',
         facts='CPI-U annual average rose 8.7% (1973), 12.3% (1974), 13.5% (1980). '
               'The California assessment inflation factor stayed at 1.02 while CCPI '
               'changes peaked at 17.316% (1980-81).',
         effect='Costs (insurance, water, repairs) can outrun the 2% assessment cap: '
                'voter-approved debt service and charges still grow. Fixed-rate debt '
                'would have been the winner; unleveraged cash lagged prices for years.',
         keys='cpitable lta26002'),
    dict(name='1980-82 Volcker disinflation', window='1980-1982',
         facts='CPI decelerated from 13.5% (1980 annual average) to 3.8% (1982). '
               'In 2010-11 the Prop. 13 factor fell to 0.99763 \u2014 assessed values '
               'can decline in a deflation year.',
         effect='A sale into a high-rate, recession-stricken market realizes losses; '
                'the Prop. 13 base protects the tax side but not market value.',
         keys='cpitable lta26002'),
    dict(name='2021-22 inflation surge', window='2021-2023',
         facts='CPI rose 9.1% in the 12 months ended June 2022 (largest in 40 years); '
               'electricity rose 13.7% over the same 12 months.',
         effect='Operating costs can jump double digits in one year while rents on '
                'covered units are limited to the Rent Board\u2019s annual allowance '
                '(1.6% for March 2026 \u2013 February 2027).',
         keys='cpi rentlocal'),
    dict(name='2022-2026 Bay Area price plateau', window='2022-2026',
         facts='FHFA all-transactions HPI (2026 summary tables): San Jose metro '
               '\u22120.98% over 1 year and +27.43% over 5; San Francisco metro '
               'division \u22120.28% over 1 year and +17.50% over 5; California '
               '\u22120.20% over 1 year vs U.S. +2.13%. Since 1991: San Jose '
               '+425.88%, U.S. +335.69%.',
         effect='Flat-to-negative years are inside recent memory. A smooth 3%/yr '
                'line is an assumption; the same 5-year window elsewhere in the '
                'last decade produced wildly different results.',
         keys='fhfa'),
    dict(name='2023-2026 California insurance repricing', window='2023-2026',
         facts='CDI reports FAIR Plan residential growth slowed to ~16,000 policies '
               'in Q1 2026 (+2.4%) from 35,000-50,000 per quarter during 2024 through '
               'September 2025; insurers re-entering under the Sustainable Insurance '
               'Strategy.',
         effect='Insurance is the fastest-rising carrying cost in California. The '
                'owner\u2019s ~$1,500/yr estimates are unquoted; model at 5%/yr and '
                're-quote at every decision point.',
         keys='cdi2026 insurance'),
    dict(name='Rate-level uncertainty', window='2026-2036',
         facts='CBO baseline: the 10-year Treasury note averages 4.3% over 2026-2036 '
               '(inflation 2.7% in 2026 slowing to 2.0% in 2030). CBO notes the note '
               'closed at 5.2% on October 1, 2026 and models +50bp and +150bp '
               'alternatives.',
         effect='The safe-asset anchor for \u201csell and reinvest\u201d moves about '
                'a point; re-run the comparison across CBO\u2019s own 3.5-4.8% '
                'uncertainty band before committing.',
         keys='cbo62809 cbo62105'),
    dict(name='Japan-style lost decades (hypothetical)', window='not a forecast',
         facts='No official U.S. agency forecasts a multi-decade real estate or '
               'equity stagnation. This row is a labeled hypothetical sensitivity, '
               'not data.',
         effect='If nominal home growth were 0% for 15 years while costs kept rising, '
                'renting A turns deeply negative and selling at the stepped-up basis '
                'protects more value. Liquid assets can be rebalanced; a house cannot.',
         keys='stocks'),
]
