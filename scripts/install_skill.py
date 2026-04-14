#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


VALID_SKILL_NAME = re.compile(r"^[A-Za-z0-9_-][A-Za-z0-9._-]*$")
TARGETS: Dict[str, Tuple[str, str]] = {
    "claude": (".claude", "skills"),
    "codex": (".agents", "skills"),
    "gemini": (".agents", "skills"),
    "copilot": (".github", "skills"),
}


class InstallError(Exception):
    pass


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(
        prog="install-skill.sh",
        description="Install repository skills into a workspace.",
    )
    parser.add_argument("skill_name", metavar="skill-name|all")
    parser.add_argument(
        "target",
        nargs="?",
        default="codex",
        choices=sorted([*TARGETS, "all"]),
        metavar="target",
        help="agent target: claude, codex, copilot, gemini, or all",
    )
    parser.add_argument(
        "workspace_root",
        nargs="?",
        default=".",
        metavar="workspace-root",
        help="workspace root to install into",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="copy skill directories instead of creating relative symlinks",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace existing real directories or files",
    )
    if not argv:
        parser.print_help()
        raise SystemExit(0)
    return parser.parse_args(argv)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def validate_skill_name(skill_name: str) -> None:
    if skill_name == "all":
        return
    if not VALID_SKILL_NAME.fullmatch(skill_name) or ".." in skill_name:
        raise InstallError(f"Invalid skill name: {skill_name}")


def validate_source(source_dir: Path, skill_name: str) -> None:
    if not source_dir.is_dir():
        raise InstallError(f"Skill not found: {skill_name}")
    if not (source_dir / "SKILL.md").is_file():
        raise InstallError(f"Invalid skill '{skill_name}': missing {source_dir / 'SKILL.md'}")


def target_base_dirs(workspace_root: Path, target: str) -> List[Path]:
    if target != "all":
        return [workspace_root.joinpath(*TARGETS[target])]

    paths: List[Path] = []
    seen: Set[Path] = set()
    for target_name in ("claude", "codex", "gemini", "copilot"):
        path = workspace_root.joinpath(*TARGETS[target_name])
        resolved = path.resolve(strict=False)
        if resolved in seen:
            continue
        seen.add(resolved)
        paths.append(path)
    return paths


def remove_existing(target_dir: Path, force: bool) -> None:
    if target_dir.is_symlink():
        target_dir.unlink()
        return

    if not target_dir.exists():
        return

    if not force:
        raise InstallError(
            f"Refusing to replace existing non-symlink target: {target_dir}. "
            "Use --force to replace it."
        )

    if target_dir.is_dir():
        shutil.rmtree(target_dir)
    else:
        target_dir.unlink()


def install_skill(
    skill_name: str,
    source_dir: Path,
    target_base_dir: Path,
    *,
    copy: bool,
    force: bool,
) -> None:
    validate_source(source_dir, skill_name)

    target_dir = target_base_dir / skill_name
    target_base_dir.mkdir(parents=True, exist_ok=True)
    remove_existing(target_dir, force)

    if copy:
        shutil.copytree(source_dir, target_dir, symlinks=True)
        mode = "Copied"
    else:
        relative_source = os.path.relpath(
            source_dir.resolve(strict=True),
            start=target_base_dir.resolve(strict=False),
        )
        target_dir.symlink_to(relative_source, target_is_directory=True)
        mode = "Linked"

    print(f"{mode} {skill_name} -> {target_dir}")


def skill_names(skills_dir: Path, requested: str) -> List[str]:
    if requested != "all":
        return [requested]

    names = sorted(
        path.name
        for path in skills_dir.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    if not names:
        raise InstallError(f"No valid skills found in {skills_dir}")
    return names


def main() -> int:
    args = parse_args()
    validate_skill_name(args.skill_name)

    skills_dir = repo_root() / "skills"
    if not skills_dir.is_dir():
        raise InstallError(f"Skills directory not found: {skills_dir}")

    workspace_root = Path(args.workspace_root).expanduser()
    base_dirs = target_base_dirs(workspace_root, args.target)

    for skill_name in skill_names(skills_dir, args.skill_name):
        source_dir = skills_dir / skill_name
        for target_base_dir in base_dirs:
            install_skill(
                skill_name,
                source_dir,
                target_base_dir,
                copy=args.copy,
                force=args.force,
            )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InstallError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
