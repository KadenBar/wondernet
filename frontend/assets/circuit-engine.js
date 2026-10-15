// SPDX-License-Identifier: AGPL-3.0-only
// Circuit Garden has no backend state, accounts, random network calls or storage.
(function (root) {
  "use strict";

  const NORTH = 1, EAST = 2, SOUTH = 4, WEST = 8;
  const DIRECTIONS = [
    { bit: NORTH, opposite: SOUTH, dr: -1, dc: 0 },
    { bit: EAST, opposite: WEST, dr: 0, dc: 1 },
    { bit: SOUTH, opposite: NORTH, dr: 1, dc: 0 },
    { bit: WEST, opposite: EAST, dr: 0, dc: -1 }
  ];
  const BASE = { source: NORTH, flower: NORTH, straight: NORTH | SOUTH,
    bend: NORTH | EAST, tee: NORTH | EAST | SOUTH, cross: 15 };
  const LEVELS = [
    { name: "First Spark", size: 4, note: "One little bloom. Follow the path!",
      source: "3,0", flowers: ["0,3"],
      paths: ["3,0 3,1 2,1 1,1 1,2 0,2 0,3"] },
    { name: "The Long Way", size: 4, note: "Every corner matters.",
      source: "0,0", flowers: ["3,3"],
      paths: ["0,0 0,1 1,1 1,2 2,2 2,3 3,3"] },
    { name: "Two Buds", size: 5, note: "A split wire can feed two flowers.",
      source: "4,0", flowers: ["0,1", "1,4"],
      paths: ["4,0 3,0 2,0 2,1 2,2 1,2 0,2 0,1",
              "2,2 2,3 1,3 1,4"] },
    { name: "Side Quest", size: 5, note: "Two branches, one battery.",
      source: "0,4", flowers: ["4,1", "3,4"],
      paths: ["0,4 1,4 1,3 2,3 2,2 3,2 4,2 4,1",
              "2,3 3,3 3,4"] },
    { name: "Sunrise", size: 5, note: "Find the best way through the garden.",
      source: "4,4", flowers: ["0,0", "0,4"],
      paths: ["4,4 4,3 3,3 2,3 2,2 1,2 1,1 1,0 0,0",
              "1,2 0,2 0,3 0,4"] },
    { name: "Greenhouse", size: 6, note: "There is more than one route to a bloom.",
      source: "5,0", flowers: ["0,1", "3,5"],
      paths: ["5,0 5,1 4,1 3,1 3,2 2,2 1,2 1,1 0,1",
              "3,2 3,3 4,3 4,4 3,4 3,5"] },
    { name: "The Fork", size: 6, note: "The turns get trickier now.",
      source: "0,0", flowers: ["5,1", "5,5"],
      paths: ["0,0 0,1 1,1 1,2 2,2 2,1 3,1 4,1 5,1",
              "2,2 3,2 3,3 4,3 4,4 5,4 5,5"] },
    { name: "Triple Bloom", size: 6, note: "Three flowers. Two branching points.",
      source: "5,5", flowers: ["0,0", "0,4", "4,0"],
      paths: ["5,5 5,4 4,4 3,4 3,3 2,3 2,2 2,1 1,1 0,1 0,0",
              "2,3 1,3 0,3 0,4",
              "2,1 2,0 3,0 4,0"] },
    { name: "Wild Vines", size: 6, note: "Keep all three paths alive.",
      source: "0,5", flowers: ["5,0", "5,5", "0,0"],
      paths: ["0,5 1,5 2,5 2,4 2,3 3,3 3,4 4,4 4,5 5,5",
              "3,3 3,2 4,2 4,1 5,1 5,0",
              "2,3 1,3 1,2 0,2 0,1 0,0"] },
    { name: "Grand Garden", size: 6, note: "Last puzzle. Grow the whole garden!",
      source: "5,2", flowers: ["0,0", "0,5", "5,5"],
      paths: ["5,2 4,2 3,2 2,2 2,1 1,1 1,0 0,0",
              "2,2 1,2 1,3 0,3 0,4 0,5",
              "3,2 3,3 4,3 4,4 5,4 5,5"] }
  ];

  function turn(mask, steps = 1) {
    for (let i = 0; i < ((steps % 4) + 4) % 4; i += 1) {
      mask = ((mask << 1) & 15) | (mask >> 3);
    }
    return mask;
  }

  function coord(value, size) {
    const match = /^(\d+),(\d+)$/.exec(value);
    if (!match) throw new Error("Invalid garden coordinate");
    const row = Number(match[1]), col = Number(match[2]);
    if (row >= size || col >= size) throw new Error("Garden coordinate out of range");
    return row * size + col;
  }

  function kind(mask) {
    const count = DIRECTIONS.reduce((sum, d) => sum + ((mask & d.bit) ? 1 : 0), 0);
    if (count === 4) return "cross";
    if (count === 3) return "tee";
    if (count === 2) return mask === 5 || mask === 10 ? "straight" : "bend";
    if (count === 1) return "flower";
    throw new Error("Invalid tile connections");
  }

  function solvedRotation(type, mask) {
    for (let rotation = 0; rotation < 4; rotation += 1) {
      if (turn(BASE[type], rotation) === mask) return rotation;
    }
    throw new Error("Tile cannot be oriented");
  }

  function createBoard(number) {
    if (!Number.isInteger(number) || number < 0 || number >= LEVELS.length) {
      throw new RangeError("No such Circuit Garden level");
    }
    const def = LEVELS[number], size = def.size;
    const links = Array.from({ length: size * size }, () => 0);
    for (const path of def.paths) {
      const coords = path.trim().split(/\s+/).map(text => coord(text, size));
      for (let j = 1; j < coords.length; j += 1) {
        const a = coords[j - 1], b = coords[j];
        const dr = Math.floor(b / size) - Math.floor(a / size);
        const dc = b % size - a % size;
        const direction = DIRECTIONS.find(d => d.dr === dr && d.dc === dc);
        if (!direction) throw new Error("Path must follow adjacent cells");
        links[a] |= direction.bit;
        links[b] |= direction.opposite;
      }
    }
    const source = coord(def.source, size);
    const flowers = def.flowers.map(value => coord(value, size));
    if (new Set(flowers).size !== flowers.length || flowers.includes(source)) throw new Error("Bad flower locations");
    if (kind(links[source]) !== "flower" || flowers.some(i => kind(links[i]) !== "flower")) {
      throw new Error("Source and flowers must be endpoints");
    }
    const tiles = links.map((mask, index) => {
      if (!mask) {
        const row = Math.floor(index / size), col = index % size;
        return { type: (row * 7 + col * 11 + number) % 6 === 0 ? "rock" : "grass",
          row, col, rotation: 0, mask: 0, solution: 0, fixed: true };
      }
      const row = Math.floor(index / size), col = index % size;
      const type = index === source ? "source" : flowers.includes(index) ? "flower" : kind(mask);
      const solution = solvedRotation(type, mask);
      const offset = type === "source" || type === "cross" ? 0 :
        type === "straight" ? 1 : 1 + (row * 5 + col * 3 + number) % 3;
      const rotation = (solution + offset) % 4;
      return { type, row, col, rotation, mask: turn(BASE[type], rotation),
        solution, fixed: type === "source" || type === "cross" };
    });
    const par = tiles.reduce((sum, tile) => {
      if (tile.fixed) return sum;
      const rotations = (tile.solution - tile.rotation + 4) % 4;
      return sum + rotations;
    }, 0);
    const board = { size, tiles, source, flowers, par, number,
      name: def.name, note: def.note };
    const test = evaluate(tiles, size, source, flowers);
    if (test.complete) throw new Error("Puzzle starts completed");
    return board;
  }

  function evaluate(tiles, size, source, flowers) {
    const powered = new Set([source]), queue = [source];
    for (let q = 0; q < queue.length; q += 1) {
      const current = queue[q], tile = tiles[current];
      for (const direction of DIRECTIONS) {
        if (!(tile.mask & direction.bit)) continue;
        const row = tile.row + direction.dr, col = tile.col + direction.dc;
        if (row < 0 || row >= size || col < 0 || col >= size) continue;
        const next = row * size + col, neighbor = tiles[next];
        if (!(neighbor.mask & direction.opposite) || powered.has(next)) continue;
        powered.add(next);
        queue.push(next);
      }
    }
    const blooms = flowers.filter(i => powered.has(i));
    return { powered, blooms, complete: blooms.length === flowers.length };
  }

  function rotate(tiles, index, steps = 1) {
    if (!Number.isInteger(index) || index < 0 || index >= tiles.length ||
        tiles[index].fixed || !Number.isInteger(steps)) return tiles;
    return tiles.map((tile, i) => i === index ?
      { ...tile, rotation: (tile.rotation + steps + 4) % 4,
        mask: turn(BASE[tile.type], tile.rotation + steps) } : tile);
  }

  function hint(tiles) {
    return tiles.findIndex(t => !t.fixed && t.mask !== turn(BASE[t.type], t.solution));
  }

  function stars(moves, par, hints) {
    if (hints === 0 && moves <= par + 2) return 3;
    if (hints <= 1 && moves <= par + Math.ceil(par * .7)) return 2;
    return 1;
  }

  const api = Object.freeze({ LEVELS, DIRECTIONS, BASE, turn, createBoard, evaluate, rotate, hint, stars });
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root && typeof root === "object") root.CircuitGardenEngine = api;
})(typeof window === "undefined" ? null : window);
