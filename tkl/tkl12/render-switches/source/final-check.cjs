const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),crypto=require('crypto');
const {pathToFileURL}=require('node:url');
const out=path.resolve(__dirname,'..'),modules=path.resolve(out,'../../tkl10/render-case-editions/source/node_modules');
const {chromium}=require(path.join(modules,'playwright'));
const quick=process.argv.includes('--quick');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/brave-browser',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader','--disable-dev-shm-usage']});
 try{
 const context=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 const errors=[],network=[];await context.route(/^https?:/,r=>{network.push(r.request().url());return r.abort()});
 const page=await context.newPage();page.setDefaultTimeout(90000);page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(pathToFileURL(path.join(out,'index.html')).href);await page.waitForFunction(()=>window.v12?.ready);
 await page.evaluate(()=>v12.renderer.setAnimationLoop(null));
 console.log('Final HTML loaded.');
 await page.selectOption('#cap-profile','nsa-coast');
 const color=await page.evaluate(()=>Object.fromEntries(v12.capMeshes.filter(c=>['Esc','Enter','Space'].includes(c.userData.label)).map(c=>[c.userData.label,'#'+c.material.color.getHexString()])));
 assert.deepEqual(color,{Esc:'#61c7b1',Enter:'#e16c3c',Space:'#dfb92c'});
 if(!quick){await page.evaluate(()=>v12.render());await page.locator('#viewport').screenshot({path:path.join(out,'views','choc-v2-nsa-coast.png')});}
 console.log('Reference palette and material overrides pass.');
 await page.selectOption('#switch-family','choc-v1');await page.selectOption('#cap-profile','mbk-chili');
 assert.equal(await page.evaluate(()=>v12.materials.alpha.color.getHexString()),'eeeae6');
 if(!quick){await page.evaluate(()=>v12.render());await page.locator('#viewport').screenshot({path:path.join(out,'views','choc-v1-mbk-chili.png')});}
 await page.selectOption('#switch-family','gateron-heron');await page.selectOption('#cap-profile','nsa-coast');
 assert.equal(await page.evaluate(()=>v12.selection().plateTop),2.5);
 if(!quick){await page.evaluate(()=>v12.render());await page.locator('#viewport').screenshot({path:path.join(out,'views','gateron-heron-nsa-coast.png')});}
 // Cap-family labels remain correct in a narrow viewport.
 await page.setViewportSize({width:390,height:844});await page.selectOption('#switch-family','choc-v1');await page.selectOption('#cap-profile','cfx-white');
 assert.equal(await page.evaluate(()=>v12.selection().customCaps),2);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 await page.evaluate(()=>v12.setView('hero'));
 await page.screenshot({path:path.join(out,'views','mobile.png')});
 assert.deepEqual(errors,[]);assert.deepEqual(network,[]);
 const report={passed:true,checkedAt:new Date().toISOString(),htmlSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(out,'index.html'))).digest('hex'),checks:['final offline HTML loaded in Brave','NuPhy individual key accent colours','MBK palette','Gateron height preview','Choc-only profile filter and custom widths','mobile layout without horizontal overflow'],pageErrors:errors,networkRequests:network};
 fs.writeFileSync(path.join(out,'final-check.json'),JSON.stringify(report,null,2)+'\n');console.log('PASS final artifact:',report.htmlSha256);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
