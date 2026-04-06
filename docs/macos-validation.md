# macOS Validation Guide

Use this guide on a real macOS machine to validate the current alpha behavior.

## Goal

Confirm that the following work on a real macOS environment:

- screenshot capture through `screencapture`
- recording through `ffmpeg` and `avfoundation`
- MCP and CLI session flow

## Prerequisites

- Python 3.10+
- `ffmpeg` installed and available on `PATH`
- screen recording permissions granted to the terminal or app that runs the commands

## Setup

```bash
pip install -e .[dev]
python -m pytest -q
agent-evidence-mcp show-defaults
```

If needed, create a config:

```bash
agent-evidence-mcp init
```

Recommended config settings:

```toml
[capture]
recording_enabled = true
ffmpeg_path = "ffmpeg"
macos_avfoundation_input = "Capture screen 0:none"
macos_capture_cursor = true
```

If the default input does not work, list devices with ffmpeg and update `macos_avfoundation_input`.

## Validation Flow

1. Start a session:

```bash
agent-evidence-mcp start-session "macos-validation"
```

2. Capture a screenshot checkpoint.
3. Start a short recording.
4. Wait a few seconds while changing visible screen content.
5. Stop the recording.
6. End the session.
7. Confirm that:
   - `summary.md` exists
   - the screenshot opens correctly
   - the `.mp4` file plays correctly

## What To Record

For release confidence, note:

- macOS version
- ffmpeg version
- whether the default `macos_avfoundation_input` worked
- whether extra permissions were needed
- any error output or required config changes
