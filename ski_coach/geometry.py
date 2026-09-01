from __future__ import annotations

import math
from collections.abc import Iterable

from .models import Landmark


def angle(a: Landmark, vertex: Landmark, c: Landmark) -> float:
    """Return the smaller 2D angle a-vertex-c in degrees."""
    u = (a.x - vertex.x, a.y - vertex.y)
    v = (c.x - vertex.x, c.y - vertex.y)
    denominator = math.hypot(*u) * math.hypot(*v)
    if denominator == 0:
        return 0.0
    cosine = max(-1.0, min(1.0, (u[0] * v[0] + u[1] * v[1]) / denominator))
    return math.degrees(math.acos(cosine))


def midpoint(a: Landmark, b: Landmark) -> Landmark:
    return Landmark((a.x + b.x) / 2, (a.y + b.y) / 2, min(a.visibility, b.visibility))


def distance(a: Landmark, b: Landmark) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def line_angle(a: Landmark, b: Landmark) -> float:
    return math.degrees(math.atan2(b.y - a.y, b.x - a.x))


def mean(values: Iterable[float]) -> float:
    items = list(values)
    return sum(items) / len(items) if items else 0.0


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))

