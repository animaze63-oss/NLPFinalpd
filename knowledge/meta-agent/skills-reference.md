# Skills reference

Source: https://code.claude.com/docs/en/skills

- Project skill: `.claude/skills/<skill-name>/SKILL.md`. Commit it so the team gets it. Directory name (or `name`) becomes `/skill-name`.
- `SKILL.md` = YAML frontmatter + Markdown instructions. Frontmatter is read only if `---` is the first line.
- Key fields (lowercase-hyphen): `name`, `description` (recommended; key use case first; `description` + `when_to_use` truncated at 1,536 chars), `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context: fork`, `agent`, `paths`, `hooks`, `metadata`, `license`, `compatibility`.
- Invocation control: default = user and Claude can invoke; `disable-model-invocation: true` = user only (and **can't be preloaded into subagents**); `user-invocable: false` = Claude only (background knowledge).
- Content types: **reference content** (conventions, domain knowledge — runs inline) vs **task content** (step-by-step actions).
- "Keep the body itself concise. Once a skill loads, its content stays in context across turns, so every line is a recurring token cost." Keep `SKILL.md` under 500 lines; move detail into supporting files referenced from SKILL.md.
- After compaction, Claude Code re-attaches up to the first 5,000 tokens of each invoked skill (25,000 total) → put the most important rules at the top.
- Troubleshooting: if a skill doesn't trigger, the description lacks the words users say; validate with `claude plugin validate .claude/skills`.
- Skills vs subagents: subagent `skills` field preloads skills into that agent; a skill with `context: fork` runs itself in a subagent.
