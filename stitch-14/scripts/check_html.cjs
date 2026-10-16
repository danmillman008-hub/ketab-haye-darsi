const {chromium}=require('playwright');
const c=require('@sparticuz/chromium').default;
const path=require('path');
const fs=require('fs');
(async()=>{
 const base=path.resolve(__dirname,'..');
 const b=await chromium.launch({executablePath:await c.executablePath(),args:c.args,headless:true});
 try{
  const p=await b.newPage();
  await p.route(/^https?:/,route=>route.abort()); // Final deliverable must work offline.
  await p.goto('file://'+base+'/index.html');
  await p.emulateMedia({media:'print'});
  await p.evaluate(()=>document.fonts.ready);
  const checks=await p.evaluate(()=>Array.from(document.querySelectorAll('.sheet')).map(s=>{
   const image=s.querySelector('header img');
   const note=s.querySelector('.planning-note').getBoundingClientRect();
   const footer=s.querySelector('footer').getBoundingClientRect();
   const section=s.querySelector('section:last-child').getBoundingClientRect();
   const cards=Array.from(s.querySelectorAll('section .grid>div'));
   const overflow=cards.filter(card=>{
    const content=card.querySelector('.box-content');
    return card.scrollHeight>card.clientHeight+1 || (content &&
     Array.from(content.children).some(x=>x.getBoundingClientRect().bottom>card.lastElementChild.getBoundingClientRect().top+1));
   }).length;
   return {page:s.id,logoLoaded:image.complete&&image.naturalWidth>0,
    overflowingCards:overflow,footerClear:section.bottom<=note.top&&note.bottom<=footer.top&&footer.bottom<=s.getBoundingClientRect().bottom};
  }));
  if(checks.some(x=>!x.logoLoaded||x.overflowingCards||!x.footerClear))throw new Error(JSON.stringify(checks));
  await p.pdf({path:path.join(base,'../.work/stitch14-html-reference.pdf'),preferCSSPageSize:true,printBackground:true});
  fs.writeFileSync(base+'/QA-browser.json',JSON.stringify(checks,null,2)+'\n');
  console.log('PASS: four offline pages, all logos loaded, no card/footer overflow.');
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exit(1)});
