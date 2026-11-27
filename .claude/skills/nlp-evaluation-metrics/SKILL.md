---
name: nlp-evaluation-metrics
description: "Measure NLP quality: VADER vs Fresh/Rotten labels and aspect extraction vs a hand-labelled sample. Use when reporting accuracy, comparing lexicon changes, or writing the methodology panel."
---

# nlp-evaluation-metrics

Used by: **nlp-evaluator** (owner), nltk-expert, spacy-expert, qa-engineer

- Metrics: accuracy, balanced accuracy (classes are imbalanced), macro-F1, confusion matrix (rows = true), per film and overall; Cohen's kappa for annotator agreement.
- Report the neutral band separately; include a threshold-0 two-class variant.
- Ablations: with/without sci-fi lexicon overrides.
- Output: `site/data/eval.json` + methodology text with versions and failure modes.

Reference: `knowledge/nlp-evaluator/sklearn-metrics.md`, `knowledge/nlp-evaluator/evaluation-plan.md`.
