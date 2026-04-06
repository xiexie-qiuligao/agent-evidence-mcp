from datetime import datetime
from pathlib import Path

from task_evidence_mcp.layout import (
    SessionLayout,
    build_artifact_name,
    build_session_id,
    ensure_unique_path,
    slugify,
)


def test_slugify_normalizes_text() -> None:
    assert slugify("Deploy Admin Panel") == "deploy-admin-panel"
    assert slugify("  !!! ") == "task"


def test_build_session_id_is_sortable_and_readable() -> None:
    session_id = build_session_id(
        "Deploy Admin Panel",
        timestamp=datetime(2026, 4, 6, 15, 30, 12),
    )

    assert session_id == "20260406-153012-deploy-admin-panel"


def test_build_artifact_name_matches_expected_format() -> None:
    artifact_name = build_artifact_name(
        "Final Result",
        "png",
        timestamp=datetime(2026, 4, 6, 15, 45, 0),
    )

    assert artifact_name == "20260406-154500-final-result.png"


def test_session_layout_paths_follow_repository_convention(tmp_path: Path) -> None:
    layout = SessionLayout(tmp_path, "20260406-153012-demo")

    assert layout.session_dir == tmp_path / "20260406-153012-demo"
    assert layout.screenshots_dir == tmp_path / "20260406-153012-demo" / "screenshots"
    assert layout.recordings_dir == tmp_path / "20260406-153012-demo" / "recordings"
    assert layout.timeline_path == tmp_path / "20260406-153012-demo" / "timeline.jsonl"


def test_ensure_unique_path_adds_numeric_suffix(tmp_path: Path) -> None:
    original = tmp_path / "session"
    original.mkdir()

    unique = ensure_unique_path(original)

    assert unique == tmp_path / "session-2"
