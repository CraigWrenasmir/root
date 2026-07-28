#!/usr/bin/env python3
"""Write rooms-bundle.json — the whole mesh (manifest + every room) in one file.
The iOS app fetches this single file to catch up, instead of one request per
room. Regenerated nightly from grow.sh, so it always mirrors the live mesh."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RD = os.path.join(ROOT, "rooms")
manifest = json.load(open(os.path.join(RD, "manifest.json")))
rooms = {}
for fn in os.listdir(RD):
    if fn == "manifest.json" or not fn.endswith(".json"):
        continue
    rooms[fn[:-5]] = json.load(open(os.path.join(RD, fn)))
bundle = {"manifest": manifest, "rooms": rooms}
out = os.path.join(ROOT, "rooms-bundle.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(bundle, f, ensure_ascii=False, separators=(",", ":"))
print(f"rooms-bundle.json: {len(rooms)} rooms, {os.path.getsize(out)//1024} KB")
