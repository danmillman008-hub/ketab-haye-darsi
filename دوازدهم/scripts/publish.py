"""Publish the debugged grade-12 files into `دوازدهم/` (never into the old folder)."""
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parents[1]
DATA = BASE / 'annual/data'
DOCX = ROOT / '.work/d12/docx'
PDF = ROOT / '.work/d12/render'
FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


def fa(x):
    return str(x).translate(FA)


def main():
    ids = sorted(p.stem for p in DATA.glob('*.json'))
    for pid in ids:
        subprocess.run([sys.executable, str(BASE / 'scripts/build_word.py'), pid], check=True,
                       stdout=subprocess.DEVNULL)
    subprocess.run(['node', str(BASE / 'scripts/render.mjs'), str(PDF)], check=True)
    rows = []
    for pid in ids:
        meta = json.loads((DATA / (pid + '.json')).read_text())
        docx, pdf = DOCX / (pid + '.docx'), PDF / (pid + '.pdf')
        assert docx.exists() and pdf.exists(), pid
        pages = pymupdf.open(pdf).page_count
        assert pages == meta['pages'], f"{pid}: {pages} != {meta['pages']}"
        dest = ROOT / meta['directory']
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(docx, dest / (meta['stem'] + '.docx'))
        shutil.copy2(pdf, dest / (meta['stem'] + '.pdf'))
        rows.append(meta)
    readmes(rows)
    bundle(rows)
    print('published', len(rows), 'plans')


def readmes(rows):
    base_rel = 'دوازدهم'
    intro = ['# برنامه‌های مطالعاتی دوازدهم تجربی', '',
             'نسخهٔ اصلیِ برنامه با همان فرم و چیدمان قبلی؛ فقط دو اصلاح جزئی اعمال شده است: '
             'حذف باکس‌های درسنامهٔ یک/دو صفحه‌ای (ادغام در باکس اصلی و تبدیل جای آن به تست) و '
             'نوشتن عنوان تست ریاضی و فیزیک به‌صورت کل محدودهٔ مطالعه‌شده با زیرمبحث خاکستری «* ترجیحاً:».',
             '', '[توضیح اصلاحات](PRINCIPLES.md) · [بستهٔ کامل](annual-1405-1406.zip)', '',
             '| آزمون | Word | PDF |', '|---|---|---|']
    for meta in rows:
        rel = Path(meta['directory']).relative_to(base_rel)
        intro.append(f"| {meta['title']} | [Word](<{rel}/{meta['stem']}.docx>) | "
                     f"[PDF](<{rel}/{meta['stem']}.pdf>) |")
    intro.append('')
    (BASE / 'README.md').write_text('\n'.join(intro))
    for folder in sorted((BASE).iterdir()):
        if not folder.is_dir() or folder.name in ('annual', 'scripts'):
            continue
        entries = [m for m in rows if Path(m['directory']).parts[1] == folder.name]
        lines = [f'# {folder.name}', '']
        for meta in entries:
            rel = Path(meta['directory']).relative_to(base_rel)
            lines.append(f"- {meta['title']}: [Word](<{rel}/{meta['stem']}.docx>) · "
                         f"[PDF](<{rel}/{meta['stem']}.pdf>)")
        (folder / 'README.md').write_text('\n'.join(lines) + '\n')


def bundle(rows):
    target = BASE / 'annual-1405-1406.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for meta in rows:
            rel = Path(meta['directory']).relative_to('دوازدهم')
            for ext in ('docx', 'pdf'):
                z.write(ROOT / meta['directory'] / (meta['stem'] + '.' + ext),
                        str(Path('دوازدهم') / rel / (meta['stem'] + '.' + ext)))
        z.write(BASE / 'README.md', 'دوازدهم/README.md')
        z.write(BASE / 'PRINCIPLES.md', 'دوازدهم/PRINCIPLES.md')
    print('zip', target, target.stat().st_size)


if __name__ == '__main__':
    main()
