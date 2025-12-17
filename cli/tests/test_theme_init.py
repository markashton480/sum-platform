"""
Name: CLI Theme Init Tests
Path: cli/tests/test_theme_init.py
Purpose: Integration tests for sum init --theme functionality
Family: sum_cli tests
Dependencies: sum_cli, sum_core.themes
"""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from sum_cli.commands.init import run_init


def test_init_with_theme_creates_theme_config(monkeypatch) -> None:
    """Test that sum init --theme creates .sum/theme.json provenance file."""
    repo_root = Path(__file__).resolve().parents[2]

    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"theme-test-{unique_suffix}"

    monkeypatch.chdir(repo_root)
    project_root = repo_root / "clients" / project_name

    try:
        code = run_init(project_name, theme_slug="theme_a")
        assert code == 0

        # Check .sum/theme.json was created
        theme_file = project_root / ".sum" / "theme.json"
        assert theme_file.exists()

        # Validate provenance content
        with theme_file.open("r") as f:
            config = json.load(f)

        assert config["theme"] == "theme_a"
        assert "original_version" in config, "Provenance must include original_version"
        assert config["original_version"] == "1.0.0"
        assert "locked_at" in config
    finally:
        if project_root.exists():
            shutil.rmtree(project_root)


def test_init_copies_theme_to_active_directory(monkeypatch) -> None:
    """Test that sum init --theme copies theme to theme/active/ directory."""
    repo_root = Path(__file__).resolve().parents[2]

    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"theme-copy-{unique_suffix}"

    monkeypatch.chdir(repo_root)
    project_root = repo_root / "clients" / project_name

    try:
        code = run_init(project_name, theme_slug="theme_a")
        assert code == 0

        # Check theme/active/ directory exists
        theme_active_dir = project_root / "theme" / "active"
        assert theme_active_dir.exists(), "theme/active/ should exist"
        assert theme_active_dir.is_dir(), "theme/active/ should be a directory"

        # Check theme.json was copied
        theme_manifest = theme_active_dir / "theme.json"
        assert theme_manifest.exists(), "theme.json should be copied"

        # Check templates were copied
        templates_dir = theme_active_dir / "templates"
        assert templates_dir.exists(), "templates/ should be copied"
        assert (templates_dir / "theme_a" / "base.html").exists()

        # Check static files were copied
        static_dir = theme_active_dir / "static"
        assert static_dir.exists(), "static/ should be copied"
        assert (static_dir / "theme_a" / "css" / "main.css").exists()
    finally:
        if project_root.exists():
            shutil.rmtree(project_root)


def test_init_with_invalid_theme_fails(monkeypatch, capsys) -> None:
    """Test that sum init --theme fails gracefully with invalid theme."""
    repo_root = Path(__file__).resolve().parents[2]

    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"invalid-theme-{unique_suffix}"

    monkeypatch.chdir(repo_root)
    project_root = repo_root / "clients" / project_name

    try:
        code = run_init(project_name, theme_slug="nonexistent_theme")
        captured = capsys.readouterr()

        # Should fail
        assert code == 1

        # Should mention the invalid theme
        assert "nonexistent_theme" in captured.out or "does not exist" in captured.out

        # Project should not have been created or should be incomplete
        # (depending on when validation happens)
    finally:
        if project_root.exists():
            shutil.rmtree(project_root)


def test_init_default_theme_is_theme_a(monkeypatch) -> None:
    """Test that sum init without --theme uses theme_a by default."""
    repo_root = Path(__file__).resolve().parents[2]

    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"default-theme-{unique_suffix}"

    monkeypatch.chdir(repo_root)
    project_root = repo_root / "clients" / project_name

    try:
        # Call without theme_slug - should use default
        code = run_init(project_name)
        assert code == 0

        # Check theme file has theme_a
        theme_file = project_root / ".sum" / "theme.json"
        assert theme_file.exists()

        with theme_file.open("r") as f:
            config = json.load(f)

        assert config["theme"] == "theme_a"

        # Also verify theme was actually copied
        assert (project_root / "theme" / "active" / "theme.json").exists()
    finally:
        if project_root.exists():
            shutil.rmtree(project_root)
