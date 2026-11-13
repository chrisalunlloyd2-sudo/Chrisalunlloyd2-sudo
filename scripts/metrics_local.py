#!/usr/bin/env python3
"""Local replacement for the disabled metrics.yml (lowlighter/metrics "classic" template).
Reads cached GitHub API responses in .cache/ + git activity, writes docs/assets/github-metrics.svg.
Output path matches the workflow's `filename: assets/github-metrics.svg` under docs/.
"""
import json, html, datetime, collections, pathlib, subprocess, os

ROOT = pathlib.Path(__file__).resolve().parent.parent
C = ROOT / ".cache"
OUT = ROOT / "docs" / "assets" / "github-metrics.svg"

user = json.load(open(C / "gh_user.json"))
langs = json.load(open(C / "gh_languages.json"))
repos = json.load(open(C / "gh_repos1.json")) + json.load(open(C / "gh_repos2.json"))
repos = [r for r in repos if not r.get("fork")]

# activity: last 365 days of commits (all branches) from local git
activity = {}
for line in open(C / "activity_year.txt"):
    d, n = line.split()
    activity[d] = int(n)
days = sorted(activity)
total_commits = sum(activity.values())
peak = max(activity.values()) if activity else 1

def esc(s): return html.escape(str(s), quote=True)
def fmt_date(s): return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").strftime("%d %b %Y")

created = fmt_date(user["created_at"])
now = datetime.datetime.utcnow()
age_days = (now - datetime.datetime.strptime(user["created_at"], "%Y-%m-%dT%H:%M:%SZ")).days

# language bar (bytes -> %)
tot_bytes = sum(langs.values()) or 1
LANG_COLORS = {"Python": "#3572A5", "JavaScript": "#f1e05a", "Mermaid": "#ff3670",
               "HTML": "#e34c26", "CSS": "#563d7c", "Java": "#b07219", "Smali": "#e2e200"}
lang_items = sorted(langs.items(), key=lambda kv: -kv[1])
lang_rows, x = [], 0.0
for name, b in lang_items:
    w = b / tot_bytes * 760
    lang_rows.append(f'<rect x="{80+x:.1f}" y="0" width="{max(w,2):.1f}" height="26" fill="{LANG_COLORS.get(name,"#8b949e")}"><title>{esc(name)} {b/tot_bytes*100:.1f}%</title></rect>')
    x += w
legend = "  ".join(f'<tspan fill="{LANG_COLORS.get(n,"#8b949e")}">■</tspan> {esc(n)} {b/tot_bytes*100:.1f}%' for n, b in lang_items)

# top repos by stars/pushed
top = sorted(repos, key=lambda r: (r["stargazers_count"], r["pushes"] if "pushes" in r else 0), reverse=True)[:6]
repo_rows = "".join(
    f'<tr><td><a href="{esc(r["html_url"])}">{esc(r["full_name"])}</a></td>'
    f'<td class="c">{r["stargazers_count"]}</td><td class="c">{r["forks_count"]}</td>'
    f'<td class="c">{(r["language"] or "—")}</td>'
    f'<td class="c">{fmt_date(r["pushed_at"]) if r.get("pushed_at") else "—"}</td></tr>'
    for r in top)

# activity sparkline: 53 weeks x 7 days grid
grid = ""
if days:
    first = datetime.date.fromisoformat(days[0])
    for d in days:
        dt = datetime.date.fromisoformat(d)
        idx = (dt - first).days
        col, row = idx // 7, idx % 7
        n = activity[d]
        lvl = 0 if n == 0 else min(4, 1 + (n * 4) // max(peak, 1))
        color = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"][lvl]
        grid += f'<rect x="{col*14}" y="{row*14}" width="12" height="12" rx="2" fill="{color}"><title>{d}: {n} commits</title></rect>'
    grid_w = (len(days) // 7 + 1) * 14
else:
    grid_w = 700

active_days = len(days)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="840" height="{700 + (0 if days else 0)}" viewBox="0 0 840 700" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">
<style>
  .bg{{fill:#0d1117}} .card{{fill:#161b22;stroke:#30363d;stroke-width:1;rx:8}}
  text{{fill:#c9d1d9}} .h1{{font-size:24px;font-weight:700;fill:#f0f6fc}}
  .h2{{font-size:15px;font-weight:700;fill:#f0f6fc}} .muted{{fill:#8b949e;font-size:12px}}
  .big{{font-size:28px;font-weight:700;fill:#58a6ff}} .c{{text-anchor:middle}}
  a{{fill:#58a6ff;text-decoration:none}} table{{font-size:13px}}
  th{{fill:#8b949e;font-size:11px;text-transform:uppercase;letter-spacing:.5px}}
  .stat{{font-size:22px;font-weight:700;fill:#3fb950}}
</style>
<rect class="bg" width="840" height="700"/>

<!-- header -->
<rect class="card" x="20" y="20" width="800" height="110" rx="8"/>
<image href="https://avatars.githubusercontent.com/u/{user['id']}?v=4" x="40" y="40" width="70" height="70" clip-path="circle(35px at 35px 35px)"/>
<text class="h1" x="130" y="65">{esc(user['login'])}</text>
<text class="muted" x="130" y="88">Account created {created} · {age_days} days active · "{esc(user['bio'] or 'autonomous agent fleet operator')}"</text>
<text class="muted" x="130" y="108">{user['public_repos']} public repos · {user['followers']} followers · {user['following']} following</text>

<!-- stats -->
<rect class="card" x="20" y="145" width="190" height="80" rx="8"/>
<text class="stat c" x="115" y="185">{total_commits}</text><text class="muted c" x="115" y="208">commits / 365d</text>
<rect class="card" x="225" y="145" width="190" height="80" rx="8"/>
<text class="stat c" x="320" y="185">{active_days}</text><text class="muted c" x="320" y="208">active days</text>
<rect class="card" x="430" y="145" width="190" height="80" rx="8"/>
<text class="stat c" x="525" y="185">{len(repos)}</text><text class="muted c" x="525" y="208">own repos</text>
<rect class="card" x="635" y="145" width="185" height="80" rx="8"/>
<text class="stat c" x="727" y="185">{peak}</text><text class="muted c" x="727" y="208">peak commits/day</text>

<!-- activity grid -->
<rect class="card" x="20" y="240" width="800" height="140" rx="8"/>
<text class="h2" x="40" y="268">Activity — last {active_days} days</text>
<g transform="translate(40,285)">{grid}</g>

<!-- languages -->
<rect class="card" x="20" y="395" width="800" height="95" rx="8"/>
<text class="h2" x="40" y="423">Languages — {esc(user['login'])}/Chrisalunlloyd2-sudo</text>
<g transform="translate(0,435)"><svg x="80" y="0" width="760" height="26" overflow="visible">{"".join(lang_rows)}</svg></g>
<text class="muted" x="40" y="478"><tspan>{legend}</tspan></text>

<!-- repositories -->
<rect class="card" x="20" y="505" width="800" height="175" rx="8"/>
<text class="h2" x="40" y="533">Repositories</text>
<text class="muted" x="40" y="560" font-size="13">REPO<tspan dx="330">★</tspan><tspan dx="60">FORKS</tspan><tspan dx="55">LANG</tspan><tspan dx="60">LAST PUSH</tspan></text>
<line x1="40" y1="568" x2="800" y2="568" stroke="#30363d"/>
<text class="muted" x="40" y="592" font-size="13">
{chr(10).join('' for _ in [])}
</text>
<g font-size="13">{"".join(f'<text y="{592+i*22}"><a href="{esc(r["html_url"])}" fill="#58a6ff">{esc(r["full_name"])}</a></text><text class="c" x="510" y="{592+i*22}">{r["stargazers_count"]}</text><text class="c" x="580" y="{592+i*22}">{r["forks_count"]}</text><text class="c" x="650" y="{592+i*22}">{esc(r["language"] or "—")}</text><text class="c" x="745" y="{592+i*22}">{fmt_date(r["pushed_at"]) if r.get("pushed_at") else "—"}</text>' for i, r in enumerate(top))}</g>
<text class="muted" x="40" y="668">Generated locally by scripts/metrics_local.py (Alice heartbeat · replacement for disabled metrics.yml) · {now.strftime("%Y-%m-%d %H:%M")} UTC</text>
</svg>'''

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg)
print(f"wrote {OUT} ({len(svg)} bytes, {total_commits} commits, {active_days} active days, {len(repos)} repos)")
