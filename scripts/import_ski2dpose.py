#!/usr/bin/env python3
"""Import the official EPFL Ski 2DPose labels into this project's schema.

The importer downloads only the small annotation/metadata archives by default.
It does not fetch or redistribute the source videos.
"""
from __future__ import annotations

import argparse
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path

LABELS_URL = "https://datasets-cvlab.epfl.ch/2019-ski-2d-pose/ski2dpose_labels.json.zip"
INFO_URL = "https://datasets-cvlab.epfl.ch/2019-ski-2d-pose/ski2dpose_info.json"
JOINTS = (
    "head", "neck", "shoulder_right", "elbow_right", "hand_right", "pole_basket_right",
    "shoulder_left", "elbow_left", "hand_left", "pole_basket_left", "hip_right", "knee_right",
    "ankle_right", "hip_left", "knee_left", "ankle_left", "ski_tip_right", "toes_right",
    "heel_right", "ski_tail_right", "ski_tip_left", "toes_left", "heel_left", "ski_tail_left",
)
REQUIRED = {
    "shoulder_left": 6, "shoulder_right": 2, "hip_left": 13, "hip_right": 10,
    "knee_left": 14, "knee_right": 11, "ankle_left": 15, "ankle_right": 12,
}
VALIDATION = {"5UHRvqx1iuQ": {"0", "1"}, "oKQFABiOTw8": {"0", "1", "2"},
              "qxfgw1Kd98A": {"0", "1"}, "uLW74013Wp0": {"0", "1"}, "zW1bF2PsB0M": {"0", "1"}}


def fetch(source: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(source) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def load_sources(cache: Path) -> tuple[dict, dict]:
    labels_zip = cache / "ski2dpose_labels.json.zip"
    info_path = cache / "ski2dpose_info.json"
    if not labels_zip.exists():
        fetch(LABELS_URL, labels_zip)
    if not info_path.exists():
        fetch(INFO_URL, info_path)
    with zipfile.ZipFile(labels_zip) as archive:
        labels = json.loads(archive.read("ski2dpose_labels.json"))
    return labels, json.loads(info_path.read_text(encoding="utf-8"))


def import_dataset(output: Path, cache: Path, validation_only: bool) -> int:
    labels, info = load_sources(cache)
    output.mkdir(parents=True, exist_ok=True)
    imported = 0
    for video_id, splits in labels.items():
        selected = VALIDATION.get(video_id, set()) if validation_only else set(splits)
        for split_id, images in splits.items():
            if selected is not None and split_id not in selected:
                continue
            frames = []
            for image_id, value in sorted(images.items(), key=lambda pair: pair[1]["frame_idx"]):
                annotation = value.get("annotation", [])
                if len(annotation) != len(JOINTS):
                    raise ValueError(f"{video_id}/{split_id}/{image_id} has an unexpected joint count")
                landmarks = {
                    name: {"x": float(annotation[index][0]), "y": float(annotation[index][1]),
                           "visibility": float(annotation[index][2])}
                    for name, index in REQUIRED.items()
                }
                frames.append({"timestamp": round(float(value["frame_idx"]) / 30, 3),
                               "landmarks": landmarks, "pose_count": 1})
            if not frames:
                continue
            directory = output / f"{video_id}-{split_id}"
            directory.mkdir(parents=True, exist_ok=True)
            metadata = info.get(video_id, {})
            video_info = metadata.get("video_info", {})
            split_info = metadata.get("splits_info", {}).get(split_id, {})
            (directory / "metadata.json").write_text(json.dumps({
                "source": "EPFL Ski 2DPose", "source_video_id": video_id,
                "source_url": video_info.get("url"), "license_review_required": True,
                "type": video_info.get("type"), "location": video_info.get("location"),
                "weather": video_info.get("weather"), "camera_view": split_info,
                "skier_level": "unknown", "terrain": "groomer",
                "exercise": "parallel turns",
            }, indent=2) + "\n", encoding="utf-8")
            (directory / "landmarks.json").write_text(json.dumps({"frames": frames}, indent=2) + "\n", encoding="utf-8")
            imported += 1
    return imported


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("datasets/ski2dpose"))
    parser.add_argument("--cache", type=Path, default=Path(".cache/ski2dpose"))
    parser.add_argument("--all", action="store_true", help="import all annotated splits, not only the validation set")
    args = parser.parse_args()
    print(f"Imported {import_dataset(args.output, args.cache, not args.all)} Ski 2DPose splits")


if __name__ == "__main__":
    main()
