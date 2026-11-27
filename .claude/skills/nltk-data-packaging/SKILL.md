---
name: nltk-data-packaging
description: "Download and ship NLTK data (punkt_tab, stopwords, vader_lexicon) for the Netlify build and for Pyodide. Use when NLTK raises LookupError or when changing which NLTK resources the app needs."
---

# nltk-data-packaging

Used by: **nltk-expert** (owner), pyodide-engineer, netlify-engineer

- Build: `python -m nltk.downloader -d ./nltk_data punkt_tab stopwords vader_lexicon` then `NLTK_DATA=./nltk_data` (in the netlify.toml build command). Don't commit `nltk_data/`.
- Browser: copy `nltk_data/sentiment/vader_lexicon.zip` (and `tokenizers/punkt_tab` if used) into `site/nltk_data/` during the build; Pyodide writes them into its FS and adds the path to `nltk.data.path`.
- Never download `all` or `book`.

Reference: `knowledge/nltk-expert/data-downloads.md`, `knowledge/pyodide-engineer/file-system.md`.
