from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib


@dataclass(frozen=True)
class AppConfig:
    """Minimal configuration for the initial scaffold."""

    artifacts_dir: str = "artifacts"
    screenshot_format: str = "png"
    recording_enabled: bool = False
    recording_format: str = "mp4"
    recording_frame_rate: int = 8
    ffmpeg_path: str = "ffmpeg"
    macos_avfoundation_input: str = "Capture screen 0:none"
    macos_capture_cursor: bool = True
    linux_x11_display: str = ":0.0"
    linux_draw_mouse: bool = True
    ocr_enabled: bool = False
    ocr_backend: str = "tesseract"
    tesseract_path: str = "tesseract"
    ocr_language: str = "eng"

    def resolve_artifacts_dir(self, base_dir: Path) -> Path:
        return (base_dir / self.artifacts_dir).resolve()

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "AppConfig":
        storage = data.get("storage", {})
        capture = data.get("capture", {})
        return cls(
            artifacts_dir=storage.get("artifacts_dir", "artifacts"),
            screenshot_format=capture.get("screenshot_format", "png"),
            recording_enabled=bool(capture.get("recording_enabled", False)),
            recording_format=capture.get("recording_format", "mp4"),
            recording_frame_rate=int(capture.get("recording_frame_rate", 8)),
            ffmpeg_path=capture.get("ffmpeg_path", "ffmpeg"),
            macos_avfoundation_input=capture.get("macos_avfoundation_input", "Capture screen 0:none"),
            macos_capture_cursor=bool(capture.get("macos_capture_cursor", True)),
            linux_x11_display=capture.get("linux_x11_display", ":0.0"),
            linux_draw_mouse=bool(capture.get("linux_draw_mouse", True)),
            ocr_enabled=bool(data.get("ocr", {}).get("enabled", False)),
            ocr_backend=data.get("ocr", {}).get("backend", "tesseract"),
            tesseract_path=data.get("ocr", {}).get("tesseract_path", "tesseract"),
            ocr_language=data.get("ocr", {}).get("language", "eng"),
        )

    def to_toml(self) -> str:
        recording = "true" if self.recording_enabled else "false"
        return "\n".join(
            [
                "# Agent Evidence MCP configuration",
                "",
                "[storage]",
                f'artifacts_dir = "{self.artifacts_dir}"',
                "",
                "[capture]",
                f'screenshot_format = "{self.screenshot_format}"',
                f"recording_enabled = {recording}",
                f'recording_format = "{self.recording_format}"',
                f"recording_frame_rate = {self.recording_frame_rate}",
                f'ffmpeg_path = "{self.ffmpeg_path}"',
                f'macos_avfoundation_input = "{self.macos_avfoundation_input}"',
                f"macos_capture_cursor = {'true' if self.macos_capture_cursor else 'false'}",
                f'linux_x11_display = "{self.linux_x11_display}"',
                f"linux_draw_mouse = {'true' if self.linux_draw_mouse else 'false'}",
                "",
                "[ocr]",
                f"enabled = {'true' if self.ocr_enabled else 'false'}",
                f'backend = "{self.ocr_backend}"',
                f'tesseract_path = "{self.tesseract_path}"',
                f'language = "{self.ocr_language}"',
                "",
            ]
        )


DEFAULT_CONFIG = AppConfig()


def load_config(path: Path | None) -> AppConfig:
    if path is None or not path.exists():
        return DEFAULT_CONFIG

    with path.open("rb") as handle:
        payload = tomllib.load(handle)
    return AppConfig.from_mapping(payload)
