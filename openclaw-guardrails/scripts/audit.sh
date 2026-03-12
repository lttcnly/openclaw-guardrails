#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/reports"
mkdir -p "$OUT_DIR"
TS="$(date +%Y%m%d-%H%M%S)"

report="$OUT_DIR/audit-$TS.txt"
models_json="$OUT_DIR/models-status-$TS.json"
openclaw_json="$OUT_DIR/openclaw-config-$TS.json"
skills_txt="$OUT_DIR/skills-check-$TS.txt"
netstat_txt="$OUT_DIR/netstat-tcp-$TS.txt"

have_cmd() { command -v "$1" >/dev/null 2>&1; }

{
  echo "== OpenClaw Guardrails Audit (read-only) =="
  echo "time: $(date)"
  echo

  echo "-- system"
  uname -a || true
  if [[ "$(uname)" == "Darwin" ]]; then
    sw_vers || true
    echo
    echo "-- disk encryption (FileVault)"
    fdesetup status 2>/dev/null || echo "(no permission / not available)"
    echo
    echo "-- Time Machine status"
    tmutil status 2>/dev/null || echo "(tmutil not available)"
    echo
  fi

  echo "-- openclaw version"
  openclaw --version || true
  echo

  echo "-- openclaw gateway status"
  openclaw gateway status 2>/dev/null || true
  echo

  echo "-- openclaw status"
  openclaw status || true
  echo

  echo "-- openclaw health (json)"
  openclaw health --json 2>/dev/null || true
  echo

  echo "-- openclaw config path"
  echo "config: $HOME/.openclaw/openclaw.json"
  if [[ -f "$HOME/.openclaw/openclaw.json" ]]; then
    # copy (redaction handled by humans; this file may contain secrets)
    cp -f "$HOME/.openclaw/openclaw.json" "$openclaw_json" 2>/dev/null || true
    echo "saved copy: $openclaw_json"
  fi
  echo

  echo "-- openclaw security audit (deep)"
  openclaw security audit --deep || true
  echo

  echo "-- openclaw update status"
  openclaw update status || true
  echo

  echo "-- openclaw skills check"
  openclaw skills check | tee "$skills_txt" || true
  echo "saved: $skills_txt"
  echo

  echo "-- openclaw models status (probe)"
  openclaw models status --probe --json 2>&1 | sed -n '/^{/,$p' > "$models_json" || true
  echo "models json: $models_json"
  echo

  if [[ "$(uname)" == "Darwin" ]]; then
    echo "-- macOS firewall state"
    /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate || true
    echo

    echo "-- macOS listening ports (tcp)"
    if [[ -x /usr/sbin/netstat ]]; then
      /usr/sbin/netstat -anv -p tcp > "$netstat_txt" || true
      # Show only listeners in main report for readability
      grep -E "LISTEN" "$netstat_txt" || true
      echo "saved: $netstat_txt"
    else
      echo "netstat not found"
    fi
    echo
  fi
} | tee "$report"

echo
echo "Saved report: $report"
