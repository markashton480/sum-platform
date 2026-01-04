"""
Name: Seed Orchestrator Tests
Path: tests/seeders/test_orchestrator.py
Purpose: Verify orchestration planning and dry-run behavior.
"""

from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path
from typing import Any

import pytest

import seeders.orchestrator as orchestrator_module
from seeders.base import BaseSeeder
from seeders.exceptions import SeederNotFoundError

SeedOrchestrator = orchestrator_module.SeedOrchestrator
SeedPlan = orchestrator_module.SeedPlan


class DummyImageManager:
    def __init__(self, events: list[str] | None = None) -> None:
        self.events = events

    def generate_manifest(self, manifest: Any) -> dict[str, Any]:
        if self.events is not None:
            self.events.append("images")
        return {"TEST_IMAGE": object()}


class HomeSeeder(BaseSeeder):
    def seed(self, content: dict[str, Any], clear: bool = False) -> None:
        self.pages = {"home": "home"}

    def clear(self) -> None:
        pass


class AboutSeeder(BaseSeeder):
    def seed(self, content: dict[str, Any], clear: bool = False) -> None:
        self.pages = {"about": "about"}

    def clear(self) -> None:
        pass


def _write_profile(
    content_dir: Path,
    *,
    profile: str = "demo",
    pages: tuple[str, ...] = ("home", "about"),
) -> None:
    """Write a minimal profile directory to support seeding tests.

    Creates the expected profile structure:
    - ``<profile>/site.yaml``
    - ``<profile>/navigation.yaml``
    - ``<profile>/pages/*.yaml``
    """
    profile_dir = content_dir / profile
    pages_dir = profile_dir / "pages"
    pages_dir.mkdir(parents=True)

    (profile_dir / "site.yaml").write_text(
        'brand:\n  company_name: "Test Co"\n',
        encoding="utf-8",
    )
    (profile_dir / "navigation.yaml").write_text(
        "footer:\n  tagline: Test\n",
        encoding="utf-8",
    )
    for page in pages:
        title = page.replace("-", " ").title()
        (pages_dir / f"{page}.yaml").write_text(
            f'title: "{title}"\nslug: "{page}"\n',
            encoding="utf-8",
        )


def test_seed_orchestrator_plan_orders_seeders(tmp_path: Path) -> None:
    content_dir = tmp_path / "content"
    _write_profile(content_dir)

    orchestrator = SeedOrchestrator(
        content_dir=content_dir,
        image_manager=DummyImageManager(),
        image_manifest=[],
        page_seeder_classes={"about": AboutSeeder, "home": HomeSeeder},
    )

    plan = orchestrator.plan("demo")

    assert plan.seeders == ["home", "about"]
    assert plan.pages == ["home", "about"]


def test_seed_orchestrator_dry_run_returns_plan(tmp_path: Path) -> None:
    content_dir = tmp_path / "content"
    _write_profile(content_dir, pages=("home",))

    orchestrator = SeedOrchestrator(
        content_dir=content_dir,
        image_manager=DummyImageManager(),
        image_manifest=[],
        page_seeder_classes={"home": HomeSeeder},
    )

    plan = orchestrator.seed("demo", dry_run=True)

    assert isinstance(plan, SeedPlan)


def test_seed_orchestrator_list_profiles(tmp_path: Path) -> None:
    content_dir = tmp_path / "content"
    _write_profile(content_dir, profile="alpha")
    _write_profile(content_dir, profile="beta")

    orchestrator = SeedOrchestrator(
        content_dir=content_dir,
        image_manager=DummyImageManager(),
        image_manifest=[],
        page_seeder_classes={"home": HomeSeeder},
    )

    assert orchestrator.list_profiles() == ["alpha", "beta"]


def test_seed_orchestrator_plan_raises_when_no_seeders_registered(
    tmp_path: Path,
) -> None:
    content_dir = tmp_path / "content"
    _write_profile(content_dir)

    orchestrator = SeedOrchestrator(
        content_dir=content_dir,
        image_manager=DummyImageManager(),
        image_manifest=[],
        page_seeder_classes={},
    )

    with pytest.raises(SeederNotFoundError):
        orchestrator.plan("demo")


def test_seed_orchestrator_seed_calls_clear_then_seeds_pages_and_site(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    content_dir = tmp_path / "content"
    _write_profile(content_dir)

    # This is a unit test for orchestration flow. We stub out `transaction.atomic`
    # to avoid requiring a configured database/transaction backend here; rollback
    # behaviour is not exercised by this test.
    monkeypatch.setattr(
        orchestrator_module.transaction,
        "atomic",
        lambda *args, **kwargs: nullcontext(),
    )

    events: list[str] = []

    class RecordingSiteSeeder(BaseSeeder):
        def seed(self, content: dict[str, Any], clear: bool = False) -> None:
            events.append(f"seed:site:{clear}")
            assert content["profile"] == "demo"
            assert "pages" in content
            assert "images" in content

        def clear(self) -> None:
            events.append("clear:site")

    def make_page_seeder(name: str) -> type[BaseSeeder]:
        class RecordingPageSeeder(BaseSeeder):
            def seed(self, content: dict[str, Any], clear: bool = False) -> None:
                events.append(f"seed:{name}:{clear}")
                assert content["images"].get("TEST_IMAGE") is not None
                self.pages = {name: content["page_data"]["slug"]}

            def clear(self) -> None:
                events.append(f"clear:{name}")

        return RecordingPageSeeder

    orchestrator = SeedOrchestrator(
        content_dir=content_dir,
        image_manager=DummyImageManager(events=events),
        image_manifest=[{"key": "TEST_IMAGE", "width": 1, "height": 1}],
        page_seeder_classes={
            "about": make_page_seeder("about"),
            "home": make_page_seeder("home"),
        },
        site_seeder_class=RecordingSiteSeeder,
    )

    result = orchestrator.seed("demo", clear=True)

    assert result.profile == "demo"
    assert result.pages == {"home": "home", "about": "about"}
    assert events == [
        "images",
        "clear:site",
        "clear:about",
        "clear:home",
        "seed:home:False",
        "seed:about:False",
        "seed:site:False",
    ]
