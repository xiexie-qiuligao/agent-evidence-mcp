from __future__ import annotations

from pathlib import Path, PurePosixPath
import subprocess

from task_evidence_mcp.recording import FFmpegRecordingBackend, RecordingHandle


class FakeStdin:
    def __init__(self) -> None:
        self.writes: list[str] = []

    def write(self, text: str) -> None:
        self.writes.append(text)

    def flush(self) -> None:
        return None


class GracefulFakeProcess:
    def __init__(self) -> None:
        self.stdin = FakeStdin()
        self.wait_called_with: float | None = None

    def poll(self) -> None:
        return None

    def wait(self, timeout: float) -> int:
        self.wait_called_with = timeout
        return 0


class TimeoutFakeProcess(GracefulFakeProcess):
    def wait(self, timeout: float) -> int:
        self.wait_called_with = timeout
        raise subprocess.TimeoutExpired(cmd="ffmpeg", timeout=timeout)


def test_stop_recording_prefers_graceful_quit() -> None:
    backend = FFmpegRecordingBackend(stop_timeout_seconds=2.5)
    process = GracefulFakeProcess()
    backend._processes[1234] = process

    backend.stop_recording(RecordingHandle(pid=1234))

    assert process.stdin.writes == ["q\n"]
    assert process.wait_called_with == 2.5


def test_build_start_command_uses_windows_gdigrab() -> None:
    backend = FFmpegRecordingBackend(
        ffmpeg_path="ffmpeg",
        platform_name="win32",
    )

    command = backend._build_start_command(Path("D:/tmp/demo.mp4"), frame_rate=8)

    assert command == [
        "ffmpeg",
        "-y",
        "-f",
        "gdigrab",
        "-framerate",
        "8",
        "-i",
        "desktop",
        str(Path("D:/tmp/demo.mp4")),
    ]


def test_build_start_command_uses_macos_avfoundation() -> None:
    backend = FFmpegRecordingBackend(
        ffmpeg_path="ffmpeg",
        platform_name="darwin",
        macos_avfoundation_input="Capture screen 1:none",
        macos_capture_cursor=False,
    )

    command = backend._build_start_command(PurePosixPath("/tmp/demo.mp4"), frame_rate=12)

    assert command == [
        "ffmpeg",
        "-y",
        "-f",
        "avfoundation",
        "-framerate",
        "12",
        "-capture_cursor",
        "0",
        "-i",
        "Capture screen 1:none",
        "/tmp/demo.mp4",
    ]


def test_build_start_command_uses_linux_x11grab() -> None:
    backend = FFmpegRecordingBackend(
        ffmpeg_path="ffmpeg",
        platform_name="linux",
        linux_x11_display=":1.0",
        linux_draw_mouse=False,
    )

    command = backend._build_start_command(PurePosixPath("/tmp/demo.mp4"), frame_rate=15)

    assert command == [
        "ffmpeg",
        "-y",
        "-f",
        "x11grab",
        "-framerate",
        "15",
        "-draw_mouse",
        "0",
        "-i",
        ":1.0",
        "/tmp/demo.mp4",
    ]


def test_stop_recording_uses_ctrl_break_before_taskkill_when_process_object_is_missing() -> None:
    backend = FFmpegRecordingBackend(stop_timeout_seconds=1.0, platform_name="win32")
    calls: list[str] = []

    def fake_send_ctrl_break(pid: int) -> bool:
        calls.append(f"break:{pid}")
        return True

    def fake_wait(pid: int, timeout_seconds: float) -> bool:
        calls.append(f"wait:{pid}:{timeout_seconds}")
        return True

    backend._send_ctrl_break = fake_send_ctrl_break  # type: ignore[method-assign]
    backend._wait_for_process_exit = fake_wait  # type: ignore[method-assign]

    backend.stop_recording(RecordingHandle(pid=2222))

    assert calls == ["break:2222", "wait:2222:1.0"]


def test_stop_recording_falls_back_to_taskkill_after_timeout() -> None:
    backend = FFmpegRecordingBackend(stop_timeout_seconds=1.0, platform_name="win32")
    process = TimeoutFakeProcess()
    backend._processes[4321] = process
    calls: list[str] = []

    def fake_send_ctrl_break(pid: int) -> bool:
        calls.append(f"break:{pid}")
        return False

    wait_results = iter([True])

    def fake_wait(pid: int, timeout_seconds: float) -> bool:
        calls.append(f"wait:{pid}:{timeout_seconds}")
        return next(wait_results)

    def fake_taskkill(pid: int, force: bool):
        calls.append(f"taskkill:{pid}:{force}")
        return subprocess.CompletedProcess(
            args=["taskkill"],
            returncode=0,
            stdout="ok",
            stderr="",
        )

    backend._send_ctrl_break = fake_send_ctrl_break  # type: ignore[method-assign]
    backend._wait_for_process_exit = fake_wait  # type: ignore[method-assign]
    backend._taskkill = fake_taskkill  # type: ignore[method-assign]

    backend.stop_recording(RecordingHandle(pid=4321))

    assert calls == [
        "break:4321",
        "taskkill:4321:False",
        "wait:4321:1.0",
    ]
