# openclaw-guardrails

A pragmatic guardrails kit for OpenClaw deployments.

Goal: reduce real-world risk in 4 areas:
1) prompt injection (untrusted content)
2) destructive mis-ops (delete/overwrite)
3) skill supply-chain (suspicious skills)
4) platform vulnerabilities (exposure + auditing)

## Quickstart

Run a read-only baseline audit (recommended first):

```bash
./scripts/audit.sh
```

## What this repo contains

- `scripts/` read-only audits + optional hardening helpers
- `policies/` guardrail policies / checklists
- `docs/` threat model + rationale
- `reports/` generated audit reports (gitignored)

## Safety

- Default mode is **read-only**.
- Any state-changing operation must be explicit and reversible.

## License

MIT
