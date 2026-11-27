# Rule-based matching

Source: https://spacy.io/usage/rule-based-matching

## EntityRuler
```python
ruler = nlp.add_pipe("entity_ruler", before="ner")   # before ner so ner respects our spans
patterns = [{"label": "ORG", "pattern": "Apple", "id": "apple"},
            {"label": "GPE", "pattern": [{"LOWER": "san"}, {"LOWER": "francisco"}], "id": "san-francisco"}]
ruler.add_patterns(patterns)
[(ent.text, ent.label_, ent.ent_id_) for ent in doc.ents]
```
- Phrase patterns are strings; token patterns are lists of attribute dicts.
- > "To overwrite overlapping entities, you can set `overwrite_ents=True` on initialization."
- > "If the `id` attribute is included in the EntityRuler patterns, the `ent_id_` property of the matched entity is set to the `id`" — use it to merge "Villeneuve" and "Denis Villeneuve".

## PhraseMatcher (multi-word aspect triggers)
```python
from spacy.matcher import PhraseMatcher
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")      # case-insensitive; attr="LEMMA" needs full pipeline docs
patterns = [nlp.make_doc(t) for t in ["special effects", "production design", "sound design", "world building"]]
matcher.add("VISUALS", patterns)
for match_id, start, end in matcher(doc):
    span = doc[start:end]
```
> "Only run nlp.make_doc to speed things up" (when building patterns).

## Matcher (token patterns)
> "The `Matcher` isn't as blazing fast as the `PhraseMatcher`, since it compares across individual token attributes."
```python
from spacy.matcher import Matcher
matcher = Matcher(nlp.vocab)
matcher.add("HelloWorld", [[{"LOWER": "hello"}, {"IS_PUNCT": True}, {"LOWER": "world"}]])
string_id = nlp.vocab.strings[match_id]
```

## DependencyMatcher
> "lets you match patterns within the dependency parse using Semgrex operators. It requires a model containing a parser."
```python
from spacy.matcher import DependencyMatcher
matcher = DependencyMatcher(nlp.vocab)
pattern = [{"RIGHT_ID": "anchor_founded", "RIGHT_ATTRS": {"ORTH": "founded"}}]
matcher.add("FOUNDED", [pattern])
```
Option for the aspect rules: anchor on an aspect-lemma NOUN, then `{"LEFT_ID": "aspect", "REL_OP": ">", "RIGHT_ID": "adj", "RIGHT_ATTRS": {"DEP": "amod"}}`.
