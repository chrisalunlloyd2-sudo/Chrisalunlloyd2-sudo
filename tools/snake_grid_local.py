#!/usr/bin/env python3
"""Local replacement for snake_grid.yml (Actions disabled 2026-11-12).
Fetches the owner's contribution calendar via GraphQL and renders a GitHub-style
contribution heatmap SVG to docs/snake_grid.svg. Data source: GitHub API only."""
import json, subprocess, sys, datetime, pathlib

OWNER = "chrisalunlloyd2-sudo"
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "snake_grid.svg"

def token():
    url = subprocess.check_output(
        ["git", "-C", str(ROOT), "remote", "get-url", "origin"], text=True).strip()
    if "x-access-token:" in url:
        return url.split("x-access-token:")[1].split("@")[0].split(":")[0]
    raise SystemExit("no token in origin url")

def fetch(tok):
    q = ('query{user(login:"%s"){contributionsCollection{contributionCalendar'
         '{weeks{contributionDays{date contributionCount contributionLevel}}}}}}') % OWNER
    r = subprocess.run(["curl", "-s", "-H", f"Authorization: token {tok}",
                        "-H", "Content-Type: application/json",
                        "-d", json.dumps({"query": q}),
                        "https://api.github.com/graphql"],
                       capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    if "errors" in d:
        raise SystemExit(f"graphql: {d['errors']}")
    weeks = d["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [c for w in weeks for c in w["contributionDays"]]

COLORS = {"NONE": "#161b22", "FIRST": "#0e4429", "SECOND": "#006d32",
          "THIRD": "#26a641", "FOURTH": "#39d353"}

def render(days):
    cell, pad, gap = 11, 20, 3
    step = cell + gap
    weeks = [[]]
    # align to weeks: first day column = weekday of first date
    d0 = datetime.date.fromisoformat(days[0]["date"])
    weeks[0] = [None] * d0.weekday()
    for d in days:
        wd = datetime.date.fromisoformat(d["date"]).weekday()
        if wd == 0 and weeks[-1]:
            weeks.append([])
        weeks[-1].append(d)
    rows = 7
    w = pad * 2 + len(weeks) * step
    h = pad * 2 + rows * step + 30
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',
         f'<rect width="{w}" height="{h}" fill="#0d1117" rx="6"/>',
         f'<text x="{pad}" y="{pad+6}" fill="#e6edf3" font-size="13" font-weight="600">'
         f'{OWNER} contributions</text>']
    total = sum(c["contributionCount"] for c in days)
    p.append(f'<text x="{w-pad}" y="{pad+6}" fill="#8b949e" font-size="12" '
             f'text-anchor="end">{total} contributions in the last year</text>')
    y0 = pad + 24
    for wi, week in enumerate(weeks):
        for di, d in enumerate(week):
            if d is None:
                continue
            col = COLORS.get(d["contributionLevel"], "#39d353")
            x = pad + wi * step
            y = y0 + di * step
            p.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                     f'rx="2" fill="{col}"><title>{d["date"]}: '
                     f'{d["contributionCount"]} contributions</title></rect>')
    ly = y0 + rows * step + 14
    p.append(f'<text x="{pad}" y="{ly+9}" fill="#8b949e" font-size="11">Less</text>')
    for i, k in enumerate(["NONE", "FIRST", "SECOND", "THIRD", "FOURTH"]):
        p.append(f'<rect x="{pad+34+i*(cell+3)}" y="{ly}" width="{cell}" '
                 f'height="{cell}" rx="2" fill="{COLORS[k]}"/>')
    p.append(f'<text x="{pad+34+5*(cell+3)+6}" y="{ly+9}" fill="#8b949e" '
             f'font-size="11">More</text>')
    p.append("</svg>")
    return "\n".join(p), total

def main():
    days = fetch(token())
    svg, total = render(days)
    OUT.write_text(svg)
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    rec = ROOT / "docs" / "snake-grid-run.md"
    rec.write_text(f"# snake_grid — local run (Actions disabled)\n\n"
                   f"- when: {stamp}\n"
                   f"- source: GitHub GraphQL contributionCalendar for {OWNER}\n"
                   f"- days: {len(days)}  total: {total}\n"
                   f"- output: docs/snake_grid.svg\n"
                   f"- generator: tools/snake_grid_local.py (replaces snake_grid.yml)\n")
    print(f"OK {len(days)} days, {total} contributions -> {OUT}")

if __name__ == "__main__":
    sys.exit(main())
