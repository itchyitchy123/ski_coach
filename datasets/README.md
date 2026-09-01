# Validation dataset

Use one directory per source clip. Keep videos outside Git (or in private object storage) and commit only metadata and anonymized labels:

```text
datasets/
  clip-001/
    metadata.json
    labels.json
```

`metadata.json` should record `skier_level`, `terrain`, `exercise`, `camera_view`, and consent status. `labels.json` follows [examples/labels.json](../examples/labels.json): an instructor records each complete turn's direction and start/end seconds, with an optional 0–100 reference score.

Recommended initial study: five clips from five skiers, each with one independent instructor label. Add a second instructor to at least two clips to measure agreement before changing scoring thresholds.

Once clips are present, run the whole study with:

```bash
ski-coach --dataset datasets/validation --model models/pose_landmarker_lite.task > validation-report.json
```

Each clip can contain `landmarks.json` instead of a video, which is useful for replaying exported pose data without rerunning pose extraction. The batch report includes completed/failed clips and aggregate direction, count, score, and turn-boundary timing errors.

Never commit identifiable video, names, or contact information. The repository's evaluation command compares a report to labels without uploading either file.
