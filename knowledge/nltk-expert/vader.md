# VADER (`nltk.sentiment.vader`)

Sources:
- API: https://www.nltk.org/api/nltk.sentiment.vader.html
- How-to with reference outputs: https://www.nltk.org/howto/sentiment.html
- Original project (thresholds): https://github.com/cjhutto/vaderSentiment

## API
```python
from nltk.sentiment.vader import SentimentIntensityAnalyzer   # data: nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()   # lexicon_file='sentiment/vader_lexicon.zip/vader_lexicon/vader_lexicon.txt'
sia.polarity_scores(text)            # {'neg', 'neu', 'pos', 'compound'}
sia.lexicon                          # dict word -> valence; editable at runtime
```
- `normalize(score, alpha=15)` maps the summed valence into `compound` ∈ [-1, 1].
- Labelling convention (VADER authors): `compound >= 0.05` positive, `<= -0.05` negative, otherwise neutral.

## Constants (from the API page)
| Constant | Value | Meaning |
|---|---|---|
| `B_INCR` / `B_DECR` | 0.293 / -0.293 | booster words (very, extremely / slightly, barely) |
| `C_INCR` | 0.733 | ALL-CAPS emphasis increment |
| `N_SCALAR` | -0.74 | multiplier applied when a word is negated |
| `NEGATE` | {"not", "never", "nothing", "without", "despite", "rarely", "seldom", "isn't", "don't", "won't", …} | negation triggers |
| `BOOSTER_DICT` | absolutely, completely, extremely, incredibly, really, very = +0.293; barely, hardly, kinda, slightly, somewhat, sort-of = -0.293 | |
| `SPECIAL_CASE_IDIOMS` | badass 1.5, "cut the mustard" 2, "kiss of death" -1.5, "the bomb" 3, "yeah right" -2 | idioms |

## Reference outputs from the how-to (use as regression tests)
| Sentence | compound |
|---|---|
| The book was good. | 0.4404 |
| The book was kind of good. | 0.3832 |
| The plot was good, but the characters are uncompelling and the dialog is not great. | -0.7042 |
| At least it isn't a horrible book. | 0.431 |
| VERY BAD movie! | -0.7616 |
| The script is not fantastic, but the acting is decent and the cinematography is EXCELLENT! | 0.7565 |
| There are slow and repetitive parts, BUT it has just enough spice to keep it interesting. | 0.4678 |
| This movie was actually neither that funny, nor super witty. | -0.6759 |
| (empty string) | 0.0 |

These show: punctuation (`!`) and ALL CAPS raise intensity; "kind of" dampens; "but" shifts weight to the clause after it; negation flips ("isn't a horrible" → positive).

## Project rules
- Score per sentence for aspects; per review for the overall gauge.
- Neutralise sci-fi plot vocabulary before scoring (same list at build time and in Pyodide):
  `for w in ["alien","aliens","dark","war","invasion","kill","killer","destroy","apocalypse","dystopian","monster","horror"]: sia.lexicon[w] = 0.0`
- Record the NLTK version and override list in `site/data/eval.json` so results are reproducible.
