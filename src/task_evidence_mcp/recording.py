from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from typing import Any
import ctypes


class RecordingError(RuntimeError):
    """Raised when a recording operation fails."""


class RecordingUnavailableError(RecordingError):
    """Raised when recording is disabled or the backend is unavailable."""


@dataclass(frozen=True)
class RecordingHandle:
    pid: int


class RecordingBackend:
    def is_available(self) -> bool:
        raise NotImplementedError

    def start_full_screen_recording(
        self,
        destination: Path,
        frame_rate: int,
    ) -> RecordingHandle:
        raise NotImplementedError

    def stop_recording(self, handle: RecordingHandle) -> None:
        raise NotImplementedError


@dataclass
class FFmpegRecordingBackend(RecordingBackend):
    ffmpeg_path: str = "ffmpeg"
    stop_timeout_seconds: float = 5.0
    platform_name: str = field(default_factory=lambda: sys.platform)
    macos_avfoundation_input: str = "Capture screen 0:none"
    macos_capture_cursor: bool = True
    linux_x11_display: str = ":0.0"
    linux_draw_mouse: bool = True
    _processes: dict[int, Any] = field(default_factory=dict, init=False, repr=False)

    def is_available(self) -> bool:
        return shutil.which(self.ffmpeg_path) is not None

    def start_full_screen_recording(
        self,
        destination: Path,
        frame_rate: int,
    ) -> RecordingHandle:
        if not self.is_available():
            raise RecordingUnavailableError(
                f"Recording backend is unavailable because `{self.ffmpeg_path}` was not found."
            )

        destination.parent.mkdir(parents=True, exist_ok=True)
        command = self._build_start_command(destination, frame_rate)
        popen_kwargs: dict[str, Any] = {
            "stdin": subprocess.PIPE,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "text": True,
        }
        if self.platform_name.startswith("win") and hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
            popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

        process = subprocess.Popen(command, **popen_kwargs)
        self._processes[process.pid] = process
        return RecordingHandle(pid=process.pid)

    def stop_recording(self, handle: RecordingHandle) -> None:
        process = self._processes.pop(handle.pid, None)
        if process is not None and process.poll() is None:
            try:
                if process.stdin is not None:
                    process.stdin.write("q\n")
                    process.stdin.flush()
                process.wait(timeout=self.stop_timeout_seconds)
                return
            except subprocess.TimeoutExpired:
                pass
            except OSError:
                pass

        if self.platform_name.startswith("win"):
            self._stop_recording_windows(handle)
            return

        self._stop_recording_posix(handle, process)

    def _build_start_command(self, destination: Path, frame_rate: int) -> list[str]:
        command = [self.ffmpeg_path, "-y"]
        if self.platform_name.startswith("win"):
            command.extend(
                [
                    "-f",
                    "gdigrab",
                    "-framerate",
                    str(frame_rate),
                    "-i",
                    "desktop",
                ]
            )
        elif self.platform_name == "darwin":
            command.extend(
                [
                    "-f",
                    "avfoundation",
                    "-framerate",
                    str(frame_rate),
                    "-capture_cursor",
                    "1" if self.macos_capture_cursor else "0",
                    "-i",
                    self.macos_avfoundation_input,
                ]
            )
        elif self.platform_name.startswith("linux"):
            command.extend(
                [
                    "-f",
                    "x11grab",
                    "-framerate",
                    str(frame_rate),
                    "-draw_mouse",
                    "1" if self.linux_draw_mouse else "0",
                    "-i",
                    self.linux_x11_display,
                ]
            )
        else:
            raise RecordingUnavailableError(
                f"Recording backend is not implemented for platform `{self.platform_name}`."
            )
        command.append(str(destination))
        return command

    def _stop_recording_windows(self, handle: RecordingHandle) -> None:
        if self._send_ctrl_break(handle.pid) and self._wait_for_process_exit(
            handle.pid,
            self.stop_timeout_seconds,
        ):
            return

        graceful = self._taskkill(handle.pid, force=False)
        if graceful.returncode == 0 and self._wait_for_process_exit(
            handle.pid,
            self.stop_timeout_seconds,
        ):
            return

        forced = self._taskkill(handle.pid, force=True)
        if forced.returncode != 0:
            stderr = forced.stderr.strip() or forced.stdout.strip()
            raise RecordingError(stderr or f"Failed to stop recording process {handle.pid}.")

    def _stop_recording_posix(self, handle: RecordingHandle, process: Any | None) -> None:
        if process is not None and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=self.stop_timeout_seconds)
                return
            except subprocess.TimeoutExpired:
                try:
                    process.kill()
                    process.wait(timeout=self.stop_timeout_seconds)
                    return
                except subprocess.TimeoutExpired as exc:  # pragma: no cover - defensive path
                    raise RecordingError(
                        f"Failed to stop recording process {handle.pid} gracefully on {self.platform_name}."
                    ) from exc
        if self._send_signal(handle.pid, signal.SIGTERM) and self._wait_for_process_exit(
            handle.pid,
            self.stop_timeout_seconds,
        ):
            return
        if self._send_signal(handle.pid, signal.SIGKILL) and self._wait_for_process_exit(
            handle.pid,
            self.stop_timeout_seconds,
        ):
            return
        raise RecordingError(
            f"Failed to stop recording process {handle.pid} on platform `{self.platform_name}`."
        )

    def _taskkill(self, pid: int, force: bool) -> subprocess.CompletedProcess[str]:
        command = ["taskkill", "/PID", str(pid), "/T"]
        if force:
            command.append("/F")
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )

    def _send_ctrl_break(self, pid: int) -> bool:
        try:
            os.kill(pid, signal.CTRL_BREAK_EVENT)
            return True
        except (OSError, ProcessLookupError, AttributeError, ValueError):
            return False

    def _send_signal(self, pid: int, sig: int) -> bool:
        try:
            os.kill(pid, sig)
            return True
        except (OSError, ProcessLookupError, AttributeError, ValueError):
            return False

    def _wait_for_process_exit(self, pid: int, timeout_seconds: float) -> bool:
        if timeout_seconds <= 0:
            return not self._is_process_running(pid)

        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if not self._is_process_running(pid):
                return True
            time.sleep(0.1)
        return not self._is_process_running(pid)

    def _is_process_running(self, pid: int) -> bool:
        if not self.platform_name.startswith("win"):
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False
        synchronize = 0x00100000
        handle = ctypes.windll.kernel32.OpenProcess(synchronize, False, pid)
        if not handle:
            return False
        try:
            wait_result = ctypes.windll.kernel32.WaitForSingleObject(handle, 0)
            return wait_result == 0x00000102
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
