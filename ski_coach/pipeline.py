from __future__ import annotations

from .feedback import make_feedback
from .metrics import frame_metrics
from .models import AnalysisReport, PoseFrame
from .quality import assess_quality
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
    quality_summary = assess_quality(frames, len(metrics))
    quality = quality_summary.overall
    overall, balance, symmetry, upper, rhythm = report_scores(turns)
    feedback, warnings = make_feedback(turns, confidence)
    warnings = quality_summary.warnings + warnings
    return AnalysisReport(
        turns=len(turns), overall_score=overall, balance_score=balance,
        symmetry_score=symmetry, upper_body_score=upper, rhythm_score=rhythm,
        confidence=confidence, data_quality=quality,
        quality_breakdown={"pose_coverage": quality_summary.pose_coverage, "framing": quality_summary.framing, "single_subject": quality_summary.single_subject},
        context={"level": level, "terrain": terrain, "exercise": exercise},
        turns_analysis=turns, feedback=feedback, warnings=warnings,
    )
