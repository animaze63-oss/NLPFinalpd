# 01 — What NLTK does best in Scifi Cinema Lens

**Role in the app:** NLTK handles the *counting and scoring* layer: tokenizing, removing stopwords, VADER sentiment, word frequencies and collocations. It is lightweight, rule- and lexicon-based, has no trained neural model to load, and its outputs are easy to explain on a dashboard.

Division of labour with spaCy: **NLTK scores and counts; spaCy finds structure** (entities, noun phrases, lemmas, grammatical links). See [02-spacy.md](02-spacy.md).

---

## 1. Tokenizing

| Function | Use in the app |
|---|---|
| `nltk.sent_tokenize(text)` | Split each review into sentences. Sentence-level sentiment is what lets us say *"the visuals were praised, the story was criticised"* inside one mixed review. |
| `nltk.word_tokenize(sent)` | Word tokens for frequency counts and collocations. Uses the Treebank tokenizer (splits `don't` → `do`, `n't`). |
| `nltk.tokenize.RegexpTokenizer(r"[A-Za-z']+")` | Simpler alternative when we only want alphabetic words for word clouds. |

**Data requirement:** `sent_tokenize`/`word_tokenize` need the Punkt model. In NLTK 3.9+ the resource is **`punkt_tab`** (older code used `punkt`). Download it explicitly: `nltk.download("punkt_tab")`.

## 2. Stopwords

- `from nltk.corpus import stopwords; stopwords.words("english")` — ~180 common words. Needs `nltk.download("stopwords")`.
- **Extend it with domain stopwords** or the frequency charts will be dominated by noise: `film, movie, films, movies, one, like, story*, sci, fi, scifi, science, fiction, director, character*`.
  - *Careful:* do **not** strip aspect words (`story`, `character`, `visuals`, `score`) from the text used for aspect detection — only from the "top words" chart.
- Keep negators (`not`, `no`, `never`, `n't`) **out** of the stopword list for any text fed to sentiment; VADER needs them.

## 3. VADER sentiment (the headline feature)

```python
from nltk.sentiment import SentimentIntensityAnalyzer   # nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()
sia.polarity_scores("The visuals are stunning but the plot is a mess.")
# -> {'neg': ..., 'neu': ..., 'pos': ..., 'compound': ...}
```

- **Output:** `neg`, `neu`, `pos` proportions plus `compound` in **[-1, 1]**. Conventional thresholds (from the VADER authors): `compound >= 0.05` positive, `<= -0.05` negative, else neutral.
- **Why it fits:** no training, fast (pure Python, a lexicon of ~7.5k entries), handles negation (`not good`), intensifiers (`very`, `extremely`), capitalisation and `but` contrast — which is common in critic prose ("gorgeous, *but* hollow").
- **Run it per sentence, not per review.** Review-level compound is useful for the overall gauge; sentence-level is required for aspect sentiment.
- **Known limits (document these in the app's "methodology" panel):**
  - Tuned on social media; critic writing is drier and ironic ("a triumph of style over substance" is negative but lexically mixed).
  - Domain words can mislead: *alien*, *dark*, *war*, *kill*, *destroy* carry negative lexicon weight but are neutral plot descriptions in sci-fi. **Mitigation:** override them in the lexicon:
    ```python
    for w in ["alien", "aliens", "dark", "war", "invasion", "kill", "killer", "destroy", "apocalypse", "dystopian", "monster", "horror"]:
        sia.lexicon[w] = 0.0
    ```
  - Validate against the dataset's own labels (Rotten Tomatoes `review_type` Fresh/Rotten, see [03-dataset.md](03-dataset.md)) and report accuracy in the docs/app — a good NLP-course talking point.

## 4. Frequency distributions

- `nltk.FreqDist(tokens).most_common(25)` → "most-used words" bar chart per film, and separately for positive vs. negative reviews (a "praise words vs. criticism words" split chart).
- `nltk.ConditionalFreqDist((label, w) for ...)` → frequency conditioned on sentiment label or aspect.
- Feed **spaCy lemmas** (not raw tokens) into `FreqDist` so `effects/effect`, `characters/character` merge — this is the clearest place where the two libraries are combined.

## 5. Collocations (n-grams that "belong together")

```python
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
finder = BigramCollocationFinder.from_words(tokens)
finder.apply_freq_filter(3)                 # ignore rare pairs
finder.apply_word_filter(lambda w: w in stop)
finder.nbest(BigramAssocMeasures.pmi, 20)              # or .likelihood_ratio
```

- Surfaces phrases such as *special effects, production design, practical effects, world building, slow burn, third act, sound design, hard sci fi, time travel*.
- **PMI** over-rewards rare pairs → always apply a frequency filter; **likelihood ratio** is more stable for small per-film corpora.
- Show collocations from positive vs. negative sentences side by side.

## 6. Other NLTK pieces worth knowing (optional)

| Tool | Possible use |
|---|---|
| `nltk.stem.WordNetLemmatizer` + `wordnet` corpus | Fallback lemmatizer / synonym expansion of aspect keyword lists (`wordnet.synsets("score")`). Prefer spaCy lemmas in the main pipeline. |
| `nltk.ngrams`, `nltk.bigrams` | Plain n-gram counts (no association scoring). |
| `nltk.Text(tokens).concordance("score")` | Keyword-in-context view: "show me every sentence mentioning the soundtrack". |
| `nltk.classify.NaiveBayesClassifier` | Optional baseline trained on Fresh/Rotten labels to compare with VADER (course-worthy). |

## 7. NLTK data packages to download (build time)

```bash
python -m nltk.downloader -d ./nltk_data punkt_tab stopwords vader_lexicon wordnet omw-1.4
export NLTK_DATA=./nltk_data
```

Per [nltk.org/data](https://www.nltk.org/data.html): data can be installed with the downloader (`-d` sets the directory; then set `NLTK_DATA`), or manually by unzipping packages from `https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/...` into the matching subfolder (`sentiment/`, `tokenizers/`, `corpora/`). The manual route is how to ship `vader_lexicon` to the browser if we use Pyodide (see [04-netlify-deployment.md](04-netlify-deployment.md)).

## Sources

- NLTK data installation: https://www.nltk.org/data.html
- NLTK in Pyodide's built-in package list (nltk 3.9.4): https://pyodide.org/en/stable/usage/packages-in-pyodide.html
- VADER paper: Hutto, C.J. & Gilbert, E. (2014). *VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text.* ICWSM. (Thresholds ±0.05 come from the VADER project README: https://github.com/cjhutto/vaderSentiment)
- NLTK API: https://www.nltk.org/api/nltk.html
