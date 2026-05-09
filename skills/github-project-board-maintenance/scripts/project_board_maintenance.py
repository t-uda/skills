#!/usr/bin/env python3
"""Rate-limit-aware GitHub Projects v2 board maintenance helper.

Default mode is dry-run (read-only planning). Mutation requires --apply.
Stdout: single JSON object. Stderr: diagnostics.

dry-run is read-only **planning**, not no-cost: it still calls
gh api rate_limit, REST list endpoints, and at most one paginated
GraphQL Project snapshot. It performs no mutations.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

GRAPHQL_THRESHOLD_DEFAULT = 1000


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def run_gh(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def gh_auth_ok() -> bool:
    rc, _, _ = run_gh(["auth", "status"])
    return rc == 0


def gh_api_json(args: list[str]) -> tuple[bool, Any, str]:
    rc, out, err = run_gh(["api", *args])
    if rc != 0:
        # gh exits non-zero for partial GraphQL errors (e.g. user vs org ambiguity)
        # but still emits a JSON body with a "data" key — try to salvage it.
        try:
            parsed = json.loads(out)
            if isinstance(parsed, dict) and "data" in parsed:
                return True, parsed, ""
        except (json.JSONDecodeError, ValueError):
            pass
        return False, None, (err.strip() or out.strip())[:500]
    try:
        return True, json.loads(out), ""
    except json.JSONDecodeError as e:
        return False, None, f"json_decode: {e}"


def get_rate_limit() -> tuple[bool, dict, str]:
    ok, data, err = gh_api_json(["rate_limit"])
    if not ok:
        return False, {}, err
    return True, data.get("resources", {}), ""


def parse_iso(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts)


def fetch_recent(repo: str, since: datetime, kind: str) -> tuple[list[dict], list[dict]]:
    """Fetch recent issues (kind='issue') or PRs (kind='pr') via REST, paginated to cutoff."""
    endpoint = "/issues" if kind == "issue" else "/pulls"
    records: list[dict] = []
    errors: list[dict] = []
    page = 1
    while True:
        path = (
            f"/repos/{repo}{endpoint}"
            f"?state=all&per_page=100&sort=updated&direction=desc&page={page}"
        )
        ok, data, err = gh_api_json([path])
        if not ok:
            errors.append(
                {"reason": "gh_command_failed", "detail": f"GET {path}: {err}"}
            )
            break
        if not isinstance(data, list) or not data:
            break
        oldest = None
        for item in data:
            updated = parse_iso(item["updated_at"])
            oldest = updated
            if updated < since:
                continue
            if kind == "issue":
                if item.get("pull_request"):
                    continue
                records.append(
                    {
                        "type": "issue",
                        "number": item["number"],
                        "title": item.get("title", ""),
                        "state": item.get("state", ""),
                        "draft": False,
                        "merged": False,
                        "merged_at": None,
                        "updated_at": item["updated_at"],
                        "html_url": item.get("html_url", ""),
                    }
                )
            else:
                records.append(
                    {
                        "type": "pr",
                        "number": item["number"],
                        "title": item.get("title", ""),
                        "state": item.get("state", ""),
                        "draft": bool(item.get("draft", False)),
                        "merged": bool(item.get("merged_at")),
                        "merged_at": item.get("merged_at"),
                        "updated_at": item["updated_at"],
                        "html_url": item.get("html_url", ""),
                    }
                )
        if oldest is None or oldest < since:
            break
        page += 1
    return records, errors


PROJECT_QUERY = """
query($owner: String!, $number: Int!, $statusField: String!, $cursor: String) {
  organization(login: $owner) {
    projectV2(number: $number) { ...projFields }
  }
  user(login: $owner) {
    projectV2(number: $number) { ...projFields }
  }
}
fragment projFields on ProjectV2 {
  id
  title
  field(name: $statusField) {
    __typename
    ... on ProjectV2SingleSelectField {
      id
      name
      options { id name }
    }
  }
  items(first: 100, after: $cursor) {
    nodes {
      id
      content {
        __typename
        ... on Issue { number repository { nameWithOwner } }
        ... on PullRequest { number repository { nameWithOwner } }
      }
      fieldValueByName(name: $statusField) {
        __typename
        ... on ProjectV2ItemFieldSingleSelectValue { optionId name }
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
"""


def fetch_project_snapshot(
    owner: str, number: int, status_field: str
) -> tuple[bool, dict, str]:
    """Single paginated GraphQL snapshot of the Project."""
    cursor: str | None = None
    project_id: str | None = None
    field_id: str | None = None
    field_options: list[dict] = []
    items: list[dict] = []
    while True:
        args = [
            "graphql",
            "-f", f"query={PROJECT_QUERY}",
            "-F", f"owner={owner}",
            "-F", f"number={number}",
            "-f", f"statusField={status_field}",
        ]
        if cursor is not None:
            args += ["-f", f"cursor={cursor}"]
        ok, data, err = gh_api_json(args)
        if not ok:
            return False, {}, err
        d = data.get("data", {}) if isinstance(data, dict) else {}
        if isinstance(data, dict) and data.get("errors"):
            # Partial errors (e.g. user-not-found when owner is an org) are tolerated
            # as long as we can resolve the project from the data that did come back.
            proj_check = (
                (d.get("organization") or {}).get("projectV2")
                or (d.get("user") or {}).get("projectV2")
            )
            if not proj_check:
                return False, {}, json.dumps(data["errors"])[:500]
        proj = (
            (d.get("organization") or {}).get("projectV2")
            or (d.get("user") or {}).get("projectV2")
        )
        if not proj:
            return False, {}, f"project not found: {owner} #{number}"
        if project_id is None:
            project_id = proj["id"]
            field = proj.get("field") or {}
            if field.get("__typename") == "ProjectV2SingleSelectField":
                field_id = field.get("id")
                field_options = field.get("options") or []
        for node in proj["items"]["nodes"]:
            items.append(node)
        page = proj["items"]["pageInfo"]
        if not page["hasNextPage"]:
            break
        cursor = page["endCursor"]
    return True, {
        "project_id": project_id,
        "field_id": field_id,
        "field_options": field_options,
        "items": items,
    }, ""


def classify_candidate(c: dict) -> str:
    if c["type"] == "issue":
        return "closed_issue" if c["state"] == "closed" else "open_issue"
    if c.get("merged"):
        return "merged_pr"
    if c.get("draft"):
        return "draft_pr"
    return "open_pr"


def load_status_map(path: str) -> tuple[bool, dict, str]:
    try:
        with open(path) as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return False, {}, f"status_map_invalid: {e}"
    if not isinstance(data, dict):
        return False, {}, "status_map_invalid: top-level must be an object"
    return True, data, ""


def match_items(snapshot: dict, repo: str) -> dict[tuple[str, int], dict]:
    """Build (type, number) -> snapshot item index for the target repo."""
    repo_lc = repo.lower()
    out: dict[tuple[str, int], dict] = {}
    for node in snapshot["items"]:
        content = node.get("content") or {}
        typename = content.get("__typename")
        if typename not in ("Issue", "PullRequest"):
            continue
        repo_name = (content.get("repository") or {}).get("nameWithOwner") or ""
        if repo_name.lower() != repo_lc:
            continue
        kind = "issue" if typename == "Issue" else "pr"
        num = content.get("number")
        if num is None:
            continue
        key = (kind, int(num))
        if key in out:
            out[key] = {"_ambiguous": True}
        else:
            out[key] = node
    return out


APPLY_MUTATION = """
mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $project
    itemId: $item
    fieldId: $field
    value: { singleSelectOptionId: $option }
  }) {
    projectV2Item { id }
  }
}
"""


def apply_update(project_id: str, item_id: str, field_id: str, option_id: str) -> tuple[bool, str]:
    args = [
        "graphql",
        "-f", f"query={APPLY_MUTATION}",
        "-f", f"project={project_id}",
        "-f", f"item={item_id}",
        "-f", f"field={field_id}",
        "-f", f"option={option_id}",
    ]
    ok, data, err = gh_api_json(args)
    if not ok:
        return False, err
    if isinstance(data, dict) and data.get("errors"):
        return False, json.dumps(data["errors"])[:500]
    return True, ""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--repo", required=True, help="OWNER/REPO")
    p.add_argument("--since-hours", type=float, required=True)
    p.add_argument("--project-owner", help="user or org login that owns the Project")
    p.add_argument("--project-number", type=int)
    p.add_argument("--status-field", default="Status")
    p.add_argument("--status-map")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", default=False)
    mode.add_argument("--apply", action="store_true", default=False)
    p.add_argument("--allow-low-graphql-budget", action="store_true", default=False)
    p.add_argument(
        "--graphql-threshold",
        type=int,
        default=GRAPHQL_THRESHOLD_DEFAULT,
        help=f"GraphQL remaining-budget stop threshold (default {GRAPHQL_THRESHOLD_DEFAULT})",
    )
    args = p.parse_args()

    apply_mode = bool(args.apply)
    mode_label = "apply" if apply_mode else "dry-run"

    out: dict[str, Any] = {
        "summary": {"mode": mode_label},
        "rate_limit_before": {},
        "rate_limit_after": {},
        "candidates": [],
        "matched_items": [],
        "proposed_updates": [],
        "skipped": [],
        "errors": [],
    }
    if apply_mode:
        out["applied_updates"] = []

    if not re.match(r"^[^/]+/[^/]+$", args.repo):
        out["errors"].append({"reason": "bad_repo", "detail": "expected OWNER/REPO"})
        print(json.dumps(out, indent=2))
        return 2

    if apply_mode and not (args.project_owner and args.project_number):
        out["errors"].append(
            {
                "reason": "project_arguments_missing",
                "detail": "--apply requires --project-owner and --project-number",
            }
        )
        print(json.dumps(out, indent=2))
        return 2

    if apply_mode and not args.status_map:
        out["errors"].append(
            {"reason": "status_map_invalid", "detail": "--apply requires --status-map"}
        )
        print(json.dumps(out, indent=2))
        return 2

    if not gh_auth_ok():
        out["errors"].append({"reason": "gh_not_authenticated"})
        print(json.dumps(out, indent=2))
        return 2

    ok, rl_before, err = get_rate_limit()
    out["rate_limit_before"] = rl_before
    if not ok:
        out["errors"].append({"reason": "gh_command_failed", "detail": err})
        print(json.dumps(out, indent=2))
        return 2

    graphql_remaining = (rl_before.get("graphql") or {}).get("remaining", 0)
    low_budget = graphql_remaining < args.graphql_threshold

    since = datetime.now(timezone.utc) - timedelta(hours=args.since_hours)

    issues, ie = fetch_recent(args.repo, since, "issue")
    prs, pe = fetch_recent(args.repo, since, "pr")
    out["errors"].extend(ie)
    out["errors"].extend(pe)

    seen: set[tuple[str, int]] = set()
    candidates: list[dict] = []
    for rec in issues + prs:
        key = (rec["type"], rec["number"])
        if key in seen:
            continue
        seen.add(key)
        candidates.append(rec)
    out["candidates"] = candidates

    project_args_supplied = bool(args.project_owner and args.project_number)

    if not project_args_supplied:
        for c in candidates:
            out["skipped"].append(
                {
                    "type": c["type"],
                    "number": c["number"],
                    "reason": "project_arguments_missing",
                }
            )
        out["summary"].update(_summary(out))
        print(json.dumps(out, indent=2))
        return 0 if not apply_mode else 2

    if low_budget and not args.allow_low_graphql_budget:
        for c in candidates:
            out["skipped"].append(
                {
                    "type": c["type"],
                    "number": c["number"],
                    "reason": "low_graphql_budget",
                    "detail": (
                        f"graphql.remaining={graphql_remaining} "
                        f"< threshold={args.graphql_threshold}"
                    ),
                }
            )
        out["rate_limit_after"] = rl_before
        out["summary"].update(_summary(out))
        print(json.dumps(out, indent=2))
        return 0 if not apply_mode else 2

    status_map: dict = {}
    if args.status_map:
        ok, status_map, err = load_status_map(args.status_map)
        if not ok:
            out["errors"].append({"reason": "status_map_invalid", "detail": err})
            if apply_mode:
                print(json.dumps(out, indent=2))
                return 2

    if apply_mode:
        required_keys = {"closed_issue", "merged_pr", "open_issue", "open_pr", "draft_pr"}
        missing = sorted(required_keys - set(status_map.keys()))
        if missing or not args.status_map:
            out["errors"].append(
                {"reason": "status_map_invalid", "detail": f"missing keys: {missing or '<no file>'} (required in --apply)"}
            )
            print(json.dumps(out, indent=2))
            return 2

    ok, snapshot, err = fetch_project_snapshot(
        args.project_owner, int(args.project_number), args.status_field
    )
    ok2, rl_after, _ = get_rate_limit()
    out["rate_limit_after"] = rl_after if ok2 else {}
    if not ok:
        out["errors"].append({"reason": "gh_command_failed", "detail": err})
        out["summary"].update(_summary(out))
        print(json.dumps(out, indent=2))
        return 2

    if not snapshot.get("field_id"):
        out["errors"].append(
            {
                "reason": "unknown_status_option",
                "detail": (
                    f"status field {args.status_field!r} is not a single-select field "
                    "or was not found"
                ),
            }
        )
        out["summary"].update(_summary(out))
        print(json.dumps(out, indent=2))
        return 2

    name_to_option_id: dict[str, str] = {
        opt["name"]: opt["id"] for opt in snapshot["field_options"]
    }
    desired_option_id: dict[str, str | None] = {}
    for key, name in status_map.items():
        if name is None:
            desired_option_id[key] = None
            continue
        if name not in name_to_option_id:
            out["errors"].append(
                {
                    "reason": "unknown_status_option",
                    "detail": f"{key}={name!r} not in field options",
                }
            )
            desired_option_id[key] = None
        else:
            desired_option_id[key] = name_to_option_id[name]

    if apply_mode and any(
        v is None and status_map.get(k) is not None for k, v in desired_option_id.items()
    ):
        print(json.dumps(out, indent=2))
        return 2

    item_index = match_items(snapshot, args.repo)

    for c in candidates:
        key = (c["type"], c["number"])
        if key not in item_index:
            out["skipped"].append({"type": c["type"], "number": c["number"], "reason": "not_on_project"})
            continue
        node = item_index[key]
        if node.get("_ambiguous"):
            out["skipped"].append(
                {"type": c["type"], "number": c["number"], "reason": "ambiguous_project_item_match"}
            )
            continue
        current = node.get("fieldValueByName") or {}
        current_option_id = current.get("optionId")
        current_option_name = current.get("name")
        out["matched_items"].append(
            {
                "type": c["type"],
                "number": c["number"],
                "item_id": node["id"],
                "current_status_option_id": current_option_id,
                "current_status_option_name": current_option_name,
            }
        )
        policy_key = classify_candidate(c)
        if policy_key not in status_map:
            out["skipped"].append(
                {"type": c["type"], "number": c["number"], "reason": "no_status_policy", "detail": policy_key}
            )
            continue
        target_name = status_map[policy_key]
        if target_name is None:
            out["skipped"].append(
                {"type": c["type"], "number": c["number"], "reason": "no_status_policy", "detail": f"{policy_key}=null"}
            )
            continue
        target_option_id = desired_option_id.get(policy_key)
        if target_option_id is None:
            continue
        if current_option_id == target_option_id:
            out["skipped"].append(
                {"type": c["type"], "number": c["number"], "reason": "already_correct", "detail": target_name}
            )
            continue
        out["proposed_updates"].append(
            {
                "type": c["type"],
                "number": c["number"],
                "item_id": node["id"],
                "from_option_id": current_option_id,
                "from_option_name": current_option_name,
                "to_option_id": target_option_id,
                "to_option_name": target_name,
                "policy_key": policy_key,
            }
        )

    if apply_mode:
        for upd in out["proposed_updates"]:
            ok, err = apply_update(
                snapshot["project_id"], upd["item_id"], snapshot["field_id"], upd["to_option_id"]
            )
            if ok:
                out["applied_updates"].append(
                    {"type": upd["type"], "number": upd["number"], "item_id": upd["item_id"], "to_option_id": upd["to_option_id"]}
                )
            else:
                out["errors"].append(
                    {"reason": "gh_command_failed", "detail": f"apply {upd['number']}: {err}"}
                )
        ok2, rl_after, _ = get_rate_limit()
        out["rate_limit_after"] = rl_after if ok2 else out["rate_limit_after"]

    out["summary"].update(_summary(out))
    print(json.dumps(out, indent=2))
    return 0 if not out["errors"] else 1


def _summary(out: dict) -> dict:
    s = {
        "candidates": len(out["candidates"]),
        "matched": len(out["matched_items"]),
        "proposed": len(out["proposed_updates"]),
        "skipped": len(out["skipped"]),
        "errors": len(out["errors"]),
    }
    if "applied_updates" in out:
        s["applied"] = len(out["applied_updates"])
    return s


if __name__ == "__main__":
    sys.exit(main())
