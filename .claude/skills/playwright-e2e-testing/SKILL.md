---
name: playwright-e2e-testing
description: "Write Playwright end-to-end tests for the dashboard and the Pyodide analyzer, locally and on Deploy Previews. Use when UI flows change or before a release."
---

# playwright-e2e-testing

Used by: **qa-engineer** (owner), frontend-engineer, pyodide-engineer

- `webServer` serves `site/` locally; `BASE_URL` env var points tests at a Deploy Preview instead.
- Role-based locators; web-first assertions; no sleeps.
- Flows: pick film → dashboard; deep link; error state for a missing slug; analyzer lazy-loads and returns a score; 360 px width has no horizontal scroll.
- Run with `--trace off` unless debugging.

Reference: `knowledge/qa-engineer/playwright.md`.
