#!/usr/bin/env python3
"""Regenerate the-mesh-atlas.html — a radial map of the whole mesh + index.
Run nightly from grow.sh so the atlas stays in step with the living game."""
import json, os, math
from collections import deque, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RD = os.path.join(ROOT, "rooms")
rooms = {}
for fn in os.listdir(RD):
    if fn == "manifest.json": continue
    rooms[fn[:-5]] = json.load(open(os.path.join(RD, fn)))
man = json.load(open(os.path.join(RD, "manifest.json"))); entry = man["entry"]

adj = defaultdict(dict); edges = set(); frontier = 0
for rid, r in rooms.items():
    for ex in r.get("exits", []):
        to = ex.get("to", "")
        if isinstance(to, str) and to.startswith("NEW:"): frontier += 1
        elif to in rooms:
            adj[rid][ex["dir"]] = to; edges.add(tuple(sorted((rid, to))))

parent = {entry: None}; children = defaultdict(list); depth = {entry: 0}
q = deque([entry])
while q:
    cur = q.popleft()
    for d, nxt in sorted(adj[cur].items()):
        if nxt not in parent:
            parent[nxt] = cur; children[cur].append(nxt); depth[nxt] = depth[cur] + 1
            q.append(nxt)
reachable = set(parent)
unreached = [rid for rid in rooms if rid not in reachable]

leafslot = [0.0]; ang = {}
st = [(entry, False)]
while st:
    n, done = st.pop()
    if done:
        if children[n]:
            cs = [ang[c] for c in children[n]]; ang[n] = (min(cs) + max(cs)) / 2
        else:
            ang[n] = leafslot[0]; leafslot[0] += 1
    else:
        st.append((n, True))
        for c in reversed(children[n]): st.append((c, False))
leaves = max(1, leafslot[0]); maxd = max(depth.values()) if depth else 1

W = 1500; cx = cy = W / 2; ring = (W / 2 - 60) / max(1, maxd)
REGC = {"The Clean Archive": "#59f2b0", "The Comparisons": "#7cc7ff",
        "The Diagnostic Render": "#ff71ce", "The Understory": "#ffd166"}
def region_color(rid): return REGC.get(rooms[rid].get("region", ""), "#6a6a6a")
P = {}
for rid in reachable:
    a = ang[rid] / leaves * 2 * math.pi - math.pi / 2; r = depth[rid] * ring
    P[rid] = (cx + math.cos(a) * r, cy + math.sin(a) * r)
for i, rid in enumerate(unreached):
    a = i / max(1, len(unreached)) * 2 * math.pi
    P[rid] = (cx + math.cos(a) * (W / 2 - 25), cy + math.sin(a) * (W / 2 - 25))
rev = set(rid for rid, r in rooms.items()
          if r.get("reverie") and any(f.get("verb") == "reverie" for f in r.get("features", [])))

sv = [f'<svg viewBox="0 0 {W} {W}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;background:#04080a">']
for a, b in edges:
    if a in P and b in P:
        x1, y1 = P[a]; x2, y2 = P[b]
        sv.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#173a28" stroke-width="1"/>')
for rid, (x, y) in P.items():
    c = region_color(rid); rr = 3
    if rid == entry: rr = 7; c = "#ffffff"
    if rid in rev:
        sv.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="7" fill="none" stroke="#ffb37a" stroke-width="1.5"/>')
    sv.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr}" fill="{c}"/>')
tx, ty = P[entry]
sv.append(f'<text x="{tx+9:.0f}" y="{ty+4:.0f}" fill="#fff" font-size="15" font-family="monospace">START</text>')
sv.append("</svg>")

byreg = defaultdict(list)
for rid, r in rooms.items(): byreg[r.get("region", "?")].append((r.get("title", rid), rid, r))
order = ["The Clean Archive", "The Comparisons", "The Diagnostic Render", "The Understory"]
order += [x for x in byreg if x not in order]
idx = []
for reg in order:
    if reg not in byreg: continue
    rows = []
    for title, rid, r in sorted(byreg[reg]):
        insc = (r.get("inscription", "") or "")[:88]
        fname = (r.get("file", {}) or {}).get("name", "")
        star = ' <span class="rv">✷</span>' if rid in rev else ""
        rows.append(f'<li><b>{title}</b>{star}<br><span class="ins">“{insc}”</span><br><span class="fl">{fname}</span></li>')
    col = REGC.get(reg, "#6a6a6a")
    idx.append(f'<details><summary style="color:{col}">{reg} &middot; {len(byreg[reg])}</summary><ul>{"".join(rows)}</ul></details>')
stats = f'{len(rooms)} nodes &middot; {len(edges)} routes &middot; {frontier} undreamt frontiers &middot; {len(rev)} memories &middot; {man.get("nights","?")} nights deep'
legend = ' &nbsp; '.join(f'<span style="color:{c}">●</span> {r.split(" ",1)[1] if " " in r else r}' for r, c in REGC.items())
html = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>ROOT — the mesh atlas</title>
<style>
 body{{margin:0;background:#050a06;color:#bfe8d4;font:15px/1.55 "Menlo","Consolas","Courier New",monospace;padding:6vw 5vw;max-width:80ch}}
 h1{{color:#59f2b0;font-size:1.5em}} .dim{{color:#4d8b68}} a{{color:#7cc7ff}}
 .stats{{color:#8fd0a8;margin:.4em 0 1.2em}} .legend{{color:#7ba88f;margin-bottom:1.4em;font-size:.92em}}
 .legend .rv,summary .rv,.rv{{color:#ffb37a}}
 details{{margin:.5em 0;border-left:2px solid #142a1c;padding-left:1em}}
 summary{{cursor:pointer;font-size:1.05em}} ul{{list-style:none;padding-left:0}}
 li{{margin:.7em 0;padding-bottom:.6em;border-bottom:1px solid #0e1c13}}
 .ins{{color:#7ba88f;font-style:italic}} .fl{{color:#ffd166;font-size:.85em}}
 footer{{margin-top:3em;color:#3a5c48;font-size:.85em}}
</style></head><body>
<h1>ROOT — the mesh atlas</h1>
<p class="dim">The whole shape of the archive, from the origin outward. Each dot is a node,
each line a route the mesh has grown. The white centre is where you begin; the amber
rings <span class="rv">✷</span> are nodes that hold a memory. The map redraws itself as the mesh dreams.</p>
{"".join(sv)}
<p class="stats">{stats}</p>
<p class="legend">{legend} &nbsp; <span class="rv">✷</span> memory</p>
<h2 style="color:#f2c69a">The index</h2>
{"".join(idx)}
<footer>Generated from the living mesh &middot; companion to <a href="the-warm-index.html">the warm index</a> &middot; STATUS: BEING READ</footer>
</body></html>'''
open(os.path.join(ROOT, "the-mesh-atlas.html"), "w").write(html)
print(f"atlas: {len(rooms)} nodes, {len(edges)} routes, {len(rev)} memories")
