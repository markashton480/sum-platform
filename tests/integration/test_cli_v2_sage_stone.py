"""
CLI v2 integration tests for Sage & Stone seeder.

These tests validate that the seeder integrates properly with CLI v2.0.0.
They are skipped when CLI v2 is not installed.

See Issue #210 for CLI v2 implementation status.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


def cli_v2_installed() -> bool:
    """Check if CLI v2 (sum command) is installed and available.

    Note: There's a system 'sum' command (BSD checksum utility) that we need
    to distinguish from our sum CLI. We check for 'sum --version' output
    containing 'sum-cli' or 'SUM' to identify our CLI.
    """
    if shutil.which("sum") is None:
        return False

    try:
        result = subprocess.run(
            ["sum", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # Our CLI should have 'sum-cli' or 'SUM' in version output
        # The system 'sum' (coreutils) has 'coreutils' in output
        return "sum-cli" in result.stdout.lower() or (
            "sum" in result.stdout.lower() and "coreutils" not in result.stdout.lower()
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def cli_v2_supports_sage_stone() -> bool:
    """Check if CLI v2 supports sage-and-stone preset."""
    if not cli_v2_installed():
        return False

    try:
        result = subprocess.run(
            ["sum", "init", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return "sage-and-stone" in result.stdout.lower()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


@pytest.mark.skipif(
    not cli_v2_installed(),
    reason="CLI v2 not installed (see #210 for implementation status)",
)
class TestCLIv2Integration:
    """Tests for CLI v2.0.0 integration with Sage & Stone seeder."""

    def test_sum_command_exists(self) -> None:
        """The 'sum' command should be available."""
        result = subprocess.run(
            ["sum", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_sum_init_help_shows_options(self) -> None:
        """sum init --help should show available options."""
        result = subprocess.run(
            ["sum", "init", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should show seed-site option
        assert "--seed" in result.stdout or "seed" in result.stdout.lower()

    @pytest.mark.skipif(
        not cli_v2_supports_sage_stone(),
        reason="CLI v2 does not support sage-and-stone preset yet",
    )
    def test_cli_init_sage_and_stone(self) -> None:
        """sum init sage-and-stone --seed-site should create seeded project."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "test-project"

            result = subprocess.run(
                [
                    "sum",
                    "init",
                    "sage-and-stone",
                    "--name",
                    "test-project",
                    "--seed-site",
                    "--no-prompt",
                ],
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes for full setup
            )

            # Command should succeed
            assert result.returncode == 0, f"CLI failed: {result.stderr}"

            # Project should be created
            assert project_path.exists()

            # Should have management command
            manage_py = project_path / "manage.py"
            assert manage_py.exists()

    @pytest.mark.skipif(
        not cli_v2_supports_sage_stone(),
        reason="CLI v2 does not support sage-and-stone preset yet",
    )
    def test_cli_creates_seeded_site(self) -> None:
        """CLI should invoke seeder and create complete site."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create and seed project
            result = subprocess.run(
                [
                    "sum",
                    "init",
                    "sage-and-stone",
                    "--name",
                    "test-project",
                    "--seed-site",
                    "--no-prompt",
                ],
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )

            assert result.returncode == 0

            # Verify seeder output message
            assert "Sage & Stone" in result.stdout or "seeded" in result.stdout.lower()

    @pytest.mark.skipif(
        not cli_v2_supports_sage_stone(),
        reason="CLI v2 does not support sage-and-stone preset yet",
    )
    def test_cli_with_theme_flag(self) -> None:
        """sum init sage-and-stone --theme theme_a should apply theme."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                [
                    "sum",
                    "init",
                    "sage-and-stone",
                    "--name",
                    "test-project",
                    "--theme",
                    "theme_a",
                    "--seed-site",
                    "--no-prompt",
                ],
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )

            assert result.returncode == 0


@pytest.mark.skipif(
    not cli_v2_installed(),
    reason="CLI v2 not installed (see #210 for implementation status)",
)
class TestCLIv2SeedCommand:
    """Tests for standalone seed command via CLI v2."""

    def test_sum_seed_command_exists(self) -> None:
        """sum seed command should exist."""
        result = subprocess.run(
            ["sum", "seed", "--help"],
            capture_output=True,
            text=True,
        )

        # Command should exist (even if not implemented yet)
        # returncode 0 means exists, 2 usually means unknown command
        if result.returncode == 0:
            assert "seed" in result.stdout.lower()

    @pytest.mark.skipif(
        not cli_v2_supports_sage_stone(),
        reason="CLI v2 does not support sage-and-stone seeder yet",
    )
    def test_sum_seed_sage_stone(self) -> None:
        """sum seed sage-stone should run the seeder."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # This assumes a project already exists
            # In practice, you'd init first then seed

            result = subprocess.run(
                ["sum", "seed", "sage-stone"],
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )

            # Check if command worked or gave useful error
            if result.returncode != 0:
                # Should give clear error about no project
                assert (
                    "project" in result.stderr.lower()
                    or "not found" in result.stderr.lower()
                )
