# CSE 4095 TODO — Build and Deploy a Web-Based Hangman Game

This roadmap records the verified status of an individual CSE 4095 Agentic Programming assignment built from scratch. Checked items have implementation and verification evidence; unchecked items are incomplete or not yet verified. The final review below supersedes earlier progress notes. The instructor's completion claims do not establish completion in this project.

Use [SPECIFICATION.md](SPECIFICATION.md) for the relevant game rules and REST API contract. The file on disk is named `SPECIFICATION.md`. Use [docs/cursor_transcript.md](docs/cursor_transcript.md) only to understand the instructor's historical development process and design questions. Its code, completed tasks, test counts, vocabulary counts, GitHub repository, and Render URL belong to the instructor's project; do not copy them or claim them as this project's work.

The professor's actual requirements, supplied by the student in the final submission request, take precedence over the larger specification and extra AI-generated QA procedures. Required deliverables are the working Python/Flask/browser Hangman project, testing/debugging, GitHub source, public Render deployment, a 1–2 page report, 2–3 representative prompts, an approximately 2–3 minute demonstration, and HuskyCT submission. Supporting QA documents and screenshots are useful evidence, not additional mandatory HuskyCT deliverables.

## Assignment Scope

The assignment covers the Python Hangman engine, Easy/Medium/Hard word management, Flask REST API, HTML/CSS/JavaScript browser client, testing/debugging, GitHub repository/documentation, public Render deployment, and report/prompts/demonstration submitted through HuskyCT. Actual HuskyCT submission is **Completed — confirmed by student**. Existing automated/live tests, recorded gameplay, and the student's manual confirmations support the testing requirement. Remaining additional QA procedures are not separate instructor deliverables.

The following features are explicitly **out of scope** and have no implementation phases:

- Human terminal clients.
- Automated playing bots and reference bot examples.
- Evaluation mode, evaluation sessions, and evaluation integrity systems.
- Scoring and official bot scoring.
- Leaderboards and rankings.
- Game logging for replay, replay endpoints, and replay tools.
- Tournament mode and bot competitions.

## Implementation and Progress Rules

- Preserve the seven-phase development history. Required features and their verification establish assignment progress; retained optional QA items may remain open without blocking later phases or becoming new instructor requirements.
- Add tests alongside each feature. Phase 5 expands integration and manual testing; it does not postpone the tests required in earlier phases.
- Keep the engine independent of Flask, HTTP, HTML, JavaScript, and browser drawing. The server owns all rules, word selection, and game state.
- Keep the selected word on the server during active gameplay. Omit the answer from active-game JSON, page source, browser state, and error messages. Reveal it only after a win or loss.
- Preserve the three specified game endpoints, request field names, response field names, spaced pattern format, and statuses `playing`, `won`, and `lost`.
- Resolve details left open by the specification explicitly and consistently. Document decisions in this roadmap and the README without importing unrelated instructor features.
- Write an original implementation. Keep development notes, actual test results, and representative prompts from this project's own AI-assisted development for the final report.
- Change a checkbox to completed only after its work exists and its required verification passes. Record failures and remaining work honestly.
- Make meaningful Git commits as phases are implemented; Phase 6 reviews and publishes that history. This final review modifies only `TODO.md`; it does not change application functionality, tests, deployment settings, or Git history.

## Game and API Decisions

These implemented choices resolve details left open by the specification. Source review, the current regression suite, and live checks support the behaviors below.

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

## Final Checkbox Review — October 28, 2026

**160 completed; 7 unchecked; all 167 checklist items and seven phases retained.** The file at the start of this review already contained **156 completed / 11 unchecked**; the student's **147 / 20** figures describe an earlier checkpoint. This update closes **4** more items: manual desktop/mobile/keyboard checks, both Render log-review items, and the already-prepared submission package. All checklist item wording and order are preserved. The original 20 open items are reconciled individually below.

| Phase | Checked | Unchecked | Current status |
| --- | ---: | ---: | --- |
| 1 — Project setup and game engine | 30 | 0 | Required work complete |
| 2 — Word management | 19 | 0 | Required work complete |
| 3 — Flask REST server | 27 | 0 | Required work complete |
| 4 — Browser interface | 25 | 0 | Functionality verified; manual layout/keyboard checks student-confirmed |
| 5 — Testing and debugging | 19 | 1 | Chrome/manual gameplay confirmed; optional recording of results in another document remains |
| 6 — GitHub and Render | 25 | 0 | Deployment verified; dashboard/startup/log inspection student-confirmed |
| 7 — Final verification/submission | 15 | 6 | Package prepared and actually submitted; video-duration acceptance and artifact/access verification remain |
| **Total** | **160** | **7** | **1 optional documentation task + 2 overlapping duration criteria + 4 artifact/access verification items remain open** |

### Student-Confirmed Activities

The activities below are **Completed — confirmed by student**, accepted as user-reported evidence from the latest instruction. The AI did not independently observe these personal checks or inspect the student's dashboard, portal, or DevTools session. No repetition or receipt screenshot is required merely because the AI was absent. Activity dates, completion times, and the exact uploaded artifact versions were not specified.

| Activity | Accepted confirmation and scope |
| --- | --- |
| Render startup settings and logs | Student confirms startup-settings and deployment-log inspection. This closes both retained dashboard/log-review items using student-reported evidence and existing successful deployment checks. No deployment failure or repair is invented. |
| Render deployment verification | Student confirms deployment verification and reports an Events screenshot showing commit `471d0cf`. Existing independently executed public HTTPS/API/Chrome checks also support working deployment. |
| Actual HuskyCT submission | Student confirms actual submission, not only preparation. The preparation/submission workflow is complete; this does not automatically verify every uploaded file's duration or reviewer access. |
| Google Chrome Developer Tools | Student confirms Network/Console inspection, HTTP methods, JSON payloads/responses, and hidden-word protection. Both Chrome-specific items are complete; no new AI DevTools session is claimed. |
| Manual Easy/Medium/Hard gameplay | Student confirms personal gameplay at all three difficulties. The existing inspected recording also establishes win/loss/restart content. |
| Physical keyboard and desktop/mobile layouts | Student explicitly confirms these manual checks. This satisfies the retained Phase 4 manual item without inferring unreported screen-reader, named-device, or additional-browser testing. |

### Instructor Requirements and Evidence

The supplied professor requirements take priority over AI-added QA procedures. A separate local rubric file, testing/readiness-document submission, fixed screenshot count, startup-command screenshots, separate log report, and separate manual-testing document are not added HuskyCT deliverables. Optional items stay open only for genuinely distinct, unconfirmed work; confirmed manual activities are not represented as unperformed.

| Instructor requirement | Status and evidence |
| --- | --- |
| Python Hangman engine | Complete — independent engine; 78 passing engine cases |
| Easy/Medium/Hard words | Complete — validated lists; 76 word cases and all-difficulty live verification |
| Flask REST API | Complete — three required endpoints; 102 API cases and live checks |
| HTML/CSS/JavaScript browser client | Complete — interface, 40 browser cases, recorded live gameplay |
| Testing/debugging | Complete — 296 passed, 0 failed; regression/live evidence and student-confirmed manual checks |
| GitHub repository | Complete — published source, README, tests, configuration and development history |
| Public Render deployment | Complete — verified public HTTPS application/API and supplied deployment evidence |
| Render configuration/startup/log inspection | Completed — confirmed by student; no independent AI dashboard inspection claimed |
| 1–2 page development report | Complete — directly inspected two-page, six-section report |
| 2–3 representative prompts | Complete — three student prompts and correct report links/results |
| Demonstration | Required content exists; measured duration is **3:52.75**, longer than the instructor's **approximate 2–3-minute target**. No shorter export or accepted exception is evidenced. |
| Actual HuskyCT submission | **Completed — confirmed by student**; uploaded-version acceptance/access is not inferred |

### Updated Classification of the 20 Earlier Open Items

**A:** completed mandatory work. **B:** unresolved demonstration-duration criterion. **C:** additional optional QA/documentation. **D:** follow-up artifact/access verification awaiting completion/confirmation. Category D does not mean the actual HuskyCT submission is pending. The two B items concern the same video-duration deviation; the four D items overlap on final artifact/access verification. They are not six missing deliverables. Measuring and reporting an overlong recording is completed verification, not proof that its duration meets the target.

| Earlier open item | Category | Current checkbox status |
| --- | --- | --- |
| Additional manual desktop/mobile/keyboard check | C | Completed — confirmed by student |
| Chrome-specific Network/Console inspection | C | Completed — confirmed by student |
| Separate manual-results document | C | Open — distinct optional work |
| Additional manual Medium/Hard play | C | Completed — confirmed by student |
| Chrome-specific HTTP/privacy inspection | C | Completed — confirmed by student |
| Render service creation and production setup | A | Complete |
| Complete Render build/runtime log review | C | Completed — confirmed by student |
| Record the deployed application commit | C | Complete |
| Dashboard runtime/settings/error-log inspection | C | Completed — confirmed by student |
| Compare deployed and submitted application source | C | Complete |
| Development report | A | Complete |
| Demonstration duration | B | Open — 3:52.75 exceeds approximate 2–3-minute target |
| Final recording export/access check | D | Open — follow-up review |
| Final check against supplied instructor requirements | D | Open — follow-up review |
| Prepare HuskyCT submission | A | Completed — confirmed by student |
| Combined final artifact acceptance checks | D | Open — measurements/links verified; reviewer access unconfirmed |
| Review actual HuskyCT materials | D | Open — follow-up review |
| Final application/source verification | A | Complete |
| Report plus duration-compliant/viewable video criterion | B | Open — duration/access part |
| Final package and submission readiness | A | Completed — package prepared and actual submission confirmed; known duration deviation recorded separately |

### Evidence Provenance and Reuse

Application/test/configuration revision is `471d0cf4751cc0e07ae1360fdcde28b30a113805`. Existing verification is reused: **296 passed, 0 failed, 0 errors, 0 skipped** (**78 engine, 76 word-management, 102 API, 40 browser**) in the previously recorded 21.10-second run. Prior actual HTTPS/Chrome checks covered all difficulties, endpoints, answer privacy, outcomes, restart, independent games, responsive views, and interrupted-response GET recovery. No application changes or redundant test runs were needed for this confirmation update.

**Deployment:** the supplied newer Events description identifies `471d0cf` successfully deployed on October 28, 2026 at 10:44 AM through Auto-Deploy, matching the reviewed application source. The available older `10_render_deployment.png` remains historical `138e095` evidence; only evidence files changed between those commits. Student-reported Gunicorn termination/worker/master messages are normal shutdown/lifecycle evidence, not proof of a crash. The latest explicit confirmation establishes personal startup-settings inspection, deployment-log inspection, and deployment verification. Dashboard/log activities are **Completed — confirmed by student**; the AI did not independently reopen the newer screenshot or dashboard, and no new deployment or repair is claimed.

**Report:** [Hangman_Development_Report.pdf](docs/Hangman_Development_Report.pdf), **923,167 bytes**, SHA-256 `706c36eeb7552b95bfb8edc37b88b68f8a0dff881b53c5fc03357ae4e92a1254`, is unchanged from its direct inspection. It has two pages, six main sections, three representative prompts, accurate testing figures, and correct GitHub/Render links. An additional limitations sentence remains optional, not an unmet instructor requirement.

**Video:** [Hangman_Demonstration.mp4](docs/Hangman_Demonstration.mp4) is unchanged, SHA-256 `280a6efba65d1837a68f6d3c1fa528bb5f0fa8a24b02d5ba95ea0220c232037a`. The available file's measured duration is **232.746896 seconds (3:52.75)**. Prior decoding and visual inspection established deployed gameplay, Easy win/loss/restart, and Safari request/response evidence. Those facts remain valid; the newly confirmed Chrome inspection is a separate student-performed activity. No shorter local recording, accepted exception, exact HuskyCT-uploaded version, or final reviewer-access result was confirmed.

### Submission Completed; Remaining Acceptance and Follow-up Checks

**Actual HuskyCT submission is completed on the student's explicit confirmation.** Do not request another submission or proof solely because the AI did not observe it. The record does not certify the exact submitted video version or professor acceptance of its duration.

For the known local **3:52.75** recording, the approximately **53-second overrun** remains unresolved. If needed and permitted by course rules, shorten/re-export while preserving required content, or obtain instructor acceptance of the longer recording as an exception. An exception must still be described as 3:52.75, not as within three minutes. Confirm remaining reviewer-access/uploaded-artifact checks if completing those combined items; no duplicate gameplay, DevTools, startup-settings inspection, or automated test run is requested.

The remaining optional C item is recording the confirmed manual steps/results and browser/viewport details in `docs/testing.md`. It is not an additional instructor deliverable, and the checks themselves are complete. That separate document was not edited under this TODO-only authorization. The report/video and all source, tests, README, dependencies, deployment configuration, and other documentation were preserved. Only `TODO.md` was edited. No AI commit, push, deployment change, portal operation, or Git-history rewrite was performed. Older pending/manual-not-run statements in README/testing/readiness documents describe earlier records and do not override the accepted confirmations here.

### Exact Remaining Work

The seven preserved unchecked items reduce to the following overlapping work. None requires repeating confirmed gameplay, keyboard/layout checks, DevTools inspection, Render checks, or the 296-test run.

| Remaining checkbox | Classification | Missing evidence / exact next action |
| --- | --- | --- |
| Phase 5: record manual steps/results in `docs/testing.md` | Optional AI-added documentation | In a separately authorized documentation edit, record the already-completed checks and supplied browser/viewport details; do not invent missing dimensions or rerun checks just for AI observation. |
| Phase 7: record a 2–3 minute demonstration | Instructor duration target | Required content exists, but the local file is 3:52.75. If required/permitted by the course, provide an approximately 2–3-minute export or obtain acceptance of the accurately disclosed longer duration. |
| Phase 7: verify recording duration/playback/readability/access | Additional verification | Duration, local playback, and readability were checked. Confirm reviewer permissions/access to the final submitted video or link; no new recording is needed solely to measure duration. |
| Phase 7: compare all deliverables, filenames/formats/access with course instructions | Additional final QA | Confirm that the actual submitted filenames, formats, permissions, and any course-specific details were reviewed. No extra local rubric file is required. |
| Phase 7: verify report/prompts/video length/links/reviewer access | Additional verification | Report, prompts, measured video length, and link destinations are verified. Confirm final reviewer access; the known duration deviation is tracked in the separate duration criteria. |
| Phase 7: review uploaded/exported HuskyCT artifacts | Additional final QA | Confirm the submitted/exported report and video open correctly and satisfy the actual upload/access instructions. Submission itself is already complete. |
| Phase 7: combined report and 2–3-minute/viewable recording criterion | Overlapping instructor-duration/access criterion | Report is complete. Resolve or obtain acceptance of the same video-duration deviation, and confirm final reviewer access. |

**Final readiness:** Required application, tests, report/prompts, GitHub, public Render deployment, and actual HuskyCT submission are complete on the evidence identified above. The known demonstration-duration deviation and unconfirmed final artifact/access checks prevent an unqualified claim that every retained acceptance criterion is complete. The optional manual-results document is not a submission blocker.

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

Historical Phase 1 checkpoint, 2026-10-26, using Python 3.13.1 and pytest 9.1.1: `.venv/bin/python -m pytest tests/test_game.py` — **76 passed**. A standalone completed-game check with `.venv/bin/python -S` also passed with site-packages disabled. The existing virtual environment, pytest installation, Git repository, and ignore rules were verified. At that checkpoint, word loading, Flask, and browser implementation were reserved for later phases.

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

Historical Phase 2 checkpoint, 2026-10-26, using Python 3.13.1 and pytest 9.1.1: `.venv/bin/python -m pytest tests/test_game.py tests/test_words.py` — **141 passed (76 engine tests and 65 word-management tests)**. A separate loading/engine check launched from `/private/tmp` with site-packages disabled passed for all three difficulties and confirmed that active game state omits the selected answer. Phase 3 and later work had not yet been completed at that checkpoint.

## Phase 3: Flask REST Server

### Dependencies on Previous Phases

Phases 1 and 2 must be complete and their tests passing. Flask combines the tested engine and word manager without taking over their responsibilities.

### Files Involved

- `server.py` — Flask application, request validation, game storage, and routes.
- `game.py`, `word_manager.py`, `words/*.txt` — existing backend components.
- `tests/test_api.py` — Flask API tests and isolated application/vocabulary fixtures.
- `requirements.txt`, `TODO.md` — dependencies and verified progress.

### Tasks

- [x] Create a Flask application that can be instantiated with isolated storage and controlled test vocabulary.
- [x] Export the application as `app`, support local startup with `python server.py`, and verify the one-worker Gunicorn entry point with debug disabled.
- [x] Serve the existing `static/index.html` at `/` and existing assets at `/static/` without implementing the Phase 4 frontend.
- [x] Store games on the server in memory and generate unique, opaque game IDs; never derive IDs from the hidden word.
- [x] Keep games independent; creating or guessing in one game must not alter another.
- [x] Implement `POST /api/games` with a JSON `difficulty` field and return `201` with `game_id`, normalized `difficulty`, and safe initial state.
- [x] Implement `GET /api/games/{game_id}` and return `200` with the current safe state without modifying the game.
- [x] Implement `POST /api/games/{game_id}/guess` with a JSON `letter` field and return `200` with updated safe state.
- [x] Preserve `pattern`, `guessed_letters`, `incorrect_letters`, `remaining_guesses`, and `status`; return `game_id` and `difficulty` consistently across all three endpoints.
- [x] Return `400` for invalid difficulty, missing or invalid fields, duplicate guesses, and guesses after completion; leave the game unchanged on rejected guesses.
- [x] Return `404` for unknown game IDs and consistent JSON error responses for API failures.
- [x] Return `400` for malformed JSON, non-object JSON, and empty JSON bodies; return `415` for unsupported or missing JSON content types on POST requests.
- [x] Accept only the documented request fields; return `400` for unexpected fields, including client-supplied words or rule overrides.
- [x] Use the safe serializer for responses; include `word` only when `status` is `won` or `lost`.
- [x] Return `405` for unsupported methods and consistent JSON errors for API validation and routing failures; avoid HTML error pages in API responses.
- [x] Keep word files outside publicly served static assets and avoid including hidden answers in errors or debugging responses.
- [x] Add API tests alongside each endpoint.

### Testing Requirements

- [x] Use Flask's test client to test all three endpoints, JSON field types, status codes, and all three difficulties.
- [x] Test missing fields, malformed/non-object/empty JSON, unsupported content types, invalid difficulty, invalid letters, duplicates, unknown game IDs, and unsupported methods.
- [x] Use server-side test fixtures with known words to exercise complete win and loss paths without adding a public answer-selection feature.
- [x] Create two games and verify ID uniqueness, state independence, and safe retrieval before and after guesses.
- [x] Verify invalid requests do not consume attempts and finished games cannot change.
- [x] Verify active create/get/guess responses and errors omit the answer; verify completed get/guess responses reveal it.
- [x] Run all engine, word management, and API tests successfully; manually exercise a complete game using HTTP requests.

### Completion Criteria

- [x] A full game can be created, inspected, and completed through the original three-endpoint REST contract.
- [x] All API success and failure responses use the documented JSON and HTTP behavior.
- [x] Backend tests pass, independent games work, and active-game answers remain server-side.

Implementation: `create_app(config=None, word_manager=None)` creates independent per-app game storage and supports controlled server-side vocabulary fixtures. The factory's `word_manager` argument is keyword-only. Module-level `app` is the Gunicorn entry point. Creation selects a word through `WordManager`, creates a `HangmanGame`, and assigns a UUID-based ID with collision protection. A lock protects dictionary operations and game-state snapshots/updates within the process. Responses combine game ID and difficulty with `HangmanGame.to_state()`; no private game fields are serialized directly.

Validation: POST bodies must be JSON objects containing only the required `difficulty` or `letter` field. Difficulty case is normalized; the engine validates letters and rejects duplicate and post-game guesses. Invalid bodies/fields/guesses return `400`, unknown games return `404`, unsupported methods return `405` with their `Allow` header, and unsupported content types return `415`. Unknown game IDs are checked before parsing guess bodies. API failures use `{"error": "message"}` JSON, unexpected server errors use a generic `500` message, and API responses carry `Cache-Control: no-store`.

Verified on 2026-10-26 using Python 3.13.1, Flask 3.1.3, and pytest 9.1.1: `.venv/bin/python -m pytest tests/test_game.py tests/test_words.py tests/test_api.py` — **240 passed (76 engine, 65 word-management, and 99 API tests)**. Real local HTTP checks passed for both `python server.py` and Gunicorn 26.2.0 with one worker, including complete games, GET state retrieval, answer omission during play, answer disclosure after completion, rejection of post-game guesses, malformed JSON, unknown IDs, and existing static-file routing. Both temporary server processes were stopped after verification.

Local startup: `.venv/bin/python server.py` (loopback port 5000, or the `PORT` environment variable). Production entry point: `.venv/bin/gunicorn --workers 1 --bind 0.0.0.0:$PORT server:app`. Keep one worker and one instance while game storage is process-local; games are lost on restart. At the Phase 3 checkpoint, the root served an empty HTML placeholder; the implemented browser client and later verification are documented in the subsequent phases.

## Phase 4: Browser Interface

### Dependencies on Previous Phases

Phases 1–3 must be complete and passing. The browser presents server state and sends requests through the established API.

### Files Involved

- `static/index.html` — page structure, controls, and SVG Hangman.
- `static/style.css` — styling and responsive layout.
- `static/app.js` — input, fetch requests, and state rendering.
- `server.py` — existing page and asset routes, preserved without backend changes.
- `tests/test_browser.py` — real-browser tests, temporary Flask HTTP server, and controlled server-side vocabulary fixtures.
- `requirements.txt`, `TODO.md` — browser test tooling and verified progress.

### Tasks

- [x] Build the HTML, CSS, and JavaScript interface and serve it through Flask.
- [x] Add labeled Easy, Medium, and Hard difficulty controls and a New Game button.
- [x] Create games using `fetch()` with `POST /api/games` and keep the returned game ID for subsequent requests.
- [x] Use `GET /api/games/{game_id}` to retrieve and render the current game without starting another one.
- [x] Display the masked word, all previous guesses, incorrect guesses, remaining guesses, and current game status.
- [x] Add a clickable A–Z alphabet keyboard and physical keyboard letter input.
- [x] Route both input methods through the same guess-request flow; ignore modifier shortcuts and typing within unrelated form controls.
- [x] Disable guessed letters, block duplicate submissions while a request is pending, and disable guessing after completion.
- [x] Draw six Hangman body parts in SVG, updating only from the incorrect-guess count returned by the server.
- [x] Display win and loss messages and reveal the answer received from the server after completion.
- [x] Implement restart through a new game ID and reset the pattern, keyboard, drawing, guess history, and messages.
- [x] Make the layout usable at common desktop and mobile widths with readable labels and usable controls.
- [x] Show loading and request-error feedback; update guesses and remaining attempts only from accepted server state.
- [x] Ignore delayed responses from an earlier game after New Game is selected, and prevent overlapping submissions from corrupting the displayed state.
- [x] Keep the selected hidden word and all game-rule decisions out of active browser state and source.
- [x] Select and document real-browser test tooling, add its dependencies and setup steps, and write initial automated interaction tests as the interface is built.

### Testing Requirements

- [x] Verify Flask serves `/`, JavaScript, and CSS successfully.
- [x] Run real-browser tests for difficulty selection, game creation, mouse guesses, physical keyboard guesses, and GET-based state rendering.
- [x] Verify drawing progression, history, remaining guesses, and disabled keys match server responses.
- [x] Verify completed-game feedback and that New Game resets all displayed and interactive state.
- [x] Manually check desktop and mobile layouts and usable keyboard input.

  **C — Additional optional QA:** **Completed — confirmed by student.** The latest instruction explicitly confirms physical-keyboard and desktop/mobile-layout checks, satisfying all parts of this manual item. These personal checks supplement existing automated viewport/keyboard tests and inspected recording evidence. No independent AI observation of the student's manual session or unreported device/screen-reader testing is claimed.

- [x] Run the existing backend suite and initial browser tests successfully.

### Completion Criteria

- [x] A player can complete and restart a game entirely through the browser.
- [x] Both input methods, SVG drawing, responsive layout, and API communication work together.
- [x] Initial browser tests and all earlier tests pass; active answers remain on the server.

Implementation: the vanilla HTML page provides labeled difficulty radios, New Game and Refresh controls, a six-part SVG drawing, masked-letter slots, history, counters, and an A–Z keyboard. CSS uses an original ivory, forest-green, and clay palette, responsive grid layouts, visible focus indicators, and reduced-motion support. Normal text and button palette contrast was checked; desktop and mobile screenshots were visually inspected at 1280×1000, 390×844, and 320×740. The narrow-screen grid was corrected and is protected by internal-overflow regression checks.

Event flow: New Game sends `POST /api/games` with the selected difficulty. Letter clicks and physical-keyboard events share one `POST /api/games/{id}/guess` handler. Refresh retrieves the existing game through `GET /api/games/{id}`. All pattern, history, counter, drawing, and outcome updates render server responses; the browser does not choose words, determine correct letters, calculate remaining guesses, or decide win/loss. Answer text is retained and displayed only after a server-reported outcome.

Only one guess request can be pending. New Game cancels an earlier request; operation-identity checks also prevent delayed responses and cleanup callbacks from changing a newer game. Network failures, unreadable responses, server errors, and request timeouts show feedback. A failed guess pauses guessing until Refresh confirms server state, because an interrupted response does not prove the guess was rejected. Missing games prompt a new round. The existing Python engine, word manager, Flask server, and word lists were unchanged.

Browser tooling: `pytest-playwright` was added to `requirements.txt`. For a fresh environment, run `python -m pip install -r requirements.txt`, then `python -m playwright install chromium`. Run the complete suite with `python -m pytest tests/test_game.py tests/test_words.py tests/test_api.py tests/test_browser.py`. An existing Google Chrome installation can be used by adding `--browser-channel=chrome`; that is the verified configuration here. The test fixture starts and stops its own temporary Flask server and keeps deterministic answers in Python test fixtures, outside static assets.

Historical Phase 4 checkpoint, 2026-10-26, using Python 3.13.1, pytest 9.1.1, pytest-playwright 0.10.0, Playwright 1.64.1, and Chrome 156.0.8078.48: `.venv/bin/python -m pytest tests/test_game.py tests/test_words.py tests/test_api.py tests/test_browser.py --browser-channel=chrome` — **256 passed (240 existing backend tests and 16 browser tests)**. Browser checks covered initial controls, all difficulties, both input methods, keyboard-only navigation, GET refresh, history/drawing/counters, win and loss, restart, duplicate/modifier/form-input suppression, network recovery, pending guesses, stale responses after New Game, and desktop/mobile overflow with no console errors in normal responsive flows. JavaScript syntax and Git whitespace checks passed. Temporary verification servers and browsers were stopped. Phase 5 and later work was still pending at that historical checkpoint.

Historical audit follow-up (2026-10-26): confirmed and fixed lost keyboard focus, incomplete response validation, incorrect clearing of an existing round after a creation-request 404, and missing live-region progress information. That checkpoint passed **276 tests (240 backend and 36 automated Chrome browser tests)**, with JavaScript syntax, dependency, whitespace, and checked contrast pairs also passing. [docs/testing.md](docs/testing.md) records those reproduced issues and fixes. The manual item was reopened at that time because automation alone did not establish hands-on testing. It is now complete on the student's explicit layout/keyboard confirmation; the later complete suite passed 296 cases. Spoken screen-reader or additional named-device testing is not inferred or added as an instructor requirement.

## Phase 5: Testing and Debugging

### Dependencies on Previous Phases

The required features from Phases 1–4 and their automated tests are complete. This phase records coverage/debugging and complete browser/server verification; retained optional manual QA does not become an extra instructor submission prerequisite.

### Files Involved

- `tests/test_game.py`, `tests/test_words.py`, `tests/test_api.py` — automated backend coverage.
- `tests/test_browser.py` — separately marked browser integration coverage.
- `tests/conftest.py`, `pytest.ini` — ordinary-test socket isolation and browser markers.
- `docs/testing.md` — manual procedures, actual results, and resolved defects.
- `game.py`, `word_manager.py`, `server.py`, `static/*` — fixes where defects are demonstrated.
- `requirements.txt`, `TODO.md` — test dependencies and verified progress.

### Tasks

- [x] Review all in-scope requirements against the automated suite and add missing behavioral coverage.
- [x] Exercise correct and incorrect guesses, repeated letters in a word, duplicate guesses, invalid input, and uppercase input.
- [x] Verify win and loss paths, six-incorrect-guess behavior, and rejection of guesses after completion.
- [x] Verify New Game changes the game ID and resets every browser control and display.
- [x] Verify multiple games retain independent state through complete API and browser flows.
- [x] Add complete real-browser integration tests for start, guess, finish, and restart using controlled server-side fixtures.
- [x] Verify hidden-word security in active JSON, initial HTML, browser state, static resources, and error responses.
- [x] Use Chrome Developer Tools Network and Console panels to inspect request methods, paths, JSON payloads, status codes, response fields, and JavaScript errors.

  **C — Additional optional QA:** **Completed — confirmed by student.** The student explicitly confirms personal Google Chrome Developer Tools Network/Console inspection, HTTP request methods, and JSON payloads/responses. This supplements the previously accepted inspection covering this checklist's status-code, response-field, and error-review scope. The AI did not independently perform or observe that session, and the student is not asked to repeat it.

- [x] Test unknown game IDs and IDs invalidated by a server restart, failed network requests, non-JSON error responses, and server errors; display actionable feedback and permit a new game.
- [x] Check that pending requests cannot apply an old game's response to a newly created game.
- [ ] Record manual test steps and actual results in `docs/testing.md`, including tested browser and viewport sizes.

  **C — Additional optional QA:** Optional supporting-document task, not an instructor-required upload. The manual activities themselves are now confirmed complete by the student. This particular checkbox remains open because `docs/testing.md` has not been updated with their steps/results and browser/viewport details; only TODO.md may be changed in this review. A later authorized documentation edit can record the confirmations and existing video evidence without rerunning the checks.

- [x] Fix confirmed defects, add meaningful regression tests, and rerun the affected tests plus the complete suite.

### Testing Requirements

- [x] Run the complete automated suite, including real-browser tests, with no failing tests or unreported skips.
- [x] Manually play Easy, Medium, and Hard games, observe both outcomes across the checks, and restart after completion.

  **C — Additional optional QA:** **Completed — confirmed by student.** The student explicitly confirms personal Easy, Medium, and Hard gameplay. Combined with the already-inspected win/loss/restart recording, this satisfies all three difficulties and both outcomes across the checks. No claim is made that the AI observed the student's personal gameplay or that both outcomes were manually repeated at every level.

- [x] Verify keyboard and pointer input, correct SVG progression, responsive layout, and error recovery.
- [x] Confirm HTTP/JSON behavior and answer-disclosure rules directly in Chrome Developer Tools.

  **C — Additional optional QA:** **Completed — confirmed by student.** The student explicitly confirms inspecting HTTP methods, JSON payloads/responses, and hidden-word protection in Chrome DevTools. Existing engine/API/live-browser checks independently support the same answer-disclosure contract. No new independent AI DevTools session or privacy test is claimed.

- [x] Review and resolve unexplained console errors and failed application requests.

### Completion Criteria

- [x] All in-scope features have appropriate automated or recorded manual verification.
- [x] The complete test suite passes and no known blocking gameplay, API, or answer-disclosure defect remains.
- [x] Testing notes accurately describe results and remaining limitations.

Verified on 2026-10-26: the full discovery command `.venv/bin/python -m pytest --browser-channel=chrome` passed **296 cases: 78 engine, 76 word-management, 102 API, and 40 browser tests; 0 failures, 0 errors, 0 skips**. JUnit XML confirmed the counts. The independent ordinary-test run `.venv/bin/python -m pytest -m "not browser"` passed **256 cases** with 40 browser cases deselected, while socket connections/listeners were blocked. Ordinary tests use Flask's in-process test client and temporary files; only marked browser integration tests start local HTTP listeners. No production service was used.

One new defect was reproduced by eight failing regressions before repair: `splitlines()` silently accepted embedded control/Unicode separators as new word boundaries. Word loading now splits at normalized file newlines so those entries are rejected with their real filename/line; LF, CRLF, and CR files remain supported and unchanged on disk. Added coverage includes last-life validation, partial-pattern losses, concurrent duplicate API requests, completed-game isolation, exact frontend REST requests, API-authoritative rendering, independent browser tabs, and recovery after a stopped/recreated HTTP application. The Python engine, Flask server, frontend, dependencies, and vocabulary contents were preserved.

[docs/testing.md](docs/testing.md) maps all 38 requested cases to evidence and provides manual procedures. The historical automated review passed syntax/dependency/whitespace and viewport checks. At that earlier checkpoint, the record had not received the student's manual confirmations. Personal Easy/Medium/Hard play, physical keyboard, desktop/mobile layouts, Chrome Network/Console, HTTP/JSON, and hidden-word inspection are now **Completed — confirmed by student**. Updating the separate manual-results document is still an optional, distinct task and was not performed in this TODO-only review.

## Phase 6: GitHub and Render Deployment

### Dependencies on Previous Phases

Required implementation/testing from Phases 1–5 is complete and passing, and this project's tested application is publicly deployed. Unchecked optional QA in those phases does not invalidate the verified GitHub/Render work.

### Files Involved

- `.git/` — local version-control metadata.
- `.gitignore`, `README.md`, `requirements.txt` — repository hygiene and reproducible setup.
- `server.py` — importable Flask application for Gunicorn.
- `render.yaml` — prepared Python web-service Blueprint, plus matching README dashboard settings.
- `.python-version` — tested Python 3.13.1 runtime.
- `docs/testing.md`, `TODO.md` — deployment verification and progress.
- External resources: this project's GitHub repository and Render web service.

### Tasks

- [x] Review this project's Git repository and commit history; verify that commits describe the student's original implementation and commit any remaining intended work.
- [x] Verify `.gitignore` excludes virtual environments, Python/test caches, local secrets, and operating-system files.
- [x] Create the student's own GitHub repository, configure its remote, and push the intended branch.
- [x] Review tracked files to ensure source, word lists, tests, and documentation are included and secrets and local environments are excluded.
- [x] Complete `requirements.txt` with tested application and test dependencies, including Flask, Gunicorn, pytest, and the selected browser test tooling; record tested versions and the selected Python runtime.
- [x] Write a README describing assignment scope, architecture, rules, setup, local startup, browser use, automated/manual tests, and the three REST endpoints with example requests and responses.
- [x] Document validation policies, status codes, answer-disclosure behavior, and the limits of in-memory storage.
- [x] Expose an importable Flask application or factory and document the verified Gunicorn entry point.
- [x] Configure Gunicorn with debug disabled and binding to `0.0.0.0` on Render's assigned `PORT`; record the build and start commands in `render.yaml` or the README.
- [x] Configure one worker and one service instance while game storage is process-local; document that games are lost on process restart.
- [x] Create a Render web service connected to this project's GitHub repository and configure its dependency installation and Gunicorn startup.

  **A — Mandatory instructor requirement verified:** Public Render deployment is verified. **Dashboard/startup-settings, deployment logs, and deployment verification: Completed — confirmed by student.** This personal confirmation supplements the working public service/API, reviewed source configuration, local Gunicorn checks, report, and supplied Events evidence. The AI did not independently inspect the dashboard. A settings screenshot or repeat inspection is not required; the log-review items below are now also complete on the accepted confirmation.

- [x] Check build and runtime logs and resolve deployment failures.

  **C — Additional optional QA:** **Completed — confirmed by student.** The latest explicit deployment-log inspection and deployment verification are accepted for this build/runtime-log review, together with existing successful startup/public-service evidence. No unresolved deployment failure is evidenced, and no specific failure or repair is invented. Previously described Gunicorn termination/worker/master messages alone do not establish a crash. The AI did not independently inspect the logs; no repeat is required.

- [x] Obtain a public HTTPS URL and add it and the correct GitHub URL to the README.
- [x] Record the deployed commit and verify that Render is running the intended version; reserve the complete final deployment review for Phase 7.

  **C — Additional optional QA:** Additional QA, completed using explicitly supplied evidence: the user reports that the latest Render Events screenshot shows `471d0cf` successfully deployed on October 28, 2026 at 10:44 AM through Auto-Deploy. That matches reviewed local application commit `471d0cf4751cc0e07ae1360fdcde28b30a113805`. The latest image was not available for independent reopening in this directory; provenance is the user's screenshot description, not a new dashboard inspection. The existing 138e095 image remains a historical capture.


### Testing Requirements

- [x] Verify a clean prepared-source copy and fresh virtual environment can install the pinned requirements, run all tests, and start the documented Flask/Gunicorn entry points locally.
- [x] Verify a fresh clone can install dependencies, run the documented test commands, and start the app using the README.
- [x] Smoke-test the production Gunicorn entry point locally, including API requests and static assets.
- [x] Open the public HTTPS URL in a fresh browser session and verify the page, assets, and all three endpoints.
- [x] Smoke-test a deployed browser game through completion and restart; leave the full deployment verification matrix for Phase 7.
- [x] Verify active deployed responses omit the word and tested 400/404/405/415 responses contain JSON errors without debugging details.
- [x] Confirm production debug/runtime settings and unexpected-error logs in the Render dashboard; live 500 errors were not deliberately induced.

  **C — Additional optional QA:** **Completed — confirmed by student.** The combined startup-settings/deployment-log confirmation is accepted for the dashboard runtime/settings and error-log review. Existing local debug-off/error-handling verification remains valid. No independent AI dashboard access, absence of every possible error, or deliberately induced production 500 is claimed. This additional QA item is not a separate required submission artifact.

- [x] Record actual deployment checks and any observed startup/restart limitations in `docs/testing.md`.

### Completion Criteria

- [x] GitHub contains this project's intended source, tests, word lists, dependencies, and usable documentation.
- [x] Render serves the tested Flask application and browser client at a working public HTTPS URL.
- [x] Fresh-install and deployment smoke checks pass and repository/deployment links are accurate.

Historical documentation/configuration checkpoint, 2026-10-26: `README.md` documented the implementation, three endpoints and example JSON, setup/tests, vocabulary provenance, AI-assisted methodology, known limits, and planned Render steps. GitHub/public-URL fields were placeholders at that checkpoint; they have since been replaced with the actual links. The imported third-party packages were reviewed; `requirements.txt` pins Flask 3.1.3, Werkzeug 3.1.9, Gunicorn 26.2.0, pytest 9.1.1, pytest-playwright 0.10.0, and Playwright 1.64.1. `.python-version` selects the tested Python 3.13.1.

Historical configuration preparation: `render.yaml` passed Render's published JSON Schema and declares a Python web service, free plan, one instance, root health check, requirements-install build, and `gunicorn --workers 1 --threads 1 --bind 0.0.0.0:$PORT server:app`. The Blueprint specifies automatic deployments off; the supplied Events evidence later shows Auto-Deploy on the actual service. That earlier configuration review performed local validation rather than deployment. The public deployment is now verified, and the student's actual configuration/startup-settings inspection is confirmed separately above.

A separate clean-source copy and new virtual environment installed all pinned versions and passed `pip check` and **296 tests (0 failures, 0 errors, 0 skips)**. Real local HTTP checks passed for both Flask and the exact prepared Gunicorn command, covering static assets, all difficulties, creation, retrieval, guessing through completion, answer-disclosure rules, and rejected requests. API examples were checked against Flask's test client. Static files and word lists loaded from an unrelated working directory. Ignore checks covered environments, caches, browser artifacts, `.env` variants, and private keys; those paths were not tracked. All temporary servers stopped. See [docs/testing.md](docs/testing.md#phase-6-local-documentation-and-configuration-verification).

Those initial checks used a prepared source copy rather than a fresh remote clone. Remote-clone verification, public HTTPS checks, actual URL replacement, and deployed-commit verification were completed in the later reviews below. Personal Render startup/log inspection and deployment verification are now student-confirmed. This paragraph records the earlier checkpoint, not current missing work.

Earlier production review, 2026-10-28: the user supplied the actual [Render URL](https://hangman-web-app-6fy1.onrender.com) and [GitHub repository](https://github.com/jgb23002/hangman-web-app). Direct HTTPS and Chrome verified live wins, losses, and restarts at every difficulty, all three endpoints, validation, answer privacy, counters, drawing, and responsive viewports. All 296 local tests passed again. GitHub `main` matched application commit `e70800b71046a349f0cc35107ce8b735774b6774`; public static files matched local bytes. A fresh published clone installed dependencies and passed all tests in the preceding same-day audit, and its documented Flask startup was checked in this review. The configured Gunicorn entry point, module-relative paths, and current Render schema also passed.

At that earlier review, README links and deployment wording were corrected locally. [docs/production_readiness.md](docs/production_readiness.md) and [docs/testing.md](docs/testing.md#october-28-production-verification) record that verification. Documentation and screenshots were subsequently committed in `138e095` and `471d0cf`. The supplied newer Events description records successful deployment of `471d0cf` at 10:44 AM. Render dashboard/startup-settings inspection, deployment-log inspection, and deployment verification are now **Completed — confirmed by student**. No Render-review checkbox remains open. The normal shutdown messages are not crash evidence. No application or deployment change was performed by this TODO review; historical notes do not override the latest accepted confirmations.

## Phase 7: Final Verification and Submission

### Dependencies on Previous Phases

Required application/testing/repository/deployment work is verified, and actual HuskyCT submission is **Completed — confirmed by student**. Use the professor's requirement list for any remaining artifact-acceptance or post-submission access review. Optional QA items are not additional submission prerequisites, and no repeat submission or app redeployment is implied by their open status.

### Files Involved

- `README.md`, `TODO.md`, `docs/testing.md` — final documentation and verification evidence.
- `tests/*` and application files — final regression checks and necessary corrections.
- `docs/Hangman_Development_Report.pdf` — verified two-page, six-section report with three prompts and correct links; explicit limitations wording is optional.
- `docs/submission_checklist.md` — optional planned mapping; not present and not an extra instructor-required deliverable.
- `docs/Hangman_Demonstration.mp4` — inspected recording; measured duration 3:52.75 exceeds the instructor's approximate 2–3-minute target.
- Instructor requirements — the actual list supplied by the student in the current request is authoritative. A separate local assignment-instructions/rubric file is not itself a submission requirement; follow the course's actual upload directions.
- External resources: GitHub, Render, the recording host if used, and HuskyCT.

### Tasks

- [x] Verify deployed Easy, Medium, and Hard selection, game creation, GET-based retrieval, both input methods, drawing, previous and remaining guesses, completion, and restart.
- [x] Verify both deployed win and loss paths, invalid/duplicate guesses, independent games, hidden-word protection, error recovery, and desktop/mobile layouts.
- [x] Run final automated tests against the final source revision and record the results.
- [x] Review the GitHub repository, correct branch, README instructions, dependency list, and public deployment link.
- [x] Confirm that the deployed revision matches the source being submitted; redeploy and recheck if final fixes are made.

  **C — Additional optional QA:** Additional QA, completed for the application version: the user-supplied Events evidence identifies deployed `471d0cf`, matching the reviewed application/test/configuration revision. Current local changes are TODO/report/video artifacts, not application code. This records application-source alignment; it does not claim that an eventual new documentation-only commit is already deployed. No unnecessary redeploy is required to publish this checklist; reassess only if application/configuration code changes.

- [x] Write and verify the instructor-required 1–2 page development report with its six required sections.

  **A — Mandatory instructor requirement verified:** Mandatory report work is complete. The current `docs/Hangman_Development_Report.pdf` (923,167 bytes) was reopened and rendered: two pages; Development Process, Application Implementation, Testing and Verification, Cloud Deployment, Challenges and Problem-Solving, and Reflection; three representative student prompts; accurate test figures and GitHub/Render links. Scope correction: the earlier AI-generated report item added an explicit remaining-limitations discussion. Adding a storage/restart-limit sentence is an optional editorial improvement, not an instructor requirement and not a reason to call this report incomplete. No such sentence was added or claimed. The original item's implementation/architecture/AI/debugging/testing/deployment topics remain covered by the six sections. Earlier AI wording retained for transparency: “Write a 1–2 page development report covering the original implementation, architecture and decisions, AI-assisted workflow, debugging, testing, deployment, and remaining limitations.”

- [x] Include 2–3 representative AI prompts from this project's own development and explain how their outputs were reviewed, adapted, and verified.

  **Verified deliverable evidence:** Verified in `docs/Hangman_Development_Report.pdf`, page 2: three labeled excerpts (Planning; Flask Implementation; Testing and Debugging) match this student's development prompts. Development Process, Challenges and Problem-Solving, and Reflection explain phased review, adaptation, debugging, and test verification. The report was inspected directly; this is not inferred from the instructor's transcript.

- [x] Include accurate GitHub and Render URLs and actual testing results in the report where required.

  **Verified deliverable evidence:** Verified in the PDF: both displayed URLs and actual hyperlink targets match `https://github.com/jgb23002/hangman-web-app` and `https://hangman-web-app-6fy1.onrender.com`. Its 296 passing cases (78/76/102/40) and approximately 99% combined Python coverage agree with prior executed verification. Existing successful public-link checks were reused; the application tests were not rerun.

- [ ] Record a 2–3 minute demonstration showing the public game, difficulty selection, guessing, drawing, finished-game feedback, and restart.

  **B — Unresolved combined acceptance criterion:** The recording exists and its required content is verified. The available local file still measures 232.746896 seconds (3:52.75), and no shorter export or instructor acceptance was confirmed. Actual HuskyCT submission is **Completed — confirmed by student**; that does not establish the submitted recording's exact version or duration compliance. Resolve or obtain instructor acceptance of the known deviation if a follow-up is needed/permitted. Never describe 3:52.75 as within three minutes.

- [ ] Verify recording duration, playback, readability, and access permissions.

  **D — Follow-up verification not yet confirmed:** Duration measurement, local playback/decoding, and readability were already checked. The measured **3:52.75** is accurately recorded even though it exceeds the approximate target. This item remains open solely for final reviewer access/permissions to the submitted video or link. Submission itself is confirmed; no new upload, replay, or resubmission is required merely for AI observation. Duration acceptance belongs to the separate duration criteria.

- [ ] Compare every deliverable with the official assignment instructions and rubric; confirm filenames, formats, access requirements, and any additional submission details.

  **D — Follow-up verification not yet confirmed:** The supplied instructor requirements were mapped, the report/application were checked, and the known duration deviation is documented. Actual submission is confirmed. A comprehensive check of the final submitted filenames, formats, permissions, and any additional course-specific directions was not confirmed. Confirm only that remaining review; no separate local rubric file, fixed screenshot count, QA document, or repeated gameplay is imposed. Comparison can honestly record a deviation without claiming it is compliant.

- [x] Prepare the HuskyCT submission with the required repository URL, Render URL, report, demonstration file/link, and any other confirmed deliverables.

  **A — Mandatory instructor requirement:** **Completed — confirmed by student.** The student explicitly confirms completing the actual HuskyCT submission, so the preparation/submission workflow is recorded as complete on user-reported evidence. No AI upload, independent portal inspection, receipt inspection, or reviewer-access test is claimed or required to accept that confirmation. The exact submitted file versions and any video-duration acceptance remain separate, unconfirmed matters; this checkbox does not certify them.

- [x] Review every remaining checkbox and completion claim; leave unfinished or unverified work unchecked.

### Testing Requirements

- [x] Run the final engine, word management, API, and real-browser suites successfully.
- [x] Perform a final public-URL smoke test in a fresh session, including one finished game and a restart.
- [ ] Verify report length, prompt count, recording length, link destinations, and reviewer access.

  **D — Follow-up verification not yet confirmed:** Report length, three prompts, measured recording length, and link destinations have been verified. The measured recording length is **3:52.75**; measuring it does not certify it meets the target. This item remains unchecked only for final reviewer access, which was not confirmed. Do not repeat report, duration-measurement, or automated checks. The separate duration criteria remain open for the known overrun.

- [ ] Review the prepared HuskyCT materials against the rubric and verify that uploaded/exported files open correctly.

  **D — Follow-up verification not yet confirmed:** **Actual submission: Completed — confirmed by student.** The separate activity of opening/checking the uploaded/exported artifacts against the course requirements and confirming reviewer access was not explicitly confirmed. This item concerns that remaining follow-up review, not whether a submission happened. It may be completed by confirming an already-performed artifact/access review; the student need not repeat it solely for AI observation.


### Completion Criteria

- [x] The deployed app and submitted source revision have passed final verification.

  **A — Mandatory instructor requirement verified:** Application verification remains complete using the existing 296-case result, recorded all-difficulty live checks, unchanged application files and supplied deployment evidence for `471d0cf`. Personal Easy/Medium/Hard gameplay, keyboard/layout checks, Chrome DevTools/HTTP/JSON/privacy inspection, Render startup/log/deployment inspection, and actual HuskyCT submission are **Completed — confirmed by student**. These are accepted student-reported facts, not independent AI observations. Video-duration and final artifact/access criteria remain separate and unresolved.

- [ ] The 1–2 page report includes 2–3 representative prompts, and the 2–3 minute recording is viewable.

  **B — Unresolved combined acceptance criterion:** The report's two pages and three prompts are verified, and actual submission is student-confirmed. The local recording is viewable but measures 3:52.75; no shorter/accepted version or final reviewer-access confirmation was supplied. This combined criterion remains open for its video-duration/access part, not for the already-complete report or submission.

- [x] All confirmed submission requirements are accounted for and the HuskyCT submission package is prepared.

  **A — Mandatory submission preparation:** **Completed — confirmed by student.** The supplied requirement list is accounted for, the package was prepared, and actual HuskyCT submission occurred. Accounting for a requirement includes recording its known deviation: this checkbox does not certify that the 3:52.75 recording meets the approximate target or that reviewer access was tested. Those matters remain under their own unchecked items. The earlier AI note unnecessarily treated package preparation as a duplicate all-criteria-accepted gate; that interpretation is corrected without changing the original task wording.

- [x] Documentation and task statuses accurately reflect the work actually completed and verified.
