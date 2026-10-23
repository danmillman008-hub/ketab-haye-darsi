"""Turn the reviewed grade-12 plans into a clean per-phase scope table.

`annual/data/*.json` was checked page by page against the printed MAZ booklet.
This script keeps only what the generator needs: for every exam block and every
phase (a one- or two-week span) the grade of the material and the printed page
ranges of the four subjects, each range tagged with its book grade so a grade-12
plan can carry tenth- and eleventh-grade review blocks too.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'annual/data'
OUT = Path(__file__).resolve().parent / 'scopes12.json'
EXAMS = ['1405-07-17', '1405-08-01', '1405-08-15', '1405-08-29', '1405-09-13', '1405-09-27',
         '1405-10-25', '1405-11-09', '1405-11-23', '1405-12-07', '1405-12-21', '1406-01-06',
         '1406-01-20', '1406-02-03', '1406-02-17', '1406-02-24', '1406-03-21', '1406-03-28',
         '1406-04-04']
GRADE = {'دهم': 10, 'یازدهم': 11, 'دوازدهم': 12, 'پایه': 0, 'سه پایه': 0}
FA = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
RNG = re.compile(r'ص\s*([۰-۹]+)\s*[–-]\s*([۰-۹]+)')
MRNG = re.compile(r'ریاضی\s*([۱۲۳])\s*ص\s*([۰-۹]+)\s*[–-]\s*([۰-۹]+)')
FULL = {10: {'bio': (1, 111), 'phys': (1, 120), 'chem': (1, 122), 'math': (1, 170)},
        11: {'bio': (1, 152), 'phys': (1, 104), 'chem': (1, 123), 'math': (1, 166)},
        12: {'bio': (1, 124), 'phys': (1, 125), 'chem': (1, 123), 'math': (1, 148)}}

FIXES = {
    '1405-08-01': [
        {'grade': 12,
         'bio': [[12, 1, 20]], 'phys': [[12, 1, 15]], 'chem': [[12, 1, 24]],
         'math': [[12, 1, 29]],
         'head': {'bio': 'مولکول‌های اطلاعاتی + گوارش و جذب مواد',
                  'phys': 'حرکت بر خط راست؛ تا قبل از حرکت با شتاب ثابت',
                  'chem': 'مولکول‌ها در خدمت تندرستی؛ تا ابتدای pH',
                  'math': 'تابع'}},
        {'grade': 10,
         'bio': [[10, 25, 46]], 'phys': [[10, 23, 52]], 'chem': [[10, 19, 46]],
         'math': [[10, 70, 82]],
         'head': {'bio': 'تبادلات گازی', 'phys': 'ویژگی‌های فیزیکی مواد',
                  'chem': 'کیهان، زادگاه الفبای هستی', 'math': 'تابع و معادلهٔ درجه۲'}},
    ],
    '1405-08-29': [
        {'grade': 12,
         'bio': [[12, 27, 41]], 'phys': [[12, 15, 37]], 'chem': [[12, 24, 44]],
         'math': [[12, 42, 48]],
         'head': {'bio': 'به سوی پروتئین + تنظیم بیان ژن + مفاهیم پایه',
                  'phys': 'دینامیک؛ تا قبل از اصطکاک',
                  'chem': 'از pH تا قبل از واکنش‌ها و سفر هدایت‌شدهٔ الکترون',
                  'math': 'معادلات مثلثاتی'}},
    ],
}

# Manual corrections found by the page audit (old file had gaps, duplicates or the
# wrong grade attached to a phase).
FIXES['1405-08-29'] = [
    {'grade': 12, 'bio': [[12, 27, 41]], 'phys': [[12, 15, 37]], 'chem': [[12, 24, 44]],
     'math': [[12, 42, 48]],
     'head': {'bio': 'به سوی پروتئین، تنظیم بیان ژن و آغاز تغییر', 'phys': 'دینامیک؛ تا قبل از اصطکاک',
              'chem': 'از pH تا قبل از واکنش‌ها و سفر هدایت‌شدهٔ الکترون', 'math': 'معادلات مثلثاتی'}},
    {'grade': 10, 'bio': [[10, 69, 89]], 'phys': [[10, 83, 103]], 'chem': [[10, 70, 98]],
     'math': [[11, 95, 118]],
     'head': {'bio': 'تنظیم اسمزی و دفع مواد زائد', 'phys': 'دما و گرما؛ تا قبل از تغییر حالت',
              'chem': 'گازها و آب؛ تا انتهای قسمت در میلیون', 'math': 'توابع نمایی و لگاریتمی'}},
]
FIXES['1405-10-25'] = [
    {'grade': 12, 'bio': [[12, 1, 14]], 'phys': [[12, 1, 15]], 'chem': [[12, 1, 17]],
     'math': [[12, 1, 30]], 'head': {'bio': 'نوکلئیک‌اسیدها و همانندسازی',
                                    'phys': 'حرکت بر خط راست', 'chem': 'مولکول‌ها در خدمت تندرستی', 'math': 'تابع'}},
    {'grade': 12, 'bio': [[12, 15, 32]], 'phys': [[12, 15, 37]], 'chem': [[12, 18, 33]],
     'math': [[12, 31, 48]], 'head': {'bio': 'پروتئین‌ها، رونویسی و ترجمه',
                                     'phys': 'شتاب ثابت و دینامیک', 'chem': 'تندرستی و آغاز آسایش', 'math': 'تناوب، تانژانت و معادلات مثلثاتی'}},
    {'grade': 12, 'bio': [[12, 33, 46]], 'phys': [[12, 37, 52]], 'chem': [[12, 34, 50]],
     'math': [[12, 49, 57]], 'head': {'bio': 'تنظیم بیان ژن و انتقال اطلاعات',
                                     'phys': 'دینامیک؛ اصطکاک تا پایان', 'chem': 'آسایش و رفاه', 'math': 'حد بی‌نهایت'}},
    {'grade': 12, 'bio': [[12, 47, 62]], 'phys': [[12, 53, 62]], 'chem': [[12, 51, 66]],
     'math': [[12, 58, 76]], 'head': {'bio': 'تغییر در اطلاعات وراثتی', 'phys': 'آغاز نوسان',
                                     'chem': 'آسایش و رفاه؛ تا پایان فصل', 'math': 'حد در بی‌نهایت و مفهوم مشتق'}},
]
FIXES['1406-02-03'] = [
    {'grade': 12, 'bio': [[12, 91, 106]], 'phys': [[12, 95, 111]], 'chem': [[12, 103, 110]],
     'math': [[12, 121, 142]], 'head': {'bio': 'مهندسی ژنتیک و زیست‌فناوری', 'phys': 'فیزیک اتمی؛ تا قبل از ساختار هسته',
                                       'chem': 'آیندهٔ روشن‌تر؛ ارزش فناوری', 'math': 'مقاطع مخروطی و دایره'}},
    {'grade': 11, 'bio': [[11, 119, 152]], 'phys': [[11, 85, 104]], 'chem': [[11, 77, 98]],
     'math': [[10, 118, 140]], 'head': {'bio': 'تولیدمثل نهان‌دانگان و پاسخ گیاهان',
                                       'phys': 'القای الکترومغناطیسی', 'chem': 'در پی غذای سالم',
                                       'math': 'شمارش، بدون شمردن'}},
]
FIXES['1406-02-17'] = [
    {'grade': 12, 'bio': [[12, 107, 124]], 'phys': [[12, 112, 125]], 'chem': [[12, 111, 123]],
     'math': [[12, 143, 148]], 'head': {'bio': 'اساس رفتار و ارتباط جانوران', 'phys': 'ساختار هسته تا پایان فصل۴',
                                       'chem': 'آیندهٔ روشن‌تر؛ تا پایان', 'math': 'قانون احتمال کل'}},
    {'grade': 12, 'bio': [[10, 1, 111], [11, 1, 152]], 'phys': [[10, 1, 120], [11, 1, 104]],
     'chem': [[10, 1, 122], [11, 1, 123]], 'math': [[10, 118, 151], [11, 143, 152]],
     'head': {'bio': 'مرور جامع سه پایه', 'phys': 'مرور جامع سه پایه', 'chem': 'مرور جامع سه پایه',
              'math': 'مرور جامع شمارش و احتمال'}},
]
FIXES['1406-03-28'] = [
    {'grade': 12,
     'bio': [[12, 1, 124], [11, 1, 152], [10, 1, 111]],
     'phys': [[12, 1, 125], [11, 1, 104], [10, 1, 120]],
     'chem': [[12, 1, 123], [11, 1, 123], [10, 1, 122]],
     'math': [[12, 1, 148], [11, 1, 166], [10, 1, 170]],
     'head': {'bio': 'مرور جامع سه پایه', 'phys': 'مرور جامع سه پایه',
              'chem': 'مرور جامع سه پایه', 'math': 'ریاضی سه پایه'}},
]
FIXES['1406-04-04'] = FIXES['1406-03-28']
FIXES['1406-03-21'] = [
    {'grade': 12, 'bio': [[12, 1, 62]], 'phys': [[12, 1, 52]], 'chem': [[12, 1, 66]],
     'math': [[12, 1, 76]], 'head': {'bio': 'مرور جامع نیم‌سال اول', 'phys': 'مرور جامع نیم‌سال اول',
                                    'chem': 'مرور جامع نیم‌سال اول', 'math': 'مرور جامع نیم‌سال اول'}},
    {'grade': 10, 'bio': [[10, 1, 111]], 'phys': [[10, 1, 120]], 'chem': [[10, 1, 122]],
     'math': [[10, 1, 170]], 'head': {'bio': 'مرور جامع دهم', 'phys': 'مرور جامع دهم',
                                     'chem': 'مرور جامع دهم', 'math': 'مرور جامع ریاضی۱'}},
    {'grade': 11, 'bio': [[11, 1, 152]], 'phys': [[11, 1, 104]], 'chem': [[11, 1, 123]],
     'math': [[11, 1, 166]], 'head': {'bio': 'مرور جامع یازدهم', 'phys': 'مرور جامع یازدهم',
                                     'chem': 'مرور جامع یازدهم', 'math': 'مرور جامع ریاضی۲'}},
    {'grade': 12, 'bio': [[12, 63, 124]], 'phys': [[12, 53, 125]], 'chem': [[12, 67, 123]],
     'math': [[12, 65, 148]], 'head': {'bio': 'مرور جامع نیم‌سال دوم', 'phys': 'مرور جامع نیم‌سال دوم',
                                      'chem': 'مرور جامع نیم‌سال دوم', 'math': 'مرور جامع نیم‌سال دوم'}},
]


def num(x):
    return int(x.translate(FA))


def full(grade):
    return {k: [[grade, *FULL[grade][k]]] for k in FULL[grade]}


def parse(scope):
    bio = scope.get('bio') or []
    chem = scope.get('chem') or []
    grade = int(bio[0][0]) if bio else (int(chem[0][0]) if chem else GRADE[scope['label']])
    out = {'grade': grade, 'bio': [[int(a) if isinstance(a, int) else a, int(b), int(c)]
                                   for a, b, c in bio],
           'chem': [[int(a), int(b), int(c)] for a, b, c, _ in chem]}
    out['phys'] = [[grade, num(a), num(b)]
                   for a, b in RNG.findall(' '.join(scope.get('physics') or []))]
    out['math'] = [[{1: 10, 2: 11, 3: 12}[num(bk)], num(a), num(b)]
                   for bk, a, b in MRNG.findall(' '.join(scope.get('math') or []))]
    head = {'bio': (scope.get('bio') and '') or '',
            'phys': ((scope.get('physics') or [''])[0]).split('؛')[0],
            'chem': chem[0][3] if chem else '',
            'math': ((scope.get('math') or [''])[0]).split('؛')[0]}
    out['head'] = head
    if grade == 0:
        merged = {}
        for subj in ('bio', 'phys', 'chem', 'math'):
            merged[subj] = [[10, *FULL[10][subj]], [11, *FULL[11][subj]]]
        out.update(merged)
        out['grade'] = 12
        out['head'] = {k: 'مرور جامع سه پایه' for k in head}
        return out
    if not out['bio']:
        out['bio'] = [[grade, *FULL[grade]['bio']]]
    if not out['chem']:
        out['chem'] = [[grade, *FULL[grade]['chem']]]
    if not out['phys']:
        out['phys'] = [[grade, *FULL[grade]['phys']]]
    if not out['math']:
        out['math'] = [[grade, *FULL[grade]['math']]]
    return out


def merge(ranges):
    spans = sorted((int(a), int(b)) for _, a, b in ranges)
    out = []
    for a, b in spans:
        if out and a <= out[-1][1] + 1:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def tidy(phase):
    for subj in ('bio', 'phys', 'chem', 'math'):
        by_grade = {}
        for g, a, b in phase[subj]:
            by_grade.setdefault(int(g), []).append((g, int(a), int(b)))
        phase[subj] = [item for g in sorted(by_grade)
                       for item in ([g, a, b] for a, b in merge(by_grade[g]))]
    return phase


def main():
    data = {}
    for exam in EXAMS:
        plan = json.loads((OLD / (exam + '.json')).read_text())
        if exam in FIXES:
            phases = FIXES[exam]
        else:
            phases = [parse(s) for s in plan['scopes']]
        data[exam] = {'weeks': plan['weeks'], 'phases': [tidy(p) for p in phases]}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    for exam, v in data.items():
        print(exam, v['weeks'], 'w', [(p['grade'], p['bio'], p['phys'], p['math'], p['chem']) for p in v['phases']])


if __name__ == '__main__':
    main()
