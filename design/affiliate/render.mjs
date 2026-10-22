// Renders mock-affiliate-v1.html: each look at 1380 and 390 → renders/*.png
import { chromium } from '/home/claude/repo/tools/harness/node_modules/playwright/index.mjs';
import path from 'node:path';
import fs from 'node:fs';
const here = path.dirname(new URL(import.meta.url).pathname);
const out = path.join(here, 'renders'); fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
for (const w of [1380, 390]) {
  const page = await browser.newPage({ viewport: { width: w + (w > 500 ? 80 : 0), height: 1200 }, deviceScaleFactor: w > 500 ? 1 : 2 });
  await page.goto('file://' + path.join(here, 'mock-affiliate-v1.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);
  const over = await page.evaluate(() => {
    const bad = [];
    for (const sec of document.querySelectorAll('.pg')) {
      const r = sec.getBoundingClientRect();
      for (const el of sec.querySelectorAll('*')) { const b = el.getBoundingClientRect(); if (b.width && (b.right > r.right + 1 || b.left < r.left - 1)) { bad.push(el.className + ' ' + Math.round(b.left) + '-' + Math.round(b.right)); if (bad.length > 8) break; } }
    }
    return { sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, bad };
  });
  console.log(w, JSON.stringify(over));
  for (const id of ['lookA', 'lookB']) {
    await page.locator('#' + id).screenshot({ path: path.join(out, `affil-v1-${id.slice(-1).toLowerCase()}-${w}.png`) });
  }
  await page.close();
}
await browser.close();
