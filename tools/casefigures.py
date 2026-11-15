#!/usr/bin/env python3
"""Anonymized working figures, rendered as source-linked page sections.

WHY THIS MODULE EXISTS
----------------------
The public site was built deliberately blank: every private value was left as an
em-dash so that nothing could be fingerprinted. The owner has since asked for
the decision analysis to show real, clear numbers and projections, rounded to
the nearest ten dollars so they cannot be traced back to a source document.

This module is the compromise between those two requirements. It adds the working
figures as a clearly separated layer:

  * Every amount is rounded to the nearest ten dollars.
  * No name, street address, parcel or assessor identifier, trust name, account
    number, date of birth or document image appears anywhere.
  * The only location detail is the county and the public postal area, which is
    needed to reproduce the utility-tariff and insurance research.
  * Every row carries an evidence badge. Owner-supplied figures are labelled
    "Owner-supplied" and are never presented as verified.
  * Anything that could not be confirmed against an official page stays blank
    and is cross-referenced on the flagged page.

EVIDENCE LADDER USED HERE
-------------------------
  "Verified"     Read from an official page and quoted within its scope.
  "Official"     A statute or agency rule.
  "Historical"   An official historical observation.
  "Owner"        From the owner's own records, rounded, not verified.
  "Projection"   Arithmetic on owner figures plus a stated assumption.
  "Assumption"   A modelling input chosen by the reader or by default.
  "Missing"      Unknown. Blank by design; never filled with an inference.

Property A is the home expected to transfer through a trust. Property B is the
three-unit building the decision maker already owns and lives in. They are kept
separate in every table because they have different owners, bases, assessments
and clocks.
"""
from __future__ import annotations

import casedata as cd

# Evidence labels available in the shared builder.
VERIFIED = "Verified"
OFFICIAL = "Official"
HISTORICAL = "Historical"
OWNER = "Owner-supplied"
PROJECTION = "Projection"
ASSUMPTION = "Assumption"
MISSING = "Missing"
GUIDANCE = "Guidance"
ACTION = "Action needed"


def money(value: float) -> str:
    return f"${cd.money(value):,}"


def rate(value: float) -> str:
    return f"{value * 100:.3f}%"


def pct(value: float, places: int = 1) -> str:
    return f"{value * 100:.{places}f}%"


def num(value: float) -> str:
    """Render a rounded whole-dollar figure with thousands separators."""
    return f"{cd.money(value):,}"


# --------------------------------------------------------------- page: intro
CASE_INTRO = (
    "The owner's working figures, rounded to the nearest ten dollars and stripped of every "
    "personal identifier, are published below so the analysis can be checked rather than "
    "asserted. They are the owner's own records, not official determinations. Each row names "
    "the evidence that would replace an estimate."
)

CASE_DISCLAIMER = (
    "These are working figures, not conclusions. A rounded assessment history plus a public "
    "postal area could in principle be matched against a county assessment roll. That residual "
    "risk is documented on the privacy page. If it is not acceptable, remove the postal areas "
    "and re-run the utility and insurance research at county level."
)


# ------------------------------------------------------------------ sections
def asset_definitions() -> tuple[str, list[dict]]:
    """The assets, and the distinction that governs the whole analysis."""
    rows = [
        {
            "cells": [
                "Property A",
                "Anticipated transfer through a revocable trust",
                cd.PROPERTY_A["county"] + ", " + cd.PROPERTY_A["area"],
                "Not owned by the decision maker today",
                money(cd.PROPERTY_A["value_now"]),
                "Owner estimate as of November 2026. Not an appraisal.",
                "Rounded to ten dollars. Expected to transfer inside the 2040-2050 window.",
            ],
            "status": OWNER,
            "sources": ["irs_basis", "boe_pub29"],
        },
        {
            "cells": [
                "Property B",
                "Already owned by the decision maker",
                cd.PROPERTY_B["county"] + ", " + cd.PROPERTY_B["area"],
                "Owned today, and the current residence",
                money(cd.PROPERTY_B["value_now"]),
                "Owner estimate as of November 2026. Not an appraisal.",
                "Three units, two let. Carries its own basis, assessment and tenancies.",
            ],
            "status": OWNER,
            "sources": ["irs_basis", "boe_pub29"],
        },
        {
            "cells": [
                "Why they stay separate",
                "Different owners, bases, assessments and clocks",
                "Both in California",
                "A choice about one must not silently assume the other's numbers",
                "—",
                "No official source combines them.",
                "Property A's tax line is discontinuous at transfer; Property B's is continuous.",
            ],
            "status": GUIDANCE,
            "sources": ["boe_pub29", "ca_rtc51"],
        },
    ]
    return (
        "The two assets, and why they are never combined",
        ["Asset", "Role", "Location", "Ownership state", "Owner's value estimate", "Basis of the estimate", "What makes it distinct"],
        rows,
    )


def property_a_history() -> tuple[str, list[str], list[dict]]:
    rows = []
    prev = None
    for year, tax, assessed in cd.A_HISTORY:
        change = "-"
        if prev is not None and tax is not None:
            change = f"{(tax - prev) / prev * 100:+.1f}%"
        if tax is not None:
            prev = tax
        rows.append({
            "cells": [
                str(year),
                money(tax) if tax is not None else "not yet billed",
                change,
                money(assessed),
            ],
            "status": OWNER,
            "sources": ["boe_pub29", "ca_rtc218"],
        })
    return (
        "Property A — billed tax and enrolled assessment, rounded to ten dollars",
        ["Year", "Property tax billed", "Change in bill", "Enrolled assessment"],
        rows,
    )


def property_b_history() -> tuple[str, list[str], list[dict]]:
    rows = []
    prev = None
    for year, tax, assessed in cd.B_HISTORY:
        change = "-"
        if prev is not None:
            change = f"{(tax - prev) / prev * 100:+.1f}%"
        prev = tax
        rows.append({
            "cells": [str(year), money(tax), change, money(assessed)],
            "status": OWNER,
            "sources": ["boe_pub29", "ca_rtc51"],
        })
    return (
        "Property B — billed tax and enrolled assessment, rounded to ten dollars",
        ["Year", "Property tax billed", "Change in bill", "Enrolled assessment"],
        rows,
    )


def step_up_arithmetic(inputs: dict) -> tuple[str, list[str], list[dict]]:
    s = cd.scenario(inputs)
    a = s["a"]
    rows = [
        {"cells": ["Market value at transfer", money(a["value_at_transfer"]),
                   "Owner estimate grown at the appreciation assumption. Not an appraisal."],
         "status": PROJECTION, "sources": ["irs_basis", "fhfa_hpi"]},
        {"cells": ["Enrolled assessment at transfer", money(a["assessed_at_transfer"]),
                   "Factored base year value grown at the annual cap."],
         "status": PROJECTION, "sources": ["ca_rtc51", "boe_pub29"]},
        {"cells": ["Adjusted value limit at transfer", money(a["prop19_limit"]),
                   f"Published amount is ${cd.PROP19_LIMIT_NOW:,} for transfers {cd.PROP19_LIMIT_FROM} through {cd.PROP19_LIMIT_TO}. Carrying it forward uses an assumption."],
         "status": ASSUMPTION, "sources": ["boe_prop19", "fhfa_hpi"]},
        {"cells": ["New taxable value if occupied", money(a["taxable_prop19"]),
                   "Market value less the adjusted limit, because the excess above the limit is positive."],
         "status": PROJECTION, "sources": ["ca_rtc63", "boe_prop19"]},
        {"cells": ["New taxable value if rented", money(a["taxable_full"]),
                   "Full reassessment at market value, with no homeowners' exemption."],
         "status": PROJECTION, "sources": ["ca_rtc63", "ca_rtc218"]},
        {"cells": ["Annual tax today", money(a["tax_now"]),
                   "Derived from the owner's own last bill. The county rate was not retrieved."],
         "status": OWNER, "sources": ["boe_pub29", "scc_assessor_fetch"]},
        {"cells": ["Annual tax if occupied", money(a["tax_prop19"]),
                   f"About {money(a['tax_prop19'] / 12)} a month. A multiple of about {a['tax_multiple_prop19']}x."],
         "status": PROJECTION, "sources": ["ca_rtc63", "boe_pub29"]},
        {"cells": ["Annual tax if rented", money(a["tax_full"]),
                   f"About {money(a['tax_full'] / 12)} a month. A multiple of about {a['tax_multiple_full']}x."],
         "status": PROJECTION, "sources": ["ca_rtc63", "ca_rtc218"]},
    ]
    return (
        f"The step-up arithmetic at the {inputs['transfer_year']} default transfer year",
        ["Line", "Amount", "How it is built and what is missing"],
        rows,
    )


def a_projection_rows(inputs: dict, years: list[int]) -> list[dict]:
    rows = []
    for year in years:
        mkt = cd.market_value("A", year, inputs)
        assessed = cd.assessed_value("A", year, inputs)
        cap = cd.prop19_limit(year, inputs)
        occ = cd.new_taxable_value(mkt, assessed, cap)
        rows.append({
            "cells": [
                str(year),
                money(mkt),
                money(assessed),
                money(cd.property_tax(assessed, cd.A_EFFECTIVE_RATE, True)) if year <= inputs["transfer_year"] else "transferred",
                money(cd.property_tax(occ, cd.A_EFFECTIVE_RATE, True)),
                money(cd.property_tax(cd.money(mkt), cd.A_EFFECTIVE_RATE, False)),
            ],
            "status": PROJECTION,
            "sources": ["ca_rtc51", "ca_rtc63", "boe_prop19"],
        })
    return rows


def b_projection_rows(inputs: dict, years: list[int]) -> list[dict]:
    rows = []
    for year in years:
        assessed = cd.assessed_value("B", year, inputs)
        rows.append({
            "cells": [
                str(year),
                money(cd.market_value("B", year, inputs)),
                money(assessed),
                money(cd.property_tax(assessed, cd.B_EFFECTIVE_RATE, False)),
                money(cd.b_rent_income(year, inputs)),
                money(cd.annual_operating("B", year, inputs)["total"]),
            ],
            "status": PROJECTION,
            "sources": ["boe_pub29", "irs_rental", "ca_rent"],
        })
    return rows


def operating_rows(inputs: dict) -> tuple[str, list[str], list[dict]]:
    op_a = cd.annual_operating("A", inputs["transfer_year"], inputs)
    op_b = cd.annual_operating("B", inputs["transfer_year"], inputs)
    o = cd.OPERATING
    rows = [
        {"cells": ["A", "Water", f"${o['a_water_low']} to ${o['a_water_high']} a month", money(op_a["water"]),
                   "Owner-supplied range. The retail water provider for the parcel was not confirmed."],
         "status": OWNER, "sources": ["water_board", "cpuc_water_404"]},
        {"cells": ["A", "Electricity, net of solar", f"About ${o['a_electric_low']} to ${o['a_electric_high']} a month in credit", money(abs(op_a["electric"])) + " credit",
                   "Owner-supplied range. Export credits under net billing are usually below retail and depend on the tariff and interconnection date."],
         "status": OWNER, "sources": ["cpuc_solar"]},
        {"cells": ["A", "Insurance", f"About {money(o['a_insurance'])} a year", money(op_a["insurance"]),
                   "Owner's estimate, not a quote. Obtain written quotes for owner-occupied and landlord use."],
         "status": MISSING, "sources": ["cdi"]},
        {"cells": ["A", "Upkeep and repair", f"{cd.DEFAULT_INPUTS['maintenance_a'] * 100:.1f}% of value a year", money(op_a["maintenance"]),
                   "Assumption only. Replace with inspection findings and three years of actual spend."],
         "status": ASSUMPTION, "sources": ["cslb", "irs_rental"]},
        {"cells": ["B", "Water, three units", f"${o['b_water_low']} to ${o['b_water_high']} a month", money(op_b["water"]),
                   "Owner-supplied range. The account's metered usage is not known."],
         "status": OWNER, "sources": ["water_board", "cpuc_water_404"]},
        {"cells": ["B", "Electricity, common and vacant unit", f"${o['b_electric_low']} to ${o['b_electric_high']} a month", money(op_b["electric"]),
                   "Owner-supplied range, not verified against bills."],
         "status": OWNER, "sources": ["cpuc_solar"]},
        {"cells": ["B", "Insurance", f"About {money(o['b_insurance'])} a year", money(op_b["insurance"]),
                   "Owner's estimate, not a quote. A three-unit building needs a landlord or mixed-use policy."],
         "status": MISSING, "sources": ["cdi"]},
        {"cells": ["B", "Upkeep and repair", f"{cd.DEFAULT_INPUTS['maintenance_b'] * 100:.1f}% of value a year", money(op_b["maintenance"]),
                   "Assumption only, set higher than Property A because the building is older and has more units."],
         "status": ASSUMPTION, "sources": ["cslb", "irs_rental"]},
        {"cells": ["B", "Gross rent", f"{money(o['b_rent_income'])} a month for {o['b_rent_units_rented']} of {o['b_rent_units_total']} units", money(cd.b_rent_income(inputs["transfer_year"], inputs)),
                   "Owner-supplied figure, not verified against leases. Increases are subject to the statutory cap and local rules."],
         "status": OWNER, "sources": ["ca_rent", "sf_rent_board", "irs_rental"]},
    ]
    return (
        "Operating costs and income at the default transfer year",
        ["Property", "Item", "Owner's range or figure", "Modelled annual amount", "What is missing"],
        rows,
    )


def carrying_rows(inputs: dict) -> tuple[str, list[str], list[dict]]:
    s = cd.scenario(inputs)
    a = s["a"]
    op_a = a["operating"]
    rented_total = a["tax_full"] + op_a["total"]
    b_tax = cd.property_tax(cd.assessed_value("B", 2026, inputs), cd.B_EFFECTIVE_RATE, False)
    op_b = cd.annual_operating("B", 2026, inputs)["total"]
    rows = [
        {"cells": ["Property A, occupied", money(a["tax_prop19"]), money(op_a["total"]),
                   money(a["carrying_total"]), money(a["carrying_monthly"])],
         "status": PROJECTION, "sources": ["ca_rtc63", "boe_pub29"]},
        {"cells": ["Property A, rented", money(a["tax_full"]), money(op_a["total"]),
                   money(rented_total), money(rented_total / 12)],
         "status": PROJECTION, "sources": ["ca_rtc63", "ca_rtc218"]},
        {"cells": ["Property B today", money(b_tax), money(op_b),
                   money(b_tax + op_b), money((b_tax + op_b) / 12)],
         "status": PROJECTION, "sources": ["boe_pub29", "ca_rtc51"]},
    ]
    return (
        "Annual carrying cost, excluding financing, vacancy and management",
        ["Case", "Property tax", "Operating cost", "Total a year", "Total a month"],
        rows,
    )


def paths_rows(inputs: dict) -> tuple[str, list[str], list[dict]]:
    s = cd.scenario(inputs)
    a, b, sale = s["a"], s["b"], s["sale"]
    be_rent = cd.breakeven_rent(a["taxable_full"], cd.A_EFFECTIVE_RATE, a["operating"]["total"], inputs)
    gap = sale["invested_now_end"] - sale["invested_staged_end"]
    rows = [
        {"cells": ["P1", "Mixed", "Occupy Property A; leave Property B as it is", money(a["tax_prop19"]),
                   money(b["rent_income"]) + " gross rent from B",
                   "Concentration in one asset with a large fixed annual bill and low liquidity.",
                   "Reverses if the household cannot occupy within one year, or the bill becomes unaffordable."],
         "status": PROJECTION, "sources": ["ca_rtc63", "ca_rtc218"]},
        {"cells": ["P2", "Mixed", "Occupy Property A and also let the third unit at Property B", money(a["tax_prop19"]),
                   money(b["rent_income"]) + " plus the third unit, unquoted",
                   "Adds landlord exposure at B and changes its owner-occupancy profile.",
                   "Reverses if the third unit is not lawfully lettable, or local rules or insurance change."],
         "status": PROJECTION, "sources": ["ca_rtc63", "ca_rent", "sf_rent_board"]},
        {"cells": ["P3", "Mixed", "Occupy for the qualifying year, then let Property A and return to Property B", money(a["tax_prop19"]),
                   "Market rent for A, unquoted",
                   "Depends on the statutory rule for when the exclusion later stops applying. Needs legal confirmation.",
                   "Reverses if counsel reads the statute differently, or rent does not clear the break-even."],
         "status": PROJECTION, "sources": ["ca_rtc63", "irs_rental", "hud_fmr"]},
        {"cells": ["P4", "Pure", "Let Property A from the start and keep living at Property B", money(a["tax_full"]),
                   "Market rent for A, unquoted",
                   "Pays the highest annual bill and keeps the largest concentration.",
                   f"Reverses if market rent cannot clear the break-even of about {money(be_rent)} a year before financing."],
         "status": PROJECTION, "sources": ["ca_rtc63", "ca_rtc218", "irs_rental"]},
        {"cells": ["P5", "Pure", "Sell Property A at transfer and invest the proceeds immediately", "None after sale",
                   money(sale["net_proceeds"]) + " invested",
                   "Full exposure to entry-point risk; a crash just after the sale is the worst case.",
                   "Reverses if the household needs the housing service, or a crash at entry would be unrecoverable."],
         "status": PROJECTION, "sources": ["irs_basis", "irs_121", "sec_stocks"]},
        {"cells": ["P6", "Mixed", "Sell Property A, park the proceeds in Treasury bills and notes, then phase into equities", "None after sale",
                   money(sale["net_proceeds"]) + " staged",
                   f"Trades entry-point risk for reinvestment risk. Ends about {money(gap)} behind immediate entry if markets do not fall.",
                   "Reverses if yields fall while waiting, or equities rise strongly during the staging window and never retrace."],
         "status": PROJECTION, "sources": ["treasury_bills", "treasury_notes", "sec_stocks"]},
        {"cells": ["P7", "Mixed", "Sell Property B, move into Property A, invest the Property B proceeds", money(a["tax_prop19"]),
                   f"Proceeds from B, valued about {money(b['value_at_transfer'])} at transfer",
                   "Gives up an income-producing asset with a low relative assessment to secure the exclusion.",
                   "Reverses if B's low assessment and rent are worth more than the exclusion, or the sale creates a large gain."],
         "status": PROJECTION, "sources": ["ca_rtc63", "irs_121", "boe_pub29"]},
        {"cells": ["P8", "Pure", "Sell both properties and invest everything", "None after sale",
                   money(sale["net_proceeds"] + b["value_at_transfer"] * (1 - inputs["selling_cost"])) + " invested",
                   "Maximum liquidity and diversification, but gives up both housing service and low assessed values.",
                   "Reverses if local housing cost rises faster than the portfolio, or the household wants a property anchor."],
         "status": PROJECTION, "sources": ["irs_121", "sec_stocks", "hud_fmr"]},
    ]
    return (
        "Eight paths, including five mixed paths",
        ["ID", "Type", "Path", "Annual property tax on A", "Income or proceeds", "Principal risk", "What would reverse it"],
        rows,
    )


def headline_stats(inputs: dict) -> list[tuple[str, str, str]]:
    s = cd.scenario(inputs)
    a, b, sale = s["a"], s["b"], s["sale"]
    be_rent = cd.breakeven_rent(a["taxable_full"], cd.A_EFFECTIVE_RATE, a["operating"]["total"], inputs)
    return [
        ("Property A modelled value at transfer", money(a["value_at_transfer"]), PROJECTION),
        ("Annual property tax today", money(a["tax_now"]), OWNER),
        ("Annual property tax if occupied", money(a["tax_prop19"]), PROJECTION),
        ("Annual property tax if rented", money(a["tax_full"]), PROJECTION),
        ("Break-even gross rent for A", money(be_rent), ASSUMPTION),
        ("Property B gross rent", money(b["rent_income"]), OWNER),
        ("Net proceeds if sold at transfer", money(sale["net_proceeds"]), PROJECTION),
        ("Staged versus immediate entry", money(sale["invested_staged_end"]), ASSUMPTION),
    ]


def executive_findings(inputs: dict) -> tuple[str, list[str], list[dict]]:
    s = cd.scenario(inputs)
    a, b = s["a"], s["b"]
    be_rent = cd.breakeven_rent(a["taxable_full"], cd.A_EFFECTIVE_RATE, a["operating"]["total"], inputs)
    rows = [
        {"cells": ["The step-up dominates every other number",
                   f"About {money(a['tax_now'])} today versus about {money(a['tax_prop19'])} occupied or {money(a['tax_full'])} rented at the default transfer year.",
                   "Model the assessment before the financing or rent questions."],
         "status": PROJECTION, "sources": ["ca_rtc63", "boe_prop19", "boe_pub29"]},
        {"cells": ["Occupancy is worth real money",
                   "The exclusion requires the home to be the transferor's principal residence, to become the transferee's principal residence within one year, and an exemption filing within one year.",
                   "Treat the one-year occupancy decision as a deadline, not a preference."],
         "status": OFFICIAL, "sources": ["ca_rtc63", "boe_prop19", "ca_rtc218"]},
        {"cells": ["Moving out later may not lose the value",
                   "The statute provides that when the exclusion stops applying, the base year value established at the change in ownership date, adjusted annually, is enrolled.",
                   "Confirm the wording and the county procedure with counsel before relying on it."],
         "status": OFFICIAL, "sources": ["ca_rtc63"]},
        {"cells": ["Basis resets at death",
                   "Basis of inherited property is generally fair market value at date of death, or the alternate valuation date only if a return is filed and the election is made.",
                   "Get the date-of-death valuation documented; it sets basis for every later path."],
         "status": VERIFIED, "sources": ["irs_basis", "irs_basis_pub"]},
        {"cells": ["Federal estate tax is a threshold test, not a beneficiary allowance",
                   "The 2026 Form 706 filing threshold is $15,000,000 and the 2027 basic exclusion is $15,480,000. The test uses the gross estate plus adjusted taxable gifts.",
                   "Obtain the estate inventory rather than assuming the home alone answers it."],
         "status": VERIFIED, "sources": ["irs_estate", "irs_2027", "irs_estate_faq"]},
        {"cells": ["Renting Property A needs a rent number nobody has yet",
                   f"Carrying cost if rented is about {money(a['tax_full'] + a['operating']['total'])} a year before financing. Break-even gross rent is about {money(be_rent)} a year.",
                   "Obtain three written rent opinions and compare against the break-even."],
         "status": PROJECTION, "sources": ["irs_rental", "hud_fmr", "ca_rent"]},
        {"cells": ["Sequence risk is the real reason to consider staging",
                   "The Dow did not regain its 1929 high until November 1954, about 25 years later. The S&P 500 fell 57 percent from October 2007 to March 2009.",
                   "Compare crash-during-wait with crash-after-entry before trusting any headline."],
         "status": HISTORICAL, "sources": ["fed_1929", "fed_2008"]},
        {"cells": ["Property tax is deductible only up to a cap",
                   "An individual's state and local tax deduction is limited to a combined $40,000, or $20,000 if married filing separately, subject to a modified adjusted gross income limitation but not reduced below $10,000.",
                   "Do not model the full property tax as deductible at the federal level."],
         "status": VERIFIED, "sources": ["irs_salt"]},
        {"cells": ["The two assets have very different tax behaviour",
                   f"Property B's bill is about {money(b['tax_at_transfer'])} at the transfer year against Property A's about {money(a['tax_prop19'])} if occupied, on a lower relative assessment.",
                   "Keep the two calculations separate; combining them hides the discontinuity at transfer."],
         "status": PROJECTION, "sources": ["boe_pub29", "ca_rtc51"]},
        {"cells": ["Today's rules will not be the rules at transfer",
                   "The adjusted value limit is recalculated every other February from the California house price index, and the federal exclusion is indexed from 2027. Neither guarantees a future amount.",
                   "Re-read every figure at the transfer date; nothing here promises future law."],
         "status": OFFICIAL, "sources": ["boe_prop19", "fhfa_hpi", "irs_2027"]},
    ]
    return (
        "Executive findings on the working figures",
        ["Finding", "What the model and the statutes show", "What to do with it"],
        rows,
    )


def questions_rows(inputs: dict) -> tuple[str, list[str], list[dict]]:
    s = cd.scenario(inputs)
    a = s["a"]
    rows = [
        {"cells": ["Was the home the transferor's principal residence at transfer?",
                   "Not in evidence",
                   "Get a written statement from the trustee and evidence of residence. The exclusion applies only to a principal residence of the transferor."],
         "status": ACTION, "sources": ["ca_rtc63", "boe_prop19"]},
        {"cells": ["Can the transferee occupy it within one year?",
                   "Not decided",
                   "Decide before the transfer, not after. Occupancy within one year and an exemption filing within one year are both required."],
         "status": ACTION, "sources": ["ca_rtc63", "ca_rtc218"]},
        {"cells": ["What is the tax-rate-area rate for Property A?",
                   f"Derived: about {rate(cd.A_EFFECTIVE_RATE)}",
                   "The official county rate was not retrieved. Ask the county, or read the tax-rate area from the bill itself."],
         "status": MISSING, "sources": ["scc_assessor_fetch", "boe_pub29"]},
        {"cells": ["Why does Property B's implied rate look so high?",
                   f"Derived: about {rate(cd.B_EFFECTIVE_RATE)}",
                   "That is far above the 1% general levy plus voter-approved debt. Reconcile the bill line by line and identify direct assessments and parcel taxes."],
         "status": MISSING, "sources": ["boe_pub29", "ca_rtc51", "scc_assessor_fetch"]},
        {"cells": ["What is market rent for Property A?",
                   "Not in evidence",
                   f"Obtain three written rent opinions, then compare with the break-even of about {money(cd.breakeven_rent(a['taxable_full'], cd.A_EFFECTIVE_RATE, a['operating']['total'], inputs))} a year."],
         "status": MISSING, "sources": ["hud_fmr", "irs_rental"]},
        {"cells": ["What does insurance actually cost, and is it available?",
                   "Owner estimate only",
                   "Obtain written owner-occupied and landlord quotes with replacement cost, exclusions and any FAIR Plan fallback."],
         "status": MISSING, "sources": ["cdi"]},
        {"cells": ["Who supplies water to Property A, and on what tariff?",
                   "Not confirmed",
                   "More than one provider serves the postal area. Read the provider and tariff from a current bill."],
         "status": MISSING, "sources": ["water_board", "cpuc_water_404"]},
        {"cells": ["What is the solar interconnection agreement and tariff?",
                   "Not in evidence",
                   "Export credits under net billing are usually below retail and depend on the tariff, the interconnection date and the true-up month."],
         "status": MISSING, "sources": ["cpuc_solar"]},
        {"cells": ["Is the third unit at Property B lawfully lettable?",
                   "Not in evidence",
                   "Confirm permits, unit legality and local registration before counting any additional rent."],
         "status": MISSING, "sources": ["ca_rent", "sf_rent_board"]},
        {"cells": ["What is the gross estate, including adjusted taxable gifts?",
                   "Not in evidence",
                   "The filing test adds lifetime taxable gifts to the gross estate. The home alone does not answer it."],
         "status": MISSING, "sources": ["irs_estate", "irs_estate_faq"]},
    ]
    return (
        "The questions that would move the numbers most",
        ["Question", "What is known now", "How to discover the missing information"],
        rows,
    )


def flagged_rows(inputs: dict) -> list[dict]:
    s = cd.scenario(inputs)
    a = s["a"]
    return [
        {"cells": ["F-20", "Property B implied effective rate is anomalous",
                   f"The owner's own figures imply about {rate(cd.B_EFFECTIVE_RATE)}, far above the 1% general levy plus voter-approved bonded indebtedness.",
                   "Reconcile the bill line by line and identify direct assessments, parcel taxes and supplemental items. Until then, every Property B projection is unreliable.",
                   "High"],
         "status": ACTION, "sources": ["boe_pub29", "ca_rtc51", "scc_assessor_fetch"]},
        {"cells": ["F-21", "Property A tax rate is derived, not official",
                   f"The model uses about {rate(cd.A_EFFECTIVE_RATE)}, derived from the owner's last bill. No official county tax-rate-area rate was retrieved.",
                   "Ask the county for the composite rate, or read it from the bill's tax-rate area line.",
                   "High"],
         "status": MISSING, "sources": ["scc_assessor_fetch", "boe_pub29"]},
        {"cells": ["F-22", "Retail water provider for Property A is unconfirmed",
                   "More than one provider serves the postal area. A filed tariff names the territory as portions of Cupertino among other cities, which does not confirm the parcel.",
                   "Read the provider name and tariff from a current bill.",
                   "Medium"],
         "status": MISSING, "sources": ["cpuc_water_404", "water_board"]},
        {"cells": ["F-23", "Insurance premium is an estimate for both properties",
                   f"The owner's figure of about {money(cd.OPERATING['a_insurance'])} a year for each property was not quoted. Property B is a three-unit building and needs a landlord or mixed-use policy.",
                   "Obtain written quotes with replacement cost and exclusions, and compare with the FAIR Plan and a Differences in Conditions policy.",
                   "High"],
         "status": MISSING, "sources": ["cdi"]},
        {"cells": ["F-24", "Upkeep is a placeholder percentage, not an estimate",
                   f"Modelled at {cd.DEFAULT_INPUTS['maintenance_a'] * 100:.1f}% of value for Property A and {cd.DEFAULT_INPUTS['maintenance_b'] * 100:.1f}% for Property B.",
                   "Replace with inspection-derived reserve schedules and three years of actual spend.",
                   "Medium"],
         "status": ASSUMPTION, "sources": ["cslb", "irs_rental"]},
        {"cells": ["F-25", "Market rent for Property A is unknown",
                   "No rent figure is published on this site because none has been verified.",
                   "Obtain three written rent opinions and compare with the break-even rent.",
                   "High"],
         "status": MISSING, "sources": ["hud_fmr", "irs_rental"]},
        {"cells": ["F-26", "The adjusted value limit is carried forward by assumption",
                   f"The published amount is ${cd.PROP19_LIMIT_NOW:,} for transfers {cd.PROP19_LIMIT_FROM} through {cd.PROP19_LIMIT_TO}. Carrying it to the 2040s uses an assumed rate.",
                   "Re-read the published amount for the actual transfer period; it is recalculated every other February.",
                   "High"],
         "status": ASSUMPTION, "sources": ["boe_prop19", "fhfa_hpi"]},
        {"cells": ["F-27", "Estate size is described but not quantified",
                   "The owner states the inheritance includes a considerable sum that may exceed the exempt amount. No inventory was available.",
                   "Obtain the estate inventory and prior gift history; the home alone does not answer the filing test.",
                   "High"],
         "status": MISSING, "sources": ["irs_estate", "irs_estate_faq"]},
        {"cells": ["F-28", "Transfer window is an expectation, not a date",
                   "The 2040 to 2050 window is the owner's expectation. No document establishing it was available.",
                   "Confirm from the trust; model both the early and the late end.",
                   "Medium"],
         "status": MISSING, "sources": ["ca_prob160617"]},
        {"cells": ["F-29", "Rounded working figures remain theoretically linkable",
                   "An assessment history rounded to ten dollars, combined with a public postal area, could in principle be matched against a county assessment roll.",
                   "Weigh the analytical benefit against that residual risk, and consider the banded default view proposed in the review queues.",
                   "Medium"],
         "status": ACTION, "sources": ["github_history", "boe_pub29"]},
    ]


def brief_lines(inputs: dict) -> list[tuple[str, list[str]]]:
    s = cd.scenario(inputs)
    a = s["a"]
    be_rent = cd.breakeven_rent(a["taxable_full"], cd.A_EFFECTIVE_RATE, a["operating"]["total"], inputs)
    return [
        ("The two assets", [
            f"Property A — anticipated transfer through a revocable trust, {cd.PROPERTY_A['county']}, {cd.PROPERTY_A['area']}. Not owned by the client today. Owner's estimate of value about {money(cd.PROPERTY_A['value_now'])} as of November 2026. Expected transfer window 2040 to 2050.",
            f"Property B — already owned, {cd.PROPERTY_B['county']}, {cd.PROPERTY_B['area']}. Three units, two currently let, about {money(cd.OPERATING['b_rent_income'])} a month gross on the owner's figures. Owner's estimate of value about {money(cd.PROPERTY_B['value_now'])}.",
        ]),
        ("The number that drives everything", [
            f"Modelled value of Property A at the {inputs['transfer_year']} default transfer year: about {money(a['value_at_transfer'])}.",
            f"Enrolled assessment at that year: about {money(a['assessed_at_transfer'])}.",
            f"New taxable value if the intergenerational exclusion applies: about {money(a['taxable_prop19'])}. If it does not: about {money(a['taxable_full'])}.",
            f"Annual property tax: about {money(a['tax_now'])} today, about {money(a['tax_prop19'])} if occupied, about {money(a['tax_full'])} if rented. A multiple of about {a['tax_multiple_prop19']}x or {a['tax_multiple_full']}x.",
        ]),
        ("Questions we need answered in writing", [
            "Was the home the transferor's principal residence at transfer, and can that be evidenced?",
            "Can the transferee occupy it as a principal residence within one year, and file the homeowners' exemption within one year?",
            "Does the trust permit occupancy, letting or sale, and who must consent?",
            "Confirm the statutory consequence if the exclusion later stops applying: is the base year value established at the change in ownership date, adjusted annually, the value that is enrolled?",
            "What is the gross estate, including adjusted taxable gifts, and is a federal estate return required?",
            "What is the date-of-death valuation, and was an alternate valuation date elected on a filed return?",
            f"What is the tax-rate-area rate, and why does Property B's bill imply about {rate(cd.B_EFFECTIVE_RATE)} when the general levy is 1% plus voter-approved debt and direct charges?",
            "What local transfer charges would apply on a sale?",
            "What insurance is actually available, for owner-occupied and for landlord use, and at what price?",
        ]),
        ("Modelling notes the adviser should challenge", [
            f"The effective tax rates are derived from the client's own bills, not from an official county rate. Property A about {rate(cd.A_EFFECTIVE_RATE)}, Property B about {rate(cd.B_EFFECTIVE_RATE)}.",
            f"Upkeep is modelled as a share of value ({cd.DEFAULT_INPUTS['maintenance_a'] * 100:.1f}% for A, {cd.DEFAULT_INPUTS['maintenance_b'] * 100:.1f}% for B). That is a placeholder, not an estimate.",
            f"Insurance is the client's own estimate of about {money(cd.OPERATING['a_insurance'])} a year for each property and has not been quoted.",
            f"Selling costs are assumed at {inputs['selling_cost'] * 100:.1f}% of price. Local transfer charges are not verified.",
            f"Market rent for Property A is unknown. The break-even gross rent before any financing is about {money(be_rent)} a year.",
            "The state and local tax deduction is capped at $40,000, or $20,000 if married filing separately, subject to a modified adjusted gross income limitation but not reduced below $10,000.",
            f"The adjusted value limit is ${cd.PROP19_LIMIT_NOW:,} for transfers {cd.PROP19_LIMIT_FROM} through {cd.PROP19_LIMIT_TO}, and is recalculated every other February.",
        ]),
        ("What would change our recommendation", [
            "The home is not the transferor's principal residence at transfer.",
            "Occupancy within one year is not realistic.",
            "The trust restricts occupancy, letting or sale.",
            "Insurance is unavailable or unaffordable.",
            f"Market rent cannot clear the break-even of about {money(be_rent)} a year.",
            "The estate crosses the filing threshold and liquidity is needed to pay tax.",
            "The household needs the proceeds inside the staging window.",
        ]),
    ]
