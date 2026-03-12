#!/usr/bin/env python3
"""Daily guardrails job (read-only).

Runs:
- skills_scan.py
- config_extract.py
- audit.py

Designed to be used by schedulers (OpenClaw cron, systemd timer, launchd, schtasks).
Exit code is non-zero if any step fails.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BASELINE = ROOT / "reports" / "skill-hashes-baseline.json"

STEPS = [
    # Supplementary layers (we do NOT re-implement OpenClaw's official security audit)
    [sys.executable, str(ROOT / "scripts" / "skills_scan.py")],
    [sys.executable, str(ROOT / "scripts" / "config_extract.py")],
    [sys.executable, str(ROOT / "scripts" / "audit.py")],
    [sys.executable, str(ROOT / "scripts" / "sbom.py")],
    [sys.executable, str(ROOT / "scripts" / "vuln_scan.py")],
    [sys.executable, str(ROOT / "scripts" / "risk_score.py")],
    
    # Threat Intelligence (NEW)
    [sys.executable, str(ROOT / "scripts" / "threat_intel.py")],
    
    # Configuration Drift Detection (NEW)
    [sys.executable, str(ROOT / "scripts" / "config_drift.py")],
]


def main() -> int:
    rc_any = 0

    # Pin baseline if missing
    if not BASELINE.exists():
        print(f"[guardrails] baseline missing; pinning -> {BASELINE}")
        p = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'hash_pin.py'), '--out', str(BASELINE)])
        if p.returncode != 0:
            rc_any = p.returncode

    for cmd in STEPS:
        p = subprocess.run(cmd)
        if p.returncode != 0:
            rc_any = p.returncode

    # Weekly skills audit (only on Sundays)
    import time as _time
    if _time.strftime('%w') == '0':  # Sunday
        print("[guardrails] Running weekly skills audit...")
        p = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'skills_audit.py')])
        if p.returncode != 0:
            rc_any = p.returncode

    # Verify against baseline (supply-chain tampering detector)
    if BASELINE.exists():
        p = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'hash_verify.py'), '--baseline', str(BASELINE)])
        if p.returncode != 0:
            rc_any = p.returncode

    # Use official OpenClaw security audit (no wheel re-invention):
    # - persist JSON evidence
    # - if critical>0: push alert to main session (user-facing)
    try:
        audit = subprocess.run(
            ['openclaw', 'security', 'audit', '--deep', '--json'],
            capture_output=True,
            text=True,
            timeout=180,
        )
        mixed = (audit.stdout or '') + "\n" + (audit.stderr or '')
        j = mixed.find('{')
        if j >= 0:
            import json as _json
            decoder = _json.JSONDecoder()
            data, _end = decoder.raw_decode(mixed[j:])

            import time as _time
            rep = ROOT / 'reports'
            rep.mkdir(exist_ok=True)
            ts = _time.strftime('%Y%m%d-%H%M%S')
            audit_path = rep / f'openclaw-security-audit-{ts}.json'
            audit_path.write_text(
                _json.dumps(data, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )

            crit = int((data.get('summary') or {}).get('critical') or 0)
            if crit > 0:
                # Dedup: only alert if new critical findings (compare to last alert)
                last_alert_path = rep / "last-alert-critical.json"
                last_criticals = set()
                if last_alert_path.exists():
                    try:
                        last_data = json.loads(last_alert_path.read_text())
                        last_criticals = {f"{f['checkId']}:{f['title']}" for f in last_data.get('findings', [])}
                    except Exception:
                        pass

                current_criticals = [f for f in data.get('findings', []) if f.get('severity') == 'critical']
                current_set = {f"{f['checkId']}:{f['title']}" for f in current_criticals}

                # Only alert if there are NEW criticals
                new_criticals = current_set - last_criticals
                if new_criticals or not last_alert_path.exists():
                    findings = [f['title'] for f in current_criticals[:5]]
                    alert_lines = [
                        "🚨 **Guardrails 发现高危风险**",
                        f"- critical: {crit}",
                        f"- 新增：{len(new_criticals) if new_criticals else crit}",
                    ]
                    for f in findings:
                        alert_lines.append(f"  - {f}")
                    alert_lines.append(f"- 完整报告：{audit_path}")
                    alert_text = "\n".join(alert_lines)
                    try:
                        subprocess.run(['openclaw', 'system', 'event', '--mode', 'now', '--text', alert_text], timeout=30)
                        # Save current criticals for next dedup
                        last_alert_path.write_text(json.dumps({'findings': current_criticals, 'time': time.strftime('%Y-%m-%d %H:%M:%S')}, ensure_ascii=False, indent=2))
                    except Exception:
                        pass
        else:
            # couldn't parse json; push error alert
            try:
                subprocess.run(['openclaw', 'system', 'event', '--mode', 'now', '--text', '🚨 Guardrails 审计失败：无法解析 openclaw security audit JSON'], timeout=30)
            except Exception:
                pass
    except Exception:
        pass

    return rc_any


if __name__ == "__main__":
    raise SystemExit(main())
