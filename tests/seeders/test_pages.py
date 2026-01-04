"""
Name: Page Seeder Tests
Path: tests/seeders/test_pages.py
Purpose: Verify page seeders create/update pages from YAML content.
Family: Seeder architecture tests.
Dependencies: pytest, Wagtail models, seeders modules.
"""

from __future__ import annotations

from typing import Any

import pytest
from home.models import HomePage
from sum_core.pages.blog import BlogIndexPage, BlogPostPage, Category
from sum_core.pages.legal import LegalPage
from sum_core.pages.standard import StandardPage
from wagtail.models import Page, Site

from seeders.content import ContentLoader
from seeders.images import IMAGE_MANIFEST, ImageManager
from seeders.pages.about import AboutPageSeeder
from seeders.pages.blog import BlogSeeder
from seeders.pages.contact import ContactPageSeeder
from seeders.pages.home import HomePageSeeder
from seeders.pages.legal import LegalPageSeeder
from seeders.pages.portfolio import PortfolioPageSeeder
from seeders.pages.services import ServicesPageSeeder

pytestmark = [pytest.mark.django_db, pytest.mark.integration, pytest.mark.slow]


def _add_image_keys_to_set(data: Any, keys: set[str]) -> None:
    if isinstance(data, dict):
        for key, value in data.items():
            if key in {"image", "photo", "logo", "image_key"} and isinstance(
                value, str
            ):
                keys.add(value)
            else:
                _add_image_keys_to_set(value, keys)
    elif isinstance(data, list):
        for item in data:
            _add_image_keys_to_set(item, keys)


@pytest.fixture(scope="session")
def sage_stone_profile(repo_root) -> Any:
    loader = ContentLoader(content_dir=repo_root / "content")
    return loader.load_profile("sage-stone")


@pytest.fixture
def seeder_images(db, sage_stone_profile) -> dict[str, Any]:
    keys: set[str] = set()
    for page_content in sage_stone_profile.pages.values():
        _add_image_keys_to_set(page_content, keys)

    manifest = [spec for spec in IMAGE_MANIFEST if spec["key"] in keys]
    missing = keys - {spec["key"] for spec in manifest}
    assert not missing, f"Missing image specs for: {sorted(missing)}"

    manager = ImageManager(prefix="TEST")
    return manager.generate_manifest(manifest)


@pytest.fixture
def home_page(db, wagtail_default_site: Site) -> HomePage:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Home", slug="seed-home")
    root.add_child(instance=homepage)
    wagtail_default_site.root_page = homepage
    wagtail_default_site.save()
    return homepage


def test_home_page_seeder_creates_home_page(seeder_images, sage_stone_profile) -> None:
    root = Page.get_first_root_node()
    seeder = HomePageSeeder(root_page=root, images=seeder_images)
    seeder.seed(sage_stone_profile.pages["home"])

    page = HomePage.objects.get(slug="home")
    assert page.title == "Sage & Stone"
    assert page.seo_title == "Sage & Stone | Bespoke Kitchens, Herefordshire"
    block_types = [block.block_type for block in page.body]
    assert "hero_image" in block_types

    hero_block = next(block for block in page.body if block.block_type == "hero_image")
    assert hero_block.value["image"].pk == seeder_images["HERO_IMAGE"].pk


def test_about_page_seeder_creates_standard_page(
    home_page, seeder_images, sage_stone_profile
) -> None:
    seeder = AboutPageSeeder(home_page=home_page, images=seeder_images)
    seeder.seed(sage_stone_profile.pages["about"])

    page = StandardPage.objects.child_of(home_page).get(slug="about")
    block_types = [block.block_type for block in page.body]
    assert "team_members" in block_types

    featured = next(
        block for block in page.body if block.block_type == "featured_case_study"
    )
    assert featured.value["image"].pk == seeder_images["FOUNDER_IMAGE"].pk


def test_services_page_seeder_creates_standard_page(
    home_page, seeder_images, sage_stone_profile
) -> None:
    seeder = ServicesPageSeeder(home_page=home_page, images=seeder_images)
    seeder.seed(sage_stone_profile.pages["services"])

    page = StandardPage.objects.child_of(home_page).get(slug="services")
    block_types = [block.block_type for block in page.body]
    assert "trust_strip_logos" in block_types

    trust_block = next(
        block for block in page.body if block.block_type == "trust_strip_logos"
    )
    first_logo = trust_block.value["items"][0]["logo"]
    assert first_logo.pk == seeder_images["LOGO_GASSAFE"].pk


def test_portfolio_page_seeder_creates_standard_page(
    home_page, seeder_images, sage_stone_profile
) -> None:
    seeder = PortfolioPageSeeder(home_page=home_page, images=seeder_images)
    seeder.seed(sage_stone_profile.pages["portfolio"])

    page = StandardPage.objects.child_of(home_page).get(slug="portfolio")
    block_types = [block.block_type for block in page.body]
    assert "featured_case_study" in block_types

    featured = next(
        block for block in page.body if block.block_type == "featured_case_study"
    )
    assert featured.value["image"].pk == seeder_images["PORTFOLIO_HIGHLAND"].pk


def test_contact_page_seeder_creates_standard_page(
    home_page, seeder_images, sage_stone_profile
) -> None:
    seeder = ContactPageSeeder(home_page=home_page, images=seeder_images)
    seeder.seed(sage_stone_profile.pages["contact"])

    page = StandardPage.objects.child_of(home_page).get(slug="contact")
    block_types = [block.block_type for block in page.body]
    assert "contact_form" in block_types


def test_legal_page_seeder_creates_terms_privacy_accessibility(
    home_page, seeder_images, sage_stone_profile
) -> None:
    seeder = LegalPageSeeder(home_page=home_page, images=seeder_images)
    seeder.seed(sage_stone_profile.pages["legal"])

    terms = LegalPage.objects.child_of(home_page).get(slug="terms")
    section_types = [block.block_type for block in terms.sections]
    assert "section" in section_types

    privacy = StandardPage.objects.child_of(home_page).get(slug="privacy")
    accessibility = StandardPage.objects.child_of(home_page).get(slug="accessibility")
    assert privacy.body
    assert accessibility.body


def test_blog_seeder_creates_blog_index_categories_posts(
    home_page, seeder_images, sage_stone_profile
) -> None:
    seeder = BlogSeeder(home_page=home_page, images=seeder_images)
    seeder.seed(sage_stone_profile.pages["blog"])

    blog_index = BlogIndexPage.objects.child_of(home_page).get(slug="journal")
    assert blog_index.posts_per_page == 9
    categories = sage_stone_profile.pages["blog"]["categories"]
    assert Category.objects.count() == len(categories)

    post = BlogPostPage.objects.child_of(blog_index).get(slug="art-of-seasoning-timber")
    assert post.featured_image is not None
    assert post.featured_image.pk == seeder_images["BLOG_TIMBER_IMAGE"].pk

    image_block = next(
        block for block in post.body if block.block_type == "image_block"
    )
    assert image_block.value["image"].pk == seeder_images["BLOG_TIMBER_STACK"].pk
