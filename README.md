# Ski Coach MVP

A Python-first prototype that extracts body landmarks from ski video, detects alternating turns, compares left and right movement, and generates confidence-aware coaching cues.

## What works now

- MediaPipe pose extraction from an uploaded or local video
- knee flex, torso lean, shoulder/hip rotation, stance, and balance measurements
- turn segmentation for steady downhill/front-view footage
- turn, rhythm, symmetry, balance, and upper-body scores
- skill-level context and explicit low-confidence/safety warnings
- a Streamlit UI, JSON CLI, synthetic demo, and unit tests

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
curl http://localhost:8000/demo
```

Mobile clients can POST normalized pose frames to `/analyze/landmarks`. The payload format is intentionally simple and versionable:

```json
{
  "context": {"level": "intermediate", "terrain": "groomer", "exercise": "parallel turns"},
  "frames": [{"timestamp": 0.0, "landmarks": {"left_hip": {"x": 0.4, "y": 0.5, "visibility": 0.9}}}]
}
```

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

## Known MVP limitations

- One skier and a static, downhill/front-view camera only
- 2D projection can confuse true joint motion with camera angle
- turns are inferred from lateral hip movement relative to the feet
- no IMU/GPS import yet
- no instructor-labelled calibration yet
- video is processed locally and is not retained by the app
- data-quality is a visibility/pose-coverage signal, not a measure of skiing ability
