from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PromptManager:
    no_prompt: bool = False
    ci: bool = False

    def _should_prompt(self) -> bool:
        return not (self.no_prompt or self.ci)

    def confirm(self, message: str, default: bool = True) -> bool:
        if not self._should_prompt():
            return default

        suffix = " [Y/n]" if default else " [y/N]"
        response = input(f"{message}{suffix}: ").strip().lower()
        if not response:
            return default
        return response in {"y", "yes"}

    def text(self, message: str, default: str | None = None) -> str:
        if not self._should_prompt():
            return default or ""

        suffix = f" [{default}]" if default else ""
        response = input(f"{message}{suffix}: ").strip()
        if response:
            return response
        return default or ""
