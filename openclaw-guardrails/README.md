# OpenClaw Guardrails 🛡️

**Enterprise-Grade Security Monitoring for OpenClaw** - Silent monitoring, auto-fix, compliance checks

[![GitHub stars](https://img.shields.io/github/stars/lttcnly/openclaw-guardrails)](https://github.com/lttcnly/openclaw-guardrails/stargazers)
[![License](https://img.shields.io/github/license/lttcnly/openclaw-guardrails)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-blue)](https://github.com/lttcnly/openclaw-guardrails)

**[🇨🇳 中文文档](README.zh-CN.md)**

---

## 🌟 Key Features

| Feature | Description |
|---------|-------------|
| 🤫 **Silent Monitoring** | No daily spam, alerts only on critical risks |
| 🤖 **Auto-Fix** | Automatically fix low-risk issues (config drift, dependency upgrades) |
| 📊 **Risk Scoring** | 0-100 score with red/yellow/green indicators |
| 🔍 **Threat Intelligence** | Integrated OSV + NVD + GitHub vulnerability databases |
| 📋 **Compliance Checks** | MLPS 2.0 / CIS Benchmarks automated checks |
| 🚀 **Performance** | Incremental scanning, only changed files |
| 🧹 **Auto Cleanup** | Automatic report retention management |
| 🌐 **Cross-Platform** | One-click install for macOS / Linux / Windows |

---

## 🚀 Quick Start

### One-Click Install (Recommended)

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/lttcnly/openclaw-guardrails/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -UseBasicParsing https://raw.githubusercontent.com/lttcnly/openclaw-guardrails/main/install.ps1 | Invoke-Expression
```

**Manual Install:**
```bash
# 1. Clone to OpenClaw skills directory
git clone https://github.com/lttcnly/openclaw-guardrails.git ~/.openclaw/skills/openclaw-guardrails

# 2. Run initial scan
cd ~/.openclaw/skills/openclaw-guardrails
python3 scripts/run_daily.py

# 3. Setup daily cron (optional)
openclaw cron add --name guardrails:daily \
  --cron "17 3 * * *" \
  --session isolated \
  --light-context \
  --no-deliver \
  --message "Daily guardrails: exec python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py"
```

---

## 📋 What's Included

### Daily Automated Tasks
| Task | Script | Description |
|------|--------|-------------|
| 🔍 Risk Scoring | `risk_score.py` | 0-100 score with fix suggestions |
| 📡 Threat Intel | `threat_intel.py` | OSV + NVD + GitHub sources |
| 📊 Config Drift | `config_drift.py` | Detect unsafe config changes |
| 🔧 Auto-Fix | `auto_fix.py` | Automatic remediation |
| 🎨 HTML Dashboard | `html_dashboard.py` | Interactive web dashboard |
| 🧹 Report Cleanup | `cleanup_reports.py` | Auto-delete old reports |
| 🔄 Incremental Scan | `incremental_scan.py` | Scan only changed files |

### Weekly Tasks (Sundays)
| Task | Script | Description |
|------|--------|-------------|
| 🎯 Skills Audit | `skills_audit.py` | Detect skill updates and new risks |
| 📋 Compliance | `compliance_check.py` | MLPS 2.0 / CIS checks |

### Monthly Tasks (1st of month)
| Task | Script | Description |
|------|--------|-------------|
| 📈 Trend Analysis | `trend_analysis.py` | Monthly risk trend report |

### On-Demand
| Task | Script | Description |
|------|--------|-------------|
| 🚫 Pre-Install Scan | `preinstall_scan.py` | Block dangerous skills before install |

---

## 📊 Risk Score Explained

| Score | Level | Color | Meaning |
|-------|-------|-------|---------|
| 80-100 | LOW | 🟢 | Secure |
| 60-79 | MEDIUM | 🟡 | Moderate risk |
| 40-59 | HIGH | 🟠 | High risk |
| 0-39 | CRITICAL | 🔴 | Critical, immediate action required |

**Deduction Rules:**
- Each critical finding: -20 pts (max -60)
- Each warning: -5 pts (max -20)
- Each HIGH skill flag: -10 pts (max -20)
- Each high/critical vuln: -10 pts (max -20)

---

## 🛠️ Usage Guide

### View Risk Score
```bash
cat ~/.openclaw/skills/openclaw-guardrails/reports/summary-*.md
```

### Open HTML Dashboard
```bash
# macOS
open ~/.openclaw/skills/openclaw-guardrails/reports/dashboard-*.html

# Linux
xdg-open ~/.openclaw/skills/openclaw-guardrails/reports/dashboard-*.html

# Windows
start $env:USERPROFILE\.openclaw\skills\openclaw-guardrails\reports\dashboard-*.html
```

### Manual Scan
```bash
python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py
```

### Pre-Install Skill Scan
```bash
# Scan a skill folder before installation
python3 ~/.openclaw/skills/openclaw-guardrails/scripts/preinstall_scan.py /path/to/skill-folder

# Exit codes:
# 0 = Safe to install
# 1 = Warning (review recommended)
# 2 = Blocked (critical risk detected)
```

### Auto-Fix (Dry Run)
```bash
# Default: simulate only (safe)
python3 ~/.openclaw/skills/openclaw-guardrails/scripts/auto_fix.py

# Actually execute fixes (will modify system)
python3 ~/.openclaw/skills/openclaw-guardrails/scripts/auto_fix.py --execute
```

### View Compliance Report
```bash
cat ~/.openclaw/skills/openclaw-guardrails/reports/compliance-*.md
```

---

## 📁 Report Files

All reports saved in `~/.openclaw/skills/openclaw-guardrails/reports/`

| File | Description | Retention |
|------|-------------|-----------|
| `summary-*.md` | Risk score summary | 7 days |
| `risk-score-*.json` | Risk score details | 7 days |
| `threat-intel-*.json` | Threat intelligence | 7 days |
| `config-drift-*.json` | Config drift report | 7 days |
| `auto-fix-*.json` | Auto-fix report | 7 days |
| `compliance-*.md` | Compliance report | 30 days |
| `skills-audit-*.md` | Skills audit report | 30 days |
| `trend-*.json` | Monthly trend data | 12 months |
| `dashboard-*.html` | HTML dashboard | Latest only |

---

## 🛡️ Security Boundaries

### Auto-Execute (No Confirmation)
- ✅ Dependency upgrades (`npm update`, `pip install --upgrade`)
- ✅ Restore known safe configs

### Requires Confirmation
- ⚠️ Uninstall skills
- ⚠️ Modify core configs (gateway bind, etc.)
- ⚠️ System-level software upgrades

### Never Auto-Execute
- ❌ Download/execute external scripts
- ❌ Modify firewall/network configs
- ❌ Install unverified patches

---

## 📈 Performance Impact

| Metric | Value |
|--------|-------|
| Daily scan time | 30-60 seconds |
| Incremental scan | 5-10 seconds |
| Memory usage | < 50MB |
| Disk usage | ~100MB (with reports) |
| CPU usage | < 5% (during scan) |

---

## 🐛 Troubleshooting

### Reports Not Generated
```bash
# Check Python version
python3 --version  # Requires 3.10+

# Run manually
python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py
```

### Alerts Not Pushed
```bash
# Check cron jobs
openclaw cron list | grep guardrails

# View cron history
openclaw cron runs --id <job-id>
```

### Abnormal Risk Score
```bash
# View detailed deductions
cat ~/.openclaw/skills/openclaw-guardrails/reports/risk-score-*.json | jq .breakdown
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- [OpenClaw](https://openclaw.ai) - Powerful AI agent framework
- [OSV.dev](https://osv.dev) - Google-maintained vulnerability database
- [NVD](https://nvd.nist.gov) - US National Vulnerability Database
- [GitHub Advisories](https://github.com/advisories) - GitHub Security Advisories

---

## 📞 Contact

- GitHub Issues: https://github.com/lttcnly/openclaw-guardrails/issues
- Email: lttcnly@gmail.com

---

**🛡️ Make OpenClaw Safer with Guardrails!**
