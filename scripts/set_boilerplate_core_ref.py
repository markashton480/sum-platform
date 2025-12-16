#!/usr/bin/env python3
"""
Set the SUM_CORE_GIT_REF in boilerplate requirements.txt.

Updates the canonical boilerplate to pin to a specific git tag,
then syncs the CLI boilerplate copy.

Usage:
    python scripts/set_boilerplate_core_ref.py --ref v0.1.2

Requirements:
    - Must be run from the repository root
    - The ref should be a valid git tag (e.g., v0.1.0)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def get_repo_root() -> Path:
    """Get the repository root directory."""
    script_dir = Path(__file__).resolve().parent
    # scripts -> repo_root
    return script_dir.parent


def validate_ref(ref: str) -> bool:
    """
    Validate the ref format.

    Accepts semantic version tags: v0.x.y or vX.Y.Z
    """
    pattern = r"^v\d+\.\d+\.\d+$"
    return bool(re.match(pattern, ref))


def update_requirements(requirements_path: Path, ref: str) -> bool:
    """
    Update the SUM_CORE_GIT_REF placeholder in requirements.txt.

    Returns True if changes were made, False otherwise.
    """
    if not requirements_path.exists():
        print(
            f"ERROR: Requirements file not found: {requirements_path}", file=sys.stderr
        )
        return False

    content = requirements_path.read_text()
    original_content = content

    # Pattern to match the sum-core line with any ref (placeholder or existing tag)
    # Matches: sum-core @ git+https://github.com/ORG/REPO.git@<ref>#subdirectory=core
    pattern = r"(sum-core @ git\+https://github\.com/[^@]+@)([^#]+)(#subdirectory=core)"
    replacement = rf"\g<1>{ref}\g<3>"

    new_content, count = re.subn(pattern, replacement, content)

    if count == 0:
        print(
            "ERROR: Could not find sum-core git reference line in requirements.txt",
            file=sys.stderr,
        )
        print(
            "Expected format: sum-core @ git+https://github.com/ORG/REPO.git@<ref>#subdirectory=core",
            file=sys.stderr,
        )
        return False

    if new_content == original_content:
        print(f"INFO: Requirements already pins to {ref}")
        return True

    requirements_path.write_text(new_content)
    print(f"Updated {requirements_path.name}: pinned to {ref}")
    return True


def run_sync_boilerplate(repo_root: Path) -> bool:
    """Run the boilerplate sync script."""
    sync_script = repo_root / "cli" / "scripts" / "sync_boilerplate.py"

    if not sync_script.exists():
        print(f"ERROR: Sync script not found: {sync_script}", file=sys.stderr)
        return False

    print("Syncing CLI boilerplate...")
    result = subprocess.run(
        [sys.executable, str(sync_script)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("ERROR: Boilerplate sync failed:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return False

    print(result.stdout.strip())
    return True


def run_check_boilerplate(repo_root: Path) -> bool:
    """Run the boilerplate drift check."""
    sync_script = repo_root / "cli" / "scripts" / "sync_boilerplate.py"

    if not sync_script.exists():
        print(f"ERROR: Sync script not found: {sync_script}", file=sys.stderr)
        return False

    print("Verifying boilerplate sync...")
    result = subprocess.run(
        [sys.executable, str(sync_script), "--check"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("ERROR: Boilerplate drift check failed:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return False

    print(result.stdout.strip())
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Set SUM_CORE_GIT_REF in boilerplate requirements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/set_boilerplate_core_ref.py --ref v0.1.0
    make release-set-core-ref REF=v0.1.2
        """,
    )
    parser.add_argument(
        "--ref",
        required=True,
        help="Git ref to pin to (e.g., v0.1.0)",
    )
    parser.add_argument(
        "--skip-sync",
        action="store_true",
        help="Skip CLI boilerplate sync after updating",
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip drift check after syncing",
    )

    args = parser.parse_args()

    # Validate ref format
    if not validate_ref(args.ref):
        print(f"ERROR: Invalid ref format: {args.ref}", file=sys.stderr)
        print("Expected format: vX.Y.Z (e.g., v0.1.0)", file=sys.stderr)
        return 1

    repo_root = get_repo_root()
    requirements_path = repo_root / "boilerplate" / "requirements.txt"

    # Step 1: Update requirements.txt
    if not update_requirements(requirements_path, args.ref):
        return 1

    # Step 2: Sync CLI boilerplate
    if not args.skip_sync:
        if not run_sync_boilerplate(repo_root):
            return 1

    # Step 3: Verify no drift
    if not args.skip_sync and not args.skip_check:
        if not run_check_boilerplate(repo_root):
            return 1

    print(f"\n[OK] Boilerplate now pins to {args.ref}")
    print("Next steps:")
    print("  1. Run 'make release-check' to verify all checks pass")
    print("  2. Commit the changes")
    print(
        f"  3. Create and push the tag: git tag -a {args.ref} -m 'Release {args.ref}'"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
