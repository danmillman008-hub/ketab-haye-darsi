"""Native editable report forms: fixed card/field geometry, not space/dot padding.

Only the two student-report outputs are written. Planner generation is untouched.
"""
import importlib
import branding
import word_layout as w
from docx.shared import Mm, Pt, RGBColor
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ROW_HEIGHT_RULE, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml.ns import qn

GOLD='D1A843';EDGE='C59B27';GREY='D1D5DB';MUTED='6B7280'


def tight(p):
 p.paragraph_format.space_before=p.paragraph_format.space_after=Pt(0)
 p.paragraph_format.line_spacing=Pt(1)
 for r in p.runs:r.font.size=Pt(1)


def paint(p,color):
 for r in p.runs:r.font.color.rgb=RGBColor.from_string(color)
 return p


def underline(p,kind='dotted',color='9CA3AF'):
 pr=p._p.get_or_add_pPr()
 old=pr.find(qn('w:pBdr'))
 if old is not None:pr.remove(old)
 bs=w.el('pBdr');bs.append(w.el('bottom',val=kind,sz=3,space=1,color=color));pr.append(bs)


def local_table(cell,rows,widths):
 return w.local_table(cell,rows,widths)


def blank(cell):
 # A real empty paragraph with a dotted border, rather than a run of periods.
 p=w.text(cell.paragraphs[0],'',7.5)
 underline(p)
 return p


def card(cell,title,optional,short):
 if optional:w.shade(cell,'F9FAFB')
 # The outer cells are 49.5 mm; 2 mm inset per side mirrors source px-2/py-2.5.
 pr=cell._tc.get_or_add_tcPr();m=w.el('tcMar')
 for edge,value in [('top',65),('bottom',65),('left',85),('right',85)]:m.append(w.el(edge,w=value,type='dxa'))
 pr.append(m)
 t=local_table(cell,4,[9,10,9,17.5])
 heights=[5,8.8,8.8,7.4] if not short else [4.5,6.7,6.7,6.1]
 for row,h in zip(t.rows,heights):row.height=Mm(h)
 if optional:
  label=t.cell(0,0).merge(t.cell(0,1));field=t.cell(0,2).merge(t.cell(0,3))
  p=paint(w.text(label.paragraphs[0],'درس اختیاری:',7.5,True),MUTED)
  blank(field);underline(p,'single',GREY)
 else:
  c=t.cell(0,0).merge(t.cell(0,3))
  underline(w.text(c.paragraphs[0],title,8.5,True),'single',GREY)
 for i,label in [(1,'مبحث:'),(2,'زمان:')]:
  paint(w.text(t.cell(i,0).paragraphs[0],label,7.5),MUTED)
  blank(t.cell(i,1).merge(t.cell(i,3)))
 paint(w.text(t.cell(3,0).paragraphs[0],'تست:',7.5),MUTED)
 blank(t.cell(3,1).merge(t.cell(3,2)))
 # Separate native correct/wrong entry fields; no padding-sensitive dot strings.
 stats=t.cell(3,3)
 w.margins(stats)
 st=w.local_table(stats,1,[1.25,3.75,3.75,3.75,3.75,1.25]);st.rows[0].height=Mm(4.5)
 for col,label in [(0,'('),(1,'ص:'),(3,'غ:'),(5,')')]:paint(w.text(st.cell(0,col).paragraphs[0],label,6),MUTED)
 for col in [2,4]:blank(st.cell(0,col))


for part in [1,2]:
 if part==2:w=importlib.reload(w)
 doc=w.doc;sec=doc.sections[0]
 sec.left_margin=sec.right_margin=Mm(6)
 sec.top_margin=sec.bottom_margin=Mm(6)
 for name in ['Report Header','Report Metadata','Report Day','Report Friday']:
  doc.styles.add_style(name,WD_STYLE_TYPE.TABLE)
 # Header date and week are side-by-side, as in the original ZIP.
 h=branding.header(w,'Report Header','گزارش کار و پایش تست هفتگی داوطلب',
  '' if part==1 else '(برگ ۲: سه‌شنبه تا جمعه)',
  'هفته: ..............','تاریخ: .... / .... / ۱۴۰....')
 w.gap(1.5)
 meta=w.grid(1,8,'Report Metadata',[21,28.5]*3+[29,20.5]);meta.rows[0].height=Mm(8)
 for c in meta.rows[0].cells:
  w.shade(c,'F9FAFB');c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
  for edge in ['left','right']:w.border(c,edge,val='nil')
  for edge in ['top','bottom']:w.border(c,edge,GREY,3)
 for j,label in enumerate(['نام داوطلب:','رشته / پایه:','مشاور ناظر:','هدف ساعت / تست:']):
  paint(w.text(meta.cell(0,j*2).paragraphs[0],label,7.5,True),MUTED)
  blank(meta.cell(0,j*2+1))
 w.gap(3)

 def day(name,friday=False):
  t=w.grid(2 if friday else 3,4,'Report Friday' if friday else 'Report Day',[49.5]*4)
  t.rows[0].height=Mm(6)
  daycell=t.cell(0,0);rating=t.cell(0,1).merge(t.cell(0,3))
  for c in [daycell,rating]:
   w.shade(c,'B88D1D' if friday else GOLD)
   c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
  w.text(daycell.paragraphs[0],name,9,True)
  w.margins(rating,left=1,right=1)
  rt=w.local_table(rating,1,[50.5,21,15,15,17,28]);rt.rows[0].height=Mm(4.7)
  for j,label in enumerate(['','میزان رضایت:','○ عالی','○ خوب','○ متوسط','○ نیاز به بازنگری']):
   w.text(rt.cell(0,j).paragraphs[0],label,7,align='start')
  for ri in range(1,len(t.rows)):
   t.rows[ri].height=Mm(34.5 if part==1 else 27.5)
   for j,c in enumerate(t.rows[ri].cells):
    optional=(ri==2 or friday)
    card(c,'درس اختیاری:' if optional else ['زیست‌شناسی','فیزیک','شیمی','ریاضی'][j],optional,part==2)
  # Gold outside, grey column dividers and a single separator between card rows.
  for ri,row in enumerate(t.rows):
   seen=set()
   for ci,c in enumerate(row.cells):
    if id(c._tc) in seen:continue
    seen.add(id(c._tc))
    for edge in ['top','bottom','left','right']:w.border(c,edge,GREY,3)
    if ri==0:
     for edge in ['top','left','right']:w.border(c,edge,GOLD,3)
    if ri==len(t.rows)-1:w.border(c,'bottom',EDGE,8)
   w.border(row.cells[0],'left',EDGE,8)
   w.border(row.cells[-1],'right',EDGE,8)
  w.gap(3 if not friday else 2)
 for name in (['شنبه','یکشنبه','دوشنبه'] if part==1 else ['سه‌شنبه','چهارشنبه','پنج‌شنبه']):day(name)
 if part==2:day('جمعه (آزمون، تحلیل و جبرانی)',True)
 # Both Stitch14 forms now carry institute and social branding.
 branding.footer(w,report=True,part=part)
 doc.core_properties.title='گزارش دانش‌آموز — برگ '+w.fa(part)
 w.save(w.BASE/f'student-report-{part}.docx')
 print('Built report',part,'with native blank writing fields')
