from __future__ import annotations

import pytest

from cli.sum.config import SetupConfig


def test_setup_config_mutually_exclusive_flags() -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        SetupConfig(full=True, quick=True)


def test_setup_config_ci_enables_no_prompt() -> None:
    config = SetupConfig(ci=True)
    assert config.no_prompt is True


def test_setup_config_from_cli_args() -> None:
    config = SetupConfig.from_cli_args(
        full=True,
        skip_venv=True,
        run_server=True,
        port=9001,
        superuser_username="root",
        superuser_email="root@example.com",
        superuser_password="secret",
        seed_preset="demo",
    )

    assert config.full is True
    assert config.skip_venv is True
    assert config.run_server is True
    assert config.port == 9001
    assert config.superuser_username == "root"
    assert config.superuser_email == "root@example.com"
    assert config.superuser_password == "secret"
    assert config.seed_preset == "demo"
