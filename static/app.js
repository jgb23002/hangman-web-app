(() => {
  "use strict";

  const byId = (id) => document.getElementById(id);
  const elements = {
    board: byId("game-board"), word: byId("word-display"), detail: byId("word-detail"),
    badge: byId("round-badge"), remaining: byId("remaining"),
    previous: byId("previous-guesses"), incorrect: byId("incorrect-guesses"),
    status: byId("status-box"), title: byId("status-title"), message: byId("status-message"),
    symbol: byId("status-symbol"), answer: byId("answer"), revealed: byId("revealed-answer"),
    progress: byId("game-progress"),
    newGame: byId("new-game"), newLabel: byId("new-game-label"), refresh: byId("refresh-game"),
    keyboard: byId("alphabet"), drawingDescription: byId("drawing-description"),
  };
  const parts = [...document.querySelectorAll(".hangman-part")];
  const pips = [...document.querySelectorAll(".life-pips span")];
  let game = null;
  let pending = null;
  let needsRefresh = false;

  class RequestError extends Error {
    constructor(message, status = 0) {
      super(message);
      this.status = status;
    }
  }

  for (const letter of "abcdefghijklmnopqrstuvwxyz") {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "letter-key";
    button.dataset.letter = letter;
    button.textContent = letter.toUpperCase();
    button.setAttribute("aria-label", `Guess ${letter.toUpperCase()}`);
    button.disabled = true;
    button.addEventListener("click", () => submitGuess(letter));
    elements.keyboard.append(button);
  }

  function updateControls() {
    const canGuess = game?.status === "playing" && !pending && !needsRefresh;
    for (const button of elements.keyboard.children) {
      const letter = button.dataset.letter;
      const used = Boolean(game?.guessed_letters.includes(letter));
      button.disabled = !canGuess || used;
      button.classList.toggle("is-used", used);
      button.classList.toggle("is-miss", Boolean(game?.incorrect_letters.includes(letter)));
    }
    elements.newGame.disabled = pending?.kind === "create";
    elements.newLabel.textContent = pending?.kind === "create" ? "Starting…" : "New Game";
    elements.refresh.disabled = !game || Boolean(pending);
    // The live status must stay outside the busy region so loading/error
    // feedback is not postponed until the entire request finishes.
    elements.keyboard.setAttribute("aria-busy", String(Boolean(pending)));
  }

  function feedback(tone, title, message) {
    elements.progress.textContent = "";
    elements.status.dataset.tone = tone;
    elements.title.textContent = title;
    elements.message.textContent = message;
    elements.symbol.textContent = { idle: "↗", playing: "↗", won: "✓", lost: "↺", error: "!" }[tone];
  }

  function showGameMessage() {
    if (!game) {
      feedback("idle", "Ready when you are", "Select New Game to begin.");
    } else if (game.status === "won") {
      feedback("won", "Word solved. Nicely done!", "A fresh word is waiting whenever you’re ready.");
    } else if (game.status === "lost") {
      feedback("lost", "This round is over", "A fresh word is one click away. Give it another go.");
    } else {
      feedback("playing", "One letter closer", "Choose a letter below or type on your keyboard.");
    }
    if (game?.status === "playing") {
      const lastGuess = game.guessed_letters.at(-1);
      elements.progress.textContent = `${lastGuess ? `Last guess: ${lastGuess.toUpperCase()}. ` : ""}${elements.word.getAttribute("aria-label")}. ${game.remaining_guesses} incorrect guesses remaining.`;
    }
  }

  function renderHistory(element, letters) {
    element.textContent = letters.length ? letters.join(" · ") : "None yet";
    element.classList.toggle("has-letters", letters.length > 0);
  }

  function renderGame() {
    elements.word.replaceChildren();
    elements.word.classList.toggle("is-empty", !game);
    if (game) {
      const slots = game.pattern.split(" ");
      for (const letter of slots) {
        const slot = document.createElement("span");
        slot.className = `letter-slot${letter === "_" ? " is-blank" : ""}`;
        slot.textContent = letter;
        slot.setAttribute("aria-hidden", "true");
        elements.word.append(slot);
      }
      elements.word.setAttribute("aria-label", `Word: ${slots.map((letter) => letter === "_" ? "blank" : letter.toUpperCase()).join(", ")}`);
      elements.detail.textContent = `${slots.length} letters · ${game.difficulty.charAt(0).toUpperCase() + game.difficulty.slice(1)} challenge`;
      elements.badge.textContent = `${game.difficulty} · ${game.status === "playing" ? "in progress" : game.status === "won" ? "word solved" : "round finished"}`.toUpperCase();
    } else {
      elements.word.textContent = "Your next word awaits.";
      elements.word.setAttribute("aria-label", "Start a new game to reveal the word length.");
      elements.detail.textContent = "Choose a difficulty. Make your first move.";
      elements.badge.textContent = "READY TO PLAY";
    }
    elements.remaining.textContent = game ? String(game.remaining_guesses) : "—";
    renderHistory(elements.previous, game?.guessed_letters ?? []);
    renderHistory(elements.incorrect, game?.incorrect_letters ?? []);
    const misses = game?.incorrect_letters.length ?? 0;
    parts.forEach((part, index) => part.classList.toggle("is-visible", index < misses));
    pips.forEach((pip, index) => pip.classList.toggle("is-available", Boolean(game) && index < game.remaining_guesses));
    elements.drawingDescription.textContent = `${misses} incorrect guesses shown in the drawing.`;
    elements.answer.hidden = !game || game.status === "playing";
    elements.revealed.textContent = game?.status !== "playing" ? game?.word ?? "" : "";
    showGameMessage();
    updateControls();
  }

  function isLetterList(letters) {
    return Array.isArray(letters)
      && letters.every((letter) => typeof letter === "string" && /^[a-z]$/.test(letter))
      && new Set(letters).size === letters.length;
  }

  function readGameState(data, expectedId = null) {
    // Check the response contract before replacing the last confirmed state.
    // These are shape/range checks, not calculations of correctness or outcome.
    if (!data || typeof data.game_id !== "string" || !data.game_id.trim()
      || !["easy", "medium", "hard"].includes(data.difficulty)
      || typeof data.pattern !== "string" || !/^[a-z_](?: [a-z_])*$/.test(data.pattern)
      || !isLetterList(data.guessed_letters) || !isLetterList(data.incorrect_letters)
      || !Number.isInteger(data.remaining_guesses)
      || data.remaining_guesses < 0 || data.remaining_guesses > parts.length
      || !["playing", "won", "lost"].includes(data.status)
      || (data.status !== "playing" && (typeof data.word !== "string" || !/^[a-z]+$/.test(data.word)))
      || (expectedId && data.game_id !== expectedId)) {
      throw new RequestError("The server returned an invalid game state. Please refresh this game.");
    }
    // Keep only public rendering fields. An answer is retained only after an
    // outcome supplied by the server; the browser never determines that outcome.
    const state = {
      game_id: data.game_id, difficulty: data.difficulty, pattern: data.pattern,
      guessed_letters: [...data.guessed_letters], incorrect_letters: [...data.incorrect_letters],
      remaining_guesses: data.remaining_guesses, status: data.status,
    };
    if (data.status !== "playing" && typeof data.word === "string") state.word = data.word;
    return state;
  }

  function beginRequest(kind) {
    pending?.controller.abort();
    const operation = {
      kind, controller: new AbortController(), focusedControl: document.activeElement,
    };
    pending = operation;
    updateControls();
    return operation;
  }

  function finishRequest(operation) {
    // Older requests must not enable controls or move focus in a newer game.
    if (pending !== operation) return;
    pending = null;
    updateControls();

    const previous = operation.focusedControl;
    if (!(previous instanceof HTMLButtonElement) || !previous.isConnected) return;
    // Preserve deliberate focus changes made while the request was pending.
    if (document.activeElement !== document.body && document.activeElement !== previous) return;
    let target = previous;
    if (previous.disabled) {
      if (needsRefresh && game) {
        target = elements.refresh;
      } else if (game?.status === "playing") {
        const buttons = [...elements.keyboard.children];
        target = buttons.slice(buttons.indexOf(previous) + 1).find((button) => !button.disabled)
          ?? buttons.find((button) => !button.disabled);
      } else {
        target = elements.newGame;
      }
    }
    target?.focus({ preventScroll: true });
  }

  async function apiRequest(path, operation, body) {
    let timedOut = false;
    const timeout = window.setTimeout(() => {
      timedOut = true;
      operation.controller.abort();
    }, 20000);
    try {
      const response = await fetch(path, {
        method: body === undefined ? "GET" : "POST",
        headers: body === undefined ? {} : { "Content-Type": "application/json" },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: operation.controller.signal,
        cache: "no-store",
      });
      let data;
      try { data = await response.json(); }
      catch { throw new RequestError("The server returned an unreadable response. Please try again.", response.status); }
      if (!response.ok) throw new RequestError(typeof data?.error === "string" ? data.error : "The request could not be completed.", response.status);
      return data;
    } catch (error) {
      if (timedOut) throw new RequestError("The request took too long. Please try again.");
      if (error instanceof RequestError || error.name === "AbortError") throw error;
      throw new RequestError("Could not reach the game. Check your connection and try again.");
    } finally {
      window.clearTimeout(timeout);
    }
  }

  function showRequestError(error, operation) {
    // A creation endpoint failing is not evidence that the old game vanished.
    if (error.status === 404 && operation.kind !== "create") {
      game = null;
      needsRefresh = false;
      renderGame();
      feedback("error", "This game is no longer available", "Select New Game to start a fresh round.");
    } else {
      // A failed request may still have reached the server. Require a GET before
      // allowing more guesses, rather than guessing what happened to the game.
      needsRefresh = Boolean(game);
      feedback("error", error.message, game ? "Refresh this game to continue, or start a new one." : "Select New Game when you’re ready to try again.");
    }
  }

  async function newGame() {
    if (pending?.kind === "create") return;
    const difficulty = document.querySelector('input[name="difficulty"]:checked').value;
    const operation = beginRequest("create");
    feedback("idle", "Finding your next word…", "A new challenge is on its way.");
    try {
      const data = await apiRequest("/api/games", operation, { difficulty });
      if (pending !== operation) return;
      game = readGameState(data);
      needsRefresh = false;
      renderGame();
    } catch (error) {
      if (pending === operation) showRequestError(error, operation);
    } finally {
      // Aborting fetch is best-effort. Identity checks also protect against a
      // delayed response (or finally block) belonging to an earlier game.
      finishRequest(operation);
    }
  }

  async function submitGuess(letter) {
    if (!game || game.status !== "playing" || pending || needsRefresh || game.guessed_letters.includes(letter)) return;
    const gameId = game.game_id;
    const operation = beginRequest("guess");
    feedback("playing", `Trying ${letter.toUpperCase()}…`, "Checking your letter.");
    try {
      const data = await apiRequest(`/api/games/${encodeURIComponent(gameId)}/guess`, operation, { letter });
      if (pending !== operation) return;
      game = readGameState(data, gameId);
      renderGame();
    } catch (error) {
      if (pending === operation) showRequestError(error, operation);
    } finally {
      finishRequest(operation);
    }
  }

  async function refreshGame() {
    if (!game || pending) return;
    const gameId = game.game_id;
    const operation = beginRequest("refresh");
    feedback("idle", "Refreshing your game…", "Picking up the latest progress.");
    try {
      const data = await apiRequest(`/api/games/${encodeURIComponent(gameId)}`, operation);
      if (pending !== operation) return;
      game = readGameState(data, gameId);
      needsRefresh = false;
      renderGame();
    } catch (error) {
      if (pending === operation) showRequestError(error, operation);
    } finally {
      finishRequest(operation);
    }
  }

  elements.newGame.addEventListener("click", newGame);
  elements.refresh.addEventListener("click", refreshGame);
  document.addEventListener("keydown", (event) => {
    if (event.defaultPrevented || event.repeat || event.ctrlKey || event.metaKey || event.altKey) return;
    if (event.target instanceof Element && event.target.closest('input, select, textarea, [contenteditable]:not([contenteditable="false"])')) return;
    if (/^[a-z]$/i.test(event.key)) {
      event.preventDefault();
      submitGuess(event.key.toLowerCase());
    }
  });
  renderGame();
})();
