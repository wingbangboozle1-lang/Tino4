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

  const sellRun = document.getElementById('sell-run');
  const sellClear = document.getElementById('sell-clear');
  const sellResult = document.getElementById('sell-result');
  const sellFmt = (value) => new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Math.max(0, Math.round(value / 10) * 10));
  if (sellRun && sellResult) {
    sellRun.addEventListener('click', () => {
      const value = Number(document.getElementById('sell-value')?.value);
      const basis = Number(document.getElementById('sell-basis')?.value);
      const costsPct = Number(document.getElementById('sell-costs')?.value);
      const dttPct = Number(document.getElementById('sell-dtt')?.value);
      const otherRaw = document.getElementById('sell-other')?.value.trim() ?? '';
      const other = otherRaw === '' ? 0 : Number(otherRaw);
      const timing = document.getElementById('sell-timing')?.value ?? 'later';
      const exclusion = Number(document.getElementById('sell-121')?.value);
      if (!(value > 0) || !Number.isFinite(basis) || basis < 0 || !Number.isFinite(costsPct) || costsPct < 0 || costsPct > 30 || !Number.isFinite(dttPct) || dttPct < 0 || dttPct > 10 || !Number.isFinite(other) || other < 0) {
        sellResult.textContent = 'Enter a positive sale value, a non-negative basis, and valid percentage assumptions.';
        return;
      }
      const costs = value * (costsPct / 100);
      const transferTax = value * (dttPct / 100);
      const realized = value - costs - basis;
      const modeledGain = timing === 'transfer' ? 0 : Math.max(0, realized);
      const gainAfterExclusion = Math.max(0, modeledGain - exclusion);
      const taxable = Math.max(0, gainAfterExclusion + other);
      const excess = Math.max(0, taxable - 1000000);
      const addOn = excess * 0.01;
      const lines = [
        `Estimated sale transaction costs: $${sellFmt(costs)}.`,
        `Estimated documentary transfer tax at the entered rate: $${sellFmt(transferTax)} (recording fees are additional; use the property's official schedule).`,
      ];
      if (timing === 'transfer') {
        lines.push('Transfer-year sale: gain is modeled at $0 because inherited basis is generally date-of-death value; a later sale adds post-death appreciation.');
      } else {
        lines.push(`Modeled gain before exclusion: $${sellFmt(modeledGain)}.`);
        lines.push(`Modeled gain after the entered section 121 amount: $${sellFmt(gainAfterExclusion)} (eligibility requires ownership and use tests).`);
      }
      lines.push(`Illustrative California 1% add-on on taxable income above $1,000,000: $${sellFmt(addOn)} (computed with the entered other income; not a complete tax return).`);
      sellResult.textContent = lines.join(' ');
    });
  }
  sellClear?.addEventListener('click', () => {
    ['sell-value', 'sell-basis', 'sell-costs', 'sell-dtt', 'sell-other'].forEach((id) => { const el = document.getElementById(id); if (el) el.value = ''; });
    const sel = document.getElementById('sell-121');
    if (sel) sel.value = '0';
    if (sellResult) sellResult.textContent = 'Inputs cleared.';
  });
})();
