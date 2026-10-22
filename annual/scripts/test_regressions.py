"""Negative tests: deliberately corrupted schedules must be rejected; originals always restored."""
import copy,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
master=ROOT/'annual/YEAR_PLAN.json';master_bytes=master.read_bytes()
cases=[('short-goftar-review','1405-08-01',' + مرور گفتارهای پیشین همین هفته',''),('whole-goftar-cut','1405-08-01','۳۳–۴۴','۳۳–۴۳'),('math-current-page','1405-07-17','۱۰۱–۱۰۸','۱۰۴–۱۰۹'),('nuclear-boundary','1406-02-17','۱۱۲–۱۲۵','۱۰۳–۱۲۵')]
for name,identifier,before,after in cases:
 p=ROOT/'annual/data'/(identifier+'.json');original=p.read_bytes()
 try:
  d=json.loads(original);changed=False
  for day in d['days']:
   for box in day['boxes']:
    if before in box['topic']:box['topic']=box['topic'].replace(before,after);changed=True
  assert changed,name
  plans=json.loads(master_bytes)
  plans=[d if x['id']==identifier else x for x in plans]
  p.write_text(json.dumps(d,ensure_ascii=False));master.write_text(json.dumps(plans,ensure_ascii=False))
  result=subprocess.run([sys.executable,'annual/scripts/check_topics.py'],cwd=ROOT,capture_output=True,text=True)
  assert result.returncode!=0,(name,'Corruption was accepted')
  print('PASS: rejects',name)
 finally:p.write_bytes(original);master.write_bytes(master_bytes)
subprocess.run([sys.executable,'annual/scripts/check_topics.py'],cwd=ROOT,check=True)
