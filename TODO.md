# CSE 4095 TODO — Build and Deploy a Web-Based Hangman Game

This is the implementation plan for an individual CSE 4095 Agentic Programming assignment, built from scratch. All task, testing, and completion checkboxes start unchecked. Existing folders, placeholder files, and the instructor's completion claims do not establish implementation or verification in this project.

Use [SPECIFICATION.md](SPECIFICATION.md) for the relevant game rules and REST API contract. The file on disk is named `SPECIFICATION.md`. Use [docs/cursor_transcript.md](docs/cursor_transcript.md) only to understand the instructor's historical development process and design questions. Its code, completed tasks, test counts, vocabulary counts, GitHub repository, and Render URL belong to the instructor's project; do not copy them or claim them as this project's work.

The student's assignment requirements take precedence over features in the larger specification. The final deliverables include a 1–2 page development report, 2–3 representative AI prompts, a 2–3 minute demonstration, and a prepared HuskyCT submission. Confirm final formats, filenames, and access requirements against the official rubric in Phase 7.

## Assignment Scope

Build the Python Hangman engine, Easy/Medium/Hard word management, Flask REST API, HTML/CSS/JavaScript browser client, automated and manual tests, GitHub repository and documentation, and public Render deployment.

The following features are explicitly **out of scope** and have no implementation phases:

- Human terminal clients.
- Automated playing bots and reference bot examples.
- Evaluation mode, evaluation sessions, and evaluation integrity systems.
- Scoring and official bot scoring.
- Leaderboards and rankings.
- Game logging for replay, replay endpoints, and replay tools.
- Tournament mode and bot competitions.

## Implementation and Progress Rules

- Implement one phase at a time. Complete its tasks, run its required tests, and satisfy its completion criteria before beginning the next phase.
- Add tests alongside each feature. Phase 5 expands integration and manual testing; it does not postpone the tests required in earlier phases.
- Keep the engine independent of Flask, HTTP, HTML, JavaScript, and browser drawing. The server owns all rules, word selection, and game state.
- Keep the selected word on the server during active gameplay. Omit the answer from active-game JSON, page source, browser state, and error messages. Reveal it only after a win or loss.
- Preserve the three specified game endpoints, request field names, response field names, spaced pattern format, and statuses `playing`, `won`, and `lost`.
- Resolve details left open by the specification explicitly and consistently. Document decisions in this roadmap and the README without importing unrelated instructor features.
- Write an original implementation. Keep development notes, actual test results, and representative prompts from this project's own AI-assisted development for the final report.
- Change a checkbox to completed only after its work exists and its required verification passes. Record failures and remaining work honestly.
- Make meaningful Git commits as phases are implemented; Phase 6 reviews and publishes that history. This planning revision does not implement any application functionality.

## Planned Game and API Decisions

These choices resolve details left open by the specification. They describe intended behavior, not completed features.

- Use exactly six incorrect guesses per game. A correct guess reveals every occurrence of that letter and costs no attempt.
- Accept nonempty ASCII-letter words and single ASCII-letter guesses; normalize uppercase to lowercase. Reject invalid, duplicate, and post-game guesses without changing state.
- Keep guessed and incorrect letters unique and in the order first guessed. Use spaces between pattern characters, such as `_ e _ _ e`.
- Use the same public state fields across the API: `pattern`, `guessed_letters`, `incorrect_letters`, `remaining_guesses`, and `status`. Status is `playing`, `won`, or `lost`.
- Omit `word` entirely while playing and include it after either outcome. The client cannot choose the hidden word or override game rules.
- Store games in memory, keyed by server-generated unique IDs. Games are independent and are lost when the server process restarts; shared storage and persistence are not required.
- Serve the page and API from the same Flask application. Browser requests use relative `/api/...` URLs.

| Endpoint | Request | Successful response |
| --- | --- | --- |
| `POST /api/games` | JSON object containing `difficulty`: `easy`, `medium`, or `hard` | `201`; `game_id` and safe initial state |
| `GET /api/games/{game_id}` | No body | `200`; current safe state, without modifying the game |
| `POST /api/games/{game_id}/guess` | JSON object containing `letter` | `200`; updated safe state |

Accept only `difficulty` on game creation and `letter` on guesses. Use consistent JSON errors: `400` for malformed/non-object JSON, missing, unexpected, or invalid fields, invalid difficulty, duplicate guesses, and post-game guesses; `404` for unknown game IDs; `405` for unsupported HTTP methods; `415` for POST requests without a supported JSON content type. Reject client attempts to supply an answer or alter rules. Unexpected server failures must not expose the hidden word or a production debugger.

## Phase 1: Project Setup and Core Game Engine

### Dependencies on Previous Phases

None. This phase establishes the Python foundation. Tests use supplied words directly; word-file loading belongs to Phase 2.

### Files Involved

- `game.py` — independent Hangman rules and safe state serialization.
- `tests/test_game.py` — game engine unit tests.
- `requirements.txt` — Python dependencies, including pytest for engine tests.
- `.gitignore` — verify that the local environment and generated test artifacts remain untracked.
- `TODO.md` — record verified progress.
- Existing `static/`, `words/`, `tests/`, and `docs/` directories — verify the intended layout.

### Tasks

- [x] Verify the project layout, select the Python interpreter, and verify or create a usable virtual environment.
- [x] Install and verify the dependencies needed for this phase, including pytest; confirm that `python -m pytest --version` uses the selected environment.
- [x] Verify environment/cache exclusions and the existing Git repository; initialize Git only if absent, and preserve this implementation's own development history.
- [x] Implement an original `HangmanGame` class without Flask or JavaScript dependencies.
- [x] Accept a supplied, nonempty word containing only ASCII letters, normalize it to lowercase, and keep it internal to the game.
- [x] Accept Easy, Medium, and Hard as difficulty metadata, normalize case, and reject unsupported values; difficulty does not select a word or change the six-miss limit.
- [x] Initialize independent guessed-letter and incorrect-letter collections for each game, preserving first-guess order.
- [x] Accept one ASCII letter per guess and normalize uppercase guesses to lowercase.
- [x] Reject empty, non-string, multi-character, numeric, punctuation, and whitespace guesses without changing game state.
- [x] Reject duplicate guesses without changing state or consuming an attempt; use this policy consistently in later phases.
- [x] Reveal every occurrence of a correctly guessed letter without reducing remaining guesses.
- [x] Record each new incorrect letter and reduce remaining guesses by exactly one.
- [x] Allow exactly six incorrect guesses, with six remaining at the start and no negative remaining count.
- [x] Generate a pattern with spaces between letters or underscores, matching the specification.
- [x] Detect a win when all letters have been revealed and a loss on the sixth incorrect guess.
- [x] Report `playing`, `won`, or `lost` and reject further guesses after completion without changing state.
- [x] Produce a client-safe state dictionary containing `pattern`, `guessed_letters`, `incorrect_letters`, `remaining_guesses`, and `status`.
- [x] Omit `word` entirely while playing; include `word` only after a win or loss as the documented answer-field choice.
- [x] Return public state snapshots whose letter collections cannot be used by callers to mutate the internal game.
- [x] Add deterministic unit tests alongside the engine implementation.

### Testing Requirements

- [x] Verify initial state, word and difficulty normalization and validation, stable guess ordering, and independent state across two game objects.
- [x] Verify correct guesses, repeated letters within a word, incorrect guesses, and the exact remaining-guess count.
- [x] Verify uppercase handling and rejection of invalid and duplicate guesses with unchanged state.
- [x] Exercise a complete win and a complete loss, including the fifth-versus-sixth incorrect-guess boundary.
- [x] Verify answer omission in every active state, disclosure after both outcomes, and unchanged state after post-game guesses.
- [x] Verify that changing a returned state snapshot does not change the game.
- [x] Run `python -m pytest tests/test_game.py` successfully without starting Flask or loading word files.

### Completion Criteria

- [x] The engine supports a complete deterministic game using Python alone.
- [x] All Phase 1 unit tests pass and cover the rules and validation cases above.
- [x] No Flask routes, word loading, or browser implementation is needed to verify this phase.

Verified on 2026-10-26 using Python 3.13.1 and pytest 9.1.1: `.venv/bin/python -m pytest tests/test_game.py` — **76 passed**. A standalone completed-game check with `.venv/bin/python -S` also passed with site-packages disabled. The existing virtual environment, pytest installation, Git repository, and ignore rules were verified. Word loading, Flask, and browser implementation remain for later phases.

## Phase 2: Word Management

### Dependencies on Previous Phases

Phase 1 must be complete and its tests passing. Word selection remains separate from the engine so the engine can still be tested with a supplied word.

### Files Involved

- `word_manager.py` — loading, validation, and difficulty-based selection.
- `words/easy.txt`, `words/medium.txt`, `words/hard.txt` — vocabulary.
- `words/README.md` — generated-list provenance, word counts, difficulty criteria, and loader behavior.
- `tests/test_words.py` — word management tests.
- `game.py`, `tests/test_game.py` — integration boundary and regression checks.
- `TODO.md` — vocabulary decisions and verified progress.

### Tasks

- [x] Populate nonempty Easy, Medium, and Hard word lists using assignment-provided vocabulary when supplied; otherwise document the chosen vocabulary sources and difficulty criteria.
- [x] Store one word per line in each difficulty file.
- [x] Implement word loading in `word_manager.py` without depending on Flask or browser code.
- [x] Resolve word-file paths relative to the project/module location rather than the caller's working directory.
- [x] Trim line whitespace, normalize words to lowercase, ignore blank lines, and remove duplicates within each list.
- [x] Validate that accepted words contain only ASCII letters; report invalid entries clearly.
- [x] Handle missing files and lists with no usable words with clear errors rather than starting an unplayable game.
- [x] Support only `easy`, `medium`, and `hard`, normalizing case consistently with the engine; reject missing or invalid difficulty values instead of silently selecting another list.
- [x] Select a random word from the requested difficulty so the Flask server can supply it to a new `HangmanGame` in Phase 3; keep word-file loading outside the engine.
- [x] Add tests for loading, validation, failures, and selection by difficulty.

### Testing Requirements

- [x] Verify the actual three lists are nonempty and contain usable words after validation.
- [x] Use temporary test lists to verify normalization, blank-line handling, deduplication, and invalid entries.
- [x] Verify missing and empty files and invalid difficulty values produce clear failures.
- [x] Verify selected words belong to the requested list using controlled randomness where needed; do not require consecutive random choices to differ.
- [x] Verify selection works when launched from another working directory.
- [x] Run `python -m pytest tests/test_game.py tests/test_words.py` successfully.

### Completion Criteria

- [x] Each difficulty reliably supplies a valid word for a new game.
- [x] Loading and selection behavior is tested, with no dependence on HTTP or the browser.
- [x] Phase 1 and Phase 2 tests pass together.

The three files were empty when Phase 2 began. Newly generated common English vocabulary was added for this student's implementation: **169 Easy words (3–5 letters), 156 Medium words (6–8), and 181 Hard words (9–12)**. These are not the instructor's original lists. [words/README.md](words/README.md) records their provenance and difficulty criteria. Loading preserves supplied files, ignores blanks, normalizes and deduplicates in memory, and rejects an entire list if any entry is invalid.

Verified on 2026-10-26 using Python 3.13.1 and pytest 9.1.1: `.venv/bin/python -m pytest tests/test_game.py tests/test_words.py` — **141 passed (76 engine tests and 65 word-management tests)**. A separate loading/engine check launched from `/private/tmp` with site-packages disabled passed for all three difficulties and confirmed that active game state omits the selected answer. Phase 3 and later work remains unchecked.

## Phase 3: Flask REST Server

### Dependencies on Previous Phases

Phases 1 and 2 must be complete and their tests passing. Flask combines the tested engine and word manager without taking over their responsibilities.

### Files Involved

- `server.py` — Flask application, request validation, game storage, and routes.
- `game.py`, `word_manager.py`, `words/*.txt` — existing backend components.
- `tests/test_api.py` — Flask API tests.
- `tests/conftest.py` — shared fixtures if needed.
- `requirements.txt`, `TODO.md` — dependencies and verified progress.

### Tasks

- [ ] Create a Flask application that can be instantiated with isolated storage and controlled test vocabulary.
- [ ] Store games on the server in memory and generate unique, opaque game IDs; never derive IDs from the hidden word.
- [ ] Keep games independent; creating or guessing in one game must not alter another.
- [ ] Implement `POST /api/games` with a JSON `difficulty` field and return `201` with `game_id` and safe initial state.
- [ ] Implement `GET /api/games/{game_id}` and return `200` with the current safe state without modifying the game.
- [ ] Implement `POST /api/games/{game_id}/guess` with a JSON `letter` field and return `200` with updated safe state.
- [ ] Preserve `pattern`, `guessed_letters`, `incorrect_letters`, `remaining_guesses`, and `status`; use the same state meanings across all three endpoints.
- [ ] Return `400` for invalid difficulty, missing or invalid fields, duplicate guesses, and guesses after completion; leave the game unchanged on rejected guesses.
- [ ] Return `404` for unknown game IDs and consistent JSON error responses for API failures.
- [ ] Return `400` for malformed JSON, non-object JSON, and empty JSON bodies; return `415` for unsupported or missing JSON content types on POST requests.
- [ ] Accept only the documented request fields; return `400` for unexpected fields, including client-supplied words or rule overrides.
- [ ] Use the safe serializer for responses; include `word` only when `status` is `won` or `lost`.
- [ ] Return `405` for unsupported methods and consistent JSON errors for API validation and routing failures; avoid HTML error pages in API responses.
- [ ] Keep word files outside publicly served static assets and avoid including hidden answers in errors or debugging responses.
- [ ] Add API tests alongside each endpoint.

### Testing Requirements

- [ ] Use Flask's test client to test all three endpoints, JSON field types, status codes, and all three difficulties.
- [ ] Test missing fields, malformed/non-object/empty JSON, unsupported content types, invalid difficulty, invalid letters, duplicates, unknown game IDs, and unsupported methods.
- [ ] Use server-side test fixtures with known words to exercise complete win and loss paths without adding a public answer-selection feature.
- [ ] Create two games and verify ID uniqueness, state independence, and safe retrieval before and after guesses.
- [ ] Verify invalid requests do not consume attempts and finished games cannot change.
- [ ] Verify active create/get/guess responses and errors omit the answer; verify completed get/guess responses reveal it.
- [ ] Run all engine, word management, and API tests successfully; manually exercise a complete game using HTTP requests.

### Completion Criteria

- [ ] A full game can be created, inspected, and completed through the original three-endpoint REST contract.
- [ ] All API success and failure responses use the documented JSON and HTTP behavior.
- [ ] Backend tests pass, independent games work, and active-game answers remain server-side.

## Phase 4: Browser Interface

### Dependencies on Previous Phases

Phases 1–3 must be complete and passing. The browser presents server state and sends requests through the established API.

### Files Involved

- `static/index.html` — page structure, controls, and SVG Hangman.
- `static/style.css` — styling and responsive layout.
- `static/app.js` — input, fetch requests, and state rendering.
- `server.py` — serve the browser page at `/` and its static assets.
- `tests/test_browser.py`, `tests/conftest.py` if needed — real-browser tests and fixtures.
- `requirements.txt`, `TODO.md` — browser test tooling and verified progress.

### Tasks

- [ ] Build the HTML, CSS, and JavaScript interface and serve it through Flask.
- [ ] Add labeled Easy, Medium, and Hard difficulty controls and a New Game button.
- [ ] Create games using `fetch()` with `POST /api/games` and keep the returned game ID for subsequent requests.
- [ ] Use `GET /api/games/{game_id}` to retrieve and render the current game without starting another one.
- [ ] Display the masked word, all previous guesses, incorrect guesses, remaining guesses, and current game status.
- [ ] Add a clickable A–Z alphabet keyboard and physical keyboard letter input.
- [ ] Route both input methods through the same guess-request flow; ignore modifier shortcuts and typing within unrelated form controls.
- [ ] Disable guessed letters, block duplicate submissions while a request is pending, and disable guessing after completion.
- [ ] Draw six Hangman body parts in SVG, updating only from the incorrect-guess count returned by the server.
- [ ] Display win and loss messages and reveal the answer received from the server after completion.
- [ ] Implement restart through a new game ID and reset the pattern, keyboard, drawing, guess history, and messages.
- [ ] Make the layout usable at common desktop and mobile widths with readable labels and usable controls.
- [ ] Show loading and request-error feedback; update guesses and remaining attempts only from accepted server state.
- [ ] Ignore delayed responses from an earlier game after New Game is selected, and prevent overlapping submissions from corrupting the displayed state.
- [ ] Keep the selected hidden word and all game-rule decisions out of active browser state and source.
- [ ] Select and document real-browser test tooling, add its dependencies and setup steps, and write initial automated interaction tests as the interface is built.

### Testing Requirements

- [ ] Verify Flask serves `/`, JavaScript, and CSS successfully.
- [ ] Run real-browser tests for difficulty selection, game creation, mouse guesses, physical keyboard guesses, and GET-based state rendering.
- [ ] Verify drawing progression, history, remaining guesses, and disabled keys match server responses.
- [ ] Verify completed-game feedback and that New Game resets all displayed and interactive state.
- [ ] Manually check desktop and mobile layouts and usable keyboard input.
- [ ] Run the existing backend suite and initial browser tests successfully.

### Completion Criteria

- [ ] A player can complete and restart a game entirely through the browser.
- [ ] Both input methods, SVG drawing, responsive layout, and API communication work together.
- [ ] Initial browser tests and all earlier tests pass; active answers remain on the server.

## Phase 5: Testing and Debugging

### Dependencies on Previous Phases

Phases 1–4 must be complete, with their feature-level tests passing. This phase closes coverage gaps and verifies complete browser/server flows.

### Files Involved

- `tests/test_game.py`, `tests/test_words.py`, `tests/test_api.py` — automated backend coverage.
- `tests/test_browser.py`, `tests/conftest.py` if needed — browser integration coverage.
- `docs/testing.md` — manual procedures, actual results, and resolved defects.
- `game.py`, `word_manager.py`, `server.py`, `static/*` — fixes where defects are demonstrated.
- `requirements.txt`, `TODO.md` — test dependencies and verified progress.

### Tasks

- [ ] Review all in-scope requirements against the automated suite and add missing behavioral coverage.
- [ ] Exercise correct and incorrect guesses, repeated letters in a word, duplicate guesses, invalid input, and uppercase input.
- [ ] Verify win and loss paths, six-incorrect-guess behavior, and rejection of guesses after completion.
- [ ] Verify New Game changes the game ID and resets every browser control and display.
- [ ] Verify multiple games retain independent state through complete API and browser flows.
- [ ] Add complete real-browser integration tests for start, guess, finish, and restart using controlled server-side fixtures.
- [ ] Verify hidden-word security in active JSON, initial HTML, browser state, static resources, and error responses.
- [ ] Use Chrome Developer Tools Network and Console panels to inspect request methods, paths, JSON payloads, status codes, response fields, and JavaScript errors.
- [ ] Test unknown game IDs and IDs invalidated by a server restart, failed network requests, non-JSON error responses, and server errors; display actionable feedback and permit a new game.
- [ ] Check that pending requests cannot apply an old game's response to a newly created game.
- [ ] Record manual test steps and actual results in `docs/testing.md`, including tested browser and viewport sizes.
- [ ] Fix confirmed defects, add meaningful regression tests, and rerun the affected tests plus the complete suite.

### Testing Requirements

- [ ] Run the complete automated suite, including real-browser tests, with no failing tests or unreported skips.
- [ ] Manually play Easy, Medium, and Hard games, observe both outcomes across the checks, and restart after completion.
- [ ] Verify keyboard and pointer input, correct SVG progression, responsive layout, and error recovery.
- [ ] Confirm HTTP/JSON behavior and answer-disclosure rules directly in Chrome Developer Tools.
- [ ] Review and resolve unexplained console errors and failed application requests.

### Completion Criteria

- [ ] All in-scope features have appropriate automated or recorded manual verification.
- [ ] The complete test suite passes and no known blocking gameplay, API, or answer-disclosure defect remains.
- [ ] Testing notes accurately describe results and remaining limitations.

## Phase 6: GitHub and Render Deployment

### Dependencies on Previous Phases

Phases 1–5 must be complete and passing. Deploy this project's own tested source and vocabulary.

### Files Involved

- `.git/` — local version-control metadata.
- `.gitignore`, `README.md`, `requirements.txt` — repository hygiene and reproducible setup.
- `server.py` — importable Flask application for Gunicorn.
- `render.yaml` if used, or documented Render dashboard settings in `README.md`.
- `.python-version` if used — selected Python runtime.
- `docs/testing.md`, `TODO.md` — deployment verification and progress.
- External resources: this project's GitHub repository and Render web service.

### Tasks

- [ ] Review this project's Git repository and commit history; verify that commits describe the student's original implementation and commit any remaining intended work.
- [ ] Verify `.gitignore` excludes virtual environments, Python/test caches, local secrets, and operating-system files.
- [ ] Create the student's own GitHub repository, configure its remote, and push the intended branch.
- [ ] Review tracked files to ensure source, word lists, tests, and documentation are included and secrets and local environments are excluded.
- [ ] Complete `requirements.txt` with tested application and test dependencies, including Flask, Gunicorn, pytest, and the selected browser test tooling; record tested versions and the selected Python runtime.
- [ ] Write a README describing assignment scope, architecture, rules, setup, local startup, browser use, automated/manual tests, and the three REST endpoints with example requests and responses.
- [ ] Document validation policies, status codes, answer-disclosure behavior, and the limits of in-memory storage.
- [ ] Expose an importable Flask application or factory and document the verified Gunicorn entry point.
- [ ] Configure Gunicorn with debug disabled and binding to `0.0.0.0` on Render's assigned `PORT`; record the build and start commands in `render.yaml` or the README.
- [ ] Use one worker and one service instance while game storage is process-local; document that games are lost on process restart.
- [ ] Create a Render web service connected to this project's GitHub repository and configure its dependency installation and Gunicorn startup.
- [ ] Check build and runtime logs and resolve deployment failures.
- [ ] Obtain a public HTTPS URL and add it and the correct GitHub URL to the README.
- [ ] Record the deployed commit and verify that Render is running the intended version; reserve the complete final deployment review for Phase 7.

### Testing Requirements

- [ ] Verify a fresh clone can install dependencies, run the documented test commands, and start the app using the README.
- [ ] Smoke-test the production Gunicorn entry point locally, including API requests and static assets.
- [ ] Open the public HTTPS URL in a fresh browser session and verify the page, assets, and all three endpoints.
- [ ] Smoke-test a deployed browser game through completion and restart; leave the full deployment verification matrix for Phase 7.
- [ ] Verify active deployed responses omit the word and production errors do not expose debugging details.
- [ ] Record actual deployment checks and any observed startup/restart limitations in `docs/testing.md`.

### Completion Criteria

- [ ] GitHub contains this project's intended source, tests, word lists, dependencies, and usable documentation.
- [ ] Render serves the tested Flask application and browser client at a working public HTTPS URL.
- [ ] Fresh-install and deployment smoke checks pass and repository/deployment links are accurate.

## Phase 7: Final Verification and Submission

### Dependencies on Previous Phases

Phases 1–6 must be complete, including a public deployment that passes its initial smoke tests. Perform the full deployment review here and confirm final deliverables against the official assignment instructions and rubric.

### Files Involved

- `README.md`, `TODO.md`, `docs/testing.md` — final documentation and verification evidence.
- `tests/*` and application files — final regression checks and necessary corrections.
- `docs/development_report.md` and its submission export — planned development report.
- `docs/submission_checklist.md` — planned mapping of rubric items to links/files.
- Demonstration recording file or shareable video link in the required submission format.
- Official assignment instructions and rubric — reference materials for confirming submission details; `docs/assignment_instructions.md` is currently absent and must not be assumed to contain requirements.
- External resources: GitHub, Render, the recording host if used, and HuskyCT.

### Tasks

- [ ] Verify deployed Easy, Medium, and Hard selection, game creation, GET-based retrieval, both input methods, drawing, previous and remaining guesses, completion, and restart.
- [ ] Verify both deployed win and loss paths, invalid/duplicate guesses, independent games, hidden-word protection, error recovery, and desktop/mobile layouts.
- [ ] Run final automated tests against the final source revision and record the results.
- [ ] Review the GitHub repository, correct branch, README instructions, dependency list, and public deployment link.
- [ ] Confirm that the deployed revision matches the source being submitted; redeploy and recheck if final fixes are made.
- [ ] Write a 1–2 page development report covering the original implementation, architecture and decisions, AI-assisted workflow, debugging, testing, deployment, and remaining limitations.
- [ ] Include 2–3 representative AI prompts from this project's own development and explain how their outputs were reviewed, adapted, and verified.
- [ ] Include accurate GitHub and Render URLs and actual testing results in the report where required.
- [ ] Record a 2–3 minute demonstration showing the public game, difficulty selection, guessing, drawing, finished-game feedback, and restart.
- [ ] Verify recording duration, playback, readability, and access permissions.
- [ ] Compare every deliverable with the official assignment instructions and rubric; confirm filenames, formats, access requirements, and any additional submission details.
- [ ] Prepare the HuskyCT submission with the required repository URL, Render URL, report, demonstration file/link, and any other confirmed deliverables.
- [ ] Review every remaining checkbox and completion claim; leave unfinished or unverified work unchecked.

### Testing Requirements

- [ ] Run the final engine, word management, API, and real-browser suites successfully.
- [ ] Perform a final public-URL smoke test in a fresh session, including one finished game and a restart.
- [ ] Verify report length, prompt count, recording length, link destinations, and reviewer access.
- [ ] Review the prepared HuskyCT materials against the rubric and verify that uploaded/exported files open correctly.

### Completion Criteria

- [ ] The deployed app and submitted source revision have passed final verification.
- [ ] The 1–2 page report includes 2–3 representative prompts, and the 2–3 minute recording is viewable.
- [ ] All confirmed submission requirements are accounted for and the HuskyCT submission package is prepared.
- [ ] Documentation and task statuses accurately reflect the work actually completed and verified.
