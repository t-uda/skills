---
name: growing-agents-md
description: Seed, lint, or update a compact canonical AGENTS.md with deterministic guardrails. Use this when AGENTS.md is missing, stale, structurally degraded, or when durable repo guidance changed.
---

# Growing AGENTS.md

Use this skill to keep `AGENTS.md` canonical, compact, and durable.

Use it when:

- `AGENTS.md` is missing
- `AGENTS.md` fails structural lint
- the current task changes durable commands, architecture, or workflow rules
- the file became generic, bloated, or stale enough to prune

The bundled script is the source of truth for scaffold shape, guard comments, placeholder rules, section rendering, and the counted-line budget:

```sh
python3 skills/growing-agents-md/scripts/growing_agents_md.py <command>
```

## Workflow

1. Run `init` when `AGENTS.md` is missing. This writes the canonical scaffold only.
2. Run `lint` before editing an existing file. If lint fails, do not guess repairs outside the canonical schema.
3. Gather only stable, repo-specific facts worth preserving in durable agent guidance.
4. Run `apply` with structured JSON input to replace whole sections deterministically.
5. Review the result for repo-specific quality, then keep moving. Do not turn `AGENTS.md` into a changelog.

## Commands

```sh
python3 skills/growing-agents-md/scripts/growing_agents_md.py init
python3 skills/growing-agents-md/scripts/growing_agents_md.py lint
python3 skills/growing-agents-md/scripts/growing_agents_md.py apply --input agents.json
```

`apply` expects JSON shaped like:

```json
{
  "project_overview": ["- ..."],
  "commands": ["~~~sh", "make test", "~~~"],
  "code_conventions": ["- ..."],
  "architecture": ["- ..."]
}
```

Missing or empty arrays remove that replaceable section. The script hard-fails on non-canonical structure, placeholder leftovers, forbidden catch-all headings, or counted-line budget overflow.

## Content policy

- Keep only repo-specific, non-obvious, stable guidance.
- Prefer terse bullets and one high-value shell block.
- Delete stale or inferable content instead of appending.
- Do not add generic advice, history, or catch-all sections such as `Notes` or `Context`.
