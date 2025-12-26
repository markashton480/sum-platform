from __future__ import annotations

import builtins

from cli.sum.utils.prompts import PromptManager


def test_confirm_no_prompt_returns_default(monkeypatch) -> None:
    def fail_input(*_args, **_kwargs):
        raise AssertionError("input() should not be called")

    monkeypatch.setattr(builtins, "input", fail_input)

    manager = PromptManager(no_prompt=True)
    assert manager.confirm("Proceed?", default=False) is False


def test_text_ci_returns_default(monkeypatch) -> None:
    def fail_input(*_args, **_kwargs):
        raise AssertionError("input() should not be called")

    monkeypatch.setattr(builtins, "input", fail_input)

    manager = PromptManager(ci=True)
    assert manager.text("Name?", default="admin") == "admin"


def test_text_no_prompt_without_default(monkeypatch) -> None:
    def fail_input(*_args, **_kwargs):
        raise AssertionError("input() should not be called")

    monkeypatch.setattr(builtins, "input", fail_input)

    manager = PromptManager(no_prompt=True)
    assert manager.text("Name?") == ""


def test_confirm_prompts_user(monkeypatch) -> None:
    inputs = iter(["", "n", "yes"])
    monkeypatch.setattr(builtins, "input", lambda *_args: next(inputs))

    manager = PromptManager()
    assert manager.confirm("Proceed?", default=True) is True
    assert manager.confirm("Proceed?", default=True) is False
    assert manager.confirm("Proceed?", default=False) is True


def test_confirm_handles_common_inputs(monkeypatch) -> None:
    inputs = iter(["Y", "N", "YES", "NO", "maybe", ""])
    monkeypatch.setattr(builtins, "input", lambda *_args: next(inputs))

    manager = PromptManager()
    assert manager.confirm("Proceed?", default=False) is True
    assert manager.confirm("Proceed?", default=True) is False
    assert manager.confirm("Proceed?", default=False) is True
    assert manager.confirm("Proceed?", default=True) is False
    assert manager.confirm("Proceed?", default=True) is False
    assert manager.confirm("Proceed?", default=False) is False


def test_text_prompts_user(monkeypatch) -> None:
    inputs = iter(["", "custom"])
    monkeypatch.setattr(builtins, "input", lambda *_args: next(inputs))

    manager = PromptManager()
    assert manager.text("Project?", default="demo") == "demo"
    assert manager.text("Project?", default="demo") == "custom"
