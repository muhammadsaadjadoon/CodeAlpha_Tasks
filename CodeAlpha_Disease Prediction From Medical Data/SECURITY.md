# Security

## Development Configuration

The repository contains environment examples only. Do not commit real secrets or production credentials.

Before deploying HeartTrack:

- replace the default signing secret with a strong unique secret
- enable secure-cookie behavior when serving over HTTPS
- configure the allowed frontend origin explicitly
- use a persistent, production-grade identity and account store if persistent accounts are required
- add deployment-level HTTPS, logging, monitoring, rate limiting, and secret management
- perform an appropriate privacy and security review before processing sensitive information

## Reporting a Security Issue

If this repository is used publicly, report security issues privately to the repository owner rather than opening a public issue containing exploit details or credentials.
