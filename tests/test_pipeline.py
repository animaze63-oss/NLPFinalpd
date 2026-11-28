"""Built JSON: schema validation, contract rules, attribution, sizes, parity file, data sample."""
import json
import math
import re
from pathlib import Path

import pandas as pd
import pytest
from jsonschema import Draft202012Validator

from conftest import ROOT, load

SCHEMAS = ROOT / "schemas"


def validator(name):
    return Draft202012Validator(load(SCHEMAS / f"{name}.schema.json"))


def test_schemas_are_valid():
    for p in SCHEMAS.glob("*.schema.json"):
        Draft202012Validator.check_schema(load(p))


def test_all_outputs_validate(site_data):
    errs = []
    for name, files in [("films", [site_data / "films.json"]), ("lexicon", [site_data / "lexicon.json"]),
                        ("eval", [site_data / "eval.json"]), ("film", sorted((site_data / "film").glob("*.json")))]:
        v = validator(name)
        for f in files:
            errs += [f"{f.name}: {e.message}" for e in v.iter_errors(load(f))]
    assert errs == []


def test_index_matches_film_files(site_data):
    idx = load(site_data / "films.json")
    slugs = {f["slug"] for f in idx["films"]}
    assert slugs == {p.stem for p in (site_data / "film").glob("*.json")}
    assert all(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", s) for s in slugs)
    assert idx["build"]["nltk"] == "3.9.4"


def test_contract_rules(site_data):
    for p in (site_data / "film").glob("*.json"):
        raw = p.read_text(encoding="utf-8")
        assert "NaN" not in raw and "Infinity" not in raw
        assert p.stat().st_size < 150_000
        d = json.loads(raw)
        assert d["schema_version"].startswith("1.")
        quotes = [q for a in d["aspects"].values() for q in a["quotes"]] + d["quotes"]["most_positive"] + d["quotes"]["most_negative"]
        for q in quotes:  # decision record 7: every quote credits critic + publication
            assert q["critic"].strip() and q["publisher"].strip() and len(q["text"]) <= 300
            assert "[Full review" not in q["text"]
        assert d["sources"]["entities"] == "spacy" and d["sources"]["sentiment"] == "nltk"


def test_quotes_are_verbatim_from_dataset(site_data):
    reviews = " ".join(pd.read_csv(ROOT / "data" / "scifi_reviews.csv").review_content.astype(str))
    norm = " ".join(reviews.split())
    for p in (site_data / "film").glob("*.json"):
        d = load(p)
        for q in d["quotes"]["most_positive"] + d["quotes"]["most_negative"]:
            assert q["text"].rstrip("…") in norm


def test_lexicon_json_equals_python_lexicon(site_data, lex):
    j = load(site_data / "lexicon.json")
    j.pop("schema_version")
    assert j == json.loads(json.dumps(lex))


def test_browser_copy_is_identical_to_pipeline_module(site_data):
    assert (ROOT / "site" / "py" / "analyze_text.py").read_bytes() == (ROOT / "pipeline" / "analyze_text.py").read_bytes()


def test_parity_file_reproduces_in_cpython(site_data, lex, sia):
    from analyze_text import analyze
    for case in load(site_data / "parity.json")["cases"]:
        r = analyze(case["text"], lex, sia)
        assert r["compound"] == case["result"]["compound"]
        assert r["aspects"] == case["result"]["aspects"]


def test_eval_numbers_are_consistent(site_data):
    e = load(site_data / "eval.json")
    t = e["vader_vs_labels"]["two_class"]
    assert t["n"] == e["dataset"]["n_reviews"] == sum(t["confusion"].values())
    assert e["regression"]["all_pass"]
    assert e["aspect_extraction"]["available"]


def test_committed_sample_is_small_and_attributed():
    r = pd.read_csv(ROOT / "data" / "scifi_reviews.csv")
    f = pd.read_csv(ROOT / "data" / "scifi_films.csv")
    assert (ROOT / "data" / "scifi_reviews.csv").stat().st_size < 1_000_000
    assert 8 <= len(f) <= 15 and r.groupby("rotten_tomatoes_link").size().between(40, 80).all()
    assert r.critic_name.notna().all() and r.publisher_name.notna().all()
    assert set(r.review_type) == {"Fresh", "Rotten"}
    assert f.genres.str.contains("Science Fiction").all()


def test_no_functions_or_spacy_in_browser():
    """Decision record: no Netlify Functions / Edge Functions; spaCy never in site/."""
    assert not (ROOT / "netlify" / "functions").exists() and not (ROOT / "netlify" / "edge-functions").exists()
    for p in (ROOT / "site").rglob("*"):
        if p.suffix in {".js", ".mjs", ".py", ".html"} and "pyodide" not in p.parts:
            assert "import spacy" not in p.read_text(encoding="utf-8", errors="ignore")
    toml = (ROOT / "netlify.toml").read_text()
    assert 'PYTHON_VERSION = "3.12"' in toml and 'publish = "site"' in toml
    assert "cdn.jsdelivr" not in (ROOT / "site" / "js" / "analyzer.worker.mjs").read_text()
