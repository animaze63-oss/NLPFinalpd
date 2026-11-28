"""NLTK layer: VADER reference outputs, overrides, thresholds, tokenizing, counts, phrases."""
import pytest
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import nlp_nltk
from analyze_text import analyze, content_words, keyword_aspects, label, tokens
from evaluate import REGRESSION


@pytest.mark.parametrize("text,expected", REGRESSION)
def test_vader_reference_outputs_from_nltk_howto(text, expected):
    assert SentimentIntensityAnalyzer().polarity_scores(text)["compound"] == pytest.approx(expected, abs=1e-4)


def test_scifi_overrides_neutralise_plot_words(sia):
    stock = SentimentIntensityAnalyzer()
    assert stock.polarity_scores("an alien war")["compound"] < 0
    assert sia.polarity_scores("an alien war")["compound"] == 0.0
    for w in ["alien", "war", "dark", "kill", "apocalypse"]:
        assert sia.lexicon[w] == 0.0


@pytest.mark.parametrize("c,lab", [(0.05, "positive"), (0.049, "neutral"), (-0.049, "neutral"), (-0.05, "negative")])
def test_thresholds(c, lab, lex):
    assert label(c, lex) == lab


def test_tokens_keep_negators_but_content_words_drop_them(lex):
    toks = tokens("The plot isn't good and the score is not great.")
    assert "n't" in toks and "not" in toks
    cw = content_words(toks, lex)
    assert "n't" not in cw and "not" not in cw and "plot" in cw


def test_sentence_split_uses_punkt():
    assert len(nlp_nltk.sentences("Dr. Smith liked it. I did not.")) == 2


def test_keyword_aspects_phrase_beats_word_and_theme_rule(lex):
    hits = keyword_aspects(tokens("The sound design is great."), lex)
    assert [(h["aspect"], h["term"]) for h in hits] == [("soundtrack", "sound design")]
    assert {h["aspect"] for h in keyword_aspects(tokens("The theme is grief."), lex)} == {"story"}
    assert {h["aspect"] for h in keyword_aspects(tokens("The theme music soars."), lex)} == {"soundtrack"}


def test_top_words_and_collocations(lex):
    sents = [tokens(s) for s in ["The production design is gorgeous."] * 3 + ["Gorgeous production design again."]]
    top = dict(nlp_nltk.top_words(sents, lex))
    assert top["production"] == 4 and "the" not in top
    phrases = [p["phrase"] for p in nlp_nltk.collocations(sents, lex)]
    assert "production design" in phrases


def test_analyze_shape(lex, sia):
    r = analyze("The visuals are stunning. The plot is a mess.", lex, sia)
    assert set(r) >= {"compound", "label", "scores", "sentences", "aspects", "top_words"}
    assert r["n_sentences"] == 2
    assert r["aspects"]["visuals"]["mean_compound"] > 0 > r["aspects"]["story"]["mean_compound"]
    assert analyze("", lex, sia)["compound"] == 0.0
