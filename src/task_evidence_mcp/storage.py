from __future__ import annotations

import json
from pathlib import Path

from .models import ArtifactDetails, ArtifactRecord, RecordingState, SessionRecord


class SessionNotFoundError(FileNotFoundError):
    """Raised when a requested session cannot be found on disk."""


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_session(session: SessionRecord, path: Path) -> None:
    write_json(path, session.to_dict())


def load_session(path: Path) -> SessionRecord:
    if not path.exists():
        raise SessionNotFoundError(f"Session file not found: {path}")
    return SessionRecord.from_dict(read_json(path))


def append_timeline_entry(path: Path, artifact: ArtifactRecord) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(artifact.to_dict()) + "\n")


def load_timeline(path: Path) -> list[ArtifactRecord]:
    if not path.exists():
        return []

    artifacts: list[ArtifactRecord] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            artifacts.append(ArtifactRecord.from_dict(json.loads(line)))
    return artifacts


def save_recording_state(recording: RecordingState, path: Path) -> None:
    write_json(path, recording.to_dict())


def load_recording_state(path: Path) -> RecordingState | None:
    if not path.exists():
        return None
    return RecordingState.from_dict(read_json(path))


def clear_recording_state(path: Path) -> None:
    if path.exists():
        path.unlink()


def save_artifact_details(details: ArtifactDetails, path: Path) -> None:
    write_json(path, details.to_dict())


def load_artifact_details(path: Path) -> ArtifactDetails | None:
    if not path.exists():
        return None
    return ArtifactDetails.from_dict(read_json(path))
