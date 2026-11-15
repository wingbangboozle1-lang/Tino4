// Optional DOM smoke test for the local-only interactive panels.
// Uses jsdom so it runs without a browser binary; serve nothing, no network.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const candidates = [
  process.env.DOM_MODULES,
  path.join(__dirname, 'browser', 'node_modules'),
  path.join(process.cwd(), 'node_modules'),
].filter(Boolean);
const modules = candidates.find(candidate => fs.existsSync(path.join(candidate, 'jsdom')));
if (!modules) throw new Error('jsdom not found; install optional test dependencies or set DOM_MODULES.');
const { JSDOM } = require(path.join(modules, 'jsdom'));

const script = fs.readFileSync(path.join(__dirname, '..', 'assets', 'app.js'), 'utf8');
const read = relative => fs.readFileSync(path.join(__dirname, '..', relative), 'utf8');

function load(relative) {
  const dom = new JSDOM(read(relative), { runScripts: 'outside-only', url: 'https://example.invalid/' + relative });
  dom.window.print = () => {};
  dom.window.eval(script);
  return dom;
}

// 1. Phased-entry panel computes both entry scenarios.
const phased = load('pages/phased-investing.html');
const value = id => phased.window.document.getElementById(id).textContent;
assert.notEqual(value('early-phased-value'), '—');
assert.notEqual(value('late-immediate-value'), '—');
assert.match(value('phase-status'), /assumption-driven scenarios/i);

// 2. Ladder panel reports a reinvestment penalty and reacts to a lower renewal yield.
const ladder = load('pages/phased-investing.html');
const flat = ladder.window.document.getElementById('ladder-flat-interest').textContent;
const falling = ladder.window.document.getElementById('ladder-falling-interest').textContent;
const lost = ladder.window.document.getElementById('ladder-falling-year').textContent;
assert.notEqual(flat, '—');
assert.notEqual(falling, '—');
assert.notEqual(lost, '—');
assert.notEqual(flat, falling, 'constant and falling renewal paths must differ by default');
const dropped = Number(lost.split(' ')[0]);
assert.ok(dropped > 0, `expected a positive reinvestment penalty, saw ${lost}`);
const renewal = ladder.window.document.getElementById('ladder-renewal3');
renewal.value = '0';
renewal.dispatchEvent(new ladder.window.Event('input'));
const lostAfter = Number(ladder.window.document.getElementById('ladder-falling-year').textContent.split(' ')[0]);
assert.ok(lostAfter > dropped, 'a lower renewal yield must increase the penalty');

// 3. Path tool prices the sell branch: transfer tax, fees, gain sensitivity, recapture.
const analysis = load('pages/decision-analysis.html');
const av = id => analysis.window.document.getElementById(id).textContent;
for (const id of ['path-transfer-tax', 'path-closing', 'path-net', 'path-taxes', 'path-aftertax',
                  'path-imputed10', 'path-sellnet', 'path-hurdle']) {
  assert.notEqual(av(id), '—', `${id} never computed`);
}
// Published county schedule: 0.55 per $500 on the default price.
assert.equal(av('path-transfer-tax'), '$7,180');
assert.equal(av('path-gain'), 'nil', 'a date-of-death basis should show no gain by default');
assert.match(av('path-recap'), /nil/);
const zeroTax = av('path-taxes');
const gainBox = analysis.window.document.getElementById('path-gainpct');
gainBox.value = '100';
gainBox.dispatchEvent(new analysis.window.Event('input'));
const taxedGain = Number(av('path-gain').replace(/[$,]/g, ''));
assert.ok(taxedGain > 6000000, `full-price gain expected, saw ${av('path-gain')}`);
assert.notEqual(av('path-taxes'), zeroTax, 'a bigger gain must change the modeled tax');
assert.ok(Number(av('path-aftertax').replace(/[$,]/g, '')) < Number(av('path-net').replace(/[$,]/g, '')),
  'after-tax proceeds cannot exceed the net before income tax');
// Depreciation moves part of the gain into the 25% recapture bucket.
const depreciation = analysis.window.document.getElementById('path-depr');
depreciation.value = '1500000';
depreciation.dispatchEvent(new analysis.window.Event('input'));
assert.match(av('path-recap'), /\$375,000 on \$1,500,000/, 'recapture must be the ceiling rate on the depreciation portion');
// The main-home exclusion must reduce the taxable gain, and reset must restore the baseline.
const principal = analysis.window.document.getElementById('path-principal');
principal.checked = true;
principal.dispatchEvent(new analysis.window.Event('change'));
const excludedGain = Number(av('path-gain').replace(/[$,]/g, ''));
assert.equal(excludedGain, taxedGain - 250000, 'the exclusion must come off the gain');
analysis.window.document.getElementById('path-reset').click();
assert.equal(av('path-gain'), 'nil', 'reset must return to the date-of-death baseline');
assert.equal(av('path-transfer-tax'), '$7,180');

// 4. Proposition H estimator: class, inflation and the pass-through ceiling.
const propH = load('pages/rental-economics.html');
const pv = id => propH.window.document.getElementById(id).textContent;
for (const id of ['ph-charge', 'ph-cum', 'ph-life', 'ph-pass', 'ph-net']) {
  assert.notEqual(pv(id), '—', `${id} never computed`);
}
assert.equal(pv('ph-charge'), '$250', 'published first-year multifamily amount, rounded for display');
assert.equal(pv('ph-pass'), '$130', 'two rent-controlled units at the published 65 dollar ceiling');
assert.equal(pv('ph-net'), '$120', 'owner cost is the charge less what may be passed through');
const phClass = propH.window.document.getElementById('ph-class');
phClass.value = '799';
phClass.dispatchEvent(new propH.window.Event('change'));
assert.ok(Number(pv('ph-charge').replace(/[$,]/g, '')) > 250, 'a nonresidential class must cost more');
const phYear = propH.window.document.getElementById('ph-year');
phYear.value = '2042';
phYear.dispatchEvent(new propH.window.Event('input'));
assert.equal(pv('ph-cum'), pv('ph-life'), 'the sunset year must equal the lifetime total');
phYear.value = '2026';
phYear.dispatchEvent(new propH.window.Event('input'));
assert.match(pv('ph-charge'), /no charge in this year/, 'the tax cannot be charged before FY 2027-28');
propH.window.document.getElementById('ph-reset').click();
assert.equal(pv('ph-charge'), '$250', 'reset must return to the published baseline');

// 5. The projections chart must render from the model, not from a hand-typed number.
const projections = load('pages/projections.html');
const chart = projections.window.document.querySelector('svg.dist-chart');
assert.ok(chart, 'distribution chart missing');
assert.equal(chart.querySelectorAll('rect.dist-bar').length, 6, 'one bar per labeled market regime');
assert.ok(/^\$[0-9,]+$/.test(chart.querySelector('text.dist-value').textContent), 'bars must be labeled with rounded dollars');
assert.notEqual(chart.querySelector('text.dist-value').textContent,
  chart.querySelectorAll('text.dist-value')[5].textContent, 'a flat distribution would be a bug');

// 6. Review queues save only in local storage and reset cleanly.
const log = load('pages/decision-log.html');
const doc = log.window.document;
assert.equal(doc.querySelectorAll('.review-choice').length, 12);
const choice = doc.querySelector('.review-choice[data-id="D07"]');
choice.value = 'Selected for testing';
choice.dispatchEvent(new log.window.Event('change'));
assert.match(doc.getElementById('review-summary').textContent, /1 of 12 suggestions reviewed/);
assert.ok(log.window.localStorage.getItem('public-suggestion-review-v2').includes('D07'));
assert.equal(/fetch|XMLHttpRequest|sendBeacon/.test(script), false);
doc.getElementById('reset-reviews').click();
assert.equal(doc.querySelector('.review-choice[data-id="D07"]').value, 'Not reviewed');

console.log('DOM smoke passed: phased-entry scenarios, ladder reinvestment penalty, priced path tool '
  + '(transfer tax, gain sensitivity, recapture, imputed rent), Proposition H estimator, projections chart, '
  + 'review-queue save/reset, no network API.');
