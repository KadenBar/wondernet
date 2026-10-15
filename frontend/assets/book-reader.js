// SPDX-License-Identifier: AGPL-3.0-only
// Offline WonderNet chapter reader. No fetch, storage, accounts or third-party code.
"use strict";
(() => {
  const chapters = Array.from(document.querySelectorAll(".reader-chapter"));
  const toc = Array.from(document.querySelectorAll("[data-open-chapter]"));
  const previous = document.getElementById("reader-previous");
  const next = document.getElementById("reader-next");
  const progress = document.getElementById("reader-progress");
  const progressCopy = document.getElementById("reader-progress-copy");
  const pageLabel = document.getElementById("reader-page-label");
  const smaller = document.getElementById("reader-smaller");
  const larger = document.getElementById("reader-larger");
  const sizeLabel = document.getElementById("reader-size");
  const paper = document.querySelector(".reader-paper");
  const bookTop = document.querySelector(".reader-book-top");
  if (!chapters.length || !previous || !next || !paper) return;

  const sizeOptions = [80, 90, 100, 110, 120, 130, 140, 150, 160];
  let sizeIndex = 2;
  let current = 1;
  // The original demo has chapters; complete picture-book stories have short reading pages.
  const unit = document.body.dataset.readerUnit === "Page" ? "Page" : "Chapter";
  const languageSelect = document.getElementById("reader-language");
  let currentLanguage = "en";
  const title = number => {
    const heading = chapters[number - 1].querySelector("h2");
    const visibleTranslation = heading.querySelector("[data-story-lang]:not([hidden])");
    return visibleTranslation ? visibleTranslation.textContent : heading.textContent;
  };

  function chapterFromHash() {
    const result = /^#chapter-([1-9][0-9]*)$/.exec(window.location.hash);
    if (!result) return null;
    const number = Number(result[1]);
    return number >= 1 && number <= chapters.length ? number : null;
  }

  function renderChapter(number, fromHash = false, initial = false) {
    if (!Number.isInteger(number) || number < 1 || number > chapters.length) return;
    current = number;
    for (let index = 0; index < chapters.length; index += 1) {
      chapters[index].hidden = index !== number - 1;
    }
    for (const button of toc) {
      if (Number(button.dataset.openChapter) === number) button.setAttribute("aria-current", "true");
      else button.removeAttribute("aria-current");
    }
    previous.disabled = number === 1;
    next.disabled = number === chapters.length;
    next.textContent = number === chapters.length ?
      (currentLanguage === "es" ? "Fin del cuento ✓" : "End of story ✓") :
      (currentLanguage === "es" ? "Página siguiente →" : "Next " + unit.toLowerCase() + " →");
    previous.textContent = currentLanguage === "es" ? "← Página anterior" : "← Previous " + unit.toLowerCase();
    progress.max = chapters.length;
    progress.value = number;
    progressCopy.textContent = currentLanguage === "es" ?
      "Página " + number + " de " + chapters.length + " · " + title(number) :
      unit + " " + number + " of " + chapters.length + " · " + title(number);
    pageLabel.textContent = number + " / " + chapters.length;
    if (!fromHash && window.history && window.history.replaceState) {
      // The URL itself can identify the chapter. Nothing is saved to a device or server.
      window.history.replaceState(null, "", "#chapter-" + number);
    }
    if (!initial) {
      const heading = chapters[number - 1].querySelector("h2");
      heading.focus({ preventScroll: true });
      bookTop.scrollIntoView({ behavior: "auto", block: "start" });
    }
  }

  function renderFontSize() {
    const amount = sizeOptions[sizeIndex];
    paper.style.setProperty("--reader-text-size", (1.12 * amount / 100).toFixed(3) + "rem");
    sizeLabel.textContent = amount + "%";
    smaller.disabled = sizeIndex === 0;
    larger.disabled = sizeIndex === sizeOptions.length - 1;
  }

  toc.forEach(button => {
    button.addEventListener("click", () => renderChapter(Number(button.dataset.openChapter)));
  });
  previous.addEventListener("click", () => renderChapter(current - 1));
  next.addEventListener("click", () => renderChapter(current + 1));
  smaller.addEventListener("click", () => {
    if (sizeIndex > 0) sizeIndex -= 1;
    renderFontSize();
  });
  larger.addEventListener("click", () => {
    if (sizeIndex < sizeOptions.length - 1) sizeIndex += 1;
    renderFontSize();
  });

  for (const radio of document.querySelectorAll('input[name="reading-theme"]')) {
    radio.addEventListener("change", () => {
      if (radio.checked && ["paper", "night", "contrast"].includes(radio.value)) {
        document.body.dataset.readerTheme = radio.value;
      }
    });
  }
  // The new original picture book has parallel English/Spanish text and
  // original local SVGs. Switching never fetches, stores or executes content.
  // Other older books have no language selector and retain prior behavior.
  if (languageSelect) {
    const translations = Array.from(document.querySelectorAll("[data-story-lang]"));
    const illustrations = Array.from(document.querySelectorAll(".story-illustration img"));
    languageSelect.addEventListener("change", () => {
      const lang = languageSelect.value;
      if (lang !== "en" && lang !== "es") return;
      currentLanguage = lang;
      for (const node of translations) {
        node.hidden = node.dataset.storyLang !== lang;
      }
      for (const img of illustrations) {
        img.alt = lang === "es" ? img.dataset.altEs : img.dataset.altEn;
      }
      // Refresh progress and button labels, without changing or scrolling page.
      renderChapter(current, true, true);
    });
  }
  document.addEventListener("keydown", event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || event.repeat) return;
    if (event.target.closest("a, button, input, select, textarea, [contenteditable]")) return;
    if (event.key === "ArrowRight" && current < chapters.length) {
      event.preventDefault();
      renderChapter(current + 1);
    } else if (event.key === "ArrowLeft" && current > 1) {
      event.preventDefault();
      renderChapter(current - 1);
    }
  });
  window.addEventListener("hashchange", () => {
    const chapter = chapterFromHash();
    if (chapter !== null && chapter !== current) renderChapter(chapter, true);
  });

  renderFontSize();
  renderChapter(chapterFromHash() || 1, true, true);
})();
