---
name: agent-prompt-skill-design
description: "Write or revise Claude Code subagent files (.claude/agents) and skills (.claude/skills) for this team. Use when adding a role, changing an agent's model/tools/skills, or a skill isn't triggering."
---

# agent-prompt-skill-design

Used by: **meta-agent** (owner), orchestrator

- Subagent: frontmatter `name`, `description` (when to delegate), `tools` (minimum), `model`, `skills` (≤ 32, preloaded in full). Body = system prompt.
- Every agent body starts with: read `knowledge/<agent>/README.md` and every file it lists.
- Skill: `.claude/skills/<name>/SKILL.md`, frontmatter `name` + `description` with trigger words; body short; link to knowledge files instead of copying.
- Don't set `disable-model-invocation: true` on a skill an agent preloads — it can't be preloaded then.
- After any change, update `docs/agent-brains.md` and `docs/expert-roster.md` if roles or skills changed.

References: `knowledge/meta-agent/subagents-reference.md`, `knowledge/meta-agent/skills-reference.md`.
