from __future__ import annotations

import math

from .models import Landmark, PoseFrame


def demo_frames(seconds: float = 10, fps: int = 15) -> list[PoseFrame]:
    """Create plausible landmark motion for UI/testing; not training data."""
    frames: list[PoseFrame] = []
    for i in range(round(seconds * fps)):
        t = i / fps
        phase = 2 * math.pi * t / 1.7
        lateral = 0.055 * math.sin(phase)
        asymmetry = 0.018 if math.sin(phase) > 0 else 0.0
        hip_y = .49 + .015 * math.cos(phase)
        knee_y = .68
        visibility = .94
        points = {
            "left_shoulder": Landmark(.44 + lateral * .35, .28, visibility),
            "right_shoulder": Landmark(.56 + lateral * .35, .285 + asymmetry, visibility),
            "left_hip": Landmark(.46 + lateral, hip_y, visibility),
            "right_hip": Landmark(.54 + lateral, hip_y + asymmetry, visibility),
            "left_knee": Landmark(.455 + lateral * .45, knee_y, visibility),
            "right_knee": Landmark(.545 + lateral * .45, knee_y, visibility),
            "left_ankle": Landmark(.445, .89, visibility),
            "right_ankle": Landmark(.555, .89, visibility),
        }
        frames.append(PoseFrame(t, points))
    return frames

