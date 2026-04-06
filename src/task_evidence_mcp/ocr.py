from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess


class OCRError(RuntimeError):
    """Raised when OCR processing fails."""


class OCRUnavailableError(OCRError):
    """Raised when OCR is disabled or the backend is unavailable."""


class OCRBackend:
    def is_available(self) -> bool:
        raise NotImplementedError

    def extract_text(self, image_path: Path) -> str:
        raise NotImplementedError


@dataclass
class TesseractOCRBackend(OCRBackend):
    tesseract_path: str = "tesseract"
    language: str = "eng"

    def is_available(self) -> bool:
        return shutil.which(self.tesseract_path) is not None

    def extract_text(self, image_path: Path) -> str:
        if not self.is_available():
            raise OCRUnavailableError(
                f"OCR backend is unavailable because `{self.tesseract_path}` was not found."
            )

        completed = subprocess.run(
            [
                self.tesseract_path,
                str(image_path),
                "stdout",
                "-l",
                self.language,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or completed.stdout.strip()
            raise OCRError(stderr or f"Tesseract failed for {image_path}.")
        return completed.stdout.strip()
