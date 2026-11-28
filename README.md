# Scifi Cinema Lens

**What do critics praise or criticise about science-fiction films, especially their visuals, story, characters and soundtrack?**

Scifi Cinema Lens is a cinematic dashboard for an NLP final project. You pick a sci-fi film and see what critics say about it.
The app uses **both NLTK and spaCy** and is **deployed on Netlify** with no outside servers. You can also paste your own critique
into **Analyze your own critique**. NLTK then scores it inside your browser with Pyodide, and the text never leaves your device.

- Live site: deploy with the steps below. Netlify gives you a `https://<site-name>.netlify.app` URL.
- Repository: https://github.com/animaze63-oss/NLPFinalpd
- In-app pages: `/` (film picker and dashboards), `/methodology.html` (evaluation), `/resources.html` (every link the project relies on).

## Architecture

```
data/scifi_reviews.csv ──► Netlify build (Python 3.12) ─────────────────────────────────────────┐
data/scifi_films.csv       pipeline/build_data.py                                               │
                           ├─ spaCy en_core_web_sm: NER + EntityRuler, noun chunks, lemmas,     │
                           │  dependency links aspect ↔ opinion                                 │
                           ├─ NLTK: sent/word tokenize, stopwords, VADER, FreqDist, collocations │
                           └─ evaluate.py: VADER vs Fresh/Rotten, aspect gold set                │
                           → site/data/*.json (validated against schemas/)                      │
                           scripts/prepare_pyodide.py → site/pyodide/v314.0.8/ (self-hosted)    │
                                                                                                ▼
Netlify CDN serves site/ (static HTML/CSS/JS + self-hosted Chart.js) ──► browser reads the JSON
"Analyze your own critique" ──► module Web Worker ──► Pyodide + NLTK VADER (same analyze_text.py
                                                       and lexicon.json as the build)
```

The decision record (`CLAUDE.md`) has the full rules. In short:
- Python runs only at build time.
- spaCy never runs in the browser, because it is not available in Pyodide.
- There are no Netlify Functions or Edge Functions.
- Pyodide is self-hosted, with no runtime CDN.
- The Content-Security-Policy `connect-src 'self'` means the analyzer cannot send text anywhere.

## Which parts use NLTK and which use spaCy

Every panel in the app carries a badge: **NLTK**, **spaCy**, **spaCy + NLTK** or **Dataset**.

| Result | Library | Code |
|---|---|---|
| Sentence splitting (`punkt_tab`), word tokens, English and sci-fi stopwords | NLTK | `pipeline/analyze_text.py`, `pipeline/nlp_nltk.py` |
| VADER sentiment per review and per sentence, with sci-fi overrides (*alien*, *war*, *dark* → 0) | NLTK | `analyze_text.make_analyzer` |
| Praise vs criticism words (`FreqDist`), key phrases (bigram and trigram collocations, likelihood ratio) | NLTK | `nlp_nltk.top_words`, `nlp_nltk.collocations` |
| Named entities with an `EntityRuler` before `ner` | spaCy | `pipeline/nlp_spacy.py` |
| Noun-chunk aspects ("visual effects", "sound design", "third act", "lead performance") | spaCy | `nlp_spacy.noun_chunk_aspects` |
| Aspect ↔ opinion links (`amod`, `nsubj` + `acomp`, `conj`, `neg`, `compound`, PhraseMatcher) | spaCy | `nlp_spacy.sentence_aspects` |
| Aspect sentiment for visuals, story, characters and soundtrack | spaCy finds, NLTK scores | `build_data.build_film` |
| displaCy dependency diagrams (pre-rendered SVG) | spaCy | `nlp_spacy.render_examples` |
| Analyze your own critique (in the browser) | NLTK in Pyodide | `site/js/analyzer.worker.mjs` + `site/py/analyze_text.py` |

**Template translation.** The project brief used a product-review template: "brands and products" and noun-chunk aspects
such as "battery life". In the film domain:
- The EntityRuler adds **STUDIO** (Warner Bros., 20th Century Fox, A24), **FRANCHISE** (Star Wars, Alien, Mad Max) and
  **FILM_TECH** (IMAX, 3D, CGI, motion capture) patterns.
- It also adds **PERSON** and **WORK_OF_ART** patterns seeded from each film's directors, writers, cast and title.
- Noun-chunk aspects are film phrases such as "visual effects", "sound design", "production design", "third act",
  "world building" and "lead performance", mapped to visuals, story, characters and soundtrack.

## Project layout

```
data/            committed sample (CSV), aspect gold set, make_subset.py, provenance README
pipeline/        lexicon.py (shared lists), analyze_text.py (NLTK, also runs in Pyodide), nlp_nltk.py,
                 nlp_spacy.py, evaluate.py, build_data.py (Netlify build entry point)
schemas/         JSON Schemas for site/data/*.json (data contract 1.0)
scripts/         prepare_pyodide.py (self-host Pyodide + wheels + NLTK data), serve.py (local Netlify-like server)
site/            static site: index.html, methodology.html, resources.html, css/, js/, vendor/chart.umd.min.js
                 generated at build time (git-ignored): data/, py/, pyodide/, nltk_data/
tests/           pytest: NLTK, spaCy, pipeline, schema validation, parity
e2e/             Playwright + axe tests (own package.json so Netlify installs no Node packages)
netlify.toml     build command, publish folder, PYTHON_VERSION, redirects, headers
requirements.txt pinned build dependencies (nltk 3.9.4 matches Pyodide's nltk for parity)
docs/, knowledge/, .claude/   research notes and the agent team that built the app
```

## Run it locally

You need Python 3.12 or newer (3.13 also works) and Node 18 or newer (only for the browser tests).

Create a virtual environment:

```bash
python3.12 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install the pinned build dependencies (spaCy's English model comes as a wheel URL):

```bash
pip install -r requirements.txt
```

Run the same build command Netlify runs (NLTK data, then the NLP pipeline, then the self-hosted Pyodide files):

```bash
python -m nltk.downloader -d ./nltk_data punkt_tab stopwords vader_lexicon && NLTK_DATA=./nltk_data python pipeline/build_data.py && NLTK_DATA=./nltk_data python scripts/prepare_pyodide.py
```

Serve `site/` with the same redirects and headers as `netlify.toml`:

```bash
python scripts/serve.py --port 8888
```

Then open http://127.0.0.1:8888/ in your browser.

## Deploy to Netlify (step by step)

1. Push this repository to GitHub. `main` is the production branch.
2. In Netlify, choose **Add new project → Import an existing project → GitHub** and pick `animaze63-oss/NLPFinalpd`.
3. Leave the build settings empty in the UI. `netlify.toml` overrides them:
   - **Build command:** downloads NLTK data, runs `pipeline/build_data.py`, then `scripts/prepare_pyodide.py`.
   - **Publish directory:** `site`
   - **Environment:** `PYTHON_VERSION = "3.12"` and `NLTK_DATA = "./nltk_data"`.
   - Because `requirements.txt` is in the base directory, Netlify runs `pip install -r requirements.txt` automatically
     before the build command ([docs](https://docs.netlify.com/build/configure-builds/manage-dependencies/)).
4. Click **Deploy**. Expected build log lines:
   ```
   [build] 14 films, 1120 reviews
   [build] spaCy 3.6s, NLTK 0.4s
   [build] wrote 19 JSON files, 212 KB total (largest film file 13 KB)
   [build] VADER vs Fresh/Rotten accuracy (2-class): 0.685
   [pyodide] wheels: nltk-3.9.4-py3-none-any.whl, regex-2026.3.32-cp314-cp314-pyemscripten_2026_0_wasm32.whl
   [pyodide] site/pyodide/v314.0.8 15.0 MB, site/nltk_data/browser-nltk-data.zip 188 KB
   ```
   Locally, the build command took about 22 s on Python 3.12, and `pip install` took about 15 s with a warm pip cache.
   The publish folder is about 16 MB in 43 files.
5. Verify the deploy:
   - `/` lists 14 films and shows three labelled visuals: the **spaCy** aspect-mentions chart, the **spaCy + NLTK** aspect heatmap and the **NLTK** Tomatometer-vs-VADER chart.
   - `/film/arrival` opens a dashboard with NLTK, spaCy and spaCy + NLTK badges, and the noun-chunk and entity panels show spaCy bar charts.
   - `/resources.html` is linked from both the header and the footer.
   - **Analyze your own critique** returns a VADER score after a few seconds (the first load fetches about 14 MB, cached afterwards).
   - Check the headers. This command should show `Content-Type: application/wasm` and `Cache-Control: public, max-age=31536000, immutable`:
     ```bash
     curl -I https://<site-name>.netlify.app/pyodide/v314.0.8/pyodide.asm.wasm
     ```
6. Every branch or pull request gets a Deploy Preview. To run the browser tests against one, set `BASE_URL` (see Testing).
   To roll back, publish an earlier deploy in **Deploys** in the Netlify UI.

## Testing

Install the test runner:

```bash
pip install -r requirements-dev.txt
```

Run the Python tests (NLTK, spaCy, pipeline, JSON Schema validation, parity). Run the build first:

```bash
NLTK_DATA=./nltk_data python -m pytest -q
```

Install the browser-test dependencies:

```bash
npm --prefix e2e install
```

Run the Playwright and axe tests. They start `scripts/serve.py` automatically:

```bash
npm --prefix e2e test
```

Run the same browser tests against a Deploy Preview:

```bash
BASE_URL=https://deploy-preview-1--your-site.netlify.app npm --prefix e2e test
```

What the tests cover:
- VADER reference sentences from the NLTK how-to, and the sci-fi overrides.
- spaCy dependency rules and EntityRuler labels.
- Every JSON file validates against `schemas/`, with no NaN, size budgets, and every quote credited to critic and publication.
- The picker → dashboard flow and deep links.
- NLTK and spaCy labels on every panel.
- The Resources page links, reachable from the header and the footer.
- Layout at 360 px.
- axe WCAG 2.2 AA checks in dark and light themes.
- The Pyodide analyzer is lazy-loaded, makes no outside requests, and its output matches the build-time
  `site/data/parity.json` to 3 dp.

## Results (from `site/data/eval.json`)

Measured on 1,120 reviews: 818 Fresh and 302 Rotten.

- VADER with the sci-fi overrides vs Fresh/Rotten, 2-class rule (compound ≥ 0 → Fresh):
  - accuracy 0.685, balanced accuracy 0.582, macro-F1 0.585.
- Baseline "always Fresh": accuracy 0.73, balanced accuracy 0.5.
- Stock VADER without the overrides: accuracy 0.679.
- On 61 hand-labelled sentences (single annotator):
  - spaCy aspect detection: micro precision 0.955, recall 0.568.
  - Browser keyword matcher: precision 0.917, recall 0.595.

How to read these numbers:
- Lexicon sentiment barely beats chance at separating Fresh from Rotten in short critic blurbs. Irony, plot
  description and "recommended overall but critical in places" reviews are the main failure modes.
- Accuracy alone flatters any model because most reviews are Fresh. Use balanced accuracy.

The methodology page discusses all of this.

## Dataset and licence

The data is the Rotten Tomatoes movies and critic reviews dataset by Stefano Leone, Kaggle, **CC0**:
https://www.kaggle.com/datasets/stefanoleone992/rotten-tomatoes-movies-and-critic-reviews-dataset

It was downloaded from a byte-identical GitHub mirror because Kaggle needs a login. Only a small sample is committed:
14 films × 80 reviews, about 240 KB. [`data/README.md`](data/README.md) records the exact mirror, commit, checksums and filters.

Review excerpts are the words of the credited critics and publications. They are shown with attribution and are not ours.

## Credits

- [NLTK](https://www.nltk.org/) and the [VADER](https://github.com/cjhutto/vaderSentiment) lexicon (Hutto & Gilbert, 2014).
- [spaCy](https://spacy.io/) and `en_core_web_sm` 3.8.0.
- [Pyodide](https://pyodide.org/en/stable/) 314.0.8.
- [Chart.js](https://www.chartjs.org/) 4.6.2 (MIT, self-hosted in `site/vendor/`).
- [pandas](https://pandas.pydata.org/docs/) and [jsonschema](https://python-jsonschema.readthedocs.io/en/stable/).
- Built by the Scifi Cinema Lens agent team (`.claude/agents/`).
