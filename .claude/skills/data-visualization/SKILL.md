---
name: data-visualization
description: "Draw the dashboard's charts (aspect scores, praise vs criticism words, collocations, timeline) clearly and accessibly. Use when choosing or implementing a chart."
---

# data-visualization

Used by: **frontend-engineer** (owner), ux-designer, nlp-evaluator

- Bar (diverging, zero baseline) for aspect means with mention counts; line for timeline; ranked horizontal bars for words/phrases; avoid pie except pos/neu/neg share.
- Show n (mentions/reviews) next to every score; grey out aspects with < 10 mentions.
- Chart.js self-hosted; canvas gets `role="img"` + `aria-label`; provide a data table.
- Use the design tokens for colours in both themes.

Reference: `knowledge/frontend-engineer/chartjs.md`.
