"""Compare predicted turns with a small instructor-labelled JSON file."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from .models import AnalysisReport


def validate_labels(labels: dict[str, Any]) -> None:
    turns = labels.get("turns")
    if not isinstance(turns, list):
        raise ValueError("labels must contain a 'turns' list")
    previous_end = -1.0
    for number, turn in enumerate(turns, 1):
        if not isinstance(turn, dict):
            raise ValueError(f"turn {number} must be an object")
        direction = str(turn.get("direction", "")).lower()
        if direction not in {"left", "right"}:
            raise ValueError(f"turn {number} direction must be left or right")
        if "start_time" in turn or "end_time" in turn:
            start, end = float(turn.get("start_time", -1)), float(turn.get("end_time", -1))
            if start < 0 or end <= start or start < previous_end:
                raise ValueError(f"turn {number} has invalid or overlapping timestamps")
            previous_end = end


@dataclass(frozen=True)
class EvaluationResult:
    predicted_turns: int
    labeled_turns: int
    direction_accuracy: float
    count_error: int
    mean_score_error: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_report(report: AnalysisReport, labels: dict[str, Any]) -> EvaluationResult:
    validate_labels(labels)
    expected = labels.get("turns", [])
    predicted = report.turns_analysis
    pairs = zip(predicted, expected)
    directions = [actual.direction == str(label.get("direction", "")).lower() for actual, label in pairs]
    scores = [abs(actual.score - float(label["score"])) for actual, label in zip(predicted, expected) if "score" in label]
    return EvaluationResult(
        predicted_turns=len(predicted), labeled_turns=len(expected),
        direction_accuracy=round(sum(directions) / len(directions), 3) if directions else 0.0,
        count_error=len(predicted) - len(expected),
        mean_score_error=round(sum(scores) / len(scores), 2) if scores else None,
    )
