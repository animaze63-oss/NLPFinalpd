# Agent quality checklist (project-defined)

For each agent file:
- [ ] Frontmatter parses; `name` matches the file name; description says *when* to use it in ≤ 2 sentences.
- [ ] `model` justified in docs/agent-brains.md (opus = judgment/linguistic depth; sonnet = build work; haiku = small, well-specified config tasks).
- [ ] `skills` lists exactly the skills the roster assigns (owner + also-uses), ≤ 32.
- [ ] Body starts with the "read your knowledge folder first" step and names the folder.
- [ ] Decision record restated in one line; hand-off format included.
- [ ] Tools are the minimum needed (e.g. UX doesn't need Bash; only the Orchestrator has Agent).

For each skill: description has trigger words; body < 60 lines; points to knowledge files instead of copying them.

For each knowledge folder: every note has a source URL; README index lists all files; facts not confirmed are marked.

Retrospective questions after each phase: Which hand-offs failed? Which facts were wrong or stale? Which agent did work outside its role? Update the files, then record the change in docs/agent-brains.md → Changelog.
