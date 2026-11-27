---
name: browser-build-parity
description: "Keep the in-browser Pyodide analyzer and the build-time pipeline consistent (same NLTK version behaviour, lexicon overrides, aspect lists, thresholds). Use whenever either side changes sentiment or aspect logic."
---

# browser-build-parity

Used by: **nltk-expert** (owner), pyodide-engineer, spacy-expert, qa-engineer

- Single source: `site/data/lexicon.json` (overrides, aspect triggers, thresholds) read by both sides.
- `site/py/analyze.py` (stdlib + NLTK only) is imported by the build tests too.
- Parity test: 50 fixed sentences, compound equal to 3 decimal places; aspect labels equal where keyword rules apply.
- The browser can't run spaCy, so its aspect detection is keyword-based — the UI must say so.
- Note: build uses PyPI NLTK; Pyodide 314.0.8 ships nltk 3.9.4 — pin the build to the same version.
