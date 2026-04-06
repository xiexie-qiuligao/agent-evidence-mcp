# Known Limitations

This file tracks the highest-signal limitations for the current alpha stage.

## Platform Coverage

- Windows is the only platform with end-to-end local validation for screenshot capture, redaction, and recording.
- macOS screenshot and recording backends exist, but they have not yet been exercised in this repository on a real macOS machine.
- Linux screenshot support depends on common desktop capture tools being available, and Linux recording currently assumes an `x11grab`-friendly environment.

## Capture Model

- Capture currently focuses on full-screen workflows.
- Window-specific capture and region capture at capture time are not implemented yet.
- Redaction creates a new screenshot artifact; it does not modify an artifact in place.

## OCR

- Automatic OCR currently supports screenshot artifacts only.
- OCR depends on an optional backend such as Tesseract being installed and configured.
- OCR quality is backend-dependent and not normalized across platforms.

## Recording

- Recording is optional and disabled by default.
- Recording depends on `ffmpeg` being available.
- macOS recording may require local device discovery and a custom `macos_avfoundation_input` value.
- Linux recording may require a working X11 display and a custom `linux_x11_display` value.

## Review Workflow

- Artifact comparison is metadata-aware and review-oriented, but it does not yet perform pixel-level visual diffing.
- Summary review signals highlight recent evidence pairs, but they are intentionally lightweight and should not be treated as exhaustive audit output.

## Security And Privacy

- Redaction is currently implemented for Windows screenshots only.
- The project does not yet provide automatic sensitive-data detection.
- Users should still review redacted outputs before sharing them externally.
