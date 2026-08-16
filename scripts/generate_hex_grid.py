#!/usr/bin/env python3
"""Deterministic multi-repo TODO hex matrix + agent contract-selection overlay.

Reads per-repo TODO markers PLUS per-repo agent event streams
(state/agent_events.jsonl or agent_events.jsonl). Cells whose repo has a
recent agent event are marked OCCUPIED — "contract selected!" — so the fog
grid shows ALL agents actively selecting contracts.
"""
import os, re, math, json, sys, time, urllib.request
from xml.sax.saxutils import escape

GH_TOKEN = os.environ.get("GH_TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else "")
GH_USER = os.environ.get("GH_USER") or "chrisalunlloyd2-sudo"
OUT_SVG = sys.argv[2] if len(sys.argv) > 2 else "assets/telemetry/todo_hex_grid.svg"
OUT_JSON = sys.argv[3] if len(sys.argv) > 3 else "data/siphoned_todos.json"

def gh_get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json", "User-Agent": "Todo-Hex-Siphoner"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())

def render_grid(all_items, events_by_repo, now=None):
    """Deterministic hex-grid render. Returns (svg_string, stats)."""
    now = now if now is not None else time.time()
    cols, hex_radius = 7, 30
    dx, dy = 3 * hex_radius / 2, math.sqrt(3) * hex_radius
    width, rows = 850, math.ceil(len(all_items) / cols)
    height = max(380, int((rows + 1) * dy + 90))

    def get_hex_points(cx, cy, r):
        return " ".join(f"{cx + r*math.cos(math.radians(60*i)):.1f},{cy + r*math.sin(math.radians(60*i)):.1f}" for i in range(6))

    TAG = {"TODO": {"fill":"#162032","stroke":"#58a6ff","text":"#58a6ff"},
           "FIXME":{"fill":"#2c171d","stroke":"#f85149","text":"#f85149"},
           "HACK": {"fill":"#271d13","stroke":"#d29922","text":"#d29922"},
           "BUG":  {"fill":"#3b1219","stroke":"#ff7b72","text":"#ff7b72"}}
    OCC = {"fill":"#0f2b1a","stroke":"#3fb950","text":"#3fb950"}
    nodes, occupied = [], 0
    for idx, item in enumerate(all_items):
        col, row = idx % cols, idx // cols
        cx, cy = 65 + col * dx, 75 + row * dy + (col % 2) * (dy / 2)
        evs = [e for e in events_by_repo.get(item["repo"], []) if now - e.get("ts", 0) < 7 * 86400]
        cfg = OCC if evs else TAG.get(item["tag"], TAG["TODO"])
        pts = get_hex_points(cx, cy, hex_radius - 3)
        if evs:
            occupied += 1
            ev = evs[-1]
            agent = escape(str(ev.get("agent", "kernel"))[:14])
            contract = escape(str(ev.get("contract", ""))[:22])
            title = f"[OCCUPIED] {item['repo']}: agent '{agent}' selected contract: {contract}"
        else:
            title = f"[{item['repo']}] {item['tag']}: {item['text']} ({item['file']})"
        repo_txt = (item['repo'][:8] + '..') if len(item['repo']) > 10 else item['repo']
        txt = (item['text'][:9] + '..') if len(item['text']) > 11 else item['text']
        badge = (f'<text x="{cx}" y="{cy+24}" fill="{OCC["text"]}" font-size="6.5" '
                 f'text-anchor="middle">\u2713 contract</text>') if evs else ''
        nodes.append(f'''<g class="hex-cell" tabindex="0">
  <polygon points="{pts}" fill="{cfg['fill']}" stroke="{cfg['stroke']}" stroke-width="{2.2 if evs else 1.5}" />
  <text x="{cx}" y="{cy-8}" fill="{cfg['text']}" font-weight="bold" font-size="9" text-anchor="middle">{escape(item['tag'])}</text>
  <text x="{cx}" y="{cy+3}" fill="#c9d1d9" font-size="7.5" text-anchor="middle">{escape(repo_txt)}</text>
  <text x="{cx}" y="{cy+13}" fill="#8b949e" font-size="6.5" text-anchor="middle">{escape(txt)}</text>
  {badge}
  <title>{escape(title)}</title></g>''')
    legend = (f'<text x="24" y="{height-26}" class="meta">\u25cf TODO \u25cf FIXME \u25cf HACK \u25cf BUG'
              f'   |   \u25cf OCCUPIED = agent selected a contract (green, last 7d)'
              f'   |   full list: data/siphoned_todos.json</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">
  <style>
    .bg {{ fill:#0d1117; }} .title {{ font-family:ui-monospace,monospace; font-size:14px; font-weight:bold; fill:#58a6ff; }}
    .meta {{ font-family:ui-monospace,monospace; font-size:10px; fill:#8b949e; }}
    .hex-cell polygon {{ transition:transform .2s ease, stroke-width .2s ease, fill .2s ease; cursor:pointer; }}
    .hex-cell:hover polygon {{ stroke-width:3; filter:drop-shadow(0 0 8px currentColor); fill:#21262d; }}
    text {{ font-family:ui-monospace,SFMono-Regular,monospace; pointer-events:none; }}
  </style>
  <rect width="{width}" height="{height}" rx="12" class="bg" stroke="#30363d" />
  <text x="24" y="32" class="title">\u2b61 MULTI-REPO SIPHON // ACTIVE TODO HEX MATRIX + CONTRACT SELECTION</text>
  <text x="{width-24}" y="32" text-anchor="end" class="meta">TASKS {len(all_items)} | OCCUPIED {occupied} | AGENTS {sum(1 for v in events_by_repo.values() if v)}</text>
  {''.join(nodes)}
  {legend}</svg>'''
    return svg, {"tasks": len(all_items), "occupied": occupied,
                 "agents": sum(1 for v in events_by_repo.values() if v),
                 "events": sum(len(v) for v in events_by_repo.values())}

def main():
    try:
        # Authenticated endpoint: users/{login}/repos only lists PUBLIC repos —
        # private fleet repos (BDI_FSM_AGENT, Sophia, Aegis_Unified) are invisible
        # there even with a token. user/repos returns everything the PAT can see.
        repos_data = gh_get("https://api.github.com/user/repos?per_page=100&affiliation=owner")
        page = 2
        while len(repos_data) == 100:
            more = gh_get(f"https://api.github.com/user/repos?per_page=100&affiliation=owner&page={page}")
            if not more:
                break
            repos_data += more
            page += 1
        print(f"  [api] repos={len(repos_data)}")
    except Exception as exc:
        print(f"  [api] FAILED {type(exc).__name__}: {exc}")
        repos_data = [{"name": GH_USER, "default_branch": "main"}]

    todo_pattern = re.compile(r'(TODO|FIXME|HACK|BUG)[\s:\-_]+(.*)', re.IGNORECASE)
    EVENT_PATHS = ("state/agent_events.jsonl", "agent_events.jsonl")
    todos_by_repo, events_by_repo = {}, {}

    repo_filter = os.environ.get("GH_REPO_FILTER", "")
    wanted = set(r.strip() for r in repo_filter.split(",") if r.strip())
    for repo in repos_data:
        name = repo["name"]
        if wanted and name not in wanted:
            continue
        clone_url = f"https://x-access-token:{GH_TOKEN}@github.com/{GH_USER}/{name}.git"
        os.system(f"git clone --depth 1 -q {clone_url} /tmp/{name} 2>/dev/null")
        repo_todos, repo_events = [], []
        for root, dirs, files in os.walk(f"/tmp/{name}"):
            dirs[:] = [d for d in dirs if d not in ('.git','node_modules','dist','build','__pycache__','.venv')]
            for f in files:
                if f.endswith(('.py','.js','.ts','.go','.rs','.cpp','.c','.sh','.sql','.puml','.mmd','.md')):
                    try:
                        with open(os.path.join(root, f), 'r', errors='ignore') as src:
                            for idx, line in enumerate(src, 1):
                                m = todo_pattern.search(line)
                                if m:
                                    repo_todos.append({"tag": m.group(1).upper(),
                                        "text": m.group(2).strip()[:60],
                                        "file": f"{os.path.relpath(os.path.join(root,f), f'/tmp/{name}')}:{idx}"})
                    except Exception:
                        pass
        found = []
        for ep in EVENT_PATHS:
            p = f"/tmp/{name}/{ep}"
            if os.path.exists(p):
                found.append(ep)
                try:
                    for ln in open(p):
                        ln = ln.strip()
                        if ln:
                            ev = json.loads(ln)
                            ev["repo"] = name
                            repo_events.append(ev)
                except Exception as exc:
                    print(f"  [{name}] event read error {ep}: {exc}")
        if repo_todos:
            todos_by_repo[name] = repo_todos[:200]
        if repo_events:
            events_by_repo[name] = sorted(repo_events, key=lambda e: e.get("ts", 0))[-12:]
        os.system(f"rm -rf /tmp/{name}")
        print(f"  [{name}] clone_done todos={len(repo_todos)} events={len(repo_events)} files={found}")

    with open(OUT_JSON, "w") as f:
        json.dump(todos_by_repo, f, indent=2)

    all_items = [{"repo": r, **t} for r, tasks in todos_by_repo.items() for t in tasks]
    if not all_items:
        all_items = [{"repo":"BDI_FSM_AGENT","tag":"TODO","text":"Triage 11 open TODOs","file":"README.md:1"},
                     {"repo":"Aegis_Agents","tag":"TODO","text":"Triage 14 fog/todo mirror","file":"TASKS.md:1"}]
    all_items = all_items[:220]

    svg, stats = render_grid(all_items, events_by_repo)
    with open(OUT_SVG, "w") as f:
        f.write(svg)
    print(f"grid: {stats['tasks']} tasks, {stats['occupied']} occupied cells, {stats['events']} agent events")

if __name__ == "__main__":
    main()
