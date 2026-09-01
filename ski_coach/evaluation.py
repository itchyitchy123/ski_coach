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
    matched_turns: int
    mean_start_error: float | None
    mean_end_error: float | None
    mean_timing_error: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_report(report: AnalysisReport, labels: dict[str, Any]) -> EvaluationResult:
    validate_labels(labels)
    expected = labels.get("turns", [])
    predicted = report.turns_analysis
    # Greedily match each label to the nearest unused prediction, preferring direction.
    used: set[int] = set()
    matches: list[tuple[Any, dict[str, Any]]] = []
    for label in expected:
        direction = str(label.get("direction", "")).lower()
        start = float(label.get("start_time", 0))
        candidates = [i for i in range(len(predicted)) if i not in used]
        if not candidates:
            continue
        index = min(candidates, key=lambda i: (predicted[i].direction != direction, abs(predicted[i].start_time - start)))
        used.add(index)
        matches.append((predicted[index], label))
    directions = [actual.direction == str(label.get("direction", "")).lower() for actual, label in matches]
    scores = [abs(actual.score - float(label["score"])) for actual, label in matches if "score" in label]
    starts = [abs(actual.start_time - float(label["start_time"])) for actual, label in matches if "start_time" in label]
    ends = [abs(actual.end_time - float(label["end_time"])) for actual, label in matches if "end_time" in label]
    timing = starts + ends
    average = lambda values: round(sum(values) / len(values), 3) if values else None
    return EvaluationResult(
        predicted_turns=len(predicted), labeled_turns=len(expected),
        direction_accuracy=round(sum(directions) / len(directions), 3) if directions else 0.0,
        count_error=len(predicted) - len(expected),
        mean_score_error=round(sum(scores) / len(scores), 2) if scores else None,
        matched_turns=len(matches), mean_start_error=average(starts),
        mean_end_error=average(ends), mean_timing_error=average(timing),
    )
