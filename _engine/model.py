"""Projection, tax and decision model.  Standard library only.  Deterministic."""
import json, math, os
from inputs import (A, B, OFFICIAL as O, ASSUME, FIXED as F, BASE_YEAR, LAST_YEAR, PROJ_LAST,
                    INHERIT_YEARS, CENTRAL_T, HORIZONS, CENTRAL_H)

HERE = os.path.dirname(os.path.abspath(__file__))
SERIES = json.load(open(os.path.join(HERE, "..", "_research", "series.json")))


def r10(x):
    """Round half-up to the nearest $10."""
    return int(math.floor(x / 10.0 + 0.5)) * 10


def mid(pair):
    return (pair[0] + pair[1]) / 2.0


# ------------------------------------------------------------------ scenarios
class Scn:
    """Constant-rate scenario for the years before inheritance, plus per-year paths after it."""

    def __init__(self, home="base", invest="base", infl="base", name=None):
        self.name = name or f"home {home} / investments {invest}"
        self.infl = ASSUME["infl"][infl]
        self.gA = ASSUME["home_A"][home]
        self.gB = ASSUME["home_B"][home]
        self.stock = ASSUME["stock"][invest]
        self.cash = ASSUME["cash"][invest]
        self.post = None          # optional dict of per-year lists (history replay)

    # per-year rates after inheritance, k = 1..H
    def home(self, k):
        return self.post["home"][k - 1] if self.post else self.gA

    def cpi(self, k):
        return self.post["cpi"][k - 1] if self.post else self.infl

    def rentg(self, k):
        return self.post["rent"][k - 1] if self.post else self.infl + F["spread_rent"]

    def stockr(self, k):
        return self.post["stock"][k - 1] if self.post else self.stock

    def cashr(self, k):
        return self.post["cash"][k - 1] if self.post else self.cash


def cum(fn, k):
    """Product of (1+rate_j) for j = 1..k."""
    p = 1.0
    for j in range(1, k + 1):
        p *= 1.0 + fn(j)
    return p


# ------------------------------------------------------------------ income tax
def _bracket_tax(amount, brackets, f, start=0.0, cap=None):
    """Tax on income lying between `start` and `start+amount` under indexed brackets."""
    if amount <= 0:
        return 0.0
    tax, lo, hi = 0.0, start, start + amount
    for i, (thr, rate) in enumerate(brackets):
        b_lo = thr * f
        b_hi = brackets[i + 1][0] * f if i + 1 < len(brackets) else float("inf")
        seg = min(hi, b_hi) - max(lo, b_lo)
        if seg > 0:
            tax += seg * (min(rate, cap) if cap is not None else rate)
    return tax


def tax_total(year, infl, ordinary=0.0, ltcg=0.0, recap=0.0, invest_income=0.0):
    """Federal + California income tax (joint return) on taxable income; returns dollars."""
    ff = (1 + infl - F["chained_gap"]) ** (year - 2027)      # federal thresholds index from 2027
    cf = (1 + infl) ** (year - 2025)                          # California thresholds index from 2025
    fed = _bracket_tax(ordinary, O["fed_joint_2027"], ff)
    fed += _bracket_tax(recap, O["fed_joint_2027"], ff, start=ordinary, cap=O["recapture_cap"])
    z0, z15 = (t * ff for t in O["fed_ltcg_joint_2027"])
    lo, hi = ordinary + recap, ordinary + recap + ltcg
    fed += 0.15 * max(0.0, min(hi, z15) - max(lo, z0)) + 0.20 * max(0.0, hi - max(lo, z15))
    total = ordinary + recap + ltcg
    niit = O["niit_rate"] * min(max(invest_income, 0.0), max(0.0, total - O["niit_joint"]))
    ca = _bracket_tax(total, O["ca_joint_2025"], cf)
    return fed + niit + ca


def inc_tax(year, infl, ordinary=0.0, ltcg=0.0, recap=0.0):
    """Extra tax caused by investment-type income stacked on the household's other income."""
    base = F["other_income_2026"] * (1 + infl) ** (year - BASE_YEAR)
    with_ = tax_total(year, infl, base + max(ordinary, 0.0), max(ltcg, 0.0), max(recap, 0.0),
                      invest_income=max(ordinary, 0.0) + max(ltcg, 0.0) + max(recap, 0.0))
    return with_ - tax_total(year, infl, base)


# ------------------------------------------------------------------ portfolio
class Portfolio:
    """60% stock index fund / 40% Treasuries.  Dividends and interest taxed yearly; stock gains at sale."""

    def __init__(self, amount=0.0):
        self.stock = self.basis = self.cashv = 0.0
        self.tax_paid = 0.0
        self.add(amount)

    def add(self, amount):
        if amount >= 0:
            self.stock += amount * F["stock_share"]
            self.basis += amount * F["stock_share"]
            self.cashv += amount * (1 - F["stock_share"])
        else:                                   # a shortfall is drawn from the same mix
            tot = self.stock + self.cashv
            if tot <= 0:
                self.cashv += amount            # goes negative: money the household must find elsewhere
                return
            share = min(1.0, -amount / tot)
            self.basis *= (1 - share)
            self.stock *= (1 - share)
            self.cashv *= (1 - share)
            rest = -amount - share * tot
            if rest > 0:
                self.cashv -= rest

    def grow(self, year, infl, r_stock, r_cash):
        div = max(self.stock, 0.0) * F["dividend_yield"]
        interest = max(self.cashv, 0.0) * r_cash
        t_int = inc_tax(year, infl, ordinary=interest)
        t_div = inc_tax(year, infl, ordinary=interest, ltcg=div) - t_int
        self.stock = self.stock * (1 + r_stock) - t_div
        self.basis += div - t_div
        self.cashv = self.cashv * (1 + r_cash) - t_int if self.cashv >= 0 else self.cashv * (1 + r_cash)
        self.tax_paid += t_int + t_div

    @property
    def value(self):
        return self.stock + self.cashv

    @property
    def gain(self):
        return max(0.0, self.stock - self.basis)


# ------------------------------------------------------------------ property A at inheritance
def prop19_adjustments(T):
    """Number of biennial adjustments of the $1 million amount between now and the transfer."""
    return len([y for y in range(2027, T + 1, 2)])


def a_state(T, scn):
    """Property A on 1 January of the inheritance year T (baseline growth before T)."""
    n = T - BASE_YEAR
    fmv = A["value_2026"] * (1 + scn.gA) ** n
    fbyv = A["assessed"][2026] * (1 + O["prop13_cap"]) ** n
    allow = O["prop19_allowance"] * (1 + scn.gA) ** prop19_adjustments(T)
    limit = fbyv + allow
    av_live = fbyv if fmv <= limit else fbyv + (fmv - limit)
    fixed_2025 = A["tax"][2025] - A["assessed"][2025] * O["rate_A"]
    return {
        "T": T, "fmv": fmv, "fbyv": fbyv, "allow": allow, "limit": limit,
        "av_live": av_live, "av_full": fmv,
        "fixed": fixed_2025 * (1 + scn.infl) ** (T - 2025),
        "ins": A["insurance_year"] * (1 + scn.infl + F["spread_insurance"]) ** n,
        "water": mid(A["water_month"]) * 12 * (1 + scn.infl + F["spread_water"]) ** n,
        "maint": F["maint_A_2026"] * (1 + scn.infl) ** n,
        "rent": O["hud_rent_A_4br_2026"] * 12 * (1 + scn.infl + F["spread_rent"]) ** n,
        "b_unit_rent": F["b_unit_rent_month_2026"] * 12 * (1 + scn.infl + F["spread_rent"]) ** n,
    }


def decide(T, H, scn, ov=None):
    """After-tax wealth from Property A at the end of H years, for each option.

    `ov` holds optional sensitivity overrides: rent, ins, maint (multipliers), selling_cost,
    stock_share, other_income_2026 (absolute values), no_prop19 (bool)."""
    ov = ov or {}
    saved = {k: F[k] for k in ("selling_cost", "stock_share", "other_income_2026")}
    for k in saved:
        if k in ov:
            F[k] = ov[k]
    try:
        return _decide(T, H, scn, ov)
    finally:
        F.update(saved)


def _decide(T, H, scn, ov):
    s = a_state(T, scn)
    s["rent"] *= ov.get("rent", 1.0)
    s["ins"] *= ov.get("ins", 1.0)
    s["maint"] *= ov.get("maint", 1.0)
    if ov.get("no_prop19"):
        s["av_live"] = s["av_full"]
    out = {"state": s, "T": T, "H": H, "scn": scn.name, "options": {}}
    cap = O["prop13_cap"]

    def cpi_i(k):       # price index at start of year k (k=1 -> 1.0)
        return cum(scn.cpi, k - 1)

    def spread_i(k, sp):
        return cum(lambda j: scn.cpi(j) + sp, k - 1)

    def av_i(k):        # Prop 13 factor: lower of 2% and inflation, never negative here
        return cum(lambda j: max(0.0, min(cap, scn.cpi(j))), k - 1)

    def year(k):
        return T + k - 1

    fmv_end = s["fmv"] * cum(scn.home, H)
    deflator = (1 + scn.infl) ** (T - BASE_YEAR) * cum(scn.cpi, H)
    net_sale_end = fmv_end * (1 - F["selling_cost"])

    # ---------------- option 1: live in the home (Prop 19 family-home exclusion)
    for rent_out_b in (True, False):
        pf, rows = Portfolio(0.0), []
        for k in range(1, H + 1):
            ptax = (s["av_live"] * av_i(k) - O["homeowners_exemption"]) * O["rate_A"] + s["fixed"] * cpi_i(k)
            ins = s["ins"] * spread_i(k, F["spread_insurance"])
            water = s["water"] * spread_i(k, F["spread_water"])
            maint = s["maint"] * cpi_i(k)
            # the unit the household leaves in Property B: market rent in year 1, then 60% of CPI
            b_rent = s["b_unit_rent"] * cum(lambda j: O["sf_rent_share_of_cpi"] * max(scn.cpi(j), 0.0), k - 1) \
                * (1 - F["vacancy"]) if rent_out_b else 0.0
            tax = inc_tax(year(k), scn.infl, ordinary=b_rent)
            net = b_rent - tax - ptax - ins - water - maint
            pf.grow(year(k), scn.infl, scn.stockr(k), scn.cashr(k))
            pf.add(net)
            rows.append({"year": year(k), "ptax": ptax, "ins": ins, "water": water, "maint": maint,
                         "income": b_rent, "inc_tax": tax, "net": net})
        gain = max(0.0, net_sale_end - s["fmv"] - (O["sec121_joint"] if H >= 2 else 0.0))
        exit_tax = inc_tax(year(H), scn.infl, ltcg=gain + pf.gain)
        key = "live" if rent_out_b else "live_empty"
        out["options"][key] = {
            "rows": rows, "home_end": fmv_end, "side": pf.value, "exit_tax": exit_tax,
            "sale_cost": fmv_end * F["selling_cost"], "taxable_gain": gain,
            "hold": fmv_end + pf.value, "liq": net_sale_end + pf.value - exit_tax,
        }

    # ---------------- option 2: rent the home out (reassessed to market value)
    pf, rows, susp, depr_acc = Portfolio(0.0), [], 0.0, 0.0
    depr = F["building_share"] * s["fmv"] / O["depr_years"]
    for k in range(1, H + 1):
        gross = s["rent"] * cum(scn.rentg, k - 1) * (1 - F["vacancy"])
        ptax = s["av_full"] * av_i(k) * O["rate_A"] + s["fixed"] * cpi_i(k)
        ins = s["ins"] * spread_i(k, F["spread_insurance"])
        maint = s["maint"] * cpi_i(k)
        taxable = gross - ptax - ins - maint - depr
        depr_acc += depr
        if taxable < 0:
            susp += -taxable
            taxable = 0.0
        else:
            use = min(susp, taxable)
            taxable -= use
            susp -= use
        tax = inc_tax(year(k), scn.infl, ordinary=taxable)
        net = gross - ptax - ins - maint - tax
        pf.grow(year(k), scn.infl, scn.stockr(k), scn.cashr(k))
        pf.add(net)
        rows.append({"year": year(k), "ptax": ptax, "ins": ins, "water": 0.0, "maint": maint,
                     "income": gross, "inc_tax": tax, "net": net, "depr": depr})
    gain_total = net_sale_end - (s["fmv"] - depr_acc)
    recap = max(0.0, min(depr_acc, gain_total))
    ltcg = max(0.0, gain_total - recap - susp)
    exit_tax = inc_tax(year(H), scn.infl, ltcg=ltcg + pf.gain, recap=recap)
    out["options"]["rent"] = {
        "rows": rows, "home_end": fmv_end, "side": pf.value, "exit_tax": exit_tax,
        "sale_cost": fmv_end * F["selling_cost"], "taxable_gain": ltcg + recap, "depr": depr,
        "hold": fmv_end + pf.value, "liq": net_sale_end + pf.value - exit_tax,
    }

    # ---------------- option 3: sell on inheritance and invest the proceeds
    carry = F["sale_months"] / 12.0 * (s["av_full"] * O["rate_A"] + s["fixed"] + s["ins"] + s["maint"] + s["water"])
    proceeds = s["fmv"] * (1 - F["selling_cost"]) - carry
    pf, rows = Portfolio(proceeds), []
    for k in range(1, H + 1):
        before = pf.tax_paid
        pf.grow(year(k), scn.infl, scn.stockr(k), scn.cashr(k))
        rows.append({"year": year(k), "value": pf.value, "inc_tax": pf.tax_paid - before})
    exit_tax = inc_tax(year(H), scn.infl, ltcg=pf.gain)
    out["options"]["sell"] = {
        "rows": rows, "proceeds": proceeds, "carry": carry, "sale_cost": s["fmv"] * F["selling_cost"],
        "side": pf.value, "exit_tax": exit_tax, "taxable_gain": pf.gain, "home_end": 0.0,
        "hold": pf.value, "liq": pf.value - exit_tax,
    }
    for o in out["options"].values():
        o["liq_real"] = o["liq"] / deflator
        o["hold_real"] = o["hold"] / deflator
    main = {k: v["liq"] for k, v in out["options"].items() if k != "live_empty"}
    out["best"] = max(main, key=main.get)
    out["deflator"] = deflator
    return out


LABEL = {"live": "Live in it", "live_empty": "Live in it (unit in Property B left empty)",
         "rent": "Rent it out", "sell": "Sell and invest"}


def breakeven_home(T, H):
    """Post-inheritance home growth at which the better keep option matches selling (base everything else)."""
    def diff(g):
        scn = Scn()
        n = H
        scn.post = {"home": [g] * n, "cpi": [scn.infl] * n, "rent": [scn.infl + F["spread_rent"]] * n,
                    "stock": [scn.stock] * n, "cash": [scn.cash] * n}
        d = decide(T, H, scn)["options"]
        return max(d["live"]["liq"], d["rent"]["liq"]) - d["sell"]["liq"]
    lo, hi = -0.05, 0.20
    if diff(lo) > 0 or diff(hi) < 0:
        return None
    for _ in range(60):
        m = (lo + hi) / 2
        if diff(m) > 0:
            hi = m
        else:
            lo = m
    return (lo + hi) / 2


def breakeven_rent(T, H):
    """Multiple of the benchmark rent at which renting matches selling (base case)."""
    def diff(m):
        d = decide(T, H, Scn(), {"rent": m})["options"]
        return d["rent"]["liq"] - d["sell"]["liq"]
    lo, hi = 0.5, 4.0
    if diff(lo) > 0 or diff(hi) < 0:
        return None
    for _ in range(60):
        m = (lo + hi) / 2
        if diff(m) > 0:
            hi = m
        else:
            lo = m
    return (lo + hi) / 2


def breakeven_stock(T, H):
    """Stock return at which selling matches the better keep option (Treasury yield and home growth at base)."""
    def diff(r):
        scn = Scn()
        scn.stock = r
        d = decide(T, H, scn)["options"]
        return d["sell"]["liq"] - max(d["live"]["liq"], d["rent"]["liq"])
    lo, hi = -0.05, 0.25
    if diff(lo) > 0 or diff(hi) < 0:
        return None
    for _ in range(60):
        m = (lo + hi) / 2
        if diff(m) > 0:
            hi = m
        else:
            lo = m
    return (lo + hi) / 2


# ------------------------------------------------------------------ year-by-year baseline projections
def project_A(scn=None, last=PROJ_LAST):
    scn = scn or Scn()
    rows = []
    fixed_2025 = A["tax"][2025] - A["assessed"][2025] * O["rate_A"]
    for y in range(BASE_YEAR, last + 1):
        n = y - BASE_YEAR
        av = A["assessed"][2026] * (1 + min(O["prop13_cap"], scn.infl)) ** n
        rows.append({
            "year": y,
            "value_low": A["value_2026"] * (1 + ASSUME["home_A"]["low"]) ** n,
            "value": A["value_2026"] * (1 + scn.gA) ** n,
            "value_high": A["value_2026"] * (1 + ASSUME["home_A"]["high"]) ** n,
            "assessed": av,
            "ptax": av * O["rate_A"] + fixed_2025 * (1 + scn.infl) ** (y - 2025),
            "ins": A["insurance_year"] * (1 + scn.infl + F["spread_insurance"]) ** n,
            "water": mid(A["water_month"]) * 12 * (1 + scn.infl + F["spread_water"]) ** n,
            "elec": mid(A["elec_month"]) * 12 if y < F["solar_legacy_latest_end"] else None,
            "maint": F["maint_A_2026"] * (1 + scn.infl) ** n,
        })
    return rows


def project_A_after(T, scn=None, last=PROJ_LAST):
    """Assessed value and property tax after inheritance in year T: Prop 19 exclusion vs full reassessment."""
    scn = scn or Scn()
    s = a_state(T, scn)
    rows = []
    for y in range(T, last + 1):
        k = y - T
        f = (1 + min(O["prop13_cap"], scn.infl)) ** k
        fixed = s["fixed"] * (1 + scn.infl) ** k
        rows.append({
            "year": y, "value": s["fmv"] * (1 + scn.gA) ** k,
            "av_none": s["fbyv"] * f, "tax_none": s["fbyv"] * f * O["rate_A"] + fixed,
            "av_live": s["av_live"] * f,
            "tax_live": (s["av_live"] * f - O["homeowners_exemption"]) * O["rate_A"] + fixed,
            "av_full": s["av_full"] * f, "tax_full": s["av_full"] * f * O["rate_A"] + fixed,
        })
    return rows


def project_B(scn=None, last=PROJ_LAST):
    scn = scn or Scn()
    rows = []
    flat_2025 = B["tax"][2025] - B["assessed"][2025] * O["rate_B"]
    for y in range(BASE_YEAR, last + 1):
        n = y - BASE_YEAR
        av = B["assessed"][2025] * (1 + min(O["prop13_cap"], scn.infl)) ** (y - 2025)
        flat = flat_2025 * (1 + scn.infl) ** (y - 2025)
        mh = O["sf_measure_h_min"] * (1 + scn.infl) ** (y - 2027) if 2027 <= y <= 2041 else 0.0
        rent = B["rent_month"] * 12 * (1 + O["sf_rent_share_of_cpi"] * scn.infl) ** n
        r = {
            "year": y,
            "value_low": B["value_2026"] * (1 + ASSUME["home_B"]["low"]) ** n,
            "value": B["value_2026"] * (1 + scn.gB) ** n,
            "value_high": B["value_2026"] * (1 + ASSUME["home_B"]["high"]) ** n,
            "assessed": av, "ptax": av * O["rate_B"] + flat + mh,
            "ins": B["insurance_year"] * (1 + scn.infl + F["spread_insurance"]) ** n,
            "water": mid(B["water_month"]) * 12 * (1 + scn.infl + F["spread_water"]) ** n,
            "elec": mid(B["elec_month"]) * 12 * (1 + scn.infl + F["spread_elec"]) ** n,
            "maint": F["maint_B_2026"] * (1 + scn.infl) ** n,
            "rent": rent,
        }
        r["net"] = r["rent"] - r["ptax"] - r["ins"] - r["water"] - r["elec"] - r["maint"]
        rows.append(r)
    return rows


# ------------------------------------------------------------------ estate threshold
def estate_exclusion(y, infl=None):
    infl = ASSUME["infl"]["base"] if infl is None else infl
    if y in O["estate_excl"]:
        return O["estate_excl"][y]
    return int(round(O["estate_excl"][2027] * (1 + infl - F["chained_gap"]) ** (y - 2027) / 10_000.0)) * 10_000


def estate_table(first=BASE_YEAR, last=2050):
    rows = []
    for y in range(first, last + 1):
        ex = estate_exclusion(y)
        n = y - BASE_YEAR
        vals = {k: A["value_2026"] * (1 + ASSUME["home_A"][k]) ** n for k in ("low", "base", "high")}
        rows.append({"year": y, "excl": ex, "excl_low": estate_exclusion(y, ASSUME["infl"]["low"]),
                     "excl_high": estate_exclusion(y, ASSUME["infl"]["high"]),
                     "home": vals["base"], "home_low": vals["low"], "home_high": vals["high"],
                     "head1": ex - vals["base"], "head2": 2 * ex - vals["base"],
                     "head1_high_home": ex - vals["high"]})
    return rows


def estate_tax(total_estate, exclusion):
    return max(0.0, total_estate - exclusion) * O["estate_rate"]


# ------------------------------------------------------------------ history (black-swan section)
def _chg(key, y):
    v = SERIES[key]["values"]
    return v[str(y)] / v[str(y - 1)] - 1


def dividend_addon():
    """Gap between the stock index fund's total return and the price-only share index, 1988-2025."""
    sh = SERIES["shares_us"]["values"]
    price = (sh["2025"] / sh["1987"]) ** (1 / 38.0) - 1
    fund = (5869 / 100.0) ** (1 / (37 + 11 / 12.0)) - 1
    return (1 + fund) / (1 + price) - 1


def history_path(start, H):
    """Actual year-by-year changes for the H years after `start` (official series)."""
    add = dividend_addon()
    yrs = range(start + 1, start + H + 1)
    return {
        "home": [_chg("hpi_sj", y) for y in yrs],
        "cpi": [_chg("cpi_dec", y) for y in yrs],
        "rent": [_chg("rent_sf", y) for y in yrs],
        "stock": [_chg("shares_us", y) + add for y in yrs],
        "cash": [SERIES["tbill3m"]["values"][str(y)] / 100.0 for y in yrs],
    }


def replay(T=CENTRAL_T, H=CENTRAL_H):
    rows = []
    for start in range(1976, 2024 - H + 1):
        scn = Scn(name=f"history {start + 1}-{start + H}")
        scn.post = history_path(start, H)
        d = decide(T, H, scn)
        infl_cum = cum(scn.cpi, H)
        rows.append({
            "start": start + 1, "end": start + H,
            "home": cum(scn.home, H) ** (1.0 / H) - 1, "cpi": infl_cum ** (1.0 / H) - 1,
            "stock": cum(scn.stockr, H) ** (1.0 / H) - 1,
            "worst_home": min(scn.post["home"]), "worst_stock": min(scn.post["stock"]),
            "max_cpi": max(scn.post["cpi"]),
            # wealth in dollars of the inheritance year (deflated by the replayed inflation)
            "live": d["options"]["live"]["liq"] / infl_cum, "rent": d["options"]["rent"]["liq"] / infl_cum,
            "sell": d["options"]["sell"]["liq"] / infl_cum, "best": d["best"],
        })
    return rows


def fifty_year_path():
    """2026-2075: smooth baseline next to a replay of the official 1976-2025 record."""
    base = Scn()
    rows = []
    a_v = a_b = A["value_2026"]
    b_v = b_b = B["value_2026"]
    a_av = a_avb = A["assessed"][2026]
    cpi_r = cpi_b = 100.0
    st_r = st_b = 100.0
    add = dividend_addon()
    factors = FACTORS
    for y in range(BASE_YEAR, LAST_YEAR + 1):
        src = y - 50                                    # 2027 <- 1977 ... 2075 <- 2025
        if y > BASE_YEAR:
            a_v *= 1 + _chg("hpi_sj", src); b_v *= 1 + _chg("hpi_sf", src)
            cpi_r *= 1 + _chg("cpi_dec", src); st_r *= 1 + _chg("shares_us", src) + add
            a_av *= factors[src]
            a_b *= 1 + base.gA; b_b *= 1 + base.gB; cpi_b *= 1 + base.infl; st_b *= 1 + base.stock
            a_avb *= 1 + O["prop13_cap"]
        rows.append({"year": y, "src": src if y > BASE_YEAR else None,
                     "home_chg": _chg("hpi_sj", src) if y > BASE_YEAR else None,
                     "cpi_chg": _chg("cpi_dec", src) if y > BASE_YEAR else None,
                     "stock_chg": _chg("shares_us", src) + add if y > BASE_YEAR else None,
                     "a_replay": a_v, "a_base": a_b, "b_replay": b_v, "b_base": b_b,
                     "av_replay": a_av, "av_base": a_avb,
                     "cpi_replay": cpi_r, "cpi_base": cpi_b, "stock_replay": st_r, "stock_base": st_b})
    return rows


# official Prop 13 inflation factors by roll year (BOE Letter to Assessors 2026/002)
FACTORS = {int(k): v for k, v in json.loads(next(
    json.loads(l)["v"] for l in open(os.path.join(HERE, "..", "_research", "notes.jsonl"))
    if json.loads(l)["k"] == "p13_factors_history")).items()}


def cagr(key, a, b):
    v = SERIES[key]["values"]
    return (v[str(b)] / v[str(a)]) ** (1.0 / (b - a)) - 1


if __name__ == "__main__":
    d = decide(CENTRAL_T, CENTRAL_H, Scn())
    print({k: round(v) for k, v in d["state"].items()})
    for k, o in d["options"].items():
        print(f"{k:11s} liq {o['liq']:>14,.0f} real {o['liq_real']:>12,.0f} hold {o['hold']:>14,.0f} side {o['side']:>12,.0f} exit tax {o['exit_tax']:>11,.0f}")
    print("best", d["best"])
    print("break-even home growth", breakeven_home(CENTRAL_T, CENTRAL_H), "stock", breakeven_stock(CENTRAL_T, CENTRAL_H))
    for T in INHERIT_YEARS:
        for H in HORIZONS:
            dd = decide(T, H, Scn())
            print(T, H, {k: round(v["liq_real"]) for k, v in dd["options"].items()}, dd["best"])
    for h in ("low", "base", "high"):
        for i in ("low", "base", "high"):
            dd = decide(CENTRAL_T, CENTRAL_H, Scn(h, i))
            print(h, i, {k: round(v["liq_real"] / 1000) for k, v in dd["options"].items()}, dd["best"])
    rp = replay()
    from collections import Counter
    print(Counter(r["best"] for r in rp), len(rp))
    print("addon", dividend_addon())
