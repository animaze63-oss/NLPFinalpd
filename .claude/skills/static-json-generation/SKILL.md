---
name: static-json-generation
description: "Aggregate NLP results per film and write compact, valid static JSON for the site. Use when creating or changing files under site/data/."
---

# static-json-generation

Used by: **pipeline-engineer** (owner), spacy-expert, nltk-expert

- Write with `ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False`, UTF-8.
- Round floats to 3 dp; replace NaN with null; quotes ≤ 300 chars with critic + publisher.
- Files: `films.json`, `film/<slug>.json` (< 150 KB each), `eval.json`, `lexicon.json`.
- Validate every file against `schemas/` before finishing; fail the build on errors.

Reference: `knowledge/pipeline-engineer/json-output.md`, `knowledge/pipeline-engineer/data-contract.md`.
