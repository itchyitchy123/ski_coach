#!/usr/bin/env python3
"""Download the MediaPipe Pose Landmarker Lite model artifact."""
from __future__ import annotations
import argparse
import hashlib
import urllib.request
from pathlib import Path

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("models/pose_landmarker_lite.task"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading Pose Landmarker Lite to {args.output} …")
    urllib.request.urlretrieve(MODEL_URL, args.output)
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(f"Downloaded {args.output.stat().st_size:,} bytes (sha256: {digest})")

if __name__ == "__main__":
    main()

