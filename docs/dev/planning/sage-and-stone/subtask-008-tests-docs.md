# Subtask 008: Tests & Documentation

## Overview

Implement comprehensive test suite using Test-Driven Development (TDD) methodology and create user-facing documentation for the Sage & Stone seeder.

## Deliverables

1. **Unit Tests** — Test each seeding function in isolation
2. **Integration Tests** — Test full seed → verify workflow
3. **Idempotency Tests** — Verify safe re-runs
4. **CLI Integration Tests** — Test CLI v2.0.0 invocation
5. **User Documentation** — Usage guide and customization instructions
6. **Developer Documentation** — Extend/modify guide for future seeders

---

## TDD Approach

### Principle

Write tests FIRST, then implement functionality. Each subtask (1-7) should include:
- Unit tests for its functions
- Integration points with other subtasks
- Edge case handling

### Test Structure

```
tests/
├── management/
│   └── commands/
│       └── test_seed_sage_stone.py       # Main test suite
├── integration/
│   └── test_sage_stone_seeder.py         # Full integration tests
└── fixtures/
    └── sage_stone_expected.json          # Expected site structure
```

---

## Implementation

### 1. Unit Tests

Test each seeding function independently:

```python
# tests/management/commands/test_seed_sage_stone.py
import pytest
from django.core.management import call_command
from wagtail.models import Site, Page
from home.models import HomePage

class TestSiteSetup:
    """Tests for Subtask 1: Site & Root Setup"""

    @pytest.mark.django_db
    def test_setup_site_creates_site(self):
        """Should create Site with correct hostname and port."""
        call_command("seed_sage_stone", "--site-only")

        site = Site.objects.get(hostname="localhost", port=8000)
        assert site.site_name == "Sage & Stone"
        assert site.is_default_site is True

    @pytest.mark.django_db
    def test_setup_site_creates_homepage(self):
        """Should create HomePage as site root."""
        call_command("seed_sage_stone", "--site-only")

        site = Site.objects.get(hostname="localhost", port=8000)
        assert site.root_page.specific_class == HomePage
        assert site.root_page.slug == "home"
        assert site.root_page.title == "Sage & Stone"

    @pytest.mark.django_db
    def test_setup_site_idempotent(self):
        """Should be safe to run multiple times."""
        call_command("seed_sage_stone", "--site-only")
        call_command("seed_sage_stone", "--site-only")

        assert Site.objects.filter(hostname="localhost", port=8000).count() == 1
        assert HomePage.objects.filter(slug="home").count() == 1


class TestImageGeneration:
    """Tests for Subtask 2: Image Generation"""

    @pytest.mark.django_db
    def test_generates_all_images(self):
        """Should create all 35+ placeholder images."""
        from wagtail.images.models import Image

        call_command("seed_sage_stone", "--images-only")

        # All images prefixed with SS_
        images = Image.objects.filter(title__startswith="SS_")
        assert images.count() >= 35

    @pytest.mark.django_db
    def test_image_dimensions_correct(self):
        """Should match wireframe aspect ratios."""
        from wagtail.images.models import Image

        call_command("seed_sage_stone", "--images-only")

        hero_image = Image.objects.get(title="SS_hero_home")
        # Hero images are 1920x1080 (16:9)
        assert hero_image.width == 1920
        assert hero_image.height == 1080


class TestBranding:
    """Tests for Subtask 3: Branding Configuration"""

    @pytest.mark.django_db
    def test_creates_site_settings(self):
        """Should create SiteSettings with brand colors."""
        from sum_core.branding.models import SiteSettings

        call_command("seed_sage_stone")

        site = Site.objects.get(hostname="localhost", port=8000)
        settings = SiteSettings.for_site(site)

        assert settings.primary_color == "#1a1a1a"  # sage-black
        assert settings.company_name == "Sage & Stone"
        assert settings.established_year == 2005


class TestNavigation:
    """Tests for Subtask 4: Navigation Structure"""

    @pytest.mark.django_db
    def test_creates_header_navigation(self):
        """Should create 3-level mega menu."""
        from sum_core.navigation.models import HeaderNavigation

        call_command("seed_sage_stone")

        site = Site.objects.get(hostname="localhost", port=8000)
        header = HeaderNavigation.objects.get(site=site)

        # Top level menu items
        assert len(header.menu_items) >= 5  # Kitchens, About, Services, etc.

        # Check nested structure (Kitchens → Collections → The Heritage)
        kitchens_menu = next(
            item for item in header.menu_items
            if item.value.get('link_text') == 'Kitchens'
        )
        assert 'submenu_items' in kitchens_menu.value

    @pytest.mark.django_db
    def test_creates_footer_navigation(self):
        """Should create footer with link sections."""
        from sum_core.navigation.models import FooterNavigation

        call_command("seed_sage_stone")

        site = Site.objects.get(hostname="localhost", port=8000)
        footer = FooterNavigation.objects.get(site=site)

        assert len(footer.sections) >= 3  # Company, Legal, Contact


class TestCorePages:
    """Tests for Subtask 5: Core Pages"""

    @pytest.mark.django_db
    def test_creates_all_core_pages(self):
        """Should create About, Services, Portfolio, Contact pages."""
        from sum_core.pages.models import StandardPage

        call_command("seed_sage_stone")

        site = Site.objects.get(hostname="localhost", port=8000)
        home = site.root_page

        # All pages should be children of home
        children = home.get_children().live()
        slugs = [page.slug for page in children]

        assert "about" in slugs
        assert "services" in slugs
        assert "portfolio" in slugs
        assert "contact" in slugs

    @pytest.mark.django_db
    def test_pages_have_streamfield_content(self):
        """Pages should have populated StreamField blocks."""
        from sum_core.pages.models import StandardPage

        call_command("seed_sage_stone")

        about_page = StandardPage.objects.get(slug="about")

        # About page should have content blocks
        assert len(about_page.content) > 0
        # Should include specific block types from wireframe
        block_types = [block.block_type for block in about_page.content]
        assert "hero_gradient" in block_types or "hero_image" in block_types


class TestBlogContent:
    """Tests for Subtask 6: Blog Content"""

    @pytest.mark.django_db
    def test_creates_blog_categories(self):
        """Should create 3 categories."""
        from sum_core.blog.models import Category

        call_command("seed_sage_stone")

        categories = Category.objects.all()
        category_names = [cat.name for cat in categories]

        assert "Commission Stories" in category_names
        assert "Material Science" in category_names
        assert "The Workshop" in category_names

    @pytest.mark.django_db
    def test_creates_blog_posts(self):
        """Should create 7 blog articles."""
        from sum_core.pages.blog import BlogPostPage

        call_command("seed_sage_stone")

        posts = BlogPostPage.objects.live()
        assert posts.count() == 7

        # All posts should have categories
        for post in posts:
            assert post.category is not None


class TestLegalPages:
    """Tests for Subtask 7: Legal Pages"""

    @pytest.mark.django_db
    def test_creates_legal_pages(self):
        """Should create Terms, Privacy, Accessibility pages."""
        from sum_core.pages.models import LegalPage

        call_command("seed_sage_stone")

        legal_pages = LegalPage.objects.live()
        slugs = [page.slug for page in legal_pages]

        assert "terms-of-supply" in slugs
```

---

### 2. Integration Tests

Test full seeding workflow:

```python
# tests/integration/test_sage_stone_seeder.py
import pytest
from django.core.management import call_command
from wagtail.models import Site

@pytest.mark.django_db
class TestFullSeedWorkflow:
    """Integration tests for complete site seeding."""

    def test_full_seed_creates_complete_site(self):
        """Running seed_sage_stone should create fully functional site."""
        call_command("seed_sage_stone")

        # Verify site exists
        site = Site.objects.get(hostname="localhost", port=8000)
        assert site.site_name == "Sage & Stone"

        # Verify page tree
        home = site.root_page
        children = home.get_children().live()
        assert children.count() >= 7  # About, Services, Portfolio, Contact, Blog, etc.

        # Verify navigation
        from sum_core.navigation.models import HeaderNavigation, FooterNavigation
        assert HeaderNavigation.objects.filter(site=site).exists()
        assert FooterNavigation.objects.filter(site=site).exists()

        # Verify branding
        from sum_core.branding.models import SiteSettings
        settings = SiteSettings.for_site(site)
        assert settings.company_name == "Sage & Stone"

        # Verify images
        from wagtail.images.models import Image
        assert Image.objects.filter(title__startswith="SS_").count() >= 35

        # Verify blog
        from sum_core.blog.models import Category
        from sum_core.pages.blog import BlogPostPage
        assert Category.objects.count() >= 3
        assert BlogPostPage.objects.live().count() >= 7

    def test_idempotent_full_seed(self):
        """Should be safe to run seed multiple times."""
        call_command("seed_sage_stone")
        call_command("seed_sage_stone")

        # Should still have exactly one site
        assert Site.objects.filter(hostname="localhost", port=8000).count() == 1

        # Pages should be updated, not duplicated
        from home.models import HomePage
        assert HomePage.objects.filter(slug="home").count() == 1

    def test_clear_flag_removes_content(self):
        """--clear flag should remove existing Sage & Stone content."""
        call_command("seed_sage_stone")

        # Verify content exists
        site = Site.objects.get(hostname="localhost", port=8000)
        assert site is not None

        # Clear and verify removal
        call_command("seed_sage_stone", "--clear")

        # Site should be deleted
        assert not Site.objects.filter(hostname="localhost", port=8000).exists()

        # Can recreate cleanly
        call_command("seed_sage_stone")
        site = Site.objects.get(hostname="localhost", port=8000)
        assert site.site_name == "Sage & Stone"
```

---

### 3. CLI Integration Tests

Test CLI v2.0.0 invocation:

```python
# tests/integration/test_cli_v2_integration.py
import pytest
import subprocess

@pytest.mark.skipif(
    not shutil.which("sum"),
    reason="CLI v2 not installed"
)
class TestCLIv2Integration:
    """Tests for CLI v2.0.0 integration."""

    def test_cli_init_with_seed_flag(self, tmp_path):
        """sum init sage-and-stone --seed-site should invoke seeder."""
        # This test requires CLI v2 to be installed
        result = subprocess.run(
            ["sum", "init", "sage-and-stone", "--seed-site"],
            cwd=tmp_path,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "Sage & Stone site seeded successfully" in result.stdout
```

---

### 4. Regression Tests

Ensure existing functionality isn't broken:

```python
@pytest.mark.django_db
def test_seed_showroom_still_works():
    """seed_sage_stone should not break existing seed_showroom command."""
    # seed_showroom should still work
    call_command("seed_showroom")

    # Verify showroom site exists
    # (Assuming seed_showroom creates a site on port 8001 or different hostname)
    assert Site.objects.filter(site_name__icontains="showroom").exists()
```

---

## Documentation Deliverables

### 1. User Documentation

**File:** `docs/user/seed-sage-stone.md`

```markdown
# Sage & Stone Demo Site Seeder

Generate a complete demonstration website for "Sage & Stone," a fictional bespoke kitchen company.

## Quick Start

### Via CLI v2.0.0 (Recommended)

\`\`\`bash
sum init sage-and-stone --theme theme_a --seed-site
\`\`\`

### Via Management Command

\`\`\`bash
python manage.py seed_sage_stone
\`\`\`

## What Gets Created

- **7 Page Types:** Home, About, Services, Portfolio, Blog Index, Blog Posts (7), Legal Pages
- **Navigation:** 3-level mega menu, footer with sections
- **Branding:** Site settings, brand colors, typography
- **Content:** Realistic copy from wireframes, 7 blog articles
- **Images:** 35+ placeholder images in brand colors
- **Categories:** Blog categories for filtering

## Options

\`\`\`bash
# Clear existing Sage & Stone content first
python manage.py seed_sage_stone --clear

# Generate images only
python manage.py seed_sage_stone --images-only

# Generate content only (skip images)
python manage.py seed_sage_stone --content-only
\`\`\`

## Customization

### Change Site Details

Edit the seeder constants:

\`\`\`python
# home/management/commands/seed_sage_stone.py
HOSTNAME = "localhost"
PORT = 8000
SITE_NAME = "Sage & Stone"
\`\`\`

### Modify Content

All copy is extracted from wireframes. Edit the content dictionaries in the command file.

### Replace Images

Images are generated as placeholders. Replace with real images:

\`\`\`bash
# Images are stored with SS_ prefix
# Find and replace in Wagtail admin: /admin/images/
\`\`\`

## Idempotency

Safe to re-run. The seeder:
- Updates existing pages instead of creating duplicates
- Uses parent+slug lookups for Wagtail pages
- Uses get_or_create for settings/navigation

For structural changes (reordering, parent changes), use \`--clear\` first.

## Troubleshooting

### "Site already exists" error
\`\`\`bash
python manage.py seed_sage_stone --clear
python manage.py seed_sage_stone
\`\`\`

### Missing blocks error
Ensure Theme A is applied and all sum_core blocks are available.

### Image generation fails
Requires PIL/Pillow:
\`\`\`bash
pip install Pillow
\`\`\`

## See Also

- [Content Mapping](../dev/planning/sage-and-stone/content-mapping.md) — Detailed wireframe mapping
- [Work Order](../dev/planning/sage-and-stone/work-order.md) — Implementation plan
\`\`\`
```

---

### 2. Developer Documentation

**File:** `docs/dev/extending-seeders.md`

```markdown
# Extending Seeders

Guide for creating additional site seeders based on Sage & Stone patterns.

## Seeder Structure

All seeders should follow this pattern:

\`\`\`python
class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true')
        parser.add_argument('--images-only', action='store_true')
        parser.add_argument('--content-only', action='store_true')

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_existing_content()
            return

        # Images OUTSIDE transaction
        if not options['content_only']:
            self.create_images()

        # DB operations IN transaction
        if not options['images_only']:
            with transaction.atomic():
                self.setup_site()
                self.create_branding()
                self.create_navigation()
                self.create_pages()
                self.create_blog_content()
\`\`\`

## Idempotency Pattern

For Wagtail pages:

\`\`\`python
def _get_or_create_page(self, parent, slug, model, **kwargs):
    try:
        page = parent.get_children().type(model).get(slug=slug)
        # Update existing
        for key, value in kwargs.items():
            setattr(page, key, value)
        page.save_revision().publish()
        return page, False
    except model.DoesNotExist:
        # Create new
        page = model(slug=slug, **kwargs)
        parent.add_child(instance=page)
        page.save_revision().publish()
        return page, True
\`\`\`

## CLI v2 Integration

To integrate with CLI v2.0.0:

1. Add to CLI's seeder registry
2. Implement `--seed-site` flag handling
3. Coordinate with CLI orchestrator

See #210 for CLI v2 architecture.
\`\`\`
```

---

## Acceptance Criteria

- [ ] All unit tests written and passing (TDD approach)
- [ ] Integration tests verify full site creation
- [ ] Idempotency tests confirm safe re-runs
- [ ] CLI v2 integration tests pass (when CLI v2 available)
- [ ] Regression test confirms seed_showroom still works
- [ ] User documentation complete with examples
- [ ] Developer documentation explains extension patterns
- [ ] Test coverage >= 90%
- [ ] All tests run in CI/CD pipeline

---

## Dependencies

- All subtasks 1-7 completed
- pytest and pytest-django installed
- CLI v2.0.0 for CLI integration tests (#210, #190)

---

## Testing Strategy

1. **Unit tests written FIRST** for each subtask (TDD)
2. **Integration tests** after all subtasks complete
3. **Manual QA** with visual wireframe comparison
4. **Regression testing** for existing seeders
5. **CLI integration testing** once CLI v2 available

---

## Related Documentation

- [Work Order](./work-order.md) — Overall project plan
- [Subtask 1-7](./subtask-001-site-setup.md) — Implementation details
- [Content Mapping](./content-mapping.md) — Wireframe content
