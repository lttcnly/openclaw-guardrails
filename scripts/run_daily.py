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
                # Push alert to main session (danger/virus detected)
                findings = [f['title'] for f in data.get('findings', []) if f.get('severity') == 'critical'][:5]
                alert_lines = [
                    "🚨 **Guardrails 发现高危风险**",
                    f"- critical: {crit}",
                ]
                for f in findings:
                    alert_lines.append(f"  - {f}")
                alert_lines.append(f"- 完整报告：{audit_path}")
                alert_text = "\n".join(alert_lines)
                try:
                    subprocess.run(['openclaw', 'system', 'event', '--mode', 'now', '--text', alert_text], timeout=30)
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
