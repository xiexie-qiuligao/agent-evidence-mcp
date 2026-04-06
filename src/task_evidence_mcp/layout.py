from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return cleaned or "task"


def build_session_id(task_name: str, timestamp: datetime | None = None) -> str:
    timestamp = timestamp or datetime.now()
    return f"{timestamp:%Y%m%d-%H%M%S}-{slugify(task_name)}"


def build_artifact_name(label: str, extension: str, timestamp: datetime | None = None) -> str:
    timestamp = timestamp or datetime.now()
    safe_extension = extension.lstrip(".")
    return f"{timestamp:%Y%m%d-%H%M%S}-{slugify(label)}.{safe_extension}"


def ensure_unique_path(path: Path) -> Path:
    if not path.exists():
        return path

    suffix = path.suffix
    stem = path.stem if suffix else path.name
    counter = 2
    while True:
        candidate_name = f"{stem}-{counter}{suffix}"
        candidate = path.with_name(candidate_name)
        if not candidate.exists():
            return candidate
        counter += 1


@dataclass(frozen=True)
class SessionLayout:
    root: Path
    session_id: str

    @property
    def session_dir(self) -> Path:
        return self.root / self.session_id

    @property
    def screenshots_dir(self) -> Path:
        return self.session_dir / "screenshots"

    @property
    def recordings_dir(self) -> Path:
        return self.session_dir / "recordings"

    @property
    def timeline_path(self) -> Path:
        return self.session_dir / "timeline.jsonl"

    @property
    def session_path(self) -> Path:
        return self.session_dir / "session.json"

    @property
    def summary_path(self) -> Path:
        return self.session_dir / "summary.md"

    @property
    def active_recording_path(self) -> Path:
        return self.session_dir / "active_recording.json"

    @property
    def details_dir(self) -> Path:
        return self.session_dir / "details"

    def create(self) -> None:
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.details_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_session_dir(cls, session_dir: Path) -> "SessionLayout":
        return cls(session_dir.parent, session_dir.name)
