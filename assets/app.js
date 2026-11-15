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

  function simulateScenario(crashStart, stagingMonths, drawdown, troughMonths, drift, firstYield, renewalYield) {
    const starting = 100;
    const horizon = Math.max(stagingMonths, crashStart + troughMonths);
    const peakAtCrash = Math.pow(1 + drift, crashStart / 12);
    const indexAt = month => {
      if (month < crashStart) return Math.pow(1 + drift, month / 12);
      const elapsed = Math.min(1, Math.max(0, (month - crashStart) / troughMonths));
      return peakAtCrash * (1 - drawdown * elapsed);
    };

    let reserve = starting;
    let phasedShares = 0;
    const immediateShares = starting;
    let immediatePeak = starting;
    let phasedPeak = starting;
    let immediateWorst = 0;
    let phasedWorst = 0;

    for (let month = 1; month <= horizon; month += 1) {
      if (month <= stagingMonths) {
        const annualYield = (month <= 12 ? firstYield : renewalYield) / 100;
        reserve *= Math.pow(1 + annualYield, 1 / 12);
        const scheduledPurchase = starting / stagingMonths;
        const purchase = Math.min(scheduledPurchase, reserve);
        phasedShares += purchase / Math.max(indexAt(month), 0.000001);
        reserve -= purchase;
        if (month === stagingMonths && reserve > 0) {
          phasedShares += reserve / Math.max(indexAt(month), 0.000001);
          reserve = 0;
        }
      }
      const index = indexAt(month);
      const immediateValue = immediateShares * index;
      const phasedValue = phasedShares * index + reserve;
      immediatePeak = Math.max(immediatePeak, immediateValue);
      phasedPeak = Math.max(phasedPeak, phasedValue);
      immediateWorst = Math.min(immediateWorst, immediateValue / immediatePeak - 1);
      phasedWorst = Math.min(phasedWorst, phasedValue / phasedPeak - 1);
    }
    const finalIndex = indexAt(horizon);
    return {
      months: horizon,
      immediate: immediateShares * finalIndex,
      phased: phasedShares * finalIndex + reserve,
      immediateDrawdown: immediateWorst * 100,
      phasedDrawdown: phasedWorst * 100,
    };
  }

  function displayScenario(prefix, result, inflation) {
    const inflationFactor = Math.pow(1 + inflation / 100, result.months / 12);
    element(`${prefix}-immediate-value`).textContent = units(result.immediate);
    element(`${prefix}-phased-value`).textContent = units(result.phased);
    element(`${prefix}-immediate-real`).textContent = units(result.immediate / inflationFactor);
    element(`${prefix}-phased-real`).textContent = units(result.phased / inflationFactor);
    element(`${prefix}-immediate-dd`).textContent = pct(result.immediateDrawdown);
    element(`${prefix}-phased-dd`).textContent = pct(result.phasedDrawdown);
    element(`${prefix}-months`).textContent = `${result.months} months`;
  }

  function simulate() {
    const stagingMonths = numeric('phase-months', 30, 1, 120);
    const drawdown = numeric('phase-drawdown', 57, 0, 99) / 100;
    const troughMonths = numeric('phase-trough', 17, 1, 120);
    const drift = numeric('phase-drift', 0, -20, 30) / 100;
    const firstYield = numeric('phase-yield1', 0, -5, 20);
    const renewalYield = numeric('phase-yield2', 0, -5, 20);
    const inflation = numeric('phase-inflation', 0, -5, 20);
    const earlyStart = Math.max(0, Math.floor(stagingMonths / 2));
    const lateStart = stagingMonths;
    const early = simulateScenario(earlyStart, stagingMonths, drawdown, troughMonths, drift, firstYield, renewalYield);
    const late = simulateScenario(lateStart, stagingMonths, drawdown, troughMonths, drift, firstYield, renewalYield);
    displayScenario('early', early, inflation);
    displayScenario('late', late, inflation);

    const status = element('phase-status');
    const earlyDiff = early.phased - early.immediate;
    const lateDiff = late.phased - late.immediate;
    const earlyResult = Math.abs(earlyDiff) < 0.01 ? 'is nearly even with' : earlyDiff > 0 ? 'ends above' : 'ends below';
    const lateResult = Math.abs(lateDiff) < 0.01 ? 'is nearly even with' : lateDiff > 0 ? 'ends above' : 'ends below';
    status.textContent = `At the modeled early-crash trough, phasing ${earlyResult} immediate investment; after staging, phasing ${lateResult} immediate investment. These are assumption-driven scenarios, not forecasts or probabilities. See the stated model limits.`;
  }

  // Ladder reinvestment risk: split the reserve across term slots and reprice
  // each slot at a different renewal yield so the user can see how a falling
  // short-rate path changes the staged reserve before it is spent.
  function ladderScenario(stagingMonths, drawdown, troughMonths, drift, yield1, yieldPath) {
    const starting = 100;
    const horizon = Math.max(stagingMonths, troughMonths);
    const peakAtCrash = 1;
    const indexAt = month => {
      const elapsed = Math.min(1, Math.max(0, month / troughMonths));
      return peakAtCrash * (1 - drawdown * elapsed);
    };
    const slots = 4; // 3-, 6-, 12- and 24-month style rungs, normalized
    let reserve = starting;
    let shares = 0;
    let interest = 0;
    const monthlyRate = (annual, month) => {
      const slot = Math.min(slots - 1, Math.floor(((month - 1) * slots) / Math.max(stagingMonths, 1)));
      return Math.pow(1 + yieldPath[slot] / 100, 1 / 12);
    };
    for (let month = 1; month <= stagingMonths; month += 1) {
      const growth = monthlyRate(month <= 12 ? yield1 : yieldPath[0], month);
      const earned = reserve * (growth - 1);
      interest += earned;
      reserve += earned;
      const purchase = starting / stagingMonths;
      shares += purchase / Math.max(indexAt(month), 0.000001);
      reserve -= purchase;
    }
    if (reserve > 0) { shares += reserve / Math.max(indexAt(stagingMonths), 0.000001); reserve = 0; }
    return { interest, finalIndex: indexAt(horizon), shares, months: horizon };
  }

  function displayLadder(prefix, result, inflation) {
    const inflationFactor = Math.pow(1 + inflation / 100, result.months / 12);
    element(`${prefix}-interest`).textContent = units(result.interest);
    element(`${prefix}-value`).textContent = units(result.shares * result.finalIndex);
    element(`${prefix}-real`).textContent = units((result.shares * result.finalIndex) / inflationFactor);
  }

  function simulateLadder() {
    const stagingMonths = numeric('ladder-months', 30, 6, 60);
    const drawdown = numeric('ladder-drawdown', 57, 0, 99) / 100;
    const troughMonths = numeric('ladder-trough', 17, 1, 120);
    const drift = numeric('ladder-drift', 0, -20, 30) / 100;
    const yield1 = numeric('ladder-yield1', 0, -5, 20);
    const renewal1 = numeric('ladder-renewal1', 0, -5, 20);
    const renewal2 = numeric('ladder-renewal2', 0, -5, 20);
    const renewal3 = numeric('ladder-renewal3', 0, -5, 20);
    const inflation = numeric('ladder-inflation', 0, -5, 20);
    const flat = ladderScenario(stagingMonths, drawdown, troughMonths, drift, yield1, [yield1, yield1, yield1, yield1]);
    const falling = ladderScenario(stagingMonths, drawdown, troughMonths, drift, yield1, [renewal1, renewal2, renewal3, renewal3]);
    element('ladder-flat-year').textContent = '0.00 units (baseline)';
    element('ladder-falling-year').textContent = units(Math.max(0, flat.interest - falling.interest));
    displayLadder('ladder-flat', flat, inflation);
    displayLadder('ladder-falling', falling, inflation);
    const status = element('ladder-status');
    if (status) {
      const gap = flat.interest - falling.interest;
      status.textContent = gap > 0.005
        ? `Repricing the later rungs at lower yields removes ${units(gap)} of accrued reserve interest over ${stagingMonths} months before the crash outcome is applied. This is reinvestment risk, not a forecast of yields.`
        : 'The renewal path is not below the first-year yield, so this run shows no reinvestment penalty. Lower a renewal yield to isolate the effect.';
    }
  }

  if (document.getElementById('ladder-tool')) {
    document.getElementById('ladder-tool').querySelectorAll('input, select').forEach(control => {
      control.addEventListener('input', simulateLadder);
      control.addEventListener('change', simulateLadder);
    });
    element('ladder-reset')?.addEventListener('click', () => {
      element('ladder-months').value = '30';
      element('ladder-drawdown').value = '57';
      element('ladder-trough').value = '17';
      element('ladder-drift').value = '0';
      element('ladder-yield1').value = '4.0';
      element('ladder-renewal1').value = '3.0';
      element('ladder-renewal2').value = '2.5';
      element('ladder-renewal3').value = '2.0';
      element('ladder-inflation').value = '2.5';
      simulateLadder();
    });
    simulateLadder();
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
    element('phase-drawdown').value = '57';
    element('phase-trough').value = '17';
    element('phase-drift').value = '0';
    element('phase-yield1').value = '0';
    element('phase-yield2').value = '0';
    element('phase-inflation').value = '0';
    simulate();
  });
  simulate();
}

/* Working-figure projection controls. Uses the pure engine in
   assets/projection-engine.js so the browser and Python implementations can be
   kept in step by tools/engine_check.cjs. */
(function wireProjectionTool() {
  const engine = window.ProjectionEngine;
  const form = document.getElementById('projection-tool');
  const payloadNode = document.getElementById('runtime-payload');
  if (!engine || !form || !payloadNode) return;

  let data;
  try {
    data = JSON.parse(payloadNode.dataset.payload);
  } catch (error) {
    return;
  }
  if (!data || !data.a) return;

  const fields = [
    ['transfer_year', v => String(v)],
    ['a_appreciation', v => v.toFixed(1) + '% a year'],
    ['b_appreciation', v => v.toFixed(1) + '% a year'],
    ['inflation', v => v.toFixed(1) + '% a year'],
    ['assessed_growth', v => v.toFixed(1) + '% a year'],
    ['prop19_growth', v => v.toFixed(1) + '% a year'],
    ['insurance_growth', v => v.toFixed(1) + '% a year'],
    ['rent_growth', v => v.toFixed(1) + '% a year'],
    ['maintenance_a', v => v.toFixed(1) + '% of value a year'],
    ['maintenance_b', v => v.toFixed(1) + '% of value a year'],
    ['selling_cost', v => v.toFixed(1) + '% of price'],
    ['equity_return', v => v.toFixed(1) + '% a year'],
    ['treasury_yield', v => v.toFixed(1) + '% a year'],
    ['staging_months', v => String(v) + ' months'],
    ['horizon_years', v => String(v) + ' years']
  ];

  const defaults = {};
  fields.forEach(([id]) => {
    const node = document.getElementById(id);
    if (node) defaults[id] = node.value;
  });

  const value = (id, fallback) => {
    const node = document.getElementById(id);
    if (!node) return fallback;
    const parsed = Number(node.value);
    return Number.isFinite(parsed) ? parsed : fallback;
  };

  const readInputs = () => ({
    transferYear: value('transfer_year', 2045),
    aApp: value('a_appreciation', 3.5) / 100,
    bApp: value('b_appreciation', 3.0) / 100,
    inflation: value('inflation', 2.5) / 100,
    assessedGrowth: value('assessed_growth', 2.0) / 100,
    prop19Growth: value('prop19_growth', 2.0) / 100,
    insuranceGrowth: value('insurance_growth', 3.0) / 100,
    rentGrowth: value('rent_growth', 3.0) / 100,
    maintenanceA: value('maintenance_a', 0.5) / 100,
    maintenanceB: value('maintenance_b', 1.0) / 100,
    sellingCost: value('selling_cost', 6.0) / 100,
    equityReturn: value('equity_return', 6.0) / 100,
    treasuryYield: value('treasury_yield', 3.6) / 100,
    stagingMonths: value('staging_months', 30),
    horizonYears: value('horizon_years', 20)
  });

  const tableByCaption = prefix =>
    [...document.querySelectorAll('table')].find(
      table => table.querySelector('caption') &&
        table.querySelector('caption').textContent.trim().startsWith(prefix)
    );

  function recalculate() {
    fields.forEach(([id, format]) => {
      const node = document.getElementById(id);
      const out = document.getElementById(id + '-out');
      if (node && out) out.textContent = format(Number(node.value));
    });

    const inputs = readInputs();
    const model = engine.projectionModel(data, inputs);

    const tableA = tableByCaption('Property A — value');
    if (tableA) {
      [...tableA.querySelectorAll('tbody tr')].forEach(row => {
        const year = Number(row.children[0].textContent.trim());
        if (!Number.isFinite(year)) return;
        const fmv = model.marketA(year);
        const base = model.assessedA(year);
        const occ = model.taxable(fmv, base, model.limit(year));
        row.children[1].textContent = engine.moneyWhole(fmv);
        row.children[2].textContent = engine.moneyWhole(base);
        row.children[3].textContent =
          year <= inputs.transferYear
            ? engine.moneyWhole(model.tax(base, data.effectiveRateA, true))
            : 'transferred';
        row.children[4].textContent = engine.moneyWhole(model.tax(occ, data.effectiveRateA, true));
        row.children[5].textContent = engine.moneyWhole(model.tax(fmv, data.effectiveRateA, false));
      });
    }

    const tableB = tableByCaption('Property B — value');
    if (tableB) {
      [...tableB.querySelectorAll('tbody tr')].forEach(row => {
        const year = Number(row.children[0].textContent.trim());
        if (!Number.isFinite(year)) return;
        const assessed = model.assessedB(year);
        row.children[1].textContent = engine.moneyWhole(model.marketB(year));
        row.children[2].textContent = engine.moneyWhole(assessed);
        row.children[3].textContent = engine.moneyWhole(model.tax(assessed, data.effectiveRateB, false));
        row.children[4].textContent = engine.moneyWhole(model.rentB(year));
        row.children[5].textContent = engine.moneyWhole(model.opB(year));
      });
    }

    const status = document.getElementById('projection-status');
    if (status) {
      const transfer = inputs.transferYear;
      const fmv = model.marketA(transfer);
      const base = model.assessedA(transfer);
      const occ = model.taxable(fmv, base, model.limit(transfer));
      const occupied = model.tax(occ, data.effectiveRateA, true);
      const rented = model.tax(fmv, data.effectiveRateA, false);
      const today = model.tax(model.assessedA(data.baseYear), data.effectiveRateA, true);
      status.textContent =
        `At a ${transfer} transfer: value ${engine.moneyWhole(fmv)}, assessment ${engine.moneyWhole(base)}, ` +
        `property tax about ${engine.moneyWhole(occupied)} a year if occupied or ${engine.moneyWhole(rented)} ` +
        `if rented, against about ${engine.moneyWhole(today)} today. Rounded to ten dollars, computed in this browser.`;
    }
  }

  form.addEventListener('input', recalculate);
  document.getElementById('projection-reset')?.addEventListener('click', () => {
    Object.keys(defaults).forEach(id => {
      const node = document.getElementById(id);
      if (node) node.value = defaults[id];
    });
    recalculate();
  });
  recalculate();
})();
