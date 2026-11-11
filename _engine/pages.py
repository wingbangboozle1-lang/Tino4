"""Page content.  All numbers come from model.py; all owner figures are rounded to $10."""
from types import SimpleNamespace
import model as M
from inputs import (A, B, OFFICIAL as O, ASSUME, FIXED as F, BASE_YEAR, LAST_YEAR, PROJ_LAST,
                    INHERIT_YEARS, CENTRAL_T, CENTRAL_H, HORIZONS)
from content import SOURCES, VERIFIED_ON
from render import (ESC, table, cards, note, legend, money, mill, pct, link, srcs, badge, page,
                    line_chart, bar_chart, r10, NAV, STATUS_HELP)

V, OI, MD, AS, UV = "Verified", "Owner input", "Model", "Assumption", "Unverified"
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
<p><b>Reading:</b> a home valued at {money(A['value_2026'])} is likely to cost more to insure than the statewide average home, and a three-unit rental needs a landlord policy, which is priced differently from a homeowner policy. Both guesses should be replaced with written quotes. Tripling the premium changes the ten-year result by less than {money(abs(C.sens[2][3]['options']['rent']['liq_real'] - C.d['options']['rent']['liq_real']) + 10)} and does not change the ranking.</p>
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
