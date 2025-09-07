# Hardening & Compliance Checklist (Required before production)

- Move PRIVATE_KEY_CONTENT into a secure KMS (HashiCorp Vault / AWS KMS / Azure Key Vault) and do not store it in plain environment variables in production.
- Use mTLS between agents and verifier (create CA and issue client certs).
- Ensure agents run only on trusted on-prem hosts with restricted physical access.
- Require two-person approval for bulk/irreversible wipe operations where needed.
- Log all operations to an append-only remote store (S3 with versioning, or write-once storage).
- Regularly rotate signing keys and publish revocation/stale key policy.
- Obtain legal sign-off for procedures and retention of certificates.
- Test with loopback images (Linux) and VHDX (Windows) before any real wipes.
