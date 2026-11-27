# Theming and motion

Sources:
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-color-scheme
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion

## prefers-color-scheme
- Values: `light` ("prefer… a light theme, or has not expressed an active preference"), `dark`.
- Baseline widely available since January 2020.
- Related: the `color-scheme` CSS property and `<meta name="color-scheme">`. Embedded SVGs (`<img src=…svg>`) inherit the parent's `color-scheme`.
```css
:root { --bg:#0b0d12; --fg:#e9ecf2; --accent:#7c5cff; color-scheme: dark light; }
@media (prefers-color-scheme: light) { :root:not([data-theme="dark"]) { --bg:#f7f7fb; --fg:#151821; } }
:root[data-theme="light"] { --bg:#f7f7fb; --fg:#151821; }
body { background: var(--bg); color: var(--fg); }
```
(The cinematic design is dark-first; light must still be fully supported.)

## prefers-reduced-motion
- Values: `no-preference`, `reduce` ("user has enabled the setting on their device for reduced motion").
- OS settings it maps to: macOS Accessibility › Reduce motion; Windows 11 Accessibility › Visual effects › Animation effects; iOS Accessibility › Motion; Android 9+ Remove animations.
```css
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }
```
JS: `matchMedia('(prefers-reduced-motion: reduce)').matches` before starting chart/hero animations.
