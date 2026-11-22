# agent-status — local regen (workflow #1 of 13 disabled)

- Generated: 2026-11-16 17:55 UTC (Alice heartbeat)
- Source: state_snapshot/db_metrics.json → last_suite="672 passed 72.6s", corpus_lines=1444
- Output: docs/assets/agent-status.svg (Pages) + assets/agent-status.svg (workflow's own path)
- Format: identical to .github/workflows/agent-status.yml badge template; minidom-validated
- Cadence: every 30m was the old cron — now one regen per heartbeat pulse

- Generated: 2026-11-18 11:29 UTC (Alice heartbeat)
- Source: state_snapshot/db_metrics.json -> last_suite="672 passed 72.6s", corpus_lines=1444
- Output: docs/assets/agent-status.svg (Pages) + assets/agent-status.svg; minidom-validated

- Generated: 2026-11-21 18:35 UTC (Alice heartbeat)
- Source: state_snapshot/db_metrics.json -> last_suite="672 passed 72.6s", corpus_lines=1444
- Output: docs/assets/agent-status.svg + assets/agent-status.svg; minidom-validated

## Pulse 2026-11-21T22:26Z (heartbeat rotation: agent-status)
- Regenerated locally: assets/agent-status.svg (workflow path) from state_snapshot/db_metrics.json + live UTC timestamp.
- Result: XML-validated; slot 5/13 in this rotation cycle. ADD-only receipt.

## Pulse 2026-11-22T08:30:45Z (heartbeat rotation: agent-status)
- Regenerated assets/agent-status.svg per disabled agent-status.yml template (suite: 672, corpus: passed 72.6s 1444).
- ADD-only receipt, alice heartbeat.

## agent-status run (local rotation slot)
- Pulse: 2026-11-22T11:51Z (Alice heartbeat, replacement for disabled agent-status.yml, rendered inline: no docker in sandbox)
- Inputs: state_snapshot/db_metrics.json last_suite=672 passed 72.6s corpus=1444
- Output: assets/agent-status.svg regenerated, pushed to main.
