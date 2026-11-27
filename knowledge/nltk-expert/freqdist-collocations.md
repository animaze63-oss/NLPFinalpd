# FreqDist and collocations

Sources:
- https://www.nltk.org/api/nltk.probability.FreqDist.html
- https://www.nltk.org/howto/collocations.html

## FreqDist (`nltk.probability.FreqDist`, subclass of `collections.Counter`)
```python
fdist = FreqDist(word.lower() for word in word_tokenize(sent))
fdist.most_common(25)   # [(sample, count), ...] most → least common
fdist.N()      # total number of sample outcomes recorded
fdist.B()      # number of bins with count > 0
fdist.freq(w)  # count(w) / N()
fdist.hapaxes()# samples that occur once
fdist.update(more)   # overrides Counter.update to invalidate the cached N
fdist.r_Nr()   # {r: Nr} number of samples with frequency r
fdist.tabulate(10); fdist.plot(10)   # plot needs matplotlib — never in the build
```
`ConditionalFreqDist((label, word) for ...)` gives one FreqDist per condition (e.g. positive vs negative sentences).

## Collocations (`nltk.collocations`)
```python
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
bigram_measures = BigramAssocMeasures()
finder = BigramCollocationFinder.from_words(tokens)            # window_size=2 default
finder = BigramCollocationFinder.from_words(tokens, window_size=5)   # allow intervening words
finder.apply_freq_filter(3)                                    # drop n-grams seen < 3 times
finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in ignored_words)
finder.apply_ngram_filter(lambda w1, w2, w3: 'and' in (w1, w3))      # trigram finder
finder.nbest(bigram_measures.pmi, 10)
finder.score_ngrams(bigram_measures.raw_freq)                  # [(ngram, score), ...]
```
Measures: `pmi`, `likelihood_ratio`, `chi_sq`, `student_t`, `raw_freq`.

Caveat from the how-to: n-grams can be "highly collocated while also being very infrequent", so apply frequency filters — "lack of sufficient evidence about their significance".

## Project rules
- Feed spaCy lemmas (alpha, non-stop) into FreqDist/finders so inflections merge.
- Per film: `apply_freq_filter(3)`, rank with `likelihood_ratio` (stable on small corpora); report PMI only with the filter.
- Compute separately for positive and negative sentences (VADER label) → "praise vs criticism" phrases.
