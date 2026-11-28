"""spaCy layer: EntityRuler film-domain labels, aspect<->opinion dependency rules, noun chunks."""
import pytest

import nlp_spacy


def run(nlp, lex, text):
    return nlp_spacy.analyze_docs(nlp, [text], lex)[0]


def links(r):
    return {(m["aspect"], m["term"], o["word"], o["negated"]) for s in r["sentences"] for m in s["aspects"] for o in m["opinions"]}


def test_pipeline_has_ruler_before_ner(nlp):
    names = nlp.pipe_names
    assert names.index("entity_ruler") < names.index("ner")


@pytest.mark.parametrize("text,ent,label", [
    ("Shot in IMAX with motion capture.", "IMAX", "FILM_TECH"),
    ("Shot in IMAX with motion capture.", "motion capture", "FILM_TECH"),
    ("A Warner Bros. release.", "Warner Bros.", "STUDIO"),
    ("It is no Star Wars.", "Star Wars", "FRANCHISE"),
    ("Denis Villeneuve directs.", "Denis Villeneuve", "PERSON"),
    ("Better than Ex Machina.", "Ex Machina", "WORK_OF_ART"),
])
def test_entity_ruler_labels(nlp, lex, text, ent, label):
    ents = {(e["text"], e["label"], e["source"]) for e in run(nlp, lex, text)["entities"]}
    assert (ent, label, "ruler") in ents


def test_amod(nlp, lex):
    assert ("soundtrack", "score", "gorgeous", False) in links(run(nlp, lex, "It has a gorgeous score."))


def test_nsubj_acomp(nlp, lex):
    assert ("story", "plot", "thin", False) in links(run(nlp, lex, "The plot is thin."))


def test_negation(nlp, lex):
    assert ("characters", "character", "memorable", True) in links(run(nlp, lex, "The characters are not memorable."))


def test_conj_opinions(nlp, lex):
    # Note: en_core_web_sm misparses "The beautiful and haunting score lingers." ("lingers" as a
    # noun), a known small-model failure mode; the copular form parses reliably.
    ls = links(run(nlp, lex, "The score is beautiful and haunting."))
    assert {("soundtrack", "score", "beautiful", False), ("soundtrack", "score", "haunting", False)} <= ls


def test_phrase_aspect_and_no_self_modifier(nlp, lex):
    r = run(nlp, lex, "The visual effects are stunning, but the third act is clunky.")
    ls = links(r)
    assert ("visuals", "visual effects", "stunning", False) in ls
    assert ("story", "third act", "clunky", False) in ls
    assert not any(w in ("visual", "third") for _, _, w, _ in ls)


def test_conj_aspect_shares_predicate(nlp, lex):
    ls = links(run(nlp, lex, "The visuals and the sound design are breathtaking."))
    assert {a for a, *_ in ls} == {"visuals", "soundtrack"}


def test_score_as_verb_is_not_soundtrack(nlp, lex):
    r = run(nlp, lex, "It never soars beyond its cold desire to score the big bucks.")
    assert not any(m["aspect"] == "soundtrack" for s in r["sentences"] for m in s["aspects"])


def test_noun_chunks_map_to_aspects(nlp, lex):
    chunks = dict(run(nlp, lex, "The sound design and the lead performance carry a thin plot.")["noun_chunks"])
    assert chunks["sound design"] == "soundtrack"
    assert chunks["lead performance"] == "characters"
    assert chunks["thin plot"] == "story"
