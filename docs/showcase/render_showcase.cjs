const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:1588,height:1123},deviceScaleFactor:1});
  const checks = [];
  for (const [source, output] of (process.argv.includes('--script-only') ? [['presentation-demo-script.html','presentation-demo-script.pdf']] : [['farmlens-poster.html','farmlens-poster-a3.pdf'],['presentation-demo-script.html','presentation-demo-script.pdf']])) {
    await page.goto('file://' + path.join(__dirname,source));
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({path:path.join(__dirname,output),preferCSSPageSize:true,printBackground:true});
    checks.push(await page.evaluate(() => ({title:document.title,fonts:document.fonts.status,images:[...document.images].map(i=>({ok:i.complete&&i.naturalWidth>0,alt:i.alt})),overflow:[...document.querySelectorAll('p,h1,h2,h3,.barrow,.flow,.segment,.spoken-line')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.innerText)})));
  }
  console.log(JSON.stringify(checks,null,2));
  await browser.close();
})();
