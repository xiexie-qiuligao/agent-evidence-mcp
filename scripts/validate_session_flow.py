from __future__ import annotations

import json
import sys
from pathlib import Path

from task_evidence_mcp.service import TaskEvidenceService


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    task_name = argv[0] if argv else "validation-run"
    workspace = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()

    service = TaskEvidenceService(workspace)
    start = service.start_session(task_name)
    capture = service.capture_checkpoint(
        start.layout.session_dir,
        label="validation-shot",
        reason="Validation checkpoint.",
    )
    end = service.end_session(start.layout.session_dir)

    payload = {
        "session_dir": str(start.layout.session_dir),
        "screenshot_path": capture.artifact.path,
        "summary_path": end.summary_path,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
