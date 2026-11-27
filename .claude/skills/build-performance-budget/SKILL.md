---
name: build-performance-budget
description: "Keep the Netlify build (pip install + NLP + JSON writing) fast and inside the build time limit. Use when the build gets slower, the corpus grows, or dependencies change."
---

# build-performance-budget

Used by: **pipeline-engineer** (owner), spacy-expert, netlify-engineer

- Target: whole Netlify build < 5 minutes (limit is commonly 15 — confirm on the plan).
- Measure stage timings and write them to `eval.json` → `build_stats`.
- Levers: smaller curated corpus, `nlp.pipe` batching, avoid re-tokenising, cache nothing that changes output silently.
- Fallback: committed JSON + `SKIP_NLP=1` publishes without re-running the NLP.

Reference: `knowledge/pipeline-engineer/build-budget.md`.
