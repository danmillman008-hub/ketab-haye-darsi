"""Derive the grade-12 MAZ budget from the previously reviewed annual plans.

Every grade-12 plan in `annual/data` was already checked against the MAZ booklet.
This script reads those reviewed boxes and keeps, per exam and subject, the union
of page ranges actually assigned to each grade. Lower-grade ranges appear only
where the MAZ exam itself covers them (the جمع‌بندی exams).
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'annual/data'
OUT = Path(__file__).resolve().parent / 'budget12.json'
FA = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
EXAMS = ['1405-07-17', '1405-08-01', '1405-08-15', '1405-08-29', '1405-09-13', '1405-09-27',
         '1405-10-25', '1405-11-09', '1405-11-23', '1405-12-07', '1405-12-21', '1406-01-06',
         '1406-01-20', '1406-02-03', '1406-02-17', '1406-02-24', '1406-03-21', '1406-03-28',
         '1406-04-04']
SUBJ = {'زیست': 'bio', 'فیزیک': 'physics', 'شیمی': 'chem'}
RANGE = re.compile(r'ص\s*([۰-۹]+)\s*[–-]\s*([۰-۹]+)')
MATH = re.compile(r'ریاضی\s*([۱۲۳])\s*ص\s*([۰-۹]+)\s*[–-]\s*([۰-۹]+)')


def num(s):
    return int(s.translate(FA))


def grade_of(label):
    return {'دهم': 10, 'یازدهم': 11, 'دوازدهم': 12}[label]


def merge(ranges):
    """Union of ranges as a minimal sorted list."""
    spans = sorted(ranges)
    out = []
    for a, b in spans:
        if out and a <= out[-1][1] + 1:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def extract():
    result = {}
    missing = []
    for exam in EXAMS:
        plan = json.loads((OLD / (exam + '.json')).read_text())
        pages = {}
        for day in plan['days']:
            for box in day['boxes']:
                text = unicodedata.normalize('NFKC', box['topic'])
                parts = box['subject'].split()
                subject = parts[0]
                if subject in SUBJ:
                    if len(parts) < 2 or parts[1] not in ('دهم', 'یازدهم', 'دوازدهم'):
                        missing.append((exam, box['subject'], text[:60]))
                        continue
                    grade = grade_of(parts[1])
                    key = (SUBJ[subject], grade)
                    found = [(num(a), num(b)) for a, b in RANGE.findall(text)]
                    if not found:
                        missing.append((exam, box['subject'], text[:60]))
                    pages.setdefault(key, []).extend(found)
                elif subject == 'ریاضی':
                    for book, a, b in MATH.findall(text):
                        grade = {1: 10, 2: 11, 3: 12}[num(book)]
                        pages.setdefault(('math', grade), []).append((num(a), num(b)))
        result[exam] = {f'{s}{g}': merge(v) for (s, g), v in pages.items()}
    return result, missing


if __name__ == '__main__':
    data, missing = extract()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    for exam, vals in data.items():
        print(exam, dict(sorted(vals.items())))
    print('boxes without a page range:', len(missing))
    for item in missing[:12]:
        print('  ', item)
