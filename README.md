# Agent Evidence MCP

Agent Evidence MCP is a lightweight MCP server for screenshots, short recordings, and milestone evidence capture during long-running agent tasks.

The project is designed for users who want an agent to do real work on desktop or browser flows while leaving behind a clean, reviewable trail of what happened, when it happened, and where the artifacts were saved.

## Product Goal

Turn "take a screenshot" into a higher-level workflow:

- create a session for a long task
- capture evidence at important checkpoints
- store artifacts in a predictable directory layout
- summarize the timeline at the end

## Core Experience

A good run should feel like this:

1. The user asks an agent to complete a multi-step task.
2. The agent starts an evidence session.
3. The agent captures screenshots at key milestones and on failures.
4. The agent stores everything under a single session directory.
5. The agent ends with a short summary and file paths the user can open.

## Scope

### MVP

- screenshot-first workflow
- session-based artifact storage
- checkpoint metadata and timeline logging
- companion skill to teach agents when and how to capture evidence

### Later

- short recordings for motion-heavy flows
- OCR on screenshots
- review-oriented artifact comparison and summaries
- privacy-preserving redaction for sensitive screenshots

## Repository Layout

```text
.
|-- README.md
|-- docs/
|   |-- architecture.md
|   |-- client-configs.md
|   |-- project-spec.md
|   |-- recipes.md
|   `-- tasks.md
|-- examples/
|   |-- client-configs/
|   `-- prompts/
|-- skills/
|   `-- agent-evidence-capture/
|       `-- SKILL.md
|-- src/
|   `-- task_evidence_mcp/
|       |-- __init__.py
|       |-- cli.py
|       |-- config.py
|       |-- layout.py
|       `-- server.py
`-- tests/
    |-- test_cli.py
    |-- test_config.py
    |-- test_layout.py
    |-- test_server.py
    `-- test_service.py
```

## Current Status

The repository now includes a working screenshot-first local MVP and an MCP tool layer:

- session creation
- Windows full-screen screenshot capture
- macOS screenshot backend support through the native `screencapture` path
- Linux screenshot backend support through common desktop tools such as `gnome-screenshot`, `grim`, or `import`
- optional short recording support via `ffmpeg`
- platform-aware recording backend selection for Windows and macOS
- checkpoint metadata and timeline logging
- session summary generation with notes and OCR-ready artifact metadata
- review-oriented artifact comparison for long-task handoff and validation
- redacted screenshot copies for safer sharing and review
- MCP tools for session lifecycle and artifact capture
- a companion skill draft for long-running tasks

The repository also includes client configuration examples plus basic contribution and issue-reporting assets for open-source use.

Release-facing assets now also include:

- a basic GitHub Actions CI workflow
- a changelog
- a release checklist for packaging and validation

## Alpha Readiness

This repository is now close to an alpha-style public release:

- core CLI and MCP flows are implemented
- Windows has real local validation for screenshot capture, redaction, and recording
- macOS and Linux have partial cross-platform backend coverage, but not the same validation depth yet
- packaging, tests, and build checks are in place

The best current fit is an honest `alpha` release rather than a 鈥渇ully stable鈥?one.

## Support Snapshot

- Windows: best-supported platform today
- macOS: screenshot and recording backends implemented, validation still needed
- Linux: screenshot and recording backends implemented, validation still needed

See the detailed matrix here: [support-matrix.md](docs/support-matrix.md)

## Quickstart

Install the package in editable mode from the repository root:

```bash
pip install -e .
```

Optionally write a starter config:

```bash
agent-evidence-mcp init
```

Recording is disabled by default. To use recording commands, enable it in `agent-evidence-mcp.toml` and point `ffmpeg_path` at a working `ffmpeg` binary if it is not already on your `PATH`.

### 1. Show defaults

```bash
agent-evidence-mcp show-defaults
```

### 2. Start a session

```bash
agent-evidence-mcp start-session "Admin QA Flow"
```

This returns JSON including:

- `session_id`
- `session_dir`
- `timeline_path`

### 3. Capture a checkpoint

```bash
agent-evidence-mcp capture-checkpoint "D:\path\to\session" "form-submitted" "The form was submitted successfully." --step step-02
```

### 4. Capture a raw screenshot

```bash
agent-evidence-mcp capture-screenshot "D:\path\to\session" "manual-shot"
```

### 5. List artifacts

```bash
agent-evidence-mcp list-artifacts "D:\path\to\session"
```

### 6. End the session

```bash
agent-evidence-mcp end-session "D:\path\to\session"
```

The session directory contains:

- `session.json`
- `timeline.jsonl`
- `summary.md`
- `details/`
- `screenshots/`
- `recordings/`

## Review Workflow

After attaching notes or OCR text, compare two artifacts from the same session:

```bash
agent-evidence-mcp compare-artifacts "D:\path\to\session" "artifact-a" "artifact-b"
```

The comparison result includes:

- a `verdict` such as `unchanged`, `metadata_changed`, or `content_changed`
- `changed_fields` so agents can see what shifted
- `review_focus` guidance for what a human should inspect next
- OCR previews when available

Session summaries also surface lightweight review signals automatically when a session has at least two screenshots or two recordings of the same type, so `summary.md` can act as a quick handoff brief.

## Privacy-Preserving Redaction

Create a shareable copy of a screenshot without modifying the original artifact:

```bash
agent-evidence-mcp redact-artifact "D:\path\to\session" "artifact-a" "shareable-copy" --region 120,80,240,60 --region 410,90,120,40
```

This creates a new screenshot artifact that:

- keeps the original screenshot untouched
- records which source artifact it came from
- stores the redaction rectangles in artifact metadata
- surfaces the redacted copy in `summary.md` and `list_artifacts`

For the common review case where you just want the latest comparable pair:

```bash
agent-evidence-mcp compare-latest-artifacts "D:\path\to\session" --artifact-type screenshot
```

If `--artifact-type` is omitted, the CLI compares the latest two artifacts of the latest artifact type in the session.

## Optional Recording

Recording is intentionally optional and should be used for short, motion-heavy moments rather than entire long-running tasks.

Example config:

```toml
[storage]
artifacts_dir = "artifacts"

[capture]
screenshot_format = "png"
recording_enabled = true
recording_format = "mp4"
recording_frame_rate = 8
ffmpeg_path = "ffmpeg"
macos_avfoundation_input = "Capture screen 0:none"
macos_capture_cursor = true
```

Start a recording:

```bash
agent-evidence-mcp start-recording "D:\path\to\session" "drag-flow" "Capture the drag and drop interaction."
```

Check whether a recording is active:

```bash
agent-evidence-mcp recording-status "D:\path\to\session"
```

Stop the recording and save it as an artifact:

```bash
agent-evidence-mcp stop-recording "D:\path\to\session"
```

On macOS, the recording backend now uses `ffmpeg` with `avfoundation`. The default input is `Capture screen 0:none`, and you can override it in config if your machine exposes a different screen capture device name.

## Run As MCP

Run the server over stdio:

```bash
agent-evidence-mcp serve
```

Available MCP tools:

- `start_session`
- `capture_checkpoint`
- `capture_screenshot`
- `list_artifacts`
- `start_recording`
- `get_recording_status`
- `stop_recording`
- `attach_note`
- `ocr_artifact`
- `redact_artifact`
- `compare_artifacts`
- `compare_latest_artifacts`
- `end_session`

The server currently exposes the same core flow as the local CLI, including optional recording support when enabled in config.

## Examples And Client Configs

- Prompt recipes: [recipes.md](docs/recipes.md)
- Architecture notes: [architecture.md](docs/architecture.md)
- Roadmap: [roadmap.md](docs/roadmap.md)
- Release checklist: [release-checklist.md](docs/release-checklist.md)
- Alpha release audit: [alpha-release-audit.md](docs/alpha-release-audit.md)
- Support matrix: [support-matrix.md](docs/support-matrix.md)
- Known limitations: [known-limitations.md](docs/known-limitations.md)
- Alpha release notes draft: [alpha-release-notes.md](docs/alpha-release-notes.md)
- macOS validation guide: [macos-validation.md](docs/macos-validation.md)
- Linux validation guide: [linux-validation.md](docs/linux-validation.md)
- Client config notes: [client-configs.md](docs/client-configs.md)
- Platform notes: [platform-notes.md](docs/platform-notes.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Claude Desktop example: [claude_desktop_config.json](examples/client-configs/claude_desktop_config.json)
- Generic stdio example: [agent-evidence-stdio.json](examples/client-configs/agent-evidence-stdio.json)
- Examples index: [examples/README.md](examples/README.md)
- Prompt snippets: [examples/prompts](examples/prompts)
- Validation helper script: [validate_session_flow.py](scripts/validate_session_flow.py)
- Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)
- License: [LICENSE](LICENSE)

## Near-Term Build Order

1. Deepen review workflows around `compare_artifacts`.
2. Keep the review path low-friction for agents and first-time users.
3. Add more GitHub release polish as the public API stabilizes.
4. Expand OCR and redaction features carefully around the evidence workflow.
5. Add macOS backend work.
6. Add Linux backend work.

## Quality Bar

- simple install path
- predictable file layout
- low-friction first run
- minimal dependencies
- clear user-facing summaries
- stable default behavior for long tasks


