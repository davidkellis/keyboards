/* Exercise the real offline V11 WebGL studio, including assembly round trips. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {pathToFileURL}=require('url');
const out=path.resolve(__dirname,'..'),repo=path.resolve(out,'../../..');
const modules=process.env.V11_RENDER_NODE_MODULES||path.resolve(out,'../../tkl10/render-case-editions/source/node_modules');
const {chromium}=require(path.join(modules,'playwright'));
const stage=process.argv[2]||'validate';
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/brave-browser',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader','--disable-dev-shm-usage']});
 const context=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 const errors=[],network=[];await context.route(/^https?:/,r=>{network.push(r.request().url());r.abort()});
 const page=await context.newPage();page.setDefaultTimeout(60000);
 page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 await page.goto(pathToFileURL(path.join(out,'index.html')).href);await page.waitForFunction(()=>window.v11?.ready);
 await page.evaluate(()=>v11.renderer.setAnimationLoop(null));
 const draw=()=>page.evaluate(()=>v11.render());
 const shot=async name=>{await draw();await page.locator('#viewport').screenshot({path:path.join(out,'views',name+'.png')})};
 const original=await page.evaluate(()=>{
   v11.cad.updateMatrixWorld(true);
   return Object.fromEntries(Object.entries(v11.assembly.layers).map(([id,layer])=>[id,{position:layer.position.toArray(),children:layer.children.map(m=>({uuid:m.uuid,matrix:m.matrixWorld.toArray()}))}]));
 });
 const source=JSON.parse(fs.readFileSync(path.join(out,'provenance.json')));
 const checks=[],combinations=[];
 if(stage==='validate'){
   for(const edition of ['current','raised'])for(const profile of ['xvx-bow','xvx-wob','flat','glass','slim']){
     await page.selectOption('#case-edition',edition);await page.selectOption('#cap-profile',profile);
     for(const treatment of ['original','clear','frosted','etched']){
       await page.selectOption('#case-design',treatment);
       for(const amount of [0,.45,1]){
         const state=await page.evaluate(amount=>{
           v11.assembly.set(amount);v11.cad.updateMatrixWorld(true);
           return {selection:v11.selection(),keys:v11.keys.children.length,
             layers:Object.fromEntries(Object.entries(v11.assembly.layers).map(([id,g])=>[id,g.position.toArray()])),
             frames:Object.entries(v11.acrylicGroups).filter(([,g])=>g.frame.visible).map(([id])=>id),
             plates:Object.entries(v11.acrylicGroups).filter(([,g])=>g.group.visible).map(([id])=>id),
             sources:v11.pointLights.map(l=>({ref:l.userData.ledRef,xy:l.position.toArray().slice(0,2)})),
             collectors:v11.acrylicGroups[v11.selection().edition].collectors.length,
             glowingLegends:v11.legends.children.filter(l=>l.material.emissiveIntensity>0).length,
             plateEmission:v11.materials.acrylicEtched.emissiveIntensity};
         },amount);
         assert.equal(state.keys,86);assert.equal(state.collectors,10);assert.equal(state.glowingLegends,0);
         assert.deepEqual(state.frames,[edition]);assert.deepEqual(state.plates,[edition]);
         assert.equal(state.selection.exploded,amount);assert.equal(state.selection.profile,profile);
         const levels={bottom:0,battery:42,pcb:105,plate:165,top:225,switches:275,caps:320};
         for(const[id,pos]of Object.entries(state.layers))assert.deepEqual(pos,[0,0,levels[id]*amount]);
         for(const led of state.sources)for(let i=0;i<2;i++)assert(Math.abs(led.xy[i]-source.led_positions_board_xy_mm[led.ref][i])<.00001);
         if(amount)assert.equal(state.plateEmission,0,'Detached plate must not glow from PCB sources');
         combinations.push({edition,profile,treatment,amount});
       }
     }
     console.log('Checked',edition,profile,'in four treatments and three separation states');
   }
   await page.selectOption('#case-edition','raised');await page.selectOption('#cap-profile','xvx-bow');await page.selectOption('#case-design','etched');await page.evaluate(()=>v11.assembly.set(0));
   const restored=await page.evaluate(()=>{v11.cad.updateMatrixWorld(true);return Object.fromEntries(Object.entries(v11.assembly.layers).map(([id,g])=>[id,g.children.map(m=>({uuid:m.uuid,matrix:m.matrixWorld.toArray()}))]))});
   for(const[id,g]of Object.entries(original)){
     const fixed=id==='caps'?g.children.filter((_,i)=>i<2):g.children;
     for(const item of fixed){const after=restored[id].find(m=>m.uuid===item.uuid);assert(after,'Lost assembly child '+id);after.matrix.forEach((n,i)=>assert(Math.abs(n-item.matrix[i])<1e-9));}
   }
   for(const id of ['bottom','battery','pcb','plate','top','switches']){
     await page.locator('#visible-'+id).uncheck();assert.equal(await page.evaluate(id=>v11.assembly.layers[id].visible,id),false);await page.locator('#visible-'+id).check();
   }
   await page.locator('#visible-hardware').uncheck();assert(await page.evaluate(()=>v11.assembly.hardware.every(m=>!m.visible)));await page.locator('#visible-hardware').check();
   await page.locator('#caps-visible').uncheck();assert.equal(await page.evaluate(()=>v11.assembly.layers.caps.visible),false);await page.locator('#caps-visible').check();
   await page.locator('#xray-case').check();assert.equal(await page.evaluate(()=>v11.materials.shell.opacity),.19);await page.locator('#xray-case').uncheck();
   await page.locator('#key-travel').fill('2.8');await page.locator('#key-travel').dispatchEvent('input');assert(await page.evaluate(()=>v11.keys.children.every(k=>Math.abs(k.userData.restZ-k.position.z-2.8)<1e-9)));
   await page.locator('#key-travel').fill('0');await page.locator('#key-travel').dispatchEvent('input');
   await page.locator('#seat-depth').fill('2.4');await page.locator('#seat-depth').dispatchEvent('input');assert.equal((await page.evaluate(()=>v11.selection())).seat,2.4);
   await page.locator('#seat-depth').fill('3');await page.locator('#seat-depth').dispatchEvent('input');
   await page.locator('#leds').uncheck();assert(await page.evaluate(()=>v11.pointLights.every(p=>p.intensity===0)&&v11.materials.acrylicEtched.emissiveIntensity===0));await page.locator('#leds').check();
   await page.locator('#reflector').uncheck();assert(await page.evaluate(()=>Object.values(v11.acrylicGroups).every(p=>!p.reflector.visible)));await page.locator('#reflector').check();
   await page.evaluate(()=>{v11.assembly.set(1);v11.renderer.setAnimationLoop(()=>{v11.assembly.tick(performance.now());v11.controls.update(.02);v11.render()})});
   await page.locator('#assemble').click();await page.waitForFunction(()=>v11.assembly.amount===0);await page.locator('#explode').click();await page.waitForFunction(()=>v11.assembly.amount===1);
   await page.locator('#assembly-labels').uncheck();await draw();assert(await page.locator('#layer-labels').isHidden());await page.locator('#assembly-labels').check();
   await page.locator('#spin').check();const angle=await page.evaluate(()=>v11.controls.getAzimuthalAngle());await page.waitForFunction(a=>Math.abs(v11.controls.getAzimuthalAngle()-a)>.00001,angle);await page.locator('#spin').uncheck();
   await page.evaluate(()=>v11.renderer.setAnimationLoop(null));
   const fields=await page.evaluate(()=>v11.fieldRecords);for(const f of Object.values(fields))assert(Math.abs(f.integratedKernelWeight-10*Math.PI)<1e-9);
   checks.push('120 case/profile/treatment/separation combinations','assembly matrices restored exactly at zero separation','ten real V11 LED locations and ten optical entry models','seven independent layer visibilities and hardware control','case transparency','86 caps and 2.8 mm key travel','socket engagement','lighting and reflector controls','no light transfer to detached plate','no luminous legends','animated assembly buttons','layer labels','auto-rotation','ten-source field normalization');
 }
 if(stage==='stack'){
   await page.evaluate(()=>{v11.assembly.set(1);v11.setView('stack')});await shot('exploded-stack');await page.screenshot({path:path.join(out,'exploded-preview.png')});
   await page.evaluate(()=>v11.assembly.set(.55));await shot('partially-exploded');
   await page.evaluate(()=>{v11.assembly.set(0);v11.setView('hero')});await page.screenshot({path:path.join(out,'studio-preview.png')});
   await page.setViewportSize({width:390,height:844});await page.evaluate(()=>{v11.assembly.set(.8);v11.setView('stack');v11.render()});
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(out,'mobile-preview.png'),fullPage:true});
   checks.push('final exploded stack framing','intermediate layer spacing','assembled zero-separation appearance','mobile exploded layout');
 }
 if(stage==='capture'){
   await page.locator('#assembly-labels').check();await page.evaluate(()=>v11.assembly.set(0));
   for(const view of ['hero','top','front','rear','side','bottom','edge','usb','light']){
     await page.evaluate(view=>v11.setView(view),view);await shot('assembled-'+view);console.log('Captured assembled',view);
   }
   await page.evaluate(()=>{v11.assembly.set(1);v11.setView('stack')});await shot('exploded-stack');await page.screenshot({path:path.join(out,'exploded-preview.png')});
   await page.evaluate(()=>v11.assembly.set(.55));await shot('partially-exploded');
   await page.locator('#visible-top').uncheck();await page.locator('#caps-visible').uncheck();await page.locator('#visible-switches').uncheck();await page.locator('#visible-plate').uncheck();await page.evaluate(()=>{v11.assembly.set(0);v11.setView('top')});await shot('pcb-ten-led-locations');
   for(const id of ['top','switches','plate'])await page.locator('#visible-'+id).check();await page.locator('#caps-visible').check();
   await page.selectOption('#cap-profile','glass');await page.selectOption('#case-edition','current');await page.evaluate(()=>v11.setView('hero'));await shot('floating-scottocaps-glass');
   await page.selectOption('#case-edition','raised');await page.selectOption('#cap-profile','xvx-wob');await page.selectOption('#room','dim');await page.evaluate(()=>v11.setView('hero'));await shot('dim-xvx-wob');
   await page.selectOption('#room','day');await page.selectOption('#cap-profile','xvx-bow');await page.evaluate(()=>v11.setView('hero'));await page.screenshot({path:path.join(out,'studio-preview.png')});
   await page.setViewportSize({width:390,height:844});await page.evaluate(()=>{v11.assembly.set(.8);v11.setView('stack');v11.render()});
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(out,'mobile-preview.png'),fullPage:true});
   checks.push('nine assembled viewpoints','exploded and intermediate stack captures','isolated actual PCB capture','ScottoCaps and XVX comparison captures','day and dim lighting','390px mobile layout');
 }
 if(stage==='exports'){
   await page.evaluate(()=>v11.assembly.set(0));await page.evaluate(()=>v11.setView('hero'));
   const before=await page.evaluate(()=>v11.camera.position.toArray()),bounds=await page.locator('#viewport').boundingBox();
   await page.mouse.move(bounds.x+bounds.width*.4,bounds.y+bounds.height*.5);await page.mouse.down();await page.mouse.move(bounds.x+bounds.width*.55,bounds.y+bounds.height*.6,{steps:5});await page.mouse.up();
   assert.notDeepEqual(await page.evaluate(()=>v11.camera.position.toArray()),before);
   const zoom=await page.evaluate(()=>v11.camera.zoom);await page.mouse.wheel(0,-200);await page.waitForFunction(z=>v11.camera.zoom>z,zoom);
   await page.evaluate(()=>v11.setView('hero'));
   for(const amount of [0,1]){
     await page.evaluate(v=>v11.assembly.set(v),amount);const state=amount?'exploded':'assembled';
     const png=page.waitForEvent('download');await page.locator('#save').click();await(await png).saveAs(path.join(out,'v11-'+state+'.png'));
     const glb=page.waitForEvent('download');await page.locator('#download-model').click();const file=path.join(out,'v11-'+state+'.glb');await(await glb).saveAs(file);
     const bytes=fs.readFileSync(file);assert.equal(bytes.toString('utf8',0,4),'glTF');const doc=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
     for(const [name,z]of [['V11 PCB + electronics',105],['Acrylic switch plate',165],['Top case frame',225],['5000 mAh battery',42],['Lower case',0]]){
       const node=doc.nodes.find(n=>n.name===name);assert(node,name);assert(Math.abs((node.translation?.[2]??node.matrix?.[14]??0)-z*amount)<1e-9,name);
     }
     assert.equal(doc.nodes.filter(n=>/LED\d+ reverse-mount LED body/.test(n.name)).length,10);
     assert(doc.nodes.some(n=>n.name==='raised V11 acrylic switch plate — fit trial'));assert(!doc.nodes.some(n=>n.name==='current V11 acrylic switch plate — fit trial'));
     console.log('Exported and verified',state,bytes.length,'GLB bytes');
   }
   checks.push('free orbit','wheel zoom','high-resolution PNG downloads','assembled and exploded GLB downloads','exported layer transforms','ten LED packages exported','only selected case edition exported');
 }
 for(const [name,sha]of Object.entries(source.source_sha256))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(repo,name))).digest('hex'),sha,name+' changed');
 assert.deepEqual(errors,[]);assert.deepEqual(network,[]);
 fs.writeFileSync(path.join(out,stage+'-validation.json'),JSON.stringify({stage,passed:true,checked_at:new Date().toISOString(),browser:'Brave / Playwright / offline file',checks,combinations,errors,network,source_files_unchanged:true},null,2)+'\n');
 await browser.close();console.log(stage,'passed',checks.length,'checks');
})().catch(e=>{console.error(e);process.exit(1)});
