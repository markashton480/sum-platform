#!/usr/bin/env python3
"""
Name: sync_to_public.py
Path: scripts/sync_to_public.py
Purpose: Synchronize allowed paths from sum-platform (private) to sum-core (public)
Dependencies: None (stdlib only)
Family: Release automation (used by RELEASE_RUNBOOK.md, release-sync.yml)

This script handles the selective sync of public-facing code from the private
development monorepo to the public distribution repository.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class SyncConfig(NamedTuple):
    """Configuration for the sync operation."""

    # Source paths (relative to sum-platform root)
    # Format: (source_path, destination_path)
    # If destination is None, uses same path as source
    paths_to_sync: tuple[tuple[str, str | None], ...] = (
        ("core", None),
        ("boilerplate", None),
        ("docs/public", "docs"),  # Renamed on destination
        ("pyproject.toml", None),
        ("README.md", None),
        ("LICENSE", None),
    )

    # Paths to explicitly exclude (even if inside synced directories)
    paths_to_exclude: tuple[str, ...] = (
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        ".mypy_cache",
        ".coverage",
        "*.egg-info",
    )

    # Public repo details
    public_repo_url: str = "git@github.com:markashton480/sum-core.git"
    public_repo_name: str = "sum-core"

    # Working directory for clone
    work_dir: str = "/tmp/sum-core-sync"


def run_cmd(
    cmd: list[str],
    cwd: Path | None = None,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a shell command with error handling."""
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        capture_output=capture,
        text=True,
    )


def find_repo_root() -> Path:
    """Find the sum-platform repository root."""
    # Look for markers that indicate repo root
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / "core").is_dir() and (parent / "boilerplate").is_dir():
            return parent
    raise RuntimeError(
        "Could not find sum-platform root. "
        "Run this script from within the repository."
    )


def clone_or_update_public_repo(config: SyncConfig) -> Path:
    """Clone or update the public repository."""
    work_path = Path(config.work_dir)
    repo_path = work_path / config.public_repo_name

    if repo_path.exists():
        print(f"📂 Updating existing clone at {repo_path}")
        run_cmd(["git", "fetch", "origin"], cwd=repo_path)
        run_cmd(["git", "checkout", "main"], cwd=repo_path)
        run_cmd(["git", "reset", "--hard", "origin/main"], cwd=repo_path)
    else:
        print(f"📥 Cloning {config.public_repo_url}")
        work_path.mkdir(parents=True, exist_ok=True)
        run_cmd(
            ["git", "clone", config.public_repo_url, config.public_repo_name],
            cwd=work_path,
        )

    return repo_path


def clean_destination(repo_path: Path, config: SyncConfig) -> None:
    """Remove existing content from destination (except .git)."""
    print("🧹 Cleaning destination repository")
    for item in repo_path.iterdir():
        if item.name == ".git":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def should_exclude(path: Path, config: SyncConfig) -> bool:
    """Check if a path should be excluded from sync."""
    name = path.name
    for pattern in config.paths_to_exclude:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    return False


def copy_path(
    src: Path,
    dst: Path,
    config: SyncConfig,
) -> None:
    """Copy a file or directory, respecting exclusions."""
    if should_exclude(src, config):
        return

    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    elif src.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            copy_path(item, dst / item.name, config)


def sync_paths(
    source_root: Path,
    dest_root: Path,
    config: SyncConfig,
) -> list[str]:
    """Sync configured paths from source to destination."""
    synced: list[str] = []

    for src_path, dst_path in config.paths_to_sync:
        src = source_root / src_path
        dst = dest_root / (dst_path or src_path)

        if not src.exists():
            print(f"  ⚠️  Skipping {src_path} (not found)")
            continue

        print(f"  📁 {src_path} → {dst_path or src_path}")
        copy_path(src, dst, config)
        synced.append(src_path)

    return synced


def commit_and_push(
    repo_path: Path,
    version: str,
    synced_paths: list[str],
) -> bool:
    """Commit changes and push to remote."""
    # Check if there are changes
    result = run_cmd(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture=True,
    )

    if not result.stdout.strip():
        print("ℹ️  No changes to commit")
        return False

    # Stage all changes
    run_cmd(["git", "add", "-A"], cwd=repo_path)

    # Commit
    commit_msg = f"chore(release): sync {version} from sum-platform\n\nSynced paths:\n"
    for path in synced_paths:
        commit_msg += f"- {path}\n"

    run_cmd(["git", "commit", "-m", commit_msg], cwd=repo_path)

    # Push
    run_cmd(["git", "push", "origin", "main"], cwd=repo_path)

    return True


def create_tag(repo_path: Path, version: str, push: bool = True) -> None:
    """Create and optionally push an annotated tag."""
    # Check if tag exists
    result = run_cmd(
        ["git", "tag", "-l", version],
        cwd=repo_path,
        capture=True,
    )

    if result.stdout.strip():
        raise RuntimeError(
            f"Tag {version} already exists. Use a new patch version instead."
        )

    # Create annotated tag
    run_cmd(
        ["git", "tag", "-a", version, "-m", f"Release {version}"],
        cwd=repo_path,
    )

    if push:
        run_cmd(["git", "push", "origin", version], cwd=repo_path)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sync sum-platform to sum-core (public)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync without tagging (CI use)
  python scripts/sync_to_public.py

  # Sync and create tag
  python scripts/sync_to_public.py --version v0.6.0

  # Sync with custom public repo URL
  python scripts/sync_to_public.py --public-repo git@github.com:mymarkashton480/sum-core.git
        """,
    )
    parser.add_argument(
        "--version",
        "-v",
        help="Version to tag after sync (e.g., v0.6.0). If not provided, no tag is created.",
    )
    parser.add_argument(
        "--public-repo",
        help="Override public repo URL",
    )
    parser.add_argument(
        "--work-dir",
        help="Override working directory for clone",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Don't push changes (for testing)",
    )
    parser.add_argument(
        "--tag-only",
        action="store_true",
        help="Skip sync, only create tag (assumes repo is already synced)",
    )

    args = parser.parse_args()

    # Build config with overrides
    config_kwargs: dict[str, str] = {}
    if args.public_repo:
        config_kwargs["public_repo_url"] = args.public_repo
    if args.work_dir:
        config_kwargs["work_dir"] = args.work_dir

    config = SyncConfig(**config_kwargs) if config_kwargs else SyncConfig()

    # Normalize version
    version = args.version
    if version and not version.startswith("v"):
        version = f"v{version}"

    try:
        print("=" * 60)
        print("SUM Platform → sum-core Sync")
        print("=" * 60)

        # Find source repo
        source_root = find_repo_root()
        print(f"📍 Source: {source_root}")

        # Clone or update public repo
        print("\n📦 Preparing public repository...")
        repo_path = clone_or_update_public_repo(config)
        print(f"📍 Destination: {repo_path}")

        if not args.tag_only:
            # Clean and sync
            print("\n🔄 Syncing content...")
            clean_destination(repo_path, config)
            synced = sync_paths(source_root, repo_path, config)

            if not synced:
                print("❌ No paths were synced!")
                return 1

            # Commit and push
            print("\n📤 Committing changes...")
            had_changes = commit_and_push(
                repo_path,
                version or "latest",
                synced,
            )

            if not had_changes and not args.no_push:
                print("ℹ️  Repository already up to date")

        # Create tag if version specified
        if version:
            print(f"\n🏷️  Creating tag {version}...")
            create_tag(repo_path, version, push=not args.no_push)
            print(f"✅ Tag {version} created" + (" and pushed" if not args.no_push else ""))

        print("\n" + "=" * 60)
        print("✅ Sync complete!")
        print("=" * 60)

        if version:
            print(f"\n📦 Release URL: https://github.com/{config.public_repo_url.split(':')[1].replace('.git', '')}/releases/tag/{version}")

        return 0

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Command failed: {e}")
        return 1
    except RuntimeError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Aborted by user")
        return 130


if __name__ == "__main__":
    sys.exit(main())
