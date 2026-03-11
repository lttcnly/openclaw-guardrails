#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/reports"
mkdir -p "$OUT_DIR"
TS="$(date +%Y%m%d-%H%M%S)"

report="$OUT_DIR/audit-$TS.txt"
json="$OUT_DIR/models-status-$TS.json"

{
  echo "== OpenClaw Guardrails Audit =="
  echo "time: $(date)"
  echo

  echo "-- openclaw version"
  openclaw --version || true
  echo

  echo "-- openclaw status"
  openclaw status || true
  echo

  echo "-- openclaw security audit (deep)"
  openclaw security audit --deep || true
  echo

  echo "-- openclaw update status"
  openclaw update status || true
  echo

  echo "-- openclaw models status (probe)"
  openclaw models status --probe --json 2>&1 | sed -n '/^{/,$p' > "$json" || true
  echo "models json: $json"
  echo

  if [[ "$(uname)" == "Darwin" ]]; then
    echo "-- macOS listening ports"
    lsof -nP -iTCP -sTCP:LISTEN || true
    echo

    echo "-- macOS firewall state"
    /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate || true
    echo
  fi
} | tee "$report"

echo "\nSaved report: $report"
