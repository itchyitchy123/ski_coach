"""Render a lightweight review overlay without changing the analysis engine."""
from __future__ import annotations

from pathlib import Path

from .models import PoseFrame


def render_pose_overlay(video_path: str | Path, frames: list[PoseFrame], output_path: str | Path) -> None:
    try:
        import cv2
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install video dependencies with: pip install -e '.[video]'") from exc
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    width, height = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    by_time = {round(frame.timestamp, 2): frame for frame in frames}
    index = 0
    try:
        while True:
            ok, image = capture.read()
            if not ok:
                break
            timestamp = round(index / fps, 2)
            frame = by_time.get(timestamp)
            if frame:
                for point in frame.landmarks.values():
                    color = (60, 220, 120) if point.visibility >= .5 else (60, 120, 220)
                    cv2.circle(image, (round(point.x * width), round(point.y * height)), 5, color, -1)
                cv2.putText(image, f"t={timestamp:.2f}s  pose={frame.pose_count}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, .8, (255, 255, 255), 2)
            writer.write(image)
            index += 1
    finally:
        capture.release()
        writer.release()

