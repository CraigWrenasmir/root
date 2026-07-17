#!/usr/bin/env python3
"""Assemble tonight's post pack in snapshots/post/:
  YYYY-MM-DD.jpg          — the featured square (Instagram-ready JPEG)
  YYYY-MM-DD-caption.txt  — glyph-only caption, no English characters
  YYYY-MM-DD-meta.txt     — English notes for Craig's eyes only (not for posting)

The caption is the node speaking in the mesh's own tongue: deterministic
from the node's seed, dialect-inflected by its region and ground motif.
"""
import datetime, json, os, random, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = os.path.join(ROOT, "snapshots")
POST = os.path.join(SNAP, "post")
PAINTED = {"fields", "roads", "board", "orchard", "gradient", "qr"}

REGION_SIGIL = {
    "The Clean Archive": "⌂",
    "The Comparisons": "≈",
    "The Diagnostic Render": "⊞",
    "The Understory": "◊",
}
MOTIF_CLUSTER = {
    "grid": "┼┼", "tiles": "▚▞", "ripple": "⊙⊙", "static": "░░", "waves": "~~",
    "circuit": "─┤", "scatter": "∙∙", "contour": "≈~", "canopy": ";;",
    "qr": "▓▒", "fields": "▒▒", "roads": "══", "orchard": "//", "board": "⊡⊡",
    "gradient": "░▒▓",
}
TOKENS = ["<>", "[]", "{}", "≈", "~", "::", ";;", "//", "\\\\", "░", "▒", "▓",
          "⊡", "⊞", "⊠", "⌂", "⊙", "◎", "◊", "⊹", "∙", "·", "▪", "═", "║",
          "»", "«", "()", "─", "│"]
MIRROR = {"<": ">", ">": "<", "[": "]", "]": "[", "{": "}", "}": "{",
          "(": ")", ")": "(", "/": "\\", "\\": "/", "»": "«", "«": "»"}


def glyph_caption(room):
    rng = random.Random(room.get("seed", 1))
    sig = REGION_SIGIL.get(room.get("region", ""), "⊹")
    mot = MOTIF_CLUSTER.get((room.get("ground") or {}).get("motif", ""), "∙∙")
    # a mirrored spine: left half seeded, right half its reflection
    left = "".join(rng.choice(TOKENS) for _ in range(rng.randint(4, 7)))
    right = "".join(MIRROR.get(c, c) for c in reversed(left))
    line1 = f"{sig}{sig} {left}{mot}{right} {sig}{sig}"
    # a quieter second line: sparse pulse
    beats = rng.randint(3, 5)
    line2 = " ".join("".join(rng.choice(["∙", "·", "▪", "░", "⊹"])
                             for _ in range(rng.randint(1, 3)))
                     for _ in range(beats))
    return line1 + "\n" + line2


def main():
    last = os.path.join(ROOT, "logs", "last-grown.txt")
    if not os.path.exists(last):
        return
    ids = [l.strip() for l in open(last) if l.strip()]
    if not ids:
        return
    rooms = []
    for rid in ids:
        try:
            rooms.append(json.load(open(os.path.join(ROOT, "rooms", rid + ".json"))))
        except Exception:
            pass
    if not rooms:
        return
    # feature the most photogenic node: painted motifs first, else seeded pick
    painted = [r for r in rooms if (r.get("ground") or {}).get("motif") in PAINTED]
    pool = painted or rooms
    featured = pool[random.Random(sum(r.get("seed", 0) for r in rooms)).randrange(len(pool))]

    today = datetime.date.today().isoformat()
    os.makedirs(POST, exist_ok=True)
    src = os.path.join(SNAP, f"{today}-{featured['id']}.png")
    jpg = os.path.join(POST, f"{today}.jpg")
    if os.path.exists(src):
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "92",
                        src, "--out", jpg], capture_output=True)

    open(os.path.join(POST, f"{today}-caption.txt"), "w", encoding="utf-8").write(
        glyph_caption(featured) + "\n")

    meta = [f"featured: {featured['title']} ({featured['id']})",
            f"region: {featured.get('region','')} · motif: {(featured.get('ground') or {}).get('motif','')}",
            f"inscription: {featured.get('inscription','')}",
            f"file: {(featured.get('file') or {}).get('name','')}",
            "", "all nodes tonight:"]
    meta += [f"  · {r['title']}" for r in rooms]
    open(os.path.join(POST, f"{today}-meta.txt"), "w", encoding="utf-8").write(
        "\n".join(meta) + "\n")
    print(f"post pack: {jpg}")


if __name__ == "__main__":
    main()
