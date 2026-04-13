# skills

This repository is the source of truth for a small set of agent skills.

The default distribution model is conservative:

- keep each skill under version control in this repository
- avoid public registries and auto-install workflows by default
- copy only the required skills into a project workspace when needed

This layout is intended to work with agents that discover skills from local folders, including:

- Claude Code: `.claude/skills/`
- Codex: `.agents/skills/`

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

Example:

```sh
./scripts/install-skill.sh my-skill both /path/to/workspace
```

## Notes

- Keep repository files and skill artifacts in English.
- Keep skills narrow, explicit, and easy for agents to apply.
- Prefer project-local installation unless there is a clear reason to install globally.
