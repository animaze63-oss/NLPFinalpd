# Kaggle CLI

Sources: https://github.com/Kaggle/kaggle-cli/blob/main/docs/README.md, https://github.com/Kaggle/kaggle-cli/blob/main/docs/datasets.md

Install: `pipx install kaggle` (or `uv tool install kaggle`, or `pip install kaggle`).

Authentication (any one):
1. `kaggle auth login` (OAuth)
2. `export KAGGLE_API_TOKEN=...`
3. token file `~/.kaggle/access_token`
4. legacy `~/.kaggle/kaggle.json`

Never commit tokens. Never run the download on Netlify (it needs credentials) — run it locally and commit only the filtered subset.

```bash
kaggle datasets download <owner/dataset-name>[/version] [-f FILE] [-p PATH] [--unzip] [-o] [-q]
kaggle datasets download -d stefanoleone992/rotten-tomatoes-movies-and-critic-reviews-dataset -p raw/ --unzip
```
- `-f` one file only; `-p` target folder; `--unzip` extracts and deletes the zip; `-o/--force` overwrite; `-q` quiet.
- Pin a version with `owner/name/<version>` for reproducibility and record it in `data/README.md`.
- Keep `raw/` in `.gitignore`.
