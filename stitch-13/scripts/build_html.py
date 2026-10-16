from pathlib import Path
from bs4 import BeautifulSoup as Soup
import json
BASE=Path(__file__).resolve().parents[1]
days=json.loads((BASE/'plan.json').read_text())
fa=lambda x:str(x).translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹'))
root=Soup('<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>برنامهٔ آزمون ۱ آبان ۱۴۰۵</title><link rel="stylesheet" href="assets/planner.css"></head><body><nav class="no-print"><strong>برنامهٔ آزمون ۱ آبان ۱۴۰۵</strong> <button onclick="window.print()">چاپ / ذخیره PDF</button><p>۱۸ تا ۳۰ مهر • هفتهٔ اول دوازدهم، هفتهٔ دوم دهم • توضیحات منابع در README</p></nav><main></main></body></html>','html.parser')
for week in range(2):
 for half in range(2):
  src=Soup((BASE / 'templates' / ['planner-first.html','planner-second.html'][half]).read_text(),'html.parser')
  sheet=src.select_one('#planner-sheet');sheet['id']=f'week-{week+1}-part-{half+1}';sheet['class'].append('sheet');sheet.attrs.pop('style',None)
  header=sheet.select_one('header')
  header.select_one('h1').string='برنامه‌ریزی هفتگی | آزمون ۱ آبان'
  for span in header.select('span'):
   if span.get_text().strip()=='. ——':span.string=fa(week+1)+' ـ '+['دوازدهم','دهم'][week]
   if '____ /' in span.get_text():span.string=['۱۸ تا ۲۴ مهر ۱۴۰۵','۲۵ مهر تا ۱ آبان ۱۴۰۵'][week]
  fields=header.select('div.grid > div')
  for i,value in [(1,'تجربی / '+['دوازدهم','دهم'][week]),(3,'۴۱ ساعت*'),(4,'۴۹۵ تست')]:fields[i].select('span')[-1].string=value
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
  sheet.select_one('footer span').string='* تست زیست: هر باکس ۱ ساعت پیشنهادی با تحلیل؛ استراحت و آزمون در جمع ساعت نیست. | '+fa(week*2+half+1)+' / ۴'
  root.main.append(sheet)
(BASE / 'index.html').write_text(str(root))
print('Built 4 sheets;',sum(d['tests'] for d in days),'tests;',sum(d['hours'] for d in days),'hours')
