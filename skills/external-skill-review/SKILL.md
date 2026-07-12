---
name: external-skill-review
description: Review a candidate external skill against the repo policy, record approved entries in a project-local catalog, and recommend APM install commands when approved.
---

# External Skill Review

Use when the user wants to adopt an external skill, reuse a prior approval, or check whether a candidate is already cataloged. Do not use it to review skills already in this repository. It never installs anything — final installation and trust decisions remain the user's.

Governing policy: `docs/external-skills.md` — approval rules, content risk classes, provenance requirements, and the normative install tool are authoritative there. This skill states the decision cascade and invocation contract only; it does not restate that document's mechanics.

## Inputs

Gather before proceeding; ask the user for anything missing:

- `repo` — upstream repository, `owner/repo`
- `skill_path` — path or name of the skill within that repository
- `pinned_ref` — commit SHA (preferred), or a branch/tag with a documented reason
- `targets` — agent targets (e.g. `claude`, `codex`, `copilot`, `gemini`)
- `license` — SPDX identifier or description; state "unknown" if not yet checked
- `notes` — any review notes already available
- `catalog_entry` — optional, pass if reusing a prior approval

## Catalog check (do first)

```sh
python3 scripts/catalog.py get <repo> <skill_path> <pinned_ref>
```

An entry printed means an exact `(repo, skill_path, pinned_ref)` match with `review_status: approved` exists — reuse its provenance and skip to **Required output**.

No output covers: no catalog file, no matching entry, a different `pinned_ref`, or a non-approved entry — continue to the decision cascade; each upstream update requires a fresh review.

## Decision cascade

Evaluate in order. First match wins; do not evaluate further predicates once one matches.

1. **`not approved`** — a confirmed hard blocker exists:
   - no `pinned_ref` at all
   - license missing, ambiguous, or incompatible with the intended use
   - content disallowed by `docs/external-skills.md` (e.g. compiled binaries, obfuscated/minified code, installers or bootstrap hooks pulling in additional code without separate approval)
   - any other required approval-rule condition is confirmed to fail (not merely unverified)

2. **`needs manual review`** — no confirmed hard blocker, but required evidence or judgement is unresolved:
   - `repo` or `skill_path` missing or too vague to identify a unique upstream source
   - `pinned_ref` is a branch or tag — with or without a documented reason. Approval requires an identified commit SHA (`docs/external-skills.md` approval rules), so this skill never returns `approved` for a floating ref; ask for a documented reason if none exists, record the exception, and leave the proceed/hold decision with the user
   - license present but not yet checked for compatibility
   - higher-risk-but-reviewable content present (workspace-modifying scripts, command-executing helpers, remote references that can drift from the pinned ref) and unconfirmed by the user
   - any other approval-rule condition unresolved from the information available

3. **`approved`** — every `docs/external-skills.md` approval-rule condition holds for the exact pinned commit SHA, and no higher-risk content remains unconfirmed.

## Required output

Return all five, in order:

1. **Result** — exactly one of `approved`, `not approved`, `needs manual review`
2. **Rationale** — tied to the specific cascade predicate(s) matched
3. **Provenance fields** to preserve or update: `repo`, `skill_path`, `pinned_ref`, `targets`, `license`, `review_status`, `reviewer`, `review_date`, `notes`
4. **Next steps**
5. **Install commands** — only when Result is `approved` (fresh or reused); never otherwise

On `not approved` or `needs manual review`: state precisely what blocks approval or is missing; never emit install commands.

Install commands: use the current APM form and manual fallback in `docs/external-skills.md` (`apm install owner/repo/path#COMMIT_SHA`, or the pinned manual clone) — do not restate the mechanics here.

## Catalog

`.agents/approved-external-skills.json` in the target workspace: a project-local JSON array of provenance entries (never the home directory).

```json
{
  "repo": "owner/repo",
  "skill_path": "skills/example",
  "pinned_ref": "abc1234",
  "targets": ["claude", "codex"],
  "license": "MIT",
  "review_status": "approved",
  "reviewer": "your-name",
  "review_date": "2026-04-17",
  "notes": ""
}
```

```sh
python3 scripts/catalog.py get <repo> <skill_path> <pinned_ref>
python3 scripts/catalog.py add '<json-entry>'
```

## Validation cases

- **Every outcome**: approval-rule conditions all hold for a pinned SHA → `approved`. No `pinned_ref` at all → `not approved`. `skill_path` too vague to identify a unique source → `needs manual review`.
- **`not approved` / `needs manual review` boundary**: no ref at all is a confirmed blocker (`not approved`); a branch/tag ref — even with a documented reason — is `needs manual review`, never `approved`: approval requires a commit SHA, and the documented exception is the user's decision to carry.
- **`needs manual review` / `approved` boundary**: a workspace-modifying script flagged but not yet confirmed reviewed by the user → `needs manual review`; same script after confirmation, all else holding → `approved`.
- **Multi-condition**: license missing (hard blocker) *and* `skill_path` vague (unresolved judgement) at once → `not approved` wins by precedence; never downgrade to `needs manual review`.
- **Insufficient information**: `repo` given, `skill_path` absent → `needs manual review`, ask for `skill_path`.
- **Exact enum formatting**: Result is always exactly `approved`, `not approved`, or `needs manual review` — lowercase, no alternate spellings.

## Constraints

- Never auto-install. This skill reviews, catalogs, and recommends only.
- Do not emit install commands unless Result is `approved` or the reused entry is `approved`.
- Do not approve when any required field is unknown or incomplete.
- Treat branch or tag refs as documented exceptions, never the default.
- Treat each upstream update as a new review event requiring a new pinned commit SHA.
- Do not override `docs/external-skills.md`.
