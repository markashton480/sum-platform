from __future__ import annotations

from collections.abc import Mapping


class OutputFormatter:
    """Formatting helpers for CLI output."""

    @staticmethod
    def progress(step: int, total: int, message: str, status: str = "running") -> str:
        """Format, print, and return a progress line for a multi-step operation."""
        line = f"⏳ [{step}/{total}] {status}: {message}"
        print(line)
        return line

    @staticmethod
    def success(message: str) -> str:
        """Format, print, and return a success message string."""
        line = f"✅ {message}"
        print(line)
        return line

    @staticmethod
    def error(message: str) -> str:
        """Format, print, and return an error message string."""
        line = f"❌ {message}"
        print(line)
        return line

    @staticmethod
    def info(message: str) -> str:
        """Format, print, and return an informational message string."""
        line = f"ℹ {message}"
        print(line)
        return line

    @staticmethod
    def summary(project_name: str, data: Mapping[str, str]) -> str:
        """Format, print, and return a formatted summary block for a project."""
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
