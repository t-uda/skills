---
name: owner-file-request
description: Obtain a file or reference material that only the owner can supply and that is not already reachable from the workspace or a connected source. Use when the agent must request an inbound owner-to-agent handoff; prefer a connected Google Drive over an ad hoc upload. Not for publishing agent output or for general artifact management.
---

# Owner File Request

Get owner-supplied input into the agent's hands with one predictable handoff path.

## Handoff rule

- Prefer a source that is already connected or shared over asking for an upload.
- With a connected Google Drive, ask the owner to put the file in Drive (an existing shared folder if there is one) and reply with its name or link; read it through the connector.
- Otherwise use whatever channel the owner already uses with the agent.

Never offer the Git repository as the drop point, and commit received material only when the task itself makes it repository content.

## Runtime first step

- Claude Code: call the connected `claude.ai Google Drive` MCP tool `search_files` (load it with `ToolSearch` if it is deferred).
- Codex: call the connected apps MCP tool `mcp__codex_apps__google_drive_search`.

If the tool is absent, the integration is not connected in this session; say so and use the owner's usual channel instead.

## Out of scope

- Configuring or explaining the Drive integration.
- Outbound delivery of agent-produced artifacts.
- Cataloguing, versioning, or otherwise managing transferred files.
