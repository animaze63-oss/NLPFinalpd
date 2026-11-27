# Team workflow

## Phases and order
1. **Design** — UX (wireframes, tokens) ∥ DATA (film list, subset CSV) ∥ NLTK + SPACY (module APIs, aspect lexicon) → PIPE (contract v1) → ORC approves.
2. **Build** — NLTK + SPACY modules → PIPE `build_data.py` + schemas → FE dashboard ∥ PYO analyzer → NET `netlify.toml`.
3. **Test** — QA (pytest, Playwright, axe, Lighthouse) ∥ EVAL (metrics, methodology) → fixes routed back to owners.
4. **Deploy** — NET Deploy Preview → QA sign-off → merge to `main` → production → EVAL final report.
META runs a short retrospective after each phase and updates agents/skills/knowledge.

## Hand-off format (ask every agent to end with this)
```
DONE: <what was produced, file paths>
CONTRACT: <data contract version touched, or "none">
TESTS: <what was run and the result>
OPEN: <risks, questions, blockers>
NEXT: <who should act next and on what>
```

## Definition of done
- Code in the right folder, tests pass, JSON validates, Deploy Preview builds, axe has no violations, decision record respected, docs updated.
