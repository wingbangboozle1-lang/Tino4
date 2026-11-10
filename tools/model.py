#!/usr/bin/env python3
"""Projection and decision model.

Reads data/inputs.json and writes data/projections.json.
Every number is computed from (a) owner-provided inputs published in generalized
form, (b) official rules and rates recorded in data/facts/, and (c) growth rates
derived from official index series. Nothing here looks up a specific property.

Run:  python3 tools/model.py
"""
import json
import math
import pathlib
import statistics

ROOT = pathlib.Path(__file__).resolve().parent.parent
INP = json.loads((ROOT / "data" / "inputs.json").read_text())

BASE = INP["meta"]["base_year"]
H = INP["meta"]["horizon_years"]
T_YEARS = INP["meta"]["inheritance_years"]
T_HEAD = INP["meta"]["headline_year"]
A = INP["properties"]["A"]
B = INP["properties"]["B"]
RULES = INP["rules"]
CAP = RULES["prop13_cap"]
SCN = ("low", "base", "high")


# ---------------------------------------------------------------- growth rates
def cagr(v0, v1, years):
    return (v1 / v0) ** (1.0 / years) - 1.0


def windows(points):
    """Compound annual growth from each earlier point to the latest point."""
    yrs = sorted(int(y) for y in points)
    last = yrs[-1]
    out = {}
    for y in yrs[:-1]:
        out[last - y] = cagr(points[str(y)], points[str(last)], last - y)
    return out


def scen(points):
    w = windows(points)
    vals = sorted(w.values())
    return {"low": vals[0], "base": statistics.median(vals), "high": vals[-1], "windows": w}


G = {k: scen(v["points"]) for k, v in INP["series"].items()}


def geo_mean(pcts):
    prod = 1.0
    for p in pcts:
        prod *= 1.0 + p / 100.0
    return prod ** (1.0 / len(pcts)) - 1.0


_inc = INP["sf_allowable_increases"]["by_start_year"]
_years = sorted(int(y) for y in _inc)
_rc = {n: geo_mean([_inc[str(y)] for y in _years[-n:]]) for n in (10, 20, 30)}
_rv = sorted(_rc.values())
G["rent_control"] = {"low": _rv[0], "base": statistics.median(_rv), "high": _rv[-1], "windows": _rc}

INV = INP["investment_cases"]


# ---------------------------------------------------------------- helpers
def grow(v, rate, years):
    return v * (1.0 + rate) ** years


def mid(lo, hi):
    return (lo + hi) / 2.0


def direct_charges_base(prop):
    """Fixed charges on the tax bill, inferred from the owner's latest bill.

    latest bill (prior roll year) = rate x prior-year assessed value + fixed charges.
    The result is moved one year forward at base inflation to the base year.
    """
    prior_av = prop["assessed_value"] / (1.0 + CAP)
    fixed_prior = prop["latest_tax_bill"] - prop["ad_valorem_rate"] * prior_av
    return fixed_prior * (1.0 + G["cpi"]["base"])


DIRECT0 = {"A": direct_charges_base(A), "B": direct_charges_base(B)}
PROP = {"A": A, "B": B}
HOME = {"A": "home_A", "B": "home_B"}


def market_value(p, year, s="base"):
    return grow(PROP[p]["market_value"], G[HOME[p]][s], year - BASE)


def assessed_current_owner(p, year):
    return grow(PROP[p]["assessed_value"], CAP, year - BASE)


def direct_charges(p, year, s="base"):
    return grow(DIRECT0[p], G["cpi"][s], year - BASE)


def tax_bill(p, taxable_value, year, s="base"):
    return PROP[p]["ad_valorem_rate"] * taxable_value + direct_charges(p, year, s)


def excluded_amount(year, s="base"):
    """Proposition 19 '$1 million' amount in a given year.

    Official: $1,044,586 through Feb 15, 2027; adjusted every other Feb 16 by the
    FHFA California index change for the prior calendar year only.
    Projection: one year of scenario home-price growth is applied in each odd year.
    """
    e = RULES["prop19_excluded_amount_2026"]
    for y in range(BASE + 1, year + 1):
        if y % 2 == 1:
            e *= 1.0 + G["home_A"][s]
    return e


def prop19_taxable_value(fbyv, fmv, excl):
    """New taxable value for a qualifying family-home transfer (R&T Code 63.2)."""
    limit = fbyv + excl
    if fmv <= limit:
        return fbyv
    return fbyv + (fmv - limit)


def estate_exemption(year, s="base"):
    ex = RULES["estate_exemption"]
    if str(year) in ex:
        return ex[str(year)]
    return grow(ex["2027"], G["ccpi"][s], year - 2027)


def cost_A(year, s="base"):
    return {
        "insurance": grow(A["insurance_annual"], G["cpi"][s], year - BASE),
        "water": grow(12 * mid(A["water_monthly_low"], A["water_monthly_high"]), G["water"][s], year - BASE),
        "electricity": grow(12 * mid(A["electricity_monthly_low"], A["electricity_monthly_high"]), G["electricity"][s], year - BASE),
    }


def cost_B(year, s="base"):
    return {
        "insurance": grow(B["insurance_annual"], G["cpi"][s], year - BASE),
        "water": grow(12 * mid(B["water_monthly_low"], B["water_monthly_high"]), G["water"][s], year - BASE),
        "electricity": grow(12 * mid(B["electricity_monthly_low"], B["electricity_monthly_high"]), G["electricity"][s], year - BASE),
    }


def rent_A(year, s="base", bedrooms=4):
    key = "rent_benchmark_monthly_4br" if bedrooms == 4 else "rent_benchmark_monthly_3br"
    return 12 * grow(A[key], G["rent"][s], year - BASE)


def rent_B_existing(year, s="base"):
    return 12 * grow(B["rent_monthly"], G["rent_control"][s], year - BASE)


def rent_B_third_unit(year, T, s="base"):
    """Third unit rented from the inheritance year T: starts at the average of the two
    current rents moved to year T at market-rent growth, then follows the rent-control rate."""
    start = (B["rent_monthly"] / B["units_rented"]) * (1.0 + G["rent"][s]) ** (T - BASE)
    return 12 * start * (1.0 + G["rent_control"][s]) ** (year - T)


# ---------------------------------------------------------------- self checks (official examples)
assert round(prop19_taxable_value(300000, 1500000, 1000000)) == 500000   # BOE Prop 19 FAQ 6
assert round(prop19_taxable_value(159181, 800000, 1000000)) == 159181    # BOE LTA 2026/026 Q51
assert round(prop19_taxable_value(163076, 1200000, 1000000)) == 200000   # LTA 2026/026 Q50 (163,076 + 36,924)


# ---------------------------------------------------------------- tables
def yearly_table():
    rows = []
    for y in range(BASE, 2051):
        row = {"year": y}
        for p in ("A", "B"):
            av = assessed_current_owner(p, y)
            row[p] = {
                "value": {s: market_value(p, y, s) for s in SCN},
                "assessed": av,
                "tax": tax_bill(p, av, y),
            }
        row["excluded_amount"] = {s: excluded_amount(y, s) for s in SCN}
        row["estate_exemption"] = {s: estate_exemption(y, s) for s in SCN}
        rows.append(row)
    return rows


def inheritance_table(s="base"):
    rows = []
    for T in T_YEARS:
        vA = market_value("A", T, s)
        fbyv = assessed_current_owner("A", T)
        excl = excluded_amount(T, s)
        ntv_live = prop19_taxable_value(fbyv, vA, excl)
        y1 = T + 1
        vB = market_value("B", T, s)
        avB = assessed_current_owner("B", T)
        rows.append({
            "year": T,
            "A": {
                "value": vA,
                "assessed_before": fbyv,
                "excluded_amount": excl,
                "taxable_live": ntv_live,
                "taxable_full": vA,
                "tax_before": tax_bill("A", fbyv * (1 + CAP), y1, s),
                "tax_live": tax_bill("A", ntv_live * (1 + CAP), y1, s),
                "tax_full": tax_bill("A", vA * (1 + CAP), y1, s),
            },
            "B": {
                "value": vB,
                "assessed_before": avB,
                "taxable_full": vB,
                "tax_before": tax_bill("B", avB * (1 + CAP), y1, s),
                "tax_full": tax_bill("B", vB * (1 + CAP), y1, s),
            },
        })
    return rows


def option_flows(T, s="base", bedrooms=4):
    """Year-by-year cash flows for each option, years T+1 .. T+H (before income tax)."""
    vA_T = market_value("A", T, s)
    fbyv = assessed_current_owner("A", T)
    ntv_live = prop19_taxable_value(fbyv, vA_T, excluded_amount(T, s))
    out = []
    for k in range(1, H + 1):
        y = T + k
        c = cost_A(y, s)
        tax_live = tax_bill("A", ntv_live * (1 + CAP) ** k, y, s)
        tax_full = tax_bill("A", vA_T * (1 + CAP) ** k, y, s)
        rent = rent_A(y, s, bedrooms)
        out.append({
            "year": y,
            "k": k,
            "value_A": vA_T * (1 + G["home_A"][s]) ** k,
            "live": {
                "property_tax": tax_live,
                "insurance": c["insurance"],
                "water": c["water"],
                "electricity": c["electricity"],
                "total_cost": tax_live + c["insurance"] + c["water"] + c["electricity"],
                "third_unit_rent": rent_B_third_unit(y, T, s),
            },
            "rent": {
                "rent": rent,
                "property_tax": tax_full,
                "insurance": c["insurance"],
                "net": rent - tax_full - c["insurance"],
            },
        })
    return out


def sale_proceeds(T, s="base", commission=None):
    c = RULES["selling_commission"] if commission is None else commission
    v = market_value("A", T, s)
    return {
        "price": v,
        "commission": v * c,
        "transfer_tax": v * RULES["transfer_tax_rate"],
        "net": v * (1 - c - RULES["transfer_tax_rate"]),
        "taxable_gain": 0.0,
    }


def wealth(T, s="base", r=0.05, bedrooms=4, post_growth=None):
    """Wealth attributable to Property A at T+H under each option, before income tax.

    The house is still held at T+H (no sale costs). Yearly cash flows are
    reinvested (or, for costs, funded) at the investment rate r.
    """
    flows = option_flows(T, s, bedrooms)
    gA = G["home_A"][s] if post_growth is None else post_growth
    v_end = market_value("A", T, s) * (1 + gA) ** H
    sell = sale_proceeds(T, s)["net"] * (1 + r) ** H
    fv_rent = sum(f["rent"]["net"] * (1 + r) ** (H - f["k"]) for f in flows)
    fv_cost = sum(f["live"]["total_cost"] * (1 + r) ** (H - f["k"]) for f in flows)
    fv_unit3 = sum(f["live"]["third_unit_rent"] * (1 + r) ** (H - f["k"]) for f in flows)
    return {
        "sell": sell,
        "rent": v_end + fv_rent,
        "live_empty": v_end - fv_cost,
        "live_rented": v_end - fv_cost + fv_unit3,
        "house_value_end": v_end,
    }


TAXR = INP["illustrative_tax"]
T_ORD = TAXR["ordinary_federal"] + TAXR["ordinary_california"]
T_GAIN = TAXR["capital_gain_federal"] + TAXR["niit"] + TAXR["capital_gain_california"]
SELL_COST = RULES["selling_commission"] + RULES["transfer_tax_rate"]


def after_tax_multiple(case):
    """Value of $1 after H years, after illustrative income tax, cashed out at the end.

    The share of each year's return that is interest ('income_share') is taxed
    every year at the ordinary rate; the rest is treated as unrealized gain and
    taxed once, at the capital-gain rate, when cashed out.
    """
    r, share = case["rate"], case["income_share"]
    value, basis = 1.0, 1.0
    for _ in range(H):
        interest = value * r * share * (1 - T_ORD)
        gain = value * r * (1 - share)
        value += interest + gain
        basis += interest
    return value - T_GAIN * (value - basis)


def wealth_after_tax(T, s="base", case=None, bedrooms=4):
    """Everything cashed out at T+H, after illustrative income tax."""
    flows = option_flows(T, s, bedrooms)
    mult = after_tax_multiple(case)
    r_eff = mult ** (1.0 / H) - 1.0
    v_T = market_value("A", T, s)
    v_end = v_T * (1 + G["home_A"][s]) ** H
    net_sale = v_end * (1 - SELL_COST)
    gain = net_sale - v_T
    house_rent = net_sale - T_GAIN * max(0.0, gain)
    house_live = net_sale - T_GAIN * max(0.0, gain - TAXR["home_sale_exclusion"])
    fv = lambda amt, k: amt * (1 + r_eff) ** (H - k)
    fv_rent = sum(fv(f["rent"]["net"] * (1 - T_ORD), f["k"]) for f in flows)
    fv_cost = sum(fv(f["live"]["total_cost"], f["k"]) for f in flows)
    fv_unit3 = sum(fv(f["live"]["third_unit_rent"] * (1 - T_ORD), f["k"]) for f in flows)
    return {
        "sell": sale_proceeds(T, s)["net"] * mult,
        "rent": house_rent + fv_rent,
        "live_empty": house_live - fv_cost,
        "live_rented": house_live - fv_cost + fv_unit3,
        "effective_return": r_eff,
    }


def breakeven_return(T, s="base"):
    """Investment return at which selling and renting give the same pre-tax wealth."""
    lo, hi = 0.0, 0.30
    for _ in range(80):
        m = (lo + hi) / 2
        w = wealth(T, s, m)
        if w["sell"] < w["rent"]:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def upkeep_sensitivity(r):
    """Effect on the T+H result of $10,000 a year of extra cost, rising with base inflation."""
    return sum(10000 * (1 + G["cpi"]["base"]) ** (k - 1) * (1 + r) ** (H - k) for k in range(1, H + 1))


def breakeven_upkeep(T, r, s="base"):
    """First-year upkeep (rising with inflation) that would make renting equal selling."""
    w = wealth(T, s, r)
    gap = w["rent"] - w["sell"]
    return gap / upkeep_sensitivity(r) * 10000


def deflator(year):
    return (1 + G["cpi"]["base"]) ** (year - BASE)


def breakeven_growth(T, r, s="base"):
    """House appreciation after inheritance at which renting equals selling."""
    lo, hi = -0.05, 0.30
    for _ in range(80):
        m = (lo + hi) / 2
        w = wealth(T, s, r, post_growth=m)
        if w["rent"] < w["sell"]:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def breakeven_rent(T, r, s="base"):
    """Monthly rent in the first year at which renting equals selling."""
    base_rent = rent_A(T + 1, s) / 12
    lo, hi = 0.0, 20.0
    flows = option_flows(T, s)
    v_end = market_value("A", T, s) * (1 + G["home_A"][s]) ** H
    sell = sale_proceeds(T, s)["net"] * (1 + r) ** H
    for _ in range(80):
        m = (lo + hi) / 2
        fv = sum((f["rent"]["rent"] * m - f["rent"]["property_tax"] - f["rent"]["insurance"]) * (1 + r) ** (H - f["k"]) for f in flows)
        if v_end + fv < sell:
            lo = m
        else:
            hi = m
    return base_rent * (lo + hi) / 2


def property_B_after(T, s="base"):
    y = T + 1
    rent = rent_B_existing(y, s)
    c = cost_B(y, s)
    av = assessed_current_owner("B", T)
    before = tax_bill("B", av * (1 + CAP), y, s)
    after = tax_bill("B", market_value("B", T, s) * (1 + CAP), y, s)
    costs = c["insurance"] + c["water"] + c["electricity"]
    return {
        "year": y, "rent": rent, "insurance": c["insurance"], "water": c["water"], "electricity": c["electricity"],
        "tax_before": before, "tax_after": after,
        "net_before": rent - costs - before, "net_after": rent - costs - after,
        "value": market_value("B", T, s),
    }


def estate_table():
    rows = []
    for y in [2026, 2027, 2030, 2035] + T_YEARS:
        ex = estate_exemption(y)
        vA, vB = market_value("A", y), market_value("B", y)
        rows.append({
            "year": y, "exemption": ex, "exemption_low": estate_exemption(y, "low"), "exemption_high": estate_exemption(y, "high"),
            "value_A": vA, "value_B": vB,
            "headroom_A": ex - vA, "headroom_AB": ex - vA - vB,
            "headroom_AB_two": 2 * ex - vA - vB,
        })
    return rows


def costs_table():
    rows = []
    for y in range(BASE, 2051):
        a, b = cost_A(y), cost_B(y)
        rows.append({"year": y, "A": a, "B": b, "rent_B": rent_B_existing(y)})
    return rows


def lifetime_sale_illustration():
    """Tax if the current owners sold Property A today, versus after inheritance.

    Assumptions (illustration only): joint filers, no other income, tax basis no higher
    than the current assessed value, full $500,000 home-sale exclusion.
    Federal 2027 thresholds (Rev. Proc. 2026-35); California 2025 Schedule Y.
    """
    price = A["market_value"]
    basis = A["assessed_value"]
    gain = price - basis
    taxable = gain - 500000
    fed = 0.15 * (633600 - 102100) + 0.20 * (taxable - 633600)
    niit = 0.038 * min(taxable, taxable - 250000)
    ca = 144439.65 + 0.123 * (taxable - 1485906)
    return {"price": price, "basis": basis, "gain": gain, "exclusion": 500000, "taxable_gain": taxable,
            "federal": fed, "niit": niit, "california": ca, "total": fed + niit + ca}


def build():
    out = {
        "meta": {"base_year": BASE, "horizon": H, "headline_year": T_HEAD,
                 "tax_ordinary": T_ORD, "tax_gain": T_GAIN, "selling_cost": SELL_COST},
        "rates": {k: {"low": v["low"], "base": v["base"], "high": v["high"],
                      "windows": {str(n): r for n, r in sorted(v["windows"].items())}} for k, v in G.items()},
        "direct_charges_base": DIRECT0,
        "yearly": yearly_table(),
        "inheritance": {s: inheritance_table(s) for s in SCN},
        "costs": costs_table(),
        "estate": estate_table(),
        "lifetime_sale": lifetime_sale_illustration(),
        "options": {},
        "wealth": {},
        "breakeven": {},
        "property_B": {str(T): property_B_after(T) for T in T_YEARS},
        "sale": {str(T): sale_proceeds(T) for T in T_YEARS},
    }
    for T in T_YEARS:
        out["options"][str(T)] = option_flows(T)
        out["wealth"][str(T)] = {
            s: {c["key"]: wealth(T, s, c["rate"]) for c in INV} for s in SCN
        }
    out["wealth_after_tax"] = {
        s: {c["key"]: wealth_after_tax(T_HEAD, s, c) for c in INV} for s in SCN
    }
    out["breakeven_return"] = {s: breakeven_return(T_HEAD, s) for s in SCN}
    out["upkeep"] = {c["key"]: {"per_10k": upkeep_sensitivity(c["rate"]),
                                "breakeven_first_year": breakeven_upkeep(T_HEAD, c["rate"])} for c in INV}
    out["deflator"] = {str(y): deflator(y) for y in range(BASE, 2062)}
    out["wealth_3br"] = {c["key"]: wealth(T_HEAD, "base", c["rate"], bedrooms=3) for c in INV}
    out["breakeven"] = {
        c["key"]: {"growth": breakeven_growth(T_HEAD, c["rate"]), "rent_monthly": breakeven_rent(T_HEAD, c["rate"]),
                   "benchmark_rent_monthly": rent_A(T_HEAD + 1) / 12}
        for c in INV
    }
    out["sale_no_commission"] = sale_proceeds(T_HEAD, commission=0.0)
    (ROOT / "data" / "projections.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


if __name__ == "__main__":
    o = build()
    r = o["rates"]
    print("growth rates (low / base / high):")
    for k, v in r.items():
        print(f"  {k:13s} {v['low']*100:5.2f}% {v['base']*100:5.2f}% {v['high']*100:5.2f}%   windows " +
              ", ".join(f"{n}y {x*100:.2f}%" for n, x in v["windows"].items()))
    print("direct charges base year:", {k: round(v) for k, v in o["direct_charges_base"].items()})
    h = [x for x in o["inheritance"]["base"] if x["year"] == T_HEAD][0]
    print("headline", T_HEAD, {k: round(v) for k, v in h["A"].items()})
    print("B", {k: round(v) for k, v in h["B"].items()})
    print("wealth", {s: {k: {a: round(b) for a, b in v.items()} for k, v in d.items()} for s, d in o["wealth"][str(T_HEAD)].items()}["base"])
    print("breakeven", o["breakeven"])
    print("lifetime sale", {k: round(v) for k, v in o["lifetime_sale"].items()})
    print("breakeven return", {k: round(v * 100, 2) for k, v in o["breakeven_return"].items()})
    print("upkeep", {k: {a: round(b) for a, b in v.items()} for k, v in o["upkeep"].items()})
    for sc in SCN:
        for k, v in o["wealth_after_tax"][sc].items():
            print(f"  after-tax {sc:4s} {k:9s} " + " ".join(f"{a} {b/1e6:6.2f}M" for a, b in v.items() if a != "effective_return") + f"  r_eff {v['effective_return']*100:.2f}%")
