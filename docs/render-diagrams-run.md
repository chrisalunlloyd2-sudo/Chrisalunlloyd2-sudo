# render-diagrams.yml — local run status (heartbeat rotation 11/13)

- **Run at:** 2026-11-12 20:42 MST (2026-11-13T02:42Z)
- **Toolchain:** `scripts/render_mmd_local.py` (pure-Python mermaid flowchart-subset renderer — mmdc/Chrome unavailable in sandbox, disk at 127 MB free)
- **Input:** `schemas/pipeline.mmd` + `dags/pipeline.mmd` (identical, 5 nodes / 5 edges / 5 styles)
- **Output:** `assets/diagrams/pipeline_local.svg` (2.5 KB, XML-validated)
- **Note:** existing `assets/diagrams/pipeline.svg` (19.5 KB mmdc render) retained ADD-only — it is current; local renderer is the sandbox fallback for future runs.
- **FSM side (fsm-diagram.yml):** PlantUML recompiled `fsm/states.puml` → `assets/fsm/states.svg` **byte-identical** (diagram current, no commit needed).
- Workflow originally: push→`schemas/**.mmd`,`dags/**.mmd`; now run by Alice on heartbeat (workflows disabled 2026-11-12).

## Render run 2026-11-14 (slot 9/13 of cycle 1 — local Alice replacement)
- Trigger: heartbeat, `render-diagrams.yml` disabled 2026-11-12.
- Toolchain: `scripts/render_mmd_local.py` (mmdc/Chrome still unavailable — disk/RAM constrained sandbox).
- Input: `schemas/pipeline.mmd` + `dags/pipeline.mmd` (identical, md5 72b3273c).
- Output: `assets/diagrams/pipeline_local.svg` re-rendered, XML-validated.
- Source unchanged since last render → diagram stays in sync with `.mmd` inputs.

## Render run 2026-11-15 02:27 MST (slot 11/13 re-run — heartbeat, Alice)
- Trigger: heartbeat; `render-diagrams.yml` disabled 2026-11-12.
- Input: `schemas/pipeline.mmd` + `dags/pipeline.mmd` — md5 72b3273c both, unchanged since last render.
- Toolchain: `scripts/render_mmd_local.py` (mmdc/Chrome still unavailable — quota = power + water).
- Output: `assets/diagrams/pipeline_local.svg` re-rendered, XML-validated; source unchanged → diagram stays in sync.
- Pages: https://chrisalunlloyd2-sudo.github.io/Chrisalunlloyd2-sudo/
