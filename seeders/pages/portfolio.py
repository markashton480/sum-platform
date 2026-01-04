"""Portfolio page seeder."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from seeders.base import SeederRegistry
from seeders.pages.standard import StandardPageSeeder


@SeederRegistry.register("portfolio")
class PortfolioPageSeeder(StandardPageSeeder):
    """Seed the Portfolio page from YAML content."""

    def __init__(self, *, home_page: Any, images: Mapping[str, Any]) -> None:
        super().__init__(
            home_page=home_page,
            images=images,
            page_slug="portfolio",
            default_title="Portfolio",
            label="Portfolio",
        )
