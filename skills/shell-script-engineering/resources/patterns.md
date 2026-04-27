# Shell Script Engineering Patterns

Use these patterns as starting points. Adapt names and messages to the repository. Do not paste them blindly.

## Privilege escalation once

Use this when a script may run with `sudo`, as root, or without privilege escalation.

```bash
# "sudo" | "" (already root) | "none" (unprivileged)
if command -v sudo >/dev/null 2>&1; then
  _priv="sudo"
elif [ "$(id -u)" -eq 0 ]; then
  _priv=""
else
  _priv="none"
fi

_run() {
  if [ "$_priv" = "sudo" ]; then
    sudo "$@"
  else
    "$@"
  fi
}
```

Before calling `_run chown` or another privileged operation, guard the unprivileged case explicitly:

```bash
if [ "$_priv" = "none" ]; then
  echo "WARNING: cannot fix ownership without sudo or root; path may remain unwritable" >&2
else
  _run chown user:group "$target"
  _run chmod u+rwx "$target"
fi
```

## Container volume mount-root repair

Use this for Docker named volumes that should be writable by a non-root runtime user. Keep the operation non-recursive unless existing children must be repaired.

```bash
target="/workspaces/projects"

if [ "$_priv" != "none" ]; then
  _run mkdir -p "$target"
  _run chown vscode:vscode "$target"
  _run chmod u+rwx "$target"
else
  echo "WARNING: cannot fix ownership for $target without sudo or root" >&2
  mkdir -p "$target" 2>/dev/null || true
fi
```

Do not put large repository volumes into an array that is processed by `chown -R` or `chmod -R` on every container start.

## Directory usability check

Use this when a path must be a usable directory, not merely an existing path.

```bash
check_usable_dir() {
  local path="$1"

  if [ -d "$path" ] && [ -w "$path" ] && [ -x "$path" ]; then
    echo "PASS: $path present and writable"
  elif [ -d "$path" ]; then
    echo "WARN: $path present but not writable/searchable" >&2
    return 1
  elif [ -e "$path" ]; then
    echo "WARN: $path exists but is not a directory" >&2
    return 1
  else
    echo "WARN: $path not found" >&2
    return 1
  fi
}
```

## Safe idempotent line append

Use this for files such as `.gitignore`, where the script must append a line only if absent and must preserve correct line boundaries.

```bash
append_if_missing() {
  local file="$1"
  local entry="$2"

  if [ -f "$file" ] && grep -qxF "$entry" "$file"; then
    return 0
  fi

  if [ -f "$file" ] && [ -s "$file" ] && [ "$(tail -c 1 "$file" | wc -l)" -eq 0 ]; then
    printf '\n' >> "$file"
  fi

  printf '%s\n' "$entry" >> "$file"
}
```

## Argument contract validation

Use this shape for small provisioning scripts. Unknown flags and invalid combinations should fail rather than be silently ignored.

```bash
usage() {
  cat >&2 <<'USAGE'
usage:
  script.sh <dest> --baseline governance
  script.sh <dest> <item> [<item> ...]
USAGE
}

if [ "$#" -lt 2 ]; then
  usage
  exit 2
fi

dest="$1"
shift

if [ "$1" = "--baseline" ]; then
  if [ "$#" -ne 2 ]; then
    usage
    exit 2
  fi
  baseline="$2"
else
  items=("$@")
fi
```
