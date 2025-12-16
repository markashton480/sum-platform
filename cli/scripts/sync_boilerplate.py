#!/usr/bin/env python3
"""
Sync canonical /boilerplate/ to CLI package boilerplate.

This script ensures the bundled boilerplate in cli/sum_cli/boilerplate/
stays in sync with the canonical /boilerplate/ directory.

Usage:
    python cli/scripts/sync_boilerplate.py        # Sync (copy files)
    python cli/scripts/sync_boilerplate.py --check  # Check for drift (CI mode)
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path


def get_repo_root() -> Path:
    """Get the repository root directory."""
    script_dir = Path(__file__).resolve().parent
    # cli/scripts -> cli -> repo_root
    return script_dir.parent.parent


def get_canonical_boilerplate() -> Path:
    """Get the canonical boilerplate directory."""
    return get_repo_root() / "boilerplate"


def get_cli_boilerplate() -> Path:
    """Get the CLI package boilerplate directory."""
    return get_repo_root() / "cli" / "sum_cli" / "boilerplate"


def compare_directories(dir1: Path, dir2: Path) -> list[str]:
    """
    Compare two directories recursively.

    Returns a list of differences (empty if identical).
    """
    differences: list[str] = []

    # Get all files from both directories
    dir1_files: set[str] = set()
    dir2_files: set[str] = set()

    for f in dir1.rglob("*"):
        if f.is_file() and "__pycache__" not in str(f):
            rel = f.relative_to(dir1)
            dir1_files.add(str(rel))

    for f in dir2.rglob("*"):
        if f.is_file() and "__pycache__" not in str(f):
            rel = f.relative_to(dir2)
            dir2_files.add(str(rel))

    # Files only in canonical
    only_in_canonical = dir1_files - dir2_files
    for rel_path in sorted(only_in_canonical):
        differences.append(f"+ {rel_path} (missing from CLI boilerplate)")

    # Files only in CLI
    only_in_cli = dir2_files - dir1_files
    for rel_path in sorted(only_in_cli):
        differences.append(f"- {rel_path} (extra in CLI boilerplate)")

    # Files in both - check for content differences
    common_files = dir1_files & dir2_files
    for rel_path in sorted(common_files):
        f1 = dir1 / rel_path
        f2 = dir2 / rel_path
        if not filecmp.cmp(f1, f2, shallow=False):
            differences.append(f"~ {rel_path} (content differs)")

    return differences


def sync_boilerplate(canonical: Path, cli_bp: Path) -> None:
    """Sync canonical boilerplate to CLI package."""
    # Remove existing CLI boilerplate (except __pycache__)
    if cli_bp.exists():
        for item in cli_bp.iterdir():
            if item.name == "__pycache__":
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    # Copy canonical to CLI
    for item in canonical.iterdir():
        if item.name == "__pycache__":
            continue
        dest = cli_bp / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync canonical boilerplate to CLI package"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for drift without syncing (CI mode)",
    )
    args = parser.parse_args()

    canonical = get_canonical_boilerplate()
    cli_bp = get_cli_boilerplate()

    if not canonical.exists():
        print(f"ERROR: Canonical boilerplate not found: {canonical}", file=sys.stderr)
        return 1

    if not cli_bp.exists():
        print(f"ERROR: CLI boilerplate not found: {cli_bp}", file=sys.stderr)
        return 1

    if args.check:
        differences = compare_directories(canonical, cli_bp)
        if differences:
            print("Boilerplate drift detected:", file=sys.stderr)
            for diff in differences:
                print(f"  {diff}", file=sys.stderr)
            print("")
            print("Run 'make sync-cli-boilerplate' to sync.", file=sys.stderr)
            return 1
        else:
            print("[OK] CLI boilerplate is in sync with canonical boilerplate.")
            return 0
    else:
        print(f"Syncing {canonical} -> {cli_bp}")
        sync_boilerplate(canonical, cli_bp)
        print("[OK] Boilerplate synced successfully.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
