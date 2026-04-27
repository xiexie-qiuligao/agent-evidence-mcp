from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .artifacts import ArtifactReviewError
from .capture import CaptureError
from .config import DEFAULT_CONFIG, load_config
from .ocr import OCRError, OCRUnavailableError as OCRBackendUnavailableError
from .redaction import RedactionError
from .recording import RecordingError, RecordingUnavailableError
from .service import TaskEvidenceService
from .server import run_server
from .storage import SessionNotFoundError

DEFAULT_CONFIG_PATH = Path("agent-evidence-mcp.toml")


def parse_region_arg(value: str) -> dict[str, int]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("Region must use x,y,width,height.")
    try:
        x, y, width, height = (int(part) for part in parts)
    except ValueError as exc:  # pragma: no cover - argparse handles the user path
        raise argparse.ArgumentTypeError("Region values must be integers.") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("Region width and height must be positive.")
    return {"x": x, "y": y, "width": width, "height": height}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-evidence-mcp",
        description="CLI for the Agent Evidence MCP project.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init",
        help="Write a starter configuration file for local development.",
    )
    init_parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to write the generated TOML config.",
    )

    subparsers.add_parser(
        "show-defaults",
        help="Print the default configuration template.",
    )

    serve_parser = subparsers.add_parser(
        "serve",
        help="Run the MCP server.",
    )
    serve_parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport to use for the MCP server.",
    )
    serve_parser.add_argument(
        "--cwd",
        type=Path,
        default=Path.cwd(),
        help="Workspace directory used for artifact storage.",
    )
    serve_parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Optional TOML config path. Defaults to agent-evidence-mcp.toml if present.",
    )

    start_session_parser = subparsers.add_parser(
        "start-session",
        help="Create a new evidence session for a long-running task.",
    )
    start_session_parser.add_argument(
        "task_name",
        help="Human-readable task name for the session.",
    )

    list_sessions_parser = subparsers.add_parser(
        "list-sessions",
        help="List evidence sessions, newest first.",
    )
    list_sessions_parser.add_argument(
        "--status",
        default=None,
        help="Optional session status filter, such as active or completed.",
    )
    list_sessions_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of sessions to return.",
    )

    get_session_parser = subparsers.add_parser(
        "get-session",
        help="Load a session by session id or session directory path.",
    )
    get_session_parser.add_argument(
        "session_ref",
        help="Session id or path to the session directory.",
    )

    latest_session_parser = subparsers.add_parser(
        "latest-session",
        help="Return the newest evidence session.",
    )
    latest_session_parser.add_argument(
        "--status",
        default=None,
        help="Optional session status filter, such as active or completed.",
    )

    capture_parser = subparsers.add_parser(
        "capture-checkpoint",
        help="Capture a screenshot checkpoint for an existing session.",
    )
    capture_parser.add_argument("session_dir", type=Path, help="Path to the session directory.")
    capture_parser.add_argument("label", help="Short label for the checkpoint.")
    capture_parser.add_argument("reason", help="Why this checkpoint matters.")
    capture_parser.add_argument(
        "--step",
        default=None,
        help="Optional step identifier for the checkpoint.",
    )
    capture_parser.add_argument(
        "--target",
        default="desktop",
        help="Capture target label stored in metadata.",
    )
    capture_parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        default=[],
        help="Optional tag. Repeat to add multiple tags.",
    )

    start_recording_parser = subparsers.add_parser(
        "start-recording",
        help="Start a short recording for an existing session.",
    )
    start_recording_parser.add_argument("session_dir", type=Path, help="Path to the session directory.")
    start_recording_parser.add_argument("label", help="Short label for the recording.")
    start_recording_parser.add_argument("reason", help="Why this recording matters.")
    start_recording_parser.add_argument(
        "--step",
        default=None,
        help="Optional step identifier for the recording.",
    )
    start_recording_parser.add_argument(
        "--target",
        default="desktop",
        help="Capture target label stored in metadata.",
    )
    start_recording_parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        default=[],
        help="Optional tag. Repeat to add multiple tags.",
    )

    status_recording_parser = subparsers.add_parser(
        "recording-status",
        help="Show the active recording state for a session.",
    )
    status_recording_parser.add_argument(
        "session_dir",
        type=Path,
        help="Path to the session directory.",
    )

    stop_recording_parser = subparsers.add_parser(
        "stop-recording",
        help="Stop the active recording for a session and save it as an artifact.",
    )
    stop_recording_parser.add_argument(
        "session_dir",
        type=Path,
        help="Path to the session directory.",
    )

    screenshot_parser = subparsers.add_parser(
        "capture-screenshot",
        help="Capture a raw screenshot artifact for an existing session.",
    )
    screenshot_parser.add_argument("session_dir", type=Path, help="Path to the session directory.")
    screenshot_parser.add_argument("label", help="Short label for the screenshot.")
    screenshot_parser.add_argument(
        "--reason",
        default="Manual screenshot capture.",
        help="Optional reason stored alongside the screenshot.",
    )
    screenshot_parser.add_argument(
        "--step",
        default=None,
        help="Optional step identifier for the screenshot.",
    )
    screenshot_parser.add_argument(
        "--target",
        default="desktop",
        help="Capture target label stored in metadata.",
    )
    screenshot_parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        default=[],
        help="Optional tag. Repeat to add multiple tags.",
    )

    list_parser = subparsers.add_parser(
        "list-artifacts",
        help="List captured artifacts for a session.",
    )
    list_parser.add_argument("session_dir", type=Path, help="Path to the session directory.")

    end_parser = subparsers.add_parser(
        "end-session",
        help="Mark a session as completed and refresh its summary.",
    )
    end_parser.add_argument("session_dir", type=Path, help="Path to the session directory.")

    note_parser = subparsers.add_parser(
        "attach-note",
        help="Attach a human-readable note to an existing artifact.",
    )
    note_parser.add_argument("session_dir", type=Path, help="Path to the session directory.")
    note_parser.add_argument("artifact_id", help="Artifact id to annotate.")
    note_parser.add_argument("note", help="Note text to attach.")

    ocr_parser = subparsers.add_parser(
        "ocr-artifact",
        help="Attach OCR text to an existing artifact, either manually or via the configured OCR backend.",
    )
    ocr_parser.add_argument("session_dir", type=Path, help="Path to the session directory.")
    ocr_parser.add_argument("artifact_id", help="Artifact id to enrich.")
    ocr_parser.add_argument(
        "text",
        nargs="?",
        default=None,
        help="Optional OCR text to store manually. If omitted, the configured OCR backend is used.",
    )

    redact_parser = subparsers.add_parser(
        "redact-artifact",
        help="Create a redacted screenshot artifact from an existing screenshot.",
    )
    redact_parser.add_argument("session_dir", type=Path, help="Path to the session directory.")
    redact_parser.add_argument("artifact_id", help="Source screenshot artifact id.")
    redact_parser.add_argument("label", help="Label for the redacted artifact.")
    redact_parser.add_argument(
        "--region",
        action="append",
        dest="regions",
        required=True,
        type=parse_region_arg,
        help="Rectangle to redact in x,y,width,height form. Repeat for multiple regions.",
    )
    redact_parser.add_argument(
        "--color",
        default="#000000",
        help="Fill color for redaction rectangles, such as #000000.",
    )
    redact_parser.add_argument(
        "--reason",
        default=None,
        help="Optional reason stored alongside the redacted artifact.",
    )
    redact_parser.add_argument(
        "--step",
        default=None,
        help="Optional step identifier for the redacted artifact. Defaults to the source step.",
    )
    redact_parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        default=[],
        help="Optional tag. Repeat to add multiple tags.",
    )

    compare_parser = subparsers.add_parser(
        "compare-artifacts",
        help="Compare two artifacts from the same session.",
    )
    compare_parser.add_argument("session_dir", type=Path, help="Path to the session directory.")
    compare_parser.add_argument("from_artifact_id", help="Baseline artifact id.")
    compare_parser.add_argument("to_artifact_id", help="Newer artifact id.")

    compare_latest_parser = subparsers.add_parser(
        "compare-latest-artifacts",
        help="Compare the two most recent comparable artifacts in a session.",
    )
    compare_latest_parser.add_argument("session_dir", type=Path, help="Path to the session directory.")
    compare_latest_parser.add_argument(
        "--artifact-type",
        default=None,
        help="Optional artifact type filter such as screenshot or recording. Defaults to the latest artifact type in the session.",
    )

    return parser


def cmd_init(path: Path) -> int:
    if path.exists():
        print(f"Refusing to overwrite existing file: {path}")
        return 1

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(DEFAULT_CONFIG.to_toml(), encoding="utf-8")
    print(f"Wrote config to {path.resolve()}")
    return 0


def print_json(payload: dict | list[dict]) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def print_error(message: str) -> None:
    print(message, file=sys.stderr)


def build_service(config_path: Path | None = None, cwd: Path | None = None) -> TaskEvidenceService:
    base_dir = (cwd or Path.cwd()).resolve()
    config = load_config(config_path)
    return TaskEvidenceService(base_dir, config)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        return cmd_init(args.path)
    if args.command == "show-defaults":
        print(DEFAULT_CONFIG.to_toml(), end="")
        return 0
    if args.command == "serve":
        config_path = args.config if args.config.exists() else None
        config = load_config(config_path)
        return run_server(args.cwd, config=config, transport=args.transport)

    config_path = DEFAULT_CONFIG_PATH if DEFAULT_CONFIG_PATH.exists() else None
    service = build_service(config_path=config_path)
    try:
        if args.command == "start-session":
            result = service.start_session(args.task_name)
            print_json(result.to_dict())
            return 0
        if args.command == "list-sessions":
            result = service.list_sessions(status=args.status, limit=args.limit)
            print_json(result.to_dict())
            return 0
        if args.command == "get-session":
            result = service.get_session(args.session_ref)
            print_json(result.to_dict())
            return 0
        if args.command == "latest-session":
            result = service.get_latest_session(status=args.status)
            print_json(result.to_dict())
            return 0
        if args.command == "capture-checkpoint":
            result = service.capture_checkpoint(
                args.session_dir,
                args.label,
                args.reason,
                step=args.step,
                target=args.target,
                tags=args.tags,
            )
            print_json(result.to_dict())
            return 0
        if args.command == "capture-screenshot":
            result = service.capture_screenshot(
                args.session_dir,
                args.label,
                reason=args.reason,
                step=args.step,
                target=args.target,
                tags=args.tags,
            )
            print_json(result.to_dict())
            return 0
        if args.command == "start-recording":
            result = service.start_recording(
                args.session_dir,
                args.label,
                args.reason,
                step=args.step,
                target=args.target,
                tags=args.tags,
            )
            print_json(result.to_dict())
            return 0
        if args.command == "recording-status":
            result = service.get_recording_status(args.session_dir)
            print_json(result.to_dict())
            return 0
        if args.command == "stop-recording":
            result = service.stop_recording(args.session_dir)
            print_json(result.to_dict())
            return 0
        if args.command == "list-artifacts":
            artifacts = service.list_artifacts(args.session_dir)
            print_json([artifact.to_dict() for artifact in artifacts])
            return 0
        if args.command == "end-session":
            result = service.end_session(args.session_dir)
            print_json(result.to_dict())
            return 0
        if args.command == "attach-note":
            result = service.attach_note(args.session_dir, args.artifact_id, args.note)
            print_json(result.to_dict())
            return 0
        if args.command == "ocr-artifact":
            result = service.ocr_artifact(args.session_dir, args.artifact_id, args.text)
            print_json(result.to_dict())
            return 0
        if args.command == "redact-artifact":
            result = service.redact_artifact(
                args.session_dir,
                args.artifact_id,
                args.label,
                args.regions,
                color=args.color,
                reason=args.reason,
                step=args.step,
                tags=args.tags,
            )
            print_json(result.to_dict())
            return 0
        if args.command == "compare-artifacts":
            result = service.compare_artifacts(
                args.session_dir,
                args.from_artifact_id,
                args.to_artifact_id,
            )
            print_json(result.to_dict())
            return 0
        if args.command == "compare-latest-artifacts":
            result = service.compare_latest_artifacts(
                args.session_dir,
                artifact_type=args.artifact_type,
            )
            print_json(result.to_dict())
            return 0
    except SessionNotFoundError as exc:
        print_error(f"Session error: {exc}")
        return 1
    except ArtifactReviewError as exc:
        print_error(f"Review error: {exc}")
        return 1
    except RecordingUnavailableError as exc:
        print_error(f"Recording unavailable: {exc}")
        return 1
    except RecordingError as exc:
        print_error(f"Recording error: {exc}")
        return 1
    except CaptureError as exc:
        print_error(f"Capture error: {exc}")
        return 1
    except OCRBackendUnavailableError as exc:
        print_error(f"OCR unavailable: {exc}")
        return 1
    except OCRError as exc:
        print_error(f"OCR error: {exc}")
        return 1
    except RedactionError as exc:
        print_error(f"Redaction error: {exc}")
        return 1
    except ValueError as exc:
        print_error(f"Input error: {exc}")
        return 1

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
