(() => {
  'use strict';

  document.getElementById('print-page')?.addEventListener('click', () => window.print());
  document.getElementById('print-brief')?.addEventListener('click', () => window.print());

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
      const renewalRaw = document.getElementById('phase-renewal')?.value.trim() ?? '';
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
      if (renewalRaw !== '') inputs.renewalYieldPct = Number(renewalRaw);
      try {
        const outcomes = window.PhaseModel.simulate(inputs);
        const fmt = (value) => new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Math.round(value / 10) * 10);
        const delta = outcomes.phasedEnding - outcomes.immediateEnding;
        const relation = Math.abs(delta) < 5 ? 'approximately matches' : delta > 0 ? 'is above' : 'is below';
        const crashWhen = inputs.crashMonth === inputs.months + 1 ? 'immediately after staging' : `at month ${inputs.crashMonth}`;
        result.textContent = `At the selected shock ${crashWhen}, the illustrative mark-to-market shock loss is about $${fmt(outcomes.immediateShockLoss)} for immediate investment versus $${fmt(outcomes.phasedShockLoss)} for the staged portfolio. Ending values: phased $${fmt(outcomes.phasedEnding)}; immediate $${fmt(outcomes.immediateEnding)}. Phased ${relation} immediate by about $${fmt(Math.abs(delta))} under these assumptions. The reduced early shock exposure trades against delayed market exposure and Treasury reinvestment risk.${inputs.renewalYieldPct === undefined ? '' : ` Reinvestment risk: rungs after month ${Math.ceil(inputs.months / 2)} were reinvested at the entered renewal yield of ${inputs.renewalYieldPct}% instead of ${inputs.treasuryYieldPct}%.`}`;
      } catch (_error) {
        result.textContent = 'Check: positive amount; 24–36 staging months; crash month from 1 through staging months + 1; crash from 0–90%; and valid annual yield and equity drift.';
      }
    });
  }
  clear?.addEventListener('click', () => {
    ['phase-amount', 'phase-yield', 'phase-renewal', 'phase-equity'].forEach((id) => { const input = document.getElementById(id); if (input) input.value = ''; });
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
      const depRaw = document.getElementById('sell-dep')?.value.trim() ?? '';
      const depreciation = depRaw === '' ? 0 : Number(depRaw);
      const costsPct = Number(document.getElementById('sell-costs')?.value);
      const dttPct = Number(document.getElementById('sell-dtt')?.value);
      const otherRaw = document.getElementById('sell-other')?.value.trim() ?? '';
      const other = otherRaw === '' ? 0 : Number(otherRaw);
      const timing = document.getElementById('sell-timing')?.value ?? 'later';
      const exclusion = Number(document.getElementById('sell-121')?.value);
      if (!(value > 0) || !Number.isFinite(basis) || basis < 0 || !Number.isFinite(depreciation) || depreciation < 0 || !Number.isFinite(costsPct) || costsPct < 0 || costsPct > 30 || !Number.isFinite(dttPct) || dttPct < 0 || dttPct > 10 || !Number.isFinite(other) || other < 0) {
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
      const recaptureTaxable = Math.min(depreciation, gainAfterExclusion);
      if (depreciation > 0) {
        lines.push(`Depreciation recapture overlay: up to $${sellFmt(recaptureTaxable)} of prior depreciation may be taxed as unrecaptured section 1250 gain at a maximum 25% federal rate — about $${sellFmt(recaptureTaxable * 0.25)} at that rate — and California taxes the gain as ordinary income. Confirm the depreciation schedule with the CPA.`);
      }
      lines.push(`Illustrative California 1% add-on on taxable income above $1,000,000: $${sellFmt(addOn)} (uses entered other taxable income plus modeled gain; not a complete tax return).`);
      sellResult.textContent = lines.join(' ');
    });
  }
  sellClear?.addEventListener('click', () => {
    ['sell-value', 'sell-basis', 'sell-dep', 'sell-costs', 'sell-dtt', 'sell-other'].forEach((id) => { const el = document.getElementById(id); if (el) el.value = ''; });
    const sel = document.getElementById('sell-121');
    if (sel) sel.value = '0';
    if (sellResult) sellResult.textContent = 'Inputs cleared.';
  });

  // ---- Live-path imputed-rent comparison ----
  const liveRun = document.getElementById('live-run');
  const liveClear = document.getElementById('live-clear');
  const liveResult = document.getElementById('live-result');
  const fmtR = (value) => new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Math.round(value / 10) * 10);
  const signedR = (value) => {
    const rounded = Math.round(value / 10) * 10;
    const formatted = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Math.abs(rounded));
    return rounded < 0 ? `-$${formatted}` : `$${formatted}`;
  };
  if (liveRun && liveResult) {
    liveRun.addEventListener('click', () => {
      const rent = Number(document.getElementById('live-rent')?.value);
      const cost = Number(document.getElementById('live-cost')?.value);
      const proceedsRaw = document.getElementById('live-proceeds')?.value.trim() ?? '';
      const proceeds = proceedsRaw === '' ? 0 : Number(proceedsRaw);
      if (!(rent > 0) || !Number.isFinite(cost) || cost < 0 || !Number.isFinite(proceeds) || proceeds < 0) {
        liveResult.textContent = 'Enter a positive monthly market rent and non-negative cost and proceeds figures.';
        return;
      }
      const imputedYear = rent * 12;
      const netPosition = imputedYear - cost;
      const investIncome = proceeds * 0.04;
      liveResult.textContent = `Living path: imputed rent about $${fmtR(imputedYear)} per year for a carrying cost of $${fmtR(cost)} — net lifestyle position about ${signedR(netPosition)} per year (positive means housing value exceeds carrying cost). Selling instead and investing $${fmtR(proceeds)} at an illustrative 4% would generate about $${fmtR(investIncome)} per year before taxes. Illustration only; 4% is an assumption, not a promised return.`;
    });
  }
  liveClear?.addEventListener('click', () => {
    ['live-rent', 'live-cost', 'live-proceeds'].forEach((id) => { const el = document.getElementById(id); if (el) el.value = ''; });
    if (liveResult) liveResult.textContent = 'Inputs cleared.';
  });

  // ---- Distribution chart (seeded regime-mixture illustration) ----
  const distRun = document.getElementById('dist-run');
  const distClear = document.getElementById('dist-clear');
  const distResult = document.getElementById('dist-result');
  const distChart = document.getElementById('dist-chart');
  const simulatePath = (pathKey, horizon, rnd) => {
    const net = 5157840; // 2045 base-case net proceeds, rounded per policy
    const normal = () => {
      const u1 = Math.max(1e-9, rnd());
      const u2 = rnd();
      return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    };
    const drawYear = () => {
      const u = rnd();
      let mu; let sd;
      if (u < 0.05) { mu = -0.28; sd = 0.20; } else if (u < 0.15) { mu = -0.02; sd = 0.15; } else if (u < 0.32) { mu = 0.03; sd = 0.18; } else { mu = 0.085; sd = 0.13; }
      return Math.max(-0.60, Math.min(0.45, mu + sd * normal()));
    };
    if (pathKey === 'rent') {
      const flows = 27000 * Math.pow(1.025, horizon / 2) * horizon * 1.25;
      const homeEnd = 3100000 * Math.pow(1.03, horizon + 19) * 0.939;
      return flows + homeEnd;
    }
    const months = pathKey === 'stage24' ? 24 : pathKey === 'stage36' ? 36 : 0;
    if (months === 0) {
      let f = 1;
      for (let y = 0; y < horizon; y += 1) f *= 1 + drawYear();
      return net * f;
    }
    const ty = Math.max(0, 0.04 + 0.01 * normal());
    const ry = Math.max(0, 0.03 + 0.01 * normal());
    const m0 = Math.pow(1 + ty, 1 / 12) - 1;
    const m1 = Math.pow(1 + ry, 1 / 12) - 1;
    const me = Math.pow(1.07, 1 / 12) - 1;
    let reserve = net;
    let shares = 0;
    let index = 1;
    for (let month = 1; month <= months; month += 1) {
      reserve *= 1 + (month <= months / 2 ? m0 : m1);
      const purchase = Math.min(reserve, net / months);
      reserve -= purchase;
      shares += purchase / index;
      index *= 1 + me;
    }
    const remaining = Math.max(0, horizon - months / 12);
    let f2 = 1;
    for (let y = 0; y < remaining; y += 1) f2 *= 1 + drawYear();
    return (shares * index + reserve) * f2;
  };
  if (distRun && distChart) {
    distRun.addEventListener('click', () => {
      const horizon = Number(document.getElementById('dist-horizon')?.value ?? 20);
      const pathKey = document.getElementById('dist-path')?.value ?? 'immediate';
      let state = 20261117;
      const rnd = () => {
        state = (1103515245 * state + 12345) % 2147483648;
        return state / 2147483648;
      };
      const draws = [];
      for (let i = 0; i < 2000; i += 1) draws.push(simulatePath(pathKey, horizon, rnd));
      draws.sort((a, b) => a - b);
      const q = (p) => draws[Math.min(draws.length - 1, Math.max(0, Math.floor(p * draws.length)))];
      const ctx = distChart.getContext('2d');
      const w = distChart.width; const h = distChart.height;
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = '#f4f1ea';
      ctx.fillRect(0, 0, w, h);
      const bins = 22;
      const lo = draws[0]; const hi = draws[draws.length - 1];
      const counts = new Array(bins).fill(0);
      draws.forEach((v) => {
        const b = Math.min(bins - 1, Math.floor(((v - lo) / Math.max(1, hi - lo)) * bins));
        counts[b] += 1;
      });
      const maxCount = Math.max(...counts);
      ctx.fillStyle = '#2f5d50';
      counts.forEach((c, i) => {
        const barH = (c / maxCount) * (h - 30);
        ctx.fillRect(10 + i * ((w - 20) / bins), h - 10 - barH, (w - 20) / bins - 2, barH);
      });
      ctx.fillStyle = '#1c1c1c';
      ctx.font = '12px sans-serif';
      ctx.fillText(`$${fmtR(lo)}`, 10, h - 0);
      ctx.fillText(`$${fmtR(hi)}`, w - 120, h - 0);
      if (distResult) {
        distResult.textContent = `Seeded illustration, ${horizon} years, 2,000 draws (not a probability forecast): P5 $${fmtR(q(0.05))}; P25 $${fmtR(q(0.25))}; median $${fmtR(q(0.5))}; P75 $${fmtR(q(0.75))}; P95 $${fmtR(q(0.95))}. Inputs run in browser memory only.`;
      }
    });
  }
  distClear?.addEventListener('click', () => {
    if (distChart) {
      const ctx = distChart.getContext('2d');
      ctx.clearRect(0, 0, distChart.width, distChart.height);
    }
    if (distResult) distResult.textContent = 'Inputs cleared.';
  });
})();
