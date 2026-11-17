/*
 * Staged-versus-lump-sum entry model for inherited-sale proceeds.
 *
 * THE QUESTION THIS ANSWERS
 * "If the sale proceeds arrive as one lump sum, does parking them in 3-month to
 * 2-year Treasuries and phasing into equities over 24-36 months actually make
 * a 1929- or 2008-shaped crash less damaging to the household?"
 *
 * It cannot be answered by a single drawdown number. It depends on WHERE in the
 * staging window the crash lands, HOW LONG the market then takes to recover,
 * and WHAT the waiting reserve earns once yields fall. This model varies those
 * three things across a fixed, published scenario set.
 *
 * DESIGN RULES
 * 1. Nothing is stored, logged or transmitted. Evaluation is in memory only.
 * 2. Every scenario is a named, fixed assumption set defined in this file. The
 *    visitor types no figures, so no household amount can be recovered from
 *    this page or from anything it sends.
 * 3. Historical anchors are used as drawdown DEPTHS and RECOVERY DURATIONS.
 *    They are never presented as probabilities and never as a forecast of any
 *    portfolio.
 * 4. The output is the distribution over the scenario set, not one headline
 *    number. A single number is how a projection gets reverse-engineered into
 *    a conclusion, which the decision log explicitly forbids.
 *
 * SCOPE LIMITS (repeated on the page)
 * - Price-index arithmetic only: no dividends, fees, taxes, inflation,
 *   withdrawals, or cross-asset correlation.
 * - The Treasury reserve earns a stated annual yield. Price risk from selling a
 *   note before maturity is not modeled, because the ladder is assumed to be
 *   held to maturity.
 * - Recovery is a monotone path back to the prior peak. Real recoveries are
 *   irregular; some markets have not regained a peak for decades, which is why
 *   the 1929 anchor is included at all.
 */
(function (root) {
  'use strict';

  // ---- Verified historical anchors -------------------------------------
  // 1929: Dow Jones Industrial Average fell 89% peak to trough; the peak was
  // not regained until November 1954.
  //   https://www.federalreservehistory.org/essays/stock-market-crash-of-1929
  // 2007-09: S&P 500 fell 57% from its October 2007 peak to its March 2009
  // trough.
  //   https://www.federalreservehistory.org/essays/great-recession-of-200709
  const ANCHORS = Object.freeze({
    crash1929: Object.freeze({
      depthPct: 89,
      monthsToTrough: 33, // September 1929 peak to July 1932 trough
      monthsToRecover: 302, // July 1932 trough to November 1954
    }),
    crash2008: Object.freeze({
      depthPct: 57,
      monthsToTrough: 17, // October 2007 peak to March 2009 trough
      monthsToRecover: 49, // March 2009 trough to March 2013 nominal regain
    }),
  });

  // ---- Published scenario set ------------------------------------------
  // crashAtMonth is 1-based; 0 means no crash in the horizon.
  // renewalYieldPct is the annual Treasury yield after the crash begins. This
  // is the reinvestment risk that the staged path actually carries, and it is
  // the reason staging can lose to a lump sum even in a real crash.
  const SCENARIOS = Object.freeze([
    { id: 'early-2008', name: 'Crash in month 3, 2008-shaped, yields fall to 0.5%', crashAtMonth: 3, anchor: 'crash2008', renewalYieldPct: 0.5, note: 'Best case for staging: almost nothing is invested yet, so almost nothing is exposed.' },
    { id: 'early-1929', name: 'Crash in month 3, 1929-shaped, yields fall to 0.5%', crashAtMonth: 3, anchor: 'crash1929', renewalYieldPct: 0.5, note: 'Same timing with the deeper, far slower 1929-shaped path. The reserve still has to fund 21 more purchases into a falling market.' },
    { id: 'mid-2008', name: 'Crash in month 12, 2008-shaped, yields fall to 1.5%', crashAtMonth: 12, anchor: 'crash2008', renewalYieldPct: 1.5, note: 'Roughly half the scheduled purchases are already done when the crash lands.' },
    { id: 'mid-1929', name: 'Crash in month 12, 1929-shaped, yields fall to 1.5%', crashAtMonth: 12, anchor: 'crash1929', renewalYieldPct: 1.5, note: 'Half deployed, then a 25-year recovery.' },
    { id: 'late-2008', name: 'Crash in month 24, 2008-shaped, yields fall to 1.5%', crashAtMonth: 24, anchor: 'crash2008', renewalYieldPct: 1.5, note: 'A 24-month plan is complete; a 36-month plan still has a third of the money waiting.' },
    { id: 'late-1929', name: 'Crash in month 24, 1929-shaped, yields fall to 1.5%', crashAtMonth: 24, anchor: 'crash1929', renewalYieldPct: 1.5, note: 'A 24-month plan is complete, with the deep slow path.' },
    { id: 'after-2008', name: 'Crash in month 37, 2008-shaped', crashAtMonth: 37, anchor: 'crash2008', renewalYieldPct: 1.5, note: 'After a 36-month plan finishes: staging is over, so it protects nothing. Both paths are fully exposed.' },
    { id: 'flat', name: 'No crash, flat price index (0% drift), 2% reserve yield', crashAtMonth: 0, anchor: null, renewalYieldPct: 2.0, driftPct: 0, note: 'Staging earns the reserve yield on money not yet invested, so with a flat index the staged path finishes ahead by roughly the reserve yield.' },
    { id: 'rising', name: 'No crash, steady rise (8% drift), 2% reserve yield', crashAtMonth: 0, anchor: null, renewalYieldPct: 2.0, driftPct: 8, note: 'The standard argument against staging: the reserve misses a rising market. The cost is the equity-minus-Treasury spread on money still waiting, not the whole equity return.' },
  ]);

  const WINDOWS = Object.freeze([24, 36]);
  // Every scenario is evaluated at the SAME date, 60 months (5 years) after the
  // lump sum arrives. Comparing scenarios at different dates would let a late
  // crash look benign simply because it was measured early, which is exactly
  // the reverse-engineering this project forbids.
  const EVALUATION_HORIZON_MONTHS = 60;

  function monthlyRate(annualPct) {
    return Math.pow(1 + annualPct / 100, 1 / 12);
  }

  /**
   * Equity price index for one scenario.
   * index[t] is the level at the start of month t; index[0] = 1.
   * Drift compounds every month; the crash is a separate multiplier applied on
   * top from crashAtMonth to the trough, then unwound to the prior peak over
   * the anchor's recovery period. Using a multiplier keeps the two effects
   * separable and testable.
   */
  function buildIndex(scenario, totalMonths, equityDriftPct) {
    const drift = monthlyRate(equityDriftPct);
    const anchor = scenario.anchor ? ANCHORS[scenario.anchor] : null;
    const crash = scenario.crashAtMonth;
    const troughLevel = anchor ? 1 - anchor.depthPct / 100 : 1;
    const troughMonth = anchor ? crash + anchor.monthsToTrough : 0;
    const recoverMonth = anchor ? troughMonth + anchor.monthsToRecover : 0;

    const index = [1];
    let level = 1;
    for (let month = 1; month <= totalMonths; month += 1) {
      level *= drift;
      let multiplier = 1;
      if (crash && month > crash && month <= troughMonth) {
        // Declining phase: geometric interpolation from 1 to troughLevel.
        const progress = (month - crash) / (troughMonth - crash);
        multiplier = Math.pow(troughLevel, progress);
      } else if (anchor && month > troughMonth && month <= recoverMonth) {
        // Recovery phase: geometric interpolation from troughLevel back to 1.
        const progress = (month - troughMonth) / (recoverMonth - troughMonth);
        multiplier = Math.pow(troughLevel, 1 - progress);
      }
      index.push(level * multiplier);
    }
    return index;
  }

  /**
   * Run the staged and immediate paths for one published scenario.
   *
   * @param {object} options
   * @param {number} options.months staging window in months (24 or 36)
   * @param {number} options.treasuryYieldPct starting annual reserve yield
   * @param {number} options.equityDriftPct annual equity price drift
   * @param {string} options.scenarioId a published scenario id
   */
  function run({ months, treasuryYieldPct, equityDriftPct, scenarioId }) {
    const scenario = SCENARIOS.find((item) => item.id === scenarioId);
    if (!scenario) throw new RangeError('Unknown scenario.');
    if (!Number.isInteger(months) || !WINDOWS.includes(months)) {
      throw new RangeError('Staging window must be 24 or 36 months.');
    }
    if (![treasuryYieldPct, equityDriftPct].every(Number.isFinite)) {
      throw new RangeError('Numeric assumptions required.');
    }
    if (treasuryYieldPct <= -100 || equityDriftPct <= -100) {
      throw new RangeError('Assumptions out of range.');
    }

    const totalMonths = Math.max(EVALUATION_HORIZON_MONTHS, (scenario.crashAtMonth || 0) + 1);
    // A scenario may pin its own drift (the no-crash pair must differ, or the
    // comparison tests nothing). Otherwise the caller's drift applies.
    const drift = Number.isFinite(scenario.driftPct) ? scenario.driftPct : equityDriftPct;
    const index = buildIndex(scenario, totalMonths, drift);
    const startYield = monthlyRate(treasuryYieldPct);
    const laterYield = monthlyRate(scenario.renewalYieldPct);
    const installment = 1 / months; // the lump sum is normalized to 1

    // Immediate: the whole lump sum buys equity in month 1.
    const immediateShares = 1 / index[0];

    // Staged: 1/months of the lump sum converts to equity each month; the rest
    // waits in the reserve and earns the reserve yield (which falls after a
    // crash, exactly when the staged path is holding the most cash).
    let stagedShares = 0;
    let reserve = 1;
    const immediateCurve = [];
    const stagedCurve = [];

    for (let month = 1; month <= totalMonths; month += 1) {
      const rate = scenario.crashAtMonth && month > scenario.crashAtMonth ? laterYield : startYield;
      reserve *= rate;
      if (month <= months) {
        const buy = Math.min(reserve, installment);
        reserve -= buy;
        stagedShares += buy / index[month - 1];
      }
      immediateCurve.push(immediateShares * index[month]);
      stagedCurve.push(stagedShares * index[month] + reserve);
    }

    const immediateEnding = immediateCurve[immediateCurve.length - 1];
    const stagedEnding = stagedCurve[stagedCurve.length - 1];

    return {
      scenarioId,
      scenarioName: scenario.name,
      scenarioNote: scenario.note,
      crashAtMonth: scenario.crashAtMonth,
      months,
      totalMonths,
      immediateEnding,
      stagedEnding,
      difference: stagedEnding - immediateEnding,
      immediateWorstDrawdownPct: worstDrawdownPct(immediateCurve),
      stagedWorstDrawdownPct: worstDrawdownPct(stagedCurve),
      uninvestedReserve: reserve,
      immediateCurve,
      stagedCurve,
    };
  }

  /** Worst peak-to-trough percentage fall in a value series. */
  function worstDrawdownPct(series) {
    let peak = 0;
    let worst = 0;
    for (const value of series) {
      peak = Math.max(peak, value);
      if (peak > 0) worst = Math.max(worst, (peak - value) / peak);
    }
    return worst * 100;
  }

  /** Run every published scenario and summarize the distribution. */
  function runAll({ months, treasuryYieldPct, equityDriftPct }) {
    const results = SCENARIOS.map((scenario) =>
      run({ months, treasuryYieldPct, equityDriftPct, scenarioId: scenario.id })
    );
    const differences = results.map((item) => item.difference);
    const wins = differences.filter((value) => value > 0).length;
    return {
      results,
      wins,
      losses: results.length - wins,
      medianDifference: median(differences),
      worstDifference: Math.min(...differences),
      bestDifference: Math.max(...differences),
      meanDifference: differences.reduce((a, b) => a + b, 0) / differences.length,
    };
  }

  function median(values) {
    const sorted = [...values].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
  }

  const api = Object.freeze({
    ANCHORS,
    SCENARIOS,
    WINDOWS,
    EVALUATION_HORIZON_MONTHS,
    run,
    runAll,
    worstDrawdownPct,
  });
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.StagedEntryModel = api;
})(globalThis);
