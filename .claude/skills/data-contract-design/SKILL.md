---
name: data-contract-design
description: "Design and version the JSON contract between the build pipeline and the frontend/Pyodide code. Use before adding, renaming or removing any field in site/data/."
---

# data-contract-design

Used by: **pipeline-engineer** (owner), frontend-engineer, pyodide-engineer, qa-engineer, orchestrator

- Contract = JSON Schema files in `schemas/` + the table in `knowledge/pipeline-engineer/data-contract.md`.
- Every file carries `schema_version`. Additive change → minor bump; rename/remove → major bump and Orchestrator approval.
- Frontend reads only documented fields and tolerates missing optional ones.
- Announce changes in the hand-off `CONTRACT:` line.

Reference: `knowledge/pipeline-engineer/jsonschema.md`.
