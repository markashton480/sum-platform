from __future__ import annotations

from collections.abc import Mapping


class OutputFormatter:
    """Formatting helpers for CLI output."""

    @staticmethod
    def progress(step: int, total: int, message: str, status: str = "running") -> str:
        line = f"⏳ [{step}/{total}] {status}: {message}"
        print(line)
        return line

    @staticmethod
    def success(message: str) -> str:
        line = f"✅ {message}"
        print(line)
        return line

    @staticmethod
    def error(message: str) -> str:
        line = f"❌ {message}"
        print(line)
        return line

    @staticmethod
    def info(message: str) -> str:
        line = f"ℹ️ {message}"
        print(line)
        return line

    @staticmethod
    def summary(project_name: str, data: Mapping[str, str]) -> str:
        lines = [
            "📋 Summary",
            "--------------------",
            f"🏷️  Project: {project_name}",
        ]
        for key, value in data.items():
            lines.append(f"✅ {key}: {value}")
        lines.append("--------------------")
        output = "\n".join(lines)
        print(output)
        return output
