#!/usr/bin/env python3
"""Local replacement for disabled lowlighter/metrics workflow (slot 3/13).
Renders assets/github-metrics.svg from live GitHub API data. ADD-only."""
import json, os, subprocess, sys, datetime, urllib.request

TOKEN = os.environ.get("GH_TOKEN") or subprocess.run(
    ["git", "remote", "get-url", "origin"], capture_output=True, text=True).stdout
import re
m = re.search(r"x-access-token:([^@]+)", TOKEN)
TOKEN = m.group(1) if m else TOKEN.strip()

def api(path):
    req = urllib.request.Request("https://api.github.com" + path,
        headers={"Authorization": f"token {TOKEN}", "User-Agent": "metrics-local"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

me = api("/users/chrisalunlloyd2-sudo")
try:
    u = api("/user")
    login = u["login"]; private_ok = True
except Exception:
    login = me["login"]; private_ok = False

repos = []
for page in (1, 2):
    try:
        r = api(f"/users/{login}/repos?per_page=100&page={page}&sort=updated")
        if not isinstance(r, list): break
        repos += r
        if len(r) < 100: break
    except Exception: break
if private_ok:
    try:
        mine = api("/user/repos?per_page=100&sort=updated&affiliation=owner")
        if isinstance(mine, list):
            known = {x["full_name"] for x in repos}
            repos += [x for x in mine if x["full_name"] not in known]
    except Exception: pass

total_stars = sum(r.get("stargazers_count", 0) for r in repos)
total_forks = sum(r.get("forks_count", 0) for r in repos)
lang_bytes = {}
for r in repos:
    if r.get("fork"): continue
    lg = r.get("language") or "Other"
    lang_bytes[lg] = lang_bytes.get(lg, 0) + (r.get("size", 0))
lang_sorted = sorted(lang_bytes.items(), key=lambda kv: -kv[1])[:6]
lang_sum = sum(v for _, v in lang_sorted) or 1
top_repos = sorted([r for r in repos if not r.get("fork")],
                   key=lambda r: -(r.get("stargazers_count", 0) * 10 + r.get("size", 0)))[:8]

try:
    iso = (datetime.datetime.utcnow() - datetime.timedelta(days=365)).strftime("%Y-%m-%dT00:00:00Z")
    contrib = api(f"/users/{login}/events/public?per_page=100")
    week_commits = len([e for e in contrib if e["type"] == "PushEvent"])
except Exception:
    week_commits = 0

now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
W, H = 800, 560
accent, ink, sub, bg = "#2ea043", "#1f2328", "#656d76", "#ffffff"
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-sans-serif,Segoe UI,Helvetica,Arial">']
parts.append(f'<rect width="{W}" height="{H}" fill="{bg}"/>')
parts.append(f'<rect width="{W}" height="70" fill="{ink}"/>')
parts.append(f'<text x="28" y="44" font-size="24" fill="#ffffff" font-weight="700">@{login} — deep metrics</text>')
parts.append(f'<text x="28" y="62" font-size="12" fill="#9da7b1">local regeneration of lowlighter/metrics classic · {now}</text>')

stats = [("repositories", str(len(repos))), ("stars", str(total_stars)), ("forks", str(total_forks)),
         ("followers", str(me.get("followers", 0))), ("public events/100", str(week_commits)),
         ("mode", "private+public" if private_ok else "public")]
x = 28
for label, val in stats:
    parts.append(f'<text x="{x}" y="118" font-size="26" font-weight="700" fill="{ink}">{val}</text>')
    parts.append(f'<text x="{x}" y="138" font-size="11" fill="{sub}">{label}</text>')
    x += 132

parts.append(f'<text x="28" y="184" font-size="15" font-weight="700" fill="{ink}">Languages (repo size share, non-forks)</text>')
y = 206
for lg, b in lang_sorted:
    pct = b / lang_sum * 100
    parts.append(f'<text x="28" y="{y+11}" font-size="12" fill="{ink}">{lg}</text>')
    parts.append(f'<rect x="170" y="{y}" width="{int(pct*5)}" height="14" rx="3" fill="{accent}" opacity="0.85"/>')
    parts.append(f'<text x="{176+int(pct*5)}" y="{y+11}" font-size="11" fill="{sub}">{pct:.1f}%</text>')
    y += 24

parts.append(f'<text x="28" y="{y+26}" font-size="15" font-weight="700" fill="{ink}">Top repositories (stars · size)</text>')
y += 48
parts.append(f'<text x="28" y="{y}" font-size="11" fill="{sub}">REPO</text><text x="480" y="{y}" font-size="11" fill="{sub}">LANG</text><text x="600" y="{y}" font-size="11" fill="{sub}">★</text><text x="670" y="{y}" font-size="11" fill="{sub}">KB</text><text x="740" y="{y}" font-size="11" fill="{sub}">UPD</text>')
y += 20
for r in top_repos:
    nm = r["name"][:30]
    upd = (r.get("pushed_at") or "")[:10]
    parts.append(f'<text x="28" y="{y}" font-size="12" fill="{ink}">{nm}</text>')
    parts.append(f'<text x="480" y="{y}" font-size="12" fill="{sub}">{r.get("language") or "—"}</text>')
    parts.append(f'<text x="600" y="{y}" font-size="12" fill="{ink}">{r.get("stargazers_count",0)}</text>')
    parts.append(f'<text x="670" y="{y}" font-size="12" fill="{ink}">{r.get("size",0)}</text>')
    parts.append(f'<text x="740" y="{y}" font-size="11" fill="{sub}">{upd}</text>')
    y += 20

parts.append(f'<line x1="28" y1="{H-40}" x2="{W-28}" y2="{H-40}" stroke="#d0d7de"/>')
parts.append(f'<text x="28" y="{H-20}" font-size="11" fill="{sub}">Generated locally by scripts_local_metrics.py (Alice heartbeat rotation 3/13, replaces disabled metrics.yml). Pages: /Chrisalunlloyd2-sudo/</text>')
parts.append("</svg>")
out = "assets/github-metrics.svg"
with open(out, "w") as f:
    f.write("\n".join(parts))
print(f"wrote {out}: repos={len(repos)} stars={total_stars} forks={total_forks} lang={lang_sorted}")
