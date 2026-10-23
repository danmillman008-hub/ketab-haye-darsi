"""Validate sample data and native editable Word against both independent PDF exports."""
import json,sys,hashlib,zipfile,unicodedata,copy
from pathlib import Path
from collections import Counter
from lxml import etree
import pymupdf as fitz
import jdatetime
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parent
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
chars=lambda t:Counter(c for c in unicodedata.normalize('NFKC',t) if not c.isspace() and unicodedata.category(c)!='Cf')
EXPECTED={10:{'زیست':[[1,21]],'ریاضی':[[1,27]],'فیزیک':[[1,32]],'شیمی':[[1,23]]},11:{'زیست':[[1,28]],'ریاضی':[[1,18],[25,30]],'فیزیک':[[1,21]],'شیمی':[[1,24]]}}
def pages(ranges):return {p for a,b in ranges for p in range(a,b+1)}
def check_data(d):
 g=d['grade'];days=d['days'];assert len(days)==6 and d['weeks']==1 and d['pages']==2
 assert d['target']=='1405-08-15' and d['start']=='1405-08-02' and d['end']=='1405-08-08'
 assert not d['week_meta'][0]['official_exam'],'Do not label 8 Aban as an official MAZ exam'
 assert [x['hours'] for x in days]==([5,7,5,5,5,4] if g==10 else [5,7,5,6,6,4])
 assert d['hours']==sum(x['hours'] for x in days)==(31 if g==10 else 33)
 assert d['tests']==sum(x['tests'] for x in days)==230
 seen={k:set() for k in EXPECTED[g]};finals=[]
 for i,day in enumerate(days):
  assert day['day']==i and day['week']==1
  assert day['iso']==f'1405-08-{i+2:02}' and jdatetime.date.fromisoformat(day['iso']).weekday()==i
  assert day['hours']==sum(b['hours'] for b in day['boxes'])
  assert day['tests']==sum(b['tests'] for b in day['boxes'])
  assert len(day['boxes'])<=6
  assert {b['subject'].split()[0] for b in day['boxes'] if b['kind']!='finals'}==({'زیست','ریاضی'} if i%2==0 else {'فیزیک','شیمی'})
  subjects=[b['subject'] for b in day['boxes']]
  assert all(a!=b for a,b in zip(subjects,subjects[1:])), 'Consecutive same-subject boxes'
  for b in day['boxes']:
   if b['kind']=='finals':
    assert b['hours']==2 and b['tests']==0 and i in [1,3];finals.append(i);continue
   subject=b['subject'].split()[0];covered=pages(b['ranges']);assert covered<=pages(EXPECTED[g][subject])
   assert b['subject']==('ریاضی' if subject=='ریاضی' else subject+' '+('دهم' if g==10 else 'یازدهم'))
   if b['kind']=='test':
    assert covered<=seen[subject],('Test before study',subject)
    assert b['hours']==2 and b['tests']=={'زیست':20,'ریاضی':30,'فیزیک':30,'شیمی':25}[subject]
    if subject in ['ریاضی','فیزیک']:
     study=next(x for dd in days for x in dd['boxes'] if x['subject']==b['subject'] and x['kind']=='study')
     assert b['topic']==study['topic'] and covered==pages(EXPECTED[g][subject])
     assert b['preference'].startswith('* ترجیحاً: ')
   else:
    assert b['kind'] in ['study','review'] and not b['tests'] and len(covered)>1
    seen[subject]|=covered
   for forbidden in ['ماز','چاپ ۱۴۰۵','طبق فرمول','زمین‌شناسی','دوازدهم']:assert forbidden not in b['topic']+b['detail']
   if g==10 and subject=='زیست' and 21 in covered:assert 'قبل از شیرهٔ معده' in b['topic']
   if g==10 and subject=='فیزیک':assert 'قبل از فشار در شاره‌ها' in b['topic']
   if g==11 and subject=='زیست' and 28 in covered:assert 'قبل از شنوایی و تعادل' in b['topic']
   if g==11 and subject=='شیمی' and 24 in covered:assert 'قبل از خود را بیازمایید ص۲۴' in b['topic']
   if g==11 and subject=='فیزیک':assert 'قبل از پتانسیل الکتریکی' in b['topic']
 assert finals==[1,3]
 assert all(b['kind']=='test' for b in days[5]['boxes'])
 assert seen=={k:pages(v) for k,v in EXPECTED[g].items()}
 return True

def main():
 render=ROOT/sys.argv[1];other=ROOT/sys.argv[2]
 result={r['id']:r for r in load(render/'results.json')};ind={r['id']:r for r in load(other/'results.json')}
 checks=[];source=[]
 for b in load(ROOT/'annual/BOOK_EDITIONS.json')['books']:
  if b['key'][-2:] not in ['10','11']:continue
  file=ROOT/b['file'];assert sha(file)==b['sha256']
  with fitz.open(file) as pdf:assert len(pdf)==b['pdf_pages']
  source.append({k:b[k] for k in ['key','drive_id','sha256','pdf_offset']})
 for s in load(BASE/'sources.json'):assert sha(ROOT/'google_drive'/s['filename'])==s['sha256']
 for entry in load(BASE/'samples.json'):
  ident=entry['id'];d=load(BASE/'data'/(ident+'.json'));check_data(d)
  for mutation in ['missing-final','changed-boundary','restricted-test','single-page','wrong-date']:
   x=copy.deepcopy(d)
   if mutation=='missing-final':x['days'][1]['boxes'].pop()
   if mutation=='changed-boundary':x['days'][4]['boxes'][0]['topic']='زیست؛ بدون قید پایان'
   if mutation=='restricted-test':x['days'][2]['boxes'][1]['topic']='فقط یک زیرمبحث اجباری'
   if mutation=='single-page':x['days'][0]['boxes'][0]['ranges']=[[1,1]]
   if mutation=='wrong-date':x['days'][0]['iso']='1405-08-09'
   try:check_data(x)
   except AssertionError:pass
   else:raise AssertionError('Mutation incorrectly accepted: '+mutation)
  word=ROOT/'.work/foundation/docx'/(ident+'.docx');pdf=render/(ident+'.pdf')
  for r in [result[ident],ind[ident]]:
   assert r['inputSha256']==sha(word) and r['pageCount']==2 and not r['missingFonts']
  with zipfile.ZipFile(word) as z:
   xml=etree.fromstring(z.read('word/document.xml'))
   assert sum(n.startswith('word/fonts/') for n in z.namelist())==3
   assert sum(n.startswith('word/media/') for n in z.namelist())==3
  paragraphs=[''.join(p.xpath('.//w:t/text()',namespaces=NS)) for p in xml.xpath('//w:p',namespaces=NS)]
  counter=Counter(paragraphs);boxes=[b for day in d['days'] for b in day['boxes']]
  for field in ['topic','detail']:
   values=Counter(b[field] for b in boxes);assert not values-counter
  assert not Counter('☐ '+b['subject'] for b in boxes)-counter
  topics={b['topic'] for b in boxes}
  assert [p for p in paragraphs if p in topics]==[b['topic'] for b in boxes]
  for b in boxes:
   if 'preference' not in b:continue
   ps=[p for p in xml.xpath('//w:p',namespaces=NS) if ''.join(p.xpath('.//w:t/text()',namespaces=NS))==b['preference']];assert ps
   for p in ps:assert p.xpath('.//w:color[@w:val="707070"]',namespaces=NS) and p.xpath('.//w:sz[@w:val="15"]',namespaces=NS)
  textpages=['']
  for node in xml.find('w:body',NS):
   if node.xpath('.//w:br[@w:type="page"]',namespaces=NS):textpages.append('')
   textpages[-1]+=''.join(node.xpath('.//w:t/text()',namespaces=NS))
  for table in xml.xpath('//w:tbl',namespaces=NS):assert table.find('w:tblPr/w:tblLayout',NS).get('{'+NS['w']+'}type')=='fixed'
  a=fitz.open(pdf);b=fitz.open(other/(ident+'.pdf'));assert len(a)==len(b)==len(textpages)==2
  pagechecks=[]
  for i,p in enumerate(a):
   missing=chars(textpages[i])-chars(p.get_text());extra=chars(p.get_text())-chars(textpages[i])
   assert not missing and not extra,(ident,i,missing,extra)
   assert len(p.get_image_info())==3
   for wordrect in p.get_text('words'):assert -1<=wordrect[0]<=wordrect[2]<=p.rect.width+1 and -1<=wordrect[1]<=wordrect[3]<=p.rect.height+1
   pix=p.get_pixmap(dpi=110);assert pix.samples==b[i].get_pixmap(dpi=110).samples
   pix.save(str(render/f'{ident}-{i+1}.png'))
   pagechecks.append(dict(page=i+1,missing_characters=0,extra_characters=0,pixel_sha256=hashlib.sha256(pix.samples).hexdigest()))
  checks.append(dict(id=ident,hours=d['hours'],tests=d['tests'],data_sha256=sha(BASE/'data'/(ident+'.json')),word_sha256=sha(word),pdf_sha256=sha(pdf),pages=pagechecks))
 qa=dict(status='passed',scope='two one-week samples, not full-year plans',textbooks=source,independent_render_pixels_match=True,microsoft_word_tested=False,full_book_line_by_line_audit=False,negative_tests=10,checks=checks)
 (BASE/'SAMPLE_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
 exec((BASE/'scripts/check_preserved.py').read_text(),{'__file__':str(BASE/'scripts/check_preserved.py')})
 print('PASS: two samples; source hashes, complete scope, study before tests, 4h finals, Thursday tests only, native Word/all-page text/independent PDFs, 10 negative tests.')
if __name__=='__main__':main()
