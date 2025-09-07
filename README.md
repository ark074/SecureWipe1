# SecureWipe — Production-ready Platform (Linux + Windows agents, Cloud Verifier)

This repository provides a production-oriented secure data wiping platform.
It includes:
- `backend/` — Rust agent service (device enumeration, wipe orchestration, certificate JSON generation)
- `tools/` — Python utilities: RSA signing, PDF generation, email sending, verification
- `verifier/` — Flask-based cloud verifier (validates signed certificates, stores receipts)
- `agent/linux/` and `agent/windows/` — install scripts & service stubs for on-prem agents
- `deploy/` — Render deployment config and hardening checklist
- `Dockerfiles` and `render.yaml` for cloud deployment

IMPORTANT SAFETY NOTE: This software performs destructive operations. **DO NOT** point it at production disks until you've:
1. Completed the Hardening Checklist in `deploy/HARDENING.md`.
2. Tested thoroughly using the provided loopback/VHDX scripts in `scripts/`.
3. Ensured signing keys are stored in a secure KMS or HSM for production.

This repo uses RSA (PKCS#1 v1.5 + SHA256) for signatures so the platform is interoperable with standard OpenSSL keys.
