"""NLTK-only review analyzer shared by the build and the browser (Pyodide).

Owner: nltk-expert (logic) / pyodide-engineer (browser wiring).

This file must import nothing but NLTK and the standard library: the build copies it
verbatim to ``site/py/analyze_text.py`` and the Pyodide Web Worker runs it in the
visitor's browser. spaCy is NOT available there, so aspect detection here is
keyword-based (lexicon terms and phrases), while the build-time dashboard uses spaCy
dependency parses. The VADER setup (lexicon overrides and thresholds) is identical.

Works on Python 3.12 (Netlify build), 3.13 (local) and 3.14 (Pyodide 314.0.8).
"""
from __future__ import annotations

import re

from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize, word_tokenize

_WORD_RE = re.compile(r"^[a-z][a-z'\-]*$")


def make_analyzer(lexicon: dict) -> SentimentIntensityAnalyzer:
    """VADER with the project's sci-fi overrides applied (same list in build and browser)."""
    sia = SentimentIntensityAnalyzer()
    for word, valence in lexicon["vader_overrides"].items():
        sia.lexicon[word] = float(valence)
    return sia


def label(compound: float, lexicon: dict) -> str:
    """VADER authors' convention: >= 0.05 positive, <= -0.05 negative, else neutral."""
    th = lexicon["thresholds"]
    if compound >= th["positive"]:
        return "positive"
    if compound <= th["negative"]:
        return "negative"
    return "neutral"


def tokens(text: str) -> list[str]:
    """Lowercased NLTK Treebank word tokens (keeps negators such as "n't")."""
    return [t.lower() for t in word_tokenize(text)]


def content_words(toks: list[str], lexicon: dict) -> list[str]:
    """Alphabetic tokens minus NLTK English stopwords and the domain stopword list.

    For frequency charts only. Never use this to filter text sent to VADER.
    """
    stop = set(stopwords.words("english")) | set(lexicon["domain_stopwords"]) | set(lexicon["negators"])
    return [t for t in toks if _WORD_RE.match(t) and "'" not in t and t not in stop and len(t) > 2]


def keyword_aspects(toks: list[str], lexicon: dict) -> list[dict]:
    """Find aspect triggers in a token list: phrases first, then single words.

    Returns [{"aspect", "term", "index"}]. Ambiguous "theme" follows lexicon["ambiguous"].
    """
    found: list[dict] = []
    used: set[int] = set()
    for aspect, phrases in lexicon["aspect_phrases"].items():
        for phrase in phrases:
            parts = phrase.split()  # word_tokenize keeps "world-building" as one token
            n = len(parts)
            for i in range(len(toks) - n + 1):
                if toks[i:i + n] == parts and not used.intersection(range(i, i + n)):
                    found.append({"aspect": aspect, "term": phrase, "index": i})
                    used.update(range(i, i + n))
    index = {t: a for a, terms in lexicon["aspect_terms"].items() for t in terms}
    has = {index.get(t) for t in toks}
    for i, t in enumerate(toks):
        if i in used:
            continue
        # crude plural fold so "effects"/"characters" match like lemmas do at build time
        base = t if t in index else (t[:-1] if t.endswith("s") and t[:-1] in index else None)
        if base is None:
            continue
        aspect = index[base]
        rule = lexicon["ambiguous"].get(base)
        if rule:
            aspect = rule["then"] if rule["if_sentence_has"] in has else rule["default"]
        found.append({"aspect": aspect, "term": base, "index": i})
    found.sort(key=lambda f: f["index"])
    return found


def analyze(text: str, lexicon: dict, sia: SentimentIntensityAnalyzer | None = None) -> dict:
    """Analyze one critique with NLTK: sentences, VADER, keyword aspects, top words.

    Output (plain JSON types):
      {compound, label, scores{neg,neu,pos,compound}, n_sentences, n_tokens,
       sentences: [{text, compound, label, aspects: [aspect...] }],
       aspects: {aspect: {mentions, mean_compound, label, terms}},
       top_words: [[word, count], ...]}
    """
    sia = sia or make_analyzer(lexicon)
    text = (text or "").strip()
    scores = sia.polarity_scores(text)
    out_sentences = []
    per_aspect: dict[str, list[float]] = {a: [] for a in lexicon["aspects"]}
    terms: dict[str, list[str]] = {a: [] for a in lexicon["aspects"]}
    all_toks: list[str] = []
    for sent in sent_tokenize(text) if text else []:
        toks = tokens(sent)
        all_toks.extend(toks)
        c = round(sia.polarity_scores(sent)["compound"], 3)
        hits = keyword_aspects(toks, lexicon)
        aspects = sorted({h["aspect"] for h in hits})
        for h in hits:
            terms[h["aspect"]].append(h["term"])
        for a in aspects:
            per_aspect[a].append(c)
        out_sentences.append({"text": sent, "compound": c, "label": label(c, lexicon), "aspects": aspects})
    aspects_out = {}
    for a, vals in per_aspect.items():
        if vals:
            m = round(sum(vals) / len(vals), 3)
            aspects_out[a] = {"mentions": len(vals), "mean_compound": m, "label": label(m, lexicon),
                              "terms": sorted(set(terms[a]))}
    counts: dict[str, int] = {}
    for w in content_words(all_toks, lexicon):
        counts[w] = counts.get(w, 0) + 1
    top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    compound = round(scores["compound"], 3)
    return {
        "compound": compound,
        "label": label(compound, lexicon),
        "scores": {k: round(v, 3) for k, v in scores.items()},
        "n_sentences": len(out_sentences),
        "n_tokens": len(all_toks),
        "sentences": out_sentences,
        "aspects": aspects_out,
        "top_words": [[w, n] for w, n in top],
    }
