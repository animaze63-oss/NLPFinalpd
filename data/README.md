# data/ — the committed sci-fi review sample

Owner: dataset-curator. These files are the only data the Netlify build reads.

| File | What it is | Size |
|---|---|---|
| `scifi_reviews.csv` | 1,120 critic reviews (80 per film), verbatim, with critic and publication | ~240 KB |
| `scifi_films.csv` | 14 curated films: title, release date, directors, writers, first 10 billed actors, studio, genres, Tomatometer, critics consensus | ~7 KB |
| `aspect_gold.json` | 61 review sentences hand-labelled with aspects, used by the evaluator | ~10 KB |
| `make_subset.py` | Script that builds the two CSVs from the raw files (run locally, not on Netlify) | |

## Source and licence

- **Dataset:** *Rotten Tomatoes movies and critic reviews dataset* by Stefano Leone, Kaggle:
  https://www.kaggle.com/datasets/stefanoleone992/rotten-tomatoes-movies-and-critic-reviews-dataset
  The licence declared on Kaggle is **CC0: Public Domain**. The data was scraped on 2020-10-31.
- **Review text** was written by the credited critics and publications. The app shows short excerpts only, always with
  `critic_name` and `publisher_name`, and links to Rotten Tomatoes. We never present excerpts as our own writing, and no review
  text was invented or paraphrased.

## How the raw files were obtained (provenance)

Kaggle needs a login and was not reachable from the build environment. The same two Kaggle files are mirrored in public
GitHub repositories as Git LFS objects. We downloaded them on **2026-11-28** from:

- Mirror: https://github.com/Telmo465/FEUP-PRI, commit `1306d9cbe7e5c83ea7661e5c26fc58c5be99d33c`, folder `M1/datasets/`.
  We used the LFS media URLs `https://media.githubusercontent.com/media/Telmo465/FEUP-PRI/1306d9cbe7e5c83ea7661e5c26fc58c5be99d33c/M1/datasets/<file>`.
- Checksums of the downloaded files. Each matches the LFS pointer `oid`:
  - `rotten_tomatoes_movies.csv`: sha256 `c21dbd4849691e9b938a1bba362e374bb1aa82d5178ce7b8e06a17c14c3e9251`, 17,115,750 bytes
  - `rotten_tomatoes_critic_reviews.csv`: sha256 `ceaf1851d3948ca24b7a124ac3e15dbf0436666ec8673c25dd3f2ee0a5580c1f`, 226,049,903 bytes
- Cross-check: independent mirrors point to the same LFS objects (same sha256 oids):
  - jenny4567/intro-to-data-analysis @ `d6ae394eb7b55f1d1cc48086e8d42cf3909baea4`, `data/extra-challenge/rotten-tomatoes/` (both files)
  - XNTOL/Movie-Sentiment-Analysis @ `06b0e3db4ee021f13c27eccb45c34fc410596933`, `data/raw/` (reviews file checked)
- The headers match the documented Kaggle schema exactly: 22 movie columns and 8 review columns (30 in total).
  Raw size: 17,712 movies and 1,130,017 reviews.

The raw files stay in `raw/`, which is git-ignored. They are never committed.

## Filters (see `make_subset.py`)

1. **Curated sci-fi list** of 14 films, keyed by `rotten_tomatoes_link` because titles are not unique (there are two
   *Ghost in the Shell* films). Every film's `genres` contains "Science Fiction & Fantasy". The list was chosen to be clearly
   science fiction, not fantasy, and to spread Tomatometer scores from 31 to 98, so the Fresh/Rotten evaluation sees both classes.
2. Drop reviews with no `review_content`, `critic_name`, `publisher_name` or `review_type`, blurbs shorter than 40 characters,
   and duplicate texts within a film.
3. Random sample of **80 reviews per film** (`random_state=42`), so the result is reproducible.
4. The CSV text is kept verbatim. The build pipeline strips Rotten Tomatoes' "[Full review in Spanish]" notes before NLP and
   display, because they are site metadata, not the critic's words.

## Resulting sample

| Film | Year | Director(s) | Tomatometer | RT link | Reviews | Fresh |
|---|---|---|---|---|---|---|
| Alien | 1979 | Ridley Scott | 98 | m/alien | 80 | 78 |
| The Matrix | 1999 | Lilly Wachowski, Lana Wachowski | 88 | m/matrix | 80 | 69 |
| Oblivion | 2013 | Joseph Kosinski | 53 | m/oblivion_2013 | 80 | 41 |
| Elysium | 2013 | Neill Blomkamp | 65 | m/elysium_2013 | 80 | 54 |
| Interstellar | 2014 | Christopher Nolan | 72 | m/interstellar_2014 | 80 | 56 |
| Ex Machina | 2015 | Alex Garland | 92 | m/ex_machina | 80 | 77 |
| Mad Max: Fury Road | 2015 | George Miller | 97 | m/mad_max_fury_road | 80 | 74 |
| The Martian | 2015 | Ridley Scott | 91 | m/the_martian | 80 | 70 |
| Arrival | 2016 | Denis Villeneuve | 94 | m/arrival_2016 | 80 | 77 |
| Passengers | 2016 | Morten Tyldum | 31 | m/passengers_2016 | 80 | 20 |
| Ghost in the Shell | 2017 | Rupert Sanders | 43 | m/ghost_in_the_shell_2017 | 80 | 31 |
| Valerian and the City of a Thousand Planets | 2017 | Luc Besson | 48 | m/valerian_and_the_city_of_a_thousand_planets | 80 | 37 |
| Blade Runner 2049 | 2017 | Denis Villeneuve | 88 | m/blade_runner_2049 | 80 | 68 |
| Annihilation | 2018 | Alex Garland | 88 | m/annihilation | 80 | 66 |

Totals: 1,120 reviews, of which 818 are Fresh and 302 Rotten. 205 are by Top Critics. Review dates run from 1979-01-01 to
2020-10-21. Note: Rotten Tomatoes stores some old reviews with a placeholder date, such as `2000-01-01`.

## Regenerate

```bash
python data/make_subset.py --raw raw/
```

## Aspect gold set (`aspect_gold.json`)

The gold set has 61 sentences from this sample, split by NLTK `sent_tokenize`:

- 50 were drawn at random (seed 7).
- 12 were drawn from sentences matching sound or music words (seed 11), so the soundtrack aspect has some support.
- Duplicates were removed.

The labelling rule is recorded in the file. There was a single annotator (the project's nlp-evaluator agent), and the set was
not double-coded, so treat the precision and recall numbers on the methodology page as indicative.
