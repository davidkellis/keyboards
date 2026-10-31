/* Check the offline optical-study viewer and capture its actual WebGL output. */
const path = require('path');
const fs = require('fs');
const assert = require('assert/strict');
const crypto = require('crypto');
const {pathToFileURL} = require('url');
const modules = process.env.V10_RENDER_NODE_MODULES || path.join(__dirname,'node_modules');
const {chromium} = require(path.join(modules,'playwright'));

(async()=>{
  const stage=process.argv[2]||'validate';
  const out=path.resolve(__dirname,'..'),root=path.dirname(out);
  fs.mkdirSync(path.join(out,'views'),{recursive:true});
  const browser=await chromium.launch({executablePath:process.env.V10_RENDER_BROWSER||'/usr/bin/brave-browser',headless:true,
    args:['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader','--disable-dev-shm-usage']});
  const context=await browser.newContext({viewport:stage==='features'?{width:1000,height:700}:{width:1600,height:1000},deviceScaleFactor:1});
  const network=[],errors=[];
  await context.route(/^https?:/,route=>{network.push(route.request().url());return route.abort()});
  const page=await context.newPage();page.setDefaultTimeout(60000);
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  await page.goto(pathToFileURL(path.join(out,'index.html')).href);
  await page.waitForFunction(()=>window.v10?.ready);
  // Captures explicitly render after state changes. Avoid an additional
  // animation pass competing with every software-rendered validation frame.
  await page.evaluate(()=>v10.renderer.setAnimationLoop(null));
  const settle=async()=>{await page.evaluate(()=>v10.render());await page.waitForTimeout(80)};
  const shot=async name=>{await settle();await page.locator('#viewport').screenshot({path:path.join(out,'views',name+'.png')})};
  const summary=await page.evaluate(()=>v10.summary());assert.equal(summary.keys,86);
  const manifest=JSON.parse(fs.readFileSync(path.join(out,'acrylic-study.json')));
  if(stage==='mobile'){
    await page.setViewportSize({width:390,height:844});
    await page.selectOption('#case-design','clear');await page.selectOption('#cap-profile','glass');
    await page.waitForTimeout(150);await page.evaluate(()=>v10.setView('hero'));await settle();
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await page.screenshot({path:path.join(out,'mobile-preview.png'),fullPage:true});
    assert.equal(errors.length,0);await browser.close();return;
  }
  if(stage==='capture'){
    const edition=process.argv[3],design=process.argv[4];
    assert(['current','raised'].includes(edition));assert(['original','clear','frosted','etched'].includes(design));
    await page.selectOption('#case-edition',edition);await page.selectOption('#case-design',design);
    await page.evaluate(()=>v10.setView('hero'));await shot(`${edition}-${design}-hero`);
    await page.evaluate(()=>v10.setView('top'));await shot(`${edition}-${design}-top`);
    if(edition==='raised'){
      await page.evaluate(()=>v10.setView('light'));await shot(`${edition}-${design}-detail`);
      await page.locator('#caps-visible').uncheck();await page.evaluate(()=>v10.setView('top'));await shot(`${edition}-${design}-plate`);
    }
    assert.equal(errors.length,0);assert.equal(network.length,0);
    console.log('Captured',edition,design);await browser.close();return;
  }
  if(stage==='caps'){
    await page.selectOption('#case-design','frosted');
    for(const profile of ['xvx-bow','xvx-wob','flat','glass','slim']){
      await page.selectOption('#cap-profile',profile);await page.evaluate(()=>v10.setView('hero'));await shot(`caps-${profile}-frosted`);
    }
    assert.equal(errors.length,0);await browser.close();return;
  }
  const combinations=stage==='features'?JSON.parse(fs.readFileSync(path.join(out,'matrix-validation.json'))).combinations:[];
  let rest=await page.evaluate(()=>v10.cad.getObjectByName('Illustrative components at existing fit coordinates').children.find(g=>g.name.startsWith('86 ')).children.map(m=>m.position.toArray()));
  if(stage==='validate'){
  for(const edition of ['current','raised']){
    await page.selectOption('#case-edition',edition);
    for(const profile of ['xvx-bow','xvx-wob','flat','glass','slim']){
      await page.selectOption('#cap-profile',profile);
      for(const design of ['original','clear','frosted','etched']){
        await page.selectOption('#case-design',design);
        const state=await page.evaluate(()=>{
          const v=v10,keys=v.cad.getObjectByName('Illustrative components at existing fit coordinates').children.find(g=>g.name.startsWith('86 '));
          const labels=v.cad.getObjectByName('Illustrative ANSI legends');
          return {...v.selection(),keys:keys.children.length,positions:keys.children.map(m=>m.position.toArray()),
            visibleAcrylic:Object.entries(v.acrylicGroups).filter(([,g])=>g.group.visible).map(([k])=>k),
            visibleRaised:Object.entries(v.raisedGroups).filter(([,g])=>g.visible).map(([k])=>k),
            originalVisible:v.partMeshes.find(m=>m.name==='upper').visible,
            emittingLegends:labels.children.filter(m=>m.material.emissiveIntensity>0).length,
            sources:v.pointLights.map(p=>p.position.toArray()),collectors:v.acrylicGroups[v.selection().edition].collectors.length};
        });
        assert.equal(state.keys,86);assert.equal(state.collectors,6);assert.equal(state.emittingLegends,0);
        assert.equal(state.edition,edition);assert.equal(state.design,design);assert.equal(state.profile,profile);
        assert.deepEqual(state.visibleAcrylic,design==='original'?[]:[edition]);
        assert.deepEqual(state.visibleRaised,design==='original'&&edition==='raised'?['original']:[]);
        assert.equal(state.originalVisible,design==='original'&&edition==='current');
        assert.deepEqual(state.sources.map(p=>p.slice(0,2)),manifest.led_positions_board_xy_mm);
        if(profile==='xvx-bow'&&design==='original'){
          if(rest)assert.deepEqual(state.positions,rest,'Case switching must leave all 86 keys in place');
          else rest=state.positions;
        }
        delete state.positions;combinations.push(state);
      }
      console.log('Checked',edition,profile,'in all four plate treatments');
    }
  }
  }
  const fields=await page.evaluate(()=>v10.fieldRecords);
  const weights=Object.values(fields).map(f=>f.integratedKernelWeight);
  assert(weights.every(w=>Math.abs(w-6*Math.PI)<1e-10));
  assert(fields.clear.peak>fields.frosted.peak,'Wider spread must not retain the clear-sheet peak');
  if(stage==='validate'){
    assert.equal(errors.length,0);assert.equal(network.length,0);
    fs.writeFileSync(path.join(out,'matrix-validation.json'),JSON.stringify({checked_at:new Date().toISOString(),combinations,fields,errors,network,passed:true},null,2)+'\n');
    console.log('Matrix passed:',combinations.length);await browser.close();return;
  }
  // The exact same six-source setup must visibly change when switched off.
  await page.selectOption('#cap-profile','xvx-bow');await page.selectOption('#case-design','etched');
  await page.locator('#leds').uncheck();await settle();
  const off=await page.evaluate(()=>({materials:['acrylicClear','acrylicFrosted','acrylicEtched','diffuser'].map(k=>v10.materials[k].emissiveIntensity),lights:v10.pointLights.map(p=>p.intensity)}));
  assert(off.materials.every(n=>n===0)&&off.lights.every(n=>n===0));
  await page.evaluate(()=>v10.setView('top'));await shot('lights-off-top');
  const offPixels=await page.evaluate(()=>v10.renderer.domElement.toDataURL());
  await page.locator('#leds').check();await settle();
  assert.notEqual(await page.evaluate(()=>v10.renderer.domElement.toDataURL()),offPixels);
  const backedStrength=await page.evaluate(()=>v10.materials.acrylicEtched.emissiveIntensity);
  await page.locator('#reflector').uncheck();
  assert(await page.evaluate(()=>Object.values(v10.acrylicGroups).every(g=>!g.reflector.visible)));
  assert(Math.abs((await page.evaluate(()=>v10.materials.acrylicEtched.emissiveIntensity))/backedStrength-.7)<1e-10);
  await shot('etched-without-backing-top');await page.locator('#reflector').check();
  // Full captures can be run in independent short browser batches.
  if(stage==='all'){
  for(const edition of ['current','raised']){
    await page.selectOption('#case-edition',edition);
    for(const design of ['original','clear','frosted','etched']){
      await page.selectOption('#case-design',design);
      await page.evaluate(()=>v10.setView('hero'));await shot(`${edition}-${design}-hero`);
      await page.evaluate(()=>v10.setView('top'));await shot(`${edition}-${design}-top`);
      if(edition==='raised'){
        await page.evaluate(()=>v10.setView('light'));await shot(`${edition}-${design}-detail`);
        await page.locator('#caps-visible').uncheck();
        assert.equal((await page.evaluate(()=>v10.selection())).capsVisible,false);
        await page.evaluate(()=>v10.setView('top'));await shot(`${edition}-${design}-plate`);
        await page.locator('#caps-visible').check();
      }
    }
  }
  // Keep the alternative keycaps available and supply a few actual comparisons.
  await page.selectOption('#case-design','frosted');
  for(const profile of ['xvx-bow','xvx-wob','flat','glass','slim']){
    await page.selectOption('#cap-profile',profile);await page.evaluate(()=>v10.setView('hero'));
    await shot(`caps-${profile}-frosted`);
  }
  }
  await page.selectOption('#cap-profile','xvx-bow');
  for(const view of ['hero','front','rear','side','top','bottom','edge','usb','light']){
    await page.locator(`[data-view="${view}"]`).click();await settle();
    assert.equal(await page.locator(`[data-view="${view}"]`).getAttribute('aria-pressed'),'true');
  }
  await page.evaluate(()=>v10.setView('hero'));
  const before=await page.evaluate(()=>v10.camera.position.toArray());
  const bounds=await page.locator('#viewport').boundingBox();
  await page.mouse.move(bounds.x+bounds.width*.4,bounds.y+bounds.height*.45);await page.mouse.down();
  await page.mouse.move(bounds.x+bounds.width*.6,bounds.y+bounds.height*.6,{steps:10});await page.mouse.up();
  const after=await page.evaluate(()=>v10.camera.position.toArray());
  assert(Math.hypot(...before.map((v,i)=>v-after[i]))>10);
  const zoom=await page.evaluate(()=>v10.camera.zoom);await page.mouse.wheel(0,-150);
  await page.waitForFunction(z=>v10.camera.zoom>z,zoom);
  await page.evaluate(()=>v10.renderer.setAnimationLoop(()=>{v10.controls.update(.025);v10.render()}));
  await page.locator('#spin').check();const angle=await page.evaluate(()=>v10.controls.getAzimuthalAngle());
  await page.waitForFunction(a=>Math.abs(v10.controls.getAzimuthalAngle()-a)>1e-6,angle);await page.locator('#spin').uncheck();
  await page.evaluate(()=>v10.renderer.setAnimationLoop(null));
  await page.locator('#key-travel').fill('2.8');await page.locator('#key-travel').dispatchEvent('input');
  const pressed=await page.evaluate(()=>v10.cad.getObjectByName('Illustrative components at existing fit coordinates').children.find(g=>g.name.startsWith('86 ')).children.map(m=>m.position.toArray()));
  for(let i=0;i<86;i++){assert.equal(rest[i][0],pressed[i][0]);assert.equal(rest[i][1],pressed[i][1]);assert(Math.abs(rest[i][2]-pressed[i][2]-2.8)<1e-8)}
  await page.locator('#key-travel').fill('0');await page.locator('#key-travel').dispatchEvent('input');
  await page.selectOption('#room','day');await page.evaluate(()=>v10.setView('hero'));await shot('daylight-frosted-hero');
  await page.selectOption('#room','dim');await page.selectOption('#case-design','etched');
  await page.evaluate(()=>v10.setView('hero'));
  const pngWait=page.waitForEvent('download');await page.locator('#save').click();
  await (await pngWait).saveAs(path.join(out,'v10-acrylic-preview.png'));
  const glbWait=page.waitForEvent('download');await page.locator('#download-model').click();
  const glbPath=path.join(out,'v10-raised-etched-acrylic.glb');await(await glbWait).saveAs(glbPath);
  const glb=fs.readFileSync(glbPath);assert.equal(glb.toString('utf8',0,4),'glTF');
  const doc=JSON.parse(glb.subarray(20,20+glb.readUInt32LE(12)).toString());
  assert(doc.nodes.some(n=>n.name==='raised acrylic switch plate'));
  assert(doc.nodes.some(n=>n.name==='raised white reflector backing'));
  assert.equal(doc.nodes.filter(n=>n.name?.includes('acrylic input collector')).length,6);
  assert(!doc.nodes.some(n=>n.name==='upper'||n.name==='current acrylic switch plate'));
  assert(doc.materials.some(m=>m.emissiveTexture),'Optical field maps must accompany the GLB');
  assert(doc.materials.some(m=>m.extensions?.KHR_materials_transmission));
  assert(doc.extensionsUsed?.includes('KHR_materials_emissive_strength'));
  await page.setViewportSize({width:390,height:844});await settle();
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile horizontal overflow');
  await page.selectOption('#case-design','clear');await page.selectOption('#case-edition','current');
  await page.selectOption('#cap-profile','glass');await page.selectOption('#case-edition','raised');
  assert.equal((await page.evaluate(()=>v10.selection())).profile,'glass');
  await page.evaluate(()=>v10.setView('hero'));await settle();
  await page.screenshot({path:path.join(out,'mobile-preview.png'),fullPage:true});
  await page.setViewportSize({width:1600,height:1000});await page.selectOption('#cap-profile','xvx-bow');
  await page.selectOption('#case-design','etched');await page.evaluate(()=>v10.setView('hero'));await settle();
  await page.locator('aside').evaluate(el=>el.scrollTop=0);
  await page.screenshot({path:path.join(out,'studio-preview.png')});
  for(const filename of ['provenance.json','acrylic-study.json']){
    for(const[relative,expected]of Object.entries(JSON.parse(fs.readFileSync(path.join(out,filename))).source_sha256)){
      assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,relative))).digest('hex'),expected,relative+' changed');
    }
  }
  const result={checked_at:new Date().toISOString(),browser:'Brave / Playwright / standalone offline file',passed:errors.length===0&&network.length===0,
    errors,network_requests:network,combinations,fields,glb_bytes:glb.length,source_files_unchanged:true,
    checks:['40 edition / material / cap combinations','six fixed LED positions and collectors','equal initial source-kernel weights; wider fields have lower peaks',
      'no emitting keycap legends','lights off and brightness control','white backing on/off','86 identical key positions and 2.8 mm travel',
      'caps-on and caps-off comparisons','nine cameras, orbit, zoom and auto-rotation','day/dim lighting','PNG export','selected GLB with optical textures and transmission','390px mobile layout','unchanged source CAD hashes']};
  fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({...result,combinations:combinations.length},null,2));
  await browser.close();assert(result.passed);
})().catch(e=>{console.error(e);process.exit(1)});
