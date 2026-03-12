---
name: openclaw-guardrails
description: Enterprise-grade security monitoring for OpenClaw. Silent monitoring, risk scoring (0-100), auto-fix, threat intelligence, compliance checks. Cross-platform (macOS/Linux/Windows).
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

**Enterprise-Grade Security Monitoring for OpenClaw**

## Quick Install

### From ClawHub
```bash
clawhub install openclaw-guardrails
```

### From GitHub (Recommended)
```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/lttcnly/openclaw-guardrails/main/install.sh | bash

# Windows (PowerShell)
Invoke-WebRequest -UseBasicParsing https://raw.githubusercontent.com/lttcnly/openclaw-guardrails/main/install.ps1 | Invoke-Expression

# Manual
git clone https://github.com/lttcnly/openclaw-guardrails.git ~/.openclaw/skills/openclaw-guardrails
```

## Features

- 🤫 Silent monitoring (alerts only on critical risks)
- 🤖 Auto-fix for low-risk issues
- 📊 Risk scoring (0-100)
- 🔍 Threat intelligence (OSV + NVD + GitHub)
- 📋 Compliance checks (MLPS 2.0 / CIS)
- 🚀 Incremental scanning (performance optimized)
- 🌐 Cross-platform support

## Usage

After installation, the daily cron job runs automatically at 03:17.

**Manual scan:**
```bash
python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py
```

**View reports:**
```bash
cat ~/.openclaw/skills/openclaw-guardrails/reports/summary-*.md
open ~/.openclaw/skills/openclaw-guardrails/reports/dashboard-*.html
```

**Pre-install skill scan:**
```bash
python3 ~/.openclaw/skills/openclaw-guardrails/scripts/preinstall_scan.py /path/to/skill
```

## Documentation

- 📖 Full README: https://github.com/lttcnly/openclaw-guardrails
- 🇨🇳 中文文档：https://github.com/lttcnly/openclaw-guardrails/blob/master/README.zh-CN.md
- 📦 GitHub: https://github.com/lttcnly/openclaw-guardrails

## License

MIT License
