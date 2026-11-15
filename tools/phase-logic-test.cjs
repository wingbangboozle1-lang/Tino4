// Headless functional check of the phased-investing calculator logic.
// Runs assets/app.js against a minimal DOM stub and asserts the model output:
// the headline, the reinvestment-risk line beside it, the ladder split, the
// parked-reserve yield and the renewal-yield stress.
//
// Run with: node tools/phase-logic-test.cjs
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const ROOT = path.resolve(__dirname, '..');

const CONTROL_IDS = [
  'phase-event', 'phase-months', 'phase-noteshare', 'phase-drawdown',
  'phase-trough', 'phase-drift', 'phase-yield1', 'phase-yield2',
  'phase-yielddrop', 'phase-inflation',
];

function makeElement(id) {
  return {
    id,
    value: '',
    textContent: '',
    dataset: {},
    listeners: {},
    addEventListener(type, handler) { this.listeners[type] = handler; },
    querySelectorAll() {
      if (id === 'phase-tool') return CONTROL_IDS.map(controlId => get(controlId));
      return [];
    },
  };
}

const elements = new Map();
const get = id => {
  if (!elements.has(id)) elements.set(id, makeElement(id));
  return elements.get(id);
};

const store = new Map();
const sandbox = {
  console,
  window: { print() {} },
  localStorage: {
    getItem: k => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => store.set(k, v),
    removeItem: k => store.delete(k),
  },
  document: {
    getElementById: id => get(id),
    querySelectorAll: () => [],
  },
};
sandbox.globalThis = sandbox;

const script = fs.readFileSync(path.join(ROOT, 'assets/app.js'), 'utf8');
vm.createContext(sandbox);
vm.runInContext(script, sandbox);

function setValues(values) {
  for (const [id, value] of Object.entries(values)) get(id).value = String(value);
  for (const controlId of CONTROL_IDS) {
    const control = get(controlId);
    if (control.listeners.input) control.listeners.input();
  }
}

function number(id) {
  return Number.parseFloat(get(id).textContent.replace(/[^0-9.\-]/g, ''));
}

// Default run: 2008 anchor, 30-month parking, 50% in 2-year notes.
setValues({
  'phase-event': '2008',
  'phase-months': '30',
  'phase-noteshare': '50',
  'phase-drawdown': '57',
  'phase-trough': '17',
  'phase-drift': '0',
  'phase-yield1': '0',
  'phase-yield2': '0',
  'phase-yielddrop': '1',
  'phase-inflation': '0',
});

assert.match(get('phase-status').textContent, /phasing .* immediate investment/, 'status line missing');
assert.match(get('early-headline').textContent, /Phasing (is nearly even with|ends above|ends below) immediate investment/, 'headline missing');
assert.match(get('late-headline').textContent, /Phasing/, 'late headline missing');
assert.match(get('early-reinvestment').textContent, /re-prices quarterly from month 13/, 'reinvestment line missing');
assert.match(get('early-lock').textContent, /locked in 2-year notes to month 24/, 'lock line missing');
assert.match(get('early-reinvest-cost').textContent, /if renewal yields fall 1\.00 points/, 'reinvest cost missing');

const earlyValue = number('early-phased-value');
const lateValue = number('late-phased-value');
const immediateValue = number('late-immediate-value');
assert.ok(earlyValue > 0 && lateValue > 0 && immediateValue > 0, 'values must be positive');
assert.ok(Math.abs(lateValue - immediateValue) < 0.5, 'with no drift and no yield both paths hold the same index exposure');
// A crash that starts during the parking window buys more units at lower prices.
assert.ok(earlyValue > number('early-immediate-value'), 'phasing through a falling market should buy more units');
// A rising market before the crash makes staged buying lag a lump-sum investment.
setValues({ 'phase-drift': '5' });
assert.ok(number('late-phased-value') < number('late-immediate-value'), 'staged buying should lag in a rising market');
setValues({ 'phase-drift': '0' });

// With a 3 percentage point yield, the parked reserve must earn more than at zero.
setValues({ 'phase-yield1': '3', 'phase-yield2': '3' });
const withYield = number('late-phased-value');
assert.ok(withYield > lateValue, `parked yield must raise the phased value (${withYield} vs ${lateValue})`);

// A full 2-year-note allocation must show less quarterly re-pricing than an all-bill ladder.
setValues({ 'phase-yield1': '0', 'phase-yield2': '0', 'phase-noteshare': '0' });
const allBills = get('early-reinvestment').textContent;
setValues({ 'phase-noteshare': '100' });
const allNotes = get('early-reinvestment').textContent;
assert.notEqual(allBills, allNotes, 'the ladder split must change the re-pricing share');
assert.ok(allBills.startsWith('100%'), `an all-bill ladder re-prices entirely: ${allBills}`);
assert.ok(allNotes.startsWith('0%'), `an all-note ladder re-prices nothing before month 13: ${allNotes}`);

// A falling renewal yield must cost the phased path.
setValues({ 'phase-noteshare': '50', 'phase-yield1': '4', 'phase-yield2': '4', 'phase-yielddrop': '1' });
const costText = get('late-reinvest-cost').textContent;
assert.match(costText, /lost if renewal yields fall 1\.00 points/, `unexpected cost line: ${costText}`);

console.log('OK — phased calculator logic behaves as documented');
