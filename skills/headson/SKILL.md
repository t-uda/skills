---
name: headson
description: Use this skill when inspecting large JSON, YAML, JSONL, text, source code, or Jupyter notebook files with structure-aware, budgeted previews using the hson CLI.
---

# Headson

Use this skill when a task requires a compact preview of structured or large text data before deciding what to inspect next.

`headson` is the package name. The CLI command is `hson`.

## When to use

Use `hson` for:

- large JSON, YAML, JSONL, NDJSON, logs, or text files
- Jupyter notebooks with large cell outputs, tracebacks, images, or HTML payloads
- source files when an outline-like preview is enough
- multi-file snapshots under a strict total budget
- grep-like inspection where matching keys, values, or lines must stay visible

Do not use `hson` when exact extraction, transformation, schema validation, or deterministic data processing is required. Use `jq`, Python, or a purpose-built parser for those tasks.

## Availability check

Before using this skill, check whether `hson` is installed:

```sh
command -v hson
hson --version
```

If it is missing, recommend an explicit user-controlled install.

Preferred pinned Cargo path:

```sh
cargo install headson --version 0.17.0 --locked
```

Homebrew convenience path, useful on macOS and Linuxbrew environments:

```sh
brew install headson
```

Prefer the pinned Cargo path when version control matters. Homebrew is convenient but may lag behind the latest Cargo release.

Do not recommend `pip install headson` as the primary CLI install path. The Python package provides Python bindings, not the normal `hson` CLI workflow expected here.

## Core commands

### Basic previews

```sh
hson -c 1200 data.json
hson -c 1200 -f json -t strict data.json
hson -c 1200 -f yaml -t detailed config.yaml
```

Use `-c, --bytes` for a per-file byte budget. Use `-u, --chars` for a per-file character budget. Use `-n, --lines` for a per-file line budget.

Use `-t strict` when the preview itself must be machine-readable. Use `-t default` or `-t detailed` for human inspection.

### JSONL and NDJSON

```sh
hson -c 1200 events.jsonl
hson -c 1200 events.ndjson
```

### Multi-file previews

```sh
hson -c 300 -C 2000 logs/*.json
hson --tree --glob 'src/**/*' -n 8 -N 120
```

Use `-C, --global-bytes` or `-N, --global-lines` when the entire output must stay within a shared budget.

Use `--tree` for a directory-tree view with inline previews.

### Grep-like inclusion

```sh
hson --grep 'error|warning|traceback' -c 800 -C 3000 logs/*.json
hson --igrep 'exception|failed|timeout' -c 800 -C 3000 logs/*.json
```

Use strong grep when matches must remain visible under tight budgets. Matching keys, values, or lines and their ancestors are preserved before the remaining budget is spent.

Use `--weak-grep` or `--weak-igrep` only when matches should be prioritised but not guaranteed.

### Head or tail bias

```sh
hson --head -c 1200 data.json
hson --tail -c 1200 data.json
```

Use `--head` to prefer early array entries. Use `--tail` to prefer late array entries. This affects arrays, not string truncation.

## Jupyter notebooks

`.ipynb` files are JSON, but handle them explicitly rather than relying on extension auto-detection. Force JSON ingestion and rendering:

```sh
hson -i json -f json -c 2500 --string-cap 120 notebook.ipynb
```

Prefer early cells:

```sh
hson -i json -f json --head -c 3000 --string-cap 120 notebook.ipynb
```

Prefer later cells and recent outputs:

```sh
hson -i json -f json --tail -c 3000 --string-cap 120 notebook.ipynb
```

Keep important output and error fields visible:

```sh
hson -i json -f json \
  --grep 'traceback|ename|evalue|text/plain|image/png|outputs|source' \
  -c 3000 --string-cap 120 notebook.ipynb
```

For notebooks with very large encoded image data, keep `--string-cap` low enough to preserve structure without flooding the context.

## Practical workflow

1. Start with a small preview budget.
2. Increase the per-file or global budget only if the first preview is insufficient.
3. Add `--grep` when the task names relevant keys, errors, warnings, or output types.
4. Use `--head` or `--tail` when the beginning or end of arrays is more relevant.
5. Switch to exact tools such as `jq` or Python once the required path or schema is known.

## Output expectations

When reporting findings from `hson`, state that the output is a preview, not the full file. Mention any budget, grep, head/tail, or string-cap settings that shaped the view when they affect the conclusion.
