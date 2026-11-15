#!/usr/bin/env node
/* Offline DOM and script check.

   Loads every generated page, evaluates the local scripts, and asserts
   structure, sourcing and interactive behaviour. It runs without a browser
   engine so it can run anywhere Node is available; the fuller Playwright smoke
   test in tools/browser-test.cjs additionally checks layout where the optional
   browser dependencies are installed.

   Usage: node tools/dom-test.cjs   (needs jsdom in tools/browser/node_modules)
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

/* External resource loading is disabled, so the deferred local scripts are
   evaluated directly after parsing. This still exercises the real scripts. */
const engineScript = fs.readFileSync(path.join(root, 'assets', 'projection-engine.js'), 'utf8');
const appScript = fs.readFileSync(path.join(root, 'assets', 'app.js'), 'utf8');

function load(relative) {
  const file = path.join(root, relative);
  const dom = new JSDOM(fs.readFileSync(file, 'utf8'), {
    url: 'https://example.invalid/' + relative,
    runScripts: 'dangerously',
    beforeParse(window) {
      window.requestAnimationFrame = (callback) => setTimeout(callback, 0);
    },
  });
  dom.window.eval(engineScript);
  dom.window.eval(appScript);
  return dom;
}

const problems = [];

for (const relative of manifest) {
  const dom = load(relative);
  const { document } = dom.window;
  if (document.querySelectorAll('h1').length !== 1) {
    problems.push(`${relative}: expected exactly one h1`);
  }
  if (document.querySelectorAll('nav a[aria-current="page"]').length !== 1) {
    problems.push(`${relative}: expected exactly one active navigation link`);
  }
  for (const [index, row] of [...document.querySelectorAll('table tbody tr')].entries()) {
    if (row.querySelectorAll('td').length === 0) continue;
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

/* Working figures: every published amount is a multiple of ten dollars. */
{
  let checked = 0;
  for (const relative of manifest) {
    const { document } = load(relative).window;
    for (const cell of document.querySelectorAll('td')) {
      const text = cell.textContent.trim();
      const match = /^\$([0-9][0-9,]*)$/.exec(text);
      if (!match) continue;
      const value = Number(match[1].replace(/,/g, ''));
      if (value % 10 !== 0) {
        problems.push(`${relative}: "${text}" is not rounded to ten dollars`);
      }
      checked += 1;
    }
  }
  assert.ok(checked > 50, `expected published working figures, scanned ${checked}`);
}

/* Suggestions and decision log: review choices persist locally and reset. */
for (const relative of ['pages/suggestions.html', 'pages/decision-log.html']) {
  const dom = load(relative);
  const { document, window } = dom.window;
  const selects = [...document.querySelectorAll('.review-choice')];
  assert.ok(selects.length >= 10, `${relative}: expected a populated queue, found ${selects.length}`);
  const first = selects[0].dataset.id;
  selects[0].value = 'Investigate';
  selects[0].dispatchEvent(new window.Event('change', { bubbles: true }));
  assert.match(
    document.getElementById('review-summary').textContent,
    new RegExp(`1 of ${selects.length} suggestions reviewed`),
    `${relative}: summary did not update`
  );
  assert.ok(window.localStorage.getItem('public-suggestion-review-v2'), `${relative}: not persisted`);
  document.getElementById('reset-reviews').click();
  assert.match(
    document.getElementById('review-summary').textContent,
    new RegExp(`0 of ${selects.length} suggestions reviewed`),
    `${relative}: reset did not clear the queue`
  );
  dom.window.close();
}

/* Treasury staging tool: both scenarios compute and the ladder reports the
   reinvestment penalty. */
{
  const dom = load('pages/phased-investing.html');
  const { document, window } = dom.window;
  const text = id => document.getElementById(id).textContent;
  assert.notEqual(text('early-phased-value').trim(), '—', 'early scenario never computed');
  assert.notEqual(text('late-phased-value').trim(), '—', 'late scenario never computed');
  const before = text('early-phased-value');
  const select = document.getElementById('phase-event');
  select.value = '1929';
  select.dispatchEvent(new window.Event('change', { bubbles: true }));
  assert.notEqual(text('early-phased-value'), before, 'changing the anchor did not recompute');
  assert.match(text('phase-status'), /assumption-driven scenarios/i);
  assert.notEqual(text('early-months'), text('late-months'), 'early and late horizons should differ');
  assert.deepEqual(
    Object.keys(window.localStorage).filter(key => key.startsWith('phase-')),
    [],
    'staging inputs must not be stored'
  );
  dom.window.close();
}

/* Working-figure projection controls recompute the year-by-year tables locally. */
{
  const dom = load('pages/projections.html');
  const { document, window } = dom.window;
  const form = document.getElementById('projection-tool');
  assert.ok(form, 'missing the projection controls');
  const tableByCaption = prefix =>
    [...document.querySelectorAll('table')].find(
      table => table.querySelector('caption') &&
        table.querySelector('caption').textContent.trim().startsWith(prefix)
    );
  const tableA = tableByCaption('Property A — value');
  const tableB = tableByCaption('Property B — value');
  assert.ok(tableA && tableB, 'missing the year-by-year projection tables');

  const lastA = () => [...tableA.querySelectorAll('tbody tr')].pop().children[1].textContent;
  const lastB = () => [...tableB.querySelectorAll('tbody tr')].pop().children[4].textContent;
  const status = () => document.getElementById('projection-status').textContent;

  const aBefore = lastA();
  const bBefore = lastB();
  const statusBefore = status();

  const set = (id, value) => {
    const node = document.getElementById(id);
    node.value = String(value);
    node.dispatchEvent(new window.Event('input', { bubbles: true }));
  };

  set('a_appreciation', 6);
  assert.notEqual(lastA(), aBefore, 'growth rate did not move the Property A table');
  set('rent_growth', 7);
  assert.notEqual(lastB(), bBefore, 'rent growth did not move the Property B table');
  set('transfer_year', 2050);
  assert.notEqual(status(), statusBefore, 'transfer year did not update the summary');
  assert.match(status(), /^\$[\d,]+$|transfer/i, 'summary should describe the transfer year');
  assert.match(lastA(), /^\$[\d,]+$/);

  document.getElementById('projection-reset').click();
  assert.equal(lastA(), aBefore, 'reset did not restore the defaults');
  assert.deepEqual(
    Object.keys(window.localStorage).filter(key => key.startsWith('proj')),
    [],
    'projection inputs must not be stored'
  );
  dom.window.close();
}

if (problems.length) {
  console.error('DOM check FAILED');
  problems.forEach(line => console.error('  ' + line));
  process.exit(1);
}
console.log(`DOM check passed: ${manifest.length} pages; every row sourced and badged; working figures rounded to ten dollars; review queues; staging tool; projection controls.`);
