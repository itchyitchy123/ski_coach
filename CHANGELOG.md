# Changelog

All notable changes to Ski Coach are documented here.

This project follows a lightweight Keep a Changelog format. The current release is an early MVP and does not claim validated coaching accuracy.

## [Unreleased]

### Added

- Structured next-run drill recommendations with focus, priority, and success signals.
- Session-level progress history in the Streamlit UI.
- EPFL Ski 2DPose validation fixtures and a repeatable official-data importer.
- Versioned API routes, request schemas, API-key support, request limits, and rate limiting.
- Docker deployment configuration and environment-variable settings.

### Changed

- JSON boundaries now reject non-finite values, unordered timestamps, invalid GPS coordinates, and oversized inputs.
- Video uploads are limited to 200 MB and temporary overlay artifacts are cleaned up.
- Coaching notes are more specific and action-oriented.

### Known limitations

- Analysis is synchronous and intended for single-worker or local use.
- Coaching rules are heuristic and have not yet been calibrated against a broad instructor-labeled alpine dataset.
- Live GPS, IMU, and heart-rate ingestion is not part of the current product workflow.

## [0.1.0] - 2026-09-01

Initial MVP release with video pose extraction, turn segmentation, scoring, CLI, API boundary, Streamlit UI, sensor/GPS summaries, and batch evaluation.
