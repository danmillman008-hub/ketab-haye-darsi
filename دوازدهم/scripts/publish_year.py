"""Publish the checked grade-12 year: Word files, native PDFs and the bundle."""
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pymupdf

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent
MANIFEST = json.loads((BASE / 'annual/year_manifest.json').read_text())
QA = json.loads((BASE / 'annual/YEAR_QA.json').read_text())
RENDER = ROOT / '.work/foundation12/render'
DOCX = ROOT / '.work/foundation/docx'
MONTH_ORDER = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
               'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
MONTH_DIRS = ['۰۱', '۰۲', '۰۳', '۰۴', '۰۵', '۰۶', '۰۷', '۰۸', '۰۹', '۱۰', '۱۱', '۱۲']
ACADEMIC = ['مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند',
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور']
FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


def fa(x):
    return str(x).translate(FA)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert QA['issues'] == [], 'QA must be clean'
    assert QA['plans'] == len(MANIFEST)
    for entry in MANIFEST:
        subprocess.run([sys.executable, str(BASE / 'scripts/build_word.py'), entry['id']], check=True,
                       stdout=subprocess.DEVNULL)
    subprocess.run(['node', str(BASE / 'scripts/render.mjs'), str(RENDER),
                    str(BASE / 'annual/year_manifest.json')], check=True)
    links = []
    for entry in MANIFEST:
        meta = json.loads((BASE / 'data' / (entry['id'] + '.json')).read_text())
        docx = DOCX / (entry['id'] + '.docx')
        pdf = RENDER / (entry['id'] + '.pdf')
        assert docx.exists() and pdf.exists(), entry['id']
        assert pymupdf.open(pdf).page_count == meta['pages'], f"{entry['id']}: page count"
        target = ROOT / meta['directory']
        target.mkdir(parents=True, exist_ok=True)
        out_docx = target / (meta['stem'] + '.docx')
        out_pdf = target / (meta['stem'] + '.pdf')
        shutil.copy2(docx, out_docx)
        shutil.copy2(pdf, out_pdf)
        assert sha(out_docx) == sha(docx) and sha(out_pdf) == sha(pdf)
        links.append(meta)
    readmes(links)
    bundle(links)
    print('Published', len(links), 'grade-12 plans.')


def readmes(links):
    for meta in links:
        path = ROOT / meta['directory']
        text = '\n'.join([
            f"# {meta['title']}", '',
            f"- هفته: {fa(meta['weeks'])} · صفحه: {fa(meta['pages'])} · "
            f"ساعت: {fa(meta['hours'])} · تست: {fa(meta['tests'])}",
            f"- [Word قابل‌ویرایش]({meta['stem']}.docx)",
            f"- [PDF]({meta['stem']}.pdf)", '',
            '> همهٔ باکس‌های درسی مرور همان صفحات اعلام‌شده‌اند؛ '
            'باکس‌های تست آزاد و قابل انتخاب‌اند.', ''])
        (path / 'README.md').write_text(text)
    lines = ['# برنامهٔ سال تحصیلی ۱۴۰۵–۱۴۰۶ — دوازدهم تجربی', '',
             f"{fa(len(links))} برنامه، {fa(sum(m['hours'] for m in links))} ساعت، "
             f"{fa(sum(m['tests'] for m in links))} تست، {fa(sum(m['pages'] for m in links))} صفحه.", '',
             '[خلاصهٔ سال و تصمیم‌ها](../سال-کامل.md) · [اصول](../PRINCIPLES.md)', '']
    for i, month in enumerate(ACADEMIC, 1):
        rows = [m for m in links if m['target'].split('-')[1] == str(MONTH_ORDER.index(month) + 1).zfill(2)]
        if rows:
            lines.append(f'- [{month}](<{MONTH_DIRS[i - 1]} - {month}/README.md>)')
    lines += ['', '| آزمون | هفته | صفحه | ساعت | تست | فایل |', '|---|---:|---:|---:|---:|---|']
    for m in sorted(links, key=lambda x: x['target']):
        rel = Path(m['directory']).relative_to('دوازدهم/دوازدهم')
        lines.append(f"| {m['exam_title']} | {fa(m['weeks'])} | {fa(m['pages'])} | {fa(m['hours'])} | "
                     f"{fa(m['tests'])} | [Word](<{rel}/{m['stem']}.docx>) · "
                     f"[PDF](<{rel}/{m['stem']}.pdf>) |")
    lines.append('')
    (BASE / 'README.md').write_text('\n'.join(lines))
    for i, month in enumerate(ACADEMIC, 1):
        folder = BASE / 'دوازدهم' / f'{MONTH_DIRS[i - 1]} - {month}'
        rows = [m for m in links if m['target'].split('-')[1] == str(MONTH_ORDER.index(month) + 1).zfill(2)]
        if not rows:
            continue
        folder.mkdir(parents=True, exist_ok=True)
        body = [f'# {month}', '']
        for m in rows:
            body.append(f"- [{m['exam_title']}](<{Path(m['directory']).name}/README.md>)")
        body.append('')
        (folder / 'README.md').write_text('\n'.join(body))


def bundle(links):
    target = BASE / 'annual-1405-1406.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for m in links:
            folder = Path(m['directory'])
            for suffix in ('docx', 'pdf'):
                z.write(ROOT / folder / (m['stem'] + '.' + suffix),
                        str(Path('دوازدهم') / Path(m['directory']).relative_to('دوازدهم/دوازدهم')
                            / (m['stem'] + '.' + suffix)))
        z.write(BASE / 'سال-کامل.md', 'دوازدهم/سال-کامل.md')
        z.write(BASE / 'PRINCIPLES.md', 'دوازدهم/PRINCIPLES.md')
    print('ZIP', target, target.stat().st_size)


if __name__ == '__main__':
    main()
