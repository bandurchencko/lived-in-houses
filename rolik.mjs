// Frame-by-frame capture of the viewer for the trailer: node rolik.mjs <out-folder>
// (docs/ served at http://localhost:8157; frames kadr-0000.png … at 30 fps, 1920×1080)
import { chromium } from 'playwright';
import fs from 'node:fs';

const URL = process.env.URL || 'http://localhost:8157/';
const OUT = process.argv[2] || 'kadry';
const FPS = 30;
const ease = t => t * t * (3 - 2 * t);
const lerp = (a, b, t) => a + (b - a) * t;

// shots: house, frames, (t) => {az, el, cut, roof}
const SHOTS = [
  ['tavern-13-gallery.glb', 90, t => ({ az: lerp(-70, -30, ease(t)), el: 22, cut: 1, roof: true })],
  ['tavern-13-gallery.glb', 45, t => ({ az: lerp(-30, -20, t), el: lerp(22, 34, ease(t)), cut: 1, roof: false })],
  ['tavern-13-gallery.glb', 90, t => ({ az: lerp(-20, 0, t), el: lerp(34, 46, ease(t)), cut: lerp(1, 0.38, ease(t)), roof: false })],
  ['tavern-13-gallery.glb', 30, t => ({ az: lerp(0, 6, t), el: 46, cut: 0.38, roof: false })],
  ['tavern-7-annex.glb', 45, t => ({ az: lerp(-55, -38, t), el: 22, cut: 1, roof: true })],
  ['tavern-4-corner.glb', 45, t => ({ az: lerp(-55, -38, t), el: 22, cut: 1, roof: true })],
  ['garden-house-1818.glb', 75, t => ({ az: lerp(-62, -28, ease(t)), el: 24, cut: 1, roof: true })],
  ['workshop-house-2020.glb', 45, t => ({ az: lerp(42, 26, t), el: 24, cut: 1, roof: true })],
  ['porch-house-1717.glb', 45, t => ({ az: lerp(-42, -26, t), el: 24, cut: 1, roof: true })],
];
// «рисунок → дом»: облёт дома, построенного по рисунку кузни (отдельной папкой: <out>-obraz)
const SHOTS_OBRAZ = [
  ['obraz/dom-kuznya/dom.glb', 150, t => ({ az: lerp(-62, -24, ease(t)), el: lerp(12, 20, t), cut: 1, roof: true })],
];

fs.mkdirSync(OUT, { recursive: true });
const b = await chromium.launch({ args: ['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await p.goto(URL, { waitUntil: 'networkidle' });
await p.waitForFunction(() => window.prosmotr && document.querySelectorAll('#dom option').length > 0);
await p.evaluate(() => { document.getElementById('panel').style.display = 'none'; });
let n = 0, tekushchij = null;
const t0 = Date.now();
const VSE = process.env.TOLKO_OBRAZ ? SHOTS_OBRAZ : SHOTS;
for (const [dom, kadrov, f] of VSE) {
  if (dom !== tekushchij) {
    await p.evaluate(d => window.prosmotr.zagruzit(d), dom);
    await p.waitForTimeout(400);
    tekushchij = dom;
  }
  for (let i = 0; i < kadrov; i++) {
    const s = f(kadrov > 1 ? i / (kadrov - 1) : 0);
    await p.evaluate(s => {
      const P = window.prosmotr;
      P.camera.clearViewOffset(); P.camera.updateProjectionMatrix();
      P.rakurs(s.az, s.el); P.srez(s.cut); P.gruppa('krysha', s.roof);
      return new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
    }, s);
    await p.screenshot({ path: `${OUT}/kadr-${String(n).padStart(4, '0')}.png` });
    n++;
  }
  console.log(dom, 'кадров всего', n, ((Date.now() - t0) / 1000).toFixed(0) + ' с');
}
await b.close();
console.log('готово:', n, 'кадров,', (n / FPS).toFixed(1), 'с ролика');
