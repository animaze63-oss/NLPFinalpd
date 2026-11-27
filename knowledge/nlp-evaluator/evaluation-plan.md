# Evaluation plan

1. **VADER vs `review_type`** (Fresh = positive, Rotten = negative), per review:
   - Map compound ≥ 0.05 → Fresh, ≤ -0.05 → Rotten; report the neutral band size separately, and a 2-class variant with threshold 0.
   - Metrics: accuracy, balanced accuracy, macro-F1, confusion matrix; overall and per film.
   - Ablation: with vs without the sci-fi lexicon overrides (show that neutralising *alien/war/dark…* helps or not).
2. **Aspect extraction quality**: hand-label 200 random sentences (aspect present? which? polarity?). Report precision/recall per aspect; Cohen's kappa if two annotators.
3. **Regression set**: VADER reference sentences from the NLTK how-to must reproduce exactly (see ../nltk-expert/vader.md).
4. **Parity**: browser analyzer vs build pipeline on 50 fixed sentences — same compound to 3 dp.
5. Write `site/data/eval.json` and the "Methodology" panel text: what was measured, numbers, known failure modes (irony, short blurbs, plot-description negativity), and versions.
