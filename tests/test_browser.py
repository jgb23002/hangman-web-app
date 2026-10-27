"""Phase 4 browser interactions against a real Flask server and fixed test words.

Install a browser: python -m playwright install chromium
Run: python -m pytest tests/test_browser.py
Existing Chrome: add --browser-channel=chrome to the pytest command.
"""

from threading import Thread
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import expect
from werkzeug.serving import make_server

from server import create_app
from word_manager import WordManager


pytestmark = pytest.mark.browser


@pytest.fixture(autouse=True)
def no_uncaught_browser_runtime_errors(page, context):
    errors = []

    def watch(tab):
        tab.on("pageerror", lambda error: errors.append(str(error)))

    watch(page)
    context.on("page", watch)
    yield
    context.remove_listener("page", watch)
    assert errors == [], f"Uncaught browser JavaScript errors: {errors}"


@pytest.fixture
def restartable_server(tmp_path):
    for difficulty, word in {
        "easy": "apple", "medium": "balloon", "hard": "refrigerator"
    }.items():
        (tmp_path / f"{difficulty}.txt").write_text(word + "\n", encoding="utf-8")
    manager = WordManager(tmp_path)

    def start(port):
        application = create_app({"TESTING": True}, word_manager=manager)
        listener = make_server("127.0.0.1", port, application, threaded=True)
        thread = Thread(target=listener.serve_forever, daemon=True)
        thread.start()
        return listener, thread

    listener, thread = start(0)
    port = listener.server_port

    def restart():
        nonlocal listener, thread
        listener.shutdown()
        listener.server_close()
        thread.join(timeout=5)
        listener, thread = start(port)

    try:
        yield f"http://127.0.0.1:{port}", restart
    finally:
        listener.shutdown()
        listener.server_close()
        thread.join(timeout=5)


@pytest.fixture(scope="module")
def live_url(tmp_path_factory):
    directory = tmp_path_factory.mktemp("browser-vocabulary")
    for difficulty, word in {
        "easy": "apple", "medium": "balloon", "hard": "refrigerator"
    }.items():
        (directory / f"{difficulty}.txt").write_text(word + "\n", encoding="utf-8")
    application = create_app({"TESTING": True}, word_manager=WordManager(directory))
    http_server = make_server("127.0.0.1", 0, application, threaded=True)
    thread = Thread(target=http_server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{http_server.server_port}"
    finally:
        http_server.shutdown()
        http_server.server_close()
        thread.join(timeout=5)


def choose_difficulty(page, difficulty):
    page.locator(".difficulty-options label").filter(has_text=difficulty.capitalize()).click()


def start_game(page, live_url, difficulty="easy"):
    page.goto(live_url)
    choose_difficulty(page, difficulty)
    return new_game(page)


def new_game(page):
    with page.expect_response(lambda response: response.url.endswith("/api/games") and response.request.method == "POST") as result:
        page.get_by_role("button", name="New Game", exact=True).click()
    state = result.value.json()
    expect(page.locator("#round-badge")).to_contain_text(state["difficulty"].upper())
    expect(page.get_by_role("button", name="Guess A", exact=True)).to_be_enabled()
    expect(page.locator(".letter-key:enabled")).to_have_count(26)
    expect(page.locator("#revealed-answer")).to_have_text("")
    return state


def guess(page, letter, method="keyboard"):
    with page.expect_response(lambda response: response.url.endswith("/guess")) as result:
        if method == "mouse":
            page.get_by_role("button", name=f"Guess {letter.upper()}", exact=True).click()
        else:
            page.keyboard.press(letter)
    expect(page.locator(f'[data-letter="{letter.lower()}"]')).to_have_class("letter-key is-used" if letter.lower() in result.value.json()["pattern"] else "letter-key is-used is-miss")
    return result.value.json()


def hold_guess_response(page):
    page.add_init_script("""
      const originalFetch = window.fetch.bind(window);
      window.fetch = async (url, options) => {
        if (String(url).endsWith('/guess')) {
          const response = await originalFetch(url, { ...options, signal: undefined });
          await new Promise((resolve) => { window.releaseOldGuess = resolve; });
          return response;
        }
        return originalFetch(url, options);
      };
    """)


def test_initial_screen_has_semantic_controls_and_inactive_keyboard(page, live_url):
    page.goto(live_url)
    expect(page.get_by_role("heading", name="Hangman.", exact=True)).to_be_visible()
    expect(page.get_by_role("radio")).to_have_count(3)
    expect(page.locator(".letter-key")).to_have_count(26)
    expect(page.locator(".letter-key:disabled")).to_have_count(26)
    expect(page.locator("#remaining")).to_have_text("—")
    expect(page.locator("#answer")).to_be_hidden()


def test_game_can_be_started_and_played_using_only_the_keyboard(page, live_url):
    page.goto(live_url)
    page.keyboard.press("Tab")
    expect(page.get_by_role("link", name="Skip to the game")).to_be_focused()
    expect(page.get_by_role("link", name="Skip to the game")).to_have_css("opacity", "1")
    page.keyboard.press("Enter")
    expect(page.locator("main")).to_be_focused()
    page.keyboard.press("Tab")
    expect(page.get_by_role("radio", name="Easy", exact=True)).to_be_focused()
    page.keyboard.press("ArrowRight")
    expect(page.get_by_role("radio", name="Medium", exact=True)).to_be_checked()
    page.keyboard.press("Tab")
    expect(page.get_by_role("button", name="New Game", exact=True)).to_be_focused()
    with page.expect_response(lambda response: response.url.endswith("/api/games")):
        page.keyboard.press("Enter")
    expect(page.locator(".letter-slot")).to_have_count(7)
    expect(page.get_by_role("button", name="Guess L", exact=True)).to_be_enabled()
    guess(page, "l")
    expect(page.locator("#previous-guesses")).to_have_text("l")


@pytest.mark.parametrize(("difficulty", "length"), [("easy", 5), ("medium", 7), ("hard", 12)])
def test_selects_difficulty_and_displays_server_state(page, live_url, difficulty, length):
    state = start_game(page, live_url, difficulty)
    assert "word" not in state
    expect(page.locator(".letter-slot")).to_have_count(length)
    assert page.locator(".letter-slot").all_text_contents() == ["_"] * length
    expect(page.locator("#remaining")).to_have_text("6")
    expect(page.locator(".letter-key:enabled")).to_have_count(26)


def test_click_and_physical_keyboard_update_history_drawing_and_disabled_keys(page, live_url):
    start_game(page, live_url)
    guess(page, "p", method="mouse")
    assert page.locator(".letter-slot").all_text_contents() == ["_", "p", "p", "_", "_"]
    guess(page, "A")
    guess(page, "z", method="mouse")
    expect(page.locator("#remaining")).to_have_text("5")
    expect(page.locator(".hangman-part.is-visible")).to_have_count(1)
    expect(page.locator("#previous-guesses")).to_have_text("p · a · z")
    expect(page.locator("#incorrect-guesses")).to_have_text("z")
    expect(page.locator('[data-letter="p"]')).to_be_disabled()
    expect(page.locator('[data-letter="z"]')).to_be_disabled()


def test_refresh_retrieves_current_game_without_starting_another(page, live_url):
    state = start_game(page, live_url)
    game_url = f'{live_url}/api/games/{state["game_id"]}'
    assert page.request.post(game_url + "/guess", data={"letter": "z"}).ok
    expect(page.locator("#remaining")).to_have_text("6")
    with page.expect_response(lambda response: response.url == game_url and response.request.method == "GET"):
        page.get_by_role("button", name="Refresh current game").click()
    expect(page.locator("#remaining")).to_have_text("5")
    expect(page.locator(".hangman-part.is-visible")).to_have_count(1)
    expect(page.locator("#incorrect-guesses")).to_have_text("z")


@pytest.mark.parametrize(("outcome", "letters"), [("won", "aple"), ("lost", "bcdfgh")])
def test_finishes_and_restarts_without_reloading(page, live_url, outcome, letters):
    first = start_game(page, live_url)
    for letter in letters:
        state = guess(page, letter, method="mouse" if letter == letters[-1] else "keyboard")
        expect(page.locator("#remaining")).to_have_text(str(state["remaining_guesses"]))
        visible_parts = page.locator(".hangman-part.is-visible").evaluate_all(
            "parts => parts.map(part => Number(part.dataset.part))"
        )
        assert visible_parts == list(range(len(state["incorrect_letters"])))
    assert state["status"] == outcome
    expect(page.locator("#status-box")).to_have_attribute("data-tone", outcome)
    expect(page.locator("#answer")).to_be_visible()
    expect(page.locator("#revealed-answer")).to_have_text("apple")
    expect(page.locator(".letter-key:disabled")).to_have_count(26)
    expect(page.get_by_role("button", name="New Game", exact=True)).to_be_focused()
    expect(page.locator(".hangman-part.is-visible")).to_have_count(6 if outcome == "lost" else 0)
    completed_requests = []
    page.on("request", lambda request: completed_requests.append(request) if request.url.endswith("/guess") else None)
    page.keyboard.press("z")
    page.locator('[data-letter="z"]').dispatch_event("click")
    assert completed_requests == []
    second = new_game(page)
    assert first["game_id"] != second["game_id"]
    assert page.locator(".letter-slot").all_text_contents() == ["_"] * 5
    expect(page.locator("#previous-guesses")).to_have_text("None yet")
    expect(page.locator("#incorrect-guesses")).to_have_text("None yet")
    expect(page.locator(".hangman-part.is-visible")).to_have_count(0)
    expect(page.locator("#remaining")).to_have_text("6")
    expect(page.locator("#answer")).to_be_hidden()


def test_keyboard_ignores_modifiers_duplicates_and_difficulty_input(page, live_url):
    start_game(page, live_url)
    guesses = []
    page.on("request", lambda request: guesses.append(request) if request.url.endswith("/guess") else None)
    page.keyboard.press("Control+z")
    page.keyboard.press("Meta+a")
    page.get_by_role("radio", name="Easy", exact=True).focus()
    page.keyboard.press("b")
    page.locator("#new-game").focus()
    guess(page, "a")
    page.keyboard.press("a")
    assert len(guesses) == 1
    expect(page.locator("#previous-guesses")).to_have_text("a")


def test_network_error_when_starting_can_be_retried(page, live_url):
    page.goto(live_url)
    page.route("**/api/games", lambda route: route.abort("internetdisconnected"), times=1)
    page.get_by_role("button", name="New Game", exact=True).click()
    expect(page.locator("#status-box")).to_have_attribute("data-tone", "error")
    expect(page.locator("#status-title")).to_contain_text("Could not reach")
    expect(page.get_by_role("button", name="New Game", exact=True)).to_be_enabled()
    new_game(page)


def test_failed_guess_is_reconciled_by_get_before_guessing_continues(page, live_url):
    start_game(page, live_url)

    def drop_response(route):
        route.fetch()  # Let Flask accept the guess, then lose its response.
        route.abort("failed")

    page.route("**/api/games/*/guess", drop_response, times=1)
    page.get_by_role("button", name="Guess Z", exact=True).click()
    expect(page.locator("#status-box")).to_have_attribute("data-tone", "error")
    expect(page.locator("#remaining")).to_have_text("6")
    expect(page.locator(".letter-key:disabled")).to_have_count(26)
    expect(page.get_by_role("button", name="Refresh current game")).to_be_focused()
    page.get_by_role("button", name="Refresh current game").click()
    expect(page.locator("#remaining")).to_have_text("5")
    expect(page.locator("#incorrect-guesses")).to_have_text("z")
    expect(page.get_by_role("button", name="Guess A", exact=True)).to_be_enabled()
    expect(page.get_by_role("button", name="Guess Z", exact=True)).to_be_disabled()


def test_pending_guesses_and_old_responses_cannot_corrupt_a_new_game(page, live_url):
    # Delay a real response and ignore abort signals to exercise the identity
    # guard independently of the browser's best-effort network cancellation.
    hold_guess_response(page)
    start_game(page, live_url, "medium")
    guesses = []
    page.on("request", lambda request: guesses.append(request) if request.url.endswith("/guess") else None)
    page.get_by_role("button", name="Guess L", exact=True).click()
    page.wait_for_function("typeof window.releaseOldGuess === 'function'")
    expect(page.locator(".letter-key:disabled")).to_have_count(26)
    page.keyboard.press("z")
    page.locator('[data-letter="z"]').dispatch_event("click")
    assert len(guesses) == 1
    choose_difficulty(page, "hard")
    new_game(page)
    page.evaluate("window.releaseOldGuess()")
    page.evaluate("() => new Promise(requestAnimationFrame)")
    expect(page.locator(".letter-slot")).to_have_count(12)
    assert page.locator(".letter-slot").all_text_contents() == ["_"] * 12
    expect(page.locator("#previous-guesses")).to_have_text("None yet")
    expect(page.locator("#remaining")).to_have_text("6")
    expect(page.locator("#status-box")).to_have_attribute("data-tone", "playing")


@pytest.mark.parametrize(("width", "height"), [(1280, 1000), (1024, 768), (768, 1024), (390, 844), (320, 740)])
def test_responsive_layout_and_clean_browser_console(page, live_url, width, height):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
    page.set_viewport_size({"width": width, "height": height})
    start_game(page, live_url, "hard")
    expect(page.locator(".letter-slot")).to_have_count(12)
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    assert page.locator(".drawing-panel, .play-panel, .round-header, .word-display, .alphabet").evaluate_all(
        "elements => elements.every(element => element.scrollWidth <= element.clientWidth + 1)"
    )
    guess(page, "z", method="mouse")
    expect(page.locator("#remaining")).to_have_text("5")
    assert errors == []


def test_keyboard_focus_survives_start_and_letter_submissions(page, live_url):
    start_game(page, live_url)
    expect(page.get_by_role("button", name="New Game", exact=True)).to_be_focused()
    page.get_by_role("button", name="Guess P", exact=True).focus()
    with page.expect_response(lambda response: response.url.endswith("/guess")):
        page.keyboard.press("Enter")
    expect(page.get_by_role("button", name="Guess Q", exact=True)).to_be_focused()
    expect(page.locator("#previous-guesses")).to_have_text("p")


@pytest.mark.parametrize(
    "invalid_fields",
    [
        {"remaining_guesses": -1},
        {"remaining_guesses": 7},
        {"guessed_letters": ["aa"]},
        {"incorrect_letters": [7]},
        {"difficulty": "expert"},
        {"pattern": ""},
        {"status": "lost"},
        {"status": "won", "word": ""},
    ],
    ids=["negative-counter", "excess-counter", "invalid-letter", "nonletter-history", "unknown-difficulty", "empty-pattern", "missing-answer", "empty-answer"],
)
def test_invalid_state_responses_preserve_the_last_confirmed_game(
    page, live_url, invalid_fields
):
    state = start_game(page, live_url)
    page.route(
        f'**/api/games/{state["game_id"]}',
        lambda route: route.fulfill(json={**state, **invalid_fields}),
        times=1,
    )
    page.get_by_role("button", name="Refresh current game").click()
    expect(page.locator("#status-box")).to_have_attribute("data-tone", "error")
    expect(page.locator("#remaining")).to_have_text("6")
    assert page.locator(".letter-slot").all_text_contents() == ["_"] * 5
    expect(page.locator("#answer")).to_be_hidden()
    expect(page.locator(".letter-key:disabled")).to_have_count(26)
    page.get_by_role("button", name="Refresh current game").click()
    expect(page.get_by_role("button", name="Guess A", exact=True)).to_be_enabled()


def test_failed_new_game_404_preserves_the_current_round(page, live_url):
    state = start_game(page, live_url, "medium")
    guess(page, "l")
    page.route(
        "**/api/games", lambda route: route.fulfill(status=404, json={"error": "Service temporarily unavailable."}),
        times=1,
    )
    page.get_by_role("button", name="New Game", exact=True).click()
    expect(page.locator("#status-box")).to_have_attribute("data-tone", "error")
    expect(page.locator(".letter-slot")).to_have_count(7)
    expect(page.locator("#previous-guesses")).to_have_text("l")
    with page.expect_response(lambda response: response.url.endswith(state["game_id"])):
        page.get_by_role("button", name="Refresh current game").click()
    expect(page.get_by_role("button", name="Guess A", exact=True)).to_be_enabled()


def test_request_timeout_can_be_reconciled_without_losing_the_game(page, live_url):
    page.clock.install()
    start_game(page, live_url)
    held_requests = []
    page.route("**/api/games/*/guess", lambda route: held_requests.append(route))
    page.get_by_role("button", name="Guess Z", exact=True).click()
    expect(page.locator("#status-title")).to_have_text("Trying Z…")
    page.clock.fast_forward(20001)
    expect(page.locator("#status-title")).to_contain_text("took too long")
    expect(page.locator(".letter-key:disabled")).to_have_count(26)
    expect(page.locator("#remaining")).to_have_text("6")
    page.get_by_role("button", name="Refresh current game").click()
    expect(page.get_by_role("button", name="Guess Z", exact=True)).to_be_enabled()


def test_live_status_includes_the_current_pattern_and_remaining_guesses(page, live_url):
    start_game(page, live_url)
    guess(page, "p")
    expect(page.locator("#game-progress")).to_contain_text("blank, P, P, blank, blank")
    expect(page.locator("#game-progress")).to_contain_text("6 incorrect guesses remaining")
    accessible_status = page.get_by_role("status").aria_snapshot()
    assert "blank, P, P, blank, blank" in accessible_status
    assert "6 incorrect guesses remaining" in accessible_status
    assert page.locator("#status-box").evaluate(
        "element => !element.closest('[aria-busy=\"true\"]')"
    )


def test_active_game_answers_are_absent_from_dom_and_static_assets(page, live_url):
    state = start_game(page, live_url, "medium")
    guess(page, "l")
    assert "word" not in page.request.get(f'{live_url}/api/games/{state["game_id"]}').json()
    assert "balloon" not in page.content().lower()
    for path in ("/", "/static/app.js", "/static/style.css"):
        assert "balloon" not in page.request.get(live_url + path).text().lower()
    expect(page.locator("#revealed-answer")).to_have_text("")


def test_request_completion_preserves_deliberate_focus_changes(page, live_url):
    hold_guess_response(page)
    start_game(page, live_url)
    page.get_by_role("button", name="Guess P", exact=True).click()
    page.wait_for_function("typeof window.releaseOldGuess === 'function'")
    difficulty = page.get_by_role("radio", name="Hard", exact=True)
    difficulty.focus()
    page.evaluate("window.releaseOldGuess()")
    expect(page.locator('[data-letter="p"]')).to_have_class("letter-key is-used")
    expect(difficulty).to_be_focused()


def test_missing_game_get_resets_the_board_and_offers_a_new_game(page, live_url):
    state = start_game(page, live_url)
    page.route(
        f'**/api/games/{state["game_id"]}',
        lambda route: route.fulfill(status=404, json={"error": "Game not found."}),
        times=1,
    )
    page.get_by_role("button", name="Refresh current game").click()
    expect(page.locator("#status-title")).to_contain_text("no longer available")
    expect(page.locator("#remaining")).to_have_text("—")
    expect(page.locator(".letter-slot")).to_have_count(0)
    expect(page.locator(".letter-key:disabled")).to_have_count(26)
    expect(page.get_by_role("button", name="New Game", exact=True)).to_be_enabled()
    new_game(page)


@pytest.mark.parametrize(
    ("status", "content_type", "body"),
    [
        (500, "application/json", '{"error":"Internal server error."}'),
        (502, "text/html", "<h1>Private diagnostics: apple</h1>"),
        (200, "application/json", "not-json"),
    ],
    ids=["server-error", "html-error", "invalid-json"],
)
def test_error_responses_keep_progress_and_do_not_render_raw_bodies(
    page, live_url, status, content_type, body
):
    start_game(page, live_url)
    page.route(
        "**/api/games/*/guess",
        lambda route: route.fulfill(status=status, content_type=content_type, body=body),
        times=1,
    )
    page.get_by_role("button", name="Guess Z", exact=True).click()
    expect(page.locator("#status-box")).to_have_attribute("data-tone", "error")
    expect(page.locator("#remaining")).to_have_text("6")
    expect(page.locator(".letter-key:disabled")).to_have_count(26)
    assert "Private diagnostics" not in page.content()
    expect(page.locator("#revealed-answer")).to_have_text("")
    page.get_by_role("button", name="Refresh current game").click()
    expect(page.get_by_role("button", name="Guess Z", exact=True)).to_be_enabled()


def test_frontend_uses_the_three_required_endpoints_with_expected_json(page, live_url):
    calls = []

    def record(request):
        if request.url.startswith(live_url + "/api/"):
            calls.append((
                request.method,
                urlsplit(request.url).path,
                request.post_data_json if request.method == "POST" else None,
            ))

    page.on("request", record)
    state = start_game(page, live_url, "medium")
    guess(page, "l")
    url = f'/api/games/{state["game_id"]}'
    with page.expect_response(lambda response: response.url == live_url + url):
        page.get_by_role("button", name="Refresh current game").click()
    expect(page.get_by_role("button", name="Guess A", exact=True)).to_be_enabled()
    assert calls == [
        ("POST", "/api/games", {"difficulty": "medium"}),
        ("POST", url + "/guess", {"letter": "l"}),
        ("GET", url, None),
    ]


def test_frontend_renders_supplied_state_without_predicting_letter_correctness(page, live_url):
    initial = start_game(page, live_url, "medium")
    # This is a contract-valid API fixture for a different server-selected word.
    # The browser must follow it rather than predict the Python fixture's answer.
    supplied = {
        **initial,
        "pattern": "z _ _ _ _ _ _",
        "guessed_letters": ["z"],
        "incorrect_letters": [],
        "remaining_guesses": 6,
    }
    page.route(
        "**/api/games/*/guess", lambda route: route.fulfill(json=supplied), times=1
    )
    page.get_by_role("button", name="Guess Z", exact=True).click()
    expect(page.locator('[data-letter="z"]')).to_have_class("letter-key is-used")
    assert page.locator(".letter-slot").all_text_contents() == ["z"] + ["_"] * 6
    expect(page.locator("#remaining")).to_have_text("6")
    expect(page.locator("#incorrect-guesses")).to_have_text("None yet")
    expect(page.locator(".hangman-part.is-visible")).to_have_count(0)
    expect(page.locator("#answer")).to_be_hidden()


def test_two_browser_games_remain_independent_through_completion_and_restart(
    page, context, live_url
):
    first = start_game(page, live_url, "easy")
    other = context.new_page()
    try:
        second = start_game(other, live_url, "medium")
        second_progress = guess(other, "l", method="mouse")
        for letter in "aple":
            state = guess(page, letter, method="mouse")
        assert state["status"] == "won"
        fresh = new_game(page)
        assert len({first["game_id"], second["game_id"], fresh["game_id"]}) == 3

        with other.expect_response(lambda response: response.url.endswith(second["game_id"])) as refreshed:
            other.get_by_role("button", name="Refresh current game").click()
        assert refreshed.value.json() == second_progress
        expect(other.locator("#previous-guesses")).to_have_text("l")
        for letter in "cdefgh":
            state = guess(other, letter, method="mouse")
        assert state["status"] == "lost"

        with page.expect_response(lambda response: response.url.endswith(fresh["game_id"])) as unchanged:
            page.get_by_role("button", name="Refresh current game").click()
        assert unchanged.value.json() == fresh
        expect(page.locator("#previous-guesses")).to_have_text("None yet")
        expect(page.locator("#remaining")).to_have_text("6")
        expect(page.locator("#answer")).to_be_hidden()
    finally:
        other.close()


def test_browser_recovers_after_the_http_application_restarts(page, restartable_server):
    url, restart = restartable_server
    previous = start_game(page, url)
    guess(page, "p")
    restart()
    page.get_by_role("button", name="Refresh current game").click()
    expect(page.locator("#status-title")).to_contain_text("no longer available")
    expect(page.locator("#remaining")).to_have_text("—")
    expect(page.locator(".letter-key:disabled")).to_have_count(26)
    fresh = new_game(page)
    assert previous["game_id"] != fresh["game_id"]
