# github-driven-workflow — bundled scripts

This README documents the operational details of the scripts bundled with this skill. The user-facing procedure lives in `SKILL.md`.

## `scripts/acquire-review.py`

Default implementation of §7 review acquisition. Reviewer-neutral by design: when the caller does not specify a kind, the script picks one uniformly at random from `{copilot, codex}` and dispatches a single review request. The bundled default never prefers a specific automatic reviewer.

| Kind | Effect | Stdout |
|------|--------|--------|
| `copilot` | Assigns the `copilot-pull-request-reviewer[bot]` reviewer to the PR. | `route: copilot (dispatched)` |
| `codex`   | Posts an `@codex please review this PR` comment on the PR.            | `route: codex (dispatched)` |

Both routes are asynchronous: stdout reports only that a request was *dispatched*. Evidence accrues separately on the PR and is checked by the §8 merge gate, not by this script.

### Contract

```
scripts/acquire-review.py <OWNER>/<REPO> <PR_NUMBER> [kind]
```

| Exit | Meaning |
|------|---------|
| `0`  | The route succeeded. Stdout: `route: <kind> (dispatched)`. |
| `1`  | Dispatch failed. Caller should record an authorized bypass per SKILL.md §7. |
| `64` | Usage error (missing arguments, too many arguments, or unknown kind). |
| `127`| Precondition error (e.g., `gh` CLI not on `PATH`). |

Pass an explicit `kind` only when the caller — or a project policy — requires a specific reviewer for this dispatch. Omit it for the reviewer-neutral default.

## Project override: `REVIEW_ACQUIRE_SCRIPT`

When `REVIEW_ACQUIRE_SCRIPT` is set in the environment to a path of an executable file, `scripts/acquire-review.py` will `exec` it with the same arguments. Its exit code and stdout surface unchanged.

```sh
export REVIEW_ACQUIRE_SCRIPT=/path/to/your/acquire-review
```

### Override contract

A project-specific override **must**:

- Accept `<OWNER>/<REPO> <PR_NUMBER>` as positional arguments. It **may** accept an optional `[kind]` third positional and **should** match the `{copilot, codex}` vocabulary; the bundled script forwards the third argument unchanged when present.
- Exit `0` on success and print `route: <name> (dispatched)` or `route: <name> (evidence)` to stdout. The route name is free-form but should be stable. The `(evidence)` token is reserved for routes that post a durable, machine-recognizable artifact on the PR (e.g. a `Reviewed-by:` comment) at dispatch time.
- Exit nonzero when no route succeeded. Callers treat any nonzero exit as "review not acquired" and proceed to authorized bypass (SKILL.md §7).

Implementations are encouraged but not required to use exit `64` for usage error and exit `127` for missing dependencies.

### Self-reference safety

The bundled script unsets `REVIEW_ACQUIRE_SCRIPT` from the environment before `exec`'ing the override. If the operator points the env var back at this script (or the override re-invokes the bundled script), the child process sees no override and falls through to built-in routes — no infinite recursion regardless of platform.

### Why an env var (not SKILL.md text)

The override mechanism is a *project environment* concern, not part of the skill's procedure. SKILL.md describes the procedure in skill-relative terms (`scripts/acquire-review.py`); the bundled script transparently honors the env-var override. Project setup (devcontainer config, direnv, orchestrator session) is the right place to wire `REVIEW_ACQUIRE_SCRIPT`.

## `scripts/test_acquire_review.sh`

Smoke tests for `acquire-review.py`. Shadows `gh` with a fake binary on `PATH` to drive each route without touching real GitHub. Run from this skill's root:

```sh
bash scripts/test_acquire_review.sh
```

Covers usage error (no args, too many args, unknown kind), missing-`gh` precondition, explicit `kind=copilot` / `kind=codex` success paths, dispatch failure, the kind-omitted reviewer-neutral random observation across many runs, and `REVIEW_ACQUIRE_SCRIPT` delegation (forwarding plain and `[kind]` arguments, plus the self-reference fall-through).
