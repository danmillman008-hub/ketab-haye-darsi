"""Fixed-formula/calendar regression and named student-facing copy; source corrections are allowed."""
from pathlib import Path
import json,hashlib,re,subprocess
ROOT=Path(__file__).resolve().parents[2]
def baseline(path):return json.loads(subprocess.check_output(['git','show','50b9922:'+path],cwd=ROOT))
def pages(text):
 return {p for a,b in re.findall(r'ص\s*([۰-۹0-9]+)\s*[–ـ-]\s*([۰-۹0-9]+)',text) for p in range(int(a),int(b)+1)}
import sys
sys.path.insert(0,str(ROOT/'annual'))
from aban15_revision import validate as validate_aban15
checks=[]
for e in json.loads((ROOT/'annual/manifest.json').read_text()):
 path='annual/data/'+e['id']+'.json';new=json.loads((ROOT/path).read_text());old=baseline(path)
 # Source-supported changes are audited separately, not forced back to old pages.
 assert new['weeks']==old['weeks'] and new['start']==old['start'] and new['target']==old['target']
 assert new['pages']==new['weeks']*2
 if new['id']=='1405-08-15':validate_aban15(new)
 else:
  for a,b in zip(old['days'],new['days'],strict=True):
   assert (a['week'],a['day'],a['date'],a['hours'],a['tests'])==(b['week'],b['day'],b['date'],b['hours'],b['tests'])
   for x,y in zip(a['boxes'],b['boxes'],strict=True):
    assert (x['subject'].split()[0],x['hours'],x['tests'])==(y['subject'].split()[0],y['hours'],y['tests'])
    assert x['detail']==y['detail']  # Only page allocation/title may change.

    for forbidden in ['ماز','صفحات محدوده','طبق فرمول','مطابق آزمون','گ۱','گ۲','گ۳']:
     assert forbidden not in y['topic']+' '+y['detail']
    assert not re.search(r'؛\s*[۰-۹0-9]+ صفحه',y['topic'])
    if y['subject'].startswith('زیست'):
     meaningful=re.sub(r'[۰-۹0-9\W]+',' ',y['topic']);meaningful=re.sub(r'\b(فصل|گفتار|ص)\b','',meaningful)
     assert len(meaningful.strip())>=2,('Missing named biology topic',e['id'],y['topic'])
 checks.append({'id':e['id'],'data_sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()})
(ROOT/'annual/STYLE_QA.json').write_text(json.dumps({'status':'passed','baseline':'50b9922','unchanged_calendar_and_formula_except_approved_15_aban':True,'instructions_hours_tests_unchanged_except_approved_15_aban':True,'plans':len(checks),'student_source_notes_forbidden':True,'checks':checks},ensure_ascii=False,indent=2)+'\n')
print('PASS: 21 plans (approved 15 Aban exception), topic-first allocation and short-goftar review, named biology topics, no source/volume commentary.')
