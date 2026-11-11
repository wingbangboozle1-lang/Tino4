"""Page content.  All numbers come from model.py; all owner figures are rounded to $10."""
from types import SimpleNamespace
import model as M
from inputs import (A, B, OFFICIAL as O, ASSUME, FIXED as F, BASE_YEAR, LAST_YEAR, PROJ_LAST,
                    INHERIT_YEARS, CENTRAL_T, CENTRAL_H, HORIZONS)
from content import SOURCES, VERIFIED_ON
from render import (ESC, table, cards, note, legend, money, mill, pct, link, srcs, badge, page,
                    line_chart, bar_chart, r10, NAV, STATUS_HELP)

V, OI, MD, AS, UV, GD = "Verified", "Owner input", "Model", "Assumption", "Unverified", "Guidance"
OPT = ["live", "rent", "sell"]
NAME = {"live": "Live in it", "rent": "Rent it out", "sell": "Sell and invest"}


def context():
    C = SimpleNamespace()
    C.T, C.H = CENTRAL_T, CENTRAL_H
    C.base = M.Scn()
    C.d = M.decide(C.T, C.H, C.base)
    C.s = C.d["state"]
    C.by = {(T, H): M.decide(T, H, M.Scn()) for T in INHERIT_YEARS for H in HORIZONS}
    C.matrix = {(h, i): M.decide(C.T, C.H, M.Scn(h, i)) for h in ("low", "base", "high") for i in ("low", "base", "high")}
    C.mix = {sh: M.decide(C.T, C.H, M.Scn(), {"stock_share": sh}) for sh in (0.0, 0.6, 1.0)}
    C.sens = [(lab, why, sid, M.decide(C.T, C.H, M.Scn(), ov)) for lab, why, sid, ov in [
        ("Rent 25% above the HUD benchmark", "The benchmark is a 40th-percentile rent; a well-kept home may earn more.", ["S36"], {"rent": 1.25}),
        ("Rent 50% above the HUD benchmark", "Upper test for rent.", ["S36"], {"rent": 1.5}),
        ("Insurance premium three times higher", "The insurance regulator says wildfire surcharges of 15% to over 300% are not in its comparison premiums.", ["S34"], {"ins": 3.0}),
        ("Upkeep twice the placeholder", "Upkeep is a placeholder until actual spending is known.", ["S09"], {"maint": 2.0}),
        ("Selling cost 4% instead of 6%", "Commissions are negotiable; the transfer tax set by state law is 0.11%.", ["S30"], {"selling_cost": 0.04}),
        ("Selling cost 8% instead of 6%", "Upper test for selling cost.", ["S30"], {"selling_cost": 0.08}),
        ("Family-home exclusion not obtained", "Home was not the parent's principal residence, or the one-year move-in or the filing deadline was missed.", ["S12"], {"no_prop19": True}),
        ("Other household income $100,000", "Lower tax brackets.", ["S02", "S26"], {"other_income_2026": 100_000}),
        ("Other household income $400,000", "Higher tax brackets.", ["S02", "S26"], {"other_income_2026": 400_000}),
    ]]
    C.be_home = M.breakeven_home(C.T, C.H)
    C.be_stock = M.breakeven_stock(C.T, C.H)
    C.be_rent = M.breakeven_rent(C.T, C.H)
    C.pa, C.pb = M.project_A(), M.project_B()
    C.pa_after = M.project_A_after(C.T)
    C.states = {T: M.a_state(T, C.base) for T in INHERIT_YEARS}
    C.estate = M.estate_table()
    C.replay = M.replay()
    C.replay20 = M.replay(H=20)
    C.fifty = M.fifty_year_path()
    C.best = C.d["best"]
    o = C.d["options"]
    ranked = sorted(OPT, key=lambda k: -o[k]["liq"])
    C.ranked = ranked
    C.margin = o[ranked[0]]["liq_real"] - o[ranked[1]]["liq_real"]
    C.wins = {k: sum(1 for r in C.replay if r["best"] == k) for k in OPT}
    C.cells = {k: sum(1 for d in C.matrix.values() if d["best"] == k) for k in OPT}
    return C


def year_ranges(ys):
    """[1977, 1996, 1997, 1998] -> '1977 and 1996-1998'."""
    ys = sorted(ys)
    if not ys:
        return "no period"
    runs, a, b = [], ys[0], ys[0]
    for y in ys[1:]:
        if y == b + 1:
            b = y
        else:
            runs.append((a, b)); a = b = y
    runs.append((a, b))
    parts = [str(a) if a == b else f"{a}-{b}" for a, b in runs]
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def real(C, x, d=None):
    return x / (d or C.d)["deflator"]


# ====================================================================== overview
def p_index(C, out):
    o, s = C.d["options"], C.s
    pa0 = C.pa[0]
    yr1 = {k: o[k]["rows"][0] for k in ("live", "rent")}
    ex27 = M.estate_exclusion(2027)
    e45 = next(r for r in C.estate if r["year"] == C.T)
    body = f"""
<div class="answer"><h2>Best plan on the numbers: keep Property B, and {NAME[C.best].lower()} when Property A is inherited</h2>
<p>In the central case (inheritance in {C.T}, results measured {C.H} years later, after all taxes, in today's dollars)
<b>{NAME[C.ranked[0]]}</b> leaves about <b>{money(o[C.ranked[0]]['liq_real'])}</b>,
{NAME[C.ranked[1]].lower()} about {money(o[C.ranked[1]]['liq_real'])} and
{NAME[C.ranked[2]].lower()} about {money(o[C.ranked[2]]['liq_real'])}.
Selling wins because the inherited home gets a new tax basis on the date of death, so a prompt sale carries little or no capital-gains tax,
while keeping it means the property tax jumps from about {money(next(r for r in C.pa if r['year'] == C.T)['ptax'])} a year to
{money(yr1['live']['ptax'])} (if the family moves in) or {money(yr1['rent']['ptax'])} (if it is rented out).
The answer flips to keeping the home only if it appreciates faster than about {pct(C.be_home)} a year after inheritance,
if a stock index fund returns less than about {pct(C.be_stock)} a year, or if the proceeds would sit in savings instead of a diversified portfolio.
<a href="pages/executive-summary.html">Read the executive summary</a> · <a href="pages/decision-analysis.html">See every number</a></p></div>
""" + cards([
        ("Property A today", money(A["value_2026"]), f"owner's estimate, Nov 2026; assessed at {money(A['assessed'][2026])}"),
        (f"Property A in {C.T}", money(s["fmv"]), f"projected at {pct(C.base.gA)} a year (range {money(A['value_2026'] * (1 + ASSUME['home_A']['low']) ** (C.T - BASE_YEAR))} to {money(A['value_2026'] * (1 + ASSUME['home_A']['high']) ** (C.T - BASE_YEAR))})"),
        ("Property tax after inheritance", f"{money(yr1['live']['ptax'])} / {money(yr1['rent']['ptax'])}", f"a year in {C.T}: living in it / renting it out, versus {money(next(r for r in C.pa if r['year'] == C.T)['ptax'])} without a transfer"),
        ("Federal estate tax-free amount", money(ex27), "per person for deaths in 2027 (official); indexed to inflation each year"),
        (f"Room for cash in {C.T}", money(e45["head1"]), f"projected tax-free amount {money(e45['excl'])} less Property A; double with a spouse's unused amount"),
        ("History test", f"{C.wins['sell']} of {len(C.replay)}", f"ten-year periods since 1977 in which selling came out ahead ({C.wins['rent']} renting, {C.wins['live']} living in)"),
    ]) + f"""
<h2>The three choices for Property A at a glance</h2>
<p>Inheritance in {C.T}; results {C.H} years later with everything cashed out and all taxes paid. Property B is kept in every case.</p>
""" + table(["Choice", "Property tax, first year", "Net cash, first year", f"After-tax wealth in {C.T + C.H - 1}", "Same, in today's dollars", "Versus best"], [
        ([NAME[k],
          money(o[k]["rows"][0]["ptax"]) if k != "sell" else "none after the sale",
          money(o[k]["rows"][0]["net"]) if k != "sell" else "proceeds invested: " + money(o[k]["proceeds"]),
          money(o[k]["liq"]), money(o[k]["liq_real"]),
          "best" if k == C.best else money(o[k]["liq_real"] - o[C.best]["liq_real"])],
         {"live": ["S12", "S15", "S16"], "rent": ["S12", "S16", "S36"], "sell": ["S04", "S30", "S49"]}[k], MD)
        for k in C.ranked], cls="num") + bar_chart(
        f"After-tax wealth from Property A, {C.H} years after a {C.T} inheritance (today's dollars)",
        [(NAME[k], o[k]["liq_real"]) for k in C.ranked],
        "Model result; assumptions are on the Methodology page. Property B's own value and rent are the same in all three and are left out.") + f"""
<h2>Why the two properties are treated differently</h2>
""" + table(["Question", "Property A (Cupertino)", "Property B (San Francisco)"], [
        (["Ownership", "Held in a family trust; expected to pass to the beneficiary between 2040 and 2050", "Already owned by the beneficiary"], ["S12"], OI),
        (["Value / assessed value today", f"{money(A['value_2026'])} / {money(A['assessed'][2026])}", f"{money(B['value_2026'])} / {money(B['assessed'][2025])} (2025 roll)"], ["S14"], OI),
        (["What inheritance does to property tax", "Reassessed to market value on the date of death, unless the child moves in within a year and claims the family-home exclusion, which shelters only part of the value", "Nothing. No change of ownership, so the low assessed value keeps rising by at most 2% a year"], ["S12", "S14"], V),
        (["Income-tax basis", "Reset to market value on the date of death, so a prompt sale has little or no taxable gain", "No reset. A sale would be taxed on the gain over the owner's own basis"], ["S04", "S07"], V),
        (["Role in the plan", "The asset to decide about: live in, rent out, or sell and reinvest", "The household's base: a place to live plus rental income, with a property tax bill near 0.14% of value. Keep"], ["S12", "S17"], MD),
    ], raw=False) + """
<h2>Sections</h2><div class="tiles">""" + "".join(
        f'<a class="tile" href="pages/{k}.html"><b>{ESC(lab)}</b><span>{ESC(desc)}</span></a>' for k, lab, desc in [
            ("executive-summary", "Executive summary", "The recommendation, the numbers behind it and what would change it."),
            ("properties", "The two properties", "Owner figures rounded to $10, checked against the official assessment rules."),
            ("decision-analysis", "Decision: live, rent or sell", "After-tax comparison, sensitivity tests and break-even points."),
            ("projections", "Year-by-year projections", "Value, assessed value, property tax, insurance, water, electricity and upkeep to 2060."),
            ("property-tax", "Property tax & assessment", "Proposition 13, Proposition 19 and what reassessment costs."),
            ("operating-costs", "Insurance, utilities, upkeep", "What official data says about premiums, water, solar and electricity."),
            ("estate-thresholds", "Cash inheritance & tax-free limits", "How much can pass before federal estate tax, year by year."),
            ("inheritance-law", "Estate & inheritance tax rules", "Federal, California and local rules, each with its source."),
            ("inheritance-process", "Step-by-step process", "What to do before, at and after the transfer, with deadlines."),
            ("black-swan-scenarios", "Black-swan scenarios", "The plan replayed through 50 years of real booms, busts and inflation."),
            ("law-watchlist", "Law changes to watch", "Enacted, pending and failed measures and what each would do."),
            ("flagged-for-review", "Flagged for Review", "Everything that could not be confirmed, with links for manual checking."),
        ]) + "</div>" + legend()
    page("index", "Inherited home and owned rental: what to do, and why",
         "Property A (a Cupertino house) will be inherited through a trust around 2040-2050. Property B (a three-unit San Francisco building) is already owned. "
         "This dashboard works out, with official sources and stated assumptions, whether to live in, rent out or sell Property A.", body, out)


# ====================================================================== executive summary
def p_exec(C, out):
    o, s = C.d["options"], C.s
    pa_T = next(r for r in C.pa if r["year"] == C.T)
    e = {r["year"]: r for r in C.estate}
    live1, rent1 = o["live"]["rows"][0], o["rent"]["rows"][0]
    mixT, mixS = C.mix[0.0]["options"], C.mix[1.0]["options"]
    body = f"""
<div class="answer"><h2>Recommendation</h2>
<ol>
<li><b>Keep Property B.</b> It is already owned, so nothing about the inheritance changes its taxes. Its property tax bill is about {money(B['tax'][2025])} a year on a building worth about {money(B['value_2026'])}, and it supplies both a home and about {money(B['rent_month'] * 12)} a year of rent. Selling it would give up that low assessed value and trigger tax on its whole gain.</li>
<li><b>When Property A is inherited, {NAME[C.best].lower()}</b> unless the family wants to live there. In the central case this leaves about {money(C.margin)} more (today's dollars, after tax, {C.H} years on) than the next-best choice, {NAME[C.ranked[1]].lower()}.</li>
<li><b>Invest the proceeds in a diversified portfolio, not in savings alone.</b> With the proceeds in Treasuries or savings only, selling ({money(mixT['sell']['liq_real'])}) falls behind renting the home out ({money(mixT['rent']['liq_real'])}).</li>
<li><b>If the family does want to live in Property A,</b> move in within one year of the death and file both claims on time. That keeps about {money(C.sens[6][3]['options']['live']['rows'][0]['ptax'] - live1['ptax'])} a year of property tax off the bill. Living there costs about {money((o[C.best]['liq_real'] - o['live']['liq_real']) / C.H)} a year in today's dollars compared with selling.</li>
</ol></div>
<h2>The numbers behind the recommendation</h2>
<p>Central case: inheritance in {C.T}, home worth {money(s['fmv'])} by then, results measured after {C.H} years with everything sold and all taxes paid.</p>
""" + table(["Measure", NAME["live"], NAME["rent"], NAME["sell"]], [
        (["Assessed value after inheritance", money(s["av_live"]), money(s["av_full"]), "not applicable"], ["S12", "S13"], MD),
        (["Property tax, first year", money(live1["ptax"]), money(rent1["ptax"]), "none after the sale"], ["S12", "S16"], MD),
        (["Income, first year", money(live1["income"]) + " (rent from the unit left in Property B)", money(rent1["income"]) + " (rent from Property A)", money(o["sell"]["proceeds"]) + " invested"], ["S36", "S44"], MD),
        (["Net cash after costs and tax, first year", money(live1["net"]), money(rent1["net"]), "reinvested returns"], ["S09", "S02"], MD),
        ([f"Tax if cashed out in {C.T + C.H - 1}", money(o["live"]["exit_tax"]), money(o["rent"]["exit_tax"]), money(o["sell"]["exit_tax"])], ["S06", "S07", "S08", "S25"], MD),
        ([f"After-tax wealth in {C.T + C.H - 1}", money(o["live"]["liq"]), money(o["rent"]["liq"]), money(o["sell"]["liq"])], ["S04", "S49"], MD),
        (["Same, in today's dollars", money(o["live"]["liq_real"]), money(o["rent"]["liq_real"]), money(o["sell"]["liq_real"])], ["S43"], MD),
    ], cls="num") + f"""
<h2>Why selling comes out ahead</h2>
<ul>
<li><b>The tax basis resets at death.</b> Inherited property takes a basis equal to its market value on the date of death, so selling soon afterwards produces little or no taxable gain. Wait ten years and the growth since the death is taxed: about {money(o['rent']['exit_tax'])} in the rental case.</li>
<li><b>Keeping the home ends its low assessment.</b> Without a transfer the {C.T} tax bill would be about {money(pa_T['ptax'])}. After inheritance it is about {money(live1['ptax'])} if the family moves in (the family-home exclusion shelters only {money(s['allow'])} of value) or {money(rent1['ptax'])} if it is rented.</li>
<li><b>The rent is small next to the value.</b> The official rent benchmark is {money(O['hud_rent_A_4br_2026'])} a month today for a home worth {money(A['value_2026'])}: about {pct(O['hud_rent_A_4br_2026'] * 12 / A['value_2026'])} a year before costs. After the reassessed property tax, insurance and upkeep, the first-year net rent is about {money(rent1['net'])}, or {pct(rent1['net'] / s['fmv'])} of the home's value.</li>
<li><b>The household already has a home.</b> Property B houses the family and pays rent, so Property A is an investment choice, not a housing need. Both properties are Bay Area real estate; selling one spreads the risk.</li>
</ul>
<h2>What would change the answer</h2>
""" + table(["Test", "Break-even", "Central assumption", "Reading"], [
        (["Home appreciation after inheritance", pct(C.be_home) + " a year", pct(C.base.gA) + " a year", "Above the break-even, keeping the home beats selling"], ["S41"], MD),
        (["Stock index fund return", pct(C.be_stock) + " a year", pct(C.base.stock) + " a year", "Below the break-even, keeping the home beats selling"], ["S49", "S48"], MD),
        (["Rent for Property A, today's dollars", money(O["hud_rent_A_4br_2026"] * C.be_rent) + " a month" if C.be_rent else "no break-even in range", money(O["hud_rent_A_4br_2026"]) + " a month", "Above the break-even, renting out beats selling"], ["S36"], MD),
        (["Where the proceeds go", "Treasuries or savings only", "60% stock index fund, 40% Treasuries", f"Savings only: selling {money(mixT['sell']['liq_real'])}, renting {money(mixT['rent']['liq_real'])}. All stocks: selling {money(mixS['sell']['liq_real'])}"], ["S51", "S49"], MD),
        (["Combinations of slow/central/fast home growth and low/central/high investment returns", f"selling best in {C.cells['sell']} of 9, renting in {C.cells['rent']}, living in {C.cells['live']}", "central / central", "Renting wins only when investments do poorly and homes do well"], ["S41", "S49"], MD),
        ([f"Replay of {len(C.replay)} real ten-year periods, 1977-2024", f"selling best in {C.wins['sell']}, renting in {C.wins['rent']}, living in {C.wins['live']}", "not applicable", "Renting won in periods that began in 1977, 1996-2000 and 2013-2014"], ["S41", "S43", "S48"], MD),
    ]) + f"""
<h2>The cash inheritance</h2>
<p>California has no estate or inheritance tax and bars cities and counties from having one. An inheritance is not income to the person who receives it.
The only tax that can apply is the federal estate tax, paid by the estate at 40% of the amount above the tax-free limit. That limit is {money(O['estate_excl'][2026])} per person for deaths in 2026 and {money(O['estate_excl'][2027])} in 2027, and is indexed to inflation afterwards.
With Property A counted at its projected value, the room left for cash and other assets is about {money(e[2040]['head1'])} in 2040, {money(e[2045]['head1'])} in 2045 and {money(e[2050]['head1'])} in 2050 for one person's limit, and about {money(e[2045]['head2'])} in 2045 if a spouse's unused limit was preserved by filing an estate tax return at the first death.
The cash amount itself was not supplied, so the dashboard shows room rather than a tax figure. Details: <a href="estate-thresholds.html">Cash inheritance &amp; tax-free limits</a>.</p>
<h2>What to do, in order</h2>
<ol>
<li><b>Now:</b> confirm the home is titled in the trust, that it is the parent's principal residence with a homeowners' exemption on file, and whether an estate tax return was or will be filed at the first parent's death to preserve the unused federal limit.</li>
<li><b>At the death:</b> get a date-of-death appraisal (it sets the new tax basis), have the trustee send the required notice within 60 days and file the change-in-ownership statement within 150 days.</li>
<li><b>Decide within months, not years:</b> sell promptly, or move in within one year and file the exemption and exclusion claims.</li>
<li><b>If selling:</b> invest the proceeds in a diversified, low-cost mix rather than leaving them in savings.</li>
</ol>
<p>Full list with deadlines and sources: <a href="inheritance-process.html">Step-by-step process</a>.</p>
<h2>What is not certain</h2>
<p>The home's value, rent, insurance, utility and upkeep figures come from the owner or from stated assumptions, not from records. Tax law for 2040-2050 is unknown; the model uses today's rules.
{len(FLAGS)} items are listed on <a href="flagged-for-review.html">Flagged for Review</a>, and the <a href="black-swan-scenarios.html">black-swan section</a> shows the plan under real historical sequences rather than steady growth.</p>
""" + legend()
    page("executive-summary", "Executive summary",
         "The recommendation, the numbers behind it, what would change it, and what to do next.", body, out)


# ====================================================================== the two properties
def _hist_rows(P, factors, rate, rate_src, tag):
    rows, yrs = [], sorted(P["assessed"])
    for y in yrs:
        av = P["assessed"][y]
        prev = P["assessed"].get(y - 1)
        chg = pct(av / prev - 1, 2) if prev else ""
        off = pct(factors[y] - 1, 2) if y in factors else ""
        tax = P["tax"].get(y)
        eff = pct(tax / av, 2) if tax else ""
        rows.append(([str(y), money(av), chg, off, money(tax), eff], ["S14", rate_src], OI))
    return rows


def p_properties(C, out):
    fa = A["tax"][2025] - A["assessed"][2025] * O["rate_A"]
    fa_ex = A["tax"][2025] - (A["assessed"][2025] - O["homeowners_exemption"]) * O["rate_A"]
    fb = B["tax"][2025] - B["assessed"][2025] * O["rate_B"]
    body = legend() + """
<h2>Side by side</h2>
""" + table(["Item", "Property A", "Property B"], [
        (["Place", "Cupertino, Santa Clara County", "San Francisco"], ["S16", "S17"], OI),
        (["Type", "Single-family home with rooftop solar", "Building with three livable units"], ["S12"], OI),
        (["Ownership", "Family trust; inheritance expected 2040-2050", "Already owned by the beneficiary"], ["S12"], OI),
        (["Owner's estimate of market value, Nov 2026", money(A["value_2026"]), money(B["value_2026"])], ["S41", "S42"], OI),
        (["Latest assessed value supplied", f"{money(A['assessed'][2026])} (2026 roll)", f"{money(B['assessed'][2025])} (2025 roll)"], ["S14"], OI),
        (["Assessed value as a share of market value", pct(A["assessed"][2026] / A["value_2026"]), pct(B["assessed"][2025] / B["value_2026"])], ["S14"], MD),
        (["Latest tax bill supplied", f"{money(A['tax'][2025])} (2025)", f"{money(B['tax'][2025])} (2025)"], ["S16", "S17"], OI),
        (["Tax bill as a share of market value", pct(A["tax"][2025] / A["value_2026"], 2), pct(B["tax"][2025] / B["value_2026"], 2)], ["S16", "S17"], MD),
        (["Rent", "none (not rented)", f"{money(B['rent_month'])} a month from two units; the third unit is not rented and the household can live in it"], ["S37"], OI),
        (["Water", f"{money(A['water_month'][0])} to {money(A['water_month'][1])} a month", f"{money(B['water_month'][0])} to {money(B['water_month'][1])} a month for all three units"], ["S45"], OI),
        (["Electricity", f"none; solar gives a net credit of about {money(-A['elec_month'][1])} to {money(-A['elec_month'][0])} a month", f"{money(B['elec_month'][0])} to {money(B['elec_month'][1])} a month"], ["S32", "S46"], OI),
        (["Insurance", f"owner's guess: about {money(A['insurance_year'])} a year", f"owner's guess: about {money(B['insurance_year'])} a year"], ["S33"], OI),
        (["Upkeep", "said to be lower than Property B; no figure supplied", "no figure supplied"], ["S09"], OI),
    ]) + f"""
<h2>Property A: assessed value and tax bills</h2>
<p>Owner figures, rounded to the nearest $10. The official factor is the yearly inflation factor published by the State Board of Equalization; a home that has not changed hands should rise by exactly that factor.</p>
""" + table(["Roll year", "Assessed value", "Change", "Official factor", "Tax bill", "Bill as share of assessed value"],
            _hist_rows(A, M.FACTORS, O["rate_A"], "S16", "A"), cls="num") + f"""
<h2>Property B: assessed value and tax bills</h2>
""" + table(["Roll year", "Assessed value", "Change", "Official factor", "Tax bill", "Bill as share of assessed value"],
            _hist_rows(B, M.FACTORS, O["rate_B"], "S17", "B"), cls="num") + f"""
<h2>What the check against official rules shows</h2>
""" + table(["Finding", "Detail"], [
        (["Assessed values follow the official factor every year",
          "Both series rise by the published factor in every year supplied, including the three years when it was below 2% (2014, 2016, 2021). That is what the rules predict for property that has not changed hands, and it supports the supplied series."], ["S14"], MD),
        (["Property A's bill is higher than rate times assessed value",
          f"The component rates for a Cupertino elementary / Fremont Union High / Foothill-De Anza area add up to {pct(O['rate_A'], 4)}. Applied to the 2025 assessed value that gives {money(A['assessed'][2025] * O['rate_A'])}; the bill was {money(A['tax'][2025])}. The gap of about {money(fa)} ({money(fa_ex)} if the homeowners' exemption is on the bill) is consistent with flat charges collected on the tax roll. The parcel's own rate area and charges were not looked up."], ["S16", "S15"], MD),
        (["Property B's bill is nearly twice rate times assessed value, and that is explained",
          f"The city-wide rate of {pct(O['rate_B'], 4)} on the 2025 assessed value gives {money(B['assessed'][2025] * O['rate_B'])}. Official flat parcel taxes for 2025-26 add $829.22 for a three-unit parcel ($334.38 + $319.34 + 3 x $21.50 + $99 + $12). That leaves about {money(fb - O['sf_parcel_taxes_2025'])} of other direct charges that were not itemised. An earlier version of this site flagged the bill as inconsistent with the official rate; the flat taxes account for most of the difference."], ["S17", "S18"], MD),
        (["Tax bills grow faster than assessed values",
          f"Property A's bill rose {pct((A['tax'][2025] / A['tax'][2015]) ** 0.1 - 1)} a year over 2015-2025 against {pct((A['assessed'][2025] / A['assessed'][2015]) ** 0.1 - 1)} for the assessed value. Property B's rose {pct((B['tax'][2025] / B['tax'][2016]) ** (1 / 9) - 1)} a year over 2016-2025 against {pct((B['assessed'][2025] / B['assessed'][2016]) ** (1 / 9) - 1)}. Flat charges and voter-approved rates are not capped at 2%."], ["S16", "S18"], MD),
        (["2026 tax bill for Property A", ""], ["S16"], UV),
        (["2026 assessed value for Property B", ""], ["S14"], UV),
    ])
    page("properties", "The two properties",
         "What the owner supplied, rounded to the nearest $10, and how it lines up with the official assessment rules. No parcel, address or account was looked up.", body, out)


# ====================================================================== decision analysis
def p_decision(C, out):
    o, s, T, H = C.d["options"], C.s, C.T, C.H
    live1, rent1 = o["live"]["rows"][0], o["rent"]["rows"][0]
    sell1 = o["sell"]["rows"][0]
    pa_T = next(r for r in C.pa if r["year"] == T)
    end = T + H - 1

    def opt_row(d, k, extra=None):
        x = d["options"][k]
        return [money(x["liq_real"])]

    body = f"""
<div class="answer"><h2>Result</h2><p><b>{NAME[C.ranked[0]]}</b> ranks first, <b>{NAME[C.ranked[1]].lower()}</b> second and
<b>{NAME[C.ranked[2]].lower()}</b> third in the central case. The lead over second place is about {money(C.margin)} in today's dollars after {H} years.
Selling is ahead in {C.cells['sell']} of 9 combinations of home growth and investment returns and in {C.wins['sell']} of {len(C.replay)} replayed historical periods.</p></div>
{legend()}
<h2>1. Where things stand on the day of inheritance</h2>
<p>Central case: inheritance on 1 January {T}. Growth before that date uses the central assumptions on the <a href="methodology.html">Methodology</a> page.</p>
""" + table(["Item", f"Value in {T}", "How it is worked out"], [
        (["Market value of Property A", money(s["fmv"]), f"{money(A['value_2026'])} today, growing {pct(C.base.gA)} a year"], ["S41"], MD),
        (["New income-tax basis", money(s["fmv"]), "Market value on the date of death"], ["S04"], MD),
        (["Parent's assessed value by then", money(s["fbyv"]), f"{money(A['assessed'][2026])} today, rising 2% a year"], ["S14"], MD),
        (["Family-home allowance", money(s["allow"]), f"$1,044,586 today, adjusted every second year by one year's change in California house prices ({M.prop19_adjustments(T)} adjustments at {pct(C.base.gA)})"], ["S13"], MD),
        (["Assessed value if the child moves in", money(s["av_live"]), "Parent's assessed value plus the part of market value above (assessed value + allowance)"], ["S12"], MD),
        (["Assessed value if the child does not move in", money(s["av_full"]), "Full market value"], ["S12"], MD),
        (["Property tax without any transfer (for comparison)", money(pa_T["ptax"]), f"Assessed value x {pct(O['rate_A'], 4)} plus flat charges"], ["S16"], MD),
        (["Rent Property A could earn", money(s["rent"] / 12) + " a month", f"HUD four-bedroom benchmark of {money(O['hud_rent_A_4br_2026'])} today, growing {pct(C.base.infl + F['spread_rent'])} a year"], ["S36", "S44"], MD),
        (["Rent from the unit the household would leave in Property B", money(s["b_unit_rent"] / 12) + " a month", f"Average of the two rented units today ({money(F['b_unit_rent_month_2026'])}), growing {pct(C.base.infl + F['spread_rent'])} a year"], ["S37", "S44"], AS),
    ]) + f"""
<h2>2. First-year cash flow under each choice</h2>
<p>In the rent and sell choices the household lives in Property B's third unit. In the live-in choice it moves to Property A and that unit can be rented.</p>
""" + table(["Line", NAME["live"], NAME["rent"], NAME["sell"]], [
        (["Rent received (after 5% vacancy)", money(live1["income"]), money(rent1["income"]), money(0)], ["S36", "S37"], MD),
        (["Property tax", money(-live1["ptax"]), money(-rent1["ptax"]), "paid only until the sale"], ["S12", "S16"], MD),
        (["Insurance", money(-live1["ins"]), money(-rent1["ins"]), money(0)], ["S33"], AS),
        (["Water", money(-live1["water"]), "paid by the tenant", money(0)], ["S45"], MD),
        (["Upkeep", money(-live1["maint"]), money(-rent1["maint"]), money(0)], ["S09"], AS),
        (["Depreciation deduction (reduces taxable rent, not cash)", "none", money(o["rent"]["depr"]), "none"], ["S10"], MD),
        (["Income tax on the rent", money(-live1["inc_tax"]), money(-rent1["inc_tax"]), money(0)], ["S02", "S26", "S08"], MD),
        (["Net cash for the year", money(live1["net"]), money(rent1["net"]), "see below"], ["S09"], MD),
        (["Sale price", "not sold", "not sold", money(s["fmv"])], ["S41"], MD),
        (["Selling costs at 6%", "none", "none", money(-o["sell"]["sale_cost"])], ["S30"], AS),
        (["Six months of carrying costs while selling", "none", "none", money(-o["sell"]["carry"])], ["S16"], AS),
        (["Capital-gains tax on the sale", "none", "none", "none: sale price does not exceed the new basis"], ["S04"], V),
        (["Amount invested", "none", "none", money(o["sell"]["proceeds"])], ["S49", "S51"], MD),
        (["Tax on first-year interest and dividends", "none", "none", money(-sell1["inc_tax"])], ["S02", "S26", "S08"], MD),
    ], cls="num") + f"""
<h2>3. Result after {H} years</h2>
<p>Each year's net cash is added to (or taken from) a side account invested the same way as the sale proceeds. In {end} everything is sold and all taxes are paid, so the three choices are compared on the same footing.</p>
""" + table(["Choice", f"Home value, {end}", f"Investments, {end}", "Selling cost if sold", "Tax on cashing out", "After-tax wealth", "In today's dollars", "Before cashing out"], [
        ([NAME[k], money(o[k]["home_end"]) if k != "sell" else "sold in " + str(T), money(o[k]["side"]),
          money(-o[k]["sale_cost"]) if k != "sell" else "paid in " + str(T), money(-o[k]["exit_tax"]),
          money(o[k]["liq"]), money(o[k]["liq_real"]), money(o[k]["hold"])],
         {"live": ["S06", "S07", "S12"], "rent": ["S07", "S09", "S10"], "sell": ["S04", "S49", "S51"]}[k], MD)
        for k in OPT] + [
        (["Live in it, unit in Property B left empty", money(o["live_empty"]["home_end"]), money(o["live_empty"]["side"]),
          money(-o["live_empty"]["sale_cost"]), money(-o["live_empty"]["exit_tax"]), money(o["live_empty"]["liq"]),
          money(o["live_empty"]["liq_real"]), money(o["live_empty"]["hold"])], ["S06", "S12"], MD)], cls="num") + f"""
<p>A negative investment figure means the choice costs money each year; it is the running total of what the household would have to pay in, with interest.
"Before cashing out" shows paper wealth if nothing is sold in {end}; on that measure the three are closer, because the tax on the home's growth and on the portfolio's growth has not yet been paid.</p>
<h2>4. Other inheritance years and a longer holding period</h2>
""" + table(["Inheritance year", "Years held", NAME["live"], NAME["rent"], NAME["sell"], "Best"], [
        ([str(t), str(h)] + [money(d["options"][k]["liq_real"]) for k in OPT] + [NAME[d["best"]]], ["S41", "S49", "S12"], MD)
        for (t, h), d in sorted(C.by.items())], caption="After-tax wealth in today's dollars", cls="num") + f"""
<h2>5. Slow, central and fast markets</h2>
<p>Home growth: {pct(ASSUME['home_A']['low'])} / {pct(ASSUME['home_A']['base'])} / {pct(ASSUME['home_A']['high'])} a year.
Investment returns: stock index fund {pct(ASSUME['stock']['low'])} / {pct(ASSUME['stock']['base'])} / {pct(ASSUME['stock']['high'])}, Treasuries {pct(ASSUME['cash']['low'])} / {pct(ASSUME['cash']['base'])} / {pct(ASSUME['cash']['high'])}.</p>
""" + table(["Home growth", "Investment returns", NAME["live"], NAME["rent"], NAME["sell"], "Best", "Lead over second"], [
        ([h, i] + [money(d["options"][k]["liq_real"]) for k in OPT] + [NAME[d["best"]],
         money(sorted((d["options"][k]["liq_real"] for k in OPT), reverse=True)[0] - sorted((d["options"][k]["liq_real"] for k in OPT), reverse=True)[1])],
         ["S41", "S49", "S51"], MD) for (h, i), d in C.matrix.items()], caption=f"Inheritance {T}, {H} years, today's dollars", cls="num") + f"""
<h2>6. Where the sale proceeds go</h2>
<p>The brief asks about the stock market, savings and similar choices. The same mix is used for the side account in the other two choices.</p>
""" + table(["Proceeds invested in", NAME["live"], NAME["rent"], NAME["sell"], "Best"], [
        ([lab] + [money(C.mix[sh]["options"][k]["liq_real"]) for k in OPT] + [NAME[C.mix[sh]["best"]]], sid, MD)
        for sh, lab, sid in [(0.0, f"Treasuries or savings only ({pct(C.base.cash)} a year, taxed yearly)", ["S51", "S50"]),
                             (0.6, f"60% stock index fund ({pct(C.base.stock)}), 40% Treasuries: central case", ["S49", "S51"]),
                             (1.0, f"Stock index fund only ({pct(C.base.stock)} a year)", ["S49", "S48"])]], cls="num") + f"""
<h2>7. One change at a time</h2>
""" + table(["Change", "Why test it", NAME["live"], NAME["rent"], NAME["sell"], "Best"], [
        ([lab, why] + [money(d["options"][k]["liq_real"]) for k in OPT] + [NAME[d["best"]]], sid, MD)
        for lab, why, sid, d in C.sens], caption="After-tax wealth in today's dollars; central case otherwise", cls="num") + f"""
<h2>8. Break-even points</h2>
""" + table(["If this is true", "then", "Central assumption"], [
        ([f"Property A appreciates more than {pct(C.be_home)} a year after inheritance", "keeping it (renting it out) beats selling", pct(C.base.gA) + " a year"], ["S41"], MD),
        ([f"A stock index fund returns less than {pct(C.be_stock)} a year", "keeping the home beats selling", pct(C.base.stock) + " a year"], ["S49", "S48"], MD),
        ([f"Property A can be rented for more than {money(O['hud_rent_A_4br_2026'] * C.be_rent)} a month in today's dollars" if C.be_rent else "No rent level in the tested range", "renting it out beats selling", money(O["hud_rent_A_4br_2026"]) + " a month"], ["S36"], MD),
        (["The family values living in Property A at more than " + money((o[C.best]["liq_real"] - o["live"]["liq_real"]) / H) + " a year in today's dollars", "living in it is worth its cost", "a personal judgement, not modelled"], ["S12"], MD),
    ]) + f"""
<h2>9. How Property B shapes the decision about Property A</h2>
""" + table(["Fact about Property B", "What it means for Property A"], [
        (["It is already owned, so the inheritance does not touch its assessed value or tax basis",
          "Keep it. Its tax bill is about " + pct(B["tax"][2025] / B["value_2026"], 2) + " of its value; Property A's would be about " + pct(rent1["ptax"] / s["fmv"], 2) + " after reassessment"], ["S12", "S14"], MD),
        (["It has had no basis reset; Property A will get one at the death",
          "If one property is ever sold, Property A is the tax-efficient one to sell and Property B the costly one"], ["S04", "S07"], V),
        (["It gives the household a home that costs no rental income",
          "Property A is not needed for housing. Only one home can be a principal residence, so moving to Property A to claim the family-home exclusion means leaving Property B's unit, which can then be rented"], ["S12", "S37"], MD),
        (["Its rent rises with the city's allowed increase, 60% of inflation, while water, insurance and upkeep rise faster",
          f"Its net income grows slowly: about {money(C.pb[0]['net'])} in 2026 and {money(next(r for r in C.pb if r['year'] == T)['net'])} in {T}, which is {money(next(r for r in C.pb if r['year'] == T)['net'] / (1 + C.base.infl) ** (T - BASE_YEAR))} in today's dollars. Proceeds from Property A invested elsewhere offset that"], ["S37", "S45"], MD),
        (["Both properties are Bay Area housing",
          "Keeping both ties the household's wealth to one regional market; selling Property A spreads it"], ["S41", "S42"], MD),
    ])
    page("decision-analysis", "Decision: live in, rent out, or sell and invest",
         "An after-tax comparison of the three choices for Property A, with Property B kept in every case. All figures are model results in dollars rounded to the nearest $10.", body, out)


# ====================================================================== projections
def p_projections(C, out):
    T = C.T
    ch = line_chart("Property A: market value (slow / central / fast) and assessed value without a transfer",
                    [("Central", [(r["year"], r["value"]) for r in C.pa]),
                     ("Slow", [(r["year"], r["value_low"]) for r in C.pa]),
                     ("Fast", [(r["year"], r["value_high"]) for r in C.pa]),
                     ("Assessed", [(r["year"], r["assessed"]) for r in C.pa])],
                    "Model projection. Home values never grow at a constant rate; see the black-swan section for a path built from real history.")
    chb = line_chart("Property B: rent received and total running costs",
                     [("Rent (rises 60% of inflation)", [(r["year"], r["rent"]) for r in C.pb]),
                      ("Costs", [(r["year"], r["rent"] - r["net"]) for r in C.pb])],
                     "Model projection: allowed rent increases are 60% of inflation, while water, insurance and upkeep rise faster.",
                     fmt=lambda v: f"${v / 1000:.0f}k")
    body = f"""{legend()}
<p>Central assumptions: prices {pct(C.base.infl)} a year; Property A {pct(C.base.gA)} and Property B {pct(C.base.gB)} a year; water {pct(C.base.infl + F['spread_water'])}; electricity {pct(C.base.infl + F['spread_elec'])}; insurance {pct(C.base.infl + F['spread_insurance'])}; upkeep with prices; assessed values 2% a year.
Where each comes from is on the <a href="methodology.html">Methodology</a> page. Every figure is a projection, not a forecast or an official value.</p>
<h2>Property A before inheritance (no change of ownership)</h2>{ch}
""" + table(["Year", "Value, slow", "Value, central", "Value, fast", "Assessed value", "Property tax", "Insurance", "Water", "Electricity (solar)", "Upkeep"], [
        ([str(r["year"]), money(r["value_low"]), money(r["value"]), money(r["value_high"]), money(r["assessed"]), money(r["ptax"]),
          money(r["ins"]), money(r["water"]), money(r["elec"]), money(r["maint"])], ["S41", "S14", "S16", "S45"], MD) for r in C.pa], cls="num") + f"""
<p>Electricity is blank from {F['solar_legacy_latest_end']}: the legacy solar tariff lasts 20 years from the connection date, and the last date any home could join it was April 2023, so it will have ended by then. The bill after that depends on usage and equipment and was not estimated (see <a href="flagged-for-review.html">Flagged for Review</a>).
The property tax column includes flat charges of about {money(A['tax'][2025] - A['assessed'][2025] * O['rate_A'])} a year in 2025, grown with prices.</p>
<h2>Property A after inheritance in {T}</h2>
<p>The same year, three ways: no transfer (for comparison only), the child moves in and claims the family-home exclusion, or the home is rented or held without moving in.</p>
""" + table(["Year", "Market value", "Assessed, no transfer", "Tax, no transfer", "Assessed, child moves in", "Tax, child moves in", "Assessed, rented or held", "Tax, rented or held"], [
        ([str(r["year"]), money(r["value"]), money(r["av_none"]), money(r["tax_none"]), money(r["av_live"]), money(r["tax_live"]),
          money(r["av_full"]), money(r["tax_full"])], ["S12", "S13", "S14", "S16"], MD) for r in C.pa_after], cls="num") + f"""
<h2>Property B (already owned; no change of ownership)</h2>{chb}
""" + table(["Year", "Value, slow", "Value, central", "Value, fast", "Assessed value", "Property tax", "Insurance", "Water", "Electricity", "Upkeep", "Rent received", "Net income"], [
        ([str(r["year"]), money(r["value_low"]), money(r["value"]), money(r["value_high"]), money(r["assessed"]), money(r["ptax"]),
          money(r["ins"]), money(r["water"]), money(r["elec"]), money(r["maint"]), money(r["rent"]), money(r["net"])],
         ["S42", "S14", "S17", "S18", "S37"], MD) for r in C.pb], cls="num") + f"""
<p>Property B's tax includes flat parcel taxes and charges of about {money(B['tax'][2025] - B['assessed'][2025] * O['rate_B'])} a year in 2025 grown with prices, plus the new transit parcel tax at its $129 minimum from 2027 to 2041 (the amount for a three-unit parcel was not confirmed).
Rent assumes the two tenancies continue under the city's rent rules; if a unit turns over, the rent can be reset to the market.</p>
"""
    page("projections", "Year-by-year projections",
         "Market value, assessed value, property tax, insurance, water, electricity and upkeep for both properties, 2026-2060.", body, out)


# ====================================================================== property tax
def p_ptax(C, out):
    rows_T = []
    for T in INHERIT_YEARS:
        s = C.states[T]
        t_none = s["fbyv"] * O["rate_A"] + s["fixed"]
        t_live = (s["av_live"] - O["homeowners_exemption"]) * O["rate_A"] + s["fixed"]
        t_full = s["av_full"] * O["rate_A"] + s["fixed"]
        rows_T.append(([str(T), money(s["fmv"]), money(s["fbyv"]), money(s["allow"]), money(s["av_live"]), money(t_live),
                        money(s["av_full"]), money(t_full), money(t_full - t_live), money(t_none)], ["S12", "S13", "S14", "S16"], MD))
    body = f"""{legend()}
<h2>The rules</h2>
""" + table(["Rule", "What it says"], [
        (["Yearly cap on assessed value (Proposition 13)", "A property's base year value rises each year by an inflation factor of no more than 2%. The factor for the 2026 roll is 1.02."], ["S14"], V),
        (["Tax rate, Santa Clara County", "1% of assessed value plus voter-approved debt rates that differ by tax rate area. The county had 816 tax rate areas in 2025-26."], ["S16"], V),
        (["Rate used for Property A", "1.1636%: the 2025-26 component rates for the county, county library, Cupertino elementary bonds, Fremont Union High bonds, Foothill-De Anza bonds, the open space district and the water district's State Water Project levy. A calculation from official components, not a rate printed for the parcel."], ["S16"], MD),
        (["Property A's own tax rate area and its 2026-27 rates", ""], ["S16"], UV),
        (["Tax rate, San Francisco", "1.18162182% of assessed value for fiscal year 2026-27, one rate city-wide."], ["S17"], V),
        (["Flat parcel taxes, San Francisco, 2025-26", "$334.38 and $319.34 for the school district, $21.50 per dwelling unit on multi-family parcels, $99 for City College and $12 for bay restoration; adjusted for inflation each year."], ["S18"], V),
        (["What a death does", "A transfer on death, including through a trust, is a change of ownership. The assessor reappraises to market value and issues supplemental bills, unless an exclusion applies."], ["S12", "S16", "S17"], V),
        (["Family-home exclusion (Proposition 19)", "Applies only to a home that was the parent's principal residence and becomes the child's principal residence within one year. The Board of Equalization states there are no exceptions to the one-year rule."], ["S12"], V),
        (["How much the exclusion shelters", "If market value is above the parent's assessed value plus the allowance, the excess is added to the parent's assessed value. The result then rises by the yearly factor."], ["S12"], V),
        (["Allowance", "$1,044,586 for transfers from 16 February 2025 through 15 February 2027 (earlier: $1,022,600, and $1,000,000)."], ["S13"], V),
        (["How the allowance changes", "Every second 16 February it is adjusted by the change in the FHFA California house price index for the single prior calendar year. Next adjustment: February 2027."], ["S13"], V),
        (["Allowance from 16 February 2027", ""], ["S13"], UV),
        (["Claims and deadlines", "Homeowners' exemption claim within one year of the transfer; exclusion claim within three years or before a sale to a third party, whichever is earlier (or within six months of a supplemental or escape assessment notice). Later claims give relief only going forward."], ["S12"], V),
        (["Moving out later", "The exclusion is removed. The value enrolled is the market value on the date of the transfer, raised by the yearly factors since then, unless another eligible child moves in within a year."], ["S12"], V),
        (["Parent in a care facility", "The home still counts as the parent's principal residence if the parent would live there, intends to return, and it is not rented to anyone other than an immediate family member."], ["S12"], V),
        (["Two homes, one child", "Only one home can be the child's principal residence, so only one can qualify."], ["S12"], V),
        (["Multi-unit buildings", "Only the unit the parent lived in can qualify; the rest is reassessed."], ["S12"], V),
        (["Homeowners' exemption", "$7,000 off the taxable value of an owner-occupied principal residence; one-time claim on form BOE-266."], ["S15"], V),
        (["Wildfire-area extension", "SB 293 (Chapter 539, Statutes of 2025) amended the family-transfer sections; the Board's letter describes longer claim periods for the 2025 Los Angeles and Ventura County fire areas. Not relevant to either property."], ["S31", "S12"], V),
    ]) + f"""
<h2>What inheritance does to Property A's assessed value</h2>
<p>Property B is not affected: it does not change hands. For Property A, the table shows the first year after inheritance under central assumptions.</p>
""" + table(["Inheritance year", "Market value", "Parent's assessed value", "Allowance", "Assessed, child moves in", "Tax, child moves in", "Assessed, not moved in", "Tax, not moved in", "Yearly saving from moving in", "Tax if no transfer"], rows_T, cls="num") + f"""
<p>The exclusion protects only the allowance. In {C.T} that is about {money(C.s['allow'])} of a {money(C.s['fmv'])} home, so even with the exclusion the tax bill is about {pct(((C.s['av_live'] - 7000) * O['rate_A'] + C.s['fixed']) / (C.s['fbyv'] * O['rate_A'] + C.s['fixed']) - 1, 0)} higher than the parent's.</p>
<h2>Santa Clara County component rates used for Property A (2025-26, per $100 of value)</h2>
""" + table(["Component", "Rate"], [
        (["1% maximum levy", "1.00000"], ["S16"], V), (["County retirement levy", "0.03880"], ["S16"], V),
        (["County housing bond 2016", "0.00560"], ["S16"], V), (["Valley Medical Center 2008", "0.00520"], ["S16"], V),
        (["County library retirement levy", "0.00240"], ["S16"], V), (["Water district, State Water Project (land and improvements)", "0.00390"], ["S16"], V),
        (["Mid-Peninsula open space 2014", "0.00140"], ["S16"], V),
        (["Cupertino elementary bonds (2001, 2012, 2024)", "0.01650 + 0.01690 + 0.00010"], ["S16"], V),
        (["Fremont Union High bonds (2008, 2014, 2018, 2022)", "0.00880 + 0.01070 + 0.01180 + 0.01040"], ["S16"], V),
        (["Foothill-De Anza bonds (1999, 2006, 2020)", "0.00750 + 0.01010 + 0.01350"], ["S16"], V),
        (["Total used in the model", "1.16360"], ["S16"], MD),
    ], cls="num")
    page("property-tax", "Property tax & assessment",
         "The official rules, and what they do to each property. Property A faces reassessment at inheritance; Property B does not.", body, out)


# ====================================================================== operating costs
def p_costs(C, out):
    c = M.cagr
    body = f"""{legend()}
<h2>Insurance</h2>
<p>The owner's guess is about {money(A['insurance_year'])} a year for each property. The official statewide average supports that order of size for an owner-occupied home, but no official premium for either property's area or for a rental building could be read, so those rows are blank.</p>
""" + table(["Item", "Finding"], [
        (["Average homeowner premium, California", "$1,571 a year (national: $1,512), on the insurance regulator's page updated 27 October 2026"], ["S33"], V),
        (["Owner's guess, Property A (primary-residence policy)", f"about {money(A['insurance_year'])} a year"], ["S33"], OI),
        (["Owner's guess, Property B (rental-property policy)", f"about {money(B['insurance_year'])} a year"], ["S33"], OI),
        (["Premium for a home like Property A in its ZIP code area", ""], ["S34"], UV),
        (["Premium for a tenant-occupied three-unit building in Property B's area", ""], ["S34"], UV),
        (["Why those two rows are blank", "The regulator's 2026 comparison tool gives insurer premiums for sample homes by ZIP code, but it is an interactive form that could not be operated here, and it covers homeowners, condominium, renters and earthquake policies only, not landlord policies."], ["S34"], V),
        (["What the comparison tool leaves out", "Wildfire surcharges of 15% to over 300%, which the regulator says are not reflected in its premiums."], ["S34"], V),
        (["Direction of rates", "In 2025 one large insurer asked for 22% more on homeowners and 38% more on rental dwellings; a 17% interim increase on the homeowners line was approved."], ["S35"], V),
        (["What counts as residential in the regulator's data", "Policies on residences of four units or fewer, including dwelling-fire and landlord policies."], ["S33"], V),
        (["Used in the model", f"The owner's {money(A['insurance_year'])} for each property in 2026, rising {pct(C.base.infl + F['spread_insurance'])} a year; a test at three times the premium is on the Decision page"], ["S33", "S35"], AS),
    ]) + f"""
<p><b>Reading:</b> the guess of {money(A['insurance_year'])} is within a few percent of the statewide average for owner-occupied homes. That average covers homes of every value, so it is a floor rather than an estimate for a home valued at {money(A['value_2026'])}, and a three-unit rental needs a landlord policy, which is priced separately. Both guesses should be replaced with written quotes. In the model, tripling Property A's premium lowers the ten-year result of renting it out by about {money(C.d['options']['rent']['liq_real'] - C.sens[2][3]['options']['rent']['liq_real'])} in today's dollars and does not change the ranking.</p>
<h2>Water</h2>
""" + table(["Item", "Finding"], [
        (["Property A, owner's bills", f"{money(A['water_month'][0])} to {money(A['water_month'][1])} a month; the model uses {money(M.mid(A['water_month']) * 12)} a year"], ["S45"], OI),
        (["Property B, owner's bills (all three units)", f"{money(B['water_month'][0])} to {money(B['water_month'][1])} a month; the model uses {money(M.mid(B['water_month']) * 12)} a year"], ["S45"], OI),
        (["National price trend for water, sewer and trash service", f"{pct(c('water_cpi', 1998, 2024))} a year over 1998-2024; {pct(c('water_cpi', 2004, 2024))} over 2004-2024; {pct(c('water_cpi', 2014, 2024))} over 2014-2024"], ["S45"], V),
        (["San Francisco water and sewer rate increases adopted for 2026 and 2027", ""], ["S52"], UV),
        (["Water tariff of the utility serving Property A", ""], ["S45"], UV),
        (["Used in the model", f"Owner's bills rising {pct(C.base.infl + F['spread_water'])} a year"], ["S45"], AS),
    ]) + f"""
<h2>Electricity and solar</h2>
""" + table(["Item", "Finding"], [
        (["Property A, owner's bills", f"No electricity cost; a net credit of about {money(-A['elec_month'][1])} to {money(-A['elec_month'][0])} a month from rooftop solar"], ["S32"], OI),
        (["Property B, owner's bills", f"{money(B['elec_month'][0])} to {money(B['elec_month'][1])} a month; the model uses {money(M.mid(B['elec_month']) * 12)} a year"], ["S46"], OI),
        (["How long a legacy solar tariff lasts", "20 years from the date the system was connected. The tariffs are closed to new customers; since 15 April 2023 new systems go on net billing."], ["S32"], V),
        (["What changes after that", "Under net billing, exported power is credited at a value that is usually below the retail rate. Yearly surplus is paid at about $0.02 to $0.03 per kWh."], ["S32"], V),
        (["Property A's connection date, and the year its legacy tariff ends", ""], ["S32"], UV),
        (["Property A's electricity bill after the legacy tariff ends", ""], ["S32"], UV),
        (["National price trend for electricity", f"{pct(c('elec_cpi', 1995, 2024))} a year over 1995-2024; {pct(c('elec_cpi', 2004, 2024))} over 2004-2024; {pct(c('elec_cpi', 2014, 2024))} over 2014-2024"], ["S46"], V),
        (["Used in the model", f"Property A: the current credit held flat until {F['solar_legacy_latest_end'] - 1}, then blank. Property B: owner's bills rising {pct(C.base.infl + F['spread_elec'])} a year"], ["S32", "S46"], AS),
    ]) + f"""
<p><b>Reading:</b> whatever the connection date, the legacy tariff will have ended by April 2043, before or soon after the inheritance window. Anyone living in Property A after that should expect an ordinary electricity bill unless the solar equipment is renewed. Each $100 a month of electricity cost lowers the live-in result by about {money(1200)} a year.</p>
<h2>Upkeep</h2>
""" + table(["Item", "Finding"], [
        (["Property A, actual repair and maintenance spending", ""], ["S09"], UV),
        (["Property B, actual repair and maintenance spending", ""], ["S09"], UV),
        (["Tax treatment", "For a rental, repairs and operating expenses are deductible and the building is depreciated; for a home the family lives in they are not."], ["S09", "S10"], V),
        (["Used in the model", f"Placeholders of {money(F['maint_A_2026'])} a year for Property A and {money(F['maint_B_2026'])} for Property B in 2026 (the owner says Property A costs less), rising with prices. Doubling Property A's figure does not change the ranking"], ["S09"], AS),
    ]) + f"""
<h2>Official price trends used for the projections</h2>
""" + table(["Series", "Last 10 years", "Last 20 years", "Last 30 years or full series", "Used as"], [
        (["Consumer prices (December to December)", pct(c("cpi_dec", 2015, 2025)), pct(c("cpi_dec", 2005, 2025)), pct(c("cpi_dec", 1995, 2025)) + " (1995-2025)", "inflation: " + pct(C.base.infl)], ["S43", "S50"], V),
        (["House prices, San Jose metro", pct(c("hpi_sj", 2015, 2025)), pct(c("hpi_sj", 2005, 2025)), pct(c("hpi_sj", 1995, 2025)) + " (1995-2025)", "Property A: " + pct(C.base.gA)], ["S41"], V),
        (["House prices, San Francisco metro division", pct(c("hpi_sf", 2015, 2025)), pct(c("hpi_sf", 2005, 2025)), pct(c("hpi_sf", 1995, 2025)) + " (1995-2025)", "Property B: " + pct(C.base.gB)], ["S42"], V),
        (["Rents, San Francisco area", pct(c("rent_sf", 2014, 2024)), pct(c("rent_sf", 2004, 2024)), pct(c("rent_sf", 1994, 2024)) + " (1994-2024)", "market rent: " + pct(C.base.infl + F["spread_rent"])], ["S44"], V),
        (["Water, sewer and trash", pct(c("water_cpi", 2014, 2024)), pct(c("water_cpi", 2004, 2024)), pct(c("water_cpi", 1998, 2024)) + " (1998-2024)", "water: " + pct(C.base.infl + F["spread_water"])], ["S45"], V),
        (["Electricity", pct(c("elec_cpi", 2014, 2024)), pct(c("elec_cpi", 2004, 2024)), pct(c("elec_cpi", 1995, 2024)) + " (1995-2024)", "electricity: " + pct(C.base.infl + F["spread_elec"])], ["S46"], V),
    ], cls="num")
    page("operating-costs", "Insurance, utilities and upkeep",
         "What official sources say about each running cost, what the owner supplied, and what remains unconfirmed.", body, out)


# ====================================================================== cash inheritance & thresholds
def p_estate(C, out):
    e = {r["year"]: r for r in C.estate}
    eT = e[C.T]
    ex = eT["excl"]
    ch = line_chart("Federal tax-free amount (one person) and Property A's projected value",
                    [("Tax-free amount", [(r["year"], r["excl"]) for r in C.estate]),
                     ("Property A, central", [(r["year"], r["home"]) for r in C.estate]),
                     ("Property A, fast", [(r["year"], r["home_high"]) for r in C.estate])],
                    "2026 and 2027 tax-free amounts are official; later years are projected with inflation.")
    cash_rows = []
    for cash in (5_000_000, 10_000_000, 15_000_000, 20_000_000, 30_000_000, 40_000_000):
        tot = cash + eT["home"]
        cash_rows.append(([money(cash), money(tot), money(M.estate_tax(tot, ex)), money(max(0, tot - M.estate_tax(tot, ex))),
                           money(M.estate_tax(tot, 2 * ex))], ["S55", "S01", "S02"], MD))
    half = ex / 2
    body = f"""{legend()}
<div class="answer"><h2>Short answer</h2>
<p><b>Local and state:</b> nothing. California has no estate tax and its law bars the state, counties and cities from taxing gifts, inheritances or estates. The cash is not income to the person who inherits it.<br>
<b>Federal:</b> the estate pays 40% on what exceeds the tax-free amount: {money(O['estate_excl'][2026])} per person for deaths in 2026 and {money(O['estate_excl'][2027])} in 2027, indexed to inflation after that.
The house counts toward that amount at its market value. In {C.T}, with Property A at {money(eT['home'])}, about {money(eT['head1'])} of cash and other assets could pass under one person's limit, or about {money(eT['head2'])} if a spouse's unused limit was preserved.</p></div>
""" + cards([
        ("Tax-free amount, 2026", money(O["estate_excl"][2026]), "per person; official"),
        ("Tax-free amount, 2027", money(O["estate_excl"][2027]), "per person; official, released 5 Nov 2026"),
        (f"Projected for {C.T}", money(ex), f"at {pct(C.base.infl - F['chained_gap'])} a year indexing; range {money(eT['excl_low'])} to {money(eT['excl_high'])}"),
        ("Rate above the limit", "40%", "federal; California and local: none"),
    ]) + ch + f"""
<h2>Room for cash and other assets, year by year</h2>
<p>"Room" is the tax-free amount minus Property A's projected value: how much cash and other property the same estate could hold before any federal estate tax. The amount of cash was not supplied, so no tax figure is shown for the family's own case.</p>
""" + table(["Year of death", "Tax-free amount, one person", "Property A, central", "Room, one person's amount", "Room with a spouse's unused amount", "Room if Property A grows fast"], [
        ([str(r["year"]), money(r["excl"]), money(r["home"]), money(r["head1"]), money(r["head2"]), money(r["head1_high_home"])],
         ["S01", "S02", "S41"], V if False else MD) for r in C.estate], cls="num") + f"""
<p>The first two rows use the official amounts. Later amounts are projected: the law indexes the amount to a chained price index, assumed here to rise {pct(C.base.infl - F['chained_gap'])} a year, and rounds it to the nearest $10,000.</p>
<h2>If the estate is larger than the limit</h2>
<p>Illustration for a death in {C.T} under today's law, with Property A at {money(eT['home'])} and a tax-free amount of {money(ex)}. The estate, not the heir, pays the tax.</p>
""" + table(["Cash and other assets", "Total estate with Property A", "Federal estate tax, one person's amount", "Left after tax", "Tax if a spouse's unused amount is added"], cash_rows, cls="num") + f"""
<h2>The rules behind the numbers</h2>
""" + table(["Question", "Answer"], [
        (["What counts toward the limit?", "Everything the person owns at death at fair market value: cash, securities, real estate, insurance, trusts and other assets. Property A is counted at its market value on the date of death, not its assessed value."], ["S01"], V),
        (["Is the limit per heir or per estate?", "Per person who dies. It is not multiplied by the number of heirs. Taxable gifts made during life count against the same amount."], ["S01", "S55"], V),
        (["Two parents", "A surviving spouse can use the first spouse's unused amount, but only if an estate tax return (Form 706) was filed for the first spouse. A simplified late election is available up to five years after that death when no return was otherwise required."], ["S01", "S03"], V),
        (["When is an estate tax return due?", "Nine months after the death; an automatic six-month extension is available. It is required when the gross estate plus taxable gifts exceeds the filing threshold for that year."], ["S03"], V),
        (["Rate", "The schedule rises to 40% on amounts over $1,000,000; the credit that goes with the tax-free amount removes the tax below it, so the excess is taxed at 40%."], ["S55"], V),
        (["California estate tax", "None. No California estate tax return for deaths on or after 1 January 2005."], ["S22"], V),
        (["California or local inheritance or gift tax", "Prohibited by statute for the state and every political subdivision."], ["S23"], V),
        (["Is inherited cash income?", "No. Do not include an inheritance in income; interest, dividends, rent or gains it later produces are taxable."], ["S24"], V),
        (["Giving during life", "The first $19,000 per recipient in 2026 and $20,000 in 2027 is not a taxable gift. Giving the house itself during life is a gift that the giver reports on Form 709."], ["S05", "S02", "S56"], V),
        (["Does a lifetime gift of the house keep the basis reset?", ""], ["S56"], UV),
        (["Cash held in retirement accounts", ""], ["S24"], UV),
        (["The actual amount of cash to be inherited", ""], ["S01"], UV),
    ]) + f"""
<h2>If the law changes</h2>
<p>The limit has moved by law before: the official table shows $5,490,000 in 2017, $11,180,000 in 2018 and $15,000,000 in 2026. The rows below are what-if calculations, not predictions.</p>
""" + table(["What-if for a death in " + str(C.T), "Tax-free amount", "Room for cash after Property A", "Estate tax on Property A plus $10,000,000 of cash"], [
        (["Today's law, indexed", money(ex), money(ex - eT["home"]), money(M.estate_tax(eT["home"] + 10_000_000, ex))], ["S01", "S02"], MD),
        (["Limit cut in half by a future Congress", money(half), money(half - eT["home"]), money(M.estate_tax(eT["home"] + 10_000_000, half))], ["S01"], MD),
        (["Estate tax repealed (as H.R.1301 proposes; introduced, no action)", "no limit", "unlimited", money(0)], ["S39"], MD),
        (["Today's law plus a spouse's unused amount", money(2 * ex), money(2 * ex - eT["home"]), money(M.estate_tax(eT["home"] + 10_000_000, 2 * ex))], ["S01", "S03"], MD),
    ], cls="num")
    page("estate-thresholds", "Cash inheritance & tax-free limits",
         "How much can be inherited before tax at the local, state and federal level, how much room is left once the house is counted, and how that room is projected to change.", body, out)


# ====================================================================== rules
def p_law(C, out):
    body = legend() + """
<h2>Federal</h2>
""" + table(["Topic", "Rule"], [
        (["Estate tax: tax-free amount", "$15,000,000 per person for 2026 (set by Public Law 119-21, signed 4 July 2025); $15,480,000 for 2027 after the yearly inflation adjustment."], ["S57", "S01", "S02"], V),
        (["Estate tax: rate", "Up to 40% on the amount above the tax-free amount."], ["S55"], V),
        (["Estate tax: who files and when", "The estate files Form 706 within nine months (six-month automatic extension) when the gross estate plus taxable gifts exceeds the threshold, or to pass a spouse's unused amount to the survivor."], ["S03"], V),
        (["Estate tax: unused amount of the first spouse", "Available to the surviving spouse only if elected on a timely estate tax return; simplified late relief up to the fifth anniversary of the death."], ["S01", "S03"], V),
        (["Gift tax: yearly exclusion", "$19,000 per recipient for 2025 and 2026; $20,000 for 2027."], ["S05", "S02"], V),
        (["Income tax: basis of inherited property", "Generally the fair market value on the date of death (or the alternate valuation date if elected on an estate tax return). Gain is taxable only above that basis."], ["S04"], V),
        (["Income tax: sale of inherited property", "Reported on Schedule D and Form 8949. If the estate had to file an estate tax return, the heir's basis must match the value reported there."], ["S04"], V),
        (["Income tax: long-term gain rates", "0%, 15% or 20% depending on income; 2027 thresholds for a joint return are $102,100 and $633,600. Depreciation previously claimed on a rental building is taxed at up to 25%."], ["S07", "S02"], V),
        (["Income tax: net investment income tax", "3.8% on investment income (interest, dividends, rent, gains) when income exceeds $250,000 on a joint return or $200,000 single. Home-sale gain that is excluded is not subject to it."], ["S08"], V),
        (["Income tax: selling a home you live in", "Up to $250,000 of gain ($500,000 on a joint return) is excluded if you owned and lived in the home for 24 months of the five years before the sale."], ["S06"], V),
        (["Income tax: renting", "Rent is taxable; property tax, insurance, repairs and depreciation are deductible. Residential buildings are depreciated over 27.5 years; land is not depreciated."], ["S09", "S10"], V),
        (["Income tax: the trust after the death", "The trust or estate needs its own tax ID number and files Form 1041 for any year with more than $600 of gross income."], ["S11"], V),
        (["Income tax: 2027 rates for a joint return", "10% to $25,600; 12% to $104,050; 22% to $218,250; 24% to $416,650; 32% to $529,100; 35% to $793,650; 37% above."], ["S02"], V),
    ]) + """
<h2>California</h2>
""" + table(["Topic", "Rule"], [
        (["Estate tax", "None for deaths on or after 1 January 2005."], ["S22"], V),
        (["Inheritance and gift tax", "The state may not impose a gift, inheritance, succession, legacy or estate tax."], ["S23"], V),
        (["Is an inheritance income?", "No. Income it later produces is taxable."], ["S24"], V),
        (["Capital gains", "No lower rate; taxed as ordinary income at rates from 1% to 12.3% under the 2025 schedules."], ["S25", "S26"], V),
        (["Basis rules", "California applies the federal rules on gain or loss on the disposition of property, which include the date-of-death basis rule, except as otherwise provided. The exceptions were not searched one by one."], ["S27"], V),
        (["Property tax on inherited real estate", "See Property tax & assessment: reassessment at death unless the family-home exclusion applies."], ["S12"], V),
    ]) + """
<h2>Local (county and city)</h2>
""" + table(["Topic", "Rule"], [
        (["Local inheritance, estate or gift tax", "Not allowed. The statutory bar covers the state and any political subdivision of the state."], ["S23"], V),
        (["Transfer tax on the inheritance itself", ""], ["S30"], UV),
        (["Transfer tax when a property is sold", "State law lets a county charge $0.55 per $500 of sale price, with a city able to take half of it. The local ordinances for Property A's city and county were not read."], ["S30"], V),
        (["San Francisco flat parcel taxes and the new transit parcel tax", "See Property tax & assessment and Law changes to watch."], ["S18", "S38"], V),
    ])
    page("inheritance-law", "Estate & inheritance tax rules",
         "Federal, California and local rules that apply to the inheritance, each read on the official page linked in its row.", body, out)


# ====================================================================== process
def p_process(C, out):
    body = legend() + note("Placeholders: [TRUSTEE] is the successor trustee named in the trust; [BENEFICIARY] is the child who inherits; [ADVISOR] is the family's estate attorney or tax professional. No real names are used anywhere on this site.") + """
<h2>Before the transfer (now to 2040)</h2>
""" + table(["Step", "What to do", "Why it matters"], [
        (["1", "Confirm Property A is titled in the trust and that the trust names [BENEFICIARY] and a successor [TRUSTEE].", "A transfer through a trust is treated like any other transfer at death for property tax; the date of death is the date that counts."], ["S12"], V),
        (["2", "Confirm Property A is the parent's principal residence and that a homeowners' exemption is on file.", "The family-home exclusion applies only to the parent's principal residence. If the exemption is not in the parent's name, the assessor may ask for proof of residence."], ["S12", "S15"], V),
        (["3", "If one parent dies first, ask [ADVISOR] about filing Form 706 for that parent even if no tax is due.", "It is the only way to pass that parent's unused federal tax-free amount to the survivor."], ["S01", "S03"], V),
        (["4", "If a parent moves to a care facility, do not rent Property A to anyone outside the immediate family.", "The home keeps its principal-residence status only if it is not rented to others and the parent intends to return."], ["S12"], V),
        (["5", "Do not transfer Property A during the parent's lifetime without advice.", "A lifetime transfer is a gift, not an inheritance; the basis reset on the date of death applies to inherited property."], ["S56", "S04"], V),
        (["6", "Keep records: solar connection date and agreement, insurance policy, major repairs, a recent estimate of value.", "The solar tariff's end date and the insurance cost are two of the blanks on Flagged for Review."], ["S32", "S34"], GD),
        (["7", "Decide in advance who would live in Property A, if anyone.", "The one-year move-in rule has no exceptions."], ["S12"], V),
    ]) + """
<h2>After the death</h2>
""" + table(["Step", "Deadline", "What to do"], [
        (["8", "Right away", "[TRUSTEE] secures the home, keeps it insured, and obtains certified death certificates."], ["S28"], GD),
        (["9", "Within 60 days", "[TRUSTEE] serves the written notification to every beneficiary and heir that the trust has become irrevocable."], ["S28"], V),
        (["10", "Promptly", "Order a written appraisal of Property A as of the date of death. That value is the new income-tax basis and the starting point for any reassessment."], ["S04", "S12"], V),
        (["11", "Promptly", "Get a tax ID number for the trust; file Form 1041 for any year in which the trust has more than $600 of gross income. The parent's final personal return is separate."], ["S11"], V),
        (["12", "Within 150 days", "[TRUSTEE] or [BENEFICIARY] files the change in ownership statement with the county assessor or recorder."], ["S29"], V),
        (["13", "Within 9 months", "If the estate exceeds the federal threshold for that year, or a spouse survives and the unused amount should be preserved, file Form 706 (six-month extension available)."], ["S03"], V),
        (["14", "Within months", "Choose: sell, rent out or move in. The comparison is on the Decision page; the property tax bill is higher from the date of death in every case."], ["S12", "S16"], GD),
    ]) + """
<h2>If the choice is to sell (the recommended path)</h2>
""" + table(["Step", "What to do"], [
        (["15a", "List and sell. Expect supplemental property tax bills for the period between the death and the sale."], ["S16"], V),
        (["15b", "Report the sale on Schedule D and Form 8949 using the date-of-death value as basis. With a prompt sale the taxable gain is small or nil."], ["S04"], V),
        (["15c", "Expect a documentary transfer tax of $0.55 per $500 of price under state law, plus negotiated commissions and closing costs."], ["S30"], V),
        (["15d", "Invest the proceeds in a diversified mix. Interest and dividends are taxed each year; the 3.8% net investment income tax applies above $250,000 of joint income."], ["S08", "S49"], V),
    ]) + """
<h2>If the choice is to move in</h2>
""" + table(["Step", "Deadline", "What to do"], [
        (["16a", "Within 1 year of the death", "[BENEFICIARY] makes Property A the principal residence. There are no exceptions to this deadline."], ["S12"], V),
        (["16b", "Within 1 year of the death", "File the homeowners' exemption claim (form BOE-266) with the county assessor."], ["S12", "S15"], V),
        (["16c", "Within 3 years, or before any sale", "File the family-home exclusion claim. A claim is also timely within six months of a supplemental or escape assessment notice."], ["S12"], V),
        (["16d", "Ongoing", "Tell the assessor if the home stops being the principal residence. The exclusion ends and the date-of-death market value, with yearly factors, is enrolled."], ["S12"], V),
        (["16e", "After 2 years", "A later sale can exclude up to $250,000 of gain ($500,000 on a joint return) that built up after the inheritance."], ["S06"], V),
        (["16f", "Any time", "The unit left in Property B can be rented; the first rent for a new tenant is not limited, later increases are."], ["S37"], V),
    ]) + """
<h2>If the choice is to rent it out</h2>
""" + table(["Step", "What to do"], [
        (["17a", "Expect reassessment to full market value; the family-home exclusion does not apply to a home the child does not live in."], ["S12"], V),
        (["17b", "Report rent and expenses on Schedule E; depreciate the building portion of the date-of-death value over 27.5 years."], ["S09", "S10"], V),
        (["17c", "Replace the homeowner policy with a landlord policy and get written quotes."], ["S34"], GD),
        (["17d", "On a later sale, depreciation claimed is taxed at up to 25% and the rest of the gain at capital-gain rates, plus California tax at ordinary rates."], ["S07", "S25"], V),
    ])
    page("inheritance-process", "Step-by-step inheritance process",
         "What to do before the transfer, in the months after the death, and on each of the three paths, with the official deadline for each step.", body, out)


# ====================================================================== black swan
def p_swan(C, out):
    T, H = C.T, C.H
    dT = (1 + C.base.infl) ** (T - BASE_YEAR)          # to today's dollars
    rp = C.replay
    best_row = {k: max(rp, key=lambda r: r[k]) for k in OPT}
    worst_row = {k: min(rp, key=lambda r: r[k]) for k in OPT}
    med = {k: sorted(r[k] for r in rp)[len(rp) // 2] for k in OPT}
    o = C.d["options"]
    episodes = [
        (1977, "High inflation: prices rose as much as 13% in a single year and homes and rents rose with them"),
        (1990, "California housing slump of the early 1990s alongside a strong stock market"),
        (2000, "Two stock-market crashes in one decade (2000-2002 and 2008)"),
        (2006, "Housing bust: home prices fell for several years after the 2006 peak"),
        (2013, "Housing boom, then the 2021-2022 inflation shock and a stock fall"),
    ]
    ep_rows = []
    for st, desc in episodes:
        r = next(x for x in rp if x["start"] == st)
        ep_rows.append(([f"{r['start']}-{r['end']}", desc, pct(r["worst_home"]), pct(r["worst_stock"]), pct(r["max_cpi"]),
                         money(r["live"] / dT), money(r["rent"] / dT), money(r["sell"] / dT), NAME[r["best"]]], ["S41", "S43", "S48", "S47"], MD))
    shocks = [
        ("Home prices fall 25% in the first year after inheritance, then grow normally", "Selling at inheritance avoids the fall; keeping absorbs it.", ["S41"],
         M.decide(T, H, M.shock_path(H, home=-0.25))),
        ("Stocks fall 40% in the first year after the sale, then grow normally", "The sale proceeds take the fall; the home does not.", ["S48"],
         M.decide(T, H, M.shock_path(H, stock=-0.40))),
        ("Both of the above in the same year", "A 2008-style year.", ["S41", "S48"], M.decide(T, H, M.shock_path(H, home=-0.25, stock=-0.40))),
        ("Insurance premium triples", "The regulator notes wildfire surcharges of 15% to over 300%.", ["S34"], C.sens[2][3]),
        ("Family-home exclusion lost (deadline missed, or the home was not the parent's principal residence)", "No exceptions to the one-year rule.", ["S12"], C.sens[6][3]),
        (f"A one-off repair of {money(150_000)} in today's dollars in the first year", "Roof, foundation or similar; applies only if the home is kept.", ["S09"],
         M.decide(T, H, M.Scn(), {"one_off": 150_000 * dT})),
        ("The home sits empty for the whole first year when rented", "No rent, full costs.", ["S09"], M.decide(T, H, M.Scn(), {"vacant_year1": True})),
    ]
    ch = line_chart("Property A's value 2026-2075: smooth central path against a replay of 1976-2025",
                    [("Replay of real history", [(r["year"], r["a_replay"]) for r in C.fifty]),
                     ("Smooth central path", [(r["year"], r["a_base"]) for r in C.fifty]),
                     ("Assessed value (official factors replayed)", [(r["year"], r["av_replay"]) for r in C.fifty])],
                    "The replay applies each year's actual change in the San Jose metro house price index, 1977 to 2025, to the years 2027 to 2075.")
    w20 = {k: sum(1 for r in C.replay20 if r["best"] == k) for k in OPT}
    body = f"""{legend()}
<p>The projections elsewhere on this site grow at steady rates. Real economies do not: over the last 50 years U.S. inflation ranged from {pct(min(M._chg('cpi_dec', y) for y in range(1976, 2026)))} to {pct(max(M._chg('cpi_dec', y) for y in range(1976, 2026)))} in a year,
San Jose-area home prices from {pct(min(M._chg('hpi_sj', y) for y in range(1977, 2026)))} to {pct(max(M._chg('hpi_sj', y) for y in range(1977, 2026)))}, and a broad share-price index from {pct(min(M._chg('shares_us', y) for y in range(1976, 2026)))} to {pct(max(M._chg('shares_us', y) for y in range(1976, 2026)))}.
This section puts the decision through those real sequences instead of an invented one.</p>
<h2>How the test works</h2>
<ul>
<li>The starting point is the central case on the day of inheritance in {T}: the same home value, costs, rent and tax rules as on the Decision page.</li>
<li>For the {H} years that follow, each year's change in home prices, consumer prices, rents, share prices and the Treasury-bill rate is taken from an actual {H}-year stretch of official data. Every stretch from 1977-1986 to 2015-2024 is used: {len(rp)} in all.</li>
<li>Stock returns are the yearly change in a broad share-price index plus {pct(M.dividend_addon())} a year for dividends. That add-on is the amount that makes the index match the federal index fund's actual 1988-2025 return; it is a calibration, not an official series.</li>
<li>Results are after-tax wealth with everything cashed out, in today's dollars, the same measure as on the Decision page ({money(o['live']['liq_real'])} / {money(o['rent']['liq_real'])} / {money(o['sell']['liq_real'])} for live / rent / sell in the steady central case).</li>
</ul>
""" + cards([
        ("Selling came out ahead", f"{C.wins['sell']} of {len(rp)}", "replayed ten-year periods"),
        ("Renting out came out ahead", f"{C.wins['rent']} of {len(rp)}", "periods beginning " + year_ranges([r["start"] for r in rp if r["best"] == "rent"])),
        ("Living in it came out ahead", f"{C.wins['live']} of {len(rp)}", "it is a lifestyle choice, not the financial winner"),
        ("Range for selling", f"{mill(worst_row['sell']['sell'] / dT)} to {mill(best_row['sell']['sell'] / dT)}", f"worst {worst_row['sell']['start']}-{worst_row['sell']['end']}, best {best_row['sell']['start']}-{best_row['sell']['end']}"),
        ("Range for renting out", f"{mill(worst_row['rent']['rent'] / dT)} to {mill(best_row['rent']['rent'] / dT)}", f"worst {worst_row['rent']['start']}-{worst_row['rent']['end']}, best {best_row['rent']['start']}-{best_row['rent']['end']}"),
        ("Typical (median) result", f"{mill(med['sell'] / dT)} vs {mill(med['rent'] / dT)}", "selling vs renting out"),
    ]) + f"""
<h2>Five episodes</h2>
""" + table(["Years replayed", "What happened", "Worst year, homes", "Worst year, stocks", "Highest inflation", NAME["live"], NAME["rent"], NAME["sell"], "Best"], ep_rows, cls="num") + f"""
<p><b>Reading:</b> selling loses to renting when stocks have a poor decade while local home prices boom (the periods beginning in the late 1990s) and in the highest-inflation period, when homes and rents rose with prices.
Selling wins by the widest margins when the home is inherited near a housing peak or before a long bull market. Nobody knows in advance which period lies ahead, which is why the result is shown for all of them.</p>
<h2>Every replayed period</h2>
""" + table(["Years replayed", "Homes, a year", "Prices, a year", "Stocks, a year", "Worst year, homes", "Worst year, stocks", NAME["live"], NAME["rent"], NAME["sell"], "Best"], [
        ([f"{r['start']}-{r['end']}", pct(r["home"]), pct(r["cpi"]), pct(r["stock"]), pct(r["worst_home"]), pct(r["worst_stock"]),
          money(r["live"] / dT), money(r["rent"] / dT), money(r["sell"] / dT), NAME[r["best"]]], ["S41", "S43", "S44", "S48", "S47"], MD) for r in rp],
        caption=f"After-tax wealth from Property A, {H} years after a {T} inheritance, today's dollars", cls="num") + f"""
<p>Over 20-year stretches (1977-1996 to 2005-2024, {len(C.replay20)} in all) selling came out ahead in {w20['sell']}, renting in {w20['rent']} and living in the home in {w20['live']}.</p>
<h2>Shocks that are not market cycles</h2>
<p>One thing goes wrong; everything else follows the central case.</p>
""" + table(["Shock", "Why it is plausible", NAME["live"], NAME["rent"], NAME["sell"], "Best"], [
        ([lab, why] + [money(d["options"][k]["liq_real"]) for k in OPT] + [NAME[d["best"]]], sid, MD) for lab, why, sid, d in shocks],
        caption="After-tax wealth in today's dollars", cls="num") + f"""
<p>Law shocks (a lower federal tax-free amount, repeal of the estate tax) are on <a href="estate-thresholds.html">Cash inheritance &amp; tax-free limits</a> and <a href="law-watchlist.html">Law changes to watch</a>.
A change to the basis reset at death would matter most, because the case for selling rests on it; no such bill was confirmed, and the parent's own basis was not supplied, so its cost is left blank on Flagged for Review.</p>
<h2>Fifty years, replayed: 2026 to 2075</h2>
{ch}
<p>Each row applies the actual change from 50 years earlier. Assessed value uses the official yearly factors for the same years, which shows how far a capped assessment falls behind market value when prices rise unevenly.</p>
""" + table(["Year", "Replays", "Home prices", "Consumer prices", "Stocks", "Property A, replay", "Property A, smooth", "Assessed value, replay", "Property B, replay", "Property B, smooth"], [
        ([str(r["year"]), str(r["src"]) if r["src"] else "start", pct(r["home_chg"]), pct(r["cpi_chg"]), pct(r["stock_chg"]),
          money(r["a_replay"]), money(r["a_base"]), money(r["av_replay"]), money(r["b_replay"]), money(r["b_base"])],
         ["S41", "S42", "S43", "S48", "S14"], MD) for r in C.fifty], cls="num") + f"""
<p>Limits of this test: the indexes describe a metro area, not one house; the periods overlap, so they are not {len(rp)} independent trials; the rent index is for the San Francisco area; property-tax factors in the ten-year replays use U.S. rather than California prices; and tax law is held at today's rules.</p>
"""
    page("black-swan-scenarios", "Black-swan scenarios",
         "The plan under real booms, busts and inflation instead of steady growth: every ten-year period since 1977 replayed, plus single shocks and a 50-year path.", body, out)


# ====================================================================== law watch
def p_watch(C, out):
    body = legend() + """
<p>Status is as read on the linked official page on """ + VERIFIED_ON + """. "What it means here" is this project's reading.</p>
<h2>Federal</h2>
""" + table(["Measure", "Status", "What it means here"], [
        (["Estate tax-free amount (Public Law 119-21)", "Enacted 4 July 2025: $15,000,000 for 2026. The 2027 adjustment to $15,480,000 was released 5 November 2026.", "Raises the room for the cash inheritance. The model indexes it forward; a later Congress can change it."], ["S57", "S02"], V),
        (["2027 inflation-adjustment document", "Posted with an unfilled drafting placeholder in its first section (\"[Release Date, 2026]\"). The dollar amounts are stated clearly.", "Re-check the amounts when the document appears in the Internal Revenue Bulletin."], ["S02"], V),
        (["H.R.1301, Death Tax Repeal Act", "Introduced 13 February 2025; referred to the Ways and Means Committee; no further action.", "If enacted, no federal estate tax on the cash or the house. Not law."], ["S39"], V),
        (["H.R.5336, Equal Tax Act", "Introduced 11 September 2025; referred to the Ways and Means Committee; no summary published.", ""], ["S40"], UV),
        (["Any bill to end or limit the basis reset at death", "", ""], ["S04"], UV),
    ]) + """
<h2>California</h2>
""" + table(["Measure", "Status", "What it means here"], [
        (["Proposition 19 family-home exclusion", "In force. The allowance is $1,044,586 until 15 February 2027 and is adjusted again in February 2027.", "Sets how much of Property A's value is sheltered if the child moves in. The new amount was not yet published."], ["S13", "S12"], V),
        (["Initiative to repeal Proposition 19's family-transfer rules", "Failed to qualify for the ballot (Secretary of State memorandum, 18 May 2026).", "The rules used in this analysis stay as they are."], ["S21"], V),
        (["SB 293 (2025): family transfers in wildfire areas", "Chaptered 10 October 2025.", "Longer claim periods for certain 2025 fire areas. No effect on either property."], ["S31", "S12"], V),
        (["Proposition 3 (Nov 2026): extends an existing tax on high incomes", "Unofficial count 10 Nov 2026: 60.6% yes. Certified by 11 December 2026.", "The model already assumes today's California rate schedule continues. The measure's text was not read."], ["S20"], V),
        (["Proposition 40 (Nov 2026): one-time tax on certain taxpayers", "Unofficial count: 47.4% yes, 52.6% no.", "Failing in the unofficial count. The measure's text was not read."], ["S20"], V),
        (["Proposition 42 (Nov 2026): prohibits new state personal property taxes and certain retroactive state taxes", "Unofficial count: 51.5% yes. A close contest.", "If it stands, it limits new state taxes of that kind. The measure's text was not read."], ["S20"], V),
        (["Proposition 43 (Nov 2026): limits voters' ability to raise revenues for local services", "Unofficial count: 42.6% yes, 57.4% no.", "Failing in the unofficial count; local parcel-tax rules stay as they are."], ["S20"], V),
        (["Insurance rates", "A 17% interim increase for one large insurer's homeowners line took effect 1 June 2025; it had asked for 38% on rental dwellings.", "Premiums for both properties may rise faster than prices; the model assumes 2 points faster."], ["S35"], V),
        (["Rooftop solar tariffs", "Legacy tariffs closed; new systems on net billing since 15 April 2023; legacy customers keep their tariff for 20 years.", "Property A's small electricity credit will not last into the inheritance window."], ["S32"], V),
    ]) + """
<h2>San Francisco (Property B)</h2>
""" + table(["Measure", "Status", "What it means here"], [
        (["Measure H (Nov 2026): parcel tax for Muni", "Preliminary count 10 Nov 2026: 74.4% yes (needs a simple majority). Rates from $129 per parcel, inflation-adjusted, for 15 years.", "Adds at least $129 a year to Property B's bill. The rate for a three-unit parcel was not read."], ["S38"], V),
        (["File No. 261020: cap on banked and capital-improvement rent increases", "Pending at the Board of Supervisors; not enacted (Rent Board notice, 9 November 2026).", "Would limit how fast banked increases can be applied to Property B's tenants."], ["S37"], V),
        (["Allowed annual rent increase", "1.6% for 1 March 2026 to 28 February 2027; set at 60% of the Bay Area price increase.", "Property B's rent from sitting tenants rises more slowly than costs."], ["S37"], V),
        (["Empty Homes Tax", "Struck down in 2024; Court of Appeal affirmed 11 September 2026. Not collected unless reversed.", "Relevant because one of Property B's units is not rented. No tax applies today."], ["S19"], V),
        (["Secured property tax rate, 2026-27", "1.18162182%.", "Used for Property B's projections."], ["S17"], V),
        (["Water and sewer rate increases for 2026 and 2027", "", ""], ["S52"], UV),
    ])
    page("law-watchlist", "Law changes to watch",
         "Measures that are enacted, pending, failing or failed, and what each would do to the decision.", body, out)


# ====================================================================== flagged items
# (id, area, what is flagged, what to do, source ids, status)
FLAGS = [
    ("F01", "Privacy", "Earlier commits, pull requests and deployments of this public repository contain the owner's figures before rounding. Removing them from the current files does not remove them from Git history, forks or caches.",
     "Repository owner: follow GitHub's procedure for removing sensitive data, or make the repository private.", ["S53"], V),
    ("F02", "Privacy", "Rounding to $10 hides exact figures from a text search but a multi-year series of rounded assessed values could still be matched against public assessment rolls.",
     "Owner to decide whether the two history tables on 'The two properties' should be coarsened further or removed. They are published because the brief asks for assessed-value tables rounded to $10.", ["S53"], OI),
    ("F03", "Owner inputs", "Market values, assessed values, tax bills, rent, utility bills and insurance guesses come from the owner. None was checked against a record, by design: no parcel, address or account is looked up.",
     "Owner to confirm against the latest bills and statements.", ["S14"], OI),
    ("F04", "Property tax", "Property A's 2026 tax bill was not supplied.", "Left blank. Add when the bill arrives.", ["S16"], UV),
    ("F05", "Property tax", "Property A's tax rate area is unknown, and the county's 2026-27 rates were not available in the document read (2025-26). The model uses the sum of 2025-26 component rates for the school and special districts that serve the city (1.1636%).",
     "Read the tax rate area and total rate from the tax bill.", ["S16"], UV),
    ("F06", "Property tax", "Property A's bill is about $930 to $1,010 a year above rate times assessed value; Property B's is about $260 above rate times assessed value plus the official flat parcel taxes. The extra charges were not itemised.",
     "Compare with the 'direct charges' lines on each bill.", ["S16", "S18"], UV),
    ("F07", "Property tax", "The family-home exclusion needs Property A to be the parent's principal residence at death. That was not stated in the brief.",
     "Confirm, and confirm a homeowners' exemption is on file in the parent's name.", ["S12", "S15"], UV),
    ("F08", "Property tax", "The allowance that applies from 16 February 2027 was not yet published. For 2040-2050 the model grows today's allowance by one year of house-price change every second year.",
     "Check the Board of Equalization's letter in early 2027 and near the transfer date.", ["S13"], UV),
    ("F09", "Insurance", "No official premium for a home like Property A in its area, or for a tenant-occupied three-unit building in Property B's area, could be read. The regulator's comparison tool is an interactive form and does not cover landlord policies.",
     "Get written quotes; the tool is linked for manual use.", ["S34"], UV),
    ("F10", "Insurance", "The owner's guesses (about $1,500 a year each) are used in the model with growth 2 points above inflation. The growth rate is this project's assumption.",
     "Replace with quotes. The Decision page tests a premium three times higher.", ["S33", "S35"], AS),
    ("F11", "Solar", "Property A's solar connection date is unknown, so the year its legacy tariff ends is unknown; the bill after that was not estimated and is blank from 2043.",
     "Find the interconnection date on the utility agreement.", ["S32"], UV),
    ("F12", "Water", "The water tariff of the utility serving Property A was not read, and adoption of San Francisco's 2026 and 2027 water and sewer increases was not confirmed on an official page.",
     "Check the latest utility notices.", ["S52", "S45"], UV),
    ("F13", "Upkeep", "No repair or maintenance figures were supplied. The model uses placeholders ($10,000 a year for Property A and $15,000 for Property B in 2026).",
     "Replace with actual spending.", ["S09"], AS),
    ("F14", "Rent", "Property A's rent uses HUD's four-bedroom benchmark for its ZIP code area, a 40th-percentile figure that includes utilities; the home's bedroom count and condition are unknown. The rent for the unit the household would leave in Property B uses the average of the two rented units.",
     "Ask a local property manager for a rent estimate for each.", ["S36", "S37"], AS),
    ("F15", "Rent", "Whether Property B's units are covered by the city's rent rules depends on the building's age and legal unit count, which were not looked up. The model assumes they are.",
     "Confirm with the Rent Board.", ["S37"], UV),
    ("F16", "Tax model", "The household's filing status and income are unknown. The model assumes a joint return and $200,000 of other taxable income in today's dollars, indexes today's brackets forward, and leaves out the standard deduction, the state-and-local-tax deduction cap, the business-income deduction for rentals, the alternative minimum tax, California's surtax on very high incomes and the California exemption for Treasury interest.",
     "Have a tax professional rerun the comparison with actual returns. The Decision page tests $100,000 and $400,000.", ["S02", "S26"], AS),
    ("F17", "Tax model", "The depreciable building is assumed to be 25% of Property A's value; the 27.5-year period was read as an excerpt of the official publication, not by paging through it.",
     "Use the land and improvement split on the assessment notice.", ["S10"], AS),
    ("F18", "Investments", "Future returns are assumptions, not official forecasts: stock index fund 8% a year (6% to 10% tested), Treasuries 4.5%. The historical replay uses a price-only share index plus a 3.6-point calibration for dividends.",
     "Treat the break-even returns on the Decision page as the test, not the central numbers.", ["S49", "S48", "S51"], AS),
    ("F19", "Selling costs", "Commissions are negotiated, not set by law; 6% of the price is assumed for all selling costs. The local transfer-tax ordinances were not read (state law allows $0.55 per $500).",
     "Get a listing proposal when the time comes.", ["S30"], AS),
    ("F20", "Estate", "The amount of cash to be inherited was not supplied, so the site shows room under the limit instead of a tax figure. Cash held in retirement accounts follows different income-tax rules that were not read.",
     "Give [ADVISOR] the full list of assets.", ["S01"], UV),
    ("F21", "Estate", "Whether a lifetime gift of the house would keep the date-of-death basis reset was not read on an official page in this pass.",
     "Ask [ADVISOR] before any lifetime transfer.", ["S56", "S04"], UV),
    ("F22", "Estate", "California applies the federal rules on gain or loss, which contain the date-of-death basis rule, 'except as otherwise provided'. The exceptions were not searched one by one.",
     "Confirm with a California tax professional.", ["S27"], UV),
    ("F23", "Official source", "The IRS document with the 2027 amounts still contains an unfilled drafting placeholder, '[Release Date, 2026]'.",
     "Re-check when it is published in the Internal Revenue Bulletin.", ["S02"], V),
    ("F24", "Official source", "The November 2026 state and San Francisco results are unofficial or preliminary until certified (state: by 11 December 2026).",
     "Re-check after certification. The amount of the new San Francisco parcel tax for a three-unit building was not read.", ["S20", "S38"], V),
    ("F25", "Official source", "Read without scripts, the federal Thrift Savings Plan's returns page showed identical placeholder values for every fund in 2024 and 2025. Those figures were not used; the fund information sheet was used instead.",
     "No action; noted so the figures are not picked up by mistake.", ["S54", "S49"], V),
    ("F26", "Official source", "The consumer price index has no October 2025 value (federal shutdown). California's 2026 assessment factor was therefore computed from August to August, and the St. Louis Fed returns blank 2025 annual averages for several series.",
     "No action; series end in 2024 where the 2025 average is blank.", ["S14", "S43"], V),
    ("F27", "Law", "The text of H.R.5336 and of the November 2026 state propositions was not read; only their official titles and status are shown. No bill to end the basis reset at death was confirmed.",
     "Re-check the federal and state legislative sites near the transfer date.", ["S40", "S20"], UV),
    ("F28", "Model", "Projections assume steady growth and today's law for 15 to 35 years. The parcel-level property-tax factor in the ten-year replays uses U.S. prices in place of California prices, and metro price indexes stand in for two specific buildings.",
     "Read the central numbers together with the black-swan section.", ["S41", "S43"], AS),
    ("F29", "Earlier versions", "Earlier versions of this site said 'sell' using a model that left out California tax and rental income tax, and a later version withdrew all figures. This version recomputes the comparison with those taxes included and reaches 'sell' again, with the conditions under which it flips.",
     "None; recorded so the change of method is visible.", ["S25", "S09"], MD),
    ("F30", "Earlier versions", "Facts that earlier sessions cited but that were not re-read from the official page in this pass are not carried forward (for example city-level insurance survey data and the statewide rent-cap statute).",
     "They can be added back once re-read.", ["S33"], UV),
    ("F31", "Process", "The hosting platform fixes each working session to one branch, so the requested 'session-id/task' branch names could not be used; isolation was by exclusive file scopes recorded on the task board.",
     "None.", ["S53"], V),
]


def p_flagged(C, out):
    body = legend() + f"""
<p>{len(FLAGS)} items. Nothing here blocks the analysis; each is something that could not be confirmed from an official source, an assumption the owner should replace, or an irregularity in a source. Blank values elsewhere on the site are listed here.</p>
""" + table(["No.", "Area", "What is flagged", "What to do"], [([i, a, w, t], sid, st) for i, a, w, t, sid, st in FLAGS])
    page("flagged-for-review", "Flagged for Review",
         "Unverified values, assumptions and irregularities, each with a link for manual checking.", body, out)


# ====================================================================== methodology
def p_method(C, out):
    lab = {"infl": "Consumer-price inflation", "home_A": "Property A value growth", "home_B": "Property B value growth",
           "rent_mkt": "Market rent growth", "water": "Water cost growth", "elec": "Electricity cost growth",
           "stock": "Stock index fund return", "cash": "Treasury / savings return"}
    src = {"infl": ["S43", "S50"], "home_A": ["S41"], "home_B": ["S42"], "rent_mkt": ["S44"], "water": ["S45"],
           "elec": ["S46"], "stock": ["S49", "S48"], "cash": ["S51"]}
    body = legend() + f"""
<h2>How the work was done</h2>
<ul>
<li><b>Sources.</b> Every fact was read on an official page on {VERIFIED_ON}; the page is linked in the same table row. Values that could not be confirmed are left blank and listed on Flagged for Review.</li>
<li><b>Owner figures.</b> Rounded to the nearest $10 before they were written anywhere in this project. No parcel, address, account or person was looked up.</li>
<li><b>Model figures.</b> Calculated from the official rules and the assumptions below, then rounded to $10. They are projections, not forecasts.</li>
<li><b>Recommendation.</b> Not chosen by hand: it is the choice with the highest after-tax wealth in the central case, reported with the conditions under which another choice wins.</li>
</ul>
<h2>Growth assumptions</h2>
""" + table(["Assumption", "Low", "Central", "High", "Basis"], [
        ([lab[k], pct(v["low"]), pct(v["base"]), pct(v["high"]), v["why"]], src[k], AS) for k, v in ASSUME.items()]) + f"""
<h2>Other assumptions</h2>
""" + table(["Assumption", "Value", "Note"], [
        (["Inheritance year", "2040, 2045, 2050", f"Central case {C.T}; the brief gives 2040-2050"], ["S12"], OI),
        (["Holding period compared", "10 and 20 years", "Central case 10 years; everything is cashed out at the end so the choices are compared after tax"], ["S07"], AS),
        (["Assessed value growth", "2% a year", "The cap binds whenever inflation is at or above 2%"], ["S14"], MD),
        (["Family-home allowance growth", f"{pct(C.base.gA)} every second year", "One year's house-price change is applied every other February"], ["S13"], MD),
        (["Federal tax-free amount and brackets", f"{pct(C.base.infl - F['chained_gap'])} a year", "Chained price index assumed 0.3 point below ordinary inflation"], ["S02"], AS),
        (["California brackets", f"{pct(C.base.infl)} a year from the 2025 schedule", "Indexed with inflation"], ["S26"], AS),
        (["Insurance growth", f"{pct(C.base.infl + F['spread_insurance'])} a year", "2 points above inflation"], ["S35"], AS),
        (["Upkeep", f"{money(F['maint_A_2026'])} (A) and {money(F['maint_B_2026'])} (B) in 2026", "Placeholders, rising with prices"], ["S09"], AS),
        (["Property A rent", f"{money(O['hud_rent_A_4br_2026'])} a month in 2026", "HUD four-bedroom small-area benchmark"], ["S36"], V),
        (["Rent from the unit left in Property B", f"{money(F['b_unit_rent_month_2026'])} a month in 2026", "Average of the two rented units; then rises at 60% of inflation"], ["S37"], AS),
        (["Vacancy", pct(F["vacancy"], 0), "Share of rent lost in rental choices"], ["S09"], AS),
        (["Selling costs", pct(F["selling_cost"], 0) + " of price", "Commission, transfer tax, escrow and preparation; plus six months of carrying costs"], ["S30"], AS),
        (["Building share of Property A", pct(F["building_share"], 0), "Depreciated over 27.5 years when rented"], ["S10"], AS),
        (["Portfolio", "60% stock index fund, 40% Treasuries", f"Dividends ({pct(F['dividend_yield'])} of the stock value) and interest taxed yearly; stock gains taxed when sold"], ["S49", "S51"], AS),
        (["Household", f"Joint return; {money(F['other_income_2026'])} other taxable income in 2026 dollars", "Sets the tax bracket for extra income"], ["S02", "S26"], AS),
        (["Home-sale exclusion", money(O["sec121_joint"]), "Joint return, after two years of living in the home"], ["S06"], V),
        (["Solar credit", f"held at the owner's figure until {F['solar_legacy_latest_end'] - 1}", "Blank afterwards"], ["S32"], AS),
    ]) + f"""
<h2>Formulas</h2>
""" + table(["Quantity", "Formula"], [
        (["Property tax, Property A", "assessed value x 1.1636% + flat charges (the gap between the 2025 bill and rate x assessed value, grown with prices)"], ["S16"], MD),
        (["Property tax, Property B", "assessed value x 1.18162182% + flat charges (same method) + $129 a year for the new transit parcel tax, 2027-2041"], ["S17", "S18", "S38"], MD),
        (["Assessed value after inheritance, child moves in", "parent's assessed value, plus any part of market value above (parent's assessed value + allowance); then 2% a year; less the $7,000 homeowners' exemption"], ["S12", "S15"], MD),
        (["Assessed value after inheritance, otherwise", "market value on the date of death; then 2% a year"], ["S12"], MD),
        (["Taxable rent", "rent x (1 - vacancy) - property tax - insurance - upkeep - depreciation; losses are carried forward and used against later rent or the sale"], ["S09", "S10"], MD),
        (["Income tax on extra income", "federal 2027 joint brackets and capital-gain thresholds (indexed) + 3.8% net investment income tax above $250,000 + California 2025 joint brackets (indexed), computed with and without the extra income"], ["S02", "S08", "S26"], MD),
        (["Tax when a kept home is sold", "(price - selling costs - basis) taxed as long-term gain; depreciation taken is taxed at up to 25%; up to $500,000 excluded if lived in; California taxes all of it as ordinary income"], ["S06", "S07", "S25"], MD),
        (["After-tax wealth", "home sale proceeds or portfolio value, plus the side account of yearly net cash, minus all taxes due on cashing out"], ["S04"], MD),
        (["Today's dollars", f"divide by (1 + {pct(C.base.infl)}) for each year after 2026"], ["S43"], MD),
        (["Room under the estate limit", "tax-free amount for the year - Property A's projected value"], ["S01", "S02"], MD),
        (["Replay stock return", f"yearly change in the share-price index + {pct(M.dividend_addon())}"], ["S48", "S49"], MD),
    ]) + """
<h2>What the model leaves out</h2>
<p>Mortgage debt (none was mentioned), earthquake damage and insurance, the tenant-side rules that apply if Property A is rented, changes in tax law, the family's own preferences, and Property B's value and rent (identical in all three choices). See Flagged for Review for the full list.</p>
"""
    page("methodology", "Methodology & assumptions",
         "Where every assumption comes from, the formulas, and what is left out.", body, out)


# ====================================================================== sources and privacy
def p_sources(C, out):
    rows = [([sid, ag, f'<a class="doc" href="{ESC(url, quote=True)}" rel="noopener noreferrer">{ESC(title)}</a>', ESC(read), VERIFIED_ON], [sid], V)
            for sid, (ag, label, title, url, read) in sorted(SOURCES.items())]
    rows = [([ESC(c) if i not in (2, 3) else c for i, c in enumerate(cells)], s, st) for cells, s, st in rows]
    body = legend() + f"""
<p>{len(SOURCES)} official pages and documents, each opened and read for this version. The same links appear in every table row that relies on them, so any figure can be checked by hand.
Four hosts are official but do not end in .gov: the Federal Reserve Bank of St. Louis data service (which republishes Bureau of Labor Statistics, Federal Housing Finance Agency, Federal Reserve and OECD series), the San Francisco Treasurer &amp; Tax Collector, the San Francisco Department of Elections, and GitHub's own documentation.</p>
""" + table(["ID", "Agency", "Document", "What was read", "Read on"], rows, raw=True)
    page("sources", "Official sources", "Every source used on this site, with what was read on it.", body, out)


def p_privacy(C, out):
    body = legend() + """
<h2>What this site does and does not show</h2>
""" + table(["Kind of information", "Treatment"], [
        (["Names of people, the trust and advisers", "Never shown. Placeholders such as [BENEFICIARY], [TRUSTEE] and [ADVISOR] are used."], ["S53"], V),
        (["Street addresses, parcel numbers, account numbers", "Never collected, never looked up, never shown."], ["S53"], V),
        (["ZIP codes and neighbourhood names", "Not shown. Each property is identified by city only."], ["S53"], V),
        (["Owner's dollar figures", "Rounded to the nearest $10 before being written into this project, as the brief instructs. The figures before rounding are not stored anywhere in the current files, not even as test patterns."], ["S53"], V),
        (["Model results", "Rounded to the nearest $10."], ["S53"], V),
        (["Official statutory amounts", "Shown exactly (for example $1,044,586 or $334.38) because they are public and identify no one."], ["S13", "S18"], V),
        (["Search engines", "Every page asks search engines not to index it."], ["S53"], V),
    ]) + """
<h2>What remains exposed</h2>
<p>This repository and its history are public. Earlier commits and earlier deployments contained the owner's figures before rounding, and removing them from the current files does not remove them from Git history, forks or caches.
Only the repository owner can purge history or make the repository private; GitHub's procedure is linked in the table above and on Flagged for Review (items F01 and F02).
Rounding prevents a search for an exact figure but cannot guarantee that a determined person could not match a series of rounded values against public records.</p>
"""
    page("privacy", "Privacy", "What is withheld, what is rounded, and what the owner still needs to do.", body, out)


ALL_PAGES = [p_index, p_exec, p_properties, p_decision, p_projections, p_ptax, p_costs, p_estate, p_law,
             p_process, p_swan, p_watch, p_method, p_sources, p_flagged, p_privacy]
