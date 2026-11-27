# Delegating to subagents (Claude Code)

Source: https://code.claude.com/docs/en/sub-agents

- Project subagents live in `.claude/agents/*.md`: YAML frontmatter (`name`, `description` required) + Markdown body = the subagent's system prompt. Claude Code watches the folder; edits apply to the next delegation without restart.
- > "Each subagent starts with a fresh, isolated context window. It doesn't see your conversation history, the skills you've already invoked, or the files Claude has already read. Claude composes a delegation message that summarizes the task."
  → Every delegation message must be self-contained: goal, files, inputs, the contract, acceptance criteria.
- A subagent's initial context: its system prompt, the task message, CLAUDE.md files, git status, **preloaded skills** (full content of each skill in its `skills` field), and a sibling roster if it has `SendMessage`.
- Automatic delegation uses the `description` field; "use proactively" in a description encourages it.
- Nesting: subagents can spawn subagents up to three layers below the main conversation by default (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`); at the limit the `Agent` tool is withheld.
- Custom subagents started from the main conversation run in the **background** by default; background subagents keep Read, Grep, Glob, Bash, Edit, Write, WebFetch, WebSearch, Skill, SendMessage and a few others.
- Model order: per-invocation `model` → the agent's `model` field → `CLAUDE_CODE_SUBAGENT_MODEL` → parent's model.
- Patterns from the docs: isolate high-volume operations (tests, doc fetching), run parallel research, **chain subagents** ("use the code-reviewer subagent… then use the optimizer subagent").
- Use the main conversation instead when the task needs frequent back-and-forth, phases share a lot of context, or it's a quick targeted change.
- Warning from the docs: many subagents each returning detailed results "can consume significant context" → ask each agent for a short structured hand-off.
