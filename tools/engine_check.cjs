#!/usr/bin/env node
/* Offline parity check between the browser engine and the Python engine.

   Run: node tools/engine_check.cjs <fixture.json>

   The fixture is produced by tools/test_case.py from tools/casedata.py. Any
   difference between the two implementations fails the build, because the page
   ships Python-computed default tables that the browser then recomputes.
*/
'use strict';

const fs = require('fs');
const path = require('path');

const fixturePath = process.argv[2];
if (!fixturePath) {
  console.error('usage: node tools/engine_check.cjs <fixture.json>');
  process.exit(2);
}

const fixture = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
const engine = require(path.join(__dirname, '..', 'assets', 'app.js'));

const inputs = {
  transferYear: fixture.inputs.transferYear,
  aApp: fixture.inputs.aApp,
  bApp: fixture.inputs.bApp,
  inflation: fixture.inputs.inflation,
  assessedGrowth: fixture.inputs.assessedGrowth,
  prop19Growth: fixture.inputs.prop19Growth,
  insuranceGrowth: fixture.inputs.insuranceGrowth,
  rentGrowth: fixture.inputs.rentGrowth,
  maintenanceA: fixture.inputs.maintenanceA,
  maintenanceB: fixture.inputs.maintenanceB,
  sellingCost: fixture.inputs.sellingCost,
  equityReturn: fixture.inputs.equityReturn,
  treasuryYield: fixture.inputs.treasuryYield,
  stagingMonths: fixture.inputs.stagingMonths,
  horizonYears: fixture.inputs.horizonYears
};

const model = engine.makeModel(fixture.data, inputs);
const failures = [];

function check(label, actual, expected) {
  if (Math.abs(actual - expected) > 0.5) {
    failures.push(`${label}: browser ${actual} vs python ${expected}`);
  }
}

fixture.expectations.forEach((row) => {
  const year = row.year;
  check(`marketA ${year}`, model.marketA(year), row.marketA);
  check(`marketB ${year}`, model.marketB(year), row.marketB);
  check(`assessedA ${year}`, model.assessedA(year), row.assessedA);
  check(`assessedB ${year}`, model.assessedB(year), row.assessedB);
  check(`limit ${year}`, model.limit(year), row.limit);
  check(`taxableOccupied ${year}`,
    model.taxable(row.marketA, row.assessedA, row.limit), row.taxableOccupied);
  check(`taxOccupied ${year}`,
    model.tax(model.taxable(row.marketA, row.assessedA, row.limit), fixture.data.effectiveRateA, true),
    row.taxOccupied);
  check(`taxRented ${year}`,
    model.tax(engine.round10(row.marketA), fixture.data.effectiveRateA, false), row.taxRented);
  check(`taxB ${year}`,
    model.tax(row.assessedB, fixture.data.effectiveRateB, false), row.taxB);
  check(`rentB ${year}`, model.rentB(year), row.rentB);
  check(`opATotal ${year}`, model.opA(year).total, row.opATotal);
  check(`opBTotal ${year}`, model.opB(year).total, row.opBTotal);
});

const params = {
  start: 100,
  staging: fixture.inputs.stagingMonths,
  phase: 12,
  yield: fixture.inputs.treasuryYield,
  yieldAfter: 0.02,
  equity: fixture.inputs.equityReturn,
  fallDepth: 0.57,
  fallStart: 6,
  fallMonths: 18,
  recover: 0.08,
  horizon: fixture.inputs.horizonYears
};
const sims = {
  immediate: engine.simulate('immediate', params),
  staged: engine.simulate('staged', params),
  cash: engine.simulate('cash', params)
};
check('sim immediate', Number(sims.immediate.end.toFixed(4)), fixture.sim.immediate);
check('sim immediate worst', Number(sims.immediate.worst.toFixed(4)), fixture.sim.immediateWorst);
check('sim staged', Number(sims.staged.end.toFixed(4)), fixture.sim.staged);
check('sim staged worst', Number(sims.staged.worst.toFixed(4)), fixture.sim.stagedWorst);
check('sim cash', Number(sims.cash.end.toFixed(4)), fixture.sim.cash);

if (failures.length) {
  console.error('engine parity FAILED');
  failures.forEach((line) => console.error('  ' + line));
  process.exit(1);
}
process.stdout.write(`engine parity OK (${fixture.expectations.length} years, 3 simulations)\n`);
