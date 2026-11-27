---
name: pyodide-runtime
description: "Load Pyodide and NLTK in the browser and run the review analyzer. Use when building or debugging the 'Analyze your own review' panel."
---

# pyodide-runtime

Used by: **pyodide-engineer** (owner), frontend-engineer, qa-engineer

- Pyodide 314.0.8, self-hosted under `site/pyodide/` (`loadPyodide({ indexURL: "/pyodide/" })`); CDN only as an approved fallback.
- `await pyodide.loadPackage("nltk")` (pulls `regex`); no micropip needed.
- Fetch `vader_lexicon.zip` into `pyodide.FS` at `/nltk_data/sentiment/`, then `nltk.data.path.insert(0, "/nltk_data")`.
- Run fixed code from `site/py/analyze.py`; pass user text as data; return JSON.
- spaCy is not available in Pyodide — don't try.

Reference: `knowledge/pyodide-engineer/` (all files).
