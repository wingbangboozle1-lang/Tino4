#!/usr/bin/env python3
"""s-179ec133 — dashboard pages, part A: overview, summary, decision, properties, projections, running costs."""
from sitegen import *

D = R["decision"]; T0, H0 = D["T"], D["H"]
BY = {o["T"]: o for o in D["by_year"]}
V = D["by_vehicle"]
PRM = {p["key"]: p for p in R["params"]}
C = R["cost_2026"]
PA = {r["year"]: r for r in R["proj_a"]}; PB = {r["year"]: r for r in R["proj_b"]}
EST = {r["year"]: r for r in R["estate"]}
FY = D["first_year"]
BE = D["breakeven"]
PLAN = {"sell": "Sell and reinvest", "rent": "Rent it out", "live": "Live in it"}
NAME_A = "Property A (Cupertino house, to be inherited)"
NAME_B = "Property B (San Francisco 3-unit building, already owned)"
RW = R["replay_summary"]; BW = R["bootstrap"]["summary"]


def p_index(out):
    s = "index"
    gap = V["stocks"]["sell_real"] - V["stocks"]["live_real"]
    body = """
<div class="answer">
<p><strong>Best plan on the numbers:</strong> keep Property B exactly as it is, and when Property A is inherited, sell it within about a year
and invest what is left after costs in a low-cost stock index fund (or a stock-heavy mix).</p>
<p><strong>Why:</strong> inheriting resets Property A's taxable value, so its yearly property tax would rise from about %s to about %s
(living in it) or %s (renting it out) in %d. The same event resets its tax cost basis to market value, so selling soon after triggers little or
no capital gains tax. Property B is the opposite: its low taxable value and its rents are worth keeping, and selling it would be taxed.</p>
<p><strong>How firm is this:</strong> selling wins in the baseline for every inheritance year from 2040 to 2050, and in %s of the %d
replays of real 1977–2025 history. It stops winning if stocks return less than about %s a year for 20 years, or if the money would
sit in savings or Treasuries while local house prices repeat their long-run record. See %s.</p>
</div>
<div class="cards">
<div class="card"><div class="k">Wealth from Property A after %d years</div><div class="v">%s</div><div class="n">Sell and hold a stock index fund, in 2026 dollars. Renting it out: %s. Living in it: %s.</div>%s</div>
<div class="card"><div class="k">Price of living in Property A</div><div class="v">%s</div><div class="n">Difference between selling and living in it over %d years, in 2026 dollars. A choice, not a mistake — but it has a price.</div>%s</div>
<div class="card"><div class="k">Property A tax in %d</div><div class="v">%s → %s</div><div class="n">Before inheritance → if a child moves in. %s if it is rented or left empty.</div>%s</div>
<div class="card"><div class="k">Estate tax room in %d</div><div class="v">%s</div><div class="n">Projected room for cash and other assets, on top of the house, before any federal estate tax (one parent's exclusion).</div>%s</div>
</div>
<div class="legend">%s</div>
<h2>Sections</h2>
""" % (money(BY[T0]["ptax_before"]), money(BY[T0]["ptax_live"]), money(BY[T0]["ptax_rent"]), T0,
       pct(RW["stocks"]["wins"]["sell"] / 100.0, 0), len(R["replay"]), pct(BE["stock_return"]), link("black-swan-scenarios", "Black-swan conditions", s),
       H0, money(V["stocks"]["sell_real"]), money(V["stocks"]["rent_real"]), money(V["stocks"]["live_real"]), link("decision-analysis", "Open the comparison →", s).replace("<a ", '<a class="more" '),
       money(gap), H0, link("decision-analysis", "See what drives it →", s, "#first-year").replace("<a ", '<a class="more" '),
       T0, money(BY[T0]["ptax_before"]), money(BY[T0]["ptax_live"]), money(BY[T0]["ptax_rent"]), link("projections", "Year-by-year tables →", s).replace("<a ", '<a class="more" '),
       T0, money(EST[T0]["room"]), link("estate-thresholds", "Thresholds and headroom →", s).replace("<a ", '<a class="more" '),
       " ".join("%s %s" % (chip(k), e(STATUS[k][2])) for k in "VOPAU"))
    rows = [
        ([link("executive-summary", "Executive summary", s), "The answer, the key facts and what to do next, on one page."], ["IRS-INHERIT-FAQ", "BOE-PROP19"], "P"),
        ([link("decision-analysis", "Live, rent or sell", s), "The three plans for Property A compared after tax, with break-even points and sensitivity tests."], ["BOE-LTA-2026-026", "IRS-TC409", "FTB-CAPGAINS"], "P"),
        ([link("properties", "The two properties", s), "Why the inherited home and the already-owned building are treated differently; the owner's tax history checked against official factors."], ["BOE-LTA-2026-002", "SF-TTX-SECURED"], "O"),
        ([link("projections", "Year-by-year projections", s), "Value, assessed value, property tax, insurance, water, electricity and upkeep for both properties, 2026–2076."], ["BOE-LTA-2026-002", "CBO-OUTLOOK-2026"], "P"),
        ([link("operating-costs", "Running costs", s), "Insurance, water, electricity, solar and upkeep: what the owner reported, what official sources say, what is still open."], ["CFPB-WORKSHEET", "EIA-T5A-2024", "CPUC-NEM"], "O"),
        ([link("inheritance-law", "Tax and property law", s), "The federal, California and local rules that drive the numbers, each quoted from the official page."], ["IRS-ESTATE", "BOE-PROP19", "CA-RTC-13301"], "V"),
        ([link("estate-thresholds", "Estate tax thresholds", s), "How much can pass tax-free, how much room the house leaves for cash, and how that changes over time."], ["IRS-RP-2026-35", "IRS-I706"], "V"),
        ([link("inheritance-process", "Inheritance step by step", s), "What to do before and after the transfer, in order, with deadlines and forms."], ["BOE-PUB800-9", "CA-PROB-16061-7", "IRS-ESTATE-FAQ"], "V"),
        ([link("black-swan-scenarios", "Black-swan conditions", s), "The plans re-run through real 1977–2025 history: inflation shocks, housing slumps and market crashes."], ["FRED-SERIES", "ERP-B55", "ERP-B56"], "P"),
        ([link("law-watchlist", "Law changes to watch", s), "Rules under discussion or just changed, and what each would do to the decision."], ["CA-SOS-RESULTS-2026", "US-S587", "CPUC-EO-N-5-24"], "V"),
        ([link("flagged-for-review", "Flagged for Review", s), "Everything that is unverified, assumed, irregular or needs the owner's own documents."], ["CDI-SHOP", "SCC-TAXRATEBOOK-2025"], "U"),
        ([link("sources", "Sources", s), "Every official page used, with the exact passage relied on, for manual review."], ["IRS-ESTATE", "BOE-LTA-2026-026"], "V"),
        ([link("methodology", "Method and privacy", s), "How the model works, every assumption, and how personal information is kept out."], ["CBO-OUTLOOK-2026", "FRED-SERIES"], "A"),
    ]
    body += table(["Section", "What it answers"], rows)
    return page(out, s, "Overview",
                "A decision guide for a home that will be inherited through a trust between 2040 and 2050, kept side by side with a rental building the inheritor already owns. Every figure links to the official source it rests on.",
                body)


def p_summary(out):
    s = "executive-summary"
    o = BY[T0]
    body = """
<div class="answer">
<p><strong>1. Keep Property B.</strong> It pays about %s a year in rent, its property tax is about %s a year because its taxable value was set long ago,
and the owners can live in the third unit. If it were reassessed today its tax would be about %s a year. None of that survives a sale.</p>
<p><strong>2. Sell Property A after inheriting it.</strong> Inheritance resets both its property-tax value (bad for keeping) and its income-tax basis (good for selling).
A prompt sale turns about %s (projected for %d) into about %s after selling costs, with little or no capital gains tax.</p>
<p><strong>3. Invest the proceeds for growth.</strong> In a stock index fund the projected result after %d years is %s in today's dollars, against %s for renting the house out and %s for living in it.</p>
<p><strong>4. If the family wants to live in Property A, that is affordable but costs about %s of future wealth</strong> (today's dollars, %d years) — and to keep the partial property-tax break a child must move in within one year and file two forms.</p>
<p><strong>5. Renting Property A out is the weakest use of it.</strong> In %d the rent would be about %s, but property tax alone would take %s of it.</p>
</div>
<h2>Key facts</h2>
""" % (money(C["rent_b"]), money(PB[2026]["ptax"]), money(PB[2026]["reassessed_tax"]),
       money(o["value_T"]), T0, money(o["net_proceeds"]), H0, money(V["stocks"]["sell_real"]), money(V["stocks"]["rent_real"]), money(V["stocks"]["live_real"]),
       money(V["stocks"]["sell_real"] - V["stocks"]["live_real"]), H0, FY["year"], money(FY["rent"]["rent"]), money(FY["rent"]["ptax"]))
    rows = [
        (["Two properties, two sets of rules", "Property A changes owner at death, so it is revalued for property tax and for income tax. Property B does not change owner, so it keeps both its low taxable value and its old tax basis."], ["BOE-CIO-FAQ", "IRS-INHERIT-FAQ"], "V"),
        (["Property tax reset on inheritance", "A transfer through a trust at death is a change in ownership; the county resets the value to market value as of that date."], ["BOE-CIO-FAQ"], "V"),
        (["Partial relief if a child lives there", "Only for a parent's principal residence that becomes the child's principal residence within one year; the protected amount is the old taxable value plus $1,044,586 (through February 15, 2027)."], ["BOE-LTA-2026-026", "BOE-LTA-2025-009"], "V"),
        (["No relief if it is rented", "The exclusion for property other than a principal residence was eliminated."], ["BOE-PROP19"], "V"),
        (["Income-tax basis resets to market value", "The basis of inherited property is generally its fair market value on the date of death, so a prompt sale has little gain."], ["IRS-INHERIT-FAQ"], "V"),
        (["California taxes gains as ordinary income", "There is no lower state rate for capital gains — one reason selling Property B would be costly."], ["FTB-CAPGAINS"], "V"),
        (["Federal estate tax starts above $15,000,000 per person (2026)", "It rises to $15,480,000 in 2027 and is indexed after that; the rate above it is 40%."], ["IRS-ESTATE", "IRS-RP-2026-35", "IRS-I706"], "V"),
        (["California has no inheritance or estate tax", "State law bars the state and every city and county from imposing one."], ["CA-RTC-13301", "CA-SCO-ESTATE"], "V"),
        (["Property A's tax in %d" % T0, "%s before inheritance; %s if a child moves in; %s if rented or empty." % (money(o["ptax_before"]), money(o["ptax_live"]), money(o["ptax_rent"]))], ["BOE-LTA-2026-026", "SCC-TAXRATEBOOK-2025"], "P"),
        (["Wealth after %d years, in 2026 dollars" % H0, "Sell and hold stocks %s · rent out %s · live in %s. With Treasuries instead of stocks: sell %s · rent %s · live %s." % (
            money(V["stocks"]["sell_real"]), money(V["stocks"]["rent_real"]), money(V["stocks"]["live_real"]),
            money(V["treasuries"]["sell_real"]), money(V["treasuries"]["rent_real"]), money(V["treasuries"]["live_real"]))], ["IRS-RP-2026-35", "FTB-RATES-2025", "CBO-61912"], "P"),
        (["Break-even points", "Selling stops being best if stocks return less than %s a year, or if Property A's value grows faster than %s a year (%s if the proceeds sit in Treasuries)." % (
            pct(BE["stock_return"]), pct(BE["home_growth_vs_stocks"]), pct(BE["home_growth_vs_treasuries"]))], ["FRED-SERIES", "ERP-B56"], "P"),
        (["Real history, replayed", "Across %d replays of 1977–2025, selling into stocks was best in %s; selling into Treasuries was best in only %s — keeping the house as a rental beat bonds in most of history." % (
            len(R["replay"]), pct(RW["stocks"]["wins"]["sell"] / 100.0, 0), pct(RW["treasuries"]["wins"]["sell"] / 100.0, 0))], ["FRED-SERIES", "ERP-B55", "ERP-B56"], "P"),
        (["Estate tax room in %d" % T0, "Projected exclusion %s less the house %s leaves about %s for cash and other assets under one parent's exclusion." % (
            money(EST[T0]["exclusion"]), money(EST[T0]["house"]), money(EST[T0]["room"]))], ["IRS-RP-2026-35", "IRS-ESTATE"], "P"),
    ]
    body += table(["Fact", "What it means here"], rows)
    body += """
<h2>What to do, in order</h2>
<ol class="steps">
<li><strong>Now:</strong> confirm the trust is a revocable living trust that holds title to Property A and that the parents' homeowners' exemption is on file. %s</li>
<li><strong>Now:</strong> add up the whole estate (house, cash, investments) and compare it with the table on %s.</li>
<li><strong>At the transfer:</strong> get a written date-of-death appraisal, send the trustee notice within 60 days, and file the county change-in-ownership statement within 150 days. %s</li>
<li><strong>Within about a year:</strong> sell Property A, or — if the family chooses to live there — move in and file the two county claims.</li>
<li><strong>Afterwards:</strong> invest the proceeds according to how much risk the household can carry; the comparison on %s shows the cost of each choice.</li>
</ol>
<h2>What could change the answer</h2>
<ul>
<li>A long stretch of poor stock returns (below about %s a year) or very strong local house prices (above about %s a year).</li>
<li>Keeping the proceeds in savings or Treasuries instead of investing for growth.</li>
<li>A change in the rules listed on %s — especially the inherited-basis rule and the Proposition 19 rules.</li>
<li>The open items on %s: the trust type, the household's tax bracket, insurance quotes and the true rent Property A would earn.</li>
</ul>
""" % (link("inheritance-process", "Steps and forms", s), link("estate-thresholds", "Estate tax thresholds", s), link("inheritance-process", "Deadlines", s),
       link("decision-analysis", "Live, rent or sell", s), pct(BE["stock_return"]), pct(BE["home_growth_vs_stocks"]),
       link("law-watchlist", "Law changes to watch", s), link("flagged-for-review", "Flagged for Review", s))
    return page(out, s, "Executive summary", "The answer first, then the facts behind it and the order of work.", body)


def p_decision(out):
    s = "decision-analysis"
    o = BY[T0]
    tax_src = ["IRS-RP-2026-35", "FTB-RATES-2025", "IRS-TC559"]
    body = """
<div class="answer"><p><strong>Result:</strong> for an inheritance in %d and a %d-year view, selling Property A and investing the proceeds leaves the household with the most wealth.
Renting it out is second; living in it is third. Property B is kept in every plan.</p></div>
<p>All amounts on this page are after federal and California income tax, after selling costs, and — unless marked "then-year dollars" — in 2026 dollars.
Each plan ends by turning everything into cash after %d years so that the three can be compared like for like.</p>
<h2>The three plans compared</h2>
""" % (T0, H0, H0)
    def r(plan, what, srcs):
        cells = ["<strong>%s</strong>" % PLAN[plan], what] + [money(V[v][plan + "_real"]) for v in ("stocks", "mix6040", "treasuries", "savings")]
        return (cells, srcs, "P")
    rows = [
        r("sell", "Sell within about a year of inheriting; pay about %s in selling costs; no gain to tax because the basis was reset; invest about %s." % (
            pct(PRM["sell_comm"]["value"] + PRM["transfer_tax"]["value"]), money(o["net_proceeds"])), ["IRS-INHERIT-FAQ", "CA-RTC-11911"] + tax_src),
        r("rent", "Keep it as a rental. Taxable value resets to full market value. Rent is taxed as ordinary income after depreciation; spare cash is invested.", ["BOE-PROP19", "IRS-P527", "HUD-FMR-FY2027"] + tax_src),
        r("live", "A child moves in within a year and claims the Proposition 19 exclusion. The unit the owners leave in Property B is rented out. Yearly shortfall comes out of savings.", ["BOE-LTA-2026-026", "BOE-HOX", "IRS-TC701"] + tax_src),
    ]
    body += table(["Plan for Property A", "What happens", "Spare cash in a stock index fund", "60% stocks / 40% Treasuries", "Treasuries", "Savings"], rows,
                  caption="Wealth produced by Property A %d years after an inheritance in %d, 2026 dollars" % (H0, T0), num=(2, 3, 4, 5))
    body += """<p><strong>One exception, in the right-hand column:</strong> if the sale proceeds would only sit in a savings account, renting the house out ends ahead of selling.
Selling is the better plan only if the money is then invested — in stocks, a mix, or at least Treasuries, whose interest California does not tax.</p>
<p>If the family lives in Property A and leaves its unit in Property B empty instead of renting it, the live-in result falls to %s.</p>
<h2 id="first-year">Why: the first full year after inheritance (%d, then-year dollars)</h2>
""" % (money(D["live_unit3_empty"]["live_real"]), FY["year"])
    lv, rn, sl = FY["live"], FY["rent"], FY["sell"]
    rows = [
        (["Live in it", "Property tax after the partial exclusion", money(-lv["ptax"])], ["BOE-LTA-2026-026", "SCC-TAXRATEBOOK-2025"], "P"),
        (["Live in it", "Insurance, upkeep, water, electricity", money(-(lv["ins"] + lv["maint"] + lv["water"] + lv["elec"]))], ["CFPB-WORKSHEET", "CBO-OUTLOOK-2026"], "P"),
        (["Live in it", "Rent from the unit left behind in Property B", money(lv["unit3"], True)], ["SF-RENT-LEARN"], "P"),
        (["Live in it", "Income tax on that rent", money(-lv["tax"])], tax_src, "P"),
        (["Live in it", "<strong>Net cash for the year</strong>", "<strong>%s</strong>" % money(lv["cash"], True)], ["BOE-LTA-2026-026"], "P"),
        (["Rent it out", "Rent collected (after %s vacancy)" % pct(PRM["vacancy"]["value"], 0), money(rn["rent"], True)], ["HUD-FMR-FY2027", "HUD-SAFMR-METHOD"], "P"),
        (["Rent it out", "Property tax on the full market value", money(-rn["ptax"])], ["BOE-PROP19", "SCC-TAXRATEBOOK-2025"], "P"),
        (["Rent it out", "Insurance and upkeep", money(-(rn["ins"] + rn["maint"]))], ["CFPB-WORKSHEET"], "P"),
        (["Rent it out", "Income tax (depreciation shelters the small profit)", money(-rn["tax"])], ["IRS-P527"] + tax_src, "P"),
        (["Rent it out", "<strong>Net cash for the year</strong>", "<strong>%s</strong>" % money(rn["cash"], True)], ["BOE-PROP19"], "P"),
        (["Sell and reinvest", "Cash invested after selling costs", money(sl["proceeds"])], ["IRS-INHERIT-FAQ", "CA-RTC-11911"], "P"),
        (["Sell and reinvest", "Dividends received in the year", money(sl["income"], True)], ["ERP-B56"], "P"),
        (["Sell and reinvest", "Income tax on those dividends", money(-sl["tax"])], tax_src, "P"),
    ]
    body += table(["Plan", "Item", "Amount"], rows, num=(2,))
    body += """
<ul>
<li><strong>Keeping the house means paying tax on a value of millions.</strong> Even with the family exclusion, the yearly bill is about %s in %d — more than four times the bill before inheritance.</li>
<li><strong>As a rental it barely pays for itself.</strong> Rent of about %s is %s of the home's value; property tax, insurance and upkeep take most of it, leaving about %s.</li>
<li><strong>Selling costs almost nothing in tax.</strong> The gain built up during the parents' ownership is never taxed, because the basis resets at death.</li>
<li><strong>The growth then comes from the investment, not the house.</strong> The projection uses %s a year for stocks against %s a year for the house; the black-swan page tests what happens when those are wrong.</li>
</ul>
<h2>Does the inheritance year matter?</h2>
<p>No. Selling is best for every year from 2040 to 2050. Later years only make every figure larger.</p>
""" % (money(lv["ptax"]), FY["year"], money(rn["rent"]), pct(rn["rent"] / PA[FY["year"]]["value"]), money(rn["cash"]),
       pct(PRM["eq"]["value"], 0), pct(PRM["hpi_a"]["value"], 0))
    rows = []
    for T in range(2040, 2051):
        o2 = BY[T]
        rows.append(([str(T), money(o2["value_T"]), money(o2["net_proceeds"]), money(o2["sell_real"]), money(o2["rent_real"]), money(o2["live_real"]),
                      PLAN[o2["best"]], PLAN[o2["treasuries"]["best"]]], ["BOE-LTA-2026-026", "IRS-INHERIT-FAQ", "FRED-SERIES"], "P"))
    body += table(["Inheritance year", "Value at inheritance (then-year $)", "Cash from a sale (then-year $)", "Sell → stocks", "Rent out", "Live in", "Best", "Best if only Treasuries are used"],
                  rows, caption="Wealth %d years after inheritance, 2026 dollars" % H0, num=(1, 2, 3, 4, 5))
    body += "<h2>Does the holding period matter?</h2><p>The longer the view, the wider the gap. Over only five years the three plans are close, because selling costs are paid up front.</p>"
    rows = []
    for o2 in D["by_horizon"]:
        t = o2["treasuries"]
        rows.append((["%d years" % o2["H"], money(o2["sell_real"]), money(o2["rent_real"]), money(o2["live_real"]), PLAN[o2["best"]],
                      money(t["sell_real"]), money(t["rent_real"]), money(t["live_real"]), PLAN[t["best"]]], ["IRS-TC701", "IRS-TC409", "CBO-61912"], "P"))
    body += table(["Years after a %d inheritance" % T0, "Sell → stocks", "Rent out", "Live in", "Best", "Sell → Treasuries", "Rent out", "Live in", "Best"], rows,
                  caption="2026 dollars. Left: spare cash in stocks. Right: spare cash in Treasuries.", num=(1, 2, 3, 5, 6, 7))
    body += """<h2>Break-even points</h2>
<p>These are the values at which selling stops being the best plan, with everything else unchanged.</p>"""
    rows = [
        (["Stock return below which selling no longer wins", pct(BE["stock_return"]), "The planning figure is %s. From 1977 to 2025 the S&amp;P 500 with dividends returned 11.6%% a year; from 2000 to 2012 only 1.6%%." % pct(PRM["eq"]["value"], 0)], ["ERP-B55", "ERP-B56"], "P"),
        (["Home price growth above which keeping the house wins (proceeds in stocks)", pct(BE["home_growth_vs_stocks"]), "The planning figure is %s. San Jose-area prices grew 3.0%% a year over 2005–2025 and 6.7%% a year over 1977–2025." % pct(PRM["hpi_a"]["value"], 0)], ["FRED-SERIES"], "P"),
        (["Home price growth above which keeping the house wins (proceeds in Treasuries)", pct(BE["home_growth_vs_treasuries"]), "Close to the planning figure: with bonds only, the decision is a near tie and history favours the house."], ["FRED-SERIES", "CBO-61912"], "P"),
    ]
    body += table(["Break-even", "Value", "Compare with"], rows, num=(1,))
    body += "<h2>Home growth against stock returns</h2><p>Best plan for each combination (wealth after %d years, 2026 dollars).</p>" % H0
    rows = []
    for g in D["grid"]:
        rows.append(([pct(g["hpi"]), pct(g["eq"]), money(g["sell_real"]), money(g["rent_real"]), money(g["live_real"]), "<strong>%s</strong>" % PLAN[g["best"]]],
                     ["FRED-SERIES", "ERP-B56"], "P"))
    body += table(["Home price growth a year", "Stock return a year", "Sell → stocks", "Rent out", "Live in", "Best"], rows, num=(0, 1, 2, 3, 4))
    body += "<h2>Sensitivity: one change at a time</h2><p>Selling stays best in every single-change test below.</p>"
    rows = []
    for x in D["sensitivity"]:
        ids = ["IRS-RP-2026-35"] if x["src"] in ("—", "ASSUMPTION") else [x["src"]]
        rows.append(([e(x["label"]), money(x["sell_real"]), money(x["rent_real"]), money(x["live_real"]), PLAN[x["best"]]], ids + (["FTB-RATES-2025"] if x["src"] in ("—", "ASSUMPTION") else []), "P"))
    body += table(["Change", "Sell → stocks", "Rent out", "Live in", "Best"], rows, caption="Wealth after %d years, 2026 dollars" % H0, num=(1, 2, 3))
    b26 = PB[2026]
    body += """<h2>Property B: keep it</h2>
<p>Property B is not part of the inheritance, but it shapes the answer: it is the reason the household does not need Property A as a home or as an income property.</p>"""
    rows = [
        (["Property tax today", money(b26["ptax"]) + " a year", "Based on a taxable value of about %s set under Proposition 13." % money(b26["assessed"])], ["BOE-LTA-2026-002", "SF-TTX-SECURED"], "O"),
        (["Property tax if it were sold and bought back today", money(b26["reassessed_tax"]) + " a year", "The same rate on today's market value. A buyer would pay this; the current owners do not."], ["BOE-CIO-FAQ", "SF-TTX-SECURED"], "P"),
        (["Rent from two units", money(b26["rent"]) + " a year", "Rent-controlled increases are limited to 60% of Bay Area inflation (1.6% for March 2026 – February 2027)."], ["SF-RENT-RATES", "SF-RENT-LEARN"], "O"),
        (["Rent left after tax, insurance, utilities and upkeep", money(b26["net"]) + " a year", "Before income tax. About %s of the building's value, plus a home for the owners." % pct(b26["net"] / b26["value"])], ["CFPB-WORKSHEET", "SF-TTX-SECURED"], "P"),
        (["Income tax if Property B were sold", "", "Not computed: the owners' tax basis in Property B was not supplied. Any gain would be taxed federally and, in California, at ordinary rates."], ["FTB-CAPGAINS", "IRS-TC409"], "U"),
        (["Vacant third unit", "No vacancy tax", "San Francisco's Empty Homes Tax is not being collected after the September 2026 appeal ruling."], ["SF-EHT"], "V"),
    ]
    body += table(["Item", "Amount", "Note"], rows, num=(1,))
    body += """<h2>The plan</h2>
<ol class="steps">
<li>Keep Property B, keep living in its third unit, keep the two rents.</li>
<li>On inheriting Property A, order a date-of-death appraisal: it fixes the tax basis.</li>
<li>Do not move in and do not let it — list it for sale. The county bills property tax at the reassessed value until it sells, so a quick sale saves money.</li>
<li>Invest the net proceeds in a broad, low-cost stock index fund, keeping in Treasuries whatever the household may need within about five years.</li>
<li>If the family would rather live in Property A, treat the difference on this page as the price, move in within one year and file the claims on %s.</li>
</ol>""" % link("inheritance-process", "Inheritance step by step", s)
    return page(out, s, "Live in it, rent it, or sell and reinvest",
                "Three plans for Property A after it is inherited, compared after tax, with Property B kept in every case.", body)


def p_properties(out):
    s = "properties"
    a, b = INP["A"], INP["B"]
    rows = [
        (["How it is held", "Parents' home, in a trust; passes at death (planned 2040–2050)", "Already owned by the inheritor"], ["CA-COURTS-ESTATE-PLAN"], "O"),
        (["Estimated market value, November 2026", money(a["market_value_2026"]), money(b["market_value_2026"])], ["FRED-SERIES"], "O"),
        (["Taxable (assessed) value, latest", money(a["assessed"]["2026"]) + " (2026)", money(b["assessed"]["2025"]) + " (2025)"], ["BOE-LTA-2026-002"], "O"),
        (["What inheritance does to the property tax value", "Reset to market value at the date of death; partly protected only if a child makes it a principal residence", "Nothing — no change of ownership"], ["BOE-CIO-FAQ", "BOE-LTA-2026-026"], "V"),
        (["What inheritance does to the income-tax basis", "Reset to market value at the date of death", "Nothing — the old basis stays"], ["IRS-INHERIT-FAQ"], "V"),
        (["Tax on selling it", "Little or none if sold soon after inheriting", "Federal capital gains tax plus California ordinary rates on the whole gain"], ["IRS-INHERIT-FAQ", "FTB-CAPGAINS"], "V"),
        (["Income", "None today", "About %s a month from two units; third unit used by the owners" % money(b["rent_per_month_two_units"])], ["SF-RENT-RATES"], "O"),
        (["Rent rules if let", "Statewide cap of 5% plus inflation, at most 10% a year, where it applies", "San Francisco rent control: 1.6% for March 2026 – February 2027"], ["CA-AG-RENTCAPS", "SF-RENT-RATES"], "V"),
        (["Best use on the numbers", "Sell after inheriting", "Keep"], ["BOE-PROP19", "IRS-INHERIT-FAQ"], "P"),
    ]
    body = "<h2>The key distinction</h2>" + table(["", NAME_A, NAME_B], rows)
    body += """<h2>Tax history supplied by the owner</h2>
<p>Every figure is rounded to the nearest $10. This session cannot look the bills up, because that needs the address or parcel number, which are deliberately not held.
What it can do is test each year's assessed value against the official statewide inflation factor: the growth must equal the factor. %d of %d year-to-year steps match.</p>""" % (
        sum(1 for h in R["history"] if h.get("match")), sum(1 for h in R["history"] if "match" in h))
    for tag, name in (("A", NAME_A), ("B", NAME_B)):
        rows = []
        for h in R["history"]:
            if h["prop"] != tag:
                continue
            m = "" if "match" not in h else ("matches" if h["match"] else "<strong>does not match</strong>")
            rows.append(([str(h["year"]), money(h["assessed"]), "" if "growth" not in h else pct(h["growth"], 2),
                          "" if "official_factor" not in h else pct(h["official_factor"] - 1, 2), m,
                          money(h["tax"]) if h["tax"] else "", ("$%.2f" % h["tax_per_100"]) if h.get("tax_per_100") else ""],
                         ["BOE-LTA-2026-002"] + (["SF-TTX-SECURED"] if tag == "B" else ["SCC-TAXRATEBOOK-2025"]), "O"))
        body += table(["Year", "Assessed value", "Growth", "Official factor", "Check", "Property tax", "Tax per $100 of assessed value"], rows, caption=name, num=(1, 2, 3, 5, 6))
    body += "<h2>Irregularities in the supplied history</h2><p>None of these changes the decision; each is worth a look at the original bill.</p>"
    rows = []
    for i in R["history_irregular"]:
        rows.append((["Property " + i["prop"], str(i["year"]), e(i["text"]).capitalize() + ".",
                      {"same": "Likely a repeated figure in the data the owner copied from; a bill should move when the assessed value does.",
                       "jump": "Usually a change in fixed charges on the bill (parcel taxes, district charges) rather than in the value.",
                       "factor": "Small; may be a correction by the assessor."}[i["kind"]]],
                     ["BOE-LTA-2026-002", "SF-TTX-SECURED"] if i["prop"] == "B" else ["BOE-LTA-2026-002", "SCC-TAXRATEBOOK-2025"], "O"))
    body += table(["Property", "Year", "What looks odd", "Likely reason"], rows)
    body += """<p>The tax per $100 is higher than the published rate because every bill also carries fixed charges that do not depend on value:
about %s a year on Property A and about %s on Property B, backed out of the latest bills.</p>""" % (money(C["fix_a_2025"]), money(C["fix_b_2025"]))
    return page(out, s, "The two properties", "One home will be inherited; one building is already owned. The law treats them in opposite ways, and that difference drives the whole plan.", body)


def p_projections(out):
    s = "projections"
    body = """<p>Baseline projection with an inheritance in %d. Property A is shown under the parents' taxable value until then; afterwards two columns show its
taxable value and tax if a child lives in it (Proposition 19 partial exclusion) or if it is rented or left empty (full reassessment). Amounts are in then-year dollars, rounded to $10.</p>
<h2>Assumptions behind the tables</h2>""" % T0
    keys = ["infl", "hpi_a", "hpi_b", "p13_cap", "rate_a", "rate_b", "x19_2026", "hox", "maint_a_pct", "maint_b_pct", "sf_rent_share"]
    rows = []
    for k in keys:
        p = PRM[k]
        val = pct(p["value"], 3 if "rate_" in k else 1) if p["unit"] in ("rate", "share") else money(p["value"])
        st = "A" if (p["src"] == "ASSUMPTION" or "ASSUMPTION" in p["note"]) else "V"
        rows.append(([e(p["note"]), val], [p["src"]] if p["src"] != "ASSUMPTION" else ["CBO-OUTLOOK-2026"], st))
    body += table(["Assumption", "Value"], rows, num=(1,))
    body += "<h2>%s</h2>" % NAME_A
    rows = []
    for y in range(2026, 2077):
        r = PA[y]
        if r["phase"] == "before":
            cells = [str(y), money(r["value"]), money(r["assessed"]), money(r["ptax"]),
                     money(r.get("assessed_live")) if y == T0 else "", "", money(r.get("assessed_rent")) if y == T0 else "", ""]
        else:
            cells = [str(y), money(r["value"]), "", "", money(r["assessed_live"]), money(r["ptax_live"]), money(r["assessed_rent"]), money(r["ptax_rent"])]
        cells += [money(r["ins"]), money(r["water"]), money(r["elec"]), money(r["maint"])]
        rows.append((cells, ["BOE-LTA-2026-002", "BOE-LTA-2026-026", "CBO-OUTLOOK-2026"] if y >= T0 else ["BOE-LTA-2026-002", "CBO-OUTLOOK-2026"], "O" if y == 2026 else "P"))
    body += table(["Year", "Market value", "Assessed value (parents)", "Property tax (parents)", "Assessed value if a child lives in it", "Property tax if lived in",
                   "Assessed value if rented", "Property tax if rented", "Insurance", "Water", "Electricity (solar credit)", "Upkeep"], rows,
                  caption="Inheritance in %d: the value is reset in that row and taxed at the new value from the next year" % T0, num=tuple(range(1, 12)))
    body += """<p>The electricity column keeps the owner's reported solar credit for the whole period. That is unlikely to hold after the solar tariff's 20-year
protection ends — see %s.</p><h2>%s</h2>""" % (link("operating-costs", "Running costs", s), NAME_B)
    rows = []
    for y in range(2026, 2077):
        r = PB[y]
        rows.append(([str(y), money(r["value"]), money(r["assessed"]), money(r["ptax"]), money(r["ins"]), money(r["water"]), money(r["elec"]),
                      money(r["maint"]), money(r["rent"]), money(r["net"])], ["BOE-LTA-2026-002", "SF-TTX-SECURED", "SF-RENT-LEARN"], "P"))
    body += table(["Year", "Market value", "Assessed value", "Property tax", "Insurance", "Water", "Electricity", "Upkeep", "Rent from two units", "Rent left after these costs"], rows,
                  caption="Property B does not change owner, so its assessed value keeps rising by at most 2% a year", num=tuple(range(1, 10)))
    body += "<h2>The inheritance year, 2040 to 2050</h2><p>What the reset looks like in each possible year.</p>"
    rows = []
    for T in range(2040, 2051):
        o = BY[T]
        rows.append(([str(T), money(o["value_T"]), money(o["fbyv_T"]), money(o["x19_T"]), money(o["assessed_live_T"]), money(o["ptax_before"]), money(o["ptax_live"]), money(o["ptax_rent"])],
                     ["BOE-LTA-2026-026", "BOE-LTA-2025-009", "SCC-TAXRATEBOOK-2025"], "P"))
    body += table(["Year", "Market value", "Parents' taxable value", "Proposition 19 allowance", "New taxable value if a child lives in it", "Tax before", "Tax if lived in", "Tax if rented"], rows, num=tuple(range(1, 8)))
    body += """<p>How the allowance is projected: the law adjusts it every second February by the previous calendar year's change in the California house price index,
so it grows at about half the pace of prices. New taxable value = parents' taxable value + (market value − parents' taxable value − allowance).</p>"""
    return page(out, s, "Year-by-year projections", "House value, assessed value, property tax, insurance, water, electricity and upkeep for both properties, every year from 2026 to 2076.", body)


def p_costs(out):
    s = "operating-costs"
    a, b = INP["A"], INP["B"]
    body = """<div class="warn"><strong>Insurance could not be priced from an official source.</strong> The California Department of Insurance publishes a premium survey, but it only
returns figures after choosing a location, coverage amount and home age in an interactive tool, and it does not publish averages by ZIP code. The owner's own estimates are used
and flagged. Because the two homes need different policies — an owner-occupied homeowners policy for Property A, a landlord (rental dwelling) policy for Property B — quotes should be requested separately.</div>
<h2>%s</h2>""" % NAME_A
    rows = [
        (["Home insurance (owner-occupied policy)", money(a["insurance_per_year_owner_estimate"]) + " a year (owner unsure)", "", "Owner's figure, rising with inflation. Tested at three times this amount: the decision does not change."], ["CDI-SHOP"], "U"),
        (["Water", "%s–%s a month" % (money(a["water_per_month"][0]), money(a["water_per_month"][1])), "", "Midpoint, %s a year, rising with inflation." % money(C["water_a"])], ["CBO-OUTLOOK-2026"], "O"),
        (["Electricity", "Credit of %s–%s a month (solar)" % (money(-a["electricity_per_month"][1]), money(-a["electricity_per_month"][0])),
          "Average California household bill: $160.86 a month in 2024", "Owner's credit kept, %s a year. Flagged: see solar row." % money(C["elec_a"])], ["EIA-T5A-2024"], "O"),
        (["Solar tariff", "Installed; date not supplied", "Older net-metering customers keep their tariff for 20 years from connection; the protection currently stays with the system when ownership changes",
          "If the 20 years end before the inheritance, expect a normal bill instead of a credit — roughly %s a year more at the 2024 state average." % money(round(160.86 * 12 / 10) * 10 - C["elec_a"])], ["CPUC-NEM", "CPUC-EO-N-5-24"], "V"),
        (["Upkeep and repairs", "Lower than Property B (no amount)", "Rule of thumb: 1%% of the home's price a year = %s" % money(0.01 * a["market_value_2026"]),
          "Half the rule, %s a year in 2026 dollars, because the owner reports it is the cheaper home to maintain. Tested at the full 1%%." % money(C["maint_a"])], ["CFPB-WORKSHEET"], "A"),
        (["Property tax", money(a["tax"]["2025"]) + " (2025 bill)", "County rates run from about 1.147% to 1.241% of assessed value, plus fixed charges",
          "Rate of %s plus fixed charges of %s." % (pct(PRM["rate_a"]["value"], 2), money(C["fix_a_2025"]))], ["SCC-TAXRATEBOOK-2025"], "O"),
        (["Rent it could earn", "Not supplied", "HUD fair market rent, 4 bedrooms, metro area: $4,688 a month; a ZIP-level figure can be at most 150% of that",
          "%s a month in 2026 dollars (midpoint). Tested at both ends." % money(PRM["rent_a_month"]["value"])], ["HUD-FMR-FY2027", "HUD-SAFMR-METHOD"], "A"),
    ]
    body += table(["Cost", "Owner's figure", "Official benchmark", "Used in the model"], rows)
    body += "<h2>%s</h2>" % NAME_B
    rows = [
        (["Insurance (rental-property policy)", money(b["insurance_per_year_owner_estimate"]) + " a year (owner unsure)", "", "Owner's figure, rising with inflation. A three-unit rental normally needs a landlord policy with liability cover; request quotes."], ["CDI-SHOP"], "U"),
        (["Water and sewer, all three units", "%s–%s a month" % (money(b["water_per_month"][0]), money(b["water_per_month"][1])),
          "City rates were reset on July 1, 2026 and will be again on July 1, 2027", "Midpoint, %s a year, rising with inflation." % money(C["water_b"])], ["SFPUC-RATES-FY27"], "O"),
        (["Electricity", "%s–%s a month" % (money(b["electricity_per_month"][0]), money(b["electricity_per_month"][1])), "Average California household bill: $160.86 a month in 2024",
          "Midpoint, %s a year, rising with inflation." % money(C["elec_b"])], ["EIA-T5A-2024"], "O"),
        (["Upkeep and repairs", "Higher than Property A (no amount)", "Rule of thumb: 1% of the price a year", "%s a year in 2026 dollars." % money(C["maint_b"])], ["CFPB-WORKSHEET"], "A"),
        (["Property tax", money(b["tax"]["2025"]) + " (2025 bill)", "Rate 1.18162182% for 2026-27, plus direct charges", "That rate plus fixed charges of %s." % money(C["fix_b_2025"])], ["SF-TTX-SECURED"], "O"),
        (["Rent, two units", money(b["rent_per_month_two_units"]) + " a month", "Allowed increase 1.6% (March 2026 – February 2027); 60% of Bay Area inflation", "%s a year, rising by 60%% of inflation." % money(C["rent_b"])], ["SF-RENT-RATES", "SF-RENT-LEARN"], "O"),
        (["Third unit, if the owners move out", "Not rented today", "A new tenancy in an empty rent-controlled unit can start at any rent", "%s a year in 2026 dollars: the average of the other two units." % money(C["unit3"])], ["SF-RENT-LEARN"], "A"),
    ]
    body += table(["Cost", "Owner's figure", "Official benchmark", "Used in the model"], rows)
    body += """<h2>Running costs in the year after inheritance (%d)</h2>""" % FY["year"]
    lv, rn = FY["live"], FY["rent"]
    rows = [
        (["Property A, lived in", money(lv["ptax"]), money(lv["ins"]), money(lv["water"]), money(lv["elec"]), money(lv["maint"]), money(lv["ptax"] + lv["ins"] + lv["water"] + lv["elec"] + lv["maint"])], ["BOE-LTA-2026-026", "CFPB-WORKSHEET"], "P"),
        (["Property A, rented out (tenant pays utilities)", money(rn["ptax"]), money(rn["ins"]), "", "", money(rn["maint"]), money(rn["ptax"] + rn["ins"] + rn["maint"])], ["BOE-PROP19", "CFPB-WORKSHEET"], "P"),
        (["Property B", money(PB[FY["year"]]["ptax"]), money(PB[FY["year"]]["ins"]), money(PB[FY["year"]]["water"]), money(PB[FY["year"]]["elec"]), money(PB[FY["year"]]["maint"]),
          money(sum(PB[FY["year"]][k] for k in ("ptax", "ins", "water", "elec", "maint")))], ["SF-TTX-SECURED", "CFPB-WORKSHEET"], "P"),
    ]
    body += table(["", "Property tax", "Insurance", "Water", "Electricity", "Upkeep", "Total"], rows, num=(1, 2, 3, 4, 5, 6))
    body += "<p>Every year from 2026 to 2076 is on %s.</p>" % link("projections", "Year-by-year projections", s)
    return page(out, s, "Running costs", "Insurance, water, electricity, solar and upkeep: what the owner reported, what official sources say, and what the model uses.", body)
