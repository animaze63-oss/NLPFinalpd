---
name: netlify-configuration
description: "Configure netlify.toml, requirements.txt and the Python build on Netlify. Use when setting up or changing the build command, publish directory, Python version, redirects or environment."
---

# netlify-configuration

Used by: **netlify-engineer** (owner), pipeline-engineer, orchestrator

- `[build] command` downloads NLTK data then runs `python pipeline/build_data.py`; `publish = "site"`.
- `[build.environment] PYTHON_VERSION = "3.12"`; `requirements.txt` at the base dir is auto-installed with pip.
- `[[redirects]] from = "/film/*" to = "/index.html" status = 200`.
- netlify.toml overrides UI settings. No `netlify/functions` or edge functions.

Reference: `knowledge/netlify-engineer/netlify-toml.md`, `knowledge/netlify-engineer/build-image-and-python.md`.
