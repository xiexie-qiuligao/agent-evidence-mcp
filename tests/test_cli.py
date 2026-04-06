from __future__ import annotations

from pathlib import Path

from task_evidence_mcp import cli


def test_missing_session_returns_clean_error(capsys) -> None:
    exit_code = cli.main(["list-artifacts", str(Path("D:/definitely-missing-session"))])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Session error:" in captured.err


def test_compare_latest_artifacts_missing_session_returns_clean_error(capsys) -> None:
    exit_code = cli.main(
        ["compare-latest-artifacts", str(Path("D:/definitely-missing-session"))]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Session error:" in captured.err
