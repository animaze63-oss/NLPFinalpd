---
name: nltk-frequency-collocations
description: "Count words and find collocations with NLTK FreqDist and collocation finders. Use for top-words, praise-vs-criticism words and phrase charts."
---

# nltk-frequency-collocations

Used by: **nltk-expert** (owner), pipeline-engineer, nlp-evaluator

- Input: spaCy lemmas, alphabetic, non-stopword, lowercase.
- `FreqDist(...).most_common(25)`; `ConditionalFreqDist` by sentiment label.
- `BigramCollocationFinder.from_words(tokens)`; `apply_freq_filter(3)`; `apply_word_filter(stop)`; rank with `likelihood_ratio` (PMI only with the frequency filter).
- Produce separate lists for positive and negative sentences.

Reference: `knowledge/nltk-expert/freqdist-collocations.md`.
