# Production readiness review — October 28, 2026

The implemented application passed local and live functionality checks. No
application code defect was confirmed. Submission is still incomplete because
the report, representative prompt selection, and demonstration are absent from
the repository. They may exist elsewhere; their completion was not assumed.

- Application: [public Render game](https://hangman-web-app-6fy1.onrender.com).
- Source: [GitHub repository](https://github.com/jgb23002/hangman-web-app).
- Application revision reviewed: `e70800b71046a349f0cc35107ce8b735774b6774`.
  GitHub `main` matched local HEAD before these documentation edits. All required
  application source, three word files, tests, requirements, and configuration
  were tracked. This review's documentation changes still need committing/pushing.
- Scope: the reduced CSE 4095 server/browser assignment. Terminal clients, bots,
  evaluations, scoring, leaderboards, and replay are excluded.

## Results

| Requirement | Result | Evidence |
| --- | --- | --- |
| Independent engine, six misses, validation, duplicate rejection, outcomes | Pass | `game.py`; 78 engine tests |
| Three validated difficulty lists and server-side random selection | Pass | `word_manager.py`; 76 tests; 169/156/181 words |
| Three required REST routes and JSON contract | Pass | `server.py`; 102 API tests; direct live requests |
| Unique IDs and independent server-side game states | Pass | API isolation/collision/concurrency tests; independent live games |
| Answer omitted while playing and disclosed after completion | Pass | Engine/API/browser tests; live active states and completed games |
| Browser controls, both input methods, history, counter, drawing, restart | Pass | 40 local Chrome tests; live win and loss at every difficulty |
| Relative fetch URLs and server-authoritative rules | Pass | Reviewed `static/app.js`; endpoint/supplied-state tests |
| Keyboard navigation and accessible state rendering | Pass for automated checks | Local keyboard/focus/live-region tests; live skip-link/radio navigation |
| Responsive layout | Pass for tested viewports | Local five-viewport suite; live 1280/768/390/320 px checks |
| Production startup, debug setting, asset/word paths | Pass locally | Exact configured Gunicorn command; app loaded from unrelated working directory |
| Render YAML | Pass | Validated against [Render's current JSON Schema](https://render.com/schema/render.yaml.json) |
| Pinned dependency compatibility | Pass | `pip check`; installed versions match requirements; full suite passed |
| Secrets and ignored artifacts | No findings in performed scan | 42 reachable-history blobs; no credential-pattern matches or sensitive paths |
| Render deployed commit, actual worker/runtime settings and logs | Not verified | Owner dashboard access was unavailable; static-file identity is not commit proof |
| Report, representative prompts, demonstration and submission package | Missing from repository | Planned Phase 7 deliverables were not found |

## Automated and live checks actually executed

The complete local suite passed **296 cases: 78 engine, 76 word-management,
102 API, and 40 browser tests; 0 failures, 0 errors, 0 skips**. Parametrized cases
count individually. Repeat runs and external smoke checks do not inflate this
unique-case count. Python was 3.13.1; Chrome was 156.0.8078.48.

```sh
python -m pytest --browser-channel=chrome
python -m pip check
node --check static/app.js
git diff --check
```

The execution used `-B`, disabled pytest's cache provider, and placed JUnit/browser
artifacts outside the repository. Ordinary tests use Flask's in-process client;
only browser integration starts temporary local HTTP servers. An earlier
read-only audit on the same date also cloned the published application revision
into a temporary directory, installed requirements into a fresh environment, and
passed all 296 cases. That clone predates this documentation update.
Its documented `python server.py` startup also served the page and a safe API
response during this review using the separate dependency environment.

The generic web-opening tool could not open the live URL, but direct HTTPS
requests and actual Chrome automation could. Live HTML, JavaScript, and CSS
matched the local files byte for byte. The successful direct HTTP review made
63 sequential requests covering creation/retrieval/guessing at all difficulties,
uppercase normalization, invalid/duplicate requests without mutation, 400/404/
405/415 JSON errors, independent games, six-miss losses, post-game rejection,
and answer disclosure. Completed answers belonged to the corresponding project
lists. Vocabulary, Python source, `.env`, and `.git/config` URL probes returned
404. HTTP header names were compared case-insensitively, including the proxy's
lowercase `allow` header.

Live Chrome exercised a win and a loss at **each** difficulty, mixed clickable
letters and uppercase physical-keyboard input, suppressed repeated guesses,
retrieved state with Refresh, checked each SVG stage and remaining counter,
disabled completed keyboards, and restarted without reloading. The main browser
flow made 53 API calls and reported no uncaught JavaScript or Console errors.
Separate fresh sessions verified stable desktop/mobile rendering, no horizontal
overflow, an empty drawing, and a fully reset keyboard. Stable 1280px and 320px
screenshots were visually inspected. These were automated browser sessions,
not hands-on device or screen-reader testing.

Only new test games were used. Existing players' games were not changed. No
deployment, service restart, commit, push, or dashboard setting change was made.
Temporary local Gunicorn/browser processes were closed. No live 500 error was
deliberately induced; generic unexpected-error handling passed the local API
test. The public service was not load-tested or monitored for long-term uptime.

## Corrections and limits

The confirmed documentation issues were fixed locally: README URL placeholders,
pre-deployment wording, missing clone command, and the wrapped inline Chrome
test command. README now links the actual application and this review. No game,
API, frontend, dependency, or configuration code change was needed.

The credential inspection covered reachable Git history with patterns for private
keys, common service tokens, credentialed URLs, and likely credential assignments,
plus sensitive filenames. No findings were detected. Pattern inspection cannot
prove the absence of every possible secret format. Local environment/cache/key
exclusions were reviewed; no credentials were added.

The configuration uses one worker and one instance because storage is
process-local. Games disappear on restart/redeploy and accumulate until process
exit. Production restarts were not forced. Verify the actual Render dashboard
settings and deployed SHA before submission; matching public assets and working
endpoints alone do not establish the backend commit or runtime settings.

## Final readiness checklist

- [x] Implement and test all required engine, word, API, and browser features.
- [x] Pass the complete local automated suite, including real Chrome.
- [x] Verify HTTPS, live assets, API validation, answer privacy, and game isolation.
- [x] Win, lose, and restart live games at Easy, Medium, and Hard.
- [x] Verify the configured Gunicorn entry point, module-relative paths, and Render schema.
- [x] Review published application files, dependency pins, ignore rules, and reachable history for credentials.
- [x] Replace README repository/deployment placeholders locally and record verified results.
- [ ] Commit and push these documentation updates; review the published README and links.
- [ ] Confirm Render's deployed commit, connected branch, Python/startup settings, one worker/instance, and build/runtime logs in the dashboard.
- [ ] Record hands-on desktop/mobile, Safari/Firefox, zoom, screen-reader, and Chrome DevTools checks using the [manual procedures](testing.md#detailed-pending-manual-checklist).
- [ ] Prepare the 1–2 page development report with 2–3 representative prompts from this student's development; no curated report/prompt selection is present.
- [ ] Record and verify the 2–3 minute demonstration, then add its file or accessible link to the submission materials.
- [ ] Check the official assignment rubric and prepare the HuskyCT package, including accurate repository/app/report/video links or files.

`docs/assignment_instructions.md` and the official rubric are absent, so exact
submission formats and any requirements beyond the supplied assignment list
remain unverified. A separate submission-mapping document is also not present;
this checklist records readiness, not a prepared HuskyCT upload.
