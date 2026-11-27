# jsonschema

Source: https://python-jsonschema.readthedocs.io/en/stable/ (v4.26)

```bash
pip install jsonschema
```
```python
from jsonschema import validate, Draft202012Validator, ValidationError
validate(instance=film_json, schema=FILM_SCHEMA)        # raises ValidationError: "'Invalid' is not of type 'number'"
v = Draft202012Validator(FILM_SCHEMA)
errors = sorted(v.iter_errors(film_json), key=lambda e: e.path)   # lazily reports *all* errors
```
- Full Draft 2020-12 support. Keep schemas in `schemas/*.schema.json` with `"$schema": "https://json-schema.org/draft/2020-12/schema"`.
- The build fails if any generated file fails validation (exit code 1) — a broken contract must never deploy.
