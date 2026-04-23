---
name: devcontainer-cli
description: Use this skill when working with Dev Containers, devcontainer.json, or Dev Container CLI for setup, review, validation, or troubleshooting.
---

# Dev Container CLI

Use this skill when a task involves `.devcontainer/`, `devcontainer.json`, Dev Container Features/Templates, or Dev Container CLI commands.

## Goals

- review existing Dev Container setup
- create or revise `devcontainer.json`
- choose among image / Dockerfile / Compose setups
- validate with Dev Container CLI
- troubleshoot common Dev Container-specific failures

## Core rules

- Prefer the official Dev Container specification and CLI behaviour over editor-specific assumptions.
- Inspect `.devcontainer/`, Dockerfile, Compose files, and referenced scripts before editing.
- Choose the simplest viable topology:
  - `image` for simple reuse
  - `build` for project-specific tooling
  - `dockerComposeFile` for multi-service environments
- Prefer Features or Templates over ad-hoc bootstrap when practical.
- Place lifecycle commands in the correct phase, and avoid heavy repeated work in startup hooks.
- Treat `remoteUser` and `containerUser` carefully, especially for Linux bind-mount permissions.
- Optimise for reproducibility across laptop, VM, server, and CI.

## CLI workflow

Use the CLI as the primary validation path:

- `devcontainer read-configuration --workspace-folder <repo>`
- `devcontainer build --workspace-folder <repo>`
- `devcontainer up --workspace-folder <repo>`
- `devcontainer exec --workspace-folder <repo> <cmd>`
- `devcontainer run-user-commands --workspace-folder <repo>`

Do not assume a setup is correct until it is CLI-verifiable.

## What to check

When reviewing or authoring a Dev Container, check:

- topology choice is justified
- lifecycle commands are placed correctly
- ports and mounts are minimal and explicit
- user and permission settings are coherent
- secrets are not baked into committed files
- host-specific assumptions are avoided
- the setup can be reused or prebuilt when beneficial

## Troubleshooting checklist

Check in roughly this order:

1. config or path errors
2. image / build / compose mismatch
3. lifecycle hook misuse
4. user or UID/GID mismatch
5. mount or workspace issues
6. service readiness or port issues
7. env or secret handling mistakes

## Output expectations

Provide:

- proposed config changes
- brief rationale
- exact CLI validation commands
- remaining assumptions or risks

## References

- Development Containers specification: https://containers.dev/
- Dev Container CLI: https://github.com/devcontainers/cli
