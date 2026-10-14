"use strict";
const field = document.getElementById("section-search");
const cards = Array.from(document.querySelectorAll("#sections .tile"));
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
