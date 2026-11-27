---
name: constraint-guarding
description: "Check designs, PRs and plans against the Netlify-only decision record (no outside servers, Python only at build time, NLTK in the browser via Pyodide, spaCy build-time only). Use before approving any architecture or dependency change."
---

# constraint-guarding

Used by: **orchestrator** (owner), meta-agent, netlify-engineer, qa-engineer

Reject and name the broken rule if a change:
- adds a server, external API, database or third-party runtime service (including a runtime CDN that isn't approved);
- adds `netlify/functions/` or `netlify/edge-functions/` for NLP, or any Python that runs after deploy;
- tries to load spaCy in the browser;
- sends user-typed review text off the device;
- shows review excerpts without critic and publisher attribution.

Allowed: Python in the Netlify build, static files, Pyodide + NLTK in a Web Worker, self-hosted vendor JS.

Source of truth: `knowledge/orchestrator/decision-record.md`, `docs/04-netlify-deployment.md`.
