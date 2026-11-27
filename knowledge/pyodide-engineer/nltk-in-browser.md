# Project recipe — "Analyze your own review"

Derived from the other notes in this folder and https://www.nltk.org/data.html.

1. User opens the panel → main thread creates `new Worker("/js/analyzer.worker.mjs", { type: "module" })`.
2. Worker: `loadPyodide({ indexURL: "/pyodide/" })` → `loadPackage("nltk")` → fetch `vader_lexicon.zip` (and `punkt_tab` if `sent_tokenize` is used) into `/nltk_data` → set `nltk.data.path`.
3. Worker runs the same `analyze.py` that ships in `site/py/analyze.py` and is **generated from / tested against** `pipeline/nlp_nltk.py` (same lexicon overrides, same aspect keyword lists, same ±0.05 thresholds).
4. Input is passed as data; output is JSON: `{compound, label, sentences: [{text, compound, aspects: [...]}], aspects: {visuals: {...}, ...}}`.
5. Show a progress state while Pyodide loads (first load is several MB); keep the main dashboard usable throughout.

Limits to state in the UI: no spaCy in the browser, so aspect detection here is keyword-based (lemma/phrase lists), not dependency-based like the build-time results.
