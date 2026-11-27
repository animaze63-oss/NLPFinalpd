---
name: git-github-workflow
description: "Branch, commit, push and open PRs for Scifi Cinema Lens. Use whenever an agent changes files in the repository."
---

# git-github-workflow

Used by: **orchestrator** (owner), meta-agent, ux-designer, dataset-curator, nltk-expert, spacy-expert, pipeline-engineer, frontend-engineer, pyodide-engineer, nlp-evaluator, qa-engineer, netlify-engineer

- Work on a feature branch; `main` is production (Netlify deploys it). Only the Orchestrator merges to `main`.
- Small commits with imperative messages: `pipeline: add aspect aggregation`.
- Never commit secrets (Kaggle tokens), `raw/` data, `nltk_data/` downloads, or `node_modules/`.
- Every PR gets a Netlify Deploy Preview; link it in the PR and wait for QA.
- Don't rewrite shared history; resolve conflicts by merging.
