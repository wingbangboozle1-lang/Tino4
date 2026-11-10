"""Inheritance process, law tracker, sources and flagged-for-review pages."""
from common import (ASSUM, FACTS, P19, PROJ, SOURCES, badge, esc, layout, money, pct, src_link, table)


def process():
    steps = [
        ("Before death", "Confirm the house is actually titled to the trust",
         "A trust avoids probate only for assets titled in the trust's name. Check the recorded deed, not the trust document.",
         "None — do this now", "Deed / trust certification",
         "SCC-COURTS-PROBATE"),
        ("Before death", "Make the Cupertino house the parents' principal residence, if it is not already",
         "Prop 19 relief exists only for the transferor's principal residence. Occupancy plus a filed homeowners' exemption is the evidence an assessor will look for.",
         "Before death", "Homeowners' exemption (BOE-19 or county form)",
         "SCC-HOE"),
        ("Before death", "Document the parents' basis",
         "Purchase price, closing statement and capital improvements. These records set the pre-death basis that the step-up replaces — and they prove the numbers to the IRS if audited.",
         "Ongoing", "Deeds, closing statements, receipts",
         "IRS-P551"),
        ("Before death", "Review how the trust distributes the house",
         "Outright distribution to the child, or a continuing trust with a right of occupancy? The answer changes who files the Prop 19 claim and who can claim the homeowners' exemption.",
         "Before death", "Trust instrument",
         "RTC-63.2"),
        ("Before death", "Size the estate against the federal exclusion",
         "The exclusion is $15,000,000 per person for 2026 deaths and indexed after that. Portability requires a timely Form 706 even when no tax is due.",
         "Before death", "Form 706 (portability election)",
         "IRS-I706"),
        ("At death", "Obtain certified death certificates",
         "Typically 10–15. Needed for the deed, insurance, utilities, brokerage and the assessor.",
         "First weeks", "Death certificates", "SCC-COURTS-PROBATE"),
        ("At death", "Successor trustee accepts and inventories the estate",
         "The trustee administers the trust's assets, keeps records, pays debts and files the fiduciary income tax return (Form 1041 federally; California Form 541 for the state).",
         "Immediately", "Trustee acceptance; Form 541 / 1041",
         "IRS-P559"),
        ("At death", "Establish fair market value as of the date of death",
         "A dated appraisal does double duty: it sets the new income-tax basis under §1014 and it is the market value the assessor will compare against the Prop 19 cap.",
         "Date of death", "Appraisal / date-of-death valuation",
         "IRS-P551"),
        ("At death", "File Form 706 if the estate exceeds the exclusion",
         "Due nine months after death; a six-month extension is available. No California estate tax return is required because California has no estate tax.",
         "9 months", "Form 706", "IRS-706-FILING"),
        ("Transfer", "Record the deed from the trustee to the beneficiary",
         "A trustee's deed transfers title. A preliminary change of ownership report (PCOR) is filed with the recording and triggers the assessor's review.",
         "After authority to distribute", "Trustee's deed; PCOR",
         "SCC-COURTS-PROBATE"),
        ("Transfer", "Expect a supplemental property tax bill",
         "The assessor reassesses as of the transfer date and bills the difference for the balance of the fiscal year. This arrives before any Prop 19 decision is final.",
         "Same fiscal year", "Supplemental bill", "SF-TREAS"),
        ("Transfer", "File the Prop 19 claim and prove occupancy",
         "Form BOE-19-P within three years of the transfer (or before sale to a third party), the homeowners' exemption within one year, and actual occupancy within one year. Miss the one-year occupancy/exemption steps and relief is prospective only.",
         "1 year (occupancy, exemption) / 3 years (claim)", "BOE-19-P; homeowners' exemption",
         "SCC-PROP19"),
        ("First year", "Rebuild the insurance and utility accounts",
         "A trust policy or a lapse in coverage is a common and expensive gap. The heir's policy must be in force at the transfer, and landlord coverage is a different product from homeowners.",
         "At transfer", "New policy", "CDI-HOME"),
        ("First year", "Choose: occupy, rent or sell — and record why",
         "Occupying preserves the exclusion; renting ends it from the move-out date; selling ends the question but realises gain measured from the stepped-up basis. This file's Decision Analysis quantifies all three.",
         "Within 12 months", "—", "RTC-63.2"),
    ]
    rows = []
    for phase, title, detail, deadline, form, sid in steps:
        rows.append([f"<span class='small'>{esc(phase)}</span><br><strong>{esc(title)}</strong><br>"
                     f"<span class='small'>{esc(detail)}</span>", esc(deadline), esc(form), src_link(sid)])
    tbl = table("Step by step: from the trust to the first property tax bill",
                ["Step", "Deadline", "Form / document", "Official source"], rows,
                "Deadlines are the ones that carry a tax consequence. Probate timelines are deliberately excluded: with the property "
                "titled to the trust, no probate is expected for the real property.")

    body = f"""
<section class="hero">
  <div class="eyebrow">Inheritance process</div>
  <h1>What actually happens, in order</h1>
  <p class="lede">Fourteen steps, four phases. The expensive mistakes are all deadline mistakes: the one-year occupancy and
  exemption filings that preserve Prop 19 relief, the nine-month federal estate tax return, and the decision to rent the house out
  before the exclusion has been secured.</p>
</section>

<div class="callout info">
  <div class="h">The 30-second version</div>
  <p>Trustee deeds the house to you → assessor reassesses it as of the death date → you move in within 12 months and file the
  homeowners' exemption → you file BOE-19-P within 3 years → the taxable value drops back to the parent's base plus any excess over
  the indexed $1M cap. If you rent it out instead, the reassessment stands and the exclusion never applies.</p>
</div>

{tbl}

<h2 class="anchor" id="trust">How the trust changes the picture</h2>
<ul class="tight">
  <li><strong>No probate for the real property</strong> if the deed is in the trust's name. That saves the statutory probate fees and,
  more importantly, the 12–18 months a probate can add — which matters because the Prop 19 clock starts at the transfer, not at the
  end of an estate administration.</li>
  <li><strong>The trust does not create a property tax exclusion.</strong> A trust is a title-holding device; Prop 19 is about who
  occupied the house and who occupies it next.</li>
  <li><strong>If the trust keeps the house</strong> (for example, a continuing trust with a right of occupancy), the assessor looks at
  who has the present beneficial ownership and whether the occupancy and exemption conditions are met. Get this structure reviewed
  before death, not after.</li>
  <li><strong>Trustee duties continue after death.</strong> The trustee must administer prudently, account to beneficiaries and file
  fiduciary income tax returns
  (<a class="src" href="https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?lawCode=PROB&division=9.&title=&part=4.&chapter=&article=" target="_blank" rel="noopener">Probate Code §16000 et seq.</a>).</li>
</ul>

<h2 class="anchor" id="deadlines">Deadline calendar</h2>
<div class="tablewrap"><table>
<thead><tr><th>Deadline</th><th>What is due</th><th>Consequence of missing it</th></tr></thead>
<tbody>
<tr><td><strong>Date of death</strong></td><td>Date-of-death valuation; basis is set under §1014</td><td>An appraisal obtained months later is weaker evidence and can cost real money on sale</td></tr>
<tr><td><strong>9 months</strong></td><td>Form 706 if the estate exceeds the exclusion</td><td>Penalties and interest; portability can be lost</td></tr>
<tr><td><strong>1 year</strong></td><td>Occupy the house; file the homeowners' (or disabled veterans') exemption</td><td>Prop 19 relief becomes prospective only — the reassessment stands for the period before the claim</td></tr>
<tr><td><strong>3 years</strong></td><td>File BOE-19-P, or before sale to a third party</td><td>Exclusion lost entirely</td></tr>
<tr><td><strong>Each November 1 / February 1</strong></td><td>Secured property tax installments (delinquent December 10 / April 10)</td><td>10% penalty plus fees, then tax-default</td></tr>
</tbody></table></div>

<h2 class="anchor" id="documents">Document checklist</h2>
<div class="grid g2">
  <div class="card"><h3>Before death</h3>
    <ul class="tight"><li>Recorded deed showing the trust as owner</li><li>Trust instrument and any amendments</li>
    <li>Purchase closing statement and improvement receipts</li><li>Homeowners' exemption confirmation for the residence</li>
    <li>Insurance declarations pages</li><li>Solar agreement / NEM tariff documentation</li></ul></div>
  <div class="card"><h3>After death</h3>
    <ul class="tight"><li>Certified death certificates</li><li>Date-of-death appraisal</li><li>Trustee's deed and PCOR</li>
    <li>BOE-19-P and homeowners' exemption filings (with proof of filing)</li><li>Form 706 if required; Form 541 / 1041</li>
    <li>Supplemental tax bills and payment confirmations</li><li>Boundary of coverage: new insurance policy in the heir's name</li></ul></div>
</div>
"""
    return layout("process", "Inheritance Process", body, prefix="../")


def laws():
    fed = [
        ["Federal estate tax exemption", "$15,000,000 per person (2026); $30,000,000 for a couple with portability", "IRS-ESTATE", "verified",
         "Indexed for inflation after 2026. No scheduled sunset."],
        ["Federal estate tax rate", "40% of the amount above the exclusion", "IRS-I706", "verified",
         "Applies to the estate, before distribution to heirs."],
        ["Federal inheritance tax", "None — the United States has no inheritance tax", "IRS-ESTATE", "verified",
         "No tax is imposed on a beneficiary merely for receiving assets."],
        ["Basis at death", "Fair market value at date of death", "IRS-P551", "verified",
         "This 'step-up' erases pre-death appreciation. It is the single most valuable rule in this file."],
        ["Long-term capital gains, 2026", "0% / 15% / 20% with breakpoints of $98,900 and $613,700 for MFJ", "IRS-RP2532", "verified",
         "Land sales of the house sit in the 20% band for a high-income household."],
        ["Net investment income tax", "3.8% above $250,000 MFJ / $200,000 single MAGI", "IRS-NIIT", "verified",
         "Applies to rents and to gains."],
        ["Depreciation, residential rental", "27.5 years straight line, building only", "IRS-P527", "verified",
         "A new depreciation schedule starts at the stepped-up basis."],
        ["§121 exclusion on a principal residence", "$250,000 single / $500,000 MFJ", "IRS-P523", "verified",
         "Applies if the heir lives in the house for 2 of the 5 years before sale."],
        ["Like-kind exchange", "Available for investment real property, not a principal residence", "IRS-1031", "verified",
         "A fallback if the family wants to stay in real estate rather than sell outright."],
        ["Annual gift exclusion, 2026", "$19,000 per recipient", "IRS-RP2532", "verified",
         "Useful for reducing the estate below the exclusion over time."],
    ]
    fed_tbl = table("Federal rules", ["Rule", "Current position", "Source", "Status", "Why it matters here"],
                    [[a, b, src_link(d), badge(e), f] for a, b, d, e, f in fed] if False else
                    [[r[0], r[1], src_link(r[2]), badge(r[3]), r[4]] for r in fed],
                    "Verified 10 November 2026 against the pages linked in each row.")

    ca = [
        ["California inheritance tax", "None", "SCC-COURTS-PROBATE", "verified",
         "Confirmed in the Santa Clara County Superior Court probate self-help page."],
        ["California state estate tax", "None", "SCC-COURTS-PROBATE", "verified",
         "The historic 'pick-up' tax tracked a federal credit that no longer exists. Confirm for the year of death."],
        ["Prop 13 levy", "1% plus voter-approved debt", "CA-XIIIA", "verified",
         "The county rate does the work: 1.2% planning rate in Santa Clara, 1.18162182% in San Francisco."],
        ["Prop 13 assessment cap", "2% per year", "RTC-51", "verified",
         "2026-27 factor is 1.02 — ninth straight year at the cap."],
        ["Prop 19 parent-child exclusion", "Principal residence only; child occupancy within 1 year; exemption within 1 year; claim within 3 years", "RTC-63.2", "verified",
         "The only mechanism that keeps a low base."],
        ["Prop 19 value cap", "$1,044,586 for transfers 2/16/2025–2/15/2027", "BOE-LTA25015", "verified",
         "Re-indexed every two years. With a $550k base, only the first ~$1.6M of value is protected."],
        ["Exclusion ends on move-out", "Base year value re-enrolled at market value as of transfer, grown by 2%", "RTC-63.2", "verified",
         "Renting the house out destroys the benefit."],
        ["Homeowners' exemption", "$7,000 off assessed value (~$70–$80/yr)", "SCC-HOE", "verified",
         "Small dollars, but it is also the occupancy evidence Prop 19 requires."],
        ["Statewide rent cap (AB 1482)", "5% + CPI, maximum 10%", "CIV-1947.12", "verified",
         "Relevant to Cupertino, which has no local rent ordinance."],
        ["Costa-Hawkins", "Initial rent on a new tenancy cannot be capped locally", "CIV-1954.52", "verified",
         "When a Sunset tenant leaves, the vacancy resets to market."],
        ["San Francisco rent increase", "1.6% for March 2026–February 2027", "SF-RENT", "verified",
         "Well below inflation — the reason the Sunset building's cash flow erodes over time."],
        ["California income tax", "Up to 12.3%, plus 1% above $1,000,000 = 13.3%", "RTC-17043", "verified",
         "California taxes rent and capital gains at ordinary rates."],
        ["Enacted 2026 change — SB 974", "Chapter 665, Statutes of 2026; amends R&TC §63.2 for special needs trusts", "LEG-SB974", "verified",
         "Narrow. It does not relax the principal-residence or value-cap rules."],
    ]
    ca_tbl = table("California rules", ["Rule", "Current position", "Source", "Status", "Why it matters here"],
                   [[r[0], r[1], src_link(r[2]), badge(r[3]), r[4]] for r in ca])

    local = [
        ["Santa Clara County planning rate", "1.2% of assessed value", "SCC-FAQ", "verified", "Cupertino base rate in the model."],
        ["San Francisco secured rate 2026-27", "1.18162182%", "SF-TREAS", "verified", "San Francisco base rate in the model."],
        ["San Francisco transfer tax, $1M–$5M", "0.75% of consideration", "SF-ASSESSOR-TT", "verified", "≈$13,500 on a $1.8M sale; not triggered by an inheritance."],
        ["Cupertino direct charges", "≈$730/yr implied from the tax series", "", "flagged", "Residual after the 1.2% ad valorem component; confirm on the bill."],
        ["San Francisco direct charges / parcel taxes", "≈$1,089/yr implied from the tax series", "", "flagged", "Residual after the 1.18162182% component; unusually large — confirm on the bill."],
    ]
    loc_tbl = table("Local rules and rates", ["Item", "Current position", "Source", "Status", "Note"],
                    [[r[0], r[1], src_link(r[2]) if r[2] else "<span class='small'>no official source</span>", badge(r[3]), r[4]] for r in local])

    watch = table("What is being discussed, and what it would do",
                  ["Item", "Status", "Effect if enacted", "Where to watch"],
                  [["Federal exclusion after 2026", "<span class='badge b-neutral'>Enacted — indexed</span>",
                    "OBBBA set $15M for 2026 and indexes it; no sunset. A future Congress could reduce it. Each $5M reduction would add up to $2M of tax on a $20M estate.",
                    "<a class='src' href='https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax' target='_blank' rel='noopener'>IRS estate tax page</a>"],
                   ["California estate / inheritance tax", "<span class='badge b-neutral'>No bill verified</span>",
                    "Would be a new tax; nothing was enacted or verified in this window. Not modelled.",
                    "<a class='src' href='https://leginfo.legislature.ca.gov/' target='_blank' rel='noopener'>California Legislative Information</a>"],
                   ["Split-roll / Prop 13 changes for commercial property", "<span class='badge b-neutral'>No change to residential</span>",
                    "Residential owner-occupied and small-rental property has not been reassessed by any verified enacted measure. Not modelled.",
                    "<a class='src' href='https://boe.ca.gov/proptaxes/changeownership.htm' target='_blank' rel='noopener'>BOE change in ownership</a>"],
                   ["Prop 19 amendments", "<span class='badge b-neutral'>One enacted (SB 974)</span>",
                    "Special needs trusts now qualify as an eligible medium of transfer. No change to the occupancy or value-cap rules.",
                    "<a class='src' href='https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202520260SB974' target='_blank' rel='noopener'>SB 974 status</a>"]],
                  "Only enacted law is used in any projection. Anything under discussion is listed here and nowhere else.")

    estate_rows_html = "".join(
        f"<tr><td>{e['year']}</td><td class='num'>{money(e['exclusion'])}</td>"
        f"<td class='num'>{money(e['tax_on_20m'])}</td><td class='num'>{money(e['tax_on_30m'])}</td></tr>"
        for e in PROJ["estate"])

    body = f"""
<section class="hero">
  <div class="eyebrow">Law tracker</div>
  <h1>The rules that decide this, at three levels of government</h1>
  <p class="lede">Every row links to the government page it came from. Rows without an official source are marked
  <span class="badge b-bad">Flagged</span> rather than filled in.</p>
</section>

<div class="callout ok">
  <div class="h">How much can be inherited before a death tax applies?</div>
  <p><strong>Federal:</strong> up to {money(15000000)} for a 2026 death, per person, indexed afterwards. Above that, 40% of the
  excess is payable by the estate. <strong>California:</strong> no limit, because there is no California estate or inheritance tax.
  A couple with portability starts at {money(30000000)}.
  <span class="small">Sources: <a class="src" href="https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax" target="_blank" rel="noopener">IRS</a>,
  <a class="src" href="https://santaclara.courts.ca.gov/self-help/self-help-topics/self-help-probate/self-help-probate-property-transfers/administering-probate-estate-after-appointment" target="_blank" rel="noopener">Santa Clara Superior Court</a>.</span></p>
</div>

<h2 class="anchor" id="federal">Federal</h2>
{fed_tbl}

<h2 class="anchor" id="california">California</h2>
{ca_tbl}

<h2 class="anchor" id="local">Local</h2>
{loc_tbl}

<h2 class="anchor" id="estate">Inheritance thresholds in practice</h2>
<p>The federal estate tax is imposed on the <em>estate</em>, not on each beneficiary, so "how much can be inherited tax-free"
really means "how large can the estate be". The 2026 figure is $15,000,000 per person and it is indexed after that. On the
model's 2.5% indexing assumption:</p>
<div class="tablewrap"><table>
<thead><tr><th>Year of death</th><th>Exclusion (projected)</th><th>Estate of $20M — federal tax</th><th>Estate of $30M — federal tax</th></tr></thead>
<tbody>
{estate_rows_html}
</tbody></table></div>
<p class="tnote">2026 is verified. Later years apply an assumed 2.5% annual indexation — the statute indexes the amount, but the
future figures have not been published. California adds nothing on top.</p>

<h2 class="anchor" id="watch">Changes under discussion</h2>
{watch}

<h2 class="anchor" id="scenario">What would change the decision</h2>
<ul class="tight">
  <li><strong>A cut to the federal exclusion</strong> would raise estate tax but not change which house strategy is better — the
  houses would be a smaller share of a taxable estate, and liquidity would become more valuable. That argues for selling, not holding.</li>
  <li><strong>Any reinstated California estate tax</strong> would do the same, with a larger effect, because California has the
  largest concentration of high-value homes.</li>
  <li><strong>Tighter rent control in San Francisco</strong> (or repeal of Costa-Hawkins vacancy decontrol) would reduce the
  Sunset building's value and push toward Scenario D in the Decision Analysis.</li>
  <li><strong>Any weakening of Prop 19</strong> would make the Cupertino base worthless on transfer and remove the main reason to
  occupy the house. Nothing verified suggests this is pending.</li>
</ul>
"""
    return layout("laws", "Law Tracker", body, prefix="../")


def sources():
    rows = [[s["id"], esc(s["publisher"]), f"<a href='{s['url']}' target='_blank' rel='noopener'>{esc(s['title'])}</a>",
             esc(s["covers"])] for s in SOURCES.values()]
    src_tbl = table("Source registry — every row on this site resolves to one of these",
                    ["ID", "Publisher", "Document", "What it was used for"], rows,
                    f"{len(SOURCES)} primary sources, all retrieved {PROJ['meta']['retrieved']}. Each was opened and read; links are "
                    "checked automatically by <code>tools/check_links.py</code> before every publish.")

    facts_rows = [[f["id"], esc(f["group"]), esc(f["metric"]), esc(f["value"]), src_link(f["source"]), badge(f["status"])]
                  for f in FACTS]
    facts_tbl = table("Verification record — every factual claim, line by line",
                      ["ID", "Group", "Claim", "Value used", "Source", "Status"], facts_rows,
                      "A blank source with an <span class='badge b-bad'>Flagged</span> or <span class='badge b-warn'>Owner-reported</span> "
                      "badge means no official source exists for that claim. Nothing was inferred to fill a gap.")

    A = ASSUM
    asm_rows = [
        ["Market appreciation", f"{pct(A['appreciation']['base'],1)} (range {pct(A['appreciation']['low'],1)}–{pct(A['appreciation']['high'],1)})",
         "Long-run nominal growth for Bay Area houses. A judgement, not a forecast; the break-even table shows how much it matters."],
        ["CPI / cost inflation", f"{pct(A['inflation']['cpi_base'],1)} (range {pct(A['inflation']['cpi_low'],1)}–{pct(A['inflation']['cpi_high'],1)})",
         "Drives charges, rent growth, housing rent and deflation to today's dollars."],
        ["Portfolio return, after tax", f"{pct(A['investment']['after_tax_nominal_base'],1)} (range {pct(A['investment']['low'],1)}–{pct(A['investment']['high'],1)})",
         "A 60/40-style diversified portfolio net of tax drag. No single security is assumed."],
        ["Prop 13 factor", f"{pct(A['property_tax']['prop13_factor'],1)} every year",
         "Statutory ceiling; BOE has applied the full 2% in nine consecutive years."],
        ["Cupertino ad valorem rate", pct(A['property_tax']['cupertino_advalorem_base'],2),
         "Santa Clara County planning guidance (1.2%). Observed effective rate is 1.33%; see flagged items."],
        ["San Francisco ad valorem rate", "1.18162182%", "Published FY 2026-27 secured rate."],
        ["Direct charges", "$730/yr Cupertino, $1,089/yr SF, grown at CPI", "Residual between the reported bill and the statutory rate."],
        ["Prop 19 cap indexation", pct(A['prop19_cap_growth'],1), "The $1,044,586 cap is re-indexed every two years; future factors are unknown."],
        ["Estate exemption indexation", pct(A['estate_indexing'],1), "Statute indexes the $15M after 2026; the 2027+ figures are not yet published."],
        ["Selling costs", pct(A['selling_cost_pct'],1)+" of price", "Commission, escrow, title, transfer taxes other than SF's."],
        ["Cupertino transfer tax", "0.11% of price", "County documentary transfer tax convention; not independently re-verified this window."],
        ["Capital gains tax on sale", "20% federal + 3.8% NIIT + 13.3% California = 37.1%", "Top-bracket household."],
        ["Rental income tax", "24% federal + 9.3% California + 3.8% NIIT = 37.1%, after depreciation", "Assumes passive income is fully taxed; losses are floored at zero."],
        ["Depreciation", "27.5 years, 40% of value treated as building", "IRS Pub 527 life; the 40% building split is an assumption."],
        ["Vacancy / management", "5% / 8% of gross rent", "Third-party management of the Sunset building."],
        ["Cupertino market rent", "$6,000/mo in 2026, growing with CPI", "Assumption. No official source for a specific house; sensitivity table provided."],
        ["SF third-unit market rent", "$3,600/mo in 2026, growing with CPI", "Assumption for the currently vacant unit's rent on a new tenancy."],
        ["Housing rent in Scenario D", "$4,500/mo in 2045, growing with CPI", "Assumption for replacement housing if both properties are sold."],
    ]
    asm_tbl = table("Model assumptions", ["Input", "Value", "Basis"], asm_rows,
                    "These are assumptions, not sourced facts. They are listed here so every projected dollar can be traced and challenged.")

    body = f"""
<section class="hero">
  <div class="eyebrow">Sources &amp; method</div>
  <h1>Where every number came from</h1>
  <p class="lede">The registry, the line-by-line verification record, and the complete assumption set. If you want to audit one
  figure, start here.</p>
</section>

<h2 class="anchor" id="registry">Source registry</h2>
{src_tbl}

<h2 class="anchor" id="verification">Verification record</h2>
{facts_tbl}

<h2 class="anchor" id="assumptions">Model assumptions</h2>
{asm_tbl}

<h2 class="anchor" id="method">Method</h2>
<ul class="tight">
  <li><strong>One model, no hand-typed results.</strong> <code>tools/model.py</code> holds every input and emits
  <code>data/projections.json</code>; <code>tools/build.py</code> renders the tables from that file. Change an assumption and every
  table changes consistently.</li>
  <li><strong>Rounding.</strong> All dollar outputs are rounded to the nearest $10, as requested. Percentages are shown to one or two
  decimals and are computed from unrounded values.</li>
  <li><strong>Nominal vs today's dollars.</strong> Every 2065 figure is shown in future dollars, with a deflated figure where the
  comparison would otherwise be misleading.</li>
  <li><strong>No inference.</strong> Where a value could not be sourced — insurance premiums, Cupertino water tariffs, the split of the
  bill between ad valorem tax and direct charges — the cell is left as reported or blank and flagged, never filled with a plausible number.</li>
  <li><strong>Privacy.</strong> No address, APN, owner, trustee or beneficiary identifier is stored. Parcel-level history is presented as
  an index (year, assessed value, tax) with no location beyond ZIP code.</li>
</ul>
"""
    return layout("sources", "Sources", body, prefix="../")


def flagged():
    flagged_facts = [f for f in FACTS if f["status"] in ("flagged", "reported")]
    rows = [[f["id"], esc(f["metric"]), esc(f["value"]), src_link(f["source"]), badge(f["status"]), esc(f["note"])]
            for f in flagged_facts]
    tbl = table("Unverified and flagged values", ["ID", "Item", "Value carried", "Source", "Status", "What would resolve it"],
                rows, "Nothing on this page is used as if it were verified. Each item shows the value the model carries and the evidence that would settle it.")

    body = f"""
<section class="hero">
  <div class="eyebrow">Flagged for review</div>
  <h1>What is not verified, and why</h1>
  <p class="lede">These items do not block publication, and none of them is hidden inside a table: each is reproduced here with
  the value the model carries and the evidence that would close it.</p>
</section>

<div class="callout bad">
  <div class="h">Three irregularities worth your attention first</div>
  <p><strong>1. San Francisco's effective tax rate is ~2.1% of assessed value</strong>, against a published secured rate of
  1.18162182%. That is a ~96 basis point gap — about $1,089 a year. It is plausibly parcel taxes and direct assessments, but it has
  not been reconciled to a bill.</p>
  <p><strong>2. Cupertino's effective rate is ~1.33%</strong>, above the county's 1.2% planning guidance. The 12-year series is
  internally consistent, so the rate is probably real; the split between ad valorem tax and charges is not.</p>
  <p><strong>3. Both insurance figures ($1,500/yr) are owner estimates.</strong> No agency publishes a parcel-level premium, and a
  three-unit Sunset building is a landlord policy, not a homeowners policy.</p>
</div>

{tbl}

<h2 class="anchor" id="data">Data irregularities</h2>
<div class="tablewrap"><table>
<thead><tr><th>#</th><th>Observation</th><th>Why it is irregular</th><th>How it is handled</th></tr></thead>
<tbody>
<tr><td>1</td><td>Cupertino 2026 property tax is blank in the supplied series</td>
<td>No 2026-27 bill has been issued yet</td><td>2026 tax is projected at 1.20% × $550,537 + $730, labelled projected</td></tr>
<tr><td>2</td><td>San Francisco 2025 tax rose 5.3% while assessed value rose 2%</td>
<td>Growth above the Prop 13 cap must come from rate or charge changes</td><td>Carried as reported; the residual is modelled as a charge line</td></tr>
<tr><td>3</td><td>San Francisco 2018 tax jumped 18.4%</td><td>Far above the 2% assessment cap</td><td>Flagged; no explanation available without the bill</td></tr>
<tr><td>4</td><td>Cupertino 2017 tax fell 0.5% while assessed value rose 2%</td><td>Implies a rate-area levy change</td><td>Carried as reported; supports treating part of the bill as a fixed charge</td></tr>
<tr><td>5</td><td>San Francisco electricity of $30–$70/mo for three units</td><td>Only plausible if tenants pay their own accounts</td><td>Carried as reported; noted as a possible understatement</td></tr>
<tr><td>6</td><td>Cupertino is described as the property to inherit while the family lives in San Francisco</td>
<td>Prop 19 relief requires the Cupertino house to be the <em>parents'</em> principal residence at death</td>
<td>Modelled both ways: with the exclusion, and without it (full reassessment). Flagged as the highest-value open question in the file.</td></tr>
<tr><td>7</td><td>Cash inheritance amount not supplied</td><td>Cannot be projected</td><td>Held as <code>[AMOUNT REDACTED]</code>; the estate-tax tables show tax at $10M–$30M estate sizes instead</td></tr>
</tbody></table></div>

<h2 class="anchor" id="next">What to send back</h2>
<ul class="tight">
  <li>One annual property tax bill for each property (redact the address and APN) — resolves items 1–4.</li>
  <li>Two insurance quotes per property — replaces the weakest input in the cash-flow model.</li>
  <li>Which property is the parents' principal residence, and whether a homeowners' exemption is filed there — resolves item 6, the
  highest-value open question.</li>
  <li>The size of the cash inheritance, in bands if preferred — turns the estate-tax tables into a single answer.</li>
</ul>
"""
    return layout("flagged", "Flagged for Review", body, prefix="../")
