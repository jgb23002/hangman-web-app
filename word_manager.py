"""Load and select server-side Hangman vocabulary without Flask or UI code."""

from pathlib import Path
from random import choice


DIFFICULTIES = ("easy", "medium", "hard")


class WordListError(ValueError):
    """A required vocabulary file is unreadable, invalid, or empty."""


class WordManager:
    """Load all three lists once and keep their validated words in memory.

    Default and custom relative directories are resolved from this module,
    so changing the working directory does not change the vocabulary path.
    An absolute custom directory supports isolated tests or other word sets.
    """

    def __init__(self, words_dir: str | Path | None = None) -> None:
        directory = Path(words_dir) if words_dir is not None else Path("words")
        if not directory.is_absolute():
            directory = Path(__file__).resolve().parent / directory

        # Fail during initialization if any difficulty cannot supply a word.
        self._words_by_difficulty = {
            difficulty: self._load_words(directory / f"{difficulty}.txt")
            for difficulty in DIFFICULTIES
        }

    @staticmethod
    def _load_words(path: Path) -> tuple[str, ...]:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as error:
            raise WordListError(f"Cannot read word list '{path}'.") from error

        words = []
        seen = set()
        for line_number, line in enumerate(lines, start=1):
            word = line.strip()
            if not word:
                continue
            # Match the engine's ASCII alphabet before lowercasing Unicode.
            if not word.isascii() or not word.isalpha():
                raise WordListError(
                    f"Word list '{path}', line {line_number}: "
                    "expected a word containing only ASCII letters."
                )
            word = word.lower()
            if word not in seen:
                seen.add(word)
                words.append(word)

        if not words:
            raise WordListError(f"Word list '{path}' contains no usable words.")
        # Preserve file order while preventing callers from changing the cache.
        return tuple(words)

    def words_for(self, difficulty: str) -> tuple[str, ...]:
        """Return immutable server-side vocabulary for a valid difficulty."""
        if not isinstance(difficulty, str) or difficulty.lower() not in DIFFICULTIES:
            raise ValueError("Difficulty must be easy, medium, or hard.")
        return self._words_by_difficulty[difficulty.lower()]

    def random_word(self, difficulty: str) -> str:
        """Select an answer for the Python engine, never a browser response."""
        return choice(self.words_for(difficulty))
