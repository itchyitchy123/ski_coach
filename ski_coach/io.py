"""Stable JSON boundary for future mobile clients and integrations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Landmark, PoseFrame
from .sensors import SensorSample


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


def load_sensor_samples(path: str | Path) -> list[SensorSample]:
    with Path(path).open(encoding="utf-8") as handle:
        payload = json.load(handle)
    values = payload.get("samples", payload) if isinstance(payload, dict) else payload
    if not isinstance(values, list):
        raise ValueError("sensor payload must contain a 'samples' list")
    return _sensor_samples(values)


def _sensor_samples(values: list[dict]) -> list[SensorSample]:
    return [SensorSample(
        timestamp=float(item["timestamp"]),
        acceleration=tuple(float(v) for v in item.get("acceleration", (0, 0, 0))),
        rotation_rate=tuple(float(v) for v in item.get("rotation_rate", (0, 0, 0))),
        speed=float(item["speed"]) if item.get("speed") is not None else None,
        altitude=float(item["altitude"]) if item.get("altitude") is not None else None,
        heart_rate=float(item["heart_rate"]) if item.get("heart_rate") is not None else None,
    ) for item in values]


def sensor_samples_from_dict(payload: dict) -> list[SensorSample]:
    """Parse the same sensor schema from an API request."""
    values = payload.get("samples", [])
    if not isinstance(values, list):
        raise ValueError("sensor payload must contain a 'samples' list")
    return _sensor_samples(values)
