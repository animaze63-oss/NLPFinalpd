---
name: pandas-data-wrangling
description: "Load, join, filter and clean the Rotten Tomatoes CSVs with pandas. Use when reading the raw dataset, building the sci-fi subset, or aggregating reviews per film."
---

# pandas-data-wrangling

Used by: **dataset-curator** (owner), pipeline-engineer, nlp-evaluator

- Read big files with `usecols`, `dtype` and `chunksize`; filter each chunk to the selected `rotten_tomatoes_link`s.
- Join reviews → movies with `merge(..., on="rotten_tomatoes_link", how="inner", validate="m:1", indicator=True)` and report unmatched rows.
- Drop empty `review_content`; strip whitespace; de-duplicate on (link, critic_name, review_content).
- Never fill NaN with fake values; write `None` → JSON `null`.

Reference: `knowledge/dataset-curator/pandas.md`.
