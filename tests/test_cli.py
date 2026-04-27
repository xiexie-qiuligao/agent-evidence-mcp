from __future__ import annotations

import json
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


def test_session_lookup_commands_return_json(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    start_exit = cli.main(["start-session", "CLI Lookup Flow"])
    start_output = capsys.readouterr()
    start_payload = json.loads(start_output.out)

    list_exit = cli.main(["list-sessions", "--status", "active"])
    list_output = capsys.readouterr()
    list_payload = json.loads(list_output.out)

    get_exit = cli.main(["get-session", start_payload["session_id"]])
    get_output = capsys.readouterr()
    get_payload = json.loads(get_output.out)

    latest_exit = cli.main(["latest-session", "--status", "active"])
    latest_output = capsys.readouterr()
    latest_payload = json.loads(latest_output.out)

    assert start_exit == 0
    assert list_exit == 0
    assert get_exit == 0
    assert latest_exit == 0
    assert list_payload["session_count"] == 1
    assert get_payload["task_name"] == "CLI Lookup Flow"
    assert latest_payload["session_id"] == start_payload["session_id"]
