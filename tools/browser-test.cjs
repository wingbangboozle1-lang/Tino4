// Optional browser smoke test. Install playwright-core and @sparticuz/chromium
// under _7eff7e24/browser; serve only public files on port 8000 first.
// If the system lacks NSS/NSPR shared libraries, put them on LD_LIBRARY_PATH
// (for example the nss-libs folder under _7eff7e24/browser).
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
  const manifest = JSON.parse(fs.readFileSync(path.join(__dirname,'../_7adb71fc/manifest.json')));
  for (const file of manifest) {
    const response=await page.goto('http://127.0.0.1:8000/'+file);
    assert.equal(response.status(),200,file);
    assert.equal(await page.locator('h1').count(),1,file);
    assert.equal(await page.locator('nav a[aria-current="page"]').count(),1,file);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,file+' page overflow');
  }
  await page.goto('http://127.0.0.1:8000/index.html');
  await page.screenshot({path:path.join(__dirname,'../_7eff7e24/screenshots/desktop.png'),fullPage:true});
  // Review queue: choices persist locally and reset; nothing is implemented.
  await page.goto('http://127.0.0.1:8000/pages/suggestions.html');
  const total = await page.locator('.review-choice').count();
  assert.ok(total >= 8, 'expected a populated review queue, found ' + total);
  const first = await page.locator('.review-choice').first().getAttribute('data-id');
  await page.selectOption(`.review-choice[data-id="${first}"]`, 'Investigate');
  assert.match(await page.locator('#review-summary').textContent(), new RegExp('1 of ' + total));
  await page.reload();
  assert.equal(await page.locator(`.review-choice[data-id="${first}"]`).inputValue(), 'Investigate');
  await page.click('#reset-reviews');
  assert.equal(await page.locator(`.review-choice[data-id="${first}"]`).inputValue(), 'Not reviewed');
  assert.match(await page.locator('#review-summary').textContent(), new RegExp('0 of ' + total));
  // The phased-entry calculator updates locally, exposes a synthetic scenario,
  // and never stores the selected amount or market path.
  await page.goto('http://127.0.0.1:8000/pages/black-swan.html');
  assert.equal(await page.locator('#phase-staged-value').textContent(), '$113,840');
  await page.selectOption('#phase-sequence', '1929');
  const drawdownValue = await page.locator('#phase-staged-value').textContent();
  assert.equal(drawdownValue, '$84,030');
  await page.selectOption('#phase-wait', '36');
  const bridge36Value = await page.locator('#phase-staged-value').textContent();
  assert.equal(bridge36Value, '$111,030');
  await page.selectOption('#phase-immediate', '0.25');
  assert.notEqual(await page.locator('#phase-staged-value').textContent(), bridge36Value);
  await page.locator('#phase-yield').fill('7');
  assert.match(await page.locator('#phase-error').textContent(), /gross yield from 0% to 6%/);
  await page.locator('#phase-yield').fill('3');
  assert.equal(await page.locator('#phase-error').textContent(), '');
  assert.deepEqual(await page.evaluate(() => Object.keys(localStorage)), []);
  await page.goto('http://127.0.0.1:8000/pages/advisor-brief.html');
  assert.equal(await page.locator('body').getAttribute('class'), 'advisor-print');
  await page.emulateMedia({media:'print'});
  assert.equal(await page.locator('.page-heading').evaluate(el => getComputedStyle(el).display), 'none');
  const briefPdf = path.join(__dirname, '../_7eff7e24/browser/advisor-brief-print-test.pdf');
  await page.pdf({path:briefPdf, format:'Letter', printBackground:true, preferCSSPageSize:true});
  const pdfText = fs.readFileSync(briefPdf, 'latin1');
  const printedPages = pdfText.split('/Type /Page').length - 1 - (pdfText.split('/Type /Pages').length - 1);
  assert.equal(printedPages, 1, 'advisor briefing sheet should print as one page');
  fs.unlinkSync(briefPdf);
  await page.emulateMedia({media:'screen'});
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
  console.log(`Browser passed: ${manifest.length} desktop + ${manifest.length} mobile pages; ${total} persisted/reset reviews; no JS errors or third-party requests.`);
  await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
