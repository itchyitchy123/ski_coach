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

## Imported research data

`datasets/ski2dpose/` contains the curated 11-split validation subset of the [EPFL Ski 2DPose Dataset](https://www.epfl.ch/labs/cvlab/data/ski-2dpose-dataset/). The repository stores only the normalized eight-body-joint fixtures and metadata needed by this project; it does not store the source videos. The importer retains source URLs and marks `license_review_required` because downstream commercial use must be reviewed against the dataset's terms and the underlying video rights.

Regenerate the import from the official EPFL labels and metadata with:

```bash
python3 scripts/import_ski2dpose.py
```

Use `--all` to import every annotated split locally. The imported validation fixtures are useful for pose-schema and pipeline smoke tests, but they are not instructor-quality labels and should not be used to claim coaching accuracy. The Nordic Skiing Dataset is cross-country rather than alpine and Skiing-6 access/licensing should be confirmed separately before adding either to a commercial training corpus.
