"""Stable JSON boundary for future mobile clients and integrations."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .models import Landmark, PoseFrame
from .sensors import SensorSample
from .tracking import GPSPoint

MAX_FRAMES = 100_000
MAX_LANDMARKS_PER_FRAME = 64
MAX_SENSOR_SAMPLES = 500_000
MAX_GPS_POINTS = 500_000


def _finite(value: Any, field: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


def _sequence(value: Any, field: str, limit: int) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    if len(value) > limit:
        raise ValueError(f"{field} exceeds the maximum of {limit} items")
    return value


def frames_from_dict(payload: dict[str, Any] | list[Any]) -> list[PoseFrame]:
    raw_frames = payload if isinstance(payload, list) else payload.get("frames", [])
    raw_frames = _sequence(raw_frames, "frames", MAX_FRAMES)
    frames: list[PoseFrame] = []
    previous_timestamp = -math.inf
    for number, item in enumerate(raw_frames, 1):
        if not isinstance(item, dict) or "timestamp" not in item:
            raise ValueError(f"frame {number} requires a numeric timestamp and landmarks")
        timestamp = _finite(item["timestamp"], f"frame {number} timestamp")
        if timestamp < 0 or timestamp < previous_timestamp:
            raise ValueError(f"frame {number} timestamp must be non-negative and ordered")
        previous_timestamp = timestamp
        raw_landmarks = item.get("landmarks", {})
        if not isinstance(raw_landmarks, dict):
            raise ValueError(f"frame {number} landmarks must be an object")
        if len(raw_landmarks) > MAX_LANDMARKS_PER_FRAME:
            raise ValueError(f"frame {number} exceeds the maximum of {MAX_LANDMARKS_PER_FRAME} landmarks")
        landmarks = {
            name: Landmark(
                _finite(value["x"], f"frame {number} landmark {name}.x"),
                _finite(value["y"], f"frame {number} landmark {name}.y"),
                _finite(value.get("visibility", 1.0), f"frame {number} landmark {name}.visibility"),
            )
            for name, value in raw_landmarks.items()
            if isinstance(value, dict) and "x" in value and "y" in value
        }
        if len(landmarks) != len(raw_landmarks):
            raise ValueError(f"frame {number} landmarks must contain x and y coordinates")
        visibility = [point.visibility for point in landmarks.values()]
        if any(value < 0 or value > 1 for value in visibility):
            raise ValueError(f"frame {number} landmark visibility must be between 0 and 1")
        pose_count = int(item.get("pose_count", 1))
        if pose_count < 0 or pose_count > 32:
            raise ValueError(f"frame {number} pose_count must be between 0 and 32")
        frames.append(PoseFrame(timestamp, landmarks, pose_count))
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
    values = _sequence(values, "sensor samples", MAX_SENSOR_SAMPLES)
    result: list[SensorSample] = []
    previous_timestamp = -math.inf
    for number, item in enumerate(values, 1):
        if not isinstance(item, dict):
            raise ValueError(f"sensor sample {number} must be an object")
        timestamp = _finite(item["timestamp"], f"sensor sample {number} timestamp")
        if timestamp < 0 or timestamp < previous_timestamp:
            raise ValueError(f"sensor sample {number} timestamp must be non-negative and ordered")
        previous_timestamp = timestamp
        acceleration = tuple(_finite(v, f"sensor sample {number} acceleration") for v in item.get("acceleration", (0, 0, 0)))
        rotation_rate = tuple(_finite(v, f"sensor sample {number} rotation_rate") for v in item.get("rotation_rate", (0, 0, 0)))
        if len(acceleration) != 3 or len(rotation_rate) != 3:
            raise ValueError(f"sensor sample {number} vectors must contain three values")
        result.append(SensorSample(
            timestamp=timestamp, acceleration=acceleration, rotation_rate=rotation_rate,
            speed=_finite(item["speed"], f"sensor sample {number} speed") if item.get("speed") is not None else None,
            altitude=_finite(item["altitude"], f"sensor sample {number} altitude") if item.get("altitude") is not None else None,
            heart_rate=_finite(item["heart_rate"], f"sensor sample {number} heart_rate") if item.get("heart_rate") is not None else None,
        ))
    return result


def sensor_samples_from_dict(payload: dict) -> list[SensorSample]:
    """Parse the same sensor schema from an API request."""
    values = payload.get("samples", [])
    if not isinstance(values, list):
        raise ValueError("sensor payload must contain a 'samples' list")
    return _sensor_samples(values)


def load_gps_points(path: str | Path) -> list[GPSPoint]:
    with Path(path).open(encoding="utf-8") as handle:
        payload = json.load(handle)
    values = payload.get("points", payload) if isinstance(payload, dict) else payload
    if not isinstance(values, list):
        raise ValueError("GPS payload must contain a 'points' list")
    return gps_points_from_dict({"points": values})


def gps_points_from_dict(payload: dict) -> list[GPSPoint]:
    values = payload.get("points", [])
    values = _sequence(values, "GPS points", MAX_GPS_POINTS)
    result: list[GPSPoint] = []
    previous_timestamp = -math.inf
    for number, item in enumerate(values, 1):
        if not isinstance(item, dict):
            raise ValueError(f"GPS point {number} must be an object")
        timestamp = _finite(item["timestamp"], f"GPS point {number} timestamp")
        latitude = _finite(item["latitude"], f"GPS point {number} latitude")
        longitude = _finite(item["longitude"], f"GPS point {number} longitude")
        if timestamp < 0 or timestamp < previous_timestamp:
            raise ValueError(f"GPS point {number} timestamp must be non-negative and ordered")
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            raise ValueError(f"GPS point {number} has invalid coordinates")
        previous_timestamp = timestamp
        result.append(GPSPoint(timestamp, latitude, longitude,
                               _finite(item["altitude"], f"GPS point {number} altitude") if item.get("altitude") is not None else None,
                               _finite(item["speed"], f"GPS point {number} speed") if item.get("speed") is not None else None))
    return result
