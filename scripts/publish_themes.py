#!/usr/bin/env python3
"""
Name: publish_themes.py
Path: scripts/publish_themes.py
Purpose: Sync themes from sum-platform to sum-themes distribution repo
Dependencies: None (stdlib only)
"""

from __future__ import annotations

import argparse
import fnmatch
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ThemeSyncConfig:
    source_repo_path: Path
    themes_repo_url: str
    themes_repo_branch: str = "main"
    themes_repo_path: Path | None = None
    source_themes_dir: str = "themes"
    dest_themes_dir: str = "themes"
    exclude_patterns: list[str] = field(default_factory=list)


DEFAULT_THEMES_REPO_URL = "git@github.com:markashton480/sum-themes.git"
DEFAULT_THEMES_REPO_PATH = Path("/tmp/sum-themes-sync")

DEFAULT_EXCLUDE_PATTERNS: list[str] = [
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".DS_Store",
    "node_modules",
    ".venv",
]


def run_cmd(
    cmd: list[str],
    cwd: Path | None = None,
    capture: bool = False,
) -> str:
    """Run a command and return output if capture=True."""
    if capture:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    subprocess.run(cmd, cwd=cwd, check=True)
    return ""


def should_exclude(path: Path, config: ThemeSyncConfig) -> bool:
    """Check if path should be excluded based on patterns."""
    name = path.name
    return any(fnmatch.fnmatch(name, pattern) for pattern in config.exclude_patterns)


def ensure_clean_repo(repo_path: Path) -> None:
    """Ensure repo has no uncommitted changes."""
    status = run_cmd(["git", "status", "--porcelain"], cwd=repo_path, capture=True)
    if status:
        raise RuntimeError(
            f"Repository at {repo_path} has uncommitted changes:\n{status}"
        )


def clone_or_update_themes_repo(config: ThemeSyncConfig) -> Path:
    """Clone themes repo if needed, otherwise fetch and reset to origin/main."""
    themes_path = config.themes_repo_path or DEFAULT_THEMES_REPO_PATH

    if not themes_path.exists():
        print(f"Cloning themes repo into {themes_path}...")
        run_cmd(["git", "clone", config.themes_repo_url, str(themes_path)])
    else:
        print(f"Updating themes repo at {themes_path}...")
        run_cmd(["git", "fetch", "origin"], cwd=themes_path)

    run_cmd(["git", "checkout", config.themes_repo_branch], cwd=themes_path)
    run_cmd(
        ["git", "reset", "--hard", f"origin/{config.themes_repo_branch}"],
        cwd=themes_path,
    )
    run_cmd(["git", "clean", "-fd"], cwd=themes_path)

    return themes_path


def copy_path(src: Path, dst: Path, config: ThemeSyncConfig) -> None:
    """Copy file or directory from src to dst, respecting exclusions."""
    if should_exclude(src, config):
        return

    if src.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
        for child in src.iterdir():
            copy_path(child, dst / child.name, config)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def sync_themes(config: ThemeSyncConfig, themes_repo_path: Path) -> list[str]:
    """Sync theme directories into the themes repo."""
    source_root = config.source_repo_path / config.source_themes_dir
    if not source_root.exists():
        raise RuntimeError(f"Missing source themes directory: {source_root}")

    dest_root = themes_repo_path / config.dest_themes_dir
    if dest_root.exists():
        shutil.rmtree(dest_root)
    dest_root.mkdir(parents=True, exist_ok=True)

    theme_dirs = sorted(
        path
        for path in source_root.iterdir()
        if path.is_dir() and not should_exclude(path, config)
    )

    if not theme_dirs:
        raise RuntimeError(f"No theme directories found in {source_root}")

    for theme_dir in theme_dirs:
        print(f"  {theme_dir.name}/ -> {config.dest_themes_dir}/{theme_dir.name}/")
        copy_path(theme_dir, dest_root / theme_dir.name, config)

    return [theme_dir.name for theme_dir in theme_dirs]


def commit_and_push(
    repo_path: Path,
    source_sha: str,
    theme_names: list[str],
    push: bool = True,
) -> bool:
    """Commit changes and optionally push to remote."""
    status = run_cmd(["git", "status", "--porcelain"], cwd=repo_path, capture=True)
    if not status:
        return False

    if not push:
        print("Dry run: skipping commit and push.")
        print("Pending changes:")
        print(status)
        return True

    run_cmd(["git", "add", "-A"], cwd=repo_path)

    themes_summary = ", ".join(theme_names)
    commit_msg = (
        "chore(sync): publish themes\n\n"
        f"Source: {source_sha}\n"
        f"Themes: {themes_summary}"
    )
    run_cmd(["git", "commit", "-m", commit_msg], cwd=repo_path)
    run_cmd(["git", "push", "origin", "main"], cwd=repo_path)
    return True


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Sync themes from sum-platform to sum-themes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (no commit/push)
  python scripts/publish_themes.py --dry-run

  # Publish to default repo
  python scripts/publish_themes.py

  # Publish to a specific clone path
  python scripts/publish_themes.py --themes-repo-path /tmp/sum-themes-sync
        """,
    )
    parser.add_argument(
        "--source-repo",
        type=Path,
        default=Path.cwd(),
        help="Path to sum-platform repo (default: current directory)",
    )
    parser.add_argument(
        "--themes-repo-url",
        default=DEFAULT_THEMES_REPO_URL,
        help="Git URL for sum-themes repo (default: %(default)s)",
    )
    parser.add_argument(
        "--themes-repo-path",
        type=Path,
        default=None,
        help="Path to local sum-themes clone (default: /tmp/sum-themes-sync)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not commit or push changes",
    )
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    config = ThemeSyncConfig(
        source_repo_path=args.source_repo.resolve(),
        themes_repo_url=args.themes_repo_url,
        themes_repo_path=(
            args.themes_repo_path.resolve() if args.themes_repo_path else None
        ),
        exclude_patterns=DEFAULT_EXCLUDE_PATTERNS,
    )

    try:
        print("=" * 60)
        print("SUM Platform -> sum-themes sync")
        print("=" * 60)

        if args.dry_run:
            print("Dry run enabled: no commit or push will occur.\n")

        print("Checking source repo status...")
        ensure_clean_repo(config.source_repo_path)

        print("\nUpdating sum-themes repo...")
        themes_repo_path = clone_or_update_themes_repo(config)

        print("\nSyncing themes...")
        theme_names = sync_themes(config, themes_repo_path)

        source_sha = run_cmd(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=config.source_repo_path,
            capture=True,
        )

        print("\nCommitting changes...")
        had_changes = commit_and_push(
            themes_repo_path,
            source_sha,
            theme_names,
            push=not args.dry_run,
        )

        if not had_changes:
            print("No changes to commit (already up to date).")

        print("\nSync complete.")
        return 0

    except subprocess.CalledProcessError as exc:
        print(f"Command failed: {exc}")
        return 1
    except RuntimeError as exc:
        print(f"Error: {exc}")
        return 1
    except KeyboardInterrupt:
        print("Aborted by user.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
