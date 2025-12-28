from __future__ import annotations

from cli.sum.utils.output import OutputFormatter


def test_progress_output(capsys) -> None:
    OutputFormatter.progress(1, 3, "Booting", status="done")
    captured = capsys.readouterr()
    assert "⏳ [1/3] done: Booting" in captured.out


def test_success_output(capsys) -> None:
    OutputFormatter.success("All set")
    captured = capsys.readouterr()
    assert "✅ All set" in captured.out


def test_error_output(capsys) -> None:
    OutputFormatter.error("Something broke")
    captured = capsys.readouterr()
    assert "❌ Something broke" in captured.out


def test_info_output(capsys) -> None:
    OutputFormatter.info("FYI")
    captured = capsys.readouterr()
    assert "ℹ FYI" in captured.out


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


def test_progress_emit_false_suppresses_output(capsys) -> None:
    message = OutputFormatter.progress(1, 3, "Setup", emit=False)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert message == "⏳ [1/3] running: Setup"


def test_success_emit_false_suppresses_output(capsys) -> None:
    message = OutputFormatter.success("Done", emit=False)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert message == "✅ Done"


def test_error_emit_false_suppresses_output(capsys) -> None:
    message = OutputFormatter.error("Bad", emit=False)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert message == "❌ Bad"


def test_info_emit_false_suppresses_output(capsys) -> None:
    message = OutputFormatter.info("Heads up", emit=False)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert message == "ℹ Heads up"


def test_summary_omits_sensitive_fields(capsys) -> None:
    OutputFormatter.summary(
        "demo-project",
        {
            "password": "secret",
            "location": "/tmp/demo",
        },
    )
    captured = capsys.readouterr()
    assert "secret" not in captured.out
    assert "location" in captured.out


def test_output_can_be_silent(capsys) -> None:
    message = OutputFormatter.success("quiet success", emit=False)
    captured = capsys.readouterr()
    assert message == "✅ quiet success"
    assert captured.out == ""
