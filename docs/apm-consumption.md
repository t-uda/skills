# APM consumption

This document describes how to consume this repository via APM
([Agent Package Manager](https://microsoft.github.io/apm)).

## Scope

Phase 1 ships **skills only**. The following APM primitive types are not
distributed from this repository yet:

- prompts
- agents
- instructions
- hooks
- MCP server configs
- plugin bundles

Each is tracked as a separate follow-up and will be evaluated before adoption.

## Policy

- `apm install` is the preferred consumption path for tools that support it.
- Compiled outputs (`AGENTS.md`, `CLAUDE.md`) produced by `apm compile` are a
  compatibility layer, not the primary delivery. Compiled artifacts in this
  repository stay compact and procedural content remains in skill files.
- The manual installer (`scripts/install-skill.sh`) remains supported for
  environments without APM.

## Repository layout

Skills live at `skills/<skill-name>/SKILL.md`. This is a monorepo layout; APM
consumes each skill by subpath rather than as a single bundled package.

There is no `.apm/` directory. It will be introduced only when a non-skill
primitive is added to this repository.

## Install patterns

### Single skill by subpath

```sh
apm install t-uda/skills/skills/triage
apm install t-uda/skills/skills/metaplan
apm install t-uda/skills/skills/lite-spec
```

### Pinned commit

```sh
apm install t-uda/skills/skills/triage#<commit-sha>
```

Pin to a commit SHA for reproducible installs. Branch or tag refs are allowed
as explicit exceptions only.

### Declared in `apm.yml`

```yaml
dependencies:
  apm:
    - t-uda/skills/skills/triage
    - t-uda/skills/skills/metaplan#<commit-sha>
```

## Target directory mapping

See [docs/apm-primitive-matrix.md](apm-primitive-matrix.md) for the full
verified matrix of (tool × primitive) deployment paths, detection triggers,
native support, and install-first classifications for APM CLI 0.8.12.

Summary for skills (subpath install):

| Tool            | Skill destination      | Detection trigger     |
| --------------- | ---------------------- | --------------------- |
| Claude Code     | `.claude/skills/`      | `.claude/` present    |
| GitHub Copilot  | `.github/skills/`      | `.github/` present    |
| Cursor          | `.cursor/skills/`      | `.cursor/` present    |
| OpenCode        | `.opencode/skills/`    | `.opencode/` present  |
| Codex CLI       | `.agents/skills/`      | `.codex/` present     |
| Gemini CLI      | — (no APM target)      | —                     |
| (bare workspace) | `.github/skills/`     | APM creates `.github/` |

## Validation

At least one subpath install is verified end-to-end before releases that
change APM-facing layout or metadata. Detailed validation records live in
[docs/apm-primitive-matrix.md](apm-primitive-matrix.md).

Last validated: 2026-04-21 against APM CLI 0.8.12.

## Follow-ups

- Evaluate whether to migrate skills under `.apm/skills/` when a non-skill
  primitive is first added (#30).
- Evaluate adoption of prompts, agents, instructions, or hooks as separate
  tracked issues (#31).
- Revisit repository name if scope broadens beyond skills (#24).
- Revisit Gemini CLI support when a newer APM version adds a Gemini target.
- Revisit Claude Code hook integration once APM hook schema aligns with
  Claude Code settings.json format (see matrix gap notes).
