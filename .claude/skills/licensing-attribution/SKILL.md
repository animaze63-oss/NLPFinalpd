---
name: licensing-attribution
description: "Apply dataset licences and credit critics correctly. Use when publishing data files, showing review quotes, or writing data/README.md."
---

# licensing-attribution

Used by: **dataset-curator** (owner), ux-designer, frontend-engineer, nlp-evaluator

- RT Kaggle dataset is declared CC0, but quotes belong to critics → always show `critic_name` and `publisher_name` with each excerpt; keep excerpts short (≤ 300 chars).
- IMDb non-commercial data: filter use only at build time; don't republish files.
- Cite datasets and libraries in the methodology panel and the report.

Reference: `knowledge/dataset-curator/licensing.md`.
