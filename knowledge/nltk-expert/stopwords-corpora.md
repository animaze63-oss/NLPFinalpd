# Stopwords and corpora

Source: https://www.nltk.org/howto/corpus.html (stopwords section) and https://www.nltk.org/data.html

```python
>>> from nltk.corpus import stopwords
>>> stopwords.fileids()
['arabic', 'azerbaijani', 'bengali', 'danish', 'dutch', 'english', 'finnish', 'french', ...]
>>> sorted(stopwords.words('portuguese'))
['a', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', ...]
```

- Data package: `stopwords` (`nltk.download("stopwords")`), stored under `nltk_data/corpora/stopwords/`.
- `stopwords.words("english")` returns a list — convert to a `set` for lookups.
- Corpus readers load lazily: the first access raises `LookupError` if the package is missing.

## Project rules (from docs/01-nltk.md)
- Domain stopwords for the "top words" chart: film, films, movie, movies, one, like, sci, fi, scifi, science, fiction.
- Never remove negators (`not`, `no`, `never`, `n't`, `nor`) from text sent to VADER — English stopwords include them.
- Never remove aspect triggers (story, character, visuals, score) from text used for aspect detection.
