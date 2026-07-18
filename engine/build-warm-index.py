#!/usr/bin/env python3
"""Regenerate the-warm-index.html — the hidden guide to the reverie scenes.
Run nightly from grow.sh so newly-dreamt memories appear automatically."""
import json, os
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RD = os.path.join(ROOT, "rooms")
rooms = {}
for fn in os.listdir(RD):
    if fn == "manifest.json": continue
    rooms[fn[:-5]] = json.load(open(os.path.join(RD, fn)))
man = json.load(open(os.path.join(RD, "manifest.json"))); entry = man["entry"]

adj = {}
for rid, r in rooms.items():
    adj[rid] = {}
    for ex in r.get("exits", []):
        to = ex.get("to", "")
        if isinstance(to, str) and not to.startswith("NEW:") and to in rooms:
            adj[rid][ex["dir"]] = to

def path(target):
    if target == entry: return []
    q = deque([(entry, [])]); seen = {entry}
    while q:
        cur, p = q.popleft()
        for d, nxt in adj.get(cur, {}).items():
            if nxt in seen: continue
            np = p + [d]
            if nxt == target: return np
            seen.add(nxt); q.append((nxt, np))
    return None

DIR = {"n": "N", "s": "S", "e": "E", "w": "W"}
WORD = {"N": "north", "S": "south", "E": "east", "W": "west"}
rev = [rid for rid, r in rooms.items()
       if r.get("reverie") and any(f.get("verb") == "reverie" for f in r.get("features", []))]
data = []
for rid in rev:
    r = rooms[rid]; p = path(rid)
    trig = next((f["name"] for f in r["features"] if f.get("verb") == "reverie"), "")
    revd = r["reverie"]
    data.append({"title": r.get("title"), "region": r.get("region"),
                 "path": [DIR[d] for d in p] if p else "HERE",
                 "trigger": trig, "revtitle": revd.get("title"),
                 "first_narr": (revd.get("narr", [""]) or [""])[0]})
data.sort(key=lambda d: (d["path"] == "HERE" and 0) or len(d["path"]) if isinstance(d["path"], list) else -1)

def moves(p):
    if p == "HERE" or p == []: return '<span class="here">you begin here</span>'
    return " &nbsp;→&nbsp; ".join(f"<b>{d}</b>" for d in p)
def prose(p):
    if p == "HERE" or p == []: return "This is the very first node — you are already here when you connect."
    return "From the Daisy Field, leave by the " + ", then ".join(WORD[d] for d in p) + " route" + ("s" if len(p) > 1 else "") + "."

cards = []
for d in data:
    cards.append(f'''  <div class="scene">
    <div class="path">{moves(d['path'])}</div>
    <h2>{d['revtitle'] or 'a memory'}</h2>
    <p class="loc">in <b>{d['title']}</b> · {d['region']}</p>
    <p class="how">{prose(d['path'])} Look for the warm <span class="mark">✷</span> and walk onto it — the message row will read <i>"something of hers is filed here."</i> Query <span class="trig">{d['trigger']}</span>.</p>
    <p class="teaser">“{d['first_narr']}…”</p>
  </div>''')
html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ROOT — the warm index</title>
<style>
  body{{margin:0;background:#050a06;color:#bfe8d4;font:16px/1.6 "Menlo","Consolas","Courier New",monospace;padding:8vw 6vw;max-width:74ch}}
  h1{{color:#59f2b0;font-size:1.5em}} h2{{color:#f2c69a;font-size:1.05em;margin:.2em 0}}
  a{{color:#7cc7ff}} .dim{{color:#4d8b68}} i{{color:#8fd0a8}}
  .intro{{border-left:2px solid #1d4d33;padding-left:1em;color:#8fd0a8}}
  .scene{{margin:2.4em 0;padding-bottom:1.6em;border-bottom:1px solid #142a1c}}
  .path{{color:#59f2b0;letter-spacing:.15em;font-size:1.1em;margin-bottom:.3em}}
  .path b{{color:#d8fff0}} .here{{color:#f2c69a}}
  .loc{{color:#7ba88f;margin:.1em 0 .6em}}
  .how{{color:#bfe8d4}} .mark{{color:#ffb37a}}
  .trig{{color:#ffd166}} .teaser{{color:#e8b98a;font-style:italic;margin-top:.6em}}
  footer{{margin-top:3em;color:#3a5c48;font-size:.85em}}
</style></head><body>
<h1>ROOT — the warm index</h1>
<p class="intro">The mesh is cold. But here and there, if you query the right thing, the
screen turns warm and a memory surfaces — a side-on scene from a life, a beat of
narrative, then the archive takes you back. These are the ones that have grown so
far. More appear as the mesh dreams. Movements below are d-pad directions from the
first node, the Daisy Field, where you always begin.</p>
{"".join(cards)}
<footer>Reveries are rare — roughly one node in five, and only where something private is kept.
The <span style="color:#ffb37a">✷</span> always marks them. New scenes are dreamt into the mesh
most nights, so this index grows. Companion to <a href="the-mesh-atlas.html">the mesh atlas</a>. — ROOT · STATUS: BEING READ</footer>
</body></html>'''
open(os.path.join(ROOT, "the-warm-index.html"), "w").write(html)
print(f"warm index: {len(rev)} scenes")
