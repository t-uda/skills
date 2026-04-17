# External skill installation

This document defines the first-pass policy for using skills that live in upstream repositories.

It does not vendor those skills into this repository, and it does not extend `scripts/install-skill.sh`.

## Defaults

- prefer skills stored in this repository when they already meet the need;
- use external skills only when the user or project explicitly chooses an external source;
- install external skills project-locally in the target workspace;
- pin to a commit SHA by default;
- use branch or tag refs only as an explicit exception with a documented reason.

## Normative tool

Use Agent Skills CLI as the normative example tool for this policy.

Example commands:

```sh
npx agent-skills-cli add owner/repo@skill-name -a claude,codex,copilot
npx agent-skills-cli install owner/repo#COMMIT_SHA -a codex
```

If a project uses another tool, it should meet the same pinning, provenance, license, and review requirements described here.

## Approval rules

Approve an external skill only when all of the following are true:

- the upstream repository, skill path, and pinned commit SHA are identified;
- the repository owner or maintainers are known and trusted for the intended use;
- the skill content is readable and reviewable;
- the license is clear enough to allow the intended use;
- any scripts or executable helpers are small enough to review directly and are acceptable for project-local use.

Do not approve an external skill when any of the following are true:

- the license is missing, ambiguous, or incompatible with the intended use;
- the install depends on an unpinned floating ref by default;
- the skill includes opaque binaries, obfuscated code, or generated artifacts that cannot be meaningfully reviewed;
- the skill downloads or executes additional remote code as part of install or normal use without separate review;
- the skill requires broader trust than the project is prepared to grant.

## Content expectations

Expected content:

- `SKILL.md` and small supporting text assets;
- small reviewed helper scripts only when the skill clearly requires them.

Higher-risk content that requires extra scrutiny:

- shell, Python, or Node.js helpers that modify the workspace;
- prompts or helpers that execute commands on behalf of the user;
- references to remote resources that may change independently of the pinned ref.

Disallowed by default:

- compiled binaries;
- obfuscated or minified executable code;
- installers, update hooks, or bootstrap scripts that pull in additional code without separate approval.

## Provenance requirements

The target workspace must preserve at least these fields for each approved external skill:

- upstream repository;
- upstream skill path;
- pinned ref;
- review status;
- reviewer;
- review date.

This repository does not define a standard provenance filename yet. Until a format is standardised, the consuming project should keep these fields in a workspace-local record that is easy to review and update.

## Update rules

- treat each upstream update as a new review event;
- move to a new pinned commit SHA only after reviewing the diff from the previously approved ref;
- keep branch or tag based installs as temporary exceptions, not the default workflow;
- re-record provenance after each approved update.

## Non-goals

- vendoring upstream skills into `skills/`;
- adding external install support to `scripts/install-skill.sh`;
- marketplace or registry support;
- unpinned remote installs by default;
- provenance automation in this repository.

## Follow-up work

- define a standard provenance file format and location for target workspaces;
- decide whether a lightweight approval checklist should live in this repository;
- decide whether README examples should link to vetted external-skill workflows for specific tools.
