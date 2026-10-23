"""Focused regression tests for the approved 15 Aban revision and unchanged other plans."""
import sys,json,copy,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'annual'))
from aban15_revision import ID,validate
p=json.loads((ROOT/'annual/data'/(ID+'.json')).read_text());validate(p)
for case in ['missing-finals','wrong-chem-hours','forced-subtopic','wrong-week-total','missing-boundary']:
 q=copy.deepcopy(p)
 if case=='missing-finals':q['days'][1]['boxes'].pop()
 if case=='wrong-chem-hours':q['days'][5]['boxes'][1]['hours']=1
 if case=='forced-subtopic':q['days'][0]['boxes'][3]['topic']='نسبت‌های مثلثاتی'
 if case=='wrong-week-total':q['days'][1]['hours']=7
 if case=='missing-boundary':q['days'][3]['boxes'][1]['topic']='مولکول‌ها در خدمت تندرستی؛ ص۲۷–۳۰'
 try:validate(q)
 except AssertionError:print('PASS: rejects',case)
 else:raise AssertionError('Invalid schedule accepted: '+case)
for e in json.loads((ROOT/'annual/manifest.json').read_text()):
 if e['id']==ID:continue
 for path in ['annual/data/'+e['id']+'.json']+[str(Path(e['directory'])/(e['stem']+'.'+ext)) for ext in ['docx','pdf']]:
  assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show','dffd67f:'+path],cwd=ROOT),path
for path,h in json.loads((ROOT/'annual/preserved.json').read_text()).items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h
print('PASS: approved 15 Aban counts and exact changes; other 20 data/Word/PDF plans and reports unchanged.')
