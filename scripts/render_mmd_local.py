#!/usr/bin/env python3
"""Local replacement for render-diagrams.yml (mmdc requires Chrome; sandbox has none).

Renders the supported mermaid flowchart subset to a dark-theme SVG:
  - 'flowchart TD' graphs, node ids with [label] (supports <br/>), edge labels -.txt.-> / -->
  - 'style ID fill:..,stroke:..,color:..' directives
Usage: python3 scripts/render_mmd_local.py input.mmd output.svg
"""
import re, sys, html

def parse(text):
    nodes, edges, styles = {}, [], {}
    node_re = re.compile(r'([A-Za-z_][\w]*)\s*\[([^\]]*)\]')
    edge_re = re.compile(r'([A-Za-z_][\w]*)\s*(?:-\.([^>]*?)\.->|-->)\s*([A-Za-z_][\w]*)')
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(('flowchart', 'graph', '%%')):
            continue
        m = re.match(r'style\s+(\w+)\s+(.*)', line)
        if m:
            styles[m.group(1)] = dict(kv.split(':', 1) for kv in
                                      (p.strip() for p in m.group(2).split(',')) if ':' in kv)
            continue
        em = edge_re.search(line)
        if em:
            edges.append((em.group(1), em.group(3), (em.group(2) or '').strip()))
            for nid, lab in node_re.findall(line):
                nodes[nid] = lab
            nodes.setdefault(em.group(1), em.group(1))
            nodes.setdefault(em.group(3), em.group(3))
            continue
        nm = node_re.match(line)
        if nm:
            nodes[nm.group(1)] = nm.group(2)
    return nodes, edges, styles

def render(nodes, edges, styles):
    children = {n: [] for n in nodes}
    for s, d, _ in edges:
        if s in children and d in children and s != d:
            children[s].append(d)
    roots = [n for n in nodes if not any(n in c for c in children.values())] or list(nodes)
    depth, seen = {}, set()
    for r in roots:
        stack = [(r, 0)]
        while stack:
            n, d = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            depth[n] = d
            for c in children.get(n, []):
                stack.append((c, d + 1))
    for n in nodes:
        depth.setdefault(n, 0)
    rows = {}
    for n, d in sorted(depth.items(), key=lambda kv: (kv[1], kv[0])):
        rows.setdefault(d, []).append(n)
    NH, NW, GAPX, GAPY = 78, 260, 90, 110
    pos, maxw = {}, 0
    for d, ns in rows.items():
        total = len(ns) * NW + (len(ns) - 1) * GAPX
        maxw = max(maxw, total)
        for i, n in enumerate(ns):
            pos[n] = (i * (NW + GAPX), d * (NH + GAPY))
    width = maxw + 80
    height = (max(rows) + 1) * (NH + GAPY) - GAPY + 80
    ox = 40
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" font-family="ui-sans-serif,system-ui,sans-serif">',
           '<defs><marker id="ar" markerWidth="10" markerHeight="8" refX="9" refY="4" '
           'orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#7ee787"/></marker></defs>']
    for s, d, lbl in edges:
        if s not in pos or d not in pos:
            continue
        x1, y1 = pos[s][0] + ox + NW // 2, pos[s][1] + 40 + NH // 2
        x2, y2 = pos[d][0] + ox + NW // 2, pos[d][1] + 40 + NH // 2
        if s == d:  # self-loop
            path = f'M{x1-NW//4},{y1} C{x1-NW//2-30},{y1-50} {x1+NW//2+30},{y1-50} {x1+NW//4},{y1}'
            dash = ' stroke-dasharray="6 4"'
            out.append(f'<path d="{path}" fill="none" stroke="#7ee787" stroke-width="1.6"{dash} marker-end="url(#ar)"/>')
            if lbl:
                out.append(f'<text x="{x1}" y="{y1-56}" fill="#8b949e" font-size="11" text-anchor="middle">{html.escape(lbl)}</text>')
            continue
        if y2 > y1:
            my = (y1 + y2) / 2
            path = f'M{x1},{y1+NH//2} C{x1},{my} {x2},{my} {x2},{y2-NH//2}'
        else:
            path = f'M{x1},{y1-NH//2} C{x1},{(y1+y2)/2} {x2},{(y1+y2)/2} {x2},{y2+NH//2}'
        out.append(f'<path d="{path}" fill="none" stroke="#7ee787" stroke-width="1.6" marker-end="url(#ar)"/>')
        if lbl:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            out.append(f'<text x="{mx}" y="{my}" fill="#8b949e" font-size="11" text-anchor="middle">{html.escape(lbl)}</text>')
    for n, lab in nodes.items():
        if n not in pos:
            continue
        st = styles.get(n, {})
        fill = st.get('fill', '#16b22'.replace('b', '1b') if False else '#161b22')
        fill = st.get('fill', '#161b22'); stroke = st.get('stroke', '#58a6ff'); color = st.get('color', '#c9d1d9')
        x, y = pos[n][0] + ox, pos[n][1] + 40
        out.append(f'<rect x="{x}" y="{y}" width="{NW}" height="{NH}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
        parts = lab.split('<br/>')
        for i, p in enumerate(parts):
            ty = y + NH / 2 + 5 - (len(parts) - 1) * 8 + i * 16
            out.append(f'<text x="{x+NW//2}" y="{ty}" fill="{color}" font-size="13" text-anchor="middle" '
                       f'font-weight="{"600" if i == 0 else "400"}">{html.escape(p)}</text>')
    out.append('</svg>')
    return '\n'.join(out)

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    with open(src) as f:
        text = f.read()
    nodes, edges, styles = parse(text)
    with open(dst, 'w') as f:
        f.write(render(nodes, edges, styles))
    print(f'{src} -> {dst}: {len(nodes)} nodes, {len(edges)} edges, {len(styles)} styles')
