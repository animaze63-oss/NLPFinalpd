# Downloading and deploying

Source: https://pyodide.org/en/stable/usage/downloading-and-deploying.html

- Current stable: **314.0.8**. CDN base: `https://cdn.jsdelivr.net/pyodide/v314.0.8/full/` — the version in the path is the pin.
- Full distribution (`pyodide-314.0.8.tar.bz2`) "includes all vendored packages and is quite large (200+ megabytes)".
- Core distribution (`pyodide-core-314.0.8.tar.bz2`): the minimal files to start — `pyodide.js`, `pyodide.mjs`, `pyodide.asm.mjs`, `pyodide.asm.wasm`, `python_stdlib.zip`, `pyodide-lock.json`, `package.json`.
- Self-hosting requires a server that "correctly sets the WASM MIME type" (`application/wasm`).

## Options on Netlify (no outside servers)
1. **Recommended:** self-host the core files plus the nltk and regex wheels under `site/pyodide/` and call `loadPyodide({ indexURL: "/pyodide/" })`. Everything is served by Netlify; set `Content-Type: application/wasm` and long `Cache-Control` in `netlify.toml` if the defaults are wrong.
2. Load from jsDelivr: zero setup but depends on a third-party CDN at runtime. Use only as a documented fallback — confirm with the Orchestrator, because the decision record says no outside servers.
