# 02 — What spaCy does best in Scifi Cinema Lens

**Role in the app:** spaCy provides the *linguistic structure* layer: who/what is mentioned (named entities), what is being talked about (noun chunks), normalised word forms (lemmas), and how opinion words attach to the things they describe (dependency parsing). That structure is what turns "sentiment scores" into **aspect-based** answers: *what* reviewers praise or criticise — visuals, story, characters, soundtrack.

## Model choice

| Model | Size | Components | NER F | Dep. LAS |
|---|---|---|---|---|
| `en_core_web_sm` 3.8.0 | **12 MB** | tok2vec, tagger, parser, senter, attribute_ruler, lemmatizer, ner | 0.84 | 0.90 |
| `en_core_web_md` 3.8.0 | 31 MB | same + word vectors | 0.85 | 0.90 |

Source: https://spacy.io/models/en. **Recommendation: `en_core_web_sm`** — near-identical accuracy, smallest download, fastest build. Use `_md` only if we want vector similarity (e.g. "find reviews similar to this one").

Install (pin the model as a wheel URL in `requirements.txt` so `pip install -r` works on Netlify without a separate download step):

```
spacy>=3.8,<3.9
en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

Efficiency: process reviews with `nlp.pipe(texts, batch_size=256)`; disable unused components where possible (`nlp.select_pipes(disable=[...])`).

---

## 1. Named entities (NER)

`[(e.text, e.label_) for e in doc.ents]`

What it gives this app:

| Label | Typical hits in sci-fi reviews | Dashboard use |
|---|---|---|
| `PERSON` | Denis Villeneuve, Hans Zimmer, Ridley Scott, Ryan Gosling | "People reviewers talk about" chip cloud; links praise to composer / director / cast |
| `WORK_OF_ART` | *Blade Runner*, *2001: A Space Odyssey*, *Star Wars* | **Comparisons**: which classics a film is measured against |
| `ORG` | Pixar, Marvel, Warner Bros., Netflix | Studio mentions |
| `GPE` / `LOC` | Arrakis (often mislabelled), Los Angeles, Mars | Settings (noisy — treat as exploratory) |
| `DATE` | "1982", "the '70s" | Era references |

Caveats: the small model was trained on news/web text (OntoNotes), so fictional names (*Arrakis*, *HAL 9000*) are sometimes mislabelled or missed. Mitigation: an `EntityRuler` added **before** `ner` with a small pattern list built from the film metadata (title, director, cast columns in the dataset):

```python
ruler = nlp.add_pipe("entity_ruler", before="ner")
ruler.add_patterns([{"label": "PERSON", "pattern": "Hans Zimmer"},
                    {"label": "WORK_OF_ART", "pattern": "Blade Runner 2049"}])
```

## 2. Noun chunks

`[c.text for c in doc.noun_chunks]` → base noun phrases such as *"the stunning visual effects"*, *"a thin plot"*, *"Zimmer's thunderous score"*.

- Use `chunk.root.lemma_` to map each chunk to an **aspect** (see the lexicon below).
- Chunks whose root is an aspect word, plus their adjectives, are the best raw material for a "what people said about the visuals" list.
- Noun-chunk frequency is a better "topics" chart than single-word frequency.

## 3. Lemmas

`token.lemma_` — `effects → effect`, `characters → character`, `was → be`, `stunning → stunning`.

- Feed lemmas (filtered with `not token.is_stop and token.is_alpha`) into **NLTK `FreqDist` / collocations** so counts merge inflected forms.
- Aspect matching is done on lemmas so one lexicon entry covers all forms.
- Also available per token: `pos_` (coarse POS), `tag_`, `is_stop`, `like_num` — e.g. keep only `ADJ` lemmas for an "adjectives used about this film" cloud.

## 4. Dependency parsing (aspect ↔ opinion linking)

This is spaCy's most valuable contribution: it tells us **which adjective describes which noun**, so *"The visuals are breathtaking but the dialogue is clunky"* yields `visuals → breathtaking (+)` and `dialogue → clunky (−)` instead of one blended score.

Key relations (`token.dep_`, `token.head`, `token.children`):

| Pattern | Example | Rule |
|---|---|---|
| `amod` | "a **gorgeous** *score*" | adjective child of the aspect noun |
| `nsubj` + `acomp` | "the *plot* is **thin**" | aspect is `nsubj` of a copula whose child is `acomp` |
| `conj` | "**beautiful** and **haunting** *music*" | follow `conj` from an opinion word to collect siblings |
| `neg` | "the *characters* are **not** **memorable**" | flip polarity if a `neg` child is present |
| `compound` | "*sound design*", "*special effects*" | join compound + head to get multi-word aspects |

Sketch:

```python
def aspect_opinions(doc):
    out = []
    for tok in doc:
        if tok.pos_ == "NOUN" and tok.lemma_ in ASPECT_OF:
            aspect = ASPECT_OF[tok.lemma_]
            opinions = [c for c in tok.children if c.dep_ == "amod"]
            if tok.dep_ == "nsubj":
                opinions += [c for c in tok.head.children if c.dep_ in ("acomp", "attr") and c.pos_ == "ADJ"]
            opinions += [c for o in list(opinions) for c in o.children if c.dep_ == "conj"]
            negated = any(c.dep_ == "neg" for c in tok.head.children)
            for o in opinions:
                out.append((aspect, tok.text, o.lemma_, negated, tok.sent))
    return out
```

Each opinion word (or its sentence) is then scored with **NLTK VADER** → per-aspect sentiment.

Visual bonus for the dashboard / report: `spacy.displacy.render(doc, style="dep")` and `style="ent"` produce SVG/HTML — pre-render one or two example sentences at build time for an "how the NLP works" panel.

## 5. Aspect lexicon (starting point — agents should extend it)

| Aspect | Lemma triggers |
|---|---|
| **Visuals** | visual, effect, cgi, vfx, cinematography, imagery, image, shot, frame, look, design, production, spectacle, photography, color, lighting, set, world-building |
| **Story** | story, plot, script, screenplay, narrative, premise, pacing, ending, act, twist, dialogue, idea, theme, writing, logic |
| **Characters** | character, performance, acting, cast, actor, actress, protagonist, villain, hero, role, chemistry, lead, ensemble |
| **Soundtrack** | soundtrack, score, music, sound, composer, theme (ambiguous with Story), synth, audio, song |

Handle ambiguity explicitly (e.g. *theme* → Story unless the sentence also contains a Soundtrack trigger; *design* → Visuals; *sound design* compound → Soundtrack). Also match multi-word triggers with spaCy's `PhraseMatcher` (`special effects`, `production design`, `sound design`, `world building`).

## 6. spaCy outside of normal Python (important for deployment)

- **spaCy is not in Pyodide's built-in package list** (checked on the stable docs page, Pyodide 314.0.8; nor are its compiled deps `thinc`, `blis`, `cymem`, `preshed`, `murmurhash`, `srsly`). The long-open request [pyodide/pyodide-recipes#179](https://github.com/pyodide/pyodide-recipes/issues/179) (opened 2020, still open) reports `cython-blis` failing on WASM (`unknown FP unit 'sse'`) and earlier attempts ([pyodide/pyodide#368](https://github.com/pyodide/pyodide/pull/368), #734, #4108) were closed without merging. A community demo (`SyedAhkam/spacy-wasm`) exists but is unofficial.
- **Conclusion:** run spaCy in **Python at build time**, not in the browser and not in Netlify Functions. Details in [04-netlify-deployment.md](04-netlify-deployment.md).

## Sources

- spaCy English models: https://spacy.io/models/en
- spaCy linguistic features (NER, noun chunks, dependency parse): https://spacy.io/usage/linguistic-features
- Pyodide package list: https://pyodide.org/en/stable/usage/packages-in-pyodide.html
- spaCy-in-Pyodide request: https://github.com/pyodide/pyodide-recipes/issues/179
