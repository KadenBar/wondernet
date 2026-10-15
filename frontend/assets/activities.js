// SPDX-License-Identifier: AGPL-3.0-only
// All questions are bundled locally; answers are kept only in this browser page's memory.
"use strict";
(() => {
  const root = document.querySelector("[data-activity]");
  if (!root) return;

  const questionSets = {
    "letter-match": [
      { prompt: "Which lowercase letter matches M?", hint: "Look closely at the letter shapes.", choices: ["n", "m", "h"], answer: "m" },
      { prompt: "Which lowercase letter matches S?", hint: "Choose its small-letter partner.", choices: ["s", "c", "z"], answer: "s" },
      { prompt: "Which lowercase letter matches A?", hint: "These are two ways to write the same letter.", choices: ["o", "a", "e"], answer: "a" },
      { prompt: "Which lowercase letter matches R?", hint: "Find the lowercase form.", choices: ["v", "r", "n"], answer: "r" },
      { prompt: "Which lowercase letter matches T?", hint: "Just one of these matches.", choices: ["t", "f", "l"], answer: "t" }
    ],
    "patterns": [
      { prompt: "Circle, triangle, circle, triangle, ...", hint: "What shape comes next?", choices: ["Square", "Circle", "Triangle"], answer: "Circle" },
      { prompt: "Square, square, circle, square, square, circle, ...", hint: "The pattern repeats in groups of three.", choices: ["Square", "Triangle", "Circle"], answer: "Square" },
      { prompt: "Star, heart, heart, star, heart, heart, ...", hint: "Look for what starts each group.", choices: ["Heart", "Star", "Circle"], answer: "Star" },
      { prompt: "Triangle, square, circle, triangle, square, ...", hint: "What comes after square?", choices: ["Circle", "Triangle", "Star"], answer: "Circle" },
      { prompt: "Circle, circle, star, circle, circle, star, ...", hint: "One more group begins.", choices: ["Star", "Square", "Circle"], answer: "Circle" }
    ]
  };
  const questions = questionSets[root.dataset.activity];
  if (!questions) return;
  const progress = document.getElementById("activity-progress");
  const prompt = document.getElementById("activity-prompt");
  const hint = document.getElementById("activity-hint");
  const choices = document.getElementById("activity-choices");
  const feedback = document.getElementById("activity-feedback");
  const next = document.getElementById("activity-next");
  let index = 0;
  let correct = false;

  function showQuestion() {
    correct = false;
    const question = questions[index];
    progress.textContent = `Round ${index + 1} of ${questions.length}`;
    prompt.textContent = question.prompt;
    hint.textContent = question.hint;
    choices.replaceChildren();
    feedback.textContent = "Choose an answer when you're ready.";
    feedback.className = "activity-feedback";
    next.disabled = true;
    next.textContent = index === questions.length - 1 ? "Finish →" : "Next round →";
    for (const answer of question.choices) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "answer-option";
      button.textContent = answer;
      button.addEventListener("click", () => {
        if (correct) return;
        if (answer === question.answer) {
          correct = true;
          button.classList.add("answer-correct");
          for (const option of choices.querySelectorAll("button")) option.disabled = true;
          feedback.textContent = "That's it! Great thinking. 🌟";
          feedback.className = "activity-feedback activity-good";
          next.disabled = false;
          next.focus();
        } else {
          button.classList.add("answer-try-again");
          button.disabled = true;
          feedback.textContent = "Not quite. Try another!";
          feedback.className = "activity-feedback activity-retry";
        }
      });
      choices.append(button);
    }
  }

  next.addEventListener("click", () => {
    if (!correct) return;
    if (index < questions.length - 1) {
      index += 1;
      showQuestion();
    } else {
      progress.textContent = "All 5 rounds complete";
      prompt.textContent = "You finished! 🎉";
      hint.textContent = "Want to try again?";
      choices.replaceChildren();
      feedback.textContent = "Nice work exploring WonderNet.";
      feedback.className = "activity-feedback activity-good";
      next.textContent = "Play again ↻";
      next.disabled = false;
      next.onclick = () => { index = 0; next.onclick = null; showQuestion(); };
    }
  });
  showQuestion();
})();