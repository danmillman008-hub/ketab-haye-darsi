"""Publish Persian-named folders, preserving versioned source outputs.
Usage: .venv/bin/python scripts/organize_deliverables.py <fresh-Word-render-directory>
Render the latest Stitch14 DOCXs first with its render_word.mjs script.
"""
import json, shutil, sys, zipfile
from pathlib import Path
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
calendar=json.loads((ROOT/'docs/maz-calendar.json').read_text())
rendered=Path(sys.argv[1]).resolve()
source=ROOT/calendar['completed_plan_source']
fa=lambda s:str(s).translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹'))
plans=ROOT/'برنامه تحصیلی'
reports=ROOT/'گزارش دانش آموز'

# Validate all report sources before publishing anything.
for part in [1,2]:
 with pymupdf.open(rendered/f'student-report-{part}.pdf') as pdf:
  assert len(pdf)==1
  text=pdf[0].get_text()
  assert text.count('مبحث')==(24 if part==1 else 28)
  assert text.count('○')==(12 if part==1 else 16)
  assert len(pdf[0].get_image_info())==3
 assert (source/f'student-report-{part}.docx').is_file()

plans.mkdir(exist_ok=True);reports.mkdir(exist_ok=True)
completed=None
calendar_rows=[]
for month in calendar['months']:
 y,m,name=month['year'],month['month'],month['name']
 folder=plans/month['folder']
 folder.mkdir(exist_ok=True)
 for day in month['days']:
  exam=folder/f'{fa(day)} {name}'
  exam.mkdir(exist_ok=True)
  if f'{y}-{m:02}-{day:02}'==calendar['completed_exam']:
   completed=exam
  elif not any(exam.iterdir()):
   (exam/'.gitkeep').touch() # Git does not store empty folders.
 if not month['days'] and not any(folder.iterdir()):(folder/'.gitkeep').touch()
 days_text='، '.join(fa(d) for d in month['days']) or 'تاریخ اعلام‌شده در منبع ندارد'
 page_text=fa(month['source_page']) if month['source_page'] else '—'
 calendar_rows.append(f'| {name} {fa(y)} | {days_text} | {page_text} |')
for item in calendar['undated']:
 folder=plans/'تاریخ اعلام‌نشده'/item['name']
 folder.mkdir(parents=True,exist_ok=True)
 if not any(folder.iterdir()):(folder/'.gitkeep').touch()
assert completed is not None
for suffix in ['pdf','docx']:
 shutil.copyfile(source/f'plan-1-aban-1405.{suffix}',completed/f'برنامه آزمون ۰۱ آبان ۱۴۰۵.{suffix}')
for part in [1,2]:
 stem=f'گزارش دانش آموز - برگ {fa(part)} - '+('شنبه تا دوشنبه' if part==1 else 'سه‌شنبه تا جمعه')
 shutil.copyfile(source/f'student-report-{part}.docx',reports/(stem+'.docx'))
 shutil.copyfile(rendered/f'student-report-{part}.pdf',reports/(stem+'.pdf'))

(plans/'README.md').write_text('''# برنامه تحصیلی — تقویم آزمون‌های ماز ۱۴۰۵–۱۴۰۶

پوشه‌ها بر اساس **ماه آزمون** دسته‌بندی شده‌اند. ترتیب پوشه‌ها از مهر تا شهریور است: مهر، آبان، آذر، دی، بهمن، اسفند، فروردین، اردیبهشت، خرداد، تیر، مرداد، شهریور. پیشوندهای «۰۱» تا «۱۲» برای حفظ همین ترتیب در مرتب‌سازی بر اساس نام در GitHub و فایل ZIP هستند، نه شمارهٔ ماه تقویم. زیرپوشه‌ها به شکل «۱ آبان» هستند. سال تحصیلی در همین راهنما ثبت است. این تقویم از نسخهٔ ارسالی ماز، ویژهٔ دوازدهم تجربی با شروع مهر، استخراج و با تصاویر صفحات ۵ تا ۷ تطبیق داده شده است؛ تقویم تازهٔ وب جایگزین منبع ارسالی نشده است.

## برنامهٔ آماده

[پوشهٔ آزمون ۱ آبان ۱۴۰۵](<۰۲ - آبان/۱ آبان/>) شامل PDF چهارصفحه‌ای و Word قابل‌ویرایش نسخهٔ نهایی Stitch14 است. روزهای مطالعهٔ آن ۱۸ تا ۳۰ مهر و آزمون هدف آن ۱ آبان است؛ بنابراین در ماه **آبان** قرار گرفته است. محتوا و قالب برنامه تغییر نکرده‌اند.

بقیهٔ پوشه‌ها فعلاً برای برنامه‌های بعدی آماده‌اند و برنامهٔ تحصیلی داخلشان تولید نشده است. فایل مخفی `.gitkeep` فقط برای حفظ پوشه‌های خالی در GitHub است. دو آزمون پریمیوم، طبق منبع هنوز تاریخ اعلام‌شده ندارند و در «تاریخ اعلام‌نشده» قرار دارند؛ تاریخ فرضی برایشان تعیین نشده است.

پوشه‌های مرداد و شهریور به درخواست کاربر ایجاد شده‌اند؛ در منبع فعلی تاریخی برای آزمون‌های این دو ماه درج نشده و داخلشان فعلاً خالی است.

## تاریخ‌های منبع

| ماه | روز آزمون | صفحهٔ PDF منبع |
|---|---|---|
'''+ '\n'.join(calendar_rows)+'''

در مجموع **۱۹ آزمون تاریخ‌دار و ۲ آزمون پریمیوم بدون تاریخ** ثبت شده است. آبان سه آزمون دارد: ۱، ۱۵ و ۲۹ آبان. نخستین آزمون این تقویم ۱۷ مهر است، نه ۱ مهر.

گزارش‌های خالی دانش‌آموز در پوشهٔ مستقل [گزارش دانش آموز](<../گزارش دانش آموز/>) قرار دارند: دو برگ، هر برگ PDF و DOCX (چهار فایل).

منبع: فایل `nnn1pTQT401yrhukz2t0zJLr3KNuRZVJwGoorjHP.pdf` در Drive با شناسهٔ `1NLhRx-u-d3I2DiOGixzBNDsyqF_PFkZS`. فهرست ماشینی و اثرانگشت منبع در `docs/maz-calendar.json` مخزن است. فایل کامل بودجه‌بندی و کتاب‌های درسی در Git منتشر نشده‌اند. پوشه‌های نسخه‌های قبلی برای بازتولید و حفظ تاریخچه باقی مانده‌اند.
''')

# Verify academic-year order as well as exact month and exam folder names.
assert {p.name for p in plans.iterdir() if p.is_dir()} == {m['folder'] for m in calendar['months']} | {'تاریخ اعلام‌نشده'}
assert [m['name'] for m in calendar['months']]==['مهر','آبان','آذر','دی','بهمن','اسفند','فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور']
assert sorted(m['folder'] for m in calendar['months'])==[m['folder'] for m in calendar['months']]
for month in calendar['months']:
 assert {p.name for p in (plans/month['folder']).iterdir() if p.is_dir()} == {f"{fa(day)} {month['name']}" for day in month['days']}

with zipfile.ZipFile(ROOT/'organized-deliverables.zip','w',zipfile.ZIP_DEFLATED) as z:
 for top in [plans,reports]:
  # Explicit directory entries preserve empty exam folders in the download.
  for p in [top]+sorted(top.rglob('*')):
   if p.name=='.gitkeep':continue
   z.write(p,p.relative_to(ROOT))

# Verify copied files and ZIP's UTF-8 Persian paths.
assert len(list(reports.glob('*.pdf')))==len(list(reports.glob('*.docx')))==2
for suffix in ['pdf','docx']:
 assert (completed/f'برنامه آزمون ۰۱ آبان ۱۴۰۵.{suffix}').read_bytes()==(source/f'plan-1-aban-1405.{suffix}').read_bytes()
with zipfile.ZipFile(ROOT/'organized-deliverables.zip') as z:
 assert z.testzip() is None
 for p in [*plans.rglob('*'),*reports.rglob('*')]:
  if p.name=='.gitkeep':continue
  key=p.relative_to(ROOT).as_posix()+('/' if p.is_dir() else '')
  assert key in z.namelist(),key
  if p.is_file():assert z.read(key)==p.read_bytes()
print('PASS: 12 ordered months (Mehr to Shahrivar), 19 dated + 2 undated exam folders; unchanged planner PDF/DOCX; two one-page report PDFs and two editable DOCXs; UTF-8 ZIP verified.')
