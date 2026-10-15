// SPDX-License-Identifier: AGPL-3.0-only
"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const engine = require("../frontend/assets/word-workshop-engine.js");

class Element {
  constructor(tag = "div") {
    this.tagName = tag.toUpperCase();
    this.className = "";
    this.dataset = {};
    this.style = {};
    this.children = [];
    this.parentNode = null;
    this.handlers = new Map();
    this.textContent = "";
    this.disabled = false;
    this.capturedPointer = null;
    this.removed = false;
    this.classList = {
      add: (...names) => {
        const all = new Set(this.className.split(/\s+/).filter(Boolean));
        for (const name of names) all.add(name);
        this.className = [...all].join(" ");
      },
      remove: (...names) => {
        const all = new Set(this.className.split(/\s+/).filter(Boolean));
        for (const name of names) all.delete(name);
        this.className = [...all].join(" ");
      },
      contains: name => this.className.split(/\s+/).includes(name)
    };
  }
  addEventListener(type, fn) {
    if (!this.handlers.has(type)) this.handlers.set(type, []);
    this.handlers.get(type).push(fn);
  }
  fire(type, properties = {}) {
    const e = {
      pointerId: 3, button: 0, isPrimary: true,
      clientX: 12, clientY: 12, cancelable: true,
      prevented: false, preventDefault() { this.prevented = true; },
      target: this, ...properties
    };
    for (const handler of this.handlers.get(type) || []) handler(e);
    return e;
  }
  setPointerCapture(id) { this.capturedPointer = id; }
  hasPointerCapture(id) { return this.capturedPointer === id; }
  releasePointerCapture(id) {
    if (!this.hasPointerCapture(id)) return;
    this.capturedPointer = null;
    this.fire("lostpointercapture", { pointerId: id });
  }
  setAttribute(name, value) {
    if (!this.attrs) this.attrs = {};
    this.attrs[name] = String(value);
  }
  append(...children) {
    for (const child of children) {
      child.parentNode = this;
      this.children.push(child);
    }
  }
  appendChild(child) { this.append(child); return child; }
  replaceChildren(...children) {
    for (const child of this.children) child.parentNode = null;
    this.children = [];
    this.append(...children);
  }
  remove() {
    this.removed = true;
    if (!this.parentNode) return;
    this.parentNode.children = this.parentNode.children.filter(x => x !== this);
    this.parentNode = null;
  }
  contains(node) {
    for (let current = node; current; current = current.parentNode) {
      if (current === this) return true;
    }
    return false;
  }
  closest(selector) {
    const cls = selector.startsWith(".") ? selector.slice(1) : selector;
    for (let current = this; current; current = current.parentNode) {
      if (current.classList.contains(cls)) return current;
    }
    return null;
  }
  querySelectorAll(selector) {
    const results = [];
    for (const child of this.children) {
      if (selector.startsWith("button") && child.tagName === "BUTTON" &&
          (!selector.includes(":not(:disabled)") || !child.disabled)) results.push(child);
      results.push(...child.querySelectorAll(selector));
    }
    return results;
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
  focus() {}
  scrollIntoView() {}
  get offsetWidth() { return 120; }
}

function makeApp(touchMode = false) {
  const names = ["ww-tray","ww-slots","ww-feedback","ww-clue-text","ww-emoji",
    "ww-letter-count","ww-world","ww-stage-title","ww-round","ww-completed",
    "ww-check","ww-hint","ww-shuffle","ww-clear","ww-win","ww-win-emoji",
    "ww-win-description","ww-stars","ww-next","ww-world-list","ww-precision"];
  const buttons = new Set(["ww-check","ww-hint","ww-shuffle","ww-clear","ww-next","ww-precision"]);
  const elements = Object.fromEntries(names.map(id =>
    [id, new Element(buttons.has(id) ? "button" : "div")]));
  const body = new Element("body");
  const timers = [];
  let hit = null;
  const document = {
    body,
    getElementById: id => elements[id] || null,
    createElement: name => new Element(name),
    elementFromPoint: () => hit
  };
  const js = fs.readFileSync(path.join(__dirname, "../frontend/assets/word-workshop.js"), "utf8");
  const testWindow = { WordWorkshopEngine: engine };
  if (touchMode) testWindow.ontouchstart = null;
  vm.runInNewContext(js, {
    window: testWindow, document,
    setTimeout: fn => timers.push(fn), console
  }, { filename: "word-workshop.js" });
  const tray = elements["ww-tray"], slots = elements["ww-slots"];
  return {
    document, elements, tray, slots, timers,
    hitSlot(index) { hit = slots.children[index]; },
    clearHit() { hit = null; },
    pointer(tile, type, x = 12, y = 12, data = {}) {
      return tile.fire(type, { clientX: x, clientY: y, ...data });
    },
    flushTimers() { while (timers.length) timers.shift()(); }
  };
}

test("touch pointer drag drops an available letter into the selected slot, not the first slot", () => {
  const app = makeApp();
  const tile = app.tray.children[0], letter = tile.textContent;
  assert.equal(app.slots.children.length, 3);
  app.pointer(tile, "pointerdown", 12, 12, { pointerType: "touch" });
  assert.equal(tile.hasPointerCapture(3), true);
  app.hitSlot(1);
  app.pointer(tile, "pointermove", 140, 180, { pointerType: "touch" });
  assert.equal(app.document.body.children.length, 1, "floating letter is visible");
  assert.equal(app.slots.children[1].classList.contains("ww-drop-target"), true);
  app.pointer(tile, "pointerup", 140, 180, { pointerType: "touch" });
  assert.equal(app.document.body.children.length, 0, "floating letter cleaned up");
  assert.equal(app.slots.children[1].textContent, letter);
  assert.equal(app.slots.children[0].textContent, "");
  assert.equal(app.tray.children.length, 3, "used tile removed from tray");
  assert.equal(tile.hasPointerCapture(3), false);
});

test("short touch tap still places the tile in the first empty word space", () => {
  const app = makeApp();
  const tile = app.tray.children[0], letter = tile.textContent;
  app.pointer(tile, "pointerdown", 12, 12, { pointerType: "touch" });
  app.pointer(tile, "pointermove", 15, 15, { pointerType: "touch" });
  assert.equal(app.document.body.children.length, 0, "short movement is not a drag");
  app.pointer(tile, "pointerup", 15, 15, { pointerType: "touch" });
  tile.fire("click");
  assert.equal(app.slots.children[0].textContent, letter);
  assert.equal(app.slots.children[1].textContent, "");
});

test("a released drag outside slots cancels, suppressing a stray click", () => {
  const app = makeApp();
  const tile = app.tray.children[0];
  app.pointer(tile, "pointerdown");
  app.clearHit();
  app.pointer(tile, "pointermove", 270, 270);
  app.pointer(tile, "pointerup", 270, 270);
  tile.fire("click");
  assert.equal(app.slots.children.every(x => !x.textContent), true);
  assert.equal(app.tray.children.length, 4);
  assert.equal(app.document.body.children.length, 0);
  app.flushTimers();
  tile.fire("click");
  assert.ok(app.slots.children[0].textContent, "later real tap still works");
});

test("canceling a touch drag removes the ghost and highlight without placing it", () => {
  const app = makeApp();
  const tile = app.tray.children[0];
  app.pointer(tile, "pointerdown", 10, 10, { pointerType: "touch" });
  app.hitSlot(2);
  app.pointer(tile, "pointermove", 150, 150, { pointerType: "touch" });
  assert.equal(app.slots.children[2].classList.contains("ww-drop-target"), true);
  app.pointer(tile, "pointercancel", 150, 150, { pointerType: "touch" });
  assert.equal(app.document.body.children.length, 0);
  assert.equal(app.slots.children[2].classList.contains("ww-drop-target"), false);
  assert.equal(app.slots.children.every(x => !x.textContent), true);
  assert.equal(tile.hasPointerCapture(3), false);
});

test("a second pointer cannot steal an ongoing primary drag", () => {
  const app = makeApp();
  const tile = app.tray.children[0];
  app.pointer(tile, "pointerdown", 10, 10, { pointerType: "touch" });
  app.pointer(tile, "pointerdown", 300, 300, { pointerId: 8, isPrimary: false, pointerType: "touch" });
  app.hitSlot(0);
  app.pointer(tile, "pointermove", 150, 150, { pointerId: 8, pointerType: "touch" });
  assert.equal(app.document.body.children.length, 0);
  app.pointer(tile, "pointermove", 150, 150, { pointerType: "touch" });
  assert.equal(app.document.body.children.length, 1);
  app.pointer(tile, "pointerup", 150, 150, { pointerType: "touch" });
  assert.ok(app.slots.children[0].textContent);
});


function touch(identifier, x, y) {
  return { identifier, clientX: x, clientY: y };
}
function fireTouch(tile, type, current, touches = []) {
  return tile.fire(type, { touches, changedTouches: [current] });
}

test("touchstart prevents browser scrolling before drag movement", () => {
  const app = makeApp(true);
  const tile = app.tray.children[0];
  const start = touch(1, 12, 12);
  const event = fireTouch(tile, "touchstart", start, [start]);
  assert.equal(event.prevented, true, "touchstart must cancel native page scroll");
  const move = touch(1, 200, 155);
  app.hitSlot(2);
  const moved = fireTouch(tile, "touchmove", move, [move]);
  assert.equal(moved.prevented, true, "touchmove must prevent page scrolling");
  assert.equal(app.document.body.children.length, 1, "drag ghost follows finger");
  assert.equal(app.slots.children[2].classList.contains("ww-drop-target"), true);
  const released = fireTouch(tile, "touchend", move, []);
  assert.equal(released.prevented, true);
  assert.equal(app.slots.children[2].textContent, tile.textContent);
  assert.equal(app.document.body.children.length, 0);
  tile.fire("click");
  assert.equal(app.slots.children[0].textContent, "", "compatibility click must not place again");
});

test("short finger tap places only one letter without a native click", () => {
  const app = makeApp(true);
  const tile = app.tray.children[0], letter = tile.textContent;
  const start = touch(9, 30, 30);
  fireTouch(tile, "touchstart", start, [start]);
  const end = touch(9, 34, 33);
  fireTouch(tile, "touchend", end, []);
  assert.equal(app.slots.children[0].textContent, letter);
  tile.fire("click");
  assert.equal(app.slots.children[1].textContent, "", "must not place a second tile");
});

test("touchcancel leaves the board alone and cleans the preview", () => {
  const app = makeApp(true);
  const tile = app.tray.children[0], start = touch(1, 20, 20);
  fireTouch(tile, "touchstart", start, [start]);
  app.hitSlot(1);
  fireTouch(tile, "touchmove", touch(1, 250, 190), [touch(1, 250, 190)]);
  assert.equal(app.document.body.children.length, 1);
  fireTouch(tile, "touchcancel", touch(1, 250, 190), []);
  assert.equal(app.document.body.children.length, 0);
  assert.equal(app.slots.children[1].classList.contains("ww-drop-target"), false);
  assert.equal(app.slots.children.every(x => !x.textContent), true);
});

test("precise placement lets users tap a tile then choose an arbitrary slot", () => {
  const app = makeApp();
  app.elements["ww-precision"].fire("click");
  assert.equal(app.elements["ww-precision"].attrs["aria-pressed"], "true");
  const tile = app.tray.children[0], letter = tile.textContent;
  tile.fire("click");
  assert.equal(app.slots.children.every(x => !x.textContent), true,
    "selected tile should not be placed automatically");
  const chosen = app.slots.children[2];
  chosen.fire("click");
  assert.equal(app.slots.children[2].textContent, letter);
  assert.equal(app.slots.children[0].textContent, "");
  assert.equal(app.elements["ww-precision"].attrs["aria-pressed"], "true");
  app.elements["ww-precision"].fire("click");
  assert.equal(app.elements["ww-precision"].attrs["aria-pressed"], "false");
});

test("precise placement also works using a phone's touch tap", () => {
  const app = makeApp(true);
  app.elements["ww-precision"].fire("click");
  const tile = app.tray.children[0], letter = tile.textContent;
  const start = touch(4, 24, 24);
  fireTouch(tile, "touchstart", start, [start]);
  fireTouch(tile, "touchend", start, []);
  assert.equal(app.slots.children.every(x => !x.textContent), true);
  app.slots.children[1].fire("click");
  assert.equal(app.slots.children[1].textContent, letter);
});
