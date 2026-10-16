from word_layout import *

for sheet in range(4):
 if sheet:
  p=doc.add_paragraph();p.paragraph_format.line_spacing=Pt(1)
  p.add_run().add_break(__import__('docx').enum.text.WD_BREAK.PAGE)
 week=sheet//2;half=sheet%2
 h=grid(2,2,'Planner Header',[125,77]);h.rows[0].height=Mm(8);h.rows[1].height=Mm(5)
 for c in h.rows[0].cells:
  for edge in ['top','left','right']:border(c,edge,val='nil')
 text(h.cell(0,0).paragraphs[0],'برنامه‌ریزی هفتگی | آزمون ۱ آبان',14,True)
 text(h.cell(0,1).paragraphs[0],'هفته: '+fa(week+1)+' ـ '+['دوازدهم','دهم'][week]+' | '+['۱۸ تا ۲۴ مهر ۱۴۰۵','۲۵ مهر تا ۱ آبان ۱۴۰۵'][week],8)
 meta=h.cell(1,0).merge(h.cell(1,1))
 for edge in ['left','right']:border(meta,edge,val='nil')
 text(meta.paragraphs[0],'نام داوطلب: ................    رشته / پایه: تجربی / '+['دوازدهم','دهم'][week]+'    مشاور: ................    هدف ساعت: ۴۱*    هدف تست: ۴۹۵',8)
 gap(1)
 for day in plan[week*6+half*3:week*6+half*3+3]:
  t=grid(5,3,'Planner Day')
  for ri,row in enumerate(t.rows):
   border(row.cells[0],'left','C59B27');border(row.cells[-1],'right','C59B27')
   if ri in [0,4]:
    for cell in row.cells:border(cell,'top' if ri==0 else 'bottom','C59B27')
  t.rows[0].height=Mm(6)
  for c in t.rows[0].cells:shade(c)
  text(t.cell(0,0).paragraphs[0],day['name']+' | '+day['date'],9,True)
  text(t.cell(0,1).paragraphs[0],'اهداف: '+('زیست و ریاضی' if day['day']%2==0 else 'فیزیک و شیمی'),8)
  text(t.cell(0,2).paragraphs[0],'مجموع ساعت: '+fa(day['hours'])+'   مجموع تست: '+fa(day['tests']),8,True)
  for row in [1,3]:
   t.rows[row].height=Mm(35.5 if half==0 else 29.5)
   t.rows[row+1].height=Mm(4.5)
   for col in range(3):
    i=((row-1)//2)*3+col
    fill(t.cell(row,col),t.cell(row+1,col),day['boxes'][i] if i<len(day['boxes']) else None)
  gap(1)
 if half:
  t=grid(3,1,'Planner Exam');t.rows[0].height=Mm(6);t.rows[1].height=Mm(17);t.rows[2].height=Mm(5)
  shade(t.cell(0,0))
  text(t.cell(0,0).paragraphs[0],'جمعه | '+['۲۴ مهر — آزمون تمرینی هفتهٔ دوازدهم','۱ آبان — آزمون ماز ۱ آبان ۱۴۰۵'][week],9,True)
  text(t.cell(1,0).paragraphs[0],'☐ درس، آزمون یا مبحث:',8)
  text(t.cell(1,0).add_paragraph(),'شرکت در آزمون و سپس تحلیل غلط‌ها و نزده‌ها؛ ثبت علت خطا و مباحث نیازمند مرور. ساعت و تعداد سؤال مطابق آزمون ثبت شود؛ باکس مطالعهٔ جدید ندارد.',9)
  text(t.cell(2,0).paragraphs[0],'ساعت مطالعه: ..............       تعداد تست: ..............       تراز / درصد آزمون: ..............',8)
  border(t.cell(1,0),'bottom','CCCCCC',3);border(t.cell(2,0),'top','CCCCCC',3)
  gap(1)
 text(doc.add_paragraph(),'* تست زیست: هر باکس ۱ ساعت پیشنهادی با تحلیل؛ استراحت و آزمون در جمع ساعت نیست. | '+fa(sheet+1)+' / ۴',7)


doc.core_properties.title='برنامهٔ ۱ آبان ۱۴۰۵ — Stitch 13'
save(BASE/'plan-1-aban-1405.docx')
