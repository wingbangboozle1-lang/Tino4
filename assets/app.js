(() => {
  'use strict';

  document.getElementById('print-page')?.addEventListener('click', () => window.print());

  const reviews = [...document.querySelectorAll('.review-choice')];
  const summary = document.getElementById('review-summary');
  const copyBox = document.getElementById('review-copy');
  const updateReviewSummary = () => {
    if (!summary) return;
    const counts = { Adopt: 0, Defer: 0, Reject: 0 };
    reviews.forEach((item) => { if (Object.hasOwn(counts, item.value)) counts[item.value] += 1; });
    summary.textContent = `Session-only review: ${counts.Adopt} adopt, ${counts.Defer} defer, ${counts.Reject} reject, ${reviews.length - counts.Adopt - counts.Defer - counts.Reject} not reviewed. Choices clear on refresh.`;
    // Produce a dated, copyable record against each suggestion ID. The ID is
    // what belongs in the decision log; a reworded title is not an identifier.
    if (copyBox) {
      const decided = reviews.filter((item) => item.value !== 'Not reviewed');
      if (!decided.length) {
        copyBox.textContent = '';
        return;
      }
      const today = new Date().toISOString().slice(0, 10);
      const lines = decided.map((item) => {
        const id = item.dataset.id || 'unknown';
        return `${id}: ${item.value} (recorded in this browser session on ${today})`;
      });
      copyBox.textContent = `Suggested decision-log lines:\n${lines.join('\n')}\nReason and sign-off are required before this becomes a decision.`;
    }
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

  // ---- Staged-versus-lump distribution chart -------------------------
  // Reads the fixed scenario set from assets/staged-vs-lump.js. The visitor
  // chooses only a staging window and two assumption levels; no household
  // amount is ever entered, so nothing here can be traced to the family.
  const chart = document.getElementById('staged-chart');
  const chartLegend = document.getElementById('staged-chart-legend');
  const drawChart = () => {
    if (!chart || !window.StagedEntryModel) return;
    const months = Number(document.getElementById('staged-window')?.value ?? 24);
    const treasuryYieldPct = Number(document.getElementById('staged-yield')?.value ?? 4);
    const equityDriftPct = Number(document.getElementById('staged-drift')?.value ?? 7);
    let summary;
    try {
      summary = window.StagedEntryModel.runAll({ months, treasuryYieldPct, equityDriftPct });
    } catch (_error) {
      if (chartLegend) chartLegend.textContent = 'Check the window and the two percentage assumptions.';
      return;
    }
    const rows = summary.results;
    const values = rows.map((row) => row.difference * 100);
    const maxAbs = Math.max(10, ...values.map((value) => Math.abs(value)));
    const width = 720;
    const rowHeight = 26;
    const labelWidth = 250;
    const barWidth = width - labelWidth - 70;
    const zero = labelWidth + barWidth / 2;
    const scale = (barWidth / 2) / maxAbs;
    const ns = 'http://www.w3.org/2000/svg';
    chart.setAttribute('viewBox', `0 0 ${width} ${rows.length * rowHeight + 30}`);
    while (chart.firstChild) chart.removeChild(chart.firstChild);
    const title = document.createElementNS(ns, 'title');
    title.textContent = 'Staged minus lump-sum outcome by fixed scenario, percent of the lump sum at month 60';
    chart.appendChild(title);
    const axis = document.createElementNS(ns, 'line');
    axis.setAttribute('x1', zero); axis.setAttribute('x2', zero);
    axis.setAttribute('y1', 6); axis.setAttribute('y2', rows.length * rowHeight + 6);
    axis.setAttribute('stroke', '#8a8f98'); axis.setAttribute('stroke-width', '1');
    chart.appendChild(axis);
    rows.forEach((row, index) => {
      const value = row.difference * 100;
      const y = 10 + index * rowHeight;
      const label = document.createElementNS(ns, 'text');
      label.setAttribute('x', 4); label.setAttribute('y', y + 13);
      label.setAttribute('font-size', '10'); label.setAttribute('fill', '#243040');
      label.textContent = row.scenarioName.split(',')[0].slice(0, 44);
      chart.appendChild(label);
      const bar = document.createElementNS(ns, 'rect');
      const barLen = Math.abs(value) * scale;
      bar.setAttribute('x', value >= 0 ? zero : zero - barLen);
      bar.setAttribute('y', y + 3);
      bar.setAttribute('width', Math.max(1, barLen));
      bar.setAttribute('height', 13);
      bar.setAttribute('fill', value >= 0 ? '#2f7d5a' : '#a33a3a');
      bar.setAttribute('rx', 2);
      chart.appendChild(bar);
      const caption = document.createElementNS(ns, 'text');
      caption.setAttribute('x', value >= 0 ? zero + barLen + 6 : zero + 6);
      caption.setAttribute('y', y + 13);
      caption.setAttribute('font-size', '10'); caption.setAttribute('fill', '#243040');
      caption.textContent = `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
      chart.appendChild(caption);
    });
    chart.setAttribute('aria-label', rows.map((row) => `${row.scenarioName}: ${(row.difference * 100).toFixed(1)} percent`).join('; '));
    if (chartLegend) {
      chartLegend.textContent = `Fixed scenario set, ${months}-month window, evaluated at month 60. Staged ahead in ${summary.wins} of ${rows.length} scenarios; median ${(summary.medianDifference * 100).toFixed(1)}%, worst ${(summary.worstDifference * 100).toFixed(1)}%, best ${(summary.bestDifference * 100).toFixed(1)}%. These are assumption outcomes, not probabilities.`;
    }
  };
  if (chart) {
    ['staged-window', 'staged-yield', 'staged-drift'].forEach((id) => {
      document.getElementById(id)?.addEventListener('change', drawChart);
    });
    drawChart();
  }

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

  // Multi-regime (uneven growth and inflation) stress tool. Local only.
  const bwRun = document.getElementById('bw-run');
  const bwClear = document.getElementById('bw-clear');
  const bwResult = document.getElementById('bw-result');
  const bwChart = document.getElementById('bw-chart');
  const bwFmt = (value) => new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Math.round(value / 10) * 10);
  const bwPct = (value) => `${(Math.round(value * 10) / 10).toFixed(1)}%`;

  const bwRenderChart = (band, startValue) => {
    if (!bwChart) return;
    while (bwChart.firstChild) bwChart.removeChild(bwChart.firstChild);
    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox', '0 0 660 300');
    svg.setAttribute('role', 'img');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '300');
    svg.setAttribute('aria-label', 'Distribution of illustrative inflation-adjusted ending values across the entered number of paths.');
    const title = document.createElementNS(ns, 'title');
    title.textContent = 'Illustrative distribution of inflation-adjusted ending values';
    svg.appendChild(title);

    const left = 8;
    const base = 250;
    const plotWidth = 644;
    const maxCount = Math.max(...band.histogram.map((bucket) => bucket.count), 1);
    const slot = plotWidth / band.histogram.length;

    band.histogram.forEach((bucket, i) => {
      const height = Math.round((bucket.count / maxCount) * 190);
      const rect = document.createElementNS(ns, 'rect');
      rect.setAttribute('x', String(left + i * slot + 3));
      rect.setAttribute('y', String(base - height));
      rect.setAttribute('width', String(slot - 6));
      rect.setAttribute('height', String(Math.max(height, 1)));
      rect.setAttribute('fill', '#0f8a76');
      svg.appendChild(rect);
      const label = document.createElementNS(ns, 'text');
      label.setAttribute('x', String(left + i * slot + slot / 2));
      label.setAttribute('y', String(base + 16));
      label.setAttribute('text-anchor', 'middle');
      label.setAttribute('font-size', '9');
      label.setAttribute('fill', '#5d6f6d');
      label.textContent = String(Math.round(bucket.to / 1000));
      svg.appendChild(label);
      const count = document.createElementNS(ns, 'text');
      count.setAttribute('x', String(left + i * slot + slot / 2));
      count.setAttribute('y', String(base - height - 4));
      count.setAttribute('text-anchor', 'middle');
      count.setAttribute('font-size', '9');
      count.setAttribute('fill', '#37504c');
      count.textContent = String(bucket.count);
      svg.appendChild(count);
    });

    const axis = document.createElementNS(ns, 'line');
    axis.setAttribute('x1', String(left));
    axis.setAttribute('y1', String(base));
    axis.setAttribute('x2', String(left + plotWidth));
    axis.setAttribute('y2', String(base));
    axis.setAttribute('stroke', '#c5d8d4');
    svg.appendChild(axis);

    const startSlot = Math.min(band.histogram.length - 1, Math.max(0, Math.round(((startValue - band.low) / ((band.high - band.low) || 1)) * band.histogram.length)));
    const marker = document.createElementNS(ns, 'line');
    const markerX = left + startSlot * slot + slot / 2;
    marker.setAttribute('x1', String(markerX));
    marker.setAttribute('y1', '20');
    marker.setAttribute('x2', String(markerX));
    marker.setAttribute('y2', String(base));
    marker.setAttribute('stroke', '#d98026');
    marker.setAttribute('stroke-dasharray', '4 3');
    svg.appendChild(marker);
    const markerText = document.createElementNS(ns, 'text');
    markerText.setAttribute('x', String(markerX + 4));
    markerText.setAttribute('y', '16');
    markerText.setAttribute('font-size', '10');
    markerText.setAttribute('fill', '#8a5410');
    markerText.textContent = 'start (today\'s purchasing power)';
    svg.appendChild(markerText);

    const caption = document.createElementNS(ns, 'text');
    caption.setAttribute('x', String(left));
    caption.setAttribute('y', '285');
    caption.setAttribute('font-size', '10');
    caption.setAttribute('fill', '#5d6f6d');
    caption.textContent = 'Bar height = number of illustrative paths. Horizontal axis = inflation-adjusted ending value, in thousands of the entered currency units.';
    svg.appendChild(caption);

    bwChart.appendChild(svg);
  };

  if (bwRun && bwResult) {
    bwRun.addEventListener('click', () => {
      const read = (id) => document.getElementById(id)?.value.trim() ?? '';
      const amount = Number(read('bw-amount'));
      const years = Number(read('bw-years'));
      const equityPct = Number(read('bw-equity'));
      const cashYieldPct = Number(read('bw-cash'));
      const volatilityPct = Number(read('bw-vol'));
      const preset = read('bw-preset');
      const shockPct = Number(read('bw-shock'));
      const shockYear = Number(read('bw-shock-year'));
      const stagingMonths = Number(read('bw-staging'));
      const paths = Number(read('bw-paths'));
      if (!window.RegimeModel) {
        bwResult.textContent = 'The regime model did not load; reload the page and try again.';
        return;
      }
      const base = {
        amount, years, equityPct, cashYieldPct, volatilityPct,
        preset, shockPct, shockYear, stagingMonths, paths, seed: 20261117,
      };
      try {
        const staged = window.RegimeModel.simulate(base);
        const immediate = stagingMonths === 0 ? staged : window.RegimeModel.simulate({ ...base, stagingMonths: 0 });
        const lines = [
          `Scenario: ${staged.presetLabel}. ${staged.presetNote}`,
          `Regime walk over ${years} years: ${staged.blocks.map((b) => `${b.years}y ${b.label}`).join(' → ')}.`,
          `Inflation-adjusted ending value: staged entry $${bwFmt(staged.endingReal)} versus immediate entry $${bwFmt(immediate.endingReal)} (nominal staged $${bwFmt(staged.endingNominal)}).`,
          `Real annualised change: staged ${bwPct(staged.realCagrPct)} versus immediate ${bwPct(immediate.realCagrPct)}.`,
          `Largest peak-to-trough fall: staged ${bwPct(staged.maxDrawdownPct)} (around year ${staged.drawdownYear}) versus immediate ${bwPct(immediate.maxDrawdownPct)} (around year ${immediate.drawdownYear}).`,
          `Illustrative band over ${staged.band.paths} seeded paths: 10th percentile $${bwFmt(staged.band.p10)}, median $${bwFmt(staged.band.p50)}, 90th percentile $${bwFmt(staged.band.p90)}; ${bwPct(staged.band.shareBelowStartPct)} of paths finish below today's purchasing power.`,
        ];
        if (stagingMonths > 0) {
          const difference = staged.endingReal - immediate.endingReal;
          const softer = staged.maxDrawdownPct < immediate.maxDrawdownPct;
          lines.push(`Staging result is ${difference >= 0 ? 'above' : 'below'} immediate entry by about $${bwFmt(Math.abs(difference))} in inflation-adjusted terms here; the largest fall is ${softer ? 'smaller' : 'not smaller'} with staging. Staging trades early-market exposure for Treasury reinvestment risk and delayed participation, so it softens crash-entry risk only when the fall arrives while funds are still in the ladder.`);
        }
        lines.push('Deterministic illustration: the same inputs always produce the same result. It is not a forecast, a probability, a historical backtest, or advice. It excludes taxes, fees, dividends, contributions, withdrawals, property cash flows, changing Treasury yields beyond the entered rate, and recovery effects after the one-year shock.');
        bwResult.textContent = lines.join(' ');
        bwRenderChart(staged.band, amount);
      } catch (_error) {
        bwResult.textContent = 'Check: positive amount; horizon 5-50 years; equity share 0-100%; cash yield 0-25%; volatility 0-60%; shock 0-95%; shock year 0 (none) or within the horizon; staging 0 or 24-36 months; paths 1-500.';
      }
    });
  }
  bwClear?.addEventListener('click', () => {
    ['bw-amount', 'bw-equity', 'bw-cash', 'bw-vol', 'bw-shock'].forEach((id) => { const el = document.getElementById(id); if (el) el.value = ''; });
    const set = (id, value) => { const el = document.getElementById(id); if (el) el.value = value; };
    set('bw-years', '30');
    set('bw-preset', 'crash2008');
    set('bw-shock-year', '0');
    set('bw-staging', '24');
    set('bw-paths', '240');
    if (bwResult) bwResult.textContent = 'Inputs cleared.';
    if (bwChart) while (bwChart.firstChild) bwChart.removeChild(bwChart.firstChild);
  });
})();
