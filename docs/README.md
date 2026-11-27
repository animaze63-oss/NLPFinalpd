# Scifi Cinema Lens — research docs

**Use case:** a user selects a science-fiction film and explores its written reviews through a cinematic dashboard.
**Question the app answers:** *What do reviewers praise or criticise about sci-fi movies — especially their visuals, story, characters and soundtrack?*
**Hard constraints:** use **both NLTK and spaCy** in one app; **deploy on Netlify**.

These files are context for the team of agents that will build the app. Read them in order.

| # | File | What it covers |
|---|---|---|
| 1 | [01-nltk.md](01-nltk.md) | Tokenizing, stopwords, VADER sentiment (incl. sci-fi lexicon fixes), FreqDist, collocations, required NLTK data |
| 2 | [02-spacy.md](02-spacy.md) | Model choice, NER, noun chunks, lemmas, dependency-based aspect↔opinion extraction, aspect lexicon |
| 3 | [03-dataset.md](03-dataset.md) | Recommended dataset (Rotten Tomatoes critic reviews, Kaggle, CC0), schema, caveats, alternatives |
| 4 | [04-netlify-deployment.md](04-netlify-deployment.md) | What Netlify can/can't run (build Python, Functions, Edge, Pyodide) and the recommended architecture + JSON contract |
| 5 | [expert-roster.md](expert-roster.md) | The 12 expert agents (incl. Orchestrator, Meta, NLTK and spaCy experts), one-line jobs, hand-offs, and the shared-skills matrix |

**Decision (final):** everything runs on Netlify, with no outside servers. NLTK and spaCy run over the dataset at build time and write static files. NLTK also runs live in the browser via Pyodide for "Analyze your own review".

## Key decisions (summary)

1. **Architecture:** Python NLP runs **at Netlify build time** and writes static JSON; the dashboard is a static site that reads it. Netlify Functions support only TypeScript/JavaScript/Go, Edge Functions are Deno, so neither can run NLTK or spaCy.
2. **spaCy runs only at build time** — it is not available in Pyodide. **NLTK is** (nltk 3.9.4 is a Pyodide built-in), so an optional lazy-loaded "score your own review" panel can run VADER in the browser.
3. **Division of labour:**
   - **spaCy** → sentence splitting, lemmas, NER (people, compared films, studios), noun chunks, dependency parse linking opinion adjectives to aspect nouns.
   - **NLTK** → VADER sentiment per sentence/review, stopwords, FreqDist of spaCy lemmas, bigram/trigram collocations, optional Naive Bayes baseline.
   - **Combined** → aspect-based sentiment for **visuals / story / characters / soundtrack**.
4. **Dataset:** Kaggle *Rotten Tomatoes movies and critic reviews* (CC0, scraped Oct 2020). Filter "Science Fiction & Fantasy" down to a curated sci-fi film list, keep films with ≥ 40 reviews, commit only the small subset CSV. Use `review_type` (Fresh/Rotten) to evaluate VADER.
5. **Model:** `en_core_web_sm` 3.8.0 (12 MB), pinned as a wheel URL in `requirements.txt`; `PYTHON_VERSION=3.12` in `netlify.toml`.

## End-to-end pipeline (per review)

```
review_content
  └─ spaCy nlp.pipe ─► sentences ─► for each sentence:
        ├─ NLTK VADER compound score
        ├─ aspect nouns (lemma ∈ aspect lexicon, PhraseMatcher for multi-word)
        ├─ opinion words via deps (amod, nsubj+acomp, conj, neg)
        ├─ entities (PERSON, WORK_OF_ART, ORG …)
        └─ noun chunks
  └─ lemmas (no stopwords) ─► NLTK FreqDist + collocations (split by pos/neg)
aggregate per film ─► site/data/film/<slug>.json ─► dashboard
```

## Suggested agent roles

- **Data agent** — download/filter the Kaggle dataset, curate the sci-fi list, commit `data/scifi_reviews.csv`.
- **NLP pipeline agent** — `pipeline/` (spaCy + NLTK), aspect lexicon, VADER evaluation, emits JSON per the contract in doc 04.
- **Frontend agent** — cinematic static dashboard (film picker, aspect chart, praise vs. criticism words, quotes, entities, timeline), optional Pyodide panel.
- **Deploy/QA agent** — `netlify.toml`, `requirements.txt`, build verification, accessibility and performance checks.

## Open items to verify during the build

- Exact column list and row counts after downloading the Kaggle files.
- Netlify build time limit on the team's plan (expected 15 min default).
- Pyodide version to pin (stable docs show 314.0.8) and the URL for loading it.
