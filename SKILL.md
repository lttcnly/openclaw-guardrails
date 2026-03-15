---
name: openclaw-guardrails
description: The "Immune System" for OpenClaw. High-performance parallel scanning, risk scoring (0-100), MLPS 2.0 compliance, and self-healing auto-fix.
version: 1.0.0
metadata:
  {
    "clawdbot":
      {
        "emoji": "🛡️",
        "requires": { "bins": ["openclaw", "python3"] },
        "os": ["linux", "darwin", "win32"],
      },
  }
---

# OpenClaw Guardrails 🛡️

**Enterprise-Grade Security Monitoring & Immune System for OpenClaw**

## ⚡ Quick Setup (New v1.1 Architecture)

### 1. Install & Secure
The new architecture uses a sandboxed virtual environment to ensure stability and anti-injection security.

```bash
# Clone and Run Secure Installer
git clone https://github.com/lttcnly/openclaw-guardrails.git
cd openclaw-guardrails
python3 scripts/install.py
```

### 2. Configure Daily "Immune Scan"
Update your OpenClaw cron to use the new parallel execution engine:

```bash
openclaw cron add --name guardrails:daily \
  --cron "17 3 * * *" \
  --session isolated \
  --light-context \
  --no-deliver \
  --message "Daily Guardrails: exec /Users/lttcn/.openclaw/skills/openclaw-guardrails/venv/bin/python3 /Users/lttcn/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py"
```

---

## 🚀 Key Capabilities

- ⚡ **Parallel Engine**: Blazing fast security audits using multi-process scanning.
- 🧠 **Dynamic Risk Scoring**: Real-time 0-100 score based on weighted `guardrails.yaml` logic.
- 📋 **Deep Compliance**: Out-of-the-box checks for **等保 2.0 (MLPS)** and CIS Benchmarks.
- 🩹 **Self-Healing**: Automatically restores unsafe configurations with timestamped backups.
- 🔍 **Zero-Trust Audit**: Scans Skill supply-chains and identifies malicious dependencies.

---

## 📊 Security Dashboard

Guardrails generates a dynamic HTML dashboard at:
`~/.openclaw/skills/openclaw-guardrails/reports/dashboard.html`

View your **10-day risk trends** and detailed breakdown of security deductions.

---

## 📖 Documentation

- **English**: [README.md](https://github.com/lttcnly/openclaw-guardrails/blob/main/README.md)
- **中文**: [README.zh-CN.md](https://github.com/lttcnly/openclaw-guardrails/blob/main/README.zh-CN.md)

---
**🛡️ Bulletproof your AI agents with OpenClaw Guardrails.**
