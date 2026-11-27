# Build image and Python

Sources:
- https://docs.netlify.com/build/configure-builds/available-software-at-build-time/
- https://docs.netlify.com/build/configure-builds/manage-dependencies/
- https://www.netlify.com/blog/announcing-configurable-python-versions-in-netlify-builds

> "Our current build is based on Ubuntu version 24.04 (also called Noble Numbat)."

| Language/tool | Default | Available | Set with |
|---|---|---|---|
| Python | 3.x | Any official Python version | `PYTHON_VERSION` env var, `Pipfile`, or `runtime.txt` |
| pip | matches installed Python | | |
| Pipenv | latest | | |
| Node.js | 24 | anything `nvm` installs | `.nvmrc`, `.node-version`, `NODE_VERSION` |
| Deno | 1.x | | |

- > "The default Python version is determined by the site's selected build image." → always pin it.
- `runtime.txt`: "The file must include the version number only: `x.y`, with no trailing newline."
- Dependencies: a `requirements.txt` in the **base directory** "creates a requirements.txt file that Netlify will use to install your dependencies by running pip install." `Pipfile` → `pipenv install` (commit `Pipfile.lock` for exact versions).

## Project settings
```toml
[build.environment]
  PYTHON_VERSION = "3.12"
```
`requirements.txt` (repo root = base dir): `nltk`, `spacy>=3.8,<3.9`, `pandas`, and the `en_core_web_sm` 3.8.0 wheel URL. Pin exact versions once the pipeline works.
