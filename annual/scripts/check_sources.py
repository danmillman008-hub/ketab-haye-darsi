"""Check actual active PDFs, boundary evidence and generated coverage. No renderer dependency."""
from pathlib import Path
import hashlib,json,re,sys,unicodedata,subprocess
from check_topics import pages_from_box
from collections import Counter
import pymupdf
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'annual'))
from curriculum import BIO
load=lambda p:json.loads((ROOT/p).read_text())
books={b['key']:b for b in load('annual/BOOK_EDITIONS.json')['books']}
docs={}
for k,b in books.items():
 p=ROOT/b['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==b['sha256'],k
 assert hashlib.md5(p.read_bytes()).hexdigest()==b['md5'],k
 docs[k]=pymupdf.open(p);assert len(docs[k])==b['pdf_pages']
def text(k,p):return docs[k][p+books[k]['pdf_offset']-1].get_text()
def norm(s):return re.sub(r'[^\w]+','',unicodedata.normalize('NFKC',s).replace('ك','ک').replace('ي','ی'))
starts=[]
for g,chs in BIO.items():
 for ch,title,lo,hi,units in chs:
  for page,name in units:
   assert 'گفتار' in text('b'+str(g),page),(g,page)
   starts.append([g,ch,page])
anchors=[('c10',98,'غلظت مولی'),('c12',37,'آسایش و رفاه'),('c12',44,'سفر'),('c12',61,'آبکاری'),('c12',62,'فرایند هال'),('c12',77,'شاره'),('c12',86,'واناد'),('c12',103,'آمونیاک'),('c12',111,'ارزش فناوری'),('c11',77,'غذای سالم'),('p12',15,'شتاب ثابت'),('p12',37,'اصطکاک'),('p12',44,'تکانه'),('p12',62,'مشخصه'),('p12',64,'موج عرضی'),('p12',76,'بازتاب'),('p12',112,'ساختار هسته'),('p11',45,'عوامل مؤثر'),('p11',85,'القای'),('m12',77,'مشتق'),('m11',25,'ترسیم'),('m10',94,'تابع')]
for k,p,anchor in anchors:assert norm(anchor) in norm(text(k,p)),(k,p,anchor)
def ranges(t):return [(int(a),int(b or a)) for a,b in re.findall(r'ص\s*([۰-۹0-9]+)(?:\s*–\s*([۰-۹0-9]+))?',t)]
catalog_probes=[]
def anchor_norm(s):
 s=s.replace('ۀ','ه').replace('معادالت','معادلات').replace('استدالل','استدلال')
 return ''.join(c for c in unicodedata.normalize('NFKC',s).replace('ي','ی').replace('ك','ک') if c.isalnum())
for r in load('annual/PAGE_CATALOG.json')['rows']:
 k=r['book'];p=r['heading_page']
 assert 1<=r['start']<=p<=r['end']<=books[k]['printed_content_end'],r
 anchor='پرسش' if r['title'].startswith('تمرین') else r['title'].split()[0].split('؛')[0].split('،')[0].split('‌')[0]
 if (k,p)==('m12',42):anchor='دو برابر' # Main heading is outline artwork; visually checked.
 assert anchor_norm(anchor) in anchor_norm(text(k,p)),(k,p,anchor)
 catalog_probes.append({'book':k,'printed_page':p,'anchor':anchor})
checks=[];changes=[]
for e in load('annual/manifest.json'):
 data=load('annual/data/'+e['id']+'.json')
 old=json.loads(subprocess.check_output(['git','show','50b9922:annual/data/'+e['id']+'.json'],cwd=ROOT))
 assert len(old['days'])==len(data['days'])
 if data['id']=='1405-08-15':
  from aban15_revision import validate as validate_aban15
  validate_aban15(data)
 else:
  for a,b in zip(old['days'],data['days']):
   assert [(x['subject'].split()[0],x['hours'],x['tests']) for x in a['boxes']]==[(x['subject'].split()[0],x['hours'],x['tests']) for x in b['boxes']]
 for wi,w in enumerate(data['scopes'],1):
  days=[d for d in data['days'] if d['week']==wi]
  for code,field in [('b','bio'),('c','chem')]:
   for scope in w[field]:
    g,a,b=scope[:3];assert 1<=a<=b<=books[code+str(g)]['printed_content_end']
   if w[field]:
    target={(g,p) for g,a,b,*_ in w[field] for p in range(a,b+1)};actual=[]
    for day in days[(0 if code=='b' else 1)::2]:
     box=day['boxes'][0 if code=='b' else 1]
     actual.extend(pages_from_box(box))
    assert set(actual)==target,(e['id'],wi,code,set(actual)^target)
  checks.append({'id':e['id'],'week':wi,'coverage':'passed'})
 for day,prior in zip(data['days'],old['days']):
  for j,(newbox,oldbox) in enumerate(zip(day['boxes'],prior['boxes'])):
   if newbox['topic']!=oldbox['topic']:changes.append({'id':e['id'],'week':day['week'],'day':day['name'],'box':j+1,'before':oldbox['topic'],'after':newbox['topic']})
result={'status':'passed','scope':'Actual source hashes; 69 biology goftar starts; 220 named-unit page/keyword probes (not a line-by-line semantic audit); selected printed-page boundary anchors; exact ordinary biology/chemistry page-set coverage; unchanged base formula except the user-approved 15 Aban revision. Not a full line-by-line audit of every textbook or individual student feasibility.','books_verified':len(books),'biology_starts':len(starts),'anchors':[{'book':k,'printed_page':p,'anchor':a} for k,p,a in anchors],'catalog_heading_probes':catalog_probes,'catalog_sha256':hashlib.sha256((ROOT/'annual/PAGE_CATALOG.json').read_bytes()).hexdigest(),'full_text_line_by_line_claim':False,'unresolved_source_conflicts':[],'resolved_source_conflicts':[{'id':'1406-02-17','week':1,'subject':'physics12','maz_pdf_page':7,'maz_numeric_range':[103,125],'maz_start_heading':'ساختار هسته','current_book_heading_page':112,'status':'resolved-current-textbook-first','corrected_range':[112,125],'note':'User explicitly prioritized current textbooks over MAZ; heading verified on current textbook p112.'}],'weeks':len(checks),'checks':checks,'data_hashes':{e['id']:hashlib.sha256((ROOT/'annual/data'/(e['id']+'.json')).read_bytes()).hexdigest() for e in load('annual/manifest.json')}}
(ROOT/'annual/SOURCE_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(ROOT/'annual/SOURCE_CHANGES.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')
print('PASS: 12 current PDFs,',len(starts),'goftar starts,',len(anchors),'boundary anchors,',len(catalog_probes),'catalog page/keyword probes,',len(checks),'weekly coverage checks.')
