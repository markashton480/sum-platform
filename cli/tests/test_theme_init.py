"""
Name: CLI Theme Init Tests
Path: cli/tests/test_theme_init.py
Purpose: Integration tests for sum init --theme functionality
Family: sum_cli tests
Dependencies: sum_cli
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from sum_cli.commands.init import run_init


def _assert_output_boundary(project_root: Path, output_root: Path) -> None:
    assert project_root.is_relative_to(
        output_root
    ), "Project must be created under SUM_CLIENT_OUTPUT_PATH"


def _assert_source_theme_present(theme_root: Path) -> None:
    assert theme_root.exists(), "Source theme directory must exist"
    assert (theme_root / "theme.json").exists(), "Source theme.json must exist"


def test_init_with_theme_creates_theme_config(
    monkeypatch, isolated_theme_env, apply_isolated_theme_env, theme_snapshot
) -> None:
    """Test that sum init --theme creates .sum/theme.json provenance file."""
    output_root = Path(isolated_theme_env["SUM_CLIENT_OUTPUT_PATH"])
    theme_root = Path(isolated_theme_env["SUM_THEME_PATH"]) / "theme_a"
    before_snapshot = theme_snapshot(theme_root)
    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"theme-test-{unique_suffix}"

    monkeypatch.chdir(output_root)
    # init creates "clients" subdir in CWD
    project_root = output_root / "clients" / project_name

    code = run_init(project_name, theme_slug="theme_a")
    assert code == 0
    _assert_output_boundary(project_root, output_root)
    _assert_source_theme_present(theme_root)
    assert theme_snapshot(theme_root) == before_snapshot

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


def test_init_copies_theme_to_active_directory(
    monkeypatch, isolated_theme_env, apply_isolated_theme_env, theme_snapshot
) -> None:
    """Test that sum init --theme copies theme to theme/active/ directory."""
    output_root = Path(isolated_theme_env["SUM_CLIENT_OUTPUT_PATH"])
    theme_root = Path(isolated_theme_env["SUM_THEME_PATH"]) / "theme_a"
    before_snapshot = theme_snapshot(theme_root)
    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"theme-copy-{unique_suffix}"

    monkeypatch.chdir(output_root)
    project_root = output_root / "clients" / project_name

    code = run_init(project_name, theme_slug="theme_a")
    assert code == 0
    _assert_output_boundary(project_root, output_root)
    _assert_source_theme_present(theme_root)
    assert theme_snapshot(theme_root) == before_snapshot

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
    assert (templates_dir / "theme" / "base.html").exists()

    # Check static files were copied
    static_dir = theme_active_dir / "static"
    assert static_dir.exists(), "static/ should be copied"
    compiled_css = static_dir / "theme_a" / "css" / "main.css"
    assert compiled_css.exists(), "compiled theme CSS must be present"

    # Compiled output should be non-trivial and not reference legacy core CSS
    assert compiled_css.stat().st_size > 5 * 1024
    css_text = compiled_css.read_text(encoding="utf-8", errors="ignore")
    assert "/static/sum_core/css/main.css" not in css_text

    # Toolchain files should be shipped for maintainers (no runtime Node required)
    assert (theme_active_dir / "tailwind" / "tailwind.config.js").exists()
    assert (theme_active_dir / "tailwind" / "postcss.config.js").exists()
    assert (theme_active_dir / "tailwind" / "package.json").exists()
    assert (theme_active_dir / "tailwind" / "npm-shrinkwrap.json").exists()
    assert (static_dir / "theme_a" / "css" / "input.css").exists()

    # init must not copy node_modules into the client project
    assert not (theme_active_dir / "node_modules").exists()


def test_init_with_invalid_theme_fails(
    monkeypatch,
    capsys,
    isolated_theme_env,
    apply_isolated_theme_env,
    theme_snapshot,
) -> None:
    """Test that sum init --theme fails gracefully with invalid theme."""
    output_root = Path(isolated_theme_env["SUM_CLIENT_OUTPUT_PATH"])
    theme_root = Path(isolated_theme_env["SUM_THEME_PATH"]) / "theme_a"
    before_snapshot = theme_snapshot(theme_root)
    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"invalid-theme-{unique_suffix}"

    monkeypatch.chdir(output_root)
    project_root = output_root / "clients" / project_name

    code = run_init(project_name, theme_slug="nonexistent_theme")
    captured = capsys.readouterr()

    # Should fail
    assert code == 1
    _assert_output_boundary(project_root, output_root)
    _assert_source_theme_present(theme_root)
    assert theme_snapshot(theme_root) == before_snapshot
    assert not project_root.exists()

    # Should mention the invalid theme
    assert "nonexistent_theme" in captured.out or "does not exist" in captured.out

    # Project should not have been created or should be incomplete
    # (depending on when validation happens)


def test_init_default_theme_is_theme_a(
    monkeypatch, isolated_theme_env, apply_isolated_theme_env, theme_snapshot
) -> None:
    """Test that sum init without --theme uses theme_a by default."""
    output_root = Path(isolated_theme_env["SUM_CLIENT_OUTPUT_PATH"])
    theme_root = Path(isolated_theme_env["SUM_THEME_PATH"]) / "theme_a"
    before_snapshot = theme_snapshot(theme_root)
    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"default-theme-{unique_suffix}"

    monkeypatch.chdir(output_root)
    project_root = output_root / "clients" / project_name

    # Call without theme_slug - should use default
    code = run_init(project_name)
    assert code == 0
    _assert_output_boundary(project_root, output_root)
    _assert_source_theme_present(theme_root)
    assert theme_snapshot(theme_root) == before_snapshot

    # Check theme file has theme_a
    theme_file = project_root / ".sum" / "theme.json"
    assert theme_file.exists()

    with theme_file.open("r") as f:
        config = json.load(f)

    assert config["theme"] == "theme_a"

    # Also verify theme was actually copied
    assert (project_root / "theme" / "active" / "theme.json").exists()


def test_init_includes_seed_showroom_command(
    monkeypatch, isolated_theme_env, apply_isolated_theme_env, theme_snapshot
) -> None:
    """Generated client projects should include the seed_showroom management command."""
    output_root = Path(isolated_theme_env["SUM_CLIENT_OUTPUT_PATH"])
    theme_root = Path(isolated_theme_env["SUM_THEME_PATH"]) / "theme_a"
    before_snapshot = theme_snapshot(theme_root)
    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"seed-showroom-{unique_suffix}"
    python_pkg = project_name.replace("-", "_")

    monkeypatch.chdir(output_root)
    project_root = output_root / "clients" / project_name

    code = run_init(project_name, theme_slug="theme_a")
    assert code == 0
    _assert_output_boundary(project_root, output_root)
    _assert_source_theme_present(theme_root)
    assert theme_snapshot(theme_root) == before_snapshot

    cmd = (
        project_root
        / python_pkg
        / "home"
        / "management"
        / "commands"
        / "seed_showroom.py"
    )
    assert (
        cmd.exists()
    ), "seed_showroom command should be present in the generated project"

    # SQ-002 regression check: Kitchen Sink stream should not double-to_python()
    # StreamChild items. We look for the safe raw-data merge via get_prep_value().
    text = cmd.read_text(encoding="utf-8")
    assert "get_prep_value" in text
    assert "combined_data = list(home_data) + list(showroom_data)" not in text
    assert "return stream_block.to_python(combined_data)" not in text

    # Navigation seeding should match StreamField-based settings models.
    assert "header.menu_items" in text
    assert "footer.link_sections" in text
    assert "header.items" not in text
    assert "sub_items" not in text

    # Branding seeding should use sum_core SiteSettings fields.
    assert "settings.company_name" in text
    assert "settings.header_logo_id" in text
    assert "settings.footer_logo_id" in text
    assert "settings.favicon_id" in text


def test_init_settings_include_canonical_theme_override(
    monkeypatch, isolated_theme_env, apply_isolated_theme_env, theme_snapshot
) -> None:
    """Generated settings should include the canonical theme dev override."""
    output_root = Path(isolated_theme_env["SUM_CLIENT_OUTPUT_PATH"])
    theme_root = Path(isolated_theme_env["SUM_THEME_PATH"]) / "theme_a"
    before_snapshot = theme_snapshot(theme_root)
    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"canonical-theme-{unique_suffix}"
    python_pkg = project_name.replace("-", "_")

    monkeypatch.chdir(output_root)
    project_root = output_root / "clients" / project_name

    code = run_init(project_name, theme_slug="theme_a")
    assert code == 0
    _assert_output_boundary(project_root, output_root)
    _assert_source_theme_present(theme_root)
    assert theme_snapshot(theme_root) == before_snapshot

    settings_base = project_root / python_pkg / "settings" / "base.py"
    text = settings_base.read_text(encoding="utf-8")

    assert "SUM_CANONICAL_THEME_ROOT" in text
    assert "_get_canonical_theme_root" in text

    template_canonical_idx = text.find('canonical_theme_root / "templates"')
    template_active_idx = text.find('theme" / "active" / "templates"')
    assert template_canonical_idx != -1
    assert template_active_idx != -1
    assert template_canonical_idx < template_active_idx

    static_canonical_idx = text.find('canonical_theme_root / "static"')
    static_active_idx = text.find('theme" / "active" / "static"')
    assert static_canonical_idx != -1
    assert static_active_idx != -1
    assert static_canonical_idx < static_active_idx

    assert "ImproperlyConfigured" in text
    assert "Unset SUM_CANONICAL_THEME_ROOT" in text


def test_init_fails_fast_when_theme_missing_compiled_css(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """
    Theme exists + manifest is valid, but missing compiled CSS => init should fail
    before scaffolding the client project.
    """
    repo_root = Path(__file__).resolve().parents[2]
    monkeypatch.setenv("SUM_BOILERPLATE_PATH", str(repo_root / "boilerplate"))

    # Create a fake theme registry in a temp directory
    themes_dir = tmp_path / "themes"
    themes_dir.mkdir()

    slug = "theme_b"
    theme_dir = themes_dir / slug
    (theme_dir / "templates" / "theme").mkdir(parents=True)
    (theme_dir / "static" / slug / "css").mkdir(parents=True)

    (theme_dir / "theme.json").write_text(
        json.dumps(
            {
                "slug": slug,
                "name": "Theme B",
                "description": "Test theme for init validation",
                "version": "0.0.1",
            }
        ),
        encoding="utf-8",
    )
    (theme_dir / "templates" / "theme" / "base.html").write_text(
        "<!doctype html><html><body>{% block main %}{% endblock %}</body></html>\n",
        encoding="utf-8",
    )
    # Intentionally omit static/theme_b/css/main.css

    # Override theme discovery for this test to point at our temp registry
    monkeypatch.setenv("SUM_THEME_PATH", str(themes_dir))

    unique_suffix = int(time.time() * 1000) % 100000
    project_name = f"missing-css-{unique_suffix}"
    monkeypatch.chdir(tmp_path)
    project_root = tmp_path / "clients" / project_name

    code = run_init(project_name, theme_slug=slug)
    captured = capsys.readouterr()

    assert code == 1
    assert "Missing compiled CSS" in captured.out or "main.css" in captured.out
    assert not project_root.exists(), "init should not scaffold a half-broken client"
