"""Command-line entrypoint wiring for the SUM platform CLI."""

from __future__ import annotations

import click

from cli.sum.commands.check import check
from cli.sum.commands.run import run


@click.group()
def cli() -> None:
    """SUM Platform CLI (v2)."""


cli.add_command(check)
cli.add_command(run)

try:
    from cli.sum.commands.init import init
except ModuleNotFoundError:
    init = None
else:
    cli.add_command(init)


if __name__ == "__main__":
    cli()
