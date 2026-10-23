"""Only the requested first-week samples; never writes the grade-12 pipeline."""
import json,copy
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
FA=str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹')
def fa(x):return str(x).translate(FA)
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
S={
10:dict(label='دهم',bio=[('دنیای زنده؛ زیست‌شناسی چیست و گسترهٔ حیات؛ ص۱–۱۰',1,10,1,'مرور متن، شکل‌ها و قیدهای کتاب'),('دنیای زنده؛ یاخته و بافت؛ ص۱۱–۱۶',11,16,1,'مطالعه و تثبیت متن و شکل‌های کتاب'),('گوارش و جذب مواد؛ ساختار لولهٔ گوارش؛ ص۱۷–۲۱؛ قبل از شیرهٔ معده',17,21,1,'مطالعهٔ متن، شکل‌ها و مقایسه‌ها')],math='مجموعه، الگو و دنباله؛ ص۱–۲۷',math_ranges=[[1,27]],math_hints=['مجموعه‌ها و الگوها','دنباله‌های حسابی و هندسی'],physics='فیزیک و اندازه‌گیری + ویژگی‌های فیزیکی مواد؛ ص۱–۳۲؛ قبل از فشار در شاره‌ها',physics_end=32,physics_hints=['تبدیل یکا و چگالی','نیروهای بین‌مولکولی'],chem=[('کیهان، زادگاه الفبای هستی؛ عنصرها، ایزوتوپ‌ها و جرم اتمی؛ ص۱–۱۵',1,15,1,'مرور متن، شکل‌ها و مسئله‌های کتاب'),('کیهان، زادگاه الفبای هستی؛ مول، نور و طیف نشری؛ ص۱۶–۲۳',16,23,1,'مطالعهٔ متن، مثال‌ها و خود را بیازمایید')],chem_all='کیهان، زادگاه الفبای هستی؛ ص۱–۲۳؛ تا پایان نشر نور و طیف نشری'),
11:dict(label='یازدهم',bio=[('تنظیم عصبی؛ یاخته‌های بافت عصبی؛ ص۱–۸',1,8,1,'مرور متن، شکل‌ها و قیدهای کتاب'),('تنظیم عصبی؛ ساختار دستگاه عصبی؛ ص۹–۱۸',9,18,1,'مرور متن، شکل‌ها و مقایسه‌ها'),('حواس؛ گیرنده‌های حسی و بینایی؛ ص۱۹–۲۸؛ قبل از شنوایی و تعادل',19,28,2,'مطالعهٔ متن و شکل‌ها؛ مقایسهٔ بخش‌های چشم')],math='هندسهٔ تحلیلی و جبر + ترسیم‌های هندسی؛ ص۱–۱۸ و ۲۵–۳۰',math_ranges=[[1,18],[25,30]],math_hints=['هندسهٔ تحلیلی و معادلهٔ درجه۲','ترسیم‌های هندسی'],physics='الکتریسیتهٔ ساکن؛ ص۱–۲۱؛ قبل از پتانسیل الکتریکی',physics_end=21,physics_hints=['قانون کولن و میدان الکتریکی','برهم‌نهی میدان و انرژی پتانسیل'],chem=[('قدر هدایای زمینی را بدانیم؛ عنصرها و روندهای تناوبی؛ ص۱–۱۴',1,14,1,'مرور متن، شکل‌ها و روندهای تناوبی'),('قدر هدایای زمینی را بدانیم؛ فلزها، استخراج و محاسبات واکنش؛ ص۱۵–۲۴؛ قبل از خود را بیازمایید ص۲۴',15,24,2,'مطالعه و تثبیت مثال‌ها؛ درصد خلوص و بازده')],chem_all='قدر هدایای زمینی را بدانیم؛ ص۱–۲۴؛ قبل از خود را بیازمایید ص۲۴')}

def build(grade):
 s=S[grade];label=s['label'];sub=lambda x:x+(' '+label if x!='ریاضی' else '')
 def box(subject,topic,detail,hours,tests=0,ranges=None,kind='study',preference=None):
  b=dict(subject=sub(subject),topic=topic,detail=detail,hours=hours,tests=tests,kind=kind,ranges=ranges or [])
  if preference:b['preference']='* ترجیحاً: '+preference
  return b
 bio=[]
 for topic,a,b,h,detail in s['bio']:
  bio.append([box('زیست',topic,detail,h,ranges=[[a,b]],kind='review' if detail.startswith('مرور') else 'study'),box('زیست',topic,'۲۰ تست آموزشی + تحلیل همهٔ گزینه‌ها',2,20,[[a,b]],'test')])
 math=[box('ریاضی',s['math'],'۲ ساعت درسنامه و مثال؛ مرور مباحث قبلی و مطالعهٔ بخش جدید',2,ranges=s['math_ranges'])]
 physics=[box('فیزیک',s['physics'],'۲ ساعت درسنامه و مثال؛ مرور مباحث قبلی و مطالعهٔ بخش جدید',2,ranges=[[1,s['physics_end']]])]
 for i in range(2):
  detail='۳۰ تست '+('غیرزمان‌دار' if i==0 else 'ترجیحاً زمان‌دار')+' + تحلیل'
  math.append(box('ریاضی',s['math'],detail,2,30,s['math_ranges'],'test',s['math_hints'][i]))
  physics.append(box('فیزیک',s['physics'],detail,2,30,[[1,s['physics_end']]],'test',s['physics_hints'][i]))
 chem=[]
 for topic,a,b,h,detail in s['chem']:chem.append(box('شیمی',topic,detail,h,ranges=[[a,b]],kind='review' if detail.startswith('مرور') else 'study'))
 ctest1=box('شیمی',s['chem'][0][0],'۲۵ تست مرتبط + تحلیل کامل',2,25,[[s['chem'][0][1],s['chem'][0][2]]],'test')
 ctest2=box('شیمی',s['chem_all'],'۲۵ تست ترکیبی + تحلیل و ثبت خطا',2,25,[[1,s['chem'][1][2]]],'test')
 final=dict(subject='دروس نهایی',topic='مطالعه دروس نهایی',detail='مرور متن و تمرین تشریحی',hours=2,tests=0,kind='finals',ranges=[])
 boxes=[ [bio[0][0],math[0],bio[0][1]], [chem[0],physics[0],ctest1,copy.deepcopy(final)], [bio[1][0],math[1],bio[1][1]], [physics[1],chem[1],copy.deepcopy(final)], [bio[2][0],math[2],bio[2][1]], [physics[2],ctest2] ]
 names=['شنبه','یکشنبه','دوشنبه','سه‌شنبه','چهارشنبه','پنجشنبه']
 days=[dict(day=i,week=1,name=names[i],date=fa(i+2)+' آبان',iso=f'1405-08-{i+2:02}',boxes=b,hours=sum(x['hours'] for x in b),tests=sum(x['tests'] for x in b)) for i,b in enumerate(boxes)]
 return dict(id=f'g{grade}-1405-08-15-week1',title=f'نمونهٔ هفتهٔ اول آزمون ۱۵ آبان ۱۴۰۵ — {label} تجربی',grade=grade,kind='one-week-sample',target='1405-08-15',start='1405-08-02',end='1405-08-08',weeks=1,pages=2,preserved=False,special=False,week_meta=[dict(label=label,date_range='۲ تا ۸ آبان ۱۴۰۵',friday='۸ آبان',official_exam=False)],days=days,scope=dict(bio=[[1,s['bio'][-1][2]]],math=s['math_ranges'],physics=[[1,s['physics_end']]],chem=[[1,s['chem'][1][2]]]),hours=sum(d['hours'] for d in days),tests=sum(d['tests'] for d in days),directory=f'دهم و یازدهم/{label}/۰۲ - آبان/۱۵ آبان',stem=f'نمونه هفته اول آزمون ۱۵ آبان ۱۴۰۵ - {label}')
if __name__=='__main__':
 samples=[build(g) for g in [10,11]]
 for s in samples:save(BASE/'data'/(s['id']+'.json'),s)
 save(BASE/'samples.json',[{k:s[k] for k in ['id','grade','hours','tests','pages','directory','stem']} for s in samples])
 print([(s['grade'],s['hours'],s['tests'],[d['hours'] for d in s['days']]) for s in samples])
