#!/usr/bin/env python3
"""CLI tests for growing_agents_md.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("growing_agents_md.py")
EXPECTED_SCAFFOLD = """# Agent Guidelines

<!-- Do not restructure or delete sections. Update individual values in-place when they change. -->

## Core Principles

- Keep this file under 20-30 lines of visible guidance.
- Keep only repo-specific, non-obvious instructions here.

## Project Overview

<!-- Replace this section in-place. Remove the placeholder line once filled. -->
- [TODO: add stable repo overview]

## Commands

<!-- Replace this section in-place. Remove the placeholder block once filled. -->
~~~sh
# [TODO: add only high-value commands]
~~~

## Code Conventions

<!-- Replace this section in-place. Remove the placeholder line once filled. -->
- [TODO: add only non-obvious repo-specific conventions]

## Architecture

<!-- Replace this section in-place. Remove the placeholder line once filled. -->
- [TODO: add only stable architecture boundaries or entry points]

## Maintenance Notes

<!-- This section is permanent. Do not delete. -->
- Delete stale or inferable guidance.
- Update commands and architecture when workflows change.
- Keep durable rules here; move detail to dedicated docs.
"""


def run_script(
    cwd: Path,
    *args: str,
    input_text: str | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(cwd),
        input=input_text,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed: {sys.executable} {SCRIPT} {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: dict[str, list[str]]) -> None:
    write(path, json.dumps(payload, indent=2) + "\n")


class GrowingAgentsMdTests(unittest.TestCase):
    def test_lint_fails_when_agents_md_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_script(Path(tmp), "lint", check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("does not exist", result.stderr)

    def test_init_creates_literal_scaffold_and_lint_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            run_script(root, "init")

            self.assertEqual((root / "AGENTS.md").read_text(encoding="utf-8"), EXPECTED_SCAFFOLD)
            lint = run_script(root, "lint")
            self.assertEqual(lint.returncode, 0)

    def test_init_fails_without_rewriting_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = "# custom\n"
            write(root / "AGENTS.md", original)

            result = run_script(root, "init", check=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((root / "AGENTS.md").read_text(encoding="utf-8"), original)

    def test_apply_populates_sections_and_removes_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_script(root, "init")
            payload_path = root / "apply.json"
            write_json(
                payload_path,
                {
                    "project_overview": [
                        "- Stores reusable agent skills and small supporting docs.",
                    ],
                    "commands": [
                        "~~~sh",
                        "python3 -m unittest skills/growing-agents-md/scripts/test_growing_agents_md.py",
                        "~~~",
                    ],
                    "code_conventions": [
                        "- Keep skill text compact and operational.",
                    ],
                    "architecture": [
                        "- Script-backed skills keep deterministic rules in scripts/ and prose in SKILL.md.",
                    ],
                },
            )

            run_script(root, "apply", "--input", str(payload_path))

            text = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("## Project Overview", text)
            self.assertIn("## Commands", text)
            self.assertIn("## Code Conventions", text)
            self.assertIn("## Architecture", text)
            self.assertNotIn("[TODO:", text)
            self.assertIn("## Maintenance Notes", text)
            self.assertEqual(run_script(root, "lint").returncode, 0)

    def test_apply_removes_empty_or_missing_replaceable_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_script(root, "init")

            result = run_script(
                root,
                "apply",
                "--input",
                "-",
                input_text=json.dumps(
                    {
                        "project_overview": ["- Keeps only durable repo-specific guidance."],
                        "commands": [],
                    }
                ),
            )

            self.assertEqual(result.returncode, 0)
            text = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("## Project Overview", text)
            self.assertNotIn("## Commands", text)
            self.assertNotIn("## Code Conventions", text)
            self.assertNotIn("## Architecture", text)

    def test_lint_fails_when_placeholder_tokens_remain_in_populated_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "AGENTS.md",
                EXPECTED_SCAFFOLD.replace(
                    "- [TODO: add stable repo overview]",
                    "- Stable overview\n- [TODO: add stable repo overview]",
                ),
            )

            result = run_script(root, "lint", check=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Project Overview still contains placeholder tokens", result.stderr)

    def test_lint_fails_on_forbidden_catch_all_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "AGENTS.md",
                EXPECTED_SCAFFOLD.replace(
                    "## Maintenance Notes",
                    "## Notes\n\n- Generic filler.\n\n## Maintenance Notes",
                ),
            )

            result = run_script(root, "lint", check=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("forbidden catch-all heading found: Notes", result.stderr)

    def test_lint_fails_on_structural_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "AGENTS.md", EXPECTED_SCAFFOLD.replace("## Maintenance Notes\n", ""))

            result = run_script(root, "lint", check=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing permanent section: Maintenance Notes", result.stderr)

    def test_lint_fails_when_budget_is_exceeded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_script(root, "init")
            payload_path = root / "apply.json"
            write_json(
                payload_path,
                {
                    "project_overview": [f"- overview line {index}" for index in range(1, 27)],
                    "commands": ["~~~sh", "git status", "~~~"],
                    "code_conventions": [],
                    "architecture": [],
                },
            )

            result = run_script(root, "apply", "--input", str(payload_path), check=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("counted guidance lines exceed budget", result.stderr)

    def test_apply_hard_fails_on_noncanonical_target_without_rewriting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            broken = EXPECTED_SCAFFOLD.replace(
                "<!-- Replace this section in-place. Remove the placeholder line once filled. -->",
                "<!-- broken -->",
                1,
            )
            write(root / "AGENTS.md", broken)
            payload_path = root / "apply.json"
            write_json(payload_path, {"project_overview": ["- Stable repo summary."]})

            result = run_script(root, "apply", "--input", str(payload_path), check=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((root / "AGENTS.md").read_text(encoding="utf-8"), broken)


if __name__ == "__main__":
    unittest.main()
