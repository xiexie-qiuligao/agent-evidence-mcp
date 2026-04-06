from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


def utc_now() -> datetime:
    return datetime.now().astimezone()


@dataclass
class SessionRecord:
    session_id: str
    task_name: str
    created_at: str
    artifacts_root: str
    status: str = "active"
    closed_at: str | None = None
    artifact_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        session_id: str,
        task_name: str,
        artifacts_root: Path,
        metadata: dict[str, Any] | None = None,
    ) -> "SessionRecord":
        return cls(
            session_id=session_id,
            task_name=task_name,
            created_at=utc_now().isoformat(),
            artifacts_root=str(artifacts_root),
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionRecord":
        return cls(**data)


@dataclass
class ArtifactRecord:
    artifact_id: str
    session_id: str
    artifact_type: str
    created_at: str
    label: str
    reason: str
    path: str
    step: str | None = None
    target: str = "desktop"
    tags: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    ocr_text: str | None = None
    source_artifact_id: str | None = None
    redactions: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        artifact_id: str,
        session_id: str,
        artifact_type: str,
        label: str,
        reason: str,
        path: Path,
        step: str | None = None,
        target: str = "desktop",
        tags: list[str] | None = None,
        notes: list[str] | None = None,
        ocr_text: str | None = None,
        source_artifact_id: str | None = None,
        redactions: list[dict[str, Any]] | None = None,
    ) -> "ArtifactRecord":
        return cls(
            artifact_id=artifact_id,
            session_id=session_id,
            artifact_type=artifact_type,
            created_at=utc_now().isoformat(),
            label=label,
            reason=reason,
            path=str(path),
            step=step,
            target=target,
            tags=tags or [],
            notes=notes or [],
            ocr_text=ocr_text,
            source_artifact_id=source_artifact_id,
            redactions=redactions or [],
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ArtifactRecord":
        return cls(**data)


@dataclass
class RecordingState:
    recording_id: str
    session_id: str
    started_at: str
    label: str
    reason: str
    path: str
    pid: int
    status: str = "recording"
    step: str | None = None
    target: str = "desktop"
    tags: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        recording_id: str,
        session_id: str,
        label: str,
        reason: str,
        path: Path,
        pid: int,
        step: str | None = None,
        target: str = "desktop",
        tags: list[str] | None = None,
    ) -> "RecordingState":
        return cls(
            recording_id=recording_id,
            session_id=session_id,
            started_at=utc_now().isoformat(),
            label=label,
            reason=reason,
            path=str(path),
            pid=pid,
            step=step,
            target=target,
            tags=tags or [],
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecordingState":
        return cls(**data)


@dataclass
class ArtifactDetails:
    artifact_id: str
    session_id: str
    artifact_path: str
    notes: list[str] = field(default_factory=list)
    ocr_text: str | None = None
    source_artifact_id: str | None = None
    redactions: list[dict[str, Any]] = field(default_factory=list)
    updated_at: str | None = None

    @classmethod
    def create(
        cls,
        artifact_id: str,
        session_id: str,
        artifact_path: Path,
    ) -> "ArtifactDetails":
        return cls(
            artifact_id=artifact_id,
            session_id=session_id,
            artifact_path=str(artifact_path),
            source_artifact_id=None,
            redactions=[],
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ArtifactDetails":
        return cls(**data)
