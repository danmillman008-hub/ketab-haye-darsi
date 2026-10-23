"""User-approved exception for 15 Aban only; all other plans retain the base formula."""
import copy,json,subprocess
from pathlib import Path
ID='1405-08-15'
ROOT=Path(__file__).resolve().parents[1]
def apply(plan):
 if plan['id']!=ID:return plan
 for day in plan['days']:
  w=plan['scopes'][day['week']-1]
  for box in day['boxes']:
   code=box['subject'].split()[0]
   if code in ['ریاضی','فیزیک'] and box['tests']:
    box['preference']='* ترجیحاً: '+box['topic']
    box['topic']=w['math' if code=='ریاضی' else 'physics'][0]
    box['detail']='۳۰ تست '+('غیرزمان‌دار' if day['day'] in [0,1] else 'ترجیحاً زمان‌دار')+' + تحلیل'
   if day['week']==1 and code=='شیمی':
    box['topic']={1:'مولکول‌ها در خدمت تندرستی؛ ص۲۴–۲۶؛ از pH',3:'مولکول‌ها در خدمت تندرستی؛ ص۲۷–۳۰؛ قبل از شوینده‌های خورنده',5:'مولکول‌ها در خدمت تندرستی؛ ص۲۴–۳۰؛ از pH تا قبل از شوینده‌های خورنده'}[day['day']]
    if day['day']==5 and not box['tests']:
     box.update(hours=2,tests=25,detail='۲۵ تست از محدودهٔ مطالعه‌شده + تحلیل')
  if day['day'] in [1,3]:day['boxes'].append(dict(subject='دروس نهایی',topic='مطالعه دروس نهایی',detail='مرور متن و تمرین تشریحی',hours=2,tests=0))
  day['hours']=sum(b['hours'] for b in day['boxes']);day['tests']=sum(b['tests'] for b in day['boxes'])
 return plan

def validate(plan):
 assert plan['id']==ID
 base=json.loads(subprocess.check_output(['git','show','dffd67f:annual/data/'+ID+'.json'],cwd=ROOT))
 assert json.loads(json.dumps(plan))==apply(copy.deepcopy(base)),'Unapproved change in 15 Aban'
 for wi,(hours,tests) in enumerate([(52,520),(51,495)],1):
  days=[d for d in plan['days'] if d['week']==wi]
  assert sum(d['hours'] for d in days)==hours and sum(d['tests'] for d in days)==tests
  assert [d['hours'] for d in days]==([8,9,9,9,9,8] if wi==1 else [8,9,9,9,9,7])
  finals=[b for d in days for b in d['boxes'] if b['subject']=='دروس نهایی']
  assert len(finals)==2 and all(b['hours']==2 and b['tests']==0 for b in finals)
  chem=[b for d in days for b in d['boxes'] if b['subject'].startswith('شیمی')]
  assert len(chem)==6 and sum(b['tests']==0 for b in chem)==(2 if wi==1 else 3)
  assert sum(b['tests'] for b in chem)==(100 if wi==1 else 75)
  for day in days:
   assert len(day['boxes'])<=6
   for b in day['boxes']:
    if b['subject'] in ['ریاضی','فیزیک دهم','فیزیک دوازدهم'] and b['tests']:
     assert b['tests']==30 and b['hours']==2 and b['preference'].startswith('* ترجیحاً: ')
 return True
