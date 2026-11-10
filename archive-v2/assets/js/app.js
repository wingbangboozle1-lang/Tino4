/* Small progressive enhancement: click a column header to sort a table.
   No dependencies, no data fetching, no personal information. */
(function () {
  "use strict";

  function valueOf(cell) {
    var t = (cell.textContent || "").trim();
    if (!t || t === "—") return null;
    var neg = /^\(?-?\$?-?/.test(t) && t.indexOf("-") === 0;
    var n = t.replace(/[^0-9.\-]/g, "");
    if (n === "" || isNaN(parseFloat(n))) return { s: t.toLowerCase() };
    var v = parseFloat(n);
    if (t.indexOf("%") > -1) v = v; // percentages compare fine as numbers
    return { n: neg ? -Math.abs(v) : v };
  }

  function sortTable(table, idx) {
    var tbody = table.tBodies[0];
    if (!tbody) return;
    var rows = Array.prototype.slice.call(tbody.rows);
    var dir = table.getAttribute("data-sort-dir") === "asc" ? -1 : 1;
    table.setAttribute("data-sort-dir", dir === 1 ? "asc" : "desc");
    rows.sort(function (a, b) {
      var va = valueOf(a.cells[idx]), vb = valueOf(b.cells[idx]);
      if (va === null) return 1;
      if (vb === null) return -1;
      if (va.n !== undefined && vb.n !== undefined) return (va.n - vb.n) * dir;
      var sa = va.s || "", sb = vb.s || "";
      return sa.localeCompare(sb) * dir;
    });
    rows.forEach(function (r) { tbody.appendChild(r); });
  }

  document.querySelectorAll(".tablewrap table").forEach(function (table) {
    var head = table.tHead;
    if (!head || !head.rows.length) return;
    Array.prototype.forEach.call(head.rows[0].cells, function (th, i) {
      th.style.cursor = "pointer";
      th.title = "Click to sort";
      th.addEventListener("click", function () { sortTable(table, i); });
    });
  });
})();
