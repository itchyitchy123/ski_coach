"""Stable JSON boundary for future mobile clients and integrations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Landmark, PoseFrame


def frames_from_dict(payload: dict[str, Any]) -> list[PoseFrame]:
    raw_frames = payload.get("frames", payload if isinstance(payload, list) else [])
    if not isinstance(raw_frames, list):
        raise ValueError("landmark payload must contain a 'frames' list")
    frames: list[PoseFrame] = []
    for item in raw_frames:
        if not isinstance(item, dict) or "timestamp" not in item:
            raise ValueError("each frame requires a numeric timestamp and landmarks")
        raw_landmarks = item.get("landmarks", {})
        landmarks = {
            name: Landmark(float(value["x"]), float(value["y"]), float(value.get("visibility", 1.0)))
            for name, value in raw_landmarks.items()
        }
        frames.append(PoseFrame(float(item["timestamp"]), landmarks, int(item.get("pose_count", 1))))
    return frames


def load_frames(path: str | Path) -> list[PoseFrame]:
    with Path(path).open(encoding="utf-8") as handle:
        return frames_from_dict(json.load(handle))
