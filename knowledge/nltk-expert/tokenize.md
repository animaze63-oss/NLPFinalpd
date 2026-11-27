# NLTK tokenizers

Source: https://www.nltk.org/api/nltk.tokenize.html

## `sent_tokenize(text, language='english')`
> "Return a sentence-tokenized copy of text, using NLTK's recommended sentence tokenizer (currently `PunktSentenceTokenizer` for the specified language)."

## `word_tokenize(text, language='english', preserve_line=False)`
> "Return a tokenized copy of text, using NLTK's recommended word tokenizer (currently an improved `TreebankWordTokenizer` along with `PunktSentenceTokenizer` for the specified language)."

- `preserve_line=True` skips the sentence-splitting step (use it when the input is already one sentence, e.g. a sentence from spaCy).
- Treebank conventions: contractions split (`don't` → `do`, `n't`), punctuation becomes separate tokens.

## Required data
Both functions need the Punkt model. NLTK 3.9+ loads it from the **`punkt_tab`** resource (older releases used the pickled `punkt`). Missing data raises `LookupError` naming the resource.

```python
import nltk
nltk.download("punkt_tab")
from nltk.tokenize import sent_tokenize, word_tokenize
sents = sent_tokenize("Stunning visuals. The plot, however, drags.")
toks  = word_tokenize(sents[1], preserve_line=True)
```

## Other tokenizers in `nltk.tokenize` (submodules)
- `RegexpTokenizer(pattern)` (`nltk.tokenize.regexp`) — e.g. `RegexpTokenizer(r"[A-Za-z']+")` for word-cloud tokens.
- `TreebankWordTokenizer` (`nltk.tokenize.treebank`).
- `TweetTokenizer` (`nltk.tokenize.casual`) — keeps emoticons/hashtags; useful for user-typed text in the Pyodide panel.
- `wordpunct_tokenize` — splits on `\w+|[^\w\s]+`.

## Project rules
- In the build pipeline, spaCy splits sentences; NLTK tokenizes for counts and scores. Do not mix two sentence splitters for the same statistic.
- In Pyodide (no spaCy), use `sent_tokenize` — ship `punkt_tab` as a static file or fall back to a regex splitter.
