'use strict';

// Local interactions only: no analytics, API calls, third-party assets, or
// household-specific financial input storage.
document.getElementById('print-page')?.addEventListener('click', () => window.print());

// Review choices are intentionally client-local and contain no case details.
const reviewStorageKey = 'public-suggestion-review-v2';
const reviewChoices = [...document.querySelectorAll('.review-choice')];
const reviewSummary = document.getElementById('review-summary');
let reviewState = {};
let reviewStorageAvailable = true;
try {
  const saved = JSON.parse(localStorage.getItem(reviewStorageKey) || '{}');
  if (saved && typeof saved === 'object' && !Array.isArray(saved)) reviewState = saved;
} catch (_) {
  reviewStorageAvailable = false;
}
const allowedChoices = new Set(['Not reviewed', 'Investigate', 'Selected for testing', 'Defer']);
function updateReviewSummary() {
  if (!reviewSummary) return;
  const count = reviewChoices.filter(choice => choice.value !== 'Not reviewed').length;
  reviewSummary.textContent = `${count} of ${reviewChoices.length} suggestions reviewed. ${reviewStorageAvailable ? 'Saved only in this browser.' : 'Browser storage is unavailable; choices last only for this page.'} No change was applied.`;
}
reviewChoices.forEach(choice => {
  const value = reviewState[choice.dataset.id];
  if (allowedChoices.has(value)) choice.value = value;
  choice.addEventListener('change', () => {
    reviewState = Object.fromEntries(reviewChoices.map(item => [item.dataset.id, item.value]));
    try {
      localStorage.setItem(reviewStorageKey, JSON.stringify(reviewState));
      reviewStorageAvailable = true;
    } catch (_) {
      reviewStorageAvailable = false;
    }
    updateReviewSummary();
  });
});
document.getElementById('reset-reviews')?.addEventListener('click', () => {
  reviewChoices.forEach(choice => { choice.value = 'Not reviewed'; });
  reviewState = {};
  try {
    localStorage.removeItem(reviewStorageKey);
    reviewStorageAvailable = true;
  } catch (_) {
    reviewStorageAvailable = false;
  }
  updateReviewSummary();
});
updateReviewSummary();

// Local-only Treasury-ladder / phased-equity scenario tool. Starting capital
// is normalized to 100 units; values are not currency amounts. Nothing is
// stored, transmitted, or read from a network.
const phaseForm = document.getElementById('phase-tool');
if (phaseForm) {
  const element = id => document.getElementById(id);
  const numeric = (id, fallback, min, max) => {
    const raw = Number(element(id)?.value);
    const value = Number.isFinite(raw) ? raw : fallback;
    return Math.max(min, Math.min(value, max));
  };
  const pct = value => `${value.toFixed(1)}%`;
  const units = value => `${value.toFixed(2)} units`;

  // One parking-period simulation. `noteShare` is the share of the parked
  // proceeds placed in 2-year notes (locked to maturity at month 24); the
  // remainder rolls in 3-month bills that re-price every quarter.
  // `renewalDrop` prices a fall in renewal yields, in percentage points.
  function simulateScenario(crashStart, stagingMonths, drawdown, troughMonths, drift, firstYield, renewalYield, noteShare, renewalDrop) {
    const starting = 100;
    const horizon = Math.max(stagingMonths, crashStart + troughMonths);
    const peakAtCrash = Math.pow(1 + drift, crashStart / 12);
    const indexAt = month => {
      if (month < crashStart) return Math.pow(1 + drift, month / 12);
      const elapsed = Math.min(1, Math.max(0, (month - crashStart) / troughMonths));
      return peakAtCrash * (1 - drawdown * elapsed);
    };

    let notes = starting * noteShare / 100;
    let bills = starting - notes;
    let phasedShares = 0;
    const immediateShares = starting;
    let immediatePeak = starting;
    let phasedPeak = starting;
    let immediateWorst = 0;
    let phasedWorst = 0;
    let lockedShare = 0;
    let repricingShare = 0;

    for (let month = 1; month <= horizon; month += 1) {
      const noteRate = (month <= 12 ? firstYield : renewalYield) / 100;
      const billRate = (month <= 12 ? firstYield : renewalYield - renewalDrop) / 100;
      notes *= Math.pow(1 + noteRate, 1 / 12);
      bills *= Math.pow(1 + billRate, 1 / 12);
      if (month === 24) {
        // The 2-year notes mature and join the bill ladder, which is the
        // moment the locked portion of the parking plan re-prices.
        bills += notes;
        notes = 0;
      }
      if (month === 12) {
        const parked = notes + bills;
        lockedShare = parked > 0 ? notes / parked : 0;
        repricingShare = parked > 0 ? bills / parked : 0;
      }
      if (month <= stagingMonths) {
        const scheduledPurchase = starting / stagingMonths;
        let purchase = Math.min(scheduledPurchase, notes + bills);
        const fromBills = Math.min(bills, purchase);
        bills -= fromBills;
        const fromNotes = Math.min(notes, purchase - fromBills);
        notes -= fromNotes;
        purchase = fromBills + fromNotes;
        phasedShares += purchase / Math.max(indexAt(month), 0.000001);
        if (month === stagingMonths) {
          phasedShares += (notes + bills) / Math.max(indexAt(month), 0.000001);
          notes = 0;
          bills = 0;
        }
      }
      const index = indexAt(month);
      const immediateValue = immediateShares * index;
      const phasedValue = phasedShares * index + notes + bills;
      immediatePeak = Math.max(immediatePeak, immediateValue);
      phasedPeak = Math.max(phasedPeak, phasedValue);
      immediateWorst = Math.min(immediateWorst, immediateValue / immediatePeak - 1);
      phasedWorst = Math.min(phasedWorst, phasedValue / phasedPeak - 1);
    }
    const finalIndex = indexAt(horizon);
    return {
      months: horizon,
      immediate: immediateShares * finalIndex,
      phased: phasedShares * finalIndex + notes + bills,
      immediateDrawdown: immediateWorst * 100,
      phasedDrawdown: phasedWorst * 100,
      lockedShare,
      repricingShare,
    };
  }

  function displayScenario(prefix, result, inflation, reinvestCost, yieldDrop) {
    const inflationFactor = Math.pow(1 + inflation / 100, result.months / 12);
    element(`${prefix}-immediate-value`).textContent = units(result.immediate);
    element(`${prefix}-phased-value`).textContent = units(result.phased);
    element(`${prefix}-immediate-real`).textContent = units(result.immediate / inflationFactor);
    element(`${prefix}-phased-real`).textContent = units(result.phased / inflationFactor);
    element(`${prefix}-immediate-dd`).textContent = pct(result.immediateDrawdown);
    element(`${prefix}-phased-dd`).textContent = pct(result.phasedDrawdown);
    element(`${prefix}-months`).textContent = `${result.months} months`;
    const difference = result.phased - result.immediate;
    const direction = Math.abs(difference) < 0.01
      ? 'is nearly even with'
      : difference > 0 ? 'ends above' : 'ends below';
    element(`${prefix}-headline`).textContent = `Phasing ${direction} immediate investment by ${units(Math.abs(difference))}`;
    element(`${prefix}-lock`).textContent = `${(result.lockedShare * 100).toFixed(0)}% locked in 2-year notes to month 24`;
    element(`${prefix}-reinvestment`).textContent = `${(result.repricingShare * 100).toFixed(0)}% of the reserve re-prices quarterly from month 13`;
    const dropText = yieldDrop.toFixed(2);
    element(`${prefix}-reinvest-cost`).textContent = reinvestCost >= 0
      ? `${units(reinvestCost)} lost if renewal yields fall ${dropText} points`
      : `${units(Math.abs(reinvestCost))} gained if renewal yields fall ${dropText} points`;
  }

  function simulate() {
    const stagingMonths = numeric('phase-months', 30, 1, 120);
    const drawdown = numeric('phase-drawdown', 57, 0, 99) / 100;
    const troughMonths = numeric('phase-trough', 17, 1, 120);
    const drift = numeric('phase-drift', 0, -20, 30) / 100;
    const firstYield = numeric('phase-yield1', 0, -5, 20);
    const renewalYield = numeric('phase-yield2', 0, -5, 20);
    const inflation = numeric('phase-inflation', 0, -5, 20);
    const noteShare = numeric('phase-noteshare', 50, 0, 100);
    const yieldDrop = numeric('phase-yielddrop', 1, -5, 5);
    const earlyStart = Math.max(0, Math.floor(stagingMonths / 2));
    const lateStart = stagingMonths;
    const early = simulateScenario(earlyStart, stagingMonths, drawdown, troughMonths, drift, firstYield, renewalYield, noteShare, 0);
    const late = simulateScenario(lateStart, stagingMonths, drawdown, troughMonths, drift, firstYield, renewalYield, noteShare, 0);
    const earlyStress = simulateScenario(earlyStart, stagingMonths, drawdown, troughMonths, drift, firstYield, renewalYield, noteShare, yieldDrop);
    const lateStress = simulateScenario(lateStart, stagingMonths, drawdown, troughMonths, drift, firstYield, renewalYield, noteShare, yieldDrop);
    displayScenario('early', early, inflation, early.phased - earlyStress.phased, yieldDrop);
    displayScenario('late', late, inflation, late.phased - lateStress.phased, yieldDrop);

    const status = element('phase-status');
    const earlyDiff = early.phased - early.immediate;
    const lateDiff = late.phased - late.immediate;
    const earlyResult = Math.abs(earlyDiff) < 0.01 ? 'is nearly even with' : earlyDiff > 0 ? 'ends above' : 'ends below';
    const lateResult = Math.abs(lateDiff) < 0.01 ? 'is nearly even with' : lateDiff > 0 ? 'ends above' : 'ends below';
    status.textContent = `At the modeled early-crash trough, phasing ${earlyResult} immediate investment; after the parking window, phasing ${lateResult} immediate investment. Read each headline together with the reinvestment line beside it: ${(early.repricingShare * 100).toFixed(0)}% of the reserve re-prices quarterly and ${(early.lockedShare * 100).toFixed(0)}% stays locked in 2-year notes to month 24. These are assumption-driven scenarios, not forecasts or probabilities.`;
  }

  element('phase-event')?.addEventListener('change', () => {
    if (element('phase-event').value === '1929') {
      element('phase-drawdown').value = '89';
      element('phase-trough').value = '36';
    } else {
      element('phase-drawdown').value = '57';
      element('phase-trough').value = '17';
    }
    simulate();
  });
  phaseForm.querySelectorAll('input, select').forEach(control => {
    control.addEventListener('input', simulate);
    control.addEventListener('change', simulate);
  });
  element('phase-reset')?.addEventListener('click', () => {
    element('phase-event').value = '2008';
    element('phase-months').value = '30';
    element('phase-noteshare').value = '50';
    element('phase-drawdown').value = '57';
    element('phase-trough').value = '17';
    element('phase-drift').value = '0';
    element('phase-yield1').value = '0';
    element('phase-yield2').value = '0';
    element('phase-yielddrop').value = '1';
    element('phase-inflation').value = '0';
    simulate();
  });
  simulate();
}
