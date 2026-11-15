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
// Count is derived from the page rather than hardcoded, so adding a logged
// decision cannot silently break the release gate.
const reviewCount = doc.querySelectorAll('.review-choice').length;
assert.ok(reviewCount >= 12, `expected at least 12 review controls, saw ${reviewCount}`);
assert.match(doc.getElementById('review-summary').textContent, new RegExp(`0 of ${reviewCount} suggestions reviewed`));
const choice = doc.querySelector('.review-choice[data-id="D07"]');
choice.value = 'Selected for testing';
choice.dispatchEvent(new log.window.Event('change'));
assert.match(doc.getElementById('review-summary').textContent, new RegExp(`1 of ${reviewCount} suggestions reviewed`));
assert.ok(log.window.localStorage.getItem('public-suggestion-review-v2').includes('D07'));
assert.equal(/fetch|XMLHttpRequest|sendBeacon/.test(script), false);
doc.getElementById('reset-reviews').click();
assert.equal(doc.querySelector('.review-choice[data-id="D07"]').value, 'Not reviewed');

// 4. What-if path tool: every declared output is wired, and the new inputs move it.
const decisions = load('pages/decision-analysis.html');
const d = decisions.window.document;
const dvalue = id => d.getElementById(id).textContent;
for (const id of ['path-tax-excl', 'path-hurdle', 'path-sellnet', 'path-imputed10',
                  'path-liveadj', 'path-sellnet2', 'path-selladj']) {
  assert.notEqual(dvalue(id), '\u2014', `${id} was never computed`);
}
const liveBefore = dvalue('path-liveadj');
const netBefore = dvalue('path-sellnet2');
const imputed = d.getElementById('path-imputed');
imputed.value = '120000';                       // annual avoided rent, 10k a month
imputed.dispatchEvent(new decisions.window.Event('input'));
assert.notEqual(dvalue('path-liveadj'), liveBefore, 'imputed rent must change the live-in adjustment');
const cost = d.getElementById('path-sellcost');
cost.value = '10';
cost.dispatchEvent(new decisions.window.Event('input'));
assert.notEqual(dvalue('path-sellnet2'), netBefore, 'a higher cost assumption must reduce net proceeds');
assert.match(d.getElementById('path-status').textContent, /not tax advice/);

console.log('DOM smoke passed: phased-entry scenarios, ladder reinvestment penalty, review-queue save/reset, no network API, what-if inputs wired.');
