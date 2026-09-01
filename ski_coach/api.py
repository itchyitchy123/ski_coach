"""Small HTTP boundary for a future mobile client.

Install the API extra and run ``uvicorn ski_coach.api:app --reload``.
"""

from __future__ import annotations

from typing import Any

from .demo import demo_frames
from .io import frames_from_dict, sensor_samples_from_dict
from .pipeline import analyze_landmarks

try:
    from fastapi import FastAPI, HTTPException
except ImportError as exc:  # pragma: no cover - exercised only without the api extra
    raise RuntimeError("Install the API with: pip install -e '.[api]'") from exc

app = FastAPI(title="Ski Coach API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze/landmarks")
def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        frames = frames_from_dict(payload)
        context = payload.get("context", {})
        report = analyze_landmarks(
            frames,
            level=context.get("level", "intermediate"),
            terrain=context.get("terrain", "groomer"),
            exercise=context.get("exercise", "parallel turns"),
            sensor_samples=sensor_samples_from_dict(payload.get("sensors", {})) if payload.get("sensors") else None,
        )
        return report.to_dict()
    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/demo")
def demo() -> dict[str, Any]:
    return analyze_landmarks(demo_frames()).to_dict()
