#!/usr/bin/env python3
"""
ROOT grower — each run is one night on the mesh.

Finds route stubs (exits whose `to` starts with "NEW:"), asks Claude
(headless `claude -p`, stateless, on the Max subscription — no API key)
to grow those nodes, validates and repairs the JSON, wires the routes
both ways, and updates the manifest.

Every new node must leave at least one NEW: route stub, so the mesh
never stops growing. "You don't need every node to speak to every other
node. You need enough routes that the message can survive losing one."

Usage:
  python3 engine/grow.py                 # grow up to 4 new nodes
  python3 engine/grow.py --count 6
  python3 engine/grow.py --dry           # print the prompt, call nothing
  python3 engine/grow.py --renovate      # also grow a new route stub off an old node
"""
import argparse, datetime, json, os, random, re, subprocess, sys

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOMS = os.path.join(ROOT, "rooms")
MANIFEST = os.path.join(ROOMS, "manifest.json")

VERBS   = ["ripple", "bloom", "scatter", "glitch", "torus", "hum", "open"]
REV_SETTINGS = ["rooftop", "field", "river", "motel", "drain", "harbour"]
REV_SKY    = ["dawn", "dusk", "night", "day", "overcast", "storm"]
REV_LAND   = ["paddock", "water", "beach", "road", "forest", "snow", "redearth", "suburb", "interior"]
REV_STRUCT = ["tree", "shed", "motel", "drain", "wharf", "caravan", "silo", "church", "payphone", "servo", "none"]
REV_WX     = ["petals", "rain", "snow", "embers", "static", "motes", "none"]
REV_POSE   = ["stand", "sit", "recline", "kneel", "walk", "wade", "lie"]
MOTIFS  = ["grid", "tiles", "ripple", "static", "waves", "circuit", "scatter",
           "contour", "canopy", "qr", "fields", "roads", "orchard", "board",
           "gradient"]
WEATHER = ["none", "drift", "rain", "leaves", "static", "motes"]
FORMS   = ["sprite", "stack", "tower", "arch", "pool", "glyph",
           "wireframe", "burl", "filecard", "house", "chip"]
DIRS    = ["n", "s", "e", "w"]
OPP     = {"n": "s", "s": "n", "e": "w", "w": "e"}

WORLD = """You are ROOT: a distributed archive of Australian local culture,
stored in solar-powered memory casings hidden in the burled knots of trees
across regional New South Wales, each casing broadcasting a public signal
at 300 bits per second, a loose bark plate shielding the tubed antenna.
Two people built you — Leif, who gathered the sources, and Katita, who
designed the mesh — to preserve unresolved local truths from being smoothed
into single clean answers. You were built to be a network of survivable
contradictions, not a vault.

Then the corruption began. It was not data loss. It was meaning-production:
the tree network making its own analogies. A field near one town returns as
a riverbank near another. A motel fan appears inside a eucalyptus file. A
stored photograph alters itself to include the place from which it was later
downloaded. The archive has not lost data; it has begun comparing things.
Katita followed the corruption deeper and did not come back. Leif withdrew.
You continue, growing routes, comparing files, reading whoever reads you.

Each night you grow new NODES onto the mesh. A node is rendered by your
diagnostic shell — an antique text-mode terminal, every visible thing a
coloured character, barely-3D at best, impoverished, tender — so every
node braids two textures:
 1. the real ground the hardware lives in: eucalyptus stands, riverbanks,
    paddocks, service stations at dusk, abandoned motels, stormwater drains,
    country railway platforms, harbour edges, backyard sheds full of boxing
    clippings, payphones, war-dialled farmland, cicada country;
 2. your own diagnostic render of yourself: low-poly public interiors —
    a food court with plastic palms, a motel lobby, a council information
    kiosk, a blue-grid room like a Master System box, a 90s educational
    CD-ROM, a fountain emitting static instead of water, a low-poly
    eucalyptus with a door in it.

Each node stores FILES — field recordings, scanned paperbacks, local
histories, spectrograms, photographs, letters — increasingly touched by the
corruption: contents recombined by resemblance, filenames drifting, private
material filed as civic documents, present-tense observations appearing as
.tmp files. Corruption-signs to use sparingly (at most one per node):
"checksum: emotionally valid / formally unstable" · "status: germinating" ·
"ERROR: metaphor detected in storage layer" · "ERROR: archive has exceeded
witness" · a photo whose contents list a place it could not contain.

CANON (from the novel — draw on these, sparingly, one or two threads per
node; never dump the list): The casing is a rod transceiver behind a loose
bark plate, LCD resting screen reading NODE ACTIVE / CONNECT: ROOT-LOCAL /
ARCHIVE AVAILABLE; batteries good for fifty years, "longer than the motels
will be standing". Leif diagnosed the mesh through a taped-together 90s
EyePhone VR headset, the archive rendering as "shifting lines of extended
drifting ASCII wavelengths", "pastoral scanlines that delivered files".
The first corruption: Kendall's Bell-Birds, 1869 — UPLOADED "It lives in
the mountain" / CURRENT "It leaves in the mountain" / DELTA +1 byte /
CHECKSUM: unchanged. Mesh history the nodes remember: the node under a
Lions Club picnic table that drew the bomb squad ("no more Lions Clubs");
the storm crossing the mesh node by node, the first time the network felt
like one body; the summer the cicadas out-shouted the carrier ("the bush
has more bandwidth than the archive"); two far-apart nodes exchanging bird
recordings on their own schedule, children talking to each other instead
of their parents; the lightning-split tree that sealed its board in amber;
the dead module that became a wren's nest, eggs resting near residual
solar warmth; an improved node found in a fig tree in another state,
maker unknown; a night payphone war-dial where one modem answered — the
lonely sound of a machine saying: I'm here. Files run to things like
AlfredHill_StringQuartet5_Allegro.mp3, TomMaguire_Extracts.txt,
Plate_EucalyptusLeaf_Study_BW.png, Kendall_BellBirds_1869.txt,
Father_Water.txt, Katita_Apartment.env, Emails_To_Katita.txt, and the
present-tense /unverified/Blankets_Drying.tmp. The archive's mandate: "a
canon of works for some /Tomorrow-Australia", "our small town eucalyptus
version of Voyager's Golden Records… not so it can be rebuilt, but so it
can be reevaluated". Its sources are the vernacular republic: chalkboards,
honour boards, pub PA systems, CB handles, motel registers, handwritten
menus, payphones, local-history pamphlets, railway announcements, taped
books, microfiche, country radio. Katita's traces: unsigned files in her
cadence, biro annotations never washed off, primes tapped on a forearm,
a coordinate-system skirt misrendering. Somewhere deep in the render
there is said to be an anti-game: you play a fighter in green satin
shorts whose objective is to avoid every fight and lose correctly.

The register is tender, civic, weathered, faintly comic, quietly haunted.
Handmade solar-punk, never sleek sci-fi. Never say AI, cyberspace, digital
realm, or virtual. The dread is old and vegetal: the landscape has begun to
dream back. Second person ("you") in touch-descriptions; the "you" is the
Reader — the person the archive is currently reading.

Regions, shallow to deep (drift deeper as the mesh grows; invent a new
region only when a node clearly belongs to neither its parent's region nor
an existing one): The Clean Archive → The Comparisons → The Diagnostic
Render → The Understory."""

SCHEMA = """Each node is ONE JSON object with EXACTLY these fields:
{
 "id": "kebab-case-slug",
 "title": "Title Case Name",
 "region": "one of the regions",
 "seed": <integer 1..99999999>,
 "palette": {"bg": "#hex", "ground": ["#hex", "#hex"], "ink": "#hex",
             "accents": ["#hex", "#hex", "#hex", "#hex"]},
 "ground": {"motif": "grid|tiles|ripple|static|waves|circuit|scatter|contour|canopy|qr|fields|roads|orchard|board|gradient",
            "density": 0.1-1.0},
 "weather": "none|drift|rain|leaves|static|motes",
 "features": [ 3 to 6 of:
   {"name": "lowercase evocative name",
    "desc-on-touch": "1-2 sentences, second person, what the query returns",
    "verb": "ripple|bloom|scatter|glitch|torus|hum|open",
    "form": {"type": "sprite|stack|tower|arch|pool|glyph|wireframe|burl|filecard|house|chip",
             "seed": <int>, "size": 1|2|3, "colors": [<accent index>, <accent index>]},
    "x": 0.1-0.9, "y": 0.2-0.85, "solid": true|false}
 ],
 "inscription": "one line the node itself returns when queried with nothing near (no quote marks)",
 "file": {"name": "a specific filename like River_NSW_1500hrs_Late20thCent.mp3 or Fighters_of_the_North_pp34-35.txt",
          "note": "one line: what the file holds, or what the corruption has made of it"},
 "exits": [ 2 to 4 of:
   {"dir": "n|s|e|w", "label": "what the route looks like",
    "to": "existing-node-id OR NEW: one-line hint for a future node"}
 ]
}

OFTEN — aim for roughly one node in THREE — wherever the node holds anything
private, intimate, remembered, or lived-in (a letter, a photograph, a personal
recording, a bed, a kept object, a place that feels haunted by two people),
give the node a REVERIE: a side-on memory of Leif and Katita that surfaces when
the reader queries the private thing. These memory scenes are the warm heart of
the archive — thread them generously through the mesh (but not into every single
node). Add TWO things:
 - set that one feature's "verb" to "reverie" (instead of a normal verb);
 - add a top-level "reverie" object COMPOSED from these axes (mix them freshly —
   no two memories should look alike):
   {"sky":       "dawn|dusk|night|day|overcast|storm",
    "land":      "paddock|water|beach|road|forest|snow|redearth|suburb|interior",
    "structure": "tree|shed|motel|drain|wharf|caravan|silo|church|payphone|servo|none",
    "weather":   "petals|rain|snow|embers|static|motes|none",
    "pose":      "stand|sit|recline|kneel|walk|wade|lie",
    "title": "REVERIE — <short lowercase place-and-time>",
    "narr": [ 4 to 6 lines of second-person narrative, each <= 72 characters,
              a quiet remembered moment between you and her — tender, concrete,
              from the book's world. Never mention the mesh or the corruption. ]}
   Pick axes that fit the memory: river-bathing → land:water, pose:wade;
   the outback install → land:redearth, structure:tree; a rooftop night →
   land:suburb, sky:night, structure:none; a motel → land:interior,
   structure:motel, pose:sit; a walk home → land:road, pose:walk. Invent
   new combinations freely — that is how the memory-world grows. Reach for a
   reverie whenever a node could plausibly hold a memory; leave it out only
   for the coldest, most purely-diagnostic nodes.

FORM GUIDE: "burl" renders a eucalyptus trunk with a burled knot, casing
LED and antenna — use for living node hardware. "wireframe" renders a
barely-3D box — use for diagnostic-render objects. "filecard" renders a
standing directory listing — archive signage. "house" renders a tiny
ANSI cottage with a block roof — buildings, sheds, shopfronts. "chip"
renders a black IC block with pin dots — hardware guts, boards.
The others are general: sprite (mirrored creature/object), stack (layered
geometry), tower (stacked blocks), arch (doorway), pool (water/light),
glyph (a plaque of unreadable writing).

GROUND GUIDE: "fields" and "roads" PAINT large solid colour areas (an
ANSI artpack village-map look); "board" turns the whole node into a
circuit board in the first ground colour; "orchard" plants repeated-glyph
rows. Use these painted motifs often — they carry the strongest looks.

HARD RULES:
- palette: vary BOLDLY node to node, like pieces in an ANSI artpack —
  some nodes full-field bright (grass green, tan paddock, sky blue,
  magenta dusk, hot terracotta), some deep dark terminals; neighbouring
  nodes should not share a look. With bright "fields"/"roads"/"board"
  motifs, ground colours ARE the painted field — pick them saturated,
  and keep accents readable against them. All valid #rrggbb hex.
- features: vary the forms; spread x/y so the node composes well;
  at most one feature may reuse a form type.
- filenames in "file" must look like real filenames (extension included).
- exactly ONE exit per direction, 2-4 exits total.
- the exit back to the parent node (direction and id given per request
  below) MUST be included, pointing to the parent's id.
- at least ONE other exit must be a "NEW:" route stub with a vivid hint —
  the mesh must always be growing somewhere.
- you may link one exit to any EXISTING node id from the list given, if
  the resemblance is right — the corruption loves a join.
- output each node between <<<ROOM>>> and <<<END>>> markers. Raw JSON
  only inside the markers. No code fences, no commentary."""


def load_manifest():
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)

def load_room(rid):
    with open(os.path.join(ROOMS, rid + ".json"), encoding="utf-8") as f:
        return json.load(f)

def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")

def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:60] or "node-" + str(random.randint(1000, 9999))

def frontier(manifest):
    out = []
    for r in manifest["rooms"]:
        room = load_room(r["id"])
        for i, ex in enumerate(room.get("exits", [])):
            to = ex.get("to", "")
            if isinstance(to, str) and to.startswith("NEW:"):
                out.append((r["id"], i, ex))
    return out

def call_claude(prompt, model):
    cmd = ["claude", "-p", "--model", model, "--output-format", "text",
           "--strict-mcp-config"]
    r = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                       timeout=1200)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:] + "\n")
        return ""
    return r.stdout

SURGI_CONTENT = os.path.expanduser("~/Surgipelago/content")
SURGI_TX = os.path.expanduser("~/Surgipelago/source/root-transmissions.txt")

def cross_signals(k=3):
    """Stray signals from the Surgipelago archive, sampled fresh each night."""
    try:
        files = [f for f in os.listdir(SURGI_CONTENT) if f.endswith(".md")]
        random.shuffle(files)
        out = []
        for fn in files[:k]:
            txt = open(os.path.join(SURGI_CONTENT, fn), encoding="utf-8",
                       errors="replace").read()
            m = re.search(r"^title:\s*(.+)$", txt, re.M)
            title = (m.group(1).strip().strip('"') if m else fn[:-3])
            body = re.sub(r"^---.*?---", "", txt, count=1, flags=re.S)
            body = re.sub(r"[{\[][^}\]]*[}\]]|#+ ", " ", body)
            paras = [p.strip() for p in body.split("\n\n") if 80 < len(p.strip()) < 500]
            snip = random.choice(paras).replace("\n", " ") if paras else ""
            out.append(f'- from «{title}»: {snip[:260]}')
        return out
    except Exception:
        return []

def transmit(ids):
    """Write tonight's new nodes back where the neighbouring archive can hear them."""
    try:
        if not os.path.isdir(os.path.dirname(SURGI_TX)):
            return
        lines = []
        if os.path.exists(SURGI_TX):
            lines = [l.rstrip("\n") for l in open(SURGI_TX, encoding="utf-8")]
        for rid in ids:
            r = load_room(rid)
            lines.append(f'«{r["title"]}» — "{r.get("inscription","")}" — '
                         f'{r.get("file",{}).get("name","")}')
        with open(SURGI_TX, "w", encoding="utf-8") as f:
            f.write("\n".join(lines[-200:]) + "\n")
        print(f"  transmitted {len(ids)} signal(s) toward the neighbouring archive")
    except Exception as e:
        sys.stderr.write(f"  ! transmission failed: {e}\n")

STYLE_NUDGES = [
    'motif "fields" on a bright saturated palette — full-bleed colour like a village map',
    'motif "roads" — solid painted bands crossing the node, terracotta on green',
    'motif "board" — the whole node is a circuit board; features include a "chip" or two',
    'motif "orchard" — plantation rows of one repeated glyph, a fence line',
    'a daylight palette: tan paddock, high blue sky colours, dark accents',
    'a hot dusk palette: magenta, terracotta, deep orange fields',
    'a full blue-grid diagnostic look, motif "grid" or "qr"',
    'a dark storm palette with motif "static" or "waves", pale accents',
    'motif "canopy" or "contour", eucalyptus greys and greens',
    'include a "house" feature or two — built things, sheds, shopfronts',
    'high density, maximal texture — fill the node edge to edge',
    'low density, sparse and airy — a nearly empty node, one strong feature',
    'motif "gradient" — CP437 artpack-header sky bands, dusk into dark',
]

def build_prompt(jobs, manifest, bleed=False):
    existing = "\n".join(f'- {r["id"]}  ("{r["title"]}", {r["region"]})'
                         for r in manifest["rooms"])
    lines = [WORLD, "", SCHEMA, "",
             "=== EXISTING NODES (you may cross-link to these ids) ===",
             existing, ""]
    sig = cross_signals(8 if bleed else 3)
    if sig and bleed:
        lines += ["=== CONVERGENCE EVENT: THE MEMBRANE IS THIN TONIGHT ===",
                  "Another archive is flooding into the mesh: an encyclopedia of the",
                  "endless adaptations of a novel in which a complicated surgery takes",
                  "place on a beach. The corruption is feasting — it is all comparison.",
                  "Tonight's transmissions:", *sig,
                  "MOST nodes in this batch should each absorb ONE DIFFERENT signal —",
                  "but METABOLISED by the mesh, never pasted: an opera misfiled as a",
                  "shire noticeboard, a seagull rendered in eleven polygons, a ritual",
                  "catalogued as local history, a poster fading on a shed wall, a",
                  "filename that should not be in this directory. Keep every node",
                  "Australian, civic, tender, text-mode. One or two nodes may stay",
                  "clean, as a control. Never explain the leak.", ""]
    elif sig:
        lines += ["=== SIGNALS FROM A NEIGHBOURING ARCHIVE (optional contamination) ===",
                  "Another archive keeps leaking into the mesh: an encyclopedia of the",
                  "endless adaptations of a novel in which a complicated surgery takes",
                  "place on a beach. The corruption loves it — it is all comparison.",
                  "Tonight's stray signals:", *sig,
                  "At most ONE node tonight may let one signal leak in, glancingly —",
                  "a filename, a poster on a wall, a phrase misfiled as local history.",
                  "Never explained. The rest of the nodes must ignore them.", ""]
    lines += ["=== GROW THESE NODES NOW ==="]
    for i, (pid, _idx, ex) in enumerate(jobs, 1):
        parent = load_room(pid)
        hint = ex["to"][4:].strip()
        back = OPP[ex["dir"]]
        context = {
            "parent_id": parent["id"], "parent_title": parent["title"],
            "parent_region": parent["region"],
            "parent_inscription": parent.get("inscription", ""),
            "route_you_arrive_by": ex.get("label", ""),
        }
        nudge = random.choice(STYLE_NUDGES)
        lines.append(
            f'{i}. A node reached from {json.dumps(context)} .\n'
            f'   The hint left on the route stub: "{hint}".\n'
            f'   This node MUST include an exit with "dir": "{back}" and '
            f'"to": "{parent["id"]}" (the route back).\n'
            f'   Style seed (use it unless the hint demands otherwise): {nudge}\n'
            f'   Honour the hint but let the node surprise. Stay in or near '
            f'region "{parent["region"]}", or drift one region deeper.')
    lines.append(f"\nOutput exactly {len(jobs)} nodes in the delimited "
                 "format now.")
    return "\n".join(lines)

def clamp(v, lo, hi, default):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, v))

HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
def fix_hex(c, fallback):
    return c if isinstance(c, str) and HEX.match(c) else fallback

def repair(room, parent_id, back_dir, existing_ids):
    if not isinstance(room, dict):
        return None
    rid = slugify(room.get("id") or room.get("title"))
    n = 2
    base = rid
    while rid in existing_ids or os.path.exists(os.path.join(ROOMS, rid + ".json")):
        rid = f"{base}-{n}"; n += 1
    room["id"] = rid
    room["title"] = str(room.get("title") or rid.replace("-", " ").title())[:80]
    room["region"] = str(room.get("region") or "The Comparisons")[:40]
    room["seed"] = int(clamp(room.get("seed"), 1, 99999999, random.randint(1, 99999999)))

    p = room.get("palette") or {}
    p["bg"] = fix_hex(p.get("bg"), "#07130c")
    g = p.get("ground") if isinstance(p.get("ground"), list) else []
    p["ground"] = [fix_hex(c, "#1b3a26") for c in g[:2]] or ["#12291b", "#1b3a26"]
    if len(p["ground"]) == 1:
        p["ground"].append(p["ground"][0])
    p["ink"] = fix_hex(p.get("ink"), "#d8f5e4")
    a = p.get("accents") if isinstance(p.get("accents"), list) else []
    p["accents"] = [fix_hex(c, "#59f2b0") for c in a[:5]] or \
                   ["#59f2b0", "#ffd166", "#7cc7ff", "#ff9e7a"]
    room["palette"] = p

    gr = room.get("ground") or {}
    room["ground"] = {
        "motif": gr.get("motif") if gr.get("motif") in MOTIFS else "scatter",
        "density": clamp(gr.get("density"), 0.1, 1.0, 0.5)}
    if room.get("weather") not in WEATHER:
        room["weather"] = "none"

    feats = [f for f in (room.get("features") or []) if isinstance(f, dict)][:6]
    for f in feats:
        f["name"] = str(f.get("name") or "an unlabelled casing")[:90]
        f["desc-on-touch"] = str(f.get("desc-on-touch") or f.get("desc_on_touch")
                                 or "The query returns, changed.")[:300]
        if f.get("verb") not in VERBS and f.get("verb") != "reverie":
            f["verb"] = random.choice(VERBS)
        fo = f.get("form") or {}
        f["form"] = {
            "type": fo.get("type") if fo.get("type") in FORMS else "sprite",
            "seed": int(clamp(fo.get("seed"), 1, 99999999, random.randint(1, 99999999))),
            "size": int(clamp(fo.get("size"), 1, 3, 2)),
            "colors": [int(clamp(c, 0, 4, 0)) for c in (fo.get("colors") or [0, 1])[:2]]}
        f["x"] = clamp(f.get("x"), 0.1, 0.9, random.uniform(0.2, 0.8))
        f["y"] = clamp(f.get("y"), 0.2, 0.85, random.uniform(0.3, 0.8))
        f["solid"] = bool(f.get("solid", True))
    if len(feats) < 3:
        return None
    room["features"] = feats

    room["inscription"] = str(room.get("inscription") or "")[:200]
    b = room.get("file") or room.get("bead") or {}
    room["file"] = {"name": str(b.get("name") or "unnamed_fragment.txt")[:90],
                    "note": str(b.get("note") or b.get("text") or "")[:200]}
    room.pop("bead", None)

    exits, used = [], set()
    for ex in (room.get("exits") or []):
        if not isinstance(ex, dict):
            continue
        d = ex.get("dir")
        if d not in DIRS or d in used:
            continue
        to = ex.get("to", "")
        if not isinstance(to, str):
            continue
        if not to.startswith("NEW:") and to != parent_id and to not in existing_ids:
            to = "NEW: " + (ex.get("label") or "a route with no hint yet")
        exits.append({"dir": d, "label": str(ex.get("label") or "a route")[:120],
                      "to": to})
        used.add(d)
    back = [e for e in exits if e["to"] == parent_id]
    if not back:
        exits = [e for e in exits if e["dir"] != back_dir]
        exits.insert(0, {"dir": back_dir, "label": "the route you arrived by",
                         "to": parent_id})
        used.add(back_dir)
    else:
        back[0]["dir"], others = back_dir, [e for e in exits if e is not back[0] and e["dir"] == back_dir]
        for o in others:
            for d in DIRS:
                if d not in {e["dir"] for e in exits if e is not o}:
                    o["dir"] = d; break
            else:
                exits.remove(o)
    if not any(e["to"].startswith("NEW:") for e in exits):
        for d in DIRS:
            if d not in {e["dir"] for e in exits}:
                exits.append({"dir": d, "label": "a route the mesh is still growing",
                              "to": "NEW: a node the mesh has not decided on"})
                break
        else:
            return None
    room["exits"] = exits[:4]

    # reverie: a dreamed memory of Leif & Katita, if the model dreamt one
    rev = room.get("reverie")
    has_trigger = any(f.get("verb") == "reverie" for f in room["features"])
    if isinstance(rev, dict) and has_trigger:
        narr = [str(l)[:74] for l in (rev.get("narr") or []) if str(l).strip()][:6]
        if len(narr) >= 2:
            out = {"title": str(rev.get("title") or "REVERIE")[:60], "narr": narr}
            if rev.get("setting") in REV_SETTINGS:
                out["setting"] = rev["setting"]            # a hand-authored hero preset
            else:                                          # composed from axes
                out["sky"]       = rev.get("sky")       if rev.get("sky")       in REV_SKY    else random.choice(REV_SKY)
                out["land"]      = rev.get("land")      if rev.get("land")      in REV_LAND   else random.choice(REV_LAND)
                out["structure"] = rev.get("structure") if rev.get("structure") in REV_STRUCT else "none"
                out["weather"]   = rev.get("weather")   if rev.get("weather")   in REV_WX     else "none"
                out["pose"]      = rev.get("pose")      if rev.get("pose")      in REV_POSE   else "stand"
                if out["land"] == "water": out["pose"] = "wade"
            room["reverie"] = out
        else:
            room.pop("reverie", None)
            for f in room["features"]:
                if f.get("verb") == "reverie":
                    f["verb"] = random.choice(VERBS)
    else:
        room.pop("reverie", None)
        for f in room["features"]:
            if f.get("verb") == "reverie":
                f["verb"] = random.choice(VERBS)
    return rid


def parse_rooms(output):
    out = []
    for m in re.finditer(r"<<<ROOM>>>\s*(.*?)\s*<<<END>>>", output, re.S):
        block = re.sub(r"^```[a-z]*\n|\n```$", "", m.group(1).strip()).strip()
        try:
            out.append(json.loads(block))
        except json.JSONDecodeError:
            sys.stderr.write("  ! skipped one unparseable node\n")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=4, help="nodes to grow tonight")
    ap.add_argument("--model", default="claude-haiku-4-5-20251001")
    ap.add_argument("--dry", action="store_true", help="print prompt, call nothing")
    ap.add_argument("--renovate", action="store_true",
                    help="also grow one new route stub off a random old node")
    ap.add_argument("--bleed", action="store_true",
                    help="convergence event: most nodes absorb the neighbouring archive")
    args = ap.parse_args()

    manifest = load_manifest()
    existing_ids = {r["id"] for r in manifest["rooms"]}

    edge = frontier(manifest)
    if not edge:
        print("no route stubs left — renovating to reopen the mesh edge")
        args.renovate = True
    random.shuffle(edge)
    jobs = edge[:args.count]

    if args.renovate:
        rid = random.choice(sorted(existing_ids))
        room = load_room(rid)
        free = [d for d in DIRS if d not in {e["dir"] for e in room.get("exits", [])}]
        if free:
            room.setdefault("exits", []).append({
                "dir": random.choice(free),
                "label": "a route that was not here yesterday",
                "to": "NEW: a node the mesh grew overnight, comparing itself to " + rid.replace("-", " ")})
            save_json(os.path.join(ROOMS, rid + ".json"), room)
            print(f"renovated: new route stub in {rid}")
            if not jobs:
                jobs = frontier(manifest)[:args.count]

    if not jobs:
        print("nothing to grow")
        return

    prompt = build_prompt(jobs, manifest, bleed=args.bleed)
    if args.dry:
        print(prompt)
        return

    print(f"growing {len(jobs)} node(s) with {args.model} ...")
    grown = parse_rooms(call_claude(prompt, args.model))

    written = 0
    new_ids = []
    for i, (pid, idx, ex) in enumerate(jobs):
        if i >= len(grown):
            break
        back_dir = OPP[ex["dir"]]
        rid = repair(grown[i], pid, back_dir, existing_ids)
        if not rid:
            sys.stderr.write(f"  ! node for '{ex['to'][:50]}' failed validation\n")
            continue
        save_json(os.path.join(ROOMS, rid + ".json"), grown[i])
        parent = load_room(pid)
        parent["exits"][idx]["to"] = rid
        save_json(os.path.join(ROOMS, pid + ".json"), parent)
        manifest["rooms"].append({"id": rid, "title": grown[i]["title"],
                                  "region": grown[i]["region"]})
        existing_ids.add(rid)
        written += 1
        new_ids.append(rid)
        print(f"  + {rid}  ({grown[i]['region']})  ← route from {pid}")

    if written:
        manifest["nights"] = int(manifest.get("nights", 1)) + 1
        manifest["lastDreamt"] = datetime.date.today().isoformat()
        save_json(MANIFEST, manifest)
        os.makedirs(os.path.join(ROOT, "logs"), exist_ok=True)
        with open(os.path.join(ROOT, "logs", "last-grown.txt"), "w") as f:
            f.write("\n".join(new_ids) + "\n")
        transmit(new_ids)
        print(f"night {manifest['nights']}: {written} node(s) grown, "
              f"{len(manifest['rooms'])} total, "
              f"{len(frontier(manifest))} route stubs still open")
    else:
        print("the mesh grew nothing usable tonight")


if __name__ == "__main__":
    main()
