# Build Tasks

This file breaks the project into delivery phases with outputs, acceptance criteria, and sequencing.

## Status Snapshot

### Completed

- Phase 0 foundation
- Phase 1 screenshot MVP
- Phase 3 MCP exposure for the current screenshot-first tool set

### In Progress

- Phase 2 recording and summaries
- Phase 4 GitHub-ready polish

### Remaining Major Work

- deeper review workflows around OCR, redaction, and artifact comparison
- lower-friction review commands and MCP patterns for recent evidence
- additional release polish as the API stabilizes
- future macOS and Linux backend work

## Phase 0: Foundation

### Goal

Lock product direction, repository structure, and workflow conventions before implementing capture logic.

### Tasks

1. Create the repository skeleton.
2. Write the README, spec, and phased task plan.
3. Draft the companion skill for agent behavior.
4. Define the session layout and naming conventions in code.
5. Add a minimal CLI so the package can be installed and exercised early.

### Acceptance Criteria

- repository structure exists
- project goals are documented
- skill draft exists and is usable as a starting point
- layout logic is codified and testable

## Phase 1: Screenshot MVP

### Goal

Ship the first genuinely useful version for long-running tasks.

### Tasks

1. Implement session creation with a stable `session_id`.
2. Create session directories on demand.
3. Implement screenshot capture on Windows.
4. Implement `capture_checkpoint` metadata and timeline logging.
5. Implement `list_artifacts` and `end_session`.
6. Add tests around path generation and metadata persistence.
7. Add a short local demo flow and document it in the README.

### Acceptance Criteria

- a user can start a session and save evidence into a clean folder
- checkpoint captures generate readable file names
- timeline entries reflect saved artifacts
- final output reports where artifacts were stored

## Phase 2: Recording and Summaries

### Goal

Add optional short recordings without making them the center of the product.

### Tasks

1. Implement recording abstraction and ffmpeg integration.
2. Add `start_recording`, `stop_recording`, and status reporting.
3. Write `summary.md` at session end.
4. Add `attach_note` for human-readable context.
5. Document when agents should prefer recording over screenshots.

### Acceptance Criteria

- a user can create a short recording under the same session
- the session summary includes both screenshots and recordings
- recording remains optional and disabled by default if unavailable

## Phase 3: MCP Exposure

### Goal

Expose the core functionality as stable MCP tools.

### Tasks

1. Add MCP server wiring around the session and capture services.
2. Register phase-one tools with clear schemas.
3. Add error messages that help users recover from bad inputs.
4. Document example client configuration for common MCP clients.

### Acceptance Criteria

- the server starts cleanly
- tools are discoverable by an MCP client
- a client can run the screenshot MVP end to end

## Phase 4: GitHub-Ready Polish

### Goal

Make the repository easy to understand, install, and trust.

### Tasks

1. Add installation instructions for pip and uv.
2. Add example prompts and example client configs.
3. Add a short architecture document if implementation complexity grows.
4. Add issue templates or contribution notes if community usage starts.
5. Review naming, defaults, and path conventions from a first-time user perspective.
6. Add CI and release validation assets once packaging stabilizes.

### Acceptance Criteria

- a new user can understand the project from the README alone
- at least one quickstart path is less than ten minutes
- examples show the intended long-task workflow clearly
- the repository has an obvious automated quality gate

## Quality Gates

### Before v0.1

- no broken package entrypoint
- tests pass for config and layout behavior
- directory layout is stable
- skill instructions align with the actual tool design

### Before v0.2

- recording failures do not break screenshot workflows
- summaries reflect real session state
- optional dependencies are documented clearly

### Before v1.0

- docs match actual commands
- first-run defaults are stable
- common failure paths are explained in plain language
