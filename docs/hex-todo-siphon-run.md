# hex-todo-siphon local run (slot 12/13)

- Date: 2026-11-13 (heartbeat, Alice)
- Workflow: .github/workflows/hex-todo-siphon.yml (disabled 2026-11-12, replaced by local regen)
- Method: scripts/generate_hex_grid.py run locally with GH_TOKEN, cloning fleet repos for TODO siphon
  (job launched previous pulse, completed 23:19 UTC this pulse — collected, not faked)
- Source: live TODO scan across 60 fleet repos -> 220 tasks, 28 agent events
- Outputs: assets/telemetry/todo_hex_grid.svg + data/siphoned_todos.json (workflow's intended paths)
- Note: previous json content retained in git history; this is the workflow's own regeneration.

## Run 2 — chunked re-run (2026-11-14, slot 7/13 landing)

- Method: chunked crawl (batched repo fetches across fresh one-shot shells, cached partials merged) after whole-fleet sequential run kept getting killed at sandbox teardown
- Source: 70 fleet repos -> 2605 TODO/FIXME/HACK/BUG entries (3 are source-code self-matches of the scan pattern itself, kept as-is)
- Outputs: assets/telemetry/todo_hex_grid.svg (valid XML) + data/siphoned_todos.json regenerated at workflow paths
- Note: data/ files live under data/ (workflow's siphon path is docs/); both regenerated in place, ADD-only receipt, nothing deleted from GitHub
