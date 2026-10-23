"""Whole-year plan for grade 12 (تجربی), built on the approved 10/11 model.

Rules encoded here (see ../PRINCIPLES.md):
* every subject box is a *review* of the pages the booklet lists — grade 12 is
  followed at school, the plan locks the pages down instead of re-teaching them;
* the time freed by that is spent on tests the student picks himself;
* four hours of final-exam subjects every week (2 h Sunday, 2 h Tuesday);
* the Thursday of the second week of each block is a comprehensive test day with
  one short sample lesson of the block;
* physics and maths tests are chosen freely from everything studied so far.
"""
import json
import sys
from datetime import timedelta
from pathlib import Path

import jdatetime

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'annual'))
from curriculum_map import LIGHT, chapters_for, pages, split_units, units_for  # noqa: E402

FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
          'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
DAY_NAMES = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه']
LABELS = {10: 'دهم', 11: 'یازدهم', 12: 'دوازدهم', 0: 'دهم و یازدهم'}
ACADEMIC = ['مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند',
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور']
PERSIAN_2D = ['۰۱', '۰۲', '۰۳', '۰۴', '۰۵', '۰۶', '۰۷', '۰۸', '۰۹', '۱۰', '۱۱', '۱۲']
SCOPE = json.loads((BASE / 'annual/scopes12.json').read_text())
EXAMS = list(SCOPE)
MIN_PAGES = 4
BOOK = {10: {'bio': 111, 'physics': 120, 'chem': 122, 'math': 170},
        11: {'bio': 152, 'physics': 104, 'chem': 123, 'math': 166},
        12: {'bio': 124, 'physics': 125, 'chem': 123, 'math': 148}}
SUBJECT_MAP = {'phys': 'physics'}


def fa(x):
    return str(x).translate(FA)


def jd(s):
    return jdatetime.date(*map(int, s.split('-')))


def label(d, year=False):
    return fa(d.day) + ' ' + MONTHS[d.month - 1] + (' ' + fa(d.year) if year else '')


def folder_month(d):
    return PERSIAN_2D[ACADEMIC.index(MONTHS[d.month - 1])] + ' - ' + MONTHS[d.month - 1]


def join_fa(items, sep='، '):
    items = list(items)
    if len(items) <= 1:
        return ''.join(items)
    return sep.join(items[:-1]) + ' و ' + items[-1]


def overlap(units, ranges):
    return [u for u in units if any(u[0] <= b and u[1] >= a for a, b in ranges)]


def light_spans(subject, grade):
    return LIGHT.get((subject, grade)) or []


def readable_units(subject, grade, ranges):
    out = []
    for unit in overlap(units_for(subject, grade), ranges):
        if any(a <= unit[0] and unit[1] <= b for a, b in light_spans(subject, grade)):
            continue
        out.append(unit)
    return out


def span_pages(unit, ranges):
    return sum(max(0, min(unit[1], b) - max(unit[0], a) + 1) for a, b in ranges)


def main_chapter(subject, grade, ranges):
    chs = overlap(chapters_for(subject, grade), ranges)
    if not chs:
        return ''
    return max(chs, key=lambda c: span_pages(c, ranges))[3]


def head_for(subject, grade, ranges):
    units = readable_units(subject, grade, ranges)
    if subject == 'bio':
        chapter = main_chapter('bio', grade, ranges)
        if chapter and len(overlap(chapters_for('bio', grade), ranges)) == 1 and units:
            candidate = chapter + '؛ ' + join_fa(u[3] for u in units[:2])
            return candidate if len(candidate) <= 30 else chapter
        return chapter or 'زیست'
    if subject == 'chem':
        return main_chapter('chem', grade, ranges) or 'شیمی'
    if subject == 'physics':
        chapter = main_chapter('physics', grade, ranges)
        if units and len(units) == 1:
            return join_fa([chapter, units[0][3]])
        return chapter or 'فیزیک'
    if subject == 'math':
        return join_fa([u[3] for u in units[:2]]) if units else 'ریاضی'
    raise KeyError(subject)


def page_text(ranges, subject=None, grade=None):
    if len(ranges) == 1:
        a, b = ranges[0]
        body = 'ص' + fa(a) + ('–' + fa(b) if b != a else '')
    else:
        body = 'ص' + ' و '.join(fa(a) + '–' + fa(b) for a, b in ranges)
    if subject == 'math':
        body = 'ریاضی' + fa({10: 1, 11: 2, 12: 3}[grade]) + ' ' + body
    return body


def math_page_text(pairs):
    """Three maths books in one cell, heaviest book first, as in the booklet."""
    return '، '.join(page_text(r, 'math', g) for g, r in sorted(pairs, key=lambda p: -p[0]))


def shorten(head, limit):
    """Cut on a word boundary and never leave a dangling conjunction."""
    if len(head) <= limit:
        return head
    cut = head[:limit]
    if ' ' in cut:
        cut = cut[:cut.rfind(' ')]
    return cut.rstrip('،، و') .strip() + '…'


def clean_head(text):
    return text.replace('مرور جامع ', '').replace('مرور ', '').strip() if text else text


def is_full_book(subject, grade, ranges):
    length = BOOK[grade][{'phys': 'physics'}.get(subject, subject)]
    return len(pages(ranges)) >= 0.85 * length


def topic(subject, grade, ranges, review=True, comprehensive=False, note='', head=None):
    head = clean_head(head) or head_for(subject, grade, ranges)
    if is_full_book(subject, grade, ranges):
        head = 'کل کتاب'
    elif len(head) > 30:
        head = shorten(head, 30)
    if comprehensive:
        head = 'مرور جامع ' + head
    elif review:
        head = 'مرور ' + head
    text = head + '؛ ' + page_text(ranges, subject, grade)
    if note:
        text += '؛ ' + note
    if len(text) > 70:
        text = shorten(head, 22) + '؛ ' + page_text(ranges, subject, grade)
    return text


def box(subject, topic_text, detail, hours, tests=0, ranges=None, kind='review', preference=None):
    b = dict(subject=subject, topic=topic_text, detail=detail, hours=hours,
             tests=tests, kind=kind, ranges=ranges or [])
    if preference:
        b['preference'] = '* ترجیحاً: ' + preference
    return b


def subject_label(subject, grade):
    if subject == 'math':
        return 'ریاضی'
    return {'bio': 'زیست ', 'physics': 'فیزیک ', 'chem': 'شیمی '}[subject] + LABELS[grade]


REVIEW_DETAIL = {
    'bio': 'مرور متن، شکل‌ها و قیدها',
    'math': 'مرور درسنامه و مثال‌های حل‌شده',
    'physics': 'مرور درسنامه و مثال‌های حل‌شده',
    'chem': 'مرور متن، مثال‌ها و بیازمایید',
}
TEST_DETAIL = {
    'bio': 'آزادی انتخاب تست؛ از ۳۰ تست تا جامع',
    'math': 'آزادی انتخاب تست؛ از ۳۰ تست تا جامع',
    'physics': 'آزادی انتخاب تست؛ از ۳۰ تست تا جامع',
    'chem': 'آزادی انتخاب تست؛ از ۳۰ تست تا جامع',
}


def scope_of(phase, subject):
    groups = {}
    for g, a, b in phase[subject]:
        groups.setdefault(int(g), []).append([int(a), int(b)])
    return sorted(groups.items(), key=lambda kv: -len(pages(kv[1])))


def _union(ranges):
    spans = sorted(tuple(r) for r in ranges)
    out = []
    for a, b in spans:
        if out and a <= out[-1][1] + 1:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def merge_short(pieces):
    """No review box smaller than MIN_PAGES while a neighbour can absorb it."""
    out = [[list(r) for r in p] for p in pieces]
    while len(out) > 1:
        idx = next((i for i, p in enumerate(out) if len(pages(p)) < MIN_PAGES), None)
        if idx is None:
            break
        j = idx - 1 if idx else 1
        lo, hi = min(idx, j), max(idx, j)
        out[lo:hi + 1] = [_union(out[lo] + out[hi])]
    return out


def study_items(phase, subject, slots):
    groups = scope_of(phase, subject)
    book_subject = SUBJECT_MAP.get(subject, subject)
    sizes = [len(pages(r)) for _, r in groups]
    if len(groups) == 1:
        pieces = split_units(groups[0][1], book_subject, groups[0][0], slots)
        pieces = merge_short(pieces)
        combined = _union([r for piece in pieces for r in piece])
        while len(pieces) < slots:
            pieces.append([list(r) for r in combined])
        return [(groups[0][0], p) for p in pieces]
    total = sum(sizes)
    alloc = [max(1, round(slots * s / total)) for s in sizes]
    while sum(alloc) > slots:
        alloc[alloc.index(max(alloc))] -= 1
    while sum(alloc) < slots:
        alloc[alloc.index(min(alloc))] += 1
    out = []
    for (g, r), n in zip(groups, alloc):
        out += [(g, piece) for piece in split_units(r, book_subject, g, n)]
    return out


def preference(subject, grade, ranges):
    if subject not in ('math', 'physics'):
        return None
    units = readable_units(subject, grade, ranges)
    return units[0][3] if units else None


def week_days(phase, start, week_no, final_week, block):
    bio = study_items(phase, 'bio', max(3, len(scope_of(phase, 'bio'))))
    chem = study_items(phase, 'chem', max(2, len(scope_of(phase, 'chem'))))
    maths = scope_of(phase, 'math')
    phys = scope_of(phase, 'phys')
    phys_items = study_items(phase, 'phys', max(1, len(phys)))
    math_head = phase['head'].get('math') or None

    def math_topic(comprehensive=False, review=True):
        head = clean_head(math_head) or join_fa([u[3] for u in readable_units('math', maths[0][0], maths[0][1])[:2]])
        if comprehensive:
            head = 'مرور جامع ' + head
        elif review:
            head = 'مرور ' + head
        return head + '؛ ' + math_page_text(maths)

    def math_box(hours, tests=0, kind='review', comprehensive=False, prefer=None):
        detail = REVIEW_DETAIL['math'] if kind == 'review' else TEST_DETAIL['math']
        return box('ریاضی', math_topic(comprehensive, kind == 'review'), detail, hours, tests,
                   [r for _, rs in maths for r in rs], kind, prefer)

    def math_pref():
        g = max(maths, key=lambda kv: kv[0] == 12)[0]
        return preference('math', g, dict(maths)[g])

    def rev(subject, grade, ranges, hours):
        return box(subject_label(subject, grade), topic(subject, grade, ranges, True),
                   REVIEW_DETAIL[subject], hours, ranges=ranges)

    def test(subject, grade, ranges, hours, tests, comprehensive=False, prefer=None):
        return box(subject_label(subject, grade),
                   topic(subject, grade, ranges, False, comprehensive=comprehensive),
                   TEST_DETAIL[subject], hours, tests, ranges, 'test', prefer)

    b1, b2, b3 = bio[0], bio[1], bio[2]
    c1, c2 = chem[0], chem[1]
    bio_all = (b1[0], _union([r for g, piece in bio if g == b1[0] for r in piece]))
    chem_all = (c1[0], _union([r for g, piece in chem if g == c1[0] for r in piece]))
    p_g, p_r = phys[0]

    def ph(i):
        return phys_items[min(i, len(phys_items) - 1)]
    m_g = maths[0][0]
    m_all = [r for _, rs in maths for r in rs]

    day_boxes = [[] for _ in range(6)]
    day_boxes[0] = [rev('bio', *b1, 1), math_box(2), test('bio', *b1, 2, 20), math_box(2, 30, 'test', prefer=math_pref())]
    ph_revs = [rev('physics', *ph(0), 1 if len(phys_items) > 1 else 2)]
    if len(phys_items) > 1:
        ph_revs.append(rev('physics', *ph(1), 1))
    day_boxes[1] = [rev('chem', *c1, 1), *ph_revs, test('chem', *c1, 2, 25),
                    box('دروس نهایی', 'مطالعهٔ دروس نهایی', 'متن و تمرین تشریحی', 2, 0, [], 'finals')]
    day_boxes[2] = [rev('bio', *b2, 1), math_box(2), test('bio', *b2, 2, 20), math_box(1, 15, 'test', prefer=math_pref())]
    day_boxes[3] = [test('physics', p_g, p_r, 2, 30, prefer=preference('physics', p_g, p_r)),
                    rev('chem', *c2, 1), test('chem', *c2, 2, 25),
                    box('دروس نهایی', 'مطالعهٔ دروس نهایی', 'متن و تمرین تشریحی', 2, 0, [], 'finals')]
    day_boxes[4] = [rev('bio', *b3, 1), math_box(2),
                    test('physics', *ph(0), 2, 30, prefer=preference('physics', *ph(0)))]
    # Blocks that span three books still get one review box per book.
    day_boxes[4] += [rev('chem', *c, 1) for c in chem[2:]]
    day_boxes[4] += [rev('physics', *p, 1) for p in phys_items[2:]]

    if final_week:
        sample_g, sample_r = block['sample']
        thursday = [box(subject_label('bio', sample_g),
                        'درسنامهٔ نمونه: ' + head_for('bio', sample_g, sample_r) + '؛ ' + page_text(sample_r),
                        'نمونهٔ کوتاه از کل بازه', 1, 0, sample_r, 'study'),
                    test('physics', p_g, p_r, 2, 30, True, preference('physics', p_g, p_r)),
                    test('chem', *chem_all, 2, 25, True),
                    test('bio', *bio_all, 2, 20, True),
                    math_box(1, 20, 'test', comprehensive=True, prefer=math_pref())]
    else:
        thursday = [test('physics', p_g, p_r, 2, 30, prefer=preference('physics', p_g, p_r)),
                    test('chem', *chem_all, 2, 25),
                    test('bio', *bio_all, 2, 20),
                    math_box(2, 30, 'test', prefer=math_pref())]
    day_boxes[5] = thursday

    days = []
    for i, boxes in enumerate(day_boxes):
        d = start + timedelta(days=i)
        days.append(dict(day=i, week=week_no, name=DAY_NAMES[i], date=label(d), iso=d.isoformat(),
                         boxes=boxes, hours=sum(x['hours'] for x in boxes),
                         tests=sum(x['tests'] for x in boxes)))
    return days, start + timedelta(days=6)


def block_info(phases):
    """Dominant grade-12 scope of the block, for the sample lesson."""
    best = None
    for phase in phases:
        for g, a, b in phase['bio']:
            size = b - a + 1
            if g == 12 and (best is None or size > best[2]):
                best = (g, a, b, size)
    if best and best[3] > 10:
        return {'sample': (12, [[best[1], best[1] + 9]])}
    if best:
        return {'sample': (12, [[best[1], best[2]]])}
    g, a, b = phases[-1]['bio'][0]
    return {'sample': (g, [[a, min(b, a + 9)]])}


def build():
    manifest = []
    for idx, exam in enumerate(EXAMS):
        block = SCOPE[exam]
        target = jd(exam)
        prev = EXAMS[idx - 1] if idx else None
        begin = (jd(prev) + timedelta(days=1)) if prev else (target - timedelta(days=13))
        weeks, phases = block['weeks'], block['phases']
        assert len(phases) == weeks, (exam, len(phases), weeks)
        info = block_info(phases)
        days, week_meta = [], []
        for w, phase in enumerate(phases):
            wk_start = begin + timedelta(days=7 * w)
            final_week = w == weeks - 1
            d, friday = week_days(phase, wk_start, w + 1, final_week, info)
            days += d
            week_meta.append(dict(label=LABELS[phase['grade']],
                                  date_range=label(wk_start) + ' تا ' + label(wk_start + timedelta(days=6)),
                                  friday=label(friday), official_exam=final_week, review=True))
        title = 'برنامهٔ آزمون ' + label(target, year=True) + ' — دوازدهم تجربی'
        meta = dict(id='g12-' + exam, grade=12, title=title, target=exam,
                    start=begin.isoformat(), end=target.isoformat(), weeks=weeks,
                    pages=weeks * 2, preserved=False, special=False, compact_layout=True,
                    week_meta=week_meta, days=days,
                    hours=sum(d['hours'] for d in days), tests=sum(d['tests'] for d in days),
                    directory='دوازدهم/دوازدهم/' + folder_month(target) + '/' + label(target),
                    stem='برنامه آزمون ' + label(target, year=True) + ' - دوازدهم',
                    exam_title=label(target, year=True), footer_target=label(target, year=True))
        manifest.append({k: meta[k] for k in ('id', 'grade', 'hours', 'tests', 'pages', 'directory', 'stem')})
        yield meta
    (BASE / 'annual/year_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')


def main():
    for meta in build():
        (BASE / 'data' / (meta['id'] + '.json')).write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
        print(meta['id'], meta['weeks'], 'weeks', meta['pages'], 'pages',
              meta['hours'], 'h', meta['tests'], 'tests')


if __name__ == '__main__':
    main()
