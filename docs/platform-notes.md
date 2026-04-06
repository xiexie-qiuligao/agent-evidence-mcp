# Platform Notes

This project is currently Windows-first.

## Current Validation Status

### Windows

Validated locally on April 6, 2026 with:

- Python package installed in editable mode
- screenshot capture via PowerShell and Windows desktop APIs
- screenshot redaction via PowerShell and `System.Drawing`
- recording via `ffmpeg` using `gdigrab`
- MCP and CLI session flows

Real local recording validation completed on this machine:

- `start-session`
- `start-recording`
- wait a few seconds
- `stop-recording`
- `end-session`
- `ffprobe` verification of the saved `.mp4`

Result:

- recording artifact created successfully
- valid MP4 file detected by `ffprobe`
- summary and timeline updated correctly

## Recording Notes

For Windows recording, the project currently depends on `ffmpeg` with desktop capture support. The local validation in this repository used a Gyan Windows build of ffmpeg.

If `ffmpeg` is not on `PATH`, set `ffmpeg_path` in `task-evidence-mcp.toml`.

## macOS

Initial screenshot backend support is now implemented through the native `screencapture` command.

Current status:

- screenshot backend implemented
- recording backend implemented through `ffmpeg` and `avfoundation`
- not yet locally validated in this repository

Likely future direction:

- keep using native `screencapture` for screenshot capture
- use ffmpeg with `avfoundation` for optional recording
- keep the same session and artifact model
- preserve the screenshot-first default behavior

## Linux

Initial screenshot backend support is now implemented.

Current status:

- screenshot backend implemented through common desktop tools
- current tool preference order is `gnome-screenshot`, then `grim`, then ImageMagick `import`
- not yet locally validated in this repository
- recording backend implemented through `ffmpeg` and `x11grab`

Likely future direction:

- support ffmpeg-based capture paths such as x11grab, kmsgrab, or pipewire-friendly flows depending on the desktop environment
- keep recording optional and avoid making Linux support block Windows reliability

## Cross-Platform Design Rule

The storage model, session lifecycle, MCP tool names, and summary format should remain stable across operating systems even if the capture backend differs.

## macOS Recording Notes

The current macOS recording path assumes `ffmpeg` can access a screen source through `avfoundation`.

Default config values:

- `macos_avfoundation_input = "Capture screen 0:none"`
- `macos_capture_cursor = true`

If a machine exposes a different screen input name, list devices with ffmpeg and override the config accordingly.

## Linux Recording Notes

The current Linux recording path assumes `ffmpeg` can capture through `x11grab`.

Default config values:

- `linux_x11_display = ":0.0"`
- `linux_draw_mouse = true`

This is a deliberately small alpha-stage baseline. Wayland-heavy environments may still need follow-up work.
