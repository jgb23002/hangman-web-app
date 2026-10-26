"""Flask REST API for the independently tested Hangman components.

Local development: python server.py
Production: gunicorn --workers 1 --bind 0.0.0.0:$PORT server:app
Games live in one process's memory and disappear when it restarts.
"""

import os
from pathlib import Path
from threading import Lock
from uuid import uuid4

from flask import Flask, abort, jsonify, request
from werkzeug.exceptions import BadRequest, HTTPException

from game import HangmanGame
from word_manager import DIFFICULTIES, WordManager


def create_app(
    config: dict[str, object] | None = None,
    *,
    word_manager: WordManager | None = None,
) -> Flask:
    """Create an app with its own game dictionary and optional test vocabulary."""
    application = Flask(
        __name__,
        static_folder=Path(__file__).resolve().parent / "static",
        static_url_path="/static",
    )
    application.config["DEBUG"] = False
    if config is not None:
        application.config.update(config)

    manager = word_manager if word_manager is not None else WordManager()
    games: dict[str, HangmanGame] = {}
    state_lock = Lock()
    # Extensions expose state to server-side fixtures, never to HTTP clients.
    application.extensions["hangman_games"] = games
    application.extensions["hangman_word_manager"] = manager

    def is_api_request() -> bool:
        return request.path == "/api" or request.path.startswith("/api/")

    @application.errorhandler(HTTPException)
    def handle_http_error(error):
        response = error.get_response()
        if is_api_request():
            message = "Internal server error." if error.code == 500 else error.description
            response.set_data(application.json.dumps({"error": message}))
            response.content_type = "application/json"
        # Retain protocol headers such as Allow on a 405 response.
        return response

    @application.after_request
    def prevent_stale_game_responses(response):
        if is_api_request():
            response.cache_control.no_store = True
        return response

    def required_json_field(field: str):
        if not request.is_json:
            abort(415, description="Request body must use a JSON content type.")
        try:
            payload = request.get_json()
        except BadRequest:
            # Do not reflect parser details or request values into errors.
            abort(400, description="Malformed JSON request body.")
        if not isinstance(payload, dict):
            abort(400, description="Request body must be a JSON object.")
        if field not in payload:
            abort(400, description=f"Missing required field: {field}.")
        if set(payload) != {field}:
            abort(400, description="Unexpected request fields.")
        return payload[field]

    def require_game(game_id: str) -> HangmanGame:
        # Call while holding state_lock so lookups and snapshots are consistent.
        game = games.get(game_id)
        if game is None:
            abort(404, description="Game not found.")
        return game

    def public_state(game_id: str, game: HangmanGame) -> dict[str, object]:
        # Only the engine decides whether the finished game's answer is public.
        return {
            "game_id": game_id,
            "difficulty": game.difficulty,
            **game.to_state(),
        }

    @application.get("/")
    def index():
        return application.send_static_file("index.html")

    @application.post("/api/games")
    def create_game():
        difficulty = required_json_field("difficulty")
        if not isinstance(difficulty, str) or difficulty.lower() not in DIFFICULTIES:
            abort(400, description="Difficulty must be easy, medium, or hard.")
        difficulty = difficulty.lower()
        game = HangmanGame(manager.random_word(difficulty), difficulty)

        with state_lock:
            game_id = uuid4().hex
            while game_id in games:
                game_id = uuid4().hex
            games[game_id] = game
            state = public_state(game_id, game)
        return jsonify(state), 201

    @application.get("/api/games/<game_id>")
    def get_game(game_id: str):
        with state_lock:
            state = public_state(game_id, require_game(game_id))
        return jsonify(state)

    @application.post("/api/games/<game_id>/guess")
    def guess_letter(game_id: str):
        with state_lock:
            game = require_game(game_id)
        letter = required_json_field("letter")

        # A threaded server must not interleave validation and game mutations.
        with state_lock:
            try:
                game.guess(letter)
            except ValueError as error:
                abort(400, description=str(error))
            state = public_state(game_id, game)
        return jsonify(state)

    return application


# Gunicorn imports this object; importing never starts a development server.
app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
