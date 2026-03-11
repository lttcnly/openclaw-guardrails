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
python3 scripts/run_daily.py
```

## Enable daily silent monitoring (recommended)

Creates/updates a Gateway cron job (`guardrails:daily`) that runs once per day and writes artifacts under `reports/`.

**Alert behavior:**
- Normal days: silent (no messages)
- When critical risks detected: pushes an alert to the main session via `openclaw system event`

```bash
openclaw cron add --name guardrails:daily --cron "17 3 * * *" --session isolated --light-context --no-deliver \
  --message "Daily guardrails: exec python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py (fallback: python). Save artifacts under reports/. Alert on critical."
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
