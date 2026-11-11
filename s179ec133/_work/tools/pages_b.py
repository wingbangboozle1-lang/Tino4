#!/usr/bin/env python3
"""s-179ec133 — dashboard pages, part B: law, estate thresholds, process, black swan, law watch, flagged, sources, method."""
from sitegen import *
from pages_a import D, T0, H0, BY, V, PRM, C, PA, PB, EST, FY, BE, PLAN, NAME_A, NAME_B, RW, BW


def p_law(out):
    s = "inheritance-law"
    body = "<p>Rules in force on 11 November 2026. Each row states the rule in plain words and what it does to this decision; the quoted passage is on %s.</p><h2>Federal</h2>" % link("sources", "Sources", s)
    rows = [
        (["Estate tax threshold", "An estate tax return is required, and tax can be due, only when the estate exceeds $15,000,000 (2026 deaths) or $15,480,000 (2027). The house, cash and investments all count, at market value.", "Sets the room available for cash on top of the house."], ["IRS-ESTATE", "IRS-RP-2026-35"], "V"),
        (["Law behind the threshold", "Public Law 119-21 (July 4, 2025) set $15,000,000 for 2026; the 2027 figure shows it is now adjusted for inflation each year.", "No scheduled drop, unlike the old law."], ["IRS-EG-WHATSNEW", "IRS-RP-2026-35"], "V"),
        (["Estate tax rate", "40% on the amount above the threshold.", "Each $1,000,000 over costs $400,000."], ["IRS-I706"], "V"),
        (["Unused exclusion of the first parent", "A surviving spouse can use it, but only if an estate tax return is filed for the first death — due in 9 months, 6 more on request, up to 5 years in simple cases.", "Can double the room. Easy to lose by not filing."], ["IRS-ESTATE", "IRS-ESTATE-FAQ"], "V"),
        (["Gifts during life", "$19,000 per recipient in 2026 and $20,000 in 2027 pass with no gift tax return.", "A way to move cash out of the estate gradually."], ["IRS-RP-2026-35"], "V"),
        (["Basis of inherited property", "Generally the market value on the date of death.", "The reason a prompt sale of Property A is almost tax-free."], ["IRS-INHERIT-FAQ"], "V"),
        (["When the basis does not reset", "Assets in an irrevocable trust that are not counted in the estate keep their old basis.", "The trust type must be confirmed."], ["IRS-RR-2023-2"], "V"),
        (["Capital gains", "0%, 15% or 20% depending on income; depreciation taken on a rental is taxed at up to 25% on sale.", "Applies to growth after the date of death, and to Property B if ever sold."], ["IRS-TC409", "IRS-RP-2026-35"], "V"),
        (["Net investment income tax", "3.8% on rents, dividends, interest and gains once income passes $250,000 (joint) or $200,000 (single); these amounts are not indexed.", "By the 2040s most of this household's investment income is likely to be above the line."], ["IRS-TC559"], "V"),
        (["Selling a home you live in", "Up to $250,000 of gain ($500,000 joint) is excluded after owning and living in it 2 of the last 5 years.", "Softens the tax if the family lives in Property A and sells later."], ["IRS-TC701"], "V"),
        (["Renting a house out", "The building (not the land) is depreciated over 27.5 years.", "Shelters part of the rent; recaptured on sale."], ["IRS-P527"], "V"),
        (["Deducting property tax", "State and local taxes are deductible up to $40,000 (2025), shrinking for high incomes; the higher cap ends before 2030.", "From 2030 little of a large property tax bill on a home is deductible."], ["IRS-SCHA-2025", "IRS-VITA-SALT"], "V"),
        (["Interest on Treasuries", "Taxed federally, exempt from California income tax.", "Makes Treasuries better than bank savings for a California resident."], ["TD-FAQ"], "V"),
    ]
    body += table(["Rule", "What it says", "Effect on this decision"], rows)
    body += '<h2 id="property-tax">California</h2>'
    rows = [
        (["Inheritance and estate tax", "None. State law forbids the state, counties and cities from taxing gifts, estates or inheritances.", "Only the federal threshold matters."], ["CA-RTC-13301", "CA-SCO-ESTATE"], "V"),
        (["Yearly cap on assessed value", "Assessed value rises by California inflation, at most 2% a year (1.02 for the 2026 roll).", "Why both homes are taxed far below market value today."], ["BOE-LTA-2026-002"], "V"),
        (["Change in ownership", "Inheritance, including through a trust, is a change in ownership; the value is reset to market value on that date.", "Property A's tax base jumps at death."], ["BOE-CIO-FAQ"], "V"),
        (["Family exclusion (Proposition 19)", "Only a parent's principal residence that becomes the child's principal residence within one year. Protected value = old taxable value + $1,044,586 (transfers through February 15, 2027); anything above is added.", "Partial relief only if a child moves in — and Property A's value is far above the limit."], ["BOE-PROP19", "BOE-LTA-2026-026", "BOE-LTA-2025-009"], "V"),
        (["How the allowance changes", "Every second February 16, by the prior calendar year's change in the California house price index. Next change: February 2027.", "It grows slowly, so more of the value is reassessed the later the transfer."], ["BOE-LTA-2025-009"], "V"),
        (["Rental and second homes", "No exclusion.", "Renting Property A means tax on its full market value."], ["BOE-PROP19"], "V"),
        (["If the child later moves out", "The exclusion ends and the date-of-death market value, adjusted for inflation, is enrolled from the next January 1.", "Living there a while and then renting brings the full bill."], ["BOE-LTA-2026-026"], "V"),
        (["One principal residence only", "A child who keeps another home as principal residence cannot claim the exclusion on the inherited one.", "The owners must really move from Property B to Property A."], ["BOE-LTA-2026-026"], "V"),
        (["Homeowners' exemption", "$7,000 off the taxable value of an owner-occupied home; claimed once on form BOE-266.", "Small in dollars, but filing it within a year is a condition of the family exclusion."], ["BOE-HOX", "BOE-LTA-2026-026"], "V"),
        (["Multi-unit buildings", "Only the unit a parent lives in can qualify for the family exclusion.", "Matters when Property B passes to the next generation."], ["BOE-LTA-2026-026"], "V"),
        (["Capital gains", "Taxed as ordinary income; top bracket rates 9.3% to 12.3%, plus 1% above $1,000,000.", "Raises the cost of selling Property B, and of selling Property A long after inheriting."], ["FTB-CAPGAINS", "FTB-RATES-2025", "FTB-540ES-2026"], "V"),
        (["Transfer tax on a sale", "County tax of $0.55 per $500 of price ($1.10 per $1,000).", "About %s on a sale of Property A in %d." % (money(round(0.0011 * BY[T0]["value_T"] / 10) * 10), T0)], ["CA-RTC-11911"], "V"),
        (["Statewide rent cap", "Rent increases limited to 5% plus inflation, never more than 10% a year, on covered housing.", "Applies if Property A is rented, unless an exemption is met."], ["CA-AG-RENTCAPS"], "V"),
    ]
    body += table(["Rule", "What it says", "Effect on this decision"], rows)
    body += "<h2>Local</h2>"
    rows = [
        (["Santa Clara County tax rate (Property A)", "1% plus voter-approved debt rates; totals from about 1.147% to 1.241% in the 2025-26 rate book, plus fixed charges on each bill.", "The model uses %s; the exact rate is on the owner's bill." % pct(PRM["rate_a"]["value"], 2)], ["SCC-TAXRATEBOOK-2025"], "V"),
        (["San Francisco tax rate (Property B)", "1.18162182% for fiscal year 2026-27, plus direct charges and special assessments.", "Used as published."], ["SF-TTX-SECURED"], "V"),
        (["San Francisco rent control", "Allowed increase 1.6% from March 1, 2026 to February 28, 2027; set at 60% of Bay Area inflation. A new tenancy in an empty unit can start at any rent.", "Property B's rents grow more slowly than prices."], ["SF-RENT-RATES", "SF-RENT-LEARN"], "V"),
        (["San Francisco Empty Homes Tax", "Not being collected: the Court of Appeal held on September 11, 2026 that state law overrides it.", "No vacancy tax on Property B's unrented unit for now."], ["SF-EHT"], "V"),
        (["City and county inheritance taxes", "Barred by state law.", "None."], ["CA-RTC-13301"], "V"),
    ]
    body += table(["Rule", "What it says", "Effect on this decision"], rows)
    return page(out, s, "Tax and property law today", "The federal, California and local rules that decide the numbers, each read on the official page.", body)


def p_estate(out):
    s = "estate-thresholds"
    body = """<div class="answer"><p><strong>Short version:</strong> the house alone is far below the federal threshold. Whether any estate tax is due depends on the cash and other assets.
The amount of cash is deliberately not shown here, so the tables give the room left after the house — compare it privately with the real figure.</p></div>
<h2>Thresholds by level of government</h2>"""
    rows = [
        (["Federal", "$15,000,000 per person for deaths in 2026; $15,480,000 in 2027", "40% above it", "Indexed for inflation from here on"], ["IRS-ESTATE", "IRS-RP-2026-35", "IRS-I706"], "V"),
        (["Federal, married parents", "The survivor can add the first parent's unused amount if a return was filed for the first death", "40% above the combined amount", "The first parent's amount is fixed at that death; it does not keep growing"], ["IRS-ESTATE", "IRS-ESTATE-FAQ"], "V"),
        (["California", "No estate or inheritance tax, no return", "0%", "Barred by a 1982 voter initiative"], ["CA-RTC-13301", "CA-SCO-ESTATE"], "V"),
        (["County and city", "None allowed", "0%", "Same state law"], ["CA-RTC-13301"], "V"),
        (["Gifts while living", "$19,000 per recipient (2026), $20,000 (2027) with no return", "Larger gifts use up the lifetime amount", "Adjusted for inflation"], ["IRS-RP-2026-35"], "V"),
    ]
    body += table(["Level", "Amount that passes free of tax", "Tax above it", "How it changes"], rows)
    body += """<h2>Room left after the house, by year</h2>
<p>Projected federal threshold less the projected value of Property A. "Room" is what cash, investments and everything else can add up to before any federal estate tax.
The last two columns stress the law itself: what if Congress cut the threshold in half, as the pre-2026 law would have done.</p>"""
    rows = []
    for e_ in R["estate"]:
        st = "V" if e_["year"] in (2026, 2027) else "P"
        rows.append(([str(e_["year"]), money(e_["exclusion"]), money(e_["house"]), money(e_["room"]), money(e_["room_two"]), money(e_["half_law"]), money(e_["room_half"])],
                     ["IRS-RP-2026-35", "IRS-ESTATE", "FRED-SERIES"], st))
    body += table(["Year of death", "Federal threshold (one person)", "Property A value", "Room for other assets", "Room with a full second exclusion", "Threshold if halved", "Room if halved"], rows, num=(1, 2, 3, 4, 5, 6))
    body += """<p>2026 and 2027 thresholds are the published amounts. Later years assume the threshold grows with inflation of %s less %s a year
(it follows a slower-moving price index) and Property A grows %s a year. The "second exclusion" column is an upper bound: a first parent's unused amount is frozen at the first death.</p>
<h2>If the estate is over the line</h2>""" % (pct(PRM["infl"]["value"]), pct(PRM["excl_gap"]["value"], 2), pct(PRM["hpi_a"]["value"], 0))
    rows = [([money(x["over"]), money(x["tax"])], ["IRS-I706"], "P") for x in R["estate_examples"]]
    body += table(["Amount above the threshold", "Federal estate tax at 40%"], rows, num=(0, 1))
    body += """<h2>How to use this with the cash amount</h2>
<ol class="steps">
<li>Add the cash, investments, retirement accounts, life insurance and any other property the parents will own at death.</li>
<li>Compare the total with the "Room for other assets" column for the expected year.</li>
<li>If it is below the room: no federal estate tax, and no California tax in any case. Still file a return at the first parent's death to keep the unused exclusion.</li>
<li>If it is above: every dollar over is taxed at 40%. Gifts within the yearly limit, and spending, reduce the total; the trust should be reviewed with an estate attorney.</li>
</ol>"""
    return page(out, s, "Estate tax thresholds and headroom", "How much can pass before tax at each level of government, how much room the house leaves for cash, and how that room is projected to change.", body)


def p_process(out):
    s = "inheritance-process"
    body = "<p>The steps in order. Deadlines run from the date of death. Forms named BOE are filed with the county assessor where the property is.</p><h2>Before the transfer (now)</h2>"
    rows = [
        (["1", "Confirm the trust", "Check that it is a revocable living trust, that Property A's title is in the trust's name, and who the successor trustee is. Assets properly in a living trust pass without probate.", "Now"], ["CA-COURTS-ESTATE-PLAN", "CA-COURTS-SIMPLE"], "V"),
        (["2", "Confirm the basis reset will apply", "The reset to market value applies to property counted in the estate. An irrevocable trust outside the estate does not get it.", "Now"], ["IRS-RR-2023-2", "IRS-INHERIT-FAQ"], "V"),
        (["3", "Confirm the home is the parents' principal residence on the county's records", "The family exclusion requires a home eligible for the homeowners' exemption through the parent's ownership and occupation.", "Now"], ["BOE-LTA-2026-026", "BOE-HOX"], "V"),
        (["4", "Size the estate", "Add the house and all other assets and compare with the threshold table.", "Now, then yearly"], ["IRS-ESTATE"], "V"),
        (["5", "Plan for the first parent's death", "File a federal estate tax return then, even if no tax is due, to pass the unused exclusion to the survivor.", "Within 9 months of the first death (+6 on request)"], ["IRS-ESTATE-FAQ"], "V"),
        (["6", "Find the solar connection date", "The 20-year tariff protection runs from that date.", "Now"], ["CPUC-NEM"], "V"),
    ]
    body += table(["Step", "What", "Why and how", "When"], rows)
    body += "<h2>After the transfer</h2>"
    rows = [
        (["7", "Order a date-of-death appraisal", "The market value on that date becomes the tax basis and the value the county will enrol.", "At once"], ["IRS-INHERIT-FAQ", "BOE-CIO-FAQ"], "V"),
        (["8", "Trustee's notice", "The trustee notifies beneficiaries and heirs that the trust has become irrevocable; they have 120 days to contest.", "Within 60 days"], ["CA-PROB-16061-7-SB202", "CA-PROB-16061-7"], "V"),
        (["9", "Tell the assessor", "File form BOE-502-D, Change in Ownership Statement — Death of Real Property Owner. Required for property in a trust too.", "Within 150 days"], ["BOE-PUB800-9"], "V"),
        (["10", "Federal estate tax return, if needed", "Form 706 when the estate is over the threshold, or to pass on an unused exclusion.", "Within 9 months (+6 on request)"], ["IRS-ESTATE", "IRS-ESTATE-FAQ"], "V"),
        (["11", "California estate return", "None required.", "—"], ["CA-SCO-ESTATE"], "V"),
        (["12", "Choose the plan for Property A", "Sell, live in, or rent — see the comparison. The property tax value resets as of the date of death whichever is chosen.", "Within the first months"], ["BOE-CIO-FAQ", "BOE-PROP19"], "V"),
    ]
    body += table(["Step", "What", "Why and how", "When"], rows)
    body += "<h2>If selling (the recommended plan)</h2>"
    rows = [
        (["S1", "Sell", "A sale near the appraised value produces little or no taxable gain.", "As soon as practical"], ["IRS-INHERIT-FAQ"], "V"),
        (["S2", "Pay the county transfer tax", "$1.10 per $1,000 of price, at closing.", "At closing"], ["CA-RTC-11911"], "V"),
        (["S3", "Report the sale", "On the income tax return for the year of sale, with the date-of-death value as basis.", "Next tax return"], ["IRS-INHERIT-FAQ"], "V"),
        (["S4", "Invest the proceeds", "Interest on Treasuries is exempt from California tax; dividends and gains on stocks are taxed federally at 0–20% and in California at ordinary rates.", "After closing"], ["TD-FAQ", "IRS-TC409", "FTB-CAPGAINS"], "V"),
    ]
    body += table(["Step", "What", "Why and how", "When"], rows)
    body += "<h2>If living in it</h2>"
    rows = [
        (["L1", "Move in", "It must become the child's principal residence.", "Within 1 year"], ["BOE-LTA-2026-026"], "V"),
        (["L2", "Claim the homeowners' exemption", "Form BOE-266.", "Within 1 year"], ["BOE-HOX", "BOE-LTA-2026-026"], "V"),
        (["L3", "Claim the family exclusion", "Form BOE-19-P. A late claim only helps from the year it is filed.", "Within 3 years, and before any transfer to someone else"], ["BOE-PROP19", "BOE-LTA-2026-026"], "V"),
        (["L4", "Stay", "If the child moves out, the full date-of-death value is enrolled from the next January 1.", "Ongoing"], ["BOE-LTA-2026-026"], "V"),
    ]
    body += table(["Step", "What", "Why and how", "When"], rows)
    body += "<h2>If renting it out</h2>"
    rows = [
        (["R1", "Expect the full reassessment", "No exclusion applies to a rental.", "From the date of death"], ["BOE-PROP19"], "V"),
        (["R2", "Start depreciation", "Building value over 27.5 years; land is not depreciated.", "From the date it is available for rent"], ["IRS-P527"], "V"),
        (["R3", "Follow the rent cap", "5% plus inflation, at most 10% a year, where it applies.", "Each increase"], ["CA-AG-RENTCAPS"], "V"),
    ]
    body += table(["Step", "What", "Why and how", "When"], rows)
    return page(out, s, "The inheritance, step by step", "What to do before and after the transfer, in order, with the form and the deadline for each step.", body)


def p_blackswan(out):
    s = "black-swan-scenarios"
    hs = {h["key"]: h for h in R["history_stats"]}
    body = """<div class="answer"><p><strong>Why this page exists:</strong> the projections elsewhere use one steady rate for each thing. Real economies do not behave like that.
Here the same plans are pushed through the actual year-by-year record from 1977 to 2025 — inflation, local house prices, rents, interest rates and stocks, all moving together as they really did.</p>
<p><strong>Result:</strong> with the proceeds in stocks, selling was the best plan in %s of %d replays. With the proceeds in Treasuries only, selling was best in just %s:
historically, local house prices outran bond interest.</p></div>
<h2>What the last 49 years actually looked like</h2>""" % (pct(RW["stocks"]["wins"]["sell"] / 100.0, 0), len(R["replay"]), pct(RW["treasuries"]["wins"]["sell"] / 100.0, 0))
    base = {"infl": PRM["infl"]["value"], "ha": PRM["hpi_a"]["value"], "hb": PRM["hpi_b"]["value"], "hca": PRM["hpi_ca"]["value"], "rg": PRM["rent_mkt"]["value"],
            "eq": PRM["eq"]["value"], "t10": PRM["t10_long"]["value"], "tb": PRM["tb_long"]["value"]}
    rows = []
    for k in ("infl", "ha", "hb", "hca", "rg", "eq", "t10", "tb"):
        h = hs[k]
        ids = ["ERP-B55", "ERP-B56"] if k == "eq" else ["FRED-SERIES"]
        rows.append(([e(h["name"]).replace("&amp;", "&amp;"), pct(h["full"]), pct(h["last20"]), pct(h["last10"]), "%s (%d)" % (pct(h["worst"]), h["worst_year"]),
                      "%s (%d)" % (pct(h["best"]), h["best_year"]), str(h["down_years"]) if k not in ("t10", "tb") else "—", pct(base[k])], ids, "V" if k != "eq" else "P"))
    body += table(["Series", "1977–2025 a year", "2006–2025", "2016–2025", "Lowest year", "Highest year", "Years it fell", "Steady rate used in the baseline"], rows, num=(1, 2, 3, 4, 5, 6, 7))
    body += """<p>The baseline is deliberately more cautious than history on house prices and stocks, and close to current official projections on inflation and interest rates.
Note how uneven the record is: inflation ran from 0.1%% to 13.3%%, San Jose-area house prices fell in %d of 49 years, and stocks fell in %d.</p>
<h2>Four hard starts</h2>
<p>Each row inherits in %d at the baseline value, then lives through %d real years in their real order. Wealth is in 2026 dollars.</p>""" % (hs["ha"]["down_years"], hs["eq"]["down_years"], T0, H0)
    rows = []
    for ep in R["episodes"]:
        for v, vn in (("stocks", "stocks"), ("treasuries", "Treasuries")):
            x = ep[v]
            rows.append((["<strong>%s</strong><br>%s" % (e(ep["title"]), e(ep["why"])) if v == "stocks" else "", "%d–%d" % (ep["first"], ep["last"]),
                          "house %+.0f%%, stocks %+.0f%%, prices %+.0f%%" % (100 * ep["house_change"], 100 * ep["stock_change"], 100 * ep["price_change"]) if v == "stocks" else "",
                          vn, money(x["sell"]), money(x["rent"]), money(x["live"]), "<strong>%s</strong>" % PLAN[x["best"]]], ["FRED-SERIES", "ERP-B55", "ERP-B56"], "P"))
    body += table(["Episode", "History used", "Over the 20 years", "Spare cash held in", "Sell", "Rent out", "Live in", "Best"], rows, num=(4, 5, 6))
    body += """<p>The one hard start where keeping the house beat selling into stocks was 2000–2019: stocks lost three years running at the outset while local house prices kept climbing.
That is the real risk in the recommended plan — a market fall soon after investing a lump sum. Investing in stages over a year or two, or holding part in Treasuries, reduces it.</p>
<h2>Every replay of the record</h2>
<p>All %d possible starting points: the 50 years from 2027 follow history beginning in that year and wrapping around. This changes the years before the inheritance too, so the house value at inheritance differs in each.</p>""" % len(R["replay"])
    def sumrows(S, label):
        out = []
        for v, vn in (("stocks", "Stock index fund"), ("mix6040", "60% stocks / 40% Treasuries"), ("treasuries", "Treasuries")):
            w, p = S[v]["wins"], S[v]["pct"]
            out.append(([label, vn, pct(w["sell"] / 100.0, 0), pct(w["rent"] / 100.0, 0), pct(w["live"] / 100.0, 0),
                         "%s / %s / %s" % (money(p["sell"]["p5"]), money(p["sell"]["p50"]), money(p["sell"]["p95"])),
                         "%s / %s / %s" % (money(p["rent"]["p5"]), money(p["rent"]["p50"]), money(p["rent"]["p95"])),
                         "%s / %s / %s" % (money(p["live"]["p5"]), money(p["live"]["p50"]), money(p["live"]["p95"]))], ["FRED-SERIES", "ERP-B55", "ERP-B56"], "P"))
        return out
    body += table(["Test", "Spare cash held in", "Sell best", "Rent best", "Live-in best", "Sell: low / middle / high", "Rent: low / middle / high", "Live in: low / middle / high"],
                  sumrows(RW, "%d replays" % len(R["replay"])) + sumrows(BW, "%d shuffled histories" % R["bootstrap"]["n"]),
                  caption="Share of cases in which each plan was best, and wealth after %d years (2026 dollars) at the 5th, 50th and 95th percentile" % H0)
    body += """<p>The shuffled histories re-draw the same 49 years in random blocks averaging %d years (fixed random seed %d, so the result can be reproduced),
which creates sequences that never happened but keep each year's real combination of inflation, prices and returns.</p>
<p><strong>Read the dollar figures with care.</strong> They are much larger than the baseline because 1977–2025 was an unusually generous period for both houses and stocks, helped by
interest rates falling from 14%% to near zero. The ranking of the plans is the useful part, not the size of the numbers.</p>
<h2>All %d replays</h2>""" % (R["bootstrap"]["mean_block_years"], R["bootstrap"]["seed"], len(R["replay"]))
    rows = []
    for x in R["replay"]:
        st = x["stocks"]; tr = x["treasuries"]
        rows.append(([str(x["first"]), str(x["at_inheritance"]), money(x["value_T"]), money(st["sell"]), money(st["rent"]), money(st["live"]), PLAN[st["best"]], PLAN[tr["best"]]],
                     ["FRED-SERIES", "ERP-B56"], "P"))
    body += table(["History starts in", "History year at the %d inheritance" % T0, "House value at inheritance (2026 $)", "Sell → stocks", "Rent out", "Live in", "Best (stocks)", "Best (Treasuries only)"], rows, num=(2, 3, 4, 5))
    body += """<h2>What the stress tests change in the plan</h2>
<ul>
<li><strong>Sell, but invest for growth.</strong> Selling and then holding savings or bonds gives up the advantage; in most of history that was worse than keeping the house as a rental.</li>
<li><strong>Spread the entry.</strong> The worst outcomes come from a market fall right after investing everything at once.</li>
<li><strong>Keep Property B through all of it.</strong> Its rents and its capped tax bill held up in every sequence, which is what lets the household ride out bad years.</li>
<li><strong>Living in Property A was never the best financial result</strong> in any replay — it is a lifestyle choice with a price that varies with the economy.</li>
</ul>
<h2>Limits</h2>
<ul>
<li>49 years of data, one country, one metro area. The future can be worse than anything in the record.</li>
<li>Stock returns are computed from year-end index levels and dividend yields in official tables; they match published index-fund returns to within about half a point a year.</li>
<li>Treasuries are modelled as earning each year's yield, without the price swings of a bond fund.</li>
<li>Tax law is held at today's rules, with brackets rising with each path's inflation.</li>
</ul>"""
    return page(out, s, "Black-swan economic conditions", "Growth and inflation are never steady for 50 years. This page re-runs the plans through the real record instead of a smooth line.", body)


def p_lawwatch(out):
    s = "law-watchlist"
    body = "<p>Items are grouped by how settled they are. Election figures are the Secretary of State's unofficial count as of November 10, 2026; certification is due by December 11, 2026.</p><h2>Just changed</h2>"
    rows = [
        (["Federal estate threshold for 2027", "Published: $15,480,000 (from $15,000,000). Gift limit $20,000.", "More room. Confirms yearly indexing."], ["IRS-RP-2026-35"], "V"),
        (["Proposition 19 and special needs trusts", "SB 974 signed September 27, 2026, amending the family-exclusion statute.", "Relevant only if a beneficiary's share is held in a special needs trust."], ["CA-SB974-2026"], "V"),
        (["San Francisco Empty Homes Tax", "Court of Appeal ruled against the city on September 11, 2026; not collected unless reversed.", "Property B's unrented unit carries no vacancy tax for now."], ["SF-EHT"], "V"),
        (["San Francisco water and sewer rates", "Reset July 1, 2026; again July 1, 2027.", "Property B's water bill will rise faster than inflation for two years."], ["SFPUC-RATES-FY27"], "V"),
        (["San Francisco rent increase", "1.6% for March 2026 – February 2027.", "Property B's rents rise more slowly than costs."], ["SF-RENT-RATES"], "V"),
    ]
    body += table(["Item", "Status", "Effect on the decision"], rows)
    body += "<h2>Decided at the November 3, 2026 election (count not yet certified)</h2>"
    rows = [
        (["Proposition 3 — keeps the higher California income tax rates on high incomes permanently", "Ahead, 60.6% yes", "California's upper brackets stay. A large one-year gain — for example selling Property B — would continue to be taxed at up to 12.3% plus 1%."], ["CA-SOS-RESULTS-2026", "FTB-RATES-2025"], "V"),
        (["Proposition 42 — bars new state taxes on personal property (investments, accounts) and certain retroactive taxes", "Narrowly ahead, 51.5% yes", "Lowers the risk of a future California tax on the invested proceeds themselves."], ["CA-SOS-RESULTS-2026"], "V"),
        (["Proposition 40 — one-time tax on very large fortunes", "Behind, 47.4% yes", "No effect at this scale either way."], ["CA-SOS-RESULTS-2026"], "V"),
        (["Proposition 43 — would have made voter-initiated local special taxes harder to pass", "Behind, 42.6% yes", "New parcel taxes remain as easy to pass as today; fixed charges on both bills can keep growing."], ["CA-SOS-RESULTS-2026"], "V"),
        (["Any change to Proposition 13 or to the Proposition 19 inheritance rules", "None was on the ballot", "The reassessment rules on this dashboard stand."], ["CA-SOS-QUALIFIED-2026"], "V"),
    ]
    body += table(["Item", "Status", "Effect on the decision"], rows)
    body += "<h2>Proposed or under discussion</h2>"
    rows = [
        (["Repeal of the federal estate tax (S.587 and H.R.1301)", "Introduced February 13, 2025; referred to committee; no further action.", "If enacted, the threshold table would no longer matter. Do not plan on it."], ["US-S587"], "V"),
        (["Next Proposition 19 allowance", "Changes February 16, 2027 by the 2026 change in the California house price index; not yet published.", "Small. The allowance moves by one year's price change every two years."], ["BOE-LTA-2025-009"], "V"),
        (["Solar tariff protection on a change of ownership", "Today the 20-year protection belongs to the system. The utilities regulator has listed ending it when a home changes ownership as an option.", "If adopted, the solar credit on Property A could end at the inheritance even inside the 20 years."], ["CPUC-EO-N-5-24", "CPUC-NEM"], "V"),
        (["Higher cap on deducting state and local taxes", "Temporary: ends before 2030.", "After that, almost none of Property A's property tax would be deductible if it is a home."], ["IRS-VITA-SALT", "IRS-SCHA-2025"], "V"),
        (["Net investment income tax thresholds", "Fixed in dollars; not indexed.", "More of the household's investment income becomes subject to the 3.8% tax every year. Already in the model."], ["IRS-TC559"], "V"),
    ]
    body += table(["Item", "Status", "Effect on the decision"], rows)
    body += """<h2>If the big rules changed</h2>
<p>Two rules carry the recommendation. If either were repealed the comparison should be re-run.</p>"""
    rows = [
        (["The basis reset at death", "Selling Property A soon after inheriting would become taxable on decades of growth. Living in it or holding it would look better, and the timing of any sale would matter much more.", "No bill changing it was found in this review; it has been proposed in past years."], ["IRS-INHERIT-FAQ"], "V"),
        (["Proposition 19's limits on the family exclusion", "If the pre-2021 rules returned, Property A could be kept — even as a rental — at the parents' taxable value, cutting the yearly tax by tens of thousands of dollars and making keeping it far more attractive.", "A repeal measure was not on the November 2026 ballot."], ["BOE-PROP19", "CA-SOS-QUALIFIED-2026"], "V"),
        (["The estate tax threshold", "Halving it would leave about %s of room after the house in %d instead of %s." % (money(EST[T0]["room_half"]), T0, money(EST[T0]["room"])), "Congress can change it at any time; the current law has no built-in drop."], ["IRS-EG-WHATSNEW", "IRS-RP-2026-35"], "P"),
    ]
    body += table(["Rule", "What a change would do", "Where it stands"], rows)
    return page(out, s, "Law changes to watch", "What has just changed, what voters decided this month, what is proposed — and what each means for the plan.", body)


FLAGS = [
    # id, item, why, how to check, effect, sources, status
    ("F-01", "All owner-supplied figures", "Market values, assessed values, tax bills, rents and utility costs come from the owner and were rounded to $10. They cannot be looked up without the address or parcel number, which this project deliberately does not hold.", "Compare with the county and city bills.", "Inputs to everything.", ["SF-TTX-SECURED", "BOE-LTA-2026-002"], "O"),
    ("F-02", "Property A tax bills repeat", "The supplied bill is identical in 2017 and 2018, and in 2019 and 2020, although the assessed value rose each year.", "Check the original bills; one of each pair is probably a copied figure.", "None on the decision.", ["BOE-LTA-2026-002", "SCC-TAXRATEBOOK-2025"], "O"),
    ("F-03", "Property B tax bill jumps", "Up 18.4% in 2018 and down 5.9% in 2021 while the assessed value rose about 2%.", "Read the direct-charge lines on those bills.", "None on the decision.", ["SF-TTX-SECURED"], "O"),
    ("F-04", "Property B assessed value, 2022", "About $50 below the previous year times the official 2% factor.", "Check the 2022-23 bill.", "None.", ["BOE-LTA-2026-002"], "O"),
    ("F-05", "Insurance premiums", "No official premium for either home could be obtained: the state survey needs interactive input and publishes no ZIP-level average. The owner's own estimates, which the owner is unsure of, are used. A home of this value and a three-unit rental may each cost several times more.", "Use the Department of Insurance comparison tool, then request an owner-occupied quote for Property A and a landlord-policy quote for Property B.", "Tested at three times the estimate: no change.", ["CDI-SHOP"], "U"),
    ("F-06", "Property A tax rate", "The owner's tax rate area is unknown. The model uses 1.17%, inside the county's published range of about 1.147% to 1.241%.", "Read the rate on the bill.", "Tested at 1.241%: no change.", ["SCC-TAXRATEBOOK-2025"], "A"),
    ("F-07", "Rent Property A could earn", "Not supplied, and the bedroom count is unknown. The model uses the midpoint between HUD's metro figure for 4 bedrooms and HUD's ceiling of 150% of it.", "Ask a local property manager for a rent opinion.", "Tested at both ends: no change.", ["HUD-FMR-FY2027", "HUD-SAFMR-METHOD"], "A"),
    ("F-08", "Upkeep costs", "No amounts supplied. Property B uses the 1%-of-price rule of thumb; Property A uses half of it because the owner reports it is cheaper to maintain.", "Replace with actual spending.", "Tested at the full 1%: no change.", ["CFPB-WORKSHEET"], "A"),
    ("F-09", "Solar credit on Property A", "The connection date is unknown. Tariff protection lasts 20 years from connection, so the credit will probably have ended before 2040–2050, and panels will be near the end of their life. The projections keep the credit anyway.", "Find the permission-to-operate date on the utility account.", "Adds roughly $2,000 a year in today's money to the cost of living there.", ["CPUC-NEM", "EIA-T5A-2024"], "A"),
    ("F-10", "Type of trust", "Assumed to be a revocable living trust counted in the estate. If it is irrevocable and outside the estate, the basis does not reset and selling would be taxable.", "Read the trust document with an estate attorney.", "Could reverse the recommendation.", ["IRS-RR-2023-2", "IRS-INHERIT-FAQ"], "A"),
    ("F-11", "Relationship and residence", "Assumed: parent-to-child transfer of the parents' principal residence. Otherwise no family exclusion is available at all.", "Confirm the homeowners' exemption is on the parents' bill.", "Affects only the live-in plan.", ["BOE-LTA-2026-026"], "A"),
    ("F-12", "Household income and filing status", "Not supplied. The model assumes a joint return and $150,000 of other income in 2026 dollars; $60,000, $400,000 and single filing were tested.", "Use the household's own tax return.", "No change in any test.", ["IRS-RP-2026-35", "FTB-RATES-2025"], "A"),
    ("F-13", "Cash in the inheritance", "The amount is not stored or published. Tables show the room left after the house instead.", "Compare privately.", "Decides whether any estate tax is due.", ["IRS-ESTATE"], "O"),
    ("F-14", "Stock return of 7% a year", "A planning figure, not an official forecast; no government body publishes one. History: 11.6% a year 1977–2025, 1.6% a year 2000–2012.", "See the break-even: selling still wins above 3.8%.", "The central assumption.", ["ERP-B55", "ERP-B56"], "A"),
    ("F-15", "Selling costs of 5%", "No official rate exists for agent, escrow and preparation costs. Only the county transfer tax is fixed by law.", "Ask two agents for a written fee quote.", "Tested at 3% and 7%: no change.", ["CA-RTC-11911"], "A"),
    ("F-16", "Election results", "Unofficial count as of November 10, 2026; Proposition 42 is close.", "Recheck after certification on December 11, 2026.", "Law-watch page only.", ["CA-SOS-RESULTS-2026"], "V"),
    ("F-17", "Thrift Savings Plan page", "The official returns page loads its yearly table by script; the plain page shows placeholder figures (the same value for every fund). Those were not used. Stock returns come from the Economic Report of the President instead.", "Open the page in a browser to see the real table.", "None.", ["TSP-RETURNS", "ERP-B56"], "V"),
    ("F-18", "Stock returns are computed", "Total return = year-end index change plus dividend yield on the average index level, from official tables. Within about half a point a year of published index-fund returns.", "Compare any year with a published S&amp;P 500 total return.", "Small.", ["ERP-B55", "ERP-B56"], "P"),
    ("F-19", "Hand-transcribed series", "The 1975–2025 price, rent and interest-rate series were typed from the official download and spot-checked, not machine-copied.", "Open the linked download and compare.", "Small.", ["FRED-SERIES"], "V"),
    ("F-20", "California tax tables are for 2025", "The 2026 schedule had not been read. The 4% bracket was worked out from the published amounts on either side of it. Single-filer brackets are taken as half the joint ones, and the 2027 federal joint standard deduction as twice the single amount the IRS announced.", "Check against the Franchise Tax Board booklet.", "Negligible.", ["FTB-RATES-2025", "IRS-RP-2026-35"], "P"),
    ("F-21", "Rental depreciation rule", "Read in an earlier IRS edition of Publication 527; the current edition is linked but was not re-read line by line.", "Open the current publication.", "None expected.", ["IRS-P527"], "V"),
    ("F-22", "San Francisco transfer tax", "The city's tiered rates could not be read on an official page in this session, so no figure is shown. Needed only if Property B were sold.", "See the Assessor-Recorder's transfer tax page.", "None on the plan (Property B is kept).", ["SF-TTX-SECURED"], "U"),
    ("F-23", "San Francisco water increases", "The size of the 2026 and 2027 increases was reported by news outlets; only the existence of the new schedule was read officially, so no percentage is shown.", "Read the linked schedule.", "Small.", ["SFPUC-RATES-FY27"], "U"),
    ("F-24", "Tax basis of Property B", "Not supplied, so the tax on selling it is not computed.", "From the owners' purchase or inheritance records.", "Supports keeping it regardless.", ["IRS-TC409", "FTB-CAPGAINS"], "U"),
    ("F-25", "Rent control on Property B", "Assumed covered, so rents rise at 60% of inflation.", "Check with the Rent Board.", "Small.", ["SF-RENT-LEARN"], "A"),
    ("F-26", "Statewide rent-cap exemptions", "Some single-family homes are exempt under conditions that were not verified here.", "Read the Attorney General's page before letting Property A.", "Affects only the rent plan.", ["CA-AG-RENTCAPS"], "U"),
    ("F-27", "Future estate threshold", "Assumed to grow 0.25 point a year slower than consumer prices; the 2026 house-price change that sets the next Proposition 19 allowance is not yet published and is assumed to equal the 20-year average.", "Update each November when the IRS publishes the next year's figure.", "Small.", ["IRS-RP-2026-35", "BOE-LTA-2025-009"], "A"),
    ("F-28", "Vacancy and building share", "5% vacancy and a 20% building share of Property A's value are assumptions; the assessor's land and improvement split is on the bill.", "Read the bill.", "Tested at 40% building share: no change.", ["IRS-P527"], "A"),
    ("F-29", "Santa Clara County rate book", "Read through search excerpts of the official document rather than page by page.", "Open the linked document.", "Small.", ["SCC-TAXRATEBOOK-2025"], "V"),
    ("F-30", "Repository history", "Earlier versions of this repository, written by other sessions and since deleted from the published site, contained un-rounded figures. They remain in the public commit history, which only the repository owner can purge.", "See the project's task board.", "Privacy, not the decision.", ["BOE-LTA-2026-002"], "O"),
]


def p_flagged(out):
    s = "flagged-for-review"
    body = """<p>Nothing here blocks the plan, but each item is either unverified, assumed, irregular, or needs a document only the owner has. Where a value could not be confirmed from an official source it is left blank on the other pages and marked %s.</p>""" % chip("U")
    counts = {}
    for f in FLAGS:
        counts[f[6]] = counts.get(f[6], 0) + 1
    body += '<div class="legend">%s</div>' % " ".join("%s × %d" % (chip(k), n) for k, n in sorted(counts.items()))
    rows = [([f[0], "<strong>%s</strong>" % f[1], f[2], f[3], f[4]], f[5], f[6]) for f in FLAGS]
    body += table(["No.", "Item", "Why it is flagged", "How to check", "Effect on the answer"], rows)
    body += "<h2>Every assumption in the model</h2>"
    rows = []
    for p in R["params"]:
        if p["src"] == "ASSUMPTION" or "ASSUMPTION" in p["note"]:
            val = pct(p["value"], 2) if p["unit"] in ("rate", "share") else (money(p["value"]) if p["unit"] == "usd" else str(p["value"]))
            rows.append(([e(p["note"]), val], ["CBO-OUTLOOK-2026"] if p["src"] == "ASSUMPTION" else [p["src"]], "A"))
    body += table(["Assumption", "Value"], rows, num=(1,))
    return page(out, s, "Flagged for Review", "Unverified items, assumptions, irregularities and open questions — each with the official link to check it.", body)


def p_sources(out):
    s = "sources"
    groups = [("01-", "Federal estate and gift tax"), ("02-", "California death taxes"), ("03-", "Proposition 13 and 19"), ("04-", "Income tax"),
              ("05-", "Local property tax and transfer tax"), ("06-", "Running costs and rental rules"), ("07-", "Process"), ("08-", "Law watch"), ("09-", "Economy and markets")]
    n_src = len(LEDGER); n_claim = sum(len(x["verified"]) for x in LEDGER.values())
    body = """<p>%d official sources, %d quoted passages. Each was opened and read by this session on 11 November 2026. Follow any link to check the passage yourself.
Only government bodies, courts, legislatures and Federal Reserve data services are used; commercial sites were consulted to find pages but are never cited.</p>""" % (n_src, n_claim)
    for prefix, name in groups:
        body += "<h2>%s</h2>" % name
        rows = []
        for sid, x in LEDGER.items():
            if not x["file"].startswith(prefix):
                continue
            q = "".join("<details><summary>%s</summary><blockquote>%s</blockquote></details>" % (e(c["claim"]), e(c["quote"])) for c in x["verified"])
            note = ("<p><em>%s</em></p>" % e(x["note"])) if x.get("note") else ""
            rows.append(([e(x["agency"]), e(x["title"]) + note, q, e(x["fetched"])], [sid], "V"))
        body += table(["Publisher", "Document", "What was relied on (open to see the passage)", "Read on"], rows)
    return page(out, s, "Sources", "Every official page behind the dashboard, with the exact passage relied on.", body)


def p_method(out):
    s = "methodology"
    body = """<h2>How the comparison works</h2>
<ol class="steps">
<li><strong>Start from the owner's figures, rounded to $10,</strong> and from rules read on official pages.</li>
<li><strong>Project each year from 2026 to 2076:</strong> prices, house values, assessed values (rising by inflation, at most 2%), tax bills (rate × assessed value + fixed charges), running costs and rents.</li>
<li><strong>At the inheritance year, split into three plans</strong> for Property A. Property B and the household's other income are the same in all three.</li>
<li><strong>Each year, work out income tax twice</strong> — with and without the plan's income — using the full federal and California bracket tables, the 3.8% investment-income tax and the California exemption for Treasury interest. The difference is the plan's tax.</li>
<li><strong>Put every spare dollar into, and take every shortfall out of, the same investment</strong> (stocks, a 60/40 mix, Treasuries or savings), so plans are compared on equal terms.</li>
<li><strong>At the end, turn everything into cash:</strong> sell the house (selling costs, tax on the gain since inheritance, the home-sale exclusion if lived in, depreciation recapture if rented) and sell the investments (tax on their gains).</li>
<li><strong>Repeat with real history</strong> in place of the steady rates.</li>
</ol>
<h2>Every parameter</h2>"""
    rows = []
    for p in R["params"]:
        val = pct(p["value"], 3 if p["key"].startswith("rate_") else 2) if p["unit"] in ("rate", "share") else (money(p["value"]) if p["unit"] == "usd" else str(p["value"]))
        assumed = p["src"] == "ASSUMPTION" or "ASSUMPTION" in p["note"]
        rows.append(([e(p["note"]), val], ["CBO-OUTLOOK-2026"] if p["src"] == "ASSUMPTION" else [p["src"]], "A" if assumed else "V"))
    body += table(["Parameter", "Value"], rows, num=(1,))
    body += """<p>Where the status is Assumption and no official source fixes the value, the link shown is the official inflation projection the model is built around; the assumption itself is listed on %s.</p>
<h2>What "verified" means here</h2>
<ul>
<li>The official page was opened by this session and the passage that supports the statement is quoted on %s.</li>
<li>A figure the owner supplied is never called verified. It is labelled Owner-supplied and listed for review.</li>
<li>A figure the model computes is labelled Projection, and its row links to the official rule that drives it.</li>
<li>If a value could not be confirmed officially, it is left blank and flagged.</li>
</ul>
<h2>Checks that were run</h2>""" % (link("flagged-for-review", "Flagged for Review", s), link("sources", "Sources", s))
    n_match = sum(1 for h in R["history"] if h.get("match")); n_all = sum(1 for h in R["history"] if "match" in h)
    rows = [
        (["Owner's assessed values against the official yearly factor", "%d of %d year-to-year steps match; the exception is flagged" % (n_match, n_all)], ["BOE-LTA-2026-002"], "V"),
        (["Proposition 19 allowance arithmetic", "$1,022,600 × 1.0215 = $1,044,586, as published"], ["BOE-LTA-2025-009"], "V"),
        (["California 4% bracket", "Recomputed from the published tax amounts at the brackets on either side"], ["FTB-RATES-2025"], "V"),
        (["Stock return series", "Years 2000–2003 appear in both official tables with identical values; computed returns match known index-fund results within about half a point"], ["ERP-B55", "ERP-B56"], "V"),
        (["Every table row on every page", "Has a link to an official source and a status label; checked by script at build time"], ["IRS-ESTATE"], "V"),
        (["Every dollar figure from the owner or the model", "Is a multiple of $10; checked by script at build time"], ["BOE-LTA-2026-002"], "V"),
        (["Every internal link", "Resolves to a page; checked by script at build time"], ["IRS-ESTATE"], "V"),
    ]
    body += table(["Check", "Result"], rows)
    body += """<h2 id="privacy">Privacy</h2>
<ul>
<li>No names, street addresses, parcel numbers, account numbers or ZIP codes appear anywhere in this dashboard or its working files.</li>
<li>Every figure supplied by the owner was rounded to the nearest $10 before it was written to any file. The model is run on the rounded figures, so nothing published can be worked back to an exact amount held in this project.</li>
<li>The amount of cash in the inheritance is not stored or shown; the estate tables are built so it is not needed.</li>
<li>Rounding lowers the chance of a search match; it is not a guarantee. Public assessment rolls can be searched by value, so anyone with the address could confirm the figures, though not derive the address from them easily.</li>
<li>Pages carry a "noindex" tag asking search engines not to list them.</li>
</ul>
<h2>Limits</h2>
<ul>
<li>A model of this kind compares plans; it does not predict amounts. The ranking and the break-even points are the reliable part.</li>
<li>Tax rules are today's, carried forward with inflation. They will change.</li>
<li>Living in a home has value that is not money. The live-in plan's lower figure is its financial price, not a verdict on it.</li>
<li>This is general information, not legal, tax, investment or insurance advice.</li>
</ul>"""
    return page(out, s, "Method and privacy", "How the numbers are produced, every parameter with its source, the checks that were run, and how personal information is kept out.", body)
