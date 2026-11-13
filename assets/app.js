'use strict';
// No network requests, private inputs, analytics, or remotely stored approvals.
document.getElementById('print-page')?.addEventListener('click', () => window.print());
const storageKey = 'public-suggestion-review-v1';
const choices = [...document.querySelectorAll('.review-choice')];
const summary = document.getElementById('review-summary');
let state = {};
let storageAvailable = true;
try {
  const data = JSON.parse(localStorage.getItem(storageKey) || '{}');
  if (data && typeof data === 'object' && !Array.isArray(data)) state = data;
} catch (_) { storageAvailable = false; }
const allowed = new Set(['Not reviewed', 'Investigate', 'Preferred path', 'Defer']);
function updateSummary() {
  if (!summary) return;
  const count = choices.filter(choice => choice.value !== 'Not reviewed').length;
  summary.textContent = `${count} of ${choices.length} proposals reviewed. ${storageAvailable ? 'Saved only in this browser.' : 'Browser storage unavailable; choices last only for this page.'} No changes implemented.`;
}
choices.forEach(choice => {
  if (allowed.has(state[choice.dataset.id])) choice.value = state[choice.dataset.id];
  choice.addEventListener('change', () => {
    state = Object.fromEntries(choices.map(item => [item.dataset.id, item.value]));
    try { localStorage.setItem(storageKey, JSON.stringify(state)); }
    catch (_) { storageAvailable = false; }
    updateSummary();
  });
});
document.getElementById('reset-reviews')?.addEventListener('click', () => {
  choices.forEach(choice => { choice.value = 'Not reviewed'; });
  state = {};
  try { localStorage.removeItem(storageKey); }
  catch (_) { storageAvailable = false; }
  updateSummary();
});
updateSummary();
