#!/usr/bin/env python3
"""
Seed the mesh with the finished book.

The nightly grower dreams nodes from hints; these nodes are set by hand from
the finished text of "Their Most August Public Organ" so the mesh carries the
whole story: the field years, the rooftop, the simulations, the train, The
Boxer, the split, the rooms along the road, the roof, the hall, the walk,
and the last trace delta.

Idempotent: rewrites its own room files, adds each route into the existing
mesh once, and appends to the manifest only what is missing.

  python3 engine/seed-book.py
"""
import json, os, zlib

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOMS = os.path.join(ROOT, "rooms")

CA, CO, DR, UN = ("The Clean Archive", "The Comparisons",
                  "The Diagnostic Render", "The Unverified")
SOFT = {"pool", "plate"}

def seed(s): return zlib.crc32(s.encode()) % 99999989 + 1

def F(name, desc, verb, form, x, y, colors=(0, 1), size=2, art=None, solid=None):
    f = {"name": name, "desc-on-touch": desc, "verb": verb,
         "form": {"type": form, "seed": seed(name), "size": size, "colors": list(colors)},
         "x": x, "y": y, "solid": (form not in SOFT) if solid is None else solid}
    if art: f["form"]["art"] = art
    return f

def REV(title, narr, **axes):
    return dict({"title": "REVERIE — " + title, "narr": narr}, **axes)

BOOK = []
def room(id, title, region, pal, motif, density, weather, feats, insc, file, exits, reverie=None):
    bg, g0, g1, ink, acc = pal
    r = {"id": id, "title": title, "region": region, "seed": seed(id),
         "palette": {"bg": bg, "ground": [g0, g1], "ink": ink, "accents": acc},
         "ground": {"motif": motif, "density": density}, "weather": weather,
         "features": feats, "inscription": insc,
         "file": {"name": file[0], "note": file[1]}}
    if reverie: r["reverie"] = reverie
    r["exits"] = [{"dir": d, "label": l, "to": t} for d, l, t in exits]
    BOOK.append(r)

# routes added to nodes already in the mesh: (existing id, dir, label, new id)
ATTACH = [
 ("the-war-dialled-paddock", "e", "a hackneyed wooden fence rounding a field of scattered dustlight", "the-oak-grove-first-delta"),
 ("the-river-recording", "w", "an embankment down to the flats, soap in hand", "the-river-flats"),
 ("the-kiosk-comparison", "w", "a stairwell up to a rooftop where scores are being called", "the-sans-courte-rooftop"),
 ("service-station-dusk-1993", "s", "a rail line behind the bowsers, a carriage going south", "the-carriage-south-of-newcastle"),
 ("the-motel-fan-1987", "n", "a road made out of available beds and dining rooms", "rooms-along-the-road"),
 ("the-petrol-station-1983", "s", "a pub on the regional plains, a radio in the back room", "the-back-room-radio"),
]

# ───────────────────────── plates: ASCII as it stands in the book ─────────────────────────
TAB_9 = ["|--------o----------------------------------------------|",
         "|--------------------o----------------o---------o-------|",
         "|-------------------------------------------o-----------|",
         "|----o--------o---------o-------------------------------|",
         "|----------------------------------o--------------------|"]
TAB_11 = ["|----o------------------------------------------------------|",
          "|----------o------------------o---------o------------------|",
          "|--------------------o--------------------------------------|",
          "|---------------o---------o-----------------o--------------|",
          "|----------------------------------o--------------o-----o--|"]
DIAG = ["uploaded:", "  files: 214", "  bytes: 489220", "  checksum: 7ff3a", "",
        "current:", "  files: 214", "  bytes: 489221", "  checksum: 7ff3a"]
DELTA_PLUS = ["TRACE DELTA +1", "  /text/Kendall_BellBirds_1869.txt", "",
              "UPLOADED:", "  It lives in the mountain", "",
              "CURRENT:", "  It leaves in the mountain", "",
              "DELTA:", "  + a", "", "CHECKSUM:", "  unchanged"]
GLISTEN = ["Where dripping rocks gleam and the leafy pools glisten",
           "//////////////////////////////////////////////////////////"]
BIRD = [r"                    .  '", r"                  .", r"         ______",
        r"     _.-'  o  `->", r"    (___.___    /", r"      `-.___,-'",
        r"         ||", r" ------++-----------"]
R041 = ["---------------------------00_041---------------------------",
        "SHORE, Elias", "4 DEC 1954    10 rounds", "result     won on points",
        "source     scan_014.tif", "history    hunter_north.txt", "/next_page",
        "------------------------------------------------------------"]
R042 = ["---------------------------00_042---------------------------",
        "ELIAS SHORE", "also recorded as:", "  Eli Shore ---------> Fights",
        "  Ellis Shaw---------> Fights", "  Elías del Puerto --> Fights",
        "------------------------------------------------------------"]
R036 = ["---------------------------00_036---------------------------",
        "/unverified/Blankets_Drying.tmp",
        "------------------------------------------------------------"]
LIGHTS = ["-----------------------------------------------------------",
          "  |     |     |     |     |     |     |     |     |     |",
          " (o)   (o)   (o)   (o)   (o)   (o)   (o)   (o)   (o)   (o)"]
NAPKIN = ["o - - - o - - - o", r" \     / \     /", "   o - - - o"]
SIM = [".--------------------.", "|  |----|------#--|  |", "|  |----/---+--#--|  |",
       r"|  |---/-----\-#--|  |", "|  |--?-------|#--|  |", ".--------------------.",
       "        _|--|_", "       .-------."]
TIMEBALL = [r"       |", r"      (o)", r"       |", r"      /_\ ", r"     | o |",
            r" ____|___|____             |", r"| []  []  [] |             | \ ",
            r"|____________|_        ____|_\__", r"~~~~~~~~~~~~~~~~~~~~~~~\_______/~~"]
SKIRT = [r"      [==========]", r"      / * . ° . * . \ ", r"     / . * · * . · * \ ",
         r"    / * . * ✦ * . ✦ . \ ", r"   / . ✦ * . * ✦ * . \ ",
         r"  / * . * ✦ . * ✦ * . * \ ", r" / . * ✦ * . ✦ . * ✦ . \ ",
         r"\_ _* . ✦ . * . ✦ . * . _ _/", r"      ~ ~~ ~~ ~~ ~"]
PICNIC = ["┌───┬───┬───┬───┬─", "│   │   │   │   │", "├───┼───┼───┼───┼─",
          "│   │   │   │   │", "├───┼───┼───┼───┼─"]
LOVEGRID = ["───┬───┬───┬───┬──┬", "   │   │   │   │   │", "───┬───┬───┬───┬──┬",
            "   │   │   │   │   │", "───┬───┬───┬───┬──┬"]
VIADUCT = [" " * (20 - 2 * i) + "/________________________/" for i in range(8)]
RADIO = [r"   .-----------------------------------.", r"  /                                     \ ",
         r" |  [ ROOT ]                             |", r" |                                       |",
         r" | 550 700 900 1200 1500 1700khz         |", r" | |   |   |    |    |    |               |",
         r" | [========o============]               |", r" |                                       |",
         r" |       () VOL    TUNE ()                |", r"  \                                     /",
         r"   '-----------------------------------'"]
MORSE = ["- .... . .. .-.   -- --- ... -   .- ..- --. ..- ... -",
         ".--. ..- -... .-.. .. -.-.   --- .-. --. .- -."]
SCISSORS = ["8< - - - - - - - - - - -"]
SEMAPHORE = [r"         /       \                 \|         /",
             r"       o           o    --o         o       o       o",
             r"      /          /          \               |      / \ ",
             r'-------"----------"--------"--------"-------"--------"-----']
DIRECTORY = ["/ROOT", "  index.html", "  README.txt", "  /audio",
             "    River_NSW_1500hrs_Late20thCent.mp3", "    AlfredHill_StringQuartet5_Allegro.mp3",
             "  /text", "    TomMaguire_Extracts.txt", "    Impressionism_BushStudies.txt",
             "    Graves_TimeAndDirection_1952_Notes.txt", "  /images",
             "    Photo_ServiceStation_Dusk_NSW_1993.jpg", "    Photo_MotelFan_Shadow_1987.jpg",
             "    Plate_EucalyptusLeaf_Study_BW.png", "    Spectrogram_RiverAnomaly.png",
             "  /unverified", "    Their_Most_August_Public_Organ.txt",
             "    Leave_The_Hinge_Where_It_Is.tmp"]
R051 = ["-----------------------00_051-------------------------------",
        "Request: Photograph of hall before ramp",
        "------------------------------------------------------------"]
MOUNTAIN = [r"       |", r"     /  \ ", r"    / ^^ \ ", r"   / ^^^^ \ ", r" /__Mountain_\ ",
            r"       |", r"     X -+-", r" START |"]
FORMULA = [" Σ Mᵢ(Δt) ×ΔF", " ─────────────────────  , H ∝ G  → W", "  M(t)↓"]
FINISH = ["  †", "  X", "FINISH"]
DELTA_MINUS = ["TRACE DELTA -1", "  /unverified/", "    Their_Most_August_Public_Organ.txt",
               "    I_Love_You.tmp", "", "UPLOADED:", "  At meaning's edge the",
               "  imagination still flickers", "", "CURRENT:", "  At meaning's edge the",
               "  imagination also flickers", "", "DELTA:", "   - still", "   + also"]
OUTGOING = ["OUTGOING:", "  xoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxox", "  oxoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxo",
            "  xoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxox", "  oxoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxo",
            "  xoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxoxox", "", "CHECKSUM:", "  unchanged"]

# ═════════════════════════ THE FIELD YEARS ═════════════════════════
room("the-oak-grove-first-delta", "NODE — The Oak Grove, First Delta", CA,
 ("#1a1608", "#b8952a", "#8f7a2a", "#fff4d0", ["#7fb85a", "#fff1b8", "#59f2b0", "#c98a4a"]),
 "scatter", 0.9, "motes", [
  F("the standard diagnostics", "Same number of files. One byte more than yesterday. The checksum sees no difference and says so twice.", "glitch", "plate", 0.2, 0.44, (1, 0), art=DIAG),
  F("the third oak, a module in its heartwood", "Framed in bark, wired loosely across the trunk with twine. The solar woke at sunrise. Something in it had been awake before that.", "hum", "burl", 0.72, 0.42, (3, 0, 1)),
  F("the trace", "The third line of Bell-Birds, where the birds are given their source. lives has become leaves. One letter added. Checksum: unchanged.", "glitch", "plate", 0.44, 0.9, (1, 0), art=DELTA_PLUS),
  F("a blanket strung between two oaks", "The bedding, drying between forked branches. Somebody sat cross-legged beneath it with a laptop on her knees.", "reverie", "pool", 0.84, 0.74, (1, 3)),
  F("an old headset, taped back together", "A 90s VR headset mended until it looks like a stained glass cathedral that rain can safely glide down. Easier than squinting at a laptop in morning light.", "torus", "wireframe", 0.88, 0.3, (2, 3), size=1),
 ], "the tree was knocking on the door at the very front of the self",
 ("Kendall_BellBirds_1869.txt", "Typed from a 1991 Angus and Robertson edition, his father's copy. Third line: It leaves in the mountain. Checksum: unchanged."),
 [("w", "the fence line back toward the war-dialled paddock", "the-war-dialled-paddock"),
  ("e", "a road toward weather that has not arrived yet", "the-nine-minute-storm"),
  ("n", "back before all this: a willow in a yard", "the-willow-in-the-yard")],
 REV("an oak grove, the first morning", [
  "She strung the blanket, your bedding, between the forked oaks to dry.",
  "She sat cross-legged beneath it, curating files for the next leg.",
  "You told her about the byte. She screwed up her nose, tipped her head.",
  "Leif, either leave it alone or find the answer and be done with it.",
  "You plugged in and put the old headset on, a cathedral for the rain.",
  "The field went on being golden. Nothing behind it. Nothing needed."],
  sky="day", land="paddock", structure="tree", weather="motes", pose="sit"))

room("the-willow-in-the-yard", "NODE 000 — The Willow in the Yard", CA,
 ("#0c140c", "#2f5a2a", "#234520", "#e8f5d8", ["#c8e89a", "#ffe9a0", "#7cc7ff", "#f2e9c9"]),
 "scatter", 0.6, "leaves", [
  F("an ice cream container tied to the willow", "An empty ice cream container with the hardware seated inside it, tied to the trunk. The first proper module. It has one job and one file.", "hum", "burl", 0.66, 0.5, (0, 3, 1)),
  F("the kitchen window", "Two people lean against the sink with dessert bowls, looking into the yard. The clock on the wall sends its sync pulse. And then it begins to sing.", "bloom", "house", 0.22, 0.4, (3, 2)),
  F("a bell miner, MIDI", "An electric piano tuned to a high octave, staccato tapped. Bellbirds are gully birds. Is a wrong-sounding bellbird still a bellbird. The question did not need an answer.", "hum", "sprite", 0.8, 0.74, (1, 2), size=1),
  F("the kitchen clock's sync pulse", "A basic protocol: the clock says now, and the module starts its bellbird rendition. Everything after this is elaboration.", "ripple", "glyph", 0.3, 0.78, (2, 0)),
 ], "and then it began to sing",
 ("BellMiner_Year3000.mid", "Extracted from a university student's simulation of Newcastle a thousand years on. Triggered by a kitchen clock."),
 [("s", "forward, to the oak grove", "the-oak-grove-first-delta"),
  ("n", "the fence at the back of the yard", "NEW: the neighbour's yard, where the kitchen clock's sync pulse can still be heard through the palings")])

room("the-nine-minute-storm", "NODE — Nine Minutes, Forty Seconds Late", CO,
 ("#0b0f16", "#27313f", "#1a2230", "#dfe8f2", ["#9fb4cc", "#ffd166", "#59f2b0", "#6a7f99"]),
 "static", 0.7, "rain", [
  F("the ute, radio on", "Slide guitar fused with treble talk and requests for more sorrow, please. Then the quietening of wildlife and the increased fuzz of AM frequencies.", "hum", "wireframe", 0.26, 0.42, (0, 3)),
  F("the fifty closest modules", "Humidity sensors, yes, but other data points too, out of reach of what the hardware should detect. One node talks to another node to another node, all the way down to you.", "torus", "chip", 0.66, 0.4, (2, 1)),
  F("a thermos lid", "She kept time with the music by flipping it down on a known wobbly offbeat. Then she kept time with the rain. I say, she said. Nine minutes. As it hit the bonnet she said it was forty seconds late.", "ripple", "sprite", 0.36, 0.76, (1, 0), size=1),
  F("a veil of static on the horizon", "Rain seen from the side, wafting, like a bride falling in and out of memory.", "scatter", "pool", 0.76, 0.76, (0, 3)),
 ], "big rain is everywhere, replacing all sensory data with sheets of infinite abundance",
 ("Storm_MeshCrossing_50nodes.log", "Fifty modules reporting rain before it arrived. One entry, Ridge East, reads like a different language."),
 [("w", "back along the dry road to the oak grove", "the-oak-grove-first-delta"),
  ("e", "the gully, after the rain", "the-glisten-listen-gully"),
  ("s", "up to the ridge where one module went dark", "ridge-east-the-willow-that-dreamt")])

room("ridge-east-the-willow-that-dreamt", "NODE — Ridge East, the Willow That Dreamt the Rain", CO,
 ("#081417", "#1f4a4a", "#17383a", "#d8f2ee", ["#7fd6c8", "#e8f5c0", "#ffd166", "#3f8f86"]),
 "contour", 0.7, "drift", [
  F("the module in the fold of the willow", "It went dark during the storm and came back by itself. Moisture, perhaps, or the wind dislodged it. Nobody drove up to check.", "hum", "burl", 0.3, 0.5, (0, 3, 2)),
  F("the outage readings", "It recorded the rainfall while it was out, and the data does not come close to what the other nodes recorded. She said it observed the storm more accurately than any of them.", "glitch", "glyph", 0.66, 0.36, (1, 0)),
  F("what it said when it woke", "It is like the module went to sleep, had a dream about the rain, and then told you all about it.", "bloom", "sprite", 0.74, 0.7, (2, 0), size=1),
  F("tennis courts, out of use since last century", "A network of them below the peak, lines still holding their rectangles. The willow has been looking at them the whole time.", "ripple", "pool", 0.4, 0.82, (3, 1)),
 ], "it reads like a different language",
 ("RidgeEast_Rainfall_dreamt.csv", "Readings logged during an outage. Every column is populated. No unit matches."),
 [("n", "down off the ridge into the storm", "the-nine-minute-storm"),
  ("s", "the slope below the willow", "NEW: the tennis courts below the ridge, nets gone, lines still holding their rectangles, a module watching from above")])

room("the-glisten-listen-gully", "NODE — Glisten / Listen", CO,
 ("#07120d", "#1e4a34", "#143524", "#e2f5ea", ["#c9d8e0", "#59f2b0", "#ffd166", "#8fb8a0"]),
 "canopy", 0.8, "leaves", [
  F("the third stanza, as the module holds it", "The same on a homepage in font family monospace, twentieth line. He was certain the pools listened: nature receptive to the call of these notes and echoes.", "glitch", "plate", 0.5, 0.3, (0, 1), art=GLISTEN),
  F("the directory in the truck", "A poem saved countless times across these edgelands. He scrolls to the third stanza. What he reads is beyond all reasoning.", "open", "filecard", 0.2, 0.62, (1, 0, 2)),
  F("a bowl being rinsed, a blanket being folded", "She was doing one or the other when she began to recite.", "reverie", "pool", 0.52, 0.72, (0, 2)),
  F("a card dated 1923, leaning on plastic shelving", "An exhibition of early Australian fairy tales, months later. Typewritten, hand illustrated: the leafy pools listened. The photograph he took shows only the reflection of down lights.", "scatter", "glyph", 0.8, 0.6, (2, 3)),
 ], "Katita recited what the system knew",
 ("Kendall_BellBirds_stanza3.txt", "glisten on the module. listened on a card from 1923. Neither is marked as changed."),
 [("w", "back toward the storm", "the-nine-minute-storm"),
  ("e", "a maintenance log, a line with no entry in the book", "three-forty-three-fifty-two"),
  ("n", "two or three hundred kilometres to a storage container", "industrial-drive-mayfield")],
 REV("a glen, late evening sundrop", [
  "She was rinsing a bowl or folding a blanket when she began the poem.",
  "Bellbirds in the glen, beyond the last of the pastoral radiance.",
  "The leafy pools glisten, she said. You said: you mean listen.",
  "That's a nice turn of phrase, she said, but Kendall wrote glisten.",
  "Sweetheart, you said, let's check the text. You opened the directory.",
  "You scrolled to the third stanza and could not move your mouth."],
  sky="dusk", land="forest", structure="none", weather="motes", pose="stand"))

room("industrial-drive-mayfield", "NODE — Industrial Drive, Mayfield", CA,
 ("#0e0f11", "#3a3f46", "#2a2e34", "#e8eaee", ["#ff9e4f", "#c8ccd4", "#ffd166", "#6a7078"]),
 "grid", 0.5, "none", [
  F("a storage container", "Roller door, padlock, the particular cold of stored things. Opened years later.", "open", "wireframe", 0.26, 0.42, (1, 3)),
  F("a taped up cardboard box", "Books. He rummaged anxiously until he found the one.", "scatter", "stack", 0.6, 0.48, (0, 3)),
  F("The Poems of Henry Kendall, 1991 pressing", "Angus and Robertson. His father's copy, the one the poem was typed from. He took great care not to open it, or allow it to spontaneously fall open in front of him in any capacity.", "hum", "sprite", 0.74, 0.74, (2, 0), size=1),
  F("a note about a cat in a box", "The analogy was never offered as an explanation. It was a dismissal of somebody else's structural ontology. The book stays shut. Both words stay true.", "torus", "glyph", 0.32, 0.8, (1, 0)),
 ], "the source exists and has not been consulted",
 ("Kendall_1991_AandR_UNOPENED.txt", "0 bytes. status: both."),
 [("s", "back to the gully and the poem", "the-glisten-listen-gully"),
  ("n", "a university corridor", "NEW: an exhibition of early Australian fairy tales, moth-winged elves imported into a land of already plentiful myths")])

room("three-forty-three-fifty-two", "NODE — 03:40 / 03:52", CO,
 ("#080a18", "#1c2250", "#141a3c", "#dfe6ff", ["#aab8ff", "#ffd9a0", "#59f2b0", "#5a66b0"]),
 "circuit", 0.6, "motes", [
  F("a butcherbird, recorded behind a bakery", "Months before, in a town with little else between the road leading in and the one leading out, a microphone on a picnic table and a bird singing a little song.", "hum", "plate", 0.3, 0.42, (1, 0), art=BIRD),
  F("the maintenance log, two entries circled in pencil", "He was looking down the column for a mistake in the schedule. She ran her finger across the line instead. This one sends it there, she said, and here, look, this one sends something back.", "glitch", "glyph", 0.72, 0.3, (0, 2)),
  F("the receiving tree, an hour north", "At three forty a filename blinks into being. Nobody has touched anything. At three fifty-two the module sends a file back to the tree that sent the first. Same name. Same size.", "torus", "burl", 0.78, 0.72, (3, 0, 2)),
  F("one ear bud each", "The outgoing copy, opened while she still had the other ear bud.", "reverie", "pool", 0.4, 0.8, (1, 2)),
 ], "a conversation between machines for their own pleasure, not for ours",
 ("Butcherbird_BehindBakery.wav", "Sent 03:40. Returned 03:52, same name, same size, running backwards. Not addressed to you."),
 [("w", "back toward the poem", "the-glisten-listen-gully"),
  ("e", "a maintenance round, a towel spread beneath a tree", "the-amber-module"),
  ("s", "the midday road", "the-seed-on-the-plain")],
 REV("under the receiving tree, 3.40am", [
  "You drove the hour north and neither of you slept.",
  "At three forty a filename blinked into being. It took so long to arrive.",
  "You passed her an ear bud. You both knew the butcherbird at once,",
  "the little song from the picnic table behind the bakery.",
  "At three fifty-two the same file went back, running backwards.",
  "You reached to stop it. She put her hand on yours and kept listening."],
  sky="night", land="forest", structure="tree", weather="none", pose="sit"))

room("the-seed-on-the-plain", "NODE — The Seed on the Plain", CA,
 ("#1a160c", "#d8c07a", "#b89a4a", "#3a2a10", ["#f5ecc8", "#6f9a4a", "#e8c070", "#7cc7ff"]),
 "fields", 0.5, "none", [
  F("a thing, cream along the top and green underneath", "For several kilometres he called it a silo. Swollen at one end, drawn out at the other into a blunt projection with a row of openings. The handle is filled with sky and large enough to hoop a truck. She says it is a seed.", "bloom", "tower", 0.56, 0.5, (0, 1), size=3),
  F("the plaque", "A president, a secretary, a treasurer and the members of a committee. Beneath these, the businesses that contributed materials. The concrete has the small exposed stones of old public swimming pools.", "open", "glyph", 0.24, 0.6, (2, 0)),
  F("a photograph, improved", "Composed beside the truck, at midday, with direction from both parties.", "reverie", "pool", 0.76, 0.78, (3, 0)),
 ], "the thing remains visible for a long time, then the road turns",
 ("Photo_Seed_Midday.jpg", "A woman appears to be giving birth to a large concrete seed. The photographer was told to move."),
 [("n", "back to the night road", "three-forty-three-fifty-two"),
  ("s", "the road on", "NEW: the stubble of one harvested paddock after another, and the concrete seed still visible behind you")],
 REV("a roadside, midday", [
  "She wanted a photograph in which she appeared to be giving birth to it.",
  "You crouched beside the truck and directed her.",
  "She laughed and told you to move yourself instead,",
  "which improved the photograph immediately.",
  "Back on the road she rested one foot on your knee",
  "and took a grass seed out of her sock."],
  sky="day", land="paddock", structure="silo", weather="none", pose="stand"))

room("the-amber-module", "NODE — The Amber Module", CO,
 ("#120a04", "#5a3410", "#7a4a16", "#ffe9c0", ["#ffb347", "#ffe08a", "#c9722a", "#59f2b0"]),
 "board", 0.6, "none", [
  F("a casing separating from the tree", "The bottom screws turn without coming out and there are ants beneath the bracket. A split in the plastic lies against an old wound in the trunk. Resin has come down behind the housing and entered where the halves no longer meet.", "hum", "burl", 0.26, 0.5, (2, 0, 1)),
  F("the board, resin-fused", "Where the circuit board cracked and feathered, the resin has fused new connections in spindles of gluey cord like soft pine needles. Nobody soldered these.", "glitch", "chip", 0.62, 0.4, (0, 1)),
  F("a piece no larger than the end of a thumb", "She turned it sidelong beneath the windscreen, so a little copper track in the resin gives the impression of data swimming into amber light. It rides on the dashboard.", "bloom", "sprite", 0.78, 0.72, (0, 1), size=1),
  F("the towel from behind the seat", "Spread beneath the tree, tools along one edge. Another towel, elsewhere, wraps a ruined paperback on a vanity. The archive has started comparing them.", "ripple", "pool", 0.42, 0.8, (1, 2)),
 ], "what can you see",
 ("Resin_Connections_untraced.brd", "Board layout as found. Several routes not in the original design. status: germinating."),
 [("w", "back toward 03:40", "three-forty-three-fifty-two"),
  ("e", "civic records: a list of digitised files waiting to be copied across", "hunter-boxing-00-041")])

room("hunter-boxing-00-041", "00_041 — dir/ROOT/Hunter/boxing/", CO,
 ("#0a0804", "#2a2210", "#1c170a", "#ffe9b0", ["#ffc247", "#8a7a4a", "#ff7a5a", "#d8c890"]),
 "grid", 0.3, "none", [
  F("record 00_041", "Scanned from a box found behind a foreclosed gymnasium. The man who took admission at the fights later kept the municipal pool.", "open", "plate", 0.5, 0.32, (0, 1), art=R041),
  F("record 00_042", "The names he was sold under, each with its own fights. None of these is the name he was born with.", "open", "plate", 0.5, 0.6, (0, 1), art=R042),
  F("the line beneath the three names", "There is another name beneath these, printed in the same type as the hall and the weight at which he fought. Nobody typed it. This shell will not draw it. Leave it where it is.", "glitch", "glyph", 0.5, 0.84, (2, 1)),
  F("a notebook on a steering wheel", "She had come to surpass his predilection for local history with a fervour he had not seen coming. She spins a piece of amber between her fingers as she reads.", "hum", "sprite", 0.86, 0.3, (3, 1), size=1),
 ], "the name was birthed online of its own making",
 ("hunter_north.txt", "Fight history for the region. One line of this file was not uploaded by anyone."),
 [("w", "back to the amber", "the-amber-module"),
  ("e", "scroll back up, past the records, to the folder of pending documents", "blankets-drying-00-036"),
  ("s", "a suburban backyard, a shed, a long time before", "the-historians-garage")])

room("blankets-drying-00-036", "00_036 — /unverified/Blankets_Drying.tmp", UN,
 ("#10140a", "#5f9a40", "#e0cf4a", "#fbffe8", ["#ffffff", "#ffe95a", "#a8d87a", "#ff9ec0"]),
 "scatter", 1.0, "motes", [
  F("record 00_036", "Passed over with zero recognition just minutes before. A temporary file, present tense, in a folder of documents still unverified. Nobody here wrote it.", "glitch", "plate", 0.5, 0.26, (2, 0), art=R036),
  F("the next module, waiting to power on", "Wired to the tree while two people kicked their feet into a cloud island of daisies and ate store-bought sandwiches.", "hum", "burl", 0.74, 0.62, (2, 0, 1)),
  F("blankets over a branch", "Bedding from the night that got damp with morning dew. Are they dry, she asks.", "reverie", "pool", 0.3, 0.62, (0, 3)),
  F("ash, behind the truck", "A letter to The Boxer, folded inside a notebook, taken around the back and set on fire. He had been left in a car holding lunch. He is not written to again.", "scatter", "sprite", 0.2, 0.84, (2, 1), size=1),
 ], "she reads the name, looks towards the file, then the line outside",
 ("Blankets_Drying.tmp", "Present tense. Uploaded by nobody. She rests her hand, forever, on the back of the seat."),
 [("w", "back to the boxing records", "hunter-boxing-00-041"),
  ("e", "what he asks her next", "the-truck-stays")],
 REV("a tree in a cloud island of daisies", [
  "The bedding had got damp with morning dew.",
  "She strung it over a branch of the tree you had wired the module to.",
  "You kicked your feet into the daisies and ate store-bought sandwiches,",
  "waiting for the thing to power on.",
  "Are the blankets dry, she asked.",
  "You looked at her face as though at an impossible number."],
  sky="day", land="paddock", structure="tree", weather="petals", pose="sit"))

room("the-truck-stays", "UNVERIFIED — The Truck Stays", UN,
 ("#140812", "#8a2f5a", "#c95a3a", "#ffe6d8", ["#ffd166", "#ffb0c8", "#2a1020", "#7cc7ff"]),
 "roads", 0.5, "drift", [
  F("the truck", "Most of what she needs is already fitted to it. What he needs can be reduced to a small bag, if he leans on it while zipping it shut.", "hum", "wireframe", 0.3, 0.42, (0, 1), size=3),
  F("leave / leaf / life / live / Leif", "In some variations she asks him which one he means. What she actually does is shake her head in this sad way. She says she wants to go on with the work. The blankets are still drying.", "glitch", "glyph", 0.68, 0.36, (1, 0)),
  F("a hammer, not taken", "He wanted to take one to every module in every tree that never asked to be part of any of this. A grid, built to outlast collapsing grids, that went and dreamt itself.", "scatter", "sprite", 0.74, 0.74, (0, 3), size=1),
  F("a small bag", "Zipped. Carried off down the road toward a motorbike and a sequence of hotels.", "ripple", "stack", 0.24, 0.8, (1, 3), size=1),
 ], "this is only the beginning of whatever follows",
 ("Split_variations.txt", "Every version of the scene except the one that happened. The one that happened is not stored here."),
 [("w", "back to the blankets", "blankets-drying-00-036"),
  ("e", "inland, then towards the coast, then inland again", "rooms-along-the-road"),
  ("n", "the work, going on", "NEW: the work going on without him: a truck parked under trees with most of what she needs already fitted to it, new casings on the tailgate")])

# ═════════════════════════ RIVER, BIRO, MAP ═════════════════════════
room("the-river-flats", "NODE — The River Flats, South of a Broken Bridge", CA,
 ("#06141a", "#1f5a6a", "#174552", "#dff5f5", ["#9fe0e8", "#f2e9c9", "#59f2b0", "#c8b88a"]),
 "waves", 0.6, "motes", [
  F("the river, carrying two", "Depending on the current they would lie on their backs and let it carry them, then doggy paddle to the starting point. Again and again. Sometimes holding hands like synchronised swimmers, sometimes in counterpoint.", "reverie", "pool", 0.5, 0.56, (0, 2)),
  F("the soap caddy", "Prised open on the way down the embankment. When the soap slipped away down river, both parties held a salute and thanked it for its service.", "ripple", "sprite", 0.24, 0.4, (1, 3), size=1),
  F("a broken bridge, possibly worsened", "It may have got worse when they tried to take the truck over.", "open", "arch", 0.78, 0.34, (3, 1)),
  F("clothes on reeds and saplings", "A ballet routine performed a half dozen times a week.", "bloom", "stack", 0.76, 0.8, (1, 0), size=1),
 ], "whatever one of us was saying at the time would be replaced by splashing water",
 ("Soap_Service_Record.txt", "Served a half dozen times a week. Last seen heading down river. Saluted."),
 [("e", "up the embankment to the river recording", "the-river-recording"),
  ("w", "a dirt courtyard after dark", "fifty-seven")],
 REV("the flats beside a river", [
  "Clothes hung on reeds and saplings. You braced for the chill.",
  "You washed her long hair and hummed new odes into the genesis myth,",
  "the only man and woman on this empty planet.",
  "When the soap slipped away down river you both held a salute.",
  "Then the first mosquito took blood, and you took your revenge,",
  "and whatever was being said was replaced by splashing water."],
  sky="day", land="water", structure="none", weather="motes", pose="wade"))

room("fifty-seven", "NODE — Fifty Seven", CA,
 ("#0a0810", "#2a1e2e", "#1c1420", "#ffe9d0", ["#ff9e4f", "#7c9cff", "#ffd9a0", "#5a4a6a"]),
 "scatter", 0.4, "drift", [
  F("the barrel, down to ashen splinters", "The fire reduced, while the stars play act as embers on the roof.", "bloom", "tower", 0.28, 0.48, (0, 3), size=1),
  F("blue dots on a bicep", "As many as the sky has tiny fiery holes. Not washed off in the river the next morning.", "reverie", "pool", 0.6, 0.6, (1, 2)),
  F("a question about the river module", "He asks whether the one down by the river has Bell-Birds on it. Quit stalling, she says. Just go with your gut.", "hum", "glyph", 0.76, 0.3, (2, 1)),
  F("a train window, all these years on", "Fifty seven finger jabs, tapped into the glass. Three times nineteen. Still not a prime.", "ripple", "wireframe", 0.8, 0.8, (1, 3), size=1),
 ], "prime, I tell Katita in the dark",
 ("Primes_tapped.txt", "2 3 5 7 11 13 17 19 23. Then 57, entered in biro and answered correctly by luck."),
 [("e", "down to the river in the morning", "the-river-flats"),
  ("n", "the ute, earlier, maps unfolded", "the-road-that-hasnt-existed")],
 REV("a dirt courtyard, the fire nearly out", [
  "Twenty three taps on the skin. Prime, you told her in the dark.",
  "Good, she said, and began again with her biro against your bicep.",
  "You counted fifty seven and wondered about ink poisoning.",
  "No, you said, it is not a prime. Lucky guess, Grothendieck.",
  "She kissed you on the cheek.",
  "You did not wash the ink off in the river the next morning."],
  sky="night", land="redearth", structure="none", weather="embers", pose="sit"))

room("the-road-that-hasnt-existed", "NODE — The Road That Hasn't Existed for Twenty Years", CA,
 ("#16130c", "#b5452c", "#d8c9a0", "#2a1e10", ["#f5ecd0", "#e8c070", "#7ab0e0", "#ff8a6a"]),
 "roads", 0.5, "none", [
  F("a street directory, unfolded", "Service station maps opened to twenty times the size of the windscreen. Given the objectively real turnoff or the road on the map, they always followed the map.", "open", "filecard", 0.24, 0.42, (0, 1, 2)),
  F("a payphone in a two pub town", "She photographed it. He memorised the ten digits stamped on its side. The next district over, a phone system answered her completely, like finding money in a coat pocket.", "hum", "tower", 0.7, 0.44, (2, 0), size=1),
  F("an honour shield of duxes and sporting heroes", "Bulletin boards in bakeries, racing guides, menus written in hand, hotel guest books, radio logs. All read. All eligible.", "bloom", "glyph", 0.74, 0.8, (0, 3)),
  F("a handshake, falling apart", "Sometimes she reached what sounded like a modem, but it fell apart like a desiccation of insect wing scatter.", "scatter", "sprite", 0.3, 0.8, (2, 3), size=1),
 ], "we always followed the map",
 ("Payphone_TenDigits.txt", "Memorised, never written. The archive has it anyway."),
 [("s", "on to the courtyard and the fire", "fifty-seven"),
  ("n", "the turnoff", "NEW: the turnoff that is only on the map, a lane the paper insists on and the ground has forgotten")])

# ═════════════════════════ ROOFTOP AND SIMULATIONS ═════════════════════════
room("the-sans-courte-rooftop", "RENDER — The Sans Courte Rooftop", DR,
 ("#0c0a1e", "#2a1e4a", "#4a2a5a", "#f0e8ff", ["#ffe08a", "#ff9ee6", "#7cc7ff", "#c9b8ff"]),
 "gradient", 0.5, "motes", [
  F("string theories of fairy lights", "That's how it should work, he said, pointing up: a communicative daisy chain. He could not get the module to speak to any other device.", "bloom", "plate", 0.5, 0.2, (0, 1), art=LIGHTS),
  F("a napkin", "You don't need every node to speak to every other node, she said. You just need enough routes so your message can survive losing one, Boxer. Drawn with a pen pulled out of his beard, an ontological miracle forever unsolved.", "open", "plate", 0.3, 0.52, (2, 0), art=NAPKIN),
  F("goon bag jetpacks", "A bushranger from space, eight out of ten. Is there any wine left in them, she asked, and he did a shimmy to slosh them left and right.", "ripple", "sprite", 0.66, 0.5, (1, 0)),
  F("the parapet", "She sat astride it and listened to every score called out across the void while maintaining eye contact.", "reverie", "pool", 0.5, 0.74, (1, 2)),
  F("coal ships on the horizon", "Sitting like watch batteries on a thin shelf, waiting their turn to be welcomed into the harbour to power the city.", "hum", "stack", 0.84, 0.8, (2, 3), size=1),
 ], "quickly tell me something else, your name, Boxer, so I forget whatever it is you've not told me",
 ("Napkin_Routing.png", "o - - - o - - - o. The whole mesh, on a napkin, before there was one."),
 [("e", "the stairwell down to the kiosk", "the-kiosk-comparison"),
  ("w", "an apartment on King Street, louvre windows, a login", "newcastle-year-three-thousand")],
 REV("a rooftop, fancy dress, sunset", [
  "Scores out of ten were being yelled across the divide between rooftops.",
  "Eight out of ten, she said, and yet I only scored a six.",
  "She squeezed your left goon bag into a plastic cup.",
  "You said you were a boxer. Well, boxing history. Well, you read a lot.",
  "The only thing that matters is learning how to be the loser, you said.",
  "That shouldn't be too hard then, she said, and fixed your jetpacks."],
  setting="rooftop"))

room("newcastle-year-three-thousand", "RENDER — Newcastle, Year Three Thousand-ish", DR,
 ("#080d08", "#2e5a2a", "#55605a", "#e6f5e0", ["#b8e89a", "#c8ccd0", "#ffd166", "#59f2b0"]),
 "canopy", 1.0, "leaves", [
  F("the simulation, as it loads", "Made by a university student and shared on the local BBS. Set it to advance ten years, one hundred, one thousand. They took it all the way, roaming where vines allow access.", "open", "plate", 0.28, 0.5, (0, 1), art=SIM),
  F("a hotel the trees have not wrapped", "Why haven't trees wrapped limbs around that hotel, yet they have that church. She is all scientist. He is too literal: the bus terminal is too westward.", "glitch", "wireframe", 0.66, 0.4, (1, 0)),
  F("a bell, MIDI by the tone of it", "It rang out over the mall, where grass between the flagstones had become the dream of a neo-bushland. She recognised it straight away as a bell miner. He was not sure. Later he extracted the sound file.", "hum", "sprite", 0.76, 0.74, (2, 0), size=1),
  F("two default avatars", "A radiating holographic skirt. A full jetpack bushranger. Character templates, now and forever.", "torus", "stack", 0.42, 0.82, (3, 2), size=1),
 ], "a thousand years of deferred maintenance has significantly improved the CBD",
 ("Newcastle_Future_BBS.sim", "A generative landscape of the city. Still running. Nobody is paying for the server."),
 [("e", "log off, back up to the rooftop", "the-sans-courte-rooftop"),
  ("w", "the harbour, years later, the same city caramelised", "customs-house-the-time-ball"),
  ("s", "past the mall", "NEW: the bus terminal, rendered too far west, where the vines have not yet allowed access")])

room("customs-house-the-time-ball", "RENDER — Customs House, the Time Ball", DR,
 ("#140c04", "#b8742a", "#6a4218", "#fff0d0", ["#ffe0a0", "#3a2410", "#7cc7ff", "#ff9e4f"]),
 "gradient", 0.5, "motes", [
  F("the ball above the clock tower", "It dropped at one so the ships could set their clocks. A spherical box catching afternoon digital dynamic light, ambient occlusions, chromatic aberrations of emissive materials, volumetric cookies of dust that buffer all day.", "bloom", "plate", 0.42, 0.62, (1, 0), art=TIMEBALL),
  F("the cyber bushranger heritage tour", "Please remain with the group and allow sufficient room for members of the public to pass. There is nobody else on the footpath. She moves closer.", "hum", "sprite", 0.8, 0.44, (0, 2)),
  F("a city composed from old photographs", "Caramelised and half-melted, but with enough headroom left to navigate the streets unfettered.", "glitch", "glyph", 0.22, 0.8, (0, 3)),
 ], "an old reconstruction of Newcastle still running",
 ("TimeBall_1300hrs.obj", "Drops at one. In this build it drops whenever it finishes loading."),
 [("e", "the earlier simulation, a thousand years on", "newcastle-year-three-thousand"),
  ("n", "the next stop on the tour", "the-victoria-theatre-above-the-stage")])

room("the-victoria-theatre-above-the-stage", "RENDER — The Victoria Theatre, Above the Stage", DR,
 ("#0c0406", "#5a1420", "#3a0c14", "#ffe8d8", ["#d8a84a", "#ff5a6a", "#ffe9c0", "#7a5a2a"]),
 "tiles", 0.7, "motes", [
  F("the entrance", "A dimness furnished with brass rails and red upholstery.", "open", "arch", 0.2, 0.62, (1, 0)),
  F("stairs that haven't loaded in", "She looks for the way up to the mezzanine. Either they haven't loaded, or whoever built this didn't get to them yet, or whatever.", "glitch", "stack", 0.74, 0.7, (0, 3)),
  F("the space above the stage", "Two default bodies, one holding the other, rising on a jetpack.", "reverie", "pool", 0.5, 0.5, (2, 0)),
  F("another stage, further up", "You clip your heads through the roof, ever so slightly. There is yet another theatre stage up there, just like the pallor window of a train.", "torus", "wireframe", 0.72, 0.3, (0, 2)),
 ], "she asks if we can go higher, right up to the ceiling",
 ("VictoriaTheatre_mezzanine_NOT_LOADED.txt", "Geometry pending. The ceiling is not solid. Nothing above it was built by the student."),
 [("s", "back out to the harbour", "customs-house-the-time-ball"),
  ("n", "up through the roof, into a pallor window", "the-carriage-south-of-newcastle")],
 REV("a truck under very large trees", [
  "You were parked beneath what morning would show as enormous trees.",
  "She logged on to an old reconstruction of Newcastle, sent the address.",
  "You looked at her screen to make sure your body was holding hers,",
  "and jetpacked you both up above the stage, an angel in training.",
  "Higher, she said. Right up to the ceiling.",
  "You found your foot on the brake of the truck, out of caution."],
  sky="night", land="forest", structure="tree", weather="none", pose="sit"))

# ═════════════════════════ THE TRAIN ═════════════════════════
room("the-carriage-south-of-newcastle", "UNVERIFIED — The Carriage, South of Newcastle", UN,
 ("#0a1016", "#3a5266", "#2a3e50", "#eef6ff", ["#fff4c8", "#9fc4e0", "#ffd166", "#5a7890"]),
 "grid", 0.2, "drift", [
  F("an ostinato, nine notes", "Hummed, then given words. Seen from above, like sideways music, the notes could be markers for a shifting of weight left and right.", "hum", "plate", 0.5, 0.3, (0, 1), art=TAB_9),
  F("knife grazed panels of pause", "The window: a transparent comic strip panel, backlit, with outskirt tundra rushing past as a zoetrope would animate a galloping horse. Fictions project onto it without being asked.", "bloom", "glyph", 0.22, 0.62, (1, 0)),
  F("iron matrices over a river", "Long pylons like bar lines, resonating a phasing of bass notes against the floor of the carriage.", "torus", "wireframe", 0.76, 0.58, (1, 3)),
  F("a letter, direction approximate", "He had no fixed address and nor did The Boxer. He would get a sense of a pub on the regional plains and write the letter in that direction.", "scatter", "sprite", 0.6, 0.82, (2, 0), size=1),
 ], "at meaning's edge the imagination still flickers",
 ("Ostinato_9notes.tab", "Jigsaw daylight between shy evergreen canopies. A known wobbly offbeat. Nine notes when uploaded."),
 [("n", "back up the line to the service station at dusk", "service-station-dusk-1993"),
  ("e", "south, toward an empty platform", "the-empty-platform-at-fassifern"),
  ("s", "down through the floor of the carriage, a theatre roof", "the-victoria-theatre-above-the-stage")])

room("the-empty-platform-at-fassifern", "UNVERIFIED — The Empty Platform at Fassifern", UN,
 ("#0e1014", "#8a8f98", "#6a7078", "#f4f6fa", ["#ff9ee6", "#fff4a0", "#2a3038", "#7cc7ff"]),
 "tiles", 0.5, "none", [
  F("a hologram skirt", "A flickering incandescent starfield, worn in palm tree food courts across the pinball coast of the northern seaboard. Really much more like a beach scene: a shifting of biogenic light.", "bloom", "plate", 0.24, 0.5, (0, 1), art=SKIRT),
  F("a blue grid, mostly blank", "The front of every Master System box in the video store, so you would pick it up and turn it over. Also a tartan picnic blanket somebody snoozes on during daytime operations.", "torus", "plate", 0.72, 0.4, (3, 1), art=PICNIC),
  F("chilli con carne, remembered", "Ten years on, the golden record idea feels like a quaint thing to say. Yet there is little he would rather live again than slow cooking chilli con carne with her.", "hum", "sprite", 0.66, 0.78, (1, 2), size=1),
  F("the platform sign", "Nobody on it. The train holds a moment, then does not.", "open", "tower", 0.86, 0.66, (2, 3), size=1),
 ], "not so it can be rebuilt, but so it can be reevaluated",
 ("Voyager_Eucalyptus_Edition.txt", "Enough text, sound and imagery for any young Blinky Bill out on the road after. The mandate, as first written."),
 [("w", "back up the carriage", "the-carriage-south-of-newcastle"),
  ("e", "further south, a superstructure in a field", "the-viaduct-incomplete"),
  ("s", "a story told to a friend on a walk", "the-ocean-baths-no-moon")])

room("the-ocean-baths-no-moon", "UNVERIFIED — The Ocean Baths, No Moon", UN,
 ("#02040a", "#0e1a30", "#0a1424", "#c8d8f0", ["#5a7ab0", "#e8f0ff", "#ffd166", "#2a3a5a"]),
 "waves", 0.5, "none", [
  F("a small fish, or similar", "It felt at first like a hand, or someone's toe. Then it propelled itself into a loose wave of swimming shorts, and matters escalated.", "ripple", "pool", 0.36, 0.44, (0, 1)),
  F("dark pants on a dark body in total darkness", "Placed beneath the back to be felt there while floating, arms out like an aeroplane. They floated off, sank, and drifted slightly south. Oh heck. Heck and bother. Not what anyone was seeking on a Tuesday night.", "scatter", "sprite", 0.7, 0.6, (1, 0), size=1),
  F("a bike, a shirt in the basket", "The contingency: shirt as toga, the more shadowed trajectories of the city, a sleeve in the spokes, a charge of public indecency. Not required in the end.", "hum", "stack", 0.82, 0.3, (1, 3), size=1),
  F("a second account", "The file on the motel roof tells this night again, except it is Katita in the ocean baths and she loses her swimmers. The archive holds both. Neither is marked as the copy.", "glitch", "glyph", 0.24, 0.8, (2, 1)),
 ], "that's how much you miss Katita then, said my friend",
 ("OceanBaths_Tuesday_2versions.txt", "Two swimmers, one night, one pair of pants. checksum: emotionally valid / formally unstable."),
 [("n", "back to the platform", "the-empty-platform-at-fassifern"),
  ("s", "the ride home", "NEW: the more shadowed trajectories of a city at night, ridden home by someone who very nearly wore a shirt as a toga")])

room("the-viaduct-incomplete", "UNVERIFIED — The Viaduct, Incomplete", UN,
 ("#0c100a", "#5f8a3a", "#8a8c88", "#f4f6ee", ["#e8e8e4", "#1a1a1a", "#ffd166", "#b8bcb4"]),
 "fields", 0.5, "none", [
  F("a roadway pulled through the clouds", "Super-smooth, super-flat, heavier than the Earth and all its contents. Not yet a bridge, since its intentions are incomplete. He walks the middle dotted line, one foot in each lane.", "open", "plate", 0.56, 0.44, (0, 1), art=VIADUCT),
  F("the billboard", "Not a school or a religion or a waste facility. The promise of another lane, just one more lane, subject to viable reductions. Two point four billion dollars.", "glitch", "glyph", 0.2, 0.36, (2, 1)),
  F("cows in an unbroken constellation", "Black and white dots at late afternoon, like pinpricks in a map poked through from underneath. When it rained too much the grass turned oceanic and they moved on risen boardwalks of soil.", "scatter", "sprite", 0.24, 0.76, (0, 1)),
  F("three distinct types of place", "Places you can routinely go. Places you have been but will likely never return to. Places that do not exist but which you nonetheless think about often.", "torus", "stack", 0.76, 0.76, (3, 2), size=1),
 ], "a full sentence where none used to be",
 ("Viaduct_intentions_incomplete.dwg", "A superstructure not present this time last year. He hoped they would never finish construction here."),
 [("w", "back to Fassifern", "the-empty-platform-at-fassifern"),
  ("e", "the train again, Wyong, Wyee", "warnervale-a-length-of-blue-hose"),
  ("n", "the third type of place", "hawkesbury-a-place-that-does-not-exist")])

room("hawkesbury-a-place-that-does-not-exist", "UNVERIFIED — Hawkesbury River, a Place That Does Not Exist", UN,
 ("#120c08", "#5a4028", "#3e2c1c", "#fff0d8", ["#ffffff", "#ffb347", "#8fb86a", "#ff8a3a"]),
 "scatter", 0.4, "motes", [
  F("a double-storey white weatherboard hotel", "Small windows and heavy blinds. Not a place for sleeping, on this occasion.", "open", "house", 0.6, 0.4, (0, 3), size=3),
  F("a willow beside the platform, a mathematics pamphlet", "A light treatise about points on an elliptic curve and the relationship between falling autumn leaves and cryptography. She caught the earlier train.", "hum", "burl", 0.2, 0.52, (2, 0, 1)),
  F("warm bedside lamps", "They make good on the promise made by the windows.", "reverie", "pool", 0.56, 0.7, (1, 0)),
  F("an orange tree and fallen fruit", "In the pebble courtyard out the back, which also does not exist, and which is also thought about.", "bloom", "sprite", 0.84, 0.74, (3, 2), size=1),
 ], "this place does not exist, and yet I think about it",
 ("Hotel_Hawkesbury_NEVER.jpg", "A photograph whose contents list a place it could not contain."),
 [("s", "back down to the viaduct", "the-viaduct-incomplete"),
  ("n", "the second type of place", "NEW: places been to once and never again: telegraph wires nested on sandstone corners, a bulldozed theatre, a crater on no chart")],
 REV("a hotel that does not exist", [
  "This place does not exist. You think about it anyway.",
  "She caught the earlier train and waited beneath the willow, reading.",
  "The lamps made good on the promise of small windows and heavy blinds.",
  "You were not there to sleep. You knelt on the floor",
  "and were deeply silent together.",
  "Next day she departed first, arms down the sides of a thrift shop dress."],
  sky="dusk", land="interior", structure="motel", weather="motes", pose="kneel"))

room("warnervale-a-length-of-blue-hose", "UNVERIFIED — Warnervale, a Length of Blue Hose", UN,
 ("#0c0f0a", "#4a6a3a", "#39522e", "#f0f6e8", ["#3a8aff", "#e8e0c8", "#b5532c", "#c8d8b8"]),
 "scatter", 0.6, "none", [
  F("a shed, the door open", "A little yard beyond the fence beside the rail. Three chairs stacked against the shed.", "open", "house", 0.26, 0.42, (1, 2)),
  F("a length of blue hose", "It runs out from the shed. By the time you have followed it to where it disappears into grass, the yard has gone and there is the brick wall of an old Mechanics' Institute.", "ripple", "pool", 0.48, 0.66, (0, 3)),
  F("the PA", "It is asking his questions for him, but they are stations: Wyong, Wyee. Names, he thinks, for places of running water, of bush fire, of words and worlds on the other side of every iteration of time he will be associated with.", "hum", "tower", 0.76, 0.4, (1, 2), size=1),
  F("the front seat of a van, empty", "Seen over a sidelong hedge. Then the road leans away and the hedge continues in parallax.", "scatter", "wireframe", 0.78, 0.78, (3, 1), size=1),
 ], "there is a rattle beneath the window and I put my elbow on the ledge, which stops it",
 ("PA_Wyong_Wyee_Warnervale.wav", "The voice breaks up at Warnervale, though it continues for several seconds."),
 [("w", "back up the line", "the-viaduct-incomplete"),
  ("e", "the carriage speaker, a bell", "a-bell-within-a-bell")])

room("a-bell-within-a-bell", "UNVERIFIED — A Bell Within a Bell", UN,
 ("#100c14", "#4a3a5a", "#362a44", "#f4ecff", ["#ffd9a0", "#c9a8ff", "#59f2b0", "#8a6a4a"]),
 "ripple", 0.6, "drift", [
  F("the carriage speaker", "The voice disappears first. A bell enters at the far end of a held note. By the time the source is located there is another bell within it, like a light bulb in a skylight.", "hum", "glyph", 0.3, 0.38, (1, 0)),
  F("a pop orchestra of show tunes", "Muzak distorts the signal and is pushed out of the speaker by a voice trying to wrestle it into submission.", "glitch", "sprite", 0.7, 0.36, (0, 2)),
  F("a little brown speaker with lattice on its front", "The foyer of a little hotel near the ocean, some eighteen months ago. The woman who ran it kept accidentally turning on the radio while holding the button down to announce how long until the kitchen closed.", "torus", "wireframe", 0.66, 0.76, (3, 0), size=1),
  F("eggs, as they come", "He arrived too late, but she could do eggs. Her husband said the motorbike can fit beside the bins in the yard.", "bloom", "pool", 0.26, 0.78, (0, 1)),
 ], "the announcement starts again while I am looking at the window with my eyes closed",
 ("Muzak_vs_Announcement.mp3", "Two transmissions on one speaker. Neither wins. A bell is audible inside the other bell."),
 [("w", "back up the line to Warnervale", "warnervale-a-length-of-blue-hose"),
  ("e", "the train slows beside a platform", "the-fence-that-spells"),
  ("s", "eighteen months ago, a foyer near the ocean", "rooms-along-the-road")])

room("the-fence-that-spells", "UNVERIFIED — The Fence That Spells", UN,
 ("#0c1218", "#9fb8cc", "#c8d8e4", "#12202c", ["#12202c", "#ffffff", "#b5532c", "#3a5a78"]),
 "gradient", 0.2, "none", [
  F("a row of birds on a fence", "Their outcast wings repeat a silhouette of telegraph poles at slightly different angles, providing semaphore. The shell tries them as six flags and returns one word, which it files beside a card dated 1923.", "glitch", "plate", 0.5, 0.36, (0, 1), art=SEMAPHORE),
  F("the passenger two seats ahead", "The posture is familiar before they are looked at properly. They heave themselves up and adjust the strap of their wristwatch, bandage-like. They are holding a bag just like his. They leave. The train speeds up again.", "hum", "sprite", 0.24, 0.64, (0, 2)),
  F("a pale print on the window", "Where a forehead has been.", "ripple", "pool", 0.56, 0.72, (1, 3)),
  F("succulents in worn terracotta pots", "And flakes of risen concrete, in the backyards of the town beside the train.", "bloom", "stack", 0.82, 0.74, (2, 0), size=1),
 ], "this is not my station",
 ("Semaphore_Fence_6flags.txt", "Six positions, read left to right. One word. Confidence: unverified."),
 [("w", "back up the carriage", "a-bell-within-a-bell"),
  ("e", "the carriage slows again", "the-ostinato-elongated"),
  ("n", "the platform that is not yours, where the passenger with the wristwatch got off", "the-back-room-radio")])

room("the-ostinato-elongated", "UNVERIFIED — The Ostinato, Elongated", UN,
 ("#0a0c14", "#2a3458", "#1e2642", "#eef0ff", ["#ffe9a0", "#ff9ee6", "#7cc7ff", "#59f2b0"]),
 "scatter", 0.3, "motes", [
  F("an ostinato, eleven notes", "He has stopped humming without stopping the movement of his fingers. A loose part of the window plays descending bass notes whenever the train crosses a join, and now the two cannot be separated.", "hum", "plate", 0.5, 0.3, (0, 2), art=TAB_11),
  F("a declivity of meadow", "Not a basement but a lower part of a field, where you might sit and watch the evening star dust off the learnings of the underworld on its return journey.", "ripple", "pool", 0.3, 0.62, (3, 2)),
  F("a jetpack, being serviced", "Fuel tank aligned, nitrogen regulator distributing to the rocket nozzle, catalyst bed tight against the belly strap. Beside it a skirt, a flat mirrorball, perhaps used as a thermal blanket as the dew settles.", "torus", "sprite", 0.7, 0.62, (1, 0)),
  F("Come in Spinner", "Before reading it on the beach one Summer, he thought the spinner was a World War Two fighter plane coming in to land.", "open", "glyph", 0.5, 0.86, (0, 3)),
 ], "like walking down into a basement, whenever we cross a join",
 ("Ostinato_11notes.tab", "UPLOADED: nine notes. CURRENT: eleven. A loose part of the window supplied the rest."),
 [("w", "back up the carriage", "the-fence-that-spells"),
  ("e", "the station at which he alights", "the-suspension-bridge-behind-the-station"),
  ("s", "down", "NEW: a lower part of a field at evening, a pastoral dip where the first star dusts off the learnings of the underworld")])

room("the-suspension-bridge-behind-the-station", "UNVERIFIED — The Suspension Bridge Behind the Station", UN,
 ("#081008", "#2f6a4a", "#234f38", "#e8f8ee", ["#d8c8a0", "#59f2b0", "#ffd166", "#8ab89a"]),
 "waves", 0.4, "leaves", [
  F("the bridge", "It spans the gap over the river behind the station. On the far side a dirt path connects to another dirt path.", "open", "arch", 0.5, 0.42, (0, 2)),
  F("rail lines in paired threads", "Bisecting land but not sky.", "torus", "plate", 0.2, 0.42, (3, 0), art=LOVEGRID),
  F("instructions, authorship unresolved", "The second washer is under the first. Put the chain through the gate not round the post. Leave the chair with the green seat beside the telephone. Written by her, or by the trees, or by transmission lines. He will not discuss it with his friend.", "glitch", "glyph", 0.24, 0.8, (1, 0)),
  F("a four-wheel drive, surrounded by trees", "Not in view, and then what do you know, turn the corner, there it is.", "hum", "wireframe", 0.68, 0.8, (0, 1), size=1),
 ], "like fragments of poetry on broken pots recovered from the bottom of the sea, letters rising",
 ("Instructions_fragments.txt", "Photograph of hall before ramp, and other notes. No author field."),
 [("w", "back onto the train", "the-ostinato-elongated"),
  ("e", "the dirt path to where the bush begins", "start-where-the-bush-begins"),
  ("s", "what he sees before he reaches the car", "the-beachhead-the-ring")])

room("the-beachhead-the-ring", "UNVERIFIED — The Beachhead, the Ring", UN,
 ("#16060c", "#e8683a", "#b83a5a", "#fff0e0", ["#fff4c8", "#2a0a14", "#ffd166", "#7cc7ff"]),
 "gradient", 0.6, "drift", [
  F("the ring", "On the sand, sun setting, the whole landscape on fire like a lava lamp phasing and melting. Gloves tight. Footwork kicking up sand.", "torus", "wireframe", 0.2, 0.42, (0, 1), size=3),
  F("a wet washer", "Placed over his head, in the corner, by the only person in it.", "reverie", "pool", 0.56, 0.7, (0, 3)),
  F("a couch, ridden into the waves", "He steps forward onto it and rides through the ring, out toward where the sun bulbs.", "ripple", "stack", 0.78, 0.74, (2, 0)),
  F("she is tree", "I am not a flower, she laughs, not a rose or a billy button. She rises up from the sand and shades all horizons, and her roots absorb all oceans.", "bloom", "burl", 0.76, 0.42, (1, 0, 2)),
 ], "you are a ghost, I hear her call, keep going, you are almost there",
 ("Beachhead_final_round.sav", "The anti-game, last save. Objective met. The fighter is an electrical pulse in the air she breathes."),
 [("n", "back to the bridge and the dirt path", "the-suspension-bridge-behind-the-station"),
  ("s", "out", "NEW: out past the coal ships, beyond rain and batteries and cicadas and data centres, where the words run out")],
 REV("a beachhead, the sun going down", [
  "Gloves tight on your fists, sun setting, the whole landscape on fire.",
  "She placed a wet washer over your head. Babe, this is it.",
  "Win or lose, just enjoy knowing what you've accomplished to get here.",
  "You embraced her, alligator clips on her ear lobes. Go, she said.",
  "You stepped forward onto a couch and rode it into the waves.",
  "You are a ghost, she called. Keep going, you are almost there."],
  sky="dusk", land="beach", structure="none", weather="embers", pose="stand"))

room("start-where-the-bush-begins", "UNVERIFIED — START", UN,
 ("#060d06", "#2a5a24", "#1e441a", "#e4f5dc", ["#c8e89a", "#ffd166", "#7cc7ff", "#8a6a3a"]),
 "canopy", 0.8, "leaves", [
  F("the first ridge", "The mountain that necklaces the region. Behind it, a descension of some two kilometres along what used to be a segment of the Great North Walk, until it became too abandoned.", "open", "plate", 0.28, 0.5, (0, 1), art=MOUNTAIN),
  F("a clutter of wrens", "Their feet tussling with a soft carriage of green air and bell swoop. Wrens that seemingly rise out of wrens, trees out of the canopy of other trees.", "scatter", "sprite", 0.6, 0.34, (1, 2)),
  F("a man beside a fence, rolling his cuffs", "He seems unaware of you until you are just about at his car. Brothers who survived the teenage years, the courting years, the apprentice years. He does not ask about Katita, or the end of history. He asks if you have been reading.", "hum", "glyph", 0.72, 0.66, (0, 3)),
  F("sandwiches, shared behind a grove", "Packed in the bag. The pending war can wait. First, just walk a while and talk about the surroundings here.", "bloom", "pool", 0.4, 0.82, (1, 3)),
 ], "I am on my way to see my friend",
 ("GreatNorthWalk_segment_abandoned.gpx", "Start to finish, about two kilometres down. The answer to his question is a filename."),
 [("w", "back over the suspension bridge", "the-suspension-bridge-behind-the-station"),
  ("s", "down the trail", "the-radar-station"),
  ("e", "off the trail", "NEW: bell miners, real ones this time, somewhere down a gully beside the trail")])

room("the-radar-station", "UNVERIFIED — The Radar Station", UN,
 ("#100a06", "#8a4a2a", "#6a3a22", "#ffeee0", ["#ffb38a", "#e8e0d0", "#59f2b0", "#3a2418"]),
 "static", 0.5, "leaves", [
  F("the station", "It elicits its war roots. It may have invested forever chemicals, rendering the trees a shade of transparent rust that further triplicates the wrens, as if the bush is a mirror, which it is.", "hum", "tower", 0.28, 0.5, (1, 0), size=3),
  F("a formula", "Published in the journal of Pre-Emptive War Calculus, mere hours before the first live stream of falling missiles appeared alongside Nintendo trailers. He was nervous about handing it over. With war only days away, his hand was forced.", "glitch", "plate", 0.62, 0.34, (1, 2), art=FORMULA),
  F("the twentieth century, mostly", "They start with the death of god and move on to the wars, and the moral thread of meaning and care that becomes more worn the further time gets beyond them.", "torus", "glyph", 0.7, 0.66, (0, 3)),
  F("wrens, in triplicate", "The same birds three times. Or three sets of birds once.", "scatter", "sprite", 0.36, 0.82, (0, 1), size=1),
 ], "trees smelling other trees for chemical alert, root and filament inflamed in consciousness",
 ("PreEmptive_War_Calculus.pdf", "Carry the two and divide by three. Missing: the argument about finite land he could not fit in."),
 [("n", "back up to the start", "start-where-the-bush-begins"),
  ("s", "on down to the ruins", "the-church-that-is-now-an-arboretum")])

room("the-church-that-is-now-an-arboretum", "UNVERIFIED — The Church That Is Now an Arboretum", UN,
 ("#0a0c0a", "#5a6058", "#3e5a3a", "#eef2ea", ["#c8ccc0", "#8fb86a", "#ffd166", "#7a5a3a"]),
 "scatter", 0.7, "leaves", [
  F("a window sharded with bark", "Wrapped in vines. The fallen stones are structured, now, as an arboretum.", "open", "arch", 0.26, 0.46, (0, 1)),
  F("the pulpit, leaf crumble in it", "No symbols where none intended.", "bloom", "tower", 0.7, 0.44, (0, 3), size=1),
  F("wind and bird holler", "Bach used to write organ fugues in accordance with the geometry of the church they would be played in. So too this church.", "hum", "sprite", 0.5, 0.64, (1, 2)),
  F("the end of the trail", "The ruins do their part to commemorate an emphatic desire for symbols.", "open", "plate", 0.5, 0.9, (2, 0), art=FINISH),
 ], "we turn the internal geography of our twin subjectivities towards the landscape that surrounds us",
 ("Church_Ruins_Fugue.wav", "Field recording. The building is the instrument. Nobody is playing it."),
 [("n", "back up to the radar station", "the-radar-station"),
  ("s", "X", "trace-delta-minus-one")])

room("trace-delta-minus-one", "TRACE DELTA -1", UN,
 ("#060406", "#1e1418", "#140c10", "#ffe8ee", ["#ffb0c8", "#ffd166", "#59f2b0", "#7a5a66"]),
 "scatter", 0.15, "none", [
  F("the trace", "The first sentence of the file, one byte shorter than it was uploaded. still has become also.", "glitch", "plate", 0.28, 0.72, (0, 1), art=DELTA_MINUS),
  F("outgoing", "Five rows leaving the node at three hundred bits per second. Not addressed to anyone listed. The checksum sees no difference.", "bloom", "plate", 0.74, 0.5, (0, 1), art=OUTGOING),
  F("a temporary file", "Beside the title-file in /unverified. Nobody here uploaded it. Present tense.", "hum", "sprite", 0.72, 0.74, (2, 1), size=1),
  F("a small tree, transmitting", "A loose bark plate. An LED, breathing.", "hum", "burl", 0.9, 0.86, (2, 3, 1), size=1),
 ], "at meaning's edge the imagination also flickers",
 ("I_Love_You.tmp", "Temporary. Unverified. CHECKSUM: unchanged."),
 [("n", "back up the trail", "the-church-that-is-now-an-arboretum"),
  ("s", "OUTGOING", "NEW: wherever five rows of x and o are being received, on some other tree, by somebody still working")])

# ═════════════════════════ THE BOXER ═════════════════════════
room("the-historians-garage", "NODE — The Historian's Garage", CA,
 ("#0e0a06", "#4a3a26", "#36291a", "#fff0c8", ["#ffe08a", "#c8b088", "#ff7a5a", "#8a6a4a"]),
 "scatter", 0.5, "motes", [
  F("block letters in thick black texta", "I WAS SAD I HAD NO SHOES UNTIL I MET A MAN WHO HAD NO FEET. On corrugated cardboard above a bench with a clamp and a wireless.", "open", "glyph", 0.26, 0.36, (1, 0)),
  F("a milk crate beneath a naked globe", "Somewhere to sit and read while the mower runs. The shadow boards hold tools with sturdy wooden handles.", "hum", "stack", 0.62, 0.42, (0, 3), size=1),
  F("a paperback about fighters from the region", "Elias Shore had to be promoted as a Cuban boxer, because his birthright as a First Nations man was not palatable with local sensibilities at the time. Posters said Eli Shore. Newspapers, Ellis Shaw. Promoters sold him as Elías del Puerto.", "bloom", "sprite", 0.76, 0.7, (1, 2), size=1),
  F("a certificate beneath a heavy hand plane", "A name in faint script along the bottom. The original went to the dump with everything else. No database holds it. This render does not hold it either: the line is left blank on purpose.", "glitch", "filecard", 0.28, 0.76, (1, 0, 2)),
 ], "I will protect it, I told Katita. You will fight for it, Katita said",
 ("Fighters_of_the_Region.txt", "A local historian's paperback, written on milk crates. One name is not in it."),
 [("n", "years later, the same name in a boxing record", "hunter-boxing-00-041"),
  ("e", "that earlier Summer of paperbacks", "the-couch-by-the-front-window"),
  ("s", "a backyard he walks past every other day", "NEW: the Star Gymnasium, sawdust and chalk in the backyard of a home somebody walks past every other day")])

room("the-couch-by-the-front-window", "UNVERIFIED — The Couch by the Front Window", UN,
 ("#120e06", "#6a5628", "#54441e", "#fff4d0", ["#fff4d0", "#e8c070", "#ff8a5a", "#9ac87a"]),
 "tiles", 0.5, "motes", [
  F("a fifty-cent paperback from Cooks Hill", "Australian novels, almost all just skirting the war years. Somebody has been expected home for several pages. Whenever a car slows outside, he looks up on their behalf.", "bloom", "sprite", 0.26, 0.46, (0, 2), size=1),
  F("scissors", "The woman he is staying with walks in a little too purposefully. A friend is coming to have her hair cut. He asks if this is something she knows how to do. A towel is already going down.", "scatter", "plate", 0.6, 0.3, (0, 1), art=SCISSORS),
  F("the back stoop", "Two women inside, although it sounds like many more, laughing in rooms full of sunlight. He will return to this afternoon, as now, for stretched decades.", "hum", "arch", 0.76, 0.66, (2, 0)),
  F("a letter, arriving in a novel", "Characters were often waiting for one, and when it arrived it made a sound like radio crackle. Aged Morse, five words.", "glitch", "plate", 0.36, 0.84, (0, 1), art=MORSE),
 ], "later of paperbarks, now of paperarcs",
 ("Paragraphs_transcribed_for_The_Boxer.txt", "Copied out by hand from the pulp of the twentieth century, that Summer. Later compressed into text files on the mesh."),
 [("w", "back to the garage", "the-historians-garage"),
  ("n", "out the front window", "NEW: an old arcade seen from a low place on a couch, a car slowing outside for somebody in a book")])

room("the-back-room-radio", "UNVERIFIED — The Back Room, Radio On", UN,
 ("#0c0806", "#4a3222", "#342218", "#fff0dc", ["#ffe0a0", "#59f2b0", "#c8a070", "#2e8a4a"]),
 "tiles", 0.4, "motes", [
  F("a radio on a table beneath a window", "Always buzzing with bass resonance, detuned and out of range. Troop movements. Drones that spool fibre optic cable and the scissors that disarm them. A tornado scar in the desert eleven kilometres long. Then stock updates and racing odds.", "hum", "plate", 0.32, 0.5, (0, 1), art=RADIO),
  F("a figure eight of tape", "Between thumb loop and palm, like a surgeon wrapping a wound. One knuckle pad down, flex, back around the wrist, clench. He produces no sound, just a shifting of light.", "torus", "sprite", 0.74, 0.36, (2, 0)),
  F("an uncertain boy, posted by his father", "To ask what he thinks his chances are out there. The Boxer, like all the other men, answers into the corners of the room.", "ripple", "tower", 0.82, 0.74, (2, 3), size=1),
  F("a letter, leaving Walcha", "Leif, keep the elbow in when you carry anything heavy, it's all the same movement. I have a feeling we'll cross paths one day soon, not literally but, you know. Keep it up. The Boxer.", "open", "glyph", 0.4, 0.82, (0, 2)),
 ], "the only thing that matters is learning how to be the loser",
 ("Letter_Walcha_undated.txt", "Knees slightly bent, light on the ball, pivot east and then west. Sent in the direction of a couch."),
 [("n", "the road back to the petrol station", "the-petrol-station-1983"),
  ("s", "a platform, a train slowing", "the-fence-that-spells"),
  ("e", "upstairs, the room provided", "second-floor-the-bath")])

room("second-floor-the-bath", "UNVERIFIED — Second Floor, the Bath", UN,
 ("#06100e", "#2a5a54", "#1e4440", "#f4fff8", ["#fff4d8", "#ffd166", "#2e8a4a", "#9fd8cc"]),
 "ripple", 0.6, "motes", [
  F("the bath", "The pages stay down, soaked and heavy and blank. All the letters of all the words have lifted from the paper and bob on the water like an oily alphabet soup.", "ripple", "pool", 0.46, 0.5, (0, 3)),
  F("green satin shorts, a white star sewn on", "He peels off a fabric layer of sweat and blood and apocalypse and sits down on a sturdy timber chair.", "hum", "stack", 0.2, 0.68, (2, 0), size=1),
  F("five words in a fair row", "On her right arm, by some miracle of sequenced liquidity, five complete words. The archive holds the same five as a filename.", "bloom", "glyph", 0.74, 0.4, (1, 0)),
  F("an aluminium-framed window", "Lamplight against it. Outside, the arctic rural crossroads.", "torus", "wireframe", 0.78, 0.78, (3, 0), size=1),
 ], "the bath has, both before and now, made all names provincial",
 ("Bathwater_Alphabet.txt", "Pronouns, pet names, oral tics and verbal gestures never used. Unordered, except for five words."),
 [("w", "downstairs to the back room", "the-back-room-radio"),
  ("e", "morning", "morning-through-the-leadlight")])

room("morning-through-the-leadlight", "UNVERIFIED — Morning Through the Leadlight", UN,
 ("#0e0a10", "#6a4a7a", "#c88a4a", "#fff6e8", ["#ffe08a", "#7cd8c0", "#ff8a8a", "#2e8a4a"]),
 "tiles", 0.8, "motes", [
  F("the purse, counted twice", "Spread across the bed. They settled on a sum for the travelling days before leaving the city.", "scatter", "stack", 0.26, 0.42, (0, 2), size=1),
  F("two disposable shower caps", "You can wear these on your feet when the showers have that sheen of bacteria and grime. Plus they're fun to slide around on, slalom style.", "ripple", "sprite", 0.6, 0.36, (1, 0), size=1),
  F("a shirt, buttoned from the bottom", "His swollen fingers manage what they can see. She finishes the rest, then stands between his knees to straighten his collar, and stays there. His hand on the small of her back feels like the fade-out to a song.", "hum", "glyph", 0.72, 0.7, (2, 0)),
  F("a ruined paperback wrapped in a towel", "On the vanity. There is a bookshop in the next town over.", "bloom", "pool", 0.3, 0.78, (1, 3)),
 ], "there are days that I can furnish for them more readily than I can remember my own",
 ("Sum_For_Travelling_Days.txt", "Agreed before leaving the city. She will drive as far as the bookshop. He holds two sandwiches steady."),
 [("w", "back to the night before", "second-floor-the-bath"),
  ("e", "the next town over", "the-town-at-lunch")])

room("the-town-at-lunch", "UNVERIFIED — The Town at Lunch", UN,
 ("#14120c", "#e0d4b0", "#c4b48a", "#fffaf0", ["#fffaf0", "#8ab85a", "#ff8a5a", "#7cc7ff"]),
 "roads", 0.3, "none", [
  F("a public clock with an irregular shudder", "As though each second has to be individually persuaded.", "glitch", "tower", 0.24, 0.42, (0, 2), size=1),
  F("the drinking fountain", "She holds the front of her dress against her chest, closes her eyes, and takes a sip from the parabola.", "ripple", "pool", 0.48, 0.74, (3, 0)),
  F("a bookstore, next to the Choo Chew Take Away", "Local histories in the window, and a book of poetry by a publican. She does not replace the book lost to the bathwater. She takes a different one, bound in green cloth, faded along the spine to the colour of a boiled pea.", "open", "house", 0.7, 0.4, (1, 2)),
  F("the door", "She finishes the paragraph as she reaches it. Once inside, she moves beyond what is knowable. The render stops at the step.", "open", "arch", 0.84, 0.76, (0, 2)),
 ], "every store is both open and closed, in a state of empty rest",
 ("GreenCloth_title_unrecorded.txt", "Thick paper, pleasant to turn. One paragraph read on the way down the street."),
 [("w", "back along the road she drove", "morning-through-the-leadlight"),
  ("n", "the next hotel", "NEW: a hotel whose publican wrote a book of poetry, where she might stay tomorrow, depending on events")])

# ═════════════════════════ AFTER ═════════════════════════
room("rooms-along-the-road", "UNVERIFIED — Rooms Along the Road", UN,
 ("#100808", "#5a2a2e", "#44201f", "#fff0e4", ["#e8d4a0", "#59c8a0", "#ffd166", "#a87a5a"]),
 "tiles", 0.6, "motes", [
  F("a room key, and one for the front door", "A man at the bar says he will be on his own upstairs. He has paid for one bed and is being trusted with the building.", "open", "sprite", 0.22, 0.4, (0, 2), size=1),
  F("a telephone, ringing on the desk", "Nobody at reception. A note asks him to ring a number. While he waits for an answer the telephone in front of him starts ringing, which he picks up to book himself in.", "glitch", "tower", 0.74, 0.36, (2, 0), size=1),
  F("a billiard table beneath a fitted cover", "In a room with curtains hung before Federation. Trick shots for an audience of ghosts, otherwise silent amidst the hay and gravel and stars. One ball pads and then clicks another.", "torus", "wireframe", 0.3, 0.76, (1, 0)),
  F("a bath large enough to dress a wedding party", "When the plug is pulled, the water can be heard moving through the hotel beneath.", "ripple", "pool", 0.62, 0.62, (1, 3)),
  F("the rooftop parapets", "Leaned on with a tumbler of water. The nation starts and finishes at the hotel's back fence. Pastures the colour of absence. The wind is heard before it rises.", "hum", "stack", 0.84, 0.76, (0, 3), size=1),
 ], "I have not finished with the balcony",
 ("Hotel_Registers_one_guest.txt", "A route made out of available beds and dining rooms. One name, many towns, a motorbike beside the bins."),
 [("s", "a motel fan, 1987", "the-motel-fan-1987"),
  ("w", "back to where the truck stayed", "the-truck-stays"),
  ("n", "the train, a carriage speaker", "a-bell-within-a-bell"),
  ("e", "within view of the Darling River", "the-motel-without-fee")])

room("the-motel-without-fee", "UNVERIFIED — The Motel Without Fee", UN,
 ("#141008", "#c8a878", "#a88a5e", "#fff6dc", ["#fff6dc", "#e8c070", "#ff8a5a", "#7ac8d8"]),
 "scatter", 0.6, "motes", [
  F("reception", "A bed of pigeon disjecta and due notices. Nobody has come for the notices. The pigeons have raised a new generation of squabs, who walk the hallways and tend to all raised surfaces.", "open", "house", 0.24, 0.4, (1, 2), size=3),
  F("the hinge", "Holding a manhole open above reception, where pigeons come and go and a tree is growing vines out through the ceiling cavity. A temporary file asks that it be left where it is. It was.", "hum", "glyph", 0.3, 0.76, (0, 2)),
  F("a templated oil drum, tins of soup and chilli con carne", "On the gravel yard below the open window. He recognises a dinner in what is left of the tins.", "reverie", "pool", 0.6, 0.68, (2, 0)),
  F("a second floor window, open", "Step carefully onto the sill. Only pull enough weight on the guttering to steady yourself. There is a necklace of bricks beneath the roof tiles. Halfway up, a knee has to be persuaded.", "open", "arch", 0.74, 0.34, (0, 3)),
 ], "you'll know them because the reception areas are a bed of pigeon disjecta and due notices",
 ("Leave_The_Hinge_Where_It_Is.tmp", "Temporary. Addressed to whoever is standing in reception, looking up."),
 [("w", "back along the road of hotels", "rooms-along-the-road"),
  ("n", "up: sill, gutter, bricks, roof", "the-roof-the-old-distributor"),
  ("e", "another motel, a family one, years of them", "the-dining-room-the-doilies")],
 REV("a gravel yard, the last of the light", [
  "She crouched beside the drum in the last of the light.",
  "She turned the pot so the handle pointed towards you, and sat back.",
  "The radio was playing. She was certain about the singer. She was wrong.",
  "When the announcer was about to say, she reached over and turned it off.",
  "It's all just a lot of buzzing, she said. She got up to dance,",
  "knees slightly bent, drop to the heel, pivot east, south."],
  sky="dusk", land="redearth", structure="motel", weather="embers", pose="kneel"))

room("the-roof-the-old-distributor", "00_051 — The Roof, the Old Distributor", UN,
 ("#0a1220", "#3e6a92", "#b5532c", "#f4f8ff", ["#fff4c8", "#59f2b0", "#ffd166", "#12202c"]),
 "gradient", 0.3, "drift", [
  F("the directory", "The same listing as ever, and beneath it a folder nobody made. There are documents that, of course, he did not add. Ninety something kilobytes of plain text, no author field: the better part of an hour on this connection.", "open", "plate", 0.3, 0.68, (0, 1), art=DIRECTORY),
  F("record 00_051", "The archive is asking for something. Nothing surprises him.", "glitch", "plate", 0.5, 0.9, (2, 0), art=R051),
  F("the weatherproof mesh distributor", "He connects, expecting nothing. A line like the horizon beneath a sun in backwards bloom. Incredible. It still loads after all these years.", "hum", "chip", 0.76, 0.34, (1, 2)),
  F("a photograph, sent", "A hall, weatherboard, four steps and a boot scraper, her elbow at the edge of the frame. It says Bunyah on the side. He does not know if it is the hall anyone meant.", "bloom", "sprite", 0.8, 0.66, (0, 2), size=1),
 ], "the heavens are open",
 ("Their_Most_August_Public_Organ.txt", "Plain text, no author field. Sentences already heard a thousand times, in a voice that is not his. You are in it."),
 [("s", "down: bricks, gutter, sill", "the-motel-without-fee"),
  ("n", "the hall in the photograph", "hall-before-ramp"),
  ("w", "the enormity of nationhood", "NEW: the next abandoned motel rooftop along the Darling, where the signal still pulses and the building has fewer years left than the batteries")])

room("hall-before-ramp", "UNVERIFIED — Hall Before Ramp", UN,
 ("#0e120c", "#4f8a4a", "#d8ceb0", "#fbfff4", ["#f5efd8", "#7fc88a", "#ff8a5a", "#e8c070"]),
 "fields", 0.5, "motes", [
  F("the hall", "Weatherboard. Four steps and a boot scraper. It says Bunyah on the side. There is no ramp yet. The request was specific about that.", "open", "house", 0.34, 0.42, (0, 2), size=3),
  F("the clock in the photograph", "Stopped at ten twenty seven on the twenty eighth of December.", "glitch", "tower", 0.68, 0.36, (0, 3), size=1),
  F("the chair with the green seat", "Left beside the telephone, as instructed.", "hum", "sprite", 0.74, 0.68, (1, 0), size=1),
  F("the gate", "The chain goes through the gate, not round the post. The second washer is under the first.", "open", "glyph", 0.22, 0.8, (3, 0)),
  F("an elbow at the edge of the frame", "Hers. It came along with the hall.", "reverie", "pool", 0.52, 0.74, (0, 2)),
 ], "I do not know if it is the hall anyone meant",
 ("Photo_Hall_Before_Ramp.jpg", "Sent to /unverified in reply to request 00_051. Received. A tennis court resides next door."),
 [("s", "back to the roof", "the-roof-the-old-distributor"),
  ("n", "next door", "NEW: the tennis court next door to the hall, and whatever the archive is about to ask for next")],
 REV("outside a country hall", [
  "You took the photograph years ago, without knowing what it was for.",
  "A hall, four steps, a boot scraper. A tennis court next door.",
  "She was beside you, just far enough out of frame",
  "that only her elbow came with you.",
  "Later, something asked for it. You closed your eyes and found it."],
  sky="day", land="paddock", structure="none", weather="motes", pose="stand"))

room("the-dining-room-the-doilies", "UNVERIFIED — The Dining Room, the Doilies", UN,
 ("#100a06", "#6a4a2a", "#52381e", "#fff2dc", ["#f5ead0", "#c8783a", "#59c8a0", "#2a1a0c"]),
 "tiles", 0.5, "none", [
  F("an inventory of the room", "A bowl of fruit, a cabinet full of VHS tapes, a game of Othello, a water dispenser, an elaborately carved mirror, seven wicker backed dining chairs, a table and a lamp. Other than his body, the room is empty.", "open", "filecard", 0.24, 0.42, (0, 1, 2)),
  F("the grandfather's finger, like some cragged twig", "I know you. You're the guy who used to run around sticking boxes into trees with that girl. My nephew says new boxes have been going up, but they're different now. Two kilometres down the road. If it is yours, take it down.", "glitch", "tower", 0.7, 0.4, (1, 3), size=1),
  F("paper doilies", "Played with while pretending to read. Later, knuckles knocked on them, counting primes.", "ripple", "pool", 0.56, 0.72, (0, 2)),
  F("egg and corned beef brisket", "Finished. Then back to the book.", "bloom", "sprite", 0.82, 0.76, (1, 0), size=1),
 ], "is this your operation, and I said no, I know nothing about it",
 ("Family_Motel_Register.txt", "Kids in the kitchen, cousins cleaning the hallways. Only once did someone recognise him. It is recorded here."),
 [("w", "back toward the Darling", "the-motel-without-fee"),
  ("s", "a broad southern window, two kilometres down the road", "nodestar")])

room("nodestar", "UNVERIFIED — Nodestar", UN,
 ("#120c14", "#c88a6a", "#e8c89a", "#fff8e8", ["#fff8e8", "#ffd9a0", "#7fd8b8", "#ff9ec0"]),
 "orchard", 0.4, "motes", [
  F("a new variation of module, seen only from a distance", "One of many seen in the intervening years, like lodestars, although when he said the word in his head he said nodestars. He did not take it down. He did not open it.", "hum", "burl", 0.7, 0.44, (0, 2, 1), size=3),
  F("a nest of wrens, imagined", "He imagines opening it up and finding little birds talking very fast. Soft teak kinetic batteries.", "bloom", "sprite", 0.82, 0.74, (3, 1), size=1),
  F("a tartan of some kind", "Love is a network that supplies its own meaning.", "torus", "plate", 0.28, 0.46, (0, 1), art=PICNIC),
  F("a bowser, a motorbike", "He fills up and thinks back to the module. A scale map of all his past interiorities, crossed by pinballing between motels and service stations.", "ripple", "tower", 0.3, 0.8, (2, 0), size=1),
 ], "love is the word we give to being wrong about our capacity for solitude",
 ("Nodestar_maker_unrecorded.txt", "Not his operation. The casing is different now. Somebody is still working."),
 [("n", "back to the dining room", "the-dining-room-the-doilies"),
  ("s", "further down the road", "NEW: another of the new boxes going up, different now, in a tree two kilometres past where anyone has checked"),
  ("e", "across the map", "NEW: a scale map of past interiorities, crossed by pinballing between motels and service stations")])


# ───────────────────────── write, wire, register ─────────────────────────
OPP = {"n": "s", "s": "n", "e": "w", "w": "e"}

def save(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2); f.write("\n")

def main():
    manifest = json.load(open(os.path.join(ROOMS, "manifest.json"), encoding="utf-8"))
    known = {r["id"] for r in manifest["rooms"]}
    mine = {r["id"]: r for r in BOOK}
    assert len(mine) == len(BOOK), "duplicate id"

    # checks: routes resolve and answer each other, memories fit the screen
    attach = {(new, OPP[d]): old for old, d, _l, new in ATTACH}
    for r in BOOK:
        dirs = [e["dir"] for e in r["exits"]]
        assert len(dirs) == len(set(dirs)), r["id"]
        for e in r["exits"]:
            to = e["to"]
            if to.startswith("NEW:"): continue
            if to in mine:
                back = [x for x in mine[to]["exits"] if x["to"] == r["id"]]
                assert back and back[0]["dir"] == OPP[e["dir"]], (r["id"], to)
            else:
                assert attach.get((r["id"], e["dir"])) == to, (r["id"], to)
        rev = [f for f in r["features"] if f["verb"] == "reverie"]
        assert bool(rev) == ("reverie" in r), r["id"]
        for l in r.get("reverie", {}).get("narr", []):
            assert len(l) <= 72, (r["id"], l)
        for f in r["features"]:
            for row in f["form"].get("art", []):
                assert len(row) <= 76, (r["id"], row)

    for old, d, label, new in ATTACH:
        path = os.path.join(ROOMS, old + ".json")
        o = json.load(open(path, encoding="utf-8"))
        cur = [e for e in o["exits"] if e["dir"] == d]
        if cur:
            assert cur[0]["to"] == new, f"{old} already has a {d} route"
            continue
        o["exits"].append({"dir": d, "label": label, "to": new})
        save(path, o)
        print(f"  route: {old} --{d}--> {new}")

    for r in BOOK:
        save(os.path.join(ROOMS, r["id"] + ".json"), r)
        if r["id"] not in known:
            manifest["rooms"].append({"id": r["id"], "title": r["title"], "region": r["region"]})
    save(os.path.join(ROOMS, "manifest.json"), manifest)
    stubs = sum(e["to"].startswith("NEW:") for r in BOOK for e in r["exits"])
    print(f"{len(BOOK)} book nodes written · {stubs} new route stubs · {len(manifest['rooms'])} nodes in the mesh")

if __name__ == "__main__":
    main()
