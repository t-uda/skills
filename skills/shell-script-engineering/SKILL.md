---
name: shell-script-engineering
description: Use for non-trivial Bash/sh creation, edits, or review where correctness depends on execution context, permissions, filesystem mutation, argument parsing, idempotency, CI/container/devcontainer behaviour, or repeated shell-script review failures.
---

# Shell Script Engineering

Use this skill to write and review shell scripts that are safe, idempotent, and reviewable. The goal is not to make every script elaborate. The goal is to prevent common shell failures before they cause long review cycles.

## Operating stance

Treat shell as a small systems-integration language.

Use shell when the task is mostly invoking existing CLI tools, wiring files, or doing short environment setup. Prefer Python, Go, or another structured language when the script grows complex: non-trivial state, complex parsing, JSON/YAML transformation, long branching logic, concurrency, or large testable business logic.

## Before editing

For non-trivial changes, identify only the assumptions that affect correctness:

- Dialect: Bash or POSIX `sh`.
- Execution context: host, container, devcontainer, CI, login shell, or non-interactive shell.
- Privilege model: expected user, whether root may run it, and whether `sudo` is allowed.
- Filesystem model: bind mount, Docker named volume, symlinked path, generated directory, or repository file.
- Rerun model: whether the script must be idempotent.
- Failure model: fail fast, warn and continue, or collect errors.
- Argument contract: if the script accepts flags, subcommands, or positional arguments, define the exact accepted forms before editing.
- User-facing diagnostics: when the script emits remediation text, verify that command paths, script names, and suggested commands are executable from the documented working directory.

For Docker named volumes, do not stop at "the path exists". A new named volume may be mounted as `root:root`, while the runtime user may be non-root. Confirm where ownership is corrected: Dockerfile, postCreate, postStart, entrypoint, or manual remediation.

## Dialect policy

Be explicit. If the script uses arrays, `[[ ... ]]`, `pipefail`, `mapfile`, process substitution, or Bash-specific parameter expansion, use a Bash shebang and do not claim POSIX compatibility.

For Bash scripts, prefer:

```bash
#!/usr/bin/env bash
```

For POSIX scripts, avoid Bash-only features and validate with ShellCheck using the intended shell.

## Error handling policy

Do not argue about `set -euo pipefail` as a universal rule.

Use this decision rule:

- For short, mostly linear Bash scripts, `set -euo pipefail` is acceptable and often useful.
- For scripts with expected failures, probing commands, loops, cleanup, fallback branches, or partial success semantics, use explicit checks around commands that may fail.
- If using `set -e`, account for its known traps: conditionals, pipelines, command substitutions, arithmetic expressions such as `((i++))`, subshells, and cleanup paths.
- Do not hide errors with broad `|| true`. If a failure is acceptable, document why and constrain it locally.

Prefer explicit error exits for important operations:

```bash
if ! mkdir -p -- "$target_dir"; then
  echo "error: failed to create $target_dir" >&2
  exit 1
fi
```

For scripts with flags or subcommands, validate invalid combinations explicitly. Do not silently ignore extra arguments.

Use a dedicated usage error exit path:

```bash
usage() {
  echo "usage: $0 <dest> [--baseline governance | <skill> ...]" >&2
}

if [ "$#" -eq 0 ]; then
  usage
  exit 2
fi
```

When parsing options, define whether unknown flags, duplicate flags, missing operands, and extra operands are errors. Prefer fail-fast behaviour for provisioning scripts.

## Quoting and argument safety

- Quote variable expansions by default: `"$var"`.
- Use `--` before path operands when supported: `rm -rf -- "$tmpdir"`.
- Use arrays for command construction in Bash.
- Use `"$@"`, not `$*`, when forwarding arguments.
- Treat paths as possibly containing spaces, tabs, newlines, glob characters, and leading dashes.
- Avoid parsing `ls` output.

## Filesystem safety checklist

Before modifying the filesystem, check the relevant cases:

- Does the path already exist?
- Is it a regular file, directory, symlink, broken symlink, FIFO, or socket?
- Should symlinks be followed or treated as symlink objects?
- Is the parent directory present and writable?
- Is the operation safe when the variable is empty?
- Is the operation safe when run twice?
- Is the operation safe under root and non-root users?
- Does it cross a bind mount or named volume boundary?

For destructive operations, compute and validate the target first. Never run `rm -rf` on a path unless the variable is non-empty, expected, and constrained.

## Directory and diagnostic predicates

For diagnostic checks, enumerate the possible states before writing the branch logic. Avoid a final `else` branch that conflates "missing" with "exists but has the wrong type".

For a directory that must accept created files or cloned repositories, presence is not enough. Writability alone is also not enough: a usable directory normally needs directory type, write permission, and execute/search permission.

Prefer this shape:

```bash
if [ -d "$path" ] && [ -w "$path" ] && [ -x "$path" ]; then
  pass "path: $path present and writable"
elif [ -d "$path" ]; then
  warn "path: $path present but not writable/searchable" \
       "fix ownership or permissions for $path"
elif [ -e "$path" ]; then
  warn "path: $path exists but is not a directory" \
       "remove or replace the path"
else
  warn "path: $path not found" \
       "create or mount the expected directory"
fi
```

Keep remediation text exact. If the hint says to rerun a script, include the repository-relative or absolute path that the user can actually execute.

## Permission and ownership policy

Permission fixes must state the intended owner, group, and mode.

Check both existence and type before changing ownership or permissions. For container/devcontainer scripts, handle Docker named volumes carefully: first-created volume contents may be owned by `root:root`, while the runtime user may be `vscode` or another non-root user.

For mount points that may contain user repositories or caches, prefer changing only the mount root. Avoid recursive `chown -R` or `chmod -R` unless the target tree is known to be small or the recursive walk is explicitly required.

If recursive ownership or permission changes are used, document why a mount-root fix is insufficient.

For scripts that may run with `sudo`, as root, or as an unprivileged user, compute the privilege mode once and reuse it. Do not duplicate sudo/root/no-sudo branches for each path; duplicated privilege logic tends to drift during review iterations.

For sensitive directories, use restrictive modes:

- `.ssh`: directory `700`; private keys `600`; public keys `644`.
- auth/config directories: normally user-owned and not group/world writable.

## Symlink policy

Decide whether symlinks are valid inputs. If a script creates or overwrites paths, explicitly handle symlinks to avoid surprising writes outside the intended tree.

Use `realpath` only when canonicalisation is intended. Do not canonicalise away a symlink boundary accidentally.

## Temporary files and cleanup

Use `mktemp` or `mktemp -d`. Register cleanup with `trap` only after the temporary path has been created and validated.

```bash
tmpdir="$(mktemp -d)"
cleanup() {
  [[ -n "${tmpdir:-}" && -d "$tmpdir" ]] && rm -rf -- "$tmpdir"
}
trap cleanup EXIT
```

## Tooling baseline

When practical, run:

```bash
shellcheck path/to/script.sh
shfmt -d path/to/script.sh
# Bash scripts:
bash -n path/to/script.sh
# POSIX sh scripts (use the actual target shell, e.g. dash):
sh -n path/to/script.sh
```

For scripts with meaningful filesystem, permission, or CLI argument behaviour, add a small fixture test. Prefer Bats when the repository already uses shell testing or when the behaviour is naturally expressed as UNIX command execution.

Minimal behavioural tests should cover:

- first run;
- second run/idempotency;
- missing dependency or missing path;
- invalid argument combinations;
- file-vs-directory conflict;
- symlink case if relevant;
- non-root execution if relevant;
- no-sudo/no-root branch if relevant;
- failure output and exit code.

## Review convergence protocol

When reviewing shell-script PRs, make comments concrete.

A useful review comment should include:

- the failure scenario;
- why the current script mishandles it;
- a minimal fix direction;
- the validation command or test case that would catch it.

Avoid broad rewrites unless the script is already beyond shell's appropriate complexity. Prefer small, targeted patches that preserve the issue scope.

After responding to review comments, re-read the whole edited script once. Do not only patch the commented line. Check whether the fix changed the script's scope, duplicated an existing branch, made comments stale, or invalidated PR description / validation text.

If two or more review comments target the same script, pause and restate the relevant assumptions from "Before editing" before patching again.

## Final validation checklist

Before considering a shell-script change ready, verify:

- The dialect is explicit and consistent with the features used.
- ShellCheck findings are resolved or locally justified.
- shfmt either passes or the repository's existing formatting policy is followed.
- Important variables are quoted.
- CLI argument contracts are explicit; unknown flags and invalid combinations fail clearly.
- Filesystem mutations are idempotent.
- Permission and ownership changes are narrow and justified.
- Symlink/file/directory cases are handled where relevant.
- Destructive operations are guarded.
- Directory usability checks use type, write, and execute/search predicates where relevant.
- User-facing diagnostics and remediation hints name correct paths and commands.
- stdout and stderr are separated: machine-readable output on stdout, diagnostics on stderr.
- The PR body includes the commands used for validation.
