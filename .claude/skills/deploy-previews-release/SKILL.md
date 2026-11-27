---
name: deploy-previews-release
description: "Ship through Netlify Deploy Previews and promote to production. Use when a PR is ready for QA, when releasing, or when rolling back."
---

# deploy-previews-release

Used by: **netlify-engineer** (owner), qa-engineer, orchestrator

- Every PR builds `deploy-preview-<n>--<site>.netlify.app`; post the URL in the PR.
- QA runs Playwright + axe + Lighthouse against it; Orchestrator merges to `main` after sign-off.
- Production deploy = `main`. Roll back by publishing the previous deploy in the Netlify UI.
- Read the build log for pip/NLTK/spaCy timings and errors.

Reference: `knowledge/netlify-engineer/deploy-previews.md`.
