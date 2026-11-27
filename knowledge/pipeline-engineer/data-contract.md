# Data contract (owned by PIPE, consumed by FE, PYO, EVAL, QA)

From ../../docs/04-netlify-deployment.md. Version it: every file has `"schema_version": "1.x"`.

| File | Content |
|---|---|
| `site/data/films.json` | index: slug, title, year, directors, n_reviews, tomatometer, mean_compound, aspect summary |
| `site/data/film/<slug>.json` | per-film: sentiment, aspects{visuals,story,characters,soundtrack}{mentions, mean_compound, top_opinions, quotes}, top_words{positive,negative}, collocations, entities, noun_chunks, timeline |
| `site/data/eval.json` | VADER vs Fresh/Rotten metrics, aspect-extraction precision, versions of nltk/spacy/model, lexicon overrides |
| `site/data/lexicon.json` | aspect trigger lists + VADER overrides — the single source the Pyodide analyzer also loads (parity) |

Rules: slugs are lowercase-kebab ASCII; numbers rounded to 3 dp; quotes ≤ 300 chars with critic + publisher; no NaN; each per-film file < 150 KB.
