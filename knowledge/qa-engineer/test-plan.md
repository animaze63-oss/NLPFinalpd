# Test plan

| Layer | Tests | Tool |
|---|---|---|
| NLTK module | VADER reference sentences (../nltk-expert/vader.md) reproduce; lexicon overrides applied; tokenizer keeps negators | pytest |
| spaCy module | aspect↔opinion extraction on fixed sentences (amod, acomp, conj, neg, compound); EntityRuler hits | pytest |
| Pipeline | end-to-end on a 50-review fixture → files written; every JSON validates against `schemas/`; no NaN; size limits | pytest + jsonschema |
| Parity | build `analyze` vs Pyodide `analyze` on 50 sentences: same compound (3 dp) | pytest + Playwright |
| Frontend | picker → dashboard, deep link `/film/<slug>`, empty/error states, 360 px width without horizontal scroll | Playwright |
| Pyodide | panel lazy-loads, shows progress, returns a score, UI stays responsive | Playwright |
| A11y | axe on home, film page, analyzer; dark + light | @axe-core/playwright |
| Perf | Lighthouse on Deploy Preview; JSON and page weight budgets | Lighthouse CLI |
| Deploy | Deploy Preview build passes; headers correct (`curl -I`) | Netlify |
