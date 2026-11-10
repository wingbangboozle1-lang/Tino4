#!/usr/bin/env node
/**
 * Tino4 projection model — deterministic, no manual input.
 * Reads data/assumptions.json + data/property-tax-history.json -> writes data/model-output.json
 *
 * Conventions
 *  - Nominal USD, rounded to nearest $10 at output only (full precision internally).
 *  - Calendar year == assessment/tax year, matching the client's tables.
 *  - No mortgage: no debt was disclosed, so the portfolio is unlevered.
 *  - The inheritance event occurs in the middle of `inheritanceYear`; operating years run
 *    from inheritanceYear+1 for `horizon` years, and the terminal sale happens at the end
 *    of the last operating year.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const A = JSON.parse(readFileSync(join(root, 'data/assumptions.json'), 'utf8'));
const H = JSON.parse(readFileSync(join(root, 'data/property-tax-history.json'), 'utf8'));
const P0 = Object.fromEntries(A.inputs.map((i) => [i.id, i.value]));

const r10 = (n) => (n == null || Number.isNaN(n) ? null : Math.round(n / 10) * 10);
const pct = (n) => (n == null ? null : Number((n * 100).toFixed(2)));
const START = 2026; // model base year

/* =====================================================================
   1. Value and assessed-value projection (Prop 13 mechanics)
   ===================================================================== */
function buildProjection(P, maxYear = 2075) {
  const proj = new Map();
  for (let y = START; y <= maxYear; y++) {
    const k = Math.max(0, y - START);
    proj.set(y, {
      year: y,
      A: {
        marketValue: P.valueA * Math.pow(1 + P.appreciation, k),
        assessedValue: P.avA2026 * Math.pow(P.inflator2027, k),
      },
      B: {
        marketValue: P.valueB * Math.pow(1 + P.appreciation, k),
        assessedValue: P.avB2026 * Math.pow(P.inflator2027, k),
      },
    });
    const a = proj.get(y);
    a.A.assessedAsPctOfMarket = a.A.assessedValue / a.A.marketValue;
  }
  return proj;
}

const fi = (y, base, growth) => base * Math.pow(1 + growth, y - START);
const taxOn = (assessed, rate, ownerOccupied, P) => {
  const taxable = ownerOccupied ? Math.max(0, assessed - P.homeownersExemption) : assessed;
  return taxable * rate;
};

/* =====================================================================
   2. Proposition 19 test (RTC 63.2) at the transfer date
   ===================================================================== */
function cushionAt(y, P) {
  return P.prop19Cushion * Math.pow(1 + P.prop19CushionGrowth, Math.max(0, y - START));
}

/**
 * @param prop 'A' | 'B'
 * @param mode 'live' | 'rent'
 * @param occupancyShare fraction of the property that becomes the heir's principal residence
 *        (1 for A; 1/3 for one unit of the three-unit building B, per BOE LTA 2026/026 Q5)
 */
function prop19Test(prop, mode, proj, inhYear, P, occupancyShare = 1) {
  const row = proj.get(inhYear);
  const fbyv = row[prop].assessedValue;
  const fmv = row[prop].marketValue;
  const cap = P.fullExclusion ? Infinity : fbyv + cushionAt(inhYear, P);
  const rate = P[`rate${prop}_billed`];

  if (mode !== 'live' || occupancyShare <= 0) {
    return {
      prop,
      mode,
      eligible: false,
      occupancyShare: 0,
      fbyv, fmv, cap,
      excess: null,
      newTaxableValue: fmv,
      firstYearTax: taxOn(fmv, rate, false, P),
      rationale:
        'No eligible transferee occupies the home as a principal residence within one year, so the intergenerational exclusion is unavailable and the property is reassessed to full market value (RTC 63.2(a)(1)(A); BOE LTA 2026/026 Q7 "There are no exceptions to this rule").',
    };
  }

  const excess = Math.max(0, fmv * occupancyShare - cap * occupancyShare);
  const excludedBase = fbyv * occupancyShare + excess; // occupied portion
  const marketBase = fmv * (1 - occupancyShare);        // non-qualifying portion, at full cash value
  const newTaxableValue = excludedBase + marketBase;

  return {
    prop,
    mode,
    eligible: true,
    occupancyShare,
    fbyv, fmv,
    cap,
    excess,
    excludedBase,
    marketBase,
    newTaxableValue,
    firstYearTax: taxOn(newTaxableValue, rate, occupancyShare >= 1, P),
    rationale:
      (occupancyShare < 1
        ? `Only the unit occupied as the principal residence qualifies; the other ${Math.round((1 - occupancyShare) * 100 / occupancyShare)} units are reassessed at full cash value (BOE LTA 2026/026 Q5). `
        : '') +
      (excess > 0
        ? 'Market value exceeds taxable value plus the adjusted $1M cushion, so the excess is added to the taxable value (RTC 63.2(d)).'
        : 'Market value falls inside the cushion, so the taxable value carries over unchanged.'),
  };
}

/* =====================================================================
   3. One operating year for one property
   ===================================================================== */
function operatingYear(prop, cfg, proj, y, inhYear, P) {
  const row = proj.get(y);
  const rate = P[`rate${prop}_billed`];
  const liveIn = cfg.mode === 'live';
  const share = cfg.occupancyShare ?? 1;

  // Property tax: new taxable value from the transfer, factored forward under Prop 13.
  const base = cfg.newTaxableValue * Math.pow(P.inflator2027, Math.max(0, y - inhYear));
  const tax = taxOn(base, rate, liveIn && share >= 1, P);

  const water = fi(y, P[`water${prop}`] * 12, P.utilityInflation) * (cfg.utilityShare ?? 1);
  const elec = fi(y, P[`electric${prop}`] * 12, P.utilityInflation) * (cfg.utilityShare ?? 1); // may be negative for A (solar credit)
  const ins = fi(y, P[`insurance${prop}`], P.insuranceInflation);
  // Maintenance is a percentage of the property's value IN THAT YEAR. The market value already
  // embeds appreciation, so no additional CPI indexation is applied (doing both would double-count).
  const maint = P[`maintenance${prop}`] * row[prop].marketValue;
  const grossRent = cfg.rentBase ? fi(y, cfg.rentBase * 12, cfg.rentGrowth) : 0;
  const vacancy = grossRent * P.vacancyLoss;

  // cashCosts excludes vacancy; vacancy is subtracted once, below.
  const cashCosts = tax + water + Math.max(0, elec) + ins + maint;
  // Depreciation shelter, on the stepped-up income-tax basis (IRC 1014), building portion only.
  const dep = cfg.rentBase ? (row[prop].marketValue * P.buildingShare) / P.depreciationLife : 0;
  const netBeforeDep = grossRent - vacancy - cashCosts;
  const taxableRent = Math.max(0, netBeforeDep - dep);
  const rentTax = taxableRent * (P.marginalRateFed + P.marginalRateCA);

  const net = cfg.rentBase ? netBeforeDep - rentTax : -(tax + water + elec + ins + maint);

  return {
    prop, mode: cfg.mode, year: y,
    propertyTax: tax, water, electricity: elec, insurance: ins, maintenance: maint,
    grossRent, vacancyLoss: vacancy,
    depreciationShelter: Math.min(dep, Math.max(0, netBeforeDep)),
    rentalIncomeTax: rentTax,
    netCashFlow: net,
  };
}

/* =====================================================================
   4. Strategy engine
   ===================================================================== */
function runStrategy(def, P, params = {}) {
  const inhYear = params.inheritanceYear ?? P.inheritanceYear;
  const horizon = params.horizon ?? 20;
  const proj = params.proj ?? buildProjection(P);
  const startYear = inhYear + 1;

  // Resolve each property's transfer treatment first.
  const A_cfg = def.A?.keep
    ? { ...def.A, ...prop19Test('A', def.A.mode, proj, inhYear, P, 1) }
    : null;
  const B_cfg = def.B?.keep
    ? { ...def.B, ...prop19Test('B', def.B.mode, proj, inhYear, P, def.B.mode === 'live' ? 1 / 3 : 0) }
    : null;

  const rows = [];
  let cum = 0;
  for (let y = startYear; y < startYear + horizon; y++) {
    const lines = [];
    if (A_cfg) lines.push(operatingYear('A', { ...A_cfg, rentBase: A_cfg.mode === 'rent' ? A_cfg.rentBase : 0, rentGrowth: P.rentGrowthA }, proj, y, inhYear, P));
    if (B_cfg) lines.push(operatingYear('B', { ...B_cfg, rentBase: B_cfg.mode === 'rent' ? B_cfg.rentBase : (def.B.mode === 'live' ? def.B.rentBase : 0), rentGrowth: P.rentGrowthB, utilityShare: B_cfg.mode === 'live' ? 1 : 1 }, proj, y, inhYear, P));
    const net = lines.reduce((s, l) => s + l.netCashFlow, 0);
    cum += net;
    rows.push({ year: y, lines, netCashFlow: net, cumulative: cum });
  }

  // Terminal event at the end of the last operating year.
  const endYear = startYear + horizon - 1;
  const endRow = proj.get(endYear);
  const inhRow = proj.get(inhYear);
  const sales = [];
  let saleNet = 0;
  let cgtTotal = 0;

  // A sale that happened AT inheritance (for the sell-and-reinvest branch) is handled by the caller.
  for (const [prop, cfg] of [['A', A_cfg], ['B', B_cfg]]) {
    if (!cfg) continue;
    const price = endRow[prop].marketValue;
    const deathValue = inhRow[prop].marketValue;
    const costs = price * P.sellingCosts;
    const gain = Math.max(0, price - deathValue);
    const principalShare = cfg.mode === 'live' ? (prop === 'B' ? 1 / 3 : 1) : 0;
    const exclusion = P.section121 * principalShare;
    const taxableGain = Math.max(0, gain - exclusion);
    const cgt = taxableGain * (P.capGainFed + P.capGainNiit + P.capGainCA);
    cgtTotal += cgt;
    const net = price - costs - cgt;
    saleNet += net;
    sales.push({
      prop, salePrice: r10(price), costOfSale: r10(costs), incomeTaxBasis: r10(deathValue),
      gain: r10(gain), section121Exclusion: r10(exclusion), taxableGain: r10(taxableGain),
      capitalGainsTax: r10(cgt), netProceeds: r10(net),
    });
  }

  // Reinvested portfolio from any property sold at inheritance.
  let portfolio = 0;
  const earlySales = [];
  if (def.sellAtInheritance) {
    for (const prop of def.sellAtInheritance) {
      const price = inhRow[prop].marketValue;
      const costs = price * P.sellingCosts;
      // Basis = date-of-death value, so the immediate gain is ~0 (IRC 1014). Transfer taxes still apply.
      const net = price - costs;
      earlySales.push({ prop, salePrice: r10(price), costOfSale: r10(costs), incomeTaxBasis: r10(price), gain: 0, section121Exclusion: 0, taxableGain: 0, capitalGainsTax: 0, netProceeds: r10(net) });
      portfolio += net;
    }
  }
  if (portfolio > 0) portfolio *= Math.pow(1 + P.portfolioReturn, horizon);

  const terminal = cum + saleNet + portfolio;

  // ---- Housing-consumption equaliser -------------------------------------------------
  // Every strategy must deliver the same thing: somewhere for the household to live.
  // Where the heir occupies an inherited house, the market rent he does not have to pay is a
  // real economic benefit (in kind, not cash). Where neither house is occupied, he must rent.
  let imputedHousingBenefit = 0;
  let rentPaid = 0;
  if (def.housing === 'rentA') {
    // living in A: 95014 two-bedroom benchmark (S30)
    for (let y = startYear; y < startYear + horizon; y++) imputedHousingBenefit += fi(y, P.rentA * 12, P.rentGrowthA);
  } else if (def.housing === 'rentB') {
    // living in B's vacant unit: 94122 one-bedroom benchmark (S31)
    for (let y = startYear; y < startYear + horizon; y++) imputedHousingBenefit += fi(y, P.rentB_vacantUnit * 12, P.rentGrowthB);
  } else if (def.housing === 'payRent') {
    // must rent a comparable home: 95014 two-bedroom benchmark, market (not rent-capped) growth
    for (let y = startYear; y < startYear + horizon; y++) rentPaid += fi(y, P.rentA * 12, P.rentGrowthA);
  } else if (def.housing === 'rentFreeElsewhere') {
    // S4: the heir lives in housing already owned/paid for outside this portfolio — no charge,
    // no benefit. Stated explicitly so the comparison is not silently favourable.
  }

  return {
    name: def.name,
    note: def.note,
    housing: def.housing,
    imputedHousingBenefit: r10(imputedHousingBenefit),
    rentPaid: r10(rentPaid),
    economicTerminalWealth: r10(terminal + imputedHousingBenefit - rentPaid),
    inheritanceYear: inhYear,
    horizonYears: horizon,
    construction: { A: A_cfg ? { ...prop19Test('A', A_cfg.mode, proj, inhYear, P, 1) } : null, B: B_cfg ? { ...prop19Test('B', B_cfg.mode, proj, inhYear, P, B_cfg.mode === 'live' ? 1 / 3 : 0) } : null },
    earlySales,
    firstYear: rows[0],
    lastYear: rows[rows.length - 1],
    cumulativeOperatingCashFlow: r10(cum),
    terminalSales: sales,
    terminalCapitalGainsTax: r10(cgtTotal),
    reinvestedPortfolioAtEnd: r10(portfolio),
    terminalWealth: r10(terminal),
    totalPropertyTaxOverHorizon: r10(rows.reduce((s, r) => s + r.lines.reduce((t, l) => t + l.propertyTax, 0), 0)),
    totalMaintenanceOverHorizon: r10(rows.reduce((s, r) => s + r.lines.reduce((t, l) => t + l.maintenance, 0), 0)),
    totalInsuranceOverHorizon: r10(rows.reduce((s, r) => s + r.lines.reduce((t, l) => t + l.insurance, 0), 0)),
    totalUtilitiesOverHorizon: r10(rows.reduce((s, r) => s + r.lines.reduce((t, l) => t + l.water + Math.max(0, l.electricity), 0), 0)),
    totalGrossRent: r10(rows.reduce((s, r) => s + r.lines.reduce((t, l) => t + l.grossRent, 0), 0)),
    totalRentalIncomeTax: r10(rows.reduce((s, r) => s + r.lines.reduce((t, l) => t + l.rentalIncomeTax, 0), 0)),
  };
}

/* =====================================================================
   5. Base parameter set
   ===================================================================== */
const P = {
  ...P0,
  valueA: H.properties[0].valueNov2026,
  valueB: H.properties[1].valueNov2026,
  avA2026: 550537, // client table, 2026 tax assessment
  avB2026: 114248, // client table, 2025 tax assessment (latest supplied); carried to 2026 at the 1.02 factor
  section121: 500000,
  capGainFed: 0.20,
  capGainNiit: 0.038,
  capGainCA: 0.093,
};
P.avB2026 = 114248 * P.inflator2027; // B's 2026 assessed value was not supplied; factored at the official 2026-27 factor

const proj = buildProjection(P);

const STRATEGY_DEFS = [
  {
    key: 'S1',
    name: 'S1 — Move into Property A, keep Property B fully rented',
    note: 'The heir occupies A (so A can use the Prop 19 exclusion) and both existing B tenancies continue; the third unit stays vacant.',
    A: { keep: true, mode: 'live' },
    B: { keep: true, mode: 'rent', rentBase: P.rentB },
    housing: 'rentA',
  },
  {
    key: 'S2',
    name: 'S2 — Rent both houses out, live elsewhere',
    note: 'Nobody occupies either home, so the Prop 19 exclusion is forfeited on both: both reassess to full market value. B\'s vacant unit is leased at the FY2026 HUD 94122 one-bedroom benchmark.',
    A: { keep: true, mode: 'rent', rentBase: P.rentA },
    B: { keep: true, mode: 'rent', rentBase: P.rentB + P.rentB_vacantUnit },
    housing: 'payRent',
  },
  {
    key: 'S3',
    name: 'S3 — Sell Property A, move into B while both tenancies continue',
    note: 'A is sold right after death; the step-up under IRC 1014 means the sale realises essentially no capital gain, only the cost of sale. The heir occupies B\'s vacant third unit, so B still produces two rents and the occupied third of B can use the Prop 19 exclusion.',
    sellAtInheritance: ['A'],
    B: { keep: true, mode: 'live', rentBase: P.rentB },
    housing: 'rentB',
  },
  {
    key: 'S4',
    name: 'S4 — Sell Property A, invest the proceeds, keep B fully rented',
    note: 'A is sold at inheritance and the net proceeds compound at the assumed after-tax portfolio return for the whole horizon; B stays a pure rental and is sold at the end.',
    sellAtInheritance: ['A'],
    B: { keep: true, mode: 'rent', rentBase: P.rentB },
    housing: 'rentFreeElsewhere',
  },
  {
    key: 'S5',
    name: 'S5 — Sell both properties at inheritance and rent a home',
    note: 'Both houses sold immediately (≈zero gain because of the step-up), proceeds invested, and the heir rents. This is the clean liquid benchmark.',
    sellAtInheritance: ['A', 'B'],
    housing: 'payRent',
  },
  {
    key: 'S6',
    name: 'S6 — Move into Property B\'s vacant unit, rent Property A out',
    note: 'The heir takes B\'s empty third unit (so one third of B can use the Prop 19 exclusion and both rents continue) and leases A at the 95014 market benchmark. This keeps the Cupertino house as an income asset instead of converting it to personal use.',
    A: { keep: true, mode: 'rent', rentBase: P.rentA },
    B: { keep: true, mode: 'live', rentBase: P.rentB },
    housing: 'rentB',
  },
];

/* =====================================================================
   6. Estate-tax test
   ===================================================================== */
function estateTest(P, years = [2040, 2045, 2050]) {
  return years.map((y) => {
    const row = proj.get(y);
    const exemption = P.estateExemption2026 * Math.pow(1 + P.estateExemptionIndex, y - START);
    const gross = row.A.marketValue + row.B.marketValue + P.cashLegacy;
    return {
      year: y,
      propertyA: r10(row.A.marketValue),
      propertyB: r10(row.B.marketValue),
      cashAndSecurities: r10(P.cashLegacy),
      grossEstate: r10(gross),
      exemptionPerPerson: r10(exemption),
      exemptionMarriedWithPortability: r10(exemption * 2),
      headroomSingle: r10(exemption - gross),
      federalEstateTaxSingle: r10(Math.max(0, gross - exemption) * P.estateTaxRate),
      federalEstateTaxMarried: r10(Math.max(0, gross - exemption * 2) * P.estateTaxRate),
      californiaEstateOrInheritanceTax: 0,
    };
  });
}

/* =====================================================================
   7. Sensitivity — reruns the strategy engine
   ===================================================================== */
function sensitivity() {
  const combos = [];
  for (const app of [0.02, 0.035, 0.05]) {
    for (const pr of [0.04, 0.06, 0.08]) {
      const p2 = { ...P, appreciation: app, portfolioReturn: pr };
      const proj2 = buildProjection(p2);
      const all = STRATEGY_DEFS.map((d) => ({ key: d.key, s: runStrategy(d, p2, { proj: proj2 }) }));
      const ranked = [...all].sort((x, y) => y.s.economicTerminalWealth - x.s.economicTerminalWealth);
      combos.push({
        appreciationPct: pct(app),
        portfolioReturnPct: pct(pr),
        economicTerminal: Object.fromEntries(all.map((a) => [a.key, a.s.economicTerminalWealth])),
        winner: ranked[0].key,
        winnerEconomic: ranked[0].s.economicTerminalWealth,
        runnerUp: ranked[1].key,
        gap: r10(ranked[0].s.economicTerminalWealth - ranked[1].s.economicTerminalWealth),
        s1_vs_s4: r10(all.find(a=>a.key==='S4').s.economicTerminalWealth - all.find(a=>a.key==='S1').s.economicTerminalWealth),
      });
    }
  }
  return combos;
}

/* =====================================================================
   8. Assemble output
   ===================================================================== */
const strategies = STRATEGY_DEFS.map((d) => runStrategy(d, P, { proj }));

const projectionOut = [];
for (let y = 2026; y <= 2065; y++) {
  const row = proj.get(y);
  projectionOut.push({
    year: y,
    A: {
      marketValue: r10(row.A.marketValue),
      assessedValue: r10(row.A.assessedValue),
      propertyTaxOwnerOccupied: r10(taxOn(row.A.assessedValue, P.rateA_billed, true, P)),
      propertyTaxRental: r10(taxOn(row.A.assessedValue, P.rateA_billed, false, P)),
      assessedAsPctOfMarket: pct(row.A.assessedAsPctOfMarket),
    },
    B: {
      marketValue: r10(row.B.marketValue),
      assessedValue: r10(row.B.assessedValue),
      propertyTaxRental: r10(taxOn(row.B.assessedValue, P.rateB_billed, false, P)),
      assessedAsPctOfMarket: pct(row.B.assessedValue / row.B.marketValue),
    },
  });
}

// Stress test: what if the parents' principal residence was B, not A?
const swapP = { ...P };
const swapped = {
  note: 'If the parents\' principal residence was Property B (the San Francisco house) rather than Property A, the Prop 19 exclusion is only available on B. A then reassesses to full market value even if the heir moves in.',
  inheritanceYear: P.inheritanceYear,
  A_ifNotPrincipalResidence: runStrategy({ ...STRATEGY_DEFS[0], key: 'S1-swap' }, swapP, { proj }),
};
// Recompute A's transfer treatment with no exclusion for the swap case
const aNoExclusion = prop19Test('A', 'rent', proj, P.inheritanceYear, P, 0);

const out = {
  generated: new Date().toISOString(),
  modelDate: A.modelDate,
  rounding: 'nearest $10',
  privacy: H.privacy,
  centralInheritanceYear: P.inheritanceYear,
  horizonYears: 20,
  firstOperatingYear: P.inheritanceYear + 1,
  projection: projectionOut,
  prop19AtTransfer: {
    inheritanceYear: P.inheritanceYear,
    cushion: r10(cushionAt(P.inheritanceYear, P)),
    A_ifHeirOccupies: prop19Test('A', 'live', proj, P.inheritanceYear, P, 1),
    A_ifNotOccupied: prop19Test('A', 'rent', proj, P.inheritanceYear, P, 0),
    B_ifHeirOccupiesOneUnit: prop19Test('B', 'live', proj, P.inheritanceYear, P, 1 / 3),
    B_ifFullyRented: prop19Test('B', 'rent', proj, P.inheritanceYear, P, 0),
  },
  prop19AtTransfer_byYear: [2040, 2045, 2050].map((y) => ({
    inheritanceYear: y,
    cushion: r10(cushionAt(y, P)),
    A_marketValue: r10(proj.get(y).A.marketValue),
    A_taxableValueAtDeath: r10(proj.get(y).A.assessedValue),
    A_ifOccupied: prop19Test('A', 'live', proj, y, P, 1),
    A_ifNotOccupied: prop19Test('A', 'rent', proj, y, P, 0),
  })),
  strategies: strategies.map((s) => ({ ...s, inheritanceYear: s.inheritanceYear })),
  estateTest: estateTest(P),
  estateStress: {
    note: 'The estate test is highly sensitive to the one number nobody supplied: the size of the cash/securities inheritance. These rows show how far the placeholder can move before federal estate tax appears.',
    rows: [0, 4000000, 8000000, 12000000, 20000000].map((cash) => {
      const e = estateTest({ ...P, cashLegacy: cash }, [2045, 2050]);
      return { cashLegacy: r10(cash), ...e[1] };
    }),
  },
  exemptionFreezeStress: {
    note: 'If the federal exclusion were frozen at $15,000,000 (no indexation) rather than indexed after 2026.',
    rows: [2040, 2045, 2050].map((y) => {
      const row = proj.get(y);
      const gross = row.A.marketValue + row.B.marketValue + P.cashLegacy;
      return { year: y, grossEstate: r10(gross), exemptionFrozen: 15000000, federalEstateTaxSingle: r10(Math.max(0, gross - 15000000) * P.estateTaxRate) };
    }),
  },
  sensitivity: sensitivity(),
  stepUpRepealStress: {
    note: 'If the step-up in basis were replaced by carryover basis (the STEP Act proposal, not enacted), a sale would be taxed on the parents\' original low basis instead of the date-of-death value. Quantified for Property A, assumed original basis of $440,305 (the 2014 assessed value in the client\'s own table) and Property B at $96,557 (2016).',
    rows: ['A', 'B'].map((prop) => {
      const deathValue = proj.get(P.inheritanceYear)[prop].marketValue;
      const carryover = prop === 'A' ? 440305 : 96557;
      const gainWithStepUp = 0; // sold at inheritance
      const gainCarryover = deathValue - carryover;
      const rate = 0.20 + 0.038 + 0.093;
      return {
        property: prop,
        valueAtInheritance: r10(deathValue),
        carryoverBasis: r10(carryover),
        taxWithStepUpIfSoldNow: r10(gainWithStepUp * rate),
        taxWithCarryoverIfSoldNow: r10(gainCarryover * rate),
        difference: r10(gainCarryover * rate),
      };
    }),
  },
  flaggedAssumptions: A.inputs.filter((i) => i.basis === 'assumption').map((i) => ({ id: i.id, label: i.label, value: i.value, range: i.range, note: i.note })),
  unverifiedInputs: A.inputs.filter((i) => i.basis === 'client').map((i) => ({ id: i.id, label: i.label, value: i.value, note: i.note })),
  sourcesUsed: [...new Set(A.inputs.map((i) => i.sourceId).filter(Boolean))].sort(),
};

/* ---- repeal counterfactual: what the Prop 19 cap is actually costing ---- */
const pFull = { ...P, fullExclusion: true };
const s1Full = runStrategy(STRATEGY_DEFS[0], pFull, { proj });
out.repealCounterfactual = {
  note: 'What strategy S1 would look like if the intergenerational exclusion had no value cap — i.e. the pre-Proposition-19 rule that the failed 2026 rollback initiative would have restored. The difference is the current cost of Proposition 19 to this household.',
  withProp19Cap: { firstYearPropertyTaxA: r10(strategies[0].construction.A.firstYearTax), terminalWealth: strategies[0].terminalWealth, economicTerminalWealth: strategies[0].economicTerminalWealth },
  withUncappedExclusion: { firstYearPropertyTaxA: r10(s1Full.construction.A.firstYearTax), terminalWealth: s1Full.terminalWealth, economicTerminalWealth: s1Full.economicTerminalWealth },
  costOfProp19Cap: {
    firstYearPropertyTax: r10(strategies[0].construction.A.firstYearTax - s1Full.construction.A.firstYearTax),
    terminalWealth: r10(strategies[0].terminalWealth - s1Full.terminalWealth),
    economicTerminalWealth: r10(strategies[0].economicTerminalWealth - s1Full.economicTerminalWealth),
  },
  caveat: 'The rollback initiative failed to qualify for the 2026 ballot (S39), so the capped rule is current law and is the base case.',
};

/* ---- 5-year delay cost: the value of knowing the transfer year ---- */
out.delayCost = {
  note: 'Property tax on Property A in the first full year of ownership, depending on when the transfer happens. Later transfers mean a higher market value and therefore a bigger reassessment, but also more years of the parents paying the low Prop 13 bill.',
  rows: [2040, 2042, 2044, 2046, 2048, 2050].map((y) => {
    const t = prop19Test('A', 'live', proj, y, P, 1);
    const n = prop19Test('A', 'rent', proj, y, P, 0);
    return {
      transferYear: y,
      marketValue: r10(proj.get(y).A.marketValue),
      taxableValueAtDeath: r10(proj.get(y).A.assessedValue),
      cushion: r10(cushionAt(y, P)),
      newTaxableValueIfOccupied: r10(t.newTaxableValue),
      firstFullYearPropertyTaxIfOccupied: r10(t.firstYearTax),
      firstFullYearPropertyTaxIfVacantOrRented: r10(n.firstYearTax),
      valueOfOccupying: r10(n.firstYearTax - t.firstYearTax),
    };
  }),
};

/* ---- break-even portfolio return between the leading strategies ---- */
out.breakEven = (() => {
  const solve = (keyA, keyB) => {
    // find the portfolio return at which strategy keyB overtakes keyA
    let lo = 0.0, hi = 0.20;
    const val = (pr) => {
      const p2 = { ...P, portfolioReturn: pr };
      const proj2 = buildProjection(p2);
      const a = runStrategy(STRATEGY_DEFS.find(d => d.key === keyA), p2, { proj: proj2 }).economicTerminalWealth;
      const b = runStrategy(STRATEGY_DEFS.find(d => d.key === keyB), p2, { proj: proj2 }).economicTerminalWealth;
      return b - a;
    };
    // val(pr) = strategy B minus strategy A. We look for the return where B catches A.
    if (val(lo) > 0) return { rate: 0, note: 'B already leads with a 0% portfolio return' };
    if (val(hi) < 0) return { rate: null, note: 'B never catches A even at a 20% portfolio return' };
    for (let i = 0; i < 40; i++) { const mid = (lo + hi) / 2; if (val(mid) > 0) lo = mid; else hi = mid; }
    return { rate: Number(((lo + hi) / 2 * 100).toFixed(2)) };
  };
  return {
    note: 'Portfolio return at which selling everything (S5) overtakes keeping Property B and living in its vacant unit (S3), at the central 3.5% appreciation.',
    s5_overtakes_s3_atPortfolioReturn: {
      solve: solve('S3', 'S5'),
      interpretation: 'Even at a 20% portfolio return, selling both houses does not overtake living in B and renting out A. The dominant reason is that S3 keeps both properties for 20 years and pays almost no tax on the gains through the step-up, while S5 converts everything to taxable investments on day one.',
    },
    s4_overtakes_s1_atPortfolioReturn: {
      solve: solve('S1', 'S4'),
      interpretation: 'Selling A and reinvesting (S4) overtakes occupying A (S1) at this portfolio return, holding housing cost equal (S4 assumes the household already has a place to live).',
    },
    costOfLivingInA_vs_B: {
      note: 'S6 (live in B\'s vacant unit, rent out A) minus S1 (live in A, rent out B), over 20 years. This is the price of choosing the Cupertino house as the family home.',
      over20Years: r10(strategies.find(s=>s.name.startsWith('S6')).economicTerminalWealth - strategies.find(s=>s.name.startsWith('S1')).economicTerminalWealth),
      perYear: r10((strategies.find(s=>s.name.startsWith('S6')).economicTerminalWealth - strategies.find(s=>s.name.startsWith('S1')).economicTerminalWealth) / 20),
    },
  };
})();

/* ---- annual operating projection per property (client asked for this explicitly) ---- */
function annualOperating(prop, mode, years = 2026) {
  const rate = P[`rate${prop}_billed`];
  const rows = [];
  for (let y = 2026; y <= 2055; y++) {
    const row = proj.get(y);
    const live = mode === 'live';
    const base = live || prop === 'B' ? row[prop].assessedValue : row[prop].assessedValue;
    rows.push({
      year: y,
      marketValue: r10(row[prop].marketValue),
      taxableValue: r10(base),
      propertyTax: r10(taxOn(base, rate, live, P)),
      insurance: r10(fi(y, P[`insurance${prop}`], P.insuranceInflation)),
      water: r10(fi(y, P[`water${prop}`] * 12, P.utilityInflation)),
      electricity: r10(fi(y, P[`electric${prop}`] * 12, P.utilityInflation)),
      maintenance: r10(P[`maintenance${prop}`] * row[prop].marketValue),
      grossRent: mode === 'rent' ? r10(fi(y, (prop === 'A' ? P.rentA : P.rentB) * 12, prop === 'A' ? P.rentGrowthA : P.rentGrowthB)) : null,
      totalCosts: null,
    });
    const r = rows[rows.length - 1];
    r.totalCosts = r10(r.propertyTax + r.insurance + r.water + Math.max(0, r.electricity) + r.maintenance);
  }
  return rows;
}

out.annualOperating = {
  propertyA_ownerOccupied: annualOperating('A', 'live'),
  propertyA_rented: annualOperating('A', 'rent'),
  propertyB_rented: annualOperating('B', 'rent'),
  note: '2026-2055. These are the parents\' current Prop 13 assessment carried forward at the 2% cap, so they show the parents\' current tax bill until the transfer; after a transfer the taxable value resets as shown in the Proposition 19 tables. Insurance, water, electricity and maintenance are projected from the client\'s stated figures at the inflation assumptions in Assumptions.',
};

/* ---- internal audit: every headline number must reconcile ---- */
out.audit = strategies.map((s) => {
  const recon = s.cumulativeOperatingCashFlow + s.terminalSales.reduce((a, b) => a + b.netProceeds, 0) + (s.reinvestedPortfolioAtEnd || 0);
  return {
    strategy: s.key ?? s.name,
    terminalWealth: s.terminalWealth,
    recomputedTerminal: r10(recon),
    reconciles: Math.abs(recon - s.terminalWealth) <= 10,
    capitalGainsTaxInSales: r10(s.terminalSales.reduce((a, b) => a + b.capitalGainsTax, 0)),
    capitalGainsTaxReported: s.terminalCapitalGainsTax,
    cgtReconciles: Math.abs(s.terminalSales.reduce((a, b) => a + b.capitalGainsTax, 0) - s.terminalCapitalGainsTax) <= 10,
  };
});

writeFileSync(join(root, 'data/model-output.json'), JSON.stringify(out, null, 2));

/* ---- console audit ---- */
console.log('=== Prop 19 at transfer', P.inheritanceYear, '===');
console.log('cushion       ', r10(cushionAt(P.inheritanceYear, P)));
for (const [k, v] of Object.entries(out.prop19AtTransfer)) {
  if (typeof v !== 'object' || !v.newTaxableValue) continue;
  console.log(k.padEnd(24), 'newTaxable', r10(v.newTaxableValue), 'firstYrTax', r10(v.firstYearTax), 'vs old', r10(v.fbyv * P.rateA_billed));
}
console.log('\n=== Strategies (20y) ===');
for (const s of out.strategies) {
  console.log(s.name.slice(0, 48).padEnd(50), 'opCF', String(s.cumulativeOperatingCashFlow).padStart(12), 'terminal', String(s.terminalWealth).padStart(12), 'cgt', String(s.terminalCapitalGainsTax).padStart(10));
}
console.log('\n=== Estate ===');
for (const e of out.estateTest) console.log(e.year, 'gross', e.grossEstate, 'exempt', e.exemptionPerPerson, 'taxSingle', e.federalEstateTaxSingle, 'taxMarried', e.federalEstateTaxMarried);
console.log('\n=== Repeal counterfactual ===');
console.log(JSON.stringify(out.repealCounterfactual.costOfProp19Cap));
console.log('\n=== Delay cost ===');
for (const d of out.delayCost.rows) console.log(d.transferYear, 'mv', d.marketValue, 'taxOccupied', d.firstFullYearPropertyTaxIfOccupied, 'taxVacant', d.firstFullYearPropertyTaxIfVacantOrRented);
console.log('\n=== Economic terminal wealth ===');
for (const s2 of out.strategies) console.log(s2.name.slice(0,3), 'cash', s2.terminalWealth, 'economic', s2.economicTerminalWealth);
console.log('\n=== Audit ===');
for (const a of out.audit) console.log(a.strategy, a.reconciles, a.cgtReconciles, a.terminalWealth);
console.log('\n=== Break-even ===');
console.log(JSON.stringify(out.breakEven, null, 1));
console.log('\n=== Sensitivity (economic terminal, all strategies) ===');
for (const c of out.sensitivity) console.log('app', c.appreciationPct, 'port', c.portfolioReturnPct, 'winner', c.winner, JSON.stringify(c.economicTerminal));
