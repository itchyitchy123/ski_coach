"""Environment-backed settings for the HTTP service."""
from __future__ import annotations

import os
from dataclasses import dataclass


def _positive_int(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
    if value < 1:
        raise RuntimeError(f"{name} must be positive")
    return value


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    max_request_bytes: int
    requests_per_minute: int
    version: str


def load_settings() -> Settings:
    return Settings(
        api_key=os.getenv("SKI_COACH_API_KEY") or None,
        max_request_bytes=_positive_int("SKI_COACH_MAX_REQUEST_BYTES", 10 * 1024 * 1024),
        requests_per_minute=_positive_int("SKI_COACH_REQUESTS_PER_MINUTE", 30),
        version=os.getenv("SKI_COACH_VERSION", "0.1.0"),
    )
