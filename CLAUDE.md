# Scifi Cinema Lens — team guide for Claude

**Project:** NLP final project. A user picks a science-fiction film and explores what critics praise or criticise, especially its **visuals, story, characters and soundtrack**, in a cinematic dashboard. The app uses **both NLTK and spaCy** and is **deployed on Netlify**.

## Decision record (always applies)

1. Everything runs on Netlify. **No outside servers, APIs or databases.**
2. **Build time:** NLTK and spaCy process the committed sci-fi review subset (`data/scifi_reviews.csv`) during the Netlify build and write **static JSON** to `site/data/`.
3. **Runtime:** a static site (HTML/CSS/vanilla JS + self-hosted Chart.js) reads that JSON.
4. **"Analyze your own review":** NLTK VADER runs **in the visitor's browser with Pyodide** (module Web Worker). User text never leaves the device.
5. **spaCy never runs in the browser.** It isn't available in Pyodide.
6. **No Netlify Functions or Edge Functions** for NLP. They support only TypeScript/JavaScript/Go, and Edge Functions run on Deno.
7. Review quotes always show the critic and publication.

## The team (`.claude/agents/`)

| Agent | Name | Model | Owns |
|---|---|---|---|
| `orchestrator` | Nova Reyes, The Director | opus | Planning, delegation, hand-off review, merging to `main` |
| `meta-agent` | Echo Lindqvist, The Script Supervisor | opus | The agents, skills and knowledge themselves; retrospectives |
| `ux-designer` | Lumen Okafor, The Production Designer | sonnet | Cinematic design, tokens, WCAG 2.2 AA |
| `dataset-curator` | Archie Vault, The Archivist | sonnet | Rotten Tomatoes dataset, sci-fi film list, `data/` |
| `nltk-expert` | Nell Tokes, The Lexicographer | opus | Tokenizing, stopwords, VADER, FreqDist, collocations, NLTK data |
| `spacy-expert` | Sy Parsons, The Syntax Cartographer | opus | en_core_web_sm, NER/EntityRuler, noun chunks, lemmas, aspect↔opinion dependencies, displaCy |
| `pipeline-engineer` | Reel Martinez, The Editor | sonnet | `pipeline/build_data.py`, JSON contract and schemas, build speed |
| `frontend-engineer` | Pixel Andersen, The Cinematographer | sonnet | Static dashboard and charts in `site/` |
| `pyodide-engineer` | Wasm Kowalski, The Practical-Effects Technician | sonnet | In-browser NLTK analyzer (Pyodide 314.0.8) |
| `nlp-evaluator` | Dr. Imani Gauge, The Critic | opus | Metrics, `eval.json`, methodology text, final report |
| `qa-engineer` | Quinn Assure, The Stunt Coordinator | sonnet | pytest, Playwright, axe, Lighthouse on Deploy Previews |
| `netlify-engineer` | Dock Harbor, The Projectionist | haiku | `netlify.toml`, Python build setup, headers, releases |

Full roster and skills matrix: `docs/expert-roster.md`. Personalities and model reasoning: `docs/agent-brains.md`.

## How the team works

- **Start with the Orchestrator** for anything that spans more than one role. It delegates to the experts and chains them: contract → pipeline → frontend/Pyodide → QA → deploy.
- **Knowledge first:** every agent reads `knowledge/<agent-name>/README.md` and every file it lists before answering. The notes come from official docs (nltk.org, spacy.io, pyodide.org, docs.netlify.com, and others) and include source links. When you work in an agent's area yourself, read that folder too.
- **Skills:** 37 project skills in `.claude/skills/<skill>/SKILL.md`. Each agent preloads its own skills, and any session can invoke them with `/skill-name`.
- **Hand-offs:** every agent ends with a `DONE / CONTRACT / TESTS / OPEN / NEXT` block.
- **Data contract:** `site/data/*.json` shapes are defined in `knowledge/pipeline-engineer/data-contract.md` and `schemas/`. Only the pipeline engineer changes them, and the Orchestrator approves breaking changes.

## Repository map

```
.claude/agents/     12 subagents          .claude/skills/   37 skills
knowledge/<agent>/  reference notes        docs/             research, roster, brains
data/               committed sci-fi subset (planned)
pipeline/           build-time NLTK + spaCy code (planned)
schemas/            JSON Schemas for site/data (planned)
site/               static site published by Netlify (planned)
tests/, e2e/        pytest and Playwright (planned)
netlify.toml, requirements.txt (planned)
```

## Conventions

- Python 3.12; dependencies pinned in `requirements.txt` (spaCy model as a wheel URL).
- Never commit secrets (Kaggle tokens), `raw/` data, `nltk_data/` downloads or `node_modules/`.
- `main` is production on Netlify. Work on branches and verify every change on a Deploy Preview.
