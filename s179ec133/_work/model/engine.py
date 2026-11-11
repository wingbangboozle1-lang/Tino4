#!/usr/bin/env python3
"""s-179ec133 — projection, decision and black-swan engine (Python standard library only).

Inputs : ../data/inputs.json            owner-supplied figures, already rounded to $10
         ../data/official/*.csv         official historical series (URL in each file header)
Output : ../data/results.json           every number the dashboard shows

Nothing here reads or writes an un-rounded owner-supplied figure.
Every parameter carries the id of the evidence-ledger entry (../research/ledger) that supports it,
or the word ASSUMPTION when no official source fixes the value.
"""
import csv, json, math, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
Y0, Y1 = 2026, 2076


def r10(x):
    """Round to the nearest $10 (half up)."""
    return int(math.floor(x / 10.0 + 0.5)) * 10


def read_csv(name):
    rows = [r for r in csv.reader(l for l in open(os.path.join(DATA, "official", name)) if not l.startswith("#"))]
    hdr = rows[0]
    return [{h: (float(v) if v != "" else None) for h, v in zip(hdr, r)} for r in rows[1:]]


INP = json.load(open(os.path.join(DATA, "inputs.json")))
A, B = INP["A"], INP["B"]
mid = lambda pair: (pair[0] + pair[1]) / 2.0

# --------------------------------------------------------------------------------------------
# Parameters.  src = evidence-ledger id, or ASSUMPTION.
# --------------------------------------------------------------------------------------------
PARAMS = [
    # key, value, unit, source id, plain-language note
    ("infl", 0.023, "rate", "CBO-OUTLOOK-2026", "Consumer price inflation, every year from 2027 (CBO long-run CPI-U projection)"),
    ("infl_2026", 0.028, "rate", "CBO-OUTLOOK-2026", "Consumer price inflation during 2026 (CBO)"),
    ("hpi_a", 0.030, "rate", "FRED-SERIES", "Home price growth, Property A: the San Jose metro FHFA index grew 3.0% a year from end-2005 to end-2025"),
    ("hpi_b", 0.027, "rate", "FRED-SERIES", "Home price growth, Property B: the San Francisco metro-division FHFA index grew 2.7% a year from end-2005 to end-2025"),
    ("hpi_ca", 0.022, "rate", "FRED-SERIES", "California FHFA index growth, 2.2% a year from end-2005 to end-2025 (drives the Proposition 19 allowance)"),
    ("eq", 0.07, "rate", "ASSUMPTION", "Stock total return used for planning. Not an official forecast: the official record is 11.6% a year for 1977-2025 and 1.6% a year for 2000-2012"),
    ("div", 0.013, "rate", "ERP-B56", "Dividend yield on stocks (S&P 500 yield was 1.34% in 2024 and 1.24% in 2025)"),
    ("t10_long", 0.044, "rate", "CBO-61912", "10-year Treasury yield from 2032 (CBO); 4.2%-4.3% in 2027-2031"),
    ("tb_long", 0.031, "rate", "CBO-61912", "3-month Treasury bill yield from 2033 (CBO); 3.2%-3.3% in 2027-2032. Used as the savings-account rate"),
    ("rent_mkt", 0.030, "rate", "ASSUMPTION", "Market rent growth, set equal to Property A price growth so the rent-to-value ratio stays constant (San Francisco-area rent CPI grew 3.5% a year 2005-2025)"),
    ("sf_rent_share", 0.60, "share", "SF-RENT-LEARN", "Rent-controlled rents in San Francisco may rise by 60% of Bay Area inflation"),
    ("rate_a", 0.0117, "rate", "SCC-TAXRATEBOOK-2025", "Property A tax rate. ASSUMPTION inside the official county range (1.147%-1.241%); the exact rate is on the owner's bill"),
    ("rate_b", 0.0118162182, "rate", "SF-TTX-SECURED", "Property B tax rate, San Francisco fiscal year 2026-27"),
    ("hox", 7000, "usd", "BOE-HOX", "Homeowners' exemption"),
    ("p13_cap", 0.02, "rate", "BOE-LTA-2026-002", "Yearly cap on assessed-value growth"),
    ("x19_2026", 1044586, "usd", "BOE-LTA-2025-009", "Proposition 19 allowance for transfers through February 15, 2027"),
    ("excl_2026", 15000000, "usd", "IRS-ESTATE", "Federal basic exclusion amount, 2026"),
    ("excl_2027", 15480000, "usd", "IRS-RP-2026-35", "Federal basic exclusion amount, 2027"),
    ("excl_gap", 0.0025, "rate", "ASSUMPTION", "The exclusion's yearly inflation adjustment is assumed to run 0.25 point below consumer price inflation (the published 2027 step was +3.2%)"),
    ("estate_rate", 0.40, "rate", "IRS-I706", "Top federal estate tax rate"),
    ("sell_comm", 0.05, "rate", "ASSUMPTION", "Agent commissions, escrow, title and preparation when selling. No official rate exists"),
    ("transfer_tax", 0.0011, "rate", "CA-RTC-11911", "County documentary transfer tax, $1.10 per $1,000"),
    ("rent_a_month", 5860, "usd", "HUD-FMR-FY2027", "Property A market rent in 2026 dollars. ASSUMPTION: midpoint of the official HUD 4-bedroom figure ($4,688) and HUD's own ceiling of 150% of it (about $7,030); bedroom count not supplied"),
    ("vacancy", 0.05, "share", "ASSUMPTION", "Share of the year a rented Property A stands empty"),
    ("bldg_share", 0.20, "share", "ASSUMPTION", "Share of Property A's value that is building (depreciable) rather than land. The assessor's land/improvement split on the bill replaces this"),
    ("dep_years", 27.5, "years", "IRS-P527", "Depreciation period for a rented house"),
    ("maint_a_pct", 0.005, "share", "CFPB-WORKSHEET", "Property A upkeep: half the CFPB 1% rule, because the owner reports it costs less than Property B. ASSUMPTION"),
    ("maint_b_pct", 0.01, "share", "CFPB-WORKSHEET", "Property B upkeep: CFPB rule of thumb, 1% of value a year"),
    ("s121_mfj", 500000, "usd", "IRS-TC701", "Home-sale gain exclusion, joint return (held fixed in dollars)"),
    ("s121_single", 250000, "usd", "IRS-TC701", "Home-sale gain exclusion, single (held fixed in dollars)"),
    ("wages_real", 150000, "usd", "ASSUMPTION", "Household's other taxable income in 2026 dollars. Not supplied; three levels are tested"),
]
P = {k: v for k, v, *_ in PARAMS}
SELL = P["sell_comm"] + P["transfer_tax"]
CBO_T10 = {2027: .042, 2028: .043, 2029: .043, 2030: .043, 2031: .043}
CBO_TB = {2027: .033, 2028: .033, 2029: .033, 2030: .032, 2031: .032, 2032: .032}

# Owner-supplied running costs (2026 dollars a year), from the $10-rounded inputs
COST = dict(
    ins_a=A["insurance_per_year_owner_estimate"], water_a=r10(mid(A["water_per_month"]) * 12),
    elec_a=r10(mid(A["electricity_per_month"]) * 12), maint_a=r10(P["maint_a_pct"] * A["market_value_2026"]),
    ins_b=B["insurance_per_year_owner_estimate"], water_b=r10(mid(B["water_per_month"]) * 12),
    elec_b=r10(mid(B["electricity_per_month"]) * 12), maint_b=r10(P["maint_b_pct"] * B["market_value_2026"]),
    rent_b=B["rent_per_month_two_units"] * 12, unit3=r10(B["rent_per_month_two_units"] / 2.0) * 12,
    rent_a=P["rent_a_month"] * 12,
)
# Fixed (non-ad-valorem) charges on each bill, backed out of the owner's latest bill
FIX_A_2025 = r10(A["tax"]["2025"] - P["rate_a"] * (A["assessed"]["2025"] - P["hox"]))
FIX_B_2025 = r10(B["tax"]["2025"] - P["rate_b"] * B["assessed"]["2025"])

# --------------------------------------------------------------------------------------------
# Income tax.  Federal: Rev. Proc. 2026-35 (2027 amounts).  California: FTB 2025 schedules.
# --------------------------------------------------------------------------------------------
FED = {
    "mfj": dict(br=[(25600, .10), (104050, .12), (218250, .22), (416650, .24), (529100, .32), (793650, .35), (None, .37)],
                sd=33200, cg0=102100, cg15=633600, niit=250000),
    "single": dict(br=[(12800, .10), (52025, .12), (109125, .22), (208325, .24), (264550, .32), (661375, .35), (None, .37)],
                   sd=16600, cg0=51050, cg15=563200, niit=200000),
}
CAL = {
    "mfj": dict(br=[(22158, .01), (52528, .02), (82904, .04), (115084, .06), (145448, .08), (742958, .093),
                    (891542, .103), (1485906, .113), (None, .123)], sd=11412),
    "single": dict(br=[(11079, .01), (26264, .02), (41452, .04), (57542, .06), (72724, .08), (371479, .093),
                       (445771, .103), (742953, .113), (None, .123)], sd=5706),
}


def bracket_tax(x, br, f):
    tax, lo = 0.0, 0.0
    for hi, rate in br:
        if hi is None or x <= hi * f:
            return tax + (x - lo) * rate
        tax += (hi * f - lo) * rate
        lo = hi * f
    return tax


def total_tax(status, ff, fc, wages=0.0, ord_nii=0.0, treas=0.0, pref=0.0, recapture=0.0):
    """Federal income tax + net investment income tax + California income tax.
    wages     ordinary income that is not investment income
    ord_nii   ordinary investment income taxed by both (net rent, savings interest)
    treas     Treasury interest (federal only; exempt in California)
    pref      qualified dividends and long-term gains (federal 0/15/20%; California ordinary rates)
    recapture depreciation recapture on sale (federal ordinary rate capped at 25%)
    ff, fc    inflation index of the federal (2027) and California (2025) bracket amounts"""
    F, C = FED[status], CAL[status]
    ord_fed = wages + ord_nii + treas
    sd = F["sd"] * ff
    ti_ord = max(0.0, ord_fed - sd)
    sd_left = max(0.0, sd - ord_fed)
    rec = max(0.0, recapture - sd_left)
    sd_left = max(0.0, sd_left - recapture)
    prf = max(0.0, pref - sd_left)
    t_ord = bracket_tax(ti_ord, F["br"], ff)
    t_rec = min(bracket_tax(ti_ord + rec, F["br"], ff) - t_ord, 0.25 * rec)
    base = ti_ord + rec
    z0, z15 = F["cg0"] * ff, F["cg15"] * ff
    at0 = max(0.0, min(prf, z0 - base))
    at15 = max(0.0, min(prf - at0, z15 - max(base, z0)))
    t_pref = 0.15 * at15 + 0.20 * (prf - at0 - at15)
    nii = max(0.0, ord_nii + treas + pref + recapture)
    t_niit = 0.038 * max(0.0, min(nii, ord_fed + pref + recapture - F["niit"]))      # threshold is not indexed
    ti_ca = max(0.0, wages + ord_nii + pref + recapture - C["sd"] * fc)
    t_ca = bracket_tax(ti_ca, C["br"], fc) + 0.01 * max(0.0, ti_ca - 1_000_000)
    return t_ord + t_rec + t_pref + t_niit + t_ca


# --------------------------------------------------------------------------------------------
# Economic paths.  A path gives, for each year 2027..2076, the change during that year.
# --------------------------------------------------------------------------------------------
KEYS = ("infl", "ha", "hb", "hca", "eq", "dy", "t10", "tb", "rg")


def baseline_path(**over):
    p = {k: {} for k in KEYS}
    for y in range(Y0 + 1, Y1 + 1):
        p["infl"][y] = over.get("infl", P["infl"])
        p["ha"][y] = over.get("hpi_a", P["hpi_a"])
        p["hb"][y] = over.get("hpi_b", P["hpi_b"])
        p["hca"][y] = over.get("hpi_ca", P["hpi_ca"])
        p["eq"][y] = over.get("eq", P["eq"])
        p["dy"][y] = P["div"]
        p["t10"][y] = over.get("t10", CBO_T10.get(y, P["t10_long"]))
        p["tb"][y] = over.get("tb", CBO_TB.get(y, P["tb_long"]))
        p["rg"][y] = over.get("rent_mkt", over.get("hpi_a", P["rent_mkt"]) if "hpi_a" in over and "rent_mkt" not in over else P["rent_mkt"])
    return p


def load_history():
    fr = {int(r["year"]): r for r in read_csv("fred_annual.csv")}
    sp = {int(r["year"]): r for r in read_csv("erp_sp500.csv")}
    h = {}
    for y in range(1977, 2026):
        d = sp[y]["div_yield"] / 100.0
        p0, p1 = sp[y - 1]["sp500_eoy"], sp[y]["sp500_eoy"]
        h[y] = dict(
            infl=fr[y]["cpi_dec"] / fr[y - 1]["cpi_dec"] - 1,
            ha=fr[y]["hpi_sj"] / fr[y - 1]["hpi_sj"] - 1,
            hb=fr[y]["hpi_sf"] / fr[y - 1]["hpi_sf"] - 1,
            hca=fr[y]["hpi_ca"] / fr[y - 1]["hpi_ca"] - 1,
            eq=(p1 + d * (p0 + p1) / 2.0) / p0 - 1,          # price change plus dividends on the average index level
            dy=d * (p0 + p1) / 2.0 / p0,
            t10=fr[y]["gs10"] / 100.0, tb=fr[y]["tb3m"] / 100.0,
            rg=fr[y]["rent_sf"] / fr[y - 1]["rent_sf"] - 1,
        )
    return h


HIST = load_history()
HYEARS = sorted(HIST)


def path_from_years(years, pre=None, start=Y0 + 1):
    """Model year start+i takes the history of years[i]; earlier model years follow `pre` (baseline)."""
    p = pre if pre is not None else baseline_path()
    p = {k: dict(v) for k, v in p.items()}
    for i, hy in enumerate(years):
        y = start + i
        if y > Y1:
            break
        for k in KEYS:
            p[k][y] = HIST[hy][k]
    return p


def cyclic_years(first, n):
    i = HYEARS.index(first)
    return [HYEARS[(i + j) % len(HYEARS)] for j in range(n)]


def bootstrap_years(rng, n, mean_block=6):
    out = []
    while len(out) < n:
        i = rng.randrange(len(HYEARS))
        ln = 1
        while rng.random() > 1.0 / mean_block:
            ln += 1
        out += [HYEARS[(i + j) % len(HYEARS)] for j in range(ln)]
    return out[:n]


# --------------------------------------------------------------------------------------------
# Levels implied by a path (values, assessed values, taxes and running costs for every year)
# --------------------------------------------------------------------------------------------
def levels(path):
    L = {k: {} for k in ("I", "VA", "VB", "p13", "AVAp", "AVB", "X19", "EX", "fixA", "fixB", "rentB", "mktA", "mktU3", "ctrl")}
    I25 = 1.0 / (1.0 + P["infl_2026"])
    L["I"][Y0] = 1.0
    L["VA"][Y0], L["VB"][Y0] = float(A["market_value_2026"]), float(B["market_value_2026"])
    L["AVAp"][Y0] = float(A["assessed"]["2026"])
    L["AVB"][Y0] = B["assessed"]["2025"] * 1.02                       # 2026 roll factor 1.02 (BOE-LTA-2026-002)
    L["X19"][Y0] = float(P["x19_2026"])
    ex = float(P["excl_2026"]); L["EX"][Y0] = ex
    L["rentB"][Y0] = float(COST["rent_b"]); L["mktA"][Y0] = float(COST["rent_a"]); L["mktU3"][Y0] = float(COST["unit3"])
    for y in range(Y0 + 1, Y1 + 1):
        prev_infl = P["infl_2026"] if y == Y0 + 1 else path["infl"][y - 1]
        prev_hca = P["hpi_ca"] if y == Y0 + 1 else path["hca"][y - 1]
        L["I"][y] = L["I"][y - 1] * (1 + path["infl"][y])
        L["VA"][y] = L["VA"][y - 1] * (1 + path["ha"][y])
        L["VB"][y] = L["VB"][y - 1] * (1 + path["hb"][y])
        L["p13"][y] = min(1 + P["p13_cap"], 1 + prev_infl)             # last year's inflation, capped at 2%
        L["AVAp"][y] = L["AVAp"][y - 1] * L["p13"][y]
        L["AVB"][y] = L["AVB"][y - 1] * L["p13"][y]
        # Prop 19 allowance: every odd year, by the prior calendar year's California index change
        L["X19"][y] = L["X19"][y - 1] * (1 + prev_hca) if y % 2 == 1 else L["X19"][y - 1]
        if y == 2027:
            ex = float(P["excl_2027"])
        else:
            ex = ex * (1 + prev_infl - P["excl_gap"])
        L["EX"][y] = math.floor(ex / 10000.0) * 10000.0                # statute rounds down to $10,000
        L["ctrl"][y] = min(0.07, P["sf_rent_share"] * max(0.0, prev_infl))
        L["rentB"][y] = L["rentB"][y - 1] * (1 + L["ctrl"][y])
        L["mktA"][y] = L["mktA"][y - 1] * (1 + path["rg"][y])
        L["mktU3"][y] = L["mktU3"][y - 1] * (1 + path["rg"][y])
    for y in range(Y0, Y1 + 1):
        L["fixA"][y] = FIX_A_2025 * L["I"][y] / I25
        L["fixB"][y] = FIX_B_2025 * L["I"][y] / I25
    L["ff"] = {y: L["I"][y] / L["I"][2027] for y in L["I"]}
    L["fc"] = {y: L["I"][y] / I25 for y in L["I"]}
    return L


def cost(L, name, y):
    return COST[name] * L["I"][y]


def b_net(L, y):
    """Property B: rent less tax, insurance, water, electricity and upkeep (same in every plan)."""
    tax = P["rate_b"] * L["AVB"][y] + L["fixB"][y]
    out = tax + cost(L, "ins_b", y) + cost(L, "water_b", y) + cost(L, "elec_b", y) + cost(L, "maint_b", y)
    return L["rentB"][y] - out, tax


def prop19_value(fbyv, market, allowance):
    """New taxable value when a child moves in (BOE-LTA-2026-026): base value plus any excess over base + allowance."""
    return fbyv + max(0.0, market - (fbyv + allowance))


# --------------------------------------------------------------------------------------------
# Investment account (stocks / Treasuries / savings)
# --------------------------------------------------------------------------------------------
MIX = {"stocks": (1.0, 0.0, 0.0), "mix6040": (0.6, 0.4, 0.0), "treasuries": (0.0, 1.0, 0.0), "savings": (0.0, 0.0, 1.0)}


class Acct:
    def __init__(self, vehicle):
        self.mix = MIX[vehicle]; self.eq = self.basis = self.tr = self.cash = 0.0

    def flow(self, amt):
        self.eq += amt * self.mix[0]; self.basis += amt * self.mix[0]
        self.tr += amt * self.mix[1]; self.cash += amt * self.mix[2]

    def grow(self, path, y):
        div = self.eq * path["dy"][y]
        self.eq *= 1 + path["eq"][y]; self.basis += div
        ti = self.tr * path["t10"][y]; self.tr += ti
        ci = self.cash * path["tb"][y]; self.cash += ci
        return div, ti, ci

    @property
    def total(self):
        return self.eq + self.tr + self.cash

    @property
    def gain(self):
        return max(0.0, self.eq - self.basis)


# --------------------------------------------------------------------------------------------
# The three plans for Property A after inheritance in year T, compared H years later.
# Result: after-tax wealth produced by Property A if everything is turned into cash at T+H.
# --------------------------------------------------------------------------------------------
def simulate(path, T, H, vehicle="stocks", status="mfj", wages=None, L=None, detail=False, rent_unit3=True):
    L = L or levels(path)
    wages = P["wages_real"] if wages is None else wages
    end = T + H
    VT = L["VA"][T]
    s121 = P["s121_mfj"] if status == "mfj" else P["s121_single"]
    rows = {"sell": [], "rent": [], "live": []}

    def base_tax(y):
        bn, _ = b_net(L, y)
        w = wages * L["I"][y]
        return w, max(0.0, bn), total_tax(status, L["ff"][y], L["fc"][y], wages=w, ord_nii=max(0.0, bn))

    # ---- Sell at T (half a year of carrying cost at the reassessed value), invest the proceeds
    carry = 0.5 * (P["rate_a"] * VT + L["fixA"][T] + cost(L, "ins_a", T) + cost(L, "maint_a", T) + cost(L, "water_a", T))
    acc = Acct(vehicle); acc.flow(VT * (1 - SELL) - carry)
    for y in range(T + 1, end + 1):
        w, bn, t0 = base_tax(y)
        div, ti, ci = acc.grow(path, y)
        t1 = total_tax(status, L["ff"][y], L["fc"][y], wages=w, ord_nii=bn + ci, treas=ti, pref=div)
        if y == end:
            t2 = total_tax(status, L["ff"][y], L["fc"][y], wages=w, ord_nii=bn + ci, treas=ti, pref=div + acc.gain)
            w_sell = acc.total - (t1 - t0) - (t2 - t1)
        else:
            acc.flow(-(t1 - t0))
        if detail:
            rows["sell"].append(dict(year=y, income=div + ti + ci, tax=t1 - t0, account=acc.total))

    # ---- Rent it out: full reassessment at T, rent taxed as ordinary income, depreciation on the building share
    acc = Acct(vehicle); av = VT; dep_basis = P["bldg_share"] * VT; dep_acc = 0.0; susp = 0.0
    for y in range(T + 1, end + 1):
        av = av * L["p13"][y] if y > T + 1 else av
        ptax = P["rate_a"] * av + L["fixA"][y]
        rent = L["mktA"][y] * (1 - P["vacancy"])
        exp = ptax + cost(L, "ins_a", y) + cost(L, "maint_a", y)
        dep = min(dep_basis / P["dep_years"], dep_basis - dep_acc); dep_acc += dep
        nt = rent - exp - dep
        if nt < 0:
            susp += -nt; nt = 0.0
        else:
            use = min(susp, nt); nt -= use; susp -= use
        w, bn, t0 = base_tax(y)
        div, ti, ci = acc.grow(path, y)
        t1 = total_tax(status, L["ff"][y], L["fc"][y], wages=w, ord_nii=bn + nt + ci, treas=ti, pref=div)
        cash = rent - exp - (t1 - t0)
        if y == end:
            realized = L["VA"][end] * (1 - SELL)
            gain = max(0.0, realized - (VT - dep_acc) - susp)
            rec = min(dep_acc, gain)
            t2 = total_tax(status, L["ff"][y], L["fc"][y], wages=w, ord_nii=bn + nt + ci, treas=ti,
                           pref=div + (gain - rec) + acc.gain, recapture=rec)
            w_rent = realized + acc.total + cash - (t2 - t1)
        else:
            acc.flow(cash)
        if detail:
            rows["rent"].append(dict(year=y, value=L["VA"][y], assessed=av, ptax=ptax, ins=cost(L, "ins_a", y),
                                     maint=cost(L, "maint_a", y), rent=rent, tax=t1 - t0, cash=cash, account=acc.total))

    # ---- Live in it: Prop 19 partial exclusion; the unit in Property B the owners leave can be rented
    acc = Acct(vehicle); fbyv = L["AVAp"][T]; av = prop19_value(fbyv, VT, L["X19"][T]); av_T = av
    u3 = L["mktU3"][T] if rent_unit3 else 0.0
    for y in range(T + 1, end + 1):
        if y > T + 1:
            av *= L["p13"][y]; u3 *= 1 + L["ctrl"][y]
        ptax = P["rate_a"] * (av - P["hox"]) + L["fixA"][y]
        costs = ptax + cost(L, "ins_a", y) + cost(L, "maint_a", y) + cost(L, "water_a", y) + cost(L, "elec_a", y)
        w, bn, t0 = base_tax(y)
        div, ti, ci = acc.grow(path, y)
        t1 = total_tax(status, L["ff"][y], L["fc"][y], wages=w, ord_nii=bn + u3 + ci, treas=ti, pref=div)
        cash = u3 - costs - (t1 - t0)
        if y == end:
            realized = L["VA"][end] * (1 - SELL)
            gain = max(0.0, realized - VT - (s121 if H >= 2 else 0.0))
            t2 = total_tax(status, L["ff"][y], L["fc"][y], wages=w, ord_nii=bn + u3 + ci, treas=ti, pref=div + gain + acc.gain)
            w_live = realized + acc.total + cash - (t2 - t1)
        else:
            acc.flow(cash)
        if detail:
            rows["live"].append(dict(year=y, value=L["VA"][y], assessed=av, ptax=ptax, ins=cost(L, "ins_a", y),
                                     maint=cost(L, "maint_a", y), water=cost(L, "water_a", y), elec=cost(L, "elec_a", y),
                                     unit3=u3, tax=t1 - t0, cash=cash, account=acc.total))

    out = dict(sell=w_sell, rent=w_rent, live=w_live, deflator=L["I"][end], value_T=VT, assessed_live_T=av_T,
               assessed_rent_T=VT, fbyv_T=fbyv, x19_T=L["X19"][T])
    if detail:
        out["rows"] = rows
    return out


def best_of(res):
    return max(("sell", "rent", "live"), key=lambda k: res[k])


def bisect(f, lo, hi, n=60):
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        return None
    for _ in range(n):
        m = (lo + hi) / 2.0
        fm = f(m)
        if flo * fm <= 0:
            hi, fhi = m, fm
        else:
            lo, flo = m, fm
    return (lo + hi) / 2.0


# --------------------------------------------------------------------------------------------
# Build every published result
# --------------------------------------------------------------------------------------------
def main():
    R = {"generated_by": "s-179ec133", "inputs_as_of": INP["as_of"], "rounding": "all dollar results rounded to the nearest $10"}
    R["params"] = [dict(key=k, value=v, unit=u, src=s, note=n) for k, v, u, s, n in PARAMS]
    R["cost_2026"] = dict(COST, fix_a_2025=FIX_A_2025, fix_b_2025=FIX_B_2025)
    base = baseline_path(); L = levels(base)
    T0, H0 = 2045, 20

    # ---- 1. history check: owner's assessed values against the official inflation factors
    fac = {int(r["roll_year"]): r["factor"] for r in read_csv("boe_inflation_factors.csv")}
    chk = []
    for tag, prop in (("A", A), ("B", B)):
        ys = sorted(int(y) for y in prop["assessed"])
        for y in ys:
            row = dict(prop=tag, year=y, assessed=prop["assessed"][str(y)], tax=prop["tax"].get(str(y)))
            if y - 1 in ys:
                a0, a1 = prop["assessed"][str(y - 1)], prop["assessed"][str(y)]
                row["growth"] = round(a1 / a0 - 1, 5)
                row["official_factor"] = fac[y]
                row["match"] = abs(a1 - a0 * fac[y]) <= 5 + 5 * fac[y] + 0.01     # both ends rounded to $10
            if row["tax"]:
                row["tax_per_100"] = round(100.0 * row["tax"] / row["assessed"], 3)
            chk.append(row)
    R["history"] = chk
    irr = []
    for tag, prop in (("A", A), ("B", B)):
        ys = sorted(int(y) for y in prop["tax"])
        for y in ys:
            if y - 1 in ys:
                t0, t1 = prop["tax"][str(y - 1)], prop["tax"][str(y)]
                ch = t1 / t0 - 1
                if t1 == t0:
                    irr.append(dict(prop=tag, year=y, kind="same", text="tax bill identical to %d although the assessed value rose" % (y - 1)))
                elif ch > 0.10 or ch < -0.03:
                    irr.append(dict(prop=tag, year=y, kind="jump", text="tax bill changed %+.1f%% while the assessed value changed about +2%%" % (100 * ch)))
    for row in chk:
        if row.get("match") is False:
            irr.append(dict(prop=row["prop"], year=row["year"], kind="factor",
                            text="assessed value differs by about $%d from the previous year times the official factor %.5f" % (
                                r10(abs(row["assessed"] - (A if row["prop"] == "A" else B)["assessed"][str(row["year"] - 1)] * row["official_factor"])), row["official_factor"])))
    R["history_irregular"] = irr

    # ---- 2. year-by-year projections (baseline), inheritance in T0
    d = simulate(base, T0, Y1 - T0, detail=True, L=L)
    live = {r["year"]: r for r in d["rows"]["live"]}; rent = {r["year"]: r for r in d["rows"]["rent"]}
    pa, pb = [], []
    for y in range(Y0, Y1 + 1):
        row = dict(year=y, value=r10(L["VA"][y]), ins=r10(cost(L, "ins_a", y)), water=r10(cost(L, "water_a", y)),
                   elec=r10(cost(L, "elec_a", y)), maint=r10(cost(L, "maint_a", y)))
        if y <= T0:
            av = L["AVAp"][y]
            row.update(phase="before", assessed=r10(av), ptax=r10(P["rate_a"] * (av - P["hox"]) + L["fixA"][y]))
            if y == T0:
                row.update(assessed_live=r10(d["assessed_live_T"]), assessed_rent=r10(d["assessed_rent_T"]))
        else:
            row.update(phase="after", assessed_live=r10(live[y]["assessed"]), ptax_live=r10(live[y]["ptax"]),
                       assessed_rent=r10(rent[y]["assessed"]), ptax_rent=r10(rent[y]["ptax"]),
                       rent_income=r10(rent[y]["rent"]))
        pa.append(row)
        bn, btax = b_net(L, y)
        pb.append(dict(year=y, value=r10(L["VB"][y]), assessed=r10(L["AVB"][y]), ptax=r10(btax), ins=r10(cost(L, "ins_b", y)),
                       water=r10(cost(L, "water_b", y)), elec=r10(cost(L, "elec_b", y)), maint=r10(cost(L, "maint_b", y)),
                       rent=r10(L["rentB"][y]), net=r10(bn), reassessed_tax=r10(P["rate_b"] * L["VB"][y] + L["fixB"][y])))
    R["proj_a"], R["proj_b"] = pa, pb

    # ---- 3. the decision, baseline
    def pack(res):
        o = {k: r10(res[k]) for k in ("sell", "rent", "live")}
        o.update({k + "_real": r10(res[k] / res["deflator"]) for k in ("sell", "rent", "live")})
        o["best"] = best_of(res)
        return o

    dec = dict(T=T0, H=H0, by_vehicle={}, by_year=[], by_horizon=[])
    for v in MIX:
        dec["by_vehicle"][v] = pack(simulate(base, T0, H0, vehicle=v, L=L))
    for T in range(2040, 2051):
        res = simulate(base, T, H0, L=L)
        o = pack(res)
        o.update(T=T, value_T=r10(res["value_T"]), fbyv_T=r10(res["fbyv_T"]), x19_T=r10(res["x19_T"]),
                 assessed_live_T=r10(res["assessed_live_T"]),
                 ptax_before=r10(P["rate_a"] * (res["fbyv_T"] - P["hox"]) + L["fixA"][T]),
                 ptax_live=r10(P["rate_a"] * (res["assessed_live_T"] - P["hox"]) + L["fixA"][T]),
                 ptax_rent=r10(P["rate_a"] * res["value_T"] + L["fixA"][T]),
                 net_proceeds=r10(res["value_T"] * (1 - SELL)), mix6040=pack(simulate(base, T, H0, vehicle="mix6040", L=L)),
                 treasuries=pack(simulate(base, T, H0, vehicle="treasuries", L=L)))
        dec["by_year"].append(o)
    for H in (5, 10, 20, 30):
        o = pack(simulate(base, T0, H, L=L)); o["H"] = H
        o["treasuries"] = pack(simulate(base, T0, H, vehicle="treasuries", L=L))
        dec["by_horizon"].append(o)
    no3 = simulate(base, T0, H0, L=L, rent_unit3=False)
    dec["live_unit3_empty"] = dict(live=r10(no3["live"]), live_real=r10(no3["live"] / no3["deflator"]))

    # annual cash picture in the first full year after inheritance (T0+1), stocks vehicle
    dd = simulate(base, T0, H0, detail=True, L=L)
    y1 = T0 + 1
    lv, rn, sl = dd["rows"]["live"][0], dd["rows"]["rent"][0], dd["rows"]["sell"][0]
    dec["first_year"] = dict(
        year=y1,
        live=dict(ptax=r10(lv["ptax"]), ins=r10(lv["ins"]), maint=r10(lv["maint"]), water=r10(lv["water"]), elec=r10(lv["elec"]),
                  unit3=r10(lv["unit3"]), tax=r10(lv["tax"]), cash=r10(lv["cash"])),
        rent=dict(rent=r10(rn["rent"]), ptax=r10(rn["ptax"]), ins=r10(rn["ins"]), maint=r10(rn["maint"]), tax=r10(rn["tax"]), cash=r10(rn["cash"])),
        sell=dict(proceeds=r10(dd["value_T"] * (1 - SELL)), income=r10(sl["income"]), tax=r10(sl["tax"])))
    dec["yearly"] = [dict(year=a["year"], sell_account=r10(a["account"]), rent_cash=r10(b["cash"]), rent_account=r10(b["account"]),
                          live_cash=r10(c["cash"]), live_account=r10(c["account"]), value=r10(c["value"]))
                     for a, b, c in zip(dd["rows"]["sell"], dd["rows"]["rent"], dd["rows"]["live"])]

    # break-evens
    def gap_eq(g):
        r = simulate(baseline_path(eq=g), T0, H0); return r["sell"] - max(r["rent"], r["live"])

    def gap_hp(g):
        r = simulate(baseline_path(hpi_a=g), T0, H0); return max(r["rent"], r["live"]) - r["sell"]

    def gap_hp_tr(g):
        r = simulate(baseline_path(hpi_a=g), T0, H0, vehicle="treasuries"); return max(r["rent"], r["live"]) - r["sell"]

    be_eq, be_hp, be_hp_tr = bisect(gap_eq, 0.0, 0.15), bisect(gap_hp, 0.0, 0.15), bisect(gap_hp_tr, 0.0, 0.15)
    dec["breakeven"] = dict(stock_return=None if be_eq is None else round(be_eq, 4),
                            home_growth_vs_stocks=None if be_hp is None else round(be_hp, 4),
                            home_growth_vs_treasuries=None if be_hp_tr is None else round(be_hp_tr, 4))
    # grid: home growth x stock return
    grid = []
    for hp in (0.023, 0.030, 0.047, 0.067):
        for g in (0.04, 0.05, 0.07, 0.09, 0.116):
            r = simulate(baseline_path(hpi_a=hp, eq=g), T0, H0)
            grid.append(dict(hpi=hp, eq=g, **pack(r)))
    dec["grid"] = grid
    # sensitivities (one change at a time)
    sens = []

    def add(label, src, **kw):
        global SELL, FIX_A_2025
        over = {k: v for k, v in kw.items() if k in ("infl", "hpi_a", "eq", "rent_mkt", "t10", "tb")}
        saved_p, saved_c, saved = dict(P), dict(COST), (SELL, FIX_A_2025)
        for k, v in kw.items():
            if k in P:
                P[k] = v
            if k in COST:
                COST[k] = v
        SELL = P["sell_comm"] + P["transfer_tax"]
        FIX_A_2025 = r10(A["tax"]["2025"] - P["rate_a"] * (A["assessed"]["2025"] - P["hox"]))   # keeps today's bill unchanged
        r = simulate(baseline_path(**over), T0, H0, status=kw.get("status", "mfj"), wages=kw.get("wages"))
        P.clear(); P.update(saved_p); COST.clear(); COST.update(saved_c); SELL, FIX_A_2025 = saved
        sens.append(dict(label=label, src=src, **pack(r)))

    add("Baseline", "—")
    add("Other household income $60,000 (2026 dollars)", "ASSUMPTION", wages=60000)
    add("Other household income $400,000 (2026 dollars)", "ASSUMPTION", wages=400000)
    add("Single filer instead of joint return", "IRS-RP-2026-35", status="single")
    add("Property A rent at the HUD metro figure ($4,690 a month)", "HUD-FMR-FY2027", rent_a=4690 * 12)
    add("Property A rent at HUD's 150% ceiling ($7,030 a month)", "HUD-SAFMR-METHOD", rent_a=7030 * 12)
    add("Upkeep on Property A at the full CFPB 1% rule", "CFPB-WORKSHEET", maint_a=r10(0.01 * A["market_value_2026"]))
    add("Insurance on Property A three times the owner's estimate", "ASSUMPTION", ins_a=4500)
    add("Selling costs 3% instead of 5%", "ASSUMPTION", sell_comm=0.03)
    add("Selling costs 7% instead of 5%", "ASSUMPTION", sell_comm=0.07)
    add("Property tax rate at the top of the county range (1.241%)", "SCC-TAXRATEBOOK-2025", rate_a=0.01241)
    add("Building is 40% of Property A's value (more depreciation)", "ASSUMPTION", bldg_share=0.40)
    add("Everything 1.7 points hotter: inflation 4%, home growth 4.7%, rents 4.7%, stocks 8.7%, Treasuries 6.1%", "ASSUMPTION",
        infl=0.04, hpi_a=0.047, rent_mkt=0.047, eq=0.087, t10=0.061, tb=0.048)
    add("Stocks return only 4% a year", "ASSUMPTION", eq=0.04)
    add("Home price growth 4.7% a year (San Jose metro, 2015-2025 record)", "FRED-SERIES", hpi_a=0.047)
    add("Home price growth equal to inflation only (2.3%)", "CBO-OUTLOOK-2026", hpi_a=0.023)
    dec["sensitivity"] = sens
    R["decision"] = dec

    # ---- 4. estate threshold
    est = []
    for T in list(range(2026, 2031)) + list(range(2040, 2051)):
        est.append(dict(year=T, exclusion=int(L["EX"][T]), house=r10(L["VA"][T]),
                        room=r10(L["EX"][T] - L["VA"][T]), room_two=r10(2 * L["EX"][T] - L["VA"][T]),
                        half_law=int(math.floor(L["EX"][T] / 2 / 10000.0) * 10000), room_half=r10(L["EX"][T] / 2 - L["VA"][T])))
    R["estate"] = est
    R["estate_examples"] = [dict(over=o, tax=int(P["estate_rate"] * o)) for o in (500000, 1000000, 2500000, 5000000)]

    # ---- 5. history summary
    def cagr(k, a, b):
        return math.prod(1 + HIST[y][k] for y in range(a, b + 1)) ** (1.0 / (b - a + 1)) - 1

    hs = []
    for k, name, src in (("infl", "Consumer prices (CPI-U, December to December)", "FRED-SERIES"),
                         ("ha", "House prices, San Jose metro (FHFA)", "FRED-SERIES"),
                         ("hb", "House prices, San Francisco metro division (FHFA)", "FRED-SERIES"),
                         ("hca", "House prices, California (FHFA)", "FRED-SERIES"),
                         ("rg", "Rents, San Francisco area (BLS)", "FRED-SERIES"),
                         ("eq", "Stocks, S&P 500 with dividends (computed from ERP tables)", "ERP-B56")):
        vals = [(HIST[y][k], y) for y in HYEARS]
        hs.append(dict(key=k, name=name, src=src, full=round(cagr(k, 1977, 2025), 4), last20=round(cagr(k, 2006, 2025), 4),
                       last10=round(cagr(k, 2016, 2025), 4), worst=round(min(vals)[0], 4), worst_year=min(vals)[1],
                       best=round(max(vals)[0], 4), best_year=max(vals)[1],
                       down_years=sum(1 for v, _ in vals if v < 0)))
    for k, name in (("t10", "10-year Treasury yield (annual average)"), ("tb", "3-month Treasury bill yield (annual average)")):
        vals = [(HIST[y][k], y) for y in HYEARS]
        hs.append(dict(key=k, name=name, src="FRED-SERIES", full=round(sum(v for v, _ in vals) / len(vals), 4),
                       last20=round(sum(HIST[y][k] for y in range(2006, 2026)) / 20, 4),
                       last10=round(sum(HIST[y][k] for y in range(2016, 2026)) / 10, 4),
                       worst=round(min(vals)[0], 4), worst_year=min(vals)[1], best=round(max(vals)[0], 4), best_year=max(vals)[1], down_years=0))
    R["history_stats"] = hs
    R["history_years"] = [dict(year=y, **{k: round(HIST[y][k], 4) for k in KEYS}) for y in HYEARS]

    # ---- 6. black swan: real history replayed
    def realpack(res):
        return {k: r10(res[k] / res["deflator"]) for k in ("sell", "rent", "live")}

    vehicles = ("stocks", "mix6040", "treasuries")
    episodes = []
    for first, title, why in (
            (1977, "Inflation shock first", "1977-1996: double-digit inflation, 14% Treasury bills, then the 1990s California housing slump"),
            (1990, "California housing slump first", "1990-2009: house prices fall for five years, then the dot-com boom and bust, then the 2008 crash"),
            (2000, "Stock market crash first", "2000-2019: stocks lose three years running, housing boom, 2008 crash, long recovery"),
            (2006, "Housing crash first", "2006-2025: house prices fall 26% in five years, stocks fall 37% in 2008, then 2022 inflation")):
        p = path_from_years(list(range(first, first + H0)), start=T0 + 1)
        row = dict(first=first, last=first + H0 - 1, title=title, why=why)
        for v in vehicles:
            res = simulate(p, T0, H0, vehicle=v)
            row[v] = realpack(res); row[v]["best"] = best_of(res)
        row["house_change"] = round(math.prod(1 + HIST[y]["ha"] for y in range(first, first + H0)) - 1, 3)
        row["stock_change"] = round(math.prod(1 + HIST[y]["eq"] for y in range(first, first + H0)) - 1, 3)
        row["price_change"] = round(math.prod(1 + HIST[y]["infl"] for y in range(first, first + H0)) - 1, 3)
        episodes.append(row)
    R["episodes"] = episodes

    # every possible 50-year replay (history wrapped around), inheritance in T0
    replay = []
    for first in HYEARS:
        p = path_from_years(cyclic_years(first, Y1 - Y0))
        Lp = levels(p)
        row = dict(first=first, at_inheritance=cyclic_years(first, Y1 - Y0)[T0 - Y0 - 1], value_T=r10(Lp["VA"][T0] / Lp["I"][T0]))
        for v in vehicles:
            res = simulate(p, T0, H0, vehicle=v, L=Lp)
            row[v] = realpack(res); row[v]["best"] = best_of(res)
        replay.append(row)
    R["replay"] = replay

    def summarize(rowsets, n):
        out = {}
        for v in vehicles:
            wins = {k: 0 for k in ("sell", "rent", "live")}
            vals = {k: [] for k in ("sell", "rent", "live")}
            beats_both = 0
            for r in rowsets:
                wins[r[v]["best"]] += 1
                for k in vals:
                    vals[k].append(r[v][k])
            pct = lambda xs, q: r10(sorted(xs)[min(len(xs) - 1, int(q * len(xs)))])
            out[v] = dict(wins={k: round(100.0 * wins[k] / n, 1) for k in wins},
                          pct={k: dict(p5=pct(vals[k], .05), p25=pct(vals[k], .25), p50=pct(vals[k], .50), p75=pct(vals[k], .75), p95=pct(vals[k], .95),
                                       worst=r10(min(vals[k])), best=r10(max(vals[k]))) for k in vals})
        return out

    R["replay_summary"] = summarize(replay, len(replay))

    # seeded block bootstrap
    rng = random.Random(179)
    N = 2000
    boot = []
    for _ in range(N):
        p = path_from_years(bootstrap_years(rng, Y1 - Y0))
        Lp = levels(p)
        row = {}
        for v in vehicles:
            res = simulate(p, T0, H0, vehicle=v, L=Lp)
            row[v] = realpack(res); row[v]["best"] = best_of(res)
        boot.append(row)
    R["bootstrap"] = dict(n=N, seed=179, mean_block_years=6, summary=summarize(boot, N))

    json.dump(R, open(os.path.join(DATA, "results.json"), "w"), indent=1)
    return R


if __name__ == "__main__":
    R = main()
    d = R["decision"]
    print("baseline T=%d H=%d (stocks): " % (d["T"], d["H"]), d["by_vehicle"]["stocks"])
    print("treasuries:", d["by_vehicle"]["treasuries"])
    print("breakeven:", d["breakeven"])
    print("first year:", json.dumps(d["first_year"]))
    print("replay wins:", {v: R["replay_summary"][v]["wins"] for v in R["replay_summary"]})
    print("bootstrap wins:", {v: R["bootstrap"]["summary"][v]["wins"] for v in R["bootstrap"]["summary"]})
