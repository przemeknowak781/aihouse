// Render an HTML board to a PDF of exact physical size (default 1000x700 mm) and optional PNG preview.
// Usage: node html2pdf.js in.html out.pdf [widthMM heightMM] [--png out.png --pngw 3000] [--outline]
//   Multi-page documents: CSS @page { size: …; margin: … } wins over widthMM/heightMM (preferCSSPageSize), so a
//   paged HTML (e.g. tools/opis.py) renders to as many pages as its content needs; margin boxes (@top-left …,
//   counter(page)/counter(pages)) are supported by Chromium ≥ 131.
//   --outline  (optional, added for tools/opis.py) embeds a PDF outline (bookmarks) built from h1–h6 and writes a
//              tagged PDF. Without the flag the output is byte-for-byte the same kind as before (existing callers).
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const a = process.argv.slice(2);
  const inp = path.resolve(a[0]), out = path.resolve(a[1]);
  const num = (s, d) => (s === undefined || String(s).startsWith('--')) ? d : parseFloat(s);
  const wmm = num(a[2], 1000), hmm = num(a[3], 700);
  const pi = a.indexOf('--png'); const png = pi >= 0 ? path.resolve(a[pi + 1]) : null;
  const wi = a.indexOf('--pngw'); const pngw = wi >= 0 ? parseInt(a[wi + 1]) : 2800;
  const outline = a.includes('--outline');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + inp, { waitUntil: 'networkidle', timeout: 300000 });
  await page.evaluate(() => document.fonts.ready);
  const opts = { path: out, width: `${wmm}mm`, height: `${hmm}mm`, printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 }, preferCSSPageSize: true };
  if (outline) { opts.outline = true; opts.tagged = true; }
  await page.pdf(opts);
  if (png) {
    const pxW = wmm / 25.4 * 96, pxH = hmm / 25.4 * 96;
    await page.setViewportSize({ width: Math.round(pxW), height: Math.round(pxH) });
    const scale = pngw / pxW;
    const p2 = await browser.newPage({ viewport: { width: Math.round(pxW), height: Math.round(pxH) }, deviceScaleFactor: scale });
    await p2.goto('file://' + inp, { waitUntil: 'networkidle', timeout: 300000 });
    await p2.evaluate(() => document.fonts.ready);
    await p2.screenshot({ path: png, fullPage: false });
  }
  await browser.close();
  console.log('OK', out, png || '');
})().catch(e => { console.error(e); process.exit(1); });
