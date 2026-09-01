"""Device-neutral motion samples and lightweight offline turn detection."""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class SensorSample:
    timestamp: float
    acceleration: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation_rate: tuple[float, float, float] = (0.0, 0.0, 0.0)
    speed: float | None = None
    altitude: float | None = None
    heart_rate: float | None = None


def align_timestamps(samples: list[SensorSample], offset_seconds: float) -> list[SensorSample]:
    """Return samples shifted into the video clock (positive offset moves forward)."""
    return [SensorSample(s.timestamp + offset_seconds, s.acceleration, s.rotation_rate, s.speed, s.altitude, s.heart_rate) for s in samples]


def detect_sensor_turns(samples: list[SensorSample], minimum_duration: float = .45) -> list[tuple[str, float, float]]:
    """Detect coarse turns from the sign of the yaw-rate (z-axis) signal."""
    if len(samples) < 3:
        return []
    groups: list[list[SensorSample]] = []
    start = 0
    previous = 1 if samples[0].rotation_rate[2] >= 0 else -1
    for index, sample in enumerate(samples[1:], 1):
        current = 1 if sample.rotation_rate[2] >= 0 else -1
        if current != previous:
            groups.append(samples[start:index])
            start, previous = index, current
    groups.append(samples[start:])
    result = []
    for group in groups:
        if group[-1].timestamp - group[0].timestamp >= minimum_duration:
            result.append(("right" if mean(s.rotation_rate[2] for s in group) > 0 else "left", group[0].timestamp, group[-1].timestamp))
    return result


def summarize_fusion(visual_turns: list, samples: list[SensorSample]) -> dict[str, float | int | bool | None]:
    sensor_turns = detect_sensor_turns(samples)
    count = min(len(visual_turns), len(sensor_turns))
    agreements = sum(visual_turns[i].direction == sensor_turns[i][0] for i in range(count))
    timing = [abs(visual_turns[i].start_time - sensor_turns[i][1]) + abs(visual_turns[i].end_time - sensor_turns[i][2]) for i in range(count)]
    return {
        "available": True, "sensor_turns": len(sensor_turns), "matched_turns": count,
        "direction_agreement": round(agreements / count, 3) if count else None,
        "mean_boundary_error": round(mean(timing) / 2, 3) if timing else None,
    }

