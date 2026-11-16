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
      const amountRaw = document.getElementById('phase-amount')?.value.trim() ?? '';
      const monthsRaw = document.getElementById('phase-months')?.value.trim() ?? '';
      const treasuryRaw = document.getElementById('phase-yield')?.value.trim() ?? '';
      const equityRaw = document.getElementById('phase-equity')?.value.trim() ?? '';
      const crashRaw = document.getElementById('phase-crash')?.value.trim() ?? '';
      const crashMonthRaw = document.getElementById('phase-crash-month')?.value.trim() ?? '';
      if (!amountRaw || !monthsRaw || !treasuryRaw || !equityRaw || !crashRaw || !crashMonthRaw || !window.PhaseModel) {
        result.textContent = 'Enter a positive amount and both percentage assumptions; verify the staging controls loaded.';
        return;
      }
      const inputs = {
        amount: Number(amountRaw),
        months: Number(monthsRaw),
        treasuryYieldPct: Number(treasuryRaw),
        equityDriftPct: Number(equityRaw),
        crashPct: Number(crashRaw),
        crashMonth: Number(crashMonthRaw),
      };
      try {
        const outcomes = window.PhaseModel.simulate(inputs);
        const fmt = (value) => new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Math.round(value / 10) * 10);
        const delta = outcomes.phasedEnding - outcomes.immediateEnding;
        const relation = Math.abs(delta) < 5 ? 'approximately matches' : delta > 0 ? 'is above' : 'is below';
        const crashWhen = inputs.crashMonth === inputs.months + 1 ? 'immediately after staging' : `at month ${inputs.crashMonth}`;
        result.textContent = `At the selected shock ${crashWhen}, the illustrative mark-to-market shock loss is about $${fmt(outcomes.immediateShockLoss)} for immediate investment versus $${fmt(outcomes.phasedShockLoss)} for the staged portfolio. Ending values: phased $${fmt(outcomes.phasedEnding)}; immediate $${fmt(outcomes.immediateEnding)}. Phased ${relation} immediate by about $${fmt(Math.abs(delta))} under these assumptions. The reduced early shock exposure trades against delayed market exposure and Treasury reinvestment risk.`;
      } catch (_error) {
        result.textContent = 'Check: positive amount; 24–36 staging months; crash month from 1 through staging months + 1; crash from 0–90%; and valid annual yield and equity drift.';
      }
    });
  }
  clear?.addEventListener('click', () => {
    ['phase-amount', 'phase-yield', 'phase-equity'].forEach((id) => { const input = document.getElementById(id); if (input) input.value = ''; });
    document.getElementById('phase-months').value = '24';
    document.getElementById('phase-crash').value = '57';
    document.getElementById('phase-crash-month').value = '13';
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
      const modeledGain = Math.max(0, realized);
      const gainAfterExclusion = Math.max(0, modeledGain - exclusion);
      const taxable = Math.max(0, gainAfterExclusion + other);
      const excess = Math.max(0, taxable - 1000000);
      const addOn = excess * 0.01;
      const lines = [
        `Estimated sale transaction costs: $${sellFmt(costs)}.`,
        `Estimated documentary transfer tax at the entered rate: $${sellFmt(transferTax)} (recording fees are additional; the tax rate and income-tax treatment of costs need adviser verification).`,
      ];
      lines.push(`Modeled positive gain before any section 121 exclusion: $${sellFmt(modeledGain)} from sale value less entered transaction costs and basis${timing === 'transfer' ? ' for a transfer-year sale' : ''}. A same-year sale is not automatically tax-free: inherited basis is generally the date-of-death fair market value, subject to exceptions, and sale price/costs can differ.`);
      lines.push(`Modeled positive gain after the entered section 121 amount: $${sellFmt(gainAfterExclusion)} (eligibility requires ownership and use tests; this tool does not model a deductible loss).`);
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
