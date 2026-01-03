"""
Name: Image Manager Tests
Path: tests/seeders/test_image_manager.py
Purpose: Verify placeholder image generation utilities.
"""

from __future__ import annotations

import pytest
from wagtail.images.models import Image
from wagtail.models import Site

from seeders.images import ImageManager, ImageSpec


@pytest.mark.django_db
def test_image_manager_generates_and_tracks(wagtail_default_site: Site) -> None:
    manager = ImageManager(prefix="TEST")

    image = manager.generate("SAMPLE", 320, 200, label="Sample")

    assert image.title == "TEST_SAMPLE"
    assert image.width == 320
    assert image.height == 200
    assert manager.get("SAMPLE") == image


@pytest.mark.django_db
def test_image_manager_idempotent(wagtail_default_site: Site) -> None:
    manager = ImageManager(prefix="TEST")

    first = manager.generate("SAMPLE", 320, 200)
    second = manager.generate("SAMPLE", 320, 200)

    assert first.pk == second.pk


@pytest.mark.django_db
def test_image_manager_manifest_generation(wagtail_default_site: Site) -> None:
    manager = ImageManager(prefix="TEST")

    manifest: list[ImageSpec] = [
        {"key": "ONE", "width": 120, "height": 90, "bg": "sage_black"},
        {"key": "TWO", "width": 140, "height": 100, "label": "Second"},
    ]

    images = manager.generate_manifest(manifest)

    assert set(images) == {"ONE", "TWO"}
    assert manager.get("ONE") == images["ONE"]
    assert Image.objects.filter(title="TEST_ONE").exists()
    assert Image.objects.filter(title="TEST_TWO").exists()
