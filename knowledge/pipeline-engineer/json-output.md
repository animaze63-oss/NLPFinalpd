# Writing JSON (Python `json`)

Source: https://docs.python.org/3/library/json.html

- `separators=(',', ':')` — "For the most compact JSON… eliminate whitespace." Use for everything in `site/data/`.
- `ensure_ascii=False` — keep non-ASCII as-is (critic names, accents). Files must then be written with `encoding="utf-8"`.
- `allow_nan` — default `True` writes `NaN`/`Infinity`, which **are not valid JSON** and break `response.json()` in browsers. Always pass `allow_nan=False` and replace NaN with `None` first.
- `sort_keys=True` — stable diffs between builds.
- `indent=None` (default) — no newlines.
- `default=` — hook for non-serialisable values (e.g. numpy ints → `int`).
- Conversion: dict → object, list/tuple → array, str → string, int/float → number, True/False → true/false, None → null.

```python
def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True,
                  allow_nan=False, default=lambda o: o.item() if hasattr(o, "item") else str(o))
```
Round floats (3 decimals) before dumping to keep files small.
