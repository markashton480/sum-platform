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
import fnmatch
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SyncConfig:
    """Configuration for repository sync."""

    private_repo_path: Path
    public_repo_url: str
    public_repo_branch: str = "main"
    public_repo_path: Path | None = None

    # Define what gets synced: source -> dest (None means same path)
    sync_map: dict[str, str | None] = field(default_factory=dict)

    # Exclusion patterns (fnmatch-style)
    exclude_patterns: list[str] = field(default_factory=list)


DEFAULT_SYNC_MAP: dict[str, str | None] = {
    "core": "core",
    "boilerplate": "boilerplate",
    "docs/public": "docs",
    "pyproject.toml": "pyproject.toml",
    "README.md": "README.md",
    "LICENSE": "LICENSE",
}

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

DEFAULT_PUBLIC_REPO_PATH = Path("/tmp/sum-core-sync")


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


def should_exclude(path: Path, config: SyncConfig) -> bool:
    """Check if path should be excluded based on patterns."""
    name = path.name
    for pattern in config.exclude_patterns:
        # Match against filename (for patterns like "*.pyc", "__pycache__")
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def ensure_clean_repo(repo_path: Path) -> None:
    """Ensure repo has no uncommitted changes."""
    status = run_cmd(["git", "status", "--porcelain"], cwd=repo_path, capture=True)
    if status:
        raise RuntimeError(
            f"Repository at {repo_path} has uncommitted changes:\n{status}"
        )


def clone_or_update_public_repo(config: SyncConfig) -> Path:
    """Clone public repo if needed, otherwise fetch and reset to origin/main."""
    public_path = config.public_repo_path or DEFAULT_PUBLIC_REPO_PATH

    if not public_path.exists():
        print(f"📦 Cloning public repo into {public_path}...")
        run_cmd(["git", "clone", config.public_repo_url, str(public_path)])
    else:
        print(f"🔄 Updating public repo at {public_path}...")
        run_cmd(["git", "fetch", "origin"], cwd=public_path)

    # Checkout branch and hard reset to origin/branch for clean slate
    run_cmd(["git", "checkout", config.public_repo_branch], cwd=public_path)
    run_cmd(
        ["git", "reset", "--hard", f"origin/{config.public_repo_branch}"],
        cwd=public_path,
    )
    run_cmd(["git", "clean", "-fd"], cwd=public_path)

    return public_path


def copy_path(src: Path, dst: Path, config: SyncConfig) -> None:
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


def sync_paths(config: SyncConfig, public_repo_path: Path) -> list[str]:
    """Sync allowed paths from private repo to public repo."""
    sync_map = config.sync_map or DEFAULT_SYNC_MAP
    synced: list[str] = []

    for src_path, dst_path in sync_map.items():
        src = config.private_repo_path / src_path
        if not src.exists():
            print(f"⚠️  Skipping missing path: {src_path}")
            continue

        dst = public_repo_path / (dst_path or src_path)

        print(f"  📁 {src_path} → {dst_path or src_path}")
        copy_path(src, dst, config)
        synced.append(src_path)

    return synced


def commit_and_push(
    repo_path: Path,
    version: str,
    synced_paths: list[str],
    push: bool = True,
) -> bool:
    """Commit changes and optionally push to remote."""
    # Check if there are changes
    status = run_cmd(["git", "status", "--porcelain"], cwd=repo_path, capture=True)
    if not status:
        return False

    # Stage all changes
    run_cmd(["git", "add", "-A"], cwd=repo_path)

    # Commit
    summary = ", ".join(synced_paths)
    commit_msg = f"chore(sync): {version}\n\nSynced: {summary}"
    run_cmd(["git", "commit", "-m", commit_msg], cwd=repo_path)

    if push:
        run_cmd(["git", "push", "origin", "main"], cwd=repo_path)
    else:
        print("ℹ️  --no-push: skipping push to origin/main")

    return True


def create_tag(repo_path: Path, version: str, push: bool = True) -> None:
    """Create and optionally push an annotated tag."""
    # Check if tag already exists locally
    existing = run_cmd(["git", "tag", "-l", version], cwd=repo_path, capture=True)
    if existing:
        print(f"⚠️  Tag {version} already exists locally")
    else:
        run_cmd(
            ["git", "tag", "-a", version, "-m", f"Release {version}"],
            cwd=repo_path,
        )
        print(f"✅ Created tag {version}")

    if push:
        run_cmd(["git", "push", "origin", version], cwd=repo_path)
        print(f"✅ Pushed tag {version}")
    else:
        print("ℹ️  --no-push: skipping tag push")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Sync public-facing code from sum-platform (private) to sum-core (public).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync without tagging
  python scripts/sync_to_public.py --public-repo-url git@github.com:ORG/sum-core.git

  # Sync and create tag
  python scripts/sync_to_public.py --public-repo-url git@github.com:ORG/sum-core.git --version v0.6.0

  # Dry run (no push)
  python scripts/sync_to_public.py --public-repo-url git@github.com:ORG/sum-core.git --version v0.6.0 --no-push
        """,
    )
    parser.add_argument(
        "--private-repo",
        type=Path,
        default=Path.cwd(),
        help="Path to private repo (default: current directory)",
    )
    parser.add_argument(
        "--public-repo-url",
        required=True,
        help="Git URL for public repo (e.g., git@github.com:ORG/sum-core.git)",
    )
    parser.add_argument(
        "--public-repo-path",
        type=Path,
        default=None,
        help="Path to local public repo clone (default: /tmp/sum-core-sync)",
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Version tag to create (e.g., v0.1.0). If omitted, no tag is created.",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Do not push commits or tags (dry run mode)",
    )
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    config = SyncConfig(
        private_repo_path=args.private_repo.resolve(),
        public_repo_url=args.public_repo_url,
        public_repo_path=(
            args.public_repo_path.resolve() if args.public_repo_path else None
        ),
        sync_map=DEFAULT_SYNC_MAP,
        exclude_patterns=DEFAULT_EXCLUDE_PATTERNS,
    )

    version = args.version
    push = not args.no_push

    try:
        print("=" * 60)
        print("🔧 SUM Platform → Public Repo Sync")
        print("=" * 60)

        if args.no_push:
            print("⚠️  DRY RUN MODE: No changes will be pushed\n")

        # Ensure private repo is clean
        print("✅ Checking private repo status...")
        ensure_clean_repo(config.private_repo_path)

        # Clone or update public repo
        print()
        public_path = clone_or_update_public_repo(config)

        # Ensure public repo is clean (after reset)
        print("\n✅ Checking public repo status...")
        ensure_clean_repo(public_path)

        # Sync files
        print("\n📁 Syncing paths...")
        synced = sync_paths(config, public_path)

        if not synced:
            print("❌ No paths were synced!")
            return 1

        # Commit and push
        print("\n📤 Committing changes...")
        had_changes = commit_and_push(
            public_path,
            version or "latest",
            synced,
            push=push,
        )

        if not had_changes:
            print("ℹ️  No changes to commit (already up to date)")

        # Create tag if version specified
        if version:
            print(f"\n🏷️  Tagging {version}...")
            create_tag(public_path, version, push=push)

        print("\n" + "=" * 60)
        print("✅ Sync complete!")
        print("=" * 60)

        if version and push:
            # Extract org/repo from git URL
            repo_path_str = config.public_repo_url.split(":")[-1].replace(".git", "")
            print(
                f"\n📦 Release: https://github.com/{repo_path_str}/releases/tag/{version}"
            )

        return 0

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Command failed: {e}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return 1
    except RuntimeError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Aborted by user")
        return 130


if __name__ == "__main__":
    sys.exit(main())
