# Ski Coach

A Python-first prototype that extracts body landmarks from ski video, detects alternating turns, compares left and right movement, and generates confidence-aware coaching cues.

## What works now

- MediaPipe pose extraction from an uploaded or local video
- knee flex, torso lean, shoulder/hip rotation, stance, and balance measurements
- turn segmentation for steady downhill/front-view footage
- turn, rhythm, symmetry, balance, and upper-body scores
- skill-level context and explicit low-confidence/safety warnings
- a Streamlit UI, JSON CLI, synthetic demo, imported research fixtures, and unit tests
- structured next-run training plans with drills and measurable success signals

Scores are heuristic coaching signals, not objective technique grades. Terrain and exercise are captured now for the product workflow; only skill level changes thresholds in this first version. Instructor-labelled calibration is the next major milestone.

## Quick start (demo—no video model needed)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[ui,dev]'
streamlit run app.py
```

Choose **Demo**, then **Analyze run**. Or use the JSON CLI:

```bash
ski-coach --demo
pytest
```

## API boundary

The same engine is available as a small HTTP service for a future phone app:

```bash
pip install -e '.[api]'
uvicorn ski_coach.api:app --reload
curl http://localhost:8000/health
```

Mobile clients can POST normalized pose frames to `/v1/analyze/landmarks`. The payload format is intentionally simple and versionable:

```json
{
  "context": {"level": "intermediate", "terrain": "groomer", "exercise": "parallel turns"},
  "frames": [{"timestamp": 0.0, "landmarks": {"left_hip": {"x": 0.4, "y": 0.5, "visibility": 0.9}}}]
}
```

For deployments, use the versioned `/v1/analyze/landmarks` and `/v1/demo` endpoints. Set `SKI_COACH_API_KEY` before exposing the service beyond a trusted local network; clients send it in the `X-API-Key` header. The service also applies configurable request-size and per-client rate limits. See `.env.example` and the included `Dockerfile`.

The in-process rate limiter is suitable for a single worker only. A multi-worker or multi-instance deployment should move rate limiting and job state to shared infrastructure and place the API behind TLS, an authenticated gateway, and a queue-backed worker service. Video analysis remains synchronous in this MVP and should be moved to background jobs before accepting long-running or high-volume workloads.

## Analyze a real video

1. Download Google's [Pose Landmarker Lite model](https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task) into `models/`. The model is deliberately not committed because it is a separate binary artifact.

   Or run `python3 scripts/download_pose_model.py`.
2. Record 6–10 linked turns with the full skier visible, a steady camera, and a downhill/front view.
3. In the UI choose **Upload video**, or run:

```bash
ski-coach --video run.mp4 --model models/pose_landmarker_lite.task \
  --level intermediate --terrain groomer --exercise "parallel turns"
```

For integration testing without a video, analyze the checked-in fixture:

```bash
ski-coach --landmarks examples/landmarks.json
```

Google's [current Python Pose Landmarker API](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker/python) requires monotonically increasing timestamps in video mode; the extractor samples frames while retaining their original video timestamps.

## Architecture

```text
video -> pose.py -> metrics.py -> turns.py -> scoring.py -> feedback.py
                                      |                         |
                                      +------ pipeline.py ------+
```

The pose layer is replaceable. Scoring consumes plain landmark dataclasses, so rules and future instructor-trained models can be tested without MediaPipe or video files.

## Wearable sensor input

The engine accepts device-neutral timestamped sensor samples (`acceleration`, `rotation_rate`, optional GPS speed, altitude, and heart rate). Pass them to the CLI with `--sensors examples/sensors.json`; the report will include `sensor_fusion` agreement and boundary error. This is offline comparison only for now—native Apple Watch/Wear OS capture comes after the video pipeline is validated.

GPS session summaries are available with `--gps examples/gps.json`. The tracker reports distance, vertical descent, top/average run speed, stopped/lift/run time, and classified segments. This is the foundation for Slopes-style day summaries; map tiles, resort metadata, and background mobile recording come later.

## Known MVP limitations

- One skier and a static, downhill/front-view camera only
- 2D projection can confuse true joint motion with camera angle
- turns are inferred from lateral hip movement relative to the feet
- sensor and GPS import is offline only; live device capture is not implemented
- no instructor-labelled calibration yet
- video is processed locally and is not retained by the app
- data-quality is a visibility/pose-coverage signal, not a measure of skiing ability

Every report includes a quality breakdown for pose coverage, full-body framing, and single-subject confidence. These checks are separate from technique scores so poor footage cannot masquerade as poor skiing.

## Instructor review loop

Copy `examples/labels.json` for each clip and record turn directions/timing plus an optional instructor score. Evaluate a run with `--labels labels.json`; add `--overlay-output reviewed.mp4` to export a video with the detected pose landmarks for review. This is the path from heuristics to instructor-calibrated scoring.

See [datasets/README.md](datasets/README.md) for the recommended validation-study layout and privacy rules. Uploaded-video review in the Streamlit app now includes the same pose overlay.

## Repository guides

- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Production deployment notes](docs/production.md)
- data-quality is a visibility/pose-coverage signal, not a measure of skiing ability
