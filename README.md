# 🛡️ OpenClaw Guardrails

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a>
</p>

[![OpenClaw](https://img.shields.io/badge/Eco-OpenClaw-blueviolet)](https://github.com/google/gemini-cli)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.1.0-blue)](SKILL.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/lttcnly/openclaw-guardrails/pulls)

**The ultimate "Immune System" for your AI Agents.**  
OpenClaw Guardrails is a comprehensive, enterprise-grade security orchestration suite specifically designed for OpenClaw. It transforms silent security audits into an active defense shield.

---

## 🚀 One-Click Intelligence (AI-Native Installation)

If you are already running **OpenClaw**, you can leverage its intelligence to set up this entire defense system in seconds. Just say:

> **"Help me install the GitHub project `lttcnly/openclaw-guardrails`. Once installed, initialize the security baseline, set up the daily automated scan, and show me the first security report."**

*This instruction triggers the agent to: clone, run `install.py`, configure cron, and perform the initial audit.*

---

## 💎 Why Every OpenClaw User Needs Guardrails

1.  **Trust, But Verify**: AI agents have powerful tools (shell, file access). Guardrails ensures no Skill or prompt injection can escalate privileges unnoticed.
2.  **Compliance Without Effort**: Meeting security standards like **MLPS 2.0** or **CIS** is usually painful. Guardrails automates 90% of the checks.
3.  **Zero-Noise Monitoring**: Unlike traditional logs, Guardrails uses **Alert Deduplication**. You only hear from us if something actually changed or broke.
4.  **Complete Asset Visibility**: Do you know exactly which third-party packages your 20+ Skills are using? Guardrails' **SBOM engine** does.

---

## 🔥 Deep Dive: Core Capabilities

### 🛡️ Layer 1: Active Defense & Self-Healing
*   **Automated Remediation (`auto_fix.py`)**: Detects unsafe `groupPolicy="open"` or unauthorized shell exposures and restores them with timestamped backups.
*   **Integrity Protection (`hash_pin.py/verify.py`)**: Generates a cryptographically signed baseline of your Skills. If a Skill's code is tampered with (e.g., via a supply-chain attack), it triggers an immediate lockdown.

### 🔍 Layer 2: Deep Inspection Engine
*   **System Hardening Audit (`audit.py`)**: Scans for OS-level listeners, firewall misconfigurations, and non-standard proxies used by agents.
*   **Zero-Trust Skill Scan (`skills_scan.py`)**: Performs static analysis on every installed Skill to detect credential leaks, hardcoded keys, and suspicious API patterns.
*   **Dependency Vuln Scanner (`vuln_scan.py`)**: Automatically checks `package.json` and `requirements.txt` of all Skills against global vulnerability databases (NVD/CVE).

### 📋 Layer 3: Enterprise Compliance & Governance
*   **SBOM (Software Bill of Materials) (`sbom.py`)**: Generates a full inventory of all software components used by your AI setup, enabling rapid response to "Log4j-style" zero-day events.
*   **Config Drift Detection (`config_drift.py`)**: Tracks every change in `openclaw.json`. Know exactly *who* changed *what* and *when*.
*   **MLPS 2.0 Compliance (`compliance_check.py`)**: Tailored checks for regional cybersecurity standards, ensuring your AI deployment is "Audit-Ready."

### 📊 Layer 4: Intelligence & Visualization
*   **Risk Scoring Algorithm (`risk_score.py`)**: A weighted 0-100 score that translates complex security findings into a single, understandable metric.
*   **Interactive Dashboard (`html_dashboard.py`)**: Generates beautiful, responsive HTML reports with **10-day risk trends**, helping you visualize your security posture over time.
*   **Threat Intelligence Integration (`threat_intel.py`)**: Correlates local findings with global threat feeds to identify emerging attack patterns.

---

## 🛠️ Performance & Engineering Highlights
*   **Parallel Execution Engine**: All scans run in parallel using Python's multi-processing, completing a full audit in seconds, not minutes.
*   **Incremental Scanning**: Only scans what's changed since the last run to minimize CPU/IO impact.
*   **Redacted Artifacts**: All reports automatically redact sensitive information (PII/Tokens) before saving to `reports/`.
*   **Automated Lifecycle**: `cleanup_reports.py` ensures your disk space is never overwhelmed by old audit artifacts.

---

## 📖 Roadmap
- [x] Parallel Scanning Engine (v1.1)
- [x] Risk Scoring & HTML Dashboard
- [x] Auto-fix Remediation
- [ ] **Cloud Sync**: Sync security baselines across multiple OpenClaw nodes.
- [ ] **ML-based Anomaly Detection**: Detect suspicious prompt patterns using local models.
- [ ] **Slack/Discord/Telegram Alerting**: Native integrations for real-time risk alerts.

---

## 🤝 Community & Support

Join us in building the most secure AI environment on the planet.
- **Bug Reports**: Open an issue if you find a bypass.
- **Feature Requests**: Want a specific compliance check? Let us know.
- **Security Researchers**: We value your feedback.

**🛡️ Bulletproof your AI. Guardrails is your first and last line of defense.**
