---
name: openclaw-guardrails
description: Silent security monitoring for OpenClaw deployments. Daily scans (official audit + supply-chain + vuln), risk scoring (0-100), alert deduplication, and one-click fixes. Use when you need continuous security posture monitoring without noise.
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

# OpenClaw Guardrails

**Silent security monitoring** for OpenClaw deployments. Runs daily scans, calculates risk score (0-100), and alerts only when critical risks are detected.

## When to Use

- You want **continuous security monitoring** without daily noise
- You need **risk scoring** to track security posture over time
- You want **alert deduplication** (only new critical findings trigger alerts)
- You need **supply-chain integrity** checks (hash pinning + verify)

## Installation

```bash
# Clone to OpenClaw skills directory
git clone https://github.com/lttcnly/openclaw-guardrails.git ~/.openclaw/skills/openclaw-guardrails

# Run once to verify
cd ~/.openclaw/skills/openclaw-guardrails
python3 scripts/run_daily.py
```

## Enable Daily Monitoring

Creates a cron job that runs at 03:17 daily:

```bash
openclaw cron add --name guardrails:daily --cron "17 3 * * *" --session isolated --light-context --no-deliver \
  --message "Daily guardrails: exec python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py (fallback: python). Save artifacts under reports/. Alert on critical."
```

## What It Scans

| Layer | Tool | Output |
|-------|------|--------|
| Official Audit | `openclaw security audit --deep` | `reports/openclaw-security-audit-*.json` |
| Skills Supply-Chain | Custom static scan | `reports/skills-scan-*.json/.md` |
| Config Snapshot | Redacted extract | `reports/openclaw-config-redacted-*.json` |
| Cross-Platform Audit | Custom checks | `reports/audit-*.txt/.json` |
| SBOM | Asset inventory | `reports/sbom-*.json` |
| Dependency Vulns | `npm audit` / `pip-audit` | `reports/vuln-scan-*.json` |
| Hash Pinning | SHA256 baseline | `reports/skill-hashes-baseline.json` |
| **Risk Score** | Weighted calculation | `reports/risk-score-*.json` |
| **Summary** | Human-readable | `reports/summary-*.md` |

## Alert Behavior

| Scenario | Behavior |
|----------|----------|
| Normal day | Silent (no messages) |
| Critical detected | Push alert to main session |
| Same critical recurring | Deduplicated (no repeat alert) |
| New critical | Alert with "新增" count |

## Risk Score Calculation

| Factor | Deduction | Max |
|--------|-----------|-----|
| Each critical | -20 pts | -60 |
| Each warn | -5 pts | -20 |
| Each HIGH skill flag | -10 pts | -20 |
| Each vuln (high/critical) | -10 pts | -20 |

**Risk Levels:**
- 🟢 80-100: LOW
- 🟡 60-79: MEDIUM
- 🟠 40-59: HIGH
- 🔴 0-39: CRITICAL

## One-Click Fixes (Coming Soon)

Future version will include remediation commands for common findings:
- `groupPolicy="open"` → `allowlist`
- Plugin quarantine
- Tool exposure reduction

## Files Structure

```
openclaw-guardrails/
├── SKILL.md
├── README.md
├── scripts/
│   ├── run_daily.py          # Main entry point
│   ├── skills_scan.py        # Supply-chain scan
│   ├── audit.py              # Cross-platform audit
│   ├── sbom.py               # Asset inventory
│   ├── vuln_scan.py          # Dependency vulns
│   ├── hash_pin.py           # Baseline generation
│   ├── hash_verify.py        # Baseline verification
│   ├── risk_score.py         # Risk calculation
│   └── enforce.py            # Auto-remediation (optional)
└── reports/                  # Artifacts (gitignored)
```

## Notes

- **Read-only by default**: Does not modify system configuration
- **Alert deduplication**: Only new critical findings trigger alerts
- **Cross-platform**: Works on macOS, Linux, Windows
- **Silent operation**: No daily spam, only alerts on real risks
