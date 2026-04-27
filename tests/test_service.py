from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

from task_evidence_mcp.capture import ScreenshotBackend
from task_evidence_mcp.config import AppConfig
from task_evidence_mcp.ocr import OCRBackend, OCRUnavailableError
from task_evidence_mcp.redaction import RedactionBackend, RedactionRegion
from task_evidence_mcp.recording import RecordingBackend, RecordingHandle, RecordingUnavailableError
from task_evidence_mcp.artifacts import ArtifactReviewError
from task_evidence_mcp.service import TaskEvidenceService


class FakeScreenshotBackend(ScreenshotBackend):
    def capture_full_screen(self, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(f"fake-image:{destination.name}".encode("utf-8"))


class FakeRecordingBackend(RecordingBackend):
    def __init__(self) -> None:
        self.started: list[tuple[Path, int]] = []
        self.stopped: list[int] = []
        self._pid = 9000

    def is_available(self) -> bool:
        return True

    def start_full_screen_recording(self, destination: Path, frame_rate: int) -> RecordingHandle:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"fake-video")
        self._pid += 1
        self.started.append((destination, frame_rate))
        return RecordingHandle(pid=self._pid)

    def stop_recording(self, handle: RecordingHandle) -> None:
        self.stopped.append(handle.pid)


class MissingFileRecordingBackend(FakeRecordingBackend):
    def start_full_screen_recording(self, destination: Path, frame_rate: int) -> RecordingHandle:
        destination.parent.mkdir(parents=True, exist_ok=True)
        self._pid += 1
        self.started.append((destination, frame_rate))
        return RecordingHandle(pid=self._pid)


class FakeOCRBackend(OCRBackend):
    def is_available(self) -> bool:
        return True

    def extract_text(self, image_path: Path) -> str:
        return f"OCR::{image_path.name}"


class FakeRedactionBackend(RedactionBackend):
    def redact_image(
        self,
        source: Path,
        destination: Path,
        regions: list[RedactionRegion],
        color: str = "#000000",
    ) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = f"redacted:{source.name}:{color}:{len(regions)}"
        destination.write_text(payload, encoding="utf-8")


def test_start_session_creates_expected_files(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )

    result = service.start_session("Deploy Admin Panel")

    assert Path(result.layout.session_path).exists()
    assert Path(result.layout.summary_path).exists()
    payload = json.loads(result.layout.session_path.read_text(encoding="utf-8"))
    assert payload["task_name"] == "Deploy Admin Panel"
    assert payload["status"] == "active"


def test_list_sessions_returns_newest_first_and_supports_filters(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    first = service.start_session("First Flow", timestamp=datetime(2026, 4, 6, 9, 0, 0))
    second = service.start_session("Second Flow", timestamp=datetime(2026, 4, 6, 10, 0, 0))
    service.end_session(first.layout.session_dir)

    listed = service.list_sessions()
    active = service.list_sessions(status="active")
    limited = service.list_sessions(limit=1)

    assert [item.session.session_id for item in listed.sessions] == [
        second.session.session_id,
        first.session.session_id,
    ]
    assert [item.session.session_id for item in active.sessions] == [second.session.session_id]
    assert limited.sessions[0].session.session_id == second.session.session_id


def test_get_session_accepts_session_id_or_directory(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    start = service.start_session("Lookup Flow")

    by_id = service.get_session(start.session.session_id)
    by_dir = service.get_session(start.layout.session_dir)
    latest = service.get_latest_session()

    assert by_id.session.task_name == "Lookup Flow"
    assert by_dir.session.session_id == start.session.session_id
    assert latest.session.session_id == start.session.session_id
    assert Path(by_id.to_dict()["summary_path"]).exists()


def test_session_summary_and_artifact_payload_helpers(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    start = service.start_session("Resource Flow")
    capture = service.capture_checkpoint(
        start.layout.session_dir,
        label="ready",
        reason="Ready for resource inspection.",
    )

    summary = service.read_latest_session_summary()
    payload = service.get_session_artifacts_payload(start.session.session_id)

    assert "Resource Flow" in summary
    assert payload["session_id"] == start.session.session_id
    assert payload["artifact_count"] == 1
    assert payload["artifacts"][0]["artifact_id"] == capture.artifact.artifact_id


def test_capture_checkpoint_updates_timeline_and_summary(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    start = service.start_session("QA Flow")

    result = service.capture_checkpoint(
        start.layout.session_dir,
        label="form-submitted",
        reason="Submission completed successfully.",
        step="step-02",
        tags=["qa", "success"],
    )

    assert Path(result.artifact.path).exists()
    timeline_lines = start.layout.timeline_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(timeline_lines) == 1
    timeline_payload = json.loads(timeline_lines[0])
    assert timeline_payload["label"] == "form-submitted"
    assert timeline_payload["step"] == "step-02"
    summary_text = start.layout.summary_path.read_text(encoding="utf-8")
    assert "Submission completed successfully." in summary_text
    assert "## Highlights" in summary_text
    assert "Screenshot count" in summary_text


def test_summary_includes_review_signals_when_two_screenshots_exist(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    start = service.start_session("Review Signals")
    service.capture_checkpoint(
        start.layout.session_dir,
        label="before-change",
        reason="Before the key action.",
    )
    service.capture_checkpoint(
        start.layout.session_dir,
        label="after-change",
        reason="After the key action.",
    )

    summary_text = start.layout.summary_path.read_text(encoding="utf-8")

    assert "## Review Signals" in summary_text
    assert "Latest `screenshot` pair" in summary_text
    assert "verdict: `content_changed`" in summary_text
    assert "review focus:" in summary_text


def test_attach_note_and_ocr_enrich_artifact_and_summary(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    start = service.start_session("OCR Ready Flow")
    capture = service.capture_checkpoint(
        start.layout.session_dir,
        label="error-dialog",
        reason="Dialog appeared for review.",
    )

    noted = service.attach_note(
        start.layout.session_dir,
        capture.artifact.artifact_id,
        "Need to review the dialog copy.",
    )
    ocred = service.ocr_artifact(
        start.layout.session_dir,
        capture.artifact.artifact_id,
        "Error: invalid credentials",
    )
    listed = service.list_artifacts(start.layout.session_dir)

    assert noted.artifact.notes == ["Need to review the dialog copy."]
    assert ocred.artifact.ocr_text == "Error: invalid credentials"
    assert listed[0].notes == ["Need to review the dialog copy."]
    assert listed[0].ocr_text == "Error: invalid credentials"
    summary_text = start.layout.summary_path.read_text(encoding="utf-8")
    assert "Need to review the dialog copy." in summary_text
    assert "Error: invalid credentials" in summary_text


def test_redact_artifact_creates_new_redacted_screenshot(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
        redaction_backend=FakeRedactionBackend(),
    )
    start = service.start_session("Redaction Flow")
    source = service.capture_checkpoint(
        start.layout.session_dir,
        label="contains-sensitive-value",
        reason="Need a safe shareable copy.",
    )

    redacted = service.redact_artifact(
        start.layout.session_dir,
        source.artifact.artifact_id,
        "safe-copy",
        [{"x": 10, "y": 20, "width": 30, "height": 40}],
        reason="Mask the sensitive value before sharing.",
        tags=["shareable"],
    )

    assert Path(redacted.artifact.path).exists()
    assert redacted.artifact.source_artifact_id == source.artifact.artifact_id
    assert redacted.artifact.redactions == [{"x": 10, "y": 20, "width": 30, "height": 40}]
    assert "redacted" in redacted.artifact.tags
    assert "shareable" in redacted.artifact.tags
    summary_text = start.layout.summary_path.read_text(encoding="utf-8")
    assert "source artifact" in summary_text
    assert "redactions: 1 region(s)" in summary_text


def test_automatic_ocr_uses_backend_for_screenshot_artifact(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(ocr_enabled=True),
        screenshot_backend=FakeScreenshotBackend(),
        ocr_backend=FakeOCRBackend(),
    )
    start = service.start_session("Automatic OCR")
    capture = service.capture_checkpoint(
        start.layout.session_dir,
        label="login-error",
        reason="Need OCR automatically.",
    )

    updated = service.ocr_artifact(
        start.layout.session_dir,
        capture.artifact.artifact_id,
    )

    assert updated.artifact.ocr_text == f"OCR::{Path(capture.artifact.path).name}"


def test_automatic_ocr_fails_when_disabled(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(ocr_enabled=False),
        screenshot_backend=FakeScreenshotBackend(),
        ocr_backend=FakeOCRBackend(),
    )
    start = service.start_session("Disabled OCR")
    capture = service.capture_checkpoint(
        start.layout.session_dir,
        label="dialog",
        reason="Need OCR",
    )

    try:
        service.ocr_artifact(
            start.layout.session_dir,
            capture.artifact.artifact_id,
        )
    except OCRUnavailableError as exc:
        assert "disabled" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected OCRUnavailableError when OCR is disabled.")


def test_compare_artifacts_reports_metadata_and_ocr_changes(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    start = service.start_session("Compare Flow")
    first = service.capture_checkpoint(
        start.layout.session_dir,
        label="state-a",
        reason="Before change.",
    )
    second = service.capture_checkpoint(
        start.layout.session_dir,
        label="state-b",
        reason="After change.",
    )
    service.attach_note(start.layout.session_dir, second.artifact.artifact_id, "Changed visual state.")
    service.ocr_artifact(start.layout.session_dir, second.artifact.artifact_id, "New OCR text")

    comparison = service.compare_artifacts(
        start.layout.session_dir,
        first.artifact.artifact_id,
        second.artifact.artifact_id,
    )

    assert comparison.comparison.same_artifact_type is True
    assert comparison.comparison.verdict == "content_changed"
    assert comparison.comparison.label_changed is True
    assert comparison.comparison.source_artifact_changed is False
    assert comparison.comparison.notes_changed is True
    assert comparison.comparison.ocr_changed is True
    assert "binary_content" in comparison.comparison.changed_fields
    assert "ocr_text" in comparison.comparison.changed_fields
    assert comparison.comparison.review_focus
    assert "verdict: content changed" in comparison.comparison.summary


def test_compare_artifacts_can_report_unchanged_when_same_artifact_is_used(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    start = service.start_session("Compare Same Artifact")
    first = service.capture_checkpoint(
        start.layout.session_dir,
        label="stable-state",
        reason="No change expected.",
    )

    comparison = service.compare_artifacts(
        start.layout.session_dir,
        first.artifact.artifact_id,
        first.artifact.artifact_id,
    )

    assert comparison.comparison.verdict == "unchanged"
    assert comparison.comparison.changed_fields == []
    assert "No meaningful differences" in comparison.comparison.review_focus[0]


def test_compare_artifacts_reports_redaction_metadata_changes(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
        redaction_backend=FakeRedactionBackend(),
    )
    start = service.start_session("Compare Redactions")
    source = service.capture_checkpoint(
        start.layout.session_dir,
        label="raw",
        reason="Raw screenshot.",
    )
    redacted = service.redact_artifact(
        start.layout.session_dir,
        source.artifact.artifact_id,
        "redacted",
        [{"x": 1, "y": 2, "width": 10, "height": 10}],
    )

    comparison = service.compare_artifacts(
        start.layout.session_dir,
        source.artifact.artifact_id,
        redacted.artifact.artifact_id,
    )

    assert comparison.comparison.redactions_changed is True
    assert comparison.comparison.source_artifact_changed is True
    assert "redactions" in comparison.comparison.changed_fields


def test_compare_latest_artifacts_prefers_latest_artifact_type(tmp_path: Path) -> None:
    backend = FakeRecordingBackend()
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(recording_enabled=True),
        screenshot_backend=FakeScreenshotBackend(),
        recording_backend=backend,
    )
    start = service.start_session("Latest Compare")
    first = service.capture_checkpoint(
        start.layout.session_dir,
        label="before",
        reason="Before change.",
    )
    service.capture_checkpoint(
        start.layout.session_dir,
        label="after",
        reason="After change.",
    )
    service.start_recording(
        start.layout.session_dir,
        label="motion-a",
        reason="Motion snapshot one.",
    )
    service.stop_recording(start.layout.session_dir)
    service.start_recording(
        start.layout.session_dir,
        label="motion-b",
        reason="Motion snapshot two.",
    )
    last_recording = service.stop_recording(start.layout.session_dir)

    comparison = service.compare_latest_artifacts(start.layout.session_dir)

    assert comparison.comparison.from_artifact_id != first.artifact.artifact_id
    assert comparison.comparison.to_artifact_id == last_recording.artifact.artifact_id
    assert comparison.comparison.same_artifact_type is True


def test_compare_latest_artifacts_can_filter_by_type(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    start = service.start_session("Latest Screenshot Compare")
    service.capture_checkpoint(
        start.layout.session_dir,
        label="first-screen",
        reason="First state.",
    )
    second = service.capture_checkpoint(
        start.layout.session_dir,
        label="second-screen",
        reason="Second state.",
    )

    comparison = service.compare_latest_artifacts(
        start.layout.session_dir,
        artifact_type="screenshot",
    )

    assert comparison.comparison.to_artifact_id == second.artifact.artifact_id
    assert comparison.comparison.verdict == "content_changed"


def test_compare_latest_artifacts_fails_when_not_enough_candidates(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    start = service.start_session("Insufficient Review Artifacts")
    service.capture_checkpoint(
        start.layout.session_dir,
        label="only-one",
        reason="Only one artifact available.",
    )

    try:
        service.compare_latest_artifacts(start.layout.session_dir, artifact_type="screenshot")
    except ArtifactReviewError as exc:
        assert "Need at least two artifacts" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected ArtifactReviewError when fewer than two comparable artifacts exist.")


def test_end_session_marks_session_completed(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    start = service.start_session("Admin Audit")

    service.capture_checkpoint(
        start.layout.session_dir,
        label="initial-state",
        reason="Beginning audit run.",
    )
    result = service.end_session(start.layout.session_dir)

    assert result.session.status == "completed"
    session_payload = json.loads(start.layout.session_path.read_text(encoding="utf-8"))
    assert session_payload["status"] == "completed"
    assert "Closed at" in start.layout.summary_path.read_text(encoding="utf-8")


def test_capture_screenshot_uses_default_reason(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    start = service.start_session("Manual Capture")

    result = service.capture_screenshot(
        start.layout.session_dir,
        label="manual-shot",
    )

    assert result.artifact.reason == "Manual screenshot capture."


def test_start_session_avoids_collision_for_same_task_name_and_timestamp(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    timestamp = datetime(2026, 4, 6, 16, 30, 0)

    first = service.start_session("Repeated Task", timestamp=timestamp)
    second = service.start_session("Repeated Task", timestamp=timestamp)

    assert first.layout.session_dir != second.layout.session_dir
    assert second.session.session_id == second.layout.session_dir.name


def test_recording_round_trip_creates_recording_artifact(tmp_path: Path) -> None:
    backend = FakeRecordingBackend()
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(recording_enabled=True),
        screenshot_backend=FakeScreenshotBackend(),
        recording_backend=backend,
    )
    start = service.start_session("Demo Recording")

    recording = service.start_recording(
        start.layout.session_dir,
        label="drag-flow",
        reason="Motion matters here.",
        step="step-03",
    )
    status = service.get_recording_status(start.layout.session_dir)
    stopped = service.stop_recording(start.layout.session_dir)

    assert recording.recording.label == "drag-flow"
    assert status.active is True
    assert stopped.artifact.artifact_type == "recording"
    assert stopped.artifact.label == "drag-flow"
    assert backend.stopped == [recording.recording.pid]
    summary_text = start.layout.summary_path.read_text(encoding="utf-8")
    assert "Recording count" in summary_text
    assert "drag-flow" in summary_text


def test_start_recording_fails_when_disabled(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(recording_enabled=False),
        screenshot_backend=FakeScreenshotBackend(),
        recording_backend=FakeRecordingBackend(),
    )
    start = service.start_session("Disabled Recording")

    try:
        service.start_recording(
            start.layout.session_dir,
            label="demo",
            reason="Should fail",
        )
    except RecordingUnavailableError as exc:
        assert "disabled" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected RecordingUnavailableError when recording is disabled.")


def test_end_session_fails_when_recording_is_active(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(recording_enabled=True),
        screenshot_backend=FakeScreenshotBackend(),
        recording_backend=FakeRecordingBackend(),
    )
    start = service.start_session("End While Recording")
    service.start_recording(
        start.layout.session_dir,
        label="demo",
        reason="Still recording",
    )

    try:
        service.end_session(start.layout.session_dir)
    except RecordingUnavailableError as exc:
        assert "Stop the recording first" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected RecordingUnavailableError when ending an active recording session.")


def test_start_recording_fails_when_one_is_already_active(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(recording_enabled=True),
        screenshot_backend=FakeScreenshotBackend(),
        recording_backend=FakeRecordingBackend(),
    )
    start = service.start_session("Duplicate Recording")
    service.start_recording(
        start.layout.session_dir,
        label="first",
        reason="First recording",
    )

    try:
        service.start_recording(
            start.layout.session_dir,
            label="second",
            reason="Should fail",
        )
    except RecordingUnavailableError as exc:
        assert "already active" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected RecordingUnavailableError when starting a second recording.")


def test_stop_recording_fails_when_output_file_is_missing(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(recording_enabled=True),
        screenshot_backend=FakeScreenshotBackend(),
        recording_backend=MissingFileRecordingBackend(),
    )
    start = service.start_session("Missing Recording File")
    service.start_recording(
        start.layout.session_dir,
        label="missing-video",
        reason="Backend did not write output",
    )

    try:
        service.stop_recording(start.layout.session_dir)
    except RecordingUnavailableError as exc:
        assert "was not found" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected RecordingUnavailableError when the recording file is missing.")
