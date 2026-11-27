# Linguistic features

Source: https://spacy.io/usage/linguistic-features

## Token attributes
```python
nlp = spacy.load("en_core_web_sm")
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")
for token in doc:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
          token.shape_, token.is_alpha, token.is_stop)
```
- Lemmas: `token.lemma_`. The `Lemmatizer` component supports `mode: "lookup"` and `mode: "rule"` (rule mode uses POS/morph); `en_core_web_sm` ships the rule-based lemmatizer, so it needs the tagger + attribute_ruler.
- POS: `token.pos_` (coarse UPOS, e.g. ADJ, NOUN), `token.tag_` (fine), `token.morph`.

## Dependency parse
Navigate with `token.dep_`, `token.head`, `token.children`, `token.lefts`, `token.rights`, `token.subtree`.

## Noun chunks
```python
doc = nlp("Autonomous cars shift insurance liability toward manufacturers")
for chunk in doc.noun_chunks:
    print(chunk.text, chunk.root.text, chunk.root.dep_, chunk.root.head.text)
```
| Text | root.text | root.dep_ | root.head.text |
|---|---|---|---|
| Autonomous cars | cars | nsubj | shift |
| insurance liability | liability | dobj | shift |
| manufacturers | manufacturers | pobj | toward |

## Named entities
```python
for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)
```
Token-level: `token.ent_iob_` (B/I/O), `token.ent_type_`.

## Sentences
```python
doc = nlp("This is a sentence. This is another sentence.")
assert doc.has_annotation("SENT_START")
for sent in doc.sents: print(sent.text)
```
(The parser sets sentence boundaries in `en_core_web_sm`.)

## Aspect↔opinion relations used in this project
| Relation | Example | Rule |
|---|---|---|
| `amod` | "a gorgeous *score*" | ADJ child of aspect noun |
| `nsubj` + `acomp`/`attr` | "the *plot* is thin" | aspect is nsubj of copula; ADJ child of head |
| `conj` | "beautiful and haunting *music*" | follow conj from an opinion word |
| `neg` | "not memorable" | flip polarity |
| `compound` | "*sound design*" | join compound + head |
