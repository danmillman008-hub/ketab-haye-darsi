"""Publish only checked Word/PDF pairs, including the rebuilt 1-Aban pair."""
from pathlib import Path
import json,hashlib,shutil,sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
render=ROOT/sys.argv[1]
manifest=json.loads((ROOT/'annual/manifest.json').read_text())
qa=json.loads((ROOT/'annual/QA.json').read_text())
assert qa['status']=='passed' and qa['independentPixelComparison']
checks={c['id']:c for c in qa['checks']}
curriculum_qa=json.loads((ROOT/'annual/CURRICULUM_QA.json').read_text())
assert curriculum_qa['status']=='passed'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Validate the entire batch before copying any new deliverable.
for e in manifest:
 assert sha(ROOT/'annual/data'/(e['id']+'.json'))==curriculum_qa['data_hashes'][e['id']]
 if e['preserved']:continue
 assert sha(ROOT/'.work/annual/docx'/(e['id']+'.docx'))==checks[e['id']]['docxSha256']
 assert sha(render/(e['id']+'.pdf'))==checks[e['id']]['pdfSha256']
for e in manifest:
 dest=ROOT/e['directory'];dest.mkdir(parents=True,exist_ok=True)
 if not e['preserved']:
  for ext,source in [('docx',ROOT/'.work/annual/docx'),('pdf',render)]:shutil.copyfile(source/(e['id']+'.'+ext),dest/(e['stem']+'.'+ext))
 for ext in ['docx','pdf']:assert (dest/(e['stem']+'.'+ext)).exists()
rows=[]
for e in manifest:
 prefix=Path(e['directory']).relative_to('برنامه تحصیلی')
 links=' / '.join(f'[{ext.upper()}](<{prefix}/{e["stem"]}.{ext}>)' for ext in ['pdf','docx'])
 rows.append(f'| {e["title"]} | {e["weeks"]} | '+('برآیندی؛ بدون تاریخ قطعی' if not e['target'] else 'برآیندی' if e['special'] else 'عادی؛ نسخهٔ تأییدشده' if e['preserved'] else 'عادی')+f' | {links} |')
fa=lambda s:str(s).translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹'))
intro='''# مجموعهٔ برنامه‌های ماز ۱۴۰۵–۱۴۰۶

۱۹ برنامهٔ تاریخ‌دار از ۱۷ مهر تا ۴ تیر؛ برای هر آزمون یک Word قابل‌ویرایش و یک PDF همان Word. برنامه‌های تاریخ‌دار در مجموع ۳۹ هفتهٔ پیوسته از ۴ مهر ۱۴۰۵ تا ۴ تیر ۱۴۰۶ را پوشش می‌دهند. دو برنامهٔ پریمیوم به‌صورت نسبی و **بدون تاریخ قطعی** آماده‌اند؛ پس از اعلام تاریخ و بودجهٔ نهایی باید تطبیق شوند. همهٔ برنامه‌ها، از جمله ۱ آبان، با منابع چاپ ۱۴۰۵ بازسازی شده‌اند.

فرمول هر هفته: **۴۷ ساعت، ۴۹۵ تست، ۲۷ باکس**؛ جفت‌درس‌ها، زمان مطالعه و زمان/تعداد تست‌ها ثابت‌اند. آزمون‌ها و استراحت در مجموع ساعت نیستند. گزارش‌های دانش‌آموز تغییر نکرده‌اند.

**نسخهٔ جاری:** فایل‌های جدول زیر معتبرند. نسخه‌های قبلی فقط در [آرشیو جداگانه](../آرشیو/README.md) نگهداری می‌شوند و داخل بستهٔ دانلود جاری نیستند.

## دریافت فایل‌ها

| آزمون | تعداد هفته | نوع | فایل‌ها |
|---|---:|---|---|
'''
notes='''
## فایل‌های برآیندی و تصمیم‌های خاص

در خود فایل‌های ویژه، صفحهٔ توضیح با عنوان «فایل برآیندی» و نیز همین عنوان روی صفحات برنامه درج شده است. قالب جدول‌های مصوب عوض نشده؛ فقط صفحهٔ توضیح اضافه شده است.

'''
for e in manifest:
 if e['special']:notes+='- **'+e['title']+'**: '+e['reason']+'\n'
notes+='''
## نکات منبع و حدود استفاده

- منابع همان PDF ماز ارسالی (جدول صفحات ۵–۷) و فایل‌های درسی موجود در Drive هستند؛ تاریخ تازه یا آزمون فرضی ساخته نشده است.
- پایه در ردیف ۲۷ آذرِ خود ماز به یازدهم تغییر می‌کند؛ این گذار طبق منبع انجام شده، نه صرفاً با تعویض ماه تقویمی.
- در ۲۱ اسفند، مسیر مجاز «مرور ۵۰درصدی دوازدهم» انتخاب شده است؛ نه مسیر پیشروی صددرصدی.
- **صفحه‌بندی چاپ ۱۴۰۵:** شماره‌ها به صفحات چاپی کتاب‌های جدید ارجاع دارند؛ صفحات مرزی را فقط تا عنوان مشخص‌شده بخوانید. [راهنمای حجم صفحات](راهنمای%20حجم%20صفحات.md) و [جدول قابل‌محاسبه](حجم%20صفحات.csv) همراه مجموعه است. شمار صفحات گسترهٔ بودجه است، نه شمار صفحات حتماً خوانده‌شده در مرور موضوعی.
- در ۱۷ اردیبهشت، بازهٔ عددی فیزیک ماز ۱۰۳–۱۲۵ و عنوان آن «از ساختار هسته» است؛ در کتاب، ساختار هسته ص۱۱۲ آغاز می‌شود. برای حذف‌نشدن بخشی از بازه، ص۱۰۳–۱۱۱ نیز مرور شده و این تصمیم داخل فایل آمده است.
- در برنامه‌های جامع، مطالعهٔ یک‌ساعته به معنای مرور و بازیابی هدفمند است، نه آموزش اولیهٔ همهٔ فصل‌ها. اجرای آن نیازمند مطالعهٔ قبلی است؛ تست‌های تعیین‌شده باید نمایندهٔ همهٔ سرفصل‌ها باشند.
- فقط چهار درسِ فرمول کاربر پوشش داده شده‌اند؛ زمین‌شناسی اضافه نشده است. تعداد سؤال آزمون رسمی، تعداد تست تمرینی برنامه نیست.
- مرداد و شهریور در منبع آزمون تاریخ‌دار ندارند؛ پوشه‌هایشان حفظ شده ولی برنامهٔ فرضی ساخته نشده است.
- PDFها خروجی مستقیم Word هستند. کنترل همهٔ نویسه‌ها، صفحه‌بندی و تطابق تصویری رندر مستقل انجام شده؛ آزمون مستقیم Microsoft Word انجام نشده است.

[دانلود کل مجموعه](../organized-deliverables.zip) · [روش بازتولید و کنترل](../annual/README.md)
'''
(ROOT/'برنامه تحصیلی/README.md').write_text(intro+'\n'.join(rows)+'\n'+notes)
with zipfile.ZipFile(ROOT/'organized-deliverables.zip','w',zipfile.ZIP_DEFLATED) as z:
 for folder in ['برنامه تحصیلی','گزارش دانش آموز']:
  for p in sorted((ROOT/folder).rglob('*')):
   if p.is_dir():z.writestr(str(p.relative_to(ROOT))+'/',b'')
   elif p.name!='.gitkeep':z.write(p,str(p.relative_to(ROOT)))
with zipfile.ZipFile(ROOT/'organized-deliverables.zip') as z:
 for e in manifest:
  for ext in ['docx','pdf']:
   p=Path(e['directory'])/(e['stem']+'.'+ext)
   assert z.read(str(p))==(ROOT/p).read_bytes()
for name,h in json.loads((ROOT/'annual/preserved.json').read_text()).items():assert sha(ROOT/name)==h,name
print('Published 21 pairs (19 dated + 2 provisional); ZIP verified; all preserved artifacts unchanged.')
