// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (c) 2026 WonderNet contributors
"use strict";
// The homepage search filters its six local section cards without fetching data.
const field = document.getElementById("section-search");
const cards = Array.from(document.querySelectorAll("#sections .portal-card"));
const status = document.getElementById("search-count");
const empty = document.getElementById("no-results");
if (field && status && empty && cards.length) {
  field.addEventListener("input", () => {
    const query = field.value.trim().toLocaleLowerCase();
    let visible = 0;
    cards.forEach(card => {
      const haystack = `${card.textContent} ${card.dataset.search || ""}`.toLocaleLowerCase();
      card.hidden = !haystack.includes(query);
      if (!card.hidden) visible += 1;
    });
    status.textContent = `Showing ${visible} ${visible === 1 ? "section" : "sections"}`;
    empty.hidden = visible !== 0;
  });
}
