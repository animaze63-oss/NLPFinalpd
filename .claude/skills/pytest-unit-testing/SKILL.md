---
name: pytest-unit-testing
description: "Write and run pytest tests for the NLP modules, pipeline and JSON outputs. Use when adding or changing Python code."
---

# pytest-unit-testing

Used by: **qa-engineer** (owner), dataset-curator, nltk-expert, spacy-expert, pipeline-engineer

- `tests/conftest.py`: session-scoped fixtures for the spaCy model and VADER analyzer.
- Parametrize sentence-level cases (VADER reference outputs, each dependency rule, lexicon overrides).
- Pipeline test on a 50-review fixture using `tmp_path`; validate outputs with jsonschema; assert no NaN.
- Run: `pytest -q`; CI and the Orchestrator need green before merge.

Reference: `knowledge/qa-engineer/pytest.md`, `knowledge/qa-engineer/test-plan.md`.
