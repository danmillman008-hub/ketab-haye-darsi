"""Canonical editable planner: native fields and boxed totals match the supplied form.
The published PDF is exported from this DOCX, not from a separate HTML layout.
"""
from word_layout import *
import word_layout as w
import branding


def day_header(cell,name,goal,hours=None,tests=None):
 margins(cell,top=.3,bottom=.3,left=1,right=1)
 shade(cell)
 t=local_table(cell,1,[32,93,25,12,3,23,12]);t.rows[0].height=Mm(5)
 text(t.cell(0,0).paragraphs[0],name,8.5,True)
 text(t.cell(0,1).paragraphs[0],goal,8)
 for label_i,box_i,label,value in [(2,3,'مجموع ساعت:',hours),(5,6,'مجموع تست:',tests)]:
  text(t.cell(0,label_i).paragraphs[0],label,8,True)
  box=t.cell(0,box_i);shade(box,'FFFFFF')
  for edge in ['top','bottom','left','right']:border(box,edge,'775A00',4)
  text(box.paragraphs[0],'' if value is None else fa(value),8,True,align='center')
 return t


for sheet in range(4):
 if sheet:
  p=doc.add_paragraph();tight(p)
  p.add_run().add_break(__import__('docx').enum.text.WD_BREAK.PAGE)
 week=sheet//2;half=sheet%2
 branding.planner_header(w,week,half)
 gap(1)
 for day in plan[week*6+half*3:week*6+half*3+3]:
  t=grid(5,3,'Planner Day')
  for ri,row in enumerate(t.rows):
   border(row.cells[0],'left','C59B27');border(row.cells[-1],'right','C59B27')
   if ri in [0,4]:
    for cell in row.cells:border(cell,'top' if ri==0 else 'bottom','C59B27')
  t.rows[0].height=Mm(7)
  head=t.cell(0,0).merge(t.cell(0,2))
  day_header(head,day['name']+' | '+day['date'],
   'اهداف: '+('زیست و ریاضی' if day['day']%2==0 else 'فیزیک و شیمی'),day['hours'],day['tests'])
  for row in [1,3]:
   t.rows[row].height=Mm(31.8 if half==0 else 25.8)
   t.rows[row+1].height=Mm(5.5)
   for col in range(3):
    i=((row-1)//2)*3+col
    fill(t.cell(row,col),t.cell(row+1,col),day['boxes'][i] if i<len(day['boxes']) else None)
  gap(1)
 if half:
  t=grid(3,1,'Planner Exam');t.rows[0].height=Mm(7);t.rows[1].height=Mm(20);t.rows[2].height=Mm(5.5)
  day_header(t.cell(0,0),'جمعه | '+['۲۴ مهر','۱ آبان'][week],
   ['آزمون تمرینی هفتهٔ دوازدهم','آزمون ماز ۱ آبان ۱۴۰۵'][week])
  text(t.cell(1,0).paragraphs[0],'☐ درس، آزمون یا مبحث:',8)
  p=text(t.cell(1,0).add_paragraph(),'شرکت در آزمون و سپس تحلیل غلط‌ها و نزده‌ها؛ ثبت علت خطا و مباحث نیازمند مرور. ساعت و تعداد سؤال مطابق آزمون ثبت شود؛ باکس مطالعهٔ جدید ندارد.',9)
  p.paragraph_format.space_before=Pt(4)
  margins(t.cell(2,0),left=1,right=1)
  ft=local_table(t.cell(2,0),1,[21,32,15,21,32,15,32,32]);ft.rows[0].height=Mm(4.3)
  for label_i,field_i,label in [(0,1,'ساعت مطالعه:'),(3,4,'تعداد تست:'),(6,7,'تراز / درصد آزمون:')]:
   text(ft.cell(0,label_i).paragraphs[0],label,7)
   field(ft.cell(0,field_i))
  border(t.cell(1,0),'bottom','CCCCCC',3);border(t.cell(2,0),'top','CCCCCC',3)
  gap(1)
 text(doc.add_paragraph(),'* تست زیست: هر باکس ۲ ساعت با تحلیل؛ استراحت و آزمون در جمع ساعت نیست. | '+fa(sheet+1)+' / ۴',6.5)
 branding.footer(w)

doc.core_properties.title='برنامهٔ ۱ آبان ۱۴۰۵ — Stitch 14'
doc.core_properties.subject='نسخهٔ مبنا برای PDF؛ متن و جدول قابل‌ویرایش'
save(BASE/'plan-1-aban-1405.docx')
