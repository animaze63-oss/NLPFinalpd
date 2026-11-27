# Quickstart

Source: https://pyodide.org/en/stable/usage/quickstart.html

```html
<script src="https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.js"></script>
<script>
  async function main() {
    let pyodide = await loadPyodide();
    pyodide.runPython(`
      import sys
      sys.version
    `);
  }
  main();
</script>
```
- `loadPyodide()` returns a promise for the runtime; await it once and reuse the instance.
- `pyodide.runPython(code)` runs synchronously and returns the last expression; `pyodide.runPythonAsync(code, { globals })` allows top-level `await` (used in the worker example).
- Read Python values from JS: `pyodide.globals.get('x').toJs()` — `toJs()` converts a PyProxy (dict/list) into JS Map/Array. Call `.destroy()` on PyProxies you no longer need to avoid leaks.
- ES-module alternative: `import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs"`.
