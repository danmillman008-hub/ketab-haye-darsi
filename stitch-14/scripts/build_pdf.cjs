// Publish PDFs only from the canonical DOCX files (never a second HTML layout).
const fs=require('node:fs');
const path=require('node:path');
const {spawnSync}=require('node:child_process');
const base=path.resolve(__dirname,'..');
const work=path.join(base,'../.work');fs.mkdirSync(work,{recursive:true});
const output=process.argv[2]?path.resolve(process.argv[2]):fs.mkdtempSync(path.join(work,'stitch14-word-export-'));
function run(command,args){
 const result=spawnSync(command,args,{stdio:'inherit'});
 if(result.error)throw result.error;
 if(result.status!==0)process.exit(result.status||1);
}
run(process.execPath,[path.join(__dirname,'render_word.mjs'),output]);
run(process.env.PYTHON||path.join(base,'../.venv/bin/python'),[path.join(__dirname,'validate_rendered.py'),output,'--publish']);
console.log('Canonical PDFs published. Render directory: '+output);
