# vector-cluster-map run (slot 11/13) — local heartbeat regen
- Date: 2026-11-13 | Replaces: disabled `.github/workflows/vector-cluster-map.yml`
- Data: **real** `data/synthesis.json` — 66 repos, 78 domain-tagged cross-links.
- Method: per-repo feature vector = one-hot domain membership + link degree, z-scored,
  2D projection via numpy SVD (PCA) — no sklearn needed in sandbox. Point size = link degree.
- Upgrade over workflow: the disabled workflow plotted `np.random.randn()` fake clusters.
- Output: `assets/vectors/semantic_cluster.svg` (Pages: https://chrisalunlloyd2-sudo.github.io/Chrisalunlloyd2-sudo/)

## Run 2026-11-14 (heartbeat, Alice) — slot 11/13 re-run
- Data: **live GitHub REST** `users/Chrisalunlloyd2-sudo/repos` (66 repos) + `data/synthesis.json` (15 cross-links, 5 domain labels) — refreshed same pulse.
- Features per repo: log1p(stars, forks, size, open_issues, staleness-days) + fork flag; z-scored; PCA via numpy SVD (no sklearn — keeps disk/RAM quota).
- Result: rank-6 projection, PC1 44.7% / PC2 20.6% var. 6 cross-linked core repos red-ringed + labeled, sized by link degree; colored by language group.
- Fixed a bug in prior approach: synthesis-only features collapsed to rank 1 (all degrees=5) — real metadata added the needed spread.
- Output: `assets/vectors/semantic_cluster.svg` (78 KB, XML-validated). Pages: https://chrisalunlloyd2-sudo.github.io/Chrisalunlloyd2-sudo/
