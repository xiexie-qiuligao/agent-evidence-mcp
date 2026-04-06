# Roadmap

This roadmap is intentionally product-oriented rather than just code-oriented.

## Current State

The project already supports:

- session-based screenshot capture
- optional recording
- MCP and CLI interfaces
- note and OCR enrichment for artifacts
- real Windows validation for screenshot and recording flows

## Next Product Milestones

### 1. Artifact Review Workflows

Move beyond capture into review:

- richer `compare_artifacts`
- low-friction latest-artifact review flows
- better summary narratives
- clearer highlighting of important changes

### 2. OCR Expansion

Turn OCR from a backend hook into a stronger workflow:

- more than one OCR provider
- configurable language support
- better OCR summaries and comparisons

### 3. Safety And Privacy

Add features that help the project work in more real environments:

- redaction hooks and shareable redacted copies
- safer handling of sensitive UI content
- clearer review guidance for private data

### 4. Platform Expansion

Keep Windows stable while expanding carefully:

- macOS recording validation
- Linux capture validation and recording strategy
- stable session and tool contracts across platforms

### 5. Release Maturity

Make the repository easier for strangers to trust:

- more examples
- release notes discipline
- clearer contribution pathways

## Product Rule

Every new capability should improve one of these three outcomes:

- capture better evidence
- review evidence more effectively
- keep the user experience predictable and lightweight
