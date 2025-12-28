"""Command-line entrypoint wiring for the SUM platform CLI."""

from __future__ import annotations

from typing import cast

import click

from cli.sum.commands.check import check
from cli.sum.commands.init import init
from cli.sum.commands.run import run


@click.group()
def cli() -> None:
    """SUM Platform CLI (v2)."""


cli.add_command(check)
cli.add_command(run)
cli.add_command(cast("click.Command", init))


if __name__ == "__main__":
    cli()
