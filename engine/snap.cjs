/* ROOT snapshot — photograph a square from a node, for the daily feed.
   Usage: NODE_PATH=/opt/homebrew/lib/node_modules node engine/snap.cjs <port> <outdir> <id> [id...]
   Serves nothing itself: expects the repo already served on <port>. */
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const [port, outdir, ...ids] = process.argv.slice(2);
  if (!port || !outdir || !ids.length) {
    console.error('usage: snap.cjs <port> <outdir> <roomId> [roomId...]');
    process.exit(1);
  }
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1000, height: 780 } });
  await pg.goto(`http://localhost:${port}/`);
  await pg.waitForTimeout(900);
  await pg.keyboard.press('Enter');            // leave boot
  await pg.waitForTimeout(300);
  const today = new Date().toISOString().slice(0, 10);
  for (const id of ids) {
    await pg.evaluate((rid) => window.DR.go(rid, 's'), id);
    await pg.waitForTimeout(2600);             // static wipe + caption settle
    const box = await pg.locator('canvas').boundingBox();
    // the photograph: a square detail, seeded off the room id so each
    // node is always photographed from the same angle
    let h = 0; for (const c of id) h = (h * 31 + c.charCodeAt(0)) >>> 0;
    const side = Math.min(box.width, box.height) * 0.92;
    const maxX = box.width - side;
    const x = box.x + (h % 97) / 97 * maxX;
    const y = box.y + (box.height - side) / 2;
    const out = path.join(outdir, `${today}-${id}.png`);
    await pg.screenshot({ path: out, clip: { x, y, width: side, height: side } });
    console.log('  photographed ' + out);
  }
  await b.close();
})();
