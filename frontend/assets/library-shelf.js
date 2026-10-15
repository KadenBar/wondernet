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
})();
