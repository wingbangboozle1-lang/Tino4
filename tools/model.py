#!/usr/bin/env python3
"""Projection and decision model for the inherited-property analysis.

All inputs live in data/assumptions.json and data/facts.json.  This script
writes data/projections.json and data/decisions.json, which tools/build.py
renders into static HTML.  Nothing here is hand-entered into the site.

Conventions
-----------
* All dollar outputs are rounded to the nearest $10 (requirement).
* "nominal" = future dollars; "today" = deflated by CPI to 2026 dollars.
* Every derived figure is traceable to a line in data/assumptions.json.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name):
    with open(os.path.join(ROOT, "data", name)) as fh:
        return json.load(fh)


A = load("assumptions.json")

CPI = A["inflation"]["cpi_base"]
APPR = A["appreciation"]["base"]
RINV = A["investment"]["after_tax_nominal_base"]
INH = A["inheritance_year"]
END = A["horizon_end"]
START = 2026

CUP_V0 = 3_100_000
CUP_AV0 = 550_537
SF_V0 = 1_800_000
SF_AV0_2025 = 114_248
SF_AV0 = SF_AV0_2025 * 1.02  # 2026-27 roll: 2% factor (BOE LTA 2026/002)

PT = A["property_tax"]
FACTOR = PT["prop13_factor"]
CUP_RATE = PT["cupertino_advalorem_base"]
CUP_CH = PT["cupertino_charges_2026"]
SF_RATE = PT["sf_advalorem"]
SF_CH = PT["sf_charges_2026"]

CGT = sum(A["capital_gains"].values())
RIT = sum(A["rental_income_tax"].values())


def r10(x):
    return int(round(x / 10.0) * 10)


def g(base, rate, n):
    return base * (1 + rate) ** n


# --------------------------------------------------------------------------
# Property series (2026 .. 2065)
# --------------------------------------------------------------------------
def build_series():
    rows_C, rows_S = [], []
    for y in range(START, END + 1):
        n = y - START
        # Cupertino
        val = g(CUP_V0, APPR, n)
        av = g(CUP_AV0, FACTOR, n)
        tax = CUP_RATE * av + g(CUP_CH, CPI, n)
        ins = g(1500, 0.05, n)
        water = g(1500, 0.06, n)
        elec = g(-180, 0.04, n)
        maint = g(6000, CPI + 0.01, n)
        rows_C.append({
            "year": y, "market_value": r10(val), "assessed": r10(av),
            "tax": r10(tax), "insurance": r10(ins), "water": r10(water),
            "electric": r10(elec), "maintenance": r10(maint),
            "effective_rate_of_market": round(tax / val * 100, 2),
        })
        # San Francisco
        sval = g(SF_V0, APPR, n)
        sav = g(SF_AV0, FACTOR, n)
        stax = SF_RATE * sav + g(SF_CH, CPI, n)
        rows_S.append({
            "year": y, "market_value": r10(sval), "assessed": r10(sav),
            "tax": r10(stax), "insurance": r10(g(1500, 0.05, n)),
            "water": r10(g(4380, 0.06, n)),
            "electric": r10(g(600, 0.04, n)),
            "maintenance": r10(g(9000, 0.04, n)),
            "rent_two_units": r10(7150 * 12 * (1.016 ** n)),
            "effective_rate_of_market": round(stax / sval * 100, 2),
        })
    return rows_C, rows_S


# --------------------------------------------------------------------------
# Prop 19 outcome at the inheritance year
# --------------------------------------------------------------------------
def prop19(year=INH):
    n = year - START
    fbyv = g(CUP_AV0, FACTOR, n)
    fmv = g(CUP_V0, APPR, n)
    cap = g(A["prop19_cap_2026"], A["prop19_cap_growth"], n)
    excluded_cap = fbyv + cap
    if fmv <= excluded_cap:
        reassessed_if_claimed = fbyv
        excess = 0
    else:
        excess = fmv - excluded_cap
        reassessed_if_claimed = fbyv + excess
    return {
        "year": year,
        "factored_base_year_value": r10(fbyv),
        "market_value": r10(fmv),
        "cap_amount": r10(cap),
        "excluded_value_cap": r10(excluded_cap),
        "excess_above_cap": r10(excess),
        "taxable_if_claimed": r10(reassessed_if_claimed),
        "taxable_if_not_claimed": r10(fmv),
        "tax_if_claimed": r10(CUP_RATE * reassessed_if_claimed + CUP_CH * (1 + CPI) ** n),
        "tax_if_not_claimed": r10(CUP_RATE * fmv + CUP_CH * (1 + CPI) ** n),
        "first_year_saving": r10(CUP_RATE * (fmv - reassessed_if_claimed)),
    }


# --------------------------------------------------------------------------
# Scenario engine
# --------------------------------------------------------------------------
def rental_tax(gross_rent, opex, basis):
    """Income tax on net rental income after straight-line depreciation."""
    dep = basis * A["depreciation_building_share"] / A["depreciation_years"]
    taxable = max(0.0, gross_rent - opex - dep)
    return taxable * RIT, dep


def run_scenario(key, appr=APPR, rinv=RINV, inh=INH):
    n0 = inh - START
    cup_val = g(CUP_V0, appr, n0)
    sf_val = g(SF_V0, appr, n0)
    p19 = prop19(inh)

    # start-of-scenario inputs (inheritance year)
    cup_av = g(CUP_AV0, FACTOR, n0)          # preserved base year value
    cup_tax_base = p19["taxable_if_claimed"]  # if exclusion preserved
    cup_tax_full = p19["taxable_if_not_claimed"]
    sf_av = g(SF_AV0, FACTOR, n0)
    sf_basis = sf_val                        # stepped-up basis at death
    cup_basis = cup_val
    portfolio = 0.0
    cum_cf = 0.0
    rows = []

    for y in range(inh, END + 1):
        n = y - START
        m = y - inh
        val_c = g(cup_val, appr, m)
        val_s = g(sf_val, appr, m)
        av_c_keep = g(cup_tax_base, FACTOR, m)
        av_c_full = g(cup_tax_full, FACTOR, m)
        av_s = g(sf_av, FACTOR, m)
        cup_ch = g(CUP_CH, CPI, n)
        sf_ch = g(SF_CH, CPI, n)
        ins_c = g(1500, 0.05, n)
        ins_s = g(1500, 0.05, n)
        water_c = g(1500, 0.06, n)
        water_s = g(4380, 0.06, n)
        elec_c = g(-180, 0.04, n)
        elec_s = g(600, 0.04, n)
        maint_c = g(6000, CPI + 0.01, n)
        maint_s = g(9000, 0.04, n)
        rent_s_two = 7150 * 12 * (1.016 ** n)
        rent_s_three = rent_s_two + g(3600 * 12, CPI, n)   # third unit reset at market
        rent_base = globals().get("CUP_RENT_OVERRIDE") or 6000
        rent_c = g(rent_base * 12, CPI, n)                # assumption, flagged
        housing_rent = g(4500 * 12, CPI, n)               # scenario D only

        cf = 0.0
        detail = {}
        if key == "A":  # live in Cupertino, rent all three SF units
            cup_tax = CUP_RATE * av_c_keep + cup_ch
            cup_opex = cup_tax + ins_c + water_c + elec_c + maint_c
            gross = rent_s_three * (1 - A["vacancy_pct"])
            sf_opex = SF_RATE * av_s + sf_ch + ins_s + water_s + elec_s + maint_s + gross * A["management_pct"]
            tax_s, _ = rental_tax(gross, sf_opex, sf_basis)
            imputed = g((globals().get("CUP_RENT_OVERRIDE") or 6000) * 12, CPI, n)  # value of living in the Cupertino house
            cf = gross - sf_opex - tax_s - cup_opex + imputed
            detail = {"cup_tax": cup_tax, "cup_opex": cup_opex, "sf_gross": gross, "sf_opex": sf_opex,
                      "sf_tax": tax_s, "cup_rent": 0.0}
        elif key == "B":  # rent Cupertino (exclusion lost), live in third SF unit
            cup_tax = CUP_RATE * av_c_full + cup_ch
            cup_opex = cup_tax + ins_c * 1.15 + water_c + elec_c + maint_c
            gross_c = rent_c * (1 - A["vacancy_pct"])
            cup_opex += gross_c * A["management_pct"]
            tax_c, _ = rental_tax(gross_c, cup_opex, cup_basis)
            gross_s = rent_s_two * (1 - A["vacancy_pct"])
            sf_opex = SF_RATE * av_s + sf_ch + ins_s + water_s + elec_s + maint_s + gross_s * A["management_pct"]
            tax_s, _ = rental_tax(gross_s, sf_opex, sf_basis)
            imputed = g(3600 * 12, CPI, n)      # value of living in the Sunset flat
            cf = (gross_c - cup_opex - tax_c) + (gross_s - sf_opex - tax_s) + imputed
            detail = {"cup_tax": cup_tax, "cup_opex": cup_opex, "sf_gross": gross_s,
                      "sf_opex": sf_opex, "sf_tax": tax_s, "cup_rent": gross_c}
        elif key == "C":  # sell Cupertino, invest, live in third SF unit
            if m == 0:
                proceeds = val_c * (1 - A["selling_cost_pct"] - A["cupertino_transfer_tax_pct"])
                gain = max(0.0, val_c - cup_basis)
                proceeds -= gain * CGT
                portfolio += proceeds
            else:
                proceeds = 0.0
            gross_s = rent_s_two * (1 - A["vacancy_pct"])
            sf_opex = SF_RATE * av_s + sf_ch + ins_s + water_s + elec_s + maint_s + gross_s * A["management_pct"]
            tax_s, _ = rental_tax(gross_s, sf_opex, sf_basis)
            imputed = g(3600 * 12, CPI, n)      # value of living in the Sunset flat
            cf = gross_s - sf_opex - tax_s + imputed
            detail = {"sale_proceeds": proceeds, "sf_gross": gross_s, "sf_opex": sf_opex,
                      "sf_tax": tax_s, "cup_tax": 0.0, "cup_rent": 0.0}
        elif key == "D":  # sell both, invest, rent housing
            if m == 0:
                p_c = val_c * (1 - A["selling_cost_pct"] - A["cupertino_transfer_tax_pct"])
                p_s = val_s * (1 - A["selling_cost_pct"] - A["sf_transfer_tax_pct"])
                gain_c = max(0.0, val_c - cup_basis)
                gain_s = max(0.0, val_s - sf_basis)
                portfolio += p_c + p_s - (gain_c + gain_s) * CGT
            else:
                p_c = p_s = 0.0
            cf = -housing_rent
            detail = {"sale_proceeds": p_c + p_s, "housing_rent": housing_rent,
                      "cup_tax": 0.0, "cup_rent": 0.0, "sf_gross": 0.0, "sf_opex": 0.0, "sf_tax": 0.0}

        portfolio = portfolio * (1 + rinv) + cf
        cum_cf += cf

        prop_equity = 0.0
        for k, v in (("A", (val_c, val_s)), ("B", (val_c, val_s)), ("C", (0.0, val_s)), ("D", (0.0, 0.0))):
            if k == key:
                prop_equity = v[0] + v[1]
        rows.append({"year": y, "cash_flow": r10(cf), "portfolio": r10(portfolio),
                     "property_value": r10(prop_equity), **{k: r10(v) for k, v in detail.items()}})

    # liquidation at END
    last = rows[-1]
    m_end = END - inh
    val_c_end = g(cup_val, appr, m_end)
    val_s_end = g(sf_val, appr, m_end)
    if key == "A" or key == "B":
        sold = val_c_end * (1 - A["selling_cost_pct"] - A["cupertino_transfer_tax_pct"])
        gain = max(0.0, val_c_end - cup_basis)
        sold -= gain * CGT
        sold_s = val_s_end * (1 - A["selling_cost_pct"] - A["sf_transfer_tax_pct"])
        gain_s = max(0.0, val_s_end - sf_basis)
        sold += sold_s - gain_s * CGT
    elif key == "C":
        sold = val_s_end * (1 - A["selling_cost_pct"] - A["sf_transfer_tax_pct"])
        gain_s = max(0.0, val_s_end - sf_basis)
        sold -= gain_s * CGT
    else:
        sold = 0.0

    net_worth = last["portfolio"] + sold
    if key in ("A", "B"):
        gross_prop = val_c_end + val_s_end
        deferred = (max(0.0, val_c_end - cup_basis) + max(0.0, val_s_end - sf_basis)) * CGT
    elif key == "C":
        gross_prop = val_s_end
        deferred = max(0.0, val_s_end - sf_basis) * CGT
    else:
        gross_prop = 0.0
        deferred = 0.0
    hold_basis = last["portfolio"] + gross_prop
    deflator = (1 + CPI) ** (END - START)
    return {
        "net_worth_hold_2065": r10(hold_basis),
        "net_worth_hold_2065_today": r10(hold_basis / deflator),
        "deferred_capital_gains_tax": r10(deferred),
        "gross_property_2065": r10(gross_prop),
        "key": key,
        "net_worth_2065": r10(net_worth),
        "net_worth_2065_today": r10(net_worth / deflator),
        "portfolio_2065": r10(last["portfolio"]),
        "property_net_2065": r10(sold),
        "cumulative_cash_flow": r10(cum_cf),
        "rows": rows,
    }


SCENARIO_META = {
    "A": {"name": "Live in the Cupertino house", "sub": "Preserve the Prop 19 base; rent all three Sunset units",
          "eligibility": "Requires the exclusion to be preserved (parent used it as a principal residence; heir moves in within 1 year and files the exemption + BOE-19-P)."},
    "B": {"name": "Rent the Cupertino house", "sub": "Exclusion lost, reassessed to market; live in the vacant Sunset unit",
          "eligibility": "No occupancy requirement. Property tax resets to full market value."},
    "C": {"name": "Sell Cupertino and invest", "sub": "Net proceeds into a diversified portfolio; live in the Sunset unit",
          "eligibility": "Step-up basis means little or no capital gain if sold soon after death."},
    "D": {"name": "Sell both houses and invest", "sub": "Full liquidity; rent housing at market",
          "eligibility": "Largest tax-free (basis-stepped) liquidity event, but gives up both low tax bases and rent control income."},
}


def main():
    rows_C, rows_S = build_series()
    p19 = prop19()
    scen = [run_scenario(k) for k in "ABCD"]
    for s in scen:
        s.update(SCENARIO_META[s["key"]])
        s.pop("rows", None)

    # scenario detail for the two living-arrangement scenarios (annual table)
    detail_A = run_scenario("A")["rows"]
    detail_B = run_scenario("B")["rows"]

    # estate tax path: exclusion indexed from $15M in 2026
    estate = []
    for y in [2026, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2065]:
        n = y - START
        ex = g(A["estate_exclusion_2026"], A["estate_indexing"], n)
        estate.append({
            "year": y, "exclusion": r10(ex),
            "tax_on_10m": r10(max(0, 10e6 - ex) * A["federal_estate_rate"]),
            "tax_on_15m": r10(max(0, 15e6 - ex) * A["federal_estate_rate"]),
            "tax_on_20m": r10(max(0, 20e6 - ex) * A["federal_estate_rate"]),
            "tax_on_25m": r10(max(0, 25e6 - ex) * A["federal_estate_rate"]),
            "tax_on_30m": r10(max(0, 30e6 - ex) * A["federal_estate_rate"]),
        })

    # sensitivity: appreciation x investment return
    sens = []
    for ap in [0.025, 0.035, 0.045]:
        for ri in [0.04, 0.055, 0.07]:
            res = {k: run_scenario(k, appr=ap, rinv=ri)["net_worth_2065"] for k in "ABCD"}
            best = max(res, key=res.get)
            sens.append({"appreciation": ap, "investment": ri, "best": best, **{k: r10(v) for k, v in res.items()}})

    # inheritance timing sensitivity for scenario A vs C
    timing = []
    for inh in [2040, 2045, 2050]:
        a = run_scenario("A", inh=inh)["net_worth_2065"]
        c = run_scenario("C", inh=inh)["net_worth_2065"]
        timing.append({"inheritance_year": inh, "live": r10(a), "sell_invest": r10(c), "advantage_live": r10(a - c)})

    # break-even appreciation: lowest appreciation at which "live" beats "sell & invest"
    breakeven = []
    for ri in [0.04, 0.055, 0.07]:
        lo, hi = 0.02, 0.10
        for _ in range(40):
            mid = (lo + hi) / 2
            if run_scenario("A", appr=mid, rinv=ri)["net_worth_2065"] > run_scenario("C", appr=mid, rinv=ri)["net_worth_2065"]:
                hi = mid
            else:
                lo = mid
        breakeven.append({"investment": ri, "appreciation": round((lo + hi) / 2 * 100, 2)})

    # rent sensitivity for scenario A (the Cupertino market-rent assumption)
    rent_sens = []
    for rent in [5000, 6000, 7000, 8000]:
        globals()["CUP_RENT_OVERRIDE"] = rent
        rent_sens.append({"rent": rent, "A": run_scenario("A")["net_worth_2065"],
                          "C": run_scenario("C")["net_worth_2065"]})
    globals()["CUP_RENT_OVERRIDE"] = None

    out = {
        "breakeven": breakeven,
        "rent_sensitivity": rent_sens,
        "meta": {"start": START, "inheritance": INH, "end": END, "cpi": CPI, "appreciation": APPR,
                 "investment_return": RINV, "retrieved": "2026-11-10"},
        "cupertino_series": rows_C,
        "sf_series": rows_S,
        "prop19": p19,
        "scenarios": scen,
        "detail_A": [r for r in detail_A if r["year"] in (INH, INH + 5, INH + 10, INH + 15, END)],
        "detail_B": [r for r in detail_B if r["year"] in (INH, INH + 5, INH + 10, INH + 15, END)],
        "estate": estate,
        "sensitivity": sens,
        "timing": timing,
    }
    with open(os.path.join(ROOT, "data", "projections.json"), "w") as fh:
        json.dump(out, fh, indent=1)

    dec = {
        "ranking": sorted(
            [{"key": s["key"], "name": s["name"], "net_worth": s["net_worth_2065"]} for s in scen],
            key=lambda x: -x["net_worth"]),
        "delta_A_minus_B": r10(next(s for s in scen if s["key"] == "A")["net_worth_2065"]
                              - next(s for s in scen if s["key"] == "B")["net_worth_2065"]),
        "delta_A_minus_C": r10(next(s for s in scen if s["key"] == "A")["net_worth_2065"]
                              - next(s for s in scen if s["key"] == "C")["net_worth_2065"]),
        "prop19_value_20yr": r10((p19["tax_if_not_claimed"] - p19["tax_if_claimed"]) * 20 * 0.72),
    }
    with open(os.path.join(ROOT, "data", "decisions.json"), "w") as fh:
        json.dump(dec, fh, indent=1)

    print(json.dumps(dec, indent=2))
    print("prop19:", json.dumps(p19, indent=2))
    for s in scen:
        print(s["key"], f'liq {s["net_worth_2065"]:,}', f'hold {s["net_worth_hold_2065"]:,}',
              f'deferred {s["deferred_capital_gains_tax"]:,}', f'cf {s["cumulative_cash_flow"]:,}')


if __name__ == "__main__":
    main()
