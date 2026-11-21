# Live at The Oak - Lite

A pixel-art, three-song cut of Wrenasmir's *Live at The Oak* rhythm game
(full game: theoak.wrenasmir.com), made to be embedded in **Play Newcastle**
as the thing you do when you walk into The Oak.

- Three 90-second cuts: **Rdst Gm**, **Crafluropi**, **Mabon**, Standard and Hard.
- Same four lanes, shapes, timing windows, combo multiplier and hold notes as the full game.
- 180px-tall canvas scaled by whole numbers; landscape and portrait layouts.
- No dependencies, no build step, no network calls. About 4.4 MB, nearly all of it the three mp3s.

Try it on its own: `python3 -m http.server 8151` in this folder, open
`http://localhost:8151/`. Add `?bot` to watch it play itself.

## Embedding (notes for Codex)

Copy `oak-lite.js`, `oak-lite-songs.js` and `audio/` into the Play Newcastle project.

```html
<script src="oak-lite/oak-lite-songs.js"></script>
<script src="oak-lite/oak-lite.js"></script>
```

```js
// Call from the player's interact/click handler so the browser allows audio.
const gig = OakLite.mount(overlayEl, {
  audioBase: "oak-lite/audio/",        // folder holding <slug>.mp3, trailing slash
  onResult: r => { /* after each song: r.score, r.grade (S-D), r.accuracy, r.maxCombo, r.fullCombo, r.newBest */ },
  onExit:   r => { /* player chose "Leave the stage": r.results is every song played this visit */ }
});
```

`overlayEl` is any sized element (a full-screen overlay div works well); the
game fills it and letterboxes itself. On exit it removes its canvas, listeners
and audio before calling `onExit`, so the host only needs to hide the overlay
and hand control back to the player.

Things the host should do:

- **Pause Play Newcastle's own input and music while mounted.** OakLite listens
  for keys on `window` in the capture phase and stops propagation of the keys it
  uses (D F J K, arrows, Enter, Space, Esc, P), but a host listener registered
  earlier in the capture phase would still fire.
- Don't call `mount` on page load; the first song needs a user gesture for audio.

Options (all optional): `audioBase`, `onResult`, `onExit`, `keys` (four
`KeyboardEvent.code`s, default D F J K; arrow keys always work too),
`palette` (override any colour in `DEFAULT_PALETTE` at the top of
`oak-lite.js` to match Play Newcastle's art), `volume` (0-1),
`audioContext` / `destination` (share the host's Web Audio graph),
`audioOffset` (seconds, default 0.15, carried over from the full game),
`autoplay` (bot plays; useful for an attract mode).

Returned handle: `destroy()`, `pause()`, `play(songIndex, "standard" | "hard")`,
`screen`, `results`, `canvas`.

Best scores, difficulty and the timing nudge persist in `localStorage` under `oaklite.*`.

## Rebuilding the clips

`tools/build_songs.py /path/to/Live-at-The-Oak` recuts `audio/*.mp3` and
`oak-lite-songs.js` from the full game's audio and charts (needs ffmpeg).
Change `PICKS` in that file to swap songs or clip lengths.
