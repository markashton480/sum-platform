from __future__ import annotations

from cli.sum.utils.output import OutputFormatter


def test_progress_output(capsys) -> None:
    OutputFormatter.progress(1, 3, "Booting", status="done")
    captured = capsys.readouterr()
    assert "⏳ [1/3] done: Booting" in captured.out


def test_success_error_info_output(capsys) -> None:
    OutputFormatter.success("All set")
    OutputFormatter.error("Something broke")
    OutputFormatter.info("FYI")
    captured = capsys.readouterr()
    assert "✅ All set" in captured.out
    assert "❌ Something broke" in captured.out
    assert "ℹ️ FYI" in captured.out


def test_summary_output(capsys) -> None:
    OutputFormatter.summary(
        "demo-project",
        {
            "Location": "/tmp/demo",
            "Status": "ready",
        },
    )
    captured = capsys.readouterr()
    assert "📋 Summary" in captured.out
    assert "🏷️  Project: demo-project" in captured.out
    assert "✅ Location: /tmp/demo" in captured.out
    assert "✅ Status: ready" in captured.out
