from __future__ import annotations

import statistics

from .geometry import clamp, mean
from .models import FrameMetrics, TurnAnalysis

LEVEL_TARGETS = {
    "beginner": (105.0, 170.0),
    "intermediate": (95.0, 165.0),
    "advanced": (85.0, 160.0),
    "expert": (80.0, 160.0),
}


def range_score(value: float, low: float, high: float, softness: float) -> float:
    if low <= value <= high:
        return 100.0
    return clamp(100 - min(abs(value-low), abs(value-high)) * softness)


def score_turn(index: int, direction: str, frames: list[FrameMetrics], level: str) -> TurnAnalysis:
    knee = mean(min(f.left_knee_angle, f.right_knee_angle) for f in frames)
    lean = mean(f.torso_lean for f in frames)
    rotation = mean(f.counter_rotation for f in frames)
    stance = mean(f.stance_ratio for f in frames)
    balance = mean(abs(f.balance_offset) for f in frames)
    low, high = LEVEL_TARGETS.get(level, LEVEL_TARGETS["intermediate"])
    components = [
        range_score(knee, low, high, 1.5),
        range_score(lean, 3, 28, 2.0),
        range_score(rotation, 0, 18, 2.5),
        range_score(stance, 0.45, 1.35, 70),
        range_score(balance, 0, 0.65, 100),
    ]
    return TurnAnalysis(
        turn=index,
        direction=direction,  # type: ignore[arg-type]
        start_time=round(frames[0].timestamp, 2),
        end_time=round(frames[-1].timestamp, 2),
        duration=round(frames[-1].timestamp - frames[0].timestamp, 2),
        knee_flex=round(knee, 1), torso_angle=round(lean, 1),
        upper_body_rotation=round(rotation, 1), stance_ratio=round(stance, 2),
        balance_offset=round(balance, 2), score=round(mean(components)),
        confidence=round(mean(f.confidence for f in frames), 2),
    )


def report_scores(turns: list[TurnAnalysis]) -> tuple[int, int, int, int, int]:
    if not turns:
        return 0, 0, 0, 0, 0
    balance = round(mean(range_score(t.balance_offset, 0, 0.65, 100) for t in turns))
    upper = round(mean(range_score(t.upper_body_rotation, 0, 18, 2.5) for t in turns))
    durations = [t.duration for t in turns]
    rhythm = round(clamp(100 - (statistics.pstdev(durations) / max(mean(durations), .01)) * 160))
    left = [t.score for t in turns if t.direction == "left"]
    right = [t.score for t in turns if t.direction == "right"]
    symmetry = round(clamp(100 - abs(mean(left) - mean(right)) * 2)) if left and right else 0
    overall = round(mean([balance, upper, rhythm, symmetry or mean(t.score for t in turns)]))
    return overall, balance, symmetry, upper, rhythm

