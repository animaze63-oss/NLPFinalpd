# Processing pipelines

Source: https://spacy.io/usage/processing-pipelines

> "`spacy.load` puts this all together and returns an instance of `Language` with a pipeline set and access to the binary data."

What `spacy.load` does internally: get the Language class (`spacy.util.get_lang_class("en")`), initialise it, `add_pipe` each component from the config, then `nlp.from_disk(data_path)`.

| Component | Creates |
|---|---|
| tokenizer | `Doc` |
| tagger | `Token.tag` |
| parser | `Token.head`, `Token.dep`, `Doc.sents`, `Doc.noun_chunks` |
| ner | `Doc.ents`, `Token.ent_iob`, `Token.ent_type` |
| lemmatizer | `Token.lemma` |

```python
print(nlp.pipe_names)
# ['tok2vec', 'tagger', 'parser', 'ner', 'attribute_ruler', 'lemmatizer']
```
Note the lemmatizer depends on `attribute_ruler`/tagger output; disabling the tagger degrades lemmas.

## Batch processing
> "spaCy's `nlp.pipe` method takes an iterable of texts and yields processed `Doc` objects. The batching is done internally."
> "When processing large volumes of text, the statistical models are usually more efficient if you let them work on batches of texts."

```python
docs = list(nlp.pipe(texts))
docs = nlp.pipe(texts, n_process=2, batch_size=2000)   # default batch size is nlp.batch_size (typically 1000)
for doc, ctx in nlp.pipe(((text, meta) for ...), as_tuples=True):   # keep review metadata with each doc
    ...
```
> "For shorter tasks and in particular with `spawn`, it can be faster to use a smaller number of processes with a larger batch size."

## Disable vs exclude
> "**Disable:** The component and its data will be loaded with the pipeline, but it will be disabled by default and not run."
> "**Exclude:** Don't load the component and its data with the pipeline."

```python
nlp = spacy.load("en_core_web_sm", exclude=["ner"])
nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser"]); nlp.enable_pipe("tagger")
with nlp.select_pipes(disable=["ner"]):
    doc = nlp("...")
for doc in nlp.pipe(texts, disable=["ner"]): ...
```

## Adding components
`nlp.add_pipe(name, before=..., after=..., first=True, last=True)` — `last=True` is the default.
```python
ruler = nlp.add_pipe("entity_ruler", before="ner")
```

## Project rules
- Use `nlp.pipe(..., as_tuples=True, batch_size=256–1000)` over all reviews; never call `nlp()` in a Python loop over 10k+ texts.
- Keep every component: we need parser (deps, sents, noun_chunks), ner and lemmatizer.
- `n_process>1` only if the Netlify build is proven faster with it (check build minutes).
