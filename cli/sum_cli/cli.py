from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from sum_cli.commands.check import run_check
from sum_cli.commands.init import run_init
from sum_cli.commands.themes import run_themes_list


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sum",
        description="SUM Platform CLI (v1): scaffolding + validation only",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init", help="Create a new client project from the boilerplate"
    )
    init_parser.add_argument("project_name", help="Client project name (slug)")
    init_parser.add_argument(
        "--theme",
        default="theme_a",
        help="Theme slug to use (default: theme_a)",
    )

    subparsers.add_parser("check", help="Validate the current client project")

    subparsers.add_parser("themes", help="List available themes")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """
    CLI entry point for both console script and tests.

    Returns a process exit code (0 success, 1 failure, 2 usage).
    """
    args = _build_parser().parse_args(list(argv) if argv is not None else None)

    if args.command == "init":
        return run_init(
            project_name=str(args.project_name),
            theme_slug=str(args.theme),
        )
    if args.command == "check":
        return run_check()
    if args.command == "themes":
        return run_themes_list()

    # Defensive: argparse required=True should prevent this.
    print("Unknown command.", file=sys.stderr)
    return 2
