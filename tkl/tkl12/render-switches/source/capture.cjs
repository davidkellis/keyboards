/* Validate the offline artifact in Brave, using actual selectors and exports. */
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),crypto=require('crypto');
const {pathToFileURL}=require('node:url');
const out=path.resolve(__dirname,'..'),repo=path.resolve(out,'../../..');
const modules=process.env.V12_RENDER_NODE_MODULES||path.resolve(out,'../../tkl10/render-case-editions/source/node_modules');
const {chromium}=require(path.join(modules,'playwright'));
const takeShots=process.argv.includes('--capture');
(async()=>{
 fs.mkdirSync(path.join(out,'views'),{recursive:true});
 const browser=await chromium.launch({executablePath:'/usr/bin/brave-browser',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader','--disable-dev-shm-usage']});
 try{
 const context=await browser.newContext({viewport:{width:1560,height:1080},deviceScaleFactor:1,acceptDownloads:true});
 const errors=[],network=[];await context.route(/^https?:/,r=>{network.push(r.request().url());return r.abort()});
 const page=await context.newPage();page.setDefaultTimeout(60000);
 page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 await page.goto(pathToFileURL(path.join(out,'index.html')).href);
 await page.waitForFunction(()=>window.v12?.ready);
 await page.evaluate(()=>v12.renderer.setAnimationLoop(null));
 const draw=()=>page.evaluate(()=>v12.render());
 const shot=async name=>{if(!takeShots)return;await draw();await page.locator('#viewport').screenshot({path:path.join(out,'views',name+'.png')})};
 await shot('whale-xvx-overview');
 if(takeShots)await page.screenshot({path:path.join(out,'views','studio.png')});
 if(!takeShots)await page.evaluate(()=>{window.testRender=v12.renderer.render.bind(v12.renderer);v12.renderer.render=()=>{}});
 console.log('Initial viewer loaded and ready.');
 const combinations=[];
 const families=await page.evaluate(()=>Object.keys(v12.switchFamilies));
 for(const family of families){
   await page.selectOption('#switch-family',family);
   const profiles=await page.locator('#cap-profile option').evaluateAll(opts=>opts.map(o=>o.value));
   const meta=await page.evaluate(()=>v12.switchFamilies[v12.selection().switch]);
   assert.equal(profiles.length,meta.mount==='choc'?3:6);
   for(const profile of profiles){
     await page.selectOption('#cap-profile',profile);
     const state=await page.evaluate(()=>{
       v12.cad.updateMatrixWorld(true);
       const g=v12.acrylicGroups[v12.selection().edition];
       return {selection:v12.selection(),keys:v12.keys.children.length,stems:v12.stemMeshes.length,
         heights:v12.capMeshes.map(c=>({rest:c.userData.restZ,z:c.position.z,mount:c.userData.mount,height:c.userData.nominalHeight})),
         switchLayer:v12.switchBodies.parent.parent===v12.assembly.layers.switches,
         lift:g.group.position.toArray(),
         coverage:!document.querySelector('#coverage-note').hidden,
         travelMax:Number(document.querySelector('#key-travel').max),
         source:v12.profiles[v12.selection().profile].mount,
         leds:v12.pointLights.length};
     });
     assert.equal(state.keys,86);assert.equal(state.stems,86);assert.equal(state.switchLayer,true);assert.equal(state.leds,10);
     assert.equal(state.source,meta.mount);assert.equal(state.travelMax,meta.travel);
     assert.equal(state.selection.switch,family);assert.equal(state.selection.profile,profile);
     const expected=1.6+meta.stemTip-state.selection.seat;
     for(const c of state.heights){assert(Math.abs(c.rest-expected)<1e-9);assert.equal(c.mount,meta.mount);}
     const delta=meta.plateTop-2.2;assert(Math.abs(Math.hypot(...state.lift)-delta)<1e-8);
     if(profile==='cfx-white'){assert.equal(state.selection.customCaps,2);assert.equal(state.coverage,true);}
     else if(profile==='mbk-glow'){assert(state.selection.customCaps>2);assert.equal(state.coverage,true);}
     else assert.equal(state.coverage,false);
     await page.locator('#key-travel').evaluate((el,max)=>{el.value=max;el.dispatchEvent(new Event('input',{bubbles:true}))},meta.travel);
     const pressed=await page.evaluate(()=>({caps:v12.capMeshes.every(c=>Math.abs(c.position.z-(c.userData.restZ-v12.selection().travel))<1e-8),stems:v12.stemMeshes.every(c=>Math.abs(c.position.z-(c.userData.restZ-v12.selection().travel))<1e-8)}));
     assert.equal(pressed.caps,true);assert.equal(pressed.stems,true);
     await page.locator('#key-travel').evaluate(el=>{el.value=0;el.dispatchEvent(new Event('input',{bubbles:true}))});
     await page.evaluate(()=>v12.setView('hero'));
     if(family==='choc-v1'||family==='choc-v2'||profile==='nsa-coast')await shot(family+'-'+profile);
     combinations.push({family,profile,mount:meta.mount,plateTop:meta.plateTop,travel:meta.travel,customCaps:state.selection.customCaps});
   }
   await page.locator('#inspect-switches').click();
   assert.equal(await page.evaluate(()=>v12.assembly.layers.caps.visible),false);
   assert.equal(await page.evaluate(()=>v12.assembly.layers.top.visible),false);
   await shot(family+'-stems');
   await page.locator('#restore-caps').click();
   assert.equal(await page.evaluate(()=>v12.assembly.layers.caps.visible),true);
   assert.equal(await page.evaluate(()=>v12.assembly.layers.top.visible),true);
   // An incompatible programmatic profile request must also be ignored.
   const selected=await page.evaluate(()=>v12.selection().profile);
   await page.evaluate(mount=>v12.rebuildCaps(mount==='choc'?'xvx-bow':'cfx-white'),meta.mount);
   assert.equal(await page.evaluate(()=>v12.selection().profile),selected);
   console.log('Validated family:',family,profiles.length,'profiles');
 }
 await page.selectOption('#switch-family','choc-v2');await page.selectOption('#cap-profile','xvx-bow');
 console.log('All family/profile checks passed. Checking assembly controls.');
 const original=await page.evaluate(()=>{v12.cad.updateMatrixWorld(true);return Object.fromEntries(Object.entries(v12.assembly.layers).map(([id,g])=>[id,g.children.map(m=>({uuid:m.uuid,matrix:m.matrixWorld.toArray()}))]))});
 for(const edition of ['current','raised'])for(const treatment of ['original','clear','frosted','etched']){
   await page.selectOption('#case-edition',edition);await page.selectOption('#case-design',treatment);
   for(const amount of [0,.45,1]){
     const state=await page.evaluate(amount=>{
       v12.assembly.set(amount);v12.cad.updateMatrixWorld(true);
       return {selection:v12.selection(),layers:Object.fromEntries(Object.entries(v12.assembly.layers).map(([id,g])=>[id,g.position.z])),
         frames:Object.entries(v12.acrylicGroups).filter(([,g])=>g.frame.visible).map(([id])=>id),
         plates:Object.entries(v12.acrylicGroups).filter(([,g])=>g.group.visible).map(([id])=>id),
         emission:v12.materials.acrylicEtched.emissiveIntensity,legends:v12.legends.children.filter(m=>m.material.emissiveIntensity>0).length};
     },amount);
     assert.deepEqual(state.frames,[edition]);assert.deepEqual(state.plates,[edition]);assert.equal(state.legends,0);
     for(const[id,level]of Object.entries({bottom:0,battery:42,pcb:105,plate:165,top:225,switches:275,caps:320}))assert.equal(state.layers[id],level*amount);
     if(amount)assert.equal(state.emission,0);
   }
 }
 await page.selectOption('#case-edition','raised');await page.selectOption('#case-design','etched');
 await page.evaluate(()=>{v12.assembly.set(1);v12.setView('stack')});await shot('exploded');
 await page.evaluate(()=>v12.assembly.set(0));
 const restored=await page.evaluate(()=>{v12.cad.updateMatrixWorld(true);return Object.fromEntries(Object.entries(v12.assembly.layers).map(([id,g])=>[id,g.children.map(m=>({uuid:m.uuid,matrix:m.matrixWorld.toArray()}))]))});
 for(const[id,items]of Object.entries(original))for(const before of items){const after=restored[id].find(m=>m.uuid===before.uuid);assert(after);before.matrix.forEach((v,i)=>assert(Math.abs(v-after.matrix[i])<1e-9));}
 for(const id of ['bottom','battery','pcb','plate','top','switches']){
   await page.locator('#visible-'+id).uncheck();assert.equal(await page.evaluate(id=>v12.assembly.layers[id].visible,id),false);await page.locator('#visible-'+id).check();
 }
 await page.locator('#xray-case').check();assert.equal(await page.evaluate(()=>v12.materials.shell.opacity),.19);await page.locator('#xray-case').uncheck();
 await page.locator('#leds').uncheck();assert.equal(await page.evaluate(()=>v12.pointLights.every(l=>l.intensity===0)),true);await page.locator('#leds').check();
 await page.selectOption('#room','dim');await page.evaluate(()=>v12.setView('hero'));await shot('dim-acrylic');await page.selectOption('#room','day');
 await page.locator('[data-finish="chalk"]').click();await page.selectOption('#key-style','two-tone');await shot('chalk-two-tone');await page.locator('[data-finish="graphite"]').click();await page.selectOption('#key-style','source');
 console.log('Assembly matrices, layer controls and lighting passed.');
 for(const view of ['hero','top','front','rear','side','bottom','edge','usb','light','switch']){await page.locator('[data-view="'+view+'"]').click();await draw();}
 // Render a compact viewport for export checks; the high resolution option is
 // otherwise extremely slow with the headless SwiftShader software rasterizer.
 await page.setViewportSize({width:900,height:700});
 for(const id of ['bottom','battery','pcb','plate','top','caps'])await page.locator(id==='caps'?'#caps-visible':'#visible-'+id).uncheck();
 await page.evaluate(()=>{if(window.testRender)v12.renderer.render=window.testRender;v12.setView('hero')});
 const [download]=await Promise.all([page.waitForEvent('download',{timeout:180000}),page.locator('#save').click({timeout:180000})]);await download.saveAs(path.join(out,'views','exported-view.png'));assert(fs.statSync(path.join(out,'views','exported-view.png')).size>10000);
 // Export a selected single visible assembly layer to keep the regression test compact.
 for(const id of ['bottom','battery','pcb','plate','top','caps'])await page.locator(id==='caps'?'#caps-visible':'#visible-'+id).uncheck();
 console.log('PNG download passed. Checking GLB.');
 const glb=await page.evaluate(async()=>{const b=await v12.exportGLB();return {bytes:b.length,magic:Array.from(b.slice(0,4))}});
 assert.deepEqual(glb.magic,[103,108,84,70]);assert(glb.bytes>100000);
 for(const id of ['bottom','battery','pcb','plate','top','caps'])await page.locator(id==='caps'?'#caps-visible':'#visible-'+id).check();
 await page.evaluate(()=>v12.setView('hero'));
 console.log('GLB passed. Checking mobile.');
 await page.setViewportSize({width:390,height:844});await page.evaluate(()=>v12.setView('hero'));await draw();await page.screenshot({path:path.join(out,'views','mobile.png')});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 await page.selectOption('#switch-family','choc-v1');await page.selectOption('#cap-profile','cfx-white');assert.equal(await page.evaluate(()=>v12.keys.children.length),86);
 const preserved=JSON.parse(fs.readFileSync(path.join(out,'preserved-sources.json')));
 for(const[file,hash]of Object.entries(preserved))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(repo,file))).digest('hex'),hash,file);
 assert.deepEqual(errors,[]);assert.deepEqual(network,[]);
 fs.writeFileSync(path.join(out,'validation.json'),JSON.stringify({passed:true,checkedAt:new Date().toISOString(),browser:'Brave / Playwright',offline:true,networkRequests:network,consoleErrors:errors,combinations,assemblyCombinations:24,sourceFilesPreserved:Object.keys(preserved).length,htmlSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(out,'index.html'))).digest('hex'),checks:['family-filtered keycaps','86 caps and moving stems','family contact and peg geometry','installed heights and plate lifts','full travel per reference','custom cap width warnings','all layer visibility','explosion matrix round trip','both case editions and four plate treatments','no detached lighting or fake emissive legends','PNG download','selected GLB export','all camera presets','mobile layout']},null,2)+'\n');
 console.log('PASS:',combinations.length,'switch/cap combinations; 24 assembly states; offline, exports and mobile.');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1)});
