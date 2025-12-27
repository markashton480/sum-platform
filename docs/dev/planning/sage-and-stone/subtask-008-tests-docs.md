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

### 5. E2E Tests (Critical User Journeys)

Smoke tests to verify the generated site works for end users, not just database records.

**Purpose:** Validate integration between seeder, sum_core blocks, and Theme A. Ensure the demo site delivers on its promise: a working, navigable site out of the box.

**Tool:** Playwright (fast, reliable, multi-browser support)

**Scope:** 5-7 critical journeys that exercise integration points

**Run Frequency:**
- **Locally:** Optional (slow, ~2-3 minutes)
- **CI:** On PR to feature branch
- **Nightly:** Full suite with multiple browsers (Chrome, Firefox, Safari)

---

#### Test Structure

```
tests/
└── e2e/
    ├── conftest.py                    # Playwright fixtures
    ├── test_navigation.py             # Navigation journeys
    ├── test_blog.py                   # Blog filtering & reading
    ├── test_forms.py                  # Contact form submission
    └── test_mobile.py                 # Mobile-specific journeys
```

---

#### Journey 1: Mega Menu Navigation

```python
# tests/e2e/test_navigation.py
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_mega_menu_navigation_desktop(page: Page, live_server):
    """User can navigate through 3-level mega menu to nested pages."""
    page.goto(f"{live_server.url}")

    # Verify homepage loaded
    expect(page.locator("h1")).to_contain_text("Sage & Stone")

    # Hover over "Kitchens" to open mega menu
    kitchens_menu = page.locator("nav >> text=Kitchens")
    kitchens_menu.hover()

    # Mega menu should be visible
    mega_menu = page.locator(".mega-menu, .submenu")
    expect(mega_menu).to_be_visible()

    # Click "Collections" submenu
    collections = page.locator("text=Collections").first
    collections.click()

    # Sub-submenu should appear
    expect(page.locator("text=The Heritage")).to_be_visible()

    # Click "The Heritage" sub-submenu
    page.click("text=The Heritage")

    # Should navigate to collection detail page
    page.wait_for_url("**/collections/the-heritage/**")
    expect(page.locator("h1")).to_contain_text("The Heritage")

    # Page should have content (not empty)
    expect(page.locator("main")).not_to_be_empty()
```

---

#### Journey 2: Blog Category Filtering

```python
# tests/e2e/test_blog.py
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_blog_category_filtering(page: Page, live_server):
    """User can filter blog posts by category and read articles."""
    page.goto(f"{live_server.url}/blog/")

    # Verify blog index loaded
    expect(page.locator("h1")).to_contain_text("Blog")

    # Count total posts (should be 7)
    post_cards = page.locator(".blog-post-card, article.post")
    initial_count = post_cards.count()
    assert initial_count == 7, f"Expected 7 posts, found {initial_count}"

    # Click "Material Science" category filter
    material_science_filter = page.locator("text=Material Science").first
    material_science_filter.click()

    # Wait for filter to apply (URL should update or posts should filter)
    page.wait_for_timeout(500)

    # Should show fewer posts (only Material Science)
    filtered_count = post_cards.count()
    assert filtered_count < initial_count, "Filter didn't reduce post count"
    assert filtered_count > 0, "Filter removed all posts"

    # All visible posts should have Material Science category
    for i in range(filtered_count):
        post = post_cards.nth(i)
        expect(post.locator("text=Material Science")).to_be_visible()

    # Click first post to read
    first_post = post_cards.first
    first_post.click()

    # Should navigate to article detail page
    page.wait_for_url("**/blog/**")

    # Article should have content
    article_body = page.locator("article.blog-post, .article-content")
    expect(article_body).to_be_visible()
    expect(article_body).not_to_be_empty()

    # Should show category badge
    expect(page.locator("text=Material Science")).to_be_visible()
```

---

#### Journey 3: Contact Form Submission

```python
# tests/e2e/test_forms.py
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_contact_form_submission(page: Page, live_server):
    """User can submit contact form successfully."""
    page.goto(f"{live_server.url}/contact/")

    # Verify contact page loaded
    expect(page.locator("h1")).to_contain_text("Contact")

    # Fill form fields
    page.fill("input[name='name'], input[name='full_name']", "Test User")
    page.fill("input[name='email']", "test@example.com")
    page.fill("input[name='phone'], input[name='telephone']", "+44 1234 567890")
    page.fill("textarea[name='message']", "Test inquiry about bespoke kitchens.")

    # Submit form
    submit_button = page.locator("button[type='submit'], input[type='submit']")
    submit_button.click()

    # Should see success message (or redirect to thank you page)
    # Adjust selector based on actual implementation
    success_indicator = page.locator(
        "text=/thank you|success|received|we'll be in touch/i"
    )
    expect(success_indicator).to_be_visible(timeout=5000)

    # Alternative: Check for redirect to thank you page
    # page.wait_for_url("**/thank-you/**")
    # expect(page.locator("h1")).to_contain_text("Thank You")
```

---

#### Journey 4: Mobile Navigation Drill-Down

```python
# tests/e2e/test_mobile.py
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_mobile_navigation_drill_down(page: Page, live_server):
    """User can navigate 3-level menu on mobile (drill-down pattern)."""
    # Set mobile viewport
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(f"{live_server.url}")

    # Open mobile menu (hamburger icon)
    mobile_menu_toggle = page.locator(
        "button.mobile-menu-toggle, .hamburger, [aria-label='Menu']"
    )
    mobile_menu_toggle.click()

    # Mobile menu should be visible
    mobile_menu = page.locator(".mobile-menu, nav.mobile")
    expect(mobile_menu).to_be_visible()

    # Click "Kitchens" to drill into submenu
    kitchens = page.locator(".mobile-menu >> text=Kitchens")
    kitchens.click()

    # Should see submenu with back button
    back_button = page.locator("button.back, text=Back")
    expect(back_button).to_be_visible()

    # Should see "Collections" option
    collections = page.locator("text=Collections")
    expect(collections).to_be_visible()

    # Click "Collections" to drill deeper
    collections.click()

    # Should see sub-submenu
    heritage = page.locator("text=The Heritage")
    expect(heritage).to_be_visible()

    # Click "The Heritage" to navigate to page
    heritage.click()

    # Should navigate to collection page
    page.wait_for_url("**/collections/the-heritage/**")
    expect(page.locator("h1")).to_contain_text("The Heritage")
```

---

#### Journey 5: Portfolio Case Study Interaction

```python
# tests/e2e/test_portfolio.py
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_portfolio_case_study_viewing(page: Page, live_server):
    """User can view portfolio case studies."""
    page.goto(f"{live_server.url}/portfolio/")

    # Verify portfolio page loaded
    expect(page.locator("h1")).to_contain_text("Portfolio")

    # Should see portfolio items
    portfolio_items = page.locator(".portfolio-item, .case-study-card")
    expect(portfolio_items.first).to_be_visible()

    # Click first portfolio item
    portfolio_items.first.click()

    # Should open modal OR navigate to detail page
    # Check for modal first
    modal = page.locator(".modal, .case-study-modal, [role='dialog']")
    if modal.is_visible(timeout=1000):
        # Modal opened - verify content
        expect(modal).to_be_visible()

        # Should see case study details
        expect(modal.locator(".case-study-detail, .project-details")).to_be_visible()

        # Should see "brass plate" signature section (if implemented)
        # This is the unique Sage & Stone feature from wireframes
        signature = modal.locator("text=/Completed|Handcrafted by|GPS/i")
        # May not be implemented in all versions

        # Close modal
        close_button = modal.locator("button.close, [aria-label='Close']")
        close_button.click()
        expect(modal).not_to_be_visible()
    else:
        # Navigated to detail page
        page.wait_for_url("**/portfolio/**")
        expect(page.locator(".case-study-detail")).to_be_visible()
```

---

#### Journey 6: Legal Page Table of Contents

```python
# tests/e2e/test_legal.py
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_legal_page_toc_navigation(page: Page, live_server):
    """User can use ToC to navigate long legal page."""
    page.goto(f"{live_server.url}/terms-of-supply/")

    # Verify legal page loaded
    expect(page.locator("h1")).to_contain_text("Terms")

    # Table of Contents should be visible
    toc = page.locator(".table-of-contents, .toc, aside nav")
    expect(toc).to_be_visible()

    # Should have multiple sections listed
    toc_links = toc.locator("a")
    assert toc_links.count() >= 3, "ToC should have multiple sections"

    # Click a section link (e.g., "Payment Terms")
    payment_link = toc.locator("a >> text=/Payment/i").first
    payment_link.click()

    # Should scroll to section
    payment_section = page.locator("#payment-terms, h2:has-text('Payment')")
    expect(payment_section).to_be_in_viewport()

    # URL should update with anchor (if implemented)
    # expect(page.url).to_contain("#payment-terms")
```

---

#### Journey 7: Site Search (Optional)

```python
# tests/e2e/test_search.py
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
@pytest.mark.skipif("not FEATURE_SEARCH_ENABLED", reason="Search not implemented")
def test_site_search_functionality(page: Page, live_server):
    """User can search site content."""
    page.goto(f"{live_server.url}")

    # Open search (various implementations)
    search_toggle = page.locator(
        "button.search-toggle, [aria-label='Search'], .search-icon"
    )

    if search_toggle.is_visible(timeout=1000):
        search_toggle.click()

        # Search input should appear
        search_input = page.locator("input[type='search'], input[name='q']")
        expect(search_input).to_be_visible()

        # Enter query
        search_input.fill("oak")
        search_input.press("Enter")

        # Should navigate to results page or show results
        page.wait_for_url("**/search/**", timeout=3000)

        # Should see results
        results = page.locator(".search-results, .results")
        expect(results).to_be_visible()

        result_items = page.locator(".search-result, .result-item")
        assert result_items.count() > 0, "Search should return results for 'oak'"
```

---

#### E2E Test Configuration

```python
# tests/e2e/conftest.py
import pytest
from playwright.sync_api import sync_playwright
from django.core.management import call_command

@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Seed Sage & Stone site before E2E tests."""
    with django_db_blocker.unblock():
        # Clear and seed fresh site
        call_command("seed_sage_stone", "--clear")
        call_command("seed_sage_stone")

@pytest.fixture(scope="function")
def page(live_server):
    """Provide Playwright page for each test."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-GB"
        )
        page = context.new_page()

        yield page

        page.close()
        context.close()
        browser.close()
```

---

#### pytest.ini Configuration

```ini
[pytest]
markers =
    e2e: End-to-end tests using Playwright (slow, run separately)

# Run E2E tests separately
# pytest -m e2e
# pytest -m "not e2e"  # Skip E2E in fast test runs
```

---

#### CI/CD Integration

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  pull_request:
    branches: [feature/sage-stone-seeder]
  schedule:
    - cron: '0 2 * * *'  # Nightly at 2 AM

jobs:
  e2e:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install playwright pytest-playwright
          playwright install chromium

      - name: Run E2E tests
        run: |
          pytest -m e2e --video=retain-on-failure

      - name: Upload failure videos
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: e2e-videos
          path: test-results/
```

---

#### What E2E Tests DO NOT Cover

- ❌ **Pixel-perfect design** — Use visual regression testing for that
- ❌ **Every single page** — Only key representatives
- ❌ **All form validations** — Unit tests handle those
- ❌ **Every block type** — Theme A's responsibility
- ❌ **Performance** — Use separate load testing
- ❌ **Accessibility** — Use separate a11y testing (though Playwright can check basics)

---

#### Success Metrics

- [ ] All 7 E2E journeys pass on Chrome
- [ ] Mobile journeys pass on mobile viewport
- [ ] Tests run in under 3 minutes
- [ ] Failure videos help debug issues
- [ ] Tests catch integration bugs unit tests miss

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
- [ ] E2E tests pass for 7 critical user journeys
- [ ] E2E tests validate generated site works for end users
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
