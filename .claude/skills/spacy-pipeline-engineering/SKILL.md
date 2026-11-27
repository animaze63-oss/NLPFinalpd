---
name: spacy-pipeline-engineering
description: "Load and run the spaCy en_core_web_sm pipeline efficiently at build time. Use when processing reviews with spaCy, adding components, or tuning speed."
---

# spacy-pipeline-engineering

Used by: **spacy-expert** (owner), pipeline-engineer

- `en_core_web_sm` 3.8.0 (12 MB), pinned as a wheel URL in requirements.txt with `spacy>=3.8,<3.9`.
- Process with `nlp.pipe(((text, meta) for ...), as_tuples=True, batch_size=500)`; never `nlp()` in a loop over thousands of texts.
- Keep tagger + attribute_ruler (lemmas depend on them), parser (deps, sents, noun_chunks) and ner.
- Add the EntityRuler with `before="ner"`.

Reference: `knowledge/spacy-expert/pipelines.md`, `knowledge/spacy-expert/en-core-web-sm.md`.
