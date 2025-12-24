# M5-003 task implementation
_Exported on 12/16/2025 at 18:13:58 GMT from Cursor (2.2.20)_

---

**User**

Please see @AGENTS.md and @docs/dev/AGENT-ORIENTATION.md to establish your baseline understanding of this project, then see task details in @docs/dev/M5/M5-003.md.  Carefully implement, paying close attention to the requirements and guardrails. Take your time, and think through each step. When complete, please write a full work report and file it in `docs/dev/M5/M5-003_followup.md.`  

---

**Cursor**

Got it. I’ll first inspect the existing repo structure (`cli/`, packaging config, and the current `/boilerplate/` placeholders), then implement `sum init` + `sum check` with a minimal, deterministic argparse-based CLI, add pytest coverage (unit + one integration-style temp-dir flow), and finally write the requested work report to `docs/dev/M5/M5-003_followup.md`.

Nice: the repo currently has only a stub `cli/__init__.py` and the root `pyproject.toml` is monorepo-oriented (tests run from `tests/`, and boilerplate is excluded from mypy). Next I’ll inspect the boilerplate placeholders + existing “smoke consumer” patterns, then implement a self-contained `sum_cli` package under `cli/` and wire a `sum` console script in `pyproject.toml`.

Aha: the boilerplate already standardizes on a literal `project_name` Python package folder and string placeholders in `manage.py`, `pytest.ini`, and settings—so `sum init` can be a deterministic “copy + rename directory + global text replacement” exactly like the boilerplate README. Next I’ll inspect the boilerplate’s `.env.example` + URLs/health wiring, then implement the CLI package and hook it up to a `sum` console script.

Next I’ll trace how packaging is meant to work for the CLI in this repo (root `pyproject.toml` vs a dedicated `cli/pyproject.toml`), since that determines where we wire the `sum` console script and how we bundle `boilerplate/` so `sum init` works outside the monorepo.

I found two competing expectations in the docs: M5-003 says `sum check` takes no args, while the SSOT mentions `sum check <project-path>`. I’ll treat M5-003 as the locked spec for this milestone, but I’ll design the implementation so adding an optional path later is trivial. Next I’ll inspect SSOT + existing tooling to decide whether the CLI should be its own installable package (`cli/pyproject.toml`) like `core/`, and then start implementing `sum_cli` with boilerplate bundled as package data.

Good catch: `.env.example` is present but hidden from the repo-reading tool because it’s a dotfile. I’ll inspect it via the terminal instead, then implement `sum check` to parse it normally from disk (Python can read it fine) to validate required env vars.

```plaintext
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "sum-cli"
version = "0.1.0"
description = "SUM Platform CLI (v1): sum init + sum check"
requires-python = ">=3.12"
dependencies = []

[project.scripts]
sum = "sum_cli.__main__:main"

[tool.setuptools]
include-package-data = true

[tool.setuptools.packages.find]
where = ["."]
include = ["sum_cli*"]

[tool.setuptools.package-data]
sum_cli = [
  "boilerplate/**/*",
]


```

```python
"""
SUM CLI package.

This package intentionally contains no Django imports. It is filesystem
scaffolding + validation only.
"""

from __future__ import annotations


```

```python
from __future__ import annotations

import sys

from sum_cli.cli import main as _main


def main() -> None:
    sys.exit(_main())


if __name__ == "__main__":
    main()


```

```python
from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from sum_cli.commands.check import run_check
from sum_cli.commands.init import run_init


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sum",
        description="SUM Platform CLI (v1): scaffolding + validation only",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init", help="Create a new client project from the boilerplate"
    )
    init_parser.add_argument("project_name", help="Client project name (slug)")

    subparsers.add_parser("check", help="Validate the current client project")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """
    CLI entry point for both console script and tests.

    Returns a process exit code (0 success, 1 failure, 2 usage).
    """
    args = _build_parser().parse_args(list(argv) if argv is not None else None)

    if args.command == "init":
        return run_init(project_name=str(args.project_name))
    if args.command == "check":
        return run_check()

    # Defensive: argparse required=True should prevent this.
    print("Unknown command.", file=sys.stderr)
    return 2


```

Cool: we now have a clean, dependency-free `sum_cli` skeleton with a real `sum` entrypoint and a dedicated `cli/pyproject.toml` that can ship the boilerplate as package data. Next I’ll implement the actual `init` and `check` command logic (name validation, copy/rename/replace, structured checks + exit codes), then wire in pytest coverage under `cli/tests/` so we don’t inherit the Django-heavy root test fixtures.

```python
from __future__ import annotations


```

```python
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import importlib.resources


PROJECT_SLUG_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9-]*$")


@dataclass(frozen=True)
class ProjectNaming:
    """
    Naming derived from the user-provided project slug.

    - slug: directory name under clients/
    - python_package: importable Python identifier (hyphens converted to underscores)
    """

    slug: str
    python_package: str


def validate_project_name(project_name: str) -> ProjectNaming:
    """
    Validate and normalize the project name.

    Allowed: lowercase letters, digits, hyphens; must start with a letter.
    """
    name = project_name.strip()
    if not PROJECT_SLUG_RE.fullmatch(name):
        raise ValueError(
            "Invalid project name. Use lowercase letters, digits, and hyphens "
            "(must start with a letter). Example: acme-kitchens"
        )
    python_pkg = name.replace("-", "_")
    return ProjectNaming(slug=name, python_package=python_pkg)


def get_packaged_boilerplate_dir() -> Path:
    """
    Return the boilerplate directory bundled with the CLI package.
    """
    root = importlib.resources.files("sum_cli")
    bp = root.joinpath("boilerplate")
    # importlib.resources returns a Traversable; cast to Path when possible.
    # In source checkouts, this is a real path; in wheels, it's still readable.
    try:
        return Path(bp)  # type: ignore[arg-type]
    except TypeError:
        # Fallback: materialize to a temporary location is out of scope here;
        # we rely on wheel installs having a real filesystem path.
        raise RuntimeError("Packaged boilerplate is not available as a filesystem path.")


def is_boilerplate_dir(path: Path) -> bool:
    """
    Minimal structural validation for a boilerplate directory.
    """
    return (
        path.is_dir()
        and (path / "manage.py").is_file()
        and (path / "pytest.ini").is_file()
        and (path / "project_name").is_dir()
    )


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def safe_text_replace_in_file(path: Path, old: str, new: str) -> bool:
    """
    Replace text in a file if it looks like UTF-8 text.

    Returns True if the file was modified.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    if old not in content:
        return False

    path.write_text(content.replace(old, new), encoding="utf-8")
    return True


```

```python
from __future__ import annotations

import os
import shutil
from pathlib import Path

from sum_cli.util import (
    ProjectNaming,
    get_packaged_boilerplate_dir,
    is_boilerplate_dir,
    safe_text_replace_in_file,
    validate_project_name,
)


def _resolve_boilerplate_dir() -> Path:
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

    packaged = get_packaged_boilerplate_dir()
    if not is_boilerplate_dir(packaged):
        raise RuntimeError(
            "Packaged boilerplate missing or malformed. "
            "Install a CLI build that includes boilerplate data."
        )
    return packaged


def _replace_placeholders(project_root: Path, naming: ProjectNaming) -> None:
    for path in project_root.rglob("*"):
        if path.is_file():
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


def run_init(project_name: str) -> int:
    try:
        naming = validate_project_name(project_name)
    except ValueError as e:
        print(f"[FAIL] {e}")
        return 1

    try:
        boilerplate_dir = _resolve_boilerplate_dir()
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
        shutil.copytree(boilerplate_dir, target_dir, dirs_exist_ok=False)
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
    except Exception as e:
        print(f"[FAIL] Project created but failed to finalize rename/replace: {e}")
        print(f"       You may need to delete: {target_dir}")
        return 1

    print("[OK] Project created.")
    print(f"     Location: {target_dir}")
    print("")
    print("Next steps:")
    print(f"  cd {target_dir}")
    print("  # create/activate your venv, install requirements.txt, then:")
    print("  sum check")
    return 0


```

```python
from __future__ import annotations

import importlib
import importlib.util
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


def _urlconf_has_health_wiring(urlconf_module: str) -> tuple[bool, str]:
    spec = importlib.util.find_spec(urlconf_module)
    if spec is None or spec.origin is None:
        return False, f"Could not locate URLConf module: {urlconf_module}"
    path = Path(spec.origin)
    if not path.exists():
        return False, f"URLConf file not found: {path}"

    text = path.read_text(encoding="utf-8", errors="ignore")
    if "sum_core.ops.urls" not in text:
        return False, "URLConf does not include sum_core ops URLs (expected /health/ wiring)."
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

    for path in project_dir.rglob("*"):
        if path.is_dir():
            if path.name in skip_dirs:
                # Prevent descending into this directory by skipping children via continue;
                # rglob doesn't support prune, so we just ignore hits within it.
                continue
            continue

        if path.name not in allow_names and path.suffix not in allow_suffixes:
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "test_project" in content:
            hits.append(path)
    return hits


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
        results.append(CheckItem(name="Env template", ok=True, details=".env.example found"))

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

    try:
        importlib.import_module("sum_core")
        results.append(CheckItem(name="sum_core import", ok=True))
    except Exception as e:
        results.append(
            CheckItem(
                name="sum_core import",
                ok=False,
                details=f"Failed to import sum_core: {e}",
            )
        )

    hits = _scan_for_test_project_refs(root)
    if hits:
        results.append(
            CheckItem(
                name="No test_project references",
                ok=False,
                details="Found in: " + ", ".join(str(p.relative_to(root)) for p in hits[:10]),
            )
        )
    else:
        results.append(CheckItem(name="No test_project references", ok=True))

    _print_results(results)
    return 0 if all(r.ok for r in results) else 1


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


```

```python
from __future__ import annotations

import importlib
import importlib.util
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


def _urlconf_has_health_wiring(urlconf_module: str) -> tuple[bool, str]:
    spec = importlib.util.find_spec(urlconf_module)
    if spec is None or spec.origin is None:
        return False, f"Could not locate URLConf module: {urlconf_module}"
    path = Path(spec.origin)
    if not path.exists():
        return False, f"URLConf file not found: {path}"

    text = path.read_text(encoding="utf-8", errors="ignore")
    if "sum_core.ops.urls" not in text:
        return False, "URLConf does not include sum_core ops URLs (expected /health/ wiring)."
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
        results.append(CheckItem(name="Env template", ok=True, details=".env.example found"))

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

    try:
        importlib.import_module("sum_core")
        results.append(CheckItem(name="sum_core import", ok=True))
    except Exception as e:
        results.append(
            CheckItem(
                name="sum_core import",
                ok=False,
                details=f"Failed to import sum_core: {e}",
            )
        )

    hits = _scan_for_test_project_refs(root)
    if hits:
        results.append(
            CheckItem(
                name="No test_project references",
                ok=False,
                details="Found in: " + ", ".join(str(p.relative_to(root)) for p in hits[:10]),
            )
        )
    else:
        results.append(CheckItem(name="No test_project references", ok=True))

    _print_results(results)
    return 0 if all(r.ok for r in results) else 1


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



```

```plaintext
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "Straight Up Marketing Platform"
version = "0.1.0"
description = "Monorepo for trade website platform"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = [
    "black>=23.0.0",
    "isort>=5.12.0",
    "ruff>=0.1.0",
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.5.0",
    "pre-commit>=3.4.0",
]

[tool.black]
line-length = 88
target-version = ["py312"]
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_glob = ["*/migrations/*", "*/venv/*", "*/.venv/*"]

[tool.ruff]
line-length = 88
target-version = "py312"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort (we'll use isort directly, but ruff can check)
    "N",   # pep8-naming
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by black)
    "I001",  # isort handled separately
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__.py

[tool.pytest.ini_options]
testpaths = ["tests", "cli/tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--cov=.",
    "--cov-report=term-missing",
    "--cov-report=term-missing",
    "--cov-report=html",
]
pythonpath = ["core", "core/sum_core/test_project", "cli"]
DJANGO_SETTINGS_MODULE = "sum_core.test_project.test_project.settings"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow running tests",
    "django_db: Tests that require database access",
]

[tool.coverage.run]
source = ["."]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*",
    "*/migrations/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == \"__main__\":",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
ignore_missing_imports = true
exclude = [
    "/(build|dist|\\.eggs|\\.git|\\.hg|\\.mypy_cache|\\.tox|\\.venv|venv|_build|buck-out)/",
    "^boilerplate/",
]

```

```python
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


```

```python
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import importlib.resources

import importlib.resources.abc

PROJECT_SLUG_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9-]*$")


@dataclass(frozen=True)
class ProjectNaming:
    """
    Naming derived from the user-provided project slug.

    - slug: directory name under clients/
    - python_package: importable Python identifier (hyphens converted to underscores)
    """

    slug: str
    python_package: str


def validate_project_name(project_name: str) -> ProjectNaming:
    """
    Validate and normalize the project name.

    Allowed: lowercase letters, digits, hyphens; must start with a letter.
    """
    name = project_name.strip()
    if not PROJECT_SLUG_RE.fullmatch(name):
        raise ValueError(
            "Invalid project name. Use lowercase letters, digits, and hyphens "
            "(must start with a letter). Example: acme-kitchens"
        )
    python_pkg = name.replace("-", "_")
    return ProjectNaming(slug=name, python_package=python_pkg)


def get_packaged_boilerplate() -> importlib.resources.abc.Traversable:
    """
    Return the boilerplate directory bundled with the CLI package as a Traversable.

    Use `importlib.resources.as_file(...)` to materialize this to a real filesystem
    path when you need to pass it to APIs like shutil.copytree.
    """
    root = importlib.resources.files("sum_cli")
    return root.joinpath("boilerplate")


def is_boilerplate_dir(path: Path) -> bool:
    """
    Minimal structural validation for a boilerplate directory.
    """
    return (
        path.is_dir()
        and (path / "manage.py").is_file()
        and (path / "pytest.ini").is_file()
        and (path / "project_name").is_dir()
    )


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def safe_text_replace_in_file(path: Path, old: str, new: str) -> bool:
    """
    Replace text in a file if it looks like UTF-8 text.

    Returns True if the file was modified.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    if old not in content:
        return False

    path.write_text(content.replace(old, new), encoding="utf-8")
    return True



```

```python
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Union

import importlib.resources
import importlib.resources.abc

from sum_cli.util import (
    ProjectNaming,
    get_packaged_boilerplate,
    is_boilerplate_dir,
    safe_text_replace_in_file,
    validate_project_name,
)

BoilerplateSource = Union[Path, importlib.resources.abc.Traversable]


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
    for path in project_root.rglob("*"):
        if path.is_file():
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


def run_init(project_name: str) -> int:
    try:
        naming = validate_project_name(project_name)
    except ValueError as e:
        print(f"[FAIL] {e}")
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
    except Exception as e:
        print(f"[FAIL] Project created but failed to finalize rename/replace: {e}")
        print(f"       You may need to delete: {target_dir}")
        return 1

    print("[OK] Project created.")
    print(f"     Location: {target_dir}")
    print("")
    print("Next steps:")
    print(f"  cd {target_dir}")
    print("  # create/activate your venv, install requirements.txt, then:")
    print("  sum check")
    return 0



```

```python
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



```

```python
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Union

import importlib.resources
import importlib.resources.abc

from sum_cli.util import (
    ProjectNaming,
    get_packaged_boilerplate,
    is_boilerplate_dir,
    safe_text_replace_in_file,
    validate_project_name,
)

BoilerplateSource = Union[Path, importlib.resources.abc.Traversable]


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


def run_init(project_name: str) -> int:
    try:
        naming = validate_project_name(project_name)
    except ValueError as e:
        print(f"[FAIL] {e}")
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
    except Exception as e:
        print(f"[FAIL] Project created but failed to finalize rename/replace: {e}")
        print(f"       You may need to delete: {target_dir}")
        return 1

    print("[OK] Project created.")
    print(f"     Location: {target_dir}")
    print("")
    print("Next steps:")
    print(f"  cd {target_dir}")
    print("  # create/activate your venv, install requirements.txt, then:")
    print("  sum check")
    return 0



```

```python
from __future__ import annotations

import importlib
import importlib.util
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


def _urlconf_has_health_wiring(urlconf_module: str) -> tuple[bool, str]:
    spec = importlib.util.find_spec(urlconf_module)
    if spec is None or spec.origin is None:
        return False, f"Could not locate URLConf module: {urlconf_module}"
    path = Path(spec.origin)
    if not path.exists():
        return False, f"URLConf file not found: {path}"

    text = path.read_text(encoding="utf-8", errors="ignore")
    if "sum_core.ops.urls" not in text:
        return False, "URLConf does not include sum_core ops URLs (expected /health/ wiring)."
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
        results.append(CheckItem(name="Env template", ok=True, details=".env.example found"))

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
        if added_to_syspath:
            sys.path.remove(str(root))
        _print_results(results)
        return 1
    finally:
        # Keep sys.path changes in place only for the duration of this check run.
        if added_to_syspath and str(root) in sys.path:
            sys.path.remove(str(root))

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

    try:
        importlib.import_module("sum_core")
        results.append(CheckItem(name="sum_core import", ok=True))
    except Exception as e:
        results.append(
            CheckItem(
                name="sum_core import",
                ok=False,
                details=f"Failed to import sum_core: {e}",
            )
        )

    hits = _scan_for_test_project_refs(root)
    if hits:
        results.append(
            CheckItem(
                name="No test_project references",
                ok=False,
                details="Found in: " + ", ".join(str(p.relative_to(root)) for p in hits[:10]),
            )
        )
    else:
        results.append(CheckItem(name="No test_project references", ok=True))

    _print_results(results)
    return 0 if all(r.ok for r in results) else 1


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



```

```python
from __future__ import annotations

import importlib
import importlib.util
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


def _urlconf_has_health_wiring(urlconf_module: str) -> tuple[bool, str]:
    spec = importlib.util.find_spec(urlconf_module)
    if spec is None or spec.origin is None:
        return False, f"Could not locate URLConf module: {urlconf_module}"
    path = Path(spec.origin)
    if not path.exists():
        return False, f"URLConf file not found: {path}"

    text = path.read_text(encoding="utf-8", errors="ignore")
    if "sum_core.ops.urls" not in text:
        return False, "URLConf does not include sum_core ops URLs (expected /health/ wiring)."
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
        results.append(CheckItem(name="Env template", ok=True, details=".env.example found"))

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

    try:
        importlib.import_module("sum_core")
        results.append(CheckItem(name="sum_core import", ok=True))
    except Exception as e:
        results.append(
            CheckItem(
                name="sum_core import",
                ok=False,
                details=f"Failed to import sum_core: {e}",
            )
        )

    hits = _scan_for_test_project_refs(root)
    if hits:
        results.append(
            CheckItem(
                name="No test_project references",
                ok=False,
                details="Found in: " + ", ".join(str(p.relative_to(root)) for p in hits[:10]),
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



```

```python
from __future__ import annotations

import importlib
import importlib.util
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


def _urlconf_has_health_wiring(urlconf_module: str) -> tuple[bool, str]:
    spec = importlib.util.find_spec(urlconf_module)
    if spec is None or spec.origin is None:
        return False, f"Could not locate URLConf module: {urlconf_module}"
    path = Path(spec.origin)
    if not path.exists():
        return False, f"URLConf file not found: {path}"

    text = path.read_text(encoding="utf-8", errors="ignore")
    if "sum_core.ops.urls" not in text:
        return False, "URLConf does not include sum_core ops URLs (expected /health/ wiring)."
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
        results.append(CheckItem(name="Env template", ok=True, details=".env.example found"))

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

        try:
            importlib.import_module("sum_core")
            results.append(CheckItem(name="sum_core import", ok=True))
        except Exception as e:
            results.append(
                CheckItem(
                    name="sum_core import",
                    ok=False,
                    details=f"Failed to import sum_core: {e}",
                )
            )

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



```

```markdown
## SUM CLI (v1): `sum init`, `sum check`

This repo ships a minimal **filesystem scaffolding + validation CLI**.
It intentionally does **not** create virtualenvs, install dependencies, initialise git, or touch databases.

### Install (monorepo dev)

From repo root (using the repo virtualenv):

```bash
source .venv/bin/activate
pip install -e ./cli
```

### `sum init <project-name>`

Creates a new client project at `clients/<project-name>/` by copying the boilerplate and applying deterministic renames:

- client directory name uses the provided slug (e.g. `acme-kitchens`)
- Django project package name is normalized for Python imports (hyphens → underscores, e.g. `acme_kitchens`)
- all `project_name` placeholders are replaced
- `.env` is created by copying `.env.example` (no secret generation)

Run from the repo root:

```bash
sum init acme-kitchens
```

### `sum check`

Validates the **current working directory** is a structurally-correct client project:

- `.env.example` exists
- required env var keys (from `.env.example`) are provided via `.env` and/or process environment
- settings module is importable (inferred from `.env` or `manage.py`)
- URLConf includes sum_core ops wiring (health endpoint)
- `sum_core` is importable
- no references to `test_project` exist in the project tree

Run from a client project directory:

```bash
cd clients/acme-kitchens
sum check
```

### Boilerplate source resolution

`sum init` uses the canonical repo `/boilerplate/` if present (and valid). If not, it falls back to a boilerplate copy bundled with the CLI package.

You can override the boilerplate path for development:

```bash
SUM_BOILERPLATE_PATH=/path/to/boilerplate sum init acme-kitchens
```


```

```markdown
## **[M5-003]: Implement CLI v1 (`sum init`, `sum check`) using boilerplate — Follow-up Report**

### Summary

Implemented the v1 SUM CLI with exactly two commands:

- **`sum init <project-name>`**: deterministic client scaffolding by copying the canonical boilerplate into `clients/<project-name>/` and applying safe, boring renames.
- **`sum check`**: structural validation for a client project with clear pass/fail output and exit codes (no stack traces on expected failures).

This work keeps the CLI strictly **filesystem + validation** as required: no venv creation, no dependency installation, no git init, no DB touches.

---

### Key decisions (explicitly allowed by spec)

#### 1) Project name rules + normalization

- **Accepted input**: lowercase letters, digits, hyphens; must start with a letter.
  - Regex: `^[a-z][a-z0-9-]*$`
- **Python package name**: hyphens are converted to underscores for importability.
  - Example: `acme-kitchens` → `acme_kitchens`

This aligns the CLI with the platform’s documented “project slug” expectations while still producing a valid Django project package.

#### 2) Boilerplate resolution (canonical-first, works outside monorepo)

`sum init` selects boilerplate source in this order:

1. `SUM_BOILERPLATE_PATH` (explicit override)
2. `./boilerplate/` when run from a repo root containing a valid boilerplate (canonical source)
3. packaged boilerplate bundled inside the CLI distribution (so the CLI works outside the monorepo)

#### 3) Making `sum init` projects pass `sum check`

To satisfy the milestone acceptance criteria (“`sum init foo` … passes `sum check`”) while still keeping `sum init` deterministic, `sum init` **copies `.env.example` to `.env`** (no secret generation, no “magic”).

---

### Implementation details

#### CLI structure

- Implemented as a dedicated installable package under `cli/`:
  - `cli/pyproject.toml` defines the `sum` console script and bundles boilerplate as package data.
  - Commands are implemented with Python’s built-in `argparse` (no extra runtime dependencies).

#### `sum init`

Behaviour:

- Copies boilerplate → `clients/<project-slug>/`
- Renames the internal Django project package:
  - `project_name/` → `<python_package>/`
- Replaces all `project_name` placeholders in file contents (including dotfiles)
- Creates `.env` from `.env.example` (deterministic copy)
- Refuses to overwrite existing target directory
- Fails loudly on invalid project names or malformed boilerplate

#### `sum check`

Checks implemented (minimum set from the milestone spec):

- **Required env vars present**: reads required keys from `.env.example` assignments and verifies they are provided by `.env` and/or the process environment.
- **Settings module importable**: inferred from `.env` or `manage.py` and imported safely.
- **`/health/` wiring**: verifies URLConf includes `sum_core.ops.urls`.
- **`sum_core` importable**
- **No `test_project` references**: scans common project text files for `test_project`.

Output:

- Human-readable checklist: `[OK]` / `[FAIL]` lines with short details
- Exit code `0` if all pass, `1` otherwise

---

### Documentation added

Created `docs/dev/cli.md` documenting:

- installation for monorepo development (`pip install -e ./cli`)
- command usage for `sum init` and `sum check`
- boilerplate source resolution rules

---

### Tests

Added pytest coverage under `cli/tests/` (kept separate from the Django-heavy `tests/` tree):

- Unit test: project name validation + normalization
- Integration-style test:
  - create temp workspace
  - run `sum init acme-kitchens`
  - run `sum check` in the created project
- Negative test: `sum check` fails on missing required env vars

Repo wiring update:

- Root `pyproject.toml` updated to include `cli/tests` in pytest discovery and add `cli` to `pythonpath`.

Test run performed (in repo `.venv`):

- `python -m pytest cli/tests -q`

---

### Files changed / added

- **CLI package**
  - `cli/pyproject.toml`
  - `cli/sum_cli/__main__.py`
  - `cli/sum_cli/cli.py`
  - `cli/sum_cli/util.py`
  - `cli/sum_cli/commands/init.py`
  - `cli/sum_cli/commands/check.py`
  - `cli/sum_cli/boilerplate/**` (bundled boilerplate copy for non-monorepo usage)

- **Tests**
  - `cli/tests/test_cli_init_and_check.py`

- **Repo test config**
  - `pyproject.toml` (added `cli/tests` + `cli` pythonpath)

- **Docs**
  - `docs/dev/cli.md`

---

### Notes / follow-ups (not implemented here)

- **Future optional path argument**: SSOT mentions `sum check <project-path>`, but M5-003 locked scope is `sum check` with no args. Implementation is structured so an optional `--path` / positional can be added later without redesign.
- **Boilerplate sync**: the CLI bundles a boilerplate copy to work outside the monorepo. In practice, release automation should ensure this packaged boilerplate stays in sync with the canonical `/boilerplate/`.


```

### What I implemented (M5-003)
- **CLI v1 with only two commands**: `sum init <project-name>` and `sum check`
- **Deterministic scaffolding** (`sum init`):
  - Copies boilerplate to `clients/<project-name>/`
  - Renames `project_name/` → `<python_package>/` (hyphens normalized to underscores, e.g. `acme-kitchens` → `acme_kitchens`)
  - Replaces all `project_name` placeholders in file contents (including dotfiles)
  - Creates `.env` by copying `.env.example` (no secret generation)
  - Refuses to overwrite existing targets; fails loudly on malformed boilerplate
- **Validation** (`sum check`): prints a clear checklist and exits `0/1` (no stack traces on expected failures)
  - Required env keys from `.env.example` are present via `.env` and/or process env
  - Settings module inferred from `.env` or `manage.py` and importable
  - URLConf contains `sum_core.ops.urls` wiring (health endpoint)
  - `sum_core` importable
  - No `test_project` references in the project tree

### Where it lives
- **Installable CLI package**: `cli/pyproject.toml` (console script `sum = sum_cli.__main__:main`)
- **CLI implementation**: `cli/sum_cli/`
- **Bundled boilerplate for non-monorepo usage**: `cli/sum_cli/boilerplate/**` (canonical `/boilerplate/` is still preferred when present)
- **Docs**: `docs/dev/cli.md`
- **Tests**: `cli/tests/test_cli_init_and_check.py`
- **Pytest discovery updated**: root `pyproject.toml` now includes `cli/tests`

### Testing
- Ran (in repo `.venv`): `python -m pytest cli/tests -q`

### Work report
- Filed as requested at: `docs/dev/M5/M5-003_followup.md`

---

**User**

@bash (46-51) Please correct 

---

**Cursor**

I’ll fix the Ruff UP007 warning by replacing the `typing.Union[...]` alias in `cli/sum_cli/commands/init.py` with the modern `X | Y` union syntax (Python 3.12), then re-run `ruff check` on the file to confirm it’s clean.

```python
from __future__ import annotations

import importlib.resources
import importlib.resources.abc
import os
import shutil
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


def run_init(project_name: str) -> int:
    try:
        naming = validate_project_name(project_name)
    except ValueError as e:
        print(f"[FAIL] {e}")
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
    except Exception as e:
        print(f"[FAIL] Project created but failed to finalize rename/replace: {e}")
        print(f"       You may need to delete: {target_dir}")
        return 1

    print("[OK] Project created.")
    print(f"     Location: {target_dir}")
    print("")
    print("Next steps:")
    print(f"  cd {target_dir}")
    print("  # create/activate your venv, install requirements.txt, then:")
    print("  sum check")
    return 0

```

### Fix applied
- **Updated** `cli/sum_cli/commands/init.py` to replace `Union[...]` with modern `X | Y` union typing (Ruff **UP007**).

### Verification
- Ran `ruff check cli/sum_cli/commands/init.py` in `.venv` → **All checks passed**.

