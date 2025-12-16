from __future__ import annotations

import sys
from pathlib import Path

from sum_cli.commands.check import run_check
from sum_cli.commands.init import run_init
from sum_cli.util import validate_project_name


def _add_repo_core_to_syspath() -> None:
    """
    Ensure sum_core is importable during CLI tests without installing dependencies.
    """
    repo_root = Path(__file__).resolve().parents[2]
    core_dir = repo_root / "core"
    if str(core_dir) not in sys.path:
        sys.path.insert(0, str(core_dir))


def test_validate_project_name_allows_hyphens_and_normalizes() -> None:
    naming = validate_project_name("acme-kitchens")
    assert naming.slug == "acme-kitchens"
    assert naming.python_package == "acme_kitchens"


def test_init_creates_project_and_check_passes(tmp_path, monkeypatch) -> None:
    _add_repo_core_to_syspath()

    monkeypatch.chdir(tmp_path)
    code = run_init("acme-kitchens")
    assert code == 0

    project_root = tmp_path / "clients" / "acme-kitchens"
    assert project_root.exists()
    assert (project_root / "manage.py").exists()
    assert (project_root / ".env").exists()
    assert (project_root / ".env.example").exists()

    # project package renamed
    assert not (project_root / "project_name").exists()
    assert (project_root / "acme_kitchens").is_dir()

    manage_text = (project_root / "manage.py").read_text(encoding="utf-8")
    assert "acme_kitchens.settings.local" in manage_text

    # check passes when run from project root
    monkeypatch.chdir(project_root)
    assert run_check() == 0


def test_check_fails_on_missing_required_env_vars(tmp_path, monkeypatch) -> None:
    _add_repo_core_to_syspath()
    monkeypatch.delenv("FOO", raising=False)

    # Minimal fake project (no Django needed); we only exercise env var check + imports.
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
        assert run_check() == 1
    finally:
        sys.path.remove(str(project))
