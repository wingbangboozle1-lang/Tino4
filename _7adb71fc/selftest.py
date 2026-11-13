"""Arithmetic self-checks that must pass before the site is written."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '_7eff7e24'))
sys.path.insert(0, str(ROOT / '_7adb71fc'))

from case_data import A, B, CA_HPI, BOE_FACTORS, BOE_CCPI
from case_model import rounded, projection, path_comparison, allowance, money
import swan

fail = []


def check(name, condition):
    if not condition:
        fail.append(name)


check('round 125 -> 130', rounded(125) == 130)
check('round 124.99 -> 120', rounded(124.99) == 120)
check('round -125 -> -130', rounded(-125) == -130)
check('money negative sign', money(-125).startswith('\u2212'))

rows = projection('A', transfer=2045)
check('51 rows', len(rows) == 51)
check('start 2026', rows[0]['year'] == 2026)
check('end 2076', rows[-1]['year'] == 2076)

check('no reset before transfer',
      abs(rows[18]['tax_assessed'] - A['assessed_2026'] * 1.02 ** 18) < 1)
check('reset at transfer', abs(rows[19]['tax_assessed'] - rows[19]['value']) < 1)
check('A unaffected before transfer', abs(rows[0]['tax_assessed'] - A['assessed_2026']) < 1)
rowsb = projection('B')
check('no reset for B', abs(rowsb[19]['tax_assessed'] - B['assessed_2026'] * 1.02 ** 19) < 1)

for r in rows:
    if r['tax_qualified'] > r['value'] + 1:
        fail.append('qualified assessment above market value at ' + str(r['year']))
    if r['tax_qualified'] < r['assessed'] - 1:
        fail.append('qualified assessment below the carried base at ' + str(r['year']))

check('allowance present', allowance(2026) == 1_044_590)

c = path_comparison(2045)
check('reinvest above rental', c['reinvest_after_tax'] > c['rental_total'])
check('rental cash negative', c['rental_income_20y'] < 0)
check('sale net below price',
      c['sale_net'] < c['sale_price'] * (1 - 0.05) and c['sale_net'] > c['sale_price'] * 0.92)

for r in projection('A', transfer=2040) + projection('B'):
    for k in ('value', 'tax_assessed', 'tax_qualified', 'bill_full', 'bill_qualified',
              'insurance', 'water', 'electric', 'maintenance', 'rent'):
        if rounded(r[k]) % 10:
            fail.append('unrounded ' + k)

check('HPI quarters', len(CA_HPI) == 206)
check('HPI last value', CA_HPI[(2026, 2)] == 974.97)
check('BOE factors', len(BOE_FACTORS) == 51 and len(BOE_CCPI) == 51)
check('replay 1975-2026 about 6.35%', abs(swan.cagr((1975, 1), (2026, 2)) - 6.35) < 0.02)
eps, dd = swan.episodes()
check('worst drawdown about 41%', abs(dd['trough_pct'] + 41.04) < 0.1)
check('recovery about 12.75 years', abs(swan.recovery()['years'] - 12.75) < 0.01)
a = swan.assessment_replay()
check('assessment replay about 1.81%', abs(a['factor_cagr'] - 1.81) < 0.02)
check('assessment below ceiling years', a['below_ceiling'] == 11)
check('real assessment negative', a['real_assessment_cagr'] < 0)
check('every start window positive',
      all(w['cagr'] > 0 for w in swan.start_windows()))

if fail:
    for f in fail:
        print('FAIL:', f)
    print(len(fail), 'self-check failures')
    sys.exit(1)
print(f'Self-checks passed: {len(CA_HPI)} index quarters, {len(BOE_FACTORS)} factor years, '
      f'{len(rows)} projection rows per case.')
