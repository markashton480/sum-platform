from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from seeders.base import BaseSeeder, SeederRegistry, generate_slug, get_or_create_page
from seeders.exceptions import SeederRegistrationError


class DummyRevision:
    def __init__(self) -> None:
        self.published = False

    def publish(self) -> None:
        self.published = True


@dataclass
class DummyPage:
    slug: str
    title: str

    def __post_init__(self) -> None:
        self._revision = DummyRevision()
        self.saved = False

    def save_revision(self) -> DummyRevision:
        return self._revision

    def save(self) -> None:
        self.saved = True


class DummyChildren:
    def __init__(self, pages: list[DummyPage]) -> None:
        self._pages = pages

    def filter(self, slug: str) -> DummyChildren:
        return DummyChildren([page for page in self._pages if page.slug == slug])

    def first(self) -> DummyPage | None:
        return self._pages[0] if self._pages else None

    def __iter__(self):
        return iter(self._pages)


class DummyParent:
    def __init__(self) -> None:
        self.pages: list[DummyPage] = []

    def get_children(self) -> DummyChildren:
        return DummyChildren(self.pages)

    def add_child(self, *, instance: DummyPage) -> None:
        self.pages.append(instance)


class ExampleSeeder(BaseSeeder):
    def seed(self, content: dict[str, Any], clear: bool = False) -> None:
        if clear:
            self.clear()

    def clear(self) -> None:
        return None


def test_seeder_registry_registers_and_gets() -> None:
    SeederRegistry.clear()

    @SeederRegistry.register("example")
    class RegisteredSeeder(ExampleSeeder):
        pass

    assert SeederRegistry.get("example") is RegisteredSeeder


def test_seeder_registry_duplicate_registration_raises() -> None:
    SeederRegistry.clear()

    @SeederRegistry.register("duplicate")
    class DuplicateSeeder(ExampleSeeder):
        pass

    with pytest.raises(SeederRegistrationError):

        @SeederRegistry.register("duplicate")
        class DuplicateSeederTwo(ExampleSeeder):
            pass


def test_generate_slug_falls_back_when_empty() -> None:
    assert generate_slug("Hello World") == "hello-world"
    assert generate_slug("!!!", fallback="Fallback Name") == "fallback-name"


def test_get_or_create_page_creates_and_updates() -> None:
    parent = DummyParent()

    page, created = get_or_create_page(
        parent,
        slug="home",
        page_class=DummyPage,
        title="Home",
    )
    assert created is True
    assert page.slug == "home"
    assert page.title == "Home"
    assert page.save_revision().published is True

    page, created = get_or_create_page(
        parent,
        slug="home",
        page_class=DummyPage,
        title="Updated Home",
    )
    assert created is False
    assert page.title == "Updated Home"
    assert page.save_revision().published is True
