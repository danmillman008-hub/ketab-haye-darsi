const {chromium}=require('playwright');
const c=require('@sparticuz/chromium').default;
(async()=>{const b=await chromium.launch({executablePath:await c.executablePath(),args:c.args,headless:true});try{const p=await b.newPage();await p.goto('file://'+process.cwd()+'/index.html');await p.evaluate(()=>document.fonts.ready);await p.pdf({path:'plan-1-aban-1405.pdf',preferCSSPageSize:true,printBackground:true});}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1)});
