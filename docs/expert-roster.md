# Expert roster — Scifi Cinema Lens

The team of expert agents needed to **design, build, test and deploy** Scifi Cinema Lens.

## Decision record (constraints every agent follows)

1. **Everything runs on Netlify. No outside servers, APIs or databases.**
2. **Build time:** during the Netlify build, NLTK and spaCy process the committed sci-fi review dataset and write **static JSON** files.
3. **Runtime:** a **static site** served by Netlify's CDN reads that JSON.
4. **Live NLP in the browser:** the **"Analyze your own review"** panel runs **NLTK (VADER) in the browser with Pyodide**. spaCy is not available in Pyodide, so it runs only at build time.
5. **No Netlify Functions or Edge Functions for NLP.** They can't run Python.

Background: [04-netlify-deployment.md](04-netlify-deployment.md).

Only roles a static site, a Python build step and Pyodide actually need are on this roster. See [Roles deliberately left out](#roles-deliberately-left-out).

---

## 1. The roster

| # | Agent (ID) | One-line job description | Main phases |
|---|---|---|---|
| 1 | **Orchestrator** (`ORC`) | Breaks the project into tasks, assigns them to agents, sequences the hand-offs, merges work and enforces the decision record above. | All |
| 2 | **Meta Agent** (`META`) | Designs and improves the agents themselves: writes and tunes their prompts, skills and checklists, audits their output quality and runs retrospectives. | All (mainly before and between phases) |
| 3 | **Cinematic UX & Visual Designer** (`UX`) | Designs the film-picker → dashboard experience, the "cinematic" visual language and the chart layout, accessible in light and dark themes. | Design |
| 4 | **Dataset Curator** (`DATA`) | Gets the Rotten Tomatoes dataset, curates the true sci-fi film list, cleans and filters reviews, and commits the small subset CSV with attribution and licence notes. | Design, Build |
| 5 | **NLTK Expert** (`NLTK`) | Owns everything NLTK: tokenizing, stopwords, VADER sentiment with sci-fi lexicon fixes, FreqDist and collocations, and packaging NLTK data for the build and for Pyodide. | Design, Build, Test |
| 6 | **spaCy Expert** (`SPACY`) | Owns everything spaCy: the `en_core_web_sm` pipeline, NER with an EntityRuler, noun chunks, lemmas, and dependency rules that link opinion words to visuals, story, characters and soundtrack. | Design, Build, Test |
| 7 | **Build Pipeline Engineer** (`PIPE`) | Combines the NLTK and spaCy modules into `pipeline/build_data.py`: aggregates per film, writes the JSON files that match the agreed data contract, and keeps the build within Netlify's time limit. | Build, Test |
| 8 | **Frontend & Data-Viz Engineer** (`FE`) | Builds the static dashboard (HTML/CSS/JS) and its charts from the generated JSON: aspect scores, praise vs. criticism words, collocations, entities, quotes and timeline. | Build, Test |
| 9 | **Pyodide Engineer** (`PYO`) | Builds the lazy-loaded "Analyze your own review" panel: loads Pyodide and NLTK in a Web Worker, mounts the bundled `vader_lexicon`, and returns VADER and aspect results that match the build-time output. | Build, Test |
| 10 | **NLP Evaluation & Methodology Analyst** (`EVAL`) | Measures how well the NLP works: VADER vs. Fresh/Rotten labels, and aspect extraction against a hand-labelled sample. Writes the in-app methodology panel and the final-project report. | Test, Deploy (report) |
| 11 | **QA & Test Engineer** (`QA`) | Owns the test strategy: pytest for the pipeline, JSON contract checks, Playwright end-to-end and Pyodide tests, plus accessibility and performance audits on Netlify Deploy Previews. | Test |
| 12 | **Netlify Deployment Engineer** (`NET`) | Owns `netlify.toml`, `requirements.txt` and Python/NLTK data setup on Netlify's build image, publish settings, cache headers and Deploy Previews, and gets production deploys passing. | Build, Deploy |

### Who hands what to whom

```
META ─ defines/tunes every agent ─────────────────────────────────────────────┐
ORC  ─ plans, assigns, merges, guards the Netlify-only rule ───────────────────┤
                                                                               ▼
UX ──── wireframes, design tokens ───────────────────────────────► FE, PYO
DATA ── data/scifi_reviews.csv ──────────────────────────────────► NLTK, SPACY, PIPE
NLTK ── nlp_nltk.py, lexicon overrides, nltk_data/ ──────────────► PIPE, PYO
SPACY ─ nlp_spacy.py, aspects.py, displaCy examples ─────────────► PIPE
PIPE ── site/data/*.json (contract in 04-netlify-deployment.md) ─► FE, EVAL, QA
FE ──── static dashboard ────────────────────────────────────────► QA
PYO ─── in-browser analyzer ─────────────────────────────────────► QA
EVAL ── metrics, methodology text, report ───────────────────────► FE (panel), ORC
QA ──── test results, bug reports ───────────────────────────────► owners, ORC
NET ─── netlify.toml, green Deploy Preview and production URL ───► QA, ORC
```

---

## 2. Skills, and which agents share each one

**Owner** is the agent accountable for the skill. **Also uses** lists the agents that need working proficiency.

### A. Coordination and agent design

| Skill | What it means in this project | Owner | Also uses |
|---|---|---|---|
| Task breakdown and planning | Turning the use case into ordered, assignable tasks with clear done-criteria | ORC | META |
| Guarding the constraints | Rejecting designs that need a server, Python Functions or spaCy in the browser | ORC | META, NET, QA |
| Agent prompt and skill design | Writing role prompts, skill files, checklists and hand-off templates for each agent | META | ORC |
| Output review and retrospectives | Grading agent output, finding gaps, refining roles between phases | META | ORC, QA |
| Git/GitHub workflow | Branches, commits, PRs, reviews, merging to `main` | ORC | **all agents** |
| Technical writing | READMEs, docstrings, `docs/`, methodology and final report | EVAL | ORC, META, NLTK, SPACY, PIPE, NET |

### B. Data

| Skill | What it means in this project | Owner | Also uses |
|---|---|---|---|
| Data wrangling with pandas | Joining movies↔reviews, filtering, cleaning nulls, grouping per film | DATA | PIPE, EVAL |
| Sci-fi film curation | Splitting real sci-fi from "Science Fiction & Fantasy"; ≥ 40 reviews per film | DATA | UX (picker content), EVAL |
| Licensing and attribution | CC0 dataset label vs. critics' copyright; critic and publication credits; IMDb non-commercial terms | DATA | EVAL, FE, UX |

### C. NLP

| Skill | What it means in this project | Owner | Also uses |
|---|---|---|---|
| Python 3.12 engineering | Clean modules, type hints, `requirements.txt`, reproducible runs | PIPE | DATA, NLTK, SPACY, PYO, EVAL, QA, NET |
| NLTK tokenizing and stopwords | `sent_tokenize`, `word_tokenize`, `punkt_tab`, domain stopword list that keeps negators | NLTK | PIPE, PYO |
| VADER sentiment and lexicon tuning | Sentence- and review-level compound scores, ±0.05 thresholds, neutralising sci-fi plot words such as *alien*, *war* and *dark* | NLTK | PYO, EVAL |
| Frequency and collocations | `FreqDist` of spaCy lemmas; bigram/trigram finders with PMI or likelihood ratio and frequency filters | NLTK | PIPE, EVAL |
| NLTK data packaging | `nltk.downloader -d`, `NLTK_DATA`, shipping `vader_lexicon` as a static file for Pyodide | NLTK | PYO, NET |
| spaCy pipeline engineering | `en_core_web_sm` wheel pin, `nlp.pipe` batching, disabling unused components | SPACY | PIPE |
| Named entities and EntityRuler | PERSON / WORK_OF_ART / ORG; patterns seeded from directors and actors | SPACY | PIPE |
| Noun chunks and lemmas | Chunk roots mapped to aspects; lemma-based counts | SPACY | NLTK, PIPE |
| Dependency parsing for aspect↔opinion | `amod`, `nsubj`+`acomp`, `conj`, `neg`, `compound`; PhraseMatcher for multi-word aspects | SPACY | NLTK (scores the opinions), EVAL |
| Aspect lexicon design | Trigger lists for visuals / story / characters / soundtrack, ambiguity rules (e.g. *theme*, *sound design*) | SPACY | NLTK, PYO, EVAL |
| Keeping browser and build output consistent | The in-browser analyzer uses the same lexicon overrides and aspect lists as the build | NLTK | PYO, SPACY, QA |
| NLP evaluation metrics | Accuracy, precision/recall/F1, confusion matrix, hand-labelled aspect samples, error analysis | EVAL | NLTK, SPACY, QA |

### D. Build step and data contract

| Skill | What it means in this project | Owner | Also uses |
|---|---|---|---|
| Aggregation and static JSON generation | `films.json`, `film/<slug>.json`, `eval.json`; small, cache-friendly files | PIPE | SPACY, NLTK |
| Data contract design | Versioned JSON schema shared by the pipeline and the UI | PIPE | FE, PYO, QA, ORC |
| Build-time performance budget | Keeping install and processing within Netlify's build limit; profiling `nlp.pipe` | PIPE | SPACY, NET |

### E. Frontend and in-browser Python

| Skill | What it means in this project | Owner | Also uses |
|---|---|---|---|
| Cinematic visual and interaction design | Dark "theater" aesthetic, film-picker flow, motion that doesn't hurt readability | UX | FE |
| Accessibility (WCAG 2.2 AA) | Contrast, keyboard navigation, chart text alternatives, reduced motion | UX | FE, PYO, QA |
| Static frontend engineering | HTML/CSS/vanilla JS (or a static-output bundler), routing per film, fetching JSON | FE | PYO, UX |
| Data visualization | Aspect bars/radar, diverging praise-vs-criticism charts, timelines, word lists | FE | UX, EVAL |
| Pyodide runtime | `loadPyodide`, `loadPackage("nltk")`, virtual filesystem for `nltk_data`, Python↔JS data conversion | PYO | FE, QA |
| Web Workers and lazy loading | Running Pyodide off the main thread and loading it only when the panel opens | PYO | FE |
| Web performance | Page weight, caching, Lighthouse budgets, Pyodide download cost | FE | PYO, NET, QA |

### F. Testing and deployment

| Skill | What it means in this project | Owner | Also uses |
|---|---|---|---|
| Python unit testing (pytest) | Tests for tokenizing, VADER overrides, aspect rules, JSON schema validation | QA | NLTK, SPACY, PIPE, DATA |
| Browser end-to-end testing (Playwright) | Film picker → dashboard flows; Pyodide panel returns scores; works at phone width | QA | FE, PYO |
| Accessibility and Lighthouse audits | Automated (axe/Lighthouse) and manual checks on Deploy Previews | QA | UX, FE |
| Netlify configuration | `netlify.toml`, `PYTHON_VERSION`, auto `pip install` of `requirements.txt`, build command, publish dir, headers | NET | PIPE, ORC |
| Deploy Previews and release | Checking every PR on a preview URL, promoting to production, rollback | NET | QA, ORC |
| Static hosting headers and caching | `Cache-Control` for JSON and Pyodide assets, correct MIME types for `.wasm` | NET | PYO, FE |

### Skill coverage matrix (● owner, ○ also uses)

| Skill | ORC | META | UX | DATA | NLTK | SPACY | PIPE | FE | PYO | EVAL | QA | NET |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Task breakdown and planning | ● | ○ | | | | | | | | | | |
| Guarding the constraints | ● | ○ | | | | | | | | | ○ | ○ |
| Agent prompt and skill design | ○ | ● | | | | | | | | | | |
| Output review and retrospectives | ○ | ● | | | | | | | | | ○ | |
| Git/GitHub workflow | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| Technical writing | ○ | ○ | | | ○ | ○ | ○ | | | ● | | ○ |
| Data wrangling with pandas | | | | ● | | | ○ | | | ○ | | |
| Sci-fi film curation | | | ○ | ● | | | | | | ○ | | |
| Licensing and attribution | | | ○ | ● | | | | ○ | | ○ | | |
| Python 3.12 engineering | | | | ○ | ○ | ○ | ● | | ○ | ○ | ○ | ○ |
| NLTK tokenizing and stopwords | | | | | ● | | ○ | | ○ | | | |
| VADER sentiment and lexicon tuning | | | | | ● | | | | ○ | ○ | | |
| Frequency and collocations | | | | | ● | | ○ | | | ○ | | |
| NLTK data packaging | | | | | ● | | | | ○ | | | ○ |
| spaCy pipeline engineering | | | | | | ● | ○ | | | | | |
| Named entities and EntityRuler | | | | | | ● | ○ | | | | | |
| Noun chunks and lemmas | | | | | ○ | ● | ○ | | | | | |
| Dependency parsing for aspect↔opinion | | | | | ○ | ● | | | | ○ | | |
| Aspect lexicon design | | | | | ○ | ● | | | ○ | ○ | | |
| Keeping browser and build output consistent | | | | | ● | ○ | | | ○ | | ○ | |
| NLP evaluation metrics | | | | | ○ | ○ | | | | ● | ○ | |
| Aggregation and static JSON generation | | | | | ○ | ○ | ● | | | | | |
| Data contract design | ○ | | | | | | ● | ○ | ○ | | ○ | |
| Build-time performance budget | | | | | | ○ | ● | | | | | ○ |
| Cinematic visual and interaction design | | | ● | | | | | ○ | | | | |
| Accessibility (WCAG 2.2 AA) | | | ● | | | | | ○ | ○ | | ○ | |
| Static frontend engineering | | | ○ | | | | | ● | ○ | | | |
| Data visualization | | | ○ | | | | | ● | | ○ | | |
| Pyodide runtime | | | | | | | | ○ | ● | | ○ | |
| Web Workers and lazy loading | | | | | | | | ○ | ● | | | |
| Web performance | | | | | | | | ● | ○ | | ○ | ○ |
| Python unit testing (pytest) | | | | ○ | ○ | ○ | ○ | | | | ● | |
| Browser end-to-end testing (Playwright) | | | | | | | | ○ | ○ | | ● | |
| Accessibility and Lighthouse audits | | | ○ | | | | | ○ | | | ● | |
| Netlify configuration | ○ | | | | | | ○ | | | | | ● |
| Deploy Previews and release | ○ | | | | | | | | | | ○ | ● |
| Static hosting headers and caching | | | | | | | | ○ | ○ | | | ● |

**Skills used by the most agents** (best candidates for shared skill files written by META):
- Git workflow: all 12 agents.
- Python 3.12 engineering: 8 agents.
- Technical writing: 7 agents.
- Data contract design: 5 agents.
- Pytest: 5 agents.

**The NLTK–spaCy overlap is deliberate.** Noun chunks and lemmas, dependency rules, aspect lexicon design and keeping browser and build output consistent are each owned by one expert and used by the other. This is where the two libraries are combined into aspect-based sentiment.

---

## 3. Roles deliberately left out

The Netlify-only, static-site decision removes the need for these roles:

| Role | Why it isn't needed |
|---|---|
| Backend / API engineer | No server and no Python Functions. All NLP runs at build time or in Pyodide. |
| Database administrator | Data ships as static JSON. There's no runtime database. |
| Cloud / DevOps (Docker, Kubernetes, other hosts) | Netlify's build image and CDN do the hosting. |
| ML training / GPU engineer | Uses pretrained `en_core_web_sm` and the rule-based VADER. Nothing is trained. |
| Auth / security engineer for user accounts | No logins. User-typed reviews stay in the browser. Static-hosting security headers are handled by NET. |
| Separate data-viz designer | Covered by UX (design) and FE (implementation). |
