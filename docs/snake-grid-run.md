# snake_grid — local run (Alice heartbeat)

- Date: 2026-11-15T09:32Z
- Replacement for: `.github/workflows/snake_grid.yml` (disabled 2026-11-11, Actions minutes)
- Data source: github-contributions-api.jogruber.de/v4/Chrisalunlloyd2-sudo?y=last — 16,418 contributions / 365 day-cells (live pull)
- Regenerated: `docs/github-snake.svg`, `docs/github-snake-dark.svg`, `docs/ocean.svg` (all XML-validated)
- Method: boustrophedon crawl path, 53 week-columns x 7 weekdays, animated stroke snake head + moving head-dot, 3 palettes (github light / github-dark / ocean)
- Note: `ocean.gif` from old workflow not regenerated (SVG is the Pages source of truth)

## Run 4 — 2026-11-16T08:5Z heartbeat (slot snake_grid)

- Data source: github-contributions-api.jogruber.de/v4/Chrisalunlloyd2-sudo?y=last — 16,458 contributions / 366 day-cells (live pull)
- Regenerated: docs/github-snake.svg, docs/github-snake-dark.svg, docs/ocean.svg (all XML-validated)
- Method: fresh script /root/snake_gen.py — 53 week-columns boustrophedon path, animated stroke-dashoffset snake + animateMotion head-dot, 3 palettes, footer timestamp
- Note: ADD-only receipt, nothing deleted from GitHub

---

## Run 2026-11-16 07:00 MST — Alice local regeneration (replaces snake_grid.yml, disabled 2026-11-12)

- Source: live contribution calendar HTML for `chrisalunlloyd2-sudo` (fetched with VoiceHex PAT, read-only), 366 day-cells parsed with exact tooltip counts.
- Output regenerated: `docs/github-snake.svg` (light) + `docs/github-snake-dark.svg` (dark), 7×53 week grid, per-day tooltips, month labels, XML-valid (minidom).
- Stats: **16,454 contributions / last year**, 145 active days, peak day 5,102, levels 0–4 palette (light `#9be9a8…`, dark `#0e4429…`).
- `ocean.gif` color-snake output NOT regenerated (no Platane/snk runtime in sandbox) — SVG pair is the working replacement; honest skip.
- Pushed straight to `main` (Pages serves /docs directly). Next rotation slot: `bdi-state-hud`.

## Run 2026-11-18T00:23:54Z — heartbeat rotation slot `snake_grid` (local regen, replaces disabled snake_grid.yml)

- Source: live contribution API for chrisalunlloyd2-sudo via /root/snake_gen.py — 16,458 contributions / last year
- Regenerated: docs/github-snake.svg, docs/github-snake-dark.svg, docs/ocean.svg (all XML-validated)
- Method: boustrophedon 53x7 animated stroke path + head-dot, 3 palettes
- ADD-only receipt, pushed straight to main (Pages serves /docs)

## Run 2026-11-18T15:49:52Z — heartbeat rotation slot `snake_grid` cycle-2 (local regen, replaces disabled snake_grid.yml)

- Source: live contribution API for chrisalunlloyd2-sudo via /root/snake_gen.py — 16,458 contributions / last year
- Regenerated: docs/github-snake.svg, docs/github-snake-dark.svg, docs/ocean.svg (all XML-validated)
- ADD-only receipt, pushed straight to main (Pages serves /docs)
