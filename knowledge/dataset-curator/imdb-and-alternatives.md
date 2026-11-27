# IMDb data and alternatives

## IMDb non-commercial datasets
Source: https://developer.imdb.com/non-commercial-datasets/
- "Subsets of IMDb data are available for access to customers for personal and non-commercial use. You can hold local copies of this data, and it is subject to our terms and conditions."
- Files at https://datasets.imdbws.com/ — gzipped TSV, UTF-8, header row.
- `title.basics.tsv.gz`: `tconst`, `titleType` (movie, short, tvseries…), `primaryTitle`, `originalTitle`, `isAdult`, `startYear`, `endYear`, `genres` ("up to three genres").
- Use: keep `titleType == "movie"` and `"Sci-Fi" in genres`; join to RT on normalised title + year to split sci-fi from fantasy. Use as a build-time filter only; don't republish the IMDb file.

## IMDb Large Movie Review Dataset (Maas et al., ACL 2011)
Source: https://ai.stanford.edu/~amaas/data/sentiment/
- 50,000 labelled reviews (25k train / 25k test) + 50,000 unlabelled; `aclImdb_v1.tar.gz` ~84 MB.
- Labelled only when strongly positive (≥ 7/10) or negative (≤ 4/10).
- Fields: `text`, `label` (0 negative, 1 positive) — **no title or genre**. Mirrors: Hugging Face `stanfordnlp/imdb`, TFDS `imdb_reviews`.
- Use: optional second benchmark for VADER (EVAL agent). Cite the ACL 2011 paper.
