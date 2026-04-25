#!/usr/bin/env python3
"""Create, lint, and update the canonical AGENTS.md scaffold."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TITLE = "# Agent Guidelines"
FILE_GUARD = "<!-- Do not restructure or delete sections. Update individual values in-place when they change. -->"
CORE_HEADING = "Core Principles"
CORE_LINES = (
    "- Keep this file under 20-30 lines of visible guidance.",
    "- Keep only repo-specific, non-obvious instructions here.",
)
MAINTENANCE_HEADING = "Maintenance Notes"
MAINTENANCE_GUARD = "<!-- This section is permanent. Do not delete. -->"
MAINTENANCE_LINES = (
    "- Delete stale or inferable guidance.",
    "- Update commands and architecture when workflows change.",
    "- Keep durable rules here; move detail to dedicated docs.",
)
FORBIDDEN_HEADINGS = {"notes", "misc", "context", "important context", "other"}


@dataclass(frozen=True)
class ReplaceableSection:
    key: str
    heading: str
    comment: str
    placeholder_lines: tuple[str, ...]
    kind: str


REPLACEABLE_SECTIONS = (
    ReplaceableSection(
        key="project_overview",
        heading="Project Overview",
        comment="<!-- Replace this section in-place. Remove the placeholder line once filled. -->",
        placeholder_lines=("- [TODO: add stable repo overview]",),
        kind="bullets",
    ),
    ReplaceableSection(
        key="commands",
        heading="Commands",
        comment="<!-- Replace this section in-place. Remove the placeholder block once filled. -->",
        placeholder_lines=("~~~sh", "# [TODO: add only high-value commands]", "~~~"),
        kind="commands",
    ),
    ReplaceableSection(
        key="code_conventions",
        heading="Code Conventions",
        comment="<!-- Replace this section in-place. Remove the placeholder line once filled. -->",
        placeholder_lines=("- [TODO: add only non-obvious repo-specific conventions]",),
        kind="bullets",
    ),
    ReplaceableSection(
        key="architecture",
        heading="Architecture",
        comment="<!-- Replace this section in-place. Remove the placeholder line once filled. -->",
        placeholder_lines=("- [TODO: add only stable architecture boundaries or entry points]",),
        kind="bullets",
    ),
)
SECTION_BY_HEADING = {section.heading: section for section in REPLACEABLE_SECTIONS}
SECTION_BY_KEY = {section.key: section for section in REPLACEABLE_SECTIONS}
SECTION_ORDER = [CORE_HEADING, *(section.heading for section in REPLACEABLE_SECTIONS), MAINTENANCE_HEADING]
PLACEHOLDER_LINES = {line for section in REPLACEABLE_SECTIONS for line in section.placeholder_lines}
PLACEHOLDER_TODO_LINES = {line for line in PLACEHOLDER_LINES if "[TODO:" in line}


class ToolError(Exception):
    """Raised for actionable CLI failures."""


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage the canonical AGENTS.md scaffold.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create the canonical scaffold")
    init_parser.add_argument("--path", default="AGENTS.md", help="target AGENTS.md path")

    lint_parser = subparsers.add_parser("lint", help="lint the canonical scaffold")
    lint_parser.add_argument("--path", default="AGENTS.md", help="target AGENTS.md path")
    lint_parser.add_argument("--max-lines", type=int, default=30, help="maximum counted guidance lines")

    apply_parser = subparsers.add_parser("apply", help="rewrite replaceable sections from JSON input")
    apply_parser.add_argument("--path", default="AGENTS.md", help="target AGENTS.md path")
    apply_parser.add_argument("--input", required=True, help="JSON file path or '-' for stdin")
    apply_parser.add_argument("--max-lines", type=int, default=30, help="maximum counted guidance lines")

    return parser.parse_args(argv)


def fail(message: str) -> ToolError:
    return ToolError(message)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise fail(f"unable to read {path}: {exc}") from exc


def read_json_input(raw_path: str) -> dict[str, Any]:
    if raw_path == "-":
        try:
            raw = sys.stdin.read()
        except OSError as exc:
            raise fail(f"unable to read JSON from stdin: {exc}") from exc
    else:
        source = Path(raw_path)
        try:
            raw = source.read_text(encoding="utf-8")
        except OSError as exc:
            raise fail(f"unable to read input JSON {source}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise fail(f"input JSON is invalid: {exc}") from exc
    if not isinstance(data, dict):
        raise fail("input JSON must be an object keyed by section name")
    unexpected = sorted(set(data) - set(SECTION_BY_KEY))
    if unexpected:
        raise fail(f"input JSON contains unknown section keys: {', '.join(unexpected)}")
    return data


def write_validated_text(path: Path, text: str, max_lines: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.tmp-", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        lint_or_raise(tmp_path, max_lines)
        tmp_path.replace(path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def trimmed_body(lines: list[str]) -> list[str]:
    result = list(lines)
    while result and result[-1] == "":
        result.pop()
    return result


def collect_headings(lines: list[str]) -> tuple[list[tuple[int, str]], list[str]]:
    headings: list[tuple[int, str]] = []
    errors: list[str] = []
    in_code = False

    for index, line in enumerate(lines):
        if line == "~~~sh" and not in_code:
            in_code = True
            continue
        if line == "~~~" and in_code:
            in_code = False
            continue
        if in_code:
            continue
        if index == 0 and line == TITLE:
            continue
        if not line.startswith("#"):
            continue
        level = len(line) - len(line.lstrip("#"))
        if len(line) <= level or line[level] != " ":
            continue
        heading_text = line[level + 1 :].strip()
        if heading_text.lower() in FORBIDDEN_HEADINGS:
            errors.append(f"forbidden catch-all heading found: {heading_text}")
            continue
        if level == 2:
            headings.append((index, heading_text))
        else:
            errors.append(f"unexpected heading outside canonical schema: {line}")

    if in_code:
        errors.append("unterminated fenced code block")

    return headings, errors


def validate_top_matter(lines: list[str]) -> list[str]:
    errors: list[str] = []
    if not lines:
        return ["AGENTS.md is empty"]
    if lines[0] != TITLE:
        errors.append(f"first line must be {TITLE!r}")
    if len(lines) < 2 or lines[1] != "":
        errors.append("line 2 must be blank")
    if len(lines) < 3 or lines[2] != FILE_GUARD:
        errors.append("file guard comment is missing or modified")
    if len(lines) < 4 or lines[3] != "":
        errors.append("line 4 must be blank")
    return errors


def validate_heading_order(headings: list[tuple[int, str]]) -> list[str]:
    errors: list[str] = []
    names = [name for _index, name in headings]

    for name in names:
        if name not in SECTION_ORDER:
            errors.append(f"unexpected section heading: {name}")

    for name in SECTION_ORDER:
        if names.count(name) > 1:
            errors.append(f"section heading appears more than once: {name}")

    last_index = -1
    for name in names:
        if name not in SECTION_ORDER:
            continue
        current_index = SECTION_ORDER.index(name)
        if current_index <= last_index:
            errors.append(f"sections are out of canonical order near: {name}")
            break
        last_index = current_index

    for name in (CORE_HEADING, MAINTENANCE_HEADING):
        if name not in names:
            errors.append(f"missing permanent section: {name}")

    return errors


def validate_section_body(
    heading: str,
    body: list[str],
) -> list[str]:
    if heading == CORE_HEADING:
        expected = ["", *CORE_LINES]
        if body != expected:
            return [f"{heading} must match the canonical scaffold exactly"]
        return []

    if heading == MAINTENANCE_HEADING:
        expected = ["", MAINTENANCE_GUARD, *MAINTENANCE_LINES]
        if body != expected:
            return [f"{heading} must match the canonical scaffold exactly"]
        return []

    section = SECTION_BY_HEADING[heading]
    expected_prefix = ["", section.comment]
    if body[:2] != expected_prefix:
        return [f"{heading} must keep its canonical guard comment"]
    content = body[2:]
    if not content:
        return [f"{heading} must contain placeholder content or final content"]
    return validate_content_lines(section, content, allow_placeholder=True, context=heading)


def validate_content_lines(
    section: ReplaceableSection,
    content: list[str],
    *,
    allow_placeholder: bool,
    context: str,
) -> list[str]:
    if allow_placeholder and content == list(section.placeholder_lines):
        return []

    errors: list[str] = []
    if any(line in PLACEHOLDER_TODO_LINES or "[TODO:" in line for line in content):
        errors.append(f"{context} still contains placeholder tokens")
        return errors

    if section.kind == "bullets":
        for line in content:
            if not line.startswith("- "):
                errors.append(f"{context} must contain bullet lines only")
                break
        return errors

    if content[0] != "~~~sh" or content[-1] != "~~~":
        return [f"{context} must contain exactly one fenced sh block"]
    inner = content[1:-1]
    if not inner:
        return [f"{context} fenced sh block must not be empty"]
    if any(line.startswith("~~~") for line in inner):
        return [f"{context} must contain exactly one fenced sh block"]
    return errors


def counted_guidance_lines(lines: list[str]) -> int:
    count = 0
    in_code = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if line == "~~~sh" and not in_code:
            in_code = True
            continue
        if line == "~~~" and in_code:
            in_code = False
            continue
        if stripped in PLACEHOLDER_TODO_LINES:
            continue
        if not in_code:
            if stripped.startswith("<!--") and stripped.endswith("-->"):
                continue
            if stripped in {"---", "***", "___"}:
                continue
            if stripped.startswith("#"):
                continue
        count += 1
    return count


def lint_text(text: str, max_lines: int) -> list[str]:
    if max_lines <= 0:
        return ["--max-lines must be greater than zero"]

    lines = text.splitlines()
    errors = validate_top_matter(lines)
    headings, heading_errors = collect_headings(lines)
    errors.extend(heading_errors)
    errors.extend(validate_heading_order(headings))

    positions = {name: index for index, name in headings if name in SECTION_ORDER}
    end_of_file = len(lines)
    for section_index, heading in enumerate(SECTION_ORDER):
        if heading not in positions:
            continue
        start = positions[heading]
        later_positions = [
            positions[next_heading]
            for next_heading in SECTION_ORDER[section_index + 1 :]
            if next_heading in positions
        ]
        end = min(later_positions) if later_positions else end_of_file
        body = trimmed_body(lines[start + 1 : end])
        errors.extend(validate_section_body(heading, body))

    count = counted_guidance_lines(lines)
    if count > max_lines:
        errors.append(f"counted guidance lines exceed budget: {count} > {max_lines}")

    return errors


def lint_or_raise(path: Path, max_lines: int) -> None:
    if not path.exists():
        raise fail(f"{path} does not exist")
    errors = lint_text(read_text(path), max_lines)
    if errors:
        raise fail("\n".join(f"error: {message}" for message in errors))


def render_document(section_content: dict[str, list[str] | None]) -> str:
    lines = [TITLE, "", FILE_GUARD, "", f"## {CORE_HEADING}", "", *CORE_LINES, ""]
    for section in REPLACEABLE_SECTIONS:
        content = section_content[section.key]
        if not content:
            continue
        lines.extend([f"## {section.heading}", "", section.comment, *content, ""])
    lines.extend([f"## {MAINTENANCE_HEADING}", "", MAINTENANCE_GUARD, *MAINTENANCE_LINES])
    return "\n".join(lines) + "\n"


def scaffold_content() -> dict[str, list[str] | None]:
    return {section.key: list(section.placeholder_lines) for section in REPLACEABLE_SECTIONS}


def load_apply_content(data: dict[str, Any]) -> dict[str, list[str] | None]:
    rendered: dict[str, list[str] | None] = {}
    for section in REPLACEABLE_SECTIONS:
        raw_value = data.get(section.key)
        if raw_value is None:
            rendered[section.key] = None
            continue
        if not isinstance(raw_value, list):
            raise fail(f"{section.key} must be an array of markdown lines")
        if not raw_value:
            rendered[section.key] = None
            continue
        if not all(isinstance(item, str) for item in raw_value):
            raise fail(f"{section.key} must contain strings only")
        if any("\n" in item or "\r" in item for item in raw_value):
            raise fail(f"{section.key} items must be single markdown lines")
        errors = validate_content_lines(
            section,
            list(raw_value),
            allow_placeholder=False,
            context=section.key,
        )
        if errors:
            raise fail("\n".join(f"error: {message}" for message in errors))
        rendered[section.key] = list(raw_value)
    return rendered


def cmd_init(path: Path) -> None:
    if path.exists():
        raise fail(f"{path} already exists")
    write_validated_text(path, render_document(scaffold_content()), max_lines=30)


def cmd_lint(path: Path, max_lines: int) -> None:
    lint_or_raise(path, max_lines)


def cmd_apply(path: Path, input_path: str, max_lines: int) -> None:
    if not path.exists():
        raise fail(f"{path} does not exist")
    lint_or_raise(path, max_lines)
    content = load_apply_content(read_json_input(input_path))
    rendered = render_document(content)
    errors = lint_text(rendered, max_lines)
    if errors:
        raise fail("\n".join(f"error: {message}" for message in errors))
    write_validated_text(path, rendered, max_lines)
    lint_or_raise(path, max_lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    path = Path(args.path)

    try:
        if args.command == "init":
            cmd_init(path)
        elif args.command == "lint":
            cmd_lint(path, args.max_lines)
        elif args.command == "apply":
            cmd_apply(path, args.input, args.max_lines)
        else:
            raise fail(f"unknown command: {args.command}")
    except ToolError as exc:
        message = str(exc)
        if message:
            print(message, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
