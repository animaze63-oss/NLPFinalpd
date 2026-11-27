---
name: static-hosting-headers
description: "Set cache, MIME and security headers for static files on Netlify. Use when adding Pyodide/WASM assets, data files, or when caching behaves wrongly."
---

# static-hosting-headers

Used by: **netlify-engineer** (owner), pyodide-engineer, frontend-engineer

- `/pyodide/*`: `Cache-Control: public, max-age=31536000, immutable` (path is versioned).
- `/data/*`: short cache (`max-age=300, must-revalidate`).
- `*.wasm`: `Content-Type: application/wasm`.
- `/*`: `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`.
- Headers are global (not per deploy context) and don't apply to function responses. Verify with `curl -I` on the preview.

Reference: `knowledge/netlify-engineer/headers.md`.
