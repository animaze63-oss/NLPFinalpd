# Knowledge — Pyodide Engineer

Reference notes from the official Pyodide documentation (pyodide.org, stable = **314.0.8**), retrieved 2026-11-27.
Read every file before answering. Re-check the version pin in `deploying.md` before changing it.

| File | Topic | Source |
|---|---|---|
| [quickstart.md](quickstart.md) | Script tag, `loadPyodide`, `runPython`, globals | https://pyodide.org/en/stable/usage/quickstart.html |
| [loading-packages.md](loading-packages.md) | `loadPackage` vs `micropip`, NLTK availability | https://pyodide.org/en/stable/usage/loading-packages.html, https://pyodide.org/en/stable/usage/packages-in-pyodide.html |
| [webworker.md](webworker.md) | Module worker pattern | https://pyodide.org/en/stable/usage/webworker.html |
| [file-system.md](file-system.md) | `pyodide.FS`, MEMFS, mounting NLTK data | https://pyodide.org/en/stable/usage/file-system.html |
| [deploying.md](deploying.md) | CDN vs self-hosting, required files | https://pyodide.org/en/stable/usage/downloading-and-deploying.html |
| [nltk-in-browser.md](nltk-in-browser.md) | Project recipe: VADER in a worker | derived from the above + https://www.nltk.org/data.html |

Project context: ../../docs/04-netlify-deployment.md §4
