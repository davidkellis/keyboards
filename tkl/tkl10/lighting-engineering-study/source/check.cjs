const path=require('path'),fs=require('fs'),assert=require('assert/strict'),crypto=require('crypto');
const modules=process.env.V10_RENDER_NODE_MODULES||path.resolve(__dirname,'../../render-case-editions/source/node_modules');
const{chromium}=require(path.join(modules,'playwright'));
const{pathToFileURL}=require('url');
(async()=>{
 const out=path.resolve(__dirname,'..'),root=path.dirname(out),data=JSON.parse(fs.readFileSync(path.join(out,'study.json')));
 const browser=await chromium.launch({executablePath:'/usr/bin/brave-browser',headless:true,args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:1440,height:1100}}),errors=[],network=[];
 await context.route(/^https?:/,r=>{network.push(r.request().url());r.abort()});
 const p=await context.newPage();p.on('pageerror',e=>errors.push(String(e)));
 await p.goto(pathToFileURL(path.join(out,'index.html')).href);await p.waitForFunction(()=>window.lightingStudy);
 const baseline=await p.evaluate(()=>lightingStudy.calculate());
 assert(Math.abs(baseline.days-30.136284038070418)<1e-8);
 const initialPower=baseline.lightingMw;
 assert.equal(await p.locator('#keyboard .led').count(),86);
 for(const count of [24,6,86]){
  await p.selectOption('#count',String(count));
  assert.equal(await p.locator('#keyboard .led').count(),count);
  const r=await p.evaluate(()=>lightingStudy.calculate());assert(Math.abs(r.lightingMw-initialPower)<1e-5,'Equal-power source-count comparison');
 }
 await p.locator('#hold').uncheck();await p.selectOption('#count','86');await p.locator('#current').fill('0.2');
 const middle=await p.evaluate(()=>lightingStudy.calculate());assert(Math.abs(middle.days-15.945102204556145)<1e-8);
 for(const h of [0,6,12,24]){
  await p.locator('#hours').fill(String(h));await p.locator('#hours').dispatchEvent('input');
  const r=await p.evaluate(()=>lightingStudy.calculate());assert(Number.isFinite(r.days)&&r.days>0);
  if(h===24)assert(Math.abs(r.days*24-r.continuous)<1e-8);
 }
 await p.locator('#hours').fill('12');await p.locator('#hours').dispatchEvent('input');
 await p.locator('#month-budget').click();assert(Math.abs((await p.evaluate(()=>lightingStudy.calculate())).lightingMa-10)<1e-5);
 await p.locator('#normal-budget').click();assert(Math.abs((await p.evaluate(()=>lightingStudy.calculate())).lightingMa-20)<1e-5);
 await p.locator('#current').fill('0.1');await p.locator('#hold').check();
 for(const id of ['capacity','usable','rail','eff','active','sleep','self'])assert(await p.locator('#'+id).count());
 // Download paths are local and point to actual engineering files.
 const links=await p.locator('a[href]').evaluateAll(as=>as.map(a=>a.getAttribute('href')).filter(h=>!/^https?:/.test(h)));
 for(const link of links)assert(fs.existsSync(path.resolve(out,link)),link);
 for(const[rel,sha]of Object.entries(data.source_sha256))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,rel))).digest('hex'),sha);
 await p.screenshot({path:path.join(out,'design-preview.png'),fullPage:true});
 await p.locator('section.card').nth(1).screenshot({path:path.join(out,'power-budget-preview.png')});
 await p.setViewportSize({width:390,height:844});
 assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile horizontal overflow');
 await p.screenshot({path:path.join(out,'mobile-preview.png'),fullPage:true});
 const report={passed:errors.length===0&&network.length===0,errors,network_requests:network,source_files_unchanged:true,
  zmk_reproduced_days:data.zmk_screenshot.days,runtime_scenarios:data.runtime_scenarios,
  checks:['calculator matches independent energy calculations','source-count switch retains electrical power','6 / 24 / 86 source diagrams','0 / 6 / 12 / 24 hour boundary cases','battery budget presets','all local reference/coupon links','390px responsive layout','original V10 source hashes'],
  physical_photometry_verified:false,production_pcb_released:false,firmware_compiled:false};
 fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));await browser.close();assert(report.passed);
})().catch(e=>{console.error(e);process.exit(1)});
