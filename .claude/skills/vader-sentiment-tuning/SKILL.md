---
name: vader-sentiment-tuning
description: "Score sentiment with NLTK VADER and tune its lexicon for sci-fi reviews. Use when computing review/sentence/aspect sentiment or changing thresholds or lexicon overrides."
---

# vader-sentiment-tuning

Used by: **nltk-expert** (owner), pyodide-engineer, nlp-evaluator

- `SentimentIntensityAnalyzer().polarity_scores(text)` → `neg, neu, pos, compound`; label: compound ≥ 0.05 positive, ≤ -0.05 negative, else neutral.
- Score per sentence for aspects; per review for the overall gauge.
- Neutralise plot vocabulary (alien, aliens, dark, war, invasion, kill, killer, destroy, apocalypse, dystopian, monster, horror) via `sia.lexicon[w] = 0.0`; keep the list in `site/data/lexicon.json` so the browser uses the same one.
- Keep the NLTK how-to reference sentences as regression tests.

Reference: `knowledge/nltk-expert/vader.md`.
