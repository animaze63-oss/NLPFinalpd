---
name: accessibility-lighthouse-audits
description: "Run automated accessibility (axe) and Lighthouse audits plus a manual keyboard pass. Use before approving any UI PR or release."
---

# accessibility-lighthouse-audits

Used by: **qa-engineer** (owner), ux-designer, frontend-engineer

- axe via `@axe-core/playwright` with tags wcag2a, wcag2aa, wcag21a, wcag21aa; expect zero violations on home, film page and analyzer, in dark and light.
- Lighthouse on the Deploy Preview: record performance, accessibility, best-practices scores.
- Manual: keyboard-only walkthrough, focus visibility, screen-reader names on charts.
- Automated tools can't find everything — report manual findings separately.

Reference: `knowledge/qa-engineer/accessibility-testing.md`, `knowledge/ux-designer/wcag22.md`.
