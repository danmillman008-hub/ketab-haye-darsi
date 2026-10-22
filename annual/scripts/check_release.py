"""Verify published files, ZIP members, sample aliases, HTML text, and untouched reports."""
import json,hashlib,zipfile
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
load=lambda p:json.loads((ROOT/p).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={x['id']:x for x in load('annual/QA.json')['checks']}
with zipfile.ZipFile(ROOT/'organized-deliverables.zip') as z:
 for e in load('annual/manifest.json'):
  for ext,key in [('pdf','pdfSha256'),('docx','docxSha256')]:
   p=ROOT/e['directory']/(e['stem']+'.'+ext)
   assert sha(p)==checks[e['id']][key]
   assert z.read(str(p.relative_to(ROOT)))==p.read_bytes()
for name,h in load('annual/preserved.json').items():assert sha(ROOT/name)==h
sample=load('annual/data/1405-08-01.json')['days']
for folder in ['', 'stitch-13','stitch-14']:
 base=ROOT/folder;assert load(str(Path(folder)/'plan.json'))==sample
 for ext,key in [('pdf','pdfSha256'),('docx','docxSha256')]:assert sha(base/('plan-1-aban-1405.'+ext))==checks['1405-08-01'][key]
 html=BeautifulSoup((base/'index.html').read_text(),'html.parser').get_text()
 for day in sample:
  for b in day['boxes']:assert b['topic'] in html
 zipname='plan-1-aban-1405.zip' if not folder else folder+'-deliverables.zip'
 with zipfile.ZipFile(base/zipname) as z:
  for name in ['plan-1-aban-1405.pdf','plan-1-aban-1405.docx','index.html','README.md']:assert z.read(name)==(base/name).read_bytes()
print('PASS: 42 monthly files, annual ZIP, 3 sample copies/HTMLs/ZIPs, and preserved student reports.')
