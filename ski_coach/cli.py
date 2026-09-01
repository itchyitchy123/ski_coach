from __future__ import annotations

import argparse
import json
from pathlib import Path

from .demo import demo_frames
from .io import load_frames, load_sensor_samples
from .evaluation import evaluate_report
from .overlay import render_pose_overlay
from .batch import evaluate_dataset
from .pipeline import analyze_landmarks
from .pose import extract_video_landmarks


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Analyze ski turns from a static-camera video")
    source = result.add_mutually_exclusive_group(required=True)
    source.add_argument("--demo", action="store_true", help="run with synthetic demo landmarks")
    source.add_argument("--video", help="path to MP4/MOV ski video")
    source.add_argument("--landmarks", help="JSON landmark sequence (useful for mobile clients)")
    source.add_argument("--dataset", help="directory of clip folders for batch evaluation")
    result.add_argument("--model", help="path to pose_landmarker.task (required with --video)")
    result.add_argument("--level", choices=["beginner", "intermediate", "advanced", "expert"], default="intermediate")
    result.add_argument("--terrain", choices=["groomer", "moguls", "powder", "steeps"], default="groomer")
    result.add_argument("--exercise", choices=["parallel turns", "carving", "short radius", "balance"], default="parallel turns")
    result.add_argument("--overlay-output", help="write a review video with pose landmarks (requires --video)")
    result.add_argument("--labels", help="instructor labels JSON to evaluate predicted turns")
    result.add_argument("--sensors", help="timestamped sensor JSON to compare with video turns")
    return result


def main() -> None:
    args = parser().parse_args()
    if args.dataset:
        if args.overlay_output or args.labels:
            parser().error("--dataset cannot be combined with per-run --labels or --overlay-output")
        if not args.model:
            # A dataset may contain landmarks.json fixtures and need no model.
            model = None
        else:
            model = args.model
        print(json.dumps(evaluate_dataset(args.dataset, model).to_dict(), indent=2))
        return
    if args.video and not args.model:
        parser().error("--model is required with --video")
    if args.demo:
        frames = demo_frames()
    elif args.landmarks:
        frames = load_frames(args.landmarks)
    else:
        frames = extract_video_landmarks(args.video, args.model)
    sensor_samples = load_sensor_samples(args.sensors) if args.sensors else None
    report = analyze_landmarks(frames, level=args.level, terrain=args.terrain, exercise=args.exercise, sensor_samples=sensor_samples)
    result = report.to_dict()
    if args.overlay_output:
        if not args.video:
            parser().error("--overlay-output requires --video")
        render_pose_overlay(args.video, frames, Path(args.overlay_output))
        result["overlay_output"] = args.overlay_output
    if args.labels:
        with Path(args.labels).open(encoding="utf-8") as handle:
            result["evaluation"] = evaluate_report(report, json.load(handle)).to_dict()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
