# Security policy

## Supported versions

Only the latest version on the `main` branch is currently supported.

## Reporting a vulnerability

Do not open a public issue for a security vulnerability. Contact the repository owner privately through the GitHub security advisory workflow or the private contact method configured for this repository. Include:

- a description and impact;
- reproducible steps or a minimal proof of concept;
- affected versions or commit IDs; and
- any suggested mitigation.

Please do not include real user videos, GPS tracks, biometric data, API keys, or other personal information in a report.

## Deployment requirements

Before exposing the API to an untrusted network, configure `SKI_COACH_API_KEY`, terminate TLS at a trusted gateway, and place the service behind shared rate limiting and resource quotas. The built-in rate limiter is process-local and is not sufficient for a multi-instance deployment.
