# 04 — Netlify: what it can and cannot run, and the recommended architecture

The app **must** be deployed on Netlify. NLTK and spaCy are Python libraries. This document establishes where Python can run on Netlify and picks an architecture. All facts below were checked against the current Netlify / Pyodide docs on 2026-11-25 (links at the bottom).

## TL;DR

| Where | Python? | NLTK | spaCy | Verdict |
|---|---|---|---|---|
| **Netlify build** (CI container) | ✅ Yes — any official Python version | ✅ | ✅ | **Run the whole NLP pipeline here** |
| **Netlify Functions** (serverless) | ❌ No — TypeScript, JavaScript, Go only | ❌ | ❌ | Not usable for NLP; optional JS glue only |
| **Netlify Edge Functions** (Deno) | ❌ No (TS/JS on Deno; 50 ms CPU/request) | ❌ | ❌ | Not usable |
| **Browser via Pyodide** (static files served by Netlify) | ✅ Yes — CPython compiled to WebAssembly | ✅ nltk 3.9.4 is a built-in package | ❌ Not available | Optional: live NLTK/VADER on user-typed text |

**Recommended architecture:** *build-time Python NLP → static JSON → static cinematic dashboard*, with an optional *Pyodide + NLTK "try your own review"* panel. spaCy runs only at build time.

---

## 1. Netlify build environment (✅ Python works)

From *Available software at build time*:

- Build image: **Ubuntu 24.04 (Noble Numbat)**.
- **Python:** default `3.x`; "Any official Python version". Set with build env var **`PYTHON_VERSION`**, a `Pipfile`, or `runtime.txt` (runtime.txt must contain only `x.y`, no trailing newline).
- `pip` and Pipenv are available.
- Node.js default 24 (handy if the frontend uses a JS bundler).

From *Manage build dependencies*:

- If a **`requirements.txt`** is in the site's **base directory**, Netlify **automatically runs `pip install`** on it before the build command. (Pipfile + Pipfile.lock → `pipenv install`.)

Practical consequences:

- Put `nltk`, `spacy`, `pandas`, and the `en_core_web_sm` wheel URL in `requirements.txt` (see [02-spacy.md](02-spacy.md)) — no `spacy download` step needed.
- NLTK data must be downloaded in the build command (`python -m nltk.downloader -d ./nltk_data punkt_tab stopwords vader_lexicon`) or committed to the repo.
- The Kaggle dataset needs a login → **commit the pre-filtered sci-fi subset CSV** (`data/scifi_reviews.csv`, a few MB) instead of downloading at build time.
- **Build time limit:** builds are time-limited (commonly 15 minutes by default — *not re-verified in this research; check Site configuration → Build & deploy*). spaCy `en_core_web_sm` on tens of thousands of short reviews with `nlp.pipe` takes minutes, well within that. Keep the corpus to the curated films.
- Safety valve: also commit the generated JSON. If the build ever has trouble, set the build command to skip the pipeline and just publish.

Example `netlify.toml`:

```toml
[build]
  command = "python -m nltk.downloader -d ./nltk_data punkt_tab stopwords vader_lexicon && NLTK_DATA=./nltk_data python pipeline/build_data.py"
  publish = "site"

[build.environment]
  PYTHON_VERSION = "3.12"
```

## 2. Netlify Functions (❌ no Python)

- *Get started with functions* offers three languages: **TypeScript, JavaScript, Go** ("To write functions in Go, use the Lambda-compatible functions API"). Python is not offered. Community answers confirm there is no Python Lambda support on Netlify.
- Defaults (*Configuration for functions*): memory **1024 MB**; **synchronous execution limit 60 s**; scheduled 30 s; background 15 min (none configurable). Streaming responses: 10 s, 20 MB.
- Memory can be raised to 4 GB only on credit-based Pro/Enterprise plans; usage is billed in GB-hours.
- ⇒ Functions cannot import NLTK or spaCy. Do **not** design an "/api/analyze" Python endpoint on Netlify. If the team wants an API later, it would have to live on another host — out of scope given the Netlify requirement.

## 3. Netlify Edge Functions (❌ no Python)

- Run on **Deno** (TypeScript/JavaScript). Limits: code size **20 MB** compressed, **512 MB** memory, **50 ms CPU per request**, 40 s response-header timeout.
- ⇒ No Python, and 50 ms CPU rules out heavy NLP even via WASM.

## 4. Python in the browser with Pyodide (✅ NLTK, ❌ spaCy)

- Pyodide = CPython compiled to WebAssembly; it is just static files, so Netlify can serve it (or load it from the jsDelivr CDN).
- **Built-in packages** on the stable docs (Pyodide 314.0.8): **`nltk` 3.9.4**, `regex`, `numpy` 2.4.6, `pandas` 3.0.2, `scikit-learn` 1.8.0. Load with `await pyodide.loadPackage("nltk")` (or `micropip`).
- **spaCy is not available**, nor its compiled deps (`thinc`, `blis`, `cymem`, `preshed`, `murmurhash`, `srsly`). The open request (pyodide-recipes#179, since 2020) cites `cython-blis` failing to build for WASM; previous spaCy PRs were closed unmerged. A community demo exists (`spacy-wasm`) but is unofficial and not something to bet a final project on.
- NLTK data in the browser: `nltk.download()` needs network access to GitHub and a writable filesystem; simpler to **ship `vader_lexicon.zip` (and `punkt_tab` if needed) as static files** in `site/nltk_data/`, fetch them into Pyodide's virtual FS (`/home/pyodide/nltk_data/sentiment/...`) and set `nltk.data.path`.
- Cost: the Pyodide runtime plus packages is a multi-MB download and a few seconds of startup → **lazy-load** it only when the user opens the "analyze your own review" panel.

## 5. Recommended architecture

```
                         ┌────────────────── Netlify build (Ubuntu 24.04, Python 3.12) ──────────────────┐
 data/scifi_reviews.csv ─►  pipeline/build_data.py                                                        │
 (committed subset)      │   spaCy en_core_web_sm: sentences, NER, noun chunks, lemmas, dependency arcs   │
                         │   NLTK: tokenize, stopwords, VADER (sentence + review), FreqDist, collocations │
                         │   aspect mapping (visuals / story / characters / soundtrack)                   │
                         │   → site/data/films.json  (index: title, year, director, n_reviews, scores)    │
                         │   → site/data/film/<slug>.json (per-film aggregates + top quotes)              │
                         │   → site/data/eval.json   (VADER vs Fresh/Rotten accuracy)                     │
                         └───────────────────────────────────────┬───────────────────────────────────────┘
                                                                 ▼
                         Netlify CDN serves static site/: index.html + JS + CSS + JSON
                                                                 ▼
          Browser: film picker → cinematic dashboard (aspect radar/bars, sentiment timeline,
          praise vs. criticism words, collocations, entities, example quotes)
          Optional lazy panel: Pyodide + NLTK VADER scores text the user types
```

Why this design:

1. **Both libraries are genuinely used** and their Python code is gradable (`pipeline/`), meeting the "NLTK and spaCy in one app" requirement.
2. **Works on any Netlify plan**: only static hosting + a Python build; no functions needed.
3. **Fast UX**: the dashboard loads small JSON files; no model runs on page load.
4. **Reproducible**: every deploy reruns the pipeline from the committed CSV.
5. **Interactive NLP** is still possible in the browser with Pyodide + NLTK, without pretending spaCy can run there. (If live spaCy-style output is wanted, show precomputed displaCy SVGs for example sentences.)

### Per-film JSON shape (suggested contract between pipeline and frontend agents)

```json
{
  "slug": "blade-runner-2049",
  "title": "Blade Runner 2049", "year": 2017, "directors": ["Denis Villeneuve"],
  "n_reviews": 412, "tomatometer": 88, "critics_consensus": "...",
  "sentiment": { "mean_compound": 0.41, "pos": 0.71, "neu": 0.12, "neg": 0.17 },
  "aspects": {
    "visuals":    { "mentions": 230, "mean_compound": 0.62, "top_opinions": [["stunning", 41], ["gorgeous", 30]], "quotes": [{"text": "...", "critic": "...", "publisher": "...", "compound": 0.8}] },
    "story":      { "...": "..." },
    "characters": { "...": "..." },
    "soundtrack": { "...": "..." }
  },
  "top_words":   { "positive": [["visual", 120]], "negative": [["long", 33]] },
  "collocations":{ "positive": ["production design"], "negative": ["running time"] },
  "entities":    { "PERSON": [["Hans Zimmer", 21]], "WORK_OF_ART": [["Blade Runner", 88]] },
  "noun_chunks": [["the visual effects", 40]],
  "timeline":    [{ "month": "2017-10", "mean_compound": 0.45, "n": 210 }]
}
```

### Suggested repo layout

```
requirements.txt          # nltk, spacy, pandas, en_core_web_sm wheel
netlify.toml
data/scifi_reviews.csv    # committed, filtered subset
pipeline/                 # build_data.py, aspects.py, nlp_nltk.py, nlp_spacy.py
site/                     # index.html, app.js, styles.css, data/ (generated), nltk_data/ (for Pyodide)
docs/                     # this research
```

### Rejected options

- **Python Netlify Function** — not supported.
- **spaCy in the browser** — not in Pyodide; unofficial builds are fragile.
- **External Python API (Render/Railway/etc.) + Netlify frontend** — works technically, but adds a second host, cold starts and cost, and weakens "deployed on Netlify".
- **Rewriting the NLP in JavaScript (compromise.js, wink-nlp, vader-sentiment JS ports)** — would drop the NLTK/spaCy requirement.

## Sources

- Netlify — Available software at build time: https://docs.netlify.com/build/configure-builds/available-software-at-build-time/
- Netlify — Manage build dependencies: https://docs.netlify.com/build/configure-builds/manage-dependencies/
- Netlify — Get started with functions (TS/JS/Go): https://docs.netlify.com/build/functions/get-started/
- Netlify — Configuration for functions (limits): https://docs.netlify.com/build/functions/configuration/
- Netlify — Lambda compatibility (streaming limits): https://docs.netlify.com/build/functions/lambda-compatibility/
- Netlify — Functions usage and billing: https://docs.netlify.com/build/functions/usage-and-billing/
- Netlify — Edge Functions limits: https://docs.netlify.com/build/edge-functions/limits/
- Netlify — configurable Python versions announcement: https://www.netlify.com/blog/announcing-configurable-python-versions-in-netlify-builds
- Netlify forum — Python lambda functions: https://answers.netlify.com/t/python-lambda-functions/3423
- Pyodide — Packages built in Pyodide: https://pyodide.org/en/stable/usage/packages-in-pyodide.html
- Pyodide — spaCy request: https://github.com/pyodide/pyodide-recipes/issues/179
- NLTK — Installing NLTK data: https://www.nltk.org/data.html
