# 🛡️ OpenClaw Guardrails

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Eco-OpenClaw-blueviolet?style=for-the-badge" alt="Eco-OpenClaw">
  <img src="https://img.shields.io/badge/Security-Enterprise_Grade-red?style=for-the-badge" alt="Enterprise">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Version-1.1.0-blue?style=for-the-badge" alt="Version">
</p>

---

**OpenClaw Guardrails** is a **full-stack security protection and self-healing framework** designed for AI Agents. Acting as the "Immune System" for the OpenClaw ecosystem, it ensures your AI assistants operate within safe boundaries through real-time semantic interception, configuration enforcement, and deep supply-chain scanning.

---

## 🚀 Quick Start: AI-Native Installation

If you are using **OpenClaw**, leverage its intelligence to deploy a full enterprise-grade defense system. Just say to your Agent:

> **"Help me install `lttcnly/openclaw-guardrails`. Once installed, initialize the security baseline, set up a daily automated audit at 03:17, and show me the first risk-score report."**

---

## 🏗️ System Architecture: Three-Pillar Defense (Vertical Flow)

本项目采用垂直分层架构，从入口到持久化层提供全方位保护：

```mermaid
graph TD
    subgraph L1 [Layer 1: Active Defense - Shield Mode]
        A[Agent Action Start] --> B{Intent Analysis}
        B -- Risk Identified --> C[Block & Request Human Review]
        B -- Safe Confirmed --> D[Execute Allowed]
    end

    D --> E

    subgraph L2 [Layer 2: Self-Healing - Enforce Mode]
        E[Config Monitoring] --> F{Baseline Check}
        F -- Unauthorized Drift --> G[Auto-Revert & Snapshot Backup]
        F -- Baseline Compliant --> H[Keep Running]
    end

    H --> I

    subgraph L3 [Layer 3: Deep Audit - Intelligence]
        I[SBOM Asset Inventory] --> J[Global Vuln Intel Correlation]
        J --> K[Dynamic Risk Score Report]
    end

    style L1 fill:#f9f,stroke:#333,stroke-width:2px
    style L2 fill:#bbf,stroke:#333,stroke-width:2px
    style L3 fill:#bfb,stroke:#333,stroke-width:2px
```

---

## 🔥 Enterprise Features

### 💎 1. Financial-Grade Shield
The only framework capable of understanding Agent intent at a semantic level:
-   **Semantic Recognition**: Identifies hidden intents like `transfer`, `pay`, or `withdraw` in natural language.
-   **Circuit Breaker**: Instantly cuts tool execution flows when risk is detected and requests admin approval.

### 🩹 2. Golden Baseline Enforcement
Eliminates security gaps caused by "permission drift":
-   **Strict Guarding**: Enforces core settings like `authMode: token` and `systemRunApproval: always`.
-   **Instant Reversion**: Auto-restores configurations within milliseconds of detecting a violation.

### 🕵️ 3. PII & Credential Sanitizer
Ensures your API Keys don't become "public secrets":
-   **Full-Spectrum Probe**: Scans `.env`, `.log`, and `.json` for keys, emails, IPs, and tokens.
-   **Auto-Redaction**: Reports automatically replace sensitive data with `[REDACTED]` tokens.

---

## 📋 Compliance & Governance

Guardrails helps organizations meet global cybersecurity standards:
-   ✅ **MLPS 2.0 (China)**: Identity, Access Control, Security Audit, Data Integrity.
-   ✅ **CIS Benchmarks**: OS and service hardening checks.
-   ✅ **GDPR**: Automatic privacy data identification and redaction.

---

## 💡 Call for Contributions & Better Algorithms (Join Us!)

**We believe that security is an endless game of wits.**

We warmly welcome security experts, algorithm engineers, and community developers to provide better ways to harden this "Immune System". We are particularly focused on:
1.  **More Accurate Intent Recognition Algorithms**: How to more effectively identify complex prompt injections or bypass attacks?
2.  **More Efficient Self-Healing Mechanisms**: For large-scale distributed nodes, how to elegantly synchronize security policies?
3.  **Zero-Trust Audit Models**: For dynamically loaded third-party tools, are there deeper sandbox audit solutions?

If you have any ideas, feel free to submit an **Issue** or open a **Pull Request**! Every algorithm optimization you contribute will make the AI world safer.

---

## 🛠️ Performance Benchmarks

| Metric | Result | Description |
| :--- | :--- | :--- |
| **Full Audit Duration** | < 15s | Powered by Python multi-processing engine. |
| **Self-Healing Latency** | < 100ms | Detection-to-reversion speed for critical drifts. |
| **Scanning Depth** | 5 Levels | Deeply identifies nested npm/pip shadow dependencies. |

---

## 🤝 Community & Roadmap
- [x] v1.1 Parallel Engine & Configuration Enforcement
- [x] Financial-grade Semantic Interception & PII Redaction
- [ ] **Federated Protection**: Federated security audits across multiple OpenClaw nodes.
- [ ] **Behavioral Profiling**: ML-based recognition of anomalous operation sequences.

---

**🛡️ Bulletproof your AI Agents. Guardrails is your first and last line of defense.**
