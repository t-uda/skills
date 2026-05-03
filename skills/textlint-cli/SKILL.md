---
name: textlint-cli
description: Use when running textlint from the command line in a repository that has, or is about to add, textlint configuration. Covers detection, repo-local invocation, fix mode, diagnostic flags, CI-oriented formats, MCP mode, and how to distinguish lint failures from tooling failures. Do not use to define a writing policy or to claim correctness beyond the configured rules.
---

# textlint CLI

Use this skill when a task requires running `textlint` against repository text and the operational concern is *how to invoke it correctly*, not *what writing rules to enforce*.

## When to use

Use this skill when:

- a repository already has `.textlintrc`, `.textlintrc.{js,json,yaml,yml}`, or a `textlint` key in `package.json`;
- a task asks to run textlint, fix textlint findings, or wire textlint into CI;
- an agent needs to lint Markdown, plain text, or other supported formats through textlint plugins.

Do not use this skill to:

- invent or recommend a writing policy that is not encoded in the repository's textlint config;
- treat textlint as a checker for factual, mathematical, or logical correctness;
- run `--fix` blindly across a repository.

## Configuration is the source of truth

textlint has no meaningful default policy. Without rules or presets it reports nothing useful.

Treat the following as the source of truth:

- `.textlintrc` or `.textlintrc.{js,json,yaml,yml}`;
- a `textlint` field in `package.json`;
- `.textlintignore` or a path passed to `--ignore-path`;
- any repository-local dictionaries or rule options referenced from those files.

If no config is present, stop and ask whether textlint should be configured before running it. Do not silently introduce a preset.

## Detect existing setup

Before running anything:

```sh
ls .textlintrc .textlintrc.js .textlintrc.json .textlintrc.yaml .textlintrc.yml 2>/dev/null
test -f package.json && jq -e '.textlint, .scripts.lint, .scripts["lint:text"], .devDependencies.textlint, .dependencies.textlint' package.json
test -f .textlintignore && echo "ignore file present"
```

If `package.json` defines a textlint script (commonly `lint:text`, `text-lint`, or `lint`), prefer that script over a raw CLI invocation so repository options stay consistent.

## Invocation

Prefer repository-local textlint. In order of preference:

1. `npm run <script>` (or the equivalent in `pnpm`, `yarn`, `bun`) when a textlint script exists.
2. `npx textlint ...` to use the locally installed binary.
3. `pnpm exec textlint ...` / `yarn textlint ...` / `bunx textlint ...` in repos that pin a non-npm package manager.

Avoid a globally installed `textlint`; it bypasses the repository's pinned version, plugins, and rules.

## Core commands

Lint specific files (preferred over globbing the entire repository):

```sh
npx textlint <files>
npx textlint --config .textlintrc <files>
```

Diff-scoped lint (only files touched on the current branch):

```sh
git diff --name-only --diff-filter=ACMR origin/main...HEAD -- '*.md' '*.txt' \
  | xargs -r npx textlint
```

Machine-readable output for agents:

```sh
npx textlint --format json <files>
```

GitHub Actions annotations:

```sh
npx textlint --format github <files>
```

Lint content from stdin (the filename matters because rules and plugins key on extension):

```sh
some-generator | npx textlint --stdin --stdin-filename example.md
```

Diagnostics:

```sh
npx textlint --print-config example.md
npx textlint --debug <files>
```

## Fix mode

`--fix` writes changes only for fixable rules. Many rules report without offering a fix.

Always preview first:

```sh
npx textlint --dry-run --fix <files>
```

Apply only after confirming the diff is safe and limited to the intended files:

```sh
npx textlint --fix <files>
```

Guidelines:

- run `--fix` on a clean working tree so the resulting diff is reviewable;
- scope `<files>` to the change under discussion, not the whole repository;
- do not chain `--fix` with broad globs in CI;
- after `--fix`, rerun textlint without `--fix` to confirm remaining issues are reported.

## Exit codes

In recent textlint (v15+), exit codes are:

- `0`: no errors;
- `1`: lint errors remain (policy violations);
- `2`: fatal error (configuration, plugin loading, file not found, internal failure).

Treat `1` and `2` as different categories:

- `1` is a content problem: report findings, optionally apply `--fix`, ask a human about ambiguous rules.
- `2` is a tooling problem: report the underlying error from `--debug` or stderr; do not pretend the text is clean.

If the running textlint version is older and conflates these, state the version (`npx textlint --version`) when reporting results.

## Ignoring files

Use `.textlintignore` (gitignore-style patterns) or `--ignore-path <file>` to exclude generated content, vendored text, or fixtures. Do not delete or weaken rules to silence findings in files that should simply be ignored.

## MCP mode

Recent textlint can run as an MCP server:

```sh
npx textlint --mcp
```

Use this when an MCP-aware agent needs to lint text or obtain fixed content while sharing the same repository configuration. MCP mode is optional; do not require it when CLI invocation is sufficient.

## Reporting findings

When reporting textlint results:

- distinguish policy violations (exit `1`) from tooling failures (exit `2`);
- include the rule id for each reported finding so a human can decide whether the rule applies;
- name the config file and textlint version that produced the result;
- state whether `--fix` was applied and which files changed;
- list any files skipped via `.textlintignore` if they were expected to be linted.

## References

- textlint CLI: https://textlint.org/docs/cli/
- textlint configuration: https://textlint.org/docs/configuring/
- textlint ignore: https://textlint.org/docs/ignore/
- textlint integrations: https://textlint.org/docs/integrations/
- textlint MCP: https://textlint.org/docs/mcp/
- textlint v15 release notes: https://textlint.org/blog/2025/06/22/textlint-15/
