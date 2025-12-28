from __future__ import annotations

import pytest

from cli.sum import exceptions


@pytest.mark.parametrize(
    "exc_type",
    [
        exceptions.SetupError,
        exceptions.VenvError,
        exceptions.DependencyError,
        exceptions.MigrationError,
        exceptions.SeedError,
        exceptions.SuperuserError,
    ],
)
def test_exceptions_inherit_sum_cli_error(exc_type) -> None:
    assert issubclass(exc_type, exceptions.SumCliError)
    instance = exc_type("Do the thing")
    assert str(instance) == "Do the thing"
