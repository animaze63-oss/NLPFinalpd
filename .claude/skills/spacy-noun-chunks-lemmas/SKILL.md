---
name: spacy-noun-chunks-lemmas
description: "Use spaCy noun chunks and lemmas to find what reviewers talk about. Use when building topic lists, lemma inputs for NLTK counts, or mapping phrases to aspects."
---

# spacy-noun-chunks-lemmas

Used by: **spacy-expert** (owner), nltk-expert, pipeline-engineer

- `doc.noun_chunks` → count by lowercased text without determiners; map `chunk.root.lemma_` to an aspect.
- Lemma stream for NLTK: `[t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop]`.
- Adjective cloud: tokens with `pos_ == "ADJ"`.

Reference: `knowledge/spacy-expert/linguistic-features.md`.
