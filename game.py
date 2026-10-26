"""Hangman rules and public game state, independent of any web framework."""


MAX_INCORRECT_GUESSES = 6


class HangmanGame:
    """Play one game with a supplied word and difficulty.

    Difficulty is metadata: every difficulty allows exactly six misses.
    Invalid construction arguments or rejected guesses raise ValueError.
    Word selection and HTTP handling belong to later project phases.
    """

    def __init__(self, word: str, difficulty: str) -> None:
        # Validate before lowercasing so Unicode letters cannot normalize
        # into the ASCII alphabet used by the browser's A-Z keyboard.
        if not isinstance(word, str) or not word.isascii() or not word.isalpha():
            raise ValueError("Word must be nonempty and contain only ASCII letters.")
        if not isinstance(difficulty, str) or difficulty.lower() not in (
            "easy", "medium", "hard"
        ):
            raise ValueError("Difficulty must be easy, medium, or hard.")

        self.__word = word.lower()
        self._difficulty = difficulty.lower()
        self._guessed_letters: list[str] = []
        self._incorrect_letters: list[str] = []

    @property
    def difficulty(self) -> str:
        """Return the normalized difficulty without selecting a word."""
        return self._difficulty

    @property
    def remaining_guesses(self) -> int:
        """Return the number of incorrect guesses still allowed."""
        return MAX_INCORRECT_GUESSES - len(self._incorrect_letters)

    @property
    def pattern(self) -> str:
        """Reveal every occurrence of guessed letters in the spaced mask."""
        return " ".join(
            letter if letter in self._guessed_letters else "_"
            for letter in self.__word
        )

    @property
    def status(self) -> str:
        """Derive the outcome from the guesses instead of duplicating state."""
        if self.remaining_guesses == 0:
            return "lost"
        if all(letter in self._guessed_letters for letter in self.__word):
            return "won"
        return "playing"

    def guess(self, letter: str) -> dict[str, object]:
        """Accept one new ASCII letter and return the updated public state.

        Validate everything before mutation: invalid, duplicate, and
        post-game guesses never consume an attempt or change history.
        Error messages deliberately omit the supplied value and answer.
        """
        if self.status != "playing":
            raise ValueError("Cannot guess after the game has ended.")
        if (
            not isinstance(letter, str)
            or len(letter) != 1
            or not letter.isascii()
            or not letter.isalpha()
        ):
            raise ValueError("Guess must be a single ASCII letter.")

        letter = letter.lower()
        if letter in self._guessed_letters:
            raise ValueError("Letter has already been guessed.")

        self._guessed_letters.append(letter)
        if letter not in self.__word:
            self._incorrect_letters.append(letter)
        return self.to_state()

    def to_state(self) -> dict[str, object]:
        """Return a JSON-serializable snapshot using the REST state fields."""
        status = self.status
        state: dict[str, object] = {
            "pattern": self.pattern,
            # Copies keep callers from changing the engine through a snapshot.
            "guessed_letters": self._guessed_letters.copy(),
            "incorrect_letters": self._incorrect_letters.copy(),
            "remaining_guesses": self.remaining_guesses,
            "status": status,
        }
        # The answer key is absent during play, rather than present as null.
        if status != "playing":
            state["word"] = self.__word
        return state
