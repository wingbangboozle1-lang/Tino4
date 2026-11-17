/* Local-only multi-regime sensitivity model.
   Deterministic: identical inputs always produce identical outputs.
   No inputs are stored, persisted, or transmitted.

   The engine walks a user-selected sequence of economic regimes. Each regime
   states an annual inflation rate, an annual equity price return and an annual
   cash/Treasury yield. Regimes make growth and inflation uneven over long
   horizons instead of assuming one constant 50-year rate. Values are
   illustrative assumptions, not forecasts. */

(function (root) {
  'use strict';

  // Regime definitions: illustrative annual assumptions, editable in the UI.
  const REGIMES = {
    expansion: { label: 'Disinflationary expansion', inflationPct: 2.5, equityPct: 9, cashPct: 3.0 },
    boom: { label: 'Productivity boom', inflationPct: 3.0, equityPct: 15, cashPct: 4.0 },
    goldilocks: { label: 'Moderate growth', inflationPct: 2.0, equityPct: 7, cashPct: 2.5 },
    stagflation: { label: 'Stagflation', inflationPct: 7.0, equityPct: 2, cashPct: 6.5 },
    rateshock: { label: 'Inflation and rate shock', inflationPct: 5.0, equityPct: -3, cashPct: 5.0 },
    recession: { label: 'Recession and bear market', inflationPct: 1.0, equityPct: -25, cashPct: 4.0 },
    lostdecade: { label: 'Lost decade', inflationPct: 2.5, equityPct: 0, cashPct: 3.0 },
    deflation: { label: 'Debt deflation', inflationPct: -2.0, equityPct: -8, cashPct: 0.5 },
  };

  // Preset sequences. Blocks are listed in order and cycled when the horizon is
  // longer than the sequence. Anchors beside each preset are historical
  // observations from official sources, not predictions of order or timing.
  const PRESETS = {
    constant: {
      label: 'Constant-rate baseline (what most projections assume)',
      note: 'One growth and inflation rate for the whole horizon; shown for contrast only.',
      blocks: [{ years: 50, regime: 'expansion' }],
    },
    greatinflation: {
      label: '1970s-style stagflation, then disinflation',
      note: 'Anchored to the Federal Reserve History account of 1965-1982: inflation near 1 percent in 1964, above 14 percent in 1980, peaking near 15 percent in March 1980.',
      blocks: [
        { years: 6, regime: 'stagflation' },
        { years: 3, regime: 'rateshock' },
        { years: 6, regime: 'expansion' },
        { years: 10, regime: 'goldilocks' },
        { years: 25, regime: 'expansion' },
      ],
    },
    crash1929: {
      label: '1929-style crash, depression, very slow recovery',
      note: 'Anchored to Federal Reserve History: the Dow closed 89 percent below its September 1929 peak in July 1932 and did not regain the prior high until November 1954.',
      blocks: [
        { years: 1, regime: 'boom' },
        { years: 3, regime: 'deflation' },
        { years: 5, regime: 'recession' },
        { years: 6, regime: 'lostdecade' },
        { years: 10, regime: 'expansion' },
        { years: 25, regime: 'expansion' },
      ],
    },
    crash2008: {
      label: '2007-09-style crash, slow recovery, then expansion',
      note: 'Anchored to Federal Reserve History: the S&P 500 index fell 57 percent from its October 2007 peak to its March 2009 trough, and average home prices fell about 30 percent from mid-2006 to mid-2009.',
      blocks: [
        { years: 2, regime: 'recession' },
        { years: 3, regime: 'lostdecade' },
        { years: 5, regime: 'expansion' },
        { years: 5, regime: 'boom' },
        { years: 35, regime: 'expansion' },
      ],
    },
    lostdecade: {
      label: 'Lost decade first, then recovery',
      note: 'Flat real equity returns early, recovery later; tests a household that needs results early.',
      blocks: [
        { years: 10, regime: 'lostdecade' },
        { years: 5, regime: 'expansion' },
        { years: 5, regime: 'goldilocks' },
        { years: 30, regime: 'expansion' },
      ],
    },
    stopstart: {
      label: 'Stop-start: recurring shocks every decade',
      note: 'Tests repeated sequence risk rather than a single bad year.',
      blocks: [
        { years: 4, regime: 'expansion' },
        { years: 1, regime: 'recession' },
        { years: 5, regime: 'goldilocks' },
        { years: 2, regime: 'stagflation' },
      ],
    },
  };

  function blockList(presetKey, years) {
    const preset = PRESETS[presetKey];
    if (!preset) throw new RangeError('Unknown regime preset.');
    const blocks = [];
    let remaining = years;
    let index = 0;
    // Cycle through the preset sequence until the horizon is filled.
    while (remaining > 0) {
      const source = preset.blocks[index % preset.blocks.length];
      const span = Math.min(source.years, remaining);
      const regime = REGIMES[source.regime];
      if (!regime) throw new RangeError('Unknown regime in preset.');
      blocks.push({
        years: span,
        label: regime.label,
        inflationPct: regime.inflationPct,
        equityPct: regime.equityPct,
        cashPct: regime.cashPct,
      });
      remaining -= span;
      index += 1;
    }
    return blocks;
  }

  // Deterministic pseudo-random generator so the distribution is reproducible.
  function makeRandom(seed) {
    let state = (seed >>> 0) || 1;
    return function next() {
      state = (state * 1664525 + 1013904223) >>> 0;
      return state / 4294967296;
    };
  }

  // Approximately standard-normal draw from four uniform draws (Irwin-Hall).
  function normalDraw(random) {
    let total = 0;
    for (let i = 0; i < 4; i += 1) total += random();
    return ((total - 2) / Math.sqrt(1 / 3));
  }

  function validate(options) {
    const {
      amount, years, equityPct, cashYieldPct, volatilityPct,
      preset, shockPct, shockYear, stagingMonths, paths, seed,
    } = options;
    if (!Number.isFinite(amount) || amount <= 0) throw new RangeError('Enter a positive starting amount.');
    if (!Number.isInteger(years) || years < 5 || years > 50) throw new RangeError('Horizon must be a whole number of years from 5 to 50.');
    if (!Number.isFinite(equityPct) || equityPct < 0 || equityPct > 100) throw new RangeError('Equity share must be between 0 and 100 percent.');
    if (!Number.isFinite(cashYieldPct) || cashYieldPct < 0 || cashYieldPct > 25) throw new RangeError('Cash or Treasury yield must be between 0 and 25 percent.');
    if (!Number.isFinite(volatilityPct) || volatilityPct < 0 || volatilityPct > 60) throw new RangeError('Volatility must be between 0 and 60 percent.');
    if (!PRESETS[preset]) throw new RangeError('Choose a regime preset.');
    if (!Number.isFinite(shockPct) || shockPct < 0 || shockPct > 95) throw new RangeError('One-year shock must be between 0 and 95 percent.');
    if (!Number.isInteger(shockYear) || shockYear < 0 || shockYear > years) throw new RangeError('Shock year must be 0 (none) or a year from 1 to the horizon.');
    if (!Number.isInteger(stagingMonths) || stagingMonths < 0 || (stagingMonths !== 0 && (stagingMonths < 24 || stagingMonths > 36))) {
      throw new RangeError('Staging must be 0 months (invest immediately) or 24 to 36 months.');
    }
    if (!Number.isInteger(paths) || paths < 1 || paths > 500) throw new RangeError('Path count must be between 1 and 500.');
    if (!Number.isFinite(seed)) throw new RangeError('Seed must be numeric.');
  }

  function annualFactorsForYear(blocks, year) {
    let cursor = 0;
    for (let i = 0; i < blocks.length; i += 1) {
      cursor += blocks[i].years;
      if (year <= cursor) return blocks[i];
    }
    return blocks[blocks.length - 1];
  }

  // Single deterministic path (volatility = 0 for the path walk).
  function walkPath(options, blocks) {
    const {
      amount, years, equityPct, cashYieldPct, shockPct, shockYear, stagingMonths,
    } = options;
    const equityShare = equityPct / 100;
    const totalMonths = years * 12;
    const installments = stagingMonths === 0 ? 1 : stagingMonths;
    let reserve = amount;
    let equityUnits = 0;
    let index = 1;
    let deflator = 1;
    let peak = amount;
    let maxDrawdownPct = 0;
    let drawdownYear = 0;
    let yearsToRecover = null;
    const path = [];
    let recovered = stagingMonths === 0;

    for (let month = 1; month <= totalMonths; month += 1) {
      const year = Math.ceil(month / 12);
      const block = annualFactorsForYear(blocks, year);
      const cashMonthly = Math.pow(1 + cashYieldPct / 100, 1 / 12);
      let equityMonthly = Math.pow(1 + block.equityPct / 100, 1 / 12);
      if (shockYear > 0 && year === shockYear) {
        // Replace that year's equity return with the single-year shock.
        equityMonthly = Math.pow(1 - shockPct / 100, 1 / 12);
      }
      const inflationMonthly = Math.pow(1 + block.inflationPct / 100, 1 / 12);

      reserve *= cashMonthly;
      if (stagingMonths === 0) {
        if (month === 1) {
          equityUnits = amount / index;
          reserve = 0;
        }
      } else if (month <= stagingMonths) {
        const purchase = Math.min(reserve, amount / stagingMonths);
        reserve -= purchase;
        equityUnits += purchase / index;
      }

      index *= equityMonthly;
      deflator *= inflationMonthly;
      const nominal = equityUnits * index + reserve;
      const real = nominal / deflator;
      if (nominal > peak) {
        peak = nominal;
        if (!recovered && nominal >= amount) {
          recovered = true;
          yearsToRecover = Math.round((month / 12) * 10) / 10;
        }
      }
      const drawdown = (peak - nominal) / peak * 100;
      if (drawdown > maxDrawdownPct) {
        maxDrawdownPct = drawdown;
        drawdownYear = Math.round((month / 12) * 10) / 10;
      }
      if (month % 12 === 0) {
        path.push({ year: month / 12, nominal, real, drawdownFromPeakPct: Math.round(drawdown * 10) / 10 });
      }
    }

    const endingNominal = equityUnits * index + reserve;
    const endingReal = endingNominal / deflator;
    const realCagrPct = (Math.pow(endingReal / amount, 1 / years) - 1) * 100;
    return {
      path,
      endingNominal,
      endingReal,
      realCagrPct,
      maxDrawdownPct,
      drawdownYear,
      yearsToRecover,
    };
  }

  // Deterministic band: identical inputs always give the same sorted outcomes.
  function buildBand(options, blocks) {
    const {
      amount, years, equityPct, cashYieldPct, volatilityPct,
      shockPct, shockYear, stagingMonths, paths, seed,
    } = options;
    const equityShare = equityPct / 100;
    const totalMonths = years * 12;
    const vol = volatilityPct / 100;
    const results = [];

    for (let p = 0; p < paths; p += 1) {
      const random = makeRandom(seed + p * 7919);
      const installments = stagingMonths === 0 ? 1 : stagingMonths;
      let reserve = amount;
      let equityUnits = 0;
      let index = 1;
      let deflator = 1;
      for (let month = 1; month <= totalMonths; month += 1) {
        const year = Math.ceil(month / 12);
        const block = annualFactorsForYear(blocks, year);
        const cashMonthly = Math.pow(1 + cashYieldPct / 100, 1 / 12);
        let equityAnnual = block.equityPct / 100;
        if (shockYear > 0 && year === shockYear) equityAnnual = -shockPct / 100;
        const inflationMonthly = Math.pow(1 + block.inflationPct / 100, 1 / 12);
        let equityMonthly = Math.pow(1 + equityAnnual, 1 / 12);
        if (vol > 0) {
          const shock = vol * normalDraw(random) / Math.sqrt(12);
          equityMonthly = Math.max(0.05, Math.pow(1 + equityAnnual, 1 / 12) * (1 + shock));
        }
        reserve *= cashMonthly;
        if (stagingMonths === 0) {
          if (month === 1) {
            equityUnits = amount / index;
            reserve = 0;
          }
        } else if (month <= stagingMonths) {
          const purchase = Math.min(reserve, amount / stagingMonths);
          reserve -= purchase;
          equityUnits += purchase / index;
        }
        index *= equityMonthly;
        deflator *= inflationMonthly;
      }
      results.push((equityUnits * index + reserve) / deflator);
    }

    results.sort((a, b) => a - b);
    const pick = (q) => results[Math.min(results.length - 1, Math.max(0, Math.round(q * (results.length - 1))))];
    const low = results[0];
    const high = results[results.length - 1];
    const buckets = 10;
    const width = (high - low) / buckets || 1;
    const histogram = [];
    for (let b = 0; b < buckets; b += 1) {
      histogram.push({ from: low + b * width, to: low + (b + 1) * width, count: 0 });
    }
    results.forEach((value) => {
      const slot = Math.min(buckets - 1, Math.floor((value - low) / width));
      histogram[slot].count += 1;
    });
    const belowStart = results.filter((value) => value < amount).length / results.length * 100;
    return {
      paths: results.length,
      low,
      p10: pick(0.1),
      p50: pick(0.5),
      p90: pick(0.9),
      high,
      histogram,
      shareBelowStartPct: belowStart,
    };
  }

  function simulate(options) {
    validate(options);
    const blocks = blockList(options.preset, options.years);
    const pathResult = walkPath(options, blocks);
    const band = buildBand(options, blocks);
    return {
      blocks,
      presetLabel: PRESETS[options.preset].label,
      presetNote: PRESETS[options.preset].note,
      ...pathResult,
      band,
    };
  }

  const api = Object.freeze({ simulate, presets: PRESETS, regimes: REGIMES, blockList });
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.RegimeModel = api;
})(globalThis);
