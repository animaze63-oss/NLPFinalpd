# displaCy (static visualizations)

Source: https://spacy.io/usage/visualizers

- `displacy.serve` "will spin up a simple web server" — **never use it** (no servers on Netlify).
- `displacy.render` "returns a string containing the markup" — use this at build time and write files into `site/`.
- Styles: `dep` (POS tags and dependencies), `ent` (entities and labels), `span` (overlapping spans).
- Options: dep → `compact`, `color`, `bg`, `font`, `offset_x`; ent/span → `ents` (types to highlight), `colors` (label → color).
- `page=True` wraps the markup as a full HTML page; `jupyter=False` forces raw markup outside notebooks.

```python
from pathlib import Path
from spacy import displacy
svg = displacy.render(doc, style="dep", jupyter=False, options={"compact": True})
Path("site/assets/displacy/example-1.svg").write_text(svg, encoding="utf-8")
html = displacy.render(doc, style="ent", jupyter=False,
                       options={"ents": ["PERSON", "WORK_OF_ART", "ORG"], "colors": {"WORK_OF_ART": "#7c5cff"}})
```
Project use: pre-render 2–3 example review sentences for the "How the NLP works" panel. Check the SVG colours against the dark theme with the UX designer.
