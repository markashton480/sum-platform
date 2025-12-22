"""
Name: Pytest Django Configuration
Path: tests/conftest.py
Purpose: Configure Django/Wagtail settings and test database for pytest runs.
Family: Shared fixtures for the test suite.
Dependencies: Django test utilities, pytest.
"""

from __future__ import annotations

import logging
import re
import shutil
import sys
from importlib import metadata
from pathlib import Path

import pytest
from django.conf import settings
from django.template import engines

from tests.utils import REPO_ROOT, create_filesystem_sandbox, get_protected_paths
from tests.utils.safe_cleanup import safe_rmtree as safe_cleanup_rmtree

# Use centralized REPO_ROOT from tests.utils.fixtures
ROOT_DIR = REPO_ROOT
CORE_DIR = ROOT_DIR / "core"
TEST_PROJECT_DIR = CORE_DIR / "sum_core" / "test_project"

if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

if str(TEST_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_PROJECT_DIR))

logger = logging.getLogger(__name__)


def _resolve_sum_core_version() -> str | None:
    try:
        import sum_core

        version = getattr(sum_core, "__version__", None)
        if version:
            return str(version)
    except Exception:
        pass

    try:
        return metadata.version("sum-core")
    except metadata.PackageNotFoundError:
        return None
    except Exception:
        return None


def _parse_major_minor(version: str) -> tuple[int, int] | None:
    match = re.match(r"^(\d+)\.(\d+)", version)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def _sum_core_major_minor() -> tuple[int, int] | None:
    version = _resolve_sum_core_version()
    if not version:
        logger.warning(
            "sum_core version could not be determined; skipping version-based marker logic."
        )
        return None

    parsed = _parse_major_minor(version)
    if not parsed:
        logger.warning(
            "sum_core version %r could not be parsed; skipping version-based marker logic.",
            version,
        )
        return None

    return parsed


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    parsed_version = _sum_core_major_minor()
    if not parsed_version:
        return

    is_legacy_line = parsed_version < (0, 6)

    if is_legacy_line:
        skip_marker = pytest.mark.skip(
            reason="requires themes; skipped on sum_core < 0.6"
        )
        for item in items:
            if "requires_themes" in item.keywords:
                item.add_marker(skip_marker)
    else:
        skip_marker = pytest.mark.skip(reason="legacy-only; skipped on sum_core >= 0.6")
        for item in items:
            if "legacy_only" in item.keywords:
                item.add_marker(skip_marker)


def _reset_django_template_loaders() -> None:
    engine = engines["django"].engine
    loaders = getattr(engine, "template_loaders", [])
    for loader in loaders:
        reset = getattr(loader, "reset", None)
        if callable(reset):
            reset()


@pytest.fixture(scope="session")
def _session_media_root(tmp_path_factory) -> Path:
    return Path(tmp_path_factory.mktemp("django-media"))


@pytest.fixture(autouse=True)
def _isolate_django_media_root(_session_media_root: Path, settings) -> None:
    """
    Ensure tests never write uploaded/generated files into the repo.

    Wagtail image tests save uploaded images + renditions via Django's default
    storage (MEDIA_ROOT). If MEDIA_ROOT points at a path within the repo, test
    runs can produce untracked images that accidentally get committed.
    """
    settings.MEDIA_ROOT = str(_session_media_root)

    if hasattr(settings, "STORAGES") and "default" in settings.STORAGES:
        settings.STORAGES["default"] = {
            **settings.STORAGES["default"],
            "LOCATION": str(_session_media_root),
        }

    from django.core.files.storage import default_storage, storages
    from django.utils.functional import empty

    # Force default_storage + storages handler to re-read settings for this test.
    default_storage._wrapped = empty
    if hasattr(storages, "_storages"):
        storages._storages.clear()


@pytest.fixture()
def wagtail_default_site(db):
    """
    Return a deterministic default Wagtail Site for tests that use HTTP routing.

    Why: this repo's test DB is session-scoped (see `django_test_environment`),
    so other tests can mutate `Site` and Wagtail's internal site-root-path cache.
    Rendering tests that call `client.get(page.url)` should not depend on test order.
    """
    from wagtail.models import Page, Site

    # Ensure Wagtail's computed site root paths cache can't go stale across tests.
    Site.clear_site_root_paths_cache()

    root = Page.get_first_root_node()
    site = Site.objects.filter(is_default_site=True).first()

    if site is None:
        site = Site.objects.create(
            hostname="testserver",
            port=80,
            root_page=root,
            is_default_site=True,
        )
    else:
        changed = False
        if site.hostname != "testserver":
            site.hostname = "testserver"
            changed = True
        if site.port != 80:
            site.port = 80
            changed = True
        if site.root_page_id != root.id:
            site.root_page = root
            changed = True
        if not site.is_default_site:
            site.is_default_site = True
            changed = True
        if changed:
            site.save()

    Site.clear_site_root_paths_cache()
    return site


@pytest.fixture(autouse=True)
def _reset_homepage_between_tests(db) -> None:
    """
    Ensure HomePage tests remain isolated.

    The test DB is session-scoped (see `django_test_environment`), so without
    cleanup, a HomePage created in one test would prevent other tests from
    creating one because HomePage enforces a single-instance constraint.
    """
    from home.models import HomePage
    from wagtail.models import Page, Site

    # If any Site is currently pointing at a HomePage, reset it back to the root node
    # before deleting HomePages to avoid dangling references/caches.
    root = Page.get_first_root_node()
    for site in Site.objects.all():
        if HomePage.objects.filter(pk=site.root_page_id).exists():
            site.root_page = root
            site.save()

    for homepage in HomePage.objects.all():
        homepage.delete()
    Site.clear_site_root_paths_cache()


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Return resolved repository root Path (single source of truth).

    This fixture provides a consistent way to access the repo root across
    all test slices without duplicating path resolution logic.
    """
    return REPO_ROOT


@pytest.fixture(scope="session")
def protected_paths() -> tuple[str, ...]:
    """Return canonical list of protected repo directory names.

    These are directories that tests must never modify or delete.
    Useful for assertions in test teardowns or guardrail fixtures.
    """
    return get_protected_paths()


@pytest.fixture(scope="session")
def safe_rmtree(tmp_path_factory):
    """
    Guarded shutil.rmtree for tests.

    Refuse to delete:
    - any path containing .git
    - the repo root itself
    - any path outside pytest's temp root
    """
    tmp_root = Path(tmp_path_factory.getbasetemp()).resolve()
    repo_root = ROOT_DIR.resolve()

    def _safe_rmtree(path: Path) -> None:
        safe_cleanup_rmtree(path, repo_root=repo_root, tmp_base=tmp_root)

    return _safe_rmtree


@pytest.fixture
def filesystem_sandbox(request, tmp_path_factory):
    repo_root = ROOT_DIR.resolve()
    tmp_base = Path(tmp_path_factory.getbasetemp()).resolve()
    return create_filesystem_sandbox(repo_root, tmp_base, request)


@pytest.fixture(scope="module")
def theme_active_copy(tmp_path_factory, safe_rmtree):
    """Install Theme A templates into an isolated theme/active sandbox."""

    repo_root = ROOT_DIR.resolve()
    source_templates_dir = repo_root / "themes" / "theme_a" / "templates"

    if not source_templates_dir.exists():
        raise RuntimeError(
            f"Theme A templates not found at {source_templates_dir}."
            " The theme guardrails fixture requires canonical templates."
        )

    active_root_dir = Path(tmp_path_factory.mktemp("theme-active"))
    active_templates_dir = active_root_dir / "templates"
    active_templates_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_templates_dir, active_templates_dir, dirs_exist_ok=True)

    original_theme_templates_dir = Path(settings.THEME_TEMPLATES_DIR)
    original_theme_template_dirs = list(getattr(settings, "THEME_TEMPLATE_DIRS", []))
    original_template_dirs = list(settings.TEMPLATES[0]["DIRS"])

    normalized_theme_dirs = (
        [Path(entry) for entry in original_theme_template_dirs]
        if original_theme_template_dirs
        else [original_theme_templates_dir]
    )

    new_theme_dirs: list[Path] = [active_templates_dir]
    for directory in normalized_theme_dirs:
        if directory != active_templates_dir:
            new_theme_dirs.append(directory)

    settings.THEME_TEMPLATE_DIRS = new_theme_dirs
    settings.THEME_TEMPLATES_DIR = str(active_templates_dir)
    client_overrides_dir = Path(settings.CLIENT_OVERRIDES_DIR)
    settings.TEMPLATES[0]["DIRS"] = [*new_theme_dirs, client_overrides_dir]

    _reset_django_template_loaders()

    try:
        yield active_templates_dir
    finally:
        settings.THEME_TEMPLATE_DIRS = original_theme_template_dirs
        settings.THEME_TEMPLATES_DIR = str(original_theme_templates_dir)
        settings.TEMPLATES[0]["DIRS"] = original_template_dirs
        _reset_django_template_loaders()
        safe_rmtree(active_root_dir)


@pytest.fixture
def caplog_propagate(caplog):
    """
    Fixture returning a context manager that temporarily enables propagation
    for specified loggers.

    This is useful for testing logs in codebases that disable propagation
    to prevent double-logging (like this one).
    """
    import contextlib
    import logging

    @contextlib.contextmanager
    def _propagator(*logger_names: str):
        original_states = {}
        loggers = []
        for name in logger_names:
            logger = logging.getLogger(name)
            loggers.append(logger)
            original_states[name] = logger.propagate
            logger.propagate = True

        try:
            yield caplog
        finally:
            for logger in loggers:
                logger.propagate = original_states[logger.name]

    return _propagator
