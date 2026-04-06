from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from .artifacts import (
    ArtifactReviewError,
    append_artifact_note,
    find_artifact,
    find_latest_comparable_artifacts,
    load_artifacts_with_details,
    set_artifact_redactions,
    set_artifact_ocr_text,
)
from .capture import ScreenshotBackend, create_default_screenshot_backend
from .compare import ArtifactComparison, compare_artifacts
from .config import AppConfig
from .layout import (
    SessionLayout,
    build_artifact_name,
    build_session_id,
    ensure_unique_path,
)
from .models import ArtifactRecord, RecordingState, SessionRecord
from .ocr import OCRBackend, OCRUnavailableError, TesseractOCRBackend
from .redaction import PowerShellRedactionBackend, RedactionBackend, RedactionError, RedactionRegion
from .recording import (
    FFmpegRecordingBackend,
    RecordingBackend,
    RecordingHandle,
    RecordingUnavailableError,
)
from .storage import (
    append_timeline_entry,
    clear_recording_state,
    load_session,
    load_recording_state,
    load_timeline,
    save_recording_state,
    save_session,
)
from .summary import build_summary_markdown


@dataclass
class StartSessionResult:
    session: SessionRecord
    layout: SessionLayout

    def to_dict(self) -> dict:
        payload = asdict(self.session)
        payload["session_dir"] = str(self.layout.session_dir)
        payload["timeline_path"] = str(self.layout.timeline_path)
        return payload


@dataclass
class CaptureCheckpointResult:
    artifact: ArtifactRecord
    session: SessionRecord

    def to_dict(self) -> dict:
        payload = self.artifact.to_dict()
        payload["artifact_count"] = self.session.artifact_count
        return payload


@dataclass
class EndSessionResult:
    session: SessionRecord
    artifacts: list[ArtifactRecord]
    summary_path: str

    def to_dict(self) -> dict:
        payload = self.session.to_dict()
        payload["summary_path"] = self.summary_path
        payload["artifacts"] = [artifact.to_dict() for artifact in self.artifacts]
        return payload


@dataclass
class StartRecordingResult:
    recording: RecordingState

    def to_dict(self) -> dict:
        return self.recording.to_dict()


@dataclass
class RecordingStatusResult:
    session_id: str
    active: bool
    recording: RecordingState | None

    def to_dict(self) -> dict:
        payload = {
            "session_id": self.session_id,
            "active": self.active,
            "recording": None,
        }
        if self.recording is not None:
            payload["recording"] = self.recording.to_dict()
        return payload


@dataclass
class StopRecordingResult:
    recording: RecordingState
    artifact: ArtifactRecord
    session: SessionRecord

    def to_dict(self) -> dict:
        payload = {
            "recording": self.recording.to_dict(),
            "artifact": self.artifact.to_dict(),
            "artifact_count": self.session.artifact_count,
        }
        return payload


@dataclass
class ArtifactUpdateResult:
    artifact: ArtifactRecord

    def to_dict(self) -> dict:
        return self.artifact.to_dict()


@dataclass
class ArtifactComparisonResult:
    comparison: ArtifactComparison

    def to_dict(self) -> dict:
        return self.comparison.to_dict()


class TaskEvidenceService:
    def __init__(
        self,
        base_dir: Path,
        config: AppConfig | None = None,
        screenshot_backend: ScreenshotBackend | None = None,
        recording_backend: RecordingBackend | None = None,
        ocr_backend: OCRBackend | None = None,
        redaction_backend: RedactionBackend | None = None,
    ) -> None:
        self.base_dir = base_dir.resolve()
        self.config = config or AppConfig()
        self.screenshot_backend = screenshot_backend or create_default_screenshot_backend()
        self.recording_backend = recording_backend or FFmpegRecordingBackend(
            ffmpeg_path=self.config.ffmpeg_path,
            macos_avfoundation_input=self.config.macos_avfoundation_input,
            macos_capture_cursor=self.config.macos_capture_cursor,
            linux_x11_display=self.config.linux_x11_display,
            linux_draw_mouse=self.config.linux_draw_mouse,
        )
        self.ocr_backend = ocr_backend or TesseractOCRBackend(
            tesseract_path=self.config.tesseract_path,
            language=self.config.ocr_language,
        )
        self.redaction_backend = redaction_backend or PowerShellRedactionBackend()

    @property
    def artifacts_root(self) -> Path:
        return self.config.resolve_artifacts_dir(self.base_dir)

    def start_session(
        self,
        task_name: str,
        metadata: dict | None = None,
        timestamp: datetime | None = None,
    ) -> StartSessionResult:
        layout = SessionLayout(
            self.artifacts_root,
            build_session_id(task_name, timestamp=timestamp),
        )
        if layout.session_dir.exists():
            layout = SessionLayout(self.artifacts_root, ensure_unique_path(layout.session_dir).name)
        layout.create()

        session = SessionRecord.create(
            session_id=layout.session_id,
            task_name=task_name,
            artifacts_root=self.artifacts_root,
            metadata=metadata,
        )
        save_session(session, layout.session_path)
        layout.summary_path.write_text(
            build_summary_markdown(session, []),
            encoding="utf-8",
        )
        return StartSessionResult(session=session, layout=layout)

    def capture_checkpoint(
        self,
        session_dir: Path,
        label: str,
        reason: str,
        step: str | None = None,
        target: str = "desktop",
        tags: list[str] | None = None,
        timestamp: datetime | None = None,
    ) -> CaptureCheckpointResult:
        return self._capture_screenshot_artifact(
            session_dir=session_dir,
            label=label,
            reason=reason,
            step=step,
            target=target,
            tags=tags,
            timestamp=timestamp,
        )

    def capture_screenshot(
        self,
        session_dir: Path,
        label: str,
        reason: str = "Manual screenshot capture.",
        step: str | None = None,
        target: str = "desktop",
        tags: list[str] | None = None,
        timestamp: datetime | None = None,
    ) -> CaptureCheckpointResult:
        return self._capture_screenshot_artifact(
            session_dir=session_dir,
            label=label,
            reason=reason,
            step=step,
            target=target,
            tags=tags,
            timestamp=timestamp,
        )

    def _capture_screenshot_artifact(
        self,
        session_dir: Path,
        label: str,
        reason: str,
        step: str | None = None,
        target: str = "desktop",
        tags: list[str] | None = None,
        timestamp: datetime | None = None,
    ) -> CaptureCheckpointResult:
        layout = SessionLayout.from_session_dir(session_dir.resolve())
        session = load_session(layout.session_path)
        artifact_name = build_artifact_name(
            label,
            self.config.screenshot_format,
            timestamp=timestamp,
        )
        artifact_path = ensure_unique_path(layout.screenshots_dir / artifact_name)
        self.screenshot_backend.capture_full_screen(artifact_path)

        artifact = ArtifactRecord.create(
            artifact_id=artifact_path.stem,
            session_id=session.session_id,
            artifact_type="screenshot",
            label=label,
            reason=reason,
            path=artifact_path,
            step=step,
            target=target,
            tags=tags,
        )
        append_timeline_entry(layout.timeline_path, artifact)
        session.artifact_count += 1
        save_session(session, layout.session_path)
        layout.summary_path.write_text(
            build_summary_markdown(session, load_timeline(layout.timeline_path)),
            encoding="utf-8",
        )
        return CaptureCheckpointResult(artifact=artifact, session=session)

    def list_artifacts(self, session_dir: Path) -> list[ArtifactRecord]:
        layout = SessionLayout.from_session_dir(session_dir.resolve())
        load_session(layout.session_path)
        return load_artifacts_with_details(layout)

    def start_recording(
        self,
        session_dir: Path,
        label: str,
        reason: str,
        step: str | None = None,
        target: str = "desktop",
        tags: list[str] | None = None,
        timestamp: datetime | None = None,
    ) -> StartRecordingResult:
        if not self.config.recording_enabled:
            raise RecordingUnavailableError(
                "Recording is disabled in config. Set recording_enabled = true to use recording tools."
            )
        if not self.recording_backend.is_available():
            raise RecordingUnavailableError(
                "Recording backend is unavailable. Install ffmpeg or configure ffmpeg_path."
            )

        layout = SessionLayout.from_session_dir(session_dir.resolve())
        active = load_recording_state(layout.active_recording_path)
        if active is not None and active.status == "recording":
            raise RecordingUnavailableError(
                f"A recording is already active for this session: {active.recording_id}"
            )

        session = load_session(layout.session_path)
        recording_name = build_artifact_name(
            label,
            self.config.recording_format,
            timestamp=timestamp,
        )
        recording_path = ensure_unique_path(layout.recordings_dir / recording_name)
        handle = self.recording_backend.start_full_screen_recording(
            recording_path,
            frame_rate=self.config.recording_frame_rate,
        )
        recording = RecordingState.create(
            recording_id=recording_path.stem,
            session_id=session.session_id,
            label=label,
            reason=reason,
            path=recording_path,
            pid=handle.pid,
            step=step,
            target=target,
            tags=tags,
        )
        save_recording_state(recording, layout.active_recording_path)
        return StartRecordingResult(recording=recording)

    def get_recording_status(self, session_dir: Path) -> RecordingStatusResult:
        layout = SessionLayout.from_session_dir(session_dir.resolve())
        session = load_session(layout.session_path)
        recording = load_recording_state(layout.active_recording_path)
        return RecordingStatusResult(
            session_id=session.session_id,
            active=recording is not None and recording.status == "recording",
            recording=recording,
        )

    def stop_recording(self, session_dir: Path) -> StopRecordingResult:
        layout = SessionLayout.from_session_dir(session_dir.resolve())
        session = load_session(layout.session_path)
        recording = load_recording_state(layout.active_recording_path)
        if recording is None or recording.status != "recording":
            raise RecordingUnavailableError("No active recording was found for this session.")

        self.recording_backend.stop_recording(RecordingHandle(pid=recording.pid))
        recording.status = "stopped"
        recording_exists = Path(recording.path).exists()
        if not recording_exists:
            raise RecordingUnavailableError(
                f"Recording file was not found after stopping the process: {recording.path}"
            )
        artifact = ArtifactRecord.create(
            artifact_id=recording.recording_id,
            session_id=session.session_id,
            artifact_type="recording",
            label=recording.label,
            reason=recording.reason,
            path=Path(recording.path),
            step=recording.step,
            target=recording.target,
            tags=recording.tags,
        )
        append_timeline_entry(layout.timeline_path, artifact)
        session.artifact_count += 1
        save_session(session, layout.session_path)
        clear_recording_state(layout.active_recording_path)
        layout.summary_path.write_text(
            build_summary_markdown(session, load_artifacts_with_details(layout)),
            encoding="utf-8",
        )
        return StopRecordingResult(recording=recording, artifact=artifact, session=session)

    def attach_note(
        self,
        session_dir: Path,
        artifact_id: str,
        note: str,
    ) -> ArtifactUpdateResult:
        layout = SessionLayout.from_session_dir(session_dir.resolve())
        load_session(layout.session_path)
        artifact = find_artifact(layout, artifact_id)
        append_artifact_note(layout, artifact, note)
        updated = find_artifact(layout, artifact_id)
        session = load_session(layout.session_path)
        layout.summary_path.write_text(
            build_summary_markdown(session, load_artifacts_with_details(layout)),
            encoding="utf-8",
        )
        return ArtifactUpdateResult(artifact=updated)

    def ocr_artifact(
        self,
        session_dir: Path,
        artifact_id: str,
        text: str | None = None,
    ) -> ArtifactUpdateResult:
        layout = SessionLayout.from_session_dir(session_dir.resolve())
        load_session(layout.session_path)
        artifact = find_artifact(layout, artifact_id)
        ocr_text = text or self._extract_ocr_text(artifact)
        set_artifact_ocr_text(layout, artifact, ocr_text)
        updated = find_artifact(layout, artifact_id)
        session = load_session(layout.session_path)
        layout.summary_path.write_text(
            build_summary_markdown(session, load_artifacts_with_details(layout)),
            encoding="utf-8",
        )
        return ArtifactUpdateResult(artifact=updated)

    def redact_artifact(
        self,
        session_dir: Path,
        artifact_id: str,
        label: str,
        regions: list[dict[str, int]] | list[RedactionRegion],
        *,
        color: str = "#000000",
        reason: str | None = None,
        step: str | None = None,
        tags: list[str] | None = None,
    ) -> CaptureCheckpointResult:
        layout = SessionLayout.from_session_dir(session_dir.resolve())
        session = load_session(layout.session_path)
        source = find_artifact(layout, artifact_id)
        if source.artifact_type != "screenshot":
            raise RedactionError("Redaction currently supports screenshot artifacts only.")

        normalized_regions = self._normalize_redaction_regions(regions)
        artifact_name = build_artifact_name(
            label,
            self.config.screenshot_format,
        )
        artifact_path = ensure_unique_path(layout.screenshots_dir / artifact_name)
        self.redaction_backend.redact_image(
            Path(source.path),
            artifact_path,
            normalized_regions,
            color=color,
        )

        merged_tags: list[str] = list(source.tags)
        for tag in ["redacted", *(tags or [])]:
            if tag not in merged_tags:
                merged_tags.append(tag)

        artifact = ArtifactRecord.create(
            artifact_id=artifact_path.stem,
            session_id=session.session_id,
            artifact_type="screenshot",
            label=label,
            reason=reason or f"Redacted copy created from artifact {artifact_id}.",
            path=artifact_path,
            step=step if step is not None else source.step,
            target=source.target,
            tags=merged_tags,
            source_artifact_id=artifact_id,
            redactions=[region.to_dict() for region in normalized_regions],
        )
        append_timeline_entry(layout.timeline_path, artifact)
        session.artifact_count += 1
        save_session(session, layout.session_path)
        set_artifact_redactions(
            layout,
            artifact,
            source_artifact_id=artifact_id,
            redactions=[region.to_dict() for region in normalized_regions],
        )
        updated_artifacts = load_artifacts_with_details(layout)
        layout.summary_path.write_text(
            build_summary_markdown(session, updated_artifacts),
            encoding="utf-8",
        )
        updated_artifact = find_artifact(layout, artifact.artifact_id)
        return CaptureCheckpointResult(artifact=updated_artifact, session=session)

    def _extract_ocr_text(self, artifact: ArtifactRecord) -> str:
        if not self.config.ocr_enabled:
            raise OCRUnavailableError(
                "OCR is disabled in config. Set [ocr].enabled = true to use automatic OCR."
            )
        if artifact.artifact_type != "screenshot":
            raise OCRUnavailableError("Automatic OCR currently supports screenshot artifacts only.")
        if not self.ocr_backend.is_available():
            raise OCRUnavailableError(
                "OCR backend is unavailable. Install tesseract or configure tesseract_path."
            )
        return self.ocr_backend.extract_text(Path(artifact.path))

    def end_session(self, session_dir: Path) -> EndSessionResult:
        layout = SessionLayout.from_session_dir(session_dir.resolve())
        session = load_session(layout.session_path)
        recording = load_recording_state(layout.active_recording_path)
        if recording is not None and recording.status == "recording":
            raise RecordingUnavailableError(
                "Cannot end a session while a recording is active. Stop the recording first."
            )
        artifacts = load_artifacts_with_details(layout)
        session.status = "completed"
        session.closed_at = datetime.now().astimezone().isoformat()
        save_session(session, layout.session_path)
        layout.summary_path.write_text(
            build_summary_markdown(session, artifacts),
            encoding="utf-8",
        )
        return EndSessionResult(
            session=session,
            artifacts=artifacts,
            summary_path=str(layout.summary_path),
        )

    def compare_artifacts(
        self,
        session_dir: Path,
        from_artifact_id: str,
        to_artifact_id: str,
    ) -> ArtifactComparisonResult:
        layout = SessionLayout.from_session_dir(session_dir.resolve())
        load_session(layout.session_path)
        older = find_artifact(layout, from_artifact_id)
        newer = find_artifact(layout, to_artifact_id)
        return ArtifactComparisonResult(
            comparison=compare_artifacts(older, newer),
        )

    def compare_latest_artifacts(
        self,
        session_dir: Path,
        artifact_type: str | None = None,
    ) -> ArtifactComparisonResult:
        layout = SessionLayout.from_session_dir(session_dir.resolve())
        load_session(layout.session_path)
        older, newer = find_latest_comparable_artifacts(layout, artifact_type=artifact_type)
        return ArtifactComparisonResult(
            comparison=compare_artifacts(older, newer),
        )

    def _normalize_redaction_regions(
        self,
        regions: list[dict[str, int]] | list[RedactionRegion],
    ) -> list[RedactionRegion]:
        normalized: list[RedactionRegion] = []
        for region in regions:
            if isinstance(region, RedactionRegion):
                normalized.append(region)
                continue
            normalized.append(
                RedactionRegion(
                    x=int(region["x"]),
                    y=int(region["y"]),
                    width=int(region["width"]),
                    height=int(region["height"]),
                )
            )
        if not normalized:
            raise RedactionError("At least one redaction region is required.")
        return normalized
