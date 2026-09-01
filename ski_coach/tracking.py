"""Offline GPS session tracking and simple run/lift classification."""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class GPSPoint:
    timestamp: float
    latitude: float
    longitude: float
    altitude: float | None = None
    speed: float | None = None


@dataclass(frozen=True)
class TrackSegment:
    kind: str
    start_time: float
    end_time: float
    distance_m: float
    vertical_change_m: float


@dataclass(frozen=True)
class SessionSummary:
    points: int
    distance_m: float
    vertical_descent_m: float
    top_speed_mps: float
    average_run_speed_mps: float
    moving_seconds: float
    lift_seconds: float
    stopped_seconds: float
    runs: int
    lifts: int
    segments: list[TrackSegment]

    def to_dict(self) -> dict:
        return asdict(self)


def distance_m(a: GPSPoint, b: GPSPoint) -> float:
    radius = 6_371_000
    lat1, lat2 = math.radians(a.latitude), math.radians(b.latitude)
    dlat = lat2 - lat1
    dlon = math.radians(b.longitude - a.longitude)
    value = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * radius * math.asin(min(1, math.sqrt(value)))


def summarize_track(points: list[GPSPoint], *, moving_speed_mps: float = 1.5) -> SessionSummary:
    if len(points) < 2:
        return SessionSummary(len(points), 0, 0, 0, 0, 0, 0, 0, 0, 0, [])
    segments: list[TrackSegment] = []
    interval_speeds: list[float] = []
    run_speeds: list[float] = []
    total_distance = vertical_descent = moving = lift = stopped = 0.0
    current_kind: str | None = None
    current_start = 0
    current_distance = current_vertical = 0.0
    for index, (a, b) in enumerate(zip(points, points[1:])):
        duration = max(0.0, b.timestamp - a.timestamp)
        distance = distance_m(a, b)
        speed = b.speed if b.speed is not None else (distance / duration if duration else 0.0)
        vertical = (b.altitude - a.altitude) if a.altitude is not None and b.altitude is not None else 0.0
        # Uphill movement is treated as a lift; downhill movement is a run.
        kind = "lift" if speed >= moving_speed_mps and vertical > .3 else "run" if speed >= moving_speed_mps else "stopped"
        if kind != current_kind:
            if current_kind is not None:
                segments.append(TrackSegment(current_kind, points[current_start].timestamp, a.timestamp, round(current_distance, 1), round(current_vertical, 1)))
            current_kind, current_start, current_distance, current_vertical = kind, index, 0.0, 0.0
        current_distance += distance
        current_vertical += vertical
        total_distance += distance
        vertical_descent += max(0.0, -vertical)
        interval_speeds.append(speed)
        if kind == "run":
            moving += duration; run_speeds.append(speed)
        elif kind == "lift":
            lift += duration
        else:
            stopped += duration
    segments.append(TrackSegment(current_kind or "stopped", points[current_start].timestamp, points[-1].timestamp, round(current_distance, 1), round(current_vertical, 1)))
    return SessionSummary(
        points=len(points), distance_m=round(total_distance, 1), vertical_descent_m=round(vertical_descent, 1),
        top_speed_mps=round(max(interval_speeds, default=0.0), 2), average_run_speed_mps=round(sum(run_speeds) / len(run_speeds), 2) if run_speeds else 0.0,
        moving_seconds=round(moving, 2), lift_seconds=round(lift, 2), stopped_seconds=round(stopped, 2),
        runs=sum(segment.kind == "run" for segment in segments), lifts=sum(segment.kind == "lift" for segment in segments), segments=segments,
    )

