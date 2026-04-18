---
name: external-skill-review
description: Review a candidate external skill against the repo policy, record approved entries in a project-local catalog, and recommend Agent Skills CLI install commands when approved.
---

# External Skill Review

Use this skill when the user wants to adopt an external skill, reuse a prior approval, or check whether a candidate is already cataloged.

Do not use this skill to review skills that already live in this repository.

This skill does not install anything. Final installation and trust decisions remain the user's responsibility.

Governing policy: `docs/external-skills.md`.

## Inputs

Gather the following before proceeding. Ask the user for any that are missing.

- `repo` — upstream repository in `owner/repo` form
- `skill_path` — path or name of the skill within that repository
- `pinned_ref` — commit SHA (preferred), or a branch or tag with a documented reason
- `targets` — agent targets (e.g. `claude`, `codex`, `copilot`, `gemini`)
- `license` — SPDX identifier or plain description; state "unknown" if not yet checked
- `notes` — any relevant review notes already available
- `catalog_entry` — optional; pass if the user wants to reuse a prior approval

## Decision flow

Work through these steps in order. Stop at the first blocking condition.

### 1. Check the catalog

Read `.agents/approved-external-skills.json` in the target workspace using the bundled script:

```sh
python3 skills/external-skill-review/scripts/catalog.py get <repo> <skill_path>
```

If a matching approved entry exists **with the same `pinned_ref`**, skip to step 8 and reuse the stored provenance.

If the entry exists but the `pinned_ref` differs, treat it as a new review event and continue from step 2. Each upstream update requires a fresh review.

### 2. Validate specificity

If `repo` or `skill_path` is missing or too vague to identify a unique upstream source, return `needs manual review` and ask for more detail.

### 3. Check pinning

If `pinned_ref` is not a commit SHA:
- If it is a branch or tag, the user must provide a documented reason before proceeding. Treat as a provisional exception, not the default.
- If no ref is provided at all, return `not approved`. Do not approve an unpinned install.

### 4. Check license

If the license is missing, unknown, ambiguous, or incompatible with the intended use, return `not approved`.

### 5. Check higher-risk content

Identify whether the skill includes any of the following:
- shell, Python, or Node.js helpers that modify the workspace
- prompts or helpers that execute commands on behalf of the user
- references to remote resources that may change independently of the pinned ref
- compiled binaries, obfuscated or minified code
- installers, update hooks, or bootstrap scripts that pull in additional code

If disallowed content is present (compiled binaries, obfuscated code, auto-downloading installers), return `not approved`.

If higher-risk but reviewable content is present, flag it explicitly and require the user to confirm they have reviewed it before returning `approved`.

### 6. Apply policy

Apply the full approval rules from `docs/external-skills.md`. All of the following must be true for `approved`:

- upstream repository, skill path, and pinned commit SHA are identified
- repository owner or maintainers are known and trusted for the intended use
- skill content is readable and reviewable
- license is clear enough to allow the intended use
- any scripts or executable helpers are small enough to review directly and acceptable for project-local use

### 7. Classify

Return one of:
- `approved` — all checks pass
- `not approved` — at least one hard blocker (no SHA, bad license, disallowed content)
- `needs manual review` — inputs are incomplete or a check cannot be resolved automatically

### 8. Emit output

See **Required output** below.

If `approved` or reusing an approved catalog entry:
- describe the catalog entry to write
- provide Agent Skills CLI command examples

If `not approved` or `needs manual review`:
- explain what is missing or what blocks approval
- do not emit install commands

## Required output

Return all five items in this order:

1. **Result** — `approved`, `not approved`, or `needs manual review`
2. **Rationale** — short explanation tied to specific policy checks
3. **Provenance fields** — the fields the user should preserve or update in the catalog:
   - `repo`
   - `skill_path`
   - `pinned_ref`
   - `targets`
   - `license`
   - `review_status`
   - `reviewer`
   - `review_date`
   - `notes`
4. **Next steps** — what the user should do after this review
5. **Install commands** — only when result is `approved` or reusing an approved catalog entry

Example install commands (replace placeholders):

```sh
npx agent-skills-cli install owner/repo#COMMIT_SHA --skill skill-path -a claude,codex
```

## Catalog model

The catalog lives at `.agents/approved-external-skills.json` in the target workspace. It is a JSON array of provenance entries.

Example entry:

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

Use the bundled script to read and write the catalog reliably:

```sh
# Look up an entry
python3 skills/external-skill-review/scripts/catalog.py get owner/repo skills/example

# Add or update an entry (pass JSON string)
python3 skills/external-skill-review/scripts/catalog.py add '{"repo":"owner/repo","skill_path":"skills/example",...}'
```

The home directory is not the source of truth. Keep the catalog project-local.

## Constraints

- Never auto-install. This skill reviews, catalogs, and recommends only.
- Do not emit install commands unless the result is `approved` or the entry being reused is `approved`.
- Do not approve when any required field is unknown or incomplete.
- Treat branch or tag refs as documented exceptions, not the default.
- Treat each upstream update as a new review event with a new commit SHA.
- Do not override `docs/external-skills.md`.
