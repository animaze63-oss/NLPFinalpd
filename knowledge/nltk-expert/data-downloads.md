# Installing NLTK data

Source: https://www.nltk.org/data.html

- Full list of packages: https://www.nltk.org/nltk_data/
- Collections: `all`, `book`, `all-corpora` — never download these in CI; fetch only what we use.
- Command line: `python -m nltk.downloader all`; `-d DIR` chooses the location — "be sure to set the `NLTK_DATA` environment variable accordingly".
- Default search locations: `/usr/share/nltk_data`, `/usr/local/share/nltk_data` (Unix), `C:\nltk_data` (Windows), or the user's home.
- Proxy: `nltk.set_proxy('http://proxy.example.com:3128', ('USERNAME', 'PASSWORD'))`.
- Manual install: create `nltk_data/` with subfolders `chunkers, grammars, misc, sentiment, taggers, corpora, help, models, stemmers, tokenizers`; download zips from `https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/...` and unzip into the matching subfolder (e.g. `corpora/brown.zip` → `nltk_data/corpora/brown`).

## Project commands
```bash
python -m nltk.downloader -d ./nltk_data punkt_tab stopwords vader_lexicon
export NLTK_DATA=./nltk_data
```
For Pyodide: copy `nltk_data/sentiment/vader_lexicon.zip` (and `tokenizers/punkt_tab` if used) into `site/nltk_data/` so the browser can fetch them; NLTK reads `vader_lexicon.zip` directly without unzipping.
