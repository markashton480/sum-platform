"""Tests for CLI v2 seed site selection."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cli.sum.config import SetupConfig
from cli.sum.exceptions import SetupError
from cli.sum.setup.orchestrator import SetupOrchestrator
from cli.sum.utils.environment import ExecutionMode


def _make_orchestrator(tmp_path: Path) -> SetupOrchestrator:
    project_path = tmp_path / "project"
    project_path.mkdir()
    return SetupOrchestrator(project_path, ExecutionMode.STANDALONE)


@patch("cli.sum.setup.orchestrator.ContentSeeder.seed_profile")
@patch("cli.sum.setup.orchestrator.ContentSeeder.seed_homepage")
@patch("cli.sum.setup.orchestrator.DjangoCommandExecutor")
def test_seed_content_routes_sage_and_stone(
    mock_executor_class: MagicMock,
    mock_seed_homepage: MagicMock,
    mock_seed_profile: MagicMock,
    tmp_path: Path,
) -> None:
    config = SetupConfig(seed_site="sage-and-stone")
    orchestrator = _make_orchestrator(tmp_path)

    orchestrator._seed_content(config)

    mock_executor_class.assert_called_once_with(
        orchestrator.project_path, ExecutionMode.STANDALONE
    )
    mock_seed_profile.assert_called_once_with("sage-stone")
    mock_seed_homepage.assert_not_called()


@patch("cli.sum.setup.orchestrator.ContentSeeder.seed_profile")
@patch("cli.sum.setup.orchestrator.ContentSeeder.seed_homepage")
@patch("cli.sum.setup.orchestrator.DjangoCommandExecutor")
def test_seed_content_defaults_to_homepage(
    mock_executor_class: MagicMock,
    mock_seed_homepage: MagicMock,
    mock_seed_profile: MagicMock,
    tmp_path: Path,
) -> None:
    config = SetupConfig(seed_preset="theme-x")
    orchestrator = _make_orchestrator(tmp_path)

    orchestrator._seed_content(config)

    mock_executor_class.assert_called_once_with(
        orchestrator.project_path, ExecutionMode.STANDALONE
    )
    mock_seed_homepage.assert_called_once_with(preset="theme-x")
    mock_seed_profile.assert_not_called()


@patch("cli.sum.setup.orchestrator.ContentSeeder.seed_homepage")
@patch("cli.sum.setup.orchestrator.DjangoCommandExecutor")
def test_seed_content_rejects_unknown_site(
    mock_executor_class: MagicMock,
    mock_seed_homepage: MagicMock,
    tmp_path: Path,
) -> None:
    config = SetupConfig(seed_site="unknown-site")
    orchestrator = _make_orchestrator(tmp_path)

    with pytest.raises(SetupError, match="Unknown seed site"):
        orchestrator._seed_content(config)

    mock_executor_class.assert_called_once_with(
        orchestrator.project_path, ExecutionMode.STANDALONE
    )
    mock_seed_homepage.assert_not_called()
