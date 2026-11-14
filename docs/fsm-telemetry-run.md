run: fsm-telemetry-plot (workflow slot — local Alice regen)
date: 2026-11-14T18:49:22+00:00
slot: 6/13
output: assets/agent/fsm_density.svg
source: fsm/states.puml topology (18 edges, 8 states) × whole-word trigger occurrence counts in repo source (excl. .git/assets/docs)
total_weight: 53
max_cell: 39 (COMMIT → IDLE); next VERIFY → COMMIT 11, VERIFY → BLOCKED 2
note: deterministic real data replaces np.random.randint noise of the disabled workflow; counts tightened vs 2026-11-13 receipt (160 → 53) by whole-word matching — 'pass'/'fail' no longer match substrings. Workflow fsm-telemetry-plot.yml remains disabled.
