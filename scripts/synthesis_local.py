#!/usr/bin/env python3
"""Local replacement for cross-repo-unifier.yml (Action disabled 2026-11-12).
Pulls live GitHub REST data via curl (urllib hits IncompleteRead on sandbox),
correlates repos by domain keywords, renders unified DAG via graphviz dot.
Outputs: data/synthesis.json, SYNTHESIS_PLAN.md, assets/synthesis/unified_dag.svg
"""
import os, json, subprocess, sys
from collections import defaultdict

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GH_USER = "Chrisalunlloyd2-sudo"

def sh(cmd, input=None):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                          cwd=REPO_DIR, input=input)

# token from origin url (pure python parse - no grep escaping headaches)
url = sh("git remote get-url origin").stdout.strip()
tok = url.split("x-access-token:")[1].split("@")[0] if "x-access-token:" in url else ""
if not tok:
    print("no token found in origin url:", url[:60]); sys.exit(1)

r = sh(f"curl -s -H 'Authorization: Bearer {tok}' "
       f"'https://api.github.com/users/{GH_USER}/repos?per_page=100&type=owner'")
try:
    repos_data = json.loads(r.stdout)
    assert isinstance(repos_data, list)
except Exception as e:
    print(f"repo fetch failed: {e}"); sys.exit(1)

try:
    todos_by_repo = json.load(open(os.path.join(REPO_DIR, "data/siphoned_todos.json")))
except Exception:
    todos_by_repo = {}

repo_names = [x["name"] for x in repos_data]
domain_keywords = {
    "Database": ["timescale", "postgres", "sql", "mongo", "hypertable", "vector", "corpus"],
    "Orchestration": ["airflow", "dag", "cron", "pipeline", "schedule", "dream"],
    "Agent/BDI": ["bdi", "fsm", "state", "belief", "intention", "desire", "memory", "markov", "ban"],
    "API/Web": ["api", "fastapi", "flask", "endpoint", "nginx", "caddy", "socket", "webui"],
    "Telemetry": ["stats", "telemetry", "metric", "log", "monitor", "svg", "heartbeat"],
}
repo_domains = defaultdict(set); cross_links = []; next_actions = []
for repo in repo_names:
    tasks = todos_by_repo.get(repo, [])
    combined = (repo + " " + " ".join(t.get("text", "") for t in tasks)).lower()
    for domain, keys in domain_keywords.items():
        if any(k in combined for k in keys):
            repo_domains[repo].add(domain)
for i, r1 in enumerate(repo_names):
    for r2 in repo_names[i+1:]:
        shared = repo_domains[r1].intersection(repo_domains[r2])
        if shared:
            cross_links.append({"source": r1, "target": r2, "domains": sorted(shared)})
priority_weight = {"FIXME": 1, "BUG": 1, "TODO": 2, "HACK": 3}
for repo, tasks in todos_by_repo.items():
    for t in tasks:
        next_actions.append({
            "priority": priority_weight.get(t.get("tag", "TODO"), 2),
            "tag": t.get("tag", "TODO"), "repo": repo, "task": t.get("text"),
            "location": t.get("file"),
            "domains": sorted(repo_domains.get(repo, ["General"]))})
next_actions.sort(key=lambda x: x["priority"])

os.makedirs(os.path.join(REPO_DIR, "data"), exist_ok=True)
os.makedirs(os.path.join(REPO_DIR, "assets/synthesis"), exist_ok=True)
payload = {
    "total_repos": len(repo_names), "cross_links": cross_links,
    "next_actions": next_actions[:25],
    "unified_stack": {d: [r for r, doms in repo_domains.items() if d in doms]
                      for d in domain_keywords},
}
json.dump(payload, open(os.path.join(REPO_DIR, "data/synthesis.json"), "w"), indent=2)

md = ["# 🌐 Multi-Repo Unified Synthesis & Next Steps", "",
      "> Automated correlation report generated for Kernel BDI execution loops. "
      "(local run by Alice — Action disabled 2026-11-12)", "",
      "### 🔗 Cross-Repository Domain Correlations",
      "| Source Repo | Target Repo | Shared Domains |", "| :--- | :--- | :--- |"]
for link in cross_links:
    md.append(f"| `{link['source']}` | `{link['target']}` | {', '.join(link['domains'])} |")
md += ["", "### ⚡ Prioritized Execution Queue (Next Steps)"]
for act in next_actions[:15]:
    icon = "🔴" if act["tag"] in ["FIXME", "BUG"] else "🟡" if act["tag"] == "HACK" else "🔵"
    md.append(f"- {icon} **[{act['tag']}]** `{act['repo']}` → {act['task']} *({act['location']})*")
open(os.path.join(REPO_DIR, "SYNTHESIS_PLAN.md"), "w").write("\n".join(md) + "\n")

dot = ['digraph UnifiedArchitecture {', '  bgcolor="#0d1117"; pad=0.3; rankdir=LR;',
       '  node [shape=box, style="filled,rounded", color="#30363d", fillcolor="#161b22", '
       'fontcolor="#c9d1d9", fontname="Courier"];',
       '  edge [color="#58a6ff", penwidth=1.2, arrowsize=0.8, fontcolor="#8b949e", '
       'fontname="Courier", fontsize=9];']
for repo, doms in repo_domains.items():
    dot.append(f'  "{repo}" [label="{repo}\\n[{", ".join(list(doms)[:2])}]", '
               f'color="#58a6ff", fillcolor="#161b22"];')
for link in cross_links:
    lbl = link["domains"][0] if link["domains"] else ""
    dot.append(f'  "{link["source"]}" -> "{link["target"]}" [label=" {lbl} "];')
dot.append("}")
open("/tmp/arch.dot", "w").write("\n".join(dot))
out = sh("dot -Tsvg /tmp/arch.dot -o assets/synthesis/unified_dag.svg")
if out.returncode != 0:
    print("dot failed:", out.stderr); sys.exit(1)

print(f"repos={len(repo_names)} links={len(cross_links)} actions={len(next_actions)} "
      f"stacked={sum(len(v) for v in repo_domains.values())}")
