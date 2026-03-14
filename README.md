# 🛡️ OpenClaw Guardrails

[![OpenClaw](https://img.shields.io/badge/Eco-OpenClaw-blueviolet)](https://github.com/google/gemini-cli)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.1.0-blue)](SKILL.md)

**The "Immune System" for your AI Agents.**  
OpenClaw Guardrails provides silent, enterprise-grade security monitoring, risk scoring, and self-healing capabilities for OpenClaw deployments.

---

## 🚀 Quick Start (AI-Native Installation)

If you are using **OpenClaw**, you don't need to manually clone or configure. Just tell your agent:

> **"Help me install the GitHub open-source project `lttcnly/openclaw-guardrails` and configure it as required."**

Or use the specialized setup command:
```bash
# One-click installation and security baseline setup
openclaw skill install https://github.com/lttcnly/openclaw-guardrails --auto-setup
```

---

## ✨ Why Guardrails?

In an AI-driven world, your agents have high privileges. Guardrails ensures they stay within safe boundaries without slowing you down.

*   **⚡ Parallel Engine**: Blazing fast multi-process scanning (Audit + Supply Chain + Vuln).
*   **🧠 Dynamic Risk Scoring**: Real-time 0-100 score based on weighted security logic.
*   **🩹 Self-Healing**: Automatically detects and restores unsafe configurations (with timestamped backups).
*   **🔍 Zero-Trust Supply Chain**: Scans third-party Skill dependencies for malicious patterns.
*   **📋 Compliance Ready**: Out-of-the-box checks for **MLPS 2.0 (China Cybersecurity Level Protection)** and CIS Benchmarks.

---

## 📊 Capabilities at a Glance

| Layer | Feature | Benefit |
| :--- | :--- | :--- |
| **Identity** | Credential Leak Detection | Prevents API keys from being exposed in logs/chats. |
| **System** | Config Drift Monitoring | Alerts you if a Skill or User changes critical settings. |
| **Supply Chain** | Hash Pinning & Verify | Ensures your Skills haven't been tampered with. |
| **Network** | Port & Proxy Audit | Detects unauthorized external connections. |
| **Executive** | Risk Trend Dashboard | Generates a 10-day trend HTML report automatically. |

---

## 🛠️ Advanced Usage

### Enable Daily "Immune Scan"
Set it and forget it. Guardrails will run silently in the background and only alert you if a **CRITICAL** risk is found.

```bash
openclaw cron add --name guardrails:daily \
  --cron "17 3 * * *" \
  --session isolated \
  --message "exec python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py"
```

### View Interactive Dashboard
```bash
# Open the generated security report in your browser
open .openclaw/skills/openclaw-guardrails/reports/dashboard.html
```

---

## 🤝 Contributing

We welcome security researchers and OpenClaw enthusiasts! Feel free to:
1.  Submit new **Security Policies** in `guardrails.yaml`.
2.  Improve the **Risk Scoring** algorithm.
3.  Add **Auto-fix** scripts for common vulnerabilities.

---

**🛡️ Bulletproof your AI agents. Trust, but verify.**
