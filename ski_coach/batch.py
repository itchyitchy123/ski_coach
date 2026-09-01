"""Batch processing for the instructor-validation dataset layout."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .evaluation import EvaluationResult, evaluate_report
from .io import load_frames
from .pipeline import analyze_landmarks
from .pose import extract_video_landmarks


@dataclass(frozen=True)
class ClipResult:
    clip: str
    status: str
    report: dict[str, Any] | None = None
    evaluation: dict[str, Any] | None = None
    error: str | None = None


@dataclass(frozen=True)
class DatasetResult:
    clips: list[ClipResult]
    completed: int
    failed: int
    mean_direction_accuracy: float | None
    mean_count_error: float | None
    mean_score_error: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def _process_clip(directory: Path, model_path: str | Path | None) -> ClipResult:
    try:
        metadata = _load_json(directory / "metadata.json") if (directory / "metadata.json").exists() else {}
        labels_path = directory / "labels.json"
        labels = _load_json(labels_path) if labels_path.exists() else None
        landmark_path = directory / "landmarks.json"
        if landmark_path.exists():
            frames = load_frames(landmark_path)
        else:
            if not model_path:
                raise ValueError("model path is required when landmarks.json is absent")
            video_name = metadata.get("video")
            video_path = directory / video_name if video_name else next(directory.glob("*.mp4"), None)
            if not video_path or not video_path.exists():
                raise FileNotFoundError("no video found (set metadata.json video or add an .mp4 file)")
            frames = extract_video_landmarks(video_path, model_path)
        report = analyze_landmarks(
            frames,
            level=metadata.get("skier_level", "intermediate"),
            terrain=metadata.get("terrain", "groomer"),
            exercise=metadata.get("exercise", "parallel turns"),
        )
        evaluation = evaluate_report(report, labels).to_dict() if labels else None
        return ClipResult(directory.name, "completed", report.to_dict(), evaluation)
    except (OSError, TypeError, ValueError, KeyError, RuntimeError) as exc:
        return ClipResult(directory.name, "failed", error=str(exc))


def evaluate_dataset(root: str | Path, model_path: str | Path | None = None) -> DatasetResult:
    root = Path(root)
    if not root.is_dir():
        raise NotADirectoryError(root)
    directories = sorted(path for path in root.iterdir() if path.is_dir() and not path.name.startswith("."))
    clips = [_process_clip(directory, model_path) for directory in directories]
    completed = [clip for clip in clips if clip.status == "completed"]
    evaluations = [clip.evaluation for clip in completed if clip.evaluation]
    def average(key: str) -> float | None:
        values = [float(item[key]) for item in evaluations if item and item.get(key) is not None]
        return round(sum(values) / len(values), 3) if values else None
    return DatasetResult(
        clips=clips, completed=len(completed), failed=len(clips) - len(completed),
        mean_direction_accuracy=average("direction_accuracy"),
        mean_count_error=average("count_error"), mean_score_error=average("mean_score_error"),
    )

