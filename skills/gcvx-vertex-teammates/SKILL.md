---
name: gcvx-vertex-teammates
description: Run a Claude Code team whose leader stays on the caller's provider while teammates run on Vertex AI through gcvx — session start, model policy, cost model, and mandatory teardown. Use when a session should offload teammate work to metered Vertex billing instead of the leader's subscription quota.
---

# gcvx Vertex teammates

Claude Code runs tmux-mode teammates as separate processes, so a leader and its
teammates can sit on different providers. `gcvx team` starts a leader on the
caller's own provider and routes teammates to Vertex AI. The in-session
teammate protocol is unaffected: teammates appear in the team list, and
`SendMessage` reaches a running one.

Use this when teammate work should be billed to Vertex rather than consume the
leader's subscription quota. Do not use it for a single short task — see Cost.

## Preconditions

Requires `gcvx` >= 0.2.0 (`uda-lab/gcvx`), `tmux`, and valid Google Cloud
Application Default Credentials. Verify all three at once:

```sh
gcvx doctor      # the "Teammates (gcvx team)" section must be ok
```

A failing ADC check means `gcloud auth application-default login` is needed;
that is the user's action, not the agent's.

## Starting a session

```sh
gcvx team              # options pass through to claude
```

The leader must be started this way. A plain `claude` session spawns
in-process teammates, which necessarily share the leader's provider — there is
no way to convert a running session.

## Model policy

Enforced in `gcvx claude-teammate` by argv rewrite, not by prose or
environment pinning: Claude Code passes the leader's chosen model on the
teammate's argv, and argv beats `ANTHROPIC_MODEL`. A model outside
`GCVX_TEAMMATE_ALLOWED_MODELS` is rewritten to `GCVX_TEAMMATE_MODEL` and a
warning appears in the teammate's pane.

Never route around this by editing a teammate's command line. To let teammates
reach another model, add both its alias and its explicit id to the allowlist in
`~/.config/gcvx/config` — the leader may request either form. Vertex
deployments enable a specific model set; an id absent from the deployment fails
or silently degrades to a neighbouring model, so confirm with a one-shot probe
before adding it:

```sh
gcvx claude --model <explicit-id> -p ok --output-format json   # check .modelUsage
```

## Cost

Each teammate pays a full session startup cost on its first request — system
prompt, `CLAUDE.md`, and skill metadata, tens of thousands of cache-creation
tokens before any work happens. This is charged per teammate, not per team.

Consequences:

- Prefer few long-lived teammates given substantial tasks over many
  short-lived ones.
- A teammate that answers one question is dominated by its own startup cost.
- Reuse an idle teammate with `SendMessage` instead of spawning a replacement.

## Teardown (mandatory)

Teammate processes outlive their pane. Killing the window, the tmux session, or
the leader leaves them running and holding memory. They must be reaped
explicitly:

```sh
pgrep -af 'claude --agent-id' # teammates of any session
kill <pids>
```

Do this when the team's work is done, before any memory-hungry build, and
before leaving a session. On a memory-constrained host, treat orphaned
teammates the same as any other leaked agent process.

## Verifying a teammate is really on Vertex

Two independent signals; check the process, not just the UI, because the leader
displays the model it *requested*:

```sh
tmux capture-pane -p -t <pane> | head       # banner: "... · Google Vertex AI"
tr '\0' '\n' < /proc/<pid>/environ | grep CLAUDE_CODE_USE_VERTEX
tr '\0' ' ' < /proc/<pid>/cmdline | grep -o '\--model [^ ]*'
```

## Failure modes

| Symptom | Cause |
|---|---|
| Teammates appear in-process, no new pane | Leader not started with `gcvx team` |
| `teammate launcher is missing` | `gcvx-teammate` not beside `gcvx`; reinstall gcvx |
| Teammate exits immediately | Model not enabled on the Vertex deployment; probe the explicit id |
| Leader itself is on Vertex | Vertex variables were exported before `gcvx team`; the leader must inherit the caller's provider |
| Memory pressure after the team finishes | Orphaned teammates; see Teardown |
