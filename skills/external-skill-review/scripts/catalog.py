#!/usr/bin/env python3
"""
Narrow helper for reading and writing the approved external skills catalog.

Catalog location: .agents/approved-external-skills.json (relative to cwd).

Usage:
  python3 catalog.py get <repo> <skill_path>
      Print the matching approved entry as JSON, or nothing if not found.

  python3 catalog.py add <json-entry>
      Append or update an entry in the catalog.
      Matches on (repo, skill_path). Overwrites an existing entry if found.
"""

import json
import pathlib
import sys

CATALOG_PATH = pathlib.Path(".agents/approved-external-skills.json")


def load() -> list[dict]:
    if not CATALOG_PATH.exists():
        return []
    return json.loads(CATALOG_PATH.read_text())


def save(entries: list[dict]) -> None:
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.write_text(json.dumps(entries, indent=2) + "\n")


def cmd_get(repo: str, skill_path: str) -> None:
    for entry in load():
        if entry.get("repo") == repo and entry.get("skill_path") == skill_path:
            print(json.dumps(entry, indent=2))
            return


def cmd_add(raw: str) -> None:
    new_entry = json.loads(raw)
    repo = new_entry.get("repo")
    skill_path = new_entry.get("skill_path")
    if not repo or not skill_path:
        print("error: entry must include 'repo' and 'skill_path'", file=sys.stderr)
        sys.exit(1)
    entries = load()
    for i, entry in enumerate(entries):
        if entry.get("repo") == repo and entry.get("skill_path") == skill_path:
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
        if len(sys.argv) != 4:
            print("usage: catalog.py get <repo> <skill_path>", file=sys.stderr)
            sys.exit(1)
        cmd_get(sys.argv[2], sys.argv[3])
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
