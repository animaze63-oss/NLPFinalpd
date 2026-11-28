"""Build-time spaCy layer: NER + EntityRuler, noun-chunk aspects, aspect<->opinion links.

Owner: spacy-expert. Runs ONLY at Netlify build time (spaCy is not available in Pyodide).

Film-domain translation of the "brands and products" idea: the EntityRuler (added before
the statistical ``ner``) labels
  PERSON       directors, writers and billed cast from data/scifi_films.csv
  WORK_OF_ART  film titles (the curated films + classics critics compare them to)
  STUDIO       studios and production companies (Warner Bros., 20th Century Fox, ...)
  FRANCHISE    franchises / shared universes (Star Wars, Star Trek, Mad Max, ...)
  FILM_TECH    formats and filmmaking technology (IMAX, 3D, CGI, motion capture, ...)
and "noun-chunk aspects" are phrases such as "visual effects", "sound design",
"third act", "lead performance", mapped to visuals / story / characters / soundtrack.

Sources: https://spacy.io/usage/rule-based-matching#entityruler,
https://spacy.io/usage/linguistic-features (noun chunks, dependency parse),
https://spacy.io/api/phrasematcher, https://spacy.io/usage/visualizers
"""
from __future__ import annotations

from collections.abc import Iterable

import spacy
from spacy.language import Language
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc, Span, Token

MODEL = "en_core_web_sm"
RULER_ID = "film-ruler"

# Curated, film-domain patterns (not from the dataset).
COMPARED_WORKS = [
    "2001: A Space Odyssey", "2001", "Blade Runner", "Solaris", "Stalker", "Metropolis",
    "Close Encounters of the Third Kind", "Contact", "Gravity", "Inception", "Interstellar",
    "Prometheus", "Aliens", "Alien: Covenant", "The Terminator", "Terminator 2", "RoboCop",
    "Total Recall", "Minority Report", "Gattaca", "Moon", "Her", "District 9", "Avatar",
    "The Fifth Element", "Jurassic Park", "Titanic", "Arrival", "Ex Machina", "Annihilation",
    "Sicario", "Dune", "Ghost in the Shell", "Akira", "Oblivion", "Elysium", "Tron",
    "Tron: Legacy", "Children of Men", "The Road Warrior", "Mad Max 2", "Under the Skin",
    "Contagion", "Cast Away", "Apollo 13", "Passengers", "Valerian", "Edge of Tomorrow",
    "The Thing", "Jaws", "Star Wars", "The Empire Strikes Back", "Snowpiercer",
]
FRANCHISES = [
    "Star Wars", "Star Trek", "Mad Max", "The Matrix", "Matrix", "Alien", "Terminator",
    "Marvel Cinematic Universe", "MCU", "Marvel", "DC", "Transformers", "Jurassic",
    "Planet of the Apes", "Blade Runner", "Ghost in the Shell", "Doctor Who", "Avengers",
    "James Bond", "Harry Potter", "Lord of the Rings", "Twilight", "Hunger Games",
]
STUDIOS = [
    "Warner Bros.", "Warner Bros", "Warner Brothers", "20th Century Fox", "Twentieth Century Fox",
    "Fox", "Paramount", "Universal", "Sony", "Columbia Pictures", "Disney", "Pixar", "A24",
    "Netflix", "Amazon", "Lionsgate", "Legendary", "Legendary Pictures", "DreamWorks",
    "Marvel Studios", "Lucasfilm", "Weta", "Weta Digital", "Industrial Light & Magic", "ILM",
    "Village Roadshow", "Alcon Entertainment", "Scott Free", "EuropaCorp", "MGM",
    "Studio Ghibli", "Hollywood",
]
FILM_TECH = [
    "IMAX", "3D", "3-D", "CGI", "CG", "VFX", "Dolby Atmos", "Dolby", "70mm", "70 mm", "35mm",
    "65mm", "motion capture", "performance capture", "mo-cap", "green screen", "greenscreen",
    "practical effects", "animatronics", "digital effects", "computer-generated",
    "computer graphics", "4K", "HFR", "widescreen", "Steadicam",
]


def _split_names(cell: str | None) -> list[str]:
    if not cell or not isinstance(cell, str):
        return []
    return [p.strip() for p in cell.split(",") if p.strip()]


def ruler_patterns(films: Iterable[dict]) -> list[dict]:
    """EntityRuler patterns seeded from film metadata plus the curated lists above.

    Precedence on duplicates: dataset titles (WORK_OF_ART) > FRANCHISE > compared works.
    """
    pats: dict[str, dict] = {}

    def add(label: str, text: str, lower: bool = False) -> None:
        key = text.lower() if lower else text
        if not text or key in pats:
            return
        if lower:
            pattern = [{"LOWER": t.lower()} for t in text.split()]
        else:
            pattern = text
        pats[key] = {"label": label, "pattern": pattern, "id": RULER_ID}

    films = list(films)
    for f in films:
        add("WORK_OF_ART", f["title"])
    for f in films:
        for person in _split_names(f.get("directors")) + _split_names(f.get("authors")) + _split_names(f.get("actors")):
            add("PERSON", person)
        for d in _split_names(f.get("directors")):
            last = d.split()[-1]
            if len(last) > 4:
                add("PERSON", last)
        for studio in _split_names(f.get("production_company")):
            add("STUDIO", studio)
    for x in FRANCHISES:
        add("FRANCHISE", x)
    for x in COMPARED_WORKS:
        add("WORK_OF_ART", x)
    for x in STUDIOS:
        add("STUDIO", x)
    for x in FILM_TECH:
        add("FILM_TECH", x, lower=True)
    return list(pats.values())


def load_nlp(films: Iterable[dict], lexicon: dict) -> Language:
    """en_core_web_sm + EntityRuler before ner + an aspect PhraseMatcher (LOWER)."""
    nlp = spacy.load(MODEL)
    ruler = nlp.add_pipe("entity_ruler", before="ner", config={"phrase_matcher_attr": None})
    ruler.add_patterns(ruler_patterns(films))
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    for aspect, phrases in lexicon["aspect_phrases"].items():
        matcher.add(aspect, [nlp.make_doc(p) for p in phrases])
    nlp.user_data = {"aspect_matcher": matcher}  # type: ignore[attr-defined]
    return nlp


# ---------------------------------------------------------------- aspect extraction

def _term_index(lexicon: dict) -> dict[str, str]:
    return {t: a for a, terms in lexicon["aspect_terms"].items() for t in terms}


def _is_negated(*toks: Token) -> bool:
    return any(c.dep_ == "neg" for t in toks for c in t.children)


def _is_opinion(t: Token) -> bool:
    """Adjectives, plus -ing/-ed participles used adjectivally ("haunting", "overstuffed")."""
    if t.ent_type_ in ("ORDINAL", "CARDINAL") or t.like_num:
        return False
    return t.pos_ == "ADJ" or (t.pos_ == "VERB" and t.tag_ in ("VBG", "VBN"))


def _opinions_for(noun: Token, exclude: set[int] = frozenset()) -> list[Token]:
    """Opinion words attached to an aspect noun through the dependency parse.

    amod: "a gorgeous score"; nsubj + acomp/attr: "the plot is thin";
    predicate participle: "the visuals are breathtaking" (ROOT VBG with aux "be");
    conj siblings of an opinion: "beautiful and haunting music"; conj aspect nouns share
    their head's predicate: "the visuals and the sound design are breathtaking".
    """
    ops = [c for c in noun.children if c.dep_ == "amod" and _is_opinion(c)]
    subj = noun
    while subj.dep_ == "conj" and subj.head.pos_ in ("NOUN", "PROPN"):
        subj = subj.head
    if subj.dep_ in ("nsubj", "nsubjpass"):
        head = subj.head
        ops += [c for c in head.children if c.dep_ in ("acomp", "attr", "oprd") and _is_opinion(c)]
        if _is_opinion(head) and any(c.dep_ in ("aux", "auxpass") and c.lemma_ == "be" for c in head.children):
            ops.append(head)
        elif head.pos_ == "ADJ":
            ops.append(head)
        for c in head.children:  # "the score is a masterpiece" -> adjectives on the attr noun
            if c.dep_ == "attr" and c.pos_ == "NOUN":
                ops += [g for g in c.children if g.dep_ == "amod" and _is_opinion(g)]
    for o in list(ops):
        ops += [c for c in o.children if c.dep_ == "conj" and _is_opinion(c)]
    seen, uniq = set(exclude), []
    for o in ops:
        if o.i not in seen:
            seen.add(o.i)
            uniq.append(o)
    return uniq


def sentence_aspects(sent: Span, lexicon: dict, matcher: PhraseMatcher, index: dict[str, str]) -> list[dict]:
    """Aspect mentions in one spaCy sentence with their linked opinion words."""
    doc = sent.doc
    found: list[dict] = []
    covered: set[int] = set()
    sent_aspects = {index.get(t.lemma_.lower()) for t in sent if t.pos_ in ("NOUN", "PROPN")}
    # match on the whole Doc (doc-relative offsets) and keep matches inside this sentence
    for match_id, start, end in matcher(doc):
        if start < sent.start or end > sent.end:
            continue
        span = doc[start:end]
        if covered.intersection(range(span.start, span.end)):
            continue
        covered.update(range(span.start, span.end))
        root = span.root
        found.append({"aspect": doc.vocab.strings[match_id], "term": span.text.lower(), "root": root,
                      "span": set(range(span.start, span.end))})
    for tok in sent:
        if tok.i in covered or tok.pos_ not in ("NOUN", "PROPN"):
            continue
        lemma = tok.lemma_.lower()
        aspect = index.get(lemma)
        if not aspect:
            continue
        rule = lexicon["ambiguous"].get(lemma)
        if rule:
            aspect = rule["then"] if rule["if_sentence_has"] in sent_aspects else rule["default"]
        # compound modifiers make the term multi-word: "sound design", "creature effects"
        comp = [c for c in tok.children if c.dep_ == "compound" and c.i < tok.i]
        term = " ".join([c.text.lower() for c in comp] + [lemma])
        found.append({"aspect": aspect, "term": term, "root": tok, "span": {c.i for c in comp} | {tok.i}})
    out = []
    for f in found:
        root = f["root"]
        ops = _opinions_for(root, f["span"])
        neg_head = _is_negated(root.head) if root.dep_ in ("nsubj", "nsubjpass") else False
        out.append({
            "aspect": f["aspect"],
            "term": f["term"],
            "opinions": [{"word": (o.lemma_ if o.pos_ == "ADJ" else o.text).lower(),
                          "negated": neg_head or _is_negated(o)} for o in ops],
        })
    return out


def noun_chunk_aspects(doc: Doc, index: dict[str, str], phrases: dict[str, str] | None = None) -> list[tuple[str, str | None]]:
    """Noun chunks normalised (no determiners/pronouns/stopwords), with an aspect:
    a lexicon phrase inside the chunk wins ("sound design" -> soundtrack), else the root lemma."""
    phrases = phrases or {}
    out = []
    for chunk in doc.noun_chunks:
        words = [t for t in chunk if t.is_alpha and t.pos_ not in ("DET", "PRON")
                 and (not t.is_stop or t.ent_type_ == "ORDINAL")]
        if not words or all(t.pos_ == "PROPN" for t in words):
            continue
        phrase = " ".join(t.lemma_.lower() if t.i == chunk.root.i else t.text.lower() for t in words)
        if len(phrase) < 3:
            continue
        text = chunk.text.lower()
        aspect = next((a for p, a in phrases.items() if p in text), None) or index.get(chunk.root.lemma_.lower())
        out.append((phrase, aspect))
    return out


def analyze_docs(nlp: Language, texts: list[str], lexicon: dict, batch_size: int = 256) -> list[dict]:
    """Run the pipeline over all review texts with nlp.pipe and return plain dicts."""
    matcher: PhraseMatcher = nlp.user_data["aspect_matcher"]  # type: ignore[attr-defined]
    index = _term_index(lexicon)
    phrases = {p: a for a, ps in lexicon["aspect_phrases"].items() for p in ps}
    results = []
    for doc in nlp.pipe(texts, batch_size=batch_size):
        sents = []
        for sent in doc.sents:
            sents.append({"text": sent.text.strip(), "aspects": sentence_aspects(sent, lexicon, matcher, index)})
        ents = [{"text": e.text, "label": e.label_, "source": "ruler" if e.ent_id_ == RULER_ID else "model"}
                for e in doc.ents]
        results.append({
            "sentences": sents,
            "entities": ents,
            "noun_chunks": noun_chunk_aspects(doc, index, phrases),
            "lemmas": [t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop],
        })
    return results


def render_examples(nlp: Language, sentences: list[str]) -> list[dict]:
    """Pre-render displaCy SVG (dependencies) and HTML (entities) at build time."""
    from spacy import displacy

    out = []
    for s in sentences:
        doc = nlp(s)
        out.append({
            "text": s,
            "dep_svg": displacy.render(doc, style="dep", jupyter=False,
                                       options={"compact": True, "distance": 110, "bg": "transparent",
                                                "color": "currentColor", "font": "inherit"}),
            "ents": [{"text": e.text, "label": e.label_, "start": e.start_char, "end": e.end_char} for e in doc.ents],
        })
    return out
