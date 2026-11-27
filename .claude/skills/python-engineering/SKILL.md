---
name: python-engineering
description: "Write clean, tested Python 3.12 for the build pipeline and the Pyodide analyzer. Use for any Python module, script or requirements.txt change."
---

# python-engineering

Used by: **pipeline-engineer** (owner), dataset-curator, nltk-expert, spacy-expert, pyodide-engineer, nlp-evaluator, qa-engineer, netlify-engineer

- Python 3.12 (`PYTHON_VERSION` in netlify.toml). Type hints, small pure functions, `pathlib`, no global state except loaded models.
- Pin dependencies in `requirements.txt` (repo root). The spaCy model is a wheel URL there.
- Modules: `pipeline/nlp_nltk.py`, `pipeline/nlp_spacy.py`, `pipeline/aspects.py`, `pipeline/build_data.py`; tests in `tests/`.
- Code shared with the browser (`site/py/analyze.py`) must use only the standard library + NLTK.
- Log stage timings; exit non-zero on any validation failure.
