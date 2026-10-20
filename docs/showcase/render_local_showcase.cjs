// Render only local, self-contained publishing sources in a temporary browser.
const {chromium} = require('playwright');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const fs = require('node:fs/promises');

(async () => {
  const browser = await chromium.launch({headless:true});
  try {
    const page = await browser.newPage({viewport:{width:1588,height:1123}});
    const checks = [];
    for (const name of ['farmlens-showcase-2026-10-20','showcase-demo-script','farmlens-linkedin']) {
      await page.goto(pathToFileURL(path.join(__dirname,name+'.html')).href);
      await page.evaluate(()=>document.fonts.ready);
      if (name === 'farmlens-linkedin') {
        await page.setViewportSize({width:1200,height:1500});
        await page.screenshot({path:path.join(__dirname,name+'.png'),fullPage:false});
      } else {
        await page.pdf({path:path.join(__dirname,name+'.pdf'),preferCSSPageSize:true,printBackground:true});
      }
      checks.push(await page.evaluate(()=>({
        title:document.title,
        fonts:document.fonts.status,
        images:[...document.images].every(image=>image.complete&&image.naturalWidth>0),
        footerOverlap:[...document.querySelectorAll('footer')].some(footer=>footer.previousElementSibling.getBoundingClientRect().bottom>footer.getBoundingClientRect().top-8),
        overflow:[...document.querySelectorAll('h1,h2,h3,p,.poster,.page,.social')].filter(e=>e.scrollWidth>e.clientWidth+1||e.scrollHeight>e.clientHeight+1).map(e=>({element:e.className||e.tagName,width:[e.scrollWidth,e.clientWidth],height:[e.scrollHeight,e.clientHeight]}))
      })));
    }
    await fs.writeFile(path.join(__dirname,'showcase-render-checks.json'),JSON.stringify(checks,null,2)+'\n');
    console.log(JSON.stringify(checks,null,2));
    if(checks.some(check=>!check.images||check.overflow.length||check.footerOverlap)) process.exitCode=1;
  } finally {
    await browser.close();
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
