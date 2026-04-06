from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
import textwrap


class RedactionError(RuntimeError):
    """Raised when screenshot redaction fails."""


@dataclass(frozen=True)
class RedactionRegion:
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Redaction regions must use positive width and height.")

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


class RedactionBackend:
    def redact_image(
        self,
        source: Path,
        destination: Path,
        regions: list[RedactionRegion],
        color: str = "#000000",
    ) -> None:
        raise NotImplementedError


@dataclass
class PowerShellRedactionBackend(RedactionBackend):
    powershell_exe: str = "powershell"

    def redact_image(
        self,
        source: Path,
        destination: Path,
        regions: list[RedactionRegion],
        color: str = "#000000",
    ) -> None:
        if not source.exists():
            raise RedactionError(f"Cannot redact missing image: {source}")
        if not regions:
            raise RedactionError("At least one redaction region is required.")

        destination.parent.mkdir(parents=True, exist_ok=True)
        region_json = json.dumps([region.to_dict() for region in regions])
        script = textwrap.dedent(
            f"""
            Add-Type -AssemblyName System.Drawing
            $sourcePath = '{str(source).replace("'", "''")}'
            $destinationPath = '{str(destination).replace("'", "''")}'
            $color = '{color.replace("'", "''")}'
            $regions = @'
            {region_json}
            '@ | ConvertFrom-Json
            $bitmap = [System.Drawing.Bitmap]::FromFile($sourcePath)
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $brush = New-Object System.Drawing.SolidBrush ([System.Drawing.ColorTranslator]::FromHtml($color))
            foreach ($region in $regions) {{
                $graphics.FillRectangle($brush, [int]$region.x, [int]$region.y, [int]$region.width, [int]$region.height)
            }}
            $bitmap.Save($destinationPath, [System.Drawing.Imaging.ImageFormat]::Png)
            $brush.Dispose()
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
            raise RedactionError(stderr or "Screenshot redaction failed.")
        if not destination.exists():
            raise RedactionError("Redaction command completed but no file was created.")
