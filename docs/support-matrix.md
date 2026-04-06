# Support Matrix

This matrix is meant to help first-time users quickly understand what is implemented, what is locally validated, and where platform caveats still exist.

## Current Alpha Snapshot

| Capability | Windows | macOS | Linux |
| --- | --- | --- | --- |
| Session lifecycle | Implemented and locally validated | Implemented by shared code path | Implemented by shared code path |
| Screenshot capture | Implemented and locally validated | Implemented, not locally validated in this repo | Implemented, not locally validated in this repo |
| Screenshot redaction | Implemented and locally validated | Not yet implemented | Not yet implemented |
| Recording start/stop | Implemented and locally validated | Implemented, not locally validated in this repo | Implemented, not locally validated in this repo |
| OCR enrichment | Implemented behind optional backend | Implemented behind optional backend | Implemented behind optional backend |
| MCP server | Implemented and tested | Implemented by shared code path | Implemented by shared code path |
| CLI | Implemented and tested | Implemented by shared code path | Implemented by shared code path |

## Platform Notes

### Windows

- This is the strongest platform today.
- Screenshot capture, redaction, and recording have all been exercised locally in this repository.

### macOS

- Screenshot capture uses native `screencapture`.
- Recording uses `ffmpeg` with `avfoundation`.
- The code path exists, but this repository has not yet run a real local macOS validation flow.

### Linux

- Screenshot capture currently depends on one of:
  - `gnome-screenshot`
  - `grim`
  - ImageMagick `import`
- Recording currently uses `ffmpeg` with `x11grab`.
- Linux support should be treated as early and environment-dependent until real validation is added.

## Practical Recommendation

If you are choosing one platform for early adoption, prefer Windows first.

If you are trying macOS or Linux, expect to verify local tool availability and be prepared to override platform-specific config values.
