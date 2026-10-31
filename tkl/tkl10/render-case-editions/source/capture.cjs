/* Validate the standalone viewer in Brave with HTTP blocked; capture comparisons. */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const crypto = require('crypto');
const { pathToFileURL } = require('url');

(async () => {
  const out = path.resolve(__dirname, '..');
  const root = path.dirname(out);
  fs.mkdirSync(path.join(out, 'views'), { recursive: true });
  const browser = await chromium.launch({
    executablePath: process.env.V10_RENDER_BROWSER || '/usr/bin/brave-browser',
    headless: true,
    args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--disable-dev-shm-usage'],
  });
  const context = await browser.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1 });
  const requests = [], errors = [];
  await context.route(/^https?:/, route => { requests.push(route.request().url()); return route.abort(); });
  const page = await context.newPage();
  page.setDefaultTimeout(60000);
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(pathToFileURL(path.join(out, 'index.html')).href);
  await page.waitForFunction(() => window.v10?.ready, null, { timeout: 60000 });
  const summary = await page.evaluate(() => window.v10.summary());
  assert.equal(summary.keys, 86);
  assert.equal(summary.caseTriangles.length, 3);
  const settle = async () => { await page.evaluate(() => window.v10.render()); await page.waitForTimeout(80); };
  await settle();
  await page.screenshot({ path: path.join(out, 'studio-preview.png') });
  const profiles = ['xvx-bow', 'xvx-wob', 'flat', 'glass', 'slim'];
  const concepts = ['original', 'pills', 'nav', 'deck', 'halo', 'perkey'];
  const combinations = [];
  let editionOneRest;
  for (const edition of ['current','raised']) {
  await page.selectOption('#case-edition',edition);
  for (const profile of profiles) {
    await page.selectOption('#cap-profile', profile);
    for (const design of concepts) {
      await page.selectOption('#case-design', design);
      const state = await page.evaluate(() => {
        const v = window.v10;
        const keyGroup = v.cad.children.find(g => g.name.startsWith('Illustrative components')).children.find(g => g.name.startsWith('86 '));
        const labels = v.cad.getObjectByName('Illustrative ANSI legends');
        const positions = keyGroup.children.map(m => { m.geometry.computeBoundingBox();return [m.geometry.boundingBox.min.z,m.geometry.boundingBox.max.z]; });
        return { ...v.selection(), keys:keyGroup.children.length, topRange:[Math.min(...positions.map(p=>p[1])),Math.max(...positions.map(p=>p[1]))],
          legendsVisible:labels.visible, emittingLegends:labels.children.filter(m=>m.material.emissiveIntensity>0).length,
          visibleVariants:Object.entries(v.variantGroups).filter(([,g])=>g.visible).map(([k])=>k),
          visibleRaised:Object.entries(v.raisedGroups).filter(([,g])=>g.visible).map(([k])=>k),
          originalVisible:v.partMeshes.find(m=>m.name==='upper').visible };
      });
      assert.equal(state.keys,86);
      assert.equal(state.profile,profile);
      assert.equal(state.design,design);
      assert.equal(state.edition,edition);
      assert(Math.abs(state.topRange[1]-state.topRange[0])<.001,'All unit sizes must share the same mounted cap-top height');
      assert.equal(state.originalVisible,edition==='current'&&['original','perkey'].includes(design));
      assert.equal(state.visibleVariants.length,edition==='current'&&!['original','perkey'].includes(design)?1:0);
      assert.equal(state.visibleRaised.length,edition==='raised'?1:0);
      assert.equal(state.emittingLegends,design==='perkey'&&profile.startsWith('xvx')?86:0);
      if(['flat','glass','slim'].includes(profile)) assert.equal(state.legendsVisible,false,'Blank cap designs default to no legends');
      await settle();
      combinations.push(state);
    }
    console.log('Checked all six lighting concepts:',edition,profile);
    await page.selectOption('#case-design','original');
    await page.selectOption('#room','day');
    await page.evaluate(()=>window.v10.setView('hero'));
    await settle();
    await page.locator('#viewport').screenshot({path:path.join(out,'views',`caps-${profile}-hero.png`)});
    await page.evaluate(()=>window.v10.setView('side'));
    await settle();
    await page.locator('#viewport').screenshot({path:path.join(out,'views',`caps-${profile}-side.png`)});
  }
  await page.selectOption('#cap-profile','xvx-bow');await page.selectOption('#case-design','nav');
  for(const view of ['hero','side','front','edge']) {
    await page.evaluate(v=>window.v10.setView(v),view);await settle();
    await page.locator('#viewport').screenshot({path:path.join(out,'views',`${edition}-${view}.png`)});
  }
  const rest=await page.evaluate(()=>window.v10.cad.children.find(g=>g.name.startsWith('Illustrative components')).children.find(g=>g.name.startsWith('86 ')).children.map(m=>m.position.toArray()));
  if(edition==='current')editionOneRest=rest;
  else assert.deepEqual(rest,editionOneRest,'Case switching must preserve every key position');
  await page.locator('#key-travel').fill('2.8');await page.locator('#key-travel').dispatchEvent('input');
  const pressed=await page.evaluate(()=>window.v10.cad.children.find(g=>g.name.startsWith('Illustrative components')).children.find(g=>g.name.startsWith('86 ')).children.map(m=>m.position.toArray()));
  for(let i=0;i<86;i++) {
    assert.equal(rest[i][0],pressed[i][0]);assert.equal(rest[i][1],pressed[i][1]);
    assert(Math.abs(rest[i][2]-pressed[i][2]-2.8)<1e-8,'Every key must move downward by its full travel');
  }
  await page.evaluate(()=>window.v10.setView('side'));await settle();
  await page.locator('#viewport').screenshot({path:path.join(out,'views',`${edition}-pressed-side.png`)});
  await page.locator('#key-travel').fill('0');await page.locator('#key-travel').dispatchEvent('input');
  }
  await page.selectOption('#cap-profile','xvx-wob');
  await page.selectOption('#room','dim');
  await page.evaluate(()=>window.v10.setView('hero'));
  for(const design of concepts) {
    await page.selectOption('#case-design',design);
    await settle();
    await page.locator('#viewport').screenshot({path:path.join(out,'views',`lighting-${design}.png`)});
  }
  console.log('Captured profile and lighting comparisons');
  await page.selectOption('#cap-profile','xvx-bow');
  await page.selectOption('#case-design','nav');
  const viewNames={hero:'Overview',front:'Front',rear:'Rear',side:'Profile',top:'Top',bottom:'Underneath',edge:'Edge detail',usb:'USB detail'};
  for(const [view,label] of Object.entries(viewNames)) {
    await page.getByRole('button',{name:label,exact:true}).click();await settle();
    await page.locator('#viewport').screenshot({path:path.join(out,'views',`${view}.png`)});
    assert.equal(await page.locator(`[data-view="${view}"]`).getAttribute('aria-pressed'),'true');
  }
  await page.evaluate(()=>window.v10.setView('hero'));
  const before=await page.evaluate(()=>window.v10.camera.position.toArray());
  const bounds=await page.locator('#viewport').boundingBox();
  await page.mouse.move(bounds.x+bounds.width*.4,bounds.y+bounds.height*.48);
  await page.mouse.down();await page.mouse.move(bounds.x+bounds.width*.6,bounds.y+bounds.height*.64,{steps:10});await page.mouse.up();
  const after=await page.evaluate(()=>window.v10.camera.position.toArray());
  assert(Math.hypot(...before.map((v,i)=>v-after[i]))>10,'Orbit drag must move the camera');
  const zoomBefore=await page.evaluate(()=>window.v10.camera.zoom);
  await page.mouse.wheel(0,-150);
  await page.waitForFunction(z=>window.v10.camera.zoom>z,zoomBefore);
  await page.locator('#spin').check();
  const angle=await page.evaluate(()=>window.v10.controls.getAzimuthalAngle());
  await page.waitForFunction(a=>Math.abs(window.v10.controls.getAzimuthalAngle()-a)>1e-6,angle);
  await page.locator('#spin').uncheck();
  for(const finish of ['chalk','slate','graphite']) {
    await page.locator(`[data-finish="${finish}"]`).click();
    assert.equal(await page.locator(`[data-finish="${finish}"]`).getAttribute('aria-pressed'),'true');
  }
  await page.locator('#case-color').fill('#42524c');await page.locator('#case-color').dispatchEvent('input');
  for(const color of ['two-tone','light','dark','source']) await page.selectOption('#key-style',color);
  await page.locator('#roughness').fill('0.4');await page.locator('#roughness').dispatchEvent('input');
  assert.equal(await page.locator('#finish-name').textContent(),'Satin');
  await page.locator('#roughness').fill('0.62');await page.locator('#roughness').dispatchEvent('input');
  await page.locator('[data-finish="graphite"]').click();
  await page.locator('#seat-depth').fill('2.5');await page.locator('#seat-depth').dispatchEvent('input');
  assert.equal((await page.evaluate(()=>window.v10.selection())).seat,2.5);
  await page.selectOption('#cap-profile','xvx-bow');
  await page.locator('#legends').uncheck();await page.locator('#legends').check();
  await page.locator('#raking').check();await page.locator('#raking').uncheck();
  await page.selectOption('#case-design','perkey');
  await page.locator('#leds').uncheck();
  assert.equal(await page.evaluate(()=>window.v10.cad.getObjectByName('Illustrative ANSI legends').children.reduce((n,m)=>n+m.material.emissiveIntensity,0)),0);
  await page.locator('#leds').check();
  await page.locator('#light-level').fill('0.5');await page.locator('#light-level').dispatchEvent('input');
  assert(await page.evaluate(()=>window.v10.cad.getObjectByName('Illustrative ANSI legends').children[0].material.emissiveIntensity>0));
  await page.locator('#light-level').fill('0.7');await page.locator('#light-level').dispatchEvent('input');
  await page.selectOption('#case-design','nav');
  await page.getByRole('button',{name:'Reset view',exact:true}).click();
  const pngWait=page.waitForEvent('download');
  await page.getByRole('button',{name:'Save this view',exact:true}).click();
  const png=await pngWait;await png.saveAs(path.join(out,'v10-xvx-bow-navigation-bar.png'));
  const glbWait=page.waitForEvent('download');
  await page.getByRole('button',{name:'Download this 3D model',exact:true}).click();
  const download=await glbWait;
  const glbPath=path.join(out,'v10-xvx-bow-navigation-bar.glb');await download.saveAs(glbPath);
  const glb=fs.readFileSync(glbPath);assert.equal(glb.toString('utf8',0,4),'glTF');
  const gltf=JSON.parse(glb.subarray(20,20+glb.readUInt32LE(12)).toString());
  assert.equal(gltf.nodes.filter(n=>n.name?.includes('keycap')).length,87); // group plus 86 keys
  assert(gltf.nodes.some(n=>n.name==='raised-navigation-lightguide'));
  assert(gltf.nodes.some(n=>n.name==='raised-navigation-shell'));
  assert(!gltf.nodes.some(n=>n.name==='navigation-lightbar-shell'),'Hidden Edition 1 shell must not export');
  assert(!gltf.nodes.some(n=>n.name==='upper'),'Hidden original shell must not be exported beside its replacement');
  await page.selectOption('#cap-profile','glass');
  const encoded=await page.evaluate(async()=>{
    const bytes=await window.v10.exportGLB();return await new Promise(resolve=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.readAsDataURL(new Blob([bytes]));});
  });
  const glass=Buffer.from(encoded,'base64');assert.equal(glass.toString('utf8',0,4),'glTF');
  const glassDoc=JSON.parse(glass.subarray(20,20+glass.readUInt32LE(12)).toString());
  assert(glassDoc.nodes.some(n=>n.extras?.author==='Joe Scotto'),'Scotto attribution must accompany GLB');
  await page.selectOption('#cap-profile','xvx-bow');
  await page.setViewportSize({width:390,height:844});await settle();
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No mobile horizontal overflow');
  await page.selectOption('#cap-profile','flat');await page.selectOption('#case-design','pills');
  await page.selectOption('#case-edition','current');await page.selectOption('#case-edition','raised');
  assert.equal((await page.evaluate(()=>window.v10.selection())).profile,'flat');
  await page.screenshot({path:path.join(out,'mobile-preview.png'),fullPage:true});
  await page.setViewportSize({width:1600,height:1000});
  await page.selectOption('#cap-profile','xvx-bow');await page.selectOption('#case-design','nav');
  await page.getByRole('button',{name:'Reset view',exact:true}).click();await settle();
  await page.screenshot({path:path.join(out,'studio-preview.png')});
  for(const filename of ['provenance.json','geometry-study.json']) {
    const manifest=JSON.parse(fs.readFileSync(path.join(out,filename)));
    for(const [relative,expected] of Object.entries(manifest.source_sha256)) {
      const actual=crypto.createHash('sha256').update(fs.readFileSync(path.join(root,relative))).digest('hex');assert.equal(actual,expected,relative+' changed');
    }
  }
  const result={checked_at:new Date().toISOString(),browser:'Brave / Playwright; standalone file URL',offline_http_requests:requests,errors,
    ...summary,combinations,glb_bytes:glb.length,scotto_glb_bytes:glass.length,source_files_unchanged:true,
    checks:['all 60 edition / profile / lighting combinations','case switching leaves all key positions unchanged','86 key travel positions move down 2.8 mm','aligned cap tops across all unit sizes','blank versus luminous legends','correct edition / concept meshes visible and exported',
      'all eight views','free orbit / zoom / auto-rotation','finish and cap colours','socket engagement adjustment','lights off and brightness adjustment',
      'PNG download','selected GLB download','Scotto GLB attribution','390px mobile controls','source CAD and reference hashes'],
    passed:errors.length===0&&requests.length===0};
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({...result,combinations:combinations.length},null,2));
  await browser.close();assert(result.passed,'Browser errors or network dependencies found');
})().catch(e=>{console.error(e);process.exit(1);});
