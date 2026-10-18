"""Check actual active PDFs, boundary evidence and generated coverage. No renderer dependency."""
from pathlib import Path
import hashlib,json,re,sys,unicodedata,subprocess
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
checks=[];changes=[]
for e in load('annual/manifest.json'):
 data=load('annual/data/'+e['id']+'.json')
 old=json.loads(subprocess.check_output(['git','show','5395648:annual/data/'+e['id']+'.json'],cwd=ROOT))
 assert len(old['days'])==len(data['days'])
 for a,b in zip(old['days'],data['days']):
  assert [(x['subject'],x['hours'],x['tests']) for x in a['boxes']]==[(x['subject'],x['hours'],x['tests']) for x in b['boxes']]
 for wi,w in enumerate(data['scopes'],1):
  days=[d for d in data['days'] if d['week']==wi]
  for code,field in [('b','bio'),('c','chem')]:
   for scope in w[field]:
    g,a,b=scope[:3];assert 1<=a<=b<=books[code+str(g)]['printed_content_end']
   if w[field] and not w.get(field+'_daily'):
    target={(g,p) for g,a,b,*_ in w[field] for p in range(a,b+1)};actual=[]
    for day in days[(0 if code=='b' else 1)::2]:
     box=day['boxes'][0 if code=='b' else 1]
     g=next(g for g,s in [(10,'دهم'),(11,'یازدهم'),(12,'دوازدهم')] if s in box['subject'].split())
     # Notes may mention one boundary page again; compare coverage as a set.
     for a,b in ranges(box['topic']):actual.extend((g,p) for p in range(a,b+1))
    assert set(actual)==target,(e['id'],wi,code,set(actual)^target)
  checks.append({'id':e['id'],'week':wi,'coverage':'passed'})
 for day,prior in zip(data['days'],old['days']):
  for j,(newbox,oldbox) in enumerate(zip(day['boxes'],prior['boxes'])):
   if newbox['topic']!=oldbox['topic']:changes.append({'id':e['id'],'week':day['week'],'day':day['name'],'box':j+1,'before':oldbox['topic'],'after':newbox['topic']})
result={'status':'passed','scope':'Actual source hashes; 69 biology goftar starts; selected printed-page boundary anchors; exact ordinary biology/chemistry page-set coverage; unchanged formula. Not a full line-by-line audit of every textbook or individual student feasibility.','books_verified':len(books),'biology_starts':len(starts),'anchors':[{'book':k,'printed_page':p,'anchor':a} for k,p,a in anchors],'weeks':len(checks),'checks':checks,'data_hashes':{e['id']:hashlib.sha256((ROOT/'annual/data'/(e['id']+'.json')).read_bytes()).hexdigest() for e in load('annual/manifest.json')}}
(ROOT/'annual/SOURCE_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(ROOT/'annual/SOURCE_CHANGES.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')
print('PASS: 12 current PDFs,',len(starts),'goftar starts,',len(anchors),'boundary anchors,',len(checks),'weekly coverage checks.')
