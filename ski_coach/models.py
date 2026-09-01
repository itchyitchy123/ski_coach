from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

Direction = Literal["left", "right"]


@dataclass(frozen=True)
class Landmark:
    x: float
    y: float
    visibility: float = 1.0


@dataclass(frozen=True)
class PoseFrame:
    timestamp: float
    landmarks: dict[str, Landmark]
    pose_count: int = 1


@dataclass(frozen=True)
class FrameMetrics:
    timestamp: float
    left_knee_angle: float
    right_knee_angle: float
    torso_lean: float
    counter_rotation: float
    stance_ratio: float
    balance_offset: float
    confidence: float


@dataclass(frozen=True)
class TurnAnalysis:
    turn: int
    direction: Direction
    start_time: float
    end_time: float
    duration: float
    knee_flex: float
    torso_angle: float
    upper_body_rotation: float
    stance_ratio: float
    balance_offset: float
    score: int
    confidence: float


@dataclass(frozen=True)
class AnalysisReport:
    turns: int
    overall_score: int
    balance_score: int
    symmetry_score: int
    upper_body_score: int
    rhythm_score: int
    confidence: int
    data_quality: int
    quality_breakdown: dict[str, int]
    context: dict[str, str]
    turns_analysis: list[TurnAnalysis]
    feedback: list[str]
    warnings: list[str]

    def to_dict(self) -> dict:
        return asdict(self)
