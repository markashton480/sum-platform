import pytest
from django.test import Client
from home.models import HomePage
from sum_core.branding.models import SiteSettings
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page, Site


@pytest.mark.django_db
class TestSeoTags:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Setup site and home page
        self.root = Page.get_first_root_node()

        if not self.root:
            pass  # Should probably handle this, but let it fail if root is missing

        # Check for existing page with slug 'home' to avoid collision
        existing = self.root.get_children().filter(slug="home").first()
        if existing:
            if isinstance(existing.specific, HomePage):
                self.home = existing.specific
            else:
                existing.delete()
                self.home = None
        else:
            self.home = None

        if not self.home:
            self.home = HomePage(title="Home", slug="home", intro="Welcome")
            self.root.add_child(instance=self.home)

        self.site = Site.objects.first()
        if not self.site:
            self.site = Site.objects.create(
                hostname="localhost",
                root_page=self.home,
                is_default_site=True,
                site_name="Test Site",
            )
        else:
            self.site.root_page = self.home
            self.site.site_name = "Test Site"
            self.site.save()

        # Setup branding
        self.site_settings = SiteSettings.for_site(self.site)
        self.site_settings.company_name = "ACME Corp"
        self.site_settings.save()

        self.client = Client()

    def test_meta_defaults(self):
        """Test default meta title, description, and canonical."""
        response = self.client.get(self.home.url)
        content = response.content.decode()

        # Title: Page Title | Site Name
        assert "<title>Home | ACME Corp</title>" in content

        # Canonical
        expected_canonical = f"http://testserver{self.home.url}"
        # Note: client.get sets host to testserver usually
        # But wait, self.home.url is usually just path /.../ for root usually /
        # Canonical logic uses request.build_absolute_uri
        assert f'<link rel="canonical" href="{expected_canonical}">' in content

        # Robots default (index, follow implied or explicit)
        # My implementation outputs "index, follow"
        assert '<meta name="robots" content="index, follow">' in content

    def test_meta_overrides(self):
        """Test overriding meta title, description, and robots."""
        self.home.meta_title = "Custom SEO Title"
        self.home.meta_description = "A custom description."
        self.home.seo_noindex = True
        self.home.seo_nofollow = True
        self.home.save()

        response = self.client.get(self.home.url)
        content = response.content.decode()

        assert "<title>Custom SEO Title</title>" in content
        assert '<meta name="description" content="A custom description.">' in content
        assert '<meta name="robots" content="noindex, nofollow">' in content

    def test_og_defaults(self):
        """Test OG tags presence and defaults."""
        response = self.client.get(self.home.url)
        content = response.content.decode()

        assert '<meta property="og:title" content="Home | ACME Corp">' in content
        assert '<meta property="og:type" content="website">' in content
        assert '<meta property="og:url" content="http://testserver/">' in content
        assert '<meta property="og:site_name" content="Test Site">' in content
        # No image by default
        assert '<meta property="og:image"' not in content

    def test_og_overrides(self):
        """Test OG tags with explicit image and title."""
        # Create image
        image = Image.objects.create(title="OG Image", file=get_test_image_file())
        self.home.og_image = image
        self.home.save()

        response = self.client.get(self.home.url)
        content = response.content.decode()

        assert '<meta property="og:image"' in content
        # Check absolute URL
        # image.file.url is relative e.g. /media/...
        # absolute_url filter prepends request host
        expected_url = f"http://testserver{image.file.url}"
        assert expected_url in content

    def test_og_fallback_to_site_settings(self):
        """Test OG image fallback to site default."""
        image = Image.objects.create(title="Site OG", file=get_test_image_file())
        self.site_settings.og_default_image = image
        self.site_settings.save()

        response = self.client.get(self.home.url)
        content = response.content.decode()

        assert '<meta property="og:image"' in content
        expected_url = f"http://testserver{image.file.url}"
        assert expected_url in content

    def test_seo_title_fallback_logic(self):
        """Test fallback when seo_title (Wagtail default) is set but meta_title (Mixin) is not."""
        self.home.seo_title = "Wagtail SEO Title"
        self.home.meta_title = ""
        self.home.save()

        response = self.client.get(self.home.url)
        content = response.content.decode()

        # logic: if get_meta_title() -> returns self.meta_title or title|site
        # Wait, my Mixin `get_meta_title` implementation:
        # if self.meta_title: return ...
        # else: return "{self.title} | {site_name}"
        # It DOES NOT check `seo_title`!
        # This is a regression if we expect usage of Wagtail's native `seo_title`.
        # However, `SeoFieldsMixin` defines `meta_title`.
        # If I want to support Wagtail's `seo_title`, I should update the mixin or the tag.
        # My tag logic:
        # if hasattr(page, "get_meta_title") ... call it.
        # render_meta tag implementation:
        # if hasattr(page, "get_meta_title") and site_settings: meta_title = page.get_meta_title(site_settings)
        # So it uses the mixin helper.
        # The mixin helper `get_meta_title` (lines 53-70 of mixin.py)
        # if self.meta_title: return ...
        # return f"{self.title} | {site_name}"
        # It ignores `seo_title`.

        # Let's check requirements.
        # "AC2: default meta title = page title + site name (or equivalent) when page meta title is blank."
        # It doesn't explicitly mention `seo_title`.
        # But Wagtail pages have `seo_title` by default (on Promote tab).
        # Should we respect it?
        # A good implementation normally does.
        # I should probably update `SeoFieldsMixin.get_meta_title` to check `seo_title` if available.

        # I will update the test to expect this behavior (respect seo_title).
        # And then I will update the Mixin.

        assert "<title>Wagtail SEO Title</title>" in content
