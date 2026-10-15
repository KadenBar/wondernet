// SPDX-License-Identifier: AGPL-3.0-only
// Word Workshop is a stand-alone local spelling puzzle. No network or persistent state.
"use strict";
(() => {
  const engine = window.WordWorkshopEngine;
  const tray = document.getElementById("ww-tray");
  if (!engine || !tray) return;

  const byId = id => document.getElementById(id);
  const slotsEl = byId("ww-slots"), feedback = byId("ww-feedback");
  const clueText = byId("ww-clue-text"), emojiEl = byId("ww-emoji");
  const countText = byId("ww-letter-count"), worldText = byId("ww-world");
  const stageText = byId("ww-stage-title"), roundText = byId("ww-round");
  const completedText = byId("ww-completed"), checkButton = byId("ww-check");
  const hintButton = byId("ww-hint"), shuffleButton = byId("ww-shuffle");
  const clearButton = byId("ww-clear"), winCard = byId("ww-win");
  const winEmoji = byId("ww-win-emoji"), winDescription = byId("ww-win-description");
  const winStars = byId("ww-stars"), nextButton = byId("ww-next");
  const worldList = byId("ww-world-list");
  let currentLevel = 0, unlocked = 1;
  let puzzle, wrongChecks = 0, hintsUsed = 0, shuffleCount = 0, won = false;
  let lastWrongWord = "";
  const completed = new Map();

  const create = (tag, className, text) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = text;
    return el;
  };

  function say(message, state = "") {
    feedback.textContent = message;
    feedback.className = "ww-feedback" + (state ? " ww-feedback-" + state : "");
  }

  function renderCollection() {
    worldList.replaceChildren();
    engine.WORLDS.forEach((world, worldIndex) => {
      const group = create("section", "ww-world-group ww-world-" + world.color);
      const header = create("div", "ww-world-heading");
      header.append(
        create("span", "ww-world-icon", world.icon),
        create("strong", "", world.name),
        create("small", "", engine.LEVELS.slice(worldIndex * 4, worldIndex * 4 + 4)
          .filter((_, i) => completed.has(worldIndex * 4 + i)).length + "/4")
      );
      group.appendChild(header);
      const list = create("div", "ww-word-buttons");
      for (let i = worldIndex * 4; i < worldIndex * 4 + 4; i += 1) {
        const def = engine.LEVELS[i];
        const button = create("button", "ww-level");
        button.type = "button";
        button.disabled = i >= unlocked;
        if (i === currentLevel) {
          button.classList.add("ww-active");
          button.setAttribute("aria-current", "step");
        }
        const medal = completed.get(i);
        const display = medal ? def.word : "Word " + String(i + 1);
        const label = medal ? def.word + ", " + medal + " stars" :
          i < unlocked ? "Word " + (i + 1) + ", available" : "Word " + (i + 1) + ", locked";
        button.setAttribute("aria-label", world.name + ": " + label);
        button.append(
          create("span", "ww-level-name", display),
          create("span", "ww-level-icon", i >= unlocked ? "○" :
            medal ? "★".repeat(medal) : "◇")
        );
        if (i < unlocked) button.addEventListener("click", () => loadLevel(i));
        list.appendChild(button);
      }
      group.appendChild(list);
      worldList.appendChild(group);
    });
  }

  function makeSlot(index) {
    const id = puzzle.slots[index];
    const tile = id === null ? null : puzzle.pool[id];
    const button = create("button", "ww-slot" + (tile ? " ww-slot-filled" : ""),
      tile ? tile.letter : "");
    button.type = "button";
    button.dataset.slot = String(index);
    button.disabled = won;
    button.setAttribute("aria-label", "Position " + (index + 1) + " of " +
      puzzle.slots.length + ": " + (tile ? tile.letter + ". Press to remove this letter." :
        "Empty. Select a tile or drag one here."));
    button.addEventListener("click", () => {
      if (!tile || won) return;
      puzzle = engine.removeAt(puzzle, index);
      lastWrongWord = "";
      say("Letter back on the tray. You can try another!");
      renderBoard();
      const buttonToFocus = tray.querySelector("button:not(:disabled)");
      if (buttonToFocus) buttonToFocus.focus();
    });
    return button;
  }

  // Pointer Events handle both touch and mouse. Native HTML drag/drop does not
  // consistently fire from touchscreens, particularly mobile browsers.
  function installPointerDrag(button, tile) {
    let gesture = null;
    let suppressNextClick = false;

    function targetAt(x, y) {
      const element = document.elementFromPoint(x, y);
      const slot = element && element.closest(".ww-slot");
      return slot && slotsEl.contains(slot) && !slot.disabled ? slot : null;
    }

    function highlight(slot) {
      if (!gesture || gesture.highlighted === slot) return;
      if (gesture.highlighted) gesture.highlighted.classList.remove("ww-drop-target");
      gesture.highlighted = slot;
      if (slot) slot.classList.add("ww-drop-target");
    }

    function finish(pointerId) {
      if (!gesture || gesture.pointerId !== pointerId) return;
      const { ghost, highlighted } = gesture;
      gesture = null;
      if (highlighted) highlighted.classList.remove("ww-drop-target");
      if (ghost) ghost.remove();
      button.classList.remove("ww-being-dragged");
      if (button.hasPointerCapture(pointerId)) button.releasePointerCapture(pointerId);
    }

    button.addEventListener("pointerdown", event => {
      if (won || gesture || !event.isPrimary || event.button !== 0) return;
      gesture = {
        pointerId: event.pointerId,
        startX: event.clientX, startY: event.clientY,
        dragging: false, ghost: null, highlighted: null
      };
      button.setPointerCapture(event.pointerId);
    });

    button.addEventListener("pointermove", event => {
      if (!gesture || gesture.pointerId !== event.pointerId) return;
      const distance = Math.hypot(
        event.clientX - gesture.startX, event.clientY - gesture.startY
      );
      // A normal short tap still activates the ordinary accessible button.
      if (!gesture.dragging && distance < 10) return;
      if (!gesture.dragging) {
        gesture.dragging = true;
        gesture.ghost = create("span", "ww-drag-ghost", tile.letter);
        gesture.ghost.setAttribute("aria-hidden", "true");
        document.body.appendChild(gesture.ghost);
        button.classList.add("ww-being-dragged");
      }
      if (event.cancelable) event.preventDefault();
      gesture.ghost.style.left = event.clientX + "px";
      gesture.ghost.style.top = event.clientY + "px";
      highlight(targetAt(event.clientX, event.clientY));
    });

    button.addEventListener("pointerup", event => {
      if (!gesture || gesture.pointerId !== event.pointerId) return;
      const dragged = gesture.dragging;
      const slot = dragged ? targetAt(event.clientX, event.clientY) : null;
      finish(event.pointerId);
      if (!dragged) return; // Let the standard click handler place this tile.
      // A synthetic click can follow pointerup, even when drag ended off-tile.
      suppressNextClick = true;
      setTimeout(() => { suppressNextClick = false; }, 0);
      if (event.cancelable) event.preventDefault();
      if (!slot || won) {
        say("Drop your letter on a word space, or tap it to place it.");
        return;
      }
      const index = Number(slot.dataset.slot);
      const next = engine.placeAt(puzzle, tile.id, index);
      if (next === puzzle) return;
      puzzle = next;
      lastWrongWord = "";
      say("Letter dropped into place! You can move it again.");
      renderBoard();
    });

    button.addEventListener("pointercancel", event => {
      if (!gesture || gesture.pointerId !== event.pointerId) return;
      const dragged = gesture.dragging;
      finish(event.pointerId);
      if (dragged) {
        suppressNextClick = true;
        setTimeout(() => { suppressNextClick = false; }, 0);
      }
    });

    button.addEventListener("lostpointercapture", () => {
      if (gesture) finish(gesture.pointerId);
    });

    button.addEventListener("click", event => {
      if (suppressNextClick) {
        event.preventDefault();
        suppressNextClick = false;
        return;
      }
      if (won) return;
      const next = engine.placeNext(puzzle, tile.id);
      if (next === puzzle) {
        say("Your word spaces are full. Tap a letter above to change it.");
        return;
      }
      puzzle = next;
      lastWrongWord = "";
      say("Nice! Keep placing letters.");
      renderBoard();
      if (engine.check(puzzle).filled) {
        checkButton.focus();
      } else {
        const nextTile = tray.querySelector("button:not(:disabled)");
        if (nextTile) nextTile.focus();
      }
    });
  }

  function makeTile(tile) {
    const button = create("button", "ww-letter", tile.letter);
    button.type = "button";
    button.dataset.tile = String(tile.id);
    button.setAttribute("aria-label",
      "Letter " + tile.letter + ". Tap to place in the next empty space, or drag to a word space.");
    installPointerDrag(button, tile);
    return button;
  }

  function renderBoard() {
    slotsEl.replaceChildren(...puzzle.slots.map((_, i) => makeSlot(i)));
    const used = new Set(puzzle.slots.filter(id => id !== null));
    const remaining = puzzle.order.filter(id => !used.has(id));
    tray.replaceChildren(...remaining.map(id => makeTile(puzzle.pool[id])));
    const result = engine.check(puzzle);
    checkButton.disabled = won || !result.filled;
    hintButton.disabled = won;
    shuffleButton.disabled = won;
    clearButton.disabled = won;
    slotsEl.setAttribute("aria-label", "Your word: " +
      (puzzle.slots.map(id => id === null ? "blank" : puzzle.pool[id].letter).join(", ")));
  }

  function celebrate() {
    won = true;
    const award = engine.stars(wrongChecks, hintsUsed);
    completed.set(currentLevel, Math.max(award, completed.get(currentLevel) || 0));
    unlocked = Math.min(engine.LEVELS.length, Math.max(unlocked, currentLevel + 2));
    completedText.textContent = String(completed.size);
    winEmoji.textContent = puzzle.level.emoji;
    winDescription.textContent = "You built " + puzzle.level.word + "! " +
      (wrongChecks || hintsUsed ? "Every try helps you learn." : "First try, no hints. Nicely done!");
    winStars.textContent = "★".repeat(award) + "☆".repeat(3 - award);
    winStars.setAttribute("aria-label", award + " out of three stars");
    nextButton.textContent = currentLevel === engine.LEVELS.length - 1 ?
      "Back to the first world ↻" : "Next word →";
    winCard.hidden = false;
    say("You built " + puzzle.level.word + "! Your word is complete!", "success");
    renderCollection();
    renderBoard();
    nextButton.focus();
  }

  function loadLevel(index) {
    if (index < 0 || index >= unlocked || index >= engine.LEVELS.length) return;
    currentLevel = index;
    puzzle = engine.createPuzzle(index);
    won = false;
    wrongChecks = 0;
    hintsUsed = 0;
    shuffleCount = 0;
    lastWrongWord = "";
    const world = engine.WORLDS[puzzle.level.world];
    document.body.dataset.world = world.color;
    worldText.textContent = world.icon + " " + world.name.toUpperCase();
    stageText.textContent = "Build word " + (index + 1);
    roundText.textContent = "WORD " + String(index + 1).padStart(2, "0") +
      " OF " + engine.LEVELS.length;
    emojiEl.textContent = puzzle.level.emoji;
    clueText.textContent = puzzle.level.clue;
    countText.textContent = puzzle.level.word.length + " letters to find";
    winCard.hidden = true;
    completedText.textContent = String(completed.size);
    renderCollection();
    renderBoard();
    say("Choose a letter tile to begin. You can change your mind!");
  }

  checkButton.addEventListener("click", () => {
    if (won) return;
    const result = engine.check(puzzle);
    if (!result.filled) {
      say("Fill every space before building your word.");
      return;
    }
    if (result.correct) {
      celebrate();
      return;
    }
    if (lastWrongWord !== result.built) {
      wrongChecks += 1;
      lastWrongWord = result.built;
    }
    say("Not quite! Try swapping a tile or asking for a hint. You can do this.", "retry");
    slotsEl.classList.remove("ww-gentle-shake");
    // Request reflow so a fresh wrong guess can animate again.
    void slotsEl.offsetWidth;
    slotsEl.classList.add("ww-gentle-shake");
  });
  clearButton.addEventListener("click", () => {
    if (won) return;
    puzzle = engine.clear(puzzle);
    lastWrongWord = "";
    renderBoard();
    say("Fresh start! All the letters are back on your tray.");
  });
  shuffleButton.addEventListener("click", () => {
    if (won) return;
    shuffleCount += 1;
    puzzle = engine.shuffle(puzzle, 173 + currentLevel * 47 + shuffleCount * 13);
    renderBoard();
    say("Letters mixed! Let's try a different arrangement.");
  });
  hintButton.addEventListener("click", () => {
    if (won) return;
    const result = engine.hint(puzzle);
    if (!result.changed) {
      say("All the letters are in the right spaces. Try building your word!");
      return;
    }
    puzzle = result.puzzle;
    hintsUsed += 1;
    lastWrongWord = "";
    renderBoard();
    say("Here's one helpful letter. Keep going!");
    const slot = slotsEl.querySelectorAll("button")[result.position];
    if (slot) {
      slot.classList.add("ww-hinted");
      slot.focus();
    }
  });
  nextButton.addEventListener("click", () => {
    loadLevel((currentLevel + 1) % engine.LEVELS.length);
    const target = slotsEl.querySelector("button");
    if (target) target.scrollIntoView({ block: "nearest", behavior: "auto" });
  });

  loadLevel(0);
})();
