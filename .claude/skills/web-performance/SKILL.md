---
name: web-performance
description: "Keep page weight, JSON size and Pyodide cost under budget. Use when adding assets, charts or data, or when Lighthouse scores drop."
---

# web-performance

Used by: **frontend-engineer** (owner), pyodide-engineer, netlify-engineer, qa-engineer

- Budgets: initial HTML+CSS+JS < 200 KB gzipped (excluding Pyodide); `films.json` < 50 KB; per-film JSON < 150 KB.
- Pyodide only after user action; cache it with long immutable headers.
- Defer non-critical JS; lazy-render below-the-fold charts.
- Check with Lighthouse on the Deploy Preview.
