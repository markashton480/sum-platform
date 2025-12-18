from __future__ import annotations

import importlib
import importlib.util
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckItem:
    name: str
    ok: bool
    details: str = ""


MIN_COMPILED_CSS_BYTES = 5 * 1024
LEGACY_CORE_CSS_REF = "/static/sum_core/css/main.css"

ENV_KEY_RE = re.compile(r"^([A-Z][A-Z0-9_]*)=(.*)$")
SETDEFAULT_RE = re.compile(
    r"""os\.environ\.setdefault\(\s*["']DJANGO_SETTINGS_MODULE["']\s*,\s*["']([^"']+)["']\s*\)"""
)


def _parse_env_assignments(path: Path) -> dict[str, str]:
    """
    Parse KEY=VALUE assignments from .env-style files.

    - ignores blank lines and comments
    - ignores commented-out assignments
    """
    data: dict[str, str] = {}
    if not path.exists():
        return data

    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = ENV_KEY_RE.match(line)
        if not m:
            continue
        key, value = m.group(1), m.group(2)
        data[key] = value
    return data


def _infer_settings_module(project_dir: Path) -> str | None:
    """
    Determine DJANGO_SETTINGS_MODULE for the project.

    Priority:
    - .env (if set)
    - manage.py os.environ.setdefault(...)
    """
    env = _parse_env_assignments(project_dir / ".env")
    if "DJANGO_SETTINGS_MODULE" in env and env["DJANGO_SETTINGS_MODULE"].strip():
        return env["DJANGO_SETTINGS_MODULE"].strip()

    manage_py = project_dir / "manage.py"
    if manage_py.exists():
        content = manage_py.read_text(encoding="utf-8", errors="ignore")
        m = SETDEFAULT_RE.search(content)
        if m:
            return m.group(1).strip()

    return None


def _read_json_file(path: Path) -> tuple[dict[str, object] | None, str]:
    """
    Read and parse a JSON file.

    Returns:
        (data, error) where data is None if parsing failed.
    """
    if not path.exists():
        return None, f"Missing file: {path}"
    try:
        return json.loads(path.read_text(encoding="utf-8")), ""
    except Exception as e:
        return None, f"Invalid JSON in {path}: {e}"


def _check_theme_contract(project_root: Path) -> list[CheckItem]:
    results: list[CheckItem] = []

    provenance_path = project_root / ".sum" / "theme.json"
    provenance, provenance_err = _read_json_file(provenance_path)
    expected_slug: str | None = None
    if provenance is None:
        results.append(
            CheckItem(
                name="Theme provenance",
                ok=False,
                details=f"{provenance_err} (expected from `sum init --theme <slug> ...`)",
            )
        )
    else:
        theme_value = provenance.get("theme")
        if isinstance(theme_value, str) and theme_value.strip():
            expected_slug = theme_value.strip()
            results.append(
                CheckItem(
                    name="Theme provenance",
                    ok=True,
                    details=f".sum/theme.json ({expected_slug})",
                )
            )
        else:
            results.append(
                CheckItem(
                    name="Theme provenance",
                    ok=False,
                    details="Missing `theme` field in .sum/theme.json",
                )
            )

    theme_root = project_root / "theme" / "active"
    if not theme_root.is_dir():
        results.append(
            CheckItem(
                name="Theme directory",
                ok=False,
                details=f"Missing {theme_root} (expected active theme install)",
            )
        )
        return results
    results.append(CheckItem(name="Theme directory", ok=True, details=str(theme_root)))

    manifest_path = theme_root / "theme.json"
    manifest, manifest_err = _read_json_file(manifest_path)
    manifest_slug: str | None = None
    if manifest is None:
        results.append(CheckItem(name="Theme manifest", ok=False, details=manifest_err))
    else:
        slug_value = manifest.get("slug")
        if isinstance(slug_value, str) and slug_value.strip():
            manifest_slug = slug_value.strip()
            if expected_slug and manifest_slug != expected_slug:
                results.append(
                    CheckItem(
                        name="Theme slug match",
                        ok=False,
                        details=f".sum says '{expected_slug}' but theme/active says '{manifest_slug}'",
                    )
                )
            else:
                results.append(
                    CheckItem(
                        name="Theme slug match",
                        ok=True,
                        details=manifest_slug,
                    )
                )
        else:
            results.append(
                CheckItem(
                    name="Theme manifest",
                    ok=False,
                    details="Missing `slug` field in theme/active/theme.json",
                )
            )

    base_template = theme_root / "templates" / "theme" / "base.html"
    if base_template.is_file():
        results.append(CheckItem(name="Theme base template", ok=True))
    else:
        results.append(
            CheckItem(
                name="Theme base template",
                ok=False,
                details=f"Missing {base_template}",
            )
        )

    css_slug = expected_slug or manifest_slug
    if not css_slug:
        results.append(
            CheckItem(
                name="Theme compiled CSS",
                ok=False,
                details="Could not determine theme slug for static path (check .sum/theme.json and theme/active/theme.json)",
            )
        )
        return results

    compiled_css = theme_root / "static" / css_slug / "css" / "main.css"
    if not compiled_css.is_file():
        results.append(
            CheckItem(
                name="Theme compiled CSS",
                ok=False,
                details=f"Missing {compiled_css}",
            )
        )
        return results

    try:
        size = compiled_css.stat().st_size
    except OSError as e:
        results.append(
            CheckItem(
                name="Theme compiled CSS",
                ok=False,
                details=f"Could not stat {compiled_css}: {e}",
            )
        )
        return results

    if size <= MIN_COMPILED_CSS_BYTES:
        results.append(
            CheckItem(
                name="Theme compiled CSS",
                ok=False,
                details=f"File too small ({size} bytes): {compiled_css}",
            )
        )
        return results

    try:
        css_text = compiled_css.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        results.append(
            CheckItem(
                name="Theme compiled CSS",
                ok=False,
                details=f"Could not read {compiled_css}: {e}",
            )
        )
        return results

    if LEGACY_CORE_CSS_REF in css_text:
        results.append(
            CheckItem(
                name="Theme compiled CSS",
                ok=False,
                details=f"References legacy stylesheet ({LEGACY_CORE_CSS_REF})",
            )
        )
        return results

    results.append(
        CheckItem(name="Theme compiled CSS", ok=True, details=str(compiled_css))
    )
    return results


def _urlconf_has_health_wiring(urlconf_module: str) -> tuple[bool, str]:
    spec = importlib.util.find_spec(urlconf_module)
    if spec is None or spec.origin is None:
        return False, f"Could not locate URLConf module: {urlconf_module}"
    path = Path(spec.origin)
    if not path.exists():
        return False, f"URLConf file not found: {path}"

    text = path.read_text(encoding="utf-8", errors="ignore")
    if "sum_core.ops.urls" not in text:
        return (
            False,
            "URLConf does not include sum_core ops URLs (expected /health/ wiring).",
        )
    return True, ""


def _scan_for_test_project_refs(project_dir: Path) -> list[Path]:
    hits: list[Path] = []
    skip_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        "staticfiles",
        "media",
        ".mypy_cache",
        ".pytest_cache",
    }
    allow_names = {
        "manage.py",
        "pytest.ini",
        "pyproject.toml",
        "requirements.txt",
        ".env",
        ".env.example",
    }
    allow_suffixes = {".py", ".txt", ".md", ".toml", ".ini", ".cfg", ".yml", ".yaml"}

    for dirpath, dirnames, filenames in os.walk(project_dir):
        # Prune in-place so os.walk doesn't descend into ignored directories.
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]

        for filename in filenames:
            path = Path(dirpath) / filename
            if path.name not in allow_names and path.suffix not in allow_suffixes:
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if "test_project" in content:
                hits.append(path)
    return hits


def _detect_monorepo_root(start_dir: Path) -> Path | None:
    """
    Traverse upward from start_dir to find the monorepo root.

    Returns the repo root if found (directory containing both `core/` and
    `boilerplate/` with expected markers), otherwise None.
    """
    current = start_dir.resolve()
    # Limit traversal to avoid infinite loops
    for _ in range(20):
        core_marker = current / "core" / "sum_core" / "__init__.py"
        boilerplate_marker = current / "boilerplate" / "manage.py"
        if core_marker.exists() and boilerplate_marker.exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _setup_monorepo_core_import(repo_root: Path) -> bool:
    """
    Add the monorepo core directory to sys.path if not already present.

    Returns True if the path was added, False if it was already present.
    """
    core_dir = repo_root / "core"
    core_str = str(core_dir)
    if core_str not in sys.path:
        sys.path.insert(0, core_str)
        return True
    return False


def _cleanup_monorepo_core_import(repo_root: Path) -> None:
    """Remove the monorepo core directory from sys.path if present."""
    core_dir = repo_root / "core"
    core_str = str(core_dir)
    if core_str in sys.path:
        sys.path.remove(core_str)


def run_check(project_dir: Path | None = None) -> int:
    """
    Validate that a client project is structurally correct.

    Returns exit code 0 on success, 1 on failure.
    """
    root = (project_dir or Path.cwd()).resolve()

    results: list[CheckItem] = []

    manage_py = root / "manage.py"
    if not manage_py.exists():
        results.append(
            CheckItem(
                name="Project root",
                ok=False,
                details="Run `sum check` from a client project directory (missing manage.py).",
            )
        )
        _print_results(results)
        return 1
    results.append(CheckItem(name="Project root", ok=True, details=str(root)))

    results.extend(_check_theme_contract(root))

    # Env vars: required keys come from .env.example assignments
    env_example_path = root / ".env.example"
    required_env = _parse_env_assignments(env_example_path)
    if not env_example_path.exists():
        results.append(
            CheckItem(
                name="Env template",
                ok=False,
                details="Missing .env.example",
            )
        )
    else:
        results.append(
            CheckItem(name="Env template", ok=True, details=".env.example found")
        )

    env = _parse_env_assignments(root / ".env")
    missing = []
    for key in required_env.keys():
        if key in env:
            continue
        if key in os.environ and os.environ[key].strip():
            continue
        missing.append(key)

    if required_env and missing:
        results.append(
            CheckItem(
                name="Required env vars",
                ok=False,
                details="Missing: " + ", ".join(sorted(missing)),
            )
        )
    else:
        results.append(CheckItem(name="Required env vars", ok=True))

    settings_module = _infer_settings_module(root)
    if not settings_module:
        results.append(
            CheckItem(
                name="Settings module",
                ok=False,
                details="Could not infer DJANGO_SETTINGS_MODULE from .env or manage.py",
            )
        )
        _print_results(results)
        return 1

    results.append(CheckItem(name="Settings module", ok=True, details=settings_module))

    # Ensure the project root is importable (like `manage.py` would do).
    added_to_syspath = False
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
        added_to_syspath = True

    try:
        try:
            settings_mod = importlib.import_module(settings_module)
            results.append(CheckItem(name="Settings import", ok=True))
        except Exception as e:
            results.append(
                CheckItem(
                    name="Settings import",
                    ok=False,
                    details=f"Failed to import {settings_module}: {e}",
                )
            )
            _print_results(results)
            return 1
        urlconf = getattr(settings_mod, "ROOT_URLCONF", None)
        if not isinstance(urlconf, str) or not urlconf.strip():
            results.append(
                CheckItem(
                    name="Health wiring",
                    ok=False,
                    details="Settings missing ROOT_URLCONF",
                )
            )
        else:
            ok, details = _urlconf_has_health_wiring(urlconf.strip())
            results.append(CheckItem(name="Health wiring", ok=ok, details=details))

        # sum_core import with monorepo detection
        monorepo_root = _detect_monorepo_root(root)
        monorepo_core_added = False
        if monorepo_root is not None:
            monorepo_core_added = _setup_monorepo_core_import(monorepo_root)

        try:
            importlib.import_module("sum_core")
            if monorepo_root is not None:
                results.append(
                    CheckItem(name="sum_core import", ok=True, details="monorepo mode")
                )
            else:
                results.append(CheckItem(name="sum_core import", ok=True))
        except ImportError:
            if monorepo_root is not None:
                # Monorepo mode but still failed - unexpected
                results.append(
                    CheckItem(
                        name="sum_core import",
                        ok=False,
                        details="Failed in monorepo mode - check core/ directory structure",
                    )
                )
            else:
                # Standalone mode - provide helpful message
                results.append(
                    CheckItem(
                        name="sum_core import",
                        ok=False,
                        details="Install requirements first: pip install -r requirements.txt",
                    )
                )
        except Exception as e:
            results.append(
                CheckItem(
                    name="sum_core import",
                    ok=False,
                    details=f"Failed to import sum_core: {e}",
                )
            )
        finally:
            if monorepo_core_added and monorepo_root is not None:
                _cleanup_monorepo_core_import(monorepo_root)

        hits = _scan_for_test_project_refs(root)
        if hits:
            results.append(
                CheckItem(
                    name="No test_project references",
                    ok=False,
                    details="Found in: "
                    + ", ".join(str(p.relative_to(root)) for p in hits[:10]),
                )
            )
        else:
            results.append(CheckItem(name="No test_project references", ok=True))

        _print_results(results)
        return 0 if all(r.ok for r in results) else 1
    finally:
        if added_to_syspath and str(root) in sys.path:
            sys.path.remove(str(root))


def _print_results(results: list[CheckItem]) -> None:
    for item in results:
        status = "OK" if item.ok else "FAIL"
        if item.details:
            print(f"[{status}] {item.name}: {item.details}")
        else:
            print(f"[{status}] {item.name}")
    if not all(r.ok for r in results):
        print("", file=sys.stderr)
        print("One or more checks failed.", file=sys.stderr)
