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

// Local-only Treasury-ladder / phased-equity stress calculator. No values are
// stored, transmitted, or read from a network. All outputs are illustrative.
const phaseForm = document.getElementById('phase-tool');
if (phaseForm) {
  const get = id => document.getElementById(id);
  const number = (id, fallback) => {
    const value = Number(get(id)?.value);
    return Number.isFinite(value) ? value : fallback;
  };
  const roundTen = value => Math.sign(value) * Math.floor(Math.abs(value) / 10 + 0.5) * 10;
  const dollars = value => new Intl.NumberFormat('en-US', {
    style: 'currency', currency: 'USD', maximumFractionDigits: 0
  }).format(roundTen(value));
  function simulate() {
    const principal = Math.max(0, number('phase-principal', 1000000));
    const phaseMonths = Math.max(1, Math.min(number('phase-months', 30), 360));
    const treasury = number('phase-treasury', 3) / 100;
    const equity = number('phase-equity', 6) / 100;
    const drawdown = Math.max(0, Math.min(number('phase-drawdown', 50) / 100, 0.9));
    const crashMonth = Math.max(0, Math.min(number('phase-crash-month', 0), 360));
    const recovery = Math.max(1, number('phase-recovery', 60));
    const horizon = Math.max(phaseMonths, number('phase-horizon', 120));
    const months = Math.min(phaseMonths, horizon);
    const priceAt = month => {
      const trend = Math.pow(1 + equity, month / 12);
      let shock = 1;
      if (month >= crashMonth && month < crashMonth + recovery) {
        shock = 1 - drawdown + drawdown * (month - crashMonth) / recovery;
      }
      return trend * shock;
    };
    let reserve = principal;
    let phasedShares = 0;
    let phasedPeak = principal;
    let immediatePeak = principal;
    let phasedWorst = 0;
    let immediateWorst = 0;
    const immediateShares = principal;
    for (let month = 1; month <= horizon; month++) {
      const price = priceAt(month);
      if (month <= months) {
        reserve *= Math.pow(1 + treasury, 1 / 12);
        const purchase = Math.min(principal / months, reserve);
        phasedShares += purchase / Math.max(price, 1e-9);
        reserve -= purchase;
        if (month === months && reserve > 0) {
          phasedShares += reserve / Math.max(price, 1e-9);
          reserve = 0;
        }
      }
      const immediateValue = immediateShares * price;
      const phasedValue = phasedShares * price + reserve;
      immediatePeak = Math.max(immediatePeak, immediateValue);
      phasedPeak = Math.max(phasedPeak, phasedValue);
      immediateWorst = Math.min(immediateWorst, immediateValue / immediatePeak - 1);
      phasedWorst = Math.min(phasedWorst, phasedValue / phasedPeak - 1);
    }
    const immediateTerminal = immediateShares * priceAt(horizon);
    const phasedTerminal = phasedShares * priceAt(horizon) + reserve;
    get('phase-immediate-value').textContent = dollars(immediateTerminal);
    get('phase-phased-value').textContent = dollars(phasedTerminal);
    get('phase-immediate-dd').textContent = `${(immediateWorst * 100).toFixed(1)}%`;
    get('phase-phased-dd').textContent = `${(phasedWorst * 100).toFixed(1)}%`;
    let interpretation = 'For these assumptions, phasing lowers the modeled maximum drawdown.';
    if (phasedWorst < immediateWorst - 0.0001) interpretation = 'For these assumptions, phasing does not lower the modeled maximum drawdown.'
    else if (Math.abs(phasedWorst - immediateWorst) <= 0.0001) interpretation = 'For these assumptions, phasing does not materially change the modeled maximum drawdown.';
    if (phasedTerminal < immediateTerminal) interpretation += ' It also ends below the immediate path at this horizon.';
    else if (phasedTerminal > immediateTerminal) interpretation += ' It ends above the immediate path at this horizon.';
    get('phase-status').textContent = `${interpretation} Scenario only; not a forecast.`;
  }
  get('phase-stress-preset')?.addEventListener('change', () => {
    if (get('phase-stress-preset').value === 'deep') {
      get('phase-drawdown').value = '50'; get('phase-recovery').value = '60';
    } else if (get('phase-stress-preset').value === 'sharp') {
      get('phase-drawdown').value = '35'; get('phase-recovery').value = '36';
    }
    simulate();
  });
  const controls = [...phaseForm.querySelectorAll('input, select')];
  const updateFromControl = event => {
    if (['phase-drawdown', 'phase-recovery'].includes(event.currentTarget.id)) {
      get('phase-stress-preset').value = 'custom';
    }
    simulate();
  };
  controls.forEach(control => control.addEventListener('input', updateFromControl));
  controls.forEach(control => control.addEventListener('change', updateFromControl));
  get('phase-reset')?.addEventListener('click', () => {
    get('phase-stress-preset').value = 'deep';
    get('phase-principal').value = '1000000';
    get('phase-months').value = '30';
    get('phase-treasury').value = '3';
    get('phase-equity').value = '6';
    get('phase-drawdown').value = '50';
    get('phase-crash-month').value = '0';
    get('phase-recovery').value = '60';
    get('phase-horizon').value = '120';
    simulate();
  });
  simulate();
}
