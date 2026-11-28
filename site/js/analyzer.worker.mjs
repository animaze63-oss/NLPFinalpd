// Module Web Worker: Pyodide 314.0.8 + NLTK, self-hosted under /pyodide/v314.0.8/ (no CDN).
// Owner: pyodide-engineer. Runs the SAME Python file as the build (pipeline/analyze_text.py,
// copied to /py/analyze_text.py) with the SAME lexicon (/data/lexicon.json) -> parity.
// User text arrives as data (postMessage) and is passed to Python as a variable, never
// interpolated into code. Nothing is sent over the network except fetching these static files.
import { loadPyodide } from "/pyodide/v314.0.8/pyodide.mjs";

const progress = (stage, detail) => self.postMessage({ type: "progress", stage, detail });

async function fetchOk(url, as = "text") {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
  return as === "buffer" ? r.arrayBuffer() : r.text();
}

const ready = (async () => {
  const t0 = performance.now();
  progress("runtime", "Starting Python (Pyodide)…");
  const py = await loadPyodide({ indexURL: "/pyodide/v314.0.8/" });
  progress("packages", "Loading NLTK…");
  await py.loadPackage("nltk", { messageCallback: () => {}, errorCallback: (m) => console.warn(m) });
  progress("data", "Loading the VADER lexicon and tokenizer data…");
  const [zip, code, lexicon] = await Promise.all([
    fetchOk("/nltk_data/browser-nltk-data.zip", "buffer"),
    fetchOk("/py/analyze_text.py"),
    fetchOk("/data/lexicon.json"),
  ]);
  py.FS.mkdirTree("/home/pyodide/nltk_data");
  py.unpackArchive(zip, "zip", { extractDir: "/home/pyodide/nltk_data" });
  py.FS.writeFile("/home/pyodide/analyze_text.py", code);
  py.globals.set("LEXICON_JSON", lexicon);
  py.runPython(`
import sys, json
sys.path.insert(0, "/home/pyodide")
import nltk
nltk.data.path.insert(0, "/home/pyodide/nltk_data")
import analyze_text
LEX = json.loads(LEXICON_JSON)
SIA = analyze_text.make_analyzer(LEX)
NLTK_VERSION = nltk.__version__
PY_VERSION = sys.version.split()[0]
`);
  const info = { nltk: py.globals.get("NLTK_VERSION"), python: py.globals.get("PY_VERSION"), ms: Math.round(performance.now() - t0) };
  self.postMessage({ type: "ready", info });
  return py;
})();
ready.catch((e) => self.postMessage({ type: "error", error: String(e && e.message ? e.message : e) }));

self.onmessage = async (event) => {
  const { id, text } = event.data || {};
  try {
    const py = await ready;
    py.globals.set("USER_TEXT", String(text ?? ""));
    const out = py.runPython("json.dumps(analyze_text.analyze(USER_TEXT, LEX, SIA))");
    py.globals.delete("USER_TEXT");
    self.postMessage({ type: "result", id, result: JSON.parse(out) });
  } catch (e) {
    self.postMessage({ type: "error", id, error: String(e && e.message ? e.message : e) });
  }
};
