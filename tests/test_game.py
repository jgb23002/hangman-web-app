"""Deterministic engine tests; no Flask app, browser, or word files needed."""

import json

import pytest

from game import HangmanGame


@pytest.fixture
def game():
    return HangmanGame("balloon", "medium")


def test_initial_state_matches_public_contract(game):
    assert game.to_state() == {
        "pattern": "_ _ _ _ _ _ _",
        "guessed_letters": [],
        "incorrect_letters": [],
        "remaining_guesses": 6,
        "status": "playing",
    }
    assert game.pattern == "_ _ _ _ _ _ _"
    assert game.remaining_guesses == 6
    assert game.status == "playing"


@pytest.mark.parametrize(
    ("difficulty", "normalized"),
    [("easy", "easy"), ("Medium", "medium"), ("HARD", "hard")],
)
def test_difficulty_is_normalized_metadata_with_six_attempts(difficulty, normalized):
    game = HangmanGame("cat", difficulty)
    assert game.difficulty == normalized
    assert game.remaining_guesses == 6


@pytest.mark.parametrize(
    "word",
    [None, 42, True, [], {}, b"cat", "", " ", "two words", "can't",
     "co-op", "cat1", "café", "K", "cat\n"],
)
def test_invalid_words_are_rejected(word):
    with pytest.raises(ValueError, match="Word must"):
        HangmanGame(word, "easy")


@pytest.mark.parametrize(
    "difficulty", [None, 3, True, [], {}, "", "expert", " easy", "easy "]
)
def test_invalid_difficulties_are_rejected(difficulty):
    with pytest.raises(ValueError, match="Difficulty must"):
        HangmanGame("cat", difficulty)


def test_uppercase_word_and_guesses_are_normalized():
    game = HangmanGame("BaLlOoN", "medium")
    state = game.guess("L")
    assert state["pattern"] == "_ _ l l _ _ _"
    assert state["guessed_letters"] == ["l"]
    assert "word" not in state

    for letter in "BAON":
        state = game.guess(letter)
    assert state["status"] == "won"
    assert state["word"] == "balloon"
    assert state["pattern"] == "b a l l o o n"


def test_correct_guess_reveals_all_positions_without_costing_an_attempt(game):
    state = game.guess("l")
    assert state["pattern"] == "_ _ l l _ _ _"
    assert state["guessed_letters"] == ["l"]
    assert state["incorrect_letters"] == []
    assert state["remaining_guesses"] == 6
    assert state["status"] == "playing"


def test_incorrect_guesses_each_cost_one_attempt(game):
    for misses, letter in enumerate("xz", start=1):
        state = game.guess(letter)
        assert state["remaining_guesses"] == 6 - misses
        assert state["pattern"] == "_ _ _ _ _ _ _"
    assert state["guessed_letters"] == ["x", "z"]
    assert state["incorrect_letters"] == ["x", "z"]


def test_mixed_guesses_preserve_first_guess_order(game):
    for letter in ["l", "Z", "b", "X", "o"]:
        state = game.guess(letter)
    assert state["guessed_letters"] == ["l", "z", "b", "x", "o"]
    assert state["incorrect_letters"] == ["z", "x"]
    assert state["pattern"] == "b _ l l o o _"
    assert state["remaining_guesses"] == 4


@pytest.mark.parametrize(
    "letter",
    [None, True, 7, 1.5, [], {}, b"a", "", " ", "\t", "\n", "aa", "a1",
     "1", "!", "a ", " a", "é", "ß", "İ", "K", "😀"],
)
def test_invalid_guesses_leave_existing_state_unchanged(game, letter):
    game.guess("l")
    game.guess("z")
    before = game.to_state()
    with pytest.raises(ValueError, match="single ASCII letter") as error:
        game.guess(letter)
    assert game.to_state() == before
    assert "balloon" not in str(error.value)


@pytest.mark.parametrize("letter", ["l", "L", "z", "Z"])
def test_duplicate_guesses_are_rejected_without_state_changes(game, letter):
    game.guess(letter.lower())
    before = game.to_state()
    with pytest.raises(ValueError, match="already been guessed"):
        game.guess(letter)
    assert game.to_state() == before


def test_complete_win_reveals_answer_only_on_final_guess(game):
    for letter in "balo":
        state = game.guess(letter)
        assert state["status"] == "playing"
        assert "word" not in state
        assert "balloon" not in json.dumps(state)

    state = game.guess("n")
    assert state["status"] == "won"
    assert state["word"] == "balloon"
    assert state["pattern"] == "b a l l o o n"
    assert state["remaining_guesses"] == 6
    assert state["guessed_letters"] == ["b", "a", "l", "o", "n"]
    assert game.status == "won"
    assert game.to_state() == state


def test_a_game_can_still_be_won_after_five_incorrect_guesses(game):
    for letter in "cdefg":
        game.guess(letter)
    assert game.status == "playing"
    assert game.remaining_guesses == 1

    for letter in "balon":
        state = game.guess(letter)
    assert state["status"] == "won"
    assert state["remaining_guesses"] == 1
    assert state["word"] == "balloon"


def test_loss_occurs_on_exactly_the_sixth_incorrect_guess(game):
    for misses, letter in enumerate("cdefg", start=1):
        state = game.guess(letter)
        assert state["status"] == "playing"
        assert state["remaining_guesses"] == 6 - misses
        assert "word" not in state
        assert "balloon" not in json.dumps(state)

    state = game.guess("h")
    assert state["status"] == "lost"
    assert state["remaining_guesses"] == 0
    assert state["word"] == "balloon"
    assert state["pattern"] == "_ _ _ _ _ _ _"
    assert state["incorrect_letters"] == list("cdefgh")
    assert game.status == "lost"
    assert game.to_state() == state


@pytest.mark.parametrize("outcome", ["won", "lost"])
@pytest.mark.parametrize("letter", ["x", "a", None])
def test_finished_games_reject_further_guesses_without_changes(game, outcome, letter):
    for prior_letter in "balon" if outcome == "won" else "cdefgh":
        game.guess(prior_letter)
    before = game.to_state()
    with pytest.raises(ValueError, match="game has ended"):
        game.guess(letter)
    assert game.to_state() == before
    assert game.remaining_guesses >= 0


def test_games_keep_independent_state(game):
    other = HangmanGame("balloon", "medium")
    original = other.to_state()
    game.guess("l")
    game.guess("x")
    assert other.to_state() == original

    game_state = game.to_state()
    other.guess("o")
    assert game.to_state() == game_state
    assert other.to_state()["guessed_letters"] == ["o"]


@pytest.mark.parametrize("snapshot_source", ["guess", "to_state"])
def test_public_snapshots_cannot_mutate_the_game(game, snapshot_source):
    state = game.guess("z")
    if snapshot_source == "to_state":
        state = game.to_state()
    before = game.to_state()

    state["guessed_letters"].append("l")
    state["incorrect_letters"].clear()
    state["pattern"] = "changed"
    state["remaining_guesses"] = 99
    state["status"] = "won"
    state["word"] = "changed"
    assert game.to_state() == before


def test_old_snapshots_do_not_change_when_new_guesses_arrive(game):
    initial = game.to_state()
    game.guess("l")
    game.guess("z")
    assert initial["guessed_letters"] == []
    assert initial["incorrect_letters"] == []
    assert initial["remaining_guesses"] == 6
    assert initial["status"] == "playing"


@pytest.mark.parametrize("outcome", ["playing", "won", "lost"])
def test_public_state_is_json_serializable_for_every_status(game, outcome):
    letters = {"playing": "lz", "won": "balon", "lost": "cdefgh"}[outcome]
    for letter in letters:
        game.guess(letter)
    state = game.to_state()
    assert state["status"] == outcome
    assert json.loads(json.dumps(state)) == state
    assert ("word" in state) == (outcome != "playing")


@pytest.mark.parametrize("word", ["a", "aaaa"])
def test_one_unique_letter_can_complete_a_word(word):
    game = HangmanGame(word, "easy")
    assert game.pattern == " ".join("_" for _ in word)
    state = game.guess("A")
    assert state["status"] == "won"
    assert state["word"] == word
    assert state["remaining_guesses"] == 6
    assert state["guessed_letters"] == ["a"]
