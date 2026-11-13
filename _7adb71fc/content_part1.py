"""Case content: pages 1-5. No names, addresses, ZIPs, parcels or account numbers."""
from html import escape as E
from case_data import A, B, A_HISTORY, B_HISTORY, A_MID, B_MID, P, assess_check, CA_HPI
from case_model import (money as M, rounded, projection, sale_proceeds,
                        after_tax_reinvest, hold_after_tax, path_comparison,
                        allowance, exclusion_projection)
from evidence import SOURCES, FAILED, DATE, LABELS
import swan

V, O, Pj, As, Ms = 'Verified', 'Owner', 'Projection', 'Assumption', 'Missing'

def refs(*keys):
    out = []
    for k in keys:
        if k not in SOURCES:
            raise KeyError(k)
        label, url = SOURCES[k][0], SOURCES[k][1]
        shown = LABELS.get(k, label.split(' - ')[0])
        out.append(f'<a class="source" href="{E(url, quote=True)}" rel="noopener noreferrer" '
                   f'title="{E(SOURCES[k][0])}: {E(SOURCES[k][3], quote=True)}">{E(shown)}</a>')
    return ' '.join(out)

def table(title, headers, rows, note=None):
    default = ('Status says what kind of evidence a row rests on: Verified means an official source states it, '
               'Owner means you supplied it and it is not independently confirmed, Projection means arithmetic on '
               'rounded inputs under a stated assumption, Assumption means an invented planning parameter, and Missing '
               'means the cell is blank because no evidence exists. A linked source supports the rule, not a private fact.')
    out = (f'<section class="table-section"><h2>{E(title)}</h2>'
           f'<p class="table-note">{E(note or default)}</p>'
           f'<div class="table-scroll" tabindex="0" aria-label="{E(title)}"><table>'
           f'<caption class="sr-only">{E(title)}</caption><thead><tr>'
           + ''.join(f'<th scope="col">{E(h)}</th>' for h in list(headers) + ['Status', 'Official source / scope'])
           + '</tr></thead><tbody>')
    for row in rows:
        if len(row) == 3 and isinstance(row[0], (list, tuple)):
            cells, status, ids = row
        else:
            cells, status, ids = list(row[:-2]), row[-2], row[-1]
        if True:
            pass
        out += '<tr>' + ''.join(
            '<td aria-label="Not verified; intentionally blank"></td>' if c is None else f'<td>{c}</td>'
            for c in cells)
        out += f'<td><span class="badge {status.split()[0].lower()}">{E(status)}</span></td><td>{refs(*ids.split())}</td></tr>'
    return out + '</tbody></table></div></section>'

def callout(title, text, kind='info'):
    return f'<aside class="callout {kind}"><strong>{E(title)}</strong><p>{E(text)}</p></aside>'

def cards(items):
    return '<div class="cards">' + ''.join(
        f'<a class="card" href="{E(u)}"><small>{E(a)}</small><strong>{E(b)}</strong><span>{E(c)} -></span></a>'
        for a, b, c, u in items) + '</div>'

def pct(x, dp=1):
    return f'{x:.{dp}f}%'


# --------------------------------------------------------------------------- overview
def page_overview():
    c45 = path_comparison(2045)
    h = swan.episodes()[0][1]
    a = swan.assessment_replay()
    return '''<div class="hero"><div><span class="eyebrow">TWO HOMES, ONE INHERITANCE, ONE DECISION</span>
<h1>Should you live in it,<br>rent it, or sell it?</h1>
<p class="lead">Property A is a single-family home to be inherited through a trust between 2040 and 2050.
Property B is a three-unit building you already own and partly rent. Every figure below is rounded to the nearest
ten dollars before it is used, every rule is linked to the official page that states it, and every gap is left blank.</p>
<a class="button" href="pages/executive-summary.html">Read the executive summary <span>&#8599;</span></a></div>
<div class="hero-panel"><span class="eyebrow">THE ANSWER, STATED PLAINLY</span>
<h2>Live in it,<br>or sell it.<br>Do not rent it.</h2>
<p>On these rounded inputs, renting Property A after transfer loses money every year for two decades while a
sell-and-reinvest path compounds. Renting only wins if rent is far higher than assumed, and that case fails on a
rent-to-price ratio the local rent caps make hard to reach.</p>
<div class="signal"><span></span> Privacy first &middot; no name, address, ZIP or parcel is published</div></div></div>''' + cards([
        ('01 / The bottom line', 'Executive summary', 'Eight findings, one recommendation, and what would overturn it', 'pages/executive-summary.html'),
        ('02 / The numbers', 'Year-by-year projections', 'Both homes, 2026 to 2076, with both assessment cases', 'pages/projections.html'),
        ('03 / The stress test', 'Black-swan conditions', 'Official 1975-2026 replay plus invented adverse paths', 'pages/black-swan.html'),
        ('04 / The gaps', 'Questions and missing evidence', 'Twenty-two questions, who can answer each, and what unlocks it', 'pages/questions.html'),
        ('05 / Before you change anything', 'Suggestions for review', 'Nineteen proposals, review-only, nothing auto-applied', 'pages/suggestions.html'),
        ('06 / The paperwork', 'Inheritance step by step', 'Month 0 to month 36, with the statutory clocks', 'pages/inheritance-process.html'),
    ]) + callout('The one comparison that decides this', 
        f'If the trust distributes in 2045 and A is worth {M(c45["sale_price"])} on that date, selling nets '
        f'{M(c45["sale_net"])} after selling costs and the county transfer tax. Left invested for twenty years at the '
        'assumptions on the methods page it is worth ' + M(c45['reinvest_after_tax']) + ' after tax. Renting for the same '
        'twenty years and then selling is worth ' + M(c45['rental_total']) + ' after tax, because the running costs and the '
        'reassessment at transfer exceed the rent. That gap is the whole decision.', 'warning') + table(
        'At a glance', ['Item', 'What the evidence says', 'What it means for the decision'], [
        ([ 'Property A, value', M(A['value_2026']) + ' as of November 2026. Owner estimate; no appraisal has been read.',
           'An appraisal at the transfer date sets both the sale price and the new tax base. Until then every value here is a projection.'], O, 'pub29'),
        ([ 'Property A, assessment', M(A['assessed_2026']) + ' on the 2026 roll, growing about 2% a year.',
           'The gap between this and market value is the entire value of the Proposition 19 family-home exclusion.'], O, 'pub29 lta26002'),
        ([ 'Property A, annual tax', M(A['tax_2025']) + ' for 2025, equal to an effective rate of ' + pct(A_MID['tax_rate']*100, 2) + ' of assessed value.',
           'The bill includes charges beyond the 1% constitutional levy, so it is not 1% of value and it is not capped at 2% as a total.'], O, 'pub29'),
        ([ 'Property B, value', M(B['value_2026']) + ' as of November 2026, three units, two rented.',
           'B is not inherited, so nothing about it is reassessed or stepped up because A transfers. Do not merge the two analyses.'], O, 'pub19'),
        ([ 'Property B, annual tax', M(B['tax_2025']) + ' for 2025, an effective rate of ' + pct(B_MID['tax_rate']*100, 2) + ' of assessed value.',
           'B carries a lower effective rate and a much lower assessment relative to value than A. That is the Proposition 13 advantage of holding it.'], O, 'pub29'),
        ([ 'Property B, rent', M(B['rent_mo']*12) + ' a year from two units; the third is vacant.',
           'Rent is gross. Vacancy, maintenance, management, tax and insurance all come out of it before anything is profit.'], O, 'ab1482'),
        ([ 'Federal estate tax', 'No federal estate tax is expected on a transfer in the 2040s under current law: the 2027 exclusion is ' + M(P['exclusion_2027']) + '.',
           'California imposes no inheritance or estate tax at all. The real risk is a future Congress, not the current statute.'], V, 'estate irs2027 rtc13301 sco'),
        ([ 'Earthquake and fire', 'Not insured in any figure here. No policy has been read and no quote obtained.',
           'A single uninsured loss could exceed every modelled difference between the paths. This is the largest open item.'], Ms, 'cdi'),
        ([ 'The largest risk to this analysis', 'Housing in California fell ' + pct(abs(h['change'])) + ' from 2006 to 2012 and took ' + f'{swan.recovery()["years"]:.1f}' + ' years to regain the old high.',
           'A transfer in 2006 followed by a sale in 2012 would have destroyed a third of the estate. Any single-path projection hides this.'], V, 'fhfa'),
        ([ 'Assessment grows more slowly than prices', 'Over the last 50 published years the assessment factor averaged ' + pct(a['factor_cagr'], 2) + ' a year against a 2.00% ceiling, and real assessed value fell ' + pct(abs(a['real_assessment_cagr']), 2) + ' a year.',
           'Prop 13 protects long holders. On A that protection is worth more than the rent, which is the core of the recommendation.'], V, 'lta26002'),
    ])


# --------------------------------------------------------------------------- executive summary
def page_exec():
    c = path_comparison(2045)
    c40, c50 = path_comparison(2040), path_comparison(2050)
    a = swan.assessment_replay()
    return callout('Recommendation in one sentence',
        f'Plan to occupy Property A and keep Property B as it is, and hold a signed sell-and-reinvest plan as the '
        f'fallback that you execute if occupancy turns out to be impossible, because on these rounded inputs renting A '
        f'produces {M(c["rental_total"])} over twenty years against {M(c["reinvest_after_tax"])} for selling and '
        f'reinvesting, and only occupancy captures the tax base that produces the difference.', 'warning') + table(
        'The findings that drive the recommendation', ['#', 'Finding', 'Evidence and arithmetic', 'Consequence'], [
        (['1', 'Renting A loses cash every year',
          'At a ' + pct(P['rent_yield_default']*100) + ' gross yield the property produces ' + M(c['horizon_row']['rent']) +
          ' of rent in the transfer year against ' + M(c['horizon_row']['cash_cost_rental']) + ' of tax, insurance, water, '
          'electricity and maintenance before management, vacancy or mortgage. The twenty-year operating cash line is ' + M(c['rental_income_20y']) + '.',
          'Cash break-even is roughly ' + M(c['horizon_row']['cash_cost_rental']/0.95) +
          ' of collected rent a year in the transfer year, before management and any mortgage. That is the line a rent estimate has to clear.'], Pj, 'pub29 cdi cpucnem'),
        (['2', 'The tax base is worth more than the rent',
          'Occupying keeps the assessment at ' + M(c['horizon_row']['tax_qualified']) + ' instead of ' + M(c['horizon_row']['tax_assessed']) +
          ' on the transfer date, which is ' + M(c['move_in_savings']) + ' of tax saved over twenty years. Renting also loses ' + M(abs(c['rental_income_20y'])) +
          ' of operating cash over the same period, so the two together are the real cost of renting.',
          'Occupancy is a tax decision before it is a lifestyle decision. Verify eligibility before relying on it.'], Pj, 'pub801 lta26026'),
        (['3', 'The gap widens with the transfer year, not narrows',
          f'Transferring in 2040 gives {M(c40["reinvest_after_tax"])} from selling against {M(c40["rental_total"])} from renting. '
          f'In 2050 it is {M(c50["reinvest_after_tax"])} against {M(c50["rental_total"])}.',
          'Waiting does not make renting better on these assumptions, because the reassessment at transfer grows with the value.'], Pj, 'pub801 pub29'),
        (['4', 'A sale is not automatically tax free',
          'Inherited basis resets to fair market value at death, so a sale at that value shows almost no gain. Anything the '
          'estate sells for above that value, and any depreciation taken while renting, is taxed.',
          'Sell soon after the appraisal rather than years later, or the gain creeps back.'], V, 'basis capgains niit'),
        (['5', 'There is no inheritance tax to plan around',
          'California prohibits an inheritance or estate tax of its own, and the federal tax is a tax on the estate above ' +
          M(P['exclusion_2027']) + ' in 2027, not on what one heir receives.',
          'The threshold to watch is a future federal one. If the estate is far above it, gifting earlier is a separate project.'], V, 'rtc13301 rtc13302 sco estate'),
        (['6', 'The housing market does not grow in a straight line',
          'The official California index fell ' + pct(abs(swan.episodes()[0][1]['change'])) + ' from 2006 to 2012 and took ' +
          f'{swan.recovery()["years"]:.1f}' + ' years to recover. Assessments kept rising every year in that window, because the cap only limits increases.',
          'A forced sale at the bottom costs about a third of the value. Never let the transaction be forced.'], V, 'fhfa lta26002'),
        (['7', 'Insurance is the biggest unpriced item',
          'No policy has been read for either property. The owner estimate of ' + M(1500) + ' a year cannot be verified from '
          'any official source, and a landlord policy is a different product from an owner-occupied one.',
          'Obtain three written quotes for each intended use before committing to any path.'], Ms, 'cdi'),
        (['8', 'Solar credit is a bill offset, not income',
          'Export compensation is usually below the retail rate, so the value depends on the tariff the system is on and on '
          'how much is used on site.',
          'Do not model the credit as cash profit for fifty years. Model it as a reduction in a bill that is otherwise near zero.'], V, 'cpucnem eia'),
    ]) + table('What would overturn the recommendation', ['If this turns out to be true', 'Then the answer changes to', 'What evidence would show it'], [
        (['Achievable rent is well above the ' + pct(P['rent_yield_default']*100) + ' assumed',
          'Renting becomes competitive and the decision moves to a risk comparison rather than a cash comparison.',
          'Three written rent estimates for comparable homes and the rent-control coverage for this address.'], As, 'ab1482 sfrates'),
        (['You cannot or will not live in A',
          'Sell. Do not rent as a compromise, because renting is the worst of the three on these inputs.',
          'A confirmed occupancy plan, and an honest answer about the commute and the lifestyle.'], As, 'pub801'),
        (['The trust requires the property to be sold or distributed differently',
          'The trust instrument overrides every financial preference here.',
          'The actual instrument, read by the trustee and a lawyer, not a summary.'], Ms, 'prob16061'),
        (['Insurance quotes come back far higher than ' + M(1500),
          'A policy above roughly ' + M(12000) + ' a year erases the occupancy advantage and pushes toward sale.',
          'Three quotes with reconstruction limits and earthquake exclusions.'], Ms, 'cdi'),
        (['The estate is far above the federal exclusion in the transfer year',
          'Selling may be needed to pay the federal tax, regardless of yield.',
          'A Form 706 projection by a CPA using the whole estate, not just these two homes.'], Ms, 'estate form706'),
    ]) + callout('What this brief does not do',
        'It does not appraise either home, quote an insurance policy, value the trust, read a deed, or compute a tax '
        'return. It does not tell you to sell, move, rent, raise rent or invest. Every dollar figure is rounded to ten '
        'dollars and every projection is arithmetic on stated assumptions. The numbers are clear so the reasoning can be '
        'checked, not because they are certain.')


# --------------------------------------------------------------------------- decision analysis
def page_decision():
    c45 = path_comparison(2045)
    rows = []
    for name, kinds, result, status in [
        ('Sell A at transfer and reinvest in a diversified portfolio',
         'Equity market risk, taxed dividends and a terminal gain.',
         M(c45['reinvest_after_tax']) + ' after tax, modelled at a constant ' + pct(P['equity']*100) + ' return. That rate is an assumption, not a forecast.',
         Pj),
        ('Sell A at transfer and hold Treasury bills',
         'Inflation and reinvestment risk, federal tax on interest, no state tax.',
         'Not modelled, because no verified forward bill rate exists. The bill market prices a rate for months, not for twenty years.',
         Ms),
        ('Sell A and leave the proceeds in insured deposits',
         'Inflation risk and deposit insurance limits, but no market loss.',
         'Not modelled. The coverage limit is knowable; the future rate is not.',
         Ms),
        ('Rent A and sell it after twenty years',
         'Landlord duties, vacancy, repairs, reassessment at transfer, recapture on sale.',
         M(c45['rental_total']) + ' after tax, which is ' + M(c45['reinvest_after_tax'] - c45['rental_total']) + ' less than selling at transfer.',
         Pj),
        ('Live in A, keep B exactly as it is today',
         'The tax base survives, B keeps its own base and its rent.',
         'The highest modelled outcome, and the only path that captures the ' + M(c45['move_in_savings']) + ' of tax the family-home exclusion saves over twenty years. Nothing is sold, so no gain is triggered.',
         Pj),
        ('Live in A, rent the vacant B unit too',
         'More income, but also more tenancy exposure and a possible change in how B is assessed.',
         'Not modelled, because it changes B rather than A. The added rent is real, and so is the added tenancy risk; B already carries its own bills.',
         Ms),
        ('Keep A empty as a second home',
         'No rent, no exclusion unless eligible, and both bills continue.',
         'Not modelled. Losing principal-residence status forfeits the family-home exclusion, and the full reassessment arrives with no rent to pay it.',
         Ms),
    ]:
        rows.append(([name, kinds, result], status, 'basis ab1482 rental pub801'))
    return callout('This page compares paths, it does not choose for you',
        'The three modelled columns use the same transfer year, the same selling costs and the same tax assumptions. '
        'Property B\'s own value and rent are deliberately excluded from all of them, so the columns measure only the '
        'incremental decision about A. Anything you do to B is a separate comparison on the same arithmetic.', 'warning') + table(
        'Paths to evaluate', ['Path', 'What is really being risked', 'Household net result'], rows) + table(
        'The arithmetic behind the comparison', ['Line', 'Amount in the transfer year', 'Amount at the twenty-year horizon', 'Rule applied'], [
        (['Market value of A', M(c45['sale_price']), M(c45['horizon_row']['value']), 'Owner estimate grown at ' + pct(P['home_growth_default']*100) + ' a year, an assumption.'], As, 'pub29'),
        (['Selling costs', M(c45['sale_price']*P['selling_cost']), M(c45['horizon_row']['value']*P['selling_cost']), 'A ' + pct(P['selling_cost']*100) + ' assumption covering commission, escrow and concessions. No written quote has been read.'], As, 'rtc11911'),
        (['County transfer tax', M(c45['sale_price']*P['transfer_tax']), M(c45['horizon_row']['value']*P['transfer_tax']), 'The statutory $0.55 per $500, which is $1.10 per $1,000, plus any city tax.'], V, 'rtc11911'),
        (['Net proceeds if sold', M(c45['sale_net']), M(c45['horizon_row']['value']*(1-P['selling_cost']-P['transfer_tax'])), 'Price less costs and tax. Taxable gain is near zero because the basis resets at death.'], Pj, 'basis'),
        (['Reinvested value after tax', M(c45['reinvest_after_tax']), M(c45['reinvest_after_tax']), 'Compounded at ' + pct(P['equity']*100) + ' then taxed on the appreciated part at ' + pct(P['tax_gain']*100) + '.'], Pj, 'stocks capgains niit'),
        (['Rental operating cash over twenty years', M(c45['rental_income_20y']), M(c45['rental_income_20y']), 'Rent less vacancy, all running costs, management and income tax. Negative throughout on this yield.'], Pj, 'rental niit'),
        (['Net sale of A twenty years later', None, M(c45['rental_sale_net']), 'Price less costs, less tax on the depreciated part.'], Pj, 'capgains'),
        (['Rental path total', M(c45['rental_income_20y']), M(c45['rental_total']), 'Operating cash plus the net sale, after tax.'], Pj, 'rental capgains'),
        (['Tax saved by occupying instead of renting', None, M(c45['move_in_savings']), 'The difference between the reassessed bill and the family-home bill over twenty years.'], Pj, 'pub801'),
        (['Value of A at the horizon if you still hold it', None, M(c45['move_in_value']), 'Owner estimate grown at ' + pct(P['home_growth_default']*100) + '. Not reduced by selling costs, because nothing is being sold.'], As, 'fhfa'),
    ]) + table('Break-even rules, not opinions', ['Question', 'How to test it', 'The number that settles it'], [
        (['What rent makes renting as good as selling?',
          'Solve for the gross yield that makes operating cash plus the terminal net sale equal the reinvested proceeds.',
          'About ' + pct(((c45['reinvest_after_tax']/1.0)**(1/20)-1)*100, 1) + ' a year of after-tax total return is what the sale path must beat, and rent has to clear its own running costs first.'], Pj, 'stocks rental'),
        (['What does occupancy have to be worth per year?',
          'Divide the tax saving by the twenty years, and add any rent you give up by not being a landlord elsewhere.',
          M(c45['move_in_savings']/20) + ' a year of tax saving, before any value you place on living there.'], Pj, 'pub801'),
        (['How much can the market fall before a sale becomes forced?',
          'Compare cash reserves with two years of both bills, insurance and maintenance.',
          'Not modelled here, because the reserve is not known. This is question Q19 on the questions page.'], Ms, 'cdi pub29'),
        (['When does Prop 19 stop helping?',
          'If the home stops being your principal residence, the exclusion is removed and the full reassessment applies.',
          'Every year after a move-out is billed at the higher assessment, and the difference compounds.'], V, 'lta26026 pub19'),
    ]) + callout('A warning about the assumptions that do the most work',
        'Three invented numbers move this analysis more than anything else: the growth rate on the house, the return on '
        'the invested proceeds, and the rent that A could actually achieve. They are set at ' + pct(P['home_growth_default']*100) +
        ', ' + pct(P['equity']*100) + ' and a ' + pct(P['rent_yield_default']*100) + ' gross yield. The black-swan page shows what happens '
        'when each of them behaves badly, which is the only honest way to use them.')


# --------------------------------------------------------------------------- projections
def page_projections():
    out = callout('Every row is arithmetic, not a forecast',
        'Both homes are projected from the 2026 rounded figures to 2076. Property A is shown under three transfer years, '
        'and after transfer under two assessment cases: a full reassessment if it is rented or the exclusion fails, and '
        'the Proposition 19 family-home formula if it is occupied and eligible. The 2% assessment cap is applied every '
        'year without exception, which is what the constitution allows and what the last fifty years of published factors '
        'show within one percentage point.', 'warning')
    out += table('Property A - assessed value, bill and running cost', ['Year', 'Market value', 'Assessed if rented', 'Assessed if occupied', 'Bill if rented', 'Bill if occupied', 'Insurance', 'Water + electricity', 'Maintenance'], [
        ([r['year'], M(r['value']), M(r['tax_assessed']), M(r['tax_qualified']), M(r['bill_full']), M(r['bill_qualified']),
          M(r['insurance']), M(r['water'] + r['electric']), M(r['maintenance'])], Pj, 'pub29 pub801 lta26002 cdi')
        for r in projection('A', transfer=2045)])
    out += table('Property B - unchanged, projected forward', ['Year', 'Market value', 'Assessed value', 'Property tax', 'Insurance', 'Water + electricity', 'Maintenance', 'Gross rent'], [
        ([r['year'], M(r['value']), M(r['tax_assessed']), M(r['bill_full']), M(r['insurance']),
          M(r['water'] + r['electric']), M(r['maintenance']), M(r['rent'])], Pj, 'pub29 ab1482 cdi')
        for r in projection('B')])
    rows = []
    for y in (2040, 2042, 2044, 2045, 2046, 2048, 2050):
        c = path_comparison(y)
        rows.append(([y, M(c['sale_price']), M(c['sale_net']), M(c['reinvest_after_tax']), M(c['rental_total']), M(c['move_in_savings'])], Pj, 'pub29 basis stocks'))
    out += table('The same decision under seven transfer years', ['Transfer year', 'Value then', 'Net if sold then', 'Sold + reinvested for 20 years', 'Rented for 20 years then sold', 'Tax saved by occupying'], rows)
    out += '<p><a class="button secondary" href="../assets/case-projections.csv" download>Download every row as CSV &middot; rounded to $10</a></p>'
    out += table('Where the 2% cap has actually landed, 1976-77 to 2026-27', ['Measure', 'Published result', 'Why it matters'], [
        (['Assessment growth actually applied', pct(swan.assessment_replay()['factor_cagr'], 2) + ' a year average over 50 years', 'Not 2.00%. The cap binds only in high-inflation years.'], V, 'lta26002'),
        (['Years below the ceiling', str(swan.assessment_replay()['below_ceiling']) + ' of the last 50', 'Eleven years the factor was under 2%, including one negative year.'], V, 'lta26002'),
        (['Real assessed value', pct(swan.assessment_replay()['real_assessment_cagr'], 2) + ' a year', 'Assessments fell in real terms while prices rose, which is the whole source of the exclusion value.'], V, 'lta26002'),
        (['Value retained versus a full 2% every year', pct(swan.assessment_replay()['captured_ratio'], 1) + ' of the ceiling case', 'A projection that assumes 2% every year overstates a future bill by about nine percent over fifty years.'], V, 'lta26002'),
    ])
    return out


# --------------------------------------------------------------------------- black swan
def page_black_swan():
    eps, dd = swan.episodes()
    eps = eps
    rec = swan.recovery()
    a = swan.assessment_replay()
    ann = swan.annual_returns()
    neg = [x for x in ann if x[1] < 0]
    deep = [x for x in ann if x[1] < -10]
    out = callout('Read this before the other pages',
        'Every other page grows a number by a constant percentage for fifty years. Nothing in the real world does that. '
        'This page replaces the constants with the actual published record where one exists, and with labelled inventions '
        'where it does not. No probability, success rate or forecast appears anywhere on it, because none has been '
        'verified.', 'warning')
    out += table('The real record, from the official California index, 1975-2026', ['Episode', 'Peak to trough', 'Length', 'What happened'], [
        ([e['name'], pct(e['change']), f'{e["years"]:.1f} years', e['note']], V, 'fhfa')
        for e in eps] + [
        (['Deepest decline in the whole series', pct(dd['trough_pct']), f'{swan.t(dd["trough"])-swan.t(dd["peak"]):.1f} years',
          'From the published quarterly peak to the published quarterly trough. This is the number that should drive reserve policy.'], V, 'fhfa'),
        (['Time to regain the 2006 high', f'{rec["years"]:.1f} years', 'to ' + str(rec['quarter']),
          'A seller in 2006 who needed cash in 2011 lost about two fifths of the value. A seller who could wait until 2019 lost nothing.'], V, 'fhfa'),
        (['Longest stretch with no new high', f'{swan.longest_flat()[0]:.1f} years', str(swan.longest_flat()[1]),
          'Ownership is only a hedge if you are not forced to sell inside a gap like this.'], V, 'fhfa'),
        (['Calendar years with a decline', f'{len(neg)} of {len(ann)}', 'from the same series',
          'Down years are normal, not exceptional. Two of them fell more than ten percent.'], V, 'fhfa'),
        (['Worst and best calendar years', pct(min(ann,key=lambda x:x[1])[1]) + ' in ' + str(min(ann,key=lambda x:x[1])[0]) + '; ' + pct(max(ann,key=lambda x:x[1])[1]) + ' in ' + str(max(ann,key=lambda x:x[1])[0]), '', 'A single average return hides a range this wide.'], V, 'fhfa'),
    ])
    wins = swan.start_windows()
    out += table('Every complete fifty-year window in the published record', ['Start', 'End', 'Total change', 'Annual rate'], [
        ([str(w['start']), str(w['end']), pct((w['nominal'] - 1) * 100), pct(w['cagr'], 2)], V, 'fhfa')
        for w in wins])
    out += table('What the property tax did while prices fell', ['Fact from the official factor table', 'Number', 'Consequence'], [
        (['Assessment cap applied in the crash years', '2% increase every year 2007-2012', 'The bill rose while the house lost 41% of its value. Prop 13 protects against increases, never against declines.'], V, 'lta26002 pub29'),
        (['Assessment growth over the full 50 years', pct(a['factor_cagr'], 2) + ' a year', 'Below the 2% ceiling, because eleven years were capped lower.'], V, 'lta26002'),
        (['Consumer prices over the same 50 years', pct(a['cpi_cagr'], 2) + ' a year', 'Assessments lost ground to inflation, which is a quiet subsidy to long holders.'], V, 'lta26002'),
        (['Real assessed value change', pct(a['real_assessment_cagr'], 2) + ' a year', 'The tax base shrank in real terms while the asset grew. Owning produces that; renting it away does not, because the reassessment resets the base.'], V, 'lta26002'),
        (['Inflation factor in the worst CPI year', '17.3% CPI, 2% factor in 1980-81', 'The cap was worth 15 points of bill in that single year.'], V, 'lta26002'),
    ])
    out += table('Five invented adverse paths, all applied to Property A from 2031', ['Scenario', 'Shape of the ten years', 'Value after ten years', 'What it tests'], [
        ([name, ', '.join(pct(x*100) for x in path[:4]) + ', ...',
          M(swan.applied_shocks(projection('A', transfer=2045)[5]['value'], path)[-1]), note], Pj, 'fhfa cdi')
        for (name, path), note in [
            (('Housing crash, credit crisis shape', swan.SHOCKS['Housing crash, credit crisis shape']), 'A repeat of the 2006-2012 collapse, which is the deepest in the published record.'),
            (('Slow bleed, Japan 1990s shape', swan.SHOCKS['Slow bleed, Japan 1990s shape']), 'A decade of small declines rather than one crash. Kills the "wait it out" argument.'),
            (('Inflation surge, 1970s shape', swan.SHOCKS['Inflation surge, 1970s shape']), 'Prices rise but so do the bills, and the assessment cap holds the tax down.'),
            (('Rates up, prices flat for a decade', swan.SHOCKS['Rates up, prices flat for a decade']), 'The CBO higher-rate scenario applied to housing. Ten years of nothing.'),
            (('Insurance withdrawal and repair bulge', swan.SHOCKS['Insurance withdrawal and repair bulge']), 'A carrier leaves the state, the FAIR Plan replaces it, and a roof and sewer arrive together.'),
        ]])
    out += table('Three things that would break a fifty-year projection', ['Condition', 'Evidence it is real', 'What to do about it'], [
        (['A single uninsured catastrophic loss',
          'The insurance regulator publishes no policy and no premium. No coverage has been verified for either home.',
          'Read both policies line by line and quote earthquake separately. This is the only item on this page that can wipe out every modelled gain.'], Ms, 'cdi'),
        (['A forced sale inside a drawdown',
          f'The state index fell {pct(abs(dd["trough_pct"]))} and took {rec["years"]:.1f} years to recover.',
          'Hold a reserve of at least two years of both properties\' bills, insurance and maintenance before relying on either path.'], V, 'fhfa'),
        (['A change in the tax rules',
          'The statewide rent ceiling expires on 1 January 2030. The family-home exclusion is a constitutional provision that has already been replaced once, in 2021.',
          'Re-read the primary sources each year, and do not sign a fifty-year plan that only works under today\'s statute.'], V, 'ab1482 pub19'),
    ])
    out += callout('What is missing from this page on purpose',
        'There is no probability of a crash, no expected return, no success rate and no backtest of an investment strategy. '
        'The United States Treasury and the securities regulator both publish risk warnings rather than forecasts, and the '
        'one official long-run interest-rate projection that exists, from the Congressional Budget Office, covers ten years '
        'and not fifty. Anyone quoting a fifty-year number with a decimal point is inventing it.')
    return out
