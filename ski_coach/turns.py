from __future__ import annotations

from .geometry import mean
from .models import FrameMetrics


def smooth(values: list[float], radius: int = 2) -> list[float]:
    return [mean(values[max(0, i-radius):i+radius+1]) for i in range(len(values))]


def segment_turns(
    frames: list[FrameMetrics], minimum_duration: float = 0.45, dead_zone: float = 0.025
) -> list[tuple[str, list[FrameMetrics]]]:
    """Split a frontal/downhill sequence using lateral hip-to-feet movement."""
    if len(frames) < 3:
        return []
    signal = smooth([f.balance_offset for f in frames])
    signs: list[int] = []
    last = 1 if signal[0] >= 0 else -1
    for value in signal:
        if abs(value) >= dead_zone:
            last = 1 if value > 0 else -1
        signs.append(last)

    groups: list[list[FrameMetrics]] = []
    start = 0
    for i in range(1, len(frames)):
        if signs[i] != signs[i - 1]:
            groups.append(frames[start:i])
            start = i
    groups.append(frames[start:])

    result: list[tuple[str, list[FrameMetrics]]] = []
    for group in groups:
        duration = group[-1].timestamp - group[0].timestamp
        if duration >= minimum_duration:
            direction = "left" if mean(f.balance_offset for f in group) < 0 else "right"
            result.append((direction, group))
    return result

