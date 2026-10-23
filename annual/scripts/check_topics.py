"""Topic-first checks: whole goftars, explicit revision, no fabricated page-equality claims."""
import json,re,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'annual'))
from curriculum import BIO
load=lambda p:json.loads((ROOT/p).read_text())
GRADES={'دهم':10,'یازدهم':11,'دوازدهم':12}
def page_ranges(topic):
 return [(int(a),int(b or a)) for a,b in re.findall(r'ص\s*([۰-۹0-9]+)(?:\s*–\s*([۰-۹0-9]+))?',topic)]
def pages_from_box(box):
 gs=[g for word,g in GRADES.items() if word in box['subject'].split()]
 assert len(gs)==1,box
 return {(gs[0],p) for a,b in page_ranges(box['topic']) for p in range(a,b+1)}
def check():
 checks=[];review_days=[];thematic=[]
 plans=load('annual/YEAR_PLAN.json')
 for d in plans:
  assert d==load('annual/data/'+d['id']+'.json')
  assert 'page_allocation' not in d,'Retired equal-page allocator still active'
  for wi in range(1,d['weeks']+1):
   w=d['scopes'][wi-1] if d['scopes'] else {'bio':[(12,1,20)] if wi==1 else [(10,25,46)]}
   if w.get('bio_daily'):
    thematic.append((d['id'],wi,'bio'));continue
   scope=w['bio'];target={(g,p) for g,a,b in scope for p in range(a,b+1)};covered=set()
   starts=set();ends=set()
   for g,a,b in scope:
    for ch,title,lo,hi,us in BIO[g]:
     for i,(p,name) in enumerate(us):
      x=max(a,lo if i==0 else p);y=min(b,us[i+1][0]-1 if i+1<len(us) else hi)
      if x<=y:starts.add((g,x));ends.add((g,y))
   for day in [x for x in d['days'] if x['week']==wi and x['day']%2==0]:
    bs=[b for b in day['boxes'] if b['subject'].startswith('زیست')];assert len(bs)==3
    assert len({b['topic'] for b in bs})==1
    actual=pages_from_box(bs[0]);covered|=actual
    assert actual<=target,(d['id'],wi,actual-target)
    g=next(iter(actual))[0]
    for a,b in page_ranges(bs[0]['topic']):assert (g,a) in starts and (g,b) in ends,(d['id'],bs[0]['topic'])
    if day['day']>0 and len(actual)<=3:
     assert 'مرور' in bs[0]['topic'],(d['id'],day)
    if 'مرور گفتارهای پیشین همین هفته' in bs[0]['topic']:review_days.append((d['id'],wi,day['day']))
   assert covered==target,(d['id'],wi,'Missing goftar coverage')
   checks.append((d['id'],wi))
  # Check study/test topic order against the weekly named curriculum, not only page sets.
  def clean(t):
   for a,b in [('بازهٔ عددی ماز',''),('ص ماز','ص'),('مسیر مرور ۵۰درصدی؛ ',''),('مسیر مرور؛ ','')]:t=t.replace(a,b)
   return t
  if d['id']=='1405-08-15':
   from aban15_revision import validate as validate_aban15
   validate_aban15(d)
  for wi,w in enumerate(d['scopes'],1):
   if d['id']=='1405-08-15':continue
   for subject,field in [('ریاضی','math'),('فیزیک','physics')]:
    actual=[b['topic'] for day in d['days'] if day['week']==wi for b in day['boxes'] if b['subject'].startswith(subject)]
    assert actual==[clean(t) for t in w[field]],(d['id'],wi,field,'Topic order or scope mismatch')
  if d['id']=='1406-02-17':
   assert d['scopes'][0]['physics'][0]=='ساختار هسته تا پایان فصل۴؛ ص۱۱۲–۱۲۵'
   for day in d['days'][:6]:
    for b in day['boxes']:
     if b['subject'].startswith('فیزیک'):assert 'بور' not in b['topic'] and 'لیزر' not in b['topic']
 organic=load('annual/data/1406-02-03.json')
 assert organic['scopes'][1]['chem_daily']==[
  ['شیمی یازدهم','هیدروکربن‌ها؛ ص۳۱–۴۳'],
  ['شیمی یازدهم','اتر، کتون و آلدهید؛ ص۷۰–۷۲ / کربوکسیلیک‌اسید؛ ص۸۴ + مرور هیدروکربن‌ها'],
  ['شیمی یازدهم','پلیمر، آمین و آمید؛ ص۱۰۲–۱۲۱']]
 # Current textbook lesson boundaries, independent regression expectations.
 early=load('annual/data/1405-07-17.json')
 math=' '.join(b['topic'] for x in early['days'][:6] for b in x['boxes'] if b['subject']=='ریاضی')
 assert 'ص۱۰۱–۱۰۸' in math and 'ص۱۰۹–۱۱۷' in math and 'ص۹۴–۱۰۰' in math
 result={'status':'passed','method':'whole-topics-and-review','equal_page_load_required':False,'whole_goftar_weeks':len(checks),'short_goftar_review_days':review_days,'selected_review_weeks':thematic,'data_hashes':{d['id']:hashlib.sha256((ROOT/'annual/data'/(d['id']+'.json')).read_bytes()).hexdigest() for d in plans}}
 (ROOT/'annual/TOPIC_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('PASS:',len(checks),'whole-goftar weeks; short-goftar revision explicit; current math/physics source corrections retained.')
if __name__=='__main__':check()
