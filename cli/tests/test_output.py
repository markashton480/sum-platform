from __future__ import annotations

from cli.sum.utils.output import OutputFormatter


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


def test_summary_omits_password(capsys) -> None:
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
