# Architecture

Agent Evidence MCP is organized around a stable session-and-artifact model with swappable backends.

## Core Layers

### 1. Session and Artifact Model

The persistent model lives in:

- `session.json`
- `timeline.jsonl`
- `details/<artifact_id>.json`
- `summary.md`

This layer is intentionally backend-agnostic. Screenshots, recordings, notes, and OCR text all map back to the same artifact shape.

### 2. Service Layer

`TaskEvidenceService` is the main orchestration layer.

It is responsible for:

- creating sessions
- capturing screenshots
- starting and stopping recordings
- enriching artifacts with notes or OCR text
- regenerating summaries after changes

The service layer should remain the single source of truth for behavior used by both CLI and MCP tools.

### 3. Backend Layer

Backends are optional and replaceable.

- screenshot backend: Windows PowerShell capture today
- recording backend: ffmpeg on Windows today
- OCR backend: tesseract-compatible abstraction

The backends should stay narrow:

- take input paths and options
- produce files or extracted text
- raise clear errors when unavailable

### 4. Interface Layer

The repository exposes the same behaviors through:

- CLI commands
- MCP tools

The CLI is useful for direct testing and local workflows. The MCP server is the integration surface for agents.

## OCR Design

OCR now supports two modes:

1. Manual mode: store user-supplied text on an artifact.
2. Automatic mode: run the configured OCR backend when enabled.

This keeps the project useful even when OCR binaries are unavailable, while leaving a clean path for real OCR providers.

## Backend Design Rule

Keep public behavior stable while letting backends vary by platform.

That means:

- tool names should stay stable
- session layout should stay stable
- summary format should stay stable
- only the capture backend should vary by OS

## Why This Structure

This project is intended to grow over time:

- macOS and Linux will likely need different capture paths
- OCR may have multiple providers later
- artifact comparison and redaction may add more enrichment files

The current structure is meant to support that growth without forcing a redesign of the CLI, MCP tools, or stored session format.
