---
name: output-review-retrospectives
description: "Review agents' outputs against their role and run phase retrospectives. Use at the end of each phase or when an agent's work was wrong, off-role or based on stale facts."
---

# output-review-retrospectives

Used by: **meta-agent** (owner), orchestrator, qa-engineer

1. Collect each agent's hand-off block for the phase.
2. Score: correct? within role? sourced? tested? contract respected?
3. Find root causes: missing knowledge, vague prompt, wrong model, missing skill, bad hand-off.
4. Fix the cause in `.claude/agents/`, `.claude/skills/` or `knowledge/` (with source links).
5. Log the change in `docs/agent-brains.md` → Changelog.

Checklist: `knowledge/meta-agent/agent-quality-checklist.md`.
