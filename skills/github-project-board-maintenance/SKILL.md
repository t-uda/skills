---
name: github-project-board-maintenance
description: Rate-limit-aware GitHub Projects v2 board maintenance — REST-first candidate discovery, single GraphQL snapshot, mechanical status-update planning, guarded apply. Use whenever a request asks to organise a Project board for issues/PRs updated within the last N hours.
---

# github-project-board-maintenance

Use this skill when the user asks to organise a GitHub Projects v2 board for
issues or PRs updated within a recent time window. The bundled script is the
operational source of truth. Do **not** start with ad hoc `gh project
item-list` — large item-list calls can consume a substantial part of the
hourly GraphQL budget.

## Core invocation

```sh
python3 scripts/project_board_maintenance.py \
  --repo OWNER/REPO \
  --since-hours 24 \
  --project-owner OWNER_OR_ORG \
  --project-number PROJECT_NUMBER \
  --status-field "Status" \
  --status-map status-map.json \
  --dry-run
```

Default mode is `--dry-run` (read-only planning) when neither `--dry-run` nor
`--apply` is given. The script always emits a single JSON object on stdout;
diagnostics go to stderr.

`--dry-run` is **read-only planning, not cost-free**: it still calls
`gh api rate_limit`, REST list endpoints, and one paginated GraphQL Project
snapshot. It performs no mutations.

## Status policy file

A name-based JSON map. The script resolves names against the snapshot's
field schema and never guesses transitions.

```json
{
  "closed_issue": "Done",
  "merged_pr": "Done",
  "open_issue": null,
  "open_pr": null,
  "draft_pr": null
}
```

- string value: propose updating to that status option (by **name**).
- `null`: inspect but do not propose a change.
- missing key in dry-run: treated as `null` (skipped with `no_status_policy`).
- missing key under `--apply`: the run halts with `status_map_invalid`.

## What the script does

1. **Preconditions** — `gh auth status` precheck. Failure produces
   `errors: [{reason: "gh_not_authenticated"}]` and exits without further calls.
2. **Rate-limit preflight** — `gh api rate_limit`, recorded as
   `rate_limit_before`. If `graphql.remaining < 1000` (configurable via
   `--graphql-threshold`) and `--allow-low-graphql-budget` is not set, the
   GraphQL snapshot is skipped and all candidates are reported as
   `low_graphql_budget`.
3. **REST candidate discovery** — paginates `/repos/.../issues` (filtering out
   PR rows) and `/repos/.../pulls`, sorted by `updated` descending, stopping
   when the page's oldest item is older than the cutoff. Dedupes by
   `(type, number)`.
4. **Single GraphQL snapshot** — when `--project-owner` and `--project-number`
   are supplied, the script issues one paginated `gh api graphql` query that
   returns: project ID, the configured single-select status field's ID and
   option list, and all Project items with their current status option.
   Repeated full-board scans are forbidden.
5. **Mechanical plan** — matches candidates to Project items by
   `(type, number)` against the target repo, classifies each candidate
   (`closed_issue`, `merged_pr`, `open_issue`, `open_pr`, `draft_pr`),
   resolves status-map names to option IDs locally, and emits
   `proposed_updates` only where current and target option IDs differ.
6. **Guarded apply** — `--apply` requires every required status-map key to be
   present and resolve to an option ID; otherwise the run halts. Mutations
   use the `updateProjectV2ItemFieldValue` GraphQL mutation. `rate_limit_after`
   is re-read after mutation.

## Output schema

```json
{
  "summary":          { "mode": "dry-run", "candidates": N, ... },
  "rate_limit_before": { "core": {...}, "graphql": {...} },
  "rate_limit_after":  { "core": {...}, "graphql": {...} },
  "candidates":       [ { "type", "number", "title", "state", "draft", "merged", "merged_at", "updated_at", "html_url" } ],
  "matched_items":    [ { "type", "number", "item_id", "current_status_option_id", "current_status_option_name" } ],
  "proposed_updates": [ { "type", "number", "item_id", "from_option_id", "from_option_name", "to_option_id", "to_option_name", "policy_key" } ],
  "skipped":          [ { "type", "number", "reason", "detail?" } ],
  "errors":           [ { "reason", "detail?" } ]
}
```

`applied_updates` is added under `--apply`.

### Skip reasons

- `not_on_project`
- `ambiguous_project_item_match`
- `no_status_policy`
- `already_correct`
- `low_graphql_budget`
- `project_arguments_missing`

### Error reasons

- `gh_not_authenticated`
- `unknown_status_option`
- `gh_command_failed`
- `status_map_invalid`
- `bad_repo`

## Agent invocation contract

The script is the safe workbench. Treat its JSON as the source of truth for
the candidate set, mechanically justified updates, skipped reasons, and
errors.

The agent must **not**:

- mutate Project items when the script reports `low_graphql_budget`,
  `ambiguous_project_item_match`, missing status policy, missing Project
  metadata, or `unknown_status_option`;
- broaden into repeated full-board scans to compensate for uncertain matching;
- guess status transitions not encoded in the explicit policy file;
- start a board-maintenance request with `gh project item-list`.

The agent **does** retain semantic judgement: reading issue/PR bodies,
comments, linked PRs, dependency state, blocked/priority/milestone judgement,
and any repo-specific workflow conventions not encoded in the policy file.
For items the script skips and the user asks about, read the issue/PR
directly and explain the situation rather than guessing.

## When to re-invoke

The script is idempotent within a single run. Re-run only when:

- the input changed (different `--repo`, `--since-hours`, `--status-map`,
  Project arguments, or threshold), or
- a previous `--dry-run` plan has been approved and you are switching to
  `--apply`, or
- the previous run reported `low_graphql_budget` and the budget has since
  recovered.

Do not loop the script hoping for a different classification.
