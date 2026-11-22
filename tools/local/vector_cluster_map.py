#!/usr/bin/env python3
"""Local replacement for disabled vector-cluster-map.yml (owned by Alice, heartbeat rotation).

Real data (data/repos_live.json from live GitHub REST + data/synthesis.json cross-links).
Features per repo: log1p(stars, forks, size_kb, open_issues) + staleness-days + fork flag + link degree.
z-scored, 2D projection via numpy SVD (PCA). Colored by language group; red-ringed cross-linked
core repos, sized by link degree. Deterministic (no RNG) so re-runs are byte-comparable modulo metadata.
"""
import json, math, datetime as dt
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NOW = dt.datetime(2026, 11, 15, tzinfo=dt.timezone.utc)
repos = json.load(open("data/repos_live.json"))
syn = json.load(open("data/synthesis.json"))
links = syn.get("cross_links", [])
if isinstance(links, int):
    # Schema variant: cross_links is a count; rebuild real edges from domains co-membership
    by_dom = syn.get("domains", {})
    pairs = {}
    for dom, members in by_dom.items():
        members = sorted(set(members))
        for i, a in enumerate(members):
            for b in members[i+1:]:
                pairs.setdefault((a, b), set()).add(dom)
    links = [{"source": a, "target": b, "domains": sorted(d)} for (a, b), d in sorted(pairs.items())]
degree, domains = {}, {}
for l in links:
    for k in ("source", "target"):
        n = l.get(k)
        if n:
            degree[n] = degree.get(n, 0) + 1
            domains.setdefault(n, set()).update(l.get("domains", []))

LANG_C = {"Python": "#58a6ff", "JavaScript": "#f0883e", "TypeScript": "#3178c6",
          "Kotlin": "#a371f7", "Java": "#ff6b6b", "HTML": "#7ee787",
          "CSS": "#79c0ff", "Shell": "#d29922", "Rust": "#dea584", "C++": "#8b949e"}
names = [r["name"] for r in repos]
rows, langs = [], []
for r in repos:
    try:
        stale = max(0.0, (NOW - dt.datetime.fromisoformat(r["pushed"].replace("Z", "+00:00"))).days)
    except Exception:
        stale = 0.0
    rows.append([math.log1p(r.get("stars") or 0), math.log1p(r.get("forks") or 0),
                 math.log1p(r.get("size_kb") or 0), math.log1p(r.get("open_issues") or 0),
                 stale / 365.0, 1.0 if r.get("fork") else 0.0,
                 math.log1p(degree.get(r["name"], 0))])
    langs.append(r.get("lang") or "Other")
X = np.array(rows, dtype=float)
mu, sd = X.mean(0), X.std(0); sd[sd == 0] = 1
Z = (X - mu) / sd
U, S, Vt = np.linalg.svd(Z, full_matrices=False)
P = U[:, :2] * S[:2]
var = S ** 2 / (S ** 2).sum()

fig, ax = plt.subplots(figsize=(9, 6), facecolor="#0d1117")
ax.set_facecolor("#0d1117")
plotted = set()
core = sorted(degree.items(), key=lambda kv: -kv[1])
for i, name in enumerate(names):
    lang = langs[i] if langs[i] in LANG_C else "Other"
    lab = lang if lang not in plotted else None
    plotted.add(lang)
    ax.scatter(P[i, 0], P[i, 1], c=LANG_C.get(lang, "#8b949e"), label=lab, s=40 + 18 * degree.get(name, 0),
               alpha=0.85, edgecolors="#30363d", linewidths=0.5, zorder=3)
    if degree.get(name, 0) > 0:
        ax.scatter(P[i, 0], P[i, 1], s=140 + 18 * degree.get(name, 0), facecolors="none",
                   edgecolors="#ff5555", linewidths=1.4, zorder=4)
for name, _deg in core[:8]:
    i = names.index(name)
    ax.annotate(name, (P[i, 0], P[i, 1]), textcoords="offset points", xytext=(6, 6),
                fontsize=7.5, color="#c9d1d9", zorder=5)
ax.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9", fontsize=8, loc="best")
ax.set_title(f"Kernel Cross-Repo Semantic Vector Clusters (PCA) — {len(repos)} repos, {len(links)} cross-links, live {NOW:%Y-%m-%d}",
             color="#58a6ff", fontsize=11, pad=12, fontname="monospace")
ax.set_xlabel(f"PC1 {var[0]*100:.1f}%", color="#8b949e", fontsize=9)
ax.set_ylabel(f"PC2 {var[1]*100:.1f}%", color="#8b949e", fontsize=9)
ax.tick_params(colors="#8b949e", labelsize=8)
for sp in ax.spines.values():
    sp.set_color("#30363d")
plt.tight_layout()
plt.savefig("assets/vectors/semantic_cluster.svg", format="svg", transparent=True)
print(f"OK repos={len(repos)} links={len(links)} core_ringed={len(degree)} PC1={var[0]*100:.1f}% PC2={var[1]*100:.1f}%")
