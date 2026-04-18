#!/usr/bin/env python3
"""
Narrow helper for reading and writing the approved external skills catalog.

Catalog location: .agents/approved-external-skills.json (relative to cwd).

Usage:
  python3 catalog.py get <repo> <skill_path> <pinned_ref>
      Print the matching approved entry as JSON, or nothing if not found.
      All three fields must match. A different pinned_ref returns nothing.

  python3 catalog.py add <json-entry>
      Append or update an entry in the catalog.
      Matches on (repo, skill_path, pinned_ref). Adds a new entry if not found.
"""

import json
import pathlib
import sys
import tempfile

CATALOG_PATH = pathlib.Path(".agents/approved-external-skills.json")


def load() -> list[dict]:
    if not CATALOG_PATH.exists():
        return []
    try:
        entries = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"error: unable to read catalog {CATALOG_PATH}: {exc}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"error: catalog {CATALOG_PATH} contains invalid JSON: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(entries, list):
        print(f"error: catalog {CATALOG_PATH} must contain a JSON list", file=sys.stderr)
        sys.exit(1)
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            print(
                f"error: catalog {CATALOG_PATH} entry at index {i} must be a JSON object",
                file=sys.stderr,
            )
            sys.exit(1)
    return entries


def save(entries: list[dict]) -> None:
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(entries, indent=2) + "\n"
    tmp = pathlib.Path(tempfile.mktemp(dir=CATALOG_PATH.parent, prefix=".catalog-tmp-"))
    try:
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(CATALOG_PATH)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def cmd_get(repo: str, skill_path: str, pinned_ref: str) -> None:
    for entry in load():
        if entry.get("review_status") != "approved":
            continue
        if entry.get("repo") != repo:
            continue
        if entry.get("skill_path") != skill_path:
            continue
        if entry.get("pinned_ref") != pinned_ref:
            continue
        print(json.dumps(entry, indent=2))
        return


def cmd_add(raw: str) -> None:
    new_entry = json.loads(raw)
    repo = new_entry.get("repo")
    skill_path = new_entry.get("skill_path")
    pinned_ref = new_entry.get("pinned_ref")
    if not repo or not skill_path or not pinned_ref:
        print("error: entry must include 'repo', 'skill_path', and 'pinned_ref'", file=sys.stderr)
        sys.exit(1)
    entries = load()
    for i, entry in enumerate(entries):
        if (
            entry.get("repo") == repo
            and entry.get("skill_path") == skill_path
            and entry.get("pinned_ref") == pinned_ref
        ):
            entries[i] = new_entry
            save(entries)
            return
    entries.append(new_entry)
    save(entries)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        return

    command = sys.argv[1]
    if command == "get":
        if len(sys.argv) != 5:
            print("usage: catalog.py get <repo> <skill_path> <pinned_ref>", file=sys.stderr)
            sys.exit(1)
        cmd_get(sys.argv[2], sys.argv[3], sys.argv[4])
    elif command == "add":
        if len(sys.argv) != 3:
            print("usage: catalog.py add <json-entry>", file=sys.stderr)
            sys.exit(1)
        cmd_add(sys.argv[2])
    else:
        print(f"unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
