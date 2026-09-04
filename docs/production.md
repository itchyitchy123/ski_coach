# Production deployment notes

## Current supported shape

The included container runs the HTTP API:

```bash
docker build -t ski-coach .
docker run --rm -p 8000:8000 \
  -e SKI_COACH_API_KEY='use-a-secret-manager-value' \
  ski-coach
```

Health check: `GET /health`.

Analysis endpoint: `POST /v1/analyze/landmarks` with `X-API-Key` when authentication is configured. The legacy `/analyze/landmarks` and `/demo` routes remain available for MVP clients but should not be used for new integrations.

## Before public launch

- Put TLS, authentication policy, and a shared rate limiter in front of the service.
- Move video analysis to a queue-backed worker so HTTP requests are not held open during inference.
- Add shared job/result storage, retries, cancellation, and artifact expiration.
- Set CPU, memory, duration, and concurrency limits for video processing.
- Add centralized logs, error reporting, latency metrics, and alerts.
- Define deletion, retention, consent, and export controls for video, landmarks, GPS, and heart-rate data.
- Run dependency and container vulnerability scans on every release.
