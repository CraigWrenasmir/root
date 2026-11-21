/* Live at The Oak - Lite
 * A pixel-art, three-song cut of Wrenasmir's Live at The Oak rhythm game,
 * built to be embedded inside another game (Play Newcastle, in The Oak).
 *
 *   <script src="oak-lite-songs.js"></script>
 *   <script src="oak-lite.js"></script>
 *   const gig = OakLite.mount(containerEl, { audioBase: "oak-lite/audio/", onExit: r => {...} });
 *   gig.destroy();
 *
 * No dependencies. Everything is drawn in code on one low-res canvas; all
 * gameplay time comes from AudioContext.currentTime, as in the full game.
 */
(function () {
"use strict";

var LANE_COLORS = ["#3ec54b", "#e04a3a", "#e8c53a", "#3a7de0"];
var LANE_DARK = ["#1c6b25", "#7d231b", "#8a7216", "#1c4287"];
var WINDOWS = { perfect: 0.045, great: 0.090, ok: 0.130 };   // seconds, same as the full game
var POINTS = { perfect: 100, great: 60, ok: 30 };
var LOOKAHEAD = 1.6;       // seconds of highway visible
var LEAD_IN = 2.2;         // silence before the song starts
var GRADE_COLORS = { perfect: "#7ee787", great: "#e8c53a", ok: "#b8a98f", miss: "#e04a3a" };

var DEFAULT_PALETTE = {
  ink: "#0d090b", wall: "#1c1216", brick: "#26181c", cream: "#e8ddc9", dim: "#8d7f72",
  wood: "#6b4a2f", woodDark: "#3f2a1c", rug: "#8a2a22", rugDark: "#5e1b17",
  skin: "#d9a066", tee: "#7d8794", teeDark: "#5e6773", khaki: "#a08a4f", khakiDark: "#7d6a3a",
  hat: "#d9bf8a", hatDark: "#a88d5c", head: "#e8cdb5", headDark: "#c9a98f",
  yellow: "#e8c53a", sign: "#f2c14e", signHot: "#fff0b8", shoe: "#6b7785",
  crowdBack: "#1a1114", crowdFront: "#0d090b", highway: "rgba(16,10,13,0.9)"
};

/* 3x5 pixel font: 15 bits per glyph, row by row */
var FONT = {
  A: "010101111101101", B: "110101110101110", C: "011100100100011", D: "110101101101110",
  E: "111100110100111", F: "111100110100100", G: "011100101101011", H: "101101111101101",
  I: "111010010010111", J: "001001001101010", K: "101101110101101", L: "100100100100111",
  M: "111111101101101", N: "110101101101101", O: "010101101101010", P: "110101110100100",
  Q: "010101101110011", R: "110101110101101", S: "011100010001110", T: "111010010010010",
  U: "101101101101111", V: "101101101101010", W: "101101101111111", X: "101101010101101",
  Y: "101101010010010", Z: "111001010100111",
  0: "111101101101111", 1: "010110010010111", 2: "110001010100111", 3: "110001010001110",
  4: "101101111001001", 5: "111100110001110", 6: "011100111101111", 7: "111001010010010",
  8: "111101111101111", 9: "111101111001110",
  ".": "000000000000010", ",": "000000000010100", "!": "010010010000010", "?": "110001010000010",
  "-": "000000111000000", "+": "000010111010000", ":": "000010000010000", "/": "001001010100100",
  "%": "101001010100101", "'": "010010000000000", "<": "001010100010001", ">": "100010001010100"
};

/* one silhouette per lane so colour is never the only signal:
   green circle, red diamond, yellow square, blue triangle (as in the full game) */
var GEM_ROWS = [[5, 7, 9, 9, 9, 7, 5], [1, 5, 7, 9, 7, 5, 1], [9, 9, 9, 9, 9, 9, 9], [1, 3, 5, 5, 7, 9, 9]];

function hash(a, b) {
  var h = (Math.imul(a | 0, 374761393) + Math.imul(b | 0, 668265263)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}
function store(key, val) {
  try {
    if (val === undefined) return JSON.parse(localStorage.getItem("oaklite." + key));
    localStorage.setItem("oaklite." + key, JSON.stringify(val));
  } catch (e) { /* storage is a nicety, never required */ }
  return null;
}

function mount(container, opts) {
  opts = opts || {};
  var SONGS = opts.songs || window.OakLiteSongs;
  if (!SONGS || !SONGS.length) throw new Error("OakLite: load oak-lite-songs.js before mounting");
  var P = {}, k;
  for (k in DEFAULT_PALETTE) P[k] = DEFAULT_PALETTE[k];
  for (k in (opts.palette || {})) P[k] = opts.palette[k];
  var audioBase = opts.audioBase == null ? "audio/" : opts.audioBase;
  var audioOffset = opts.audioOffset == null ? 0.15 : opts.audioOffset;  // Craig's measured audio-vs-tiles offset
  var laneKeys = opts.keys || ["KeyD", "KeyF", "KeyJ", "KeyK"];
  var altKeys = ["ArrowLeft", "ArrowDown", "ArrowUp", "ArrowRight"];
  var keyLabels = laneKeys.map(function (c) { return c.replace("Key", "").replace("Digit", "").slice(0, 1); });

  var cv = document.createElement("canvas");
  cv.style.cssText = "display:block;margin:auto;image-rendering:pixelated;image-rendering:crisp-edges;" +
    "touch-action:none;user-select:none;-webkit-user-select:none;outline:none;";
  var wrap = document.createElement("div");
  wrap.style.cssText = "position:absolute;inset:0;display:flex;align-items:center;justify-content:center;" +
    "background:" + P.ink + ";overflow:hidden;";
  if (getComputedStyle(container).position === "static") container.style.position = "relative";
  wrap.appendChild(cv); container.appendChild(wrap);
  var g = cv.getContext("2d");

  /* ---------------- layout ---------------- */
  var W = 320, H = 180, portrait = false;
  var SW, SH, CX, SY, FEET, CROWD_H;          // scene: width, height, centre x, stage y, feet y
  var HX, LW, HTOP, HIT_Y, GS;                // highway: left x, lane width, top, hit line, gem scale
  var bg = document.createElement("canvas");
  var beamPat = [];

  function layout() {
    var cw = Math.max(1, wrap.clientWidth), ch = Math.max(1, wrap.clientHeight);
    portrait = ch > cw * 1.1;
    if (portrait) {
      W = 180; H = Math.max(280, Math.min(400, Math.round(180 * ch / cw)));
      SW = W; SH = 120; CROWD_H = 18;
      LW = 42; HX = 6; HTOP = SH; HIT_Y = H - 30; GS = 2;
    } else {
      H = 180; W = Math.max(260, Math.min(400, Math.round(180 * cw / ch)));
      LW = 24; HX = W - 8 - LW * 4; HTOP = 0; HIT_Y = H - 24; GS = 1;
      SW = HX - 2; SH = H; CROWD_H = 28;
    }
    CX = Math.floor(SW / 2); SY = SH - CROWD_H - 22; FEET = SY + 8;
    cv.width = W; cv.height = H;
    var s = Math.min(cw / W, ch / H);
    if (s >= 1) s = Math.floor(s);            // whole-number scaling keeps the pixels square
    cv.style.width = Math.round(W * s) + "px"; cv.style.height = Math.round(H * s) + "px";
    g.imageSmoothingEnabled = false;
    buildBackground();
  }

  function buildBackground() {
    bg.width = W; bg.height = SH;
    var b = bg.getContext("2d"), x, y, i;
    b.fillStyle = P.wall; b.fillRect(0, 0, W, SH);
    b.fillStyle = P.brick;                                     // brick courses
    for (y = 0; y < SY; y += 6) {
      b.fillRect(0, y, W, 1);
      for (x = (y / 6) % 2 ? 0 : 7; x < W; x += 14) b.fillRect(x, y, 1, 6);
    }
    var posters = [[CX - 62, 44, "#3a7de0"], [CX + 48, 40, "#e04a3a"]];   // gig posters
    for (i = 0; i < posters.length; i++) {
      x = posters[i][0]; y = posters[i][1];
      if (x < 2 || x + 14 > SW - 2 || y + 18 > SY - 4) continue;
      b.fillStyle = P.cream; b.fillRect(x, y, 14, 18);
      b.fillStyle = posters[i][2]; b.fillRect(x + 2, y + 2, 10, 8);
      b.fillStyle = P.dim; b.fillRect(x + 2, y + 12, 10, 1); b.fillRect(x + 2, y + 14, 7, 1);
    }
    b.fillStyle = P.ink; b.fillRect(0, 4, W, 2);              // lighting truss
    b.fillStyle = P.woodDark; b.fillRect(CX - 35, 12, 70, 17); // sign board
    b.fillStyle = P.ink; b.fillRect(CX - 33, 14, 66, 13);
    b.fillStyle = P.wood; b.fillRect(0, SY, W, 14);           // stage boards
    b.fillStyle = P.woodDark;
    for (x = 6; x < W; x += 16) b.fillRect(x, SY, 1, 14);
    b.fillStyle = P.rug; b.fillRect(CX - 34, SY + 3, 68, 9);   // the red rug
    b.fillStyle = P.rugDark; b.fillRect(CX - 34, SY + 11, 68, 1); b.fillRect(CX - 32, SY + 5, 64, 1);
    b.fillStyle = P.woodDark; b.fillRect(0, SY + 14, W, SH - SY - 14);   // stage front
    b.fillStyle = P.ink; b.fillRect(0, SY + 14, W, 1);
    b.fillStyle = "#2b2226"; b.fillRect(CX + 15, FEET - 17, 15, 17);      // amp
    b.fillStyle = P.ink; b.fillRect(CX + 17, FEET - 12, 11, 10);
    b.fillStyle = "#3a2e33";
    for (y = FEET - 11; y < FEET - 3; y += 2) b.fillRect(CX + 18, y, 9, 1);
    b.fillStyle = P.sign; b.fillRect(CX + 26, FEET - 15, 1, 1);
    b.fillStyle = P.hat; b.fillRect(CX - 29, FEET - 21, 17, 2);           // laptop table
    b.fillStyle = P.dim; b.fillRect(CX - 27, FEET - 19, 1, 19); b.fillRect(CX - 15, FEET - 19, 1, 19);
    b.fillStyle = P.headDark; b.fillRect(CX - 26, FEET - 22, 11, 1);      // laptop base
    for (i = 0; i < 4; i++) {                                             // dithered beam patterns
      var pc = document.createElement("canvas"); pc.width = pc.height = 2;
      var pg = pc.getContext("2d"); pg.fillStyle = LANE_COLORS[i];
      pg.fillRect(0, 0, 1, 1); pg.fillRect(1, 1, 1, 1);
      beamPat[i] = g.createPattern(pc, "repeat");
    }
  }

  /* ---------------- drawing helpers ---------------- */
  function rect(x, y, w, h, c) { g.fillStyle = c; g.fillRect(x | 0, y | 0, w | 0, h | 0); }
  function textW(s, sc) { return String(s).length * 4 * (sc || 1) - (sc || 1); }
  function text(s, x, y, c, sc, align) {
    s = String(s).toUpperCase(); sc = sc || 1;
    var w = textW(s, sc), i, r, col, gl;
    x = Math.round(align === "center" ? x - w / 2 : align === "right" ? x - w : x);
    g.fillStyle = c;
    for (i = 0; i < s.length; i++, x += 4 * sc) {
      gl = FONT[s[i]]; if (!gl) continue;
      for (r = 0; r < 5; r++) for (col = 0; col < 3; col++)
        if (gl[r * 3 + col] === "1") g.fillRect(x + col * sc, y + r * sc, sc, sc);
    }
    return w;
  }
  function gemRows(lane, cx, cy, c, inset, sc) {
    var rows = GEM_ROWS[lane], r, w;
    g.fillStyle = c;
    for (r = inset; r < 7 - inset; r++) {
      w = rows[r] - inset * 2; if (w < 1) continue;
      g.fillRect(cx - ((w * sc) >> 1), cy + (r - 3) * sc - (sc >> 1), w * sc, sc);
    }
  }
  function gem(lane, cx, cy, sc) {                 // a falling note
    g.fillStyle = P.ink;
    var rows = GEM_ROWS[lane], r, w;
    for (r = 0; r < 7; r++) {
      w = (rows[r] + 2) * sc;
      g.fillRect(cx - (w >> 1), cy + (r - 3) * sc - (sc >> 1) - 1, w, sc + 2);
    }
    gemRows(lane, cx, cy + sc, LANE_DARK[lane], 0, sc);
    gemRows(lane, cx, cy, LANE_COLORS[lane], 0, sc);
    rect(cx - sc, cy - 2 * sc, 2 * sc, sc, "rgba(255,255,255,0.8)");
  }
  function receptor(lane, cx, cy, sc, lit) {
    gemRows(lane, cx, cy, lit ? "#ffffff" : LANE_COLORS[lane], 0, sc);
    gemRows(lane, cx, cy, lit ? LANE_COLORS[lane] : P.ink, 1, sc);
  }

  /* ---------------- state ---------------- */
  var screen = "menu";            // menu | loading | play | pause | results | error
  var songIdx = 0, difficulty = store("diff") === "hard" ? "hard" : "standard";
  var latency = (opts.latency != null ? opts.latency : (store("latency") || 0));
  var best = store("best") || {};
  var session = [];               // every finished song this visit
  var ac = null, ownAc = false, source = null, gain = null, buffers = {};
  var song = null, notes = [], startAt = 0, pausedAt = 0, beatLen = 0.5;
  var score = 0, combo = 0, maxCombo = 0, counts = null, maxScore = 1;
  var judgements = [], laneFlash = [-9, -9, -9, -9], laneHeld = [false, false, false, false];
  var strumAt = -9, missAt = -9, loadMsg = "", lastResult = null;
  var sel = 0, hits = [], hitsFor = "", touchSeen = false, pointers = {}, botHolds = [0, 0, 0, 0];
  var raf = 0, alive = true;

  function songTime() { return ac ? ac.currentTime - startAt : 0; }
  function mult() { return 1 + Math.min(3, Math.floor(combo / 10)); }

  /* ---------------- audio ---------------- */
  function ensureAudio() {
    if (!ac) {
      if (opts.audioContext) ac = opts.audioContext;
      else { ac = new (window.AudioContext || window.webkitAudioContext)(); ownAc = true; }
    }
    if (ac.state === "suspended") ac.resume();
  }
  function loadBuffer(s) {
    if (buffers[s.slug]) return Promise.resolve(buffers[s.slug]);
    return fetch(audioBase + s.slug + ".mp3").then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.arrayBuffer();
    }).then(function (ab) {
      return new Promise(function (res, rej) { ac.decodeAudioData(ab, res, rej); });
    }).then(function (buf) { buffers[s.slug] = buf; return buf; });
  }
  function stopAudio() {
    if (source) { try { source.stop(); } catch (e) {} source.disconnect(); source = null; }
  }
  /* (re)start the clip so that it lines up with the note clock from song time `from` */
  function startAudio(from) {
    stopAudio();
    var p0 = Math.max(0, from - audioOffset);
    if (p0 >= song.duration) return;
    source = ac.createBufferSource(); source.buffer = buffers[song.slug];
    if (!gain) { gain = ac.createGain(); gain.connect(opts.destination || ac.destination); }
    gain.gain.value = opts.volume == null ? 1 : opts.volume;
    source.connect(gain);
    source.start(Math.max(ac.currentTime, startAt + p0 + audioOffset), p0);
  }

  /* ---------------- flow ---------------- */
  function chooseSong(i) {
    songIdx = i; song = SONGS[i];
    ensureAudio();
    screen = "loading"; loadMsg = "TUNING UP";
    loadBuffer(song).then(function () { if (alive && screen === "loading") startPlay(); })
      .catch(function (e) { if (alive) { screen = "error"; loadMsg = String(e.message || e); } });
  }
  function startPlay() {
    notes = song.charts[difficulty].map(function (n) {
      return { t: n[0], lane: n[1], len: n[2] || 0, state: "pending" };
    });
    beatLen = 60 / song.bpm;
    score = 0; combo = 0; maxCombo = 0; judgements = [];
    counts = { perfect: 0, great: 0, ok: 0, miss: 0 };
    maxScore = 0;
    notes.forEach(function (n, i) {
      maxScore += 100 * (1 + Math.min(3, Math.floor((i + 1) / 10))) + Math.round(n.len * 100);
    });
    startAt = ac.currentTime + 0.1 + LEAD_IN;
    startAudio(-LEAD_IN);
    screen = "play";
  }
  function pause() {
    if (screen !== "play") return;
    pausedAt = songTime();
    releaseAll();
    stopAudio();
    screen = "pause"; sel = 0;
  }
  function resume() {
    ensureAudio();
    var from = pausedAt - 1.2;             // roll back a moment so you can find the beat again
    startAt = ac.currentTime - from;
    startAudio(from);
    screen = "play";
  }
  function toMenu() { stopAudio(); screen = "menu"; sel = songIdx; }
  function finish() {
    stopAudio(); releaseAll();
    var total = counts.perfect + counts.great + counts.ok + counts.miss;
    var acc = total ? (counts.perfect + counts.great * 0.6 + counts.ok * 0.3) / total : 0;
    var f = score / Math.max(1, maxScore);
    var key = song.slug + "." + difficulty;
    var isBest = score > (best[key] || 0);
    if (isBest) { best[key] = score; store("best", best); }
    lastResult = {
      song: song.slug, title: song.title, difficulty: difficulty, score: score, maxScore: maxScore,
      accuracy: +(acc * 100).toFixed(1), maxCombo: maxCombo, counts: counts,
      grade: f >= 0.9 ? "S" : f >= 0.75 ? "A" : f >= 0.55 ? "B" : f >= 0.35 ? "C" : "D",
      fullCombo: counts.miss === 0 && total > 0, newBest: isBest
    };
    session.push(lastResult);
    screen = "results"; sel = 0;
    if (opts.onResult) opts.onResult(lastResult);
  }
  function leave() {
    var payload = { results: session.slice(), best: best };
    destroy();
    if (opts.onExit) opts.onExit(payload);
  }

  /* ---------------- judgement (ported from the full game) ---------------- */
  function pressLane(lane) {
    if (screen !== "play") return;
    var now = songTime() - latency, bestN = null, bestDist = Infinity, i, n, d;
    laneFlash[lane] = songTime(); strumAt = songTime(); laneHeld[lane] = true;
    for (i = 0; i < notes.length; i++) {
      n = notes[i];
      if (n.state !== "pending" || n.lane !== lane) continue;
      d = Math.abs(n.t - now);
      if (d < bestDist) { bestDist = d; bestN = n; }
      if (n.t - now > WINDOWS.ok) break;
    }
    if (!bestN || bestDist > WINDOWS.ok) return;          // empty strum: no penalty
    var grade = bestDist <= WINDOWS.perfect ? "perfect" : bestDist <= WINDOWS.great ? "great" : "ok";
    bestN.state = bestN.len > 0 ? "holding" : "hit";
    counts[grade]++;
    combo++; maxCombo = Math.max(maxCombo, combo);
    score += POINTS[grade] * mult();
    judgements.push({ text: grade, grade: grade, t: songTime(), lane: lane });
  }
  function finishHold(n, now) {
    var held = Math.max(0, Math.min(now, n.t + n.len) - n.t), pts = Math.round(held * 100);
    score += pts; n.state = "done";
    judgements.push({ text: (held >= n.len - 0.1 ? "HELD +" : "+") + pts,
      grade: held >= n.len - 0.1 ? "perfect" : "ok", t: songTime(), lane: n.lane });
  }
  function releaseLane(lane) {
    laneHeld[lane] = false;
    if (screen !== "play") return;
    var now = songTime() - latency;
    notes.forEach(function (n) { if (n.state === "holding" && n.lane === lane) finishHold(n, now); });
  }
  function releaseAll() { for (var l = 0; l < 4; l++) if (laneHeld[l]) releaseLane(l); pointers = {}; }
  function tick() {
    var now = songTime() - latency, i, n, l;
    if (opts.autoplay) {                                   // the bot: every note, perfect
      for (i = 0; i < notes.length; i++) {
        n = notes[i];
        if (n.state !== "pending") continue;
        if (n.t - now > 0.01) break;
        pressLane(n.lane);
        if (n.len) botHolds[n.lane] = n.t + n.len; else laneHeld[n.lane] = false;
      }
      for (l = 0; l < 4; l++) if (botHolds[l] && now > botHolds[l]) { botHolds[l] = 0; releaseLane(l); }
    }
    for (i = 0; i < notes.length; i++) {
      n = notes[i];
      if (n.state === "pending" && n.t < now - WINDOWS.ok) {
        n.state = "missed"; counts.miss++;
        if (combo > 0) judgements.push({ text: "miss", grade: "miss", t: songTime(), lane: n.lane });
        if (combo >= 10) missAt = songTime();
        combo = 0;
      } else if (n.state === "holding" && now >= n.t + n.len) finishHold(n, now);
      if (n.t > now + 1) break;
    }
    if (songTime() > song.duration + 0.6) finish();
  }

  /* ---------------- the room ---------------- */
  function drawScene(t, beatIdx, pulse, heat, live) {
    var i, x, y, f, lx, tx, hw, b, bob = pulse > 0.55 ? 1 : 0;
    g.drawImage(bg, 0, 0);
    // sign
    text("THE OAK", CX, 16, pulse > 0.7 && live ? P.signHot : P.sign, 2, "center");
    // lights: one can per lane, flaring when that lane is hit
    var spacing = Math.min(30, SW / 5);
    for (i = 0; i < 4; i++) {
      lx = Math.round(CX + (i - 1.5) * spacing);
      tx = CX + (i - 1.5) * 9 + (live ? 0 : Math.sin(t * 0.7 + i * 1.7) * 14);
      b = live ? 0.08 + 0.10 * pulse * (0.4 + heat) + 0.6 * Math.max(0, 1 - (t - laneFlash[i]) / 0.3)
               : 0.10 + 0.05 * Math.sin(t * 1.3 + i);
      g.globalAlpha = Math.min(0.75, b); g.fillStyle = beamPat[i];
      for (y = 11; y < SY + 12; y++) {
        f = (y - 11) / (SY + 1);
        hw = 2 + f * 12;
        g.fillRect(Math.round(lx + (tx - lx) * f - hw), y, Math.round(hw * 2), 1);
      }
      g.globalAlpha = 1;
      rect(lx - 3, 3, 6, 6, P.ink); rect(lx - 2, 8, 4, 2, b > 0.3 ? "#ffffff" : LANE_COLORS[i]);
    }
    // laptop glow
    rect(CX - 26, FEET - 30, 10, 8, P.headDark); rect(CX - 25, FEET - 29, 8, 6, pulse > 0.6 ? "#fff6dc" : P.head);
    drawWrenasmir(CX, FEET, bob, beatIdx, t);
    // the crowd
    var jump = heat > 0.4 ? 2 : 1, sad = live && t - missAt < 0.8, row, n = 0;
    for (row = 0; row < 2; row++) {
      var top = SH - CROWD_H + (row ? (CROWD_H > 20 ? 12 : 7) : 2);
      var step = row ? 13 : 11, c = row ? P.crowdFront : P.crowdBack;
      for (x = row ? -3 : 3; x < W; x += step, n++) {
        var up = !sad && ((beatIdx + n) & 1) === 0 && pulse > 0.45 ? jump : 0;
        y = top - up + (hash(n, 7) < 0.3 ? 1 : 0);
        rect(x + 2, y, 5, 5, c); rect(x, y + 5, 9, SH - y, c);
        if (!sad && hash(n, 3) < heat * 0.75) { rect(x, y - 3, 2, 8, c); rect(x + 7, y - 3, 2, 8, c); }
      }
    }
  }

  function drawWrenasmir(px, fy, bob, beatIdx, t) {
    var y = fy - 54 + bob, i, j, h, strum = t - strumAt < 0.09 ? 1 : 0;
    rect(px - 6, fy - 3, 5, 3, P.shoe); rect(px + 1, fy - 3, 5, 3, P.shoe);                 // shoes
    rect(px - 5, fy - 5, 3, 2, P.cream); rect(px + 2, fy - 5, 3, 2, P.cream);               // socks
    rect(px - 5, fy - 4, 3, 1, P.rug); rect(px + 2, fy - 4, 3, 1, P.rug);
    rect(px - 5, fy - 13, 3, 8, P.skin); rect(px + 2, fy - 13, 3, 8, P.skin);               // legs
    rect(px - 6, y + 32, 12, 9, P.khaki); rect(px - 1, y + 37, 2, 4, P.khakiDark);          // shorts
    rect(px - 7, y + 19, 14, 14, P.tee); rect(px - 7, y + 31, 14, 2, P.teeDark);            // tee
    rect(px - 10, y + 19, 3, 6, P.teeDark); rect(px + 7, y + 19, 3, 6, P.teeDark);          // sleeves
    rect(px - 14, y + 24, 5, 2, P.skin); rect(px - 16, y + 25, 3, 2, P.skin);               // arm out to the laptop
    for (i = 0; i < 9; i++) rect(px + 4 - i, y + 19 + i, 2, 2, P.yellow);                   // strap
    rect(px + 2, y + 24, 9, 2, P.woodDark);                                                 // neck
    rect(px - 5, y + 27, 8, 6, P.yellow); rect(px - 3, y + 29, 3, 2, P.woodDark);           // little yellow body
    rect(px + 7, y + 24 + strum, 3, 3, P.skin); rect(px - 1 + strum, y + 28 + strum * 2, 3, 2, P.skin);
    rect(px - 2, y + 17, 4, 2, P.skin);                                                     // neck
    rect(px - 6, y + 5, 12, 12, P.head); rect(px + 5, y + 5, 1, 12, P.headDark);            // box head
    var seed = beatIdx >> 1;
    for (j = 0; j < 8; j++) for (i = 0; i < 8; i++) {                                       // mosaic face
      h = hash(i + j * 8, seed);
      var mid = i === 3 || i === 4;
      g.fillStyle = h < 0.08 ? "#2a1a08" : mid ? (h < 0.5 ? "#e04a3a" : h < 0.8 ? "#e8823a" : "#f0a070")
        : (i === 2 || i === 5) ? (h < 0.5 ? "#c9b85a" : "#9fce5e") : (h < 0.55 ? "#5ec24a" : h < 0.85 ? "#8fd86a" : "#3fa032");
      g.fillRect(px - 4 + i, y + 8 + j, 1, 1);
    }
    rect(px - 9, y + 3, 18, 3, P.hat); rect(px - 9, y + 5, 18, 1, P.hatDark);               // bucket hat
    rect(px - 5, y, 10, 3, P.hat); rect(px, y, 2, 2, LANE_COLORS[1]); rect(px + 1, y, 2, 1, "#8fbf7a");
  }

  /* ---------------- the highway ---------------- */
  function laneX(l) { return HX + l * LW + (LW >> 1); }
  function noteY(dt) { return Math.round(HIT_Y - dt / LOOKAHEAD * (HIT_Y - HTOP - 6)); }
  function drawHighway(now, t) {
    var l, i, n, y, y2, x;
    rect(HX - 2, HTOP, LW * 4 + 4, H - HTOP, P.highway);
    rect(HX - 2, HTOP, 1, H - HTOP, P.ink); rect(HX + LW * 4 + 1, HTOP, 1, H - HTOP, P.ink);
    for (l = 1; l < 4; l++) rect(HX + l * LW, HTOP, 1, H - HTOP, "rgba(232,221,201,0.08)");
    var first = Math.ceil((now - song.beatOffset) / beatLen);
    for (i = first; ; i++) {                                   // beat lines; bar lines brighter
      var bt = song.beatOffset + i * beatLen; if (bt > now + LOOKAHEAD) break;
      rect(HX, noteY(bt - now), LW * 4, 1, "rgba(232,221,201," + (i % 4 === 0 ? 0.16 : 0.07) + ")");
    }
    rect(HX - 1, HIT_Y + 5 * GS, LW * 4 + 2, 1, "rgba(232,221,201,0.25)");
    for (l = 0; l < 4; l++) {
      var lit = t - laneFlash[l] < 0.1 || laneHeld[l];
      if (lit) rect(HX + l * LW + 1, HTOP, LW - 1, H - HTOP, "rgba(232,221,201,0.05)");
      receptor(l, laneX(l), HIT_Y, GS, lit);
      if (!touchSeen) text(keyLabels[l], laneX(l), HIT_Y + 6 * GS + 4, P.dim, 1, "center");
    }
    if (combo >= 10) {
      var pop = t - (judgements.length ? judgements[judgements.length - 1].t : -9) < 0.06 ? 3 : 2;
      g.globalAlpha = 0.55;
      text(combo, HX + LW * 2, HTOP + 16, P.cream, pop, "center");
      text("COMBO", HX + LW * 2, HTOP + 16 + pop * 6, P.dim, 1, "center");
      g.globalAlpha = 1;
    }
    var vis = [];
    for (i = 0; i < notes.length; i++) {
      n = notes[i];
      if (n.t - now > LOOKAHEAD) break;
      x = laneX(n.lane);
      if (n.state === "holding") {                             // sustain being held: fat, pulsing
        y2 = Math.max(HTOP, noteY(n.t + n.len - now));
        var fat = (2 + (Math.floor(now * 12) & 1)) * GS;
        rect(x - fat, y2, fat * 2, HIT_Y - y2, LANE_COLORS[n.lane]);
        rect(x - GS, y2, GS, HIT_Y - y2, "rgba(255,255,255,0.6)");
        continue;
      }
      if (n.state !== "pending") continue;
      y = noteY(n.t - now);
      if (n.len > 0) {
        y2 = Math.max(HTOP, noteY(n.t + n.len - now));
        rect(x - GS * 2, y2, GS * 4, y - y2, LANE_DARK[n.lane]);
        rect(x - GS, y2, GS * 2, y - y2, LANE_COLORS[n.lane]);
      }
      if (y < H + 8) vis.push(n);
    }
    for (i = vis.length - 1; i >= 0; i--) gem(vis[i].lane, laneX(vis[i].lane), noteY(vis[i].t - now), GS);
    judgements = judgements.filter(function (j) { return t - j.t < 0.55; });
    judgements.forEach(function (j) {
      var a = (t - j.t) / 0.55, jx = Math.max(HX + 14, Math.min(HX + LW * 4 - 14, laneX(j.lane)));
      g.globalAlpha = a > 0.6 ? 1 - (a - 0.6) / 0.4 : 1;
      text(j.text, jx, HIT_Y - 14 * GS - Math.round(a * 8), GRADE_COLORS[j.grade], 1, "center");
      g.globalAlpha = 1;
    });
    rect(HX - 2, HTOP, LW * 4 + 4, 2, P.ink);                  // song progress
    rect(HX - 2, HTOP, Math.round((LW * 4 + 4) * Math.max(0, Math.min(1, now / song.duration))), 2, P.sign);
  }

  function drawHud(now) {
    var sc = SW >= 200 ? 2 : 1, s = String(score), w = textW(s, sc);
    rect(2, 12, Math.max(w, 30) + 5, 5 * sc + 12, "rgba(13,9,11,0.8)");
    text(s, 4, 14, P.cream, sc);
    text("X" + mult(), 4, 16 + 5 * sc, combo >= 10 ? P.sign : P.dim);
    rect(SW - 13, 12, 11, 11, "rgba(13,9,11,0.8)");            // pause button
    rect(SW - 10, 15, 2, 5, P.cream); rect(SW - 6, 15, 2, 5, P.cream);
    hits.push({ x: SW - 16, y: 8, w: 16, h: 18, action: pause, hidden: true });
    if (now < 2.5) {                                            // now-playing chyron
      var y = SY - 16;
      rect(0, y, textW(song.title) + 12, 15, "rgba(13,9,11,0.85)"); rect(0, y, 2, 15, P.rug);
      text("NOW PLAYING", 5, y + 2, P.dim); text(song.title, 5, y + 8, P.cream);
    }
  }

  /* ---------------- menus ---------------- */
  var panelX, panelW;
  function panel(h) {
    panelW = Math.min(W - 8, 176); panelX = (W - panelW) >> 1;
    var y = Math.max(2, (H - h) >> 1);
    rect(0, 0, W, H, "rgba(13,9,11,0.55)");
    rect(panelX - 1, y - 1, panelW + 2, h + 2, P.sign); rect(panelX, y, panelW, h, P.ink);
    return y;
  }
  function row(label, right, y, action, lr) {
    var on = visibleHits().length === sel;
    if (on) rect(panelX + 3, y - 3, panelW - 6, 11, P.rug);
    text(label, panelX + 8, y, on ? P.cream : P.dim);
    if (right) text(right, panelX + panelW - 8, y, on ? P.cream : P.dim, 1, "right");
    hits.push({ x: panelX, y: y - 3, w: panelW, h: 11, action: action, lr: lr });
  }
  function visibleHits() { return hits.filter(function (h) { return !h.hidden; }); }
  function toggleDiff() { difficulty = difficulty === "hard" ? "standard" : "hard"; store("diff", difficulty); }
  function nudge(dir) { latency = Math.max(-0.2, Math.min(0.2, Math.round((latency + dir * 0.01) * 100) / 100)); store("latency", latency); }

  function drawMenu() {
    var y = panel(112), cx = W >> 1;
    text("LIVE AT THE OAK", cx, y + 7, P.sign, 2, "center");
    text("WRENASMIR - THE LITE SET", cx, y + 21, P.dim, 1, "center");
    SONGS.forEach(function (s, i) {
      var b = best[s.slug + "." + difficulty];
      row("0" + (i + 1) + " " + s.title, b ? "BEST " + b : Math.round(s.duration) + " SEC", y + 35 + i * 12,
        function () { chooseSong(i); }, toggleDiff);
    });
    row("LEVEL", "< " + difficulty + " >", y + 73, toggleDiff, toggleDiff);
    row("LEAVE THE STAGE", "", y + 85, leave);
    text(touchSeen ? "TAP A SONG - TAP THE LANES TO PLAY" : keyLabels.join(" ") + " OR ARROWS - ENTER TO PLAY",
      cx, y + 101, P.dim, 1, "center");
  }
  function drawPause() {
    var y = panel(72), cx = W >> 1, ms = Math.round(latency * 1000);
    text("PAUSED", cx, y + 7, P.sign, 2, "center");
    row("RESUME", "", y + 25, resume);
    row("RESTART SONG", "", y + 37, function () { chooseSong(songIdx); });
    row("TIMING", "< " + (ms > 0 ? "+" : "") + ms + " MS >", y + 49, function () { nudge(1); }, nudge);
    row("BACK TO SETLIST", "", y + 61, toMenu);
  }
  function drawResults() {
    var r = lastResult, y = panel(118), cx = W >> 1, c = r.counts;
    text(r.title, cx, y + 6, P.sign, 2, "center");
    text(r.difficulty + (r.fullCombo ? " - FULL COMBO!" : ""), cx, y + 19, P.dim, 1, "center");
    text(r.score, panelX + 10, y + 30, P.cream, 3);
    text(r.newBest ? "NEW BEST!" : "BEST " + (best[r.song + "." + r.difficulty] || 0), panelX + 10, y + 48, r.newBest ? GRADE_COLORS.perfect : P.dim);
    rect(panelX + panelW - 34, y + 28, 24, 26, P.rug);
    text(r.grade, panelX + panelW - 22, y + 31, P.cream, 4, "center");
    var lx = panelX + 10, rx = cx + 4;
    text("PERFECT " + c.perfect, lx, y + 59, GRADE_COLORS.perfect); text("GREAT " + c.great, rx, y + 59, GRADE_COLORS.great);
    text("OK " + c.ok, lx, y + 66, GRADE_COLORS.ok); text("MISS " + c.miss, rx, y + 66, GRADE_COLORS.miss);
    text("ACC " + r.accuracy + "%", lx, y + 73, P.dim); text("MAX COMBO " + r.maxCombo, rx, y + 73, P.dim);
    row("PLAY IT AGAIN", "", y + 85, function () { chooseSong(songIdx); });
    row("BACK TO SETLIST", "", y + 96, toMenu);
    row("LEAVE THE STAGE", "", y + 107, leave);
  }
  function drawMessage(title, msg, withBack) {
    var y = panel(withBack ? 50 : 30), cx = W >> 1;
    text(title, cx, y + 7, P.sign, 2, "center");
    text(String(msg).slice(0, 40), cx, y + 21, P.dim, 1, "center");
    if (withBack) row("BACK TO SETLIST", "", y + 37, toMenu);
  }

  /* ---------------- frame ---------------- */
  function frame() {
    if (!alive) return;
    raf = requestAnimationFrame(frame);
    hits = [];
    var live = screen === "play" || screen === "pause";
    var t = live ? (screen === "pause" ? pausedAt : songTime()) : performance.now() / 1000;
    if (screen === "play") { tick(); if (screen !== "play") return; }
    var bl = live ? beatLen : 0.5, bo = live ? song.beatOffset : 0;
    var bp = (t - bo) / bl, beatIdx = Math.floor(bp), pulse = live && t < 0 ? 0 : 1 - (bp - beatIdx);
    var heat = live ? Math.min(1, combo / 40) : 0.15;
    rect(0, 0, W, H, P.ink);
    drawScene(t, beatIdx, pulse, heat, live);
    if (live) { drawHighway(t - latency, t); drawHud(t); }
    if (screen === "menu") drawMenu();
    else if (screen === "pause") drawPause();
    else if (screen === "results") drawResults();
    else if (screen === "loading") drawMessage(loadMsg, song.title);
    else if (screen === "error") drawMessage("NO SOUND", loadMsg, true);
    hitsFor = screen;
    var n = visibleHits().length;
    if (sel >= n) sel = Math.max(0, n - 1);
  }

  /* ---------------- input ---------------- */
  function menuKey(code) {
    var rows = hitsFor === screen ? visibleHits() : [], n = rows.length;   // never act on a stale screen
    if (code === "Escape") {
      if (screen === "menu") leave(); else if (screen === "pause") resume(); else if (screen !== "loading") toMenu();
      return true;
    }
    if (!n) return false;
    if (code === "ArrowUp" || code === "KeyW") sel = (sel + n - 1) % n;
    else if (code === "ArrowDown" || code === "KeyS") sel = (sel + 1) % n;
    else if (code === "ArrowLeft" || code === "ArrowRight") { if (rows[sel].lr) rows[sel].lr(code === "ArrowLeft" ? -1 : 1); }
    else if (code === "Enter" || code === "Space" || code === "NumpadEnter") rows[sel].action();
    else return false;
    return true;
  }
  function onKeyDown(e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var handled = false, lane;
    if (screen === "play") {
      lane = laneKeys.indexOf(e.code); if (lane < 0) lane = altKeys.indexOf(e.code);
      if (lane >= 0) { if (!e.repeat) pressLane(lane); handled = true; }
      else if (e.code === "Escape" || e.code === "KeyP") { pause(); handled = true; }
      else if (e.code === "Space" || e.code === "Enter") handled = true;
    } else handled = e.repeat ? /^Arrow|Space|Enter/.test(e.code) : menuKey(e.code);
    if (handled) { e.preventDefault(); e.stopImmediatePropagation(); }
  }
  function onKeyUp(e) {
    var lane = laneKeys.indexOf(e.code); if (lane < 0) lane = altKeys.indexOf(e.code);
    if (lane >= 0 && screen === "play") { releaseLane(lane); e.preventDefault(); e.stopImmediatePropagation(); }
  }
  function toCanvas(e) {
    var r = cv.getBoundingClientRect();
    return { x: (e.clientX - r.left) / r.width * W, y: (e.clientY - r.top) / r.height * H };
  }
  function onPointerDown(e) {
    e.preventDefault();
    var touch = e.pointerType !== "mouse", p = toCanvas(e), i, h;
    if (touch) touchSeen = true;
    for (i = 0; hitsFor === screen && i < hits.length; i++) {
      h = hits[i];
      if (p.x >= h.x && p.x < h.x + h.w && p.y >= h.y && p.y < h.y + h.h) {
        if (!h.hidden) sel = visibleHits().indexOf(h);
        h.action(1); return;
      }
    }
    if (screen !== "play") return;
    // touch: the whole stage is four big lanes. Mouse: click the lanes themselves.
    var lane = touch && !portrait ? Math.floor(p.x / W * 4) : Math.floor((p.x - HX) / LW);
    if (lane < 0 || lane > 3) return;
    pointers[e.pointerId] = lane; pressLane(lane);
  }
  function onPointerUp(e) {
    var lane = pointers[e.pointerId];
    if (lane != null) { delete pointers[e.pointerId]; releaseLane(lane); }
  }
  function onVisibility() { if (document.hidden && !opts.autoplay) pause(); }
  function onContext(e) { e.preventDefault(); }

  window.addEventListener("keydown", onKeyDown, true);
  window.addEventListener("keyup", onKeyUp, true);
  cv.addEventListener("pointerdown", onPointerDown);
  window.addEventListener("pointerup", onPointerUp);
  window.addEventListener("pointercancel", onPointerUp);
  cv.addEventListener("contextmenu", onContext);
  document.addEventListener("visibilitychange", onVisibility);
  var ro = window.ResizeObserver ? new ResizeObserver(layout) : null;
  if (ro) ro.observe(wrap); else window.addEventListener("resize", layout);
  layout();
  raf = requestAnimationFrame(frame);

  function destroy() {
    if (!alive) return;
    alive = false; cancelAnimationFrame(raf); stopAudio();
    if (gain) gain.disconnect();
    if (ownAc && ac) ac.close();
    window.removeEventListener("keydown", onKeyDown, true);
    window.removeEventListener("keyup", onKeyUp, true);
    window.removeEventListener("pointerup", onPointerUp);
    window.removeEventListener("pointercancel", onPointerUp);
    document.removeEventListener("visibilitychange", onVisibility);
    if (ro) ro.disconnect(); else window.removeEventListener("resize", layout);
    if (wrap.parentNode) wrap.parentNode.removeChild(wrap);
  }

  return {
    destroy: destroy,
    pause: pause,
    play: function (i, diff) { if (diff) difficulty = diff; chooseSong(i || 0); },   // call from a user gesture
    get screen() { return screen; },
    get results() { return session.slice(); },
    canvas: cv
  };
}

window.OakLite = { mount: mount, version: "1.0.0" };
})();
