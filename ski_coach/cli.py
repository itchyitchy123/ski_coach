from __future__ import annotations

import argparse
import json

from .demo import demo_frames
from .pipeline import analyze_landmarks
from .pose import extract_video_landmarks


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Analyze ski turns from a static-camera video")
    source = result.add_mutually_exclusive_group(required=True)
    source.add_argument("--demo", action="store_true", help="run with synthetic demo landmarks")
    source.add_argument("--video", help="path to MP4/MOV ski video")
    result.add_argument("--model", help="path to pose_landmarker.task (required with --video)")
    result.add_argument("--level", choices=["beginner", "intermediate", "advanced", "expert"], default="intermediate")
    result.add_argument("--terrain", choices=["groomer", "moguls", "powder", "steeps"], default="groomer")
    result.add_argument("--exercise", choices=["parallel turns", "carving", "short radius", "balance"], default="parallel turns")
    return result


def main() -> None:
    args = parser().parse_args()
    if args.video and not args.model:
        parser().error("--model is required with --video")
    frames = demo_frames() if args.demo else extract_video_landmarks(args.video, args.model)
    report = analyze_landmarks(frames, level=args.level, terrain=args.terrain, exercise=args.exercise)
    print(json.dumps(report.to_dict(), indent=2))


if __name__ == "__main__":
    main()

