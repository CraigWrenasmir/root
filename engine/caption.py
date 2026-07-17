#!/usr/bin/env python3
"""Write tonight's feed caption: snapshots/YYYY-MM-DD-caption.txt
covering the nodes listed in logs/last-grown.txt."""
import datetime, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
last = os.path.join(ROOT, "logs", "last-grown.txt")
if not os.path.exists(last):
    raise SystemExit(0)
ids = [l.strip() for l in open(last) if l.strip()]
if not ids:
    raise SystemExit(0)

manifest = json.load(open(os.path.join(ROOT, "rooms", "manifest.json")))
today = datetime.date.today().isoformat()
lines = [f"ROOT · night {manifest.get('nights','?')} · {today}",
         f"the mesh grew {len(ids)} node{'s' if len(ids)!=1 else ''} overnight.", ""]
for rid in ids:
    try:
        r = json.load(open(os.path.join(ROOT, "rooms", rid + ".json")))
    except Exception:
        continue
    lines.append(f"▓ {r.get('title', rid)}  ({r.get('region','')})")
    if r.get("inscription"):
        lines.append(f'  "{r["inscription"]}"')
    if r.get("file", {}).get("name"):
        lines.append(f"  file: {r['file']['name']}")
    lines.append("")
lines += ["a text-mode archive that grows itself every night, at 300bps.",
          "STATUS: BEING READ",
          "",
          "#asciiart #ansiart #textmode #generativeart #interactivefiction "
          "#solarpunk #australianliterature #rootgame"]

os.makedirs(os.path.join(ROOT, "snapshots"), exist_ok=True)
out = os.path.join(ROOT, "snapshots", f"{today}-caption.txt")
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("caption:", out)
