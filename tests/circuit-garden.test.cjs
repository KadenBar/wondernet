// SPDX-License-Identifier: AGPL-3.0-only
"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const game = require("../frontend/assets/circuit-engine.js");

test("quarter-turns have consistent direction and cycle back to the start", () => {
  assert.equal(game.turn(1, 1), 2);
  assert.equal(game.turn(2, 1), 4);
  assert.equal(game.turn(4, 1), 8);
  assert.equal(game.turn(8, 1), 1);
  assert.equal(game.turn(3, 4), 3);
  assert.equal(game.turn(3, -1), 9);
});

test("ten handcrafted levels begin unsolved and are all solvable", () => {
  assert.equal(game.LEVELS.length, 10);
  for (let level = 0; level < game.LEVELS.length; level += 1) {
    const puzzle = game.createBoard(level);
    assert.equal(puzzle.tiles.length, puzzle.size ** 2, "correct board size");
    assert.ok(puzzle.par > 0, "some turns required");
    assert.ok(puzzle.tiles[puzzle.source].fixed, "battery stays fixed");
    assert.equal(puzzle.tiles[puzzle.source].type, "source");
    const state = game.evaluate(puzzle.tiles, puzzle.size, puzzle.source, puzzle.flowers);
    assert.equal(state.complete, false, puzzle.name + " begins unfinished");
    assert.ok(puzzle.flowers.length >= 1);
    for (const flower of puzzle.flowers) {
      assert.equal(puzzle.tiles[flower].type, "flower");
    }
    let turns = 0;
    let tiles = puzzle.tiles;
    for (let cell = 0; cell < tiles.length; cell += 1) {
      const piece = tiles[cell];
      if (piece.fixed) continue;
      while (tiles[cell].rotation !== piece.solution) {
        tiles = game.rotate(tiles, cell);
        turns += 1;
        assert.ok(turns < 500, "bounded solve");
      }
    }
    assert.equal(turns, puzzle.par, "calculated ideal number of clockwise turns");
    const result = game.evaluate(tiles, puzzle.size, puzzle.source, puzzle.flowers);
    assert.equal(result.complete, true, puzzle.name + " can be fully powered");
    assert.equal(result.blooms.length, puzzle.flowers.length);
    assert.equal(game.hint(tiles), -1, "no more hints once solved");
    assert.equal(game.stars(turns, puzzle.par, 0), 3, "ideal play earns three stars");
  }
});

test("a rotation never mutates earlier board objects or fixed tiles", () => {
  const board = game.createBoard(0);
  const original = board.tiles;
  assert.equal(game.rotate(original, board.source), original, "battery cannot rotate");
  assert.equal(game.rotate(original, -1), original, "invalid index cannot rotate");
  const i = game.hint(original);
  assert.ok(i >= 0);
  const altered = game.rotate(original, i);
  assert.notEqual(altered, original);
  assert.notEqual(altered[i].mask, original[i].mask);
  assert.equal(original[i].rotation, board.tiles[i].rotation);
});

test("levels reject invalid indexes and no user state is serialized", () => {
  assert.throws(() => game.createBoard(-1), RangeError);
  assert.throws(() => game.createBoard(10), RangeError);
  assert.throws(() => game.createBoard(1.5), RangeError);
  assert.equal(game.stars(999, 5, 8), 1);
  const level = game.createBoard(5);
  assert.equal(level.flowers.length, 2);
  assert.equal(game.createBoard(7).flowers.length, 3);
  assert.equal(game.createBoard(9).flowers.length, 3);
});
