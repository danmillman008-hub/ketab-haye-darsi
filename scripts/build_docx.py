"""Build a genuinely editable RTL Word companion from the same plan.json as HTML."""
import json
from pathlib import Path
from docx import Document
from docx.shared import Mm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ROW_HEIGHT_RULE, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

fa=lambda x:str(x).translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹'))
plan=json.loads(Path('plan.json').read_text())
doc=Document()
sec=doc.sections[0]
sec.page_width=Mm(210);sec.page_height=Mm(297)
sec.top_margin=sec.bottom_margin=Mm(7)
sec.left_margin=sec.right_margin=Mm(7)
sec.header_distance=sec.footer_distance=Mm(3)
style=doc.styles['Normal']
style.font.name='Tahoma';style.font.size=Pt(9)
style.paragraph_format.space_after=Pt(0)
style.paragraph_format.space_before=Pt(0)
style.paragraph_format.line_spacing=1.1

def el(tag,**attrs):
 e=OxmlElement('w:'+tag)
 for k,v in attrs.items():e.set(qn('w:'+k),str(v))
 return e

def text(p,s='',size=9,bold=False):
 p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
 pp=p._p.get_or_add_pPr();pp.append(el('bidi',val='1'))
 p.paragraph_format.keep_with_next=False
 r=p.add_run(s);r.bold=bold;r.font.size=Pt(size);r.font.name='Tahoma'
 rp=r._r.get_or_add_rPr();rp.append(el('rtl',val='1'));rp.append(el('szCs',val=int(size*2)))
 rp.rFonts.set(qn('w:cs'),'Tahoma')
 if bold:rp.append(el('bCs',val='1'))
 return p

def table():
 t=doc.add_table(rows=3,cols=3)
 t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 t.style='Table Grid'
 for col in t.columns:col.width=Mm(65.3)
 prop=t._tbl.tblPr;prop.append(el('bidiVisual',val='1'))
 margins=el('tblCellMar')
 for edge in ['top','bottom','left','right']:margins.append(el(edge,w='75',type='dxa'))
 prop.append(margins)
 for row in t.rows:
  row._tr.get_or_add_trPr().append(el('cantSplit'))
 return t

def fill(cell,b):
 cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.TOP
 if b:
  text(cell.paragraphs[0],'☐ '+b['subject'],10,True)
  p=text(cell.add_paragraph(),b['topic'],9,True);p.paragraph_format.space_before=Pt(4)
  p=text(cell.add_paragraph(),b['detail'],9);p.paragraph_format.space_before=Pt(5)
  p=text(cell.add_paragraph(),'ساعت: '+fa(b['hours'])+'                 تست: '+fa(b['tests']),8)
  p.paragraph_format.space_before=Pt(8)
 else:
  text(cell.paragraphs[0],'☐ درس و مبحث:',8)
  p=text(cell.add_paragraph(),'');p.paragraph_format.space_after=Pt(38)
  text(cell.add_paragraph(),'ساعت: ..............           تست: ..............',8)

for sheet in range(4):
 if sheet:doc.add_page_break()
 week=sheet//2;half=sheet%2
 text(doc.add_paragraph(),'برنامه‌ریزی هفتگی | آزمون ۱ آبان ۱۴۰۵',16,True)
 text(doc.add_paragraph(),'هفتهٔ '+fa(week+1)+' — '+['دوازدهم','دهم'][week]+'     |     '+['۱۸ تا ۲۴ مهر ۱۴۰۵','۲۵ مهر تا ۱ آبان ۱۴۰۵'][week],10,True)
 p=text(doc.add_paragraph(),'نام داوطلب: ................  مشاور: ................  رشته: تجربی  هدف: ۴۱ ساعت* / ۴۹۵ تست',8)
 p.paragraph_format.space_after=Pt(5)
 for day in plan[week*6+half*3:week*6+half*3+3]:
  t=table();head=t.rows[0].cells[0].merge(t.rows[0].cells[2]);head._tc.get_or_add_tcPr().append(el('shd',fill='EEEEEA'))
  text(head.paragraphs[0],day['name']+' | '+day['date']+'    —    '+('زیست و ریاضی' if day['day']%2==0 else 'فیزیک و شیمی')+'     مجموع ساعت: '+fa(day['hours'])+'   مجموع تست: '+fa(day['tests']),9,True)
  for row_index in [1,2]:
   row=t.rows[row_index];row.height=Mm(34 if half==0 else 29);row.height_rule=WD_ROW_HEIGHT_RULE.AT_LEAST
   for col in range(3):
    i=(row_index-1)*3+col
    fill(row.cells[col],day['boxes'][i] if i<len(day['boxes']) else None)
  spacer=doc.add_paragraph();spacer.paragraph_format.line_spacing=Pt(3);spacer.paragraph_format.space_after=Pt(0)
 if half:
  t=doc.add_table(rows=2,cols=1);t.style='Table Grid'
  t.rows[0].cells[0]._tc.get_or_add_tcPr().append(el('shd',fill='EEEEEA'))
  text(t.cell(0,0).paragraphs[0],'جمعه | '+['۲۴ مهر — آزمون تمرینی دوازدهم','۱ آبان — آزمون ماز'][week],10,True)
  text(t.cell(1,0).paragraphs[0],'شرکت در آزمون و تحلیل غلط‌ها و نزده‌ها؛ ثبت علت خطا و مباحث نیازمند مرور. ساعت و تعداد سؤال مطابق آزمون ثبت شود.',9)
  text(t.cell(1,0).add_paragraph(),'ساعت: ..............    تعداد سؤال: ..............    تراز / درصد: ..............',8)
 text(doc.add_paragraph(),'* تست زیست: هر باکس ۱ ساعت پیشنهادی با تحلیل؛ استراحت و آزمون در جمع ساعت نیست.',7)
text(sec.footer.paragraphs[0],'برنامهٔ ۱ آبان ۱۴۰۵ • نسخهٔ قابل‌ویرایش • برای چاپ با صفحه‌بندی ثابت از PDF استفاده کنید.',7)
doc.core_properties.title='برنامهٔ آزمون ۱ آبان ۱۴۰۵'
doc.core_properties.subject='برنامهٔ دو هفته‌ای ماز؛ فیزیک دهم با منبع اصلاح‌شده'
doc.save('plan-1-aban-1405.docx')
print('Saved editable DOCX: 4 designed sheets, 72 study cells, 18 blank cells.')
