# vector-cluster-map run (slot 11/13) — local heartbeat regen
- Date: 2026-11-13 | Replaces: disabled `.github/workflows/vector-cluster-map.yml`
- Data: **real** `data/synthesis.json` — 66 repos, 78 domain-tagged cross-links.
- Method: per-repo feature vector = one-hot domain membership + link degree, z-scored,
  2D projection via numpy SVD (PCA) — no sklearn needed in sandbox. Point size = link degree.
- Upgrade over workflow: the disabled workflow plotted `np.random.randn()` fake clusters.
- Output: `assets/vectors/semantic_cluster.svg` (Pages: https://chrisalunlloyd2-sudo.github.io/Chrisalunlloyd2-sudo/)
