# Alpha Release Notes Draft

## What This Release Is

Agent Evidence MCP is an alpha-stage MCP server for agents that need to leave behind a reviewable artifact trail while performing long-running desktop or browser tasks.

The project is aimed at workflows like:

- browser admin tasks
- QA verification
- desktop troubleshooting
- long-running agent execution that needs visible checkpoints

## Highlights

- Session-based screenshot capture with stable artifact directories
- Optional short recordings
- Review-oriented artifact comparison with verdicts and follow-up guidance
- OCR-ready and notes-aware artifact enrichment
- Shareable redacted screenshot copies
- MCP and CLI entry points

## Platform Snapshot

- Windows: strongest support and locally validated for screenshot capture, redaction, and recording
- macOS: screenshot and recording backends implemented, but not yet locally validated in this repository
- Linux: screenshot backend implemented through common desktop tools, recording still pending

## Known Caveats

- Recording is disabled by default and requires `ffmpeg`
- OCR requires an optional backend such as Tesseract
- Linux support is still environment-dependent
- This release is screenshot-first and does not yet aim to replace dedicated automation or test frameworks

## Recommended First Prompt

```text
Use the agent-evidence MCP server for this long-running task.
Start a session before the task, capture checkpoints at major state changes,
prefer screenshots over recording, and end the session with artifact paths and a short review summary.
```
