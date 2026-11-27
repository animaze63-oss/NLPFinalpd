# File system

Source: https://pyodide.org/en/stable/usage/file-system.html

- `pyodide.FS` re-exports the Emscripten File System API.
- Default FS is **MEMFS** — "a virtual in-memory file system. The data stored in MEMFS will be lost when the page is reloaded."
- Persistent options: `IDBFS` (browser IndexedDB), `NODEFS` (Node only), `WORKERFS`, experimental `mountNativeFS` (Chromium only).

```js
pyodide.FS.writeFile("/hello.txt", "hello world!", { encoding: "utf8" });
let file = pyodide.FS.readFile("/hello.txt", { encoding: "utf8" });
pyodide.FS.mkdirTree("/mnt");
pyodide.FS.mount(pyodide.FS.filesystems.IDBFS, {}, "/mnt");
```

## Project recipe: put `vader_lexicon.zip` where NLTK looks
```js
const buf = new Uint8Array(await (await fetch("/nltk_data/sentiment/vader_lexicon.zip")).arrayBuffer());
pyodide.FS.mkdirTree("/nltk_data/sentiment");
pyodide.FS.writeFile("/nltk_data/sentiment/vader_lexicon.zip", buf);
pyodide.runPython(`import nltk; nltk.data.path.insert(0, "/nltk_data")`);
```
NLTK reads the zip directly (`sentiment/vader_lexicon.zip/vader_lexicon/vader_lexicon.txt`), so no unzip is needed. MEMFS is fine — the file is re-fetched (browser-cached) on each visit.
