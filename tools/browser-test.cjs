// Optional Playwright smoke test. Serve the repository root on port 8000 first.
// Browser dependencies are located via BROWSER_MODULES or tools/browser/node_modules.
// Nothing here is required for the site to build; it is a rendering and script
// check that runs only where the optional dependencies are installed.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const candidates = [
  process.env.BROWSER_MODULES,
  path.join(__dirname, 'browser', 'node_modules'),
  path.join(process.cwd(), 'node_modules'),
].filter(Boolean);
const foundModules = candidates.find(candidate => fs.existsSync(path.join(candidate, 'playwright-core')));
const modules = foundModules ? path.resolve(foundModules) : null;
if (!modules) throw new Error('Playwright not found; set BROWSER_MODULES or install optional browser-test dependencies.');
const { chromium: playwright } = require(path.join(modules, 'playwright-core'));

(async () => {
  const { default: chromium } = await import(path.join(modules, '@sparticuz/chromium/build/index.js'));
  const browser = await playwright.launch({
    args: chromium.args,
    executablePath: await chromium.executablePath(),
    headless: true,
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errors = [];
    const unexpected = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => {
      if (!request.url().startsWith('http://127.0.0.1:8000/')) unexpected.push(request.url());
    });

    const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, 'site-manifest.json'), 'utf8'));
    for (const file of manifest) {
      const response = await page.goto(`http://127.0.0.1:8000/${file}`);
      assert.equal(response.status(), 200, file);
      assert.equal(await page.locator('h1').count(), 1, file);
      assert.equal(await page.locator('nav a[aria-current="page"]').count(), 1, file);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `${file} desktop overflow`);
    }

    // Review choices are local, persist on this browser, and reset cleanly.
    await page.goto('http://127.0.0.1:8000/pages/suggestions.html');
    const total = await page.locator('.review-choice').count();
    assert.ok(total >= 8, `expected populated review queue, found ${total}`);
    const first = await page.locator('.review-choice').first().getAttribute('data-id');
    await page.selectOption(`.review-choice[data-id="${first}"]`, 'Investigate');
    assert.match(await page.locator('#review-summary').textContent(), /1 investigate/i);
    await page.reload();
    assert.equal(await page.locator(`.review-choice[data-id="${first}"]`).inputValue(), 'Investigate');
    await page.click('#reset-reviews');
    assert.equal(await page.locator(`.review-choice[data-id="${first}"]`).inputValue(), 'Not reviewed');
    assert.match(await page.locator('#review-summary').textContent(), /0 investigate/i);

    // Projection what-if controls recompute in the browser only.
    await page.goto('http://127.0.0.1:8000/pages/projections.html');
    const statBefore = await page.locator('#scenario-stats .stat .stat-value').first().textContent();
    await page.locator('#transfer_year').fill('2050');
    const statAfter = await page.locator('#scenario-stats .stat .stat-value').first().textContent();
    assert.notEqual(statBefore, statAfter);
    const tableBefore = await page.locator('.table-section table tbody tr td').nth(1).textContent();
    await page.locator('#a_appreciation').fill('6');
    const tableAfter = await page.locator('.table-section table tbody tr td').nth(1).textContent();
    assert.notEqual(tableBefore, tableAfter);
    assert.deepEqual(await page.evaluate(() => Object.keys(localStorage)), []);

    // Staging calculator recalculates all three cases and reports the risk set.
    await page.goto('http://127.0.0.1:8000/pages/phased-investing.html');
    const rowCount = await page.locator('#calc-rows tr').count();
    assert.equal(rowCount, 3, 'expected three entry cases');
    const initial = await page.locator('#calc-rows tr:nth-child(2) td').first().textContent();
    assert.notEqual(initial.trim(), '');
    await page.locator('#calc-drop').fill('89');
    assert.notEqual(await page.locator('#calc-rows tr:nth-child(2) td').first().textContent(), initial);
    await page.locator('#calc-yield-after').fill('1.5');
    await page.locator('#calc-equity').fill('8');
    const riskCount = await page.locator('#calc-risk li').count();
    assert.equal(riskCount, 5, 'expected five reinvestment-risk statements');
    assert.match(await page.locator('#calc-risk').textContent(), /yield/i);
    assert.deepEqual(await page.evaluate(() => Object.keys(localStorage).filter(key => key.startsWith('calc-'))), []);

    // Ladder panel: reinvestment penalty appears and remains local-only.
    const flatInterest = await page.locator('#ladder-flat-interest').textContent();
    const fallingInterest = await page.locator('#ladder-falling-interest').textContent();
    assert.notEqual(flatInterest, '—');
    assert.notEqual(fallingInterest, '—');
    assert.match(await page.locator('#ladder-status').textContent(), /reinvestment risk|no reinvestment penalty/i);
    await page.fill('#ladder-renewal3', '0');
    const afterCut = await page.locator('#ladder-falling-interest').textContent();
    assert.notEqual(afterCut, fallingInterest);
    await page.click('#ladder-reset');
    assert.equal(await page.locator('#ladder-renewal3').inputValue(), '2.0');
    assert.deepEqual(await page.evaluate(() => Object.keys(localStorage).filter(key => key.startsWith('ladder-'))), []);

    // Decision log carries its own independent review queue.
    await page.goto('http://127.0.0.1:8000/pages/decision-log.html');
    const logTotal = await page.locator('.review-choice').count();
    assert.equal(logTotal, 12, `expected 12 decision-log items, found ${logTotal}`);
    await page.selectOption('.review-choice[data-id="D07"]', 'Selected');
    assert.match(await page.locator('#review-summary').textContent(), /1 of 12 suggestions reviewed/);
    await page.click('#reset-reviews');
    assert.equal(await page.locator('.review-choice[data-id="D07"]').inputValue(), 'Not reviewed');

    await page.goto('http://127.0.0.1:8000/pages/attorney-cpa-brief.html');
    await page.emulateMedia({ media: 'print' });
    assert.equal(await page.locator('.sidebar').evaluate(element => getComputedStyle(element).display), 'none');
    await page.emulateMedia({ media: 'screen' });

    await page.setViewportSize({ width: 390, height: 844 });
    for (const file of manifest) {
      await page.goto(`http://127.0.0.1:8000/${file}`);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `${file} mobile overflow`);
    }
    assert.deepEqual(errors, []);
    assert.deepEqual(unexpected, []);
    console.log(`Browser passed: ${manifest.length} desktop + ${manifest.length} mobile pages; review save/reset; projection controls; staging calculator; print layout; no JS errors or third-party requests.`);
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exit(1);
});
