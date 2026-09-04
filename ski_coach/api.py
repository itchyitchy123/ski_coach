"""Small HTTP boundary for a future mobile client.

Install the API extra and run ``uvicorn ski_coach.api:app --reload``.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from typing import Any

from .demo import demo_frames
from .io import frames_from_dict, sensor_samples_from_dict, gps_points_from_dict
from .pipeline import analyze_landmarks
from .config import load_settings

try:
    from fastapi import FastAPI, HTTPException, Request
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover - exercised only without the api extra
    raise RuntimeError("Install the API with: pip install -e '.[api]'") from exc

logger = logging.getLogger("ski_coach.api")
settings = load_settings()


class AnalyzeRequest(BaseModel):
    frames: list[dict[str, Any]] = Field(default_factory=list, max_length=100_000)
    context: dict[str, Any] = Field(default_factory=dict)
    sensors: dict[str, Any] | None = None
    gps: dict[str, Any] | None = None


app = FastAPI(title="Ski Coach API", version=settings.version)

VALID_CONTEXT = {
    "level": {"beginner", "intermediate", "advanced", "expert"},
    "terrain": {"groomer", "moguls", "powder", "steeps"},
    "exercise": {"parallel turns", "carving", "short radius", "balance"},
}

_requests: dict[str, deque[float]] = defaultdict(deque)


@app.middleware("http")
async def request_guards(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > settings.max_request_bytes:
        raise HTTPException(status_code=413, detail="request body is too large")
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    recent = _requests[client]
    while recent and now - recent[0] >= 60:
        recent.popleft()
    if len(recent) >= settings.requests_per_minute:
        raise HTTPException(status_code=429, detail="rate limit exceeded")
    recent.append(now)
    if request.method in {"POST", "PUT", "PATCH"}:
        body = await request.body()
        if len(body) > settings.max_request_bytes:
            raise HTTPException(status_code=413, detail="request body is too large")
    return await call_next(request)


def _authorize(request: Request) -> None:
    if settings.api_key and request.headers.get("x-api-key") != settings.api_key:
        raise HTTPException(status_code=401, detail="invalid API key")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/analyze/landmarks")
def analyze(payload: AnalyzeRequest, request: Request) -> dict[str, Any]:
    _authorize(request)
    try:
        raw = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
        frames = frames_from_dict(raw)
        context = raw.get("context", {})
        if not isinstance(context, dict):
            raise ValueError("context must be an object")
        defaults = {"level": "intermediate", "terrain": "groomer", "exercise": "parallel turns"}
        for name, allowed in VALID_CONTEXT.items():
            if context.get(name, defaults[name]) not in allowed:
                raise ValueError(f"context.{name} must be one of: {', '.join(sorted(allowed))}")
        report = analyze_landmarks(
            frames,
            level=context.get("level", "intermediate"),
            terrain=context.get("terrain", "groomer"),
            exercise=context.get("exercise", "parallel turns"),
            sensor_samples=sensor_samples_from_dict(raw["sensors"]) if raw.get("sensors") else None,
            gps_points=gps_points_from_dict(raw["gps"]) if raw.get("gps") else None,
        )
        logger.info("analysis completed frames=%d turns=%d", len(frames), report.turns)
        return report.to_dict()
    except (TypeError, ValueError, KeyError, IndexError, OverflowError, AttributeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/analyze/landmarks", include_in_schema=False)
def analyze_legacy(payload: AnalyzeRequest, request: Request) -> dict[str, Any]:
    """Compatibility route for clients using the original MVP endpoint."""
    return analyze(payload, request)


@app.get("/v1/demo")
def demo(request: Request) -> dict[str, Any]:
    _authorize(request)
    return analyze_landmarks(demo_frames()).to_dict()


@app.get("/demo", include_in_schema=False)
def demo_legacy(request: Request) -> dict[str, Any]:
    return demo(request)
