# Vulnerability Layer (v0.2 draft)

This layer goes beyond heuristic pattern flags and adds:

1) **Dependency vulnerability scans** (best-effort)
   - Python: `pip-audit` if available
   - Node: `npm audit` if a project has lockfiles
   - Optional OSV (network) can be added later

2) **Skill hash pinning**
   - Generate a baseline manifest (sha256 per file)
   - Verify current state against the baseline
   - Detect silent supply-chain changes (unexpected updates / tampering)

3) **Provenance / SBOM-lite**
   - For each skill: origin metadata (if present), version tag, file inventory, hashes

## Philosophy

- Default: **read-only**.
- Best-effort: if a scanner tool is missing, we still output actionable guidance.
- No secrets: never dump raw tokens/keys.

## Scripts

- `scripts/vuln_scan.py` — best-effort dependency vulnerability scan
- `scripts/hash_pin.py` — generate baseline hashes
- `scripts/hash_verify.py` — verify against a baseline
- `scripts/sbom.py` — SBOM-lite + provenance report
