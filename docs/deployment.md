# Deployment

This project is intentionally **read-only by default**.

## Install (recommended)

Clone into OpenClaw's global skills directory so it is discoverable:

```bash
git clone <REPO_URL> ~/.openclaw/skills/openclaw-guardrails
cd ~/.openclaw/skills/openclaw-guardrails
python3 scripts/audit.py
```

## Windows

Use PowerShell:

```powershell
git clone <REPO_URL> "$env:USERPROFILE\.openclaw\skills\openclaw-guardrails"
cd "$env:USERPROFILE\.openclaw\skills\openclaw-guardrails"
python scripts\audit.py
```

## Optional: schedule daily audits (cross-platform)

This uses the OpenClaw Gateway scheduler (`openclaw cron`). Default cadence: once per day.

Print a plan (no changes):

```bash
python3 scripts/install.py --plan
```

Apply the plan (changes gateway state; use intentionally):

```bash
python3 scripts/install.py --apply
```
