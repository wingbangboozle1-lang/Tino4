'use strict';
// No network requests, private inputs, analytics, or remotely stored approvals.
const year = document.getElementById('inherit-year');
if (year) {
  year.addEventListener('change', () => {
    document.querySelectorAll('.projection-group').forEach(group => {
      group.hidden = group.dataset.year !== year.value;
    });
  });
}
document.getElementById('print-page')?.addEventListener('click', () => window.print());

// Phased-entry what-if controls run only in this browser. The paths are
// illustrative price-index scenarios; no values are sent to a server.
const phaseLab = document.querySelector('.phase-lab');
if (phaseLab) {
  const get = id => document.getElementById(id);
  const controls = {
    principal: get('phase-principal'), wait: get('phase-wait'), ramp: get('phase-ramp'),
    yield: get('phase-yield'), sequence: get('phase-sequence'), immediate: get('phase-immediate')
  };
  const labels = {
    '1929': '1929-like severe drawdown (synthetic linear path)',
    '2008': '2008–2011 annual-point price-index sequence (interpolated)',
    rising: 'invented rising-market opportunity-cost case'
  };
  let paths;
  try { paths = JSON.parse(phaseLab.dataset.paths); }
  catch (_) { paths = null; }
  const displayMoney = value => {
    const rounded = Math.sign(value) * Math.round(Math.abs(value) / 10) * 10;
    return `${rounded < 0 ? '−' : ''}$${Math.abs(rounded).toLocaleString('en-US')}`;
  };
  const calculate = () => {
    const principal = Number(controls.principal.value);
    const wait = Number(controls.wait.value);
    const ramp = Number(controls.ramp.value);
    const annualYield = Number(controls.yield.value) / 100;
    const immediateShare = Number(controls.immediate.value);
    const scenario = controls.sequence.value;
    const explanation = get('phase-explanation');
    const error = get('phase-error');
    if (!paths || !paths[scenario] || !Number.isFinite(principal) || principal < 10000 || principal > 5000000 ||
        !Number.isFinite(annualYield) || annualYield < 0 || annualYield > 0.06 ||
        wait + ramp > 48 || !Number.isFinite(immediateShare)) {
      error.textContent = 'Use a starting amount from $10,000 to $5,000,000 and a gross yield from 0% to 6%.';
      return;
    }
    error.textContent = '';
    const market = paths[scenario];
    const monthlyGrowth = Math.pow(1 + annualYield, 1 / 12);
    let cash = principal * (1 - immediateShare);
    let shares = principal * immediateShare / market[0];
    let fixedPurchase = 0;
    for (let month = 1; month <= 48; month += 1) {
      cash *= monthlyGrowth;
      if (month === wait) {
        let annuityFactor = 0;
        for (let k = 0; k < ramp; k += 1) annuityFactor += Math.pow(monthlyGrowth, k);
        fixedPurchase = cash * Math.pow(monthlyGrowth, ramp) / annuityFactor;
      }
      if (month > wait && month <= wait + ramp) {
        const purchase = month === wait + ramp ? cash : Math.min(cash, fixedPurchase);
        shares += purchase / market[month];
        cash -= purchase;
      }
    }
    const immediateValue = principal * market[48] / market[0];
    const phaseValue = shares * market[48] + cash;
    const treasuryOnly = principal * Math.pow(1 + annualYield, 4);
    get('phase-immediate-value').textContent = displayMoney(immediateValue);
    get('phase-staged-value').textContent = displayMoney(phaseValue);
    get('phase-treasury-value').textContent = displayMoney(treasuryOnly);
    get('phase-delta-value').textContent = displayMoney(phaseValue - immediateValue);
    explanation.textContent = `Selected case: ${labels[scenario]}. ${Math.round(immediateShare * 100)}% is invested in stocks at month 0; the remaining cash earns the assumed ${(annualYield * 100).toFixed(2)}% gross annual yield, then enters stocks in ${ramp} equal-dollar monthly installments after a ${wait}-month bridge. Values are compared at month 48, before tax, inflation, dividends, fees and any note-sale price change.`;
  };
  Object.values(controls).forEach(control => {
    control?.addEventListener('input', calculate);
    control?.addEventListener('change', calculate);
  });
  calculate();
}

const storageKey = 'public-suggestion-review-v1';
const choices = [...document.querySelectorAll('.review-choice')];
const summary = document.getElementById('review-summary');
let state = {};
let storageAvailable = true;
try {
  const data = JSON.parse(localStorage.getItem(storageKey) || '{}');
  if (data && typeof data === 'object' && !Array.isArray(data)) state = data;
} catch (_) { storageAvailable = false; }
const allowed = new Set(['Not reviewed', 'Investigate', 'Preferred path', 'Defer']);
function updateSummary() {
  if (!summary) return;
  const count = choices.filter(choice => choice.value !== 'Not reviewed').length;
  summary.textContent = `${count} of ${choices.length} proposals reviewed. ${storageAvailable ? 'Saved only in this browser.' : 'Browser storage unavailable; choices last only for this page.'} No changes implemented.`;
}
choices.forEach(choice => {
  if (allowed.has(state[choice.dataset.id])) choice.value = state[choice.dataset.id];
  choice.addEventListener('change', () => {
    state = Object.fromEntries(choices.map(item => [item.dataset.id, item.value]));
    try { localStorage.setItem(storageKey, JSON.stringify(state)); }
    catch (_) { storageAvailable = false; }
    updateSummary();
  });
});
document.getElementById('reset-reviews')?.addEventListener('click', () => {
  choices.forEach(choice => { choice.value = 'Not reviewed'; });
  state = {};
  try { localStorage.removeItem(storageKey); }
  catch (_) { storageAvailable = false; }
  updateSummary();
});
updateSummary();
