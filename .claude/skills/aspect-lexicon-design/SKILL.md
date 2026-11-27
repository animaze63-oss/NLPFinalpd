---
name: aspect-lexicon-design
description: "Maintain the trigger word lists for the four aspects (visuals, story, characters, soundtrack) and their ambiguity rules. Use when aspect detection misses or misassigns mentions."
---

# aspect-lexicon-design

Used by: **spacy-expert** (owner), nltk-expert, pyodide-engineer, nlp-evaluator

- One file: `pipeline/aspects.py` → exported to `site/data/lexicon.json` (the browser reads the same lists).
- Triggers are lemmas + multi-word phrases (special effects, production design, sound design, world building).
- Ambiguity: "theme" → story unless a soundtrack trigger is in the sentence; "design" → visuals; "sound design" → soundtrack; "performance" → characters.
- Every change: rerun the aspect sample evaluation and record precision/recall.

Starting lists: `docs/02-spacy.md` §5.
