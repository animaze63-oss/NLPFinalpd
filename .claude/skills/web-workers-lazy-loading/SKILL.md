---
name: web-workers-lazy-loading
description: "Run Pyodide in a module Web Worker and load it only when the user opens the analyzer. Use when wiring the analyzer panel or fixing UI jank."
---

# web-workers-lazy-loading

Used by: **pyodide-engineer** (owner), frontend-engineer

- `new Worker("/js/analyzer.worker.mjs", { type: "module" })` — classic workers with `importScripts()` are not supported by Pyodide.
- Create the worker on first open of the panel; reuse it afterwards.
- Message protocol with ids: `{id, type: "analyze", text}` → `{id, result}` / `{id, error}`; post progress messages (`loading-runtime`, `loading-nltk`, `ready`).
- Show progress in a `role="status"` region; the dashboard stays usable while loading.

Reference: `knowledge/pyodide-engineer/webworker.md`.
