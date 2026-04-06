from __future__ import annotations

from .compare import compare_artifacts
from .models import ArtifactRecord, SessionRecord


def _count_artifacts_by_type(artifacts: list[ArtifactRecord]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for artifact in artifacts:
        counts[artifact.artifact_type] = counts.get(artifact.artifact_type, 0) + 1
    return counts


def _recent_highlights(artifacts: list[ArtifactRecord], limit: int = 5) -> list[ArtifactRecord]:
    if len(artifacts) <= limit:
        return artifacts
    return artifacts[-limit:]


def _latest_pair_by_type(
    artifacts: list[ArtifactRecord],
    artifact_type: str,
) -> tuple[ArtifactRecord, ArtifactRecord] | None:
    matches = [artifact for artifact in artifacts if artifact.artifact_type == artifact_type]
    if len(matches) < 2:
        return None
    return matches[-2], matches[-1]


def _append_review_signals(lines: list[str], artifacts: list[ArtifactRecord]) -> None:
    review_pairs: list[tuple[str, tuple[ArtifactRecord, ArtifactRecord]]] = []
    for artifact_type in ("screenshot", "recording"):
        pair = _latest_pair_by_type(artifacts, artifact_type)
        if pair is not None:
            review_pairs.append((artifact_type, pair))

    if not review_pairs:
        return

    lines.extend(
        [
            "",
            "## Review Signals",
            "",
        ]
    )
    for artifact_type, (older, newer) in review_pairs:
        comparison = compare_artifacts(older, newer)
        lines.append(
            f"- Latest `{artifact_type}` pair: `{older.label}` -> `{newer.label}` | verdict: `{comparison.verdict}`"
        )
        changed_fields = ", ".join(comparison.changed_fields) if comparison.changed_fields else "none"
        lines.append(f"  changed fields: {changed_fields}")
        if comparison.review_focus:
            lines.append(f"  review focus: {comparison.review_focus[0]}")


def build_summary_markdown(
    session: SessionRecord,
    artifacts: list[ArtifactRecord],
) -> str:
    counts = _count_artifacts_by_type(artifacts)
    screenshot_count = counts.get("screenshot", 0)
    recording_count = counts.get("recording", 0)
    lines = [
        f"# Session Summary: {session.task_name}",
        "",
        f"- Session ID: `{session.session_id}`",
        f"- Status: `{session.status}`",
        f"- Artifact count: `{len(artifacts)}`",
        f"- Screenshot count: `{screenshot_count}`",
        f"- Recording count: `{recording_count}`",
        f"- Created at: `{session.created_at}`",
        f"- Artifacts root: `{session.artifacts_root}`",
    ]

    if session.closed_at:
        lines.append(f"- Closed at: `{session.closed_at}`")

    if not artifacts:
        lines.extend(
            [
                "",
                "## Timeline",
                "",
            ]
        )
        lines.append("No artifacts were captured in this session.")
        lines.append("")
        return "\n".join(lines)

    lines.extend(
        [
            "## Highlights",
            "",
        ]
    )
    for artifact in _recent_highlights(artifacts):
        lines.append(f"- `{artifact.label}` (`{artifact.artifact_type}`) -> `{artifact.path}`")

    _append_review_signals(lines, artifacts)

    lines.extend(
        [
            "",
            "## Timeline",
            "",
        ]
    )

    for artifact in artifacts:
        step_suffix = f" | step: `{artifact.step}`" if artifact.step else ""
        tag_suffix = f" | tags: `{', '.join(artifact.tags)}`" if artifact.tags else ""
        reason = artifact.reason or "No reason provided."
        lines.append(
            f"- `{artifact.created_at}` | `{artifact.label}` | `{artifact.artifact_type}`{step_suffix}{tag_suffix}"
        )
        lines.append(f"  path: `{artifact.path}`")
        lines.append(f"  reason: {reason}")
        if artifact.notes:
            lines.append(f"  notes: {' | '.join(artifact.notes)}")
        if artifact.ocr_text:
            preview = artifact.ocr_text[:160].replace("\n", " ").strip()
            lines.append(f"  ocr: {preview}")
        if artifact.source_artifact_id:
            lines.append(f"  source artifact: `{artifact.source_artifact_id}`")
        if artifact.redactions:
            lines.append(f"  redactions: {len(artifact.redactions)} region(s)")

    lines.append("")
    return "\n".join(lines)
