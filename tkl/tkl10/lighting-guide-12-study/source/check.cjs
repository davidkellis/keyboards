const fs=require('fs');
const path=require('path');
const assert=require('assert/strict');
const {chromium}=require(process.env.V10_RENDER_NODE_MODULES+'/playwright');
(async()=>{
 const out=path.resolve(__dirname,'..');
 const browser=await chromium.launch({executablePath:'/usr/bin/brave-browser',headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:960}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('https://**',r=>r.abort());
  await page.goto('file://'+out+'/index.html');
  assert.equal(await page.locator('.led-source').count(),10);
  assert.equal(await page.locator('#days').innerText(),'27.7');
  await page.screenshot({path:out+'/design-preview.png',fullPage:true});
  const before=await page.locator('#days').innerText();
  await page.selectOption('#count','12');
  assert.equal(await page.locator('.led-source').count(),12);
  assert.equal(await page.locator('#days').innerText(),before);
  assert.equal(await page.locator('#led-current').innerText(),'0.84');
  await page.fill('#hours','6');
  assert.equal(await page.locator('#days').innerText(),'52.7');
  await page.fill('#power','80');
  assert.equal(await page.locator('#days').innerText(),'28.4');
  for(const n of ['6','8','10','12']){
   await page.selectOption('#count',n);assert.equal(await page.locator('.led-source').count(),+n);
  }
  await page.selectOption('#count','10');await page.fill('#power','40');await page.fill('#hours','12');
  await page.setViewportSize({width:390,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:out+'/mobile-preview.png',fullPage:true});
  assert.deepEqual(errors,[]);
  const report={passed:true,offline:true,sourceCounts:[6,8,10,12],fixedPowerRuntimeCountIndependent:true,mobileNoHorizontalOverflow:true,pageErrors:errors};
  fs.writeFileSync(out+'/browser-validation.json',JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
