"""Word loading, validation, selection, and the engine's answer boundary."""

import json
import os
from pathlib import Path

import pytest

import word_manager
from game import HangmanGame
from word_manager import WordListError, WordManager


@pytest.fixture
def word_directory(tmp_path):
    directory = tmp_path / "vocabulary"
    directory.mkdir()
    for difficulty, content in {
        "easy": "cat\ndog\n",
        "medium": "rabbit\npuzzle\n",
        "hard": "adventure\nwatermelon\n",
    }.items():
        (directory / f"{difficulty}.txt").write_text(content, encoding="utf-8")
    return directory


@pytest.fixture
def manager(word_directory):
    return WordManager(word_directory)


@pytest.mark.parametrize(
    ("difficulty", "expected"),
    [
        ("easy", ("cat", "dog")),
        ("medium", ("rabbit", "puzzle")),
        ("hard", ("adventure", "watermelon")),
    ],
)
def test_loads_each_difficulty(manager, difficulty, expected):
    assert manager.words_for(difficulty) == expected


def test_normalizes_words_skips_blanks_and_removes_duplicates(word_directory):
    path = word_directory / "easy.txt"
    original = "  Cat  \n\nDOG\ncat\n\t\n dog \nBird\nCAT\n"
    path.write_text(original, encoding="utf-8")

    manager = WordManager(word_directory)
    assert manager.words_for("easy") == ("cat", "dog", "bird")
    # Normalization is in memory; supplied vocabulary files stay untouched.
    assert path.read_text(encoding="utf-8") == original


@pytest.mark.parametrize("difficulty", ["EASY", "Medium", "Hard"])
def test_normalizes_difficulty_case(manager, difficulty):
    assert manager.words_for(difficulty) == manager.words_for(difficulty.lower())


@pytest.mark.parametrize("method", ["words_for", "random_word"])
@pytest.mark.parametrize(
    "difficulty",
    [None, True, 0, 1.5, [], {}, b"easy", "", "expert", " easy", "easy ", "../easy"],
)
def test_rejects_invalid_difficulties(manager, method, difficulty):
    with pytest.raises(ValueError, match="Difficulty must be easy, medium, or hard"):
        getattr(manager, method)(difficulty)


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_random_selection_stays_within_requested_difficulty(manager, difficulty):
    expected = manager.words_for(difficulty)
    assert all(manager.random_word(difficulty) in expected for _ in range(20))


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
@pytest.mark.parametrize("index", [0, -1])
def test_random_selection_uses_the_whole_requested_list(
    manager, monkeypatch, difficulty, index
):
    expected = manager.words_for(difficulty)

    def controlled_choice(candidates):
        assert candidates == expected
        return candidates[index]

    monkeypatch.setattr(word_manager, "choice", controlled_choice)
    assert manager.random_word(difficulty) == expected[index]


def test_single_word_lists_allow_repeated_random_choices(word_directory):
    (word_directory / "easy.txt").write_text("cat\nCAT\n", encoding="utf-8")
    manager = WordManager(word_directory)
    assert manager.words_for("easy") == ("cat",)
    assert [manager.random_word("easy") for _ in range(3)] == ["cat"] * 3


def test_default_paths_work_from_another_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    manager = WordManager()
    for difficulty in ("easy", "medium", "hard"):
        assert len(manager.words_for(difficulty)) >= 100


def test_custom_relative_directory_is_relative_to_module(
    word_directory, tmp_path, monkeypatch
):
    project_directory = Path(word_manager.__file__).resolve().parent
    relative_directory = os.path.relpath(word_directory, project_directory)
    monkeypatch.chdir(tmp_path)
    manager = WordManager(relative_directory)
    assert manager.words_for("easy") == ("cat", "dog")


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_missing_word_files_have_clear_errors(word_directory, difficulty):
    (word_directory / f"{difficulty}.txt").unlink()
    with pytest.raises(WordListError, match=f"Cannot read word list .*{difficulty}.txt"):
        WordManager(word_directory)


def test_missing_directory_has_a_clear_error(tmp_path):
    with pytest.raises(WordListError, match="Cannot read word list .*easy.txt"):
        WordManager(tmp_path / "missing")


@pytest.mark.parametrize("content", ["", "\n \n\t\n"])
def test_rejects_empty_or_blank_only_lists(word_directory, content):
    (word_directory / "easy.txt").write_text(content, encoding="utf-8")
    with pytest.raises(WordListError, match="easy.txt.*contains no usable words"):
        WordManager(word_directory)


@pytest.mark.parametrize(
    "invalid_word", ["cat1", "two words", "co-op", "can't", "éclair", "K", "word!", "a\x00b"]
)
def test_rejects_invalid_entries_with_filename_and_line_number(
    word_directory, invalid_word
):
    (word_directory / "medium.txt").write_text(
        f"rabbit\n\n{invalid_word}\n", encoding="utf-8"
    )
    with pytest.raises(WordListError, match="medium.txt.*line 3.*ASCII letters") as error:
        WordManager(word_directory)
    assert invalid_word not in str(error.value)


def test_rejects_invalid_utf8_with_a_clear_file_error(word_directory):
    (word_directory / "medium.txt").write_bytes(b"\xff")
    with pytest.raises(WordListError, match="Cannot read word list .*medium.txt"):
        WordManager(word_directory)


def test_directory_in_place_of_a_file_has_a_clear_error(word_directory):
    path = word_directory / "hard.txt"
    path.unlink()
    path.mkdir()
    with pytest.raises(WordListError, match="Cannot read word list .*hard.txt"):
        WordManager(word_directory)


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_project_lists_have_at_least_one_hundred_unique_valid_words(difficulty):
    path = Path(__file__).resolve().parents[1] / "words" / f"{difficulty}.txt"
    words = path.read_text(encoding="utf-8").splitlines()
    assert len(words) >= 100
    assert len(words) == len(set(words))
    assert all(word.isascii() and word.isalpha() and word == word.lower() for word in words)
    assert WordManager().words_for(difficulty) == tuple(words)


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_selected_answers_stay_out_of_active_game_state(manager, monkeypatch, difficulty):
    monkeypatch.setattr(word_manager, "choice", lambda words: words[0])
    selected_word = manager.random_word(difficulty)
    game = HangmanGame(selected_word, difficulty)

    for state in (game.to_state(), game.guess(selected_word[0])):
        assert state["status"] == "playing"
        assert "word" not in state
        assert selected_word not in json.dumps(state)


@pytest.mark.parametrize(
    "separator", ["\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"],
    ids=["vertical-tab", "form-feed", "file-separator", "group-separator", "record-separator", "next-line", "unicode-line", "unicode-paragraph"],
)
def test_embedded_non_file_line_separators_are_invalid_entries(word_directory, separator):
    (word_directory / "medium.txt").write_text(
        f"rabbit\nrab{separator}bit\n", encoding="utf-8"
    )
    with pytest.raises(WordListError, match="medium.txt.*line 2.*ASCII letters"):
        WordManager(word_directory)


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"], ids=["lf", "crlf", "cr"])
def test_normal_text_file_newlines_are_supported_without_rewriting(word_directory, newline):
    path = word_directory / "easy.txt"
    original = f"Cat{newline}DOG{newline}cat{newline}".encode("ascii")
    path.write_bytes(original)
    assert WordManager(word_directory).words_for("easy") == ("cat", "dog")
    assert path.read_bytes() == original
