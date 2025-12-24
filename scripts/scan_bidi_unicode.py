from __future__ import annotations

import argparse
import unicodedata
from collections.abc import Iterable
from pathlib import Path

BANNED_CODEPOINTS = {
    0x202A,  # LEFT-TO-RIGHT EMBEDDING
    0x202B,  # RIGHT-TO-LEFT EMBEDDING
    0x202C,  # POP DIRECTIONAL FORMATTING
    0x202D,  # LEFT-TO-RIGHT OVERRIDE
    0x202E,  # RIGHT-TO-LEFT OVERRIDE
    0x2066,  # LEFT-TO-RIGHT ISOLATE
    0x2067,  # RIGHT-TO-LEFT ISOLATE
    0x2068,  # FIRST STRONG ISOLATE
    0x2069,  # POP DIRECTIONAL ISOLATE
    0x200E,  # LEFT-TO-RIGHT MARK
    0x200F,  # RIGHT-TO-LEFT MARK
    0x061C,  # ARABIC LETTER MARK
    0xFEFF,  # ZERO WIDTH NO-BREAK SPACE (BOM)
}


def scan_text(path: Path, text: str) -> list[tuple[int, int, str, int]]:
    issues: list[tuple[int, int, str, int]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for column_number, character in enumerate(line, start=1):
            code_point = ord(character)
            if code_point in BANNED_CODEPOINTS:
                name = unicodedata.name(character, "UNKNOWN")
                issues.append((line_number, column_number, name, code_point))
    return issues


def scan_file(path: Path) -> list[tuple[int, int, str, int]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    return scan_text(path, text)


def resolve_paths(inputs: Iterable[Path]) -> list[Path]:
    resolved: list[Path] = []
    for value in inputs:
        if value.is_dir():
            for child in sorted(value.rglob("*")):
                if child.is_file():
                    resolved.append(child)
        else:
            resolved.append(value)
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan files for hidden bidi/control Unicode characters."
    )
    parser.add_argument(
        "paths",
        metavar="PATH",
        type=Path,
        nargs="+",
        help="File or directory paths to scan",
    )
    args = parser.parse_args()

    target_files = resolve_paths(args.paths)
    total_issues = 0

    for path in target_files:
        issues = scan_file(path)
        if not issues:
            continue
        total_issues += len(issues)
        for line, column, name, code_point in issues:
            print(
                f"{path}: line {line} column {column} contains {name} (U+{code_point:04X})"
            )

    if total_issues:
        print(f"Detected {total_issues} hidden directional/control characters.")
        return 1

    print("No banned bidi/control characters found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
