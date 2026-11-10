"""Operating costs and decision analysis pages."""
from common import (ASSUM, BY_YEAR, CU, DEC, PROJ, SCEN, SF, SF_BY_YEAR, badge, esc, layout,
                    money, pct, src_link, table)


def _proj_rows(series, keys, every=5):
    out = []
    for r in series:
        if r["year"] == 2026 or (r["year"] - 2026) % every == 0:
            out.append([str(r["year"])] + [("num", money(r[k])) for k in keys])
    return out


def costs():
    cost_rows = [
        ["Home insurance", ("num", money(1500)), ("num", money(125)), ("num", money(1500)), ("num", money(125)),
         "Owner estimate, trailing 12 months", badge("flagged")],
        ["Water", ("num", money(1500)), ("num", money(125)), ("num", money(4380)), ("num", money(365)),
         "Owner-reported; Cupertino $100–$150/mo, SF $330–$400/mo for three units", badge("reported")],
        ["Electricity", ("num", money(-180)), ("num", "-$15"), ("num", money(600)), ("num", money(50)),
         "Owner-reported; Cupertino net credit from rooftop solar", badge("reported")],
        ["Maintenance & repairs", ("num", money(6000)), ("num", money(500)), ("num", money(9000)), ("num", money(750)),
         "Model assumption: ≈0.2% of value (Cupertino, newer systems) and ≈0.5% (SF, three units, 1920s-era)", badge("assumption")],
        ["Property management", ("num", "—"), ("num", "—"), ("num", "8% of collected rent"), ("num", "≈$572"),
         "Model assumption; self-management would remove it", badge("assumption")],
        ["Vacancy allowance", ("num", "—"), ("num", "—"), ("num", "5% of gross rent"), ("num", "≈$358"),
         "Model assumption; covers turnover and unpaid rent", badge("assumption")],
        ["<strong>Property tax (2026)</strong>", ("num", money(BY_YEAR[2026]["tax"])), ("num", money(BY_YEAR[2026]["tax"]/12)),
         ("num", money(SF_BY_YEAR[2026]["tax"])), ("num", money(SF_BY_YEAR[2026]["tax"]/12)),
         "Rate × assessed value + charges; see Taxes", badge("projected")],
    ]
    cost_tbl = table("2026 operating cost build-up",
                     ["Line item", "Cupertino / yr", "Cupertino / mo", "San Francisco / yr", "San Francisco / mo",
                      "Basis", "Status"],
                     cost_rows,
                     "Negative electricity is a credit: the rooftop solar system generates more than the house uses. "
                     "Totals below include property tax; the four cost items alone are ≈$8,800 (Cupertino) and ≈$15,500 (SF) a year.")

    tot_c = BY_YEAR[2026]["tax"] + 1500 + 1500 - 180 + 6000
    tot_s = SF_BY_YEAR[2026]["tax"] + 1500 + 4380 + 600 + 9000 + 7150*12*0.13
    totals = table("Total annual carrying cost, 2026",
                   ["Property", "Property tax", "Insurance", "Water", "Electric", "Maintenance", "Management + vacancy", "Total", "% of value"],
                   [["Cupertino", ("num", money(BY_YEAR[2026]["tax"])), ("num", money(1500)), ("num", money(1500)),
                     ("num", money(-180)), ("num", money(6000)), ("num", "—"), ("num", money(tot_c)),
                     ("num", pct(tot_c/3100000, 2))],
                    ["San Francisco", ("num", money(SF_BY_YEAR[2026]["tax"])), ("num", money(1500)), ("num", money(4380)),
                     ("num", money(600)), ("num", money(9000)), ("num", money(7150*12*0.13)), ("num", money(tot_s)),
                     ("num", pct(tot_s/1800000, 2))]],
                   "Cupertino is the cheaper property to hold: about 0.5% of value a year all-in, against about 1.6% for the "
                   "three-unit building. The gap is management, vacancy, water and maintenance on three tenancies.")

    cup_proj = table("Cupertino — projected carrying costs (5-year steps)",
                     ["Year", "Property tax", "Insurance", "Water", "Electric", "Maintenance"],
                     _proj_rows(CU, ["tax", "insurance", "water", "electric", "maintenance"]),
                     "Insurance grows at 5%/yr, water at 6%/yr, electricity at 4%/yr, maintenance at CPI + 1%. These growth rates are "
                     "assumptions; the 2026 base values are the sources listed above.")
    sf_proj = table("San Francisco — projected carrying costs (5-year steps)",
                    ["Year", "Property tax", "Insurance", "Water", "Electric", "Maintenance"],
                    _proj_rows(SF, ["tax", "insurance", "water", "electric", "maintenance"]),
                    "Same growth assumptions. Water is the fastest-growing line in San Francisco: SFPUC approved a 23% two-year "
                    "increase in 2026 (10.5% from 1 July 2026, 12.5% from 1 July 2027).")

    body = f"""
<section class="hero">
  <div class="eyebrow">Operating costs</div>
  <h1>Insurance, water, power and upkeep</h1>
  <p class="lede">These are the numbers that quietly decide whether keeping a house is a good idea. Two of the four categories
  are owner-reported, one is an estimate that no agency publishes at parcel level, and one is a modelling assumption — each is
  labelled.</p>
</section>

<h2 class="anchor" id="build">2026 build-up</h2>
{cost_tbl}
{totals}

<h2 class="anchor" id="insurance">Insurance: what can and cannot be verified</h2>
<p>The California Department of Insurance publishes policy forms, coverage guidance and complaint data, but <strong>no
official premium for a given ZIP code or parcel</strong>. Premiums are individually rated on dwelling value, roof age, claims
history and fire-score. The $1,500 figure for each property is therefore an owner estimate and is flagged as unverified.</p>
<ul class="tight">
  <li><a class="src" href="https://www.insurance.ca.gov/01-consumers/105-type/95-guides/03-res/" target="_blank" rel="noopener">CDI homeowners guide</a> — coverage and shopping guidance (verified).</li>
  <li><a class="src" href="https://www.cfpnet.com/" target="_blank" rel="noopener">California FAIR Plan</a> — insurer of last resort. The FAIR Plan writes fire-only dwelling coverage; a separate difference-in-conditions policy is normally needed for full HO-3 coverage, so a FAIR Plan quote is not a like-for-like replacement for a $1,500 homeowners policy.</li>
</ul>

<div class="callout warn">
  <div class="h">Planning caution</div>
  <p>A three-unit 1920s building in the Sunset with two tenancies is a landlord policy, not a homeowners policy, and a
  Cupertino house with solar and a $3.1M replacement cost is unlikely to be insured for $1,500 at today's construction costs. Both
  figures are carried as reported because no official source exists, but the model's 5%/yr growth from a $1,500 base is more
  likely to understate than overstate. Resolve this with two actual quotes before relying on the cash-flow projections.</p>
</div>

<h2 class="anchor" id="water">Water and power</h2>
<ul class="tight">
  <li><strong>San Francisco water.</strong> SFPUC's residential volumetric rate was $11.40 per unit (748 gallons) for the first four
  units a month in FY 2025-26, proposed to rise to $12.20 in FY 2026-27. The average single-family combined water-and-sewer bill is
  about $171 a month. Three units at $330–$400 a month is consistent with that average once sewer and common-area use are included —
  the owner-reported figure passes a sanity check.
  <a class="src" href="https://www.sfpuc.gov/accounts-services/water-power-sewer-rates/proposed-water-sewer-rates-2026/proposition-218-notice" target="_blank" rel="noopener">SFPUC Prop 218 notice</a>.</li>
  <li><strong>Cupertino water.</strong> Supplied by San Jose Water, whose tariff is filed with the CPUC. The published tariff could not
  be retrieved in this window, so $100–$150 a month stands as owner-reported only.</li>
  <li><strong>Electricity.</strong> PG&amp;E Schedule E-1 is the applicable residential tariff
  (<a class="src" href="https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_SCHEDS_E-1.pdf" target="_blank" rel="noopener">PG&amp;E E-1</a>).
  The Cupertino house is net-negative because of rooftop solar; the model credits $180 a year and grows the credit at 4%. The
  San Francisco building's $30–$70 a month is common-area power only if tenants pay their own accounts; if the owner pays all three
  units, this line is understated.</li>
</ul>

<h2 class="anchor" id="projections">Projected costs</h2>
{cup_proj}
{sf_proj}

<h2 class="anchor" id="why">Why maintenance is a percentage, not a guess</h2>
<p>There is no official source for "maintenance on a Bay Area house", so the model anchors to replacement-cost logic:
roughly 0.2% of value a year for a single house with solar and recent systems, and 0.5% for a three-unit building. Deferred
maintenance is the risk: a roof, a sewer lateral or a foundation on a 1920s Sunset building can be a $50,000–$100,000 event that
averages out to far more in the year it happens. The Scenario Analysis does not model a capital event; treat the 0.5% as a floor.</p>
"""
    return layout("costs", "Operating Costs", body, prefix="../")


def decisions():
    # results table
    res_rows = []
    for k in "ABCD":
        s = SCEN[k]
        res_rows.append([f"<strong>{k}</strong>", f"{esc(s['name'])}<br><span class='small'>{esc(s['sub'])}</span>",
                         ("num", money(s["net_worth_hold_2065"])), ("num", money(s["net_worth_2065"])),
                         ("num", money(s["deferred_capital_gains_tax"])),
                         ("num", money(s["cumulative_cash_flow"])),
                         ("num", money(s["net_worth_hold_2065"] / 20))])
    res = table("Four strategies run to 2065",
                ["#", "Strategy", "Net worth 2065 (hold basis)", "Net worth 2065 (liquidated)",
                 "Deferred capital gains tax", "Cumulative cash flow 2045–2065", "Average annual cash flow"],
                res_rows,
                "Starting point is the inheritance year (2045). 'Hold basis' marks houses to market and does not deduct selling "
                "costs or capital gains tax; 'liquidated' does. Cash flow includes the rental value of the home occupied in that "
                "scenario, because otherwise the four options would be consuming different amounts of housing.")

    # sensitivity grid
    sens = PROJ["sensitivity"]
    invs = sorted({s["investment"] for s in sens})
    apps = sorted({s["appreciation"] for s in sens})
    hdr = ["House appreciation ↓ / portfolio return →"] + [f"{pct(i,1)} after tax" for i in invs]
    rows = []
    for a in apps:
        row = [f"{pct(a,1)} per year"]
        for i in invs:
            m = next(s for s in sens if s["appreciation"] == a and s["investment"] == i)
            vals = sorted([(m["A"], "Live"), (m["B"], "Rent"), (m["C"], "Sell & invest"), (m["D"], "Sell both")], reverse=True)
            row.append(f"<strong>{vals[0][1]}</strong><br><span class='small'>+{money(vals[0][0]-vals[1][0])} vs next</span>")
        rows.append(row)
    sens_tbl = table("Which strategy wins under different return assumptions", hdr, rows,
                     "Each cell shows the winning strategy and its margin over the runner-up, in 2065 hold-basis net worth. "
                     "The winner never changes inside this grid — but the margin does, and at the top-right corner it is thin.")

    # break-even
    be_rows = [[f"{pct(b['investment'],1)} after tax", f"{b['appreciation']:.1f}% per year",
                "Hold the house if you believe Cupertino appreciates faster than this"] for b in PROJ["breakeven"]]
    be = table("Break-even appreciation: when does keeping the Cupertino house beat selling it?",
               ["Portfolio return", "Cupertino appreciation needed", "Reading"],
               be_rows,
               "Solved numerically: the appreciation rate at which the 'live in it' strategy's 2065 net worth equals "
               "'sell and invest'. Above the threshold, holding wins; below it, selling wins.")

    # rent sensitivity
    rent_rows = [[money(r["rent"]) + "/mo", ("num", money(r["A"])), ("num", money(r["C"])),
                  ("num", money(r["A"] - r["C"]))] for r in PROJ["rent_sensitivity"]]
    rent_tbl = table("The most uncertain input: Cupertino market rent",
                     ["Cupertino rent, 2026", "'Live in it' net worth 2065", "'Sell & invest' net worth 2065", "Gap"],
                     rent_rows,
                     "No official rent for a Cupertino house of this size was retrievable; $6,000 a month is the model assumption. "
                     "Rent matters twice — as the income you forgo by living there, and as the income you earn by renting it out.")

    # timing
    time_rows = [[str(t["inheritance_year"]), ("num", money(t["live"])), ("num", money(t["sell_invest"])),
                  ("num", money(t["advantage_live"]))] for t in PROJ["timing"]]
    time_tbl = table("Does the timing inside the 2040–2050 window change the answer?",
                     ["Inheritance year", "Live in it", "Sell & invest", "Advantage of living"],
                     time_rows,
                     "Earlier inheritance means more years of compounding for whichever asset you end up holding; the ranking does "
                     "not change across the window.")

    # annual detail for A
    det_a = PROJ["detail_A"]
    det_rows = [[str(r["year"]), ("num", money(r["cup_tax"])), ("num", money(r["cup_opex"])),
                 ("num", money(r["sf_gross"])), ("num", money(r["sf_tax"])), ("num", money(r["cash_flow"])),
                 ("num", money(r["portfolio"])), ("num", money(r["property_value"]))] for r in det_a]
    det = table("Inside the 'live in it' scenario — every fifth year",
                ["Year", "Cupertino tax", "Cupertino all-in cost", "SF gross rent (3 units)", "SF income tax",
                 "Net cash flow", "Portfolio", "Property value"],
                det_rows,
                "Cupertino all-in cost = property tax + insurance + water + electricity + maintenance. Cash flow includes the "
                "imputed rent of living in the house, which is why it stays positive while the house itself throws off nothing.")

    body = f"""
<section class="hero">
  <div class="eyebrow">Decision analysis</div>
  <h1>Live in it, rent it, or sell it — with the tax consequences attached</h1>
  <p class="lede">Four strategies, one model, identical assumptions, run from the inheritance year to 2065. Everything below is
  generated by <code>tools/model.py</code>: there are no hand-typed results.</p>
</section>

<div class="callout ok">
  <div class="h">Result</div>
  <p><strong>Sell the Cupertino house shortly after death and reinvest the proceeds; keep the San Francisco building.</strong>
  Base case: {money(SCEN['C']['net_worth_hold_2065'])} of 2065 net worth against {money(SCEN['A']['net_worth_hold_2065'])} for living
  in it and {money(SCEN['B']['net_worth_hold_2065'])} for renting it out. The margin over "live in it" is
  {money(SCEN['C']['net_worth_hold_2065'] - SCEN['A']['net_worth_hold_2065'])} on a hold basis and {money(SCEN['C']['net_worth_2065'] - SCEN['A']['net_worth_2065'])} after
  liquidation costs and capital gains tax.</p>
  <p><strong>Renting the house out and living in it are effectively tied</strong> — a difference of {money(DEC['delta_A_minus_B'])} in
  2065. That is a useful finding: you are not giving up much by choosing the living arrangement you actually prefer.</p>
</div>

<h2 class="anchor" id="strategies">The four strategies</h2>
{res}

<h2 class="anchor" id="ranking">Ranking</h2>
<div class="card">
{_bars()}
</div>

<h2 class="anchor" id="sensitivity">Sensitivity: 3 × 3</h2>
{sens_tbl}

<h2 class="anchor" id="breakeven">Where the recommendation would flip</h2>
{be}
<div class="callout warn">
  <div class="h">Read the break-even honestly</div>
  <p>Bay Area house prices have historically compounded faster than 5.5% nominal over long windows, and a 4% after-tax portfolio
  return is pessimistic. If you believe both of those at once — Cupertino above 5.46% and a portfolio at 4% — then keeping the
  house wins. With the model's own 5.5% portfolio return, the house would need 7.44% a year to catch up. <strong>The decision is
  a bet on appreciation versus diversified returns, not a bet on the tax code.</strong></p>
</div>

<h2 class="anchor" id="rent">Rent assumption</h2>
{rent_tbl}

<h2 class="anchor" id="timing">Timing</h2>
{time_tbl}

<h2 class="anchor" id="inside">Inside the recommended path</h2>
{det}

<h2 class="anchor" id="risks">Risk register — what would change the answer</h2>
<div class="tablewrap"><table>
<thead><tr><th>Risk</th><th>Direction</th><th>Size</th><th>Mitigation</th></tr></thead>
<tbody>
<tr><td>Cupertino appreciates faster than 7.4%/yr while the portfolio returns 5.5%</td><td>Favours keeping the house</td>
    <td>Flips the ranking</td><td>Re-run the model at each 5-year review; do not pre-commit to selling before the death occurs</td></tr>
<tr><td>Cupertino is not the parents' principal residence at death</td><td>Favours selling</td>
    <td>Removes ≈$20k/yr of Prop 19 relief at 2045</td><td>Establish and document residency, or accept full reassessment</td></tr>
<tr><td>Federal estate exclusion is reduced by future legislation</td><td>Neutral for the property choice; raises estate tax</td>
    <td>40% of the excess over the exclusion</td><td>Annual gifting, trust structuring, life insurance; review after each federal tax act</td></tr>
<tr><td>Portfolio returns below 4% after tax for 20 years</td><td>Favours keeping the house</td><td>≈$4M swing</td>
    <td>Glide to a lower-volatility allocation as the horizon shortens</td></tr>
<tr><td>Deferred maintenance on the Sunset building</td><td>Favours selling Cupertino (less capital need)</td>
    <td>$50k–$100k per event</td><td>Reserve 0.5% of value a year; inspect roof, sewer lateral and foundation now</td></tr>
<tr><td>Rent control tightens further or a tenant vacates</td><td>Favours selling San Francisco</td>
    <td>Vacancy decontrol is an upside; tighter rules a downside</td><td>Keep the third unit available for family use as planned</td></tr>
</tbody></table></div>

<h2 class="anchor" id="actions">Action list</h2>
<ol class="steps">
  <li><h4>Now — confirm residency facts</h4><p>Which property is the parents' principal residence, and is a homeowners' exemption
  filed there? This single fact determines whether Prop 19 relief exists at all.</p></li>
  <li><h4>Now — get two real insurance quotes per property</h4><p>The $1,500 estimate is the weakest input in the cash-flow model.</p></li>
  <li><h4>Now — confirm the trust actually holds the real property</h4><p>A trust avoids probate only for assets titled to it. A deed
  into the trust now is far cheaper than a probate later.</p></li>
  <li><h4>Now — record the basis</h4><p>Keep the original purchase documents. The step-up at death is only as good as the
  paperwork that proves what the parents paid and what was improved.</p></li>
  <li><h4>Do not sell either property before death</h4><p>A sale by the parents realises their capital gain and destroys the
  step-up. The cheapest exit is the one that happens after death.</p></li>
  <li><h4>At death — get a dated appraisal before anything else</h4><p>It sets the new basis and the Prop 19 market value.</p></li>
  <li><h4>Within 12 months — decide occupancy</h4><p>Move in and file the exemption, or accept reassessment. There is no extension.</p></li>
  <li><h4>At each 5-year review — re-run <code>tools/model.py</code></h4><p>Update appreciation, rents and rates; the ranking is
  sensitive to the first two.</p></li>
</ol>
"""
    return layout("decisions", "Decision Analysis", body, prefix="../")


def _bars():
    order = sorted(PROJ["scenarios"], key=lambda s: -s["net_worth_hold_2065"])
    top = order[0]["net_worth_hold_2065"]
    out = ['<div class="bars">']
    for s in order:
        w = max(3, s["net_worth_hold_2065"] / top * 100)
        cls = "bar-fill win" if s is order[0] else "bar-fill"
        out.append(
            f'<div class="bar-row"><div class="bar-label">{esc(s["name"])}<small>{esc(s["sub"])}</small></div>'
            f'<div class="bar-track"><div class="{cls}" style="width:{w:.1f}%"></div></div>'
            f'<div class="bar-val">{money(s["net_worth_hold_2065"])}</div></div>')
    out.append("</div>")
    return "\n".join(out)
