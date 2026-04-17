# skills

This repository is the source of truth for a small set of reusable agent skills.

The default distribution model is conservative:

- keep each skill under version control in this repository
- avoid public registries and auto-install workflows by default
- link only the required skills into a project workspace when needed

## Repository layout

```text
skills/
  <skill-name>/
    SKILL.md
scripts/
  install-skill.sh
```

Each skill must live at `skills/<skill-name>/SKILL.md`.

## Current skills

### Planning flow

- `triage`: choose the lightest adequate planning route for a development task
- `lite-spec`: write a compact execution brief for bounded implementation work
- `metaplan`: review and tighten specs, plans, and task breakdowns before autonomous implementation

### Handoff

- `handoff-prompt`: generate a compact prompt for the next agent or stage

### Notebook review

- `marimo-reactive-review`: review an existing marimo notebook for reactive design quality and refactor opportunities

### Repository guidance

- `growing-agents-md`: create or refine a compact `AGENTS.md` without letting it bloat

### Git maintenance

- `git-prune-worktrees`: safely prune stale refs, clean merged worktrees, merged local branches, and stale worktree metadata

## Naming guidance

Prefer short, command-friendly names.

Use names that:

- are easy to invoke directly as slash-style commands
- distinguish categories without excessive prefixes
- describe the skill's role in a few syllables
- avoid avoidable collisions with common built-in commands such as `/plan`

## Tool compatibility

This repository targets multiple coding agents, but each tool discovers reusable guidance differently:

- Claude Code: project-local skills in `.claude/skills/`
- Codex: project-local skills in `.agents/skills/`
- GitHub Copilot CLI: project-local skills in `.github/skills/` or `.claude/skills/`
- Gemini CLI: project-local skills in `.agents/skills/`

## Installation model

The installer script links skills from this repository into a target workspace by default.
It does not depend on a remote marketplace or registry.
It runs with `python3` when available and falls back to `uv`.
Use `--copy` when a workspace needs its own editable copy.
Use `--force` to replace an existing real directory or file.
For external skills installed directly from upstream repositories, see `docs/external-skills.md`.

Supported targets:

- `claude`: install to `.claude/skills/`
- `codex`: install to `.agents/skills/`
- `copilot`: install to `.github/skills/`
- `gemini`: install to `.agents/skills/`
- `all`: install to all supported agent locations

Examples:

```sh
./scripts/install-skill.sh all all
./scripts/install-skill.sh triage codex .
./scripts/install-skill.sh lite-spec copilot /path/to/workspace
./scripts/install-skill.sh metaplan gemini /path/to/workspace
./scripts/install-skill.sh handoff-prompt all /path/to/workspace
./scripts/install-skill.sh triage codex /path/to/workspace --copy
./scripts/install-skill.sh triage codex /path/to/workspace --force
```

## Project instruction files

These are separate from skills, but they affect project-local behaviour:

- GitHub Copilot supports `AGENTS.md`, `GEMINI.md`, and `.github/copilot-instructions.md`
- Gemini CLI loads hierarchical `GEMINI.md` files and can be configured to accept other context filenames

The installer in this repository manages skills only. It does not generate repository-wide instruction files such as `AGENTS.md` or `.github/copilot-instructions.md`.

## Notes

- Keep repository files and skill artifacts in English.
- Keep skills narrow, explicit, and easy for agents to apply.
- Prefer project-local installation unless there is a clear reason to install globally.
