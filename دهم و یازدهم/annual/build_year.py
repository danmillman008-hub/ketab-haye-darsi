"""Full-year plans for grades 10 and 11, driven by the transcribed MAZ budget.

Rules encoded here (see PRINCIPLES.md): six study days and a Friday; the normal
two-week cycle teaches in week one and explicitly reviews the same pages in week
two; long calendar gaps split the scope into two teach/review pairs or review
weeks; Thursdays carry the approved eight-hour consolidation block. Nothing is
written outside `دهم و یازدهم/`.
"""
import json
import sys
from datetime import timedelta
from pathlib import Path

import jdatetime

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'annual'))
from curriculum_map import (BIO_CHAPTERS, CHEM_CHAPTERS, chapters_for,  # noqa: E402
                            pages, split_units, units_for)

FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
          'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
DAY_NAMES = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه']
LABELS = {10: 'دهم', 11: 'یازدهم'}
SUBJECTS = ['bio', 'physics', 'chem', 'math', 'geo']


def fa(x):
    return str(x).translate(FA)


def jd(s):
    return jdatetime.date(*map(int, s.split('-')))


def label(d, year=False):
    return fa(d.day) + ' ' + MONTHS[d.month - 1] + (' ' + fa(d.year) if year else '')


# The academic year starts in Mehr, matching the folders created before this build.
ACADEMIC = ['مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند',
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور']
PERSIAN_2D = ['۰۱', '۰۲', '۰۳', '۰۴', '۰۵', '۰۶', '۰۷', '۰۸', '۰۹', '۱۰', '۱۱', '۱۲']


def folder_month(d):
    name = MONTHS[d.month - 1]
    return PERSIAN_2D[ACADEMIC.index(name)] + ' - ' + name


def join_fa(items, sep='، '):
    items = list(items)
    if len(items) <= 1:
        return ''.join(items)
    return sep.join(items[:-1]) + ' و ' + items[-1]


def overlap(units, ranges):
    out = []
    for unit in units:
        lo, hi = unit[0], unit[1]
        for a, b in ranges:
            if lo <= b and hi >= a:
                out.append(unit)
                break
    return out


def chapter_names(subject, grade, ranges):
    return [c[3] for c in overlap(chapters_for(subject, grade), ranges)]


def unit_names(subject, grade, ranges, limit=2):
    names = [u[3] for u in overlap(units_for(subject, grade), ranges)]
    return names[:limit]


def page_text(ranges):
    if len(ranges) == 1:
        a, b = ranges[0]
        return 'ص' + fa(a) + ('–' + fa(b) if b != a else '')
    return 'ص' + ' و '.join(fa(a) + '–' + fa(b) for a, b in ranges)


def topic(subject, grade, ranges, boundary='', review=False, compact=False, comprehensive=False):
    """A descriptive, book-anchored label that fits the fixed table cells."""
    if subject == 'math':
        names = unit_names('math', grade, ranges, 2)
        head = join_fa(names) if names else 'ریاضی'
    elif subject == 'bio':
        chs = chapter_names('bio', grade, ranges)
        if len(chs) <= 2:
            names = [u[3] for u in overlap(units_for('bio', grade), ranges)]
            if len(chs) == 1 and names:
                head = chs[0] + '؛ ' + join_fa(names[:2] if len(chs) and review else names[:3])
            else:
                head = join_fa(chs)
        else:
            head = join_fa(chs[:2]) + ' و فصل‌های دیگر'
    elif subject == 'chem':
        head = join_fa(chapter_names('chem', grade, ranges))
    elif subject == 'physics':
        head = join_fa(chapter_names('physics', grade, ranges))
    elif subject == 'geo':
        head = join_fa(chapter_names('geo', grade, ranges))
    else:
        raise KeyError(subject)
    if comprehensive:
        head = 'جمع‌بندی جامع ' + head
    if review:
        head = 'مرور ' + head
    text = head + '؛ ' + page_text(ranges)
    if boundary:
        text += '؛ ' + boundary
    if len(text) > 104:
        text = head[:52] + '…؛ ' + page_text(ranges) + ('؛ ' + boundary if boundary else '')
    return text


def box(subject, topic_text, detail, hours, tests=0, ranges=None, kind='study', preference=None):
    b = dict(subject=subject, topic=topic_text, detail=detail, hours=hours,
             tests=tests, kind=kind, ranges=ranges or [])
    if preference:
        b['preference'] = '* ترجیحاً: ' + preference
    return b


def subject_label(subject, grade):
    return {'bio': 'زیست ' + LABELS[grade], 'physics': 'فیزیک ' + LABELS[grade],
            'chem': 'شیمی ' + LABELS[grade], 'math': 'ریاضی',
            'geo': 'زمین‌شناسی یازدهم'}[subject]


def preference(subject, grade, ranges):
    if subject == 'math':
        names = unit_names('math', grade, ranges, 1)
    elif subject == 'physics':
        names = unit_names('physics', grade, ranges, 1)
    else:
        return None
    return names[0] if names else None


STUDY_DETAIL = {
    'bio': 'مطالعهٔ متن، شکل‌ها و قیدهای کتاب',
    'math': '۲ ساعت درسنامه و مثال؛ مرور مباحث قبلی و مطالعهٔ بخش جدید',
    'physics': '۲ ساعت درسنامه و مثال؛ مرور مباحث قبلی و مطالعهٔ بخش جدید',
    'chem': 'مطالعهٔ متن، مثال‌ها و خود را بیازمایید',
    'geo': 'مطالعهٔ متن و شکل‌های کتاب',
}
REVIEW_DETAIL = {
    'bio': 'مرور متن، شکل‌ها و قیدهای کتاب',
    'math': 'مرور درسنامه و مثال‌های حل‌شده',
    'physics': 'مرور درسنامه و مثال‌های حل‌شده',
    'chem': 'مرور متن، مثال‌ها و خود را بیازمایید',
    'geo': 'مرور متن و شکل‌های کتاب',
}


def teach_box(subject, grade, ranges, hours, review, boundary=''):
    kind = 'review' if review else 'study'
    return box(subject_label(subject, grade),
               topic(subject, grade, ranges, boundary, review=review),
               REVIEW_DETAIL[subject] if review else STUDY_DETAIL[subject],
               hours, ranges=ranges, kind=kind)


def test_box(subject, grade, ranges, hours, tests, detail, prefer=None, review=False, comprehensive=False):
    return box(subject_label(subject, grade),
               topic(subject, grade, ranges, review=review or None, comprehensive=comprehensive),
               detail, hours, tests, ranges, 'test', prefer)


def week_days(grade, start, week_no, scopes, review, final_week, exam_scope, official_exam, friday_label):
    """"scopes" maps subject -> list of ranges actually studied this week."""
    n_bio = 3 if len(pages(scopes['bio'])) >= 12 else (2 if len(pages(scopes['bio'])) >= 6 else 1)
    n_chem = 2 if len(pages(scopes['chem'])) >= 12 else 1
    bio_parts = split_units(scopes['bio'], 'bio', grade, n_bio)
    chem_parts = split_units(scopes['chem'], 'chem', grade, n_chem)
    bio_core, chem_core = list(bio_parts), list(chem_parts)
    while len(bio_parts) < 3:
        bio_parts.append(bio_parts[-1])
    while len(chem_parts) < 2:
        chem_parts.append(chem_parts[-1])
    math_r, phy_r = scopes['math'], scopes['physics']
    bio_full_test = exam_scope['bio'] if final_week else scopes['bio']
    chem_full_test = exam_scope['chem'] if final_week else scopes['chem']
    math_full_test = exam_scope['math'] if final_week else math_r
    phy_full_test = exam_scope['physics'] if final_week else phy_r
    geo_full_test = exam_scope.get('geo') or []

    def bio_study(i):
        r = bio_parts[i]
        repeat = i >= len(bio_core)
        if repeat:
            b = teach_box('bio', grade, r, 1, True)
            b['detail'] = 'مرور و تثبیت بخش‌های همین هفته'
            return b
        return teach_box('bio', grade, r, 1, review)

    def chem_study(i):
        r = chem_parts[i]
        repeat = i >= len(chem_core)
        if repeat:
            b = teach_box('chem', grade, r, 1, True)
            b['detail'] = 'مرور و تثبیت بخش‌های همین هفته'
            return b
        return teach_box('chem', grade, r, 1, review)

    day_boxes = [[] for _ in range(6)]
    day_boxes[0] += [bio_study(0),
                     teach_box('math', grade, math_r, 2, review),
                     test_box('bio', grade, bio_parts[0], 2, 20, '۲۰ تست آموزشی + تحلیل همهٔ گزینه‌ها')]
    day_boxes[1] += [chem_study(0),
                     teach_box('physics', grade, phy_r, 2, review),
                     test_box('chem', grade, chem_parts[0], 2, 25, '۲۵ تست مرتبط + تحلیل کامل'),
                     box('دروس نهایی', 'مطالعه دروس نهایی', 'مرور متن و تمرین تشریحی', 2, 0, [], 'finals')]
    day_boxes[2] += [bio_study(1),
                     test_box('math', grade, math_r, 2, 30, '۳۰ تست غیرزمان‌دار + تحلیل',
                              preference('math', grade, math_r)),
                     test_box('bio', grade, bio_parts[1], 2, 20, '۲۰ تست آموزشی + تحلیل همهٔ گزینه‌ها')]
    day_boxes[3] += [test_box('physics', grade, phy_r, 2, 30, '۳۰ تست غیرزمان‌دار + تحلیل',
                              preference('physics', grade, phy_r)),
                     chem_study(1),
                     box('دروس نهایی', 'مطالعه دروس نهایی', 'مرور متن و تمرین تشریحی', 2, 0, [], 'finals')]
    day_boxes[4] += [bio_study(2),
                     test_box('math', grade, math_r, 2, 30, '۳۰ تست ترجیحاً زمان‌دار + تحلیل',
                              preference('math', grade, math_r)),
                     test_box('bio', grade, bio_parts[2], 2, 20, '۲۰ تست تکمیلی + تحلیل و ثبت خطا')]
    thursday = [test_box('physics', grade, phy_full_test, 2, 30, '۳۰ تست ترجیحاً زمان‌دار + تحلیل',
                         preference('physics', grade, phy_full_test)),
                test_box('chem', grade, chem_full_test, 2, 25, '۲۵ تست ترکیبی + تحلیل و ثبت خطا')]
    if grade == 10:
        thursday += [test_box('bio', grade, bio_full_test, 2, 20, '۲۰ تست جمع‌بندی + تحلیل و ثبت خطا', review=review),
                     test_box('math', grade, math_full_test, 2, 30, '۳۰ تست جمع‌بندی + تحلیل', review=review)]
    else:
        assert geo_full_test
        thursday += [box(subject_label('geo', grade), topic('geo', grade, geo_full_test, review=review),
                         REVIEW_DETAIL['geo'] if review else STUDY_DETAIL['geo'], 1, 0, geo_full_test,
                         'review' if review else 'study'),
                     test_box('bio', grade, bio_full_test, 1, 10, '۱۰ تست جمع‌بندی + تحلیل', review=review),
                     test_box('geo', grade, geo_full_test, 1, 15, '۱۵ تست + تحلیل و ثبت خطا'),
                     test_box('math', grade, math_full_test, 1, 15, '۱۵ تست جمع‌بندی + تحلیل', review=review)]
    day_boxes[5] = thursday

    days = []
    for i, boxes in enumerate(day_boxes):
        d = start + timedelta(days=i)
        days.append(dict(day=i, week=week_no, name=DAY_NAMES[i], date=label(d), iso=d.isoformat(),
                         boxes=boxes,
                         hours=sum(b['hours'] for b in boxes),
                         tests=sum(b['tests'] for b in boxes)))
    friday = start + timedelta(days=6)
    return days, friday


def exam_schedule(cal, grade):
    """Weeks per cycle and the mode of every week."""
    budget = json.loads((BASE / 'annual/budget.json').read_text())
    rows = [r for r in budget if r['grade'] == grade]
    assert len(rows) == len(cal) == 17
    covered = {s: set() for s in SUBJECTS}
    plans = []
    for i, (c, row) in enumerate(zip(cal, rows)):
        target = jd(c['id'])
        start = (jd(cal[i - 1]['id']) + timedelta(days=1)) if i else (target - timedelta(days=13))
        weeks = ((target - start).days + 1) // 7
        assert (start + timedelta(days=7 * weeks - 1)) == target, (c['id'], weeks)
        scopes = {s: row['subjects'][s]['ranges'] for s in SUBJECTS if s in row['subjects']}
        new = {s: [p for p in pages(r) if p not in covered[s]] for s, r in scopes.items()}
        if weeks == 2:
            learn = bool(new['bio'] or new['physics'] or new['math'] or new['chem'])
            weeks_spec = [(scopes, not learn), (scopes, True)]
        elif weeks == 1:
            weeks_spec = [(scopes, not new['bio'])]
        elif weeks == 4:
            # Two normal weeks, then two consolidation weeks over half the scope
            # each; the last Thursday is comprehensive.
            learn = bool(new['bio'] or new['physics'] or new['math'] or new['chem'])
            halves = {s: split_units(r, s, grade, 2) for s, r in scopes.items()}
            weeks_spec = [(scopes, not learn), (scopes, True),
                          ({s: halves[s][0] for s in scopes}, True),
                          ({s: halves[s][1] for s in scopes}, True)]
        elif weeks == 5:
            fifths = {s: split_units(r, s, grade, 5) for s, r in scopes.items()}
            weeks_spec = [({s: fifths[s][k] for s in scopes}, True) for k in range(5)]
        else:
            raise AssertionError(weeks)
        assert len(weeks_spec) == weeks
        for s, r in scopes.items():
            covered[s].update(pages(r))
        plans.append(dict(row=row, exam=c['id'], target=target, start=start, weeks=weeks,
                          scopes=scopes, spec=weeks_spec))
    return plans


def build(grade, cal):
    label_g = LABELS[grade]
    manifest = []
    for plan in exam_schedule(cal, grade):
        days, week_meta = [], []
        for w, (week_scopes, review) in enumerate(plan['spec']):
            start = plan['start'] + timedelta(days=7 * w)
            final_week = w == plan['weeks'] - 1
            official = final_week
            d, friday = week_days(grade, start, w + 1, week_scopes, review, final_week,
                                  plan['scopes'], official, '')
            days += d
            week_meta.append(dict(label=label_g,
                                  date_range=label(start) + ' تا ' + label(start + timedelta(days=6)),
                                  friday=label(friday), official_exam=official,
                                  review=review))
        target = plan['target']
        exam_title = label(target, year=True)
        pid = f'g{grade}-{plan["exam"]}'
        last = week_meta[-1]
        meta = dict(id=pid, grade=grade,
                    title=f'برنامهٔ آزمون {exam_title} — {label_g} تجربی',
                    target=plan['exam'], start=plan['start'].isoformat(), end=target.isoformat(),
                    weeks=plan['weeks'], pages=plan['weeks'] * 2, preserved=False, special=False,
                    compact_layout=True,
                    week_meta=week_meta, days=days,
                    hours=sum(d['hours'] for d in days), tests=sum(d['tests'] for d in days),
                    directory=f'دهم و یازدهم/{label_g}/{folder_month(target)}/{label(target)}',
                    stem=f'برنامه آزمون {exam_title} - {label_g}',
                    exam_title=exam_title,
                    footer_target=exam_title)
        entry={k: meta[k] for k in ['id', 'grade', 'hours', 'tests', 'pages', 'directory', 'stem']}
        manifest.append(entry)
        yield meta, entry


def main():
    cal = json.loads((BASE / 'calendar.json').read_text())
    all_meta, all_manifest = [], []
    for grade in (10, 11):
        for meta, entry in build(grade, cal):
            all_meta.append(meta)
            all_manifest.append(entry)
            (BASE / 'data' / (meta['id'] + '.json')).write_text(
                json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    (BASE / 'annual/year_manifest.json').write_text(
        json.dumps(all_manifest, ensure_ascii=False, indent=2) + '\n')
    for meta in all_meta:
        print(meta['id'], meta['weeks'], 'weeks', meta['pages'], 'pages',
              meta['hours'], 'h', meta['tests'], 'tests')


if __name__ == '__main__':
    main()
