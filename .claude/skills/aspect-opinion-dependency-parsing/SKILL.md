---
name: aspect-opinion-dependency-parsing
description: "Link opinion words to the aspect they describe (visuals, story, characters, soundtrack) using spaCy dependency relations, then score them with VADER. Use when building or debugging aspect-based sentiment."
---

# aspect-opinion-dependency-parsing

Used by: **spacy-expert** (owner), nltk-expert, nlp-evaluator

Rules on each aspect noun (lemma in the lexicon, or PhraseMatcher span):
- `amod` ADJ children → opinions ("gorgeous score").
- If the noun is `nsubj`, ADJ children of its head with `acomp`/`attr` → opinions ("the plot is thin").
- Follow `conj` from each opinion ("beautiful and haunting music").
- `neg` child on the head → negated (flip in reporting).
- Join `compound` + head for multi-word aspects ("sound design").
Score: VADER on the sentence (primary) and on the opinion phrase (secondary); store both.
Unit-test each rule with one sentence.

Reference: `knowledge/spacy-expert/linguistic-features.md`, `knowledge/spacy-expert/rule-based-matching.md`.
