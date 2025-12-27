from __future__ import annotations

import importlib.resources
import importlib.resources.abc
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from sum_cli.themes_registry import ThemeNotFoundError, ThemeValidationError
from sum_cli.util import (
    ProjectNaming,
    get_packaged_boilerplate,
    is_boilerplate_dir,
    safe_rmtree,
    safe_text_replace_in_file,
    validate_project_name,
)

from cli.sum.exceptions import SetupError
from cli.sum.utils.environment import find_monorepo_root

BoilerplateSource = Path | importlib.resources.abc.Traversable

DEFAULT_THEME_SLUG = "theme_a"
LEGACY_CORE_CSS_REF = "/static/sum_core/css/main.css"
MIN_COMPILED_CSS_BYTES = 5 * 1024


@dataclass(frozen=True, slots=True)
class ThemeManifest:
    slug: str
    name: str
    description: str
    version: str

    def validate(self) -> None:
        if not self.slug:
            raise ValueError("slug cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        if not self.version:
            raise ValueError("version cannot be empty")


def _read_manifest(theme_dir: Path) -> ThemeManifest:
    manifest_path = theme_dir / "theme.json"
    if not manifest_path.is_file():
        raise ThemeValidationError(f"Missing theme manifest: {manifest_path}")

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ThemeValidationError(
            f"Invalid JSON in theme manifest: {manifest_path} ({exc})"
        ) from exc

    if not isinstance(data, dict):
        raise ThemeValidationError(f"Theme manifest must be an object: {manifest_path}")

    manifest = ThemeManifest(
        slug=str(data.get("slug", "")).strip(),
        name=str(data.get("name", "")).strip(),
        description=str(data.get("description", "")).strip(),
        version=str(data.get("version", "")).strip(),
    )
    try:
        manifest.validate()
    except ValueError as exc:
        raise ThemeValidationError(str(exc)) from exc

    if manifest.slug != theme_dir.name:
        raise ThemeValidationError(
            f"Theme slug mismatch: dir='{theme_dir.name}' manifest='{manifest.slug}'"
        )
    return manifest


def _resolve_theme_dir(theme_slug: str, repo_root: Path | None) -> Path:
    slug = theme_slug.strip()
    if not slug:
        raise ThemeNotFoundError("Theme slug cannot be empty")

    env = os.getenv("SUM_THEME_PATH")
    if env:
        path = Path(env).expanduser().resolve()
        if not path.exists():
            raise ThemeNotFoundError(f"SUM_THEME_PATH does not exist: {path}")
        if (path / "theme.json").is_file():
            return path
        candidate = path / slug
        if candidate.is_dir():
            return candidate
        raise ThemeNotFoundError(
            f"Theme '{slug}' not found under SUM_THEME_PATH: {path}"
        )

    if repo_root is not None:
        repo_theme = repo_root / "themes" / slug
        if repo_theme.is_dir():
            return repo_theme

    cwd_theme = (Path.cwd() / "themes" / slug).resolve()
    if cwd_theme.is_dir():
        return cwd_theme

    raise ThemeNotFoundError(
        f"Theme '{slug}' not found. Looked in SUM_THEME_PATH (if set) and themes/"
    )


def _get_theme(theme_slug: str, repo_root: Path | None) -> tuple[ThemeManifest, Path]:
    theme_dir = _resolve_theme_dir(theme_slug, repo_root)
    try:
        return _read_manifest(theme_dir), theme_dir
    except ThemeValidationError as exc:
        raise ThemeValidationError(str(exc)) from exc


def _resolve_boilerplate_source(repo_root: Path | None) -> BoilerplateSource:
    env_override = os.getenv("SUM_BOILERPLATE_PATH")
    if env_override:
        path = Path(env_override).expanduser().resolve()
        if not is_boilerplate_dir(path):
            raise SetupError(
                "SUM_BOILERPLATE_PATH is set but is not a valid boilerplate dir: "
                f"{path}"
            )
        return path

    if repo_root is not None:
        repo_boilerplate = repo_root / "boilerplate"
        if is_boilerplate_dir(repo_boilerplate):
            return repo_boilerplate

    cwd_boilerplate = (Path.cwd() / "boilerplate").resolve()
    if is_boilerplate_dir(cwd_boilerplate):
        return cwd_boilerplate

    packaged = get_packaged_boilerplate()
    return cast(BoilerplateSource, packaged)


def _replace_placeholders(project_root: Path, naming: ProjectNaming) -> None:
    for dirpath, _, filenames in os.walk(project_root):
        for filename in filenames:
            path = Path(dirpath) / filename
            safe_text_replace_in_file(path, "project_name", naming.python_package)


def _rename_project_package_dir(project_root: Path, naming: ProjectNaming) -> None:
    src = project_root / "project_name"
    dst = project_root / naming.python_package
    if not src.exists():
        raise SetupError("Boilerplate is malformed: missing 'project_name/' package.")
    if dst.exists():
        raise SetupError(
            f"Refusing to overwrite existing project package directory: {dst}"
        )
    src.rename(dst)


def _create_env_from_example(project_root: Path) -> None:
    env_example = project_root / ".env.example"
    env_file = project_root / ".env"
    if env_file.exists():
        return
    if env_example.exists():
        shutil.copy2(env_example, env_file)


def _theme_contract_errors(theme_root: Path, theme_slug: str) -> list[str]:
    errors: list[str] = []

    manifest_path = theme_root / "theme.json"
    if not manifest_path.is_file():
        errors.append(f"Missing theme manifest: {manifest_path}")

    base_template = theme_root / "templates" / "theme" / "base.html"
    if not base_template.is_file():
        errors.append(f"Missing theme base template: {base_template}")

    compiled_css = theme_root / "static" / theme_slug / "css" / "main.css"
    if not compiled_css.is_file():
        errors.append(f"Missing compiled CSS: {compiled_css}")
    else:
        try:
            size = compiled_css.stat().st_size
        except OSError as exc:
            errors.append(f"Could not stat compiled CSS: {compiled_css} ({exc})")
        else:
            if size <= MIN_COMPILED_CSS_BYTES:
                errors.append(
                    f"Compiled CSS is unexpectedly small ({size} bytes): {compiled_css}"
                )

        try:
            css_text = compiled_css.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            errors.append(f"Could not read compiled CSS: {compiled_css} ({exc})")
        else:
            if LEGACY_CORE_CSS_REF in css_text:
                errors.append(
                    "Compiled CSS references legacy core stylesheet "
                    f"({LEGACY_CORE_CSS_REF}): {compiled_css}"
                )

    return errors


def _copy_theme_to_active(
    project_root: Path, theme_source_dir: Path, theme_slug: str
) -> None:
    theme_target_dir = project_root / "theme" / "active"
    theme_parent_dir = theme_target_dir.parent
    theme_parent_dir.mkdir(parents=True, exist_ok=True)

    if theme_target_dir.exists():
        raise SetupError(f"Theme target directory already exists: {theme_target_dir}")

    ignore = shutil.ignore_patterns("node_modules")
    with tempfile.TemporaryDirectory(prefix=f"sum-theme-{theme_slug}-") as tmp_root:
        tmp_dir = Path(tmp_root) / theme_slug
        shutil.copytree(theme_source_dir, tmp_dir, dirs_exist_ok=False, ignore=ignore)

        errors = _theme_contract_errors(tmp_dir, theme_slug)
        if errors:
            raise SetupError(
                "Theme copy validation failed:\n  - " + "\n  - ".join(errors)
            )

        shutil.move(str(tmp_dir), str(theme_target_dir))


def _write_theme_config(
    project_root: Path, theme_slug: str, theme_version: str
) -> None:
    sum_dir = project_root / ".sum"
    sum_dir.mkdir(parents=True, exist_ok=True)

    theme_config = {
        "theme": theme_slug,
        "original_version": theme_version,
        "locked_at": datetime.now(UTC).isoformat(),
    }

    theme_file = sum_dir / "theme.json"
    theme_file.write_text(
        json.dumps(theme_config, indent=2) + "\n",
        encoding="utf-8",
    )


def scaffold_project(
    project_name: str,
    clients_dir: Path,
    theme_slug: str = DEFAULT_THEME_SLUG,
) -> Path:
    try:
        naming = validate_project_name(project_name)
    except ValueError as exc:
        raise SetupError(str(exc)) from exc

    project_path: Path = clients_dir / naming.slug
    if project_path.exists():
        raise SetupError(f"Target directory already exists: {project_path}")

    repo_root = find_monorepo_root(clients_dir)

    try:
        theme_manifest, theme_source_dir = _get_theme(theme_slug, repo_root)
    except ThemeNotFoundError as exc:
        raise SetupError(f"Theme '{theme_slug}' does not exist.") from exc
    except ThemeValidationError as exc:
        raise SetupError(f"Theme '{theme_slug}' is invalid: {exc}") from exc

    contract_errors = _theme_contract_errors(theme_source_dir, theme_slug)
    if contract_errors:
        raise SetupError(
            f"Theme '{theme_slug}' is missing required files:\n  - "
            + "\n  - ".join(contract_errors)
        )

    boilerplate_source = _resolve_boilerplate_source(repo_root)

    try:
        clients_dir.mkdir(parents=True, exist_ok=True)
        if isinstance(boilerplate_source, Path):
            if not is_boilerplate_dir(boilerplate_source):
                raise SetupError(
                    f"Boilerplate missing or malformed at: {boilerplate_source}"
                )
            shutil.copytree(boilerplate_source, project_path, dirs_exist_ok=False)
        else:
            with importlib.resources.as_file(boilerplate_source) as bp_path:
                bp_path = Path(bp_path)
                if not is_boilerplate_dir(bp_path):
                    raise SetupError("Packaged boilerplate missing or malformed.")
                shutil.copytree(bp_path, project_path, dirs_exist_ok=False)
    except FileExistsError as exc:
        raise SetupError(f"Target directory already exists: {project_path}") from exc
    except SetupError:
        raise
    except Exception as exc:
        raise SetupError(f"Failed to copy boilerplate: {exc}") from exc

    try:
        _rename_project_package_dir(project_path, naming)
        _replace_placeholders(project_path, naming)
        _create_env_from_example(project_path)
        _copy_theme_to_active(project_path, theme_source_dir, theme_slug)
        _write_theme_config(project_path, theme_slug, theme_manifest.version)
    except Exception as exc:
        repo_root = find_monorepo_root(project_path)
        try:
            safe_rmtree(project_path, tmp_root=None, repo_root=repo_root)
        except Exception:
            pass
        raise SetupError(f"Project created but failed to finalize init: {exc}") from exc

    return project_path


def validate_project_structure(project_path: Path) -> None:
    if not project_path.is_dir():
        raise SetupError(f"Project directory does not exist: {project_path}")

    required_files = [
        project_path / "manage.py",
        project_path / "pytest.ini",
        project_path / ".env",
        project_path / ".env.example",
    ]
    for path in required_files:
        if not path.exists():
            raise SetupError(f"Missing required file: {path}")

    theme_dir = project_path / "theme" / "active"
    if not theme_dir.is_dir():
        raise SetupError(f"Missing active theme directory: {theme_dir}")

    theme_config = project_path / ".sum" / "theme.json"
    if not theme_config.is_file():
        raise SetupError(f"Missing theme config: {theme_config}")
