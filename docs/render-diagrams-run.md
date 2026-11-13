# render-diagrams.yml — local run status (heartbeat rotation 11/13)

- **Run at:** 2026-11-12 20:42 MST (2026-11-13T02:42Z)
- **Toolchain:** `scripts/render_mmd_local.py` (pure-Python mermaid flowchart-subset renderer — mmdc/Chrome unavailable in sandbox, disk at 127 MB free)
- **Input:** `schemas/pipeline.mmd` + `dags/pipeline.mmd` (identical, 5 nodes / 5 edges / 5 styles)
- **Output:** `assets/diagrams/pipeline_local.svg` (2.5 KB, XML-validated)
- **Note:** existing `assets/diagrams/pipeline.svg` (19.5 KB mmdc render) retained ADD-only — it is current; local renderer is the sandbox fallback for future runs.
- **FSM side (fsm-diagram.yml):** PlantUML recompiled `fsm/states.puml` → `assets/fsm/states.svg` **byte-identical** (diagram current, no commit needed).
- Workflow originally: push→`schemas/**.mmd`,`dags/**.mmd`; now run by Alice on heartbeat (workflows disabled 2026-11-12).
