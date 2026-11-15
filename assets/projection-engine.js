/* Pure projection engine for the working-figure layer.
 *
 * This file has no DOM dependency at load time. It is loaded by every page and
 * used by assets/app.js, and it is also required directly by
 * tools/engine_check.cjs so the browser and Python engines can be compared.
 *
 * It mirrors tools/casedata.py. If either implementation changes, the other
 * must change with it: the Python test suite fails the build when they diverge.
 *
 * Everything is computed locally. There is no network request.
 */
(function (root) {
  'use strict';

  function round10(value) {
    if (!Number.isFinite(value)) return 0;
    return Math.round(value / 10) * 10;
  }

  function moneyWhole(value) {
    var rounded = Math.round(value);
    var sign = rounded < 0 ? '-' : '';
    var digits = String(Math.abs(rounded));
    var out = '';
    for (var i = 0; i < digits.length; i++) {
      if (i > 0 && (digits.length - i) % 3 === 0) out += ',';
      out += digits.charAt(i);
    }
    return sign + '$' + out;
  }

  function growth(base, rate, years) {
    return base * Math.pow(1 + rate, years);
  }

  function mid(band) {
    return (band[0] + band[1]) / 2;
  }

  function projectionModel(data, inputs) {
    var HOX = data.homeownersExemption;

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
      return round10(Math.max(0, value - (applyHox ? HOX : 0)) * rate);
    }
    function opA(year) {
      var y = year - data.baseYear;
      var water = round10(round10(mid(data.a.waterBand) * 12) * Math.pow(1 + inputs.inflation, y));
      var electric = -round10(round10(mid(data.a.electricCreditBand) * 12) * Math.pow(1 + inputs.inflation, y));
      var insurance = round10(data.a.insurance * Math.pow(1 + inputs.insuranceGrowth, y));
      var maintenance = round10(marketA(year) * inputs.maintenanceA);
      return round10(water + electric + insurance + maintenance);
    }
    function opB(year) {
      var y = year - data.baseYear;
      var water = round10(round10(mid(data.b.waterBand) * 12) * Math.pow(1 + inputs.inflation, y));
      var electric = round10(round10(mid(data.b.electricBand) * 12) * Math.pow(1 + inputs.inflation, y));
      var insurance = round10(data.b.insurance * Math.pow(1 + inputs.insuranceGrowth, y));
      var maintenance = round10(marketB(year) * inputs.maintenanceB);
      return round10(water + electric + insurance + maintenance);
    }
    function rentB(year) {
      return round10(data.b.rentIncomeMonthly * 12 * Math.pow(1 + inputs.rentGrowth, year - data.baseYear));
    }

    return {
      marketA: marketA, marketB: marketB,
      assessedA: assessedA, assessedB: assessedB,
      limit: limit, taxable: taxable, tax: tax,
      opA: opA, opB: opB, rentB: rentB
    };
  }

  var api = {
    round10: round10,
    moneyWhole: moneyWhole,
    projectionModel: projectionModel
  };

  if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = api;
  }
  if (root) {
    root.ProjectionEngine = api;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
