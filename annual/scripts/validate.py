"""Annual data/Word/PDF checks; staging only until all plans pass."""
import sys,json,zipfile,hashlib,unicodedata,copy
from pathlib import Path
from collections import Counter
from lxml import etree
import pymupdf as fitz
import jdatetime
ROOT=Path(__file__).resolve().parents[2]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def chars(s):return Counter(c for c in unicodedata.normalize('NFKC',s) if not c.isspace() and unicodedata.category(c)!='Cf')
def source_pages(path):
 with zipfile.ZipFile(path) as z:
  xml=etree.fromstring(z.read('word/document.xml'))
  assert len([n for n in z.namelist() if n.startswith('word/fonts/')])==3
  assert len([n for n in z.namelist() if n.startswith('word/media/')])==3
 pages=['']
 for child in xml.find('w:body',NS):
  if child.xpath('.//w:br[@w:type="page"]',namespaces=NS):pages.append('')
  pages[-1]+=''.join(child.xpath('.//w:t/text()',namespaces=NS))
 for tbl in xml.xpath('//w:tbl',namespaces=NS):
  assert tbl.find('w:tblPr/w:tblLayout',NS).get('{'+NS['w']+'}type')=='fixed'
 return pages
render=ROOT/ sys.argv[1]
compare=ROOT/sys.argv[2] if len(sys.argv)>2 else None
results={r['id']:r for r in json.loads((render/'results.json').read_text())}
errors=[];checks=[];prev=None
for entry in json.loads((ROOT/'annual/manifest.json').read_text()):
 data=json.loads((ROOT/'annual/data'/(entry['id']+'.json')).read_text());days=data['days']
 assert len(days)==entry['weeks']*6
 for wi in range(1,entry['weeks']+1):
  week=[d for d in days if d['week']==wi]
  assert [d['day'] for d in week]==list(range(6))
  assert sum(d['hours'] for d in week)==47 and sum(d['tests'] for d in week)==495
  for prefix,count,tests in [('زیست',9,120),('ریاضی',6,150),('فیزیک',6,150),('شیمی',6,75)]:
   bs=[b for d in week for b in d['boxes'] if b['subject'].startswith(prefix)]
   assert len(bs)==count and sum(b['tests'] for b in bs)==tests
  for d in week:
   assert d['hours']==sum(b['hours'] for b in d['boxes'])
   for b in d['boxes']:
    if b['tests']:assert b['hours']==2 and b['tests']=={'زیست':20,'ریاضی':30,'فیزیک':30,'شیمی':25}[b['subject'].split()[0]]
    else:assert b['hours']==(2 if b['subject'].startswith('فیزیک') else 1)
   assert [b['subject'].split()[0] for b in d['boxes']]==(['زیست','ریاضی','زیست','ریاضی','زیست'] if d['day']%2==0 else ['فیزیک','شیمی','فیزیک','شیمی'])
 if entry['target']:
  target=jdatetime.date.fromisoformat(entry['target']);start=jdatetime.date.fromisoformat(entry['start'])
  assert target.weekday()==6 and start.weekday()==0
  assert (target-start).days==entry['weeks']*7-1
  if prev:assert (start-prev).days==1
  prev=target
  if not entry['preserved']:
   for d in days:assert jdatetime.date.fromisoformat(d['iso']).weekday()==d['day']
 if entry['preserved']:
  assert days==json.loads((ROOT/'stitch-14/plan.json').read_text())
  continue
 docx=ROOT/'.work/annual/docx'/(entry['id']+'.docx');pdf=render/(entry['id']+'.pdf')
 r=results[entry['id']];assert r['inputSha256']==sha(docx)
 assert not r['missingFonts']
 # Bind native Word content to the current dataset, not merely to its own PDF.
 with zipfile.ZipFile(docx) as z:
  xml=etree.fromstring(z.read('word/document.xml'))
 paragraph_list=[''.join(p.xpath('.//w:t/text()',namespaces=NS)) for p in xml.xpath('//w:p',namespaces=NS)]
 paragraphs=Counter(paragraph_list)
 topics=Counter(b['topic'] for day in days for b in day['boxes'])
 assert [p for p in paragraph_list if p in topics]==[b['topic'] for day in days for b in day['boxes']],('Word day/box topic order',entry['id'])
 details=Counter(b['detail'] for day in days for b in day['boxes'])
 subjects=Counter('☐ '+b['subject'] for day in days for b in day['boxes'])
 assert not (details-paragraphs) and not (subjects-paragraphs),('Word instructions/subjects',entry['id'])
 assert not (topics-paragraphs),('Stale or changed Word topics',entry['id'],topics-paragraphs)
 expected=source_pages(docx);doc=fitz.open(pdf)
 assert len(doc)==len(expected)==entry['pages']
 pp=[]
 for i,(page,txt) in enumerate(zip(doc,expected)):
  actual=page.get_text();missing=chars(txt)-chars(actual);extra=chars(actual)-chars(txt)
  if missing or extra:errors.append((entry['id'],i+1,dict(missing),dict(extra)))
  assert len(page.get_image_info())==3
  assert actual.count('مجموع ساعت')==(4 if i%2 else 3)
  assert actual.count('هدف ساعت')==1
  if entry['special']:assert 'فایل برآیندی' in actual
  for forbidden in ['ماز','مطابق بودجه','صفحات محدوده','چاپ ۱۴۰۵']:
   assert forbidden not in actual,(entry['id'],i+1,forbidden)
  for word in page.get_text('words'):assert -1<=word[0]<=word[2]<=page.rect.width+1 and -1<=word[1]<=word[3]<=page.rect.height+1
  pix=page.get_pixmap(dpi=100)
  if compare:
   other=fitz.open(compare/(entry['id']+'.pdf'));assert pix.samples==other[i].get_pixmap(dpi=100).samples
  pp.append({'page':i+1,'missingCharacters':sum(missing.values()),'extraCharacters':sum(extra.values()),'pixelSha256At100dpi':hashlib.sha256(pix.samples).hexdigest()})
  # Contact images are scratch QA only, not delivery.
  if not compare and i in [0,1,len(doc)-1]:page.get_pixmap(dpi=90).save(str(render/(entry['id']+f'-p{i+1}.png')))
 checks.append(dict(id=entry['id'],docxSha256=sha(docx),pdfSha256=sha(pdf),dataSha256=sha(ROOT/'annual/data'/(entry['id']+'.json')),pages=pp))
for name,h in json.loads((ROOT/'annual/preserved.json').read_text()).items():assert sha(ROOT/name)==h,name
print('Character errors:',json.dumps(errors,ensure_ascii=False))
if errors:sys.exit(1)
qa=dict(status='passed',datedPlans=19,undatedRelativePlans=2,formula='47 hours / 495 tests per week',independentPixelComparison=bool(compare),pixelDpi=100,wordApplicationTested=False,checks=checks)
(ROOT/'annual/QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print('PASS: calendar continuity, formula, native Word, embedded fonts, all-page text, image counts, preserved files'+(' and independent pixels' if compare else ''))
