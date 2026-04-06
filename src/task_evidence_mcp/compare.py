from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path

from .models import ArtifactRecord


def _file_size(path: str) -> int | None:
    file_path = Path(path)
    if not file_path.exists():
        return None
    return file_path.stat().st_size


def _file_hash(path: str) -> str | None:
    file_path = Path(path)
    if not file_path.exists():
        return None
    digest = sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _preview_text(text: str | None, limit: int = 120) -> str | None:
    if not text:
        return None
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."


@dataclass
class ArtifactComparison:
    from_artifact_id: str
    to_artifact_id: str
    same_artifact_type: bool
    from_label: str
    to_label: str
    from_path: str
    to_path: str
    from_size: int | None
    to_size: int | None
    size_delta: int | None
    hash_changed: bool | None
    label_changed: bool
    reason_changed: bool
    step_changed: bool
    target_changed: bool
    tags_changed: bool
    source_artifact_changed: bool
    redactions_changed: bool
    notes_changed: bool
    ocr_changed: bool
    verdict: str
    changed_fields: list[str]
    review_focus: list[str]
    from_ocr_preview: str | None
    to_ocr_preview: str | None
    summary: str

    def to_dict(self) -> dict:
        return asdict(self)


def compare_artifacts(
    older: ArtifactRecord,
    newer: ArtifactRecord,
) -> ArtifactComparison:
    from_size = _file_size(older.path)
    to_size = _file_size(newer.path)
    size_delta = None
    if from_size is not None and to_size is not None:
        size_delta = to_size - from_size

    from_hash = _file_hash(older.path)
    to_hash = _file_hash(newer.path)
    hash_changed = None
    if from_hash is not None and to_hash is not None:
        hash_changed = from_hash != to_hash

    label_changed = older.label != newer.label
    reason_changed = older.reason != newer.reason
    step_changed = older.step != newer.step
    target_changed = older.target != newer.target
    tags_changed = older.tags != newer.tags
    source_artifact_changed = older.source_artifact_id != newer.source_artifact_id
    redactions_changed = older.redactions != newer.redactions
    notes_changed = older.notes != newer.notes
    ocr_changed = (older.ocr_text or "") != (newer.ocr_text or "")
    same_artifact_type = older.artifact_type == newer.artifact_type

    changed_fields: list[str] = []
    if not same_artifact_type:
        changed_fields.append("artifact_type")
    if label_changed:
        changed_fields.append("label")
    if reason_changed:
        changed_fields.append("reason")
    if step_changed:
        changed_fields.append("step")
    if target_changed:
        changed_fields.append("target")
    if tags_changed:
        changed_fields.append("tags")
    if source_artifact_changed:
        changed_fields.append("source_artifact_id")
    if redactions_changed:
        changed_fields.append("redactions")
    if notes_changed:
        changed_fields.append("notes")
    if ocr_changed:
        changed_fields.append("ocr_text")
    if hash_changed is True:
        changed_fields.append("binary_content")
    elif hash_changed is None and size_delta not in (None, 0):
        changed_fields.append("file_size")

    content_changed = hash_changed is True or "file_size" in changed_fields or ocr_changed
    metadata_changed = any(
        field in changed_fields
        for field in ["label", "reason", "step", "target", "tags", "notes"]
    )

    if not same_artifact_type:
        verdict = "type_changed"
    elif content_changed:
        verdict = "content_changed"
    elif metadata_changed:
        verdict = "metadata_changed"
    elif hash_changed is False:
        verdict = "unchanged"
    else:
        verdict = "inconclusive"

    review_focus: list[str] = []
    if verdict == "type_changed":
        review_focus.append(
            "Artifacts use different capture types. Confirm the workflow intentionally switched between screenshot and recording."
        )
    if hash_changed is True:
        review_focus.append(
            "Binary content changed. Open both artifacts to verify the visual or motion difference."
        )
    elif hash_changed is None:
        review_focus.append(
            "Binary comparison was unavailable. Check that both artifact files still exist on disk before relying on this diff."
        )
    if ocr_changed:
        review_focus.append(
            "OCR text changed. Review visible text, values, or status messages between the two checkpoints."
        )
    if notes_changed:
        review_focus.append(
            "Attached notes changed. Review analyst commentary for additional context that may not be visible in the media alone."
        )
    if redactions_changed:
        review_focus.append(
            "Redaction regions changed. Confirm the redacted copy still hides the intended sensitive content without obscuring needed evidence."
        )
    metadata_fields = [
        field
        for field in ["label", "reason", "step", "target", "tags", "source_artifact_id", "redactions"]
        if field in changed_fields
    ]
    if metadata_fields:
        review_focus.append(
            "Metadata changed. Confirm the checkpoints still describe the same workflow moment: "
            + ", ".join(metadata_fields)
            + "."
        )
    if not review_focus and verdict == "unchanged":
        review_focus.append(
            "No meaningful differences were detected. Reuse either artifact unless a human reviewer expects a subtle visual change."
        )
    if not review_focus and verdict == "inconclusive":
        review_focus.append(
            "Comparison was inconclusive. Open both artifacts manually before drawing conclusions."
        )

    summary_parts = [f"verdict: {verdict.replace('_', ' ')}"]
    if changed_fields:
        summary_parts.append(f"changed fields: {', '.join(changed_fields)}")
    else:
        summary_parts.append("changed fields: none")
    summary_parts.append(
        "artifact type unchanged" if same_artifact_type else "artifact type changed"
    )
    summary_parts.append(
        "hash changed"
        if hash_changed
        else "hash unchanged"
        if hash_changed is not None
        else "hash unavailable"
    )
    if size_delta is not None:
        summary_parts.append(f"size delta {size_delta}")

    return ArtifactComparison(
        from_artifact_id=older.artifact_id,
        to_artifact_id=newer.artifact_id,
        same_artifact_type=same_artifact_type,
        from_label=older.label,
        to_label=newer.label,
        from_path=older.path,
        to_path=newer.path,
        from_size=from_size,
        to_size=to_size,
        size_delta=size_delta,
        hash_changed=hash_changed,
        label_changed=label_changed,
        reason_changed=reason_changed,
        step_changed=step_changed,
        target_changed=target_changed,
        tags_changed=tags_changed,
        source_artifact_changed=source_artifact_changed,
        redactions_changed=redactions_changed,
        notes_changed=notes_changed,
        ocr_changed=ocr_changed,
        verdict=verdict,
        changed_fields=changed_fields,
        review_focus=review_focus,
        from_ocr_preview=_preview_text(older.ocr_text),
        to_ocr_preview=_preview_text(newer.ocr_text),
        summary="; ".join(summary_parts),
    )
