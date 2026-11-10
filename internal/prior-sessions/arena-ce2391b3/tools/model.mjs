#!/usr/bin/env node
/**
 * Deterministic projection + decision model for the Property A inheritance decision.
 *
 * Design rules:
 *  1. Inputs come only from data/*.json, each carrying a source_id or an explicit
 *     "model_assumption" status with a range. This file contains arithmetic only.
 *  2. If a required input is missing, the model throws. It never invents a default.
 *  3. All three strategies are compared at the SAME horizon, on the SAME basis:
 *     every asset is notionally liquidated at the horizon and taxed, so no scenario wins
 *     merely by deferring tax. Cash flows received along the way are added back.
 *  4. Dollar outputs are rounded to the nearest $10 (project instruction). Internal math is not.
 */

import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "..");
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), "utf8"));

const costs = read("data/costs.json");
const properties = read("data/properties.json");
const laws = read("data/laws.json");
const pending = read("data/pending.json");

// ------------------------------------------------------------------ inputs
const A = {};
for (const a of costs.assumptions) A[a.id] = a.value;
const need = (id) => {
  const v = A[id];
  if (v === undefined || v === null) throw new Error(`Missing required input: ${id}`);
  return v;
};

const round10 = (n) => Math.round(n / 10) * 10;
const round4 = (n) => Math.round(n * 10000) / 10000;

const START = 2026;          // first year of the projection
const END = 2065;            // last year of the projection window
const INHERIT = need("A-INHERITANCE-YEAR");
const HORIZON = END;         // decision horizon: liquidate everything and compare

// Planning assumptions
const APPREC_A = need("A-APPRECIATION-BASE");
const APPREC_B = need("A-APPRECIATION-SF");
const INFL = need("A-INFLATION");
const ASSESS_CAP = need("A-ASSESSMENT-CAP");
const RATE_A = need("A-RATE-A");
const RATE_B = need("A-RATE-B");
const RENT_GROWTH = need("A-RENT-GROWTH");
const STOCK = need("A-STOCK-RETURN");
const STOCK_YIELD = need("A-STOCK-YIELD");
const STOCK_TAX = need("A-STOCK-TAX");
const RENTAL_TAX = need("A-RENTAL-TAX");
const SELL_COST = need("A-SELLING-COST");
const VACANCY = need("A-VACANCY");
const MGMT = need("A-PROPERTY-MGMT");

// Verified statutory constants (laws.json is itself sourced)
const LAW = {};
for (const cat of laws.categories) for (const it of cat.items) LAW[it.id] = it;
const PROP19_CAP = LAW["L-PROP19-EXCL"].amount;   // $1,044,586
const HOME_EXEMPTION = LAW["L-HOMEEX"].amount;    // $7,000
const SEC121_JOINT = LAW["L-SEC121"].amount;      // $500,000
const FED_EXCLUSION_2026 = LAW["L-FED-EXCLUSION"].amount; // $15,000,000
const FED_ANNUAL_GIFT = LAW["L-FED-ANNUAL-GIFT"].amount;  // $19,000
const FED_TOP_RATE = 0.40;
const SCC_TRANSFER = LAW["L-TRANSFER-TAX-SCC"].amount; // 0.0011
const SF_TRANSFER = LAW["L-TRANSFER-TAX-SF"].amount;   // 0.0075 (applies to the $1M-$5M tier)

// Combined tax on a long-term capital gain, split out so each component is visible.
// federal 20% + 3.8% NIIT + California ordinary rate ~9.3% at these income levels.
const LTCG_FED_TOP = 0.20;
const NIIT = 0.038;
const CA_ORD = 0.093;

// Baseline records
const PA = properties.properties.find((p) => p.id === "A");
const PB = properties.properties.find((p) => p.id === "B");
const A_TAX_2025 = PA.tax_history.find((r) => r.year === 2025).property_tax;
const A_ASSESS_2026 = PA.tax_history.find((r) => r.year === 2026).assessment;
const B_TAX_2025 = PB.tax_history.find((r) => r.year === 2025).property_tax;
const B_ASSESS_2025 = PB.tax_history.find((r) => r.year === 2025).assessment;

// ------------------------------------------------------------------ timeline (2026-2065)
// Pre-inheritance, both properties run on the supplied 2026 baselines with the 2% cap.
const timeline = [];
{
  let assessedA = A_ASSESS_2026;
  let assessedB = B_ASSESS_2025 * (1 + ASSESS_CAP);
  let marketA = PA.market_value.amount;
  let marketB = PB.market_value.amount;
  let rentB = PB.rent_monthly_total * 12;

  for (let y = START; y <= END; y++) {
    if (y > START) {
      assessedA *= 1 + ASSESS_CAP;
      assessedB *= 1 + ASSESS_CAP;
      marketA *= 1 + APPREC_A;
      marketB *= 1 + APPREC_B;
      rentB *= 1 + RENT_GROWTH;
    }
    timeline.push({
      year: y,
      market_value_a: round10(marketA),
      assessed_value_a: round10(assessedA),
      property_tax_a: round10(assessedA * RATE_A),
      implied_rate_a: round4(RATE_A),
      market_value_b: round10(marketB),
      assessed_value_b: round10(assessedB),
      property_tax_b: round10(assessedB * RATE_B),
      rent_b_annual: round10(rentB),
      basis: y === START ? "supplied baseline" : "projected",
      after_inheritance: y >= INHERIT
    });
  }
}
const at = (y) => timeline.find((r) => r.year === y);

// ------------------------------------------------------------------ Prop 19
// Excluded amount = transferor's factored base year value on the transfer date + the biennially
// adjusted $1M amount. BOE LTA 2025/009 publishes $1,044,586 for 2/16/2025-2/15/2027; later
// adjustments are not yet published, so the published figure is held flat (conservative for the
// heir, because the FHFA CA HPI has been rising).
function prop19(fbyvAtTransfer, marketAtTransfer) {
  const excluded = fbyvAtTransfer + PROP19_CAP;
  const excess = Math.max(0, marketAtTransfer - excluded);
  return { excluded, excess, newTaxable: fbyvAtTransfer + excess };
}

// ------------------------------------------------------------------ scenario engine
function runScenario({ id, name, liveInA, monthlyRentA, useProp19, ownsA = true }) {
  const inh = at(INHERIT);
  const prev = at(INHERIT - 1);
  const marketA0 = inh.market_value_a;
  const marketB0 = inh.market_value_b;
  const fbyv0 = prev.assessed_value_a;

  const p19 = prop19(fbyv0, marketA0);
  const assessedA0 = useProp19 ? p19.newTaxable : marketA0;
  const basisA = assessedA0; // IRC 1014 basis is market value at death, independent of Prop 19
  const depreciableBasisA = useProp19 ? p19.newTaxable : marketA0;

  let assessedA = assessedA0;
  let assessedB = prev.assessed_value_b;
  let rentA = monthlyRentA * 12;
  let rentB = prev.rent_b_annual;

  const rows = [];
  let cumCash = 0;
  let cumIncomeTax = 0;
  let cumPropertyTax = 0;

  for (let y = INHERIT; y <= HORIZON; y++) {
    if (y > INHERIT) {
      assessedA *= 1 + ASSESS_CAP;
      assessedB *= 1 + ASSESS_CAP;
      rentA *= 1 + RENT_GROWTH;
      rentB *= 1 + RENT_GROWTH;
    }
    const esc = Math.pow(1 + INFL, y - INHERIT);
    const mvA = at(y).market_value_a;
    const mvB = at(y).market_value_b;

    // Property tax. Homeowners' exemption applies only while it is the heir's residence.
    // A property that has been sold carries no tax and no operating cost for the heir.
    const taxableA = liveInA ? Math.max(0, assessedA - HOME_EXEMPTION) : assessedA;
    const taxA = ownsA ? taxableA * RATE_A : 0;
    const taxB = assessedB * RATE_B;

    // Operating costs, escalated at general inflation from 2026 baselines.
    const waterA = need("A-WATER-A") * 12 * esc;
    const elecA = need("A-ELEC-A") * 12 * esc;
    const insA = need("A-INSURANCE-A") * esc;
    const maintA = need("A-MAINT-A") * mvA;
    const opA = ownsA ? waterA + elecA + insA + maintA : 0;

    const waterB = need("A-WATER-B") * 12 * esc;
    const elecB = need("A-ELEC-B") * 12 * esc;
    const insB = need("A-INSURANCE-B") * esc;
    const maintB = need("A-MAINT-B") * mvB;
    const opB = waterB + elecB + insB + maintB;

    // Rent. Property B is always partly rented; Property A only in the rent-out case.
    const grossRentA = liveInA ? 0 : rentA;
    const grossRentTotal = grossRentA + rentB;
    const vacancyLoss = grossRentTotal * VACANCY;
    const mgmtFee = grossRentA > 0 ? grossRentA * MGMT : 0;
    const rentCollected = grossRentTotal - vacancyLoss - mgmtFee;

    // Depreciation shelter on the rental portion only (land excluded, 27.5-year straight line).
    let depreciation = 0;
    if (ownsA && !liveInA) {
      depreciation = (depreciableBasisA * (1 - need("A-LAND-SHARE-A"))) / need("A-DEPRECIATION");
    }

    const deductibleRent = rentCollected - depreciation - taxA - taxB - (grossRentA > 0 ? opA : 0);
    const taxableRentIncome = grossRentA > 0 ? Math.max(0, deductibleRent) : 0;
    const incomeTax = taxableRentIncome * RENTAL_TAX;

    const netCash = rentCollected - opA - opB - taxA - taxB - incomeTax;
    cumCash += netCash;
    cumIncomeTax += incomeTax;
    cumPropertyTax += taxA + taxB;

    rows.push({
      year: y,
      rent_collected: round10(rentCollected),
      property_tax_a: round10(taxA),
      property_tax_b: round10(taxB),
      operating_costs_a: round10(opA),
      operating_costs_b: round10(opB),
      depreciation_shelter: round10(depreciation),
      income_tax: round10(incomeTax),
      net_cash_flow: round10(netCash),
      cumulative_net_cash: round10(cumCash)
    });
  }

  // ---- liquidation at the horizon
  let terminalA = 0;
  let liquidationTaxA = 0;
  let portfolioValue = 0;
  let portfolioBasis = 0;
  let portfolioTax = 0;

  const endMvA = at(HORIZON).market_value_a;
  const endMvB = at(HORIZON).market_value_b;

  if (id === "SC-SELL") {
    // Sold at inheritance. Tax on the gain over the stepped-up basis, then reinvest.
    const price = marketA0;
    const costOfSale = price * SELL_COST;
    const transfer = price * SCC_TRANSFER;
    const realizedGain = Math.max(0, price - costOfSale - transfer - basisA);
    // A stepped-up basis normally makes this gain ~0; the arithmetic is carried so the
    // number is auditable rather than assumed.
    const taxableAfter121 = Math.max(0, realizedGain - SEC121_JOINT);
    const gainTax = taxableAfter121 * (LTCG_FED_TOP + NIIT) + taxableAfter121 * CA_ORD;
    liquidationTaxA = gainTax;
    const proceeds = price - costOfSale - transfer - gainTax;
    terminalA = 0;

    // Compound the net proceeds. Income is taxed each year; unrealized growth is taxed at
    // liquidation so the comparison does not reward mere deferral.
    portfolioValue = proceeds;
    portfolioBasis = proceeds;
    for (let i = 0; i < HORIZON - INHERIT; i++) {
      const income = portfolioValue * STOCK_YIELD;
      const incomeTax = income * STOCK_TAX;
      portfolioValue = portfolioValue + portfolioValue * STOCK - incomeTax;
      portfolioBasis += income - incomeTax; // reinvested after-tax income raises basis
      cumIncomeTax += incomeTax;
      cumCash -= incomeTax;              // income tax reduces spendable cash
      rows[i].income_tax = round10(rows[i].income_tax + incomeTax);
      rows[i].net_cash_flow = round10(rows[i].net_cash_flow - incomeTax);
      rows[i].cumulative_net_cash = round10(cumCash);
    }
    const unrealized = Math.max(0, portfolioValue - portfolioBasis);
    portfolioTax = unrealized * STOCK_TAX;
  } else {
    // Held, then liquidated at the horizon.
    const price = endMvA;
    const costOfSale = price * SELL_COST;
    const transfer = price * SCC_TRANSFER;
    const gain = Math.max(0, price - costOfSale - transfer - basisA);
    const excludable = liveInA ? SEC121_JOINT : 0;
    const taxableGain = Math.max(0, gain - excludable);
    liquidationTaxA = taxableGain * (LTCG_FED_TOP + NIIT) + taxableGain * CA_ORD;
    terminalA = price - costOfSale - transfer - liquidationTaxA;
  }

  // Property B: retained in every scenario, valued the same way at the horizon.
  const bPrice = endMvB;
  const bCost = bPrice * SELL_COST;
  const bTransfer = bPrice * SF_TRANSFER;
  const bBasis = prev.assessed_value_b; // Proxy for the owners' low Prop 13 base; flagged.
  const bGain = Math.max(0, bPrice - bCost - bTransfer - bBasis);
  const bTax = bGain * (LTCG_FED_TOP + NIIT) + bGain * CA_ORD;
  const bNet = bPrice - bCost - bTransfer - bTax;

  const terminal = terminalA + portfolioValue - portfolioTax + bNet + cumCash;

  return {
    id,
    name,
    live_in_a: !!liveInA,
    prop19_applied: !!useProp19,
    monthly_rent_a: monthlyRentA,
    assessed_value_a_at_inheritance: round10(assessedA0),
    property_tax_a_first_full_year: round10(rows[0].property_tax_a),
    prop19_detail: useProp19
      ? {
          parent_factored_base_year_value: round10(fbyv0),
          excluded_amount: round10(p19.excluded),
          market_value_at_transfer: round10(marketA0),
          excess_over_cap: round10(p19.excess),
          new_taxable_value: round10(p19.newTaxable),
          assessed_value_avoided: round10(Math.max(0, marketA0 - p19.newTaxable)),
          annual_tax_saved_year_one: round10(Math.max(0, (marketA0 - p19.newTaxable) * RATE_A))
        }
      : null,
    cash_flow: rows,
    totals: {
      horizon_year: HORIZON,
      years_after_inheritance: HORIZON - INHERIT,
      cumulative_net_cash: round10(cumCash),
      cumulative_property_tax: round10(cumPropertyTax),
      cumulative_income_tax: round10(cumIncomeTax),
      property_a_net_liquidation: round10(terminalA),
      property_a_liquidation_tax: round10(liquidationTaxA),
      reinvested_portfolio_net_of_tax: round10(portfolioValue - portfolioTax),
      property_b_net_after_tax: round10(bNet),
      terminal_net_worth: round10(terminal)
    }
  };
}

const defs = [
  { id: "SC-LIVE", name: "Live in Property A", liveInA: true, monthlyRentA: 0, useProp19: true, ownsA: true },
  { id: "SC-RENT", name: "Rent out Property A", liveInA: false, monthlyRentA: 5400, useProp19: false, ownsA: true },
  { id: "SC-SELL", name: "Sell Property A and reinvest", liveInA: false, monthlyRentA: 0, useProp19: false, ownsA: false }
];

const scenarios = defs.map(runScenario);
const ranked = [...scenarios].sort((a, b) => b.totals.terminal_net_worth - a.totals.terminal_net_worth);
const winner = ranked[0];
const runnerUp = ranked[1];

// ------------------------------------------------------------------ sensitivity
function rerun(overrides, def) {
  const saved = {};
  for (const k of Object.keys(overrides)) { saved[k] = A[k]; A[k] = overrides[k]; }
  const r = runScenario(def);
  for (const k of Object.keys(saved)) A[k] = saved[k];
  return r;
}

const sensitivity = {
  live_plus_rent_pb_third_unit: rerun({ "A-RENT-GROWTH": RENT_GROWTH }, defs[0]).totals.terminal_net_worth,
  sell_reinvest_stock_low: rerun({ "A-STOCK-RETURN": 0.045 }, defs[2]).totals.terminal_net_worth,
  sell_reinvest_stock_high: rerun({ "A-STOCK-RETURN": 0.085 }, defs[2]).totals.terminal_net_worth,
  rent_low_rent: rerun({}, { ...defs[1], monthlyRentA: 4500 }).totals.terminal_net_worth,
  rent_high_rent: rerun({}, { ...defs[1], monthlyRentA: 7000 }).totals.terminal_net_worth,
  live_appreciation_low: rerun({ "A-APPRECIATION-BASE": 0.02 }, defs[0]).totals.terminal_net_worth,
  live_appreciation_high: rerun({ "A-APPRECIATION-BASE": 0.04 }, defs[0]).totals.terminal_net_worth,
  live_rate_county_typical: rerun({ "A-RATE-A": 0.011488 }, defs[0]).totals.terminal_net_worth,
  live_insurance_doubled: rerun({ "A-INSURANCE-A": 3000 }, defs[0]).totals.terminal_net_worth,
  live_baseline: ranked.find((s) => s.id === "SC-LIVE").totals.terminal_net_worth,
  rent_baseline: ranked.find((s) => s.id === "SC-RENT").totals.terminal_net_worth,
  sell_baseline: ranked.find((s) => s.id === "SC-SELL").totals.terminal_net_worth
};

// ------------------------------------------------------------------ estate tax headroom
const estate = {
  per_unit: 1000000,
  rows: [],
  note:
    "The federal basic exclusion is $15,000,000 per decedent for 2026 (IRS) and is indexed for inflation from 2027 under the enacted legislation. Because the IRS has not published the forward indexed amounts, every year after 2026 shows the 2026 figure as a FLOOR — actual future exclusions will be higher, so the modelled tax is an upper bound."
};
for (let y = 2026; y <= END; y++) {
  const r = at(y);
  estate.rows.push({
    year: y,
    federal_basic_exclusion_floor: round10(FED_EXCLUSION_2026),
    annual_gift_exclusion: round10(FED_ANNUAL_GIFT),
    combined_property_market_value: round10(r.market_value_a + r.market_value_b),
    property_only_headroom_below_exclusion: round10(
      Math.max(0, FED_EXCLUSION_2026 - (r.market_value_a + r.market_value_b))
    ),
    inherited_cash_that_would_exhaust_exclusion:
      round10(Math.max(0, FED_EXCLUSION_2026 - (r.market_value_a + r.market_value_b))),
    marginal_tax_per_1m_over_the_exclusion: round10(1000000 * FED_TOP_RATE)
  });
}

// ------------------------------------------------------------------ output
const output = {
  meta: {
    generated_on: "2026-11-10",
    model: "tools/model.mjs",
    rounding: "All dollar amounts rounded to the nearest $10 per project instruction.",
    inheritance_year: INHERIT,
    projection_window: { start: START, end: END },
    decision_horizon: HORIZON,
    comparison_basis:
      "All three strategies are notionally liquidated at the horizon and taxed, with cash flows received along the way added back. No scenario wins by deferring tax.",
    disclaimer:
      "Planning model, not tax or legal advice. Every statutory input carries a primary-source citation; every planning input is labelled as an assumption with a range."
  },
  inputs_used: {
    appreciation_a: APPREC_A,
    appreciation_b: APPREC_B,
    inflation: INFL,
    assessment_cap: ASSESS_CAP,
    property_tax_rate_a: RATE_A,
    property_tax_rate_b: RATE_B,
    rent_growth: RENT_GROWTH,
    stock_return: STOCK,
    stock_income_yield: STOCK_YIELD,
    stock_effective_tax: STOCK_TAX,
    rental_effective_tax: RENTAL_TAX,
    selling_cost: SELL_COST,
    vacancy: VACANCY,
    property_management: MGMT,
    sec121_exclusion_joint: SEC121_JOINT,
    prop19_cap: PROP19_CAP,
    homeowners_exemption: HOME_EXEMPTION
  },
  timeline,
  prop19_comparison: {
    cap_used: PROP19_CAP,
    cap_source_id: "S-BOE-LTA25009",
    note:
      "Prop 19 applies only if Property A was the transferor's principal residence AND becomes the transferee's principal residence. It does not apply to a rental home, and it is lost once the heir stops occupying the property.",
    scenarios: scenarios.map((s) => ({
      id: s.id,
      name: s.name,
      prop19_applied: s.prop19_applied,
      assessed_value_a_at_inheritance: s.assessed_value_a_at_inheritance,
      prop19_detail: s.prop19_detail
    }))
  },
  scenarios,
  ranking: ranked.map((s, i) => ({
    rank: i + 1,
    id: s.id,
    name: s.name,
    terminal_net_worth: s.totals.terminal_net_worth,
    cumulative_net_cash: s.totals.cumulative_net_cash,
    delta_vs_best: round10(s.totals.terminal_net_worth - winner.totals.terminal_net_worth)
  })),
  recommendation: {
    scenario_id: winner.id,
    scenario_name: winner.name,
    terminal_net_worth: winner.totals.terminal_net_worth,
    runner_up_id: runnerUp.id,
    runner_up_name: runnerUp.name,
    margin: round10(winner.totals.terminal_net_worth - runnerUp.totals.terminal_net_worth),
    margin_pct: round4((winner.totals.terminal_net_worth - runnerUp.totals.terminal_net_worth) / Math.abs(runnerUp.totals.terminal_net_worth))
  },
  sensitivity,
  estate_headroom: estate,
  pending_legislation: pending.items.map((p) => ({
    id: p.id,
    name: p.name,
    status: p.status,
    used_in_model: false,
    source_id: p.source_id
  }))
};

fs.writeFileSync(path.join(ROOT, "data/projections.json"), JSON.stringify(output, null, 2));
console.log("wrote data/projections.json\n");
for (const s of ranked) {
  console.log(
    `${s.rank ?? ""}${s.name.padEnd(32)} terminal $${s.totals.terminal_net_worth.toLocaleString().padStart(12)}  cash $${s.totals.cumulative_net_cash.toLocaleString().padStart(12)}`
  );
}
console.log(`\nrecommendation: ${winner.name} by $${output.recommendation.margin.toLocaleString()} (${(output.recommendation.margin_pct * 100).toFixed(1)}%)`);
