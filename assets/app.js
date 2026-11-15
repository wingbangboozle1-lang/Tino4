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
  const dollars = value => `$${(Math.round(value / 10) * 10).toLocaleString('en-US')}`;

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

  function displayScenario(prefix, result, inflation, proceeds) {
    const inflationFactor = Math.pow(1 + inflation / 100, result.months / 12);
    element(`${prefix}-immediate-value`).textContent = units(result.immediate);
    element(`${prefix}-phased-value`).textContent = units(result.phased);
    const scale = proceeds / 100;
    const immediateDollars = element(`${prefix}-immediate-dollars`);
    const phasedDollars = element(`${prefix}-phased-dollars`);
    if (immediateDollars) immediateDollars.textContent = dollars(result.immediate * scale);
    if (phasedDollars) phasedDollars.textContent = dollars(result.phased * scale);
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
    const proceeds = numeric('phase-proceeds', 2945000, 100000, 20000000);
    const earlyStart = Math.max(0, Math.floor(stagingMonths / 2));
    const lateStart = stagingMonths;
    const early = simulateScenario(earlyStart, stagingMonths, drawdown, troughMonths, drift, firstYield, renewalYield);
    const late = simulateScenario(lateStart, stagingMonths, drawdown, troughMonths, drift, firstYield, renewalYield);
    displayScenario('early', early, inflation, proceeds);
    displayScenario('late', late, inflation, proceeds);

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
      element('phase-trough').value = '34';
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
    element('phase-proceeds').value = '2945000';
    simulate();
  });
  simulate();
}

// Local-only path what-if tool (decision-analysis page). Defaults mirror the
// published baseline assumptions; nothing is stored or transmitted and no
// network API is used.
const pathForm = document.getElementById('path-tool');
if (pathForm) {
  const pathEl = id => document.getElementById(id);
  const pathNum = (id, min, max) => {
    const raw = Number(pathEl(id)?.value);
    const value = Number.isFinite(raw) ? raw : min;
    return Math.max(min, Math.min(value, max));
  };
  const pathMoney = value => {
    const rounded = Math.round(value / 10) * 10;
    const sign = rounded < 0 ? '-' : '';
    return sign + '$' + Math.abs(rounded).toLocaleString('en-US');
  };

  function runPathTool() {
    const marketValue = pathNum('path-value', 0, 99999999);
    const carriedBase = pathNum('path-base', 0, 99999999);
    const rate = pathNum('path-rate', 0, 5) / 100;
    const cap = pathNum('path-cap', 0, 10) / 100;
    const exclusion = pathNum('path-excl', 0, 99999999);
    const load = pathNum('path-load', 0, 90) / 100;

    const exclTax1 = carriedBase * rate;
    const reassessedBase = Math.max(marketValue - exclusion, 0);
    const reTax1 = reassessedBase * rate;
    const cum = base => {
      let total = 0;
      for (let year = 0; year < 10; year += 1) total += base * Math.pow(1 + cap, year);
      return total;
    };
    const exclCum = cum(exclTax1);
    const reCum = cum(reTax1);
    const delta1 = reTax1 - exclTax1;
    const delta10 = reCum - exclCum;
    const hurdle = load < 1 ? (delta10 / 10) / 12 / (1 - load) : NaN;

    // Transfer-cost and income-tax layers (T9806-5). Rate inputs mirror the
    // published schedules; every derived figure stays rounded on screen.
    const dttPer500 = pathNum('path-dtt', 0, 50);
    const otherFees = pathNum('path-fees', 0, 99_99_99);
    const imputedMonthly = pathNum('path-imputed', 0, 9_999, 3550);
    const gainPct = pathNum('path-gainpct', 0, 100) / 100;
    const caRate = pathNum('path-ca', 0, 20) / 100;
    const depreciation = pathNum('path-depr', 0, 99_99_999);
    const principal = Boolean(pathEl('path-principal')?.checked);

    const transferTax = marketValue > 100 ? Math.ceil(marketValue / 500) * dttPer500 : 0;
    const commissions = marketValue * 0.07;
    const netProceeds = marketValue - commissions - transferTax - otherFees;
    const rawGain = marketValue * gainPct;
    const gain = principal ? Math.max(0, rawGain - 250_000) : rawGain;
    const recaptured = Math.min(depreciation, gain);
    const residual = Math.max(0, gain - recaptured);
    const taxDue = recaptured * 0.25
      + residual * 0.238
      + gain * caRate
      + Math.max(0, gain - 1_000_000) * 0.01;
    const afterTax = netProceeds - taxDue;
    const sell10 = afterTax * Math.pow(1.06, 10);
    // A living path earns no rent but avoids housing cost: the imputed-rent
    // line values the occupied unit, so the two branches can be compared.
    const livingBenefit10 = imputedMonthly * 12 * 10 - exclCum;

    pathEl('path-tax-excl').textContent = pathMoney(exclTax1);
    pathEl('path-tax-excl10').textContent = pathMoney(exclTax1 * Math.pow(1 + cap, 9));
    pathEl('path-tax-exclcum').textContent = pathMoney(exclCum);
    pathEl('path-tax-re').textContent = pathMoney(reTax1);
    pathEl('path-tax-re10').textContent = pathMoney(reTax1 * Math.pow(1 + cap, 9));
    pathEl('path-tax-recum').textContent = pathMoney(reCum);
    pathEl('path-delta1').textContent = pathMoney(delta1);
    pathEl('path-delta10').textContent = pathMoney(delta10);
    pathEl('path-hurdle').textContent = Number.isFinite(hurdle) ? pathMoney(hurdle) + ' / month' : '—';
    if (pathEl('path-transfer-tax')) pathEl('path-transfer-tax').textContent = pathMoney(transferTax);
    if (pathEl('path-closing')) pathEl('path-closing').textContent = pathMoney(commissions + otherFees);
    if (pathEl('path-net')) pathEl('path-net').textContent = pathMoney(netProceeds);
    if (pathEl('path-gain')) pathEl('path-gain').textContent = gain > 0 ? pathMoney(gain) : 'nil';
    if (pathEl('path-recap')) pathEl('path-recap').textContent = recaptured > 0 ? pathMoney(recaptured * 0.25) + ' on ' + pathMoney(recaptured) : 'nil';
    if (pathEl('path-taxes')) pathEl('path-taxes').textContent = taxDue > 0 ? pathMoney(taxDue) : 'nil';
    if (pathEl('path-aftertax')) pathEl('path-aftertax').textContent = pathMoney(afterTax);
    if (pathEl('path-imputed10')) pathEl('path-imputed10').textContent = pathMoney(livingBenefit10);
    pathEl('path-sellnet').textContent = pathMoney(afterTax);
    pathEl('path-sell10').textContent = pathMoney(sell10);
    pathEl('path-status').textContent = 'Local scenario recomputed. Reassessed branch is ' +
      (delta10 > 0 ? 'more expensive' : 'less expensive') +
      ' over ten years under these assumptions, and the sell branch nets ' + pathMoney(afterTax) +
      ' after the transfer tax, fees and this gain sensitivity. Assumptions are labeled on the page; this is not tax advice.';
  }

  pathForm.querySelectorAll('input').forEach(control => {
    control.addEventListener('input', runPathTool);
    control.addEventListener('change', runPathTool);
  });
  pathEl('path-reset')?.addEventListener('click', () => {
    pathEl('path-value').value = '6531230';
    pathEl('path-base').value = '802030';
    pathEl('path-rate').value = '1.34';
    pathEl('path-cap').value = '2';
    pathEl('path-excl').value = '1886640';
    pathEl('path-load').value = '35';
    pathEl('path-imputed').value = '3550';
    pathEl('path-dtt').value = '0.55';
    pathEl('path-fees').value = '190';
    pathEl('path-gainpct').value = '0';
    pathEl('path-ca').value = '12.3';
    pathEl('path-depr').value = '0';
    if (pathEl('path-principal')) pathEl('path-principal').checked = false;
    runPathTool();
  });
  runPathTool();
}

// Local-only Proposition H parcel-charge estimator (rental-economics page).
const propHForm = document.getElementById('prop-h-tool');
if (propHForm) {
  const phEl = id => document.getElementById(id);
  const phNum = (id, min, max, fallback) => {
    const raw = Number(phEl(id)?.value);
    const value = Number.isFinite(raw) ? raw : fallback;
    return Math.max(min, Math.min(value, max));
  };
  const phMoney = value => {
    const rounded = Math.round(value / 10) * 10;
    return (rounded < 0 ? '-' : '') + '$' + Math.abs(rounded).toLocaleString('en-US');
  };
  const SUNSET_YEAR = 2042;
  const PASS_THROUGH = 65;

  function runPropH() {
    const base = phNum('ph-class', 0, 9_999, 249);
    const year = Math.round(phNum('ph-year', 2024, SUNSET_YEAR, 2027));
    const inflation = phNum('ph-infl', 0, 10, 2) / 100;
    const units = phNum('ph-units', 0, 9, 0);
    const chargeFor = y => (y < 2027 || y > SUNSET_YEAR ? 0 : base * Math.pow(1 + inflation, y - 2027));
    let cumulative = 0;
    let lifetime = 0;
    for (let y = 2027; y <= SUNSET_YEAR; y += 1) {
      lifetime += chargeFor(y);
      if (y <= year) cumulative += chargeFor(y);
    }
    const passThrough = units * PASS_THROUGH;
    const charge = chargeFor(year);
    phEl('ph-charge').textContent = charge > 0 ? phMoney(charge) : 'no charge in this year';
    phEl('ph-cum').textContent = phMoney(cumulative);
    phEl('ph-life').textContent = phMoney(lifetime);
    phEl('ph-pass').textContent = phMoney(passThrough);
    phEl('ph-net').textContent = phMoney(Math.max(0, charge - passThrough));
    phEl('ph-status').textContent = 'Fiscal year ' + year + '-' + String(year + 1).slice(2) +
      ': modeled charge ' + phMoney(charge) + ', owner-borne after the pass-through ceiling ' +
      phMoney(Math.max(0, charge - passThrough)) + '. The tax ends June 30, ' + SUNSET_YEAR +
      '; eligibility for an exemption or credit is an owner application, not a model output.';
  }

  propHForm.querySelectorAll('input, select').forEach(control => {
    control.addEventListener('input', runPropH);
    control.addEventListener('change', runPropH);
  });
  phEl('ph-reset')?.addEventListener('click', () => {
    phEl('ph-class').value = '249';
    phEl('ph-year').value = '2027';
    phEl('ph-infl').value = '2';
    phEl('ph-units').value = '2';
    runPropH();
  });
  runPropH();
}
