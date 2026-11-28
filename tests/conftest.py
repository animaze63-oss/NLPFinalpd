import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

import lexicon as lexmod  # noqa: E402
import nlp_nltk  # noqa: E402

nlp_nltk.ensure_data()


@pytest.fixture(scope="session")
def lex():
    return lexmod.export()


@pytest.fixture(scope="session")
def sia(lex):
    return nlp_nltk.make_analyzer(lex)


@pytest.fixture(scope="session")
def films():
    import pandas as pd
    return pd.read_csv(ROOT / "data" / "scifi_films.csv").rename(columns={"movie_title": "title"}).to_dict("records")


@pytest.fixture(scope="session")
def nlp(films, lex):
    import nlp_spacy
    return nlp_spacy.load_nlp(films, lex)


@pytest.fixture(scope="session")
def site_data():
    d = ROOT / "site" / "data"
    if not (d / "films.json").exists():
        pytest.skip("run the build first: NLTK_DATA=./nltk_data python pipeline/build_data.py")
    return d


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
