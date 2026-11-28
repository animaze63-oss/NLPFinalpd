"""Shared lexicon: aspect triggers, VADER overrides, thresholds and stopword extras.

Single source of truth for BOTH the build pipeline and the in-browser analyzer.
`build_data.py` exports it to ``site/data/lexicon.json``; the Pyodide worker loads that
file, so the browser and the build use the same lists (browser-build parity).

Owners: aspect lists -> spacy-expert; VADER overrides, thresholds, stopwords -> nltk-expert.
"""
from __future__ import annotations

LEXICON_VERSION = "1.0.0"

ASPECTS = ("visuals", "story", "characters", "soundtrack")

# Single-word lemma triggers (lowercase lemmas). Source: docs/02-spacy.md section 5, extended.
ASPECT_TERMS: dict[str, list[str]] = {
    "visuals": [
        "visual", "visuals", "effect", "effects", "cgi", "vfx", "cinematography", "cinematographer",
        "imagery", "image", "shot", "frame", "look", "spectacle", "photography", "color",
        "colour", "lighting", "landscape", "aesthetic", "camera", "camerawork",
        "3d", "imax", "animation", "design", "vista",     ],
    "story": [
        "story", "plot", "script", "screenplay", "narrative", "premise", "pacing", "pace",
        "ending", "act", "twist", "dialogue", "dialog", "idea", "writing", "logic", "storytelling",
        "plotting", "structure", "subplot", "climax", "finale", "concept", "storyline", "tale",
        "theme", "message", "allegory", "metaphor", "exposition", "runtime", "length",
    ],
    "characters": [
        "character", "characterization", "characterisation", "performance", "acting", "cast",
        "actor", "actress", "protagonist", "villain", "hero", "heroine", "role", "chemistry",
        "lead", "ensemble", "portrayal", "android", "replicant", "robot",
    ],
    "soundtrack": [
        "soundtrack", "score", "music", "sound", "composer", "synth", "audio", "song",
        "soundscape", "orchestra", "melody",
    ],
}

# Multi-word triggers (matched on lowercased text with a PhraseMatcher at build time and
# by token n-grams in the browser). A phrase match wins over its single-word parts.
ASPECT_PHRASES: dict[str, list[str]] = {
    "visuals": [
        "visual effects", "special effects", "practical effects", "production design",
        "art direction", "set design", "costume design", "world building", "world-building",
        "visual style", "visual splendor", "eye candy",
    ],
    "story": [
        "third act", "second act", "first act", "running time", "plot hole", "plot holes",
        "story line", "slow burn", "time travel", "hard sci fi", "hard science fiction",
    ],
    "characters": [
        "lead performance", "supporting cast", "main character", "central performance",
        "leading man", "leading lady",
    ],
    "soundtrack": [
        "sound design", "sound effects", "musical score", "original score", "electronic score",
        "sound mix", "theme song",
    ],
}

# Ambiguity rules (documented in the methodology page):
# - "theme" maps to soundtrack only when the sentence also has a soundtrack trigger, else story.
# - "design" alone is visuals; "sound design" (phrase) is soundtrack (phrase beats word).
# - "score" is soundtrack (critics' "review score" never appears in blurbs).
AMBIGUOUS = {"theme": {"default": "story", "if_sentence_has": "soundtrack", "then": "soundtrack"}}

# VADER lexicon overrides: neutralise sci-fi plot vocabulary that VADER scores as negative
# (docs/01-nltk.md section 3, knowledge/nltk-expert/vader.md).
VADER_OVERRIDES: dict[str, float] = {
    w: 0.0
    for w in [
        "alien", "aliens", "dark", "war", "invasion", "kill", "killer", "destroy",
        "apocalypse", "dystopian", "monster", "horror",
    ]
}

# VADER authors' thresholds (https://github.com/cjhutto/vaderSentiment).
POS_THRESHOLD = 0.05
NEG_THRESHOLD = -0.05

# Extra stopwords for the "top words" chart ONLY (never applied to VADER or aspect input).
DOMAIN_STOPWORDS = [
    "film", "films", "movie", "movies", "one", "like", "sci", "fi", "sci-fi", "scifi",
    "science", "fiction", "director", "also", "even", "much", "may", "might", "would", "could",
    "us", "make", "makes", "made", "get", "gets", "way", "thing", "things", "something",
    "still", "yet", "every", "ever", "least", "lot", "bit", "quite", "rather", "though",
    "enough", "takes", "take", "two", "first", "new", "year", "years", "time", "see", "seen",
    "full", "review", "spoiler", "alert",
]

# Negators are never removed from sentiment input (English stopwords include them).
NEGATORS = ["not", "no", "never", "n't", "nor", "nothing", "without"]


def export() -> dict:
    """Return the JSON-serialisable lexicon (written to site/data/lexicon.json)."""
    return {
        "lexicon_version": LEXICON_VERSION,
        "aspects": list(ASPECTS),
        "aspect_terms": ASPECT_TERMS,
        "aspect_phrases": ASPECT_PHRASES,
        "ambiguous": AMBIGUOUS,
        "vader_overrides": VADER_OVERRIDES,
        "thresholds": {"positive": POS_THRESHOLD, "negative": NEG_THRESHOLD},
        "domain_stopwords": DOMAIN_STOPWORDS,
        "negators": NEGATORS,
    }


def term_index(lex: dict | None = None) -> dict[str, str]:
    """Map every single-word trigger to its aspect."""
    lex = lex or export()
    return {t: a for a, terms in lex["aspect_terms"].items() for t in terms}
