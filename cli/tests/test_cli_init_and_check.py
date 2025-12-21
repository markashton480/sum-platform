from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from sum_cli.commands.check import run_check
from sum_cli.commands.init import run_init
from sum_cli.util import validate_project_name


def test_validate_project_name_allows_hyphens_and_normalizes() -> None:
    naming = validate_project_name("acme-kitchens")
    assert naming.slug == "acme-kitchens"
    assert naming.python_package == "acme_kitchens"


def test_init_creates_project_and_check_passes(tmp_path, monkeypatch) -> None:
    """
    Test that sum init + sum check works from repo root context.

    The CLI's monorepo detection will find core/ by traversing upward from
    the project directory to the repo root.
    """
    repo_root = Path(__file__).resolve().parents[2]
    monkeypatch.setenv("SUM_THEME_PATH", str(repo_root / "themes"))
    monkeypatch.setenv("SUM_BOILERPLATE_PATH", str(repo_root / "boilerplate"))

    # Use unique project name to avoid conflicts with existing projects
    # Note: avoid names containing 'test' since the check scans for 'test_project'
    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"cli-check-{unique_suffix}"
    python_package = f"cli_check_{unique_suffix}"

    # Create a new project from repo root context
    monkeypatch.chdir(tmp_path)
    project_root = tmp_path / "clients" / project_name

    code = run_init(project_name)
    assert code == 0

    assert project_root.exists()
    assert (project_root / "manage.py").exists()
    assert (project_root / ".env").exists()
    assert (project_root / ".env.example").exists()

    # project package renamed
    assert not (project_root / "project_name").exists()
    assert (project_root / python_package).is_dir()

    manage_text = (project_root / "manage.py").read_text(encoding="utf-8")
    assert f"{python_package}.settings.local" in manage_text

    # check passes when run from project root - CLI detects monorepo mode
    monkeypatch.chdir(project_root)
    assert run_check() == 0


def test_check_fails_on_missing_required_env_vars(tmp_path, monkeypatch) -> None:
    """Test that check fails when required env vars from .env.example are missing."""
    monkeypatch.delenv("FOO", raising=False)

    # Create minimal fake project in tmp_path (outside monorepo context)
    project = tmp_path / "proj"
    project.mkdir()
    (project / "manage.py").write_text(
        'import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "dummy.settings")\n',
        encoding="utf-8",
    )
    (project / ".env.example").write_text("FOO=bar\n", encoding="utf-8")
    # No .env and no FOO in os.environ

    pkg = project / "dummy"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "settings.py").write_text('ROOT_URLCONF="dummy.urls"\n', encoding="utf-8")
    (pkg / "urls.py").write_text('# include("sum_core.ops.urls")\n', encoding="utf-8")

    monkeypatch.chdir(project)
    # Ensure the fake package is importable
    sys.path.insert(0, str(project))
    try:
        # This will fail due to missing env var (FOO) and possibly other issues
        # since we're outside monorepo context
        assert run_check() == 1
    finally:
        sys.path.remove(str(project))


def test_check_standalone_mode_fails_with_friendly_message(
    tmp_path, monkeypatch, capsys
) -> None:
    """
    Test that standalone mode (no monorepo detected) provides friendly error
    when sum_core is not installed.
    """
    # Create minimal project structure in tmp_path (isolated from monorepo)
    project = tmp_path / "standalone_proj"
    project.mkdir()
    (project / "manage.py").write_text(
        'import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")\n',
        encoding="utf-8",
    )
    (project / ".env.example").write_text("SECRET_KEY=changeme\n", encoding="utf-8")
    (project / ".env").write_text("SECRET_KEY=test\n", encoding="utf-8")

    pkg = project / "mysite"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "settings.py").write_text('ROOT_URLCONF="mysite.urls"\n', encoding="utf-8")
    (pkg / "urls.py").write_text(
        "# no sum_core wiring\nurlpatterns = []\n", encoding="utf-8"
    )

    # Critical: ensure sum_core is NOT importable
    # We remove any paths that might contain sum_core
    original_path = sys.path.copy()
    sys.path = [p for p in sys.path if "core" not in p and "sum_core" not in p]

    # Also add project to path so settings can be imported
    sys.path.insert(0, str(project))

    monkeypatch.chdir(project)
    try:
        exit_code = run_check()
        captured = capsys.readouterr()

        # Should fail (exit code 1)
        assert exit_code == 1

        # Should contain friendly message about installing requirements
        assert (
            "Install requirements" in captured.out or "sum_core import" in captured.out
        )
    finally:
        sys.path = original_path


def test_check_fails_when_theme_compiled_css_missing(
    tmp_path, monkeypatch, capsys
) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    monkeypatch.setenv("SUM_THEME_PATH", str(repo_root / "themes"))
    monkeypatch.setenv("SUM_BOILERPLATE_PATH", str(repo_root / "boilerplate"))

    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"cli-theme-check-{unique_suffix}"

    monkeypatch.chdir(tmp_path)
    project_root = tmp_path / "clients" / project_name

    assert run_init(project_name) == 0

    css_path = (
        project_root / "theme" / "active" / "static" / "theme_a" / "css" / "main.css"
    )
    assert css_path.exists()
    css_path.unlink()

    monkeypatch.chdir(project_root)
    exit_code = run_check()
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Theme compiled CSS" in captured.out


def test_check_fails_when_theme_slug_mismatch(tmp_path, monkeypatch, capsys) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    monkeypatch.setenv("SUM_THEME_PATH", str(repo_root / "themes"))
    monkeypatch.setenv("SUM_BOILERPLATE_PATH", str(repo_root / "boilerplate"))

    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"cli-theme-mismatch-{unique_suffix}"

    monkeypatch.chdir(tmp_path)
    project_root = tmp_path / "clients" / project_name

    assert run_init(project_name) == 0

    # Break provenance to simulate a bad/partial theme install
    theme_provenance = project_root / ".sum" / "theme.json"
    config = json.loads(theme_provenance.read_text(encoding="utf-8"))
    config["theme"] = "theme_b"
    theme_provenance.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    monkeypatch.chdir(project_root)
    exit_code = run_check()
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Theme slug match" in captured.out
