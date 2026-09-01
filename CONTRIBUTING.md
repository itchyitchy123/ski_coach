# Contributing

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[ui,api,dev]'
pytest
```

Keep analysis rules deterministic and unit-testable. New technique cues should include a confidence condition and should not imply safety certification. Do not commit model binaries, user videos, or generated pose data.

## Pull requests

Describe the camera framing and skier skill level used to validate changes. Include tests for geometry, segmentation, or scoring changes. Keep API payload changes backwards compatible where possible.

