"""Rebuild all plans, including 1 Aban, from the reviewed 1405 edition scopes."""
import sys,json,hashlib,copy,math
from pathlib import Path
from datetime import timedelta
import jdatetime
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'annual'))
from curriculum import *
from revision1405 import apply, volumes, enrich_final, math_ranges
apply()
fa=lambda x:str(x).translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹'))
MONTHS=['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
DAYS=['شنبه','یکشنبه','دوشنبه','سه‌شنبه','چهارشنبه','پنجشنبه']
def jd(s):return jdatetime.date(*map(int,s.split('-')))
def date_label(d,year=False):return fa(d.day)+' '+MONTHS[d.month-1]+(' '+fa(d.year) if year else '')
def groups(items,n):
 if len(items)<n:return [[items[min(i,len(items)-1)]] for i in range(n)]
 q,r=divmod(len(items),n);out=[];pos=0
 for i in range(n):k=q+(i<r);out.append(items[pos:pos+k]);pos+=k
 return out

def bio_units(scopes):
 units=[]
 for grade,a,b in scopes:
  for chapter,title,lo,hi,goftars in BIO[grade]:
   for idx,(start,topic) in enumerate(goftars):
    first=lo if idx==0 else start;end=goftars[idx+1][0]-1 if idx+1<len(goftars) else hi
    x,y=max(a,first),min(b,end)
    if x<=y:units.append(dict(grade=grade,chapter=chapter,goftar=idx+1,topic=topic,start=x,end=y))
 return units

def weighted_groups(units,n=3):
 # Respect complete goftars when possible. Only split a goftar when fewer
 # units than study days exist; no extra study/test boxes are introduced.
 units=copy.deepcopy(units)
 while len(units)<n:
  ix=max(range(len(units)),key=lambda i:units[i]['end']-units[i]['start'])
  u=units[ix];assert u['end']>u['start']
  mid=(u['start']+u['end'])//2
  left=dict(u,end=mid);right=dict(u,start=mid+1)
  units[ix:ix+1]=[left,right]
 from itertools import combinations
 def score(cuts):
  points=(0,*cuts,len(units));loads=[sum(u['end']-u['start']+1 for u in units[a:b]) for a,b in zip(points,points[1:])]
  return (max(loads)-min(loads),sum(x*x for x in loads),cuts)
 cuts=min(combinations(range(1,len(units)),n-1),key=score)
 points=(0,*cuts,len(units))
 return [units[a:b] for a,b in zip(points,points[1:])]

def bio_daily(w):
 if 'bio_daily' in w:return w['bio_daily']
 result=[]
 for chunk in weighted_groups(bio_units(w['bio'])):
  by={}
  for u in chunk:by.setdefault((u['grade'],u['chapter']),[]).append(u)
  parts=[];grades=[]
  for (grade,ch),us in by.items():
   if grade not in grades:grades.append(grade)
   gs=sorted(set(u['goftar'] for u in us));label=fa(gs[0]) if len(gs)==1 else fa(gs[0])+'–'+fa(gs[-1])
   prefix=(GRADES[grade]+'؛ ') if len(set(u['grade'] for u in chunk))>1 else ''
   parts.append(prefix+'فصل '+fa(ch)+' گ'+label+'؛ ص'+fa(us[0]['start'])+'–'+fa(us[-1]['end']))
  pages=sum(u['end']-u['start']+1 for u in chunk)
  result.append(('زیست '+' و '.join(GRADES[g] for g in grades),' / '.join(parts)+'؛ '+fa(pages)+' صفحه'))
 return result

def chem_daily(w):
 if 'chem_daily' in w:return w['chem_daily']
 pages=[(g,p,t) for g,a,b,t in w['chem'] for p in range(a,b+1)]
 result=[]
 for chunk in groups(pages,3):
  parts=[];grades=[];runs=[]
  for g,p,t in chunk:
   if g not in grades:grades.append(g)
   if runs and runs[-1][0]==g and runs[-1][3]==t and runs[-1][2]+1==p:runs[-1][2]=p
   else:runs.append([g,p,p,t])
  for g,a,b,t in runs:
   # Current printed pages; boundary restrictions are retained in the scope audit.
   parts.append(t+'؛ ص'+fa(a)+('–'+fa(b) if a!=b else ''))
  result.append(('شیمی '+' و '.join(GRADES[g] for g in grades),' / '.join(parts)+'؛ '+fa(len(chunk))+' صفحه'))
 return result

def box(s,t,d,h,n=0):return dict(subject=s,topic=t,detail=d,hours=h,tests=n)
def make_days(weeks,start):
 days=[];metas=[]
 for wi,w in enumerate(weeks):
  bio=bio_daily(w);chem=chem_daily(w);g=w['grade'];review=w['review']
  if w.get('chem_boundary'):chem[-1]=(chem[-1][0],chem[-1][1]+'؛ '+w['chem_boundary'])
  if w.get('physics_boundary'):w['physics'][0]+='؛ '+w['physics_boundary']
  first=start+timedelta(days=wi*7) if start else None
  metas.append(dict(label=w['label'],date_range=(date_label(first)+' تا '+date_label(first+timedelta(days=6),True)) if first else 'هفتهٔ نسبی '+fa(wi+1)+'؛ تاریخ اعلام نشده',friday=date_label(first+timedelta(days=6)) if first else 'جمعهٔ هفتهٔ '+fa(wi+1)))
  for di in range(6):
   n=di//2
   if di%2==0:
    s,t=bio[n];study=box(s,t,'مرور متن، شکل‌ها و نکات نشان‌دار' if review else 'مطالعهٔ دقیق متن، شکل‌ها و قیدهای کتاب',1)
    bt=[box(s,t,'۲۰ تست آموزشی + تحلیل همهٔ گزینه‌ها',2,20),box(s,t,'۲۰ تست تکمیلی + تحلیل و ثبت خطا',2,20)]
    mt=[box('ریاضی',w['math'][i],('غیرزمان‌دار' if n==0 else 'ترجیحاً زمان‌دار')+'؛ ۳۰ تست + تحلیل',2,30) for i in ([1] if n==0 else [n*2,n*2+1])]
    if n==0:mt.insert(0,box('ریاضی',w['math'][0],'۱ ساعت مرور درسنامه و مثال‌های اصلی' if review else '۱ ساعت درسنامه و مثال‌های اصلی',1))
    for mb in mt:
     if 'ریاضی' not in mb['topic']:
      grades=list(dict.fromkeys(g for g,a,b in math_ranges(w)))
      mb['topic']=' و '.join(GRADES[g] for g in grades)+'؛ '+mb['topic']
    bs=[study,mt[0],bt[0],mt[1],bt[1]]
   else:
    def ps(i):return 'فیزیک '+(GRADES[w['physics_daily_grades'][i]] if 'physics_daily_grades' in w else GRADES[g])
    pt=[box(ps(i),w['physics'][i],('غیرزمان‌دار' if n==0 else 'ترجیحاً زمان‌دار')+'؛ ۳۰ تست + تحلیل',2,30) for i in ([1] if n==0 else [n*2,n*2+1])]
    if n==0:pt.insert(0,box('فیزیک سه پایه' if 'physics_daily_grades' in w else ps(0),w['physics'][0],'۲ ساعت مرور درسنامه و مثال‌ها' if review else '۲ ساعت درسنامه و مثال؛ تنها درسنامهٔ هفته',2))
    s,t=chem[n]
    bs=[pt[0],box(s,t,'۱ ساعت مرور متن، شکل و تمرین‌ها' if review else '۱ ساعت متن کتاب، شکل و خودرابیازمایید',1),pt[1],box(s,t,'۲۵ تست مرتبط + تحلیل کامل',2,25)]
   days.append(dict(week=wi+1,day=di,name=DAYS[di],date=date_label(first+timedelta(days=di)) if first else 'روز '+fa(wi*7+di+1),iso=(first+timedelta(days=di)).isoformat() if first else None,boxes=bs,hours=sum(b['hours'] for b in bs),tests=sum(b['tests'] for b in bs)))
 return days,metas

calendar=json.loads((ROOT/'docs/maz-calendar.json').read_text())
items=[];prev=None
for month in calendar['months']:
 for day in month['days']:
  target=jdatetime.date(month['year'],month['month'],day);key=target.isoformat()
  assert target.weekday()==6,(key,target.weekday()) # jdatetime: Saturday=0
  n=2 if prev is None else (target-prev).days//7
  assert prev is None or (target-prev).days%7==0
  start=target-timedelta(days=n*7-1)
  dest=Path('برنامه تحصیلی')/month['folder']/(fa(day)+' '+month['name'])
  label=date_label(target,True);existing=False
  if existing:
   data=copy.deepcopy(json.loads((ROOT/'stitch-14/plan.json').read_text()));metas=[];weeks=[]
   stem='برنامه آزمون ۰۱ آبان ۱۴۰۵'
  else:
   weeks=copy.deepcopy((NORMAL|SPECIAL)[key]);assert len(weeks)==n,(key,n,len(weeks))
   data,metas=make_days(weeks,start);stem='برنامه آزمون '+label
   if key=='1405-08-01':stem='برنامه آزمون ۰۱ آبان ۱۴۰۵'
  special=key in REASONS
  notes=[REASONS[key]] if special else []
  if key=='1405-09-27':notes.append('گذار بودجهٔ پایه از دهم به یازدهم طبق خودِ ردیف ۲۷ آذر ماز انجام شده است.')
  if key=='1406-02-17':notes.append('فیزیک: ماز بازهٔ ۱۰۳–۱۲۵ را کنار «از ساختار هسته» نوشته؛ ساختار هسته در کتاب از ۱۱۲ است. برای حذف‌نشدن بودجه، ۱۰۳–۱۱۱ نیز مرور شده است.')
  if key in ['1406-03-28','1406-04-04']:
   for w in weeks:w['review']=True
   for d in data:
    for b in d['boxes']:
     if b['tests']:b['detail']=fa(b['tests'])+' تست نشان‌دار + تحلیل خطاهای جامع قبلی'
  item=dict(id=key,title='برنامهٔ آزمون '+label,target=key,start=start.isoformat(),weeks=n,pages=n*2+int(special),special=special,reason=REASONS.get(key,''),notes=notes,source_page=month['source_page'],preserved=existing,directory=str(dest),stem=stem,days=data,week_meta=metas,scopes=weeks)
  items.append(item);prev=target
# Undated folders get reusable relative-week plans, never invented calendar dates.
for number in [1,2]:
 weeks=[full_week(12),enrich_final(compressed_final())]
 data,metas=make_days(weeks,None)
 for d in data:
  for b in d['boxes']:
   if b['tests']:b['detail']=fa(b['tests'])+' تست '+('نشان‌دار' if number==1 else 'از خطاهای پریمیوم اول')+' + تحلیل کامل'
 title='آزمون جامع پریمیوم '+fa(number)
 items.append(dict(id='premium-'+str(number),title=title,target=None,start=None,weeks=2,pages=5,special=True,reason='تاریخ رسمی اعلام نشده؛ فایل برآیندی با هفته‌های نسبی، نه برنامهٔ تقویمی قطعی.',notes=['پس از اعلام تاریخ و بودجهٔ نهایی ماز، تاریخ‌گذاری و انطباق نهایی لازم است.','مرور انتخابی و رفع خطا؛ این فایل جای مطالعهٔ اولیهٔ کل کتاب‌ها نیست.'],source_page=7,preserved=False,directory=str(Path('برنامه تحصیلی')/'تاریخ اعلام‌نشده'/title),stem='فایل برآیندی '+title+' - بدون تاریخ',days=data,week_meta=metas,scopes=weeks))
for it in items:
 for w in it['scopes']:w['page_volume']=volumes(w)
 it['edition']='چاپ ۱۴۰۵'
 it['page_count_method']='شمار صفحات چاپی در محدوده؛ صفحات مشترک مرزی یک بار؛ تکرار تست شمرده نمی‌شود. مرور موضوعی به معنای مطالعهٔ کامل همهٔ صفحات نیست.'
 for d in it['days']:
  assert d['hours']==[8,7,9,7,9,7][d['day']]
  assert d['tests']==[70,55,100,85,100,85][d['day']]
  assert [b['subject'].split()[0] for b in d['boxes']]==(['زیست','ریاضی','زیست','ریاضی','زیست'] if d['day']%2==0 else ['فیزیک','شیمی','فیزیک','شیمی'])
 assert sum(d['hours'] for d in it['days'])==47*it['weeks']
 assert sum(d['tests'] for d in it['days'])==495*it['weeks']
 # No missing pages in the ordinary goftar mapping.
 for w in it['scopes']:
  for g,a,b in w['bio']:
   covered={p for u in bio_units([(g,a,b)]) for p in range(u['start'],u['end']+1)}
   assert covered==set(range(a,b+1))
 (ROOT/'annual/data'/f"{it['id']}.json").write_text(json.dumps(it,ensure_ascii=False,indent=2)+'\n')
summary=[{k:v for k,v in it.items() if k not in ['days','scopes','week_meta']} for it in items]
(ROOT/'annual/manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print('Generated',len(items),'plans;',sum(it['weeks'] for it in items if it['target']),'dated weeks;',sum(it['pages'] for it in items),'pages; all plans rebuilt.')
