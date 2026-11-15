// Optional DOM smoke test for the local-only panels (jsdom; no browser binary, no network).
// Skips cleanly when jsdom is absent: it is not a published dependency of this repository.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const candidates = [
  process.env.DOM_MODULES,
  path.join(process.cwd(), 'node_modules'),
  path.join(__dirname, 'browser', 'node_modules'),
].filter(Boolean);
const modules = candidates.find(candidate => fs.existsSync(path.join(candidate, 'jsdom')));
if (!modules) {
  console.log('DOM smoke skipped: jsdom not installed (npm install --no-save jsdom, or set DOM_MODULES).');
  process.exit(0);
}
const { JSDOM } = require(path.join(modules, 'jsdom'));

const script = fs.readFileSync(path.join(__dirname, '..', 'assets', 'app.js'), 'utf8');
const read = relative => fs.readFileSync(path.join(__dirname, '..', relative), 'utf8');

function load(relative) {
  const dom = new JSDOM(read(relative), { runScripts: 'outside-only', url: 'https://example.invalid/' + relative });
  dom.window.print = () => {};
  dom.window.eval(script);
  return dom;
}

// 1. Treasury staging panel runs, and refuses an out-of-range staging period.
const phased = load('pages/phased-investing.html');
const phaseResult = phased.window.document.getElementById('phase-result');
const fill = (id, value) => {
  const field = phased.window.document.getElementById(id);
  field.value = String(value);
};
fill('phase-amount', 1000000);
fill('phase-months', 24);
fill('phase-yield', 4);
fill('phase-equity', 8);
fill('phase-crash', 57);
phased.window.document.getElementById('phase-run').click();
assert.match(phaseResult.textContent, /Illustrative ending values/);
assert.doesNotMatch(phaseResult.textContent, /undefined|NaN/, 'panel printed a non-number');
fill('phase-months', 6);
phased.window.document.getElementById('phase-run').click();
assert.match(phaseResult.textContent, /Enter a positive amount/, 'range guard did not fire');
phased.window.document.getElementById('phase-clear').click();
assert.match(phased.window.document.getElementById('phase-result').textContent, /Inputs cleared/);

// 2. Capital and tax sensitivity panel: depreciation, recapture, transfer cost, avoided rent.
const decisions = load('pages/decision-analysis.html');
const d = decisions.window.document;
const status = d.getElementById('cap-status');
d.getElementById('cap-basis').value = '1000000';
d.getElementById('cap-sale').value = '2000000';
d.getElementById('cap-run').click();
assert.match(status.textContent, /Depreciation: about \$36,360 a year/, 'straight-line deduction changed');
assert.match(status.textContent, /recovered over 10 years/);
assert.match(status.textContent, /federal on unrecaptured gain/, 'federal repayment line missing');
assert.match(status.textContent, /investable/, 'net proceeds line missing');
assert.match(status.textContent, /not tax advice/);
assert.doesNotMatch(status.textContent, /NaN|undefined/);
// a steeper transfer schedule must reduce what is investable
const before = status.textContent.match(/about (\$[\d,]+) investable/)[1];
d.getElementById('cap-dtt').value = '6';
d.getElementById('cap-cost').value = '7';
d.getElementById('cap-run').click();
const after = status.textContent.match(/about (\$[\d,]+) investable/)[1];
assert.notEqual(after, before, 'transfer tax input is not wired into the result');
assert.ok(Number(after.replace(/[$,]/g, '')) < Number(before.replace(/[$,]/g, '')), 'a higher transfer tax must reduce proceeds');
d.getElementById('cap-clear').click();
assert.match(status.textContent, /Inputs cleared/);

// 3. Review queue keeps its choices in the page only.
const suggestions = load('pages/suggestions.html');
const s = suggestions.window.document;
const count = s.querySelectorAll('.review-choice').length;
assert.ok(count >= 6, `expected at least 6 review controls, saw ${count}`);
const select = s.querySelector('.review-choice');
select.value = 'Adopt';
select.dispatchEvent(new suggestions.window.Event('change'));
assert.match(s.getElementById('review-summary').textContent, /1 adopt/);

// 4. No network or storage API anywhere in the published script.
assert.equal(/fetch|XMLHttpRequest|sendBeacon|localStorage|sessionStorage/.test(script), false);

console.log('DOM smoke passed: staging panel guards and clears, capital panel wired to its inputs, review queue in-memory only, no network or storage API.');
