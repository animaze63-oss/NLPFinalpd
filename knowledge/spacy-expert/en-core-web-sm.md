# en_core_web_sm

Source: https://spacy.io/models/en

| | en_core_web_sm | en_core_web_md |
|---|---|---|
| Latest version | 3.8.0 | 3.8.0 |
| Package size | 12 MB | 31 MB |
| Pipeline | tok2vec, tagger, parser, attribute_ruler, lemmatizer, ner | same + vectors |
| NER F (`ENTS_F`) | 0.84 | 0.85 |
| Dependency LAS | 0.90 | 0.90 |

NER labels (OntoNotes): `CARDINAL, DATE, EVENT, FAC, GPE, LANGUAGE, LAW, LOC, MONEY, NORP, ORDINAL, ORG, PERCENT, PERSON, PRODUCT, QUANTITY, TIME, WORK_OF_ART`.

## Install so Netlify's automatic `pip install -r requirements.txt` gets it
```
spacy>=3.8,<3.9
en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```
Local alternative: `python -m spacy download en_core_web_sm`. Model version must match the spaCy minor version (3.8.x ↔ 3.8.0).

## Project choice
Use `_sm`: near-identical accuracy, fastest build. Trained on news/web text, so fictional names (Arrakis, HAL 9000) may be mislabelled — patch with an EntityRuler seeded from dataset metadata.
