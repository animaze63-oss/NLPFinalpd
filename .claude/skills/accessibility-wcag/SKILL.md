---
name: accessibility-wcag
description: "Make the dashboard meet WCAG 2.2 AA (contrast, keyboard, focus, charts with text alternatives, status messages). Use when designing or building any UI."
---

# accessibility-wcag

Used by: **ux-designer** (owner), frontend-engineer, pyodide-engineer, qa-engineer

- Text contrast ≥ 4.5:1; UI/graphics ≥ 3:1; targets ≥ 24×24 px; visible focus never hidden by sticky headers.
- Every chart: `role="img"` + `aria-label` and a data table alternative.
- Everything works by keyboard; the custom picker exposes name/role/value.
- Loading and analyzer results use a live region (`role="status"`).
- Honour `prefers-reduced-motion` and `prefers-color-scheme`.

Reference: `knowledge/ux-designer/wcag22.md`, `knowledge/frontend-engineer/chartjs.md`.
