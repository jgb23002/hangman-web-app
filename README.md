# Hangman — CSE 4095

An individual **CSE 4095 Agentic Programming** assignment: build and deploy a
web-based Hangman game. This independent implementation combines a Python game
engine, Flask REST API, and responsive vanilla HTML/CSS/JavaScript client.
The server owns the answer, guesses, and outcome; the browser renders its state.

| Project links | Status |
| --- | --- |
| GitHub repository | **TODO: replace with the actual repository URL** |
| Public Render application | **TODO: replace with the verified HTTPS URL after deployment** |

Deployment configuration is prepared; no public deployment is claimed here.

## Features and stack

- Easy, Medium, and Hard vocabulary; six incorrect guesses per game.
- Clickable A–Z keys, physical-keyboard input, SVG drawing, guess history,
  remaining counter, win/loss messages, and New Game without reloading.
- Refresh and network-error recovery, serialized guesses, and protection against
  delayed responses from an earlier game.
- Input validation, independent game IDs, and automated engine/API/browser tests.

**Stack:** Python, Flask, Werkzeug, Gunicorn, HTML, CSS, JavaScript, SVG, pytest,
and Playwright. Git/GitHub manage source; Render is the intended host.
The frontend has no framework, build step, or separate frontend server.
Terminal clients, bots, evaluations, scoring, leaderboards, and replay are outside
this assignment's scope.

## Architecture and files

```text
Browser (HTML/CSS/JS) -- relative fetch() /api/... --> Flask server.py
                                                     |-- game.py: rules/state
                                                     `-- word_manager.py: vocabulary
```

`HangmanGame` is independent of Flask and JavaScript. `WordManager` validates and
selects vocabulary. `create_app()` gives each Flask app its own in-memory game
dictionary; module-level `app` is the Gunicorn entry point. A lock protects
updates and snapshots within that process.

```text
hangman-web-app/
├── game.py                   # HangmanGame and safe state serialization
├── word_manager.py           # Loading, validation, and random selection
├── server.py                 # Flask app factory, routes, and game storage
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── words/
│   ├── easy.txt
│   ├── medium.txt
│   ├── hard.txt
│   └── README.md              # Vocabulary provenance and criteria
├── tests/
│   ├── conftest.py            # Ordinary-test network isolation
│   ├── test_game.py
│   ├── test_words.py
│   ├── test_api.py
│   └── test_browser.py
├── docs/
│   ├── testing.md            # Results, requirement mapping, manual checklist
│   ├── evidence/             # Recorded test output
│   └── cursor_transcript.md  # Instructor's historical reference transcript
├── SPECIFICATION.md          # Larger original specification
├── TODO.md                   # Reduced assignment roadmap and verified progress
├── requirements.txt          # Pinned direct runtime/test dependencies
├── pytest.ini
├── .python-version           # Tested Python runtime
├── .gitignore
└── render.yaml               # Prepared Render web-service configuration
```

## Local setup

Prerequisites: **Python 3.13.1** (the tested version), Git, and a modern browser.
Full browser tests additionally need Google Chrome or Playwright's Chromium.
Run these commands from a clone or copy of this project:

```sh
cd hangman-web-app
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python server.py
```

On Windows, create the environment with `py -3.13 -m venv .venv` and activate
with `.venv\Scripts\Activate.ps1` in PowerShell instead.
Gunicorn production verification uses a Unix-like environment; Render supplies
the Linux production runtime.

Open **http://127.0.0.1:5000**. Select a difficulty, click **New Game**, then click
letters or type A–Z. Correct guesses reveal every matching position; invalid or
duplicate guesses consume no attempt. Six incorrect guesses end the game.
**Refresh** retrieves the current game, including after an interrupted guess.
Use Ctrl+C to stop the local server. If port 5000 is occupied, run
`PORT=5001 python server.py` on macOS/Linux and open port 5001 instead.

## Word lists

| Difficulty | Current words | Generation criteria |
| --- | ---: | --- |
| Easy | 169 | Familiar words, 3–5 letters |
| Medium | 156 | Common words, 6–8 letters |
| Hard | 181 | Longer common words, 9–12 letters |

These were newly generated with AI assistance for this implementation, not copied
from the instructor's lists. See [words/README.md](words/README.md).
Each file contains one lowercase ASCII alphabetic word per line. Loading trims
whitespace, skips blank lines, normalizes case, and removes duplicates without
rewriting files. Missing, empty, unreadable, or invalid files raise clear errors.
The length ranges describe these lists; the loader does not impose them on
replacement vocabulary. Lists are loaded once per `WordManager` instance.

Both vocabulary and static-file paths resolve relative to the Python modules,
so they do not depend on the shell's working directory. Keep `words/` and
`static/` in the repository when deploying.

## REST API

POST requests require a JSON object and `Content-Type: application/json`.
Difficulty values are case-insensitive; letters are normalized to lowercase.
Only the documented request field is accepted. Examples below use an
**illustrative** seven-letter game and placeholder `GAME_ID`; use the real ID
returned by creation. Random words and IDs vary.

### Create a game — `POST /api/games`

Request:

```json
{"difficulty": "medium"}
```

Response: **201 Created**.

```json
{
  "game_id": "GAME_ID",
  "difficulty": "medium",
  "pattern": "_ _ _ _ _ _ _",
  "guessed_letters": [],
  "incorrect_letters": [],
  "remaining_guesses": 6,
  "status": "playing"
}
```

### Retrieve a game — `GET /api/games/{game_id}`

No request body. Returns **200 OK** with the current state, using the same fields
as the guess response below. Retrieval does not create or modify a game.
Unknown IDs return **404**.

```sh
curl http://127.0.0.1:5000/api/games/GAME_ID
```

### Guess a letter — `POST /api/games/{game_id}/guess`

Request:

```json
{"letter": "L"}
```

Response: **200 OK**. A GET after this guess returns the same state.

```json
{
  "game_id": "GAME_ID",
  "difficulty": "medium",
  "pattern": "_ _ l l _ _ _",
  "guessed_letters": ["l"],
  "incorrect_letters": [],
  "remaining_guesses": 6,
  "status": "playing"
}
```

Status is `playing`, `won`, or `lost`. After either outcome, GET/guess state
includes `word`. For example, after subsequently guessing B, A, O, and N:

```json
{
  "game_id": "GAME_ID",
  "difficulty": "medium",
  "pattern": "b a l l o o n",
  "guessed_letters": ["l", "b", "a", "o", "n"],
  "incorrect_letters": [],
  "remaining_guesses": 6,
  "status": "won",
  "word": "balloon"
}
```

Further guesses after completion are rejected without changing state.

| HTTP status | Meaning |
| --- | --- |
| 400 | Malformed/non-object JSON, missing/unexpected fields, invalid difficulty or letter, duplicate or post-game guess |
| 404 | Unknown game or API route |
| 405 | Unsupported method; the `Allow` header is retained |
| 415 | POST body lacks a supported JSON content type |
| 500 | Unexpected failure; response contains a generic error |

API errors use JSON such as `{"error": "Letter has already been guessed."}`.
Guess input must be one ASCII letter; empty, numeric, symbolic, and multi-letter
values are rejected. Unknown IDs are checked before guess-body validation.

## Browser communication and answer privacy

`app.js` uses relative URLs with `fetch()` for all three endpoints. It renders
the returned pattern, histories, remaining count, and status. It does not select
words, compare guesses to an answer, or determine win/loss. During requests it
blocks overlapping guesses; New Game cancels old requests and ignores stale
responses. After an uncertain request, Refresh confirms the server's state.

**The hidden word is omitted entirely from active-game responses.** The answer
is returned only after a win or loss. Vocabulary is outside the public `static/`
directory. Responses use `HangmanGame.to_state()`; API errors do not echo private
answers or production tracebacks. API responses are marked `Cache-Control:
no-store`.

## Automated and manual testing

With the virtual environment activated:

```sh
# Ordinary tests: no browser or listening HTTP server required
python -m pytest -m "not browser"

# Install Chromium once, then run every test
python -m playwright install chromium
python -m pytest
```

Alternatively, use installed Google Chrome: `python -m pytest
--browser-channel=chrome`. Tests marked `browser` start and stop temporary local
Flask servers; ordinary tests block socket connections/listeners and use Flask's
test client and temporary word files. They do not depend on a deployed service.

The recorded Phase 5 run passed **296 cases** (256 ordinary and 40 browser), with
zero failures, errors, or skips. See [docs/testing.md](docs/testing.md) for actual
results, the 38-case requirements mapping, and the detailed pending manual
checklist. Hands-on device, screen-reader, and Developer Tools checks remain
open; automated browser testing does not certify them.

## Prepared Render deployment

The repository includes [render.yaml](render.yaml) for a **Python web service**,
not a static site. It specifies the free plan, one instance, `/` as the health
check, and these commands:

```sh
# Build
python -m pip install -r requirements.txt

# Production startup; Render supplies PORT
gunicorn --workers 1 --threads 1 --bind 0.0.0.0:$PORT server:app
```

`.python-version` selects Python 3.13.1. Leave Root Directory at the repository
root and avoid a conflicting `PYTHON_VERSION` setting. Debug is disabled by the
application. No database, secret key, or credential is required by this app.
Browser binaries are needed for local browser tests, not to serve the website.

**Future deployment steps — not performed in this phase:**

1. Commit and push the reviewed source, word lists, static files, and configuration
   to your own GitHub repository; replace the repository placeholder above.
2. When ready to deploy, create a Render Blueprint from that repository and
   review `render.yaml`. Applying/creating the service starts an initial deploy.
   Alternatively, create a Python Web Service with the same build/start commands,
   free plan, one instance, and health path `/`.
3. The Blueprint sets `autoDeployTrigger: "off"`. For dashboard-created services,
   also disable automatic deploys if you want the same behavior. Later updates
   can be published intentionally with **Manual Deploy**.
4. Inspect Render's build/runtime logs, then verify the assigned HTTPS URL,
   static assets, all three endpoints, complete games, and restart behavior.
   Add the verified public URL above and record the deployed commit.

For a local production-server check, run
`gunicorn --workers 1 --threads 1 --bind 127.0.0.1:8000 server:app` and open
http://127.0.0.1:8000. This does not publish to Render.

Configuration follows Render's [Flask deployment guide](https://render.com/docs/deploy-flask),
[Blueprint reference](https://render.com/docs/blueprint-spec),
[Python version settings](https://render.com/docs/python-version), and
[port-binding requirements](https://render.com/docs/web-services#port-binding).
The prepared configuration still requires an actual Render build and deployment
to verify the hosted environment.

## Known limitations

- Games live in one process's memory. Restarts/redeploys discard them, and stored
  games are retained until the process exits. Use **one worker and one service
  instance**; a lock does not share state between separate processes.
- Reloading the browser page does not automatically restore the previous ID.
- Vocabulary changes require a new `WordManager`/server restart.
- Automated browser coverage uses Chrome/Chromium; real-device, other-browser,
  screen-reader, and manual DevTools checks remain pending.
- No accounts, database persistence, or additional competition features are
  implemented. Public-host availability and performance await deployment checks.

## AI-assisted development

AI assistance supported scoped planning, implementation drafts, tests, debugging,
and documentation. Work proceeded phase by phase: inspect the real files and
specification, make a bounded change, run relevant checks, investigate failures,
and record only verified progress. A failing regression exposed the word-loader
separator bug before its implementation was corrected. Results and pending work
are documented in `TODO.md` and `docs/testing.md`.

The instructor's specification/transcript are reference material, not an
implementation to copy or evidence of this student's completed work. The
student remains responsible for reviewing AI output, understanding the code,
and selecting genuine project prompts and verified results for the final report.
