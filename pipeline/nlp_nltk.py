"""Build-time NLTK layer: tokenizing, stopwords, VADER, FreqDist and collocations.

Owner: nltk-expert. Everything here is NLTK; spaCy output is never an input, so the
dashboard can label these panels "NLTK" honestly.

Sources: https://www.nltk.org/api/nltk.tokenize.html, https://www.nltk.org/howto/sentiment.html,
https://www.nltk.org/howto/collocations.html, https://www.nltk.org/data.html
"""
from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path

import nltk
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.corpus import stopwords
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from nltk.probability import FreqDist
from nltk.tokenize import sent_tokenize

from analyze_text import content_words, label, make_analyzer, tokens  # noqa: F401  (re-export)

REQUIRED = {
    "punkt_tab": "tokenizers/punkt_tab",
    "stopwords": "corpora/stopwords",
    "vader_lexicon": "sentiment/vader_lexicon.zip",
}


def ensure_data(data_dir: str | os.PathLike | None = None) -> Path:
    """Make sure punkt_tab, stopwords and vader_lexicon are available; download if missing.

    The Netlify build downloads them first with ``python -m nltk.downloader -d ./nltk_data``;
    this is a safety net for local runs and tests.
    """
    d = Path(data_dir or os.environ.get("NLTK_DATA") or Path(__file__).resolve().parents[1] / "nltk_data")
    d.mkdir(parents=True, exist_ok=True)
    if str(d) not in nltk.data.path:
        nltk.data.path.insert(0, str(d))
    for pkg, resource in REQUIRED.items():
        try:
            nltk.data.find(resource)
        except LookupError:
            nltk.download(pkg, download_dir=str(d), quiet=True)
    return d


def sentences(text: str) -> list[str]:
    """NLTK Punkt sentence split (punkt_tab)."""
    return sent_tokenize(text)


def score_sentences(texts: Iterable[str], sia) -> list[float]:
    return [round(sia.polarity_scores(t)["compound"], 3) for t in texts]


def top_words(token_lists: Iterable[list[str]], lexicon: dict, n: int = 15) -> list[list]:
    """FreqDist of content words (NLTK stopwords + domain stopwords removed)."""
    fd = FreqDist()
    for toks in token_lists:
        fd.update(content_words(toks, lexicon))
    return [[w, c] for w, c in sorted(fd.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]


def _phrase_tokens(token_lists: Iterable[list[str]]) -> list[str]:
    """Alphabetic tokens joined across sentences with a boundary marker so n-grams don't
    span sentences."""
    words: list[str] = []
    for toks in token_lists:
        words.extend(t for t in toks if t.isalpha() or "-" in t)
        words.append("<s>")
    return words


def collocations(token_lists: list[list[str]], lexicon: dict, n: int = 10, min_freq: int = 2) -> list[dict]:
    """Key phrases: bigram + trigram collocations ranked by likelihood ratio.

    Frequency filter first (PMI/LR over-reward rare pairs on small corpora), then drop
    n-grams that start/end with a stopword or contain the sentence marker.
    """
    stop = set(stopwords.words("english")) | set(lexicon["domain_stopwords"])
    words = _phrase_tokens(token_lists)

    def bad(w: str) -> bool:
        return w == "<s>" or w in stop or len(w) < 3

    out: dict[str, dict] = {}
    bf = BigramCollocationFinder.from_words(words)
    bf.apply_freq_filter(min_freq)
    bf.apply_ngram_filter(lambda a, b: bad(a) or bad(b))
    for (a, b), s in bf.score_ngrams(BigramAssocMeasures.likelihood_ratio)[: n * 2]:
        out[f"{a} {b}"] = {"phrase": f"{a} {b}", "count": bf.ngram_fd[(a, b)], "score": round(s, 3)}
    tf = TrigramCollocationFinder.from_words(words)
    tf.apply_freq_filter(min_freq)
    tf.apply_ngram_filter(lambda a, b, c: bad(a) or bad(c) or b == "<s>")
    for (a, b, c), s in tf.score_ngrams(TrigramAssocMeasures.likelihood_ratio)[:n]:
        out[f"{a} {b} {c}"] = {"phrase": f"{a} {b} {c}", "count": tf.ngram_fd[(a, b, c)], "score": round(s, 3)}
    ranked = sorted(out.values(), key=lambda d: (-d["count"], -d["score"], d["phrase"]))
    return ranked[:n]
