# Subagents reference

Source: https://code.claude.com/docs/en/sub-agents

## File
`.claude/agents/<name>.md` — frontmatter between `---` (must be the first line) + Markdown body (system prompt). Subagents receive this prompt plus environment details, **not** the Claude Code system prompt.

## Frontmatter (camelCase; unknown fields are silently ignored)
| Field | Notes |
|---|---|
| `name` (required) | unique, ≤ 256 chars, no `:` and must not start with `-` |
| `description` (required) | when to delegate; keep brief (combined descriptions > 15,000 tokens → warning) |
| `tools` | comma list or YAML list; omit to inherit all; to preload skills use `skills`, not `Skill` here |
| `disallowedTools` | removed from the inherited/listed set |
| `model` | `sonnet`, `opus`, `haiku`, `fable`, a full ID, or `inherit` |
| `permissionMode` | default / acceptEdits / auto / dontAsk / bypassPermissions / plan |
| `maxTurns`, `effort`, `color`, `memory` (user/project/local), `isolation: worktree`, `background`, `omitClaudeMd`, `hooks`, `mcpServers`, `initialPrompt` | optional |
| `skills` | skills to **preload**: "The full content is injected, not only the description", up to the first 32 names. Skills with `disable-model-invocation: true` can't be preloaded |

Files are skipped when: no `name`; opening `---` not on line 1; bad name; `name` without `description`; YAML that doesn't parse. Check with `claude plugin validate .claude/agents`.

## Startup context
Fresh context: system prompt + task message + CLAUDE.md hierarchy + git status + preloaded skills (+ sibling roster with SendMessage). It doesn't see the parent conversation.

## Models
Precedence: per-invocation `model` → `model` field → `CLAUDE_CODE_SUBAGENT_MODEL` → parent model.
