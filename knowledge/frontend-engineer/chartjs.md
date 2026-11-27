# Chart.js

Sources: https://www.chartjs.org/docs/latest/getting-started/, https://www.chartjs.org/docs/latest/general/accessibility.html

```html
<div><canvas id="aspects" role="img" aria-label="Average sentiment by aspect"></canvas></div>
<script src="/vendor/chart.umd.min.js"></script>   <!-- self-hosted copy, version-pinned -->
<script>
  new Chart(document.getElementById('aspects'), {
    type: 'bar',
    data: { labels: ['Visuals','Story','Characters','Soundtrack'],
            datasets: [{ label: 'Mean compound', data: [0.62, 0.11, 0.25, 0.48], borderWidth: 1 }] },
    options: { scales: { y: { beginAtZero: true, min: -1, max: 1 } } }
  });
</script>
```
- The docs' quick start loads `https://cdn.jsdelivr.net/npm/chart.js`; **we self-host** a pinned file under `site/vendor/` (no outside servers at runtime) or bundle it from npm at build.
- "It's recommended to give the chart its own container for responsiveness."
- Types we use: `bar` (aspect scores, diverging), `line` (timeline), `radar` (aspect profile, optional), `doughnut` (pos/neu/neg).

## Accessibility (from the Chart.js docs)
> "the `canvas` content will not be accessible to screen readers… accessibility has to be added with ARIA attributes on the `canvas` element or added using internal fallback content."
- Good: `<canvas role="img" aria-label="…">` or meaningful fallback content inside `<canvas>…</canvas>`.
- Bad: no name/role, or fallback like "Your browser does not support the canvas element."
- Project rule: every chart also has a visually-hidden or toggleable data table with the same numbers.
