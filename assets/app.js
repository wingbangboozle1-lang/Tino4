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
  const sellSignedFmt = (value) => {
    const rounded = Math.round(value / 10) * 10;
    const formatted = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Math.abs(rounded));
    return rounded < 0 ? `-$${formatted}` : `$${formatted}`;
  };
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
        `Estimated documentary transfer tax at the entered rate: $${sellFmt(transferTax)} (recording fees are additional; use the property's official schedule).`,
        `Illustrative sale value less entered sale costs and basis: ${sellSignedFmt(realized)} (${realized < 0 ? 'potential loss' : 'potential gain'} before other tax rules).`,
      ];
      if (timing === 'transfer') {
        lines.push('Transfer-year sale is not forced to zero: the result uses the entered sale value, assumed sale costs, and basis. Confirm date-of-death value, sale timing, deductible costs, exceptions and tax treatment with the CPA.');
      }
      lines.push(`Positive modeled gain after the entered section 121 amount: $${sellFmt(gainAfterExclusion)} (eligibility requires ownership and use tests; this simple overlay does not model loss rules).`);
      lines.push(`Illustrative California 1% add-on on taxable income above $1,000,000: $${sellFmt(addOn)} (uses entered other taxable income plus modeled gain; not a complete tax return).`);
      sellResult.textContent = lines.join(' ');
    });
  }
  sellClear?.addEventListener('click', () => {
    ['sell-value', 'sell-basis', 'sell-costs', 'sell-dtt', 'sell-other'].forEach((id) => { const el = document.getElementById(id); if (el) el.value = ''; });
    const sel = document.getElementById('sell-121');
    if (sel) sel.value = '0';
    if (sellResult) sellResult.textContent = 'Inputs cleared.';
  });

  const cmpRun = document.getElementById('cmp-run');
  const cmpClear = document.getElementById('cmp-clear');
  const cmpResult = document.getElementById('cmp-result');
  const cmpMoney = (value) => '$' + new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Math.round(value / 10) * 10);
  const cmpDelta = (value) => {
    const rounded = Math.round(value / 10) * 10;
    if (rounded === 0) return 'level with';
    return `about ${cmpMoney(Math.abs(rounded))} ${rounded > 0 ? 'above' : 'below'}`;
  };
  if (cmpRun && cmpResult) {
    cmpRun.addEventListener('click', () => {
      const field = (id, fallback) => {
        const raw = document.getElementById(id)?.value.trim() ?? '';
        if (raw === '') return fallback;
        const parsed = Number(raw);
        return Number.isFinite(parsed) ? parsed : NaN;
      };
      const value = field('cmp-value', NaN);
      const rate = field('cmp-rate', NaN);
      const rentYield = field('cmp-yield', NaN);
      const costs = field('cmp-costs', 0);
      const portfolio = field('cmp-portfolio', NaN);
      const reserve = field('cmp-reserve', 0);
      const growth = field('cmp-growth', 3);
      const months = field('cmp-window', 30);
      const years = field('cmp-years', 25);
      if (!(value > 0) || !(rate >= 0) || rate > 10 || !(rentYield > 0) || rentYield > 20 || !Number.isFinite(portfolio) || !Number.isFinite(costs) || costs < 0 || !Number.isFinite(growth) || !(years >= 1) || years > 60 || !(months >= 0) || months > years * 12) {
        cmpResult.textContent = 'Enter a positive transfer-year value, a tax rate and rent yield within their ranges, a numeric portfolio return, and 1 to 60 years; the parking window must fit inside the horizon.';
        return;
      }
      const netRate = portfolio / 100;
      const saleCosts = 0.060 + 0.0011;
      const proceeds = value * (1 - saleCosts) - 220;
      const immediate = proceeds * (1 + netRate) ** years;
      const parked = proceeds * (1 + reserve / 100 / 12) ** months * (1 + netRate) ** Math.max(0, years - months / 12);
      let rentCash = 0;
      for (let year = 1; year <= years; year += 1) {
        const gross = value * (1 + growth / 100) ** year * (rentYield / 100);
        const carrying = value * (rate / 100) * 1.02 ** year + costs * 1.03 ** year + gross * 0.04;
        const operating = gross * 0.96 - carrying;
        rentCash += operating * (1 + netRate) ** (years - year);
      }
      const horizonValue = value * (1 + growth / 100) ** years;
      const horizonGain = Math.max(0, horizonValue * (1 - saleCosts) - value);
      const holding = horizonValue * (1 - saleCosts) - 220 - horizonGain * 0.371 + rentCash;
      const best = Math.max(immediate, parked, holding);
      const named = best === immediate ? 'selling in the transfer year and investing at once' : (best === parked ? 'parking before a single purchase' : 'holding and letting to the horizon');
      cmpResult.textContent = `Modeled position at the horizon: sell and invest ${cmpMoney(immediate)}; park ${Math.round(months)} months then invest ${cmpMoney(parked)}; hold and let ${cmpMoney(holding)}. The ranking on these inputs favors ${named}. Relative to investing at once, parking sits ${cmpDelta(parked - immediate)} and holding and letting sits ${cmpDelta(holding - immediate)}. Rounded figures on the assumptions typed in, computed in this tab and never sent anywhere: re-run the site tables and the private model with written records before treating any ranking as a decision.`;
    });
    cmpClear?.addEventListener('click', () => {
      ['cmp-value', 'cmp-rate', 'cmp-yield', 'cmp-costs', 'cmp-portfolio', 'cmp-reserve'].forEach((id) => { const el = document.getElementById(id); if (el) el.value = ''; });
      const defaults = { 'cmp-growth': '3', 'cmp-window': '30', 'cmp-years': '25' };
      Object.entries(defaults).forEach(([id, val]) => { const el = document.getElementById(id); if (el) el.value = val; });
      if (cmpResult) cmpResult.textContent = 'Inputs cleared; nothing was stored.';
    });
  }
})();
