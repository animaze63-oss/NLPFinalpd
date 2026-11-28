"""Netlify build step: run NLTK + spaCy over the committed sample and write static JSON.

Owner: pipeline-engineer. Invoked by the netlify.toml build command:

    NLTK_DATA=./nltk_data python pipeline/build_data.py

Reads  data/scifi_films.csv, data/scifi_reviews.csv
Writes site/data/films.json, site/data/film/<slug>.json, site/data/lexicon.json,
       site/data/examples.json (displaCy), site/data/parity.json, site/data/eval.json,
       site/py/analyze_text.py (verbatim copy for the Pyodide worker)
Every file is validated against schemas/*.schema.json before the build succeeds.
Contract: knowledge/pipeline-engineer/data-contract.md (schema_version 1.0).
"""
from __future__ import annotations

import json
import math
import platform
import re
import shutil
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import nltk  # noqa: E402
import pandas as pd  # noqa: E402
import spacy  # noqa: E402

import evaluate  # noqa: E402
import lexicon as lexmod  # noqa: E402
import nlp_nltk  # noqa: E402
import nlp_spacy  # noqa: E402
from analyze_text import analyze  # noqa: E402

ROOT = HERE.parent
DATA = ROOT / "data"
SITE = ROOT / "site"
OUT = SITE / "data"
SCHEMAS = ROOT / "schemas"
SCHEMA_VERSION = "1.0"
ASPECTS = list(lexmod.ASPECTS)
SKIP_ENT_LABELS = {"CARDINAL", "ORDINAL", "DATE", "TIME", "PERCENT", "MONEY", "QUANTITY"}
QUOTE_MAX = 300

# Sentences used for the browser/build parity check (written by the team, not critics).
PARITY_SENTENCES = [
    "The visual effects are stunning, but the third act is a mess.",
    "Hans Zimmer's score is thunderous and unforgettable.",
    "The characters are not memorable and the dialogue is clunky.",
    "A gorgeous, haunting film with a brilliant lead performance.",
    "The alien invasion plot is dark, but the world building is superb.",
    "Boring, overlong and painfully dull.",
    "The sound design is extraordinary.",
    "It's fine.",
    "The script is not fantastic, but the acting is decent and the cinematography is EXCELLENT!",
    "The plot was good, but the characters are uncompelling and the dialog is not great.",
]


# Rotten Tomatoes appends notes such as "[Full review in Spanish]" to translated blurbs.
# They are site metadata, not the critic's words, so they are removed before NLP and display.
RT_NOTE = re.compile(r"\s*\[\s*full review in [a-z ]+\.?\s*\]\.?", re.IGNORECASE)


def clean_review(text: str) -> str:
    return RT_NOTE.sub("", str(text)).strip()


def slugify(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def r3(x: float | None) -> float | None:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    return round(float(x), 3)


def mean(xs: list[float]) -> float | None:
    return r3(sum(xs) / len(xs)) if xs else None


def clip(text: str, n: int = QUOTE_MAX) -> str:
    """Verbatim excerpt, cut at a word boundary with an ellipsis if longer than n chars."""
    text = " ".join(str(text).split())
    if len(text) <= n:
        return text
    cut = text[: n - 1].rsplit(" ", 1)[0]
    return cut + "…"


def write_json(path: Path, obj) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)
    path.write_text(s, encoding="utf-8")
    return len(s.encode("utf-8"))


def none_if_nan(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    return v


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    films = pd.read_csv(DATA / "scifi_films.csv")
    reviews = pd.read_csv(DATA / "scifi_reviews.csv")
    reviews = reviews.dropna(subset=["review_content", "critic_name", "publisher_name"])
    reviews["review_content"] = reviews.review_content.map(clean_review)
    reviews = reviews[reviews.review_content.str.len() > 0]
    assert set(reviews.rotten_tomatoes_link) <= set(films.rotten_tomatoes_link)
    return films, reviews


def quote_of(row, text: str, compound: float) -> dict:
    return {
        "text": clip(text),
        "critic": str(row["critic_name"]),
        "publisher": str(row["publisher_name"]),
        "top_critic": bool(row["top_critic"]),
        "review_type": str(row["review_type"]),
        "date": none_if_nan(row["review_date"]),
        "compound": r3(compound),
    }


def build_film(film: dict, rows: pd.DataFrame, sp: list[dict], nl: list[dict], sia, lex: dict) -> dict:
    """Aggregate one film. ``sp`` = spaCy results per review, ``nl`` = NLTK results per review."""
    histogram = [{"from": r3(-1 + 0.2 * i), "to": r3(-0.8 + 0.2 * i), "n": 0} for i in range(10)]
    review_c = [n["compound"] for n in nl]
    for c in review_c:
        histogram[min(int((c + 1) / 0.2), 9)]["n"] += 1
    labels = Counter(nlp_nltk.label(c, lex) for c in review_c)

    # --- aspects (spaCy finds mention + opinion words; NLTK VADER scores the sentence)
    asp = {a: {"c": [], "reviews": set(), "terms": Counter(), "ops": Counter(), "neg": Counter(), "quotes": []}
           for a in ASPECTS}
    for ri, (row, s) in enumerate(zip(rows.to_dict("records"), sp)):
        for sent in s["sentences"]:
            if not sent["aspects"]:
                continue
            c = sia.polarity_scores(sent["text"])["compound"]
            for a in {m["aspect"] for m in sent["aspects"]}:
                asp[a]["c"].append(c)
                asp[a]["reviews"].add(ri)
                asp[a]["quotes"].append((c, row, sent["text"]))
            for m in sent["aspects"]:
                asp[m["aspect"]]["terms"][m["term"]] += 1
                for o in m["opinions"]:
                    asp[m["aspect"]]["ops"][o["word"]] += 1
                    asp[m["aspect"]]["neg"][o["word"]] += int(o["negated"])
    aspects = {}
    for a, d in asp.items():
        qs = sorted(d["quotes"], key=lambda q: q[0])
        picks = []
        if qs:
            if qs[-1][0] >= lex["thresholds"]["positive"]:
                picks.append(qs[-1])
            if qs[0][0] <= lex["thresholds"]["negative"] and qs[0] is not qs[-1]:
                picks.append(qs[0])
        aspects[a] = {
            "mentions": len(d["c"]),
            "reviews": len(d["reviews"]),
            "mean_compound": mean(d["c"]),
            "positive": sum(1 for c in d["c"] if c >= lex["thresholds"]["positive"]),
            "negative": sum(1 for c in d["c"] if c <= lex["thresholds"]["negative"]),
            "neutral": sum(1 for c in d["c"] if lex["thresholds"]["negative"] < c < lex["thresholds"]["positive"]),
            "top_terms": [[t, n] for t, n in d["terms"].most_common(8)],
            "top_opinions": [
                {"word": w, "count": n, "valence": r3(sia.lexicon.get(w, 0.0)), "negated": d["neg"][w]}
                for w, n in d["ops"].most_common(10)
            ],
            "quotes": [quote_of(row, text, c) for c, row, text in picks],
        }

    # --- NLTK: praise vs criticism words and key phrases (sentence label from VADER)
    by_label: dict[str, list[list[str]]] = defaultdict(list)
    for n in nl:
        for st in n["sentences"]:
            by_label[st["label"]].append(st["tokens"])
    all_toks = [t for v in by_label.values() for t in v]
    # The film's own title words ("blade", "runner") would top every list: drop them here only.
    title_words = [w for w in re.findall(r"[a-z]+", film["movie_title"].lower())]
    lex_words = {**lex, "domain_stopwords": lex["domain_stopwords"] + title_words}

    # --- spaCy: entities and noun chunks
    ent_counts: Counter = Counter()
    ent_source: dict = {}
    chunk_counts: Counter = Counter()
    chunk_aspect: dict = {}
    generic = set(lex["domain_stopwords"]) | {"sequel", "original", "people", "way", "end", "bit", "audience",
                                              "viewer", "filmmaker", "moment", "minute", "kind", "sort"}
    for s in sp:
        for e in s["entities"]:
            if e["label"] in SKIP_ENT_LABELS:
                continue
            key = (e["text"], e["label"])
            ent_counts[key] += 1
            if ent_source.get(key) != "ruler":
                ent_source[key] = e["source"]
        for phrase, aspect in s["noun_chunks"]:
            chunk_counts[phrase] += 1
            if aspect:
                chunk_aspect[phrase] = aspect
    entities = [{"text": t, "label": lab, "count": n, "source": ent_source[(t, lab)]}
                for (t, lab), n in sorted(ent_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:40]]
    ranked_chunks = [(p, n) for p, n in sorted(chunk_counts.items(), key=lambda kv: (-kv[1], kv[0]))
                     if p not in generic]
    with_aspect = [{"phrase": p, "count": n, "aspect": chunk_aspect[p]} for p, n in ranked_chunks if p in chunk_aspect][:20]
    other = [{"phrase": p, "count": n, "aspect": None} for p, n in ranked_chunks if p not in chunk_aspect and n >= 2][:12]
    noun_chunks = with_aspect + other

    # --- timeline by review year (NLTK review compound)
    years: dict[int, list[float]] = defaultdict(list)
    for row, c in zip(rows.to_dict("records"), review_c):
        d = none_if_nan(row["review_date"])
        if d:
            years[int(str(d)[:4])].append(c)
    timeline = [{"year": y, "n": len(v), "mean_compound": mean(v)} for y, v in sorted(years.items())]

    ranked = sorted(zip(review_c, rows.to_dict("records")), key=lambda t: t[0])
    most_pos = [quote_of(r, r["review_content"], c) for c, r in ranked[::-1][:3]]
    most_neg = [quote_of(r, r["review_content"], c) for c, r in ranked[:3] if c < 0]

    year = none_if_nan(film["original_release_date"])
    tm = none_if_nan(film["tomatometer_rating"])
    studio = none_if_nan(film["production_company"])
    consensus = none_if_nan(film["critics_consensus"])
    return {
        "schema_version": SCHEMA_VERSION,
        "slug": film["slug"],
        "title": film["movie_title"],
        "year": int(str(year)[:4]) if year else None,
        "directors": nlp_spacy._split_names(none_if_nan(film["directors"])),
        "cast": nlp_spacy._split_names(none_if_nan(film["actors"]))[:6],
        "studio": studio,
        "critics_consensus": consensus,
        "rt_url": "https://www.rottentomatoes.com/" + film["rotten_tomatoes_link"],
        "n_reviews": len(rows),
        "n_fresh": int((rows.review_type == "Fresh").sum()),
        "n_rotten": int((rows.review_type == "Rotten").sum()),
        "n_top_critics": int(rows.top_critic.astype(bool).sum()),
        "tomatometer": int(tm) if tm is not None else None,
        "sentiment": {
            "source": "nltk",
            "mean_compound": mean(review_c),
            "positive": labels["positive"],
            "neutral": labels["neutral"],
            "negative": labels["negative"],
            "n_sentences": sum(len(n["sentences"]) for n in nl),
            "histogram": histogram,
        },
        "aspects": aspects,
        "top_words": {
            "positive": nlp_nltk.top_words(by_label["positive"], lex_words),
            "negative": nlp_nltk.top_words(by_label["negative"], lex_words),
        },
        "collocations": {
            "positive": nlp_nltk.collocations(by_label["positive"], lex, n=8),
            "negative": nlp_nltk.collocations(by_label["negative"], lex, n=8),
            "all": nlp_nltk.collocations(all_toks, lex, n=12),
        },
        "entities": entities,
        "noun_chunks": noun_chunks,
        "timeline": timeline,
        "quotes": {"most_positive": most_pos, "most_negative": most_neg},
        "sources": {
            "sentiment": "nltk", "top_words": "nltk", "collocations": "nltk", "timeline": "nltk",
            "quotes": "nltk", "aspects": "spacy+nltk", "entities": "spacy", "noun_chunks": "spacy",
            "film": "dataset",
        },
    }


def pick_examples(reviews: pd.DataFrame, sp_all: list[dict]) -> list[dict]:
    """Two real review sentences with a linked aspect + opinion, for the displaCy panel."""
    picks, seen_aspects = [], set()
    for row, s in zip(reviews.to_dict("records"), sp_all):
        for sent in s["sentences"]:
            ok = [m for m in sent["aspects"] if m["opinions"]]
            if ok and 40 <= len(sent["text"]) <= 110 and ok[0]["aspect"] not in seen_aspects:
                seen_aspects.add(ok[0]["aspect"])
                picks.append((sent["text"], row, ok))
        if len(picks) >= 2:
            break
    return picks


def validate(files: dict[str, object]) -> None:
    from jsonschema import Draft202012Validator

    for schema_name, objs in files.items():
        schema = json.loads((SCHEMAS / f"{schema_name}.schema.json").read_text())
        v = Draft202012Validator(schema)
        for obj in objs if isinstance(objs, list) else [objs]:
            errs = sorted(v.iter_errors(obj), key=lambda e: e.path)
            if errs:
                raise SystemExit(f"schema {schema_name} failed: {errs[0].message} at {list(errs[0].path)}")


def main() -> None:
    t0 = time.perf_counter()
    nlp_nltk.ensure_data()
    lex = lexmod.export()
    sia = nlp_nltk.make_analyzer(lex)
    films, reviews = load_data()
    # Title slug; the 2017 Ghost in the Shell keeps its year so it can't clash with the 1995 anime.
    films["slug"] = [slugify(t) + ("-2017" if link == "m/ghost_in_the_shell_2017" else "")
                     for t, link in zip(films.movie_title, films.rotten_tomatoes_link)]
    assert films.slug.is_unique
    print(f"[build] {len(films)} films, {len(reviews)} reviews")

    # spaCy over all reviews in one nlp.pipe pass
    film_records = films.rename(columns={"movie_title": "title"}).to_dict("records")
    t = time.perf_counter()
    nlp = nlp_spacy.load_nlp(film_records, lex)
    texts = reviews.review_content.astype(str).tolist()
    sp_all = nlp_spacy.analyze_docs(nlp, texts, lex)
    t_spacy = time.perf_counter() - t

    # NLTK over all reviews
    t = time.perf_counter()
    nl_all = []
    for text in texts:
        sents = []
        for s in nlp_nltk.sentences(text):
            c = round(sia.polarity_scores(s)["compound"], 3)
            sents.append({"text": s, "compound": c, "label": nlp_nltk.label(c, lex), "tokens": nlp_nltk.tokens(s)})
        nl_all.append({"compound": round(sia.polarity_scores(text)["compound"], 3), "sentences": sents})
    t_nltk = time.perf_counter() - t
    print(f"[build] spaCy {t_spacy:.1f}s, NLTK {t_nltk:.1f}s")

    if OUT.exists():
        shutil.rmtree(OUT)
    sizes = {}
    film_objs, index = [], []
    reviews = reviews.reset_index(drop=True)
    for film in films.to_dict("records"):
        mask = (reviews.rotten_tomatoes_link == film["rotten_tomatoes_link"]).to_numpy()
        idx = [i for i, m in enumerate(mask) if m]
        rows = reviews.iloc[idx]
        obj = build_film(film, rows, [sp_all[i] for i in idx], [nl_all[i] for i in idx], sia, lex)
        film_objs.append(obj)
        index.append({
            "slug": obj["slug"], "title": obj["title"], "year": obj["year"], "directors": obj["directors"],
            "n_reviews": obj["n_reviews"], "tomatometer": obj["tomatometer"],
            "mean_compound": obj["sentiment"]["mean_compound"],
            "aspects": {a: obj["aspects"][a]["mean_compound"] for a in ASPECTS},
            "aspect_mentions": {a: obj["aspects"][a]["mentions"] for a in ASPECTS},
        })
    index.sort(key=lambda f: (f["year"] or 0, f["title"]))
    films_json = {
        "schema_version": SCHEMA_VERSION,
        "build": {
            "nltk": nltk.__version__, "spacy": spacy.__version__,
            "model": f"{nlp.meta['lang']}_{nlp.meta['name']}-{nlp.meta['version']}",
            "python": platform.python_version(), "n_films": len(index), "n_reviews": len(reviews),
            "lexicon_version": lex["lexicon_version"],
        },
        "films": index,
    }
    lex_json = {"schema_version": SCHEMA_VERSION, **lex}

    # displaCy examples from real review sentences (attributed)
    examples = []
    rendered = nlp_spacy.render_examples(nlp, [p[0] for p in pick_examples(reviews, sp_all)])
    for (text, row, ok), r in zip(pick_examples(reviews, sp_all), rendered):
        examples.append({**r, "critic": row["critic_name"], "publisher": row["publisher_name"],
                         "links": [{"aspect": m["aspect"], "term": m["term"],
                                    "opinions": [o["word"] for o in m["opinions"]]} for m in ok]})

    parity = {
        "schema_version": SCHEMA_VERSION,
        "note": "Build-time output of pipeline/analyze_text.py (CPython). The browser runs the same file in Pyodide; tests compare the two.",
        "python": platform.python_version(), "nltk": nltk.__version__,
        "cases": [{"text": s, "result": {k: v for k, v in analyze(s, lex, sia).items() if k in ("compound", "label", "aspects")}}
                  for s in PARITY_SENTENCES],
    }
    eval_json = evaluate.evaluate(reviews, nl_all, lex, films_json["build"], parity, nlp)
    eval_json["schema_version"] = SCHEMA_VERSION

    validate({"film": film_objs, "films": films_json, "lexicon": lex_json, "eval": eval_json})
    for obj in film_objs:
        sizes[f"film/{obj['slug']}.json"] = write_json(OUT / "film" / f"{obj['slug']}.json", obj)
    sizes["films.json"] = write_json(OUT / "films.json", films_json)
    sizes["lexicon.json"] = write_json(OUT / "lexicon.json", lex_json)
    sizes["examples.json"] = write_json(OUT / "examples.json", {"schema_version": SCHEMA_VERSION, "examples": examples})
    sizes["parity.json"] = write_json(OUT / "parity.json", parity)
    sizes["eval.json"] = write_json(OUT / "eval.json", eval_json)
    too_big = {k: v for k, v in sizes.items() if k.startswith("film/") and v > 150_000}
    if too_big:
        raise SystemExit(f"per-film JSON over 150 KB budget: {too_big}")

    (SITE / "py").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / "analyze_text.py", SITE / "py" / "analyze_text.py")
    total = sum(sizes.values())
    print(f"[build] wrote {len(sizes)} JSON files, {total / 1024:.0f} KB total "
          f"(largest film file {max(v for k, v in sizes.items() if k.startswith('film/')) / 1024:.0f} KB)")
    print(f"[build] VADER vs Fresh/Rotten accuracy (2-class): {eval_json['vader_vs_labels']['two_class']['accuracy']}")
    print(f"[build] done in {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
