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
const engine = require(path.join(__dirname, '..', 'assets', 'projection-engine.js'));

const model = engine.projectionModel(fixture.data, fixture.inputs);
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
  const taxable = model.taxable(row.marketA, row.assessedA, row.limit);
  check(`taxableOccupied ${year}`, taxable, row.taxableOccupied);
  check(`taxOccupied ${year}`, model.tax(taxable, fixture.data.effectiveRateA, true), row.taxOccupied);
  check(`taxRented ${year}`, model.tax(row.marketA, fixture.data.effectiveRateA, false), row.taxRented);
  check(`taxB ${year}`, model.tax(row.assessedB, fixture.data.effectiveRateB, false), row.taxB);
  check(`rentB ${year}`, model.rentB(year), row.rentB);
  check(`opATotal ${year}`, model.opA(year), row.opATotal);
  check(`opBTotal ${year}`, model.opB(year), row.opBTotal);
});

/* Rounding is part of the contract: every published figure is a multiple of ten. */
[
  ['round10 half-up', engine.round10(5965), 5970],
  ['round10 down', engine.round10(7003), 7000],
  ['round10 large', engine.round10(550537), 550540],
].forEach(([label, actual, expected]) => check(label, actual, expected));

if (failures.length) {
  console.error('engine parity FAILED');
  failures.forEach((line) => console.error('  ' + line));
  process.exit(1);
}
process.stdout.write(`engine parity OK (${fixture.expectations.length} years, rounding contract)\n`);
