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
- Treat committed `.devcontainer/*`, referenced Docker/Compose files, and lifecycle scripts as the current implementation; treat the official specification and CLI behaviour as the correctness authority when editor defaults disagree.
- Inspect `.devcontainer/`, Dockerfile, Compose files, and referenced scripts before editing.
- Edit `.devcontainer/*`, referenced Docker/Compose files, and lifecycle scripts only when needed for the task.
- Treat commands that start the container or run lifecycle hooks as execution steps, not routine inspection.
- Choose the simplest viable topology:
  - `image` for simple reuse
  - `build` for project-specific tooling
  - `dockerComposeFile` for multi-service environments
- Prefer a maintained Feature or Template when it already provides the required tool or runtime; use ad-hoc bootstrap only when the setup is repo-specific or no suitable reusable option exists.
- Put one-time setup in `onCreateCommand`, `updateContentCommand`, or `postCreateCommand`; keep `postStartCommand` and `postAttachCommand` lightweight, idempotent, and fast.
- Treat `remoteUser` and `containerUser` carefully, especially for Linux bind-mount permissions.
- Flag host-only assumptions such as absolute host paths, host package managers, or UID/GID expectations that will not survive across laptop, VM, server, or CI.

## CLI workflow

Use CLI validation when the task requires runtime verification and the environment has Dev Container CLI, Docker/Compose access, and approval for execution steps.

- Static inspection:
  - `devcontainer read-configuration --workspace-folder <repo>`
- Optional build validation:
  - `devcontainer build --workspace-folder <repo>`
  - Use this when image or build correctness matters and Docker-heavy execution is in scope.
  - This can pull images or run Docker build steps, but it does not run repo lifecycle hooks by itself.
- Approval-required execution:
  - `devcontainer up --workspace-folder <repo>`
  - `devcontainer exec --workspace-folder <repo> <cmd>`
  - `devcontainer run-user-commands --workspace-folder <repo>`
  - Use these only after explicit approval, because they start the target container and may run repo-defined lifecycle hooks or project commands.

If runtime validation cannot run, complete a static review and state exactly which validation steps remain unverified.

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
- validation status: static review only, build-validated, or runtime-validated
- exact CLI validation commands run, skipped, or still required
- remaining assumptions or risks

## References

- Development Containers specification: https://containers.dev/
- Dev Container CLI: https://github.com/devcontainers/cli
