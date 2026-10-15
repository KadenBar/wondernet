// SPDX-License-Identifier: AGPL-3.0-only
// Fully local, in-memory Circuit Garden UI. No network, cookies or storage.
"use strict";
(() => {
  const engine = window.CircuitGardenEngine;
  const boardElement = document.getElementById("cg-board");
  if (!engine || !boardElement) return;

  const byId = id => document.getElementById(id);
  const nameEl = byId("cg-level-name"), counterEl = byId("cg-counter");
  const noteEl = byId("cg-level-note"), movesEl = byId("cg-moves");
  const bloomsEl = byId("cg-blooms"), statusEl = byId("cg-status");
  const resetButton = byId("cg-reset"), hintButton = byId("cg-hint");
  const winCard = byId("cg-win"), winMessage = byId("cg-win-message");
  const winStars = byId("cg-win-stars"), nextButton = byId("cg-continue");
  const levelList = byId("cg-level-list");
  const SVG_NS = "http://www.w3.org/2000/svg";
  const LABELS = { source: "battery", flower: "flower", straight: "straight wire",
    bend: "corner wire", tee: "three-way wire", cross: "four-way wire" };
  const DIR_NAMES = ["north", "east", "south", "west"];

  let board, tiles, gameState, moves = 0, hintCount = 0;
  let unlocked = 1, levelNumber = 0, completed = false;
  const best = new Map();
  let cells = [];

  function svgPart(tag, attributes) {
    const el = document.createElementNS(SVG_NS, tag);
    for (const [key, value] of Object.entries(attributes)) {
      el.setAttribute(key, String(value));
    }
    return el;
  }

  function tileGraphic(tile) {
    const svg = svgPart("svg", { viewBox: "0 0 100 100",
      "aria-hidden": "true", focusable: "false", class: "cg-connections" });
    for (const direction of engine.DIRECTIONS) {
      if (!(tile.mask & direction.bit)) continue;
      const endX = 50 + direction.dc * 51;
      const endY = 50 + direction.dr * 51;
      svg.appendChild(svgPart("line", { x1: 50, y1: 50, x2: endX, y2: endY,
        class: "cg-pipe" }));
      svg.appendChild(svgPart("line", { x1: 50, y1: 50, x2: endX, y2: endY,
        class: "cg-water" }));
    }
    if (tile.type !== "source" && tile.type !== "flower") {
      svg.appendChild(svgPart("circle", { cx: 50, cy: 50, r: 9, class: "cg-node" }));
    }
    return svg;
  }

  function cellLabel(tile, index, powered) {
    const row = Math.floor(index / board.size) + 1, col = index % board.size + 1;
    const directions = engine.DIRECTIONS
      .filter(direction => tile.mask & direction.bit)
      .map(direction => DIR_NAMES[engine.DIRECTIONS.indexOf(direction)]).join(", ");
    if (tile.type === "source") {
      return `Row ${row}, column ${col}: fixed battery, points ${directions}.`;
    }
    const state = tile.type === "flower" && powered ? "Blooming!" :
      powered ? "Receiving power." : "Not powered.";
    return `Row ${row}, column ${col}: ${LABELS[tile.type]}. ${state} Open ends: ${directions}. Press to rotate clockwise.`;
  }

  function createCell(tile, index) {
    if (tile.type === "grass" || tile.type === "rock") {
      const cell = document.createElement("div");
      cell.className = "cg-cell cg-ground " + (tile.type === "rock" ? "cg-rock" : "cg-grass");
      cell.setAttribute("aria-hidden", "true");
      if (tile.type === "rock") {
        const rock = document.createElement("span");
        rock.className = "cg-rock-shape";
        cell.appendChild(rock);
      }
      return cell;
    }
    const cell = document.createElement(tile.fixed ? "div" : "button");
    if (!tile.fixed) {
      cell.type = "button";
      cell.addEventListener("click", () => rotateAt(index));
    }
    cell.className = "cg-cell cg-tile cg-" + tile.type;
    cell.dataset.index = String(index);
    if (tile.fixed) cell.setAttribute("role", "img");
    return cell;
  }

  function renderLevelList() {
    levelList.replaceChildren();
    engine.LEVELS.forEach((level, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "cg-level-button";
      if (index === levelNumber) button.classList.add("cg-current");
      button.disabled = index >= unlocked;
      if (index === levelNumber) button.setAttribute("aria-current", "step");
      const medal = best.get(index);
      button.setAttribute("aria-label", `Garden ${index + 1}: ${level.name}. ${index >= unlocked ? "Locked" : medal ? medal + " stars earned" : "Unlocked"}`);
      const number = document.createElement("strong");
      number.textContent = String(index + 1).padStart(2, "0");
      const title = document.createElement("span");
      title.textContent = level.name;
      const achievement = document.createElement("span");
      achievement.className = "cg-level-medal";
      achievement.textContent = index >= unlocked ? "🔒" : medal ? "★".repeat(medal) : "◦";
      button.append(number, title, achievement);
      if (index < unlocked) button.addEventListener("click", () => loadLevel(index));
      levelList.appendChild(button);
    });
  }

  function refresh() {
    gameState = engine.evaluate(tiles, board.size, board.source, board.flowers);
    movesEl.textContent = String(moves);
    bloomsEl.textContent = `${gameState.blooms.length} / ${board.flowers.length}`;
    cells.forEach((cell, index) => {
      const tile = tiles[index];
      if (tile.type === "rock" || tile.type === "grass") return;
      const powered = gameState.powered.has(index);
      const blooming = tile.type === "flower" && powered;
      cell.classList.toggle("cg-powered", powered);
      cell.classList.toggle("cg-blooming", blooming);
      cell.setAttribute("aria-label", cellLabel(tile, index, powered));
      if (!tile.fixed) cell.disabled = completed;
      cell.replaceChildren(tileGraphic(tile));
      if (tile.type === "source" || tile.type === "flower") {
        const icon = document.createElement("span");
        icon.className = tile.type === "source" ? "cg-battery-icon" : "cg-flower-icon";
        icon.textContent = tile.type === "source" ? "⚡" : "✿";
        icon.setAttribute("aria-hidden", "true");
        cell.appendChild(icon);
      }
    });
    if (gameState.complete && !completed) completeLevel();
  }

  function rotateAt(index, usingHint = false) {
    if (completed || tiles[index].fixed) return;
    tiles = engine.rotate(tiles, index);
    moves += 1;
    if (usingHint) hintCount += 1;
    refresh();
    if (!completed) {
      statusEl.textContent = usingHint ? "One piece turned for you. Try following the green wires!" :
        gameState.blooms.length ? `${gameState.blooms.length} of ${board.flowers.length} flowers blooming. Keep going!` :
          "The energy is moving. Keep connecting the open ends!";
    }
  }

  function completeLevel() {
    completed = true;
    for (const cell of cells) {
      if (cell.tagName === "BUTTON") cell.disabled = true;
    }
    const award = engine.stars(moves, board.par, hintCount);
    best.set(levelNumber, Math.max(best.get(levelNumber) || 0, award));
    unlocked = Math.min(engine.LEVELS.length, Math.max(unlocked, levelNumber + 2));
    winMessage.textContent = `You powered ${board.flowers.length} ${board.flowers.length === 1 ? "flower" : "flowers"} in ${moves} turns. ${hintCount ? "Hints used: " + hintCount + "." : "No hints needed!"}`;
    winStars.textContent = "★".repeat(award) + "☆".repeat(3 - award);
    winStars.setAttribute("aria-label", `${award} out of 3 stars`);
    nextButton.textContent = levelNumber === engine.LEVELS.length - 1 ? "Explore your gardens ↻" : "Next garden →";
    winCard.hidden = false;
    hintButton.disabled = true;
    statusEl.textContent = "Garden complete! All the flowers are blooming.";
    renderLevelList();
    nextButton.focus();
  }

  function loadLevel(number) {
    if (number >= unlocked || number < 0 || number >= engine.LEVELS.length) return;
    levelNumber = number;
    board = engine.createBoard(number);
    tiles = board.tiles;
    moves = 0;
    hintCount = 0;
    completed = false;
    winCard.hidden = true;
    hintButton.disabled = false;
    counterEl.textContent = `GARDEN ${String(number + 1).padStart(2, "0")} / ${engine.LEVELS.length}`;
    nameEl.textContent = board.name;
    noteEl.textContent = board.note;
    boardElement.className = `cg-board cg-size-${board.size}`;
    boardElement.setAttribute("aria-label", `${board.name}. ${board.size} by ${board.size} board. Use Tab or arrow keys to reach pipes, Enter or Space to rotate.`);
    cells = tiles.map((tile, index) => createCell(tile, index));
    boardElement.replaceChildren(...cells);
    statusEl.textContent = "Connect the battery to every flower. You've got this!";
    renderLevelList();
    refresh();
  }

  function nextFocusable(start, dr, dc) {
    let row = Math.floor(start / board.size) + dr;
    let col = start % board.size + dc;
    while (row >= 0 && row < board.size && col >= 0 && col < board.size) {
      const target = row * board.size + col;
      if (cells[target].tagName === "BUTTON" && !cells[target].disabled) return cells[target];
      row += dr;
      col += dc;
    }
    return null;
  }

  boardElement.addEventListener("keydown", event => {
    if (!event.target.matches("button.cg-tile")) return;
    const movements = { ArrowUp: [-1, 0], ArrowRight: [0, 1],
      ArrowDown: [1, 0], ArrowLeft: [0, -1] };
    const step = movements[event.key];
    if (step) {
      const target = nextFocusable(Number(event.target.dataset.index), ...step);
      if (target) {
        event.preventDefault();
        target.focus();
      }
    } else if (event.key.toLowerCase() === "r") {
      event.preventDefault();
      rotateAt(Number(event.target.dataset.index));
    }
  });

  hintButton.addEventListener("click", () => {
    if (completed) return;
    const index = engine.hint(tiles);
    if (index < 0) {
      statusEl.textContent = "All the wires are pointed the right way!";
      return;
    }
    rotateAt(index, true);
    if (!completed) {
      cells[index].classList.add("cg-nudged");
      cells[index].focus();
    }
  });
  resetButton.addEventListener("click", () => loadLevel(levelNumber));
  nextButton.addEventListener("click", () => {
    const next = (levelNumber + 1) % engine.LEVELS.length;
    loadLevel(next);
    boardElement.scrollIntoView({ block: "nearest", behavior: "auto" });
  });

  loadLevel(0);
})();
