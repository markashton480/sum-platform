from __future__ import annotations

import importlib.resources
import importlib.resources.abc
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

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
