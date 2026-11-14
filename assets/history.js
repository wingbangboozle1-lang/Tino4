/* Local-only calculator for the public historical price-index page.
   No network, analytics, storage, cookies, or personal-data collection. */
(function (root) {
  'use strict';

  function monthlyRate(ratePercent) {
    return Math.pow(1 + ratePercent / 100, 1 / 12) - 1;
  }

  function simulate(series, treasury, pathKey, waitMonths, principal) {
    if (!series || !Number.isFinite(principal) || principal <= 0) {
      throw new Error('A historical series and positive principal are required.');
    }
    const step = series.step_months;
    const indexForMonth = (months) => {
      if (months < 0 || months % step !== 0) throw new Error('Wait period does not match sourced observations.');
      const index = months / step;
      if (index >= series.values.length) throw new Error('Series does not cover the selected case.');
      return index;
    };
    if (pathKey === 'immediate') {
      const shares = principal / series.values[0];
      const values = series.values.map(price => shares * price);
      return summarize(values, principal, series);
    }
    if (!['bill-roll', 'four-rung-ladder'].includes(pathKey) || ![24, 36].includes(waitMonths)) {
      throw new Error('Select a supported parking path and a 24- or 36-month wait.');
    }
    const buyMonths = [waitMonths, waitMonths + 3, waitMonths + 6, waitMonths + 9];
    const buyIndexes = buyMonths.map(indexForMonth);
    if (buyIndexes[buyIndexes.length - 1] >= series.values.length) {
      throw new Error('The sourced series does not cover the full equity phase-in.');
    }

    const rates = treasury.rates_percent;
    let accounts;
    if (pathKey === 'bill-roll') {
      accounts = [{ balance: principal, rungMonths: 0 }];
    } else {
      accounts = [3, 6, 12, 24].map(rungMonths => ({
        balance: principal / 4,
        rungMonths
      }));
    }
    let cash = 0;
    let shares = 0;
    let phaseStartBalance = null;
    let previousMonth = 0;
    let buyCounter = 0;
    const values = [];

    for (let index = 0; index < series.values.length; index += 1) {
      const price = series.values[index];
      const elapsedMonth = index * step;
      if (phaseStartBalance === null) {
        for (let month = previousMonth; month < elapsedMonth; month += 1) {
          for (const account of accounts) {
            const rate = pathKey === 'four-rung-ladder' && month < account.rungMonths
              ? rates[account.rungMonths]
              : rates[3];
            account.balance *= 1 + monthlyRate(rate);
          }
        }
        if (elapsedMonth === waitMonths) {
          cash = accounts.reduce((sum, account) => sum + account.balance, 0);
          accounts = [{ balance: cash, rungMonths: 0 }];
        }
      } else {
        for (let month = previousMonth; month < elapsedMonth; month += 1) {
          cash *= 1 + monthlyRate(rates[3]);
        }
      }

      if (buyMonths.includes(elapsedMonth)) {
        if (phaseStartBalance === null) phaseStartBalance = cash;
        const purchase = Math.min(buyCounter < 3 ? phaseStartBalance / 4 : cash, cash);
        shares += purchase / price;
        cash -= purchase;
        buyCounter += 1;
      }

      const marketValue = shares * price;
      const reserveValue = phaseStartBalance === null
        ? accounts.reduce((sum, account) => sum + account.balance, 0)
        : cash;
      values.push(marketValue + reserveValue);
      previousMonth = elapsedMonth;
    }
    return summarize(values, principal, series);
  }

  function summarize(values, principal, series) {
    let peak = 0;
    let worst = 0;
    for (const value of values) {
      peak = Math.max(peak, value);
      if (peak > 0) worst = Math.min(worst, value / peak - 1);
    }
    return {
      terminalPerStartingUnit: values[values.length - 1] / principal,
      maximumObservedDrawdownPct: worst * 100,
      terminalDate: dateLabel(series, series.values.length - 1)
    };
  }

  function dateLabel(series, index) {
    const totalMonth = (series.start_year - 1) * 12 + (series.start_month - 1) + index * series.step_months;
    const year = Math.floor(totalMonth / 12) + 1;
    const month = (totalMonth % 12) + 1;
    if (series.step_months === 3) return `${year} Q${Math.floor((month - 1) / 3) + 1}`;
    return `${year}-${String(month).padStart(2, '0')}`;
  }

  function roundToTen(value) {
    return Math.sign(value) * Math.floor(Math.abs(value) / 10 + 0.5) * 10;
  }

  const api = { simulate, dateLabel, roundToTen };
  root.historyCalculator = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;

  if (typeof document === 'undefined') return;
  const dataNode = document.getElementById('market-data');
  const form = document.getElementById('market-form');
  if (!dataNode || !form) return;
  const data = JSON.parse(dataNode.textContent);
  const seriesSelect = document.getElementById('market-series');
  const waitSelect = document.getElementById('market-wait');
  const pathSelect = document.getElementById('market-path');
  const principalInput = document.getElementById('market-principal');
  const output = document.getElementById('market-output');
  const reset = document.getElementById('market-reset');
  const money = value => new Intl.NumberFormat('en-US', {
    style: 'currency', currency: 'USD', maximumFractionDigits: 0
  }).format(roundToTen(value));

  function render() {
    const principal = Number(principalInput.value);
    if (principalInput.value.trim() === '' || !Number.isFinite(principal) || principal <= 0) {
      output.textContent = 'Enter a positive amount to see rounded dollar outputs. No amount is prefilled, stored, or sent anywhere.';
      return;
    }
    const seriesKey = seriesSelect.value;
    const waitMonths = Number(waitSelect.value);
    const pathKey = pathSelect.value;
    const series = data.series[seriesKey];
    const immediate = simulate(series, data.treasury, 'immediate', 0, principal);
    const delayed = simulate(series, data.treasury, pathKey, waitMonths, principal);
    const difference = delayed.terminalPerStartingUnit - immediate.terminalPerStartingUnit;
    const sign = difference >= 0 ? '+' : '−';
    const diffText = `${sign}${money(Math.abs(difference * principal))}`;
    const pathLabel = pathKey === 'bill-roll'
      ? '3-month bill-roll scenario'
      : 'equal four-rung 3m/6m/1y/2y ladder scenario';
    output.innerHTML = `<div class="result-grid">
      <article><h3>Immediate price-index path</h3><p class="result-value">${money(immediate.terminalPerStartingUnit * principal)}</p><p>${immediate.maximumObservedDrawdownPct.toFixed(1)}% maximum observed drawdown</p></article>
      <article><h3>${waitMonths}-month wait + ${pathLabel}</h3><p class="result-value">${money(delayed.terminalPerStartingUnit * principal)}</p><p>${delayed.maximumObservedDrawdownPct.toFixed(1)}% maximum observed drawdown</p></article>
      <article><h3>Difference at ${delayed.terminalDate}</h3><p class="result-value">${diffText}</p><p>Delayed path minus immediate path; price-only equity and pretax Treasury assumptions.</p></article>
    </div><p class="result-warning">This is a hybrid illustration: historical price-index observations plus a 2026 Treasury-yield scenario. It is not a historical portfolio replay, forecast, or after-tax result.</p>`;
  }

  form.addEventListener('input', render);
  form.addEventListener('change', render);
  reset.addEventListener('click', () => {
    form.reset();
    output.textContent = 'Enter a positive amount to see rounded dollar outputs. No amount is prefilled, stored, or sent anywhere.';
    principalInput.focus();
  });
  render();
})(typeof window !== 'undefined' ? window : globalThis);
