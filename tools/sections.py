#!/usr/bin/env python3
"""Page sections for the decision workspace. All case figures are $10-rounded."""
from __future__ import annotations

import models as M
from sitebuild import (
    CHECKED, SafeHTML, badge, callout, cards, cell, esc, make_table, paragraph,
    render_page, source_link, SOURCES,
)

MO = M.money
EX = M.money_exact
P = M.pct


def snapshot_rows() -> list[dict]:
    return [
        {"cells": [
            "Property A — suburban single-family home (Silicon Valley)",
            f"Est. market value {MO(M.A_VALUE_2026)} ({MO(M.A_VALUE_LOW)}–{MO(M.A_VALUE_HIGH)})",
            f"Factored base year value {MO(M.A_AV_2026)} (2026 roll, +2%/yr)",
            f"{MO(M.A_TAX_2026)} per year (observed ≈ {P(M.RATIO_A, 2)} of assessed value)",
        ], "status": "Owner-supplied", "sources": ["boe_pub29", "boe_prop19"]},
        {"cells": [
            "Property A — utilities and insurance",
            "Water about $100–$150 per month; rooftop solar usually nets a $10–$20 monthly credit",
            f"Insurance: owner guess {MO(M.A_INS_OWNER)} — market planning band {MO(M.A_INS_LOW)}–{MO(M.A_INS_HIGH)} per year",
            "Maintenance scenario band 0.5%–1.0% of value per year (older systems cost more; owner reports less than Property B)",
        ], "status": "Owner-supplied", "sources": ["cdi", "cpuc_solar", "water_board"]},
        {"cells": [
            "Property B — San Francisco west-side 3-unit building (already owned)",
            f"Est. market value {MO(M.B_VALUE_2026)} ({MO(M.B_VALUE_LOW)}–{MO(M.B_VALUE_HIGH)})",
            f"Assessed value {MO(M.B_AV_2025)} (2025) — deep Proposition 13 basis",
            f"{MO(M.B_TAX_2025)} per year (observed ≈ {P(M.RATIO_B, 2)} of assessed value — irregular, flagged)",
        ], "status": "Owner-supplied", "sources": ["boe_pub29", "boe_prop19"]},
        {"cells": [
            "Property B — income and costs",
            f"Two units rent for {MO(M.B_RENT_2UNITS_MO)} per month combined; a third unit is owner-occupied/available (scenario band {MO(M.B_RENT_UNIT3_LOW_MO)}–{MO(M.B_RENT_UNIT3_HIGH_MO)} per month if rented)",
            "Water about $330–$400 per month for all three units; electricity about $30–$70 per month",
            f"Insurance: owner guess {MO(M.B_INS_OWNER)} — landlord planning band {MO(M.B_INS_LOW)}–{MO(M.B_INS_HIGH)} per year; older multi-unit maintenance band {MO(M.B_MAINT_LOW)}–{MO(M.B_MAINT_HIGH)} per year",
        ], "status": "Owner-supplied", "sources": ["sfpuc_rates", "cdi", "irs_rental"]},
        {"cells": [
            "Expected transfer of Property A",
            "Via a trust, long-range window 2040–2050 (planning window, not a confirmed date)",
            "Property B stays separately owned and is not part of the trust transfer",
            "Cash and investments may accompany the transfer and can exceed the federal estate-tax exclusion — see the estate page",
        ], "status": "Owner-supplied", "sources": ["ca_prob160617", "ca_rtc480", "irs_estate"]},
    ]


def prop19_math_rows() -> list[dict]:
    rows = []
    for year in (2040, 2050):
        fm = M.value_at(year)
        fbv = M.fbv_a_at(year)
        cap = M.prop19_cap_at(year)
        av_p19 = M.p19_av(year)
        av_full = M.full_reassess_av(year)
        rows.append({"cells": [
            f"Transfer in {year} (base-case value growth {P(M.VALUE_GROWTH_BASE)})",
            f"Market value at transfer {MO(fm)}; factored base year value {MO(fbv)}; projected cap {MO(cap)}",
            f"With the family-home exclusion (move in within 1 year): new taxable value {MO(av_p19)} → tax about {MO(M.tax_a(av_p19))} per year",
            f"Without it (rented or vacant): taxable value {MO(av_full)} → tax about {MO(M.tax_a(av_full))} per year. Occupancy is worth about {MO(M.tax_a(av_full) - M.tax_a(av_p19))} per year in tax",
        ], "status": "Projection", "sources": ["boe_prop19", "boe_lta25009", "boe_pub29"]})
    return rows


def build_index() -> str:
    cf = M.path_cashflows()
    rows = [
        {"cells": ["Will the family actually occupy Property A as a principal residence within one year of the trust transfer?",
                   f"Under current law the family-home exclusion keeps only the factored base year value plus a capped amount (about {EX(M.PROP19_CAP_2025_2027)} for transfers through February 2027; the cap adjusts with the FHFA California index). Everything above the cap is reassessed even with the exclusion.",
                   "If yes → occupying A is the leading path (it saves roughly the projected cap × the tax rate each year versus not occupying). If no → selling A around the transfer is the leading path; renting it out is the weakest."],
         "status": "Guidance", "sources": ["boe_prop19", "boe_lta25009"]},
        {"cells": ["Total gross estate versus the federal exclusion",
                   f"Federal exclusion: {EX(M.EXCLUSION_2026)} (2026 deaths) / {EX(M.EXCLUSION_2027)} (2027); indexed thereafter under current law. The two homes alone total about {MO(M.A_VALUE_2026 + M.B_VALUE_2026)} at 2026 estimates.",
                   f"Headroom for cash and other assets is roughly {MO(M.EXCLUSION_2027 - M.A_VALUE_2026 - M.B_VALUE_2026)} before federal estate tax applies (2027 basis). California adds no inheritance or estate tax. See the estate page for the scenario grid."],
         "status": "Verified", "sources": ["irs_estate", "irs_rp2532", "ca_rtc13301"]},
        {"cells": ["Proposition 19 eligibility facts (relationship, both principal residences, filings)",
                   "The exclusion needs the transferor's and transferee's principal residence, a homeowners' exemption filed within 1 year, and a claim within 3 years (or before a third-party transfer). Grandparent-grandchild transfers need the parent-generation deceased condition.",
                   "Missing or late facts flip the transfer to full reassessment (about " + MO(M.tax_a(M.full_reassess_av(2040))) + " per year at 2040 base-case values instead of about " + MO(M.tax_a(M.p19_av(2040))) + ")."],
         "status": "Missing", "sources": ["boe_prop19", "ca_rtc63"]},
        {"cells": ["Property B's role: the cash-flow anchor",
                   f"Two rented units already produce about {MO(M.B_RENT_2UNITS_MO)} per month with an assessed value near {MO(M.B_AV_2025)} and a tax bill near {MO(M.B_TAX_2025)} per year. Renting the third unit adds a scenario band of {MO(M.B_RENT_UNIT3_LOW_MO)}–{MO(M.B_RENT_UNIT3_HIGH_MO)} per month.",
                   "B is the strongest income asset in the plan; its bill-to-assessment ratio and any rent-regulation coverage still need verification (flagged)."],
         "status": "Owner-supplied", "sources": ["irs_rental", "ca_rent", "sfpuc_rates"]},
        {"cells": ["What Property A costs to keep after transfer",
                   f"Even with the family-home exclusion, base-case 2040 tax is about {MO(M.tax_a(M.p19_av(2040)))} per year — versus about {MO(M.A_TAX_2026)} today. Renting A out at a scenario band of $5,500–$7,500 per month roughly breaks even at 2026 costs and goes negative after transfer-date reassessment.",
                   "This is the single number that most changes the answer: keeping A is a consumption-and-appreciation decision, not a cash-flow decision."],
         "status": "Projection", "sources": ["boe_pub29", "boe_lta25009", "irs_rental"]},
        {"cells": ["Insurance market condition at decision time",
                   "California's homeowners market is under active regulatory rebuild (CDI Sustainable Insurance Strategy: catastrophe models, insurer writing commitments, FAIR Plan modernization). Owner guesses of about $1,500 per property appear low versus recent market reporting; planning bands are higher.",
                   "Re-shop both policies near the transfer; a non-renewal or FAIR Plan fallback changes carrying costs and can delay occupancy."],
         "status": "Missing", "sources": ["cdi_sis", "cdi"]},
        {"cells": ["Sale proceeds, basis and staging",
                   f"Property A receives a date-of-death basis step-up (generally fair market value), so a sale near the transfer has little income-tax gain; selling costs are a scenario band of 4%–8% (about {MO(M.sale_net())} net at the {MO(M.A_VALUE_2026)} estimate on the 5% base case).",
                   "A 24–36 month Treasury staging plan before stock purchases softens 1929/2008-style crash entry risk but adds reinvestment risk and can lag a rising market. Use the stress tool."],
         "status": "Assumption", "sources": ["irs_basis", "treasury_bills", "treasury_notes", "fed_2008"]},
        {"cells": ["Future law and long-run economics",
                   "No official source can verify 2040–2050 thresholds, values, premiums, rents or returns. The 2026 Prop 19 repeal initiative failed officially in May 2026; future attempts and federal exclusion changes remain possible.",
                   "Re-check enacted law, the adjusted Prop 19 cap (next adjustment February 2027), valuations and quotes near the actual event; do not extrapolate one rate for fifty years."],
         "status": "Missing", "sources": ["sos_initiatives", "irs_2027", "cbo_ltbo", "fhfa_hpi"]},
    ]
    body = callout(
        "Conditional answer — ready to sharpen as evidence closes",
        "On the rounded figures available today: if the family will genuinely move into Property A as a principal residence within one year of the trust transfer, occupy A and rent all three units of Property B (best expected after-tax net worth, and occupancy saves a projected five-figure sum per year in property tax). If the family will not move, sell Property A around the transfer and stage the proceeds into diversified investments while keeping Property B fully rented — renting A out is projected to be cash-flow negative after reassessment. Estate-tax exposure appears unlikely unless total assets materially exceed the exclusion, but this must be confirmed against the whole estate.",
        "warning",
    )
    body += make_table(
        "What would change the answer?",
        ["Decision-changing fact", "What is established now", "Next evidence / decision gate"],
        rows,
        "First-screen triage list. Official links support the rule or published figure shown; they do not verify private title, occupancy, cost or tax facts. Dollar figures are rounded to the nearest $10 or are published statutory amounts.",
    )
    body += callout(
        "Keep the ownership roles distinct",
        "Property A is the anticipated trust transfer (2040–2050 planning window). Property B is already owned. A choice about one asset must not silently assume the other has the same basis, assessment, rent or costs.",
        "info",
    )
    body += cards("Use this workspace in order", [
        ("1. Read the executive summary", "Rounded snapshot, key economics and the conditional recommendation.", "pages/executive-summary.html"),
        ("2. Compare complete paths", "Occupancy, sale, rental and mixed paths with annual cash-flow bands.", "pages/decision-analysis.html"),
        ("3. Stress and stage", "Black-swan regimes and the 24–36 month Treasury staging tool.", "pages/black-swan.html"),
        ("4. Review with advisers", "Print the one-page attorney and CPA briefing sheet.", "pages/attorney-cpa-brief.html"),
    ])
    return render_page(
        "index.html",
        "Decision overview",
        "A privacy-first planning framework for an anticipated trust transfer and a separate already-owned property. Figures are rounded to the nearest $10; no addresses, postal codes, parcel identifiers or names are published.",
        body,
        "START HERE",
    )


def build_executive_summary() -> str:
    cf = M.path_cashflows()
    rows = [
        {"cells": ["Asset roles", "Property A is an expected future trust transfer (2040–2050 window). Property B is separately already owned and already produces rental income.", "Model the two assets separately; B's cash flow funds the plan regardless of what happens to A."], "status": "Owner-supplied", "sources": ["ca_prob160617", "irs_rental"]},
        {"cells": ["Property A economics at a glance", f"Value {MO(M.A_VALUE_2026)} (est.); assessed {MO(M.A_AV_2026)}; tax {MO(M.A_TAX_2026)}/yr today. After transfer the tax jumps even in the best case: about {MO(M.tax_a(M.p19_av(2040)))}/yr with the family-home exclusion vs about {MO(M.tax_a(M.full_reassess_av(2040)))}/yr without (2040 base case).", "Keeping A is driven by appreciation and (optionally) occupancy value — not cash flow."], "status": "Projection", "sources": ["boe_pub29", "boe_lta25009"]},
        {"cells": ["Proposition 19 in one line", f"Move in within 1 year + file the homeowners' exemption → the factored base year value plus about {EX(M.PROP19_CAP_2025_2027)} of value escapes reassessment (cap adjusted biennially by the FHFA California index). For a home this far above the cap, the exclusion is worth about {MO(M.tax_a(M.p19_av(2040)) * 0 + (M.tax_a(M.full_reassess_av(2040)) - M.tax_a(M.p19_av(2040))))} per year — material, but far less than the old unlimited parent-child exclusion.", "This is why 'inherit and keep the low taxes' is only half true: the low assessment largely disappears at transfer unless the cap grows enough."], "status": "Verified", "sources": ["boe_prop19", "boe_lta25009"]},
        {"cells": ["Property B economics at a glance", f"Value {MO(M.B_VALUE_2026)} (est.); assessed {MO(M.B_AV_2025)}; tax {MO(M.B_TAX_2025)}/yr; two units rent for {MO(M.B_RENT_2UNITS_MO)}/mo. Occupying one unit while renting two nets an estimated {MO(cf['p2'][0])}–{MO(cf['p2'][1])}/yr before income tax; renting the third unit adds roughly {MO((M.B_RENT_UNIT3_LOW_MO - 200) * 12)}–{MO((M.B_RENT_UNIT3_HIGH_MO - 200) * 12)}/yr.", "Keep B. It is the cash-flow anchor with a deep Prop 13 basis; selling it would trigger a large gain (basis unconfirmed) and end the income stream."], "status": "Owner-supplied", "sources": ["irs_rental", "irs_topic701", "sfpuc_rates"]},
        {"cells": ["Estate-tax exposure", f"2026 exclusion {EX(M.EXCLUSION_2026)}; 2027 {EX(M.EXCLUSION_2027)} (indexed thereafter under current law). Homes alone ≈ {MO(M.A_VALUE_2026 + M.B_VALUE_2026)}. California imposes no inheritance or estate tax.", "If cash and other assets keep the gross estate under the projected exclusion, no federal estate tax is expected; beneficiaries receive a basis step-up. Retirement-account money is income-taxable on withdrawal (IRD) — classify the estate's assets."], "status": "Verified", "sources": ["irs_estate", "irs_rp2532", "ca_rtc13301", "irs_basis"]},
        {"cells": ["Federal filing and trust income", f"Form 706 is due 9 months after death if the gross estate plus adjusted taxable gifts exceeds the year's threshold (extension up to 6 months via Form 4768; portability can require filing below the threshold). A non-grantor trust hits the 37% bracket over {EX(M.TRUST_TOP_2026)} of retained income (2026).", "Plan distributions of rental income rather than retaining it at trust rates; calendar the 706/4768/notice/150-day/1-year/3-year clocks."], "status": "Verified", "sources": ["irs_estate_faq", "irs_rp2532", "irs_1041"]},
        {"cells": ["Conditional recommendation", "Occupy A (within the one-year window) + rent all three B units if the family will move; otherwise sell A near the transfer and stage proceeds via 24–36 month Treasuries while keeping B fully rented. Do not hold A as a rental after full reassessment.", "Final ranking requires: executed trust terms, whole-estate inventory, Prop 19 eligibility facts, insurance quotes, and the family's true occupancy intent."], "status": "Guidance", "sources": ["boe_prop19", "irs_basis", "treasury_bills", "sec_stocks"]},
    ]
    body = callout(
        "Executive conclusion",
        "Two facts drive everything: (1) Proposition 19 preserves only a capped slice of Property A's low assessment, so keeping A is an appreciation/occupancy bet, and (2) Property B is a strong, low-tax cash-flow asset that should anchor the plan. The recommended path forks on one question — will the family occupy Property A within the one-year window? Everything else is sizing and stress-testing.",
        "warning",
    )
    body += make_table(
        "Important facts and current limits",
        ["Topic", "Verified rule or rounded case figure", "Decision implication"],
        rows,
    )
    body += make_table(
        "The two transfer-cost scenarios that decide the fork",
        ["Scenario", "Numbers at the 2040 transfer (base case)", "Annual tax comparison"],
        prop19_math_rows(),
        "Base case: 3.5% value growth, 2% assessed-value factor, 2% cap indexation. Projection — not a forecast. Every figure is rounded to the nearest $10.",
    )
    body += cards("Next pages", [
        ("Missing evidence", "Question-by-question record list for counsel, CPA, assessor, insurer and rental adviser.", "pages/questions.html"),
        ("Numbers", "Year-by-year projections of value, assessed value, tax and costs.", "pages/projections.html"),
        ("Risk", "Historical stress anchors, a 50-year irregular regime path and the Treasury phasing comparison.", "pages/black-swan.html"),
    ], current="pages/executive-summary.html")
    return render_page("pages/executive-summary.html", "Executive summary",
                       "The short version, with rounded numbers: separate the assets, treat Proposition 19 as a capped discount rather than a full carryover, let Property B's income anchor the plan, and fork the decision on genuine occupancy intent.",
                       body, "EXECUTIVE SUMMARY")


def build_decisions() -> str:
    cf = M.path_cashflows()
    net_sale = cf["net_sale"]
    rows = [
        {"cells": [
            "1. Occupy A after transfer (family-home exclusion) + rent all 3 B units",
            f"A: move in within 1 year, file homeowners' exemption; tax about {MO(M.tax_a(M.p19_av(2040)))}/yr at 2040 base case (vs {MO(M.tax_a(M.full_reassess_av(2040)))} without occupancy). B: {MO(cf['b_rent_all'][0])}–{MO(cf['b_rent_all'][1])}/yr gross rent.",
            f"Estimated net cash flow {MO(cf['p1'][0])}–{MO(cf['p1'][1])}/yr before income tax (2026 money).",
            "Highest expected net worth if occupancy is genuine and long-term: dual appreciation + capped tax + strong B income. Reverses if the family will not move, trust terms forbid occupancy, or insurance cannot be bound.",
        ], "status": "Projection", "sources": ["boe_prop19", "boe_lta25009", "irs_rental", "cdi"]},
        {"cells": [
            "2. Sell A near the transfer + stage proceeds (24–36 month Treasuries → stocks) + live in B (rent 2 units)",
            f"Basis step-up keeps income-tax gain near zero on a prompt sale; selling costs band 4%–8% → about {MO(net_sale)} investable at the {MO(M.A_VALUE_2026)} estimate (5% base).",
            f"Estimated net cash flow {MO(cf['p2'][0])}–{MO(cf['p2'][1])}/yr from B alone, plus portfolio growth on about {MO(net_sale)} (scenario 4%/6%/8% nominal).",
            "Best path if the family stays in San Francisco: liquidity, diversification, no reassessed-tax drag. Reverses if occupancy intent is genuine (then Path 1 wins on the tax delta) or if markets are deliberately avoided.",
        ], "status": "Projection", "sources": ["irs_basis", "irs_topic701", "treasury_bills", "sec_stocks", "fed_2008"]},
        {"cells": [
            "3. Rent A out (no occupancy) + live in B",
            "A is fully reassessed at transfer: taxable value ≈ market value (about {0}/yr tax at 2040 base case). Scenario rent band $5,500–$7,500/mo; vacancy+management band 11%.".format(MO(M.tax_a(M.full_reassess_av(2040)))),
            f"Estimated net cash flow {MO(cf['p3'][0])}–{MO(cf['p3'][1])}/yr from the A rental alone (2026 money) — around break-even at today's values and negative at transfer-date values.",
            "Weakest pure path: negative carry, illiquidity, landlord obligations. Reverses only if market rent materially exceeds the band or assessments change.",
        ], "status": "Projection", "sources": ["boe_pub29", "irs_rental", "ca_rent", "hud_fmr"]},
        {"cells": [
            "4. Mixed: occupy A for ≥1 year (secure the exclusion), then move back to B and rent A later",
            "Occupancy secures the capped exclusion first; later converting A to a rental risks a new change-in-ownership/reassessment when it ceases to be the principal residence (confirm with the assessor — flagged).",
            "Same early numbers as Path 1, then Path 3 economics with a capped assessment — the best of both only if the move-out consequence is confirmed benign.",
            "Reverses if the assessor confirms reassessment on move-out (likely) or if the two moves cost more than the delta. Verify before relying on this path.",
        ], "status": "Missing", "sources": ["boe_prop19", "ca_rtc63", "ca_rtc480"]},
        {"cells": [
            "5. Short-hold A (2–3 years) then sell",
            "Carry Path-3 costs (or Path-1 occupancy) for a couple of years, then sell with the inherited basis (little gain) after paying reassessed or excluded taxes depending on occupancy.",
            f"About {MO(cf['p3'][0] * 2)}–{MO(cf['p3'][1] * 2)} cumulative carrying variance over 2 years, then ≈{MO(net_sale)} invested.",
            "Useful when the market is soft at transfer or a tenant/sale decision needs time. Reverses if prices fall further or carrying costs exceed the band.",
        ], "status": "Assumption", "sources": ["irs_basis", "irs_rental", "boe_pub29"]},
        {"cells": [
            "6. Sell B + live in A",
            f"Selling B triggers gain on ≈{MO(M.B_VALUE_2026)} minus an unconfirmed basis (assessed value {MO(M.B_AV_2025)} implies a decades-old purchase) — up to {EX(500000)} of gain may be excluded if the 2-of-5-year principal-residence tests are met; the rest is taxable.",
            f"Loses the {MO(cf['p2'][0])}–{MO(cf['p2'][1])}/yr B income stream and its low assessment; adds A's full post-transfer carrying costs.",
            "Generally the weakest choice: destroys the best asset to fund the most expensive one. Reverses only with a confirmed large basis, a compelling need for liquidity, or strong personal preference.",
        ], "status": "Missing", "sources": ["irs_topic701", "irs_basis", "irs_rental"]},
    ]
    body = callout("How to read the rankings",
                   "Cash-flow bands are 2026-money estimates from rounded owner inputs and labeled scenario bands; they exclude income taxes, debt service (none disclosed), and transfer-time values. Path 1 and Path 2 dominate on expected value; which one wins depends almost entirely on genuine occupancy intent for Property A.",
                   "info")
    body += make_table("Pure and mixed paths — with estimated numbers",
                       ["Path", "Mechanics and key figures", "Estimated annual cash flow (2026 money)", "Why it ranks here / what reverses it"],
                       rows,
                       "Projection rows use base-case growth and cost bands from the projections page. Owner-supplied inputs are rounded to $10. No official source verifies a household rent, premium or repair cost — see flagged items.")
    body += paragraph("Comparison rule",
                      "For every path show after-tax cash flows, one-time sale or transfer costs, debt, vacancy, repairs, insurance, utilities, property tax, rent legality, liquidity and reinvestment risk — on the same horizon, with every assumption disclosed. The mixed paths (4 and 5) exist because the choice is not limited to three pure options.")
    return render_page("pages/decision-analysis.html", "Compare live, rent, sell and mixed paths",
                       "Six paths with rounded cash-flow bands and explicit reversal conditions. The two assets are modeled separately: Property A is the trust transfer; Property B is the already-owned cash-flow anchor.",
                       body, "DECISION")


def build_questions() -> str:
    rows = [
        {"cells": ["Q1 — What exactly transfers, when, and under whose authority?", "The trust-transfer role and the 2040–2050 planning window are supplied; the instrument, amendments, distribution terms and trustee authority are absent.", "No verified answer; do not assume a beneficiary can occupy, rent or sell without trustee authority.", "Executed trust and amendments, deed, trustee contact, written distribution/sale/occupancy directions.", "Attorney / trustee"], "status": "Owner-supplied", "sources": ["ca_prob160617", "ca_rtc480"]},
        {"cells": ["Q2 — What is the full gross estate, gift history and specific exemption use?", f"Homes total ≈{MO(M.A_VALUE_2026 + M.B_VALUE_2026)} at 2026 estimates; the accompanying cash is described only as potentially above the exclusion. 2027 exclusion {EX(M.EXCLUSION_2027)}.", "Federal exposure cannot be calculated from two homes; portability can independently require filing.", "Asset/debt inventory, prior taxable gifts, specific gift-tax exemption, deductions, spouse/portability facts, valuation date.", "CPA / estate attorney"], "status": "Missing", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["Q3 — What is the income-tax basis and defensible transfer value?", "No appraisal, Form 706, Schedule A/Form 8971 or basis schedule is published.", "Inherited basis is generally date-of-death fair market value; a later sale above basis may create gain.", "Date-of-death appraisal, executor basis statement, improvements, depreciation and prior transfer records.", "CPA / appraiser"], "status": "Missing", "sources": ["irs_basis", "irs_estate"]},
        {"cells": ["Q4 — Does the transfer qualify for the California family-home exclusion?", "Relationship, transferor occupancy, trust title, transferee occupancy plan and claim status are not verified.", f"Eligibility is conditional; without it, base-case 2040 tax ≈{MO(M.tax_a(M.full_reassess_av(2040)))}/yr vs ≈{MO(M.tax_a(M.p19_av(2040)))}/yr with it.", "Deed/trust, family relationship, any intermediary-parent status (grandchild rule), principal-residence proof, value-limit calculation, filed claim and dates.", "Assessor / property-tax adviser"], "status": "Missing", "sources": ["boe_prop19", "ca_rtc63", "boe_lta25009"]},
        {"cells": ["Q5 — What is the complete current tax bill for each asset?", f"Rounded owner tables show {MO(M.A_TAX_2026)} on {MO(M.A_AV_2026)} (≈{P(M.RATIO_A, 2)}) and {MO(M.B_TAX_2025)} on {MO(M.B_AV_2025)} (≈{P(M.RATIO_B, 2)}). B's ratio is irregular versus A's.", "A 1% base levy and 2% cap do not explain B's higher ratio; special charges or partial-bill reporting may.", "Current roll, supplemental bill, direct assessments, bond charges, base-year value, appeal status for both parcels.", "Assessor / CPA"], "status": "Owner-supplied", "sources": ["boe_pub29", "boe_prop19"]},
        {"cells": ["Q6 — What is the legal unit count and rent-regulation coverage?", "Three livable units are described for B; no permit, certificate or lease is published. San Francisco units are often rent-regulated; coverage is fact-specific.", "Do not assume all units are freely rentable or that statewide caps are the only rules.", "Permits, certificates of occupancy, leases, rent registry, local ordinances and tenant notices.", "Landlord-tenant attorney / building authority"], "status": "Missing", "sources": ["ca_rent", "hud_fmr", "irs_rental"]},
        {"cells": ["Q7 — What is Property B's income after vacancy, expenses and taxes?", f"Owner reports {MO(M.B_RENT_2UNITS_MO)}/mo from two units; the third unit is unrented (scenario band {MO(M.B_RENT_UNIT3_LOW_MO)}–{MO(M.B_RENT_UNIT3_HIGH_MO)}/mo).", f"Estimated net {MO(M.path_cashflows()['p2'][0])}–{MO(M.path_cashflows()['p2'][1])}/yr with two units rented, before income tax.", "B's leases, rent roll, deposits, vacancy/collection history, permitted unit status, expense ledger and tax return.", "CPA / property manager"], "status": "Owner-supplied", "sources": ["hud_fmr", "irs_rental", "ca_rent"]},
        {"cells": ["Q8 — What insurance is available for each intended use?", f"Owner guesses ≈{MO(M.A_INS_OWNER)} and ≈{MO(M.B_INS_OWNER)}; market planning bands are {MO(M.A_INS_LOW)}–{MO(M.A_INS_HIGH)} and {MO(M.B_INS_LOW)}–{MO(M.B_INS_HIGH)}. California's market is mid-rebuild (CDI strategy; FAIR Plan changes).", "Primary-residence and landlord underwriting differ; a price cannot be derived from state pages.", "Separate written quotes, exclusions, replacement-cost basis, liability, fire/earthquake and any FAIR Plan/DIC gap.", "Licensed insurance broker"], "status": "Missing", "sources": ["cdi", "cdi_sis"]},
        {"cells": ["Q9 — What are water, electricity, solar-credit and repair costs?", "Owner bands: A water $100–$150/mo with a $10–$20 solar credit; B water $330–$400/mo and electricity $30–$70/mo. SFPUC's published average single-family combined bill is about $170/mo rising to about $210 by FYE 2028 (rounded from its notice).", "Solar export credits depend on tariff and interconnection; no account credit can be inferred from equipment.", "24 months of bills, solar/NEM/NBT agreement, roof/infrastructure inspections, licensed bids.", "Utility / solar provider / contractor"], "status": "Owner-supplied", "sources": ["sfpuc_rates", "cpuc_solar", "cslb"]},
        {"cells": ["Q10 — What are net sale proceeds and selling costs?", f"No sale contract or fee quote is published; scenario band 4%–8% of price (base 5%) → ≈{MO(M.sale_net())} at the {MO(M.A_VALUE_2026)} estimate.", "Gross value is not investable cash; basis (step-up), costs and any debt all matter.", "Broker/closing estimate, debt statement, title search, transfer charges and tax calculation.", "CPA / escrow / attorney"], "status": "Missing", "sources": ["irs_basis", "irs_estate"]},
        {"cells": ["Q11 — Can Property B serve as the family residence, and what happens to its rent?", "Yes per the owner (one unit is currently owner-occupied); legal suitability and tenant obligations are not independently confirmed.", "Compare living in B with occupying A only after confirming lawful units, leases and net rent.", "B's lease/tenant records, lawful-unit permits, inspection, title/debt, use-specific insurance and occupancy plan.", "Landlord-tenant counsel / insurer"], "status": "Owner-supplied", "sources": ["irs_rental", "ca_rent", "cdi"]},
        {"cells": ["Q12 — What investment policy should apply to any sale proceeds?", f"No distribution amount, tax reserve, portfolio or risk tolerance is published. Scenario return bands used here: {P(M.STOCK_LOW, 0)}/{P(M.STOCK_BASE, 0)}/{P(M.STOCK_HIGH, 0)} nominal.", "The Treasury staging plan is a scenario, not an individualized recommendation.", "Net proceeds, tax reserve, cash needs, allocation policy, fee schedule, net yields and withdrawal plan.", "Fee-only fiduciary adviser / CPA"], "status": "Missing", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
        {"cells": ["Q13 — What is the decedent's domicile and the trust's situs?", "Not disclosed. State death taxation follows domicile/situs rules; California's bar on death taxes applies to California transfers.", "A non-California domicile can trigger another state's inheritance or estate tax.", "Domicile evidence, trust situs language, prior-year filings.", "Estate attorney / CPA"], "status": "Missing", "sources": ["ca_rtc13301", "irs_estate"]},
        {"cells": ["Q14 — What assets are retirement accounts versus cash/securities?", "The accompanying money is not classified. Retirement accounts (IRD) are income-taxable to beneficiaries; cash and securities receive a basis step-up.", "The same dollar of 'inheritance' can be worth materially less after income tax if it sits in a pre-tax account.", "Account statements, beneficiary designations, Form 1099-R/IRA records, trust funding schedule.", "CPA"], "status": "Missing", "sources": ["irs_basis", "irs_estate"]},
        {"cells": ["Q15 — Is there debt on either property?", "None disclosed. Mortgages change sale math, cash flow and risk.", "Debt payoff at sale reduces proceeds; leverage amplifies a downside path.", "Mortgage statements, payoff quotes, HELOC records.", "CPA / lender"], "status": "Missing", "sources": ["irs_estate"]},
        {"cells": ["Q16 — Parent-child or grandparent-grandchild transfer?", "Not disclosed. Grandparent-grandchild transfers qualify only if the statutory middle-generation condition is met.", "A grandchild transfer without the condition loses the exclusion entirely.", "Family tree documentation, death certificates if applicable.", "Attorney / assessor"], "status": "Missing", "sources": ["boe_prop19", "ca_rtc63"]},
        {"cells": ["Q17 — Is the homeowners' exemption currently filed on Property A?", "Unknown. Prop 19's transferor-principal-residence condition generally expects the exemption (or equivalent) in place.", "Missing exemption history complicates eligibility evidence.", "Assessor exemption records for A.", "Assessor"], "status": "Missing", "sources": ["boe_prop19", "ca_rtc63"]},
        {"cells": ["Q18 — Will the family genuinely relocate into Property A?", "The decisive lifestyle question; not answered in the record.", "This single answer forks the entire plan (Path 1 vs Path 2).", "A documented household decision, school/work plan and timeline.", "Family"], "status": "Missing", "sources": ["boe_prop19"]},
        {"cells": ["Q19 — What happens if the family occupies A and later moves out?", "Under review: conversion of the transferred home away from principal-residence use can end the exclusion and trigger reassessment; official treatment must be confirmed.", "This governs whether the 'occupy then rent' mixed path is real or illusory.", "Written assessor confirmation or counsel opinion on reassessment after move-out.", "Assessor / property-tax counsel"], "status": "Missing", "sources": ["ca_rtc63", "boe_prop19"]},
        {"cells": ["Q20 — Which pending bills could change the analysis?", "Verified as of the check date: the Prop 19 repeal initiative failed (official SOS memo, May 2026); SCA-4 is a veterans' exemption measure (not parent-child relief); SB 79 transit-oriented zoning took effect July 2026. Others must be searched fresh.", "No pending proposal is treated as law; each would need enactment plus effective-date review.", "Congress.gov and leginfo searches near the decision date; SOS ballot status for any new initiative.", "Attorney / adviser"], "status": "Verified", "sources": ["sos_initiatives", "leginfo_sca4", "hcd_sb79", "congress_legislation"]},
    ]
    body = callout("Answers are intentionally bounded",
                   "Only rounded owner-supplied figures and published statutory amounts appear. Status 'Owner-supplied' means the figure came from the owner's rounded description — the linked source verifies the rule cited, not the household fact.",
                   "info")
    body += make_table("Questions, information required and answer status",
                       ["Question", "Information available", "Answer from verified evidence", "Record needed to close the gap", "Who should confirm"],
                       rows,
                       "Discovery order: trust and title records → estate valuation/basis and property-tax deadlines → lawful use and leases → insurance/repair/utility quotes → only then the final after-tax comparison.")
    body += paragraph("What we still do not have",
                      "Executed trust documents, the estate inventory, appraisals, assessor rolls, bills, leases, permits, insurance quotes, repair bids, solar interconnection records and the family's occupancy decision. Until these arrive, all rankings stay conditional and every projection is labeled.")
    return render_page("pages/questions.html", "Questions & missing evidence",
                       "A clear register of what is known (rounded), what is not established, and the document or official rule needed to close each gap.",
                       body, "DECISION")
def build_projections() -> str:
    a_rows = []
    for year in range(2026, 2056):
        v = M.value_at(year)
        av = M.fbv_a_at(year)
        t = M.tax_a(av)
        note = "—"
        if year == 2026:
            note = "Baseline: rounded owner inputs"
        elif year in (2040, 2050):
            note = "Example transfer year — see the assessment-branch table"
        elif year == 2027:
            note = "Next Proposition 19 cap adjustment due February 2027"
        a_rows.append({"cells": [str(year), MO(v), MO(av), MO(t), note],
                       "status": "Projection", "sources": ["boe_pub29", "fhfa_hpi"]})
    b_rows = []
    for year in range(2026, 2056, 5):
        v = M.value_at(year, start=M.B_VALUE_2026)
        av = M.b_av_at(year)
        t = M.tax_b(av)
        rent = M.B_RENT_2UNITS_MO * (1 + M.RENT_GROWTH) ** (year - 2026) * 12
        b_rows.append({"cells": [str(year), MO(v), MO(av), MO(t), MO(rent)],
                       "status": "Projection", "sources": ["boe_pub29", "irs_rental"]})
    scen_rows = []
    for year in (2030, 2035, 2040, 2045, 2050, 2055):
        scen_rows.append({"cells": [
            str(year),
            MO(M.value_at(year, M.VALUE_GROWTH_LOW)),
            MO(M.value_at(year, M.VALUE_GROWTH_BASE)),
            MO(M.value_at(year, M.VALUE_GROWTH_HIGH)),
            MO(M.value_at(year, M.VALUE_GROWTH_BASE, start=M.B_VALUE_2026)),
        ], "status": "Projection", "sources": ["fhfa_hpi", "cbo_ltbo"]})
    branch_rows = []
    for year in (2040, 2050):
        for hpi, tag in ((M.CAP_GROWTH_LOW, "cap +2.0%/yr"), (M.CAP_GROWTH_HIGH, "cap +3.5%/yr")):
            fbv = M.fbv_a_at(year)
            cap = M.prop19_cap_at(year, hpi)
            av_p19 = M.p19_av(year, hpi_rate=hpi)
            av_full = M.full_reassess_av(year)
            branch_rows.append({"cells": [
                f"{year} transfer ({tag})",
                f"Factored base year value {MO(fbv)}; projected cap {MO(cap)}; market value {MO(M.value_at(year))}",
                f"{MO(av_p19)} → about {MO(M.tax_a(av_p19))} per year",
                f"{MO(av_full)} → about {MO(M.tax_a(av_full))} per year",
                f"Occupancy saves about {MO(M.tax_a(av_full) - M.tax_a(av_p19))} per year",
            ], "status": "Projection", "sources": ["boe_lta25009", "boe_prop19", "boe_pub29"]})
    cost_rows = []
    a_ins, b_ins = (M.A_INS_LOW + M.A_INS_HIGH) / 2, (M.B_INS_LOW + M.B_INS_HIGH) / 2
    a_water = (M.A_WATER_LOW_MO + M.A_WATER_HIGH_MO) / 2 * 12
    b_water = (M.B_WATER_LOW_MO + M.B_WATER_HIGH_MO) / 2 * 12
    for year in (2026, 2030, 2035, 2040, 2045, 2050):
        n = year - 2026
        ins_a = a_ins * 1.04 ** n
        ins_b = b_ins * 1.04 ** n
        wat_a = a_water * 1.03 ** n
        wat_b = b_water * (1.126 if year >= 2027 else 1.0) * (1.125 if year >= 2028 else 1.0) * 1.04 ** max(0, n - 2)
        maint_a = M.A_VALUE_2026 * (1 + M.VALUE_GROWTH_BASE) ** n * 0.0075
        maint_b = 13_500 * 1.03 ** n
        cost_rows.append({"cells": [str(year), MO(ins_a), MO(wat_a), MO(maint_a), MO(ins_b), MO(wat_b), MO(maint_b)],
                          "status": "Projection", "sources": ["cdi", "sfpuc_rates", "cslb", "irs_rental"]})
    body = callout(
        "How these projections are built",
        f"Market value: {P(M.VALUE_GROWTH_LOW)}/{P(M.VALUE_GROWTH_BASE)}/{P(M.VALUE_GROWTH_HIGH)} scenario growth (base anchored loosely on CBO nominal growth and FHFA history — assumption, not a forecast). Assessed value before transfer: the general {P(M.AV_FACTOR, 0)} annual factor. After transfer: the branch tables. Costs: insurance +4%/yr scenario, water +3%/yr (Property A) and the published SFPUC increases then +4% (Property B), maintenance 0.75% of value (A) and a fixed band (B). Every figure is rounded to the nearest $10; all rates are labeled assumptions.",
        "info",
    )
    body += make_table(
        "Property A — year-by-year (base case, held without transfer)",
        ["Year", "Market value", "Pre-transfer factored assessed value", "Property tax at factored value", "Note"],
        a_rows,
        "Before the trust transfer, the factored base year value grows by the general 2% factor and tax ≈ "
        f"{P(M.RATIO_A, 2)} of assessed value (observed ratio from the rounded owner tables). At transfer the assessment branches — see below.",
    )
    body += make_table(
        "Property A — assessment branches at the transfer",
        ["Transfer scenario", "Inputs at transfer", "Family-home exclusion (occupancy path)", "Full reassessment (rental/sale-less path)", "Difference"],
        branch_rows,
        "Family-home exclusion math: new taxable value = factored base year value + any amount by which market value exceeds factored value plus the projected cap (BOE Prop 19 chart; Property Tax Rule 462.520; LTA 2025/009 for cap adjustments).",
    )
    body += make_table(
        "Property B — five-year marks (base case)",
        ["Year", "Market value", "Assessed value (+2%/yr)", f"Property tax (observed ratio {P(M.RATIO_B, 2)})", "Gross rent, two units (+1.6%/yr — SF Rent Board allowable increase for covered units; coverage unverified)"],
        b_rows,
        "B's observed bill-to-assessment ratio is irregular versus Property A's; verify the bill's components before relying on the tax column (flagged). Rent growth is capped in practice by local rules — verify rent-regulation coverage.",
    )
    body += make_table(
        "Property A market value — low / base / high scenarios",
        ["Year", f"Low ({P(M.VALUE_GROWTH_LOW)})", f"Base ({P(M.VALUE_GROWTH_BASE)})", f"High ({P(M.VALUE_GROWTH_HIGH)})", "Property B base case"],
        scen_rows,
        "Scenario outputs, not forecasts. The black-swan page replaces these smooth curves with an irregular 50-year path.",
    )
    body += make_table(
        "Operating-cost projections (mid-band assumptions)",
        ["Year", "A insurance", "A water (annual)", "A maintenance (0.75% of value)", "B insurance", "B water (annual)", "B maintenance"],
        cost_rows,
        "Insurance uses the midpoint of the flagged market planning bands; water centers on the owner bands (B reflects the published SFPUC 2026–2028 increases); maintenance is a scenario assumption. Replace all of these with quotes and bills.",
    )
    body += paragraph("Horizon and limits",
                      "The transfer window is 2040–2050 (planning window, not confirmed). CBO's cited long-run projections run to 2055 and cannot responsibly be extended as a household forecast; FHFA indexes are broad; no official source projects insurance, rent or repair costs. Use the low/base/high columns and the black-swan path together, and re-run the model when appraisals, bills and quotes arrive.")
    return render_page("pages/projections.html", "Projection worksheet",
                       "Year-by-year projections of market value, assessed value, property tax and operating costs for both properties, with post-transfer assessment branches and scenario ranges. Assumptions are labeled; figures are rounded to $10.",
                       body, "NUMBERS")


def build_property_tax() -> str:
    cap_rows = [
        {"cells": ["February 16, 2021 – February 15, 2023", EX(1_000_000), "Initial Proposition 19 $1,000,000 amount."], "status": "Verified", "sources": ["boe_lta25009"]},
        {"cells": ["February 16, 2023 – February 15, 2025", EX(1_022_600), "First biennial adjustment."], "status": "Verified", "sources": ["boe_lta25009"]},
        {"cells": ["February 16, 2025 – February 15, 2027", EX(M.PROP19_CAP_2025_2027), "Adjusted for the FHFA-reported 2024 California HPI change of 2.15%. Next adjustment due February 2027 — the amount for a 2040–2050 transfer is unknown today."], "status": "Verified", "sources": ["boe_lta25009", "fhfa_hpi"]},
    ]
    rows = [
        {"cells": ["General levy", "1% of assessed value plus voter-approved bonded indebtedness; other charges can appear on the bill.", f"The rounded owner tables imply total ratios of ≈{P(M.RATIO_A, 2)} (Property A) and ≈{P(M.RATIO_B, 2)} (Property B) — the difference is unexplained and flagged."], "status": "Verified", "sources": ["boe_pub29"]},
        {"cells": ["Annual assessed-value limit", "General limit: 2% annual growth in the factored base year value, subject to change-in-ownership and new-construction rules.", "This is why A's assessment (≈" + MO(M.A_AV_2026) + ") sits far below its market value (≈" + MO(M.A_VALUE_2026) + ") — and why the gap matters enormously at transfer."], "status": "Verified", "sources": ["boe_pub29"]},
        {"cells": ["Family-home exclusion (parent-child)", "Principal residence of transferor AND transferee; value limit = factored base year value + the adjusted $1,000,000 amount; homeowners' exemption within 1 year; claim within 3 years or before a third-party transfer.", "For Property A the market value far exceeds factored value + cap, so the exclusion produces a PARTIAL reassessment — the excess above the cap is added to the taxable value."], "status": "Verified", "sources": ["boe_prop19", "ca_rtc63"]},
        {"cells": ["Grandparent-grandchild variant", "Same rules plus the statutory condition that the grandchild's parent (the transferor's child) is deceased at transfer.", "If this is a grandparent-grandchild transfer, verify the middle-generation condition early — failing it forfeits the exclusion entirely."], "status": "Verified", "sources": ["boe_prop19", "ca_rtc63"]},
        {"cells": ["Trust transfer reporting", "Change-in-ownership statement due within 150 days after death for specified nonprobate transfers, including through a trust.", "Missing the filing can complicate the assessment record; confirm the county's route and retain proof."], "status": "Verified", "sources": ["ca_rtc480"]},
        {"cells": ["Homeowners' exemption", "The exemption is $7,000 of the dwelling's full value and does not apply to rented, vacant, secondary or vacation property on the lien date (RTC §218).", "Small yearly money, but material as evidence: the exemption is also the practical anchor for the Prop 19 principal-residence condition — losing it can signal a failed condition."], "status": "Verified", "sources": ["ca_rtc218", "boe_pub29"]},
        {"cells": ["Base year value definition", "RTC §51 defines the property's base year value; the general 2% factor builds the factored base year value used in the exclusion math.", "Do not model 'property tax = market value × one assumed rate' — model the base-year value, the factor, and the bill's separate charges."], "status": "Verified", "sources": ["ca_rtc51", "boe_pub29"]},
        {"cells": ["Occupancy-then-move-out", "Whether ceasing to use the transferred home as the principal residence triggers a new change in ownership/reassessment must be confirmed for the actual facts.", "This governs the 'occupy then rent' mixed path. Currently flagged as unresolved (Q19)."], "status": "Missing", "sources": ["ca_rtc63", "boe_prop19"]},
        {"cells": ["Actual assessed values and bills", f"Rounded owner tables only (A: {MO(M.A_AV_2026)} / {MO(M.A_TAX_2026)}; B: {MO(M.B_AV_2025)} / {MO(M.B_TAX_2025)}).", "Obtain both secured bills, direct charges, base-year values and exemption records before final modeling."], "status": "Owner-supplied", "sources": ["boe_pub29"]},
    ]
    body = callout("Critical distinction",
                   "Income-tax basis (date-of-death fair market value) and property-tax assessed value (factored base year value or reassessed value) are different systems. The step-up in basis does not preserve the low assessment, and the family-home exclusion does not change the basis.",
                   "info")
    body += make_table("Proposition 19 value-cap history (published amounts)",
                       ["Transfer window", "Adjusted $1,000,000 amount", "Note"],
                       cap_rows,
                       "Official BOE Letter to Assessors 2025/009. The cap adjusts every other February by the FHFA House Price Index for California; the 2024 change was 2.15%.")
    body += make_table("California property-tax rules and the case math",
                       ["Issue", "Current source-backed rule", "What it means here"],
                       rows,
                       "BOE warns statutes and rules change; verify the law and the assessor's calculation at the actual transfer.")
    body += make_table("Worked partial-reassessment examples (projections, rounded)",
                       ["Transfer year (base case)", "Inputs", "Exclusion path", "Full reassessment path", "Annual difference"],
                       [
                           {"cells": ["Transfer at 2040", f"FMV {MO(M.value_at(2040))}; FBV {MO(M.fbv_a_at(2040))}; cap {MO(M.prop19_cap_at(2040))}", f"Taxable {MO(M.p19_av(2040))} → tax ≈{MO(M.tax_a(M.p19_av(2040)))}", f"Taxable {MO(M.full_reassess_av(2040))} → tax ≈{MO(M.tax_a(M.full_reassess_av(2040)))}", f"{MO(M.tax_a(M.full_reassess_av(2040)) - M.tax_a(M.p19_av(2040)))}"], "status": "Projection", "sources": ["boe_lta25009", "boe_pub29"]},
                           {"cells": ["Transfer at 2050", f"FMV {MO(M.value_at(2050))}; FBV {MO(M.fbv_a_at(2050))}; cap {MO(M.prop19_cap_at(2050))}", f"Taxable {MO(M.p19_av(2050))} → tax ≈{MO(M.tax_a(M.p19_av(2050)))}", f"Taxable {MO(M.full_reassess_av(2050))} → tax ≈{MO(M.tax_a(M.full_reassess_av(2050)))}", f"{MO(M.tax_a(M.full_reassess_av(2050)) - M.tax_a(M.p19_av(2050)))}"], "status": "Projection", "sources": ["boe_lta25009", "boe_pub29"]},
                       ],
                       "Formula (BOE comparison chart and Property Tax Rule 462.520): taxable value = factored base year value + the amount by which market value exceeds factored value + cap. Assumed value growth 3.5%/yr, cap indexation 2%/yr, tax ratio ≈1.31% (observed).")
    body += paragraph("Irregularity flagged",
                      f"Property B's rounded tax-to-assessment ratio ({P(M.RATIO_B, 2)}) is far above Property A's ({P(M.RATIO_A, 2)}). This may reflect direct assessments, a partial-year bill, or a different rate structure — it is reported as supplied and flagged for assessor confirmation. No figure has been adjusted to fit expectations.")
    return render_page("pages/property-tax.html", "Property-tax rules and case math",
                       "California mechanics, the official Proposition 19 cap history, and the partial-reassessment math applied to the rounded case figures.",
                       body, "NUMBERS")


def build_costs() -> str:
    rows = [
        {"cells": ["Property tax", f"A: {MO(M.A_TAX_2026)}/yr today (rises with the 2% factor to ≈{MO(M.tax_a(M.fbv_a_at(2040)))} by 2040 pre-transfer; see branch table post-transfer). B: {MO(M.B_TAX_2025)}/yr.", "Verify both bills and direct charges; model post-transfer A tax on the branch assumption you believe."], "status": "Owner-supplied", "sources": ["boe_pub29", "boe_lta25009"]},
        {"cells": ["Homeowners insurance (A, primary-residence)", f"Owner guess {MO(M.A_INS_OWNER)}/yr. Market planning band {MO(M.A_INS_LOW)}–{MO(M.A_INS_HIGH)}/yr for a high-value suburban home; the owner guess appears low versus current California market conditions.", "Request a written quote with replacement-cost basis, liability, wildfire classification and exclusions; check FAIR Plan fallback and DIC wrap needs."], "status": "Missing", "sources": ["cdi", "cdi_sis"]},
        {"cells": ["Landlord / dwelling-fire insurance (B, 3 units)", f"Owner guess {MO(M.B_INS_OWNER)}/yr. Planning band {MO(M.B_INS_LOW)}–{MO(M.B_INS_HIGH)}/yr for an urban multi-unit rental.", "Underwriting depends on legal units, occupancy, wiring/roof age and loss history; quote the actual structure."], "status": "Missing", "sources": ["cdi", "cdi_sis"]},
        {"cells": ["Water (A)", "Owner band $100–$150/month. Provider/territory rates not independently confirmed (the property's water system is not identified here).", "Use 12 months of provider bills; confirm tier structure and any fixed charges."], "status": "Owner-supplied", "sources": ["water_board"]},
        {"cells": ["Water + sewer (B, 3 units)", "Owner band $330–$400/month for all three units. SFPUC's published notice puts the average San Francisco single-family combined bill at about $170/mo (FYE 2026) rising to about $190 then $210 — roughly consistent with ~3 units at multi-family tiering.", "Use the actual account bills; the July 2026 increase (≈12.6%) and July 2027 increase (≈12.5%) are already approved in the notice."], "status": "Owner-supplied", "sources": ["sfpuc_rates"]},
        {"cells": ["Electricity and solar (A)", "Owner band: net $10–$20/month credit (solar). Export credit value depends on the tariff (NEM vs net billing) and interconnection date; under net billing, export credits are usually below retail.", "Obtain the interconnection agreement, true-up history and 24 months of bills before counting the credit as income."], "status": "Owner-supplied", "sources": ["cpuc_solar"]},
        {"cells": ["Electricity (B)", "Owner band $30–$70/month (likely common areas or owner-paid accounts).", "Confirm which accounts the landlord pays and what the leases say."], "status": "Owner-supplied", "sources": ["sfpuc_rates"]},
        {"cells": ["Repairs and maintenance (A)", "Scenario band 0.5%–1.0% of value per year (about " + MO(M.A_VALUE_2026 * 0.005) + "–" + MO(M.A_VALUE_2026 * 0.01) + " at the 2026 estimate). Owner reports less than Property B.", "Get inspection reports and itemized licensed bids; older roofs, plumbing and foundations drive the band."], "status": "Assumption", "sources": ["cslb", "irs_rental"]},
        {"cells": ["Repairs and maintenance (B)", f"Scenario band {MO(M.B_MAINT_LOW)}–{MO(M.B_MAINT_HIGH)}/year for an older 3-unit building (owner reports higher than A).", "Same process; multi-unit systems (boilers, shared wiring, sewer laterals) can spike costs."], "status": "Assumption", "sources": ["cslb", "irs_rental"]},
        {"cells": ["Rent regulation on Property B (San Francisco)", "The SF Rent Board states a 1.6% allowable annual increase for covered units (March 1, 2026 – February 28, 2027). Coverage of these specific units is unverified (flagged).", "If covered, projected rent growth must be capped near this figure; confirm coverage, registration and just-cause rules with counsel before any increase."], "status": "Verified", "sources": ["sf_rent_board"]},
        {"cells": ["SF vacancy tax exposure", "An empty-homes/vacancy tax may apply to vacant units; the official page failed retrieval and no rule is asserted.", "Confirm the current SF Treasurer rules before leaving a unit vacant; treat this as an open cost line (flagged)."], "status": "Not verified", "sources": ["sf_treasurer_vacancy_404"]},
        {"cells": ["Vacancy, collection and management (if A rented)", "Scenario band: 5% vacancy + 6% management of gross rent (common planning allowances — assumption).", "Replace with a local management quote and the property's own history."], "status": "Assumption", "sources": ["irs_rental", "hud_fmr"]},
        {"cells": ["Income-tax side of rental use", "Rental income is taxable; depreciation (27.5-year residential schedule), expense allocation between personal and rental use, and sale-basis adjustments follow IRS rules. Trust-held rental income retained above " + EX(M.TRUST_TOP_2026) + " is taxed at 37% (2026).", "Have the CPA model each intended use; distribution planning matters if the trust holds the asset."], "status": "Verified", "sources": ["irs_rental", "irs_rp2532", "irs_1041"]},
    ]
    body = callout("No premium is a verified fact yet",
                   "Insurance figures are planning bands and owner guesses, not quotes. California's homeowners market is mid-rebuild under the CDI Sustainable Insurance Strategy (catastrophe models, insurer writing commitments, FAIR Plan modernization), so near-term quotes can differ sharply from legacy premiums. Public reporting of a 29.1% average FAIR Plan increase effective October 15, 2026 could not be confirmed on a CDI page at the check date and is flagged rather than treated as verified.",
                   "warning")
    body += make_table("Operating-cost inputs, bands and evidence needed",
                       ["Cost / income line", "Rounded figure or band", "How to verify / replace"],
                       rows,
                       "Owner-supplied figures are the owner's rounded descriptions. Scenario bands are labeled assumptions for planning, not measurements.")
    body += cards("Coverage and use checks", [
        ("Insurance gap", "The FAIR Plan covers limited perils; compare standard coverage and any DIC wrap rather than treating a FAIR Plan policy as complete.", "pages/sources.html"),
        ("Solar tariff", "Determine interconnection date, NEM/NBT tariff, true-up rules and export-credit treatment from account records.", "pages/sources.html"),
        ("Rental use", "Confirm permitted units, rent-regulation coverage, deposits and lease terms before applying projected gross rent.", "pages/questions.html"),
    ], current="pages/operating-costs.html")
    return render_page("pages/operating-costs.html", "Costs, insurance and utility evidence",
                       "Carrying-cost bands for both properties with the evidence needed to replace every estimate — owner-supplied figures rounded to $10, market bands flagged.",
                       body, "NUMBERS")


def build_black_swan() -> str:
    anchor_rows = [
        {"cells": ["1929–1954 equity collapse and recovery", "Federal Reserve History reports the Dow fell 89% peak-to-trough and did not regain its prior high until November 1954.", "Long drawdowns and delayed nominal recovery are possible. The Dow is a price index, not a diversified portfolio."], "status": "Historical", "sources": ["fed_1929"]},
        {"cells": ["2007–2009 Great Recession", "Federal Reserve History reports an approximately 57% S&P 500 peak-to-trough decline and about a 30% average U.S. home-price decline.", "Equity and housing risk overlap in a broad crisis; national averages do not predict a specific property."], "status": "Historical", "sources": ["fed_2008"]},
        {"cells": ["June 2022 inflation peak", "BLS reports CPI rose 9.1% over the 12 months through June 2022 — the largest since 1981.", "One high-inflation year erodes purchasing power and raises replacement/repair costs; it is not an annual forecast."], "status": "Historical", "sources": ["bls_cpi"]},
    ]
    for label, obs, note in M.cpi_stats():
        anchor_rows.append({"cells": [f"CPI regime: {label}", obs, note],
                            "status": "Historical", "sources": ["fred_cpi"]})
    anchor_rows.append({"cells": ["Near-term rate baseline and stress", "CBO's 2026–2036 outlook: 4.3% average 10-year Treasury rate, with 4.8% and 5.8% higher-rate scenarios.", "A near-term macro anchor only — not a 50-year yield, mortgage rate or portfolio return."], "status": "Verified", "sources": ["cbo_rates"]})
    anchor_rows.append({"cells": ["Long-run growth baseline", "CBO projects real GDP growth averaging 1.6%/yr over 2025–2055 (1.8% first decade, 1.4% third), inflation at the Fed's 2% goal after 2027, 10-year rates near their 30-year average.", "Smooth official baselines are a starting point; the eras below deliberately break smoothness."], "status": "Verified", "sources": ["cbo_ltbo"]})

    path = M.irregular_path()
    proceeds = M.sale_net()
    era_rows = []
    for label, y0, y1, s, h, c in M.IRREGULAR_ERAS:
        era_rows.append({"cells": [f"{y0}–{y1}", label, P(s, 0) + " / yr", P(h, 0) + " / yr", P(c, 1) + " / yr"],
                         "status": "Assumption", "sources": ["fred_cpi", "fed_2008", "fed_1929"]})
    end_rows = []
    for year in (2030, 2040, 2050, 2060, 2076):
        if year not in path:
            continue
        s, h, p = path[year]
        const_s = (1 + M.STOCK_BASE) ** (year - 2026)
        const_h = (1 + M.VALUE_GROWTH_BASE) ** (year - 2026)
        end_rows.append({"cells": [
            str(year),
            MO(proceeds * s),
            MO(proceeds * const_s),
            MO(M.A_VALUE_2026 * h),
            MO(M.A_VALUE_2026 * const_h),
            f"price level ×{p:.2f}",
        ], "status": "Projection", "sources": ["fred_cpi", "cbo_ltbo", "sec_stocks"]})
    regimes = [
        {"cells": ["Equity drawdown during staging", "The 1929 Dow and 2007–09 S&P episodes supply severe sourced endpoints.", "The staging tool tests a crash starting halfway through staging; it does not replay an index's daily path or include dividends."], "status": "Historical", "sources": ["fed_1929", "fed_2008"]},
        {"cells": ["Equity drawdown after staging", "The same drawdown can begin after all purchases complete.", "Compare with the early-crash case; phasing preserves less dry powder when the loss starts later."], "status": "Historical", "sources": ["fed_1929", "fed_2008", "treasury_bills"]},
        {"cells": ["Lower renewal yields", "Each Treasury auction sets the next rate; future renewals are unknown today.", "Enter a lower month-13-onward yield to expose reinvestment risk — a what-if, not a rate prediction."], "status": "Assumption", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Rising market before a crash", "No official source establishes future equity returns.", "The drift control tests opportunity cost while staging; a scenario assumption, not an expected return."], "status": "Assumption", "sources": ["sec_stocks"]},
        {"cells": ["Housing slump / flat market", "Fed History: ~30% average U.S. home-price decline 2006–2009; FHFA provides broad regional indexes.", "Use a separate low-growth/flat/decline housing scenario; indexes are not parcel forecasts."], "status": "Historical", "sources": ["fed_2008", "fhfa_hpi"]},
        {"cells": ["Insurance availability / repair shock", "No public source establishes a future premium, underwriting decision or repair bill.", "Treat coverage loss, deductibles and large repairs as explicit quote-based stress inputs."], "status": "Missing", "sources": ["cdi", "cslb"]},
    ]
    body = callout("A constant growth rate is not a 50-year economic model",
                   "Inflation, rates, housing, insurance, rents and equity returns move in regimes. The irregular path below stitches sourced historical magnitudes into a deliberately harsh 50-year sequence — two 2008-magnitude shocks, a 1970s-style inflation decade and a 1973-74-style bear — to show what smooth projections hide. It is a stress illustration, not a forecast, and carries no probabilities.",
                   "warning")
    body += make_table("Measured historical anchors and computed CPI regimes",
                       ["Episode / regime", "Official observation (or computation from official data)", "How to use it"],
                       anchor_rows,
                       "CPI regime figures are computed from the published annual CPI averages (series CPIAUCNS), not estimated. Equity anchors are price-index histories, not total returns.")
    body += make_table("Illustrative irregular 50-year path (2027–2076)",
                       ["Years", "Regime label", "Stocks (nominal)", "Housing (nominal)", "CPI"],
                       era_rows,
                       "Era rates are assumptions calibrated to the sourced anchors above; ordering and duration are illustrative.")
    body += make_table("What the irregular path does to the money (versus smooth assumptions)",
                       ["Checkpoint", f"Sale proceeds ≈{MO(proceeds)} → stocks, irregular path", "Same proceeds at constant 6%/yr", "Property A value, irregular path", f"Property A at constant {P(M.VALUE_GROWTH_BASE)}/yr", "Price level"],
                       end_rows,
                       "Proceeds figure = the base-case sale estimate after 5% selling costs. The irregular path can leave real wealth nearly flat for decades; the smooth path cannot show that. Neither is a forecast.")
    body += make_table("Stress dimensions to combine",
                       ["Regime", "Evidence or status", "What to test"],
                       regimes)
    body += cards("Run the entry-risk comparison", [
        ("24–36 month Treasury staging", "Compare a 1929/2008-magnitude crash during staging with one after staging; change yields and see dollar outcomes.", "pages/phased-investing.html"),
        ("Law and assumptions", "Refresh thresholds, caps and costs at the actual event.", "pages/law-watchlist.html"),
    ], current="pages/black-swan.html")
    return render_page("pages/black-swan.html", "Black-swan economic conditions",
                       "Sourced historical anchors, computed inflation regimes, and an illustrative irregular 50-year path — because growth and inflation are never consistent over half a century.",
                       body, "STRESS TESTS")


def build_phased_investing() -> str:
    proceeds = M.sale_net()
    body = callout("Reinvestment risk belongs beside the headline",
                   "Treasury bills and notes have fixed auction rates for their terms. When a short holding matures, the next auction yield may be lower — staging can reduce early equity exposure yet leave money earning less, and a rising market makes phased buying lag lump-sum entry. The tool below shows both effects in dollars.",
                   "warning")
    instrument_rows = [
        {"cells": ["Treasury bills", "4–52 week terms; rate fixed at auction; interest federally taxable, state/local exempt; sellable before maturity.", "A 3-month ladder reinvests 8–12 times across a 24–36 month staging window — each roll is a reinvestment point."], "status": "Verified", "sources": ["treasury_bills"]},
        {"cells": ["Treasury notes", "2-, 3-, 5-, 7- and 10-year terms; the 2-year note spans the staging horizon with one rate locked; same tax treatment.", "A note sold before maturity can trade above or below par; holding to maturity avoids that price risk."], "status": "Verified", "sources": ["treasury_notes"]},
    ]
    body += make_table("Instrument facts", ["Instrument", "Official product terms", "Decision risk"], instrument_rows)
    worked = []
    for event, dd, tr in (("2007–09 S&P episode (57% decline, 17-month slide)", 0.57, 17),
                          ("1929 Dow episode (89% decline, ~34-month slide)", 0.89, 34)):
        for months in (24, 30, 36):
            early = M.phase_model(months=months, drawdown=dd, trough=tr, early=True)
            late = M.phase_model(months=months, drawdown=dd, trough=tr, early=False)
            scale = proceeds / 100.0
            worked.append({"cells": [
                f"{event}, staged {months} months",
                f"Crash during staging: immediate ≈{MO(early['imp_final'] * scale)} vs phased ≈{MO(early['phase_final'] * scale)} (max drawdown {P(early['imp_dd'], 0)} vs {P(early['phase_dd'], 0)})",
                f"Crash after staging: immediate ≈{MO(late['imp_final'] * scale)} vs phased ≈{MO(late['phase_final'] * scale)} (max drawdown {P(late['imp_dd'], 0)} vs {P(late['phase_dd'], 0)})",
                "Zero-yield, zero-drift isolation setting. The live tool below adds yields, drift and inflation.",
            ], "status": "Projection", "sources": ["fed_2008", "fed_1929", "treasury_bills", "treasury_notes"]})
    body += make_table("Worked dollar examples (base-case proceeds ≈" + MO(proceeds) + ")",
                       ["Scenario", "Crash begins during staging", "Crash begins after staging", "Setting"],
                       worked,
                       "Dollar figures scale the normalized model output to the base-case net proceeds. Synthetic linear drawdown between sourced peak-to-trough endpoints; no dividends, fees, taxes or recovery after the trough. Projection — not a backtest or forecast.")
    body += '''<section class="tool-section" aria-labelledby="tool-heading">
<h2 id="tool-heading">Crash-entry what-if — with a dollar view</h2>
<p class="table-note">The model runs in normalized 100-unit space (no household amount embedded); the optional dollar view scales results to the proceeds figure you enter. Enter Treasury yields net of estimated taxes and fees. Inputs are transient — nothing is sent or stored.</p>
<form id="phase-tool" class="tool-grid">
<label>Historical drawdown anchor<select id="phase-event"><option value="1929">1929 Dow episode</option><option value="2008" selected>2007–09 S&amp;P episode</option></select></label>
<label>Purchase staging period<select id="phase-months"><option value="24">24 months</option><option value="30" selected>30 months</option><option value="36">36 months</option></select></label>
<label>Peak-to-trough decline (%)<input id="phase-drawdown" type="number" min="0" max="99" step="1" value="57" inputmode="decimal"></label>
<label>Peak-to-trough duration (months)<input id="phase-trough" type="number" min="1" max="120" step="1" value="17" inputmode="numeric"></label>
<label>Pre-crash equity drift (%/year)<input id="phase-drift" type="number" min="-20" max="30" step="0.1" value="0" inputmode="decimal"></label>
<label>Net Treasury yield, months 1–12 (%)<input id="phase-yield1" type="number" min="-5" max="20" step="0.1" value="0" inputmode="decimal"></label>
<label>Net renewal yield, month 13 onward (%)<input id="phase-yield2" type="number" min="-5" max="20" step="0.1" value="0" inputmode="decimal"></label>
<label>Annual inflation for purchasing-power lens (%)<input id="phase-inflation" type="number" min="-5" max="20" step="0.1" value="0" inputmode="decimal"></label>
<label>Optional dollar view — sale proceeds ($)<input id="phase-proceeds" type="number" min="100000" max="20000000" step="1000" value="2945000" inputmode="numeric"></label>
<div class="tool-actions no-print"><button id="phase-reset" type="button">Reset assumptions</button><span class="tool-assumption">0% defaults isolate timing only — they are not Treasury quotes or forecasts.</span></div>
</form>
<div class="scenario-grid" aria-live="polite">
<article class="scenario-card"><h3>Crash begins during the staging window</h3><p>Crash starts halfway through staging; results at the later of investment completion or the modeled trough.</p><dl><dt>Observation horizon</dt><dd id="early-months">—</dd><dt>Immediate — nominal</dt><dd id="early-immediate-value">—</dd><dt>Phased — nominal</dt><dd id="early-phased-value">—</dd><dt>Immediate — dollars</dt><dd id="early-immediate-dollars">—</dd><dt>Phased — dollars</dt><dd id="early-phased-dollars">—</dd><dt>Immediate — real units</dt><dd id="early-immediate-real">—</dd><dt>Phased — real units</dt><dd id="early-phased-real">—</dd><dt>Max drawdown — immediate</dt><dd id="early-immediate-dd">—</dd><dt>Max drawdown — phased</dt><dd id="early-phased-dd">—</dd></dl></article>
<article class="scenario-card"><h3>Crash begins after staging completes</h3><p>All scheduled purchases complete before the same decline begins.</p><dl><dt>Observation horizon</dt><dd id="late-months">—</dd><dt>Immediate — nominal</dt><dd id="late-immediate-value">—</dd><dt>Phased — nominal</dt><dd id="late-phased-value">—</dd><dt>Immediate — dollars</dt><dd id="late-immediate-dollars">—</dd><dt>Phased — dollars</dt><dd id="late-phased-dollars">—</dd><dt>Immediate — real units</dt><dd id="late-immediate-real">—</dd><dt>Phased — real units</dt><dd id="late-phased-real">—</dd><dt>Max drawdown — immediate</dt><dd id="late-immediate-dd">—</dd><dt>Max drawdown — phased</dt><dd id="late-phased-dd">—</dd></dl></article>
</div>
<p id="phase-status" class="tool-status" role="status">Change a control to re-run the local-only comparison.</p>
<p class="table-note">Model boundary: equal monthly equity purchases from the initial 100 units; the Treasury reserve accrues the entered yield monthly and uses the renewal yield after month 12; the final purchase includes accrued reserve. Equity grows at the entered drift until the crash, declines linearly to the selected drawdown, then stays flat at the trough. Real units divide by the inflation factor. No dividends, fees, taxes, recovery, withdrawals, property costs or probabilities. The dollar view multiplies normalized results by proceeds ÷ 100 — it embeds no household data.</p>
</section>'''
    rows = [
        {"cells": ["1929 anchor", "Federal Reserve History: 89% Dow peak-to-trough; prior high regained only in November 1954.", "The calculator starts from this drawdown endpoint; no daily prices, no dividends."], "status": "Historical", "sources": ["fed_1929"]},
        {"cells": ["2008 anchor", "Federal Reserve History: 57% S&P 500 peak-to-trough, October 2007–March 2009.", "A source-calibrated shock magnitude — not a forecast or return series."], "status": "Historical", "sources": ["fed_2008"]},
        {"cells": ["Reinvestment risk", "Treasury rates are fixed at each auction for the new security.", "Run a lower renewal-yield case beside the zero-yield isolation case."], "status": "Guidance", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["Inflation / real-value lens", "BLS: 9.1% CPI over the year through June 2022 — one observed year.", "Enter an explicit inflation stress; do not repeat a historical shock as a forecast."], "status": "Historical", "sources": ["bls_cpi"]},
        {"cells": ["Equity risk", "The SEC warns stock prices can fall and investors can lose money.", "No expected return, probability, tax rate or personal allocation is inferred here."], "status": "Verified", "sources": ["sec_stocks"]},
    ]
    body += make_table("How to read the calculator", ["Point", "Source-backed fact", "Limit / next test"], rows)
    body += paragraph("Interpretation",
                      "A staged plan buys more shares when an early decline arrives before the later installments; if the same decline starts after staging ends, all proceeds are already exposed. The drift control tests one rising-market opportunity-cost case. Use actual after-tax yields and an adviser-approved policy before any real allocation.")
    return render_page("pages/phased-investing.html", "Treasury staging and phased stock entry",
                       "A source-calibrated stress comparison for parking sale proceeds in 3-month to 2-year Treasuries for 24–36 months before phasing into stocks — with worked dollar examples, reinvestment risk beside the headline, and a live what-if tool.",
                       body, "STRESS TESTS")
def build_estate_thresholds() -> str:
    rows = [
        {"cells": ["Federal basic exclusion — 2026 deaths", EX(M.EXCLUSION_2026), "Filing test = gross estate + adjusted taxable gifts + specific gift-tax exemption; other filing triggers can apply. Estate-level, not per heir."], "status": "Verified", "sources": ["irs_estate", "irs_rp2532"]},
        {"cells": ["Federal basic exclusion — 2027 deaths", EX(M.EXCLUSION_2027), "Announced by the IRS (IR-2026-133); the next-year threshold, not a future-year projection."], "status": "Verified", "sources": ["irs_2027"]},
        {"cells": ["Current-law indexing after 2027", "OBBBA §70106 (P.L. 119-21, July 4, 2025) set the 2026 amount and directs inflation adjustment for 2027 and future years.", "Projected amounts below apply illustrative CPI scenarios to the 2027 figure — projections, not law."], "status": "Verified", "sources": ["irs_rp2532", "irs_estate_faq"]},
        {"cells": ["Annual gift exclusion", f"{EX(M.GIFT_2026)} (2026) / {EX(M.GIFT_2027)} (2027) per donor/recipient", "Separate from the lifetime exclusion; never the 'inheritance allowance'."], "status": "Verified", "sources": ["irs_2027"]},
        {"cells": ["Tax rates above the exclusion", "Top federal estate-tax rate 40% (graduated schedule in the Form 706 instructions); paid by the estate, not the beneficiary.", "Worked example below uses the top rate as a conservative illustration."], "status": "Verified", "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["California death taxes", "RTC §13301 bars state/local gift, inheritance, succession, legacy, income or estate tax on transfers by reason of death; the Controller says no California Estate Tax return for deaths on/after 2005-01-01.", "If the decedent is domiciled elsewhere, another state's tax can still apply (Q13)."], "status": "Verified", "sources": ["ca_rtc13301", "ca_death_tax"]},
        {"cells": ["Portability", "A timely Form 706 can transfer a deceased spouse's unused exclusion (DSUE); Rev. Proc. 2022-32 allows a simplified late portability election within 5 years when no filing was otherwise required.", "Portability can require filing even below the threshold — plan the filing decision with the CPA."], "status": "Verified", "sources": ["irs_estate_faq"]},
        {"cells": ["Trust/estate income brackets", f"Estates and trusts: 10/24/35/37% (2026); the 37% bracket begins over {EX(M.TRUST_TOP_2026)} of retained income; the 20% capital-gains rate begins over {EX(M.TRUST_LTCG_2026)}.", "If Property A rents before distribution, trust-level taxation can take ~37% of retained rent — distribute income or distribute the property promptly."], "status": "Verified", "sources": ["irs_rp2532", "irs_1041"]},
        {"cells": ["Beneficiary income tax", "Inherited cash and securities: no inheritance tax; basis steps up. Pre-tax retirement accounts (IRD): ordinary income as withdrawn. Rental income after distribution: beneficiary's rates.", "Classify the estate's assets early — the same headline 'inheritance' can be worth materially different after-tax amounts."], "status": "Verified", "sources": ["irs_basis", "irs_estate"]},
    ]
    fut_rows = []
    for year in (2030, 2035, 2040, 2045, 2050):
        fut_rows.append({"cells": [
            str(year),
            MO(M.exclusion_at(year, M.INFLATION_LOW)),
            MO(M.exclusion_at(year, M.INFLATION_BASE)),
            MO(M.exclusion_at(year, M.INFLATION_HIGH)),
        ], "status": "Projection", "sources": ["irs_rp2532", "irs_2027", "fred_cpi"]})
    home_total = M.A_VALUE_2026 + M.B_VALUE_2026
    head_rows = []
    for cash in (0, 2_000_000, 5_000_000, 10_000_000, 13_000_000):
        estate = home_total + cash
        excess = max(0.0, estate - M.EXCLUSION_2027)
        head_rows.append({"cells": [
            f"Homes + {MO(cash)} in cash/investments",
            MO(estate),
            MO(max(0.0, M.EXCLUSION_2027 - estate)),
            f"{MO(excess)} over the 2027 exclusion → illustration at the 40% top rate: ≈{MO(excess * 0.40)}",
        ], "status": "Projection", "sources": ["irs_estate", "irs_rp2532"]})
    body = callout("The threshold is not per heir",
                   f"Federal estate tax is an estate-level transfer tax. The IRS filing test uses the decedent's gross estate plus adjusted taxable gifts and the specific gift-tax exemption. With the two homes at ≈{MO(home_total)} (2026 estimates), roughly {MO(M.EXCLUSION_2027 - home_total)} of headroom remains before the 2027 threshold is crossed — but the whole estate, prior gifts and deductions decide the actual answer.",
                   "info")
    body += make_table("Current official thresholds and rules",
                       ["Rule / year", "Official value or rule", "What it means here"], rows)
    body += make_table("How much can be inherited before federal estate tax?",
                       ["Estate composition (2026 estimates, rounded)", "Gross estate", "Headroom vs 2027 exclusion", "If over the threshold"],
                       head_rows,
                       "Illustration only: it ignores deductions (debts, expenses, marital/charitable), state of domicile, prior taxable gifts, and the graduated rate schedule (the 40% top rate overstates the bill on modest excess). Projection rows — replace with the CPA's calculation.")
    body += make_table("Projected exclusion amounts (scenario indexing of the 2027 figure)",
                       ["Year", f"CPI {P(M.INFLATION_LOW)}", f"CPI {P(M.INFLATION_BASE)}", f"CPI {P(M.INFLATION_HIGH)}"],
                       fut_rows,
                       "OBBBA directs annual indexing after 2026; the CPI path is unknown. Any future Congress can change the exclusion — see the law watchlist. Projections, not law.")
    body += paragraph("What would change this answer",
                      "A larger cash bequest, lifetime gifts already used, a non-California domicile, retirement-account composition, portability facts, or a statutory change. Re-check the IRS annual revenue procedure and enacted statutes in the actual year of death; do not compound today's exclusion forward as if it were guaranteed.")
    return render_page("pages/estate-thresholds.html", "Estate tax, gift exclusion and headroom",
                       "Verified federal thresholds and California's no-death-tax rule, the headroom math on the rounded estate picture, projected exclusion ranges to 2050, and the trust-income brackets that shape rental decisions.",
                       body, "LAW & PROCESS")


def build_process() -> str:
    steps = [
        ("Step 1 — Death / trust becomes irrevocable", "Day 0", "The trust instrument governs who acts and when. Collect the executed trust, amendments, deed and trustee contacts immediately.", "ca_prob160617"),
        ("Step 2 — Trustee notice to beneficiaries", "By day 60", "Probate Code §16061.7 requires the statutory notice in specified events, including when a revocable trust becomes irrevocable at death. Serve and document.", "ca_prob160617"),
        ("Step 3 — Change-in-ownership statement", "By day 150", "RTC §480 requires the statement for specified real-property transfers by reason of death, including through a trust. File with the county and keep proof; ask the assessor about any Proposition 19 claim packet.", "ca_rtc480"),
        ("Step 4 — Valuation and basis records", "Months 1–9", "Obtain date-of-death appraisals for every property; the executor's basis statement (Form 8971/Schedule A when required) fixes the income-tax basis for the heirs.", "irs_basis"),
        ("Step 5 — Estate inventory and Form 706 decision", "By month 9", "Compute gross estate + adjusted taxable gifts against the year-of-death exclusion. If required (or for portability), Form 706 is due 9 months after death; Form 4768 buys up to 6 more months. Tax payment clocks are separate.", "irs_estate_faq"),
        ("Step 6 — Decide the Property A path", "Months 1–12", "The occupancy decision must be made early: the family-home exclusion needs the transferee's principal residence within 1 year plus the homeowners' exemption filing. Trustee authority to occupy must exist.", "boe_prop19"),
        ("Step 7 — File the exclusion claim", "By year 3 (or before any third-party transfer)", "BOE guidance: the intergenerational exclusion claim is generally filed within 3 years of transfer or before a transfer to a third party. Calendar it alongside the 1-year occupancy/exemption deadline — they are separate clocks.", "boe_prop19"),
        ("Step 8 — Insurance, utilities and tenant setup", "Before occupancy or rental", "Bind use-appropriate insurance on both properties, transfer utilities, confirm legal units and leases on Property B, and reserve taxes and repairs before taking on rental risk.", "cdi"),
        ("Step 9 — Trust income reporting", "Annually, if required", "A fiduciary may need Form 1041 for trust/estate income. Retained rental income above the low trust threshold is taxed at 37% (2026) — distribute or distribute the asset.", "irs_1041"),
        ("Step 10 — Implement the chosen path", "After the gates close", "Occupy A (Path 1) or list/sell A and begin the 24–36 month Treasury staging plan (Path 2), keeping B rented. Re-check insurance and law annually.", "sec_stocks"),
    ]
    step_rows = [{"cells": [title, when, what, ""], "status": "Guidance", "sources": [src]} for title, when, what, src in steps]
    timeline = SafeHTML(
        '<ol class="timeline">'
        '<li><span class="tl-when">Day 0</span><span class="tl-what">Death / trust irrevocable</span></li>'
        '<li><span class="tl-when">Day 60</span><span class="tl-what">Trustee notice (§16061.7)</span></li>'
        '<li><span class="tl-when">Day 150</span><span class="tl-what">Change-in-ownership statement (RTC §480)</span></li>'
        '<li><span class="tl-when">Month 9</span><span class="tl-what">Form 706 if required (+6 mo via Form 4768)</span></li>'
        '<li><span class="tl-when">Month 12</span><span class="tl-what">Move in + homeowners\u2019 exemption (Prop 19)</span></li>'
        '<li><span class="tl-when">Year 3</span><span class="tl-what">Exclusion claim deadline (or before 3rd-party transfer)</span></li>'
        '<li><span class="tl-when">Ongoing</span><span class="tl-what">Annual bills, Form 1041 if needed, law re-checks</span></li>'
        '</ol>'
    )
    body = callout("Start each clock from its legal trigger",
                   "The trust-notice clock, county property-tax filing, federal estate return and Proposition 19 claims have different triggers and responsible filers. Counsel should confirm actual dates from the death and transfer records; the timeline below shows relative deadlines only.",
                   "warning")
    body += timeline
    body += make_table("Step-by-step inheritance and decision sequence",
                       ["Step", "Timing", "What happens / what to do", "Official source"],
                       [{"cells": [c[0], c[1], c[2], ""], "status": "Guidance", "sources": [c[3]]} for c in steps],
                       "Every row's link verifies the rule cited. Operational steps (valuation, insurance, path implementation) cite the governing IRS or agency guidance for that activity.")
    body += paragraph("No dates have been assigned",
                      "The public page publishes no personal calendar. Once counsel confirms the date of death, title change dates, trust status and occupancy plan, replace these relative deadlines with calendar dates in a private checklist.")
    return render_page("pages/inheritance-process.html", "Inheritance process and deadline timeline",
                       "A visual timeline of the statutory deadlines and a ten-step walkthrough of the trust-based transfer — from the day of death through implementing the chosen path.",
                       body, "LAW & PROCESS")


def build_law_watchlist() -> str:
    rows = [
        {"cells": ["Proposition 19 repeal attempts", "Official: the initiative 'Repeals voter-enacted changes to property tax rules for transfers between family members' FAILED — SOS Memorandum #26138, May 18, 2026 (signatures insufficient). Proposition 19 remains in force.", "Future attempts can restart; check the SOS initiative status pages before relying on any repeal. Plan under current law."], "status": "Verified", "sources": ["sos_initiatives", "sos_ballot"]},
        {"cells": ["SCA-4 (2025–2026) — verification correction", "Official status: SCA-4 (Archuleta) is a veterans' property-tax exemption measure, NOT a restoration of parent-child exclusions (some third-party commentary claimed otherwise). Held in Senate Appropriations on 05/14/26.", "A good reminder to verify bill identity on leginfo before acting on commentary. Watch the actual bill list for genuine Prop 19 amendments."], "status": "Verified", "sources": ["leginfo_sca4"]},
        {"cells": ["SB 79 transit-oriented development (affects Property B's market)", "Signed October 10, 2025; effective July 1, 2026 (Gov. Code §65912.155 et seq.). Qualifying transit-oriented housing becomes an allowed use near specified transit stops in urban transit counties.", "Can change redevelopment value and zoning expectations near transit in San Francisco; confirm whether either property is within a qualifying corridor before valuing 'highest and best use.'"], "status": "Verified", "sources": ["hcd_sb79"]},
        {"cells": ["Federal estate/gift exclusion", "Current law: $15,000,000 (2026) / $15,480,000 (2027), indexed for inflation after 2026 per OBBBA §70106.", "Future Congresses can reduce or expand it; proposals to lower the exclusion appear regularly. Search Congress.gov near the decision; treat nothing as law until enacted."], "status": "Verified", "sources": ["irs_rp2532", "irs_2027", "congress_legislation"]},
        {"cells": ["Federal proposal — S.4196", "Congress.gov lists the bill as introduced and referred to Senate Finance as of 2026-11-15. The draft would set a $3,500,000 basic exclusion and revise estate, gift and generation-skipping transfer tax rules; its text proposes applying to deaths and gifts after December 31, 2026 if enacted.", "This could materially change the estate-level calculation, but it is not enacted and must not replace the current IRS baseline."], "status": "Proposal—not law", "sources": ["congress_s4196_status", "congress_s4196_text", "irs_estate"]},
        {"cells": ["Federal proposal — H.R.601", "As checked 2026-11-15, Congress.gov lists H.R. 601 as introduced and referred to House Ways and Means and Budget. The draft proposes a 20% rate for estate, gift and generation-skipping transfer taxes, with a proposed effective date for transfers after December 31, 2024 if enacted.", "Not enacted. Re-check Congress.gov before using any tax rate or planning around a proposed rate."], "status": "Proposal—not law", "sources": ["congress_hr601_text"]},
        {"cells": ["Federal proposal — S.587", "As checked 2026-11-15, Congress.gov lists S. 587 as introduced and referred to Senate Finance. The draft proposes repealing federal estate and generation-skipping transfer taxes and separately changing gift-tax rules.", "Not enacted. This proposal is distinct from current federal estate and gift tax law; confirm status and enacted text before relying on it."], "status": "Proposal—not law", "sources": ["congress_s587_status", "congress_s587_text"]},
        {"cells": ["California SB 974 — limited Proposition 19 amendment", "Chaptered as Chapter 665, Statutes of 2026; the official status page marks it non-urgency. It amends RTC §63.2 to recognize a Probate Code §3604 special-needs trust as an eligible transfer medium for the specified exclusion; relationship, residence, occupancy, value and claim conditions remain. Separate claim-timing relief applies only to qualifying property connected with specified 2025 wildfires.", "Counsel should verify the operative date, exact trust qualification, remaining eligibility and current assessor guidance. This is not a general rule for all family transfers or ordinary trusts."], "status": "Verified", "sources": ["ca_sb974_status", "ca_sb974_text", "ca_rtc63"]},
        {"cells": ["Nov 3, 2026 tax-related statewide measures (Props 3, 40–43)", "The official ballot titles are: 3 — extends the existing tax on high incomes for schools and health care; 40 — imposes a one-time tax on certain taxpayers; 41 — prohibits new state taxes that exclude revenue from the state spending limit and requires audits of new state special taxes; 42 — prohibits new state personal property taxes and certain retroactive state taxes; 43 — limits voters' ability to raise local government revenue. The election date (Nov 3, 2026) is before the check date (Nov 15, 2026); certified results were not read here.", "Read the certified results and each measure's full text and fiscal analysis before relying on any tax effect; a ballot title is not a legal outcome by itself."], "status": "Not verified", "sources": ["sos_qualified"]},
        {"cells": ["SF rent-control allowable increase", "The SF Rent Board page states a 1.6% allowable annual increase for covered units from March 1, 2026 through February 28, 2027. Secondary articles that cite a different figure are superseded by this official page.", "Re-check the Rent Board page each year; confirm whether a unit is covered before applying any increase."], "status": "Verified", "sources": ["sf_rent_board"]},
        {"cells": ["SF Rent Board 2026 notices (demolition/major renovation protections; security-deposit interest)", "The Rent Board page lists a January 23, 2026 item on tenant protections for demolition and major renovation, and a security-deposit interest change effective March 1, 2026. Their substance was not extracted into this site.", "Counsel should read the linked notice text and confirm how it affects Property B's units and planned renovations."], "status": "Not verified", "sources": ["sf_rent_board"]},
        {"cells": ["California bills", "No other specific pending California bill changing the parent-child rules is incorporated. A bill becomes relevant only after chaptering and effective-date verification.", "Search leginfo (property tax, transfers, insurance, rent) before each annual review."], "status": "Not verified", "sources": ["ca_legislation"]},
        {"cells": ["Insurance market regulation", "CDI's Sustainable Insurance Strategy is active: approved wildfire catastrophe models, insurer commitments to write distressed areas, FAIR Plan modernization/depopulation. Public reporting of a 29.1% average FAIR Plan increase (effective 10/15/2026) was not confirmable on a CDI page at the check date.", "Refresh quotes at decision time; availability and pricing are moving targets. The unconfirmed rate figure is flagged, not treated as verified."], "status": "Not verified", "sources": ["cdi_sis", "cdi"]},
        {"cells": ["Rent and tenant protections", "Statewide Civil Code caps have coverage conditions and exemptions; San Francisco adds local rent-regulation regimes whose coverage of this building is unverified.", "Counsel should confirm the building's registration, coverage and just-cause rules before any rent change or occupancy switch."], "status": "Missing", "sources": ["ca_rent", "ca_legislation"]},
        {"cells": ["Solar tariffs", "NEM/NBT rules set export-credit economics; net-billing export credits are usually below retail.", "Confirm the account's tariff and interconnection date; do not assume legacy NEM terms transfer to a new account holder."], "status": "Verified", "sources": ["cpuc_solar"]},
        {"cells": ["Long-run economic assumptions", "CBO's long-run horizon ends at 2055 (real GDP 1.6%/yr average; inflation at 2% after 2027). No official source forecasts household values, premiums, rents or returns for 2040–2050.", "Use several labeled stress paths (projections page + black-swan page); never promote a scenario into a forecast."], "status": "Verified", "sources": ["cbo_ltbo", "cbo_rates", "fhfa_hpi"]},
    ]
    body = callout("Watch enacted law, not headlines",
                   "This page distinguishes current statutes and official records from commentary and proposals. Two verification corrections are recorded: the Prop 19 repeal initiative officially failed in May 2026, and SCA-4 is a veterans' exemption measure despite third-party claims that it restores parent-child protections.",
                   "info")
    body += make_table("Law and market watchlist",
                       ["Topic", "Current official baseline / verified status", "What to re-check"],
                       rows)
    body += paragraph("No future-year legal projection is law",
                      "The estate-threshold projections and the Prop 19 cap projections are labeled scenarios. S.4196, H.R.601 and S.587 are introduced proposals only; SB 974 is a chaptered state amendment with limited scope (Chapter 665, Statutes of 2026), and its operative date must be confirmed before application. None predicts the law at a future transfer. Search official bill systems and verify enacted text, effective dates, local code and agency implementation near the event.")
    return render_page("pages/law-watchlist.html", "Law and market watchlist",
                       "Verified current status of the rules that can change the decision — including two corrections to widely repeated claims — and the re-check list for the years ahead.",
                       body, "LAW & PROCESS")


def build_brief() -> str:
    cf = M.path_cashflows()
    rows = [
        {"cells": ["Attorney / trustee", "What does the trust permit (occupy, rent, sell), when does title change, what debts/notices apply, and is this a parent-child or grandparent-grandchild transfer?", "Executed trust + amendments, deed, relationship evidence, trustee authority.", "Action needed"], "status": "Action needed", "sources": ["ca_prob160617", "ca_rtc480", "boe_prop19"]},
        {"cells": ["CPA / estate attorney", f"Gross estate vs year-of-death exclusion (2027: {EX(M.EXCLUSION_2027)}; projected ranges on the estate page). Any prior gifts? Portability? Are assets cash/securities (step-up) or retirement accounts (IRD)? Any non-CA domicile?", "Inventory, gift history, beneficiary designations, domicile evidence.", "Action needed"], "status": "Action needed", "sources": ["irs_estate", "irs_estate_faq", "irs_basis"]},
        {"cells": ["CPA / appraiser", "Date-of-death value and basis for both properties; tax result of selling A near transfer (little gain expected after step-up) versus renting (depreciation, trust brackets over " + EX(M.TRUST_TOP_2026) + ").", "Appraisals, executor basis statement, improvement/depreciation records.", "Action needed"], "status": "Action needed", "sources": ["irs_basis", "irs_rental", "irs_rp2532"]},
        {"cells": ["Property-tax adviser / assessor", f"Confirm Prop 19 eligibility (occupancy within 1 year; cap ≈{EX(M.PROP19_CAP_2025_2027)} for transfers through 2/15/2027 with February 2027 adjustment pending) and what happens on later move-out. Verify B's odd tax ratio ({P(M.RATIO_B, 2)}).", "Rolls, bills, exemption records, BOE-19-P/G claim analysis, assessor confirmation of move-out treatment.", "Action needed"], "status": "Action needed", "sources": ["boe_prop19", "boe_lta25009", "ca_rtc63"]},
        {"cells": ["Landlord-tenant counsel", "B's legal unit count, rent-regulation coverage, lease terms; lawfulness of renting all three units.", "Permits, leases, rent registry, tenant notices.", "Action needed"], "status": "Action needed", "sources": ["ca_rent", "irs_rental"]},
        {"cells": ["Insurance broker", f"Written quotes: homeowners (A) and landlord (B). Owner guesses ≈{MO(M.A_INS_OWNER)}/{MO(M.B_INS_OWNER)} look low against planning bands {MO(M.A_INS_LOW)}–{MO(M.A_INS_HIGH)}/{MO(M.B_INS_LOW)}–{MO(M.B_INS_HIGH)}.", "Quotes, replacement-cost basis, exclusions, FAIR Plan/DIC analysis.", "Action needed"], "status": "Action needed", "sources": ["cdi", "cdi_sis"]},
        {"cells": ["Utility / solar provider", "Actual bills and the solar tariff/interconnection terms (export credit value).", "24 months of bills; NEM/NBT agreement; true-up history.", "Action needed"], "status": "Action needed", "sources": ["sfpuc_rates", "cpuc_solar"]},
        {"cells": ["Investment adviser", f"If selling A: net proceeds ≈{MO(M.sale_net())} (base case), tax reserve, and a written staging policy for the 24–36 month Treasury phase-in — including the reinvestment-risk case.", "Proceeds estimate, liquidity plan, current net yields, risk tolerance, IPS.", "Action needed"], "status": "Action needed", "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
    ]
    body = callout("Meeting objective",
                   "Leave with a written conditional recommendation: occupy-A vs sell-A, the assumptions behind it, the deadlines to calendar, tax and insurance reserves, and the specific facts that would reverse the answer. Keep personal records out of this public repository.",
                   "info")
    body += make_table("One-page adviser handoff checklist", ["Adviser", "Question to answer", "Private records to bring", "Status"], rows)
    body += paragraph("Decision boundary",
                      f"Property A is the trust transfer (2040–2050 window); Property B is already owned and currently produces ≈{MO(M.B_RENT_2UNITS_MO)}/mo from two units. Leading paths: occupy A within the one-year window + rent all three B units (≈{MO(cf['p1'][0])}–{MO(cf['p1'][1])}/yr estimated net, 2026 money) versus sell A and stage ≈{MO(M.sale_net())} into diversified assets while keeping B (≈{MO(cf['p2'][0])}–{MO(cf['p2'][1])}/yr from B plus portfolio). Renting A without occupancy is projected weakest.")
    body += paragraph("Privacy",
                      "This printable brief contains no address, postal code, parcel identifier or name; all household figures are rounded to $10. Print this page or Save as PDF, and store completed adviser notes outside the public repository.")
    return render_page("pages/attorney-cpa-brief.html", "Attorney & CPA briefing sheet",
                       "One-page, print-ready meeting checklist with the rounded figures and deadlines that matter — no identifying details included.",
                       body, "ADVISER HANDOFF")


def build_flagged() -> str:
    rows = [
        {"cells": ["F-01 — Public Git history exposure", "The repository is public. The active site is generic and rounded, but reachable historical commits and PR material may retain earlier pre-rounding case details. This branch cannot rewrite public main history.", "Treat historic material as exposed. A ready-to-run scrub script and owner runbook are in tools/history_scrub_runbook.md; repository-owner/admin must coordinate the rewrite, forks, caches and GitHub Support."], "status": "Missing", "sources": ["github_history"]},
        {"cells": ["F-02 — Property B's tax ratio is irregular", f"The rounded owner table implies ≈{P(M.RATIO_B, 2)} of assessed value versus ≈{P(M.RATIO_A, 2)} for Property A. Direct assessments, partial-bill reporting or rate structure could explain it — unverified.", "Obtain both secured bills with all line items from the county; the projection tables use the ratios as supplied and do not adjust them."], "status": "Owner-supplied", "sources": ["boe_pub29"]},
        {"cells": ["F-03 — Insurance figures are guesses and bands", f"Owner guesses ≈{MO(M.A_INS_OWNER)}/{MO(M.B_INS_OWNER)} appear low versus market bands {MO(M.A_INS_LOW)}–{MO(M.A_INS_HIGH)}/{MO(M.B_INS_LOW)}–{MO(M.B_INS_HIGH)}. The widely reported 29.1% FAIR Plan increase (10/15/2026) could not be confirmed on a CDI page at the check date.", "Obtain written quotes for both intended uses; re-shop at decision time; verify rate actions via CDI before citing them."], "status": "Missing", "sources": ["cdi", "cdi_sis"]},
        {"cells": ["F-04 — Market rent for Property A is a scenario band, not a quote", "The $5,500–$7,500/month band is a labeled planning assumption. HUD FMR area values must be read from HUD's FMR data system for the exact county and were not confirmable here at the figure level.", "Pull HUD FMR for the county and local comps; replace the band before final modeling."], "status": "Not verified", "sources": ["hud_fmr"]},
        {"cells": ["F-05 — Future law and market path", "Verified baselines run only to 2026–2027 amounts and CBO horizons (2036/2055). The transfer is 2040–2050.", "No future exclusion, cap, house price, CPI, rent, premium or return value is claimed as fact; all future values are labeled projections. Re-check near the event."], "status": "Projection", "sources": ["irs_2027", "cbo_ltbo", "fhfa_hpi"]},
        {"cells": ["F-06 — Failed official retrievals", "404s/fetch failures on 2026-11-14/15: FTB inheritance page, BOE county-assessor directory, BOE Publication 801 PDF, CPUC water-utilities URL, SF Treasurer vacancy-tax page, Santa Clara County Assessor homepage.", "No claim rests on those URLs; working alternatives (BOE Prop 19 page, LTA 2025/009, statute) are linked instead. The SF vacancy-tax path and any county rate must be confirmed from a working official page."], "status": "Not verified", "sources": ["ftb_404", "boe_assessor_404", "boe_pub801_404", "cpuc_water_404", "sf_treasurer_vacancy_404", "scc_assessor_fetch"]},
        {"cells": ["F-07 — Equity drawdown magnitudes beyond the sourced anchors", "Only 1929 (−89% Dow) and 2007–09 (−57% S&P) are sourced endpoints here. Other well-known drawdowns (2000–02, 2022) have no single official source located in this pass and are not quoted.", "If those magnitudes are needed, add an official source first; nothing is inferred to fill the gap."], "status": "Not verified", "sources": ["fed_1929", "fed_2008"]},
        {"cells": ["F-08 — Model simplifications", "Projections use constant scenario rates; the staging tool uses synthetic linear drawdowns and flat troughs; the irregular path is an illustrative stitch of sourced magnitudes. No dividends, fees, taxes, debt or probabilities.", "Treat every output as an instrument for comparing paths under stated assumptions, not a forecast. Replace assumptions with quotes and appraisals as they arrive."], "status": "Assumption", "sources": ["fed_1929", "fed_2008", "treasury_bills", "bls_cpi"]},
        {"cells": ["F-09 — Local identifiers are deliberately absent", "No address, postal code, parcel identifier, name or exact (pre-rounding) figure appears in the public tree. Some market context requires metro-level description (e.g., San Francisco rent regulation).", "If sharper local analysis is needed, do it in a private document; do not add identifiers here. Verify local ordinances with counsel."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["F-11 — SF rent-control coverage cutoff unverified", "Secondary commentary cites a pre-June 13, 1979 coverage cutoff for San Francisco rent control; the ordinance text confirming it was not read.", "Counsel should read the ordinance text and the Rent Board's coverage rules before relying on any unit's covered status."], "status": "Not verified", "sources": ["sf_rent_board"]},
        {"cells": ["F-12 — Nov 3, 2026 measure outcomes", "The Nov 3, 2026 election is before the check date. The qualified-measure list was read, but certified results and full measure text were not read.", "Read the certified results and each voter guide before treating any of Props 3 or 40–43 as settled law."], "status": "Not verified", "sources": ["sos_qualified"]},
        {"cells": ["F-13 — SF vacancy-tax rule unconfirmed", "An official SF vacancy-tax (empty-homes) rule may apply to a vacant unit of Property B, but the official URL failed retrieval and no rate, threshold or filing duty is stated here.", "Confirm the current SF Treasurer vacancy-tax page, registration duty and any exemption before leaving a unit vacant."], "status": "Not verified", "sources": ["sf_treasurer_vacancy_404"]},
        {"cells": ["F-14 — Japan-bubble cross-check not published", "A Bank of Japan cross-check for 1989-era asset-price and discount-rate figures was attempted; the official source was not retrieved and secondary sources conflict, so no figure is published.", "If a Japan-bubble regime reference is wanted for the black-swan page, retrieve the official BoJ series first; nothing is inferred meanwhile."], "status": "Not verified", "sources": ["boj_unverified"]},
        {"cells": ["F-10 — Third-party claims corrected during research", "Two widely repeated claims failed official verification: the Prop 19 repeal initiative did NOT qualify (official failure memo) and SCA-4 is a veterans' exemption measure, not parent-child relief.", "Recorded so future reviews do not re-adopt the errors; always verify against leginfo/SOS/IRS before citing."], "status": "Verified", "sources": ["sos_initiatives", "leginfo_sca4"]},
    ]
    body = callout("Privacy issue remains urgent",
                   "The current tree and website are rounded and generic. The Git repository is public, and pre-rounding history cleanup has NOT been completed. A noindex tag and a cleaned tree do not erase old commits, PR diffs, forks, caches or clones — the scrub script and runbook await repository-owner action.",
                   "warning")
    body += make_table("Flagged for review — unresolved items do not imply a verified answer",
                       ["Flag", "What is unresolved", "Required action"],
                       rows)
    body += paragraph("History-remediation limitation",
                      "GitHub documents history rewriting as a coordinated, disruptive operation; other refs, pull requests, forks, caches and clones may retain copies. This workspace pins work to one feature branch and prohibits pushing other branches, so this session prepared tools/history_scrub_runbook.md (script + step-by-step) rather than force-pushing a rewrite. The repository owner/admin should preserve a secure private archive, run the scrub, and contact GitHub Support about PR diffs and caches.")
    return render_page("pages/flagged-for-review.html", "Flagged for review",
                       "Material uncertainties, verification corrections, and the unresolved privacy/history issue — published so they can be reviewed after the site goes live.",
                       body, "EVIDENCE")


def build_glossary() -> str:
    rows = [
        {"cells": ["Gross estate", "Property and interests included in the federal estate-tax calculation before deductions; includes more than one house plus cash, securities and more.", "Do not compare one heir's share with the federal filing threshold."], "status": "Verified", "sources": ["irs_estate"]},
        {"cells": ["Basic exclusion amount", "Federal estate/gift amount available for a given year under current law, subject to prior taxable transfers.", "Not the annual gift exclusion; not a guarantee about later years."], "status": "Verified", "sources": ["irs_estate", "irs_rp2532"]},
        {"cells": ["Portability / DSUE", "Election (on a timely Form 706) to transfer a deceased spouse's unused exclusion to the surviving spouse.", "Can require filing even below the threshold; Rev. Proc. 2022-32 offers a limited late-election method."], "status": "Verified", "sources": ["irs_estate_faq"]},
        {"cells": ["IRD (income in respect of a decedent)", "Assets whose income was never taxed to the decedent — typically pre-tax retirement accounts — taxed to the beneficiary on receipt/withdrawal.", "A dollar of IRA inheritance is worth less after income tax than a dollar of stepped-up securities."], "status": "Verified", "sources": ["irs_basis"]},
        {"cells": ["Income-tax basis", "Amount used to compute gain on sale; inherited property basis is generally date-of-death fair market value, subject to exceptions.", "Separate from the county's property-tax assessed value."], "status": "Verified", "sources": ["irs_basis"]},
        {"cells": ["Factored base year value", "California's Prop 13 assessed value: the original base-year value adjusted by up to 2% per year.", "Why A's assessment (≈" + MO(M.A_AV_2026) + ") is far below market value (≈" + MO(M.A_VALUE_2026) + ")."], "status": "Verified", "sources": ["boe_pub29"]},
        {"cells": ["Proposition 19 value cap", "The family-home exclusion covers value up to the factored base year value plus an adjusted $1,000,000 amount (" + EX(M.PROP19_CAP_2025_2027) + " for transfers 2/16/2025–2/15/2027; adjusted biennially by the FHFA California HPI).", "Above the cap, the excess is reassessed even when the exclusion applies."], "status": "Verified", "sources": ["boe_prop19", "boe_lta25009"]},
        {"cells": ["Partial reassessment", "Result of the cap math: taxable value = factored base year value + the amount by which market value exceeds factored value + cap.", "For high-value homes this is close to full reassessment minus the cap — the 2040/2050 tables quantify it."], "status": "Verified", "sources": ["boe_prop19"]},
        {"cells": ["Section 121 exclusion", "Up to $250,000 ($500,000 joint) of gain on a principal residence may be excluded if the 2-of-5-year ownership and use tests are met.", "Relevant only to Property B if ever sold while/after being the residence."], "status": "Verified", "sources": ["irs_topic701"]},
        {"cells": ["Mixed path", "A combination — e.g., occupy one property, rent units of another, sell one asset and stage the proceeds.", "Model each asset, unit and tax position separately."], "status": "Guidance", "sources": ["irs_rental", "ca_rent"]},
        {"cells": ["Sequence risk", "The effect of when returns occur; an early decline hurts more than the same decline later while funds are being invested.", "Stress crash-during-staging and crash-after-staging; neither is a probability."], "status": "Guidance", "sources": ["fed_1929", "fed_2008", "sec_stocks"]},
        {"cells": ["Reinvestment risk", "The possibility that maturing proceeds must be reinvested at a lower yield.", "A 24–36 month Treasury ladder defers equity exposure but does not lock renewal yields."], "status": "Verified", "sources": ["treasury_bills", "treasury_notes"]},
        {"cells": ["NEM / net billing (NBT)", "California solar export-credit regimes; under net billing, export credits are usually below retail rates.", "Equipment alone does not establish future credit value — the account tariff does."], "status": "Verified", "sources": ["cpuc_solar"]},
        {"cells": ["FAIR Plan / DIC wrap", "California's insurer-of-last-resort dwelling-fire program (limited perils) plus a Difference-in-Conditions policy that fills gaps.", "A FAIR Plan policy alone is not complete homeowners coverage."], "status": "Verified", "sources": ["cdi"]},
        {"cells": ["Fair Market Rent (FMR)", "HUD's annual 40th-percentile gross-rent benchmark for specified programs.", "Not an appraisal, lease amount or lawful-rent determination."], "status": "Verified", "sources": ["hud_fmr"]},
        {"cells": ["SB 79", "California transit-oriented development law (effective July 1, 2026) allowing qualifying housing near transit stops in urban transit counties.", "Can affect zoning expectations and value near transit in San Francisco."], "status": "Verified", "sources": ["hcd_sb79"]},
    ]
    body = make_table("Terms used in this workspace", ["Term", "Plain-language meaning", "Practical distinction"], rows)
    return render_page("pages/glossary.html", "Glossary",
                       "Short definitions for the legal, tax, property and investment terms used across the decision process.",
                       body, "EVIDENCE")


def build_sources() -> str:
    rows = []
    for key, item in SOURCES.items():
        rows.append({
            "cells": [item["label"], item["scope"], f"Direct page fetch: {item.get('checked', CHECKED)}"],
            "status": "Verified" if item["verified"] else "Not verified",
            "sources": [key],
        })
    body = callout("Source scope matters",
                   "Every source is an official government, regulator, or platform documentation page. A link verifies only the scope shown in its description; it never verifies a private property fact. Failed fetches stay flagged rather than silently replaced.",
                   "info")
    body += make_table("Official source register", ["Source", "What it supports / does not support", "Checked"], rows)
    body += paragraph("Verification method",
                      "Verified sources were fetched directly on the check date and read for the narrow statement shown. Computed figures (CPI regimes, projection tables) derive arithmetically from the linked official series or from labeled assumptions; the method is stated next to each table. Re-check legal text and agency guidance at the actual transfer date.")
    return render_page("pages/sources.html", "Official source register",
                       "A direct-source ledger with retrieval date, verification status and a clear statement of each source's limits.",
                       body, "EVIDENCE")


def build_privacy() -> str:
    rows = [
        {"cells": ["Rounding rule", "Every household or cost figure on this site is rounded to the nearest $10; estimates are shown as ranges where the owner was uncertain. Published statutory amounts (IRS thresholds, the BOE cap, utility tariff averages) appear exactly as published because rounding would misstate the law.", "This is the owner's required de-identification standard: exact pre-rounding figures must not appear anywhere in the public tree."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Identifiers excluded", "No street address, postal code, parcel identifier, name, account number or deed reference appears. Properties are 'Property A' (trust transfer) and 'Property B' (already owned); metro-level context appears only where market analysis requires it.", "Do not add deeds, trust papers, tax bills, leases, statements or identifiable values to this repository."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Public hosting", "GitHub Pages is a public static website. noindex discourages search indexing but is not access control.", "Treat everything here as world-readable."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Current tree", "The generated site embeds only rounded figures, computed projections and published amounts. No projection CSV, appraisal, bill or household input file exists in the tree.", "The build reads no private inputs; tools/models.py contains only the rounded figures displayed on the site."], "status": "Guidance", "sources": ["github_history"]},
        {"cells": ["Git history / copies", "Earlier commits and PR diffs may retain pre-rounding case material; forks, cached views and clones cannot be erased by a normal commit. Cleanup has NOT been completed.", "Owner/admin must run tools/history_scrub_runbook.md (script + steps), preserve a private archive first, and involve GitHub Support for PR/caches. Treat prior values as exposed until then."], "status": "Missing", "sources": ["github_history"]},
        {"cells": ["Browser controls", "Calculator inputs are transient; suggestion review choices are stored only in this browser's local storage and never transmitted (the site makes no network calls of any kind).", "Clear site data to remove saved review choices; do not use a public computer for confidential inputs."], "status": "Guidance", "sources": ["github_history"]},
    ]
    body = callout("Privacy warning — history is not scrubbed",
                   "The current site and tree follow the rounding and anonymization rules above. The public Git history still contains pre-rounding material from earlier revisions. This session cannot force-push a history rewrite (branch rules) and did not claim to have scrubbed it — use the runbook in tools/ and coordinate with the repository owner.",
                   "warning")
    body += make_table("Privacy boundary and remaining exposure", ["Area", "Current state", "Safeguard / limitation"], rows)
    body += paragraph("No third-party tracking",
                      "The pages use local HTML, CSS and JavaScript only: no analytics, remote fonts, remote scripts, API calls or form submissions. External official sources open only when a reader follows a link.")
    return render_page("pages/privacy.html", "Privacy and limitations",
                       "The exact de-identification rules this site follows, what was done, and what remains exposed in Git history until the owner runs the scrub runbook.",
                       body, "EVIDENCE")


def suggestion_table() -> str:
    suggestions = [
        ("S01", "Privacy", "Run the Git history scrub runbook", "Repository owner: preserve a private archive, run tools/history_scrub_runbook.md, contact GitHub Support about PR diffs and caches, then verify no pre-rounding figures remain reachable.", "The single highest-priority privacy item; the current tree is clean but history is not.", ["github_history"]),
        ("S02", "Decision", "Force the occupancy decision in writing", "Have the family document whether they will occupy Property A within the one-year window. Everything else is downstream of this answer.", "Forks the plan between Path 1 (occupy) and Path 2 (sell + stage).", ["boe_prop19"]),
        ("S03", "Tax", "Order a written Prop 19 pre-assessment from the county", "Ask the assessor for the projected post-transfer taxable value under both occupancy and non-occupancy, including the move-out rule (Q19).", "Replaces the projection tables with the county's own math and resolves the mixed-path question.", ["boe_prop19", "ca_rtc63"]),
        ("S04", "Tax", "Separate estate, basis and assessment schedules", "One schedule for the gross estate/706 test, one for inherited basis, one for county assessment — three distinct calculations.", "They are different legal systems; conflating them is the classic expensive error.", ["irs_estate", "irs_basis", "boe_pub29"]),
        ("S05", "Property", "Verify B's legal units and rent-regulation coverage", "Reconcile permits, leases, rent registration, deposits and local rules before projecting the third unit's rent.", "Gross rent from an unverified unit is neither lawful nor reliable.", ["ca_rent", "hud_fmr"]),
        ("S06", "Operations", "Get four insurance quotes (two uses × two properties)", "Homeowners and landlord quotes for both buildings, with replacement-cost basis and exclusions; test FAIR Plan fallback.", "Insurance availability can reverse an apparent winner and delay occupancy.", ["cdi", "cdi_sis"]),
        ("S07", "Utilities", "Reconcile 24 months of bills and the solar tariff", "Actual water/electric bills plus the signed solar interconnection and tariff documents.", "Replaces every utility band with measured costs and fixes the credit's true value.", ["sfpuc_rates", "cpuc_solar"]),
        ("S08", "Markets", "Keep reinvestment risk beside any staging headline", "Compare 24–36 months of Treasury staging under crash-during and crash-after entry, lower renewal yields, inflation and pre-crash drift.", "Staging changes risk timing; it does not make equities safe.", ["treasury_bills", "treasury_notes", "fed_2008"]),
        ("S09", "Governance", "Re-run this workspace annually", "Refresh the exclusion, the Prop 19 cap (biennial February adjustments), insurance, rents and law; log changes in the review queue.", "Today's rules do not decide a 2040–2050 question.", ["irs_2027", "boe_lta25009", "cbo_ltbo"]),
        ("S10", "Estate", "Classify the cash: retirement (IRD) versus stepped-up assets", "Map every account to its after-tax value to the beneficiary before comparing bequest sizes.", "The same headline inheritance can differ materially after income tax.", ["irs_basis", "irs_rp2532"]),
        ("S11", "Estate", "Model trust income distribution timing", "If Property A rents before distribution, model distributing income (or the property) to avoid the 37% trust bracket over " + EX(M.TRUST_TOP_2026) + ".", "Trust-level taxation can consume rental returns almost entirely.", ["irs_rp2532", "irs_1041"]),
        ("S12", "Valuation", "Test SB 79 highest-and-best-use for Property B", "Confirm whether B sits near a qualifying transit stop where upzoning could change its redevelopment value.", "A zoning change can dominate decades of rent assumptions — in either direction.", ["hcd_sb79"]),
        ("S13", "Model", "Replace every assumption band with a quote or bill", "Each replaced band (insurance, rent, maintenance, sale costs) shrinks the flagged list and sharpens the ranking.", "The ranking is only as good as the bands behind it.", ["cdi", "cslb", "hud_fmr"]),
        ("S14", "Verification", "Re-verify every legal figure at the event", "Thresholds, caps, deadlines and brackets change; the flagged page lists exactly what to re-check with counsel and the CPA.", "No projection on this site is a legal opinion.", ["irs_estate", "boe_prop19", "ca_rtc13301"]),
    ]
    rows = []
    for ident, group, title, action, why, sources in suggestions:
        select = SafeHTML(
            f'<select class="review-choice" data-id="{esc(ident)}" aria-label="Review decision for {esc(ident)}">'
            '<option value="Not reviewed">Not reviewed</option>'
            '<option value="Investigate">Investigate</option>'
            '<option value="Selected">Selected for testing</option>'
            '<option value="Defer">Defer</option></select>'
        )
        rows.append({
            "cells": [ident, group, title, action, why, select],
            "status": "Guidance",
            "sources": sources,
        })
    return make_table("Reviewable suggestions — no change is applied automatically",
                      ["ID", "Category", "Suggestion", "What to do", "Why it may improve the decision", "Review choice"],
                      rows)


def build_suggestions() -> str:
    body = callout("Choose what to review before implementing anything",
                   "Each choice is saved only in this browser's local storage. Nothing is sent to a server and no change to the site or decision is made by selecting an option. Use Reset to clear the local review queue.",
                   "info")
    body += '<p class="review-summary" id="review-summary" role="status" aria-live="polite">Loading review queue…</p><p class="no-print"><button id="reset-reviews" type="button">Reset review choices</button></p>'
    body += suggestion_table()
    body += paragraph("Suggested approval gates",
                      "Do not implement a financial or site change until the relevant owner has reviewed it, the necessary private records exist, a professional confirms applicable law, and the result is reproducible under stated assumptions. The 24–36 month staging plan (S08) and the occupancy decision (S02) are the two highest-leverage items.")
    return render_page("pages/suggestions.html", "Suggestions for review",
                       "A selectable review queue for improving decision quality. Suggestions are proposals, not automatic changes or personalized advice.",
                       body, "DECISION")


def build_decision_log() -> str:
    record_rows = [
        {"cells": ["D-01 — Asset separation recorded", "Property A = trust transfer (2040–2050 window). Property B = already owned. Modeled separately with rounded owner inputs.", "Recorded", "Both assets keep independent value, assessment, tax, rent and cost columns everywhere in this workspace."], "status": "Guidance", "sources": ["boe_pub29", "irs_rental"]},
        {"cells": ["D-02 — Conditional recommendation recorded", "Occupy A within the one-year window + rent all three B units if the family will genuinely move; otherwise sell A near transfer and stage proceeds while keeping B fully rented.", "Recorded (conditional)", "Forks on Q18 (true occupancy intent) and Q19 (assessor's move-out treatment)."], "status": "Guidance", "sources": ["boe_prop19", "irs_basis"]},
        {"cells": ["D-03 — Third-unit rental deferred", "Renting B's unrented unit is modeled as a scenario band only; permits, coverage and lease status are unverified.", "Deferred", "Close Q6/Q7 with permits and leases before treating the band as income."], "status": "Missing", "sources": ["ca_rent", "sf_rent_board"]},
        {"cells": ["D-04 — Treasury staging policy deferred", "24–36 month staging is presented as a stress-tested option, not an adopted policy; no allocation has been approved.", "Deferred", "Requires net proceeds, tax reserve, yields and an adviser-approved policy (S08)."], "status": "Missing", "sources": ["treasury_bills", "sec_stocks"]},
        {"cells": ["D-05 — Rent-growth assumption tightened", "Projected rent growth for Property B moved from 2.0% to the SF Rent Board's 1.6% allowable increase for covered units (Mar 2026–Feb 2027).", "Recorded (coverage unverified)", "If a unit is uncovered, revisit; re-check the Board's annual figure each cycle."], "status": "Verified", "sources": ["sf_rent_board"]},
        {"cells": ["D-06 — History scrub remains open", "Public Git history still holds pre-rounding material; the scrub script and runbook await repository-owner action.", "Action needed", "Highest-priority privacy item (S01). Treat prior values as exposed until done."], "status": "Missing", "sources": ["github_history"]},
    ]
    compact = [
        ("S01", "Run the Git history scrub runbook", "Medium (owner/admin)", "Critical — removes exposure"),
        ("S02", "Force the occupancy decision in writing", "Low (family)", "None"),
        ("S03", "Order a written Prop 19 pre-assessment", "Low (assessor letter)", "Low — handled privately"),
        ("S04", "Separate estate, basis and assessment schedules", "Medium (CPA)", "Low — kept private"),
        ("S05", "Verify B's legal units and rent-regulation coverage", "Medium (counsel)", "Low — records stay private"),
        ("S06", "Get four insurance quotes (two uses × two properties)", "Medium (broker)", "Low — quotes stay private"),
        ("S07", "Reconcile 24 months of bills and the solar tariff", "Low (owner records)", "Low — bills stay private"),
        ("S08", "Keep reinvestment risk beside any staging headline", "Low (analysis)", "None"),
        ("S09", "Re-run this workspace annually", "Low (process)", "None"),
        ("S10", "Classify the cash: retirement (IRD) versus stepped-up assets", "Low (CPA)", "Low — account data stays private"),
        ("S11", "Model trust income distribution timing", "Medium (CPA)", "Low — trust data stays private"),
        ("S12", "Test SB 79 highest-and-best-use for Property B", "Medium (adviser)", "None"),
        ("S13", "Replace every assumption band with a quote or bill", "High (iterative)", "Low — inputs stay private"),
        ("S14", "Re-verify every legal figure at the event", "Low (process)", "None"),
    ]
    rows = []
    for ident, title, effort, privacy in compact:
        select = SafeHTML(
            f'<select class="review-choice" data-id="{esc(ident)}" aria-label="Review decision for {esc(ident)}">'
            '<option value="Not reviewed">Not reviewed</option>'
            '<option value="Investigate">Investigate</option>'
            '<option value="Selected for testing">Selected for testing</option>'
            '<option value="Defer">Defer</option></select>'
        )
        rows.append({"cells": [ident, title, effort, privacy, select], "status": "Guidance", "sources": ["github_history"] if ident == "S01" else ["cbo_rates"]})
    body = callout("Nothing here is applied automatically",
                   "The decision record documents what has been decided, deferred or left open; the queue gives each suggestion an effort estimate and a privacy impact. Review choices are saved only in this browser's local storage and are shared with the suggestions page (same IDs).",
                   "info")
    body += make_table("Decision record — decided, deferred, open",
                       ["Entry", "What", "Status", "Gate"], record_rows)
    body += '<p class="review-summary" id="review-summary" role="status" aria-live="polite">Loading review queue…</p><p class="no-print"><button id="reset-reviews" type="button">Reset review choices</button></p>'
    body += make_table("Review queue — effort and privacy impact",
                       ["ID", "Suggestion", "Effort", "Privacy impact", "Review choice"],
                       rows,
                       "Full rationale for each suggestion is on the suggestions page. No change is applied by selecting an option.")
    body += paragraph("Suggested approval gates",
                      "Do not implement a financial or site change until the relevant owner has reviewed it, the necessary private records exist, a professional confirms applicable law, and the result is reproducible under stated assumptions.")
    return render_page("pages/decision-log.html", "Decision log and review queue",
                       "What this workspace has decided, deferred and left open — plus a selectable review queue with effort and privacy impact for each suggestion. Nothing is applied automatically.",
                       body, "DECISION")
