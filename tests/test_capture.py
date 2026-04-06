from pathlib import Path, PurePosixPath

from task_evidence_mcp.capture import (
    LinuxScreenshotBackend,
    MacOSScreenshotBackend,
    PowerShellScreenshotBackend,
    ScreenshotUnavailableError,
    UnsupportedScreenshotBackend,
    create_default_screenshot_backend,
)


def test_create_default_screenshot_backend_uses_windows_backend() -> None:
    backend = create_default_screenshot_backend("win32")

    assert isinstance(backend, PowerShellScreenshotBackend)


def test_create_default_screenshot_backend_uses_macos_backend() -> None:
    backend = create_default_screenshot_backend("darwin")

    assert isinstance(backend, MacOSScreenshotBackend)


def test_create_default_screenshot_backend_uses_linux_backend() -> None:
    backend = create_default_screenshot_backend("linux")

    assert isinstance(backend, LinuxScreenshotBackend)


def test_linux_backend_prefers_gnome_screenshot(monkeypatch) -> None:
    backend = LinuxScreenshotBackend()

    def fake_which(name: str) -> str | None:
        if name == "gnome-screenshot":
            return "/usr/bin/gnome-screenshot"
        return None

    monkeypatch.setattr("task_evidence_mcp.capture.shutil.which", fake_which)

    command = backend._build_capture_command(PurePosixPath("/tmp/demo.png"))

    assert command == ["gnome-screenshot", "-f", "/tmp/demo.png"]


def test_linux_backend_falls_back_to_grim(monkeypatch) -> None:
    backend = LinuxScreenshotBackend()

    def fake_which(name: str) -> str | None:
        if name == "grim":
            return "/usr/bin/grim"
        return None

    monkeypatch.setattr("task_evidence_mcp.capture.shutil.which", fake_which)

    command = backend._build_capture_command(PurePosixPath("/tmp/demo.png"))

    assert command == ["grim", "/tmp/demo.png"]


def test_linux_backend_falls_back_to_imagemagick_import(monkeypatch) -> None:
    backend = LinuxScreenshotBackend()

    def fake_which(name: str) -> str | None:
        if name == "import":
            return "/usr/bin/import"
        return None

    monkeypatch.setattr("task_evidence_mcp.capture.shutil.which", fake_which)

    command = backend._build_capture_command(PurePosixPath("/tmp/demo.png"))

    assert command == ["import", "-window", "root", "/tmp/demo.png"]


def test_linux_backend_raises_when_no_tool_is_available(monkeypatch) -> None:
    backend = LinuxScreenshotBackend()

    monkeypatch.setattr("task_evidence_mcp.capture.shutil.which", lambda _name: None)

    try:
        backend._build_capture_command(Path("/tmp/unused.png"))
    except ScreenshotUnavailableError as exc:
        assert "No supported Linux screenshot tool" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected ScreenshotUnavailableError when no Linux screenshot tool is available.")


def test_create_default_screenshot_backend_returns_unsupported_backend_for_unknown_platform() -> None:
    backend = create_default_screenshot_backend("plan9")

    assert isinstance(backend, UnsupportedScreenshotBackend)
