from __future__ import annotations

from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from home.models import HomePage
from PIL import Image as PILImage
from sum_core.pages.models import StandardPage
from wagtail.images import get_image_model
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


@pytest.fixture
def image():
    image_model = get_image_model()

    # Generate valid 100x100 PNG
    f = BytesIO()
    img = PILImage.new("RGB", (100, 100), "white")
    img.save(f, "PNG")
    content = f.getvalue()

    return image_model.objects.create(
        title="Test Image",
        file=SimpleUploadedFile("test.png", content, content_type="image/png"),
    )


class TestThemeAFeaturedCaseStudyBlock:
    """Tests for FeaturedCaseStudyBlock rendering with Theme A."""

    def test_featured_case_study_rendering(self, client: Client, image) -> None:
        """Test that FeaturedCaseStudyBlock renders with Theme A classes and structure."""

        # Create a page
        root = Page.get_first_root_node()
        homepage = HomePage(title="Theme Test Home", slug="theme-home-fcs")
        root.add_child(instance=homepage)

        site = Site.objects.get(is_default_site=True)
        site.root_page = homepage
        site.save()
        Site.clear_site_root_paths_cache()

        # Create StandardPage with FeaturedCaseStudyBlock
        block_data = [
            (
                "featured_case_study",
                {
                    "eyebrow": "Project 001",
                    "heading": "Solar Installation",
                    "intro": "<p>A great project.</p>",
                    "points": ["Efficient", "Sustainable", "Cost-effective"],
                    "cta_text": "View Case Study",
                    "cta_url": "https://example.com/case-study",
                    "image": image,
                    "image_alt": "Solar panels on roof",
                    "stats_label": "Savings",
                    "stats_value": "£5,000",
                },
            )
        ]

        standard = StandardPage(title="FCS Test", slug="fcs-test", body=block_data)
        homepage.add_child(instance=standard)
        revision = standard.save_revision()
        try:
            revision.publish()
        except AttributeError:
            # handle older wagtail versions where save_revision returns a different object or publish method differs
            # but here we assume standard behavior. If strict check needed:
            pass

        response = client.get(standard.url)
        content = response.content.decode("utf-8")

        # Theme A specific checks
        assert "lg:grid-cols-2 gap-16" in content, "Missing Theme A grid layout"
        assert "aspect-[4/5]" in content, "Missing Theme A image aspect ratio"
        assert "Inspect Artifact" in content, "Missing hover overlay text"
        assert "bg-sage-terra" in content, "Missing Theme A color token"
        assert "Solar Installation" in content
        assert "£5,000" in content
        assert "Savings" in content
