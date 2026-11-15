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

// ---------------------------------------------------------------------------
// Decision what-if tool (local-only; mirrors tools/sitebuild.py constants).
// Nothing is stored, transmitted, or read from a network.
const decisionForm = document.getElementById('decision-tool');
if (decisionForm) {
  const A_VALUE = 3100000, A_BASE_2026 = 550540, CAP_2025 = 1044586;
  const CAP_GROWTH = 0.022, INFLATION = 0.025, RENT_GROWTH = 0.03;
  const INS_GROWTH = 0.04, UTIL_GROWTH = 0.03, MAINT_A = 0.009, VAC_MGMT = 0.08;
  const UTIL_A_2026 = 1320; // (125 - 15) * 12, owner range midpoints
  const element = id => document.getElementById(id);
  const numeric = (id, fallback, min, max) => {
    const raw = Number(element(id)?.value);
    const value = Number.isFinite(raw) ? raw : fallback;
    return Math.max(min, Math.min(value, max));
  };
  const money = x => '$' + (Math.round(x / 10) * 10).toLocaleString('en-US');
  const money0 = x => (x < 0 ? '-' : '') + '$' + Math.abs(Math.round(x / 10) * 10).toLocaleString('en-US');

  function recompute() {
    const year = Math.round(numeric('d-year', 2045, 2040, 2050));
    const g = numeric('d-growth', 4.5, 2, 7) / 100;
    const levy = numeric('d-levy', 1.17, 1, 1.4) / 100;
    const ret = numeric('d-return', 6.5, 3, 9) / 100;
    const rent = numeric('d-rent', 7000, 5000, 9000);
    const ins = numeric('d-ins', 1500, 1000, 6000);
    const n = year - 2026;
    const fmv = A_VALUE * Math.pow(1 + g, n);
    const base = A_BASE_2026 * Math.pow(1.02, n);
    const cap = CAP_2025 * Math.pow(1 + CAP_GROWTH, year - 2025);
    const direct = (7210 - A_BASE_2026 * levy) * Math.pow(1 + INFLATION, n);
    const newBase = Math.max(base, base + Math.min(cap, fmv - base));
    const taxOcc = newBase * levy + direct;
    const taxRe = fmv * levy + direct;
    const gross = rent * 12 * Math.pow(1 + RENT_GROWTH, n);
    const costs = taxRe + ins * Math.pow(1 + INS_GROWTH, n) + MAINT_A * fmv
      + UTIL_A_2026 * Math.pow(1 + UTIL_GROWTH, n) + VAC_MGMT * gross;
    const rentNet = gross - costs;
    const portfolio = fmv * 0.94 * Math.pow(1 + ret, 2075 - year);
    element('d-out-fmv').textContent = money(fmv);
    element('d-out-base').textContent = money(base);
    element('d-out-newbase').textContent = money(newBase);
    element('d-out-tax-occ').textContent = money(taxOcc) + ' / yr';
    element('d-out-tax-re').textContent = money(taxRe) + ' / yr';
    element('d-out-rentnet').textContent = money0(rentNet) + ' / yr';
    element('d-out-portfolio').textContent = money(portfolio) + ' at 2075';
  }
  decisionForm.querySelectorAll('input').forEach(control => {
    control.addEventListener('input', recompute);
    control.addEventListener('change', recompute);
  });
  element('d-reset')?.addEventListener('click', () => {
    element('d-year').value = '2045';
    element('d-growth').value = '4.5';
    element('d-levy').value = '1.17';
    element('d-return').value = '6.5';
    element('d-rent').value = '7000';
    element('d-ins').value = '1500';
    recompute();
  });
  recompute();
}

// Projection what-if tool (local-only, same constants).
const projectionForm = document.getElementById('projection-tool');
if (projectionForm) {
  const A_VALUE = 3100000, A_BASE_2026 = 550540, CAP_2025 = 1044586;
  const element = id => document.getElementById(id);
  const numeric = (id, fallback, min, max) => {
    const raw = Number(element(id)?.value);
    const value = Number.isFinite(raw) ? raw : fallback;
    return Math.max(min, Math.min(value, max));
  };
  const money = x => '$' + (Math.round(x / 10) * 10).toLocaleString('en-US');
  function recompute() {
    const year = Math.round(numeric('p-year', 2045, 2026, 2075));
    const g = numeric('p-growth', 4.5, 2, 7) / 100;
    const infl = numeric('p-infl', 2.5, 1, 5) / 100;
    const n = year - 2026;
    const fmv = A_VALUE * Math.pow(1 + g, n);
    const base = A_BASE_2026 * Math.pow(1.02, n);
    const cap = CAP_2025 * Math.pow(1.022, year - 2025);
    const direct = (7210 - A_BASE_2026 * 0.0117) * Math.pow(1 + infl, n);
    const newBase = Math.max(base, base + Math.min(cap, fmv - base));
    element('p-out-fmv').textContent = money(fmv);
    element('p-out-base').textContent = money(base);
    element('p-out-taxocc').textContent = money(newBase * 0.0117 + direct) + ' / yr';
    element('p-out-taxre').textContent = money(fmv * 0.0117 + direct) + ' / yr';
  }
  projectionForm.querySelectorAll('input').forEach(control => {
    control.addEventListener('input', recompute);
    control.addEventListener('change', recompute);
  });
  element('p-reset')?.addEventListener('click', () => {
    element('p-year').value = '2045';
    element('p-growth').value = '4.5';
    element('p-infl').value = '2.5';
    recompute();
  });
  recompute();
}

// Black-swan stress tool: real annual S&P 500 total returns and average
// 3-month T-bill rates (NYU Stern compilation, 1928-2025), applied locally.
const SERIES = [[1928,43.81,3.08],[1929,-8.30,3.16],[1930,-25.12,4.55],[1931,-43.84,2.31],[1932,-8.64,1.07],[1933,49.98,0.96],[1934,-1.19,0.28],[1935,46.74,0.17],[1936,31.94,0.17],[1937,-35.34,0.28],[1938,29.28,0.07],[1939,-1.10,0.05],[1940,-10.67,0.04],[1941,-12.77,0.13],[1942,19.17,0.34],[1943,25.06,0.38],[1944,19.03,0.38],[1945,35.82,0.38],[1946,-8.43,0.38],[1947,5.20,0.60],[1948,5.70,1.05],[1949,18.30,1.12],[1950,30.81,1.20],[1951,23.68,1.52],[1952,18.15,1.72],[1953,-1.21,1.89],[1954,52.56,0.94],[1955,32.60,1.72],[1956,7.44,2.62],[1957,-10.46,3.22],[1958,43.72,1.77],[1959,12.06,3.39],[1960,0.34,2.87],[1961,26.64,2.35],[1962,-8.81,2.77],[1963,22.61,3.16],[1964,16.42,3.55],[1965,12.40,3.95],[1966,-9.97,4.86],[1967,23.80,4.29],[1968,10.81,5.34],[1969,-8.24,6.67],[1970,3.56,6.39],[1971,14.22,4.33],[1972,18.76,4.06],[1973,-14.31,7.04],[1974,-25.90,7.85],[1975,37.00,5.79],[1976,23.83,4.98],[1977,-6.98,5.26],[1978,6.51,7.18],[1979,18.52,10.05],[1980,31.74,11.39],[1981,-4.70,14.04],[1982,20.42,11.09],[1983,22.34,8.95],[1984,6.15,9.92],[1985,31.24,7.72],[1986,18.49,6.15],[1987,5.81,5.96],[1988,16.54,6.89],[1989,31.48,8.39],[1990,-3.06,7.75],[1991,30.23,5.54],[1992,7.49,3.51],[1993,9.97,3.07],[1994,1.33,4.37],[1995,37.20,5.66],[1996,22.68,5.15],[1997,33.10,5.20],[1998,28.34,4.91],[1999,20.89,4.78],[2000,-9.03,6.00],[2001,-11.85,3.48],[2002,-21.97,1.64],[2003,28.36,1.03],[2004,10.74,1.40],[2005,4.83,3.22],[2006,15.61,4.85],[2007,5.48,4.48],[2008,-36.55,1.40],[2009,25.94,0.15],[2010,14.82,0.14],[2011,2.10,0.05],[2012,15.89,0.09],[2013,32.15,0.06],[2014,13.52,0.03],[2015,1.38,0.05],[2016,11.77,0.32],[2017,21.61,0.95],[2018,-4.23,1.97],[2019,31.21,2.11],[2020,18.02,0.36],[2021,28.47,0.04],[2022,-18.04,2.09],[2023,26.06,5.28],[2024,24.88,5.18],[2025,17.78,4.21]];
const bsForm = document.getElementById('bs-tool');
if (bsForm) {
  const element = id => document.getElementById(id);
  const lookup = (year, col) => {
    const row = SERIES.find(item => item[0] === year);
    return row ? row[col] / 100 : 0;
  };
  const prod = (col, y0, y1) => {
    let out = 1;
    for (let y = Math.max(y0, 1928); y <= Math.min(y1, 2025); y += 1) out *= 1 + lookup(y, col);
    return out;
  };
  function run() {
    const entry = Number(element('bs-entry').value);
    const horizon = Math.max(3, Math.min(Number(element('bs-horizon').value) || 10, 30));
    const parkMonths = Math.max(0, Math.min(Number(element('bs-park').value) || 0, 60));
    const dcaMonths = Math.max(1, Math.min(Number(element('bs-dca').value) || 1, 60));
    const endYear = entry + horizon - 1;
    const lump = prod(1, entry, endYear);
    const parkYears = Math.floor(parkMonths / 12);
    const tranches = Math.max(1, Math.round(dcaMonths / 12));
    let parked = 0;
    for (let i = 0; i < tranches; i += 1) {
      const buyYear = entry + parkYears + i;
      const share = prod(2, entry, buyYear - 1) / tranches;
      parked += share * prod(1, buyYear, endYear);
    }
    const dcaImmediate = (() => {
      let total = 0;
      for (let i = 0; i < tranches; i += 1) {
        total += (1 / tranches) * prod(2, entry, entry + i - 1) * prod(1, entry + i, endYear);
      }
      return total;
    })();
    const fmt = x => x.toFixed(2) + 'x';
    element('bs-out-lump').textContent = fmt(lump);
    element('bs-out-parked').textContent = fmt(parked);
    element('bs-out-dca').textContent = fmt(dcaImmediate);
  }
  bsForm.querySelectorAll('input, select').forEach(control => {
    control.addEventListener('input', run);
    control.addEventListener('change', run);
  });
  element('bs-run')?.addEventListener('click', run);
  run();
}
