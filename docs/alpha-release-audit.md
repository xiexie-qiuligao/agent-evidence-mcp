# Alpha Release Audit

This document is a release-candidate style snapshot of the repository as it stands locally on April 6, 2026.

## Current Recommendation

Recommended release label: `alpha`

Reason:

- the core product workflow is implemented
- packaging, tests, and build checks are in place
- Windows has the strongest local validation
- macOS and Linux now have meaningful backend coverage, but not the same validation depth

## What Looks Ready

- CLI entry point
- MCP server entry point
- Session lifecycle
- Screenshot capture
- Optional recording
- OCR enrichment hooks
- Review-oriented artifact comparison
- Redacted screenshot copies
- Package build and CI baseline
- Release-facing docs, changelog, and support matrix

## Local Verification Completed

- `python -m pytest -q`
- `python -m build --sdist --wheel`
- `python -m task_evidence_mcp.cli --help`
- Real local Windows screenshot validation
- Real local Windows recording validation
- Real local Windows redaction smoke flow

## Remaining Risks Before Broader Adoption

- macOS code paths are implemented, but this repository has not run a real local validation flow on macOS
- Linux screenshot support depends on desktop tools that may not exist on every environment
- Linux recording is still pending
- OCR quality and setup are backend-dependent

## Release Decision

If the goal is an honest first public release, this repository is ready for an alpha publish.

If the goal is stronger cross-platform confidence, the next highest-value step is real macOS validation, followed by Linux recording work.
