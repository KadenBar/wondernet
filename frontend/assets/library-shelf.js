// SPDX-License-Identifier: AGPL-3.0-only
// Research shelf filters only the local page. No fetching or outbound links.
"use strict";
(() => {
  const input = document.getElementById("lb-query");
  const kind = document.getElementById("lb-kind");
  const results = document.getElementById("lb-results");
  const grid = document.getElementById("lb-grid");
  if (!input || !kind || !results || !grid) return;
  const cards = Array.from(grid.querySelectorAll(".lb-book"));
  const filter = () => {
    const search = input.value.trim().toLocaleLowerCase();
    const group = kind.value;
    let visible = 0;
    for (const card of cards) {
      const matches = (group === "all" || card.dataset.kind === group) &&
        (!search || (card.dataset.search || "").includes(search));
      card.hidden = !matches;
      if (matches) visible += 1;
    }
    results.textContent = visible ?
      "Showing " + visible + " research " +
      (visible === 1 ? "candidate" : "candidates") :
      "No matching candidates yet. Try another word or collection.";
  };
  input.addEventListener("input", filter);
  kind.addEventListener("change", filter);
  filter();

  // Complete, readable books are an independent shelf. Filtering the pending
  // curation queue must never mark an unreviewed candidate as readable.
  const readableSearch = document.getElementById("lb-ready-query");
  const readableGrid = document.getElementById("lb-complete-grid");
  const readableResults = document.getElementById("lb-ready-results");
  if (readableSearch && readableGrid && readableResults) {
    const readableBooks = Array.from(readableGrid.querySelectorAll(".lb-full-book"));
    const updateReadable = () => {
      const term = readableSearch.value.trim().toLocaleLowerCase();
      let showing = 0;
      for (const book of readableBooks) {
        const matches = !term || (book.dataset.search || "").includes(term);
        book.hidden = !matches;
        if (matches) showing += 1;
      }
      readableResults.textContent = showing ?
        "Showing " + showing + " complete " +
        (showing === 1 ? "story" : "stories") :
        "No matching complete stories. Try another title or animal.";
    };
    readableSearch.addEventListener("input", updateReadable);
    updateReadable();
  }
})();
