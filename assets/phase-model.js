/* Local-only phased-investing sensitivity model. No inputs are persisted or transmitted. */
(function (root) {
  'use strict';

  function simulate({ amount, months, treasuryYieldPct, equityDriftPct, crashPct, crashMonth }) {
    const values = [amount, months, treasuryYieldPct, equityDriftPct, crashPct, crashMonth];
    if (!values.every(Number.isFinite) || amount <= 0 || !Number.isInteger(months) || months < 24 || months > 36 || crashPct < 0 || crashPct > 90 || !Number.isInteger(crashMonth) || crashMonth < 1 || crashMonth > months + 1 || treasuryYieldPct <= -100 || equityDriftPct <= -100) {
      throw new RangeError('Invalid phased-investing inputs.');
    }

    const monthlyTreasury = Math.pow(1 + treasuryYieldPct / 100, 1 / 12);
    const monthlyEquity = Math.pow(1 + equityDriftPct / 100, 1 / 12);
    const shock = 1 - crashPct / 100;
    const installment = amount / months;
    let reserve = amount;
    let shares = 0;
    let index = 1;
    let immediateShockLoss = 0;
    let phasedShockLoss = 0;
    let shockApplied = false;

    for (let month = 1; month <= months; month += 1) {
      reserve *= monthlyTreasury;
      if (crashMonth === month) {
        immediateShockLoss = amount * index * (1 - shock);
        phasedShockLoss = shares * index * (1 - shock);
        index *= shock;
        shockApplied = true;
      }
      const purchase = Math.min(reserve, installment);
      reserve -= purchase;
      shares += purchase / index;
      index *= monthlyEquity;
    }

    // Month N+1 means a shock immediately after the final scheduled purchase.
    if (!shockApplied) {
      immediateShockLoss = amount * index * (1 - shock);
      phasedShockLoss = shares * index * (1 - shock);
      index *= shock;
    }

    return {
      immediateEnding: amount * index,
      phasedEnding: shares * index + reserve,
      immediateShockLoss,
      phasedShockLoss,
      finalIndex: index,
      uninvestedReserve: reserve,
    };
  }

  const api = Object.freeze({ simulate });
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PhaseModel = api;
})(globalThis);
