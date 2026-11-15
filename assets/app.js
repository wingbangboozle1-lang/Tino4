/* Local-only behaviour for the inheritance decision workspace.
 *
 * Everything here runs in the reader's browser. There is no network request, no
 * analytics, no remote font, no remote script and no form submission. Review
 * choices are stored in this browser's local storage only and can be cleared
 * with the reset button.
 *
 * The projection and staging calculators are illustrations built from explicit
 * assumptions. They are not forecasts, backtests or investment advice.
 */
(function () {
  'use strict';

  var REVIEW_KEY = 'inheritance-review-choices-v1';

  /* ----------------------------------------------------------------- utils */
  function round10(value) {
    if (!isFinite(value)) return 0;
    return Math.round(value / 10) * 10;
  }

  function money(value) {
    var n = Math.round(value);
    var sign = n < 0 ? '-' : '';
    var digits = Math.abs(n).toString();
    var out = '';
    for (var i = 0; i < digits.length; i++) {
      if (i > 0 && (digits.length - i) % 3 === 0) out += ',';
      out += digits.charAt(i);
    }
    return sign + '$' + out;
  }

  function pct(value, places) {
    var p = places === undefined ? 1 : places;
    return (value * 100).toFixed(p) + '%';
  }

  function el(id) {
    return document.getElementById(id);
  }

  function payload() {
    var node = document.getElementById('runtime-payload');
    if (!node) return null;
    try {
      return JSON.parse(node.getAttribute('data-payload'));
    } catch (err) {
      return null;
    }
  }

  function num(id) {
    var node = el(id);
    if (!node) return 0;
    var v = parseFloat(node.value);
    return isFinite(v) ? v : 0;
  }

  function setOutput(id, text) {
    var out = el(id + '-out');
    if (out) out.textContent = text;
  }

  /* -------------------------------------------------------------- printing */
  function wirePrint() {
    var button = el('print-page');
    if (!button) return;
    button.addEventListener('click', function () {
      window.print();
    });
  }

  /* ----------------------------------------------------------- review queue */
  function loadReviews() {
    try {
      var raw = window.localStorage.getItem(REVIEW_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (err) {
      return {};
    }
  }

  function saveReviews(store) {
    try {
      window.localStorage.setItem(REVIEW_KEY, JSON.stringify(store));
    } catch (err) {
      /* Storage may be unavailable; the page still works without it. */
    }
  }

  function wireReviews() {
    var selects = document.querySelectorAll('select.review-choice');
    if (!selects.length) return;
    var store = loadReviews();

    function summary() {
      var counts = { 'Not reviewed': 0, 'Investigate': 0, 'Selected': 0, 'Defer': 0 };
      Array.prototype.forEach.call(selects, function (select) {
        var key = select.getAttribute('data-id');
        var value = store[key] || select.value;
        counts[value] = (counts[value] || 0) + 1;
      });
      var node = el('review-summary');
      if (!node) return;
      var parts = [];
      Object.keys(counts).forEach(function (key) {
        parts.push(counts[key] + ' ' + key.toLowerCase());
      });
      node.textContent = 'Review queue: ' + parts.join(', ') + '. Saved in this browser only.';
    }

    Array.prototype.forEach.call(selects, function (select) {
      var key = select.getAttribute('data-id');
      if (store[key]) select.value = store[key];
      select.addEventListener('change', function () {
        store[key] = select.value;
        saveReviews(store);
        summary();
      });
    });

    var reset = el('reset-reviews');
    if (reset) {
      reset.addEventListener('click', function () {
        store = {};
        try {
          window.localStorage.removeItem(REVIEW_KEY);
        } catch (err) {
          /* ignore */
        }
        Array.prototype.forEach.call(selects, function (select) {
          select.value = 'Not reviewed';
        });
        summary();
      });
    }
    summary();
  }

  /* ------------------------------------------------------------ projections */
  /* Mirrors tools/casedata.py. Any change here must be made there too. */
  function makeModel(data, inputs) {
    var HOX = data.homeownersExemption;

    function growth(base, rate, years) {
      return base * Math.pow(1 + rate, years);
    }
    function marketA(year) {
      return round10(growth(data.a.valueNow, inputs.aApp, year - data.baseYear));
    }
    function marketB(year) {
      return round10(growth(data.b.valueNow, inputs.bApp, year - data.baseYear));
    }
    function assessedA(year) {
      return round10(growth(data.a.assessed2026, inputs.assessedGrowth, year - data.baseYear));
    }
    function assessedB(year) {
      return round10(growth(data.b.assessed2026, inputs.assessedGrowth, year - data.baseYear));
    }
    function limit(year) {
      return round10(growth(data.prop19LimitNow, inputs.prop19Growth, year - data.prop19LimitBaseYear));
    }
    function taxable(fmv, base, cap) {
      return round10(base + Math.max(0, fmv - (base + cap)));
    }
    function tax(value, rate, applyHox) {
      var base = value - (applyHox ? HOX : 0);
      return round10(Math.max(0, base) * rate);
    }
    function mid(band) {
      return (band[0] + band[1]) / 2;
    }
    function opA(year) {
      var y = year - data.baseYear;
      var water = round10(round10(mid(data.a.waterBand) * 12) * Math.pow(1 + inputs.inflation, y));
      var electric = -round10(round10(mid(data.a.electricCreditBand) * 12) * Math.pow(1 + inputs.inflation, y));
      var insurance = round10(data.a.insurance * Math.pow(1 + inputs.insuranceGrowth, y));
      var maintenance = round10(marketA(year) * inputs.maintenanceA);
      return { water: water, electric: electric, insurance: insurance, maintenance: maintenance,
               total: round10(water + electric + insurance + maintenance) };
    }
    function opB(year) {
      var y = year - data.baseYear;
      var water = round10(round10(mid(data.b.waterBand) * 12) * Math.pow(1 + inputs.inflation, y));
      var electric = round10(round10(mid(data.b.electricBand) * 12) * Math.pow(1 + inputs.inflation, y));
      var insurance = round10(data.b.insurance * Math.pow(1 + inputs.insuranceGrowth, y));
      var maintenance = round10(marketB(year) * inputs.maintenanceB);
      return { water: water, electric: electric, insurance: insurance, maintenance: maintenance,
               total: round10(water + electric + insurance + maintenance) };
    }
    function rentB(year) {
      return round10(data.b.rentIncomeMonthly * 12 * Math.pow(1 + inputs.rentGrowth, year - data.baseYear));
    }

    return {
      marketA: marketA, marketB: marketB, assessedA: assessedA, assessedB: assessedB,
      limit: limit, taxable: taxable, tax: tax, opA: opA, opB: opB, rentB: rentB
    };
  }

  function readInputs() {
    return {
      transferYear: num('transfer_year'),
      aApp: num('a_appreciation') / 100,
      bApp: num('b_appreciation') / 100,
      inflation: num('inflation') / 100,
      assessedGrowth: num('assessed_growth') / 100,
      prop19Growth: num('prop19_growth') / 100,
      insuranceGrowth: num('insurance_growth') / 100,
      rentGrowth: num('rent_growth') / 100,
      maintenanceA: num('maintenance_a') / 100,
      maintenanceB: num('maintenance_b') / 100,
      sellingCost: num('selling_cost') / 100,
      equityReturn: num('equity_return') / 100,
      treasuryYield: num('treasury_yield') / 100,
      stagingMonths: num('staging_months'),
      horizonYears: num('horizon_years')
    };
  }

  function wireProjections() {
    var form = el('control-form');
    if (!form) return;
    var data = payload();
    if (!data) return;

    var spec = [
      ['transfer_year', function (v) { return String(v); }],
      ['a_appreciation', function (v) { return v.toFixed(1) + '%'; }],
      ['b_appreciation', function (v) { return v.toFixed(1) + '%'; }],
      ['inflation', function (v) { return v.toFixed(1) + '%'; }],
      ['assessed_growth', function (v) { return v.toFixed(1) + '%'; }],
      ['prop19_growth', function (v) { return v.toFixed(1) + '%'; }],
      ['insurance_growth', function (v) { return v.toFixed(1) + '%'; }],
      ['rent_growth', function (v) { return v.toFixed(1) + '%'; }],
      ['maintenance_a', function (v) { return v.toFixed(1) + '%'; }],
      ['maintenance_b', function (v) { return v.toFixed(1) + '%'; }],
      ['selling_cost', function (v) { return v.toFixed(1) + '%'; }],
      ['equity_return', function (v) { return v.toFixed(1) + '%'; }],
      ['treasury_yield', function (v) { return v.toFixed(1) + '%'; }],
      ['staging_months', function (v) { return String(v); }],
      ['horizon_years', function (v) { return String(v); }]
    ];

    function syncOutputs() {
      spec.forEach(function (pair) {
        var node = el(pair[0]);
        if (node) setOutput(pair[0], pair[1](parseFloat(node.value)));
      });
    }

    function renderStats(model, inputs) {
      var t = inputs.transferYear;
      var fmv = model.marketA(t);
      var base = model.assessedA(t);
      var cap = model.limit(t);
      var occ = model.taxable(fmv, base, cap);
      var rented = round10(fmv);
      var net = round10(fmv * (1 - inputs.sellingCost));
      var stagingYears = inputs.stagingMonths / 12;
      var afterStage = round10(net * Math.pow(1 + inputs.treasuryYield, stagingYears));
      var remaining = Math.max(0, inputs.horizonYears - stagingYears);
      var staged = round10(afterStage * Math.pow(1 + inputs.equityReturn, remaining));
      var immediate = round10(net * Math.pow(1 + inputs.equityReturn, inputs.horizonYears));
      var taxNow = model.tax(model.assessedA(data.baseYear), data.effectiveRateA, true);

      var values = {
        'Value of A at transfer': money(fmv),
        'Assessment of A at transfer': money(base),
        'New taxable value if occupied': money(occ),
        'New taxable value if rented': money(rented),
        'Annual tax if occupied': money(model.tax(occ, data.effectiveRateA, true)),
        'Annual tax if rented': money(model.tax(rented, data.effectiveRateA, false)),
        'Net proceeds if sold': money(net),
        'Staged ending value': money(staged),
        'Immediate-entry ending value': money(immediate)
      };
      var nodes = document.querySelectorAll('#scenario-stats .stat');
      Array.prototype.forEach.call(nodes, function (node) {
        var key = node.getAttribute('data-stat');
        if (values[key]) {
          var target = node.querySelector('.stat-value');
          if (target) target.textContent = values[key];
        }
      });
      var note = el('tax-multiple-note');
      if (note && taxNow > 0) {
        note.textContent =
          'The step-up is about ' +
          (model.tax(occ, data.effectiveRateA, true) / taxNow).toFixed(1) + 'x if occupied and ' +
          (model.tax(rented, data.effectiveRateA, false) / taxNow).toFixed(1) + 'x if rented.';
      }
    }

    function renderTables(model, inputs) {
      var tables = document.querySelectorAll('.table-section table');
      if (tables.length < 2) return;
      var rowA = tables[0].querySelectorAll('tbody tr');
      var rowB = tables[1].querySelectorAll('tbody tr');
      Array.prototype.forEach.call(rowA, function (tr) {
        var year = parseInt(tr.children[0].textContent, 10);
        if (!isFinite(year)) return;
        var fmv = model.marketA(year);
        var base = model.assessedA(year);
        var cap = model.limit(year);
        var occ = model.taxable(fmv, base, cap);
        tr.children[1].textContent = money(fmv);
        tr.children[2].textContent = money(base);
        tr.children[3].textContent = year <= inputs.transferYear
          ? money(model.tax(base, data.effectiveRateA, true))
          : 'transferred';
        tr.children[4].textContent = money(model.tax(occ, data.effectiveRateA, true));
        tr.children[5].textContent = money(model.tax(round10(fmv), data.effectiveRateA, false));
      });
      Array.prototype.forEach.call(rowB, function (tr) {
        var year = parseInt(tr.children[0].textContent, 10);
        if (!isFinite(year)) return;
        var assessed = model.assessedB(year);
        tr.children[1].textContent = money(model.marketB(year));
        tr.children[2].textContent = money(assessed);
        tr.children[3].textContent = money(model.tax(assessed, data.effectiveRateB, false));
        tr.children[4].textContent = money(model.rentB(year));
        tr.children[5].textContent = money(model.opB(year).total);
      });
    }

    function recalc() {
      syncOutputs();
      var inputs = readInputs();
      var model = makeModel(data, inputs);
      renderStats(model, inputs);
      renderTables(model, inputs);
    }

    form.addEventListener('input', recalc);
    form.addEventListener('reset', function () {
      window.setTimeout(recalc, 0);
    });
    recalc();
  }

  /* ------------------------------------------------------- staging tool */
  function monthEquityReturn(month, params) {
    if (month < params.fallStart) return params.equity / 12;
    if (month < params.fallStart + params.fallMonths) {
      return Math.pow(1 - params.fallDepth, 1 / params.fallMonths) - 1;
    }
    return params.recover / 12;
  }

  function simulate(plan, params) {
    var cash = params.start;
    var equity = 0;
    var worst = params.start;
    var months = Math.max(1, Math.round(params.horizon * 12));
    for (var m = 0; m < months; m++) {
      var target;
      if (plan === 'cash') {
        target = 0;
      } else if (plan === 'immediate') {
        target = 1;
      } else {
        if (m < params.staging) target = 0;
        else if (m < params.staging + params.phase && params.phase > 0) {
          target = (m - params.staging + 1) / params.phase;
        } else {
          target = 1;
        }
      }
      var total = cash + equity;
      var want = total * target;
      if (want > equity) {
        var move = Math.min(cash, want - equity);
        cash -= move;
        equity += move;
      }
      var yieldMonthly = (m < params.staging ? params.yield : params.yieldAfter) / 12;
      cash *= 1 + yieldMonthly;
      equity *= 1 + monthEquityReturn(m, params);
      var now = cash + equity;
      if (now < worst) worst = now;
    }
    return { end: cash + equity, worst: worst };
  }

  function wireCalculator() {
    var form = el('calc-form');
    if (!form) return;
    var data = payload();
    var scalePerUnit = data && data.saleNetProceeds ? data.saleNetProceeds / 100 : 0;

    var spec = [
      ['calc-proceeds', function (v) { return String(v); }],
      ['calc-staging', function (v) { return String(v); }],
      ['calc-phase', function (v) { return String(v); }],
      ['calc-yield', function (v) { return v.toFixed(1); }],
      ['calc-yield-after', function (v) { return v.toFixed(1); }],
      ['calc-equity', function (v) { return v.toFixed(1); }],
      ['calc-drop', function (v) { return v.toFixed(1); }],
      ['calc-drop-start', function (v) { return String(v); }],
      ['calc-drop-months', function (v) { return String(v); }],
      ['calc-recover', function (v) { return v.toFixed(1); }],
      ['calc-horizon', function (v) { return String(v); }]
    ];

    function params() {
      return {
        start: num('calc-proceeds'),
        staging: num('calc-staging'),
        phase: num('calc-phase'),
        yield: num('calc-yield') / 100,
        yieldAfter: num('calc-yield-after') / 100,
        equity: num('calc-equity') / 100,
        fallDepth: num('calc-drop') / 100,
        fallStart: num('calc-drop-start'),
        fallMonths: num('calc-drop-months'),
        recover: num('calc-recover') / 100,
        horizon: num('calc-horizon')
      };
    }

    function amount(units) {
      var text = units.toFixed(0) + ' units';
      if (scalePerUnit > 0) {
        text += ' (' + money(round10(units * scalePerUnit)) + ')';
      }
      return text;
    }

    function recalc() {
      spec.forEach(function (pair) {
        var node = el(pair[0]);
        if (node) setOutput(pair[0], pair[1](parseFloat(node.value)));
      });

      var p = params();
      var immediate = simulate('immediate', p);
      var staged = simulate('staged', p);
      var cash = simulate('cash', p);

      var rows = [
        ['Immediate entry', immediate, 0],
        ['Staged entry', staged, staged.end - immediate.end],
        ['All Treasury paper', cash, cash.end - immediate.end]
      ];
      var body = el('calc-rows');
      if (body) {
        body.innerHTML = '';
        rows.forEach(function (row) {
          var tr = document.createElement('tr');
          [row[0], amount(row[1].end), amount(row[1].worst),
           row[2] === 0 ? 'baseline' : (row[2] > 0 ? '+' : '') + amount(row[2])].forEach(function (text, index) {
            var td = document.createElement(index === 0 ? 'th' : 'td');
            if (index === 0) td.setAttribute('scope', 'row');
            td.textContent = text;
            tr.appendChild(td);
          });
          body.appendChild(tr);
        });
      }

      /* Reinvestment risk, computed, never asserted. */
      var quiet = {
        start: p.start, staging: p.staging, phase: p.phase, yield: p.yield,
        yieldAfter: p.yieldAfter, equity: p.equity, fallDepth: 0, fallStart: 0,
        fallMonths: 1, recover: p.recover, horizon: p.horizon
      };
      var quietImmediate = simulate('immediate', quiet);
      var quietStaged = simulate('staged', quiet);
      var quietStagedHighYield = simulate('staged', {
        start: p.start, staging: p.staging, phase: p.phase, yield: p.yield,
        yieldAfter: p.yield, equity: p.equity, fallDepth: 0, fallStart: 0,
        fallMonths: 1, recover: p.recover, horizon: p.horizon
      });
      var waitBenefit = simulate('staged', {
        start: p.start, staging: p.staging, phase: p.phase, yield: p.yield,
        yieldAfter: p.yieldAfter, equity: p.equity, fallDepth: p.fallDepth,
        fallStart: Math.max(0, Math.min(Math.floor(p.staging / 2), p.staging)),
        fallMonths: p.fallMonths, recover: p.recover, horizon: p.horizon
      });
      var immediateHalfWait = simulate('immediate', {
        start: p.start, staging: p.staging, phase: p.phase, yield: p.yield,
        yieldAfter: p.yieldAfter, equity: p.equity, fallDepth: p.fallDepth,
        fallStart: Math.max(0, Math.min(Math.floor(p.staging / 2), p.staging)),
        fallMonths: p.fallMonths, recover: p.recover, horizon: p.horizon
      });
      var lateFall = simulate('staged', {
        start: p.start, staging: p.staging, phase: p.phase, yield: p.yield,
        yieldAfter: p.yieldAfter, equity: p.equity, fallDepth: p.fallDepth,
        fallStart: p.staging + p.phase, fallMonths: p.fallMonths,
        recover: p.recover, horizon: p.horizon
      });
      var immediateLate = simulate('immediate', {
        start: p.start, staging: p.staging, phase: p.phase, yield: p.yield,
        yieldAfter: p.yieldAfter, equity: p.equity, fallDepth: p.fallDepth,
        fallStart: p.staging + p.phase, fallMonths: p.fallMonths,
        recover: p.recover, horizon: p.horizon
      });

      var notes = [];
      notes.push('If nothing falls, staging ends ' +
        amount(Math.abs(quietStaged.end - quietImmediate.end)) +
        (quietStaged.end >= quietImmediate.end ? ' ahead of' : ' behind') +
        ' immediate entry. That gap is the price of the protection.');
      notes.push('If the Treasury yield available after the wait falls from ' +
        pct(p.yield) + ' to ' + pct(p.yieldAfter) + ', the staged path ends ' +
        amount(Math.abs(quietStaged.end - quietStagedHighYield.end)) +
        (quietStaged.end >= quietStagedHighYield.end ? ' better off' : ' worse off') +
        ' than if the yield had held.');
      notes.push('If the fall begins during the staging window, staged entry ends ' +
        amount(Math.abs(waitBenefit.end - immediateHalfWait.end)) +
        (waitBenefit.end >= immediateHalfWait.end ? ' ahead of' : ' behind') +
        ' immediate entry. This is the case staging is designed for.');
      notes.push('If the fall begins after the money is fully invested, staged entry ends ' +
        amount(Math.abs(lateFall.end - immediateLate.end)) +
        (lateFall.end >= immediateLate.end ? ' ahead of' : ' behind') +
        ' immediate entry. Staging does not protect against this case.');
      notes.push('The deepest point reached under immediate entry is ' +
        amount(immediate.worst) + ' against ' + amount(staged.worst) +
        ' under staging. A plan that must spend inside the trough fails even if it ends well.');

      var list = el('calc-risk');
      if (list) {
        list.innerHTML = '';
        notes.forEach(function (text) {
          var li = document.createElement('li');
          li.textContent = text;
          list.appendChild(li);
        });
      }
    }

    form.addEventListener('input', recalc);
    form.addEventListener('reset', function () {
      window.setTimeout(recalc, 0);
    });
    recalc();
  }

  /* ------------------------------------------------------------------ init */
  function init() {
    wirePrint();
    wireReviews();
    wireProjections();
    wireCalculator();
  }

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  }

  /* Exposed only for the offline parity test. The browser never sees a module
     object, so this branch is inert on the published site. */
  if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = {
      round10: round10,
      money: money,
      makeModel: makeModel,
      simulate: simulate,
      monthEquityReturn: monthEquityReturn
    };
  }
})();
