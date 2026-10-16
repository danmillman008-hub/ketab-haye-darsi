// Render the canonical DOCX files; validate_rendered.py publishes these exact PDFs.
import {createConverter} from '@deepseek-ai/libreoffice-kit';
import path from 'node:path';
import {createHash} from 'node:crypto';
import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const base=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=path.resolve(process.argv[2]||path.join(base,'../.work/stitch14-qa'));
await fs.mkdir(output,{recursive:true});
const c=await createConverter({timeoutMs:120000,fontDirectories:[path.join(base,'../assets/word-fonts'),path.join(base,'assets/word-fonts')]});
const results=[];
try{
 for(const [name,pages] of [['plan-1-aban-1405',4],['student-report-1',1],['student-report-2',1]]){
  const result=await c.render({inputPath:path.join(base,name+'.docx'),outputPath:path.join(output,name+'.pdf')});
  if(result.pageCount!==pages||result.missingFonts.length)throw new Error('Layout/font check failed: '+name+': '+JSON.stringify(result));
  const inputSha256=createHash('sha256').update(await fs.readFile(path.join(base,name+'.docx'))).digest('hex');
  results.push({file:name+'.docx',inputSha256,...result});
 }
}finally{await c.dispose()}
await fs.writeFile(path.join(output,'results.json'),JSON.stringify(results,null,2));
console.log(JSON.stringify(results,null,2));
