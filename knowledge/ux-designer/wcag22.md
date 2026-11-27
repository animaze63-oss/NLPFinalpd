# WCAG 2.2 criteria for Scifi Cinema Lens

Source: https://www.w3.org/WAI/WCAG22/quickref/ — target level **AA**.

| SC | Level | Requirement (quickref wording, shortened) | Applies to |
|---|---|---|---|
| 1.1.1 Non-text Content | A | Non-text content has a text alternative that serves the equivalent purpose | charts, posters, displaCy SVGs |
| 1.3.1 Info and Relationships | A | Structure conveyed visually is programmatically determinable | headings, tables, cards |
| 1.4.1 Use of Color | A | Colour is not the only means of conveying information | praise (green) vs criticism (red) — add icons/labels/patterns |
| 1.4.3 Contrast (Minimum) | AA | Text contrast ≥ 4.5:1 | dark theme text on near-black |
| 1.4.10 Reflow | AA | No two-dimensional scrolling (320 CSS px) | phone layout |
| 1.4.11 Non-text Contrast | AA | UI components and graphics ≥ 3:1 against adjacent colours | bars, focus rings, chart lines |
| 1.4.12 Text Spacing | AA | No loss of content when spacing is increased | quotes, cards |
| 2.1.1 Keyboard | A | All functionality operable by keyboard | picker, tabs, analyzer |
| 2.2.2 Pause, Stop, Hide | A | Moving/auto-updating content can be paused | hero animation, marquee |
| 2.3.3 Animation from Interactions | AAA (not required, but we honour `prefers-reduced-motion`) | Motion triggered by interaction can be disabled | transitions |
| 2.4.3 Focus Order | A | Focus order preserves meaning | panels |
| 2.4.7 Focus Visible | AA | Keyboard focus indicator is visible | all controls |
| 2.4.11 Focus Not Obscured (Minimum) | AA | Focused component not entirely hidden by author content | sticky header |
| 2.5.8 Target Size (Minimum) | AA | Pointer targets ≥ 24×24 CSS px | chips, tabs |
| 4.1.2 Name, Role, Value | A | Components expose name, role, state | custom picker |
| 4.1.3 Status Messages | AA | Status messages announced without focus | "Loading Python…", analyzer result |

Note: 2.3.3 is Level AAA in WCAG 2.2, so it is a stretch goal for us; we still honour `prefers-reduced-motion`.
