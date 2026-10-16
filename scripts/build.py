from bs4 import BeautifulSoup as Soup
from pathlib import Path
import json
fa=lambda x:str(x).translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹'))
def box(subject,topic,detail,hours,tests=0):return dict(subject=subject,topic=topic,detail=detail,hours=hours,tests=tests)
bios=[['نوکلئیک‌اسیدها؛ فصل ۱، گفتار ۱؛ ص ۱–۸','همانندسازی دنا؛ فصل ۱، گفتار ۲؛ ص ۹–۱۴','پروتئین‌ها؛ فصل ۱، گفتار ۳؛ ص ۱۵–۲۰'],['جذب و تنظیم گوارش + تنوع گوارش؛ فصل ۲، گفتارهای ۲ و ۳؛ ص ۲۵–۳۲','سازوکار تنفس + تهویهٔ ششی؛ فصل ۳، گفتارهای ۱ و ۲؛ ص ۳۳–۴۴','تنوع تبادلات گازی؛ فصل ۳، گفتار ۳؛ ص ۴۵–۴۶']]
maths=[['تابع؛ مفهوم، دامنه و برد، انواع، اعمال جبری، یکنوایی، ترکیب و وارون','تابع؛ مفهوم، دامنه و برد، انواع و اعمال جبری','تابع؛ چندجمله‌ای و یکنوایی','تابع؛ ترکیب و تبدیل نمودار','تابع؛ یک‌به‌یک و وارون','تابع؛ آزمونک ترکیبی کل بودجه'],['تابع و معادلهٔ درجهٔ دوم؛ روش‌های حل، سهمی و روابط ریشه‌ها','معادلهٔ درجهٔ دوم؛ روش‌های حل','تابع درجهٔ دوم؛ سهمی و رأس','معادلهٔ درجهٔ دوم؛ دلتا و تعداد ریشه‌ها','معادلهٔ درجهٔ دوم؛ مجموع و حاصل‌ضرب ریشه‌ها','تابع و معادلهٔ درجهٔ دوم؛ ترکیبی']]
physics=[['حرکت بر خط راست؛ مکان، جابه‌جایی، سرعت، شتاب و حرکت با سرعت ثابت؛ ص ۱–۱۵، قبل از شتاب ثابت','مکان، جابه‌جایی و سرعت متوسط','سرعت لحظه‌ای و نمودار مکان–زمان','شتاب متوسط و لحظه‌ای','حرکت با سرعت ثابت و نمودارها','ترکیبی حرکت؛ بدون حرکت با شتاب ثابت'],['ویژگی‌های فیزیکی مواد؛ حالت‌ها، نیروهای بین‌مولکولی، فشار، شناوری و برنولی؛ فصل ۲، ص ۲۳–۵۲','حالت‌های ماده و نیروهای بین‌مولکولی؛ ص ۲۳–۳۲','فشار در شاره‌ها؛ ص ۳۲–۴۰','شناوری و اصل ارشمیدس؛ ص ۴۰–۴۳','شاره در حرکت و اصل برنولی؛ ص ۴۳–۴۷','ترکیبی ویژگی‌های فیزیکی مواد؛ ص ۲۳–۵۲ با تمرین‌های ص ۴۸–۵۲']]
chems=[['مولکول‌ها در خدمت تندرستی؛ ص ۱–۸؛ پاکیزگی، انحلال و صابون','مولکول‌ها در خدمت تندرستی؛ ص ۹–۱۶؛ شوینده‌ها و اسید و باز آرنیوس','مولکول‌ها در خدمت تندرستی؛ ص ۱۷–۲۴ تا قبل از pH؛ رسانایی، یونش و قدرت اسیدی'],['کیهان؛ ص ۱۹–۲۸؛ محاسبات مول، نور، طیف و ساختار اتم','کیهان؛ ص ۲۹–۳۷؛ آرایش الکترونی، ظرفیت و پایداری','کیهان؛ ص ۳۸–۴۶؛ ترکیب‌های یونی و مولکولی و تمرین‌ها']]
days=[]
for week in range(2):
 grade=['دوازدهم','دهم'][week]
 for day in range(6):
  n=day//2;b=[]
  if day%2==0:
   topic=bios[week][n];subject='زیست '+grade
   b=[box(subject,topic,'متن، شکل‌ها و قیدهای کتاب؛ مطالعهٔ دقیق',1),box(subject,topic,'۲۰ تست آموزشی + تحلیل همهٔ گزینه‌ها',2,20),box(subject,topic,'۲۰ تست تکمیلی + تحلیل و ثبت خطاها',2,20)]
   if n==0:b.append(box('ریاضی',maths[week][0],'۱ ساعت درسنامهٔ مبحث؛ مثال‌های اصلی',1))
   for k in ([1] if n==0 else [2*n,2*n+1]):b.append(box('ریاضی',maths[week][k],('غیرزمان‌دار' if n==0 else 'ترجیحاً زمان‌دار')+'؛ ۳۰ تست + تحلیل در همین باکس',2,30))
  else:
   if n==0:b.append(box('فیزیک '+grade,physics[week][0],'۲ ساعت درسنامه و مثال؛ تنها باکس درسنامهٔ فیزیک',2))
   for k in ([1] if n==0 else [2*n,2*n+1]):b.append(box('فیزیک '+grade,physics[week][k],('غیرزمان‌دار' if n==0 else 'ترجیحاً زمان‌دار')+'؛ ۳۰ تست + تحلیل',2,30))
   b.extend([box('شیمی '+grade,chems[week][n],'۱ ساعت متن کتاب، شکل‌ها و خود را بیازمایید',1),box('شیمی '+grade,chems[week][n],'۲۵ تست مرتبط + تحلیل کامل در همین باکس',2,25)])
  # Alternate subjects while preserving lesson-before-test order within each.
  groups={}
  for item in b:groups.setdefault(item['subject'],[]).append(item)
  b=[group[i] for i in range(max(map(len,groups.values()))) for group in groups.values() if i<len(group)]
  days.append(dict(week=week+1,day=day,name=['شنبه','یکشنبه','دوشنبه','سه‌شنبه','چهارشنبه','پنجشنبه'][day],date=fa(18+week*7+day)+' مهر',boxes=b,hours=sum(x['hours'] for x in b),tests=sum(x['tests'] for x in b)))
Path('plan.json').write_text(json.dumps(days,ensure_ascii=False,indent=2))
root=Soup('<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>برنامهٔ آزمون ۱ آبان ۱۴۰۵</title><link rel="stylesheet" href="assets/planner.css"></head><body><nav class="no-print"><strong>برنامهٔ آزمون ۱ آبان ۱۴۰۵</strong> <button onclick="window.print()">چاپ / ذخیره PDF</button><p>۱۸ تا ۳۰ مهر • هفتهٔ اول دوازدهم، هفتهٔ دوم دهم • توضیحات منابع در README</p></nav><main></main></body></html>','html.parser')
for week in range(2):
 for half in range(2):
  src=Soup(Path('templates/'+['first-half.html','second-half.html'][half]).read_text(),'html.parser')
  sheet=src.select_one('#planner-sheet');sheet['id']=f'week-{week+1}-part-{half+1}';sheet['class'].append('sheet');sheet.attrs.pop('style',None)
  header=sheet.select_one('header')
  header.select_one('h1').string='برنامه‌ریزی هفتگی | آزمون ۱ آبان'
  for span in header.select('span'):
   if span.get_text().strip()=='. ——':span.string=fa(week+1)+' ـ '+['دوازدهم','دهم'][week]
   if '____ /' in span.get_text():span.string=['۱۸ تا ۲۴ مهر ۱۴۰۵','۲۵ مهر تا ۱ آبان ۱۴۰۵'][week]
  fields=header.select('div.grid > div')
  for i,value in [(1,'تجربی / '+['دوازدهم','دهم'][week]),(3,'۴۷ ساعت*'),(4,'۴۹۵ تست')]:fields[i].select('span')[-1].string=value
  for j,section in enumerate(sheet.select('section')):
   if j==3:
    section.select_one('span.font-title-md').string='جمعه | '+['۲۴ مهر','۱ آبان'][week]
    section.select_one('span.font-body-sm').string=['آزمون تمرینی هفتهٔ دوازدهم','آزمون ماز ۱ آبان ۱۴۰۵'][week]
    section.select_one('div.flex-1').string='شرکت در آزمون و سپس تحلیل غلط‌ها و نزده‌ها؛ ثبت علت خطا و مباحث نیازمند مرور. ساعت و تعداد سؤال مطابق آزمون ثبت شود؛ باکس مطالعهٔ جدید ندارد.'
    continue
   d=days[week*6+half*3+j]
   section.select_one('span.font-title-md').string=d['name']+' | '+d['date']
   section.select_one('span.font-body-sm').string='اهداف: '+('زیست و ریاضی' if d['day']%2==0 else 'فیزیک و شیمی')
   sums=section.select('span.w-10.h-4');sums[0].string=fa(d['hours']);sums[1].string=fa(d['tests'])
   cells=section.select_one('div.grid').find_all('div',recursive=False)
   for k,cell in enumerate(cells):
    content=cell.select_one('div.flex-1')
    if k<len(d['boxes']):
     b=d['boxes'][k];label=cell.find('span',string='درس و مبحث:');label.string=b['subject'];label['class']=['subject']
     content['class']=['box-content'];content.append(Soup('<strong>'+b['topic']+'</strong><p>'+b['detail']+'</p>','html.parser'))
     blanks=cell.select('span.border-b');blanks[0].string=fa(b['hours']);blanks[1].string=fa(b['tests'])
    # Unused cells retain the original template, including checkbox and blank
    # subject, hours and test fields, for handwritten additions.
  sheet.select_one('footer span').string='* تست زیست: هر باکس ۲ ساعت با تحلیل؛ استراحت و آزمون در جمع ساعت نیست. | '+fa(week*2+half+1)+' / ۴'
  root.main.append(sheet)
Path('index.html').write_text(str(root))
print('Built 4 sheets;',sum(d['tests'] for d in days),'tests;',sum(d['hours'] for d in days),'hours')
