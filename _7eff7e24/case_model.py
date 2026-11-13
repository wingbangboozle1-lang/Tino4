"""Case projections for the two properties.

Rules enforced here
-------------------
* Every input is already rounded to $10 in ``case_data``; nothing is re-derived
  from an unrounded figure.
* All displayed money passes through ``rounded()`` (ROUND_HALF_UP to $10).
* Property tax is split into the constitutional 1% base levy and a residual
  "other" rate, because an all-in bill is not 1% and is not capped at 2%.
* Property A is assessed two ways after transfer: a full reassessment (rental or
  ineligible transfer) and the Proposition 19 family-home formula (owner-occupier).
* Property B is never re-based because of A's transfer.
"""
from decimal import Decimal, ROUND_HALF_UP
from case_data import A, B, A_MID, B_MID, P


def rounded(n):
    return int((Decimal(str(n)) / 10).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * 10)


def money(n):
    if n is None:
        return None
    n = rounded(n)
    return ('\u2212' if n < 0 else '') + f'${abs(n):,}'


def allowance(year):
    """Prop. 19 family-home allowance, published amounts and an assumed indexation.

    Verified: $1,044,586 for transfers 2025-02-16 to 2027-02-15 (BOE LTA 2025/009).
    The 2025-02-16 to 2027-02-15 figure is shown rounded to $1,044,590 for display.
    After 2027 the amount is assumed to grow with the home-growth assumption, which
    is an assumption, not law: the statute indexes the figure to FHFA's California
    House Price Index every second February 16.
    """
    if year <= 2027:
        return P['allowance_2025']
    return P['allowance_2025'] * (1 + P['home_growth_default']) ** (year - 2027)


def base_levy_rate(property_row):
    """Owner's own 1% base levy implied by the supplied bill and assessment."""
    if property_row is A:
        return round(A['tax_2025'] / A['assessed_2026'], 5)
    return round(B['tax_2025'] / B['assessed_2026'], 5)


def projection(which, transfer=None, home_growth=None, cpi=None,
               rent_yield=None, insurance_growth=0.05, other_rates=None):
    """Year-by-year projection for one property, 2026-2076.

    Returns a list of dicts. ``transfer`` is the year the trust is assumed to
    distribute property A; it is irrelevant for B and ignored there.
    """
    transfer = P['transfer_default'] if transfer is None else transfer
    g = P['home_growth_default'] if home_growth is None else home_growth
    infl = P['cpi'] if cpi is None else cpi
    ry = P['rent_yield_default'] if rent_yield is None else rent_yield
    prop = A if which == 'A' else B
    mid = A_MID if which == 'A' else B_MID

    value = prop['value_2026'] * 1.0
    assessed = prop['assessed_2026'] * 1.0
    water = sum(prop['water_year']) / 2
    electric = sum(prop['electric_year']) / 2
    insurance = prop['insurance_year'] * 1.0
    maintenance = prop['value_2026'] * mid['maint']
    rent = (B['rent_mo'] * 12) if which == 'B' else prop['value_2026'] * ry
    # Transfer-date assessment bases for A are created once and then only grow
    # at the 2% ceiling, exactly as a real roll would.
    base_full = base_qualified = None
    rows = []
    for year in range(2026, P['horizon'] + 1):
        if year > 2026:
            value *= 1 + g
            assessed *= 1 + P['assess_cap']
            water *= 1 + infl
            electric *= 1 + infl
            insurance *= 1 + insurance_growth
            maintenance *= 1 + infl
            rent *= 1 + P['rent_growth']
        if which == 'A' and year == transfer:
            base_full = value                                  # full reassessment
            base_qualified = min(value, assessed + allowance(year))
        if which == 'A' and year > transfer:
            base_full *= 1 + P['assess_cap']
            base_qualified *= 1 + P['assess_cap']

        tax_assessed = base_full if base_full is not None else assessed
        tax_qualified = base_qualified if base_qualified is not None else assessed

        rate = mid['tax_rate']
        other_share = 1 - (0.01 / rate)
        bill_full = tax_assessed * rate
        bill_qualified = tax_qualified * rate
        rows.append(dict(
            year=year, value=value, assessed=assessed,
            tax_assessed=tax_assessed, tax_qualified=tax_qualified,
            levy_base=tax_assessed * 0.01,
            levy_other=tax_assessed * other_share,
            bill_full=bill_full, bill_qualified=bill_qualified,
            savings_qualified=bill_full - bill_qualified,
            insurance=insurance, water=water, electric=electric,
            maintenance=maintenance, rent=rent,
            gross_rent_yield=(rent / value) if rent else None,
            cash_cost_owner=bill_qualified + insurance + water + electric + maintenance,
            cash_cost_rental=bill_full + insurance + water + electric + maintenance,
        ))
    return rows


def sale_proceeds(year_row, property_key='A'):
    """Net sale proceeds after selling costs and the county documentary transfer tax."""
    prop = A if property_key == 'A' else B
    price = year_row['value']
    commission = price * P['selling_cost']
    transfer = price * P['transfer_tax']
    return dict(price=price, commission=commission, transfer_tax=transfer,
                net=price - commission - transfer)


def after_tax_reinvest(proceeds, years, taxable_gain=0.0):
    """Grow net proceeds in a diversified portfolio, then pay tax on the way out.

    Two tax events are modelled: annual tax on the dividend yield at the assumed
    combined rate, and a terminal tax on the appreciated amount. The inherited
    basis resets at death, so ``taxable_gain`` starts at zero and the whole
    post-transfer appreciation is the taxable part.
    """
    bal = proceeds
    basis = proceeds
    for _ in range(years):
        div = bal * P['div_yield']
        bal = bal * (1 + P['equity']) - div * P['tax_div']
        basis += div * (1 - P['tax_div'])
    gain = max(0.0, bal - basis)
    return dict(pre_tax=bal, tax_on_gain=gain * P['tax_gain'],
                after_tax=bal - gain * P['tax_gain'])


def hold_after_tax(row, years_held):
    """Rental hold: sell at the horizon, pay depreciation recapture then gain tax."""
    sale = sale_proceeds(row, 'A')
    building = row['value'] * P['building_share']
    dep = min(building, building * min(years_held, P['dep_life']) / P['dep_life'])
    gain = max(0.0, sale['net'] - row['value'] + dep)
    recapture = min(gain, dep)
    tax = recapture * P['recapture'] + (gain - recapture) * P['tax_gain']
    return dict(net_sale=sale['net'], depreciation=dep, taxable_gain=gain,
                recapture_tax=recapture * P['recapture'],
                gain_tax=(gain - recapture) * P['tax_gain'],
                after_tax=sale['net'] - tax)


def path_comparison(transfer=None, horizon_years=20):
    """Four household paths from the same transfer year, nominal dollars.

    Sell A and reinvest, rent A and sell later, move in and keep B rented, or
    move in and leave B's third unit empty. Property B's own value and rent are
    excluded from every column so the columns compare only the decision at hand.
    """
    transfer = P['transfer_default'] if transfer is None else transfer
    rows = projection('A', transfer=transfer)
    at_transfer = next(r for r in rows if r['year'] == transfer)
    sale = sale_proceeds(at_transfer, 'A')
    reinvest = after_tax_reinvest(sale['net'], horizon_years)
    horizon_row = next(r for r in rows if r['year'] == transfer + horizon_years)

    # Rent A: net operating income accumulated, then sale after the horizon.
    cash = 0.0
    for r in rows:
        if transfer < r['year'] <= transfer + horizon_years:
            income = r['rent'] * (1 - P['vacancy'])
            expense = (r['bill_full'] + r['insurance'] + r['water'] +
                       r['electric'] + r['maintenance'] +
                       income * P['management'])
            net = income - expense
            tax = max(0.0, net - r['value'] * P['building_share'] / P['dep_life']) * P['tax_rent']
            cash = cash * (1 + P['bills'] * (1 - P['tax_rent'])) + net - tax
    held = hold_after_tax(horizon_row, horizon_years)

    return dict(
        transfer=transfer,
        sale_price=sale['price'], sale_net=sale['net'],
        reinvest_pre_tax=reinvest['pre_tax'], reinvest_after_tax=reinvest['after_tax'],
        rental_income_20y=cash, rental_sale_net=held['net_sale'],
        rental_total=cash + held['after_tax'],
        move_in_savings=sum(r['savings_qualified'] for r in rows
                            if transfer <= r['year'] <= transfer + horizon_years),
        move_in_value=horizon_row['value'],
        horizon_year=transfer + horizon_years,
        horizon_row=horizon_row,
    )


def exclusion_projection(years=(2040, 2050)):
    """Federal estate exclusion: published 2027 anchor, then assumed indexation."""
    out = []
    for y in range(years[0], years[1] + 1):
        out.append((y, P['exclusion_2027'] * (1 + P['estate_growth']) ** (y - 2027)))
    return out
