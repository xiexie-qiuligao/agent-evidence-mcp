# Linux Validation Guide

Use this guide on a real Linux desktop environment to validate the current alpha behavior.

## Goal

Confirm that the following work on a real Linux machine:

- screenshot capture through an available desktop screenshot tool
- recording through `ffmpeg` and `x11grab`
- MCP and CLI session flow

## Prerequisites

- Python 3.10+
- `ffmpeg` installed and available on `PATH`
- an X11-compatible desktop environment for the current recording path
- at least one screenshot tool:
  - `gnome-screenshot`
  - `grim`
  - ImageMagick `import`

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
linux_x11_display = ":0.0"
linux_draw_mouse = true
```

If your desktop uses another display, update `linux_x11_display`.

## Validation Flow

1. Start a session:

```bash
agent-evidence-mcp start-session "linux-validation"
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

- distro and desktop environment
- display server type
- ffmpeg version
- which screenshot tool was used
- whether the default `linux_x11_display` worked
- any environment-specific adjustments that were required

## Current Caveat

The current Linux recording path is intentionally minimal and assumes `x11grab`. Wayland-first environments may need follow-up work before recording is reliable everywhere.
