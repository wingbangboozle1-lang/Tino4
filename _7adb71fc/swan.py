"""Black-swan and historical replay using only official published series.

Three things are computed, and each is labelled on the site:

1. REPLAY - the actual published history. FHFA California all-transactions HPI
   1975Q1-2026Q2 for prices, and the BOE assessment-factor table for the
   property-tax side. No invention, no smoothing.
2. WINDOWS - a 50-year holding period starting at every possible quarter, so a
   buyer can see how much the start date mattered. This is observation of a
   single realised path, not a probability.
3. STRESS - named adverse sequences applied on top of the case projection. These
   are invented, and are labelled Synthetic everywhere they appear.
"""
from case_data import CA_HPI, BOE_FACTORS, BOE_CCPI, BOE_START, EPISODES, P

QN = {1: 0.00, 2: 0.25, 3: 0.50, 4: 0.75}


def t(key):
    """Decimal year for a (year, quarter) key, for annualising."""
    return (key[0] - 1) + key[1] / 4


def cagr(a, b):
    ya, yb = t(a), t(b)
    return ((CA_HPI[b] / CA_HPI[a]) ** (1 / (yb - ya)) - 1) * 100


def episodes():
    """Named drawdowns, measured straight from the published series."""
    out = []
    for name, y0, q0, y1, q1, note in EPISODES:
        a, b = (y0, q0), (y1, q1)
        out.append(dict(name=name, start=a, end=b, change=(CA_HPI[b] / CA_HPI[a] - 1) * 100,
                        years=t(b) - t(a), note=note))
    vals = sorted(CA_HPI)
    peak = vals[0]
    worst = (0.0, None, None)
    for k in vals:
        if CA_HPI[k] > CA_HPI[peak]:
            peak = k
        dd = (CA_HPI[k] / CA_HPI[peak] - 1) * 100
        if dd < worst[0]:
            worst = (dd, peak, k)
    high = vals[-1]
    return out, dict(trough_pct=worst[0], peak=worst[1], trough=worst[2],
                     last=high, last_value=CA_HPI[high])


def recovery():
    """How long the state index took to regain its 2006 peak, and the longest such gap."""
    vals = sorted(CA_HPI)
    peak = (2006, 3)
    for k in vals:
        if k > peak and CA_HPI[k] >= CA_HPI[peak]:
            return dict(years=t(k) - t(peak), quarter=k)
    return None


def longest_flat():
    vals = sorted(CA_HPI)
    best, pair, pk = 0.0, None, vals[0]
    for k in vals:
        if CA_HPI[k] >= CA_HPI[pk]:
            pk = k
        gap = t(k) - t(pk)
        if gap > best:
            best, pair = gap, (pk, k)
    return best, pair


def annual_returns():
    """Calendar-year changes in the published index, for the shape of risk."""
    years = sorted({k[0] for k in CA_HPI})
    out = []
    for y in years:
        if (y, 4) in CA_HPI and (y - 1, 4) in CA_HPI:
            out.append((y, (CA_HPI[(y, 4)] / CA_HPI[(y - 1, 4)] - 1) * 100))
    return out


def start_windows(hold_years=50):
    """Every start quarter with a complete holding period."""
    starts = [k for k in sorted(CA_HPI) if t(k) + hold_years <= t((2026, 2)) + 0.001]
    out = []
    for s in starts:
        target = t(s) + hold_years
        ends = [k for k in sorted(CA_HPI) if abs(t(k) - target) < 0.001]
        if not ends:
            continue
        e = ends[0]
        out.append(dict(start=s, end=e, cagr=((CA_HPI[e] / CA_HPI[s]) ** (1 / hold_years) - 1) * 100,
                        nominal=CA_HPI[e] / CA_HPI[s]))
    return out


def assessment_replay(years=50):
    """The property-tax side: what the 2% cap actually did over the same 50 years."""
    f = BOE_FACTORS[-years:]
    c = BOE_CCPI[-years:]
    prod = 1.0
    for x in f:
        prod *= x
    cpi = 1.0
    for x in c:
        cpi *= 1 + x / 100
    return dict(years=years,
                factor_cagr=(prod ** (1 / years) - 1) * 100,
                ceil_cagr=(1.02 ** years) ** (1 / years) - 1 and 2.0,
                captured_ratio=prod / (1.02 ** years) * 100,
                below_ceiling=sum(1 for x in f if x < 1.02),
                negative=sum(1 for x in c if x < 0),
                cpi_cagr=(cpi ** (1 / years) - 1) * 100,
                real_assessment_cagr=((prod ** (1 / years)) / (cpi ** (1 / years)) - 1) * 100)


def applied_shocks(value_2031, shocks):
    """Apply a named invented shock path to a property value."""
    v = value_2031
    path = [v]
    for s in shocks:
        v *= 1 + s
        path.append(v)
    return path


SHOCKS = {
 'Housing crash, credit crisis shape': [-0.32, -0.09, 0.01, 0.06, 0.12, 0.09, 0.06, 0.05, 0.04, 0.04],
 'Slow bleed, Japan 1990s shape': [-0.06, -0.08, -0.07, -0.05, -0.04, -0.03, -0.02, -0.01, 0.00, 0.01],
 'Inflation surge, 1970s shape': [0.08, 0.10, 0.09, 0.06, 0.03, 0.01, 0.01, 0.02, 0.03, 0.03],
 'Rates up, prices flat for a decade': [0.00, 0.01, 0.00, -0.02, -0.01, 0.01, 0.02, 0.02, 0.03, 0.03],
 'Insurance withdrawal and repair bulge': [0.02, 0.03, 0.02, 0.01, 0.00, 0.01, 0.02, 0.03, 0.03, 0.03],
}
