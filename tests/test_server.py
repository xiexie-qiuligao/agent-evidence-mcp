from __future__ import annotations

import asyncio
from pathlib import Path

from task_evidence_mcp.capture import ScreenshotBackend
from task_evidence_mcp.config import AppConfig
from task_evidence_mcp.ocr import OCRBackend
from task_evidence_mcp.redaction import RedactionBackend, RedactionRegion
from task_evidence_mcp.recording import RecordingBackend, RecordingHandle
from task_evidence_mcp.server import create_mcp_server
from task_evidence_mcp.service import TaskEvidenceService


class FakeScreenshotBackend(ScreenshotBackend):
    def capture_full_screen(self, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(f"fake-image:{destination.name}".encode("utf-8"))


class FakeRecordingBackend(RecordingBackend):
    def __init__(self) -> None:
        self.pid = 1000

    def is_available(self) -> bool:
        return True

    def start_full_screen_recording(self, destination: Path, frame_rate: int) -> RecordingHandle:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"fake-video")
        self.pid += 1
        return RecordingHandle(pid=self.pid)

    def stop_recording(self, handle: RecordingHandle) -> None:
        return None


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
        destination.write_text(f"redacted:{source.name}:{len(regions)}:{color}", encoding="utf-8")


def _structured_payload(result: tuple) -> dict:
    _, payload = result
    return payload


def test_server_registers_expected_tools(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    server = create_mcp_server(tmp_path, service=service)

    async def main() -> list[str]:
        tools = await server.list_tools()
        return sorted(tool.name for tool in tools)

    tool_names = asyncio.run(main())
    assert tool_names == [
        "attach_note",
        "capture_checkpoint",
        "capture_screenshot",
        "compare_artifacts",
        "compare_latest_artifacts",
        "end_session",
        "get_recording_status",
        "list_artifacts",
        "ocr_artifact",
        "redact_artifact",
        "start_recording",
        "start_session",
        "stop_recording",
    ]


def test_server_tools_drive_session_flow(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(recording_enabled=True),
        screenshot_backend=FakeScreenshotBackend(),
        recording_backend=FakeRecordingBackend(),
    )
    server = create_mcp_server(tmp_path, service=service)

    async def main() -> tuple[dict, dict, dict, dict]:
        start_result = await server.call_tool("start_session", {"task_name": "Server Flow"})
        start_payload = _structured_payload(start_result)
        capture_result = await server.call_tool(
            "capture_checkpoint",
            {
                "session_dir": start_payload["session_dir"],
                "label": "page-loaded",
                "reason": "The target page is ready.",
                "step": "step-01",
            },
        )
        capture_payload = _structured_payload(capture_result)
        list_result = await server.call_tool(
            "list_artifacts",
            {"session_dir": start_payload["session_dir"]},
        )
        list_payload = _structured_payload(list_result)
        end_result = await server.call_tool(
            "end_session",
            {"session_dir": start_payload["session_dir"]},
        )
        end_payload = _structured_payload(end_result)
        return start_payload, capture_payload, list_payload, end_payload

    start_payload, capture_payload, list_payload, end_payload = asyncio.run(main())

    assert start_payload["task_name"] == "Server Flow"
    assert capture_payload["label"] == "page-loaded"
    assert capture_payload["artifact_count"] == 1
    assert list_payload["artifact_count"] == 1
    assert list_payload["artifacts"][0]["label"] == "page-loaded"
    assert end_payload["status"] == "completed"


def test_server_recording_tools_drive_round_trip(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(recording_enabled=True),
        screenshot_backend=FakeScreenshotBackend(),
        recording_backend=FakeRecordingBackend(),
    )
    server = create_mcp_server(tmp_path, service=service)

    async def main() -> tuple[dict, dict, dict, dict]:
        start_result = await server.call_tool("start_session", {"task_name": "Recording Flow"})
        _, start_payload = start_result
        begin_result = await server.call_tool(
            "start_recording",
            {
                "session_dir": start_payload["session_dir"],
                "label": "drag-flow",
                "reason": "Need motion evidence.",
            },
        )
        _, begin_payload = begin_result
        status_result = await server.call_tool(
            "get_recording_status",
            {"session_dir": start_payload["session_dir"]},
        )
        _, status_payload = status_result
        stop_result = await server.call_tool(
            "stop_recording",
            {"session_dir": start_payload["session_dir"]},
        )
        _, stop_payload = stop_result
        return begin_payload, status_payload, stop_payload, start_payload

    begin_payload, status_payload, stop_payload, start_payload = asyncio.run(main())

    assert begin_payload["label"] == "drag-flow"
    assert status_payload["active"] is True
    assert stop_payload["artifact"]["artifact_type"] == "recording"
    assert stop_payload["artifact_count"] == 1
    assert stop_payload["artifact"]["session_id"] == start_payload["session_id"]


def test_server_rejects_ending_session_with_active_recording(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(recording_enabled=True),
        screenshot_backend=FakeScreenshotBackend(),
        recording_backend=FakeRecordingBackend(),
    )
    server = create_mcp_server(tmp_path, service=service)

    async def main() -> None:
        start_result = await server.call_tool("start_session", {"task_name": "Active Recording End"})
        _, start_payload = start_result
        await server.call_tool(
            "start_recording",
            {
                "session_dir": start_payload["session_dir"],
                "label": "active",
                "reason": "Still running",
            },
        )
        await server.call_tool("end_session", {"session_dir": start_payload["session_dir"]})

    try:
        asyncio.run(main())
    except Exception as exc:
        assert "Stop the recording first" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected end_session to fail while recording is active.")


def test_server_can_attach_note_and_ocr_text(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
        ocr_backend=FakeOCRBackend(),
    )
    server = create_mcp_server(tmp_path, service=service)

    async def main() -> tuple[dict, dict]:
        start_result = await server.call_tool("start_session", {"task_name": "OCR Tool Flow"})
        _, start_payload = start_result
        capture_result = await server.call_tool(
            "capture_checkpoint",
            {
                "session_dir": start_payload["session_dir"],
                "label": "dialog",
                "reason": "Need OCR",
            },
        )
        _, capture_payload = capture_result
        note_result = await server.call_tool(
            "attach_note",
            {
                "session_dir": start_payload["session_dir"],
                "artifact_id": capture_payload["artifact_id"],
                "note": "Review this dialog carefully.",
            },
        )
        _, note_payload = note_result
        ocr_result = await server.call_tool(
            "ocr_artifact",
            {
                "session_dir": start_payload["session_dir"],
                "artifact_id": capture_payload["artifact_id"],
                "text": "Sample OCR text",
            },
        )
        _, ocr_payload = ocr_result
        return note_payload, ocr_payload

    note_payload, ocr_payload = asyncio.run(main())

    assert note_payload["artifact"]["notes"] == ["Review this dialog carefully."]
    assert ocr_payload["artifact"]["ocr_text"] == "Sample OCR text"


def test_server_can_run_automatic_ocr(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(ocr_enabled=True),
        screenshot_backend=FakeScreenshotBackend(),
        ocr_backend=FakeOCRBackend(),
    )
    server = create_mcp_server(tmp_path, service=service)

    async def main() -> dict:
        start_result = await server.call_tool("start_session", {"task_name": "OCR Auto Flow"})
        _, start_payload = start_result
        capture_result = await server.call_tool(
            "capture_checkpoint",
            {
                "session_dir": start_payload["session_dir"],
                "label": "dialog",
                "reason": "Need OCR automatically",
            },
        )
        _, capture_payload = capture_result
        ocr_result = await server.call_tool(
            "ocr_artifact",
            {
                "session_dir": start_payload["session_dir"],
                "artifact_id": capture_payload["artifact_id"],
            },
        )
        _, ocr_payload = ocr_result
        return ocr_payload

    ocr_payload = asyncio.run(main())

    assert ocr_payload["artifact"]["ocr_text"].startswith("OCR::")


def test_server_can_create_redacted_artifact(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
        redaction_backend=FakeRedactionBackend(),
    )
    server = create_mcp_server(tmp_path, service=service)

    async def main() -> dict:
        start_result = await server.call_tool("start_session", {"task_name": "Redaction Tool Flow"})
        _, start_payload = start_result
        capture_result = await server.call_tool(
            "capture_checkpoint",
            {
                "session_dir": start_payload["session_dir"],
                "label": "secret-screen",
                "reason": "Contains sensitive content",
            },
        )
        _, capture_payload = capture_result
        redact_result = await server.call_tool(
            "redact_artifact",
            {
                "session_dir": start_payload["session_dir"],
                "artifact_id": capture_payload["artifact_id"],
                "label": "shareable-screen",
                "regions": [{"x": 4, "y": 5, "width": 20, "height": 15}],
            },
        )
        _, redact_payload = redact_result
        return redact_payload

    payload = asyncio.run(main())

    assert payload["source_artifact_id"] is not None
    assert payload["redactions"] == [{"x": 4, "y": 5, "width": 20, "height": 15}]


def test_server_can_compare_artifacts(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
        ocr_backend=FakeOCRBackend(),
    )
    server = create_mcp_server(tmp_path, service=service)

    async def main() -> dict:
        start_result = await server.call_tool("start_session", {"task_name": "Compare Tool Flow"})
        _, start_payload = start_result
        first = await server.call_tool(
            "capture_checkpoint",
            {
                "session_dir": start_payload["session_dir"],
                "label": "first",
                "reason": "First state",
            },
        )
        _, first_payload = first
        second = await server.call_tool(
            "capture_checkpoint",
            {
                "session_dir": start_payload["session_dir"],
                "label": "second",
                "reason": "Second state",
            },
        )
        _, second_payload = second
        await server.call_tool(
            "ocr_artifact",
            {
                "session_dir": start_payload["session_dir"],
                "artifact_id": second_payload["artifact_id"],
                "text": "Different OCR",
            },
        )
        result = await server.call_tool(
            "compare_artifacts",
            {
                "session_dir": start_payload["session_dir"],
                "from_artifact_id": first_payload["artifact_id"],
                "to_artifact_id": second_payload["artifact_id"],
            },
        )
        _, payload = result
        return payload

    payload = asyncio.run(main())

    assert payload["same_artifact_type"] is True
    assert payload["verdict"] == "content_changed"
    assert "label" in payload["changed_fields"]
    assert payload["ocr_changed"] is True
    assert payload["review_focus"]


def test_server_can_compare_latest_artifacts(tmp_path: Path) -> None:
    service = TaskEvidenceService(
        tmp_path,
        AppConfig(),
        screenshot_backend=FakeScreenshotBackend(),
    )
    server = create_mcp_server(tmp_path, service=service)

    async def main() -> dict:
        start_result = await server.call_tool("start_session", {"task_name": "Latest Compare Flow"})
        _, start_payload = start_result
        await server.call_tool(
            "capture_checkpoint",
            {
                "session_dir": start_payload["session_dir"],
                "label": "before",
                "reason": "Before state",
            },
        )
        second = await server.call_tool(
            "capture_checkpoint",
            {
                "session_dir": start_payload["session_dir"],
                "label": "after",
                "reason": "After state",
            },
        )
        _, second_payload = second
        result = await server.call_tool(
            "compare_latest_artifacts",
            {
                "session_dir": start_payload["session_dir"],
                "artifact_type": "screenshot",
            },
        )
        _, payload = result
        assert payload["to_artifact_id"] == second_payload["artifact_id"]
        return payload

    payload = asyncio.run(main())

    assert payload["same_artifact_type"] is True
    assert payload["verdict"] == "content_changed"
