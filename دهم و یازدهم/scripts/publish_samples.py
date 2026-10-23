"""Publish only two checked one-week samples; keep original annual outputs untouched."""
import json,sys,hashlib,shutil,zipfile
from pathlib import Path
from check_samples import check_data
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parent
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
render=ROOT/sys.argv[1]
manifest=load(BASE/'samples.json');qa=load(BASE/'SAMPLE_QA.json');visual=load(BASE/'VISUAL_REVIEW.json')
assert qa['status']=='passed' and visual['status']=='reviewed'
checks={c['id']:c for c in qa['checks']};v={c['id']:c for c in visual['checks']}
assert {e['id'] for e in manifest}=={'g10-1405-08-15-week1','g11-1405-08-15-week1'}
exec((BASE/'scripts/check_preserved.py').read_text(),{'__file__':str(BASE/'scripts/check_preserved.py')})
for e in manifest:
 ident=e['id'];c=checks[ident];check_data(load(BASE/'data'/(ident+'.json')))
 assert sha(BASE/'data'/(ident+'.json'))==c['data_sha256']
 assert sha(ROOT/'.work/foundation/docx'/(ident+'.docx'))==c['word_sha256']
 assert sha(render/(ident+'.pdf'))==c['pdf_sha256']==v[ident]['pdf_sha256']
for e in manifest:
 dest=ROOT/e['directory'];assert dest.resolve().is_relative_to(BASE.resolve())
 for ext,src in [('docx',ROOT/'.work/foundation/docx'),('pdf',render)]:shutil.copyfile(src/(e['id']+'.'+ext),dest/(e['stem']+'.'+ext))
 (dest/'README.md').write_text(f"# نمونهٔ هفتهٔ اول آزمون ۱۵ آبان — {'دهم' if e['grade']==10 else 'یازدهم'}\n\nبازه: ۲ تا ۸ آبان ۱۴۰۵؛ نمونه برای بازخورد، نه برنامهٔ کامل دوهفته‌ای.\n\nجمع: **{e['hours']} ساعت، {e['tests']} تست**؛ شامل ۴ ساعت دروس نهایی.\n\n[Word قابل‌ویرایش](<{e['stem']}.docx>) · [PDF](<{e['stem']}.pdf>)\n\nپنجشنبه فقط تست است؛ زمین‌شناسی فعلاً اضافه نشده است.\n")
files=[ROOT/e['directory']/(e['stem']+'.'+ext) for e in manifest for ext in ['docx','pdf']]+[BASE/'SAMPLE_REVIEW.md']
with zipfile.ZipFile(BASE/'samples-15-aban.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(BASE))
with zipfile.ZipFile(BASE/'samples-15-aban.zip') as z:
 assert len(z.namelist())==5
 for p in files:assert z.read(str(p.relative_to(BASE)))==p.read_bytes()
exec((BASE/'scripts/check_preserved.py').read_text(),{'__file__':str(BASE/'scripts/check_preserved.py')})
print('PASS: two sample Word/PDF pairs and separate sample ZIP published; original files unchanged.')
