"""
Name: Seed Management Command Tests
Path: tests/sum_core/test_seed_command.py
Purpose: Verify the test-project `seed` management command behaviour.
Family: sum_core management command tests.
Dependencies: pytest, Django call_command.
"""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import home.management.commands.seed as seed_command_module
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


class DummyOrchestrator:
    last_instance: DummyOrchestrator | None = None
    default_profiles: list[str] = ["sage-stone"]

    def __init__(self, *, content_dir: Path | None = None) -> None:
        self.content_dir = content_dir
        self.plan_calls: list[str] = []
        self.seed_calls: list[tuple[str, bool]] = []
        self.profiles: list[str] = list(self.default_profiles)
        DummyOrchestrator.last_instance = self

    def list_profiles(self) -> list[str]:
        return list(self.profiles)

    def plan(self, profile: str):
        self.plan_calls.append(profile)
        return seed_command_module.SeedPlan(
            profile=profile,
            content_dir=self.content_dir or Path("content"),
            pages=["home"],
            seeders=["home"],
        )

    def seed(self, profile: str, *, clear: bool = False) -> None:
        self.seed_calls.append((profile, clear))


def test_seed_command_uses_explicit_profile_argument(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(seed_command_module, "SeedOrchestrator", DummyOrchestrator)
    DummyOrchestrator.default_profiles = ["sage-stone"]

    out = StringIO()
    call_command("seed", "demo", dry_run=True, stdout=out)

    orchestrator = DummyOrchestrator.last_instance
    assert orchestrator is not None
    assert orchestrator.plan_calls == ["demo"]


def test_seed_command_defaults_to_sage_stone_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(seed_command_module, "SeedOrchestrator", DummyOrchestrator)
    DummyOrchestrator.default_profiles = ["sage-stone"]

    out = StringIO()
    call_command("seed", dry_run=True, stdout=out)

    orchestrator = DummyOrchestrator.last_instance
    assert orchestrator is not None
    assert orchestrator.plan_calls == ["sage-stone"]


def test_seed_command_errors_when_no_profiles_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(seed_command_module, "SeedOrchestrator", DummyOrchestrator)
    DummyOrchestrator.last_instance = None
    DummyOrchestrator.default_profiles = []

    out = StringIO()
    with pytest.raises(CommandError, match="no content profiles were found"):
        call_command("seed", dry_run=True, stdout=out)


def test_seed_command_dry_run_prints_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(seed_command_module, "SeedOrchestrator", DummyOrchestrator)
    DummyOrchestrator.default_profiles = ["sage-stone"]

    out = StringIO()
    call_command("seed", "demo", dry_run=True, stdout=out)

    output = out.getvalue()
    assert "Seed plan" in output
    assert "Profile: demo" in output

    orchestrator = DummyOrchestrator.last_instance
    assert orchestrator is not None
    assert orchestrator.seed_calls == []


def test_seed_command_passes_content_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(seed_command_module, "SeedOrchestrator", DummyOrchestrator)
    DummyOrchestrator.default_profiles = ["sage-stone"]

    out = StringIO()
    call_command(
        "seed",
        "demo",
        dry_run=True,
        content_path="/tmp/test-content",
        stdout=out,
    )

    orchestrator = DummyOrchestrator.last_instance
    assert orchestrator is not None
    assert orchestrator.content_dir == Path("/tmp/test-content")
