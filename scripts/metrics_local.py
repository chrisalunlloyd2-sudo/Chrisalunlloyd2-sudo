#!/usr/bin/env python3
"""Local replacement for metrics.yml (lowlighter/metrics classic template).
Pulls GitHub REST API data and renders assets/github-metrics.svg.
Run: GH_TOKEN=<classic pat> python3 scripts/metrics_local.py"""
import json, os, urllib.request, datetime, html

U = os.environ.get("METRICS_USER", "chrisalunlloyd2-sudo")
T = os.environ.get("GH_TOKEN") or os.environ.get("TOKEN")
OUT = os.environ.get("METRICS_OUT", "assets/github-metrics.svg")

import subprocess, tempfile
def api(path, _tries=3):
    """curl-based fetch — urllib hits IncompleteRead on this sandbox."""
    for i in range(_tries):
        p = subprocess.run(["curl", "-sf", "--retry", "2", "-H", "Authorization: Bearer " + T,
                            "-H", "User-Agent: metrics-local",
                            "https://api.github.com" + path],
                           capture_output=True, text=True, timeout=60)
        if p.returncode == 0 and p.stdout:
            try:
                return json.loads(p.stdout)
            except json.JSONDecodeError:
                pass
    raise RuntimeError(f"api fetch failed after {_tries} tries: {path}")

user = api(f"/users/{U}")
repos = api(f"/users/{U}/repos?per_page=100&sort=pushed")
commits = api(f"/repos/{U}/{U}/commits?per_page=100")

stars = sum(r.get("stargazers_count", 0) for r in repos)
forks = sum(r.get("forks_count", 0) for r in repos)
langs = {}
for r in repos:
    l = r.get("language")
    if l: langs[l] = langs.get(l, 0) + (r.get("size", 0) or 0)
langs = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
top = sorted(repos, key=lambda r: -(r.get("stargazers_count", 0) + r.get("forks_count", 0)))[:5]

# activity: commits per weekday (last 100 commits fetched)
days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
cnt = dict.fromkeys(days, 0)
hours = [0]*24
for c in commits:
    d = c.get("commit", {}).get("author", {}).get("date")
    if not d: continue
    dt = datetime.datetime.fromisoformat(d.replace("Z", "+00:00"))
    cnt[days[(dt.weekday()) % 7]] += 1
    hours[dt.hour] += 1
maxd = max(cnt.values()) or 1
maxh = max(hours) or 1

def esc(s): return html.escape(str(s))

W = 640
rows = []
rows.append(f'<rect x="0" y="0" width="{W}" height="96" fill="#0d1117"/>')
rows.append(f'<text x="24" y="42" font-family="Segoe UI,sans-serif" font-size="26" fill="#e6edf3" font-weight="bold">@{esc(user["login"])}</text>')
rows.append(f'<text x="24" y="70" font-family="Segoe UI,sans-serif" font-size="14" fill="#8b949e">Deep metrics (local) &#183; {user.get("public_repos")} public repos &#183; {user.get("followers")} followers &#183; generated {datetime.datetime.utcnow():%Y-%m-%d %H:%M} UTC</text>')

y = 130
def section(title):
    global y
    rows.append(f'<text x="24" y="{y}" font-family="Segoe UI,sans-serif" font-size="17" fill="#58a6ff" font-weight="bold">{title}</text>')
    y += 26

section("Activity &#183; commits by weekday (latest 100)")
for d in days:
    w = int(240 * cnt[d] / maxd)
    rows.append(f'<text x="24" y="{y+13}" font-family="Consolas,monospace" font-size="13" fill="#8b949e">{d}</text>')
    rows.append(f'<rect x="70" y="{y+2}" width="{max(w,2)}" height="16" rx="3" fill="#3fb950"/>')
    rows.append(f'<text x="{76+max(w,2)}" y="{y+14}" font-family="Consolas,monospace" font-size="12" fill="#8b949e">{cnt[d]}</text>')
    y += 22
y += 10

section("Community")
for label, val in [("Stars earned", stars), ("Forks", forks), ("Followers", user.get("followers")), ("Public repos", user.get("public_repos"))]:
    rows.append(f'<text x="24" y="{y+14}" font-family="Segoe UI,sans-serif" font-size="14" fill="#c9d1d9">{label}</text>')
    rows.append(f'<text x="600" y="{y+14}" text-anchor="end" font-family="Consolas,monospace" font-size="15" fill="#e6edf3">{val}</text>')
    y += 24
y += 10

section("Most-starred repos")
for r in top:
    nm = esc(r["name"]); s = r.get("stargazers_count",0); f = r.get("forks_count",0)
    lang = esc(r.get("language") or "-")
    rows.append(f'<text x="24" y="{y+14}" font-family="Segoe UI,sans-serif" font-size="14" fill="#c9d1d9">{nm}</text>')
    rows.append(f'<text x="330" y="{y+14}" font-family="Consolas,monospace" font-size="13" fill="#8b949e">{lang}</text>')
    rows.append(f'<text x="600" y="{y+14}" text-anchor="end" font-family="Consolas,monospace" font-size="13" fill="#e6edf3">&#11088;{s} &#8618;{f}</text>')
    y += 24
y += 10

section("Languages by repo size")
for l, b in langs:
    w = int(300 * b / langs[0][1])
    rows.append(f'<text x="24" y="{y+13}" font-family="Consolas,monospace" font-size="13" fill="#8b949e">{esc(l)}</text>')
    rows.append(f'<rect x="140" y="{y+2}" width="{max(w,2)}" height="16" rx="3" fill="#58a6ff"/>')
    y += 22

H = y + 40
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
       f'<rect width="{W}" height="{H}" fill="#010409"/>'
       f'<rect x="0" y="{H-32}" width="{W}" height="32" fill="#0d1117"/>'
       f'<text x="24" y="{H-11}" font-family="Segoe UI,sans-serif" font-size="12" fill="#484f58">Local replacement for metrics.yml &#183; generated by scripts/metrics_local.py &#183; {esc(U)}/{esc(U)}</text>'
       + "".join(rows) + "</svg>")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write(svg)
print(f"wrote {OUT} {len(svg)} bytes; stars={stars} forks={forks} repos={len(repos)} commits={len(commits)}")
