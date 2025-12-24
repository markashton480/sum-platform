from __future__ import annotations

import importlib.resources
import importlib.resources.abc
import json
import os
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from sum_cli.themes_registry import (
    ThemeNotFoundError,
    ThemeValidationError,
    get_theme,
    resolve_theme_dir,
)
from sum_cli.util import (
    ProjectNaming,
    find_repo_root,
    get_packaged_boilerplate,
    is_boilerplate_dir,
    safe_rmtree,
    safe_text_replace_in_file,
    validate_project_name,
)

BoilerplateSource = Path | importlib.resources.abc.Traversable

MIN_COMPILED_CSS_BYTES = 5 * 1024
LEGACY_CORE_CSS_REF = "/static/sum_core/css/main.css"


def _resolve_boilerplate_source() -> BoilerplateSource:
    """
    Prefer the repo's /boilerplate when present (canonical source),
    otherwise fall back to the packaged boilerplate.
    """
    env_override = os.getenv("SUM_BOILERPLATE_PATH")
    if env_override:
        p = Path(env_override).expanduser().resolve()
        if not is_boilerplate_dir(p):
            raise RuntimeError(
                f"SUM_BOILERPLATE_PATH is set but is not a valid boilerplate dir: {p}"
            )
        return p

    cwd_bp = (Path.cwd() / "boilerplate").resolve()
    if is_boilerplate_dir(cwd_bp):
        return cwd_bp

    packaged = get_packaged_boilerplate()
    return cast(BoilerplateSource, packaged)


def _replace_placeholders(project_root: Path, naming: ProjectNaming) -> None:
    # Use os.walk so we also process dotfiles like .env.example.
    for dirpath, _, filenames in os.walk(project_root):
        for filename in filenames:
            path = Path(dirpath) / filename
            safe_text_replace_in_file(path, "project_name", naming.python_package)


def _rename_project_package_dir(project_root: Path, naming: ProjectNaming) -> None:
    src = project_root / "project_name"
    dst = project_root / naming.python_package
    if not src.exists():
        raise RuntimeError("Boilerplate is malformed: missing 'project_name/' package.")
    if dst.exists():
        raise RuntimeError(
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
        except OSError as e:
            errors.append(f"Could not stat compiled CSS: {compiled_css} ({e})")
        else:
            if size <= MIN_COMPILED_CSS_BYTES:
                errors.append(
                    f"Compiled CSS is unexpectedly small ({size} bytes): {compiled_css}"
                )

        try:
            css_text = compiled_css.read_text(encoding="utf-8", errors="ignore")
        except OSError as e:
            errors.append(f"Could not read compiled CSS: {compiled_css} ({e})")
        else:
            if LEGACY_CORE_CSS_REF in css_text:
                errors.append(
                    f"Compiled CSS references legacy core stylesheet ({LEGACY_CORE_CSS_REF}): {compiled_css}"
                )

    return errors


def _copy_theme_to_active(
    project_root: Path, theme_source_dir: Path, theme_slug: str
) -> None:
    """
    Copy the selected theme into the client's theme/active/ directory.

    Per THEME-ARCHITECTURE-SPECv1, themes are copied into the client project
    at init-time, not referenced from sum_core at runtime.

    Args:
        project_root: Root directory of the new project
        theme_slug: Theme identifier to copy

    Raises:
        RuntimeError: If theme copy fails
    """
    theme_target_dir = project_root / "theme" / "active"
    theme_parent_dir = theme_target_dir.parent
    theme_parent_dir.mkdir(parents=True, exist_ok=True)

    if theme_target_dir.exists():
        raise RuntimeError(f"Theme target directory already exists: {theme_target_dir}")

    ignore = shutil.ignore_patterns("node_modules")
    with tempfile.TemporaryDirectory(prefix=f"sum-theme-{theme_slug}-") as tmp_root:
        tmp_dir = Path(tmp_root) / theme_slug
        shutil.copytree(theme_source_dir, tmp_dir, dirs_exist_ok=False, ignore=ignore)

        errors = _theme_contract_errors(tmp_dir, theme_slug)
        if errors:
            raise RuntimeError(
                "Theme copy validation failed:\n  - " + "\n  - ".join(errors)
            )

        shutil.move(str(tmp_dir), str(theme_target_dir))


def _write_theme_config(
    project_root: Path, theme_slug: str, theme_version: str
) -> None:
    """
    Write theme provenance to .sum/theme.json.

    This file records which theme was selected and when, for provenance tracking.
    It is NOT used for runtime loading - templates/static are served from theme/active/.

    Args:
        project_root: Root directory of the new project
        theme_slug: Selected theme identifier
        theme_version: Version of the theme at init time
    """
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


def run_init(project_name: str, theme_slug: str = "theme_a") -> int:
    try:
        naming = validate_project_name(project_name)
    except ValueError as e:
        print(f"[FAIL] {e}")
        return 1

    # Validate theme exists
    try:
        theme_manifest = get_theme(theme_slug)
        theme_source_dir = resolve_theme_dir(theme_slug)
    except ThemeNotFoundError:
        print(f"[FAIL] Theme '{theme_slug}' does not exist.")
        print("       Run 'sum themes' to list available themes.")
        return 1
    except ThemeValidationError as e:
        print(f"[FAIL] Theme '{theme_slug}' is invalid: {e}")
        return 1
    except Exception as e:
        print(f"[FAIL] Failed to validate theme: {e}")
        return 1

    contract_errors = _theme_contract_errors(theme_source_dir, theme_slug)
    if contract_errors:
        print(f"[FAIL] Theme '{theme_slug}' is missing required files:")
        for err in contract_errors:
            print(f"       - {err}")
        print("       Fix the theme files in sum_core before running init.")
        return 1

    try:
        boilerplate_source = _resolve_boilerplate_source()
    except Exception as e:
        print(f"[FAIL] {e}")
        return 1

    clients_dir = Path.cwd() / "clients"
    target_dir = clients_dir / naming.slug

    if target_dir.exists():
        print(f"[FAIL] Target directory already exists: {target_dir}")
        return 1

    clients_dir.mkdir(parents=True, exist_ok=True)

    try:
        if isinstance(boilerplate_source, Path):
            if not is_boilerplate_dir(boilerplate_source):
                raise RuntimeError(
                    f"Boilerplate missing or malformed at: {boilerplate_source}"
                )
            shutil.copytree(boilerplate_source, target_dir, dirs_exist_ok=False)
        else:
            with importlib.resources.as_file(boilerplate_source) as bp_path:
                bp_path = Path(bp_path)
                if not is_boilerplate_dir(bp_path):
                    raise RuntimeError("Packaged boilerplate missing or malformed.")
                shutil.copytree(bp_path, target_dir, dirs_exist_ok=False)
    except FileExistsError:
        print(f"[FAIL] Target directory already exists: {target_dir}")
        return 1
    except Exception as e:
        print(f"[FAIL] Failed to copy boilerplate: {e}")
        return 1

    try:
        _rename_project_package_dir(target_dir, naming)
        _replace_placeholders(target_dir, naming)
        _create_env_from_example(target_dir)
        _copy_theme_to_active(target_dir, theme_source_dir, theme_slug)
        _write_theme_config(target_dir, theme_slug, theme_manifest.version)
    except Exception as e:
        print(f"[FAIL] Project created but failed to finalize init: {e}")
        repo_root = find_repo_root(Path.cwd())
        tmp_root = Path(tempfile.gettempdir())
        try:
            safe_rmtree(target_dir, tmp_root=tmp_root, repo_root=repo_root)
            print(f"       Cleaned up partial project: {target_dir}")
        except Exception as cleanup_error:
            print(f"       Refused to delete: {cleanup_error}")
            print(f"       You may need to delete: {target_dir}")
        return 1

    print("[OK] Project created.")
    print(f"     Location: {target_dir}")
    print(f"     Theme: {theme_slug}")
    print("")
    print("Next steps:")
    print(f"  cd {target_dir}")
    print("  # create/activate your venv, install requirements.txt, then:")
    print("  sum check")
    return 0
