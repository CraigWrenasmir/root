# ROOT

**A diagnostic render of a tree archive that grows itself every night.**

Solar-powered memory casings hidden in the burled knots of trees across
regional New South Wales, each broadcasting a public archive at 300 bits
per second. The corruption is not data loss. It is meaning-production:
the network has begun comparing things.

You are **the Reader** — the barely-3D wireframe figure the diagnostic
shell renders to stand for whoever is currently reading the archive.
`STATUS: BEING READ`. Wander node to node, query what you find, and
download each node's file at 300bps into your `/ROOT` listing. Routes the
mesh hasn't grown yet end mid-air; step off one and you get
`NODE UNREACHABLE — return after the next night.` Each night the growth
engine grows those nodes into being.

From the ROOT layer of the novel-in-progress
[*Their Most August Public Organ*](https://novel.wrenasmir.com) by
C. W. Smith. Built on the same self-growing engine as
[Dreamring](https://craigwrenasmir.github.io/dreamring/) and sibling to
[Surgipelago](https://surgipelago.wrenasmir.com).

## Play

```
python3 -m http.server 8041
# → http://localhost:8041
```

Arrows / WASD move · **Space** query · **Tab** /ROOT listing · **Q** sound.

## How it grows

- `rooms/*.json` — every node is one JSON file: palette, ground motif,
  weather, features (procedural forms including tree burls, wireframe
  low-poly objects, and standing file listings), an inscription, a file,
  and routes.
- Routes whose `to` begins `NEW: <hint>` are stubs — the mesh's growing
  edge. `engine/grow.py` (stateless `claude -p`, Haiku, on the Max
  subscription — no API key) grows nodes for a batch of stubs each night,
  repairs and validates the JSON, and wires routes both ways. Every new
  node must leave at least one new stub.
- `./grow.sh [count]` — one night: grow + commit + push. Sometimes it also
  renovates: a route that was not there yesterday appears on an old node.
- `index.html` — the whole game engine, no dependencies, no build step;
  all art generated at runtime from seeded JSON.

*ROOT is a work of fiction growing out of a work of fiction.*
