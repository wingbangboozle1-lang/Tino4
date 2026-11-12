// Optional browser smoke test. Install playwright-core and @sparticuz/chromium
// under _7eff7e24/browser; serve only public files on port 8000 first.
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const modules = path.join(__dirname, '../_7eff7e24/browser/node_modules');
const { chromium: playwright } = require(path.join(modules, 'playwright-core'));
(async () => {
  const {default: chromium} = await import(path.join(modules, '@sparticuz/chromium/build/index.js'));
  const browser = await playwright.launch({args:chromium.args,executablePath:await chromium.executablePath(),headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  const errors=[]; const unexpected=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:8000/'))unexpected.push(r.url());});
  fs.mkdirSync(path.join(__dirname,'../_7eff7e24/screenshots'),{recursive:true});
  const manifest = JSON.parse(fs.readFileSync(path.join(__dirname,'../_7eff7e24/manifest.json')));
  for (const file of manifest) {
    const response=await page.goto('http://127.0.0.1:8000/'+file);
    assert.equal(response.status(),200,file);
    assert.equal(await page.locator('h1').count(),1,file);
    assert.equal(await page.locator('nav a[aria-current="page"]').count(),1,file);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,file+' page overflow');
  }
  await page.goto('http://127.0.0.1:8000/index.html');
  await page.screenshot({path:path.join(__dirname,'../_7eff7e24/screenshots/desktop.png'),fullPage:true});
  await page.goto('http://127.0.0.1:8000/pages/projections.html');
  assert.equal(await page.locator('.projection-group:not([hidden])').getAttribute('data-year'),'2045');
  await page.selectOption('#inherit-year','2050');
  assert.equal(await page.locator('.projection-group:not([hidden])').getAttribute('data-year'),'2050');
  await page.goto('http://127.0.0.1:8000/pages/suggestions.html');
  await page.selectOption('[data-id="S01"]','Investigate');
  assert.match(await page.locator('#review-summary').textContent(),/1 of 17/);
  await page.reload();
  assert.equal(await page.locator('[data-id="S01"]').inputValue(),'Investigate');
  await page.click('#reset-reviews');
  assert.equal(await page.locator('[data-id="S01"]').inputValue(),'Not reviewed');
  assert.match(await page.locator('#review-summary').textContent(),/0 of 17/);
  await page.setViewportSize({width:390,height:844});
  for (const file of manifest) {
    await page.goto('http://127.0.0.1:8000/'+file);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,file+' mobile overflow');
  }
  await page.goto('http://127.0.0.1:8000/index.html');
  await page.screenshot({path:path.join(__dirname,'../_7eff7e24/screenshots/mobile.png'),fullPage:true});
  await page.route('**/*',route=>route.continue());
  assert.deepEqual(errors,[]);
  assert.deepEqual(unexpected,[]);
  console.log('Browser passed: 17 desktop + 17 mobile pages; projection selector; persisted/reset reviews; no JS errors or third-party requests.');
  await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
