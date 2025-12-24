# M3-003 requirements and implementation
_Exported on 12/12/2025 at 14:01:26 GMT from Cursor (2.1.50)_

---

**User**

Please review the requirements in @docs/dev/M3/M3-003.md and carefully implement.

---

**Cursor**

Got it. I’ll (1) inspect the current `HomePage` model + existing tests, (2) implement **root-only creation** via `can_create_at` (or Wagtail equivalent already used here) and **true single-homepage enforcement** in `clean()`, then (3) add the two negative tests and run the test suite to confirm everything passes.

Nice — `HomePage` already has a `clean()` override, but it’s currently relying on `Site.root_page` logic (which doesn’t truly enforce “only one HomePage exists”). Next I’ll inspect the existing homepage tests and then swap `clean()` to the explicit queryset check + add the root-only `can_create_at` enforcement.

Aha: tests already cover a “clean() doesn’t raise” case, but nothing yet asserts the **two new negative guarantees** (non-root creation denied, second HomePage forbidden). Next I’ll find any existing `can_create_at` patterns in this repo, then implement the model change + update/extend tests accordingly.

I’ve found there aren’t any existing `can_create_at` implementations elsewhere in this repo, so we’ll define it directly on `HomePage` using Wagtail’s standard hook: **allow creation only when `parent.is_root()`**. Next I’ll update `HomePage.clean()` to the explicit “any other HomePage exists” constraint, then extend `tests/pages/test_home_page.py` with the two negative tests from the spec.

```python
"""
Name: Test Project Home Page Models
Path: core/sum_core/test_project/home/models.py
Purpose: Provide a HomePage type with StreamField body, SEO fields, and one-per-site enforcement.
Family: Used only by sum_core.test_project; client projects will define their own page types later.
Dependencies: Wagtail Page model, sum_core.pages.mixins, sum_core.blocks.base.PageStreamBlock, sum_core base template.
"""
from __future__ import annotations

from django.core.exceptions import ValidationError
from sum_core.blocks import PageStreamBlock
from sum_core.pages.mixins import BreadcrumbMixin, OpenGraphMixin, SeoFieldsMixin
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page


class HomePage(SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin, Page):
    """
    Homepage for the test project with StreamField body, SEO fields, and one-per-site enforcement.

    Satisfies US-P01 Homepage acceptance criteria:
    - StreamField body accepting all homepage blocks (PageStreamBlock)
    - SEO fields (meta title, meta description) via SeoFieldsMixin
    - Open Graph image via OpenGraphMixin
    - Only one HomePage allowed per site (enforced via clean method)
    """

    intro: RichTextField = RichTextField(blank=True)
    body: StreamField = StreamField(
        PageStreamBlock(),
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Add content blocks to build your homepage layout.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    promote_panels = (
        SeoFieldsMixin.seo_panels
        + OpenGraphMixin.open_graph_panels
        + Page.promote_panels
    )

    # HomePage can only be created under the root page
    parent_page_types: list[str] = ["wagtailcore.Page"]

    # HomePage can have child pages (e.g., StandardPage)
    subpage_types: list[str] = ["wagtailcore.Page"]

    template: str = "sum_core/home_page.html"

    class Meta:
        verbose_name = "Home Page"
        verbose_name_plural = "Home Pages"

    @classmethod
    def can_create_at(cls, parent: Page) -> bool:
        """
        Enforce root-only creation for HomePage.

        This is used by Wagtail admin UI, but also helps prevent programmatic
        misuse when callers respect the standard Wagtail create APIs.
        """
        return parent.is_root() and super().can_create_at(parent)

    def clean(self) -> None:
        """
        Validate that only one HomePage exists.

        This rule is enforced at the model layer so programmatic creation can't
        bypass it.
        """
        super().clean()

        if HomePage.objects.exclude(pk=self.pk).exists():
            raise ValidationError({"title": "Only one HomePage is allowed per site."})

    @property
    def has_hero_block(self) -> bool:
        """Check if the StreamField body contains any hero blocks."""
        if not self.body:
            return False

        # Check against the block names defined in PageStreamBlock
        hero_block_types = ["hero_image", "hero_gradient", "hero"]

        # StreamField iteration yields blocks that behave like bound blocks
        for block in self.body:
            if block.block_type in hero_block_types:
                return True
        return False

```

```python
"""
Name: Home Page Tests
Path: tests/pages/test_home_page.py
Purpose: Validate the test project's HomePage type and its integration with the SUM base template.
Family: Part of the page-level test suite exercising the design system.
Dependencies: Wagtail Site & Page models, home.HomePage, sum_core templates.
"""
from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError
from django.template import RequestContext, Template
from django.test import RequestFactory
from home.models import HomePage
from sum_core.blocks import PageStreamBlock
from wagtail.models import Page, Site

pytestmark = pytest.mark.django_db


def test_home_page_can_be_created_under_root() -> None:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Test Home", slug="test-home")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    assert HomePage.objects.filter(title="Test Home").exists()


def test_home_page_can_only_be_created_under_root() -> None:
    root = Page.get_first_root_node()
    non_root_parent = Page(title="Non-root Parent", slug="non-root-parent")
    root.add_child(instance=non_root_parent)

    assert HomePage.can_create_at(root) is True
    assert HomePage.can_create_at(non_root_parent) is False


def test_home_page_cannot_create_second_homepage() -> None:
    root = Page.get_first_root_node()

    first = HomePage(title="Home 1", slug="home-1")
    root.add_child(instance=first)

    second = HomePage(title="Home 2", slug="home-2")
    with pytest.raises(ValidationError) as excinfo:
        root.add_child(instance=second)

    assert "Only one HomePage is allowed" in str(excinfo.value)


def test_home_page_template_uses_sum_core_base() -> None:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Test Home", slug="test-home-template")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    template = Template(
        "{% extends 'sum_core/home_page.html' %}"
        "{% block content %}<p>Content</p>{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": homepage}))

    assert "sum_core/css/main.css" in rendered
    assert "<header" in rendered
    assert "<footer" in rendered


def test_home_page_renders_streamfield_content() -> None:
    """Test that HomePage renders StreamField content below the hero section."""
    root = Page.get_first_root_node()

    # Create a PageStreamBlock with rich text content
    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python(
        [
            {
                "type": "rich_text",
                "value": "<h2>Test Heading</h2><p>This is test content with <strong>bold</strong> text.</p>",
            }
        ]
    )

    homepage = HomePage(
        title="Test Home with Content", slug="test-home-content", body=stream_data
    )
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    template = Template("{% extends 'sum_core/home_page.html' %}")
    rendered = template.render(RequestContext(request, {"page": homepage}))

    # Check that the page renders without errors
    assert rendered is not None

    # Check that StreamField content appears in the rendered output
    assert "Test Heading" in rendered
    assert "This is test content" in rendered
    assert "<strong>bold</strong>" in rendered

    # Check that the content is wrapped in the expected block structure
    # assert "section" in rendered  # RichText block might not have wrapper currently
    # assert "container" in rendered
    # assert "text-body" in rendered


def test_home_page_renders_service_cards() -> None:
    """Test that HomePage renders ServiceCardsBlock content."""
    root = Page.get_first_root_node()

    # Create a PageStreamBlock with service cards
    stream_block = PageStreamBlock()

    # Minimal valid data for service_cards
    service_card_data = {
        "eyebrow": "Our Services",
        "heading": "Comprehensive Solutions",
        "intro": "We do everything.",
        "cards": [
            {
                "title": "Service 1",
                "description": "Description 1",
                "link_url": "https://example.com/1",
                "link_label": "Go to 1",
            },
            {
                "title": "Service 2",
                "description": "Description 2",
            },
            {
                "title": "Service 3",
                "description": "Description 3",
            },
        ],
        "layout_style": "default",
    }

    stream_data = stream_block.to_python(
        [
            {
                "type": "service_cards",
                "value": service_card_data,
            }
        ]
    )

    homepage = HomePage(
        title="Test Home with Services", slug="test-home-services", body=stream_data
    )
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    template = Template("{% extends 'sum_core/home_page.html' %}")
    rendered = template.render(RequestContext(request, {"page": homepage}))

    # Check content
    assert "Comprehensive Solutions" in rendered
    assert "Our Services" in rendered
    assert "Service 1" in rendered
    assert "services__grid" in rendered
    assert "services__card" in rendered
    assert "btn--link" in rendered


def test_home_page_clean_validates_when_root_page() -> None:
    """Test that HomePage.clean() validates correctly when it's a root_page."""
    root = Page.get_first_root_node()

    # Create HomePage and set it as root_page
    homepage = HomePage(title="Root Home", slug="root-home")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    # Refresh and validate - should not raise
    homepage.refresh_from_db()
    homepage.clean()  # Should not raise ValidationError

    # Verify it's the root_page
    assert Site.objects.get(is_default_site=True).root_page == homepage


def test_home_page_has_seo_fields() -> None:
    """Test that HomePage has SEO fields from mixins."""
    root = Page.get_first_root_node()
    homepage = HomePage(
        title="SEO Test Home",
        slug="seo-test-home",
        meta_title="Custom Meta Title",
        meta_description="Custom meta description for testing.",
    )
    root.add_child(instance=homepage)

    assert homepage.meta_title == "Custom Meta Title"
    assert homepage.meta_description == "Custom meta description for testing."


def test_home_page_has_promote_panels() -> None:
    """Test that HomePage has promote_panels with SEO/OG fields."""
    # Verify promote_panels attribute exists and includes SEO/OG panels
    assert hasattr(HomePage, "promote_panels"), "HomePage should have promote_panels"
    assert len(HomePage.promote_panels) > 0, "promote_panels should not be empty"

    # Check that SEO fields are accessible
    root = Page.get_first_root_node()
    homepage = HomePage(
        title="Promote Test",
        slug="promote-test",
        meta_title="Test Meta Title",
        meta_description="Test description",
    )
    root.add_child(instance=homepage)

    assert homepage.meta_title == "Test Meta Title"
    assert homepage.meta_description == "Test description"

```

Good — model enforcement is now in place, and tests now explicitly cover the two new guarantees: **root-only creation** and **rejecting a second HomePage**. Next I’ll run lints for the touched files and execute the test suite to confirm everything passes end-to-end.

---

**User**

I just tried to load the page in browser and get the following:



ProgrammingError at /



column home_homepage.meta_title does not exist

LINE 1: ...ge"."alias_of_id", "home_homepage"."page_ptr_id", "home_home...

                                                             ^

Request Method:	GET

Request URL:	http://127.0.0.1:8000/

Django Version:	5.2.9

Exception Type:	ProgrammingError

Exception Value:

column home_homepage.meta_title does not exist

LINE 1: ...ge"."alias_of_id", "home_homepage"."page_ptr_id", "home_home...

                                                             ^

Exception Location:	/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/psycopg/cursor.py, line 117, in execute

Raised during:	wagtail.views.serve

Python Executable:	/home/mark/workspaces/tradesite/.venv/bin/python

Python Version:	3.12.3

Python Path:

['/home/mark/workspaces/tradesite/core/sum_core/test_project',

 '/usr/lib/python312.zip',

 '/usr/lib/python3.12',

 '/usr/lib/python3.12/lib-dynload',

 '/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages',

 '__editable__.sum_core-0.1.0.finder.__path_hook__']

Server time:	Fri, 12 Dec 2025 13:48:45 +0000

Traceback Switch to copy-and-paste view

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/db/backends/utils.py, line 105, in _execute

                return self.cursor.execute(sql, params)

                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/psycopg/cursor.py, line 117, in execute

            raise ex.with_traceback(None)

                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

The above exception (column home_homepage.meta_title does not exist LINE 1: ...ge"."alias_of_id", "home_homepage"."page_ptr_id", "home_home... ^) was the direct cause of the following exception:

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/core/handlers/exception.py, line 55, in inner

                response = get_response(request)

                               ^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/core/handlers/base.py, line 197, in _get_response

                response = wrapped_callback(request, *callback_args, **callback_kwargs)

                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/views.py, line 17, in serve

    route_result = Page.route_for_request(request, path)

                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/models/pages.py, line 496, in route_for_request

                        site.root_page.localized.specific.route(

                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/utils/functional.py, line 47, in __get__

        res = instance.__dict__[self.name] = self.func(instance)

                                                 ^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/models/specific.py, line 93, in specific

        return self.get_specific()

                   ^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/wagtail/models/specific.py, line 73, in get_specific

            specific_obj = model_class._default_manager.get(id=self.id)

                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/db/models/manager.py, line 87, in manager_method

                return getattr(self.get_queryset(), name)(*args, **kwargs)

                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/db/models/query.py, line 631, in get

        num = len(clone)

                   ^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/db/models/query.py, line 368, in __len__

        self._fetch_all()

             ^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/db/models/query.py, line 1954, in _fetch_all

            self._result_cache = list(self._iterable_class(self))

                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/db/models/query.py, line 93, in __iter__

        results = compiler.execute_sql(

                       …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/db/models/sql/compiler.py, line 1623, in execute_sql

            cursor.execute(sql, params)

                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/db/backends/utils.py, line 122, in execute

            return super().execute(sql, params)

                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/db/backends/utils.py, line 79, in execute

        return self._execute_with_wrappers(

                    …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/db/backends/utils.py, line 92, in _execute_with_wrappers

        return executor(sql, params, many, context)

                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/db/backends/utils.py, line 100, in _execute

        with self.db.wrap_database_errors:

             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/db/utils.py, line 91, in __exit__

                raise dj_exc_value.with_traceback(traceback) from exc_value

                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/django/db/backends/utils.py, line 105, in _execute

                return self.cursor.execute(sql, params)

                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars

/home/mark/workspaces/tradesite/.venv/lib/python3.12/site-packages/psycopg/cursor.py, line 117, in execute

            raise ex.with_traceback(None)

                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ …

Local vars



Please analyse the issue and implement a solution.

---

**Cursor**

This error is almost always a **migration/schema mismatch**: the Django model now has `meta_title` (via `SeoFieldsMixin`), but your database table `home_homepage` was created before that field existed (or migrations weren’t run/applied). Next I’ll inspect the `home` app migrations + the SEO mixin fields, then add/adjust migrations so the DB schema matches the model.

Nice: the repo already contains a migration (`home/migrations/0003_homepage_seo_fields.py`) that *adds* `meta_title`/`meta_description`/`og_image`. So your DB simply hasn’t applied it (or it was faked/ran against a different DB). Next I’ll check the Makefile/dev workflow and then add a small guard/command so applying migrations is harder to miss.

Good catch: the `home` app *does* ship the migration that adds `meta_title`, so the fix is to **apply migrations to your current DB**. I’ll do two things: (1) add a `make migrate` (and fix `make run` to use the correct `manage.py`) so this doesn’t bite again, and (2) run the migration locally in your `.venv` to confirm the homepage loads.

```makefile
.PHONY: help lint test format run migrate makemigrations install install-dev clean db-up db-down db-logs

MANAGE = python core/sum_core/test_project/manage.py

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install project dependencies
	pip install -e .

install-dev:
	pip install -U pip
	pip install -e ./core[dev]
	pre-commit install


lint: ## Run linting (ruff + mypy)
	ruff check .
	mypy . || true

test: ## Run tests with pytest
	python -m pytest

format: ## Format code with Black and isort
	black .
	isort .

run: ## Initial for local dev (may be wired to Docker later)
	$(MANAGE) migrate --noinput
	$(MANAGE) runserver

migrate: ## Apply database migrations for the test project
	$(MANAGE) migrate --noinput

makemigrations: ## Create new migrations for the test project
	$(MANAGE) makemigrations

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -r {} + 2>/dev/null || true
	rm -f .coverage .coverage.*

db-up: ## Start Postgres via Docker Compose
	docker-compose up -d db

db-down: ## Stop Postgres via Docker Compose
	docker-compose down

db-logs: ## Tail Postgres logs
	docker-compose logs -f db

```

```python
"""
Name: Pytest Django Configuration
Path: tests/conftest.py
Purpose: Configure Django/Wagtail settings and test database for pytest runs.
Family: Shared fixtures for the test suite.
Dependencies: Django test utilities, pytest.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Generator
from pathlib import Path

import django
import pytest
from django.test.utils import (
    setup_databases,
    setup_test_environment,
    teardown_databases,
    teardown_test_environment,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = ROOT_DIR / "core"
TEST_PROJECT_DIR = CORE_DIR / "sum_core" / "test_project"

if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

if str(TEST_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_PROJECT_DIR))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "sum_core.test_project.test_project.settings"
)
django.setup()


@pytest.fixture(scope="session", autouse=True)
def django_test_environment() -> Generator[None, None, None]:
    """Set up Django and the test database for the test session."""

    setup_test_environment()
    db_config = setup_databases(verbosity=0, interactive=False, keepdb=False)
    try:
        yield
    finally:
        teardown_databases(db_config, verbosity=0)
        teardown_test_environment()


@pytest.fixture()
def wagtail_default_site():
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
def _reset_homepage_between_tests() -> None:
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

    HomePage.objects.all().delete()
    Site.clear_site_root_paths_cache()

```

### What happened
- Your browser error (`column home_homepage.meta_title does not exist`) was caused by **pending migrations**: `home.0003_homepage_seo_fields` hadn’t been applied, so the DB table was missing `meta_title`.

### What I did
- **Applied the missing migrations** (confirmed `home.0003_homepage_seo_fields` was unapplied, then migrated). This fixes the runtime error.
- Added Makefile support so this is harder to miss:
  - **`make migrate`** runs `python core/sum_core/test_project/manage.py migrate --noinput`
  - **`make run`** now runs migrations first and uses the correct `manage.py` path.
- Fixed the test suite fallout from the new “single HomePage” rule:
  - Your test DB is **session-scoped**, so a HomePage created in one test persisted into later tests and caused failures.
  - I added an **autouse fixture** in `tests/conftest.py` that deletes `HomePage` rows between tests and resets any `Site.root_page` pointing at them.

### What you should do now
- Restart your devserver and reload `/` — the `meta_title` column issue should be gone.
- Going forward, use:

```bash
make migrate
make run
```

```shellscript
make migrate
make run
```
