// SPDX-License-Identifier: AGPL-3.0-only
// Search only locally bundled book metadata; no requests or tracking.
(() => {
  const query = document.getElementById('lb-new-query');
  const grid = document.getElementById('lb-new-grid');
  const results = document.getElementById('lb-new-results');
  if (!query || !grid || !results) return;
  const cards = [...grid.querySelectorAll('.lb-full-book')];
  query.addEventListener('input', () => {
    const term = query.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const card of cards) {
      const matches = (card.dataset.search || '').includes(term);
      card.hidden = !matches;
      if (matches) visible++;
    }
    results.textContent = visible === cards.length ? `Showing all ${cards.length} books` : `Showing ${visible} of ${cards.length} books`;
  });
})();
