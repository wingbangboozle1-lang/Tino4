// Optional Playwright smoke test. Serve the repository root on port 8000 first.
// Browser dependencies are located via BROWSER_MODULES or tools/browser/node_modules.
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
    assert.match(await page.locator('#review-summary').textContent(), new RegExp(`1 of ${total} suggestions reviewed`));
    await page.reload();
    assert.equal(await page.locator(`.review-choice[data-id="${first}"]`).inputValue(), 'Investigate');
    await page.click('#reset-reviews');
    assert.equal(await page.locator(`.review-choice[data-id="${first}"]`).inputValue(), 'Not reviewed');
    assert.match(await page.locator('#review-summary').textContent(), new RegExp(`0 of ${total} suggestions reviewed`));

    // Staging controls recalculate independently for early/late entry and inflation.
    await page.goto('http://127.0.0.1:8000/pages/phased-investing.html');
    const initial = await page.locator('#early-phased-value').textContent();
    assert.notEqual(initial, '—');
    const initialReal = await page.locator('#early-phased-real').textContent();
    assert.match(await page.locator('#phase-status').textContent(), /assumption-driven scenarios/i);
    await page.selectOption('#phase-event', '1929');
    assert.equal(await page.locator('#phase-drawdown').inputValue(), '89');
    assert.notEqual(await page.locator('#early-phased-value').textContent(), initial);
    await page.fill('#phase-yield2', '1.5');
    await page.fill('#phase-inflation', '3');
    assert.notEqual(await page.locator('#early-phased-real').textContent(), initialReal);
    assert.notEqual(await page.locator('#late-months').textContent(), await page.locator('#early-months').textContent());
    assert.deepEqual(await page.evaluate(() => Object.keys(localStorage).filter(key => key.startsWith('phase-'))), []);

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

    // Path tool: the priced sell branch reacts to the gain sensitivity and to depreciation.
    await page.goto('http://127.0.0.1:8000/pages/decision-analysis.html');
    assert.equal(await page.locator('#path-transfer-tax').textContent(), '$7,180');
    assert.equal(await page.locator('#path-gain').textContent(), 'nil');
    const beforeGain = await page.locator('#path-taxes').textContent();
    await page.fill('#path-gainpct', '100');
    const afterGain = await page.locator('#path-taxes').textContent();
    assert.notEqual(afterGain, beforeGain, 'a full-price gain must change the modeled tax');
    assert.ok(Number((await page.locator('#path-gain').textContent()).replace(/[$,]/g, '')) > 6000000);
    await page.fill('#path-depr', '1500000');
    assert.match(await page.locator('#path-recap').textContent(), /\$375,000 on \$1,500,000/);
    await page.check('#path-principal');
    assert.match(await page.locator('#path-status').textContent(), /Local scenario recomputed/);
    await page.click('#path-reset');
    assert.equal(await page.locator('#path-gain').textContent(), 'nil', 'reset must restore the baseline');
    assert.deepEqual(await page.evaluate(() => Object.keys(localStorage).filter(key => key.startsWith('path-'))), []);

    // Proposition H estimator: class, sunset and the pass-through ceiling.
    await page.goto('http://127.0.0.1:8000/pages/rental-economics.html');
    assert.equal(await page.locator('#ph-charge').textContent(), '$250');
    assert.equal(await page.locator('#ph-pass').textContent(), '$130');
    await page.selectOption('#ph-class', '799');
    assert.ok(Number((await page.locator('#ph-charge').textContent()).replace(/[$,]/g, '')) > 250);
    await page.fill('#ph-year', '2042');
    assert.equal(await page.locator('#ph-cum').textContent(), await page.locator('#ph-life').textContent());
    await page.click('#ph-reset');
    assert.equal(await page.locator('#ph-charge').textContent(), '$250');

    // The projections distribution chart renders from the model.
    await page.goto('http://127.0.0.1:8000/pages/projections.html');
    assert.equal(await page.locator('svg.dist-chart rect.dist-bar').count(), 6);

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
    console.log(`Browser passed: ${manifest.length} desktop + ${manifest.length} mobile pages; review save/reset; calculator controls; print layout; no JS errors or third-party requests.`);
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exit(1);
});
