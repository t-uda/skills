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

Use APM (Agent Package Manager) as the preferred tool for this policy.

Example commands:

```sh
# Install with pinned commit (preferred)
apm install owner/repo/path/to/skill#COMMIT_SHA

# Install from repo root if skill is at root
apm install owner/repo#COMMIT_SHA
```

APM automatically deploys to detected target directories (`.github/skills/`, `.claude/skills/`, `.agents/skills/`, etc.).

If APM is not available, use manual installation with the same pinning, provenance, license, and review requirements described here.

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

## Approved external skills

Each entry below has been reviewed and approved per the rules in this document.

---

### runpod/skills — runpodctl

| Field | Value |
|---|---|
| Upstream repository | `runpod/skills` |
| Upstream skill path | `runpodctl/` |
| Pinned ref | `91417885a3a335baa670b2186b1766e1993cace6` |
| License | Apache-2.0 |
| Review date | 2026-05-25 |
| Review status | approved |

**Install command**

```sh
apm install runpod/skills/runpodctl#91417885a3a335baa670b2186b1766e1993cace6
```

**What it covers**

`runpodctl` usage for Pods, Hub listings, Serverless endpoints, templates, network volumes, models, registry credentials, account information, SSH metadata, file transfer, and CLI utilities. Suitable for Runpod GPU workload management.

**Agent safety cautions**

- Read-only discovery commands (`runpodctl gpu list`, `runpodctl pod list`, `runpodctl serverless list`, `runpodctl user`) are acceptable when Runpod context is needed.
- Creating, deleting, resetting, or materially updating Runpod resources requires explicit user intent for that specific operation — do not infer intent from surrounding context alone.
- Before resource creation, list available GPUs or templates and state the intended resource shape to the user.
- Before any destructive action (delete, reset, stop), confirm the exact target resource identifier from `runpodctl` output; never guess or interpolate an ID.
- API keys, SSH keys, registry credentials, and environment variables must be treated as secrets — never paste them into issues, PRs, logs, or committed files.
- `runpodctl doctor` is appropriate for setup verification.

---

## Follow-up work

- define a standard provenance file format and location for target workspaces;
- decide whether a lightweight approval checklist should live in this repository;
- decide whether README examples should link to vetted external-skill workflows for specific tools.
