from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from mcp.server.fastmcp import Context, FastMCP

from .config import AppConfig
from .models import ArtifactRecord
from .service import TaskEvidenceService


SERVER_INSTRUCTIONS = (
    "Capture screenshots and milestone evidence for long-running agent tasks. "
    "Prefer start_session before task execution, capture_checkpoint at important "
    "state changes, and end_session to refresh the summary and return artifact paths."
)


async def _log_info(ctx: Context | None, message: str) -> None:
    if ctx is None or getattr(ctx, "_request_context", None) is None:
        return
    await ctx.info(message)


@dataclass
class StartSessionToolResult:
    session_id: str
    task_name: str
    created_at: str
    artifacts_root: str
    status: str
    closed_at: str | None
    artifact_count: int
    metadata: dict
    session_dir: str
    timeline_path: str
    summary_path: str


@dataclass
class SessionToolResult:
    session_id: str
    task_name: str
    created_at: str
    artifacts_root: str
    status: str
    closed_at: str | None
    artifact_count: int
    metadata: dict
    session_dir: str
    timeline_path: str
    summary_path: str


@dataclass
class ListSessionsToolResult:
    session_count: int
    sessions: list[SessionToolResult]


@dataclass
class CaptureToolResult:
    artifact_id: str
    session_id: str
    artifact_type: str
    created_at: str
    label: str
    reason: str
    path: str
    step: str | None
    target: str
    tags: list[str]
    source_artifact_id: str | None
    redactions: list[dict]
    artifact_count: int


@dataclass
class ListArtifactsToolResult:
    session_dir: str
    artifact_count: int
    artifacts: list[ArtifactRecord]


@dataclass
class EndSessionToolResult:
    session_id: str
    task_name: str
    created_at: str
    artifacts_root: str
    status: str
    closed_at: str | None
    artifact_count: int
    metadata: dict
    summary_path: str
    artifacts: list[ArtifactRecord]


@dataclass
class StartRecordingToolResult:
    recording_id: str
    session_id: str
    started_at: str
    label: str
    reason: str
    path: str
    pid: int
    status: str
    step: str | None
    target: str
    tags: list[str]


@dataclass
class RecordingStatusToolResult:
    session_id: str
    active: bool
    recording: dict | None


@dataclass
class StopRecordingToolResult:
    recording: dict
    artifact: ArtifactRecord
    artifact_count: int


@dataclass
class ArtifactUpdateToolResult:
    artifact: ArtifactRecord


@dataclass
class ArtifactComparisonToolResult:
    from_artifact_id: str
    to_artifact_id: str
    same_artifact_type: bool
    from_label: str
    to_label: str
    from_path: str
    to_path: str
    from_size: int | None
    to_size: int | None
    size_delta: int | None
    hash_changed: bool | None
    label_changed: bool
    reason_changed: bool
    step_changed: bool
    target_changed: bool
    tags_changed: bool
    source_artifact_changed: bool
    redactions_changed: bool
    notes_changed: bool
    ocr_changed: bool
    verdict: str
    changed_fields: list[str]
    review_focus: list[str]
    from_ocr_preview: str | None
    to_ocr_preview: str | None
    summary: str


def _to_start_session_tool_result(result) -> StartSessionToolResult:
    session = result.session
    return StartSessionToolResult(
        session_id=session.session_id,
        task_name=session.task_name,
        created_at=session.created_at,
        artifacts_root=session.artifacts_root,
        status=session.status,
        closed_at=session.closed_at,
        artifact_count=session.artifact_count,
        metadata=session.metadata,
        session_dir=str(result.layout.session_dir),
        timeline_path=str(result.layout.timeline_path),
        summary_path=str(result.layout.summary_path),
    )


def _to_session_tool_result(result) -> SessionToolResult:
    session = result.session
    return SessionToolResult(
        session_id=session.session_id,
        task_name=session.task_name,
        created_at=session.created_at,
        artifacts_root=session.artifacts_root,
        status=session.status,
        closed_at=session.closed_at,
        artifact_count=session.artifact_count,
        metadata=session.metadata,
        session_dir=str(result.layout.session_dir),
        timeline_path=str(result.layout.timeline_path),
        summary_path=str(result.layout.summary_path),
    )


def _to_list_sessions_tool_result(result) -> ListSessionsToolResult:
    sessions = [_to_session_tool_result(session) for session in result.sessions]
    return ListSessionsToolResult(
        session_count=len(sessions),
        sessions=sessions,
    )


def _to_capture_tool_result(result) -> CaptureToolResult:
    artifact = result.artifact
    return CaptureToolResult(
        artifact_id=artifact.artifact_id,
        session_id=artifact.session_id,
        artifact_type=artifact.artifact_type,
        created_at=artifact.created_at,
        label=artifact.label,
        reason=artifact.reason,
        path=artifact.path,
        step=artifact.step,
        target=artifact.target,
        tags=artifact.tags,
        source_artifact_id=artifact.source_artifact_id,
        redactions=artifact.redactions,
        artifact_count=result.session.artifact_count,
    )


def _to_end_session_tool_result(result) -> EndSessionToolResult:
    session = result.session
    return EndSessionToolResult(
        session_id=session.session_id,
        task_name=session.task_name,
        created_at=session.created_at,
        artifacts_root=session.artifacts_root,
        status=session.status,
        closed_at=session.closed_at,
        artifact_count=session.artifact_count,
        metadata=session.metadata,
        summary_path=result.summary_path,
        artifacts=result.artifacts,
    )


def _to_start_recording_tool_result(result) -> StartRecordingToolResult:
    recording = result.recording
    return StartRecordingToolResult(
        recording_id=recording.recording_id,
        session_id=recording.session_id,
        started_at=recording.started_at,
        label=recording.label,
        reason=recording.reason,
        path=recording.path,
        pid=recording.pid,
        status=recording.status,
        step=recording.step,
        target=recording.target,
        tags=recording.tags,
    )


def _to_recording_status_tool_result(result) -> RecordingStatusToolResult:
    return RecordingStatusToolResult(
        session_id=result.session_id,
        active=result.active,
        recording=result.recording.to_dict() if result.recording is not None else None,
    )


def _to_stop_recording_tool_result(result) -> StopRecordingToolResult:
    return StopRecordingToolResult(
        recording=result.recording.to_dict(),
        artifact=result.artifact,
        artifact_count=result.session.artifact_count,
    )


def _to_artifact_update_tool_result(result) -> ArtifactUpdateToolResult:
    return ArtifactUpdateToolResult(artifact=result.artifact)


def _to_artifact_comparison_tool_result(result) -> ArtifactComparisonToolResult:
    comparison = result.comparison
    return ArtifactComparisonToolResult(
        from_artifact_id=comparison.from_artifact_id,
        to_artifact_id=comparison.to_artifact_id,
        same_artifact_type=comparison.same_artifact_type,
        from_label=comparison.from_label,
        to_label=comparison.to_label,
        from_path=comparison.from_path,
        to_path=comparison.to_path,
        from_size=comparison.from_size,
        to_size=comparison.to_size,
        size_delta=comparison.size_delta,
        hash_changed=comparison.hash_changed,
        label_changed=comparison.label_changed,
        reason_changed=comparison.reason_changed,
        step_changed=comparison.step_changed,
        target_changed=comparison.target_changed,
        tags_changed=comparison.tags_changed,
        source_artifact_changed=comparison.source_artifact_changed,
        redactions_changed=comparison.redactions_changed,
        notes_changed=comparison.notes_changed,
        ocr_changed=comparison.ocr_changed,
        verdict=comparison.verdict,
        changed_fields=comparison.changed_fields,
        review_focus=comparison.review_focus,
        from_ocr_preview=comparison.from_ocr_preview,
        to_ocr_preview=comparison.to_ocr_preview,
        summary=comparison.summary,
    )


def create_mcp_server(
    base_dir: Path,
    config: AppConfig | None = None,
    service: TaskEvidenceService | None = None,
) -> FastMCP:
    config = config or AppConfig()
    service = service or TaskEvidenceService(base_dir, config)
    mcp = FastMCP(
        name="agent-evidence-mcp",
        instructions=SERVER_INSTRUCTIONS,
        dependencies=["mcp"],
    )

    @mcp.tool(
        name="start_session",
        description="Create a new evidence session for a long-running task.",
        structured_output=True,
    )
    async def start_session(
        task_name: str,
        metadata: dict | None = None,
        ctx: Context | None = None,
    ) -> StartSessionToolResult:
        await _log_info(ctx, f"Starting evidence session for {task_name}")
        result = service.start_session(task_name=task_name, metadata=metadata)
        return _to_start_session_tool_result(result)

    @mcp.tool(
        name="list_sessions",
        description="List evidence sessions, newest first. Optionally filter by status or limit the number returned.",
        structured_output=True,
    )
    async def list_sessions(
        status: str | None = None,
        limit: int | None = None,
        ctx: Context | None = None,
    ) -> ListSessionsToolResult:
        await _log_info(ctx, "Listing evidence sessions")
        result = service.list_sessions(status=status, limit=limit)
        return _to_list_sessions_tool_result(result)

    @mcp.tool(
        name="get_session",
        description="Load a session by session id or session directory path.",
        structured_output=True,
    )
    async def get_session(
        session_ref: str,
        ctx: Context | None = None,
    ) -> SessionToolResult:
        await _log_info(ctx, f"Loading evidence session {session_ref}")
        result = service.get_session(session_ref)
        return _to_session_tool_result(result)

    @mcp.tool(
        name="get_latest_session",
        description="Return the newest evidence session, optionally filtered by status.",
        structured_output=True,
    )
    async def get_latest_session(
        status: str | None = None,
        ctx: Context | None = None,
    ) -> SessionToolResult:
        await _log_info(ctx, "Loading latest evidence session")
        result = service.get_latest_session(status=status)
        return _to_session_tool_result(result)

    @mcp.resource(
        "agent-evidence://sessions",
        name="sessions",
        description="JSON index of evidence sessions, newest first.",
        mime_type="application/json",
    )
    def sessions_resource() -> str:
        return json.dumps(service.list_sessions().to_dict(), indent=2, ensure_ascii=False)

    @mcp.resource(
        "agent-evidence://latest/summary",
        name="latest_session_summary",
        description="Markdown summary for the newest evidence session.",
        mime_type="text/markdown",
    )
    def latest_session_summary_resource() -> str:
        return service.read_latest_session_summary()

    @mcp.resource(
        "agent-evidence://latest/artifacts",
        name="latest_session_artifacts",
        description="JSON artifact list for the newest evidence session.",
        mime_type="application/json",
    )
    def latest_session_artifacts_resource() -> str:
        latest = service.get_latest_session()
        payload = service.get_session_artifacts_payload(latest.session.session_id)
        return json.dumps(payload, indent=2, ensure_ascii=False)

    @mcp.resource(
        "agent-evidence://sessions/{session_id}/summary",
        name="session_summary",
        description="Markdown summary for a session id.",
        mime_type="text/markdown",
    )
    def session_summary_resource(session_id: str) -> str:
        return service.read_session_summary(session_id)

    @mcp.resource(
        "agent-evidence://sessions/{session_id}/artifacts",
        name="session_artifacts",
        description="JSON artifact list for a session id.",
        mime_type="application/json",
    )
    def session_artifacts_resource(session_id: str) -> str:
        payload = service.get_session_artifacts_payload(session_id)
        return json.dumps(payload, indent=2, ensure_ascii=False)

    @mcp.prompt(
        name="evidence_capture_plan",
        description="Prompt an agent to use Agent Evidence MCP during a long-running task.",
    )
    def evidence_capture_plan(task_name: str = "the task") -> str:
        return (
            f"Use agent-evidence MCP while working on {task_name}.\n"
            "Start with `start_session` and keep the returned `session_dir`.\n"
            "Capture checkpoints at major state changes with `capture_checkpoint`.\n"
            "Capture an extra checkpoint for errors, warnings, or unexpected UI states.\n"
            "Prefer screenshots over recordings unless motion or timing matters.\n"
            "Use `get_latest_session` or `list_sessions` if you need to recover session context.\n"
            "End with `end_session`, then report the summary path and key artifact paths."
        )

    @mcp.prompt(
        name="evidence_final_review",
        description="Prompt an agent to review a completed evidence session before handoff.",
    )
    def evidence_final_review(session_id: str = "latest") -> str:
        if session_id == "latest":
            summary_uri = "agent-evidence://latest/summary"
            artifacts_uri = "agent-evidence://latest/artifacts"
        else:
            summary_uri = f"agent-evidence://sessions/{session_id}/summary"
            artifacts_uri = f"agent-evidence://sessions/{session_id}/artifacts"
        return (
            "Review the evidence session before final handoff.\n"
            f"Read `{summary_uri}` and `{artifacts_uri}`.\n"
            "Summarize the completed task, the most important checkpoints, any recordings, "
            "and any residual risks or missing evidence. Include local artifact paths."
        )

    @mcp.tool(
        name="capture_checkpoint",
        description="Capture a screenshot checkpoint for a session at an important milestone.",
        structured_output=True,
    )
    async def capture_checkpoint(
        session_dir: str,
        label: str,
        reason: str,
        step: str | None = None,
        target: str = "desktop",
        tags: list[str] | None = None,
        ctx: Context | None = None,
    ) -> CaptureToolResult:
        await _log_info(ctx, f"Capturing checkpoint {label} for {session_dir}")
        result = service.capture_checkpoint(
            session_dir=Path(session_dir),
            label=label,
            reason=reason,
            step=step,
            target=target,
            tags=tags,
        )
        return _to_capture_tool_result(result)

    @mcp.tool(
        name="capture_screenshot",
        description="Capture a raw screenshot artifact for a session.",
        structured_output=True,
    )
    async def capture_screenshot(
        session_dir: str,
        label: str,
        reason: str = "Manual screenshot capture.",
        step: str | None = None,
        target: str = "desktop",
        tags: list[str] | None = None,
        ctx: Context | None = None,
    ) -> CaptureToolResult:
        await _log_info(ctx, f"Capturing raw screenshot {label} for {session_dir}")
        result = service.capture_screenshot(
            session_dir=Path(session_dir),
            label=label,
            reason=reason,
            step=step,
            target=target,
            tags=tags,
        )
        return _to_capture_tool_result(result)

    @mcp.tool(
        name="list_artifacts",
        description="List saved artifacts for an existing evidence session.",
        structured_output=True,
    )
    async def list_artifacts(
        session_dir: str,
        ctx: Context | None = None,
    ) -> ListArtifactsToolResult:
        artifacts = service.list_artifacts(Path(session_dir))
        await _log_info(ctx, f"Listing {len(artifacts)} artifacts for {session_dir}")
        return ListArtifactsToolResult(
            session_dir=str(Path(session_dir).resolve()),
            artifact_count=len(artifacts),
            artifacts=artifacts,
        )

    @mcp.tool(
        name="start_recording",
        description="Start a short recording for an existing session.",
        structured_output=True,
    )
    async def start_recording(
        session_dir: str,
        label: str,
        reason: str,
        step: str | None = None,
        target: str = "desktop",
        tags: list[str] | None = None,
        ctx: Context | None = None,
    ) -> StartRecordingToolResult:
        await _log_info(ctx, f"Starting recording {label} for {session_dir}")
        result = service.start_recording(
            session_dir=Path(session_dir),
            label=label,
            reason=reason,
            step=step,
            target=target,
            tags=tags,
        )
        return _to_start_recording_tool_result(result)

    @mcp.tool(
        name="get_recording_status",
        description="Report whether a session currently has an active recording.",
        structured_output=True,
    )
    async def get_recording_status(
        session_dir: str,
        ctx: Context | None = None,
    ) -> RecordingStatusToolResult:
        await _log_info(ctx, f"Checking recording status for {session_dir}")
        result = service.get_recording_status(Path(session_dir))
        return _to_recording_status_tool_result(result)

    @mcp.tool(
        name="stop_recording",
        description="Stop the active recording for a session and save it as an artifact.",
        structured_output=True,
    )
    async def stop_recording(
        session_dir: str,
        ctx: Context | None = None,
    ) -> StopRecordingToolResult:
        await _log_info(ctx, f"Stopping recording for {session_dir}")
        result = service.stop_recording(Path(session_dir))
        return _to_stop_recording_tool_result(result)

    @mcp.tool(
        name="end_session",
        description="Mark a session as completed and refresh its summary.",
        structured_output=True,
    )
    async def end_session(
        session_dir: str,
        ctx: Context | None = None,
    ) -> EndSessionToolResult:
        await _log_info(ctx, f"Ending session {session_dir}")
        result = service.end_session(Path(session_dir))
        return _to_end_session_tool_result(result)

    @mcp.tool(
        name="attach_note",
        description="Attach a human-readable note to an existing artifact.",
        structured_output=True,
    )
    async def attach_note(
        session_dir: str,
        artifact_id: str,
        note: str,
        ctx: Context | None = None,
    ) -> ArtifactUpdateToolResult:
        await _log_info(ctx, f"Attaching note to {artifact_id}")
        result = service.attach_note(Path(session_dir), artifact_id, note)
        return _to_artifact_update_tool_result(result)

    @mcp.tool(
        name="ocr_artifact",
        description="Attach OCR text to an existing artifact for review and searchability.",
        structured_output=True,
    )
    async def ocr_artifact(
        session_dir: str,
        artifact_id: str,
        text: str | None = None,
        ctx: Context | None = None,
    ) -> ArtifactUpdateToolResult:
        await _log_info(ctx, f"Storing OCR text for {artifact_id}")
        result = service.ocr_artifact(Path(session_dir), artifact_id, text)
        return _to_artifact_update_tool_result(result)

    @mcp.tool(
        name="redact_artifact",
        description="Create a new redacted screenshot artifact from an existing screenshot using one or more rectangular regions.",
        structured_output=True,
    )
    async def redact_artifact(
        session_dir: str,
        artifact_id: str,
        label: str,
        regions: list[dict],
        color: str = "#000000",
        reason: str | None = None,
        step: str | None = None,
        tags: list[str] | None = None,
        ctx: Context | None = None,
    ) -> CaptureToolResult:
        await _log_info(ctx, f"Creating redacted artifact from {artifact_id}")
        result = service.redact_artifact(
            Path(session_dir),
            artifact_id,
            label,
            regions,
            color=color,
            reason=reason,
            step=step,
            tags=tags,
        )
        return _to_capture_tool_result(result)

    @mcp.tool(
        name="compare_artifacts",
        description="Compare two artifacts from the same session and return a review-oriented verdict, changed fields, and follow-up guidance.",
        structured_output=True,
    )
    async def compare_artifacts_tool(
        session_dir: str,
        from_artifact_id: str,
        to_artifact_id: str,
        ctx: Context | None = None,
    ) -> ArtifactComparisonToolResult:
        await _log_info(ctx, f"Comparing artifacts {from_artifact_id} -> {to_artifact_id}")
        result = service.compare_artifacts(
            Path(session_dir),
            from_artifact_id,
            to_artifact_id,
        )
        return _to_artifact_comparison_tool_result(result)

    @mcp.tool(
        name="compare_latest_artifacts",
        description="Compare the two most recent comparable artifacts in a session, optionally filtered by artifact type.",
        structured_output=True,
    )
    async def compare_latest_artifacts_tool(
        session_dir: str,
        artifact_type: str | None = None,
        ctx: Context | None = None,
    ) -> ArtifactComparisonToolResult:
        await _log_info(ctx, f"Comparing latest artifacts in {session_dir}")
        result = service.compare_latest_artifacts(
            Path(session_dir),
            artifact_type=artifact_type,
        )
        return _to_artifact_comparison_tool_result(result)

    return mcp


def run_server(
    base_dir: Path,
    config: AppConfig | None = None,
    transport: str = "stdio",
) -> int:
    """Run the MCP server using the requested transport."""

    server = create_mcp_server(base_dir=base_dir, config=config)
    server.run(transport=transport)
    return 0
