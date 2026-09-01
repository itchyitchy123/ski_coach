from __future__ import annotations

from .feedback import make_feedback
from .metrics import frame_metrics
from .models import AnalysisReport, PoseFrame
from .scoring import report_scores, score_turn
from .turns import segment_turns


def analyze_landmarks(
    frames: list[PoseFrame], *, level: str = "intermediate", terrain: str = "groomer",
    exercise: str = "parallel turns",
) -> AnalysisReport:
    metrics = [m for frame in frames if (m := frame_metrics(frame)) is not None]
    groups = segment_turns(metrics)
    turns = [score_turn(i + 1, direction, group, level) for i, (direction, group) in enumerate(groups)]
    confidence = round(100 * sum(m.confidence for m in metrics) / len(metrics)) if metrics else 0
    coverage = len(metrics) / len(frames) if frames else 0.0
    quality = round(100 * (0.7 * coverage + 0.3 * confidence / 100))
    overall, balance, symmetry, upper, rhythm = report_scores(turns)
    feedback, warnings = make_feedback(turns, confidence)
    if frames and len(metrics) / len(frames) < .75:
        warnings.insert(0, "The skier was not fully visible in enough frames; results may be incomplete.")
    return AnalysisReport(
        turns=len(turns), overall_score=overall, balance_score=balance,
        symmetry_score=symmetry, upper_body_score=upper, rhythm_score=rhythm,
        confidence=confidence, data_quality=quality,
        context={"level": level, "terrain": terrain, "exercise": exercise},
        turns_analysis=turns, feedback=feedback, warnings=warnings,
    )
