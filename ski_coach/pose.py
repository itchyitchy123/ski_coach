from __future__ import annotations

from pathlib import Path

from .models import Landmark, PoseFrame

LANDMARK_NAMES = {
    11: "left_shoulder", 12: "right_shoulder", 23: "left_hip", 24: "right_hip",
    25: "left_knee", 26: "right_knee", 27: "left_ankle", 28: "right_ankle",
}


def extract_video_landmarks(
    video_path: str | Path, model_path: str | Path, sample_fps: float = 10.0,
) -> list[PoseFrame]:
    """Extract one skier's landmarks using MediaPipe Pose Landmarker video mode."""
    try:
        import cv2
        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions
        from mediapipe.tasks.python import vision
    except ImportError as exc:
        raise RuntimeError("Install video dependencies with: pip install -e '.[video]'") from exc

    model = Path(model_path)
    if not model.is_file():
        raise FileNotFoundError(f"Pose model not found: {model}")
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    source_fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    every = max(1, round(source_fps / sample_fps))
    options = vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(model)),
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=.5,
        min_pose_presence_confidence=.5,
        min_tracking_confidence=.5,
    )
    output: list[PoseFrame] = []
    frame_index = 0
    try:
        with vision.PoseLandmarker.create_from_options(options) as detector:
            while True:
                ok, bgr = capture.read()
                if not ok:
                    break
                if frame_index % every == 0:
                    timestamp_ms = round(frame_index * 1000 / source_fps)
                    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                    result = detector.detect_for_video(
                        mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), timestamp_ms
                    )
                    if result.pose_landmarks:
                        pose = result.pose_landmarks[0]
                        landmarks = {
                            name: Landmark(pose[index].x, pose[index].y, pose[index].visibility or 0.0)
                            for index, name in LANDMARK_NAMES.items()
                        }
                        output.append(PoseFrame(timestamp_ms / 1000, landmarks, pose_count=len(result.pose_landmarks)))
                frame_index += 1
    finally:
        capture.release()
    return output
