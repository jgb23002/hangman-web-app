# Browser implementation audit — October 26, 2026

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
