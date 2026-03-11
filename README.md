# openclaw-guardrails

A pragmatic guardrails kit for OpenClaw deployments.

Goal: reduce real-world risk in 4 areas:
1) prompt injection (untrusted content)
2) destructive mis-ops (delete/overwrite)
3) skill supply-chain (suspicious skills)
4) platform vulnerabilities (exposure + auditing)

## Quickstart

macOS/Linux (bash):

```bash
./scripts/audit.sh
```

Cross-platform (recommended):

```bash
python3 scripts/audit.py
python3 scripts/skills_scan.py
python3 scripts/config_extract.py
```

## Install into OpenClaw (so it becomes a skill)

```bash
git clone <REPO_URL> ~/.openclaw/skills/openclaw-guardrails
cd ~/.openclaw/skills/openclaw-guardrails
python3 scripts/audit.py
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
