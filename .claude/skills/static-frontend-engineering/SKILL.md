---
name: static-frontend-engineering
description: "Build the static dashboard with HTML, CSS and vanilla JS that reads the generated JSON. Use for pages, routing, components and rendering logic in site/."
---

# static-frontend-engineering

Used by: **frontend-engineer** (owner), pyodide-engineer, ux-designer

- No framework required; ES modules; `fetch` JSON with `response.ok` checks and `AbortController` on film switch.
- Routes: `/` and `/film/<slug>` (history API + Netlify 200 rewrite to `/index.html`).
- Mobile-first, 16 px gutters, no horizontal scroll at 360 px.
- Vendor libraries are self-hosted in `site/vendor/` with pinned versions.

Reference: `knowledge/frontend-engineer/static-architecture.md`, `knowledge/frontend-engineer/fetch-json.md`.
