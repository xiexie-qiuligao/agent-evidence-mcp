from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap


class CaptureError(RuntimeError):
    """Raised when a capture operation fails."""


class ScreenshotBackend:
    def capture_full_screen(self, destination: Path) -> None:
        raise NotImplementedError


class ScreenshotUnavailableError(CaptureError):
    """Raised when no screenshot backend is available for the current platform."""


@dataclass
class PowerShellScreenshotBackend(ScreenshotBackend):
    powershell_exe: str = "powershell"

    def capture_full_screen(self, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        script = textwrap.dedent(
            f"""
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing
            $bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
            $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bitmap.Size)
            $bitmap.Save('{str(destination).replace("'", "''")}', [System.Drawing.Imaging.ImageFormat]::Png)
            $graphics.Dispose()
            $bitmap.Dispose()
            """
        ).strip()
        completed = subprocess.run(
            [self.powershell_exe, "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or completed.stdout.strip()
            raise CaptureError(stderr or "Screenshot capture failed.")
        if not destination.exists():
            raise CaptureError("Screenshot command completed but no file was created.")


@dataclass
class MacOSScreenshotBackend(ScreenshotBackend):
    screencapture_exe: str = "screencapture"

    def capture_full_screen(self, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        completed = subprocess.run(
            [self.screencapture_exe, "-x", str(destination)],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or completed.stdout.strip()
            raise CaptureError(stderr or "macOS screenshot capture failed.")
        if not destination.exists():
            raise CaptureError("Screenshot command completed but no file was created.")


@dataclass
class LinuxScreenshotBackend(ScreenshotBackend):
    gnome_screenshot_exe: str = "gnome-screenshot"
    grim_exe: str = "grim"
    imagemagick_import_exe: str = "import"

    def capture_full_screen(self, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        command = self._build_capture_command(destination)
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or completed.stdout.strip()
            raise CaptureError(stderr or "Linux screenshot capture failed.")
        if not destination.exists():
            raise CaptureError("Screenshot command completed but no file was created.")

    def _build_capture_command(self, destination: Path) -> list[str]:
        if shutil.which(self.gnome_screenshot_exe):
            return [self.gnome_screenshot_exe, "-f", str(destination)]
        if shutil.which(self.grim_exe):
            return [self.grim_exe, str(destination)]
        if shutil.which(self.imagemagick_import_exe):
            return [self.imagemagick_import_exe, "-window", "root", str(destination)]
        raise ScreenshotUnavailableError(
            "No supported Linux screenshot tool was found. Install gnome-screenshot, grim, or ImageMagick's import."
        )


@dataclass
class UnsupportedScreenshotBackend(ScreenshotBackend):
    platform_name: str

    def capture_full_screen(self, destination: Path) -> None:
        raise ScreenshotUnavailableError(
            f"No screenshot backend is configured for platform `{self.platform_name}`."
        )


def create_default_screenshot_backend(platform_name: str | None = None) -> ScreenshotBackend:
    platform_name = platform_name or sys.platform
    if platform_name.startswith("win"):
        return PowerShellScreenshotBackend()
    if platform_name == "darwin":
        return MacOSScreenshotBackend()
    if platform_name.startswith("linux"):
        return LinuxScreenshotBackend()
    return UnsupportedScreenshotBackend(platform_name=platform_name)
