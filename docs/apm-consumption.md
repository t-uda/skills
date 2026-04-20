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

APM deploys skills to the native directories it detects in the consuming
workspace. Observed behaviour with APM CLI 0.8.12:

| Tool                    | Skill destination   | Detection trigger |
| ----------------------- | ------------------- | ----------------- |
| Claude Code             | `.claude/skills/`   | `.claude/` present |
| GitHub Copilot / VSCode | `.github/skills/`   | `.github/` present |
| Cursor                  | `.cursor/skills/`   | `.cursor/` present |
| OpenCode                | `.opencode/skills/` | `.opencode/` present |

If no native target directory is present in the consuming workspace, APM
creates `.github/` and deploys skills under `.github/skills/` as a fallback.

Notes:

- The exact set of auto-detected targets may evolve. Verify against the APM
  version in use.
- In validation with APM 0.8.12, a bare `.agents/` directory did not trigger
  a Codex skill deploy. If Codex support is required, confirm the current
  APM detection rules before relying on it.
- Non-skill primitive targets (`.claude/commands/`, `.github/prompts/`,
  `.github/agents/`, etc.) are not exercised by this repository in phase 1.

## Validation

At least one subpath install is verified end-to-end before releases that
change APM-facing layout or metadata. Record of the last validation is kept
in this document when it is run.

Last validated: 2026-04-21 against APM CLI 0.8.12.

- `apm install t-uda/skills/skills/triage` in a workspace with `.claude/`
  and `.github/` present: deployed to `.claude/skills/triage/` and
  `.github/skills/triage/`.
- `apm install t-uda/skills/skills/metaplan#<sha>` (pinned commit) in a
  workspace with only `.claude/` present: deployed to `.claude/skills/metaplan/`.
- `apm install t-uda/skills/skills/triage` in a bare workspace with no
  native directories: APM created `.github/` and deployed to
  `.github/skills/triage/`.

## Follow-ups

- Evaluate whether to migrate skills under `.apm/skills/` when a non-skill
  primitive is first added.
- Evaluate adoption of prompts, agents, instructions, or hooks as separate
  tracked issues.
- Revisit repository name if scope broadens beyond skills.
