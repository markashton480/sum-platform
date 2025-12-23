from __future__ import annotations

from io import BytesIO

import pytest
from bs4 import BeautifulSoup
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from home.models import HomePage
from PIL import Image as PILImage
from wagtail.images import get_image_model
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


@pytest.fixture
def logo_image():
    image_model = get_image_model()
    f = BytesIO()
    img = PILImage.new("RGB", (220, 220), "white")
    img.save(f, "PNG")
    content = f.getvalue()
    return image_model.objects.create(
        title="Sage & Stone",
        file=SimpleUploadedFile(
            "social-proof-logo.png", content, content_type="image/png"
        ),
    )


def _create_standard_page_with_social_proof_quote(
    slug: str,
    quote: str,
    logo=None,
    author: str = "",
    role: str = "",
    company: str = "",
) -> Page:
    from sum_core.pages.models import StandardPage

    root = Page.get_first_root_node()
    homepage = HomePage.objects.first()
    if homepage is None:
        homepage = HomePage(
            title="Theme Test Home", slug="theme-home-social-proof-quote"
        )
        root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    standard = StandardPage(title="Social Proof Quote Test", slug=slug)
    block_data = {"quote": quote}
    if logo is not None:
        block_data["logo"] = logo
    if author:
        block_data["author"] = author
    if role:
        block_data["role"] = role
    if company:
        block_data["company"] = company

    standard.body = [("social_proof_quote", block_data)]
    homepage.add_child(instance=standard)
    standard.save_revision().publish()
    return standard


class TestThemeASocialProofQuoteBlock:
    def test_social_proof_quote_renders_theme_template(
        self, client: Client, theme_active_copy, logo_image
    ) -> None:
        page = _create_standard_page_with_social_proof_quote(
            "social-proof-quote-theme-a",
            "Crafted precision.\nTrusted result.",
            logo_image,
            author="Ava Hill",
            role="Property Owner",
            company="Sage & Stone",
        )

        response = client.get(page.url)
        content = response.content.decode("utf-8")

        templates = getattr(response, "templates", [])
        template_names = [t.name for t in templates if hasattr(t, "name")]
        assert "sum_core/blocks/content_social_proof_quote.html" in template_names

        origin_paths = [
            str(getattr(template.origin, "name", ""))
            for template in templates
            if getattr(template, "name", None)
            == "sum_core/blocks/content_social_proof_quote.html"
        ]
        expected_fragments = (
            str(theme_active_copy),
            "themes/theme_a/templates",
        )
        assert any(
            any(fragment in path for fragment in expected_fragments)
            for path in origin_paths
        )
        assert "Crafted precision." in content
        assert "Ava Hill" in content
        assert "Property Owner" in content
        assert "Sage & Stone" in content
        assert "reveal" in content

        soup = BeautifulSoup(content, "html.parser")
        logo_img = soup.find("img", alt="Sage & Stone")
        assert logo_img is not None

    def test_social_proof_quote_optional_fields(self, client: Client) -> None:
        plain_page = _create_standard_page_with_social_proof_quote(
            "social-proof-quote-no-attribution",
            "Quiet confidence.",
        )
        plain_response = client.get(plain_page.url)
        plain_soup = BeautifulSoup(
            plain_response.content.decode("utf-8"), "html.parser"
        )
        assert plain_soup.find("figcaption") is None
        assert plain_soup.find("img") is None

        company_page = _create_standard_page_with_social_proof_quote(
            "social-proof-quote-company-only",
            "Measured cadence.",
            company="Arc Atelier",
        )
        company_response = client.get(company_page.url)
        company_soup = BeautifulSoup(
            company_response.content.decode("utf-8"), "html.parser"
        )
        caption = company_soup.find("figcaption")
        assert caption is not None
        assert "Arc Atelier" in caption.get_text()
        assert caption.find("cite") is None
