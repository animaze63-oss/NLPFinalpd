---
name: scifi-film-curation
description: "Choose which films count as science fiction and are rich enough to show. Use when building or changing the film list or the data/scifi_reviews.csv subset."
---

# scifi-film-curation

Used by: **dataset-curator** (owner), ux-designer, nlp-evaluator

- Start from RT `genres` containing "Science Fiction & Fantasy", then remove fantasy-only titles: curate by hand, or join IMDb `title.basics` (`titleType == "movie"`, `"Sci-Fi" in genres`) on normalised title + year.
- Keep films with ≥ 40 non-empty reviews.
- Aim for 30–60 films covering decades and sub-genres (space opera, cyberpunk, time travel, first contact, dystopia).
- Record the list, the rules and the counts in `data/README.md`.

References: `knowledge/dataset-curator/rotten-tomatoes-dataset.md`, `knowledge/dataset-curator/imdb-and-alternatives.md`.
