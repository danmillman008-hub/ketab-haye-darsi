// All annual PDFs are native Word exports through the approved renderer.
import {createConverter} from '../../stitch-14/node_modules/@deepseek-ai/libreoffice-kit/lib/index.js';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
const root=path.resolve(import.meta.dirname,'../..');
const output=path.resolve(process.argv[2]);
const manifestPath=process.argv[3]||path.join(root,'دهم و یازدهم/samples.json');
const selected=process.argv.slice(4);
await fs.mkdir(output,{recursive:true});
const plans=JSON.parse(await fs.readFile(manifestPath,'utf8')).filter(x=>!x.preserved&&(!selected.length||selected.includes(x.id)));
const c=await createConverter({timeoutMs:120000,fontDirectories:[path.join(root,'assets/word-fonts'),path.join(root,'stitch-14/assets/word-fonts')]});
const results=[];
try {
 for(const p of plans){
  const inputPath=path.join(root,'.work/foundation/docx',p.id+'.docx');
  const outputPath=path.join(output,p.id+'.pdf');
  await fs.rm(outputPath,{force:true});
  let result;
  for(let attempt=1;attempt<=3;attempt++){
   try{result=await c.render({inputPath,outputPath});break;}
   catch(e){await fs.rm(outputPath,{force:true});if(attempt===3)throw e;}
  }
  const inputSha256=createHash('sha256').update(await fs.readFile(inputPath)).digest('hex');
  results.push({id:p.id,inputSha256,...result});
  await fs.writeFile(path.join(output,'results.json'),JSON.stringify(results,null,2));
  console.log(p.id,JSON.stringify(result),result.pageCount===p.pages?'PAGES OK':'PAGE MISMATCH');
  if(result.missingFonts.length)throw new Error('Missing fonts: '+p.id);
 }
} finally {await c.dispose();}
