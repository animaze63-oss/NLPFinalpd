# Data contract (owned by PIPE, consumed by FE, PYO, EVAL, QA)

From ../../docs/04-netlify-deployment.md. Version it: every file has `"schema_version": "1.x"`.

| File | Content |
|---|---|
| `site/data/films.json` | index: slug, title, year, directors, n_reviews, tomatometer, mean_compound, aspect summary |
| `site/data/film/<slug>.json` | per-film: sentiment, aspects{visuals,story,characters,soundtrack}{mentions, mean_compound, top_opinions, quotes}, top_words{positive,negative}, collocations, entities, noun_chunks, timeline |
| `site/data/eval.json` | VADER vs Fresh/Rotten metrics, aspect-extraction precision, versions of nltk/spacy/model, lexicon overrides |
| `site/data/lexicon.json` | aspect trigger lists + VADER overrides — the single source the Pyodide analyzer also loads (parity) |

Rules: slugs are lowercase-kebab ASCII; numbers rounded to 3 dp; quotes ≤ 300 chars with critic + publisher; no NaN; each per-film file < 150 KB.

## Implemented: contract 1.0 (2026-11-28)

The schemas in `../../schemas/` are authoritative, and `pipeline/build_data.py` validates every file before it is written.
- `films.json`: `{schema_version, build{nltk, spacy, model, python, n_films, n_reviews, lexicon_version}, films[{slug, title, year, directors, n_reviews, tomatometer, mean_compound, aspects{a: mean|null}, aspect_mentions}]}`
- `film/<slug>.json`:
  - film fields: `slug, title, year, directors, cast, studio, critics_consensus, rt_url, n_reviews, n_fresh, n_rotten, n_top_critics, tomatometer`
  - `sentiment{source:"nltk", mean_compound, positive, neutral, negative, n_sentences, histogram[10]}`
  - `aspects{visuals|story|characters|soundtrack: {mentions, reviews, mean_compound, positive, neutral, negative, top_terms, top_opinions[{word, count, valence, negated}], quotes[]}}`
  - NLTK: `top_words{positive, negative}`, `collocations{positive, negative, all}[{phrase, count, score}]`
  - spaCy: `entities[{text, label, count, source: ruler|model}]`, `noun_chunks[{phrase, count, aspect|null}]`
  - `timeline[{year, n, mean_compound}]`, `quotes{most_positive, most_negative}`
  - `sources{panel: nltk|spacy|spacy+nltk|dataset}`
  - quote objects: `{text ≤ 300, critic, publisher, top_critic, review_type, date, compound}`
- `lexicon.json`: `lexicon.export()` plus `schema_version`. The Pyodide worker loads it (parity).
- `parity.json`: the build-time output of `analyze_text.analyze` on 10 fixed sentences. The e2e tests compare it with Pyodide.
- `examples.json`: displaCy dependency SVGs of 2 real, attributed review sentences.
- `eval.json`: see `pipeline/evaluate.py`.
