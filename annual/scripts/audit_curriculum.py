"""Content/volume audit independent of the renderer. Fail before publication."""
from pathlib import Path
import json,re,hashlib,sys
import pymupdf as fitz
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'annual'))
from curriculum import BIO
books={b['key']:b for b in json.loads((ROOT/'annual/BOOK_EDITIONS.json').read_text())['books']}
# Actual current files, not historical caches; the 69 goftar start pages.
starts=[]
for key,b in books.items():
 path=ROOT/b['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==b['sha256']
 assert len(fitz.open(path))==b['pdf_pages']
for g,chapters in BIO.items():
 b=books['b'+str(g)];doc=fitz.open(ROOT/b['file'])
 for ch,title,a,z,units in chapters:
  for p,t in units:
   assert 'گفتار' in doc[p+b['pdf_offset']-1].get_text(),(g,ch,p)
   starts.append([g,ch,p])
allchecks=[]
for entry in json.loads((ROOT/'annual/manifest.json').read_text()):
 data=json.loads((ROOT/'annual/data'/(entry['id']+'.json')).read_text())
 assert not data['preserved']
 # Independent transcription of the enlarged MAZ 1-Aban chemistry cell.
 if entry['id']=='1405-08-01':
  assert [tuple(x[:3]) for x in data['scopes'][1]['chem']]==[(10,19,46)]
  assert data['scopes'][1]['page_volume']['chemistry']['unique_pages_in_scope']==28
 for wi,w in enumerate(data['scopes'],1):
  ds=[d for d in data['days'] if d['week']==wi]
  assert sum(d['hours'] for d in ds)==47
  assert sum(d['tests'] for d in ds)==495
  assert sum(len(d['boxes']) for d in ds)==27
  volumes=w['page_volume']
  for subj,code in [('biology','b'),('chemistry','c'),('math','m'),('physics','p')]:
   rs=volumes[subj]['ranges'];pages={(g,p) for g,a,b in rs for p in range(a,b+1)}
   assert len(pages)==volumes[subj]['unique_pages_in_scope']
   for g,a,b in rs:assert 1<=a<=b<=books[code+str(g)]['printed_content_end'],(entry['id'],subj,g,a,b)
  # Ordinary biology daily pages must exactly partition the weekly scopes.
  if not w.get('bio_daily'):
   assigned=[]
   for d in ds[::2]:
    box=d['boxes'][0]
    grade=next(g for g,word in [(10,'دهم'),(11,'یازدهم'),(12,'دوازدهم')] if word in box['subject'].split())
    for a,b in re.findall(r'ص\s*([۰-۹0-9]+)–([۰-۹0-9]+)',box['topic']):assigned.extend((grade,p) for p in range(int(a),int(b)+1))
   target={(g,p) for g,a,b in w['bio'] for p in range(a,b+1)}
   assert set(assigned)==target and len(assigned)==len(target),(entry['id'],wi)
  if w['chem'] and not w.get('chem_daily'):
   assigned=[]
   for d in ds[1::2]:
    box=d['boxes'][1]
    gs=[g for g,word in [(10,'دهم'),(11,'یازدهم'),(12,'دوازدهم')] if word in box['subject'].split()]
    assert len(gs)==1  # Multi-grade chemical scopes must be explicitly mapped.
    for a,b in re.findall(r'؛ ص([۰-۹0-9]+)(?:–([۰-۹0-9]+))?(?=؛| / |$)',box['topic']):
     assigned.extend((gs[0],p) for p in range(int(a),int(b or a)+1))
   target={(g,p) for g,a,b,t in w['chem'] for p in range(a,b+1)}
   assert set(assigned)==target and len(assigned)==len(target),(entry['id'],wi,'chemistry')
  # Math initial lesson then exactly five 30-test boxes; physics same, 2h initial.
  for subject,hour in [('ریاضی',1),('فیزیک',2)]:
   bs=[b for d in ds for b in d['boxes'] if b['subject'].startswith(subject)]
   assert bs[0]['tests']==0 and bs[0]['hours']==hour
   assert [b['tests'] for b in bs[1:]]==[30]*5
  allchecks.append({'id':entry['id'],'week':wi,'volumes':volumes,'thematic':bool(w.get('bio_thematic'))})
result={'status':'passed','book_files_verified':12,'biology_goftar_starts_verified':len(starts),'data_hashes':{e['id']:hashlib.sha256((ROOT/'annual/data'/(e['id']+'.json')).read_bytes()).hexdigest() for e in json.loads((ROOT/'annual/manifest.json').read_text())},'weeks':len(allchecks),'notes':['Page counts are inclusive printed-page scope counts, not workload equivalence.','Thematic scopes count core/enclosing ranges; scattered topical examples are not an exact page total.','This verifies constraints and declared scopes, not individual student feasibility.'],'checks':allchecks}
(ROOT/'annual/CURRICULUM_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS:',len(starts),'goftar starts;',len(allchecks),'weeks; current file hashes, page bounds, exact ordinary bio partition and formula.')
