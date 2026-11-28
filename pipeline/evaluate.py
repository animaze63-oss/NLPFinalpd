"""Evaluation: VADER vs Rotten Tomatoes Fresh/Rotten, ablation, regression, aspect gold set.

Owner: nlp-evaluator. Called from build_data.py; writes the dict that becomes
site/data/eval.json. No scikit-learn dependency: the metrics are computed directly
(definitions as in https://scikit-learn.org/stable/modules/model_evaluation.html).
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import nlp_spacy
from analyze_text import keyword_aspects, tokens

GOLD = Path(__file__).resolve().parents[1] / "data" / "aspect_gold.json"

# Reference outputs from https://www.nltk.org/howto/sentiment.html (stock VADER lexicon).
REGRESSION = [
    ("The book was good.", 0.4404),
    ("The book was kind of good.", 0.3832),
    ("The plot was good, but the characters are uncompelling and the dialog is not great.", -0.7042),
    ("At least it isn't a horrible book.", 0.431),
    ("VERY BAD movie!", -0.7616),
    ("The script is not fantastic, but the acting is decent and the cinematography is EXCELLENT!", 0.7565),
    ("There are slow and repetitive parts, BUT it has just enough spice to keep it interesting.", 0.4678),
    ("This movie was actually neither that funny, nor super witty.", -0.6759),
    ("", 0.0),
]


def _r(x: float) -> float:
    return round(float(x), 3)


def binary_metrics(y_true: list[str], y_pred: list[str], pos: str = "Fresh", neg: str = "Rotten") -> dict:
    """Accuracy, balanced accuracy, per-class P/R/F1, macro-F1, confusion matrix."""
    cm = Counter(zip(y_true, y_pred))
    out = {"n": len(y_true), "confusion": {f"{t}->{p}": cm[(t, p)] for t in (pos, neg) for p in (pos, neg)}}
    per = {}
    for c in (pos, neg):
        tp = cm[(c, c)]
        fp = sum(v for (t, p), v in cm.items() if p == c and t != c)
        fn = sum(v for (t, p), v in cm.items() if t == c and p != c)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        per[c] = {"precision": _r(prec), "recall": _r(rec), "f1": _r(f1), "support": tp + fn}
    n = len(y_true) or 1
    out["accuracy"] = _r(sum(cm[(c, c)] for c in (pos, neg)) / n)
    out["balanced_accuracy"] = _r((per[pos]["recall"] + per[neg]["recall"]) / 2)
    out["macro_f1"] = _r((per[pos]["f1"] + per[neg]["f1"]) / 2)
    out["per_class"] = per
    return out


def vader_block(compounds: list[float], gold: list[str], lex: dict) -> dict:
    two = ["Fresh" if c >= 0 else "Rotten" for c in compounds]
    pos_t, neg_t = lex["thresholds"]["positive"], lex["thresholds"]["negative"]
    keep = [i for i, c in enumerate(compounds) if c >= pos_t or c <= neg_t]
    three = binary_metrics([gold[i] for i in keep], ["Fresh" if compounds[i] >= pos_t else "Rotten" for i in keep])
    three["neutral_excluded"] = len(compounds) - len(keep)
    three["coverage"] = _r(len(keep) / len(compounds)) if compounds else 0.0
    return {"two_class": binary_metrics(gold, two), "three_class_non_neutral": three}


def aspect_gold_eval(nlp, lex: dict) -> dict:
    """Precision/recall per aspect on the hand-labelled gold sentences (if present)."""
    if not GOLD.exists():
        return {"available": False}
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    items = gold["items"]
    preds_sp = []
    for r in nlp_spacy.analyze_docs(nlp, [it["text"] for it in items], lex):
        preds_sp.append({m["aspect"] for s in r["sentences"] for m in s["aspects"]})
    preds_kw = [{h["aspect"] for h in keyword_aspects(tokens(it["text"]), lex)} for it in items]

    def prf(preds):
        res = {}
        for a in lex["aspects"]:
            tp = sum(1 for it, p in zip(items, preds) if a in it["aspects"] and a in p)
            fp = sum(1 for it, p in zip(items, preds) if a not in it["aspects"] and a in p)
            fn = sum(1 for it, p in zip(items, preds) if a in it["aspects"] and a not in p)
            pr = tp / (tp + fp) if tp + fp else None
            rc = tp / (tp + fn) if tp + fn else None
            f1 = 2 * pr * rc / (pr + rc) if pr and rc else None
            res[a] = {"precision": _r(pr) if pr is not None else None, "recall": _r(rc) if rc is not None else None,
                      "f1": _r(f1) if f1 is not None else None, "support": tp + fn}
        tp = sum(len(set(it["aspects"]) & p) for it, p in zip(items, preds))
        fp = sum(len(p - set(it["aspects"])) for it, p in zip(items, preds))
        fn = sum(len(set(it["aspects"]) - p) for it, p in zip(items, preds))
        res["micro"] = {"precision": _r(tp / (tp + fp)) if tp + fp else None,
                        "recall": _r(tp / (tp + fn)) if tp + fn else None}
        return res

    return {
        "available": True,
        "n_sentences": len(items),
        "annotation": gold["annotation"],
        "spacy_build": prf(preds_sp),
        "keyword_browser": prf(preds_kw),
    }


def evaluate(reviews: pd.DataFrame, nl_all: list[dict], lex: dict, build: dict, parity: dict, nlp) -> dict:
    gold = reviews.review_type.astype(str).tolist()
    tuned = [n["compound"] for n in nl_all]
    stock = SentimentIntensityAnalyzer()  # no sci-fi overrides
    texts = reviews.review_content.astype(str).tolist()
    stock_c = [round(stock.polarity_scores(t)["compound"], 3) for t in texts]
    tuned_block = vader_block(tuned, gold, lex)
    stock_block = vader_block(stock_c, gold, lex)

    n_fresh = gold.count("Fresh")
    majority = binary_metrics(gold, ["Fresh"] * len(gold))

    per_film = []
    for link, g in reviews.groupby("rotten_tomatoes_link", sort=True):
        idx = list(g.index)
        m = binary_metrics([gold[i] for i in idx], ["Fresh" if tuned[i] >= 0 else "Rotten" for i in idx])
        per_film.append({"film": str(g.iloc[0]["rotten_tomatoes_link"]), "n": len(idx),
                         "fresh_share": _r(sum(1 for i in idx if gold[i] == "Fresh") / len(idx)),
                         "accuracy": m["accuracy"], "balanced_accuracy": m["balanced_accuracy"]})

    reg = []
    for text, expected in REGRESSION:
        got = stock.polarity_scores(text)["compound"]
        reg.append({"text": text, "expected": expected, "got": round(got, 4), "pass": abs(got - expected) < 1e-4})

    # Error analysis: the most confident disagreements, shown in methodology (attributed).
    errors = []
    order = sorted(range(len(gold)), key=lambda i: -abs(tuned[i]))
    for i in order:
        pred = "Fresh" if tuned[i] >= 0 else "Rotten"
        if pred != gold[i] and len(errors) < 4:
            r = reviews.iloc[i]
            errors.append({"text": str(r.review_content)[:300], "critic": str(r.critic_name),
                           "publisher": str(r.publisher_name), "label": gold[i], "compound": tuned[i]})

    t2 = tuned_block["two_class"]
    s2 = stock_block["two_class"]
    asp = aspect_gold_eval(nlp, lex)
    methodology = [
        f"Sentiment: NLTK VADER compound score per review (n = {len(gold)}), with "
        f"{len(lex['vader_overrides'])} sci-fi plot words neutralised (alien, war, dark, ...). "
        "Labels follow the VADER authors: compound >= 0.05 positive, <= -0.05 negative, otherwise neutral.",
        f"Check against Rotten Tomatoes labels (Fresh = positive, Rotten = negative), 2-class rule compound >= 0 -> Fresh: "
        f"accuracy {t2['accuracy']}, balanced accuracy {t2['balanced_accuracy']}, macro-F1 {t2['macro_f1']}. "
        f"Baseline 'always Fresh': accuracy {majority['accuracy']}, balanced accuracy {majority['balanced_accuracy']} "
        f"({n_fresh} of {len(gold)} reviews are Fresh, so accuracy alone flatters any model).",
        f"Ablation: stock VADER without the overrides scores accuracy {s2['accuracy']}, balanced accuracy "
        f"{s2['balanced_accuracy']}, macro-F1 {s2['macro_f1']}.",
        "Aspects: spaCy (en_core_web_sm) finds aspect mentions with a lemma lexicon plus a PhraseMatcher "
        "(e.g. 'sound design', 'third act'), links opinion adjectives via the dependency parse (amod, nsubj + acomp, "
        "conj, neg, compound), and NLTK VADER scores the sentence the mention is in.",
        "Film-domain EntityRuler: the product-review idea of 'brands and products' becomes STUDIO, FRANCHISE and "
        "FILM_TECH (IMAX, CGI, motion capture) patterns, plus PERSON and WORK_OF_ART seeded from each film's "
        "directors, writers, cast and title.",
        "Known failure modes: irony and backhanded praise; very short blurbs with no sentiment words (scored neutral); "
        "plot description that sounds negative; a Fresh label means the critic recommends the film overall, not "
        "that every sentence is positive.",
        "The in-browser analyzer runs the same NLTK code (pipeline/analyze_text.py) in Pyodide with the same "
        "lexicon file, but has no spaCy, so its aspect detection is keyword-based rather than dependency-based.",
    ]
    if asp.get("available"):
        sp, kw = asp["spacy_build"]["micro"], asp["keyword_browser"]["micro"]
        methodology.insert(4, f"Aspect detection on {asp['n_sentences']} hand-labelled review sentences "
                              f"({asp['annotation']['annotator']}): spaCy micro precision {sp['precision']}, "
                              f"recall {sp['recall']}; browser keyword matcher precision {kw['precision']}, "
                              f"recall {kw['recall']}.")
    return {
        "versions": build,
        "dataset": {"n_reviews": len(gold), "n_fresh": n_fresh, "n_rotten": len(gold) - n_fresh,
                    "source": "Rotten Tomatoes movies and critic reviews (Kaggle, CC0), sample in data/scifi_reviews.csv"},
        "vader_vs_labels": tuned_block,
        "baseline_majority": majority,
        "ablation": {"without_overrides": stock_block, "overrides": sorted(lex["vader_overrides"])},
        "per_film": per_film,
        "regression": {"source": "https://www.nltk.org/howto/sentiment.html", "cases": reg,
                       "all_pass": all(c["pass"] for c in reg)},
        "parity": {"n_cases": len(parity["cases"]), "method": "tests/e2e compare Pyodide output with site/data/parity.json to 3 dp"},
        "aspect_extraction": asp,
        "errors": errors,
        "methodology": methodology,
    }
