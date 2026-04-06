from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .layout import SessionLayout
from .models import ArtifactDetails, ArtifactRecord
from .storage import load_artifact_details, load_timeline, save_artifact_details


class ArtifactReviewError(ValueError):
    """Raised when a review workflow cannot be completed from the available artifacts."""


def artifact_details_path(layout: SessionLayout, artifact_id: str) -> Path:
    return layout.details_dir / f"{artifact_id}.json"


def merge_artifact_details(
    artifact: ArtifactRecord,
    details: ArtifactDetails | None,
) -> ArtifactRecord:
    if details is None:
        return artifact
    return ArtifactRecord(
        artifact_id=artifact.artifact_id,
        session_id=artifact.session_id,
        artifact_type=artifact.artifact_type,
        created_at=artifact.created_at,
        label=artifact.label,
        reason=artifact.reason,
        path=artifact.path,
        step=artifact.step,
        target=artifact.target,
        tags=artifact.tags,
        notes=details.notes,
        ocr_text=details.ocr_text,
        source_artifact_id=details.source_artifact_id,
        redactions=details.redactions,
    )


def load_artifacts_with_details(layout: SessionLayout) -> list[ArtifactRecord]:
    artifacts = load_timeline(layout.timeline_path)
    enriched: list[ArtifactRecord] = []
    for artifact in artifacts:
        details = load_artifact_details(artifact_details_path(layout, artifact.artifact_id))
        enriched.append(merge_artifact_details(artifact, details))
    return enriched


def find_artifact(layout: SessionLayout, artifact_id: str) -> ArtifactRecord:
    for artifact in load_artifacts_with_details(layout):
        if artifact.artifact_id == artifact_id:
            return artifact
    raise FileNotFoundError(f"Artifact not found in session: {artifact_id}")


def find_latest_comparable_artifacts(
    layout: SessionLayout,
    artifact_type: str | None = None,
) -> tuple[ArtifactRecord, ArtifactRecord]:
    artifacts = load_artifacts_with_details(layout)
    if artifact_type is not None:
        candidates = [artifact for artifact in artifacts if artifact.artifact_type == artifact_type]
    else:
        if not artifacts:
            candidates = []
        else:
            latest_type = artifacts[-1].artifact_type
            candidates = [artifact for artifact in artifacts if artifact.artifact_type == latest_type]

    if len(candidates) < 2:
        review_target = artifact_type or "the latest artifact type"
        raise ArtifactReviewError(
            f"Need at least two artifacts for review using {review_target}, but found {len(candidates)}."
        )

    return candidates[-2], candidates[-1]


def append_artifact_note(layout: SessionLayout, artifact: ArtifactRecord, note: str) -> ArtifactDetails:
    path = artifact_details_path(layout, artifact.artifact_id)
    details = load_artifact_details(path) or ArtifactDetails.create(
        artifact_id=artifact.artifact_id,
        session_id=artifact.session_id,
        artifact_path=Path(artifact.path),
    )
    details.notes.append(note)
    details.updated_at = datetime.now().astimezone().isoformat()
    save_artifact_details(details, path)
    return details


def set_artifact_ocr_text(layout: SessionLayout, artifact: ArtifactRecord, text: str) -> ArtifactDetails:
    path = artifact_details_path(layout, artifact.artifact_id)
    details = load_artifact_details(path) or ArtifactDetails.create(
        artifact_id=artifact.artifact_id,
        session_id=artifact.session_id,
        artifact_path=Path(artifact.path),
    )
    details.ocr_text = text
    details.updated_at = datetime.now().astimezone().isoformat()
    save_artifact_details(details, path)
    return details


def set_artifact_redactions(
    layout: SessionLayout,
    artifact: ArtifactRecord,
    *,
    source_artifact_id: str,
    redactions: list[dict[str, int]],
) -> ArtifactDetails:
    path = artifact_details_path(layout, artifact.artifact_id)
    details = load_artifact_details(path) or ArtifactDetails.create(
        artifact_id=artifact.artifact_id,
        session_id=artifact.session_id,
        artifact_path=Path(artifact.path),
    )
    details.source_artifact_id = source_artifact_id
    details.redactions = redactions
    details.updated_at = datetime.now().astimezone().isoformat()
    save_artifact_details(details, path)
    return details
