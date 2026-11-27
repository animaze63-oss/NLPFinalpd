---
name: spacy-ner-entityruler
description: "Extract named entities (people, compared films, studios) with spaCy NER plus an EntityRuler seeded from film metadata. Use when building the 'people & comparisons' data or fixing mislabelled names."
---

# spacy-ner-entityruler

Used by: **spacy-expert** (owner), pipeline-engineer

- Keep labels PERSON, WORK_OF_ART, ORG (GPE/LOC/DATE optional, noisy).
- Seed EntityRuler patterns from `directors`, `actors` and the curated film titles; use `id` to merge name variants ("Villeneuve" / "Denis Villeneuve").
- Normalise entity text (strip possessive 's, quotes) before counting; drop the film's own title from WORK_OF_ART counts for that film.

Reference: `knowledge/spacy-expert/rule-based-matching.md`, `knowledge/spacy-expert/linguistic-features.md`.
