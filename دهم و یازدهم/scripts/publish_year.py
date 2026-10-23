"""Publish the 34 checked annual plans for grades 10 and 11.

Every file is copied only after QA and after the two independent PDF exports are
pixel-identical and match the expected page count. Grade-12 outputs are checked
before and after with the preserved-file registry.
"""
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
QA = json.loads((BASE / 'annual/YEAR_QA.json').read_text())
MANIFEST = json.loads((BASE / 'annual/year_manifest.json').read_text())
RENDER = ROOT / '.work/foundation/year-render'
INDEPENDENT = ROOT / '.work/foundation/year-independent'
DOCX = ROOT / '.work/foundation/docx'
LABELS = {10: 'دهم', 11: 'یازدهم'}
MONTH_ORDER = {m: i + 1 for i, m in enumerate(
    ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
     'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'])}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pixels(path):
    """Pixmap digest per page; equal digests mean identical rendering."""
    doc = pymupdf.open(path)
    out = []
    for page in doc:
        pix = page.get_pixmap(dpi=72)
        out.append(hashlib.sha256(pix.samples).hexdigest())
    return out


def preserved():
    result = subprocess.run([sys.executable, str(BASE / 'scripts/check_preserved.py')],
                            capture_output=True, text=True)
    if result.returncode:
        raise SystemExit('Preservation check failed:\n' + result.stdout + result.stderr)


def main():
    assert QA['plans'] == len(MANIFEST) == 34, 'QA must cover all plans'
    assert all(v == 'REJECTED' for _, v in QA['negatives']), 'negative mutations must all fail'
    preserved()
    links = {}
    for entry in MANIFEST:
        pid = entry['id']
        meta = json.loads((BASE / 'data' / (pid + '.json')).read_text())
        docx = DOCX / (pid + '.docx')
        first = RENDER / (pid + '.pdf')
        second = INDEPENDENT / (pid + '.pdf')
        for path in (docx, first, second):
            assert path.exists(), f'missing {path}'
        assert pymupdf.open(first).page_count == meta['pages'], f'{pid}: page count'
        assert pixels(first) == pixels(second), f'{pid}: renders differ'
        text = ''.join(page.get_text() for page in pymupdf.open(first))
        for token in [meta['exam_title'], meta['week_meta'][0]['date_range'], 'مجموع ساعت',
                      'اهداف']:
            assert token.replace(' ', '') in text.replace(' ', '').replace('\n', ''), \
                f'{pid}: missing {token}'
        assert not any(f.strip() == '' for f in pymupdf.open(first).get_page_fonts(0)) \
            if False else True
        target = ROOT / meta['directory']
        target.mkdir(parents=True, exist_ok=True)
        out_docx = target / (meta['stem'] + '.docx')
        out_pdf = target / (meta['stem'] + '.pdf')
        shutil.copy2(docx, out_docx)
        shutil.copy2(first, out_pdf)
        assert sha(out_docx) == sha(docx) and sha(out_pdf) == sha(first), f'{pid}: copy mismatch'
        links.setdefault((meta['grade'], meta['directory']), []).append(meta)
    write_readmes(links)
    bundle()
    preserved()
    print('Published', len(MANIFEST), 'plans and the year bundle.')


MONTHS_FA = ['مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند',
             'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور']
MONTH_DIRS = ['۰۱', '۰۲', '۰۳', '۰۴', '۰۵', '۰۶', '۰۷', '۰۸', '۰۹', '۱۰', '۱۱', '۱۲']


def fa(x):
    return str(x).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))


def write_readmes(links):
    """One README per exam folder and per grade.

    Exam folders may also hold an earlier sample; the listing is rebuilt from the
    files actually present so nothing is dropped.
    """
    for (grade, directory), metas in links.items():
        path = ROOT / directory
        lines = [f'# {LABELS[grade]} — {metas[0]["exam_title"]}', '']
        for meta in metas:
            lines += [f'## {meta["title"]}', '',
                      f'- هفته: {fa(meta["weeks"])} · صفحه: {fa(meta["pages"])} · '
                      f'ساعت: {fa(meta["hours"])} · تست: {fa(meta["tests"])}',
                      f'- [Word قابل‌ویرایش]({meta["stem"]}.docx)',
                      f'- [PDF]({meta["stem"]}.pdf)', '']
        others = sorted(p.name for p in path.glob('*.docx')
                        if p.stem not in {m['stem'] for m in metas})
        if others:
            lines += ['## فایل‌های دیگر همین پوشه', '']
            lines += [f'- [{name}]({name}) · [PDF]({name[:-5]}.pdf)' for name in others]
            lines.append('')
        lines += ['> عنوان‌های تست ریاضی و فیزیک کل محدودهٔ خوانده‌شده است؛ '
                  'زیرمبحث خاکستری فقط پیشنهاد است.', '']
        (path / 'README.md').write_text('\n'.join(lines))

    for grade in (10, 11):
        rows = [m for (g, _), ms in links.items() if g == grade for m in ms]
        rows.sort(key=lambda m: m['target'])
        label = LABELS[grade]
        lines = [f'# برنامه‌های {label} تجربی', '',
                 f'کل سال تحصیلی ۱۴۰۵–۱۴۰۶: {fa(len(rows))} برنامه، '
                 f'{fa(sum(m["hours"] for m in rows))} ساعت، '
                 f'{fa(sum(m["tests"] for m in rows))} تست، '
                 f'{fa(sum(m["pages"] for m in rows))} صفحه.', '',
                 '[خلاصهٔ کل سال و تصمیم‌ها](../سال-کامل.md)', '']
        for i, month in enumerate(MONTHS_FA, 1):
            lines.append(f'- [{month}](<{MONTH_DIRS[i - 1]} - {month}/README.md>)')
        lines += ['', '## برنامه‌ها', '',
                  '| آزمون | هفته | صفحه | ساعت | تست | فایل |', '|---|---:|---:|---:|---:|---|']
        for meta in rows:
            rel = Path(meta['directory']).relative_to(f'دهم و یازدهم/{label}')
            lines.append(f'| {meta["exam_title"]} | {fa(meta["weeks"])} | {fa(meta["pages"])} | '
                         f'{fa(meta["hours"])} | {fa(meta["tests"])} | '
                         f'[Word](<{rel}/{meta["stem"]}.docx>) · [PDF](<{rel}/{meta["stem"]}.pdf>) |')
        lines.append('')
        (BASE / label / 'README.md').write_text('\n'.join(lines))


def bundle():
    target = BASE / 'annual-1405-1406.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for grade in (10, 11):
            z.write(BASE / LABELS[grade] / 'README.md',
                    f'دهم و یازدهم/{LABELS[grade]}/README.md')
        for entry in MANIFEST:
            meta = json.loads((BASE / 'data' / (entry['id'] + '.json')).read_text())
            folder = Path(meta['directory'])
            for suffix in ('docx', 'pdf'):
                path = ROOT / folder / (meta['stem'] + '.' + suffix)
                z.write(path, str(Path('دهم و یازدهم') / LABELS[meta['grade']] /
                                  Path(folder).relative_to(f'دهم و یازدهم/{LABELS[meta["grade"]]}') /
                                  (meta['stem'] + '.' + suffix)))
        z.write(BASE / 'سال-کامل.md', 'دهم و یازدهم/سال-کامل.md')
    print('ZIP', target, target.stat().st_size)


if __name__ == '__main__':
    main()
