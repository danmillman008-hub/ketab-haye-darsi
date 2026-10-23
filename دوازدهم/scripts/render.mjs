// Render the debugged grade-12 Word files to native PDFs.
import {createConverter} from '../../stitch-14/node_modules/@deepseek-ai/libreoffice-kit/lib/index.js';
import fs from 'node:fs/promises';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../..');
const src=path.join(root,'.work/d12/docx');
const output=path.resolve(process.argv[2]||path.join(root,'.work/d12/render'));
await fs.mkdir(output,{recursive:true});
const names=(await fs.readdir(src)).filter(f=>f.endsWith('.docx')).sort();
const c=await createConverter({timeoutMs:120000,fontDirectories:[path.join(root,'assets/word-fonts'),path.join(root,'stitch-14/assets/word-fonts')]});
try{
 for(const name of names){
  const id=name.replace(/\.docx$/,'');
  const inputPath=path.join(src,name);
  const outputPath=path.join(output,id+'.pdf');
  await fs.rm(outputPath,{force:true});
  let result;
  for(let attempt=1;attempt<=3;attempt++){
   try{result=await c.render({inputPath,outputPath});break;}
   catch(e){await fs.rm(outputPath,{force:true});if(attempt===3)throw e;}
  }
  console.log(id,JSON.stringify(result));
  if(result.missingFonts.length)throw new Error('Missing fonts: '+id);
 }
} finally {await c.dispose();}
