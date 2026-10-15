// SPDX-License-Identifier: AGPL-3.0-only
"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

class Node {
  constructor(text = "") {
    this.textContent = text;
    this.disabled = false;
    this.hidden = false;
    this.attrs = {};
    this.handlers = new Map();
    this.dataset = {};
    this.styleValues = {};
    this.style = { setProperty: (name, value) => { this.styleValues[name] = value; } };
    this.focused = false;
    this.scrolled = false;
  }
  addEventListener(type, fn) {
    if (!this.handlers.has(type)) this.handlers.set(type, []);
    this.handlers.get(type).push(fn);
  }
  fire(type, properties = {}) {
    const event = {
      target: this,
      preventDefault() { this.prevented = true; },
      ...properties
    };
    for (const callback of this.handlers.get(type) || []) callback(event);
    return event;
  }
  setAttribute(name, value) { this.attrs[name] = String(value); }
  removeAttribute(name) { delete this.attrs[name]; }
  querySelector(name) {
    if (name === "h2") return this.heading;
    return null;
  }
  focus() { this.focused = true; }
  scrollIntoView() { this.scrolled = true; }
}

function app(initialHash = "", unit = "Chapter") {
  const names = ["reader-previous","reader-next","reader-progress","reader-progress-copy",
    "reader-page-label","reader-smaller","reader-larger","reader-size"];
  const ids = Object.fromEntries(names.map(x => [x, new Node()]));
  const chapters = [
    "The Sky Goes Quiet", "A Map of Missing Lights", "The Fog Collector",
    "A Small, Brave Spark", "Room for Every Star"
  ].map((text, i) => {
    const node = new Node();
    node.dataset.chapter = String(i + 1);
    node.heading = new Node(text);
    return node;
  });
  const toc = chapters.map((_, i) => {
    const node = new Node();
    node.dataset.openChapter = String(i + 1);
    return node;
  });
  const themes = ["paper","night","contrast"].map(value => {
    const node = new Node();
    node.value = value;
    node.checked = value === "paper";
    return node;
  });
  const paper = new Node();
  const bookTop = new Node();
  const body = new Node();
  body.dataset.readerTheme = "paper";
  body.dataset.readerUnit = unit;
  const document = new Node();
  document.body = body;
  document.getElementById = key => ids[key] || null;
  document.querySelectorAll = selector => {
    if (selector === ".reader-chapter") return chapters;
    if (selector === "[data-open-chapter]") return toc;
    if (selector === 'input[name="reading-theme"]') return themes;
    return [];
  };
  document.querySelector = selector => {
    if (selector === ".reader-paper") return paper;
    if (selector === ".reader-book-top") return bookTop;
    return null;
  };
  const window = new Node();
  window.location = { hash: initialHash };
  window.history = { replaceState: (_, __, fragment) => { window.location.hash = fragment; } };
  const js = fs.readFileSync(
    path.join(__dirname, "../frontend/assets/book-reader.js"), "utf8");
  vm.runInNewContext(js, { document, window }, { filename:"book-reader.js" });
  return { ids, chapters, toc, themes, paper, bookTop, document, window, body };
}

test("only the selected chapter is shown and controls track its location", () => {
  const v = app();
  assert.deepEqual(v.chapters.map(ch => ch.hidden), [false,true,true,true,true]);
  assert.equal(v.ids["reader-progress"].value, 1);
  assert.equal(v.ids["reader-previous"].disabled, true);
  v.ids["reader-next"].fire("click");
  assert.deepEqual(v.chapters.map(ch => ch.hidden), [true,false,true,true,true]);
  assert.equal(v.toc[1].attrs["aria-current"], "true");
  assert.equal(v.toc[0].attrs["aria-current"], undefined);
  assert.equal(v.window.location.hash, "#chapter-2");
  assert.equal(v.bookTop.scrolled, true);
  assert.equal(v.chapters[1].heading.focused, true);
  v.ids["reader-previous"].fire("click");
  assert.equal(v.ids["reader-page-label"].textContent, "1 / 5");
});

test("table of contents opens any chapter and disables Next on last", () => {
  const v = app();
  v.toc[4].fire("click");
  assert.equal(v.ids["reader-progress"].value, 5);
  assert.equal(v.ids["reader-next"].disabled, true);
  assert.equal(v.ids["reader-next"].textContent, "End of story ✓");
  assert.equal(v.chapters[4].hidden, false);
  v.toc[2].fire("click");
  assert.equal(v.ids["reader-next"].disabled, false);
});

test("initial URL chapter and hash navigation work without local storage", () => {
  const v = app("#chapter-3");
  assert.equal(v.chapters[2].hidden, false);
  assert.equal(v.bookTop.scrolled, false, "initial load should not forcibly scroll");
  v.window.location.hash = "#chapter-5";
  v.window.fire("hashchange");
  assert.equal(v.chapters[4].hidden, false);
  assert.equal(v.ids["reader-progress"].value, 5);
  const bad = app("#chapter-9000");
  assert.equal(bad.chapters[0].hidden, false);
});

test("text-size adjustments stop at safe bounds", () => {
  const v = app();
  const label = v.ids["reader-size"];
  assert.equal(label.textContent, "100%");
  assert.equal(v.paper.styleValues["--reader-text-size"], "1.120rem");
  for (let n = 0; n < 20; n += 1) v.ids["reader-larger"].fire("click");
  assert.equal(label.textContent, "160%");
  assert.equal(v.ids["reader-larger"].disabled, true);
  for (let n = 0; n < 20; n += 1) v.ids["reader-smaller"].fire("click");
  assert.equal(label.textContent, "80%");
  assert.equal(v.ids["reader-smaller"].disabled, true);
});

test("changing between paper, night and contrast is local", () => {
  const v = app();
  v.themes[1].checked = true;
  v.themes[1].fire("change");
  assert.equal(v.body.dataset.readerTheme, "night");
  v.themes[2].checked = true;
  v.themes[2].fire("change");
  assert.equal(v.body.dataset.readerTheme, "contrast");
});

test("arrow keys navigate only when not focused on an input or control", () => {
  const v = app();
  const normalTarget = { closest: () => null };
  v.document.fire("keydown", { key: "ArrowRight", target: normalTarget });
  assert.equal(v.ids["reader-progress"].value, 2);
  v.document.fire("keydown", { key: "ArrowLeft", target: normalTarget });
  assert.equal(v.ids["reader-progress"].value, 1);
  const controlTarget = { closest: () => ({ tagName: "INPUT" }) };
  v.document.fire("keydown", { key: "ArrowRight", target: controlTarget });
  assert.equal(v.ids["reader-progress"].value, 1);
});

test("complete classic edition pages display Page labels while original demo still uses Chapter", () => {
  const v = app("", "Page");
  assert.ok(v.ids["reader-progress-copy"].textContent.startsWith("Page 1 of 5"));
  assert.equal(v.ids["reader-next"].textContent, "Next page →");
  v.ids["reader-next"].fire("click");
  assert.ok(v.ids["reader-progress-copy"].textContent.startsWith("Page 2 of 5"));
  assert.equal(v.window.location.hash, "#chapter-2");
  const original = app();
  assert.ok(original.ids["reader-progress-copy"].textContent.startsWith("Chapter 1 of 5"));
  assert.equal(original.ids["reader-next"].textContent, "Next chapter →");
});
