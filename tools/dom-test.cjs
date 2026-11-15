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

// 3. Review queues save only in local storage and reset cleanly.
const log = load('pages/decision-log.html');
const doc = log.window.document;
const reviewTotal = doc.querySelectorAll('.review-choice').length;
assert.ok(reviewTotal >= 12, `expected at least 12 logged decisions, saw ${reviewTotal}`);
const choice = doc.querySelector('.review-choice[data-id="D07"]');
choice.value = 'Selected for testing';
choice.dispatchEvent(new log.window.Event('change'));
assert.match(doc.getElementById('review-summary').textContent, new RegExp(`1 of ${reviewTotal} suggestions reviewed`));
assert.ok(log.window.localStorage.getItem('public-suggestion-review-v2').includes('D07'));
// 4. Carry-or-sell tool on the sale-timing page: every panel populates, and a
//    rented hold must produce depreciation recapture where an occupied hold does not.
const carry = load('pages/sale-timing.html');
const cdoc = carry.window.document;
const cval = id => cdoc.getElementById(id).textContent;
for (const id of ['carry-price', 'carry-gain', 'carry-taxes', 'carry-net', 'carry-relief', 'carry-breakeven', 'carry-imputed']) {
  assert.ok(cval(id) && cval(id) !== '—', `carry tool output ${id} was not populated`);
}
assert.equal(cval('carry-recapture'), 'none modeled', 'an occupied hold must not model depreciation recapture');
const useSelect = cdoc.getElementById('carry-use');
useSelect.value = 'rent';
useSelect.dispatchEvent(new carry.window.Event('change'));
assert.match(cval('carry-recapture'), /\$/, 'a rented hold must produce a recapture amount');
const rentNet = Number(cval('carry-net').replace(/[^0-9.]/g, ''));
useSelect.value = 'own121';
useSelect.dispatchEvent(new carry.window.Event('change'));
const liveNet = Number(cval('carry-net').replace(/[^0-9.]/g, ''));
assert.ok(liveNet > rentNet, 'meeting the main-home tests should beat a rented hold on net proceeds at these defaults');
assert.equal(cdoc.querySelectorAll('form[action]').length, 0, 'the tool must not be a submitting form');
assert.equal(/fetch|XMLHttpRequest|sendBeacon/.test(script), false);
doc.getElementById('reset-reviews').click();
assert.equal(doc.querySelector('.review-choice[data-id="D07"]').value, 'Not reviewed');

console.log('DOM smoke passed: phased-entry scenarios, ladder reinvestment penalty, review-queue save/reset, no network API.');
