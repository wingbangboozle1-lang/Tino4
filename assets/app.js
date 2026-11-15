(() => {
  'use strict';

  document.getElementById('print-page')?.addEventListener('click', () => window.print());

  const reviews = [...document.querySelectorAll('.review-choice')];
  const summary = document.getElementById('review-summary');
  const updateReviewSummary = () => {
    if (!summary) return;
    const counts = { Adopt: 0, Defer: 0, Reject: 0 };
    reviews.forEach((item) => { if (Object.hasOwn(counts, item.value)) counts[item.value] += 1; });
    summary.textContent = `Session-only review: ${counts.Adopt} adopt, ${counts.Defer} defer, ${counts.Reject} reject. Choices clear on refresh.`;
  };
  reviews.forEach((item) => item.addEventListener('change', updateReviewSummary));
  updateReviewSummary();

  const run = document.getElementById('phase-run');
  const clear = document.getElementById('phase-clear');
  const result = document.getElementById('phase-result');
  if (run && result) {
    run.addEventListener('click', () => {
      const amount = Number(document.getElementById('phase-amount')?.value);
      const months = Number(document.getElementById('phase-months')?.value);
      const treasuryRaw = document.getElementById('phase-yield')?.value.trim() ?? '';
      const equityRaw = document.getElementById('phase-equity')?.value.trim() ?? '';
      const treasuryPct = Number(treasuryRaw);
      const equityPct = Number(equityRaw);
      const declinePct = Number(document.getElementById('phase-crash')?.value);
      if (!treasuryRaw || !equityRaw || ![amount, months, treasuryPct, equityPct, declinePct].every(Number.isFinite) || amount <= 0 || months < 24 || months > 36 || declinePct < 0 || declinePct > 90) {
        result.textContent = 'Enter a positive amount, a staging period from 24 to 36 months, and valid percentage assumptions.';
        return;
      }
      const treasuryMonthly = Math.pow(1 + treasuryPct / 100, 1 / 12);
      const unitAt = (month) => {
        const fraction = month / months;
        return Math.max(0.0001, 1 + (equityPct / 100) * fraction - (declinePct / 100) * fraction);
      };
      const finalPrice = unitAt(months);
      const immediate = amount * finalPrice;
      let reserve = amount;
      let shares = 0;
      const purchase = amount / months;
      for (let month = 1; month <= months; month += 1) {
        reserve *= treasuryMonthly;
        const buy = Math.min(reserve, purchase);
        reserve -= buy;
        shares += buy / unitAt(month);
      }
      const phased = shares * finalPrice + reserve;
      const fmt = (value) => new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Math.round(value / 10) * 10);
      const delta = phased - immediate;
      const relation = Math.abs(delta) < 5 ? 'approximately matches' : delta > 0 ? 'is above' : 'is below';
      result.textContent = `Illustrative ending values: phased $${fmt(phased)}; immediate $${fmt(immediate)}. Under these assumptions, phased ${relation} immediate by about $${fmt(Math.abs(delta))}. This simplified path is not a forecast or backtest; it excludes taxes, fees, dividends, inflation, changing yields and other market paths.`;
    });
  }
  clear?.addEventListener('click', () => {
    document.getElementById('phase-amount').value = '';
    document.getElementById('phase-yield').value = '';
    document.getElementById('phase-equity').value = '';
    document.getElementById('phase-result').textContent = 'Inputs cleared.';
  });
})();

(() => {
  'use strict';

  // Local-only capital and tax sensitivity panel. Values never leave the page:
  // no storage, no network call, no default that could be read as a household figure.
  const capRun = document.getElementById('cap-run');
  const capStatus = document.getElementById('cap-status');
  if (!capRun || !capStatus) return;
  const num = (id, fallback) => {
    const raw = Number(document.getElementById(id)?.value);
    return Number.isFinite(raw) && raw > 0 ? raw : fallback;
  };
  const money = (value) => {
    if (!Number.isFinite(value)) return 'unavailable';
    const rounded = Math.round(value / 10) * 10;
    return (rounded < 0 ? '-' : '') + '$' + Math.abs(rounded).toLocaleString('en-US', { maximumFractionDigits: 0 });
  };
  capRun.addEventListener('click', () => {
    const basis = num('cap-basis', 0);
    const sale = num('cap-sale', 0);
    const rent = num('cap-rent', 0);
    if (!basis || !sale) {
      capStatus.textContent = 'Enter a depreciable basis and a sale price; every other field has a stated default.';
      return;
    }
    const years = num('cap-years', 10);
    const period = num('cap-period', 27.5);
    const rate = num('cap-rate', 40) / 100;
    const annual = basis / period;
    const recovered = Math.min(basis, annual * years);
    const shelter = recovered * rate;
    const federalRepay = Math.min(recovered * 0.25, recovered * rate);
    const stateRepay = recovered * rate;
    const dttRate = Number(document.getElementById('cap-dtt')?.value);
    const transferTax = Number.isFinite(dttRate) && dttRate > 0 ? (sale / 500) * dttRate : 0;
    const closingCost = sale * (num('cap-cost', 7) / 100);
    const net = sale - transferTax - closingCost;
    const avoidedRent = rent * years;
    capStatus.textContent = `Depreciation: about ${money(annual)} a year, ${money(recovered)} recovered over ${years} years, worth about ${money(shelter)} at the entered rate. `
      + `At sale the recovered amount is exposed to about ${money(federalRepay)} federal on unrecaptured gain plus about ${money(stateRepay)} state. `
      + `Transfer tax ${transferTax ? money(transferTax) : 'not entered'} and other closing costs ${money(closingCost)} leave about ${money(net)} investable. `
      + `Occupying the home avoids about ${money(avoidedRent)} of rent over the same years. Assumption-driven, rounded to the nearest ten dollars, not tax advice.`;
  });
  document.getElementById('cap-clear')?.addEventListener('click', () => {
    ['cap-basis', 'cap-sale', 'cap-rent', 'cap-dtt'].forEach((id) => {
      const field = document.getElementById(id);
      if (field) field.value = '';
    });
    capStatus.textContent = 'Inputs cleared.';
  });
})();
