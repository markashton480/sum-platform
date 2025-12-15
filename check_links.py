#!/usr/bin/env python3
"""
Check all internal markdown links in the docs directory for broken references.
"""

import re
from pathlib import Path

# Root directory of the project
ROOT_DIR = Path("/home/mark/workspaces/sum-platform")
DOCS_DIR = ROOT_DIR / "docs"

# Pattern to match markdown links: [text](path) or [text](path#anchor)
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

# Files to check
KEY_FILES = [
    ROOT_DIR / "README.md",
    DOCS_DIR / "dev/SUM-PLATFORM-SSOT.md",
    DOCS_DIR / "dev/WIRING-INVENTORY.md",
    DOCS_DIR / "dev/hygiene.md",
    DOCS_DIR / "dev/navigation-tags-reference.md",
    DOCS_DIR / "dev/NAV/navigation.md",
    DOCS_DIR / "dev/blocks-reference.md",
    DOCS_DIR / "dev/page-types-reference.md",
    DOCS_DIR / "dev/design/css-architecture-and-tokens.md",
]


def is_external_link(link: str) -> bool:
    """Check if a link is external (http://, https://, etc.)"""
    return link.startswith(("http://", "https://", "mailto:", "tel:", "ftp://"))


def is_anchor_only(link: str) -> bool:
    """Check if a link is just an anchor (starts with #)"""
    return link.startswith("#")


def is_special_link(link: str) -> bool:
    """Check if a link is special (file://, cci:, etc.)"""
    return link.startswith(("file://", "cci:"))


def resolve_link_path(source_file: Path, link: str) -> Path:
    """Resolve a relative link path from a source file."""
    # Remove anchor if present
    link_path = link.split("#")[0]

    # If it's an absolute path from repo root
    if link_path.startswith("/"):
        return ROOT_DIR / link_path.lstrip("/")

    # Otherwise it's relative to the source file's directory
    return (source_file.parent / link_path).resolve()


def check_file_links(file_path: Path) -> list[tuple[str, str, str]]:
    """
    Check all links in a markdown file.
    Returns list of (link_text, link_path, reason) for broken links.
    """
    broken_links = []

    if not file_path.exists():
        return [("N/A", str(file_path), "Source file does not exist")]

    try:
        content = file_path.read_text()
    except Exception as e:
        return [("N/A", str(file_path), f"Error reading file: {e}")]

    for match in LINK_PATTERN.finditer(content):
        link_text = match.group(1)
        link_path = match.group(2)

        # Skip external links
        if is_external_link(link_path):
            continue

        # Skip anchor-only links (they reference sections in the same document)
        if is_anchor_only(link_path):
            continue

        # Skip special links (file://, cci: protocol links from chat transcripts)
        if is_special_link(link_path):
            continue

        # Resolve the link path
        resolved_path = resolve_link_path(file_path, link_path)

        # Check if the target exists
        if not resolved_path.exists():
            broken_links.append((link_text, link_path, "Target file does not exist"))

    return broken_links


def main():
    """Main function to check all markdown links."""
    print("=" * 80)
    print("MARKDOWN LINK CHECKER")
    print("=" * 80)
    print()

    all_broken_links = []

    # Also check all markdown files in docs/dev
    all_files_to_check = list(KEY_FILES)

    # Add all markdown files from docs/dev recursively
    docs_dev = DOCS_DIR / "dev"
    if docs_dev.exists():
        for md_file in docs_dev.rglob("*.md"):
            if md_file not in all_files_to_check:
                all_files_to_check.append(md_file)

    for file_path in sorted(all_files_to_check):
        relative_path = (
            file_path.relative_to(ROOT_DIR)
            if file_path.is_relative_to(ROOT_DIR)
            else file_path
        )

        broken = check_file_links(file_path)

        if broken:
            all_broken_links.extend([(relative_path, *b) for b in broken])

    # Print results
    if all_broken_links:
        print(f"Found {len(all_broken_links)} broken link(s):\n")

        for source_file, link_text, link_path, reason in all_broken_links:
            print(f"File: {source_file}")
            print(f"  Link Text: {link_text}")
            print(f"  Link Path: {link_path}")
            print(f"  Reason: {reason}")
            print()
    else:
        print("✓ No broken internal links found!")

    print("=" * 80)
    return 0 if not all_broken_links else 1


if __name__ == "__main__":
    exit(main())
