# Phase 5 — Testing and Debugging

Verification date: October 26, 2026. The complete suite passed **296 tests**:
**296 passed, 0 failed, 0 errors, 0 skipped**. Parametrized cases are counted
individually; running the same case in multiple commands does not increase this
total.

| Module | Cases passed |
| --- | ---: |
| `tests/test_game.py` | 78 |
| `tests/test_words.py` | 76 |
| `tests/test_api.py` | 102 |
| `tests/test_browser.py` | 40 |
| **Total** | **296** |

## Test isolation and commands

Ordinary engine, vocabulary, and API tests use Python objects, temporary files,
and Flask's in-process test client. They require no Gunicorn process, Render
service, production URL, listening server, or browser binary.
`tests/conftest.py` rejects socket connections and listeners in those tests.
`pytest.ini` registers the `browser` marker; only the explicit browser
integration tests are exempt from that guard.

Run the ordinary tests:

```sh
.venv/bin/python -m pytest -m "not browser"
```

Executed result: **256 passed, 40 browser cases deselected**. Deselection here
is intentional test selection, not a skipped case in the complete run.

Run everything, including the browser integration tests:

```sh
.venv/bin/python -m pytest --browser-channel=chrome
```

Executed result: **296 passed**. JUnit XML independently reported 296 cases,
0 failures, 0 errors, and 0 skips. Reports/artifacts were written to a temporary
directory outside the repository. The browser tests use a temporary loopback
Flask server and fixed, server-side test vocabulary. All browser/server fixtures
were closed at teardown. No external live service was used. Automated viewport
checks covered 1280×1000, 1024×768, 768×1024, 390×844, and 320×740. A test fixture
checked for uncaught JavaScript errors across every browser page, while normal
responsive flows also checked Console errors; intentionally induced network/HTTP
failures were handled as test inputs.

For a new environment, install `requirements.txt`. Use an installed Google
Chrome with `--browser-channel=chrome`, or run
`python -m playwright install chromium` and omit that channel argument.

Additional executed checks passed:

```sh
node --check static/app.js
git diff --check
.venv/bin/python -m pip --disable-pip-version-check --no-cache-dir check
```

The JavaScript interpreter is only a syntax-check tool; the application still
uses vanilla HTML/CSS/JavaScript served by Flask.

## Defect found and fixed in Phase 5

The word loader used `str.splitlines()`, which interprets several embedded
control characters and Unicode separators as additional line boundaries.
A malformed entry such as `rab\vbit` could silently become the two accepted
words `rab` and `bit`, rather than raising an invalid-entry error.

Eight new regression cases failed before the fix. The loader now splits at LF
after Python text I/O has normalized normal LF, CRLF, and CR file endings.
Embedded non-file separators stay inside their entry and are rejected by the
ASCII-letter validation, with the correct filename and line number. Three
additional newline-format cases verify continued LF/CRLF/CR support and confirm
the original files are not rewritten.

No assertions were weakened or cases skipped to resolve the failures. The
engine, Flask server, frontend, vocabulary contents, and dependencies were
unchanged in this phase. Earlier browser-audit fixes remain covered by regression
tests in the historical record below.

## Coverage of the requested 38 cases

Test names below identify representative coverage; parametrized tests contain
multiple input cases.

| # | Required behavior | Verification |
| --- | --- | --- |
| 1 | Correct letter | Game: `test_correct_guess_reveals_all_positions_without_costing_an_attempt` |
| 2 | Incorrect letter | Game: `test_incorrect_guesses_each_cost_one_attempt` |
| 3 | Repeated letters in a word | Game: repeated-position test above; browser mouse/keyboard flow |
| 4 | Uppercase/lowercase | Game: `test_uppercase_word_and_guesses_are_normalized`; API correct/incorrect guesses |
| 5 | Empty guesses | Game: `test_invalid_guesses_leave_existing_state_unchanged`, empty-string case |
| 6 | Numeric guesses | Same game test, numeric/string-numeric cases; API invalid letters |
| 7 | Symbol guesses | Same game test, punctuation cases; API invalid letters |
| 8 | Multiple characters | Same game test, multi-character cases; API invalid letters |
| 9 | Duplicate guesses | Game: `test_duplicate_guesses_are_rejected_without_state_changes` |
| 10 | Loss on sixth miss | Game: `test_loss_occurs_on_exactly_the_sixth_incorrect_guess` |
| 11 | Win after unique letters | Game: `test_complete_win_reveals_answer_only_on_final_guess` |
| 12 | No guesses after either outcome | Game: `test_finished_games_reject_further_guesses_without_changes` |
| 13 | Hide active answer | Game: win/loss progression and JSON-serialization tests |
| 14 | Reveal completed answer | Game: complete win/loss and every-status serialization tests |
| 15 | Load Easy | Words: `test_loads_each_difficulty`, Easy parameter |
| 16 | Load Medium | Same words test, Medium parameter |
| 17 | Load Hard | Same words test, Hard parameter |
| 18 | Invalid difficulty | Words: `test_rejects_invalid_difficulties`, both public methods |
| 19 | Empty lists | Words: `test_rejects_empty_or_blank_only_lists` |
| 20 | Invalid entries | Words: invalid-entry, UTF-8, and embedded-separator regressions |
| 21 | Remove duplicates | Words: `test_normalizes_words_skips_blanks_and_removes_duplicates` |
| 22 | Random choice within difficulty | Words: membership and controlled first/last-choice tests |
| 23 | Valid creation | API: `test_create_returns_complete_safe_initial_state` |
| 24 | Invalid difficulty | API: `test_invalid_difficulty_does_not_create_a_game` |
| 25 | Different game IDs | API: `test_ids_are_unique_and_games_are_independent`; collision regression |
| 26 | Retrieve state | API: `test_get_returns_current_state_without_modifying_it` |
| 27 | Missing game returns 404 | API: `test_unknown_games_return_404`, GET and POST parameters |
| 28 | Valid guesses | API: `test_correct_and_incorrect_guesses_use_engine_rules` |
| 29 | Invalid guesses | API: `test_invalid_letters_do_not_change_the_game` |
| 30 | Duplicate guesses | API: `test_duplicates_are_consistently_rejected`; concurrent-duplicate test |
| 31 | Malformed JSON | API: `test_malformed_json_has_a_clear_error`, both POST endpoints |
| 32 | Hide active API answer | API: initial-state, complete-game progression, and error-disclosure tests |
| 33 | Reveal API answer only at end | API: `test_full_games_reveal_answers_only_after_completion`, both outcomes |
| 34 | Completed games reject guesses | Same API test; mixed last-life/partial-pattern regression |
| 35 | Three JavaScript REST endpoints | Browser: `test_frontend_uses_the_three_required_endpoints_with_expected_json` records actual methods, paths, and payloads |
| 36 | No independent browser answer selection | Reviewed `static/app.js` request/render flow; browser supplied-state test verifies rendering follows the API rather than predicting a letter's correctness |
| 37 | Identify manual-only behavior | Pending manual procedures below distinguish automated Chrome/viewport evidence from hands-on verification |
| 38 | Detailed manual checklist | Each procedure below gives steps and expected results; none is claimed as executed |

Additional Phase 5 coverage includes a win on the last life after invalid and
duplicate guesses, a loss after correct positions were revealed, four
simultaneous duplicate API submissions through independent test clients,
completed-game isolation, and two browser games remaining independent through
win/loss, refresh, and restart. A further browser test stops and recreates its
local HTTP listener with a fresh application on the same port, verifies that the
old game ID returns 404, and starts a new playable game.

The frontend contract test records exactly these requests for its controlled
flow: `POST /api/games` with only `difficulty`,
`POST /api/games/{id}/guess` with only `letter`, and
`GET /api/games/{id}`. Code review confirmed selection remains in Python;
JavaScript reads public response fields, validates response shape, and renders
server-supplied patterns, counters, and statuses.

## Manual test setup — not executed in this phase

Use `.venv/bin/python server.py` and open `http://127.0.0.1:5000` for normal
random-vocabulary play. For repeatable manual expectations, the optional fixture
below uses temporary server-side words on port 5001. It adds no public
answer-selection endpoint and changes no project word files.

```sh
.venv/bin/python - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
from server import create_app
from word_manager import WordManager

with TemporaryDirectory(prefix="hangman-manual-") as directory:
    vocabulary = Path(directory)
    for difficulty, word in {
        "easy": "apple",
        "medium": "balloon",
        "hard": "refrigerator",
    }.items():
        (vocabulary / f"{difficulty}.txt").write_text(word + "\n", encoding="utf-8")
    application = create_app(word_manager=WordManager(vocabulary))
    application.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False)
PY
```

Open `http://127.0.0.1:5001` when using that fixture. Stop it with Ctrl+C.
This is a manual test harness, not a dependency of ordinary pytest tests. Its
setup and expected mask lengths were validated in-process without starting the
manual HTTP server or interacting with a browser. Physical devices need a URL
reachable from that device; the loopback URLs above refer to the development
computer.

## Detailed pending manual checklist

All items below are **not run**. Record date, browser/version, OS/device, viewport,
actual result, and any console/network evidence when someone executes them.

- [ ] **Start each difficulty.** Select Easy, Medium, and Hard and click New Game.
  With the manual fixture, expect 5, 7, and 12 masked slots respectively, six
  remaining misses, no history, no body parts, and an enabled alphabet. Check the
  badge matches the new game's difficulty.
- [ ] **Mouse and physical keyboard.** In Medium, click L, then type uppercase A.
  Expect `_ a l l _ _ _`, history `l · a`, six misses remaining, disabled A/L,
  and no body parts. Type L again and try its disabled button: history, counter,
  and network request count must stay unchanged.
- [ ] **Invalid keys and ordinary shortcuts.** Try digits, punctuation, held keys,
  Ctrl/Cmd shortcuts, and typing while a difficulty radio has focus. Expect no
  invalid guess submissions, no consumed attempts, and working browser shortcuts.
- [ ] **Complete a win.** In a fresh Medium game, guess B, A, L, O, N. Expect
  repeated positions to appear together, then `won`, answer BALLOON, and all
  letter buttons disabled. Further clicks/letters must send no guess requests.
- [ ] **All six drawing stages and a loss.** In a fresh Medium game, guess
  C, D, E, F, G, H. Expect remaining counts 5, 4, 3, 2, 1, 0 and exactly one
  additional part each time: head, body, left arm, right arm, left leg, right leg.
  The fifth miss must still be playing; the sixth must show the loss and BALLOON.
- [ ] **Win and lose at every level.** Repeat both outcomes for each fixture.
  Winning unique letters are A/P/L/E for Easy, B/A/L/O/N for Medium, and
  R/E/F/I/G/A/T/O for Hard. Six misses can be B/C/D/F/G/H for Easy,
  C/D/E/F/G/H for Medium, and B/C/D/H/J/K for Hard.
- [ ] **Restart and two tabs.** After both outcomes, start another game without
  reloading. Confirm a new ID, cleared answer/history/drawing, fresh mask/counter,
  and enabled letters. Play in two tabs, finish/restart one, then Refresh the
  other: it must retain its own ID and progress.
- [ ] **Keyboard navigation and focus.** Use Tab/Shift+Tab, skip link, radio-arrow
  keys, Enter/Space on New Game and alphabet buttons. Confirm visible focus,
  sensible next-letter/recovery focus, and preserved focus if you move to a
  different control during a slow request.
- [ ] **Chrome Developer Tools HTTP/JSON.** In Network, inspect all three API
  methods/paths, JSON request fields, status codes, and response fields.
  Creation must return 201, successful GET/guess 200, invalid/duplicate requests
  400, unknown IDs 404, and unsupported POST content types 415. Confirm `word`
  is absent throughout active play and present only after an outcome. Review
  Console for unexplained errors; do not count intentional offline failures as
  unexplained defects.
- [ ] **Offline, slow, and interrupted requests.** Enable Network offline or
  throttling, submit a guess, and restore the connection. The old confirmed
  state must remain, guessing must pause until Refresh succeeds, and duplicate
  submissions must be blocked. During a delayed guess, choose New Game:
  its fresh board must survive any late old response.
- [ ] **Server restart.** With a game active, stop and restart the local server.
  Refresh should report that the game is unavailable and offer New Game.
  A fresh round should work with a new ID.
- [ ] **Physical mobile devices and orientation.** Test real iOS Safari and
  Android Chrome taps, portrait/landscape, scrolling, text enlargement, and
  long Hard masks. The automated 320–1280 px viewport checks do not certify
  physical touch or mobile-browser behavior.
- [ ] **Other browsers, zoom, and motion preference.** Check desktop Safari or
  Firefox, 200% zoom, readable contrast, visible focus, and reduced-motion OS
  preferences. Look for clipped word slots, keys, status text, or refresh controls.
- [ ] **Screen reader.** With VoiceOver or NVDA, verify the actual spoken pattern,
  last guess, counter, errors, outcome, and final answer; check repetition and
  focus transitions. Automated accessibility-tree assertions do not verify speech.

## Remaining limitations and Phase 5 status

No confirmed blocking gameplay/API/answer-disclosure defect remains in the
executed checks. Games are intentionally process-local and disappear on restart;
deployment must use one worker/instance until shared storage is introduced.
Word lists are cached when a WordManager is constructed. Automated browser
coverage used installed Chrome and emulated viewports, not physical devices.

Hands-on browser play, Developer Tools panel inspection, cross-browser/device
checks, and spoken screen-reader testing remain pending. The corresponding
Phase 5 checkboxes stay open. This phase's automated work is verified; the
entire phase must not be claimed complete until its remaining manual criteria
are actually satisfied. No deployment or submission work was performed.

---

# Historical browser audit — October 26, 2026

This audit compared the current HTML, CSS, and JavaScript with Phase 4 of
`TODO.md` and the relevant browser, REST, and game-rule sections of
`SPECIFICATION.md`. The Python engine, word manager, Flask API, vocabulary, and
dependency list were preserved. The pre-existing uncommitted Phase 4 work was
retained.

## Confirmed issues and fixes

| Issue reproduced in Chrome | Fix and regression coverage |
| --- | --- |
| Disabling a focused New Game or alphabet button discarded focus. Keyboard users lost their position after a request. | Request cleanup restores an enabled initiating control, advances to the next available letter, or focuses Refresh/New Game when appropriate. Deliberate focus changes during a request are preserved. |
| Valid JSON with negative/excess counters, malformed letter histories, invalid difficulty/pattern, or missing terminal answers replaced valid UI state. | Validate the response contract before assignment. Reject invalid responses, retain the last confirmed state, and require a successful GET before guessing resumes. Validation does not calculate correctness, remaining guesses, or outcomes. |
| A 404 while creating a new game cleared a still-valid existing round. | Distinguish a failing creation request from GET/guess requests for a missing game. Creation errors preserve the current round for recovery; a missing game still offers a fresh start. |
| The live status lacked the current pattern/counter, and a busy ancestor could defer status feedback. | Include a visually hidden public-state summary in the live region and move `aria-busy` to the keyboard. Tests verify the accessibility-tree text and busy-region placement. Spoken screen-reader behavior still requires manual confirmation. |

Eleven focused regression cases reproduced these issues before the fixes. All
pass after the fixes. Rendering continues to use server-provided state; the
browser neither selects answers nor independently decides whether a letter is
correct or a game has ended. Answer text is accepted only for a server-reported
terminal state. Text is inserted with `textContent`.

## Automated verification actually executed

The existing baseline passed all 256 tests. The final complete discovery run
passed **276 tests, with no failures or skips**:

| Test file | Passed |
| --- | ---: |
| `tests/test_game.py` | 76 |
| `tests/test_words.py` | 65 |
| `tests/test_api.py` | 99 |
| `tests/test_browser.py` | 36 |

Run the suite using the project's virtual environment:

```sh
.venv/bin/python -m pytest --browser-channel=chrome
```

The executed run additionally directed test artifacts to a temporary directory
and enabled screenshots on failure. Browser tests launched actual headless
Google Chrome and a temporary Flask HTTP server with deterministic vocabulary
provided only by Python test fixtures. Browser instances and the HTTP listener
were stopped during teardown. These are automated browser checks.

The browser suite verifies:

- All three difficulties, clickable letters, uppercase/lowercase physical-key
  events, and keyboard-only navigation.
- Correct letters in every matching position, wrong-letter history, duplicate
  suppression, and accurate server-provided counters.
- Every SVG stage, completed win/loss feedback, blocked post-game requests, and
  the full reset after New Game.
- GET-based refresh, network failure after an accepted guess, timeouts, HTTP
  errors, non-JSON responses, malformed state data, and missing-game recovery.
- Pending-guess suppression, delayed responses after New Game, focus restoration,
  and preservation of deliberate focus movement.
- Answer omission in active API responses, DOM, and static resources; raw error
  bodies are not rendered.
- Viewports of 1280×1000, 1024×768, 768×1024, 390×844, and 320×740, including
  internal panel overflow and browser console/runtime errors in normal flows.
- Public pattern/counter text in the accessibility tree. This checks structure
  and does not certify actual screen-reader announcements.

Additional checks passed:

```sh
node --check static/app.js
git diff --check
.venv/bin/python -m pip --disable-pip-version-check --no-cache-dir check
```

The existing local JavaScript interpreter was used only for syntax checking;
the frontend remains vanilla JavaScript served by Flask, with no frontend build
or separate server. Dependency checking reported no broken requirements.

Calculated contrast ratios for checked foreground/background pairs were
11.74:1 for main text, 4.80:1 for muted text, 9.65:1 for the primary button,
5.13:1 for error text, and 5.40:1 for footer text. These checks cover those
specific pairs, rather than a complete accessibility certification.

## Manual browser checks still pending

No hands-on manual browser session, physical-device interaction, screen-reader
session, or Chrome Developer Tools panel inspection was performed in this
audit. Automated viewport checks are not physical-device tests. The earlier
Phase 4 screenshot review remains historical evidence of visual inspection.
The manual Phase 4 checkbox is open so it does not imply those remaining checks
have passed.

- [ ] Play complete wins and losses in a desktop browser; check all difficulties,
  on-screen keys, repeated letters, counters, drawing stages, and a fresh round.
- [ ] Use a physical keyboard: Tab/Shift+Tab, radio-arrow navigation, Enter/Space,
  uppercase/lowercase guesses, and modifier shortcuts. Verify visible focus and
  recovery after a failed request and game completion.
- [ ] On real iOS Safari and Android Chrome devices, check touch targets, portrait
  and landscape layouts, scrolling, and enlarged text. Also check desktop zoom
  at 200% and a second desktop engine such as Safari or Firefox.
- [ ] With VoiceOver or NVDA, confirm the masked pattern, remaining count, errors,
  and completed-game answer are announced intelligibly, without excessive
  repetition, and that focus transitions remain understandable.
- [ ] In Chrome Developer Tools, inspect the three endpoint methods, JSON bodies,
  responses, status codes, and Console. Confirm `word` is absent while playing
  and present after completion. Use offline/throttling controls to check Refresh
  recovery and New Game while a request is pending.

No Phase 5 or deployment/submission checklist item is marked complete by this
audit record.

## Phase 6 local documentation and configuration verification

On October 26, 2026, the documentation and deployment-configuration portion was
checked without deploying. Source, imports, and current dependency metadata were
reviewed before writing README.md. Six direct packages were pinned to their
tested versions: Flask 3.1.3, Werkzeug 3.1.9, Gunicorn 26.2.0, pytest 9.1.1,
pytest-playwright 0.10.0, and Playwright 1.64.1. Python 3.13.1 is selected in
`.python-version`.

Executed local checks:

- A clean prepared-source copy and new virtual environment installed only the
  application/test requirements; each of the six installed versions matched its
  pin. `pip check` reported no broken requirements.
- The complete suite in that clean environment passed **296 cases: 78 engine,
  76 word-management, 102 API, and 40 browser tests**, with 0 failures, 0 errors,
  and 0 skips. The command was `python -m pytest --browser-channel=chrome` with
  temporary artifact and JUnit XML output paths.
- `render.yaml` was parsed and validated locally against the JSON Schema from
  `https://render.com/schema/render.yaml.json`. YAML/schema tooling was installed
  only into a separate temporary validation directory, not app dependencies.
  Checks confirmed a Python web service, free plan, one instance, `/` health
  check, disabled automatic deployment, and the one-worker Gunicorn command.
- Both `python server.py` and the prepared Gunicorn command started against the
  clean copy. Actual local HTTP requests verified `/`, JavaScript/CSS, all three
  difficulties, create/get/guess, a complete game, active-answer omission,
  terminal answer disclosure, malformed JSON, unknown IDs, and post-game errors.
  The temporary processes and their workers were stopped afterward.
- From an unrelated working directory, the clean environment imported the app,
  served the exact static-file bytes, loaded 169/156/181 words for the three
  difficulties, and created games through Flask's test client.
- Every README JSON example was compared with the real API using temporary
  server-side vocabulary and normalized illustrative IDs.
- Git ignore checks verified environments, Python/pytest caches, browser test
  artifacts, `.env` variants, and `.pem`/`.key` files are excluded; none of those
  paths was tracked. `.env.example` remains permitted as a future public template.

The deployment metadata matches Render's [Blueprint reference](https://render.com/docs/blueprint-spec),
[Python-version rules](https://render.com/docs/python-version), and
[port requirements](https://render.com/docs/web-services#port-binding).
These checks establish local configuration/schema validity, not a successful
Render Linux build or hosted deployment. No Render service was created, no
source was pushed, no credentials were added, and no public URL was verified.
README repository/deployment URL placeholders remain unfilled. The clean source
copy is not represented as a fresh clone of an already-published revision.

## October 28 production verification

The public application at <https://hangman-web-app-6fy1.onrender.com> was accessed
using direct HTTPS requests and actual Chrome automation. All 296 local tests
passed again, with 0 failures, errors, or skips. Live checks passed creation,
retrieval, guessing, errors, independence, answer-disclosure rules, and win/loss/
restart flows for all three difficulties. Public HTML/JS/CSS matched local files.
The configured Gunicorn startup and module-relative asset/word paths also passed
local checks. No application defect was confirmed or application code changed.

See [production_readiness.md](production_readiness.md) for the full observations,
scope of credential inspection, corrected documentation, and final checklist.
Hands-on manual procedures above remain unexecuted; automated Chrome sessions do
not complete them. Render dashboard logs/settings and the exact deployed commit
remain owner checks. The report, representative prompt selection, demonstration,
official-rubric check, and submission package are still pending in the repository.
