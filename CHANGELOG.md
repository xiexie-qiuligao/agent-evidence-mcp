# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog, and the project currently uses a simple pre-1.0 versioning flow.

## [Unreleased]

### Added

- MCP session lookup tools: `list_sessions`, `get_session`, and `get_latest_session`.
- MCP resources for session indexes, latest summaries, latest artifacts, and session-specific summaries/artifacts.
- MCP prompts for evidence capture planning and final evidence review.
- Review-oriented artifact comparison with verdicts, changed fields, OCR previews, and review guidance.
- `compare_latest_artifacts` support in the service layer, CLI, and MCP server.
- Automatic review signals in `summary.md` for the latest comparable screenshots or recordings.
- OCR backend abstraction with optional automatic OCR flow.
- Screenshot redaction that creates shareable redacted copies while preserving the original artifact.
- Platform-aware screenshot backend selection with initial macOS `screencapture` support.
- Initial Linux screenshot backend support using common desktop capture tools.
- Platform-aware recording backend selection with initial macOS `avfoundation` support.
- Release assets including CI, contribution guidance, issue templates, and platform notes.

### Changed

- README and alpha release notes now use clean bilingual copy and describe the product as an agent evidence recorder.
- Package metadata now describes the project as a local MCP server rather than scaffolding.
- Session summaries now act more like handoff briefs instead of raw artifact logs.
- Recording stop behavior on Windows now prefers graceful `ffmpeg` shutdown before fallback termination.

### Removed

- Removed planning and local release-audit notes from tracked public docs.

## [0.1.0a1] - 2026-04-06

### Added

- Initial public alpha for session-based screenshot capture.
- Optional short recording workflow.
- MCP server and CLI entry points.
- Session summaries, artifact notes, and artifact storage layout.
