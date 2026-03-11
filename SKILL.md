---
name: openclaw-guardrails
description: Cross-platform, read-only security audit + guardrails kit for OpenClaw deployments (prompt-injection, mis-ops, skill supply-chain, exposure posture). Use when a user asks to audit/harden OpenClaw, assess skills risk, or reduce prompt-injection/destructive action risk.
---

# OpenClaw Guardrails (Skill)

This repository doubles as an OpenClaw skill folder.

## What it does (default: read-only)

- Runs OpenClaw + host posture checks and saves reports.
- Scans installed skills for risky patterns (static analysis).
- Extracts a redacted OpenClaw config summary.

## How to run

From the repo root:

```bash
./scripts/audit.sh            # macOS-friendly (bash)
python3 scripts/audit.py      # cross-platform audit (preferred)
python3 scripts/skills_scan.py
python3 scripts/config_extract.py
```

## One-liner install (recommended)

Clone into `~/.openclaw/skills/` so OpenClaw can discover it:

```bash
git clone <REPO_URL> ~/.openclaw/skills/openclaw-guardrails
```

Then run audits:

```bash
cd ~/.openclaw/skills/openclaw-guardrails
python3 scripts/audit.py
```

## Safety

- No destructive actions by default.
- Any hardening steps should be presented as a plan and require explicit approval.
