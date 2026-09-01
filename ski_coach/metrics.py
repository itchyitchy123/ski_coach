from __future__ import annotations

from .geometry import angle, distance, line_angle, midpoint
from .models import FrameMetrics, PoseFrame

REQUIRED = (
    "left_shoulder", "right_shoulder", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
)


def frame_metrics(frame: PoseFrame) -> FrameMetrics | None:
    if any(name not in frame.landmarks for name in REQUIRED):
        return None
    p = frame.landmarks
    shoulder_center = midpoint(p["left_shoulder"], p["right_shoulder"])
    hip_center = midpoint(p["left_hip"], p["right_hip"])
    foot_center = midpoint(p["left_ankle"], p["right_ankle"])
    shoulder_width = distance(p["left_shoulder"], p["right_shoulder"])
    if shoulder_width < 1e-5:
        return None

    # Lean is measured from image vertical; rotation is shoulders relative to hips.
    torso_lean = abs(line_angle(hip_center, shoulder_center) + 90.0)
    if torso_lean > 90:
        torso_lean = 180 - torso_lean
    shoulder_angle = line_angle(p["left_shoulder"], p["right_shoulder"])
    hip_angle = line_angle(p["left_hip"], p["right_hip"])
    rotation = abs((shoulder_angle - hip_angle + 90) % 180 - 90)

    return FrameMetrics(
        timestamp=frame.timestamp,
        left_knee_angle=angle(p["left_hip"], p["left_knee"], p["left_ankle"]),
        right_knee_angle=angle(p["right_hip"], p["right_knee"], p["right_ankle"]),
        torso_lean=torso_lean,
        counter_rotation=rotation,
        stance_ratio=distance(p["left_ankle"], p["right_ankle"]) / shoulder_width,
        balance_offset=(hip_center.x - foot_center.x) / shoulder_width,
        confidence=sum(p[name].visibility for name in REQUIRED) / len(REQUIRED),
    )

