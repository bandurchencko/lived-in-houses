// Screenshots for the README: node snimki.mjs (needs the docs/ folder served at http://localhost:8157)
import { chromium } from 'playwright';
const URL = process.env.URL || 'http://localhost:8157/';
const KADRY = [
  ['cover-tavern-13.png', 'tavern-13-gallery.glb', -38, 20, 100],
  ['cut-tavern-13.png', 'tavern-13-gallery.glb', -30, 48, 38],
  ['garden-house-1818.png', 'garden-house-1818.glb', -35, 22, 100],
  ['cut-garden-house-1818.png', 'garden-house-1818.glb', -25, 50, 42],
  ['workshop-house-2020.png', 'workshop-house-2020.glb', 35, 22, 100],
  ['tavern-7-annex.png', 'tavern-7-annex.glb', -38, 22, 100],
];
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const p = await b.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 });
await p.goto(URL, { waitUntil: 'networkidle' });
await p.waitForFunction(() => document.querySelectorAll('#dom option').length > 0);
await p.evaluate(() => document.getElementById('panel').style.display = 'none');
for (const [imya, glb, az, el, srez] of KADRY) {
  await p.evaluate(g => { const s = document.getElementById('dom'); s.value = g; s.dispatchEvent(new Event('change')); }, glb);
  await p.waitForTimeout(2500);
  await p.evaluate(([az, el, srez]) => {
    window.prosmotr.camera.clearViewOffset(); window.prosmotr.camera.updateProjectionMatrix();
    window.prosmotr.rakurs(az, el);
    const r = document.getElementById('srez'); r.value = srez; r.dispatchEvent(new Event('input'));
  }, [az, el, srez]);
  await p.waitForTimeout(1200);
  await p.screenshot({ path: 'docs/obrazy/' + imya });
  console.log('снимок', imya);
}
await b.close();
