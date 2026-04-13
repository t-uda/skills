# skills

This repository is the source of truth for a small set of agent skills.

The default distribution model is conservative:

- keep each skill under version control in this repository
- avoid public registries and auto-install workflows by default
- copy only the required skills into a project workspace when needed

## Tool compatibility

This repository targets multiple coding agents, but each tool discovers reusable guidance differently:

- Claude Code: project-local skills in `.claude/skills/`
- Codex: project-local skills in `.agents/skills/`
- GitHub Copilot CLI: project-local skills in `.github/skills/` or `.claude/skills/`
- Gemini CLI: project-local context from `GEMINI.md`; official reusable packaging is based on Gemini extensions

For Gemini CLI, this repository provides a compatibility install mode that copies a skill into `.gemini/skills/` and imports its `SKILL.md` from `.gemini/GEMINI.md`.

## Repository layout

```text
skills/
  <skill-name>/
    SKILL.md
scripts/
  install-skill.sh
```

## Installation model

The installer script copies one skill from this repository into a target workspace.
It does not depend on a remote marketplace or registry.

Supported targets:

- `claude`: install to `.claude/skills/`
- `codex`: install to `.agents/skills/`
- `copilot`: install to `.github/skills/`
- `gemini`: compatibility mode via `.gemini/skills/` plus `.gemini/GEMINI.md`
- `all`: install to Claude Code, Codex, Copilot, and Gemini compatibility locations

Examples:

```sh
./scripts/install-skill.sh my-skill codex /path/to/workspace
./scripts/install-skill.sh my-skill copilot /path/to/workspace
./scripts/install-skill.sh my-skill gemini /path/to/workspace
./scripts/install-skill.sh my-skill all /path/to/workspace
```

## Project instruction files

These are separate from skills, but they affect project-local behaviour:

- GitHub Copilot supports `AGENTS.md`, `GEMINI.md`, and `.github/copilot-instructions.md`
- Gemini CLI loads hierarchical `GEMINI.md` files and can be configured to accept other context filenames

The installer in this repository currently copies skills only. It does not generate repository-wide instruction files such as `AGENTS.md` or `.github/copilot-instructions.md`.

## Notes

- Keep repository files and skill artifacts in English.
- Keep skills narrow, explicit, and easy for agents to apply.
- Prefer project-local installation unless there is a clear reason to install globally.
