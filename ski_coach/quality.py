"""Quality checks that gate interpretation of pose-derived coaching signals."""
from __future__ import annotations

from dataclasses import dataclass

from .metrics import REQUIRED
from .models import PoseFrame


@dataclass(frozen=True)
class QualitySummary:
    pose_coverage: int
    framing: int
    single_subject: int
    overall: int
    warnings: list[str]


def assess_quality(frames: list[PoseFrame], valid_frames: int) -> QualitySummary:
    if not frames:
        return QualitySummary(0, 0, 0, 0, ["No frames were available for quality checks."])
    visible = [[frame.landmarks[name] for name in REQUIRED if name in frame.landmarks] for frame in frames]
    visible = [points for points in visible if points]
    coverage = valid_frames / len(frames)
    framing = 0
    if visible:
        useful = 0
        for points in visible:
            width = max(p.x for p in points) - min(p.x for p in points)
            height = max(p.y for p in points) - min(p.y for p in points)
            useful += .12 <= width <= .85 and .25 <= height <= .98
        framing = round(useful / len(visible) * 100)
    counts = [getattr(frame, "pose_count", 1) for frame in frames]
    single = round(sum(count == 1 for count in counts) / len(counts) * 100)
    pose_coverage = round(coverage * 100)
    overall = round(.55 * pose_coverage + .30 * framing + .15 * single)
    warnings: list[str] = []
    if pose_coverage < 75:
        warnings.append("The skier is not visible in enough frames; use a steady camera and keep the full body in shot.")
    if framing < 70:
        warnings.append("Framing is too tight or too distant for reliable full-body measurements.")
    if single < 95:
        warnings.append("More than one person was detected in some frames; results may follow the wrong skier.")
    return QualitySummary(pose_coverage, framing, single, overall, warnings)

