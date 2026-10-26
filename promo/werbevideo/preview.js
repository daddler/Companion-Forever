const { chromium } = require('playwright');
(async () => {
  const dir = process.argv[2], times = process.argv.slice(3).map(Number);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + dir + '/index.html');
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  for (const t of times) {
    await p.evaluate(t => window.setTime(t), t);
    await p.screenshot({ path: `${dir}/prev_${t}.jpg`, type: 'jpeg', quality: 80 });
  }
  await b.close();
})();
