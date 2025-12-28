"""
Tests for scaffolding functionality.

Phase 1: Test coverage for cli/sum/setup/scaffold.py (currently 18% coverage).
These tests cover critical paths for project initialization including:
- Project name validation
- Theme resolution and validation
- Template substitution
- Error handling for edge cases
"""

from __future__ import annotations

import json

import pytest
from sum_cli.themes_registry import ThemeNotFoundError, ThemeValidationError
from sum_cli.util import ProjectNaming

from cli.sum.exceptions import SetupError
from cli.sum.setup.scaffold import (
    MIN_COMPILED_CSS_BYTES,
    ThemeManifest,
    _copy_theme_to_active,
    _create_env_from_example,
    _read_manifest,
    _rename_project_package_dir,
    _replace_placeholders,
    _resolve_theme_dir,
    _theme_contract_errors,
    _write_theme_config,
    scaffold_project,
    validate_project_structure,
)


class TestThemeManifest:
    """Test theme manifest validation."""

    def test_validate_rejects_empty_slug(self):
        manifest = ThemeManifest(
            slug="", name="Test", description="Test", version="1.0"
        )
        with pytest.raises(ValueError, match="slug cannot be empty"):
            manifest.validate()

    def test_validate_rejects_empty_name(self):
        manifest = ThemeManifest(
            slug="test", name="", description="Test", version="1.0"
        )
        with pytest.raises(ValueError, match="name cannot be empty"):
            manifest.validate()

    def test_validate_rejects_empty_version(self):
        manifest = ThemeManifest(
            slug="test", name="Test", description="Test", version=""
        )
        with pytest.raises(ValueError, match="version cannot be empty"):
            manifest.validate()

    def test_validate_accepts_valid_manifest(self):
        manifest = ThemeManifest(
            slug="test", name="Test", description="Test desc", version="1.0"
        )
        # Should not raise
        manifest.validate()


class TestReadManifest:
    """Test theme manifest reading and validation."""

    def test_read_manifest_missing_file(self, tmp_path):
        theme_dir = tmp_path / "test_theme"
        theme_dir.mkdir()

        with pytest.raises(ThemeValidationError, match="Missing theme manifest"):
            _read_manifest(theme_dir)

    def test_read_manifest_invalid_json(self, tmp_path):
        theme_dir = tmp_path / "test_theme"
        theme_dir.mkdir()
        manifest_path = theme_dir / "theme.json"
        manifest_path.write_text("{ invalid json }")

        with pytest.raises(ThemeValidationError, match="Invalid JSON"):
            _read_manifest(theme_dir)

    def test_read_manifest_not_dict(self, tmp_path):
        theme_dir = tmp_path / "test_theme"
        theme_dir.mkdir()
        manifest_path = theme_dir / "theme.json"
        manifest_path.write_text("[]")

        with pytest.raises(ThemeValidationError, match="must be an object"):
            _read_manifest(theme_dir)

    def test_read_manifest_slug_mismatch(self, tmp_path):
        theme_dir = tmp_path / "test_theme"
        theme_dir.mkdir()
        manifest_path = theme_dir / "theme.json"
        manifest_data = {
            "slug": "wrong_slug",
            "name": "Test Theme",
            "description": "A test theme",
            "version": "1.0.0",
        }
        manifest_path.write_text(json.dumps(manifest_data))

        with pytest.raises(ThemeValidationError, match="Theme slug mismatch"):
            _read_manifest(theme_dir)

    def test_read_manifest_valid(self, tmp_path):
        theme_dir = tmp_path / "test_theme"
        theme_dir.mkdir()
        manifest_path = theme_dir / "theme.json"
        manifest_data = {
            "slug": "test_theme",
            "name": "Test Theme",
            "description": "A test theme",
            "version": "1.0.0",
        }
        manifest_path.write_text(json.dumps(manifest_data))

        manifest = _read_manifest(theme_dir)
        assert manifest.slug == "test_theme"
        assert manifest.name == "Test Theme"
        assert manifest.version == "1.0.0"


class TestResolveThemeDir:
    """Test theme directory resolution."""

    def test_resolve_theme_dir_empty_slug(self):
        with pytest.raises(ThemeNotFoundError, match="slug cannot be empty"):
            _resolve_theme_dir("", None)

    def test_resolve_theme_dir_from_env(self, tmp_path, monkeypatch):
        theme_dir = tmp_path / "custom_theme"
        theme_dir.mkdir()
        (theme_dir / "theme.json").write_text("{}")

        monkeypatch.setenv("SUM_THEME_PATH", str(theme_dir))
        result = _resolve_theme_dir("any_slug", None)
        assert result == theme_dir

    def test_resolve_theme_dir_env_not_exist(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SUM_THEME_PATH", str(tmp_path / "nonexistent"))
        with pytest.raises(ThemeNotFoundError, match="SUM_THEME_PATH does not exist"):
            _resolve_theme_dir("test", None)

    def test_resolve_theme_dir_from_repo(self, tmp_path):
        repo_root = tmp_path / "repo"
        themes_dir = repo_root / "themes"
        theme_dir = themes_dir / "test_theme"
        theme_dir.mkdir(parents=True)

        result = _resolve_theme_dir("test_theme", repo_root)
        assert result == theme_dir

    def test_resolve_theme_dir_not_found(self, tmp_path):
        with pytest.raises(ThemeNotFoundError, match="not found"):
            _resolve_theme_dir("nonexistent_theme", tmp_path)


class TestReplacePlaceholders:
    """Test template placeholder replacement."""

    def test_replace_placeholders_in_files(self, tmp_path):
        project_root = tmp_path / "test_project"
        project_root.mkdir()

        # Create test files with placeholders
        test_file = project_root / "settings.py"
        test_file.write_text("PROJECT = 'project_name'\nPACKAGE = 'project_name'")

        naming = ProjectNaming(
            slug="test-project",
            python_package="test_project",
        )

        _replace_placeholders(project_root, naming)

        content = test_file.read_text()
        assert "test_project" in content
        assert "project_name" not in content

    def test_replace_placeholders_preserves_other_text(self, tmp_path):
        project_root = tmp_path / "test_project"
        project_root.mkdir()

        test_file = project_root / "readme.md"
        test_file.write_text("# project_name\n\nSome other text that should remain.")

        naming = ProjectNaming(
            slug="my-project",
            python_package="my_project",
        )

        _replace_placeholders(project_root, naming)

        content = test_file.read_text()
        assert "my_project" in content
        assert "Some other text that should remain" in content


class TestRenameProjectPackageDir:
    """Test project package directory renaming."""

    def test_rename_project_package_dir_success(self, tmp_path):
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        src_dir = project_root / "project_name"
        src_dir.mkdir()
        (src_dir / "__init__.py").write_text("")

        naming = ProjectNaming(
            slug="test",
            python_package="test_project",
        )

        _rename_project_package_dir(project_root, naming)

        assert not src_dir.exists()
        assert (project_root / "test_project").exists()
        assert (project_root / "test_project" / "__init__.py").exists()

    def test_rename_project_package_dir_missing_source(self, tmp_path):
        project_root = tmp_path / "test_project"
        project_root.mkdir()

        naming = ProjectNaming(
            slug="test",
            python_package="test_project",
        )

        with pytest.raises(SetupError, match="missing 'project_name/' package"):
            _rename_project_package_dir(project_root, naming)

    def test_rename_project_package_dir_target_exists(self, tmp_path):
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        src_dir = project_root / "project_name"
        src_dir.mkdir()
        dst_dir = project_root / "test_project"
        dst_dir.mkdir()

        naming = ProjectNaming(
            slug="test",
            python_package="test_project",
        )

        with pytest.raises(SetupError, match="Refusing to overwrite"):
            _rename_project_package_dir(project_root, naming)


class TestCreateEnvFromExample:
    """Test .env file creation from example."""

    def test_create_env_from_example_creates_file(self, tmp_path):
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        env_example = project_root / ".env.example"
        env_example.write_text("SECRET_KEY=example")

        _create_env_from_example(project_root)

        env_file = project_root / ".env"
        assert env_file.exists()
        assert env_file.read_text() == "SECRET_KEY=example"

    def test_create_env_from_example_skips_if_exists(self, tmp_path):
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        env_example = project_root / ".env.example"
        env_example.write_text("SECRET_KEY=example")
        env_file = project_root / ".env"
        env_file.write_text("SECRET_KEY=production")

        _create_env_from_example(project_root)

        # Should not overwrite existing .env
        assert env_file.read_text() == "SECRET_KEY=production"

    def test_create_env_from_example_no_example(self, tmp_path):
        project_root = tmp_path / "test_project"
        project_root.mkdir()

        # Should not raise, just skip creation
        _create_env_from_example(project_root)

        env_file = project_root / ".env"
        assert not env_file.exists()


class TestThemeContractErrors:
    """Test theme contract validation."""

    def test_theme_contract_errors_missing_manifest(self, tmp_path):
        theme_root = tmp_path / "test_theme"
        theme_root.mkdir()

        errors = _theme_contract_errors(theme_root, "test_theme")
        assert any("Missing theme manifest" in err for err in errors)

    def test_theme_contract_errors_missing_base_template(self, tmp_path):
        theme_root = tmp_path / "test_theme"
        theme_root.mkdir()
        (theme_root / "theme.json").write_text("{}")

        errors = _theme_contract_errors(theme_root, "test_theme")
        assert any("Missing theme base template" in err for err in errors)

    def test_theme_contract_errors_missing_css(self, tmp_path):
        theme_root = tmp_path / "test_theme"
        theme_root.mkdir()
        (theme_root / "theme.json").write_text("{}")
        templates_dir = theme_root / "templates" / "theme"
        templates_dir.mkdir(parents=True)
        (templates_dir / "base.html").write_text("<html></html>")

        errors = _theme_contract_errors(theme_root, "test_theme")
        assert any("Missing compiled CSS" in err for err in errors)

    def test_theme_contract_errors_css_too_small(self, tmp_path):
        theme_root = tmp_path / "test_theme"
        theme_root.mkdir()
        (theme_root / "theme.json").write_text("{}")
        templates_dir = theme_root / "templates" / "theme"
        templates_dir.mkdir(parents=True)
        (templates_dir / "base.html").write_text("<html></html>")
        css_dir = theme_root / "static" / "test_theme" / "css"
        css_dir.mkdir(parents=True)
        (css_dir / "main.css").write_text("/* too small */")

        errors = _theme_contract_errors(theme_root, "test_theme")
        assert any("unexpectedly small" in err for err in errors)

    def test_theme_contract_errors_legacy_css_ref(self, tmp_path):
        theme_root = tmp_path / "test_theme"
        theme_root.mkdir()
        (theme_root / "theme.json").write_text("{}")
        templates_dir = theme_root / "templates" / "theme"
        templates_dir.mkdir(parents=True)
        (templates_dir / "base.html").write_text("<html></html>")
        css_dir = theme_root / "static" / "test_theme" / "css"
        css_dir.mkdir(parents=True)
        # Create CSS large enough but with legacy reference
        css_content = "x" * (MIN_COMPILED_CSS_BYTES + 100)
        css_content += "\n@import '/static/sum_core/css/main.css';"
        (css_dir / "main.css").write_text(css_content)

        errors = _theme_contract_errors(theme_root, "test_theme")
        assert any("legacy core stylesheet" in err for err in errors)

    def test_theme_contract_errors_valid_theme(self, tmp_path):
        theme_root = tmp_path / "test_theme"
        theme_root.mkdir()
        (theme_root / "theme.json").write_text("{}")
        templates_dir = theme_root / "templates" / "theme"
        templates_dir.mkdir(parents=True)
        (templates_dir / "base.html").write_text("<html></html>")
        css_dir = theme_root / "static" / "test_theme" / "css"
        css_dir.mkdir(parents=True)
        # Create valid CSS (large enough, no legacy refs)
        css_content = "/* Valid theme CSS */\n" + ("body { margin: 0; }\n" * 500)
        (css_dir / "main.css").write_text(css_content)

        errors = _theme_contract_errors(theme_root, "test_theme")
        assert errors == []


class TestCopyThemeToActive:
    """Test theme copying with validation."""

    def test_copy_theme_to_active_success(self, tmp_path):
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create valid theme source
        theme_source = tmp_path / "theme_source"
        theme_source.mkdir()
        (theme_source / "theme.json").write_text("{}")
        templates_dir = theme_source / "templates" / "theme"
        templates_dir.mkdir(parents=True)
        (templates_dir / "base.html").write_text("<html></html>")
        css_dir = theme_source / "static" / "test_theme" / "css"
        css_dir.mkdir(parents=True)
        css_content = "/* Valid CSS */\n" + ("body { margin: 0; }\n" * 500)
        (css_dir / "main.css").write_text(css_content)

        _copy_theme_to_active(project_root, theme_source, "test_theme")

        theme_target = project_root / "theme" / "active"
        assert theme_target.exists()
        assert (theme_target / "theme.json").exists()
        assert (theme_target / "templates" / "theme" / "base.html").exists()

    def test_copy_theme_to_active_target_exists(self, tmp_path):
        project_root = tmp_path / "project"
        theme_target = project_root / "theme" / "active"
        theme_target.mkdir(parents=True)

        theme_source = tmp_path / "theme_source"
        theme_source.mkdir()

        with pytest.raises(SetupError, match="already exists"):
            _copy_theme_to_active(project_root, theme_source, "test_theme")

    def test_copy_theme_to_active_validation_fails(self, tmp_path):
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create invalid theme (missing manifest)
        theme_source = tmp_path / "theme_source"
        theme_source.mkdir()

        with pytest.raises(SetupError, match="validation failed"):
            _copy_theme_to_active(project_root, theme_source, "test_theme")


class TestWriteThemeConfig:
    """Test theme configuration file writing."""

    def test_write_theme_config_creates_file(self, tmp_path):
        project_root = tmp_path / "project"
        project_root.mkdir()

        _write_theme_config(project_root, "test_theme", "1.0.0")

        config_file = project_root / ".sum" / "theme.json"
        assert config_file.exists()

        config_data = json.loads(config_file.read_text())
        assert config_data["theme"] == "test_theme"
        assert config_data["original_version"] == "1.0.0"
        assert "locked_at" in config_data


class TestScaffoldProject:
    """Test full project scaffolding."""

    def test_scaffold_project_invalid_name(self, tmp_path):
        clients_dir = tmp_path / "clients"
        clients_dir.mkdir()

        with pytest.raises(SetupError):
            scaffold_project("invalid name!", clients_dir)

    def test_scaffold_project_target_exists(self, tmp_path):
        clients_dir = tmp_path / "clients"
        clients_dir.mkdir()
        existing_project = clients_dir / "test-project"
        existing_project.mkdir()

        with pytest.raises(SetupError, match="already exists"):
            scaffold_project("test-project", clients_dir)

    def test_scaffold_project_theme_not_found(self, tmp_path):
        clients_dir = tmp_path / "clients"
        clients_dir.mkdir()

        with pytest.raises(SetupError, match="does not exist"):
            scaffold_project("test-project", clients_dir, theme_slug="nonexistent")


class TestValidateProjectStructure:
    """Test project structure validation."""

    def test_validate_project_structure_not_dir(self, tmp_path):
        project_path = tmp_path / "nonexistent"

        with pytest.raises(SetupError, match="does not exist"):
            validate_project_structure(project_path)

    def test_validate_project_structure_missing_manage_py(self, tmp_path):
        project_path = tmp_path / "project"
        project_path.mkdir()

        with pytest.raises(SetupError, match="Missing required file.*manage.py"):
            validate_project_structure(project_path)

    def test_validate_project_structure_missing_theme(self, tmp_path):
        project_path = tmp_path / "project"
        project_path.mkdir()
        (project_path / "manage.py").write_text("")
        (project_path / "pytest.ini").write_text("")
        (project_path / ".env").write_text("")
        (project_path / ".env.example").write_text("")
        sum_dir = project_path / ".sum"
        sum_dir.mkdir()
        (sum_dir / "theme.json").write_text("{}")

        with pytest.raises(SetupError, match="Missing active theme directory"):
            validate_project_structure(project_path)

    def test_validate_project_structure_missing_theme_config(self, tmp_path):
        project_path = tmp_path / "project"
        project_path.mkdir()
        (project_path / "manage.py").write_text("")
        (project_path / "pytest.ini").write_text("")
        (project_path / ".env").write_text("")
        (project_path / ".env.example").write_text("")
        theme_dir = project_path / "theme" / "active"
        theme_dir.mkdir(parents=True)

        with pytest.raises(SetupError, match="Missing theme config"):
            validate_project_structure(project_path)

    def test_validate_project_structure_valid(self, tmp_path):
        project_path = tmp_path / "project"
        project_path.mkdir()
        (project_path / "manage.py").write_text("")
        (project_path / "pytest.ini").write_text("")
        (project_path / ".env").write_text("")
        (project_path / ".env.example").write_text("")
        theme_dir = project_path / "theme" / "active"
        theme_dir.mkdir(parents=True)
        sum_dir = project_path / ".sum"
        sum_dir.mkdir()
        (sum_dir / "theme.json").write_text("{}")

        # Should not raise
        validate_project_structure(project_path)
