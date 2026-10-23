"""Parameterized annual planner, reusing the approved native Stitch14 geometry."""
import sys,json
from pathlib import Path
FOUNDATION=Path(__file__).resolve().parents[1]
ROOT=FOUNDATION.parent
# Reuse the approved layout engine and embedded fonts, never overwrite its data.
sys.path.insert(0,str(ROOT/'stitch-14/scripts'))
from word_layout import *
import word_layout as w
import branding
meta=json.loads((FOUNDATION/'data'/(sys.argv[1]+'.json')).read_text())
assert not meta['preserved']
plan=meta['days'];w.plan=plan
# The original header geometry is unchanged; replace only its fixed labels with data.
src=(ROOT/'stitch-14/scripts/branding.py').read_text()
src=src.replace("['دوازدهم','دهم'][week]","w.annual_meta['week_meta'][week]['label']")
src=src.replace("['۱۸ تا ۲۴ مهر ۱۴۰۵','۲۵ مهر تا ۱ آبان ۱۴۰۵'][week]","w.annual_meta['week_meta'][week]['date_range']")
src=src.replace("'برنامه‌ریزی هفتگی',12,True","('فایل برآیندی' if w.annual_meta['special'] else 'برنامه‌ریزی هفتگی'),12,True")
exec(compile(src,'annual_branding','exec'),branding.__dict__)
w.annual_meta=meta

def day_header(cell,name,goal,hours=None,tests=None,totals=True):
 margins(cell,top=.3,bottom=.3,left=1,right=1);shade(cell)
 t=local_table(cell,1,[32,93,25,12,3,23,12] if totals else [32,120]);t.rows[0].height=Mm(5)
 text(t.cell(0,0).paragraphs[0],name,8.5,True);text(t.cell(0,1).paragraphs[0],goal,8)
 for label_i,box_i,label,value in ([(2,3,'مجموع ساعت:',hours),(5,6,'مجموع تست:',tests)] if totals else []):
  text(t.cell(0,label_i).paragraphs[0],label,8,True)
  box=t.cell(0,box_i);shade(box,'FFFFFF')
  for edge in ['top','bottom','left','right']:border(box,edge,'775A00',4)
  text(box.paragraphs[0],'' if value is None else fa(value),8,True,align='center')
 return t

base_fill=fill
def fill(content,metrics,b):
 if not b:return  # Truly empty unused cells; do not print dummy subjects or zero totals.
 if 'preference' not in b:return base_fill(content,metrics,b)
 from docx.shared import RGBColor
 margins(content,top=.6,bottom=.3,left=1,right=1)
 text(content.paragraphs[0],'☐ '+b['subject'],9,True)
 p=text(content.add_paragraph(),b['topic'],9,True);p.paragraph_format.space_before=Pt(2)
 p=text(content.add_paragraph(),b['detail'],8.5);p.paragraph_format.space_before=Pt(2)
 p=text(content.add_paragraph(),b['preference'],7.5);p.paragraph_format.space_before=Pt(1)
 for run in p.runs:run.font.color.rgb=RGBColor.from_string('707070')
 metric_pair(metrics,b['hours'],b['tests'])
 border(content,'bottom','CCCCCC',3);border(metrics,'top','CCCCCC',3)

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
  fam=[]
  for b in day['boxes']:
   name=b['subject'] if b['subject']=='دروس نهایی' else b['subject'].split()[0]
   if name not in fam:fam.append(name)
  goals='، '.join(fam)
  day_header(head,day['name']+' | '+day['date'],'اهداف: '+goals,day['hours'],day['tests'])
  boxes=day['boxes']
  single_mm=(52 if half==0 else 44) if meta.get('compact_layout') else (31.8 if half==0 else 25.8)
  def place(row,items):
   h=single_mm/2 if (meta.get('compact_layout') and len(boxes)>3) else single_mm
   t.rows[row].height=Mm(h);t.rows[row+1].height=Mm(5.5)
   for idx,b in enumerate(items):
    content=t.cell(row,idx);metrics=t.cell(row+1,idx)
    if idx==len(items)-1 and len(items)<3:
     content=content.merge(t.cell(row,2));metrics=metrics.merge(t.cell(row+1,2))
    fill(content,metrics,b)
  if meta.get('compact_layout'):
   # Annual pages: no empty bordered rows; a trailing box takes the full width.
   if len(boxes)<=3:
    place(1,boxes)
    for r in (t.rows[3],t.rows[4]):t._tbl.remove(r._tr)
   else:
    place(1,boxes[:3]);place(3,boxes[3:])
    if len(boxes)<=4:
     # A lone fourth box spans the width; the freed row can then be removed.
     for r in (t.rows[4],):t._tbl.remove(r._tr)
  else:
   place(1,boxes[:3]);place(3,boxes[3:6])
  gap(1)
 if half:
  final=meta['week_meta'][week]['official_exam']
  compact=meta.get('compact_layout')
  t=grid(3 if not compact else 2,1,'Planner Exam')
  t.rows[0].height=Mm(7);t.rows[1].height=Mm(20)
  if not compact:t.rows[2].height=Mm(5.5)
  day_header(t.cell(0,0),'جمعه | '+meta['week_meta'][week]['friday'],'آزمون' if final else 'خودسنجی هفتگی',totals=not compact)
  body=t.cell(1,0)
  text(body.paragraphs[0],'☐ درس، آزمون یا مبحث:',8)
  hint=('آزمون رسمی از محدودهٔ اعلام‌شده؛ تحلیل غلط‌ها و نزده‌ها' if final else 'خودسنجی از مطالب همین هفته؛ تحلیل غلط‌ها و نزده‌ها و ثبت مباحث نیازمند مرور')
  p=text(body.add_paragraph(),hint,9);p.paragraph_format.space_before=Pt(4)
  if compact:
   # Text-only entry line: no nested table, so nothing can overlap the prompt.
   p=text(body.add_paragraph(),'ساعت مطالعه: ....................    تعداد تست: ....................    تراز یا درصد: ....................',8)
   p.paragraph_format.space_before=Pt(10)
  else:
   margins(body,left=1,right=1)
   ft=local_table(body,1,[21,32,15,21,32,15,32,32]);ft.rows[0].height=Mm(4.3)
   for label_i,field_i,label in [(0,1,'ساعت مطالعه:'),(3,4,'تعداد تست:'),(6,7,'تراز / درصد آزمون:')]:
    text(ft.cell(0,label_i).paragraphs[0],label,7);field(ft.cell(0,field_i))
   border(t.cell(2,0),'top','CCCCCC',3)
  border(body,'bottom','CCCCCC',3)
  gap(1)
 foot='هدف: آزمون '+meta.get('footer_target','')+' | تست ریاضی/فیزیک: انتخاب آزاد در محدودهٔ عنوان | خودسنجی خارج از جمع ساعت | '+fa(sheet+1)+' / '+fa(meta['weeks']*2)
 text(doc.add_paragraph(),foot,6)
 branding.footer(w)
doc.core_properties.title=meta['title']+(' — فایل برآیندی' if meta['special'] else '')
doc.core_properties.subject='برنامهٔ مطالعاتی'
output=ROOT/'.work/foundation/docx';output.mkdir(parents=True,exist_ok=True)
save(output/(meta['id']+'.docx'))
print('Built',meta['id'],meta['pages'],'expected pages')
