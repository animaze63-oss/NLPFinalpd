# Pyodide in a Web Worker

Source: https://pyodide.org/en/stable/usage/webworker.html

> "Pyodide requires a module-type worker because `pyodide.asm.mjs` is an ES module. Classic workers using `importScripts()` are not supported."
> "Running them in the main thread blocks the UI… a worker cannot directly manipulate the DOM."

```js
// webworker.mjs
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs";
let pyodideReadyPromise = loadPyodide();
self.onmessage = async (event) => {
  const pyodide = await pyodideReadyPromise;
  const { id, python, context } = event.data;
  await pyodide.loadPackagesFromImports(python);
  const dict = pyodide.globals.get("dict");
  const globals = dict(Object.entries(context));
  try {
    const result = await pyodide.runPythonAsync(python, { globals });
    self.postMessage({ result, id });
  } catch (error) {
    self.postMessage({ error: error.message, id });
  }
};
```
```js
// workerApi.mjs — request/response by id
const pyodideWorker = new Worker("./webworker.mjs", { type: "module" });
export function asyncRun(script, context) { return requestResponse(pyodideWorker, { context, python: script }); }
```
(`requestResponse` adds a unique id, posts the message, and resolves when a reply with the same id arrives.)

## Project rules
- Create the worker only when the user opens "Analyze your own review" (lazy load).
- Don't send arbitrary Python from the UI: the worker should expose one fixed `analyze(text)` function; pass the user's text as data (`context`), never string-interpolate it into code.
- Return plain JSON (convert with `.toJs({dict_converter: Object.fromEntries})` or `json.dumps` in Python).
