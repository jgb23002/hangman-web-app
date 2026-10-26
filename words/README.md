# Hangman vocabulary

These lists were newly generated with AI assistance for this student's original
CSE 4095 implementation on October 26, 2026. They use common English vocabulary;
they are **not the instructor's original lists** and were not copied from the
instructor's implementation or transcript. All three project files were empty
before Phase 2, so there was no supplied vocabulary to preserve.

| File | Words | Difficulty criteria |
| --- | ---: | --- |
| `easy.txt` | 169 | Familiar everyday words, 3–5 letters |
| `medium.txt` | 156 | Common words, 6–8 letters |
| `hard.txt` | 181 | Longer common words, 9–12 letters |

Length and familiarity provide simple categories; letter distribution also
affects how hard a particular word is to guess. Each file contains one lowercase
ASCII alphabetic word per line, sorted alphabetically, with no duplicates.
The loader does not enforce these generated-list length ranges, so valid
instructor-provided vocabulary can be used later without changing game rules.

`WordManager()` loads these three files relative to `word_manager.py`, independent
of the process's working directory. An optional `words_dir` can be absolute or
relative to that module. Loading strips surrounding whitespace, ignores blank
lines, lowercases words, and removes duplicates while preserving first occurrence.
Files are read without being rewritten. Any invalid entry rejects its list with
a filename and line number; missing, unreadable, non-UTF-8, and empty files raise
`WordListError`. Difficulty names are case-insensitive; unsupported or missing
values raise `ValueError`.

`words_for(difficulty)` returns an immutable tuple for server-side inspection.
`random_word(difficulty)` chooses uniformly from that difficulty's unique words.
Consecutive choices may repeat. A manager validates all lists when constructed
and keeps them in memory; construct a new manager to reload changed files.

The manager returns the selected word only to its Python caller. Pass it to
`HangmanGame(word, difficulty)` and use `game.to_state()` for future browser
responses. That serializer omits the answer while playing. The vocabulary stays
outside `static/`; neither the manager nor this phase adds a browser endpoint.
