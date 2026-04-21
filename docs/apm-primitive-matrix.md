# APM primitive matrix

APM CLI version: **0.8.12**  
Verified: 2026-04-21  
Fixture: local scratch package with `skills/sample/SKILL.md`, `.apm/prompts/sample.prompt.md`, `.apm/agents/sample.agent.md`, `.apm/instructions/sample.instructions.md`, `hooks/sample.json` (not committed to this repo).

## How to read this table

**Axis A — native**: Does the tool natively discover and invoke files placed in the listed directory? Values: `Yes`, `No`, `Partial`.

**Axis B — APM install destination**: Where does `apm install` place the file? Values:
- `native:<path>` — file landed in the tool's native directory
- `compile:<file>` — file only appears after `apm compile`
- `none` — APM did not deploy this primitive for this tool
- `untested` — APM has no target for this tool (Gemini)

**Classification**: `install-first` (Axis A ∈ {Yes, Partial} and Axis B starts with `native:`), `compile-first` (Axis B starts with `compile:`), `unsupported` otherwise.

**Evidence**: `[verified]` = ran `apm install` and observed the result; `[doc]` = stated in APM or tool documentation; `[unverified]` = neither.

**Install method note**: Skills are tested via subpath install (`apm install <pkg>/skills/<name>`). All other primitives are tested via full-package install of a package with `.apm/` layout.

---

## Matrix

| Tool | Primitive | Axis A — native | Axis B — APM install | Classification | Evidence | Notes |
|------|-----------|-----------------|----------------------|----------------|----------|-------|
| Claude Code | skills | Yes | `native:.claude/skills/` | install-first | [verified] | Subpath install; invoked as `/skill-name` slash commands |
| Claude Code | prompts | Yes | `native:.claude/commands/` | install-first | [verified] | APM deploys `.apm/prompts/*.prompt.md` → `.claude/commands/*.md`; Claude Code loads these as `/command-name` |
| Claude Code | agents | Yes | `native:.claude/agents/` | install-first | [verified] | APM deploys `.apm/agents/*.agent.md` → `.claude/agents/*.md` |
| Claude Code | instructions | Partial | `native:.claude/rules/` + `compile:CLAUDE.md` | install-first | [verified] | APM deploys to `.claude/rules/` on install and compiles into `CLAUDE.md` on `apm compile`; `.claude/rules/` is a newer path; CLAUDE.md is the canonical file Claude Code reads |
| Claude Code | hooks | Yes | `native:.claude/settings.json` (partial) | install-first | [verified] | APM integrates hooks into `settings.json`; in 0.8.12 the fixture hook produced `{"hooks":{}}` — content was recognised but not populated, likely a hook-format mismatch; Claude Code settings.json hooks are natively consumed |
| GitHub Copilot | skills | Partial | `native:.github/skills/` | install-first | [verified] | Copilot reads `.github/skills/` but lacks a native skill-invocation mechanism equivalent to Claude Code; files are accessible via `#file` references |
| GitHub Copilot | prompts | Yes | `native:.github/prompts/` | install-first | [verified] | Copilot's `#prompt:name` feature reads `.github/prompts/*.prompt.md` natively |
| GitHub Copilot | agents | Yes | `native:.github/agents/` | install-first | [verified] | Copilot reads `.github/agents/*.agent.md` for custom agent definitions |
| GitHub Copilot | instructions | Yes | `native:.github/instructions/` | install-first | [verified] | Copilot reads `.github/instructions/*.instructions.md` as coding instructions |
| GitHub Copilot | hooks | No | `native:.github/hooks/` | unsupported | [verified] | APM deploys to `.github/hooks/` but GitHub Copilot has no native hook execution mechanism; file is stored but not consumed |
| Cursor | skills | No | `native:.cursor/skills/` | unsupported | [verified] | APM deploys to `.cursor/skills/` but Cursor has no native skill-invocation concept; files are not consumed by the tool runtime |
| Cursor | prompts | No | `none` | unsupported | [verified] | APM 0.8.12 does not deploy prompts for the cursor target |
| Cursor | agents | Yes | `native:.cursor/agents/` | install-first | [verified] | Cursor reads `.cursor/agents/` for agent mode configurations |
| Cursor | instructions | Yes | `native:.cursor/rules/` | install-first | [verified] | APM deploys as `.cursor/rules/*.mdc` (converts to MDC format); Cursor reads `.cursor/rules/` for project context rules |
| Cursor | hooks | Unknown | `native:.cursor/hooks.json` | unsupported | [unverified] | APM deploys to `.cursor/hooks.json`; Cursor automation support via hooks.json is not confirmed in public docs — Axis A unknown, so cannot classify as install-first |
| OpenCode | skills | Yes | `native:.opencode/skills/` | install-first | [verified] | APM deploys to `.opencode/skills/`; OpenCode natively loads skills from this path |
| OpenCode | prompts | Yes | `native:.opencode/commands/` | install-first | [verified] | APM deploys `.apm/prompts/` → `.opencode/commands/`; OpenCode treats these as slash commands |
| OpenCode | agents | Yes | `native:.opencode/agents/` | install-first | [verified] | APM deploys to `.opencode/agents/`; OpenCode reads agent definitions from this path |
| OpenCode | instructions | No | `none` | unsupported | [verified] | APM 0.8.12 does not deploy instructions for the opencode target |
| OpenCode | hooks | No | `none` | unsupported | [verified] | APM 0.8.12 does not deploy hooks for the opencode target |
| Codex CLI | skills | Partial | `native:.agents/skills/` | install-first | [verified] | Detection trigger is `.codex/` directory; APM deploys skills to `.agents/skills/` (not `.codex/skills/`); Codex reads from `.agents/` directory but invocation model differs from Claude Code |
| Codex CLI | prompts | No | `none` | unsupported | [verified] | APM 0.8.12 does not deploy prompts for the codex target |
| Codex CLI | agents | Yes | `native:.codex/agents/` | install-first | [verified] | APM deploys `.apm/agents/` → `.codex/agents/*.toml` (converts to TOML format); Codex reads agent configs from `.codex/agents/` |
| Codex CLI | instructions | No | `none` | unsupported | [verified] | APM 0.8.12 does not deploy instructions for the codex target |
| Codex CLI | hooks | Unknown | `native:.codex/hooks.json` | unsupported | [unverified] | APM deploys to `.codex/hooks.json`; Codex hook support not confirmed in public docs — Axis A unknown, so cannot classify as install-first |
| Gemini CLI | skills | Unknown | `untested` | unsupported | [unverified] | APM 0.8.12 has no Gemini target; no `gemini` option in `apm install --target` or `apm compile --target`; Gemini CLI likely uses `.gemini/` as its config root but not exercised |
| Gemini CLI | prompts | Unknown | `untested` | unsupported | [unverified] | No APM Gemini target in 0.8.12 |
| Gemini CLI | agents | Unknown | `untested` | unsupported | [unverified] | No APM Gemini target in 0.8.12 |
| Gemini CLI | instructions | Partial | `untested` | unsupported | [doc] | Gemini CLI reads `GEMINI.md` as its instruction file (analogous to CLAUDE.md); APM `compile --target all` does not produce GEMINI.md in 0.8.12 |
| Gemini CLI | hooks | Unknown | `untested` | unsupported | [unverified] | No APM Gemini target in 0.8.12 |

---

## Detection triggers

APM auto-detects the project target by scanning for these markers:

| Marker present | Detected target |
|----------------|-----------------|
| `.claude/` directory | `claude` |
| `.github/` directory | `copilot` |
| `.cursor/` directory | `cursor` |
| `.opencode/` directory | `opencode` |
| `.codex/` directory | `codex` |
| None of the above | `copilot` (fallback; APM creates `.github/`) |
| `AGENTS.md` present (no `.claude/`) | `copilot` (not codex) |
| `.agents/` present alone | `copilot` (not codex; see Codex CLI skills row) |

Multiple markers → multiple targets. Install deploys to all detected targets simultaneously.

---

## Conclusion

### Install-first safe (both axes satisfied)

| Tool | Primitives |
|------|-----------|
| Claude Code | skills, prompts, agents, instructions |
| GitHub Copilot | prompts, agents, instructions |
| Cursor | agents, instructions |
| OpenCode | skills, prompts, agents |
| Codex CLI | skills (Axis A = Partial), agents |

### Needs verification or unsupported

| Situation | Cells |
|-----------|-------|
| APM deploys, Axis A unconfirmed (classified unsupported) | Cursor hooks, Codex hooks |
| APM deploys but tool doesn't consume | GitHub Copilot hooks, Cursor skills |
| APM doesn't deploy in 0.8.12 | Cursor prompts, OpenCode instructions, OpenCode hooks, Codex prompts, Codex instructions |
| No APM target at all | All Gemini CLI cells |
| Hook content not populated (format gap) | Claude Code hooks |

### Compile-first

No cells are classified `compile-first` in 0.8.12 — `apm compile` produces `CLAUDE.md` and `AGENTS.md` from instructions, but the install path already deploys instructions natively for Claude Code (`.claude/rules/`) and GitHub Copilot (`.github/instructions/`). Compile remains a compatibility layer for tools without install-first support.

### APM 0.8.12 gaps to watch

1. **Gemini CLI**: No target exists. If Gemini support matters, verify against a newer APM version.
2. **Hook format for Claude Code**: `apm install` integrates the hook file but `settings.json` ends up with `{"hooks":{}}`. The APM hook JSON schema and Claude Code's settings.json hook schema need alignment. Re-verify when #31's hook design is finalised.
3. **Cursor hooks and Codex hooks**: APM deploys `.cursor/hooks.json` and `.codex/hooks.json` but native consumption by those tools is unconfirmed.
4. **Cursor skills**: APM deploys to `.cursor/skills/` but Cursor does not natively invoke SKILL.md files; these cells are classified `unsupported`.
