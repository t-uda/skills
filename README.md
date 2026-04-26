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

### Source-of-truth review

- `sot-integrity`: audit a source-of-truth artifact for authority, evidentiary grounding, trust scope, and conflict with repository reality before implementation or orchestration relies on it

### Artifact cleanup

- `deslop-history`: clean final user-visible artifacts from accepted decisions or issue/PR discussion by removing historical residue and process framing

### Orchestration

- `light-orchestration`: choose between single-agent execution and a minimal multi-agent split, and produce strictly bounded subtask contracts when a split is justified

### Handoff

- `handoff-prompt`: generate a compact prompt for the next agent or stage

### Notebook review

- `marimo-reactive-review`: review an existing marimo notebook for reactive design quality and refactor opportunities

### Repository guidance

- `growing-agents-md`: seed, lint, or update a compact canonical `AGENTS.md` with deterministic guardrails

### Git maintenance

- `git-prune-worktrees`: safely prune stale refs, clean merged worktrees, merged local branches, and stale worktree metadata

### External skills

- `external-skill-review`: review a candidate external skill against the repo policy, record approved entries in a project-local catalog, and recommend install commands

### Dev containers

- `devcontainer-cli`: review, validate, and troubleshoot Dev Container setup with explicit CLI-first guidance

### Delivery workflow

- `github-driven-workflow`: enforce issue-first, PR-gated delivery with no direct main pushes, independent review requirement, and deterministic merge gates

### Randomness

- `randomness`: prefer a bundled PRNG script for random selection; fall back to a String Seed prompt pattern only for low-stakes or creative-diversity use

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

## APM installation

This repository is compatible with [APM (Agent Package Manager)](https://microsoft.github.io/apm).

Install individual skills via subpath:

```sh
apm install t-uda/skills/skills/triage
apm install t-uda/skills/skills/metaplan
apm install t-uda/skills/skills/lite-spec
```

Install with pinned commit:

```sh
apm install t-uda/skills/skills/triage#abc1234
```

APM automatically deploys skills to detected target directories (`.github/skills/`, `.claude/skills/`, `.agents/skills/`, etc.).

The manual installer script remains available for environments where APM is not installed.

### Install-first, compile-minimal

This repository favours native install over compiled instruction files:

- `apm install` is the preferred path. Skills land directly in each tool's native directory.
- `apm compile` output (`AGENTS.md`, `CLAUDE.md`) is treated as a compatibility layer only.
- Compiled artifacts in this repo stay compact: durable policy, minimal guardrails, and pointers. Procedures live in skill files, not in compiled documents.

### Current APM scope

Phase 1 covers skills only. Prompts, agents, instructions, hooks, and MCP are not distributed from this repository yet. See `docs/apm-consumption.md` for supported primitives, target-directory mapping per tool, and subpath install patterns.

## Project instruction files

These are separate from skills, but they affect project-local behaviour:

- GitHub Copilot supports `AGENTS.md`, `GEMINI.md`, and `.github/copilot-instructions.md`
- Gemini CLI loads hierarchical `GEMINI.md` files and can be configured to accept other context filenames

The installer in this repository manages skills only. It does not generate repository-wide instruction files such as `AGENTS.md` or `.github/copilot-instructions.md`.

## Notes

- Keep repository files and skill artifacts in English.
- Keep skills narrow, explicit, and easy for agents to apply.
- Prefer project-local installation unless there is a clear reason to install globally.
