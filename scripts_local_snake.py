#!/usr/bin/env python3
"""Local replacement for Platane/snk@v3 (GitHub Actions disabled 2026-11-12).
Parses the public contributions page and renders light/dark snake SVGs + ocean GIF
into docs/dist/. Data source: https://github.com/users/<user>/contributions"""
import re, sys, datetime, os
USER = "chrisalunlloyd2-sudo"
HTML = open("/tmp/contr.html", encoding="utf-8").read()
cells = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"', HTML)
if not cells:
    sys.exit("no contribution data parsed — do not fake output")
data = [(datetime.date.fromisoformat(d), int(l)) for d, l in cells]
data.sort()
PALETTE_L = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
PALETTE_D = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
C, S, G = 11, 11, 3          # cell, size, gap
X0, Y0 = 40, 24
start = data[0][0]
def col_wk(d): return (d - start).days // 7
def pos(d):
    return X0 + col_wk(d) * (C + G), Y0 + d.weekday() * (S + G)
weeks = col_wk(data[-1][0]) + 1
W = X0 + weeks * (C + G) + 16
H = Y0 + 7 * (S + G) + 34
def svg(palette, bg, fg, name):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="sans-serif">',
           f'<rect width="{W}" height="{H}" fill="{bg}"/>',
           f'<text x="{X0}" y="16" fill="{fg}" font-size="11">@{USER} contribution snake — regenerated locally by Alice (Actions disabled)</text>']
    for d, lv in data:
        x, y = pos(d)
        out.append(f'<rect x="{x}" y="{y}" width="{C}" height="{S}" rx="2" fill="{palette[lv]}"/>')
    # snake: body over last 21 active days, head at the newest
    tail = data[-21:]
    pts = " ".join(f"{pos(d)[0]+C/2},{pos(d)[1]+S/2}" for d, _ in tail)
    body = "#161b22" if palette is PALETTE_L else "#58e6ff"
    out.append(f'<polyline points="{pts}" fill="none" stroke="{body}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>')
    hx, hy = pos(data[-1][0])
    out.append(f'<circle cx="{hx+C/2}" cy="{hy+S/2}" r="5.5" fill="{body}"/>')
    out.append(f'<text x="{X0}" y="{H-8}" fill="{fg}" font-size="10">total {sum(l for _, l in data)} contributions · {len(data)} days · level 0-4</text>')
    out.append('</svg>')
    open(name, "w", encoding="utf-8").write("\n".join(out))
    print("wrote", name, os.path.getsize(name))
base = "/root/Chrisalunlloyd2-sudo/docs/dist"
svg(PALETTE_L, "#ffffff", "#24292f", f"{base}/github-snake.svg")
svg(PALETTE_D, "#0d1117", "#c9d1d9", f"{base}/github-snake-dark.svg")
try:
    from PIL import Image
    pal = [tuple(int(c, 16) for c in (q[1:3], q[3:5], q[5:7])) for q in PALETTE_D]
    # simple GIF: last 26 weeks heatmap, snake body advancing per frame
    weeks_n = min(26, weeks)
    rel = [c for c in data if col_wk(c[0]) >= weeks - weeks_n]
    cw, ch = 13, 13
    gw, gh = weeks_n * cw + 8, 7 * ch + 26
    frames = []
    n = len(rel)
    for f in range(0, min(n, 40)):
        img = Image.new("RGB", (gw, gh), (13, 17, 23))
        px = img.load()
        upto = int(n * (f + 1) / min(n, 40))
        for i, (d, lv) in enumerate(rel):
            x = 4 + col_wk(d) - (weeks - weeks_n)
            y = 3 + d.weekday()
            col = pal[lv] if i < upto - 1 else ((88, 230, 255) if i == upto - 1 else pal[lv])
            for yy in range(y * ch, y * ch + ch - 2):
                for xx in range(x * cw, x * cw + cw - 2):
                    px[xx, yy] = col
        frames.append(img)
    if frames:
        frames = [f.quantize(colors=16) for f in frames]
    if frames:
        frames[0].save(f"{base}/ocean.gif", save_all=True, append_images=frames[1:],
                       duration=90, loop=0, optimize=False)
        print("wrote", f"{base}/ocean.gif", os.path.getsize(f"{base}/ocean.gif"))
except Exception as e:
    print("gif skipped:", e)
print("cells", len(data), "weeks", weeks, "total", sum(l for _, l in data))
