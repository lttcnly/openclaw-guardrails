# Threat Model (draft)

## Assets to protect
- API keys / tokens / OAuth refresh tokens
- private documents, photos, chat logs
- code repos and production data

## Adversaries
- drive-by prompt injection via web content
- malicious skill supply chain
- opportunistic scanning / exploitation of exposed services

## Key risks
1. Prompt injection
2. Destructive mis-ops
3. Skill poisoning
4. Platform vulnerabilities

## Security principles
- Treat all external content as untrusted data
- Least privilege for tools and credentials
- Two-phase commit for destructive operations
- Default-read-only audits
- Reduce exposure (bind loopback/tailnet; no public)
- Audit + patch cadence
