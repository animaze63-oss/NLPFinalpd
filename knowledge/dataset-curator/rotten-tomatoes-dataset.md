# Rotten Tomatoes movies and critic reviews (Kaggle)

Source: https://www.kaggle.com/datasets/stefanoleone992/rotten-tomatoes-movies-and-critic-reviews-dataset

Confirmed on the page: "17k+ movies and their related critic reviews scraped from Rotten Tomatoes"; files `rotten_tomatoes_movies.csv` and `rotten_tomatoes_critic_reviews.csv`; 2 files, 30 columns total; licence **CC0: Public Domain**; scraped **2020-10-31**.

Documented schema (verify against the downloaded header — it sums to 30):
- movies (22): `rotten_tomatoes_link`, `movie_title`, `movie_info`, `critics_consensus`, `content_rating`, `genres`, `directors`, `authors`, `actors`, `original_release_date`, `streaming_release_date`, `runtime`, `production_company`, `tomatometer_status`, `tomatometer_rating`, `tomatometer_count`, `audience_status`, `audience_rating`, `audience_count`, `tomatometer_top_critics_count`, `tomatometer_fresh_critics_count`, `tomatometer_rotten_critics_count`
- reviews (8): `rotten_tomatoes_link`, `critic_name`, `top_critic`, `publisher_name`, `review_type` (Fresh/Rotten), `review_score`, `review_date`, `review_content`

Gotchas:
- Genre value is the combined **"Science Fiction & Fantasy"** → needs curation or an IMDb join.
- `review_content` can be empty → drop. Reviews are 1–3 sentence blurbs.
- `review_score` is free-form ("3/5", "B+", "8/10") → don't use as a label; use `review_type`.
- Join key: `rotten_tomatoes_link` (validate `m:1` when merging reviews → movies).
