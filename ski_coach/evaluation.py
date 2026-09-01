"""Compare predicted turns with a small instructor-labelled JSON file."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from .models import AnalysisReport


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
    expected = labels.get("turns", [])
    if not isinstance(expected, list):
        raise ValueError("labels must contain a 'turns' list")
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

