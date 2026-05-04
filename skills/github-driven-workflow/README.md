# github-driven-workflow — bundled scripts

This README documents the operational details of the scripts bundled with this skill. The user-facing procedure lives in `SKILL.md`.

## `scripts/acquire-review.sh`

Default implementation of §7 review acquisition. Tries, in order:

1. **Copilot reviewer assignment** — async, prints `route: copilot (dispatched)`.
2. **`@codex` mention comment** — async, prints `route: codex_mention (dispatched)`.
3. **Codex CLI artifact** — synchronous, prints `route: codex_cli (evidence)` and posts a `Reviewed-by: codex-cli` comment.

### Contract

```
scripts/acquire-review.sh <OWNER>/<REPO> <PR_NUMBER>
```

| Exit | Meaning |
|------|---------|
| `0`  | A route succeeded. Stdout: `route: <name> (dispatched\|evidence)`. `dispatched` means an async request was sent but evidence has not yet landed on the PR; `evidence` means a durable artifact is already posted. |
| `1`  | All routes failed. Caller should record an authorized bypass per SKILL.md §7. |
| `64` | Usage error (missing arguments). |
| `127`| Precondition error (e.g., `gh` CLI not on `PATH`). |

The §8 merge gate — not this script — decides whether `dispatched` routes have accrued enough evidence to merge.

## Project override: `REVIEW_ACQUIRE_SCRIPT`

When `REVIEW_ACQUIRE_SCRIPT` is set in the environment to a path of an executable file, `scripts/acquire-review.sh` will `exec` it with the same arguments. Its exit code and stdout surface unchanged.

```sh
export REVIEW_ACQUIRE_SCRIPT=/path/to/your/acquire-review.sh
```

### Override contract

A project-specific override **must**:

- Accept `<OWNER>/<REPO> <PR_NUMBER>` as positional arguments.
- Exit `0` on success and print one of `route: <name> (dispatched)` / `route: <name> (evidence)` to stdout. The route name is free-form but should be stable.
- Exit nonzero when no route succeeded. Callers treat any nonzero exit as "review not acquired" and proceed to authorized bypass (SKILL.md §7).

Implementations are encouraged but not required to use exit `64` for usage error and exit `127` for missing dependencies.

### Self-reference safety

The bundled script unsets `REVIEW_ACQUIRE_SCRIPT` from the environment before `exec`'ing the override. If the operator points the env var back at this script (or the override re-invokes the bundled script), the child process sees no override and falls through to built-in routes — no infinite recursion regardless of platform.

### Why an env var (not SKILL.md text)

The override mechanism is a *project environment* concern, not part of the skill's procedure. SKILL.md describes the procedure in skill-relative terms (`scripts/acquire-review.sh`); the bundled script transparently honors the env-var override. Project setup (devcontainer config, direnv, orchestrator session) is the right place to wire `REVIEW_ACQUIRE_SCRIPT`.

## `scripts/test_acquire_review.sh`

Smoke tests for `acquire-review.sh`. Shadows `gh` and `codex` with fake binaries on `PATH` to drive each route without touching real GitHub. Run from this skill's root:

```sh
bash scripts/test_acquire_review.sh
```

Covers usage error, missing-`gh` precondition, each route's success path, all-routes-failed, and `REVIEW_ACQUIRE_SCRIPT` delegation (including the self-reference fall-through).
