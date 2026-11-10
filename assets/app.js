
/* Small progressive-enhancement helpers. All content is static HTML; no data fetch. */
(function () {
  'use strict';
  var input = document.getElementById('tableFilter');
  if (input) {
    input.addEventListener('input', function () {
      var q = this.value.trim().toLowerCase();
      var rows = document.querySelectorAll('table.data tbody tr');
      for (var i = 0; i < rows.length; i++) {
        rows[i].style.display = (!q || rows[i].textContent.toLowerCase().indexOf(q) !== -1) ? '' : 'none';
      }
    });
  }
  document.querySelectorAll('a[href^="http"]').forEach(function (a) {
    if (!a.hasAttribute('rel')) { a.setAttribute('rel', 'noopener noreferrer'); }
    if (!a.hasAttribute('target')) { a.setAttribute('target', '_blank'); }
  });
})();
