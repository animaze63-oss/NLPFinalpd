# Loading packages

Sources: https://pyodide.org/en/stable/usage/loading-packages.html, https://pyodide.org/en/stable/usage/packages-in-pyodide.html

> "Only the Python standard library is available after importing Pyodide."

Two loaders:
- `micropip.install()` (Python) — pure-Python wheels from PyPI, plus Pyodide packages and wasm32/emscripten wheels from the jsDelivr CDN or custom URLs. Async: `await micropip.install(...)`. Verifies hashes from the PyPI JSON API. `index_urls=` for other indexes; `deps=False` to skip dependency resolution.
- `pyodide.loadPackage()` (JS) — "for packages built with Pyodide… less overhead but also more limited functionality." Official-repo packages load **with their dependencies**; custom-URL wheels get **no dependency resolution**.

Advice from the docs: use micropip for everything **except** to load micropip itself, or "when you are optimizing for size, do not want to install the micropip package, and do not need to install packages from PyPI".

```js
await pyodide.loadPackage("nltk");                 // built-in → also pulls its deps (e.g. regex)
await pyodide.loadPackage(["cycler", "pytz"]);     // several at once
await pyodide.loadPackage("https://host/pkg-1.0-py3-none-any.whl");   // must be a valid wheel name
```
- `pyodide.loadPackagesFromImports(code)` downloads packages a snippet imports — only from the Pyodide distribution, never PyPI.
- Loading a package twice is not permitted.
- Remote wheels need CORS headers; avoid third-party CORS proxies (no integrity check).

## Built-in package facts relevant to us (stable 314.0.8)
| Package | In Pyodide? | Version |
|---|---|---|
| nltk | ✅ | 3.9.4 |
| regex | ✅ | 2026.3.32 |
| numpy / pandas / scikit-learn | ✅ | 2.4.6 / 3.0.2 / 1.8.0 |
| spacy, thinc, blis, srsly, cymem, preshed, murmurhash | ❌ | — |

**Decision for this project:** `loadPackage("nltk")` (no micropip — smaller download). spaCy is never attempted in the browser.
