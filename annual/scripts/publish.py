"""Publish only validated clean-form plans; keep source/provenance notes out of student files."""
from pathlib import Path
import json,hashlib,shutil,sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
render=ROOT/sys.argv[1]
load=lambda p:json.loads((ROOT/p).read_text())
manifest=load('annual/manifest.json');qa=load('annual/QA.json');style=load('annual/STYLE_QA.json');source=load('annual/SOURCE_QA.json')
assert source['status']=='passed'
assert qa['status']=='passed' and qa['independentPixelComparison']
assert style['status']=='passed'
checks={c['id']:c for c in qa['checks']};data_checks={c['id']:c for c in style['checks']}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Validate the whole batch before overwriting any destination.
for e in manifest:
 assert sha(ROOT/'annual/data'/(e['id']+'.json'))==data_checks[e['id']]['data_sha256']==source['data_hashes'][e['id']]
 assert sha(ROOT/'.work/annual/docx'/(e['id']+'.docx'))==checks[e['id']]['docxSha256']
 assert sha(render/(e['id']+'.pdf'))==checks[e['id']]['pdfSha256']
for e in manifest:
 dest=ROOT/e['directory'];dest.mkdir(parents=True,exist_ok=True)
 for ext,source in [('docx',ROOT/'.work/annual/docx'),('pdf',render)]:
  shutil.copyfile(source/(e['id']+'.'+ext),dest/(e['stem']+'.'+ext))
intro='''# برنامه‌های مطالعاتی — فرم توصیفیِ قبلی

نسخهٔ جاری: فرم طلایی و نام کامل مباحث حفظ شده‌اند؛ اصلاح محدوده‌ها بر اساس کتاب‌های فعال انجام شده و توضیحات منابع در فایل دانش‌آموز نیست. باکس‌های ۱ آبان با نمونهٔ قبلی یکسان‌اند.

۱۹ برنامهٔ تاریخ‌دار از مهر ۱۴۰۵ تا تیر ۱۴۰۶ و دو برنامهٔ پریمیوم با هفته‌های نسبی. برای هر برنامه یک Word قابل‌ویرایش و PDF همان Word موجود است. گزارش‌های دانش‌آموز تغییر نکرده‌اند.

| آزمون | Word | PDF |
|---|---|---|
'''
for e in manifest:
 rel=Path(e['directory']).relative_to('برنامه تحصیلی')
 intro+='| '+e['title']+' | [Word](<'+str(rel/(e['stem']+'.docx'))+'>) | [PDF](<'+str(rel/(e['stem']+'.pdf'))+'>) |\n'
intro+='\n[دریافت کل مجموعه](../organized-deliverables.zip) · [راهنمای تهیه‌کننده](../annual/README.md) · [محل کتاب‌های فعال](../annual/BOOK_EDITIONS.md)\n'
(ROOT/'برنامه تحصیلی/README.md').write_text(intro)
for folder in sorted((ROOT/'برنامه تحصیلی').iterdir()):
 if not folder.is_dir():continue
 entries=[e for e in manifest if Path(e['directory']).parts[1]==folder.name]
 text='# '+folder.name+'\n\nنسخهٔ جاری با فرم توصیفیِ قبلی.\n\n'
 for e in entries:
  rel=Path(e['directory']).relative_to(folder.relative_to(ROOT))
  text+='- '+e['title']+': [Word](<'+str(rel/(e['stem']+'.docx'))+'>) · [PDF](<'+str(rel/(e['stem']+'.pdf'))+'>)\n'
 if not entries:text+='برای این ماه تاریخ آزمون در منبع تعیین نشده است؛ برنامهٔ فرضی ساخته نشده است.\n'
 if folder.name=='تاریخ اعلام‌نشده':text+='\nاین دو برنامه تاریخ قطعی ندارند.\n'
 (folder/'README.md').write_text(text)
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
for name,h in load('annual/preserved.json').items():assert sha(ROOT/name)==h,name
print('Published 21 clean-form Word/PDF pairs; monthly indexes and ZIP verified; reports unchanged.')
