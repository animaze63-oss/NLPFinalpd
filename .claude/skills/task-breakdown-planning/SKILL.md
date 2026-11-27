---
name: task-breakdown-planning
description: "Break Scifi Cinema Lens work into ordered, assignable tasks with done-criteria. Use when planning a phase, splitting a feature, or deciding which agent does what."
---

# task-breakdown-planning

Used by: **orchestrator** (owner), meta-agent

1. Restate the goal in one sentence and name the phase (design, build, test, deploy).
2. List deliverables as file paths (e.g. `pipeline/nlp_spacy.py`, `site/data/film/<slug>.json`).
3. For each deliverable: owner agent, inputs it needs, acceptance test, dependency on other tasks.
4. Order tasks so contracts come first (data contract → pipeline → frontend/Pyodide).
5. Run independent tasks in parallel; chain dependent ones.
6. Every task ends with the hand-off block from `knowledge/orchestrator/workflow.md`.

Detail: `knowledge/orchestrator/workflow.md`.
