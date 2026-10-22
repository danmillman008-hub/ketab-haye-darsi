"""Compare every exam against reviewed MAZ rows and current-book endpoints."""
import json,re,hashlib,sys,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'annual/scripts'))
from check_topics import pages_from_box,page_ranges
load=lambda p:json.loads((ROOT/p).read_text())
review=load('annual/MAZ_SCOPE_REVIEW.json');manifest=load('annual/manifest.json')
calendar=load('docs/maz-calendar.json')
assert review['source_sha256']==calendar['source']['sha256']==hashlib.sha256((ROOT/'google_drive'/calendar['source']['filename']).read_bytes()).hexdigest()
assert {x['id'] for x in review['entries']}=={x['id'] for x in manifest}
def norm(t):return ''.join(c for c in unicodedata.normalize('NFKC',t) if c.isalnum())
def flatten(rs):return {(g,p) for g,a,b in rs for p in range(a,b+1)}
checks=[]
for row in review['entries']:
 d=load('annual/data/'+row['id']+'.json')
 text=' '.join(b['topic'] for day in d['days'] for b in day['boxes'] if b['subject']=='ریاضی')
 for topic in row['math_topics']:assert norm(topic) in norm(text),(d['id'],topic)
 if row.get('mode')=='comprehensive-selected-review':
  assert d['special'] and d['scopes'][-1]['review']
  assert d['scopes'][-1]['label']=='سه پایه'
 else:
  for field,word in [('bio','زیست'),('chem','شیمی')]:
   if d['scopes']:actual=flatten([x[:3] for w in d['scopes'] for x in w[field]])
   else:
    actual=set()
    for day in d['days']:
     bs=[b for b in day['boxes'] if b['subject'].startswith(word)]
     if bs:actual|=pages_from_box(bs[0])
   assert actual==flatten(row[field]),(d['id'],field,actual^flatten(row[field]))
  actual=set()
  if d['scopes']:
   for w in d['scopes']:
    rs=page_ranges(w['physics'][0]) or [(1,{10:120,11:104,12:125}[w['grade']])]
    actual|={(w['grade'],p) for a,b in rs for p in range(a,b+1)}
  else:
   for day in d['days']:
    bs=[b for b in day['boxes'] if b['subject'].startswith('فیزیک')]
    if bs:actual|=pages_from_box(bs[0])
  assert actual==flatten(row['physics']),(d['id'],'physics',actual^flatten(row['physics']))
 checks.append({'id':d['id'],'maz_page':row['maz_pdf_page'],'status':'passed'})
for row in review['thematic']:
 d=load('annual/data/'+row['id']+'.json');w=d['scopes'][row['week']-1]
 text=' '.join(t for subject,t in w[row['field']])
 assert w['review']
 for word in row['required']:assert norm(word) in norm(text),(row['id'],word)
 # The daily tasks must actually carry the selected scope into student boxes.
 for n,(subject,topic) in enumerate(w[row['field']]):
  day=next(x for x in d['days'] if x['week']==row['week'] and x['day']==2*n+(row['field']=='chem_daily'))
  boxes=[b for b in day['boxes'] if b['subject']==subject]
  assert boxes and all(b['topic']==topic for b in boxes)
r={'status':'passed','method':'topic-first','checks':checks,'thematic_checks':review['thematic'],'equal_page_load_claim':False,'full_text_line_by_line_claim':False,'review_sha256':hashlib.sha256((ROOT/'annual/MAZ_SCOPE_REVIEW.json').read_bytes()).hexdigest(),'data_hashes':{e['id']:hashlib.sha256((ROOT/'annual/data'/(e['id']+'.json')).read_bytes()).hexdigest() for e in manifest}}
(ROOT/'annual/BUDGET_QA.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print('PASS: 21 reviewed exam scopes, mathematics topic coverage, 3 thematic selections without invented whole-chapter page loads.')
