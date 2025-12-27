from __future__ import annotations

from pathlib import Path
from typing import Any

from cli.sum.commands.init import _build_setup_config, run_init
from cli.sum.setup.orchestrator import SetupResult
from cli.sum.utils.prompts import PromptManager


def test_run_init_scaffold_only_uses_scaffold(monkeypatch, tmp_path: Path) -> None:
    clients_dir = tmp_path / "clients"
    clients_dir.mkdir(parents=True)

    scaffold_calls: list[dict[str, Any]] = []

    def fake_scaffold(project_name: str, clients_dir: Path, theme_slug: str) -> Path:
        scaffold_calls.append(
            {
                "project_name": project_name,
                "clients_dir": clients_dir,
                "theme_slug": theme_slug,
            }
        )
        return clients_dir / project_name

    def fail_orchestrator(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("orchestrator should not be called for scaffold only")

    monkeypatch.setattr("cli.sum.commands.init.get_clients_dir", lambda: clients_dir)
    monkeypatch.setattr("cli.sum.commands.init.scaffold_project", fake_scaffold)
    monkeypatch.setattr(
        "cli.sum.commands.init.SetupOrchestrator.run_full_setup", fail_orchestrator
    )

    assert run_init("acme-kitchens") == 0
    assert scaffold_calls == [
        {
            "project_name": "acme-kitchens",
            "clients_dir": clients_dir,
            "theme_slug": "theme_a",
        }
    ]


def test_run_init_full_builds_config_and_runs_orchestrator(
    monkeypatch, tmp_path: Path
) -> None:
    clients_dir = tmp_path / "clients"
    clients_dir.mkdir(parents=True)

    captured: dict[str, Any] = {}

    def fake_run_full_setup(self, config) -> SetupResult:
        captured["config"] = config
        return SetupResult(
            success=True,
            project_path=self.project_path,
            credentials_path=Path("credentials.env"),
            url="http://127.0.0.1:9000/",
        )

    monkeypatch.setattr("cli.sum.commands.init.get_clients_dir", lambda: clients_dir)
    monkeypatch.setattr(
        "cli.sum.commands.init.SetupOrchestrator.run_full_setup", fake_run_full_setup
    )

    assert (
        run_init(
            "acme-kitchens",
            full=True,
            no_prompt=True,
            skip_migrations=True,
            run_server=True,
            port=9000,
        )
        == 0
    )

    config = captured["config"]
    assert config.full is True
    assert config.quick is False
    assert config.no_prompt is True
    assert config.skip_migrations is True
    assert config.run_server is True
    assert config.port == 9000


def test_run_init_rejects_full_and_quick(monkeypatch, tmp_path: Path) -> None:
    clients_dir = tmp_path / "clients"
    clients_dir.mkdir(parents=True)

    error_messages: list[str] = []

    monkeypatch.setattr("cli.sum.commands.init.get_clients_dir", lambda: clients_dir)
    monkeypatch.setattr(
        "cli.sum.commands.init.OutputFormatter.error",
        lambda message: error_messages.append(message),
    )

    assert run_init("acme-kitchens", full=True, quick=True) == 1
    assert error_messages == ["--full and --quick are mutually exclusive"]


def test_build_setup_config_prompts_full_flow(monkeypatch) -> None:
    responses = {
        "Setup Python environment?": False,
        "Run database migrations?": True,
        "Seed initial homepage?": False,
        "Create superuser?": True,
        "Start development server?": True,
    }
    text_responses = iter(["admin2", "admin2@example.com", "secret"])
    confirm_messages: list[str] = []
    text_messages: list[str] = []

    class FakePrompts(PromptManager):
        def confirm(self, message: str, default: bool = True) -> bool:
            confirm_messages.append(message)
            return responses[message]

        def text(self, message: str, default: str | None = None) -> str:
            text_messages.append(message)
            return next(text_responses)

    config = _build_setup_config(
        prompts=FakePrompts(),
        full=True,
        quick=False,
        no_prompt=False,
        ci=False,
        skip_venv=False,
        skip_migrations=False,
        skip_seed=False,
        skip_superuser=False,
        run_server=False,
        port=8000,
        seed_preset=None,
    )

    assert confirm_messages == [
        "Setup Python environment?",
        "Run database migrations?",
        "Seed initial homepage?",
        "Create superuser?",
        "Start development server?",
    ]
    assert text_messages == ["Username", "Email", "Password"]
    assert config.skip_venv is True
    assert config.skip_migrations is False
    assert config.skip_seed is True
    assert config.skip_superuser is False
    assert config.superuser_username == "admin2"
    assert config.superuser_email == "admin2@example.com"
    assert config.superuser_password == "secret"
    assert config.run_server is True
