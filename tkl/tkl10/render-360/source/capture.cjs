/* Browser verification and image/GLB export; opens the HTML without a server. */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const { pathToFileURL } = require('url');

(async () => {
  const out = path.resolve(__dirname, '..');
  const browser = await chromium.launch({
    executablePath: process.env.V10_RENDER_BROWSER || '/usr/bin/brave-browser',
    headless: true,
    args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--disable-dev-shm-usage'],
  });
  const context = await browser.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1 });
  const requests = [];
  await context.route(/^https?:/, route => { requests.push(route.request().url()); return route.abort(); });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(pathToFileURL(path.join(out, 'index.html')).href);
  await page.waitForFunction(() => window.v10?.ready, { timeout: 60000 });
  await page.waitForTimeout(1000);
  const summary = await page.evaluate(() => window.v10.summary());
  assert.equal(summary.keys, 86);
  assert.equal(summary.caseTriangles.length, 3);
  await page.screenshot({ path: path.join(out, 'studio-preview.png') });
  for (const view of ['hero', 'front', 'rear', 'side', 'top', 'bottom', 'edge', 'usb']) {
    await page.getByRole('button', { name: { hero: 'Overview', front: 'Front', rear: 'Rear', side: 'Profile', top: 'Top', bottom: 'Underneath', edge: 'Edge detail', usb: 'USB detail' }[view], exact: true }).click();
    await page.waitForTimeout(180);
    await page.locator('#viewport').screenshot({ path: path.join(out, `${view}.png`) });
    assert.equal(await page.locator(`[data-view="${view}"]`).getAttribute('aria-pressed'), 'true');
  }
  await page.getByRole('button', { name: 'Overview', exact: true }).click();
  const before = await page.evaluate(() => window.v10.camera.position.toArray());
  const bounds = await page.locator('#viewport').boundingBox();
  await page.mouse.move(bounds.width * .4, bounds.y + bounds.height * .48);
  await page.mouse.down();
  await page.mouse.move(bounds.width * .6, bounds.y + bounds.height * .64, { steps: 10 });
  await page.mouse.up();
  await page.waitForTimeout(400);
  const after = await page.evaluate(() => window.v10.camera.position.toArray());
  assert(Math.hypot(...before.map((v, i) => v - after[i])) > 10, 'Orbit drag must move the camera');
  const zoomBefore = await page.evaluate(() => window.v10.camera.zoom);
  await page.mouse.wheel(0, -150);
  await page.waitForTimeout(500);
  assert((await page.evaluate(() => window.v10.camera.zoom)) > zoomBefore, 'Wheel must zoom in');
  await page.locator('#spin').check();
  const angleBefore = await page.evaluate(() => window.v10.controls.getAzimuthalAngle());
  await page.waitForFunction(previous => Math.abs(window.v10.controls.getAzimuthalAngle() - previous) > 1e-6, angleBefore, { timeout: 10000 });
  await page.locator('#spin').uncheck();
  for (const theme of ['chalk', 'slate', 'graphite']) {
    await page.locator(`[data-finish="${theme}"]`).click();
    assert.equal(await page.locator(`[data-finish="${theme}"]`).getAttribute('aria-pressed'), 'true');
  }
  await page.locator('#key-style').selectOption('dark');
  await page.locator('#key-style').selectOption('two-tone');
  await page.locator('#legends').uncheck();
  await page.locator('#legends').check();
  await page.locator('#raking').check();
  await page.locator('#raking').uncheck();
  await page.locator('#leds').check();
  await page.locator('#leds').uncheck();
  await page.getByRole('button', { name: 'Reset view', exact: true }).click();
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Save this view', exact: true }).click();
  const download = await downloadPromise;
  await download.saveAs(path.join(out, 'v10-hero-high-resolution.png'));
  const encoded = await page.evaluate(async () => {
    const bytes = await window.v10.exportGLB();
    return new Promise(resolve => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result.split(',')[1]);
      reader.readAsDataURL(new Blob([bytes], { type: 'model/gltf-binary' }));
    });
  });
  const glb = Buffer.from(encoded, 'base64');
  assert.equal(glb.toString('utf8', 0, 4), 'glTF');
  fs.writeFileSync(path.join(out, 'v10-assembled.glb'), glb);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(500);
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Mobile layout must not overflow horizontally');
  await page.screenshot({ path: path.join(out, 'mobile-preview.png'), fullPage: true });
  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.getByRole('button', { name: 'Overview', exact: true }).click();
  await page.waitForTimeout(200);
  const result = { checked_at: new Date().toISOString(), browser: 'Brave / Playwright; local file URL',
    offline_http_requests: requests, errors, ...summary, glb_bytes: glb.length,
    passed: errors.length === 0 && requests.length === 0,
    checks: ['offline load', 'all eight camera views', 'free mouse orbit', 'wheel zoom', 'auto-rotation',
      'three finish presets', 'keycap colours', 'legend visibility', 'raking light', 'LED appearance',
      'PNG image download', 'binary glTF export', '390px mobile layout'] };
  fs.writeFileSync(path.join(out, 'browser-validation.json'), JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result, null, 2));
  await browser.close();
  assert(result.passed, 'Browser errors or network dependencies found');
})().catch(error => { console.error(error); process.exit(1); });
