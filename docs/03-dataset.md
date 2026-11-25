# 03 — Review dataset

We need: **written review text**, a **movie title** per review (so the user can pick a film), and a **genre** field (to keep only science fiction). Ideally a **label** (positive/negative) so we can measure how well VADER works.

## Recommendation: Rotten Tomatoes movies and critic reviews (Kaggle, CC0)

| | |
|---|---|
| URL | https://www.kaggle.com/datasets/stefanoleone992/rotten-tomatoes-movies-and-critic-reviews-dataset |
| Author | Stefano Leone |
| License (as declared on Kaggle) | **CC0: Public Domain** |
| Scraped | 2020-10-31 |
| Size | "17k+ movies and their related critic reviews"; 2 files, 30 columns total |
| Files | `rotten_tomatoes_movies.csv`, `rotten_tomatoes_critic_reviews.csv` |
| Download | Requires a free Kaggle account (web download or `kaggle datasets download -d stefanoleone992/rotten-tomatoes-movies-and-critic-reviews-dataset` with an API token) |

### Columns (verify after download — the Kaggle page confirmed the two file names, the 30-column total and the license; the list below is from the dataset's documented schema and adds up to 30)

`rotten_tomatoes_movies.csv` (22): `rotten_tomatoes_link` (join key), `movie_title`, `movie_info`, `critics_consensus`, `content_rating`, **`genres`**, `directors`, `authors`, `actors`, `original_release_date`, `streaming_release_date`, `runtime`, `production_company`, `tomatometer_status`, `tomatometer_rating`, `tomatometer_count`, `audience_status`, `audience_rating`, `audience_count`, `tomatometer_top_critics_count`, `tomatometer_fresh_critics_count`, `tomatometer_rotten_critics_count`.

`rotten_tomatoes_critic_reviews.csv` (8): `rotten_tomatoes_link` (join key), `critic_name`, `top_critic`, `publisher_name`, **`review_type`** (Fresh/Rotten), `review_score`, `review_date`, **`review_content`**.

### Why it fits

- **Has titles and genres** → a film picker and a sci-fi filter.
- **Has `review_type` Fresh/Rotten** → ground truth to evaluate VADER (accuracy / confusion matrix in the methodology panel).
- **Critic prose** naturally discusses visuals, story, performances and score.
- `directors` / `actors` columns seed the spaCy `EntityRuler` (see [02-spacy.md](02-spacy.md)).
- `critics_consensus` gives a one-line human summary per film to show next to our NLP summary.

### Caveats agents must handle

1. **Genre is combined:** Rotten Tomatoes uses **"Science Fiction & Fantasy"**, so the filter also returns fantasy films. Options (pick one):
   - Curate a list of ~30–60 clearly sci-fi films (simplest, best demo quality).
   - Join to **IMDb non-commercial `title.basics.tsv.gz`** (`genres` includes `Sci-Fi`) on normalised title + release year. IMDb data is for "personal and non-commercial use" (https://developer.imdb.com/non-commercial-datasets/) — fine for a class project, but only use it as a filter at build time; don't republish the IMDb file.
2. **Reviews are short** "blurbs" (1–3 sentences), and some rows have empty `review_content` → drop nulls. Short text is fine for sentence-level VADER and dependency parsing.
3. **Size:** the reviews file is large (on the order of 1M rows / ~200 MB). **Do not commit it.** Filter locally to the chosen sci-fi films and commit only the subset (target < 5 MB, e.g. `data/scifi_reviews.csv`). Also keep films with ≥ 40 reviews so per-film charts aren't empty.
4. **Copyright of the text:** the dataset is labelled CC0 by the uploader, but review excerpts are written by critics/publishers. For an educational project, show short excerpts with critic and publication attribution (`critic_name`, `publisher_name`) and link to Rotten Tomatoes; don't present them as our own.
5. Data stops at Oct 2020 → newer films (e.g. *Dune: Part Two*) aren't included.

## Alternatives considered

| Dataset | Pros | Cons for this app |
|---|---|---|
| **IMDb Large Movie Review Dataset** (Maas et al., ACL 2011) — https://ai.stanford.edu/~amaas/data/sentiment/ — 50k labelled + 50k unlabelled reviews, ~84 MB tar.gz; also `stanfordnlp/imdb` on Hugging Face | Long, rich full-length reviews; classic NLP benchmark; positive/negative labels | Fields are only `text` + `label` — **no title or genre**. The archive's URL lists map reviews to IMDb title pages, so you'd need to join with IMDb `title.basics` to get titles/genres. Max ~30 reviews per film → thin per-film dashboards. Good as a secondary corpus for validating VADER. |
| **IMDb non-commercial datasets** — https://datasets.imdbws.com/ | Clean `genres` (`Sci-Fi`), titles, years, ratings | **No review text.** Use only as a genre/metadata join table. Personal/non-commercial use. |
| **TMDB API** `/movie/{id}/reviews`, `/discover/movie?with_genres=878` (878 = Science Fiction) | Live, current films, true sci-fi genre id | Needs an API key; few user reviews per film; terms require attribution and limit redistribution. Fine as a stretch goal at build time, not as the core dataset. (Not re-verified in this research.) |
| Hugging Face `rotten_tomatoes` (Pang & Lee) | Easy `load_dataset` | Sentence snippets with labels only — no titles. |

## Suggested preprocessing script outline (for the data agent)

```python
movies  = pd.read_csv("rotten_tomatoes_movies.csv")
reviews = pd.read_csv("rotten_tomatoes_critic_reviews.csv")
scifi   = movies[movies.genres.str.contains("Science Fiction", na=False)]
scifi   = scifi[scifi.movie_title.isin(CURATED_SCIFI_TITLES)]          # or IMDb join
df      = reviews.merge(scifi[["rotten_tomatoes_link","movie_title","original_release_date",
                                "directors","actors","critics_consensus","tomatometer_rating"]],
                        on="rotten_tomatoes_link")
df      = df.dropna(subset=["review_content"])
df      = df.groupby("rotten_tomatoes_link").filter(lambda g: len(g) >= 40)
df.to_csv("data/scifi_reviews.csv", index=False)
```

## Sources

- Kaggle dataset page (files, CC0, scrape date, 17k+ movies): https://www.kaggle.com/datasets/stefanoleone992/rotten-tomatoes-movies-and-critic-reviews-dataset
- IMDb Large Movie Review Dataset: https://ai.stanford.edu/~amaas/data/sentiment/
- IMDb non-commercial datasets (title.basics fields, license): https://developer.imdb.com/non-commercial-datasets/
