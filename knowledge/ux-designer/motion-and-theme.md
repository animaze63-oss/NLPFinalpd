# Motion and theme (design rules)

Sources: MDN prefers-reduced-motion and prefers-color-scheme (links in README).

- `prefers-reduced-motion: reduce` → no parallax, no animated counters, no auto-playing hero motion; use fades ≤ 150 ms or none.
- `prefers-color-scheme` → dark-first "theater" palette, plus a complete light palette. A manual toggle (`data-theme`) overrides the OS setting.
- Set `color-scheme: dark light` so form controls and scrollbars match.
- Embedded SVG (displaCy) inherits `color-scheme` from its parent when used as `<img>`; inline SVG needs explicit theme colours.
