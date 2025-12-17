from __future__ import annotations

import importlib.resources
import importlib.resources.abc
import json
import os
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

from sum_cli.util import (
    ProjectNaming,
    get_packaged_boilerplate,
    is_boilerplate_dir,
    safe_text_replace_in_file,
    validate_project_name,
)

BoilerplateSource = Path | importlib.resources.abc.Traversable


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
    return packaged


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


def _copy_theme_to_active(project_root: Path, theme_slug: str) -> None:
    """
    Copy the selected theme from sum_core into the client's theme/active/ directory.

    Per THEME-ARCHITECTURE-SPECv1, themes are copied into the client project
    at init-time, not referenced from sum_core at runtime.

    Args:
        project_root: Root directory of the new project
        theme_slug: Theme identifier to copy

    Raises:
        ImportError: If sum_core is not installed
        RuntimeError: If theme copy fails
    """
    import sum_core.themes

    theme_source_dir = sum_core.themes.get_theme_dir(theme_slug)
    theme_target_dir = project_root / "theme" / "active"

    # Copy the entire theme directory
    shutil.copytree(theme_source_dir, theme_target_dir, dirs_exist_ok=False)


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
        import sum_core.themes

        theme_manifest = sum_core.themes.get_theme(theme_slug)
    except ImportError:
        print("[FAIL] sum_core is not installed or not importable.", file=sys.stderr)
        print("       Install sum_core: pip install -e ./core", file=sys.stderr)
        return 1
    except sum_core.themes.ThemeNotFoundError:
        print(f"[FAIL] Theme '{theme_slug}' does not exist.")
        print("       Run 'sum themes' to list available themes.")
        return 1
    except sum_core.themes.ThemeValidationError as e:
        print(f"[FAIL] Theme '{theme_slug}' is invalid: {e}")
        return 1
    except Exception as e:
        print(f"[FAIL] Failed to validate theme: {e}")
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
        _copy_theme_to_active(target_dir, theme_slug)
        _write_theme_config(target_dir, theme_slug, theme_manifest.version)
    except Exception as e:
        print(f"[FAIL] Project created but failed to finalize rename/replace: {e}")
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
