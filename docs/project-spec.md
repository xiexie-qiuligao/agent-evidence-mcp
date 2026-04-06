# Project Spec

## Summary

Task Evidence MCP is an open-source MCP server that lets agents capture screenshots, short recordings, and checkpoint metadata while performing long-running desktop or browser tasks.

The project exists to make agent work observable, reviewable, and easy to hand off.

## Product Principles

### 1. Prioritize evidence, not raw media

The product should focus on milestone capture, session structure, and useful summaries rather than acting like a generic recording utility.

### 2. Prefer screenshots over recordings

Screenshots are cheaper, easier to store, easier to review, and easier to index. Recording is a secondary capability for cases where motion matters.

### 3. Make the default path obvious

Users should not need to invent storage layouts, naming schemes, or prompt patterns. The default experience should already be clean.

### 4. Design for long tasks

The system should support multi-step work such as deployments, browser flows, QA runs, admin tasks, and troubleshooting.

### 5. Keep the footprint light

The project should start with minimal dependencies and avoid making recording the critical path.

## Primary Users

- people running agents on browser or desktop workflows
- users who need visible progress artifacts for long tasks
- QA and ops workflows that need checkpoint evidence
- users who want a final audit trail or delivery package

## Non-Goals

- building a full video editing tool
- building a cloud artifact management system in the first release
- supporting every desktop OS on day one
- replacing dedicated test automation frameworks

## Product Shape

The final product has three parts:

1. An MCP server that exposes tools for sessions, screenshots, recordings, and artifact lookup.
2. A companion skill that teaches agents how to use the tools well.
3. A GitHub-first repository with fast setup, clear examples, and strong defaults.

## Tool Design

### Phase-One Tools

- `start_session`
- `capture_checkpoint`
- `capture_screenshot`
- `list_artifacts`
- `end_session`

### Phase-Two Tools

- `start_recording`
- `stop_recording`
- `get_recording_status`
- `attach_note`
- `ocr_artifact`
- `compare_artifacts`
- `redact_artifact`

### Phase-Three Candidates

- `redact_sensitive_regions`
- `summarize_session`

## Session Model

Each long-running task creates a session.

Session fields:

- `session_id`
- `task_name`
- `created_at`
- `artifacts_root`
- `mode`
- `status`

## Artifact Model

Each screenshot or recording should store:

- `artifact_id`
- `session_id`
- `timestamp`
- `type`
- `label`
- `reason`
- `step`
- `path`
- `target`
- `tags`
- `notes`
- `ocr_text`

## Default Storage Layout

```text
artifacts/
  <session_id>/
    session.json
    timeline.jsonl
    details/
    screenshots/
    recordings/
    summary.md
```

## Default Behavior

- create a session before long tasks
- prefer `capture_checkpoint` over raw screenshot capture
- take extra evidence when an error or state transition occurs
- store artifacts under a single session directory unless the user overrides it
- return paths that are easy for users to inspect

## GitHub Release Expectations

The repository should feel ready for real users:

- concise README with a clear value proposition
- one-command local setup
- example MCP client configuration
- prompt examples for long-running tasks
- tests for layout and config behavior
- basic CI for tests and build validation
- an explicit release checklist and changelog

## Quality Requirements

### Functional

- screenshots save to disk reliably
- file names are readable and sortable
- timeline entries match created artifacts
- session cleanup is not required for ordinary use

### UX

- install path is short
- configuration is optional for the first run
- output paths are always surfaced back to the user

### Code

- standard-library-first where practical
- low coupling between capture, storage, and tool registration
- tests cover default config and layout behavior

## Release Criteria

### v0.1

- working session model
- working checkpoint capture path and naming
- timeline logging
- skill draft included in repo

### v0.2

- optional short recording flow
- improved summaries
- examples and recipes for common prompts

### v1.0

- robust docs
- stronger error handling
- stable defaults for daily use
- enough examples that a new user can succeed quickly
