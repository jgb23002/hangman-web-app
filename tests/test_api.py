"""HTTP contract tests using isolated Flask apps and server-side word fixtures."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from uuid import UUID

import pytest
from flask import Flask

import server
from game import HangmanGame
from server import create_app
from word_manager import WordManager


@pytest.fixture
def application(tmp_path):
    for difficulty, word in {
        "easy": "apple", "medium": "balloon", "hard": "adventure"
    }.items():
        (tmp_path / f"{difficulty}.txt").write_text(word + "\n", encoding="utf-8")
    return create_app({"TESTING": True}, word_manager=WordManager(tmp_path))


@pytest.fixture
def client(application):
    with application.test_client() as client:
        yield client


@pytest.fixture
def created_game(client):
    response = client.post("/api/games", json={"difficulty": "medium"})
    assert response.status_code == 201
    return response.get_json()


def assert_json_error(response, status):
    assert response.status_code == status
    assert response.mimetype == "application/json"
    data = response.get_json()
    assert set(data) == {"error"}
    assert isinstance(data["error"], str) and data["error"]
    assert "balloon" not in response.get_data(as_text=True)
    return data["error"]


@pytest.mark.parametrize(
    ("difficulty", "normalized", "length"),
    [("easy", "easy", 5), ("medium", "medium", 7), ("hard", "hard", 9),
     ("EASY", "easy", 5), ("Medium", "medium", 7)],
)
def test_create_returns_complete_safe_initial_state(
    client, application, difficulty, normalized, length
):
    response = client.post("/api/games", json={"difficulty": difficulty})
    assert response.status_code == 201
    assert response.mimetype == "application/json"
    state = response.get_json()
    game_id = state["game_id"]
    assert isinstance(game_id, str) and game_id
    assert state == {
        "game_id": game_id,
        "difficulty": normalized,
        "pattern": " ".join("_" for _ in range(length)),
        "remaining_guesses": 6,
        "guessed_letters": [],
        "incorrect_letters": [],
        "status": "playing",
    }
    assert isinstance(application.extensions["hangman_games"][game_id], HangmanGame)
    assert "word" not in state


def test_get_returns_current_state_without_modifying_it(client, created_game):
    url = f'/api/games/{created_game["game_id"]}'
    assert client.get(url).get_json() == created_game
    assert client.get(url).get_json() == created_game
    guessed = client.post(url + "/guess", json={"letter": "l"}).get_json()
    response = client.get(url)
    assert response.status_code == 200
    assert response.get_json() == guessed
    assert response.get_json()["pattern"] == "_ _ l l _ _ _"


def test_correct_and_incorrect_guesses_use_engine_rules(client, created_game):
    url = f'/api/games/{created_game["game_id"]}/guess'
    response = client.post(url, json={"letter": "L"})
    assert response.status_code == 200
    assert response.get_json() == {
        **created_game, "pattern": "_ _ l l _ _ _", "guessed_letters": ["l"]
    }
    response = client.post(url, json={"letter": "Z"})
    assert response.status_code == 200
    state = response.get_json()
    assert state["guessed_letters"] == ["l", "z"]
    assert state["incorrect_letters"] == ["z"]
    assert state["remaining_guesses"] == 5
    assert state["status"] == "playing"
    assert "word" not in state


@pytest.mark.parametrize(
    "difficulty", [None, True, 1, 1.5, [], {}, "", "expert", " easy", "easy ", "../easy"]
)
def test_invalid_difficulty_does_not_create_a_game(client, application, difficulty):
    response = client.post("/api/games", json={"difficulty": difficulty})
    assert_json_error(response, 400)
    assert application.extensions["hangman_games"] == {}


@pytest.mark.parametrize(
    "letter",
    [None, True, 1, 1.5, [], {}, "", " ", "\n", "aa", "balloon", "1", "!",
     " a", "a ", "é", "İ", "K"],
)
def test_invalid_letters_do_not_change_the_game(client, created_game, letter):
    url = f'/api/games/{created_game["game_id"]}'
    client.post(url + "/guess", json={"letter": "l"})
    before = client.get(url).get_json()
    response = client.post(url + "/guess", json={"letter": letter})
    assert_json_error(response, 400)
    assert client.get(url).get_json() == before


@pytest.mark.parametrize("letter", ["l", "L", "z", "Z"])
def test_duplicates_are_consistently_rejected(client, created_game, letter):
    url = f'/api/games/{created_game["game_id"]}'
    before = client.post(url + "/guess", json={"letter": letter.lower()}).get_json()
    response = client.post(url + "/guess", json={"letter": letter})
    assert "already been guessed" in assert_json_error(response, 400)
    assert client.get(url).get_json() == before


@pytest.mark.parametrize("endpoint", ["create", "guess"])
@pytest.mark.parametrize("body", [b"", b"{", b'{"letter":', b"\xff"])
def test_malformed_json_has_a_clear_error(client, created_game, endpoint, body):
    url = "/api/games" if endpoint == "create" else f'/api/games/{created_game["game_id"]}/guess'
    response = client.post(url, data=body, content_type="application/json")
    assert "Malformed JSON" in assert_json_error(response, 400)
    assert client.get(f'/api/games/{created_game["game_id"]}').get_json() == created_game


@pytest.mark.parametrize("endpoint", ["create", "guess"])
@pytest.mark.parametrize("body", ["null", "[]", '["a"]', '"medium"', "1", "true"])
def test_json_body_must_be_an_object(client, created_game, endpoint, body):
    url = "/api/games" if endpoint == "create" else f'/api/games/{created_game["game_id"]}/guess'
    response = client.post(url, data=body, content_type="application/json")
    assert "JSON object" in assert_json_error(response, 400)


@pytest.mark.parametrize("endpoint", ["create", "guess"])
def test_required_fields_must_be_present(client, created_game, endpoint):
    url = "/api/games" if endpoint == "create" else f'/api/games/{created_game["game_id"]}/guess'
    response = client.post(url, json={})
    expected = "difficulty" if endpoint == "create" else "letter"
    assert expected in assert_json_error(response, 400)


@pytest.mark.parametrize("endpoint", ["create", "guess"])
@pytest.mark.parametrize("extra", ["word", "status", "remaining_guesses", "balloon"])
def test_unexpected_fields_cannot_choose_answers_or_override_rules(
    client, application, created_game, endpoint, extra
):
    url = "/api/games" if endpoint == "create" else f'/api/games/{created_game["game_id"]}/guess'
    payload = {"difficulty": "medium"} if endpoint == "create" else {"letter": "l"}
    payload[extra] = "balloon"
    response = client.post(url, json=payload)
    assert "Unexpected request fields" in assert_json_error(response, 400)
    assert len(application.extensions["hangman_games"]) == 1
    assert client.get(f'/api/games/{created_game["game_id"]}').get_json() == created_game


@pytest.mark.parametrize("endpoint", ["create", "guess"])
@pytest.mark.parametrize("content_type", [None, "text/plain", "application/x-www-form-urlencoded"])
def test_unsupported_content_types_return_415(client, created_game, endpoint, content_type):
    url = "/api/games" if endpoint == "create" else f'/api/games/{created_game["game_id"]}/guess'
    response = client.post(url, data='{"letter":"l"}', content_type=content_type)
    assert "JSON content type" in assert_json_error(response, 415)


def test_json_compatible_media_types_are_accepted(client):
    response = client.post(
        "/api/games", data='{"difficulty":"easy"}',
        content_type="application/vnd.hangman+json",
    )
    assert response.status_code == 201


@pytest.mark.parametrize("method", ["get", "post"])
def test_unknown_games_return_404(client, method):
    url = "/api/games/balloon"
    response = client.get(url) if method == "get" else client.post(url + "/guess", json={"letter": "a"})
    assert "Game not found" in assert_json_error(response, 404)


def test_unknown_game_is_404_even_with_an_invalid_guess_body(client):
    assert_json_error(client.post("/api/games/missing/guess", data="{"), 404)


@pytest.mark.parametrize("outcome", ["won", "lost"])
def test_full_games_reveal_answers_only_after_completion(client, created_game, outcome):
    url = f'/api/games/{created_game["game_id"]}'
    letters = "balon" if outcome == "won" else "cdefgh"
    for index, letter in enumerate(letters):
        response = client.post(url + "/guess", json={"letter": letter})
        assert response.status_code == 200
        state = response.get_json()
        assert client.get(url).get_json() == state
        if index < len(letters) - 1:
            assert state["status"] == "playing"
            assert "word" not in state
            assert "balloon" not in response.get_data(as_text=True)
        else:
            assert state["status"] == outcome
            assert state["word"] == "balloon"
            assert state["remaining_guesses"] == (6 if outcome == "won" else 0)

    before = client.get(url).get_json()
    assert "game has ended" in assert_json_error(
        client.post(url + "/guess", json={"letter": "x"}), 400
    )
    assert client.get(url).get_json() == before


def test_ids_are_unique_and_games_are_independent(client):
    states = [client.post("/api/games", json={"difficulty": "medium"}).get_json() for _ in range(20)]
    assert len({state["game_id"] for state in states}) == len(states)
    first_url = f'/api/games/{states[0]["game_id"]}'
    client.post(first_url + "/guess", json={"letter": "l"})
    client.post(first_url + "/guess", json={"letter": "z"})
    for state in states[1:]:
        assert client.get(f'/api/games/{state["game_id"]}').get_json() == state


def test_id_collision_does_not_replace_an_existing_game(client, monkeypatch):
    ids = iter([UUID(int=1), UUID(int=1), UUID(int=2)])
    monkeypatch.setattr(server, "uuid4", lambda: next(ids))
    first = client.post("/api/games", json={"difficulty": "easy"}).get_json()
    second = client.post("/api/games", json={"difficulty": "hard"}).get_json()
    assert first["game_id"] != second["game_id"]
    assert client.get(f'/api/games/{first["game_id"]}').get_json() == first


def test_factories_have_independent_storage(application, client, created_game):
    other = create_app(
        {"TESTING": True}, word_manager=application.extensions["hangman_word_manager"]
    )
    with other.test_client() as other_client:
        assert_json_error(other_client.get(f'/api/games/{created_game["game_id"]}'), 404)
        second = other_client.post("/api/games", json={"difficulty": "easy"}).get_json()
    assert_json_error(client.get(f'/api/games/{second["game_id"]}'), 404)
    assert client.get(f'/api/games/{created_game["game_id"]}').get_json() == created_game


@pytest.mark.parametrize("endpoint", ["create", "get", "guess"])
def test_unsupported_methods_return_json_and_retain_allow_header(client, created_game, endpoint):
    url = {
        "create": "/api/games",
        "get": f'/api/games/{created_game["game_id"]}',
        "guess": f'/api/games/{created_game["game_id"]}/guess',
    }[endpoint]
    response = client.delete(url)
    assert_json_error(response, 405)
    assert ("GET" if endpoint == "get" else "POST") in response.headers["Allow"]


def test_unknown_api_routes_return_json(client):
    assert_json_error(client.get("/api/not-a-route"), 404)


def test_unexpected_server_errors_do_not_disclose_answers(application, client, monkeypatch):
    def fail_selection(difficulty):
        raise RuntimeError("balloon should never appear in a response")

    application.config["PROPAGATE_EXCEPTIONS"] = False
    monkeypatch.setattr(application.extensions["hangman_word_manager"], "random_word", fail_selection)
    response = client.post("/api/games", json={"difficulty": "medium"})
    assert assert_json_error(response, 500) == "Internal server error."


def test_api_success_and_error_responses_are_not_cached(client, created_game):
    for response in [
        client.get(f'/api/games/{created_game["game_id"]}'),
        client.get("/api/games/missing"),
    ]:
        assert response.cache_control.no_store


@pytest.mark.parametrize("path", ["/", "/static/app.js", "/static/style.css"])
def test_serves_existing_static_files_without_building_a_frontend(client, path):
    filename = {"/": "index.html", "/static/app.js": "app.js", "/static/style.css": "style.css"}[path]
    expected = (Path(__file__).resolve().parents[1] / "static" / filename).read_bytes()
    with client.get(path) as response:
        assert response.status_code == 200
        assert response.get_data() == expected


@pytest.mark.parametrize(
    "path", ["/words/medium.txt", "/static/words/medium.txt", "/static/../words/medium.txt", "/static/../server.py"]
)
def test_vocabulary_and_python_source_are_not_static_assets(client, path):
    with client.get(path) as response:
        assert response.status_code == 404
        assert "balloon" not in response.get_data(as_text=True)


def test_module_exports_a_production_importable_app():
    assert isinstance(server.app, Flask)
    assert server.app.debug is False


def test_concurrent_duplicate_guesses_consume_only_one_attempt(
    application, client, created_game
):
    # Each worker uses its own in-process Flask client, never a live server.
    barrier = Barrier(4, timeout=5)
    url = f'/api/games/{created_game["game_id"]}'

    def submit(_):
        with application.test_client() as worker_client:
            barrier.wait()
            response = worker_client.post(url + "/guess", json={"letter": "z"})
            return response.status_code, response.get_json()

    with ThreadPoolExecutor(max_workers=4) as executor:
        responses = list(executor.map(submit, range(4)))
    assert sorted(status for status, _ in responses) == [200, 400, 400, 400]
    state = client.get(url).get_json()
    assert state["remaining_guesses"] == 5
    assert state["guessed_letters"] == ["z"]
    assert state["incorrect_letters"] == ["z"]
    assert "word" not in state


def test_last_life_and_partial_pattern_survive_invalid_requests(client, created_game):
    url = f'/api/games/{created_game["game_id"]}'
    for letter in "lcdefg":
        assert client.post(url + "/guess", json={"letter": letter}).status_code == 200
    before = client.get(url).get_json()
    assert before["remaining_guesses"] == 1
    assert before["pattern"] == "_ _ l l _ _ _"
    for letter in ("L", "12", "!"):
        assert_json_error(client.post(url + "/guess", json={"letter": letter}), 400)
        assert client.get(url).get_json() == before
    response = client.post(url + "/guess", json={"letter": "h"})
    assert response.status_code == 200
    state = response.get_json()
    assert state["status"] == "lost"
    assert state["pattern"] == before["pattern"]
    assert state["remaining_guesses"] == 0
    assert state["word"] == "balloon"
    assert_json_error(client.post(url + "/guess", json={"letter": "a"}), 400)
    assert client.get(url).get_json() == state


def test_completed_games_remain_independent_when_a_new_game_starts(client):
    winner = client.post("/api/games", json={"difficulty": "medium"}).get_json()
    loser = client.post("/api/games", json={"difficulty": "easy"}).get_json()
    for letter in "balon":
        won = client.post(f'/api/games/{winner["game_id"]}/guess', json={"letter": letter}).get_json()
    for letter in "bcdfgh":
        lost = client.post(f'/api/games/{loser["game_id"]}/guess', json={"letter": letter}).get_json()
    fresh = client.post("/api/games", json={"difficulty": "hard"}).get_json()
    assert len({won["game_id"], lost["game_id"], fresh["game_id"]}) == 3
    assert won["status"] == "won" and won["word"] == "balloon"
    assert lost["status"] == "lost" and lost["word"] == "apple"
    assert fresh["status"] == "playing" and "word" not in fresh
    for state in (won, lost, fresh):
        assert client.get(f'/api/games/{state["game_id"]}').get_json() == state
