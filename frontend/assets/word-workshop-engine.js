// SPDX-License-Identifier: AGPL-3.0-only
// Word Workshop puzzle data and pure logic. No accounts, browser storage or network.
(function (root) {
  "use strict";

  // Visual prompts are deliberately supplemented by text. These are informal
  // spelling/word-building puzzles, NOT validated systematic phonics lessons.
  const WORLDS = Object.freeze([
    { name: "Critter Corner", icon: "🐾", color: "peach", subtitle: "A few furry and feathered friends" },
    { name: "Garden Patch", icon: "🌻", color: "mint", subtitle: "Things that grow and glow" },
    { name: "Maker's Shed", icon: "🧰", color: "butter", subtitle: "Tools for clever little builders" },
    { name: "Star Lab", icon: "🚀", color: "violet", subtitle: "Words from way up there" }
  ]);

  const LEVELS = Object.freeze([
    { word: "CAT", emoji: "🐈", clue: "A pet that purrs and says meow.", extras: "R", world: 0 },
    { word: "DOG", emoji: "🐕", clue: "A friendly pet that wags its tail.", extras: "E", world: 0 },
    { word: "BIRD", emoji: "🐦", clue: "A feathered friend that may fly and sing.", extras: "S", world: 0 },
    { word: "FROG", emoji: "🐸", clue: "A green jumper who loves ponds.", extras: "T", world: 0 },
    { word: "SUN", emoji: "☀️", clue: "The bright star that warms our planet.", extras: "P", world: 1 },
    { word: "SEED", emoji: "🌱", clue: "Plant this little thing to grow a new plant.", extras: "A", world: 1 },
    { word: "LEAF", emoji: "🍃", clue: "A green part of a plant that catches sunlight.", extras: "T", world: 1 },
    { word: "BLOOM", emoji: "🌼", clue: "When a flower opens, we say it is in...", extras: "R", world: 1 },
    { word: "BOX", emoji: "📦", clue: "A container for keeping and carrying things.", extras: "A", world: 2 },
    { word: "NAIL", emoji: "🔨", clue: "A small piece of metal you can hammer into wood.", extras: "T", world: 2 },
    { word: "BRUSH", emoji: "🖌️", clue: "Use this tool to spread paint.", extras: "A", world: 2 },
    { word: "PAINT", emoji: "🎨", clue: "Colorful liquid used to decorate a picture or wall.", extras: "S", world: 2 },
    { word: "MOON", emoji: "🌙", clue: "The glowing object you often see in the night sky.", extras: "S", world: 3 },
    { word: "STAR", emoji: "⭐", clue: "The Sun is one of these bright space objects.", extras: "E", world: 3 },
    { word: "COMET", emoji: "☄️", clue: "An icy space visitor that can grow a glowing tail.", extras: "P", world: 3 },
    { word: "PLANET", emoji: "🪐", clue: "A world such as Earth, Mars or Jupiter.", extras: "O", world: 3 }
  ]);

  function randomNumber(seed) {
    let value = seed >>> 0;
    return function () {
      value = (Math.imul(value, 1664525) + 1013904223) >>> 0;
      return value / 4294967296;
    };
  }

  function shuffled(ids, seed) {
    const result = ids.slice();
    const random = randomNumber(seed);
    for (let i = result.length - 1; i > 0; i -= 1) {
      const j = Math.floor(random() * (i + 1));
      [result[i], result[j]] = [result[j], result[i]];
    }
    return result;
  }

  function createPuzzle(index) {
    if (!Number.isInteger(index) || index < 0 || index >= LEVELS.length) {
      throw new RangeError("Unknown Word Workshop level");
    }
    const level = LEVELS[index];
    if (!/^[A-Z]{3,8}$/.test(level.word) || !/^[A-Z]{1,4}$/.test(level.extras)) {
      throw new Error("Invalid curated puzzle");
    }
    const pool = (level.word + level.extras).split("").map((letter, id) => ({ id, letter }));
    const order = shuffled(pool.map(tile => tile.id), 193 + index * 97);
    // Never show the answer already assembled in the first letter positions.
    const opening = order.slice(0, level.word.length).map(id => pool[id].letter).join("");
    if (opening === level.word) order.push(order.shift());
    return {
      index, level, pool, order,
      slots: Array(level.word.length).fill(null)
    };
  }

  function validId(puzzle, id) {
    return Number.isInteger(id) && id >= 0 && id < puzzle.pool.length;
  }

  function placeAt(puzzle, id, position) {
    if (!validId(puzzle, id) || !Number.isInteger(position) ||
        position < 0 || position >= puzzle.slots.length) return puzzle;
    const currentPosition = puzzle.slots.indexOf(id);
    if (currentPosition === position) return puzzle;
    const slots = puzzle.slots.slice();
    const displaced = slots[position];
    if (currentPosition >= 0) slots[currentPosition] = displaced;
    slots[position] = id;
    return { ...puzzle, slots };
  }

  function placeNext(puzzle, id) {
    const position = puzzle.slots.indexOf(null);
    return position < 0 ? puzzle : placeAt(puzzle, id, position);
  }

  function removeAt(puzzle, position) {
    if (!Number.isInteger(position) || position < 0 ||
        position >= puzzle.slots.length || puzzle.slots[position] === null) return puzzle;
    const slots = puzzle.slots.slice();
    slots[position] = null;
    return { ...puzzle, slots };
  }

  function clear(puzzle) {
    return { ...puzzle, slots: Array(puzzle.slots.length).fill(null) };
  }

  function shuffle(puzzle, seed) {
    if (!Number.isInteger(seed)) throw new TypeError("Shuffle seed must be an integer");
    return { ...puzzle, order: shuffled(puzzle.order, seed) };
  }

  function letters(puzzle) {
    return puzzle.slots.map(id => id === null ? "" : puzzle.pool[id].letter).join("");
  }

  function check(puzzle) {
    if (puzzle.slots.some(id => id === null)) return { filled: false, correct: false, built: letters(puzzle) };
    const built = letters(puzzle);
    return { filled: true, correct: built === puzzle.level.word, built };
  }

  function hint(puzzle) {
    const word = puzzle.level.word;
    let position = puzzle.slots.findIndex((id, i) => id === null || puzzle.pool[id].letter !== word[i]);
    if (position < 0) return { puzzle, changed: false };
    const wanted = word[position];
    let chosen = puzzle.pool.find(tile => tile.letter === wanted && !puzzle.slots.includes(tile.id));
    if (!chosen) {
      chosen = puzzle.pool.find(tile =>
        tile.letter === wanted &&
        puzzle.slots.includes(tile.id) &&
        word[puzzle.slots.indexOf(tile.id)] !== wanted);
    }
    if (!chosen) return { puzzle, changed: false };
    return { puzzle: placeAt(puzzle, chosen.id, position), changed: true, position };
  }

  function stars(wrongChecks, hintsUsed) {
    if (!wrongChecks && !hintsUsed) return 3;
    if (wrongChecks <= 2 && hintsUsed <= 1) return 2;
    return 1;
  }

  const api = Object.freeze({ WORLDS, LEVELS, createPuzzle, placeAt,
    placeNext, removeAt, clear, shuffle, letters, check, hint, stars });
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root && typeof root === "object") root.WordWorkshopEngine = api;
})(typeof window === "undefined" ? null : window);
