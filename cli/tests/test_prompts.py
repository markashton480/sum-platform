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


def test_confirm_uppercase_inputs_respected(monkeypatch) -> None:
    inputs = iter(["Y", "N"])
    monkeypatch.setattr(builtins, "input", lambda *_args: next(inputs))

    manager = PromptManager()
    assert manager.confirm("Proceed?", default=False) is True
    assert manager.confirm("Proceed?", default=True) is False


def test_confirm_full_word_inputs_respected(monkeypatch) -> None:
    inputs = iter(["YES", "NO"])
    monkeypatch.setattr(builtins, "input", lambda *_args: next(inputs))

    manager = PromptManager()
    assert manager.confirm("Proceed?", default=False) is True
    assert manager.confirm("Proceed?", default=True) is False


def test_confirm_invalid_input_uses_default(monkeypatch) -> None:
    inputs = iter(["maybe"])
    monkeypatch.setattr(builtins, "input", lambda *_args: next(inputs))

    manager = PromptManager()
    assert manager.confirm("Proceed?", default=True) is False


def test_confirm_empty_input_uses_default(monkeypatch) -> None:
    inputs = iter([""])
    monkeypatch.setattr(builtins, "input", lambda *_args: next(inputs))

    manager = PromptManager()
    assert manager.confirm("Proceed?", default=False) is False


def test_text_prompts_user(monkeypatch) -> None:
    inputs = iter(["", "custom"])
    monkeypatch.setattr(builtins, "input", lambda *_args: next(inputs))

    manager = PromptManager()
    assert manager.text("Project?", default="demo") == "demo"
    assert manager.text("Project?", default="demo") == "custom"
