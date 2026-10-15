// SPDX-License-Identifier: AGPL-3.0-only
"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const game = require("../frontend/assets/word-workshop-engine.js");

test("four distinct worlds and sixteen curated real-word puzzles", () => {
  assert.equal(game.WORLDS.length, 4);
  assert.equal(game.LEVELS.length, 16);
  for (let i = 0; i < game.LEVELS.length; i += 1) {
    const p = game.createPuzzle(i);
    assert.equal(p.slots.length, p.level.word.length);
    assert.ok(/^[A-Z]{3,8}$/.test(p.level.word));
    assert.ok(p.level.clue.length > 10);
    assert.equal(p.pool.length, p.level.word.length + p.level.extras.length);
    assert.equal(new Set(p.order).size, p.pool.length);
    assert.equal(game.check(p).filled, false);
    assert.equal(game.check(p).correct, false);
    assert.equal(p.level.world, Math.floor(i / 4));
    assert.notEqual(p.order.slice(0, p.level.word.length)
      .map(id => p.pool[id].letter).join(""), p.level.word,
      "tile tray must not start with the solved answer");
  }
});

test("all words can be assembled with letter tiles, even repeated letters", () => {
  for (let i = 0; i < game.LEVELS.length; i += 1) {
    let puzzle = game.createPuzzle(i);
    const initialSlots = puzzle.slots;
    for (let j = 0; j < puzzle.level.word.length; j += 1) {
      const wanted = puzzle.level.word[j];
      const candidate = puzzle.pool.find(tile =>
        tile.letter === wanted && !puzzle.slots.includes(tile.id));
      assert.ok(candidate, "available letter " + wanted);
      puzzle = game.placeNext(puzzle, candidate.id);
    }
    assert.equal(initialSlots.every(slot => slot === null), true, "immutable previous board");
    const result = game.check(puzzle);
    assert.equal(result.filled, true);
    assert.equal(result.correct, true, puzzle.level.word + " is buildable");
    assert.equal(result.built, puzzle.level.word);
    assert.equal(game.hint(puzzle).changed, false);
  }
});

test("tile placement can swap slots, remove tiles and clear without mutation", () => {
  const start = game.createPuzzle(0);
  let p = game.placeAt(start, start.pool[1].id, 0);
  p = game.placeAt(p, start.pool[2].id, 1);
  assert.equal(game.placeAt(p, 999, 1), p, "reject invalid tile");
  assert.equal(game.placeAt(p, 0, -1), p, "reject invalid destination");
  const before = p.slots.slice();
  p = game.placeAt(p, start.pool[1].id, 1);
  assert.equal(p.slots[1], 1);
  assert.equal(p.slots[0], 2, "swap instead of duplicating IDs");
  assert.deepEqual(before, [1, 2, null]);
  assert.equal(start.slots.every(x => x === null), true);
  const afterRemove = game.removeAt(p, 0);
  assert.equal(afterRemove.slots[0], null);
  assert.equal(p.slots[0], 2);
  assert.deepEqual(game.clear(afterRemove).slots, [null, null, null]);
});

test("hints identify and fix one missing or misplaced letter", () => {
  for (let i = 0; i < game.LEVELS.length; i += 1) {
    let p = game.createPuzzle(i);
    let safety = 0;
    while (!game.check(p).correct) {
      const response = game.hint(p);
      assert.equal(response.changed, true, "hint moves puzzle forward");
      assert.notEqual(response.puzzle, p);
      p = response.puzzle;
      assert.ok(++safety <= p.level.word.length + 2,
        p.level.word + " should be solved by bounded hints");
    }
    assert.equal(game.check(p).correct, true);
  }
});

test("hint can correct a fully-filled scrambled word and repeated letters", () => {
  let p = game.createPuzzle(7); // BLOOM contains two Os.
  for (const id of p.order.slice(0, p.slots.length)) p = game.placeNext(p, id);
  let safety = 0;
  while (!game.check(p).correct && safety < 20) {
    const hint = game.hint(p);
    assert.equal(hint.changed, true);
    p = hint.puzzle;
    safety += 1;
  }
  assert.equal(game.check(p).correct, true);
  assert.ok(safety <= p.level.word.length + 2);
});

test("shuffle only changes available tile order, not placed letters", () => {
  const p = game.createPuzzle(4);
  const a = game.placeNext(p, p.order[0]);
  const b = game.shuffle(a, 12345);
  assert.deepEqual(b.slots, a.slots);
  assert.deepEqual(b.pool, a.pool);
  assert.deepEqual(b.order.slice().sort(), a.order.slice().sort());
  assert.throws(() => game.shuffle(a, "123"), TypeError);
  assert.deepEqual(a.order, p.order);
});

test("awards reward independent completion and mistakes or hints", () => {
  assert.equal(game.stars(0, 0), 3);
  assert.equal(game.stars(1, 0), 2);
  assert.equal(game.stars(0, 1), 2);
  assert.equal(game.stars(3, 0), 1);
  assert.equal(game.stars(0, 3), 1);
  assert.throws(() => game.createPuzzle(-1), RangeError);
  assert.throws(() => game.createPuzzle(16), RangeError);
  assert.throws(() => game.createPuzzle(2.2), RangeError);
});
