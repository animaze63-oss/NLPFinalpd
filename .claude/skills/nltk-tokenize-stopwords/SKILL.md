---
name: nltk-tokenize-stopwords
description: "Tokenize review text with NLTK and filter stopwords safely. Use when splitting sentences/words or building word-frequency inputs."
---

# nltk-tokenize-stopwords

Used by: **nltk-expert** (owner), pipeline-engineer, pyodide-engineer

- `sent_tokenize` / `word_tokenize` need `punkt_tab` (NLTK 3.9+). `word_tokenize(sent, preserve_line=True)` when the sentence is already split (by spaCy).
- `stopwords.words("english")` → set; add domain words (film, movie, sci, fi, …) only for the "top words" chart.
- Never remove negators (`not`, `no`, `never`, `nor`, `n't`) from text sent to VADER, and never remove aspect triggers from text used for aspect detection.

Reference: `knowledge/nltk-expert/tokenize.md`, `knowledge/nltk-expert/stopwords-corpora.md`.
