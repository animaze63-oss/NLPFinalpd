"""Build the committed sci-fi sample from the raw Rotten Tomatoes Kaggle files.

Owner: dataset-curator. Run locally only (NOT during the Netlify build):

    python data/make_subset.py --raw raw/

Inputs (not committed, see data/README.md for provenance):
    raw/rotten_tomatoes_movies.csv, raw/rotten_tomatoes_critic_reviews.csv
Outputs (committed):
    data/scifi_films.csv   one row per curated film (metadata used by the pipeline + EntityRuler)
    data/scifi_reviews.csv sampled critic reviews (verbatim text, critic + publisher kept)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

# Curated list: clearly science fiction (not fantasy), >= 40 non-empty reviews, a spread of
# Tomatometer scores so the Fresh/Rotten evaluation sees both classes. Keyed by the
# Rotten Tomatoes link because titles are not unique (e.g. two "Ghost in the Shell" films).
CURATED_LINKS = [
    "m/alien",
    "m/matrix",
    "m/blade_runner_2049",
    "m/arrival_2016",
    "m/ex_machina",
    "m/mad_max_fury_road",
    "m/interstellar_2014",
    "m/the_martian",
    "m/annihilation",
    "m/elysium_2013",
    "m/oblivion_2013",
    "m/ghost_in_the_shell_2017",
    "m/valerian_and_the_city_of_a_thousand_planets",
    "m/passengers_2016",
]
REVIEWS_PER_FILM = 80
MIN_CHARS = 40
SEED = 42

FILM_COLS = [
    "rotten_tomatoes_link", "movie_title", "original_release_date", "directors", "authors",
    "actors", "production_company", "genres", "tomatometer_rating", "tomatometer_count",
    "critics_consensus",
]
REVIEW_COLS = [
    "rotten_tomatoes_link", "critic_name", "top_critic", "publisher_name", "review_type",
    "review_score", "review_date", "review_content",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="raw", type=Path)
    ap.add_argument("--out", default=Path(__file__).resolve().parent, type=Path)
    args = ap.parse_args()

    movies = pd.read_csv(args.raw / "rotten_tomatoes_movies.csv")
    reviews = pd.read_csv(args.raw / "rotten_tomatoes_critic_reviews.csv")
    print(f"raw: {len(movies)} movies, {len(reviews)} reviews")

    films = movies[movies.rotten_tomatoes_link.isin(CURATED_LINKS)][FILM_COLS].copy()
    assert len(films) == len(CURATED_LINKS), "a curated link is missing from the raw file"
    assert films.genres.str.contains("Science Fiction").all()
    # Keep the first 10 billed actors: enough to seed the EntityRuler, keeps the file small.
    films["actors"] = films.actors.fillna("").map(lambda s: ", ".join(s.split(", ")[:10]))

    r = reviews[reviews.rotten_tomatoes_link.isin(CURATED_LINKS)][REVIEW_COLS].copy()
    r = r.dropna(subset=["review_content", "critic_name", "publisher_name", "review_type"])
    r["review_content"] = r.review_content.str.strip()
    r = r[r.review_content.str.len() >= MIN_CHARS]
    r = r.drop_duplicates(subset=["rotten_tomatoes_link", "review_content"])
    assert r.groupby("rotten_tomatoes_link").size().min() >= REVIEWS_PER_FILM
    sample = (
        r.groupby("rotten_tomatoes_link")
        .sample(n=REVIEWS_PER_FILM, random_state=SEED)
        .sort_values(["rotten_tomatoes_link", "review_date", "critic_name"])
    )
    films = films.sort_values("original_release_date")
    films.to_csv(args.out / "scifi_films.csv", index=False)
    sample.to_csv(args.out / "scifi_reviews.csv", index=False)
    print(f"sample: {len(films)} films, {len(sample)} reviews")
    print(sample.groupby("rotten_tomatoes_link").review_type.value_counts().unstack().to_string())


if __name__ == "__main__":
    main()
