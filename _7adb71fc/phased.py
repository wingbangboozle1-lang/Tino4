"""Phased-investing test: park sale proceeds in short Treasuries, then phase into stocks.

Inputs are official quarterly averages from FRED (see data/README.md):
  share_index  - OECD broad share-price index for the United States (2015=100). Price only, not the S&P 500.
  tb           - 3-month Treasury bill, discount basis (lower than the investment yield).
  gs           - 2-year Treasury constant maturity, investment basis.

Everything is expressed per 100 of sale proceeds, so no dollar amount is invented. Parking earns the
quarterly-average yield, compounded quarterly. Phasing deploys an equal share of the remaining cash in
each of four quarters after the parking period. Standard library only; no network at build time.

Limits, stated on the page: quarterly averages cannot time an entry to a day; the stock proxy omits
dividends, which flatters the phased path relative to lump sum; taxes, fees and bid-ask spreads are ignored.
"""
import csv
import statistics
from pathlib import Path

DATA = Path(__file__).resolve().parent / 'data' / 'fred_quarterly_1976Q1_2026Q3.csv'

PHASE_QUARTERS = 4                     # deploy over 12 months
PATHS = [                              # name, parked quarters, yield column used while parked
    ('Lump sum into stocks at entry', 0, None),
    ('Park 24 months in 3-month bills, then phase over 12 months', 8, 'tb'),
    ('Park 24 months in 2-year notes, then phase over 12 months', 8, 'gs'),
    ('Park 36 months in 3-month bills, then phase over 12 months', 12, 'tb'),
    ('Park 36 months in 2-year notes, then phase over 12 months', 12, 'gs'),
]
EPISODES = ['1987Q3', '1990Q3', '2000Q3', '2007Q3', '2007Q4', '2019Q4']
HORIZON_Q = {'5 years': 20, '10 years': 40}


def load(path=DATA):
    rows = []
    with path.open(newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            rows.append(dict(
                label=r['quarter'],
                idx=float(r['share_index_2015_100_qavg']),
                tb=float(r['tb3ms_pct_qavg']) if r['tb3ms_pct_qavg'] else None,
                gs=float(r['gs2_pct_qavg']) if r['gs2_pct_qavg'] else None))
    return rows


def index_of(rows, label):
    for i, r in enumerate(rows):
        if r['label'] == label:
            return i
    raise KeyError(label)


def path_wealth(rows, s, park, key, horizon):
    """Value of 1.0 of proceeds at the end of each quarter from entry quarter s for `horizon` quarters."""
    if s + horizon >= len(rows):
        raise ValueError('horizon runs past the published data')
    cash = 1.0 if park else 0.0
    shares = 0.0 if park else 1.0 / rows[s]['idx']
    deploy_quarters = {s + park + j for j in range(PHASE_QUARTERS)} if park else set()
    remaining = PHASE_QUARTERS
    wealth = [1.0]
    for k in range(s + 1, s + horizon + 1):
        if cash:
            rate = rows[k][key]
            if rate is None:
                raise ValueError(f'no {key} yield for {rows[k]["label"]}')
            cash *= 1 + rate / 100 / 4
        if k in deploy_quarters:
            spend = cash / remaining
            shares += spend / rows[k]['idx']
            cash -= spend
            remaining -= 1
        wealth.append(cash + shares * rows[k]['idx'])
    return wealth


def summarise(wealth, horizon):
    end = wealth[-1]
    return dict(end=(end - 1) * 100 + 100,                    # value per 100 of proceeds
                worst=(min(wealth) - 1) * 100,                # deepest point vs entry, percent
                per_year=(end ** (4 / horizon) - 1) * 100)    # compound annual rate


def episode_table(rows):
    out = []
    for label in EPISODES:
        s = index_of(rows, label)
        for name, park, key in PATHS:
            cells = {}
            for hname, h in HORIZON_Q.items():
                if s + h < len(rows):
                    cells[hname] = summarise(path_wealth(rows, s, park, key, h), h)
                else:
                    cells[hname] = None
            out.append(dict(episode=label, path=name, park=park, key=key, cells=cells))
    return out


def rolling(rows, horizon, park, key):
    """Every entry quarter with a full horizon, from the first quarter with a 2-year yield."""
    first = 2
    diffs, shallower, wins = [], [], 0
    n = 0
    for s in range(first, len(rows) - horizon):
        lump = path_wealth(rows, s, 0, None, horizon)
        ph = path_wealth(rows, s, park, key, horizon)
        d = summarise(ph, horizon)['end'] - summarise(lump, horizon)['end']
        diffs.append(d)
        if d > 0:
            wins += 1
        if min(ph) > min(lump):
            shallower.append(1)
        n += 1
    return dict(windows=n, phased_ends_higher=wins / n * 100,
                median_gap=statistics.median(diffs),
                shallower_share=len(shallower) / n * 100)


def results():
    rows = load()
    return dict(
        first=rows[0]['label'], last=rows[-1]['label'], quarters=len(rows),
        first_test=rows[2]['label'],
        episodes=episode_table(rows),
        rolling={(name, hname): rolling(rows, h, park, key)
                 for name, park, key in PATHS[1:] for hname, h in HORIZON_Q.items()},
        worst_lump=min(summarise(path_wealth(rows, s, 0, None, 40), 40)['worst']
                       for s in range(2, len(rows) - 40)),
    )


if __name__ == '__main__':
    r = results()
    print('data', r['first'], '->', r['last'], r['quarters'], 'quarters')
    for e in r['episodes']:
        c5 = e['cells']['5 years']
        c10 = e['cells']['10 years']
        f = lambda c, k: '' if c is None else f"{c[k]:.1f}"
        print(f"{e['episode']} {e['path'][:44]:44s} 5y end {f(c5,'end'):>7s} worst {f(c5,'worst'):>7s} | 10y end {f(c10,'end'):>7s} worst {f(c10,'worst'):>7s}")
    for k, v in r['rolling'].items():
        print(k, {a: round(b, 1) for a, b in v.items()})
    print('worst lump-sum point, all 10-year windows:', round(r['worst_lump'], 1))
