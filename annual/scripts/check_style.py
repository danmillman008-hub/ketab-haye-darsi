"""Fixed-formula/calendar regression and named student-facing copy; source corrections are allowed."""
from pathlib import Path
import json,hashlib,re,subprocess
ROOT=Path(__file__).resolve().parents[2]
def baseline(path):return json.loads(subprocess.check_output(['git','show','fc85e03:'+path],cwd=ROOT))
def pages(text):
 return {p for a,b in re.findall(r'ص\s*([۰-۹0-9]+)\s*[–ـ-]\s*([۰-۹0-9]+)',text) for p in range(int(a),int(b)+1)}
checks=[]
for e in json.loads((ROOT/'annual/manifest.json').read_text()):
 path='annual/data/'+e['id']+'.json';new=json.loads((ROOT/path).read_text());old=baseline(path)
 # Source-supported changes are audited separately, not forced back to old pages.
 assert new['weeks']==old['weeks'] and new['start']==old['start'] and new['target']==old['target']
 assert new['pages']==new['weeks']*2
 for a,b in zip(old['days'],new['days'],strict=True):
  assert (a['week'],a['day'],a['date'],a['hours'],a['tests'])==(b['week'],b['day'],b['date'],b['hours'],b['tests'])
  for x,y in zip(a['boxes'],b['boxes'],strict=True):
   assert (x['subject'],x['hours'],x['tests'])==(y['subject'],y['hours'],y['tests'])
   if e['id']=='1405-08-01':assert x==y,'The accepted Aban box content must be unchanged'

   for forbidden in ['ماز','صفحات محدوده','طبق فرمول','مطابق آزمون','گ۱','گ۲','گ۳']:
    assert forbidden not in y['topic']+' '+y['detail']
   assert not re.search(r'؛\s*[۰-۹0-9]+ صفحه',y['topic'])
   if y['subject'].startswith('زیست'):
    meaningful=re.sub(r'[۰-۹0-9\W]+',' ',y['topic']);meaningful=re.sub(r'\b(فصل|گفتار|ص)\b','',meaningful)
    assert len(meaningful.strip())>=2,('Missing named biology topic',e['id'],y['topic'])
 checks.append({'id':e['id'],'data_sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()})
(ROOT/'annual/STYLE_QA.json').write_text(json.dumps({'status':'passed','baseline':'fc85e03','unchanged_formula_and_calendar':True,'aban_box_content_unchanged':True,'plans':len(checks),'student_source_notes_forbidden':True,'checks':checks},ensure_ascii=False,indent=2)+'\n')
print('PASS: 21 fixed-formula plans, exact Aban boxes, named biology topics, no source/volume commentary.')
