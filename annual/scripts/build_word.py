"""Parameterized annual planner, reusing the approved native Stitch14 geometry."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
# Reuse the approved layout engine and embedded fonts, never overwrite its data.
sys.path.insert(0,str(ROOT/'stitch-14/scripts'))
from word_layout import *
import word_layout as w
import branding
meta=json.loads((ROOT/'annual/data'/(sys.argv[1]+'.json')).read_text())
assert not meta['preserved']
plan=meta['days'];w.plan=plan
# The original header geometry is unchanged; replace only its fixed labels with data.
src=(ROOT/'stitch-14/scripts/branding.py').read_text()
src=src.replace("['دوازدهم','دهم'][week]","w.annual_meta['week_meta'][week]['label']")
src=src.replace("['۱۸ تا ۲۴ مهر ۱۴۰۵','۲۵ مهر تا ۱ آبان ۱۴۰۵'][week]","w.annual_meta['week_meta'][week]['date_range']")
src=src.replace("'برنامه‌ریزی هفتگی',12,True","('فایل برآیندی' if w.annual_meta['special'] else 'برنامه‌ریزی هفتگی'),12,True")
exec(compile(src,'annual_branding','exec'),branding.__dict__)
w.annual_meta=meta

def day_header(cell,name,goal,hours=None,tests=None):
 margins(cell,top=.3,bottom=.3,left=1,right=1);shade(cell)
 t=local_table(cell,1,[32,93,25,12,3,23,12]);t.rows[0].height=Mm(5)
 text(t.cell(0,0).paragraphs[0],name,8.5,True);text(t.cell(0,1).paragraphs[0],goal,8)
 for label_i,box_i,label,value in [(2,3,'مجموع ساعت:',hours),(5,6,'مجموع تست:',tests)]:
  text(t.cell(0,label_i).paragraphs[0],label,8,True)
  box=t.cell(0,box_i);shade(box,'FFFFFF')
  for edge in ['top','bottom','left','right']:border(box,edge,'775A00',4)
  text(box.paragraphs[0],'' if value is None else fa(value),8,True,align='center')
 return t

for sheet in range(meta['weeks']*2):
 if sheet:
  p=doc.add_paragraph();tight(p);p.add_run().add_break(__import__('docx').enum.text.WD_BREAK.PAGE)
 week=sheet//2;half=sheet%2
 branding.planner_header(w,week,half);gap(1)
 for day in plan[week*6+half*3:week*6+half*3+3]:
  t=grid(5,3,'Planner Day')
  for ri,row in enumerate(t.rows):
   border(row.cells[0],'left','C59B27');border(row.cells[-1],'right','C59B27')
   if ri in [0,4]:
    for cell in row.cells:border(cell,'top' if ri==0 else 'bottom','C59B27')
  t.rows[0].height=Mm(7)
  head=t.cell(0,0).merge(t.cell(0,2))
  day_header(head,day['name']+' | '+day['date'],'اهداف: '+('زیست و ریاضی' if day['day']%2==0 else 'فیزیک و شیمی'),day['hours'],day['tests'])
  for row in [1,3]:
   t.rows[row].height=Mm(31.8 if half==0 else 25.8)
   t.rows[row+1].height=Mm(5.5)
   for col in range(3):
    i=((row-1)//2)*3+col
    fill(t.cell(row,col),t.cell(row+1,col),day['boxes'][i] if i<len(day['boxes']) else None)
  gap(1)
 if half:
  t=grid(3,1,'Planner Exam');t.rows[0].height=Mm(7);t.rows[1].height=Mm(20);t.rows[2].height=Mm(5.5)
  final=week==meta['weeks']-1
  day_header(t.cell(0,0),'جمعه | '+meta['week_meta'][week]['friday'],'آزمون' if final else 'آزمون تمرینی')
  text(t.cell(1,0).paragraphs[0],'☐ درس، آزمون یا مبحث:',8)
  p=text(t.cell(1,0).add_paragraph(),'شرکت در آزمون و تحلیل غلط‌ها و نزده‌ها؛ ثبت علت خطا و مباحث نیازمند مرور.',9);p.paragraph_format.space_before=Pt(4)
  margins(t.cell(2,0),left=1,right=1)
  ft=local_table(t.cell(2,0),1,[21,32,15,21,32,15,32,32]);ft.rows[0].height=Mm(4.3)
  for label_i,field_i,label in [(0,1,'ساعت مطالعه:'),(3,4,'تعداد تست:'),(6,7,'تراز / درصد آزمون:')]:
   text(ft.cell(0,label_i).paragraphs[0],label,7);field(ft.cell(0,field_i))
  border(t.cell(1,0),'bottom','CCCCCC',3);border(t.cell(2,0),'top','CCCCCC',3);gap(1)
 foot='تست زیست: هر باکس ۲ ساعت با تحلیل؛ استراحت و آزمون در جمع ساعت نیست. | '+fa(sheet+1)+' / '+fa(meta['weeks']*2)
 text(doc.add_paragraph(),foot,6)
 branding.footer(w)
doc.core_properties.title=meta['title']+(' — فایل برآیندی' if meta['special'] else '')
doc.core_properties.subject='برنامهٔ مطالعاتی'
output=ROOT/'.work/annual/docx';output.mkdir(parents=True,exist_ok=True)
save(output/(meta['id']+'.docx'))
print('Built',meta['id'],meta['pages'],'expected pages')
