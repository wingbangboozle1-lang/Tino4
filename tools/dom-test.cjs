#!/usr/bin/env node
/* Offline DOM and script check.

   Loads every generated page, runs the local stylesheet-free script, and
   asserts structure, sourcing, and interactive behaviour. It runs without a
   browser engine so it can run anywhere Node is available; the fuller Playwright
   smoke test in tools/browser-test.cjs additionally checks layout where the
   optional browser dependencies are installed.
*/
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const candidates = [
  process.env.BROWSER_MODULES,
  path.join(__dirname, 'browser', 'node_modules'),
  path.join(process.cwd(), 'node_modules'),
].filter(Boolean);
const found = candidates.find(candidate => fs.existsSync(path.join(candidate, 'jsdom')));
if (!found) {
  console.log('jsdom not installed; skipping the DOM check.');
  process.exit(0);
}
const { JSDOM } = require(path.join(found, 'jsdom'));

const root = path.join(__dirname, '..');
const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, 'site-manifest.json'), 'utf8'));
const problems = [];

const appScript = fs.readFileSync(path.join(root, 'assets', 'app.js'), 'utf8');

/* External resource loading is disabled, so the deferred local script is
   evaluated directly after parsing. This still exercises the real script. */
function load(relative) {
  const file = path.join(root, relative);
  const dom = new JSDOM(fs.readFileSync(file, 'utf8'), {
    url: 'https://example.invalid/' + relative,
    runScripts: 'dangerously',
    beforeParse(window) {
      window.requestAnimationFrame = (callback) => setTimeout(callback, 0);
    },
  });
  dom.window.eval(appScript);
  return dom;
}

for (const relative of manifest) {
  const dom = load(relative);
  const { document } = dom.window;
  if (document.querySelectorAll('h1').length !== 1) {
    problems.push(`${relative}: expected exactly one h1`);
  }
  if (document.querySelectorAll('nav a[aria-current="page"]').length !== 1) {
    problems.push(`${relative}: expected exactly one active navigation link`);
  }
  const rows = [...document.querySelectorAll('table tbody tr')];
  for (const [index, row] of rows.entries()) {
    if (row.querySelectorAll('td').length === 0) continue;
    // Rows produced in the browser from reader-supplied controls carry no
    // evidence badge by design; they are arithmetic, not sourced figures.
    if (row.closest('table[data-generated="client"]')) continue;
    if (row.querySelectorAll('a.source').length < 1) {
      problems.push(`${relative}: row ${index + 1} has no source link`);
    }
    if (row.querySelectorAll('.badge').length < 1) {
      problems.push(`${relative}: row ${index + 1} has no evidence badge`);
    }
  }
  if (!document.getElementById('runtime-payload')) {
    problems.push(`${relative}: missing the local runtime payload`);
  }
  dom.window.close();
}

/* Suggestions: review choices persist locally and reset cleanly. */
{
  const dom = load('pages/suggestions.html');
  const { document, window } = dom.window;
  const selects = [...document.querySelectorAll('.review-choice')];
  assert.ok(selects.length >= 20, `expected a populated review queue, found ${selects.length}`);
  selects[0].value = 'Investigate';
  selects[0].dispatchEvent(new window.Event('change', { bubbles: true }));
  assert.match(document.getElementById('review-summary').textContent, /1 investigate/i);
  assert.ok(window.localStorage.getItem('inheritance-review-choices-v1'));
  document.getElementById('reset-reviews').click();
  assert.match(document.getElementById('review-summary').textContent, /0 investigate/i);
  dom.window.close();
}

/* Projections: moving a control recomputes the stats and the tables. */
{
  const dom = load('pages/projections.html');
  const { document, window } = dom.window;
  const stat = () => document.querySelector('#scenario-stats .stat .stat-value').textContent;
  const cell = () => document.querySelector('.table-section table tbody tr:last-child td:nth-child(2)').textContent;
  const statBefore = stat();
  const cellBefore = cell();
  const slider = document.getElementById('transfer_year');
  slider.value = '2050';
  slider.dispatchEvent(new window.Event('input', { bubbles: true }));
  assert.notEqual(stat(), statBefore, 'transfer year did not change the scenario stats');
  const growth = document.getElementById('a_appreciation');
  growth.value = '6';
  growth.dispatchEvent(new window.Event('input', { bubbles: true }));
  assert.notEqual(cell(), cellBefore, 'growth rate did not change the projection table');
  assert.match(stat(), /^\$[\d,]+$/, 'scenario stat should render a rounded dollar amount');
  dom.window.close();
}

/* Staging tool: three cases and five risk statements, all computed locally. */
{
  const dom = load('pages/phased-investing.html');
  const { document, window } = dom.window;
  const rows = document.querySelectorAll('#calc-rows tr');
  assert.equal(rows.length, 3, 'expected three entry cases');
  const risks = document.querySelectorAll('#calc-risk li');
  assert.equal(risks.length, 5, 'expected five reinvestment-risk statements');
  const stagedValue = () => document.querySelectorAll('#calc-rows tr')[1].querySelector('td').textContent;
  const immediateValue = () => document.querySelectorAll('#calc-rows tr')[0].querySelector('td').textContent;
  const set = (id, value) => {
    const node = document.getElementById(id);
    node.value = String(value);
    node.dispatchEvent(new window.Event('input', { bubbles: true }));
  };

  // A fall that lands inside the staging window moves the immediate case.
  const immediateBefore = immediateValue();
  set('calc-drop', 89);
  assert.notEqual(immediateValue(), immediateBefore, 'fall depth did not change the immediate case');

  // The same fall is fully avoided by the staged case while it is still in cash.
  set('calc-drop-start', 6);
  const stagedInWait = stagedValue();
  set('calc-drop', 20);
  assert.equal(stagedValue(), stagedInWait, 'a fall inside the wait should not move the staged case');

  // Once the money is invested, the same fall does move the staged case.
  set('calc-drop-start', 40);
  set('calc-drop', 89);
  const stagedAfterEntry = stagedValue();
  set('calc-drop', 20);
  assert.notEqual(stagedValue(), stagedAfterEntry, 'a fall after entry did not move the staged case');
  assert.match(document.getElementById('calc-risk').textContent, /yield/i);
  dom.window.close();
}

if (problems.length) {
  console.error('DOM check FAILED');
  problems.forEach(line => console.error('  ' + line));
  process.exit(1);
}
console.log(`DOM check passed: ${manifest.length} pages; every row sourced and badged; review queue; projection controls; staging calculator.`);
