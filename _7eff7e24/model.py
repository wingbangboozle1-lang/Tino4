"""Synthetic examples ONLY. Does not load any household inputs.
Nominal USD; annual steps; no forecasts or probabilities. Full precision internal,
Decimal ROUND_HALF_UP for public display. See methodology for exclusions.
"""
from decimal import Decimal, ROUND_HALF_UP

START, END = 2026, 2076
INHERITANCE_YEARS = tuple(range(2040, 2051))
PARAM = dict(value=1_000_000, assessment=200_000, rent=48_000,
             water=1_200, electricity=600, insurance=3_000, maintenance=10_000,
             house_growth=.03, inflation=.025, assessment_growth=.02,
             equity_return=.06, bill_return=.03, cost_growth=.03,
             insurance_growth=.04, rent_growth=.025, vacancy=.05,
             management=.08, sale_cost=.05, ordinary_tax=.30,
             gain_tax=.25, recapture_tax=.30, equity_yield=.02,
             building_share=.70, allowance=1_000_000)
REGIMES = ('Baseline', 'Inflation surge', 'Housing slump', 'Equity crash',
           'Lost decade', 'Insurance and repairs', 'Compound shock')


def rounded(n):
    return int((Decimal(str(n)) / 10).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * 10)


def money(n):
    n = rounded(n)
    return ('−' if n < 0 else '') + f'${abs(n):,}'


def prop19_assessment(market, old, allowance):
    return old + max(0, market - old - allowance)


def rates(regime, t):
    """Relative year t begins at 1 after inheritance/start. All shocks invented."""
    p = PARAM
    r = dict(house=p['house_growth'], equity=p['equity_return'],
             inflation=p['inflation'], cost=p['cost_growth'],
             insurance=p['insurance_growth'], rent=p['rent_growth'],
             bill=p['bill_return'], vacancy=p['vacancy'], repair=0)
    if regime in ('Inflation surge', 'Compound shock') and t <= 4:
        r.update(inflation=.08, cost=.09, rent=.02, equity=-.05, bill=.05)
    if regime in ('Housing slump', 'Compound shock'):
        if t == 1: r.update(house=-.25, rent=-.10, vacancy=.20)
        elif t <= 5: r.update(house=0, rent=0, vacancy=.15)
    if regime in ('Equity crash', 'Compound shock'):
        if t == 1: r['equity'] = -.40
        elif t == 2: r['equity'] = -.10
        elif t <= 5: r['equity'] = .12
    if regime == 'Lost decade' and t <= 10: r['equity'] = 0
    if regime in ('Insurance and repairs', 'Compound shock'):
        if t == 1: r['insurance'] = .60
        if t == 3: r['repair'] = 75_000
        if t in (2, 3): r['vacancy'] = .25
    return r


def projection(inherit=2045, regime='Baseline'):
    """Normalized property; assessment is full-reassessment rental case at transfer.
    Separate qualified principal-residence assessment shown. Base 1% levy only;
    no bonds, charges, homeowners exemption or deductions in this illustration.
    """
    p = PARAM
    value, base, cpi = p['value'], p['assessment'], 1.
    cost = {k: p[k] for k in ('water','electricity','insurance','maintenance')}
    out=[]
    full, qualified = base, base
    for year in range(START, END+1):
        if year > START:
            r=rates(regime,year-START)
            value *= 1+r['house']; base *= 1+p['assessment_growth']; cpi *= 1+r['inflation']
            for k in cost:
                cost[k] *= 1+r['insurance' if k=='insurance' else 'cost']
            cost['maintenance'] += r['repair']
            if year > inherit:
                full *= 1+p['assessment_growth']; qualified *= 1+p['assessment_growth']
        if year < inherit: full=qualified=base
        elif year == inherit:
            full=value; qualified=prop19_assessment(value,base,p['allowance'])
        out.append(dict(year=year,value=value,real=value/cpi,old=base,
                        full=full,qualified=qualified,tax=full*.01,
                        qualified_tax=qualified*.01,**cost))
        # One-time repair is not compounded into subsequent annual maintenance.
        if year > START: cost['maintenance'] -= r['repair']
    return out


def compare(regime='Baseline', years=20):
    """Per fictional $1m inherited value, no debt/estate allocation, B held constant.
    Sale friction 5%, equity annual dividend tax + terminal unrealized gain tax.
    Rental receipts/expenses, modeled 30% positive taxable income (no loss refund),
    GDS building depreciation simplified annual approximation; terminal taxes split.
    Cash surpluses and deficits grow at after-tax bill rate; negative ledger is a
    funding requirement (not a promise of borrowing at bill yields).
    """
    p=PARAM
    equity=equity_basis=1_000_000*(1-p['sale_cost'])
    bills=equity
    house=1_000_000.; assessment=house; rent=p['rent']
    costs={k:p[k] for k in ('water','electricity','insurance','maintenance')}
    cumulative_dep=cash=cpi=0.
    cpi=1.
    first_cash=None
    for t in range(1,years+1):
        r=rates(regime,t); cpi*=1+r['inflation']
        # Return is total return; income portion taxed even in a negative-return year.
        dividend=equity*p['equity_yield']
        reinvest=dividend*(1-p['gain_tax'])
        equity=equity*(1+r['equity'])-dividend*p['gain_tax']
        equity_basis+=reinvest
        bills*=1+r['bill']*(1-p['ordinary_tax'])
        collected=rent*(1-r['vacancy'])
        expense=sum(costs.values())+assessment*.01+collected*p['management']
        # Repair reserve is spending in this simplified model; no separate deduction
        # for capital replacement. Shock repair treated as a cash item only.
        dep=min(p['value']*p['building_share']/27.5,
                max(0,p['value']*p['building_share']-cumulative_dep))
        taxable=collected-expense-dep
        income_tax=max(0,taxable)*p['ordinary_tax']
        cf=collected-expense-income_tax-r['repair']
        if first_cash is None: first_cash=cf
        cash=cash*(1+r['bill']*(1-p['ordinary_tax']))+cf
        cumulative_dep+=dep
        house*=1+r['house']; assessment*=1+p['assessment_growth']
        rent*=1+r['rent']
        for k in costs: costs[k]*=1+r['insurance' if k=='insurance' else 'cost']
    net_house=house*(1-p['sale_cost'])
    gain=max(0,net_house-(p['value']-cumulative_dep))
    recapture=min(gain,cumulative_dep)
    rent_terminal=net_house-recapture*p['recapture_tax']-(gain-recapture)*p['gain_tax']+cash
    eq_terminal=equity-max(0,equity-equity_basis)*p['gain_tax']
    return dict(equity=eq_terminal,bills=bills,rental=rent_terminal,
                real_equity=eq_terminal/cpi,real_bills=bills/cpi,
                real_rental=rent_terminal/cpi,first_cash=first_cash,cash=cash)


def exclusion(year, growth=.025):
    """Illustration only. 2027 actual base, then assumed growth, not statutory indexing."""
    return 15_480_000*(1+growth)**(year-2027)
