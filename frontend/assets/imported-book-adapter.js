// SPDX-License-Identifier: AGPL-3.0-only
// Adapt imported, locally bundled public-domain text to the existing WonderNet reader.
// No network, storage, injected HTML, or third-party dependencies.
"use strict";
(() => {
  const source = document.querySelector("main#main");
  if (!source || source.querySelector(".reader-book")) return;
  const oldNav = source.querySelector('nav[aria-label="Chapters"],nav[aria-label="Stories"]');
  const sections = Array.from(source.querySelectorAll("section[id]"));
  if (!oldNav || sections.length < 2) return;
  const title = source.querySelector("h1")?.textContent?.trim() || document.title;
  const description = Array.from(source.children).filter(el => el.tagName === "P").slice(0, 2).map(el => el.textContent.trim());
  const chapterNames = sections.map((section, i) => section.querySelector("h2,h3")?.textContent?.trim() || "Section " + (i + 1));
  const make = (tag, cls, value) => {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    if (value != null) el.textContent = value;
    return el;
  };
  const reader = make("main", "reader-main");
  reader.id = "main-content";
  const crumbs = make("nav", "breadcrumbs");
  crumbs.setAttribute("aria-label", "Breadcrumb");
  const back = make("a", "", "← Library");
  back.href = "/explore/library";
  crumbs.append(back);
  reader.append(crumbs);
  const cover = make("section", "reader-cover");
  const coverCopy = make("div", "reader-cover-copy");
  coverCopy.append(make("p", "reader-kicker", "✦ COMPLETE OFFLINE CLASSIC"));
  const h1 = make("h1", "", title);
  h1.id = "book-title";
  coverCopy.append(h1);
  for (const line of description) coverCopy.append(make("p", "reader-summary", line));
  cover.append(coverCopy);
  reader.append(cover);
  const layout = make("div", "reader-layout");
  const sidebar = make("aside", "reader-sidebar");
  sidebar.setAttribute("aria-label", "Reading controls");
  const tools = make("section", "reader-toolbox");
  tools.append(make("p", "reader-eyebrow", "MAKE IT YOURS"), make("h2", "", "Reading tools"));
  const sizeRow = make("div", "reader-settings-row");
  sizeRow.append(make("span", "reader-setting-name", "Text size"));
  const buttons = make("div", "reader-size-buttons");
  const smaller = make("button", "", "A−"); smaller.id = "reader-smaller"; smaller.type = "button";
  const size = make("output", "", "100%"); size.id = "reader-size";
  const larger = make("button", "", "A+"); larger.id = "reader-larger"; larger.type = "button";
  buttons.append(smaller, size, larger); sizeRow.append(buttons); tools.append(sizeRow);
  const themes = make("fieldset", "reader-themes");
  themes.append(make("legend", "", "Page colors"));
  for (const [value, name] of [["paper", "Paper"], ["night", "Night"], ["contrast", "High contrast"]]) {
    const label = make("label");
    const radio = document.createElement("input");
    radio.type = "radio"; radio.name = "reading-theme"; radio.value = value; radio.checked = value === "paper";
    label.append(radio, make("span", "reader-swatch reader-swatch-" + value), document.createTextNode(" " + name));
    themes.append(label);
  }
  tools.append(themes, make("p", "reader-tool-note", "Reading settings stay on this page. No accounts or tracking."));
  sidebar.append(tools);
  const toc = make("nav", "reader-chapter-nav");
  toc.setAttribute("aria-label", "Table of contents");
  toc.append(make("p", "reader-eyebrow", "READ AT YOUR OWN PACE"), make("h2", "", "Contents"));
  const ol = make("ol"); ol.id = "reader-toc";
  chapterNames.forEach((name, i) => {
    const li = make("li");
    const button = make("button", "", name);
    button.type = "button"; button.dataset.openChapter = String(i + 1);
    li.append(button); ol.append(li);
  });
  toc.append(ol); sidebar.append(toc); layout.append(sidebar);
  const book = make("div", "reader-book");
  const top = make("div", "reader-book-top");
  const status = make("div");
  status.append(make("p", "reader-eyebrow", "YOUR CURRENT PAGE"));
  const progressCopy = make("p", "reader-progress-copy", "Chapter 1 of " + sections.length + " · " + chapterNames[0]);
  progressCopy.id = "reader-progress-copy"; progressCopy.setAttribute("role", "status");
  status.append(progressCopy);
  const progress = document.createElement("progress");
  progress.id = "reader-progress"; progress.max = sections.length; progress.value = 1;
  progress.setAttribute("aria-label", "Reading progress");
  top.append(status, progress); book.append(top);
  const paper = make("article", "reader-paper");
  paper.setAttribute("aria-label", "Complete text of " + title);
  paper.append(make("div", "reader-paper-decoration", "✦ ✧ ✦"));
  sections.forEach((section, i) => {
    section.classList.add("reader-chapter");
    section.id = "chapter-" + (i + 1);
    section.dataset.chapter = String(i + 1);
    const heading = section.querySelector("h2,h3");
    if (heading) { heading.id = "chapter-title-" + (i + 1); heading.tabIndex = -1; }
    section.prepend(make("p", "reader-chapter-number", "CHAPTER " + (i + 1) + " OF " + sections.length));
    paper.append(section);
  });
  book.append(paper);
  const pager = make("div", "reader-pager");
  const prev = make("button", "", "← Previous chapter"); prev.id = "reader-previous"; prev.type = "button";
  const page = make("span", "", "1 / " + sections.length); page.id = "reader-page-label";
  const next = make("button", "", "Next chapter →"); next.id = "reader-next"; next.type = "button";
  pager.append(prev, page, next); book.append(pager);
  const footer = source.querySelector("footer");
  if (footer) { const note = make("aside", "reader-note"); note.append(footer); book.append(note); }
  layout.append(book); reader.append(layout);
  const bottom = make("nav", "reader-bottom-nav");
  const library = make("a", "", "← Back to the Library"); library.href = "/explore/library";
  bottom.append(library); reader.append(bottom);
  source.replaceWith(reader);
  document.body.classList.add("interior-page", "reader-page");
  document.body.dataset.readerTheme = "paper";
  document.body.dataset.readerUnit = "Chapter";
})();
